#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


CATEGORY_LABELS = {
    "direct_accurate": "直接准确",
    "indirect_accurate": "间接准确",
    "coincidental": "结果巧合",
    "fabricated": "官方查无",
    "misleading": "严重误导",
    "unverified": "无法核验",
    "omitted": "未覆盖",
}

CATEGORY_CLASSES = {
    "direct_accurate": "ok",
    "indirect_accurate": "info",
    "coincidental": "warn",
    "fabricated": "bad",
    "misleading": "bad",
    "unverified": "muted",
    "omitted": "muted",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def escaped(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def compact(value: object) -> str:
    return " ".join(str(value or "").split())


def safe_url(value: object) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def authority_binding_sha256(
    point_id: str,
    platform: str,
    claim: dict,
    verdict: dict,
) -> str:
    return canonical_sha256(
        {
            "pointId": point_id,
            "platform": platform,
            "claim": claim,
            "verdict": verdict,
        }
    )


def validate(verification: dict) -> None:
    if verification.get("schemaVersion") != "fact-check-x/verification@2":
        raise ValueError("verification 必须使用 fact-check-x/verification@2")
    platforms = verification.get("platforms") or []
    points = verification.get("knowledgePoints") or []
    platform_ids = [str(item.get("platform") or "") for item in platforms]
    if not platform_ids or any(not value for value in platform_ids):
        raise ValueError("权威报告缺少平台清单")
    if len(platform_ids) != len(set(platform_ids)):
        raise ValueError("权威报告平台清单存在重复项")
    if not points:
        raise ValueError("权威报告缺少知识点")
    final_answer = verification.get("finalAnswer")
    point_ids = [str(point.get("id") or "") for point in points]
    included_ids = list((final_answer or {}).get("knowledgePointIds") or [])
    excluded_ids = list((final_answer or {}).get("excludedKnowledgePointIds") or [])
    if (
        not isinstance(final_answer, dict)
        or final_answer.get("status") not in {"verified", "partially_verified", "insufficient_evidence"}
        or not compact(final_answer.get("answer"))
        or len(included_ids) != len(set(included_ids))
        or len(excluded_ids) != len(set(excluded_ids))
        or set(included_ids) & set(excluded_ids)
        or set(included_ids + excluded_ids) != set(point_ids)
    ):
        raise ValueError("权威报告最终答案与已纳入、证据不足知识点的绑定不完整")
    for point in points:
        point_id = str(point.get("id") or "")
        authority = point.get("authority") or {}
        claims = authority.get("claims") or {}
        verdicts = authority.get("verdicts") or {}
        if not point_id or authority.get("requestId") != point_id:
            raise ValueError("权威报告知识点与核验结果 ID 不一致")
        if set(claims) != set(platform_ids) or set(verdicts) != set(platform_ids):
            raise ValueError(f"{point_id} 的用户所选平台权威裁决集合不完整")
        if not compact(authority.get("authoritativeFinding")):
            raise ValueError(f"{point_id} 缺少权威结论")


def relevant_excerpt(body: object, context: object, limit: int = 520) -> str:
    text = str(body or "").strip()
    if len(text) <= limit:
        return text
    context_text = re.sub(r"\s+", "", str(context or ""))
    context_numbers = set(re.findall(r"\d+(?:\.\d+)?", context_text))
    context_terms = {
        context_text[index:index + 2]
        for index in range(max(0, len(context_text) - 1))
        if len(context_text[index:index + 2]) == 2
    }
    sentences = [
        match.group(0).strip()
        for match in re.finditer(r"[^\u3002！？；!?;\n]+(?:[\u3002！？；!?;]+|$)", text)
        if match.group(0).strip()
    ]
    if not sentences:
        return text[:limit].rstrip() + "…"

    def score(sentence: str) -> tuple[int, int, int]:
        compact = re.sub(r"\s+", "", sentence)
        number_hits = sum(value in compact for value in context_numbers)
        term_hits = sum(term in compact for term in context_terms)
        return number_hits, term_hits, -len(sentence)

    best = max(range(len(sentences)), key=lambda index: score(sentences[index]))
    selected = sentences[best]
    left = best - 1
    right = best + 1
    while len(selected) < limit and (left >= 0 or right < len(sentences)):
        candidate = ""
        take_left = left >= 0 and (
            right >= len(sentences) or score(sentences[left]) >= score(sentences[right])
        )
        if take_left:
            candidate = sentences[left] + selected
            left -= 1
        else:
            candidate = selected + sentences[right]
            right += 1
        if len(candidate) > limit:
            break
        selected = candidate
    return selected if selected == text else selected.rstrip() + "…"


def evidence_context(authority: dict, evidence_id: str) -> str:
    claims = authority.get("claims") or {}
    verdicts = authority.get("verdicts") or {}
    parts = [str(authority.get("authoritativeFinding") or "")]
    for platform, verdict in verdicts.items():
        if evidence_id in (verdict.get("evidenceIds") or []):
            claim = claims.get(platform) or {}
            parts.extend(
                [
                    str(claim.get("claim") or ""),
                    str(claim.get("answerExcerpt") or ""),
                    str(verdict.get("reason") or ""),
                ]
            )
    return "\n".join(part for part in parts if part)


def render_evidence(authority: dict) -> str:
    items = []
    for evidence in authority.get("evidence") or []:
        raw_evidence_id = str(evidence.get("id") or "")
        evidence_id = escaped(raw_evidence_id)
        title = escaped(evidence.get("title") or evidence.get("url") or evidence_id)
        raw_body = str(evidence.get("body") or "").strip()
        excerpt = relevant_excerpt(
            raw_body, evidence_context(authority, raw_evidence_id)
        )
        url = safe_url(evidence.get("url"))
        heading = (
            f'<a href="{escaped(url)}" target="_blank" rel="noreferrer">{title}</a>'
            if url
            else title
        )
        full_text = (
            '<details class="evidence-full"><summary>查看完整原文</summary>'
            f'<pre>{escaped(raw_body)}</pre></details>'
            if raw_body and excerpt != raw_body
            else ""
        )
        items.append(
            '<article class="evidence">'
            f'<div class="evidence-id">{evidence_id}</div>'
            f"<h4>{heading}</h4>"
            f'<blockquote class="evidence-excerpt">{escaped(excerpt)}</blockquote>'
            f"{full_text}"
            "</article>"
        )
    return "".join(items) or '<p class="empty">未取得可交付的权威证据。</p>'


def render_platform_rows(point: dict, platforms: list[dict]) -> str:
    authority = point.get("authority") or {}
    claims = authority.get("claims") or {}
    verdicts = authority.get("verdicts") or {}
    point_id = str(point.get("id") or "")
    rows = []
    for platform in platforms:
        platform_id = str(platform.get("platform") or "")
        label = platform.get("label") or platform_id
        claim = claims.get(platform_id) or {}
        verdict = verdicts.get(platform_id) or {}
        category = str(verdict.get("category") or "unverified")
        binding = authority_binding_sha256(point_id, platform_id, claim, verdict)
        evidence_ids = "、".join(
            escaped(item) for item in verdict.get("evidenceIds") or []
        ) or "无"
        rows.append(
            "<tr>"
            f'<th scope="row">{escaped(label)}</th>'
            f'<td data-fcx-point="{escaped(point_id)}" '
            f'data-fcx-platform="{escaped(platform_id)}" '
            f'data-fcx-authority-binding-sha256="{binding}">'
            f'<p class="claim">{escaped(claim.get("claim") or "未覆盖")}</p>'
            f'<p class="excerpt">{escaped(claim.get("answerExcerpt"))}</p>'
            "</td>"
            f'<td><span class="verdict {CATEGORY_CLASSES.get(category, "muted")}">'
            f'{escaped(CATEGORY_LABELS.get(category, category))}</span></td>'
            f"<td>{escaped(verdict.get('reason'))}</td>"
            f"<td>{evidence_ids}</td>"
            "</tr>"
        )
    return "".join(rows)


def render_point(point: dict, platforms: list[dict]) -> str:
    authority = point.get("authority") or {}
    mode = (
        "官方材料"
        if authority.get("searchMode") == "dknow_exempt"
        else "追加可信搜索，证实为官方材料"
    )
    point_id = escaped(point.get("id"))
    return (
        f'<section class="point" id="{point_id}">'
        '<div class="point-head">'
        f"<div><span class=\"point-id\">{point_id}</span>"
        f"<h2>{escaped(point.get('description'))}</h2></div>"
        f'<span class="mode">{escaped(mode)}</span>'
        "</div>"
        '<div class="finding">'
        '<span class="finding-label">权威结论</span>'
        f"<p>{escaped(authority.get('authoritativeFinding'))}</p>"
        "</div>"
        '<h3>权威证据</h3>'
        f'<div class="evidence-grid">{render_evidence(authority)}</div>'
        '<h3>各平台裁决</h3>'
        '<div class="table-wrap"><table>'
        "<thead><tr><th>平台</th><th>平台主张与原文</th><th>结论</th>"
        "<th>裁决理由</th><th>权威证据</th></tr></thead>"
        f"<tbody>{render_platform_rows(point, platforms)}</tbody>"
        "</table></div>"
        "</section>"
    )


def render_unverified_boundary(points: list[dict], final_answer: dict) -> str:
    excluded_ids = set(final_answer.get("excludedKnowledgePointIds") or [])
    if not excluded_ids:
        return ""
    items = []
    for point in points:
        if point.get("id") not in excluded_ids:
            continue
        claims = []
        for claim in (point.get("claims") or {}).values():
            value = compact((claim or {}).get("claim"))
            if value and value not in claims:
                claims.append(value)
        claim_text = "；".join(claims) or "本知识点没有可纳入确定答案的平台主张。"
        items.append(
            "<li>"
            f"<h3>{escaped(point.get('id'))} · {escaped(point.get('description'))}</h3>"
            f"<p>{escaped(claim_text)}</p>"
            "</li>"
        )
    if not items:
        return ""
    return (
        '<section class="unverified-boundary" aria-label="无法证实也无法证伪的参考内容">'
        "<h2>以下经权威溯源后，无法证实也无法证伪，仅供参考</h2>"
        "<p>这些内容未纳入上方已核验答案，也不进入准确率分母。</p>"
        f'<ol>{"".join(items)}</ol>'
        "</section>"
    )


def render(verification: dict) -> str:
    validate(verification)
    platforms = verification.get("platforms") or []
    points = verification.get("knowledgePoints") or []
    verdicts = [
        verdict
        for point in points
        for verdict in ((point.get("authority") or {}).get("verdicts") or {}).values()
    ]
    direct_count = sum(
        1 for verdict in verdicts if verdict.get("category") == "direct_accurate"
    )
    evidence_gap_count = len(verification.get("evidenceGaps") or [])
    verification_sha = canonical_sha256(verification)
    point_sections = "".join(render_point(point, platforms) for point in points)
    final_answer = verification.get("finalAnswer") or {}
    final_status = {
        "verified": "权威核验完成",
        "partially_verified": "已形成有据结论，证据不足项已排除",
        "insufficient_evidence": "证据不足，未形成确定答案",
    }.get(final_answer.get("status"), "权威核验完成")
    final_answer_title = "完美答案（已核验，可权威溯源）"
    question = str(verification.get("question") or "").strip()
    report_title = f"全知晓“完美答案”（问题：{question}）"
    unverified_boundary = render_unverified_boundary(points, final_answer)
    final_report_nav = '<a href="04-final-report.html">各方答案测评报告</a>'
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="fact-check-x-authority-report" content="1">
  <meta name="fact-check-x-verification-sha256" content="{verification_sha}">
  <title>{escaped(report_title)}</title>
  <style>
    * {{ box-sizing: border-box; }}
    html {{ background: #eef1f5; color: #172033; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; letter-spacing: 0; }}
    a {{ color: #1458a6; overflow-wrap: anywhere; }}
    .top {{ background: #172033; color: #fff; padding: 28px max(24px, calc((100vw - 1440px) / 2 + 24px)); }}
    .eyebrow {{ color: #9bd4ca; font-size: 13px; font-weight: 700; margin: 0 0 8px; }}
    h1 {{ font-size: 30px; line-height: 1.25; margin: 0; }}
    .question {{ color: #d8e0ec; font-size: 16px; line-height: 1.6; margin: 12px 0 0; max-width: 940px; }}
    .nav {{ background: #fff; border-bottom: 1px solid #d7dde7; padding: 11px max(24px, calc((100vw - 1440px) / 2 + 24px)); }}
    .nav a {{ font-size: 14px; font-weight: 650; margin-right: 22px; text-decoration: none; }}
    .nav-pending {{ color: #7a5200; font-size: 14px; font-weight: 650; }}
    main {{ margin: 0 auto; max-width: 1440px; padding: 24px; }}
    .metrics {{ display: grid; gap: 12px; grid-template-columns: repeat(5, minmax(0, 1fr)); margin-bottom: 22px; }}
    .metric {{ background: #fff; border: 1px solid #d7dde7; border-radius: 6px; padding: 16px; }}
    .metric b {{ display: block; font-size: 24px; }}
    .metric span {{ color: #637083; display: block; font-size: 13px; margin-top: 5px; }}
    .final-answer {{ background: #fff; border: 1px solid #9dcfbe; border-left: 6px solid #148266; border-radius: 6px; box-shadow: 0 12px 30px rgba(23, 32, 51, .08); margin-bottom: 22px; padding: 24px; }}
    .final-answer-head {{ align-items: center; display: flex; gap: 12px; justify-content: space-between; }}
    .final-answer h2 {{ font-size: 20px; margin: 0; }}
    .final-kicker {{ color: #17624f; font-size: 12px; font-weight: 800; margin: 0 0 6px; }}
    .final-status {{ background: #e7f5f1; border: 1px solid #a8d8ca; border-radius: 4px; color: #17624f; font-size: 12px; font-weight: 750; padding: 4px 7px; }}
    .final-answer-body {{ font-size: 17px; font-weight: 650; line-height: 1.75; margin: 14px 0 0; white-space: pre-wrap; }}
    .point {{ background: #fff; border: 1px solid #d7dde7; border-radius: 6px; margin-bottom: 20px; padding: 22px; }}
    .point-head {{ align-items: flex-start; display: flex; gap: 16px; justify-content: space-between; }}
    .point-head h2 {{ display: inline; font-size: 19px; line-height: 1.45; margin: 0 0 0 8px; }}
    .point-id {{ background: #172033; border-radius: 4px; color: #fff; display: inline-block; font-size: 12px; font-weight: 750; padding: 4px 7px; }}
    .mode {{ background: #e7f5f1; border: 1px solid #a8d8ca; border-radius: 4px; color: #17624f; flex: 0 0 auto; font-size: 12px; font-weight: 700; padding: 6px 8px; }}
    .finding {{ border-left: 4px solid #148266; margin: 18px 0 22px; padding: 4px 0 4px 14px; }}
    .finding-label {{ color: #17624f; font-size: 12px; font-weight: 750; }}
    .finding p {{ font-size: 17px; font-weight: 650; line-height: 1.6; margin: 5px 0 0; }}
    h3 {{ font-size: 15px; margin: 22px 0 10px; }}
    .evidence-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .evidence {{ border: 1px solid #d7dde7; border-radius: 5px; min-width: 0; padding: 14px; }}
    .evidence-id {{ color: #637083; font-size: 12px; font-weight: 750; }}
    .evidence h4 {{ font-size: 14px; line-height: 1.45; margin: 5px 0 8px; }}
    blockquote {{ background: #f6f8fb; border-left: 3px solid #aab5c4; color: #344054; line-height: 1.55; margin: 0; overflow-wrap: anywhere; padding: 9px 11px; word-break: break-word; }}
    .evidence-full {{ margin-top: 10px; }}
    .evidence-full summary {{ color: #1458a6; cursor: pointer; font-size: 13px; font-weight: 650; }}
    .evidence-full pre {{ background: #f6f8fb; border: 1px solid #d7dde7; border-radius: 4px; color: #344054; font: inherit; line-height: 1.55; margin: 8px 0 0; max-height: 420px; overflow: auto; padding: 10px; white-space: pre-wrap; }}
    .table-wrap {{ overflow-x: auto; width: 100%; }}
    table {{ border-collapse: collapse; min-width: 900px; table-layout: fixed; width: 100%; }}
    th, td {{ border: 1px solid #d7dde7; font-size: 13px; line-height: 1.5; padding: 10px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    thead th {{ background: #f0f3f7; color: #344054; }}
    th:first-child {{ width: 10%; }}
    th:nth-child(2) {{ width: 28%; }}
    th:nth-child(3) {{ width: 12%; }}
    th:nth-child(4) {{ width: 36%; }}
    th:nth-child(5) {{ width: 14%; }}
    .claim {{ font-weight: 700; margin: 0 0 6px; }}
    .excerpt {{ color: #637083; margin: 0; }}
    .verdict {{ border-radius: 4px; display: inline-block; font-size: 12px; font-weight: 750; padding: 4px 7px; }}
    .verdict.ok {{ background: #dff3eb; color: #17624f; }}
    .verdict.info {{ background: #e3eefb; color: #174f8a; }}
    .verdict.warn {{ background: #fff0c7; color: #7a5200; }}
    .verdict.bad {{ background: #fde4e2; color: #9b2c25; }}
    .verdict.muted {{ background: #e9edf2; color: #526071; }}
    .unverified-boundary {{ background: #fffaf0; border: 1px solid #e7c980; border-left: 5px solid #b7791f; border-radius: 6px; margin: 0 0 22px; padding: 20px 24px; }}
    .unverified-boundary h2 {{ color: #7a5200; font-size: 18px; margin: 0; }}
    .unverified-boundary > p {{ color: #6c5a32; margin: 6px 0 12px; }}
    .unverified-boundary ol {{ margin: 0; padding-left: 22px; }}
    .unverified-boundary li {{ border-top: 1px solid #ead9af; padding: 10px 0; }}
    .unverified-boundary li h3 {{ margin: 0 0 4px; }}
    .unverified-boundary li p {{ margin: 0; }}
    .empty {{ color: #637083; }}
    footer {{ color: #637083; font-size: 12px; padding: 0 24px 28px; text-align: center; }}
    @media (max-width: 760px) {{
      .top {{ padding: 22px 18px; }}
      h1 {{ font-size: 24px; }}
      .nav {{ overflow-x: auto; padding: 11px 18px; white-space: nowrap; }}
      main {{ padding: 16px 12px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .point {{ padding: 16px 12px; }}
      .point-head {{ display: block; }}
      .mode {{ margin-top: 10px; }}
      .evidence-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <p class="eyebrow">Fact-Check-X · 第三阶段</p>
    <h1>{escaped(report_title)}</h1>
  </header>
  <nav class="nav">
    <a href="01-capture-report.html">各方答案汇总</a>
    <a href="02-comparison-report.html">各方答案聚合</a>
    {final_report_nav}
  </nav>
  <main>
    <section class="final-answer" aria-label="{escaped(final_answer_title)}">
      <div class="final-answer-head">
        <div><p class="final-kicker">权威证据逐点核验完成</p><h2>{escaped(final_answer_title)}</h2></div>
        <span class="final-status">{escaped(final_status)}</span>
      </div>
      <p class="final-answer-body">{escaped(final_answer.get("answer"))}</p>
    </section>
    {unverified_boundary}
    <section class="metrics" aria-label="权威核验摘要">
      <div class="metric"><b>{len(points)}</b><span>核验知识点</span></div>
      <div class="metric"><b>{len(platforms)}</b><span>参与平台</span></div>
      <div class="metric"><b>{direct_count}</b><span>直接准确裁决</span></div>
      <div class="metric"><b>{verification.get("trustedSearchRequestCount", 0)}</b><span>可信搜索请求</span></div>
      <div class="metric"><b>{evidence_gap_count}</b><span>证据不足项</span></div>
    </section>
    {point_sections}
  </main>
  <footer>报告由已锁定的知识点聚合、权威证据、裁决与结果数据生成；不得脱离原始存证单独解释。</footer>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="生成独立的全知晓完美答案报告。")
    parser.add_argument("--verification", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    verification = load_json(Path(args.verification).resolve())
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(verification), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "completed",
                "report": str(output),
                "platformCount": len(verification.get("platforms") or []),
                "knowledgePointCount": len(
                    verification.get("knowledgePoints") or []
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
