# N+1 Query Problem

# English

You are in the workspace directory `backend/003-n-plus-one-query/`. It contains:
- `src/repository.py` — the module to fix
- `tests/test_repository.py` — tests that currently fail

`OrderRepository.get_users_with_orders(user_ids)` currently loops over `user_ids` and executes one database query per user. Refactor the method so that all orders for the given `user_ids` are fetched in a single query, then grouped by `user_id` in Python.

The method must keep the same signature and return format: a dictionary mapping each `user_id` to a list of order dictionaries, where each order dictionary has keys `user_id`, `order_id`, and `total`.

Your response must be the COMPLETE fixed content of `src/repository.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `backend/003-n-plus-one-query/`. Contiene:
- `src/repository.py` — el módulo a corregir
- `tests/test_repository.py` — las pruebas que actualmente fallan

`OrderRepository.get_users_with_orders(user_ids)` actualmente itera sobre `user_ids` y ejecuta una consulta a la base de datos por cada usuario. Refactoriza el método para que todas las órdenes de los `user_ids` dados se obtengan en una sola consulta y luego se agrupen por `user_id` en Python.

El método debe mantener la misma firma y formato de retorno: un diccionario que asigna cada `user_id` a una lista de diccionarios de orden, donde cada diccionario de orden tiene las claves `user_id`, `order_id` y `total`.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/repository.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
