import { readFileSync } from 'node:fs'
import { assertDesignValue, designHash, selectDesignLayout } from '../shared/design-contract.mjs'
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

export function longTableText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const cjk = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]/u.test(value)
  const effective = { ...style, ...(cjk ? { italic: false } : {}) }
  const unit = (ch) =>
    ch.codePointAt(0) > 255
      ? 1
      : (style.role === 'display' ? 0.65 : 0.52) + (/[MW@]/.test(ch) ? 0.22 : 0)
  const capacity = ((frame[2] - 0.06) * 72) / style.sizePt
  const text = wrapCjkText(value, capacity * 0.95)
  let lines = 0
  for (const para of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const word of para.split(/(\s+)/u)) {
      const units = [...word].reduce((n, c) => n + unit(c), 0)
      if (units > capacity + 0.001) throw Error(`${path}: word exceeds width`)
      if (used && used + units > capacity) {
        lines++
        used = 0
      }
      used += units
    }
  }
  const requiredHeight = (lines * style.sizePt * Math.max(1.5, style.lineHeight * 1.2)) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines require ${requiredHeight.toFixed(2)}in, available ${frame[3].toFixed(2)}in`,
    )
  return {
    kind: 'text',
    text,
    frame: [...frame],
    style: effective,
    path,
    estimatedLines: lines,
    requiredHeight,
  }
}
export function compileLongTableLayout(design, family, layoutId, variant, data, path = 'data') {
  const b = design.longTable,
    r = variant.regions,
    g = b.spacing,
    cs = []
  const tx = (name, frame, value, key, field = name, extra = {}) => {
    const c = longTableText(value, frame, { ...b.styles[key], ...extra }, `${path}.${field}`)
    c.name = name
    cs.push(c)
    return c
  }
  const rule = (name, x, y, w, soft = false, dash = false) =>
    cs.push({ kind: 'rule', name, frame: [x, y, w, 0.005], color: soft ? 'ruleSoft' : 'ink', dash })
  const box = (name, frame) => cs.push({ kind: 'panel', name, frame })
  const own = (name, frame, value, key, field, kind = 'pill') => {
    const c = tx(
      name,
      [frame[0] + g.pad, frame[1], frame[2] - g.pad * 2, frame[3]],
      value,
      key,
      field,
      { alignment: 'center', verticalAnchor: 'middle' },
    )
    c.kind = kind
    c.frame = [...frame]
    c.inset = g.pad
    return c
  }
  const pills = (name, frame, values, field) => {
    const widths = values.map((value) =>
      Math.max(
        0.95,
        ([...value].reduce((n, c) => n + (c.codePointAt(0) > 255 ? 1.1 : 0.59), 0) *
          b.styles.pill.sizePt) /
          72 +
          g.pad * 2 +
          0.08,
      ),
    )
    if (widths.reduce((n, w) => n + w, 0) + g.gap * (values.length - 1) > frame[2])
      throw Error(`${path}.${field}: pills exceed available width`)
    let x = frame[0]
    values.forEach((value, i) => {
      own(name + i, [x, frame[1], widths[i], frame[3]], value, 'pill', `${field}[${i}]`)
      x += widths[i] + g.gap
    })
  }
  const role = family.role,
    center =
      (role === 'quote' && layoutId === 'centered') ||
      (role === 'closing' && layoutId === 'centered')
  if (r.badge) {
    const field = role === 'manifesto' || role === 'closing' ? 'mark' : 'edition'
    const c = tx('EditionBadge', r.badge, data[field], 'label', field, {
      alignment: 'center',
      verticalAnchor: 'middle',
    })
    c.kind = 'badge'
    c.inset = 0
  }
  if (r.eyebrow)
    tx(
      'Eyebrow',
      r.eyebrow,
      data[role === 'cover' ? 'editionLabel' : 'eyebrow'],
      'body',
      role === 'cover' ? 'editionLabel' : 'eyebrow',
    )
  if (r.title)
    tx(
      'Title',
      r.title,
      data.title,
      role === 'menu' && layoutId === 'programme' ? 'label' : variant.titleStyle,
      'title',
      center || layoutId === 'programme' ? { alignment: 'center' } : {},
    )
  if (r.subtitle)
    tx(
      'Subtitle',
      r.subtitle,
      data.subtitle,
      role === 'menu' && layoutId === 'programme' ? 'title' : 'label',
      'subtitle',
      { alignment: layoutId === 'programme' ? 'center' : 'right' },
    )
  if (['index', 'calendar'].includes(role)) rule('HeadingRule', 0.7, 2.05, 11.9)
  if (role === 'cover') {
    pills('Pill', r.pills, data.pills, 'pills')
    const [x, y, w] = r.stats
    tx('Stat', [x, y, w, 0.3], data.stat, 'small', 'stat', { bold: true })
    tx('StatNote', [x, y + 0.34, w, 0.36], data.statNote, 'small', 'statNote')
    tx('Tagline', r.tagline, data.tagline, 'body', 'tagline')
    tx('Description', r.description, data.description, 'small', 'description')
    for (const [field, key, region] of [
      ['bigEdition', 'edition', 'edition'],
      ['bigLabel', 'itemTitle', 'bigLabel'],
      ['bigMeta', 'small', 'bigMeta'],
    ])
      if (data[field] !== undefined)
        tx(field, r[region], data[field], key, field, { alignment: 'right' })
  }
  if (role === 'manifesto') {
    const [x, y, w, h] = r.paragraphs
    let top = y
    data.paragraphs.forEach((p, i) => {
      const c = tx(`Para${i}`, [x, top, w, h - (top - y)], p, 'body', `paragraphs[${i}]`)
      c.frame[3] = c.requiredHeight
      top += c.requiredHeight + g.gap
    })
    tx('Signature', r.signature, data.signature, 'body', 'signature', { bold: true })
    tx('Source', r.source, data.source, 'source', 'source')
  }
  if (role === 'index') {
    const [x, y, w, areaH] = r.items,
      h =
        data.cards.length === 1 && layoutId === 'cards'
          ? Math.min(areaH, g.singleCardHeight)
          : areaH,
      n = data.cards.length
    data.cards.forEach((card, i) => {
      if (layoutId === 'cards') {
        const cw = (w - g.gap * (n - 1)) / n,
          cx = x + i * (cw + g.gap),
          pad = g.pad,
          iw = cw - 2 * pad
        box(`Card${i}`, [cx, y, cw, h])
        tx(`CardNo${i}`, [cx + pad, y + 0.18, iw * 0.42, 0.28], card.no, 'label', `cards[${i}].no`)
        tx(
          `CardCity${i}`,
          [cx + pad + iw * 0.43, y + 0.18, iw * 0.57, 0.28],
          card.city,
          'label',
          `cards[${i}].city`,
          { alignment: 'right' },
        )
        rule(`CardRule${i}`, cx + pad, y + 0.6, iw, true)
        tx(
          `CardTitle${i}`,
          [cx + pad, y + 0.8, iw, 1],
          card.title,
          'cardTitle',
          `cards[${i}].title`,
        )
        tx(
          `CardBody${i}`,
          [cx + pad, y + 1.95, iw, h - 2.65],
          card.text,
          'small',
          `cards[${i}].text`,
        )
        rule(`CardBottom${i}`, cx + pad, y + h - 0.55, iw, true, true)
        card.meta.forEach((v, j) =>
          tx(
            `CardMeta${i}_${j}`,
            [cx + pad + iw * (j ? 0.38 : 0), y + h - 0.4, iw * (j ? 0.62 : 0.38), 0.28],
            v,
            'source',
            `cards[${i}].meta[${j}]`,
            { alignment: j ? 'right' : 'left' },
          ),
        )
      } else {
        const pitch = Math.min(h / n, g.registerMaxRowHeight),
          top = y + i * pitch
        tx(`CardNo${i}`, [x, top, 0.75, 0.3], card.no, 'label', `cards[${i}].no`)
        tx(`CardCity${i}`, [x, top + 0.4, 1.7, 0.65], card.city, 'label', `cards[${i}].city`)
        tx(
          `CardTitle${i}`,
          [x + 2, top, 3.5, pitch - 0.2],
          card.title,
          'cardTitle',
          `cards[${i}].title`,
        )
        tx(`CardBody${i}`, [x + 5.9, top, 6, pitch - 0.55], card.text, 'small', `cards[${i}].text`)
        card.meta.forEach((v, j) =>
          tx(
            `CardMeta${i}_${j}`,
            [x + 5.9 + j * 3, top + pitch - 0.4, 3, 0.28],
            v,
            'source',
            `cards[${i}].meta[${j}]`,
            { alignment: j ? 'right' : 'left' },
          ),
        )
        rule(`CardBottom${i}`, x, top + pitch - 0.08, w, true)
      }
    })
  }
  if (role === 'featured') {
    tx('Body', r.body, data.body, 'body', 'body')
    pills('Pill', r.pills, data.pills, 'pills')
    const [x, y, w, areaH] = r.details,
      pad = g.pad,
      h = Math.min(areaH, data.details.length * g.maxRowHeight + pad * 2),
      pitch = (h - pad * 2) / data.details.length
    box('InfoCard', [x, y, w, h])
    data.details.forEach((row, i) => {
      const top = y + pad + i * pitch
      tx(`InfoKey${i}`, [x + pad, top, w - pad * 2, 0.25], row[0], 'source', `details[${i}][0]`)
      tx(
        `InfoValue${i}`,
        [x + pad, top + 0.31, w - pad * 2, pitch - 0.39],
        row[1],
        'small',
        `details[${i}][1]`,
        { italic: false, bold: true },
      )
      if (i < data.details.length - 1)
        rule(`InfoRule${i}`, x + pad, top + pitch - 0.06, w - pad * 2, true, true)
    })
  }
  if (role === 'menu') {
    const [x, y, w, h] = r.items,
      pitch = Math.min(h / data.items.length, g.maxRowHeight)
    data.items.forEach((row, i) => {
      const top = y + i * pitch
      tx(`No${i}`, [x, top, 0.6, pitch - 0.1], row[0], 'label', `items[${i}][0]`)
      tx(`Name${i}`, [x + 0.8, top, w - 3.25, 0.3], row[1], 'itemTitle', `items[${i}][1]`)
      tx(
        `Desc${i}`,
        [x + 0.8, top + 0.35, w - 3.25, pitch - 0.48],
        row[2],
        'small',
        `items[${i}][2]`,
      )
      tx(`Pairing${i}`, [x + w - 2.1, top, 2.1, pitch - 0.15], row[3], 'source', `items[${i}][3]`, {
        alignment: 'right',
      })
      rule(`RowRule${i}`, x, top + pitch - 0.05, w, true)
    })
  }
  if (role === 'quote') {
    own('QuoteTag', r.label, data.label, 'label', 'label', 'tag')
    tx('Quote', r.quote, data.quote, variant.titleStyle, 'quote', {
      alignment: center ? 'center' : 'left',
    })
    rule('QuoteRule', center ? 5.3 : r.author[0], r.author[1] - 0.2, center ? 2.7 : r.author[2])
    tx('Author', r.author, data.author, 'small', 'author', {
      alignment: center ? 'center' : 'left',
      bold: true,
    })
    tx('Role', r.role, data.role, 'source', 'role', { alignment: center ? 'center' : 'left' })
  }
  if (role === 'calendar') {
    const [x, y, w, h] = r.table,
      pad = g.cellPad,
      hh = b.table.headerHeight,
      rowH = Math.min((h - hh) / data.rows.length, g.maxRowHeight)
    const cells = [data.columns, ...data.rows],
      widths = b.table.weights.map((v) => v * w)
    cells.forEach((row, i) =>
      row.forEach((value, j) =>
        longTableText(
          value,
          [0, 0, widths[j] - pad * 2, (i ? rowH : hh) - pad * 2],
          b.styles[i ? 'table' : 'tableHead'],
          `${path}.${i ? `rows[${i - 1}]` : 'columns'}[${j}]`,
        ),
      ),
    )
    cs.push({
      kind: 'table',
      name: 'Calendar',
      frame: [x, y, w, hh + rowH * data.rows.length],
      cells,
      widths,
      rowHeights: [hh, ...data.rows.map(() => rowH)],
    })
  }
  if (role === 'closing') {
    tx('Body', r.body, data.body, 'body', 'body', center ? { alignment: 'center' } : {})
    // site and CTA are both first-class owned capsule text.
    const [x, y, w, h] = r.actions
    own('Site', [x, y, w * 0.43, h], data.site, 'pill', 'site')
    own('Cta', [x + w * 0.43 + g.gap, y, w * 0.57 - g.gap, h], data.cta, 'pill', 'cta')
    const [fx, fy, fw, fh] = r.footer,
      cw = (fw - g.gap * (data.footer.length - 1)) / data.footer.length
    data.footer.forEach((row, i) => {
      const cx = fx + i * (cw + g.gap)
      rule(`FooterRule${i}`, cx, fy - g.ruleGap, cw)
      tx(`FooterLabel${i}`, [cx, fy, cw, 0.25], row[0], 'source', `footer[${i}][0]`, { bold: true })
      tx(`FooterValue${i}`, [cx, fy + 0.29, cw, fh - 0.29], row[1], 'source', `footer[${i}][1]`)
    })
  }
  return cs
}
export function resolveLongTableDeck(design, content) {
  const b = design.longTable,
    layouts = [],
    warnings = []
  if (!Array.isArray(content.slides) || !content.slides.length)
    throw Error('slides: at least one page required')
  if (content.meta?.deckkit !== 'long-table') throw Error('meta.deckkit must be long-table')
  const full =
    content.meta?.designScope === 'complete' ||
    (content.meta?.designScope !== 'excerpt' &&
      content.slides.length >= b.rhythm.minFullDeck &&
      content.slides.some((s) => b.families[s.type]?.role === 'cover'))
  for (const [s, slide] of content.slides.entries()) {
    const family = b.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unknown Long Table type ${slide.type}`)
    assertDesignValue(slide.data, inputSchema(slide.type), undefined, `slides[${s}].data`)
    if (slide.customOps?.length || Object.keys(slide.imageSlots ?? {}).length)
      throw Error(`slides[${s}]: no registered custom operations or image slots`)
    const capacityKey = {
      manifesto: 'paragraphs',
      index: 'cards',
      featured: 'details',
      menu: 'menu',
      calendar: 'rows',
      closing: 'footer',
    }[family.role]
    if (capacityKey) {
      const field = capacityKey === 'menu' ? 'items' : capacityKey,
        n = slide.data[field].length,
        [min, max] = b.capacity[capacityKey]
      if (n < min || n > max)
        throw Error(`slides[${s}].data.${field}: expected ${min}..${max} items`)
    }
    if (full && family.role === 'cover' && s !== 0)
      throw Error('Cover must open a complete Long Table deck')
    if (full && family.role === 'closing' && s !== content.slides.length - 1)
      throw Error('Closing must end a complete Long Table deck')
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileLongTableLayout(
            design,
            family,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
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
    chosen.candidates = candidates.map((c) => c.layoutId)
    chosen.slideIndex = s
    chosen.slideType = slide.type
    chosen.reason = slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm'
    layouts.push(chosen)
    if (chosen.repeated)
      warnings.push(
        `slides[${s}]: repeated composition; use auto or reorganize content when alternatives fit`,
      )
  }
  if (full && (layouts[0].role !== 'cover' || layouts.at(-1).role !== 'closing'))
    throw Error(
      'Complete Long Table decks need cover and closing; use designScope=excerpt for extracts',
    )
  return { layouts, warnings, fullDeck: full }
}
