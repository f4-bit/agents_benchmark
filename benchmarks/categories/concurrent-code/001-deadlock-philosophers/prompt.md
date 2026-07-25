# Dining philosophers deadlock

# English

You are in the workspace directory `concurrent-code/001-deadlock-philosophers/`. It contains:
- `src/philosophers.py` — the module to fix
- `tests/test_philosophers.py` — tests that currently fail

The module implements a simulation of the classic dining philosophers problem. Each philosopher is represented by a thread that tries to pick up its left fork and then its right fork before eating once. Because every philosopher acquires forks in the same left-then-right order, the simulation deadlocks when all philosophers pick up their left fork at the same time.

Fix the deadlock so that every philosopher can eat exactly once and all threads terminate. A common correct approach is to enforce a global lock ordering (for example, always acquire the lower-numbered fork first). You may also limit the number of philosophers allowed to pick up forks simultaneously, but keep the public API (`run_simulation`) unchanged.

Your response must be the COMPLETE fixed content of `src/philosophers.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `concurrent-code/001-deadlock-philosophers/`. Contiene:
- `src/philosophers.py` — el módulo a corregir
- `tests/test_philosophers.py` — pruebas que actualmente fallan

El módulo implementa una simulación del clásico problema de los filósofos comensales. Cada filósofo está representado por un hilo que intenta tomar su tenedor izquierdo y luego su tenedor derecho antes de comer una vez. Debido a que todos los filósofos adquieren los tenedores en el mismo orden (izquierdo y luego derecho), la simulación entra en deadlock cuando todos toman su tenedor izquierdo al mismo tiempo.

Corrige el deadlock para que cada filósofo pueda comer exactamente una vez y todos los hilos terminen. Un enfoque correcto común es imponer un orden global de bloqueos (por ejemplo, adquirir siempre el tenedor con el número más bajo primero). También puedes limitar la cantidad de filósofos que pueden tomar tenedores simultáneamente, pero mantén la API pública (`run_simulation`) sin cambios.

Tu respuesta debe ser el contenido COMPLETO corregido de `src/philosophers.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
