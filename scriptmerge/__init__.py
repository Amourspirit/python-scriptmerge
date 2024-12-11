from __future__ import annotations
from typing import Any, Callable, List

__version__ = "3.0.1"


from scriptmerge import merge_common as mc
from scriptmerge.merge_common import EventArgs as EventArgs
from scriptmerge.merge_common import CancelEventArgs as CancelEventArgs
from scriptmerge import merge_py as merge_py
from scriptmerge import merge_pyz as merge_pyz

# region Constants for Callbacks
CALLBACK_GENERATED_SHEBANG = mc.CALLBACK_GENERATED_SHEBANG
CALLBACK_GENERATING_FOR_MODULE = mc.CALLBACK_GENERATING_FOR_MODULE
CALLBACK_GENERATING_FOR_FILE = mc.CALLBACK_GENERATING_FOR_FILE
CALLBACK_GENERATED_PYTHON_PATHS = mc.CALLBACK_GENERATED_PYTHON_PATHS
CALLBACK_GENERATING_PRELUDE = merge_py.CALLBACK_GENERATING_PRELUDE
CALLBACK_GENERATING_INIT_PY_FILE = merge_pyz.CALLBACK_GENERATING_INIT_PY_FILE
CALLBACK_GENERATING_MAIN_PY_FILE = merge_pyz.CALLBACK_GENERATING_MAIN_PY_FILE
CALLBACK_GENERATED_MAIN_PY_FILE_CONTENT = (
    merge_pyz.CALLBACK_GENERATED_MAIN_PY_FILE_CONTENT
)
# endregion Constants for Callbacks


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
    pyz_out: bool = False,
    callback: Callable[[Any, EventArgs], None] | None = None,
    **kwargs: Any,
) -> bytes | str:
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
        clean (bool, optional): Remove comments and doc strings. Defaults to False.
        pyz_out (bool, optional): Specifies if the script should be written as a binary pyz file. Defaults to False.
        callback (Callable[[Any, EventArgs], None] | None, optional): Callback function.

    Returns:
        str: Python modules compiled into single file contents.
    """
    if pyz_out:
        subscript = merge_pyz.script

        include_main_py = bool(kwargs.get("include_main_py", True))
    else:
        subscript = merge_py.script
        include_main_py = bool(kwargs.get("include_main_py", False))
    return subscript(
        path=path,
        add_python_modules=add_python_modules,
        add_python_paths=add_python_paths,
        python_binary=python_binary,
        copy_shebang=copy_shebang,
        exclude_python_modules=exclude_python_modules,
        clean=clean,
        callback=callback,
        include_main_py=include_main_py,
        **kwargs,
    )
