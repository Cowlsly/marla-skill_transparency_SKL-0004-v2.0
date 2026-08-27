# Changelog

## 2.0.0-alpha.2

### Added
- Conservative spatial fake-checkerboard detector that ignores RGB hidden beneath fully transparent pixels.
- Direct checkerboard positive/negative regression tests.
- Linear-light sRGB compositing utilities and multi-background QA contact-sheet support.
- CLI `contact-sheet`, `attest`, and `profiles` commands.
- Machine-readable QA attestation JSON schema.
- Target-profile JSON records for Google Play app icons and feature graphics, Android adaptive icon layers, PWA maskable icons, and Apple icon foreground/background layers.

### Changed
- Checkerboard QA is now an active structural gate rather than an unverified placeholder.
- Layer-specific target profiles no longer incorrectly require transparency in every asset.
- Capability states remain conservative when semantic/edge QA is unavailable.

### Still experimental
- Mode-aware halo/chroma-spill grading.
- Semantic visual grading.
- APNG/frame-aware validation.
- Large deterministic fixture corpus and empirical false-acceptance benchmark.

## 2.0.0-alpha.1

Initial Transparency Assurance v2 scaffold.

- Added canonical SKL-0004 v2 workflow.
- Added target-aware asset profiles and transparency policies.
- Added deterministic PNG/alpha validator with machine-readable QA report.
- Added conservative boundary-connected flat-background repair.
- Added CLI entry point.
- Added regression tests and GitHub Actions CI.
- Added security guidance and capability-state model.

This alpha is not yet production-ready.
