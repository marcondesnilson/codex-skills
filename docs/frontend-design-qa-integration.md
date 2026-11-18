# Frontend design QA integration

This document connects the existing frontend implementation, visual review, and product-QA skills. It does not start
QA, authorize a paid request, select `current`/`isolated`, or approve a product by itself. Editing or distributing a skill
is not product testing.

## Responsibilities

| Skill | Responsibility in this flow |
| --- | --- |
| `global-doc-agent` | Cross-cutting security, privacy, evidence, quality, and operational boundaries. |
| `frontend-doc-agent` | Implement UI components, states, content contracts, tests, and consumer compatibility in scope. |
| `frontend-visual-quality` | Prepare direction, capture metadata, visual coverage, consultive API operations, and evidence fingerprints. |
| `qa-projects` | Execute real product QA, protect current/isolated data, verify regressions, classify outcomes, and decide evidence-based acceptance. |

No agent runtime or skill-catalog API is assumed. Skill discovery is an environment concern, not a hidden orchestration
step.

## Decision and evidence flow

1. `$qa-projects` preserves its environment prompt: every new run without `--env` asks `current` or `isolated` before
   any test that touches state. Reading these instructions does not request a choice or run checks.
2. Declare the acceptance plan before execution. `frontend_impact` controls whether the required external visual check
   is added; `api_execution_authorized` is recorded separately. API authorization, API key presence, and environment
   selection do not substitute for one another.
3. Record the served version and build ID plus hashes for source, configuration, accepted direction, and assets. A Git
   `HEAD` hash alone is insufficient. Bind each screenshot to that build and record platform, environment, device/window,
   viewport, scale, route, theme, state, tool, content ID, and file hash.
4. Map each criterion to its screen, region, state, platform, required capture IDs, and resulting evidence. A missing
   required capture or `not_evaluable` result leaves the required visual gate blocked.
5. Run existing product checks and record sanitized, non-empty evidence files inside the private task folder. The gate
   verifies their hashes and same-build fingerprints again when finalizing.
6. Compare the full adopted direction and prior findings against current application evidence. Treat suggestions as
   consultive until Codex confirms the finding. A result with no model findings is not an approval.
7. Derive the same result in task state, manifest, and report. Use `FAIL` > `BLOCKED` > `PASS WITH WARNINGS` > `PASS`.
   A missing required test is blocked; a confirmed failure remains fail even when other evidence is blocked.

For frontend impact, external visual review is an acceptance requirement. If API execution or evidence is unavailable,
report `BLOCKED` unless a confirmed `FAIL` already determines the aggregate. Backend-only work proceeds without visual
configuration. Optional helper dry-runs and fixture transports are offline evidence only; they do not demonstrate a live
API response or the quality of a real application.

## Operation boundary

Design direction, UI content, image generation/editing, and visual review are distinct task-authorized operations. They
share the same fixed-endpoint HTTPS transport, task authorization validation, bounded request counts, cost reservation,
usage and reconciliation records, and task state. Models, service tiers, prices, modalities, token/output bounds, and
allowed file IDs are explicit per-operation configuration. Synthetic offline configuration builds request payloads and
estimates only; it can never authorize live execution.

Direction proposals are not adopted automatically. The direction record keeps proposal content, source hashes, decision
actor/reason/change note, version, and the previous direction hash. Later requests receive the full accepted direction
content and finding evidence, not IDs alone. Media Kit inputs are explicitly selected, limited to the task project root,
classified as normative, example, or visual asset, and hashed. Missing or conflicting identity is recorded; the helper
does not invent or silently replace brand rules.

The distributed contracts live in [`frontend-visual-quality`](../skills/frontend-visual-quality/SKILL.md) and
[`qa-projects`](../skills/qa-projects/SKILL.md). The integrated acceptance command details are in its
[acceptance-gate reference](../skills/frontend-visual-quality/references/acceptance-gate.md).
