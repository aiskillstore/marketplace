import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { pulseAtmosphere } from './atmosphere.mjs'
export const pulseNumber = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(8)).toString()
}
export function fitPulseText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const cap = ((frame[2] - 0.04) * 72) / style.sizePt / (style.bold ? 1.08 : 1),
    text = wrapCjkText(value, cap * 0.91)
  let lines = 0
  for (const line of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const token of line.split(/(\s+)/u)) {
      const n = textUnits(token)
      if (n > cap) throw Error(`${path}: unbroken token exceeds width`)
      if (used && used + n > cap) {
        lines++
        used = 0
      }
      used += n
    }
  }
  const requiredHeight = (lines * style.sizePt * (style.sizePt >= 23 ? 1.2 : 1.5)) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines exceed ${frame[3].toFixed(2)}in; select a legal variant, reorganize or split`,
    )
  return {
    kind: 'text',
    text,
    frame: [...frame],
    allocatedFrame: [...frame],
    style: { ...style },
    path,
    paths: [path],
    estimatedLines: lines,
    requiredHeight,
  }
}
export function compilePulseLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.pulse,
    r = variant.regions,
    role = family.role,
    cs = pulseAtmosphere(design, role),
    gap = b.spacing.gap
  const tx = (name, f, value, key = 'body', fields = name, extra = {}) => {
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) => `${path}.${k}`),
      c = { ...fitPulseText(value, f, { ...b.styles[key], ...extra }, paths[0]), name, paths }
    cs.push(c)
    return c
  }
  const shape = (name, frame, color = 'rule', kind = 'box', extra = {}) =>
    cs.push({ kind, name, frame, color, ...extra })
  const rule = (name, x, y, w, vertical = false, color = 'rule') =>
    shape(name, vertical ? [x, y, 0.009, w] : [x, y, w, 0.009], color)
  const cells = (f, n, vertical = false, g = gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const ratio = (m, p) => {
    if (!(m.target > 0) || m.actual < 0 || (m.direction === 'lower' && m.actual === 0))
      throw Error(`${path}.${p}: undefined attainment; positive target and valid actual required`)
    return (m.direction === 'lower' ? m.target / m.actual : m.actual / m.target) * 100
  }
  // Every visible field is bound in the plan; generated values and editable geometry share source data.
  const metric = (m, f, i, vertical = false) => {
    const [x, y, w] = f,
      p = `metrics[${i}]`
    ratio(m, p)
    const value = tx(
      'MetricValue' + i,
      [x, y, w, vertical ? 0.5 : 0.65],
      `${pulseNumber(m.actual)} ${m.unit}`,
      'number',
      [p + '.actual', p + '.unit'],
      { sizePt: vertical ? 24 : 30 },
    )
    value.runs = [
      { text: pulseNumber(m.actual), style: value.style },
      {
        text: ` ${m.unit}`,
        style: { ...value.style, sizePt: value.style.sizePt / 2, color: 'body' },
      },
    ]
    tx(
      'MetricLabel' + i,
      [x, y + (vertical ? 0.55 : 0.7), w, 0.32],
      `${m.label} · ${pulseNumber(m.actual)} / ${pulseNumber(m.target)} · ${Number(ratio(m, p).toFixed(1))}%`,
      'small',
      [p + '.label', p + '.actual', p + '.target'],
    )
  }
  tx('Owner', b.chrome.owner, d.owner, 'small', 'owner')
  tx('Report', b.chrome.report, d.report, 'small', 'report', { alignment: 'right' })
  if (role !== 'cover') {
    tx('Title', b.chrome.title, d.title, 'title', 'title', { emphasis: d.emphasis })
    tx('Basis', b.chrome.basis, d.basis, 'small', 'basis')
  }
  if (role === 'cover') {
    tx('Title', r.hero, d.title, 'hero', 'title', { emphasis: d.emphasis })
    tx(
      'Subtitle',
      [r.hero[0], r.hero[1] + r.hero[3] + 0.15, r.hero[2], 0.34],
      d.subtitle,
      'body',
      'subtitle',
    )
    const vertical = layoutId === 'photoRail'
    cells(r.metrics, d.metrics.length, vertical, vertical ? 0.1 : 0.2).forEach((f, i) => {
      metric(d.metrics[i], f, i, vertical)
      if (i && !vertical) rule('MetricDivider' + i, f[0] - 0.12, f[1], f[3], true)
    })
    cs.push({ kind: 'image', name: 'CoverImage', frame: r.image })
    tx(
      'ImageLabel',
      [r.image[0] + 0.2, r.image[1] + r.image[3] / 2 - 0.17, r.image[2] - 0.4, 0.5],
      d.imageLabel,
      'small',
      'imageLabel',
      { alignment: 'center' },
    )
  } else if (role === 'overview') {
    const band = layoutId === 'gaugeBand',
      [jx, jy, jw, jh] = r.judgment
    tx('Judgment', [jx, jy, band ? 3.2 : jw, 0.55], d.judgment, 'heading', 'judgment')
    const noteFrame = band ? [jx + 3.5, jy, jw - 3.5, jh] : [jx, jy + 0.8, jw, jh - 0.8]
    cells(noteFrame, d.notes.length, !band, 0.12).forEach(([x, y, w, h], i) => {
      shape('JudgmentDot' + i, [x, y + 0.09, 0.055, 0.055], i ? 'amber' : 'accent', 'ellipse')
      tx('JudgmentNote' + i, [x + 0.15, y, w - 0.15, h], d.notes[i], 'body', `notes[${i}]`)
    })
    cells(r.gauges, d.metrics.length, false, 0.3).forEach(([x, y, w, h], i) => {
      const m = d.metrics[i],
        pct = ratio(m, `metrics[${i}]`),
        diam = Math.min(w - 0.05, h - 1.05),
        gx = x + (w - diam) / 2,
        p = `metrics[${i}]`,
        tone = pct >= 100 ? 'accent' : 'amber'
      cs.push({
        kind: 'gauge',
        name: 'Gauge' + i,
        frame: [gx, y, diam, diam],
        value: Math.min(100, pct),
        tone,
        data: {
          categories: [m.label, d.targetLabel],
          series: [{ name: m.label, values: [Math.min(100, pct), Math.max(0, 100 - pct)] }],
        },
      })
      shape('GaugeTick' + i, [gx + diam / 2 - 0.009, y - 0.1, 0.018, 0.14], 'ice')
      tx(
        'GaugeValue' + i,
        [gx + diam * 0.15, y + diam * (band ? 0.25 : 0.32), diam * 0.7, 0.52],
        `${Number(pct.toFixed(1))}%`,
        'gauge',
        [p + '.actual', p + '.target'],
        { alignment: 'center' },
      )
      tx(
        'GaugeLabel' + i,
        [gx + diam * 0.15, y + diam * (band ? 0.62 : 0.6), diam * 0.7, band ? 0.3 : 0.42],
        m.label,
        'small',
        p + '.label',
        { alignment: 'center', color: 'body' },
      )
      tx(
        'GaugeBasis' + i,
        [x, y + diam + 0.22, w, 0.62],
        `${d.targetLabel} ${pulseNumber(m.target)} ${m.unit}\n${d.actualLabel} ${pulseNumber(m.actual)} ${m.unit}`,
        'small',
        ['targetLabel', 'actualLabel', p + '.target', p + '.actual', p + '.unit'],
        { alignment: 'center' },
      )
    })
  } else if (role === 'audit') {
    const cols = [0.22, 0.1, 0.1, 0.12, 0.13, 0.33],
      sum = cols.reduce((a, v) => a + v, 0),
      widths = cols.map((v) => (r.table[2] * v) / sum),
      rows = [
        d.headers,
        ...d.rows.map((v) => [v.label, v.target, v.actual, v.variance, `● ${v.status}`, v.detail]),
      ],
      rowH = r.table[3] / rows.length,
      bindings = []
    if (d.headers.length !== 6) throw Error(`${path}.headers: exactly six headers required`)
    rows.forEach((row, i) => {
      let x = r.table[0]
      row.forEach((v, j) => {
        const st = { ...b.styles.table, bold: i === 0 || j === 2, color: i === 0 ? 'ice' : 'body' },
          f = [x + 0.065, r.table[1] + i * rowH + 0.045, widths[j] - 0.13, rowH - 0.09],
          key =
            i === 0
              ? `headers[${j}]`
              : `rows[${i - 1}].${['label', 'target', 'actual', 'variance', 'status', 'detail'][j]}`
        fitPulseText(v, f, st, path + '.' + key)
        bindings.push({ paths: [path + '.' + key], frame: f, style: st })
        x += widths[j]
      })
    })
    rule('AuditTop', r.table[0], r.table[1] + rowH, r.table[2], false, 'ice')
    cs.push({
      kind: 'table',
      name: 'AuditTable',
      frame: r.table,
      cells: rows,
      widths,
      rowHeights: rows.map(() => rowH),
      states: d.rows.map((v) => v.state),
      bindings,
    })
    tx('AuditNote', r.note, d.note, 'small', 'note', { color: 'body' })
  } else if (role === 'trend') {
    const f = r.chart,
      vals = d.points.map((v) => v.value),
      lo = Math.min(0, ...vals),
      hi = Math.max(0, ...vals),
      span = hi - lo || 1
    if (d.boundary < 1 || d.boundary >= d.points.length || !Number.isInteger(d.boundary))
      throw Error(`${path}.boundary: internal category boundary required`)
    if (
      d.events.some(
        (v) => !Number.isInteger(v.index) || v.index < 0 || v.index >= d.points.length,
      ) ||
      new Set(d.events.map((v) => v.index)).size !== d.events.length
    )
      throw Error(`${path}.events: distinct valid category indices required`)
    tx('ChartHead', [f[0], f[1] - 0.35, f[2] * 0.48, 0.3], `${d.seriesName} · ${d.unit}`, 'small', [
      'seriesName',
      'unit',
    ])
    cs.push({
      kind: 'chart',
      name: 'TrendChart',
      frame: f,
      data: {
        categories: d.points.map((v) => v.label),
        series: [{ name: d.seriesName, values: vals }],
      },
      minimum: lo < 0 ? lo - span * 0.15 : 0,
      maximum: hi + span * 0.25,
      numberFormat: vals.every(Number.isInteger)
        ? '0'
        : vals.some((v) => v !== 0 && Math.abs(v) < 0.001)
          ? '0.00E+00'
          : '0.00',
      inputPaths: d.points.flatMap((_, i) => [
        `${path}.points[${i}].label`,
        `${path}.points[${i}].value`,
      ]),
    })
    // Events use category-aligned positions derived from the same plot frame.
    const plot = [f[0] + 0.1, f[1] + 0.07, f[2] - 0.25, f[3] - 0.42],
      bx = plot[0] + (plot[2] * d.boundary) / d.points.length
    cs.push({
      kind: 'line',
      name: 'PhaseLine',
      frame: [bx, plot[1], 0.01, plot[3]],
      points: [
        [0, 0],
        [0, 1],
      ],
      color: 'connector',
      dash: true,
    })
    tx(
      'BoundaryLabel',
      [Math.max(f[0], bx - 0.55), f[1] - 0.35, 1.1, 0.3],
      d.boundaryLabel,
      'small',
      'boundaryLabel',
      { alignment: 'center', color: 'ice' },
    )
    cells(r.notes, d.events.length, layoutId === 'trendRail', 0.22).forEach(([x, y, w, h], i) => {
      tx(
        'EventHeading' + i,
        [x, y, w, 0.35],
        `${i + 1}. ${d.events[i].label}`,
        'heading',
        `events[${i}].label`,
        { color: 'ice' },
      )
      tx('EventNote' + i, [x, y + 0.44, w, h - 0.44], d.events[i].note, 'body', `events[${i}].note`)
      const ex = plot[0] + (plot[2] * (d.events[i].index + 0.5)) / d.points.length
      const ey =
        plot[1] +
        plot[3] *
          (1 -
            (vals[d.events[i].index] - (lo < 0 ? lo - span * 0.15 : 0)) /
              (hi + span * 0.25 - (lo < 0 ? lo - span * 0.15 : 0))) -
        0.56
      cs.push({
        kind: 'node',
        name: 'ChartEvent' + i,
        frame: [ex - 0.14, Math.max(f[1], ey), 0.28, 0.28],
        color: 'ice',
        text: String(i + 1),
        style: { ...b.styles.small, color: 'ice', alignment: 'center' },
        paths: [`${path}.events[${i}].index`],
      })
    })
  } else if (role === 'attribution') {
    const delta = d.actual - d.target,
      total = d.factors.reduce((a, v) => a + v.value, 0)
    if (Math.abs(total - delta) > 1e-9 * Math.max(1, Math.abs(total), Math.abs(delta)))
      throw Error(`${path}.factors: signed drivers do not reconcile to actual minus target`)
    if (
      d.factors.some((v) => ![0, 1].includes(v.group)) ||
      ![0, 1].every((i) => d.factors.some((v) => v.group === i))
    )
      throw Error(`${path}.factors: both registered groups required`)
    const [x, y, w, h] = r.target,
      center = [x + w / 2, y + h / 2]
    shape('BullseyeOuter', r.target, 'ice', 'outline', { ellipse: true })
    shape('BullseyeInner', [x + 0.12, y + 0.12, w - 0.24, h - 0.24], 'ice', 'outline', {
      ellipse: true,
    })
    tx('GapLabel', [x + 0.15, y + 0.55, w - 0.3, 0.35], d.totalLabel, 'small', 'totalLabel', {
      alignment: 'center',
    })
    const dense = d.factors.length > 4,
      valueY = dense ? r.factors[1] + 0.43 + (r.factors[3] - 0.43 + 0.1) / 3 : y + 1.0
    tx(
      'GapValue',
      [x + 0.1, valueY, w - 0.2, 0.65],
      pulseNumber(delta),
      'number',
      ['actual', 'target'],
      { alignment: 'center' },
    )
    tx('GapUnit', [x + 0.2, y + 1.65, w - 0.4, 0.34], d.unit, 'small', 'unit', {
      alignment: 'center',
    })
    const gapBasis = tx(
      'GapBasis',
      [x - 0.25, y + h + 0.2, w + 0.5, 0.6],
      `${d.actualLabel} ${pulseNumber(d.actual)} − ${d.targetLabel} ${pulseNumber(d.target)}`,
      'small',
      ['actualLabel', 'targetLabel', 'actual', 'target'],
      { alignment: 'center' },
    )
    if (dense) gapBasis.frame[3] = Math.min(gapBasis.frame[3], gapBasis.requiredHeight + 0.04)
    const compact = d.factors.length > 4,
      groupFrames = cells(r.factors, 2, !compact, 0.25)
    groupFrames.forEach(([gx, gy, gw, gh], g) => {
      tx('FactorGroup' + g, [gx, gy, gw, 0.3], d.groups[g], 'small', `groups[${g}]`, {
        color: 'ice',
      })
      const fs = d.factors.map((v, i) => ({ ...v, index: i })).filter((v) => v.group === g)
      cells([gx, gy + 0.43, gw, gh - 0.43], fs.length, true, 0.1).forEach(([fx, fy, fw, fh], j) => {
        const v = fs[j],
          i = v.index,
          p = `factors[${i}]`
        tx(
          'FactorValue' + i,
          [fx, fy, compact ? 0.8 : 1.25, compact ? 0.35 : 0.5],
          `${v.value > 0 ? '+' : ''}${pulseNumber(v.value)}`,
          'heading',
          p + '.value',
          { color: 'ice' },
        )
        tx(
          'FactorLabel' + i,
          [fx + (compact ? 0.95 : 1.4), fy, fw - (compact ? 0.95 : 1.4), 0.35],
          v.label,
          'heading',
          p + '.label',
        )
        const factorNote = tx(
          'FactorNote' + i,
          compact ? [fx, fy + 0.45, fw, fh - 0.45] : [fx + 1.4, fy + 0.38, fw - 1.4, fh - 0.38],
          v.note,
          'small',
          p + '.note',
        )
        if (compact)
          factorNote.frame[3] = Math.min(factorNote.frame[3], factorNote.requiredHeight + 0.04)
        const start =
            layoutId === 'targetRight'
              ? [
                  compact ? r.factors[0] + r.factors[2] + 0.1 : fx + fw + 0.1,
                  fy + 0.2 + (compact ? g * 0.12 : 0),
                ]
              : [compact ? r.factors[0] - 0.1 : fx - 0.1, fy + 0.2 + (compact ? g * 0.12 : 0)],
          end = layoutId === 'targetRight' ? [x, center[1]] : [x + w, center[1]],
          rayFrame = [
            Math.min(start[0], end[0]),
            Math.min(start[1], end[1]),
            Math.abs(start[0] - end[0]),
            Math.max(0.01, Math.abs(start[1] - end[1])),
          ]
        cs.push({
          kind: 'line',
          name: 'ConvergingRay' + i,
          frame: rayFrame,
          points: [start, end].map(([a, b]) => [
            (a - rayFrame[0]) / rayFrame[2],
            (b - rayFrame[1]) / rayFrame[3],
          ]),
          color: 'connector',
        })
      })
    })
  } else if (role === 'comparison') {
    const rows = layoutId === 'compareRows',
      [ox, oy, ow, oh] = r.overview
    tx(
      'ComparisonOverview',
      [ox, oy, rows ? 3.9 : ow, rows ? oh : 1.0],
      d.overview,
      'heading',
      'overview',
      { color: 'ice' },
    )
    tx(
      'ComparisonNote',
      rows ? [ox + 4.2, oy, ow - 4.2, oh] : [ox, oy + 1.25, ow, oh - 1.25],
      d.overviewNote,
      'body',
      'overviewNote',
    )
    cells(r.subjects, d.subjects.length, rows, 0.23).forEach(([x, y, w, h], i) => {
      const v = d.subjects[i],
        p = `subjects[${i}]`
      if (v.target <= 0 || v.actual < 0)
        throw Error(`${path}.${p}: nonnegative actual and positive target required`)
      if (rows) {
        rule('SubjectRule' + i, x, y, w)
        tx('SubjectName' + i, [x, y + 0.1, 1.8, 0.35], v.name, 'heading', p + '.name')
        tx('SubjectStatus' + i, [x, y + 0.53, 1.8, 0.3], `● ${v.status}`, 'small', p + '.status', {
          color: v.state === 'met' ? 'accent' : 'amber',
        })
        tx(
          'SubjectValue' + i,
          [x + 2, y + 0.1, 2.15, 0.6],
          `${pulseNumber(v.actual)} / ${pulseNumber(v.target)} ${v.unit}`,
          'heading',
          [p + '.actual', p + '.target', p + '.unit'],
        )
        const kvf = [x + 4.4, y + 0.08, w - 7.1, h - 0.1]
        cells(kvf, v.kv.length, false, 0.1).forEach(([kx, ky, kw, kh], j) => {
          tx('Kv' + i + '_' + j, [kx, ky, kw, kh], `${v.kv[j].label}\n${v.kv[j].value}`, 'small', [
            p + `.kv[${j}].label`,
            p + `.kv[${j}].value`,
          ])
        })
        tx(
          'Diagnosis' + i,
          [x + w - 2.5, y + 0.1, 2.5, h - 0.12],
          v.diagnosis,
          'small',
          p + '.diagnosis',
        )
      } else {
        if (i) rule('SubjectDivider' + i, x - 0.12, y, h, true)
        tx('SubjectName' + i, [x, y, w, 0.4], v.name, 'heading', p + '.name')
        tx('SubjectStatus' + i, [x, y + 0.48, w, 0.3], `● ${v.status}`, 'small', p + '.status', {
          color: v.state === 'met' ? 'accent' : 'amber',
        })
        tx(
          'SubjectValue' + i,
          [x, y + 0.95, w, 0.55],
          `${pulseNumber(v.actual)} / ${pulseNumber(v.target)}`,
          'number',
          [p + '.actual', p + '.target'],
          { sizePt: 24 },
        )
        tx('SubjectUnit' + i, [x, y + 1.53, w, 0.3], v.unit, 'small', p + '.unit')
        cells([x, y + 2.0, w, 1.05], v.kv.length, true, 0.025).forEach(([kx, ky, kw, kh], j) => {
          tx(
            'KvLabel' + i + '_' + j,
            [kx, ky, kw * 0.6, kh],
            v.kv[j].label,
            'small',
            p + `.kv[${j}].label`,
          )
          tx(
            'KvValue' + i + '_' + j,
            [kx + kw * 0.6, ky, kw * 0.4, kh],
            v.kv[j].value,
            'small',
            p + `.kv[${j}].value`,
            { alignment: 'right', color: 'ice' },
          )
        })
        rule('DiagnosisRule' + i, x, y + 3.18, w)
        tx('Diagnosis' + i, [x, y + 3.32, w, h - 3.32], v.diagnosis, 'small', p + '.diagnosis')
      }
    })
  } else if (role === 'status') {
    const columns = layoutId === 'statusColumns'
    cells(r.projects, d.projects.length, !columns, 0.2).forEach(([x, y, w, h], i) => {
      const v = d.projects[i],
        p = `projects[${i}]`,
        tone = { onTrack: 'green', atRisk: 'amber', behind: 'red' }[v.state]
      shape('ProjectOutline' + i, [x, y, w, h], 'connector', 'outline')
      const ix = x + 0.18,
        innerY = y + 0.08,
        iw = w - 0.36
      shape('ProjectDot' + i, [ix, innerY + 0.08, 0.085, 0.085], tone, 'ellipse')
      tx(
        'ProjectName' + i,
        [ix + 0.18, innerY, columns ? iw - 0.18 : 3.0, 0.35],
        v.name,
        'heading',
        p + '.name',
      )
      tx(
        'ProjectStatus' + i,
        columns ? [ix, innerY + 0.44, iw, 0.3] : [ix + 3.3, innerY, 1.6, 0.3],
        v.status,
        'small',
        p + '.status',
        { color: tone },
      )
      const evidence = columns ? [ix, innerY + 0.92, iw, 0.65] : [ix, innerY + 0.38, iw * 0.6, 0.25]
      tx('ProjectEvidence' + i, evidence, v.evidence, 'small', p + '.evidence', { color: 'body' })
      const bar = columns
        ? [ix, innerY + 1.78, iw - 0.8, 0.065]
        : [ix, innerY + 0.72, iw * 0.56, 0.055]
      shape('ProgressTrack' + i, bar, 'track')
      if (v.progress > 0)
        shape('ProgressFill' + i, [bar[0], bar[1], (bar[2] * v.progress) / 100, bar[3]], 'accent')
      tx(
        'ProgressValue' + i,
        [bar[0] + bar[2] + 0.1, bar[1] - 0.13, 0.7, 0.3],
        `${pulseNumber(v.progress)}%`,
        'small',
        p + '.progress',
        { color: 'ice' },
      )
      tx(
        'ProjectBlocker' + i,
        columns ? [ix, innerY + 2.12, iw, 0.5] : [ix, innerY + 0.92, iw * 0.6, 0.25],
        v.blocker,
        'small',
        p + '.blocker',
      )
      tx(
        'ProjectAction' + i,
        columns ? [ix, innerY + 2.8, iw, 0.62] : [ix + iw * 0.66, innerY + 0.08, iw * 0.34, 0.58],
        v.action,
        'body',
        p + '.action',
        { color: 'ice' },
      )
      tx(
        'ProjectOwner' + i,
        columns
          ? [ix, innerY + h - 0.7, iw, 0.4]
          : [ix + iw * 0.66, innerY + 0.76, iw * 0.34, 0.35],
        `${v.owner} · ${v.date}`,
        'small',
        [p + '.owner', p + '.date'],
      )
    })
  } else if (role === 'close') {
    const vertical = layoutId === 'routeLeft'
    cells(r.route, d.phases.length, vertical, 0.15).forEach(([x, y, w, h], i) => {
      const v = d.phases[i],
        p = `phases[${i}]`,
        node = vertical ? [x, y + 0.05, 0.22, 0.22] : [x + w / 2 - 0.11, y + 0.52, 0.22, 0.22]
      if (i < d.phases.length - 1) {
        if (vertical)
          rule('RouteLine' + i, node[0] + 0.105, node[1] + 0.22, h - 0.07, true, 'connector')
        else rule('RouteLine' + i, node[0] + 0.22, node[1] + 0.105, w - 0.07, false, 'connector')
      }
      shape('RouteNode' + i, node, 'ice', 'outline', { ellipse: true })
      const f = vertical ? [x + 0.42, y, w - 0.42, h] : [x, y, w, h]
      tx(
        'PhaseName' + i,
        [f[0], f[1], f[2], 0.35],
        `${v.period} · ${v.name}`,
        'heading',
        [p + '.period', p + '.name'],
        { alignment: vertical ? 'left' : 'center' },
      )
      tx(
        'Milestone' + i,
        [f[0], f[1] + (vertical ? 0.43 : 0.95), f[2], 0.42],
        v.milestone,
        'small',
        p + '.milestone',
        { alignment: vertical ? 'left' : 'center', color: 'body' },
      )
      tx(
        'Gate' + i,
        [f[0], f[1] + (vertical ? 0.87 : 1.42), f[2], 0.4],
        v.gate,
        'small',
        p + '.gate',
        { alignment: vertical ? 'left' : 'center', color: 'ice' },
      )
    })
    cells(r.decisions, d.decisions.length, vertical, 0.27).forEach(([x, y, w, h], i) => {
      const v = d.decisions[i],
        p = `decisions[${i}]`,
        ix = x + 0.19,
        iw = w - 0.38
      shape('DecisionOutline' + i, [x, y, w, h], 'ice', 'outline')
      tx(
        'DecisionLabel' + i,
        [ix, y + 0.15, vertical ? 1.25 : iw, 0.3],
        v.label,
        'small',
        p + '.label',
        { color: 'ice' },
      )
      tx(
        'DecisionRequest' + i,
        vertical ? [ix + 1.35, y + 0.15, iw - 1.35, 0.4] : [ix, y + 0.53, iw, 0.43],
        v.request,
        'heading',
        p + '.request',
      )
      tx(
        'DecisionDetail' + i,
        [ix, y + (vertical ? 0.68 : 1.03), iw, 0.38],
        v.detail,
        'small',
        p + '.detail',
        { color: 'body' },
      )
      tx(
        'DecisionConsequence' + i,
        [ix, y + (vertical ? 1.18 : 1.49), iw, 0.3],
        v.consequence,
        'small',
        p + '.consequence',
        { color: 'amber' },
      )
      tx('DecisionOwner' + i, [ix, y + h - 0.38, iw, 0.25], `${v.owner} · ${v.date}`, 'small', [
        p + '.owner',
        p + '.date',
      ])
    })
  } else throw Error(`Unregistered pulse role ${role}`)
  rule('VerdictRule', 0.8, 6.4, 11.7)
  tx('Verdict', b.chrome.verdict, d.verdict, 'small', 'verdict', { color: 'body' })
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolvePulseDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'pulseCoverSlide' ||
      content.slides.at(-1)?.type !== 'pulseCloseSlide')
  )
    throw Error(
      'Complete Midnight Pulse decks open with verdict cover and end with roadmap decisions; extracts require designScope excerpt',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.pulse.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps) throw Error('customOps forbidden')
    if (slide.imageSlots && family.role !== 'cover') throw Error('Photography is cover-only')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    if ((slide.data.emphasis ?? []).some((v) => !v || !slide.data.title.includes(v)))
      throw Error(`slides[${s}].emphasis: phrase must occur in title`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compilePulseLayout(
            design,
            family,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
          if (slide.imageSlots && Object.keys(slide.imageSlots).length) {
            const label = components.find((c) => c.name === 'ImageLabel'),
              f = v.regions.image
            Object.assign(
              label,
              fitPulseText(
                slide.data.imageLabel,
                [f[0] + 0.1, f[1] + f[3] - 0.31, f[2] - 0.2, 0.27],
                { ...design.pulse.styles.small, color: 'body' },
                `slides[${s}].data.imageLabel`,
              ),
              { caption: true },
            )
          }
          components.push({
            ...fitPulseText(
              `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
              design.pulse.chrome.page,
              { ...design.pulse.styles.small, alignment: 'right' },
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
        design.pulse.rhythm.maxConsecutive,
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
