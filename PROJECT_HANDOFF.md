# PROJECT HANDOFF — Marla Transparency Assurance SKL-0004 v2

**Prepared:** 27 August 2026  
**Project:** `marla-skill_transparency_SKL-0004-v2.0`  
**Status:** Active development, pre-release alpha foundation  
**Primary goal:** Turn transparency handling into a target-aware, verifiable, repair-before-regeneration assurance system for Marla-AI and downstream repo workflows.

---

## 1. Primary GitHub Repository

**Repository:** `Cowlsly/marla-skill_transparency_SKL-0004-v2.0`  
**GitHub URL:** https://github.com/Cowlsly/marla-skill_transparency_SKL-0004-v2.0  
**Default branch:** `main`  
**Working branch:** `build/transparency-assurance-v2`

### Active Pull Request
**PR #1:** `Build Transparency Assurance v2 foundation`  
https://github.com/Cowlsly/marla-skill_transparency_SKL-0004-v2.0/pull/1

Current policy:
- Keep PR as **draft**.
- Do not merge to `main` until CI actually runs successfully and P0 correctness has a trustworthy baseline.
- Primary quality metric is false acceptance rate.

### Roadmap Issue
**Issue #2:** `Transparency Assurance v2 completion roadmap`  
https://github.com/Cowlsly/marla-skill_transparency_SKL-0004-v2.0/issues/2

Use Issue #2 as the authoritative implementation checklist.

---

## 2. Current Repository State

Latest observed development state at handoff:

- PR remains open and draft.
- Main branch remains untouched by the v2 development work.
- Current v2 foundation includes:
  - canonical `SKILL.md`
  - target-aware asset profiles
  - deterministic PNG/alpha validator
  - SHA-256 and machine-readable QA evidence
  - conservative boundary-connected background repair
  - spatial fake-checkerboard detector
  - linear-light sRGB compositing utilities
  - multi-background contact-sheet support
  - CLI
  - pytest tests
  - GitHub Actions CI
  - asset-contract and QA-attestation JSON schemas
  - profile definitions for generic repo assets, Google Play, Android adaptive layers, PWA maskable icons, and Apple layered icons
  - `SECURITY.md`
  - `CHANGELOG.md`
  - `NOTICE`
  - Apache-2.0 license
  - README with Cowlsly / Marla-AI attribution

---

## 3. Important Repository Paths

### Core skill / documentation
- `SKILL.md`
- `README.md`
- `CHANGELOG.md`
- `SECURITY.md`
- `NOTICE`
- `LICENSE`
- `pyproject.toml`

### Python package
- `transparency_assurance/__init__.py`
- `transparency_assurance/validator.py`
- `transparency_assurance/repair.py`
- `transparency_assurance/checkerboard.py`
- `transparency_assurance/composite.py`
- `transparency_assurance/profiles.py`
- `transparency_assurance/cli.py`

### Schemas
- `schemas/asset-contract.schema.json`
- `schemas/qa-attestation.schema.json`

### Target profiles
- `profiles/repo-generic.json`
- `profiles/google-play-app-icon.json`
- `profiles/google-play-feature-graphic.json`
- `profiles/android-adaptive-foreground.json`
- `profiles/android-adaptive-background.json`
- `profiles/pwa-maskable.json`
- `profiles/apple-icon-foreground.json`
- `profiles/apple-icon-background.json`

### Tests
- `tests/test_validator.py`
- `tests/test_checkerboard.py`
- `tests/test_composite.py`
- `tests/test_target_profiles.py`

### CI
- `.github/workflows/ci.yml`

---

## 4. Current CI Blocker

GitHub Actions currently creates the `test` job but the observed workflow runs terminate before any workflow steps begin.

Observed behavior:
- workflow created
- job created
- job conclusion = failure
- zero workflow steps reported
- no usable job log payload returned

Treat this as a **CI execution/platform/configuration blocker**, not as a pytest failure.

Do not claim the code tests failed until a runner actually starts and executes steps.

Next CI investigation:
1. inspect repository Actions availability/settings manually if needed;
2. verify GitHub Actions is enabled for the repository;
3. verify public-repo runner availability / account restrictions;
4. rerun after any platform/configuration correction;
5. only then debug Python/test failures if steps actually execute.

---

## 5. P0 Roadmap Status

Completed:
- [x] Spatial fake-checkerboard detector with direct positive/negative tests
- [x] Color-managed / linear-light multi-background contact-sheet generation
- [x] Target profiles for Google Play, Android adaptive, PWA maskable and Apple layered icons
- [x] Formal QA attestation schema and CLI support

Still required:
- [ ] Mode-aware edge QA that distinguishes white/grey halos, chroma spill, legitimate shadows, glow, hair/fur, glass/smoke/translucency
- [ ] Expand regression coverage so every deterministic failure mode is directly asserted
- [ ] Add capability-state tests for environments where final output bytes are unavailable

Do not promote to production-ready v2 until these are solid.

---

## 6. P1 Roadmap

- Expand deterministic fixture corpus to ~30–50 cases
- PNG source representation reporting: bit depth, explicit alpha, palette transparency, `tRNS`, color profile/gamma metadata, APNG frames
- Animation-aware alpha validation
- EXIF/XMP sanitization policy
- ICC preservation tests
- corrupt/truncated image tests
- decompression-bomb guard tests
- `EDIT_PRESERVE_ALPHA` before/after alpha-diff validation
- dependency pinning / lockfile
- release cleanup and reproducibility

---

## 7. P2 Roadmap

- WebP / AVIF / vector asset profiles
- perceptual edge metrics
- semantic visual contact-sheet grader
- generated challenge benchmark
- threshold calibration by asset mode/profile
- empirical measurement of first-generation success, repair salvage rate, regeneration rate, false rejection, false acceptance, platform compliance, and average generations per accepted asset

Primary benchmark priority: **minimize false acceptance**.

---

## 8. Core Execution Architecture

The intended final skill workflow is:

`TARGET POLICY`
→ `GENERATION CONTROL`
→ `FORMAT/COLOR VALIDATION`
→ `PIXEL/ALPHA VALIDATION`
→ `MULTI-BACKGROUND COMPOSITE QA`
→ `SEMANTIC VISUAL QA`
→ `SAFE REPAIR OR REGENERATE`
→ `HASHED ATTESTATION`
→ `DELIVERY`

Core principle:

> Transparency is a verifiable output contract, not a style phrase.

Never claim transparency is technically verified when final bytes were not inspected.

---

## 9. Capability States

The skill should use truthful terminal states such as:

- `VERIFIED_NATIVE_ALPHA`
- `VERIFIED_REPAIRED_ALPHA`
- `VERIFIED_TARGET_COMPLIANT`
- `NATIVE_ALPHA_REQUESTED_FILE_NOT_ACCESSIBLE`
- `VISUAL_ONLY_NOT_FILE_VERIFIED`
- `FAILED_QA_REPAIRABLE`
- `FAILED_QA_REGENERATE`
- `TARGET_FORBIDS_TRANSPARENCY`

Do not elevate a weaker state into a stronger one without evidence.

---

## 10. Important Design Decisions Already Made

### Repair-before-regeneration
Do not waste a good generation if its transparency can be repaired safely.

### Boundary-connected repair
Do not globally delete every pixel matching a corner color. Background removal should normally operate on boundary-connected candidate regions.

### Target-aware transparency
Transparency may be REQUIRED, ALLOWED, LAYER-SPECIFIC, or FORBIDDEN depending on target platform / asset type.

### Checkerboard rule
A visible checkerboard is not automatically proof of transparency. Checkerboard pixels baked into RGB are a failure.

### Color-managed compositing
Composite QA should use linear-light / properly managed color math rather than naïve gamma-encoded blending where practical.

### Repo asset QA
Repo-ready assets should support machine-readable attestation including SHA-256, validator version, dimensions, format, alpha metrics, target profile, gate statuses, repair history, capability state, and compliance result.

---

## 11. Source Investigation Artifacts

### Original Transparency investigation
- `/mnt/data/transparent_assets_full_investigative_report.pdf`
- `/mnt/data/investigation-report_transparency_skill_planning_2026-08-26.txt`

### Deep maximum-quality audit
- `/mnt/data/alpha_assurance_full_investigative_report.pdf`
- `/mnt/data/investigation-report_transparency_skill_maximum_quality_2026-08-27.txt`

### Master prompt and workflow
- `/mnt/data/transparency_skill_v2_master_prompt_and_workflow.md`

### Original packaged v1.0 skill
- `/mnt/data/marla-skill_transparency_SKL-0004_v1.0.zip`
- `/mnt/data/marla-skill_transparency_SKL-0004_v1.0/`

These container paths may not persist forever. The GitHub repository should become the durable source of truth.

---

## 12. Related Skill Dependency

The transparency project was researched using the Investigate methodology:

**Skill:** `marla-skill_investigate_SKL-0003`  
**Version used:** v4.0

No GitHub repository matching `marla-skill_investigate_SKL-0003` was found under the Cowlsly account at handoff time.

Therefore:
- do not invent a GitHub URL for Investigate;
- treat the Investigate skill package / conversation artifacts as the current source;
- if/when a dedicated Investigate repo is created, add it here as an upstream methodology dependency.

---

## 13. Recommended Next Work Session

1. Open PR #1 and Issue #2.
2. Confirm the current head branch is `build/transparency-assurance-v2`.
3. Check whether GitHub Actions can actually start a runner.
4. If CI is still platform-blocked, continue deterministic development without pretending CI passed.
5. Implement mode-aware edge QA.
6. Add direct tests for each edge condition.
7. Add capability-state tests.
8. Begin expanding the fixture corpus.
9. Keep PR draft.
10. Update this handoff after any major architecture change.

---

## 14. Merge / Release Rule

Do **not** merge PR #1 merely because the code looks complete.

Minimum merge readiness:
- CI actually runs steps
- P0 tests pass
- no known false-acceptance bug in core gates
- target profile tests pass
- validator reports truthful capability states
- checkerboard detector has direct tests
- edge QA no longer treats legitimate shadows as generic corruption
- roadmap updated

Production v2.0 promotion should wait until:
- expanded deterministic corpus exists
- false acceptance has been measured
- generated challenge suite exists
- semantic QA path is defined

---

## 15. Repository License

**Apache License 2.0**

Use SPDX: `Apache-2.0`

Third-party fixtures/assets must retain compatible provenance/licensing.
Prefer synthetic/Cowlsly-created regression fixtures.

---

## 16. Handoff Summary

The project is healthy but intentionally unfinished.

The central architecture is sound. The repo now has real deterministic tooling, target profiles, checkerboard detection, linear-light composite support, schemas, CLI, tests and CI configuration.

The main technical frontier is no longer "how do we make a transparent PNG?"

It is:

> How do we prove that the alpha is semantically correct, target-compliant, visually clean, reproducible, and safe to accept without unnecessary regeneration?

That is the definition of Transparency Assurance v2.
