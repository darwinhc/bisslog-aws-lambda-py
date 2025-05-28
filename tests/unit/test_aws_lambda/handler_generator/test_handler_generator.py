import pytest
from unittest.mock import MagicMock

from bisslog_aws_lambda.aws_lambda.handler_generator.handler_generator import HandlerGenerator
from bisslog_aws_lambda.aws_lambda.handler_generator.aws_handler_gen_response import AWSHandlerGenResponse


@pytest.fixture
def mock_use_case_code_info():
    mock_uc = MagicMock()
    mock_uc.name = "get_data"
    return mock_uc


@pytest.fixture
def mock_service_info(mock_use_case_code_info):
    trigger_mock = MagicMock()
    use_case_metadata = MagicMock()
    use_case_metadata.triggers = [trigger_mock]

    service_info = MagicMock()
    service_info.use_cases = {mock_use_case_code_info.name: use_case_metadata}
    return service_info


@pytest.fixture
def mock_build_use_case_gen():
    mock = MagicMock()
    response = AWSHandlerGenResponse(
        build="uc = UseCase()",
        importing={"my.module": {"UseCase"}},
        extra={"var_name": "uc"}
    )
    mock.return_value = response
    return mock


@pytest.fixture
def mock_trigger_handler_gen():
    mock = MagicMock()
    response = AWSHandlerGenResponse(
        body="if event.get('key'): uc.execute()",
        importing={"my.mapper": {"Mapper"}}
    )
    mock.return_value = response
    return mock


@pytest.fixture
def mock_default_handler_gen():
    mock = MagicMock()
    response = AWSHandlerGenResponse(
        body="raise Exception('Unhandled')",
        importing={"builtins": {"Exception"}}
    )
    mock.return_value = response
    return mock


def test_handler_generator_successful_call(
    mock_service_info,
    mock_use_case_code_info,
    mock_build_use_case_gen,
    mock_trigger_handler_gen,
    mock_default_handler_gen
):
    generator = HandlerGenerator(
        manager_trigger_gen=mock_trigger_handler_gen,
        build_use_case_obj_gen=mock_build_use_case_gen,
        default_handler_gen=mock_default_handler_gen
    )

    code = generator(mock_service_info, mock_use_case_code_info)

    assert "def lambda_handler(event, context):" in code
    assert "uc = UseCase()" in code
    assert "uc.execute()" in code
    assert "raise Exception" in code
    assert "from my.module import UseCase" in code
    assert "from my.mapper import Mapper" in code


def test_raises_runtime_error_if_inputs_are_none(mock_build_use_case_gen):
    generator = HandlerGenerator(
        manager_trigger_gen=MagicMock(),
        build_use_case_obj_gen=mock_build_use_case_gen,
        default_handler_gen=MagicMock()
    )

    with pytest.raises(RuntimeError):
        generator(None, None)


def test_raises_value_error_if_varname_missing(
    mock_service_info,
    mock_use_case_code_info,
    mock_trigger_handler_gen,
    mock_default_handler_gen
):
    bad_build_gen = MagicMock()
    bad_response = AWSHandlerGenResponse(extra={})  # no var_name
    bad_build_gen.return_value = bad_response

    generator = HandlerGenerator(
        manager_trigger_gen=mock_trigger_handler_gen,
        build_use_case_obj_gen=bad_build_gen,
        default_handler_gen=mock_default_handler_gen
    )

    with pytest.raises(ValueError):
        generator(mock_service_info, mock_use_case_code_info)
