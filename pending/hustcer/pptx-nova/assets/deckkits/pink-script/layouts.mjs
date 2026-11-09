import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'
export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite numeric evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(9)).toString()
}
export function compilePinkLayout(design, family, id, variant, d, path = 'data') {
  const b = design.pink,
    r = variant.regions,
    cs = []
  const tx = (name, frame, value, key = 'body', fields = name, extra = {}) => {
    // The five-column metric band permits two-line labels. Make those breaks
    // explicit so native layout and the single-line label gate agree.
    if (family.role === 'stats' && id === 'band' && key === 'label') {
      const style = { ...b.styles[key], ...extra }
      const cap = ((frame[2] - 0.04) * 72) / (style.sizePt * 0.6 + 0.8)
      value = value
        .split('\n')
        .flatMap((line) => {
          const lines = []
          let current = ''
          for (const word of line.split(/\s+/u)) {
            if (current && current.length + word.length + 1 > cap) {
              lines.push(current)
              current = ''
            }
            current += (current ? ' ' : '') + word
          }
          return [...lines, current]
        })
        .join('\n')
    }
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) =>
      k.startsWith('structural.') ? k : `${path}.${k}`,
    )
    const c = {
      ...fitTextPlan(value, frame, { ...b.styles[key], ...extra }, paths[0]),
      name,
      paths,
    }
    cs.push(c)
    return c
  }
  const box = (name, frame, color, kind = 'box') => cs.push({ kind, name, frame, color })
  const rule = (name, x, y, w, color = 'rule', vertical = false) =>
    box(name, vertical ? [x, y, 0.008, w] : [x, y, w, 0.008], color)
  const cells = (f, n, vertical = false, g = b.spacing.gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const pathShape = (name, frame, commands, { line = 'accent', fill, linePt = 0.65, dash } = {}) =>
    cs.push({
      kind: 'path',
      name,
      frame,
      path: { width: 100000, height: 100000, commands },
      line,
      fill,
      linePt,
      dash,
    })
  const arrow = (name, x, y, w) =>
    pathShape(
      name,
      [x, y, w, 0.15],
      [
        { type: 'move', x: 0, y: 50000 },
        { type: 'line', x: 100000, y: 50000 },
        { type: 'move', x: 65000, y: 0 },
        { type: 'line', x: 100000, y: 50000 },
        { type: 'line', x: 65000, y: 100000 },
      ],
      { linePt: 1 },
    )
  const owned = (name, frame, value, color, fields, key = 'label', extra = {}) => {
    const inset = 0.1,
      c = tx(
        name,
        [frame[0] + inset, frame[1] + 0.04, frame[2] - 2 * inset, frame[3] - 0.08],
        value,
        key,
        fields,
        extra,
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
  // The frame and sparse editable grain are structure, not business content.
  for (let i = 0; i < 24; i++) {
    const x = 0.31 + (((i * 47) % 97) / 97) * 12.7,
      y = 0.31 + (((i * 29) % 83) / 83) * 6.85
    box('Grain' + i, [x, y, 0.012, 0.005], 'grain')
  }
  tx('Brand', b.chrome.brand, d.brand, 'kicker', 'brand')
  tx('Section', b.chrome.section, d.section, 'small', 'section', { alignment: 'right' })
  tx(
    'Kicker',
    b.chrome.kicker,
    d.kicker,
    'kicker',
    'kicker',
    family.role === 'cover' ? { alignment: 'center' } : {},
  )
  if (family.role === 'cover') {
    tx('CoverTitle', r.hero, d.title, 'hero', 'title', { alignment: 'center', glow: true })
    tx('CoverContinuation', r.continuation, d.continuation, 'continuation', 'continuation', {
      alignment: 'center',
    })
    cells(r.metadata, d.metadata.length, false, 0.4).forEach(([x, y, w, h], i) => {
      tx('MetadataLabel' + i, [x, y, w, 0.25], d.metadata[i].label, 'small', `metadata[${i}].label`)
      tx(
        'MetadataValue' + i,
        [x, y + 0.3, w, h - 0.3],
        d.metadata[i].value,
        'subhead',
        `metadata[${i}].value`,
        { color: i % 3 === 0 ? 'accent' : 'ink' },
      )
    })
  } else if (family.role === 'index') {
    tx('IndexTitle', r.hero, d.title, id === 'rail' ? 'indexHero' : 'title', 'title')
    tx('IndexContinuation', r.continuation, d.continuation, 'number', 'continuation', {
      color: 'ink',
    })
    cells(r.items, d.items.length, true, 0.05).forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        nw = 0.65,
        mw = id === 'rail' ? 1.4 : 1.6,
        g = 0.18,
        tw = w - nw - mw - g * 2
      tx(
        'IndexNumber' + i,
        [x, y + 0.04, nw, 0.65],
        String(i + 1).padStart(2, '0'),
        'number',
        'structural.index',
      )
      tx(
        'IndexHeading' + i,
        [x + nw + g, y + 0.02, tw, 0.47],
        v.title,
        'subhead',
        `items[${i}].title`,
        { color: v.focus ? 'accent' : 'ink' },
      )
      tx(
        'IndexDescription' + i,
        [x + nw + g, y + 0.5, tw, h - 0.54],
        v.description,
        'muted',
        `items[${i}].description`,
      )
      tx('IndexMeta' + i, [x + w - mw, y + 0.15, mw, 0.55], v.meta, 'small', `items[${i}].meta`, {
        alignment: 'right',
      })
      rule('IndexRule' + i, x, y + h, w, 'hair')
    })
  } else if (family.role === 'stats') {
    tx('Title', r.title, d.title, id === 'rail' ? 'title' : 'quote', 'title')
    tx('Intro', r.intro, d.intro, 'muted', 'intro')
    cells(r.stats, d.stats.length, id === 'rail', id === 'rail' ? 0.08 : 0.28).forEach(
      ([x, y, w, h], i) => {
        const v = d.stats[i],
          vertical = id === 'rail',
          vw = vertical ? w * 0.34 : w
        const uw = (textUnits(v.unit) * 15) / 72 + 0.13,
          vf = [x, y, vw, 0.85]
        fitTextPlan(
          v.unit,
          [x + vw - uw, y + 0.3, uw, 0.4],
          { ...b.styles.body, sizePt: 15 },
          `${path}.stats[${i}].unit`,
        )
        const c = tx('StatValue' + i, [x, y, vw - uw, 0.85], number(v.value), 'metric', [
          `stats[${i}].value`,
          `stats[${i}].unit`,
        ])
        c.frame = vf
        c.allocatedFrame = vf
        c.text += ' ' + v.unit
        c.unit = v.unit
        const lx = vertical ? x + vw + 0.18 : x,
          ly = vertical ? y : y + 0.96,
          lw = vertical ? w - vw - 0.18 : w
        tx(
          'StatLabel' + i,
          [lx, ly + 0.02, lw, vertical ? 0.3 : 0.5],
          v.label,
          'label',
          `stats[${i}].label`,
        )
        tx(
          'StatDescription' + i,
          [lx, ly + (vertical ? 0.37 : 0.6), lw, vertical ? h - 0.39 : h - 1.56],
          v.description,
          'muted',
          `stats[${i}].description`,
        )
        if (i < d.stats.length - 1 || !vertical)
          rule('StatRule' + i, x, vertical ? y + h : y - 0.1, w, 'hair')
      },
    )
  } else if (family.role === 'section') {
    tx('ChapterNumber', r.number, d.number, 'giant', 'number', { glow: true })
    const [x, y, w, h] = r.story
    tx('Title', [x, y, w, 2.5], d.title, 'quote', 'title')
    tx('Intro', [x, y + 2.75, w, h - 2.75], d.intro, 'muted', 'intro')
    tx('SideLabel', [1.05, 6.35, 7.1, 0.3], d.sideLabel, 'small', 'sideLabel')
  } else if (family.role === 'trend') {
    if (d.series.length !== 2 || d.series.some((s) => s.values.length !== d.categories.length))
      throw Error('Trend requires two complete named series')
    if (!Number.isInteger(d.focusIndex) || d.focusIndex < 0 || d.focusIndex >= d.categories.length)
      throw Error('focusIndex outside categories')
    tx('Title', r.title, d.title, 'quote', 'title')
    const [lx, ly, lw] = r.legend
    d.series.forEach((v, i) => {
      rule('LegendLine' + i, lx, ly + i * 0.42 + 0.13, 0.3, i ? 'muted' : 'accent')
      tx(
        'LegendLabel' + i,
        [lx + 0.43, ly + i * 0.42, lw - 0.43, 0.3],
        v.name,
        'small',
        `series[${i}].name`,
        { color: i ? 'muted' : 'ink' },
      )
    })
    const values = d.series.flatMap((s) => s.values),
      lo = Math.min(0, ...values),
      hi = Math.max(0, ...values),
      span = hi - lo || 1
    const rawStep = span / 4,
      power = 10 ** Math.floor(Math.log10(rawStep)),
      unit = [1, 2, 5, 10].find((n) => n * power >= rawStep) * power,
      minimum = Math.floor(lo / unit) * unit,
      maximum = Math.ceil((hi || unit) / unit) * unit
    cs.push({
      kind: 'chart',
      name: 'Trend',
      frame: r.plot,
      chartKind: 'line',
      data: { categories: d.categories, series: d.series },
      minimum,
      maximum,
      focusPoint: d.focusIndex,
      showValues: false,
      numberFormat: values.some((v) => v && Math.abs(v) < 0.001)
        ? '0.00E+00'
        : values.every(Number.isInteger)
          ? '0'
          : '0.00',
      seriesTone: 'accent',
      inputPaths: ['categories[]', 'series[].name', 'series[].values[]'],
    })
    tx(
      'ChartUnit',
      [r.plot[0] + 0.3, r.plot[1] - 0.25, r.plot[2] - 0.3, 0.25],
      d.unit,
      'small',
      'unit',
    )
    const [x, y, w, h] = r.callout
    if (id === 'rail') {
      rule('CalloutRail', x - 0.18, y, h, 'accent', true)
      tx('CalloutValue', [x, y, w, 0.9], d.callout.value, 'metric', 'callout.value')
      tx('CalloutLabel', [x, y + 1.05, w, 0.6], d.callout.label, 'label', 'callout.label')
      tx(
        'CalloutDescription',
        [x, y + 1.8, w, h - 1.8],
        d.callout.description,
        'muted',
        'callout.description',
      )
    } else {
      rule('CalloutRail', x, y - 0.12, w, 'accent')
      tx('CalloutValue', [x, y, 2.5, h], d.callout.value, 'number', 'callout.value')
      tx('CalloutLabel', [x + 2.85, y, 3.25, h], d.callout.label, 'label', 'callout.label')
      tx(
        'CalloutDescription',
        [x + 6.5, y, w - 6.5, h],
        d.callout.description,
        'muted',
        'callout.description',
      )
    }
  } else if (family.role === 'process') {
    tx('Title', r.title, d.title, 'title', 'title')
    tx('Intro', r.intro, d.intro, 'muted', 'intro')
    cells(r.steps, d.steps.length, id === 'rows', id === 'rows' ? 0.1 : 0.28).forEach(
      ([x, y, w, h], i) => {
        const v = d.steps[i],
          rows = id === 'rows'
        rule('StepRule' + i, x, y, w, 'accent')
        tx(
          'StepNumber' + i,
          [x, y + 0.12, rows ? 0.65 : w, rows ? 0.65 : 0.7],
          String(i + 1).padStart(2, '0'),
          'number',
          'structural.step',
        )
        tx(
          'StepTitle' + i,
          [rows ? x + 0.9 : x, y + (rows ? 0.14 : 0.95), rows ? 2 : w, 0.5],
          v.title,
          'subhead',
          `steps[${i}].title`,
        )
        tx(
          'StepDescription' + i,
          [
            rows ? x + 3.1 : x,
            y + (rows ? 0.13 : 1.57),
            rows ? w - 3.1 : w,
            rows ? h - 0.15 : h - 1.68,
          ],
          v.description,
          'muted',
          `steps[${i}].description`,
        )
        if (i < d.steps.length - 1 && !rows) arrow('StepArrow' + i, x + w + 0.06, y + 0.43, 0.15)
      },
    )
    rule('TimelineRule', r.timeline[0], r.timeline[1] - 0.12, r.timeline[2], 'hair')
    tx('Timeline', r.timeline, d.timeline, 'small', 'timeline')
  } else if (family.role === 'matrix') {
    tx('Title', r.title, d.title, id === 'full' ? 'quote' : 'heading', 'title')
    const f = r.table,
      n = d.columns.length,
      rows = [d.columns.map((c) => c.label), ...d.rows]
    if (d.rows.some((row) => row.length !== n))
      throw Error('Every table row must match all columns')
    if (!Number.isInteger(d.focusColumn) || d.focusColumn < 0 || d.focusColumn >= n)
      throw Error('focusColumn outside columns')
    const total = d.columns.reduce((a, c) => a + c.weight, 0)
    if (!(total > 0) || d.columns.some((c) => !(c.weight > 0)))
      throw Error('Positive column weights required')
    const widths = d.columns.map((c) => (f[2] * c.weight) / total),
      rh = f[3] / rows.length,
      bindings = [],
      statusKeys = new Set()
    for (const v of d.statuses ?? []) {
      if (
        !Number.isInteger(v.row) ||
        v.row < 0 ||
        v.row >= d.rows.length ||
        !Number.isInteger(v.column) ||
        v.column < 0 ||
        v.column >= n
      )
        throw Error('Status cell outside table')
      const key = `${v.row}:${v.column}`
      if (statusKeys.has(key)) throw Error('Duplicate status cell')
      statusKeys.add(key)
    }
    rows.forEach((row, i) => {
      let x = f[0]
      row.forEach((value, j) => {
        if (/[\r\n]/u.test(value)) throw Error('Native table cells require one paragraph')
        const st = {
            ...b.styles[i === 0 ? 'label' : j === 0 ? 'subhead' : 'table'],
            sizePt: i === 0 ? 10.5 : j === 0 ? 16 : 12,
          },
          frame = [x + 0.09, f[1] + i * rh + 0.06, widths[j] - 0.18, rh - 0.12],
          p = i ? `rows[${i - 1}][${j}]` : `columns[${j}].label`
        fitTextPlan(value, frame, st, `${path}.${p}`)
        bindings.push({ paths: [`${path}.${p}`], frame, style: st })
        x += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name: 'Matrix',
      frame: f,
      cells: rows,
      columns: d.columns,
      widths,
      rowHeights: rows.map(() => rh),
      focusColumn: d.focusColumn,
      focusTone: 'wash',
      bindings,
      useBindingStyles: true,
      blueRules: true,
      statuses: d.statuses ?? [],
    })
    tx('MatrixNote', r.note, d.note, 'small', 'note')
  } else if (family.role === 'quote') {
    tx('QuoteMark', r.mark, '“', 'hero', 'structural.quote')
    tx('Quotation', r.quote, d.quote, 'quote', 'quote')
    const [x, y, w, h] = r.attribution
    rule('AttributionRule', x, y - 0.16, w, 'accent')
    tx('Author', [x, y, w, 0.43], d.author, 'subhead', 'author')
    tx('AuthorRole', [x, y + 0.48, w, h - 0.48], d.role, 'kicker', 'role')
  } else if (family.role === 'closing') {
    tx('Title', r.title, d.title, id === 'invitation' ? 'title' : 'quote', 'title')
    cells(r.actions, d.actions.length, id === 'sidecar', 0.28).forEach(([x, y, w, h], i) => {
      const v = d.actions[i],
        vertical = id === 'sidecar'
      rule('ActionRule' + i, x, y, w, 'accent')
      tx(
        'ActionNumber' + i,
        [x, y + 0.1, 0.85, 0.68],
        String(i + 1).padStart(2, '0'),
        'number',
        'structural.action',
      )
      const heading = owned(
        'ActionTitle' + i,
        [vertical ? x + 0.9 : x, y + (vertical ? 0.1 : 0.75), vertical ? w - 0.9 : w, 0.55],
        v.title,
        'paper',
        `actions[${i}].title`,
        'subhead',
      )
      heading.transparent = true
      tx(
        'ActionDescription' + i,
        [
          vertical ? x + 0.9 : x,
          y + (vertical ? 0.72 : 1.4),
          vertical ? w - 0.9 : w,
          h - (vertical ? 0.66 : 1.25),
        ],
        v.description,
        'muted',
        `actions[${i}].description`,
      )
    })
    const [x, y, w, h] = r.ticket
    const qrSize = Math.min(w, h)
    cs.push({
      kind: 'image',
      name: 'ContactQR',
      frame: [x + (w - qrSize) / 2, y + (h - qrSize) / 2, qrSize, qrSize],
      slotId: 'contact.qr',
    })
  } else throw Error('Unregistered pink editorial role')

  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolvePinkDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (
    content.meta.designScope !== 'excerpt' &&
    (content.slides[0]?.type !== 'pinkCoverSlide' ||
      content.slides.at(-1)?.type !== 'pinkClosingSlide')
  )
    throw Error('Complete decks require cover and closing; use designScope excerpt for extracts')
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.pink.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps) throw Error('Pink Script accepts registered content only')
    if (
      Object.keys(slide.imageSlots ?? {}).some(
        (k) => family.role !== 'closing' || k !== 'contact.qr',
      )
    )
      throw Error('Only closing contact.qr image slot is registered')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compilePinkLayout(
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
              design.pink.chrome.page,
              { ...design.pink.styles.small, color: 'accent', alignment: 'right' },
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
        design.pink.rhythm.maxConsecutive,
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
    if (chosen.repeated)
      warnings.push(`slides[${s}]: repeated composition requires editorial review`)
    layouts.push(chosen)
  }
  return { layouts, warnings }
}
