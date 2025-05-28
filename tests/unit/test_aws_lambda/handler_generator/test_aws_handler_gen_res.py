import re
import pytest
from bisslog_aws_lambda.aws_lambda.handler_generator.aws_handler_gen_response import AWSHandlerGenResponse


def test_create_response_empty():
    response = AWSHandlerGenResponse()
    assert response.body is None
    assert response.build is None
    assert response.importing == {}
    assert response.extra == {}


def test_add_imports_merges_correctly():
    response = AWSHandlerGenResponse()
    response.add_imports({"os": {"path"}, "typing": {"List"}})
    response.add_imports({"os": {"environ"}, "typing": {"Optional"}})

    assert response.importing["os"] == {"path", "environ"}
    assert response.importing["typing"] == {"List", "Optional"}


def test_generate_handler_code_output():
    response = AWSHandlerGenResponse(
        body='return "OK"',
        build='mapper = Mapper("m", {})',
        importing={"typing": {"List", "Optional"}, "os": {"path"}}
    )

    code = response.generate_handler_code()


    assert re.search(r"from typing import .*Optional.*List|.*List.*Optional", code)
    assert "from os import path" in code
    assert "mapper = Mapper" in code
    assert "def lambda_handler(event, context):" in code
    assert "return \"OK\"" in code


def test_addition_operator_merges_fields():
    r1 = AWSHandlerGenResponse(
        body="a = 1",
        build="print('r1')",
        importing={"os": {"path"}}
    )
    r2 = AWSHandlerGenResponse(
        body="b = 2",
        build="print('r2')",
        importing={"os": {"environ"}, "sys": {"exit"}}
    )

    merged = r1 + r2

    assert "a = 1" in merged.body
    assert "b = 2" in merged.body
    assert "print('r1')" in merged.build
    assert "print('r2')" in merged.build
    assert merged.importing["os"] == {"path", "environ"}
    assert merged.importing["sys"] == {"exit"}


def test_iadd_merges_in_place():
    r1 = AWSHandlerGenResponse(
        body="a = 1",
        build="init()",
        importing={"os": {"path"}}
    )
    r2 = AWSHandlerGenResponse(
        body="b = 2",
        build="setup()",
        importing={"os": {"environ"}, "sys": {"exit"}}
    )

    r1 += r2

    assert "a = 1" in r1.body
    assert "b = 2" in r1.body
    assert "init()" in r1.build
    assert "setup()" in r1.build
    assert r1.importing["os"] == {"path", "environ"}
    assert r1.importing["sys"] == {"exit"}


def test_addition_operator_with_invalid_type():
    r = AWSHandlerGenResponse()
    with pytest.raises(NotImplementedError):
        _ = r + "invalid"


def test_iadd_with_none_returns_self():
    r = AWSHandlerGenResponse(body="test")
    result = r.__iadd__(None)
    assert result is r
    assert result.body == "test"
