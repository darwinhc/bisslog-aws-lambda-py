import pytest
from bisslog_aws_lambda.aws_lambda.handler_generator.chains.build_use_case_object import BuildUseCaseObject
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import (
    UseCaseCodeInfoObject,
    UseCaseCodeInfoClass
)


def test_build_from_object():
    builder = BuildUseCaseObject()
    obj_info = UseCaseCodeInfoObject(var_name="MY_UC", module="my.module",
                                     docs="This is my use case object.", name="MyUseCase")

    result = builder(obj_info)

    assert result.build == ""
    assert result.importing == {"my.module": ["MY_UC"]}
    assert result.extra["var_name"] == "MY_UC"


def test_build_from_class():
    builder = BuildUseCaseObject()
    cls_info = UseCaseCodeInfoClass(
        name="get_user",
        class_name="GetUser",
        module="app.uc",
        docs="Fetches user data from the database."
    )

    result = builder(cls_info)

    assert "GET_USER = GetUser()" in result.build
    assert result.importing == {"app.uc": ["GetUser"]}
    assert result.extra["var_name"] == "GET_USER"


def test_raises_on_invalid_type():
    builder = BuildUseCaseObject()
    with pytest.raises(RuntimeError) as e:
        builder("invalid")
    assert "Unknown use case code type" in str(e.value)
