# Security Policy

Transparency Assurance may inspect untrusted image uploads. Treat image decoding as part of the security boundary.

## Rules

- Allowlist supported formats in automated pipelines.
- Enforce maximum pixel/dimension limits.
- Treat decompression-bomb warnings as failures.
- Verify image structure before deeper processing where possible.
- Keep Pillow, NumPy and decoder dependencies current and pinned for releases.
- Strip EXIF/XMP from public repo derivatives by default unless preservation is required.
- Preserve or normalize ICC profiles deliberately rather than accidentally.
- Use private temporary paths and clean them after QA.
- Never include secrets, access tokens or private metadata in QA attestations.
- Preserve untouched originals when transparency edits are applied to evidence or source material.

Please report security issues privately to the repository owner rather than publishing exploit details in a public issue.
