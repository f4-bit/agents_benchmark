# Memory Leak Generator

# English

You are in the workspace directory `bug-hunt/003-memory-leak-generator/`. It contains:
- `src/reader.py` — the module to fix
- `tests/test_reader.py` — tests that currently fail

The generator function `read_records(path)` opens a file with `open(path)` and yields stripped, non-empty lines, but it never closes the file object. This leaves a file descriptor open after the generator is consumed.

Fix `src/reader.py` so that the file is always closed when processing finishes. The recommended approach is to use a `with` statement around the file access. The tests verify that all records are produced and that the file is closed after the generator is consumed.

Your response must be the COMPLETE fixed content of `src/reader.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `bug-hunt/003-memory-leak-generator/`. Contiene:
- `src/reader.py` — el módulo a corregir
- `tests/test_reader.py` — pruebas que actualmente fallan

La función generadora `read_records(path)` abre un archivo con `open(path)` y produce líneas no vacías recortadas, pero nunca cierra el objeto de archivo. Esto deja un descriptor de archivo abierto después de que el generador se consume.

Corrige `src/reader.py` para que el archivo siempre se cierre cuando termine el procesamiento. El enfoque recomendado es usar una sentencia `with` alrededor del acceso al archivo. Las pruebas verifican que se produzcan todos los registros y que el archivo se cierre después de consumir el generador.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/reader.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
