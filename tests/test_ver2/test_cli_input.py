from __future__ import annotations
import sys
import subprocess
import pytest
from pathlib import Path

if __name__ == "__main__":
    pytest.main([__file__])


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
    result = subprocess.run(cnd_args, capture_output=True, text=True)
    # print(result.stdout)
    print(result.stderr)
    assert temp_file.exists()


def test_cli_single_file_compilepyz(find_script, tmp_path):
    script_path: str = find_script("single_file/hello")
    temp_file: Path = tmp_path / "hello.pyz"
    assert temp_file.exists() is False
    cnd_args = [
        "scriptmerge",
        "compilepyz",
        script_path,
        "-o",
        str(temp_file),
        "-s",
    ]
    result = subprocess.run(cnd_args, capture_output=True, text=True)
    # print(result.stdout)
    print(result.stderr)
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
    result = subprocess.run(cnd_args, capture_output=True, text=True)
    # print(result.stdout)
    print(result.stderr)
    assert temp_file.exists()


def test_cli_explicit_rel_import_from_parent_pkg_compilepyz(find_script, tmp_path):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    temp_file: Path = tmp_path / "hello.pyz"
    assert temp_file.exists() is False
    cnd_args = [
        "scriptmerge",
        "compilepyz",
        script_path,
        "-o",
        str(temp_file),
        "-s",
    ]
    result = subprocess.run(cnd_args, capture_output=True, text=True)
    # print(result.stdout)
    print(result.stderr)
    assert temp_file.exists()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="This test is skipped on Windows"
)
def test_cli_make_executable(find_script, tmp_path):
    script_path: str = find_script("explicit_relative_import_from_parent_package/hello")
    temp_file: Path = tmp_path / "hello.pyz"
    assert temp_file.exists() is False
    cnd_args = [
        "scriptmerge",
        "compilepyz",
        script_path,
        "-o",
        str(temp_file),
        "-s",
        "-x",
    ]
    result = subprocess.run(cnd_args, capture_output=True, text=True)
    # print(result.stdout)
    print(result.stderr)
    assert temp_file.exists()
    assert temp_file.stat().st_mode & 0o111
