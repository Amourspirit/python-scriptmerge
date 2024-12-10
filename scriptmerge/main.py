import argparse
import sys

from scriptmerge import __version__
from scriptmerge.merge1 import script as merge1_script
from scriptmerge.merge2 import script as merge2_script
import os


# region Main
def main() -> int:
    # List of valid subcommands
    subcommands = set(["version", "compilepy", "compilepyz", "compile_original"])

    # Preprocess sys.argv to insert default subcommand if necessary
    if len(sys.argv) > 1:
        if sys.argv[1] not in subcommands:
            # Insert default subcommand
            sys.argv.insert(1, "compile_original")
    else:
        # No arguments provided; use default subcommand
        sys.argv.insert(1, "compile_original")

    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest="command", required=False)
    cmd_version = subparser.add_parser(
        name="version", help="Gets the version of the scriptmerge"
    )
    cmd_compile = subparser.add_parser(
        name="compilepy", help="compile into a single '.py' file"
    )

    cmd_compile_pyz = subparser.add_parser(
        name="compilepyz", help="compile into a single '.pyz' file"
    )
    cmd_compile_orig = subparser.add_parser(
        name="compile_original",
        help="compile into a single '.py' or '.pyz' file. Backwards compatibility. Recommended to use 'compilepy' or 'compilepyz'",
    )
    _args_compile_pyz(cmd_compile_pyz)
    _args_compile_py(cmd_compile)
    _args_compile_original(cmd_compile_orig)

    # Parse the initial arguments
    args, remaining_args = parser.parse_known_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        return 0
    _args_process_cmd(args)
    return 0


# endregion Main


# region helper methods
def is_posix() -> bool:
    return os.pathsep == ":"


# endregion helper methods


# region Argument parsing
def _args_compile_pyz(parser: argparse.ArgumentParser) -> None:
    _parse_args_common(parser)
    parser.add_argument(
        "-n",
        "--no-main-py",
        action="store_false",
        help="Include '__main__.py' file in the output. Default is True.",
    )


def _args_compile_py(parser: argparse.ArgumentParser) -> None:
    _parse_args_common(parser)
    parser.add_argument(
        "-y",
        "--main-py",
        action="store_true",
        help="Include '__main__.py' file in the output. Default is False.",
    )


def _args_compile_original(parser: argparse.ArgumentParser) -> None:
    _parse_args_common(parser)
    parser.add_argument(
        "-z", "--pyz-out", action="store_true", help="Output as a binary pyz file"
    )


def _parse_args_common(parser: argparse.ArgumentParser) -> None:

    parser.add_argument("script", help="Path to the entry point script")
    parser.add_argument(
        "-a",
        "--add-python-module",
        action="append",
        default=[],
        help="Add python modules to the output",
    )
    parser.add_argument(
        "-e",
        "--exclude-python-module",
        action="append",
        default=[],
        help="Exclude python modules from the output",
    )
    parser.add_argument(
        "-p",
        "--add-python-path",
        action="append",
        default=[],
        help="Add python paths to the output",
    )
    parser.add_argument(
        "-b", "--python-binary", help="Include a specific python binary in the output"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Output file such as script.py or script.pyz when using -z",
    )
    parser.add_argument(
        "-s",
        "--copy-shebang",
        action="store_true",
        help="Copy the shebang from the script",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Remove docstring and comments from the script",
    )
    if is_posix():
        parser.add_argument(
            "-x",
            "--make-executable",
            action="store_true",
            help="Make the output file executable",
        )

    # if len(sys.argv) <= 1:
    #     parser.print_help()
    #     return None


# endregion Argument parsing


# region Argument actions
def _args_process_cmd(args: argparse.Namespace) -> int:
    if args.command == "compile_original":
        return _args_compile_default_action(args)
    elif args.command == "compilepy":
        return _args_compile_py_action(args)
    elif args.command == "compilepyz":
        return _args_compile_pyz_action(args)
    elif args.command == "version":
        print(__version__)
    return 0


def _args_compile_default_action(args: argparse.Namespace) -> int:
    output = merge1_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
    )
    with open(args.output_file, "w") as output_file:
        output_file.write(output)
    make_executable = getattr(args, "make_executable", False)  # only posix
    if make_executable:
        os.chmod(args.output_file, 0o755)
    return 0


def _args_compile_py_action(args: argparse.Namespace) -> int:
    output = merge1_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
        include_main_py=args.main_py,
    )
    with open(args.output_file, "w") as output_file:
        output_file.write(output)
    make_executable = getattr(args, "make_executable", False)  # only posix
    if make_executable:
        os.chmod(args.output_file, 0o755)
    return 0


def _args_compile_pyz_action(args: argparse.Namespace) -> int:
    # output_file = _open_output(args)
    output = merge2_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
        include_main_py=args.no_main_py,
    )
    # output_file.write(output)
    with open(args.output_file, "wb") as output_file:
        output_file.write(output)
    make_executable = getattr(args, "make_executable", False)  # only posix
    if make_executable:
        os.chmod(args.output_file, 0o755)
    return 0


# endregion Argument actions

if __name__ == "__main__":
    raise SystemExit(main())
