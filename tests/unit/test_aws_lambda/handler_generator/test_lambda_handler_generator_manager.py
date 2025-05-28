import pytest
from unittest.mock import MagicMock, call
from bisslog_aws_lambda.aws_lambda.lambda_handler_generator_manager import LambdaHandlerGeneratorManager


@pytest.fixture
def mock_generate_handler():
    return MagicMock(return_value="def lambda_handler(event, context): pass")


@pytest.fixture
def mock_resolver():
    return MagicMock(return_value="handled")


@pytest.fixture
def mock_service_info():
    info = MagicMock()
    info.use_cases = {"get_user": MagicMock(triggers=["t"])}
    return info


@pytest.fixture
def mock_use_cases():
    uc = MagicMock()
    uc.name = "get_user"
    return {"get_user": uc}


@pytest.fixture
def mock_metadata(monkeypatch, mock_service_info, mock_use_cases):
    read_mock = MagicMock()
    read_mock.return_value.declared_metadata = mock_service_info
    read_mock.return_value.discovered_use_cases = mock_use_cases
    monkeypatch.setattr("bisslog_aws_lambda.aws_lambda.lambda_handler_generator_manager.read_full_service_metadata", read_mock)
    return read_mock


def test_handler_generator_manager_calls_all_components(
    mock_generate_handler, mock_resolver, mock_metadata
):
    manager = LambdaHandlerGeneratorManager(
        resolver=mock_resolver,
        generate_handler_resolver=mock_generate_handler
    )

    manager(metadata_file="path.yaml", use_cases_folder_path="code/", encoding="utf-8")

    mock_generate_handler.assert_called_once()
    mock_resolver.assert_called_once()
    assert "lambda_handler" in mock_generate_handler.return_value


def test_filter_use_case_applies(mock_generate_handler, mock_resolver, mock_metadata):
    manager = LambdaHandlerGeneratorManager(
        resolver=mock_resolver,
        generate_handler_resolver=mock_generate_handler
    )

    manager(metadata_file="x", use_cases_folder_path="y", filter_uc="get")

    mock_generate_handler.assert_called_once()
    mock_resolver.assert_called_once()
