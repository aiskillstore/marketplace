"""Calculation-owned scopes; row membership stays in memory, never in artifacts."""
from __future__ import annotations

import copy
from typing import Any

import numpy as np
import pandas as pd

from canonical_json import canonical_sha256


SCOPE_VERSION = "analysis-scope-v1"
EVIDENCE_REF_FIELDS = ("evidence_ids", "fact_evidence_ids", "driver_evidence_ids", "segment_evidence_ids")


def record_evidence_ids(record: dict[str, Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for field in EVIDENCE_REF_FIELDS for value in record.get(field, [])))


class ScopeRegistry:
    """Stable rule identities and exact overlapping-set counts from the source index."""

    def __init__(self, source: pd.DataFrame):
        if not source.index.is_unique:
            raise ValueError("scope registry requires a unique internal source index")
        self._index = source.index.copy()
        self._members: dict[str, int] = {"source_rows": (1 << len(source)) - 1}
        self._records: dict[str, dict[str, Any]] = {"source_rows": {
            "scope_id": "source_rows", "kind": "source", "parent_scope_id": None,
            "definition": "加载的源表全部记录，尚未排除日期、重复或质量问题。",
            "included_rows": len(source), "excluded_rows": 0, "filters": [],
            "quality_policy_ids": [], "rules": {"source_row_count": len(source)},
            "population_sha256": self._population_hash((1 << len(source)) - 1),
        }}

    def _population_hash(self, members: int) -> str:
        # Opaque equality proof only; never persist source rows or bitmaps.
        return canonical_sha256({"source_rows": len(self._index), "members": format(members, "x")})

    def register(
        self, included: pd.DataFrame, *, rules: dict[str, Any], definition: str,
        parent_scope_id: str = "source_rows", quality_policy_ids: list[str] | None = None,
    ) -> str:
        if parent_scope_id not in self._records or not included.index.is_unique:
            raise ValueError("scope parent or internal row membership is invalid")
        positions = self._index.get_indexer(included.index)
        if (positions < 0).any():
            raise ValueError("scope rows are outside the loaded source")
        mask = np.zeros(len(self._index), dtype=np.uint8)
        mask[positions] = 1
        members = int.from_bytes(np.packbits(mask, bitorder="little").tobytes(), "little")
        parent_members = self._members[parent_scope_id]
        if members & ~parent_members:
            raise ValueError("scope rows exceed the declared parent scope")
        identity = {"kind": "atomic", "parent_scope_id": parent_scope_id, "rules": rules}
        scope_id = "scope:" + canonical_sha256(identity)[:24]
        record = {
            "scope_id": scope_id, **copy.deepcopy(identity), "definition": definition,
            "included_rows": members.bit_count(),
            "excluded_rows": (parent_members & ~members).bit_count(),
            "filters": copy.deepcopy(rules.get("filters", [])),
            "quality_policy_ids": sorted(set(quality_policy_ids or [])),
            "population_sha256": self._population_hash(members),
        }
        if scope_id in self._members and self._members[scope_id] != members:
            raise ValueError("identical scope rules produced different row membership")
        self._members[scope_id] = members
        self._records.setdefault(scope_id, record)
        return scope_id

    def combine(self, scope_ids: list[str]) -> str:
        members = sorted(set(scope_ids))
        if not members or any(scope_id not in self._records for scope_id in members):
            raise ValueError("scope combination has an unknown or empty member")
        if len(members) == 1:
            return members[0]
        identity = {"kind": "comparison", "member_scope_ids": members, "relationship": "separate_denominators"}
        scope_id = "scope:" + canonical_sha256(identity)[:24]
        union = 0
        for member in members:
            union |= self._members[member]
        self._members[scope_id] = union
        self._records[scope_id] = {
            "scope_id": scope_id, **identity, "parent_scope_id": "source_rows",
            "definition": "分范围比较，不共用分母：" + "；".join(self._records[member]["definition"] for member in members),
            "included_rows": union.bit_count(), "excluded_rows": len(self._index) - union.bit_count(),
            "filters": [], "quality_policy_ids": sorted({policy for member in members for policy in self._records[member]["quality_policy_ids"]}),
            "population_sha256": self._population_hash(union),
        }
        return scope_id

    def bind(self, record: dict[str, Any], evidence_index: dict[str, Any]) -> None:
        refs = record_evidence_ids(record)
        if not refs:
            raise ValueError("cannot bind a business record without evidence scope")
        if any(ref not in evidence_index or not evidence_index[ref].get("scope_id") for ref in refs):
            raise ValueError("business record references evidence without scope")
        record["scope_id"] = self.combine([evidence_index[ref]["scope_id"] for ref in refs])
        record["scope_disclosure"] = self._records[record["scope_id"]]["definition"]

    def record(self, scope_id: str) -> dict[str, Any]:
        return copy.deepcopy(self._records[scope_id])

    def export(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(record) for record in self._records.values()]


def scope_lock_projection(model: dict[str, Any]) -> dict[str, Any]:
    fields = ("scope_id", "scope_disclosure", "scope_bindings", "metric_scope_bindings")
    return {
        "version": model.get("scope_contract_version"), "catalog": model.get("scope_catalog"),
        "decision_context": model.get("decision_context"),
        "decision_proposals": model.get("decision_proposals"),
        "loaded_row_count": model.get("source", {}).get("loaded_row_count"),
        "quality_decisions": model.get("quality_decisions"),
        "evidence": {key: {field: value.get(field) for field in (*fields, "sample_count", "result", "result_hash")}
                     for key, value in model.get("evidence_index", {}).items()},
        "records": {collection: [{field: item.get(field) for field in (*fields, *EVIDENCE_REF_FIELDS)} for item in model.get(collection, [])]
                    for collection in ("insights", "analysis_chapters", "charts", "actions")},
    }


def bind_existing_scope(record: dict, evidence_index: dict, scope_catalog: list) -> None:
    """Bind offline content only to exact combinations prepared during analysis."""
    catalog = {item["scope_id"]: item for item in scope_catalog}
    refs = record_evidence_ids(record)
    if not refs or any(ref not in evidence_index for ref in refs):
        raise ValueError("decision_proposal: cannot bind unknown or empty evidence")
    members = sorted({evidence_index[ref]["scope_id"] for ref in refs})
    identity = {"kind": "comparison", "member_scope_ids": members, "relationship": "separate_denominators"}
    scope_id = members[0] if len(members) == 1 else "scope:" + canonical_sha256(identity)[:24]
    if scope_id not in catalog:
        raise ValueError("decision_proposal: scope combination was not calculated; do not guess its row union")
    record["scope_id"] = scope_id
    record["scope_disclosure"] = catalog[scope_id]["definition"]
