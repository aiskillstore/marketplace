"""Read-only SFX indexing and measured, hash-bound selection; never edits a draft.

Only waveform facts are automatic. Event relevance and the perceptual attack still
need the actual picture/word anchor and a listening decision.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave

sys.dont_write_bytecode = True
AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".aif", ".aiff"}
HERE = Path(__file__).resolve().parent
EVENT_CLASSES = {
    "impact": ["hit", "impact", "punch", "重击", "强打", "击打", "撞击", "敲鼓"],
    "motion": ["whoosh", "woosh", "swish", "swoosh", "划过", "嗖", "转场", "快切"],
    "recognition": ["recognition", "notice", "ding", "灵光", "心头闪过", "提示", "滴嘟"],
    "reveal": ["reveal", "stinger", "震惊", "惊讶", "悬疑", "重磅"],
    "dread": ["dread", "rumble", "anxiety", "低音", "焦虑", "紧张", "恐怖"],
    "decision": ["decision", "resolve", "坚定", "承诺"],
    "warmth": ["warmth", "care", "温暖", "关心"],
    "phone": ["phone", "notification", "电话", "手机", "铃声"],
    "door": ["door", "门", "开门", "关门"],
    "prop": ["paper", "cloth", "glass", "footstep", "纸", "衣", "杯", "玻璃", "脚步"],
    "riser": ["riser", "rise", "上升", "蓄势"],
    "tail": ["tail", "hook", "cliff", "悬念", "片尾"],
}


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def db(value):
    return round(20 * math.log10(max(value, 1e-8)), 4)


def find_ffmpeg(value=None):
    if value:
        result = Path(value).expanduser().resolve(strict=True)
        if not result.is_file():
            raise ValueError("ffmpeg is not a file")
        return str(result)
    configured = Path.home() / ".codex/state/tiktok-drama-fine-cut/backend.json"
    if configured.is_file():
        try:
            data = json.loads(configured.read_text(encoding="utf-8-sig"))
            candidate = data.get("ffmpeg") or data.get("paths", {}).get("ffmpeg")
            if isinstance(candidate, dict):
                candidate = candidate.get("path")
            if candidate and Path(candidate).is_file():
                return str(candidate)
        except (OSError, ValueError, TypeError):
            pass
    result = shutil.which("ffmpeg")
    if not result:
        raise ValueError("Pass --ffmpeg <installed executable>; no dependency will be installed")
    return result


def pcm_samples(path, max_seconds=None):
    """Return frames as tuples, preserving maximum-channel peaks and stereo polarity."""
    with wave.open(str(path), "rb") as source:
        width, channels, rate = source.getsampwidth(), source.getnchannels(), source.getframerate()
        if source.getcomptype() != "NONE" or width not in (1, 2, 3, 4) or channels < 1:
            raise ValueError("Requires ordinary integer PCM WAVE")
        full_frames = source.getnframes()
        count = min(full_frames, math.ceil(max_seconds * rate)) if max_seconds else full_frames
        raw = source.readframes(count)
        if len(raw) != count * width * channels:
            raise ValueError("Truncated PCM sample data")
        scale = float(2 ** (width * 8 - 1))
        if width == 1:
            values = [(x - 128) / 128 for x in raw]
        elif width == 2:
            values = [v[0] / scale for v in struct.iter_unpack("<h", raw)]
        elif width == 4:
            values = [v[0] / scale for v in struct.iter_unpack("<i", raw)]
        else:
            values = [int.from_bytes(raw[i:i + 3], "little", signed=True) / scale
                      for i in range(0, len(raw), 3)]
        return values, rate, channels, full_frames / rate


def decode(path, ffmpeg=None, max_seconds=30):
    try:
        return (*pcm_samples(path, max_seconds), "integer_pcm_wave")
    except (wave.Error, EOFError, ValueError):
        args = [find_ffmpeg(ffmpeg), "-nostdin", "-v", "error", "-i", str(path),
                "-map", "0:a:0", "-vn"]
        if max_seconds:
            args += ["-t", str(max_seconds)]
        # Stereo analysis avoids cancelling phase-opposed channels into mono.
        args += ["-ac", "2", "-ar", "24000", "-f", "f32le", "-"]
        process = subprocess.run(args, capture_output=True, timeout=120)
        if process.returncode:
            raise ValueError(process.stderr.decode("utf-8", "replace")[-1200:])
        samples = array("f")
        samples.frombytes(process.stdout)
        if sys.byteorder != "little":
            samples.byteswap()
        return list(samples), 24000, 2, None, "ffmpeg_float_analysis_stereo"


def spectral_profile(values, rate, channels):
    """Approximate band energy with bounded, per-channel Hann-windowed FFTs."""
    size = 2048
    frames = len(values) // channels
    starts = list(range(0, max(1, frames - size + 1), size // 2))
    if len(starts) > 64:
        starts = sorted({starts[round(i * (len(starts) - 1) / 63)] for i in range(64)})
    totals = [0.0] * 4
    edges = (20, 250, 2000, min(12000, rate / 2))
    for start in starts:
        for channel in range(channels):
            data = [complex(values[(start+i)*channels+channel] if start+i < frames else 0)
                    * (.5-.5*math.cos(2*math.pi*i/(size-1))) for i in range(size)]
            j = 0
            for i in range(1, size):
                bit = size >> 1
                while j & bit:
                    j ^= bit
                    bit >>= 1
                j ^= bit
                if i < j:
                    data[i], data[j] = data[j], data[i]
            length = 2
            while length <= size:
                angle = -2 * math.pi / length
                unit = complex(math.cos(angle), math.sin(angle))
                for a in range(0, size, length):
                    rotation = 1
                    for b in range(length // 2):
                        even, odd = data[a+b], data[a+b+length//2] * rotation
                        data[a+b], data[a+b+length//2] = even+odd, even-odd
                        rotation *= unit
                length *= 2
            for k in range(1, size // 2 + 1):
                hz = k * rate / size
                power = abs(data[k]) ** 2
                index = 0 if edges[0] <= hz < edges[1] else 1 if edges[1] <= hz < edges[2] else 2 if edges[2] <= hz <= edges[3] else 3
                totals[index] += power
    energy = sum(totals)
    return dict(method='2048_sample_Hann_FFT_max64_windows_per_channel',
                bands_hz=[[20, 250], [250, 2000], [2000, edges[3]], 'outside'],
                energy_fractions=[round(x / energy, 6) if energy else 0 for x in totals],
                sampled_windows_per_channel=len(starts),
                scope='sampled spectral energy, not perceived timbre/relevance/phone audibility')


def measure(path, ffmpeg=None, max_seconds=30, window_ms=5, tone_profile=False):
    path = Path(path).expanduser().resolve(strict=True)
    before_sha = sha(path)
    values, rate, channels, full_duration, decoder = decode(path, ffmpeg, max_seconds)
    if not values or any(not math.isfinite(v) for v in values):
        raise ValueError("No finite audio samples")
    frames = len(values) // channels
    if not frames:
        raise ValueError("Empty audio stream")
    size = max(1, round(rate * window_ms / 1000))
    power, peaks = [], []
    for start in range(0, frames, size):
        chunk = values[start * channels:min(frames, start + size) * channels]
        power.append(sum(v * v for v in chunk) / len(chunk))
        peaks.append(max(abs(v) for v in chunk))
    envelope = [math.sqrt(v) for v in power]
    maximum = max(abs(v) for v in values)
    rms = math.sqrt(sum(v * v for v in values) / len(values))
    peak_index = max(range(len(values)), key=lambda i: abs(values[i])) // channels
    gate = max(10 ** (-60 / 20), max(envelope) * 10 ** (-35 / 20))
    audible = [i for i, v in enumerate(envelope) if v >= gate]
    onset = audible[0] * size / rate if audible else None
    tail = min(frames / rate, (audible[-1] + 1) * size / rate) if audible else None
    # Rank positive envelope changes; leave several choices for a real listening decision.
    scores = [(max(0, envelope[i] - sum(envelope[max(0, i - 4):i]) / max(1, min(i, 4))), i)
              for i in range(len(envelope))]
    ranked = []
    for strength, index in sorted(scores, reverse=True):
        if strength <= 0 or any(abs(index - other) * size / rate < .08 for other in ranked):
            continue
        ranked.append(index)
        if len(ranked) >= 5:
            break
    attacks = [{"time_us": round(i * size * 1e6 / rate),
                "window_rms_dbfs": db(envelope[i]), "rise_amplitude": round(scores[i][0], 7)}
               for i in ranked]
    attack_us = attacks[0]["time_us"] if attacks else (round(onset * 1e6) if onset is not None else None)
    result = {"path": str(path), "sha256": before_sha, "channels": channels, "analysis_rate": rate,
            "decoder": decoder, "analyzed_duration_us": round(frames * 1e6 / rate),
            "full_duration_us": round(full_duration * 1e6) if full_duration is not None else None,
            "possibly_truncated": (full_duration is None and max_seconds and frames / rate >= max_seconds - .01)
                or bool(full_duration is not None and full_duration > frames / rate + .001),
            "peak_dbfs": db(maximum), "rms_dbfs": db(rms), "crest_db": round(db(maximum) - db(rms), 4),
            "peak_sample_us": round(peak_index * 1e6 / rate),
            "estimated_onset_us": round(onset * 1e6) if onset is not None else None,
            "estimated_main_attack_us": attack_us,
            "estimated_tail_end_us": round(tail * 1e6) if tail is not None else None,
            "estimated_tail_after_attack_us": max(0, round(tail * 1e6) - attack_us) if tail is not None and attack_us is not None else None,
            "attack_candidates": attacks, "window_ms": window_ms, "silence_threshold_dbfs": db(gate),
            "silent": not audible, "measurement_scope": "waveform_only_not_listened_or_semantically_verified"}
    if tone_profile:
        result['spectral_profile'] = spectral_profile(values, rate, channels)
    if sha(path) != before_sha:
        raise ValueError("Source changed during measurement")
    return result


def name_hints(path):
    name = Path(path).stem.casefold()
    return [kind for kind, words in EVENT_CLASSES.items() if any(w.casefold() in name for w in words)]


def index_roots(roots, output, ffmpeg=None, cache=None, limit=None):
    previous = {}
    if cache and Path(cache).is_file():
        existing = json.loads(Path(cache).read_text(encoding="utf-8"))
        previous = {row["sha256"]: row for row in existing.get("assets", []) if row.get("sha256")}
    paths, seen = [], set()
    for root_value in roots:
        root = Path(root_value).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"Not a folder: {root}")
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.casefold() in AUDIO_EXTENSIONS:
                key = str(path.resolve()).casefold()
                if key not in seen:
                    seen.add(key)
                    paths.append(path)
    if limit:
        paths = paths[:limit]
    assets, errors = [], []
    for path in paths:
        try:
            checksum = sha(path)
            prior = previous.get(checksum)
            row = dict(prior) if prior else measure(path, ffmpeg)
            row["path"] = str(path.resolve())
            row["name_hints"] = name_hints(path)
            row["name_hints_verified"] = False
            row.setdefault("rights", "user_source_requires_own_license_check")
            row["mix_role"] = "sfx_candidate"
            manifest_path = path.parent / "manifest.json"
            if manifest_path.is_file():
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                meta = next((x for x in manifest.get("assets", []) if x.get("file") == path.name and x.get("sha256") == checksum), None)
                if meta:
                    row["curation"] = {k: meta[k] for k in ("id", "event_classes", "tags", "use", "avoid", "license", "provenance", "synthetic") if k in meta}
                    row["rights"] = meta.get("license", row["rights"])
            assets.append(row)
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            errors.append({"path": str(path), "error": str(exc)})
    result = {"schema_version": 1, "kind": "sfx_catalogue", "roots": [str(Path(r).resolve()) for r in roots],
              "assets": assets, "errors": errors, "asset_count": len(assets),
              "scope": "SFX only; filename tags are search hints, never evidence of scene relevance or listening"}
    save(output, result)
    return {"catalogue": str(Path(output).resolve()), "asset_count": len(assets), "error_count": len(errors)}


def search_catalogue(catalogue, query, event_class=None, count=8):
    data = json.loads(Path(catalogue).read_text(encoding="utf-8"))
    query_tokens = query.casefold().split()
    results = []
    for row in data.get("assets", []):
        curated = row.get("curation", {})
        text = " ".join([Path(row["path"]).name, *row.get("name_hints", []), *curated.get("tags", []), *curated.get("event_classes", [])]).casefold()
        score = sum(2 for token in query_tokens if token in text)
        if event_class:
            score += 5 if event_class in curated.get("event_classes", []) else 1 if event_class in row.get("name_hints", []) else -10
        if (query_tokens or event_class) and score <= 0:
            continue
        results.append({"score": score, **row})
    return {"candidates": sorted(results, key=lambda row: (-row["score"], row["path"]))[:count],
            "review_required": "Listen to at least two alternatives against the same exact picture/word anchor; check avoid and rights"}


def verify_pack(root):
    root=Path(root).resolve(strict=True)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    seen=set()
    actual={path.relative_to(root).as_posix().casefold() for path in root.rglob('*')
            if path.is_file() and path.suffix.casefold()=='.wav'}
    for row in manifest.get('assets',[]):
        path=(root/row['file']).resolve(strict=True)
        relative=path.relative_to(root).as_posix().casefold() if path.is_relative_to(root) else None
        if relative is None or path.suffix.casefold()!='.wav' or relative in seen:
            raise ValueError('Pack WAV escapes its root, is repeated or has the wrong extension')
        seen.add(relative)
        if sha(path)!=row['sha256']:raise ValueError('Pack asset hash mismatch: '+path.name)
        if not row.get('license') or not row.get('provenance'):raise ValueError('Pack asset lacks provenance/license')
    if not seen:raise ValueError('Empty pack manifest')
    if seen!=actual:
        raise ValueError('Pack WAV membership differs from manifest; unregistered: '
                         +str(sorted(actual-seen))+'; missing: '+str(sorted(seen-actual)))
    return {'status':'verified','asset_count':len(seen),'root':str(root),
            'scope':'manifest WAV membership, hashes and recorded provenance; not listening or legal provenance authentication'}


def prepare(path, output, attack_us, target_us, purpose, fader_db=-3, pre_ms=30, tail_ms=350,
            ffmpeg=None, event_id=None, event_class=None, normalize_peak_dbfs=None,
            salient_attacks_us=None, selection_end_us=None, fade_out_ms=None, attack_body_ms=80):
    """An explicit attack location is required; do not convert an estimated onset to approval."""
    path, output = Path(path).resolve(strict=True), Path(output).resolve()
    if output.exists():
        raise ValueError("Use a new output directory")
    before = measure(path, ffmpeg, max_seconds=None)
    total = before["analyzed_duration_us"]
    if type(attack_us) is not int or not 0 <= attack_us < total:
        raise ValueError("Confirmed attack must be an integer source time inside the file")
    if not -5 <= fader_db <= -2:
        raise ValueError("SFX fader must be -5 to -2 dB; condition a quiet source first instead of confusing fader and dBFS")
    advanced = bool(salient_attacks_us) or selection_end_us is not None or fade_out_ms is not None
    if any(not math.isfinite(v) for v in (pre_ms, tail_ms, attack_body_ms)) or pre_ms < 0 or tail_ms <= 0 or attack_body_ms < 0:
        raise ValueError('Pre/hold must be nonnegative and tail positive finite milliseconds')
    attacks = sorted(set([attack_us, *(salient_attacks_us or [])]))
    if any(type(t) is not int or not 0 <= t < total for t in attacks):
        raise ValueError('Every salient attack must be an integer source time inside the file')
    start = max(0, min(attacks) - round(pre_ms * 1000))
    end = min(total, max(attacks) + round(tail_ms * 1000)) if selection_end_us is None else selection_end_us
    if type(end) is not int or not start < end <= total:
        raise ValueError('Selection end must be inside the source after selection start')
    hold = round(attack_body_ms * 1000) if advanced else 0
    if end < max(attacks) + hold or end <= max(attacks):
        raise ValueError('Selection truncates the last salient attack or its declared body')
    requested_fade = None if fade_out_ms is None else round(fade_out_ms * 1000) if math.isfinite(fade_out_ms) and fade_out_ms >= 0 else -1
    if requested_fade is not None and (requested_fade < 0 or end-requested_fade < max(attacks)+hold):
        raise ValueError('Fade would attenuate a salient attack/body; shorten fade or extend selection')
    if end <= attack_us or target_us < attack_us - start:
        raise ValueError("Selection or target would truncate the attack/extend before the timeline")
    conditioning_gain = 0
    if normalize_peak_dbfs is not None:
        if not -12 <= normalize_peak_dbfs <= -1:
            raise ValueError("normalize-peak-dbfs must be -12 to -1 dBFS")
        values, rate, channels, _, _ = decode(path, ffmpeg, max_seconds=None)
        selected = values[round(start * rate / 1e6) * channels:round(end * rate / 1e6) * channels]
        selected_peak = max((abs(v) for v in selected), default=0)
        if selected_peak <= 0:
            raise ValueError("Cannot normalize a silent selection")
        conditioning_gain = normalize_peak_dbfs - db(selected_peak)
        if conditioning_gain > 18:
            raise ValueError("Selection would need more than 18 dB source conditioning; choose a cleaner/louder alternative")
    output.mkdir(parents=True)
    destination = output / "selected.wav"
    cmd = [find_ffmpeg(ffmpeg), "-nostdin", "-v", "error", "-i", str(path), "-ss", f"{start / 1e6:.6f}",
           "-t", f"{(end - start) / 1e6:.6f}", "-map", "0:a:0", "-vn"]
    if normalize_peak_dbfs is not None:
        cmd += ["-af", f"volume={conditioning_gain:.6f}dB"]
    cmd += ["-acodec", "pcm_s16le", str(destination)]
    process = subprocess.run(cmd, capture_output=True, timeout=120)
    if process.returncode:
        raise ValueError(process.stderr.decode("utf-8", "replace")[-1200:])
    evidence = measure(destination, ffmpeg, max_seconds=None)
    if evidence["silent"]:
        raise ValueError("Selected source is silent")
    selected_duration = evidence["analyzed_duration_us"]
    if max(attacks) - start >= selected_duration:
        raise ValueError("Confirmed attack was not included in decoded samples")
    row = {"path": str(destination), "sha256": evidence["sha256"], "mix_role": "sfx", "fader_db": fader_db,
           "source_start_us": 0, "source_duration_us": selected_duration, "attack_offset_us": attack_us - start,
           "target_us": target_us, "source_peak_dbfs": evidence["peak_dbfs"],
           "target_peak_dbfs": round(evidence["peak_dbfs"] + fader_db, 4),
           "fade_in_us": 0, "fade_out_us": min(60000, max(0, selected_duration - (attack_us - start)) // 3),
           "track_name": "情绪音效" if event_class in ("reveal", "recognition", "dread", "decision", "warmth", "tail") else "动作音效",
           "purpose": purpose}
    if advanced:
        available = selected_duration - (max(attacks)-start) - hold
        if available < -math.ceil(1e6 / evidence['analysis_rate']):
            raise ValueError('Decoded selection truncates the last declared attack body')
        row['fade_out_us'] = min(requested_fade if requested_fade is not None else row['fade_out_us'], max(0, available))
    if event_id:
        row["event_id"] = event_id
    if event_class:
        row["event_class"] = event_class
    row["selection_evidence"] = str(output / "selection.json")
    result = {"schema_version": 1, "plan_sfx_row": row, "source": {"path": str(path), "sha256": before["sha256"],
              "selected_start_us": start, "selected_end_us": end, "confirmed_attack_us": attack_us,
              "conditioning_gain_db": round(conditioning_gain, 4), "normalize_peak_dbfs": normalize_peak_dbfs},
              "event_id": event_id, "event_class": event_class, "measurements": evidence,
              "listening_status": "caller_must_record_actual_listening_no_auto_pass"}
    if advanced:
        result['source'].update(salient_attacks_us=attacks, attack_body_ms=attack_body_ms,
                                salient_attack_offsets_us=[t-start for t in attacks],
                                selection_end_us=end, fade_out_us=row['fade_out_us'])
    if sha(path) != before['sha256']:
        raise ValueError('Source changed during selection')
    save(output / "selection.json", result)
    return {"selection": str(output / "selection.json"), "plan_sfx_row": row}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("index", help="Index source folders without copying or editing them")
    p.add_argument("--root", action="append", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--cache")
    p.add_argument("--limit", type=int)
    p.add_argument("--ffmpeg")
    p = sub.add_parser("search", help="Return semantic/name candidates, never an automatic event assignment")
    p.add_argument("--catalogue", required=True)
    p.add_argument("--query", default="")
    p.add_argument("--event-class", choices=sorted(EVENT_CLASSES))
    p.add_argument("--count", type=int, default=8)
    p = sub.add_parser("verify-pack", help="Verify bundled manifest paths, hashes and provenance fields")
    p.add_argument("--root", required=True)
    p = sub.add_parser("measure", help="Inspect onset/attack candidates/RMS/peak in an actual source")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.add_argument("--max-seconds", type=float, default=30)
    p.add_argument("--tone-profile", action="store_true", help="Add sampled per-channel band energy; no semantic classification")
    p.add_argument("--ffmpeg")
    p = sub.add_parser("prepare", help="Decode a confirmed source attack into a separate PCM selection")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--confirmed-attack-us", type=int, required=True)
    p.add_argument("--salient-attack-us", type=int, action="append", help="Additional source attack to preserve; repeat for double/multiple hits")
    p.add_argument("--selection-end-us", type=int, help="Explicit source end; rejects truncation of a declared attack/body")
    p.add_argument("--fade-out-ms", type=float, help="Plan fade after the last attack body; WAV is not faded twice")
    p.add_argument("--attack-body-ms", type=float, default=80, help="Minimum unattenuated body after last attack in advanced selections")
    p.add_argument("--target-us", type=int, required=True)
    p.add_argument("--purpose", required=True)
    p.add_argument("--fader-db", type=float, default=-3)
    p.add_argument("--pre-ms", type=float, default=30)
    p.add_argument("--tail-ms", type=float, default=350)
    p.add_argument("--event-id")
    p.add_argument("--event-class", choices=sorted(EVENT_CLASSES))
    p.add_argument("--normalize-peak-dbfs", type=float,
                   help="Explicitly condition this selection in its separate WAV; -12 to -1 dBFS, max +18 dB gain")
    p.add_argument("--ffmpeg")
    args = parser.parse_args()
    try:
        if args.command == "index":
            result = index_roots(args.root, args.output, args.ffmpeg, args.cache, args.limit)
        elif args.command == "verify-pack":
            result = verify_pack(args.root)
        elif args.command == "search":
            if args.count < 1:
                raise ValueError("count must be positive")
            result = search_catalogue(args.catalogue, args.query, args.event_class, args.count)
        elif args.command == "measure":
            if args.max_seconds <= 0:
                raise ValueError("max-seconds must be positive")
            result = measure(args.input, args.ffmpeg, args.max_seconds, tone_profile=args.tone_profile)
            if args.output:
                save(args.output, result)
        else:
            if not math.isfinite(args.pre_ms) or not math.isfinite(args.tail_ms) or args.pre_ms < 0 or args.tail_ms <= 0:
                raise ValueError("pre-ms must be nonnegative and tail-ms positive and finite")
            result = prepare(args.input, args.output, args.confirmed_attack_us, args.target_us,
                             args.purpose, args.fader_db, args.pre_ms, args.tail_ms, args.ffmpeg,
                             args.event_id, args.event_class, args.normalize_peak_dbfs,
                             args.salient_attack_us, args.selection_end_us, args.fade_out_ms, args.attack_body_ms)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"SFX tool unavailable: {exc}\n")


if __name__ == "__main__":
    main()
