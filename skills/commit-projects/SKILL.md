---
name: commit-projects
description: Analyze the complete current Git diff, reconcile required project documentation, apply independent Semantic Versioning bumps, and commit one or multiple repositories in the current workspace. Use when the user explicitly asks Codex to execute the version-and-commit workflow across the current project or projects.
---

# Commit projects

Run a safe, diff-driven SemVer and local commit workflow in the user's current workspace. Support both layouts:

- the current folder is a single Git repository;
- the current folder contains multiple independent Git repositories;
- the current folder is a Git repository and also contains independent child repositories.

Treat every repository independently. Never push unless the user separately and explicitly requests it.

## Authorization boundary

Do not create a commit merely because this skill was read or mentioned in documentation. Start the mutating workflow only
when the user explicitly asks to execute it, for example:

```text
$commit-projects
```

or:

```text
Execute integralmente o $commit-projects agora.
```

Read-only discovery is allowed before mutation. Do not initialize Git, discard changes, rewrite history, reset files,
clean the worktree, push, or open a pull request unless the user explicitly authorizes the corresponding action.

An explicit invocation also authorizes creating or updating documentation needed to describe the reviewed diff accurately.
This is completion work inside the changed project's scope, not permission to modify unrelated behavior, fix arbitrary code,
or perform external side effects.

## Local instructions take precedence

Before acting, locate and read the applicable instructions in this order:

1. every applicable `AGENTS.md`, from the workspace root down to the repository;
2. a workspace or repository `commit.md`, when present;
3. `documentation/index.md`, current-state MOCs, and documentation relevant to changed files;
4. repository manifests, tests, routes, and executable configuration needed to verify the documentation.

Use a local `commit.md` as the repository-specific extension of this workflow. It may define stricter discovery,
validation, staging, response, or message rules. It does not grant permission to commit or push and cannot weaken safety
constraints from higher-priority instructions. Treat documentation reconciliation as an intrinsic step in every project:
local instructions may define its format and location, but a repairable documentation gap must not be used by itself to
skip an otherwise valid changed repository.

## Discover repositories

Let the user's current working directory be the workspace scope.

1. Resolve whether the current directory is inside a Git worktree with
   `git rev-parse --show-toplevel`.
2. If the current directory is below a repository root, use that containing repository as the single default scope. Do not
   scan unrelated siblings unless the user explicitly selects their common parent.
3. If the current directory is itself the repository root, include it.
4. Scan immediate child directories of the workspace. Include a child only when
   `git -C <child> rev-parse --show-toplevel` resolves to that exact child directory. This avoids treating ordinary
   subdirectories inherited from a parent worktree as separate projects.
5. Deduplicate repositories by canonical top-level path.
6. When both a root repository and independent child repositories exist, process changed child repositories first and the
   root repository last. Re-inventory the root after child commits because gitlinks or shared metadata may have changed.
7. Report directories that look project-like but are not Git repositories only when this affects the requested scope. Do
   not initialize them automatically.

If exactly one repository is discovered, run the same workflow for that repository. If several are discovered, classify,
version, validate, and commit each independently.

## Inventory the complete diff

For every repository, inspect all current changes against `HEAD`:

```sh
git status --short --untracked-files=all
git diff --stat
git diff --name-status
git diff
git diff --cached --stat
git diff --cached --name-status
git diff --cached
```

Open and review every relevant untracked file because ordinary `git diff` does not show its contents. Identify generated
files, binaries, caches, dumps, logs, credentials, secrets, and pre-existing user edits. Preserve all user changes.

If a repository is clean, do not change `VERSION` and do not create an empty commit.

Stop only the affected repository and report it as blocked when there is a merge/rebase/cherry-pick conflict, a suspected
secret or unsafe artifact, an external side effect outside the authorization, an indeterminate version, or a functional
failure caused by the diff. A blocked repository does not automatically block other independent repositories.

## Reconcile required documentation

For every changed repository, determine from the complete diff and executable sources whether the change affects behavior,
public contracts, configuration, architecture, security, dependencies, deployment, operations, commands, or maintenance
conventions.

Before classifying or bumping the version:

1. Locate the project's normative documentation using its `AGENTS.md`, MOCs, README, docs tree, or established equivalent.
2. Compare the documentation with the reviewed diff, manifests, routes, tests, workflows, and runtime configuration.
3. When documentation is absent, incomplete, or stale, create or update the smallest appropriate document from confirmed
   facts. Follow the project's existing structure and update indexes, frontmatter, links, and backlinks when applicable.
4. Re-inventory the repository so documentation created by this workflow becomes part of the same versioned diff and
   commit.

Do not stop merely to report a documentation gap that can be repaired safely from the repository evidence. Do not invent
intent, causes, guarantees, commands, or contracts that the diff does not establish. Block only when accurate documentation
requires an unresolved product decision, unavailable facts, new authority, or reconciliation of contradictory sources that
cannot be resolved from the current scope.

### Documentation ownership in multi-project workspaces

Choose documentation ownership by the scope of the fact, never merely by the presence of a Git repository at the workspace
root:

- Keep implementation, configuration, operation, commands, risks, and architecture exclusive to one project inside that
  project's own documentation tree, even when both the workspace root and the project directory are Git repositories.
- Reserve the workspace-root documentation for facts genuinely shared by two or more projects, such as cross-project
  contracts, shared architecture, ownership boundaries, coordinated operations, and workspace-wide governance.
- When a change affects several projects, update each project's local documentation only for its own implementation and
  update the root documentation only for the shared contract or behavior. Link between scopes using the workspace's
  established convention instead of duplicating the same rule.
- When a child project changes without shared impact, do not modify root documentation or the root `VERSION` merely to
  mirror the child change.
- Include project-local documentation in that project's commit. If the root is a Git repository, include genuinely shared
  root documentation in the root commit, processing it after child commits as required by repository discovery.

When correct shared documentation at the workspace root is writable but not part of any discovered Git repository, update
it if it is in scope and report that it could not be included in a project commit; do not falsely claim it was committed.
Classify SemVer by the underlying behavior, not by the number of documentation files added. A documentation-only change
remains `PATCH` unless it itself changes a published contract.

## Classify Semantic Versioning

Classify the complete pre-bump diff of each repository independently:

- `MAJOR`: confirmed incompatible contract or behavior, removed functionality, or a change that requires existing
  consumers to change.
- `MINOR`: a new backward-compatible feature, endpoint, option, filter, field, integration, or capability.
- `PATCH`: a bug fix, documentation or operational adjustment, compatible refactor, tests, observability, performance, or
  another change without a new public capability.

Be conservative: use `PATCH` without a new capability, `MINOR` for a compatible addition, and `MAJOR` only for a real
compatibility break. Classify by impact rather than file count. Exclude the `VERSION` edit made by this workflow from the
classification.

## Validate and bump VERSION

Use a `VERSION` at repository root. Accept only `X.Y.Z`; a single legacy trailing LF may be accepted as input and
normalized. Reject other whitespace, CRLF, suffixes, prefixes, extra lines, or ambiguous formats.

Choose the version path from the initial inventory:

- When `VERSION` is tracked in `HEAD`, read the base from `HEAD`, not from a possibly edited worktree file, and apply the
  SemVer bump below.
- When `VERSION` is absent from `HEAD` but already exists as a valid untracked file in the initial inventory, treat its
  value as the explicitly prepared initial release. Normalize it, include it in the commit, and do not increment it in
  that first commit because no historical base exists.
- When no `VERSION` exists in either `HEAD` or the worktree, create it as exact `1.0.0`, include it in the first commit,
  and do not increment it in that commit.
- When an existing initial file is invalid or ambiguous, block that repository rather than overwrite it silently.

For a version tracked in `HEAD`, apply exactly one bump per changed repository:

- `MAJOR`: `X.Y.Z` to `(X+1).0.0`;
- `MINOR`: `X.Y.Z` to `X.(Y+1).0`;
- `PATCH`: `X.Y.Z` to `X.Y.(Z+1)`.

Write the resulting version before the commit with no whitespace and no newline:

```sh
printf '%s' "$new_version" > VERSION
```

Verify the SemVer regex, byte count, and hexadecimal bytes. The committed file must contain exactly the version string.

## Validate changes

Choose focused tests, lint, static analysis, builds, route inspection, or other checks based on the changed files and the
repository's documented commands. Confirm important contracts in executable code instead of trusting stale documentation.
Validate documentation structure proportionally as well, including required metadata, MOC entries, links, and backlinks
where the project uses them.

After tests or builds, run the complete status inventory again. Inspect new artifacts and do not stage caches, logs,
credentials, or temporary output merely because validation generated them. A proven regression caused by the diff blocks
the affected commit; an unrelated or environmental limitation may be reported when the remaining evidence is proportional
to the change.

## Stage and perform the final review

For an authorized, changed, and unblocked repository:

```sh
git add -A
git diff --cached --stat
git diff --cached --name-status
git diff --cached
git diff --cached --check
```

Confirm that the staged diff is exactly the reviewed complete diff, including additions and deletions; `VERSION` is staged
and byte-exact; no secret or unwanted artifact is included; documentation matches the final behavior; and the SemVer class
still fits the staged impact.

If staging changes the impact assessment, recalculate the class and version, rerun affected validations, restage, and
repeat the review.

## Finalize the message and commit

Generate the message only after reviewing the complete staged diff. Immediately before `git commit`, rewrite it if needed
so it accurately describes the primary staged outcome.

The message must be clear, specific to that repository, based only on the diff, and contain no conventional fixed prefix
such as `feat:`, `fix:`, or `chore:`.

Create one local commit per repository. Do not combine independent repositories in one claimed commit and do not push.

After every commit, verify:

```sh
git status --short --untracked-files=all
git log -1 --oneline
git show --stat --oneline --decorate HEAD
git show HEAD:VERSION | xxd -p
```

Confirm the commit hash, final message, full reviewed diff, byte-exact `VERSION`, and final worktree state. If validation or
commit hooks create more files, inspect and report them; do not hide them or create an extra commit automatically.

## Report results

Follow a stricter local `commit.md` response format when one exists. Otherwise, for each committed repository, begin its
block with the classification:

```text
MAJOR|MINOR|PATCH
Projeto: <path>
Nova versão: <X.Y.Z>
Descritivo das alterações: <up to 10 factual lines based only on the diff>
Mensagem de commit: <final message without a fixed prefix>
Diff completo incluído no commit: sim
Commit: <hash>
Validações: <commands and objective results>
```

List clean and blocked repositories after committed blocks, with an objective reason and without inventing a class or
version. If no repository has changes, say that there is no diff to version and create no commit.
