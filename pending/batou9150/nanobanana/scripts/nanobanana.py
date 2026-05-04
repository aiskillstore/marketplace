#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0"]
# ///
"""nanobanana: Gemini image-generation CLI for the Claude Agent Skill.

Subcommands: generate | edit | restore | icon | pattern | story | diagram

Self-contained via PEP 723 inline metadata: `uv run` reads the header above
and provisions a cached ephemeral environment with `google-genai` on first
invocation. No manual venv / pip install required.
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import subprocess
import sys
from pathlib import Path

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = Path("nanobanana-output")
API_KEY_VARS = (
    "NANOBANANA_API_KEY",
    "NANOBANANA_GEMINI_API_KEY",
    "NANOBANANA_GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)
SEARCH_DIRS = [
    Path.cwd(),
    Path.cwd() / "images",
    Path.cwd() / "input",
    Path.cwd() / OUTPUT_DIR,
    Path.home() / "Downloads",
    Path.home() / "Desktop",
]
VARIATION_SUFFIXES = {
    "lighting": ["dramatic lighting", "soft lighting"],
    "angle": ["from above", "close-up view"],
    "color-palette": ["warm color palette", "cool color palette"],
    "composition": ["centered composition", "rule of thirds composition"],
    "mood": ["cheerful mood", "dramatic mood"],
    "season": ["in spring", "in winter"],
    "time-of-day": ["at sunrise", "at sunset"],
}


def get_api_key() -> str:
    for var in API_KEY_VARS:
        v = os.environ.get(var)
        if v:
            return v
    raise SystemExit(
        "ERROR: No API key found. Set NANOBANANA_API_KEY (preferred) or one of: "
        + ", ".join(API_KEY_VARS[1:])
        + ". Get a key at https://aistudio.google.com/apikey"
    )


def get_client() -> genai.Client:
    return genai.Client(api_key=get_api_key())


def model_name() -> str:
    return os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9\s]", "", text.lower())
    s = re.sub(r"\s+", "_", s).strip("_")[:32]
    return s or "generated_image"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def unique_path(base: str, ext: str = "png") -> Path:
    out = ensure_output_dir()
    fname = f"{base}.{ext}"
    counter = 1
    while (out / fname).exists():
        fname = f"{base}_{counter}.{ext}"
        counter += 1
    return out / fname


def find_input(name: str) -> Path:
    p = Path(name)
    if p.is_absolute() and p.exists():
        return p
    for d in SEARCH_DIRS:
        candidate = d / name
        if candidate.exists():
            return candidate
    raise SystemExit(
        f"ERROR: Input image '{name}' not found. Searched: "
        + ", ".join(str(d) for d in SEARCH_DIRS)
    )


def open_preview(path: Path) -> None:
    if sys.platform == "darwin":
        cmd = ["open", str(path)]
    elif sys.platform.startswith("win"):
        cmd = ["cmd", "/c", "start", "", str(path)]
    else:
        cmd = ["xdg-open", str(path)]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"  preview failed: {e}", file=sys.stderr)


MIME_TO_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}


def extract_images(response) -> list[tuple[bytes, str]]:
    """Return list of (raw_bytes, file_extension) tuples."""
    out: list[tuple[bytes, str]] = []
    parts = getattr(response, "parts", None)
    if not parts and getattr(response, "candidates", None):
        content = response.candidates[0].content
        parts = getattr(content, "parts", None) or []
    for part in parts or []:
        inline = getattr(part, "inline_data", None)
        data = getattr(inline, "data", None) if inline else None
        if not data:
            continue
        mime = (getattr(inline, "mime_type", None) or "image/png").lower()
        ext = MIME_TO_EXT.get(mime, "png")
        if isinstance(data, str):
            try:
                out.append((base64.b64decode(data), ext))
            except Exception:
                continue
        else:
            out.append((bytes(data), ext))
    return out


def save_image(data: bytes, base: str, ext: str = "png") -> Path:
    path = unique_path(slugify(base), ext)
    path.write_bytes(data)
    return path


def call_model(client: genai.Client, prompt: str, image_path: Path | None = None):
    contents: list = [prompt]
    if image_path:
        mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        contents.append(
            types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime)
        )
    return client.models.generate_content(model=model_name(), contents=contents)


def build_batch_prompts(prompt: str, count: int, styles, variations) -> list[str]:
    prompts: list[str] = []
    if styles:
        prompts.extend(f"{prompt}, {s} style" for s in styles)
    if variations:
        base = prompts or [prompt]
        expanded: list[str] = []
        for p in base:
            for v in variations:
                for suffix in VARIATION_SUFFIXES.get(v, []):
                    expanded.append(f"{p}, {suffix}")
        if expanded:
            prompts = expanded
    if not prompts:
        prompts = [prompt] * max(1, count)
    if count and len(prompts) > count:
        prompts = prompts[:count]
    return prompts


def cmd_generate(args):
    client = get_client()
    prompts = build_batch_prompts(args.prompt, args.count, args.styles, args.variations)
    print(f"-> generating {len(prompts)} image(s) with {model_name()}", file=sys.stderr)
    saved: list[Path] = []
    for i, p in enumerate(prompts, 1):
        try:
            response = call_model(client, p)
        except Exception as e:
            print(f"  [{i}/{len(prompts)}] FAIL: {e}", file=sys.stderr)
            continue
        for data, ext in extract_images(response):
            path = save_image(data, p, ext)
            saved.append(path)
            print(f"  [{i}/{len(prompts)}] {path}", file=sys.stderr)
            break
    if not saved:
        raise SystemExit("ERROR: no images generated")
    if args.preview:
        for p in saved:
            open_preview(p)
    for p in saved:
        print(p)


def _edit_or_restore(args, mode: str):
    client = get_client()
    src = find_input(args.file)
    print(f"-> {mode} {src} with {model_name()}", file=sys.stderr)
    response = call_model(client, args.prompt, src)
    images = extract_images(response)
    if not images:
        raise SystemExit("ERROR: no image data in response")
    data, ext = images[0]
    path = save_image(data, f"{mode}_{args.prompt}", ext)
    if args.preview:
        open_preview(path)
    print(path)


def cmd_edit(args):
    _edit_or_restore(args, "edit")


def cmd_restore(args):
    _edit_or_restore(args, "restore")


def build_icon_prompt(args) -> str:
    parts = [args.prompt, f"{args.style} style {args.type}"]
    if args.type == "app-icon":
        parts.append(f"{args.corners} corners")
    if args.background != "transparent":
        parts.append(f"{args.background} background")
    parts.extend(["clean design", "high quality", "professional"])
    return ", ".join(parts)


def cmd_icon(args):
    client = get_client()
    base_prompt = build_icon_prompt(args)
    sizes = args.sizes or [256]
    saved: list[Path] = []
    print(f"-> icon: {base_prompt} | sizes={sizes}", file=sys.stderr)
    for size in sizes:
        sized = f"{base_prompt}, {size}x{size}px"
        try:
            response = call_model(client, sized)
        except Exception as e:
            print(f"  size {size}: FAIL: {e}", file=sys.stderr)
            continue
        for data, detected_ext in extract_images(response):
            # Honor user --format override; otherwise use detected mime
            ext = "jpg" if args.format == "jpeg" else detected_ext
            path = save_image(data, f"{args.prompt}_{size}", ext)
            saved.append(path)
            print(f"  {path}", file=sys.stderr)
            break
    if not saved:
        raise SystemExit("ERROR: no icons generated")
    if args.preview:
        for p in saved:
            open_preview(p)
    for p in saved:
        print(p)


def build_pattern_prompt(args) -> str:
    parts = [
        args.prompt,
        f"{args.style} style {args.type} pattern",
        f"{args.density} density",
        f"{args.colors} colors",
    ]
    if args.type == "seamless":
        parts.extend(["tileable", "repeating pattern"])
    parts.extend([f"{args.size} tile size", "high quality"])
    return ", ".join(parts)


def cmd_pattern(args):
    client = get_client()
    prompt = build_pattern_prompt(args)
    print(f"-> pattern: {prompt}", file=sys.stderr)
    response = call_model(client, prompt)
    images = extract_images(response)
    if not images:
        raise SystemExit("ERROR: no pattern generated")
    data, ext = images[0]
    path = save_image(data, args.prompt, ext)
    if args.preview:
        open_preview(path)
    print(path)


def cmd_story(args):
    client = get_client()
    type_suffix = {
        "story": f"narrative sequence, {args.style} art style",
        "process": "procedural step, instructional illustration",
        "tutorial": "tutorial step, educational diagram",
        "timeline": "chronological progression, timeline visualization",
    }[args.type]
    saved: list[Path] = []
    print(f"-> story: {args.steps} step(s), type={args.type}", file=sys.stderr)
    for i in range(1, args.steps + 1):
        step_prompt = f"{args.prompt}, step {i} of {args.steps}, {type_suffix}"
        if i > 1:
            step_prompt += f", {args.transition} transition from previous step"
        try:
            response = call_model(client, step_prompt)
        except Exception as e:
            print(f"  step {i}: FAIL: {e}", file=sys.stderr)
            continue
        for data, ext in extract_images(response):
            path = save_image(data, f"{args.type}_step{i}_{args.prompt}", ext)
            saved.append(path)
            print(f"  step {i}: {path}", file=sys.stderr)
            break
    if not saved:
        raise SystemExit("ERROR: story generation failed")
    if args.preview:
        for p in saved:
            open_preview(p)
    for p in saved:
        print(p)


def build_diagram_prompt(args) -> str:
    return ", ".join([
        args.prompt,
        f"{args.type} diagram",
        f"{args.style} style",
        f"{args.layout} layout",
        f"{args.complexity} level of detail",
        f"{args.colors} color scheme",
        f"{args.annotations} annotations and labels",
        "clean technical illustration",
        "clear visual hierarchy",
    ])


def cmd_diagram(args):
    client = get_client()
    prompt = build_diagram_prompt(args)
    print(f"-> diagram: {prompt}", file=sys.stderr)
    response = call_model(client, prompt)
    images = extract_images(response)
    if not images:
        raise SystemExit("ERROR: no diagram generated")
    data, ext = images[0]
    path = save_image(data, args.prompt, ext)
    if args.preview:
        open_preview(path)
    print(path)


def csv_str(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def csv_int(value: str) -> list[int]:
    return [int(v) for v in csv_str(value)]


def main():
    p = argparse.ArgumentParser(prog="nanobanana", description="Gemini image-generation CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Text-to-image (single or batched)")
    g.add_argument("prompt")
    g.add_argument("--count", type=int, default=1)
    g.add_argument("--styles", type=csv_str, help="Comma-separated: photorealistic,watercolor,oil-painting,sketch,pixel-art,anime,vintage,modern,abstract,minimalist")
    g.add_argument("--variations", type=csv_str, help="Comma-separated: lighting,angle,color-palette,composition,mood,season,time-of-day")
    g.add_argument("--seed", type=int)
    g.add_argument("--preview", action="store_true")
    g.set_defaults(func=cmd_generate)

    e = sub.add_parser("edit", help="Edit existing image")
    e.add_argument("file")
    e.add_argument("prompt")
    e.add_argument("--preview", action="store_true")
    e.set_defaults(func=cmd_edit)

    r = sub.add_parser("restore", help="Restore / enhance image")
    r.add_argument("file")
    r.add_argument("prompt")
    r.add_argument("--preview", action="store_true")
    r.set_defaults(func=cmd_restore)

    ic = sub.add_parser("icon", help="App icon, favicon, UI element")
    ic.add_argument("prompt")
    ic.add_argument("--sizes", type=csv_int, help="e.g. 16,32,64,128,256,512,1024")
    ic.add_argument("--type", choices=["app-icon", "favicon", "ui-element"], default="app-icon")
    ic.add_argument("--style", choices=["flat", "skeuomorphic", "minimal", "modern"], default="modern")
    ic.add_argument("--format", choices=["png", "jpeg"], default="png")
    ic.add_argument("--background", default="transparent")
    ic.add_argument("--corners", choices=["rounded", "sharp"], default="rounded")
    ic.add_argument("--preview", action="store_true")
    ic.set_defaults(func=cmd_icon)

    pa = sub.add_parser("pattern", help="Seamless pattern / texture")
    pa.add_argument("prompt")
    pa.add_argument("--size", default="256x256")
    pa.add_argument("--type", choices=["seamless", "texture", "wallpaper"], default="seamless")
    pa.add_argument("--style", choices=["geometric", "organic", "abstract", "floral", "tech"], default="abstract")
    pa.add_argument("--density", choices=["sparse", "medium", "dense"], default="medium")
    pa.add_argument("--colors", choices=["mono", "duotone", "colorful"], default="colorful")
    pa.add_argument("--repeat", choices=["tile", "mirror"], default="tile")
    pa.add_argument("--preview", action="store_true")
    pa.set_defaults(func=cmd_pattern)

    st = sub.add_parser("story", help="Sequential image story / process / tutorial / timeline")
    st.add_argument("prompt")
    st.add_argument("--steps", type=int, default=4)
    st.add_argument("--type", choices=["story", "process", "tutorial", "timeline"], default="story")
    st.add_argument("--style", choices=["consistent", "evolving"], default="consistent")
    st.add_argument("--transition", choices=["smooth", "dramatic", "fade"], default="smooth")
    st.add_argument("--preview", action="store_true")
    st.set_defaults(func=cmd_story)

    di = sub.add_parser("diagram", help="Flowchart / architecture / network / database / wireframe / mindmap / sequence")
    di.add_argument("prompt")
    di.add_argument("--type", choices=["flowchart", "architecture", "network", "database", "wireframe", "mindmap", "sequence"], default="flowchart")
    di.add_argument("--style", choices=["professional", "clean", "hand-drawn", "technical"], default="professional")
    di.add_argument("--layout", choices=["horizontal", "vertical", "hierarchical", "circular"], default="hierarchical")
    di.add_argument("--complexity", choices=["simple", "detailed", "comprehensive"], default="detailed")
    di.add_argument("--colors", choices=["mono", "accent", "categorical"], default="accent")
    di.add_argument("--annotations", choices=["minimal", "detailed"], default="detailed")
    di.add_argument("--preview", action="store_true")
    di.set_defaults(func=cmd_diagram)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
