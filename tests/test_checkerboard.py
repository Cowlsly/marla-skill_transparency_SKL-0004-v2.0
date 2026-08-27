from pathlib import Path

from PIL import Image, ImageDraw

from transparency_assurance.checkerboard import detect_baked_checkerboard
from transparency_assurance.validator import inspect_asset


def _checker(size: int = 128, tile: int = 16) -> Image.Image:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size, tile):
        for x in range(0, size, tile):
            c = (224, 224, 224, 255) if ((x // tile + y // tile) % 2 == 0) else (184, 184, 184, 255)
            d.rectangle((x, y, x + tile - 1, y + tile - 1), fill=c)
    return im


def test_visible_baked_checkerboard_is_detected(tmp_path: Path):
    p = tmp_path / "baked.png"
    _checker().save(p)
    result = detect_baked_checkerboard(Image.open(p))
    assert result.detected is True
    assert result.score >= 0.62
    report = inspect_asset(p, "repo-generic")
    assert report["gates"]["FAKE_CHECKERBOARD"]["status"] == "FAIL"


def test_hidden_checkerboard_under_zero_alpha_is_not_visible_failure(tmp_path: Path):
    p = tmp_path / "hidden.png"
    im = _checker()
    alpha = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(alpha)
    d.ellipse((32, 32, 96, 96), fill=255)
    subject = Image.new("RGBA", im.size, (40, 120, 220, 255))
    # Keep checker RGB outside the subject but make it fully transparent.
    im.putalpha(alpha)
    subject.putalpha(alpha)
    im.alpha_composite(subject)
    im.save(p)
    result = detect_baked_checkerboard(Image.open(p))
    assert result.detected is False


def test_plain_opaque_art_is_not_checkerboard(tmp_path: Path):
    p = tmp_path / "plain.png"
    im = Image.new("RGB", (128, 128), (40, 80, 150))
    ImageDraw.Draw(im).ellipse((24, 24, 104, 104), fill=(220, 120, 40))
    im.save(p)
    result = detect_baked_checkerboard(Image.open(p))
    assert result.detected is False
