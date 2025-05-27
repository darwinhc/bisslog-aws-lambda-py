import argparse


def command_lambda_handler_generator_base(command_parser):
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
