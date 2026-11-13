"""Normalize supported still photos to tagged 8-bit sRGB before creative LUTs."""
from __future__ import annotations

import io
from PIL import Image, ImageCms, ImageOps


def srgb_profile_bytes() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def prepare_image(opened: Image.Image) -> tuple[Image.Image, dict]:
    if opened.mode not in {"1", "L", "P", "RGB", "RGBA"}:
        raise ValueError(f"Image mode {opened.mode} is outside the 8-bit photo workflow; convert RAW, HDR, 16-bit or CMYK with a managed workflow first.")
    oriented = ImageOps.exif_transpose(opened)
    alpha_present = oriented.mode == "RGBA" or (oriented.mode == "P" and "transparency" in oriented.info)
    source = oriented.convert("RGBA" if alpha_present else "RGB")
    embedded = opened.info.get("icc_profile")
    rgb = source.convert("RGB")
    if embedded:
        try:
            profile = ImageCms.ImageCmsProfile(io.BytesIO(embedded))
            rgb = ImageCms.profileToProfile(rgb, profile, ImageCms.createProfile("sRGB"), outputMode="RGB")
        except (OSError, ValueError, TypeError, ImageCms.PyCMSError) as exc:
            raise ValueError("Embedded ICC profile could not be converted to sRGB; refusing an unverified color preview.") from exc
    if alpha_present:
        rgb.putalpha(source.getchannel("A"))
    rgb.info["icc_profile"] = srgb_profile_bytes()
    return rgb, {"working_space": "sRGB", "icc_action": "converted_to_sRGB" if embedded else "untagged_assumed_sRGB", "exif_orientation_applied": True}


def open_srgb(path) -> tuple[Image.Image, dict]:
    with Image.open(path) as opened:
        return prepare_image(opened)


def save_srgb(image: Image.Image, path, **options) -> None:
    image.save(path, icc_profile=srgb_profile_bytes(), **options)


def open_for_lut(path, color_mode="srgb-photo") -> tuple[Image.Image, dict]:
    if color_mode == "srgb-photo":
        return open_srgb(path)
    if color_mode != "encoded-rgb":
        raise ValueError("Unknown preview color mode.")
    with Image.open(path) as opened:
        if opened.mode not in {"1", "L", "P", "RGB", "RGBA"}:
            raise ValueError("Encoded previews require an 8-bit image in the LUT's declared input encoding.")
        oriented = ImageOps.exif_transpose(opened)
        alpha = oriented.mode == "RGBA" or (oriented.mode == "P" and "transparency" in oriented.info)
        image = oriented.convert("RGBA" if alpha else "RGB")
        image.info.pop("icc_profile", None)
        return image, {"working_space": "user_declared_encoding", "icc_action": "explicit_bypass", "exif_orientation_applied": True}


def save_for_lut(image: Image.Image, path, color_mode="srgb-photo", **options) -> None:
    if color_mode == "srgb-photo":
        save_srgb(image, path, **options)
    else:
        copy = image.copy()
        copy.info.pop("icc_profile", None)
        copy.save(path, **options)
