


def command_lambda_aws_packager(subparsers):
    generate_lambda_zips = subparsers.add_parser("generate_lambda_zips", help="Generate lambda zip files")

    generate_lambda_zips.add_argument("--handler-name", help="Handler name to generate zip for", default=None)
    generate_lambda_zips.add_argument("--handlers-folder", help="Folder containing handler files", default="framework/lambda_aws")
    generate_lambda_zips.add_argument(
        "--src-folders",
        help="List of source folders to include in the lambda zip",
        nargs="+",
        default=["src"],
    )
