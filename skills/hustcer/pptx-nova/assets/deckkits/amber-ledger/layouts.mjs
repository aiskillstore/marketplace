import { designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'

export const amberNumber = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  if (n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)) return n.toExponential(2)
  return Number(n.toPrecision(8)).toString()
}
// Round tick intervals, never the observations. Keep headroom above and below the series.
export function amberTrendScale(values) {
  const lo = Math.min(...values),
    hi = Math.max(...values)
  const span = hi - lo || Math.max(1, Math.abs(hi) * 0.2)
  const raw = span / 4,
    power = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 5, 10].find((v) => v * power >= raw) * power
  return {
    minimum: Math.floor((lo - span * 0.12) / step) * step,
    maximum: Math.ceil((hi + span * 0.16) / step) * step,
    majorUnit: step,
  }
}
export function compileAmberLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.amber,
    evidence = b.evidence,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap
  const tx = (name, frame, value, key = 'body', fields = name, extra = {}) => {
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) => `${path}.${k}`)
    const c = {
      ...fitTextPlan(value, frame, { ...b.styles[key], ...extra }, paths[0]),
      name,
      paths,
    }
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule', kind = 'box') => cs.push({ kind, name, frame, color })
  const rule = (name, x, y, w, vertical = false) =>
    box(name, vertical ? [x, y, 0.009, w] : [x, y, w, 0.009])
  const cells = (f, n, vertical = false, g = gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const notes = (f, vs, vertical = true) =>
    cells(f, vs.length, vertical).forEach(([x, y, w, h], i) => {
      tx('NoteHeading' + i, [x, y, w, 0.34], vs[i].heading, 'heading', `notes[${i}].heading`)
      tx('NoteBody' + i, [x, y + 0.43, w, h - 0.43], vs[i].body, 'body', `notes[${i}].body`)
    })
  const nativeTable = (name, f, cols, rows, paths, focus = -1, tone = 'history') => {
    if (rows.some((row) => row.length !== cols.length))
      throw Error(`${path}: each row must match every registered column`)
    if (!Number.isInteger(focus) || focus < -1 || focus >= cols.length)
      throw Error(`${path}.focusColumn: outside columns`)
    const sum = cols.reduce((a, c) => a + c.weight, 0),
      widths = cols.map((c) => (f[2] * c.weight) / sum),
      rowH = f[3] / (rows.length + 1)
    const all = [cols.map((c) => c.label), ...rows],
      bindings = []
    all.forEach((row, i) => {
      let x = f[0]
      row.forEach((v, j) => {
        const inner = [x + 0.07, f[1] + i * rowH + 0.05, widths[j] - 0.14, rowH - 0.1]
        const st = {
          ...b.styles.small,
          bold: i === 0 || j === focus,
          color: j === focus && tone === 'ink' ? 'paper' : 'ink',
        }
        fitTextPlan(v, inner, st, `${path}.${paths(i, j)}`)
        bindings.push({ paths: [`${path}.${paths(i, j)}`], frame: inner, style: st })
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
      rowHeights: all.map(() => rowH),
      focusColumn: focus,
      focusTone: tone,
      bindings,
    })
  }
  const chart = (name, f, kind, points, seriesName, paths, focusPoint) => {
    const vals = points.map((v) => v.value)
    if (vals.some((v) => !Number.isFinite(v))) throw Error(`${path}: finite chart values required`)
    const lo = kind === 'line' ? Math.min(...vals) : Math.min(0, ...vals),
      hi = kind === 'line' ? Math.max(...vals) : Math.max(0, ...vals),
      span = hi - lo || Math.max(1, Math.abs(hi) * 0.2)
    // The current native renderer collapses all-sub-micro axes. Keep raw values,
    // draw an editable numeric plot, and disclose regeneration rather than altering data.
    if (
      kind !== 'doughnut' &&
      Math.max(...vals.map(Math.abs)) > 0 &&
      Math.max(...vals.map(Math.abs)) < 1e-5
    ) {
      const [x, y, w, h] = f,
        px = x + 0.7,
        py = y + 0.15,
        pw = w - 0.85,
        ph = h - 0.72
      const minimum = lo - span * 0.18,
        maximum = hi + span * 0.22,
        scale = (v) => py + ph * (1 - (v - minimum) / (maximum - minimum))
      for (const [i, v] of [minimum, (minimum + maximum) / 2, maximum].entries()) {
        rule(name + 'MicroGrid' + i, px, scale(v), pw)
        tx(
          name + 'MicroTick' + i,
          [x, scale(v) - 0.11, 0.63, 0.25],
          v.toExponential(1),
          'small',
          'unit',
          { alignment: 'right' },
        )
      }
      const slot = pw / points.length,
        coords = points.map((v, i) => [
          kind === 'line' ? px + slot / 2 + i * slot : px + slot * i,
          scale(v.value),
        ])
      if (kind === 'line')
        cs.push({
          kind: 'microLine',
          name: name + 'MicroLine',
          frame: [px, py, pw, ph],
          points: coords.map(([a, b]) => [(a - px) / pw, (b - py) / ph]),
          numericSource: vals,
        })
      points.forEach((v, i) => {
        const [a, vy] = coords[i],
          cx = kind === 'line' ? a : a + slot / 2
        if (kind === 'column' && v.value !== 0)
          box(
            name + 'MicroBar' + i,
            [a + slot * 0.2, Math.min(vy, scale(0)), slot * 0.6, Math.abs(vy - scale(0))],
            i === points.length - 1 ? 'accent' : evidence.history,
          )
        if (kind === 'line')
          box(
            name + 'MicroPoint' + i,
            [a - 0.035, vy - 0.035, 0.07, 0.07],
            i === focusPoint ? 'accent' : evidence.series,
            'circle',
          )
        tx(
          name + 'MicroValue' + i,
          [cx - slot * 0.45, Math.max(y, vy - 0.28), slot * 0.9, 0.25],
          String(v.value),
          'small',
          paths[i * 2 + 1]?.replace(path + '.', '') ?? 'unit',
          { alignment: 'center', color: 'ink' },
        )
        tx(
          name + 'MicroCategory' + i,
          [cx - slot * 0.45, py + ph + 0.15, slot * 0.9, 0.4],
          v.label,
          'small',
          paths[i * 2]?.replace(path + '.', '') ?? 'unit',
          { alignment: 'center' },
        )
      })
      return
    }
    cs.push({
      kind: 'chart',
      name,
      chartKind: kind,
      frame: f,
      data: {
        categories: points.map((v) => v.label),
        series: [{ name: seriesName, values: vals }],
      },
      minimum: kind === 'line' ? lo - span * 0.18 : lo < 0 ? lo - span * 0.18 : 0,
      maximum: hi + span * 0.22,
      numberFormat: vals.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) >= 1e7))
        ? '0.00E+00'
        : vals.every(Number.isInteger)
          ? '0'
          : `0.${'0'.repeat(Math.min(4, Math.max(...vals.map((v) => (String(v).split('.')[1] || '').length))))}`,
      inputPaths: paths,
      seriesTone: evidence.series,
      pointTones: kind === 'doughnut' ? evidence.categorical.slice(0, points.length) : undefined,
      ...(kind === 'line' ? amberTrendScale(vals) : {}),
    })
  }
  const role = family.role
  tx('Section', b.chrome.section, d.section, 'small', 'section')
  if (role !== 'cover') {
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Subtitle', b.chrome.subtitle, `${d.subtitle} | ${d.period}`, 'small', [
      'subtitle',
      'period',
    ])
    rule('HeaderRule', 0.6, 2.04, 12.05)
  }
  if (role === 'cover') {
    const [x, y, w, h] = r.ornament,
      diam = Math.min(w, h * 0.68)
    box('LargeCircle', [x, y, diam, diam], 'paper', 'circle')
    Object.assign(cs.at(-1), { outline: 'accent', linePt: b.cover.ringLinePt, hollow: true })
    box('SmallCircle', [x + w * 0.42, y + diam + 0.25, w * 0.4, w * 0.4], evidence.series, 'circle')
    Object.assign(cs.at(-1), { outline: 'gold', linePt: b.cover.smallLinePt })
    box('EdgeRail', [13.02, 0, 0.313, 7.5], evidence.series)
    box('EdgeAmber', [12.94, 0, 0.08, 7.5], 'accent')
    tx('Title', r.hero, d.title, 'hero', 'title')
    rule('CoverRule', r.hero[0], r.hero[1] + r.hero[3] + 0.05, r.hero[2])
    box('CoverAccent', [r.hero[0], r.hero[1] + r.hero[3] + 0.04, 1.1, 0.045], 'accent')
    const [dx, dy, dw, dh] = r.detail
    tx('Edition', [dx, dy, dw, 0.4], d.edition, 'heading', 'edition')
    tx('Subtitle', [dx, dy + 0.5, dw, 0.5], d.subtitle, 'heading', 'subtitle')
    tx('Description', [dx, dy + 1.03, dw, dh - 1.03], `${d.description} · ${d.period}`, 'body', [
      'description',
      'period',
    ])
    cells(r.register, d.metadata.length).forEach(([mx, my, mw, mh], i) => {
      if (i) rule('MetadataDivider' + i, mx - gap / 2, my, mh, true)
      tx(
        'MetadataLabel' + i,
        [mx, my, mw, 0.25],
        d.metadata[i].label,
        'small',
        `metadata[${i}].label`,
      )
      tx(
        'MetadataValue' + i,
        [mx, my + 0.31, mw, mh - 0.31],
        d.metadata[i].value,
        'small',
        `metadata[${i}].value`,
        { bold: true },
      )
    })
  } else if (role === 'summary') {
    const band = layoutId === 'verdictBand'
    d.metrics.forEach((v, i) => {
      const f = i < 2 ? r.metrics : r.notes
      const ff = band ? cells(r.metrics, 4)[i] : cells(f, 2, true, 0.23)[i % 2],
        [x, y, w, h] = ff
      tx('MetricLabel' + i, [x, y, w, 0.3], `${v.label} · ${v.unit}`, 'small', [
        `metrics[${i}].label`,
        `metrics[${i}].unit`,
      ])
      tx(
        'MetricValue' + i,
        [x, y + 0.35, w, 0.62],
        amberNumber(v.actual),
        'number',
        `metrics[${i}].actual`,
      )
      const ratio = v.target === 0 ? '—' : `${Number(((v.actual / v.target) * 100).toFixed(1))}%`
      tx(
        'MetricBasis' + i,
        [x, y + 0.99, w, band ? 0.48 : 0.3],
        `${d.metricKey}: ${amberNumber(v.actual)} / ${amberNumber(v.target)} · ${d.ratioLabel} ${ratio}`,
        'small',
        ['metricKey', 'ratioLabel', `metrics[${i}].actual`, `metrics[${i}].target`],
      )
      tx(
        'MetricNote' + i,
        [x, y + (band ? 1.5 : 1.34), w, h - (band ? 1.5 : 1.34)],
        v.note,
        'small',
        `metrics[${i}].note`,
      )
      rule('MetricRule' + i, x, y + h + 0.04, w)
    })
    tx('Analysis', r.analysis, d.analysis, 'quote', 'analysis')
    const [x, y, w] = r.focus
    box('FocusBlock', r.focus, 'accent')
    tx(
      'FocusLabel',
      [x + 0.16, y + 0.12, w - 0.32, 0.3],
      `${d.focus.label} · ${d.focus.unit}`,
      'small',
      ['focus.label', 'focus.unit'],
      { color: 'ink', alignment: 'center' },
    )
    tx(
      'FocusValue',
      [x + 0.16, y + 0.48, w - 0.32, 0.7],
      amberNumber(d.focus.value),
      'focus',
      'focus.value',
      { alignment: 'center' },
    )
    tx('FocusNote', [x + 0.16, y + 1.22, w - 0.32, 0.32], d.focus.note, 'small', 'focus.note', {
      color: 'ink',
      alignment: 'center',
    })
    // Notes are a distinct lower reading layer, independent of the four metrics.
    const text = d.notes.map((n) => `${n.heading}: ${n.body}`).join(' ')
    tx(
      'SummaryNotes',
      [0.6, 6.13, 12.05, 0.48],
      text,
      'small',
      d.notes.flatMap((_, i) => [`notes[${i}].heading`, `notes[${i}].body`]),
    )
    if (!band) {
      rule('SummaryDivider1', 4.95, 2.2, 3.7, true)
      rule('SummaryDivider2', 8.45, 2.2, 3.7, true)
    }
  } else if (role === 'mix') {
    tx(
      'HistoryHead',
      [r.history[0], 2.15, r.history[2], 0.28],
      `${d.seriesName} · ${d.unit}`,
      'small',
      ['seriesName', 'unit'],
    )
    chart(
      'HistoryChart',
      r.history,
      'column',
      d.history,
      d.seriesName,
      d.history.flatMap((_, i) => [`${path}.history[${i}].label`, `${path}.history[${i}].value`]),
    )
    const total = d.segments.reduce((a, v) => a + v.value, 0)
    if (!(total > 0)) throw Error(`${path}.segments: positive total required`)
    tx('MixHead', [r.ring[0], 2.13, r.ring[2], 0.28], d.mixLabel, 'small', 'mixLabel')
    chart('MixChart', r.ring, 'doughnut', d.segments, d.mixLabel, [])
    const [x, y, w, h] = r.ring
    tx(
      'RingTotal',
      [x + w * 0.25, y + h * 0.38, w * 0.5, 0.53],
      amberNumber(total),
      'number',
      'segments[].value',
      { alignment: 'center', sizePt: 25 },
    )
    tx(
      'RingTotalLabel',
      [x + w * 0.24, y + h * 0.59, w * 0.52, 0.3],
      d.totalLabel,
      'small',
      'totalLabel',
      { alignment: 'center' },
    )
    cells(r.legend, d.segments.length, true, 0.02).forEach(([lx, ly, lw, lh], i) => {
      box('LegendSwatch' + i, [lx, ly + 0.07, 0.08, 0.08], evidence.categorical[i])
      tx(
        'Legend' + i,
        [lx + 0.17, ly, lw - 0.17, lh],
        `${d.segments[i].label} ${amberNumber(d.segments[i].value)} | ${Number(((d.segments[i].value / total) * 100).toFixed(1))}%`,
        'small',
        [`segments[${i}].label`, `segments[${i}].value`],
      )
    })
    cells(r.metrics, d.metrics.length, layoutId === 'evidenceRail').forEach(
      ([mx, my, mw, mh], i) => {
        tx(
          'MixMetric' + i,
          [mx, my, mw, 0.42],
          `${d.metrics[i].value} · ${d.metrics[i].label}`,
          'heading',
          [`metrics[${i}].value`, `metrics[${i}].label`],
        )
        tx(
          'MixMetricNote' + i,
          [mx, my + 0.47, mw, mh - 0.47],
          d.metrics[i].note,
          'small',
          `metrics[${i}].note`,
        )
      },
    )
  } else if (role === 'trend') {
    const a = d.annotation
    if (
      !Number.isInteger(a.from) ||
      !Number.isInteger(a.to) ||
      a.to < a.from ||
      a.to >= d.points.length
    )
      throw Error(`${path}.annotation: valid ordered category indices required`)
    tx(
      'TrendHead',
      [r.chart[0], r.chart[1] - 0.31, r.chart[2], 0.28],
      `${d.seriesName} · ${d.unit}`,
      'small',
      ['seriesName', 'unit'],
    )
    chart(
      'TrendChart',
      r.chart,
      'line',
      d.points,
      d.seriesName,
      d.points.flatMap((_, i) => [`${path}.points[${i}].label`, `${path}.points[${i}].value`]),
      a.to,
    )
    if (cs.at(-1).kind === 'chart') cs.at(-1).focusPoint = a.to
    notes(r.notes, d.notes, layoutId === 'chartRail')
    tx(
      'PeriodAnnotation',
      r.annotation,
      `${d.points[a.from].label}–${d.points[a.to].label}: ${a.text}`,
      'small',
      ['annotation.text', `points[${a.from}].label`, `points[${a.to}].label`],
    )
  } else if (role === 'bridge') {
    if (d.steps.filter((v) => v.focus).length > 1)
      throw Error(`${path}.steps: maximum one focal driver`)
    const sum = d.start + d.steps.reduce((a, v) => a + v.value, 0)
    if (Math.abs(sum - d.end) > 1e-9 * Math.max(1, Math.abs(sum), Math.abs(d.end)))
      throw Error(`${path}.end: bridge does not reconcile`)
    tx(
      'BridgeHead',
      [r.bridge[0], r.bridge[1] - 0.35, r.bridge[2], 0.28],
      `${d.seriesName} · ${d.unit}`,
      'small',
      ['seriesName', 'unit'],
    )
    let running = d.start
    const vs = [
      {
        label: d.startLabel,
        value: d.start,
        from: d.baseline,
        to: d.start,
        paths: ['startLabel', 'start'],
      },
      ...d.steps.map((v, i) => {
        const from = running
        running += v.value
        return { ...v, from, to: running, paths: [`steps[${i}].label`, `steps[${i}].value`] }
      }),
      { label: d.endLabel, value: d.end, from: d.baseline, to: d.end, paths: ['endLabel', 'end'] },
    ]
    const values = vs.flatMap((v) => [v.from, v.to])
    if (
      !Number.isFinite(d.baseline) ||
      d.baseline >= Math.min(d.start, ...vs.slice(1, -1).flatMap((v) => [v.from, v.to]), d.end)
    )
      throw Error(`${path}.baseline: must be below every running total`)
    const lo = d.baseline,
      hi = Math.max(...values) + (Math.max(...values) - lo) * 0.08,
      span = hi - lo || 1
    const [x, y, w, h] = r.bridge,
      plotH = h - 0.95,
      scale = (v) => y + 0.35 + plotH * (1 - (v - lo) / span),
      slots = cells([x + 0.43, y, w - 0.43, h], vs.length, false, 0.18)
    for (const [i, v] of [lo, (lo + hi) / 2, hi].entries()) {
      rule('BridgeGrid' + i, x + 0.43, scale(v), w - 0.43)
      tx(
        'BridgeTick' + i,
        [x, scale(v) - 0.1, 0.39, 0.25],
        Number(v.toFixed(1)).toString(),
        'small',
        'baseline',
        { alignment: 'right' },
      )
    }
    vs.forEach((v, i) => {
      const [bx, , bw] = slots[i],
        by = scale(Math.max(v.from, v.to)),
        bh = (Math.abs(v.to - v.from) / span) * plotH
      if (bh > 0)
        box(
          'BridgeBar' + i,
          [bx, by, bw, bh],
          i === 0 || i === vs.length - 1 ? evidence.series : v.focus ? 'accent' : evidence.history,
        )
      tx(
        'BridgeValue' + i,
        [bx, Math.max(y, by - 0.25), bw, 0.25],
        `${i > 0 && i < vs.length - 1 && v.value > 0 ? '+' : ''}${amberNumber(v.value)}`,
        'small',
        v.paths[1],
        { alignment: 'center', color: 'ink', bold: true },
      )
      tx('BridgeLabel' + i, [bx, y + 0.35 + plotH + 0.12, bw, 0.48], v.label, 'small', v.paths[0], {
        alignment: 'center',
      })
      if (i < vs.length - 1) rule('BridgeConnector' + i, bx + bw, scale(v.to), 0.18)
    })
    tx('BridgeAnalysis', r.analysis, d.analysis, 'body', 'analysis')
    nativeTable('BenchmarkTable', r.table, d.tableColumns, d.tableRows, (i, j) =>
      i === 0 ? `tableColumns[${j}].label` : `tableRows[${i - 1}][${j}]`,
    )
    tx('BenchmarkNote', r.note, d.tableNote, 'small', 'tableNote')
  } else if (role === 'projects') {
    const columns = layoutId === 'progressColumns'
    cells(r.projects, d.projects.length, !columns, 0.25).forEach(([x, y, w, h], i) => {
      const v = d.projects[i],
        p = `projects[${i}]`
      tx('ProjectTitle' + i, [x, y, columns ? w : 3.25, 0.35], v.title, 'heading', p + '.title')
      const bx = columns ? x : x + 3.6,
        by = columns ? y + 0.62 : y + 0.08,
        bw = columns ? w : w - 3.6
      box('ProgressTrack' + i, [bx, by, bw, 0.16], evidence.track)
      if (v.actual > 0)
        box('ActualProgress' + i, [bx, by, (bw * v.actual) / 100, 0.16], evidence.series)
      box(
        'PlanTick' + i,
        [bx + Math.min(bw - 0.025, (bw * v.plan) / 100), by - 0.07, 0.025, 0.3],
        evidence.plan,
      )
      tx(
        'ProgressValues' + i,
        [bx, by + 0.31, bw, 0.3],
        `${d.actualLabel} ${amberNumber(v.actual)}% / ${d.planLabel} ${amberNumber(v.plan)}%`,
        'small',
        ['actualLabel', 'planLabel', p + '.actual', p + '.plan'],
      )
      if (columns) {
        tx('ProjectStatus' + i, [x, y + 1.3, w, 0.34], v.status, 'heading', p + '.status')
        tx('ProjectEvidence' + i, [x, y + 1.8, w, 0.6], v.evidence, 'body', p + '.evidence')
        tx('ProjectAction' + i, [x, y + 2.55, w, 0.55], v.action, 'body', p + '.action')
        tx('ProjectOwner' + i, [x, y + h - 0.35, w, 0.3], `${v.owner} | ${v.date}`, 'small', [
          p + '.owner',
          p + '.date',
        ])
      } else {
        const detail = `${v.status} · ${v.evidence} | ${v.action} | ${v.owner} | ${v.date}`
        tx('ProjectDetail' + i, [x, y + 0.73, w, h - 0.73], detail, 'small', [
          p + '.status',
          p + '.evidence',
          p + '.action',
          p + '.owner',
          p + '.date',
        ])
      }
      if (columns && i) rule('ProjectDivider' + i, x - 0.13, y, h, true)
    })
    rule('RecoveryRule', r.recovery[0], r.recovery[1] - 0.15, r.recovery[2])
    tx('Recovery', r.recovery, d.recovery, 'body', 'recovery')
  } else if (role === 'matrix') {
    nativeTable(
      'ScenarioTable',
      r.table,
      d.columns,
      d.rows,
      (i, j) => (i === 0 ? `columns[${j}].label` : `rows[${i - 1}][${j}]`),
      d.focusColumn,
      evidence.focusTones[d.focusTone],
    )
    tx('MatrixNote', r.note, d.note, 'body', 'note')
  } else if (role === 'decisions') {
    if (layoutId === 'decisionTable') {
      const keys = ['request', 'rationale', 'consequence', 'deadline'],
        weights = [2.7, 2.4, 2.4, 1.4]
      nativeTable(
        'DecisionTable',
        r.items,
        d.headers.map((label, i) => ({ label, weight: weights[i], align: 'left' })),
        d.items.map((v) => keys.map((k) => v[k])),
        (i, j) => (i === 0 ? `headers[${j}]` : `items[${i - 1}].${keys[j]}`),
      )
    } else {
      cells(r.items, d.items.length, true, 0.15).forEach(([x, y, w, h], i) => {
        rule('DecisionRule' + i, x, y, w)
        tx(
          'DecisionRequest' + i,
          [x, y + 0.12, w * 0.3, h - 0.12],
          `${d.headers[0]} ${i + 1}. ${d.items[i].request}`,
          'heading',
          ['headers[0]', `items[${i}].request`],
        )
        const keys = ['rationale', 'consequence', 'deadline']
        cells([x + w * 0.33, y + 0.12, w * 0.67, h - 0.12], 3).forEach(([dx, dy, dw, dh], j) =>
          tx(
            'DecisionDetail' + i + '_' + j,
            [dx, dy, dw, dh],
            `${d.headers[j + 1]}: ${d.items[i][keys[j]]}`,
            'small',
            [`headers[${j + 1}]`, `items[${i}].${keys[j]}`],
          ),
        )
      })
    }
    tx('Closing', r.closing, d.closing, 'quote', 'closing', { sizePt: 16 })
  } else throw Error(`Unregistered Amber Ledger role: ${role}`)
  rule('VerdictRule', 0.6, 6.85, 12.05)
  tx('Verdict', b.chrome.verdict, d.verdict, 'small', 'verdict')
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolveAmberDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'amberCoverSlide' ||
      content.slides.at(-1)?.type !== 'amberDecisionsSlide')
  )
    throw Error(
      'Complete Amber Ledger decks open with cover and end with decisions; excerpts require designScope excerpt',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.amber.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps) throw Error(`slides[${s}]: customOps forbidden`)
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileAmberLayout(
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
              design.amber.chrome.page,
              { ...design.amber.styles.small, color: 'ink', alignment: 'right' },
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
        design.amber.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(chosen, {
      slideIndex: s,
      slideType: slide.type,
      candidates: candidates.map((c) => c.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (chosen.repeated) warnings.push(`slides[${s}]: repeated composition`)
  }
  return { layouts, warnings }
}
