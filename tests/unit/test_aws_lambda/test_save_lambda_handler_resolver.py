import os


from pathlib import Path
import shutil
import pytest
from unittest.mock import MagicMock

from bisslog_aws_lambda.aws_lambda.save_lambda_handler_resolver import SaveLambdaHandlerResolver


@pytest.fixture
def use_case_code_info():
    mock = MagicMock()
    mock.name = "my_use_case"
    return mock


@pytest.fixture
def service_info():
    return MagicMock()


@pytest.fixture
def handler_code():
    return 'def handler(event, context): return "ok"'


def delete_directory(directory: Path) -> None:
    if not directory.exists():
        return  # Silently ignore if it doesn't exist
    if directory.is_absolute():
        raise ValueError("Absolute paths are not allowed. Use a relative path instead.")

    if not directory.is_dir():
        raise ValueError(f"{directory} is not a directory.")

    shutil.rmtree(directory)




def test_saves_handler_to_relative_folder(monkeypatch, tmp_path, service_info, use_case_code_info, handler_code):
    monkeypatch.chdir(tmp_path)

    resolver = SaveLambdaHandlerResolver()
    path = os.path.join("temp", "handlers")
    result = resolver(service_info, use_case_code_info, handler_code, target_folder=path)

    path = Path(path)

    expected_file = path / "my_use_case_handler.py"
    assert expected_file.exists()
    assert expected_file.read_text() == handler_code
    assert result == "Handler saved to my_use_case_handler.py"

    # Assert __init__.py exists at every level

    buffer = None
    for part in path.parts:
        if buffer is None:
            buffer = Path(part)
        else:
            buffer = buffer / part
        assert (buffer / "__init__.py").exists()
    delete_directory(Path(path.parts[0]))


def test_uses_env_relative_folder(monkeypatch, tmp_path, service_info, use_case_code_info, handler_code):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BISSLOG_FOLDER_FRAMEWORKS", "my_framework")
    monkeypatch.setenv("BISSLOG_FOLDER_LAMBDA", "my_lambda")

    resolver = SaveLambdaHandlerResolver()
    result = resolver(service_info, use_case_code_info, handler_code)

    expected_path = tmp_path / "my_framework" / "my_lambda" / "my_use_case_handler.py"
    assert expected_path.exists()
    assert expected_path.read_text() == handler_code
    assert result == "Handler saved to my_use_case_handler.py"
    delete_directory(Path("my_framework"))


def test_does_not_overwrite_existing_file(monkeypatch, tmp_path, service_info, use_case_code_info, handler_code):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "handlers"
    folder.mkdir()
    existing_file = folder / "my_use_case_handler.py"
    existing_file.write_text("original content")

    resolver = SaveLambdaHandlerResolver()
    result = resolver(service_info, use_case_code_info, handler_code, target_folder="handlers")

    # Should not overwrite
    assert existing_file.read_text() == "original content"
    assert result == "Handler saved to my_use_case_handler.py"
    delete_directory(Path("handlers"))

def test_overwrite_existing_file(monkeypatch, tmp_path, service_info, use_case_code_info, handler_code):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "handlers"
    folder.mkdir()
    existing_file = folder / "my_use_case_handler.py"
    existing_file.write_text("original content")

    resolver = SaveLambdaHandlerResolver()
    result = resolver(service_info, use_case_code_info, handler_code, target_folder="handlers", overwrite=True)

    # Should not overwrite
    assert existing_file.read_text() == handler_code
    assert result == "Handler saved to my_use_case_handler.py"
    delete_directory(Path("handlers"))