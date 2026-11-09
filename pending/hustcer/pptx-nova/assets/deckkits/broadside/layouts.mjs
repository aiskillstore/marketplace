import { readFileSync } from 'node:fs'
import { assertDesignValue, designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'

export const BROADSIDE_COMPARE_LIMITS = { title: 1.3, body: 1.5 }

export function broadsideText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const cjk = /[\u2e80-\u9fff]/u.test(value)
  style = {
    ...style,
    bold: style.bold || (cjk && style.cjkBold),
    lineHeight: cjk ? style.cjkLineHeight : style.lineHeight,
  }
  const cap = (((frame[2] - 0.05) * 72) / style.sizePt) * 0.94
  const text = wrapCjkText(value, cap)
  let lines = 0
  for (const paragraph of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const word of paragraph.split(/(\s+)/u)) {
      const units = [...word].reduce(
        (n, c) =>
          n +
          (c.codePointAt(0) > 255
            ? 1
            : style.role === 'display'
              ? 0.64
              : style.role === 'mono'
                ? 0.62
                : 0.53) +
          (/[MW@]/.test(c) ? 0.2 : 0),
        0,
      )
      if (units > cap + 0.001)
        throw Error(`${path}: word exceeds width; use another layout or split`)
      if (used && used + units > cap) {
        lines++
        used = 0
      }
      used += units
    }
  }
  const requiredHeight = (lines * style.sizePt * Math.max(1.45, style.lineHeight * 1.2)) / 72 + 0.03
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines need ${requiredHeight.toFixed(2)}in; frame has ${frame[3]}in`,
    )
  return {
    kind: 'text',
    text,
    frame: [...frame],
    style,
    path,
    estimatedLines: lines,
    requiredHeight,
  }
}
export const broadsideNumber = (value) =>
  Math.abs(value) >= 1e9 || (value !== 0 && Math.abs(value) < 0.001)
    ? value.toExponential(2)
    : String(Number(value.toFixed(3)))
export function compileBroadsideLayout(
  design,
  family,
  layoutId,
  variant,
  data,
  path = 'data',
  meta = {},
  index = 0,
) {
  const b = design.broadside,
    r = variant.regions,
    g = b.spacing,
    orange = family.mode === 'orange',
    components = []
  const text = (name, frame, value, key, field = name, extra = {}, required = true) => {
    if (!required && (value === undefined || value === '')) return null
    const style = {
      ...b.styles[key],
      ...(orange
        ? { color: key === 'label' || key === 'body' || key === 'small' ? 'orangeMuted' : 'ink' }
        : {}),
      ...extra,
    }
    const c = broadsideText(value, frame, style, `${path}.${field}`)
    c.name = name
    components.push(c)
    return c
  }
  const shape = (name, frame, color) =>
    components.push({ kind: 'shape', name, frame: [...frame], color })
  const rule = (name, x, y, w, color = orange ? 'orangeLine' : 'line') =>
    shape(name, [x, y, w, 0.008], color)
  const bulletList = (name, frame, items, field, size = 'small', tone = null) => {
    const [x, y, w, h] = frame,
      pitch = h / items.length
    items.forEach((item, i) => {
      text(`${name}Slash${i}`, [x, y + i * pitch, 0.2, 0.3], '/', 'label', `${field}[${i}]`, {
        color: tone === 'ink' ? 'ink' : orange ? 'ink' : 'orange',
      })
      text(
        `${name}Text${i}`,
        [x + 0.34, y + i * pitch, w - 0.34, pitch - g.itemGap],
        item,
        size,
        `${field}[${i}]`,
        tone ? { color: tone } : {},
      )
    })
  }
  const role = family.role
  // Chrome never supplies example text; the only automatic visible text is page numbering.
  if (!['chapter', 'quote'].includes(role)) {
    const anchor = ['cover', 'fade', 'closing'].includes(role),
      ch = b.chrome
    text(
      'ChromeL',
      anchor ? [...ch.topLeft.slice(0, 2), 2, ch.topLeft[3]] : ch.topLeft,
      anchor ? (data.number ?? String(index + 1).padStart(2, '0')) : data.section,
      'label',
      anchor ? 'number' : 'section',
      {},
      false,
    )
    text(
      'ChromeR',
      ch.topRight,
      anchor ? data.label : (data.page ?? String(index + 1).padStart(2, '0')),
      'label',
      anchor ? 'label' : 'page',
      { alignment: 'right' },
      false,
    )
    if (!anchor) rule('ChromeRule', ...ch.topRule.slice(0, 3))
    text(
      'FootL',
      ch.bottomLeft,
      anchor ? data.author : (data.footerLeft ?? meta.footerLeft),
      'label',
      anchor ? 'author' : 'footerLeft',
      {},
      false,
    )
    text(
      'FootR',
      ch.bottomRight,
      anchor ? data.context : (data.footerRight ?? meta.footerRight),
      'label',
      anchor ? 'context' : 'footerRight',
      { alignment: 'right' },
      false,
    )
    rule('FootRule', ...ch.bottomRule.slice(0, 3))
  }
  if (r.kicker)
    text('Kicker', r.kicker, data.kicker, 'label', 'kicker', {
      color: orange ? 'orangeMuted' : 'orange',
    })
  if (r.title)
    text(
      'Title',
      r.title,
      data.title,
      variant.titleStyle,
      'title',
      role === 'fade' ? { alignment: 'right' } : {},
    )
  if (['cover', 'closing'].includes(role))
    text(
      role === 'cover' ? 'Lead' : 'Contact',
      r[role === 'cover' ? 'subtitle' : 'contact'],
      data[role === 'cover' ? 'subtitle' : 'contact'],
      'body',
      role === 'cover' ? 'subtitle' : 'contact',
    )
  if (role === 'chapter') {
    text(
      'ChapterNum',
      r.number,
      data.number ?? String(index + 1).padStart(2, '0'),
      'label',
      'number',
    )
    text('Lead', r.lead, data.lead, 'body', 'lead', {}, false)
  }
  if (role === 'statement')
    rule('AccentRule', r.kicker[0], r.kicker[1] + r.kicker[3] + 0.15, 0.34, 'orange')
  if (role === 'split') {
    text('Lead', r.lead, data.lead, 'body', 'lead')
    bulletList('Bullet', r.bullets, data.bullets, 'bullets')
    components.push({ kind: 'image-shell', name: 'ImageSlot', frame: r.image })
    text(
      'ImageText',
      [r.image[0] + 0.3, r.image[1] + r.image[3] / 2 - 0.2, r.image[2] - 0.6, 0.4],
      data.imageLabel,
      'label',
      'imageLabel',
      { alignment: 'center' },
      false,
    )
    text('Caption', r.caption, data.caption, 'label', 'caption', {}, false)
  }
  if (role === 'stats') {
    const [x, y, w, h] = r.items,
      n = data.items.length,
      vertical = layoutId === 'register',
      cw = vertical ? w : (w - g.columnGap * (n - 1)) / n,
      ch = vertical ? h / n : h
    data.items.forEach((item, i) => {
      const xx = vertical ? x : x + i * (cw + g.columnGap),
        yy = vertical ? y + i * ch : y
      rule(`StatRule${i}`, xx, yy, cw)
      if (vertical) {
        text(
          `StatValue${i}`,
          [xx, yy + 0.2, cw * 0.31, ch - 0.3],
          item.value,
          'registerMetric',
          `items[${i}].value`,
        )
        text(
          `StatBody${i}`,
          [xx + cw * 0.35, yy + 0.16, cw * 0.65, ch * 0.45],
          item.label,
          'body',
          `items[${i}].label`,
        )
        text(
          `StatNote${i}`,
          [xx + cw * 0.35, yy + ch * 0.57, cw * 0.65, ch * 0.32],
          item.note,
          'label',
          `items[${i}].note`,
          {},
          false,
        )
      } else {
        text(`StatValue${i}`, [xx, yy + 0.22, cw, 1.12], item.value, 'metric', `items[${i}].value`)
        text(`StatBody${i}`, [xx, yy + 1.57, cw, 1], item.label, 'body', `items[${i}].label`)
        text(
          `StatNote${i}`,
          [xx, yy + 2.72, cw, 0.45],
          item.note,
          'label',
          `items[${i}].note`,
          {},
          false,
        )
      }
    })
  }
  if (role === 'fade') {
    const [x, y, w, h] = r.items,
      pitch = h / data.items.length
    data.items.forEach((value, i) =>
      text(`Item${i}`, [x, y + i * pitch, w, pitch - 0.05], value, 'fade', `items[${i}]`, {
        color: ['ink', 'fadeMid', 'fadeSoft'][i],
        alignment: 'right',
      }),
    )
  }
  if (role === 'list') bulletList('List', r.items, data.items, 'items', 'list')
  if (role === 'quote') {
    text('Quote', r.quote, data.quote, variant.titleStyle, 'quote')
    text('Author', r.author, data.author, 'label', 'author', { color: 'orange' })
    text('Source', r.source, data.source, 'label', 'source', {}, false)
  }
  if (role === 'compare') {
    const titleH =
      Math.max(
        ...['left', 'right'].map(
          (side) =>
            broadsideText(
              data[side].title,
              [0, 0, r[side][2] - g.padding * 2, BROADSIDE_COMPARE_LIMITS.title],
              b.styles.itemTitle,
              `${path}.${side}.title`,
            ).requiredHeight,
        ),
      ) + 0.02
    const bodyH =
      Math.max(
        ...['left', 'right'].map(
          (side) =>
            broadsideText(
              data[side].body,
              [0, 0, r[side][2] - g.padding * 2, BROADSIDE_COMPARE_LIMITS.body],
              b.styles.body,
              `${path}.${side}.body`,
            ).requiredHeight,
        ),
      ) + 0.02
    for (const [side, tone] of [
      ['left', false],
      ['right', true],
    ]) {
      const [xx, yy, ww, hh] = r[side],
        pad = g.padding,
        x = xx + pad,
        y = yy + pad,
        w = ww - pad * 2,
        d = data[side]
      if (tone) shape('RightPanel', r.right, 'orange')
      const colors = { color: tone ? 'ink' : 'cream' }
      text(`${side}Label`, [x, y, w, 0.35], d.label, 'label', `${side}.label`, {
        color: tone ? 'orangeMuted' : 'muted',
      })
      rule(`${side}Rule`, x, y + 0.52, w, tone ? 'orangeLine' : 'line')
      text(`${side}Title`, [x, y + 0.75, w, titleH], d.title, 'itemTitle', `${side}.title`, colors)
      const bodyY = 0.75 + titleH + g.paragraphGap,
        bulletY = bodyY + bodyH + g.paragraphGap
      text(`${side}Body`, [x, y + bodyY, w, bodyH], d.body, 'body', `${side}.body`, {
        color: tone ? 'orangeMuted' : 'muted',
      })
      bulletList(
        `${side}Bullet`,
        [x, y + bulletY, w, hh - pad * 2 - bulletY],
        d.bullets,
        `${side}.bullets`,
        'small',
        tone ? 'ink' : 'cream',
      )
    }
  }
  if (role === 'bar' || role === 'donut') {
    const items = role === 'bar' ? data.bars : data.items
    if (items.some((i) => typeof i.value !== 'number' || !Number.isFinite(i.value)))
      throw Error(`${path}: numeric values required in 2.0; do not infer from display strings`)
    if (items.some((i) => i.value < 0))
      throw Error(`${path}: negative values are unsupported for this positive-magnitude chart`)
    if (
      role === 'bar'
        ? !Number.isFinite(Math.max(...items.map((i) => i.value)) * 1.2)
        : !Number.isFinite(items.reduce((n, i) => n + i.value, 0))
    )
      throw Error(`${path}: chart magnitude exceeds the finite native chart range`)
    if (role === 'donut' && items.reduce((n, i) => n + i.value, 0) <= 0)
      throw Error(`${path}.items: positive total required`)
    if (items.filter((i) => i.accent === true).length > 1)
      throw Error(`${path}: at most one orange chart focus`)
    if (!data.unit?.trim() || !data.source?.trim() || !data.seriesName?.trim())
      throw Error(`${path}: unit, source and seriesName required`)
    const chartData = {
      categories: items.map((i) => i.label),
      series: [{ name: data.seriesName, values: items.map((i) => i.value) }],
    }
    for (const [i, item] of items.entries())
      broadsideText(
        item.label,
        [
          0,
          0,
          role === 'bar'
            ? layoutId === 'column'
              ? r.chart[2] / items.length - 0.15
              : 1.65
            : r.items[2] - 0.9,
          0.55,
        ],
        b.styles.label,
        `${path}.${role === 'bar' ? 'bars' : 'items'}[${i}].label`,
      )
    components.push({
      kind: 'chart',
      name: 'Chart',
      frame: r.chart,
      chartKind: role === 'donut' ? 'doughnut' : layoutId === 'column' ? 'column' : 'bar',
      data: chartData,
      focus: items.findIndex((i) => i.accent === true),
      numberFormat: data.numberFormat ?? b.chart.numberFormat,
    })
    if (role === 'bar')
      text(
        'Caption',
        r.caption,
        [data.caption, data.unit].filter(Boolean).join(' · '),
        'label',
        'caption',
      )
    else {
      const [x, y, w, h] = r.items,
        pitch = h / items.length
      items.forEach((item, i) => {
        const color = b.chart.pointColors[i]
        shape(`Swatch${i}`, [x, y + i * pitch + 0.1, 0.12, 0.12], color)
        text(
          `LegendLabel${i}`,
          [x + 0.3, y + i * pitch, w - 2.5, pitch - 0.12],
          item.label,
          'body',
          `items[${i}].label`,
          { color: 'cream' },
        )
        text(
          `LegendValue${i}`,
          [x + w - 2.2, y + i * pitch, 2.2, pitch - 0.12],
          `${broadsideNumber(item.value)} ${data.unit}`,
          'value',
          `items[${i}].value`,
          { alignment: 'right' },
        )
      })
      rule('TotalRule', r.total[0], r.total[1] - 0.15, r.total[2])
      text('Total', r.total, data.total, 'label', 'total', {}, false)
    }
    text('Source', r.source, data.source, 'label', 'source')
  }
  if (role === 'flow' || role === 'cycle') {
    const [x, y, w, h] = r.items,
      n = data.steps.length,
      vertical = layoutId === 'vertical',
      cycle = role === 'cycle'
    const gap = cycle ? 0.8 : g.columnGap,
      cw = cycle ? (w - gap) / 2 : vertical ? w : (w - gap * (n - 1)) / n,
      ch = cycle ? (h - 0.6) / 2 : vertical ? h / n : h
    const boxes = data.steps.map((step, i) => {
      const col = cycle ? (i === 1 || i === 2 ? 1 : 0) : vertical ? 0 : i,
        row = cycle ? (i >= 2 ? 1 : 0) : vertical ? i : 0
      return [x + col * (cw + gap), y + row * (ch + (cycle ? 0.6 : 0)), cw, ch]
    })
    data.steps.forEach((step, i) => {
      const [xx, yy, ww, hh] = boxes[i]
      if (cycle) rule(`StepRule${i}`, xx, yy, ww, 'orange')
      const top = yy + (cycle ? 0.12 : 0),
        numW = cycle ? 0.8 : vertical ? 1 : ww
      text(
        `StepNum${i}`,
        [xx, top, numW, vertical ? hh - 0.12 : 0.8],
        step.num ?? String(i + 1).padStart(2, '0'),
        cycle ? 'cycleNumber' : 'number',
        `steps[${i}].num`,
        { color: orange ? 'orangeMuted' : 'orange' },
      )
      const tx = cycle ? xx + 1 : vertical ? xx + 1.3 : xx,
        ty = vertical || cycle ? top : top + 0.95,
        tw = cycle ? ww - 1 : vertical ? ww - 1.3 : ww
      text(
        `StepTitle${i}`,
        [tx, ty, tw, vertical ? 0.45 : 0.55],
        step.title,
        'itemTitle',
        `steps[${i}].title`,
        { color: orange ? 'ink' : 'cream' },
      )
      const by = ty + (vertical ? 0.5 : 0.73)
      text(
        `StepBody${i}`,
        [cycle ? xx : tx, by, cycle ? ww : tw, yy + hh - by - 0.05],
        step.body,
        'small',
        `steps[${i}].body`,
        { color: orange ? 'orangeMuted' : 'muted' },
      )
    })
    if (!vertical) {
      const count = cycle ? n : n - 1
      for (let i = 0; i < count; i++) {
        const a = boxes[i],
          z = boxes[(i + 1) % n],
          right = z[0] > a[0],
          left = z[0] < a[0],
          arrow = right ? '→' : left ? '←' : i === 1 ? '↓' : '↑'
        const af =
          right || left
            ? [Math.min(a[0], z[0]) + cw + 0.04, a[1] + (cycle ? 0.2 : 0.75), gap - 0.08, 0.4]
            : [a[0] + cw * 0.5 - 0.2, Math.min(a[1], z[1]) + ch + 0.08, 0.4, 0.44]
        text(`Arrow${i}`, af, arrow, 'body', `steps[${i}]`, {
          alignment: 'center',
          color: orange ? 'orangeMuted' : 'muted',
        })
      }
    }
  }
  if (role === 'pyramid') {
    const [x, y, w, h] = r.items,
      n = data.levels.length,
      pitch = h / n
    data.levels.forEach((level, i) => {
      const ww = w * (0.5 + (0.5 * i) / (n - 1)),
        xx = x + (w - ww) / 2,
        yy = y + i * pitch,
        pad = g.padding
      shape(
        `Level${i}`,
        [xx, yy, ww, pitch - 0.05],
        ['level1', 'level2', 'level3', 'inkAlt', 'inkAlt'][i],
      )
      shape(`LevelAccent${i}`, [xx, yy, 0.035, pitch - 0.05], 'orange')
      text(
        `LevelName${i}`,
        [xx + pad, yy + 0.1, ww * 0.47 - pad, pitch - 0.2],
        level.name,
        'itemTitle',
        `levels[${i}].name`,
      )
      text(
        `LevelDesc${i}`,
        [xx + ww * 0.5, yy + 0.1, ww * 0.5 - pad, pitch - 0.2],
        level.desc,
        'small',
        `levels[${i}].desc`,
        { alignment: 'right', color: 'cream' },
      )
    })
  }
  if (role === 'timeline') {
    const [x, y, w, h] = r.items,
      n = data.events.length,
      vertical = layoutId === 'vertical',
      pitch = vertical ? h / n : (w - g.columnGap * (n - 1)) / n
    if (vertical) shape('Spine', [x + 1.9, y, 0.008, h], 'line')
    else rule('Spine', x, y + 0.56, w)
    data.events.forEach((event, i) => {
      const xx = vertical ? x : x + i * (pitch + g.columnGap),
        yy = vertical ? y + i * pitch : y,
        tw = vertical ? w - 2.3 : pitch,
        tx = vertical ? xx + 2.3 : xx
      text(
        `Date${i}`,
        [xx, yy, vertical ? 1.65 : pitch, 0.35],
        event.date,
        'label',
        `events[${i}].date`,
        vertical ? { alignment: 'right' } : {},
      )
      shape(
        `Tick${i}`,
        [vertical ? xx + 1.85 : xx, vertical ? yy + 0.1 : yy + 0.51, 0.1, 0.1],
        'orange',
      )
      const ty = vertical ? yy : yy + 0.85
      const heading = text(
        `EventTitle${i}`,
        [tx, ty, tw, vertical ? 0.42 : 1.2],
        event.title,
        'eventTitle',
        `events[${i}].title`,
      )
      if (!vertical) heading.frame[3] = heading.requiredHeight + 0.01
      const by = vertical ? ty + 0.47 : ty + heading.frame[3] + g.paragraphGap
      text(
        `EventBody${i}`,
        [tx, by, tw, vertical ? pitch - 0.52 : y + h - by - 0.05],
        event.body,
        'small',
        `events[${i}].body`,
      )
    })
  }
  return components
}
export function resolveBroadsideDeck(design, content) {
  const layouts = [],
    warnings = [],
    b = design.broadside
  if (content.meta?.deckkit && content.meta.deckkit !== design.id)
    throw Error('content.meta.deckkit must match broadside')
  if (!Array.isArray(content.slides) || !content.slides.length)
    throw Error('slides: at least one page required')
  const full =
    content.meta?.designScope === 'complete' ||
    (content.meta?.designScope !== 'excerpt' &&
      content.slides.length >= b.rhythm.minFullDeck &&
      content.slides[0].type === 'broadsideCoverSlide')
  for (const [s, slide] of content.slides.entries()) {
    const f = b.families[slide.type]
    if (!f) throw Error(`slides[${s}]: unregistered Broadside type ${slide.type}`)
    if (slide.customOps?.length) throw Error(`slides[${s}]: customOps are not supported`)
    if (slide.imageSlots && Object.keys(slide.imageSlots).length)
      throw Error('image.split is a placeholder shell; external assets are not supported')
    if (slide.layoutId && slide.layoutId !== 'auto' && !f.variants[slide.layoutId])
      throw Error(`slides[${s}]: unknown layoutId ${slide.layoutId}`)
    assertDesignValue(
      slide.data,
      JSON.parse(readFileSync(new URL(`./schemas/${slide.type}.schema.json`, import.meta.url))),
      undefined,
      `slides[${s}].data`,
    )
    const failures = [],
      candidates = Object.entries(f.variants).flatMap(([id, v]) => {
        try {
          const components = compileBroadsideLayout(
            design,
            f,
            id,
            v,
            slide.data,
            `slides[${s}].data`,
            content.meta,
            s,
          )
          return [
            {
              layoutId: id,
              role: f.role,
              mode: f.mode,
              components,
              fingerprint: designHash({
                role: f.role,
                frames: components.map((c) => [c.kind, c.frame]),
              }),
            },
          ]
        } catch (e) {
          failures.push(`${id}: ${e.message}`)
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
      slideIndex: s,
      slideType: slide.type,
      candidates: candidates.map((c) => c.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (
      full &&
      ((f.role === 'cover' && s !== 0) || (f.role === 'closing' && s !== content.slides.length - 1))
    )
      throw Error('Complete Broadside decks require cover first and closing last')
  }
  if (full && layouts[0].role !== 'cover')
    throw Error(
      'Complete Broadside decks require a cover first; use designScope=excerpt for extracts',
    )
  if (full && layouts.at(-1).role !== 'closing')
    throw Error('Complete Broadside decks require a closing; use designScope=excerpt for extracts')
  return { layouts, warnings, fullDeck: full }
}
