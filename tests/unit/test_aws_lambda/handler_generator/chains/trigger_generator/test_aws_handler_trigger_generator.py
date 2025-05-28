import pytest
from bisslog_aws_lambda.aws_lambda.handler_generator.chains.\
    trigger_generator.aws_handler_trigger_generator import AWSHandlerTriggerGenerator


class DummyGenerator(AWSHandlerTriggerGenerator):
    def __call__(self, triggers, uc_var_name):
        return None


def test_generate_mapper_returns_code():
    result = DummyGenerator.generate_mapper("mapper_test", {"event.body": "body"})
    assert result == 'mapper_test = Mapper("mapper_test", {"event.body": "body"})'


def test_generate_mapper_returns_none_on_empty_dict():
    result = DummyGenerator.generate_mapper("mapper_empty", {})
    assert result is None


def test_generate_mapper_with_requires_extracts_top_level_keys():
    line, required = DummyGenerator.generate_mapper_with_requires(
        "mapper_test", {"event.body": "body", "event.query": "query"}
    )
    assert line.startswith("mapper_test = Mapper(")
    assert required == {"event"}


def test_generate_mapper_with_requires_empty_mapper():
    line, required = DummyGenerator.generate_mapper_with_requires("mapper_empty", {})
    assert line is None
    assert required == set()


@pytest.mark.parametrize("trigger_type,keyname,index,expected", [
    ("http", "my_key", 0, "mapper_http_0_my_key"),
    ("consumer", None, 1, "mapper_consumer_1"),
])
def test_generate_mapper_name_variants(trigger_type, keyname, index, expected):
    result = DummyGenerator.generate_mapper_name(trigger_type, keyname, index)
    assert result == expected
