from serializer import serialize_user


FULL_USER = {
    "username": "alice",
    "email": "alice@example.com",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z",
    "is_active": True,
    "password_hash": "abc123hash",
    "ssn": "123-45-6789",
    "internal_id": "emp-007",
}


def test_excludes_sensitive_fields():
    result = serialize_user(FULL_USER)
    assert "password_hash" not in result
    assert "ssn" not in result
    assert "internal_id" not in result


def test_includes_public_fields():
    result = serialize_user(FULL_USER)
    assert result["username"] == "alice"
    assert result["email"] == "alice@example.com"
    assert result["role"] == "admin"
    assert result["created_at"] == "2024-01-01T00:00:00Z"
    assert result["is_active"] is True


def test_only_public_fields_present():
    result = serialize_user(FULL_USER)
    assert set(result.keys()) == {"username", "email", "role", "created_at", "is_active"}


def test_missing_public_fields_are_omitted():
    user = {"username": "bob", "email": "bob@example.com", "password_hash": "secret"}
    result = serialize_user(user)
    assert "password_hash" not in result
    assert "username" in result
    assert "email" in result
    assert "role" not in result
    assert "created_at" not in result
    assert "is_active" not in result
