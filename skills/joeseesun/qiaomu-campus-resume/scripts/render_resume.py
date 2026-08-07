#!/usr/bin/env python3
"""Render an ATS-readable single-column resume to local HTML and PDF."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


THEME_ORDER = (
    "ats-classic",
    "kami",
    "swiss",
    "tech",
    "campus",
    "compact",
)

THEMES: dict[str, dict[str, Any]] = {
    "ats-classic": {
        "label": "ATS 经典",
        "filename": "01_ATS经典",
        "use_case": "通用校招、国企、金融、咨询及正式岗位",
        "page": "#FFFFFF",
        "paper": "#FFFFFF",
        "ink": "#151515",
        "muted": "#55514E",
        "line": "#D8D3CE",
        "brand": "#6D2536",
        "tint": "#F7F1F2",
        "body_font": 'Palatino, Georgia, "Songti SC", "STSong", "SimSun", serif',
        "heading_font": 'Palatino, Georgia, "Songti SC", "STSong", "SimSun", serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "11mm 14mm",
        "body_size": "9.7pt",
        "line_height": "1.46",
        "name_size": "25pt",
        "section_size": "10.8pt",
        "entry_size": "10.4pt",
        "sub_size": "9pt",
        "meta_size": "8.7pt",
        "contact_size": "8.9pt",
        "section_gap": "5.2mm",
        "entry_gap": "1.4mm",
        "name_weight": 600,
        "section_weight": 600,
        "entry_weight": 600,
        "required_font": "Songti",
    },
    "kami": {
        "label": "Kami 编辑式",
        "filename": "02_Kami编辑式",
        "use_case": "教育、内容、品牌、产品及希望克制表达个性的岗位",
        "page": "#F5F4ED",
        "paper": "#F5F4ED",
        "ink": "#141413",
        "muted": "#6B6A64",
        "line": "#E8E6DC",
        "brand": "#1B365D",
        "tint": "#EEF2F7",
        "body_font": 'Palatino, Georgia, "TsangerJinKai02", "Songti SC", "STSong", serif',
        "heading_font": 'Palatino, Georgia, "TsangerJinKai02", "Songti SC", "STSong", serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "11.5mm 14mm",
        "body_size": "9.8pt",
        "line_height": "1.52",
        "name_size": "27pt",
        "section_size": "11.1pt",
        "entry_size": "10.45pt",
        "sub_size": "9pt",
        "meta_size": "8.75pt",
        "contact_size": "8.9pt",
        "section_gap": "6mm",
        "entry_gap": "1.55mm",
        "name_weight": 500,
        "section_weight": 500,
        "entry_weight": 500,
        "required_font": "TsangerJinKai02",
    },
    "swiss": {
        "label": "瑞士现代",
        "filename": "03_瑞士现代",
        "use_case": "产品、数据、商业分析、互联网与现代企业",
        "page": "#FCFCFA",
        "paper": "#FCFCFA",
        "ink": "#101214",
        "muted": "#5E6266",
        "line": "#D9DDDE",
        "brand": "#C63C32",
        "tint": "#F8ECEA",
        "body_font": '"Avenir Next", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
        "heading_font": '"Avenir Next", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", sans-serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "11mm 13mm",
        "body_size": "9.7pt",
        "line_height": "1.46",
        "name_size": "29pt",
        "section_size": "10.8pt",
        "entry_size": "10.35pt",
        "sub_size": "8.95pt",
        "meta_size": "8.65pt",
        "contact_size": "8.85pt",
        "section_gap": "5.4mm",
        "entry_gap": "1.35mm",
        "name_weight": 600,
        "section_weight": 600,
        "entry_weight": 600,
        "required_font": "PingFang",
    },
    "tech": {
        "label": "技术工程",
        "filename": "04_技术工程",
        "use_case": "软件、AI、数据、算法、DevOps 与工程岗位",
        "page": "#FFFFFF",
        "paper": "#FFFFFF",
        "ink": "#15212B",
        "muted": "#5C6871",
        "line": "#D8E0E5",
        "brand": "#00649A",
        "tint": "#EAF3F8",
        "body_font": '"IBM Plex Sans", "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
        "heading_font": '"IBM Plex Sans", "Avenir Next", "PingFang SC", "Hiragino Sans GB", sans-serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "11.5mm 13.5mm",
        "body_size": "9.75pt",
        "line_height": "1.46",
        "name_size": "27pt",
        "section_size": "11pt",
        "entry_size": "10.5pt",
        "sub_size": "9.1pt",
        "meta_size": "8.8pt",
        "contact_size": "8.95pt",
        "section_gap": "5.6mm",
        "entry_gap": "1.4mm",
        "name_weight": 600,
        "section_weight": 600,
        "entry_weight": 600,
        "required_font": "PingFang",
    },
    "campus": {
        "label": "校园清新",
        "filename": "05_校园清新",
        "use_case": "第一份实习、运营、市场、教育与校园招聘",
        "page": "#FFFDF8",
        "paper": "#FFFDF8",
        "ink": "#17231F",
        "muted": "#64706B",
        "line": "#DDE8E2",
        "brand": "#16745F",
        "tint": "#EAF5F1",
        "body_font": '"Avenir Next", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
        "heading_font": '"Avenir Next", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", sans-serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "11.5mm 13.5mm",
        "body_size": "9.75pt",
        "line_height": "1.48",
        "name_size": "27pt",
        "section_size": "11.1pt",
        "entry_size": "10.45pt",
        "sub_size": "9pt",
        "meta_size": "8.7pt",
        "contact_size": "8.9pt",
        "section_gap": "5.7mm",
        "entry_gap": "1.45mm",
        "name_weight": 600,
        "section_weight": 600,
        "entry_weight": 600,
        "required_font": "PingFang",
    },
    "compact": {
        "label": "高密信息",
        "filename": "06_高密信息",
        "use_case": "项目或实习较多、仍需控制在一页的候选人",
        "page": "#FFFFFF",
        "paper": "#FFFFFF",
        "ink": "#17202A",
        "muted": "#56606A",
        "line": "#D6DCE1",
        "brand": "#2B4C6F",
        "tint": "#EDF2F6",
        "body_font": 'Palatino, Georgia, "Songti SC", "STSong", "SimSun", serif',
        "heading_font": '"Avenir Next", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", sans-serif',
        "mono_font": '"SFMono-Regular", Menlo, Monaco, "PingFang SC", monospace',
        "page_margin": "9mm 11mm",
        "body_size": "9.1pt",
        "line_height": "1.34",
        "name_size": "22.5pt",
        "section_size": "10.3pt",
        "entry_size": "10pt",
        "sub_size": "8.5pt",
        "meta_size": "8.2pt",
        "contact_size": "8.35pt",
        "section_gap": "3.4mm",
        "entry_gap": ".85mm",
        "name_weight": 600,
        "section_weight": 600,
        "entry_weight": 600,
        "required_font": "Songti",
    },
}

REFERENCE_STYLE_ORDER = (
    "rc-003",
    "rc-071",
    "rc-102",
    "rc-109",
    "rc-150",
    "rc-214",
)

# ResumeCollection is used as visual prior art only. These presets are original,
# ATS-safe CSS reconstructions; no upstream Word, image, icon, or font asset is bundled.
REFERENCE_STYLES: dict[str, dict[str, Any]] = {
    "rc-003": {
        "label": "RC003 高密蓝线",
        "filename": "R01_RC003高密蓝线",
        "use_case": "软件、算法、数据岗位；项目较多但仍需一页",
        "source_id": "003",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/003",
        "base_theme": "compact",
        "tokens": {"paper": "#FFFFFF", "ink": "#17212B", "muted": "#586674", "line": "#91A8BB", "brand": "#173F63", "tint": "#EEF3F7"},
        "css": """
          header { margin-bottom: 2.7mm; padding-bottom: 1.5mm; border-bottom-color: var(--brand); }
          h1 { font-size: 23pt; letter-spacing: .2pt; }
          section { margin-top: 2.7mm; }
          .section-title { color: var(--brand); font-size: 10.2pt; letter-spacing: .8pt; padding-bottom: .55mm; margin-bottom: .9mm; border-bottom-color: var(--brand); }
        """,
    },
    "rc-071": {
        "label": "RC071 深蓝极简",
        "filename": "R02_RC071深蓝极简",
        "use_case": "通用校招、产品、运营与希望稳重克制的岗位",
        "source_id": "071",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/071",
        "base_theme": "swiss",
        "tokens": {"paper": "#FFFFFF", "ink": "#18222D", "muted": "#5D6873", "line": "#C6D0D9", "brand": "#17365D", "tint": "#EEF2F6"},
        "css": """
          header { padding-bottom: 2.2mm; border-bottom-color: var(--brand); }
          h1 { font-size: 27pt; letter-spacing: -.55pt; }
          .headline { color: var(--brand); letter-spacing: .45pt; }
          .section-title { color: var(--brand); font-size: 10.8pt; letter-spacing: 1.2pt; border-bottom-color: var(--line); }
        """,
    },
    "rc-102": {
        "label": "RC102 章条商务",
        "filename": "R03_RC102章条商务",
        "use_case": "国企、制造、金融、咨询及偏正式的校园招聘",
        "source_id": "102",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/102",
        "base_theme": "tech",
        "tokens": {"paper": "#FFFFFF", "ink": "#18232C", "muted": "#626D76", "line": "#C7D2DB", "brand": "#244E73", "tint": "#EDF2F6"},
        "css": """
          header { padding: 0 0 2.2mm; background: transparent; border-bottom-color: var(--brand); }
          .section-title { color: var(--paper); background: var(--brand); padding: .75mm 1.6mm .7mm; margin-bottom: 1.45mm; border-bottom-color: var(--brand); letter-spacing: .55pt; }
          h3 { font-family: var(--body-font); }
        """,
    },
    "rc-109": {
        "label": "RC109 双语经典",
        "filename": "R04_RC109双语经典",
        "use_case": "外企、国际项目、英文环境或希望双语章节导航的岗位",
        "source_id": "109",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/109",
        "base_theme": "ats-classic",
        "tokens": {"paper": "#FFFFFF", "ink": "#171717", "muted": "#595959", "line": "#AEB7BF", "brand": "#203E5A", "tint": "#F1F4F6"},
        "css": """
          .identity { display: flex; text-align: left; }
          .position { text-align: right; margin-top: 0; }
          .contact { justify-content: flex-end; }
          h1 { font-size: 24pt; letter-spacing: .5pt; }
          .section-title { color: var(--brand); font-size: 10.3pt; letter-spacing: .6pt; border-bottom-color: var(--brand); }
        """,
    },
    "rc-150": {
        "label": "RC150 灰白机构",
        "filename": "R05_RC150灰白机构",
        "use_case": "研究助理、公共部门、教育、行政与机构型岗位",
        "source_id": "150",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/150",
        "base_theme": "ats-classic",
        "tokens": {"paper": "#FFFFFF", "ink": "#202326", "muted": "#666B70", "line": "#C9CDD1", "brand": "#4E5963", "tint": "#F1F2F3"},
        "css": """
          .identity { display: flex; text-align: left; }
          .position { text-align: right; margin-top: 0; }
          .contact { justify-content: flex-end; }
          h1 { font-size: 24.5pt; letter-spacing: .25pt; }
          .section-title { color: var(--brand); font-size: 10.7pt; letter-spacing: .75pt; border-bottom-color: var(--line); }
        """,
    },
    "rc-214": {
        "label": "RC214 天蓝时间序",
        "filename": "R06_RC214天蓝时间序",
        "use_case": "实习经历连续、需要突出成长顺序的通用与技术岗位",
        "source_id": "214",
        "source_url": "https://github.com/mmmlllnnn/ResumeCollection/tree/main/1.%E4%B8%AD%E6%96%87%E7%AE%80%E5%8E%86/214",
        "base_theme": "campus",
        "tokens": {"paper": "#FFFFFF", "ink": "#17242D", "muted": "#61717C", "line": "#B7D4E3", "brand": "#287EAA", "tint": "#EDF7FB"},
        "css": """
          header { background: transparent; padding: 0 0 2.3mm; border-bottom-color: var(--brand); }
          h1 { font-size: 26pt; }
          .section-title { color: var(--brand); font-size: 10.8pt; letter-spacing: .65pt; border-bottom-color: var(--line); }
          .entry-date { color: var(--brand); font-weight: 600; }
        """,
    },
}

LABELS = {
    "zh-CN": {
        "education": "教育经历",
        "experience": "实习与实践",
        "projects": "项目经历",
        "skills": "专业技能",
        "awards": "奖项与证书",
    },
    "en": {
        "education": "EDUCATION",
        "experience": "EXPERIENCE",
        "projects": "PROJECTS",
        "skills": "SKILLS",
        "awards": "AWARDS & CERTIFICATIONS",
    },
}

BILINGUAL_LABELS = {
    "education": "教育经历 · EDUCATION",
    "experience": "实习与实践 · EXPERIENCE",
    "projects": "项目经历 · PROJECTS",
    "skills": "专业技能 · SKILLS",
    "awards": "奖项与证书 · AWARDS",
}

DEFAULT_SECTION_ORDER = ("education", "experience", "projects", "skills", "awards")


def esc(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=True)


def safe_url(raw: Any) -> str:
    value = str(raw or "").strip()
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "mailto"}:
        return value
    return ""


def safe_basename(raw: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", "_", raw).strip(" ._")
    return cleaned[:96] or "resume"


def resolve_theme(raw: Any) -> str:
    theme_id = str(raw or "kami").strip()
    if theme_id not in THEMES:
        raise ValueError(f"未知主题：{theme_id}；可选值：{', '.join(THEME_ORDER)}")
    return theme_id


def resolve_reference_style(raw: Any) -> str | None:
    reference_style = str(raw or "").strip()
    if not reference_style:
        return None
    if reference_style not in REFERENCE_STYLES:
        raise ValueError(f"未知参考风格：{reference_style}；可选值：{', '.join(REFERENCE_STYLE_ORDER)}")
    return reference_style


def resolve_section_order(data: dict[str, Any]) -> list[str]:
    raw = data.get("section_order")
    if not isinstance(raw, list):
        return list(DEFAULT_SECTION_ORDER)
    requested = [str(value).strip() for value in raw if str(value).strip() in DEFAULT_SECTION_ORDER]
    ordered = list(dict.fromkeys(requested))
    ordered.extend(section for section in DEFAULT_SECTION_ORDER if section not in ordered)
    return ordered


def content_density(data: dict[str, Any]) -> str:
    entries = sum(len(data.get(section, []) or []) for section in ("education", "experience", "projects", "awards"))
    bullets: list[str] = []
    visible_parts: list[str] = []
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    visible_parts.extend(str(basics.get(field, "")) for field in ("name", "headline", "location", "summary"))
    for section in ("experience", "projects"):
        for item in data.get(section, []) or []:
            if not isinstance(item, dict):
                continue
            visible_parts.extend(str(item.get(field, "")) for field in ("organization", "name", "role", "location"))
            visible_parts.extend(str(value) for value in item.get("tech", []) or [])
            for bullet in item.get("bullets", []) or []:
                if isinstance(bullet, dict):
                    text = str(bullet.get("text", "")).strip()
                    if text:
                        bullets.append(text)
                        visible_parts.append(text)
    for item in data.get("education", []) or []:
        if isinstance(item, dict):
            visible_parts.extend(str(item.get(field, "")) for field in ("school", "degree", "major", "location"))
            visible_parts.extend(str(value) for value in item.get("details", []) or [])
    for group in data.get("skills", []) or []:
        if isinstance(group, dict):
            visible_parts.append(str(group.get("category", "")))
            visible_parts.extend(str(value) for value in group.get("items", []) or [])
    for award in data.get("awards", []) or []:
        if isinstance(award, dict):
            visible_parts.extend(str(award.get(field, "")) for field in ("name", "detail"))
    visible_text = "".join(visible_parts)
    active_sections = sum(bool(data.get(section)) for section in DEFAULT_SECTION_ORDER)
    score = len(visible_text) / 95 + len(bullets) * 1.25 + entries * 1.1 + active_sections * 0.8
    if score < 24:
        return "sparse"
    if score < 36:
        return "balanced"
    return "dense"


def date_range(item: dict[str, Any]) -> str:
    start = str(item.get("start", "")).strip()
    end = str(item.get("end", "")).strip()
    if start and end:
        return f"{start}\u202f–\u202f{end}"
    return start or end


def render_contact(basics: dict[str, Any]) -> str:
    items: list[str] = []
    for field in ("phone", "email", "location"):
        value = str(basics.get(field, "")).strip()
        if value:
            items.append(f"<span>{esc(value)}</span>")
    for link in basics.get("links", []) or []:
        if not isinstance(link, dict):
            continue
        url = safe_url(link.get("url"))
        if url:
            label = esc(link.get("label") or url)
            items.append(f'<a href="{esc(url)}">{label}</a>')
    return '<div class="contact">' + '<span class="dot">·</span>'.join(items) + "</div>"


def render_bullets(raw_bullets: Any) -> str:
    bullets: list[str] = []
    for bullet in raw_bullets or []:
        text = str(bullet.get("text", "")).strip() if isinstance(bullet, dict) else str(bullet).strip()
        if text:
            bullets.append(f"<li>{esc(text)}</li>")
    return "<ul>" + "".join(bullets) + "</ul>" if bullets else ""


def render_entry(item: dict[str, Any], *, project: bool = False) -> str:
    organization = esc(item.get("organization") or item.get("name"))
    role = esc(item.get("role"))
    location = esc(item.get("location"))
    dates = esc(date_range(item))
    right = " · ".join(part for part in (dates, location) if part)
    subtitle_bits: list[str] = []
    if role:
        subtitle_bits.append(role)
    tech = [str(value).strip() for value in (item.get("tech") or []) if str(value).strip()]
    if tech:
        subtitle_bits.append(" / ".join(esc(value) for value in tech))
    link = safe_url(item.get("link"))
    if link:
        subtitle_bits.append(f'<a href="{esc(link)}">{esc(item.get("link_label") or "项目链接")}</a>')
    subtitle = " · ".join(subtitle_bits)
    kind = " project" if project else ""
    return f"""
      <article class="entry{kind}">
        <div class="entry-head">
          <h3>{organization}</h3>
          <div class="entry-date">{right}</div>
        </div>
        {f'<div class="entry-sub">{subtitle}</div>' if subtitle else ''}
        {render_bullets(item.get('bullets'))}
      </article>
    """


def render_education(item: dict[str, Any]) -> str:
    school = esc(item.get("school"))
    credential = " · ".join(part for part in (esc(item.get("degree")), esc(item.get("major"))) if part)
    right = " · ".join(part for part in (esc(date_range(item)), esc(item.get("location"))) if part)
    details = [str(value).strip() for value in (item.get("details") or []) if str(value).strip()]
    details_html = '<div class="edu-details">' + " · ".join(esc(value) for value in details) + "</div>" if details else ""
    return f"""
      <article class="entry education-item">
        <div class="entry-head">
          <h3>{school}</h3>
          <div class="entry-date">{right}</div>
        </div>
        {f'<div class="entry-sub">{credential}</div>' if credential else ''}
        {details_html}
      </article>
    """


def render_section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return f'<section><h2 class="section-title">{esc(title)}</h2>{body}</section>'


def theme_css(theme_id: str, reference_style: str | None = None) -> str:
    common = f"""
    @page {{ size: A4; margin: var(--page-margin); background: var(--paper); }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ background: var(--paper); }}
    body {{ color: var(--ink); font-family: var(--body-font); font-size: var(--body-size); font-weight: 400; line-height: var(--line-height); letter-spacing: 0; font-kerning: normal; font-variant-numeric: lining-nums; text-rendering: optimizeLegibility; widows: 3; orphans: 3; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    body.density-sparse {{ --body-size: 10.15pt; --line-height: 1.52; --name-size: 29pt; --section-size: 11.35pt; --entry-size: 10.7pt; --sub-size: 9.25pt; --meta-size: 8.95pt; --contact-size: 9.1pt; --section-gap: 6.6mm; --entry-gap: 1.9mm; }}
    body.density-balanced {{ --body-size: 9.75pt; --line-height: 1.47; --section-gap: 5.5mm; --entry-gap: 1.4mm; }}
    body.density-dense {{ --body-size: 9.1pt; --line-height: 1.36; --name-size: 24pt; --section-size: 10.4pt; --entry-size: 10pt; --sub-size: 8.55pt; --meta-size: 8.25pt; --contact-size: 8.45pt; --section-gap: 3.6mm; --entry-gap: .9mm; }}
    main {{ width: 100%; }}
    header {{ margin-bottom: 4.8mm; padding-bottom: 2.5mm; border-bottom: .55pt solid var(--line); }}
    .identity {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 6mm; }}
    h1, h2, h3, .headline {{ font-family: var(--heading-font); }}
    h1 {{ font-size: var(--name-size); line-height: 1; letter-spacing: var(--name-tracking); font-weight: var(--name-weight); white-space: nowrap; text-wrap: balance; }}
    .position {{ text-align: right; min-width: 0; }}
    .headline {{ color: var(--brand); font-size: 10.2pt; font-weight: var(--section-weight); line-height: 1.25; letter-spacing: .12pt; text-wrap: balance; }}
    .contact {{ display: flex; flex-wrap: wrap; justify-content: flex-end; align-items: baseline; gap: 0 2mm; margin-top: 1.2mm; color: var(--muted); font-size: var(--contact-size); line-height: 1.4; font-variant-numeric: tabular-nums lining-nums; }}
    .contact .dot {{ color: var(--line); font-weight: 600; }}
    a {{ color: var(--brand); text-decoration: none; }}
    .summary {{ max-width: 94%; margin-top: 3mm; color: var(--ink); text-wrap: pretty; }}
    section {{ margin-top: var(--section-gap); }}
    section:first-of-type {{ margin-top: 0; }}
    .section-title {{ color: var(--ink); font-size: var(--section-size); line-height: 1.15; letter-spacing: .55pt; font-weight: var(--section-weight); padding-bottom: .85mm; margin-bottom: 1.6mm; border-bottom: .45pt solid var(--line); }}
    .entry {{ break-inside: avoid; page-break-inside: avoid; padding: .7mm 0 .45mm; }}
    .entry + .entry {{ margin-top: var(--entry-gap); }}
    .entry-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 4mm; }}
    h3 {{ font-size: var(--entry-size); line-height: 1.25; font-weight: var(--entry-weight); }}
    .entry-date {{ flex: 0 0 auto; color: var(--muted); font-size: var(--meta-size); white-space: nowrap; font-variant-numeric: tabular-nums lining-nums; }}
    .entry-sub {{ margin-top: .45mm; color: var(--muted); font-size: var(--sub-size); font-weight: 400; }}
    .entry-sub a {{ color: var(--brand); text-decoration: underline; text-decoration-thickness: .45pt; text-underline-offset: .16em; }}
    .edu-details {{ margin-top: .6mm; color: var(--muted); font-size: var(--meta-size); font-variant-numeric: tabular-nums lining-nums; }}
    ul {{ margin: .6mm 0 0; padding-left: 4.2mm; }}
    li {{ margin: .5mm 0; padding-left: .35mm; text-wrap: pretty; }}
    li::marker {{ color: var(--brand); }}
    .skill-row {{ display: grid; grid-template-columns: 5.4em 1fr; gap: 2.8mm; padding: .25mm 0; break-inside: avoid; }}
    .skill-row strong {{ color: var(--brand); font-family: var(--heading-font); font-weight: var(--entry-weight); }}
    .skill-row span {{ color: var(--ink); }}
    .award-row {{ display: flex; justify-content: space-between; gap: 4mm; padding: .55mm 0; break-inside: avoid; }}
    .award-row strong {{ font-weight: var(--entry-weight); }}
    .award-row time {{ flex: 0 0 auto; color: var(--muted); font-size: var(--meta-size); font-variant-numeric: tabular-nums lining-nums; }}
    @media screen {{ body {{ max-width: 184mm; min-height: 275mm; margin: 5mm auto; padding: var(--page-margin); }} }}
    """
    variants = {
        "ats-classic": """
          .identity { display: block; text-align: center; }
          h1 { font-size: var(--name-size); letter-spacing: 1.1pt; }
          .position { text-align: center; margin-top: 1.1mm; }
          .contact { justify-content: center; margin-top: .8mm; }
          .summary { text-align: left; margin-top: 2.3mm; }
          .section-title { color: var(--brand); font-size: var(--section-size); letter-spacing: 1pt; border-bottom-color: var(--brand); }
          li::marker { color: var(--ink); }
        """,
        "kami": """
          h1 { font-size: var(--name-size); letter-spacing: .5pt; }
          .headline { font-size: 10.6pt; }
          .summary { max-width: 92%; }
        """,
        "swiss": """
          header { padding-bottom: 2.8mm; border-bottom-color: var(--brand); }
          .identity { display: block; }
          h1 { font-size: var(--name-size); font-weight: 600; letter-spacing: -1pt; }
          .position { display: flex; align-items: baseline; justify-content: space-between; gap: 7mm; margin-top: 1.4mm; text-align: left; }
          .contact { justify-content: flex-end; margin-top: 0; }
          .headline { font-size: 10pt; letter-spacing: .35pt; }
          .summary { max-width: 93%; }
          .section-title { color: var(--brand); font-size: var(--section-size); letter-spacing: 1.45pt; text-transform: uppercase; border-bottom-color: var(--brand); }
          h3 { font-weight: 600; }
          .skill-row strong { letter-spacing: .35pt; }
        """,
        "tech": """
          header { padding: 2.3mm 2.8mm 2.5mm; background: linear-gradient(90deg, var(--tint), transparent 72%); border-bottom-color: var(--brand); }
          h1 { font-size: var(--name-size); letter-spacing: -.45pt; }
          .headline { font-family: var(--heading-font); font-size: 9.7pt; letter-spacing: .05pt; }
          .section-title { color: var(--brand); font-family: var(--heading-font); font-size: var(--section-size); letter-spacing: .5pt; border-bottom-color: var(--brand); }
          h3 { font-family: var(--body-font); font-weight: 600; }
          .entry-sub { color: var(--brand); }
          .entry-date, .award-row time { font-family: var(--mono-font); }
          .skill-row strong { font-family: var(--mono-font); font-size: 8.8pt; }
        """,
        "campus": """
          header { background: linear-gradient(105deg, var(--tint), transparent 58%); padding: 2.4mm 3mm 2.7mm; }
          h1 { font-size: var(--name-size); font-weight: 600; letter-spacing: -.35pt; }
          .headline { font-weight: 600; }
          .summary { max-width: 95%; }
          .section-title { color: var(--brand); font-size: var(--section-size); font-weight: 600; border-bottom-color: var(--line); }
          h3 { font-weight: 600; }
          .skill-row strong { font-weight: 600; }
        """,
        "compact": """
          header { margin-bottom: 3mm; padding-bottom: 1.8mm; }
          h1 { font-size: var(--name-size); }
          .headline { font-size: 9.4pt; }
          .contact { margin-top: .7mm; font-size: var(--contact-size); }
          .summary { margin-top: 1.9mm; }
          section { margin-top: 3mm; }
          .section-title { font-size: 10.4pt; padding-bottom: .65mm; margin-bottom: 1.05mm; }
          .entry { padding: .25mm 0; }
          .entry + .entry { margin-top: .8mm; }
          h3 { font-size: 10pt; }
          .entry-sub { margin-top: .15mm; font-size: 8.5pt; }
          .entry-date, .award-row time { font-size: 8.2pt; }
          ul { margin-top: .25mm; }
          li { margin: .2mm 0; }
          .skill-row { grid-template-columns: 5.2em 1fr; padding: 0; }
          .award-row { padding: .25mm 0; }
        """,
    }
    reference_css = REFERENCE_STYLES[reference_style]["css"] if reference_style else ""
    return common + variants[theme_id] + reference_css


def make_html(
    data: dict[str, Any],
    theme_id: str | None = None,
    reference_style: str | None = None,
) -> str:
    language = str(data.get("language", "zh-CN"))
    selected_reference = resolve_reference_style(reference_style or data.get("reference_style"))
    reference = REFERENCE_STYLES[selected_reference] if selected_reference else None
    labels = BILINGUAL_LABELS if selected_reference == "rc-109" and language == "zh-CN" else LABELS.get(language, LABELS["zh-CN"])
    selected_theme = resolve_theme(reference["base_theme"] if reference else (theme_id or data.get("theme")))
    theme = dict(THEMES[selected_theme])
    if reference:
        theme.update(reference["tokens"])
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    name = esc(basics.get("name"))
    headline = esc(basics.get("headline") or target.get("role"))
    summary = esc(basics.get("summary"))
    density = content_density(data)

    education = "".join(render_education(item) for item in data.get("education", []) if isinstance(item, dict))
    experience = "".join(render_entry(item) for item in data.get("experience", []) if isinstance(item, dict))
    projects = "".join(render_entry(item, project=True) for item in data.get("projects", []) if isinstance(item, dict))

    skill_rows: list[str] = []
    for group in data.get("skills", []) or []:
        if not isinstance(group, dict):
            continue
        values = [esc(value) for value in (group.get("items") or []) if str(value).strip()]
        if values:
            skill_rows.append(f'<div class="skill-row"><strong>{esc(group.get("category"))}</strong><span>{" · ".join(values)}</span></div>')

    award_rows: list[str] = []
    for award in data.get("awards", []) or []:
        if not isinstance(award, dict):
            continue
        left = esc(award.get("name"))
        detail = esc(award.get("detail"))
        date = esc(award.get("date"))
        award_rows.append(f'<div class="award-row"><span><strong>{left}</strong>{f" · {detail}" if detail else ""}</span><time>{date}</time></div>')

    section_bodies = {
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": "".join(skill_rows),
        "awards": "".join(award_rows),
    }
    rendered_sections = "".join(
        render_section(labels[section], section_bodies[section]) for section in resolve_section_order(data)
    )

    lang_attr = "en" if language == "en" else "zh-CN"
    style_label = reference["label"] if reference else theme["label"]
    title = esc(f"{basics.get('name', '')} - {target.get('role', '')} - {style_label}")
    use_medium_face = bool(data.get("_kami_medium_available"))
    if selected_theme == "kami" and not use_medium_face:
        theme["name_weight"] = 400
        theme["section_weight"] = 400
        theme["entry_weight"] = 400
    medium_face = (
        '@font-face { font-family: "TsangerJinKai02"; src: local("TsangerJinKai02 W05"), local("仓耳今楷02 W05"); font-weight: 500; font-style: normal; }'
        if use_medium_face
        else ""
    )
    css_vars = ";".join(
        [
            f"--paper:{theme['paper']}",
            f"--ink:{theme['ink']}",
            f"--muted:{theme['muted']}",
            f"--line:{theme['line']}",
            f"--brand:{theme['brand']}",
            f"--tint:{theme['tint']}",
            f"--body-font:{theme['body_font']}",
            f"--heading-font:{theme['heading_font']}",
            f"--mono-font:{theme['mono_font']}",
            f"--page-margin:{theme['page_margin']}",
            f"--body-size:{theme['body_size']}",
            f"--line-height:{theme['line_height']}",
            f"--name-size:{theme['name_size']}",
            f"--section-size:{theme['section_size']}",
            f"--entry-size:{theme['entry_size']}",
            f"--sub-size:{theme['sub_size']}",
            f"--meta-size:{theme['meta_size']}",
            f"--contact-size:{theme['contact_size']}",
            f"--section-gap:{theme['section_gap']}",
            f"--entry-gap:{theme['entry_gap']}",
            f"--name-weight:{theme['name_weight']}",
            f"--section-weight:{theme['section_weight']}",
            f"--entry-weight:{theme['entry_weight']}",
            "--name-tracking:.45pt",
        ]
    )
    return f"""<!doctype html>
<html lang="{lang_attr}" data-theme="{selected_theme}" data-density="{density}"{f' data-reference-style="{selected_reference}"' if selected_reference else ''}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="generator" content="Qiaomu Campus Resume · Core and reference style system">
  <meta name="resume-theme" content="{selected_theme}">
  <meta name="resume-typography-system" content="1.5">
  <meta name="resume-layout-system" content="adaptive-density-1.0">
  {f'<meta name="resume-reference-style" content="{selected_reference}">' if selected_reference else ''}
  <title>{title}</title>
  <style>
    :root{{{css_vars};}}
    @font-face {{ font-family: "TsangerJinKai02"; src: local("TsangerJinKai02 W04"), local("仓耳今楷02 W04"), local("TsangerJinKai02"); font-weight: 400; font-style: normal; }}
    {medium_face}
    {theme_css(selected_theme, selected_reference)}
  </style>
</head>
<body class="theme-{selected_theme} density-{density}">
<main>
  <header>
    <div class="identity">
      <h1>{name}</h1>
      <div class="position">
        {f'<div class="headline">{headline}</div>' if headline else ''}
        {render_contact(basics)}
      </div>
    </div>
    {f'<p class="summary">{summary}</p>' if summary else ''}
  </header>
  {rendered_sections}
</main>
</body>
</html>
"""


def find_browser() -> str | None:
    configured = os.environ.get("RESUME_BROWSER", "").strip()
    candidates = [
        configured,
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
        shutil.which("microsoft-edge") or "",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def find_tsanger_faces() -> dict[str, Path]:
    configured = Path(os.environ.get("KAMI_FONT_DIR", "")).expanduser() if os.environ.get("KAMI_FONT_DIR") else None
    directories = [
        configured,
        Path.home() / "Library" / "Fonts",
        Path("/Library/Fonts"),
        Path.home() / ".local" / "share" / "fonts" / "kami",
        Path.home() / ".local" / "share" / "fonts",
    ]
    faces: dict[str, Path] = {}
    for directory in directories:
        if not directory or not directory.is_dir():
            continue
        for weight, filename in (("regular", "TsangerJinKai02-W04.ttf"), ("medium", "TsangerJinKai02-W05.ttf")):
            candidate = directory / filename
            if candidate.is_file() and candidate.stat().st_size > 100_000:
                faces.setdefault(weight, candidate)
    return faces


def print_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    pdf_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="qiaomu-resume-chrome-") as profile:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        deadline = time.monotonic() + 30
        stable_since: float | None = None
        previous_size = -1
        generated = False
        while time.monotonic() < deadline:
            if pdf_path.is_file() and pdf_path.stat().st_size > 1024:
                size = pdf_path.stat().st_size
                if size == previous_size:
                    stable_since = stable_since or time.monotonic()
                    if time.monotonic() - stable_since >= 1.0:
                        generated = pdf_path.read_bytes()[:5] == b"%PDF-"
                        break
                else:
                    previous_size = size
                    stable_since = None
            if process.poll() is not None:
                generated = pdf_path.is_file() and pdf_path.read_bytes()[:5] == b"%PDF-"
                break
            time.sleep(0.2)

        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
        stdout, stderr = process.communicate(timeout=5)
    if not generated:
        message = stderr.strip() or stdout.strip() or "浏览器未在 30 秒内生成有效 PDF"
        raise RuntimeError(message)


def render_one(
    data: dict[str, Any],
    *,
    theme_id: str,
    output_dir: Path,
    basename: str,
    browser: str | None,
    html_only: bool,
    faces: dict[str, Path],
    reference_style: str | None = None,
) -> dict[str, Any]:
    reference = REFERENCE_STYLES[reference_style] if reference_style else None
    theme = dict(THEMES[theme_id])
    if reference:
        theme.update(reference["tokens"])
    if data.get("language", "zh-CN") != "en" and theme_id == "kami" and "regular" not in faces and not html_only:
        raise RuntimeError(
            "Kami 主题缺少 TsangerJinKai02 W04。请取得字体许可后安装，或设置 KAMI_FONT_DIR。"
        )
    render_data = dict(data)
    render_data["theme"] = theme_id
    render_data["_kami_medium_available"] = "medium" in faces
    html_path = output_dir / f"{basename}.html"
    pdf_path = output_dir / f"{basename}.pdf"
    if reference_style:
        render_data["reference_style"] = reference_style
    else:
        render_data.pop("reference_style", None)
    html_path.write_text(make_html(render_data, theme_id, reference_style), encoding="utf-8")
    item: dict[str, Any] = {
        "theme": theme_id,
        "label": reference["label"] if reference else theme["label"],
        "use_case": reference["use_case"] if reference else theme["use_case"],
        "html": str(html_path),
        "pdf": None,
        "font_requirement": theme["required_font"],
    }
    if reference:
        item.update(
            {
                "reference_style": reference_style,
                "source_id": reference["source_id"],
                "source_url": reference["source_url"],
            }
        )
    if not html_only:
        if not browser:
            raise RuntimeError("未找到 Chrome、Chromium 或 Edge；可设置 RESUME_BROWSER。")
        print_pdf(browser, html_path, pdf_path)
        item["pdf"] = str(pdf_path)
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description="将结构化大学生简历渲染为本地 HTML 与 PDF。")
    parser.add_argument("input", help="resume-data.json 路径")
    parser.add_argument("--output-dir", "-o", default="output", help="输出目录")
    parser.add_argument("--basename", help="输出文件名（不含扩展名）；默认读取 JSON filename")
    parser.add_argument("--theme", choices=THEME_ORDER, help="覆盖 JSON 中的主题")
    parser.add_argument("--all-themes", "--six-styles", action="store_true", help="一次生成六套 HTML/PDF")
    parser.add_argument("--reference-style", choices=REFERENCE_STYLE_ORDER, help="选择一个 ResumeCollection 重构参考预设")
    parser.add_argument("--all-reference-styles", action="store_true", help="一次生成六套 ResumeCollection 重构参考预设")
    parser.add_argument("--html-only", action="store_true", help="只生成 HTML，不调用浏览器")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法读取简历 JSON：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if not isinstance(data, dict):
        parser.error("简历 JSON 根节点必须是对象")

    if args.all_themes and args.all_reference_styles:
        parser.error("--all-themes 与 --all-reference-styles 不能同时使用")
    if (args.reference_style or args.all_reference_styles) and args.theme:
        parser.error("参考风格会自动选择基础主题，不能同时传入 --theme")
    try:
        if args.all_reference_styles:
            selections = [(REFERENCE_STYLES[style]["base_theme"], style) for style in REFERENCE_STYLE_ORDER]
            set_type = "reference_styles"
        elif args.all_themes:
            selections = [(theme, None) for theme in THEME_ORDER]
            set_type = "core_themes"
        else:
            selected_reference = resolve_reference_style(args.reference_style or data.get("reference_style"))
            selected_theme = resolve_theme(REFERENCE_STYLES[selected_reference]["base_theme"] if selected_reference else (args.theme or data.get("theme")))
            selections = [(selected_theme, selected_reference)]
            set_type = "single"
    except ValueError as exc:
        parser.error(str(exc))
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    base = safe_basename(args.basename or str(data.get("filename") or "resume"))
    faces = find_tsanger_faces() if data.get("language", "zh-CN") != "en" else {}
    browser = None if args.html_only else find_browser()

    outputs: list[dict[str, Any]] = []
    try:
        for theme_id, reference_style in selections:
            style = REFERENCE_STYLES[reference_style] if reference_style else THEMES[theme_id]
            rendered_basename = base if len(selections) == 1 else safe_basename(f"{base}_{style['filename']}")
            outputs.append(
                render_one(
                    data,
                    theme_id=theme_id,
                    output_dir=output_dir,
                    basename=rendered_basename,
                    browser=browser,
                    html_only=args.html_only,
                    faces=faces,
                    reference_style=reference_style,
                )
            )
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"简历渲染失败：{exc}", file=sys.stderr)
        raise SystemExit(4) from exc

    manifest = {
        "ok": True,
        "input": str(input_path),
        "renderer": None if args.html_only or not browser else Path(browser).name,
        "set_type": set_type,
        "theme_count": len(outputs),
        "outputs": outputs,
    }
    if len(outputs) > 1:
        suffix = "参考风格清单" if set_type == "reference_styles" else "六风格清单"
        manifest_path = output_dir / f"{base}_{suffix}.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["manifest"] = str(manifest_path)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
