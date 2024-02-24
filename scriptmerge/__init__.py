from __future__ import annotations
from typing import List, Set
import ast
import os
import os.path
import subprocess
import re

import io
import tokenize

from .stdlib import is_stdlib_module

# set a flag to indicate that we are running in the scriptmerge context
os.environ["SCRIPT_MERGE_ENVIRONMENT"] = "1"


# _RE_CODING =  re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")
# https://peps.python.org/pep-0263/


def script(
    path: str,
    add_python_modules: List[str] | None = None,
    add_python_paths: List[str] = None,
    python_binary: str | None = None,
    copy_shebang: bool = False,
    exclude_python_modules: List[str] | None = None,
    clean: bool = False,
) -> str:
    """
    Generate Script

    Args:
        path (str): Path to entry point py file
        add_python_modules (List[str] | None, optional): Extra Python modules to include.
        add_python_paths (List[str], optional): Extra Python paths used to search for modules.
        python_binary (str | None, optional): Path to any binary to include.
        copy_shebang (bool, optional): Copy Shebang.
        exclude_python_modules (List[str] | None, optional): One or more regular expressions that match Module names to exclude as.
            Such as ["greetings*"]

    Returns:
        str: Python modules compiled into single file contents.
    """
    if add_python_modules is None:
        add_python_modules = []

    if add_python_paths is None:
        add_python_paths = []
    if exclude_python_modules is None:
        exclude_python_modules = []

    _exclude_python_modules = set(exclude_python_modules)

    python_paths = (
        [os.path.dirname(path)]
        + add_python_paths
        + _read_sys_path_from_python_bin(python_binary)
    )

    output = []

    output.append(_generate_shebang(path, copy=copy_shebang))
    output.append(_prelude())
    output.append(
        _generate_module_writers(
            path,
            sys_path=python_paths,
            add_python_modules=add_python_modules,
            exclude_python_modules=_exclude_python_modules,
            clean=clean,
        )
    )
    with _open_source_file(path) as source_file:
        output.append(_indent(source_file.read()))
    return "".join(output)


def _read_sys_path_from_python_bin(binary_path: str):
    if binary_path is None:
        return []
    else:
        output = subprocess.check_output(
            [binary_path, "-E", "-c", "import sys;\nfor path in sys.path: print(path)"],
        )
        return [
            # TODO: handle non-UTF-8 encodings
            line.strip().decode("utf-8")
            for line in output.split(b"\n")
            if line.strip()
        ]


def _indent(string: str):
    return "    " + string.replace("\n", "\n    ")


def _generate_shebang(path: str, copy: bool):
    if copy:
        with _open_source_file(path) as script_file:
            first_line = script_file.readline()
            if first_line.startswith("#!"):
                return first_line

    return "#!/usr/bin/env python"


def _prelude():
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path, encoding="utf-8") as prelude_file:
        return prelude_file.read()


def _generate_module_writers(
    path: str,
    sys_path: str,
    add_python_modules: List[str],
    exclude_python_modules: Set[str],
    clean: bool,
):
    generator = ModuleWriterGenerator(sys_path, clean)
    generator.generate_for_file(
        path,
        add_python_modules=add_python_modules,
        exclude_python_modules=exclude_python_modules,
    )
    return generator.build()


class ModuleWriterGenerator(object):
    def __init__(self, sys_path: str, clean: bool):
        self._sys_path = sys_path
        self._modules = {}
        self._clean = clean

    def build(self):
        output = []
        for module_path, module_source in self._modules.values():
            output.append(
                "    __scriptmerge_write_module({0}, {1})\n".format(
                    repr(module_path), repr(module_source)
                )
            )
        return "".join(output)

    def generate_for_file(
        self,
        python_file_path: str,
        add_python_modules: List[str],
        exclude_python_modules: Set[str],
    ):
        self._generate_for_module(
            ImportTarget(
                python_file_path,
                relative_path=None,
                is_package=False,
                module_name=None,
                clean=self._clean,
            ),
            exclude_python_modules,
        )

        for add_python_module in add_python_modules:
            import_line = ImportLine(module_name=add_python_module, items=[])
            self._generate_for_import(
                python_module=None,
                import_line=import_line,
                exclude_python_modules=exclude_python_modules,
            )

    def _generate_for_module(
        self, python_module: ImportTarget, exclude_python_modules: Set[str]
    ):
        def is_excluded(line: ImportLine):
            for exclude in exclude_python_modules:
                if re.match(exclude, line.module_name):
                    return True
            return False

        import_lines = _find_imports_in_module(python_module)
        for import_line in import_lines:
            if not _is_stdlib_import(import_line) and not is_excluded(import_line):
                self._generate_for_import(
                    python_module, import_line, exclude_python_modules
                )

    def _generate_for_import(
        self,
        python_module: ImportTarget,
        import_line: ImportTarget,
        exclude_python_modules: Set[str],
    ):
        import_targets = self._read_possible_import_targets(python_module, import_line)

        for import_target in import_targets:
            if import_target.module_name not in self._modules:
                self._modules[import_target.module_name] = (
                    import_target.relative_path,
                    import_target.read_binary(),
                )
                self._generate_for_module(
                    python_module=import_target,
                    exclude_python_modules=exclude_python_modules,
                )

    def _read_possible_import_targets(
        self, python_module: ImportTarget, import_line: ImportLine
    ) -> List[ImportTarget]:
        module_name_parts = import_line.module_name.split(".")

        module_names = [
            ".".join(module_name_parts[0 : index + 1])
            for index in range(len(module_name_parts))
        ] + [import_line.module_name + "." + item for item in import_line.items]

        import_targets = [
            self._find_module(module_name) for module_name in module_names
        ]

        valid_import_targets = [
            target for target in import_targets if target is not None
        ]
        return valid_import_targets
        # TODO: allow the user some choice in what happens in this case?
        # Detection of try/except blocks is possibly over-complicating things
        # ~ if len(valid_import_targets) > 0:
        # ~ return valid_import_targets
        # ~ else:
        # ~ raise RuntimeError("Could not find module: " + import_line.import_path)

    def _find_module(self, module_name: str):
        for sys_path in self._sys_path:
            for is_package in (True, False):
                if is_package:
                    suffix = "/__init__.py"
                else:
                    suffix = ".py"

                relative_path = module_name.replace(".", "/") + suffix
                full_module_path = os.path.join(sys_path, relative_path)
                if os.path.exists(full_module_path):
                    return ImportTarget(
                        full_module_path,
                        relative_path=relative_path,
                        is_package=is_package,
                        module_name=module_name,
                        clean=self._clean,
                    )
        return None


def _find_imports_in_module(python_module: ImportTarget):
    source = _read_binary(python_module.absolute_path)
    parse_tree = ast.parse(source, python_module.absolute_path)

    for node in ast.walk(parse_tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                yield ImportLine(name.name, [])

        if isinstance(node, ast.ImportFrom):
            if node.level == 0:
                module = node.module
            else:
                level = node.level

                if python_module.is_package:
                    level -= 1

                if level == 0:
                    package_name = python_module.module_name
                else:
                    package_name = ".".join(
                        python_module.module_name.split(".")[:-level]
                    )

                if node.module is None:
                    module = package_name
                else:
                    module = package_name + "." + node.module

            yield ImportLine(module, [name.name for name in node.names])


def _read_binary(path: str) -> bytes:
    with open(path, "rb") as file:
        return file.read()


def _open_source_file(path: str):
    return open(path, "rt", encoding="utf-8")


def _is_stdlib_import(import_line: ImportLine):
    return is_stdlib_module(import_line.module_name)


def _remove_comments_and_docstrings(source: str) -> str:
    """
    Returns 'source' minus comments and docstrings.
    """
    # https://stackoverflow.com/questions/1769332/script-to-remove-python-comments-docstrings
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    i = 0

    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += " " * (start_col - last_col)
        # Remove comments if not coding or shebang:
        if token_type == tokenize.COMMENT:
            if i > 0:
                pass
            else:
                if token_string.startswith("#!"):
                    out += token_string
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    i += 1

    # replace multiable new-lines with single new-line
    result = out.strip()
    if len(result) > 0:
        # remove empty lines
        lines = [line for line in result.splitlines() if line.strip() != ""]
        lines.append("")  # so final output ends with and empty line.
        result = "\n".join(lines)
    return result


class ImportTarget(object):
    def __init__(
        self,
        absolute_path: str,
        relative_path: str,
        is_package: bool,
        module_name: str,
        clean: bool,
    ):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.is_package = is_package
        self.module_name = module_name
        self._clean = clean

    def read_binary(self) -> bytes:
        if self._clean:
            with open(self.absolute_path, "rt", encoding="utf-8") as file:
                file_str = _remove_comments_and_docstrings(file.read())
                return file_str.encode("utf-8")

        with open(self.absolute_path, "rb") as file:
            return file.read()


class ImportLine(object):
    def __init__(self, module_name: str, items: List[str]):
        self.module_name = module_name
        self.items = items
