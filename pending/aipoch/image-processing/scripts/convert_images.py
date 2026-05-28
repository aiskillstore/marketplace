import argparse
import json
import pathlib

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".webp"}


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def normalize_format(value):
    value = value.lower().lstrip(".")
    if value == "jpeg":
        return "jpg"
    return value


def png_compress_level(quality):
    quality = max(1, min(100, quality))
    level = int(round((100 - quality) / 10))
    return max(0, min(9, level))


def save_image(image, dest_path, output_format, quality):
    params = {}
    fmt = output_format

    if fmt in ("jpg", "jpeg"):
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        fmt = "JPEG"
        params["quality"] = quality
        params["optimize"] = True
        params["progressive"] = True
    elif fmt == "webp":
        fmt = "WEBP"
        params["quality"] = quality
        params["method"] = 6
    elif fmt == "png":
        fmt = "PNG"
        params["optimize"] = True
        params["compress_level"] = png_compress_level(quality)
    elif fmt in ("tif", "tiff"):
        fmt = "TIFF"
        params["compression"] = "tiff_lzw"
    elif fmt == "gif":
        fmt = "GIF"
    elif fmt == "bmp":
        fmt = "BMP"

    image.save(dest_path, fmt, **params)


def main():
    parser = argparse.ArgumentParser(description="Convert and compress images using Pillow")
    parser.add_argument("--source-dir", required=True, help="Directory containing input images")
    parser.add_argument("--output-dir", required=True, help="Directory for converted images")
    parser.add_argument("--format", default="webp", help="Output format (webp, jpg, png, tiff, gif, bmp)")
    parser.add_argument("--quality", type=int, default=80, help="Quality 1-100")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source_dir).expanduser()
    output_dir = pathlib.Path(args.output_dir).expanduser()
    if not source_dir.is_dir():
        raise SystemExit("Source directory not found")

    output_format = normalize_format(args.format)

    pattern = "**/*" if args.recursive else "*"
    files = [p for p in source_dir.glob(pattern) if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

    converted = 0
    skipped = 0
    errors = 0

    for src in files:
        rel_path = src.relative_to(source_dir)
        dest = output_dir / rel_path
        dest = dest.with_suffix("." + output_format)
        ensure_dir(dest.parent)

        if dest.exists() and not args.overwrite:
            skipped += 1
            continue

        try:
            with Image.open(src) as image:
                save_image(image, dest, output_format, args.quality)
            converted += 1
        except Exception:
            errors += 1

    summary = {
        "tool": "pillow",
        "converted": converted,
        "skipped": skipped,
        "errors": errors,
        "output_dir": str(output_dir),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
