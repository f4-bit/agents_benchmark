# Producer-consumer deadlock

# English

You are in the workspace directory `concurrent-code/003-producer-consumer-deadlock/`. It contains:
- `src/producer_consumer.py` — the module to fix
- `tests/test_producer_consumer.py` — tests that currently fail

The module implements a bounded buffer shared between one producer thread and one consumer thread. The `Buffer` class uses `threading.Condition` objects, but the `put` and `get` methods notify the wrong condition: the producer notifies `not_full` after adding an item, and the consumer notifies `not_empty` after removing an item. Because the consumer is waiting on `not_empty` and the producer is waiting on `not_full`, neither ever receives a wakeup, and the threads deadlock.

Fix the condition-variable usage so that all items are produced and consumed without deadlock. The recommended fix is to use a single `threading.Condition` and always perform both `wait` and `notify` inside the corresponding `with cond:` block. Keep the public functions `run_producer_consumer` and `Buffer` (or equivalent) and their signatures unchanged.

Your response must be the COMPLETE fixed content of `src/producer_consumer.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `concurrent-code/003-producer-consumer-deadlock/`. Contiene:
- `src/producer_consumer.py` — el módulo a corregir
- `tests/test_producer_consumer.py` — pruebas que actualmente fallan

El módulo implementa un búfer acotado compartido entre un hilo productor y un hilo consumidor. La clase `Buffer` utiliza objetos `threading.Condition`, pero los métodos `put` y `get` notifican la condición incorrecta: el productor notifica `not_full` después de agregar un elemento, y el consumidor notifica `not_empty` después de eliminar un elemento. Como el consumidor está esperando en `not_empty` y el productor está esperando en `not_full`, ninguno recibe nunca una señal de despertar, y los hilos entran en deadlock.

Corrige el uso de las variables de condición para que todos los elementos se produzcan y consuman sin deadlock. La corrección recomendada es usar una sola `threading.Condition` y realizar siempre tanto `wait` como `notify` dentro del bloque `with cond:` correspondiente. Mantén las funciones públicas `run_producer_consumer` y `Buffer` (o equivalente) y sus firmas sin cambios.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/producer_consumer.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
