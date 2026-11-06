import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'

// Every component is planned and capacity-checked before drawing.
export function fitClayText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = ((frame[2] - 0.04) * 72) / style.sizePt / (style.bold ? 1.08 : 1)
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
      `${path}: ${lines} lines exceed ${frame[3].toFixed(2)}in; select another layout, reorganize or split`,
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
export function compileClayLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.clay,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap
  const tx = (name, f, value, key = 'body', field = name, extra = {}) => {
    const paths = (Array.isArray(field) ? field : [field]).map((k) => `${path}.${k}`)
    const c = { ...fitClayText(value, f, { ...b.styles[key], ...extra }, paths[0]), name, paths }
    c.frame[3] = c.requiredHeight
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule') => cs.push({ kind: 'box', name, frame, color })
  const rule = (name, x, y, w, vertical = false) =>
    box(name, vertical ? [x, y, 0.009, w] : [x, y, w, 0.009])
  const cells = (f, n, vertical = false) => {
    const g = vertical ? 0.1 : gap
    return Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  }
  const metric = (f, v, p, name, compact = false) => {
    const [x, y, w, h] = f,
      st = compact ? { ...b.styles.number, sizePt: 25 } : b.styles.number
    // Number and unit share a text owner and baseline. The combined width is checked.
    const width =
      (textUnits(v.value) * st.sizePt + textUnits(v.unit) * b.styles.unit.sizePt + 8) / 72
    if (width > w - 0.04) throw Error(`${path}.${p}: value and unit exceed metric width`)
    const value = tx(name + 'Value', [x, y, w, 0.66], v.value, 'number', p + '.value', {
      ...st,
      color: v.focus ? 'accent' : 'ink',
    })
    value.runs = [
      { text: v.value, style: value.style },
      { text: ' ' + v.unit, style: { ...b.styles.unit, color: v.focus ? 'accent' : 'ink' } },
    ]
    value.text = v.value + ' ' + v.unit
    value.paths.push(`${path}.${p}.unit`)
    if (compact) {
      tx(
        name + 'Details',
        [x, y + 0.62, w, h - 0.62],
        [v.label, v.note].filter(Boolean).join(' · '),
        'small',
        [p + '.label', ...(v.note ? [p + '.note'] : [])],
      )
    } else {
      tx(name + 'Label', [x, y + 0.73, w, 0.45], v.label, 'label', p + '.label')
      if (v.note) tx(name + 'Note', [x, y + 1.26, w, h - 1.26], v.note, 'small', p + '.note')
    }
  }
  const metrics = (f, vs, field, vertical = false, compact = false) => {
    const fs = cells(f, vs.length, vertical)
    fs.forEach((ff, i) => {
      if (i && !vertical) rule(field + 'Divider' + i, ff[0] - gap / 2, ff[1], ff[3], true)
      metric(ff, vs[i], `${field}[${i}]`, field + i, compact)
    })
  }
  const chip = (name, x, y, index) =>
    cs.push({
      kind: 'chip',
      name,
      frame: [x, y, 0.4, 0.4],
      text: String(index + 1).padStart(2, '0'),
      style: b.styles.chip,
      color: 'pink',
    })
  const ornament = (corner, large = false) =>
    cs.push({
      kind: 'ornament',
      name: 'Ornament' + corner,
      frame: [
        corner.includes('r') ? design.canvas.widthIn - (large ? 1.2 : 0.6) : 0,
        corner.includes('b') ? 7.5 - (large ? 1.2 : 0.6) : 0,
        large ? 1.2 : 0.6,
        large ? 1.2 : 0.6,
      ],
      corner,
      color: corner === 'tl' ? 'clay' : corner === 'br' ? 'camel' : 'pink',
    })
  const role = family.role
  if (role === 'cover') {
    ;['tl', 'tr', 'bl', 'br'].forEach((k) => ornament(k, true))
  } else {
    ornament('tr')
    if (role === 'commitments') ornament('bl')
  }
  tx(
    'Section',
    role === 'cover' ? [1.5, 0.53, 10.4, 0.28] : b.chrome.section,
    d.section,
    'label',
    'section',
    role === 'commitments' ? { alignment: 'center' } : {},
  )
  if (role !== 'cover' && role !== 'commitments') {
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Subtitle', b.chrome.subtitle, d.subtitle, 'body', 'subtitle')
  }
  if (role === 'cover') {
    tx('Title', r.hero, d.title, 'hero', 'title')
    rule('CoverAccentRule', r.hero[0], r.hero[1] + r.hero[3] + 0.18, 0.56)
    cs.at(-1).color = 'accent'
    cs.at(-1).frame[3] = 0.04
    tx('Quote', r.quote, d.quote, 'quote', 'quote')
    tx('Description', r.description, d.description, 'body', 'description')
    metrics(r.metrics, d.metrics, 'metrics', false, true)
    const [x, y, w, h] = r.asset
    box('PhotoBacking', [x - 0.12, y + 0.12, w, h], 'pink')
    cs.push({ kind: 'placeholder', name: 'PhotoSlot', frame: [x, y, w, h], color: 'paper' })
    tx(
      'AssetLabel',
      [x + 0.18, y + h / 2 - 0.3, w - 0.36, 0.8],
      d.assetLabel,
      'heading',
      'assetLabel',
      { alignment: 'center' },
    )
    tx(
      'AssetCaption',
      [x + 0.16, y + h - 1.1, w - 0.32, 0.9],
      d.assetCaption,
      'small',
      'assetCaption',
      { alignment: 'center' },
    )
    // Subtitle remains visible; it is not a hidden schema field.
    tx('Subtitle', [r.hero[0], 4.65, 7.3, 0.3], d.subtitle, 'small', 'subtitle')
  } else if (role === 'overview') {
    const vertical = layoutId === 'rail'
    metrics(r.metrics, d.metrics, 'metrics', vertical, true)
    if (vertical) rule('ColumnDivider', r.findings[0] - gap, r.findings[1], r.findings[3], true)
    cells(r.findings, d.findings.length, vertical).forEach(([x, y, w, h], i) => {
      chip('FindingChip' + i, x, y, i)
      tx(
        'FindingTitle' + i,
        [x + 0.56, y, w - 0.56, 0.38],
        d.findings[i].title,
        'heading',
        `findings[${i}].title`,
        { bold: true },
      )
      tx(
        'FindingBody' + i,
        [x + 0.56, y + 0.49, w - 0.56, h - 0.49],
        d.findings[i].body,
        'body',
        `findings[${i}].body`,
      )
    })
  } else if (role === 'chart') {
    if (d.points.some((v) => !Number.isFinite(v.value)))
      throw Error(`${path}.points: finite raw values required`)
    const vals = d.points.map((v) => v.value),
      lo = Math.min(0, ...vals),
      hi = Math.max(0, ...vals),
      span = hi - lo || 1
    const minimum = lo < 0 ? lo - span * 0.18 : 0,
      maximum = hi + span * 0.23
    const scientific = vals.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) >= 1e7))
    cs.push({
      kind: 'chart',
      name: 'EvidenceChart',
      frame: r.chart,
      data: {
        categories: d.points.map((v) => v.label),
        series: [{ name: d.seriesName, values: vals }],
      },
      minimum,
      maximum,
      numberFormat: scientific ? '0.00E+00' : vals.every(Number.isInteger) ? '0' : '0.0#####',
      inside: lo > 0 || Math.min(...vals) > hi * 0.25,
      inputPaths: d.points.map((_, i) => `${path}.points[${i}].label`),
    })
    tx(
      'Series',
      [r.chart[0], r.chart[1] - 0.32, r.chart[2], 0.28],
      d.seriesName + ' · ' + d.unit,
      'label',
      ['seriesName', 'unit'],
    )
    tx('Caption', r.caption, d.caption, 'small', 'caption')
    rule(
      'ColumnDivider',
      layoutId === 'chartLeft' ? r.analysis[0] - gap : r.chart[0] - gap,
      2.45,
      3.7,
      true,
    )
    tx(
      'AnalysisLabel',
      [r.analysis[0], r.analysis[1], r.analysis[2], 0.28],
      d.analysisLabel,
      'label',
      'analysisLabel',
    )
    tx(
      'Analysis',
      [r.analysis[0], r.analysis[1] + 0.48, r.analysis[2], 1.2],
      d.analysis,
      'body',
      'analysis',
    )
    rule('AnalysisRule', r.analysis[0], r.analysis[1] + 1.95, r.analysis[2])
    metric(
      [r.analysis[0], r.analysis[1] + 2.15, r.analysis[2], 1.55],
      d.conclusion,
      'conclusion',
      'Conclusion',
      true,
    )
  } else if (role === 'comparison' || role === 'status') {
    if (d.rows.some((v) => v.cells.length !== d.columns.length))
      throw Error(`${path}.rows: every row must have one cell per column`)
    if (role === 'status' && d.columns.filter((v) => v.kind === 'status').length !== 1)
      throw Error(`${path}.columns: exactly one status column required`)
    if (
      d.focusColumn !== undefined &&
      (!Number.isInteger(d.focusColumn) || d.focusColumn < 0 || d.focusColumn >= d.columns.length)
    )
      throw Error(`${path}.focusColumn: out of range`)
    const total = d.columns.reduce((a, v) => a + v.weight, 0),
      widths = d.columns.map((v) => (r.table[2] * v.weight) / total),
      rows = [d.columns.map((v) => v.label), ...d.rows.map((v) => v.cells)],
      rh = r.table[3] / rows.length,
      bindings = []
    rows.forEach((row, i) => {
      let x = r.table[0]
      row.forEach((v, j) => {
        const f = [x + 0.06, r.table[1] + i * rh + 0.04, widths[j] - 0.12, rh - 0.08],
          p = i === 0 ? `columns[${j}].label` : `rows[${i - 1}].cells[${j}]`
        fitClayText(v, f, b.styles.small, `${path}.${p}`)
        bindings.push({ frame: f, paths: [`${path}.${p}`] })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name: 'EvidenceTable',
      frame: r.table,
      cells: rows,
      widths,
      rowHeights: rows.map(() => rh),
      columns: d.columns,
      rows: d.rows,
      status: role === 'status',
      focusColumn: d.focusColumn,
      bindings,
    })
    tx('TableNote', r.tableNote, d.tableNote, 'small', 'tableNote')
    if (role === 'comparison') {
      if (layoutId === 'side') rule('ColumnDivider', r.evidence[0] - gap, r.evidence[1], 3.7, true)
      tx('Evidence', r.evidence, d.evidence, 'body', 'evidence')
      const [x, y, w, h] = r.quote
      box('QuoteBar', [x, y, 0.03, h], 'accent')
      tx('Quotation', [x + 0.18, y, w - 0.18, h - 0.47], d.quote, 'quote', 'quote')
      tx(
        'Attribution',
        [x + 0.18, y + h - 0.35, w - 0.18, 0.35],
        d.attribution,
        'small',
        'attribution',
      )
    }
  } else if (role === 'process') {
    metrics(r.metrics, d.metrics, 'metrics', true, true)
    rule('ColumnDivider', r.steps[0] - gap, r.steps[1], r.steps[3], true)
    const vertical = layoutId === 'vertical',
      fs = cells(r.steps, d.steps.length, vertical)
    if (vertical) rule('ProcessAxis', r.steps[0] + 0.2, r.steps[1] + 0.2, r.steps[3] - 0.4, true)
    else rule('ProcessAxis', r.steps[0] + 0.2, r.steps[1] + 0.4, r.steps[2] - 0.4)
    fs.forEach(([x, y, w, h], i) => {
      chip('StepChip' + i, x, y + (vertical ? 0 : 0.2), i)
      tx(
        'StepTitle' + i,
        [x + 0.55, y, vertical ? 1.4 : w - 0.55, vertical ? h : 0.4],
        d.steps[i].title,
        'heading',
        `steps[${i}].title`,
        { bold: true },
      )
      tx(
        'StepBody' + i,
        vertical ? [x + 2.1, y, w - 2.1, h] : [x, y + 0.85, w, h - 0.85],
        d.steps[i].body,
        'body',
        `steps[${i}].body`,
      )
    })
  } else if (role === 'kpi') {
    const vertical = layoutId === 'rail'
    metrics(r.metrics, d.metrics, 'metrics', vertical, vertical)
    if (vertical) rule('ColumnDivider', r.explanation[0] - gap, 2.45, 3.7, true)
    tx('Explanation', r.explanation, d.explanation, vertical ? 'quote' : 'body', 'explanation')
  } else if (role === 'commitments') {
    tx('Title', r.title, d.title, 'hero', 'title', { alignment: 'center' })
    tx('Subtitle', [1.35, 2.17, 10.63, 0.33], d.subtitle, 'small', 'subtitle', {
      alignment: 'center',
    })
    cells(r.items, d.items.length, layoutId === 'ledger').forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`,
        row = layoutId === 'ledger'
      if (i && !row) rule('CommitmentDivider' + i, x - gap / 2, y, h - 0.2, true)
      if (row) rule('CommitmentRule' + i, x, y, w)
      tx(
        'CommitmentLabel' + i,
        row ? [x, y + 0.1, w * 0.21, h - 0.1] : [x, y, w, 0.5],
        v.label,
        'label',
        p + '.label',
      )
      const text = `${v.baseline} → ${v.target} ${v.unit}`
      const transition = tx(
        'CommitmentValue' + i,
        row ? [x + w * 0.23, y + 0.1, w * 0.25, h - 0.1] : [x, y + 0.7, w, 0.7],
        text,
        'transition',
        [p + '.baseline', p + '.target', p + '.unit'],
        { sizePt: row ? 18 : 23 },
      )
      transition.runs = [
        { text: `${v.baseline} → ${v.target}`, style: transition.style },
        { text: ' ' + v.unit, style: b.styles.unit },
      ]
      tx(
        'CommitmentDescription' + i,
        row ? [x + w * 0.51, y + 0.1, w * 0.29, h - 0.1] : [x, y + 1.55, w, 0.7],
        v.description,
        'body',
        p + '.description',
      )
      tx(
        'CommitmentBasis' + i,
        row ? [x + w * 0.82, y + 0.1, w * 0.18, h - 0.1] : [x, y + 2.35, w, h - 2.35],
        v.basis,
        'small',
        p + '.basis',
      )
    })
    rule('MechanismRule', r.mechanism[0], r.mechanism[1] - 0.2, r.mechanism[2])
    tx('Mechanism', r.mechanism, d.mechanism, 'body', 'mechanism', { alignment: 'center' })
  } else throw Error(`Unregistered clay role ${role}`)
  rule('VerdictRule', b.chrome.verdict[0], b.chrome.verdict[1] - 0.16, b.chrome.verdict[2])
  tx(
    'Verdict',
    b.chrome.verdict,
    d.verdict,
    'small',
    'verdict',
    role === 'commitments' ? { alignment: 'center' } : {},
  )
  tx(
    'Source',
    role === 'cover' ? [1.4, 6.84, 10.03, 0.26] : b.chrome.source,
    d.source,
    'small',
    'source',
  )
  return cs
}
export function resolveClayDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'clayCoverSlide' ||
      content.slides.at(-1)?.type !== 'clayCommitmentsSlide')
  )
    throw Error(
      'Complete Warm Clay decks open with cover and end with commitments; use designScope excerpt for extracts',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const f = design.clay.families[slide.type]
    if (!f) throw Error(`slides[${s}]: unregistered clay type`)
    if (slide.customOps) throw Error(`slides[${s}]: customOps forbidden`)
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const focuses = [
      ...(slide.data.metrics ?? []),
      ...(slide.data.conclusion ? [slide.data.conclusion] : []),
    ].filter((v) => v.focus)
    if (focuses.length > 1) throw Error(`slides[${s}]: maximum one foreground focus`)
    const failures = [],
      candidates = Object.entries(f.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileClayLayout(
            design,
            f,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
          components.push({
            ...fitClayText(
              String(s + 1).padStart(2, '0'),
              design.clay.chrome.page,
              { ...design.clay.styles.small, role: 'numeral', alignment: 'right' },
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
    let selected
    try {
      selected = selectDesignLayout(
        candidates,
        slide.layoutId ?? 'auto',
        layouts,
        design.clay.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(selected, {
      slideIndex: s,
      slideType: slide.type,
      candidates: candidates.map((c) => c.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(selected)
    if (selected.repeated) warnings.push(`slides[${s}]: repeated composition`)
  }
  return { layouts, warnings }
}
