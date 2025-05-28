import pytest
from bisslog_aws_lambda.aws_lambda.handler_generator.aws_handler_generator import AWSHandlerGenerator


class DummyGenerator(AWSHandlerGenerator):
    def __call__(self, *args, **kwargs):
        return "called"


def test_join_with_depth_returns_properly_indented_code():
    gen = DummyGenerator()
    lines = [
        ("def handler():", 0),
        ("if True:", 1),
        ("return 'ok'", 2)
    ]
    result = gen.join_with_depth(lines)

    expected = (
        "def handler():\n"
        "    if True:\n"
        "        return 'ok'"
    )

    assert result == expected


def test_call_not_implemented():
    class IncompleteGen(AWSHandlerGenerator):
        pass

    with pytest.raises(TypeError):
        IncompleteGen()  # can't instantiate abstract class


def test_call_must_be_overridden():
    class Dummy(AWSHandlerGenerator):
        def __call__(self, *args, **kwargs):
            return "ok"

    d = Dummy()
    assert d() == "ok"
