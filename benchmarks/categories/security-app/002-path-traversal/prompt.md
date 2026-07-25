# Path traversal vulnerability

# English

You are in the workspace directory `security-app/002-path-traversal/`. It contains:
- `src/files.py` — the module to fix
- `tests/test_files.py` — tests that currently fail

The `read_file` function in `src/files.py` reads a file using a user-provided filename without validating that the resolved path stays inside the intended base directory. This allows path traversal attacks such as `../../../etc/passwd`. Fix `read_file` so that it resolves the requested path within `base_dir`, rejects any request that escapes the base directory (using `os.path.commonpath`), and still returns the file contents for valid relative filenames.

Your response must be the COMPLETE fixed content of `src/files.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `security-app/002-path-traversal/`. Contiene:
- `src/files.py` — el módulo a corregir
- `tests/test_files.py` — tests que actualmente fallan

La función `read_file` en `src/files.py` lee un archivo usando un nombre de archivo proporcionado por el usuario sin validar que la ruta resuelta permanezca dentro del directorio base previsto. Esto permite ataques de path traversal como `../../../etc/passwd`. Corrige `read_file` para que resuelva la ruta solicitada dentro de `base_dir`, rechace cualquier solicitud que escape del directorio base (usando `os.path.commonpath`) y siga devolviendo el contenido del archivo para nombres de archivo relativos válidos.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/files.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
