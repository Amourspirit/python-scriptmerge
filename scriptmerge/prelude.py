import contextlib as __scriptmerge_contextlib


@__scriptmerge_contextlib.contextmanager
def __scriptmerge_temporary_dir():
    import tempfile
    import shutil

    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)


with __scriptmerge_temporary_dir() as __scriptmerge_working_dir:

    def __scriptmerge_write_module(path, contents):
        import os, os.path

        def make_package(path):
            parts = path.split("/")
            partial_path = __scriptmerge_working_dir
            for part in parts:
                partial_path = os.path.join(partial_path, part)
                if not os.path.exists(partial_path):
                    os.mkdir(partial_path)
                    with open(os.path.join(partial_path, "__init__.py"), "wb") as f:
                        f.write(b"\n")

        make_package(os.path.dirname(path))

        full_path = os.path.join(__scriptmerge_working_dir, path)
        with open(full_path, "wb") as module_file:
            module_file.write(contents)

    import sys as __scriptmerge_sys

    __scriptmerge_sys.path.insert(0, __scriptmerge_working_dir)
