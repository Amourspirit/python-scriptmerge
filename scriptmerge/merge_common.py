from __future__ import annotations
from typing import Any
import io
import os
import tokenize
import tempfile
import shutil
import contextlib
from pathlib import Path

CALLBACK_GENERATED_SHEBANG = "GENERATED_SHEBANG"
CALLBACK_GENERATING_FOR_MODULE = "GENERATING_FOR_MODULE"
CALLBACK_GENERATING_FOR_FILE = "GENERATING_FOR_FILE"
CALLBACK_GENERATED_PYTHON_PATHS = "GENERATED_PYTHON_PATHS"


def remove_comments_and_doc_strings(source: str) -> str:
    """
    Returns 'source' minus comments and doc strings.
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

    # replace multiple new-lines with single new-line
    result = out.strip()
    if len(result) > 0:
        # remove empty lines
        lines = [line for line in result.splitlines() if line.strip() != ""]
        lines.append("")  # so final output ends with and empty line.
        result = "\n".join(lines)
    return result


def remove_shebang(source: str) -> str:
    """
    Removes Shebang from source if it exists.
    """
    if source.startswith("#!"):
        index = source.find("\n")
        if index != -1:
            source = source[index + 1 :].lstrip()
    return source


def read_str_file(file_path: str | Path) -> str:
    """
    Reads a file and returns its content as string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_str_file(file_path: str | Path, content: str) -> None:
    """
    Writes content to a file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


class EventArgs:
    """
    Event Arguments Class
    """

    def __init__(self, name: str, source: Any = None) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
        """
        self.name = name
        self.source = source
        self.event_data = None

    @staticmethod
    def from_args(args: EventArgs) -> EventArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (AbstractEvent): Existing Instance

        Returns:
            EventArgs: args
        """
        ev_args = EventArgs(name=args.name, source=args.source)
        ev_args.event_data = args.event_data
        return ev_args


class CancelEventArgs(EventArgs):
    """Cancel Event Arguments"""

    def __init__(self, name=str, source: Any = None) -> None:
        """
        Constructor

        Args:
            source (Any): Event Source
        """
        super().__init__(name, source)
        self.cancel = False
        self.handled = False

    @staticmethod
    def from_args(args: CancelEventArgs) -> CancelEventArgs:
        """
        Gets a new instance from existing instance

        Args:
            args (CancelEventArgs): Existing Instance

        Returns:
            CancelEventArgs: args
        """
        ev_args = CancelEventArgs(name=args.name, source=args.source)
        ev_args.event_data = args.event_data
        ev_args.cancel = args.cancel
        ev_args.handled = args.handled
        return ev_args


@contextlib.contextmanager
def temp_file_manager(content: str, manual_file_name: str = ""):
    """
    Manages the creation and cleanup of temporary files.
    This function can either create a temporary file with a given content and
    automatically delete it after use, or use a manually specified file name
    and delete it after use.

    Args:
        content (str): The content to be written to the temporary file.
        manual_file_name (str, optional): The name of the file to be created.
            If not provided, a temporary file
            with a unique name will be created.
    Yields:
        str: The name of the temporary file created.
    Raises:
        OSError: If there is an error in file creation or deletion.
    """

    if manual_file_name:
        parent_dir = Path(tempfile.mkdtemp())
        file_name = parent_dir / manual_file_name
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        try:
            yield str(file_name)
        finally:
            shutil.rmtree(parent_dir)
    else:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content.encode())
            temp_file_name = temp_file.name
        try:
            yield temp_file_name
        finally:
            os.remove(temp_file_name)
