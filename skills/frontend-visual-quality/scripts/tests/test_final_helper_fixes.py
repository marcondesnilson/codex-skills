"""Regression fixtures for current acceptance, image decoding and direction authority."""

import io
import json
import os
import struct
import unittest
from unittest.mock import patch
import zlib

from PIL import Image

import test_integration_regressions as integration
import test_visual_review as fixtures
import acceptance_gate as gate
import design_operations as design
import visual_review as review
from api_transport import ApiResponse
from review_evidence import register_criteria


def invalid_png():
    data = fixtures.png_bytes()
    length = int.from_bytes(data[33:37], "big")
    chunk = b"IDATnot a zlib stream"
    return data[:33] + struct.pack(">I", len(chunk) - 4) + chunk + struct.pack(">I", zlib.crc32(chunk)) + data[45 + length:]


def invalid_jpeg():
    return bytes.fromhex("ffd8 ffc00011080002000203011100021100031100 ffd9")


class FinalHelperTests(unittest.TestCase):
    setUp = integration.EvidenceRegressionTests.setUp
    file = integration.EvidenceRegressionTests.file
    criterion = staticmethod(integration.EvidenceRegressionTests.criterion)
    criteria = integration.EvidenceRegressionTests.criteria
    batch = integration.EvidenceRegressionTests.batch
    accept = integration.EvidenceRegressionTests.accept
    record_build = integration.EvidenceRegressionTests.record_build
    adopt = integration.EvidenceRegressionTests.adopt

    def acceptance_snapshot(self, phase, expected):
        manifest, state, _ = review.read_task(self.task)
        report = (self.task / "report.md").read_text()
        overall_line = next((line for line in report.splitlines() if line.startswith("Result:")), None)
        status = review.task_status(self.task)
        values = {
            "phase": phase, "manifest": manifest.get("overall_conclusion"),
            "manifest_conclusion": (manifest.get("conclusion") or {}).get("result"),
            "state_conclusion": (state.get("conclusion") or {}).get("result"),
            "report": overall_line, "status": status.get("acceptance"),
        }
        if os.environ.get("QA_FIXTURE_PROOF"):
            print(json.dumps(values, sort_keys=True))
        self.assertEqual(values["manifest"], expected)
        self.assertEqual(values["status"]["valid"], expected != "pending_revalidation")
        self.assertEqual(values["status"]["result"], expected)
        self.assertEqual(overall_line, f"Result: **{expected}**")
        outcome = None if expected == "pending_revalidation" else expected
        self.assertEqual(values["manifest_conclusion"], outcome)
        self.assertEqual(values["state_conclusion"], outcome)

    def test_current_acceptance_clears_on_check_failure(self):
        self.accept(self.batch(self.home))
        gate.record_check(self.task, "unit-check", "FAIL", self.evidence, "Fixture failure")
        self.acceptance_snapshot("check changed before finalization", "pending_revalidation")
        self.assertEqual(gate.finalize_task(self.task)["result"], "FAIL")
        self.acceptance_snapshot("check changed after finalization", "FAIL")

    def test_current_acceptance_clears_on_build_matrix_direction_and_review(self):
        self.adopt(1)
        self.record_build(1)
        self.accept(self.batch(self.home))
        self.acceptance_snapshot("initial finalization", "PASS")
        self.record_build(2)
        self.acceptance_snapshot("new build", "pending_revalidation")
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.acceptance_snapshot("new build finalized", "BLOCKED")
        self.accept(self.batch(self.home, cycle=2, reevaluate=True, pixel=24))
        changed = {**self.home, "description": "Check the current synthetic spacing"}
        register_criteria(self.task, self.criteria(changed), "Fixture matrix updated explicitly.")
        self.acceptance_snapshot("new matrix", "pending_revalidation")
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.acceptance_snapshot("new matrix finalized", "BLOCKED")
        self.accept(self.batch(changed, cycle=2, reevaluate=True, pixel=24))
        self.adopt(2)
        self.acceptance_snapshot("new direction", "pending_revalidation")
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.acceptance_snapshot("new direction finalized", "BLOCKED")

    def test_review_invalidates_acceptance_before_transport(self):
        self.accept(self.batch(self.home))
        original = self.hits
        class ObservedCalls(list):
            def append(_, payload):
                self.acceptance_snapshot("before review transport", "pending_revalidation")
                original.append(payload)
        self.hits = ObservedCalls()
        self.batch(self.home, outcome="not_evaluable", reevaluate=True, pixel=42)
        self.assertEqual(len(original), 2)
        self.assertEqual(gate.finalize_task(self.task)["result"], "BLOCKED")
        self.acceptance_snapshot("review finalized", "BLOCKED")

    def test_interrupted_evidence_write_leaves_pending_publication(self):
        self.accept(self.batch(self.home))
        original = gate.write_json
        def interrupt(path, data):
            if path.name == "state.json":
                raise OSError("Synthetic interruption before the new check is durable")
            return original(path, data)
        with patch.object(gate, "write_json", side_effect=interrupt):
            with self.assertRaises(OSError):
                gate.record_check(self.task, "unit-check", "FAIL", self.evidence, "Fixture failure")
        manifest, state, _ = review.read_task(self.task)
        report = (self.task / "report.md").read_text()
        validity = review.task_status(self.task)["acceptance"]
        if os.environ.get("QA_FIXTURE_PROOF"):
            print(json.dumps({"phase": "interrupted before state commit",
                              "manifest": manifest["overall_conclusion"],
                              "state_uncommitted_previous_result": state["conclusion"]["result"],
                              "report": report.splitlines()[2], "status": validity}, sort_keys=True))
        self.assertEqual(state["check_results"]["unit-check"]["status"], "PASS")
        self.assertEqual(manifest["overall_conclusion"], "pending_revalidation")
        self.assertNotIn("conclusion", manifest)
        self.assertNotIn("Result: **PASS**", report)
        self.assertFalse(validity["valid"])

    def test_interrupted_final_report_publication_is_pending(self):
        self.accept(self.batch(self.home))
        original = gate.atomic_write
        def interrupt(path, payload):
            if b"Result: **PASS**" in payload:
                raise OSError("Synthetic interruption before final report publication")
            return original(path, payload)
        with patch.object(gate, "atomic_write", side_effect=interrupt):
            with self.assertRaises(OSError):
                gate.finalize_task(self.task)
        self.assertEqual(review.task_status(self.task)["acceptance"]["result"], "pending_revalidation")
        self.assertEqual(gate.finalize_task(self.task)["result"], "PASS")

    def image_configuration(self):
        config = self.auth["operations"]["design_direction"]
        image = {**config, "service_tier": "standard", "max_output_tokens": None,
                 "identity_replacement_authorized": False,
                 "image_options": {"sizes": ["1024x1024"], "qualities": ["medium"], "formats": ["png"],
                                   "backgrounds": ["opaque"], "max_input_assets": 1, "max_output_bytes": 1048576}}
        image["model_capabilities"] = {**config["model_capabilities"], "output_modalities": ["image"], "image_generation": True}
        auth = {**self.auth, "allowed_asset_ids": ["fixture"],
                "operations": {**self.auth["operations"], "image_assets": image}}
        review.write_json(self.task / "authorization.json", auth)

    def run_image_operation(self, action, data):
        self.image_configuration()
        brief = self.project / "brief.md"
        brief.write_text("Synthetic fixture brief.")
        image = self.project / "fixture.png"
        image.write_bytes(data)
        capture_path = self.project / "captures.json"
        assets = self.project / "assets.json"
        review.write_json(assets, {"assets": [{"id": "fixture", "path": str(image), "kind": "example"}]})
        def transport(*_):
            self.hits.append(action)
            return ApiResponse(400, b"{}", "req-synthetic")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            if action == "edit":
                return design.run_image_assets(self.task, action="edit", prompt="Fixture", purpose="Fixture",
                                               size="1024x1024", quality="medium", output_format="png",
                                               background="opaque", assets_path=assets, transport=transport)
            if action == "direction":
                return design.run_design_direction(self.task, brief, identity_status="missing", assets_path=assets,
                                                   transport=transport)
            review.write_json(capture_path, {"captures": [{
                "id": "result-home-desktop", "path": str(image), "role": "result", "user_selected_target": False,
                "screen_id": "home", "viewport": "800x600", "theme": "dark", "state": "default",
                "content_id": "synthetic", "capture_tool": "fixture", "platform": "desktop",
                "environment": "isolated", "device_or_window": "fixture", "build_fingerprint": self.build,
            }]})
            return review.review_task(self.task, "creation", 1, brief, self.criteria(self.home),
                                      capture_path, transport=transport)

    def capture_rejection(self, action, data, pattern="decoded"):
        with self.assertRaises(review.ReviewError) as error:
            self.run_image_operation(action, data)
        status = review.task_status(self.task)
        values = {"operation": action, "stub_calls": len(self.hits),
                  "attempts": status["calls_attempted"], "reserved_or_committed": status["budget_committed_usd"]}
        if os.environ.get("QA_FIXTURE_PROOF"):
            print(json.dumps(values, sort_keys=True))
        self.assertEqual(list(values.values())[1:], [0, 0, 0])
        self.assertRegex(str(error.exception), pattern)

    def test_invalid_png_edit_never_reserves_or_sends(self):
        self.assertEqual(review.read_png(invalid_png()), (2, 2))
        self.capture_rejection("edit", invalid_png())

    def test_invalid_jpeg_direction_never_reserves_or_sends(self):
        self.assertEqual(review.read_jpeg(invalid_jpeg()), (2, 2))
        self.capture_rejection("direction", invalid_jpeg())

    def test_invalid_png_review_never_reserves_or_sends(self):
        self.capture_rejection("review", invalid_png())

    def test_missing_pillow_never_reserves_or_sends(self):
        with patch.dict("sys.modules", {"PIL": None}):
            self.capture_rejection("edit", fixtures.png_bytes(), pattern="requires Pillow")

    def test_valid_jpeg_keeps_original_bytes(self):
        data = io.BytesIO()
        Image.new("RGB", (12, 9)).save(data, format="JPEG")
        path = self.project / "valid.jpg"
        path.write_bytes(data.getvalue())
        config = self.auth["operations"]["design_direction"]
        result = review.read_capture(str(path), self.auth["limits"], config["pricing"])
        self.assertEqual(result["bytes"], data.getvalue())
        self.assertEqual((result["width"], result["height"]), (12, 9))

    def decision(self, task, actor, action, source):
        folder = task / "directions/proposals"
        folder.mkdir(parents=True)
        content = {"tokens": {"space": 8}}
        review.write_json(folder / "operation-001.json", {
            "content": content, "sources": [{"source_id": source}],
            "status": "proposed_not_adopted", "result_sha256": review.digest_bytes(review.canonical_json(content)),
        })
        return self.file(f"{actor}.json", {"decision": action, "actor": actor,
                         "reason": "Synthetic fixture decision", "change_note": "Fixture audit trail"})

    def test_same_visual_content_keeps_current_acceptance(self):
        first = self.decision(self.task, "fixture-initial", "adopted_within_task_scope", "initial")
        design.adopt_direction(self.task, "operation-001", first)
        self.record_build(1)
        self.accept(self.batch(self.home))
        proposal = self.task / "directions/proposals/operation-001.json"
        original = review.read_json(proposal)
        next_proposal = {key: value for key, value in original.items() if key != "decision"}
        next_proposal.update(status="proposed_not_adopted", sources=[{"source_id": "new-source"}])
        review.write_json(proposal.with_name("operation-002.json"), next_proposal)
        approval = self.file("approval.json", {"decision": "approved_by_user", "actor": "fixture-owner",
                             "reason": "Synthetic approval reason", "change_note": "Synthetic authority change"})
        design.adopt_direction(self.task, "operation-002", approval)
        self.acceptance_snapshot("authority changed with identical pixels", "PASS")
        self.assertEqual(gate.finalize_task(self.task)["result"], "PASS")

    def project_task(self, identifier):
        return review.init_task(identifier, "demo", "project direction fixture", self.task.parent, project_root=self.project)

    def test_project_inherits_new_approval_for_identical_content(self):
        a = self.project_task("task-a")
        decision = self.decision(a, "fixture-a", "adopted_within_task_scope", "source-a")
        design.adopt_direction(a, "operation-001", decision)
        b, stale = self.project_task("task-b"), self.project_task("task-stale")
        approval = self.decision(b, "fixture-b", "approved_by_user", "source-b")
        first = design.adopt_direction(b, "operation-001", approval)
        c = self.project_task("task-c")
        manifest, _, _ = review.read_task(c)
        latest = manifest["adopted_visual_direction"]
        if os.environ.get("QA_FIXTURE_PROOF"):
            print(json.dumps({"inherited_by": "task-c", "decision": latest}, sort_keys=True))
        self.assertEqual(latest["origin_task_id"], "task-b")
        self.assertEqual(latest["actor"], "fixture-b")
        self.assertEqual(latest["sources"], [{"source_id": "source-b"}])
        self.assertTrue(latest["approved_by_user"])
        self.assertEqual(latest["project_version"], 2)
        self.assertEqual(design.adopt_direction(b, "operation-001", approval), first)
        self.assertEqual(len(review.read_task(b)[1]["visual_direction_history"]), 1)
        old = self.decision(stale, "fixture-stale", "adopted_within_task_scope", "source-stale")
        with self.assertRaisesRegex(review.ReviewError, "changed in another task"):
            design.adopt_direction(stale, "operation-001", old)
        history_file, = (self.task.parent / "_project-directions").glob("*/direction.json")
        history = review.read_json(history_file)
        self.assertEqual([row["origin_task_id"] for row in history], ["task-a", "task-b"])
        self.assertEqual(len({row["decision_sha256"] for row in history}), 2)
        self.assertEqual(len({row["proposal_sha256"] for row in history}), 2)
        self.assertEqual(len({row["content_sha256"] for row in history}), 1)
        if os.environ.get("QA_FIXTURE_PROOF"):
            print(json.dumps({"history": history, "idempotent": True, "stale_conflict": True}, sort_keys=True))
