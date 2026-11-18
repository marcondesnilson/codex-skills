"""Single-request OpenAI HTTP transport with deliberately narrow endpoints."""

from __future__ import annotations

from dataclasses import dataclass
import json
import urllib.error
import urllib.request


API_ORIGIN = "https://api.openai.com"
RESPONSES_PATH = "/v1/responses"
IMAGE_GENERATIONS_PATH = "/v1/images/generations"
IMAGE_EDITS_PATH = "/v1/images/edits"
ALLOWED_PATHS = {RESPONSES_PATH, IMAGE_GENERATIONS_PATH, IMAGE_EDITS_PATH}
DEFAULT_MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_IMAGE_RESPONSE_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    body: bytes
    request_id: str | None = None

    def __iter__(self):
        # Keep the existing (status, body) transport contract.
        yield self.status_code
        yield self.body


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _request_id(headers) -> str | None:
    value = headers.get("x-request-id") if headers is not None else None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > 256 or any(ord(char) < 0x20 or ord(char) > 0x7E for char in value):
        return None
    return value


def send_json_request(
    endpoint_path: str,
    payload: dict,
    api_key: str,
    timeout_seconds: int,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> ApiResponse:
    """Send exactly one JSON POST to a fixed API endpoint without redirects."""
    if endpoint_path not in ALLOWED_PATHS:
        raise ValueError("API endpoint is not in the local allowlist")
    if not isinstance(payload, dict) or not isinstance(api_key, str) or not api_key:
        raise ValueError("API request payload and key are required")
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise ValueError("API timeout must be a positive integer")
    if not isinstance(max_response_bytes, int) or max_response_bytes < 1:
        raise ValueError("API response limit must be a positive integer")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        API_ORIGIN + endpoint_path,
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(NoRedirectHandler)
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            body = response.read(max_response_bytes + 1)
            if len(body) > max_response_bytes:
                raise OSError("API response exceeded its local size limit")
            return ApiResponse(response.status, body, _request_id(response.headers))
    except urllib.error.HTTPError as error:
        return ApiResponse(error.code, b"", _request_id(error.headers))


def send_response(payload: dict, api_key: str, timeout_seconds: int) -> ApiResponse:
    return send_json_request(RESPONSES_PATH, payload, api_key, timeout_seconds)
