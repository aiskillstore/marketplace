#!/usr/bin/env python3
"""Deterministic structured-output validators for JSON, JSONL, and YAML, plus a
named-schema mode for the meta-code coordination artifacts.

This module is PACKAGED into the shipped skill. It is import-closed: it imports
only the Python standard library, ``ruamel.yaml``, and ``jsonschema``. It never
imports from a repository tool, the repo root, or any sibling module, so it runs
unchanged from inside an extracted artifact where only the artifact is on
``sys.path``.

Each validator returns a :class:`Result`. The command line interface exits 0
when a file is valid and nonzero (with a clear message) when it is not. Warnings
are advisory and never change the exit status.

Two CLI modes:
    ``--format {json,jsonl,yaml} FILE``  structural validation (below).
    ``--schema <id> FILE``               validate an instance against the named
        JSON-Schema-2020-12 document in ``skills/stow/schemas/`` and apply the
        cross-field post-checks that JSON Schema alone cannot express (a
        declared sha256 must match a recomputed hash; a ``status`` of ``done``
        or ``passed`` must carry an evidence pointer; a decision supersession
        must not dangle). A ``.md`` instance is the single fenced yaml/json
        block inside the document; a ``.jsonl`` instance is a stream validated
        per line; an evidence-record FILE may wrap its records as
        ``{records: [...]}`` and validates per record.

JSON contract
    Exactly one JSON value. Rejects a leading BOM (U+FEFF), the non-finite
    literals ``NaN`` / ``Infinity`` / ``-Infinity`` (and any numeric literal that
    overflows to a non-finite float), ``//`` and ``/* */`` comments, trailing
    commas, duplicate object keys, and a wrapping Markdown code fence.

JSONL contract
    One JSON value per non-empty line, parsed independently, with no wrapping
    array. Failures are reported by line number. A single trailing newline (and
    incidental blank lines) are accepted.

YAML contract
    Parsed with ``ruamel.yaml`` ``YAML(typ='safe')`` pinned to version 1.2.
    Custom (non-core) tags, anchors, and aliases are rejected. Ambiguous
    scalars are reported as warnings, not failures. Duplicate keys are detected
    by a node-level walk that compares the RAW SOURCE TOKEN of each scalar key
    (its ``node.value`` plus resolved tag) -- never the resolved Python value --
    so ``1:`` and ``1.0:`` remain distinct keys, ``0x10:`` and ``16:`` remain
    distinct keys, and only the same token appearing twice is a duplicate.
"""

import argparse
import hashlib
import io
import json
import math
import os
import sys

# Exit code and message for a missing third-party runtime dependency. Kept as a
# module-level helper so the error path is unit-testable without uninstalling a
# package. The primary instruction installs the two packages directly, which is
# what a package-only user needs; the requirements-runtime.txt file at the
# repository root is offered as the repository-checkout alternative.
MISSING_DEPENDENCY_EXIT = 3
_RUNTIME_DEP_HINT = (
    "validate.py needs the ruamel.yaml and jsonschema packages. Install them "
    "with: pip install ruamel.yaml jsonschema "
    "(from a repository checkout: pip install -r requirements-runtime.txt)")


def missing_dependency_message(exc):
    """One concise install instruction for a missing runtime dependency."""
    return "%s\n(import error: %s)" % (_RUNTIME_DEP_HINT, exc)


def dependency_exit(exc, stream=None):
    """Print the install instruction and return the stable exit code 3."""
    print(missing_dependency_message(exc), file=stream or sys.stderr)
    return MISSING_DEPENDENCY_EXIT


try:
    import jsonschema
    from ruamel.yaml import YAML
    from ruamel.yaml.nodes import MappingNode, ScalarNode, SequenceNode
    _IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - exercised via dependency_exit
    jsonschema = None
    YAML = None
    MappingNode = ScalarNode = SequenceNode = None
    _IMPORT_ERROR = exc


# --------------------------------------------------------------------------- #
# Result
# --------------------------------------------------------------------------- #

class Result:
    """Outcome of one validation.

    ``ok``       -- True when there are no errors.
    ``errors``   -- human-readable failure messages (nonzero exit).
    ``warnings`` -- advisory notes (never affect the exit status).
    ``data``     -- optional structured detail (e.g. per-line errors, the raw
                    key tokens collected from a YAML root mapping).
    """

    def __init__(self, ok, errors=None, warnings=None, data=None):
        self.ok = bool(ok)
        self.errors = list(errors or [])
        self.warnings = list(warnings or [])
        self.data = dict(data or {})

    def __repr__(self):
        return "Result(ok=%r, errors=%r, warnings=%r)" % (
            self.ok, self.errors, self.warnings)


BOM = "﻿"


# --------------------------------------------------------------------------- #
# Shared JSON strictness hooks
# --------------------------------------------------------------------------- #

def _no_duplicate_pairs(pairs):
    """``object_pairs_hook`` that rejects duplicate keys instead of last-wins."""
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate object key: %r" % (key,))
        seen.add(key)
    return dict(pairs)


def _reject_constant(name):
    """``parse_constant`` hook: NaN / Infinity / -Infinity are not allowed."""
    raise ValueError("non-finite JSON constant not allowed: %s" % name)


def _strict_float(token):
    """``parse_float`` hook: reject any literal that is not a finite number."""
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("non-finite number literal not allowed: %s" % token)
    return value


def _loads_strict(text):
    """``json.loads`` with duplicate-key, non-finite, and comment strictness.

    Standard ``json`` already rejects comments and trailing commas; the hooks add
    duplicate-key and non-finite rejection on top.
    """
    return json.loads(
        text,
        object_pairs_hook=_no_duplicate_pairs,
        parse_constant=_reject_constant,
        parse_float=_strict_float,
    )


# --------------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------------- #

def validate_json(text):
    errors = []

    if text.startswith(BOM):
        errors.append("leading BOM (U+FEFF) is not allowed")
        text = text[len(BOM):]

    if text.lstrip().startswith("```"):
        errors.append("Markdown code fence detected; emit raw JSON, not a fenced block")
        return Result(False, errors)

    try:
        _loads_strict(text)
    except ValueError as exc:  # JSONDecodeError is a ValueError subclass
        errors.append("JSON parse error: %s" % exc)

    return Result(len(errors) == 0, errors)


# --------------------------------------------------------------------------- #
# JSONL
# --------------------------------------------------------------------------- #

def validate_jsonl(text):
    errors = []
    line_errors = []

    if text.startswith(BOM):
        line_errors.append((1, "leading BOM (U+FEFF) is not allowed"))
        text = text[len(BOM):]

    for lineno, raw_line in enumerate(text.split("\n"), start=1):
        line = raw_line.rstrip("\r")  # tolerate CRLF endings
        if line.strip() == "":
            continue  # blank / trailing lines carry no record
        try:
            _loads_strict(line)
        except ValueError as exc:
            line_errors.append((lineno, "JSON parse error: %s" % exc))

    for lineno, message in line_errors:
        errors.append("line %d: %s" % (lineno, message))

    return Result(len(line_errors) == 0, errors, data={"line_errors": line_errors})


# --------------------------------------------------------------------------- #
# YAML
# --------------------------------------------------------------------------- #

# YAML 1.2 core schema tags. Anything else (a custom ``!tag`` or the merge key
# ``<<``) is rejected.
_CORE_TAGS = frozenset([
    "tag:yaml.org,2002:null",
    "tag:yaml.org,2002:bool",
    "tag:yaml.org,2002:int",
    "tag:yaml.org,2002:float",
    "tag:yaml.org,2002:str",
    "tag:yaml.org,2002:seq",
    "tag:yaml.org,2002:map",
])

# Plain scalars a reader is likely to misread (the YAML "Norway problem" and the
# one-letter bool-ish tokens). Advisory only.
_AMBIGUOUS_SCALARS = frozenset(["yes", "no", "on", "off", "y", "n"])


def _new_yaml():
    yaml = YAML(typ="safe")
    yaml.version = (1, 2)
    # We do our OWN token-level duplicate detection below; the built-in
    # resolved-value comparison would wrongly flag 1 vs 1.0 as a duplicate.
    yaml.allow_duplicate_keys = True
    return yaml


def _scalar_key_tokens(mapping_node):
    """Raw source tokens of a mapping's scalar keys, in order."""
    tokens = []
    for key_node, _value_node in mapping_node.value:
        if isinstance(key_node, ScalarNode):
            tokens.append(key_node.value)
    return tokens


def _walk_node(node, errors, warnings, seen_ids):
    """Recurse the representation graph collecting structural violations."""
    node_id = id(node)
    if node_id in seen_ids:
        # The same node object reached twice means an alias resolved to it.
        errors.append("alias/anchor reuse is not allowed (YAML alias detected)")
        return
    seen_ids.add(node_id)

    anchor = getattr(node, "anchor", None)
    # In ruamel the anchor is a (possibly empty) string; a truthy value means an
    # anchor was declared on this node.
    if anchor:
        errors.append("anchors are not allowed (found &%s)" % anchor)

    if node.tag not in _CORE_TAGS:
        errors.append("custom / non-core tag is not allowed: %s" % node.tag)

    if isinstance(node, MappingNode):
        counts = {}
        for key_node, value_node in node.value:
            if isinstance(key_node, ScalarNode):
                token = (key_node.tag, key_node.value)
                counts[token] = counts.get(token, 0) + 1
            _walk_node(key_node, errors, warnings, seen_ids)
            _walk_node(value_node, errors, warnings, seen_ids)
        for (tag, raw), n in counts.items():
            if n > 1:
                errors.append(
                    "duplicate key: same source token %r (tag %s) appears %d times"
                    % (raw, tag, n))
    elif isinstance(node, SequenceNode):
        for child in node.value:
            _walk_node(child, errors, warnings, seen_ids)
    elif isinstance(node, ScalarNode):
        if node.tag == "tag:yaml.org,2002:str" \
                and node.value.strip().lower() in _AMBIGUOUS_SCALARS:
            warnings.append(
                "ambiguous scalar %r resolves to a string under YAML 1.2 but is "
                "easily misread as a boolean" % node.value)


def validate_yaml(text):
    errors = []
    warnings = []
    data = {}

    if text.startswith(BOM):
        errors.append("leading BOM (U+FEFF) is not allowed")
        text = text[len(BOM):]

    yaml = _new_yaml()
    try:
        documents = list(yaml.compose_all(io.StringIO(text)))
    except Exception as exc:  # noqa: BLE001 - surface any parser failure as an error
        errors.append("YAML parse error: %s" % exc)
        return Result(False, errors, warnings, data)

    root_tokens = []
    for index, node in enumerate(documents):
        if node is None:
            continue
        if index == 0 and isinstance(node, MappingNode):
            root_tokens = _scalar_key_tokens(node)
        _walk_node(node, errors, warnings, seen_ids=set())

    data["root_key_tokens"] = root_tokens
    data["document_count"] = len(documents)
    # De-duplicate identical messages (an anchored+aliased node yields two).
    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    return Result(len(errors) == 0, errors, warnings, data)


# --------------------------------------------------------------------------- #
# Named-schema mode (meta-code coordination artifacts)
# --------------------------------------------------------------------------- #

# Sibling directory of this runtime, resolved relative to the module so it works
# unchanged inside the extracted artifact (``.../stow/schemas``).
SCHEMA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "schemas"))

# A schema id is a bare filename stem: letters, digits, and hyphens only. This
# forbids path traversal (no ``/`` ``\`` ``.`` ``..``) when resolving the file.
_SCHEMA_ID_OK = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")


def schema_path(schema_id):
    """Absolute path of the named schema, or None if the id is malformed."""
    if not schema_id or any(ch not in _SCHEMA_ID_OK for ch in schema_id):
        return None
    return os.path.join(SCHEMA_DIR, schema_id + ".schema.json")


def _extract_fenced_block(text):
    """Return (info, body) of the single fenced yaml/json block in a Markdown
    document. String-based on purpose (no regex): the packaged validator keeps
    its import set fixed. A schema opener and closer are exact after surrounding
    whitespace is removed. Unrelated backtick or tilde fences are skipped only
    when they are closed, so a malformed fence cannot expose a later
    schema-like body."""

    def fence_parts(stripped):
        """Return (character, width, info) for a line-leading fence."""
        if not stripped or stripped[0] not in ("`", "~"):
            return None
        character = stripped[0]
        width = 0
        while width < len(stripped) and stripped[width] == character:
            width += 1
        if width < 3:
            return None
        return character, width, stripped[width:]

    def closes_fence(stripped, character, width):
        """Whether a line is an info-free closer at least as wide as opener."""
        return (len(stripped) >= width
                and all(char == character for char in stripped))

    candidates = []
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        lowered = stripped.lower()

        if lowered in ("```yaml", "```json"):
            info = lowered[3:]
            body = []
            index += 1
            while index < len(lines):
                inner = lines[index].strip()
                if inner == "```":
                    candidates.append((info, "\n".join(body)))
                    break
                nested = fence_parts(inner)
                if nested is not None and nested[2].strip():
                    raise ValueError(
                        "info-fence opener inside fenced yaml/json block")
                body.append(lines[index])
                index += 1
            else:
                raise ValueError(
                    "fenced yaml/json block has no exact closing fence")
            index += 1
            continue

        unrelated = fence_parts(stripped)
        if unrelated is not None:
            character, width, _info = unrelated
            index += 1
            while (index < len(lines)
                   and not closes_fence(lines[index].strip(), character, width)):
                index += 1
            if index >= len(lines):
                raise ValueError("unclosed unrelated fenced block")
            index += 1
            continue

        index += 1

    if not candidates:
        raise ValueError(
            "no fenced yaml/json block found in the Markdown document")
    if len(candidates) > 1:
        raise ValueError(
            "expected exactly one fenced yaml/json block, found %d"
            % len(candidates))
    return candidates[0]


def _parse_instance(text, path):
    """Parse a schema instance to plain Python. JSON for ``.json``/``.jsonl``,
    YAML for ``.yaml``/``.yml``, the single fenced yaml/json block for ``.md``,
    else try strict JSON then YAML."""
    def load_yaml_instance(yaml_text):
        """Apply the YAML structural contract before schema deserialization."""
        structural = validate_yaml(yaml_text)
        errors = list(structural.errors)
        document_count = structural.data.get("document_count", 0)
        if document_count != 1:
            errors.append(
                "expected exactly one YAML document, found %d" % document_count)
        if errors:
            raise ValueError(
                "YAML structural validation failed: %s" % "; ".join(errors))
        return _new_yaml().load(io.StringIO(yaml_text))

    lower = (path or "").lower()
    if lower.endswith(".json") or lower.endswith(".jsonl"):
        return _loads_strict(text)
    if lower.endswith(".yaml") or lower.endswith(".yml"):
        return load_yaml_instance(text)
    if lower.endswith(".md") or lower.endswith(".markdown"):
        info, body = _extract_fenced_block(text)
        if info == "json":
            return _loads_strict(body)
        return load_yaml_instance(body)
    try:
        return _loads_strict(text)
    except ValueError:
        return load_yaml_instance(text)


def _iter_mappings(node):
    """Yield every dict found anywhere in a parsed instance (self + descendants)."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _iter_mappings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_mappings(item)


def _has_evidence_pointer(mapping):
    """True when a mapping carries a non-empty evidence pointer."""
    ev = mapping.get("evidence")
    if isinstance(ev, list) and len(ev) > 0:
        return True
    ref = mapping.get("evidence_ref")
    return isinstance(ref, str) and ref.strip() != ""


def check_sha256(instance):
    """POST-CHECK: a declared sha256 must match a recomputed hash.

    Fires on any mapping that carries an ``integrity`` block (``{algo: sha256,
    value}``) alongside an inline string ``payload``: the recomputed
    ``sha256(payload.encode('utf-8'))`` must equal ``integrity.value``. A payload
    referenced by ``payload_ref`` is out of band and not recomputed here.
    """
    errors = []
    for mapping in _iter_mappings(instance):
        integrity = mapping.get("integrity")
        payload = mapping.get("payload")
        if not isinstance(integrity, dict) or integrity.get("algo") != "sha256":
            continue
        if not isinstance(payload, str):
            continue
        declared = integrity.get("value")
        actual = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if declared != actual:
            errors.append(
                "integrity mismatch: declared sha256 %r != recomputed %r"
                % (declared, actual))
    return errors


def check_status_evidence(instance):
    """POST-CHECK: a ``status`` of ``done`` or ``passed`` needs evidence.

    Applies to a state gate marked done or passed and to a returned task packet
    with ``status == "done"``; each must expose a non-empty ``evidence`` array
    or ``evidence_ref``. ``done`` and ``passed`` differ only in what completed
    (work vs a check); both are terminal claims and both need a pointer.
    """
    errors = []
    for mapping in _iter_mappings(instance):
        status = mapping.get("status")
        if status in ("done", "passed") and not _has_evidence_pointer(mapping):
            errors.append(
                "status %r carries no evidence pointer (need non-empty "
                "'evidence' or 'evidence_ref')" % status)
    return errors


def check_supersession(instance):
    """POST-CHECK: a decision supersession must not dangle.

    Every id under a ``decisions[].supersedes`` list and every
    ``decisions[].superseded_by`` must resolve to an existing decision id within
    the same ``decisions`` list.
    """
    errors = []
    for mapping in _iter_mappings(instance):
        decisions = mapping.get("decisions")
        if not isinstance(decisions, list):
            continue
        known = {d["id"] for d in decisions
                 if isinstance(d, dict) and isinstance(d.get("id"), str)}
        for decision in decisions:
            if not isinstance(decision, dict):
                continue
            refs = []
            supersedes = decision.get("supersedes")
            if isinstance(supersedes, list):
                refs.extend(r for r in supersedes if isinstance(r, str))
            superseded_by = decision.get("superseded_by")
            if isinstance(superseded_by, str):
                refs.append(superseded_by)
            for ref in refs:
                if ref not in known:
                    errors.append(
                        "dangling supersession: decision %r references unknown "
                        "decision id %r" % (decision.get("id"), ref))
    return errors


POST_CHECKS = (check_sha256, check_status_evidence, check_supersession)


def validate_schema(schema_id, text, instance_path=None):
    """Validate an instance against a named schema plus the cross-field checks."""
    path = schema_path(schema_id)
    if path is None:
        return Result(False, ["malformed schema id: %r" % (schema_id,)])
    if not os.path.isfile(path):
        available = []
        if os.path.isdir(SCHEMA_DIR):
            available = sorted(
                n[:-len(".schema.json")] for n in os.listdir(SCHEMA_DIR)
                if n.endswith(".schema.json"))
        return Result(False, ["unknown schema id %r (available: %s)"
                              % (schema_id, ", ".join(available) or "none")])

    try:
        with open(path, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, ValueError) as exc:
        return Result(False, ["cannot load schema %r: %s" % (schema_id, exc)])

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.exceptions.SchemaError as exc:
        return Result(False, ["schema %r is not valid draft 2020-12: %s"
                              % (schema_id, exc.message)])

    validator = jsonschema.Draft202012Validator(schema)

    # A .jsonl instance is a STREAM: parse and validate every line
    # independently against the schema (e.g. --schema event stream.jsonl).
    if (instance_path or "").lower().endswith(".jsonl"):
        return _validate_schema_lines(validator, text)

    try:
        instance = _parse_instance(text, instance_path)
    except Exception as exc:  # noqa: BLE001 - surface any parse failure as an error
        return Result(False, ["instance parse error: %s" % exc])

    # Wrapper contract: an evidence-record FILE may carry {records: [...]}.
    # The schema targets one record; the wrapper validates per record, and the
    # post-checks run per record too.
    if (schema_id == "evidence-record" and isinstance(instance, dict)
            and set(instance) == {"records"}
            and isinstance(instance["records"], list)):
        errors = []
        for position, record in enumerate(instance["records"]):
            for err in sorted(validator.iter_errors(record),
                              key=lambda e: list(e.absolute_path)):
                loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
                errors.append("record %d: schema %s: %s"
                              % (position, loc, err.message))
            for check in POST_CHECKS:
                errors.extend("record %d: %s" % (position, e)
                              for e in check(record))
        return Result(len(errors) == 0, errors, data={"instance": instance})

    errors = []
    for err in sorted(validator.iter_errors(instance),
                      key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append("schema %s: %s" % (loc, err.message))

    for check in POST_CHECKS:
        errors.extend(check(instance))

    return Result(len(errors) == 0, errors, data={"instance": instance})


def _validate_schema_lines(validator, text):
    """Validate every non-empty JSONL line as an independent schema instance."""
    errors = []
    count = 0
    for lineno, raw_line in enumerate(text.split("\n"), start=1):
        line = raw_line.rstrip("\r")
        if line.strip() == "":
            continue
        count += 1
        try:
            instance = _loads_strict(line)
        except ValueError as exc:
            errors.append("line %d: JSON parse error: %s" % (lineno, exc))
            continue
        for err in sorted(validator.iter_errors(instance),
                          key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append("line %d: schema %s: %s" % (lineno, loc, err.message))
        for check in POST_CHECKS:
            errors.extend("line %d: %s" % (lineno, e)
                          for e in check(instance))
    if count == 0:
        errors.append("no JSONL records found")
    return Result(len(errors) == 0, errors, data={"line_count": count})


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

VALIDATORS = {
    "json": validate_json,
    "jsonl": validate_jsonl,
    "yaml": validate_yaml,
}


def main(argv=None):
    if _IMPORT_ERROR is not None:
        return dependency_exit(_IMPORT_ERROR)
    parser = argparse.ArgumentParser(
        description="Validate a structured-output file: --format for JSON/JSONL/"
                    "YAML structure, or --schema for a named meta-code schema.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--format", choices=sorted(VALIDATORS),
                      help="the structured format to validate against")
    mode.add_argument("--schema",
                      help="the meta-code schema id in skills/stow/schemas/ "
                           "(e.g. handoff, state, task-packet)")
    parser.add_argument("file", help="path to the file to validate")
    args = parser.parse_args(argv)

    label = args.format if args.format else "schema:%s" % args.schema

    try:
        with open(args.file, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        print("INVALID (%s): cannot read %s: %s" % (label, args.file, exc),
              file=sys.stderr)
        return 2

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print("INVALID (%s): %s is not valid UTF-8: %s" % (label, args.file, exc),
              file=sys.stderr)
        return 2

    if args.schema:
        result = validate_schema(args.schema, text, args.file)
    else:
        result = VALIDATORS[args.format](text)

    for warning in result.warnings:
        print("WARN: %s" % warning)

    if result.ok:
        print("VALID (%s): %s" % (label, args.file))
        return 0

    print("INVALID (%s): %s" % (label, args.file), file=sys.stderr)
    for error in result.errors:
        print("  %s" % error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
