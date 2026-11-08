// Native evidence renderer shared by contract-driven DeckKits.
import { designFont, textUnits } from './design-contract.mjs'

import { wrapCjkText } from './design-text.mjs'

export function renderEvidence(p, design, s, slide, resolved, total) {
  const d = slide.data
  const e = design.evidence
  const c = Object.fromEntries(
    Object.entries(design.roles).map(([role, token]) => [role, design.colors[token]]),
  )
  const name = (base) => `S${s}_${base}`
  const text = (base, frame, value, role, size, extra = {}) => {
    const n = name(base)
    p.textbox(s, n, ...frame)
    p.setText(s, n, value)
    for (let i = 0; i < String(value).split(/\r\n|\r|\n/).length; i++) {
      p.runFont(s, n, designFont(design, role, size, extra), i)
      p.ops.push({
        op: 'set-paragraph',
        slide: s,
        shape: { name: n },
        paragraph: i,
        format: { lineSpacing: 1.08, spaceAfter: '0pt' },
      })
    }
  }
  p.addSlide(s, c.surface)
  const header = resolved.header
  const title =
    resolved.titleLines > 1 && !d.title.includes('\n')
      ? wrapCjkText(d.title, Math.ceil(textUnits(d.title) / 2))
      : d.title
  text('EvidenceTitle', header.title, title, 'display', e.fontPt.title)
  text('EvidenceLabel', header.label, `${d.label} · ${d.unit}`, 'body', e.fontPt.label, {
    bold: true,
  })
  p.box(s, name('EvidenceRule'), 'rectangle', ...header.rule, c.rule)
  text('EvidenceSource', header.source, d.source, 'body', e.fontPt.source)
  text(
    'EvidencePage',
    header.page,
    `${String(s + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}`,
    'mono',
    e.fontPt.source,
  )
  const layout = resolved.frame
  const fields = e.statComponents[resolved.layoutId]
  d.stats.forEach((stat, i) => {
    const [x, y, w] = layout.stats[i]
    for (const [field, spec] of Object.entries(fields)) {
      let value = field === 'value' ? `${stat.value}${stat.suffix}` : stat[field]
      const frame = [x, y + spec.y, w, spec.h]
      if (field === 'description') {
        value = wrapCjkText(value, (((w - 0.04) * 72) / e.fontPt.body) * e.cjkWrapSafety)
      }
      text(
        `EvidenceStat${i}_${field}`,
        frame,
        value,
        spec.role,
        spec.fontPt ?? e.fontPt[field === 'description' ? 'body' : field],
        field === 'label' ? { bold: true } : {},
      )
    }
  })
  renderEvidenceChart(p, design, s, d, resolved, 'EvidenceChart')
}

export function renderEvidenceChart(p, design, s, d, resolved, base) {
  const e = design.evidence
  const c = Object.fromEntries(
    Object.entries(design.roles).map(([role, token]) => [role, design.colors[token]]),
  )
  const name = (base) => `S${s}_${base}`
  const layout = resolved.frame
  const [x, y, w, h] = layout.chart
  const chart = name(base)
  p.ops.push({
    op: 'add-chart',
    slide: s,
    name: chart,
    kind: d.kind,
    x: `${x}in`,
    y: `${y}in`,
    w: `${w}in`,
    h: `${h}in`,
    data: {
      categories: d.points.map((p) => p.label),
      series: [{ name: `${d.seriesName} (${d.unit})`, values: d.points.map((p) => p.value) }],
    },
  })
  const font = designFont(design, 'body', e.fontPt.label)
  const style = e.chartStyle
  const series = {
    series: 0,
    ...(d.kind === 'bar' ? { invertIfNegative: false } : {}),
    fill: { type: 'solid', color: c.series },
    line: { color: c.series, width: `${d.kind === 'bar' ? 0 : style.lineWidthPt}pt` },
  }
  const focus = d.points.findIndex((p) => p.emphasis)
  if (focus >= 0) {
    series.points = [
      {
        point: focus,
        ...(d.kind === 'line'
          ? { marker: { symbol: 'circle', size: 8, fill: c.focus, line: c.series } }
          : {
              fill: { type: 'solid', color: c.focus },
              line: { color: c.rule, width: d.points[focus].value === 0 ? '0pt' : '0.75pt' },
            }),
      },
    ]
  }
  if (d.kind === 'line') {
    series.marker = { symbol: 'circle', size: 5, fill: c.series, line: c.series }
    series.smooth = false
  }
  p.ops.push({
    op: 'set-chart',
    slide: s,
    shape: { name: chart },
    series: [series],
    axes: [
      {
        axis: 'category',
        ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
        line: { color: c.rule, width: '0.75pt' },
      },
      {
        axis: 'value',
        ticks: {
          font,
          visible: style.valueTicks,
          major: 'none',
          minor: 'none',
          numberFormat: resolved.numberFormat,
        },
        gridlines: null,
        minorGridlines: null,
      },
    ],
    dataLabels: [
      {
        showValue: true,
        showLegendKey: false,
        showSeriesName: false,
        position: d.kind === 'bar' ? 'outside-end' : 'above',
        numberFormat: resolved.numberFormat,
        font,
      },
    ],
    ...(d.kind === 'bar' ? { plot: { gapWidth: 75 } } : {}),
  })
}
