"""
Command-line interface (CLI) for the `bisslog_aws_lambda` package.

This module provides a CLI to interact with the `bisslog_aws_lambda` package, allowing users
to analyze metadata files in various formats (e.g., YAML, JSON) and perform other related tasks.

Commands
--------
- `analyze_metadata`: Analyze a metadata file and generate a report.
"""
import argparse
import sys
import os
import traceback

from .lambda_aws_packager import command_lambda_aws_packager
from .lambda_handler_generator_manager_printer import \
    command_lambda_handler_generator_manager_printer
from .lambda_handler_generator_manager_saver import command_lambda_handler_generator_manager_saver
from ..aws_lambda.lambda_aws_packager import lambda_aws_packager
from ..aws_lambda.lambda_handler_generator_manager import (
    lambda_handler_generator_manager_saver,
    lambda_handler_generator_manager_printer
)



def main():
    """Entry point for the CLI.

    Parses command-line arguments and executes the corresponding command.

    Commands
    --------
    analyze_metadata : str
        Command to analyze a metadata file with the following parameters:
        - path: Path to the metadata file (required)
        - format_file: File format (yaml|json|xml, default: yaml)
        - encoding: File encoding (default: utf-8)
        - min_warnings: Minimum warning percentage allowed (optional)

    Examples
    --------
    $ bisslog_aws_lambda analyze_metadata /path/to/file.yaml --min-warnings 0.5

    Raises
    ------
    SystemExit
        If an invalid command is provided (exit code 1) or execution fails (exit code 2).
    """
    project_root = os.getcwd()

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    parser = argparse.ArgumentParser(prog="bisslog_aws_lambda")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    subparsers = parser.add_subparsers(dest="command", required=True)

    command_lambda_aws_packager(subparsers)
    command_lambda_handler_generator_manager_saver(subparsers)
    command_lambda_handler_generator_manager_printer(subparsers)

    args = parser.parse_args()

    try:
        if args.command == "generate_lambda_zips":
            lambda_aws_packager(args.handler_name, args.src_folders, args.handlers_folder)
        elif args.command == "generate_lambda_handlers":
            lambda_handler_generator_manager_saver(
                metadata_file=args.metadata_file,
                use_cases_folder_path=args.use_cases_folder_path,
                filter_uc=args.filter_uc,
                encoding=args.encoding,
                target_folder=args.target_folder
            )
        elif args.command == "print_lambda_handlers":
            lambda_handler_generator_manager_printer(
                metadata_file=args.metadata_file,
                use_cases_folder_path=args.use_cases_folder_path,
                filter_uc=args.filter_uc,
                encoding=args.encoding
            )
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(2)
