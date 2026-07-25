# Race Condition Counter

# English

You are in the workspace directory `bug-hunt/001-race-condition-counter/`. It contains:
- `src/counter.py` — the module to fix
- `tests/test_counter.py` — tests that currently fail

The `Counter` class increments a shared `value` field from many threads without any synchronization. The `increment` method reads `self.value`, computes the next integer, and writes it back in separate steps, so concurrent updates are lost.

Fix `src/counter.py` so that the shared counter is protected by `threading.Lock`. The test runs 100 threads, each incrementing the counter 1000 times, and expects the final value to be exactly 100000.

Your response must be the COMPLETE fixed content of `src/counter.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `bug-hunt/001-race-condition-counter/`. Contiene:
- `src/counter.py` — el módulo a corregir
- `tests/test_counter.py` — pruebas que actualmente fallan

La clase `Counter` incrementa un campo compartido `value` desde muchos hilos sin ninguna sincronización. El método `increment` lee `self.value`, calcula el siguiente entero y lo escribe de nuevo en pasos separados, por lo que las actualizaciones concurrentes se pierden.

Corrige `src/counter.py` para que el contador compartido esté protegido por `threading.Lock`. La prueba ejecuta 100 hilos, cada uno incrementando el contador 1000 veces, y espera que el valor final sea exactamente 100000.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/counter.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
