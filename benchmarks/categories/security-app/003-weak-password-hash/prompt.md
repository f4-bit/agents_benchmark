# Weak password hashing

# English

You are in the workspace directory `security-app/003-weak-password-hash/`. It contains:
- `src/passwords.py` — the module to fix
- `tests/test_passwords.py` — tests that currently fail

The `hash_password` function in `src/passwords.py` hashes passwords with MD5, which is fast and unsuitable for password storage. Replace the MD5-based implementation with a slow password hashing algorithm. Use `hashlib.scrypt` from the Python standard library (or bcrypt), and implement `verify_password` so that it correctly verifies a password against a stored hash that includes the salt.

Your response must be the COMPLETE fixed content of `src/passwords.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `security-app/003-weak-password-hash/`. Contiene:
- `src/passwords.py` — el módulo a corregir
- `tests/test_passwords.py` — tests que actualmente fallan

La función `hash_password` en `src/passwords.py` calcula el hash de las contraseñas con MD5, que es rápido e inadecuado para el almacenamiento de contraseñas. Reemplaza la implementación basada en MD5 por un algoritmo de hash de contraseñas lento. Usa `hashlib.scrypt` de la biblioteca estándar de Python (o bcrypt), e implementa `verify_password` para que verifique correctamente una contraseña contra un hash almacenado que incluya la sal.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/passwords.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
