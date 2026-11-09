import { readFileSync } from 'node:fs'
import {
  assertDesignValue,
  designHash,
  resolveEvidenceLayout,
  selectDesignLayout,
  textUnits,
} from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { BIENNALE_FIELDS } from './registry.mjs'

const schemas = new Map()
function inputSchema(id, type) {
  const key = `${id}/${type}`
  if (!schemas.has(key))
    schemas.set(
      key,
      JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url), 'utf8')),
    )
  return schemas.get(key)
}

// Resolver and renderer consume exactly the same text/frames. This is a conservative
// capacity estimate; final font metrics and optical spacing still require PNG review.
export function biennaleText(value, frame, style, path) {
  value = String(value)
  const capacity = (((frame[2] - 0.04) * 72) / style.sizePt) * 0.94
  const text = wrapCjkText(value, capacity)
  let lines = 0
  for (const paragraph of text.split(/\r\n|\r|\n/)) {
    let used = 0
    lines++
    for (const word of paragraph.split(/(\s+)/u)) {
      const units =
        [...word].reduce(
          (n, c) => n + (c.codePointAt(0) > 255 ? 1 : style.role === 'display' ? 0.46 : 0.52),
          0,
        ) +
        [...word].filter((c) => /[MW@]/u.test(c)).length * 0.3
      if (units > capacity + 0.001) throw new Error(`${path}: word exceeds component width`)
      if (used && used + units > capacity) {
        lines++
        used = 0
      }
      used += units
    }
  }
  const requiredHeight = (lines * style.sizePt * Math.max(1.42, style.lineHeight)) / 72 + 0.03
  if (requiredHeight > frame[3] + 0.002)
    throw new Error(
      `${path}: ${lines} lines need ${requiredHeight.toFixed(2)}in; component has ${frame[3]}in`,
    )
  return { kind: 'text', text, frame, style, path, estimatedLines: lines, requiredHeight }
}

export function compileBiennaleLayout(design, family, variant, data, path = 'data') {
  const b = design.biennale,
    r = variant.regions,
    gap = b.spacing
  const components = variant.decorations.map((d, i) => ({ ...d, name: `Decoration${i}` }))
  const text = (name, frame, value, style, field = name) => {
    const c = biennaleText(value, frame, b.styles[style], `${path}.${field}`)
    components.push({ ...c, name })
    return c
  }
  const rule = (name, x, y, w) =>
    components.push({
      kind: 'plane',
      name,
      frame: [x, y, w, 0.008],
      color: design.roles.rule,
      alpha: 0.35,
    })
  for (const [field, [region, style]] of Object.entries(BIENNALE_FIELDS[family.role]))
    text(field, r[region], data[field], style === '$title' ? variant.titleStyle : style, field)
  const credits = () => {
    const [x, y, w, h] = r.credits
    const weights = [2.2, 2.2, 2.7, 3.74],
      total = weights.reduce((a, b) => a + b)
    let cx = x
    data.footerItems.forEach((item, i) => {
      const cw = ((w - gap.columnGap * 3) * weights[i]) / total
      rule(`CreditRule${i}`, cx, y - gap.ruleGap, cw)
      text(
        `CreditLabel${i}`,
        [cx, y, cw, gap.creditLabelHeight],
        item.label,
        'label',
        `footerItems[${i}].label`,
      )
      const offset = gap.creditLabelHeight + gap.creditBodyGap
      text(
        `CreditText${i}`,
        [cx, y + offset, cw, h - offset],
        item.text,
        'source',
        `footerItems[${i}].text`,
      )
      cx += cw + gap.columnGap
    })
  }
  if (family.role === 'cover' || family.role === 'colophon') credits()
  if (family.role === 'programme') {
    const [x, y, w, h] = r.strands
    const titleH = (b.styles.strand.sizePt * Math.max(1.42, b.styles.strand.lineHeight)) / 72
    const bodyX = x + gap.numberWidth + gap.strandInset
    let cy = y
    const rows = data.strands.map((item, i) => {
      const frame = [bodyX, cy + titleH + 0.06, w - gap.numberWidth - gap.strandInset, h]
      const body = biennaleText(item.body, frame, b.styles.body, `${path}.strands[${i}].body`)
      const title = biennaleText(
        item.title,
        [bodyX, cy, frame[2], h],
        b.styles.strand,
        `${path}.strands[${i}].title`,
      )
      const rowH = title.requiredHeight + 0.06 + body.requiredHeight + gap.strandGap
      cy += rowH
      return { item, rowH, bodyH: body.requiredHeight, titleH: title.requiredHeight }
    })
    if (cy - y > h + 0.002)
      throw new Error(
        `${path}.strands: actual text heights exceed programme region; split the page`,
      )
    rule('ProgrammeHeadingRule', x, y - gap.ruleGap, w)
    cy = y
    rows.forEach(({ item, rowH, bodyH, titleH }, i) => {
      const num = text(
        `StrandNum${i}`,
        [x, cy, gap.numberWidth, titleH],
        item.num,
        'strand',
        `strands[${i}].num`,
      )
      num.style = { ...num.style, alignment: 'center', verticalAnchor: 'middle' }
      text(
        `StrandTitle${i}`,
        [bodyX, cy, w - (bodyX - x), titleH],
        item.title,
        'strand',
        `strands[${i}].title`,
      )
      text(
        `StrandBody${i}`,
        [bodyX, cy + titleH + 0.06, w - (bodyX - x), bodyH + 0.01],
        item.body,
        'body',
        `strands[${i}].body`,
      )
      rule(`StrandRule${i}`, x, cy + rowH - gap.strandGap / 2, w)
      cy += rowH
    })
  }
  if (family.role === 'data') {
    for (const field of ['unit', 'source'])
      if (!data[field].trim()) throw new Error(`${path}.${field}: nonblank metadata required`)
    const [x, y, w, h] = r.stats,
      rowH = (h - 0.4) / 2
    data.stats.forEach((stat, i) => {
      const sy = y + i * (rowH + 0.4)
      text(
        `StatValue${i}`,
        [x, sy, w, 1.1],
        `${stat.value}${stat.suffix}`,
        'metric',
        `stats[${i}].value+suffix`,
      )
      text(`StatLabel${i}`, [x, sy + 1.15, w, 0.25], stat.label, 'label', `stats[${i}].label`)
      text(
        `StatDescription${i}`,
        [x, sy + 1.5, w, rowH - 1.5],
        stat.description,
        'body',
        `stats[${i}].description`,
      )
    })
    const values = data.bars.map((p) => p.value)
    if (values.some((v) => typeof v !== 'number' || !Number.isFinite(v)))
      throw new Error(
        `${path}.bars[].value: 2.0 requires finite numeric values, unit and source; pct/string values need an explicit source-data migration`,
      )
    if (data.bars.filter((p) => p.accent).length > 1)
      throw new Error(`${path}.bars: at most one emphasis`)
    for (const [i, point] of data.bars.entries())
      if (textUnits(point.label) > 24)
        throw new Error(`${path}.bars[${i}].label: chart label exceeds capacity`)
    const tiny = values.some((v) => v !== 0 && Math.abs(v) < design.evidence.scientificBelow)
    const huge = values.some((v) => Math.abs(v) >= design.evidence.scientificAbove)
    components.push({
      kind: 'chart',
      name: 'DataChart',
      frame: r.chart,
      numberFormat:
        data.numberFormat ??
        (tiny || huge ? design.evidence.scientificFormat : design.evidence.numberFormat),
      data: {
        kind: 'bar',
        seriesName: data.label,
        unit: data.unit,
        points: data.bars.map((p) => ({ label: p.label, value: p.value, emphasis: p.accent })),
      },
    })
    rule('HeaderRule', 0.53, 1.35, 12.27)
    // Unit is visible metadata; chart series/workbook uses the identical string.
    text('DataUnit', [r.chart[0], r.chart[1] - 0.4, r.chart[2], 0.28], data.unit, 'label', 'unit')
  }
  if (family.role === 'calendar') {
    const [x, y, w, h] = r.table
    const weights = b.table.columnWeights,
      total = weights.reduce((a, b) => a + b)
    const widths = weights.map((weight) => (w * weight) / total)
    const cells = [
      data.columns,
      ...data.rows.map((row) => [row.date, row.title, row.venue, row.length]),
    ]
    const rowHeights = cells.map((row, i) =>
      Math.max(
        b.table.minRowHeight,
        ...row.map(
          (value, j) =>
            biennaleText(
              value,
              [0, 0, widths[j] - gap.cellPadding * 2, h],
              b.styles[i ? 'body' : 'label'],
              `${path}.${i ? `rows[${i - 1}].${['date', 'title', 'venue', 'length'][j]}` : `columns[${j}]`}`,
            ).requiredHeight +
            gap.cellPadding * 2,
        ),
      ),
    )
    const height = rowHeights.reduce((a, b) => a + b)
    if (height > h + 0.002)
      throw new Error(`${path}.rows: native table exceeds row capacity; split the calendar`)
    components.push({
      kind: 'table',
      name: 'Calendar',
      frame: [x, y, w, height],
      cells,
      widths,
      rowHeights,
    })
    rule('HeaderRule', 0.53, 1.35, 12.27)
  }
  if (family.role === 'quote')
    rule('AttributionRule', r.author[0], r.author[1] - gap.ruleGap, r.quote[2])
  return components
}

export function resolveBiennaleDeck(design, content) {
  const b = design.biennale,
    layouts = [],
    warnings = []
  if (!Array.isArray(content.slides) || !content.slides.length)
    throw new Error('slides: at least one page required')
  const full =
    content.meta?.designScope === 'complete' ||
    (content.meta?.designScope !== 'excerpt' &&
      content.slides.length >= b.rhythm.minFullDeck &&
      content.slides.some((s) => b.families[s.type]?.role === 'cover'))
  for (const [s, slide] of content.slides.entries()) {
    const path = `slides[${s}].data`,
      family = b.families[slide.type]
    if (!family && slide.type !== design.evidence.slideType)
      throw new Error(`slides[${s}]: unregistered Biennale family ${slide.type}`)
    if (
      family?.role === 'data' &&
      slide.data?.bars?.some((p) => p.pct !== undefined || typeof p.value !== 'number')
    )
      throw new Error(
        `${path}.bars: 2.0 replaces pct/string values with finite numeric value, unit and source; choose authoritative source data explicitly`,
      )
    assertDesignValue(slide.data, inputSchema(design.id, slide.type), undefined, path)
    let chosen
    if (!family) {
      chosen = { ...resolveEvidenceLayout(design, slide, layouts), role: 'evidence' }
    } else {
      const failures = []
      const candidates = Object.entries(family.variants).flatMap(([layoutId, variant]) => {
        try {
          const components = compileBiennaleLayout(design, family, variant, slide.data, path)
          return [
            {
              layoutId,
              components,
              role: family.role,
              fingerprint: designHash({ role: family.role, variant }),
            },
          ]
        } catch (e) {
          failures.push(`${layoutId}: ${e.message}`)
          return []
        }
      })
      try {
        chosen = selectDesignLayout(
          candidates,
          slide.layoutId ?? 'auto',
          layouts,
          b.rhythm.maxConsecutive,
        )
      } catch (e) {
        throw new Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
      }
      chosen.candidates = candidates.map((c) => c.layoutId)
      if (full && family.role === 'cover' && s !== 0)
        throw new Error('Cover must open a complete Biennale deck')
      if (full && family.role === 'colophon' && s !== content.slides.length - 1)
        throw new Error('Colophon must close a complete Biennale deck')
    }
    chosen.slideIndex = s
    chosen.slideType = slide.type
    chosen.reason = slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm'
    layouts.push(chosen)
    if (chosen.repeated && chosen.candidates.length > 1)
      warnings.push(`slides[${s}]: resolved composition repeats despite fitting alternatives`)
  }
  if (full && (layouts[0].role !== 'cover' || layouts.at(-1).role !== 'colophon'))
    throw new Error(
      'A complete Biennale deck requires cover and colophon; use designScope=excerpt for extracts',
    )
  return { layouts, warnings, fullDeck: full }
}

export function biennaleProjectedBudgets(design, family) {
  return Object.fromEntries(
    Object.entries(BIENNALE_FIELDS[family.role]).map(([field, [region, style]]) => {
      const budgets = Object.values(family.variants).map((v) => {
        const f = v.regions[region],
          t = design.biennale.styles[style === '$title' ? v.titleStyle : style]
        return {
          fontPt: t.sizePt,
          widthIn: f[2],
          heightIn: f[3],
          lineHeight: t.lineHeight,
          maxLines: Math.max(1, Math.floor((f[3] * 72) / (t.sizePt * t.lineHeight))),
        }
      })
      // Discovery describes the first registered layout; actual resolution tests all variants.
      return [field, budgets[0]]
    }),
  )
}
