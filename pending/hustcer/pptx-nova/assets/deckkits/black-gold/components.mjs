// Shared editorial composition compiler; no publication-specific facts or physical color names.
import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { resolveEditorialDeck } from './layouts.mjs'

export const ledgerNumber = (n) => {
  if (!Number.isFinite(n)) throw new Error('Finite numeric value required')
  const value =
    Math.abs(n) !== 0 && Math.abs(n) < 0.000001
      ? String(Math.abs(n))
      : new Intl.NumberFormat('en-US', { maximumFractionDigits: 20 }).format(Math.abs(n))
  return n < 0 ? `(${value})` : value
}

export function createEditorialDeck(design, content) {
  const resolved = resolveEditorialDeck(design, content)
  const p = createOps({ textbox: design.textFrame })
  p.ops.push(designTheme(design))
  const e = design.editorial,
    t = e.typography
  const color = (token) => design.colors[token]
  const c = {
    surface: color(design.roles.surface),
    text: color(design.roles.text),
    focus: color(design.roles.focus),
    ...Object.fromEntries(Object.entries(e.contrast).map(([k, v]) => [k, color(v)])),
  }
  for (const [s, slide] of content.slides.entries()) {
    const d = slide.data,
      layout = resolved.layouts[s],
      role = layout.role,
      dark = layout.mode === 'dark',
      r = layout.frame.regions
    const fg = dark ? c.onDark : c.text,
      muted = dark ? c.history : c.muted
    const nm = (base) => `S${s}_${base}`
    const tx = (base, frame, value, size = t.body, extra = {}) => {
      value = String(value)
      const text = wrapCjkText(value, Math.max(1, (((frame[2] - 0.02) * 72) / size) * 0.94))
      p.textbox(s, nm(base), ...frame)
      p.setText(s, nm(base), text)
      for (let i = 0; i < text.split(/\r\n|\r|\n/).length; i++) {
        p.runFont(s, nm(base), designFont(design, 'body', size, { color: fg, ...extra }), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name: nm(base) },
          paragraph: i,
          format: { lineSpacing: 1.12, spaceAfter: '0pt' },
        })
      }
    }
    const box = (base, frame, fill) => p.box(s, nm(base), 'rectangle', ...frame, fill)
    const rule = (base, x, y, w, fill = c.hairline) => box(base, [x, y, w, 0.008], fill)
    const metric = (base, m, [x, y, w, h]) => {
      tx(`${base}Value`, [x, y, w, 0.62], m.value, t.metric, {
        color: m.focus ? c.focus : fg,
        bold: true,
      })
      tx(`${base}Label`, [x, y + 0.64, w, 0.34], m.label, t.label, { bold: true })
      tx(`${base}Basis`, [x, y + 1.02, w, Math.max(0.36, h - 1.02)], m.basis, t.label, {
        color: muted,
      })
    }
    const note = (base, n, [x, y, w, h]) => {
      tx(`${base}Heading`, [x, y, w, 0.38], n.heading, t.body, { bold: true })
      tx(`${base}Body`, [x, y + 0.45, w, Math.max(0.52, h - 0.45)], n.body, t.body, {
        color: muted,
      })
    }
    const notes = (items, region, vertical = false) => {
      const [x, y, w, h] = region,
        gap = 0.3
      items.forEach((n, i) => {
        const nw = vertical ? w : (w - gap * (items.length - 1)) / items.length,
          nh = vertical ? (h - gap * (items.length - 1)) / items.length : h
        if (!vertical && i)
          rule(`NoteDivider${i}`, x + i * (nw + gap) - gap / 2, y, 0.008, c.hairline)
        note(`Note${i}`, n, [
          x + (vertical ? 0 : i * (nw + gap)),
          y + (vertical ? i * (nh + gap) : 0),
          nw,
          nh,
        ])
      })
    }
    const chart = (base, data, region) => {
      const [x, y, w, h] = region
      tx(`${base}Caption`, [x, y, w, 0.23], `${data.name} · ${data.unit}`, t.label, {
        color: c.muted,
      })
      p.ops.push({
        op: 'add-chart',
        slide: s,
        name: nm(base),
        kind: data.kind,
        x: `${x}in`,
        y: `${y + 0.3}in`,
        w: `${w}in`,
        h: `${h - 0.3}in`,
        data: {
          categories: data.categories,
          series: [{ name: `${data.name} (${data.unit})`, values: data.values }],
        },
      })
      const line = data.kind === 'line',
        primary = c.primary,
        font = designFont(design, 'body', e.chart.labelPt, { color: c.muted })
      const series = {
        series: 0,
        fill: { type: 'solid', color: line ? primary : c.history },
        line: { color: primary, width: line ? `${e.chart.linePt}pt` : '0pt' },
        ...(line
          ? {
              smooth: false,
              marker: { symbol: 'circle', size: e.chart.markerPt, fill: primary, line: primary },
            }
          : { invertIfNegative: false }),
      }
      if (!line && data.focus === undefined)
        series.points = [
          {
            point: data.kind === 'bar' ? 0 : data.values.length - 1,
            fill: { type: 'solid', color: primary },
            line: { width: '0pt', color: primary },
          },
        ]
      if (data.focus !== undefined)
        series.points = [
          {
            point: data.focus,
            ...(line
              ? {
                  marker: {
                    symbol: 'circle',
                    size: e.chart.markerPt + 3,
                    fill: c.focus,
                    line: c.focus,
                  },
                }
              : {
                  fill: { type: 'solid', color: primary },
                  line: { width: `${e.chart.focusLinePt}pt`, color: c.focus },
                }),
          },
        ]
      p.ops.push({
        op: 'set-chart',
        slide: s,
        shape: { name: nm(base) },
        series: [series],
        axes: [
          {
            axis: 'category',
            ...(data.kind === 'bar' ? { scale: { reverseOrder: true } } : {}),
            line: { color: c.hairline, width: '0.5pt' },
            ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
          },
          {
            axis: 'value',
            line: { color: c.surface, width: '0pt' },
            gridlines: null,
            minorGridlines: null,
            ticks: { visible: false, major: 'none', minor: 'none' },
          },
        ],
        dataLabels: [
          {
            showValue: true,
            showLegendKey: false,
            showSeriesName: false,
            position: line ? 'above' : 'outside-end',
            numberFormat: data.numberFormat ?? 'General',
            font,
          },
        ],
        ...(line ? {} : { plot: { gapWidth: e.chart.gap } }),
      })
    }
    p.addSlide(s, dark ? c.darkSurface : c.surface)
    tx('Footer', e.chrome.footer, `${d.source} · ${d.asOf} · ${d.unit}`, t.source, { color: muted })
    tx('Page', e.chrome.page, `${s + 1} / ${content.slides.length}`, t.source, { color: muted })
    if (role === 'cover') {
      tx('Masthead', [0.73, 0.48, 8, 0.25], d.masthead, t.label, { color: c.muted })
      tx('PublicationDate', [10.1, 0.48, 2.5, 0.25], d.date, t.label, { color: c.muted })
      box('AccentRule', [0.73, 1.48, 0.65, 0.04], c.focus)
      tx('Watermark', r.watermark, d.watermark, t.watermark, { color: c.watermark })
      tx('CoverTitle', r.title, d.title, t.cover, { bold: true })
      tx('Abstract', r.abstract, d.abstract, t.body, { color: c.muted })
      d.metrics.forEach((m, i) =>
        metric(`CoverMetric${i}`, m, [r.metrics[0] + i * 3.15, r.metrics[1], 2.85, 1.35]),
      )
      box('BasisBand', r.band, c.text)
      tx(
        'Disclosure',
        [r.band[0] + 0.13, r.band[1] + 0.07, r.band[2] - 0.26, r.band[3] - 0.12],
        d.disclosure,
        t.source,
        { color: c.onDark },
      )
    } else {
      if (!dark) box('TopRule', e.chrome.topRule, c.text)
      else tx('Eyebrow', [0.73, 0.4, 11.8, 0.22], d.label, t.label, { color: c.hairline })
      tx('Title', e.chrome.title, d.title, t.title, { bold: true })
      tx('Basis', e.chrome.basis, `${d.basis} · ${d.asOf} · ${d.unit}`, t.label, { color: muted })
      if (role === 'summary') {
        d.judgments.forEach((n, i) => {
          const y = r.main[1] + i * 1.22
          tx(`Number${i}`, [r.main[0], y, 0.55, 0.5], String(i + 1).padStart(2, '0'), 24, {
            color: c.hairline,
          })
          note(`Judgment${i}`, n, [r.main[0] + 0.78, y, r.main[2] - 0.78, 1.02])
          if (i < 2) rule(`JudgmentRule${i}`, r.main[0], y + 1.08, r.main[2], c.darkRule)
        })
        box('RailRule', [8.65, 2.08, 0.008, 3.85], c.darkRule)
        d.metrics.forEach((m, i) =>
          metric(`SummaryMetric${i}`, m, [r.side[0], r.side[1] + i * 1.35, r.side[2], 1.25]),
        )
      } else if (role === 'trend') {
        if (d.secondary) {
          const [x, y, w, h] = r.main
          chart('SecondaryChart', { ...d.secondary, categories: d.chart.categories }, [
            x,
            y,
            w,
            h * 0.44,
          ])
          chart('MainChart', d.chart, [x, y + h * 0.46, w, h * 0.54])
        } else chart('MainChart', d.chart, r.main)
        notes(d.notes, r.detail, layout.layoutId === 'rail')
        if (d.support) chart('SupportChart', d.support, r.support)
      } else if (role === 'ranking') {
        chart('MainChart', d.chart, r.main)
        const horizontal = layout.layoutId === 'wide'
        const [x, y, w] = r.side
        d.metrics.forEach((m, i) =>
          metric(
            `RankingMetric${i}`,
            m,
            horizontal
              ? [x + (i * w) / d.metrics.length, y, w / d.metrics.length - 0.3, 1.2]
              : [x, y + i * 1.38, w, 1.3],
          ),
        )
      } else if (role === 'matrix') {
        const data = [
          d.headers,
          ...d.rows.map((row) => [
            row.name,
            ledgerNumber(row.amount),
            `${ledgerNumber(row.share)}%`,
            row.representative,
            row.thesis,
          ]),
        ]
        const [x, y, w, h] = r.main,
          widths = [0.2, 0.12, 0.2, 0.23, 0.25].map((v) => v * w),
          rowH = h / data.length
        p.ops.push({
          op: 'add-table',
          slide: s,
          name: nm('Matrix'),
          rows: data.length,
          columns: 5,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data,
        })
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name: nm('Matrix') },
          style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
          rows: data.map((_, row) => ({ row, height: `${rowH}in` })),
          columns: widths.map((width, column) => ({ column, width: `${width}in` })),
          cells: data.flatMap((row, i) =>
            row.map((_, j) => ({
              row: i,
              column: j,
              style: {
                fill: { type: 'solid', color: c.surface },
                font: designFont(design, 'body', i === 0 ? t.label : t.body, {
                  color: i === 0 ? c.muted : c.text,
                  bold: i === 0 || j === 1,
                }),
                alignment: j === 1 || j === 2 ? 'right' : 'left',
                verticalAnchor: 'middle',
                marginLeft: '3pt',
                marginRight: '5pt',
                marginTop: '4pt',
                marginBottom: '4pt',
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: c.hairline, width: '0.5pt' },
                },
              },
            })),
          ),
        })
        d.rows.forEach((row, i) => {
          const px = x + widths[0] + widths[1] + 0.12,
            py = y + rowH * (i + 1.78),
            pw = widths[2] - 0.24
          box(`ShareTrack${i}`, [px, py, pw, 0.055], c.panel)
          if (row.share > 0) box(`ShareBar${i}`, [px, py, (pw * row.share) / 100, 0.055], c.primary)
        })
        tx('MatrixTotal', [0.73, 6.16, 11.87, 0.23], d.totalLabel, t.label, { bold: true })
      } else if (role === 'decision') {
        const rowH = r.main[3] / 3
        d.actions.forEach((a, i) => {
          const y = r.main[1] + i * rowH
          box(`ActionBand${i}`, [r.main[0], y, r.main[2], rowH - 0.13], c.panel)
          tx(`Observation${i}`, [0.9, y + 0.17, 2.72, 0.65], a.observation, t.body, {
            color: c.text,
            bold: true,
          })
          if (a.focus) box(`ThresholdFocus${i}`, [3.96, y + 0.18, 3.3, 0.65], c.focus)
          tx(`Threshold${i}`, [4.08, y + 0.24, 3.05, 0.56], a.threshold, t.body, {
            color: c.text,
            bold: true,
          })
          tx(`Action${i}`, [7.7, y + 0.18, 4.65, 0.76], a.action, t.body, { color: c.text })
        })
        tx('Decision', [0.73, 6.16, 11.87, 0.3], d.decision, t.body, { bold: true })
      }
      if (!dark) box('VerdictBand', e.chrome.verdict, c.panel)
      tx(
        'Verdict',
        [e.chrome.verdict[0] + 0.08, e.chrome.verdict[1] + 0.04, e.chrome.verdict[2] - 0.16, 0.28],
        d.verdict,
        t.label,
        { bold: true },
      )
    }
  }
  const result = finishDesign(
    design,
    content,
    { schemaVersion: 'pptx-patch/v1', ops: p.ops },
    resolved.layouts,
  )
  result.warnings = resolved.warnings
  result.designPlan.rhythm = resolved.rhythm
  result.designPlan.implementation = {
    renderer: e.renderer,
    table: 'native',
    dualTrend: 'aligned-native-charts',
    unverified: ['gold pixel area', 'effective theme inheritance', 'PowerPoint parity'],
  }
  return result
}
