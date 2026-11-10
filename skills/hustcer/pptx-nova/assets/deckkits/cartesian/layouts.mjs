import { readFileSync } from 'node:fs'
import {
  assertDesignValue,
  designHash,
  selectDesignLayout,
  textUnits,
} from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { resolveCartesianSpecimen } from './exhibit.mjs'

const schemas = new Map()
function inputSchema(type) {
  if (!schemas.has(type))
    schemas.set(
      type,
      JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url))),
    )
  return schemas.get(type)
}

// Fit uses the exact text and frames that render. Width estimates remain conservative;
// canonical PNG/PDF, not this estimate, proves the actual typography.
export function cartesianText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = (((frame[2] - 0.04) * 72) / style.sizePt) * 0.94
  const text = wrapCjkText(value, capacity)
  let lines = 0
  for (const paragraph of text.split(/\r\n|\r|\n/)) {
    let used = 0
    lines++
    for (const word of paragraph.split(/(\s+)/u)) {
      const units = [...word].reduce(
        (n, c) =>
          n +
          (c.codePointAt(0) > 255
            ? 1
            : style.role === 'display' && !path.endsWith('.title')
              ? 0.48
              : 0.54) +
          (/[MW@]/u.test(c) ? 0.26 : 0),
        0,
      )
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
      `${path}: ${lines} lines need ${requiredHeight.toFixed(2)}in; frame has ${frame[3]}in`,
    )
  return { kind: 'text', text, frame, style, path, estimatedLines: lines, requiredHeight }
}

export function compileCartesianLayout(design, family, layoutId, variant, data, path = 'data') {
  const b = design.cartesian,
    r = variant.regions,
    g = b.spacing
  const components = variant.decorations.map((d, i) => ({ ...d, name: `Decoration${i}` }))
  const text = (name, frame, value, key, field = name, extra = {}) => {
    const c = cartesianText(value, frame, { ...b.styles[key], ...extra }, `${path}.${field}`)
    c.name = name
    components.push(c)
    return c
  }
  const label = (name, frame, value, field = name, extra = {}) =>
    text(name, frame, value.toUpperCase(), 'label', field, extra)
  const rule = (name, x, y, w) =>
    components.push({ kind: 'rule', name, frame: [x, y, w, 0.008], color: 'line' })
  const owned = (name, frame, value, key, fill, field = name) => {
    const c = text(name, frame, value, key, field, {
      alignment: 'center',
      verticalAnchor: 'middle',
    })
    c.kind = 'medallion'
    c.fill = fill
    return c
  }
  const role = family.role,
    center = ['cards', 'team', 'closing'].includes(role)
  if (r.label) label('Label', r.label, data.label, 'label', center ? { alignment: 'center' } : {})
  const heading = r.title
    ? text(
        'Title',
        [...r.title],
        data.title,
        variant.titleStyle,
        'title',
        center ? { alignment: 'center' } : {},
      )
    : null
  if (r.body) {
    const bodyFrame = [...r.body]
    if (role === 'column' || role === 'agenda' || (role === 'line' && layoutId === 'rail')) {
      heading.frame[3] = heading.requiredHeight + 0.01
      const top = heading.frame[1] + heading.frame[3] + g.paragraphGap
      bodyFrame[3] += bodyFrame[1] - top
      bodyFrame[1] = top
    }
    text(
      'Body',
      bodyFrame,
      data.body,
      'body',
      'body',
      role === 'line' && layoutId === 'wide' ? { alignment: 'right' } : {},
    )
  }
  if (role === 'exhibit') {
    text('Source', r.source, data.source, 'source', 'source')
    components.push({
      kind: 'exhibit',
      name: 'Exhibit',
      frame: r.stage,
      specimen: resolveCartesianSpecimen(r.stage, data.specimen, cartesianText, `${path}.specimen`),
    })
  }
  if (role === 'cover') text('Description', r.subtitle, data.subtitle, 'subtitle', 'subtitle')
  if (role === 'closing') {
    label('Cta', r.cta, data.cta, 'cta', { alignment: 'center' })
    text('Contact', r.contact, data.contact, 'source', 'contact', { alignment: 'center' })
  }
  if (role === 'statement') {
    const alignment = layoutId === 'centered' ? 'center' : 'left'
    text('QuoteMark', r.quoteMark, data.quoteMark ?? '“', 'quoteMark', 'quoteMark', { alignment })
    text('Quote', r.quote, data.quote, variant.titleStyle, 'quote', { alignment })
    label('Attribution', r.attribution, data.attribution, 'attribution', { alignment })
  }
  if (role === 'agenda') {
    const [x, y, w, h] = r.items,
      pitch = h / data.items.length
    if (data.textLayout === 'paragraphs') {
      const values = data.items.map(
        (item, i) => `${item.number ?? String(i + 1).padStart(2, '0')}  ${item.text}`,
      )
      values.forEach((value, i) =>
        cartesianText(value, [x, y, w, pitch - g.ruleGap], b.styles.body, `${path}.items[${i}]`),
      )
      const c = text('AgendaParagraphs', r.items, values.join('\n'), 'body', 'items')
      c.kind = 'paragraphs'
      c.levels = data.items.map((i) => i.level ?? 0)
      c.pitch = pitch
      rule('AgendaRule', x, y + h, w)
    } else {
      data.items.forEach((item, i) => {
        if (item.level !== undefined)
          throw Error(`${path}.items[${i}].level: requires textLayout=paragraphs`)
        text(
          `AgendaNum${i}`,
          [x, y + i * pitch + 0.08, 0.65, pitch - g.ruleGap],
          item.number ?? String(i + 1).padStart(2, '0'),
          'number',
          `items[${i}].number`,
        )
        text(
          `AgendaText${i}`,
          [x + 0.85, y + i * pitch + 0.1, w - 0.85, pitch - g.ruleGap],
          item.text,
          'body',
          `items[${i}].text`,
        )
        rule(`AgendaRule${i}`, x, y + (i + 1) * pitch, w)
      })
    }
  }
  if (role === 'column' || role === 'line') {
    for (const field of ['source', 'unit'])
      if (!data[field]?.trim()) throw Error(`${path}.${field}: required in 2.0`)
    const ch = data.chart,
      values = ch.series.flatMap((ss) => ss.values)
    if (
      ch.series.some(
        (ss) =>
          !ss.name.trim() ||
          ss.values.length !== ch.categories.length ||
          ss.values.some((v) => typeof v !== 'number' || !Number.isFinite(v)),
      )
    )
      throw Error(`${path}.chart: finite values must match every category`)
    if (
      ch.categories.some((s) => !s.trim() || textUnits(s) > b.chart.maxLabelUnits) ||
      ch.series.some((s) => textUnits(s.name) > b.chart.maxSeriesUnits)
    )
      throw Error(`${path}.chart: labels exceed capacity`)
    if (data.valueAxis) {
      const a = data.valueAxis
      if (a.majorUnit !== undefined && a.majorUnit <= 0)
        throw Error(`${path}.valueAxis.majorUnit: must be positive`)
      if (a.min !== undefined && a.min > Math.min(...values))
        throw Error(`${path}.valueAxis.min: clips data`)
      if (a.max !== undefined && a.max < Math.max(...values))
        throw Error(`${path}.valueAxis.max: clips data`)
      if (a.min !== undefined && a.max !== undefined && a.min >= a.max)
        throw Error(`${path}.valueAxis: invalid range`)
    }
    label('Unit', r.unit, data.unit, 'unit')
    text('Source', r.source, data.source, 'source', 'source')
    components.push({
      kind: 'chart',
      name: 'Chart',
      frame: r.chart,
      chartKind: role === 'column' ? 'column' : 'line',
      data: ch,
      axis: data.valueAxis ?? {},
      numberFormat: data.numberFormat ?? b.chart.numberFormat,
    })
  }
  if (role === 'image') {
    components.push({ kind: 'image', name: 'ImageShell', frame: r.image, label: data.imageLabel })
    cartesianText(
      data.imageLabel,
      [r.image[0] + 0.3, r.image[1], r.image[2] - 0.6, 0.35],
      b.styles.source,
      `${path}.imageLabel`,
    )
    const [x, baseY, w, baseH] = r.paragraphs
    heading.frame[3] = heading.requiredHeight + 0.01
    const y = heading.frame[1] + heading.frame[3] + g.paragraphGap,
      h = baseY + baseH - y
    let cy = y
    const paras = data.paragraphs.map((para, i) => {
      const c = cartesianText(para, [x, cy, w, h], b.styles.body, `${path}.paragraphs[${i}]`)
      cy += c.requiredHeight + g.paragraphGap
      return c
    })
    if (cy - g.paragraphGap > y + h + 0.002)
      throw Error(`${path}.paragraphs: reserve KPI divider gap; choose another layout or split`)
    cy = y
    paras.forEach((c, i) => {
      text(
        `Paragraph${i}`,
        [x, cy, w, c.requiredHeight + 0.01],
        data.paragraphs[i],
        'body',
        `paragraphs[${i}]`,
      )
      cy += c.requiredHeight + g.paragraphGap
    })
    const [sx, sy, sw, sh] = r.stats,
      n = data.stats.length,
      cw = (sw - g.columnGap * (n - 1)) / n
    rule('StatsRule', sx, sy - g.ruleGap, sw)
    data.stats.forEach((stat, i) => {
      text(
        `StatValue${i}`,
        [sx + i * (cw + g.columnGap), sy, cw, 0.56],
        stat.value,
        'metric',
        `stats[${i}].value`,
      )
      text(
        `StatLabel${i}`,
        [sx + i * (cw + g.columnGap), sy + 0.65, cw, sh - 0.65],
        stat.label,
        'source',
        `stats[${i}].label`,
      )
    })
  }
  if (role === 'cards') {
    const [x, y, w, h] = r.items,
      n = data.cards.length
    data.cards.forEach((card, i) => {
      const row = layoutId === 'row',
        cw = row ? (w - g.columnGap * (n - 1)) / n : w,
        ch = row ? h : h / n
      const cx = row ? x + i * (cw + g.columnGap) : x,
        cy = row ? y : y + i * ch,
        pad = g.padding
      if (row)
        components.push({ kind: 'panel', name: `Card${i}`, frame: [cx, cy, cw, ch], color: 'card' })
      else rule(`CardRule${i}`, cx, cy + ch - g.ruleGap, cw)
      const diameter = g.markerDiameter
      owned(
        `CardIcon${i}`,
        [cx + pad, cy + pad, diameter, diameter],
        card.marker ?? ['I', 'II', 'III'][i],
        'marker',
        row ? 'card' : 'bg',
        `cards[${i}].marker`,
      )
      const tx = row ? cx + pad : cx + pad + diameter + g.markerGap,
        tw = row ? cw - pad * 2 : cw - (tx - cx) - pad
      const ty = row ? cy + pad + diameter + g.itemTitleGap : cy + pad
      const title = text(
        `CardTitle${i}`,
        [tx, ty, tw, row ? 0.6 : 0.4],
        card.title,
        'itemTitle',
        `cards[${i}].title`,
      )
      const by = ty + (row ? 0.6 : title.requiredHeight) + g.itemBodyGap
      text(`CardBody${i}`, [tx, by, tw, cy + ch - pad - by], card.body, 'small', `cards[${i}].body`)
    })
  }
  if (role === 'timeline') {
    const [x, y, w, h] = r.items,
      n = data.items.length,
      vertical = layoutId === 'vertical'
    if (!vertical) rule('TimelineRule', x, y, w)
    data.items.forEach((item, i) => {
      const cw = vertical ? w : (w - g.columnGap * (n - 1)) / n,
        ch = vertical ? h / n : h,
        cx = vertical ? x : x + i * (cw + g.columnGap),
        cy = vertical ? y + i * ch : y + g.ruleGap
      if (vertical) rule(`TimelineRule${i}`, cx, cy + ch - g.ruleGap, cw)
      const tx = vertical ? cx + 2 : cx,
        tw = vertical ? cw - 2 : cw
      label(`Phase${i}`, [cx, cy, vertical ? 1.8 : cw, 0.3], item.phase, `items[${i}].phase`)
      const ty = vertical ? cy : cy + 0.43
      const title = text(
        `StepTitle${i}`,
        [tx, ty, tw, 0.65],
        item.title,
        'itemTitle',
        `items[${i}].title`,
      )
      title.frame[3] = title.requiredHeight + 0.01
      const by = ty + title.frame[3] + g.itemBodyGap
      text(
        `StepBody${i}`,
        [tx, by, tw, cy + ch - g.ruleGap - by],
        item.body,
        'small',
        `items[${i}].body`,
      )
    })
  }
  if (role === 'team') {
    const [x, y, w, h] = r.items,
      n = data.members.length,
      cw = w / n,
      diameter = Math.min(1.6, cw - g.columnGap)
    data.members.forEach((m, i) => {
      const cx = x + i * cw
      owned(
        `Initial${i}`,
        [cx + (cw - diameter) / 2, y, diameter, diameter],
        m.initial,
        'initial',
        'bg2',
        `members[${i}].initial`,
      )
      text(
        `Name${i}`,
        [cx + 0.05, y + diameter + 0.2, cw - 0.1, 0.6],
        m.name,
        'itemTitle',
        `members[${i}].name`,
        { alignment: 'center' },
      )
      text(
        `RoleLabel${i}`,
        [cx + 0.05, y + diameter + 0.87, cw - 0.1, h - diameter - 0.87],
        m.role,
        'source',
        `members[${i}].role`,
        { alignment: 'center' },
      )
    })
  }
  return components
}
export function resolveCartesianDeck(design, content) {
  const b = design.cartesian,
    layouts = [],
    warnings = []
  if (!Array.isArray(content.slides) || !content.slides.length)
    throw Error('slides: at least one page required')
  const full =
    content.meta?.designScope === 'complete' ||
    (content.meta?.designScope !== 'excerpt' &&
      content.slides.length >= b.rhythm.minFullDeck &&
      content.slides.some((s) => b.families[s.type]?.role === 'cover'))
  for (const [s, slide] of content.slides.entries()) {
    const family = b.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered Cartesian role ${slide.type}`)
    assertDesignValue(slide.data, inputSchema(slide.type), undefined, `slides[${s}].data`)
    if (full && family.role === 'cover' && s !== 0)
      throw Error('Cover must open a complete Cartesian deck')
    if (full && family.role === 'closing' && s !== content.slides.length - 1)
      throw Error('Closing must end a complete Cartesian deck')
    const failures = [],
      candidates = Object.entries(family.variants).flatMap(([layoutId, variant]) => {
        try {
          const components = compileCartesianLayout(
            design,
            family,
            layoutId,
            variant,
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
    if (chosen.repeated && candidates.length > 1)
      warnings.push(`slides[${s}]: repeated composition despite fitting alternatives`)
  }
  if (full && (layouts[0].role !== 'cover' || layouts.at(-1).role !== 'closing'))
    throw Error(
      'Complete Cartesian decks need cover and closing; use designScope=excerpt for extracts',
    )
  return { layouts, warnings, fullDeck: full }
}
