"""Build reviewable cut candidates and explicitly approved timeline plans."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import timeline_ops as ops


def load(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2))


def overlaps(a, b, lo, hi):
    return max(a, lo) < min(b, hi)


def checked_context(input_path, analysis_path):
    source = Path(input_path).resolve(strict=True)
    analysis_source = Path(analysis_path).resolve(strict=True)
    doc = load(source)
    analysis = load(analysis_source)
    input_hash = sha(source)
    ops.validate_document(doc)
    if analysis.get("input_sha256") != input_hash:
        raise ValueError("Analysis belongs to a different input JSON")
    if analysis.get("timeline_id") != doc.get("id") or analysis.get("duration_us") != doc.get("duration"):
        raise ValueError("Analysis timeline identity or duration differs from the input")
    return source, analysis_source, doc, analysis, input_hash


def primary_track(doc):
    candidates = []
    for track in doc["tracks"]:
        if track.get("type") != "video":
            continue
        cursor = 0
        for segment in sorted(track["segments"], key=lambda item: ops.bounds(item)[0]):
            a, b = ops.bounds(segment)
            if a != cursor:
                break
            cursor = b
        if cursor == doc["duration"]:
            candidates.append(track["id"])
    if not candidates:
        raise ValueError("No video track continuously covers the complete timeline; choose and verify a primary track manually")
    return candidates[0]


def music_segments(doc):
    materials = ops.lookup(doc)
    result = []
    for track in doc["tracks"]:
        if track.get("type") != "audio":
            continue
        for segment in track["segments"]:
            material = materials[segment["material_id"]]
            if (material.get("type") in ("music", "extract_music")
                    and material.get("sound_separate_type") not in ("human", "background")):
                result.append(segment["id"])
    return result


def path_key(raw):
    if not isinstance(raw, str):
        return None
    path = Path(raw)
    return str(path.resolve()).casefold() if path.is_absolute() else None


def transcript_intervals(doc, transcript_path):
    if not transcript_path:
        return [], None
    source = Path(transcript_path).resolve(strict=True)
    transcript = load(source)
    if transcript.get("schema_version") != 1 or transcript.get("word_timestamps") is not True:
        raise ValueError("Transcript must be schema_version=1 output with word_timestamps=true")
    expected_hash = transcript.get("source_sha256")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise ValueError("Transcript lacks a source media SHA-256")
    materials = ops.lookup(doc)
    active = {segment["material_id"] for track in doc["tracks"] if track.get("type") in ("video", "audio")
              for segment in track["segments"]}
    source_key = path_key(transcript.get("source_path"))
    exact = [identifier for identifier in active if source_key and path_key(materials[identifier].get("path")) == source_key]
    matched = []
    for identifier in exact:
        path = Path(materials[identifier]["path"])
        if path.is_file() and sha(path) == expected_hash:
            matched.append(identifier)
    if not matched and not exact:
        for identifier in active:
            raw = materials[identifier].get("path")
            path = Path(raw) if isinstance(raw, str) else None
            if path and path.is_absolute() and path.is_file() and sha(path) == expected_hash:
                matched.append(identifier)
    if not matched:
        raise ValueError("No active timeline material matches the transcript source path/hash")
    segments = [segment for track in doc["tracks"] if track.get("type") in ("video", "audio")
                for segment in track["segments"] if segment["material_id"] in matched]
    intervals = []
    mapped_words, partial_words, unsupported_words, unused_words = set(), set(), set(), set()
    unsupported_segments = set()
    for word in transcript.get("words", []):
        start, end = word.get("start_us"), word.get("end_us")
        if type(start) is not int or type(end) is not int or not 0 <= start < end:
            raise ValueError(f"Invalid transcript word range: {word.get('id')}")
        occurrences = []
        had_partial = False
        had_unsupported = False
        had_overlap = False
        for segment in segments:
            a, b = ops.bounds(segment)
            source_range = segment.get("source_timerange") or {}
            ins = source_range.get("start", 0)
            duration = source_range.get("duration", b-a)
            if not overlaps(start, end, ins, ins+duration):
                continue
            had_overlap = True
            refs = [materials[ref] for ref in segment.get("extra_material_refs", []) if ref in materials]
            rate = duration/(b-a)
            if (rate <= 0 or segment.get("reverse") or segment.get("is_reverse")
                    or any(ref.get("curve_speed") for ref in refs if ref.get("type") == "speed")):
                had_unsupported = True
                unsupported_segments.add(segment["id"])
                continue
            if not (ins <= start and end <= ins+duration):
                had_partial = True
                continue
            mapped_a = max(a, min(b, a+round((start-ins)/rate)))
            mapped_b = max(a, min(b, a+round((end-ins)/rate)))
            if mapped_a < mapped_b:
                occurrences.append({"start_us": mapped_a, "end_us": mapped_b,
                                    "source_word_id": word.get("id"), "source_segment_id": segment["id"]})
        if had_partial:
            partial_words.add(word.get("id"))
        if occurrences:
            intervals.extend(occurrences)
            mapped_words.add(word.get("id"))
        elif had_unsupported:
            unsupported_words.add(word.get("id"))
        elif had_partial:
            pass
        elif not had_overlap:
            unused_words.add(word.get("id"))
    info = {"path": str(source), "sha256": sha(source), "source_sha256": expected_hash,
            "matched_material_ids": sorted(matched), "mapped_word_count": len(mapped_words),
            "mapped_occurrence_count": len(intervals), "partial_word_ids": sorted(partial_words),
            "unsupported_word_ids": sorted(unsupported_words), "unused_word_ids": sorted(unused_words),
            "unsupported_segment_ids": sorted(unsupported_segments),
            "mapping_note": "Words are mapped to every fully matching source occurrence; partial/unsupported words are not clipped or guessed"}
    return intervals, info


def speech_declaration(analysis, asr_intervals=()):
    rows = [(row["start_us"], row["end_us"]) for row in analysis.get("waveform", {}).get("activity_intervals", [])]
    rows.extend((row["start_us"], row["end_us"]) for row in asr_intervals)
    merged = []
    for start, end in sorted(rows):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return {"coverage_us": [0, analysis["duration_us"]],
            "intervals": [dict(id=f"voice-{index:04d}", start_us=start, end_us=end)
                          for index, (start, end) in enumerate(merged, 1)],
            "remove_ids": []}


def base_plan(doc, analysis, input_hash, asr_intervals=()):
    return {"schema_version": 1, "timeline_id": doc["id"], "input_sha256": input_hash,
            "primary_video_track_id": primary_track(doc), "boundary_tolerance_us": 4,
            "cuts": [], "speech": speech_declaration(analysis, asr_intervals),
            "remove_caption_ids": [], "shorten_caption_ids": [], "drop_transition_ids": [],
            "audio_roles": {}, "audio_edge_fades_us": {},
            "music": {"segment_ids": music_segments(doc), "energy_reasons": {}},
            "beat_events": [], "bridges": [], "flips": [], "sfx": [], "merge_contiguous": True}


def build_candidates(analysis):
    rows = []
    for kind, key in (("energy_dip", "energy_dip_candidates"), ("caption_gap", "gap_candidates")):
        for evidence in analysis.get(key, []):
            start, end = evidence.get("start_us"), evidence.get("end_us")
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= analysis["duration_us"]:
                raise ValueError(f"Invalid {kind} candidate range: {start}–{end}")
            risks = []
            if evidence.get("overlaps_unsupported_voice"):
                risks.append("overlaps_unsupported_voice")
            for unsupported in [*analysis.get("unsupported_voice_segments", []),
                                *analysis.get("unmeasured_audio_segments", [])]:
                if overlaps(start, end, unsupported["start_us"], unsupported["end_us"]):
                    risks.append(f"unverified_voice:{unsupported.get('id', 'unknown')}")
            for caption in analysis.get("captions", []):
                if start <= caption["start_us"] and end >= caption["end_us"]:
                    risks.append(f"covers_complete_caption:{caption['segment_id']}")
            rows.append({"start_us": start, "end_us": end,
                         "duration_us": end-start, "sources": [dict(kind=kind, evidence=evidence)],
                         "risk_flags": sorted(set(risks))})
    grouped = {}
    for row in rows:
        key = row["start_us"], row["end_us"]
        if key in grouped:
            grouped[key]["sources"].extend(row["sources"])
            grouped[key]["risk_flags"] = sorted(set(grouped[key]["risk_flags"] + row["risk_flags"]))
        else:
            grouped[key] = row
    result = []
    for index, row in enumerate(sorted(grouped.values(), key=lambda item: (item["start_us"], item["end_us"])), 1):
        result.append(dict(id=f"cut-{index:04d}", status="pending", **row,
                           review="Confirm picture action, actual syllables, caption readability and story causality before approval"))
    return result


def propose(args):
    source, analysis_source, doc, analysis, input_hash = checked_context(args.input, args.analysis)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError("Candidate output directory must be new")
    asr_intervals, transcript_info = transcript_intervals(doc, getattr(args, "transcript", None))
    plan = base_plan(doc, analysis, input_hash, asr_intervals)
    ops.prepare_plan(doc, plan, input_hash)
    candidates = build_candidates(analysis)
    review = {"schema_version": 1, "timeline_id": doc["id"], "input_sha256": input_hash,
              "analysis": str(analysis_source), "analysis_sha256": sha(analysis_source),
              "transcript": transcript_info, "safe_plan": "plan.json", "candidates": candidates,
              "limitations": [
                  "Candidates are low-energy and caption-gap locators, not automatic editorial decisions or ASR",
                  "Embedded audio can contain music/effects and quiet speech can be missed",
                  "ASR and energy intervals are unioned for protection; ASR accuracy and unmapped words still require review",
                  "The safe plan has zero cuts; only explicitly approved candidates become cuts",
                  "Music segments are inferred only from music/extract_music material types and still require review",
                  "Approving requires actual picture, source-audio, caption and causality review"]}
    output.mkdir(parents=True)
    save(output / "plan.json", plan)
    save(output / "review.json", review)
    return {"status": "candidate_review_required", "review": str(output / "review.json"),
            "safe_plan": str(output / "plan.json"), "candidate_count": len(candidates),
            "candidates_with_risks": sum(bool(row["risk_flags"]) for row in candidates),
            "asr_mapped_occurrences": transcript_info["mapped_occurrence_count"] if transcript_info else 0,
            "cuts_in_safe_plan": 0, "input_sha256": input_hash}


def approve(args):
    if not args.confirm_reviewed:
        raise ValueError("Use --confirm-reviewed only after reviewing picture, source audio, captions and story causality")
    source, analysis_source, doc, analysis, input_hash = checked_context(args.input, args.analysis)
    review = load(Path(args.review).resolve(strict=True))
    if (review.get("timeline_id") != doc["id"] or review.get("input_sha256") != input_hash
            or review.get("analysis_sha256") != sha(analysis_source)):
        raise ValueError("Review file is stale or belongs to different analysis")
    transcript_path = getattr(args, "transcript", None)
    reviewed_transcript = review.get("transcript")
    if bool(reviewed_transcript) != bool(transcript_path):
        raise ValueError("Approval must use the same transcript presence as the reviewed proposal")
    if reviewed_transcript and sha(Path(transcript_path).resolve(strict=True)) != reviewed_transcript.get("sha256"):
        raise ValueError("Transcript changed after candidate review")
    asr_intervals, transcript_info = transcript_intervals(doc, transcript_path)
    candidates = {row["id"]: row for row in review.get("candidates", [])}
    accepted = set(args.accept)
    unknown = accepted-candidates.keys()
    if unknown:
        raise ValueError(f"Unknown candidate IDs: {sorted(unknown)}")
    selected = sorted((candidates[identifier] for identifier in accepted), key=lambda row: row["start_us"])
    cuts = []
    for row in selected:
        a, b = row["start_us"], row["end_us"]
        if cuts and cuts[-1][1] > a:
            raise ValueError("Approved candidates overlap; approve a disjoint set")
        if any(flag.startswith("covers_complete_caption:") for flag in row.get("risk_flags", [])):
            raise ValueError(f"Candidate {row['id']} fully covers a caption; reauthor caption removal explicitly")
        cuts.append((a, b))
    plan = base_plan(doc, analysis, input_hash, asr_intervals)
    plan["cuts"] = [dict(start_us=a, end_us=b) for a, b in cuts]
    shortened = []
    for caption in analysis.get("captions", []):
        a, b = caption["start_us"], caption["end_us"]
        retained = sum(y-x for x, y in ops.pieces(a, b, cuts))
        if retained == 0 and any(overlaps(a, b, lo, hi) for lo, hi in cuts):
            raise ValueError(f"Approved cuts fully remove caption {caption['segment_id']}; explicit reauthoring required")
        if 0 < retained < b-a:
            shortened.append(caption["segment_id"])
    plan["shorten_caption_ids"] = sorted(set(shortened))
    ops.prepare_plan(doc, plan, input_hash)
    output = Path(args.output).resolve()
    save(output, plan)
    return {"status": "approved_plan_ready", "plan": str(output),
            "accepted_candidate_ids": sorted(accepted), "cut_count": len(cuts),
            "shortened_caption_ids": plan["shorten_caption_ids"],
            "asr_mapped_occurrences": transcript_info["mapped_occurrence_count"] if transcript_info else 0,
            "verification": "Plan passed structural, declared-speech and caption validation; preview and editorial review remain required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("propose", "approve"):
        entry = sub.add_parser(command)
        entry.add_argument("--input", required=True, help="Isolated baseline timeline JSON")
        entry.add_argument("--analysis", required=True, help="Hash-bound analysis.json from analyze")
        entry.add_argument("--transcript", help="Optional transcript.json with source-bound word timestamps")
        if command == "propose":
            entry.add_argument("--output", required=True, help="New directory for review.json and zero-cut plan.json")
        else:
            entry.add_argument("--review", required=True, help="review.json produced by propose")
            entry.add_argument("--accept", nargs="+", required=True, help="Candidate IDs explicitly approved for cutting")
            entry.add_argument("--confirm-reviewed", action="store_true",
                               help="Confirm actual picture, source-audio, caption and causality review")
            entry.add_argument("--output", required=True, help="New approved plan JSON; never overwritten")
    args = parser.parse_args()
    try:
        result = propose(args) if args.command == "propose" else approve(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, ops.EditError) as exc:
        parser.exit(1, f"{args.command}: {exc}\n")


if __name__ == "__main__":
    main()
