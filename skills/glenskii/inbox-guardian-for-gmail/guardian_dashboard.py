import os
import sys
import json
import datetime
import webbrowser
from html import escape
from guardian_storage import open_private_sqlite, write_private_bytes

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
CONFIG_EXAMPLE = os.path.join(SCRIPT_DIR, "config.example.json")
STATS_FILE = os.path.join(SCRIPT_DIR, "guardian_stats.json")
DB_PATH = os.path.join(SCRIPT_DIR, "sender_reputation.db")
DASHBOARD_HTML = os.path.join(SCRIPT_DIR, "dashboard.html")


def display_text(value) -> str:
    """Encode mailbox-derived data before placing it in the local HTML report."""
    return escape(str(value or ''), quote=True)

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_reputation_stats():
    vip_count = 0
    total_senders = 0
    recent_vips = []
    if os.path.exists(DB_PATH):
        try:
            with open_private_sqlite(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM senders WHERE is_vip = 1 OR score >= 5')
                vip_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM senders')
                total_senders = cursor.fetchone()[0]
                cursor.execute('SELECT email, score, last_seen, notes FROM senders WHERE is_vip = 1 ORDER BY last_seen DESC LIMIT 10')
                recent_vips = [{"email": r[0], "score": r[1], "last_seen": r[2], "notes": r[3]} for r in cursor.fetchall()]
        except Exception:
            pass
    return vip_count, total_senders, recent_vips

def generate_dashboard_html():
    cfg = load_json(CONFIG_FILE)
    if not cfg:
        cfg = load_json(CONFIG_EXAMPLE)

    stats_data = load_json(STATS_FILE)
    
    total_neutralized = stats_data.get("total_neutralized", 0)
    total_relays = stats_data.get("total_relays_harvested", 0)
    events = stats_data.get("daily_events", [])
    
    cutoff_24h = (datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()
    events_24h = [e for e in events if e.get("timestamp", "") >= cutoff_24h]
    count_24h = len(events_24h)
    
    whitelist_domains = cfg.get("whitelist_domains", [])
    blocklist_domains = cfg.get("blocklist_domains", [])
    
    vip_count, total_senders, recent_vips = get_reputation_stats()
    
    event_rows = ""
    for ev in reversed(events[-20:]):
        ts = display_text(ev.get("timestamp", "").replace("T", " ")[:19])
        relay_badge = f'<span class="badge badge-relay">🧬 {display_text(ev.get("relay_harvested"))}</span>' if ev.get("relay_harvested") else '<span class="text-muted">None</span>'
        event_rows += f"""
        <tr>
            <td class="text-muted">{ts}</td>
            <td class="fw-bold">{display_text(ev.get('sender', ''))}</td>
            <td>{display_text(ev.get('subject', ''))}</td>
            <td><span class="badge badge-reason">{display_text(ev.get('reason', ''))}</span></td>
            <td>{relay_badge}</td>
        </tr>
        """
    
    if not event_rows:
        event_rows = """<tr><td colspan="5" class="text-center text-muted py-4">No threats logged yet. System running clean!</td></tr>"""

    vip_rows = ""
    for v in recent_vips:
        vip_rows += f"""
        <tr>
            <td class="fw-bold">{display_text(v['email'])}</td>
            <td><span class="badge badge-vip">⭐ VIP (Score {display_text(v['score'])})</span></td>
            <td class="text-muted">{display_text(v.get('notes', 'Trusted correspondent'))}</td>
        </tr>
        """
    if not vip_rows:
        vip_rows = """<tr><td colspan="3" class="text-muted py-3">Run <code>python guardian.py --seed-reputation</code> to index trusted contacts.</td></tr>"""

    domain_pills = "".join([f'<span class="pill pill-domain">🌐 {display_text(d)}</span>' for d in whitelist_domains]) if whitelist_domains else '<span class="text-muted">None configured</span>'
    block_pills = "".join([f'<span class="pill pill-block">🚫 {display_text(d)}</span>' for d in blocklist_domains[-15:]]) if blocklist_domains else '<span class="text-muted">None configured</span>'

    now_str = datetime.datetime.now().strftime("%B %d, %Y - %I:%M:%S %p")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail Guardian | Visual Control Center</title>
    <style>
        :root {{
            --bg-primary: #0a0f0d;
            --bg-card: #121a16;
            --bg-card-hover: #16221c;
            --accent-green: #00e599;
            --accent-cyan: #00d2ff;
            --accent-red: #ff3366;
            --accent-orange: #ff9900;
            --text-primary: #e6f4ee;
            --text-secondary: #8da398;
            --text-muted: #53695e;
            --border-color: rgba(0, 229, 153, 0.15);
            --font-main: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            --font-mono: "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-main);
            padding: 32px 24px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 32px;
        }}
        .logo-area {{ display: flex; align-items: center; gap: 16px; }}
        .logo-badge {{
            background: rgba(0, 229, 153, 0.1);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 1px;
        }}
        h1 {{ font-size: 24px; font-weight: 800; color: #fff; }}
        .status-pill {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 229, 153, 0.1);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-green);
        }}
        .grid-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s ease;
        }}
        .stat-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent-green);
            transform: translateY(-2px);
        }}
        .stat-label {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-val {{
            font-size: 32px;
            font-weight: 800;
            color: #fff;
            font-family: var(--font-mono);
        }}
        .stat-delta {{
            font-size: 12px;
            color: var(--accent-green);
            margin-top: 4px;
            font-weight: 600;
        }}
        .section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 28px;
        }}
        .section-title {{
            font-size: 17px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            text-align: left;
            padding: 12px;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            font-family: var(--font-mono);
        }}
        .badge-reason {{ background: rgba(255, 51, 102, 0.15); color: var(--accent-red); border: 1px solid rgba(255, 51, 102, 0.3); }}
        .badge-relay {{ background: rgba(0, 210, 255, 0.15); color: var(--accent-cyan); border: 1px solid rgba(0, 210, 255, 0.3); }}
        .badge-vip {{ background: rgba(0, 229, 153, 0.15); color: var(--accent-green); border: 1px solid rgba(0, 229, 153, 0.3); }}
        .pill-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-family: var(--font-mono);
            font-weight: 600;
        }}
        .pill-domain {{ background: rgba(0, 229, 153, 0.08); color: var(--accent-green); border: 1px solid rgba(0, 229, 153, 0.2); }}
        .pill-block {{ background: rgba(255, 51, 102, 0.08); color: var(--accent-red); border: 1px solid rgba(255, 51, 102, 0.2); }}
        .text-muted {{ color: var(--text-muted); }}
        .fw-bold {{ font-weight: 600; }}
        footer {{
            margin-top: 36px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-area">
                <div class="logo-badge">🛡️ GUARDIAN</div>
                <div>
                    <h1>Gmail Guardian Control Center</h1>
                    <p style="font-size: 13px; color: var(--text-secondary);">Local-First Anti-Botnet Defense & Heuristic Quarantine Engine</p>
                </div>
            </div>
            <div class="status-pill">
                <div class="pulse-dot"></div>
                System Active (Sleep-Safe)
            </div>
        </header>

        <!-- Stats Overview -->
        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Total Threats Processed</div>
                <div class="stat-val">{total_neutralized}</div>
                <div class="stat-delta">+{count_24h} in last 24h</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Relay Networks Auto-Learned</div>
                <div class="stat-val" style="color: var(--accent-cyan);">{total_relays}</div>
                <div class="stat-delta">Autonomous harvesting active</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">VIP Trusted Contacts</div>
                <div class="stat-val" style="color: var(--accent-green);">{vip_count}</div>
                <div class="stat-delta">{total_senders} total sender records</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Protected Whitelist Domains</div>
                <div class="stat-val" style="color: var(--accent-orange);">{len(whitelist_domains)}</div>
                <div class="stat-delta">Safe domain rules active</div>
            </div>
        </div>

        <!-- Recent Neutralized Feed -->
        <div class="section-card">
            <div class="section-title">
                <span>🚨 Threat & Quarantine Event Feed (Recent)</span>
                <span style="font-size: 12px; color: var(--text-secondary); font-family: var(--font-mono);">Local-First Security Telemetry</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 170px;">Timestamp</th>
                        <th style="width: 260px;">Sender Display</th>
                        <th>Subject</th>
                        <th style="width: 200px;">Trigger Reason</th>
                        <th style="width: 180px;">Auto-Harvested Relay</th>
                    </tr>
                </thead>
                <tbody>
                    {event_rows}
                </tbody>
            </table>
        </div>

        <!-- Two Column Layout: VIPs & Protected Domains -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
            <div class="section-card">
                <div class="section-title">
                    <span>⭐ Top VIP Trusted Correspondents</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Email Address</th>
                            <th>Status</th>
                            <th>Context</th>
                        </tr>
                    </thead>
                    <tbody>
                        {vip_rows}
                    </tbody>
                </table>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <span>🌐 Whitelisted Domains & Learned Blocklists</span>
                </div>
                <div style="margin-bottom: 16px;">
                    <div style="font-size: 12px; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase;">
                        Protected Whitelist Domains:
                    </div>
                    <div class="pill-container">
                        {domain_pills}
                    </div>
                </div>
                <div>
                    <div style="font-size: 12px; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase;">
                        Recent Blocklisted Relays:
                    </div>
                    <div class="pill-container">
                        {block_pills}
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <div>Report Generated: {now_str}</div>
            <div>Inbox Guardian for Gmail v1.0.2 • 100% Local-First Open Source</div>
        </footer>
    </div>
</body>
</html>
"""
    write_private_bytes(DASHBOARD_HTML, html_content.encode('utf-8'))
    print(f"[DASHBOARD] Generated updated visual report: {DASHBOARD_HTML}")
    return DASHBOARD_HTML

def main():
    path = generate_dashboard_html()
    if "--open" in sys.argv or len(sys.argv) == 1:
        print("[DASHBOARD] Opening in default browser...")
        webbrowser.open(path)

if __name__ == '__main__':
    main()
