import pytest

from bisslog_aws_lambda.utils.to_snake_case import to_snake_case


def test_to_snake_case():
    assert to_snake_case('registerUser') == 'register_user'
    assert to_snake_case('HTTPRequest') == 'http_request'
    assert to_snake_case('UserID') == 'user_id'
    assert to_snake_case('getUserByID') == 'get_user_by_id'
    assert to_snake_case('Already_Snake') == 'already_snake'
    assert to_snake_case('') == ''

def test_error():
    with pytest.raises(ValueError, match="Cannot convert value to snake_case"):
        to_snake_case(None)
    with pytest.raises(ValueError, match="Cannot convert value to snake_case"):
        to_snake_case([])


def test_unicode_support():
    """Test Unicode character handling"""
    assert to_snake_case('MéxicoCity') == 'méxico_city'
    assert to_snake_case('日本語Test') == '日本語_test'
