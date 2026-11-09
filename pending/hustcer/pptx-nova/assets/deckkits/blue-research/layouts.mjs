import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'

export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  return n && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(9)).toString()
}
export const numberFormat = (xs) =>
  xs.some((n) => n && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7))
    ? '0.00E+00'
    : xs.every(Number.isInteger)
      ? '0'
      : '0.0'
const near = (a, b) => Math.abs(a - b) <= 1e-8 * Math.max(1, Math.abs(a), Math.abs(b))
export function compileResearchLayout(design, family, id, variant, d, path = 'data') {
  const b = design.research,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap
  const tx = (name, frame, value, key = 'body', fields = name, extra = {}) => {
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) => `${path}.${k}`)
    const style = { ...b.styles[key], ...extra }
    const fit = fitTextPlan(value, frame, style, paths[0])
    // Canonical Arial's paragraph advance includes the requested line spacing.
    // Keep the shared width/wrapping plan and add this family's measured bound.
    const advance = Math.max(style.sizePt >= 23 ? 1.18 : 1.5, 1.2 * style.lineHeight)
    fit.requiredHeight = (fit.estimatedLines * style.sizePt * advance) / 72 + 0.025
    if (fit.requiredHeight > frame[3] + 0.002)
      throw Error(
        `${paths[0]}: requested line spacing exceeds ${frame[3].toFixed(2)}in; select a legal layout, reorganize or split`,
      )
    const c = {
      ...fit,
      name,
      paths,
    }
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule', kind = 'box') => cs.push({ kind, name, frame, color })
  const line = (name, x, y, w, color = 'rule', vertical = false, dash = false) =>
    cs.push({
      kind: 'path',
      name,
      frame: vertical ? [x, y, 0.01, w] : [x, y, w, 0.01],
      line: color,
      linePt: b.spacing.rulePt,
      dash,
      path: {
        width: 100000,
        height: 100000,
        commands: [
          { type: 'move', x: 0, y: 0 },
          { type: 'line', x: vertical ? 0 : 100000, y: vertical ? 100000 : 0 },
        ],
      },
    })
  const cells = (f, n, vertical = false, g = gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const owned = (
    name,
    f,
    v,
    color,
    fields,
    key = 'small',
    shapeKind = 'ellipse',
    textColor = 'paper',
  ) =>
    Object.assign(
      tx(name, f, v, key, fields, { alignment: 'center', color: textColor, bold: true }),
      { kind: 'owned', color, shapeKind, anchor: 'middle' },
    )
  const notes = (f, vs, prefix = 'notes') => {
    cells(f, vs.length, f[3] > 2, 0.13).forEach(([x, y, w, h], i) => {
      line('NoteRule' + i, x, y, w, 'accent')
      tx(
        'NoteHeading' + i,
        [x, y + 0.1, w, 0.34],
        vs[i].heading,
        'heading',
        `${prefix}[${i}].heading`,
      )
      tx('NoteBody' + i, [x, y + 0.49, w, h - 0.49], vs[i].body, 'body', `${prefix}[${i}].body`)
    })
  }
  const table = (name, f, columns, rows, paths, tones) => {
    if (rows.some((row) => row.length !== columns.length))
      throw Error('Every table row must match columns')
    const widths = columns.map(
        (v) => (f[2] * v.weight) / columns.reduce((a, v) => a + v.weight, 0),
      ),
      all = [columns.map((v) => v.label), ...rows],
      rh = f[3] / all.length,
      bindings = []
    all.forEach((row, i) => {
      let x = f[0]
      row.forEach((v, j) => {
        if (/[\r\n]/u.test(v))
          throw Error('Native table cells require one paragraph; use automatic wrapping')
        const frame = [x + 0.08, f[1] + i * rh + 0.07, widths[j] - 0.16, rh - 0.14],
          st = {
            ...b.styles.table,
            bold: i === 0 || j === 0,
            color: tones?.[i]?.[j] === 'deep' ? 'paper' : 'ink',
          }
        const ps = (Array.isArray(paths(i, j)) ? paths(i, j) : [paths(i, j)]).map(
          (k) => `${path}.${k}`,
        )
        fitTextPlan(v, frame, st, ps[0])
        bindings.push({ paths: ps, frame, style: st })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name,
      frame: f,
      cells: all,
      columns,
      widths,
      rowHeights: all.map(() => rh),
      focusColumn: -1,
      bindings,
      useBindingStyles: true,
      blueRules: true,
      cellFills: tones,
    })
  }
  const role = family.role
  if (role !== 'cover') {
    const masthead = tx(
      'ReportMasthead',
      [0.6, 0.4, 9.5, 0.3],
      d.reportTitle,
      'small',
      'reportTitle',
      { color: 'navy' },
    )
    masthead.trackingPt = 0.85
    tx('ChapterHeading', [10.35, 0.4, 2.38, 0.3], d.eyebrow, 'small', 'eyebrow', {
      alignment: 'right',
    })
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    tx('Subtitle', b.chrome.subtitle, `${d.subtitle} · ${d.period}`, 'small', [
      'subtitle',
      'period',
    ])
  }
  if (['cover', 'scorecard', 'findings', 'implications'].includes(role)) {
    compileResearchSignature({ role, b, r, id, d, tx, box, line, cells, owned, table, cs })
  } else if (role === 'overview') {
    const f = r.claims,
      rows = cells(f, d.claims.length, true, 0.18)
    line('MetricSpine', f[0] + 0.45, f[1] + 0.2, f[3] - 0.45, 'rule', true)
    rows.forEach(([x, y, w, h], i) => {
      const v = d.claims[i]
      owned(
        'MetricCapsule' + i,
        [x, y + 0.05, 0.9, 0.43],
        v.metric,
        i === 1 ? 'deep' : 'navy',
        `claims[${i}].metric`,
      )
      tx(
        'ClaimHeading' + i,
        [x + 1.13, y, w - 1.13, 0.55],
        `${String(i + 1).padStart(2, '0')}  ${v.heading}`,
        'heading',
        `claims[${i}].heading`,
      )
      tx(
        'ClaimBody' + i,
        [x + 1.13, y + 0.62, w - 1.13, h - 0.62],
        v.body,
        'body',
        `claims[${i}].body`,
      )
    })
    notes(r.notes, d.notes)
    const af = r.agenda
    cells(af, d.agenda.length, false, 0.18).forEach(([x, y, w, h], i) =>
      tx(
        'Agenda' + i,
        [x, y, w, h],
        `${i + 1} ${d.agenda[i].label}  ${d.agenda[i].page}`,
        'small',
        [`agenda[${i}].label`, `agenda[${i}].page`],
        { color: 'navy', bold: true },
      ),
    )
  } else if (role === 'evidence') {
    const ch = d.chart,
      n = ch.categories.length
    if (ch.series.some((v) => v.values.length !== n || v.values.some((x) => !Number.isFinite(x))))
      throw Error('Chart series must match every category with finite values')
    if (
      ch.kind === 'stacked' &&
      (ch.series.length !== 2 || ch.series.some((v) => v.values.some((x) => x < 0)))
    )
      throw Error('Stacked evidence requires two nonnegative series')
    if (ch.kind !== 'stacked' && ch.series.length !== 1)
      throw Error('Column/line evidence requires one series')
    if (
      ch.forecastFrom !== undefined &&
      (!Number.isInteger(ch.forecastFrom) ||
        ch.kind !== 'column' ||
        ch.forecastFrom < 0 ||
        ch.forecastFrom >= n - 1)
    )
      throw Error('Forecast boundary must split a single column series')
    const f = r.plot,
      values = ch.series.flatMap((v) => v.values),
      totals = ch.categories.map((_, i) => ch.series.reduce((a, v) => a + v.values[i], 0)),
      hi = Math.max(0, ...values, ...totals),
      lo = Math.min(0, ...values),
      span = hi - lo || 1
    tx(
      'ChartHeading',
      [f[0], f[1], r.capsule[0] - f[0] - 0.2, 0.45],
      `${ch.series.map((v) => v.name).join(' / ')} · ${ch.unit}`,
      'heading',
      ['chart.unit', ...ch.series.map((_, i) => `chart.series[${i}].name`)],
    )
    tx(
      'ChartPhaseLabel',
      [f[0], f[1] + 0.43, f[2], 0.27],
      ch.phaseLabel,
      'small',
      'chart.phaseLabel',
    )
    const cf = [f[0], f[1] + 0.85, f[2], f[3] - 0.85]
    cs.push({
      kind: 'chart',
      name: 'EvidenceChart',
      frame: cf,
      chartKind: ch.kind === 'line' ? 'line' : 'column',
      variant: ch.kind === 'stacked' ? 'stacked' : 'clustered',
      data: {
        categories: ch.categories,
        series: ch.series.map((v) => ({ name: v.name, values: v.values })),
      },
      minimum: lo < 0 ? lo - span * 0.15 : 0,
      maximum: hi + span * 0.25,
      focusPoint: n - 1,
      uniformSeriesTone: 'accent',
      seriesTone: 'deep',
      numberFormat: numberFormat(values),
      forecastFrom: ch.forecastFrom,
      pointTones:
        ch.forecastFrom === undefined
          ? undefined
          : ch.categories.map((_, i) => (i > ch.forecastFrom ? 'paper' : 'accent')),
      inputPaths: [
        ...ch.categories.map((_, i) => `${path}.chart.categories[${i}]`),
        ...ch.series.flatMap((v, i) =>
          v.values.map((_, j) => `${path}.chart.series[${i}].values[${j}]`),
        ),
      ],
    })
    notes(r.notes, d.notes)
    owned(
      'EvidenceCapsule',
      r.capsule,
      `${d.metric.value} · ${d.metric.label}`,
      'pale',
      ['metric.value', 'metric.label'],
      'small',
      'ellipse',
      'navy',
    )
  } else if (role === 'matrix') {
    if (d.rows.some((v) => v.cells.length !== d.columns.length))
      throw Error('Matrix must retain every column and cell')
    const f = r.table
    table(
      'HeatMatrix',
      f,
      d.columns,
      d.rows.map((v) => v.cells.map((c) => c.text)),
      (i, j) => (i ? `rows[${i - 1}].cells[${j}].text` : `columns[${j}].label`),
      [d.columns.map(() => 'paper'), ...d.rows.map((v) => v.cells.map((c) => c.tone))],
    )
    tx('TableMethodology', r.note, d.methodology, 'small', 'methodology')
    tx(
      'QuoteMark',
      [r.excerpt[0], r.excerpt[1] - 0.03, 0.85, 0.8],
      '“',
      'quote',
      'structural.quote',
    )
    line('QuoteRule', r.excerpt[0] + 0.9, r.excerpt[1] + 0.16, r.excerpt[2] - 0.9, 'accent')
    tx(
      'Excerpt',
      [r.excerpt[0], r.excerpt[1] + 0.72, r.excerpt[2], r.excerpt[3] - 1.2],
      d.excerpt,
      'body',
      'excerpt',
    )
    tx(
      'Attribution',
      [r.excerpt[0], r.excerpt[1] + r.excerpt[3] - 0.37, r.excerpt[2], 0.34],
      d.attribution,
      'small',
      'attribution',
      { bold: true, color: 'navy' },
    )
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
      cum = [0, d.opening]
    let sum = d.opening
    d.drivers.forEach((v) => {
      sum += v.value
      cum.push(sum)
    })
    const lo = Math.min(0, ...cum),
      hi = Math.max(0, ...cum),
      span = hi - lo || 1,
      yy = (v) => y + 0.6 + (h - 1.25) * (1 - (v - lo) / span),
      slot = w / all.length
    tx('BridgeUnit', [x, y, w, 0.3], d.unit, 'small', 'unit', { color: 'navy' })
    line('BridgeZero', x, yy(0), w, 'navy')
    sum = d.opening
    all.forEach((v, i) => {
      const endpoint = i === 0 || i === all.length - 1,
        from = endpoint ? 0 : sum,
        to = endpoint ? v.value : sum + v.value,
        bx = x + i * slot + 0.14 * slot,
        bw = slot * 0.72,
        top = Math.min(yy(from), yy(to)),
        height = Math.abs(yy(from) - yy(to))
      if (!endpoint) sum = to
      if (height)
        box(
          'BridgeBar' + i,
          [bx, top, bw, height],
          i === 0 ? 'history' : endpoint ? 'deep' : 'accent',
        )
      else line('BridgeZeroStep' + i, bx, top, bw, 'deep')
      tx(
        'BridgeValue' + i,
        [bx - 0.1, Math.max(y + 0.35, top - 0.25), bw + 0.2, 0.26],
        `${!endpoint && v.value > 0 ? '+' : ''}${number(v.value)}`,
        'small',
        i === 0 ? 'opening' : endpoint ? 'closing' : `drivers[${i - 1}].value`,
        { alignment: 'center', bold: true, color: 'navy' },
      )
      tx(
        'BridgeLabel' + i,
        [bx - 0.1, y + h - 0.43, bw + 0.2, 0.4],
        v.label,
        'small',
        i === 0 ? 'openingLabel' : endpoint ? 'closingLabel' : `drivers[${i - 1}].label`,
        { alignment: 'center' },
      )
      if (i < all.length - 1)
        line('BridgeConnector' + i, bx + bw, yy(to), slot * 0.28, 'muted', false, true)
    })
    const nf = r.drivers,
      den = d.drivers.reduce((a, v) => a + Math.abs(v.value), 0)
    cells(nf, d.drivers.length, true, 0.12).forEach(([x, y, w, h], i) => {
      const v = d.drivers[i]
      tx(
        'DriverHeading' + i,
        [x, y, w, 0.34],
        `${v.label} · ${number(v.value)} ${d.unit}`,
        'small',
        [`drivers[${i}].label`, `drivers[${i}].value`, 'unit'],
        { bold: true, color: 'navy' },
      )
      if (den && v.value)
        box(
          'Contribution' + i,
          [x, y + 0.43, (w * Math.abs(v.value)) / den, 0.065],
          i === 0 ? 'deep' : 'accent',
        )
      tx('DriverBody' + i, [x, y + 0.57, w, h - 0.57], v.body, 'body', `drivers[${i}].body`)
    })
  } else if (role === 'tiers') {
    const rows = d.rows.map((v) => [
        v.label,
        `${number(v.value)} ${d.unit}`,
        v.secondary,
        v.tertiary,
      ]),
      cols = d.headers.map((label, i) => ({
        label,
        weight: [2, 2.2, 1.5, 1.5][i],
        align: i === 0 ? 'left' : 'center',
      })),
      f = r.table
    if (d.rows.some((v) => v.value < 0)) throw Error('Microbars require nonnegative values')
    table(
      'TierTable',
      f,
      cols,
      rows,
      (i, j) =>
        i
          ? j === 1
            ? [`rows[${i - 1}].value`, 'unit']
            : `rows[${i - 1}].${['label', 'value', 'secondary', 'tertiary'][j]}`
          : `headers[${j}]`,
      [cols.map(() => 'paper'), ...d.rows.map((v) => ['paper', v.tone, 'paper', 'paper'])],
    )
    const c = cs.at(-1),
      mx = Math.max(0, ...d.rows.map((v) => v.value)),
      rh = f[3] / (rows.length + 1)
    d.rows.forEach((v, i) => {
      if (mx && v.value)
        box(
          'TierMicrobar' + i,
          [
            f[0] + c.widths[0] + 0.1,
            f[1] + (i + 2) * rh - 0.1,
            ((c.widths[1] - 0.2) * v.value) / mx,
            0.04,
          ],
          v.tone === 'deep' ? 'paper' : 'navy',
        )
    })
    tx('TierMethodology', r.note, d.methodology, 'small', 'methodology')
    notes(r.notes, d.notes)
  } else if (role === 'timeline') {
    // Nonnegative elapsed intervals are numeric evidence, not probe-only
    // control indexes. Derive all positions and labels from this one source.
    let elapsed = d.start
    const events = d.events.map((v) => ({ ...v, at: (elapsed += v.elapsed) }))
    if (
      !(d.end > d.start) ||
      events.some((v, i) => v.at < d.start || v.at > d.end || (i && v.at <= events[i - 1].at))
    )
      throw Error('Timeline needs ordered distinct events inside positive range')
    const f = r.events,
      vertical = id === 'vertical',
      [x, y, w, h] = f,
      n = events.length
    tx('TimelineUnit', r.unit, `${number(d.start)} – ${number(d.end)} ${d.unit}`, 'small', [
      'start',
      'end',
      'unit',
    ])
    if (vertical) line('TimelineAxis', x + 0.2, y + 0.15, h - 0.3, 'muted', true)
    else line('TimelineAxis', x + 0.5, y + 0.75, w - 1, 'muted')
    cells(f, n, vertical, 0.24).forEach(([xx, yy, ww, hh], i) => {
      const v = events[i],
        cx = vertical ? x + 0.2 : x + 0.5 + ((w - 1) * (v.at - d.start)) / (d.end - d.start),
        cy = vertical ? yy + 0.24 : y + 0.75
      if (!vertical) {
        ww = Math.min(
          ww,
          i
            ? cx - (x + 0.5 + ((w - 1) * (events[i - 1].at - d.start)) / (d.end - d.start)) - 0.12
            : ww,
          i < n - 1
            ? x + 0.5 + ((w - 1) * (events[i + 1].at - d.start)) / (d.end - d.start) - cx - 0.12
            : ww,
        )
        xx = Math.max(x, Math.min(x + w - ww, cx - ww / 2))
      }
      owned(
        'EventNumber' + i,
        [cx - 0.16, cy - 0.16, 0.32, 0.32],
        String(i + 1),
        i === n - 1 ? 'orange' : 'deep',
        'structural.number',
        'small',
        'ellipse',
        i === n - 1 ? 'navy' : 'paper',
      )
      if (vertical) {
        tx(
          'EventDate' + i,
          [xx + 0.65, yy, 1.55, 0.4],
          `${number(v.at)} ${d.unit}`,
          'small',
          [`events[${i}].elapsed`, 'unit'],
          { bold: true, color: 'navy' },
        )
        tx('EventLabel' + i, [xx + 2.35, yy, 3.05, hh], v.label, 'heading', `events[${i}].label`)
        tx('EventBody' + i, [xx + 5.65, yy, 3.8, hh], v.body, 'body', `events[${i}].body`)
        tx('EventGate' + i, [xx + 9.75, yy, ww - 9.75, hh], v.gate, 'small', `events[${i}].gate`, {
          bold: true,
          color: 'navy',
        })
      } else {
        owned(
          'EventDate' + i,
          [cx - 0.6, y, 1.2, 0.4],
          `${number(v.at)} ${d.unit}`,
          'pale',
          [`events[${i}].elapsed`, 'unit'],
          'small',
          'rectangle',
          'navy',
        )
        tx('EventLabel' + i, [xx, y + 1.13, ww, 0.75], v.label, 'heading', `events[${i}].label`)
        tx('EventBody' + i, [xx, y + 2.01, ww, h - 2.7], v.body, 'body', `events[${i}].body`)
        tx('EventGate' + i, [xx, y + h - 0.57, ww, 0.55], v.gate, 'small', `events[${i}].gate`, {
          bold: true,
          color: 'navy',
        })
      }
    })
  } else throw Error('Unregistered research role')
  if (role !== 'cover') {
    box('SynthesisStrip', b.chrome.strip, 'surface')
    tx('SynthesisLabel', b.chrome.stripLabel, d.synthesisLabel, 'small', 'synthesisLabel', {
      color: 'accentText',
      bold: true,
    })
    tx('Synthesis', b.chrome.verdict, d.verdict, 'small', 'verdict', { bold: true, color: 'navy' })
  }
  line('FooterRule', 0.6, 6.79, 12.13)
  tx(
    'Source',
    role === 'cover'
      ? [b.chrome.source[0], b.chrome.source[1], 8.5, b.chrome.source[3]]
      : b.chrome.source,
    d.source,
    'small',
    'source',
  )
  return cs
}

export function resolveResearchDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    (content.meta.designScope ?? 'complete') === 'complete' &&
    (content.slides[0]?.type !== 'researchCoverSlide' ||
      content.slides.at(-1)?.type !== 'researchImplicationsSlide')
  )
    throw Error(
      'Complete Blue Research decks require cover and reader implications; use excerpt scope for extracts',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.research.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps || slide.imageSlots)
      throw Error('Only registered research content is accepted; customOps/image slots unavailable')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileResearchLayout(
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
                design.research.chrome.page,
                design.research.styles.small,
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
        design.research.rhythm.maxConsecutive,
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

// Research-specific cover, acceptance staircase and closing evidence grammar.
// Execution, fit checks and content bindings remain owned by the shared planner.
export function compileResearchSignature({
  role,
  b,
  r,
  id,
  d,
  tx,
  box,
  line,
  cells,
  owned,
  table,
  cs,
}) {
  if (role === 'cover') {
    box('CoverTopRule', [0, 0, 13.333, 0.06], 'accent')
    const masthead = tx('Masthead', [0.78, 0.46, 9.5, 0.3], d.masthead, 'small', 'masthead', {
      color: 'navy',
      bold: false,
    })
    masthead.trackingPt = 1.1
    tx('ReportDate', [10.35, 0.4, 2.38, 0.3], d.period, 'small', 'period', { alignment: 'right' })
    line('MastheadRule', 0.78, 0.88, 11.77)
    tx(
      'CoverEyebrow',
      [r.hero[0], r.hero[1] - 0.34, r.hero[2], 0.3],
      d.eyebrow,
      'small',
      'eyebrow',
      { color: 'accentText', bold: true },
    )
    line('CoverSpine', r.hero[0] - 0.3, r.hero[1] - 0.3, r.hero[3] + 0.23, 'accent', true)
    cs.at(-1).linePt = 2
    tx('CoverTitle', r.hero, d.title, 'hero', 'title')
    tx('CoverEdition', r.edition, d.edition, 'edition', 'edition', { alignment: 'right' })
    tx(
      'EditionLabel',
      [r.edition[0], r.edition[1] + r.edition[3] + 0.1, r.edition[2], 0.35],
      d.editionLabel,
      'small',
      'editionLabel',
      { alignment: 'right', color: 'navy', bold: true },
    )
    tx('CoverAbstract', r.abstract, d.subtitle, 'body', 'subtitle')
    tx('CoverDisclosure', [9.7, 6.85, 3.03, 0.25], d.disclosure, 'small', 'disclosure', {
      alignment: 'right',
    })
    return
  }
  if (role === 'scorecard') {
    cells(r.goals, d.goals.length, false, 0.3).forEach(([x, y, w, h], i) => {
      if (i) line('GoalSeparator' + i, x - 0.16, y + 0.08, 0.18, 'rule', true)
      tx('GoalLabel' + i, [x, y, w, 0.28], d.goals[i].label, 'small', `goals[${i}].label`)
      const text = `${d.goals[i].baseline} → ${d.goals[i].target} ${d.goals[i].unit}`
      tx('GoalValue' + i, [x, y + 0.38, w, h - 0.38], text, 'figure', [
        `goals[${i}].baseline`,
        `goals[${i}].target`,
        `goals[${i}].unit`,
      ])
    })
    const [x, y, w, h] = r.steps,
      a = r.acceptance
    if (id === 'steps') {
      const end = a[0] + a[2] - 0.07,
        axisY = y - 0.22
      cs.push({
        kind: 'path',
        name: 'AcceptanceAxis',
        frame: [x + 0.2, axisY - 0.08, end - x - 0.2, 0.16],
        line: 'muted',
        linePt: 1,
        path: {
          width: 100000,
          height: 100000,
          commands: [
            { type: 'move', x: 0, y: 50000 },
            { type: 'line', x: 100000, y: 50000 },
            { type: 'move', x: 98800, y: 0 },
            { type: 'line', x: 100000, y: 50000 },
            { type: 'line', x: 98800, y: 100000 },
          ],
        },
      })
      line('AcceptanceMarker', end, axisY - 0.18, y + h - axisY + 0.18, 'accent', true)
      cs.at(-1).linePt = 1.5
      const weights = [0.9, 1, 1.1],
        sum = weights.reduce((a, v) => a + v, 0),
        space = 0.18,
        usable = w - space * 2
      let xx = x
      d.steps.forEach((v, i) => {
        const ww = (usable * weights[i]) / sum,
          top = y + 0.85 - i * 0.4,
          bottom = y + h,
          tone = ['accent', 'deep', 'navy'][i]
        line('StageDependency' + i, xx + ww, axisY, top - axisY, 'muted', true)
        line('StepTop' + i, xx, top, ww, tone)
        cs.at(-1).linePt = 2
        line('StepLeft' + i, xx, top, bottom - top, 'navy', true)
        line('StepRight' + i, xx + ww, top, bottom - top, 'navy', true)
        owned(
          'StepNumber' + i,
          [xx + 0.15, top - 0.17, 0.34, 0.34],
          String(i + 1),
          'deep',
          'structural.number',
        )
        const strings = [v.heading, v.owner, ...v.actions, v.gate],
          paths = [
            `steps[${i}].heading`,
            `steps[${i}].owner`,
            ...v.actions.map((_, j) => `steps[${i}].actions[${j}]`),
            `steps[${i}].gate`,
          ]
        const c = tx(
          'StepContent' + i,
          [xx + 0.18, top + 0.25, ww - 0.36, bottom - top - 0.32],
          strings.join('\n'),
          'body',
          paths,
        )
        Object.assign(c, {
          kind: 'owned',
          shapeKind: 'rectangle',
          color: 'paper',
          anchor: 'top',
          paragraphStyles: strings.map((_, j) =>
            j === 0
              ? b.styles.heading
              : j === 1 || j === strings.length - 1
                ? { ...b.styles.small, color: 'navy', bold: true }
                : b.styles.body,
          ),
        })
        xx += ww + space
      })
      line('SharedBaseline', x, y + h, w, 'navy')
      cs.at(-1).linePt = 1.1
    } else {
      cells(r.steps, d.steps.length, true, 0.15).forEach(([xx, yy, ww, hh], i) => {
        const v = d.steps[i]
        line('RegisterRule' + i, xx, yy, ww, 'accent')
        owned(
          'StepNumber' + i,
          [xx, yy + 0.14, 0.34, 0.34],
          String(i + 1),
          'deep',
          'structural.number',
        )
        tx(
          'StepHeading' + i,
          [xx + 0.55, yy + 0.1, 2.25, hh - 0.1],
          v.heading,
          'heading',
          `steps[${i}].heading`,
        )
        tx(
          'StepOwner' + i,
          [xx + 2.95, yy + 0.1, 1.7, hh - 0.1],
          v.owner,
          'small',
          `steps[${i}].owner`,
          { bold: true, color: 'navy' },
        )
        tx(
          'StepActions' + i,
          [xx + 4.9, yy + 0.1, ww - 4.9, hh - 0.1],
          `${v.actions.join('\n')}\n${v.gate}`,
          'small',
          [...v.actions.map((_, j) => `steps[${i}].actions[${j}]`), `steps[${i}].gate`],
        )
      })
    }
    const acceptance = tx(
      'AcceptanceContent',
      [a[0], a[1] + 0.35, a[2] - 0.22, a[3] - 0.4],
      `${d.acceptanceLabel}\n${d.acceptancePeriod}\n${d.acceptanceGate}`,
      'small',
      ['acceptanceLabel', 'acceptancePeriod', 'acceptanceGate'],
      { color: 'navy' },
    )
    Object.assign(acceptance, {
      kind: 'owned',
      shapeKind: 'rectangle',
      color: 'paper',
      anchor: 'top',
      paragraphGapPt: 10,
      paragraphStyles: [
        { ...b.styles.small, color: 'navy', bold: true },
        { ...b.styles.small, color: 'accentText', bold: true },
        { ...b.styles.small, color: 'navy' },
      ],
    })
    return
  }
  if (role === 'findings') {
    box('FindingsField', r.items, 'surface')
    const f = [r.items[0] + 0.22, r.items[1] + 0.17, r.items[2] - 0.44, r.items[3] - 0.34]
    const row = (v, i, [x, y, w]) => {
      const compact = id === 'register',
        split = compact ? 0.34 : 0.39,
        subY = compact ? 0.55 : 0.67
      if (i) line('FindingDivider' + i, x, y - (compact ? 0.005 : 0.08), w, 'rule', false, true)
      owned(
        'FindingNumber' + i,
        [x, y + 0.04, 0.36, 0.36],
        String(i + 1),
        'deep',
        'structural.number',
      )
      tx(
        'FindingHeading' + i,
        [x + 0.58, y, w * split - 0.58, compact ? 0.34 : 0.58],
        v.heading,
        'heading',
        `items[${i}].heading`,
      )
      const emphasisWidth = Math.min(
        w * split - 0.58,
        Math.max(1.3, ((textUnits(v.emphasis) * b.styles.small.sizePt) / 72) * 1.14 + 0.18),
      )
      const emphasis = owned(
        'FindingEmphasis' + i,
        [x + 0.58, y + subY, emphasisWidth, 0.25],
        v.emphasis,
        'highlight',
        `items[${i}].emphasis`,
        'small',
        'rectangle',
        'ink',
      )
      emphasis.allocatedFrame = [x + 0.58, y + subY, w * split - 0.58, 0.25]
      tx(
        'FindingBody' + i,
        [x + w * (split + 0.04), y, w * (0.96 - split), 0.54],
        v.body,
        'body',
        `items[${i}].body`,
      )
      tx(
        'FindingEvidence' + i,
        [x + w * (split + 0.04), y + subY, w * (0.96 - split), 0.28],
        v.evidence,
        'small',
        `items[${i}].evidence`,
        { color: 'navy', bold: true },
      )
    }
    if (id === 'register')
      cells(f, d.items.length, true, 0.02).forEach((frame, i) => row(d.items[i], i, frame))
    else {
      const lead = d.items[0],
        left = [f[0], f[1], 3.05, f[3]],
        right = [f[0] + 3.4, f[1], f[2] - 3.4, f[3]]
      owned('FindingNumber0', [left[0], left[1], 0.42, 0.42], '1', 'deep', 'structural.number')
      tx(
        'FindingHeading0',
        [left[0], left[1] + 0.65, left[2], 1.05],
        lead.heading,
        'figure',
        'items[0].heading',
      )
      tx(
        'FindingBody0',
        [left[0], left[1] + 1.88, left[2], 0.9],
        lead.body,
        'body',
        'items[0].body',
      )
      owned(
        'FindingEmphasis0',
        [left[0], left[1] + 2.97, left[2], 0.28],
        lead.emphasis,
        'highlight',
        'items[0].emphasis',
        'small',
        'rectangle',
        'ink',
      )
      tx(
        'FindingEvidence0',
        [left[0], left[1] + 3.38, left[2], 0.28],
        lead.evidence,
        'small',
        'items[0].evidence',
        { color: 'navy', bold: true },
      )
      line('LeadFindingRule', left[0] + left[2] + 0.17, left[1], left[3], 'rule', true)
      cells(right, d.items.length - 1, true, 0.18).forEach((frame, i) =>
        row(d.items[i + 1], i + 1, frame),
      )
    }
    return
  }
  if (role === 'implications') {
    const rows = d.readers.map((v) => [
      v.reader,
      v.meaning,
      `${v.action} · ${v.owner}`,
      `${v.indicator} · ${v.timing}`,
    ])
    const cols = d.headers.map((label, i) => ({
      label,
      weight: [1.5, 2.9, 3.4, 2.7][i],
      align: 'left',
    }))
    const paths = (i, j) =>
      i
        ? j === 2
          ? [`readers[${i - 1}].action`, `readers[${i - 1}].owner`]
          : j === 3
            ? [`readers[${i - 1}].indicator`, `readers[${i - 1}].timing`]
            : `readers[${i - 1}].${['reader', 'meaning'][j]}`
        : `headers[${j}]`
    if (id === 'matrix') table('ReaderActionMatrix', r.items, cols, rows, paths)
    else
      cells(r.items, d.readers.length, true, 0.2).forEach(([x, y, w, h], i) => {
        line('ReaderRule' + i, x, y, w, 'accent')
        owned(
          'ReaderNumber' + i,
          [x, y + 0.16, 0.34, 0.34],
          String(i + 1),
          'deep',
          'structural.number',
        )
        tx(
          'ReaderHeading' + i,
          [x + 0.55, y + 0.13, 2.15, h - 0.13],
          d.readers[i].reader,
          'heading',
          `readers[${i}].reader`,
        )
        tx(
          'ReaderMeaning' + i,
          [x + 2.95, y + 0.13, 3.1, h - 0.13],
          d.readers[i].meaning,
          'body',
          `readers[${i}].meaning`,
        )
        tx(
          'ReaderAction' + i,
          [x + 6.4, y + 0.13, 3.15, h - 0.13],
          rows[i][2],
          'small',
          [`readers[${i}].action`, `readers[${i}].owner`],
          { bold: true, color: 'navy' },
        )
        tx(
          'ReaderCheck' + i,
          [x + 9.9, y + 0.13, w - 9.9, h - 0.13],
          rows[i][3],
          'small',
          [`readers[${i}].indicator`, `readers[${i}].timing`],
          { color: 'navy' },
        )
      })
    tx('DependencyLabel', r.dependencyLabel, d.dependencyLabel, 'small', 'dependencyLabel', {
      bold: true,
      color: 'accentText',
    })
    cells(r.dependencies, d.dependencies.length, false, 0.35).forEach(([x, y, w, h], i) => {
      tx(
        'Dependency' + i,
        [x, y, w, h],
        `${i + 1} ${d.dependencies[i]}`,
        'small',
        `dependencies[${i}]`,
        { color: 'navy', bold: true },
      )
      if (i < d.dependencies.length - 1)
        cs.push({
          kind: 'path',
          name: 'DependencyArrow' + i,
          frame: [x + w + 0.05, y + 0.05, 0.2, 0.12],
          line: 'muted',
          linePt: 1,
          path: {
            width: 100000,
            height: 100000,
            commands: [
              { type: 'move', x: 0, y: 50000 },
              { type: 'line', x: 100000, y: 50000 },
              { type: 'move', x: 60000, y: 0 },
              { type: 'line', x: 100000, y: 50000 },
              { type: 'line', x: 60000, y: 100000 },
            ],
          },
        })
    })
    line('AcceptanceRule', r.shared[0], r.shared[1] - 0.12, r.shared[2], 'accent')
    tx(
      'SharedAcceptance',
      r.shared,
      `${d.acceptanceLabel}: ${d.acceptance}`,
      'small',
      ['acceptanceLabel', 'acceptance'],
      { bold: true, color: 'navy' },
    )
  }
}
