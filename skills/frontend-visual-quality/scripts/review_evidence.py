"""Persistent visual criteria and attempt-level evidence."""

from pathlib import Path

from visual_review import (
    ReviewError, canonical_json, digest_bytes, exclusive_task_lock, has_symlink_component,
    iso_now, read_json, read_task, validate_criteria, has_complete_coverage, write_json,
)


OPERATIONS = {"visual_review", "visual_reevaluation"}


def direction_hash(manifest: dict) -> str | None:
    direction = manifest.get("adopted_visual_direction")
    return digest_bytes(canonical_json(direction["content"])) if direction else None


def rows(criteria: list[dict]) -> dict:
    return {(criterion["id"], row["id"]): (criterion["description"], row)
            for criterion in criteria for row in criterion["coverage"]}


def register_criteria(task_dir: Path, criteria_path: Path, reason: str = "") -> dict:
    criteria = validate_criteria(read_json(criteria_path))
    if not has_complete_coverage(criteria):
        raise ReviewError("A visual matrix needs explicit evidence for every row.")
    with exclusive_task_lock(task_dir):
        manifest, state, _ = read_task(task_dir)
        matrix = state.get("visual_matrix")
        if matrix and matrix["criteria"] == criteria:
            return matrix
        if matrix and len(reason.strip()) < 10:
            raise ReviewError("Changing the visual matrix requires an explicit decision and reason.")
        from acceptance_gate import invalidate_acceptance
        invalidate_acceptance(task_dir, manifest, state, "Visual criteria matrix changed.")
        matrix = store_matrix(state, criteria, reason or "Initial visual scope")
        write_json(task_dir / "state.json", state)
        write_json(task_dir / "manifest.json", manifest)
        return matrix


def store_matrix(state: dict, criteria: list[dict], reason: str) -> dict:
    history = state.setdefault("visual_matrix_history", [])
    matrix = {"version": len(history) + 1, "sha256": digest_bytes(canonical_json(criteria)),
              "criteria": criteria, "reason": reason.strip(), "recorded_at": iso_now()}
    history.append(matrix)
    state["visual_matrix"] = matrix
    return matrix


def validate_batch(matrix: dict, criteria: list[dict]) -> None:
    planned = rows(matrix["criteria"])
    if any(planned.get(key) != row for key, row in rows(criteria).items()):
        raise ReviewError("Batch criteria differ from the registered visual matrix; register an explicit revision first.")


def artifact(path: Path, task_dir: Path) -> dict:
    content = path.read_bytes()
    return {"file": path.relative_to(task_dir).as_posix(), "size_bytes": len(content),
            "sha256": digest_bytes(content)}


def artifacts_valid(task_dir: Path, attempt: dict) -> bool:
    captures = attempt.get("captures")
    context = attempt.get("context_artifact")
    review = attempt.get("review_artifact")
    if not captures or not context or not review:
        return False
    for entry in [*captures, context, review]:
        try:
            path = task_dir / entry["file"]
            if has_symlink_component(path) or not path.resolve().is_relative_to(task_dir) or not path.is_file():
                return False
            if path.stat().st_size != entry["size_bytes"] or artifact(path, task_dir)["sha256"] != entry["sha256"]:
                return False
        except (KeyError, OSError, ValueError):
            return False
    return all(item.get("build_fingerprint") == attempt["build_fingerprint"]
               for item in captures if item["role"] == "result")


def current_attempts(manifest: dict, state: dict) -> list[dict]:
    matrix = state.get("visual_matrix") or {}
    build = state.get("build_fingerprint")
    if not build:
        return []
    return [item for item in state.get("attempts", [])
            if item.get("operation") in OPERATIONS
            and item.get("task_scope") == {key: manifest[key] for key in ("task_id", "project", "scope")}
            and item.get("build_fingerprint") == build
            and item.get("direction_sha256") == direction_hash(manifest)
            and item.get("matrix_version") == matrix.get("version")
            and item.get("matrix_sha256") == matrix.get("sha256")]


def consolidated_coverage(task_dir: Path, manifest: dict, state: dict, attempts: list[dict]) -> tuple[set, list[str]]:
    matrix = state.get("visual_matrix")
    if not matrix:
        return set(), ["Visual matrix has not been registered."]
    # Reuse only rows that stayed identical through every intervening matrix
    # version, and only within the same served build and adopted direction.
    current_rows = rows(matrix["criteria"])
    attempts_ids = {item["call_id"] for item in attempts}
    versions = {item["version"]: rows(item["criteria"]) for item in state.get("visual_matrix_history", [])}
    latest = {}
    for attempt in state.get("attempts", []):
        current = attempt.get("call_id") in attempts_ids
        old_version = attempt.get("matrix_version")
        if not current and not (
            attempts and isinstance(old_version, int) and old_version < matrix["version"]
            and all(attempt.get(field) == attempts[-1].get(field)
                    for field in ("task_scope", "build_fingerprint", "direction_sha256", "brief_sha256"))
        ):
            continue
        for row in attempt.get("coverage_matrix", []):
            key = row["criterion_id"], row["id"]
            if current or key in current_rows and all(
                versions.get(version, {}).get(key) == current_rows[key]
                for version in range(old_version, matrix["version"] + 1)
            ):
                latest[key] = attempt, row
    calls, missing, validity = set(), [], {}
    for key, (_, planned) in rows(matrix["criteria"]).items():
        attempt, row = latest.get(key, ({}, {}))
        call_id = attempt.get("call_id")
        if call_id and call_id not in validity:
            validity[call_id] = attempt.get("status") == "completed" and artifacts_valid(task_dir, attempt)
        if (not validity.get(call_id) or row.get("status") != "evaluated"
                or not set(planned["required_capture_ids"]).issubset(row.get("evidence_capture_ids", []))
                or not planned["required_capture_ids"]):
            missing.append("/".join(key))
        else:
            calls.add(call_id)
    return calls, missing
