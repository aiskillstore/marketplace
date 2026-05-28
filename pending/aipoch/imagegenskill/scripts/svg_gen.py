import hashlib
import json
import math
import os
import random
import time


# ===================== Configuration area (modify as needed) =====================
PROMPT_FILE = "input/brief.txt"
DEFAULT_PROMPT = "Scientific research visualization poster: multi-scale network, latent space terrain, spectral texture"
OUTPUT_DIR = "output/svggen"
STYLE = "lab-atlas"  # Optional: lab-atlas/signal-loom/lattice-field
CANVAS_WIDTH = 1400
CANVAS_HEIGHT = 900
EXPORT_LATEST_NAME = "latest.svg"
# ===========================================================


STYLE_PRESETS = {
    "lab-atlas": {
        "grid_step": 40,
        "band_count": 4,
        "node_count": 80,
        "ring_density": 1.0,
        "noise_points": 260,
    },
    "signal-loom": {
        "grid_step": 55,
        "band_count": 7,
        "node_count": 55,
        "ring_density": 1.2,
        "noise_points": 360,
    },
    "lattice-field": {
        "grid_step": 32,
        "band_count": 3,
        "node_count": 110,
        "ring_density": 0.8,
        "noise_points": 220,
    },
}


def read_prompt(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        return text if text else DEFAULT_PROMPT
    return DEFAULT_PROMPT


def seed_from_text(text):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16), digest


def clamp(value, low, high):
    return max(low, min(high, value))


def hsl_to_rgb(h, s, l):
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255),
    )


def hsl_to_hex(h, s, l):
    r, g, b = hsl_to_rgb(h, s, l)
    return f"#{r:02x}{g:02x}{b:02x}"


def split_lines(text, max_len):
    if " " in text:
        words = text.split()
        lines = []
        current = []
        length = 0
        for word in words:
            if length + len(word) + (1 if current else 0) > max_len:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + (1 if current else 0)
        if current:
            lines.append(" ".join(current))
        return lines
    lines = []
    for i in range(0, len(text), max_len):
        lines.append(text[i : i + max_len])
    return lines


def build_palette(seed):
    base = seed % 360
    return [
        hsl_to_hex(base, 0.68, 0.55),
        hsl_to_hex((base + 35) % 360, 0.58, 0.42),
        hsl_to_hex((base + 210) % 360, 0.52, 0.30),
        hsl_to_hex((base + 120) % 360, 0.40, 0.68),
        hsl_to_hex((base + 280) % 360, 0.45, 0.52),
    ]


def build_wave_path(width, height, rng, y_base, amplitude, frequency, phase, step=35):
    parts = [f"M 0 {y_base:.1f}"]
    for x in range(0, width + step, step):
        y = (
            y_base
            + amplitude * math.sin(frequency * x + phase)
            + 0.35 * amplitude * math.sin(frequency * 2.2 * x + phase * 0.7)
        )
        parts.append(f"L {x:.1f} {y:.1f}")
    return " ".join(parts)


def glyph_polygon(cx, cy, size, angle):
    p1 = (cx + size * math.cos(angle), cy + size * math.sin(angle))
    p2 = (cx + size * math.cos(angle + 2.1), cy + size * math.sin(angle + 2.1))
    p3 = (cx + size * math.cos(angle + 4.2), cy + size * math.sin(angle + 4.2))
    return f"{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"


def build_svg(prompt, seed, digest, width, height, style):
    rng = random.Random(seed)
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["lab-atlas"])
    palette = build_palette(seed)

    grid_step = preset["grid_step"]
    band_count = preset["band_count"]
    node_count = preset["node_count"]
    ring_density = preset["ring_density"]
    noise_points = preset["noise_points"]

    background = hsl_to_hex((seed + 200) % 360, 0.18, 0.96)
    accent = palette[0]
    secondary = palette[1]
    deep = palette[2]

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    lines.append("<defs>")
    lines.append(
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{background}"/>'
        f'<stop offset="100%" stop-color="{palette[3]}"/>'
        f"</linearGradient>"
    )
    lines.append(
        "<style>"
        "text{font-family:'IBM Plex Sans','Noto Sans CJK SC','Source Han Sans SC',sans-serif;}"
        "</style>"
    )
    lines.append("</defs>")
    lines.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="url(#bg)"/>')

    for y in range(0, height + 1, grid_step):
        lines.append(
            f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{deep}" stroke-opacity="0.08" stroke-width="1"/>'
        )
    for x in range(0, width + 1, grid_step):
        lines.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{deep}" stroke-opacity="0.05" stroke-width="1"/>'
        )

    for i in range(band_count):
        amplitude = rng.uniform(16, 36)
        frequency = rng.uniform(0.0025, 0.006)
        phase = rng.uniform(0, math.pi * 2)
        y_base = height * (0.18 + 0.14 * i) + rng.uniform(-16, 16)
        path = build_wave_path(width, height, rng, y_base, amplitude, frequency, phase)
        color = palette[(i + 1) % len(palette)]
        lines.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-opacity="0.35" stroke-width="2"/>'
        )

    nodes = []
    for _ in range(node_count):
        x = clamp(rng.gauss(width * 0.55, width * 0.18), 90, width - 90)
        y = clamp(rng.gauss(height * 0.52, height * 0.18), 90, height - 110)
        nodes.append((x, y))

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            dx = x1 - x2
            dy = y1 - y2
            dist = math.hypot(dx, dy)
            if dist < 155:
                opacity = clamp(0.25 - dist / 700, 0.05, 0.2)
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="{secondary}" stroke-opacity="{opacity:.3f}" stroke-width="1.2"/>'
                )

    for x, y in nodes:
        radius = rng.uniform(2.2, 4.6)
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}" fill="{accent}" fill-opacity="0.75"/>'
        )

    center_x, center_y = width * 0.22, height * 0.62
    ring_radius = min(width, height) * 0.28
    prompt_chars = [c for c in prompt if not c.isspace()]
    max_chars = max(1, int(len(prompt_chars) * ring_density))
    ring_chars = prompt_chars[:max_chars]
    for idx, ch in enumerate(ring_chars):
        angle = 2 * math.pi * idx / max_chars - math.pi / 2
        radius_variation = ring_radius + rng.uniform(-18, 22)
        cx = center_x + radius_variation * math.cos(angle)
        cy = center_y + radius_variation * math.sin(angle)
        size = 7 + (ord(ch) % 7)
        lines.append(
            f'<polygon points="{glyph_polygon(cx, cy, size, angle)}" fill="{palette[4]}" fill-opacity="0.7"/>'
        )

    for _ in range(noise_points):
        x = rng.uniform(40, width - 40)
        y = rng.uniform(40, height - 40)
        r = rng.uniform(0.6, 1.8)
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{deep}" fill-opacity="0.12"/>'
        )

    panel_x = width - 380
    panel_y = height - 240
    panel_w = 330
    panel_h = 190
    lines.append(
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14" '
        f'fill="#ffffff" fill-opacity="0.78" stroke="{deep}" stroke-opacity="0.2" stroke-width="1.2"/>'
    )

    text_x = panel_x + 18
    text_y = panel_y + 30
    lines.append(f'<text x="{text_x}" y="{text_y}" font-size="16" fill="{deep}">MODE: {style}</text>')
    lines.append(f'<text x="{text_x}" y="{text_y + 22}" font-size="12" fill="{deep}">SEED: {seed}</text>')
    lines.append(
        f'<text x="{text_x}" y="{text_y + 42}" font-size="12" fill="{deep}">HASH: {digest[:10]}</text>'
    )

    prompt_lines = split_lines(prompt, 18)[:6]
    y_cursor = text_y + 70
    lines.append(f'<text x="{text_x}" y="{y_cursor}" font-size="12" fill="{deep}">PROMPT:</text>')
    for line in prompt_lines:
        y_cursor += 16
        lines.append(f'<text x="{text_x}" y="{y_cursor}" font-size="12" fill="{deep}">{line}</text>')

    bar_x = panel_x + 18
    bar_y = panel_y + panel_h - 24
    for i in range(26):
        bar_h = 4 + (ord(digest[i]) % 9)
        lines.append(
            f'<rect x="{bar_x + i * 10}" y="{bar_y - bar_h}" width="6" height="{bar_h}" '
            f'fill="{accent}" fill-opacity="0.55"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines), palette


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def main():
    prompt = read_prompt(PROMPT_FILE)
    seed, digest = seed_from_text(prompt)
    svg_text, palette = build_svg(prompt, seed, digest, CANVAS_WIDTH, CANVAS_HEIGHT, STYLE)

    ensure_dir(OUTPUT_DIR)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"svggen_{timestamp}_{seed}.svg"
    output_path = os.path.join(OUTPUT_DIR, filename)
    latest_path = os.path.join(OUTPUT_DIR, EXPORT_LATEST_NAME)
    meta_path = os.path.join(OUTPUT_DIR, f"svggen_{timestamp}_{seed}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_text)
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(svg_text)

    metadata = {
        "prompt": prompt,
        "seed": seed,
        "hash": digest,
        "style": STYLE,
        "width": CANVAS_WIDTH,
        "height": CANVAS_HEIGHT,
        "palette": palette,
        "output": output_path.replace("\\", "/"),
        "latest": latest_path.replace("\\", "/"),
        "timestamp": timestamp,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
