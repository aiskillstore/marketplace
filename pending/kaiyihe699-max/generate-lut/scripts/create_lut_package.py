#!/usr/bin/env python3
"""Generate, validate, preview and package one reproducible creative LUT."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile
import zipfile

from generate_cube_lut import LOOKS, add_look_controls, build_params, validate_params, write_cube
from validate_lut import parse_cube, analyze

VERSION = "5.0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_recipe(recipe: dict) -> dict:
    required = {"schema_version", "engine_version", "look", "size", "strength", "title", "protect_skin", "params", "working_space", "description"}
    if not isinstance(recipe, dict) or set(recipe) != required:
        raise ValueError("Recipe has missing or unsupported fields.")
    if recipe["schema_version"] != 1 or recipe["engine_version"] != VERSION or recipe["working_space"] != "sRGB":
        raise ValueError("Recipe requires the v5 sRGB creative engine.")
    if recipe["look"] not in LOOKS or type(recipe["size"]) is not int or not 2 <= recipe["size"] <= 128:
        raise ValueError("Invalid recipe look or size.")
    if type(recipe["strength"]) not in (int, float) or not math.isfinite(recipe["strength"]) or not 0 <= recipe["strength"] <= 1:
        raise ValueError("Invalid recipe strength.")
    if type(recipe["protect_skin"]) is not bool or not all(isinstance(recipe[k], str) for k in ("title", "description")):
        raise ValueError("Invalid recipe title, description or skin protection flag.")
    if not isinstance(recipe["params"], dict) or set(recipe["params"]) != set(LOOKS["neutral"]):
        raise ValueError("Recipe parameters are incomplete or unsupported.")
    params = recipe["params"]
    for key in ("shadow_tint", "mid_tint", "highlight_tint"):
        if not isinstance(params[key], (list, tuple)) or len(params[key]) != 3 or any(type(v) not in (int, float) for v in params[key]):
            raise ValueError(f"Invalid recipe {key}.")
        params[key] = tuple(params[key])
    for key in set(params) - {"shadow_tint", "mid_tint", "highlight_tint"}:
        if type(params[key]) not in (int, float):
            raise ValueError(f"Invalid numeric recipe parameter: {key}.")
    validate_params(params)
    return recipe


def recipe_from_args(args) -> dict:
    if args.recipe:
        controls = ("contrast", "saturation", "warmth", "exposure", "lift", "curve", "bleach", "shadow_tint", "mid_tint", "highlight_tint", "size", "strength", "title", "description")
        if args.no_protect_skin or any(getattr(args, k) is not None for k in controls):
            raise ValueError("Recipe replay cannot be combined with look overrides; edit a copy of the recipe for a new variation.")
        return validate_recipe(json.loads(Path(args.recipe).read_text(encoding="utf-8-sig")))
    args.look = args.look or "cinematic-teal-orange"
    return validate_recipe({"schema_version": 1, "engine_version": VERSION, "look": args.look,
        "size": args.size if args.size is not None else 33,
        "strength": args.strength if args.strength is not None else 0.65,
        "title": args.title or args.look, "protect_skin": not args.no_protect_skin,
        "params": build_params(args), "working_space": "sRGB", "description": args.description or ""})


def build_package(args) -> dict:
    recipe = recipe_from_args(args)
    output = Path(args.output_dir).resolve()
    archive = output.with_name(output.name + ".zip")
    if output.exists() or archive.exists():
        raise FileExistsError(f"Output folder or ZIP already exists: {output}")
    if args.max_size < 1:
        raise ValueError("--max-size must be positive.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lut-v5-", dir=output.parent) as temporary:
        stage = Path(temporary) / "package"
        stage.mkdir()
        lut = stage / "look.cube"
        write_cube(lut, recipe["size"], recipe["title"], recipe["look"], recipe["strength"], recipe["params"], recipe["protect_skin"])
        size, values, notes = parse_cube(lut)
        errors, warnings = analyze(size, values)
        if errors:
            raise ValueError("LUT failed validation: " + "; ".join(errors))
        # Re-generate from the serialized recipe, rather than trusting in-memory parameters.
        dump(stage / "recipe.json", recipe)
        replay = validate_recipe(json.loads((stage / "recipe.json").read_text(encoding="utf-8")))
        reproduced = Path(temporary) / "reproduced.cube"
        write_cube(reproduced, replay["size"], replay["title"], replay["look"], replay["strength"], replay["params"], replay["protect_skin"])
        reproduced_ok = digest(lut) == digest(reproduced)
        if not reproduced_ok:
            raise ValueError("Serialized recipe did not reproduce the LUT exactly.")
        from apply_lut_preview import apply_lut, comparison, resize_for_preview
        from image_color import open_srgb, save_srgb
        previews = []
        sources = [Path(args.input)] if args.input else []
        if not sources:
            from create_test_assets import make_neutral_ramp, make_color_checker
            make_neutral_ramp(stage / "neutral-ramp.png")
            make_color_checker(stage / "color-checker.png")
            sources = [stage / "neutral-ramp.png", stage / "color-checker.png"]
        for index, source in enumerate(sources, 1):
            before, color_info = open_srgb(source)
            before = resize_for_preview(before, args.max_size)
            # Strength has already been baked. Never apply it a second time here.
            after = apply_lut(before, size, values, 1.0)
            stem = "preview" if len(sources) == 1 else f"preview-{index}"
            save_srgb(after, stage / f"{stem}.png", format="PNG")
            save_srgb(comparison(before, after), stage / f"{stem}-comparison.png", format="PNG")
            previews.append({"source": source.name, "source_sha256": digest(source), "color_management": color_info,
                "file": f"{stem}.png", "comparison": f"{stem}-comparison.png", "size": list(after.size),
                "lut_sha256": digest(lut), "application_strength": 1.0})
        report = {"status": "PASS_WITH_WARNINGS" if warnings else "PASS", "size": size, "entries": len(values),
            "errors": errors, "warnings": warnings, "notes": notes, "recipe_reproduces_exact_lut": reproduced_ok,
            "limits": "Grid heuristics do not certify perceptual banding, skin quality or editor/device behavior."}
        dump(stage / "validation.json", report)
        manifest = {"engine_version": VERSION, "lut_file": "look.cube", "lut_sha256": digest(lut),
            "working_space": "sRGB", "preview_source": "user_image" if args.input else "synthetic_test_charts",
            "previews": previews, "quality_status": report["status"], "recipe_sha256": digest(stage / "recipe.json")}
        dump(stage / "manifest.json", manifest)
        (stage / "使用说明.txt").write_text(
            "映色 · LUT 交付包\n\nlook.cube：最终 LUT，强度已写入，默认按 100% 应用。\n"
            "preview：直接应用同一 look.cube；comparison 左原图、右效果。\n"
            "recipe.json：完整配方；可用 --recipe 重建。\nvalidation.json：结构检查及质量提示，请查看 warnings。\n"
            "工作空间：普通 8-bit sRGB 照片。未标记照片按 sRGB 假定，嵌入 ICC 的照片先转换。\n"
            "本包为创意调色，不包含 RAW 显影、Log/HDR 技术转换、颗粒或光晕。\n"
            + ("本次预览使用合成测试图，不代表真实照片的审美验收。\n" if not args.input else "")
            + "最终视觉效果仍需在目标照片或剪辑软件中确认。\n", encoding="utf-8")
        zip_stage = Path(temporary) / "package.zip"
        with zipfile.ZipFile(zip_stage, "x", zipfile.ZIP_DEFLATED) as z:
            for path in sorted(stage.iterdir()):
                z.write(path, path.name)
        with zipfile.ZipFile(zip_stage) as z:
            if z.testzip() is not None:
                raise ValueError("Package archive failed integrity check.")
        stage.rename(output)
        zip_stage.rename(archive)
    return manifest


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--look", choices=sorted(LOOKS))
    mode.add_argument("--recipe", help="Rebuild an exported recipe without overrides.")
    parser.add_argument("--output-dir", required=True, help="New delivery directory; existing outputs are preserved.")
    parser.add_argument("--input", help="Optional ordinary still photo. Otherwise use synthetic charts.")
    parser.add_argument("--size", type=int)
    parser.add_argument("--strength", type=float)
    parser.add_argument("--title")
    parser.add_argument("--description", help="Original mood description for traceability, not automatic scene analysis.")
    parser.add_argument("--max-size", type=int, default=1400)
    add_look_controls(parser)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        manifest = build_package(args)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise SystemExit(f"Could not create LUT package: {exc}") from exc
    print(f"Created {args.output_dir} and ZIP; quality={manifest['quality_status']}; previews use exported LUT at 1.0.")


if __name__ == "__main__":
    main()
