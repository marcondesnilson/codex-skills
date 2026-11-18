"""Verify complete offline sync and execution of a temporary distributed copy."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SYNC_SCRIPT = REPOSITORY_ROOT / "scripts" / "sync-skills.py"


@unittest.skipUnless(SYNC_SCRIPT.is_file(), "source synchronizer is not part of a distributed skill folder")
class SkillDistributionTests(unittest.TestCase):
    def test_sync_copies_and_executes_the_complete_skill_offline(self):
        with tempfile.TemporaryDirectory(prefix="frontend-visual-quality-dist-") as temporary:
            destination = Path(temporary) / "installed-skills"
            subprocess.run([
                sys.executable,
                str(SYNC_SCRIPT),
                "--source", str(REPOSITORY_ROOT),
                "--destination", str(destination),
                "--apply",
            ], check=True, capture_output=True, text=True, timeout=30)
            copied = destination / "frontend-visual-quality"
            self.assertTrue((copied / "SKILL.md").is_file())
            self.assertTrue((copied / "references" / "api-review.md").is_file())
            self.assertTrue((copied / "schemas" / "review-result.schema.json").is_file())
            self.assertTrue((copied / "scripts" / "visual_review.py").is_file())
            def distributable(path):
                relative = path.relative_to(SKILL_ROOT)
                return path.is_file() and "__pycache__" not in relative.parts and path.suffix.lower() not in {".pyc", ".pyo"}

            source_files = sorted(path.relative_to(SKILL_ROOT) for path in SKILL_ROOT.rglob("*") if distributable(path))
            copied_files = sorted(
                path.relative_to(copied) for path in copied.rglob("*")
                if path.is_file() and "__pycache__" not in path.relative_to(copied).parts and path.suffix.lower() not in {".pyc", ".pyo"}
            )
            self.assertEqual(source_files, copied_files)
            for relative in source_files:
                self.assertEqual(
                    hashlib.sha256((SKILL_ROOT / relative).read_bytes()).digest(),
                    hashlib.sha256((copied / relative).read_bytes()).digest(),
                    str(relative),
                )
            subprocess.run([sys.executable, str(copied / "scripts" / "visual_review.py"), "--help"], check=True, capture_output=True, text=True, timeout=10)
            env = {
                "PATH": os.defpath,
                "HOME": temporary,
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            copied_tests = subprocess.run([
                sys.executable, "-m", "unittest", "discover", "-s", str(copied / "scripts" / "tests"), "-v",
            ], check=False, capture_output=True, text=True, timeout=30, env=env, cwd=temporary)
            self.assertEqual(copied_tests.returncode, 0, copied_tests.stdout + copied_tests.stderr)


if __name__ == "__main__":
    unittest.main()
