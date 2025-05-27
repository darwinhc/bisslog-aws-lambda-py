from .lambda_handler_generator_base import command_lambda_handler_generator_base



def command_lambda_handler_generator_manager_saver(subparsers):
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
