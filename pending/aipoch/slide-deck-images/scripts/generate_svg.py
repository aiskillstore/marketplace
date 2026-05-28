from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

# Configuration area
OUTLINE_PATH = Path("outline.md")
PROMPTS_DIR = Path("prompts")
OUTPUT_DIR = Path("slides-svg")
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
TITLE_SIZE = 64
BODY_SIZE = 36
LINE_HEIGHT = 52
FONT_FAMILY = "Noto Sans CJK SC, Microsoft YaHei, sans-serif"
BACKGROUND_COLOR = "#FAF7F2"
ACCENT_COLOR = "#F3C7A6"
TEXT_COLOR = "#2A2A2A"


def slugify(text: str) -> str:
    ascii_text = re.sub(r"[^a-zA-Z0-9\\s-]", "", text).strip().lower()
    ascii_text = re.sub(r"\\s+", "-", ascii_text)
    return ascii_text[:30] if ascii_text else "slide"


def extract_title_and_bullets(text: str) -> tuple[str, list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = "Untitled"
    bullets: list[str] = []

    for line in lines:
        if line.lower().startswith(("headline:", "title:", "#", "##")):
            title = re.sub(r"^(headline:|title:|#+)\\s*", "", line, flags=re.I).strip()
            break
    else:
        title = lines[0] if lines else "Untitled"

    for line in lines:
        if line.startswith(("-", "*")):
            bullets.append(line.lstrip("-* ").strip())
    if not bullets:
        for line in lines[1:]:
            if len(bullets) >= 4:
                break
            if len(line) > 6:
                bullets.append(line[:80])

    return title, bullets[:4]


def parse_outline_sections(text: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    parts = re.split(r"^##\\s+Slide\\s+\\d+\\s+of\\s+\\d+\\s*$", text, flags=re.M)
    for part in parts[1:]:
        title = "Untitled"
        bullets: list[str] = []
        for line in part.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("headline:"):
                title = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- "):
                bullets.append(stripped[2:].strip())
        sections.append((title, bullets[:4]))
    return sections


def render_svg(title: str, bullets: list[str]) -> str:
    bullet_lines = ""
    y = 280
    for item in bullets:
        bullet_lines += (
            f'<text x="160" y="{y}" font-size="{BODY_SIZE}" '
            f'fill="{TEXT_COLOR}" font-family="{FONT_FAMILY}">• {escape_xml(item)}</text>\\n'
        )
        y += LINE_HEIGHT

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">
<rect width="100%" height="100%" fill="{BACKGROUND_COLOR}"/>
<rect x="0" y="0" width="100%" height="120" fill="{ACCENT_COLOR}"/>
<text x="120" y="88" font-size="{TITLE_SIZE}" fill="{TEXT_COLOR}" font-family="{FONT_FAMILY}" font-weight="700">{escape_xml(title)}</text>
{bullet_lines}
<text x="120" y="{CANVAS_HEIGHT - 80}" font-size="24" fill="{TEXT_COLOR}" font-family="{FONT_FAMILY}">Slide Deck SVG</text>
</svg>
"""


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def load_slides() -> list[tuple[str, list[str]]]:
    if PROMPTS_DIR.exists():
        prompt_files = sorted(PROMPTS_DIR.glob("*.md"))
        if prompt_files:
            slides: list[tuple[str, list[str]]] = []
            for path in prompt_files:
                text = path.read_text(encoding="utf-8")
                slides.append(extract_title_and_bullets(text))
            return slides

    if OUTLINE_PATH.exists():
        outline_text = OUTLINE_PATH.read_text(encoding="utf-8")
        sections = parse_outline_sections(outline_text)
        if sections:
            return sections

    raise FileNotFoundError("Prompts/ or outline.md not found, please generate outline/prompts first.")


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def backup_if_exists(path: Path) -> None:
    if not path.exists():
        return
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}-backup-{timestamp}{path.suffix}")
    path.rename(backup)


def main() -> None:
    slides = load_slides()
    ensure_output_dir()

    for idx, (title, bullets) in enumerate(slides, start=1):
        slug = slugify(title)
        filename = f"{idx:02d}-slide-{slug}.svg"
        out_path = OUTPUT_DIR / filename
        backup_if_exists(out_path)
        svg = render_svg(title, bullets)
        out_path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
