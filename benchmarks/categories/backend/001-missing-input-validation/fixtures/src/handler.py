def handle_registration(data):
    return {
        "status": "ok",
        "user": {
            "name": data["name"],
            "age": data["age"],
            "email": data["email"],
        },
    }
