"""Apply explicit, source-bound edit decisions to an isolated Jianying JSON."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
import struct
import sys
import uuid
import wave
from pathlib import Path


class EditError(Exception):
    pass


def check(ok, message):
    if not ok:
        raise EditError(message)


def uid():
    return str(uuid.uuid4()).upper()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def integer(value, label):
    check(type(value) is int and value >= 0, f"{label} must be a nonnegative integer in microseconds")
    return value


def number(value, label, minimum=0):
    check(type(value) in (int, float) and math.isfinite(value) and value >= minimum,
          f"{label} must be finite and at least {minimum}")
    return value


def span(item, label="range"):
    a, b = integer(item["start_us"], label), integer(item["end_us"], label)
    check(a < b, f"{label} is empty or reversed")
    return a, b


def bounds(segment):
    value = segment["target_timerange"]
    a = integer(value.get("start", 0), "target start")
    duration = integer(value["duration"], "target duration")
    check(duration > 0, "Segment duration must be positive")
    return a, a + duration


def interval(a, b):
    return {"start": a, "duration": b-a}


def lookup(doc):
    result = {}
    for group in doc["materials"].values():
        if not isinstance(group, list):
            continue
        for value in group:
            if not isinstance(value, dict) or "id" not in value:
                continue
            old = result.get(value["id"])
            check(old is None or old == value, f"Conflicting material ID {value['id']}")
            result[value["id"]] = value
    return result


def text(material):
    value = material.get("content", "")
    try:
        return json.loads(value).get("text", "")
    except (ValueError, TypeError, AttributeError):
        return value


def pieces(a, b, cuts):
    cursor = a
    for lo, hi in cuts:
        if hi <= cursor or lo >= b:
            continue
        if cursor < lo:
            yield cursor, lo
        cursor = min(b, hi)
    if cursor < b:
        yield cursor, b


def overlaps(a, b, lo, hi):
    return max(a, lo) < min(b, hi)


def mapped(t, cuts):
    return t - sum(max(0, min(t, hi)-lo) for lo, hi in cuts)


def interpolate(points, t):
    if t <= points[0][0]:
        return points[0][1]
    for (a, x), (b, y) in zip(points, points[1:]):
        if t <= b:
            return x + (y-x)*(t-a)/(b-a)
    return points[-1][1]


def volume_points(segment):
    groups = segment.get("common_keyframes") or []
    check(all(g.get("property_type") == "KFTypeVolume" for g in groups),
          f"Segment {segment['id']} has unsupported animated properties")
    check(len(groups) <= 1, f"Segment {segment['id']} has multiple volume curves")
    source = segment.get("source_timerange") or {}
    ins = source.get("start", 0)
    if not groups:
        return [(ins, number(segment.get("volume", 1), "volume"))]
    check(abs(segment.get("volume", 1)-1) < 1e-8,
          f"Segment {segment['id']} combines a scalar volume with volume keyframes; normalize in the verified backend first")
    points = []
    for key in groups[0]["keyframe_list"]:
        check(key.get("curveType", "Line") in ("Line", "Linear", "") and not key.get("graphID"),
              f"Segment {segment['id']} uses a nonlinear volume curve")
        for control in ("left_control", "right_control"):
            value = key.get(control) or {}
            check(not value.get("x", 0) and not value.get("y", 0),
                  f"Segment {segment['id']} uses curved keyframe handles")
        values = key["values"]
        check(len(values) == 1, f"Segment {segment['id']} has a nonscalar volume keyframe")
        points.append((integer(key.get("time_offset", 0), "volume source offset"), number(values[0], "keyframe volume")))
    points.sort()
    check(points and len({t for t, _ in points}) == len(points), f"Invalid volume curve in {segment['id']}")
    return points


def set_volume(segment, points, nominal=None):
    check(points, "Empty volume envelope")
    segment["volume"] = 1.0
    segment["last_nonzero_volume"] = max(v for _, v in points) if nominal is None else nominal
    segment["common_keyframes"] = [{"id": uid(), "property_type": "KFTypeVolume", "material_id": "",
        "keyframe_list": [{"id": uid(), "time_offset": t, "values": [v], "curveType": "Line", "graphID": "",
                           "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}}
                          for t, v in points]}]


def fade_values(segment, mats):
    fades = [mats[r] for r in segment.get("extra_material_refs", []) if mats[r].get("type") == "audio_fade"]
    check(len(fades) <= 1, f"Segment {segment['id']} has multiple audio fades")
    if not fades:
        return 0, 0
    fade = fades[0]
    check(not (set(fade)-{"id", "type", "fade_in_duration", "fade_out_duration"}),
          f"Segment {segment['id']} has an unsupported fade shape")
    fi = integer(fade.get("fade_in_duration", 0), "fade in")
    fo = integer(fade.get("fade_out_duration", 0), "fade out")
    check(fi+fo <= bounds(segment)[1]-bounds(segment)[0], f"Fades overlap within {segment['id']}")
    return fi, fo


def replace_fade(doc, segment, fi, fo):
    mats = lookup(doc)
    segment["extra_material_refs"] = [r for r in segment.get("extra_material_refs", []) if mats[r].get("type") != "audio_fade"]
    if fi or fo:
        value = {"id": uid(), "type": "audio_fade", "fade_in_duration": fi, "fade_out_duration": fo}
        doc["materials"].setdefault("audio_fades", []).append(value)
        segment["extra_material_refs"].append(value["id"])


SAFE_REFS = {None, "", "none", "speed", "audio_fade", "placeholder_info", "canvas_color",
             "canvas_blur", "beats", "vocal_separation", "sound_channel_mapping"}


def editable(segment, track_type, mats, dropped_transitions):
    identifier = segment["id"]
    check(segment.get("speed", 1) == 1 and not segment.get("reverse") and not segment.get("is_reverse"),
          f"Segment {identifier} has a speed change or reverse playback")
    for key in ("animation", "animations", "animation_ids", "keyframe_refs", "keyframe_refs_", "time_reversal"):
        check(not segment.get(key), f"Segment {identifier} has unsupported {key}")
    source = segment.get("source_timerange")
    check(source is not None, f"Segment {identifier} has no ordinary source range")
    a, b = bounds(segment)
    check(abs(source["duration"]-(b-a)) <= 4, f"Segment {identifier} has nonunit or ambiguous source timing")
    material = mats[segment["material_id"]]
    allowed = {"video", "photo"} if track_type == "video" else {"audio", "music", "extract_music"}
    check(material.get("type") in allowed, f"Segment {identifier} uses unsupported material type {material.get('type')!r}")
    volume_points(segment)
    for ref in segment.get("extra_material_refs", []):
        value = mats[ref]
        kind = value.get("type")
        if kind == "transition":
            check(ref in dropped_transitions, f"Segment {identifier} touches transition {ref}; explicitly list it in drop_transition_ids")
        else:
            check(kind in SAFE_REFS, f"Segment {identifier} has unsupported timed effect {kind!r} ({ref})")
        if kind == "speed":
            check(value.get("speed", 1) == 1 and not value.get("curve_speed"), f"Segment {identifier} has a speed-curve reference")


def crop(doc, segment, track_type, lo, hi, map_t, dropped_transitions, edge_fade=0):
    a, b = bounds(segment)
    result = copy.deepcopy(segment)
    result["target_timerange"] = interval(map_t(lo), map_t(hi))
    if result["target_timerange"] != segment["target_timerange"]:
        check(track_type in ("video", "audio", "text"),
              f"Cannot retime unknown track type {track_type!r}, segment {segment['id']}")
    if (lo, hi) == (a, b):
        return result
    check(track_type in ("video", "audio"), f"Cannot crop track type {track_type!r}, segment {segment['id']}")
    mats = lookup(doc)
    editable(segment, track_type, mats, dropped_transitions)
    result["id"] = uid()
    source = segment["source_timerange"]
    ins = source.get("start", 0)
    x, y = ins+lo-a, ins+hi-a
    result["source_timerange"] = interval(x, y)
    result["extra_material_refs"] = [r for r in result.get("extra_material_refs", []) if r not in dropped_transitions]
    points = volume_points(segment)
    fi, fo = fade_values(segment, mats)
    times = {x, y-1, *[t for t, _ in points if x < t < y-1]}
    # Baking the existing linear fade keeps its original position when a crop
    # begins or ends inside it. Extra samples bound the product-curve error.
    for start, duration in ((ins, fi), (ins+b-a-fo, fo)):
        if duration:
            times.update(max(x, min(y-1, start+round(duration*i/16))) for i in range(17))
    if segment.get("common_keyframes") or fi or fo:
        def gain(t):
            value = interpolate(points, t)
            if fi:
                value *= max(0, min(1, (t-ins)/fi))
            if fo:
                value *= max(0, min(1, (ins+b-a-t)/fo))
            return value
        set_volume(result, [(t, gain(t)) for t in sorted(times)], max(v for _, v in points))
    if track_type == "audio" or fi or fo:
        left = edge_fade if track_type == "audio" and lo != a else 0
        right = edge_fade if track_type == "audio" and hi != b else 0
        check(left+right <= hi-lo, f"New seam fades exceed cropped segment {segment['id']}")
        replace_fade(doc, result, left, right)
    return result


def validate_document(doc):
    check(isinstance(doc.get("id"), str) and isinstance(doc.get("tracks"), list), "Invalid timeline identity or tracks")
    duration = integer(doc["duration"], "timeline duration")
    mats = lookup(doc)
    ids = set()
    for track in doc["tracks"]:
        check(isinstance(track.get("id"), str) and track["id"] not in ids, "Missing or repeated track ID")
        ids.add(track["id"])
        for segment in track["segments"]:
            check(segment["id"] not in ids, f"Repeated segment ID {segment['id']}")
            ids.add(segment["id"])
            a, b = bounds(segment)
            check(0 <= a < b <= duration, f"Out-of-bounds segment {segment['id']}")
            for ref in [segment["material_id"], *segment.get("extra_material_refs", [])]:
                check(ref in mats, f"Missing material reference {ref} in {segment['id']}")
            source = segment.get("source_timerange")
            if source:
                integer(source.get("start", 0), "source start")
                integer(source["duration"], "source duration")
    return {"timeline_id": doc["id"], "duration_us": duration, "tracks": len(doc["tracks"]), "segments": len(ids)-len(doc["tracks"])}


def inspect_document(doc):
    summary = validate_document(doc)
    mats = lookup(doc)
    summary["tracks"] = []
    for track in doc["tracks"]:
        value = {"id": track["id"], "type": track["type"], "name": track.get("name", ""), "segments": []}
        for segment in track["segments"]:
            material = mats[segment["material_id"]]
            a, b = bounds(segment)
            item = {"id": segment["id"], "start_us": a, "end_us": b, "source_timerange": segment.get("source_timerange"),
                    "material_id": material["id"], "path": material.get("path"), "volume": segment.get("volume", 1),
                    "keyframe_properties": [g.get("property_type") for g in segment.get("common_keyframes") or []]}
            if track["type"] == "text":
                item["text"] = text(material)
            value["segments"].append(item)
        summary["tracks"].append(value)
    return summary


def check_static_caption(segment, materials):
    identifier = segment['id']
    material = materials[segment['material_id']]
    timed_keys = ('words', 'current_words', 'combo_info', 'animation', 'animations')
    segment_timing = ('source_timerange', 'common_keyframes', 'keyframe_refs', 'keyframe_refs_',
                      'animation', 'animations', 'animation_ids')
    check(material.get('type') in ('text', 'subtitle') and not any(material.get(k) for k in timed_keys)
          and not any(segment.get(k) for k in segment_timing),
          f'Caption {identifier} has timed content or animation')
    for key in ('caption_template_info', 'lyrics_template'):
        template = material.get(key) or {}
        check(isinstance(template, dict) and not any(template.values()),
              f'Caption {identifier} uses a timed or unverified template')
    for ref in segment.get('extra_material_refs', []):
        effect = materials[ref]
        check(effect.get('type') == 'sticker_animation'
              and not any(value for key, value in effect.items() if key not in ('id', 'type')),
              f'Caption {identifier} uses a timed or unverified effect')


BEAT_KINDS = {"hook", "info", "conflict", "anxiety", "decision", "reveal", "impact",
              "emotional_reaction", "prop", "door", "phone", "tail"}
BEAT_EVENT_FIELDS = {"id", "kind", "target_us", "screen_change", "dialogue_anchor", "character_state",
                     "cue", "sfx_segment_id", "attack_offset_us", "duck", "reason", "verified", "sound_action"}


def map_beat_events(doc, plan, cuts):
    result = []
    seen = set()
    for row in plan.get("beat_events", []):
        check(isinstance(row, dict), "Beat event must be an object")
        check(not (set(row)-BEAT_EVENT_FIELDS), f"Unknown beat event fields: {sorted(set(row)-BEAT_EVENT_FIELDS)}")
        identifier = row.get("id")
        check(isinstance(identifier, str) and identifier.strip() and identifier not in seen,
              "Beat event IDs must be unique nonempty strings")
        seen.add(identifier)
        check(row.get("kind") in BEAT_KINDS, f"Unsupported beat event kind: {row.get('kind')!r}")
        target = integer(row.get("target_us"), "beat event target")
        check(target < doc["duration"], f"Beat event {identifier} exceeds the input timeline")
        check(not any(a <= target < b for a, b in cuts), f"Beat event {identifier} lies in a removed interval")
        for name in ("screen_change", "dialogue_anchor", "character_state", "cue", "reason"):
            check(isinstance(row.get(name, ""), str), f"Beat event {name} must be a string")
        check(isinstance(row.get("sfx_segment_id", ""), str), "Beat event sfx_segment_id must be a string")
        if row.get("sfx_segment_id"):
            linked = [s for t in doc["tracks"] if t.get("type") == "audio" for s in t["segments"] if s["id"] == row["sfx_segment_id"]]
            check(len(linked) == 1, f"Beat event {identifier} references a missing audio segment")
            left, right = bounds(linked[0])
            check(left <= target < right, f"Beat event {identifier} is outside its linked audio segment")
        if "attack_offset_us" in row:
            integer(row["attack_offset_us"], "beat event attack offset")
        check(type(row.get("duck", False)) is bool, "Beat event duck must be a boolean")
        check(type(row.get("verified", False)) is bool, "Beat event verified must be a boolean")
        if "sound_action" in row:
            check(row["sound_action"] in ("sfx", "original", "bgm_change", "silence"), "Unknown beat sound_action")
        event = copy.deepcopy(row)
        event["input_target_us"] = target
        event["target_us"] = mapped(target, cuts)
        event["verified"] = row.get("verified", False)
        result.append(event)
    # New metadata is optional for older plans, but explicit links must be real.
    for row in plan.get("sfx", []):
        if row.get("event_id") is not None:
            check(row["event_id"] in seen, "SFX event_id is not a declared beat")
    return result


def prepare_plan(doc, plan, input_hash):
    check(isinstance(plan, dict), "Plan must be a JSON object")
    check(plan.get("schema_version") == 1, "Expected schema_version 1")
    known = {"schema_version", "timeline_id", "input_sha256", "primary_video_track_id", "boundary_tolerance_us", "cuts", "speech",
             "remove_caption_ids", "shorten_caption_ids", "drop_transition_ids", "music", "audio_roles", "audio_edge_fades_us", "bridges", "flips",
             "beat_events", "sfx", "sfx_template_segment_id", "merge_contiguous", "reframes"}
    check(not (set(plan)-known), f"Unknown plan fields: {sorted(set(plan)-known)}")
    check(type(plan.get("merge_contiguous", True)) is bool, "merge_contiguous must be a boolean")
    for name in ("cuts", "bridges", "flips", "reframes", "beat_events", "sfx", "remove_caption_ids", "shorten_caption_ids", "drop_transition_ids"):
        check(isinstance(plan.get(name, []), list), f"{name} must be an array")
    for name in ("music", "audio_roles", "audio_edge_fades_us"):
        check(isinstance(plan.get(name, {}), dict), f"{name} must be an object")
    for name in ("segment_ids", "crossfades", "ducks"):
        check(isinstance(plan.get("music", {}).get(name, []), list), f"music.{name} must be an array")
    reasons = plan.get("music", {}).get("energy_reasons", {})
    check(isinstance(reasons, dict), "music.energy_reasons must be an object")
    check(set(reasons) <= set(plan.get("music", {}).get("segment_ids", [])),
          "Energy reasons reference unclassified music segments")
    check(all(isinstance(value, str) and value.strip() for value in reasons.values()),
          "Music energy reasons must be nonempty strings")
    check(plan.get("timeline_id") == doc["id"] and plan.get("input_sha256") == input_hash, "Plan identity or input hash is stale")
    tracks = {t["id"]: t for t in doc["tracks"]}
    primary = plan.get("primary_video_track_id")
    check(primary in tracks and tracks[primary]["type"] == "video", "Specify primary_video_track_id")
    tolerance = integer(plan.get("boundary_tolerance_us", 4), "boundary tolerance")
    check(tolerance <= 100, "Boundary tolerance is limited to 100 microseconds")
    edges = [v for s in tracks[primary]["segments"] for v in bounds(s)]
    check(edges, "Primary video track is empty")
    def snap(t):
        nearest = min(edges, key=lambda x: abs(x-t))
        return nearest if abs(nearest-t) <= tolerance else t
    cuts = []
    for row in plan.get("cuts", []):
        a, b = map(snap, span(row, "cut"))
        check(a < b <= doc["duration"] and (not cuts or cuts[-1][1] <= a), "Cuts must be ordered, disjoint and within the timeline")
        cuts.append((a, b))
    removed = set(plan.get("remove_caption_ids", []))
    shortened = set(plan.get('shorten_caption_ids', []))
    captions = {s["id"]: s for t in doc["tracks"] if t["type"] == "text" for s in t["segments"]}
    check(removed <= captions.keys(), "Unknown removed caption ID")
    check(shortened <= captions.keys() and not (removed & shortened), 'Unknown or conflicting shortened caption ID')
    materials = lookup(doc) if shortened else {}
    for identifier, segment in captions.items():
        a, b = bounds(segment)
        retained = sum(y-x for x, y in pieces(a, b, cuts))
        if identifier in shortened:
            check(0 < retained < b-a, f'Caption {identifier} must have a partially retained range')
            check_static_caption(segment, materials)
        else:
            check(retained == b-a or (retained == 0 and identifier in removed), f"Cut touches protected caption {identifier}")
        check(identifier not in removed or retained == 0, f"Removed caption {identifier} must be wholly covered by cuts")
    if cuts:
        speech = plan.get("speech") or {}
        check(isinstance(speech, dict), "speech must be an object")
        check(speech.get("coverage_us") == [0, doc["duration"]], "Cuts require speech.coverage_us covering the complete input timeline")
        spans = speech.get("intervals")
        check(isinstance(spans, list), "Provide analyzed speech intervals, including an empty list for a verified silent timeline")
        permitted = set(speech.get("remove_ids", []))
        seen = set()
        for row in spans:
            identifier = row["id"]
            check(isinstance(identifier, str) and identifier not in seen, "Speech interval IDs must be unique strings")
            seen.add(identifier)
            a, b = span(row, "speech interval")
            check(b <= doc["duration"], f"Speech interval {identifier} exceeds the timeline")
            retained = sum(y-x for x, y in pieces(a, b, cuts))
            check(retained == b-a or (retained == 0 and identifier in permitted), f"Cut truncates or removes protected speech {identifier}")
            check(identifier not in permitted or retained == 0, f"Authorized speech removal {identifier} is not completely cut")
        check(permitted <= seen, "Unknown authorized speech removal ID")
    map_beat_events(doc, plan, cuts)
    return cuts, tracks, primary


def map_music(doc, segment, cuts):
    a, b = bounds(segment)
    na, nb = mapped(a, cuts), mapped(b, cuts)
    if na == nb:
        return None
    if nb-na == b-a:
        result = copy.deepcopy(segment)
        result["target_timerange"] = interval(na, nb)
        return result
    mats = lookup(doc)
    editable(segment, "audio", mats, set())
    points = volume_points(segment)
    ins = segment["source_timerange"].get("start", 0)
    for lo, hi in cuts:
        if overlaps(a, b, lo, hi):
            x, y = ins+max(a, lo)-a, ins+min(b, hi)-a
            check(abs(interpolate(points, x)-interpolate(points, y)) <= 1e-7,
                  f"Cut skips unequal music-volume states in {segment['id']}; explicitly reauthor that envelope")
    result = copy.deepcopy(segment)
    result["target_timerange"] = interval(na, nb)
    result["source_timerange"] = interval(ins, ins+nb-na)
    if segment.get("common_keyframes"):
        times = {a, b-1, *[max(a, min(b-1, a+t-ins)) for t, _ in points]}
        times.update(max(a, min(b-1, t)) for cut in cuts for t in cut)
        revised = {}
        for t in sorted(times):
            if any(lo <= t < hi for lo, hi in cuts):
                continue
            at = max(na, min(nb-1, mapped(t, cuts)))
            revised[ins+at-na] = interpolate(points, ins+t-a)
        set_volume(result, sorted(revised.items()), max(v for _, v in points))
    return result


def ripple(doc, before, plan, cuts):
    music = set(plan.get("music", {}).get("segment_ids", []))
    all_audio = {s["id"] for t in before["tracks"] if t["type"] == "audio" for s in t["segments"]}
    check(music <= all_audio, "Unknown music segment ID")
    dropped = set(plan.get("drop_transition_ids", []))
    shortened = set(plan.get('shorten_caption_ids', []))
    mats = lookup(doc)
    check(all(i in mats and mats[i].get("type") == "transition" for i in dropped), "Unknown dropped transition ID")
    roles = plan.get("audio_roles", {})
    check(set(roles) <= all_audio, "Unknown audio-role segment ID")
    check(set(roles.values()) <= {"dialogue", "ambience", "sfx", "other"}, "Unknown audio role")
    fades = plan.get("audio_edge_fades_us", {})
    check(set(fades) <= {"dialogue", "ambience", "sfx", "other"}, "Unknown audio edge-fade role")
    for value in fades.values():
        integer(value, "audio edge fade")
    for track in doc["tracks"]:
        revised = []
        for segment in track["segments"]:
            a, b = bounds(segment)
            if segment["id"] in music:
                item = map_music(doc, segment, cuts)
                if item:
                    revised.append(item)
                continue
            if track["type"] == "text" and segment["id"] in plan.get("remove_caption_ids", []):
                continue
            if track['type']=='text' and segment['id'] in shortened:
                # The original text stays continuously visible across the collapsed pause.
                item = copy.deepcopy(segment)
                item['target_timerange'] = interval(mapped(a, cuts), mapped(b, cuts))
                revised.append(item)
                continue
            for lo, hi in pieces(a, b, cuts):
                edge = fades.get(roles.get(segment["id"], "other"), 0)
                revised.append(crop(doc, segment, track["type"], lo, hi, lambda t: mapped(t, cuts), dropped, edge))
        track["segments"] = revised
    doc["duration"] = mapped(before["duration"], cuts)


def replace_range(doc, track, a, b, replacement, dropped):
    revised = []
    for segment in track["segments"]:
        for lo, hi in pieces(*bounds(segment), [(a, b)]):
            revised.append(crop(doc, segment, "video", lo, hi, lambda t: t, dropped))
    revised.extend(replacement)
    track["segments"] = sorted(revised, key=lambda s: bounds(s)[0])


def static_reframe(item, config):
    """Apply an explicit static punch-in; no animation, masks or guessed subject tracking."""
    check(isinstance(config, dict) and not (set(config)-{"scale_multiplier", "offset_x", "offset_y"}),
          "Reframe accepts only scale_multiplier, offset_x and offset_y")
    check(not item.get("common_keyframes"), "Cannot reframe a segment with animated properties")
    settings = copy.deepcopy(item.get("clip") or {})
    check(not settings.get("rotation", 0), "Rotated video needs native reframe verification")
    check(not (set(settings)-{"scale", "transform", "flip", "rotation", "alpha"}),
          "Reframe has unknown clip settings; verify them natively")
    factor = number(config.get("scale_multiplier"), "reframe scale multiplier", 1.05)
    check(factor <= 1.5, "Reframe scale multiplier is limited to 1.5; choose a real close-up for tighter framing")
    scale = settings.setdefault("scale", {})
    position = settings.setdefault("transform", {})
    for axis in ("x", "y"):
        offset = number(config.get("offset_"+axis, 0), "reframe offset", -.25)
        check(offset <= .25, "Reframe offset is limited to +/-0.25 canvas units")
        scale[axis] = number(scale.get(axis, 1), "original scale", .01)*factor
        position[axis] = number(position.get(axis, 0), "original position", -100)+offset
    item["clip"] = settings


def picture(doc, before, plan, cuts, primary, seams):
    old_tracks = {t["id"]: t for t in before["tracks"]}
    tracks = {t["id"]: t for t in doc["tracks"]}
    originals = {s["id"]: (t, s) for t in before["tracks"] for s in t["segments"]}
    mats = lookup(doc)
    dropped = set(plan.get("drop_transition_ids", []))
    used = {}
    for operation, rows in (("bridge", plan.get("bridges", [])), ("flip", plan.get("flips", [])),
                            ("reframe", plan.get("reframes", []))):
        for row in rows:
            allowed = {"start_us", "end_us", "track_id", "rationale"}
            allowed |= {"donor_segment_id", "source_start_us", "reframe"} if operation == "bridge" else {"horizontal"} if operation == "flip" else {"reframe"}
            check(not (set(row)-allowed), f"Unknown {operation} fields: {sorted(set(row)-allowed)}")
            check(isinstance(row.get("rationale", ""), str), "Picture rationale must be a string")
            track_id = row.get("track_id", primary)
            check(track_id in tracks and tracks[track_id]["type"] == "video", f"Invalid {operation} video track")
            lo, hi = span(row, operation)
            check(hi <= before["duration"], f"{operation} exceeds timeline")
            a, b = mapped(lo, cuts), mapped(hi, cuts)
            check(a < b, f"{operation} range was completely removed")
            slots = used.setdefault((operation, track_id), [])
            check(not any(overlaps(a, b, x, y) for x, y in slots), f"Overlapping {operation} ranges")
            slots.append((a, b))
            replacements = []
            if operation == "bridge":
                donor = originals.get(row["donor_segment_id"])
                check(donor is not None and donor[0]["type"] == "video", "Bridge donor must identify an input video segment")
                template = donor[1]
                editable(template, "video", mats, dropped)
                material = mats[template["material_id"]]
                check(material.get("has_sound_separated") or material.get("has_audio") is False or template.get("volume", 1) == 0,
                      "Picture-only bridge needs a silent or sound-separated donor")
                source = integer(row["source_start_us"], "bridge source start")
                check(source+b-a <= material.get("duration", -1), "Bridge exceeds donor source duration")
                check(not template.get("common_keyframes"), "Bridge donor has time-dependent volume; choose a plain silent video donor")
                item = copy.deepcopy(template)
                item.update(id=uid(), volume=0.0, target_timerange=interval(a, b), source_timerange=interval(source, source+b-a))
                item["extra_material_refs"] = [r for r in item.get("extra_material_refs", []) if r not in dropped and mats[r].get("type") != "audio_fade"]
                if "reframe" in row:
                    static_reframe(item, row["reframe"])
                replacements.append(item)
            else:
                if operation == "flip":
                    check(type(row.get("horizontal")) is bool, "Flip horizontal must be true or false")
                for segment in tracks[track_id]["segments"]:
                    x, y = bounds(segment)
                    if not overlaps(a, b, x, y):
                        continue
                    editable(segment, "video", mats, dropped)
                    check(not segment.get("common_keyframes"), "Cannot flip an animated video segment")
                    item = crop(doc, segment, "video", max(a, x), min(b, y), lambda t: t, dropped)
                    settings = item.get("clip") or {}
                    check(not settings.get("rotation", 0), "Rotated video needs native flip verification")
                    if operation == "flip":
                        old = settings.setdefault("flip", {}).get("horizontal", False)
                        if old != row["horizontal"]:
                            position = settings.setdefault("transform", {})
                            position["x"] = -position.get("x", 0)
                            settings["flip"]["horizontal"] = row["horizontal"]
                        item["clip"] = settings
                    else:
                        static_reframe(item, row.get("reframe"))
                    replacements.append(item)
            replace_range(doc, tracks[track_id], a, b, replacements, dropped)
            seams.update((a, b))


def music_envelopes(doc, plan, cuts):
    config = plan.get("music", {})
    identifiers = set(config.get("segment_ids", []))
    songs = {s["id"]: s for t in doc["tracks"] if t["type"] == "audio" for s in t["segments"] if s["id"] in identifiers}
    incoming, outgoing = {}, {}
    for row in config.get("crossfades", []):
        check(row.get("mode", "equal_power") == "equal_power", "Unsupported crossfade mode")
        left, right = songs.get(row["left_id"]), songs.get(row["right_id"])
        check(left is not None and right is not None, "Crossfade music was removed or was not explicitly classified")
        la, lb = bounds(left)
        ra, rb = bounds(right)
        check(la < ra < lb < rb, "Crossfade needs two successive, overlapping music clips")
        check(left["id"] not in outgoing and right["id"] not in incoming, "Repeated crossfade edge")
        check(not any(s["id"] not in (left["id"], right["id"]) and overlaps(ra, lb, *bounds(s)) for s in songs.values()),
              "Triple music overlap needs an explicit native mix")
        steps = row.get("steps", 16)
        check(type(steps) is int and 4 <= steps <= 128, "Crossfade steps must be 4 through 128")
        outgoing[left["id"]] = (ra, lb, steps)
        incoming[right["id"]] = (ra, lb, steps)
    ducks = config.get("ducks", [])
    for row in ducks:
        lo, hi = span(row, "music duck")
        check(hi <= mapped_input_duration(plan, doc, cuts), "Duck exceeds input timeline")
        check(0 <= number(row["factor"], "duck factor") <= 1, "Duck factor must be at most one")
        integer(row.get("attack_us", 0), "duck attack")
        integer(row.get("release_us", 0), "duck release")
        check(set(row.get("segment_ids", identifiers)) <= identifiers, "Unknown duck music segment")
    for identifier, segment in songs.items():
        a, b = bounds(segment)
        active_ducks = []
        for row in ducks:
            lo, hi = map(lambda t: mapped(t, cuts), span(row))
            if (identifier in row.get("segment_ids", identifiers) and lo != hi
                    and overlaps(a, b, lo-row.get("attack_us", 0), hi+row.get("release_us", 0))):
                active_ducks.append(row)
        if not active_ducks and identifier not in incoming and identifier not in outgoing:
            continue
        editable(segment, "audio", lookup(doc), set())
        ins = segment["source_timerange"].get("start", 0)
        source_points = volume_points(segment)
        base = [(max(a, min(b-1, a+t-ins)), v) for t, v in source_points]
        base = sorted(dict(base).items())
        nominal = max(v for _, v in source_points)
        curves = [base]
        for row in active_ducks:
            lo, hi = map(lambda t: mapped(t, cuts), span(row))
            factor = row["factor"]
            attack = max(1, row.get("attack_us", 0))
            release = max(1, row.get("release_us", 0))
            curves.append([(lo-attack, nominal), (lo, nominal*factor),
                           (hi, nominal*factor), (hi+release, nominal)])
        times = {a, b-1, *[max(a, min(b-1, t)) for curve in curves for t, _ in curve]}
        # Include intersections so min(existing envelope, duck ceiling) stays exact.
        edges = sorted(times)
        for lo, hi in zip(edges, edges[1:]):
            lines = [(interpolate(curve, lo), interpolate(curve, hi)) for curve in curves]
            for i, (x0, x1) in enumerate(lines):
                for y0, y1 in lines[i+1:]:
                    denominator = (x1-x0)-(y1-y0)
                    if denominator:
                        u = (y0-x0)/denominator
                        if 0 < u < 1:
                            times.add(round(lo+(hi-lo)*u))
        for edge in (incoming.get(identifier), outgoing.get(identifier)):
            if edge:
                lo, hi, steps = edge
                times.update(max(a, min(b-1, round(lo+(hi-lo)*i/steps))) for i in range(steps+1))
        result = []
        for t in sorted(times):
            gain = min(interpolate(curve, t) for curve in curves)
            if identifier in incoming:
                lo, hi, _ = incoming[identifier]
                gain *= math.sin(max(0, min(1, (t-lo)/(hi-lo)))*math.pi/2)
            if identifier in outgoing:
                lo, hi, _ = outgoing[identifier]
                gain *= math.cos(max(0, min(1, (t-lo)/(hi-lo)))*math.pi/2)
            result.append((ins+t-a, gain))
        fi, fo = fade_values(segment, lookup(doc))
        set_volume(segment, result, nominal)
        replace_fade(doc, segment, 0 if identifier in incoming else fi, 0 if identifier in outgoing else fo)


def mapped_input_duration(plan, doc, cuts):
    return doc["duration"] + sum(b-a for a, b in cuts)


def wav_info(path, start, duration):
    try:
        with wave.open(str(path), "rb") as audio:
            check(audio.getcomptype() == "NONE" and audio.getsampwidth() in (1, 2, 3, 4), "SFX requires integer PCM WAV")
            rate, channels, width = audio.getframerate(), audio.getnchannels(), audio.getsampwidth()
            total = round(audio.getnframes()*1_000_000/rate)
            check(start+duration <= total, "SFX source range exceeds the WAV")
            audio.setpos(round(start*rate/1_000_000))
            count = round(duration*rate/1_000_000)
            peak = 0
            remaining = count
            while remaining:
                raw = audio.readframes(min(65536, remaining))
                check(raw, "Unexpected end of SFX WAV")
                remaining -= len(raw)//(width*channels)
                if width == 1:
                    peak = max(peak, max(abs(x-128) for x in raw))
                elif width in (2, 4):
                    fmt = "<h" if width == 2 else "<i"
                    peak = max(peak, max(abs(x[0]) for x in struct.iter_unpack(fmt, raw)))
                else:
                    peak = max(peak, max(abs(int.from_bytes(raw[i:i+3], "little", signed=True)) for i in range(0, len(raw), 3)))
            check(peak > 0, "SFX selected source range is silent")
            return total, 20*math.log10(peak/(2**(width*8-1)))
    except wave.Error as exc:
        raise EditError("SFX must be integer PCM WAV. Convert and measure a separate local asset first.") from exc


def effects(doc, before, plan, cuts, output):
    rows = plan.get("sfx", [])
    if not rows:
        return []
    originals = {s["id"]: s for t in before["tracks"] if t["type"] == "audio" for s in t["segments"]}
    template = originals.get(plan.get("sfx_template_segment_id"))
    check(template is not None, "SFX requires an explicit sfx_template_segment_id from an existing audio track")
    editable(template, "audio", lookup(before), set())
    events = []
    event_ids = {e["id"]:e for e in plan.get("beat_events", [])}
    linked_events = set()
    for row in rows:
        path = Path(row["path"])
        check(path.is_absolute() and path.is_file(), f"SFX path must identify an absolute local file: {path}")
        check(digest(path) == row["sha256"], f"SFX file changed: {path}")
        ins = integer(row.get("source_start_us", 0), "SFX source start")
        duration = integer(row["source_duration_us"], "SFX source duration")
        attack = integer(row["attack_offset_us"], "SFX attack offset")
        check(0 <= attack < duration, "SFX attack must be within the selected source range")
        dest = output / "assets" / (row["sha256"]+".wav")
        dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            shutil.copyfile(path, dest)
        check(digest(dest) == row["sha256"], "Copied SFX checksum failed")
        total, source_peak = wav_info(dest, ins, duration)
        if "source_peak_dbfs" in row:
            check(abs(row["source_peak_dbfs"]-source_peak) <= .15, "SFX source peak differs from the measured selected range")
        role = row.get("mix_role", "sfx")
        check(role in ("bgm", "sfx", "other"), "SFX mix_role must be bgm, sfx, or other")
        event_id = row.get("event_id")
        selection = row.get("selection_evidence")
        selection_hash = None
        if selection:
            evidence_path = Path(selection).resolve(strict=True)
            evidence = read(evidence_path)
            selected = evidence.get("plan_sfx_row", {})
            for field in ("sha256", "source_start_us", "source_duration_us", "attack_offset_us", "target_us"):
                check(selected.get(field) == row.get(field), f"SFX selection evidence differs: {field}")
            check(evidence.get("event_id") == event_id, "SFX selection event differs")
            check(evidence.get("measurements", {}).get("silent") is False, "SFX selection is not measured as audible signal")
            selection_hash = digest(evidence_path)
        if event_id is not None:
            check(isinstance(event_id, str) and event_id in event_ids, "SFX event_id must reference an actual beat event")
            check(event_id not in linked_events, "Use one main SFX per event_id; record auxiliary layers as separate events")
            check(role == "sfx", "Only a sound effect can claim an SFX event_id")
            check(abs(row["target_us"]-event_ids[event_id]["target_us"]) <= 80000, "SFX attack differs from its beat by more than 80 ms")
            linked_events.add(event_id)
        if "fader_db" in row:
            fader = number(row["fader_db"], "SFX fader dB", -120)
            if role == "bgm":
                check(-9 <= fader <= -5, "BGM fader_db must stay between -9 and -5 dB")
            elif role == "sfx":
                check(-5 <= fader <= -2, "SFX fader_db must stay between -5 and -2 dB")
            derived_peak = source_peak + fader
            if "target_peak_dbfs" in row:
                check(abs(row["target_peak_dbfs"]-derived_peak) <= .15,
                      "SFX target peak must equal source peak plus fader_db")
            peak = derived_peak
        else:
            peak = number(row["target_peak_dbfs"], "SFX target peak", -120)
        check(peak <= 0, "SFX target peak cannot exceed 0 dBFS")
        target = integer(row["target_us"], "SFX target")
        check(target < before["duration"] and not any(a <= target < b for a, b in cuts), "SFX target lies in a removed or out-of-bounds interval")
        at = mapped(target, cuts)
        start, end = at-attack, at-attack+duration
        check(0 <= start < end <= doc["duration"], "SFX would extend beyond the edited timeline")
        fi = integer(row.get("fade_in_us", 0), "SFX fade in")
        fo = integer(row.get("fade_out_us", 0), "SFX fade out")
        check(fi+fo <= duration, "SFX fades exceed its duration")
        check(isinstance(row.get("track_name"), str) and row["track_name"], "SFX needs a track_name")
        material = {"id": uid(), "type": "music", "name": path.name, "path": str(dest.resolve()), "duration": total,
                    "music_source": "local", "resource_id": "", "category_name": "local"}
        doc["materials"].setdefault("audios", []).append(material)
        speed = {"id": uid(), "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}
        doc["materials"].setdefault("speeds", []).append(speed)
        segment = copy.deepcopy(template)
        segment.update(id=uid(), material_id=material["id"], source_timerange=interval(ins, ins+duration),
                       target_timerange=interval(start, end), volume=10**((peak-source_peak)/20),
                       common_keyframes=[], extra_material_refs=[speed["id"]], visible=True,
                       track_attribute=0, desc=row.get("purpose", ""))
        matches = [t for t in doc["tracks"] if t.get("name") == row["track_name"]]
        check(len(matches) <= 1, "SFX track_name matches multiple existing tracks")
        track = matches[0] if matches else None
        if track is None:
            track = {"id": uid(), "type": "audio", "name": row["track_name"], "is_default_name": False, "segments": []}
            doc["tracks"].append(track)
        check(track["type"] == "audio", "SFX track_name conflicts with an existing non-audio track")
        existing_indices = {s["track_render_index"] for s in track["segments"]
                            if type(s.get("track_render_index")) is int}
        check(len(existing_indices) <= 1, "SFX destination track has inconsistent render indices")
        used_indices = [s["track_render_index"] for t in doc["tracks"] if t["type"] == "audio"
                        for s in t["segments"] if type(s.get("track_render_index")) is int]
        segment["track_render_index"] = next(iter(existing_indices)) if existing_indices else max(used_indices, default=-1)+1
        track["segments"].append(segment)
        replace_fade(doc, segment, fi, fo)
        events.append({"segment_id": segment["id"], "target_us": at, "input_target_us": target,
                       "start_us": start, "end_us": end, "attack_offset_us": attack,
                       "source_start_us": ins, "source_duration_us": duration,
                       "source_peak_dbfs": source_peak, "target_peak_dbfs": peak,
                       "mix_role": role, "fader_db": peak-source_peak,
                       "fade_in_us": fi, "fade_out_us": fo,
                       "track_name": row["track_name"], "purpose": row.get("purpose", ""),
                       "sha256": row["sha256"], "path": str(dest.resolve()),
                       "event_id": event_id, "event_class": row.get("event_class"),
                       "selection_evidence": selection, "selection_evidence_sha256": selection_hash})
    return events


def merge_contiguous(doc):
    mats = lookup(doc)
    merged = []
    def identity(segment):
        if segment.get("common_keyframes"):
            return None
        refs = [mats[r] for r in segment.get("extra_material_refs", [])]
        if any(r.get("type") not in SAFE_REFS or r.get("type") == "audio_fade" for r in refs):
            return None
        if any(r.get("type") == "speed" and (r.get("speed", 1) != 1 or r.get("curve_speed")) for r in refs):
            return None
        if any(segment.get(k) for k in ("animation", "animations", "animation_ids", "keyframe_refs", "keyframe_refs_", "reverse", "is_reverse")):
            return None
        item = copy.deepcopy(segment)
        for key in ("id", "target_timerange", "source_timerange", "extra_material_refs", "desc", "track_render_index"):
            item.pop(key, None)
        item.pop("common_keyframes", None)
        material = mats[segment["material_id"]]
        item.pop("material_id", None)
        if material.get("has_sound_separated"):
            item["volume"] = 0
        else:
            item["volume"] = segment.get("volume", 1)
        normalized = lambda value: {k: v for k, v in value.items() if k != "id"}
        return item, normalized(material), [normalized(r) for r in refs]
    for track in doc["tracks"]:
        if track["type"] not in ("video", "audio"):
            continue
        revised = []
        for segment in track["segments"]:
            previous = revised[-1] if revised else None
            if previous is not None:
                a, b = bounds(previous)
                c, d = bounds(segment)
                left, right = previous.get("source_timerange"), segment.get("source_timerange")
                same = identity(previous)
                can_merge = (left and right and b == c and previous.get("speed", 1) == 1
                             and abs(left["duration"]-(b-a)) <= 4 and abs(right["duration"]-(d-c)) <= 4
                             and abs(left.get("start", 0)+left["duration"]-right.get("start", 0)) <= 4
                             and same is not None and same == identity(segment))
                if can_merge:
                    previous["target_timerange"] = interval(a, d)
                    previous["source_timerange"] = interval(left.get("start", 0), left.get("start", 0)+d-a)
                    merged.append({"kept": previous["id"], "removed": segment["id"], "seam_us": c})
                    continue
            revised.append(segment)
        track["segments"] = revised
    return merged


def current_file_hash(raw):
    if not isinstance(raw, str):
        return None
    path = Path(raw)
    return digest(path) if path.is_absolute() and path.is_file() else None


def music_report(before, doc, plan, cuts, events):
    before_segments = {s["id"]: s for t in before["tracks"] if t["type"] == "audio" for s in t["segments"]}
    after_segments = {s["id"]: s for t in doc["tracks"] if t["type"] == "audio" for s in t["segments"]}
    materials = lookup(doc)
    config = plan.get("music", {})
    identifiers = config.get("segment_ids", [])
    reasons = config.get("energy_reasons", {})
    zones = []
    for identifier in identifiers:
        segment = after_segments.get(identifier)
        if segment is None:
            continue
        original = before_segments[identifier]
        a, b = bounds(segment)
        original_a, original_b = bounds(original)
        source = segment.get("source_timerange") or {}
        material = materials[segment["material_id"]]
        raw = material.get("path")
        automated = bool(original.get("common_keyframes"))
        volume = original.get("volume", 1)
        zones.append({"segment_id": identifier, "origin": "baseline",
                      "input_start_us": original_a, "input_end_us": original_b,
                      "start_us": a, "end_us": b,
                      "source_start_us": source.get("start", 0),
                      "source_duration_us": source.get("duration", b-a),
                      "fader_db": None if automated or volume <= 0 else 20*math.log10(volume),
                      "fader_scope": "automated_or_silent" if automated or volume <= 0 else "baseline_scalar",
                      "path": raw, "sha256": current_file_hash(raw),
                      "energy_reason": reasons.get(identifier, "")})
    for event in events:
        if event["mix_role"] != "bgm":
            continue
        zones.append({"segment_id": event["segment_id"], "origin": "new",
                      "input_start_us": None, "input_end_us": None,
                      "start_us": event["start_us"], "end_us": event["end_us"],
                      "source_start_us": event["source_start_us"],
                      "source_duration_us": event["source_duration_us"],
                      "fader_db": event["fader_db"], "fader_scope": "selected_source_segment",
                      "path": event["path"], "sha256": event["sha256"],
                      "energy_reason": event["purpose"]})
    zones.sort(key=lambda zone: (zone["start_us"], zone["segment_id"]))
    ducks = []
    for row in config.get("ducks", []):
        lo, hi = span(row, "music duck")
        start, end = mapped(lo, cuts), mapped(hi, cuts)
        if start == end:
            continue
        factor = row["factor"]
        ducks.append({"input_start_us": lo, "input_end_us": hi,
                      "start_us": start, "end_us": end,
                      "attack_us": row.get("attack_us", 0), "release_us": row.get("release_us", 0),
                      "factor": factor, "planned_depth_db": -20*math.log10(factor) if factor > 0 else None,
                      "full_attenuation": factor == 0,
                      "segment_ids": row.get("segment_ids", identifiers),
                      "depth_scope": "planned gain ceiling; not a rendered duck-depth measurement"})
    return zones, ducks


def apply(args):
    source = Path(args.input).resolve(strict=True)
    plan_path = Path(args.plan).resolve(strict=True)
    output = Path(args.output).resolve()
    check(not output.exists(), "Output directory must be new")
    check(not source.is_relative_to(output) and not plan_path.is_relative_to(output), "Output cannot contain an input")
    payload = source.read_bytes()
    doc = json.loads(payload)
    before = copy.deepcopy(doc)
    validate_document(doc)
    input_hash = hashlib.sha256(payload).hexdigest()
    plan_payload = plan_path.read_bytes()
    plan_hash = hashlib.sha256(plan_payload).hexdigest()
    plan = json.loads(plan_payload)
    cuts, _, primary = prepare_plan(doc, plan, input_hash)
    seams = {mapped(a, cuts) for a, _ in cuts}
    # Work in memory first; a failed plan cannot alter the input or a live draft.
    ripple(doc, before, plan, cuts)
    picture(doc, before, plan, cuts, primary, seams)
    music_envelopes(doc, plan, cuts)
    merged = merge_contiguous(doc) if plan.get("merge_contiguous", True) else []
    output.mkdir(parents=True)
    events = effects(doc, before, plan, cuts, output)
    summary = validate_document(doc)
    check(doc["id"] == before["id"] and doc.get("canvas_config") == before.get("canvas_config"), "Timeline identity or canvas changed")
    target_track = next(t for t in doc["tracks"] if t["id"] == primary)
    cursor = 0
    for segment in target_track["segments"]:
        a, b = bounds(segment)
        check(a == cursor, f"Primary video has a gap or overlap at {cursor}")
        cursor = b
    check(cursor == doc["duration"], "Primary video does not cover the timeline")
    check(digest(source) == input_hash, "Input changed during application")
    check(digest(plan_path) == plan_hash, "Plan changed during application")
    result = output / "draft_content.json"
    write(result, doc)
    beats = map_beat_events(before, plan, cuts)
    realized = {e["event_id"] for e in events if e.get("event_id")}
    for beat in beats:
        match = next((e for e in events if e.get("event_id") == beat["id"]), None)
        if match:
            beat["sfx_segment_id"] = match["segment_id"]
            beat["realized_attack_us"] = match["target_us"]
    covered = sum(bool(event.get("cue") or event.get("sfx_segment_id") or event.get("duck")) for event in beats)
    verified = sum(event["verified"] for event in beats)
    zones, ducks = music_report(before, doc, plan, cuts, events)
    report = {"input_sha256": input_hash, "plan_sha256": plan_hash, "output_sha256": digest(result),
              "output": str(result), "timeline_id": doc["id"], "old_duration_us": before["duration"],
              "duration_us": doc["duration"], "cuts_us": cuts, "seams_us": sorted(seams), "merged": merged,
              "beat_events": beats, "planned_event_count": len(beats), "covered_event_count": covered,
              "coverage_scope": "covered_event_count is declared intent; realized_sfx_event_count checks actual event_id-linked audio, neither proves listening",
              "realized_sfx_event_count": len(realized), "picture_operations": {k:plan.get(k, []) for k in ("bridges", "flips", "reframes")},
              "verified_event_count": verified, "sfx_count": sum(event["mix_role"] == "sfx" for event in events),
              "bgm_segment_count": sum(event["mix_role"] == "bgm" for event in events),
              "bgm_zone_count": len(zones), "bgm_zones": zones, "music_ducks": ducks,
              "sfx": events, "validation": summary}
    write(output / "report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "validate", "apply"):
        entry = sub.add_parser(command)
        entry.add_argument("--input", required=True, help="Isolated decoded timeline JSON")
        if command == "apply":
            entry.add_argument("--plan", required=True, help="Source-bound schema_version=1 plan JSON")
            entry.add_argument("--output", required=True, help="New output directory outside the live draft")
    args = parser.parse_args()
    try:
        if args.command == "apply":
            result = apply(args)
        else:
            doc = read(Path(args.input).resolve(strict=True))
            result = inspect_document(doc) if args.command == "inspect" else validate_document(doc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (EditError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"{args.command}: {exc}\n")


if __name__ == "__main__":
    main()
