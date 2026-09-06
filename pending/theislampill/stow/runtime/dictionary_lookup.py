#!/usr/bin/env python3
"""Cold, sparse lookup for controlled and project terminology.

Lookup reports closed membership and listed-form facts. It does not determine
part of speech, sense, technical-term authority, or controlled-language
conformance. A project authority is read only when the caller explicitly
selects it. Candidate scanning trusts caller-labelled editable segments.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import re
import sys
import unicodedata


DEFAULT_DICTIONARY = (
    Path(__file__).resolve().parents[1] / "rules" / "controlled-dictionary-v1.json.gz"
)
SCAN_BOUNDARY = (
    "Known dictionary matches only; unknown terms, part of speech, sense, "
    "technical-term authority, and final-output custody remain unclassified."
)
PROJECT_BOUNDARY = (
    "Project declarations precede fixed lexical facts. Candidate records and "
    "examples are non-authoritative and are never approvals. Protected segments "
    "are excluded only when caller labels them. Part of speech, technical-category "
    "validity, sense, authority authenticity, and final-output custody remain "
    "contextual or external."
)
DOCUMENT_KEYS = frozenset({
    "schema_version", "normalization", "generated_counts", "records"
})
RECORD_KEYS = frozenset({
    "locator", "headword_raw", "normalized_base_key",
    "part_of_speech", "status", "construction_annotation_raw",
    "approved_forms", "form_parse_state", "meaning_or_alternatives_raw",
})
SEGMENT_KEYS = frozenset({"kind", "text"})
TOKEN_PATTERN = re.compile(r"[\w]+(?:[-'][\w]+)*", re.UNICODE)
COUNT_KEYS = frozenset({
    "records", "approved", "not_approved", "letter_sections", "approved_verbs"
})
PARTS_OF_SPEECH = frozenset({
    "n", "v", "adj", "adv", "pron", "art", "prep", "conj", "prefix",
    "unclassified",
})
FORM_STATES = frozenset({
    "not-applicable", "no-explicit-forms", "listed", "restricted-list",
    "restricted-no-other-forms", "source-separator-anomaly",
})
AUTHORITY_DOCUMENT_KEYS = frozenset({
    "schema_version", "normalization", "authority", "records"
})
AUTHORITY_KEYS = frozenset({"id", "kind", "revision", "source"})
AUTHORITY_RECORD_REQUIRED = frozenset({
    "term", "kind", "status", "preferred_form", "approved_forms",
    "nonpreferred_forms", "meaning_scope", "source_locator", "match",
})
AUTHORITY_RECORD_OPTIONAL = frozenset({"good_example", "bad_example"})
AUTHORITY_EXAMPLE_KEYS = frozenset({"text", "origin"})
AUTHORITY_EXAMPLE_ORIGINS = frozenset({
    "project-authority", "stow-synthetic",
})
AUTHORITY_KINDS = frozenset({
    "user-declaration", "project-glossary", "repository-documentation",
    "subject-field-authority", "configured-external-authority",
})
TERM_KINDS = frozenset({
    "technical-noun", "technical-verb", "abbreviation", "canonical-term",
})
TERM_STATUSES = frozenset({"candidate", "approved", "rejected"})
TERM_MATCHES = frozenset({
    "literal-exact", "literal-casefold", "token-exact", "token-casefold",
})


class DictionaryError(ValueError):
    """Dictionary data or caller input is malformed or unobservable."""


class DuplicateKeyError(ValueError):
    """A JSON object repeats a key."""


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError("duplicate JSON key %r" % key)
        value[key] = item
    return value


def normalize_key(value):
    if not isinstance(value, str):
        raise DictionaryError("lookup value must be a string")
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _validate_document(value):
    if not isinstance(value, dict) or frozenset(value) != DOCUMENT_KEYS:
        raise DictionaryError("dictionary document keys differ")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise DictionaryError("dictionary schema_version must be 1")
    if value["normalization"] != "NFKC-casefold-whitespace":
        raise DictionaryError("dictionary normalization is unsupported")
    records = value["records"]
    if not isinstance(records, list) or not records:
        raise DictionaryError("dictionary records must be a nonempty array")
    locators = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or frozenset(record) != RECORD_KEYS:
            raise DictionaryError("dictionary record %d keys differ" % index)
        if not isinstance(record["locator"], str) or not re.fullmatch(
            r"[A-Z]:[0-9]{4}", record["locator"]
        ):
            raise DictionaryError("dictionary record %d locator differs" % index)
        if record["status"] not in {"approved", "not_approved"}:
            raise DictionaryError("dictionary record %d status differs" % index)
        if record["part_of_speech"] not in PARTS_OF_SPEECH:
            raise DictionaryError("dictionary record %d part of speech differs" % index)
        if record["form_parse_state"] not in FORM_STATES:
            raise DictionaryError("dictionary record %d form state differs" % index)
        string_fields = RECORD_KEYS - {"approved_forms"}
        if any(not isinstance(record[key], str) for key in string_fields):
            raise DictionaryError("dictionary record %d string field differs" % index)
        if not record["headword_raw"] or not record["normalized_base_key"] or not record["meaning_or_alternatives_raw"]:
            raise DictionaryError("dictionary record %d required text differs" % index)
        if record["normalized_base_key"] != normalize_key(record["headword_raw"]):
            raise DictionaryError("dictionary record %d normalized key differs" % index)
        forms = record["approved_forms"]
        if not isinstance(forms, list) or any(
            not isinstance(form, str) or not form for form in forms
        ):
            raise DictionaryError("dictionary record %d forms differ" % index)
        locators.append(record["locator"])
    if len(locators) != len(set(locators)):
        raise DictionaryError("dictionary locators must be unique")
    counts = value["generated_counts"]
    if not isinstance(counts, dict) or frozenset(counts) != COUNT_KEYS:
        raise DictionaryError("dictionary generated counts differ")
    if any(type(counts[key]) is not int or counts[key] < 0 for key in COUNT_KEYS):
        raise DictionaryError("dictionary generated count types differ")
    if counts.get("records") != len(records):
        raise DictionaryError("dictionary record count differs")
    if counts.get("approved") != sum(r["status"] == "approved" for r in records):
        raise DictionaryError("dictionary approved count differs")
    if counts.get("not_approved") != sum(r["status"] == "not_approved" for r in records):
        raise DictionaryError("dictionary not-approved count differs")
    if counts.get("approved_verbs") != sum(
        r["status"] == "approved" and r["part_of_speech"] == "v" for r in records
    ):
        raise DictionaryError("dictionary approved-verb count differs")
    if counts.get("letter_sections") != len({
        locator.split(":", 1)[0] for locator in locators
    }):
        raise DictionaryError("dictionary section count differs")
    return value


def load_dictionary(path=DEFAULT_DICTIONARY):
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            value = json.load(handle, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        raise DictionaryError("dictionary could not be read: %s" % error) from error
    return _validate_document(value)


def _require_nonempty_string(value, label):
    if not isinstance(value, str) or not value:
        raise DictionaryError("%s must be a nonempty string" % label)


def _validate_string_array(value, label):
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise DictionaryError("%s must be an array of nonempty strings" % label)
    normalized = [normalize_key(item) for item in value]
    if len(normalized) != len(set(normalized)):
        raise DictionaryError("%s contains duplicate forms" % label)


def _validate_authority_example(value, label):
    if not isinstance(value, dict) or frozenset(value) != AUTHORITY_EXAMPLE_KEYS:
        raise DictionaryError("%s keys differ" % label)
    _require_nonempty_string(value["text"], label + " text")
    if value["origin"] not in AUTHORITY_EXAMPLE_ORIGINS:
        raise DictionaryError("%s origin differs" % label)


def _authority_record_surfaces(record):
    """Return authoritative scan surfaces and their roles for one record."""
    status = record["status"]
    surfaces = []
    if status == "candidate":
        surfaces.append(("candidate", record["term"]))
    elif status == "approved":
        surfaces.extend(("approved", item) for item in (
            [record["preferred_form"]] + record["approved_forms"]
        ))
        surfaces.extend(
            ("nonpreferred", item) for item in record["nonpreferred_forms"]
        )
    else:
        surfaces.append(("rejected", record["term"]))
        surfaces.extend(
            ("rejected", item) for item in record["nonpreferred_forms"]
        )

    unique = []
    seen = set()
    for role, surface in surfaces:
        key = (role, normalize_key(surface))
        if key not in seen:
            seen.add(key)
            unique.append((role, surface))
    return tuple(unique)


def validate_authority(value):
    """Validate a caller-supplied project terminology authority.

    Validation establishes only the document contract. It cannot authenticate
    the named authority or decide whether a declared meaning fits candidate text.
    """
    if not isinstance(value, dict) or frozenset(value) != AUTHORITY_DOCUMENT_KEYS:
        raise DictionaryError("project authority document keys differ")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise DictionaryError("project authority schema_version must be 1")
    if value["normalization"] != "NFKC-casefold-whitespace":
        raise DictionaryError("project authority normalization is unsupported")

    metadata = value["authority"]
    if not isinstance(metadata, dict) or frozenset(metadata) != AUTHORITY_KEYS:
        raise DictionaryError("project authority metadata keys differ")
    for key in ("id", "revision", "source"):
        _require_nonempty_string(metadata[key], "project authority " + key)
    if metadata["kind"] not in AUTHORITY_KINDS:
        raise DictionaryError("project authority kind differs")

    records = value["records"]
    if not isinstance(records, list) or not records:
        raise DictionaryError("project authority records must be a nonempty array")

    surface_owners = {}
    term_owners = {}
    allowed_keys = AUTHORITY_RECORD_REQUIRED | AUTHORITY_RECORD_OPTIONAL
    for index, record in enumerate(records):
        label = "project authority record %d" % index
        if not isinstance(record, dict):
            raise DictionaryError("%s must be an object" % label)
        keys = frozenset(record)
        if not AUTHORITY_RECORD_REQUIRED <= keys or not keys <= allowed_keys:
            raise DictionaryError("%s keys differ" % label)
        _require_nonempty_string(record["term"], label + " term")
        if record["kind"] not in TERM_KINDS:
            raise DictionaryError("%s kind differs" % label)
        if record["status"] not in TERM_STATUSES:
            raise DictionaryError("%s status differs" % label)
        if record["preferred_form"] is not None:
            _require_nonempty_string(
                record["preferred_form"], label + " preferred_form"
            )
        _validate_string_array(record["approved_forms"], label + " approved_forms")
        _validate_string_array(
            record["nonpreferred_forms"], label + " nonpreferred_forms"
        )
        _require_nonempty_string(record["meaning_scope"], label + " meaning_scope")
        _require_nonempty_string(record["source_locator"], label + " source_locator")
        if record["match"] not in TERM_MATCHES:
            raise DictionaryError("%s match differs" % label)
        for key in AUTHORITY_RECORD_OPTIONAL & keys:
            _validate_authority_example(record[key], label + " " + key)

        if record["status"] == "approved" and (
            record["preferred_form"] is None or not record["approved_forms"]
        ):
            raise DictionaryError(
                "%s approved terms need a preferred form and approved forms" % label
            )
        if record["status"] == "candidate" and (
            record["preferred_form"] is not None
            or record["approved_forms"]
            or record["nonpreferred_forms"]
        ):
            raise DictionaryError(
                "%s candidate terms cannot declare approved or nonpreferred forms"
                % label
            )

        term_key = normalize_key(record["term"])
        if term_key in term_owners:
            raise DictionaryError(
                "project authority term collision between %r and %r"
                % (term_owners[term_key], record["term"])
            )
        if term_key in surface_owners and surface_owners[term_key] != index:
            raise DictionaryError(
                "project authority term-to-surface collision for %r"
                % record["term"]
            )
        term_owners[term_key] = record["term"]

        roles_in_record = {}
        for role, surface in _authority_record_surfaces(record):
            key = normalize_key(surface)
            prior_role = roles_in_record.get(key)
            if prior_role is not None and prior_role != role:
                raise DictionaryError(
                    "%s surface collision between %s and %s for %r"
                    % (label, prior_role, role, surface)
                )
            roles_in_record[key] = role
            owner = surface_owners.get(key)
            if owner is not None and owner != index:
                raise DictionaryError(
                    "project authority surface collision for %r" % surface
                )
            if key in term_owners and term_owners[key] != record["term"]:
                raise DictionaryError(
                    "project authority surface-to-term collision for %r" % surface
                )
            surface_owners[key] = index
    return value


def load_authority(path):
    """Read and validate an explicitly selected authority without mutation."""
    try:
        with Path(path).open(encoding="utf-8") as handle:
            value = json.load(handle, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        raise DictionaryError(
            "project authority could not be read: %s" % error
        ) from error
    return validate_authority(value)


def _surface_equal(first, second, match_kind):
    if match_kind.endswith("-exact"):
        return first == second
    return normalize_key(first) == normalize_key(second)


def lookup_authority(authority, term):
    validate_authority(authority)
    matches = []
    classification = "UNKNOWN"
    for record in authority["records"]:
        match_kind = record["match"]
        if _surface_equal(term, record["term"], match_kind):
            role = record["status"]
        else:
            role = None
            if record["status"] == "approved":
                accepted = [record["preferred_form"]] + record["approved_forms"]
                if any(_surface_equal(term, item, match_kind) for item in accepted):
                    role = "approved"
                elif any(
                    _surface_equal(term, item, match_kind)
                    for item in record["nonpreferred_forms"]
                ):
                    role = "nonpreferred"
            elif record["status"] == "rejected" and any(
                _surface_equal(term, item, match_kind)
                for item in record["nonpreferred_forms"]
            ):
                role = "rejected"
        if role is None:
            continue
        matches.append(record)
        classification = {
            "candidate": "PROJECT_CANDIDATE",
            "approved": "PROJECT_APPROVED_DECLARATION",
            "nonpreferred": "PROJECT_NONPREFERRED",
            "rejected": "PROJECT_REJECTED",
        }[role]
        break
    return {
        "query": term,
        "classification": classification,
        "records": matches,
        "authority": authority["authority"],
        "boundary": PROJECT_BOUNDARY,
    }


def _construction_keys(record):
    annotation = record["construction_annotation_raw"]
    if not annotation:
        return ()
    candidate = annotation.strip().strip("()").strip()
    normalized = normalize_key(candidate)
    base = record["normalized_base_key"]
    if normalized.startswith("or "):
        return (normalize_key(normalized[3:]),)
    if base == normalized or base in normalized.split() or any(
        token.startswith(base) for token in normalized.split() if len(base) >= 4
    ):
        return (normalized,)
    return (normalize_key(base + " " + normalized),)


def _indices(data):
    headwords = {}
    forms = {}
    surfaces = {}
    records = {record["locator"]: record for record in data["records"]}
    for record in data["records"]:
        locator = record["locator"]
        base = record["normalized_base_key"]
        headwords.setdefault(base, []).append(locator)
        surfaces.setdefault(base, []).append(locator)
        for construction in _construction_keys(record):
            surfaces.setdefault(construction, []).append(locator)
        for form in record["approved_forms"]:
            key = normalize_key(form)
            forms.setdefault(key, []).append(locator)
            surfaces.setdefault(key, []).append(locator)
    for table in (headwords, forms, surfaces):
        for key, values in table.items():
            table[key] = tuple(dict.fromkeys(values))
    return records, headwords, forms, surfaces


def _classification(records, headword_match, form_match):
    statuses = {record["status"] for record in records}
    if len(statuses) > 1:
        return "AMBIGUOUS"
    if statuses == {"not_approved"}:
        return "KNOWN_NOT_APPROVED_CANDIDATE"
    if form_match and not headword_match:
        return "FORM_LISTED"
    return "KNOWN_APPROVED_CANDIDATE"


def lookup(data, term, authority=None):
    key = normalize_key(term)
    records, headwords, forms, surfaces = _indices(data)
    locators = surfaces.get(key, ())
    selected = [records[locator] for locator in locators]
    classification = "UNKNOWN"
    if selected:
        classification = _classification(
            selected, key in headwords, key in forms
        )
    result = {
        "query": term,
        "normalized_key": key,
        "classification": classification,
        "records": selected,
        "boundary": SCAN_BOUNDARY,
    }
    if authority is None:
        return result

    project = lookup_authority(authority, term)
    project_classification = project["classification"]
    if project_classification != "UNKNOWN":
        result["classification"] = project_classification
    result.update({
        "project_classification": project_classification,
        "dictionary_classification": classification,
        "project_records": project["records"],
        "project_authority": project["authority"],
        "boundary": PROJECT_BOUNDARY,
    })
    return result


def check_form(data, headword, form):
    base_key = normalize_key(headword)
    form_key = normalize_key(form)
    records, headwords, _forms, _surfaces = _indices(data)
    selected = [
        records[locator] for locator in headwords.get(base_key, ())
        if records[locator]["status"] == "approved"
    ]
    if not selected:
        classification = "UNKNOWN"
    else:
        matches = [
            record for record in selected
            if form_key in {normalize_key(item) for item in record["approved_forms"]}
        ]
        classification = "FORM_LISTED" if matches else "FORM_UNKNOWN"
        if matches:
            selected = matches
    return {
        "headword": headword,
        "form": form,
        "classification": classification,
        "records": selected,
        "boundary": SCAN_BOUNDARY,
    }


def _validate_candidate(candidate):
    if not isinstance(candidate, dict) or frozenset(candidate) != {
        "schema_version", "segments"
    }:
        raise DictionaryError("candidate keys differ")
    if type(candidate["schema_version"]) is not int or candidate["schema_version"] != 1:
        raise DictionaryError("candidate schema_version must be 1")
    if not isinstance(candidate["segments"], list) or not candidate["segments"]:
        raise DictionaryError("candidate segments must be a nonempty array")
    editable = 0
    for index, segment in enumerate(candidate["segments"]):
        if not isinstance(segment, dict) or frozenset(segment) != SEGMENT_KEYS:
            raise DictionaryError("candidate segment %d keys differ" % index)
        if segment["kind"] not in {"editable", "protected"}:
            raise DictionaryError("candidate segment %d kind differs" % index)
        if not isinstance(segment["text"], str):
            raise DictionaryError("candidate segment %d text must be a string" % index)
        editable += segment["kind"] == "editable"
    if not editable:
        raise DictionaryError("candidate has zero editable segments")


def _scan_token_spans(text, surfaces, records):
    """Return word spans, splitting only dictionary-declared prefixes.

    The general word tokenizer deliberately excludes punctuation. A declared
    prefix such as ``re-`` is the exception: it must remain observable both by
    itself and when attached to a following word. Full known surfaces retain
    precedence over prefix splitting.
    """
    prefix_keys = sorted({
        key for key, locators in surfaces.items()
        if key.endswith("-") and any(
            records[locator]["part_of_speech"] == "prefix"
            for locator in locators
        )
    }, key=len, reverse=True)
    spans = []
    for match in TOKEN_PATTERN.finditer(text):
        start, end = match.span()
        if normalize_key(text[start:end]) in surfaces:
            spans.append((start, end))
            continue
        prefix_end = None
        for prefix in prefix_keys:
            candidate_end = start + len(prefix)
            if candidate_end <= len(text) and normalize_key(
                text[start:candidate_end]
            ) == prefix:
                prefix_end = candidate_end
                break
        if prefix_end is None:
            spans.append((start, end))
            continue
        spans.append((start, prefix_end))
        if prefix_end < end:
            spans.append((prefix_end, end))
    return spans


def _scan_fixed(data, candidate):
    _validate_candidate(candidate)
    records, headwords, forms, surfaces = _indices(data)
    max_words = max(len(key.split()) for key in surfaces)
    findings = []
    for segment_index, segment in enumerate(candidate["segments"]):
        if segment["kind"] != "editable":
            continue
        text = segment["text"]
        tokens = _scan_token_spans(text, surfaces, records)
        position = 0
        while position < len(tokens):
            found = None
            consumed = 0
            remaining = len(tokens) - position
            for width in range(min(max_words, remaining), 0, -1):
                start = tokens[position][0]
                end = tokens[position + width - 1][1]
                key = normalize_key(text[start:end])
                locators = surfaces.get(key)
                if not locators:
                    continue
                selected = [records[locator] for locator in locators]
                classification = _classification(
                    selected, key in headwords, key in forms
                )
                if classification in {"KNOWN_NOT_APPROVED_CANDIDATE", "AMBIGUOUS"}:
                    found = {
                        "segment_index": segment_index,
                        "start": start,
                        "end": end,
                        "surface": text[start:end],
                        "normalized_key": key,
                        "classification": classification,
                        "records": selected,
                    }
                    position += width
                    break
                consumed = width
                position += width
                break
            if found:
                findings.append(found)
            elif consumed:
                continue
            else:
                position += 1
    return {
        "status": "REVIEW" if findings else "NO_KNOWN_DICTIONARY_FINDINGS",
        "findings": findings,
        "boundary": SCAN_BOUNDARY,
    }


def _compile_project_surface(surface, match_kind):
    expression = re.escape(surface)
    if match_kind.startswith("token-"):
        if re.match(r"\w", surface[0]):
            expression = r"(?<!\w)" + expression
        if re.match(r"\w", surface[-1]):
            expression = expression + r"(?!\w)"
    flags = 0 if match_kind.endswith("-exact") else re.IGNORECASE
    return re.compile(expression, flags)


def _project_matches(authority, candidate):
    matches = []
    authority_id = authority["authority"]["id"]
    for segment_index, segment in enumerate(candidate["segments"]):
        if segment["kind"] != "editable":
            continue
        for record in authority["records"]:
            for role, surface in _authority_record_surfaces(record):
                pattern = _compile_project_surface(surface, record["match"])
                for found in pattern.finditer(segment["text"]):
                    classification = {
                        "approved": "PROJECT_APPROVED_DECLARATION",
                        "candidate": "PROJECT_CANDIDATE",
                        "nonpreferred": "PROJECT_NONPREFERRED",
                        "rejected": "PROJECT_REJECTED",
                    }[role]
                    matches.append({
                        "segment_index": segment_index,
                        "start": found.start(),
                        "end": found.end(),
                        "surface": found.group(0),
                        "classification": classification,
                        "authority_id": authority_id,
                        "term": record["term"],
                        "kind": record["kind"],
                        "preferred_form": record["preferred_form"],
                        "source_locator": record["source_locator"],
                    })
    matches.sort(key=lambda item: (
        item["segment_index"], item["start"],
        -(item["end"] - item["start"]), item["classification"],
    ))
    selected = []
    for item in matches:
        overlaps = any(
            prior["segment_index"] == item["segment_index"]
            and item["start"] < prior["end"]
            and prior["start"] < item["end"]
            for prior in selected
        )
        if not overlaps:
            selected.append(item)
    return selected


def scan(data, candidate, authority=None):
    """Scan caller-labelled editable text with optional project precedence."""
    fixed = _scan_fixed(data, candidate)
    if authority is None:
        return fixed

    validate_authority(authority)
    project = _project_matches(authority, candidate)
    suppressing = [
        match for match in project
        if match["classification"] != "PROJECT_CANDIDATE"
    ]

    def suppressed(finding):
        return any(
            match["segment_index"] == finding["segment_index"]
            and finding["start"] < match["end"]
            and match["start"] < finding["end"]
            for match in suppressing
        )

    findings = [
        finding for finding in fixed["findings"] if not suppressed(finding)
    ]
    findings.extend(
        match for match in project
        if match["classification"] != "PROJECT_APPROVED_DECLARATION"
    )
    findings.sort(key=lambda item: (
        item["segment_index"], item["start"], item["end"],
        item["classification"],
    ))
    return {
        "status": "REVIEW" if findings else "NO_KNOWN_DICTIONARY_FINDINGS",
        "findings": findings,
        "authority": authority["authority"],
        "boundary": PROJECT_BOUNDARY,
    }


def _load_candidate(path):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        raise DictionaryError("candidate could not be read: %s" % error) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
    parser.add_argument(
        "--authority", type=Path,
        help="explicit caller-selected project terminology authority",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    lookup_parser = subparsers.add_parser("lookup")
    lookup_parser.add_argument("term")
    form_parser = subparsers.add_parser("form")
    form_parser.add_argument("headword")
    form_parser.add_argument("form")
    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--segments", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        data = load_dictionary(args.dictionary)
        authority = load_authority(args.authority) if args.authority else None
        if args.command == "lookup":
            result = lookup(data, args.term, authority=authority)
        elif args.command == "form":
            result = check_form(data, args.headword, args.form)
        else:
            result = scan(
                data, _load_candidate(args.segments), authority=authority
            )
    except DictionaryError as error:
        result = {"status": "UNKNOWN", "error": str(error), "findings": []}
        print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
