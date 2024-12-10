from __future__ import annotations
from typing import Any, List, Set, Callable
import ast
import os
import os.path
import subprocess
import re
import io
import zipapp
import tempfile
import shutil

from scriptmerge.stdlib import is_stdlib_module
import scriptmerge.merge_common as merge_common
from scriptmerge.merge_common import EventArgs, CancelEventArgs

CALLBACK_GENERATING_INIT_PY_FILE = "GENERATING_INIT_PY_FILE"
CALLBACK_GENERATING_MAIN_PY_FILE = "GENERATING_MAIN_PY_FILE"
CALLBACK_GENERATED_MAIN_PY_FILE_CONTENT = "GENERATED_MAIN_PY_FILE_CONTENT"


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
    callback: Callable[[Any, EventArgs], None] | None = None,
    **kwargs: Any,
) -> bytes:
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
        clean (bool, optional): Specifies if the source code should be cleaned. Defaults to False.
        callback (Callable[[Any, EventArgs], None] | None, optional): Callback function.

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

    if callback is not None:
        ev_args = EventArgs(
            name=merge_common.CALLBACK_GENERATED_PYTHON_PATHS, source="script"
        )
        event_data = {
            "python_paths": python_paths,
            "path": path,
            "copy": copy_shebang,
            "clean": clean,
        }
        ev_args.event_data = event_data
        callback("script", ev_args)
        python_paths = ev_args.event_data.get("python_paths", python_paths)

    shebang = _generate_interpreter(path, copy=copy_shebang)
    if callback is not None:
        ev_args = CancelEventArgs(
            name=merge_common.CALLBACK_GENERATED_SHEBANG, source="script"
        )
        event_data = {
            "shebang": shebang,
            "path": path,
            "copy": copy_shebang,
            "clean": clean,
        }
        ev_args.event_data = event_data
        callback("script", ev_args)
        if ev_args.cancel:
            shebang = None
        else:
            shebang = ev_args.event_data.get("shebang", shebang)
            if shebang.startswith("#!"):
                shebang = str(shebang[2:]).lstrip()

    source_contents = merge_common.read_str_file(path)
    shebang_src = merge_common.remove_shebang(source_contents)
    if shebang:
        gen_shebang_src = f"#!{shebang}\n" + shebang_src
    else:
        gen_shebang_src = shebang_src

    with tempfile.TemporaryDirectory() as archive_dir:
        if callback is not None:
            # This event give a chance to modify the path of the __main__.py file.
            # If the user wishes to write the script of a different file then this is the event to do it.
            # Note that __main__py is required for a pyz file or it will not build.
            ev_args = EventArgs(
                name=CALLBACK_GENERATING_MAIN_PY_FILE,
                source="script",
            )
            event_data = {
                "dir": archive_dir,
                "path": path,
                "clean": clean,
            }
            ev_args.event_data = event_data
            callback("script", ev_args)

        merge_common.write_str_file(
            os.path.join(archive_dir, "__main__.py"), gen_shebang_src
        )

        # shutil.copyfile(path, os.path.join(archive_dir, "__main__.py"))

        with open(os.path.join(archive_dir, "__main__.py"), "r", encoding="utf-8") as f:
            build_contents = f.read()

        if callback is not None:
            # if the user wants to modify the contents of the __main__.py file or append to it then
            # this is the event to do it.
            ev_args = EventArgs(
                name=CALLBACK_GENERATED_MAIN_PY_FILE_CONTENT,
                source="script",
            )
            event_data = {
                "contents": build_contents,
                "path": path,
                "clean": clean,
            }
            ev_args.event_data = event_data
            callback("script", ev_args)
            contents = ev_args.event_data.get("contents", build_contents)
            if contents != build_contents:
                with open(
                    os.path.join(archive_dir, "__main__.py"), "w", encoding="utf-8"
                ) as f:
                    f.write(contents)

        init_file_path = os.path.join(archive_dir, "__init__.py")
        contents = ""
        with open(init_file_path, "w", encoding="utf-8") as f:
            if callback is not None:
                # This event give a chance to modify the contents of the __init__.py file.
                ev_args = EventArgs(
                    name=CALLBACK_GENERATING_INIT_PY_FILE,
                    source="script",
                )
                event_data = {
                    "contents": "",
                    "clean": clean,
                }
                ev_args.event_data = event_data
                callback("script", ev_args)
                contents = ev_args.event_data.get("contents", contents)
                if not isinstance(contents, str):
                    contents = ""
            f.write(contents)

        generator = ModuleWriterGenerator(
            sys_path=python_paths, clean=clean, callback=callback
        )
        generator.generate_for_file(
            path,
            add_python_modules=add_python_modules,
            exclude_python_modules=_exclude_python_modules,
        )
        for module in generator._modules.values():
            make_package(archive_dir=archive_dir, module=module)
            archive_module_path = os.path.join(archive_dir, module.relative_path)
            if module.clean:
                with _open_source_file(module.absolute_path) as f:
                    source = f.read()
                source = merge_common.remove_comments_and_doc_strings(source)
                with open(archive_module_path, "w", encoding="utf-8") as f:
                    f.write(source)
            else:
                shutil.copyfile(module.absolute_path, archive_module_path)

        output = io.BytesIO()

        zipapp.create_archive(
            source=archive_dir,
            target=output,
            interpreter=shebang,  # this does not seem to make any difference when returning output.getvalue()
        )
        return output.getvalue()


def make_package(archive_dir, module: ImportTarget):
    parts = os.path.dirname(module.relative_path).split("/")
    partial_path = archive_dir
    for part in parts:
        partial_path = os.path.join(partial_path, part)
        if not os.path.exists(partial_path):
            os.mkdir(partial_path)
            with open(os.path.join(partial_path, "__init__.py"), "wb") as f:
                f.write(b"\n")


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


def _generate_interpreter(path, copy):
    if copy:
        with _open_source_file(path) as script_file:
            first_line = script_file.readline()
            if first_line.startswith("#!"):
                return first_line[2:]

    return "/usr/bin/env python3"


class ModuleWriterGenerator:

    def __init__(
        self,
        sys_path: str,
        clean: bool,
        callback: Callable[[Any, EventArgs], None] | None = None,
    ):
        self._sys_path = sys_path
        self._modules = {}
        self._clean = clean
        self._callback = callback

    def generate_for_file(
        self,
        python_file_path: str,
        add_python_modules: List[str],
        exclude_python_modules: Set[str],
    ):
        if self._callback is not None:
            cancel_args = CancelEventArgs(
                name=merge_common.CALLBACK_GENERATING_FOR_FILE, source=self
            )
            event_data = {
                "path": python_file_path,
                "add_python_modules": add_python_modules,
                "exclude_python_modules": exclude_python_modules,
            }
            cancel_args.event_data = event_data
            self._callback(self, cancel_args)
            if cancel_args.cancel:
                return
            python_file_path = cancel_args.event_data.get("path", python_file_path)
            add_python_modules = cancel_args.event_data.get(
                "add_python_modules", add_python_modules
            )
            exclude_python_modules = cancel_args.event_data.get(
                "exclude_python_modules", exclude_python_modules
            )
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
            import_line = ImportLine(module_name=add_python_module)
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

        if self._callback is not None:
            cancel_args = CancelEventArgs(
                name=merge_common.CALLBACK_GENERATING_FOR_MODULE, source=self
            )
            event_data = {
                "module": python_module,
                "exclude_python_modules": exclude_python_modules,
            }
            cancel_args.event_data = event_data
            self._callback(self, cancel_args)
            if cancel_args.cancel:
                return
            python_module = cancel_args.event_data.get("module", python_module)
            exclude_python_modules = cancel_args.event_data.get(
                "exclude_python_modules", exclude_python_modules
            )

        import_lines = _find_imports_in_module(python_module)
        for import_line in import_lines:
            if _is_stdlib_import(import_line) or is_excluded(import_line):
                continue
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
                self._modules[import_target.module_name] = import_target
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


class ImportTarget:
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
        self.clean = clean


class ImportLine:
    def __init__(self, module_name: str, items: List[str] | None = None):
        if not items:
            items = []
        self.module_name = module_name
        self.items = items
