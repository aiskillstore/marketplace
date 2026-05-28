from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path


# Configuration area
SAMPLE_IMAGE_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdoc/main/images/eurotext.png"
SAMPLE_IMAGE_NAME = "sample_ocr.png"
DEFAULT_LANG = "eng"
AUTO_UPDATE_CONFIG = True


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
CONFIG_PATH = ARTIFACTS_DIR / "ocr_config.json"
DEFAULT_CONFIG = {
    "image_path": "",
    "request": "",
    "lang": DEFAULT_LANG,
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


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return DEFAULT_CONFIG.copy()
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


def save_config(config: dict) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)


def print_install_hint() -> None:
    safe_print("Tesseract OCR is not detected, please complete the installation first:")
    safe_print("Prioritize getting the installation package or documentation from official channels, and check the version and completeness.")
    safe_print("After the installation is complete, please ensure that tesseract is in PATH, or set tesseract_cmd in the configuration.")


def ensure_sample_image() -> Path | None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = ARTIFACTS_DIR / SAMPLE_IMAGE_NAME
    if target_path.is_file():
        return target_path
    try:
        with urllib.request.urlopen(SAMPLE_IMAGE_URL, timeout=15) as response:
            content = response.read()
    except OSError as exc:
        safe_print(f"Failed to download sample image：{exc}")
        return None
    target_path.write_bytes(content)
    return target_path


def resolve_image_path(image_path_value: str) -> Path:
    path = Path(image_path_value)
    if path.is_absolute():
        return path
    candidate_in_artifacts = (ARTIFACTS_DIR / path).resolve()
    if candidate_in_artifacts.is_file():
        return candidate_in_artifacts
    return (REPO_ROOT / path).resolve()


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


def run_image_ocr(image_path: Path, lang: str, tesseract_cmd: str) -> int:
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        safe_print("Dependent libraries are missing, please install Pillow and pytesseract first.")
        return 5

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    try:
        image = Image.open(image_path)
    except OSError as exc:
        safe_print(f"Image reading failed：{exc}")
        return 2
    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError:
        print_install_hint()
        return 3
    except pytesseract.TesseractError as exc:
        safe_print(f"OCR Execution failed：{exc}")
        return 4

    if text.strip():
        print("OCR output:")
        safe_print(text.strip())
    return 0


def main() -> int:
    configure_console()
    config = load_config()
    tesseract_cmd = str(config.get("tesseract_cmd", "tesseract")).strip() or "tesseract"

    image_path_value = str(config.get("image_path", "")).strip()
    request_text = str(config.get("request", "")).strip()
    if not image_path_value and request_text:
        image_path_value = extract_image_path_from_request(request_text)

    image_path = resolve_image_path(image_path_value) if image_path_value else None
    if not image_path or not image_path.is_file():
        safe_print("No valid image path found, ready to download sample images.")
        sample_path = ensure_sample_image()
        if not sample_path:
            safe_print("Sample image preparation failed, please set image_path or request manually.")
            return 2
        config["image_path"] = f"artifacts/{SAMPLE_IMAGE_NAME}"
        image_path = sample_path

    lang = str(config.get("lang", "")).strip()
    if not lang:
        config["lang"] = DEFAULT_LANG

    if AUTO_UPDATE_CONFIG:
        save_config(config)
        safe_print(f"Profile updated：{CONFIG_PATH}")

    safe_print("Start the OCR process...")
    return run_image_ocr(image_path, config["lang"], tesseract_cmd)


if __name__ == "__main__":
    raise SystemExit(main())
