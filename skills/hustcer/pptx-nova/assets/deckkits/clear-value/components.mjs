import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { resolveAnnualDeck, annualNumber, annualChartLegend } from './layouts.mjs'
export { annualNumber } from './layouts.mjs'
export function createAnnualDeck(design, content) {
  const resolved = resolveAnnualDeck(design, content),
    p = createOps({ textbox: design.textFrame }),
    a = design.annual,
    t = a.typography,
    c = Object.fromEntries(
      Object.entries(a.palette).map(([role, token]) => [role, design.colors[token]]),
    )
  p.ops.push(designTheme(design))
  for (const [s, slide] of content.slides.entries()) {
    const d = slide.data,
      l = resolved.layouts[s],
      r = l.frame.regions,
      nm = (x) => `S${s}_${x}`
    const tx = (name, f, value, pt = t.body, opt = {}, role = 'body') => {
      const text = wrapCjkText(String(value), Math.max(1, (((f[2] - 0.04) * 72) / pt) * 0.94))
      p.textbox(s, nm(name), ...f)
      p.setText(s, nm(name), text)
      for (let i = 0; i < text.split('\n').length; i++) {
        p.runFont(s, nm(name), designFont(design, role, pt, { color: c.ink, ...opt }), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name: nm(name) },
          paragraph: i,
          format: { lineSpacing: 1.12, spaceAfter: '0pt' },
        })
      }
    }
    const box = (name, f, color) => p.box(s, nm(name), 'rectangle', ...f, color)
    const rule = (name, x, y, w, color = c.history) => box(name, [x, y, w, 0.009], color)
    const note = (name, n, [x, y, w, h]) => {
      if (n.emphasis) box(name + 'Tick', [x - 0.08, y + 0.03, 0.02, 0.23], c.terracotta)
      tx(name + 'Heading', [x, y, w, 0.34], n.heading, t.body, {
        bold: true,
        ...(n.emphasis ? { color: c.terracotta } : {}),
      })
      tx(name + 'Body', [x, y + 0.4, w, h - 0.4], n.body, t.body, { color: c.muted })
    }
    const table = (name, [x, y, w, h]) => {
      const data = [
          d.columns.map((x) => x.heading),
          ...d.rows.map((x) => x.cells.map((v) => v.text)),
        ],
        total = d.columns.reduce((n, x) => n + x.weight, 0),
        rh = h / data.length
      p.ops.push({
        op: 'add-table',
        slide: s,
        name: nm(name),
        rows: data.length,
        columns: d.columns.length,
        x: `${x}in`,
        y: `${y}in`,
        w: `${w}in`,
        h: `${h}in`,
        data,
      })
      p.ops.push({
        op: 'set-table',
        slide: s,
        shape: { name: nm(name) },
        style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
        columns: d.columns.map((col, column) => ({
          column,
          width: `${(w * col.weight) / total}in`,
        })),
        rows: data.map((_, row) => ({ row, height: `${rh}in` })),
        cells: data.flatMap((row, i) =>
          row.map((_, j) => ({
            row: i,
            column: j,
            style: {
              fill: { type: 'solid', color: c.paper },
              font: designFont(design, 'body', i ? t.body : t.label, {
                color:
                  i && d.rows[i - 1].cells[j].tone === 'positive'
                    ? c.deep
                    : i && d.rows[i - 1].cells[j].tone === 'negative'
                      ? c.ink
                      : i
                        ? c.ink
                        : c.muted,
                bold: !!i && d.rows[i - 1].cells[j].tone !== 'normal',
              }),
              alignment: d.columns[j].align,
              verticalAnchor: 'middle',
              marginLeft: '4pt',
              marginRight: '5pt',
              marginTop: '4pt',
              marginBottom: '4pt',
              borders: {
                top: { noLine: true },
                left: { noLine: true },
                right: { noLine: true },
                bottom: { color: i === 0 ? c.ink : c.history, width: i === 0 ? '1pt' : '0.5pt' },
              },
            },
          })),
        ),
      })
    }
    const fig = (ch, i, [x, y, w, h]) => {
      tx(`Fig${i}Number`, [x, y, 0.52, 0.27], ch.label, t.label, { color: c.muted })
      tx(`Fig${i}Title`, [x + 0.58, y, w - 0.58, 0.38], ch.name, t.figure, {}, 'display')
      tx(`Fig${i}Basis`, [x, y + 0.42, w, 0.25], `${ch.basis} · ${ch.unit}`, t.source, {
        color: c.muted,
      })
      const fy = y + 0.82,
        fh = h - 0.82
      if (ch.kind === 'circles') {
        tx(`Fig${i}Series`, [x, y + 0.68, w, 0.2], ch.series[0].name, t.source, { color: c.muted })
        const max = Math.max(...ch.series[0].values),
          diam = Math.min(fh - 0.65, w * 0.38)
        ch.series[0].values.forEach((v, j) => {
          const size = diam * Math.sqrt(v / max),
            cx = x + w * (j ? 0.73 : 0.25),
            cy = fy + (fh - 0.55) / 2
          const large = j === 1 && v / ch.series[0].values.reduce((n, x) => n + x, 0) > 1 / 3
          if (size > 0)
            p.box(
              s,
              nm(`Circle${i}_${j}`),
              'oval',
              cx - size / 2,
              cy - size / 2,
              size,
              size,
              j ? (large ? c.paper : c.teal) : c.history,
            )
          if (large && size > 0)
            p.ops.push({
              op: 'set-shape',
              slide: s,
              shape: { name: nm(`Circle${i}_${j}`) },
              line: { color: c.teal, width: '1.4pt' },
            })
          tx(
            `Circle${i}Label${j}`,
            [cx - w * 0.22, fy + fh - 0.45, w * 0.44, 0.35],
            `${ch.categories[j]} · ${annualNumber(v)}`,
            t.label,
            { color: c.ink },
          )
        })
        return
      }
      const name = nm(`Chart${i}`),
        kind = ch.kind === 'donut' ? 'doughnut' : ch.kind,
        stacked = ch.variant === 'stacked',
        line = kind === 'line',
        total = ch.series.reduce((n, ss) => n + ss.values.reduce((v, x) => v + Math.abs(x), 0), 0)
      p.ops.push({
        op: 'add-chart',
        slide: s,
        name,
        kind,
        ...(stacked ? { variant: 'stacked' } : {}),
        x: `${x}in`,
        y: `${fy}in`,
        w: `${w}in`,
        h: `${fh}in`,
        data: {
          categories: ch.categories,
          series: ch.series.map(({ name, values }) => ({ name, values })),
        },
      })
      const font = designFont(design, 'body', t.label, { color: c.ink }),
        tones = { current: c.teal, secondary: c.deep, history: c.history, negative: c.sand }
      const styles = ch.series.map((ss, j) => {
        const color = tones[ss.tone],
          share = ss.values.reduce((v, x) => v + Math.abs(x), 0) / (total || 1),
          outline = !line && ss.tone === 'current' && share > 1 / 3
        return {
          series: j,
          fill: {
            type: 'solid',
            color: outline || (stacked && ss.tone === 'secondary') ? c.paper : color,
          },
          line: {
            color,
            width: line
              ? '1.6pt'
              : outline || (stacked && ss.tone === 'secondary')
                ? '1.4pt'
                : '0pt',
          },
          ...(line
            ? { smooth: false, marker: { symbol: 'circle', size: 3, fill: color, line: color } }
            : kind === 'doughnut'
              ? {}
              : { invertIfNegative: false }),
        }
      })
      // One-series bars keep history gray; only the authored focus point is current.
      if (!line && ch.series.length === 1 && kind !== 'doughnut') {
        styles[0].fill = { type: 'solid', color: c.history }
        styles[0].line = { color: c.history, width: '0pt' }
        if (ch.focus !== undefined) {
          const big = Math.abs(ch.series[0].values[ch.focus]) / (total || 1) > 1 / 3
          styles[0].points = [
            {
              point: ch.focus,
              fill: { type: 'solid', color: big ? c.paper : c.teal },
              line: { color: c.teal, width: big ? '1.4pt' : '0pt' },
            },
          ]
        }
      }
      if (ch.forecastFrom !== undefined)
        styles[0].points = ch.categories.map((_, j) => ({
          point: j,
          fill: { type: 'solid', color: j > ch.forecastFrom ? c.paper : c.history },
          line: {
            color: j > ch.forecastFrom ? c.teal : c.history,
            width: j > ch.forecastFrom ? '1.4pt' : '0pt',
            ...(j > ch.forecastFrom ? { dash: 'dash' } : {}),
          },
        }))
      if (kind === 'doughnut')
        styles[0].points = ch.categories.map((_, j) => {
          const focused = j === ch.focus,
            large = focused && ch.series[0].values[j] / total > 1 / 3
          return {
            point: j,
            fill: { type: 'solid', color: focused ? (large ? c.paper : c.teal) : c.history },
            line: { color: focused ? c.teal : c.paper, width: focused ? '1.4pt' : '1pt' },
          }
        })
      p.ops.push({
        op: 'set-chart',
        slide: s,
        shape: { name },
        series: styles,
        ...(kind === 'doughnut'
          ? {}
          : {
              axes: [
                {
                  axis: 'category',
                  ...(kind === 'bar' ? { scale: { reverseOrder: true } } : {}),
                  line: { color: c.history, width: '0.5pt' },
                  ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
                },
                {
                  axis: 'value',
                  line: { color: c.paper, width: '0pt' },
                  gridlines: null,
                  minorGridlines: null,
                  ticks: { visible: line, font, major: 'none', minor: 'none' },
                },
              ],
            }),
        dataLabels: [
          {
            showValue: !line,
            showSeriesName: false,
            showLegendKey: false,
            showCategoryName: kind === 'doughnut',
            // Office rejects explicit doughnut label positions, including center.
            // Keep visibility/font/format and let the host choose default placement.
            ...(kind === 'doughnut'
              ? {}
              : { position: line ? 'above' : stacked ? 'center' : 'outside-end' }),
            font,
            numberFormat: ch.numberFormat ?? 'General',
          },
        ],
        ...(kind === 'doughnut' ? { plot: { holeSize: 62, firstSliceAngle: 270 } } : {}),
        ...(['bar', 'column'].includes(kind)
          ? { plot: { gapWidth: 80, ...(stacked ? { overlap: 100 } : {}) } }
          : {}),
      })
      // Legend is direct text next to the chart head; no hidden default legend dependency.
      const legend = annualChartLegend(ch)
      tx(`Fig${i}Series`, [x, y + 0.68, w, 0.2], legend, t.source, { color: c.muted })
    }
    p.addSlide(s, c.paper)
    box('TopRule', l.role === 'cover' ? [4.13, 0.32, 8.55, 0.045] : a.chrome.topRule, c.ink)
    rule('FooterRule', 0.65, 6.79, 12.03)
    tx('Footer', a.chrome.footer, `${d.source} · ${d.asOf}`, t.source, { color: c.muted })
    tx(
      'Page',
      a.chrome.page,
      `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
      t.source,
      { color: c.muted },
    )
    if (l.role === 'cover') {
      tx('Masthead', [0.8, 0.65, 11.7, 0.3], d.basis, t.label, { color: c.muted })
      tx('CoverTitle', r.title, d.title, t.cover, {}, 'display')
      tx('Abstract', r.abstract, d.abstract, 18, {}, 'display')
      const [x, y, w, h] = r.metrics,
        cw = w / d.metrics.length
      rule('MetricRule', x, y - 0.25, w)
      d.metrics.forEach((m, i) => {
        const xx = x + i * cw
        box(`MetricTick${i}`, [xx, y + 0.04, 0.025, 1.05], c.terracotta)
        tx(`Metric${i}Value`, [xx + 0.16, y, cw - 0.25, 0.56], m.value, t.metric, {}, 'display')
        tx(`Metric${i}Label`, [xx + 0.16, y + 0.65, cw - 0.25, 0.3], m.label, t.label)
        tx(`Metric${i}Detail`, [xx + 0.16, y + 1, cw - 0.25, h - 1], m.detail, t.source, {
          color: c.muted,
        })
      })
    } else {
      tx('Title', a.chrome.title, d.title, t.title, {}, 'display')
      tx('Basis', a.chrome.basis, d.basis, t.label, { color: c.muted })
      if (l.role === 'summary' || l.role === 'decision') {
        const items = d.items,
          [x, y, w, h] = r.main,
          rh = h / items.length
        items.forEach((n, i) => {
          tx(
            `Item${i}Number`,
            [x, y + i * rh, 0.5, 0.5],
            String(i + 1).padStart(2, '0'),
            22,
            { color: l.role === 'decision' ? c.terracotta : c.deep },
            'display',
          )
          note(`Item${i}`, n, [x + 0.73, y + i * rh, w - 0.73, rh - 0.16])
          if (i) rule(`ItemRule${i}`, x + 0.73, y + i * rh - 0.12, w - 0.73)
        })
        box('RailRule', [r.side[0] - 0.22, r.side[1], 0.008, r.side[3]], c.history)
        const side = d.side,
          sh = r.side[3] / side.length
        side.forEach((n, i) => {
          const yy = r.side[1] + i * sh
          tx(
            `Side${i}Value`,
            [r.side[0], yy, r.side[2], 0.58],
            n.value,
            l.role === 'summary' ? t.metric : 19,
            { color: n.focus ? c.deep : c.ink },
            'display',
          )
          tx(`Side${i}Label`, [r.side[0], yy + 0.65, r.side[2], sh - 0.8], n.label, t.label, {
            color: c.muted,
          })
          if (i) rule(`SideRule${i}`, r.side[0], yy - 0.12, r.side[2])
        })
      } else if (l.role === 'evidence') {
        d.charts.forEach((ch, i) => fig(ch, i, r[`chart${i}`]))
        const vertical = l.layoutId === 'rail',
          gap = 0.2,
          nh = (r.detail[3] - gap * ((d.notes ?? []).length - 1)) / (d.notes ?? []).length,
          nw = (r.detail[2] - 0.3 * ((d.notes ?? []).length - 1)) / (d.notes ?? []).length
        ;(d.notes ?? []).forEach((n, i) =>
          note(
            `Note${i}`,
            n,
            vertical
              ? [r.detail[0], r.detail[1] + i * (nh + gap), r.detail[2], nh]
              : [r.detail[0] + i * (nw + 0.3), r.detail[1], nw, r.detail[3]],
          ),
        )
      } else if (l.role === 'matrix' || l.role === 'composite' || l.role === 'timeline') {
        if (l.role === 'matrix') {
          tx('TableName', [r.main[0], r.main[1] - 0.28, r.main[2], 0.25], d.tableName, t.label, {
            bold: true,
          })
        }
        if (l.role === 'composite') {
          fig(d.charts[0], 0, r.chart0)
          tx(
            'TableName',
            [r.main[0], r.main[1] - 0.5, r.main[2], 0.36],
            d.tableName,
            t.figure,
            {},
            'display',
          )
        }
        if (l.role === 'timeline') {
          const [x, y, w] = r.phases,
            total = d.phases.reduce((n, p) => n + p.duration, 0)
          let xx = x
          d.phases.forEach((ph, i) => {
            const ww = (w * ph.duration) / total
            rule(`PhaseRule${i}`, xx, y, ww - 0.06, i === 0 ? c.teal : c.history)
            tx(`Phase${i}Label`, [xx, y + 0.13, ww - 0.16, 0.33], ph.label, t.body, { bold: true })
            tx(`Phase${i}Detail`, [xx, y + 0.53, ww - 0.16, 0.4], ph.detail, t.label, {
              color: c.muted,
            })
            xx += ww
          })
          tx('TableName', [r.main[0], r.main[1] - 0.28, r.main[2], 0.25], d.tableName, t.label, {
            bold: true,
          })
        }
        table('Matrix', r.main)
        tx('TableNote', r.detail, d.note, t.label, { color: c.muted })
      } else if (l.role === 'argument') {
        const cols = l.layoutId === 'split' ? 2 : 1,
          rh = r.main[3] / Math.ceil(d.paragraphs.length / cols)
        d.paragraphs.forEach((n, i) => {
          const f = cols === 2 && i % 2 ? r.side : r.main,
            yy = f[1] + Math.floor(i / cols) * rh
          note(`Paragraph${i}`, n, [f[0], yy, f[2], rh - 0.2])
        })
      }
    }
    rule('VerdictRule', 0.65, 6.43, 12.03)
    tx('Verdict', a.chrome.verdict, d.verdict, t.label, { color: c.ink })
  }
  const result = finishDesign(
    design,
    content,
    { schemaVersion: 'pptx-patch/v1', ops: p.ops },
    resolved.layouts,
  )
  result.warnings = resolved.warnings
  return result
}
