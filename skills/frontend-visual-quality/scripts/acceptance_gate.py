"""Evidence-linked acceptance planning, build tracking, and final conclusions."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re

from visual_review import (
    ReviewError,
    atomic_write,
    canonical_json,
    exclusive_task_lock,
    has_symlink_component,
    iso_now,
    operation_authorization,
    read_json,
    read_task,
    write_json,
)

from review_evidence import consolidated_coverage, current_attempts, direction_hash


CHECK_STATUSES = {"PASS", "FAIL", "BLOCKED", "PASS WITH WARNINGS"}
CHECK_CATEGORIES = {
    "STATIC", "UNIT", "FEATURE", "INTEGRATION", "DATABASE", "API", "UI", "UX", "VISUAL",
    "ACCESSIBILITY", "FORMS", "LOADING", "ERROR", "EMPTY", "E2E", "SECURITY", "BUILD",
    "RUNTIME", "SMOKE", "REGRESSION",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def validate_acceptance_plan(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"schema_version", "frontend_impact", "components", "checks"}:
        raise ReviewError("Acceptance plan must match the documented schema.")
    if value.get("schema_version") != 1 or not isinstance(value.get("frontend_impact"), bool):
        raise ReviewError("Acceptance plan needs schema_version 1 and an explicit frontend_impact decision.")
    components = value.get("components")
    if not isinstance(components, list) or not components or any(not isinstance(item, str) or not item.strip() for item in components):
        raise ReviewError("Acceptance plan must identify its affected components.")
    checks = value.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ReviewError("Acceptance plan must define checks before execution.")
    normalized = []
    ids = set()
    for item in checks:
        if not isinstance(item, dict) or set(item) != {"id", "category", "required", "description"}:
            raise ReviewError("Each acceptance check must contain id, category, required, and description.")
        identifier = item["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{1,63}", identifier) or identifier == "external_visual_review" or identifier in ids:
            raise ReviewError("Acceptance check IDs must be unique lowercase identifiers.")
        if not isinstance(item["category"], str) or item["category"] not in CHECK_CATEGORIES or not isinstance(item["required"], bool):
            raise ReviewError(f"Acceptance check {identifier} has an invalid category or required flag.")
        if not isinstance(item["description"], str) or not item["description"].strip():
            raise ReviewError(f"Acceptance check {identifier} needs a concise description.")
        ids.add(identifier)
        normalized.append(dict(item))
    if value["frontend_impact"]:
        normalized.append({
            "id": "external_visual_review",
            "category": "VISUAL",
            "required": True,
            "description": "Required external visual review and Codex evidence evaluation.",
        })
    return {"schema_version": 1, "frontend_impact": value["frontend_impact"], "components": components, "checks": normalized}


def validate_build_context(value: object) -> dict:
    fields = {
        "served_version", "build_id", "source_sha256", "configuration_sha256",
        "visual_direction_sha256", "assets_sha256",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise ReviewError("Build context must identify the served version, build, source, configuration, visual direction, and assets.")
    for name in ("served_version", "build_id"):
        if not isinstance(value.get(name), str) or not value[name].strip() or len(value[name]) > 200:
            raise ReviewError(f"Build context {name} is required.")
    for name in fields - {"served_version", "build_id"}:
        if not isinstance(value.get(name), str) or not SHA256_RE.fullmatch(value[name]):
            raise ReviewError(f"Build context {name} must be a SHA-256 fingerprint.")
    return value


def _pending_report(manifest: dict, reason: str) -> bytes:
    return (f"# QA acceptance report: {manifest['task_id']}\n\n"
            f"Result: **pending_revalidation**\n\n{reason}\n").encode("utf-8")


def invalidate_acceptance(task_dir: Path, manifest: dict, state: dict, reason: str) -> None:
    """Publish the pending barrier under the task lock before saving new evidence."""
    if not manifest.get("acceptance_plan"):
        return
    atomic_write(task_dir / "report.md", _pending_report(manifest, reason))
    manifest.pop("conclusion", None)
    manifest["overall_conclusion"] = "pending_revalidation"
    manifest["pending"] = [reason]
    write_json(task_dir / "manifest.json", manifest)
    state.pop("conclusion", None)


def current_acceptance(task_dir: Path, manifest: dict, state: dict) -> dict:
    conclusion = state.get("conclusion")
    overall = manifest.get("overall_conclusion")
    if conclusion and conclusion == manifest.get("conclusion") and overall == conclusion.get("result"):
        try:
            if (task_dir / "report.md").read_bytes() == _report_text(manifest, conclusion).encode("utf-8"):
                return {"valid": True, "result": overall, "conclusion": conclusion}
        except OSError:
            pass
    pending = "pending" if overall in (None, "pending") and not conclusion else "pending_revalidation"
    return {"valid": False, "result": pending, "conclusion": None}


def record_build_context(task_dir: Path, build_file: Path) -> dict:
    task_dir = task_dir.expanduser().resolve()
    context = validate_build_context(read_json(build_file.expanduser(), 64 * 1024))
    fingerprint = canonical_hash(context)
    with exclusive_task_lock(task_dir):
        manifest, state, _ = read_task(task_dir)
        previous = state.get("build_fingerprint")
        if previous != fingerprint:
            invalidate_acceptance(task_dir, manifest, state, "Served build changed.")
            state.setdefault("build_history", []).append({
                "fingerprint": fingerprint,
                "previous_fingerprint": previous,
                "recorded_at": iso_now(),
            })
            state["build_context"] = context
            state["build_fingerprint"] = fingerprint
            manifest["build_context"] = context
            manifest["build_fingerprint"] = fingerprint
            manifest["build_context_recorded_at"] = iso_now()
        write_json(task_dir / "state.json", state)
        write_json(task_dir / "manifest.json", manifest)
    return {"task_id": manifest["task_id"], "build_fingerprint": fingerprint, "changed": previous != fingerprint}


def _safe_evidence(task_dir: Path, evidence_path: Path) -> tuple[str, str, int]:
    if has_symlink_component(evidence_path):
        raise ReviewError("Check evidence cannot use symlinks.")
    resolved = evidence_path.expanduser().resolve()
    if not resolved.is_relative_to(task_dir) or not resolved.is_file():
        raise ReviewError("Check evidence must be a regular file inside this private task folder.")
    if resolved.suffix.lower() not in {".md", ".txt", ".json"} or resolved.stat().st_size == 0 or resolved.stat().st_size > 1024 * 1024:
        raise ReviewError("Check evidence must be a non-empty sanitized Markdown, text, or JSON file under 1 MiB.")
    data = resolved.read_bytes()
    return resolved.relative_to(task_dir).as_posix(), hashlib.sha256(data).hexdigest(), len(data)


def record_check(
    task_dir: Path,
    check_id: str,
    status: str,
    evidence_path: Path,
    summary: str,
    related_call_id: str | None = None,
) -> dict:
    if status not in CHECK_STATUSES:
        raise ReviewError("Check status must be PASS, FAIL, BLOCKED, or PASS WITH WARNINGS.")
    if not isinstance(summary, str) or not summary.strip() or len(summary) > 1000:
        raise ReviewError("Check result needs a short sanitized evidence summary.")
    task_dir = task_dir.expanduser().resolve()
    path, digest, size = _safe_evidence(task_dir, evidence_path)
    with exclusive_task_lock(task_dir):
        manifest, state, _ = read_task(task_dir)
        plan = manifest.get("acceptance_plan")
        if not isinstance(plan, dict) or not isinstance(plan.get("checks"), list):
            raise ReviewError("This task has no acceptance plan; legacy tasks cannot be promoted to approved.")
        check = next((item for item in plan["checks"] if item["id"] == check_id), None)
        if check is None:
            raise ReviewError("Check ID was not declared before execution in the acceptance plan.")
        if status == "PASS WITH WARNINGS" and check["required"]:
            raise ReviewError("A required check cannot be downgraded to a warning.")
        if check_id == "external_visual_review":
            if not related_call_id:
                raise ReviewError("External visual review needs a related completed review call ID.")
            attempts = current_attempts(manifest, state)
            attempt = attempts[-1] if attempts else None
            if not attempt or attempt.get("call_id") != related_call_id:
                raise ReviewError("External visual review must link to the latest attempt for this build, direction, and matrix.")
            if status == "PASS":
                _, missing = consolidated_coverage(task_dir, manifest, state, attempts)
                if missing:
                    raise ReviewError("Visual coverage is incomplete or its evidence is invalid.")
        result = {
            "check_id": check_id,
            "category": check["category"],
            "required": check["required"],
            "status": status,
            "summary": summary.strip(),
            "evidence_file": path,
            "evidence_sha256": digest,
            "evidence_bytes": size,
            "related_call_id": related_call_id,
            "review_ids": sorted(consolidated_coverage(task_dir, manifest, state, attempts)[0]) if check_id == "external_visual_review" else [],
            "direction_sha256": direction_hash(manifest) if check_id == "external_visual_review" or check["category"] in {"UI", "UX", "VISUAL", "ACCESSIBILITY"} else None,
            "build_fingerprint": state.get("build_fingerprint"),
            "recorded_at": iso_now(),
        }
        invalidate_acceptance(task_dir, manifest, state, f"Check {check_id} changed.")
        state.setdefault("check_results", {})[check_id] = result
        write_json(task_dir / "state.json", state)
    return result


def _visual_gate_state(task_dir: Path, manifest: dict, state: dict) -> tuple[str | None, str | None]:
    if not manifest.get("review_required"):
        return None, None
    if not manifest.get("api_execution_authorized"):
        return "BLOCKED", "External visual review is required, but this task has no API execution authorization."
    attempts = current_attempts(manifest, state)
    if not attempts:
        return "BLOCKED", "Required visual review lacks complete criterion-to-screen coverage for the served build, direction, or matrix."
    if attempts[-1].get("status") != "completed":
        return "BLOCKED", "Latest required visual review did not complete successfully."
    direction = direction_hash(manifest)
    if direction and state.get("build_context", {}).get("visual_direction_sha256") != direction:
        return "BLOCKED", "The adopted visual direction has not been recorded in the served build."
    calls, missing = consolidated_coverage(task_dir, manifest, state, attempts)
    if missing:
        return "BLOCKED", "Visual review lacks complete criterion-to-screen coverage or intact evidence: " + ", ".join(missing)
    result = state.get("check_results", {}).get("external_visual_review")
    if not result or result.get("related_call_id") != attempts[-1]["call_id"] or set(result.get("review_ids", [])) != calls:
        return "BLOCKED", "Codex evaluation of the consolidated visual evidence is not recorded."
    return None, None


def _check_evidence_valid(task_dir: Path, result: dict, state: dict) -> bool:
    if result.get("build_fingerprint") != state.get("build_fingerprint"):
        return False
    path = task_dir / result.get("evidence_file", "")
    if has_symlink_component(path) or not path.is_file():
        return False
    data = path.read_bytes()
    return len(data) == result.get("evidence_bytes") and hashlib.sha256(data).hexdigest() == result.get("evidence_sha256")


def _report_text(manifest: dict, conclusion: dict) -> str:
    lines = [
        f"# QA acceptance report: {manifest.get('task_id', 'unknown')}",
        "",
        f"Result: **{conclusion['result']}**",
        f"Frontend impact: **{str(conclusion['frontend_impact']).lower()}**",
        f"External visual review required: **{str(conclusion['review_required']).lower()}**",
        f"API execution authorized: **{str(conclusion['api_execution_authorized']).lower()}**",
        f"Build fingerprint: `{conclusion.get('build_fingerprint') or 'unrecorded'}`",
        "",
        "## Checks",
        "",
    ]
    for item in conclusion["checks"]:
        lines.append(f"- `{item['check_id']}` ({item['category']}): **{item['status']}** — {item['summary']}")
    if conclusion["pending"]:
        lines.extend(["", "## Pending", ""])
        lines.extend(f"- {item}" for item in conclusion["pending"])
    lines.extend(["", "Model review is consultive. This report does not prove a live API call or product visual quality unless the linked evidence records it.", ""])
    return "\n".join(lines)


def finalize_task(task_dir: Path) -> dict:
    task_dir = task_dir.expanduser().resolve()
    with exclusive_task_lock(task_dir):
        manifest, state, auth = read_task(task_dir)
        plan = manifest.get("acceptance_plan")
        if not isinstance(plan, dict):
            raise ReviewError("Legacy task has no predeclared acceptance plan and cannot be promoted to PASS.")
        statuses = []
        pending = []
        results = state.get("check_results", {})
        for check in plan["checks"]:
            result = results.get(check["id"])
            if result is None:
                if check["required"]:
                    statuses.append("BLOCKED")
                    pending.append(f"Required check {check['id']} has no recorded evidence.")
                continue
            if check["id"] == "external_visual_review" and result["status"] != "FAIL":
                attempts = current_attempts(manifest, state)
                if not attempts or result.get("related_call_id") != attempts[-1]["call_id"]:
                    statuses.append("BLOCKED")
                    pending.append("The recorded visual check does not evaluate the latest applicable review.")
                    continue
            if (result.get("required") != check["required"] or not _check_evidence_valid(task_dir, result, state)
                    or check["category"] in {"UI", "UX", "VISUAL", "ACCESSIBILITY"}
                    and result.get("direction_sha256") != direction_hash(manifest)):
                statuses.append("BLOCKED")
                pending.append(f"Check {check['id']} evidence is invalid, modified, or stale.")
                continue
            statuses.append(result["status"])
            if result["status"] in {"BLOCKED", "FAIL", "PASS WITH WARNINGS"}:
                pending.append(f"Check {check['id']} is {result['status']}.")
        if manifest.get("review_required"):
            visual_status, visual_pending = _visual_gate_state(task_dir, manifest, state)
            if visual_status:
                statuses.append(visual_status)
                pending.append(visual_pending)
        if any(status == "FAIL" for status in statuses):
            overall = "FAIL"
        elif any(status == "BLOCKED" for status in statuses):
            overall = "BLOCKED"
        elif any(status == "PASS WITH WARNINGS" for status in statuses):
            overall = "PASS WITH WARNINGS"
        elif statuses and all(status == "PASS" for status in statuses):
            overall = "PASS"
        else:
            overall = "BLOCKED"
            pending.append("No complete set of required checks was available.")
        conclusion = {
            "result": overall,
            "frontend_impact": plan["frontend_impact"],
            "review_required": manifest.get("review_required", False),
            "api_execution_authorized": manifest.get("api_execution_authorized", False),
            "build_fingerprint": state.get("build_fingerprint"),
            "plan_sha256": manifest.get("acceptance_plan_sha256"),
            "checks": [results[item["id"]] for item in plan["checks"] if item["id"] in results],
            "pending": list(dict.fromkeys(pending)),
            "finalized_at": iso_now(),
        }
        invalidate_acceptance(task_dir, manifest, state, "Publishing a freshly evaluated conclusion.")
        state["conclusion"] = conclusion
        manifest["conclusion"] = conclusion
        manifest["overall_conclusion"] = overall
        manifest["pending"] = conclusion["pending"]
        write_json(task_dir / "state.json", state)
        write_json(task_dir / "manifest.json", manifest)
        atomic_write(task_dir / "report.md", _report_text(manifest, conclusion).encode("utf-8"))
        return conclusion
