"""Offline tests for scoped design, UI-copy, and image operations."""

import base64
from datetime import date
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
import design_operations as operations  # noqa: E402
import visual_review as review  # noqa: E402
import api_transport  # noqa: E402
from api_transport import ApiResponse  # noqa: E402


def png_bytes(size=2):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x20\x30\x40" * size for _ in range(size))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def snapshot(root):
    return {path.relative_to(root).as_posix(): ("directory" if path.is_dir() else path.read_bytes()) for path in sorted(root.rglob("*"))}


class DesignOperationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.brief = self.project / "brief.md"
        self.brief.write_text("Prepare a calm, accessible synthetic dashboard direction.", encoding="utf-8")
        self.task = review.init_task(
            "design-offline", "synthetic project", "dashboard", self.root / "tasks", project_root=self.project,
        )
        self.no_network = patch.object(api_transport.urllib.request, "build_opener", side_effect=AssertionError("offline test attempted real network"))
        self.no_urlopen = patch.object(api_transport.urllib.request, "urlopen", side_effect=AssertionError("offline test attempted real network"))
        self.no_network.start()
        self.no_urlopen.start()

    def tearDown(self):
        self.no_urlopen.stop()
        self.no_network.stop()
        self.temp.cleanup()

    def synthetic_config(self, operation="design_direction", *, allowed_asset_ids=None):
        return {
            "synthetic": True,
            "operation": operation,
            "model": "offline-fixture-model",
            "service_tier": "standard" if operation == "image_assets" else "default",
            "max_output_tokens": None if operation == "image_assets" else 512,
            "pricing": {
                "billing_regime": "standard",
                "input_usd_per_million": 1,
                "image_input_usd_per_million": 2,
                "output_usd_per_million": 3,
                "image_output_usd_per_million": 4,
                "image_input_tokens_upper_bound_per_asset": 100,
                "image_output_tokens_upper_bound": 1000,
                "image_detail": "high",
                "image_bound_max_width": 4096,
                "image_bound_max_height": 4096,
                "image_bound_max_pixels": 16_777_216,
            },
            "allowed_asset_ids": allowed_asset_ids or [],
            "image_options": {
                "sizes": ["1024x1024"], "qualities": ["medium"], "formats": ["png"],
                "backgrounds": ["opaque"], "max_input_assets": 3, "max_output_bytes": 1024 * 1024,
            },
            "identity_replacement_authorized": False,
        }

    def test_synthetic_direction_dry_run_builds_payload_and_estimate_without_writes(self):
        before = snapshot(self.task)
        transport = lambda *args, **kwargs: self.fail("offline dry-run called transport")

        result = operations.run_design_direction(
            self.task, self.brief, identity_status="missing", dry_run=True,
            synthetic_config=self.synthetic_config(), transport=transport,
        )

        self.assertEqual(result["result"], "offline_payload_ready")
        self.assertFalse(result["api_called"])
        self.assertFalse(result["writes_performed"])
        self.assertTrue(result["payload_constructed"])
        self.assertEqual(result["server_acceptance"], "not_verified_offline")
        self.assertGreater(result["estimate"]["estimated_cost_usd"], 0)
        self.assertEqual(snapshot(self.task), before)

    def test_dry_run_without_synthetic_config_validates_inputs_but_does_not_write(self):
        before = snapshot(self.task)
        result = operations.run_design_direction(self.task, self.brief, identity_status="missing", dry_run=True)
        self.assertEqual(result["result"], "offline_inputs_validated")
        self.assertFalse(result["payload_constructed"])
        self.assertIsNone(result["estimate"])
        self.assertEqual(snapshot(self.task), before)

    def test_identity_conflict_needs_explicit_decision_before_payload(self):
        with self.assertRaisesRegex(review.ReviewError, "explicit task decision"):
            operations.run_design_direction(self.task, self.brief, identity_status="conflict", dry_run=True)

    def test_missing_identity_does_not_allow_selected_brand_material_as_authority(self):
        image = self.project / "brand.png"
        image.write_bytes(png_bytes())
        manifest = self.project / "selected-assets.json"
        manifest.write_text(json.dumps({"assets": [{"id": "logo", "path": str(image), "kind": "logo_variant"}]}), encoding="utf-8")
        with self.assertRaisesRegex(review.ReviewError, "Identity is marked missing"):
            operations.run_design_direction(
                self.task, self.brief, identity_status="missing", assets_path=manifest, dry_run=True,
                synthetic_config=self.synthetic_config(allowed_asset_ids=["logo"]),
            )

    def test_selected_assets_outside_project_root_are_rejected(self):
        outside = self.root / "outside.png"
        outside.write_bytes(png_bytes())
        manifest = self.project / "selected-assets.json"
        manifest.write_text(json.dumps({"assets": [{"id": "example", "path": str(outside), "kind": "example"}]}), encoding="utf-8")
        with self.assertRaisesRegex(review.ReviewError, "outside the task-authorized project workspace"):
            operations.run_design_direction(
                self.task, self.brief, identity_status="missing", assets_path=manifest, dry_run=True,
                synthetic_config=self.synthetic_config(allowed_asset_ids=["example"]),
            )

    def test_content_dry_run_preserves_fact_and_locale_context(self):
        request = self.project / "content.json"
        request.write_text(json.dumps({
            "request": "Suggest the dashboard greeting.", "locales": ["pt-BR"],
            "facts": [{"id": "product-name", "text": "Produto Demonstração"}],
            "terminology": ["painel"], "existing_strings": {"home.title": "Visão geral"},
            "constraints": ["Preserve the i18n key."],
        }), encoding="utf-8")
        result = operations.run_ui_content(
            self.task, request, dry_run=True, synthetic_config=self.synthetic_config("ui_content"),
        )
        self.assertTrue(result["payload_constructed"])
        self.assertFalse(result["api_called"])
        self.assertEqual(result["operation"], "ui_content")

    def test_content_request_rejects_empty_fact_ids(self):
        request = self.project / "empty-fact-id.json"
        request.write_text(json.dumps({
            "request": "Suggest a label.", "locales": ["pt-BR"],
            "facts": [{"id": "", "text": "Synthetic fact"}], "terminology": [],
            "existing_strings": {}, "constraints": [],
        }), encoding="utf-8")
        with self.assertRaisesRegex(review.ReviewError, "unique ID"):
            operations._content_input(request)

    def test_selected_asset_kind_rejects_unhashable_json_value(self):
        manifest = self.project / "bad-assets.json"
        manifest.write_text(json.dumps({"assets": [{"id": "fixture", "path": "unused.png", "kind": []}]}), encoding="utf-8")
        with self.assertRaisesRegex(review.ReviewError, "asset kind"):
            operations._selected_assets(manifest, None, 3, str(self.project))

    def test_v2_authorization_rejects_unhashable_modality_cleanly(self):
        auth = self.v2_authorization("bad-modality")
        auth["operations"]["ui_content"]["model_capabilities"]["input_modalities"] = [[]]
        task = {"task_id": "bad-modality", "project": "synthetic project", "scope": "copy request"}
        with self.assertRaisesRegex(review.ReviewError, "invalid input_modalities"):
            review.validate_authorization(auth, task)

    def test_image_generation_payload_is_explicit_and_offline_only(self):
        config = self.synthetic_config("image_assets")
        data = {
            "action": "generate", "prompt": "Abstract geometric placeholder, no brand marks.",
            "purpose": "Synthetic test asset", "size": "1024x1024", "quality": "medium",
            "format": "png", "background": "opaque", "assets": [], "replace_identity": False,
        }
        endpoint, payload, assets = operations._image_payload(data, operations._synthetic_config(config, "image_assets"))
        self.assertEqual(endpoint, "/v1/images/generations")
        self.assertEqual(payload["n"], 1)
        self.assertEqual(payload["output_format"], "png")
        self.assertEqual(assets, [])
        result = operations.run_image_assets(
            self.task, action="generate", prompt=data["prompt"], purpose=data["purpose"], size=data["size"],
            quality=data["quality"], output_format=data["format"], background=data["background"],
            dry_run=True, synthetic_config=config,
        )
        self.assertEqual(result["result"], "offline_payload_ready")
        self.assertFalse(result["api_called"])

    def test_synthetic_config_can_never_authorize_a_live_operation(self):
        with self.assertRaisesRegex(review.ReviewError, "explicitly offline dry-run"):
            operations.run_design_direction(
                self.task, self.brief, identity_status="missing", dry_run=False,
                synthetic_config=self.synthetic_config(),
            )

    def test_live_call_is_blocked_without_separate_api_execution_permission(self):
        task = self.init_v2_task("permission-fixture", api_execution=False)
        request = self.write_content_request("permission-request.json")
        calls = []
        with self.assertRaisesRegex(review.ReviewError, "separate authorization for API execution"):
            operations.run_ui_content(task, request, transport=lambda *args: calls.append(args))
        self.assertEqual(calls, [])

    def test_timeout_keeps_reservation_and_blocks_retry_of_same_operation(self):
        task = self.init_v2_task("timeout-fixture", api_execution=True)
        request = self.write_content_request("timeout-request.json")
        calls = []
        def timeout_transport(*args):
            calls.append(args)
            raise TimeoutError()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            with self.assertRaisesRegex(review.ReviewError, "consumption is indeterminate"):
                operations.run_ui_content(task, request, transport=timeout_transport)
            with self.assertRaisesRegex(review.ReviewError, "indeterminate consumption"):
                operations.run_ui_content(task, request, transport=timeout_transport)
        self.assertEqual(len(calls), 1)
        status = review.task_status(task)
        self.assertIsNotNone(status["pending_call_id"])
        self.assertGreater(status["budget_committed_usd"], 0)

    def test_image_generation_mock_is_one_shared_scoped_transport_call(self):
        task_id = "image-fixture"
        authorization = self.v2_authorization(task_id)
        base = authorization["operations"]["ui_content"]
        image_config = {
            "model": "model-fixture",
            "model_capabilities": {
                "source_url": "https://developers.openai.com/api/docs/guides/image-generation",
                "verified_at": date.today().isoformat(), "input_modalities": ["text", "image"],
                "output_modalities": ["image"], "structured_outputs": False, "image_generation": True,
            },
            "service_tier": "standard", "max_calls": 2, "max_output_tokens": None,
            "pricing": base["pricing"],
            "image_options": {
                "sizes": ["1024x1024"], "qualities": ["medium"], "formats": ["png"],
                "backgrounds": ["opaque"], "max_input_assets": 0, "max_output_bytes": 1024 * 1024,
            },
            "identity_replacement_authorized": False,
        }
        authorization["operations"] = {"image_assets": image_config}
        auth_path = self.root / "image-auth.json"
        auth_path.write_text(json.dumps(authorization), encoding="utf-8")
        plan_path = self.root / "image-plan.json"
        plan_path.write_text(json.dumps({
            "schema_version": 1, "frontend_impact": False, "components": ["synthetic image endpoint"],
            "checks": [{"id": "unit-check", "category": "UNIT", "required": True, "description": "Mocked image operation."}],
        }), encoding="utf-8")
        task = review.init_task(
            task_id, "synthetic project", "copy request", self.root / "image-tasks", auth_path,
            plan_path, api_execution_authorized=True, project_root=self.project,
        )
        calls = []
        response = {
            "created": 1794945600,
            "data": [{"b64_json": base64.b64encode(png_bytes(1024)).decode("ascii")}],
            "usage": {"input_tokens": 5, "output_tokens": 10, "total_tokens": 15},
        }
        def transport(endpoint, payload, api_key, timeout, limit):
            calls.append({"endpoint": endpoint, "payload": payload})
            return ApiResponse(200, json.dumps(response).encode(), "req-image-fixture")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            result = operations.run_image_assets(
                task, action="generate", prompt="Abstract geometric placeholder without a logo.",
                purpose="Synthetic fixture", size="1024x1024", quality="medium", output_format="png",
                background="opaque", transport=transport,
            )
        self.assertTrue(result["api_called"])
        arguments = dict(action="generate", prompt="Abstract geometric placeholder without a logo.",
                         size="1024x1024", quality="medium", output_format="png", background="opaque",
                         transport=transport)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            with self.assertRaisesRegex(review.ReviewError, "Identical payload"):
                operations.run_image_assets(task, purpose="Changed purpose only", **arguments)
            operations.run_image_assets(task, purpose="Intentional variant",
                                        variant_reason="Compare a second generated composition.", **arguments)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["payload"], calls[1]["payload"])
        self.assertEqual(calls[0]["endpoint"], "/v1/images/generations")
        self.assertEqual(calls[0]["payload"]["n"], 1)
        self.assertEqual(result["request_id"], "req-image-fixture")
        self.assertTrue((task / result["output_file"]).is_file())

    def write_content_request(self, filename):
        request = self.project / filename
        request.write_text(json.dumps({
            "request": "Offer concise dashboard copy.", "locales": ["pt-BR"],
            "facts": [{"id": "name", "text": "Painel Sintético"}], "terminology": [],
            "existing_strings": {"home.title": "Visão geral"}, "constraints": [],
        }), encoding="utf-8")
        return request

    def init_v2_task(self, task_id, *, api_execution):
        auth_path = self.root / f"{task_id}-authorization.json"
        auth_path.write_text(json.dumps(self.v2_authorization(task_id)), encoding="utf-8")
        plan_path = self.root / f"{task_id}-acceptance.json"
        plan_path.write_text(json.dumps({
            "schema_version": 1, "frontend_impact": False, "components": ["synthetic API operation"],
            "checks": [{"id": "unit-check", "category": "UNIT", "required": True, "description": "Mocked API contract."}],
        }), encoding="utf-8")
        return review.init_task(
            task_id, "synthetic project", "copy request", self.root / f"{task_id}-tasks", auth_path,
            plan_path, api_execution_authorized=api_execution, project_root=self.project,
        )

    def test_authorized_factor_blocks_budget_between_old_and_correct_estimates(self):
        task = self.init_v2_task("factor-fixture", api_execution=True)
        request = self.write_content_request("factor.json")
        stored = task / "authorization.json"
        auth = json.loads(stored.read_text())
        auth["limits"]["estimate_safety_factor"] = 2
        review.write_json(stored, auth)
        dry = operations.run_ui_content(task, request, dry_run=True)
        self.assertEqual(dry["estimate"]["safety_factor"], 2)
        auth["max_estimated_cost_usd"] = dry["estimate"]["estimated_cost_usd"] * 0.8
        review.write_json(stored, auth)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            with self.assertRaisesRegex(review.ReviewError, "remaining task budget"):
                operations.run_ui_content(task, request, transport=lambda *_: self.fail("Transport was called"))
        self.assertEqual(review.read_task(task)[1]["calls_attempted"], 0)

    def test_shared_accounting_keeps_reserve_and_settlement_from_double_counting(self):
        state = {"attempts": [{
            "estimated_cost_usd": 0.10, "reserved_cost_usd": 0.10,
            "consumption_status": "reported_usage", "status": "completed",
            "cost_calculated_from_reported_usage_usd": 0.03,
        }]}
        self.assertEqual(operations.committed_budget_usd(state), 0.03)
        state["attempts"][0]["consumption_status"] = "indeterminate"
        self.assertEqual(operations.committed_budget_usd(state), 0.10)

    def test_live_v2_ui_content_uses_one_injected_shared_transport_and_records_trace(self):
        auth = self.v2_authorization("live-fixture")
        auth_path = self.root / "authorization.json"
        auth_path.write_text(json.dumps(auth), encoding="utf-8")
        plan_path = self.root / "backend-plan.json"
        plan_path.write_text(json.dumps({
            "schema_version": 1, "frontend_impact": False, "components": ["synthetic API contract"],
            "checks": [{"id": "unit-check", "category": "UNIT", "required": True, "description": "Fixture contract."}],
        }), encoding="utf-8")
        task = review.init_task(
            "live-fixture", "synthetic project", "copy request", self.root / "live-tasks", auth_path,
            plan_path, api_execution_authorized=True, project_root=self.project,
        )
        request_file = self.project / "copy-request.json"
        request_file.write_text(json.dumps({
            "request": "Offer concise dashboard copy.", "locales": ["pt-BR"],
            "facts": [{"id": "name", "text": "Painel Sintético"}], "terminology": [],
            "existing_strings": {"home.title": "Visão geral"}, "constraints": [],
        }), encoding="utf-8")
        api_response = {
            "id": "resp_local_fixture", "model": "model-fixture", "service_tier": "default",
            "created_at": 1794945600, "status": "completed", "incomplete_details": None,
            "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps({
                "items": [{"key": "home.title", "locale": "pt-BR", "text": "Painel Sintético", "source_fact_ids": ["name"], "notes": []}],
                "limitations": ["Fixture only."],
            })}]}],
            "usage": {"input_tokens": 20, "output_tokens": 10, "total_tokens": 30},
        }
        calls = []
        def transport(endpoint, payload, api_key, timeout, response_limit):
            calls.append({"endpoint": endpoint, "payload": payload, "timeout": timeout, "limit": response_limit})
            return ApiResponse(200, json.dumps(api_response).encode(), "req_local_fixture")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-marker-only"}):
            result = operations.run_ui_content(task, request_file, transport=transport)

        self.assertTrue(result["api_called"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["endpoint"], "/v1/responses")
        self.assertEqual(result["request_id"], "req_local_fixture")
        _, state, _ = review.read_task(task)
        attempt = state["attempts"][0]
        self.assertEqual(attempt["model_returned"], "model-fixture")
        self.assertEqual(attempt["service_tier_returned"], "default")
        self.assertIsNotNone(attempt["cost_calculated_from_reported_usage_usd"])
        status = review.task_status(task)
        self.assertEqual(status["attempts"][0]["operation"], "ui_content")
        self.assertIsNone(status["attempts"][0]["cycle"])

    def v2_authorization(self, task_id):
        today = date.today().isoformat()
        pricing = {
            "model": "model-fixture", "verified_at": today,
            "source_url": "https://developers.openai.com/api/docs/pricing",
            "billing_regime": "standard", "input_usd_per_million": 1,
            "image_input_usd_per_million": 1, "output_usd_per_million": 2,
            "image_output_usd_per_million": 2, "image_input_tokens_upper_bound_per_asset": 100,
            "image_output_tokens_upper_bound": 100, "image_detail": "high",
            "image_bound_max_width": 4096, "image_bound_max_height": 4096,
            "image_bound_max_pixels": 16_777_216,
        }
        return {
            "schema_version": 2, "authorization_id": "fixture-only", "task_id": task_id,
            "project": "synthetic project", "scope": "copy request",
            "data_policy": "Only synthetic facts and local fixture text are allowed.",
            "allowed_capture_ids": [], "allowed_asset_ids": [],
            "valid_until": "2099-01-01T00:00:00Z", "max_estimated_cost_usd": 1.0,
            "limits": {
                "max_visual_cycles": 3, "max_api_calls": 2, "max_captures_or_pairs": 2,
                "max_single_file_bytes": 1024 * 1024, "max_aggregate_bytes": 2 * 1024 * 1024,
                "max_image_width": 4096, "max_image_height": 4096,
                "max_aggregate_pixels": 16_777_216, "timeout_seconds": 3,
                "estimate_safety_factor": 1.25,
            },
            "operations": {
                "ui_content": {
                    "model": "model-fixture",
                    "model_capabilities": {
                        "source_url": "https://developers.openai.com/api/docs/models/model-fixture",
                        "verified_at": today, "input_modalities": ["text"], "output_modalities": ["text"],
                        "structured_outputs": True, "image_generation": False,
                    },
                    "service_tier": "default", "max_calls": 1, "max_output_tokens": 512,
                    "pricing": pricing,
                },
            },
        }


if __name__ == "__main__":
    unittest.main()
