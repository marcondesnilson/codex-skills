"""Offline tests for the QA acceptance gate and served-build evidence."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import acceptance_gate as gate  # noqa: E402
import visual_review as review  # noqa: E402


class AcceptanceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, *, frontend=False, checks=None):
        return {
            "schema_version": 1,
            "frontend_impact": frontend,
            "components": ["synthetic component"],
            "checks": checks or [
                {"id": "unit-check", "category": "UNIT", "required": True, "description": "Run the local unit fixtures."},
            ],
        }

    def create_task(self, task_id="qa-fixture", *, frontend=False, checks=None, api=False):
        plan_path = self.root / f"{task_id}-plan.json"
        plan_path.write_text(json.dumps(self.plan(frontend=frontend, checks=checks)), encoding="utf-8")
        auth_path = None
        if api:
            raise AssertionError("This suite tests acceptance without task API authorization.")
        return review.init_task(
            task_id, "fixture", "synthetic task scope", self.root / "tasks", acceptance_plan_file=plan_path,
        )

    def evidence(self, task, name, content="offline evidence\n"):
        path = task / "evidence" / f"{name}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def record(self, task, check_id, status="PASS", content="offline evidence\n"):
        path = self.evidence(task, check_id, content)
        return gate.record_check(task, check_id, status, path, f"Synthetic fixture evidence for {check_id}.")

    def test_backend_only_plan_passes_without_visual_configuration_or_api(self):
        task = self.create_task("backend-only")
        manifest, _, _ = review.read_task(task)
        self.assertFalse(manifest["review_required"])
        self.assertFalse(manifest["api_execution_authorized"])
        self.record(task, "unit-check")

        conclusion = gate.finalize_task(task)

        self.assertEqual(conclusion["result"], "PASS")
        self.assertFalse(conclusion["review_required"])
        self.assertFalse(conclusion["api_execution_authorized"])

    def test_acceptance_plan_rejects_non_string_check_category_cleanly(self):
        with self.assertRaisesRegex(review.ReviewError, "invalid category"):
            gate.validate_acceptance_plan(self.plan(checks=[{
                "id": "unit-check", "category": [], "required": True, "description": "Malformed fixture category.",
            }]))

    def test_frontend_impact_requires_visual_review_even_without_api_permission(self):
        task = self.create_task("frontend-blocked", frontend=True)
        manifest, _, _ = review.read_task(task)
        self.assertTrue(manifest["review_required"])
        self.assertFalse(manifest["api_execution_authorized"])
        self.record(task, "unit-check")

        conclusion = gate.finalize_task(task)

        self.assertEqual(conclusion["result"], "BLOCKED")
        self.assertTrue(any("External visual review is required" in item for item in conclusion["pending"]))

    def test_missing_required_test_is_blocked_and_cannot_be_a_warning(self):
        task = self.create_task("missing-test")
        conclusion = gate.finalize_task(task)
        self.assertEqual(conclusion["result"], "BLOCKED")
        self.assertTrue(any("unit-check has no recorded evidence" in item for item in conclusion["pending"]))
        with self.assertRaisesRegex(review.ReviewError, "required check cannot be downgraded"):
            self.record(task, "unit-check", "PASS WITH WARNINGS")

    def test_failure_precedes_blocked_and_warning_results(self):
        task = self.create_task("precedence", checks=[
            {"id": "failed-check", "category": "UNIT", "required": True, "description": "Fixture failure."},
            {"id": "warning-check", "category": "STATIC", "required": False, "description": "Optional warning."},
            {"id": "missing-check", "category": "FEATURE", "required": True, "description": "Intentionally missing."},
        ])
        self.record(task, "failed-check", "FAIL")
        self.record(task, "warning-check", "PASS WITH WARNINGS")

        conclusion = gate.finalize_task(task)

        self.assertEqual(conclusion["result"], "FAIL")

    def test_modified_evidence_and_changed_served_build_are_stale(self):
        task = self.create_task("stale-build")
        evidence = self.evidence(task, "unit-check")
        gate.record_check(task, "unit-check", "PASS", evidence, "First synthetic build check.")
        context = {
            "served_version": "fixture-v1",
            "build_id": "offline-build-1",
            "source_sha256": hashlib.sha256(b"source").hexdigest(),
            "configuration_sha256": hashlib.sha256(b"config").hexdigest(),
            "visual_direction_sha256": hashlib.sha256(b"direction").hexdigest(),
            "assets_sha256": hashlib.sha256(b"assets").hexdigest(),
        }
        build_file = self.root / "build.json"
        build_file.write_text(json.dumps(context), encoding="utf-8")
        gate.record_build_context(task, build_file)

        self.assertEqual(gate.finalize_task(task)["result"], "BLOCKED")
        manifest, state, _ = review.read_task(task)
        self.assertEqual(manifest["build_fingerprint"], state["build_fingerprint"])

        evidence.write_text("changed after recording\n", encoding="utf-8")
        self.assertEqual(gate.finalize_task(task)["result"], "BLOCKED")

    def test_frontend_visual_gate_requires_complete_coverage_and_same_build(self):
        task = self.create_task("visual-coverage", frontend=True)
        context = {
            "served_version": "fixture-v1", "build_id": "offline-build",
            "source_sha256": hashlib.sha256(b"src").hexdigest(),
            "configuration_sha256": hashlib.sha256(b"cfg").hexdigest(),
            "visual_direction_sha256": hashlib.sha256(b"dir").hexdigest(),
            "assets_sha256": hashlib.sha256(b"asset").hexdigest(),
        }
        build_file = self.root / "visual-build.json"
        build_file.write_text(json.dumps(context), encoding="utf-8")
        build = gate.record_build_context(task, build_file)
        self.record(task, "unit-check")
        manifest, state, _ = review.read_task(task)
        manifest["api_execution_authorized"] = True
        review.write_json(task / "manifest.json", manifest)
        state["attempts"].append({
            "call_id": "fixture-review-001", "operation": "visual_review", "review_kind": "visual",
            "status": "completed", "build_fingerprint": build["build_fingerprint"],
            "coverage_complete": False,
            "coverage_matrix": [{"status": "not_evaluable", "evidence_capture_ids": []}],
        })
        review.write_json(task / "state.json", state)

        conclusion = gate.finalize_task(task)

        self.assertEqual(conclusion["result"], "BLOCKED")
        self.assertTrue(any("complete criterion-to-screen coverage" in item for item in conclusion["pending"]))

    def test_final_conclusion_is_derived_and_written_consistently(self):
        task = self.create_task("consistent-final")
        self.record(task, "unit-check")
        conclusion = gate.finalize_task(task)
        manifest, state, _ = review.read_task(task)
        self.assertEqual(manifest["conclusion"], state["conclusion"])
        self.assertEqual(manifest["overall_conclusion"], conclusion["result"])
        self.assertIn("does not prove a live API call", (task / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
