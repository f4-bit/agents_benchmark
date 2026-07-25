def handle_registration(data):
    name = data.get("name", "")
    age = data.get("age")
    email = data.get("email", "")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(age, int) or age < 0:
        raise ValueError("age must be a non-negative integer")
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("email must contain '@'")

    return {
        "status": "ok",
        "user": {
            "name": name.strip(),
            "age": age,
            "email": email,
        },
    }
