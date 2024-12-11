from __future__ import annotations
from typing import cast, List, TYPE_CHECKING
import pytest
import os
import sys
import subprocess
import stat
import zipfile
import tempfile

import scriptmerge

if TYPE_CHECKING:
    import bytes  # type: ignore # noqa: F401
    import Set


@pytest.fixture(scope="session")
def temporary_script(tmp_path_factory: pytest.TempPathFactory):
    fn = tmp_path_factory.mktemp("script_dir") / "script"

    def _temporary_script(contents):
        with open(fn, "wb") as script_file:
            script_file.write(contents)

        st = os.stat(fn)
        fn.chmod(st.st_mode | stat.S_IEXEC)
        return fn

    return _temporary_script


@pytest.fixture(scope="session")
def read_binary_file():
    def _read_binary_file(file_path):
        with open(file_path, "rb") as file:
            return file.read()

    return _read_binary_file


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
def get_script_from_pyz():

    def _get_mods(pyz_path):
        def extract_zipapp(zipapp_path: str, extract_to: str) -> None:
            with zipfile.ZipFile(zipapp_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)

        # def read_python_scripts(extract_to: str) -> None:
        #     for root, _, files in os.walk(extract_to):
        #         for file in files:
        #             if file.endswith(".py"):
        #                 file_path = os.path.join(root, file)
        #                 with open(file_path, "r") as f:
        #                     print(f"Contents of {file_path}:")
        #                     print(f.read())

        def get_python_module_names(extract_to: str) -> Set[str]:
            module_names = set()
            for root, _, files in os.walk(extract_to):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        module_name = os.path.splitext(
                            os.path.relpath(file_path, extract_to)
                        )[0].replace(os.sep, ".")
                        if module_name == "__main__":
                            continue
                        module_names.add(module_name)
            return module_names

        with tempfile.TemporaryDirectory() as temp_dir:
            extract_zipapp(pyz_path, temp_dir)
            # read_python_scripts(temp_dir)
            mod_names = get_python_module_names(temp_dir)

        # result = scriptmerge.script(find_script(script_path), pyz_out=True, **kwargs)
        # return result
        return mod_names

    return _get_mods


@pytest.fixture(scope="session")
def get_script_str_from_pyz():

    def _get_mods(pyz_path):
        def extract_zipapp(zipapp_path: str, extract_to: str) -> None:
            with zipfile.ZipFile(zipapp_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)

        def read_python_script(file_path: str) -> str:
            with open(file_path, "r", encoding="utf-8") as f:
                multi_line_string = f.read()
            single_line_string = multi_line_string.replace("\n", "\\n").replace(
                "\t", "\\t"
            )
            return single_line_string

        def get_python_module_names(extract_to: str) -> List[str]:
            str_results = []
            for root, _, files in os.walk(extract_to):
                for file in files:
                    if file == "__main__.py":
                        continue
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        code = read_python_script(file_path)
                        str_results.append(code)
            return str_results

        with tempfile.TemporaryDirectory() as temp_dir:
            extract_zipapp(pyz_path, temp_dir)
            results = get_python_module_names(temp_dir)

        # result = scriptmerge.script(find_script(script_path), pyz_out=True, **kwargs)
        # return result
        delimiter = "<DELIM>"
        joined_results = delimiter.join(results)
        return joined_results

    return _get_mods


@pytest.fixture(scope="session")
def get_script_bytes(find_script):
    def _get_script_bytes(script_path, **kwargs):
        result = scriptmerge.script(find_script(script_path), pyz_out=True, **kwargs)
        return result

    return _get_script_bytes


@pytest.fixture(scope="session")
def get_expected_modules(get_script_from_pyz, find_script, temporary_script):

    def _get_expected_modules(script_path):
        if not script_path:
            return set()
        result = scriptmerge.script(find_script(script_path), pyz_out=True)
        script_file_path = str(temporary_script(result))
        return get_script_from_pyz(script_file_path)
        # return set(re.findall(r"__scriptmerge_write_module\('([^']*)\.py'", script_str))

    return _get_expected_modules


@pytest.fixture(scope="session")
def get_script_str(find_script, get_script_str_from_pyz, temporary_script):
    def _get_script_str(script_path, **kwargs):
        result = scriptmerge.script(find_script(script_path), pyz_out=True, **kwargs)
        script_file_path = str(temporary_script(result))
        result = get_script_str_from_pyz(script_file_path)
        return result

    return _get_script_str


@pytest.fixture(scope="session")
def chk_script_output(
    get_script_bytes,
    run_shell_cmd,
    is_windows,
    temporary_script,
    get_expected_modules,
):
    def script_output(script_path, expected_output, expected_modules=None, **kwargs):
        result = get_script_bytes(script_path, **kwargs)
        script_file_path = str(temporary_script(result))

        try:
            if is_windows:
                command = [sys.executable, script_file_path]
            else:
                command = [script_file_path]
            output = cast("bytes", run_shell_cmd(command).replace(b"\r\n", b"\n"))
        except:
            for index, line in enumerate(result.splitlines()):
                print((index + 1), line)
            raise

        if expected_modules is not None:
            # str_result = cast("bytes", get_script_from_pyz(script_file_path))
            actual_modules = get_expected_modules(script_path)
            # actual_modules = get_expected_modules(script_file_path)
            assert set(expected_modules) == actual_modules
        assert expected_output == output

    return script_output
