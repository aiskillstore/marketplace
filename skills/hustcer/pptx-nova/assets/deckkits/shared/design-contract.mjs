// Opt-in design contracts. No DeckKit-specific decisions belong in this module.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve, sep } from 'node:path'
import { DECKKIT_ROOT } from './deckkit-paths.mjs'
import { wrapCjkText } from './design-text.mjs'
import { STRATEGY_REGIONS } from '../green-slate/registry.mjs'
import { ANNUAL_LAYOUTS } from '../clear-value/registry.mjs'
import { BIENNALE_REGIONS } from '../biennale-yellow/registry.mjs'
import { registeredDesignFamily, registeredDesignChecks } from './design-family-registry.mjs'
import { nativeChartMatches } from '../../../scripts/lib/pptx/native-chart-readback.mjs'

const root = resolve(DECKKIT_ROOT)
const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'))
export const designHash = (value) =>
  createHash('sha256').update(JSON.stringify(value)).digest('hex')
const CHECKS = new Set([
  'allowed-colors',
  'allowed-fonts',
  'forbidden-effects',
  'forbidden-operations',
  'bounds',
  'font-floor',
  'single-accent-focus',
  'editorial-language',
  'strategy-language',
  'annual-language',
  ...registeredDesignChecks,
])

// A deliberately bounded validator for the bundled design schema, not a general JSON Schema API.
export function assertDesignValue(value, schema, doc = schema, path = '$') {
  if (schema.$ref)
    return assertDesignValue(value, doc.$defs[schema.$ref.split('/').at(-1)], doc, path)
  const fail = (message) => {
    throw new Error(`${path}: ${message}`)
  }
  if (schema.oneOf) {
    const matches = schema.oneOf.filter((branch) => {
      try {
        assertDesignValue(value, branch, doc, path)
        return true
      } catch {
        return false
      }
    })
    if (matches.length !== 1) fail('expected exactly one specimen branch with its required payload')
  }
  if (schema.const !== undefined && value !== schema.const) fail(`expected ${schema.const}`)
  if (schema.enum && !schema.enum.includes(value)) fail(`expected one of ${schema.enum.join(', ')}`)
  const type = Array.isArray(value) ? 'array' : value === null ? 'null' : typeof value
  if (schema.type && type !== schema.type) fail(`expected ${schema.type}, got ${type}`)
  if (type === 'number') {
    if (!Number.isFinite(value)) fail('expected finite number')
    if (schema.minimum !== undefined && value < schema.minimum) fail(`minimum ${schema.minimum}`)
    if (schema.exclusiveMinimum !== undefined && value <= schema.exclusiveMinimum) {
      fail(`must exceed ${schema.exclusiveMinimum}`)
    }
    if (schema.maximum !== undefined && value > schema.maximum) fail(`maximum ${schema.maximum}`)
  }
  if (type === 'string') {
    if (schema.minLength && value.length < schema.minLength) fail('empty string')
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) fail('invalid format')
  }
  if (type === 'array') {
    if (schema.minItems !== undefined && value.length < schema.minItems) fail('too few items')
    if (schema.maxItems !== undefined && value.length > schema.maxItems) fail('too many items')
    value.forEach((v, i) => assertDesignValue(v, schema.items ?? {}, doc, `${path}[${i}]`))
  }
  if (type === 'object') {
    for (const k of schema.required ?? []) if (!Object.hasOwn(value, k)) fail(`missing ${k}`)
    for (const [k, v] of Object.entries(value)) {
      const child = schema.properties?.[k] ?? schema.additionalProperties
      if (child === false) fail(`unknown field ${k}`)
      if (child && typeof child === 'object') assertDesignValue(v, child, doc, `${path}.${k}`)
    }
  }
}

export function assertDesignContract(design) {
  const schema = readJson(resolve(root, 'schemas/design.schema.json'))
  assertDesignValue(design, schema, schema)
  const ruleIds = new Set()
  for (const rule of design.rules) {
    if (!CHECKS.has(rule.check)) throw new Error(`Unknown design checker: ${rule.check}`)
    if (ruleIds.has(rule.id)) throw new Error(`Duplicate design rule: ${rule.id}`)
    ruleIds.add(rule.id)
    if (['forbidden-effects', 'forbidden-operations'].includes(rule.check) && !rule.values?.length)
      throw new Error(`${rule.id}: values required`)
    if (rule.check === 'font-floor' && !(rule.minPt > 0)) {
      throw new Error(`${rule.id}: minPt required`)
    }
  }
  for (const token of [
    ...Object.values(design.roles),
    ...Object.values(design.theme.colors),
    ...Object.values(design.refurbish.palette),
  ])
    if (!Object.hasOwn(design.colors, token)) throw new Error(`Unknown color token: ${token}`)
  for (const role of [
    ...Object.values(design.theme.fonts),
    ...Object.values(design.refurbish.fonts),
  ])
    if (!Object.hasOwn(design.fonts, role)) throw new Error(`Unknown font role: ${role}`)
  if (
    !design.evidence &&
    !design.editorial &&
    !design.strategy &&
    !design.annual &&
    !design.biennale &&
    !registeredDesignFamily(design)
  )
    throw new Error('A registered design renderer is required')
  registeredDesignFamily(design)?.assert(design, { assertFrame })
  if (design.biennale) {
    const b = design.biennale
    if (!design.evidence) throw new Error('Biennale requires the native evidence renderer')
    for (const [name, style] of Object.entries(b.styles))
      if (!design.fonts[style.role]) throw new Error(name + ': unknown font role')
    for (const frame of Object.values(b.chrome)) assertFrame(design, frame, 'biennale.chrome')
    if (!Object.keys(b.families).length) throw new Error('Biennale requires families')
    for (const [type, family] of Object.entries(b.families)) {
      if (!Object.keys(family.variants).length) throw new Error(type + ': no variants')
      for (const [id, v] of Object.entries(family.variants)) {
        const expected = BIENNALE_REGIONS[family.role]
        if (
          expected.some((k) => !v.regions[k]) ||
          Object.keys(v.regions).some((k) => !expected.includes(k))
        )
          throw new Error(type + '.' + id + ': unregistered Biennale regions')
        if (!b.styles[v.titleStyle]) throw new Error(type + ': unknown title style')
        for (const frame of Object.values(v.regions)) assertFrame(design, frame, type + '.' + id)
        for (const decoration of v.decorations) {
          assertFrame(design, decoration.frame, type + '.' + id)
          if (!design.colors[decoration.color]) throw new Error('Unknown decoration token')
        }
      }
    }
  }
  for (const [id, layout] of Object.entries(design.evidence?.layouts ?? {})) {
    assertFrame(design, layout.chart, id)
    layout.stats.forEach((frame) => assertFrame(design, frame, id))
    const components = design.evidence.statComponents[id]
    if (!components) throw new Error(`${id}: missing stat components`)
    for (const component of Object.values(components)) {
      if (!Object.hasOwn(design.fonts, component.role)) throw new Error(`${id}: unknown font role`)
      if (layout.stats.some((frame) => component.y + component.h > frame[3] + 0.002)) {
        throw new Error(`${id}: stat component exceeds its region`)
      }
    }
  }
  for (const frame of Object.values(design.evidence?.header ?? {}))
    assertFrame(design, frame, 'header')
  if (design.evidence && design.evidence.scientificBelow >= design.evidence.scientificAbove) {
    throw new Error('Scientific format thresholds must be ordered')
  }
  if (design.editorial) {
    if (!design.fonts.body) throw new Error('Editorial renderer requires a body font role')
    for (const [key, frame] of Object.entries(design.editorial.chrome)) {
      if (Array.isArray(frame)) assertFrame(design, frame, `chrome.${key}`)
    }
    for (const token of Object.values(design.editorial.contrast)) {
      if (!Object.hasOwn(design.colors, token)) throw new Error(`Unknown editorial token: ${token}`)
    }
    for (const [type, family] of Object.entries(design.editorial.families)) {
      if (family.mode === 'dark' && !['summary', 'decision'].includes(family.role))
        throw new Error(`${type}: dark pages require summary/decision roles`)
      for (const [id, variant] of Object.entries(family.variants)) {
        const expected = {
          cover: ['title', 'abstract', 'metrics', 'watermark', 'band'],
          summary: ['main', 'side'],
          trend: ['main', 'detail'],
          matrix: ['main'],
          ranking: ['main', 'side'],
          decision: ['main'],
        }[family.role]
        for (const name of expected)
          if (!variant.regions[name]) throw new Error(`${type}.${id}: missing region ${name}`)
        for (const name of Object.keys(variant.regions))
          if (!expected.includes(name) && !(family.role === 'trend' && name === 'support'))
            throw new Error(`${type}.${id}: unknown region ${name}`)
        for (const [key, frame] of Object.entries(variant.regions))
          assertFrame(design, frame, `${type}.${id}.${key}`)
      }
    }
  }
  if (design.strategy) {
    const strategy = design.strategy
    for (const role of ['body', 'display'])
      if (!design.fonts[role]) throw new Error(`Strategy requires ${role} font`)
    for (const role of ['panel', 'header', 'secondary', 'negative', 'reference'])
      if (!design.roles[role]) throw new Error(`Strategy requires ${role} color role`)
    assertFrame(design, strategy.coverZone, 'coverZone')
    for (const [key, frame] of Object.entries(strategy.chrome))
      assertFrame(design, frame, `strategy.chrome.${key}`)
    if (!Object.keys(strategy.families).length) throw new Error('Strategy requires families')
    for (const [type, family] of Object.entries(strategy.families)) {
      if (!Object.keys(family.variants).length) throw new Error(`${type}: no variants`)
      for (const [id, variant] of Object.entries(family.variants)) {
        const expected = STRATEGY_REGIONS[family.role]
        if (
          expected.some((name) => !variant.regions[name]) ||
          Object.keys(variant.regions).some((name) => !expected.includes(name))
        )
          throw new Error(`${type}.${id}: regions must match strategy role ${family.role}`)
        for (const [key, frame] of Object.entries(variant.regions))
          assertFrame(design, frame, `${type}.${id}.${key}`)
      }
    }
  }
  if (design.annual) {
    const annual = design.annual
    for (const token of Object.values(annual.palette))
      if (!design.colors[token]) throw new Error('Annual palette contains an unknown token')
    for (const font of ['display', 'body'])
      if (!design.fonts[font]) throw new Error(`Annual requires ${font} font`)
    for (const [key, frame] of Object.entries(annual.chrome)) assertFrame(design, frame, key)
    if (!Object.keys(annual.families).length) throw new Error('Annual requires families')
    for (const [type, family] of Object.entries(annual.families)) {
      if (!Object.keys(family.variants).length) throw new Error(`${type}: no variants`)
      for (const [id, variant] of Object.entries(family.variants)) {
        const expected = ANNUAL_LAYOUTS[family.role]?.[id]
        if (
          !expected ||
          expected.some((k) => !variant.regions[k]) ||
          Object.keys(variant.regions).some((k) => !expected.includes(k))
        )
          throw new Error(`${type}.${id}: unregistered annual composition`)
        for (const frame of Object.values(variant.regions))
          assertFrame(design, frame, `${type}.${id}`)
      }
    }
  }
  return design
}

export function loadDesignContract(id) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id ?? '')) throw new Error('Invalid DeckKit id')
  const entry = readJson(resolve(root, 'catalog.json')).entries.find((e) => e.id === id)
  if (!entry) throw new Error(`Unknown DeckKit: ${id}`)
  if (!entry.designContract) return null
  const path = resolve(root, entry.designContract)
  if (!path.startsWith(root + sep)) {
    throw new Error('Design contract must stay inside DeckKit assets')
  }
  const design = assertDesignContract(readJson(path))
  if (design.id !== id) throw new Error('Design contract identity does not match catalog')
  return design
}

function assertFrame(design, frame, path) {
  const [x, y, w, h] = frame
  if (
    ![x, y, w, h].every(Number.isFinite) ||
    x < 0 ||
    y < 0 ||
    w <= 0 ||
    h <= 0 ||
    x + w > design.canvas.widthIn + 0.002 ||
    y + h > design.canvas.heightIn + 0.002
  )
    throw new Error(`${path}: frame outside canvas`)
}

export function designFont(design, role, sizePt, extra = {}) {
  const family = design.fonts[role]
  if (!family) throw new Error(`Unknown font role: ${role}`)
  return {
    name: family.latin,
    eastAsian: family.eastAsian,
    size: `${sizePt}pt`,
    color: design.colors[design.roles.text],
    ...extra,
  }
}

export function designTheme(design) {
  return {
    op: 'set-theme',
    colors: Object.fromEntries(
      Object.entries(design.theme.colors).map(([slot, token]) => [slot, design.colors[token]]),
    ),
    fonts: Object.fromEntries(
      Object.entries(design.theme.fonts).map(([slot, role]) => [
        slot,
        { typeface: design.fonts[role].latin, eastAsian: design.fonts[role].eastAsian },
      ]),
    ),
  }
}

// Approximate CJK/Latin advance for candidate selection only. PNG gates remain authoritative.
export const textUnits = (value) =>
  [...String(value ?? '')].reduce((n, ch) => n + (ch.codePointAt(0) > 255 ? 1 : 0.52), 0)

// Selection is shared; visual families own candidate geometry and content compatibility.
export function selectDesignLayout(candidates, requested, previous = [], maxConsecutive = 2) {
  const eligible =
    requested === 'auto' ? candidates : candidates.filter((c) => c.layoutId === requested)
  if (!eligible.length)
    throw new Error('No layout fits; choose auto, reorganize content or split the slide')
  const recent = previous.slice(-maxConsecutive)
  return eligible
    .map((candidate, order) => ({
      ...candidate,
      order,
      used: previous.filter((p) => p.fingerprint === candidate.fingerprint).length,
      repeated:
        recent.length === maxConsecutive &&
        recent.every((p) => p.fingerprint === candidate.fingerprint),
    }))
    .sort(
      (a, b) => Number(a.repeated) - Number(b.repeated) || a.used - b.used || a.order - b.order,
    )[0]
}

export function resolveEvidenceLayout(design, slide, previous = []) {
  const d = slide.data
  const e = design.evidence
  const fail = (message) => {
    throw new Error(`Evidence content: ${message}`)
  }
  for (const field of ['title', 'label', 'source', 'seriesName', 'unit']) {
    if (typeof d?.[field] !== 'string' || !d[field].trim()) fail(`${field} is required`)
  }
  if (!['bar', 'line'].includes(d.kind)) fail('kind must be bar or line')
  if (
    !Array.isArray(d.points) ||
    d.points.length < e.limits.minPoints ||
    d.points.length > e.limits.maxPoints
  )
    fail(`points must contain ${e.limits.minPoints}..${e.limits.maxPoints} observations`)
  if (d.points.some((p) => typeof p.value !== 'number' || !Number.isFinite(p.value))) {
    fail('all values must be finite numbers; missing values must not be silently converted to zero')
  }
  if (d.points.some((p) => typeof p.label !== 'string' || !p.label.trim())) {
    fail('each point needs a label')
  }
  if (d.points.filter((p) => p.emphasis).length > 1) fail('at most one emphasis point')
  if (!Array.isArray(d.stats) || d.stats.length !== 2) fail('exactly two stats are required')
  if (textUnits(d.title) > e.limits.maxTitleUnits) {
    fail('title exceeds capacity; shorten with authorization or split the slide')
  }
  const titleLines = String(d.title)
    .split('\n')
    .reduce((n, line) => n + Math.max(1, Math.ceil(textUnits(line) / e.shortTitleUnits)), 0)
  if (titleLines > 2) fail('title needs more than two lines; split or shorten with authorization')
  for (const stat of d.stats) {
    for (const field of ['value', 'suffix', 'label', 'description']) {
      if (typeof stat[field] !== 'string') fail(`stats.${field} must be text`)
    }
    if (textUnits(stat.description) > e.limits.maxDescriptionUnits) {
      fail('stat description exceeds capacity; split the slide')
    }
  }
  const linesNeeded = (text, width, size) =>
    String(text)
      .split('\n')
      .reduce(
        (n, line) => n + Math.max(1, Math.ceil(textUnits(line) / (((width - 0.04) * 72) / size))),
        0,
      )
  const fits = (text, frame, size) =>
    linesNeeded(text, frame[2], size) * size * e.textLineHeight <= frame[3] * 72
  if (
    !fits(`${d.label} · ${d.unit}`, e.header.label, e.fontPt.label) ||
    !fits(d.source, e.header.source, e.fontPt.source)
  )
    fail('label/unit or source exceeds its single-line capacity; shorten with authorization')
  const maxLabel = Math.max(...d.points.map((p) => textUnits(p.label)))
  const scientific = d.points.some(
    (p) =>
      p.value !== 0 &&
      (Math.abs(p.value) < e.scientificBelow || Math.abs(p.value) >= e.scientificAbove),
  )
  const candidates = Object.entries(e.layouts).filter(
    ([id, l]) =>
      d.points.length <= l.maxPoints &&
      maxLabel <= l.maxLabelUnits &&
      d.stats.every((stat, i) =>
        Object.entries(e.statComponents[id]).every(([field, spec]) => {
          let value = field === 'value' ? stat.value + stat.suffix : stat[field]
          if (field === 'description') {
            value = wrapCjkText(
              value,
              (((l.stats[i][2] - 0.04) * 72) / e.fontPt.body) * e.cjkWrapSafety,
            )
          }
          return fits(
            value,
            [0, 0, l.stats[i][2], spec.h],
            spec.fontPt ?? e.fontPt[field === 'description' ? 'body' : field],
          )
        }),
      ),
  )
  const requested = slide.layoutId ?? 'auto'
  if (requested !== 'auto' && !e.layouts[requested]) fail(`unknown layoutId ${requested}`)
  const eligible = requested === 'auto' ? candidates : candidates.filter(([id]) => id === requested)
  if (!eligible.length) {
    fail(
      'no layout fits the point/label budget; choose auto, shorten labels with authorization or split the slide',
    )
  }
  const geometry = (id, layout) => {
    const shift = titleLines > 1 ? e.titleShiftIn : 0
    const frame = structuredClone(layout)
    frame.chart[1] += shift
    frame.chart[3] -= shift
    if (frame.shiftStatsWithHeader) {
      frame.stats.forEach((f) => {
        f[1] += shift
      })
    }
    const header = structuredClone(e.header)
    header.title[3] += shift
    for (const key of ['label', 'rule']) header[key][1] += shift
    const fingerprint = designHash({
      chart: frame.chart,
      stats: frame.stats,
      header,
      statComponents: e.statComponents[id],
    })
    return { frame, header, fingerprint }
  }
  const ranked = eligible.map(([id, layout]) => {
    const resolved = geometry(id, layout)
    return {
      id,
      layoutId: id,
      ...resolved,
    }
  })
  const chosen = selectDesignLayout(ranked, requested, previous, e.maxConsecutiveLayout)
  const { frame, header, fingerprint } = chosen
  assertFrame(design, frame.chart, chosen.id)
  for (const f of frame.stats) assertFrame(design, f, chosen.id)
  return {
    layoutId: chosen.id,
    frame,
    header,
    fingerprint,
    titleLines,
    numberFormat: scientific ? e.scientificFormat : e.numberFormat,
    reason:
      requested === 'auto'
        ? chosen.repeated
          ? 'only-fitting-layout'
          : 'fit-and-rhythm'
        : 'explicit',
    candidates: candidates.map(([id]) => id),
    repeated: chosen.repeated,
  }
}

export function checkDesignPatch(design, patch) {
  const issues = []
  const accentGroups = new Map()
  const colors = new Set(Object.values(design.colors))
  const fonts = new Set(Object.values(design.fonts).flatMap((f) => [f.latin, f.eastAsian]))
  const issue = (rule, message, index) =>
    issues.push({ ruleId: rule.id, severity: 'error', message, opIndex: index })
  patch.ops.forEach((op, index) => {
    if (design.rules.some((r) => r.check === 'single-accent-focus')) {
      const gold = design.colors[design.roles.focus]
      const hasGold = (v) =>
        typeof v === 'string'
          ? v === gold
          : v && typeof v === 'object' && Object.values(v).some(hasGold)
      const name = op.shape?.name ?? op.name
      const remember = (group) => {
        const groups = accentGroups.get(op.slide) ?? new Set()
        groups.add(group)
        accentGroups.set(op.slide, groups)
      }
      if (hasGold(op) && op.op !== 'set-theme' && !name?.endsWith('_AccentRule')) {
        if (op.op === 'set-chart') {
          for (const series of op.series ?? []) {
            if (hasGold(series.fill) || hasGold(series.line) || hasGold(series.marker))
              remember(`${name}:series${series.series}`)
            for (const point of series.points ?? [])
              if (hasGold(point)) remember(`${name}:series${series.series}:point${point.point}`)
          }
        } else remember(name ?? op.op)
      }
    }
    for (const rule of design.rules) {
      registeredDesignFamily(design)?.checks[rule.check]?.(
        design,
        op,
        (message) => issue(rule, message, index),
        { patch, index },
      )
      if (rule.check === 'annual-language') {
        const a = design.annual,
          palette = Object.fromEntries(
            Object.entries(a.palette).map(([k, v]) => [k, design.colors[v]]),
          )
        if (
          op.op === 'set-slide-background' &&
          (op.fill?.type !== 'solid' || op.fill.color !== palette.paper)
        )
          issue(rule, 'Annual pages require a white contracted surface', index)
        if (op.op === 'add-shape' && !['rectangle', 'oval'].includes(op.kind))
          issue(rule, 'Unregistered annual shape', index)
        if (op.op === 'add-chart' && !['bar', 'column', 'line', 'doughnut'].includes(op.kind))
          issue(rule, 'Unregistered annual chart', index)
        if (op.op === 'set-chart' && op.view3D) issue(rule, '3D is forbidden', index)
        if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
          issue(rule, 'Annual tables use explicit horizontal rules', index)
        if (op.op === 'set-shape' && op.fill?.type === 'solid') {
          const owner = patch.ops.find(
            (o) => o.op === 'add-shape' && o.slide === op.slide && o.name === op.shape?.name,
          )
          if (
            owner &&
            op.fill.color === palette.terracotta &&
            parseFloat(owner.w) * parseFloat(owner.h) > 0.08
          )
            issue(rule, 'Conclusion color cannot fill a panel', index)
        }
        if (op.op === 'set-chart')
          for (const series of op.series ?? []) {
            const used = [
              series.fill?.color,
              series.line?.color,
              ...(series.points ?? []).flatMap((p) => [p.fill?.color, p.line?.color]),
            ]
            if (used.includes(palette.terracotta))
              issue(rule, 'Conclusion color is not a series or negative color', index)
          }
      }
      if (rule.check === 'strategy-language') {
        if (op.op === 'add-chart' && !['bar', 'line'].includes(op.kind))
          issue(rule, `Unregistered strategy chart ${op.kind}`, index)
        if (op.op === 'set-chart' && op.view3D) issue(rule, '3D is forbidden', index)
        if (
          op.op === 'set-slide-background' &&
          (op.fill?.type !== 'solid' || op.fill.color !== design.colors[design.roles.surface])
        )
          issue(rule, 'Strategy content requires the contracted dark surface', index)
        if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
          issue(rule, 'Strategy tables use explicit cells and fine rules', index)
        if (op.op === 'set-text-frame' && typeof op.text === 'string') {
          const owner = patch.ops.find(
            (o) => o.op === 'add-shape' && o.slide === op.slide && o.name === op.shape?.name,
          )
          if (owner?.kind === 'oval') {
            const paragraph = patch.ops.find(
              (o) =>
                o.op === 'set-paragraph' && o.slide === op.slide && o.shape?.name === owner.name,
            )
            if (op.frame?.verticalAnchor !== 'middle' || paragraph?.format?.alignment !== 'center')
              issue(rule, 'Circle-owned text must be centered horizontally and vertically', index)
          }
          const textbox = patch.ops.find(
            (o) => o.op === 'add-text-box' && o.slide === op.slide && o.name === op.shape?.name,
          )
          if (textbox) {
            const [x, y, w, h] = [textbox.x, textbox.y, textbox.w, textbox.h].map(parseFloat)
            for (const shape of patch.ops.filter(
              (o) =>
                o.op === 'add-shape' &&
                o.slide === op.slide &&
                ['oval', 'rectangle'].includes(o.kind),
            )) {
              const [sx, sy, sw, sh] = [shape.x, shape.y, shape.w, shape.h].map(parseFloat)
              if (sw > 6 || sh > 1.1) continue
              const overlap =
                (Math.max(0, Math.min(x + w, sx + sw) - Math.max(x, sx)) *
                  Math.max(0, Math.min(y + h, sy + sh) - Math.max(y, sy))) /
                (w * h)
              if (overlap >= 0.35)
                issue(
                  rule,
                  'Enclosed labels must use shape-owned text, not an independent overlapping textbox',
                  index,
                )
            }
          }
        }
      }
      if (rule.check === 'editorial-language') {
        if (op.op === 'add-chart' && !['bar', 'column', 'line'].includes(op.kind))
          issue(rule, `Unregistered editorial chart ${op.kind}`, index)
        if (op.op === 'set-chart') {
          if (op.view3D) issue(rule, '3D is forbidden', index)
          for (const axis of op.axes ?? []) {
            if (
              (axis.gridlines && !axis.gridlines.noLine) ||
              (axis.minorGridlines && !axis.minorGridlines.noLine)
            )
              issue(rule, 'Chart gridlines are forbidden', index)
            if (
              axis.axis === 'value' &&
              (axis.ticks?.visible === true || parseFloat(axis.line?.width ?? '0') > 0)
            )
              issue(rule, 'Visible value axis is forbidden', index)
          }
        }
        if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
          issue(rule, 'Table banding is forbidden', index)
        for (const cell of op.cells ?? [])
          for (const key of ['left', 'right']) {
            const border = cell.style?.borders?.[key]
            if (border && !border.noLine && parseFloat(border.width ?? '1') > 0)
              issue(rule, 'Dense vertical table rules are forbidden', index)
          }
      }
      if (rule.check === 'forbidden-operations' && rule.values.includes(op.op)) {
        issue(rule, `Forbidden operation ${op.op}`, index)
      }
      if (rule.check === 'bounds' && op.x !== undefined) {
        try {
          assertFrame(
            design,
            [op.x, op.y, op.w, op.h].map((v) =>
              /^\d+(?:\.\d+)?in$/.test(v) ? parseFloat(v) : NaN,
            ),
            op.name,
          )
        } catch (error) {
          issue(rule, error.message, index)
        }
      }
      const walk = (v, key = '') => {
        if (
          rule.check === 'allowed-colors' &&
          ['color', 'rgb', 'fill', ...Object.keys(design.theme.colors)].includes(key) &&
          typeof v === 'string' &&
          /^#?[0-9a-f]{6}$/i.test(v) &&
          !colors.has(v.replace(/^#/, '').toUpperCase())
        )
          issue(rule, `Unapproved color ${v}`, index)
        if (v && typeof v === 'object') {
          if (
            ['editorial-language', 'strategy-language', 'annual-language'].includes(rule.check) &&
            key === 'fill' &&
            v.type !== 'solid' &&
            v.type !== 'none'
          )
            issue(rule, 'Gradient/pattern fills are not part of this language', index)
          if (rule.check === 'allowed-fonts') {
            for (const k of ['name', 'eastAsian', 'typeface']) {
              if ((key === 'font' || ['major', 'minor'].includes(key)) && v[k] && !fonts.has(v[k]))
                issue(rule, `Unapproved font ${v[k]}`, index)
            }
          }
          if (
            rule.check === 'font-floor' &&
            key === 'font' &&
            v.size &&
            parseFloat(v.size) < rule.minPt
          )
            issue(rule, `Font ${v.size} is below ${rule.minPt}pt`, index)
          if (rule.check === 'forbidden-effects' && key === 'effect') {
            for (const k of rule.values) {
              if (v[k] !== undefined && v[k] !== null) issue(rule, `Forbidden effect ${k}`, index)
            }
          }
          for (const [k, c] of Object.entries(v)) walk(c, k)
        }
      }
      walk(op)
    }
  })
  const accentRule = design.rules.find((r) => r.check === 'single-accent-focus')
  for (const [slide, groups] of accentGroups) {
    if (groups.size > 1)
      issue(accentRule, `Slide ${slide}: ${groups.size} gold focus groups; maximum one`)
  }
  return {
    schemaVersion: 'pptx-nova-design-check/v1',
    status: issues.length ? 'fail' : 'pass',
    contractHash: designHash(design),
    checkedRules: design.rules.map((r) => r.id),
    issues,
    visualReviewRequired: true,
  }
}

export function finishDesign(design, content, patch, layouts = []) {
  const check = checkDesignPatch(design, patch)
  if (check.status === 'fail') {
    throw new Error(`Design check failed: ${check.issues.map((i) => i.message).join('; ')}`)
  }
  const objects = patch.ops
    .filter((o) =>
      ['add-text-box', 'add-shape', 'add-freeform', 'add-chart', 'add-table', 'add-image'].includes(
        o.op,
      ),
    )
    .map((o) => ({
      slide: o.slide,
      name: o.name,
      kind: o.op,
      frame: [o.x, o.y, o.w, o.h].map(parseFloat),
    }))
  const plan = {
    schemaVersion: 'pptx-nova-design-plan/v1',
    designId: design.id,
    designVersion: design.version,
    contractHash: designHash(design),
    contentHash: designHash(content),
    patchHash: designHash(patch),
    layouts,
    objects,
  }
  return { patch, warnings: [], designPlan: plan, designCheck: check, designContract: design }
}

function readbackObjectState(object, patch) {
  // Keep the plan's creation identity, while following names in operation order.
  // This also retains text/frame/crop expectations authored before a Morph rename.
  const state = { name: object.name }
  let created = false
  for (const op of patch.ops) {
    if (op.slide !== object.slide) continue
    if (!created) {
      if (op.op === object.kind && op.name === object.name) created = true
      continue
    }
    if (op.shape?.name !== state.name) continue
    if (op.op === 'set-text-frame') {
      if (typeof op.text === 'string') state.text = op.text
      if (op.frame) state.frame = op.frame
    }
    // A paragraph replacement resets its run content before later appends.
    if (op.op === 'set-paragraph' && typeof op.text === 'string' && state.text !== undefined) {
      const paragraphs = state.text.replace(/\r\n?/g, '\n').split('\n')
      if (Number.isInteger(op.paragraph) && op.paragraph >= 0 && op.paragraph < paragraphs.length) {
        paragraphs[op.paragraph] = op.text
        state.text = paragraphs.join('\n')
      }
    }
    // add-run appends to one paragraph, not to the end of the whole frame.
    // Follow the current name, including intervening native-shape renames.
    if (op.op === 'add-run' && typeof op.text === 'string' && state.text !== undefined) {
      const paragraphs = state.text.replace(/\r\n?/g, '\n').split('\n')
      const paragraph = op.paragraph
      if (Number.isInteger(paragraph) && paragraph >= 0 && paragraph < paragraphs.length) {
        paragraphs[paragraph] += op.text
        state.text = paragraphs.join('\n')
      }
    }
    if (op.op === 'set-image' && op.crop !== undefined) state.crop = op.crop
    if (op.op === 'set-shape' && typeof op.name === 'string') state.name = op.name
  }
  return state
}

export function checkDesignReadback(plan, patch, inspect, model = null, nativeCharts = null) {
  const issues = []
  const fail = (message) => issues.push({ severity: 'error', message })
  if (plan.patchHash !== designHash(patch)) fail('Patch hash does not match design plan')
  const expectedSlides = patch.ops.filter((o) => o.op === 'add-slide').length
  if (inspect.slides?.length !== expectedSlides) fail('Slide count differs from plan')
  for (const object of plan.objects) {
    const expectedState = readbackObjectState(object, patch)
    const matches =
      inspect.slides?.[object.slide]?.shapes?.filter((s) => s.name === expectedState.name) ?? []
    if (matches.length !== 1) {
      fail(`Expected exactly one ${expectedState.name}`)
      continue
    }
    const shape = matches[0]
    if (object.kind === 'add-chart' && shape.contentKind !== 'chart') {
      fail(`${object.name}: native chart missing`)
    }
    if (object.kind === 'add-table' && shape.contentKind !== 'table')
      fail(`${object.name}: native table missing`)
    if (object.kind === 'add-image') {
      if (shape.shapeType !== 'picture') fail(`${object.name}: native picture missing`)
      const crop = expectedState.crop ?? {}
      if (
        !shape.image?.crop ||
        ['left', 'right', 'top', 'bottom'].some(
          (key) =>
            !Number.isFinite(shape.image.crop[key]) ||
            Math.abs(shape.image.crop[key] - (crop[key] ?? 0)) > 0.00001,
        )
      )
        fail(`${object.name}: picture crop changed or is undisclosed`)
    }
    if (['add-text-box', 'add-shape', 'add-freeform'].includes(object.kind)) {
      const expected = expectedState.text
      const paragraphs = new Map()
      for (const fact of shape.fontFacts ?? []) {
        if (fact.scope === 'textRun' && typeof fact.text === 'string') {
          const index = fact.paragraph ?? 0
          paragraphs.set(index, (paragraphs.get(index) ?? '') + fact.text)
        }
      }
      const actualText = [...paragraphs]
        .sort(([a], [b]) => a - b)
        .map(([, text]) => text)
        .join('\n')
      if (expected !== undefined && expected.replace(/\r\n?/g, '\n') !== actualText) {
        fail(`${object.name}: text changed or was dropped`)
      }
      const frame = expectedState.frame
      for (const key of ['verticalAnchor', 'wordWrap'])
        if (frame?.[key] !== undefined && shape.textFrame?.[key] !== frame[key])
          fail(`${object.name}: ${key} text-frame setting changed`)
    }
    const actual = ['xEmu', 'yEmu', 'wEmu', 'hEmu'].map((k) => Number(shape.bbox?.[k]) / 914400)
    if (actual.some((v, i) => !Number.isFinite(v) || Math.abs(v - object.frame[i]) > 0.002)) {
      fail(`${object.name}: geometry changed`)
    }
  }
  const chartOps = patch.ops.filter((o) => o.op === 'add-chart')
  const tableOps = patch.ops.filter((o) => o.op === 'add-table')
  if (chartOps.length && !model) fail('Native chart data projection is required')
  if (tableOps.length && !model) fail('Native table cell projection is required')
  if (model) {
    for (const slide of inspect.slides ?? []) {
      const expected = tableOps.filter((o) => o.slide === slide.index)
      const actual =
        model.presentation?.slides?.[slide.index]?.elements?.filter((e) => e.kind === 'table') ?? []
      if (expected.length !== actual.length) fail(`Slide ${slide.index}: table count changed`)
      expected.forEach((op, i) => {
        const table = actual[i]?.table
        if (
          !table ||
          table.rows !== op.rows ||
          table.columns !== op.columns ||
          JSON.stringify(table.cells) !== JSON.stringify(op.data)
        )
          fail(`${op.name}: native table dimensions or cell text changed`)
      })
    }
    for (const slide of inspect.slides ?? []) {
      const expected = chartOps.filter((o) => o.slide === slide.index)
      const actual =
        model.presentation?.slides?.[slide.index]?.elements?.filter((e) => e.kind === 'chart') ?? []
      if (expected.length !== actual.length) {
        fail(`Slide ${slide.index}: chart count changed`)
        continue
      }
      expected.forEach((op, i) => {
        if (nativeCharts) {
          const state = readbackObjectState(
            { kind: 'add-chart', slide: op.slide, name: op.name },
            patch,
          )
          const matches = nativeCharts.filter((c) => c.slide === op.slide && c.name === state.name)
          if (matches.length !== 1 || !nativeChartMatches(op, matches[0]))
            fail(`${op.name}: native chart kind, categories, values or series semantics changed`)
          return
        }
        const chart = actual[i].chart
        if (
          !op.data?.series ||
          ['combo', 'scatter', 'bubble'].includes(op.kind) ||
          op.kind.endsWith('-3d')
        ) {
          fail(
            `${op.name}: native chart caches are required for ${op.kind}; JSON projection is incomplete`,
          )
          return
        }
        // The current JSON projection names the native c:doughnutChart family "ring".
        // Normalize only this verified alias; a pie or other family still fails closed.
        const expectedKind = op.kind === 'doughnut' ? 'ring' : op.kind
        if (chart.type !== expectedKind || chart.series.length !== op.data.series.length) {
          fail(`${op.name}: chart structure changed`)
          return
        }
        op.data.series.forEach((series, j) => {
          const read = chart.series[j]
          if (
            read.name !== series.name ||
            JSON.stringify(read.points.map((p) => p.x)) !== JSON.stringify(op.data.categories) ||
            JSON.stringify(read.points.map((p) => p.y)) !== JSON.stringify(series.values)
          )
            fail(`${op.name}: native chart categories, values or series name changed`)
        })
      })
    }
  }
  return {
    schemaVersion: 'pptx-nova-design-readback/v1',
    status: issues.length ? 'fail' : 'pass',
    checkedObjects: plan.objects.length,
    checkedCharts: chartOps.length,
    checkedTables: tableOps.length,
    issues,
    coverage: [
      'object identity',
      'plain text run content',
      'native chart presence',
      'geometry',
      'patch binding',
      ...(plan.objects.some((o) => o.kind === 'add-image')
        ? ['native picture presence, geometry and crop']
        : []),
      ...(model ? ['chart categories, series names and numeric values'] : []),
      ...(nativeCharts ? ['native chart cache families, all series and source data'] : []),
      ...(model && tableOps.length ? ['native table dimensions and every cell text'] : []),
    ],
    notVerified: [
      'complete chart XML/workbook equality',
      'effective theme inheritance',
      'pixel layout',
      'PowerPoint parity',
    ],
    visualReviewRequired: true,
  }
}
