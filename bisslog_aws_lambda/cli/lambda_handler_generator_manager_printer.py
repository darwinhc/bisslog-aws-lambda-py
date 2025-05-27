
from .lambda_handler_generator_base import command_lambda_handler_generator_base


def command_lambda_handler_generator_manager_saver(subparsers):
    command_parser = subparsers.add_parser(
        "print_lambda_handlers",
        help="Generates lambda handler found in metadata and code"
    )
    command_lambda_handler_generator_base(command_parser)
