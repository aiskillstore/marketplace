#!/usr/bin/env python3
"""HTML layout helpers for the Skill Atlas report."""

import html
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by build_skill_atlas.py to render the static Skill Atlas HTML report."


def render_html(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = []
    for skill in payload["catalog"]["skills"][:80]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(skill['name'])}</td>"
            f"<td>{html.escape(skill['path'])}</td>"
            f"<td>{html.escape(skill.get('owner') or 'missing')}</td>"
            f"<td>{html.escape(skill.get('maturity') or 'unknown')}</td>"
            f"<td>{html.escape(skill.get('review_cadence') or 'missing')}</td>"
            f"<td>{html.escape(skill.get('atlas_scope') or 'release')}</td>"
            "</tr>"
        )
    blockers = (
        payload["actionable_route_collisions"][:20]
        + payload["actionable_owner_review_gaps"][:20]
        + payload["actionable_stale_skills"][:20]
        + payload["actionable_drift_signals"][:20]
    )
    blocker_items = "".join(
        f"<li><strong>{html.escape(item.get('name', item.get('skill_a', 'issue')))}</strong> {html.escape(item.get('reason', item.get('status', ', '.join(item.get('missing', item.get('signal_types', []))))))}</li>"
        for item in blockers
    )
    opportunity_items = "".join(
        (
            "<li>"
            f"<strong>{html.escape(item.get('skill') or item.get('source_type', 'opportunity'))}</strong> "
            f"{html.escape(item.get('note') or item.get('recommendation') or item.get('signal', 'no-route opportunity'))}"
            f"<br><small>{html.escape(item.get('source', ''))}</small>"
            "</li>"
        )
        for item in payload["no_route_opportunities"][:20]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Skill Atlas</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #fff; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 40px 24px; }}
    h1 {{ font-size: 34px; margin-bottom: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin: 28px 0; }}
    .card {{ border: 1px solid #d9e0ea; border-radius: 8px; padding: 16px; background: #f8fafc; }}
    .card span {{ display: block; color: #697386; font-size: 13px; }}
    .card strong {{ display: block; font-size: 28px; color: #1B365D; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ text-align: left; border-bottom: 1px solid #e5e9f0; padding: 10px; vertical-align: top; }}
    th {{ color: #1B365D; font-size: 13px; }}
    li {{ margin: 8px 0; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>Skill Atlas</h1>
    <p>Portfolio-level review for route overlap, stale ownership, shared resources, telemetry drift, and no-route opportunities.</p>
    <section class="grid">
      <div class="card"><span>Skills</span><strong>{summary['skill_count']}</strong></div>
      <div class="card"><span>Actionable</span><strong>{summary['actionable_skill_count']}</strong></div>
      <div class="card"><span>Route Collisions</span><strong>{summary['actionable_route_collision_count']}</strong></div>
      <div class="card"><span>Owner Gaps</span><strong>{summary['actionable_owner_gap_count']}</strong></div>
      <div class="card"><span>Stale Skills</span><strong>{summary['actionable_stale_count']}</strong></div>
      <div class="card"><span>Drift Signals</span><strong>{summary['actionable_drift_signal_count']}</strong></div>
      <div class="card"><span>No-Route Opportunities</span><strong>{summary['no_route_opportunity_count']}</strong></div>
    </section>
    <section>
      <h2>Actionable Issues</h2>
      <ul>{blocker_items or '<li>No blocking portfolio issues detected.</li>'}</ul>
    </section>
    <section>
      <h2>No-Route Opportunities</h2>
      <p>Missed-trigger telemetry and explicit failure cases become candidate routing work without storing raw prompts or outputs.</p>
      <ul>{opportunity_items or '<li>No no-route opportunities detected.</li>'}</ul>
    </section>
    <section>
      <h2>Full Portfolio Counts</h2>
      <p>All scanned skills remain visible: {summary['route_collision_count']} total route collisions, {summary['owner_gap_count']} total owner gaps, {summary['stale_count']} total stale signals, and {summary['drift_signal_count']} telemetry drift signals.</p>
    </section>
    <section>
      <h2>Catalog</h2>
      <table>
        <thead><tr><th>Name</th><th>Path</th><th>Owner</th><th>Maturity</th><th>Review</th><th>Scope</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
