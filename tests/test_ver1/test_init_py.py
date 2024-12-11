from __future__ import annotations
from typing import Any, cast, Dict
import pytest
from pathlib import Path

if __name__ == "__main__":
    pytest.main(["-v", __file__])
import scriptmerge
from scriptmerge.merge_py import script


def test_empty_init_py(find_script):
    script_path: str = find_script("single_file/hello")
    output = script(
        path=script_path,
        include_init_py=True,
    )
    assert "__scriptmerge_write_module('__init__.py', b'')" in output


def test_no_init_py(find_script):
    script_path: str = find_script("single_file/hello")
    output = script(
        path=script_path,
        include_init_py=False,
    )
    assert output
    assert "__scriptmerge_write_module('__init__.py', b'')" not in output


def test_cb_init_py(find_script):
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_INIT_PY_FILE:
            ev_args = cast(Dict[str, Any], args.event_data)
            content: str = ev_args["content"]
            assert len(content) == 0
            ev_args["content"] = "print('Hello')"
            event_triggered = True

    script_path: str = find_script("single_file/hello")
    output = script(
        path=script_path,
        include_init_py=True,
        callback=cb,
    )
    assert event_triggered
    assert "__scriptmerge_write_module('__init__.py', b\"print('Hello')\\n\")" in output


def test_cb_init_py_canceled(find_script):
    event_triggered = False

    def cb(source: Any, args: scriptmerge.CancelEventArgs):
        nonlocal event_triggered
        if args.name == scriptmerge.CALLBACK_GENERATING_INIT_PY_FILE:
            ev_args = cast(Dict[str, Any], args.event_data)
            content: str = ev_args["content"]
            assert len(content) == 0
            ev_args["content"] = "print('Hello')"
            args.cancel = True
            event_triggered = True

    script_path: str = find_script("single_file/hello")
    output = script(
        path=script_path,
        include_init_py=True,
        callback=cb,
    )
    assert event_triggered
    assert "__scriptmerge_write_module('__init__.py'" not in output
