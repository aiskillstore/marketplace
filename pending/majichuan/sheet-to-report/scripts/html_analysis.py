"""宿主分析用的持久快照。计算不编写故事；HTML 合同不经过 PPT 页型。"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import uuid
from dataclasses import asdict, replace
from pathlib import Path

import pandas as pd

from canonical_json import canonical_sha256, canonical_json
from analysis_engine import file_sha256, prepare_analysis_frame, _aggregate_total, normalize_metric_contracts, required_source_fields
from input_preflight import load_source_table
from semantic_contract import resolve_request_semantic_contract
from transactional_commerce import prepare_transactional_commerce

VERSION = "html-chapters/1"
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(canonical_json(value))


def sealed(value):
    value = copy.deepcopy(value)
    value.pop("sha256", None)
    return {**value, "sha256": canonical_sha256(value)}


def verify(value):
    if sealed(value) != value:
        raise ValueError("快照或内容指纹不匹配")


def _git_provenance():
    """Optional development metadata; never borrow a parent/redirected repository."""
    def unavailable(reason):
        return {"commit": None, "tracked_changes": None,
                "git": {"status": "unavailable", "reason": reason}}

    # A worktree's .git may be a file. An unpacked install has neither form.
    if not (ROOT / ".git").exists():
        return unavailable("not_repository")
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"

    def query(*args):
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, env=env, text=True, encoding="utf-8",
            stderr=subprocess.DEVNULL, timeout=5).rstrip("\r\n")

    try:
        if Path(query("rev-parse", "--show-toplevel")).resolve() != ROOT.resolve():
            return unavailable("root_mismatch")
        commit = query("rev-parse", "--verify", "HEAD")
        changes = query("status", "--porcelain", "--untracked-files=no").splitlines()
    except FileNotFoundError:
        return unavailable("git_not_found")
    except subprocess.TimeoutExpired:
        return unavailable("git_timeout")
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        return unavailable("git_error")
    return {"commit": commit, "tracked_changes": changes, "git": {"status": "available"}}


def skill_manifest():
    # Record the full executable dependency closure, including optional legacy imports.
    paths = [ROOT / "SKILL.md", ROOT / "references/html-analysis.md", ROOT / "references/report-model.md",
             ROOT / "references/chart-spec.md"]
    paths += sorted((ROOT / "scripts").glob("*.py"))
    return {"root": str(ROOT), **_git_provenance(),
        "files": {str(p.relative_to(ROOT)).replace("\\", "/"): file_sha256(p) for p in paths},
        "read_references": ["references/html-analysis.md", "references/report-model.md", "references/chart-spec.md"]}


def load_calculation(request, retained_periods=None):
    frame, meta = load_source_table(request.source_path, request.sheet_name)
    if meta.get("needs_sheet_choice"):
        raise ValueError("需要明确工作表")
    semantic = resolve_request_semantic_contract(request, source_columns=frame.columns,
        metric_dependencies={c["name"]: required_source_fields(c) for c in normalize_metric_contracts(request)})
    if semantic["status"] != "ready":
        raise ValueError("语义合同需要确认")
    request = replace(request, semantic_contract=semantic["contract"])
    transaction = None
    if (semantic["contract"] or {}).get("domain") == "transactional_commerce":
        transaction = prepare_transactional_commerce(frame, semantic["contract"], mode=request.mode)
        if transaction["status"] != "ready":
            raise ValueError("交易口径需要确认")
        prepared = transaction["prepared_frame"]
    else:
        prepared = frame
    work, contracts, warnings, excluded = prepare_analysis_frame(prepared, request, retained_periods=retained_periods)
    return request, frame, work, contracts, warnings, excluded, transaction


def scope(work, request, filters=None):
    denominator = "各指标按已确认聚合合同独立计算"
    if (request.semantic_contract or {}).get("domain") == "transactional_commerce":
        denominator += "；客户仅含可识别 ID"
    return {"source_sha256": file_sha256(request.source_path),
            "population_sha256": canonical_sha256(sorted(int(i) for i in work.index)),
            "rows": len(work), "periods": sorted(work["__period"].unique().tolist()),
            "filters": filters or [], "denominator": denominator}


def table(work, contracts, dimensions):
    rows = []
    groups = work.groupby(dimensions, dropna=False, sort=True) if dimensions else [((), work)]
    for keys, group in groups:
        keys = keys if isinstance(keys, tuple) else (keys,)
        row = {name: str(key) if pd.notna(key) else "未填写" for name, key in zip(dimensions, keys)}
        row.update({c["name"]: _aggregate_total(group, c) for c in contracts})
        row["_population"] = canonical_sha256(sorted(int(i) for i in group.index))
        row["_rows"] = len(group)
        rows.append(row)
    return rows


def add_evidence(snapshot, key, rows, label, record_scope, columns, kind="table"):
    snapshot["evidence"][key] = {"rows": rows, "label": label, "scope": record_scope,
                                 "columns": columns, "kind": kind}


def dimension_label(request, dimension):
    """Use confirmed semantic roles for display; retain original calculation keys."""
    labels = {"geography": "地域", "product": "条目编码", "customer": "客户标识",
              "order": "交易单", "date": "日期"}
    for role, field in (request.semantic_contract or {}).get("field_mappings", {}).items():
        source = field if isinstance(field, str) else field.get("source_field")
        if source == dimension:
            return labels.get(role, dimension)
    return dimension


def analyse(request, output):
    from sheet_to_report import validate_request
    validate_request(request)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("初扫必须使用全新目录；已有运行请恢复快照")
    if request.output_mode != "report":
        raise ValueError("新版 HTML 合同仅允许 report；PPT 尚未支持")
    source_hash = file_sha256(request.source_path)
    request, raw, work, contracts, warnings, excluded, transaction = load_calculation(request)
    payload = asdict(request)
    payload["source_path"] = str(request.source_path.resolve())
    snapshot = {"contract_version": VERSION, "run_id": str(uuid.uuid4()), "version": 0,
        "previous_sha256": None, "source_sha256": source_hash, "request": payload,
        "request_sha256": canonical_sha256(payload), "skill": skill_manifest(),
        "budget": {"rounds": 0, "paths": 0, "questions": {}}, "batches": {}, "executed": {},
        "questions": {}, "decision_context": {}, "evidence": {}, "warnings": warnings,
        "excluded_periods": excluded, "metrics": contracts,
        "capabilities": {"summary_headline_version": "summary-headline/1", "action_target_version": "action-target/1", "dimensions": list(request.dimensions), "metrics": [c["name"] for c in contracts],
                         "operations": ["period_breakdown"]},
        "initial_scan": {"automatic_followups": False,
                         "declared_coverage": ["overview", "trend", "dimension_totals"]}}
    columns = {c["name"]: {"label": c.get("display_name") or c["name"], "unit": c["unit"]} for c in contracts}
    current_scope = scope(work, request)
    add_evidence(snapshot, "overview", table(work, contracts, []), "分析期整体", current_scope, columns)
    add_evidence(snapshot, "trend", table(work, contracts, ["__period"]), "完整周期变化", current_scope,
                 {"__period": {"label": "周期", "unit": ""}, **columns})
    for i, dimension in enumerate(request.dimensions):
        mapping = (request.semantic_contract or {}).get("field_mappings", {})
        customer = mapping.get("customer", {})
        if dimension == (customer if isinstance(customer, str) else customer.get("source_field")):
            continue  # Customer identifiers stay out of the host evidence directory.
        label = dimension_label(request, dimension)
        add_evidence(snapshot, f"dimension_{i}", table(work, contracts, [dimension]), f"{label}全期分布",
                     current_scope, {dimension: {"label": label, "unit": ""}, **columns})
    if transaction:
        from html_transaction_facts import coverage
        coverage(snapshot, raw, work, request, transaction)
    from chart_evidence import enrich
    enrich(snapshot)
    if file_sha256(request.source_path) != source_hash:
        raise ValueError("计算期间来源发生变化")
    snapshot = sealed(snapshot)
    write_new(output / "snapshot-000.json", snapshot)
    return snapshot


def latest(output):
    paths = sorted(Path(output).glob("snapshot-*.json"))
    if not paths:
        raise ValueError("缺少运行快照")
    previous = None
    for index, path in enumerate(paths):
        current = read(path)
        verify(current)
        if current["version"] != index or current["previous_sha256"] != (previous["sha256"] if previous else None):
            raise ValueError("快照链断裂")
        if previous and (current["run_id"] != previous["run_id"] or current["request_sha256"] != previous["request_sha256"]):
            raise ValueError("跨运行/口径混用")
        previous = current
    return previous


def binding(snapshot):
    return {"run_id": snapshot["run_id"], "snapshot_version": snapshot["version"],
            "snapshot_sha256": snapshot["sha256"]}


def check_binding(snapshot, payload):
    if any(payload.get(k) != v for k, v in binding(snapshot).items()):
        raise ValueError("过期或跨运行快照引用")


def validate_path(spec, snapshot):
    required = {"question_id", "decision_use", "gap", "basis_evidence", "operation", "metrics", "dimension"}
    if set(spec) - (required | {"periods", "filters"}) or not required <= set(spec):
        raise ValueError("补查字段不符合白名单")
    if spec["operation"] not in snapshot["capabilities"]["operations"]:
        raise ValueError("实现能力缺口：未知算子")
    if spec["dimension"] not in snapshot["capabilities"]["dimensions"]:
        raise ValueError("维度未确认")
    if not spec["metrics"] or not set(spec["metrics"]) <= set(snapshot["capabilities"]["metrics"]):
        raise ValueError("指标未确认")
    if not spec["basis_evidence"] or not set(spec["basis_evidence"]) <= set(snapshot["evidence"]):
        raise ValueError("新问题缺少初扫依据")
    if not all(isinstance(spec[k], str) and spec[k].strip() for k in ["question_id", "decision_use", "gap"]):
        raise ValueError("问题与缺口不能为空")
    if spec.get("periods") and not set(spec["periods"]) <= set(snapshot["evidence"]["overview"]["scope"]["periods"]):
        raise ValueError("周期超出冻结范围")
    for f in spec.get("filters", []):
        if set(f) != {"field", "values"} or f["field"] not in snapshot["capabilities"]["dimensions"] or not isinstance(f["values"], list):
            raise ValueError("筛选超出白名单")
    # A change of question name, period or filter cannot reset this calculation family's allowance.
    family = canonical_sha256({"operation": spec["operation"], "dimension": spec["dimension"]})
    calculation = {k: spec.get(k) for k in ["operation", "dimension", "metrics", "periods", "filters"]}
    calculation["metrics"] = sorted(set(calculation["metrics"]))
    calculation["periods"] = sorted(set(calculation["periods"] or []))
    calculation["filters"] = sorted(calculation["filters"] or [], key=canonical_json)
    return family, canonical_sha256(calculation)


def followup(output, batch):
    output = Path(output)
    # Single writer; fail on an unfinished reservation rather than silently re-execute a crash.
    lock = output / "followup.lock"
    with lock.open("x", encoding="utf-8") as stream:
        stream.write("同一运行补查正在执行")
    try:
        return _followup(output, batch)
    finally:
        lock.unlink()


def _followup(output, batch):
    from sheet_to_report import ReportRequest
    snapshot = latest(output)
    bid = batch.get("batch_id")
    if not isinstance(bid, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", bid):
        raise ValueError("非法批次标识")
    batch_hash = canonical_sha256(batch)
    if bid in snapshot["batches"]:
        if snapshot["batches"][bid]["input_sha256"] != batch_hash:
            raise ValueError("批次标识复用且内容不同")
        return read(output / snapshot["batches"][bid]["snapshot_file"])
    pending = [p for p in output.glob("reservation-*.json") if p.stem[len("reservation-"):] not in snapshot["batches"]]
    if pending:
        raise ValueError("发现未提交批次预留；禁止改批次重算，先核对恢复记录")
    check_binding(snapshot, batch)
    if skill_manifest()["files"] != snapshot["skill"]["files"]:
        raise ValueError("执行版本改变；不能在旧运行混入新计算")
    if set(batch) != {*binding(snapshot), "batch_id", "paths"} or not isinstance(batch["paths"], list) or len(batch["paths"]) > 12:
        raise ValueError("非法批次合同")
    if snapshot["budget"]["rounds"] >= 4:
        raise ValueError("计算预算停止：四轮已用尽")
    reservation = output / f"reservation-{bid}.json"
    if reservation.exists():
        raise ValueError("发现中断批次预留；停止重算，需核对恢复记录")
    write_new(reservation, {"input_sha256": batch_hash, "previous": snapshot["sha256"]})
    result = copy.deepcopy(snapshot)
    result["version"] += 1
    result["previous_sha256"] = snapshot["sha256"]
    result["budget"]["rounds"] += 1
    trace = []
    calculation = None
    for spec in batch["paths"]:
        entry = {"request": spec}
        trace.append(entry)
        try:
            family, path_hash = validate_path(spec, result)
            old = result["questions"].get(spec["question_id"])
            if old and old["family"] != family:
                raise ValueError("问题身份不能被替换为不同计算族")
        except (ValueError, TypeError, KeyError) as exc:
            entry.update(status="rejected", reason=str(exc))
            continue
        if path_hash in result["executed"]:
            entry.update(status="duplicate", result=result["executed"][path_hash])
            continue
        if result["budget"]["paths"] >= 12 or result["budget"]["questions"].get(family, 0) >= 3:
            entry.update(status="budget_stop", reason="累计路径预算停止")
            continue
        result["budget"]["paths"] += 1
        result["budget"]["questions"][family] = result["budget"]["questions"].get(family, 0) + 1
        try:
            if calculation is None:
                request = ReportRequest(**{**snapshot["request"], "source_path": Path(snapshot["request"]["source_path"])})
                if file_sha256(request.source_path) != snapshot["source_sha256"]:
                    raise ValueError("原表已改变，不能混用当前运行")
                calculation = load_calculation(request, retained_periods=snapshot["evidence"]["overview"]["scope"]["periods"])
                if file_sha256(request.source_path) != snapshot["source_sha256"]:
                    raise ValueError("读取期间来源改变")
                if scope(calculation[2], calculation[0])["population_sha256"] != snapshot["evidence"]["overview"]["scope"]["population_sha256"]:
                    raise ValueError("补查父总体与冻结范围不同")
            request, _, work, contracts, *_ = calculation
            selected = work.copy()
            for f in spec.get("filters", []):
                selected = selected[selected[f["field"]].astype(str).isin([str(v) for v in f["values"]])]
            if spec.get("periods"):
                selected = selected[selected["__period"].isin(spec["periods"])]
            if selected.empty:
                raise ValueError("筛选后无数据")
            metrics = [c for c in contracts if c["name"] in spec["metrics"]]
            rows = table(selected, metrics, ["__period", spec["dimension"]])
            ref = "followup_" + path_hash[:16]
            columns = {"__period": {"label": "周期", "unit": ""}, spec["dimension"]: {"label": dimension_label(request, spec["dimension"]), "unit": ""},
                       **{c["name"]: {"label": c.get("display_name") or c["name"], "unit": c["unit"]} for c in metrics}}
            add_evidence(result, ref, rows, spec["decision_use"], scope(selected, request, spec.get("filters")), columns, "period_breakdown")
            change_ref = None
            compared = sorted(selected["__period"].unique())[-2:]
            if len(compared) == 2:
                baseline, current = compared
                indexed = {(r["__period"], r[spec["dimension"]]): r for r in rows}
                objects = sorted({r[spec["dimension"]] for r in rows})
                changes = []
                change_columns = {"object": {"label": "对象", "unit": ""}, "comparison": {"label": "比较期", "unit": ""}}
                mapping = (request.semantic_contract or {}).get("field_mappings", {})
                display = next((v.get("display_field") for v in mapping.values() if isinstance(v, dict) and v.get("source_field") == spec["dimension"]), None)
                labels = {}
                if display and display in selected:
                    for key, group in selected.groupby(spec["dimension"], sort=False):
                        names = group[display].dropna().astype(str)
                        if len(names):
                            labels[str(key)] = str(names.mode().iloc[0]) + " · " + str(key)
                for obj in objects:
                    row = {"object": labels.get(obj, obj), "comparison": baseline+" → "+current}
                    for metric in metrics:
                        name = metric["name"]
                        absent = 0 if metric["aggregation"] in {"sum", "sum_product", "distinct_count"} else None
                        before = indexed.get((baseline, obj), {}).get(name, absent)
                        after = indexed.get((current, obj), {}).get(name, absent)
                        for suffix, value, label in [("baseline", before, "前期"), ("current", after, "本期"),
                                ("change", after-before if before is not None and after is not None else None, "变动")]:
                            key = name+"_"+suffix
                            row[key] = value
                            change_columns[key] = {"label": (metric.get("display_name") or name)+label, "unit": metric["unit"]}
                            if suffix == "change" and metric["aggregation"] in {"sum", "sum_product"}:
                                change_columns[key]["additive"] = True
                    if display:
                        amount_metric = next((m for m in metrics if m["aggregation"] == "sum_product"), None)
                        quantity_field = (mapping.get("quantity") or {}).get("source_field")
                        qty_metric = next((m for m in metrics if m["aggregation"] == "sum" and (m.get("source_field") or m["name"]) == quantity_field), None)
                        if amount_metric and qty_metric:
                            an, qn = amount_metric["name"], qty_metric["name"]
                            a0, a1, q0, q1 = [row[k] for k in [an+"_baseline", an+"_current", qn+"_baseline", qn+"_current"]]
                            comparable = q0 is not None and q1 is not None and q0 > 0 and q1 > 0
                            row["quantity_component"] = (q1-q0)*(a0/q0) if comparable else 0.0
                            row["unit_value_component"] = q1*(a1/q1-a0/q0) if comparable else 0.0
                            row["unpaired_component"] = 0.0 if comparable else a1-a0
                            for key, label in [("quantity_component", "同条目数量贡献"), ("unit_value_component", "同条目单位净金额贡献"), ("unpaired_component", "新增退出及不可比条目贡献")]:
                                change_columns[key] = {"label": label, "unit": amount_metric["unit"]}
                    changes.append(row)
                change_ref = "change_" + path_hash[:16]
                cs = scope(selected[selected["__period"].isin(compared)], request, spec.get("filters"))
                cs["denominator"] = "同一已确认总体的两期对象并集，包含新增/退出；不存在的加总/计数为零，比率无定义时不伪造。变动为数学贡献，不等同因果。"
                add_evidence(result, change_ref, changes, spec["decision_use"]+"：对象变化并集", cs, change_columns, "decomposition")
                if changes and "quantity_component" in changes[0]:
                    components = [{"component": change_columns[k]["label"], "amount": sum(r[k] for r in changes)} for k in ["quantity_component", "unit_value_component", "unpaired_component"]]
                    cs = {**cs, "denominator": "共同且两期净数量为正的条目：数量贡献=(本期数量−前期数量)×前期单位净金额；单位净金额贡献=本期数量×两期单位净金额差。新增、退出及非正净数量单列；单位净金额含折扣/交易组合影响，不等于挂牌价。包含费用候选，不据此认定纯商品涨价。"}
                    add_evidence(result, "components_"+path_hash[:16], components, "条目变化的数量、单位净金额与新增退出组成", cs,
                                 {"component": {"label": "变动组成", "unit": ""}, "amount": {"label": "数学贡献", "unit": amount_metric["unit"]}}, "decomposition")
                    result["evidence"][change_ref]["scope"] = cs
            qid = spec["question_id"]
            old = result["questions"].get(qid)
            if old and old["family"] != family:
                raise ValueError("问题身份不能被替换为不同计算族")
            extra = "components_"+path_hash[:16]
            refs = list(dict.fromkeys([*(old or {}).get("evidence_ids", []), *spec["basis_evidence"], ref, *([change_ref] if change_ref else []), *([extra] if extra in result["evidence"] else [])]))
            result["questions"][qid] = {"family": family, "decision_use": spec["decision_use"], "gap": spec["gap"], "evidence_ids": refs}
            result["decision_context"][qid] = {"evidence_ids": refs, "scopes": {r: result["evidence"][r]["scope"] for r in refs}}
            result["executed"][path_hash] = {"status": "completed", "evidence_id": ref}
            entry.update(status="completed", evidence_id=ref)
        except Exception as exc:
            result["executed"][path_hash] = {"status": "execution_failed", "reason": str(exc)}
            entry.update(status="execution_failed", reason=str(exc))
    filename = f"snapshot-{result['version']:03}.json"
    result["batches"][bid] = {"input_sha256": batch_hash, "snapshot_file": filename, "trace": trace}
    from chart_evidence import enrich
    enrich(result)
    result = sealed(result)
    write_new(output / filename, result)
    return result


def resolve_text(value, snapshot, allowed):
    """Text may carry figures only through scoped evidence cells, never free numbers."""
    if not isinstance(value, list) or not value:
        raise ValueError("文本必须是非空片段数组")
    parts = []
    for item in value:
        if isinstance(item, str):
            if re.search(r"[0-9０-９]", item):
                raise ValueError("游离数字；请引用证据单元格")
            parts.append(item)
            continue
        if not isinstance(item, dict) or set(item) != {"evidence_id", "row", "column"} or item["evidence_id"] not in allowed:
            raise ValueError("文本引用越界")
        record = snapshot["evidence"][item["evidence_id"]]
        if item["column"] not in record["columns"]:
            raise ValueError("不可引用内部字段")
        if type(item["row"]) is not int or item["row"] < 0 or item["row"] >= len(record["rows"]):
            raise ValueError("单元格行越界")
        cell = record["rows"][item["row"]][item["column"]]
        unit = record["columns"][item["column"]]["unit"]
        parts.append((f"{cell:,.2f}".rstrip("0").rstrip(".") if isinstance(cell, (float, int)) else str(cell)) + unit if cell is not None else "无可计算值")
    text = "".join(parts)
    if re.search(r"\d[\d,.]*(?:人位|人人|件件|单单|英镑英镑|%%)", text):
        raise ValueError("单位或量词重复；引用已自动附带单位")
    return text


def compose(snapshot, proposal):
    from action_target_contract import validate_target
    verify(snapshot)
    check_binding(snapshot, proposal)
    if set(proposal) != {*binding(snapshot), "title", "summary", "chapters", "actions", "sufficiency"}:
        raise ValueError("故事提案字段不符合合同")
    if not proposal["chapters"] or not proposal["sufficiency"]:
        raise ValueError("缺少章节或逐问题充分性判断")
    chapters, ids = [], set()
    chart_views = {}
    for chapter in proposal["chapters"]:
        if set(chapter) - {"nav_title"} != {"id", "role", "claim_type", "title", "body", "meaning", "limitations", "evidence_ids", "scope_bindings", "scope_relation", "charts"}:
            raise ValueError("章节字段不符合合同")
        cid, refs = chapter["id"], chapter["evidence_ids"]
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,50}", cid) or cid in ids or cid in {"summary", "overview", "actions", "method"}:
            raise ValueError("章节标识重复或非法")
        ids.add(cid)
        if chapter["role"] not in {"background", "diagnostic", "supporting"} or chapter["claim_type"] not in {"fact", "structural", "hypothesis"}:
            raise ValueError("内容角色不支持")
        if not refs or not set(refs) <= set(snapshot["evidence"]):
            raise ValueError("章节证据不存在")
        actual_scopes = {r: canonical_sha256(snapshot["evidence"][r]["scope"]) for r in refs}
        if chapter["scope_bindings"] != actual_scopes:
            raise ValueError("章节范围/分母绑定不匹配")
        populations = {snapshot["evidence"][r]["scope"]["population_sha256"] for r in refs}
        if chapter["scope_relation"] not in {"same_population", "separate_scopes"} or (len(populations) > 1 and chapter["scope_relation"] != "separate_scopes"):
            raise ValueError("跨总体必须声明独立范围，不能同口径混算")
        out = {**chapter, **{key: resolve_text(chapter[key], snapshot, refs) for key in ["title", "body", "meaning", "limitations"]}}
        if "nav_title" in chapter:
            out["nav_title"] = resolve_text(chapter["nav_title"], snapshot, refs).strip()
            if not 1 <= len(out["nav_title"]) <= 12:
                raise ValueError("短导航名称须为一至十二字符")
        for chart in chapter["charts"]:
            if chart.get("evidence_id") not in refs:
                raise ValueError("图表引用越界")
            record = snapshot["evidence"][chart["evidence_id"]]
            if 'version' in chart:
                from chart_contract import project_chart
                view = project_chart(chart, record)
                if chart['id'] in chart_views:
                    raise ValueError('图表标识重复')
                chart_views[chart['id']] = {**view, 'chapter_id': cid,
                    'scope_sha256': actual_scopes[chart['evidence_id']],
                    'snapshot_binding': binding(snapshot)}
            else:
                if snapshot.get('capabilities', {}).get('chart_spec_version'):
                    raise ValueError('新运行图表必须显式使用 chart-spec/1；旧合同只用于旧快照兼容')
                from html_chart_views import validate_chart
                validate_chart(chart, record)
            resolve_text(chart["title"], snapshot, refs)
        chapters.append(out)
    summary = []
    for item in proposal["summary"]:
        if set(item) - {'headline'} != {"chapter_ids", "text"} or not item["chapter_ids"] or not set(item["chapter_ids"]) <= ids:
            raise ValueError("摘要章节引用无效")
        refs = {r for c in chapters if c["id"] in item["chapter_ids"] for r in c["evidence_ids"]}
        resolved = {**item, "text": resolve_text(item["text"], snapshot, refs)}
        if 'headline' in item:
            resolved['headline'] = resolve_text(item['headline'], snapshot, refs)
        from summary_contract import validate_headline
        validate_headline(resolved, required=bool(snapshot.get('capabilities', {}).get('summary_headline_version')))
        summary.append(resolved)
    actions = []
    for action in proposal["actions"]:
        if set(action) - {"target_refs", "suggested_role"} != {"chapter_ids", "title", "target", "basis", "steps", "success_signal", "boundary"} or not action["chapter_ids"] or not set(action["chapter_ids"]) <= ids:
            raise ValueError("行动来源无效")
        refs = {r for c in chapters if c["id"] in action["chapter_ids"] for r in c["evidence_ids"]}
        resolved = {**action, **{k: resolve_text(action[k], snapshot, refs) for k in action if k not in {"chapter_ids", "target_refs"}}}
        validate_target(resolved, snapshot, refs, require_binding=bool(snapshot.get('capabilities', {}).get('action_target_version')))
        actions.append(resolved)
    for item in proposal["sufficiency"]:
        if set(item) != {"question", "evidence_ids", "decision", "reason"} or not item["evidence_ids"] or not set(item["evidence_ids"]) <= set(snapshot["evidence"]):
            raise ValueError("充分性依据缺失")
        if item["decision"] not in {"sufficient", "followed_up", "data_limit", "implementation_gap", "budget_stop"} or not item["reason"]:
            raise ValueError("停止依据无效")
    model = {"contract_version": VERSION, "binding": binding(snapshot), "skill": snapshot["skill"],
             "proposal_sha256": canonical_sha256(proposal), "title": resolve_text(proposal["title"], snapshot, snapshot["evidence"]),
             "summary": summary, "chapters": chapters, "actions": actions, "snapshot": snapshot,
             "sufficiency": proposal["sufficiency"], "ppt_supported": False}
    if chart_views:
        model['chart_views'] = chart_views
    return sealed(model)


def finalize(output, story_path):
    from html_chapter_renderer import render
    output = Path(output)
    story = read(story_path)
    snapshot = latest(output)
    if skill_manifest()["files"] != snapshot["skill"]["files"]:
        raise ValueError("执行版本改变；最终化不得误报旧 Skill 版本")
    check_binding(snapshot, story)
    proposal = story["proposal"]
    model = compose(snapshot, proposal)
    if story["model_sha256"] != model["sha256"]:
        raise ValueError("最终内容锁不匹配")
    destination = output / ("final-" + model["sha256"][:16])
    if destination.exists():
        raise ValueError("最终目录已存在，请使用 replay 校验，不覆盖")
    page = render(model)
    destination.mkdir()
    write_new(destination / "report_model.json", model)
    (destination / "report.html").write_text(page, encoding="utf-8")
    write_new(destination / "html_qa.json", {"contract": "passed", "model_sha256": model["sha256"],
              "html_sha256": file_sha256(destination / "report.html"), "visual": "not_verified", "human_review": "pending"})
    return destination


def cli(args):
    if args.analyse_only:
        from sheet_to_report import _request_from_json
        result = analyse(_request_from_json(args.request), args.output)
        return binding(result)
    if args.followup:
        return binding(followup(args.output, read(args.followup)))
    if args.compose_decisions:
        snapshot = latest(args.output)
        proposal = read(args.compose_decisions)
        model = compose(snapshot, proposal)
        path = args.output / ("story-" + model["sha256"][:16] + ".json")
        write_new(path, {**binding(snapshot), "proposal": proposal, "model_sha256": model["sha256"]})
        return {"story_plan": str(path)}
    if args.finalize:
        return {"output": str(finalize(args.output, args.finalize))}
    raise ValueError("正式 HTML 需要宿主先初扫、按需补查、compose，再 finalize")
