# Non-atomic shared counter

# English

You are in the workspace directory `concurrent-code/002-atomic-counter-bug/`. It contains:
- `src/atomic_counter.py` — the module to fix
- `tests/test_atomic_counter.py` — tests that currently fail

The module contains a `Counter` class that is incremented concurrently from many threads. The current implementation updates the shared `value` field without any synchronization, so increments are lost and the final total is non-deterministic.

Make the counter thread-safe so that `run_threads(100, 1000)` always returns exactly `100000`. Keep the public API (`Counter`, `run_threads`) unchanged. Use a `threading.Lock` to protect the increment.

Your response must be the COMPLETE fixed content of `src/atomic_counter.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `concurrent-code/002-atomic-counter-bug/`. Contiene:
- `src/atomic_counter.py` — el módulo a corregir
- `tests/test_atomic_counter.py` — pruebas que actualmente fallan

El módulo contiene una clase `Counter` que se incrementa concurrentemente desde muchos hilos. La implementación actual actualiza el campo compartido `value` sin ninguna sincronización, por lo que se pierden incrementos y el total final es no determinista.

Haz que el contador sea seguro para hilos para que `run_threads(100, 1000)` siempre devuelva exactamente `100000`. Mantén la API pública (`Counter`, `run_threads`) sin cambios. Usa un `threading.Lock` para proteger el incremento.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/atomic_counter.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
