# Missing Input Validation

# English

You are in the workspace directory `backend/001-missing-input-validation/`. It contains:
- `src/handler.py` — the module to fix
- `tests/test_handler.py` — tests that currently fail

The `handle_registration(data)` function accepts a dictionary describing a user registration request, but it currently returns success for any input. It should validate that:

- `name` is a non-empty string after stripping whitespace.
- `age` is a non-negative integer.
- `email` contains an `@` character.

When validation fails, raise `ValueError` with a descriptive message. For valid input, return `{"status": "ok", "user": {...}}` as before.

Your response must be the COMPLETE fixed content of `src/handler.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `backend/001-missing-input-validation/`. Contiene:
- `src/handler.py` — el módulo a corregir
- `tests/test_handler.py` — las pruebas que actualmente fallan

La función `handle_registration(data)` acepta un diccionario que describe una solicitud de registro de usuario, pero actualmente devuelve éxito para cualquier entrada. Debe validar que:

- `name` sea una cadena no vacía después de quitar los espacios en blanco.
- `age` sea un entero no negativo.
- `email` contenga el carácter `@`.

Cuando la validación falle, lanza `ValueError` con un mensaje descriptivo. Para entradas válidas, devuelve `{"status": "ok", "user": {...}}` como antes.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/handler.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
