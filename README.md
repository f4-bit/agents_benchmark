# Agents Benchmark

Benchmark suite determinística para evaluar sistemas de IA de codificación (modelo + herramientas + flujos + agentes), no solo modelos de forma aislada.

## Why this project

- Evaluar solo el modelo es engañoso: un modelo brillante con malas herramientas rinde peor que un modelo medio con un flujo excelente.
- Necesitamos reproducibilidad sin depender de LLM-as-judge ni servicios externos.
- Comparar "modelo crudo" vs "sistema completo" (con skills, MCPs, subagentes) para medir el impacto real de las herramientas.

## Benchmark categories

| Category | Focus | Tasks | Status |
|---|---|---|---|
| bug-hunt | Race conditions, off-by-one, memory leaks | 3 | Active |
| backend | Input validation, pagination, N+1 queries | 3 | Active |
| concurrent-code | Deadlocks, atomicity, producer-consumer | 3 | Active |
| security-app | SQL injection, path traversal, password hashing | 3 | Active |
| cybersecurity | Insecure config, SSRF, data exposure | 3 | Active |
| architecture | System design and architecture | — | Phase 2 |
| trade-off-evaluation | Engineering trade-off analysis | — | Phase 2 |

## How it works

El runner ejecuta un *target* (modelo, agente, flujo) contra cada tarea. La respuesta del target se aplica al workspace y se evalúa con tres capas determinísticas:

1. **Test execution**: pytest contra la solución del target.
2. **AST diff**: similitud estructural contra la solución de referencia.
3. **Rubric patterns**: verificación de patrones específicos (regex) y tests concretos.

Sin LLM-as-judge, sin servicios externos, 100% reproducible.

## Quick start

```bash
pip install -e .[dev]
python -m pytest benchmarks/tests -v
python benchmarks/run.py --targets mock-reference --categories all
```

## Project structure

```
benchmarks/
  categories/   15 tareas con fixtures, soluciones de referencia y prompts
  eval/         Motor de evaluación determinístico
  run.py        Orquestador principal
  targets.yaml  Registro de targets
  manifest.json Catálogo de tareas
  tests/        Tests unitarios del framework
  docs/         Guías de uso y extensión
  results/      Output de ejecuciones
openspec/       Especificación del cambio (OpenSpec)
pyproject.toml  Configuración del proyecto Python
```

## Documentation

- [Full benchmark guide](benchmarks/README.md)
- [Adding tasks](benchmarks/docs/adding-tasks.md)
- [Adding targets](benchmarks/docs/adding-targets.md)
- [Running benchmarks](benchmarks/docs/running-benchmarks.md)

## License

MIT
