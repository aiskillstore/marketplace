from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from sharextract.models import ExtractedContent

from .extractors.base import ExtractorError


_TIMELINE_RE = re.compile(
    r"^(?P<start>(?:\d{1,}:)?\d{2}:\d{2}[.,]\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{1,}:)?\d{2}:\d{2}[.,]\d{3})(?:\s+(?P<settings>.*))?$"
)
_SRT_TYPES = {
    "application/x-subrip",
    "application/srt",
    "text/srt",
}
_TTML_TYPES = {
    "application/ttml+xml",
    "application/ttaf+xml",
}


class _CueTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def try_extract_timed_text(
    source_url: str,
    final_url: str,
    content_type: str,
    raw: str,
) -> ExtractedContent | None:
    """Recognize and normalize public WebVTT, SRT, or TTML documents."""
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    stripped = raw.lstrip("\ufeff\r\n\t ")

    if ctype == "text/vtt" or stripped.startswith("WEBVTT"):
        cues = _parse_webvtt(raw)
        if cues:
            return _build_result(
                source_url,
                final_url,
                "webvtt",
                "standard_webvtt",
                cues,
            )
        if ctype == "text/vtt":
            raise ExtractorError("WebVTT document contained no readable cues.")

    if ctype in _SRT_TYPES or _looks_like_srt(stripped):
        cues = _parse_srt(raw)
        if cues:
            return _build_result(
                source_url,
                final_url,
                "srt",
                "standard_srt",
                cues,
            )
        if ctype in _SRT_TYPES:
            raise ExtractorError("SRT document contained no readable cues.")

    if ctype in _TTML_TYPES or _looks_like_xml(stripped):
        result = _parse_ttml(raw)
        if result is not None:
            cues, language, title = result
            if not cues:
                raise ExtractorError("TTML document contained no readable cues.")
            return _build_result(
                source_url,
                final_url,
                "ttml",
                "standard_ttml",
                cues,
                language=language,
                title=title,
            )

    return None


def _parse_webvtt(raw: str) -> list[dict[str, Any]]:
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.lstrip("\ufeff").split("\n")
    if not lines or not lines[0].strip().startswith("WEBVTT"):
        return []

    cues: list[dict[str, Any]] = []
    index = 1
    while index < len(lines):
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines):
            break

        marker = lines[index].strip()
        if marker.startswith(("NOTE", "STYLE", "REGION")):
            index += 1
            while index < len(lines) and lines[index].strip():
                index += 1
            continue

        cue_id = ""
        timeline_line = marker
        if "-->" not in timeline_line:
            cue_id = marker
            index += 1
            if index >= len(lines):
                break
            timeline_line = lines[index].strip()

        match = _TIMELINE_RE.match(timeline_line)
        if not match:
            index += 1
            while index < len(lines) and lines[index].strip():
                index += 1
            continue

        index += 1
        payload_lines: list[str] = []
        while index < len(lines) and lines[index].strip():
            payload_lines.append(lines[index])
            index += 1

        raw_text = "\n".join(payload_lines).strip()
        text, speaker = _clean_cue_text(raw_text)
        if not text:
            continue

        cue = _cue(
            cue_id=cue_id,
            start=match.group("start"),
            end=match.group("end"),
            text=text,
        )
        settings = (match.group("settings") or "").strip()
        if settings:
            cue["settings"] = settings
        if speaker:
            cue["speaker"] = speaker
        cues.append(cue)

    return cues


def _parse_srt(raw: str) -> list[dict[str, Any]]:
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", normalized.strip())
    cues: list[dict[str, Any]] = []

    for block in blocks:
        lines = [line.rstrip() for line in block.split("\n")]
        if not lines:
            continue

        cue_id = ""
        timeline_index = 0
        if "-->" not in lines[0]:
            cue_id = lines[0].strip()
            timeline_index = 1
        if timeline_index >= len(lines):
            continue

        match = _TIMELINE_RE.match(lines[timeline_index].strip())
        if not match:
            continue

        raw_text = "\n".join(lines[timeline_index + 1 :]).strip()
        text, speaker = _clean_cue_text(raw_text)
        if not text:
            continue

        cue = _cue(
            cue_id=cue_id,
            start=match.group("start"),
            end=match.group("end"),
            text=text,
        )
        if speaker:
            cue["speaker"] = speaker
        cues.append(cue)

    return cues


def _parse_ttml(
    raw: str,
) -> tuple[list[dict[str, Any]], str, str] | None:
    prefix = raw[:8192].lower()
    if "<!doctype" in prefix or "<!entity" in prefix:
        raise ExtractorError(
            "TTML document contains a DTD/entity declaration and was rejected."
        )

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    if _local_name(root.tag).lower() != "tt":
        return None

    language = (
        root.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
        or root.attrib.get("lang")
        or ""
    )
    title = ""
    for element in root.iter():
        if _local_name(element.tag).lower() == "title":
            candidate = _element_text(element)
            if candidate:
                title = candidate
                break

    cues: list[dict[str, Any]] = []
    for element in root.iter():
        if _local_name(element.tag).lower() != "p":
            continue
        text = _element_text(element)
        if not text:
            continue

        start_raw = str(element.attrib.get("begin") or "").strip()
        end_raw = str(element.attrib.get("end") or "").strip()
        duration_raw = str(element.attrib.get("dur") or "").strip()
        start_seconds = _parse_ttml_time(start_raw)
        end_seconds = _parse_ttml_time(end_raw)
        duration_seconds = _parse_ttml_time(duration_raw)

        if end_seconds is None and start_seconds is not None and duration_seconds is not None:
            end_seconds = start_seconds + duration_seconds
            end_raw = _format_timestamp(end_seconds)

        cue: dict[str, Any] = {
            "id": (
                element.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                or element.attrib.get("id")
                or ""
            ),
            "start": (
                _format_timestamp(start_seconds)
                if start_seconds is not None
                else start_raw
            ),
            "end": (
                _format_timestamp(end_seconds)
                if end_seconds is not None
                else end_raw
            ),
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "text": text,
        }
        cues.append(cue)

    return cues, language, title


def _build_result(
    source_url: str,
    final_url: str,
    format_name: str,
    method: str,
    cues: list[dict[str, Any]],
    *,
    language: str = "",
    title: str = "",
) -> ExtractedContent:
    inferred_language = ""
    if not language:
        inferred_language = _language_from_url(final_url)
        language = inferred_language
    if not title:
        title = _title_from_url(final_url)

    text = "\n".join(
        str(cue.get("text") or "").strip()
        for cue in cues
        if str(cue.get("text") or "").strip()
    )
    markdown = "\n\n".join(
        _render_cue_markdown(cue)
        for cue in cues
        if str(cue.get("text") or "").strip()
    )
    duration = max(
        (
            float(cue["end_seconds"])
            for cue in cues
            if isinstance(cue.get("end_seconds"), (int, float))
        ),
        default=0.0,
    )

    return ExtractedContent(
        source_url=source_url,
        canonical_url=final_url,
        platform="timed-text",
        kind="transcript",
        extraction_method=method,
        confidence=0.99,
        title=title,
        text=text,
        markdown=markdown,
        metadata={
            "transcript": {
                "format": format_name,
                "language": language,
                "language_source": "url_filename" if inferred_language else ("document" if language else ""),
                "cue_count": len(cues),
                "duration_seconds": duration or None,
                "cues": cues,
            },
            "standard": {
                "webvtt": "WebVTT",
                "srt": "SubRip",
                "ttml": "TTML",
            }[format_name],
        },
    )


def _cue(
    *,
    cue_id: str,
    start: str,
    end: str,
    text: str,
) -> dict[str, Any]:
    start_seconds = _parse_clock_time(start)
    end_seconds = _parse_clock_time(end)
    return {
        "id": cue_id,
        "start": _format_timestamp(start_seconds) if start_seconds is not None else start,
        "end": _format_timestamp(end_seconds) if end_seconds is not None else end,
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "text": text,
    }


def _clean_cue_text(value: str) -> tuple[str, str]:
    speaker = ""
    voice = re.search(r"<v(?:\.[^ >]+)?\s+([^>]+)>", value, flags=re.IGNORECASE)
    if voice:
        speaker = html.unescape(voice.group(1)).strip()

    parser = _CueTextParser()
    try:
        parser.feed(value)
        parser.close()
        text = parser.text
    except Exception:
        text = re.sub(r"<[^>]+>", "", value)
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text, speaker


def _render_cue_markdown(cue: dict[str, Any]) -> str:
    timestamp = str(cue.get("start") or "").strip()
    speaker = str(cue.get("speaker") or "").strip()
    text = str(cue.get("text") or "").strip()
    prefix = f"**{speaker}:** " if speaker else ""
    return f"[{timestamp}] {prefix}{text}".strip()


def _looks_like_srt(value: str) -> bool:
    lines = [line.strip() for line in value[:4096].splitlines() if line.strip()]
    if not lines:
        return False
    if _TIMELINE_RE.match(lines[0]):
        return True
    return len(lines) >= 2 and lines[0].isdigit() and bool(
        _TIMELINE_RE.match(lines[1])
    )


def _looks_like_xml(value: str) -> bool:
    lowered = value[:512].lower()
    return lowered.startswith("<?xml") or lowered.startswith("<tt") or ":tt" in lowered


def _parse_clock_time(value: str) -> float | None:
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    try:
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return None
    return None


def _parse_ttml_time(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None

    clock = _parse_clock_time(value)
    if clock is not None:
        return clock

    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(h|m|s|ms)", value)
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2)
    return {
        "h": amount * 3600,
        "m": amount * 60,
        "s": amount,
        "ms": amount / 1000,
    }[unit]


def _format_timestamp(value: float | None) -> str:
    if value is None:
        return ""
    total_ms = max(0, int(round(value * 1000)))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def _title_from_url(url: str) -> str:
    path = unquote(urlsplit(url).path)
    name = PurePosixPath(path).name
    for suffix in (".vtt", ".srt", ".ttml", ".xml"):
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)]
            break
    language = _language_token(name.rsplit(".", 1)[-1]) if "." in name else ""
    if language:
        name = name.rsplit(".", 1)[0]
    return name.replace("-", " ").replace("_", " ").strip() or "Public transcript"


def _language_from_url(url: str) -> str:
    path = unquote(urlsplit(url).path)
    name = PurePosixPath(path).name
    for suffix in (".vtt", ".srt", ".ttml", ".xml"):
        if name.lower().endswith(suffix):
            stem = name[: -len(suffix)]
            if "." in stem:
                return _language_token(stem.rsplit(".", 1)[-1])
            break
    return ""


def _language_token(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", value):
        return value
    return ""


def _element_text(element: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def _local_name(tag: Any) -> str:
    if not isinstance(tag, str):
        return ""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag
