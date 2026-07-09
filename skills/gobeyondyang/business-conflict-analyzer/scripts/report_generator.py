#!/usr/bin/env python3
"""
report_generator.py (Step 3) — Generate impact report in en or zh.

Reads impact_mapper.py JSON from stdin, writes conflict-report.md.
"""

from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

_script_dir = str(Path(__file__).parent.resolve())
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
from lang import Translator

# Force UTF-8 on stdout so Chinese/emoji render correctly on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MERMAID_COLORS = {
    "P0": "#ff4444",
    "P1": "#ffaa00",
    "P2": "#44aa44",
}

LAYER_RANK_KEYWORDS = [
    (0, [".sql", ".ddl"]),
    (1, ["dto", "vo", "request", "response"]),
    (2, ["service", "impl", "mapper", "repository"]),
    (3, ["controller", "api", "rest", "feign", "client"]),
    (4, ["frontend", "vue", "react", "angular", "component", "page"]),
]

def _domain_key(filename: str) -> str:
    """Derive a domain key from the file stem (e.g. 'UserController' → 'user')."""
    stem = Path(filename).stem
    for suffix in ["Controller", "Service", "DTO", "VO", "Feign",
                   "Mapper", "Repository", "Client", "Request", "Response"]:
        if stem.endswith(suffix):
            return stem[:-len(suffix)].lower()
    return stem.lower()

def _layer_rank(path: str) -> int:
    """Assign a layer rank (0-5) for Mermaid graph ordering based on path keywords."""
    lower = path.lower().replace("\\", "/")
    for rank, kws in LAYER_RANK_KEYWORDS:
        if any(kw in lower for kw in kws):
            return rank
    return 5

def _short_name(path: str) -> str:
    """Return the file stem (filename without extension)."""
    return Path(path).stem

def _extract_refs_from_detail(detail: str) -> list[str]:
    """Parse reference count strings like '3 location(s)' or '3 处引用' from detail."""
    # Multi-pattern fallback chain: tries each lang/regex variant.
    patterns = [
        r"(\d+)\s+location",        # EN: "3 location(s)"
        r"(\d+)\s+处",               # ZH: "3 处引用"
    ]
    for pat in patterns:
        m = re.search(pat, detail)
        if m:
            return [f"refs:{m.group(1)}"]
    return []

def _extract_hist_from_detail(detail: str) -> list[str]:
    """Parse historical co-change file references from impact detail."""
    # English: "Historically changed together: file1, file2, file3"
    m = re.search(r"together:\s*(.+?)(?: \||$)", detail)
    if m:
        return [f.strip() for f in m.group(1).split(",") if f.strip()]
    # Chinese: "曾一起变更：file1, file2, file3"
    m = re.search(r"一起变更：(.+?)(?: \||$)", detail)
    if m:
        return [f.strip() for f in m.group(1).split(",") if f.strip()]
    return []

def generate_dependency_graph(manifest: dict, matrix: dict, t: Translator) -> str:
    """Generate Mermaid flowchart showing impact dependency chain."""
    changes = manifest.get("changes", [])
    consumers = matrix.get("consumer_impacts", [])

    node_defs = {}
    edges = []
    seen_domains = {}

    # 1. Change file nodes
    for ch in changes:
        path = ch["file"]
        risk = ch.get("risk_level", "P2")
        short = _short_name(path)
        color = MERMAID_COLORS.get(risk, "#888")
        ico = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(risk, "⚪")
        label = f"{ico} {short}<br/><small>{risk}</small>"
        # Use a content-hash of the full path to avoid collisions when
        # two changed files share the same stem (e.g. dto/Order.java vs api/Order.java)
        _safe_id = re.sub(r'\W', '_', path)
        node_id = _safe_id.strip("_") if len(_safe_id) > 8 else f"n{abs(hash(path)) % 10**8}"
        node_defs[path] = (node_id, label, color, risk)
        domain = _domain_key(path)
        seen_domains.setdefault(domain, []).append(path)

    # 2. Reference nodes
    ref_nodes = {}
    for ci in consumers:
        detail = ci.get("detail", "")
        refs = _extract_refs_from_detail(detail)
        hist = _extract_hist_from_detail(detail)
        for r in refs + hist:
            if r not in ref_nodes:
                rid = f"ref_{len(ref_nodes)}"
                ref_nodes[r] = rid
                if r.startswith("refs:"):
                    count = r.split(":", 1)[1]
                    label = t.t("report.graph.ref_prefix", count=count)
                else:
                    label = f"📄 {r}"
                node_defs[rid] = (rid, label, "#e8e8e8", "ref")

    # 3. Data migration node
    migration = matrix.get("data_migration", {})
    if migration.get("required"):
        mid = "data_migration"
        node_defs[mid] = (mid, t.t("report.graph.data_migration"), "#ff8888", "migrate")

    # 4. Intra-domain edges
    for domain, paths in seen_domains.items():
        if len(paths) < 2:
            continue
        sorted_paths = sorted(paths, key=lambda p: _layer_rank(p))
        for i in range(len(sorted_paths) - 1):
            src = sorted_paths[i]
            dst = sorted_paths[i + 1]
            if src in node_defs and dst in node_defs:
                src_id = node_defs[src][0]
                dst_id = node_defs[dst][0]
                edges.append(f"    {src_id} --> {dst_id}")

    # 5. Reference/history edges
    for ci in consumers:
        path = ci["file"]
        if path not in node_defs:
            continue
        src_id = node_defs[path][0]
        detail = ci.get("detail", "")
        refs = _extract_refs_from_detail(detail)
        hist = _extract_hist_from_detail(detail)
        for r in refs + hist:
            if r in ref_nodes:
                dst_id = ref_nodes[r]
                # Index of this new edge = len(edges) before appending the dash edge
                edge_idx = len(edges)
                edges.append(f"    {src_id} -.-> {dst_id}")
                edges.append(f"    linkStyle {edge_idx} stroke:#888,stroke-dasharray:4")

    # 6. DDL → Data migration edge
    if migration.get("required"):
        for ch in changes:
            if ch.get("extension") in ("sql", "ddl") and ch["file"] in node_defs:
                src_id = node_defs[ch["file"]][0]
                edges.append(f"    {src_id} ==> {mid}")
                break

    # Sort nodes by layer rank — use original _key (filepath), not sanitised nid
    def _node_sort_key(item):
        _key, (nid, label, color, risk) = item
        if risk == "ref":
            return (10, nid)
        if risk == "migrate":
            return (20, nid)
        return (_layer_rank(str(_key) if _key else ""), 0)

    sorted_nodes = sorted(node_defs.items(), key=_node_sort_key)

    lines = ["```mermaid", "flowchart LR"]
    for _key, (nid, label, color, rtype) in sorted_nodes:
        if rtype == "ref":
            lines.append(f"    {nid}[{label}]")
        elif rtype == "migrate":
            lines.append(f"    {nid}({label})")
        else:
            lines.append(f"    {nid}[{label}]:::risk{rtype}")
    lines.extend(edges)

    defined = set()
    for _key, (nid, label, color, rtype) in sorted_nodes:
        if rtype not in ("ref", "migrate") and rtype not in defined:
            lines.append(f"    classDef risk{rtype} fill:{color},color:white,stroke:{color},stroke-width:2px")
            defined.add(rtype)

    lines.append("```")
    return "\n".join(lines)

def _type_icon(change_type: str) -> str:
    """Map change type letter (A/M/D/R/C/T) to a coloured-circle emoji."""
    return {
        "A": "\U0001f7e2 ",
        "M": "\U0001f7e1 ",
        "D": "\U0001f534 ",
        "R": "\U0001f504 ",
        "C": "\U0001f7e2 ",
        "T": "\U0001f4dd ",
    }.get(change_type, "⚪ ")

def generate_report(manifest: dict, matrix: dict, translator: Optional[Translator] = None) -> str:
    """Assemble a language-aware business impact report.

    Args:
        manifest: Diff manifest dict.
        matrix: Impact matrix dict.
        translator: Optional Translator; defaults to auto-detect from matrix.
    """
    # Determine language
    matrix_lang = matrix.get("lang") if isinstance(matrix, dict) else None
    t = translator or Translator(matrix_lang)

    m_summary = manifest.get("summary", "")
    m_changes = manifest.get("changes", [])

    o_impact = matrix.get("overall_impact", "INFO")
    o_consumer = matrix.get("consumer_impacts", [])
    o_migration = matrix.get("data_migration", {})
    o_api = matrix.get("api_compatibility", {})
    o_frontend = matrix.get("frontend_affected", False)
    o_frontend_files = matrix.get("frontend_files", [])

    risk_label, risk_note = t.risk_display(o_impact)

    change_rows = []
    for ch in m_changes:
        filepath = ch.get("file", "")
        symbols = ch.get("symbols", [])
        details = ch.get("details", "")
        risk = ch.get("risk_level", "P2")
        r_icon = risk
        t_icon = _type_icon(ch.get("type", ""))

        # Translate detail
        biz_detail = t.tech_to_business(details)
        # Append risk reason (translated i18n key).
        # Pass ext kwarg to fill {ext} placeholder in diff.reason.file_change template.
        reason_key = ch.get("reason", "")
        if reason_key:
            ext = ch.get("extension", "")
            reason_text = t.t(reason_key, ext=ext)  # safe — extra kwargs ignored by format()
            if t.lang == "zh":
                biz_detail += f"（{reason_text}）"
            else:
                biz_detail += f" ({reason_text})"
        if symbols:
            biz_symbols = [t.translate_symbol(s) for s in symbols[:3]]
            if t.lang == "zh":
                biz_detail += f"（{'；'.join(biz_symbols)}）"
            else:
                biz_detail += f" ({'; '.join(biz_symbols)})"

        # Scope column: use tech_to_business on the file path / layer info
        scope = t.tech_to_business(filepath)
        change_rows.append(f"| {r_icon} | {t_icon} | {scope} | {biz_detail} |")

    change_table = "\n".join(change_rows) if change_rows else (
        f"| {t.t('common.no_change')} | | | |"
    )

    impact_sections = []

    breaking_impacts = [c for c in o_consumer if c.get("impact") == "BREAKING"]
    major_impacts = [c for c in o_consumer if c.get("impact") == "MAJOR"]

    if breaking_impacts:
        rows = "\n".join(
            t.t("report.impact.breaking_item",
                location=t.tech_to_business(c.get("file", "")),
                detail=t.tech_to_business(c.get("detail", "")))
            for c in breaking_impacts
        )
        impact_sections.append(f"### {t.t('report.impact.breaking_title')}\n{rows}")

    if major_impacts:
        rows = "\n".join(
            t.t("report.impact.major_item",
                location=t.tech_to_business(c.get("file", "")),
                detail=t.tech_to_business(c.get("detail", "")))
            for c in major_impacts
        )
        impact_sections.append(f"### {t.t('report.impact.major_title')}\n{rows}")

    if o_migration.get("required"):
        mig_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(o_migration.get("risk", "LOW"), "⚪")
        impact_sections.append(
            f"### {t.t('report.impact.data_migration_title')}\n\n"
            + t.t("report.impact.data_migration_body", icon=mig_icon, detail=o_migration.get("detail", ""))
        )

    if o_api.get("version_required"):
        impact_sections.append(
            f"### {t.t('report.impact.api_version_title')}\n\n"
            + t.t("report.impact.api_version_body", suggestion=o_api.get("suggestion", ""))
        )

    if o_frontend:
        frontend_detail = t.t("report.impact.frontend_body")
        if o_frontend_files:
            max_show = 20
            shown = o_frontend_files[:max_show]
            file_lines = "\n".join(f"   - `{f}`" for f in shown)
            if len(o_frontend_files) > max_show:
                file_lines += f"\n   - *{t.t('report.impact.frontend_and_more', count=len(o_frontend_files) - max_show)}*"
            frontend_detail += f"\n\n{t.t('report.impact.frontend_list_header')}\n{file_lines}"
        impact_sections.append(
            f"### {t.t('report.impact.frontend_title')}\n\n{frontend_detail}"
        )

    impact_block = "\n\n".join(impact_sections) if impact_sections else t.t("report.impact.no_external")

    col_risk = t.t("report.table.risk")
    col_type = t.t("report.table.type")
    col_scope = t.t("report.table.scope")
    col_impact = t.t("report.table.business_impact")

    graph = generate_dependency_graph(manifest, matrix, t)

    analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    report = f"""## {t.t('report.title')}

### {t.t('report.section.summary')}

{t.tech_to_business(m_summary)}

### {t.t('report.section.dependency_graph')}

{graph}

### {t.t('report.section.change_list')}

| {col_risk} | {col_type} | {col_scope} | {col_impact} |
|{':'*3}|{':'*3}|{':'*3}|{':'*3}|
{change_table}

### {t.t('report.section.impact_scope')}

{impact_block}

### {t.t('report.section.risk_advice')}

| {t.t('report.risk.col_header')} | {t.t('report.advice.content')} |
|{':'*3}|{':'*3}|
| **{risk_label}** | {risk_note} |
| **{t.t('report.decision.analysis_time')}** | {analysis_time} |

### {t.t('report.section.decision')}

> {t.t('report.decision.instruction')}

- **{t.t('report.decision.accept')}**
- **{t.t('report.decision.reject')}**
- **{t.t('report.decision.modify')}**

---

{t.t('report.footer')}
"""
    return report

def main():
    raw = sys.stdin.read()
    if not raw:
        t = Translator()
        print(t.t("error.pipe_impact"), file=sys.stderr)
        print(t.t("error.usage_diff"), file=sys.stderr)
        sys.exit(1)

    data = json.loads(raw)

    # Detect language
    data_lang = data.get("lang") if isinstance(data, dict) else None
    t = Translator(data_lang)

    # Parse CLI --lang if provided
    if "--lang" in sys.argv:
        try:
            idx = sys.argv.index("--lang")
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1] in ("en", "zh"):
                t = Translator(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass

    # Determine input type and build matrix
    if "consumer_impacts" in data:
        matrix = data
        manifest = {
            "summary": matrix.get("summary", "Change analysis"),
            "risk_level": "P0" if matrix.get("overall_impact") == "CRITICAL" else "P1",
            "changes": []
        }
        for ci in matrix.get("consumer_impacts", []):
            manifest["changes"].append({
                "file": ci.get("file", ""),
                "extension": ci.get("file", "").split(".")[-1] if "." in ci.get("file", "") else "",
                "symbols": [],
                "details": ci.get("detail", ""),
                "type": "M",
                "risk_level": "P0" if ci.get("impact") == "BREAKING" else (
                    "P1" if ci.get("impact") == "MAJOR" else "P2"),
            })

    elif "changes" in data:
        manifest = data
        try:
            import importlib
            _script_dir = Path(__file__).parent.resolve()
            sys.path.insert(0, str(_script_dir))
            im = importlib.import_module("impact_mapper")
            matrix_obj = im.map_impact(manifest, t)
            matrix = {
                "summary": matrix_obj.summary,
                "consumer_impacts": [
                    {"file": c.file, "impact": c.impact, "detail": c.detail}
                    for c in matrix_obj.consumer_impacts
                ],
                "data_migration": {
                    "required": matrix_obj.data_migration.required,
                    "risk": matrix_obj.data_migration.risk,
                    "detail": matrix_obj.data_migration.detail,
                },
                "api_compatibility": {
                    "version_required": matrix_obj.api_compatibility.version_required,
                    "suggestion": matrix_obj.api_compatibility.suggestion,
                },
                "frontend_affected": matrix_obj.frontend_affected,
                "frontend_files": matrix_obj.frontend_files,
                "overall_impact": matrix_obj.overall_impact,
                "recommendation": matrix_obj.recommendation,
                "lang": t.lang_for_pipe(),
            }
        except Exception as e:
            print(t.t("error.impact_mapper_import", error=str(e)), file=sys.stderr)
            sys.exit(1)
    else:
        print(t.t("error.unknown_format"), file=sys.stderr)
        print(t.t("error.usage_diff"), file=sys.stderr)
        sys.exit(1)

    report = generate_report(manifest, matrix, t)
    print(report)

    # Save to file
    output_path = Path("conflict-report.md")
    output_path.write_text(report, encoding="utf-8")
    report_path = output_path.resolve()
    print(f"\n{t.t('report.saved_to', path=str(report_path))}", file=sys.stderr)

if __name__ == "__main__":
    main()
