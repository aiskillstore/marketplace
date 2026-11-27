#!/usr/bin/env python3
"""Subtitle indexing and no-spoiler watch-session helpers."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


TIME_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*"
    r"(?P<end>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})"
)


@dataclass
class Cue:
    start: float
    end: float
    text: str
    track: str


def parse_time(value: str) -> float:
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Invalid timestamp: {value}")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    if ms == 1000:
        whole += 1
        ms = 0
    h = whole // 3600
    m = (whole % 3600) // 60
    s = whole % 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def clean_text(lines: Iterable[str]) -> str:
    text = " ".join(line.strip() for line in lines if line.strip())
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{\\.*?\}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_subtitles(path: Path, track: str) -> list[Cue]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n"))
    cues: list[Cue] = []
    for block in blocks:
        lines = [line for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        time_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if time_index is None:
            continue
        match = TIME_RE.search(lines[time_index])
        if not match:
            continue
        text = clean_text(lines[time_index + 1 :])
        if text:
            cues.append(Cue(parse_time(match.group("start")), parse_time(match.group("end")), text, track))
    return cues


def default_state_dir() -> Path:
    return Path.cwd() / ".movie-companion"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_index(args: argparse.Namespace) -> None:
    sources: list[tuple[Path, str]] = []
    for subtitle in args.subtitle:
        sources.append((Path(subtitle).expanduser().resolve(), "dialogue"))
    for description in args.description or []:
        sources.append((Path(description).expanduser().resolve(), "description"))
    cues: list[Cue] = []
    for path, track in sources:
        cues.extend(parse_subtitles(path, track))
    cues.sort(key=lambda cue: (cue.start, cue.end, cue.track))
    if not cues:
        raise SystemExit("No subtitle cues found")
    primary = sources[0][0]
    out = Path(args.output).expanduser().resolve() if args.output else primary.with_suffix(".movie-index.json")
    payload = {
        "movie": args.movie or primary.stem,
        "sources": [{"path": str(path), "track": track} for path, track in sources],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cue_count": len(cues),
        "duration_seconds": max(cue.end for cue in cues),
        "cues": [asdict(cue) for cue in cues],
    }
    write_json(out, payload)
    print(json.dumps({"index": str(out), "cue_count": len(cues), "duration": format_time(payload["duration_seconds"])}, indent=2))


def cmd_start(args: argparse.Namespace) -> None:
    index = Path(args.index).expanduser().resolve()
    if not index.exists():
        raise SystemExit(f"Index not found: {index}")
    state_dir = Path(args.state_dir).expanduser().resolve() if args.state_dir else default_state_dir()
    session = Path(args.session).expanduser().resolve() if args.session else state_dir / "watch-session.json"
    payload = {
        "index": str(index),
        "mode": "screening",
        "started_at_wall_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_movie_seconds": parse_time(args.at),
        "playback_rate": float(args.rate),
        "safety_lag_seconds": float(args.safety_lag),
    }
    write_json(session, payload)
    print(json.dumps({"session": str(session), "started_at": format_time(payload["started_at_movie_seconds"]), "safety_lag_seconds": payload["safety_lag_seconds"]}, indent=2))


def estimate_time(session: dict) -> tuple[float, float]:
    mode = session.get("mode", "screening")
    if mode == "paused":
        estimated = float(session["paused_at_movie_seconds"])
        safe = max(0.0, estimated - float(session.get("safety_lag_seconds", 8.0)))
        return estimated, safe
    if mode == "closed":
        estimated = float(session.get("closed_at_movie_seconds", session.get("started_at_movie_seconds", 0.0)))
        safe = max(0.0, estimated - float(session.get("safety_lag_seconds", 8.0)))
        return estimated, safe
    started_wall = datetime.fromisoformat(session["started_at_wall_utc"])
    now = datetime.now(timezone.utc)
    elapsed = (now - started_wall).total_seconds() * float(session.get("playback_rate", 1.0))
    estimated = float(session["started_at_movie_seconds"]) + elapsed
    safe = max(0.0, estimated - float(session.get("safety_lag_seconds", 8.0)))
    return estimated, safe


def cmd_where(args: argparse.Namespace) -> None:
    session = read_json(Path(args.session).expanduser().resolve())
    estimated, safe = estimate_time(session)
    print(json.dumps({"mode": session.get("mode", "screening"), "estimated_time": format_time(estimated), "safe_time": format_time(safe), "safe_seconds": safe}, indent=2))


def context_payload(session_path: Path, before: float, after: float, require_open: bool = False) -> dict:
    session = read_json(session_path)
    mode = session.get("mode", "screening")
    if require_open and mode == "closed":
        raise SystemExit("Session is closed. Start or resume with a visible timestamp before asking.")
    estimated, safe = estimate_time(session)
    index = read_json(Path(session["index"]))
    start = max(0.0, safe - before)
    end = safe + after
    cues = [
        cue
        for cue in index["cues"]
        if float(cue["end"]) >= start and float(cue["start"]) <= end and float(cue["end"]) <= safe + max(0.0, after)
    ]
    return {
        "movie": index.get("movie"),
        "mode": mode,
        "estimated_time": format_time(estimated),
        "safe_time": format_time(safe),
        "lookback_start": format_time(start),
        "future_window_seconds": after,
        "cues": cues,
    }


def cmd_context(args: argparse.Namespace) -> None:
    payload = context_payload(Path(args.session).expanduser().resolve(), float(args.before), float(args.after))
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_ask(args: argparse.Namespace) -> None:
    payload = context_payload(Path(args.session).expanduser().resolve(), float(args.before), 0.0, require_open=True)
    payload["instruction"] = (
        "Answer only from cues ending at or before safe_time. "
        "Do not use later plot knowledge. If visual detail is missing from text tracks, say so."
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def update_session(path: Path, updates: dict) -> dict:
    session = read_json(path)
    session.update(updates)
    write_json(path, session)
    return session


def cmd_pause(args: argparse.Namespace) -> None:
    session_path = Path(args.session).expanduser().resolve()
    session = read_json(session_path)
    mode = session.get("mode", "screening")
    if mode == "closed":
        raise SystemExit("Session is closed. Start a new session before pausing.")
    estimated, safe = estimate_time(session)
    session = update_session(
        session_path,
        {
            "mode": "paused",
            "paused_at_wall_utc": datetime.now(timezone.utc).isoformat(),
            "paused_at_movie_seconds": estimated,
        },
    )
    print(json.dumps({"session": str(session_path), "mode": session["mode"], "paused_at": format_time(estimated), "safe_time": format_time(safe)}, indent=2))


def cmd_close(args: argparse.Namespace) -> None:
    session_path = Path(args.session).expanduser().resolve()
    session = read_json(session_path)
    estimated, safe = estimate_time(session)
    session = update_session(
        session_path,
        {
            "mode": "closed",
            "closed_at_wall_utc": datetime.now(timezone.utc).isoformat(),
            "closed_at_movie_seconds": estimated,
        },
    )
    print(json.dumps({"session": str(session_path), "mode": session["mode"], "closed_at": format_time(estimated), "safe_time": format_time(safe)}, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    session_path = Path(args.session).expanduser().resolve()
    session = read_json(session_path)
    estimated, safe = estimate_time(session)
    print(
        json.dumps(
            {
                "session": str(session_path),
                "mode": session.get("mode", "screening"),
                "estimated_time": format_time(estimated),
                "safe_time": format_time(safe),
                "index": session.get("index"),
            },
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="No-spoiler movie companion sync helper")
    sub = parser.add_subparsers(dest="command", required=True)

    index = sub.add_parser("index", help="Parse SRT/VTT subtitles into a timed JSON index")
    index.add_argument("--subtitle", required=True, action="append", help="Dialogue subtitle SRT/VTT. May be repeated.")
    index.add_argument("--description", action="append", help="Descriptive subtitle, SDH, or audio-description SRT/VTT. May be repeated.")
    index.add_argument("--movie")
    index.add_argument("--output")
    index.set_defaults(func=cmd_index)

    start = sub.add_parser("start", help="Start or resync a watch session")
    start.add_argument("--index", required=True)
    start.add_argument("--at", required=True, help="Current visible movie timestamp, e.g. 00:12:30")
    start.add_argument("--rate", default=1.0)
    start.add_argument("--safety-lag", default=8.0)
    start.add_argument("--session")
    start.add_argument("--state-dir")
    start.set_defaults(func=cmd_start)

    where = sub.add_parser("where", help="Show estimated current and safe movie time")
    where.add_argument("--session", required=True)
    where.set_defaults(func=cmd_where)

    context = sub.add_parser("context", help="Return subtitle context bounded by the safe time")
    context.add_argument("--session", required=True)
    context.add_argument("--before", default=600.0, help="Seconds to include before safe time")
    context.add_argument("--after", default=0.0, help="Future seconds; keep 0 during no-spoiler viewing")
    context.set_defaults(func=cmd_context)

    ask = sub.add_parser("ask", help="Return the current no-spoiler bundle for answering an in-screening question")
    ask.add_argument("--session", required=True)
    ask.add_argument("--before", default=900.0, help="Seconds to include before safe time")
    ask.set_defaults(func=cmd_ask)

    pause = sub.add_parser("pause", help="Pause a watch session and freeze the estimated movie time")
    pause.add_argument("--session", required=True)
    pause.set_defaults(func=cmd_pause)

    close = sub.add_parser("close", help="Close a watch session so future asks require a restart or resync")
    close.add_argument("--session", required=True)
    close.set_defaults(func=cmd_close)

    status = sub.add_parser("status", help="Show watch session mode and current safe time")
    status.add_argument("--session", required=True)
    status.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
