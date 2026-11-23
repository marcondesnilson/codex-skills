"""Local project design decisions stored beside private task evidence."""

from pathlib import Path

from visual_review import (
    ReviewError, canonical_json, digest_bytes, exclusive_task_lock, has_symlink_component,
    read_json, write_json,
)


MEDIA_KIT_NAMES = ("Media Kit", "MediaKit", "MEDIAKIT", "media-kit", "media_kit")


def media_kit(project_root: Path, configured: Path | None = None) -> Path | None:
    root = project_root.resolve()
    candidates = (root / configured,) if configured else tuple(root / name for name in MEDIA_KIT_NAMES)
    for path in candidates:
        if path.is_dir() and not has_symlink_component(path) and path.resolve().is_relative_to(root):
            return path.resolve()
    if configured:
        raise ReviewError("Configured Media Kit must be a local directory inside the project.")
    return None


def _registry(evidence_root: Path, manifest: dict) -> Path | None:
    root = manifest.get("project_root")
    if not root:
        return None
    key = digest_bytes(canonical_json([str(Path(root).resolve()), manifest["project"]]))
    path = evidence_root / "_project-directions" / key
    if has_symlink_component(path):
        raise ReviewError("Project direction registry cannot use symlinks.")
    return path


def load_direction(evidence_root: Path, manifest: dict) -> dict | None:
    registry = _registry(evidence_root, manifest)
    path = registry / "direction.json" if registry else None
    if not path or not path.exists():
        return None
    history = read_json(path, 1024 * 1024)
    direction = history[-1]
    if direction["content_sha256"] != digest_bytes(canonical_json(direction["content"])):
        raise ReviewError("Project direction content has changed outside its decision record.")
    return direction


def persist_direction(evidence_root: Path, manifest: dict, direction: dict, *, before_publish=lambda: None) -> dict:
    registry = _registry(evidence_root, manifest)
    if registry is None:
        before_publish()
        return direction
    registry.mkdir(mode=0o700, parents=True, exist_ok=True)
    with exclusive_task_lock(registry):
        path = registry / "direction.json"
        previous = load_direction(evidence_root, manifest)
        history = read_json(path, 1024 * 1024) if previous else []
        for record in history:
            if (record["origin_task_id"] == manifest["task_id"]
                    and record["decision_sha256"] == direction["decision_sha256"]):
                return record
        adopted = manifest.get("adopted_visual_direction")
        if previous and (not adopted or adopted.get("decision_sha256") != previous["decision_sha256"]):
            raise ReviewError("Project direction changed in another task; reload it before adopting a replacement.")
        before_publish()
        record = {**direction, "project_version": len(history) + 1, "origin_task_id": manifest["task_id"]}
        history.append(record)
        write_json(path, history)
        return record
