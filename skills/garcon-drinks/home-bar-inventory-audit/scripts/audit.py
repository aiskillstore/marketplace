#!/usr/bin/env python3
"""Verify exhaustive home-bar inventory reconciliation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


LINK_STATES = {"matched", "location_mismatch", "fill_mismatch", "needs_review"}
RECORD_STATES = {"missing", "needs_review"}
OBSERVATION_STATES = {"added", "duplicate", "needs_review"}


class InputError(ValueError):
    """Raised when an audit package is incomplete or inconsistent."""


def _items(raw: Any, field: str) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, list):
        raise InputError(f"{field} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise InputError(f"{field}[{index}] must be an object")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            raise InputError(f"{field}[{index}].id must be non-empty")
        item_id = item_id.strip()
        if item_id in result:
            raise InputError(f"duplicate {field} id: {item_id}")
        result[item_id] = item
    return result


def _dispositions(
    raw: Any,
    field: str,
    allowed: set[str],
    known_ids: set[str],
) -> dict[str, dict[str, str]]:
    if not isinstance(raw, list):
        raise InputError(f"{field} must be a list")
    result: dict[str, dict[str, str]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise InputError(f"{field}[{index}] must be an object")
        item_id = item.get("id")
        status = item.get("status")
        note = item.get("note")
        if item_id not in known_ids:
            raise InputError(f"{field}[{index}] uses an unknown id")
        if item_id in result:
            raise InputError(f"duplicate {field} id: {item_id}")
        if status not in allowed:
            raise InputError(f"{field}[{index}].status is invalid")
        if not isinstance(note, str) or not note.strip():
            raise InputError(f"{field}[{index}].note must be non-empty")
        result[item_id] = {"status": status, "note": note.strip()}
    return result


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    snapshot_date = data.get("snapshot_date")
    if not isinstance(snapshot_date, str) or not snapshot_date.strip():
        raise InputError("snapshot_date must be non-empty")

    records = _items(data.get("records"), "records")
    observations = _items(data.get("observations"), "observations")
    raw_links = data.get("links")
    if not isinstance(raw_links, list):
        raise InputError("links must be a list")

    links: list[dict[str, str]] = []
    linked_records: set[str] = set()
    linked_observations: set[str] = set()
    for index, link in enumerate(raw_links):
        if not isinstance(link, dict):
            raise InputError(f"links[{index}] must be an object")
        record_id = link.get("record_id")
        observation_id = link.get("observation_id")
        status = link.get("status")
        note = link.get("note")
        if record_id not in records:
            raise InputError(f"links[{index}] uses an unknown record_id")
        if observation_id not in observations:
            raise InputError(f"links[{index}] uses an unknown observation_id")
        if record_id in linked_records:
            raise InputError(f"record linked more than once: {record_id}")
        if observation_id in linked_observations:
            raise InputError(f"observation linked more than once: {observation_id}")
        if status not in LINK_STATES:
            raise InputError(f"links[{index}].status is invalid")
        if not isinstance(note, str) or not note.strip():
            raise InputError(f"links[{index}].note must be non-empty")
        linked_records.add(record_id)
        linked_observations.add(observation_id)
        links.append(
            {
                "record_id": record_id,
                "observation_id": observation_id,
                "status": status,
                "note": note.strip(),
            }
        )

    record_dispositions = _dispositions(
        data.get("record_dispositions"),
        "record_dispositions",
        RECORD_STATES,
        set(records),
    )
    observation_dispositions = _dispositions(
        data.get("observation_dispositions"),
        "observation_dispositions",
        OBSERVATION_STATES,
        set(observations),
    )

    overlap_records = linked_records & set(record_dispositions)
    overlap_observations = linked_observations & set(observation_dispositions)
    if overlap_records:
        raise InputError(f"linked record also has a disposition: {sorted(overlap_records)[0]}")
    if overlap_observations:
        raise InputError(
            "linked observation also has a disposition: "
            f"{sorted(overlap_observations)[0]}"
        )

    unaccounted_records = set(records) - linked_records - set(record_dispositions)
    unaccounted_observations = (
        set(observations) - linked_observations - set(observation_dispositions)
    )
    if unaccounted_records:
        raise InputError(f"unaccounted record: {sorted(unaccounted_records)[0]}")
    if unaccounted_observations:
        raise InputError(
            f"unaccounted observation: {sorted(unaccounted_observations)[0]}"
        )

    counts: dict[str, int] = {}
    for link in links:
        counts[link["status"]] = counts.get(link["status"], 0) + 1
    for item in record_dispositions.values():
        key = f"record_{item['status']}"
        counts[key] = counts.get(key, 0) + 1
    for item in observation_dispositions.values():
        key = f"observation_{item['status']}"
        counts[key] = counts.get(key, 0) + 1

    return {
        "snapshot_date": snapshot_date.strip(),
        "record_count": len(records),
        "observation_count": len(observations),
        "links": links,
        "record_dispositions": record_dispositions,
        "observation_dispositions": observation_dispositions,
        "counts": dict(sorted(counts.items())),
        "unaccounted_records": [],
        "unaccounted_observations": [],
        "verification": "EXHAUSTIVE REVIEW PACKAGE",
        "review_state": "READY FOR INVENTORY REVIEW",
        "external_edit": "not performed",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit.py /absolute/path/to/input.json", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise InputError("input must be a JSON object")
        print(json.dumps(calculate(payload), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, InputError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
