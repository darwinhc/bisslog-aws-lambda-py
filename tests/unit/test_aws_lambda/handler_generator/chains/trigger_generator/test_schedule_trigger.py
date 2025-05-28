import pytest
from unittest.mock import MagicMock
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema import TriggerSchedule

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.trigger_generator.schedule_aws_handler_generator import (
    ScheduleAWSHandlerGenerator
)


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def schedule_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.SCHEDULE
    trigger.keyname = "cron_event"
    trigger.options = TriggerSchedule("0 12 * * ? *")
    return trigger


def test_returns_none_when_no_schedule_triggers(uc_var_name):
    fake_trigger = MagicMock(spec=TriggerInfo)
    fake_trigger.type = TriggerEnum.HTTP
    fake_trigger.options = MagicMock()

    gen = ScheduleAWSHandlerGenerator()
    result = gen([fake_trigger], uc_var_name)
    assert result is None


def test_generates_handler_for_single_schedule(schedule_trigger, uc_var_name):
    gen = ScheduleAWSHandlerGenerator()
    result = gen([schedule_trigger], uc_var_name)

    assert result is not None
    assert "mapper_schedule_event_bridge" in result.build
    assert "request_to_uc = mapper_schedule_event_bridge.map(event)" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body
    assert "response.append(uc_response)" in result.body
    assert 'return {"statusCode": 200, "body": response}' in result.body


def test_generates_handler_for_multiple_schedules(schedule_trigger, uc_var_name):
    gen = ScheduleAWSHandlerGenerator()
    triggers = [schedule_trigger, schedule_trigger]
    result = gen(triggers, uc_var_name)

    assert result is not None
    assert result.body.count("uc_response = my_use_case(**request_to_uc)") == 2
    assert result.body.count("request_to_uc = mapper_schedule_event_bridge.map(event)") == 2
    assert result.body.count("response.append(uc_response)") == 2
