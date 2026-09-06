#!/usr/bin/env python3
"""Validate a closed canonical-term map against caller-labeled segments.

This standard-library-only G2 mechanism scans only segments labeled editable.
It does not classify segments, determine meaning, or establish final-output
custody. The host owns those conditions.
"""

import argparse
import json
import re
import sys


MAP_KEYS = frozenset({"schema_version", "case_sensitive", "entries"})
ENTRY_KEYS = frozenset({"canonical", "forbidden_variants", "match"})
SEGMENTS_KEYS = frozenset({"schema_version", "segments"})
SEGMENT_KEYS = frozenset({"kind", "text"})
MATCH_KINDS = frozenset({"literal", "token"})
SEGMENT_KINDS = frozenset({"editable", "protected"})


class InputError(ValueError):
    """An input is invalid or cannot be observed."""


class DuplicateKeyError(ValueError):
    """A JSON object repeats a key and is therefore ambiguous."""


class ResultParser(argparse.ArgumentParser):
    """Convert argument errors into the CLI's JSON UNKNOWN result."""

    def error(self, message):
        raise InputError("arguments: %s" % message)


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate JSON key %r" % key)
        result[key] = value
    return result


def _load_json(path, label):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError,
            DuplicateKeyError) as exc:
        raise InputError("%s could not be read as unambiguous JSON: %s"
                         % (label, exc)) from exc


def _require_exact_object(value, keys, label):
    if not isinstance(value, dict):
        raise InputError("%s must be an object" % label)
    actual = frozenset(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise InputError("%s keys differ: missing=%r extra=%r"
                         % (label, missing, extra))


def _require_version(value, label):
    if type(value) is not int or value != 1:
        raise InputError("%s schema_version must be 1" % label)


def _term_list(value, label):
    if isinstance(value, str):
        if not value:
            raise InputError("%s must not be empty" % label)
        return (value,)
    if not isinstance(value, list) or not value:
        raise InputError("%s must be a nonempty string or list" % label)
    if any(not isinstance(item, str) or not item for item in value):
        raise InputError("%s list members must be nonempty strings" % label)
    return tuple(value)


def _regex_flags(case_sensitive):
    return 0 if case_sensitive else re.IGNORECASE


def _terms_equivalent(first, second, case_sensitive):
    """Use the scan regex semantics to compare two declared term owners."""
    flags = _regex_flags(case_sensitive)
    first_pattern = re.compile(re.escape(first), flags)
    second_pattern = re.compile(re.escape(second), flags)
    return (first_pattern.fullmatch(second) is not None
            and second_pattern.fullmatch(first) is not None)


def validate_map(value):
    """Validate and normalize a map object for scanning."""
    _require_exact_object(value, MAP_KEYS, "map")
    _require_version(value["schema_version"], "map")
    if type(value["case_sensitive"]) is not bool:
        raise InputError("map case_sensitive must be boolean")
    if not isinstance(value["entries"], list) or not value["entries"]:
        raise InputError("map entries must be a nonempty list")

    case_sensitive = value["case_sensitive"]
    seen = []
    normalized = []
    for index, entry in enumerate(value["entries"]):
        label = "map entry %d" % index
        _require_exact_object(entry, ENTRY_KEYS, label)
        canonical_terms = _term_list(entry["canonical"], label + " canonical")
        variants = _term_list(
            entry["forbidden_variants"], label + " forbidden_variants")
        if (not isinstance(entry["match"], str)
                or entry["match"] not in MATCH_KINDS):
            raise InputError("%s match must be literal or token" % label)

        for role, terms in (("canonical", canonical_terms),
                            ("forbidden variant", variants)):
            for term in terms:
                for prior_role, prior_term in seen:
                    if _terms_equivalent(
                            prior_term, term, case_sensitive):
                        raise InputError(
                            "map term collision between %s %r and %s %r"
                            % (prior_role, prior_term, role, term))
                seen.append((role, term))

        canonical = (entry["canonical"] if isinstance(entry["canonical"], str)
                     else list(canonical_terms))
        normalized.append({
            "canonical": canonical,
            "forbidden_variants": variants,
            "match": entry["match"],
        })

    return case_sensitive, normalized


def validate_segments(value):
    """Validate segments and require at least one editable segment."""
    _require_exact_object(value, SEGMENTS_KEYS, "candidate")
    _require_version(value["schema_version"], "candidate")
    segments = value["segments"]
    if not isinstance(segments, list) or not segments:
        raise InputError("candidate segments must be a nonempty list")

    editable_count = 0
    for index, segment in enumerate(segments):
        label = "candidate segment %d" % index
        _require_exact_object(segment, SEGMENT_KEYS, label)
        if (not isinstance(segment["kind"], str)
                or segment["kind"] not in SEGMENT_KINDS):
            raise InputError("%s kind must be editable or protected" % label)
        if not isinstance(segment["text"], str):
            raise InputError("%s text must be a string" % label)
        if segment["kind"] == "editable":
            editable_count += 1

    if editable_count == 0:
        raise InputError("candidate has zero editable segments")
    return segments


def _compile_variant(variant, match_kind, case_sensitive):
    prefix = r"(?<!\w)" if re.match(r"\w", variant[0]) else ""
    suffix = r"(?!\w)" if re.match(r"\w", variant[-1]) else ""
    expression = re.escape(variant)
    if match_kind == "token":
        expression = prefix + expression + suffix
    return re.compile(expression, _regex_flags(case_sensitive))


def evaluate(mapping, candidate):
    """Return a COMPLIANT or NONCOMPLIANT result for valid input objects."""
    case_sensitive, entries = validate_map(mapping)
    segments = validate_segments(candidate)
    findings = []

    for segment_index, segment in enumerate(segments):
        if segment["kind"] != "editable":
            continue
        text = segment["text"]
        for entry in entries:
            for variant in entry["forbidden_variants"]:
                pattern = _compile_variant(
                    variant, entry["match"], case_sensitive)
                for match in pattern.finditer(text):
                    findings.append({
                        "segment_index": segment_index,
                        "canonical": entry["canonical"],
                        "forbidden_variant": variant,
                        "start": match.start(),
                        "end": match.end(),
                    })

    findings.sort(key=lambda item: (
        item["segment_index"], item["start"], item["end"],
        item["forbidden_variant"],
        json.dumps(item["canonical"], ensure_ascii=True, sort_keys=True)))
    status = "NONCOMPLIANT" if findings else "COMPLIANT"
    return {"status": status, "findings": findings}


def evaluate_files(map_path, segments_path):
    return evaluate(
        _load_json(map_path, "map"),
        _load_json(segments_path, "candidate"),
    )


def _emit(result):
    sys.stdout.write(json.dumps(
        result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    sys.stdout.write("\n")


def main(argv=None):
    parser = ResultParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--map", required=True, dest="map_path")
    parser.add_argument("--segments", required=True, dest="segments_path")
    try:
        args = parser.parse_args(argv)
        result = evaluate_files(args.map_path, args.segments_path)
    except InputError as exc:
        result = {"status": "UNKNOWN", "findings": [], "error": str(exc)}
        _emit(result)
        return 2

    _emit(result)
    return 1 if result["status"] == "NONCOMPLIANT" else 0


if __name__ == "__main__":
    sys.exit(main())
