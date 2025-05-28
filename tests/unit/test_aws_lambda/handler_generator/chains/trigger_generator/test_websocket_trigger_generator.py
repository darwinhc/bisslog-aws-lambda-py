import pytest
from unittest.mock import MagicMock

from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema import TriggerWebsocket

from bisslog_aws_lambda.aws_lambda.handler_generator.chains.trigger_generator.websocket_aws_handler_generator import (
    WebSocketAWSHandlerGenerator
)


@pytest.fixture
def uc_var_name():
    return "my_use_case"


@pytest.fixture
def websocket_trigger():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.WEBSOCKET
    trigger.keyname = "ping_keyname"
    trigger.options = TriggerWebsocket(route_key="ping", mapper=None)
    return trigger


@pytest.fixture
def websocket_trigger_with_mapper():
    trigger = MagicMock(spec=TriggerInfo)
    trigger.type = TriggerEnum.WEBSOCKET
    trigger.keyname = "sendMessage"
    trigger.options = TriggerWebsocket(
        route_key="sendMessage",
        mapper={"body.text": "message", "connection_id": "conn_id"}
    )
    return trigger


def test_returns_none_when_no_websocket_triggers(uc_var_name):
    bad_trigger = MagicMock(spec=TriggerInfo)
    bad_trigger.type = TriggerEnum.HTTP
    bad_trigger.options = MagicMock()

    gen = WebSocketAWSHandlerGenerator()
    result = gen([bad_trigger], uc_var_name)

    assert result is None


def test_generates_handler_for_single_trigger(websocket_trigger, uc_var_name):
    gen = WebSocketAWSHandlerGenerator()
    result = gen([websocket_trigger], uc_var_name)

    assert result is not None
    assert "mapper_ws" in result.build
    assert "# if \"ping\" in event[\"requestContext\"][\"routeKey\"]:" in result.body
    assert "uc_response = my_use_case(**request_to_uc)" in result.body
    assert "return {\"statusCode\": 200, \"body\": uc_response}" in result.body


def test_generates_handler_for_multiple_triggers(websocket_trigger, websocket_trigger_with_mapper, uc_var_name):
    gen = WebSocketAWSHandlerGenerator()
    result = gen([websocket_trigger, websocket_trigger_with_mapper], uc_var_name)

    assert result is not None
    assert "mapper_ws" in result.build
    assert "mapper_websocket_1_sendMessage" in result.build
    assert "if \"ping\" in event[\"requestContext\"][\"routeKey\"]:" in result.body
    assert "if \"sendMessage\" in event[\"requestContext\"][\"routeKey\"]:" in result.body
    assert "request_to_uc : dict = mapper_websocket_1_sendMessage.map" in result.body
    assert "return {\"statusCode\": 200, \"body\": uc_response}" in result.body
