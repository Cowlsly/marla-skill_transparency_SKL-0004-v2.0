from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class CheckerboardResult:
    detected: bool
    score: float
    tile_size: int | None
    visible_fraction: float
    reason: str


def _neutral_fraction(rgb: np.ndarray) -> float:
    if rgb.size == 0:
        return 0.0
    spread = rgb.max(axis=1).astype(np.int16) - rgb.min(axis=1).astype(np.int16)
    return float(np.mean(spread <= 18))


def detect_baked_checkerboard(image: Image.Image) -> CheckerboardResult:
    """Detect a visible, repeated checkerboard-like background pattern.

    Fully transparent pixels are excluded so stale/hidden RGB beneath alpha=0 cannot be
    mistaken for visible pseudo-transparency. This detector is deliberately conservative:
    it looks for a neutral, alternating square pattern at common preview tile sizes.
    Semantic QA is still required for artwork that intentionally contains a checker motif.
    """
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    visible = alpha >= 16
    visible_fraction = float(np.mean(visible))
    if visible_fraction < 0.05:
        return CheckerboardResult(False, 0.0, None, visible_fraction, "Too little visible area for checkerboard evidence")

    h, w = alpha.shape
    best_score = 0.0
    best_tile: int | None = None

    # Restrict to plausible preview checker sizes. Very tiny lags become texture/noise;
    # very large lags are poor evidence for a repeated transparency preview pattern.
    candidates = [4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64]
    candidates = [t for t in candidates if 2 * t < min(h, w)]

    gray = rgb.astype(np.float32).mean(axis=2)

    for tile in candidates:
        # A true checker alternates after one tile and repeats after two tiles.
        left = gray[:, :-2 * tile]
        mid = gray[:, tile:-tile]
        right = gray[:, 2 * tile:]
        m = visible[:, :-2 * tile] & visible[:, tile:-tile] & visible[:, 2 * tile:]
        if int(m.sum()) < max(64, int(0.01 * h * w)):
            continue

        repeat_error = float(np.mean(np.abs(left[m] - right[m])))
        alternate_delta = float(np.mean(np.abs(left[m] - mid[m])))

        top = gray[:-2 * tile, :]
        middle = gray[tile:-tile, :]
        bottom = gray[2 * tile:, :]
        mv = visible[:-2 * tile, :] & visible[tile:-tile, :] & visible[2 * tile:, :]
        if int(mv.sum()) < max(64, int(0.01 * h * w)):
            continue
        vrepeat_error = float(np.mean(np.abs(top[mv] - bottom[mv])))
        valternate_delta = float(np.mean(np.abs(top[mv] - middle[mv])))

        repeat_quality = max(0.0, 1.0 - (repeat_error + vrepeat_error) / 36.0)
        alternating_quality = min(1.0, (alternate_delta + valternate_delta) / 36.0)

        vis_rgb = rgb[visible]
        neutral = _neutral_fraction(vis_rgb)
        score = repeat_quality * alternating_quality * neutral
        if score > best_score:
            best_score = score
            best_tile = tile

    detected = best_score >= 0.62
    reason = "Visible neutral alternating square periodicity detected" if detected else "No strong visible checkerboard periodicity detected"
    return CheckerboardResult(detected, float(best_score), best_tile, visible_fraction, reason)
