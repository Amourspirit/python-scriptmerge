import pytest
import os
import platform
import shutil
import tempfile
import subprocess
import contextlib
import re
import stat

import stickytape
from test_scripts import root as test_script_root


@contextlib.contextmanager
def temporary_directory():
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)


@contextlib.contextmanager
def temporary_script(contents):
    with temporary_directory() as dir_path:
        path = os.path.join(dir_path, "script")
        with open(path, "w") as script_file:
            script_file.write(contents)

        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)
        yield path


@pytest.fixture(scope="function")
def tmp_dir_fn():
    result = tempfile.mkdtemp()
    yield result
    if os.path.exists(result):
        shutil.rmtree(result, ignore_errors=True)


@pytest.fixture(scope="session")
def run_shell_cmd() -> bytes:
    def run_shell(cmd) -> str:
        # run shell command
        result = subprocess.check_output(cmd)
        return result

    return run_shell


@pytest.fixture(scope="session")
def chk_script_output(find_script, run_shell_cmd, is_windows):
    def script_output(script_path, expected_output, expected_modules=None, **kwargs):
        result = stickytape.script(find_script(script_path), **kwargs)

        if expected_modules is not None:
            actual_modules = set(re.findall(r"__stickytape_write_module\('([^']*)\.py'", result))
            assert set(expected_modules) == actual_modules

        with temporary_script(result) as script_file_path:
            try:
                if is_windows:
                    command = ["py", script_file_path]
                else:
                    command = [script_file_path]
                output = run_shell_cmd(command).replace(b"\r\n", b"\n")
            except:
                for index, line in enumerate(result.splitlines()):
                    print((index + 1), line)
                raise
        assert expected_output == output

    return script_output


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
