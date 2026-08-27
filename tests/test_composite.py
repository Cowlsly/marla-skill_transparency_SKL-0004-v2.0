import numpy as np
from PIL import Image

from transparency_assurance.composite import composite_linear_srgb


def test_fully_transparent_pixel_becomes_background():
    im = Image.new("RGBA", (1, 1), (255, 0, 0, 0))
    out = composite_linear_srgb(im, (12, 34, 56))
    assert out.getpixel((0, 0)) == (12, 34, 56)


def test_fully_opaque_pixel_preserves_foreground():
    im = Image.new("RGBA", (1, 1), (90, 120, 180, 255))
    out = composite_linear_srgb(im, (255, 255, 255))
    got = out.getpixel((0, 0))
    assert all(abs(a - b) <= 1 for a, b in zip(got, (90, 120, 180)))


def test_half_alpha_is_not_naive_srgb_average():
    im = Image.new("RGBA", (1, 1), (255, 255, 255, 128))
    out = composite_linear_srgb(im, (0, 0, 0))
    value = out.getpixel((0, 0))[0]
    # Correct linear-light composite is much brighter than naïve 127/128 sRGB averaging.
    assert value > 180
