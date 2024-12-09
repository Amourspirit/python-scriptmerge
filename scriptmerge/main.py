import argparse
import sys

from scriptmerge import __version__
from scriptmerge.merge1 import script as merge1_script
from scriptmerge.merge2 import script as merge2_script


# region Main
def main() -> int:
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest="command", required=True)
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

    # Check if a subcommand was provided
    if args.command is None:
        # Set default subcommand to 'compile_original'
        args.command = "compile_original"
        # Parse the arguments again with the default subparser
        subparser = {
            "compilepy": cmd_compile,
            "compilepyz": cmd_compile_pyz,
            "compile_original": cmd_compile_orig,
        }[args.command]
        args = subparser.parse_args(remaining_args, namespace=args)

    if len(sys.argv) <= 1:
        parser.print_help()
        return 0
    _args_process_cmd(args)
    return 0


# endregion Main

# region Output


def _open_output(args):
    if args.output_file is None:
        if args.pyz_out:
            return sys.stdout.buffer
        return sys.stdout
    else:
        if args.pyz_out:
            return open(args.output_file, "wb")
        return open(args.output_file, "w")


# endregion Output


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
    output_file = _open_output(args)
    output = merge1_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
        pyz_out=args.pyz_out,
    )
    output_file.write(output)
    return 0


def _args_compile_py_action(args: argparse.Namespace) -> int:
    output_file = _open_output(args)
    output = merge1_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
        pyz_out=args.pyz_out,
        include_main_py=args.main_py,
    )
    output_file.write(output)
    return 0


def _args_compile_pyz_action(args: argparse.Namespace) -> int:
    output_file = _open_output(args)
    output = merge2_script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang,
        exclude_python_modules=args.exclude_python_module,
        clean=args.clean,
        pyz_out=args.pyz_out,
        include_main_py=args.no_main_py,
    )
    output_file.write(output)
    return 0


# endregion Argument actions

if __name__ == "__main__":
    raise SystemExit(main())
