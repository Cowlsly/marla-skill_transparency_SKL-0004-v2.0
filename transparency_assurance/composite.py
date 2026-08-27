from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image


def _srgb_to_linear(x: np.ndarray) -> np.ndarray:
    x = x / 255.0
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1.0 / 2.4)) - 0.055)


def composite_linear_srgb(image: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    """Composite RGBA over an sRGB background in linear light.

    Alpha is treated as linear coverage and is not gamma-corrected.
    """
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32)
    fg = _srgb_to_linear(rgba[:, :, :3])
    bg = _srgb_to_linear(np.array(background, dtype=np.float32)[None, None, :])
    alpha = rgba[:, :, 3:4] / 255.0
    out = fg * alpha + bg * (1.0 - alpha)
    encoded = np.rint(_linear_to_srgb(out) * 255.0).astype(np.uint8)
    return Image.fromarray(encoded, "RGB")


def make_contact_sheet(
    image: Image.Image,
    backgrounds: Iterable[tuple[str, tuple[int, int, int]]],
    output: str | Path,
    padding: int = 16,
) -> Path:
    rendered = [(name, composite_linear_srgb(image, rgb)) for name, rgb in backgrounds]
    if not rendered:
        raise ValueError("At least one background is required")
    width, height = rendered[0][1].size
    sheet = Image.new("RGB", (len(rendered) * width + (len(rendered) + 1) * padding, height + 2 * padding), "white")
    x = padding
    for _name, view in rendered:
        sheet.paste(view, (x, padding))
        x += width + padding
    output = Path(output)
    sheet.save(output, "PNG")
    return output


DEFAULT_BACKGROUNDS = (
    ("white", (255, 255, 255)),
    ("black", (0, 0, 0)),
    ("blue", (30, 90, 180)),
    ("magenta", (180, 30, 130)),
)
