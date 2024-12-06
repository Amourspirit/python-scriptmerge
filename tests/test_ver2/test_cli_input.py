import pytest
from pathlib import Path
import subprocess


def test_cli_single_file(find_script, tmp_path):
    script_path: str = find_script("single_file/hello")
    temp_file: Path = tmp_path / "hello.pyz"
    assert temp_file.exists() is False
    cnd_args = [
        "scriptmerge",
        script_path,
        "-o",
        str(temp_file),
        "-s",
        "-z",
    ]
    subprocess.run(cnd_args)
    assert temp_file.exists()


def test_cli_explicit_rel_import_from_parent_pkg(find_script, tmp_path):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    temp_file: Path = tmp_path / "hello.pyz"
    assert temp_file.exists() is False
    cnd_args = [
        "scriptmerge",
        script_path,
        "-o",
        str(temp_file),
        "-s",
        "-z",
    ]
    subprocess.run(cnd_args)
    assert temp_file.exists()
