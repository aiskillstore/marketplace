// Swiss typographic components compiled from bounded contract regions.
import { readFileSync } from 'node:fs'
import { assertDesignValue, designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { hasTablerIcon } from '../shared/icon-assets.kit.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'

const schemas = new Map()
function inputSchema(type) {
  if (!schemas.has(type))
    schemas.set(
      type,
      JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url))),
    )
  return schemas.get(type)
}

export function fitText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = ((frame[2] - 0.04) * 72) / style.sizePt
  const text = wrapCjkText(value, capacity * 0.94)
  let lines = 0
  for (const line of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const word of line.split(/(\s+)/u)) {
      const units = [...word].reduce(
        (n, c) => n + (c.codePointAt(0) > 255 ? 1 : 0.54 + (/[MW@]/.test(c) ? 0.23 : 0)),
        0,
      )
      if (units > capacity) throw Error(`${path}: word exceeds width`)
      if (used && used + units > capacity) {
        lines++
        used = 0
      }
      used += units
    }
  }
  const requiredHeight = (lines * style.sizePt * 1.5) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines require ${requiredHeight.toFixed(2)}in; available ${frame[3].toFixed(2)}in`,
    )
  return {
    kind: 'text',
    text,
    frame: [...frame],
    style: { ...style },
    path,
    estimatedLines: lines,
    requiredHeight,
  }
}
export function compileSwissLayout(design, family, layoutId, variant, d, path = 'data') {
  const role = family.role,
    r = variant.regions,
    b = design.swiss,
    g = b.spacing,
    cs = []
  const tx = (name, f, v, key = 'body', field = name, extra = {}) => {
    if (v === undefined) return
    const c = fitText(v, f, { ...b.styles[key], ...extra }, `${path}.${field}`)
    c.name = name
    cs.push(c)
    return c
  }
  const panel = (name, f, color = 'panel', outline) =>
    cs.push({ kind: 'panel', name, frame: f, color, outline })
  const rule = (name, x, y, w, color = 'rule', vertical = false) =>
    cs.push({
      kind: 'rule',
      name,
      frame: vertical ? [x, y, 0.005, w] : [x, y, w, 0.005],
      color,
      vertical,
    })
  const dot = (name, x, y, r, color = 'red') =>
    cs.push({ kind: 'dot', name, frame: [x - r, y - r, r * 2, r * 2], color })
  const grid = (n, frame, cols = n) => {
    const rows = Math.ceil(n / cols),
      cw = (frame[2] - g.gap * (cols - 1)) / cols,
      ch = (frame[3] - g.gap * (rows - 1)) / rows
    return Array.from({ length: n }, (_, i) => [
      frame[0] + (i % cols) * (cw + g.gap),
      frame[1] + Math.floor(i / cols) * (ch + g.gap),
      cw,
      ch,
    ])
  }
  if (d.eyebrow) tx('Eyebrow', b.chrome.eyebrow, d.eyebrow, 'label', 'eyebrow')
  const head = () => {
    tx('Title', b.chrome.title, d.title, variant.titleStyle, 'title')
    tx('Subtitle', b.chrome.subtitle, d.subtitle, 'small', 'subtitle')
    const [x, y, w] = b.chrome.mark
    rule('HeadingMark', x, y, w, 'red')
  }
  const col = (item) => (item.focus ? 'red' : 'ink')
  const callout = () => {
    const [x, top, w, h] = r.callout
    rule('CalloutMark', x - 0.2, top, h, 'red', true)
    if (d.calloutTitle)
      tx('CalloutTitle', [x, top, w, 0.32], d.calloutTitle, 'denseTitle', 'calloutTitle')
    const offset = d.calloutTitle ? 0.37 : 0,
      c = tx('Callout', [x, top + offset, w, h - offset], d.callout, 'small', 'callout')
    if (d.calloutHighlights) c.highlights = [...d.calloutHighlights]
  }
  if (role === 'cover') {
    tx('Title', r.title, d.title, 'hero', 'title')
    tx('Subtitle', r.subtitle, d.subtitle, 'subhead', 'subtitle')
    rule('TagMark', r.tag[0] - 0.22, r.tag[1], r.tag[3] - 0.03, 'red', true)
    tx('Tag', r.tag, d.tag, 'small', 'tag')
    cs.push({ kind: 'dot', name: 'SignatureDot', frame: r.dot, color: 'red' })
    if (d.footer) tx('Footer', b.chrome.footer, d.footer, 'source', 'footer')
  } else if (role === 'quote') {
    if (r.mark)
      tx('QuoteMark', r.mark, '«', 'specimen', 'structural.quoteMark', {
        color: 'red',
      })
    tx('Quote', r.quote, d.quote, 'quote', 'quote')
    tx('Body', r.body, d.body, 'body', 'body')
    rule('AuthorRule', r.author[0], r.author[1] - 0.18, 0.62, 'ink')
    tx('Author', r.author, d.author, 'denseTitle', 'author')
    tx('Source', r.source, d.source, 'small', 'source')
  } else if (role === 'timeline' || role === 'progress') {
    head()
    const items = d.steps,
      process = role === 'progress',
      vertical = layoutId === 'vertical'
    if (vertical) {
      const [x, top, w, h] = r.items,
        pitch = h / items.length
      rule('Track', x + 1.1, top + 0.14, h - pitch + 0.02, 'ink', true)
      items.forEach((a, i) => {
        const y = top + i * pitch
        dot(`Node${i}`, x + 1.1, y + 0.14, 0.05, col(a))
        tx(`Year${i}`, [x, y, 0.9, 0.4], a.year, 'denseTitle', `steps[${i}].year`, {
          color: col(a),
        })
        tx(
          `EventTitle${i}`,
          [x + 1.35, y, 3.2, pitch - 0.1],
          a.title,
          'denseTitle',
          `steps[${i}].title`,
          { color: col(a) },
        )
        tx(
          `EventBody${i}`,
          [x + 4.85, y, w - 4.85, pitch - 0.1],
          a.body,
          'small',
          `steps[${i}].body`,
        )
      })
    } else {
      const area = r.items,
        frames = grid(items.length, area),
        lineY = area[1] + (process ? 1.52 : 0.77)
      rule('Track', area[0], lineY, area[2], 'ink')
      frames.forEach(([x, y, w], i) => {
        const a = items[i],
          center = x + w / 2
        if (process) {
          tx(
            `Index${i}`,
            [x, y, w, 0.78],
            String(i + 1).padStart(2, '0'),
            'index',
            `structural.index${i}`,
            { color: a.focus ? 'red' : 'secondary' },
          )
          tx(`Year${i}`, [x, 3.35, w, 0.35], a.year, 'small', `steps[${i}].year`, { color: 'red' })
          tx(`EventTitle${i}`, [x, 4.28, w, 0.6], a.title, 'denseTitle', `steps[${i}].title`, {
            color: col(a),
          })
          tx(`EventBody${i}`, [x, 4.96, w, 0.95], a.body, 'small', `steps[${i}].body`)
        } else {
          tx(`Year${i}`, [x, y, w, 0.6], a.year, 'year', `steps[${i}].year`, {
            color: col(a),
          })
          tx(`EventTitle${i}`, [x, 3.55, w, 0.66], a.title, 'denseTitle', `steps[${i}].title`, {
            color: col(a),
          })
          tx(`EventBody${i}`, [x, 4.35, w, 1.35], a.body, 'small', `steps[${i}].body`)
        }
        dot(`Node${i}`, center, lineY, a.focus ? 0.11 : 0.065, col(a))
      })
    }
    callout()
  } else if (['principles', 'people', 'columns', 'brands'].includes(role)) {
    head()
    const field = {
        principles: 'items',
        people: 'people',
        columns: 'items',
        brands: 'brands',
      }[role],
      items = d[field]
    const cols = role === 'brands' ? 3 : 4,
      frames = grid(items.length, r.items, Math.min(cols, items.length))
    frames.forEach(([x, y, w, h], i) => {
      const a = items[i],
        p = `${field}[${i}]`,
        color = col(a)
      if (role === 'principles') {
        tx(`Index${i}`, [x, y, w, 0.5], a.num, 'year', `${p}.num`, {
          color: a.focus ? 'red' : 'secondary',
        })
        rule(`Rule${i}`, x, y + 0.57, w, color)
        tx(`ItemTitle${i}`, [x, y + 0.68, w, 0.35], a.title, 'denseTitle', `${p}.title`, { color })
        tx(`ItemSubtitle${i}`, [x, y + 1.08, w, 0.47], a.subtitle, 'label', `${p}.subtitle`)
        tx(`ItemBody${i}`, [x, y + 1.61, w, 0.5], a.body, 'small', `${p}.body`)
      } else if (role === 'people') {
        tx(
          `Index${i}`,
          [x, y, w, 0.25],
          String(i + 1).padStart(2, '0'),
          'label',
          `structural.index${i}`,
          { color: 'red' },
        )
        tx(`PersonName${i}`, [x, y + 0.31, w, 0.34], a.name, 'denseTitle', `${p}.name`, { color })
        tx(`Years${i}`, [x, y + 0.7, w, 0.26], a.years, 'label', `${p}.years`)
        rule(`Rule${i}`, x, y + 1.04, 0.62, color)
        tx(`PersonBody${i}`, [x, y + 1.16, w, 0.95], a.body, 'small', `${p}.body`)
      } else if (role === 'columns') {
        tx(
          `Index${i}`,
          [x, y, w, 0.3],
          String(i + 1).padStart(2, '0'),
          'label',
          `structural.index${i}`,
          { color: 'red' },
        )
        rule(`Rule${i}`, x, y + 0.4, w, color)
        tx(`ItemTitle${i}`, [x, y + 0.6, w, 0.65], a.title, 'itemTitle', `${p}.title`, { color })
        tx(`ItemSubtitle${i}`, [x, y + 1.3, w, 0.55], a.subtitle, 'label', `${p}.subtitle`)
        tx(`ItemBody${i}`, [x, y + 1.98, w, 0.85], a.body, 'small', `${p}.body`)
        tx(`Examples${i}`, [x, y + 2.95, w, 0.95], a.examples, 'small', `${p}.examples`, {
          color: 'secondary',
        })
        if (a.note) tx(`Note${i}`, [x, y + h - 0.35, w, 0.35], a.note, 'source', `${p}.note`)
      } else {
        rule(`Rule${i}`, x, y, w, color)
        if (a.icon)
          cs.push({
            kind: 'icon',
            name: `Icon${i}`,
            frame: [x, y + 0.26, 0.48, 0.48],
            icon: a.icon,
            color,
            path: `${path}.${p}.icon`,
          })
        const offset = a.icon ? 0.67 : 0
        tx(
          `BrandName${i}`,
          [x + offset, y + 0.23, w - offset, 0.44],
          a.name,
          'itemTitle',
          `${p}.name`,
          { color },
        )
        tx(`BrandMeta${i}`, [x + offset, y + 0.72, w - offset, 0.4], a.meta, 'label', `${p}.meta`)
        tx(`BrandBody${i}`, [x, y + 1.22, w, h - 1.22], a.body, 'small', `${p}.body`)
      }
    })
  } else if (role === 'profile') {
    head()
    const [px, py, pw] = r.identity,
      [ex, top, ew, eh] = r.events
    tx('Monogram', [px, py, pw, 1.55], d.initials, 'monogram', 'initials')
    tx('Name', [px, py + 1.65, pw, 0.55], d.name, 'label', 'name')
    rule('BioRule', px, py + 2.29, pw, 'ink')
    tx('Bio', [px, py + 2.49, pw, 0.95], d.bio, 'small', 'bio')
    tx('Meta', [px, py + 3.6, pw, 0.75], d.meta, 'small', 'meta', {
      color: 'secondary',
    })
    const pitch = eh / d.events.length
    rule('Track', ex + 0.86, top + 0.12, eh - pitch + 0.02, 'ink', true)
    d.events.forEach((a, i) => {
      const y = top + i * pitch
      dot(`Node${i}`, ex + 0.86, y + 0.12, a.focus ? 0.065 : 0.045, col(a))
      tx(`Year${i}`, [ex, y, 0.72, 0.3], a.year, 'label', `events[${i}].year`, {
        bold: true,
        color: col(a),
      })
      tx(
        `EventTitle${i}`,
        [ex + 1.1, y, ew - 1.1, 0.3],
        a.title,
        'denseTitle',
        `events[${i}].title`,
        { color: col(a) },
      )
      tx(
        `EventBody${i}`,
        [ex + 1.1, y + 0.31, ew - 1.1, pitch - 0.34],
        a.body,
        'small',
        `events[${i}].body`,
      )
    })
  } else if (role === 'typeface') {
    head()
    const frames = grid(d.cards.length, r.items)
    frames.forEach(([x, y, w], i) => {
      const a = d.cards[i],
        p = `cards[${i}]`,
        color = col(a)
      rule(`TopRule${i}`, x, y, w, color)
      tx(`FaceName${i}`, [x, y + 0.12, w, 0.36], a.name, 'itemTitle', `${p}.name`, { color })
      tx(`FaceMeta${i}`, [x, y + 0.55, w, 0.28], a.meta, 'label', `${p}.meta`)
      tx(
        `Specimen${i}`,
        [x, y + 0.92, w, 1.82],
        a.sampleText ?? d.sampleText,
        'specimen',
        a.sampleText ? `${p}.sampleText` : 'sampleText',
        {
          role: a.specimenStyle === 'heavy' ? 'heavy' : 'body',
          bold: a.specimenStyle === 'bold',
          color,
        },
      )
      tx(`Weight${i}`, [x, y + 2.8, w, 0.28], a.weight, 'label', `${p}.weight`)
      rule(`SampleRule${i}`, x, y + 3.17, 0.62, color)
      tx(`Lead${i}`, [x, y + 3.3, w, 0.54], a.lead, 'denseTitle', `${p}.lead`, {
        color,
      })
      tx(`FaceBody${i}`, [x, y + 3.94, w, 0.74], a.body, 'small', `${p}.body`)
    })
  } else if (role === 'gridTypes') {
    head()
    const frames = grid(d.items.length, r.items, Math.min(2, d.items.length))
    frames.forEach(([x, y, w, h], i) => {
      const a = d.items[i],
        p = `items[${i}]`,
        dw = 1.6,
        dx = x + w - dw,
        dy = y,
        dh = Math.min(1.9, h - 0.1),
        tw = w - dw - 0.3
      tx(`GridNum${i}`, [x, y, tw, 0.3], a.num, 'label', `${p}.num`, {
        color: col(a),
      })
      tx(`GridTitle${i}`, [x, y + 0.4, tw, 0.45], a.title, 'itemTitle', `${p}.title`, {
        color: col(a),
      })
      tx(`GridSubtitle${i}`, [x, y + 0.9, tw, 0.35], a.subtitle, 'label', `${p}.subtitle`)
      tx(`GridBody${i}`, [x, y + 1.35, tw, h - 1.35], a.body, 'small', `${p}.body`)
      cs.push({
        kind: 'diagram',
        name: `Diagram${i}`,
        frame: [dx, dy, dw, dh],
        diagram: a.diagram,
        color: col(a),
      })
    })
  } else if (role === 'system') {
    head()
    const model = d.model,
      base = model.baseUnit,
      format = (v) => `${Number(v.toFixed(4))}${model.unit}`,
      [x, y, w] = r.base
    tx('BaseLabel', [x, y, w, 0.32], d.labels.base, 'label', 'labels.base')
    tx('BaseValue', [x, y + 0.42, w, 0.95], format(base), 'statement', 'model.baseUnit', {
      color: 'red',
    })
    tx('BaseNote', [x, y + 1.45, w, 0.65], d.baseNote, 'small', 'baseNote')
    rule('BaseRule', x, y + 2.25, w, 'ink')
    const terms = [
      ['column', 'columnUnits'],
      ['gap', 'gapUnits'],
      ['row', 'rowUnits'],
    ]
    terms.forEach(([label, key], i) =>
      tx(
        `Derived${i}`,
        [x, y + 2.45 + i * 0.38, w, 0.32],
        `${d.labels[label]} ${format(base * model[key])}`,
        'small',
        `labels.${label}`,
      ),
    )
    tx('Callout', [x, y + 3.75, w, 0.55], d.callout, 'small', 'callout')
    const [dx, dy, dw, dh] = r.diagram,
      cols = model.columns,
      rows = model.rows,
      gap = model.gapUnits,
      unitsW = cols * model.columnUnits + (cols - 1) * gap,
      unitsH = rows * model.rowUnits + (rows - 1) * gap,
      cw = (dw * model.columnUnits) / unitsW,
      ch = ((dh - 0.5) * model.rowUnits) / unitsH,
      gx = (dw * gap) / unitsW,
      gy = ((dh - 0.5) * gap) / unitsH,
      ty = dy + 0.5
    for (let i = 0; i < cols; i++) {
      tx(
        `Measure${i}`,
        [dx + i * (cw + gx), dy, cw, 0.3],
        format(base * model.columnUnits),
        'label',
        'model.columnUnits',
        { alignment: 'center' },
      )
      rule(`MeasureRule${i}`, dx + i * (cw + gx), dy + 0.34, cw)
    }
    for (let j = 0; j < rows; j++)
      for (let i = 0; i < cols; i++) {
        if (j === 0 || (j >= 1 && j <= 2 && i >= 1 && i <= 2) || (j >= 3 && j <= 4 && i === 0))
          continue
        panel(`SystemCell${i}_${j}`, [dx + i * (cw + gx), ty + j * (ch + gy), cw, ch], null, 'rule')
      }
    const own = (name, frame, field, fill) => {
      const c = tx(
        name,
        [frame[0] + 0.05, frame[1], frame[2] - 0.1, frame[3]],
        d.labels[field],
        'label',
        `labels.${field}`,
        { color: 'ink', alignment: 'center', verticalAnchor: 'middle' },
      )
      Object.assign(c, { kind: 'owned', frame, fill, inset: 0.05 })
    }
    own('SystemHeadline', [dx, ty, dw, ch], 'headline', 'panel')
    own('SystemImage', [dx + cw + gx, ty + ch + gy, 2 * cw + gx, 2 * ch + gy], 'image', 'redTint')
    own('SystemText', [dx, ty + 3 * (ch + gy), cw, 2 * ch + gy], 'text', 'panel')
  } else if (role === 'statement') {
    tx('Label', r.label, d.label, 'label', 'label')
    rule('StatementMark', r.label[0] - 0.16, r.label[1], 0.62, 'red', true)
    tx('Title', r.title, d.title, 'statement', 'title')
    tx('Subtitle', r.subtitle, d.subtitle, 'itemTitle', 'subtitle')
    tx('Body', r.body, d.body, 'small', 'body')
    cs.push({ kind: 'dot', name: 'SignatureDot', frame: r.dot, color: 'red' })
  } else if (role === 'table') {
    head()
    const columns = d.columns,
      weights = columns.map((c) => c.weight ?? 1),
      total = weights.reduce((a, v) => a + v, 0),
      widths = weights.map((w) => (r.table[2] * w) / total),
      rows = d.rows,
      cells = [columns.map((c) => c.label), ...rows],
      headerH = 0.38,
      rowH = Math.min(0.52, (r.table[3] - headerH) / rows.length)
    for (let i = 0; i < cells.length; i++)
      for (let j = 0; j < columns.length; j++)
        fitText(
          cells[i][j],
          [0, 0, widths[j] - 0.2, i ? rowH : headerH],
          b.styles[i ? 'table' : 'tableHead'],
          `${path}.${i ? 'rows[' + (i - 1) + '][' + j + ']' : 'columns[' + j + '].label'}`,
        )
    cs.push({
      kind: 'table',
      name: 'Table',
      frame: [r.table[0], r.table[1], r.table[2], headerH + rowH * rows.length],
      cells,
      widths,
      rowHeights: cells.map((_, i) => (i ? rowH : headerH)),
      columns,
      rows,
      rowTones: d.rowTones ?? rows.map(() => 'neutral'),
    })
    const sourceFrame = [...r.source]
    if (layoutId === 'full')
      sourceFrame[1] = Math.min(sourceFrame[1], r.table[1] + headerH + rowH * rows.length + 0.25)
    tx('Source', sourceFrame, d.source, 'source', 'source')
  } else if (role === 'closing') {
    tx('TitleA', r.titleA, d.titleA, 'hero', 'titleA')
    tx('TitleB', r.titleB, d.titleB, 'hero', 'titleB', { color: 'red' })
    tx('Subtitle', r.subtitle, d.subtitle, 'itemTitle', 'subtitle')
    tx('FooterL', r.footerL, d.footerL, 'source', 'footerL')
    tx('FooterR', r.footerR, d.footerR, 'source', 'footerR', {
      alignment: 'right',
    })
    const [x0, y0, dw, dh] = r.dots
    for (let i = 0; i < 8; i++)
      dot(
        `ClosingDot${i}`,
        x0 + ((i % 4) * (dw - 0.07)) / 3,
        y0 + Math.floor(i / 4) * (dh - 0.07),
        0.035,
      )
  } else throw Error(`Unknown role ${role}`)
  return cs
}

export function resolveSwissDeck(design, content) {
  const b = design.swiss,
    layouts = [],
    warnings = []
  if (content.meta?.deckkit !== 'swiss-grid') throw Error('meta.deckkit must be swiss-grid')
  if (!Array.isArray(content.slides) || !content.slides.length)
    throw Error('slides must be nonempty')
  if (content.meta?.designScope && !['complete', 'excerpt'].includes(content.meta.designScope))
    throw Error('Unknown designScope')
  const full =
    content.meta?.designScope === 'complete' ||
    (content.meta?.designScope !== 'excerpt' &&
      content.slides.length >= b.rhythm.minFullDeck &&
      content.slides.some((s) => b.families[s.type]?.role === 'cover'))
  const counts = {
    timeline: 'steps',
    progress: 'steps',
    principles: 'items',
    people: 'people',
    columns: 'items',
    brands: 'brands',
    profile: 'events',
    typeface: 'cards',
    gridTypes: 'items',
    table: 'rows',
  }
  for (const [s, slide] of content.slides.entries()) {
    const family = b.families[slide.type],
      path = `slides[${s}].data`,
      d = slide.data
    if (!family) throw Error(`slides[${s}]: unknown Swiss slide type ${slide.type}`)
    assertDesignValue(d, inputSchema(slide.type), undefined, path)
    if (slide.customOps?.length || Object.keys(slide.imageSlots ?? {}).length)
      throw Error(`slides[${s}]: no registered custom operations or external image slots`)
    const field = counts[family.role]
    if (field) {
      const [min, max] = b.capacity[family.role === 'table' ? 'rows' : family.role]
      if (d[field].length < min || d[field].length > max)
        throw Error(`${path}.${field}: expected ${min}..${max} entries`)
    }
    if (full && family.role === 'cover' && s !== 0)
      throw Error('Cover must open a complete Swiss deck')
    if (full && family.role === 'closing' && s !== content.slides.length - 1)
      throw Error('Closing must end a complete Swiss deck')
    for (const a of Object.values(d).filter(Array.isArray))
      for (const item of a) {
        if (item?.icon && !hasTablerIcon(item.icon))
          throw Error(`${path}: unknown Tabler icon ${item.icon}`)
      }
    if (d.calloutHighlights) {
      for (const term of d.calloutHighlights)
        if (!d.callout.includes(term))
          throw Error(`${path}.calloutHighlights: term not present in callout`)
    }
    if (family.role === 'system') {
      for (const key of ['columns', 'rows'])
        if (!Number.isInteger(d.model[key])) throw Error(`${path}.model.${key}: integer required`)
    }
    if (family.role === 'table') {
      for (const [i, row] of d.rows.entries())
        if (row.length !== d.columns.length)
          throw Error(`${path}.rows[${i}]: expected ${d.columns.length} cells`)
      if (d.rowTones && d.rowTones.length !== d.rows.length)
        throw Error(`${path}.rowTones: one tone per row required`)
    }
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileSwissLayout(design, family, layoutId, v, d, path)
          components.push({
            ...fitText(
              `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
              b.chrome.page,
              { ...b.styles.source, alignment: 'right' },
              'structural.page',
            ),
            name: 'PageNum',
          })
          for (const c of components) {
            const [x, y, w, h] = c.frame
            if (
              x < 0 ||
              y < 0 ||
              w <= 0 ||
              h <= 0 ||
              x + w > design.canvas.widthIn + 0.001 ||
              y + h > design.canvas.heightIn + 0.001
            )
              throw Error(`${c.name}: component exceeds canvas`)
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
        b.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(chosen, {
      candidates: candidates.map((c) => c.layoutId),
      slideIndex: s,
      slideType: slide.type,
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (chosen.repeated)
      warnings.push(`slides[${s}]: repeated composition; reorganize content or use another role`)
  }
  if (full && (layouts[0].role !== 'cover' || layouts.at(-1).role !== 'closing'))
    throw Error(
      'Complete Swiss decks require cover and closing; use designScope=excerpt for extracts',
    )
  return { layouts, warnings, fullDeck: full }
}
