#!/usr/bin/env python3
"""
compose_hud.py
Cross-platform High-DPI Livestream Chrome, Interactive Popup, Bezier Heart Fountain,
Contact Sheet, Showcase Atlas, GIF, and H.264+AAC MP4 Compositor for livestream-style-video.

Reads a JSON manifest emitted by scripts/render_preview.mjs and composites:
- Multi-platform trademark-clean HUDs: douyin, kuaishou, instagram, x, tiktok, clean
- Dynamic popups: Join/Wave/Red-Heart ribbons, 2-slot Gift Combo x66 banners, Live Shopping cards,
  Instagram frosted Live Q&A cards, 1v1 PK tug-of-war score bars, Corner PiP facecams, [AF-C] brackets
- Periscope/Douyin/IG sinusoidal rising hearts
- Bilingual (.zh.png / .en.png / .png) contact sheets & showcase atlases
- Palette-optimized animated GIFs and H.264 + AAC MP4 videos via ffmpeg
"""

import json
import math
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_CANDIDATES_CJK = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]

FONT_CANDIDATES_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "C:/Windows/Fonts/consolab.ttf",
]


def load_font(size: int, mono: bool = False):
    candidates = (FONT_CANDIDATES_MONO + FONT_CANDIDATES_CJK) if mono else FONT_CANDIDATES_CJK
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_w(draw: ImageDraw.ImageDraw, txt: str, font) -> int:
    try:
        return int(math.ceil(draw.textlength(txt, font=font)))
    except Exception:
        return len(txt) * 11


def fit_text_px(draw: ImageDraw.ImageDraw, txt: str, font, max_px: int) -> str:
    txt = str(txt or "")
    if text_w(draw, txt, font) <= max_px:
        return txt
    ell = "…"
    out = txt
    while len(out) > 1 and text_w(draw, out + ell, font) > max_px:
        out = out[:-1]
    return out + ell


def draw_close_x(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color=(255, 255, 255, 235), width: int = 2):
    draw.line([(cx - r, cy - r), (cx + r, cy + r)], fill=color, width=width)
    draw.line([(cx - r, cy + r), (cx + r, cy - r)], fill=color, width=width)


def draw_heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill_rgba):
    pts = []
    for i in range(28):
        t = (i / 28.0) * math.pi * 2.0
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * (r / 16.0), cy + y * (r / 16.0)))
    draw.polygon(pts, fill=fill_rgba)


def make_scrim(w: int, h: int, top_h: int, top_alpha: int, bot_h: int, bot_alpha: int) -> Image.Image:
    scrim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = scrim.load()
    for y in range(min(top_h, h)):
        a = int(top_alpha * (1.0 - y / max(1, top_h)) ** 1.4)
        for x in range(w):
            px[x, y] = (0, 0, 0, a)
    for i in range(min(bot_h, h)):
        y = h - 1 - i
        a = int(bot_alpha * (1.0 - i / max(1, bot_h)) ** 1.35)
        for x in range(w):
            old_a = px[x, y][3]
            px[x, y] = (0, 0, 0, max(old_a, a))
    return scrim


def overlay_platform_hud(
    base_img: Image.Image,
    platform: str,
    rig: str,
    host_name: str,
    cohost_name: str,
    shot_idx: int,
    phase: float,
    lang: str = "zh",
    hud_meta: dict = None,
    pip_img: Image.Image = None,
) -> Image.Image:
    hud_meta = hud_meta or {}
    img = base_img.convert("RGBA")
    w, h = img.size
    s = w / 360.0  # Scale relative to 360x640 reference

    f_xs = load_font(max(9, int(9.5 * s)))
    f_sm = load_font(max(10, int(11 * s)))
    f_md = load_font(max(11, int(12.5 * s)))
    f_lg = load_font(max(13, int(15.5 * s)))
    f_xl = load_font(max(16, int(19 * s)))
    f_mono = load_font(max(9, int(10 * s)), mono=True)

    # Composite corner PiP facecam even in clean/HUD modes when pip_img is supplied
    if pip_img is not None and rig == "pip-facecam-rig":
        pw, ph = int(102 * s), int(136 * s)
        pip_resized = pip_img.convert("RGBA").resize((pw, ph), Image.Resampling.BILINEAR)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=int(14 * s), fill=255)
        px_pos = w - pw - int(12 * s)
        py_pos = int(94 * s) if platform != "clean" else int(18 * s)
        border_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(border_layer)
        bdraw.rounded_rectangle(
            [px_pos - int(2.5 * s), py_pos - int(2.5 * s), px_pos + pw + int(2 * s), py_pos + ph + int(2 * s)],
            radius=int(16 * s),
            fill=(15, 23, 42, 220),
            outline=(56, 189, 248, 255),
            width=max(2, int(2.5 * s)),
        )
        img = Image.alpha_composite(img, border_layer)
        img.paste(pip_resized, (px_pos, py_pos), mask)
        tag_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(tag_layer)
        tdraw.rounded_rectangle(
            [px_pos + int(8 * s), py_pos + ph - int(20 * s), px_pos + pw - int(8 * s), py_pos + ph - int(5 * s)],
            radius=int(6 * s),
            fill=(2, 6, 23, 196),
        )
        tdraw.text((px_pos + int(14 * s), py_pos + ph - int(19 * s)), "PiP CAM", font=f_mono, fill=(125, 211, 252, 255))
        img = Image.alpha_composite(img, tag_layer)

    if platform == "clean" or platform == "off":
        return img

    # Scrims for WCAG contrast
    scrim = make_scrim(w, h, int(115 * s), 125, int(245 * s), 165)
    img = Image.alpha_composite(img, scrim)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Accent palette by platform
    palettes = {
        "douyin": {"accent": (254, 44, 85, 245), "accent2": (37, 244, 238, 245), "badge": (59, 130, 246, 235)},
        "kuaishou": {"accent": (255, 80, 0, 245), "accent2": (24, 144, 255, 245), "badge": (249, 115, 22, 235)},
        "instagram": {"accent": (225, 48, 108, 245), "accent2": (131, 58, 180, 245), "badge": (225, 48, 108, 235)},
        "x": {"accent": (249, 24, 128, 245), "accent2": (29, 155, 240, 245), "badge": (53, 177, 209, 235)},
        "tiktok": {"accent": (254, 44, 85, 245), "accent2": (37, 244, 238, 245), "badge": (20, 184, 166, 235)},
    }
    pal = palettes.get(platform, palettes["douyin"])
    is_zh = lang in ("zh", "zh-tw", "zh-en")

    viewer_num = hud_meta.get("viewerCount", 14200 + shot_idx * 6300 + int(phase * 420))
    viewer_str = f"{viewer_num / 1000:.1f}K" if viewer_num >= 1000 else str(viewer_num)

    # 1. Top Header Bar
    top_y = int(16 * s)
    pad_x = int(12 * s)

    if platform == "instagram":
        # Story-ring avatar + username + magenta LIVE pill + eye viewer pill + close X
        av_r = int(15 * s)
        av_cx, av_cy = pad_x + av_r, top_y + av_r
        d.ellipse([av_cx - av_r - 2, av_cy - av_r - 2, av_cx + av_r + 2, av_cy + av_r + 2], outline=(225, 48, 108, 255), width=max(2, int(2 * s)))
        d.ellipse([av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r], fill=(56, 189, 248, 255))
        d.text((av_cx - int(4 * s), av_cy - int(7 * s)), host_name[:1].upper(), font=f_md, fill=(15, 23, 42, 255))
        d.text((av_cx + av_r + int(7 * s), top_y + int(7 * s)), f"{host_name}", font=f_md, fill=(255, 255, 255, 255))

        live_w = int(44 * s)
        rx = w - pad_x - int(24 * s) - int(62 * s) - live_w - int(10 * s)
        d.rounded_rectangle([rx, top_y + int(4 * s), rx + live_w, top_y + int(26 * s)], radius=int(5 * s), fill=(225, 48, 108, 255))
        d.text((rx + int(8 * s), top_y + int(7 * s)), "LIVE", font=f_sm, fill=(255, 255, 255, 255))

        vx = rx + live_w + int(5 * s)
        d.rounded_rectangle([vx, top_y + int(4 * s), vx + int(60 * s), top_y + int(26 * s)], radius=int(5 * s), fill=(15, 23, 42, 175))
        d.text((vx + int(8 * s), top_y + int(7 * s)), viewer_str, font=f_sm, fill=(255, 255, 255, 255))
        draw_close_x(d, w - pad_x - int(9 * s), top_y + int(15 * s), 5.5 * s, width=max(2, int(2 * s)))

    elif platform == "x":
        # X / Periscope crisp LIVE pill + watching count + @handle dark glass bar
        d.rounded_rectangle([pad_x, top_y + int(2 * s), pad_x + int(46 * s), top_y + int(25 * s)], radius=int(6 * s), fill=(239, 68, 68, 245))
        d.text((pad_x + int(9 * s), top_y + int(5 * s)), "LIVE", font=f_sm, fill=(255, 255, 255, 255))
        watch_txt = f"{viewer_str} {'正在观看' if is_zh else 'watching'}"
        ww = text_w(d, watch_txt, f_xs) + int(16 * s)
        d.rounded_rectangle([pad_x + int(52 * s), top_y + int(2 * s), pad_x + int(52 * s) + ww, top_y + int(25 * s)], radius=int(6 * s), fill=(15, 20, 25, 195))
        d.text((pad_x + int(60 * s), top_y + int(6 * s)), watch_txt, font=f_xs, fill=(226, 232, 240, 255))

        handle_txt = (host_name if host_name.startswith("@") else f"@{host_name}")[:15]
        hw = text_w(d, handle_txt, f_xs) + int(34 * s)
        d.rounded_rectangle([pad_x, top_y + int(31 * s), pad_x + hw, top_y + int(53 * s)], radius=int(11 * s), fill=(15, 20, 25, 195))
        d.ellipse([pad_x + int(5 * s), top_y + int(34 * s), pad_x + int(21 * s), top_y + int(50 * s)], fill=(53, 177, 209, 255))
        d.text((pad_x + int(26 * s), top_y + int(35 * s)), handle_txt, font=f_xs, fill=(248, 250, 252, 255))
        draw_close_x(d, w - pad_x - int(9 * s), top_y + int(14 * s), 5.5 * s, width=max(2, int(2 * s)))

    else:
        # Douyin / Kuaishou / TikTok rounded host capsule + follow pill + top viewers + viewer count
        use_zh_ui = is_zh and platform != "tiktok"
        fol_txt = "+ 关注" if (platform == "kuaishou" and use_zh_ui) else ("关注" if use_zh_ui else "+ Follow")
        fol_w = text_w(d, fol_txt, f_xs) + int(14 * s)
        sub_txt = (
            "热力 9.8万" if (platform == "kuaishou" and use_zh_ui)
            else ("本场赞 18.6万" if use_zh_ui else "Likes 42.1K")
        )
        disp_host = fit_text_px(d, host_name, f_sm, int(88 * s))
        text_col_w = max(text_w(d, disp_host, f_sm), text_w(d, sub_txt, f_xs))
        cap_w = min(int(196 * s), max(int(164 * s), int(38 * s) + text_col_w + fol_w + int(12 * s)))
        cap_h = int(34 * s)
        d.rounded_rectangle([pad_x, top_y, pad_x + cap_w, top_y + cap_h], radius=int(17 * s), fill=(0, 0, 0, 118))
        av_r = int(13 * s)
        d.ellipse([pad_x + int(4 * s), top_y + int(4 * s), pad_x + int(4 * s) + av_r * 2, top_y + int(4 * s) + av_r * 2], fill=(56, 189, 248, 255))
        d.text((pad_x + int(11 * s), top_y + int(7 * s)), host_name[:1].upper(), font=f_sm, fill=(15, 23, 42, 255))

        d.text((pad_x + int(34 * s), top_y + int(3 * s)), disp_host, font=f_sm, fill=(255, 255, 255, 255))
        d.text((pad_x + int(34 * s), top_y + int(18 * s)), sub_txt, font=f_xs, fill=(203, 213, 225, 235))

        fx0 = pad_x + cap_w - fol_w - int(5 * s)
        d.rounded_rectangle([fx0, top_y + int(5 * s), fx0 + fol_w, top_y + cap_h - int(5 * s)], radius=int(12 * s), fill=pal["accent"])
        d.text((fx0 + int(7 * s), top_y + int(8 * s)), fol_txt, font=f_xs, fill=(255, 255, 255, 255))

        # Top-right viewer pill + 2 mini rank dots
        vp_w = text_w(d, viewer_str, f_xs) + int(16 * s)
        vx0 = w - pad_x - int(24 * s) - vp_w
        for gi, gcol in enumerate([(250, 204, 21, 245), (148, 163, 184, 245)]):
            gx = vx0 - int((2 - gi) * 20 * s)
            if gx > pad_x + cap_w + int(4 * s):
                d.ellipse([gx, top_y + int(7 * s), gx + int(18 * s), top_y + int(25 * s)], fill=gcol)
        d.rounded_rectangle([vx0, top_y + int(5 * s), vx0 + vp_w, top_y + int(29 * s)], radius=int(12 * s), fill=(0, 0, 0, 118))
        d.text((vx0 + int(8 * s), top_y + int(9 * s)), viewer_str, font=f_xs, fill=(255, 255, 255, 255))
        cx_close = w - pad_x - int(10 * s)
        cy_close = top_y + int(17 * s)
        d.ellipse([cx_close - int(9 * s), cy_close - int(9 * s), cx_close + int(9 * s), cy_close + int(9 * s)], fill=(0, 0, 0, 108))
        draw_close_x(d, cx_close, cy_close, 4.0 * s, width=max(1, int(1.8 * s)))

        # Sub-rank chips row
        sub_y = top_y + cap_h + int(6 * s)
        chips = (
            ["红心热力榜", "快币红包 00:45"] if (platform == "kuaishou" and use_zh_ui)
            else (["Weekly Rank #5", "Treasure 00:58"] if platform == "tiktok"
            else (["人气榜 No.3", "福袋 01:28"] if use_zh_ui else ["Top #3", "Lucky Bag 01:28"]))
        )
        cx_cur = pad_x
        for ch in chips:
            cw = text_w(d, ch, f_xs) + int(16 * s)
            d.rounded_rectangle([cx_cur, sub_y, cx_cur + cw, sub_y + int(20 * s)], radius=int(10 * s), fill=(0, 0, 0, 102))
            d.text((cx_cur + int(8 * s), sub_y + int(3 * s)), ch, font=f_xs, fill=(241, 245, 249, 240))
            cx_cur += cw + int(6 * s)

    # 2. Rig-Specific Viewfinder / PK Tug-of-War Bar Overlays
    if rig == "overhead-showcase-rig" and shot_idx == 1:
        # Autofocus [AF-C] yellow tracking brackets framing the foreground held gadget cube + palm
        bx0, by0, bx1, by1 = int(102 * s), int(288 * s), int(258 * s), int(438 * s)
        blen = int(18 * s)
        col_af = (250, 204, 21, 245)
        lw = max(2, int(2.2 * s))
        for (x_a, y_a, dx_s, dy_s) in [
            (bx0, by0, 1, 1),
            (bx1, by0, -1, 1),
            (bx0, by1, 1, -1),
            (bx1, by1, -1, -1),
        ]:
            d.line([(x_a, y_a), (x_a + dx_s * blen, y_a)], fill=col_af, width=lw)
            d.line([(x_a, y_a), (x_a, y_a + dy_s * blen)], fill=col_af, width=lw)
        d.rounded_rectangle([bx0, by0 - int(18 * s), bx0 + int(86 * s), by0 - int(3 * s)], radius=int(4 * s), fill=(15, 23, 42, 200))
        d.text((bx0 + int(5 * s), by0 - int(17 * s)), "AF-C LOCK", font=f_mono, fill=col_af)

    if rig == "pk-cohost-split":
        # 50/50 split center seam + top PK tug-of-war progress bar + VS badge
        pk_ratio = float(hud_meta.get("pkScoreRatio", 0.52))
        pk_ratio = max(0.08, min(0.92, pk_ratio + math.sin(phase * math.pi * 2) * 0.02))
        bar_y = int(84 * s)
        bar_h = int(18 * s)
        raw_split_x = int(pad_x + (w - 2 * pad_x) * pk_ratio)
        d.rounded_rectangle([pad_x, bar_y, w - pad_x, bar_y + bar_h], radius=int(9 * s), fill=pal["accent2"])
        d.rounded_rectangle([pad_x, bar_y, max(pad_x + int(20 * s), raw_split_x), bar_y + bar_h], radius=int(9 * s), fill=pal["accent"])
        left_pts = int(pk_ratio * 150000)
        right_pts = int((1.0 - pk_ratio) * 150000)
        d.text((pad_x + int(8 * s), bar_y + int(2 * s)), f"{left_pts:,}", font=f_mono, fill=(255, 255, 255, 255))
        rt_str = f"{right_pts:,}"
        rt_w = text_w(d, rt_str, f_mono)
        d.text((w - pad_x - rt_w - int(8 * s), bar_y + int(2 * s)), rt_str, font=f_mono, fill=(15, 23, 42, 255))
        # Clamp PK badge so it never overlaps either score number
        badge_x = max(pad_x + int(68 * s), min(w - pad_x - int(68 * s), raw_split_x))
        d.rounded_rectangle([badge_x - int(14 * s), bar_y - int(3 * s), badge_x + int(14 * s), bar_y + bar_h + int(3 * s)], radius=int(8 * s), fill=(250, 204, 21, 255))
        d.text((badge_x - int(8 * s), bar_y + int(1 * s)), "PK", font=f_mono, fill=(15, 23, 42, 255))
        # Vertical center seam line across the dual rooms
        d.line([(w // 2, bar_y + bar_h + int(4 * s)), (w // 2, int(430 * s))], fill=(255, 255, 255, 145), width=max(1, int(1.5 * s)))

    # 3. Sinusoidal Bezier Rising Heart Fountain (drawn onto background heart_layer BEFORE foreground cards so popups stay 100% unobstructed!)
    periscope_cols = [
        (252, 228, 115, 255),
        (246, 139, 57, 255),
        (237, 108, 99, 255),
        (132, 123, 185, 255),
        (151, 205, 118, 255),
        (53, 177, 209, 255),
    ]
    active_popup = hud_meta.get("activePopup", "join_toast")
    by_bar = h - int(44 * s)
    heart_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(heart_layer)
    heart_cols = (
        periscope_cols if platform == "x"
        else [(pal["accent"][0], pal["accent"][1], pal["accent"][2], 235), (251, 113, 133, 235), (250, 204, 21, 225), (192, 132, 252, 230)]
    )
    num_hearts = 6 if hud_meta.get("heartBurstIntensity") == "high" else 4
    hx_anchor = w - pad_x - int(15 * s)
    hy_anchor = (h - int(184 * s)) if (active_popup == "commerce_card" and platform in ("douyin", "kuaishou", "tiktok")) else (by_bar - int(8 * s))
    for hi in range(num_hearts):
        p_h = (phase + hi / float(num_hearts)) % 1.0
        sway = math.sin(p_h * math.pi * 2.2 + hi * 1.7) * (12.0 * s)
        hy = hy_anchor - p_h * (165.0 * s)
        alpha_scale = math.sin(p_h * math.pi)
        hc = heart_cols[hi % len(heart_cols)]
        hr = (5.5 + (hi % 3) * 1.8) * s * (0.7 + 0.35 * alpha_scale)
        draw_heart(hd, hx_anchor + sway, hy, hr, (hc[0], hc[1], hc[2], int(230 * alpha_scale)))
    img = Image.alpha_composite(img, heart_layer)

    # 4. Active Interactive Popups (Gift Combo / Live Shopping Card / Instagram Q&A)
    use_zh_popup = is_zh and platform not in ("tiktok", "x", "instagram")
    if active_popup in ("gift_combo", "gift_combo_peak"):
        gift_info = hud_meta.get("giftZh" if use_zh_popup else "giftEn") or {"sender": "Nova", "gift": "Starlight", "combo": 66}
        combo_base = int(gift_info.get("combo", 66))
        combo_now = max(1, int(combo_base * (0.55 + 0.45 * phase)))
        sender_str = fit_text_px(d, str(gift_info.get("sender", "VIP")), f_xs, int(138 * s))
        verb = "送出 " if use_zh_popup else "Sent "
        gift_line = fit_text_px(d, f"{verb}{gift_info.get('gift', 'Rocket')}", f_xs, int(146 * s))
        combo_str = f"x{combo_now}"
        combo_w = text_w(d, combo_str, f_xl)
        text_block_w = max(text_w(d, sender_str, f_xs), text_w(d, gift_line, f_xs))
        gy = int(378 * s)
        gw = min(w - 2 * pad_x - int(24 * s), max(int(208 * s), int(46 * s) + text_block_w + combo_w + int(20 * s)))
        gh = int(38 * s)
        d.rounded_rectangle([pad_x, gy, pad_x + gw, gy + gh], radius=int(19 * s), fill=(15, 23, 42, 218), outline=pal["accent"], width=max(1, int(1.5 * s)))
        d.ellipse([pad_x + int(4 * s), gy + int(4 * s), pad_x + int(34 * s), gy + int(34 * s)], fill=(250, 204, 21, 255))
        d.text((pad_x + int(12 * s), gy + int(9 * s)), "★", font=f_md, fill=(15, 23, 42, 255))
        d.text((pad_x + int(40 * s), gy + int(4 * s)), sender_str, font=f_xs, fill=(253, 224, 71, 255))
        d.text((pad_x + int(40 * s), gy + int(19 * s)), gift_line, font=f_xs, fill=(255, 255, 255, 245))
        d.text((pad_x + gw - combo_w - int(10 * s), gy + int(7 * s)), combo_str, font=f_xl, fill=(253, 224, 71, 255))

    elif active_popup == "commerce_card" and platform in ("douyin", "kuaishou", "tiktok"):
        cw_card, ch_card = int(106 * s), int(116 * s)
        cx0 = w - pad_x - cw_card
        cy0 = h - int(174 * s)
        d.rounded_rectangle([cx0, cy0, cx0 + cw_card, cy0 + ch_card], radius=int(11 * s), fill=(255, 255, 255, 246))
        badge_t = "讲解中" if use_zh_popup else "PINNED"
        bw_tag = text_w(d, badge_t, f_xs) + int(10 * s)
        d.rounded_rectangle([cx0 + int(6 * s), cy0 + int(6 * s), cx0 + int(6 * s) + bw_tag, cy0 + int(21 * s)], radius=int(4 * s), fill=pal["accent"])
        d.text((cx0 + int(11 * s), cy0 + int(7 * s)), badge_t, font=f_xs, fill=(255, 255, 255, 255))
        d.rounded_rectangle([cx0 + int(6 * s), cy0 + int(25 * s), cx0 + cw_card - int(6 * s), cy0 + int(68 * s)], radius=int(7 * s), fill=(254, 226, 226, 255))
        draw_heart(d, cx0 + cw_card / 2, cy0 + int(47 * s), 11 * s, pal["accent"])
        raw_item_t = hud_meta.get("commerceItemZh" if use_zh_popup else "commerceItemEn") or ("1号福利链接" if use_zh_popup else "Link #1 Deal")
        item_t = fit_text_px(d, raw_item_t, f_xs, cw_card - int(12 * s))
        d.text((cx0 + int(6 * s), cy0 + int(72 * s)), item_t, font=f_xs, fill=(15, 23, 42, 255))
        d.text((cx0 + int(6 * s), cy0 + int(91 * s)), "¥39.9" if use_zh_popup else "$24", font=f_md, fill=(225, 29, 72, 255))
        cta_t = "抢" if use_zh_popup else "Buy"
        cta_w = max(int(28 * s), text_w(d, cta_t, f_xs) + int(12 * s))
        d.rounded_rectangle([cx0 + cw_card - cta_w - int(6 * s), cy0 + int(89 * s), cx0 + cw_card - int(6 * s), cy0 + int(109 * s)], radius=int(5 * s), fill=(225, 29, 72, 255))
        d.text((cx0 + cw_card - cta_w, cy0 + int(92 * s)), cta_t, font=f_xs, fill=(255, 255, 255, 255))

    elif active_popup == "qa_pinned" and platform == "instagram":
        qx0, qy0, qx1, qy1 = pad_x, int(386 * s), w - int(54 * s), int(442 * s)
        d.rounded_rectangle([qx0, qy0, qx1, qy1], radius=int(12 * s), fill=(255, 255, 255, 238))
        d.text((qx0 + int(10 * s), qy0 + int(6 * s)), "Q&A · @mina.design", font=f_xs, fill=(100, 116, 139, 255))
        raw_q = hud_meta.get("qaQuestionZh" if is_zh else "qaQuestionEn") or ("等等！刚才是真的自己在动吗？？" if is_zh else "Wait did that actually move on live?!")
        q_body = fit_text_px(d, raw_q, f_sm, (qx1 - qx0) - int(20 * s))
        d.text((qx0 + int(10 * s), qy0 + int(23 * s)), q_body, font=f_sm, fill=(15, 23, 42, 255))

    # 5. Join Ribbon + Scrolling Comment Feed Stack (with pixel-fitted text & Kuaishou combo pills!)
    comments = hud_meta.get("commentsZh" if is_zh else "commentsEn") or [
        {"user": "kai_live", "text": "Wait look right behind you!!", "lv": 14},
        {"user": "momo_07", "text": "No way this is unscripted!", "lv": 19},
        {"user": "clip_pro", "text": "Instant hall of fame clip!", "lv": 25},
    ]

    chat_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chat_layer)
    base_chat_y = h - int(62 * s)
    row_h = int(25 * s)
    scroll_px = int(phase * row_h * 0.45)

    max_pill_w = w - pad_x - (int(122 * s) if active_popup == "commerce_card" and platform in ("douyin", "kuaishou", "tiktok") else int(54 * s))
    for idx_c, c_item in enumerate(reversed(comments[:3])):
        ry = base_chat_y - (idx_c + 1) * (row_h + int(4 * s)) - scroll_px
        fade_alpha = 245 if idx_c < 2 else int(155 * (1.0 - phase * 0.45))
        u_name = str(c_item.get("user", "user"))
        u_text = str(c_item.get("text", ""))
        raw_line = f"{u_name}: {u_text}"

        if platform == "instagram":
            full_line = fit_text_px(cd, raw_line, f_sm, max_pill_w - int(8 * s))
            cd.text((pad_x + 1, ry + int(5 * s) + 1), full_line, font=f_sm, fill=(0, 0, 0, int(fade_alpha * 0.85)))
            cd.text((pad_x, ry + int(5 * s)), full_line, font=f_sm, fill=(255, 255, 255, fade_alpha))
        elif platform == "x":
            tint = periscope_cols[idx_c % len(periscope_cols)]
            full_line = fit_text_px(cd, raw_line, f_xs, max_pill_w - int(18 * s))
            rw = min(max_pill_w, text_w(cd, full_line, f_xs) + int(18 * s))
            cd.rounded_rectangle([pad_x, ry, pad_x + rw, ry + row_h], radius=int(11 * s), fill=(15, 20, 25, int(fade_alpha * 0.82)))
            cd.rounded_rectangle([pad_x, ry + int(4 * s), pad_x + int(3.5 * s), ry + row_h - int(4 * s)], radius=int(2 * s), fill=(tint[0], tint[1], tint[2], fade_alpha))
            cd.text((pad_x + int(9 * s), ry + int(5 * s)), full_line, font=f_xs, fill=(248, 250, 252, fade_alpha))
        else:
            lv_str = f"Lv.{c_item.get('lv', 12)}"
            lv_w = text_w(cd, lv_str, f_xs) + int(10 * s)
            combo_val = c_item.get("combo")
            combo_tag = f"x{combo_val}" if (combo_val and platform == "kuaishou") else ""
            combo_tag_w = (text_w(cd, combo_tag, f_xs) + int(10 * s)) if combo_tag else 0
            avail_msg_w = max(int(64 * s), max_pill_w - lv_w - combo_tag_w - int(18 * s))
            fitted_msg = fit_text_px(cd, raw_line, f_xs, avail_msg_w)
            msg_w = text_w(cd, fitted_msg, f_xs)
            rw = min(max_pill_w, lv_w + msg_w + combo_tag_w + int(18 * s))
            cd.rounded_rectangle([pad_x, ry, pad_x + rw, ry + row_h], radius=int(10 * s), fill=(0, 0, 0, int(fade_alpha * 0.44)))
            cd.rounded_rectangle([pad_x + int(5 * s), ry + int(4 * s), pad_x + int(5 * s) + lv_w, ry + row_h - int(4 * s)], radius=int(4 * s), fill=(pal["badge"][0], pal["badge"][1], pal["badge"][2], fade_alpha))
            cd.text((pad_x + int(10 * s), ry + int(5 * s)), lv_str, font=f_xs, fill=(255, 255, 255, fade_alpha))
            cd.text((pad_x + int(10 * s) + lv_w, ry + int(5 * s)), fitted_msg, font=f_xs, fill=(255, 255, 255, fade_alpha))
            if combo_tag:
                cx_cb = pad_x + rw - combo_tag_w - int(4 * s)
                cd.rounded_rectangle([cx_cb, ry + int(4 * s), cx_cb + combo_tag_w, ry + row_h - int(4 * s)], radius=int(7 * s), fill=(255, 80, 0, fade_alpha))
                cd.text((cx_cb + int(5 * s), ry + int(5 * s)), combo_tag, font=f_xs, fill=(255, 255, 255, fade_alpha))

    # Join toast pill just above chat stack on Shot 0 (CJK-safe symbols, zero missing emoji boxes!)
    if active_popup == "join_toast":
        jy = base_chat_y - 3 * (row_h + int(4 * s)) - int(28 * s)
        j_txt = (
            "★ [铁粉] 榜一大哥 点亮了红心" if (platform == "kuaishou" and use_zh_popup)
            else ("● kaya.studio joined · Wave" if platform == "instagram"
            else ("@alex_dev joined live" if platform == "x"
            else ("★ [钻粉] 星河舰长 来了" if use_zh_popup else "★ [Gifter Lv.24] pixel_kai joined")))
        )
        j_fitted = fit_text_px(cd, j_txt, f_xs, max_pill_w - int(18 * s))
        jw = min(max_pill_w, text_w(cd, j_fitted, f_xs) + int(18 * s))
        cd.rounded_rectangle([pad_x, jy, pad_x + jw, jy + int(22 * s)], radius=int(11 * s), fill=(pal["badge"][0], pal["badge"][1], pal["badge"][2], 198))
        cd.text((pad_x + int(9 * s), jy + int(4 * s)), j_fitted, font=f_xs, fill=(255, 255, 255, 250))

    img = Image.alpha_composite(img, chat_layer)

    # 6. Bottom Input Bar + Action Buttons
    comp_w = int(198 * s)
    d.rounded_rectangle([pad_x, by_bar, pad_x + comp_w, by_bar + int(30 * s)], radius=int(15 * s), fill=(0, 0, 0, 112), outline=(255, 255, 255, 58))
    placeholder = (
        "聊一聊…" if (platform == "kuaishou" and use_zh_popup)
        else ("Add a comment…" if platform == "instagram"
        else ("Say something…" if platform == "x"
        else ("说点什么…" if use_zh_popup else "Add comment…")))
    )
    d.text((pad_x + int(12 * s), by_bar + int(7 * s)), placeholder, font=f_xs, fill=(226, 232, 240, 200))

    # Right action circles + Heart CTA
    for bi in range(3):
        bx_c = w - pad_x - (3 - bi) * int(34 * s) + int(4 * s)
        is_heart = bi == 2
        bg_c = pal["accent"] if is_heart else (0, 0, 0, 118)
        d.ellipse([bx_c, by_bar, bx_c + int(30 * s), by_bar + int(30 * s)], fill=bg_c)
        if is_heart:
            draw_heart(d, bx_c + int(15 * s), by_bar + int(15 * s), 7.5 * s, (255, 255, 255, 255))
        else:
            sym = "+" if bi == 0 else "↗"
            d.text((bx_c + int(9 * s), by_bar + int(6 * s)), sym, font=f_md, fill=(255, 255, 255, 240))

    # Optional Roblox overhead BillboardGui crisp English speech bubble when chatEn exists
    chat_en = hud_meta.get("chatEn", "")
    if chat_en and hud_meta.get("style") == "roblox-blocky":
        bub_w = int(max(86, len(chat_en) * 9 + 24) * s)
        bub_x = (w - bub_w) // 2
        bub_y = int(124 * s) if rig == "pk-cohost-split" else int(96 * s)
        d.rounded_rectangle([bub_x, bub_y, bub_x + bub_w, bub_y + int(26 * s)], radius=int(9 * s), fill=(255, 255, 255, 244), outline=(203, 213, 225, 255))
        d.polygon([(w // 2 - int(5 * s), bub_y + int(26 * s)), (w // 2 + int(5 * s), bub_y + int(26 * s)), (w // 2, bub_y + int(33 * s))], fill=(255, 255, 255, 244))
        d.text((bub_x + int(11 * s), bub_y + int(5 * s)), chat_en[:16], font=f_mono, fill=(15, 23, 42, 255))

    return Image.alpha_composite(img, overlay)


def save_grid_sheet(cards, cols: int, card_w: int, card_h: int, out_path: str, title_text: str = ""):
    pad = 18
    header_h = 48 if title_text else 0
    rows = math.ceil(len(cards) / cols)
    total_w = pad + cols * (card_w + pad)
    total_h = header_h + pad + rows * (card_h + 44 + pad)
    sheet = Image.new("RGB", (total_w, total_h), (244, 246, 250))
    d = ImageDraw.Draw(sheet)
    f_title = load_font(20)
    f_lbl = load_font(14)

    if title_text:
        d.text((pad + 4, 14), title_text, font=f_title, fill=(15, 23, 42))

    for idx, item in enumerate(cards):
        r = idx // cols
        c = idx % cols
        x0 = pad + c * (card_w + pad)
        y0 = header_h + pad + r * (card_h + 44 + pad)
        border_col = tuple(item.get("borderColor", [203, 213, 225]))
        d.rounded_rectangle([x0, y0, x0 + card_w + 8, y0 + card_h + 42], radius=14, fill=(255, 255, 255), outline=border_col, width=2)
        im = item["image"].convert("RGB").resize((card_w, card_h), Image.Resampling.BILINEAR)
        sheet.paste(im, (x0 + 4, y0 + 4))
        lbl = fit_text_px(d, item.get("label", ""), f_lbl, card_w - 18)
        if item.get("badgeFill"):
            bf = tuple(item["badgeFill"])
            d.rounded_rectangle([x0 + 10, y0 + card_h + 9, x0 + card_w - 2, y0 + card_h + 36], radius=7, fill=bf)
            d.text((x0 + 18, y0 + card_h + 13), lbl, font=f_lbl, fill=(255, 255, 255))
        else:
            d.text((x0 + 12, y0 + card_h + 13), lbl, font=f_lbl, fill=(30, 41, 59))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path, format="PNG", optimize=True)


def encode_gif_and_mp4(frame_paths, wav_path: str, in_fps: float, gif_path: str, mp4_path: str):
    os.makedirs(os.path.dirname(gif_path), exist_ok=True)
    frames = [Image.open(fp).convert("RGB") for fp in frame_paths]
    if frames:
        dur_ms = max(60, int(round(1000.0 / max(1.0, in_fps))))
        gif_frames = [f.resize((270, 480), Image.Resampling.BILINEAR).quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]
        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=dur_ms,
            loop=0,
            optimize=True,
        )

    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin and frame_paths:
        pattern_dir = os.path.dirname(frame_paths[0])
        prefix = os.path.basename(frame_paths[0]).split("_hud_")[0]
        input_pattern = os.path.join(pattern_dir, f"{prefix}_hud_%04d.png")
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loglevel",
            "error",
            "-framerate",
            f"{in_fps:.4f}",
            "-i",
            input_pattern,
        ]
        if wav_path and os.path.exists(wav_path):
            cmd += ["-i", wav_path, "-shortest", "-c:a", "aac", "-b:a", "128k"]
        cmd += [
            "-vf",
            "scale=540:960:flags=lanczos,fps=24",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            mp4_path,
        ]
        subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: compose_hud.py <manifest.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        manifest = json.load(f)

    raw_dir = manifest["rawDir"]

    # 1. Turnaround / 3-State Rig Setup Sheet
    t_info = manifest.get("turnaround")
    if t_info and all(os.path.exists(os.path.join(raw_dir, v["file"])) for v in t_info["views"]):
        for lang in ("zh", "en"):
            cards = []
            for v in t_info["views"]:
                im = Image.open(os.path.join(raw_dir, v["file"]))
                cards.append({"image": im, "label": v["labelZh"] if lang == "zh" else v["labelEn"]})
            out_f = t_info["outZh"] if lang == "zh" else t_info["outEn"]
            title = t_info.get("titleZh" if lang == "zh" else "titleEn", "")
            save_grid_sheet(cards, 3, 360, 460, out_f, title)
            if lang == "en":
                for df in t_info.get("outDefault", []):
                    shutil.copyfile(out_f, df)

    # 2. Showcase Multi-Platform Chrome & Popup Atlas (5 platforms)
    plat_atlas = manifest.get("platformAtlas")
    if plat_atlas and os.path.exists(os.path.join(raw_dir, plat_atlas["baseFile"])):
        base_plate = Image.open(os.path.join(raw_dir, plat_atlas["baseFile"]))
        for lang in ("zh", "en"):
            cards = []
            for item in plat_atlas["items"]:
                comp = overlay_platform_hud(
                    base_plate,
                    platform=item["platform"],
                    rig=item.get("rig", "desktop-webcam"),
                    host_name=item.get("host", "Kaya"),
                    cohost_name="Momo",
                    shot_idx=item.get("shotIdx", 2),
                    phase=0.68,
                    lang=lang,
                    hud_meta=item.get("hudMeta", {}),
                )
                cards.append({
                    "image": comp,
                    "label": item["labelZh"] if lang == "zh" else item["labelEn"],
                    "borderColor": item.get("borderColor", [203, 213, 225]),
                })
            out_f = plat_atlas["outZh"] if lang == "zh" else plat_atlas["outEn"]
            save_grid_sheet(
                cards,
                5,
                252,
                448,
                out_f,
                "主流直播平台边框 / 弹窗 / 飘心逆向复刻矩阵 (REA Clean-Plate + Post-HUD)" if lang == "zh"
                else "Reconstructed Mainstream Livestream Chrome, Popups & Heart FX Matrix (REA)",
            )
            if lang == "en" and plat_atlas.get("outDefault"):
                shutil.copyfile(out_f, plat_atlas["outDefault"])

    # 3. Camera Rigs 6-Panel Atlas
    rig_atlas = manifest.get("rigAtlas")
    if rig_atlas and all(os.path.exists(os.path.join(raw_dir, r["file"])) for r in rig_atlas["items"]):
        for lang in ("zh", "en"):
            cards = []
            for r in rig_atlas["items"]:
                raw_im = Image.open(os.path.join(raw_dir, r["file"]))
                pip_im = Image.open(os.path.join(raw_dir, r["pipFile"])) if r.get("pipFile") and os.path.exists(os.path.join(raw_dir, r["pipFile"])) else None
                comp = overlay_platform_hud(
                    raw_im,
                    platform=r.get("platform", "douyin"),
                    rig=r["rig"],
                    host_name=r.get("host", "Alex"),
                    cohost_name="Noob",
                    shot_idx=r.get("shotIdx", 1),
                    phase=0.6,
                    lang=lang,
                    hud_meta=r.get("hudMeta", {}),
                    pip_img=pip_im,
                )
                cards.append({"image": comp, "label": r["labelZh"] if lang == "zh" else r["labelEn"]})
            out_f = rig_atlas["outZh"] if lang == "zh" else rig_atlas["outEn"]
            save_grid_sheet(
                cards,
                3,
                270,
                480,
                out_f,
                "六大核心直播机位光学与跨画风样本 (写实 IRL + 架空仙侠 + Roblox)" if lang == "zh"
                else "Six Core Livestream Camera Rigs Across Styles (Realistic IRL, Wuxia & Roblox)",
            )
            if lang == "en" and rig_atlas.get("outDefault"):
                shutil.copyfile(out_f, rig_atlas["outDefault"])

    # 4. 4-Way Clean-Plate vs Gibberish-UI Anti-Drift Comparison
    drift_info = manifest.get("drift")
    if drift_info and all(os.path.exists(os.path.join(raw_dir, p["file"])) for p in drift_info["panels"]):
        for lang in ("zh", "en"):
            cards = []
            for p in drift_info["panels"]:
                raw_im = Image.open(os.path.join(raw_dir, p["file"]))
                if p.get("postHudPlatform"):
                    raw_im = overlay_platform_hud(
                        raw_im,
                        platform=p["postHudPlatform"],
                        rig="handheld-selfie-irl",
                        host_name="Lin",
                        cohost_name="Momo",
                        shot_idx=2,
                        phase=0.65,
                        lang=lang,
                        hud_meta={"activePopup": "gift_combo", "heartBurstIntensity": "high"},
                    )
                cards.append({
                    "image": raw_im,
                    "label": p["labelZh"] if lang == "zh" else p["labelEn"],
                    "borderColor": p["color"],
                    "badgeFill": p["color"],
                })
            out_f = drift_info["outZh"] if lang == "zh" else drift_info["outEn"]
            save_grid_sheet(
                cards,
                4,
                270,
                480,
                out_f,
                "防跑偏对比：拒绝第三人称空镜与AI乱码UI -> 纯净底片 + 后置高清直播HUD" if lang == "zh"
                else "Anti-Drift Guard: Block 3rd-Person Drift & Gibberish AI UI -> Clean Plate + Post-HUD",
            )
            if lang == "en" and drift_info.get("outDefault"):
                shutil.copyfile(out_f, drift_info["outDefault"])

    # 5. Episode Cases (4-Shot Contact Sheets + Animated HUD Frames + GIF + MP4)
    reel_sources = []
    for case in manifest.get("cases", []):
        prefix = case["prefix"]
        platform = case.get("platform", "douyin")
        rig = case.get("rig", "desktop-webcam")
        host_name = case.get("host", "Alex")
        cohost_name = case.get("cohost", "Momo")
        style = case.get("style", "realistic-irl")
        shots = case["shots"]

        # Contact sheets (.zh.png and .en.png) + individual shot keyframes
        for lang in ("zh", "en"):
            cards = []
            for s_idx, sh in enumerate(shots):
                raw_shot_path = os.path.join(raw_dir, f"{prefix}_shot_{s_idx}.png")
                if not os.path.exists(raw_shot_path):
                    continue
                raw_im = Image.open(raw_shot_path)
                pip_shot_path = os.path.join(raw_dir, f"{prefix}_pip_shot_{s_idx}.png")
                pip_im = Image.open(pip_shot_path) if os.path.exists(pip_shot_path) else None
                meta = dict(sh.get("hudMeta") or {})
                meta["chatEn"] = sh.get("chatEn", "")
                meta["style"] = style
                comp = overlay_platform_hud(
                    raw_im,
                    platform=platform,
                    rig=rig,
                    host_name=host_name,
                    cohost_name=cohost_name,
                    shot_idx=s_idx,
                    phase=0.62,
                    lang=lang,
                    hud_meta=meta,
                    pip_img=pip_im,
                )
                if lang == "zh" and sh.get("savePath"):
                    os.makedirs(os.path.dirname(sh["savePath"]), exist_ok=True)
                    comp.convert("RGB").save(sh["savePath"], format="PNG", optimize=True)
                cards.append({
                    "image": comp,
                    "label": sh["labelZh"] if lang == "zh" else sh["labelEn"],
                })

            if cards:
                cols = 4 if len(cards) == 4 else min(4, len(cards))
                out_sheet = case["sheetZh"] if lang == "zh" else case["sheetEn"]
                save_grid_sheet(cards, cols, 270, 480, out_sheet, case.get("titleZh" if lang == "zh" else "titleEn", ""))
                if lang == "en" and case.get("sheetDefault"):
                    shutil.copyfile(out_sheet, case["sheetDefault"])

        # Composite HUD onto animation frames
        hud_frame_paths = []
        frame_cursor = 0
        for s_idx, sh in enumerate(shots):
            f_count = int(sh.get("frameCount", 6))
            meta = dict(sh.get("hudMeta") or {})
            meta["chatEn"] = sh.get("chatEn", "")
            meta["style"] = style
            for f_local in range(f_count):
                raw_anim = os.path.join(raw_dir, f"{prefix}_anim_{frame_cursor:04d}.png")
                if not os.path.exists(raw_anim):
                    frame_cursor += 1
                    continue
                pip_anim = os.path.join(raw_dir, f"{prefix}_pip_anim_{frame_cursor:04d}.png")
                raw_im = Image.open(raw_anim)
                pip_im = Image.open(pip_anim) if os.path.exists(pip_anim) else None
                phase = (f_local + 0.5) / max(1, f_count)
                comp = overlay_platform_hud(
                    raw_im,
                    platform=platform,
                    rig=rig,
                    host_name=host_name,
                    cohost_name=cohost_name,
                    shot_idx=s_idx,
                    phase=phase,
                    lang=case.get("hudLang", "zh"),
                    hud_meta=meta,
                    pip_img=pip_im,
                )
                out_hud_frame = os.path.join(raw_dir, f"{prefix}_hud_{frame_cursor:04d}.png")
                comp.convert("RGB").save(out_hud_frame, format="PNG")
                hud_frame_paths.append(out_hud_frame)
                frame_cursor += 1

        if hud_frame_paths:
            encode_gif_and_mp4(
                hud_frame_paths,
                case.get("wavPath", ""),
                float(case.get("inFps", 3.2)),
                case["gifPath"],
                case["mp4Path"],
            )
            if case.get("includeInHeroReel"):
                reel_sources.append((case.get("reelLabel", prefix), hud_frame_paths, case.get("wavPath", ""), float(case.get("inFps", 3.2))))

    # 6. 4-Up Synchronized Hero Showcase Reel (GIF + MP4)
    hero_reel = manifest.get("heroReel")
    if hero_reel and len(reel_sources) >= 4:
        selected = reel_sources[:4]
        min_len = min(len(item[1]) for item in selected)
        reel_frame_paths = []
        f_hdr = load_font(13)
        for fi in range(min_len):
            canvas = Image.new("RGB", (948, 456), (11, 15, 25))
            cd = ImageDraw.Draw(canvas)
            for ci, (lbl, fpaths, _, _) in enumerate(selected):
                x0 = 12 + ci * 234
                y0 = 10
                im = Image.open(fpaths[fi]).convert("RGB").resize((222, 395), Image.Resampling.BILINEAR)
                cd.rounded_rectangle([x0 - 2, y0 - 2, x0 + 224, y0 + 436], radius=12, fill=(30, 41, 59), outline=(51, 65, 85))
                canvas.paste(im, (x0, y0))
                cd.text((x0 + 8, y0 + 406), lbl[:24], font=f_hdr, fill=(226, 232, 240))
            rfp = os.path.join(raw_dir, f"hero_reel_hud_{fi:04d}.png")
            canvas.save(rfp, format="PNG")
            reel_frame_paths.append(rfp)

        # Save GIF directly at 948x456
        frames_rgb = [Image.open(p).convert("RGB") for p in reel_frame_paths]
        in_fps_reel = selected[0][3]
        dur_ms = max(70, int(round(1000.0 / max(1.0, in_fps_reel))))
        os.makedirs(os.path.dirname(hero_reel["gifPath"]), exist_ok=True)
        q_frames = [fr.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for fr in frames_rgb]
        q_frames[0].save(hero_reel["gifPath"], save_all=True, append_images=q_frames[1:], duration=dur_ms, loop=0, optimize=True)

        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            cmd = [
                ffmpeg_bin,
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                f"{in_fps_reel:.4f}",
                "-i",
                os.path.join(raw_dir, "hero_reel_hud_%04d.png"),
            ]
            if selected[0][2] and os.path.exists(selected[0][2]):
                cmd += ["-i", selected[0][2], "-shortest", "-c:a", "aac", "-b:a", "128k"]
            cmd += [
                "-vf",
                "fps=24,scale=948:456:flags=lanczos",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "22",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                hero_reel["mp4Path"],
            ]
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
