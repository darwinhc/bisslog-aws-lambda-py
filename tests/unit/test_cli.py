import pytest
import sys
from unittest.mock import patch, MagicMock


@pytest.fixture
def import_main():
    from bisslog_aws_lambda.cli import main
    return main


@patch("bisslog_aws_lambda.cli.lambda_aws_packager")
def test_generate_lambda_zips_command(mock_packager, import_main):
    test_args = ["bisslog_aws_lambda", "generate_lambda_zips", "--handler-name", "my_handler"]
    with patch.object(sys, "argv", test_args):
        import_main()
        mock_packager.assert_called_once()


@patch("bisslog_aws_lambda.cli.lambda_handler_generator_manager_saver")
def test_generate_lambda_handlers_command(mock_manager, import_main):
    test_args = [
        "bisslog_aws_lambda", "generate_lambda_handlers",
        "--metadata-file", "file.yaml",
        "--use-cases-folder-path", "src/use_cases",
        "--target-folder", "generated"
    ]
    with patch.object(sys, "argv", test_args):
        import_main()
        mock_manager.assert_called_once()


@patch("bisslog_aws_lambda.cli.lambda_handler_generator_manager_printer")
def test_print_lambda_handlers_command(mock_printer, import_main):
    test_args = [
        "bisslog_aws_lambda", "print_lambda_handlers",
        "--metadata-file", "file.yaml",
        "--use-cases-folder-path", "src/use_cases"
    ]
    with patch.object(sys, "argv", test_args):
        import_main()
        mock_printer.assert_called_once()


@patch("bisslog_aws_lambda.cli.lambda_aws_packager", side_effect=RuntimeError("fail"))
def test_main_exits_on_error(mock_packager, import_main, capsys):
    test_args = ["bisslog_aws_lambda", "generate_lambda_zips", "--handler-name", "bad"]
    with patch.object(sys, "argv", test_args), pytest.raises(SystemExit) as e:
        import_main()
    assert e.value.code == 2
    _, err = capsys.readouterr()
    assert "Error: fail" in err
