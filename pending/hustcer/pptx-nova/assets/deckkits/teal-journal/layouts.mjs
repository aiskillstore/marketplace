import { designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'
export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(9)).toString()
}
export function chartNumberFormat(values) {
  const nonzero = values.map(Math.abs).filter(Boolean)
  if (nonzero.some((v) => v < 0.001 || v >= 1e7)) return '0.00E+00'
  if (values.every(Number.isInteger)) return '0'
  const places = Math.min(8, Math.max(2, 2 - Math.floor(Math.log10(Math.min(...nonzero)))))
  return '0.' + '0'.repeat(places)
}
export function compileJournalLayout(design, family, id, variant, d, path = 'data') {
  const b = design.journal,
    r = variant.regions,
    cs = []
  const tx = (name, frame, value, key = 'body', fields = name, extra = {}) => {
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) => `${path}.${k}`),
      c = { ...fitTextPlan(value, frame, { ...b.styles[key], ...extra }, paths[0]), name, paths }
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule', kind = 'box') => cs.push({ kind, name, frame, color })
  const rule = (name, x, y, w, color = 'rule', vertical = false) =>
    box(name, vertical ? [x, y, 0.009, w] : [x, y, w, 0.009], color)
  const cells = (f, n, vertical = false, g = b.spacing.gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const owned = (name, frame, value, color, fields, key = 'strip') => {
    const inset = 0.12,
      c = tx(
        name,
        [frame[0] + inset, frame[1] + 0.035, frame[2] - inset * 2, frame[3] - 0.07],
        value,
        key,
        fields,
      )
    Object.assign(c, {
      kind: 'owned',
      frame,
      allocatedFrame: frame,
      color,
      shapeKind: 'rectangle',
      anchor: 'middle',
    })
    return c
  }
  const pathShape = (name, frame, points, { fill, line = 'ink', linePt = 0.8 } = {}) =>
    cs.push({
      kind: 'path',
      name,
      frame,
      fill,
      line,
      linePt,
      path: {
        width: 100000,
        height: 100000,
        commands: points
          .map(([x, y], i) => ({
            type: i ? 'line' : 'move',
            x: Math.round(x * 100000),
            y: Math.round(y * 100000),
          }))
          .concat(fill ? [{ type: 'close' }] : []),
      },
    })
  const dot = (name, x, y, solid = true) => {
    const radius = 0.065
    box(name, [x - radius, y - radius, 2 * radius, 2 * radius], 'accent', 'circle')
    if (!solid)
      box(
        name + 'Inner',
        [x - radius * 0.62, y - radius * 0.62, 2 * radius * 0.62, 2 * radius * 0.62],
        'paper',
        'circle',
      )
  }
  const notes = (f, items) =>
    cells(f, items.length, true, 0.16).forEach(([x, y, w, h], i) => {
      rule('NoteRule' + i, x, y, w)
      tx(
        'NoteHeading' + i,
        [x, y + 0.1, w, 0.35],
        items[i].heading,
        'heading',
        `notes[${i}].heading`,
      )
      tx('NoteBody' + i, [x, y + 0.51, w, h - 0.51], items[i].body, 'body', `notes[${i}].body`)
    })
  const allocation = (f, items, unit, vertical = false) => {
    const total = items.reduce((a, v) => a + v.value, 0)
    if (!(total > 0) || items.some((v) => v.value < 0))
      throw Error('Allocation requires nonnegative values and a positive total')
    let start = 0
    const tones = ['accent', 'ink', 'pale', 'rule']
    if (vertical) {
      cells(f, items.length, true, 0.15).forEach(([x, y, w, h], i) => {
        const v = items[i]
        tx('AllocationLabel' + i, [x, y, w, 0.3], v.label, 'label', `allocation[${i}].label`)
        tx(
          'AllocationValue' + i,
          [x, y + 0.34, w, 0.34],
          `${number(v.value)} ${unit} · ${number((v.value / total) * 100)}%`,
          'label',
          [`allocation[${i}].value`, 'allocationUnit'],
        )
        box('AllocationTrack' + i, [x, y + h - 0.09, w, 0.07], 'pale')
        if (v.value)
          box('AllocationSegment' + i, [x, y + h - 0.09, (w * v.value) / total, 0.07], tones[i])
      })
    } else {
      items.forEach((v, i) => {
        if (v.value)
          box(
            'AllocationSegment' + i,
            [f[0] + (f[2] * start) / total, f[1], (f[2] * v.value) / total, 0.17],
            tones[i],
          )
        start += v.value
      })
      cells([f[0], f[1] + 0.28, f[2], f[3] - 0.28], items.length, false, 0.15).forEach(
        ([x, y, w, h], i) =>
          tx(
            'AllocationLabel' + i,
            [x, y, w, h],
            `${items[i].label} ${number(items[i].value)} ${unit}`,
            'small',
            [`allocation[${i}].label`, `allocation[${i}].value`, 'allocationUnit'],
          ),
      )
    }
  }
  const table = (name, f, cols, rows, focus = -1) => {
    if (rows.some((v) => v.length !== cols.length))
      throw Error('Every table row must match all columns')
    if (!Number.isInteger(focus) || focus < 0 || focus >= cols.length)
      throw Error('focusColumn outside columns')
    const total = cols.reduce((a, v) => a + v.weight, 0),
      widths = cols.map((v) => (f[2] * v.weight) / total),
      all = [cols.map((v) => v.label), ...rows],
      rh = f[3] / all.length,
      bindings = []
    all.forEach((row, i) => {
      let x = f[0]
      row.forEach((value, j) => {
        if (/[\r\n]/u.test(value)) throw Error('Native table cells require a single paragraph')
        const frame = [x + 0.075, f[1] + i * rh + 0.055, widths[j] - 0.15, rh - 0.11],
          st = { ...b.styles[i ? 'table' : 'label'], bold: !i || j === focus },
          p = i ? `rows[${i - 1}][${j}]` : `columns[${j}].label`
        fitTextPlan(value, frame, st, `${path}.${p}`)
        bindings.push({ paths: [`${path}.${p}`], frame, style: st })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name,
      frame: f,
      cells: all,
      columns: cols,
      widths,
      rowHeights: all.map(() => rh),
      focusColumn: focus,
      focusTone: 'highlight',
      bindings,
      useBindingStyles: true,
      blueRules: true,
    })
  }
  const common = () => {
    tx('Eyebrow', b.chrome.eyebrow, d.eyebrow, 'small', 'eyebrow', { alignment: 'right' })
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Subtitle', b.chrome.subtitle, d.subtitle, 'subtitle', 'subtitle')
  }
  if (family.role === 'cover') {
    const [x, y, w, h] = r.field
    pathShape(
      'CoverAngularField',
      [x, y, w, h],
      [
        [0.18, 0],
        [1, 0],
        [1, 0.84],
        [0.78, 0.84],
        [0.62, 1],
        [0, 1],
        [0, 0.42],
      ],
      { fill: 'pale', line: 'ink', linePt: 1.1 },
    )
    pathShape(
      'CoverCoralEdge',
      [x, y + h * 0.84, w, h * 0.16],
      [
        [0, 1],
        [0.62, 1],
        [0.78, 0],
        [1, 0],
      ],
      { line: 'accent', linePt: 3 },
    )
    tx(
      'AssetCaption',
      [x + 0.3, y + h * 0.38, w - 0.6, 1],
      d.assetCaption,
      'label',
      'assetCaption',
      { color: 'deep' },
    )
    box('CoverSquare', [0.8, 0.5, 0.12, 0.12], 'accent')
    tx('Eyebrow', [1.03, 0.43, 11.5, 0.33], d.eyebrow, 'label', 'eyebrow')
    tx('CoverTitle', r.hero, d.title, 'hero', 'title')
    owned('CoverStrip', r.strip, d.subtitle, 'accent', 'subtitle')
    tx('CoverSummary', r.summary, d.summary, 'subtitle', 'summary')
    cells(r.markers, d.markers.length, false, 0.18).forEach(([mx, my, mw, mh], i) => {
      box('SeasonSquare' + i, [mx, my + 0.09, 0.075, 0.075], 'accent')
      tx('Marker' + i, [mx + 0.15, my, mw - 0.15, mh], d.markers[i], 'small', `markers[${i}]`)
    })
  } else {
    common()
    if (family.role === 'outlook') {
      const [x, y, w, h] = r.metric
      box('MetricField', r.metric, 'highlight')
      tx(
        'MetricLabel',
        [x + 0.18, y + 0.13, w - 0.36, 0.3],
        d.metric.label,
        'label',
        'metric.label',
      )
      tx(
        'MetricNumber',
        [x + 0.18, y + 0.5, w - 0.36, 0.85],
        `${number(d.metric.value)} ${d.metric.unit}`,
        'number',
        ['metric.value', 'metric.unit'],
      )
      tx('MetricNote', [x + 0.18, y + 1.43, w - 0.36, 0.26], d.metric.note, 'small', 'metric.note')
      const f = r.plot
      tx('ChartLabel', [f[0], f[1] - 0.06, f[2], 0.33], `${d.seriesName} · ${d.unit}`, 'label', [
        'seriesName',
        'unit',
      ])
      cs.push({
        kind: 'chart',
        name: 'Comparison',
        frame: [f[0], f[1] + 0.3, f[2], f[3] - 0.3],
        chartKind: 'bar',
        data: {
          categories: d.points.map((v) => v.label),
          series: [{ name: d.seriesName, values: d.points.map((v) => v.value) }],
        },
        inputPaths: d.points.flatMap((_, i) => [
          `${path}.points[${i}].label`,
          `${path}.points[${i}].value`,
        ]),
        minimum: (() => {
          const lo = Math.min(0, ...d.points.map((v) => v.value))
          const hi = Math.max(0, ...d.points.map((v) => v.value))
          return lo < 0 ? lo - (hi - lo || 1) * 0.65 : 0
        })(),
        maximum: (() => {
          const lo = Math.min(0, ...d.points.map((v) => v.value))
          const hi = Math.max(0, ...d.points.map((v) => v.value))
          const scientific = chartNumberFormat(d.points.map((v) => v.value)).includes('E')
          return hi + (hi - lo || 1) * (scientific ? 0.45 : 0.18)
        })(),
        uniformSeriesTone: 'ink',
        numberFormat: chartNumberFormat(d.points.map((v) => v.value)),
        showValues: true,
      })
      notes(r.notes, d.notes)
    } else if (family.role === 'audience') {
      if (id === 'leadLeft') {
        tx(
          'LeadHeading',
          [r.lead[0], r.lead[1], r.lead[2], 0.45],
          d.lead.heading,
          'heading',
          'lead.heading',
        )
        tx(
          'LeadBody',
          [r.lead[0], r.lead[1] + 0.65, r.lead[2], r.lead[3] - 0.65],
          d.lead.body,
          'body',
          'lead.body',
        )
      } else
        tx('LeadBody', r.lead, `${d.lead.heading} — ${d.lead.body}`, 'small', [
          'lead.heading',
          'lead.body',
        ])
      table('Audience', r.table, d.columns, d.rows, d.focusColumn)
      tx('Methodology', r.note, d.methodology, 'small', 'methodology')
    } else if (family.role === 'calendar') {
      if (!(d.axisEnd > d.axisStart)) throw Error('Calendar axis must increase')
      d.phases.forEach((v, i) => {
        if (
          !(v.start < v.end) ||
          v.start < d.axisStart ||
          v.end > d.axisEnd ||
          (i && v.start < d.phases[i - 1].end)
        )
          throw Error('Phase intervals must be ordered, nonoverlapping and within axis')
      })
      const f = r.phases,
        vertical = id === 'vertical'
      if (vertical) {
        rule('CalendarAxis', f[0] + 0.15, f[1] + 0.1, f[3] - 0.2, 'ink', true)
        cells(f, d.phases.length, true, 0.16).forEach(([x, y, w, h], i) => {
          const v = d.phases[i]
          dot('PhaseDot' + i, x + 0.15, y + 0.22, v.status === 'observed')
          tx(
            'PhaseLabel' + i,
            [x + 0.5, y, w * 0.43, 0.32],
            `${v.label} · ${v.period}`,
            'heading',
            [`phases[${i}].label`, `phases[${i}].period`],
          )
          tx(
            'PhaseValue' + i,
            [x + 0.5, y + 0.38, w * 0.43, 0.33],
            `${number(v.value)} ${d.unit}`,
            'label',
            [`phases[${i}].value`, 'unit'],
          )
          tx(
            'PhaseEvidence' + i,
            [x + w * 0.53, y, w * 0.47, h],
            v.evidence,
            'body',
            `phases[${i}].evidence`,
          )
        })
      } else {
        const axisY = f[1] + 1.5
        rule('CalendarAxis', f[0], axisY, f[2], 'ink')
        for (const [i, v] of d.phases.entries()) {
          const x = f[0] + (f[2] * (v.start - d.axisStart)) / (d.axisEnd - d.axisStart)
          rule('CalendarTick' + i, x, axisY - 0.07, 0.14, 'ink', true)
        }
        rule('CalendarEndTick', f[0] + f[2], axisY - 0.07, 0.14, 'ink', true)
        cells(f, d.phases.length, false, 0.24).forEach(([x, y, w], i) => {
          const v = d.phases[i]
          tx('PhaseLabel' + i, [x, y, w, 0.5], v.label, 'heading', `phases[${i}].label`)
          tx('PhasePeriod' + i, [x, y + 0.57, w, 0.28], v.period, 'small', `phases[${i}].period`)
          owned(
            'PhaseValue' + i,
            [x, y + 0.94, w, 0.4],
            `${number(v.value)} ${d.unit}`,
            'highlight',
            [`phases[${i}].value`, 'unit'],
            'label',
          )
          dot(
            'PhaseDot' + i,
            f[0] + (f[2] * ((v.start + v.end) / 2 - d.axisStart)) / (d.axisEnd - d.axisStart),
            axisY,
            v.status === 'observed',
          )
          tx(
            'PhaseEvidence' + i,
            [x, axisY + 0.45, w, 1],
            v.evidence,
            'body',
            `phases[${i}].evidence`,
          )
        })
      }
      allocation(r.allocation, d.allocation, d.allocationUnit, vertical)
    } else if (family.role === 'journey') {
      if (!(d.axisEnd > d.axisStart)) throw Error('Journey axis must increase')
      d.steps.forEach((v, i) => {
        if (
          !(v.start < v.end) ||
          v.start < d.axisStart ||
          v.end > d.axisEnd ||
          (i && v.start < d.steps[i - 1].end)
        )
          throw Error('Journey intervals must be ordered, nonoverlapping and within axis')
      })
      const f = r.route,
        [x, y, w, h] = f,
        arc = id === 'arc',
        arcF = [x + 1.9, y + 0.05, w - 3.8, 1.7]
      const arcPath = (name, start, end, tone, width) => {
        const points = Array.from({ length: 61 }, (_, i) => {
          const t = Math.PI * (1 - (start + ((end - start) * i) / 60))
          return [(1 + Math.cos(t)) / 2, 1 - Math.sin(t)]
        })
        pathShape(name, arcF, points, { line: tone, linePt: width })
      }
      if (arc) {
        arcPath('JourneyTrack', 0, 1, 'pale', 7)
        d.steps.forEach((v, i) =>
          arcPath(
            'JourneySegment' + i,
            (v.start - d.axisStart) / (d.axisEnd - d.axisStart),
            (v.end - d.axisStart) / (d.axisEnd - d.axisStart),
            'accent',
            20,
          ),
        )
      } else {
        rule('JourneyTrack', x + 0.1, y + 0.6, w - 0.2, 'pale')
        d.steps.forEach((v, i) => {
          const sx = x + 0.1 + ((w - 0.2) * (v.start - d.axisStart)) / (d.axisEnd - d.axisStart),
            sw = ((w - 0.2) * (v.end - v.start)) / (d.axisEnd - d.axisStart)
          box('JourneySegment' + i, [sx, y + 0.52, sw, 0.16], 'accent')
        })
      }
      cells(
        [x, y + (arc ? 2 : 0.98), w, h - (arc ? 2 : 0.98)],
        d.steps.length,
        false,
        0.35,
      ).forEach(([sx, sy, sw, sh], i) => {
        const v = d.steps[i]
        box('JourneySquare' + i, [sx, sy + 0.07, 0.08, 0.08], 'accent')
        tx(
          'JourneyHeading' + i,
          [sx + 0.17, sy, sw - 0.17, 0.4],
          `${String(i + 1).padStart(2, '0')} ${v.label}`,
          'heading',
          `steps[${i}].label`,
        )
        tx(
          'JourneyTime' + i,
          [sx, sy + 0.5, sw, 0.32],
          `${number(v.start)} → ${number(v.end)} ${d.unit}`,
          'label',
          [`steps[${i}].start`, `steps[${i}].end`, 'unit'],
        )
        tx('JourneyDetail' + i, [sx, sy + 0.94, sw, 0.55], v.detail, 'body', `steps[${i}].detail`)
        tx(
          'JourneyMeasure' + i,
          [sx, sy + 1.57, sw, 0.35],
          v.measure,
          'label',
          `steps[${i}].measure`,
        )
      })
    } else if (family.role === 'anatomy') {
      const [x, y, w, h] = r.sample
      box('SampleBorder', r.sample, 'ink')
      box('SamplePaper', [x + 0.012, y + 0.012, w - 0.024, h - 0.024], 'paper')
      owned(
        'SampleImage',
        [x + 0.13, y + 0.15, w - 0.26, 0.62],
        d.sample.imageCaption,
        'pale',
        'sample.imageCaption',
        'strip',
      )
      tx(
        'SampleTitle',
        [x + 0.18, y + 1, w - 0.36, 0.55],
        d.sample.heading,
        'heading',
        'sample.heading',
      )
      tx('SampleTag', [x + 0.18, y + 1.69, w - 0.36, 0.32], d.sample.tag, 'small', 'sample.tag')
      owned('SampleCTA', [x + 0.13, y + 2.18, w - 0.26, 0.45], d.sample.cta, 'accent', 'sample.cta')
      tx(
        'SampleTerms',
        [x + 0.18, y + 2.85, w - 0.36, 0.36],
        d.sample.terms,
        'small',
        'sample.terms',
      )
      ;[r.left, r.right].forEach((f, side) =>
        cells(f, 3, true, 0.18).forEach(([lx, ly, lw, lh], i) => {
          const index = i + side * 3,
            v = d.annotations[index]
          tx(
            'AnnotationLabel' + index,
            [lx, ly, lw, 0.32],
            v.label,
            'label',
            `annotations[${index}].label`,
          )
          tx(
            'AnnotationDetail' + index,
            [lx, ly + 0.39, lw, lh - 0.39],
            v.detail,
            'small',
            `annotations[${index}].detail`,
          )
          const cy = ly + 0.18
          if (id === 'center') {
            const start = side ? x + w : lx + lw + 0.05,
              end = side ? lx - 0.08 : x - 0.05
            rule('Leader' + index, start, cy, end - start, 'pale')
            const dx = side ? start : end
            box('LeaderDot' + index, [dx - 0.055, cy - 0.055, 0.11, 0.11], 'pale', 'circle')
            box('LeaderHole' + index, [dx - 0.035, cy - 0.035, 0.07, 0.07], 'paper', 'circle')
          } else rule('Leader' + index, lx, ly - 0.07, lw, 'pale')
        }),
      )
      const max = Math.max(...d.comparison.map((v) => Math.abs(v.value)))
      if (!max) throw Error('Comparison requires a nonzero magnitude')
      cells(r.plot, d.comparison.length, false, 0.5).forEach(([px, py, pw, ph], i) => {
        const v = d.comparison[i]
        tx(
          'ComparisonLabel' + i,
          [px, py, pw, 0.26],
          `${v.label} · ${number(v.value)} ${d.unit}`,
          'small',
          [`comparison[${i}].label`, `comparison[${i}].value`, 'unit'],
        )
        const zero = px + pw / 2,
          scale = pw / 2 / max
        if (v.value)
          box(
            'ComparisonBar' + i,
            [
              v.value < 0 ? zero + v.value * scale : zero,
              py + 0.36,
              Math.abs(v.value) * scale,
              0.1,
            ],
            i ? 'ink' : 'accent',
          )
        rule('ComparisonZero' + i, zero, py + 0.32, 0.18, 'ink', true)
      })
    } else if (family.role === 'results') {
      cells(r.outcomes, d.outcomes.length, true, 0.17).forEach(([x, y, w, h], i) => {
        const v = d.outcomes[i]
        rule('OutcomeRule' + i, x, y, w)
        tx(
          'OutcomeValue' + i,
          [x, y + 0.12, w * 0.38, 0.48],
          `${number(v.value)} ${v.unit}`,
          'metric',
          [`outcomes[${i}].value`, `outcomes[${i}].unit`],
        )
        tx(
          'OutcomeLabel' + i,
          [x + w * 0.42, y + 0.12, w * 0.58, 0.4],
          v.label,
          'heading',
          `outcomes[${i}].label`,
        )
        tx(
          'OutcomeContext' + i,
          [x + w * 0.42, y + 0.52, w * 0.58, h - 0.52],
          v.context,
          'small',
          `outcomes[${i}].context`,
        )
      })
      cells(r.outputs, d.outputs.length, id === 'band', 0.18).forEach(([x, y, w, h], i) => {
        const v = d.outputs[i]
        tx('OutputValue' + i, [x, y, w, 0.35], `${number(v.value)} ${v.unit}`, 'heading', [
          `outputs[${i}].value`,
          `outputs[${i}].unit`,
        ])
        tx('OutputLabel' + i, [x, y + 0.28, w, h - 0.28], v.label, 'small', `outputs[${i}].label`)
      })
      box('KPIField', r.kpis, 'highlight')
      cells(
        [r.kpis[0] + 0.18, r.kpis[1] + 0.15, r.kpis[2] - 0.36, r.kpis[3] - 0.3],
        d.kpis.length,
        id === 'rail',
        0.22,
      ).forEach(([x, y, w, h], i) => {
        const v = d.kpis[i]
        tx('KPILabel' + i, [x, y, w, 0.3], v.label, 'label', `kpis[${i}].label`)
        tx(
          'KPIValue' + i,
          [x, y + 0.31, w, id === 'rail' ? 0.5 : 0.35],
          `${number(v.value)} ${v.unit}`,
          id === 'rail' ? 'metric' : 'heading',
          [`kpis[${i}].value`, `kpis[${i}].unit`],
        )
        if (id === 'rail')
          tx('KPIContext' + i, [x, y + 0.83, w, h - 0.76], v.context, 'small', `kpis[${i}].context`)
        else tx('KPIContext' + i, [x, y + 0.78, w, 0.35], v.context, 'small', `kpis[${i}].context`)
      })
    } else if (family.role === 'roadmap') {
      if (id === 'rail') {
        box('RoadmapRail', r.rail, 'highlight')
        cells(r.rail, 3, true, 0.3).forEach(([x, y, w, h], i) => {
          tx(
            'RoadmapNumber' + i,
            [x + 0.18, y + 0.1, w - 0.36, 0.55],
            String(i + 1).padStart(2, '0'),
            'metric',
            'structural.number',
          )
          tx(
            'RoadmapLabel' + i,
            [x + 0.18, y + 0.63, w - 0.36, 0.6],
            d.sectionLabels[i],
            'heading',
            `sectionLabels[${i}]`,
          )
        })
      } else
        tx(
          'RoadmapLabels',
          r.rail,
          d.sectionLabels.map((v, i) => `${i + 1} ${v}`).join(' / '),
          'heading',
          d.sectionLabels.map((_, i) => `sectionLabels[${i}]`),
        )
      allocation(r.allocation, d.allocation, d.allocationUnit)
      cells(r.targets, d.targets.length, id === 'stacked', 0.2).forEach(([x, y, w, h], i) => {
        const v = d.targets[i]
        tx('TargetLabel' + i, [x, y, w, 0.33], v.label, 'label', `targets[${i}].label`)
        tx(
          'TargetValue' + i,
          [x, y + 0.41, w, 0.4],
          `${number(v.baseline)} → ${number(v.target)} ${v.unit}`,
          'heading',
          [`targets[${i}].baseline`, `targets[${i}].target`, `targets[${i}].unit`],
        )
      })
      cells(r.actions, d.actions.length, id === 'stacked', 0.2).forEach(([x, y, w, h], i) => {
        const v = d.actions[i]
        rule('ActionRule' + i, x, y, w)
        tx(
          'ActionLabel' + i,
          [x, y + (id === 'stacked' ? 0.03 : 0.1), w, 0.33],
          v.label,
          'heading',
          `actions[${i}].label`,
        )
        tx(
          'ActionContext' + i,
          [x, y + (id === 'stacked' ? 0.29 : 0.52), w, id === 'stacked' ? 0.47 : 0.6],
          `${v.owner} · ${v.date}\n${v.measure}`,
          'small',
          [`actions[${i}].owner`, `actions[${i}].date`, `actions[${i}].measure`],
        )
      })
    } else throw Error('Unregistered journal role')
  }

  const mergeStack = (names, name) => {
    const parts = names.map((n) => cs.find((c) => c.name === n)).filter(Boolean)
    if (parts.length < 2) return
    const x = parts[0].frame[0],
      y = parts[0].frame[1],
      w = parts[0].frame[2],
      last = parts.at(-1),
      h = last.frame[1] + last.frame[3] - y
    const paragraphs = [],
      styles = [],
      after = [],
      paths = []
    parts.forEach((c, i) => {
      const lines = c.text.split(/\r\n|\r|\n/)
      lines.forEach((line, j) => {
        paragraphs.push(line)
        styles.push(c.paragraphStyles?.[j] ?? c.style)
        const next = i < parts.length - 1 ? parts[i + 1].frame[1] : null
        after.push(
          j === lines.length - 1 && next !== null
            ? Math.max(
                0,
                (next - c.frame[1]) * 72 -
                  lines.reduce(
                    (a, _, k) =>
                      a +
                      (c.paragraphStyles?.[k] ?? c.style).sizePt * c.style.lineHeight +
                      (k < lines.length - 1 ? (c.paragraphAfterPt?.[k] ?? 0) : 0),
                    0,
                  ),
              )
            : (c.paragraphAfterPt?.[j] ?? 0),
        )
      })
      paths.push(...c.paths)
    })
    for (const c of parts) cs.splice(cs.indexOf(c), 1)
    cs.push({
      kind: 'text',
      name,
      frame: [x, y, w, h],
      allocatedFrame: [x, y, w, h],
      text: paragraphs.join('\n'),
      style: styles[0],
      paragraphStyles: styles,
      paragraphAfterPt: after,
      paths,
      path: paths[0],
      bindings: parts.map((c) => ({
        paths: c.paths,
        frame: c.allocatedFrame ?? c.frame,
        style: c.style,
      })),
    })
  }
  if (family.role === 'anatomy') {
    for (let i = 0; i < 6; i++)
      mergeStack(['AnnotationLabel' + i, 'AnnotationDetail' + i], 'Annotation' + i)
    mergeStack(['SampleTitle', 'SampleTag'], 'SampleStory')
    mergeStack(['Annotation0', 'Annotation1', 'Annotation2'], 'AnnotationLeft')
    mergeStack(['Annotation3', 'Annotation4', 'Annotation5'], 'AnnotationRight')
  }
  if (family.role === 'results') {
    for (let i = 0; i < d.outputs.length; i++)
      mergeStack(['OutputValue' + i, 'OutputLabel' + i], 'Output' + i)
    for (let i = 0; i < d.kpis.length; i++)
      mergeStack(['KPILabel' + i, 'KPIValue' + i, 'KPIContext' + i], 'KPI' + i)
  }
  if (family.role === 'roadmap' && id === 'stacked')
    for (let i = 0; i < d.actions.length; i++)
      mergeStack(['ActionLabel' + i, 'ActionContext' + i], 'Action' + i)
  if (family.role === 'roadmap' && id === 'rail')
    for (let i = 0; i < 3; i++)
      mergeStack(['RoadmapNumber' + i, 'RoadmapLabel' + i], 'RoadmapSection' + i)
  rule('VerdictRule', 0.8, 6.38, 11.73)
  tx('Verdict', b.chrome.verdict, d.verdict, 'label', 'verdict')
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolveJournalDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.journal.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps || slide.imageSlots)
      throw Error('Journal accepts registered content only; external image input is not registered')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileJournalLayout(
            design,
            family,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
          components.push({
            ...fitTextPlan(
              `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
              design.journal.chrome.page,
              design.journal.styles.small,
              'structural.page',
            ),
            name: 'Page',
          })
          for (const c of components) {
            const [x, y, w, h] = c.frame
            if (
              [x, y, w, h].some((v) => !Number.isFinite(v)) ||
              Math.min(x, y, w, h) < 0 ||
              x + w > design.canvas.widthIn + 0.001 ||
              y + h > design.canvas.heightIn + 0.001
            )
              throw Error(`${c.name}: outside canvas`)
          }
          return [
            {
              layoutId,
              role: family.role,
              components,
              fingerprint: designHash({
                role: family.role,
                frames: components.map((c) => [c.kind, c.frame]),
              }),
            },
          ]
        } catch (e) {
          failures.push(`${layoutId}: ${e.message}`)
          return []
        }
      })
    let chosen
    try {
      chosen = selectDesignLayout(
        candidates,
        slide.layoutId ?? 'auto',
        layouts,
        design.journal.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(chosen, {
      slideIndex: s,
      slideType: slide.type,
      candidates: candidates.map((v) => v.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (chosen.repeated)
      throw Error(`slides[${s}]: repeated composition exceeds registered cadence`)
  }
  return { layouts, warnings }
}
