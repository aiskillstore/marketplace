import { designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'
export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(9)).toString()
}
const near = (a, b) => Math.abs(a - b) <= 1e-8 * Math.max(1, Math.abs(a), Math.abs(b))
export function compileSkyLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.sky,
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
  const rule = (name, x, y, w, color = 'rule', vertical = false) =>
    box(name, vertical ? [x, y, 0.009, w] : [x, y, w, 0.009], color)
  const cells = (f, n, vertical = false, g = gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const owned = (name, frame, value, color = 'accent', fields = 'label', shapeKind = 'ellipse') => {
    const c = tx(name, frame, value, 'small', fields, {
      alignment: 'center',
      color: 'paper',
      bold: true,
    })
    Object.assign(c, { kind: 'owned', color, shapeKind, anchor: 'middle' })
  }
  const notes = (f, vs, prefix = 'notes') => {
    box('ExplanationPanel', f, 'surface')
    cells([f[0] + 0.22, f[1] + 0.2, f[2] - 0.44, f[3] - 0.4], vs.length, f[3] > 2, 0.25).forEach(
      ([x, y, w, h], i) => {
        tx(
          'NoteHeading' + i,
          [x, y, w, 0.34],
          vs[i].heading,
          'noteHeading',
          `${prefix}[${i}].heading`,
        )
        tx(
          'NoteBody' + i,
          [x, y + 0.42, w, h - 0.42 - (vs[i].measure ? 0.67 : 0)],
          vs[i].body,
          'body',
          `${prefix}[${i}].body`,
        )
        if (vs[i].measure) {
          const m = vs[i].measure
          if (!(m.total > 0 && m.value >= 0 && m.value <= m.total))
            throw Error('Track requires 0 <= value <= positive total')
          box('MeasureTrack' + i, [x, y + h - 0.14, w, 0.07], 'paper')
          if (m.value)
            box('MeasureActual' + i, [x, y + h - 0.14, (w * m.value) / m.total, 0.07], 'navy')
          tx(
            'MeasureLabel' + i,
            [x, y + h - 0.55, w, 0.3],
            `${m.label}: ${number(m.value)} / ${number(m.total)} ${m.unit}`,
            'small',
            [
              `${prefix}[${i}].measure.label`,
              `${prefix}[${i}].measure.value`,
              `${prefix}[${i}].measure.total`,
              `${prefix}[${i}].measure.unit`,
            ],
            { color: 'navy' },
          )
        }
        if (i) {
          if (f[3] > 2) rule('NoteRule' + i, x, y - 0.13, w, 'rule')
          else rule('NoteRule' + i, x - 0.13, y, h, 'rule', true)
        }
      },
    )
  }
  const table = (name, f, cols, rows, paths, focus = -1, cellTones, singleLineColumns = []) => {
    if (rows.some((v) => v.length !== cols.length)) throw Error('Every row must match all columns')
    if (!Number.isInteger(focus) || focus < -1 || focus >= cols.length)
      throw Error('focusColumn outside columns')
    const sum = cols.reduce((a, v) => a + v.weight, 0),
      widths = cols.map((v) => (f[2] * v.weight) / sum)
    const all = [cols.map((v) => v.label), ...rows],
      rh = f[3] / all.length,
      bindings = []
    all.forEach((row, i) => {
      let x = f[0]
      row.forEach((value, j) => {
        const frame = [x + 0.075, f[1] + i * rh + 0.055, widths[j] - 0.15, rh - 0.11]
        if (/[\r\n]/u.test(value))
          throw Error('Native table cells require one paragraph; use automatic wrapping')
        const sourcePaths = (Array.isArray(paths(i, j)) ? paths(i, j) : [paths(i, j)]).map(
          (k) => `${path}.${k}`,
        )
        const ownerDate =
            sourcePaths.some((p) => p.endsWith('.owner')) &&
            sourcePaths.some((p) => p.endsWith('.date')),
          st = {
            ...(ownerDate || i === 0 ? b.styles.small : b.styles.table),
            bold: i === 0 || j === focus,
          }
        const fitted = fitTextPlan(value, frame, st, sourcePaths[0])
        if (i > 0 && singleLineColumns.includes(j) && fitted.estimatedLines !== 1)
          throw Error(`${sourcePaths[0]}: numeric value and unit must fit on one line`)
        bindings.push({ paths: sourcePaths, frame, style: st })
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
      cellTones,
      blueRules: true,
    })
    rule(name + 'BottomRule', f[0], f[1] + f[3] + 0.015, f[2], 'accent')
  }
  const chart = (name, f, kind, points, seriesName, paths, tones) => {
    const vals = points.map((v) => v.value)
    if (vals.some((v) => !Number.isFinite(v))) throw Error('Finite numeric evidence required')
    if (
      kind === 'doughnut' &&
      (vals.some((v) => v < 0) ||
        !near(
          vals.reduce((a, v) => a + v, 0),
          100,
        ))
    )
      throw Error('Percentage mix must reconcile to 100')
    const lo = kind === 'line' ? Math.min(...vals) : Math.min(0, ...vals),
      hi = Math.max(0, ...vals),
      span = hi - lo || 1
    cs.push({
      kind: 'chart',
      name,
      frame: f,
      chartKind: kind,
      data: {
        categories: points.map((v) => v.label),
        series: [{ name: seriesName, values: vals }],
      },
      minimum: lo < 0 ? lo - span * 0.2 : 0,
      maximum: hi + span * 0.25,
      focusPoint: vals.length - 1,
      pointTones: tones,
      seriesTone: 'accent',
      holeSize: 68,
      numberFormat: vals.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) >= 1e7))
        ? '0.00E+00'
        : vals.every(Number.isInteger)
          ? '0'
          : '0.0',
      inputPaths: paths,
    })
  }
  const pathLine = (name, f, points, { color = 'navy', dash = false, fill } = {}) =>
    cs.push({
      kind: 'path',
      name,
      frame: f,
      line: color,
      linePt: 1.2,
      dash,
      fill,
      path: {
        width: 100000,
        height: 100000,
        commands: points.map(([x, y], i) => ({
          type: i ? 'line' : 'move',
          x: Math.round(x * 100000),
          y: Math.round(y * 100000),
        })),
      },
    })
  const role = family.role
  // The tag and its text share one native shape and one geometry source.
  const tag = tx('Section', b.chrome.section, d.section, 'small', 'section', {
    alignment: 'center',
    color: 'navy',
  })
  Object.assign(tag, {
    kind: 'owned',
    color: 'highlight',
    shapeKind: 'rectangle',
    anchor: 'middle',
  })
  if (role !== 'cover') {
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Basis', b.chrome.basis, `${d.basis} · ${d.period}`, 'small', ['basis', 'period'])
  }
  if (role === 'cover') {
    const f = r.ornament
    box('CoverScopeBand', b.chrome.coverScope, 'navy')
    // Open concentric quadrants share a bottom-right origin, stop above the scope
    // strip and echo the project-page arcs without obscuring text or metadata.
    const compass = b.compass
    for (let i = 0; i < compass.arcCount; i++) {
      const scale = 1 - i * compass.radiusStep,
        w = f[2] * scale,
        h = f[3] * scale
      cs.push({
        kind: 'path',
        name: 'CoverCompassArc' + i,
        frame: [f[0] + f[2] - w, f[1] + f[3] - h, w, h],
        line: i === 0 ? 'accent' : 'pale',
        linePt: i === 0 ? compass.strokePt : compass.strokePt * 0.6,
        path: {
          width: 100000,
          height: 100000,
          commands: [
            { type: 'move', x: 100000, y: 0 },
            { type: 'cubic', x1: 44772, y1: 0, x2: 0, y2: 44772, x: 0, y: 100000 },
          ],
        },
      })
    }
    box('CoverNavigationDot', [0.67, 0.5, 0.1, 0.1], 'accent', 'circle')
    tx('CoverMasthead', [0.98, 0.43, 9.3, 0.3], d.masthead, 'small', 'masthead')
    rule('CoverMastheadRule', 0.65, 0.95, 8.6, 'highlight')
    tx(
      'CoverReportLabel',
      [r.hero[0], r.hero[1] - 0.57, r.hero[2], 0.37],
      d.reportLabel,
      'heading',
      'reportLabel',
    )
    tx('CoverTitle', r.hero, d.title, 'hero', 'title')
    box('CoverUnderline', [r.hero[0], r.hero[1] + r.hero[3] + 0.12, 1.4, 0.055], 'accent')
    tx(
      'CoverBasis',
      [r.abstract[0], r.abstract[1], r.abstract[2], 0.4],
      d.basis,
      'heading',
      'basis',
    )
    tx(
      'CoverDescription',
      [r.abstract[0], r.abstract[1] + 0.55, r.abstract[2], r.abstract[3] - 0.55],
      d.description,
      'body',
      'description',
    )
    const vertical = layoutId === 'rail'
    cells(r.metrics, d.metrics.length, vertical, 0.22).forEach(([x, y, w, h], i) => {
      tx(
        'CoverMetric' + i,
        [x, y, w, 0.44],
        `${number(d.metrics[i].actual)} / ${number(d.metrics[i].target)} ${d.metrics[i].unit}`,
        'coverMetric',
        [`metrics[${i}].actual`, `metrics[${i}].target`, `metrics[${i}].unit`],
      )
      tx(
        'CoverMetricLabel' + i,
        [x, y + 0.5, w, h - 0.5],
        d.metrics[i].label,
        'small',
        `metrics[${i}].label`,
      )
    })
    const scopeText = tx(
      'CoverPeriod',
      [
        b.chrome.coverSource[0],
        b.chrome.coverSource[1],
        b.chrome.coverSource[2],
        b.chrome.coverSource[3],
      ],
      `${d.period} · ${d.source}`,
      'small',
      ['period', 'source'],
      { color: 'paper' },
    )
    Object.assign(scopeText, {
      kind: 'owned',
      color: 'navy',
      shapeKind: 'rectangle',
      anchor: 'middle',
    })
    rule(
      'CoverVerdictRule',
      r.verdict[0],
      r.verdict[1] - 0.2,
      Math.min(r.verdict[2], r.ornament[0] - r.verdict[0] - 0.2),
      'highlight',
    )
    tx('CoverVerdict', r.verdict, d.verdict, 'body', 'verdict', { bold: true, color: 'navy' })
    return cs
  }
  if (role === 'performance') {
    const cols = d.headers.map((label, i) => ({
      label,
      weight: (layoutId === 'rail'
        ? [2.7, 1.15, 1.2, 1.2, 1.05, 3.65]
        : [2.5, 1.1, 1.1, 1.15, 1.15, 2.7]
      )[i],
      align: i > 0 && i < 5 ? 'right' : 'left',
    }))
    const rows = d.metrics.map((v) => {
      if (v.target <= 0) throw Error('Attainment target must be positive')
      return [
        `${v.label} · ${v.statusNote}`,
        `${number(v.target)} ${v.unit}`,
        `${number(v.actual)} ${v.unit}`,
        `${number(Number(((v.actual / v.target) * 100).toFixed(1)))}%`,
        v.statusLabel,
        v.note,
      ]
    })
    table(
      'Performance',
      r.table,
      cols,
      rows,
      (i, j) =>
        i
          ? j === 0
            ? [`metrics[${i - 1}].label`, `metrics[${i - 1}].statusNote`]
            : [1, 2].includes(j)
              ? [`metrics[${i - 1}].${j === 1 ? 'target' : 'actual'}`, `metrics[${i - 1}].unit`]
              : [
                  `metrics[${i - 1}].${['label', 'target', 'actual', 'target', 'statusLabel', 'note'][j]}`,
                ]
          : `headers[${j}]`,
      2,
      [
        d.headers.map(() => 'muted'),
        ...d.metrics.map((v) => ['ink', 'muted', 'navy', 'navy', v.status, 'ink']),
      ],
      [1, 2, 3],
    )
    // Render units separately only as part of the original target/actual literal cells.
    d.metrics.forEach((v, i) => {
      const rh = r.table[3] / (d.metrics.length + 1)
      box(
        'Status' + i,
        [r.table[0] - 0.23, r.table[1] + rh * (i + 1.5) - 0.07, 0.14, 0.14],
        v.status,
        'circle',
      )
      if (v.status === 'red')
        box(
          'StatusAccent' + i,
          [r.table[0] - 0.3, r.table[1] + rh * (i + 1) + 0.07, 0.045, rh - 0.14],
          'red',
        )
    })
    if (r.note) tx('PerformanceContext', r.note, d.context, 'body', 'context')
    else
      tx(
        'PerformanceContext',
        [r.table[0], r.table[1] + r.table[3] + 0.17, r.table[2], 0.4],
        d.context,
        'small',
        'context',
      )
  } else if (role === 'coverage') {
    tx(
      'SeriesHeading',
      [r.plot[0], r.plot[1], r.plot[2], 0.34],
      `${d.seriesName} · ${d.unit}`,
      'heading',
      ['seriesName', 'unit'],
    )
    const plot = [r.plot[0], r.plot[1] + 0.45, r.plot[2] * 0.7, r.plot[3] - 0.85]
    chart(
      'MixRing',
      plot,
      'doughnut',
      d.points,
      d.seriesName,
      d.points.flatMap((_, i) => [`${path}.points[${i}].label`, `${path}.points[${i}].value`]),
      ['accent', 'navy', 'pale'],
    )
    const index = d.focusIndex
    if (!Number.isInteger(index) || !d.points[index]) throw Error('focusIndex outside points')
    tx(
      'RingFocus',
      [plot[0] + plot[2] * 0.3, plot[1] + plot[3] * 0.4, plot[2] * 0.4, 0.55],
      `${number(Number(d.points[index].value.toFixed(1)))}%`,
      'number',
      `points[${index}].value`,
      { alignment: 'center' },
    )
    const leg = [r.plot[0], 5.66, r.plot[2], 0.3]
    cells(leg, d.points.length, false, 0.14).forEach(([x, y, w, h], i) => {
      box('LegendSwatch' + i, [x, y + 0.07, 0.1, 0.1], ['accent', 'navy', 'pale'][i])
      tx(
        'LegendLabel' + i,
        [x + 0.16, y, w - 0.16, h],
        `${d.points[i].label} ${number(Number(d.points[i].value.toFixed(1)))}%`,
        'small',
        [`points[${i}].label`, `points[${i}].value`],
        { color: 'ink' },
      )
    })
    tx('MixNote', [r.plot[0], 6.01, r.plot[2], 0.27], d.mixNote, 'small', 'mixNote')
    notes(r.notes, d.notes)
  } else if (role === 'ranking') {
    tx(
      'RankSeries',
      [r.plot[0], r.plot[1], r.plot[2] - 0.95, 0.34],
      `${d.seriesName} / ${d.baselineName} · ${d.unit}`,
      'heading',
      ['seriesName', 'baselineName', 'unit'],
    )
    if (!Number.isInteger(d.focusIndex) || !d.points[d.focusIndex])
      throw Error('Ranking focusIndex outside points')
    // Source-specific bullet bars: the baseline tick, value and delta all use the same source numbers.
    const [px, py, pw, ph] = r.plot,
      values = d.points.flatMap((v) => [v.value, v.baseline])
    if (values.some((v) => !Number.isFinite(v)))
      throw Error('Ranking requires all finite current and baseline values')
    const lo = Math.min(0, ...values),
      hi = Math.max(0, ...values),
      span = hi - lo || 1
    const plotX = px + 2.45,
      plotW = pw - 4.1,
      map = (v) => plotX + ((v - lo) / span) * plotW
    const rh = (ph - 0.6) / d.points.length
    tx(
      'ChangeColumn',
      [px + pw - 0.85, py + 0.04, 0.85, 0.3],
      d.changeLabel,
      'small',
      'changeLabel',
      { alignment: 'right' },
    )
    rule('RankingHeaderRule', px, py + 0.43, pw, 'accent')
    d.points.forEach((v, i) => {
      const y = py + 0.58 + i * rh,
        zero = map(0),
        end = map(v.value),
        baseline = map(v.baseline)
      tx('RankLabel' + i, [px, y, 1.6, 0.3], v.label, 'small', `points[${i}].label`, {
        color: 'ink',
        bold: i === d.focusIndex,
      })
      if (v.value !== 0 && Math.abs(end - zero) >= 1 / 914400) {
        box(
          'RankBar' + i,
          [Math.min(zero, end), y + 0.05, Math.abs(end - zero), 0.16],
          i === d.focusIndex ? 'navy' : 'accent',
        )
        cs.at(-1).numericSource = { value: v.value, baseline: v.baseline, minimum: lo, maximum: hi }
      }
      box('RankBaseline' + i, [baseline - 0.009, y + 0.01, 0.018, 0.25], 'navy')
      tx(
        'RankValue' + i,
        [
          v.value < 0 ? Math.min(end, baseline) - 0.72 : Math.max(end, baseline) + 0.05,
          y - 0.01,
          0.66,
          0.3,
        ],
        number(v.value),
        'small',
        `points[${i}].value`,
        { color: 'ink', bold: true },
      )
      cs.at(-1).numericSource = { value: v.value, baseline: v.baseline, minimum: lo, maximum: hi }
      tx(
        'RankDelta' + i,
        [px + pw - 0.9, y - 0.01, 0.9, 0.3],
        `${v.value - v.baseline > 0 ? '+' : ''}${number(v.value - v.baseline)}`,
        'small',
        [`points[${i}].baseline`, `points[${i}].value`],
        { alignment: 'right', color: 'navy', bold: i === d.focusIndex },
      )
      tx(
        'RankDetail' + i,
        [px, y + 0.32, pw, 0.25],
        `${d.baselineName} ${number(v.baseline)} ${d.unit} · ${v.detail}`,
        'small',
        ['baselineName', 'unit', `points[${i}].baseline`, `points[${i}].detail`],
      )
    })
    notes(r.notes, d.notes)
  } else if (role === 'process') {
    if (d.steps.some((v) => v.duration < 0) || d.steps.reduce((a, v) => a + v.duration, 0) <= 0)
      throw Error('Process needs nonnegative durations and positive total')
    const total = d.steps.reduce((a, v) => a + v.duration, 0)
    tx(
      'ProcessSummary',
      layoutId === 'horizontal' ? [r.summary[0], r.summary[1], 6.7, r.summary[3]] : r.summary,
      `${d.totalLabel}: ${number(total)} ${d.unit} · ${d.targetLabel}: ${number(d.target)} ${d.unit}`,
      'heading',
      ['totalLabel', 'steps', 'unit', 'targetLabel', 'target'],
    )
    const [x, y, w, h] = r.flow,
      vertical = layoutId === 'vertical',
      start = vertical ? y + 0.25 : x + 0.5,
      span = vertical ? h - 0.65 : w - 1
    let cumulative = 0
    const positions = d.steps.map((v) => {
      const pos = start + span * ((cumulative + v.duration / 2) / total)
      cumulative += v.duration
      return pos
    })
    const cy = y + h * 0.55
    if (vertical) rule('ProcessAxis', x + 0.18, start, span, 'navy', true)
    else rule('ProcessAxis', start, cy, span, 'navy')
    if (!Number.isInteger(d.focusIndex) || !d.steps[d.focusIndex])
      throw Error('Process focusIndex outside steps')
    if (vertical)
      tx(
        'ProcessTargetLabel',
        [x, y - 0.32, w, 0.27],
        `${d.targetMarkerLabel} ${number(d.target)} ${d.unit}`,
        'small',
        ['targetMarkerLabel', 'target', 'unit'],
        { color: 'navy' },
      )
    else {
      tx(
        'ProcessTargetLabel',
        [r.summary[0] + 7.1, r.summary[1], r.summary[2] - 7.1, 0.3],
        `${d.targetMarkerLabel} ${number(d.target)} ${d.unit}`,
        'small',
        ['targetMarkerLabel', 'target', 'unit'],
        { alignment: 'right', color: 'navy' },
      )
      pathLine(
        'ProcessTarget',
        [start, y - 0.4, span, 0.18],
        [
          [0, 0],
          [0, 1],
          [1, 1],
          [1, 0],
        ],
        { color: 'navy', dash: true },
      )
    }
    d.steps.forEach((v, i) => {
      const pos = vertical ? start + (span * (i + 0.5)) / d.steps.length : positions[i],
        dot = i === d.focusIndex ? 0.35 : 0.18,
        px = vertical ? x + 0.18 : pos,
        py = vertical ? pos : cy
      box(
        'ProcessNode' + i,
        [px - dot / 2, py - dot / 2, dot, dot],
        i === d.focusIndex ? 'navy' : 'accent',
        'circle',
      )
      const width =
        Math.min(
          i ? pos - positions[i - 1] : w / d.steps.length,
          i < positions.length - 1 ? positions[i + 1] - pos : w / d.steps.length,
        ) - 0.1
      const f = vertical ? [x + 0.5, pos - 0.18, w * 0.31, 0.42] : [pos - width / 2, y, width, 0.42]
      tx('StepLabel' + i, f, v.label, 'small', `steps[${i}].label`, {
        alignment: vertical ? 'left' : 'center',
        color: 'ink',
        bold: i === d.focusIndex,
      })
      tx(
        'StepValue' + i,
        vertical ? [x + w * 0.43, pos - 0.18, w * 0.18, 0.35] : [f[0], f[1] + 0.45, f[2], 0.35],
        `${number(v.duration)} ${d.unit}`,
        'heading',
        [`steps[${i}].duration`, 'unit'],
        { alignment: vertical ? 'left' : 'center', color: 'navy' },
      )
      if (vertical && v.duration > 0)
        box(
          'DurationBar' + i,
          [x + w * 0.43, pos + 0.23, (w * 0.18 * v.duration) / total, 0.06],
          'accent',
        )
      tx(
        'StepEvidence' + i,
        vertical ? [x + w * 0.67, pos - 0.18, w * 0.32, 0.42] : [f[0], cy + 0.3, f[2], 0.3],
        v.evidence,
        'small',
        `steps[${i}].evidence`,
        {
          alignment: vertical ? 'left' : 'center',
          color: v.status === 'neutral' ? 'muted' : v.status,
        },
      )
    })
    notes(r.notes, d.notes)
  } else if (role === 'diagnosis') {
    const sum = d.issues.reduce((a, v) => a + v.attribution, 0)
    if (!near(sum, d.gap)) throw Error('Issue attribution must reconcile to gap')
    const cols = d.headers.map((label, i) => ({
      label,
      weight: [0.85, 1.45, 2.8, 0.9, 1.35, 1.6][i],
      align: i === 3 ? 'right' : 'left',
    }))
    const rows = d.issues.map((v) => [
      v.statusLabel,
      v.label,
      v.evidence,
      `${number(v.attribution)} ${d.unit}`,
      `${v.owner} · ${v.date}`,
      v.action,
    ])
    table(
      'Diagnosis',
      r.table,
      cols,
      rows,
      (i, j) =>
        i
          ? j === 4
            ? [`issues[${i - 1}].owner`, `issues[${i - 1}].date`]
            : j === 3
              ? [`issues[${i - 1}].attribution`, 'unit']
              : `issues[${i - 1}].${['statusLabel', 'label', 'evidence', 'attribution', 'owner', 'action'][j]}`
          : `headers[${j}]`,
      3,
      [
        d.headers.map(() => 'muted'),
        ...d.issues.map((v) => [v.status, 'ink', 'ink', 'navy', 'ink', 'ink']),
      ],
    )
    tx(
      'Reconciliation',
      r.note,
      `${d.reconciliationLabel}: ${d.issues.map((v) => number(v.attribution)).join(' + ')} = ${number(d.gap)} ${d.unit}`,
      'small',
      ['reconciliationLabel', 'gap', 'unit', 'issues'],
    )
  } else if (role === 'actions') {
    const vertical = layoutId === 'vertical',
      f = r.items,
      [x, y, w, h] = f
    const asDate = (v) => {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) throw Error('Action dates must use YYYY-MM-DD')
      const n = Date.parse(v + 'T00:00:00Z')
      if (!Number.isFinite(n) || new Date(n).toISOString().slice(0, 10) !== v)
        throw Error('Invalid action date')
      return n
    }
    const first = asDate(d.startDate),
      last = asDate(d.endDate)
    if (last <= first) throw Error('Action time range must be positive')
    const dates = d.items.map((v) => asDate(v.date))
    if (dates.some((v, i) => v < first || v > last || (i && v <= dates[i - 1])))
      throw Error('Action dates must be ordered, distinct and inside the range')
    const timeX = (v) => x + 1.65 + ((asDate(v) - first) / (last - first)) * (w - 3.3)
    if (d.ticks.some((v) => asDate(v.date) < first || asDate(v.date) > last))
      throw Error('Timeline tick outside range')
    const axisY = y + h * 0.4
    if (vertical) {
      tx(
        'ActionTickLabels',
        [x, y - 0.3, w, 0.27],
        d.ticks.map((v) => v.label).join(' · '),
        'small',
        d.ticks.map((_, i) => `ticks[${i}].label`),
      )
      rule('ActionAxis', x + 0.2, y + 0.2, h - 0.4, 'navy', true)
    } else {
      rule('ActionAxis', x + 0.3, axisY, w - 0.6, 'navy')
      d.ticks.forEach((v, i) => {
        const xx = timeX(v.date)
        rule('MonthTick' + i, xx, axisY - 0.06, 0.12, 'navy', true)
        tx(
          'MonthLabel' + i,
          [xx - 0.4, axisY + 0.14, 0.8, 0.25],
          v.label,
          'small',
          `ticks[${i}].label`,
          { alignment: 'center' },
        )
      })
    }
    cells(f, d.items.length, vertical, 0.25).forEach(([itemX, itemY, itemWidth], i) => {
      const v = d.items[i],
        cx = vertical ? x + 0.2 : timeX(v.date),
        cy = vertical ? itemY + 0.25 : axisY
      if (!vertical) {
        const neighbor = Math.min(
          i ? cx - timeX(d.items[i - 1].date) : itemWidth,
          i < d.items.length - 1 ? timeX(d.items[i + 1].date) - cx : itemWidth,
        )
        itemWidth = Math.min(itemWidth, neighbor - 0.12)
        itemX = cx - itemWidth / 2
      }
      owned(
        'ActionNumber' + i,
        [cx - 0.16, cy - 0.16, 0.32, 0.32],
        String(i + 1),
        'accent',
        'structural.number',
      )
      if (vertical) {
        tx(
          'ActionLabel' + i,
          [itemX + 0.65, itemY + 0.02, 3.4, 0.44],
          v.label,
          'heading',
          `items[${i}].label`,
        )
        tx(
          'ActionTarget' + i,
          [itemX + 4.4, itemY + 0.02, 3.2, 0.5],
          `${number(v.baseline)} → ${number(v.target)} ${v.unit}`,
          'bandMetric',
          [`items[${i}].baseline`, `items[${i}].target`, `items[${i}].unit`],
        )
        tx(
          'ActionOwner' + i,
          [itemX + 8.2, itemY + 0.02, 3.8, 0.3],
          `${v.owner} · ${v.dateLabel}`,
          'small',
          [`items[${i}].owner`, `items[${i}].dateLabel`],
        )
        tx(
          'ActionImpact' + i,
          [itemX + 0.65, itemY + 0.62, 7.1, 0.4],
          v.impact,
          'small',
          `items[${i}].impact`,
          { color: 'navy' },
        )
        tx(
          'ActionDependency' + i,
          [itemX + 8.2, itemY + 0.62, 3.8, 0.4],
          v.dependency,
          'small',
          `items[${i}].dependency`,
          { color: 'navy' },
        )
      } else {
        tx(
          'ActionDate' + i,
          [itemX, itemY + 0.06, itemWidth, 0.3],
          v.dateLabel,
          'small',
          `items[${i}].dateLabel`,
          { alignment: 'center' },
        )
        tx(
          'ActionTarget' + i,
          [itemX, itemY + 0.48, itemWidth, 0.9],
          `${number(v.baseline)} → ${number(v.target)} ${v.unit}`,
          'bandMetric',
          [`items[${i}].baseline`, `items[${i}].target`, `items[${i}].unit`],
          { alignment: 'center' },
        )
        tx(
          'ActionLabel' + i,
          [itemX, cy + 0.5, itemWidth, 0.55],
          v.label,
          'heading',
          `items[${i}].label`,
          {
            alignment: 'center',
          },
        )
        tx(
          'ActionOwner' + i,
          [itemX, cy + 1.13, itemWidth, 0.3],
          v.owner,
          'small',
          `items[${i}].owner`,
          {
            alignment: 'center',
          },
        )
        tx(
          'ActionImpact' + i,
          [itemX, cy + 1.5, itemWidth, 0.3],
          v.impact,
          'small',
          `items[${i}].impact`,
          {
            alignment: 'center',
            color: 'navy',
          },
        )
        tx(
          'ActionDependency' + i,
          [itemX, cy + 1.9, itemWidth, 0.3],
          v.dependency,
          'small',
          `items[${i}].dependency`,
          { alignment: 'center', color: 'navy' },
        )
      }
    })
  } else if (role === 'decisions') {
    const cols = d.headers.map((label, i) => ({
      label,
      weight: [2.2, 3.2, 1.6, 2.4][i],
      align: 'left',
    }))
    table(
      'Decisions',
      r.table,
      cols,
      d.items.map((v) => [v.request, v.rationale, `${v.owner} · ${v.date}`, v.consequence]),
      (i, j) =>
        i
          ? j === 2
            ? [`items[${i - 1}].owner`, `items[${i - 1}].date`]
            : `items[${i - 1}].${['request', 'rationale', 'owner', 'consequence'][j]}`
          : `headers[${j}]`,
    )
    tx('DecisionCommitment', r.note, d.commitment, 'heading', 'commitment', { color: 'navy' })
  } else if (role === 'project') {
    const [x, y, w, h] = r.arc
    tx(
      'ProjectState',
      [x, 5.88, w, 0.3],
      `${d.statusLabel} · ${number(d.progress)}%`,
      'small',
      ['statusLabel', 'progress'],
      { color: d.status },
    )
    for (let i = 0; i < 5; i++) {
      const radius = 0.65 + i * 0.19,
        frame = [x + w - radius, y + h / 2 - radius, radius, radius * 2]
      cs.push({
        kind: 'path',
        name: 'ProjectArc' + i,
        frame,
        line: i === 4 ? 'accent' : 'pale',
        linePt: 1,
        path: {
          width: 100000,
          height: 100000,
          commands: [
            { type: 'move', x: 100000, y: 0 },
            { type: 'cubic', x1: -33333, y1: 0, x2: -33333, y2: 100000, x: 100000, y: 100000 },
          ],
        },
      })
    }
    cells(r.metadata, d.metadata.length, true, 0.15).forEach(([mx, my, mw, mh], i) => {
      tx('MetaLabel' + i, [mx, my, mw, 0.3], d.metadata[i].label, 'small', `metadata[${i}].label`)
      tx(
        'MetaValue' + i,
        [mx, my + 0.34, mw, mh - 0.34],
        d.metadata[i].value,
        'heading',
        `metadata[${i}].value`,
      )
    })
    cells(r.notes, d.items.length, true, 0.18).forEach(([nx, ny, nw], i) => {
      box('ProjectNode' + i, [nx - 0.18, ny + 0.1, 0.09, 0.09], 'accent', 'circle')
      rule('ProjectLeader' + i, nx - 0.45, ny + 0.14, 0.25, 'accent')
      tx(
        'ProjectHeading' + i,
        [nx, ny, nw, 0.35],
        d.items[i].heading,
        'heading',
        `items[${i}].heading`,
      )
      tx(
        'ProjectEvidence' + i,
        [nx, ny + 0.4, nw, 0.31],
        d.items[i].evidence,
        'body',
        `items[${i}].evidence`,
      )
      tx(
        'ProjectAction' + i,
        [nx, ny + 0.79, nw, 0.36],
        `${d.items[i].action} · ${d.items[i].owner} · ${d.items[i].date}`,
        'small',
        [`items[${i}].action`, `items[${i}].owner`, `items[${i}].date`],
      )
    })
  } else if (role === 'trend') {
    tx(
      'TrendSeries',
      [r.plot[0], r.plot[1], r.plot[2], 0.35],
      `${d.seriesName} · ${d.unit}`,
      'heading',
      ['seriesName', 'unit'],
    )
    if (
      !Number.isInteger(d.boundaryIndex) ||
      d.boundaryIndex < 0 ||
      d.boundaryIndex >= d.points.length - 1
    )
      throw Error('Trend boundaryIndex must split observed and plan categories')
    tx(
      'PeriodBoundary',
      [r.plot[0], r.plot[1] + 0.4, r.plot[2], 0.3],
      `${d.observedLabel}: ${d.points[d.boundaryIndex].label} | ${d.planLabel}: ${d.points[d.boundaryIndex + 1].label}`,
      'small',
      [
        'observedLabel',
        'planLabel',
        `points[${d.boundaryIndex}].label`,
        `points[${d.boundaryIndex + 1}].label`,
      ],
    )
    chart(
      'ObservedTrend',
      [r.plot[0], r.plot[1] + 0.8, r.plot[2], r.plot[3] - 0.8],
      'column',
      d.points,
      d.seriesName,
      d.points.flatMap((_, i) => [`${path}.points[${i}].label`, `${path}.points[${i}].value`]),
      d.points.map((_, i) =>
        i > d.boundaryIndex ? 'paper' : i === d.boundaryIndex ? 'navy' : 'accent',
      ),
    )
    cs.at(-1).forecastFrom = d.boundaryIndex
    notes(r.notes, d.notes)
  } else if (role === 'bridge') {
    if (!near(d.opening + d.drivers.reduce((a, v) => a + v.value, 0), d.closing))
      throw Error('Bridge opening + drivers must equal closing')
    const f = r.plot,
      [x, y, w, h] = f,
      all = [
        { label: d.openingLabel, value: d.opening },
        ...d.drivers,
        { label: d.closingLabel, value: d.closing },
      ],
      pos = [0, d.opening]
    let sum = d.opening
    for (const v of d.drivers) {
      sum += v.value
      pos.push(sum)
    }
    pos.push(d.closing)
    const lo = Math.min(0, ...pos),
      hi = Math.max(0, ...pos),
      span = hi - lo || 1,
      scale = (v) => y + 0.3 + (h - 0.95) * (1 - (v - lo) / span),
      slot = w / all.length
    rule('BridgeZero', x, scale(0), w, 'navy')
    sum = d.opening
    all.forEach((v, i) => {
      let from, to
      if (i === 0 || i === all.length - 1) {
        from = 0
        to = v.value
      } else {
        from = sum
        to = sum + v.value
        sum = to
      }
      const bx = x + i * slot + slot * 0.17,
        bw = slot * 0.66,
        top = Math.min(scale(from), scale(to)),
        height = Math.abs(scale(from) - scale(to))
      if (height)
        box(
          'BridgeBar' + i,
          [bx, top, bw, height],
          i === all.length - 1 ? 'accent' : i === 0 ? 'navy' : 'pale',
        )
      if (!height && i > 0 && i < all.length - 1)
        rule('BridgeZeroStep' + i, bx, scale(to), bw, 'navy')
      const labelY = Math.max(y, top - 0.39),
        endpoint = i === 0 || i === all.length - 1,
        unit = endpoint ? (d.levelUnit ?? d.unit) : d.unit
      tx(
        'BridgeValue' + i,
        [bx - 0.08, labelY, bw + 0.16, 0.36],
        `${!endpoint && v.value > 0 ? '+' : ''}${number(v.value)} ${unit}`,
        all.length <= 4 ? 'heading' : 'body',
        [
          i === 0 ? 'opening' : i === all.length - 1 ? 'closing' : `drivers[${i - 1}].value`,
          endpoint && d.levelUnit ? 'levelUnit' : 'unit',
        ],
        { alignment: 'center', color: 'navy' },
      )
      tx(
        'BridgeLabel' + i,
        [bx - 0.1, y + h - 0.42, bw + 0.2, 0.4],
        v.label,
        'small',
        i === 0
          ? 'openingLabel'
          : i === all.length - 1
            ? 'closingLabel'
            : `drivers[${i - 1}].label`,
        { alignment: 'center' },
      )
      if (i < all.length - 1) rule('BridgeConnector' + i, bx + bw, scale(to), slot * 0.34, 'navy')
    })
    notes(r.notes, d.notes)
  } else if (role === 'appendix') {
    table(
      'Appendix',
      r.table,
      d.columns,
      d.rows,
      (i, j) => (i ? `rows[${i - 1}][${j}]` : `columns[${j}].label`),
      d.focusColumn,
    )
    tx('Methodology', r.note, d.methodology, 'small', 'methodology')
  } else throw Error('Unregistered Sky Compass role')
  rule('VerdictRule', 0.65, 6.32, 12.03, 'accent')
  tx('Verdict', b.chrome.verdict, d.verdict, 'body', 'verdict', { bold: true, color: 'navy' })
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolveSkyDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'skyCoverSlide' ||
      content.slides.at(-1)?.type !== 'skyDecisionsSlide')
  )
    throw Error(
      'Complete Sky Compass decks open with verdict cover and end with decisions; use excerpt scope for extracts',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.sky.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps || slide.imageSlots)
      throw Error('Sky Compass accepts registered content only; no customOps or image slots')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileSkyLayout(
            design,
            family,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
          if (family.role !== 'cover')
            components.push({
              ...fitTextPlan(
                `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
                design.sky.chrome.page,
                design.sky.styles.small,
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
        design.sky.rhythm.maxConsecutive,
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
    if (chosen.repeated) warnings.push(`slides[${s}]: repeated composition`)
  }
  return { layouts, warnings }
}
