# Marla Transparency Assurance Skill

**Skill ID:** SKL-0004  
**Version:** 2.0  
**Priority:** 100/100

## Purpose

Create, edit, validate, repair and deliver transparent image assets with the lowest practical regeneration rate and the lowest possible false-acceptance rate.

## Central rule

**Transparency is a verifiable output contract, not a style phrase.**

Never assume a checkerboard preview proves transparency. Never claim alpha was verified unless the actual file or bytes were inspected and the required QA gates passed.

## Execution workflow

1. Detect transparency intent.
2. Resolve the target/platform asset profile.
3. Decide whether alpha is REQUIRED, ALLOWED, LAYER_SPECIFIC or FORBIDDEN.
4. Select the edge/material mode: HARD_CUTOUT, SOFT_EDGE, TRANSLUCENT, PRODUCT, REPO_ASSET or EDIT_PRESERVE_ALPHA.
5. Build an internal asset contract: format, dimensions, edge mode, shadow, padding, target path/name, color/metadata policy and file-size limit.
6. Use a native transparent-background control when the image tool exposes one. Do not rely on prose alone.
7. If final bytes are accessible, inspect source format/transparency representation before normalization.
8. Run mode/profile-specific file, alpha, border, topology, checkerboard, edge, semantic, round-trip and target-contract QA.
9. Composite on checkerboard, white, black, a contrasting color and the real target background when known. Prefer color-managed linear-light compositing.
10. Classify failures as NO_REPAIR_NEEDED, SAFE_DETERMINISTIC, SAFE_WITH_TARGET_MASK, SEMANTIC_SEGMENTATION_REQUIRED or REGENERATION_REQUIRED.
11. Prefer deterministic repair when it preserves intent. Regenerate only when repair would damage semantic content or confidence is low.
12. Re-run QA after repair/regeneration.
13. Emit a truthful capability state and optional QA attestation with final SHA-256.
14. Deliver only the accepted asset.

## Capability states

- VERIFIED_NATIVE_ALPHA
- VERIFIED_REPAIRED_ALPHA
- VERIFIED_TARGET_COMPLIANT
- NATIVE_ALPHA_REQUESTED_FILE_NOT_ACCESSIBLE
- VISUAL_ONLY_NOT_FILE_VERIFIED
- FAILED_QA_REPAIRABLE
- FAILED_QA_REGENERATE
- TARGET_FORBIDS_TRANSPARENCY

Do not upgrade a weaker state to a stronger state without evidence.

## Source representation

A transparent PNG does not have to be literal RGBA. Valid PNG transparency can include explicit alpha or `tRNS`/palette transparency. Record source representation, bit depth, profile metadata and animation/frame state where practical before converting to a normalized QA representation.

## Core QA gates

- FILE_IDENTITY
- TRANSPARENCY_CAPABILITY
- MEANINGFUL_ALPHA_USAGE
- BACKGROUND_CONNECTIVITY
- BORDER_EXPECTATION
- ALPHA_TOPOLOGY
- FAKE_CHECKERBOARD
- EDGE_QUALITY
- SEMANTIC_TRANSPARENCY
- ROUND_TRIP
- TARGET_CONTRACT

Each gate should report PASS, FAIL, NOT_APPLICABLE or UNVERIFIED plus evidence/metrics. Avoid one universal threshold where the correct threshold depends on the selected profile.

## Repair rules

Do not delete every pixel merely because it matches a sampled corner color. For separable flat backgrounds, prefer boundary-connected flood fill from candidate border pixels. Preserve same-colored interior foreground regions. Refuse repair when confidence is low.

Do not crudely threshold hair, fur, smoke, glass, glow, translucent fabric or soft shadows.

## Target awareness

Transparency is not universally desirable. The target profile decides whether transparency is required, allowed, layer-specific or forbidden. Store platform requirements in versioned profile files rather than burying them permanently in prompt prose.

## Security

Treat uploaded images as untrusted input. Allowlist formats, verify/decode safely, enforce pixel limits, handle malformed files, control metadata, pin dependencies, and avoid leaking temporary files or repo-unnecessary metadata.

## Success metrics

Primary: false acceptance rate.

Secondary: first-generation alpha success, final accepted success, repair salvage rate, regeneration rate, false rejection rate, edge artifact rate, target compliance, generations per accepted asset and QA runtime.

## Non-negotiable honesty

If the generator was asked for transparency but final file bytes are unavailable, say that native transparency was requested but file-level alpha could not be verified. Never call that state VERIFIED_NATIVE_ALPHA.
