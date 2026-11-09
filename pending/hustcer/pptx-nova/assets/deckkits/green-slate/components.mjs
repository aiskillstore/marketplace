// Shared dark strategy renderer. All claims, units, dates and labels come from content.
import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { resolveStrategyDeck } from './layouts.mjs'

const numeric = (n) =>
  Math.abs(n) > 0 && Math.abs(n) < 0.000001
    ? String(n)
    : new Intl.NumberFormat('en-US', { maximumFractionDigits: 20 }).format(n)
export function createStrategyDeck(design, content) {
  const resolved = resolveStrategyDeck(design, content),
    p = createOps({ textbox: design.textFrame }),
    e = design.strategy,
    t = e.typography
  const c = Object.fromEntries(Object.entries(design.roles).map(([k, v]) => [k, design.colors[v]]))
  p.ops.push(designTheme(design))
  for (const [s, slide] of content.slides.entries()) {
    const d = slide.data,
      l = resolved.layouts[s],
      r = l.frame.regions,
      nm = (base) => `S${s}_${base}`
    const tx = (base, frame, value, size = t.body, extra = {}) => {
      const text = wrapCjkText(String(value), Math.max(1, (((frame[2] - 0.04) * 72) / size) * 0.94))
      const capacity = Math.max(1, (((frame[2] - 0.04) * 72) / size) * 0.94)
      const lines = text
        .split('\n')
        .reduce(
          (n, line) =>
            n +
            Math.max(
              1,
              Math.ceil(
                [...line].reduce((a, ch) => a + (ch.codePointAt(0) > 0x7f ? 1 : 0.5), 0) / capacity,
              ),
            ),
          0,
        )
      const actual = [...frame]
      actual[3] = Math.min(frame[3], (lines * size * 1.5) / 72)
      p.textbox(s, nm(base), ...actual)
      p.setText(s, nm(base), text)
      for (let i = 0; i < text.split(/\r\n|\r|\n/).length; i++) {
        p.runFont(s, nm(base), designFont(design, 'body', size, { color: c.text, ...extra }), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name: nm(base) },
          paragraph: i,
          format: { lineSpacing: 1.12, spaceAfter: '0pt' },
        })
      }
    }
    const box = (base, frame, fill = c.panel) => p.box(s, nm(base), 'rectangle', ...frame, fill)
    const line = (base, x, y, w, color = c.rule) => box(base, [x, y, w, 0.009], color)
    const circle = (base, x, y, size, fill) => p.box(s, nm(base), 'oval', x, y, size, size, fill)
    const note = (base, n, [x, y, w, h]) => {
      tx(`${base}Heading`, [x, y, w, 0.46], n.heading, t.body, { bold: true })
      tx(`${base}Body`, [x, y + 0.52, w, h - 0.52], n.body, t.body, { color: c.secondary })
    }
    const notes = (items, region, horizontal = false) => {
      const [x, y, w, h] = region,
        gap = 0.18,
        nh = (h - gap * (items.length - 1)) / items.length
      if (horizontal) {
        const nw = (w - 0.32 * (items.length - 1)) / items.length
        items.forEach((n, i) => {
          const xx = x + i * (nw + 0.32)
          tx(`Note${i}Heading`, [xx, y, nw, 0.3], n.heading, t.body, { bold: true })
          tx(`Note${i}Body`, [xx, y + 0.36, nw, h - 0.36], n.body, t.body, { color: c.secondary })
        })
        return
      }
      items.forEach((n, i) => {
        note(`Note${i}`, n, [x, y + i * (nh + gap), w, nh])
        if (i) line(`NoteRule${i}`, x, y + i * (nh + gap) - 0.12, w)
      })
    }
    const metric = (base, m, [x, y, w, h]) => {
      tx(`${base}Value`, [x, y, w, 0.72], m.value, t.metric, { color: c.focus })
      tx(`${base}Label`, [x, y + 0.78, w, 0.38], m.label, t.label, { bold: true })
      tx(`${base}Detail`, [x, y + 1.18, w, Math.max(0.42, h - 1.18)], m.detail, t.label, {
        color: c.secondary,
      })
    }
    const table = (base, columns, rows, [x, y, w, h]) => {
      const data = [
          columns.map((col) => col.heading),
          ...rows.map((row) => row.cells.map((cell) => cell.text)),
        ],
        total = columns.reduce((v, col) => v + col.weight, 0),
        rh = h / data.length
      p.ops.push({
        op: 'add-table',
        slide: s,
        name: nm(base),
        rows: data.length,
        columns: columns.length,
        x: `${x}in`,
        y: `${y}in`,
        w: `${w}in`,
        h: `${h}in`,
        data,
      })
      p.ops.push({
        op: 'set-table',
        slide: s,
        shape: { name: nm(base) },
        style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
        rows: data.map((_, row) => ({ row, height: `${rh}in` })),
        columns: columns.map((col, column) => ({ column, width: `${(w * col.weight) / total}in` })),
        cells: data.flatMap((row, i) =>
          row.map((_, j) => {
            const tone = i ? rows[i - 1].cells[j].tone : 'normal',
              fg =
                tone === 'positive'
                  ? c.focus
                  : tone === 'negative'
                    ? c.negative
                    : tone === 'muted'
                      ? c.secondary
                      : c.text
            return {
              row: i,
              column: j,
              style: {
                fill: { type: 'solid', color: i === 0 ? c.header : c.surface },
                font: designFont(design, 'body', i === 0 ? t.label : t.body, {
                  color: fg,
                  bold: i === 0 || tone === 'positive',
                }),
                alignment: columns[j].align,
                verticalAnchor: 'middle',
                marginLeft: '5pt',
                marginRight: '5pt',
                marginTop: '5pt',
                marginBottom: '5pt',
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: c.rule, width: '0.5pt' },
                },
              },
            }
          }),
        ),
      })
    }
    const chart = (base, ch, region, kind = 'bar', variant = undefined, range = false) => {
      const [x, y, w, h] = region,
        font = designFont(design, 'body', t.label, { color: c.secondary })
      tx(`${base}Caption`, [x, y, w, 0.28], `${ch.name} · ${ch.unit}`, t.label, {
        color: c.secondary,
      })
      p.ops.push({
        op: 'add-chart',
        slide: s,
        name: nm(base),
        kind,
        ...(variant ? { variant } : {}),
        x: `${x}in`,
        y: `${y + 0.36}in`,
        w: `${w}in`,
        h: `${h - 0.36}in`,
        data: { categories: ch.categories, series: ch.series },
      })
      const colors = [c.series, c.focus, c.reference]
      p.ops.push({
        op: 'set-chart',
        slide: s,
        shape: { name: nm(base) },
        series: ch.series.map((_, i) => ({
          series: i,
          fill: { type: 'solid', color: colors[i] },
          line: { color: colors[i], width: kind === 'line' ? '2pt' : '0pt' },
          ...(kind === 'line'
            ? {
                smooth: false,
                marker: { symbol: 'circle', size: 4, fill: colors[i], line: colors[i] },
              }
            : { invertIfNegative: false }),
        })),
        axes: [
          {
            axis: 'category',
            ...(kind === 'bar' ? { scale: { reverseOrder: true } } : {}),
            line: { color: c.rule, width: '0.5pt' },
            ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
          },
          {
            axis: 'value',
            line: { color: c.rule, width: '0pt' },
            gridlines: null,
            minorGridlines: null,
            ticks: { visible: kind === 'line', font, major: 'none', minor: 'none' },
            ...(range
              ? {
                  scale: {
                    min: 0,
                    max:
                      Math.max(...ch.series[0].values.map((v, i) => v + ch.series[1].values[i])) *
                        1.2 || 1,
                  },
                }
              : {}),
          },
        ],
        dataLabels: [
          {
            showValue: !range && kind !== 'line',
            showSeriesName: false,
            showLegendKey: false,
            position: kind === 'line' ? 'above' : variant === 'stacked' ? 'center' : 'outside-end',
            numberFormat: ch.numberFormat ?? 'General',
            font: variant === 'stacked' ? { ...font, color: c.surface } : font,
          },
        ],
        ...(kind === 'bar'
          ? { plot: { gapWidth: 90, ...(variant === 'stacked' ? { overlap: 100 } : {}) } }
          : {}),
      })
      // Explicit labels and swatches stay editable; do not depend on chart legend defaults.
      ch.series.forEach((series, i) => {
        const xx = x + (i * w) / ch.series.length
        box(`${base}Swatch${i}`, [xx, y + h + 0.04, 0.12, 0.07], colors[i])
        tx(
          `${base}Legend${i}`,
          [
            xx + 0.19,
            y + h - 0.02,
            Math.min(w / ch.series.length - 0.24, Math.max(2, series.name.length * 0.1 + 0.05)),
            0.27,
          ],
          series.name,
          t.label,
          { color: c.secondary },
        )
      })
    }
    const angled = () => {
      const x = e.coverZone[0],
        y = e.coverZone[1],
        w = e.coverZone[2],
        h = e.coverZone[3]
      p.ops.push({
        op: 'add-freeform',
        slide: s,
        name: nm('AngledZone'),
        x: `${x}in`,
        y: `${y}in`,
        w: `${w}in`,
        h: `${h}in`,
        path: {
          width: 1000,
          height: 1000,
          commands: [
            { type: 'move', x: 160, y: 0 },
            { type: 'line', x: 1000, y: 0 },
            { type: 'line', x: 1000, y: 1000 },
            { type: 'line', x: 0, y: 1000 },
            { type: 'close' },
          ],
        },
      })
      p.fill(s, nm('AngledZone'), c.panel)
      p.noLine(s, nm('AngledZone'))
    }
    p.addSlide(s, c.surface)
    if (['cover', 'closing'].includes(l.role)) angled()
    tx('Footer', e.chrome.footer, `${d.source} · ${d.asOf}`, t.source, { color: c.secondary })
    tx(
      'Page',
      e.chrome.page,
      `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
      t.source,
      { color: c.secondary },
    )
    if (['cover', 'closing'].includes(l.role)) {
      tx('Masthead', [0.65, 0.65, 6.5, 0.3], d.label, t.label, { color: c.secondary })
      tx('CoverTitle', r.title, d.title, t.cover)
      tx('Abstract', r.abstract, d.abstract, t.body, { color: c.secondary })
      line('TitleFrame', r.title[0], r.title[1] - 0.25, 2, c.focus)
      if (l.role === 'cover') {
        const [x, y, w, h] = r.metrics,
          cw = (w - 0.4) / 2,
          ch = (h - 0.35) / 2
        d.metrics.forEach((m, i) =>
          metric(`CoverMetric${i}`, m, [
            x + (i % 2) * (cw + 0.4),
            y + Math.floor(i / 2) * (ch + 0.35),
            cw,
            ch,
          ]),
        )
        line('MetricRule', x, y + ch + 0.14, w)
        tx('CoverCallout', [7.5, 6.25, 4.9, 0.5], d.callout, t.body, { color: c.focus, bold: true })
      } else {
        tx('ClosingNext', [8.6, 2.25, 3.9, 1.3], d.next, t.title, { color: c.focus })
        tx('ClosingContact', [8.6, 4.2, 3.9, 1.05], d.contact, t.body)
      }
    } else if (l.role === 'section' || l.role === 'notice') {
      tx('SectionLabel', [0.65, 0.6, 5, 0.3], d.label, t.label, { color: c.focus })
      tx('SectionTitle', r.title, d.title, t.cover)
      if (l.role === 'section') {
        tx('SectionAbstract', r.abstract, d.abstract, t.body, { color: c.secondary })
        box('SectionAnchor', [0.65, 2.45, 0.16, 0.16], c.focus)
      } else
        d.paragraphs.forEach((v, i) =>
          tx(
            `Notice${i}`,
            [
              r.main[0],
              r.main[1] + (i * r.main[3]) / d.paragraphs.length,
              r.main[2],
              r.main[3] / d.paragraphs.length - 0.22,
            ],
            v,
            t.body,
            { color: c.secondary },
          ),
        )
    } else {
      // The background owns the text: there is no independently sized label box.
      // Conservative glyph classes leave room for wide uppercase and CJK labels.
      const tabUnits = [...d.label].reduce(
        (n, ch) =>
          n +
          (ch.codePointAt(0) > 0x7f
            ? 1.1
            : /[MW@%]/.test(ch)
              ? 1
              : /[A-Z0-9]/.test(ch)
                ? 0.76
                : /\s/.test(ch)
                  ? 0.34
                  : 0.6),
        0,
      )
      const tabWidth = Math.min(e.chrome.tab[2], Math.max(1.5, (tabUnits * t.label) / 72 + 0.3))
      box('Tab', [e.chrome.tab[0], e.chrome.tab[1], tabWidth, e.chrome.tab[3]], c.header)
      p.ops.push({
        op: 'set-text-frame',
        slide: s,
        shape: { name: nm('Tab') },
        text: d.label,
        font: designFont(design, 'body', t.label, { color: c.text, bold: true }),
        frame: {
          marginLeft: '0.12in',
          marginRight: '0.12in',
          marginTop: '0in',
          marginBottom: '0in',
          verticalAnchor: 'middle',
          wordWrap: false,
        },
      })
      p.ops.push({
        op: 'set-paragraph',
        slide: s,
        shape: { name: nm('Tab') },
        paragraph: 0,
        format: { alignment: 'left', spaceBefore: '0pt', spaceAfter: '0pt', lineSpacing: 1 },
      })
      tx('Title', e.chrome.title, d.title, t.title)
      tx('Basis', e.chrome.basis, d.basis, t.label, { color: c.secondary })
      line('HeaderRule', 0.65, 1.99, 12.03)
      line('HeaderFocus', 0.65, 1.99, 0.85, c.focus)
      if (l.role === 'summary') {
        const [x, y, w, h] = r.main,
          rh = h / d.findings.length
        d.findings.forEach((n, i) => {
          tx(`FindingNumber${i}`, [x, y + i * rh, 0.5, 0.5], String(i + 1).padStart(2, '0'), 22, {
            color: c.focus,
          })
          note(`Finding${i}`, n, [x + 0.73, y + i * rh, w - 0.73, rh - 0.22])
          if (i) line(`FindingRule${i}`, x, y + i * rh - 0.16, w)
        })
        d.metrics.forEach((m, i) =>
          metric(`Metric${i}`, m, [
            r.side[0],
            r.side[1] + (i * r.side[3]) / d.metrics.length,
            r.side[2],
            r.side[3] / d.metrics.length - 0.12,
          ]),
        )
      } else if (l.role === 'range') {
        const range = d.range,
          values = range.low.map((v, i) => range.high[i] - v)
        chart(
          'Range',
          {
            name: range.name,
            unit: range.unit,
            categories: range.categories,
            series: [
              { name: range.lowerLabel, values: range.low },
              { name: range.spanLabel, values },
            ],
          },
          r.main,
          'bar',
          'stacked',
          true,
        )
        notes(d.notes, r.side, l.layoutId === 'wide')
        tx(
          'RangeBounds',
          [r.main[0], r.main[1] + r.main[3] + 0.4, r.main[2], l.layoutId === 'wide' ? 0.25 : 0.55],
          range.categories
            .map((v, i) => `${v}: ${numeric(range.low[i])}–${numeric(range.high[i])}${range.unit}`)
            .join('  ·  '),
          t.label,
          { color: c.secondary },
        )
      } else if (l.role === 'matrix') {
        table('Matrix', d.columns, d.rows, r.main)
        tx(
          'MatrixLegend',
          [r.main[0], r.main[1] + r.main[3] + 0.1, r.main[2], 0.2],
          d.legend,
          t.label,
          { color: c.secondary },
        )
      } else if (l.role === 'roadmap') {
        const [x, y, w, h] = r.main,
          left = 1.22,
          total = d.phases.reduce((v, ph) => v + ph.duration, 0),
          widths = d.phases.map((ph) => ((w - left) * ph.duration) / total)
        const gateY = y + h - e.roadmap.gateHeight,
          trackBottom = gateY - e.roadmap.gateGap
        const rw = (trackBottom - y - e.roadmap.trackTop) / d.tracks.length
        let xx = x + left,
          cumulative = 0
        d.phases.forEach((ph, j) => {
          const pw = widths[j]
          box(
            `PhaseBand${j}`,
            [xx, y, pw - 0.04, e.roadmap.headerHeight],
            j % 2 ? c.header : c.panel,
          )
          cumulative += ph.duration
          p.ops.push({
            op: 'set-text-frame',
            slide: s,
            shape: { name: nm(`PhaseBand${j}`) },
            text: `${ph.label}\n${numeric(cumulative)} ${d.unit}`,
            font: designFont(design, 'body', t.body, { color: c.text, bold: true }),
            frame: {
              marginLeft: '0.12in',
              marginRight: '0.12in',
              marginTop: '0.12in',
              marginBottom: '0.08in',
            },
          })
          tx(`Gate${j}`, [xx + 0.12, gateY, pw - 0.28, e.roadmap.gateHeight], ph.gate, t.label, {
            color: c.focus,
          })
          box(
            `GateLine${j}`,
            [xx + pw - 0.08, y + 0.96, 0.009, trackBottom - y - 0.96 - e.roadmap.rowBottomGap],
            c.rule,
          )
          circle(`GateNode${j}`, xx + pw - 0.13, y + 0.91, 0.11, c.focus)
          xx += pw
        })
        d.tracks.forEach((track, i) => {
          const yy = y + e.roadmap.trackTop + i * rw
          tx(`Track${i}`, [x, yy, left - 0.18, rw - 0.08], track.label, t.body, { bold: true })
          line(`TrackRule${i}`, x + left, yy + rw - e.roadmap.rowBottomGap, w - left)
          let ax = x + left
          track.activities.forEach((a, j) => {
            tx(
              `Activity${i}_${j}`,
              [ax + 0.12, yy + 0.03, widths[j] - 0.28, Math.min(0.56, rw - 0.12)],
              a,
              t.body,
              { color: c.secondary },
            )
            ax += widths[j]
          })
        })
      } else if (l.role === 'value') {
        chart('ValueChart', d.chart, r.main, 'line')
        chart('InvestmentChart', d.investment, r.support, 'bar', 'stacked')
        notes(d.notes, r.side)
      } else if (l.role === 'flow') {
        const horizontal = l.layoutId === 'horizontal',
          [x, y, w, h] = r.main,
          gap = 0.24,
          sw = horizontal ? (w - gap * (d.steps.length - 1)) / d.steps.length : w,
          sh = horizontal ? h : h / d.steps.length
        if (!horizontal) box('FlowSpine', [x + 0.19, y + 0.25, 0.012, h - 0.6], c.rule)
        d.steps.forEach((n, i) => {
          const xx = x + (horizontal ? i * (sw + gap) : 0),
            yy = y + (horizontal ? 0 : i * sh)
          circle(`StepNode${i}`, xx, yy + 0.08, 0.4, c.header)
          p.ops.push({
            op: 'set-text-frame',
            slide: s,
            shape: { name: nm(`StepNode${i}`) },
            text: String(i + 1),
            font: designFont(design, 'body', t.label, { color: c.text, bold: true }),
            frame: {
              marginLeft: '0in',
              marginRight: '0in',
              marginTop: '0in',
              marginBottom: '0in',
              verticalAnchor: 'middle',
              wordWrap: false,
            },
          })
          p.ops.push({
            op: 'set-paragraph',
            slide: s,
            shape: { name: nm(`StepNode${i}`) },
            paragraph: 0,
            format: { alignment: 'center', spaceBefore: '0pt', spaceAfter: '0pt', lineSpacing: 1 },
          })
          const fx = horizontal ? xx : xx + 0.72,
            fy = horizontal ? yy + 0.78 : yy
          note(`Step${i}`, n, [
            fx,
            fy,
            horizontal ? sw : sw - 0.72,
            horizontal ? sh - 0.8 : sh - 0.16,
          ])
          if (horizontal && i < d.steps.length - 1)
            box(`FlowLink${i}`, [xx + 0.45, yy + 0.27, sw + gap - 0.52, 0.012], c.rule)
        })
        notes(d.notes, r.side)
      }
      box(
        'VerdictMark',
        [e.chrome.verdict[0], e.chrome.verdict[1], 0.035, e.chrome.verdict[3]],
        c.focus,
      )
      tx(
        'Verdict',
        [
          e.chrome.verdict[0] + 0.18,
          e.chrome.verdict[1],
          e.chrome.verdict[2] - 0.18,
          e.chrome.verdict[3],
        ],
        d.verdict,
        t.body,
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
  return result
}
