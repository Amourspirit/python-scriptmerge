from __future__ import annotations
import pytest
import os
import platform
from test_scripts import root as test_script_root
import zipfile
from pathlib import Path


@pytest.fixture(scope="session")
def find_script():
    def _find_script(path):
        return os.path.join(test_script_root, path)

    return _find_script


@pytest.fixture(scope="session")
def is_windows():
    return platform.system() == "Windows"


@pytest.fixture(scope="session")
def find_site_packages():
    def _find_site_packages(root):
        paths = []

        for dir_path, dir_names, file_names in os.walk(root):
            for dir_name in dir_names:
                path = os.path.join(dir_path, dir_name)
                if dir_name == "site-packages" and os.listdir(path):
                    paths.append(path)

        if len(paths) == 1:
            return paths[0]
        else:
            raise ValueError("Multiple site-packages found: {}".format(paths))

    return _find_site_packages


@pytest.fixture(scope="session")
def venv_python_binary_path(is_windows):
    def _venv_python_binary_path(venv_path):
        if is_windows:
            bin_directory = "Scripts"
        else:
            bin_directory = "bin"

        return os.path.join(venv_path, bin_directory, "python")

    return _venv_python_binary_path


@pytest.fixture
def unzip_file_in_tmp(tmp_path):
    def _unzip_file(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmp_path)
        return tmp_path

    return _unzip_file


@pytest.fixture
def write_file_tmp(tmp_path):
    def _write_file_tmp(file_name: str | Path, contents: str | bytes):
        file_path = tmp_path / file_name
        if isinstance(contents, bytes):
            mode = "wb"
        else:
            mode = "w"
        with open(file_path, mode) as file:
            file.write(contents)
        return str(file_path)

    return _write_file_tmp
