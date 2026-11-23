"""Offline-only tests. Every API request uses an injected fixture transport."""

import contextlib
from datetime import date
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import visual_review as review  # noqa: E402
import acceptance_gate as gate  # noqa: E402
from api_transport import ApiResponse  # noqa: E402


def png_bytes(width=2, height=2, pixel=11):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes((pixel, 0, 0)) * width for _ in range(height))
    return signature + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def valid_result(mode="creation", finding=True):
    return {
        "mode": mode,
        "criteria": [{
            "criterion_id": "hero-hierarchy",
            "coverage_id": "hero-desktop-default",
            "status": "evaluated",
            "assessment": "gap" if finding else "meets",
            "evidence": "The heading competes with the secondary action in this test fixture.",
            "evidence_capture_ids": ["result-home-desktop"],
        }],
        "findings": ([{
            "id": "F-1",
            "severity": "medium",
            "screenshot_id": "result-home-desktop",
            "region": "hero heading",
            "evidence": "Test fixture observation only.",
            "recommendation": "Review the hierarchy against the accepted brief.",
        }] if finding else []),
        "limitations": ["Offline test fixture; not a real visual review."],
    }


def response_bytes(result=None, status="completed", usage=True, refusal=False, incomplete=None):
    output_content = []
    if refusal:
        output_content.append({"type": "refusal", "refusal": "Fixture refusal; no review was performed."})
    elif result is not None:
        output_content.append({"type": "output_text", "text": json.dumps(result)})
    response = {
        "id": "resp_fixture_001",
        "model": "gpt-6.1-sol",
        "service_tier": "default",
        "created_at": 1794945600,
        "status": status,
        "incomplete_details": incomplete,
        "output": [{"type": "message", "content": output_content}],
    }
    if usage:
        response["usage"] = {"input_tokens": 700, "output_tokens": 100, "total_tokens": 800, "input_tokens_details": {"image_tokens": 200}}
    return json.dumps(response).encode()


def tree_snapshot(root):
    return {
        path.relative_to(root).as_posix(): ("directory" if path.is_dir() else path.read_bytes())
        for path in sorted(root.rglob("*"))
    }


class FixtureTransport:
    def __init__(self, status=200, body=None, exception=None):
        self.status = status
        self.body = body if body is not None else response_bytes(valid_result())
        self.exception = exception
        self.calls = []

    def __call__(self, payload, api_key, timeout):
        self.calls.append({"payload": payload, "api_key": api_key, "timeout": timeout})
        if self.exception:
            raise self.exception
        return ApiResponse(self.status, self.body, "req_fixture_001")


class VisualReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "inputs"
        self.source.mkdir()
        (self.source / "brief.md").write_text("Create a concise synthetic home page with one primary action.", encoding="utf-8")
        (self.source / "criteria.json").write_text(json.dumps({"criteria": [{
            "id": "hero-hierarchy",
            "description": "The title, supporting text, and main action have a clear hierarchy.",
            "coverage": [{
                "id": "hero-desktop-default", "screen": "/", "region": "hero", "state": "default",
                "platform": "web", "required_capture_ids": ["result-home-desktop"],
            }],
        }]}), encoding="utf-8")
        (self.source / "result.png").write_bytes(png_bytes())
        self.write_capture_manifest()
        self.auth_path = self.root / "auth.json"
        self.auth_path.write_text(json.dumps(self.authorization()), encoding="utf-8")
        self.task_dir = self.init_authorized_task("offline-visual-task", self.auth_path, self.root / "evidence")
        self.no_network = patch.object(review.urllib.request, "build_opener", side_effect=AssertionError("offline test attempted real network"))
        self.no_urlopen = patch.object(review.urllib.request, "urlopen", side_effect=AssertionError("offline test attempted real network"))
        self.no_network.start()
        self.no_urlopen.start()
        self.env = patch.dict(os.environ, {"OPENAI_API_KEY": "test-marker-never-a-key"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.no_urlopen.stop()
        self.no_network.stop()
        self.temp.cleanup()

    def authorization(self, task_id="offline-visual-task"):
        return {
            "authorization_id": "fixture-only-authorization",
            "task_id": task_id,
            "project": "demo",
            "scope": "route /",
            "data_policy": "Synthetic fixture image only; no customer or production data.",
            "allowed_capture_ids": ["result-home-desktop", "reference-home-desktop"],
            "model": "gpt-6.1-sol",
            "model_capabilities": {
                "source_url": "https://developers.openai.com/api/docs/models/gpt-6.1-sol",
                "verified_at": date.today().isoformat(),
                "vision_input": True,
                "structured_outputs": True,
            },
            "valid_until": "2099-01-01T00:00:00Z",
            "max_estimated_cost_usd": 1.0,
            "max_output_tokens": 512,
            "limits": {
                "max_visual_cycles": 5,
                "max_api_calls": 3,
                "max_captures_or_pairs": 3,
                "max_single_file_bytes": 8388608,
                "max_aggregate_bytes": 25165824,
                "max_image_width": 4096,
                "max_image_height": 4096,
                "max_aggregate_pixels": 48000000,
                "timeout_seconds": 90,
                "estimate_safety_factor": 1.25,
            },
            "pricing": {
                "model": "gpt-6.1-sol",
                "verified_at": date.today().isoformat(),
                "source_url": "https://developers.openai.com/api/docs/pricing",
                "input_usd_per_million": 1.0,
                "image_input_usd_per_million": 2.0,
                "output_usd_per_million": 3.0,
                "image_detail": "high",
                "image_tokens_upper_bound_per_capture": 1000,
                "image_bound_max_width": 4096,
                "image_bound_max_height": 4096,
                "image_bound_max_pixels": 16777216,
                "image_bound_source_url": "https://developers.openai.com/api/docs/guides/image-cost-calculator",
            },
        }

    def init_authorized_task(self, task_id, auth_path, evidence_root):
        plan_path = self.root / f"{task_id}-acceptance.json"
        plan_path.write_text(json.dumps({
            "schema_version": 1,
            "frontend_impact": False,
            "components": ["visual-review helper fixture"],
            "checks": [{"id": "helper-contract", "category": "UNIT", "required": True, "description": "Exercise helper contract with a fixture transport."}],
        }), encoding="utf-8")
        return review.init_task(
            task_id, "demo", "route /", evidence_root, auth_path, plan_path, api_execution_authorized=True,
        )

    def write_capture_manifest(self, path=None, *, role="result", viewport="1440x900", target=False):
        path = path or self.source / "captures.json"
        entry = {
            "id": "result-home-desktop" if role == "result" else "reference-home-desktop",
            "role": role,
            "path": str(self.source / "result.png"),
            "route": "/",
            "viewport": viewport,
            "theme": "light",
            "state": "default",
            "content_id": "home-synthetic-v1",
            "capture_tool": "offline fixture generator",
            "user_selected_target": target,
        }
        if role == "reference":
            entry.update({"pair_id": "home-desktop", "reference_target": "Fixture reference; not a real target."})
        path.write_text(json.dumps({"captures": [entry]}), encoding="utf-8")
        return path

    def args(self, mode="creation", cycle=1, captures_path=None, **kwargs):
        return (self.task_dir, mode, cycle, self.source / "brief.md", self.source / "criteria.json", captures_path or self.source / "captures.json")

    def test_dry_run_without_key_and_without_authorization_never_calls_transport(self):
        task = review.init_task("no-api-task", "demo", "route /", self.root / "dry-root")
        before = tree_snapshot(task)
        with patch.dict(os.environ, {}, clear=True):
            result = review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", dry_run=True)
        self.assertFalse(result["api_called"])
        self.assertFalse(result["writes_performed"])
        self.assertIsNone(result["estimate"])
        self.assertEqual(review.task_status(task)["calls_attempted"], 0)
        self.assertEqual(tree_snapshot(task), before)

    def test_cli_dry_run_without_key_does_not_call_real_api(self):
        task = review.init_task("cli-dry-task", "demo", "route /", self.root / "cli-dry")
        before = tree_snapshot(task)
        output = io.StringIO()
        args = [
            "review", "--task-dir", str(task), "--mode", "creation", "--cycle", "1",
            "--brief", str(self.source / "brief.md"), "--criteria", str(self.source / "criteria.json"),
            "--captures", str(self.source / "captures.json"), "--dry-run",
        ]
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(output):
            exit_code = review.main(args)
        self.assertEqual(exit_code, 0)
        self.assertIn('"api_called": false', output.getvalue())
        self.assertIn('"writes_performed": false', output.getvalue())
        self.assertEqual(review.task_status(task)["calls_attempted"], 0)
        self.assertEqual(tree_snapshot(task), before)

    def test_visual_cycles_persist_without_any_api_review(self):
        auth = self.authorization("offline-cycles-task")
        auth["limits"]["max_visual_cycles"] = 1
        auth_path = self.root / "offline-cycles-auth.json"
        auth_path.write_text(json.dumps(auth))
        task = review.init_task("offline-cycles-task", "demo", "route /", self.root / "offline-cycles", auth_path)
        recorded = review.record_visual_cycle(task, "creation", 1, "Inspecionei a captura local e registrei as áreas pertinentes.", self.source / "captures.json")
        self.assertFalse(recorded["api_called"])
        status = review.task_status(task)
        self.assertEqual(status["visual_cycles_completed"], 1)
        self.assertEqual(status["calls_attempted"], 0)
        self.assertEqual(status["api_review"], "not_executed")
        (self.source / "result.png").write_bytes(png_bytes(pixel=99))
        with self.assertRaisesRegex(review.ReviewError, "visual-cycle limit"):
            review.record_visual_cycle(task, "creation", 2, "Registrei outra inspeção visual.", self.source / "captures.json")
        self.assertEqual(review.task_status(task)["visual_cycles_completed"], 1)

    def test_live_review_uses_the_registered_cycle_without_incrementing_twice(self):
        review.record_visual_cycle(self.task_dir, "creation", 1, "Capture real registrada antes da revisão.", self.source / "captures.json")
        transport = FixtureTransport(body=response_bytes(valid_result()))
        review.review_task(*self.args(), transport=transport)
        status = review.task_status(self.task_dir)
        self.assertEqual(status["visual_cycles_completed"], 1)
        self.assertEqual(status["calls_attempted"], 1)
        self.assertEqual(len(transport.calls), 1)

    def test_live_review_blocked_without_task_authorization(self):
        task = review.init_task("no-auth-task", "demo", "route /", self.root / "no-auth")
        transport = FixtureTransport()
        with self.assertRaisesRegex(review.ReviewError, "no task-scoped authorization"):
            review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", transport=transport)
        self.assertEqual(transport.calls, [])

    def test_invalid_file_format_is_rejected_before_transport(self):
        (self.source / "invalid.png").write_bytes(b"not an image at all")
        captures = json.loads((self.source / "captures.json").read_text())
        captures["captures"][0]["path"] = str(self.source / "invalid.png")
        path = self.source / "invalid-captures.json"
        path.write_text(json.dumps(captures))
        with self.assertRaisesRegex(review.ReviewError, "Only PNG and JPEG"):
            review.review_task(*self.args(captures_path=path), dry_run=True)

    def test_input_size_limit_is_enforced(self):
        auth = self.authorization("small-limit-task")
        auth["limits"]["max_single_file_bytes"] = 16
        auth_path = self.root / "small-limit.json"
        auth_path.write_text(json.dumps(auth))
        task = review.init_task("small-limit-task", "demo", "route /", self.root / "small-limit", auth_path)
        with self.assertRaisesRegex(review.ReviewError, "per-image byte limit"):
            review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", dry_run=True)

    def test_capture_count_dimension_and_aggregate_byte_limits_are_enforced(self):
        captures = json.loads((self.source / "captures.json").read_text())
        captures["captures"] = [
            {**captures["captures"][0], "id": f"capture-{index}"}
            for index in range(4)
        ]
        path = self.source / "too-many-captures.json"
        path.write_text(json.dumps(captures))
        with self.assertRaisesRegex(review.ReviewError, "Capture count exceeds"):
            review.review_task(self.task_dir, "creation", 1, self.source / "brief.md", self.source / "criteria.json", path, dry_run=True)

        (self.source / "oversized-dimensions.png").write_bytes(png_bytes(width=4097, height=1))
        captures["captures"] = [{**captures["captures"][0], "id": "result-home-desktop", "path": str(self.source / "oversized-dimensions.png")}]
        path.write_text(json.dumps(captures))
        with self.assertRaisesRegex(review.ReviewError, "dimensions exceed"):
            review.review_task(self.task_dir, "creation", 1, self.source / "brief.md", self.source / "criteria.json", path, dry_run=True)

        auth = self.authorization("small-aggregate-task")
        auth["limits"]["max_aggregate_bytes"] = 1
        auth_path = self.root / "small-aggregate.json"
        auth_path.write_text(json.dumps(auth))
        task = review.init_task("small-aggregate-task", "demo", "route /", self.root / "small-aggregate", auth_path)
        with self.assertRaisesRegex(review.ReviewError, "Aggregate screenshot bytes"):
            review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", dry_run=True)

    def test_fidelity_requires_user_selected_reference_and_equivalent_pair(self):
        reference = {
            "id": "reference-home-desktop", "role": "reference", "pair_id": "home-desktop",
            "path": str(self.source / "result.png"), "route": "/", "viewport": "1440x900",
            "theme": "light", "state": "default", "content_id": "home-synthetic-v1",
            "capture_tool": "offline fixture", "user_selected_target": True,
            "reference_target": "A target named by the test fixture.",
        }
        result = {**reference, "id": "result-home-desktop", "role": "result", "user_selected_target": False}
        result.pop("reference_target")
        manifest = self.source / "fidelity.json"
        manifest.write_text(json.dumps({"captures": [reference, {**result, "viewport": "390x844"}]}))
        with self.assertRaisesRegex(review.ReviewError, "does not match on viewport"):
            review.review_task(self.task_dir, "fidelity", 1, self.source / "brief.md", self.source / "criteria.json", manifest, dry_run=True)

    def test_insufficient_budget_blocks_before_transport(self):
        auth = self.authorization("small-budget-task")
        auth["max_estimated_cost_usd"] = 0.00000001
        path = self.root / "small-budget.json"
        path.write_text(json.dumps(auth))
        task = self.init_authorized_task("small-budget-task", path, self.root / "small-budget")
        transport = FixtureTransport()
        with self.assertRaisesRegex(review.ReviewError, "remaining task budget"):
            review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", transport=transport)
        self.assertEqual(transport.calls, [])
        self.assertEqual(review.task_status(task)["calls_attempted"], 0)

    def test_valid_response_is_normalized_and_usage_is_separate_from_estimate(self):
        transport = FixtureTransport(body=response_bytes(valid_result()))
        result = review.review_task(*self.args(), transport=transport)
        self.assertEqual(result["result"], "review_received_for_codex_evaluation")
        self.assertEqual(result["usage_reported"]["input_tokens"], 700)
        self.assertIn("estimated_cost_usd", result["estimate"])
        self.assertEqual(transport.calls[0]["timeout"], 90)
        self.assertEqual(transport.calls[0]["payload"]["store"], False)
        self.assertEqual(transport.calls[0]["payload"]["model"], "gpt-6.1-sol")
        saved = json.loads((self.task_dir / "reviews" / "review-001.json").read_text())
        self.assertEqual(saved["reviewer_status"], "consultive_not_task_approval")
        status = review.task_status(self.task_dir)
        self.assertEqual(status["calls_attempted"], 1)
        self.assertEqual(status["attempts"][0]["usage_reported"]["output_tokens"], 100)
        self.assertIsNotNone(status["attempts"][0]["cost_calculated_from_reported_usage_usd"])

    def test_visual_reevaluation_reuses_findings_and_tracks_new_build_and_context(self):
        task_id = "visual-reevaluation-v2"
        authorization_path = self.root / "visual-v2-auth.json"
        authorization_path.write_text(json.dumps(self.v2_visual_authorization(task_id)), encoding="utf-8")
        plan_path = self.root / "visual-v2-plan.json"
        plan_path.write_text(json.dumps({
            "schema_version": 1, "frontend_impact": True, "components": ["synthetic dashboard"],
            "checks": [{"id": "unit-check", "category": "UNIT", "required": True, "description": "Offline fixtures."}],
        }), encoding="utf-8")
        task = review.init_task(
            task_id, "demo", "route /", self.root / "visual-v2-evidence", authorization_path,
            plan_path, api_execution_authorized=True,
        )
        build_path = self.root / "served-build.json"
        build = {
            "served_version": "fixture-1", "build_id": "fixture-build-1",
            "source_sha256": review.digest_bytes(b"source-1"),
            "configuration_sha256": review.digest_bytes(b"config-1"),
            "visual_direction_sha256": review.digest_bytes(b"direction-1"),
            "assets_sha256": review.digest_bytes(b"assets-1"),
        }
        build_path.write_text(json.dumps(build), encoding="utf-8")
        first_build = gate.record_build_context(task, build_path)["build_fingerprint"]
        capture_path = self.source / "versioned-captures.json"
        capture = {
            **json.loads((self.source / "captures.json").read_text(encoding="utf-8"))["captures"][0],
            "environment": "offline browser fixture", "device_or_window": "desktop 1440x900",
            "scale_factor": 1, "build_fingerprint": first_build,
        }
        capture_path.write_text(json.dumps({"captures": [capture]}), encoding="utf-8")

        class V2Transport:
            def __init__(self):
                self.calls = []

            def __call__(self, payload, api_key, timeout):
                self.calls.append(payload)
                body = json.loads(response_bytes(valid_result()))
                body.update({"id": f"resp-{len(self.calls)}", "model": "model-fixture", "service_tier": "default"})
                return ApiResponse(200, json.dumps(body).encode(), f"req-v2-{len(self.calls)}")

        transport = V2Transport()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            first = review.review_task(
                task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", capture_path,
                transport=transport,
            )
        self.assertTrue(first["api_called"])

        build.update({
            "served_version": "fixture-2", "build_id": "fixture-build-2",
            "source_sha256": review.digest_bytes(b"source-2"),
        })
        build_path.write_text(json.dumps(build), encoding="utf-8")
        second_build = gate.record_build_context(task, build_path)["build_fingerprint"]
        (self.source / "result.png").write_bytes(png_bytes(pixel=91))
        capture["build_fingerprint"] = second_build
        capture_path.write_text(json.dumps({"captures": [capture]}), encoding="utf-8")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            second = review.review_task(
                task, "creation", 2, self.source / "brief.md", self.source / "criteria.json", capture_path,
                progress_note="Updated the same desktop state after addressing F-1.",
                addressed_findings=["F-1"], review_kind="reevaluation", transport=transport,
            )
        self.assertEqual(second["review_kind"], "reevaluation")
        self.assertEqual(len(transport.calls), 2)
        context_text = transport.calls[1]["input"][1]["content"][0]["text"]
        context = json.loads(context_text)
        self.assertEqual(context["review_kind"], "reevaluation")
        self.assertEqual(context["prior_findings"][0]["id"], "F-1")
        self.assertEqual(context["captures"][0]["build_fingerprint"], second_build)
        status = review.task_status(task)
        self.assertEqual(status["attempts"][1]["operation"], "visual_reevaluation")
        self.assertEqual(status["attempts"][1]["request_id"], "req-v2-2")

    def v2_visual_authorization(self, task_id):
        today = date.today().isoformat()
        pricing = {
            "model": "model-fixture", "verified_at": today,
            "source_url": "https://developers.openai.com/api/docs/pricing", "billing_regime": "standard",
            "input_usd_per_million": 1, "image_input_usd_per_million": 2,
            "output_usd_per_million": 3, "image_output_usd_per_million": 3,
            "image_input_tokens_upper_bound_per_asset": 1000, "image_output_tokens_upper_bound": 100,
            "image_detail": "high", "image_bound_max_width": 4096,
            "image_bound_max_height": 4096, "image_bound_max_pixels": 16_777_216,
        }
        visual_config = {
            "model": "model-fixture",
            "model_capabilities": {
                "source_url": "https://developers.openai.com/api/docs/models/model-fixture",
                "verified_at": today, "input_modalities": ["text", "image"],
                "output_modalities": ["text"], "structured_outputs": True, "image_generation": False,
            },
            "service_tier": "default", "max_calls": 2, "max_output_tokens": 512, "pricing": pricing,
        }
        return {
            "schema_version": 2, "authorization_id": "visual-v2-fixture", "task_id": task_id,
            "project": "demo", "scope": "route /", "data_policy": "Synthetic screenshot fixtures only; no customer data.",
            "allowed_capture_ids": ["result-home-desktop"], "allowed_asset_ids": [],
            "valid_until": "2099-01-01T00:00:00Z", "max_estimated_cost_usd": 2.0,
            "limits": {
                "max_visual_cycles": 5, "max_api_calls": 3, "max_captures_or_pairs": 3,
                "max_single_file_bytes": 8 * 1024 * 1024, "max_aggregate_bytes": 24 * 1024 * 1024,
                "max_image_width": 4096, "max_image_height": 4096,
                "max_aggregate_pixels": 48_000_000, "timeout_seconds": 5,
                "estimate_safety_factor": 1.25,
            },
            "operations": {
                "visual_review": visual_config,
                "visual_reevaluation": {**visual_config, "max_calls": 1},
            },
        }

    def test_refusal_is_not_approved(self):
        transport = FixtureTransport(body=response_bytes(refusal=True))
        with self.assertRaisesRegex(review.ReviewError, "refused the review"):
            review.review_task(*self.args(), transport=transport)
        self.assertEqual(transport.calls.__len__(), 1)
        self.assertEqual(review.task_status(self.task_dir)["attempts"][0]["status"], "refusal")

    def test_incomplete_response_is_not_approved(self):
        transport = FixtureTransport(body=response_bytes(status="incomplete", incomplete={"reason": "max_output_tokens"}))
        with self.assertRaisesRegex(review.ReviewError, "incomplete"):
            review.review_task(*self.args(), transport=transport)
        self.assertEqual(review.task_status(self.task_dir)["attempts"][0]["status"], "incomplete")

    def test_invalid_schema_result_is_not_approved(self):
        transport = FixtureTransport(body=response_bytes({"mode": "creation", "criteria": [], "findings": []}))
        with self.assertRaisesRegex(review.ReviewError, "schema violation"):
            review.review_task(*self.args(), transport=transport)
        self.assertEqual(review.task_status(self.task_dir)["attempts"][0]["status"], "schema_invalid")

    def test_invalid_response_json_is_not_approved_and_marks_usage_indeterminate(self):
        transport = FixtureTransport(body=b"{this is not JSON")
        with self.assertRaisesRegex(review.ReviewError, "invalid JSON"):
            review.review_task(*self.args(), transport=transport)
        status = review.task_status(self.task_dir)
        self.assertEqual(status["pending_call_id"], "review-001")
        self.assertEqual(status["attempts"][0]["consumption_status"], "indeterminate")

    def test_timeout_is_not_retried_and_blocks_until_reconciliation(self):
        transport = FixtureTransport(exception=TimeoutError())
        with self.assertRaisesRegex(review.ReviewError, "timed out"):
            review.review_task(*self.args(), transport=transport)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(review.task_status(self.task_dir)["pending_call_id"], "review-001")
        changed = png_bytes(pixel=77)
        (self.source / "result.png").write_bytes(changed)
        with self.assertRaisesRegex(review.ReviewError, "indeterminate consumption"):
            review.review_task(*self.args(cycle=2), progress_note="Captured the result again after a verified local adjustment.", transport=transport)
        self.assertEqual(len(transport.calls), 1)
        reconciled = review.reconcile_call(self.task_dir, "review-001", "not-charged", "Checked task usage dashboard; no request usage appeared.")
        self.assertEqual(reconciled["outcome"], "not-charged")

    def test_http_error_is_not_retried_and_secrets_are_not_logged(self):
        key = "test-marker-never-a-key"
        transport = FixtureTransport(status=401, body=key.encode())
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            with self.assertRaisesRegex(review.ReviewError, "HTTP 401") as raised:
                review.review_task(*self.args(), transport=transport)
        self.assertEqual(len(transport.calls), 1)
        self.assertNotIn(key, str(raised.exception))
        self.assertNotIn(key, output.getvalue())
        usage_log = (self.task_dir / "api-usage.jsonl").read_text()
        self.assertNotIn(key, usage_log)

    def test_counters_persist_and_prevent_more_than_authorized_calls(self):
        auth = self.authorization("one-call-task")
        auth["limits"]["max_api_calls"] = 1
        auth_path = self.root / "one-call.json"
        auth_path.write_text(json.dumps(auth))
        task = self.init_authorized_task("one-call-task", auth_path, self.root / "one-call")
        transport = FixtureTransport(body=response_bytes(valid_result(finding=True)))
        review.review_task(task, "creation", 1, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", transport=transport)
        (self.source / "result.png").write_bytes(png_bytes(pixel=55))
        with self.assertRaisesRegex(review.ReviewError, "call limit"):
            review.review_task(task, "creation", 2, self.source / "brief.md", self.source / "criteria.json", self.source / "captures.json", progress_note="Changed the real screenshot after addressing F-1.", addressed_findings=["F-1"], transport=transport)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(review.task_status(task)["calls_attempted"], 1)

    def test_identical_evidence_is_blocked_even_with_a_new_cycle_number(self):
        transport = FixtureTransport(body=response_bytes(valid_result(finding=True)))
        review.review_task(*self.args(), transport=transport)
        with self.assertRaisesRegex(review.ReviewError, "materially changed evidence"):
            review.review_task(*self.args(cycle=2), progress_note="No material screenshot change.", addressed_findings=["F-1"], transport=transport)
        self.assertEqual(len(transport.calls), 1)

    def test_template_style_stale_price_data_blocks_live_review(self):
        auth = self.authorization()
        auth["pricing"]["verified_at"] = "2000-01-01"
        with self.assertRaisesRegex(review.ReviewError, "older than 30 days"):
            review.validate_authorization(auth, {"task_id": auth["task_id"], "project": auth["project"], "scope": auth["scope"]})

    def test_authorization_rejects_unverified_model_capability_or_secret_fields(self):
        task = {"task_id": "offline-visual-task", "project": "demo", "scope": "route /"}
        auth = self.authorization()
        auth["model_capabilities"]["vision_input"] = False
        with self.assertRaisesRegex(review.ReviewError, "confirm vision input"):
            review.validate_authorization(auth, task)
        auth = self.authorization()
        auth["OPENAI_API_KEY"] = "test-marker-never-a-key"
        with self.assertRaisesRegex(review.ReviewError, "secrets and extra fields"):
            review.validate_authorization(auth, task)

    def test_authorization_and_capture_validators_reject_unhashable_enum_values(self):
        task = {"task_id": "offline-visual-task", "project": "demo", "scope": "route /"}
        auth = self.authorization()
        auth["pricing"]["image_detail"] = []
        with self.assertRaisesRegex(review.ReviewError, "image detail"):
            review.validate_authorization(auth, task)

        capture_manifest = json.loads((self.source / "captures.json").read_text(encoding="utf-8"))
        capture_manifest["captures"][0]["platform"] = []
        limits = self.authorization()["limits"]
        pricing = self.authorization()["pricing"]
        with self.assertRaisesRegex(review.ReviewError, "Capture platform"):
            review.validate_capture_manifest(capture_manifest, "creation", None, limits, pricing)

    def test_no_real_network_transport_is_ever_opened_by_unit_tests(self):
        with self.assertRaises(AssertionError):
            review.send_response({}, "test-marker-never-a-key", 1)

    def test_concurrent_review_attempt_is_blocked_by_task_lock(self):
        transport = FixtureTransport()
        with review.exclusive_task_lock(self.task_dir):
            with self.assertRaisesRegex(review.ReviewError, "concurrent calls are blocked"):
                review.review_task(*self.args(), transport=transport)
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
