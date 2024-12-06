import argparse
import sys
import pytest
from unittest import mock
from scriptmerge.main import main, _parse_args, _open_output

# FILE: scriptmerge/test_main.py


def test_parse_args_no_args():
    sys.argv = ["scriptmerge"]
    args = _parse_args()
    assert args is None


def test_parse_args_with_args():
    sys.argv = [
        "scriptmerge",
        "myscript.py",
        "-a",
        "module1",
        "-e",
        "module2",
        "-p",
        "path1",
        "-b",
        "python3",
        "-o",
        "output.txt",
        "-s",
        "-c",
        "-z",
    ]
    args = _parse_args()
    assert args.script == "myscript.py"
    assert args.add_python_module == ["module1"]
    assert args.exclude_python_module == ["module2"]
    assert args.add_python_path == ["path1"]
    assert args.python_binary == "python3"
    assert args.output_file == "output.txt"
    assert args.copy_shebang is True
    assert args.clean is True
    assert args.pyz_out is True


def test_open_output_stdout():
    args = argparse.Namespace(output_file=None, pyz_out=False)
    output = _open_output(args)
    assert output == sys.stdout


def test_open_output_stdout_buffer():
    args = argparse.Namespace(output_file=None, pyz_out=True)
    output = _open_output(args)
    assert output == sys.stdout.buffer


def test_open_output_file():
    args = argparse.Namespace(output_file="output.txt", pyz_out=False)
    with mock.patch("builtins.open", mock.mock_open()) as mocked_open:
        output = _open_output(args)
        mocked_open.assert_called_once_with("output.txt", "w")
        assert output == mocked_open()


def test_open_output_file_binary():
    args = argparse.Namespace(output_file="output.bin", pyz_out=True)
    with mock.patch("builtins.open", mock.mock_open()) as mocked_open:
        output = _open_output(args)
        mocked_open.assert_called_once_with("output.bin", "wb")
        assert output == mocked_open()


def test_main_with_args():
    sys.argv = ["scriptmerge", "myscript.py"]
    args = argparse.Namespace(
        script="myscript.py",
        add_python_module=[],
        exclude_python_module=[],
        add_python_path=[],
        python_binary=None,
        output_file=None,
        copy_shebang=False,
        clean=False,
        pyz_out=False,
    )
    with mock.patch("scriptmerge.main._parse_args", return_value=args):
        with mock.patch(
            "scriptmerge.main._open_output", return_value=mock.Mock()
        ) as mocked_open_output:
            with mock.patch("scriptmerge.script", return_value="output"):
                with mock.patch("sys.stdout", new_callable=mock.Mock()):
                    result = main()
                    assert result == 0
                    mocked_open_output().write.assert_called_once_with("output")
