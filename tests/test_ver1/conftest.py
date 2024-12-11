import pytest
import os
import sys
import subprocess
import re
import stat

import scriptmerge


@pytest.fixture(scope="session")
def temporary_script(tmp_path_factory: pytest.TempPathFactory):
    fn = tmp_path_factory.mktemp("script_dir") / "script"

    def _temporary_script(contents):
        with open(fn, "w", encoding="utf-8", newline="\n") as script_file:
            script_file.write(contents)

        st = os.stat(fn)
        fn.chmod(st.st_mode | stat.S_IEXEC)
        return fn

    return _temporary_script


@pytest.fixture
def capture_stdout(monkeypatch) -> dict:
    buffer = {"stdout": "", "write_calls": 0}

    def fake_write(s):
        buffer["stdout"] += s
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_write)
    return buffer


@pytest.fixture(scope="session")
def run_shell_cmd() -> bytes:
    def run_shell(cmd) -> str:
        result = subprocess.check_output(cmd)
        return result

    return run_shell


@pytest.fixture(scope="session")
def get_script_str(find_script):
    def _get_script_str(script_path, **kwargs):
        result = scriptmerge.script(find_script(script_path), **kwargs)
        return result

    return _get_script_str


@pytest.fixture(scope="session")
def get_expected_modules():
    def _get_expected_modules(script_str):
        return set(re.findall(r"__scriptmerge_write_module\('([^']*)\.py'", script_str))

    return _get_expected_modules


@pytest.fixture(scope="session")
def chk_script_output(
    get_script_str, run_shell_cmd, is_windows, temporary_script, get_expected_modules
):
    def script_output(script_path, expected_output, expected_modules=None, **kwargs):
        result = get_script_str(script_path, **kwargs)

        if expected_modules is not None:
            actual_modules = get_expected_modules(result)
            assert set(expected_modules) == actual_modules

        script_file_path = str(temporary_script(result))
        try:
            if is_windows:
                command = [sys.executable, script_file_path]
            else:
                command = [script_file_path]
            output = run_shell_cmd(command).replace(b"\r\n", b"\n")
        except:
            for index, line in enumerate(result.splitlines()):
                print((index + 1), line)
            raise
        assert expected_output == output

    return script_output
