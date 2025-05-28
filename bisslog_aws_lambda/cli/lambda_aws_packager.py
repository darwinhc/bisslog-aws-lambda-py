"""
Command registration for generating AWS Lambda deployment zip files.

This module defines the CLI command that allows users to package AWS Lambda handlers
along with their Python source code into `.zip` archives for deployment.
"""

def command_lambda_aws_packager(subparsers):
    """
    Registers the `generate_lambda_zips` subcommand in the CLI parser.

    This command allows the user to generate one or more Lambda deployment zip files
    by providing source folders and a handler name. The handler file is renamed
    as `lambda_function.py` in the resulting archive.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparser object from an `ArgumentParser` to which the command is added.

    CLI Arguments
    -------------
    --handler-name : str, optional
        The name of the handler file (without `.py`) to include in the zip (default: all handlers).
    --handlers-folder : str, optional
        Directory containing handler `.py` files (default: "framework/lambda_aws").
    --src-folders : List[str], optional
        One or more directories containing Python source code (default: ["src"]).
    """

    generate_lambda_zips = subparsers.add_parser("generate_lambda_zips",
                                                 help="Generate lambda zip files")

    generate_lambda_zips.add_argument("--handler-name", help="Handler name to generate zip for",
                                      default=None)
    generate_lambda_zips.add_argument("--handlers-folder", help="Folder containing handler files",
                                      default="framework/lambda_aws")
    generate_lambda_zips.add_argument(
        "--src-folders",
        help="List of source folders to include in the lambda zip",
        nargs="+",
        default=["src"],
    )
