#!/usr/bin/env python3
"""Build a camera LUT handoff folder and ZIP with a source-backed compatibility report."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from check_camera_compatibility import check_lut, load_profile
from generate_cube_lut import LOOKS, LUMIX_PHOTO_STYLE_TAGS, write_cube
from mix_lut_strength import mix_lut
from validate_lut import analyze, parse_cube


DEFAULT_PROFILE = Path(__file__).resolve().parents[1] / "references" / "camera-profiles" / "panasonic-dc-s9.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_camera_name(name: str, filesystem: str, profile: dict[str, Any]) -> str:
    if not name.isascii() or not re.fullmatch(r"[A-Za-z0-9]+", name):
        raise ValueError("--name must contain only ASCII letters and digits.")
    rules = profile.get("card_filesystems", {})
    rule = rules.get(filesystem.upper(), {})
    if filesystem.upper() == "FAT32":
        limit = rule.get("max_stem_chars", 8)
        if len(name) > limit:
            raise ValueError(f"--name must be at most {limit} characters for FAT32.")
    else:
        limit = rule.get("max_name_chars_including_extension", 255)
        if len(name + ".cube") > limit:
            raise ValueError(f"The filename must be at most {limit} characters including .cube for exFAT.")
    return name


def stamp_lumix_photo_style(path: Path, style: str) -> None:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    lines = [line for line in lines if not re.match(r"\s*#LUMIXPHOTOSTYLE\b", line, flags=re.IGNORECASE)]
    title_index = next((index for index, line in enumerate(lines) if line.lstrip().upper().startswith("TITLE")), None)
    if title_index is None:
        lines.insert(0, 'TITLE "Camera LUT"\n')
        title_index = 0
    elif not lines[title_index].endswith(("\n", "\r")):
        lines[title_index] += "\n"
    newline = "\r\n" if lines[title_index].endswith("\r\n") else "\n"
    lines.insert(title_index + 1, f"#LUMIXPHOTOSTYLE {style}{newline}")
    path.write_bytes(bom + "".join(lines).encode("utf-8"))


def make_preview(image_path: Path, lut_path: Path, output_path: Path, color_mode="srgb-photo") -> None:
    try:
        from PIL import Image, ImageOps
        from apply_lut_preview import apply_lut, parse_cube, resize_for_preview
    except ImportError as exc:
        raise ValueError("Pillow is required to include a preview image.") from exc

    from image_color import open_for_lut, save_for_lut
    lut_size, lut_values = parse_cube(lut_path)
    image, _ = open_for_lut(image_path, color_mode)
    image = resize_for_preview(image, 1400)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_for_lut(apply_lut(image, lut_size, lut_values), output_path, color_mode, format="PNG")


def write_package_readme(
    path: Path,
    device: str,
    filename: str,
    filesystem: str,
    status: str,
    quality_status: str,
    style: str | None,
    preview_present: bool,
    preview_error: str | None,
) -> None:
    state = (
        "相机档案和 LUT 结构检查通过"
        if status == "COMPATIBLE_WITH_DECLARED_PROFILE" and quality_status == "PASS"
        else "需要复核：至少一项检查未完全通过"
    )
    lines = [
        f"# {device} LUT 交付包",
        "",
        f"状态：**{state}**（{status}）",
        "",
        f"- LUT 文件：`{filename}.cube`",
        f"- SD 卡文件系统：`{filesystem}`",
        f"- Photo Style 标记：`{style or '未指定；按相机文档默认值处理'}`",
        "- 格式和相机档案检查：见 `camera-check.json`",
        "- LUT 结构与质量提示：见 `lut-quality.json`",
        f"- 预览图：{'已包含' if preview_present else ('生成失败：' + preview_error if preview_error else '未生成；打包时未提供 --preview-image')}",
        "",
        "使用前请确认相机档案检查状态为 `COMPATIBLE_WITH_DECLARED_PROFILE`。将 `.cube` 文件复制到 SD 卡根目录，再通过相机的 LUT Library 注册。该检查不能证明 LUT 的视觉效果、色彩变换准确性或真机导入结果。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def create_zip(package_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, Path(package_dir.name) / file_path.relative_to(package_dir))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or package a .cube LUT for a documented camera profile.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--lut", help="Existing .cube LUT; the source file is preserved.")
    source.add_argument("--look", choices=sorted(LOOKS), help="Generate a creative LUT from a built-in look.")
    parser.add_argument("--camera-profile", default=str(DEFAULT_PROFILE), help="Source-backed camera profile JSON (default: Panasonic DC-S9).")
    parser.add_argument("--card-filesystem", required=True, choices=("FAT32", "exFAT"), help="Filesystem of the target SD card.")
    parser.add_argument("--name", default="LUMIX01", help="Alphanumeric camera filename without extension (default: LUMIX01).")
    parser.add_argument("--output-dir", required=True, help="New folder for the LUT handoff package.")
    parser.add_argument("--strength", type=float, default=1.0, help="Generated-look strength or imported-LUT amount, from 0 to 1.")
    parser.add_argument("--size", type=int, default=33, help="Generated 3D LUT size; must be accepted by the selected camera profile.")
    parser.add_argument("--lumix-photo-style", choices=sorted(LUMIX_PHOTO_STYLE_TAGS), help="Optional Panasonic base Photo Style metadata tag.")
    parser.add_argument("--preview-image", help="Optional user-selected RGB image for an included preview.")
    parser.add_argument("--preview-color-mode", choices=("srgb-photo", "encoded-rgb"), default="srgb-photo")
    args = parser.parse_args()
    if not 0.0 <= args.strength <= 1.0:
        parser.error("--strength must be between 0 and 1")
    if args.size < 2:
        parser.error("--size must be at least 2")
    return args


def main() -> None:
    args = parse_args()
    profile_path = Path(args.camera_profile)
    output_dir = Path(args.output_dir)
    zip_path = output_dir.parent / f"{output_dir.name}.zip"
    try:
        profile = load_profile(profile_path)
        filename = safe_camera_name(args.name, args.card_filesystem, profile)
        if output_dir.exists() or zip_path.exists():
            raise FileExistsError(f"Output folder or ZIP already exists: {output_dir} / {zip_path}")
        accepted_sizes = profile.get("allowed_3d_sizes", [])
        if args.look and accepted_sizes and args.size not in {int(value) for value in accepted_sizes}:
            raise ValueError(f"Size {args.size} is not supported by the selected camera profile.")
        supported_styles = {str(value).upper() for value in profile.get("supported_lumix_photo_styles", [])}
        if args.lumix_photo_style and supported_styles and args.lumix_photo_style not in supported_styles:
            raise ValueError(f"Photo Style {args.lumix_photo_style} is not listed in the selected camera profile.")
        source_lut = None
        original_hash = None
        if args.lut:
            source_lut = Path(args.lut).resolve()
            if not source_lut.is_file() or source_lut.suffix.lower() != ".cube":
                raise ValueError("--lut must point to an existing .cube file.")
            original_hash = sha256_file(source_lut)

        with tempfile.TemporaryDirectory(prefix="lut-package-") as temporary_directory:
            staged_dir = Path(temporary_directory) / output_dir.name
            staged_dir.mkdir()
            lut_path = staged_dir / f"{filename}.cube"
            if args.look:
                params = dict(LOOKS[args.look])
                title = f"{args.look} {args.strength:.2f}"
                write_cube(lut_path, args.size, title, args.look, args.strength, params, True, args.lumix_photo_style)
                input_description = f"built-in look: {args.look}"
            else:
                if source_lut is None:
                    raise ValueError("An input LUT is required unless a built-in look is selected.")
                if math_is_full_strength(args.strength):
                    shutil.copy2(source_lut, lut_path)
                else:
                    mix_lut(source_lut, lut_path, args.strength)
                if args.lumix_photo_style:
                    stamp_lumix_photo_style(lut_path, args.lumix_photo_style)
                input_description = f"source LUT: {source_lut.name}"

            camera_check = check_lut(lut_path, profile_path, args.card_filesystem)
            camera_check["lut"] = lut_path.name
            (staged_dir / "camera-check.json").write_text(json.dumps(camera_check, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            try:
                checked_size, checked_values, notes = parse_cube(lut_path)
                quality_errors, quality_warnings = analyze(checked_size, checked_values)
                quality_report = {
                    "status": "PASS" if not quality_errors else "FAIL",
                    "size": checked_size,
                    "entries": len(checked_values),
                    "errors": quality_errors,
                    "warnings": quality_warnings,
                    "notes": notes,
                }
            except (OSError, ValueError) as exc:
                quality_report = {"status": "FAIL", "errors": [str(exc)], "warnings": [], "notes": []}
            (staged_dir / "lut-quality.json").write_text(json.dumps(quality_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            preview_error = None
            if args.preview_image:
                try:
                    make_preview(Path(args.preview_image), lut_path, staged_dir / "preview.png", args.preview_color_mode)
                except (OSError, ValueError) as exc:
                    preview_error = str(exc)

            manifest = {
                "device": profile["device"],
                "profile_verification_date": profile.get("verification_date"),
                "profile_sources": profile.get("sources", []),
                "input": input_description,
                "source_lut_sha256": original_hash,
                "lut_file": lut_path.name,
                "lut_sha256": sha256_file(lut_path),
                "lut_size": camera_check.get("lut_size"),
                "strength": args.strength,
                "lumix_photo_style": args.lumix_photo_style,
                "card_filesystem": args.card_filesystem,
                "camera_check_status": camera_check.get("status"),
                "lut_quality_status": quality_report.get("status"),
                "preview_included": (staged_dir / "preview.png").exists(),
                "preview_error": preview_error,
                "preview_color_mode": args.preview_color_mode,
            }
            (staged_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            write_package_readme(
                staged_dir / "README.md", str(profile["device"]), filename, args.card_filesystem,
                str(camera_check.get("status")), str(quality_report.get("status")), args.lumix_photo_style,
                bool(manifest["preview_included"]), preview_error,
            )
            staged_zip = Path(temporary_directory) / zip_path.name
            create_zip(staged_dir, staged_zip)
            output_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staged_dir), str(output_dir))
            shutil.move(str(staged_zip), str(zip_path))
        print(f"Package folder: {output_dir}")
        print(f"Package ZIP: {zip_path}")
        print(f"Camera check: {camera_check.get('status')}")
        if preview_error:
            print(f"Preview skipped: {preview_error}")
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not build camera LUT package: {exc}") from exc


def math_is_full_strength(value: float) -> bool:
    return value >= 1.0


if __name__ == "__main__":
    main()
