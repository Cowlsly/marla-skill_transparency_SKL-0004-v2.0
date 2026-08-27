from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def boundary_connected_flat_repair(source: str | Path, output: str | Path, tolerance: float = 18.0) -> dict:
    """Remove only background-like pixels connected to the canvas boundary.

    This is intentionally conservative. It preserves same-coloured interior regions that are
    not connected to the boundary and should not be used for complex backgrounds, hair/fur,
    smoke, glass or other semantically entangled edges without additional review.
    """
    source = Path(source)
    output = Path(output)
    im = Image.open(source).convert("RGBA")
    arr = np.asarray(im).copy()
    rgb = arr[:, :, :3].astype(np.float32)
    h, w = rgb.shape[:2]

    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]], axis=0)
    bg = np.median(border, axis=0)
    distance = np.sqrt(np.sum((rgb - bg) ** 2, axis=2))
    candidate = distance <= tolerance

    connected = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        if candidate[0, x]: q.append((0, x))
        if candidate[h - 1, x]: q.append((h - 1, x))
    for y in range(h):
        if candidate[y, 0]: q.append((y, 0))
        if candidate[y, w - 1]: q.append((y, w - 1))

    while q:
        y, x = q.popleft()
        if connected[y, x] or not candidate[y, x]:
            continue
        connected[y, x] = True
        if y: q.append((y - 1, x))
        if y + 1 < h: q.append((y + 1, x))
        if x: q.append((y, x - 1))
        if x + 1 < w: q.append((y, x + 1))

    before_opaque = int(np.sum(arr[:, :, 3] > 0))
    arr[connected, 3] = 0
    after_opaque = int(np.sum(arr[:, :, 3] > 0))
    removed_ratio = (before_opaque - after_opaque) / max(before_opaque, 1)

    Image.fromarray(arr, "RGBA").save(output, "PNG")
    return {
        "method": "boundary_connected_flat",
        "estimated_background_rgb": [float(x) for x in bg],
        "tolerance": tolerance,
        "removed_foreground_candidate_ratio": removed_ratio,
        "output": str(output),
        "requires_semantic_review": True,
    }
