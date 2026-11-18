# Authorized API operations

Version 2 task authorization is in [authorization-v2.template.json](authorization-v2.template.json) and
[task-authorization-v2.schema.json](../schemas/task-authorization-v2.schema.json). It configures a separate exact model,
verified capabilities, processing tier, price snapshot, output limit, and call cap for each operation:

- `design_direction`: structured proposal before implementation;
- `visual_review`: first consultive review of explicitly selected current screenshots;
- `visual_reevaluation`: later review with full prior findings and new screenshot/build evidence;
- `ui_content`: copy suggestions grounded in selected facts, terminology, locales, and existing keys;
- `image_assets`: one explicitly scoped image generation or edit.

All operations share task authorization, one HTTPS transport, attempt ledger, request limits, usage/cost accounting,
reservation/reconciliation, and task state. Endpoints are restricted to Responses, image generation, and image edits.
There are no automatic retries. Each request records request/response IDs when supplied, exact requested/returned model,
service tier, response time, usage, pricing snapshot, task/build/evidence fingerprints, estimate, settlement, and status.
The result remains consultive or proposed; no API response applies code, copy, assets, or a task conclusion.

Processing tiers and prices are task inputs, not model defaults. Verify capabilities, supported tier, and matching rate
regime from the [official API model documentation](https://developers.openai.com/api/docs/models/),
[Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create),
[Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses),
[Image generation guide](https://developers.openai.com/api/docs/guides/image-generation), and
[pricing page](https://developers.openai.com/api/docs/pricing) before any authorized live call. Model IDs and rates are
not hard-coded in the helper. Image detail, dimensions, token bounds, input/output sizes, formats, backgrounds, and
identity replacement are bounded by the task config.

The dry-run constructs the request payload and a conservative estimate locally. With a task authorization it uses that
task's exact config; a `synthetic: true` config uses only `offline-*` model labels and is accepted only with explicit
`--dry-run`. Dry-run performs no network call and no task writes. Its result says server acceptance is unverified. The
offline tests inject fixture transports; they do not contact the API.
