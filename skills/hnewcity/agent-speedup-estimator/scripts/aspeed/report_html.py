from __future__ import annotations

import html
import json

from .i18n import strings

# Interface follows the Duna style: warm Linen canvas, Aubergine ink, white cards, hairline rings,
# pill controls, no shadows, tight display tracking. Colour appears only on data marks; the two
# series hues were validated with the dataviz palette checker on the card surface in both modes.
_CSS = r"""
:root { color-scheme: light dark; }
.viz-root {
  color-scheme: light;
  --canvas: #f7f7f5; --card: #ffffff; --panel: #edece7; --input: #eeeeee;
  --ink: #1b0624; --ink2: #444444; --muted: #766a7c; --stone: #898683;
  --action: #160f0c; --on-action: #ffffff;
  --grid: #edece7; --axis: #d6d3cc; --ring: rgba(0,0,0,0.05); --hair: rgba(27,6,36,0.10); --wash: rgba(27,6,36,0.04);
  --s1: #7b4f9e; --s2: #c2703d; --dot: #898683; --on-fill: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --canvas: #141113; --card: #1f1b1d; --panel: #2a2528; --input: #2a2528;
    --ink: #f3eef0; --ink2: #cdc6c9; --muted: #a79caa; --stone: #8f8a87;
    --action: #f3eef0; --on-action: #160f0c;
    --grid: #2c2729; --axis: #3d373a; --ring: rgba(255,255,255,0.06); --hair: rgba(255,255,255,0.10); --wash: rgba(255,255,255,0.05);
    --s1: #9a6cc4; --s2: #c9773f; --dot: #8f8a87;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --canvas: #141113; --card: #1f1b1d; --panel: #2a2528; --input: #2a2528;
  --ink: #f3eef0; --ink2: #cdc6c9; --muted: #a79caa; --stone: #8f8a87;
  --action: #f3eef0; --on-action: #160f0c;
  --grid: #2c2729; --axis: #3d373a; --ring: rgba(255,255,255,0.06); --hair: rgba(255,255,255,0.10); --wash: rgba(255,255,255,0.05);
  --s1: #9a6cc4; --s2: #c9773f; --dot: #8f8a87;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body.viz-root {
  margin: 0; background: var(--canvas); color: var(--ink);
  font: 400 16px/1.6 "GT America", Inter, "Söhne", "Suisse Int'l", system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-feature-settings: "cv03", "cv04", "cv09", "cv11";
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
nav.top { height: 72px; display: flex; align-items: center; justify-content: space-between; }
.brand { display: inline-flex; align-items: center; gap: 8px; font-weight: 500; font-size: 15px; letter-spacing: 0.02em; color: var(--ink); }
.brand-mark { font-size: 18px; line-height: 1; }
.nav-meta { color: var(--muted); font-size: 14px; }

.hero { text-align: center; padding: 72px 0 80px; }
.pill {
  display: inline-block; background: var(--action); color: var(--on-action);
  font-size: 12px; line-height: 1.2; padding: 6px 12px; border-radius: 999px; margin-bottom: 28px;
}
.hero-lead { font-size: 20px; line-height: 1.4; letter-spacing: -0.01em; color: var(--ink2); margin: 0 auto 8px; max-width: 760px; }
.hero-num { font-size: 120px; line-height: 1; letter-spacing: -0.06em; font-weight: 400; margin: 8px 0 20px; }
.hero-sub { font-size: 18px; line-height: 1.5; color: var(--stone); margin: 0 auto; max-width: 720px; }
.switch { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 32px; }
.chip {
  font: inherit; font-size: 14px; line-height: 1.2; padding: 10px 18px; border-radius: 999px; cursor: pointer;
  background: transparent; color: var(--ink); border: 1px solid var(--axis);
}
.chip:hover { background: var(--wash); }
.chip[aria-pressed="true"] { background: var(--action); color: var(--on-action); border-color: var(--action); }

.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; padding: 0 0 96px; text-align: left; }
.stat-v { font-size: 72px; line-height: 1; letter-spacing: -0.06em; font-weight: 400; }
.stat-l { font-size: 14px; line-height: 1.5; color: var(--stone); margin-top: 12px; max-width: 320px; }

section.block { padding-bottom: 24px; }
.sec-h { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin: 0 0 20px; }
h2 { font-size: 32px; line-height: 1.2; letter-spacing: -0.03em; font-weight: 400; margin: 0; }
.sec-sub { font-size: 16px; color: var(--muted); margin: 8px 0 0; max-width: 720px; }
.card { background: var(--card); border-radius: 16px; box-shadow: var(--ring) 0 0 0 1px inset; padding: 32px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
h3 { font-size: 24px; line-height: 1.3; letter-spacing: -0.02em; font-weight: 500; margin: 0 0 6px; }
.card-sub { font-size: 14px; color: var(--muted); margin: 0 0 20px; }
.toggle {
  font: inherit; font-size: 14px; line-height: 1.2; color: var(--ink); background: transparent; white-space: nowrap;
  border: 1px solid var(--stone); border-radius: 999px; padding: 10px 18px; cursor: pointer;
}
.toggle:hover { background: var(--wash); }
.toggle:focus-visible, .chip:focus-visible, .prow:focus-visible, .row:focus-visible, .seg:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }

.legend { display: flex; flex-wrap: wrap; gap: 6px 20px; color: var(--ink2); font-size: 14px; margin-bottom: 16px; }
.lg { display: inline-flex; align-items: center; gap: 8px; }
.sw { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
.sw-model, .seg-model { background: var(--s1); }
.sw-tool, .seg-tool, .bar-tool { background: var(--s2); }
.row { display: grid; grid-template-columns: 200px 1fr; align-items: center; gap: 16px; min-height: 40px; border-radius: 8px; }
.row:hover, .prow:hover { background: var(--wash); }
.row-l { color: var(--ink); font-size: 14px; overflow-wrap: anywhere; }
.track { position: relative; display: flex; align-items: center; gap: 10px; min-height: 24px; }
.stack { display: flex; gap: 2px; height: 24px; min-width: 2px; }
.seg { position: relative; display: flex; align-items: center; justify-content: center; min-width: 2px; }
.seg:last-child { border-radius: 0 4px 4px 0; }
.seg-t { color: var(--on-fill); font-size: 12px; font-weight: 500; padding: 0 8px; white-space: nowrap; }
.bar { height: 16px; min-width: 2px; border-radius: 0 4px 4px 0; transition: filter .12s; }
.row:hover .bar, .row:focus-visible .bar { filter: brightness(1.08); }
.val { color: var(--ink2); font-size: 13px; white-space: nowrap; font-variant-numeric: tabular-nums; }

.prow {
  display: grid; grid-template-columns: 200px 1fr 120px; align-items: center; gap: 16px; width: 100%;
  text-align: left; font: inherit; color: inherit; background: transparent; border: 0; border-radius: 8px;
  min-height: 48px; padding: 0; cursor: pointer;
}
.prow .row-l { display: flex; flex-direction: column; }
.prow .tier { color: var(--stone); font-size: 12px; }
.prow[aria-pressed="true"] .nm { font-weight: 500; }
.rtrack { height: 44px; }
.gl { position: absolute; top: 0; bottom: 0; width: 1px; background: var(--grid); }
.gl.base { background: var(--axis); }
.rline { position: absolute; top: 50%; height: 2px; margin-top: -1px; background: var(--dot); border-radius: 1px; opacity: .7; }
.rdot { position: absolute; top: 50%; width: 10px; height: 10px; margin: -5px 0 0 -5px; border-radius: 50%; background: var(--dot); box-shadow: 0 0 0 2px var(--card); }
.prow[aria-pressed="true"] .rline { background: var(--ink); opacity: 1; }
.prow[aria-pressed="true"] .rdot { background: var(--ink); }
.val-col { display: flex; flex-direction: column; font-size: 12px; color: var(--muted); }
.val-col strong { font-size: 18px; color: var(--ink); font-weight: 500; letter-spacing: -0.01em; }
.flag { color: var(--stone); font-size: 12px; }
.axis { display: grid; grid-template-columns: 200px 1fr 120px; gap: 16px; margin-bottom: 4px; }
.axis-track { position: relative; height: 18px; }
.tick { position: absolute; transform: translateX(-50%); font-size: 11px; color: var(--stone); font-variant-numeric: tabular-nums; }
.hint { color: var(--stone); font-size: 13px; margin: 16px 0 0; }
.filters, .pager { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin: 16px 0; }
.filters label { display: flex; flex-direction: column; font-size: 12px; color: var(--muted); gap: 4px; }
.filters input, .filters select { font: inherit; font-size: 14px; color: var(--ink); background: var(--card); border: 1px solid var(--axis); border-radius: 8px; padding: 10px; max-width: 100%; }
.filters input { min-width: 250px; }
.pager button:disabled { opacity: .4; cursor: default; }
a { color: inherit; }

.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--grid); }
th { color: var(--muted); font-weight: 400; font-size: 13px; }
th.r, td.r { text-align: right; font-variant-numeric: tabular-nums; }
tr.total td { font-weight: 500; border-top: 1px solid var(--axis); border-bottom: 0; }
dl { display: grid; grid-template-columns: 1fr auto; gap: 12px 24px; margin: 0; font-size: 14px; }
.card > dl { max-width: 720px; }
dt { color: var(--muted); } dd { margin: 0; text-align: right; font-variant-numeric: tabular-nums; color: var(--ink); }
ul.notes { margin: 0; padding: 0; list-style: none; display: grid; gap: 14px; color: var(--ink2); font-size: 15px; line-height: 1.6; }
ul.notes li { padding-left: 20px; position: relative; }
ul.notes li::before { content: "✱"; position: absolute; left: 0; top: 0; color: var(--stone); font-size: 11px; line-height: 2.2; }
footer { color: var(--stone); font-size: 13px; padding: 48px 0 64px; }

#tip {
  position: fixed; z-index: 10; pointer-events: none; max-width: 320px; padding: 10px 12px; border-radius: 12px;
  background: var(--card); color: var(--ink); box-shadow: var(--hair) 0 0 0 1px inset; font-size: 13px;
}
.tip-t { color: var(--muted); margin-bottom: 6px; }
.tip-r { display: flex; align-items: center; gap: 8px; line-height: 1.7; }
.tip-r strong { font-size: 14px; font-weight: 500; }
.tip-n { color: var(--muted); }
.key { width: 12px; height: 2px; border-radius: 1px; display: inline-block; background: var(--dot); }
.key-model { background: var(--s1); } .key-tool { background: var(--s2); }

@media (max-width: 900px) {
  .grid2 { grid-template-columns: 1fr; }
  .stats { grid-template-columns: 1fr; gap: 28px; padding-bottom: 72px; }
}
@media (max-width: 680px) {
  .wrap { padding: 0 16px; }
  .hero { padding: 40px 0 56px; }
  .hero-num { font-size: 80px; }
  .stat-v { font-size: 56px; }
  h2 { font-size: 26px; }
  .card { padding: 20px; }
  .row, .axis { grid-template-columns: 1fr; gap: 2px; }
  .prow { grid-template-columns: 1fr; gap: 2px; padding: 8px 0; }
  .axis > :first-child, .axis > :last-child { display: none; }
  .sec-h { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
@media print, (forced-colors: active) {
  .seg-tool, .bar-tool, .sw-tool { background-image: repeating-linear-gradient(45deg, rgba(0,0,0,0.4) 0 2px, transparent 2px 6px); }
}
@media (forced-colors: active) {
  .seg, .bar, .rdot, .rline, .sw { forced-color-adjust: none; }
  .seg-model, .sw-model { background: CanvasText; } .seg-tool, .bar-tool, .sw-tool { background-color: LinkText; }
  .rdot, .rline { background: CanvasText; } .prow[aria-pressed="true"] .rdot, .prow[aria-pressed="true"] .rline { background: Highlight; }
}
@media print { .toggle, .switch { display: none; } body.viz-root { background: #fff; } }
"""

_JS = r"""
(function () {
  'use strict';
  var D = JSON.parse(document.getElementById('data').textContent);
  var R = D.r, S = D.S, CN = D.cats, A = R.agents, all = A.all, targets = R.targets;
  var agentNames = ['claude', 'codex'].filter(function (k) { return A[k]; });
  var agentLabel = { claude: S.col_claude, codex: S.col_codex };
  var sel = R.primary || 0;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function $(s) { return document.querySelector(s); }
  function fmt(t, o) { return t.replace(/\{(\w+)\}/g, function (_, k) { return o[k] != null ? o[k] : ''; }); }
  function dur(s) {
    s = +s;
    if (s < 90) return Math.round(s) + 's';
    if (s < 5400) return Math.round(s / 60) + 'm';
    return (s / 3600).toFixed(1) + 'h';
  }
  function x2(v) { return v.toFixed(2) + 'x'; }
  function pct(a, b) { return b ? Math.round(100 * a / b) + '%' : '-'; }
  function chg(o, n) {
    if (o <= 0) return '-';
    var p = (n - o) / o * 100;
    if (Math.abs(p) < 0.5) return '0%';
    return (p > 0 ? '+' : '−') + Math.abs(p).toFixed(0) + '%';
  }
  function range(t) {
    var v = ['conservative', 'expected', 'optimistic'].map(function (k) { return t.scenarios[k].total_speedup; });
    return { lo: Math.min.apply(null, v), ex: t.scenarios.expected.total_speedup, hi: Math.max.apply(null, v) };
  }

  var tip = $('#tip');
  function hideTip() { tip.hidden = true; }
  function placeTip(x, y) {
    tip.hidden = false;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.min(x + 14, window.innerWidth - w - 8);
    var top = y + 16 + h > window.innerHeight ? y - h - 12 : y + 16;
    tip.style.left = Math.max(8, left) + 'px';
    tip.style.top = Math.max(8, top) + 'px';
  }
  function tipTitle(t, text) { t.appendChild(el('div', 'tip-t', text)); }
  function tipRow(t, key, value, name) {
    var r = el('div', 'tip-r');
    r.appendChild(el('span', 'key key-' + key));
    r.appendChild(el('strong', null, value));
    r.appendChild(el('span', 'tip-n', name));
    t.appendChild(r);
  }
  function bindTip(node, build) {
    function show(x, y) { tip.replaceChildren(); build(tip); placeTip(x, y); }
    node.addEventListener('pointermove', function (e) { show(e.clientX, e.clientY); });
    node.addEventListener('pointerleave', hideTip);
    node.addEventListener('focus', function () { var r = node.getBoundingClientRect(); show(r.left + Math.min(r.width / 2, 160), r.top); });
    node.addEventListener('blur', hideTip);
    if (!node.hasAttribute('tabindex') && node.tagName !== 'BUTTON') node.tabIndex = 0;
  }

  function table(heads, rows, aligns, totalLast) {
    var wrap = el('div', 'tbl-wrap'), t = el('table'), th = el('thead'), tr = el('tr');
    heads.forEach(function (h, i) {
      var c = el('th', aligns[i] === 'r' ? 'r' : null, h); c.scope = 'col'; tr.appendChild(c);
    });
    th.appendChild(tr); t.appendChild(th);
    var tb = el('tbody');
    rows.forEach(function (r, ri) {
      var row = el('tr', totalLast && ri === rows.length - 1 ? 'total' : null);
      r.forEach(function (v, i) { row.appendChild(el('td', aligns[i] === 'r' ? 'r' : null, v)); });
      tb.appendChild(row);
    });
    t.appendChild(tb); wrap.appendChild(t);
    return wrap;
  }
  function legend(items) {
    var l = el('div', 'legend');
    items.forEach(function (it) {
      var i = el('span', 'lg'); i.appendChild(el('span', 'sw sw-' + it.cls)); i.appendChild(document.createTextNode(it.label)); l.appendChild(i);
    });
    return l;
  }
  function withToggle(head, chart, tbl) {
    tbl.hidden = true;
    var b = el('button', 'toggle', S.table_view); b.type = 'button'; b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () {
      var showTable = tbl.hidden;
      tbl.hidden = !showTable; chart.hidden = showTable;
      b.textContent = showTable ? S.chart_view : S.table_view; b.setAttribute('aria-pressed', String(showTable));
    });
    head.appendChild(b);
  }
  function section(title, sub) {
    var s = el('section', 'block'), h = el('div', 'sec-h'), t = el('div');
    t.appendChild(el('h2', null, title));
    if (sub) t.appendChild(el('p', 'sec-sub', sub));
    h.appendChild(t); s.appendChild(h);
    return { root: s, head: h };
  }
  function card(title, sub) {
    var c = el('div', 'card'), h = el('div', 'sec-h'), t = el('div');
    if (title) t.appendChild(el('h3', null, title));
    if (sub) t.appendChild(el('p', 'card-sub', sub));
    h.appendChild(t); c.appendChild(h);
    return { root: c, head: h };
  }
  function fitLabels(root) {
    root.querySelectorAll('.seg-t').forEach(function (lab) {
      lab.style.visibility = 'hidden';
      lab.style.display = '';
      var fits = lab.parentNode.clientWidth > 0 && lab.offsetWidth + 4 <= lab.parentNode.clientWidth;
      lab.style.display = fits ? '' : 'none';
      lab.style.visibility = '';
    });
  }

  var working = all.model_s + all.tool_s;

  function splitChart() {
    var wrap = el('div');
    wrap.appendChild(legend([{ cls: 'model', label: S.model }, { cls: 'tool', label: S.tools }]));
    var max = Math.max.apply(null, agentNames.map(function (n) { return A[n].model_s + A[n].tool_s; })) || 1;
    agentNames.forEach(function (n) {
      var a = A[n], tot = a.model_s + a.tool_s;
      var row = el('div', 'row'); row.setAttribute('role', 'group');
      row.setAttribute('aria-label', agentLabel[n] + ': ' + dur(tot));
      row.appendChild(el('div', 'row-l', agentLabel[n]));
      var track = el('div', 'track'), stack = el('div', 'stack');
      stack.style.width = (tot / max * 80) + '%';
      [['model', a.model_s, S.model], ['tool', a.tool_s, S.tools]].forEach(function (p) {
        if (p[1] <= 0) return;
        var seg = el('div', 'seg seg-' + p[0]); seg.style.flex = p[1] + ' 1 0';
        seg.appendChild(el('span', 'seg-t', pct(p[1], tot)));
        bindTip(seg, function (t) { tipTitle(t, agentLabel[n]); tipRow(t, p[0], dur(p[1]), p[2] + ' · ' + pct(p[1], tot)); });
        stack.appendChild(seg);
      });
      track.appendChild(stack); track.appendChild(el('span', 'val', dur(tot)));
      row.appendChild(track); wrap.appendChild(row);
    });
    return wrap;
  }
  function splitTable() {
    var rows = agentNames.map(function (n) {
      var a = A[n], tot = a.model_s + a.tool_s;
      return [agentLabel[n], dur(a.model_s), dur(a.tool_s), dur(tot)];
    });
    return table(['', S.model, S.tools, S.working], rows, ['l', 'r', 'r', 'r']);
  }

  function catRows() { return all.categories.filter(function (c) { return c.seconds >= 1; }); }
  function catChart() {
    var rows = catRows(), wrap = el('div'), max = rows.length ? rows[0].seconds : 1;
    rows.forEach(function (c) {
      var name = CN[c.category] || c.category;
      var row = el('div', 'row'); row.setAttribute('role', 'group');
      row.setAttribute('aria-label', name + ': ' + dur(c.seconds) + ' (' + pct(c.seconds, all.tool_s) + ')');
      row.appendChild(el('div', 'row-l', name));
      var track = el('div', 'track'), bar = el('div', 'bar bar-tool');
      bar.style.width = (c.seconds / max * 74) + '%';
      track.appendChild(bar); track.appendChild(el('span', 'val', dur(c.seconds) + ' · ' + pct(c.seconds, all.tool_s)));
      row.appendChild(track);
      bindTip(row, function (t) {
        tipTitle(t, name);
        tipRow(t, 'tool', dur(c.seconds), pct(c.seconds, all.tool_s) + ' · ' + c.count + ' ' + S.count);
        tipRow(t, 'none', c.median_s.toFixed(1) + 's', S.median);
        tipRow(t, 'none', c.p90_s.toFixed(1) + 's', S.p90);
        tipRow(t, 'none', dur(c.max_s), S.longest);
      });
      wrap.appendChild(row);
    });
    return wrap;
  }
  function catTable() {
    var rows = catRows().map(function (c) {
      return [CN[c.category] || c.category, String(c.count), dur(c.seconds), pct(c.seconds, all.tool_s), c.median_s.toFixed(1) + 's', c.p90_s.toFixed(1) + 's', dur(c.max_s)];
    });
    return table([S.cat, S.count, S.time, S.share, S.median, S.p90, S.longest], rows, ['l', 'r', 'r', 'r', 'r', 'r', 'r']);
  }

  var projRows = [];
  function select(i) {
    sel = i;
    projRows.forEach(function (b) { b.setAttribute('aria-pressed', String(+b.dataset.index === i)); });
    renderHero(); renderPerCat();
  }
  function projChart(indices) {
    projRows = [];
    var wrap = el('div'), gs = indices.map(function (i) { return range(targets[i]); });
    if (!gs.length) return wrap;
    var lo = Math.min(1, Math.min.apply(null, gs.map(function (g) { return g.lo; })));
    var hi = Math.max(lo + 0.1, Math.max.apply(null, gs.map(function (g) { return g.hi; })));
    var span = hi - lo, step = 5;
    [0.02, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5].some(function (s) { if (span / s <= 6) { step = s; return true; } return false; });
    var a0 = Math.floor((lo - span * 0.04) / step + 1e-9) * step, a1 = Math.ceil((hi + span * 0.04) / step - 1e-9) * step;
    function pos(v) { return (v - a0) / (a1 - a0) * 100; }
    var ticks = [];
    for (var v = a0; v <= a1 + 1e-9; v += step) ticks.push(Math.round(v * 1000) / 1000);
    var axis = el('div', 'axis'), at = el('div', 'axis-track');
    axis.appendChild(el('div'));
    ticks.forEach(function (tv) { var tk = el('span', 'tick', tv + 'x'); tk.style.left = pos(tv) + '%'; at.appendChild(tk); });
    axis.appendChild(at); axis.appendChild(el('div')); wrap.appendChild(axis);
    indices.forEach(function (i, pageIndex) {
      var t = targets[i], g = gs[pageIndex], b = el('button', 'prow'); b.type = 'button'; b.dataset.index = i; b.setAttribute('aria-pressed', String(i === sel));
      var l = el('div', 'row-l'); l.appendChild(el('span', 'nm', t.name)); l.appendChild(el('span', 'tier', t.tier));
      var track = el('div', 'track rtrack');
      ticks.forEach(function (tv) { var gl = el('span', 'gl' + (Math.abs(tv - 1) < 1e-6 ? ' base' : '')); gl.style.left = pos(tv) + '%'; track.appendChild(gl); });
      var line = el('span', 'rline'); line.style.left = pos(g.lo) + '%'; line.style.width = Math.max(0, pos(g.hi) - pos(g.lo)) + '%';
      var dot = el('span', 'rdot'); dot.style.left = pos(g.ex) + '%';
      track.appendChild(line); track.appendChild(dot);
      var vc = el('div', 'val-col'); vc.appendChild(el('strong', null, x2(g.ex)));
      vc.appendChild(el('span', null, x2(g.lo) + ' – ' + x2(g.hi)));
      if (g.hi < 1.05) vc.appendChild(el('span', 'flag', S.no_gain));
      b.appendChild(l); b.appendChild(track); b.appendChild(vc);
      b.setAttribute('aria-label', t.name + ': ' + x2(g.ex) + ' (' + x2(g.lo) + ' – ' + x2(g.hi) + ')');
      b.addEventListener('click', function () { select(i); });
      bindTip(b, function (tp) {
        tipTitle(tp, t.name + ' · CPU ' + x2(t.cpu_x_single) + ' / ' + x2(t.cpu_x_multi));
        tipRow(tp, 'none', x2(g.lo), S.cons); tipRow(tp, 'none', x2(g.ex), S.exp); tipRow(tp, 'none', x2(g.hi), S.opt);
      });
      projRows.push(b); wrap.appendChild(b);
    });
    wrap.appendChild(el('p', 'hint', S.range_hint));
    return wrap;
  }
  function projTable(indices) {
    var rows = indices.map(function (i) {
      var t = targets[i];
      var g = range(t), e = t.scenarios.expected;
      return [t.name, t.tier, x2(t.cpu_x_single), x2(t.cpu_x_multi), x2(e.tool_speedup), x2(g.lo), x2(g.ex), x2(g.hi), dur(e.saved_s)];
    });
    var result = table([S.target, S.tier, S.single_x, S.multi_x, S.tool_speedup, S.cons, S.exp, S.opt, S.saved], rows, ['l', 'l', 'r', 'r', 'r', 'r', 'r', 'r', 'r']);
    result.querySelectorAll('tbody tr').forEach(function (row, j) {
      var cell = row.firstChild, button = el('button', 'chip', targets[indices[j]].name);
      button.type = 'button'; button.addEventListener('click', function () { select(indices[j]); });
      cell.replaceChildren(button);
    });
    return result;
  }

  function browser(records, renderPage, prefix) {
    var root = el('div'), controls = el('div', 'filters'), body = el('div'), pager = el('div', 'pager');
    var search = el('input'), page = 0, size = 25, filters = [];
    search.type = 'search'; search.placeholder = S.search;
    function label(text, field) { var l = el('label', null, text); l.appendChild(field); controls.appendChild(l); }
    label(prefix + ' · ' + S.search, search);
    function filter(labelText, key) {
      var field = el('select'), values = new Set();
      records.forEach(function (r) { [].concat(r[key] || []).forEach(function (v) { values.add(v); }); });
      field.appendChild(el('option', null, S.all)); field.firstChild.value = '';
      Array.from(values).sort().forEach(function (v) { var o = el('option', null, v); o.value = v; field.appendChild(o); });
      label(labelText, field); filters.push({ field: field, key: key });
      field.addEventListener('change', function () { page = 0; draw(); });
    }
    filter(S.vendor, 'vendor'); filter(S.generation, 'generation'); filter(S.platform, 'platforms');
    if (records.some(function (r) { return r.score_status; })) filter(S.data_status, 'score_status');
    var prev = el('button', 'toggle', S.previous), next = el('button', 'toggle', S.next), count = el('span', 'hint');
    prev.type = next.type = 'button'; count.setAttribute('aria-live', 'polite');
    prev.addEventListener('click', function () { page--; draw(); });
    next.addEventListener('click', function () { page++; draw(); });
    search.addEventListener('input', function () { page = 0; draw(); });
    pager.appendChild(prev); pager.appendChild(count); pager.appendChild(next);
    root.appendChild(controls); root.appendChild(pager); root.appendChild(body);
    function draw() {
      var words = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean), matches = [];
      records.forEach(function (r, i) {
        var text = [r.name, r.generation, r.source_section || ''].join(' ').toLowerCase();
        if (words.every(function (w) { return text.includes(w); }) && filters.every(function (f) {
          return !f.field.value || [].concat(r[f.key] || []).includes(f.field.value);
        })) matches.push(i);
      });
      var start = page * size;
      prev.disabled = page === 0; next.disabled = start + size >= matches.length;
      count.textContent = fmt(S.page_count, { first: matches.length ? start + 1 : 0, last: Math.min(start + size, matches.length), total: matches.length });
      body.replaceChildren(renderPage(matches.slice(start, start + size)));
    }
    draw(); return root;
  }

  var perTitle, perBox;
  function renderPerCat() {
    var t = targets[sel], e = t.scenarios.expected;
    perTitle.textContent = S.per_cat_title + ' · ' + t.name;
    var rows = Object.keys(e.per_category).map(function (k) { return { k: k, o: e.per_category[k].old_s, n: e.per_category[k].new_s }; })
      .filter(function (r) { return r.o >= 1; }).sort(function (a, b) { return b.o - a.o; });
    var body = [[S.model_row, dur(all.model_s), dur(all.model_s), '0%']];
    rows.forEach(function (r) { body.push([CN[r.k] || r.k, dur(r.o), dur(r.n), chg(r.o, r.n)]); });
    body.push([S.total_row, dur(e.total_old_s), dur(e.total_new_s), chg(e.total_old_s, e.total_new_s)]);
    perBox.replaceChildren(table([S.cat, S.before, S.after, S.change], body, ['l', 'r', 'r', 'r'], true));
    if (t.score_status === 'cpu-reference-gb6') perBox.appendChild(el('p', 'hint', S.mac_reference));
  }
  function renderHero() {
    var t = targets[sel], g = range(t), e = t.scenarios.expected;
    $('#hero-lead').textContent = fmt(S.hero_lead, { name: t.name });
    $('#hero-num').textContent = x2(g.ex);
    $('#hero-sub').textContent = fmt(S.hero_sub, { lo: x2(g.lo), hi: x2(g.hi), saved: dur(e.saved_s), tool: x2(e.tool_speedup) });
  }

  var hw = R.hardware, B = R.baseline;
  document.title = S.title;
  $('#brand-name').textContent = S.title;
  $('#nav-meta').textContent = hw.cpu_name;
  $('#pill').textContent = fmt(S.pill, { n: all.sessions, a: R.period.first, b: R.period.last });

  var sw = $('#switch');
  var choose = el('a', 'chip', S.choose_target); choose.href = '#comparisons'; sw.appendChild(choose);

  var stats = $('#stats');
  function stat(v, l) { var d = el('div'); d.appendChild(el('div', 'stat-v', v)); d.appendChild(el('div', 'stat-l', l)); stats.appendChild(d); }
  stat(pct(all.model_s, working), fmt(S.stat_model_cap, { t: dur(all.model_s), work: dur(working) }));
  stat(dur(all.tool_s), S.tools + ' · ' + fmt(S.stat_tool_cap, { p: pct(all.tool_s, working) }));
  stat(dur(R.sensitive_expected_s), S.sens_title + ' · ' + S.sens_hint);

  var app = $('#app');

  var p = section(S.proj_title, S.e2e_note);
  p.root.id = 'comparisons';
  var pc = card(null, null), tableMode = false, projectionBody;
  var view = el('button', 'toggle', S.table_view); view.type = 'button'; view.setAttribute('aria-pressed', 'false');
  pc.head.appendChild(view);
  pc.root.appendChild(browser(targets, function (indices) {
    projectionBody = el('div'); projectionBody.appendChild(projChart(indices)); projectionBody.appendChild(projTable(indices));
    projectionBody.children[0].hidden = tableMode; projectionBody.children[1].hidden = !tableMode;
    return projectionBody;
  }, S.proj_title));
  view.addEventListener('click', function () {
    tableMode = !tableMode; view.textContent = tableMode ? S.chart_view : S.table_view; view.setAttribute('aria-pressed', String(tableMode));
    projectionBody.children[0].hidden = tableMode; projectionBody.children[1].hidden = !tableMode;
  });
  p.root.appendChild(pc.root);
  var per = card(' ', null); perTitle = per.root.querySelector('h3');
  perBox = el('div'); per.root.appendChild(perBox);
  per.root.style.marginTop = '16px';
  p.root.appendChild(per.root);
  app.appendChild(p.root);

  if (R.catalog) {
    var inventory = R.catalog.cpus, cat = section(S.catalog_title, S.catalog_note), catCard = card(null, null);
    catCard.root.appendChild(el('p', 'card-sub', fmt(S.catalog_count, { total: inventory.length, scored: inventory.filter(function (c) { return c.gb6_single; }).length, targets: targets.length, date: R.catalog.as_of })));
    catCard.root.appendChild(browser(inventory, function (indices) {
      var rows = indices.map(function (i) { var c = inventory[i]; return [c.name, c.generation, (c.platforms || []).join(', '), c.score_status, c.gb6_single ? c.gb6_single + ' / ' + c.gb6_multi : '—', '']; });
      var result = table([S.target, S.generation, S.platform, S.data_status, 'Geekbench 6', S.source], rows, ['l','l','l','l','r','l']);
      result.querySelectorAll('tbody tr').forEach(function (row, j) {
        var c = inventory[indices[j]], url = c.source_url || (c.source_urls || [])[0];
        if (url && /^https:\/\//.test(url)) { var link = el('a', null, S.source); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; row.lastChild.appendChild(link); }
      });
      return result;
    }, S.catalog_title));
    cat.root.appendChild(catCard.root); app.appendChild(cat.root);
  }

  var w = section(S.time_title, S.model_note);
  var sc = card(S.split_title, null), sChart = splitChart(), sTbl = splitTable();
  withToggle(sc.head, sChart, sTbl); sc.root.appendChild(sChart); sc.root.appendChild(sTbl);
  var mc = card(S.machine_title, null), dl = el('dl');
  var srcName = { table: S.src_table, proxy: S.src_proxy, estimated: S.src_estimated, manual: S.src_manual }[B.source] || B.source;
  [[S.m_cpu, hw.cpu_name], [S.m_threads, hw.cores + ' / ' + hw.threads], [S.m_ram, hw.ram_gb + ' GB'],
   [S.m_disk, S['disk_' + hw.disk_class] || hw.disk_class], [S.m_score, B.gb6_single + ' / ' + B.gb6_multi],
   [S.m_source, srcName + (B.proxy ? ' · ' + B.proxy : '')]].forEach(function (r) {
    dl.appendChild(el('dt', null, r[0])); dl.appendChild(el('dd', null, r[1]));
  });
  mc.root.appendChild(dl);
  mc.root.style.marginTop = '16px';
  w.root.appendChild(sc.root); w.root.appendChild(mc.root);
  app.appendChild(w.root);

  var cs = section(S.cat_title, null);
  var cc = card(null, null), cChart = catChart(), cTbl = catTable();
  withToggle(cc.head, cChart, cTbl); cc.root.appendChild(cChart); cc.root.appendChild(cTbl);
  cs.root.appendChild(cc.root);
  app.appendChild(cs.root);

  var ns = section(S.caveat_title, null);
  var g3 = el('div', 'grid2');
  var nw = card(S.not_work_title, null), ndl = el('dl');
  [[S.human, all.human_s], [S.idle, all.idle_s], [S.background, all.background_s], [S.stalled, all.stalled_s]].forEach(function (r) {
    ndl.appendChild(el('dt', null, r[0])); ndl.appendChild(el('dd', null, dur(r[1])));
  });
  nw.root.appendChild(ndl);
  var nc = card(S.assume_title, null), ul = el('ul', 'notes');
  R.notes.forEach(function (n) { ul.appendChild(el('li', null, n)); });
  nc.root.appendChild(ul);
  g3.appendChild(nc.root); g3.appendChild(nw.root);
  ns.root.appendChild(g3);
  app.appendChild(ns.root);

  $('#foot').textContent = S.generated.replace('{v}', R.version);
  renderHero(); renderPerCat(); fitLabels(document);
  if (window.ResizeObserver) {
    new ResizeObserver(function () { fitLabels(document); }).observe(document.getElementById('app'));
  } else {
    window.addEventListener('resize', function () { fitLabels(document); });
  }
})();
"""

_PAGE = r"""<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body class="viz-root">
<div class="wrap">
  <nav class="top"><span class="brand"><span class="brand-mark" aria-hidden="true">✱</span><span id="brand-name"></span></span><span class="nav-meta" id="nav-meta"></span></nav>
  <header class="hero">
    <span class="pill" id="pill"></span>
    <p class="hero-lead" id="hero-lead"></p>
    <div class="hero-num" id="hero-num"></div>
    <p class="hero-sub" id="hero-sub"></p>
    <div class="switch" id="switch" role="group"></div>
  </header>
  <section class="stats" id="stats"></section>
  <main id="app"></main>
  <footer id="foot"></footer>
</div>
<div id="tip" role="tooltip" hidden></div>
<script type="application/json" id="data">__DATA__</script>
<script>__JS__</script>
</body>
</html>
"""


def render_html(r: dict, lang: str) -> str:
    s = strings(lang)
    payload = {"r": r, "S": s, "cats": r["cat_names"]}
    data = (
        json.dumps(payload, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    page = _PAGE.replace("__LANG__", "zh-CN" if lang == "zh" else "en")
    page = page.replace("__TITLE__", html.escape(s["title"]))
    page = page.replace("__CSS__", _CSS).replace("__JS__", _JS)
    return page.replace("__DATA__", data)
