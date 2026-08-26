from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TransparencyPolicy(str, Enum):
    REQUIRED = "REQUIRED"
    ALLOWED = "ALLOWED"
    LAYER_SPECIFIC = "LAYER_SPECIFIC"
    FORBIDDEN = "FORBIDDEN"


@dataclass(frozen=True)
class AssetProfile:
    name: str
    transparency: TransparencyPolicy
    width: int | None = None
    height: int | None = None
    max_bytes: int | None = None
    border_transparency_required: bool | None = None
    notes: str = ""


PROFILES: dict[str, AssetProfile] = {
    "repo-generic": AssetProfile(
        name="repo-generic",
        transparency=TransparencyPolicy.REQUIRED,
        border_transparency_required=None,
        notes="Generic repository raster asset. Dimensions and border behavior come from the asset contract.",
    ),
    "google-play-app-icon": AssetProfile(
        name="google-play-app-icon",
        transparency=TransparencyPolicy.ALLOWED,
        width=512,
        height=512,
        max_bytes=1024 * 1024,
        notes="Google Play store app icon profile. Revalidate current vendor requirements before release automation.",
    ),
    "google-play-feature-graphic": AssetProfile(
        name="google-play-feature-graphic",
        transparency=TransparencyPolicy.FORBIDDEN,
        width=1024,
        height=500,
        notes="Google Play feature graphic profile; alpha is not permitted.",
    ),
    "pwa-maskable": AssetProfile(
        name="pwa-maskable",
        transparency=TransparencyPolicy.FORBIDDEN,
        notes="Maskable icons should provide opaque content with safe padding for platform masking.",
    ),
    "android-adaptive-foreground": AssetProfile(
        name="android-adaptive-foreground",
        transparency=TransparencyPolicy.LAYER_SPECIFIC,
        notes="Foreground layer can contain transparency; Android adaptive icon safe-zone/mask rules apply.",
    ),
    "android-adaptive-background": AssetProfile(
        name="android-adaptive-background",
        transparency=TransparencyPolicy.FORBIDDEN,
        notes="Background layer should be full supporting artwork rather than generic transparency.",
    ),
    "apple-icon-foreground": AssetProfile(
        name="apple-icon-foreground",
        transparency=TransparencyPolicy.LAYER_SPECIFIC,
        notes="Foreground layer may use opacity. Revalidate current Apple icon guidance for target platform.",
    ),
    "apple-icon-background": AssetProfile(
        name="apple-icon-background",
        transparency=TransparencyPolicy.FORBIDDEN,
        notes="Background layer should be full-bleed and opaque under current layered-icon guidance.",
    ),
}


def get_profile(name: str) -> AssetProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown asset profile: {name}") from exc
