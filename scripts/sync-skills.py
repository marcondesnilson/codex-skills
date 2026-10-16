#!/usr/bin/env python3
"""Sync complete Codex skill directories from the canonical Git repository.

Default mode is dry-run. --apply writes only managed/unmodified files and never
deletes local files. Existing unmanaged differences are reported as conflicts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SOURCE = "https://github.com/marcondesnilson/codex-skills.git"
STATE_NAME = ".codex-skills-sync.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_state(path):
    if not path.exists():
        return {"files": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("files"), dict):
        raise ValueError("Invalid state manifest")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path,
                        help="Directory containing installed skill folders (e.g. ~/.codex/skills)")
    parser.add_argument("--ref", default="main", help="Source branch or tag (default: main)")
    parser.add_argument("--apply", action="store_true", help="Apply safe changes; default is dry-run")
    parser.add_argument("--source", type=Path, help="Existing trusted local codex-skills checkout (offline)")
    args = parser.parse_args()
    dest = args.destination.expanduser().resolve()
    if dest.is_symlink():
        parser.error("Destination must not be a symlink")
    dest.mkdir(parents=True, exist_ok=True) if args.apply else None
    with tempfile.TemporaryDirectory(prefix="codex-skills-sync-") as tmp:
        if args.source:
            source = args.source.expanduser().resolve()
        else:
            source = Path(tmp) / "source"
            subprocess.run(["git", "clone", "--quiet", "--depth", "1",
                            "--branch", args.ref, SOURCE, str(source)], check=True)
        skills = source / "skills"
        if not skills.is_dir():
            parser.error("Source does not contain skills/")
        state_path = dest / STATE_NAME
        state = load_state(state_path)
        prior = state["files"]
        updated = dict(prior)
        counts = {"add": 0, "update": 0, "same": 0, "conflict": 0}
        for skill in sorted(skills.iterdir()):
            if not skill.is_dir() or skill.is_symlink() or not (skill / "SKILL.md").is_file():
                continue
            for origin in sorted(skill.rglob("*")):
                if not origin.is_file() or origin.is_symlink() or ".git" in origin.parts:
                    continue
                relative = origin.relative_to(skills)
                key = relative.as_posix()
                target = dest / relative
                if any(p.is_symlink() for p in target.parents if p != dest and dest in p.parents):
                    print("CONFLICT symlink parent:", key)
                    counts["conflict"] += 1
                    continue
                if target.is_symlink() or (target.exists() and not target.is_file()):
                    print("CONFLICT non-regular target:", key)
                    counts["conflict"] += 1
                    continue
                upstream = digest(origin)
                current = digest(target) if target.exists() else None
                if current == upstream:
                    counts["same"] += 1
                    if args.apply:
                        updated[key] = upstream
                    continue
                if current is not None and current != prior.get(key):
                    print("CONFLICT local modification/unmanaged file:", key)
                    counts["conflict"] += 1
                    continue
                operation = "update" if current is not None else "add"
                print(operation.upper(), key)
                counts[operation] += 1
                if args.apply:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as staging:
                        staging.write(origin.read_bytes())
                        staging_name = staging.name
                    os.replace(staging_name, target)
                    updated[key] = upstream
        if args.apply:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dest,
                                             delete=False) as staging:
                json.dump({"files": updated}, staging, indent=2, sort_keys=True)
                staging.write("\n")
                staging_name = staging.name
            os.replace(staging_name, state_path)
        print("Summary:", ", ".join(f"{k}={v}" for k, v in counts.items()))
        print("Mode:", "applied" if args.apply else "dry-run")
        return 2 if counts["conflict"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        sys.exit(1)
