PUBLIC_FIELDS = {"username", "email", "role", "created_at", "is_active"}


def serialize_user(user):
    """Return a public representation of a user for an API response."""
    return {field: user[field] for field in PUBLIC_FIELDS if field in user}
