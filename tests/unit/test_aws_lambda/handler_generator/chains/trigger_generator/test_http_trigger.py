import pytest
from unittest.mock import MagicMock
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_http import TriggerHttp
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.trigger_generator.http_aws_handler_generator import (
    HttpAWSHandlerGenerator
)


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def simple_http_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.HTTP
    trigger.keyname = "get_user"
    trigger.options = TriggerHttp(path="/users/<user_id>", method="GET", mapper=None)
    return trigger


@pytest.fixture
def trigger_with_mapper():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.HTTP
    trigger.keyname = "update_user"
    trigger.options = TriggerHttp(
        path="/users/<user_id>", method="POST",
        mapper={"body.name": "name", "path_query.user_id": "user_id"}
    )
    return trigger


def test_returns_none_for_non_http_triggers(uc_var_name):
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.CONSUMER
    trigger.options = MagicMock()
    generator = HttpAWSHandlerGenerator()
    assert generator([trigger], uc_var_name) is None


def test_generates_handler_for_single_trigger(simple_http_trigger, uc_var_name):
    generator = HttpAWSHandlerGenerator()
    result = generator([simple_http_trigger], uc_var_name)

    assert result is not None
    assert "if \"httpMethod\" in event" in result.body
    assert "# if event.get(\"resource\", \"\").endswith(\"/users/{user_id}\")" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body
    assert "return {\"statusCode\": 200, \"body\": uc_response}" in result.body


def test_generates_handler_with_mapper(trigger_with_mapper, uc_var_name):
    generator = HttpAWSHandlerGenerator()
    result = generator([trigger_with_mapper], uc_var_name)

    assert "mapper_http" in result.build
    assert "mapper_http_0_update_user" in result.build
    assert "request_to_uc : dict = mapper_http_0_update_user.map" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body

def test_generates_handler_for_multiple_http_triggers(simple_http_trigger, trigger_with_mapper, uc_var_name):
    generator = HttpAWSHandlerGenerator()
    result = generator([simple_http_trigger, trigger_with_mapper], uc_var_name)

    assert result is not None
    body = result.body
    build = result.build

    assert 'if event.get("resource", "").endswith("/users/{user_id}") and event.get("httpMethod") == "GET":' in body
    assert 'if event.get("resource", "").endswith("/users/{user_id}") and event.get("httpMethod") == "POST":' in body

    assert "mapper_http" in build

    assert "mapper_http_1_update_user" in build
    assert "request_to_uc : dict = mapper_http_1_update_user.map" in body

    assert "uc_response = my_use_case(**request_to_uc)" in body
    assert 'return {"statusCode": 200, "body": uc_response}' in body
