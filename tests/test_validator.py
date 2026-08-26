from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from transparency_assurance.repair import boundary_connected_flat_repair
from transparency_assurance.validator import inspect_asset


def test_good_transparent_png_passes_repo_profile(tmp_path: Path):
    p = tmp_path / "good.png"
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((24, 24, 104, 104), fill=(30, 120, 220, 255))
    im.save(p)
    report = inspect_asset(p, "repo-generic")
    assert report["gates"]["TRANSPARENCY_CAPABILITY"]["status"] == "PASS"
    assert report["gates"]["MEANINGFUL_ALPHA_USAGE"]["status"] == "PASS"
    assert report["target_compliant"] is True


def test_opaque_png_fails_required_alpha(tmp_path: Path):
    p = tmp_path / "opaque.png"
    Image.new("RGB", (128, 128), "white").save(p)
    report = inspect_asset(p, "repo-generic")
    assert report["gates"]["MEANINGFUL_ALPHA_USAGE"]["status"] == "FAIL"
    assert report["target_compliant"] is False


def test_forbidden_alpha_profile_rejects_transparency(tmp_path: Path):
    p = tmp_path / "feature.png"
    im = Image.new("RGBA", (1024, 500), (20, 20, 20, 255))
    im.putpixel((0, 0), (20, 20, 20, 0))
    im.save(p)
    report = inspect_asset(p, "google-play-feature-graphic")
    assert report["gates"]["MEANINGFUL_ALPHA_USAGE"]["status"] == "FAIL"
    assert report["target_compliant"] is False


def test_near_transparent_noise_fails_topology(tmp_path: Path):
    p = tmp_path / "noise.png"
    rng = np.random.default_rng(7)
    arr = np.zeros((128, 128, 4), dtype=np.uint8)
    arr[:, :, :3] = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
    arr[:, :, 3] = rng.integers(1, 6, size=(128, 128), dtype=np.uint8)
    Image.fromarray(arr, "RGBA").save(p)
    report = inspect_asset(p, "repo-generic")
    assert report["gates"]["ALPHA_TOPOLOGY"]["status"] == "FAIL"


def test_boundary_repair_preserves_disconnected_same_colour_subject(tmp_path: Path):
    src = tmp_path / "flat.png"
    out = tmp_path / "fixed.png"
    im = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 80, 80), fill=(0, 80, 180, 255))
    d.rectangle((40, 40, 60, 60), fill=(255, 255, 255, 255))  # interior same as background
    im.save(src)
    boundary_connected_flat_repair(src, out, tolerance=2)
    fixed = Image.open(out).convert("RGBA")
    assert fixed.getpixel((0, 0))[3] == 0
    assert fixed.getpixel((50, 50))[3] == 255
