# Benchmarks

Deterministic benchmark suite for evaluating AI coding *systems* (models +
tools + workflows + agent delegation), not just models in isolation.

## Goals

* **Deterministic**: no LLM-as-judge, no external services, reproducible scores.
* **Tool-aware**: compare raw models, opencode flows, and custom pipelines via a
  uniform CLI contract.
* **Bilingual**: every task prompt is provided in English and Spanish.
* **Extensible**: add new tasks, targets, and adapter types as the project grows.

## Current scope (Phase 1)

* 5 active categories, 3 tasks each:
  * `bug-hunt`
  * `backend`
  * `concurrent-code`
  * `security-app`
  * `cybersecurity`
* 2 deferred categories (Phase 2):
  * `architecture` (requires LLM-as-judge)
  * `trade-off-evaluation` (requires LLM-as-judge)
* 3 scoring layers:
  1. Automated pytest execution
  2. AST structural diff against reference solution
  3. Pattern-based rubric checking

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   targets    │────▶│   runner     │────▶│   results    │
│   .yaml      │     │   run.py     │     │   summary    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ target  │       │  eval   │       │ report  │
   │adapter  │       │ engine  │       │ writer  │
   └─────────┘       └─────────┘       └─────────┘
        │
        ▼
   ┌─────────────┐
   │  opencode   │
   │  wrapper    │  (--no-interactive support)
   └─────────────┘
```

## Quick start

Install the development dependencies:

```bash
pip install -e .[dev]
```

Run unit tests for the benchmark infrastructure:

```bash
python -m pytest benchmarks/tests -v
```

Run the mock target (reference solution) against all tasks:

```bash
python benchmarks/run.py --targets mock-reference --categories all
```

Inspect the report:

```bash
cat benchmarks/results/<run-id>/report.md
```

## Documentation

* [Adding a new task](docs/adding-tasks.md)
* [Adding a new target](docs/adding-targets.md)
* [Running benchmarks](docs/running-benchmarks.md)

## Project structure

```
benchmarks/
├── categories/          # 15 benchmark tasks (fixtures + expected + prompts)
├── docs/                # how-to guides
├── eval/                # deterministic eval engine
│   ├── target_adapter.py
│   ├── target_registry.py
│   ├── test_runner.py
│   ├── diff_engine.py
│   ├── rubric_checker.py
│   └── scorer.py
├── tests/               # unit tests for the benchmark framework
├── results/             # generated run output
├── run.py               # main benchmark runner
├── targets.yaml         # target registry
├── manifest.json        # task catalog and weights
└── opencode_cli_wrapper.py  # --no-interactive wrapper for opencode
```

## Notes

* The distributed `opencode` binary is a compiled executable, so the
  `--no-interactive` flag is implemented through a Python wrapper that
  enforces non-interactive behavior (closed stdin, prompt detection) and then
  delegates to the real binary.
* The runner's eval pipeline requires `pytest` and `pytest-timeout` as runtime
  dependencies (not just development dependencies) because the runner shells out
  to `python -m pytest` for every task. `PyYAML` is also required for parsing
  `targets.yaml` and the manifest.
