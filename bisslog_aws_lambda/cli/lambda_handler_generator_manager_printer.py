"""
CLI command to print generated AWS Lambda handlers to the console.

This module defines the `print_lambda_handlers` subcommand that can be used
to inspect the generated handler code without saving it to disk.
"""

from .lambda_handler_generator_base import command_lambda_handler_generator_base


def command_lambda_handler_generator_manager_printer(subparsers):
    """
    Registers the `print_lambda_handlers` command in the CLI.

    This subcommand configures the CLI to invoke the Lambda handler generator
    and print the results to standard output, instead of saving them.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparser object from an `ArgumentParser` to which the command is added.
    """
    command_parser = subparsers.add_parser(
        "print_lambda_handlers",
        help="Generates lambda handler found in metadata and code"
    )
    command_lambda_handler_generator_base(command_parser)
