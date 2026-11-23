"""Offline regressions for versioned visual evidence and accounting."""

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_visual_review as fixtures
from api_transport import ApiResponse
import acceptance_gate as gate
from cost_accounting import attempt_budget_cost, record_usage_cost, model_matches
import design_operations as design
from project_identity import media_kit
from review_evidence import direction_hash, register_criteria
import visual_review as review


class EvidenceRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.brief = self.file("brief.md", "Offline Qt fixture")
        self.auth = fixtures.VisualReviewTests.v2_visual_authorization(self, "native")
        self.auth["allowed_capture_ids"].append("settings")
        self.auth["limits"]["max_captures_or_pairs"] = 1
        self.auth["operations"]["visual_review"]["max_calls"] = 3
        self.auth["operations"]["design_direction"] = {
            **self.auth["operations"]["visual_review"], "max_calls": 1,
        }
        self.auth["operations"]["visual_reevaluation"]["max_calls"] = 2
        self.plan = self.file("plan.json", {
            "schema_version": 1, "frontend_impact": True, "components": ["Qt"],
            "checks": [{"id": "unit-check", "category": "UNIT", "required": True, "description": "Fixture"}],
        })
        self.task = review.init_task("native", "demo", "route /", self.root / "private",
                                     self.file("auth.json", self.auth), self.plan, True, self.project)
        self.evidence = self.task / "codex.md"
        self.evidence.write_text("Fixture inspection")
        self.home = self.criterion("home", "result-home-desktop")
        self.settings = self.criterion("settings", "settings")
        self.hits = []
        self.record_build(1)

    def file(self, path, value):
        target = self.root / path
        target.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return target

    @staticmethod
    def criterion(screen, capture):
        return {"id": screen, "description": "Check hierarchy", "coverage": [{
            "id": screen, "screen": screen, "region": "title", "state": "default",
            "platform": "desktop", "required_capture_ids": [capture],
        }]}

    def record_build(self, number):
        manifest, _, _ = review.read_task(self.task)
        value = {name: review.digest_bytes(str(number).encode()) for name in (
            "source_sha256", "configuration_sha256", "visual_direction_sha256", "assets_sha256",
        )}
        value.update(served_version=str(number), build_id=f"native-{number}")
        value["visual_direction_sha256"] = direction_hash(manifest) or value["visual_direction_sha256"]
        self.build = gate.record_build_context(self.task, self.file("build.json", value))["build_fingerprint"]
        gate.record_check(self.task, "unit-check", "PASS", self.evidence, "Fixture suite")

    def criteria(self, *criteria):
        return self.file("criteria.json", {"criteria": criteria})

    def batch(self, criterion, *, outcome="evaluated", cycle=1, reevaluate=False, pixel=12, dry=None):
        row = criterion["coverage"][0]
        identifier = row["required_capture_ids"][0]
        screenshot = self.project / f"{identifier}.png"
        screenshot.write_bytes(fixtures.png_bytes(pixel=pixel))
        captures = self.file("captures.json", {"captures": [{
            "id": identifier, "path": str(screenshot), "role": "result", "user_selected_target": False,
            "screen_id": row["screen"], "viewport": "800x600", "theme": "dark", "state": "default",
            "content_id": "synthetic", "capture_tool": "Qt fixture", "platform": "desktop",
            "environment": "isolated", "device_or_window": "Qt window", "scale_factor": 1,
            "build_fingerprint": self.build,
        }]})
        observation = {"mode": "creation", "findings": [], "limitations": [], "criteria": [{
            "criterion_id": criterion["id"], "coverage_id": row["id"], "status": outcome,
            "assessment": "meets" if outcome == "evaluated" else "not_evaluable",
            "evidence": "Synthetic observation", "evidence_capture_ids": [identifier] if outcome == "evaluated" else [],
        }]}
        def transport(payload, *_):
            self.hits.append(payload)
            response = json.loads(fixtures.response_bytes(observation, status=outcome if outcome == "incomplete" else "completed"))
            response["model"] = "model-fixture"
            return ApiResponse(200, json.dumps(response).encode(), f"req-{len(self.hits)}")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            result = review.review_task(
                self.task, "creation", cycle, self.brief, self.criteria(criterion), captures,
                dry_run=dry is not None, synthetic_config=dry, transport=transport, batch_id=row["screen"],
                review_kind="reevaluation" if reevaluate else "visual",
                progress_note="Corrected the rendered fixture" if cycle > 1 else "",
                reevaluation_reason="Review corrected native evidence" if reevaluate else "",
            )
        return result.get("call_id", result)

    def accept(self, call):
        gate.record_check(self.task, "external_visual_review", "PASS", self.evidence, "Inspected current batches", call)
        self.assertEqual(gate.finalize_task(self.task)["result"], "PASS")

    def adopt(self, number):
        proposal = f"operation-{number:03d}"
        folder = self.task / "directions/proposals"
        folder.mkdir(parents=True, exist_ok=True)
        content = {"tokens": {"space": number}, "sources": ["existing Qt fixture tokens"]}
        review.write_json(folder / f"{proposal}.json", {
            "content": content, "status": "proposed_not_adopted",
            "result_sha256": review.digest_bytes(review.canonical_json(content)),
        })
        design.adopt_direction(self.task, proposal, self.file("adopt.json", {
            "decision": "adopted_within_task_scope", "actor": "fixture", "reason": "Use the existing project design tokens.",
            "change_note": "Update fixture spacing.",
        }))

    def test_direction_build_review_correction_and_reevaluation(self):
        self.adopt(1)
        self.record_build(1)
        self.accept(self.batch(self.home))
        self.adopt(2)
        self.assertEqual(review.read_task(self.task)[1]["build_fingerprint"], self.build)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.record_build(2)
        self.accept(self.batch(self.home, reevaluate=True, cycle=2, pixel=91))
        self.assertEqual(json.loads(self.hits[-1]["input"][1]["content"][0]["text"])["accepted_visual_direction"]["content"]["tokens"], {"space": 2})

    def test_proposed_direction_through_transport_then_qa(self):
        schema = json.loads((fixtures.SKILL_ROOT / "schemas/design-direction-result.schema.json").read_text())
        proposal = {
            key: [] if spec["type"] == "array" else "Synthetic direction"
            for key, spec in schema["properties"].items()
        }
        proposal.update(proposal_status="proposal", identity_notes=["Brand kit missing."],
                        basis=[{"source_id": "brief", "source_type": "brief"}],
                        colors_and_tokens=["Use the Qt fixture palette"])
        brief = self.project / "direction.md"
        brief.write_text("Use the existing Qt fixture palette.")
        def transport(*_):
            response = json.loads(fixtures.response_bytes(proposal))
            response["model"] = "model-fixture"
            return ApiResponse(200, json.dumps(response).encode(), "req-direction")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            result = design.run_design_direction(self.task, brief, identity_status="missing", transport=transport)
        design.adopt_direction(self.task, result["call_id"], self.file("decision.json", {
            "decision": "adopted_within_task_scope", "actor": "fixture", "reason": "Keep the existing Qt palette.",
            "change_note": "First fixture adoption.",
        }))
        self.record_build(2)
        self.accept(self.batch(self.home))
        self.record_build(3)
        self.accept(self.batch(self.home, cycle=2, reevaluate=True, pixel=91))
        manifest, _, _ = review.read_task(self.task)
        self.assertEqual(manifest["adopted_visual_direction"]["sources"][0]["source_id"], "brief")

    def test_later_not_evaluable_and_incomplete_override_older_pass(self):
        self.accept(self.batch(self.home))
        self.batch(self.home, reevaluate=True, outcome="not_evaluable", pixel=21)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        with self.assertRaisesRegex(review.ReviewError, "incomplete"):
            self.batch(self.home, reevaluate=True, outcome="incomplete", pixel=31)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        gate.record_check(self.task, "unit-check", "FAIL", self.evidence, "Confirmed failure")
        self.assertEqual(gate.finalize_task(self.task)["result"], "FAIL")

    def test_multi_batch_preserves_pending_rows_then_consolidates(self):
        register_criteria(self.task, self.criteria(self.home, self.settings))
        self.batch(self.settings, outcome="not_evaluable")
        home = self.batch(self.home)
        with self.assertRaisesRegex(review.ReviewError, "coverage"):
            self.accept(home)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.accept(self.batch(self.settings, reevaluate=True, pixel=21))
        self.assertEqual(review.read_task(self.task)[1]["visual_cycles_completed"], 1)

    def test_explicit_matrix_change_rechecks_same_pixels_without_counting_correction(self):
        register_criteria(self.task, self.criteria(self.home))
        self.accept(self.batch(self.home))
        changed = {**self.home, "description": "Compare heading and action hierarchy"}
        with self.assertRaisesRegex(review.ReviewError, "explicit decision"):
            register_criteria(self.task, self.criteria(changed))
        register_criteria(self.task, self.criteria(changed), "Use the approved heading hierarchy criterion.")
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.accept(self.batch(changed, reevaluate=True))
        state = review.read_task(self.task)[1]
        self.assertEqual(state["visual_cycles_completed"], 1)
        self.assertEqual([matrix["version"] for matrix in state["visual_matrix_history"]], [1, 2])

    def test_insufficient_budget_keeps_unreviewed_batch_pending(self):
        register_criteria(self.task, self.criteria(self.home, self.settings))
        self.batch(self.home)
        auth_path = self.task / "authorization.json"
        auth = review.read_json(auth_path)
        auth["max_estimated_cost_usd"] = 0.000001
        review.write_json(auth_path, auth)
        with self.assertRaisesRegex(review.ReviewError, "remaining task budget"):
            self.batch(self.settings)
        state = review.read_task(self.task)[1]
        self.assertEqual(len(self.hits), 1)
        self.assertEqual(state["visual_matrix"]["version"], 1)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")

    def test_individual_evidence_corruption_and_removal_block(self):
        call = self.batch(self.home)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.accept(call)
        attempt = review.read_task(self.task)[1]["attempts"][0]
        for entry in [attempt["captures"][0], attempt["review_artifact"], attempt["context_artifact"]]:
            path = self.task / entry["file"]
            original = path.read_bytes()
            for modified in [True, False]:
                with self.subTest(path=path.name, modified=modified):
                    if modified:
                        path.write_bytes(original + b"x")
                    else:
                        path.unlink()
                    self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
                    path.write_bytes(original)
        self.record_build(2)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")

    def test_project_direction_reused_with_sources_and_isolated(self):
        (self.project / "Media Kit").mkdir()
        self.assertEqual(media_kit(self.project), self.project / "Media Kit")
        self.adopt(1)
        other = self.root / "other"
        other.mkdir()
        for name, path, expected in (("next", self.project, True), ("separate", other, False)):
            task = review.init_task(name, "demo", "new scope", self.task.parent, project_root=path)
            manifest, _, _ = review.read_task(task)
            self.assertEqual(bool(direction_hash(manifest)), expected)
            if expected:
                context = design._operation_context(task, manifest, {}, None)
                self.assertEqual(context["source_manifest"][0]["sha256"], direction_hash(manifest))
                self.assertEqual(context["adopted_visual_direction"]["content"]["sources"], ["existing Qt fixture tokens"])

    def test_synthetic_review_dry_run_does_not_spend(self):
        pricing = self.auth["operations"]["visual_review"]["pricing"]
        self.task = review.init_task("native-dry", "demo", "route /", self.root / "private", acceptance_plan_file=self.plan, project_root=self.project)
        self.evidence = self.task / "codex.md"
        self.evidence.write_text("Synthetic QA evidence")
        self.record_build(1)
        before = (self.task / "state.json").read_bytes()
        result = self.batch(self.home, dry={
            "synthetic": True, "operation": "visual_review", "model": "offline-review",
            "service_tier": "default", "max_output_tokens": 512, "pricing": pricing,
            "allowed_asset_ids": [], "image_options": None, "identity_replacement_authorized": False,
        })
        self.assertTrue(result["payload_constructed"])
        self.assertFalse(result["api_called"])
        self.assertEqual(review.read_task(self.task)[1]["attempts"], [])
        self.assertFalse(self.hits)
        self.assertEqual((self.task / "state.json").read_bytes(), before)


class CostAndBoundaryTests(unittest.TestCase):
    def test_missing_modality_and_final_reconciliation(self):
        attempt = {"consumption_status": "reported_usage", "reserved_cost_usd": 0.0001,
                   "fallback_image_input_tokens": 10000, "pricing_snapshot": {
                       "input_usd_per_million": 1, "image_input_usd_per_million": 5, "output_usd_per_million": 1,
                   }}
        record_usage_cost(attempt, {"input_tokens": 100, "output_tokens": 10})
        self.assertNotIn("cost_calculated_from_reported_usage_usd", attempt)
        self.assertEqual(str(attempt_budget_cost(attempt)), "0.00051")
        for amount in [0.00002, 0.005]:
            settled = {**attempt, "consumption_status": "reconciled_charged", "reported_cost_usd": amount}
            self.assertAlmostEqual(float(attempt_budget_cost(settled)), amount)

    def test_acceptance_runtime_and_schema_share_ids_and_categories(self):
        schema = json.loads((fixtures.SKILL_ROOT / "schemas/acceptance-plan.schema.json").read_text())
        plan = {"schema_version": 1, "frontend_impact": False, "components": ["Qt"], "checks": []}
        for identifier, category, valid in [("run-qa", "RUNTIME", True), ("Bad ID", "UNIT", False),
                                             ("external_visual_review", "VISUAL", False), ("unit", "OTHER", False)]:
            plan["checks"] = [{"id": identifier, "category": category, "required": True, "description": "Fixture"}]
            for validator in [gate.validate_acceptance_plan, lambda value: review.validate_json_schema_subset(value, schema)]:
                if valid:
                    validator(plan)
                else:
                    with self.assertRaises(review.ReviewError):
                        validator(plan)

    def test_selected_asset_total_limits_and_low_detail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assets = []
            for label in ("one", "two"):
                path = root / f"{label}.png"
                path.write_bytes(fixtures.png_bytes())
                assets.append({"id": label, "path": str(path), "kind": "example"})
            manifest = root / "assets.json"
            review.write_json(manifest, {"assets": assets})
            limits = {**review.HARD_LIMITS, "max_aggregate_pixels": 7}
            auth = {"allowed_asset_ids": ["one", "two"], "limits": limits}
            with self.assertRaisesRegex(review.ReviewError, "Aggregate asset pixels"):
                design._selected_assets(manifest, auth, 3, str(root))
            limits["max_aggregate_pixels"] = 8
            limits["max_aggregate_bytes"] = len(fixtures.png_bytes()) * 2 - 1
            with self.assertRaisesRegex(review.ReviewError, "Aggregate asset bytes"):
                design._selected_assets(manifest, auth, 3, str(root))
            limits["max_aggregate_bytes"] += 1
            assets = design._selected_assets(manifest, auth, 3, str(root))
            self.assertEqual(design._image_message(assets[0], "low")["detail"], "low")

    def test_alias_is_explicit_and_truncated_image_is_rejected(self):
        config = {"model": "fixture", "model_capabilities": {"equivalent_models": ["fixture-snapshot"]}}
        self.assertTrue(model_matches(config, "fixture-snapshot"))
        self.assertFalse(model_matches(config, "fixture-other"))
        with self.assertRaisesRegex(review.ReviewError, "decoded"):
            design._image_result({"data": [{"b64_json": "iVBORw0KGgo="}]},
                                 {"format": "png", "size": "auto"}, {"image_options": {"max_output_bytes": 100}})


if __name__ == "__main__":
    unittest.main()
