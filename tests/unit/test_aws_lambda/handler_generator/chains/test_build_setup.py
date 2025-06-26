import pytest
from unittest.mock import Mock

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.build_setup import BuildSetup
from bisslog_aws_lambda.aws_lambda.handler_generator.aws_handler_gen_response import AWSHandlerGenResponse
from bisslog_schema.setup.runtime_type import RuntimeType


@pytest.fixture
def generator():
    return BuildSetup()


def test_none_setup_returns_none(generator):
    assert generator(None) is None


def test_setup_function_no_params(generator):
    mock_func = Mock()
    mock_func.module = "my_module"
    mock_func.function_name = "init_app"
    mock_func.n_params = 0

    mock_setup = Mock()
    mock_setup.setup_function = mock_func
    mock_setup.runtime = {}

    result = generator(mock_setup)

    assert isinstance(result, AWSHandlerGenResponse)
    assert result.build == "init_app()"
    assert result.importing == {"my_module": ["init_app"]}


def test_setup_function_one_param(generator):
    mock_func = Mock()
    mock_func.module = "init"
    mock_func.function_name = "bootstrap"
    mock_func.n_params = 1

    mock_setup = Mock()
    mock_setup.setup_function = mock_func
    mock_setup.runtime = {}

    result = generator(mock_setup)

    assert result.build == "bootstrap('lambda')"
    assert result.importing == {"init": ["bootstrap"]}


def test_setup_function_multiple_params(generator):
    mock_func = Mock()
    mock_func.module = "conf"
    mock_func.function_name = "setup_all"
    mock_func.n_params = 2

    mock_setup = Mock()
    mock_setup.setup_function = mock_func
    mock_setup.runtime = {}

    result = generator(mock_setup)

    assert "setup_all('lambda')" in result.build
    assert "# TODO: change this" in result.build
    assert result.importing == {"conf": ["setup_all"]}


def test_runtime_fallback_used(generator):
    runtime_func = Mock()
    runtime_func.module = "alt_init"
    runtime_func.function_name = "lambda_setup"

    mock_setup = Mock()
    mock_setup.setup_function = None
    mock_setup.runtime = {
        RuntimeType.LAMBDA.value: runtime_func
    }

    result = generator(mock_setup)

    assert isinstance(result, AWSHandlerGenResponse)
    assert result.build == "alt_init()"
    assert result.importing == {"alt_init": ["lambda_setup"]}


def test_no_setup_function_and_no_runtime_returns_none(generator):
    mock_setup = Mock()
    mock_setup.setup_function = None
    mock_setup.runtime = {}

    result = generator(mock_setup)
    assert result is None


def test_invalid_param_count_raises(generator):
    mock_func = Mock()
    mock_func.module = "x"
    mock_func.function_name = "bad_func"
    mock_func.n_params = -1

    mock_setup = Mock()
    mock_setup.setup_function = mock_func
    mock_setup.runtime = {}

    with pytest.raises(RuntimeError, match="Invalid number of parameters"):
        generator(mock_setup)
