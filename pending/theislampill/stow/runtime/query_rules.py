#!/usr/bin/env python3
"""Look up one STOW rule by id (optional acceleration, never a contract path).

    python runtime/query_rules.py STOW-PCT-006

Prints the registry record's key fields, the profiles that include the rule
(through their selector, category prefix, or explicit guidance_rules), the
per-record registry conflicts, the composition-level conflicts that name the
rule, and the anchored corpus section sliced from the rule's corpus module.
Exit 2 with a clear message for an unknown id.

Stdlib only. The registry and conflicts files are YAML, but this helper never
imports a YAML library: it locates each record block by its id line and reads
the few flat fields it needs by hand. profiles.json is plain JSON. This tool
IS shipped: it is inside the runtime allowlist in tools/build_skill.py and
ships in the packaged skill. It is an optional acceleration: the kernel prefers
this helper when execution is available; bounded file reads remain the fallback,
and no route depends exclusively on execution.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)                       # .../skills/stow
REGISTRY = os.path.join(SKILL_DIR, "rules", "registry.yaml")
PROFILES = os.path.join(SKILL_DIR, "rules", "profiles.json")
CONFLICTS = os.path.join(SKILL_DIR, "rules", "conflicts.yaml")

ID_RE = re.compile(r"^  - id:\s*(\S+)\s*$")
CFL_ID_RE = re.compile(r"^  - id:\s*(CFL-\S+)\s*$")
# A ref token inside a flow mapping, e.g. "{kind: rule, ref: STOW-ACT-001}".
REF_RE = re.compile(r"ref:\s*([^\s,}]+)")
# A band token inside a flow mapping, e.g. "{band: contract, ref: result-first}".
BAND_RE = re.compile(r"band:\s*([^\s,}]+)")


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _record_block(text, rid):
    """The lines of the record whose ``id`` equals ``rid``, or None."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        match = ID_RE.match(line)
        if match and match.group(1) == rid:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if ID_RE.match(lines[j]):
            end = j
            break
    return lines[start:end]


def _parse_record(block):
    """Read the flat fields this helper reports from a record block."""
    rec = {"id": None, "title": None, "category": None,
           "predicate": None, "always_on_for_prose": False,
           "applicability": None, "exception": None,
           "enforcement_status": None, "advisory_validators": [],
           "corpus_ref": None, "conflicts": []}
    section = None
    reading_advisory_validators = False
    # A registry conflict entry is a "- rule:" line optionally followed by a
    # "resolution:" line at deeper indent; capture both so the resolution text
    # is reported, not just the counterpart id.
    for line in block:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if indent == 4 and stripped.endswith(":") and ":" in stripped:
            section = stripped[:-1]
            reading_advisory_validators = False
        if line.startswith("  - id:"):
            rec["id"] = _unquote(line.split(":", 1)[1])
            section = None
        elif line.startswith("    title:"):
            rec["title"] = _unquote(line.split(":", 1)[1])
            section = None
        elif line.startswith("    category:"):
            rec["category"] = _unquote(line.split(":", 1)[1])
            section = None
        elif line.startswith("    corpus_ref:"):
            rec["corpus_ref"] = _unquote(line.split(":", 1)[1])
            section = None
        elif line.startswith("      predicate:") and section == "activation":
            rec["predicate"] = _unquote(line.split(":", 1)[1])
        elif line.startswith("      always_on_for_prose:") and section == "activation":
            rec["always_on_for_prose"] = _unquote(line.split(":", 1)[1]).lower() == "true"
        elif line.startswith("      applicability:") and section == "activation":
            rec["applicability"] = _unquote(line.split(":", 1)[1])
        elif line.startswith("      exception:") and section == "activation":
            rec["exception"] = _unquote(line.split(":", 1)[1])
        elif line.startswith("      status:") and section == "enforcement":
            rec["enforcement_status"] = _unquote(line.split(":", 1)[1])
        elif line.startswith("      advisory_validators:") and section == "enforcement":
            reading_advisory_validators = True
        elif line.startswith("        - ") and reading_advisory_validators:
            rec["advisory_validators"].append(_unquote(line.split("-", 1)[1]))
        elif reading_advisory_validators and indent <= 6:
            reading_advisory_validators = False
        elif line.startswith("      - rule:") and section == "conflicts":
            rec["conflicts"].append(
                {"rule": _unquote(line.split(":", 1)[1]), "resolution": None})
        elif line.startswith("        resolution:") and section == "conflicts" \
                and rec["conflicts"]:
            rec["conflicts"][-1]["resolution"] = _unquote(line.split(":", 1)[1])
    return rec


def _profiles_including(rec):
    """Profiles that include the rule, honoring every selector kind.

    A profile includes a rule when any of these holds:
      * its ``includes.selector`` is ``always_on_for_prose`` and the rule's
        activation is always-on for prose;
      * the rule's category prefix (e.g. ``PRC``) is in the profile's
        ``includes.category_prefixes``;
      * the rule id is listed in the profile's ``guidance_rules``.
    """
    rid = rec["id"]
    with open(PROFILES, encoding="utf-8") as handle:
        data = json.load(handle)
    prefix = rid.split("-")[1] if "-" in rid else ""
    hits = []
    for prof in data.get("profiles", []):
        if prof.get("locked"):
            continue
        reasons = []
        includes = prof.get("includes") or {}
        if includes.get("selector") == "always_on_for_prose" and rec["always_on_for_prose"]:
            reasons.append("always_on_for_prose selector")
        if prefix and prefix in (includes.get("category_prefixes") or []):
            reasons.append("category-prefix selector %s" % prefix)
        if rid in (prof.get("guidance_rules") or []):
            reasons.append("guidance_rules")
        if reasons:
            hits.append((prof["id"], ", ".join(reasons)))
    return hits


def _split_cfl_blocks(lines):
    """Split conflicts.yaml lines into per-conflict blocks."""
    blocks = []
    start = None
    for i, line in enumerate(lines):
        if CFL_ID_RE.match(line):
            if start is not None:
                blocks.append(lines[start:i])
            start = i
    if start is not None:
        blocks.append(lines[start:])
    return blocks


def _composition_conflicts(rid):
    """Composition-level conflicts (origin: composition) naming the rule.

    Returns ``[(cfl_id, winner_ref, winner_band, permitted_substitute), ...]``.
    The per-record registry conflicts are reported separately, so only
    composition entries are surfaced here to avoid double-listing the eight
    registry-mirrored pairs.
    """
    if not os.path.isfile(CONFLICTS):
        return []
    lines = open(CONFLICTS, encoding="utf-8").read().splitlines()
    hits = []
    for block in _split_cfl_blocks(lines):
        cid = CFL_ID_RE.match(block[0]).group(1)
        origin = None
        winner_ref = None
        winner_band = None
        permitted = None
        refs = []
        for line in block:
            stripped = line.strip()
            if line.startswith("    origin:"):
                origin = _unquote(line.split(":", 1)[1])
            elif line.startswith("    winner:"):
                bm = BAND_RE.search(line)
                rm = REF_RE.search(line)
                winner_band = bm.group(1) if bm else None
                winner_ref = rm.group(1) if rm else None
            elif line.startswith("    permitted_substitute:"):
                permitted = _unquote(line.split(":", 1)[1])
            elif stripped.startswith("- {") and "ref:" in stripped:
                rm = REF_RE.search(stripped)
                if rm:
                    refs.append(rm.group(1))
        if origin == "composition" and rid in refs:
            hits.append((cid, winner_ref, winner_band, permitted))
    return hits


def _corpus_section(corpus_ref, rid):
    """Slice the module from the ``## <ID>`` heading to the next ``## STOW-``."""
    if not corpus_ref:
        return ""
    module = corpus_ref.split("#", 1)[0]
    path = os.path.join(SKILL_DIR, *module.split("/"))
    if not os.path.isfile(path):
        return ""
    lines = open(path, encoding="utf-8").read().splitlines()
    head = ("## " + rid).lower()
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == head:
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().lower().startswith("## stow-"):
            end = j
            break
    return "\n".join(lines[start:end]).rstrip()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # Corpus sections carry verbatim source wording that may include non-ASCII
    # characters; keep output UTF-8 regardless of the host console codepage.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    if len(argv) != 1:
        print("usage: query_rules.py STOW-XXX-NNN", file=sys.stderr)
        return 2
    rid = argv[0].strip()

    with open(REGISTRY, encoding="utf-8") as handle:
        text = handle.read()
    block = _record_block(text, rid)
    if block is None:
        print("unknown rule id: %s" % rid, file=sys.stderr)
        return 2

    rec = _parse_record(block)
    profiles = _profiles_including(rec)
    composition = _composition_conflicts(rid)
    section = _corpus_section(rec["corpus_ref"], rid)

    print("id: %s" % rec["id"])
    print("title: %s" % (rec["title"] or ""))
    print("category: %s" % (rec["category"] or ""))
    print("activation predicate: %s" % (rec["predicate"] or ""))
    if rec["applicability"]:
        print("applicability: %s" % rec["applicability"])
    if rec["exception"]:
        print("exception: %s" % rec["exception"])
    print("enforcement status: %s" % (rec["enforcement_status"] or ""))
    if rec["advisory_validators"]:
        print("advisory validators: %s" % ", ".join(rec["advisory_validators"]))
    if rec["conflicts"]:
        print("registry conflicts:")
        for conflict in rec["conflicts"]:
            if conflict["resolution"]:
                print("  %s: %s" % (conflict["rule"], conflict["resolution"]))
            else:
                print("  %s" % conflict["rule"])
    else:
        print("registry conflicts: none")
    if composition:
        print("composition conflicts:")
        for cid, winner_ref, winner_band, permitted in composition:
            band = " [band %s]" % winner_band if winner_band else ""
            sub = "; substitute: %s" % permitted if permitted else ""
            print("  %s: winner %s%s%s" % (cid, winner_ref or "?", band, sub))
    else:
        print("composition conflicts: none")
    if profiles:
        print("profiles including this rule:")
        for pid, why in profiles:
            print("  %s (%s)" % (pid, why))
    else:
        print("profiles including this rule: none")
    print("corpus section (%s):" % (rec["corpus_ref"] or "none"))
    print(section if section else "(section not found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
