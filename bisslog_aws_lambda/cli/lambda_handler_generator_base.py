"""
Base CLI arguments for Lambda handler generator commands.

This module defines shared command-line arguments used by multiple subcommands
that generate AWS Lambda handlers from metadata and source code.
"""

import argparse


def command_lambda_handler_generator_base(command_parser):
    """
    Adds common arguments to a Lambda handler generator CLI command.

    This function is intended to be reused by multiple subcommands that need
    access to service metadata and use case discovery options.

    Parameters
    ----------
    command_parser : argparse.ArgumentParser
        The parser instance to which the common arguments will be added.

    CLI Arguments
    -------------
    --metadata-file : str, optional
        Path to the metadata file to analyze (YAML or JSON).
    --use-cases-folder-path : str, optional
        Path to the folder containing Python use case implementations.
    --filter-uc : str, optional
        substring to filter specific use cases by name.
    --encoding : str, optional
        Encoding to use when reading the metadata file (default: utf-8).
        Must be one of: 'utf-8', 'ascii', 'latin-1'.
    """
    command_parser.add_argument(
        "--metadata-file",
        help="Path to the metadata file to analyze",
        default=None,
    )

    command_parser.add_argument(
        "--use-cases-folder-path",
        help="Path to the folder containing use cases",
        default=None,
    )

    command_parser.add_argument(
        "--filter-uc",
        help="Optional filter to apply to use case names",
        default=None,
    )

    command_parser.add_argument(
        "--encoding",
        help="Encoding to read the metadata file (default: utf-8)",
        default="utf-8",
        type=lambda x: x if x.lower() in ['utf-8', 'ascii', 'latin-1']
        else argparse.ArgumentTypeError("Invalid encoding")
    )
