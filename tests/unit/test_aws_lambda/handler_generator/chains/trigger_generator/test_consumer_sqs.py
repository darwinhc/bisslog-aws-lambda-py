import pytest
from unittest.mock import MagicMock

from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema import TriggerConsumer

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.trigger_generator.consumer_aws_sqs_handler_generator import (
    ConsumerAWSSQSHandlerGenerator
)


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def simple_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.keyname = "basic"
    trigger.options = TriggerConsumer(queue="my-sqs-queue", mapper=None)
    return trigger


@pytest.fixture
def trigger_with_mapper():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.keyname = "with_mapper"
    trigger.options = TriggerConsumer(
        queue="special-queue",
        mapper={"body.my_key": "mapped_key"}
    )
    return trigger


def test_returns_none_when_no_consumer_triggers(uc_var_name):
    fake_trigger = MagicMock(spec=TriggerInfo)
    fake_trigger.type = TriggerEnum.HTTP  # Not a consumer
    fake_trigger.options = MagicMock()

    generator = ConsumerAWSSQSHandlerGenerator()
    result = generator([fake_trigger], uc_var_name)

    assert result is None


def test_generates_handler_for_single_trigger(simple_trigger, uc_var_name):
    generator = ConsumerAWSSQSHandlerGenerator()
    result = generator([simple_trigger], uc_var_name)

    assert result is not None
    assert "mapper_consumer_sqs" in result.build
    assert "mapped_standard_event_sqs = mapper_consumer_sqs.map(record)" in result.body
    assert "# queue_arn = record.get(\"eventSourceARN\", \"\")" in result.body
    assert "# if \"my-sqs-queue\" in queue_arn:" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body
    assert "return {\"statusCode\": 200, \"body\": response}" in result.body


def test_generates_handler_for_multiple_triggers(simple_trigger, trigger_with_mapper, uc_var_name):
    generator = ConsumerAWSSQSHandlerGenerator()
    result = generator([simple_trigger, trigger_with_mapper], uc_var_name)

    assert result is not None
    assert "mapper_consumer_sqs" in result.build
    assert "mapper_consumer_sqs_1_with_mapper" in result.build
    assert "queue_arn = record.get(\"eventSourceARN\", \"\")" in result.body
    assert "if \"my-sqs-queue\" in queue_arn:" in result.body
    assert "if \"special-queue\" in queue_arn:" in result.body
    assert "request_to_uc : dict = mapper_consumer_sqs_1_with_mapper.map" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body
