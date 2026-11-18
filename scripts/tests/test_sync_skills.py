import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "sync-skills.py"


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): (
            "directory" if path.is_dir() else path.read_bytes()
        )
        for path in sorted(root.rglob("*"))
    }


class SyncSkillsPythonCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.skills = self.source / "skills"
        self.skill = self.skills / "example"
        self.destination = self.root / "destination"
        self.skill.mkdir(parents=True)
        self.destination.mkdir()
        (self.skill / "SKILL.md").write_text("# Example\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def write_source(self, relative, content):
        path = self.skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def write_destination(self, relative, content):
        path = self.destination / "example" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def run_sync(self, apply=False):
        command = [
            sys.executable,
            str(SCRIPT),
            "--source",
            str(self.source),
            "--destination",
            str(self.destination),
        ]
        if apply:
            command.append("--apply")
        return subprocess.run(command, check=False, capture_output=True, text=True)

    def read_manifest(self):
        return json.loads((self.destination / ".codex-skills-sync.json").read_text())

    def test_source_caches_are_skipped_but_real_skill_files_are_synced(self):
        real_files = {
            "module.py": b"print('module')\n",
            "references/guide.md": b"Reference\n",
            "schemas/config.json": b'{"enabled": true}\n',
            "scripts/tests/test_example.py": b"def test_example(): pass\n",
        }
        for relative, content in real_files.items():
            self.write_source(relative, content)
        caches = {
            "__pycache__/module.cpython-312.pyc": b"bytecode in cache dir",
            "scripts/__pycache__/test_example.cpython-312.pyc": b"test bytecode",
            "module.pyc": b"loose bytecode",
            "legacy.pyo": b"optimized bytecode",
        }
        for relative, content in caches.items():
            self.write_source(relative, content)

        result = self.run_sync(apply=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest_files = self.read_manifest()["files"]
        for relative, content in real_files.items():
            self.assertEqual((self.destination / "example" / relative).read_bytes(), content)
            self.assertIn(f"example/{relative}", manifest_files)
        for relative in caches:
            self.assertFalse((self.destination / "example" / relative).exists())
            self.assertNotIn(f"example/{relative}", manifest_files)

    def test_different_source_and_destination_caches_do_not_conflict(self):
        caches = {
            "__pycache__/module.cpython-312.pyc": b"source bytecode",
            "module.pyc": b"source stray bytecode",
            "module.pyo": b"source optimized bytecode",
        }
        for relative, content in caches.items():
            self.write_source(relative, content)
            self.write_destination(relative, b"different destination cache")
        (self.destination / "example" / "SKILL.md").write_text("# Example\n", encoding="utf-8")

        result = self.run_sync()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("conflict=0", result.stdout)
        for relative in caches:
            self.assertEqual(
                (self.destination / "example" / relative).read_bytes(),
                b"different destination cache",
            )

    def test_legacy_manifest_cache_records_are_inert_and_preserved(self):
        cache_paths = {
            "example/__pycache__/module.cpython-312.pyc": b"legacy managed cache",
            "example/module.pyo": b"legacy unmanaged cache",
        }
        for key, content in cache_paths.items():
            relative = Path(*key.split("/")[1:])
            self.write_source(relative, b"new source cache")
            self.write_destination(relative, content)
        legacy_records = {key: sha256(b"old cache hash") for key in cache_paths}
        (self.destination / ".codex-skills-sync.json").write_text(
            json.dumps({"files": legacy_records}), encoding="utf-8"
        )

        result = self.run_sync(apply=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("conflict=0", result.stdout)
        self.assertEqual(
            {key: self.read_manifest()["files"][key] for key in legacy_records},
            legacy_records,
        )
        for key, content in cache_paths.items():
            relative = Path(*key.split("/")[1:])
            self.assertEqual((self.destination / "example" / relative).read_bytes(), content)

    def test_local_python_source_modification_remains_a_conflict(self):
        source = b"value = 'upstream'\n"
        local = b"value = 'local customization'\n"
        self.write_source("scripts/module.py", source)
        self.write_destination("scripts/module.py", local)
        (self.destination / ".codex-skills-sync.json").write_text(
            json.dumps(
                {
                    "files": {
                        "example/scripts/module.py": sha256(source),
                    }
                }
            ),
            encoding="utf-8",
        )

        result = self.run_sync(apply=True)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("CONFLICT local modification/unmanaged file: example/scripts/module.py", result.stdout)
        self.assertEqual((self.destination / "example/scripts/module.py").read_bytes(), local)

    def test_dry_run_does_not_write_anything(self):
        self.write_source("module.py", b"value = 'upstream'\n")
        self.write_destination("module.py", b"value = 'local'\n")
        (self.destination / ".codex-skills-sync.json").write_text(
            json.dumps({"files": {"example/module.py": sha256(b"value = 'upstream'\n")}}),
            encoding="utf-8",
        )
        before = snapshot(self.destination)

        result = self.run_sync()

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.destination), before)

    def test_second_run_after_generating_caches_has_no_conflicts(self):
        import py_compile

        module = self.write_source("scripts/module.py", b"value = 1\n")
        first = self.run_sync(apply=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        py_compile.compile(str(module), doraise=True)
        installed_module = self.destination / "example/scripts/module.py"
        py_compile.compile(str(installed_module), doraise=True)
        source_cache = next((module.parent / "__pycache__").glob("module.*.pyc"))
        destination_cache = next(
            (installed_module.parent / "__pycache__").glob("module.*.pyc")
        )
        self.assertNotEqual(source_cache.read_bytes(), destination_cache.read_bytes())
        self.write_source("scripts/module.pyc", b"source loose cache")
        self.write_destination("scripts/module.pyc", b"destination loose cache")

        second = self.run_sync()

        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("conflict=0", second.stdout)
        self.assertEqual(
            (self.destination / "example/scripts/module.pyc").read_bytes(),
            b"destination loose cache",
        )
        self.assertNotIn("example/scripts/module.pyc", self.read_manifest()["files"])


if __name__ == "__main__":
    unittest.main()
