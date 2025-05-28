import pytest
from unittest.mock import MagicMock
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema import TriggerConsumer

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.\
    trigger_generator.consumer_aws_sns_handler_generator import ConsumerAWSSNSHandlerGenerator


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def simple_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.keyname = "my_event"
    trigger.options = TriggerConsumer(queue="arn:aws:sns:queue1", mapper=None)
    return trigger


@pytest.fixture
def trigger_with_mapper():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.keyname = "mapped_event"
    trigger.options = TriggerConsumer(
        queue="arn:aws:sns:queue2",
        mapper={"detail.data": "mapped_data"}
    )
    return trigger


def test_returns_none_for_non_consumer_triggers(uc_var_name):
    fake_trigger = MagicMock(spec=TriggerInfo)
    fake_trigger.type = TriggerEnum.HTTP
    fake_trigger.options = MagicMock()

    gen = ConsumerAWSSNSHandlerGenerator()
    result = gen([fake_trigger], uc_var_name)

    assert result is None


def test_generates_handler_for_single_trigger(simple_trigger, uc_var_name):
    gen = ConsumerAWSSNSHandlerGenerator()
    response = gen([simple_trigger], uc_var_name)

    assert response is not None
    assert "mapper_consumer_sns" in response.build
    assert f"# queue_arn = record.get(\"EventSubscriptionArn\", \"\")" in response.body
    assert f"# if \"{simple_trigger.options.queue}\" in queue_arn:" in response.body
    assert "uc_response = my_use_case(**request_to_uc)" in response.body
    assert "response.append(uc_response)" in response.body
    assert "return {\"statusCode\": 200, \"body\": response}" in response.body


def test_generates_handler_for_multiple_triggers(simple_trigger, trigger_with_mapper, uc_var_name):
    gen = ConsumerAWSSNSHandlerGenerator()
    response = gen([simple_trigger, trigger_with_mapper], uc_var_name)

    assert response is not None
    assert "for record in event[\"Records\"]" in response.body
    assert "mapper_consumer_sns" in response.build
    assert "mapper_consumer_sns_1_mapped_event" in response.build
    assert f"if \"{simple_trigger.options.queue}\" in queue_arn:" in response.body
    assert f"if \"{trigger_with_mapper.options.queue}\" in queue_arn:" in response.body
    assert "request_to_uc : dict = mapper_consumer_sns_1_mapped_event.map" in response.body
