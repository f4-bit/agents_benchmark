# Running Benchmarks

The benchmark runner is `benchmarks/run.py`.

## Quick start

Run the mock target (reference solution) against all active categories:

```bash
python benchmarks/run.py --targets mock-reference --categories all
```

Results are written to `benchmarks/results/<run-id>/`.

## Command-line options

```bash
python benchmarks/run.py --targets <id1,id2|all> --categories <cat1,cat2|all> [--output <dir>]
```

* `--targets`: comma-separated target IDs or `all`.
* `--categories`: comma-separated category names or `all`.
* `--output`: results directory (default: `benchmarks/results/`).
* `--report-only <run-id>`: regenerate `summary.json` and `report.md` from a
  previous run without invoking targets.
* `-v` / `--verbose`: enable debug logging.

## Output files

For each `(target, task)` execution:

```
results/<run-id>/<target-id>/<task-id>/
├── workspace/          # task fixtures + target output
├── stdout.log
├── stderr.log
└── eval.json           # deterministic evaluation result
```

Run-level files:

```
results/<run-id>/
├── results.jsonl       # one JSON object per execution
├── summary.json        # per-target, per-category, global scores
└── report.md           # human-readable score table
```

## Interpreting scores

Each task is scored on a 0–100 scale using three layers, weighted by category:

* **tests** (default 50%): percentage of pytest tests that pass.
* **diff** (default 30%): AST structural similarity against the reference
  solution.
* **rubric** (default 20%): pattern matching and specific test criteria.

If a layer is missing (e.g., no reference solution), its weight is
redistributed proportionally across the remaining layers.

Category scores are averages of task scores. The global score is the average of
active category scores.

## Deferred categories

`architecture` and `trade-off-evaluation` are deferred to Phase 2. They are listed
in `manifest.json` with `"status": "deferred"` and are skipped by the runner.

## Running only verification

To verify the benchmark infrastructure without invoking any model:

```bash
python -m pytest benchmarks/tests -v
```

To verify all 15 reference solutions:

```bash
# For each task, copy expected/src/ to workspace/src/ and run pytest.
python benchmarks/run.py --targets mock-reference --categories all
```

A global score of `100.0` for `mock-reference` confirms the fixtures and test
suite are correct.
