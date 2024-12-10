from __future__ import annotations
from typing import Any, cast, Dict
import pytest
from pathlib import Path

if __name__ == "__main__":
    pytest.main(["-v", __file__])
import scriptmerge
from scriptmerge.merge1 import script


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


def test_cb_generated_shebang(find_script, write_file_tmp):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATED_SHEBANG:
            ev_args = cast(Dict[str, Any], args.event_data)
            shebang: str = ev_args["shebang"]
            assert len(shebang) > 0
            event_triggered = True

    file_name = "script_mod.py"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered

    str_file = write_file_tmp(file_name, output)
    str_pth = Path(str_file)
    assert str_pth.exists()
    assert str_pth.stat().st_size > 0

    with open(str_pth, "r", encoding="utf-8") as f:
        contents = f.read()
        assert contents.startswith("#!")


def test_cb_generated_shebang_canceled(find_script, write_file_tmp):
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

    file_name = "script_mod.py"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered

    str_file = write_file_tmp(file_name, output)
    str_pth = Path(str_file)
    assert str_pth.exists()
    assert str_pth.stat().st_size > 0

    with open(str_pth, "r", encoding="utf-8") as f:
        contents = f.read()
        assert not contents.startswith("#!")


def test_cb_generating_prelude(find_script, write_file_tmp):
    from scriptmerge.merge1 import _prelude

    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False
    prelude_str = _prelude()

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered, prelude_str
        if args.name == scriptmerge.CALLBACK_GENERATING_PRELUDE:
            ev_args = cast(Dict[str, Any], args.event_data)
            pre: str = ev_args["prelude"]
            assert pre == prelude_str
            event_triggered = True

    _ = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered


def test_cb_generating_prelude_change(find_script, write_file_tmp):

    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_PRELUDE:
            ev_args = cast(Dict[str, Any], args.event_data)
            ev_args["prelude"] = "# testing prelude\n"
            event_triggered = True

    file_name = "script_mod.py"
    output = script(
        path=script_path,
        callback=cb,
    )
    assert event_triggered

    str_file = write_file_tmp(file_name, output)
    str_pth = Path(str_file)
    assert str_pth.exists()
    assert str_pth.stat().st_size > 0

    with open(str_pth, "r", encoding="utf-8") as f:
        contents = f.read()
        assert contents.splitlines()[1] == "# testing prelude"


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
