import pytest
from handler import handle_registration


def test_valid_registration():
    result = handle_registration(
        {"name": "Alice", "age": 30, "email": "alice@example.com"}
    )
    assert result["status"] == "ok"
    assert result["user"]["name"] == "Alice"
    assert result["user"]["age"] == 30
    assert result["user"]["email"] == "alice@example.com"


def test_strips_whitespace_from_name():
    result = handle_registration(
        {"name": "  Bob  ", "age": 25, "email": "bob@example.com"}
    )
    assert result["user"]["name"] == "Bob"


def test_empty_name_raises():
    with pytest.raises(ValueError, match="name"):
        handle_registration({"name": "", "age": 20, "email": "x@y.com"})


def test_negative_age_raises():
    with pytest.raises(ValueError, match="age"):
        handle_registration(
            {"name": "Carlos", "age": -1, "email": "c@example.com"}
        )


def test_email_without_at_raises():
    with pytest.raises(ValueError, match="email"):
        handle_registration(
            {"name": "Dana", "age": 40, "email": "not-an-email"}
        )
