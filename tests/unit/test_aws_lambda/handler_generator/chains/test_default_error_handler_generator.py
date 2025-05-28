import pytest
from bisslog_aws_lambda.aws_lambda.handler_generator.chains.default_error_handler_generator import DefaultHandlerGenerator


def test_default_handler_generates_runtime_error():
    generator = DefaultHandlerGenerator()
    result = generator()

    assert isinstance(result, object)
    assert isinstance(result.body, str)
    assert "raise RuntimeError(" in result.body
    assert "{str(event)[:500]}" in result.body
    assert "Unrecognized event format" in result.body
    assert result.importing == {}
    assert result.build is None or result.build == ""
