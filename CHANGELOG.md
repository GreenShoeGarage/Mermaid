# Changelog

## 1.0.0 — 2026-09-17

Initial MERMAID Diagram Workbench release.

- Static and self-contained editions with vendored offline runtime libraries.
- Multi-document source editing and live viewing; 24 templates and five palettes.
- Guided flowchart node/edge controls; source outline; source/split/preview layouts.
- Isolated renderer, conservative SVG cleanup, explicit stale-preview exports.
- Local autosave, quota/denial/corruption warnings, cross-tab conflict choices.
- Snapshots, selected baseline, line comparison, restore safeguards.
- Notes, tags/collections, assumptions, evidence, severity/confidence findings.
- Mermaid/Markdown/JSON/SVG imports and source/image/report/archive exports.
- Dark/light/high-contrast themes, Easy/Advanced modes, responsive mobile tabs.
- Regression coverage for rendering, workflow recovery, exports, state validation,
  application-cache logic, and malformed inputs.

Validation fixes included before packaging: requirements-template quoting,
C4 XLink namespace normalization, pure-SVG entity text decoding, error-state
clearing when restoring a cached valid source, stale configuration-response
checks, recovery from invalid appearance settings, and cleared quota warnings
following a successful retry.
