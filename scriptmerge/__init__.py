from __future__ import annotations
from typing import List
import os
import os.path

__version__ = "2.1.1"

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
    pyz_out: bool = False,
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

    Returns:
        str: Python modules compiled into single file contents.
    """
    if pyz_out:
        import scriptmerge.merge2 as merge
    else:
        import scriptmerge.merge1 as merge
    return merge.script(
        path=path,
        add_python_modules=add_python_modules,
        add_python_paths=add_python_paths,
        python_binary=python_binary,
        copy_shebang=copy_shebang,
        exclude_python_modules=exclude_python_modules,
        clean=clean,
    )
