from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "ocr_config.json"
DEFAULT_CONFIG = {
    "image_path": "",
    "request": "",
    "lang": "eng",
    "tesseract_cmd": "tesseract",
}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
    ".webp",
}


def safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def ensure_config_exists() -> None:
    if CONFIG_PATH.is_file():
        return
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(DEFAULT_CONFIG, file, ensure_ascii=False, indent=2)


def load_config() -> dict:
    ensure_config_exists()
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        safe_print(f"Configuration file parsing failed，Check, please JSON Format: {CONFIG_PATH}")
        return DEFAULT_CONFIG.copy()
    if not isinstance(data, dict):
        safe_print(f"Configuration file content is not an object，Check, please: {CONFIG_PATH}")
        return DEFAULT_CONFIG.copy()
    merged = DEFAULT_CONFIG.copy()
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def resolve_image_path(image_path_value: str) -> Path:
    base_dir = CONFIG_PATH.parent.parent
    path = Path(image_path_value)
    if path.is_absolute():
        return path
    candidate_in_artifacts = (CONFIG_PATH.parent / path).resolve()
    if candidate_in_artifacts.is_file():
        return candidate_in_artifacts
    return (base_dir / path).resolve()


def is_probable_path(text: str) -> bool:
    lowered = text.lower()
    if any(lowered.endswith(ext) for ext in IMAGE_EXTENSIONS):
        return True
    return any(token in text for token in (":\\", ":/", "\\", "/"))


def extract_image_path_from_request(request: str) -> str:
    cleaned = request.strip()
    if not cleaned:
        return ""
    patterns = [
        "Interpretation of \\s*['\\\"]?(?P<path>.+?)['\\\"]?\\s*(?:'s)?picture",
        "Identify \\s*['\\\"]?(?P<path>.+?)['\\\"]?\\s*(?:'s)?picture",
        "OCR\\s*['\\\"]?(?P<path>.+?)['\\\"]?\\s*(?:picture)?",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return match.group("path").strip()
    candidate = cleaned.strip().strip('"').strip("'")
    if is_probable_path(candidate):
        return candidate
    return ""


def main() -> int:
    configure_console()
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        safe_print("Dependent libraries are missing, please install Pillow and pytesseract first.")
        return 5

    config = load_config()
    image_path_value = str(config.get("image_path", "")).strip()
    request_text = str(config.get("request", "")).strip()
    if not image_path_value and request_text:
        image_path_value = extract_image_path_from_request(request_text)

    if not image_path_value:
        safe_print(f"Please set it in the configuration file image_path or request: {CONFIG_PATH}")
        return 2

    path = resolve_image_path(image_path_value)
    if not path.is_file():
        safe_print(f"Picture does not exist: {path}")
        return 2

    tesseract_cmd = str(config.get("tesseract_cmd", "tesseract")).strip() or "tesseract"
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    lang = str(config.get("lang", "eng")).strip() or "eng"
    try:
        image = Image.open(path)
    except OSError as exc:
        safe_print(f"Image reading failed：{exc}")
        return 2

    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError:
        safe_print(f"not found {tesseract_cmd}，English PATH。")
        return 3
    except pytesseract.TesseractError as exc:
        safe_print(f"OCR Execution failed：{exc}")
        return 4

    if text.strip():
        safe_print(text.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
