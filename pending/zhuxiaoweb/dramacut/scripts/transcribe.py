"""Normalize word-level ASR JSON or run an external transcription command."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shlex
import shutil
import subprocess
from pathlib import Path


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2))


def seconds(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be a finite nonnegative number of seconds")
    return round(value*1_000_000)


def normalize(payload):
    raw_segments = payload.get("segments")
    raw_words = payload.get("words")
    if not isinstance(raw_segments, list) and not isinstance(raw_words, list):
        raise ValueError("ASR JSON needs a segments array with word timestamps or a top-level words array")
    words = []
    segments = []
    if isinstance(raw_segments, list):
        for segment_index, segment in enumerate(raw_segments, 1):
            if not isinstance(segment, dict):
                raise ValueError("Every ASR segment must be an object")
            segment_words = segment.get("words") or []
            if not segment_words:
                if segment.get("text", "").strip():
                    raise ValueError(f"ASR segment {segment_index} has text but no word timestamps")
                continue
            segment_id = f"segment-{segment_index:04d}"
            normalized = {"id": segment_id, "text": segment.get("text", ""), "word_ids": []}
            segments.append(normalized)
            for word in segment_words:
                words.append((segment_id, word))
    else:
        for word in raw_words:
            words.append((None, word))
    if not words:
        raise ValueError("No word-level timestamps found; enable word timestamps in the ASR engine")
    normalized_words = []
    for segment_id, word in words:
        if not isinstance(word, dict):
            raise ValueError("Every ASR word must be an object")
        text = word.get("word", word.get("text"))
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Every ASR word needs nonempty word/text content")
        start = seconds(word.get("start"), "Word start")
        end = seconds(word.get("end"), "Word end")
        if end <= start:
            raise ValueError(f"Word end must exceed start: {text!r}")
        normalized_words.append({"segment_id": segment_id, "start_us": start, "end_us": end, "text": text.strip()})
    normalized_words.sort(key=lambda row: (row["start_us"], row["end_us"], row["segment_id"] or ""))
    by_segment = {}
    for index, word in enumerate(normalized_words, 1):
        identifier = f"word-{index:06d}"
        word["id"] = identifier
        if word["segment_id"]:
            by_segment.setdefault(word["segment_id"], []).append(word)
    for segment in segments:
        owned = by_segment.get(segment["id"], [])
        if not owned:
            raise ValueError(f"ASR segment {segment['id']} has no normalized words")
        segment["word_ids"] = [word["id"] for word in owned]
        segment["start_us"] = owned[0]["start_us"]
        segment["end_us"] = max(word["end_us"] for word in owned)
    duration = max(word["end_us"] for word in normalized_words)
    if "duration" in payload:
        duration = max(duration, seconds(payload["duration"], "ASR duration"))
    return {"duration_us": duration, "language": payload.get("language"),
            "words": normalized_words, "segments": segments}


def transcribe(args):
    source = Path(args.input).resolve(strict=True)
    if not source.is_file():
        raise ValueError("Transcription input must be a media file")
    workspace = Path(args.workspace).resolve()
    if workspace.exists():
        raise ValueError("Transcription workspace must be new")
    if args.timeout <= 0:
        raise ValueError("Transcription timeout must be positive")
    before = sha(source)
    workspace.mkdir(parents=True)
    raw = workspace / "asr-raw.json"
    executable = None
    if args.transcript:
        supplied = Path(args.transcript).resolve(strict=True)
        shutil.copyfile(supplied, raw)
        mode = "normalized_existing"
    else:
        if "{input}" not in args.command or "{output}" not in args.command:
            raise ValueError("External command must contain {input} and {output} placeholders")
        argv = [part.format(input=str(source), output=str(raw), workspace=str(workspace))
                for part in shlex.split(args.command)]
        if not argv:
            raise ValueError("External transcription command is empty")
        executable = Path(argv[0]).name
        with (workspace / "transcribe.log").open("wb") as log:
            process = subprocess.run(argv, cwd=workspace, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=args.timeout,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if process.returncode or not raw.is_file():
            raise ValueError(f"External transcription failed ({process.returncode}); see {workspace / 'transcribe.log'}")
        mode = "external_command"
    payload = json.loads(raw.read_bytes())
    normalized = normalize(payload)
    if sha(source) != before:
        raise ValueError("Media changed during transcription")
    transcript = {"schema_version": 1, "source_path": str(source), "source_sha256": before,
                  "raw_sha256": sha(raw), "word_timestamps": True,
                  "transcription_mode": mode, "executable": executable,
                  "subjective_audio_listening": False, **normalized,
                  "limitations": "ASR words and timestamps require source-audio review; normalization does not prove recognition accuracy"}
    save(workspace / "transcript.json", transcript)
    return {"status": "transcript_ready", "transcript": str(workspace / "transcript.json"),
            "source_sha256": before, "word_count": len(transcript["words"]),
            "segment_count": len(transcript["segments"]), "duration_us": transcript["duration_us"],
            "transcription_mode": mode, "raw_sha256": transcript["raw_sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Source audio/video media file")
    parser.add_argument("--workspace", required=True, help="New isolated transcription directory")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--transcript", help="Existing Whisper-style JSON with word timestamps")
    source.add_argument("--command", help="External command using {input}, {output} and optional {workspace} placeholders")
    parser.add_argument("--timeout", type=float, default=1800, help="External command timeout in seconds")
    args = parser.parse_args()
    try:
        print(json.dumps(transcribe(args), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Transcription unavailable: {exc}\n")


if __name__ == "__main__":
    main()
