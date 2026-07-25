# Incorrect Pagination

# English

You are in the workspace directory `backend/002-incorrect-pagination/`. It contains:
- `src/pagination.py` — the module to fix
- `tests/test_pagination.py` — tests that currently fail

The module provides two functions:

- `paginate(items, page, page_size)` should return the items for the given 1-indexed `page`.
- `total_pages(items, page_size)` should return the total number of pages.

Currently the slice arithmetic is wrong and `total_pages` does not account for leftover items or empty input. Fix the pagination logic and edge cases. Also validate that `page` and `page_size` are positive integers, raising `ValueError` otherwise.

Your response must be the COMPLETE fixed content of `src/pagination.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `backend/002-incorrect-pagination/`. Contiene:
- `src/pagination.py` — el módulo a corregir
- `tests/test_pagination.py` — las pruebas que actualmente fallan

El módulo proporciona dos funciones:

- `paginate(items, page, page_size)` debe devolver los elementos de la página dada (índice 1).
- `total_pages(items, page_size)` debe devolver el número total de páginas.

Actualmente la aritmética del slice es incorrecta y `total_pages` no tiene en cuenta los elementos sobrantes ni las entradas vacías. Corrige la lógica de paginación y los casos límite. También valida que `page` y `page_size` sean enteros positivos, lanzando `ValueError` en caso contrario.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/pagination.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
