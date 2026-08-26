from pathlib import Path

from PIL import Image

from transparency_assurance.validator import inspect_asset


def test_feature_graphic_opaque_png_can_pass(tmp_path: Path):
    p = tmp_path / "feature.png"
    Image.new("RGB", (1024, 500), (30, 40, 50)).save(p, "PNG")
    report = inspect_asset(p, "google-play-feature-graphic")
    assert report["gates"]["TRANSPARENCY_CAPABILITY"]["status"] == "NOT_APPLICABLE"
    assert report["gates"]["MEANINGFUL_ALPHA_USAGE"]["status"] == "PASS"
    assert report["target_compliant"] is True


def test_play_icon_wrong_dimensions_fails(tmp_path: Path):
    p = tmp_path / "icon.png"
    Image.new("RGBA", (256, 256), (0, 0, 0, 0)).save(p, "PNG")
    report = inspect_asset(p, "google-play-app-icon")
    assert report["gates"]["TARGET_CONTRACT"]["status"] == "FAIL"
    assert report["target_compliant"] is False
