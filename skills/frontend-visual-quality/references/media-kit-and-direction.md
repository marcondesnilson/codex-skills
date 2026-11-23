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

The discovery order at the authorized project root is `Media Kit`, `MediaKit`, `MEDIAKIT`,
`media-kit`, and `media_kit`. An explicit project-relative or absolute local path confined to
that root can override discovery. Inspect only relevant guides, logo variants, palettes, fonts,
images, icons and examples. Record source/version or hash, license or reuse limits, and
unreadable formats in the selected brand context. Use the existing project tokens and UI conventions
if the kit is absent. Discovery takes place locally. Transmission is limited to files and context
explicitly selected for the operation.

The helper stores project direction history beside private task evidence. Reuse requires the same
evidence root, canonical project path and project label. New tasks pin the latest adoption; another
project receives its own history. Read the adopted record, validate its sources against actual
documentation/tokens, and use the scope-specific brief for the current task. Content hash,
proposal hash and decision hash have separate purposes.

Use `locate-media-kit --task-dir <task-dir>` to perform the bounded lookup, or add `--path <directory>`
for an explicit override. Select and classify source material before preparing any operation.

A change of approval, actor or sources can produce a separate project decision with
the same visual content. The latest decision is inherited on task initialization.
An exact retry of the recorded decision is idempotent. A task pinned to a previous
decision must reload before it can publish another decision. Visual acceptance
depends on the content hash and remains current when only the authority changes.
