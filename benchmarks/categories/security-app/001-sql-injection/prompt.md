# SQL injection vulnerability

# English

You are in the workspace directory `security-app/001-sql-injection/`. It contains:
- `src/auth.py` — the module to fix
- `tests/test_auth.py` — tests that currently fail

The `authenticate` function in `src/auth.py` builds its SQL query by interpolating user input directly into the string with an f-string. This allows SQL injection that can bypass authentication. Rewrite `authenticate` so that it uses parameterized queries (sqlite3 placeholders `?`) to safely bind the username and password. Do not change the function signature or the database setup.

Your response must be the COMPLETE fixed content of `src/auth.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `security-app/001-sql-injection/`. Contiene:
- `src/auth.py` — el módulo a corregir
- `tests/test_auth.py` — tests que actualmente fallan

La función `authenticate` en `src/auth.py` construye su consulta SQL interpolando directamente la entrada del usuario en la cadena con un f-string. Esto permite una inyección SQL que puede eludir la autenticación. Reescribe `authenticate` para que use consultas parametrizadas (marcadores `?` de sqlite3) y vincule de forma segura el nombre de usuario y la contraseña. No cambies la firma de la función ni la configuración de la base de datos.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/auth.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
