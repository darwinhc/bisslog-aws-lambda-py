"""
CLI command to generate and save AWS Lambda handlers based on service metadata.

This module defines the `generate_lambda_handlers` subcommand, which generates
Lambda handler code for discovered use cases and saves the result to disk.
"""

from .lambda_handler_generator_base import command_lambda_handler_generator_base


def command_lambda_handler_generator_manager_saver(subparsers):
    """
    Registers the `generate_lambda_handlers` command in the CLI.

    This subcommand generates AWS Lambda handlers for all discovered use cases
    (based on metadata and code inspection) and writes them to a target folder.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparser object from an `ArgumentParser` to which the command is added.
    """
    command_parser = subparsers.add_parser(
        "generate_lambda_handlers",
        help="Generates lambda handler found in metadata and code"
    )
    command_lambda_handler_generator_base(command_parser)
    command_parser.add_argument(
        "--target-folder",
        help="Target folder to save the handler generator manager",
        default="framework/lambda_aws"
    )
