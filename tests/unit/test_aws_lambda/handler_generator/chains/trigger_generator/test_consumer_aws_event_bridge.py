import pytest
from unittest.mock import MagicMock
from bisslog_aws_lambda.aws_lambda.handler_generator.chains.trigger_generator.consumer_aws_event_bridge_handler_generator import (
    ConsumerAWSEventBridgeHandlerGenerator
)
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema import TriggerConsumer


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def simple_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.options = TriggerConsumer(queue="my.service.event", mapper=None)
    return trigger


@pytest.fixture
def trigger_with_mapper():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.keyname = "mapped_event"
    trigger.options = TriggerConsumer(
        queue="other.source",
        mapper={"detail.subkey": "mapped_key"}
    )
    return trigger


def test_returns_none_for_non_consumer_triggers(uc_var_name):
    fake_trigger = MagicMock(spec=TriggerInfo)
    fake_trigger.type = TriggerEnum.HTTP  # not a consumer
    fake_trigger.options = MagicMock()

    gen = ConsumerAWSEventBridgeHandlerGenerator()
    result = gen([fake_trigger], uc_var_name)

    assert result is None


def test_generates_code_for_single_consumer_trigger(simple_trigger, uc_var_name):
    gen = ConsumerAWSEventBridgeHandlerGenerator()
    response = gen([simple_trigger], uc_var_name)

    assert isinstance(response.body, str)
    assert isinstance(response.build, str)
    assert response.importing == {}
    assert "mapper_consumer_event_bridge" in response.build
    assert f"# if \"{simple_trigger.options.queue}\" in event.get(\"source\", \"\")" in response.body
    assert f"uc_response = {uc_var_name}(**request_to_uc)" in response.body


def test_generates_code_for_multiple_triggers(simple_trigger, trigger_with_mapper, uc_var_name):
    gen = ConsumerAWSEventBridgeHandlerGenerator()
    response = gen([simple_trigger, trigger_with_mapper], uc_var_name)

    assert "mapper_consumer_event_bridge" in response.build
    assert "mapper_consumer_event_bridge_1_mapped_event" in response.build
    assert "if \"my.service.event\" in event.get(\"source\", \"\"):" in response.body
    assert "if \"other.source\" in event.get(\"source\", \"\"):" in response.body
    assert "request_to_uc : dict = mapper_consumer_event_bridge_1_mapped_event.map" in response.body
    assert "response.append(uc_response)" in response.body
    assert "return {\"statusCode\": 200, \"body\": response}" in response.body
