import argparse
import sys

import scriptmerge


def main() -> int:
    args = _parse_args()
    if not args:
        return 0
    output_file = _open_output(args)
    output = scriptmerge.script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
    )
    output_file.write(output)
    return 0


def _open_output(args):
    if args.output_file is None:
        return sys.stdout
    else:
        return open(args.output_file, "w")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("-a", "--add-python-module", action="append", default=[])
    parser.add_argument("-e", "--exclude-python-module", action="append", default=[])
    parser.add_argument("-p", "--add-python-path", action="append", default=[])
    parser.add_argument("-b", "--python-binary")
    parser.add_argument("-o", "--output-file")
    parser.add_argument("-s", "--copy-shebang", action="store_true")
    parser.add_argument("-c", "--clean", action="store_true")
    if len(sys.argv) <= 1:
        parser.print_help()
        return None
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
