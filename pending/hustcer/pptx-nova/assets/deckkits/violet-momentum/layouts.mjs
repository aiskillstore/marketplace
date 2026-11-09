import { designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'
export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(9)).toString()
}
const near = (a, b) => Math.abs(a - b) <= 1e-8 * Math.max(1, Math.abs(a), Math.abs(b))
export function compileVioletLayout(design, family, id, variant, d, path = 'data') {
  const b = design.violet,
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
    box(name, vertical ? [x, y, 0.008, w] : [x, y, w, 0.008], color)
  const cells = (f, n, vertical = false, g = gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const owned = (
    name,
    f,
    text,
    fields,
    key = 'body',
    color = 'accent',
    shapeKind = 'ellipse',
    extra = {},
  ) => {
    const c = tx(name, f, text, key, fields, {
      color: 'paper',
      bold: true,
      alignment: 'center',
      ...extra,
    })
    Object.assign(c, { kind: 'owned', color, shapeKind, anchor: 'middle' })
  }
  const line = (name, a, z, color = 'accent', dash = false) => {
    const x = Math.min(a[0], z[0]),
      y = Math.min(a[1], z[1]),
      w = Math.max(0.005, Math.abs(z[0] - a[0])),
      h = Math.max(0.005, Math.abs(z[1] - a[1]))
    cs.push({
      kind: 'path',
      name,
      frame: [x, y, w, h],
      line: color,
      linePt: 0.75,
      dash,
      path: {
        width: 100000,
        height: 100000,
        commands: [
          {
            type: 'move',
            x: Math.round(((a[0] - x) / w) * 1e5),
            y: Math.round(((a[1] - y) / h) * 1e5),
          },
          {
            type: 'line',
            x: Math.round(((z[0] - x) / w) * 1e5),
            y: Math.round(((z[1] - y) / h) * 1e5),
          },
        ],
      },
    })
  }
  const outline = (name, f, color = 'accent') =>
    cs.push({
      kind: 'path',
      name,
      frame: f,
      line: color,
      linePt: 0.7,
      path: {
        width: 100000,
        height: 100000,
        commands: [
          { type: 'move', x: 0, y: 0 },
          { type: 'line', x: 100000, y: 0 },
          { type: 'line', x: 100000, y: 100000 },
          { type: 'line', x: 0, y: 100000 },
          { type: 'close' },
        ],
      },
    })
  const status = (name, x, y, value, label, fields, w = 2) => {
    box(
      name + 'Mark',
      [x, y + 0.075, 0.11, 0.11],
      value === 'positive' ? 'accent' : 'ink',
      'circle',
    )
    tx(name + 'Label', [x + 0.2, y, w - 0.2, 0.32], label, 'small', fields, {
      bold: true,
      color: value === 'positive' ? 'accent' : 'ink',
    })
  }
  const metric = (name, f, m, p, white = false) => {
    const [x, y, w, h] = f
    tx(name + 'Value', [x, y, w, 0.65], number(m.actual), 'metric', `${p}.actual`, {
      color: white ? 'paper' : 'ink',
    })
    tx(
      name + 'Label',
      [x, y + 0.72, w, 0.38],
      `${m.label} · ${m.unit}`,
      'small',
      [`${p}.label`, `${p}.unit`],
      {
        color: white ? 'paper' : 'muted',
      },
    )
    tx(
      name + 'Target',
      [x, y + 1.12, w, h - 1.12],
      `${m.targetLabel} ${number(m.target)} ${m.unit}`,
      'small',
      [`${p}.targetLabel`, `${p}.target`, `${p}.unit`],
      { color: white ? 'paper' : 'muted' },
    )
  }
  const notes = (f, values) =>
    cells(f, values.length, f[3] > 1).forEach(([x, y, w, h], i) => {
      rule('NoteTick' + i, x, y, 0.65, 'accent', true)
      tx('Note' + i, [x + 0.14, y, w - 0.14, h], values[i], 'body', `notes[${i}]`)
    })
  const table = (name, f, headers, rows, weights, paths, align) => {
    const padding = b.spacing.tablePaddingIn,
      sum = weights.reduce((a, v) => a + v, 0),
      widths = weights.map((v) => (f[2] * v) / sum),
      all = [headers, ...rows],
      rh = f[3] / all.length,
      bindings = []
    all.forEach((row, i) => {
      let x = f[0]
      row.forEach((value, j) => {
        const st = {
            ...b.styles.small,
            bold: i === 0 || (i > 0 && j === (name === 'SummaryTable' ? 1 : 2)),
            color: i > 0 && j === (name === 'SummaryTable' ? 1 : 2) ? 'accent' : 'ink',
          },
          frame = [x + padding, f[1] + i * rh + 0.065, widths[j] - 2 * padding, rh - 0.13],
          sourcePaths = (Array.isArray(paths(i, j)) ? paths(i, j) : [paths(i, j)]).map(
            (k) => `${path}.${k}`,
          )
        fitTextPlan(value, frame, st, sourcePaths[0])
        bindings.push({ paths: sourcePaths, frame, style: st })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name,
      frame: f,
      cells: all,
      columns: headers.map((label, i) => ({ label, align: align?.[i] ?? 'left' })),
      widths,
      rowHeights: all.map(() => rh),
      focusColumn: -1,
      cellTones: all.map((row, i) =>
        row.map((_, j) => (i > 0 && j === (name === 'SummaryTable' ? 1 : 2) ? 'accent' : 'ink')),
      ),
      bindings,
    })
    rule(name + 'TopRule', f[0], f[1] + rh, f[2], 'ink')
  }
  const role = family.role
  if (role === 'cover') {
    const split = id === 'split'
    box('StatementField', split ? [0, 0, 8.333, 6.89] : [0, 0, 13.333, 4.05], 'ink')
    box('CoverStrip', [0, 6.89, 13.333, 0.61], 'accent')
    rule('TitleTick', r.statement[0] - 0.18, r.statement[1], r.statement[3], 'accent', true)
    tx('CoverEyebrow', [0.88, 0.6, split ? 6.7 : 11.6, 0.34], d.eyebrow, 'small', 'eyebrow', {
      color: 'paper',
    })
    tx('CoverTitle', r.statement, d.title, 'hero', 'title')
    tx('CoverDescription', r.description, d.description, 'white', 'description')
    tx(
      'CoverVerdict',
      [0.88, split ? 5.92 : 3.38, split ? 6.7 : 11.6, 0.52],
      d.verdict,
      'white',
      'verdict',
      { bold: true },
    )
    tx(
      'CoverMetricHead',
      split ? [9.02, 0.8, 3.55, 0.55] : [1.32, 4.15, 11.28, 0.3],
      d.metricHeading,
      'small',
      'metricHeading',
    )
    rule('MetricHeadRule', split ? 9.02 : 1.32, split ? 1.55 : 4.55, split ? 3.55 : 11.28, 'accent')
    if (split) {
      const f = r.metrics,
        cellW = (f[2] - 0.32) / 2,
        cellH = (f[3] - 0.35) / 2
      d.metrics.forEach((m, i) =>
        metric(
          'Metric' + i,
          [
            f[0] + (i % 2) * (cellW + 0.32),
            f[1] + Math.floor(i / 2) * (cellH + 0.35),
            d.metrics.length === 3 && i === 2 ? f[2] : cellW,
            cellH,
          ],
          m,
          `metrics[${i}]`,
        ),
      )
      rule('MetricGridH', f[0], f[1] + cellH + 0.14, f[2])
      rule(
        'MetricGridV',
        f[0] + cellW + 0.16,
        f[1],
        d.metrics.length === 3 ? cellH : f[3],
        'rule',
        true,
      )
    } else
      cells(r.metrics, d.metrics.length).forEach((f, i) =>
        metric('Metric' + i, f, d.metrics[i], `metrics[${i}]`),
      )
    tx('CoverPeriod', [0.88, 6.46, split ? 6.7 : 11.6, 0.28], d.period, 'small', 'period', {
      color: split ? 'paper' : 'muted',
    })
    tx('CoverSource', [0.88, 7.04, 11.6, 0.28], d.source, 'small', 'source', {
      color: 'paper',
      alignment: 'center',
    })
    return cs
  }
  if (role === 'section') {
    box('SectionBackground', [0, 0, 13.333, 7.5], 'accent')
    tx('SectionTitle', r.statement, `${String(d.index).padStart(2, '0')}—${d.title}`, 'section', [
      'index',
      'title',
    ])
    tx('SectionDescription', r.description, d.description, 'white', 'description')
    tx(
      'SectionSource',
      b.chrome.source,
      `${d.period} · ${d.source}`,
      'small',
      ['period', 'source'],
      { color: 'paper' },
    )
    return cs
  }
  tx('Title', b.chrome.title, d.title, 'title', 'title')
  tx('Basis', b.chrome.basis, `${d.period} · ${d.basis}`, 'small', ['period', 'basis'])
  if (role === 'summary') {
    const [x, y, w, h] = r.judgment
    rule('JudgmentTick', x, y, h, 'accent', true)
    tx(
      'Judgment',
      [x + 0.17, y, w - 0.17, id === 'band' ? 0.44 : 0.75],
      d.judgment,
      'heading',
      'judgment',
    )
    tx(
      'JudgmentDetail',
      [x + 0.17, y + (id === 'band' ? 0.53 : 0.95), w - 0.17, id === 'band' ? 0.4 : h - 0.95],
      d.description,
      'body',
      'description',
    )
    const rows = d.metrics.map((m) => [
      m.label,
      `${number(m.actual)} ${m.unit}`,
      `${number(m.target)} ${m.unit}`,
      `${number(m.actual - m.target)} ${m.gapUnit}`,
      m.statusLabel,
    ])
    table(
      'SummaryTable',
      r.table,
      d.headers,
      rows,
      [1.6, 1.7, 1.7, 1.55, 1.4],
      (i, j) =>
        i
          ? [
              `metrics[${i - 1}].${['label', 'actual', 'target', 'actual', 'statusLabel'][j]}`,
              ...([1, 2, 3].includes(j)
                ? [`metrics[${i - 1}].${j === 3 ? 'gapUnit' : 'unit'}`]
                : []),
            ]
          : `headers[${j}]`,
      ['left', 'right', 'right', 'right', 'left'],
    )
  } else if (role === 'scorecard') {
    table(
      'Scorecard',
      r.table,
      d.headers,
      d.rows,
      [2.4, 1, 1, 1.3, 1.2, 3.4],
      (i, j) => (i ? `rows[${i - 1}][${j}]` : `headers[${j}]`),
      ['left', 'right', 'right', 'right', 'left', 'left'],
    )
  } else if (role === 'trend') {
    const f = r.plot,
      vals = d.points.map((v) => v.value),
      lo = Math.min(0, ...vals),
      hi = Math.max(0, ...vals),
      span = hi - lo || 1
    if (
      !Number.isInteger(d.boundaryIndex) ||
      d.boundaryIndex < 0 ||
      d.boundaryIndex >= d.points.length - 1
    )
      throw Error('boundaryIndex must divide observed periods')
    tx('ChartSeries', [f[0], 2.03, f[2] * 0.42, 0.3], `${d.seriesName} · ${d.unit}`, 'small', [
      'seriesName',
      'unit',
    ])
    cs.push({
      kind: 'chart',
      name: 'TrendChart',
      frame: f,
      chartKind: 'column',
      data: {
        categories: d.points.map((v) => v.label),
        series: [{ name: d.seriesName, values: vals }],
      },
      minimum: lo < 0 ? lo - span * 0.22 : 0,
      maximum: hi + span * 0.24,
      uniformSeriesTone: 'accent',
      seriesTone: 'accent',
      numberFormat: vals.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) >= 1e7))
        ? '0.00E+00'
        : vals.every(Number.isInteger)
          ? '0'
          : '0.0',
      showValues: true,
      inputPaths: d.points.flatMap((_, i) => [
        `${path}.points[${i}].label`,
        `${path}.points[${i}].value`,
      ]),
    })
    // Verified canonical plot insets for the current classic column renderer; native-host parity is reviewed separately.
    const plot = [f[0] + 0.1, f[1] + 0.07, f[2] - 0.25, f[3] - 0.42],
      bx = plot[0] + (plot[2] * (d.boundaryIndex + 1)) / d.points.length
    line('PeriodBoundary', [bx, plot[1]], [bx, plot[1] + plot[3]], 'muted', true)
    if (
      d.events.some(
        (e) => !Number.isInteger(e.index) || e.index < 0 || e.index >= d.points.length,
      ) ||
      new Set(d.events.map((e) => e.index)).size !== d.events.length
    )
      throw Error('Events require distinct valid point indices')
    d.events.forEach((e, i) => {
      const ex = plot[0] + (plot[2] * (e.index + 0.5)) / d.points.length,
        ey =
          plot[1] +
          plot[3] *
            (1 -
              (vals[e.index] - (lo < 0 ? lo - span * 0.22 : 0)) /
                (hi + span * 0.24 - (lo < 0 ? lo - span * 0.22 : 0))),
        lx = Math.max(plot[0], Math.min(ex - 1.1, plot[0] + plot[2] - 2.5)),
        ly = Math.max(plot[1], ey - 0.72)
      tx('Inflection' + i, [lx, ly, 2.5, 0.3], e.label, 'small', `events[${i}].label`, {
        bold: true,
      })
    })
    tx(
      'Boundary',
      [f[0] + f[2] * 0.44, f[1] - 0.4, f[2] * 0.56, 0.3],
      `${d.beforeLabel} ${d.points[d.boundaryIndex].label} | ${d.afterLabel} ${d.points[d.boundaryIndex + 1].label}`,
      'small',
      [
        'beforeLabel',
        'afterLabel',
        `points[${d.boundaryIndex}].label`,
        `points[${d.boundaryIndex + 1}].label`,
      ],
    )
    notes(r.notes, d.notes)
  } else if (role === 'attribution') {
    if (
      !near(
        d.drivers.reduce((a, v) => a + v.value, 0),
        d.total,
      )
    )
      throw Error('Attribution drivers must sum to total')
    notes(r.notes, d.notes)
    const [cx, cy, cw, ch] = r.total
    cells(r.drivers, d.drivers.length, true, id === 'stack' ? 0.12 : 0.16).forEach(
      ([x, y, w, h], i) => {
        const v = d.drivers[i]
        tx('DriverLabel' + i, [x, y, w * 0.59, 0.33], v.label, 'body', `drivers[${i}].label`, {
          bold: true,
        })
        tx(
          'DriverValue' + i,
          [x + w * 0.61, y, w * 0.36, 0.4],
          number(v.value),
          'heading',
          `drivers[${i}].value`,
          { color: 'accent', alignment: 'right' },
        )
        tx(
          'DriverEvidence' + i,
          [x, y + 0.36, w * 0.84, h - 0.36],
          v.evidence,
          'small',
          `drivers[${i}].evidence`,
        )
        line('Convergence' + i, [x + w, y + 0.18], [cx, cy + ch / 2])
      },
    )
    fitTextPlan(number(d.total), [cx, cy, cw * 0.75, 0.55], b.styles.metric, path + '.total')
    owned('TotalBubble', r.total, `${number(d.total)}\n${d.unit}`, ['total', 'unit'], 'body')
    cs.at(-1).paragraphStyles = [
      { ...b.styles.metric, color: 'paper' },
      { ...b.styles.small, color: 'paper' },
    ]
    tx('TotalLabel', [cx - 0.3, cy - 0.45, cw + 0.6, 0.34], d.totalLabel, 'small', 'totalLabel', {
      alignment: 'center',
    })
  } else if (role === 'diagnosis') {
    tx('DiagnosisContext', r.context, d.context, 'body', 'context')
    const horizontal = id === 'columns'
    cells(r.cases, d.cases.length, !horizontal, 0.28).forEach(([x, y, w, h], i) => {
      const v = d.cases[i],
        p = `cases[${i}]`
      if (horizontal) {
        if (i) rule('CaseDivider' + i, x - 0.14, y, h - 0.18, 'rule', true)
        tx('CaseName' + i, [x, y, w, 0.4], v.name, 'heading', p + '.name')
        status('CaseStatus' + i, x, y + 0.49, v.state, v.statusLabel, p + '.statusLabel', w)
        tx('CaseActual' + i, [x, y + 0.98, w, 0.54], `${number(v.actual)} ${v.unit}`, 'metric', [
          p + '.actual',
          p + '.unit',
        ])
        tx(
          'CaseTarget' + i,
          [x, y + 1.56, w, 0.35],
          `${v.targetLabel} ${number(v.target)} ${v.unit}`,
          'small',
          [p + '.targetLabel', p + '.target', p + '.unit'],
        )
        rule('CaseRule' + i, x, y + 2, w)
        tx('CaseEvidence' + i, [x, y + 2.16, w, 0.65], v.evidence, 'small', p + '.evidence')
        tx('CaseAction' + i, [x, y + 2.95, w, h - 2.95], v.action, 'body', p + '.action')
      } else {
        rule('CaseRowRule' + i, x, y + h, w)
        tx('CaseName' + i, [x, y, w * 0.25, 0.4], v.name, 'heading', p + '.name')
        status('CaseStatus' + i, x, y + 0.49, v.state, v.statusLabel, p + '.statusLabel', w * 0.27)
        tx(
          'CaseActual' + i,
          [x + w * 0.3, y, w * 0.31, 0.45],
          `${number(v.actual)} ${v.unit}`,
          'heading',
          [p + '.actual', p + '.unit'],
        )
        tx(
          'CaseTarget' + i,
          [x + w * 0.3, y + 0.5, w * 0.31, 0.32],
          `${v.targetLabel} ${number(v.target)} ${v.unit}`,
          'small',
          [p + '.targetLabel', p + '.target', p + '.unit'],
        )
        tx(
          'CaseEvidence' + i,
          [x + w * 0.66, y, w * 0.34, 0.44],
          v.evidence,
          'small',
          p + '.evidence',
        )
        tx(
          'CaseAction' + i,
          [x + w * 0.66, y + 0.5, w * 0.34, h - 0.5],
          v.action,
          'small',
          p + '.action',
        )
      }
    })
  } else if (role === 'projects') {
    const vertical = id === 'rows'
    tx(
      'ProjectProgressHeading',
      [
        r.projects[0] + (vertical ? 3 : 0),
        r.projects[1] - 0.3,
        vertical ? 4.7 : r.projects[2],
        0.28,
      ],
      d.progressLabel ?? 'Completion',
      'small',
      'progressLabel',
    )
    cells(r.projects, d.projects.length, vertical, 0.28).forEach(([x, y, w, h], i) => {
      const v = d.projects[i],
        p = `projects[${i}]`
      if (v.progress < 0 || v.progress > 100) throw Error('Progress must lie within 0–100')
      status(
        'ProjectStatus' + i,
        x,
        y,
        v.state,
        v.statusLabel,
        p + '.statusLabel',
        vertical ? 2.5 : w,
      )
      tx(
        'ProjectName' + i,
        [x, y + 0.38, vertical ? 2.65 : w, vertical ? 0.75 : 0.7],
        v.name,
        'heading',
        p + '.name',
      )
      const bx = vertical ? x + 3.0 : x,
        by = vertical ? y + 0.05 : y + 1.1,
        bw = vertical ? 4.55 : w - 1.02
      outline('ProjectTrack' + i, [bx, by, bw, 0.18])
      if (v.progress)
        box(
          'ProjectFill' + i,
          [bx + 0.025, by + 0.025, ((bw - 0.05) * v.progress) / 100, 0.13],
          'accent',
        )
      tx(
        'ProjectPercent' + i,
        [bx + bw + 0.12, by - 0.03, 0.8, 0.3],
        number(v.progress) + '%',
        'small',
        p + '.progress',
        { bold: true, color: 'accent' },
      )
      tx(
        'ProjectEvidence' + i,
        [bx, by + 0.35, vertical ? 4.7 : w, vertical ? 0.8 : 1.2],
        v.evidence + '\n' + v.blocker,
        'small',
        [p + '.evidence', p + '.blocker'],
      )
      const ax = vertical ? x + 8.65 : x,
        ay = vertical ? y : y + 2.78
      const response = tx(
        'ProjectResponse' + i,
        [ax, ay, vertical ? 2.63 : w, vertical ? 1.12 : 0.98],
        v.action + '\n' + v.owner + ' · ' + v.date,
        'body',
        [p + '.action', p + '.owner', p + '.date'],
      )
      response.paragraphStyles = [{ ...b.styles.body }, { ...b.styles.small }]
      if (i)
        rule(
          'ProjectRule' + i,
          vertical ? x : x - 0.14,
          vertical ? y - 0.14 : y,
          vertical ? w : h,
          'rule',
          !vertical,
        )
    })
  } else if (role === 'actions') {
    const horizontal = id === 'timeline',
      f = r.phases
    if (horizontal) rule('TimelineAxis', f[0], f[1] + 0.44, f[2], 'ink')
    else rule('TimelineAxis', f[0] + 0.08, f[1] + 0.12, f[3] - 0.24, 'ink', true)
    cells(f, d.phases.length, !horizontal, 0.28).forEach(([x, y, w, h], i) => {
      const v = d.phases[i],
        p = `phases[${i}]`
      if (horizontal) {
        box('TimelineNode' + i, [x + w / 2 - 0.065, y + 0.38, 0.13, 0.13], 'accent', 'circle')
        tx(
          'PhaseDate' + i,
          [x, y - 0.05, w, 0.35],
          `${v.date} · ${v.label}`,
          'body',
          [p + '.date', p + '.label'],
          { alignment: 'center', bold: true },
        )
        tx('PhaseAction' + i, [x, y + 0.68, w, 0.5], v.action, 'body', p + '.action')
        tx('PhaseImpact' + i, [x, y + 1.24, w, 0.42], `${v.owner} · ${v.impact}`, 'small', [
          p + '.owner',
          p + '.impact',
        ])
      } else {
        box('TimelineNode' + i, [x + 0.02, y + 0.11, 0.13, 0.13], 'accent', 'circle')
        const c = tx(
          'PhaseContent' + i,
          [x + 0.3, y, w - 0.3, h],
          v.date + ' · ' + v.label + '\n' + v.action + '\n' + v.owner + ' · ' + v.impact,
          'body',
          [p + '.date', p + '.label', p + '.action', p + '.owner', p + '.impact'],
        )
        c.paragraphStyles = [
          { ...b.styles.body, bold: true },
          { ...b.styles.body },
          { ...b.styles.small },
        ]
      }
    })
    tx(
      'DecisionHeading',
      horizontal ? [1.32, 3.98, 11.28, 0.35] : [7.35, 2.12, 5.25, 0.35],
      d.decisionHeading,
      'body',
      'decisionHeading',
      { bold: true },
    )
    cells(r.decisions, d.decisions.length, !horizontal, 0.42).forEach(([x, y, w, h], i) => {
      const v = d.decisions[i],
        p = `decisions[${i}]`
      rule('DecisionRail' + i, x, y, h, 'accent', true)
      if (horizontal) {
        tx(
          'DecisionRequest' + i,
          [x + 0.17, y, w - 0.17, horizontal ? 0.53 : 0.53],
          v.request,
          'decision',
          p + '.request',
        )
        tx(
          'DecisionBasis' + i,
          [x + 0.17, y + (horizontal ? 0.59 : 0.59), w - 0.17, horizontal ? 0.4 : 0.35],
          v.rationale,
          'small',
          p + '.rationale',
        )
        tx(
          'DecisionDelay' + i,
          [x + 0.17, y + (horizontal ? 1.05 : 1.04), w - 0.17, horizontal ? 0.55 : 0.4],
          `${v.owner} · ${v.date} · ${v.consequence}`,
          'small',
          [p + '.owner', p + '.date', p + '.consequence'],
        )
      } else {
        const c = tx(
          'DecisionContent' + i,
          [x + 0.17, y, w - 0.17, h],
          v.request + '\n' + v.rationale + '\n' + v.owner + ' · ' + v.date + ' · ' + v.consequence,
          'body',
          [p + '.request', p + '.rationale', p + '.owner', p + '.date', p + '.consequence'],
        )
        c.paragraphStyles = [{ ...b.styles.decision }, { ...b.styles.small }, { ...b.styles.small }]
      }
    })
  } else if (role === 'rating') {
    const vertical = id === 'rows'
    tx(
      'RatingScaleLabel',
      [r.ratings[0], r.ratings[1] - 0.4, r.ratings[2], 0.3],
      d.scaleLabel ?? 'Position · 1–10',
      'small',
      'scaleLabel',
    )
    cells(r.ratings, d.ratings.length, vertical, 0.25).forEach(([x, y, w, h], i) => {
      const v = d.ratings[i],
        p = `ratings[${i}]`
      if (!Number.isInteger(v.position) || v.position < 1 || v.position > 10)
        throw Error('Rating position must be an integer from 1 to 10')
      tx('RatingLabel' + i, [x, y, vertical ? 3.1 : w, 0.4], v.label, 'heading', p + '.label')
      const sx = vertical ? x + 3.6 : x,
        sy = vertical ? y + 0.05 : y + 0.7,
        dia = vertical ? 0.16 : Math.min(0.16, (w - 0.35) / 13),
        step = vertical ? 0.32 : (w - 0.35) / 10
      for (let j = 0; j < 10; j++) {
        const f = [sx + j * step, sy, dia, dia]
        if (j + 1 === v.position) box(`Rating${i}Dot${j}`, f, 'accent', 'circle')
        else
          cs.push({
            kind: 'path',
            name: `Rating${i}Dot${j}`,
            frame: f,
            line: 'accent',
            linePt: 0.7,
            path: {
              width: 100000,
              height: 100000,
              commands: [
                { type: 'move', x: 100000, y: 50000 },
                {
                  type: 'cubic',
                  x1: 100000,
                  y1: 77614,
                  x2: 77614,
                  y2: 100000,
                  x: 50000,
                  y: 100000,
                },
                { type: 'cubic', x1: 22386, y1: 100000, x2: 0, y2: 77614, x: 0, y: 50000 },
                { type: 'cubic', x1: 0, y1: 22386, x2: 22386, y2: 0, x: 50000, y: 0 },
                { type: 'cubic', x1: 77614, y1: 0, x2: 100000, y2: 22386, x: 100000, y: 50000 },
                { type: 'close' },
              ],
            },
          })
      }
      tx('RatingMinimum' + i, [sx - 0.08, sy + 0.29, 0.32, 0.28], '1', 'small', [], {
        alignment: 'center',
      })
      tx('RatingMaximum' + i, [sx + 9 * step - 0.08, sy + 0.29, 0.32, 0.28], '10', 'small', [], {
        alignment: 'center',
      })
      tx(
        'RatingValue' + i,
        [vertical ? sx + 3.4 : x, vertical ? y : y + 1.62, vertical ? 1 : w, 0.4],
        `${v.position}/10`,
        'heading',
        p + '.position',
        { color: 'accent' },
      )
      tx(
        'RatingEvidence' + i,
        [
          vertical ? sx + 4.7 : x,
          vertical ? y : y + 2.25,
          vertical ? w - 8.3 : w,
          vertical ? h : 1.05,
        ],
        v.evidence,
        'small',
        p + '.evidence',
      )
    })
  } else throw Error('Unregistered Violet role')
  rule('VerdictRule', 1.32, 6.12, 11.28)
  tx('Verdict', b.chrome.verdict, d.verdict, 'takeaway', 'verdict')
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolveVioletDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'violetCoverSlide' ||
      content.slides.at(-1)?.type !== 'violetActionsSlide')
  )
    throw Error(
      'Complete Violet decks open with verdict cover and end with actions and decisions; use excerpt for extracts',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.violet.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps || slide.imageSlots)
      throw Error('Registered content only; no customOps or image slots')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileVioletLayout(
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
                design.violet.chrome.page,
                {
                  ...design.violet.styles.small,
                  color: family.role === 'section' ? 'paper' : 'muted',
                },
                'structural.page',
              ),
              name: 'Page',
            })
          for (const c of components) {
            const [x, y, w, h] = c.frame
            if (
              [x, y, w, h].some((v) => !Number.isFinite(v)) ||
              Math.min(x, y) < 0 ||
              Math.min(w, h) <= 0 ||
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
        design.violet.rhythm.maxConsecutive,
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
