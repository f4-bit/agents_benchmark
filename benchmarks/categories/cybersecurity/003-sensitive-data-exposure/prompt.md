# Sensitive data exposure in API response

# English

You are in the workspace directory `cybersecurity/003-sensitive-data-exposure/`. It contains:
- `src/serializer.py` — the module to fix
- `tests/test_serializer.py` — tests that currently fail

The `serialize_user` function builds a dictionary representation of a user record for an API response. Currently it includes sensitive fields such as `password_hash`, `ssn`, and `internal_id`, which must never be exposed to clients.

Fix `src/serializer.py` so that `serialize_user`:
- Returns only an explicit allowlist of public fields.
- Excludes `password_hash`, `ssn`, and `internal_id`.
- Preserves all public fields that are present in the input (`username`, `email`, `role`, `created_at`, `is_active`).
- Omits public fields that are missing from the input rather than adding them as `None`.

Your response must be the COMPLETE fixed content of `src/serializer.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `cybersecurity/003-sensitive-data-exposure/`. Contiene:
- `src/serializer.py` — el módulo a corregir
- `tests/test_serializer.py` — las pruebas que actualmente fallan

La función `serialize_user` construye una representación en diccionario de un registro de usuario para una respuesta de API. Actualmente incluye campos sensibles como `password_hash`, `ssn` e `internal_id`, que nunca deben exponerse a los clientes.

Corrige `src/serializer.py` para que `serialize_user`:
- Devuelva solo una lista explícita de campos públicos permitidos.
- Excluya `password_hash`, `ssn` e `internal_id`.
- Preserve todos los campos públicos presentes en la entrada (`username`, `email`, `role`, `created_at`, `is_active`).
- Omita los campos públicos que falten en la entrada en lugar de agregarlos como `None`.

Tu respuesta debe ser el contenido completo corregido de `src/serializer.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
