import { readFileSync } from 'node:fs'
import {
  assertDesignValue,
  designHash,
  selectDesignLayout,
  textUnits,
} from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'

// Geometry is compiled before any operations are emitted. No component drops input.
export function fitImpactText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = ((frame[2] - 0.06) * 72) / style.sizePt / (style.bold ? 1.07 : 1)
  const text = wrapCjkText(value, capacity * 0.92)
  let lines = 0
  for (const line of text.split(/\r\n|\r|\n/)) {
    let used = 0
    lines++
    for (const token of line.split(/(\s+)/u)) {
      const n = textUnits(token)
      if (n > capacity) throw Error(`${path}: unbroken token exceeds width`)
      if (used && used + n > capacity) {
        lines++
        used = 0
      }
      used += n
    }
  }
  const requiredHeight = (lines * style.sizePt * 1.5) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines need ${requiredHeight.toFixed(2)}in, available ${frame[3].toFixed(2)}in; reorganize or split`,
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

export function compileImpactLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.impact,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap
  const tx = (name, f, value, key = 'body', field = name, extra = {}) => {
    const paths = (Array.isArray(field) ? field : [field]).map((k) => `${path}.${k}`)
    const c = { ...fitImpactText(value, f, { ...b.styles[key], ...extra }, paths[0]), name, paths }
    c.frame[3] = c.requiredHeight
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule') => cs.push({ kind: 'box', name, frame, color })
  const rule = (name, x, y, w, vertical = false) =>
    box(name, vertical ? [x, y, 0.008, w] : [x, y, w, 0.008])
  const cells = (f, n, vertical = false) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + gap)) / n, f[2], (f[3] - gap * (n - 1)) / n]
        : [f[0] + (i * (f[2] + gap)) / n, f[1], (f[2] - gap * (n - 1)) / n, f[3]],
    )
  const metrics = (f, values, field, mode = 'row', dark = false) => {
    const vertical = mode === 'rail' || mode === 'compactRail',
      compact = mode === 'band' || mode === 'compactRail'
    if (dark) box('MetricBand', f, 'dark')
    const inset = dark ? b.spacing.inset : 0
    const fs = cells(
      [f[0] + inset, f[1] + inset, f[2] - 2 * inset, f[3] - 2 * inset],
      values.length,
      vertical,
    )
    values.forEach((v, i) => {
      const [x, y, w, h] = fs[i],
        p = `${field}[${i}]`,
        st = compact ? 'bandMetric' : 'metric'
      if (i)
        rule(
          `${field}Separator${i}`,
          vertical ? x : x - gap / 2,
          vertical ? y - gap / 2 : y,
          vertical ? w : h,
          !vertical,
        )
      tx(`${field}Value${i}`, [x, y, w, compact ? 0.46 : 0.74], v.value, st, p + '.value', {
        color: dark ? (v.focus ? 'spring' : 'paper') : v.focus ? 'accentInk' : 'ink',
      })
      tx(
        `${field}Label${i}`,
        [x, y + (compact ? 0.48 : 0.82), w, compact ? 0.34 : 0.53],
        [v.label, v.unit].filter(Boolean).join(' · '),
        'small',
        [p + '.label', p + '.unit'],
        { color: dark ? 'paper' : 'secondary' },
      )
      if (v.note)
        tx(
          `${field}Note${i}`,
          [x, y + (compact ? 0.85 : 1.4), w, h - (compact ? 0.85 : 1.4)],
          v.note,
          'small',
          p + '.note',
          { color: dark ? 'paper' : 'secondary' },
        )
    })
  }
  const table = (name, f, columns, rows, field = 'rows', status = false) => {
    if (rows.some((row) => row.cells.length !== columns.length))
      throw Error(`${path}.${field}: one cell per column required`)
    if (status && columns.filter((column) => column.kind === 'status').length !== 1)
      throw Error(`${path}.columns: scorecard requires exactly one status column`)
    const sum = columns.reduce((n, v) => n + v.weight, 0),
      widths = columns.map((v) => (f[2] * v.weight) / sum)
    const rh = f[3] / (rows.length + 1),
      bindings = []
    const data = [columns.map((v) => v.label), ...rows.map((v) => v.cells)]
    data.forEach((row, i) => {
      let x = f[0]
      row.forEach((v, j) => {
        const frame = [x + 0.07, f[1] + i * rh + 0.06, widths[j] - 0.14, rh - 0.12]
        const p = i === 0 ? `columns[${j}].label` : `${field}[${i - 1}].cells[${j}]`
        fitImpactText(v, frame, b.styles.table, `${path}.${p}`)
        bindings.push({ frame, paths: [`${path}.${p}`] })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name,
      frame: f,
      cells: data,
      widths,
      rowHeights: data.map(() => rh),
      columns,
      rows,
      status,
      bindings,
    })
  }
  const notes = (f, items, field = 'notes') => {
    cells(f, items.length, true).forEach(([x, y, w, h], i) => {
      const v = items[i],
        p = `${field}[${i}]`
      rule(`${field}Rule${i}`, x, y, w)
      tx(`${field}Title${i}`, [x, y + 0.1, w, 0.4], v.label, 'heading', p + '.label')
      tx(`${field}Body${i}`, [x, y + 0.58, w, h - 0.62], v.body, 'body', p + '.body')
    })
  }
  tx('Document', b.chrome.document, d.document, 'label', 'document')
  tx('Section', b.chrome.section, d.section, 'label', 'section')
  tx('Source', b.chrome.source, d.source, 'source', 'source')
  if (family.role !== 'overview') {
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Subtitle', b.chrome.subtitle, d.subtitle, 'body', 'subtitle', { color: 'secondary' })
    rule(
      'HeaderRule',
      b.chrome.title[0],
      b.chrome.subtitle[1] + b.chrome.subtitle[3] + 0.12,
      b.chrome.title[2],
    )
  }
  if (family.role === 'overview') {
    const [x, y, w, h] = r.hero
    tx('Title', [x, y, w, h * 0.5], d.title, 'hero', 'title')
    tx('Highlight', [x, y + h * 0.52, w, h * 0.48], d.highlight, 'hero', 'highlight', {
      color: 'accentInk',
    })
    tx('Verdict', r.verdict, d.verdict, 'heading', 'verdict')
    tx('Description', r.description, d.description, 'body', 'description', { color: 'secondary' })
    cells(r.index, d.sections.length).forEach(([x, y, w, h], i) => {
      rule('IndexRule' + i, x, y, w)
      box('IndexMark' + i, [x, y - 0.02, 0.045, 0.045], 'ink')
      tx(
        'IndexLabel' + i,
        [x, y + 0.12, w, h * 0.5],
        `${String(i + 1).padStart(2, '0')}  ${d.sections[i].label}`,
        'small',
        `sections[${i}].label`,
        { color: 'ink' },
      )
      tx(
        'IndexRef' + i,
        [x, y + h * 0.62, w, h * 0.35],
        d.sections[i].reference,
        'label',
        `sections[${i}].reference`,
      )
    })
    metrics(r.metrics, d.metrics, 'metrics', 'band', true)
  } else if (family.role === 'review') {
    metrics(r.metrics, d.metrics, 'metrics', layoutId === 'rail' ? 'rail' : 'row')
    cells(r.findings, d.findings.length, true).forEach(([x, y, w, h], i) => {
      tx(
        'FindingIndex' + i,
        [x, y, 0.48, h],
        String(i + 1).padStart(2, '0'),
        layoutId === 'band' ? 'heading' : 'index',
        'structural.index',
        { color: 'secondary' },
      )
      tx(
        'FindingLabel' + i,
        [x + 0.62, y, 1.42, h],
        d.findings[i].label,
        'heading',
        `findings[${i}].label`,
      )
      tx(
        'FindingBody' + i,
        [x + 2.2, y, w - 2.2, h - 0.1],
        d.findings[i].body,
        'body',
        `findings[${i}].body`,
      )
      rule('FindingRule' + i, x, y + h, w)
    })
    tx('Verdict', r.verdict, d.verdict, 'heading', 'verdict', { color: 'accentInk' })
  } else if (family.role === 'chart') {
    tx(
      'ChartLabel',
      [r.chart[0], r.chart[1], r.chart[2], 0.38],
      `${d.seriesName} · ${d.unit}`,
      'small',
      ['seriesName', 'unit'],
    )
    const frame = [r.chart[0], r.chart[1] + 0.48, r.chart[2], r.chart[3] - 0.48]
    const values = d.points.map((v) => v.value),
      span = Math.max(...values) - Math.min(...values)
    const magnitude = Math.max(...values.map(Math.abs), 1e-9)
    const numberFormat = values.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) > 1e8))
      ? '0.00E+00'
      : values.every(Number.isInteger)
        ? '0'
        : 'General'
    for (const [i, v] of d.points.entries())
      fitImpactText(
        v.label,
        [0, 0, frame[2] / values.length, 0.65],
        b.styles.label,
        `${path}.points[${i}].label`,
      )
    cs.push({
      kind: 'chart',
      name: 'EvidenceChart',
      frame,
      data: { categories: d.points.map((v) => v.label), series: [{ name: d.seriesName, values }] },
      focus: d.points.findIndex((v) => v.focus),
      numberFormat,
      minimum: Math.min(0, Math.min(...values) - magnitude * 0.14),
      maximum: Math.max(0, Math.max(...values) + Math.max(span, magnitude) * 0.25),
      inputPaths: d.points.map((_, i) => `${path}.points[${i}].label`),
    })
    notes(r.notes, d.notes)
    tx('Summary', r.summary, d.summary, 'heading', 'summary')
  } else if (family.role === 'comparison') {
    table('ComparisonTable', r.table, d.columns, d.rows)
    metrics(r.metrics, d.metrics, 'metrics', layoutId === 'side' ? 'compactRail' : 'row')
    tx('TableNote', r.tableNote, d.tableNote, 'small', 'tableNote')
    tx('Evidence', r.evidence, d.evidence, 'body', 'evidence')
  } else if (family.role === 'process') {
    metrics(r.metrics, d.metrics, 'metrics', 'rail')
    const vertical = layoutId === 'vertical',
      fs = cells(r.steps, d.steps.length, vertical)
    fs.forEach(([x, y, w, h], i) => {
      const p = `steps[${i}]`,
        v = d.steps[i]
      tx(
        'StepIndex' + i,
        [x, y, vertical ? 0.4 : w, 0.28],
        String(i + 1).padStart(2, '0'),
        'label',
        'structural.index',
        { alignment: vertical ? 'left' : 'center' },
      )
      tx(
        'StepTitle' + i,
        [
          x + (vertical ? 0.55 : 0),
          y + (vertical ? 0 : 0.42),
          vertical ? 1.8 : w,
          vertical ? h : 0.7,
        ],
        v.title,
        'heading',
        p + '.title',
        { alignment: vertical ? 'left' : 'center' },
      )
      tx(
        'StepBody' + i,
        [
          x + (vertical ? 2.55 : 0),
          y + (vertical ? 0 : 1.23),
          vertical ? w - 2.55 : w,
          vertical ? h : 1.35,
        ],
        v.body,
        'small',
        p + '.body',
        { alignment: vertical ? 'left' : 'center' },
      )
      if (i < fs.length - 1) {
        const a = vertical ? [x + 0.15, y + h + 0.01] : [x + w + 0.02, y + 0.8],
          z = vertical ? [x + 0.15, fs[i + 1][1] - 0.03] : [fs[i + 1][0] - 0.03, y + 0.8]
        cs.push({
          kind: 'arrow',
          name: 'StepArrow' + i,
          frame: [a[0], a[1], z[0] - a[0], z[1] - a[1]],
        })
      }
    })
    cs.push({ kind: 'feedback', name: 'Feedback', frame: r.feedback, vertical })
    tx('FeedbackNote', r.feedbackNote, d.feedback, 'small', 'feedback', { alignment: 'center' })
    tx('Assurance', r.assurance, d.assurance, 'heading', 'assurance')
  } else if (family.role === 'capacity') {
    metrics(r.metrics, d.metrics, 'metrics', layoutId === 'strip' ? 'row' : 'rail')
    tx('Explanation', r.explanation, d.explanation, 'body', 'explanation')
    rule('OutlookRule', r.outlook[0], r.outlook[1] - 0.14, r.outlook[2])
    tx('Outlook', r.outlook, d.outlook, 'heading', 'outlook', { color: 'accentInk' })
  } else if (family.role === 'scorecard') {
    table('ScorecardTable', r.table, d.columns, d.rows, 'rows', true)
    tx('TableNote', r.note, d.note, 'small', 'note')
  } else if (family.role === 'commitments') {
    cells(r.items, d.items.length, layoutId === 'ledger').forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`,
        vert = layoutId === 'ledger'
      rule('CommitmentRule' + i, x, y, w)
      tx(
        'CommitmentLabel' + i,
        [x, y + 0.12, vert ? w * 0.23 : w, 0.45],
        v.label,
        'small',
        p + '.label',
      )
      tx(
        'CommitmentValue' + i,
        [x + (vert ? w * 0.25 : 0), y + (vert ? 0.04 : 0.78), vert ? w * 0.3 : w, 0.72],
        `${v.baseline} → ${v.target} ${v.unit}`,
        'commitment',
        [p + '.baseline', p + '.target', p + '.unit'],
      )
      tx(
        'CommitmentAction' + i,
        [
          x + (vert ? w * 0.58 : 0),
          y + (vert ? 0.08 : 1.64),
          vert ? w * 0.42 : w,
          vert ? h - 0.1 : h - 1.64,
        ],
        v.action,
        'small',
        p + '.action',
      )
    })
    tx(
      'VerificationLabel',
      r.verificationLabel,
      d.verificationLabel,
      'label',
      'verificationLabel',
      { bold: true, color: 'ink' },
    )
    tx('Verification', r.verification, d.verification, 'body', 'verification')
  } else if (family.role === 'progress') {
    const fs = cells(r.items, d.items.length, layoutId === 'rows')
    fs.forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`,
        rows = layoutId === 'rows'
      if (!(v.target > 0) || v.actual < 0)
        throw Error(`${path}.${p}: actual must be nonnegative and target positive`)
      const ratio = v.actual / v.target,
        scale = Math.max(v.actual, v.target)
      tx(
        'ProgressLabel' + i,
        rows ? [x, y, w * 0.22, h * 0.55] : [x, y, w, 0.5],
        v.label,
        'heading',
        p + '.label',
      )
      const bx = rows ? x + w * 0.25 : x,
        by = rows ? y + 0.13 : y + 0.82,
        bw = rows ? w * 0.4 : w
      box('ProgressTrack' + i, [bx, by, bw, 0.16], 'tint')
      if (v.actual > 0)
        box(
          'ProgressActual' + i,
          [bx, by, (bw * v.actual) / scale, 0.16],
          v.focus ? 'spring' : 'series',
        )
      box(
        'ProgressTarget' + i,
        [bx + (bw * v.target) / scale - 0.008, by - 0.05, 0.016, 0.26],
        'ink',
      )
      const fmt = (n) => Number(n.toPrecision(8)).toString()
      tx(
        'ProgressNumbers' + i,
        rows ? [x + w * 0.69, y, w * 0.31, h * 0.55] : [x, y + 1.25, w, 0.6],
        `${v.actual} / ${v.target} ${v.unit} · ${fmt(ratio * 100)}%`,
        'small',
        [p + '.actual', p + '.target', p + '.unit'],
      )
      tx(
        'ProgressNote' + i,
        rows ? [x, y + h - 0.34, w, 0.34] : [x, y + 2.02, w, h - 2.02],
        v.note,
        'small',
        p + '.note',
      )
    })
    tx('Basis', r.basis, d.basis, 'small', 'basis')
  } else if (family.role === 'variance') {
    const expected = d.start + d.drivers.reduce((n, v) => n + v.value, 0),
      tol = 1e-9 * Math.max(1, Math.abs(expected), Math.abs(d.end))
    if (Math.abs(expected - d.end) > tol)
      throw Error(`${path}.end: drivers do not reconcile start to end`)
    const [x, y, w, h] = r.plot,
      values = [{ label: d.startLabel, value: d.start, from: 0, to: d.start, path: 'startLabel' }]
    let running = d.start
    d.drivers.forEach((v, i) => {
      values.push({ ...v, from: running, to: running + v.value, path: `drivers[${i}].label` })
      running += v.value
    })
    values.push({ label: d.endLabel, value: d.end, from: 0, to: d.end, path: 'endLabel' })
    const max = Math.max(0, ...values.flatMap((v) => [v.from, v.to])),
      min = Math.min(0, ...values.flatMap((v) => [v.from, v.to])),
      range = max - min || 1
    const top = y + 0.6,
      ph = h - 1.35,
      py = (v) => top + ((max - v) / range) * ph,
      step = w / values.length,
      bw = step * 0.56
    rule('VarianceZero', x, py(0), w)
    values.forEach((v, i) => {
      const xx = x + i * step + (step - bw) / 2,
        yy = Math.min(py(v.from), py(v.to)),
        hh = Math.abs(py(v.from) - py(v.to))
      if (hh > 0)
        box(
          'VarianceBar' + i,
          [xx, yy, bw, hh],
          i === values.length - 1 ? 'spring' : i === 0 ? 'pale' : 'series',
        )
      const label = String(v.value)
      tx(
        'VarianceValue' + i,
        [x + i * step, y + 0.06, step, 0.34],
        (i > 0 && i < values.length - 1 && v.value > 0 ? '+' : '') + label,
        'small',
        'structural.derivedValue',
        { alignment: 'center', color: 'ink' },
      )
      tx('VarianceLabel' + i, [x + i * step, y + h - 0.55, step, 0.52], v.label, 'small', v.path, {
        alignment: 'center',
      })
    })
    tx('Unit', r.unit, d.unit, 'small', 'unit')
    tx('Explanation', r.explanation, d.explanation, 'body', 'explanation')
    cs.push({
      kind: 'numeric-model',
      name: 'VarianceModel',
      frame: [x, y, 0, 0],
      model: { start: d.start, end: d.end, drivers: d.drivers.map((v) => v.value) },
    })
  } else if (family.role === 'milestones') {
    const vertical = layoutId === 'vertical',
      fs = cells(r.items, d.items.length, vertical)
    fs.forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`
      box('MilestoneMark' + i, [x, y + 0.03, 0.07, 0.07], v.focus ? 'spring' : 'series')
      if (!vertical) rule('MilestoneRule' + i, x + 0.09, y + 0.06, w - 0.09)
      tx(
        'MilestoneDate' + i,
        [x + 0.18, y + (vertical ? 0 : 0.17), vertical ? 1.2 : w - 0.18, 0.35],
        v.date,
        'label',
        p + '.date',
        { color: 'accentInk' },
      )
      tx(
        'MilestoneTitle' + i,
        vertical ? [x + 1.6, y, w * 0.3, h] : [x, y + 0.65, w, 0.7],
        v.title,
        'heading',
        p + '.title',
      )
      tx(
        'MilestoneEvidence' + i,
        vertical ? [x + w * 0.48, y, w * 0.32, h] : [x, y + 1.6, w, 1.25],
        v.evidence,
        'body',
        p + '.evidence',
      )
      tx(
        'MilestoneOwner' + i,
        vertical ? [x + w * 0.83, y, w * 0.17, h] : [x, y + 3.13, w, 0.55],
        v.owner,
        'small',
        p + '.owner',
      )
    })
    tx('Governance', r.governance, d.governance, 'small', 'governance')
  } else if (family.role === 'decisions') {
    cells(r.items, d.items.length, true).forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`,
        split = layoutId === 'split'
      rule('DecisionRule' + i, x, y, w)
      tx(
        'DecisionIndex' + i,
        [x, y + 0.12, 0.4, h - 0.2],
        String(i + 1).padStart(2, '0'),
        'index',
        'structural.index',
      )
      tx(
        'DecisionAsk' + i,
        [x + 0.58, y + 0.12, split ? w - 0.58 : w * 0.33, split ? 0.55 : h - 0.23],
        v.ask,
        'heading',
        p + '.ask',
      )
      tx(
        'DecisionImpact' + i,
        split
          ? [x + 0.58, y + 0.77, w - 0.58, h - 0.87]
          : [x + w * 0.41, y + 0.12, w * 0.37, h - 0.23],
        v.impact,
        'body',
        p + '.impact',
      )
      tx(
        'DecisionOwner' + i,
        split
          ? [r.owners[0], y + 0.12, r.owners[2], h - 0.23]
          : [x + w * 0.82, y + 0.12, w * 0.18, h - 0.23],
        `${v.owner}\n${v.due}`,
        'small',
        [p + '.owner', p + '.due'],
      )
    })
    tx('Consequence', r.consequence, d.consequence, 'body', 'consequence', { color: 'accentInk' })
  } else throw Error(`Unknown impact role ${family.role}`)
  return cs
}

export function resolveImpactDeck(design, content) {
  const layouts = [],
    warnings = []
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  for (const [s, slide] of content.slides.entries()) {
    const f = design.impact.families[slide.type]
    if (!f) throw Error(`slides[${s}]: unregistered impact type ${slide.type}`)
    if (slide.customOps) throw Error(`slides[${s}]: customOps forbidden`)
    const schema = JSON.parse(
      readFileSync(new URL(`./schemas/${slide.type}.schema.json`, import.meta.url)),
    )
    assertDesignValue(slide.data, schema, schema, `slides[${s}].data`)
    const focuses = (xs) => {
      if (xs?.filter((v) => v.focus).length > 1) throw Error(`slides[${s}]: maximum one focus`)
    }
    focuses(slide.data.metrics)
    focuses(slide.data.points)
    focuses(slide.data.items)
    const failures = []
    const candidates = Object.entries(f.variants).flatMap(([layoutId, v]) => {
      try {
        const components = compileImpactLayout(
          design,
          f,
          layoutId,
          v,
          slide.data,
          `slides[${s}].data`,
        )
        components.push({
          ...fitImpactText(
            `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
            design.impact.chrome.page,
            { ...design.impact.styles.label, alignment: 'right' },
            'structural.page',
          ),
          name: 'Page',
        })
        for (const c of components) {
          const [x, y, w, h] = c.frame
          if (
            x < 0 ||
            y < 0 ||
            w < 0 ||
            h < 0 ||
            x + w > design.canvas.widthIn + 0.001 ||
            y + h > design.canvas.heightIn + 0.001
          )
            throw Error(`${c.name}: outside canvas`)
        }
        return [
          {
            layoutId,
            role: f.role,
            components,
            fingerprint: designHash({
              role: f.role,
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
        design.impact.rhythm.maxConsecutive,
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
