from __future__ import annotations

import hashlib
import json
import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, UnidentifiedImageError

from .profiles import TransparencyPolicy, get_profile

MAX_PIXELS = 50_000_000


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _state(value: bool | None, reason: str, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    status = "UNVERIFIED" if value is None else ("PASS" if value else "FAIL")
    return {"status": status, "reason": reason, "metrics": metrics or {}}


def inspect_asset(path: str | Path, profile_name: str = "repo-generic") -> dict[str, Any]:
    path = Path(path)
    profile = get_profile(profile_name)
    report: dict[str, Any] = {
        "validator_version": "2.0.0a1",
        "asset_profile": profile_name,
        "profile": asdict(profile),
        "source_path": str(path),
        "gates": {},
        "warnings": [],
        "repair_history": [],
    }

    if not path.exists() or not path.is_file():
        report["gates"]["FILE_IDENTITY"] = _state(False, "File does not exist or is not a regular file")
        report["capability_state"] = "FAILED_QA_REGENERATE"
        report["target_compliant"] = False
        return report

    report["sha256"] = _sha256(path)
    report["file_size_bytes"] = path.stat().st_size

    old_max = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            try:
                probe = Image.open(path)
                probe.verify()
            except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
                report["gates"]["FILE_IDENTITY"] = _state(False, f"Unsafe image dimensions: {exc}")
                report["capability_state"] = "FAILED_QA_REGENERATE"
                report["target_compliant"] = False
                return report
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                report["gates"]["FILE_IDENTITY"] = _state(False, f"Image verification failed: {exc}")
                report["capability_state"] = "FAILED_QA_REGENERATE"
                report["target_compliant"] = False
                return report
            for item in caught:
                report["warnings"].append(str(item.message))

        im = Image.open(path)
        im.load()
    finally:
        Image.MAX_IMAGE_PIXELS = old_max

    report.update({
        "format": im.format,
        "mode": im.mode,
        "width": im.width,
        "height": im.height,
        "frames": getattr(im, "n_frames", 1),
        "source_info": {
            "has_transparency_data": bool(getattr(im, "has_transparency_data", False)),
            "transparency_key_present": "transparency" in im.info,
            "icc_profile_present": bool(im.info.get("icc_profile")),
            "gamma": im.info.get("gamma"),
            "srgb": im.info.get("srgb"),
        },
    })
    report["gates"]["FILE_IDENTITY"] = _state(True, f"Decoded as {im.format}")

    if im.format != "PNG":
        report["warnings"].append("Current deterministic alpha metrics are PNG-first; other formats require a dedicated format profile.")

    rgba = im.convert("RGBA")
    arr = np.asarray(rgba)
    alpha = arr[:, :, 3]

    transparent_ratio = float(np.mean(alpha == 0))
    partial_ratio = float(np.mean((alpha > 0) & (alpha < 255)))
    opaque_ratio = float(np.mean(alpha == 255))
    nonzero = np.argwhere(alpha > 0)
    bbox = None
    if len(nonzero):
        y0, x0 = nonzero.min(axis=0)
        y1, x1 = nonzero.max(axis=0)
        bbox = [int(x0), int(y0), int(x1 + 1), int(y1 + 1)]

    report["alpha"] = {
        "min": int(alpha.min()),
        "max": int(alpha.max()),
        "transparent_ratio": transparent_ratio,
        "partial_alpha_ratio": partial_ratio,
        "opaque_ratio": opaque_ratio,
        "foreground_bbox": bbox,
    }

    source_has_transparency = bool(getattr(im, "has_transparency_data", False) or "A" in im.getbands() or "transparency" in im.info)
    report["gates"]["TRANSPARENCY_CAPABILITY"] = _state(
        source_has_transparency,
        "Source exposes alpha/transparency representation" if source_has_transparency else "No source alpha/transparency representation detected",
    )

    meaningful = alpha.min() < 255 and (transparent_ratio + partial_ratio) >= 0.001
    if profile.transparency == TransparencyPolicy.FORBIDDEN:
        report["gates"]["MEANINGFUL_ALPHA_USAGE"] = _state(alpha.min() == 255, "Profile forbids transparency")
    else:
        report["gates"]["MEANINGFUL_ALPHA_USAGE"] = _state(meaningful, "Meaningful non-opaque pixels present", {"transparent_ratio": transparent_ratio, "partial_ratio": partial_ratio})

    border = np.concatenate([alpha[0, :], alpha[-1, :], alpha[:, 0], alpha[:, -1]])
    border_transparent = float(np.mean(border == 0))
    report["alpha"]["border_transparent_ratio"] = border_transparent
    if profile.border_transparency_required is None:
        report["gates"]["BORDER_EXPECTATION"] = _state(None, "Border expectation is contract-specific for this profile", {"border_transparent_ratio": border_transparent})
    elif profile.border_transparency_required:
        report["gates"]["BORDER_EXPECTATION"] = _state(border_transparent > 0, "Profile expects some transparent border", {"border_transparent_ratio": border_transparent})
    else:
        report["gates"]["BORDER_EXPECTATION"] = _state(border_transparent == 0, "Profile expects opaque border", {"border_transparent_ratio": border_transparent})

    nearly_empty = opaque_ratio + partial_ratio < 0.001
    noisy_background = 0 < partial_ratio and partial_ratio > 0.70 and opaque_ratio < 0.20
    topology_ok = not nearly_empty and not noisy_background
    report["gates"]["ALPHA_TOPOLOGY"] = _state(topology_ok, "Alpha topology basic sanity check", {"nearly_empty": nearly_empty, "near_transparent_noise_pattern": noisy_background})

    # The spatial checkerboard detector is deliberately left UNVERIFIED until its direct
    # positive/negative fixture suite lands. This is safer than pretending a weak heuristic proves it.
    report["gates"]["FAKE_CHECKERBOARD"] = _state(None, "Spatial checkerboard detector not yet promoted to verified v2 gate")
    report["gates"]["EDGE_QUALITY"] = _state(None, "Requires color-managed composite and semantic visual QA")
    report["gates"]["SEMANTIC_TRANSPARENCY"] = _state(None, "Requires semantic visual QA")

    width_ok = profile.width is None or im.width == profile.width
    height_ok = profile.height is None or im.height == profile.height
    bytes_ok = profile.max_bytes is None or path.stat().st_size <= profile.max_bytes
    target_ok = width_ok and height_ok and bytes_ok
    if profile.transparency == TransparencyPolicy.FORBIDDEN:
        target_ok = target_ok and alpha.min() == 255
    elif profile.transparency == TransparencyPolicy.REQUIRED:
        target_ok = target_ok and meaningful

    report["gates"]["TARGET_CONTRACT"] = _state(target_ok, "Target profile contract", {"width_ok": width_ok, "height_ok": height_ok, "file_size_ok": bytes_ok, "transparency_policy": profile.transparency.value})

    # Round trip through normalized RGBA PNG. This validates the derivative path, not source metadata preservation.
    roundtrip = path.with_suffix(path.suffix + ".qa-roundtrip.png")
    try:
        rgba.save(roundtrip, "PNG")
        check = np.asarray(Image.open(roundtrip).convert("RGBA"))[:, :, 3]
        round_ok = bool(np.array_equal(alpha, check))
    finally:
        if roundtrip.exists():
            roundtrip.unlink()
    report["gates"]["ROUND_TRIP"] = _state(round_ok, "Normalized PNG round-trip alpha preservation")

    hard_fail = any(v["status"] == "FAIL" for k, v in report["gates"].items() if k not in {"EDGE_QUALITY", "SEMANTIC_TRANSPARENCY", "FAKE_CHECKERBOARD"})
    report["target_compliant"] = bool(target_ok and not hard_fail)
    report["capability_state"] = "VERIFIED_TARGET_COMPLIANT" if report["target_compliant"] else "FAILED_QA_REPAIRABLE"
    return report


def write_report(report: dict[str, Any], output: str | Path) -> None:
    Path(output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
