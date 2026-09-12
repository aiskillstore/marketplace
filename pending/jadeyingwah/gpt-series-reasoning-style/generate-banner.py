#!/usr/bin/env python3
"""Generate the GitHub social preview (1280x640) for GPT-Series Reasoning Style.

Run:  python generate-banner.py
Output: social-preview.png next to this script.

同步关系（2026-09-11 如实更正）：`social-preview.svg` 与本品视觉同款，但它把**文字全部
转成了路径轮廓**（全篇 14 个 `<path>`、零 `<text>` 节点），因此文案**无法被机器比对**——
改了本文件的文案，SVG 会静默分叉，任何自动检查都发现不了。故：本文件是文案的**权威源**，
SVG 属于需人工重新导出的冻结产物；改文案后必须同步重新导出 SVG，不得假设它会自动跟上。
English uses Segoe UI; Chinese uses Microsoft YaHei (with Noto/SimHei fallback).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1280, 640
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- palette -------------------------------------------------------------
BG_TOP = (11, 16, 32)        # #0B1020
BG_BOTTOM = (23, 18, 51)     # #171233
INK = (248, 250, 252)        # #F8FAFC title
SUB_ZH = (196, 181, 253)     # #C4B5FD
TAG_EN = (226, 232, 240)     # #E2E8F0
TAG_ZH = (148, 163, 184)     # #94A3B8
EYEBROW = (34, 211, 238)     # #22D3EE
FOOTER = (100, 116, 139)     # #64748B
CHIP_FILL = (19, 26, 49)     # #131A31
CHIP_TEXT = (241, 245, 249)  # #F1F5F9
PURPLE, CYAN, AMBER, GREEN = (139, 92, 246), (6, 182, 212), (245, 158, 11), (16, 185, 129)


def _first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _version():
    """Read the version from the VERSION file (the single source of truth).

    A hardcoded footer version would silently go stale when VERSION bumps
    (same defect family as stale version references in host memories).
    """
    try:
        with open(os.path.join(HERE, "VERSION"), encoding="utf-8") as fh:
            v = fh.read().strip()
        return v if v else "?"
    except OSError:
        return "?"


def font(size, bold=False, cjk=False):
    """Load a truetype font. CJK text must use a Chinese-capable face.

    Windows-first candidate chain; falls back to macOS/Linux system fonts so
    the maintainer tool does not silently render CJK as tofu boxes elsewhere.
    """
    win = r"C:\Windows\Fonts"
    if cjk:
        candidates = [
            os.path.join(win, "msyhbd.ttc" if bold else "msyh.ttc"),
            os.path.join(win, "NotoSansSC-VF.ttf"),
            os.path.join(win, "simhei.ttf"),
            # macOS CJK
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            # Linux CJK (Noto CJK / WenQuanYi)
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        if bold:
            candidates.insert(0, "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
    else:
        candidates = [
            os.path.join(win, "segoeuib.ttf" if bold else "segoeui.ttf"),
            os.path.join(win, "arialbd.ttf" if bold else "arial.ttf"),
            os.path.join(win, "msyhbd.ttc" if bold else "msyh.ttc"),
            # macOS / Linux Latin
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    path = _first_existing(candidates)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    if cjk:
        # M4: silent CJK tofu is worse than a loud warning.
        print('WARNING: no CJK font found — output will contain unreadable glyphs',
              file=sys.stderr)
    return ImageFont.load_default()


def main():
    f_eye = font(22, bold=True)
    f_title = font(82, bold=True)
    f_sub_zh = font(40, bold=True, cjk=True)
    f_tag_en = font(30, bold=True)
    f_tag_zh = font(23, cjk=True)
    f_chip_zh = font(24, bold=True, cjk=True)
    f_chip_en = font(18)
    f_footer = font(19)

    # ---- background gradient -------------------------------------------------
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)),
        )

    # ---- soft glows (blurred so edges are not hard) --------------------------
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([920, -120, 1320, 280], fill=(124, 58, 237, 34))
    gdraw.ellipse([-120, 360, 360, 780], fill=(6, 182, 212, 24))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)


    def text_width(d, text, ft):
        bbox = d.textbbox((0, 0), text, font=ft)
        return bbox[2] - bbox[0]      # 与 center_text 同口径：含左伸（overhang）修正


    def center_text(d, cx, y, text, ft, fill):
        bbox = d.textbbox((0, 0), text, font=ft)
        w = bbox[2] - bbox[0]
        d.text((cx - w / 2 - bbox[0], y), text, font=ft, fill=fill)


    def tracked_text(d, cx, y, text, ft, fill, tracking=4):
        widths = [ft.getlength(ch) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=ft, fill=fill)
            x += w + tracking


    # ---- eyebrow + titles ----------------------------------------------------
    tracked_text(draw, WIDTH / 2, 62, "AGENT SKILL · BEHAVIOR OVERLAY", f_eye, EYEBROW, tracking=4)

    # title with a soft shadow
    title = "GPT-Series Reasoning Style"
    tw = text_width(draw, title, f_title)
    tx = (WIDTH - tw) / 2
    ty = 104
    draw.text((tx + 2, ty + 3), title, font=f_title, fill=(2, 6, 23))
    draw.text((tx, ty), title, font=f_title, fill=INK)

    center_text(draw, WIDTH / 2, 208, "GPT 系列推理风格", f_sub_zh, SUB_ZH)
    center_text(draw, WIDTH / 2, 276, "Gate before code · Evidence before claims", f_tag_en, TAG_EN)
    center_text(draw, WIDTH / 2, 322, "先确认再动手 · 先证据再结论 · 真实环境才验收", f_tag_zh, TAG_ZH)

    # ---- three capability chips ---------------------------------------------
    chips = [
        ("实现前门禁", "Pre-Implementation Gate", PURPLE),
        ("一条主干+两扩展", "1 Backbone + 2 Extensions", CYAN),
        ("证据与实操验收", "Evidence & Hands-On", AMBER),
    ]
    chip_w, chip_h, gap = 272, 100, 26
    total_w = len(chips) * chip_w + (len(chips) - 1) * gap
    x0 = (WIDTH - total_w) / 2
    chip_y = 416
    for i, (zh, en, color) in enumerate(chips):
        x1 = x0 + i * (chip_w + gap)
        box = [x1, chip_y, x1 + chip_w, chip_y + chip_h]
        draw.rounded_rectangle(box, radius=18, fill=CHIP_FILL, outline=color, width=2)
        cx = x1 + chip_w / 2
        center_text(draw, cx, chip_y + 22, zh, f_chip_zh, CHIP_TEXT)
        center_text(draw, cx, chip_y + 64, en, f_chip_en, color)

    # ---- footer (fixed page margins, independent of chip count) --------------
    MARGIN = 57
    draw.text((MARGIN, 596), "Planning · Execution · Review", font=f_footer, fill=FOOTER)
    foot_r = "v{} · MIT".format(_version())
    fw = text_width(draw, foot_r, f_footer)
    draw.text((WIDTH - MARGIN - fw, 596), foot_r, font=f_footer, fill=FOOTER)

    out = os.path.join(HERE, "social-preview.png")
    img.save(out, "PNG")
    print(f"Saved banner to {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
