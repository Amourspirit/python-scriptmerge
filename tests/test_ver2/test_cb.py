from __future__ import annotations
from typing import Any, cast, Dict
import pytest
from pathlib import Path

if __name__ == "__main__":
    pytest.main(["-v", __file__])
import scriptmerge
from scriptmerge.merge2 import script


def test_cb_python_paths(find_script):
    """
    Test that using a callback that the python paths can be set.
    """
    paths = ["/not_real/usr/local/lib/python3.9/site-packages"]
    event_triggered = False

    def cb(source: Any, args: scriptmerge.EventArgs):
        nonlocal paths, event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATED_PYTHON_PATHS:
            ev_args = cast(Dict[str, Any], args.event_data)
            assert paths[0] in ev_args["python_paths"]
            ev_args["python_paths"].remove(paths[0])
            event_triggered = True

    script_path: str = find_script("single_file/hello")
    _ = script(
        path=script_path,
        add_python_paths=paths,
        callback=cb,
    )
    assert event_triggered


def test_cb_set_init_contents(find_script, unzip_file_in_tmp, write_file_tmp):
    """
    Test that using a callback that the contents of the __init__.py file can be set.
    """
    event_triggered = False

    def cb(source: Any, args: scriptmerge.EventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_INIT_PY_FILE:
            ev_args = cast(Dict[str, Any], args.event_data)
            ev_args["contents"] = "print('Hello World')"
            event_triggered = True

    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    file_name = "script_mod.pyz"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered
    bytes_file = write_file_tmp(file_name, output)
    bytes_pth = Path(bytes_file)
    assert bytes_pth.exists()
    assert bytes_pth.stat().st_size > 0
    assert bytes_pth.stat().st_size == len(output)

    un_zip_dir = Path(unzip_file_in_tmp(bytes_file))
    assert un_zip_dir.exists()

    with open(un_zip_dir / "__init__.py", "r", encoding="utf-8") as f:
        contents = f.read()
        assert contents == "print('Hello World')"


def test_cb_generating_main_py_file(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.EventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_MAIN_PY_FILE:
            ev_args = cast(Dict[str, Any], args.event_data)
            assert ev_args["path"] == script_path
            assert len(ev_args["dir"]) > 0
            event_triggered = True

    _ = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered


def test_cb_generated_main_py_file(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.EventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATED_MAIN_PY_FILE_CONTENT:
            ev_args = cast(Dict[str, Any], args.event_data)
            contents: str = ev_args["contents"]
            assert len(contents) > 0
            ev_args["contents"] = "print('Hello World')"
            event_triggered = True

    file_name = "script_mod.pyz"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered

    bytes_file = write_file_tmp(file_name, output)
    bytes_pth = Path(bytes_file)
    assert bytes_pth.exists()
    assert bytes_pth.stat().st_size > 0
    assert bytes_pth.stat().st_size == len(output)

    un_zip_dir = Path(unzip_file_in_tmp(bytes_file))
    assert un_zip_dir.exists()

    with open(un_zip_dir / "__main__.py", "r", encoding="utf-8") as f:
        contents = f.read()
        assert contents == "print('Hello World')"


def test_cb_generated_shebang(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATED_SHEBANG:
            ev_args = cast(Dict[str, Any], args.event_data)
            shebang: str = ev_args["shebang"]
            assert len(shebang) > 0
            event_triggered = True

    _ = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered


def test_cb_generated_shebang_canceled(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATED_SHEBANG:
            ev_args = cast(Dict[str, Any], args.event_data)
            shebang: str = ev_args["shebang"]
            assert len(shebang) > 0
            args.cancel = True
            event_triggered = True

    file_name = "script_mod.pyz"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered

    bytes_file = write_file_tmp(file_name, output)
    bytes_pth = Path(bytes_file)
    assert bytes_pth.exists()
    assert bytes_pth.stat().st_size > 0
    assert bytes_pth.stat().st_size == len(output)

    un_zip_dir = Path(unzip_file_in_tmp(bytes_file))
    assert un_zip_dir.exists()

    with open(un_zip_dir / "__main__.py", "r", encoding="utf-8") as f:
        contents = f.read()
        assert not contents.startswith("#!")


def test_cb_generating_for_file(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_FOR_FILE:
            event_triggered = True

    _ = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered


def test_cb_generating_for_module(find_script, unzip_file_in_tmp, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_FOR_MODULE:
            event_triggered = True

    _ = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered
