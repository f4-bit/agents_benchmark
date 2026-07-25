# Off-by-One Loop

# English

You are in the workspace directory `bug-hunt/002-off-by-one-loop/`. It contains:
- `src/processor.py` — the module to fix
- `tests/test_processor.py` — tests that currently fail

The function `prefix_items(items, prefix)` builds a result list by iterating with `range(len(items) - 1)`. Because the loop stops one index too early, the last element of `items` is omitted from the returned list.

Fix `src/processor.py` so the loop covers every element of `items`. The tests check that the function returns all expected prefixed values, including the last one.

Your response must be the COMPLETE fixed content of `src/processor.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `bug-hunt/002-off-by-one-loop/`. Contiene:
- `src/processor.py` — el módulo a corregir
- `tests/test_processor.py` — pruebas que actualmente fallan

La función `prefix_items(items, prefix)` construye una lista de resultados iterando con `range(len(items) - 1)`. Como el bucle se detiene un índice antes, el último elemento de `items` se omite en la lista devuelta.

Corrige `src/processor.py` para que el bucle recorra todos los elementos de `items`. Las pruebas verifican que la función devuelva todos los valores con prefijo esperados, incluido el último.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/processor.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
