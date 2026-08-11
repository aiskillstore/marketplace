#!/usr/bin/env python3
"""Build the canonical Brandkit PPTX and matching verified PDF locally.

It edits the fixed OOXML template directly, preserves its geometry, consumes
only separately approved Brandkit state, and writes files into the user's
project workspace.
"""

from __future__ import annotations

import argparse
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from typing import Any, Callable
from urllib.parse import quote, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener
import zipfile

from brandkit import assert_public_host, normalize_hex, read_state, slug, tls_context


TEMPLATE_URL = (
    "https://docs.google.com/presentation/d/"
    "1rAfUJ-PbZ4S-h3puYSUHpE5UIcdKyRw1/export/pptx"
)
MAX_TEMPLATE_BYTES = 12 * 1024 * 1024
MAX_ASSET_BYTES = 16 * 1024 * 1024
MAX_FONT_CSS_BYTES = 256 * 1024
MAX_FONT_BYTES = 8 * 1024 * 1024
MAX_MOCKUPS = 8
COMMAND_TIMEOUT_SECONDS = 90
SLIDE_WIDTH = "24384000"
SLIDE_HEIGHT = "13716000"
TITLE_SHAPES = ((1, "4312"), (2, "4315"), (3, "4318"), (4, "4325"), (5, "4337"), (6, "4341"), (7, "4343"))
REQUIRED_SHAPES = (
    (1, "4312"), (1, "4313"), (2, "4315"), (2, "4316"), (3, "4318"),
    (3, "4319"), (4, "4321"), (4, "4322"), (4, "4323"), (4, "4324"),
    (4, "4325"), (5, "4327"), (5, "4328"), (5, "4329"),
    (5, "4330"), (5, "4331"), (5, "4332"), (5, "4333"), (5, "4334"),
    (5, "4335"), (5, "4336"), (5, "4337"), (5, "4338"), (6, "4340"),
    (6, "4341"), (7, "4343"), (7, "4344"), (7, "4345"),
)
Archive = dict[str, bytes]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_bytes(url: str, limit: int, redirects: int = 2) -> bytes:
    opener = build_opener(NoRedirect, HTTPSHandler(context=tls_context()))
    current = url
    for _ in range(redirects + 1):
        parsed = urlparse(current)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username:
            raise RuntimeError("Brandbook resources must use https with a public host")
        assert_public_host(parsed.hostname)
        try:
            response = opener.open(
                Request(current, headers={"User-Agent": "higgsfield-brandkit/1"}),
                timeout=30,
            )
        except Exception as error:
            code = getattr(error, "code", None)
            headers = getattr(error, "headers", None)
            if code in {301, 302, 303, 307, 308} and headers:
                location = headers.get("Location")
                if location:
                    current = urljoin(current, location)
                    continue
            raise RuntimeError(f"failed to download Brandbook resource: {error}") from error
        declared = int(response.headers.get("Content-Length", "0") or "0")
        if declared > limit:
            raise RuntimeError(f"Brandbook resource exceeds {limit} bytes")
        data = response.read(limit + 1)
        if len(data) > limit:
            raise RuntimeError(f"Brandbook resource exceeds {limit} bytes")
        return data
    raise RuntimeError("too many Brandbook resource redirects")


def read_archive(data: bytes) -> Archive:
    try:
        with zipfile.ZipFile(BytesIO(data)) as source:
            return {name: source.read(name) for name in source.namelist()}
    except zipfile.BadZipFile as error:
        raise RuntimeError("canonical Brandbook template is not a PPTX archive") from error


def write_archive(entries: Archive, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        for name in sorted(entries):
            target.writestr(name, entries[name])


def read_xml(entries: Archive, name: str) -> str:
    if name not in entries:
        raise RuntimeError(f"brandbook template is missing {name}")
    return entries[name].decode("utf-8")


def write_xml(entries: Archive, name: str, value: str) -> None:
    entries[name] = value.encode("utf-8")


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def update_shape(
    xml: str, shape_id: str, update: Callable[[str], str], tag: str = "sp"
) -> str:
    found = False
    pattern = re.compile(rf"<p:{tag}\b[\s\S]*?</p:{tag}>")
    id_pattern = re.compile(rf'<p:cNvPr\b[^>]*\bid="{re.escape(shape_id)}"(?:\s|/|>)')

    def replace(match: re.Match[str]) -> str:
        nonlocal found
        block = match.group(0)
        if not id_pattern.search(block):
            return block
        found = True
        return update(block)

    result = pattern.sub(replace, xml)
    if not found:
        raise RuntimeError(f"brandbook template shape {shape_id} is missing")
    return result


def find_shape(xml: str, shape_id: str) -> str | None:
    for match in re.finditer(r"<p:sp\b[\s\S]*?</p:sp>", xml):
        block = match.group(0)
        if re.search(rf'<p:cNvPr\b[^>]*\bid="{re.escape(shape_id)}"(?:\s|/|>)', block):
            return block
    return None


def remove_shape(xml: str, shape_id: str, tag: str = "sp") -> str:
    return update_shape(xml, shape_id, lambda _block: "", tag)


def replace_shape_texts(xml: str, shape_id: str, values: list[str]) -> str:
    def replace(block: str) -> str:
        index = 0

        def text(match: re.Match[str]) -> str:
            nonlocal index
            value = values[index] if index < len(values) else ""
            index += 1
            return f"<a:t>{escape_xml(value)}</a:t>"

        result = re.sub(r"<a:t>[\s\S]*?</a:t>", text, block)
        if index != len(values):
            raise RuntimeError(
                f"brandbook template shape {shape_id} expected {len(values)} text runs, found {index}"
            )
        return result

    return update_shape(xml, shape_id, replace)


def run_properties(
    inner: str, family: str, color: str, normal_spacing: bool
) -> str:
    expanded = re.sub(r"<a:rPr\b([^>]*)/>", r"<a:rPr\1></a:rPr>", inner, count=1)
    match = re.search(r"<a:rPr\b([^>]*)>([\s\S]*?)</a:rPr>", expanded)
    attributes = match.group(1) if match else ""
    if normal_spacing:
        if re.search(r'\bspc="[^"]*"', attributes):
            attributes = re.sub(r'\bspc="[^"]*"', 'spc="0"', attributes)
        else:
            attributes += ' spc="0"'
    children = match.group(2) if match else ""
    children = re.sub(r"<a:solidFill>[\s\S]*?</a:solidFill>", "", children)
    children = re.sub(
        r"<a:(?:latin|ea|cs)\b[^>]*/>|<a:(?:latin|ea|cs)\b[\s\S]*?</a:(?:latin|ea|cs)>",
        "",
        children,
    )
    face = escape_xml(family)
    props = (
        f'<a:rPr{attributes}><a:solidFill><a:srgbClr val="{color}"/>'
        f'</a:solidFill><a:latin typeface="{face}"/><a:ea typeface="{face}"/>'
        f'<a:cs typeface="{face}"/>{children}</a:rPr>'
    )
    return expanded.replace(match.group(0), props, 1) if match else props + inner


def style_shape_runs(
    xml: str,
    shape_id: str,
    families: list[str],
    color: str,
    normal_spacing: bool,
) -> str:
    def replace(block: str) -> str:
        index = 0

        def run(match: re.Match[str]) -> str:
            nonlocal index
            family = families[min(index, len(families) - 1)]
            index += 1
            return f"<a:r>{run_properties(match.group(1), family, color, normal_spacing)}</a:r>"

        result = re.sub(r"<a:r>([\s\S]*?)</a:r>", run, block)
        if index == 0:
            raise RuntimeError(f"brandbook template shape {shape_id} has no text runs")
        return result

    return update_shape(xml, shape_id, replace)


def set_shape_fill(xml: str, shape_id: str, fill: str, border: str | None) -> str:
    def update(block: str) -> str:
        def properties(match: re.Match[str]) -> str:
            inner = re.sub(r"<a:solidFill>[\s\S]*?</a:solidFill>", "", match.group(1))
            inner = re.sub(r"<a:ln\b[\s\S]*?</a:ln>|<a:ln\b[^>]*/>", "", inner)
            line = (
                f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{border}"/>'
                "</a:solidFill></a:ln>"
                if border
                else "<a:ln><a:noFill/></a:ln>"
            )
            decoration = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{line}'
            updated, count = re.subn(
                r"(<a:prstGeom\b[\s\S]*?</a:prstGeom>|<a:prstGeom\b[^>]*/>)",
                rf"\1{decoration}",
                inner,
                count=1,
            )
            return f"<p:spPr>{updated if count else inner + decoration}</p:spPr>"

        return re.sub(r"<p:spPr>([\s\S]*?)</p:spPr>", properties, block, count=1)

    return update_shape(xml, shape_id, update)


def set_slide_background(xml: str, color: str) -> str:
    background = (
        f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{color}"/>'
        "</a:solidFill><a:effectLst/></p:bgPr></p:bg>"
    )
    if re.search(r"<p:bg>[\s\S]*?</p:bg>", xml):
        return re.sub(r"<p:bg>[\s\S]*?</p:bg>", background, xml, count=1)
    return re.sub(r"(<p:cSld\b[^>]*>)", rf"\1{background}", xml, count=1)


def enforce_single_line_title(xml: str, shape_id: str) -> str:
    def update(block: str) -> str:
        off = re.search(r'<a:off\b[^>]*\bx="(\d+)"[^>]*/>', block)
        width = int(SLIDE_WIDTH) - int(off.group(1)) - 537006 if off else 0
        result = re.sub(r"<a:br\b[^>]*/>|<a:br\b[\s\S]*?</a:br>", "", block)

        def body(match: re.Match[str]) -> str:
            attrs = re.sub(r'\s+wrap="[^"]*"', "", match.group(1))
            return f'<a:bodyPr{attrs} wrap="none"{match.group(2)}>'

        result = re.sub(r"<a:bodyPr\b([^>]*?)(/?)>", body, result, count=1)
        if width > 0:
            result = re.sub(
                r'(<a:ext\b[^>]*\bcx=")\d+("[^>]*/>)',
                rf"\g<1>{width}\2",
                result,
                count=1,
            )
        return result

    return update_shape(xml, shape_id, update)


def update_picture_embed(xml: str, shape_id: str, relationship_id: str) -> str:
    return update_shape(
        xml,
        shape_id,
        lambda block: re.sub(
            r'(<a:blip\b[^>]*\br:embed=")[^"]+(")',
            rf"\g<1>{relationship_id}\2",
            block,
            count=1,
        ),
        "pic",
    )


def clear_picture_crop(xml: str, shape_id: str) -> str:
    return update_shape(
        xml,
        shape_id,
        lambda block: re.sub(
            r"<a:srcRect\b[^>]*/>|<a:srcRect\b[\s\S]*?</a:srcRect>",
            "<a:srcRect/>",
            block,
        ),
        "pic",
    )


def add_relationship(
    xml: str,
    relationship_id: str,
    target: str,
    relation_type: str = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
) -> str:
    relation = (
        f'<Relationship Id="{relationship_id}" Type="{relation_type}" '
        f'Target="{target}"/>'
    )
    return xml.replace("</Relationships>", relation + "</Relationships>")


def update_relationship_target(xml: str, relationship_id: str, target: str) -> str:
    pattern = re.compile(
        rf'(<Relationship\b[^>]*\bId="{re.escape(relationship_id)}"'
        r'[^>]*\bTarget=")[^"]+(")'
    )
    if not pattern.search(xml):
        raise RuntimeError(f"brandbook template relationship {relationship_id} is missing")
    return pattern.sub(rf"\g<1>{target}\2", xml, count=1)


def color(value: str) -> str:
    normalized = value.strip()
    if re.fullmatch(r"[0-9a-f]{6}", normalized, re.IGNORECASE):
        normalized = f"#{normalized}"
    return normalize_hex(normalized)[1:].upper()


def rgb_label(value: str) -> str:
    integer = int(color(value), 16)
    return f"R{integer // 65536 % 256} G{integer // 256 % 256} B{integer % 256}"


def luminance(value: str) -> float:
    integer = int(color(value), 16)
    channels = [integer // 65536 % 256, integer // 256 % 256, integer % 256]
    linear = [
        channel / 255 / 12.92
        if channel / 255 <= 0.03928
        else ((channel / 255 + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def contrast_color(background: str) -> str:
    return "111111" if luminance(background) > 0.55 else "F7F7F5"


def choose_color(colors: list[dict[str, Any]], pattern: str) -> str | None:
    return next(
        (str(item["hex"]) for item in colors if re.search(pattern, str(item.get("role", "")), re.I)),
        None,
    )


def title_color(
    colors: list[dict[str, Any]], background: str, preferred: str
) -> str:
    candidates = [preferred]
    candidates.extend(
        str(item["hex"])
        for item in colors
        if re.search(r"text|ink|foreground|accent|primary", str(item.get("role", "")), re.I)
    )
    candidates.extend(str(item["hex"]) for item in colors)
    unique = list(dict.fromkeys(color(item) for item in candidates))
    ranked = sorted(
        (item for item in unique if item != color(background)),
        key=lambda item: contrast_ratio(item, background),
        reverse=True,
    )
    return next(
        (item for item in ranked if contrast_ratio(item, background) >= 3),
        contrast_color(background),
    )


def validate_template(entries: Archive) -> None:
    presentation = read_xml(entries, "ppt/presentation.xml")
    if not re.search(
        rf'<p:sldSz\b[^>]*\bcx="{SLIDE_WIDTH}"[^>]*\bcy="{SLIDE_HEIGHT}"',
        presentation,
    ):
        raise RuntimeError("brandbook template is not the approved 16:9 canvas")
    for slide, shape_id in REQUIRED_SHAPES:
        xml = read_xml(entries, f"ppt/slides/slide{slide}.xml")
        if not re.search(rf'<p:cNvPr\b[^>]*\bid="{shape_id}"(?:\s|/|>)', xml):
            raise RuntimeError(
                f"brandbook template contract mismatch: slide {slide}, shape {shape_id}"
            )


def remove_slide(entries: Archive, slide_number: int) -> None:
    rels_name = "ppt/_rels/presentation.xml.rels"
    rels = read_xml(entries, rels_name)
    match = re.search(
        rf'<Relationship\b[^>]*\bId="([^"]+)"[^>]*'
        rf'\bTarget="slides/slide{slide_number}\.xml"[^>]*/>',
        rels,
    )
    if not match:
        raise RuntimeError(f"brandbook template slide {slide_number} relationship missing")
    write_xml(entries, rels_name, rels.replace(match.group(0), "", 1))
    presentation = read_xml(entries, "ppt/presentation.xml")
    presentation = re.sub(
        rf'<p:sldId\b[^>]*\br:id="{re.escape(match.group(1))}"[^>]*/>',
        "",
        presentation,
        count=1,
    )
    write_xml(entries, "ppt/presentation.xml", presentation)


def add_slide(entries: Archive, slide_number: int) -> None:
    relationship_id = f"rIdBrandkit{slide_number}"
    rels_name = "ppt/_rels/presentation.xml.rels"
    write_xml(
        entries,
        rels_name,
        add_relationship(
            read_xml(entries, rels_name),
            relationship_id,
            f"slides/slide{slide_number}.xml",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
        ),
    )
    presentation = read_xml(entries, "ppt/presentation.xml")
    ids = [int(value) for value in re.findall(r'<p:sldId\b[^>]*\bid="(\d+)"', presentation)]
    slide_id = max([255, *ids]) + slide_number
    write_xml(
        entries,
        "ppt/presentation.xml",
        presentation.replace(
            "</p:sldIdLst>",
            f'<p:sldId id="{slide_id}" r:id="{relationship_id}"/></p:sldIdLst>',
        ),
    )
    write_xml(
        entries,
        "[Content_Types].xml",
        read_xml(entries, "[Content_Types].xml").replace(
            "</Types>",
            f'<Override PartName="/ppt/slides/slide{slide_number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.slide+xml"/></Types>',
        ),
    )


def source_bytes(source: str, limit: int) -> bytes:
    if source.startswith("https://"):
        return fetch_bytes(source, limit)
    path = Path(source).resolve()
    data = path.read_bytes()
    if len(data) > limit:
        raise RuntimeError(f"Brandbook asset exceeds {limit} bytes")
    return data


def asset_source(value: Any, label: str) -> str:
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be an object with path or url")
    source = str(value.get("path") or value.get("url") or "").strip()
    if not source:
        raise RuntimeError(f"{label} requires path or url")
    return source


def convert_png(data: bytes, width: int, height: int, fit: str) -> bytes:
    binary = shutil.which("magick") or shutil.which("convert")
    if not binary:
        raise RuntimeError("ImageMagick is unavailable in the local environment")
    suffix = ".svg" if b"<svg" in data[:1024].lower() else ".img"
    with tempfile.TemporaryDirectory(prefix="brandkit-image-") as directory:
        source = Path(directory) / f"input{suffix}"
        output = Path(directory) / "output.png"
        source.write_bytes(data)
        conversion_source = source
        if suffix == ".svg":
            rsvg_convert = shutil.which("rsvg-convert")
            if not rsvg_convert:
                raise RuntimeError(
                    "rsvg-convert is unavailable in the local environment"
                )
            conversion_source = Path(directory) / "input.png"
            try:
                subprocess.run(
                    [
                        rsvg_convert,
                        "--format",
                        "png",
                        "--width",
                        str(width),
                        "--height",
                        str(height),
                        "--keep-aspect-ratio",
                        "--output",
                        str(conversion_source),
                        str(source),
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=COMMAND_TIMEOUT_SECONDS,
                )
            except subprocess.CalledProcessError as error:
                detail = (error.stdout or b"").decode("utf-8", "replace").strip()
                raise RuntimeError(
                    f"Brandbook SVG conversion failed: {detail}"
                ) from error
        resize = f"{width}x{height}{'^' if fit == 'cover' else ''}"
        command = [
            binary,
            "-background",
            "none",
            str(conversion_source),
            "-resize",
            resize,
            "-gravity",
            "center",
            "-extent",
            f"{width}x{height}",
            str(output),
        ]
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except subprocess.CalledProcessError as error:
            detail = (error.stdout or b"").decode("utf-8", "replace").strip()
            raise RuntimeError(f"Brandbook image conversion failed: {detail}") from error
        return output.read_bytes()


def font_extension(data: bytes) -> str:
    signature = data[:4]
    if signature == b"OTTO":
        return "otf"
    if signature == b"wOFF":
        return "woff"
    if signature == b"wOF2":
        return "woff2"
    if signature == b"\x00\x01\x00\x00":
        return "ttf"
    raise RuntimeError("approved font source is not TTF, OTF, WOFF, or WOFF2")


def resolve_fonts(choice: dict[str, Any]) -> list[tuple[str, bytes]]:
    family = str(choice.get("family", "")).strip()
    source = str(choice.get("source", "")).strip()
    weight = int(choice.get("weight", 400))
    style = str(choice.get("style", "normal"))
    if not family:
        raise RuntimeError("approved typography requires a font family")
    if source.startswith("google:"):
        requested = source.removeprefix("google:").strip() or family
        axis = f"ital,wght@1,{weight}" if style == "italic" else f"wght@{weight}"
        css_url = (
            "https://fonts.googleapis.com/css2?family="
            + quote(requested).replace("%20", "+")
            + f":{axis}&display=swap"
        )
        css = fetch_bytes(css_url, MAX_FONT_CSS_BYTES).decode("utf-8")
        urls = list(dict.fromkeys(re.findall(r"url\(\s*[\"']?(https:[^)\"']+)", css)))
        if not urls:
            raise RuntimeError(f"Google Fonts returned no files for '{family}'")
    elif source.startswith("https://"):
        urls = [source]
    else:
        path = Path(source).expanduser().resolve()
        if not path.is_file():
            raise RuntimeError(
                f"approved font '{family}' requires a local file, public font URL, or google: source"
            )
        data = path.read_bytes()
        if len(data) > MAX_FONT_BYTES:
            raise RuntimeError(f"approved font '{family}' exceeds {MAX_FONT_BYTES} bytes")
        return [(f"{slug(f'{family}-{style}-{weight}')}.{font_extension(data)}", data)]
    stem = slug(f"{family}-{style}-{weight}")
    assets: list[tuple[str, bytes]] = []
    for index, url in enumerate(urls, start=1):
        data = fetch_bytes(url, MAX_FONT_BYTES)
        assets.append((f"{stem}-{index}.{font_extension(data)}", data))
    return assets


def place_mockups(
    entries: Archive, mockups: list[dict[str, Any]]
) -> None:
    if not mockups:
        remove_slide(entries, 7)
        return
    base_slide = read_xml(entries, "ppt/slides/slide7.xml")
    base_rels = read_xml(entries, "ppt/slides/_rels/slide7.xml.rels")
    for pair in range((len(mockups) + 1) // 2):
        slide_number = 7 + pair
        first_index = pair * 2
        second_index = first_index + 1
        slide = base_slide
        rels = re.sub(
            r'(<Relationship\b[^>]*\bId="rId2"[^>]*\bTarget=")[^"]+(")',
            rf"\g<1>../media/brandkit-mockup-{first_index + 1}.png\2",
            base_rels,
            count=1,
        )
        entries[f"ppt/media/brandkit-mockup-{first_index + 1}.png"] = convert_png(
            source_bytes(
                asset_source(mockups[first_index], f"mockups[{first_index}]"),
                MAX_ASSET_BYTES,
            ),
            1200,
            1600,
            "cover",
        )
        if second_index < len(mockups):
            relation = f"rIdBrandkitMockup{second_index + 1}"
            slide = update_picture_embed(slide, "4345", relation)
            rels = add_relationship(
                rels,
                relation,
                f"../media/brandkit-mockup-{second_index + 1}.png",
            )
            entries[f"ppt/media/brandkit-mockup-{second_index + 1}.png"] = convert_png(
                source_bytes(
                    asset_source(mockups[second_index], f"mockups[{second_index}]"),
                    MAX_ASSET_BYTES,
                ),
                1200,
                1600,
                "cover",
            )
        else:
            slide = remove_shape(slide, "4345", "pic")
        if pair > 0:
            add_slide(entries, slide_number)
        write_xml(entries, f"ppt/slides/slide{slide_number}.xml", slide)
        write_xml(entries, f"ppt/slides/_rels/slide{slide_number}.xml.rels", rels)


def png_metadata(data: bytes) -> tuple[int, int, bool]:
    if len(data) < 33 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Brandbook image output is not a PNG")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
    del bit_depth
    has_alpha = color_type in {4, 6} or b"tRNS" in data
    return width, height, has_alpha


def validate_output(
    entries: Archive,
    slide_count: int,
    display_family: str,
    has_secondary: bool,
    mockup_count: int,
) -> dict[str, Any]:
    presentation = read_xml(entries, "ppt/presentation.xml")
    active = re.findall(r'<p:sldId\b[^>]*\br:id="[^"]+"', presentation)
    if len(active) != slide_count:
        raise RuntimeError(
            f"brandbook output slide count mismatch: {len(active)} != {slide_count}"
        )
    forbidden = (
        "Name of the Company/Brand",
        "Concept Text",
        "Palette text",
        "Name of display font",
        "Name of body font",
    )
    for slide_number in range(1, slide_count + 1):
        xml = read_xml(entries, f"ppt/slides/slide{slide_number}.xml")
        for placeholder in forbidden:
            if placeholder in xml:
                raise RuntimeError(
                    f"brandbook output still contains '{placeholder}' on slide {slide_number}"
                )
        title_id = dict(TITLE_SHAPES).get(min(slide_number, 7), "4343")
        block = find_shape(xml, title_id)
        if not block or (
            f'typeface="{escape_xml(display_family)}"' not in block
            or 'spc="0"' not in block
            or 'wrap="none"' not in block
            or re.search(r"<a:br\b", block)
        ):
            raise RuntimeError(f"brandbook title style mismatch on slide {slide_number}")
    typography = read_xml(entries, "ppt/slides/slide6.xml")
    if 'sz="16000"' not in typography or 'spc="0"' not in typography:
        raise RuntimeError("brandbook typography specimen size/spacing changed")
    logo_width, logo_height, _ = png_metadata(entries.get("ppt/media/image6.png", b""))
    if (logo_width, logo_height) != (2000, 2000):
        raise RuntimeError("brandbook primary logo canvas is not square")
    if has_secondary:
        width, height, has_alpha = png_metadata(
            entries.get("ppt/media/brandkit-secondary.png", b"")
        )
        if (width, height) != (1600, 1600) or not has_alpha:
            raise RuntimeError(
                "brandbook secondary logo must be a transparent square PNG"
            )
    for index in range(1, mockup_count + 1):
        width, height, _ = png_metadata(
            entries.get(f"ppt/media/brandkit-mockup-{index}.png", b"")
        )
        if (width, height) != (1200, 1600):
            raise RuntimeError(f"brandbook mockup {index} aspect ratio changed")
    return {
        "canvas": f"{SLIDE_WIDTH}x{SLIDE_HEIGHT}",
        "mockup_px": "1200x1600" if mockup_count else None,
        "placeholder_residue": False,
        "primary_logo_px": "2000x2000",
        "secondary_logo": has_secondary,
        "slide_count": slide_count,
        "title_font": display_family,
        "title_letter_spacing": "normal",
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Brandbook input must be a JSON object")
    state = read_state(args.state_file.resolve())
    missing = [slot for slot in ("logo", "palette", "typography") if not state.get(slot)]
    if missing:
        raise RuntimeError(
            "brandbook build requires separately approved slots: " + ", ".join(missing)
        )
    brand_name = str(payload.get("brand_name", "")).strip()
    concept = str(payload.get("concept_summary", "")).strip()
    if not brand_name or len(brand_name) > 60:
        raise RuntimeError("brand_name is required and must be at most 60 characters")
    if not concept or len(concept) > 500:
        raise RuntimeError("concept_summary is required and must be at most 500 characters")
    mockups = payload.get("mockups", [])
    if not isinstance(mockups, list) or len(mockups) > MAX_MOCKUPS:
        raise RuntimeError(f"mockups must contain at most {MAX_MOCKUPS} items")

    logo = state["logo"]
    palette = state["palette"]
    typography = state["typography"]
    colors = palette.get("colors", [])
    if not isinstance(colors, list) or not colors or len(colors) > 5:
        raise RuntimeError("canonical Brandbook requires one to five primary colors")
    display = typography.get("display")
    body = typography.get("body")
    if not isinstance(display, dict) or not isinstance(body, dict):
        raise RuntimeError("approved typography requires display and body choices")

    entries = read_archive(fetch_bytes(TEMPLATE_URL, MAX_TEMPLATE_BYTES, redirects=4))
    validate_template(entries)
    background_hex = choose_color(colors, r"background") or str(colors[0]["hex"])
    background = color(background_hex)
    text_hex = choose_color(colors, r"text|ink|foreground") or f"#{contrast_color(background)}"
    text = color(text_hex)
    preferred_title = (
        choose_color(colors, r"primary|accent")
        or next((str(item["hex"]) for item in colors if item["hex"] != background_hex), text_hex)
    )
    title = title_color(colors, background_hex, preferred_title)
    display_family = str(display["family"])
    body_family = str(body["family"])

    slide = read_xml(entries, "ppt/slides/slide1.xml")
    slide = replace_shape_texts(slide, "4312", ["Brand Guidelines"])
    slide = replace_shape_texts(slide, "4313", [brand_name])
    slide = style_shape_runs(slide, "4312", [display_family], title, True)
    slide = style_shape_runs(slide, "4313", [display_family], text, True)
    write_xml(entries, "ppt/slides/slide1.xml", slide)

    slide = read_xml(entries, "ppt/slides/slide2.xml")
    slide = replace_shape_texts(slide, "4315", ["Branding concept"])
    slide = replace_shape_texts(slide, "4316", [concept])
    slide = style_shape_runs(slide, "4315", [display_family], title, True)
    slide = style_shape_runs(slide, "4316", [body_family], text, False)
    write_xml(entries, "ppt/slides/slide2.xml", slide)

    asset = logo.get("asset", {})
    logo_source = str(asset.get("url") or asset.get("path") or "").strip()
    if not logo_source:
        raise RuntimeError("approved logo requires a public URL or readable local path")
    entries["ppt/media/image6.png"] = convert_png(
        source_bytes(logo_source, MAX_ASSET_BYTES), 2000, 2000, "contain"
    )
    write_xml(
        entries,
        "ppt/slides/slide3.xml",
        clear_picture_crop(read_xml(entries, "ppt/slides/slide3.xml"), "4319"),
    )

    variants = logo.get("variants", {}) if isinstance(logo.get("variants"), dict) else {}
    secondary_source = str(payload.get("secondary_logo_url", "")).strip()
    if not secondary_source:
        reverse = "white" if contrast_color(background) == "F7F7F5" else "black"
        variant = variants.get(reverse, {}) if isinstance(variants.get(reverse), dict) else {}
        secondary_source = str(variant.get("url") or variant.get("path") or "").strip()
    slide = read_xml(entries, "ppt/slides/slide4.xml")
    slide = clear_picture_crop(slide, "4322")
    slide = replace_shape_texts(slide, "4324", ["Primary"])
    slide = style_shape_runs(slide, "4324", [body_family], text, False)
    if secondary_source:
        slide = clear_picture_crop(slide, "4323")
        slide = replace_shape_texts(slide, "4321", ["Secondary"])
        slide = style_shape_runs(slide, "4321", [body_family], text, False)
        entries["ppt/media/brandkit-secondary.png"] = convert_png(
            source_bytes(secondary_source, MAX_ASSET_BYTES), 1600, 1600, "contain"
        )
        rels_name = "ppt/slides/_rels/slide4.xml.rels"
        write_xml(
            entries,
            rels_name,
            update_relationship_target(
                read_xml(entries, rels_name), "rId3", "../media/brandkit-secondary.png"
            ),
        )
    else:
        slide = remove_shape(slide, "4321")
        slide = remove_shape(slide, "4323", "pic")
    write_xml(entries, "ppt/slides/slide4.xml", slide)

    slide = read_xml(entries, "ppt/slides/slide5.xml")
    slide = replace_shape_texts(
        slide,
        "4338",
        [str(payload.get("palette_summary") or palette.get("approvalSummary") or "")],
    )
    slide = style_shape_runs(slide, "4338", [body_family], text, False)
    for index in range(5):
        swatch_id = str(4327 + index)
        label_id = str(4332 + index)
        if index >= len(colors):
            slide = remove_shape(slide, swatch_id)
            slide = remove_shape(slide, label_id)
            continue
        item = colors[index]
        item_color = color(str(item["hex"]))
        slide = set_shape_fill(
            slide,
            swatch_id,
            item_color,
            text if item_color == background else None,
        )
        slide = replace_shape_texts(slide, swatch_id, [""])
        slide = replace_shape_texts(
            slide,
            label_id,
            [str(item["name"]), rgb_label(str(item["hex"])), f"#{item_color}"],
        )
        slide = style_shape_runs(
            slide, label_id, [body_family], contrast_color(item_color), False
        )
    write_xml(entries, "ppt/slides/slide5.xml", slide)

    slide = read_xml(entries, "ppt/slides/slide6.xml")
    slide = replace_shape_texts(slide, "4340", [display_family, body_family])
    slide = style_shape_runs(slide, "4340", [display_family, body_family], text, True)
    slide = re.sub(r'(<a:defRPr\b[^>]*\bspc=")[^"]+("[^>]*>)', r'\g<1>0\2', slide)
    write_xml(entries, "ppt/slides/slide6.xml", slide)

    place_mockups(entries, mockups)
    slide_count = 6 + ((len(mockups) + 1) // 2)
    for slide_number in range(1, slide_count + 1):
        name = f"ppt/slides/slide{slide_number}.xml"
        slide = set_slide_background(read_xml(entries, name), background)
        title_id = dict(TITLE_SHAPES).get(min(slide_number, 7), "4343")
        if re.search(rf'<p:cNvPr\b[^>]*\bid="{title_id}"', slide):
            slide = enforce_single_line_title(slide, title_id)
            slide = style_shape_runs(slide, title_id, [display_family], title, True)
        write_xml(entries, name, slide)

    qa = validate_output(
        entries, slide_count, display_family, bool(secondary_source), len(mockups)
    )
    revision = int(payload.get("revision", 1))
    if revision < 1 or revision > 999:
        raise RuntimeError("revision must be from 1 to 999")
    stem = f"{slug(brand_name)}-brand-guidelines-v{revision}"
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    pptx = output_dir / f"{stem}.pptx"
    pdf = output_dir / f"{stem}.pdf"
    write_archive(entries, pptx)
    renderer = Path(__file__).with_name("render_brandbook_pdf.py")
    with tempfile.TemporaryDirectory(
        prefix=".brandkit-render-", dir=output_dir
    ) as temporary:
        render_root = Path(temporary)
        fonts_dir = render_root / "fonts"
        fonts_dir.mkdir()
        for choice in (display, body):
            for file_name, data in resolve_fonts(choice):
                (fonts_dir / file_name).write_bytes(data)
        families = [display_family, body_family]
        families_json = render_root / "families.json"
        families_json.write_text(json.dumps(families), encoding="utf-8")
        try:
            subprocess.run(
                [
                    os.sys.executable,
                    str(renderer),
                    "--work-dir",
                    str(render_root / "work"),
                    "--pptx",
                    str(pptx),
                    "--fonts-dir",
                    str(fonts_dir),
                    "--families-json",
                    str(families_json),
                    "--output",
                    str(pdf),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS + 30,
            )
        except subprocess.CalledProcessError as error:
            detail = (error.stdout or "").strip()
            raise RuntimeError(
                f"Brandbook PDF conversion failed{f': {detail}' if detail else ''}"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("Brandbook PDF conversion timed out") from error
    return {
        "action": "build",
        "files": [str(pptx), str(pdf)],
        "font_requirements": {
            "body": body,
            "display": display,
            "embedded_in_pdf": True,
            "links": typography.get("fontLinks", []),
        },
        "pdf": {"status": "generated_from_pptx"},
        "qa": qa,
        "slide_count": slide_count,
        "template": {
            "canvas": f"{SLIDE_WIDTH}x{SLIDE_HEIGHT}",
            "version": "2026-07-23-v3",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--state-file", type=Path, default=Path("brandkit/state.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("brandkit/brandbook"))
    return parser.parse_args()


def main() -> None:
    try:
        print(json.dumps(build(parse_args()), separators=(",", ":")))
    except subprocess.CalledProcessError as error:
        detail = getattr(error, "stdout", None)
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", "replace")
        print(str(detail or error), file=os.sys.stderr)
        raise SystemExit(1) from error
    except Exception as error:
        print(str(error), file=os.sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
