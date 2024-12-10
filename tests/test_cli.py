import argparse
import sys
import pytest
from unittest import mock
from scriptmerge.main import main, _open_output

if __name__ == "__main__":
    pytest.main(["-v", __file__])
# FILE: scriptmerge/test_main.py


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
