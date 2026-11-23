"""Prepare and validate evidence for Codex-led editorial review."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def evidence_ref(path, digest=None):
    path = Path(path).resolve(strict=True)
    return {"path": str(path), "sha256": digest or sha(path)}


def _collect_dependencies(seam, ranges, auditions, extra):
    dependencies = {str(Path(path).resolve()): sha(path) for path in extra}
    for report in [seam, *ranges]:
        for path, digest in report.get("dependencies", {}).items():
            dependencies[str(Path(path).resolve())] = digest
    for audition in auditions:
        for path, digest in audition.get("artifacts", {}).items():
            dependencies[str(Path(path).resolve())] = digest
        for path, digest in audition.get("bindings", {}).items():
            dependencies[str(Path(path).resolve())] = digest
    for path in extra:
        dependencies[str(Path(path).resolve())] = sha(path)
    return dependencies


def build(input_path, report_path, qc_path, seam_path, preview_path, ffmpeg, ffprobe,
          range_paths=None, audition_paths=None, output=None, evidence_dir=None):
    from seam_review import extract_frames, probe, sheet

    input_path, report_path, qc_path, seam_path, preview_path = [
        Path(p).resolve(strict=True) for p in (input_path, report_path, qc_path, seam_path, preview_path)]
    report, qc, seam = load(report_path), load(qc_path), load(seam_path)
    if report.get("output_sha256") != sha(input_path):
        raise ValueError("Edit report is stale")
    if qc.get("input_sha256") != sha(input_path):
        raise ValueError("QC is stale")
    if seam.get("input_sha256") != sha(input_path) or seam.get("edit_report_sha256") != sha(report_path):
        raise ValueError("Seam scan is stale")
    ranges = [load(p) for p in (range_paths or [])]
    auditions = [load(p) for p in (audition_paths or [])]
    evidence_dir = Path(evidence_dir or Path(output).parent / "automated-evidence").resolve()
    evidence_dir.mkdir(parents=True)
    preview = probe(str(ffprobe), preview_path)
    fps = Fraction(preview["avg_frame_rate"])
    count = max(1, int(preview["frame_count"]))
    step = max(1, math.ceil(count / 48))
    indices = list(range(0, count, step))
    if indices[-1] != count - 1:
        indices.append(count - 1)
    pixels = extract_frames(str(ffmpeg), preview_path, indices)
    keyframe_sheets = []
    for page, start in enumerate(range(0, len(indices), 12), 1):
        page_indices = indices[start:start + 12]
        keyframe_sheet = evidence_dir / f"overview-keyframes-{page:04d}.png"
        sheet(str(ffmpeg), [pixels[i] for i in page_indices], keyframe_sheet, offsets=[0] * len(page_indices))
        keyframe_sheets.append({"path": str(keyframe_sheet), "sha256": sha(keyframe_sheet),
                                "frames": page_indices})
    keyframe_index = evidence_dir / "overview-keyframes.json"
    keyframe_rows = [{"frame": i, "time_us": round(Fraction(i * 1_000_000, 1) / fps)} for i in indices]
    save(keyframe_index, {"preview": str(preview_path), "preview_sha256": sha(preview_path), "fps": str(fps), "sampled_frames": keyframe_rows,
                          "sheets": keyframe_sheets,
                          "scope": "Evenly sampled overview frames; not exhaustive motion review"})
    dependencies = _collect_dependencies(seam, ranges, auditions,
        [input_path, report_path, qc_path, seam_path, preview_path, keyframe_index, *(audition_paths or []), *(range_paths or [])])
    dependencies.update({row["path"]: row["sha256"] for row in keyframe_sheets})
    effects = [x for x in report.get("sfx", []) if x.get("mix_role") == "sfx"]
    for event in effects:
        path = event.get("selection_evidence")
        if path and Path(path).is_file():
            dependencies[str(Path(path).resolve())] = sha(path)
    audition_events = {}
    for path, audition in zip(audition_paths or [], auditions):
        for event in audition.get("events", []):
            audition_events.setdefault(event.get("segment_id"), []).append(
                {"manifest": str(Path(path).resolve()), "manifest_sha256": sha(path), "event": event})
    seam_rows = []
    for row in seam.get("seams", []):
        refs = [evidence_ref(Path(seam_path).parent / row["source_sheet"], seam["dependencies"][str(Path(seam_path).parent / row["source_sheet"])])]
        if row.get("rendered_sheet"):
            refs.append(evidence_ref(Path(seam_path).parent / row["rendered_sheet"],
                                     seam["dependencies"][str(Path(seam_path).parent / row["rendered_sheet"])]))
        seam_rows.append({"id": row["id"], "time_us": row["time_us"], "risk_locators": row.get("risk_locators", []),
                          "decision": "pending", "observations": "", "confidence": None, "evidence_files": refs})
    range_rows = []
    for path, row in zip(range_paths or [], ranges):
        refs = [evidence_ref(k, v) for k, v in row.get("dependencies", {}).items()
                if Path(k).suffix.lower() == ".png"]
        range_rows.append({"range_id": row["range_id"], "scan": str(Path(path).resolve()),
            "scan_sha256": sha(path), "operation": row["operation"], "start_us": row["start_us"], "end_us": row["end_us"],
            "decision": "pending", "entry_observation": "", "interior_observation": "", "exit_observation": "",
            "confidence": None, "evidence_files": refs})
    sfx_rows = []
    for event in effects:
        auditions_for_event = audition_events.get(event["segment_id"], [])
        audio_refs = []
        for audition in auditions_for_event:
            for mode in ("full", "without", "solo"):
                files = audition["event"].get("files", {}).get(mode, {})
                for key in ("audio", "video"):
                    value = files.get(key)
                    if value and str(Path(value).resolve()) in dependencies:
                        audio_refs.append(evidence_ref(value, dependencies[str(Path(value).resolve())]))
        beat = next((b for b in report.get("beat_events", []) if b.get("id") == event.get("event_id")), {})
        sfx_rows.append({"segment_id": event["segment_id"], "event_id": event.get("event_id"),
            "event_class": event.get("event_class"), "purpose": event.get("purpose"),
            "target_us": event.get("target_us"), "input_target_us": event.get("input_target_us"),
            "beat_context": beat, "selection_evidence": event.get("selection_evidence"),
            "selection_evidence_sha256": event.get("selection_evidence_sha256"),
            "candidates_compared": [{"selection_evidence": event.get("selection_evidence")}, {"selection_evidence": ""}],
            "audition_manifests": [x["manifest"] for x in auditions_for_event], "audio_evidence": audio_refs,
            "decision": "pending", "anchor": "", "scene_fit": "", "sound_observation": "",
            "dialogue_impact": "", "analysis_method": "", "reason": "", "confidence": None})
    template = {"schema_version": 1, "kind": "automated_review", "review_mode": "autonomous",
        "reviewer": {"type": "agent", "name": "", "methods": [], "limitations": []},
        "bindings": {"input_sha256": sha(input_path), "edit_report_sha256": sha(report_path),
                     "qc_sha256": sha(qc_path), "seam_scan_sha256": sha(seam_path),
                     "preview_sha256": sha(preview_path)},
        "dependencies": dependencies,
        "overview": {"keyframe_sheets": [evidence_ref(x["path"], x["sha256"]) for x in keyframe_sheets],
                     "keyframe_index": evidence_ref(keyframe_index),
                     "decision": "pending", "observations": "", "confidence": None},
        "seam_scan": str(seam_path), "seams": seam_rows, "picture_ranges": range_rows, "sfx": sfx_rows,
        "qc": {"technical_status": qc.get("technical_status"), "issues": qc.get("issues", []),
               "decision": "pending", "observations": ""},
        "human_listening_claimed": False, "normal_speed_review_claimed": False,
        "scope_limitations": ["Frame and waveform evidence does not prove subjective naturalness or scene relevance.",
                              "No human listening or normal-speed viewing is claimed in autonomous mode."]}
    save(output, template)
    return {"status": "evidence_ready", "template": str(Path(output).resolve()),
            "keyframe_sheets": [x["path"] for x in keyframe_sheets], "keyframe_index": str(keyframe_index), "seam_count": len(seam_rows),
            "picture_range_count": len(range_rows), "sfx_count": len(sfx_rows),
            "requires_agent_analysis": True}


def _validate_refs(refs, dependencies, label, issues, minimum=1):
    if not isinstance(refs, list) or len(refs) < minimum:
        issues.append(label + ": evidence reference missing")
        return
    for ref in refs:
        if not isinstance(ref, dict) or not ref.get("path") or not ref.get("sha256"):
            issues.append(label + ": malformed evidence reference")
            continue
        path = str(Path(ref["path"]).resolve())
        if dependencies.get(path) != ref["sha256"]:
            issues.append(label + ": evidence is not bound to this run: " + path)
        elif not Path(path).is_file() or sha(path) != ref["sha256"]:
            issues.append(label + ": evidence changed: " + path)


def validate(review_path, input_path, report_path, qc_path, seam_path, range_paths=None, audition_paths=None):
    from audio_audition import verify_manifest
    from review_check import candidate_identity

    review = load(review_path); report = load(report_path); qc = load(qc_path); seam = load(seam_path)
    issues = []
    if review.get("schema_version") != 1 or review.get("kind") != "automated_review" or review.get("review_mode") != "autonomous":
        raise ValueError("Unsupported autonomous review record")
    if review.get("reviewer", {}).get("type") != "agent" or not review.get("reviewer", {}).get("name"):
        issues.append("reviewer identity is missing")
    if not review.get("reviewer", {}).get("methods") or not review.get("reviewer", {}).get("limitations"):
        issues.append("review methods and limitations must be recorded")
    if review.get("human_listening_claimed") is not False or review.get("normal_speed_review_claimed") is not False:
        issues.append("autonomous review cannot claim human listening or normal-speed viewing")
    expected_bindings = {"input_sha256": sha(input_path), "edit_report_sha256": sha(report_path),
                         "qc_sha256": sha(qc_path), "seam_scan_sha256": sha(seam_path)}
    for key, digest in expected_bindings.items():
        if review.get("bindings", {}).get(key) != digest:
            raise ValueError("Review belongs to another run: " + key)
    deps = review.get("dependencies", {})
    index_ref = review.get("overview", {}).get("keyframe_index", {})
    if not isinstance(index_ref, dict) or not index_ref.get("path") or not Path(index_ref["path"]).is_file():
        raise ValueError("Keyframe index is missing")
    index = load(index_ref["path"])
    expected_deps = {str(Path(p).resolve()): sha(p) for p in (input_path, report_path, qc_path, seam_path,
        index_ref["path"], index.get("preview", "")) if p and Path(p).is_file()}
    expected_deps.update({str(Path(k).resolve()): v for k, v in seam.get("dependencies", {}).items()})
    expected_ranges = {Path(p).resolve(): load(p) for p in (range_paths or [])}
    for path, row in expected_ranges.items():
        expected_deps[str(path)] = sha(path)
        expected_deps.update({str(Path(k).resolve()): v for k, v in row.get("dependencies", {}).items()})
    expected_auditions = [load(p) for p in (audition_paths or [])]
    for path, row in zip(audition_paths or [], expected_auditions):
        expected_deps[str(Path(path).resolve())] = sha(path)
        expected_deps.update({str(Path(k).resolve()): v for k, v in row.get("artifacts", {}).items()})
        expected_deps.update({str(Path(k).resolve()): v for k, v in row.get("bindings", {}).items()})
    for row in index.get("sheets", []):
        expected_deps[str(Path(row["path"]).resolve())] = row["sha256"]
    for event in report.get("sfx", []):
        selection = event.get("selection_evidence")
        if selection and Path(selection).is_file():
            expected_deps[str(Path(selection).resolve())] = sha(selection)
    if deps != expected_deps:
        raise ValueError("Review evidence dependency set differs from the generated evidence")
    for raw, digest in deps.items():
        path = Path(raw)
        if not path.is_file() or sha(path) != digest:
            raise ValueError("Automated review evidence changed or is missing: " + raw)
    overview = review.get("overview", {})
    if overview.get("decision") != "pass" or not str(overview.get("observations", "")).strip():
        issues.append("episode keyframe overview is pending")
    _confidence(overview.get("confidence"), "overview", issues)
    _validate_refs([*overview.get("keyframe_sheets", []), overview.get("keyframe_index")], deps, "overview", issues, minimum=2)
    keyframe_index = overview.get("keyframe_index", {})
    if isinstance(keyframe_index, dict) and keyframe_index.get("path") and Path(keyframe_index["path"]).is_file():
        index = load(keyframe_index["path"])
        if review.get("bindings", {}).get("preview_sha256") != index.get("preview_sha256"):
            raise ValueError("Review preview binding differs from sampled keyframes")
        if {x.get("path") for x in overview.get("keyframe_sheets", [])} != {x.get("path") for x in index.get("sheets", [])}:
            raise ValueError("Review keyframe pages differ from the bound index")
    if qc.get("technical_status") != "passed":
        issues.append("technical QC did not pass")
    if review.get("qc", {}).get("decision") != "pass" or not str(review.get("qc", {}).get("observations", "")).strip():
        issues.append("QC evidence has not been assessed")
    if review.get("seam_scan") != str(Path(seam_path).resolve()):
        raise ValueError("Seam scan path differs")
    expected_seams = {x["id"]: x for x in seam.get("seams", [])}
    supplied_seams = review.get("seams", [])
    if len(supplied_seams) != len(expected_seams) or {x.get("id") for x in supplied_seams} != set(expected_seams):
        raise ValueError("Automated review must cover every seam exactly once")
    for row in supplied_seams:
        key = row["id"]
        if row.get("decision") != "pass" or not str(row.get("observations", "")).strip():
            issues.append(key + ": seam assessment pending or needs repair")
        _confidence(row.get("confidence"), key, issues)
        _validate_refs(row.get("evidence_files"), deps, key, issues, minimum=2 if expected_seams[key].get("rendered_sheet") else 1)
    supplied_ranges = review.get("picture_ranges", [])
    if len(supplied_ranges) != len(expected_ranges) or {x.get("scan") for x in supplied_ranges} != {str(p) for p in expected_ranges}:
        raise ValueError("Automated review must cover every bridge/reframe range exactly once")
    for row in supplied_ranges:
        scan_path = Path(row["scan"]).resolve(); scan = expected_ranges[scan_path]
        if row.get("scan_sha256") != sha(scan_path) or row.get("range_id") != scan.get("range_id"):
            raise ValueError("Picture-range review binding differs")
        if row.get("decision") != "pass" or any(not str(row.get(k, "")).strip() for k in
                ("entry_observation", "interior_observation", "exit_observation")):
            issues.append(row["range_id"] + ": entry/interior/exit assessment pending")
        _confidence(row.get("confidence"), row["range_id"], issues)
        _validate_refs(row.get("evidence_files"), deps, row["range_id"], issues, minimum=2)
    expected_effects = {x["segment_id"]: x for x in report.get("sfx", []) if x.get("mix_role") == "sfx"}
    supplied_effects = review.get("sfx", [])
    if len(supplied_effects) != len(expected_effects) or {x.get("segment_id") for x in supplied_effects} != set(expected_effects):
        raise ValueError("Automated review must cover every new SFX exactly once")
    audition_events = {}
    for path in audition_paths or []:
        verify_manifest(path)
        audition = load(path)
        if audition.get("input_sha256") != sha(input_path) or audition.get("edit_report_sha256") != sha(report_path):
            raise ValueError("Native audition belongs to a different edit")
        for event in audition.get("events", []):
            audition_events.setdefault(event.get("segment_id"), []).append(event)
    for row in supplied_effects:
        key = row["segment_id"]; event = expected_effects[key]
        if row.get("selection_evidence") != event.get("selection_evidence"):
            raise ValueError("Selected SFX evidence path differs: " + key)
        if row.get("event_id") != event.get("event_id") or row.get("target_us") != event.get("target_us"):
            raise ValueError("SFX review event/target differs: " + key)
        required_text = ("anchor", "scene_fit", "sound_observation", "dialogue_impact", "analysis_method", "reason")
        if row.get("decision") != "pass" or any(not str(row.get(k, "")).strip() for k in required_text):
            issues.append(key + ": SFX assessment pending")
        _confidence(row.get("confidence"), key, issues)
        candidates = row.get("candidates_compared", [])
        if not isinstance(candidates, list) or len(candidates) < 2:
            issues.append(key + ": two prepared candidates were not compared")
        else:
            identities = []
            for candidate in candidates:
                try:
                    if not isinstance(candidate, dict) or set(candidate) != {"selection_evidence"}:
                        raise ValueError("candidate must reference selection_evidence")
                    identities.append(candidate_identity(candidate["selection_evidence"], event))
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    issues.append(key + ": invalid candidate evidence: " + str(exc))
            if len(set(identities)) < 2:
                issues.append(key + ": two distinct candidates are required")
            try:
                if candidate_identity(event["selection_evidence"], event) not in identities:
                    issues.append(key + ": comparison must include the selected candidate")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                issues.append(key + ": selected candidate invalid: " + str(exc))
        audition_rows = audition_events.get(key, [])
        if len(audition_rows) != 1 or audition_rows[0].get("event_id") != event.get("event_id") or audition_rows[0].get("target_us") != event.get("target_us"):
            issues.append(key + ": native full/without/solo evidence missing")
        elif row.get("analysis_method") == "multimodal_audio":
            _validate_refs(row.get("audio_evidence"), deps, key + " audio", issues, minimum=1)
        elif row.get("analysis_method") != "spectral_and_metadata":
            issues.append(key + ": state whether semantic audio perception or spectral/metadata analysis was used")
        for warning in (audition_rows or [{}])[0].get("warnings", []):
            if warning in ("very_low_solo_attack_check_source_selection_and_attack", "possible_masking_compare_AB_or_duck_competing_layer"):
                if not str(row.get("reason", "")).strip():
                    issues.append(key + ": measured warning needs a concrete assessment")
    return {"status": "passed" if not issues else "needs_review", "issues": issues,
            "review_sha256": sha(review_path), "review_mode": "autonomous",
            "human_listening_claimed": False, "normal_speed_review_claimed": False}


def _confidence(value, label, issues):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        issues.append(label + ": confidence must be a number from 0 to 1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build")
    for name in ("input", "edit-report", "qc", "seam-scan", "preview", "ffmpeg", "ffprobe", "output"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--range-report", action="append", default=[]); p.add_argument("--audition", action="append", default=[])
    p.add_argument("--evidence-dir")
    q = sub.add_parser("validate")
    for name in ("review", "input", "edit-report", "qc", "seam-scan"):
        q.add_argument("--" + name, required=True)
    q.add_argument("--range-report", action="append", default=[]); q.add_argument("--audition", action="append", default=[])
    args = parser.parse_args()
    if args.command == "build":
        result = build(args.input, args.edit_report, args.qc, args.seam_scan, args.preview, args.ffmpeg, args.ffprobe,
                       args.range_report, args.audition, args.output, args.evidence_dir)
    else:
        result = validate(args.review, args.input, args.edit_report, args.qc, args.seam_scan,
                          args.range_report, args.audition)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
