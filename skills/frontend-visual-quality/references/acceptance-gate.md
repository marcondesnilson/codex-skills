# Acceptance plan and evidence gate

The task plan is declared before execution. It names affected components and required checks. `frontend_impact` and
`api_execution_authorized` are separate facts: a visual impact always adds the required external visual-review check,
while API execution still needs explicit task-scoped authorization and a separate `--authorize-api-execution` flag.
An API key or authorization file alone does not grant permission to make a request.

Create a plan matching [acceptance-plan.schema.json](../schemas/acceptance-plan.schema.json), then initialize a private
task folder:

```sh
python3 scripts/visual_review.py init \
  --task-id <task-id> --project <project> --scope <routes-and-components> \
  --acceptance-plan /private/plan.json --project-root /workspace/project
```

When separate API execution permission has been granted for this task, add both `--authorization-file` and
`--authorize-api-execution`. The plan's frontend decision still requires visual acceptance if true. A frontend task
without API execution authorization remains `BLOCKED` at finalization unless a confirmed failure already makes the
result `FAIL`.

## Served build identity

Record a hash-backed build context with `record-build`. It contains a served version, build ID, source hash, runtime
configuration hash, accepted visual-direction hash, and served asset hash. Each current screenshot records the returned
`build_fingerprint` plus platform, environment, device/window, viewport, scale factor, theme, state, route, tool, and
content ID. A change to the served fingerprint makes prior checks and screenshots stale; record the checks again against
the current build. Git `HEAD` alone does not identify the served app.

## Evidence-linked checks

Declare check IDs before running checks. Store a sanitized, non-empty `.md`, `.txt`, or `.json` evidence file in the
private task folder, then register its SHA-256 and byte count with `record-check`. The helper rejects unknown check IDs,
missing evidence, symlinks, external files, and a warning downgrade of a required check. Evidence is checked again at
finalization; editing it after registration makes it stale.

```sh
python3 scripts/visual_review.py record-check --task-dir <task-dir> \
  --check-id unit-tests --status PASS \
  --evidence <task-dir>/evidence/unit-tests.txt --summary "42 offline tests passed"
python3 scripts/visual_review.py finalize --task-dir <task-dir>
```

The finalizer derives the same conclusion into state, manifest, and report. It does not accept a caller-supplied result.
Precedence is `FAIL` > `BLOCKED` > `PASS WITH WARNINGS` > `PASS`. A missing required test is `BLOCKED`, not a warning.
Only recorded checks and evidence for the same current build count. A consultive model response is not itself an approval;
Codex records the evaluation as an evidence-linked external visual check.

Backend-only plans do not need visual configuration or API authorization. Reading or changing the QA skill does not
create a task, start a product test, or count as product QA.
