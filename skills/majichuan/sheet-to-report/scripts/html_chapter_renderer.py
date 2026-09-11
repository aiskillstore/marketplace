"""只展示已验证章节；不生成判断，不读取原表，不依赖 PPT。"""
from __future__ import annotations

from html import escape
import re
from html_analysis import verify, resolve_text
from html_chart_views import chart_series


def fmt(value):
    if value is None:
        return "—"
    return f"{value:,.2f}".rstrip("0").rstrip(".") if isinstance(value, (int, float)) else str(value)


def _signed(value):
    return ("+" if value > 0 else "") + fmt(value)


def _bar(value, maximum, signed=False, role="normal"):
    width = abs(value) / (maximum or 1) * (50 if signed else 100)
    left = 50-width if value < 0 else (50 if signed else 0)
    tone = "negative" if value < 0 else ("positive" if role in {"leader", "remainder"} else "normal")
    if role == "total":
        tone = "total"
    return f'<div class="bar-track{" signed" if signed else ""}"><i class="{tone}" style="left:{left:.5f}%;width:{width:.5f}%"></i></div>'


def chart_svg(chart, snapshot, view=None):
    if chart.get("version") == "chart-spec/1":
        from chart_contract import project_chart
        from chart_svg_renderer import render_chart
        if view is None:
            view = project_chart(chart, snapshot["evidence"][chart["evidence_id"]])
        title = resolve_text(chart["title"], snapshot, [chart["evidence_id"]])
        return render_chart(view, title, chart.get("emphasis"))
    record = snapshot["evidence"][chart["evidence_id"]]
    view = chart_series(chart, record)
    labels, series = view["labels"], view["series"]
    title = resolve_text(chart["title"], snapshot, [chart["evidence_id"]])
    unit, values = series[0]["unit"], series[0]["values"]
    kind = chart["kind"]
    if kind == "paired":
        headers = "".join(f'<span>{escape(s["label"])}<small>{escape(s["unit"])}</small></span>' for s in series)
        maxima = [max(abs(v) for v in s["values"]) or 1 for s in series]
        signed = [any(v < 0 for v in s["values"]) for s in series]
        rows = []
        for i, label in enumerate(labels):
            cells = "".join(f'<div class="paired-cell"><b>{fmt(s["values"][i])}<small>{escape(s["unit"])}</small></b>' + _bar(s["values"][i], maxima[j], signed[j]) + '</div>' for j, s in enumerate(series))
            rows.append(f'<div class="paired-row"><span class="object">{escape(label)}</span>{cells}</div>')
        drawing = '<p class="chart-note">同一行对应同一对象；两列分别按各自最大绝对值缩放，跨列条长不可直接比较。</p><div class="paired-head"><span>对象</span>'+headers+'</div>'+"".join(rows)
        unit = "独立标尺"
    elif kind in {"bar", "contribution"}:
        maximum = max(abs(v) for v in values) or 1
        signed = kind == "contribution" or any(v < 0 for v in values)
        rows = []
        for i, (label, value) in enumerate(zip(labels, values)):
            role = view.get("roles", ["normal"] * len(labels))[i]
            number = _signed(value) if signed else fmt(value)
            rows.append(f'<div class="bar-row {role}"><div class="bar-heading"><span>{escape(label)}</span><b>{number}<small>{escape(unit)}</small></b></div>' + _bar(value, maximum, signed, role) + '</div>')
        drawing = '<div class="bar-chart">'+"".join(rows)+'</div>'
        if kind == "contribution":
            r = view["reconciliation"]
            drawing += f'<p class="chart-note reconciliation">全量 {view["source_count"]} 个对象对账：{_signed(r["leader"])} + ({_signed(r["remainder"])}) = {_signed(r["total"])} {escape(unit)}。零轴左侧为抵减，右侧为拉动；末行为净变动总计。</p>'
    else:
        low, high = min(0, min(values)), max(0, max(values))
        span = high-low or 1
        marks, points = [], []
        for i in range(4):
            yy, value = 205-i*55, low+span*i/3
            label = fmt(value/10000)+"万" if abs(value) >= 10000 else fmt(value)
            marks.append(f'<path d="M55 {yy} H380" stroke="#e0e5ec"/><text x="48" y="{yy+4}" text-anchor="end" class="axis">{label}</text>')
        for i, (label, value) in enumerate(zip(labels, values)):
            xx, yy = 60+i*310/max(len(labels)-1, 1), 205-(value-low)/span*165
            points.append(f"{xx:.2f},{yy:.2f}")
            marks.append(f'<circle cx="{xx}" cy="{yy}" r="3" fill="#24528a"><title>{escape(label)}：{fmt(value)}{escape(unit)}</title></circle>')
            if i % max(1, (len(labels)+4)//5) == 0 or i == len(labels)-1:
                label = label[-5:] if re.fullmatch(r"\d{4}-\d{2}", label) else label
                marks.append(f'<text x="{xx}" y="233" text-anchor="middle" class="axis">{escape(label)}</text>')
        marks.insert(0, f'<polyline points="{" ".join(points)}" fill="none" stroke="#24528a" stroke-width="2.5"/>')
        reads = "".join(f'<tr><td>{escape(label)}</td><td>{fmt(v)}{escape(unit)}</td></tr>' for label, v in zip(labels, values))
        drawing = f'<svg role="img" aria-label="{escape(title)}" viewBox="0 0 400 250">'+"".join(marks)+f'</svg><details class="chart-values"><summary>查看逐期读数</summary><table>{reads}</table></details>'
    emphasis = chart.get("emphasis", "supporting")
    return f'<figure class="{emphasis} chart-{kind}"><figcaption>{escape(title)} <span>{escape(unit)}</span></figcaption>{drawing}</figure>'


def _kpis(record, row):
    # Common metric semantics only; unknown metrics retain their declared order.
    order = [key for key in ("net", "orders", "order_value", "customers", "units", "products") if key in record["columns"]]
    order += [key for key in record["columns"] if key not in order and key not in {"period", "__period"}]
    return "".join(f'<div class="kpi"><span>{escape(record["columns"][key]["label"])}</span><strong>{fmt(row[key])}<small>{escape(record["columns"][key]["unit"])}</small></strong></div>' for key in order)


def _nav_title(chapter):
    return chapter.get("nav_title") or re.split(r"[，。；：,;:]", chapter["title"])[0][:12]


def _suggested_role(action):
    return '<p><b>建议协同角色：</b>'+escape(action['suggested_role'])+'</p>' if action.get('suggested_role') else ''


def _render(model):
    verify(model)
    snapshot = model["snapshot"]
    verify(snapshot)
    esc = escape
    from summary_contract import validate_summary
    validate_summary(model)
    summary = "".join('<li>' + (f'<strong class="summary-headline">{esc(s["headline"])}</strong>' if s.get('headline') else '') + f'{esc(s["text"])} <a href="#{s["chapter_ids"][0]}">查看依据 ↗</a></li>' for s in model["summary"])
    nav = '<a href="#summary">核心结论</a><a href="#overview">基本盘</a>'
    nav += "".join(f'<a href="#{c["id"]}">{esc(_nav_title(c))}</a>' for c in model["chapters"])
    nav += '<a href="#actions">行动路线</a><a href="#method">口径与证据</a>'
    overview = snapshot["evidence"]["overview"]
    cards = _kpis(overview, overview["rows"][0])
    periods = overview["scope"]["periods"]
    period_text = " — ".join([periods[0], periods[-1]])
    sections = []
    for c in model["chapters"]:
        charts = "".join(chart_svg(chart, snapshot, model.get("chart_views", {}).get(chart.get("id"))) for chart in c["charts"])
        sections.append(f'<section id="{c["id"]}"><p class="eyebrow">{"经营背景" if c["role"] == "background" else "分析判断"}</p><h2>{esc(c["title"])}</h2><p class="lead">{esc(c["body"])}</p><div class="charts">{charts}</div><p class="meaning">{esc(c["meaning"])}</p><p class="limit">{esc(c["limitations"])}</p></section>')
    actions = "".join(f'<article class="action"><span class="number">{i+1:02}</span><div><h3>{esc(a["title"])}</h3><p><b>行动对象：</b>{esc(a["target"])}</p>{_suggested_role(a)}<p>{esc(a["basis"])}</p><p><b>做法：</b>{esc(a["steps"])}</p><p><b>判断效果：</b>{esc(a["success_signal"])}</p><p class="limit">{esc(a["boundary"])}</p><a href="#{a["chapter_ids"][0]}">回看分析依据 ↑</a></div></article>' for i, a in enumerate(model["actions"])) or '<p>本次内容为背景分析，尚未提出正式行动。</p>'
    proofs = []
    for record in snapshot["evidence"].values():
        columns = record["columns"]
        heads = "".join(f'<th>{esc(m["label"])}{("（"+esc(m["unit"])+"）") if m["unit"] else ""}</th>' for m in columns.values())
        rows = "".join('<tr>'+"".join(f'<td>{esc(fmt(r.get(k)))}</td>' for k in columns)+'</tr>' for r in record["rows"])
        proofs.append(f'<details><summary>{esc(record["label"])}</summary><p class="limit">{esc(record["scope"]["denominator"])}</p><div class="table-scroll"><table><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table></div></details>')
    warnings = "；".join(snapshot["warnings"])
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(model["title"])+'''</title><style>

:root{--ink:#263341;--muted:#596777;--paper:#faf9f6;--line:#dde2e8;--nav:64px;--blue:#24528a;--green:#167565;--negative:#b94735;--amber:#8a5b11}*{box-sizing:border-box}html{scroll-padding-top:calc(var(--nav) + 16px)}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 "Microsoft YaHei","PingFang SC",sans-serif}nav{position:fixed;inset:0 0 auto;z-index:20;display:flex;gap:22px;padding:16px max(24px,calc((100vw - 1120px)/2));height:var(--nav);background:#fff;border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,summary:focus-visible{outline:2px solid var(--blue);outline-offset:4px}nav a{font-size:13px}nav a.active{font-weight:bold;border-bottom:2px solid var(--blue)}main{max-width:1120px;margin:auto;padding:calc(var(--nav) + 48px) 28px 70px}header{padding-bottom:30px}h1{font-size:38px;letter-spacing:-1px;line-height:1.4;margin:8px 0 16px;color:#18395f}h2{font-size:27px;line-height:1.5;margin:8px 0 20px;color:#18395f}h3{font-size:20px;margin:0 0 8px}h1,h2{text-wrap:balance}section{padding:44px 0;border-top:1px solid var(--line)}p{margin:12px 0;max-width:78ch}.lead{font-size:17px;line-height:1.9}.limit{font-size:13px;color:var(--muted)}.summary{background:#fff;padding:26px 34px;border:1px solid var(--line);border-top:4px solid var(--blue);border-radius:5px}.summary h2{font-size:24px}.summary li{margin:14px 0;font-size:17px;padding-left:4px}.summary .summary-headline{display:block;font-size:17px;line-height:1.6;font-weight:700;margin:0 0 4px;color:var(--ink)}.summary li::marker{color:var(--blue)}.summary a{font-size:12px;white-space:nowrap}.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.kpi{padding:18px 0;border-bottom:1px solid var(--line);min-width:0}.kpi span{font-size:13px;color:var(--muted)}strong{display:block;font-size:29px;line-height:1.5;color:#18395f}small{font-size:12px;margin-left:6px;font-weight:normal}.charts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;align-items:start}figure{margin:12px 0;padding:22px;background:#fff;border:1px solid var(--line);border-radius:5px;min-width:0}.charts>figure:only-child,figure.primary{grid-column:1/-1}.charts>figure.primary+figure:last-child{grid-column:1/-1}figure.primary{padding:26px 30px}figcaption{font-weight:bold;margin-bottom:16px;color:#18395f;line-height:1.6}figcaption span{display:inline-block;margin-left:10px;font-size:12px;color:var(--muted);font-weight:normal}svg{display:block;width:100%;height:auto;max-height:340px}.axis{font-size:11px;fill:#596777}.meaning{padding:12px 0;font-weight:600;font-size:16px}.meaning::before{content:"解读";display:block;font-size:12px;color:var(--blue);margin-bottom:4px}.charts~.limit{padding:12px 16px;background:#fcf7eb;border:1px solid #e9ddc2;border-radius:4px}.charts~.limit::before{content:"判断边界 · ";color:var(--amber);font-weight:bold}.action{display:flex;gap:22px;padding:28px 0;border-bottom:1px solid var(--line)}.number{font-size:24px;color:var(--blue)}.action p{font-size:15px}details{background:#fff;margin:12px 0;padding:18px}summary{cursor:pointer}.table-scroll{overflow-x:auto;max-height:600px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:10px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}th:first-child,td:first-child{text-align:left}th{position:sticky;top:0;background:#f1f4f8}footer{color:var(--muted);font-size:12px;margin-top:30px}.bar-row{padding:9px 0}.bar-heading{display:flex;gap:12px;justify-content:space-between;align-items:baseline;font-size:13px;line-height:1.5}.bar-heading>span{min-width:0;overflow-wrap:anywhere}.bar-heading b,.paired-cell b{white-space:nowrap;font-weight:500;font-variant-numeric:tabular-nums}.bar-heading small{font-size:11px}.bar-track{position:relative;height:9px;background:#edf0f4;margin-top:7px}.bar-track.signed::after{content:"";position:absolute;left:50%;top:-3px;height:15px;border-left:1px solid #758293}.bar-track i{position:absolute;top:0;height:9px;background:var(--blue)}.bar-track i.negative{background:var(--negative)}.bar-track i.positive{background:var(--green)}.bar-track i.total{background:var(--blue);height:13px;top:-2px}.bar-row.total{border-top:1px solid var(--line);margin-top:12px;padding-top:18px}.bar-row.total b{font-weight:700}.chart-note{font-size:12px;color:var(--muted);line-height:1.7}.chart-values{padding:5px 0;background:transparent;font-size:12px}.chart-values summary{color:var(--muted)}.paired-row,.paired-head{display:grid;grid-template-columns:minmax(100px,1.2fr) repeat(2,minmax(0,1fr));gap:20px;align-items:center}.paired-head{font-size:12px;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:10px}.paired-head small{display:block;margin:0}.paired-row{padding:13px 0;border-bottom:1px solid #eff1f4}.paired-row .object{font-size:13px;overflow-wrap:anywhere}.paired-cell{min-width:0;font-size:13px}.paired-cell b{font-size:13px}.paired-cell small{font-size:10px}.reconciliation{margin-top:20px}td,strong{font-variant-numeric:tabular-nums}::selection{background:#dce8f6}
@media(max-width:720px){main{padding:calc(var(--nav) + 28px) 18px 40px}nav{gap:18px;padding-inline:18px}h1{font-size:28px}h2{font-size:23px}.summary{padding:20px}.summary ul{padding-left:20px}.summary li,.lead{font-size:16px}.kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}strong{font-size:22px;overflow-wrap:anywhere}.charts{display:block}figure,figure.primary{padding:18px 12px}.axis{font-size:12px}section{padding:32px 0}.paired-row,.paired-head{grid-template-columns:minmax(68px,.9fr) repeat(2,minmax(0,1fr));gap:10px}.paired-cell b{white-space:normal;font-size:12px}.paired-cell small{display:block;margin-left:0}.action{gap:14px}.bar-heading{font-size:12px}.bar-heading b{white-space:normal;text-align:right}.bar-heading small{display:inline-block}}
@media print{nav{display:none}:root{--nav:0px}html{scroll-padding-top:0}main{padding:0;max-width:none}body{background:white;font-size:11px;print-color-adjust:exact;-webkit-print-color-adjust:exact}section{padding:18px 0}.summary{padding:18px}.charts{display:block}figure,figure.primary{break-inside:avoid;max-width:680px;padding:14px;margin:10px 0}h1{font-size:26px}h2{font-size:20px}.limit{font-size:10px}details{display:none}.bar-heading{font-size:11px}.paired-row{padding:8px 0}.action{break-inside:avoid}svg{max-height:270px}}

</style></head><body><nav aria-label="报告导航">'''+nav+'</nav><main><header><p class="eyebrow">经营分析 · 内部候选</p><h1>'+esc(model["title"])+'</h1><p>'+esc(period_text)+' · '+esc(snapshot["request"]["audience"])+'</p></header><section id="summary" class="summary"><h2>先看结论</h2><ul>'+summary+'</ul></section><section id="overview"><p class="eyebrow">建立规模与范围</p><h2>经营基本盘</h2><p class="limit">'+esc(period_text)+' · '+esc(overview["scope"]["denominator"])+'</p><div class="kpis">'+cards+'</div></section>'+"".join(sections)+'<section id="actions"><p class="eyebrow">按决策价值排序</p><h2>下一步行动</h2>'+actions+'</section><section id="method"><h2>口径与完整证据</h2><p class="limit">'+esc(warnings)+'</p>'+"".join(proofs)+'</section><footer>描述性分析与结构关联，不等同因果。候选报告，产品体验待校准。</footer></main><script>const links=[...document.querySelectorAll("nav a")];let pending=false;function highlight(){pending=false;const threshold=document.querySelector("nav").getBoundingClientRect().bottom+18;let chosen=links[0];for(const link of links){const target=document.querySelector(link.getAttribute("href"));if(target&&target.getBoundingClientRect().top<=threshold)chosen=link;}links.forEach(link=>link.classList.toggle("active",link===chosen));}addEventListener("scroll",()=>{if(pending)return;pending=true;requestAnimationFrame(highlight);},{passive:true});addEventListener("resize",highlight);highlight();</script></body></html>'


def render(model):
    page = _render(model)
    if model.get("chart_views"):
        from chart_svg_renderer import CSS
        page = page.replace('</style>', CSS+'</style>', 1)
    page = re.sub(r'<p class="eyebrow">.*?</p>', '', page)
    snapshot = model["snapshot"]
    if "commerce_trend" in snapshot["evidence"]:
        series = snapshot["evidence"]["commerce_trend"]
        current = series["rows"][-1]
        previous = series["rows"][-2] if len(series["rows"]) > 1 else None
        label = "最新完整月：" + current["period"]
        if previous:
            label += "；对比月份：" + previous["period"]
        cards = _kpis(series, current)
        fragment = '<h3 style="margin-top:32px">'+escape(label)+'</h3><div class="kpis">'+cards+'</div>'
        page = page.replace('</div></section>', '</div>'+fragment+'</section>', 1)
    return page
