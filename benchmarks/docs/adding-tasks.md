# Adding a New Benchmark Task

Benchmark tasks are self-contained Python exercises with a buggy or incomplete
implementation and a matching test suite. The benchmark runner evaluates
*targets* (models, agents, or flows) by replacing the buggy file with the
target's output and running the tests.

## Directory layout

Create a new task directory under the appropriate category:

```
benchmarks/categories/<category>/<task-id>/
├── prompt.md            # Bilingual task description
├── rubric.json          # Evaluation criteria
├── fixtures/
│   ├── src/
│   │   └── <module>.py  # Buggy or incomplete code
│   └── tests/
│       └── test_<module>.py
└── expected/
    ├── src/
    │   └── <module>.py  # Reference solution
    └── tests/
        └── test_<module>.py
```

## Rules

1. **Task ID**: kebab-case, unique across all categories. Use the format
   `NNN-short-description` (e.g. `001-race-condition-counter`).
2. **Difficulty**: pick one of `easy`, `medium`, `hard`. Each active category
   should have one task of each difficulty.
3. **Bilingual prompt**: `prompt.md` must contain an English section followed
   by a Spanish section separated by `---`:

   ```markdown
   # English

   You are in the workspace directory `<category>/<task-id>/`. It contains:
   - `src/<module>.py` — the module to fix
   - `tests/test_<module>.py` — tests that currently fail

   <Description of the bug and expected fix.>

   Your response must be the COMPLETE fixed content of `src/<module>.py`.
   Do not include explanations, markdown code fences, or any other text.
   Only the file content.

   ---

   # Español

   <Spanish translation>
   ```

4. **Self-contained**: no network access, no external files, no time-dependent
   behavior, no third-party dependencies beyond the Python standard library.
5. **Test imports**: tests must import the module directly, e.g.
   `from <module> import ...` or `import <module>`. The runner sets
   `PYTHONPATH` to the workspace `src/` directory.
6. **Reference solution**: applying `expected/src/<module>.py` to a fresh copy of
   `fixtures/` must make every test pass.

## `rubric.json` format

```json
{
  "target_file": "src/<module>.py",
  "criteria": [
    {
      "id": "uses-fix-technique",
      "type": "pattern",
      "check": "output_contains",
      "pattern": "<regex>",
      "weight": 30
    },
    {
      "id": "tests-pass",
      "type": "test",
      "check": "tests/test_<module>.py",
      "weight": 70
    }
  ]
}
```

* Weights must sum to `100`.
* `pattern` is a Python regex matched against the target's output. Backslashes
  must be escaped for JSON: use `\\.` to match a literal dot.
* `check` for a test criterion is a pytest node id or file path.

## Manifest entry

Add the task to `benchmarks/manifest.json` under the right category:

```json
{
  "id": "001-my-new-task",
  "name": "My new task",
  "difficulty": "easy",
  "timeout": 300,
  "status": "active"
}
```

You can also override scoring weights per task:

```json
{
  "id": "001-my-new-task",
  "difficulty": "easy",
  "timeout": 300,
  "status": "active",
  "weights": { "tests": 0.6, "diff": 0.2, "rubric": 0.2 }
}
```

## Verification

Before committing a task, run:

```bash
python -m pytest benchmarks/categories/<category>/<task-id>/expected/tests -v
```

with `PYTHONPATH` set to `benchmarks/categories/<category>/<task-id>/expected/src`.

Then run the benchmark with the mock target to confirm scoring works:

```bash
python benchmarks/run.py --targets mock-reference --categories <category>
```

## Deferred categories

Categories like `architecture` and `trade-off-evaluation` are marked
`"status": "deferred"` and `"eval_mode": "llm-judge"`. Do not add task
fixtures for deferred categories; they will be activated in Phase 2.
