#!/usr/bin/env python3
"""Inspect bounded collections for duplicates without changing input.

Usage:
  python3 scripts/dedupe.py inspect --request request.json

Exit codes:
  0  report written to stdout
  1  request or item could not be inspected
  2  command-line usage error

Example:
  python3 scripts/dedupe.py inspect --request examples/list-request.json
"""
import argparse
import json
import sys
from pathlib import Path

from lib.adapters import comparison_key, file_provenance, skill_provenance
from lib.core import find_similarity, key_digest, record_conflicts


def item_provenance(item, request):
    if request["adapter"] == "file":
        return file_provenance(item, request)
    if request["adapter"] == "skill":
        return skill_provenance(item)
    return None


def collect_items(items, request):
    buckets = {}
    provenance = []
    unresolved = []
    for index, item in enumerate(items):
        try:
            key = comparison_key(item, request)
            details = item_provenance(item, request)
            if details is not None:
                provenance.append(details)
        except (OSError, UnicodeError, ValueError) as error:
            unresolved.append({"index": index, "reason": str(error)})
            continue
        buckets.setdefault(key, []).append(index)
    return buckets, provenance, unresolved


def skill_identity_conflicts(provenance):
    by_name = {}
    for index, details in enumerate(provenance):
        if details["name"]:
            by_name.setdefault(details["name"], []).append((index, details["packet_sha256"]))
    conflicts = []
    for name, entries in sorted(by_name.items()):
        if len(entries) > 1 and len({digest for _, digest in entries}) > 1:
            conflicts.append({"name": name, "indices": [index for index, _ in entries],
                              "reason": "same skill name, different packet hashes"})
    return conflicts


def build_groups(items, buckets, request):
    groups = []
    canonical = []
    for key, members in buckets.items():
        canonical.append(members[0])
        if len(members) > 1:
            group = {"canonical_index": members[0], "member_indices": members,
                     "kind": request["mode"], "key_sha256": key_digest(key)}
            if request["adapter"] == "record":
                group["conflict_fields"] = record_conflicts(items, members, request["key_fields"])
            groups.append(group)
    return groups, canonical


def build_report(request):
    request = dict(request)
    request.setdefault("mode", "exact")
    adapter = request.get("adapter")
    items = request.get("items")
    if adapter not in {"list", "text", "record", "url", "file", "skill"}:
        raise ValueError(f"unsupported adapter: {adapter}")
    if not isinstance(items, list):
        raise ValueError("items must be a JSON array")
    buckets, provenance, unresolved = collect_items(items, request)
    groups, canonical = build_groups(items, buckets, request)
    threshold = request.get("similarity_threshold", 1.0)
    candidates = find_similarity(items, adapter, request.get("normalization", {}), threshold)
    duplicate_count = sum(len(members) - 1 for members in buckets.values())
    identity_conflicts = skill_identity_conflicts(provenance) if adapter == "skill" else []
    return {"adapter": adapter, "mode": request["mode"], "mutated": False,
            "source_count": len(items), "canonical_count": len(canonical),
            "duplicate_count": duplicate_count, "unresolved_count": len(unresolved),
            "canonical_indices": canonical, "groups": groups,
            "similarity_candidates": candidates, "unresolved": unresolved, "provenance": provenance,
            "identity_conflicts": identity_conflicts,
            "normalization": request.get("normalization", {}),
            "url_policy": request.get("url_policy", {})}


def load_request(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="write a non-mutating duplicate report")
    inspect_parser.add_argument("--request", required=True, help="path to a JSON request")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = build_report(load_request(args.request))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
