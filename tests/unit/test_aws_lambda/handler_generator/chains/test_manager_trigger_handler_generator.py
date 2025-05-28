import pytest
from unittest.mock import MagicMock
from bisslog_aws_lambda.aws_lambda.handler_generator.chains.manager_trigger_handler_generator import (
    ManagerTriggerHandlerGenerator
)
from bisslog_aws_lambda.aws_lambda.handler_generator.aws_handler_gen_response import AWSHandlerGenResponse
from bisslog_schema.schema import TriggerInfo


@pytest.fixture
def mock_generator():
    mock = MagicMock()
    mock.return_value = AWSHandlerGenResponse(
        body="code_line",
        build="build_line",
        importing={"mod": {"imp"}},
        extra={"key": "value"}
    )
    return mock


def test_manager_triggers_merge_all(mock_generator):
    triggers = [MagicMock(spec=TriggerInfo)]
    manager = ManagerTriggerHandlerGenerator(trigger_generator=[mock_generator, mock_generator])

    result = manager(triggers, "UC")

    assert isinstance(result, AWSHandlerGenResponse)
    assert "code_line" in result.body
    assert "build_line" in result.build
    assert "mod" in result.importing
    assert result.importing["mod"] == {"imp"}


def test_manager_uses_custom_order(mock_generator):
    # Add generators with different side effects
    generator_a = MagicMock(return_value=AWSHandlerGenResponse(body="A"))
    generator_b = MagicMock(return_value=AWSHandlerGenResponse(body="B"))

    manager = ManagerTriggerHandlerGenerator(trigger_generator=[generator_a, generator_b])
    result = manager([MagicMock()], "uc_var")

    assert result.body == "A\nB"
    generator_a.assert_called_once()
    generator_b.assert_called_once()
