# Adding a New Benchmark Target

A *target* is any system you want to evaluate (raw model, opencode agent flow,
custom pipeline, etc.). Targets are declared in `benchmarks/targets.yaml`.

## CLI adapter (primary)

The benchmark runner invokes CLI targets with a uniform contract:

```
<command> --prompt <file> --workspace <dir> --output <file> --no-interactive
```

The runner appends these four flags to the command list defined in the YAML.
The target must write its response (the complete fixed source file) to the
`--output` file.

### Example: raw model via opencode

```yaml
targets:
  - id: my-model
    type: cli
    command:
      - opencode
      - --model
      - provider/model-name
    timeout: 600
    metadata:
      provider: opencode
      model: provider/model-name
      description: My model target.
```

### Example: opencode with the non-interactive wrapper

Because the distributed `opencode` binary is a compiled executable that does
not yet expose a `--no-interactive` flag, the repo includes a wrapper at
`benchmarks/opencode_cli_wrapper.py`. It provides the same flag and enforces
non-interactive behavior externally:

```yaml
targets:
  - id: my-opencode-agent
    type: cli
    command:
      - python
      - benchmarks/opencode_cli_wrapper.py
      - --model
      - opencode-go/glm-5.2
    timeout: 1200
    metadata:
      provider: opencode
      model: opencode-go/glm-5.2
```

The wrapper also honours the `OPENCODE_NON_INTERACTIVE=1` environment variable.

## Timeout override

The runner uses the task difficulty timeout (`easy=300s`, `medium=1200s`,
`hard=2400s`) by default. A target can override it:

```yaml
targets:
  - id: slow-model
    type: cli
    command:
      - opencode
      - --model
      - slow/model
    timeout: 2400
```

## API / HTTP adapters (Phase 2)

The target registry accepts `type: api` and `type: http` entries, but they are
stubs in Phase 1. Invoking them raises a clear "not implemented" error.

## Validation

Run the unit tests to verify the registry loads your target:

```bash
python -m pytest benchmarks/tests/test_target_adapter.py -v
```

Run a quick benchmark against a single category to confirm the target is
invoked correctly:

```bash
python benchmarks/run.py --targets my-model --categories bug-hunt
```
