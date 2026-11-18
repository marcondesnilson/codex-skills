# Media Kit and visual direction

Create direction before implementing a new screen or the requested redesign. Keep the task's authorized project/workspace
as the boundary: `init --project-root` records the root, and selected briefs, asset manifests, and assets must be regular
files inside it. Select only relevant items from a Media Kit. The helper records source IDs, types, classifications, and
SHA-256 values for the brief, selected files, and accepted direction.

Classify sources before using them:

- `brand_guide`, `palette`, and `typography`: normative only when the project owner identifies them as current authority;
- `logo_variant`: an identity asset whose variant must be selected explicitly;
- `example`: visual reference only, never a rule or proof of product behavior;
- `asset` and `icon`: selected visual material, not identity policy;
- `previous_decision`: the complete adopted direction content and its hash, not just an ID.

If identity material is missing, state that fact and do not invent brand colors, logos, typography, or voice. If sources
conflict, record an explicit task decision before consulting the model. The selected sources are not automatically
approved by the tool. A response is saved as `proposed_not_adopted`; adoption or rejection appends a decision record with
actor, reason, change note, version, source hash, and prior-direction hash. A later proposal never silently overwrites
history. `adopted_within_task_scope` and `approved_by_user` remain distinct decisions.

The direction schema covers objective, audience, priorities, composition, hierarchy, density, typography, color/tokens,
components, imagery, copy guidance, accessibility, empty/loading/error states, platform adaptations, evaluation criteria,
identity notes, basis, and limitations. It is a structured proposal before a screen exists, not a screenshot or a visual
quality verdict. User-approved direction content and the full prior finding evidence are passed into later reviews; the
workflow does not reuse a direction or findings by identifier alone.

The visual reference template is [visual-direction.template.json](visual-direction.template.json). To create a proposal,
use the `design-direction` CLI command and inspect the returned proposal before recording a task decision. A synthetic
configuration can build and estimate an offline payload, but is accepted only with `--dry-run`; it cannot authorize a
live request.
