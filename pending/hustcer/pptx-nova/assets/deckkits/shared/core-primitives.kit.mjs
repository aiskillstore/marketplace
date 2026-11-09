// core-primitives.kit.mjs — 几何安全 + op 生成（所有 DeckKit 共用）
// version: 0.1.0
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { DECKKIT_ROOT, deckkitSchemaPath } from './deckkit-paths.mjs'
import { addTablerIconPicture } from './icon-assets.kit.mjs'
import { inspectAnimationCorpus } from './animation-corpus.mjs'

export const SLIDE_W = 13.333
export const SLIDE_H = 7.5
export const BOUNDS_EPS = 0.002

export const nm = (s, base) => `S${s}_${base}`

export const parseFontPt = (v) => {
  if (typeof v === 'number' && Number.isFinite(v)) return v
  const m = String(v ?? '').match(/^([0-9]+(?:\.[0-9]+)?)pt$/i)
  return m ? Number.parseFloat(m[1]) : null
}

export const fontSizeValue = (pt) => {
  const r = Number(pt.toFixed(2))
  return `${Number.isInteger(r) ? r.toFixed(0) : r}pt`
}

export const withFontFloor = (font, floorPt = 9) => {
  if (!font || typeof font !== 'object') return font
  const cur = parseFontPt(font.size)
  if (cur === null || cur >= floorPt) return font
  return { ...font, size: fontSizeValue(floorPt) }
}

export const normalizeHex = (value) => {
  const hex = String(value ?? '')
    .replace(/^#/, '')
    .toUpperCase()
  return /^[0-9A-F]{6}$/.test(hex) ? hex : null
}

const channelToLinear = (ch) => {
  const v = ch / 255
  return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
}

const luminance = (value) => {
  const hex = normalizeHex(value)
  if (!hex) return null
  const r = channelToLinear(Number.parseInt(hex.slice(0, 2), 16))
  const g = channelToLinear(Number.parseInt(hex.slice(2, 4), 16))
  const b = channelToLinear(Number.parseInt(hex.slice(4, 6), 16))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

export const contrastRatio = (fg, bg) => {
  const fgL = luminance(fg)
  const bgL = luminance(bg)
  if (fgL === null || bgL === null) return 0
  const lighter = Math.max(fgL, bgL)
  const darker = Math.min(fgL, bgL)
  return (lighter + 0.05) / (darker + 0.05)
}

export const isDarkColor = (value) => {
  const lum = luminance(value)
  return lum !== null && lum < 0.35
}

export const readableTextOn = (background, preferred, candidates = []) => {
  const bg = normalizeHex(background)
  const pref = normalizeHex(preferred)
  const MIN_CONTRAST = 4.5
  if (!bg) return pref ?? '111827'
  if (pref && contrastRatio(pref, bg) >= MIN_CONTRAST) return pref
  for (const c of candidates.map(normalizeHex).filter(Boolean)) {
    if (contrastRatio(c, bg) >= MIN_CONTRAST) return c
  }
  return contrastRatio('111827', bg) >= contrastRatio('FFFFFF', bg) ? '111827' : 'FFFFFF'
}

export const assertWithinSlide = (name, x, y, w, h) => {
  if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) {
    throw new Error(`Invalid geometry ${name}: x=${x} y=${y} w=${w} h=${h}`)
  }
  if (
    x < -BOUNDS_EPS ||
    y < -BOUNDS_EPS ||
    x + w > SLIDE_W + BOUNDS_EPS ||
    y + h > SLIDE_H + BOUNDS_EPS
  ) {
    throw new Error(
      `OOB ${name}: x=${x} y=${y} w=${w} h=${h} right=${(x + w).toFixed(3)} bottom=${(y + h).toFixed(3)}`,
    )
  }
}

export const grid = (cols, gap = 0.3, startX = 0.7, contentW = SLIDE_W - startX * 2) => {
  const w = (contentW - gap * (cols - 1)) / cols
  return Array.from({ length: cols }, (_, i) => ({ x: startX + i * (w + gap), w }))
}

export const txH = (sizePt, lines = 1) => {
  const inches = (sizePt / 72) * 1.5 * lines
  return Number(inches.toFixed(2))
}

export const parseImageRatio = (value) => {
  const match = String(value ?? '')
    .trim()
    .match(/^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$/)
  if (!match) return null
  const width = Number(match[1])
  const height = Number(match[2])
  return width > 0 && height > 0 ? width / height : null
}

const roundImageMetric = (value) => Number(Number(value).toFixed(6))

const roundedImageRect = (x, y, w, h) => ({
  x: roundImageMetric(x),
  y: roundImageMetric(y),
  w: roundImageMetric(w),
  h: roundImageMetric(h),
})

const roundedCrop = (crop) => {
  if (!crop) return undefined
  const normalized = Object.fromEntries(
    Object.entries(crop).map(([key, value]) => [key, roundImageMetric(value)]),
  )
  return Object.values(normalized).some((value) => value > 0) ? normalized : undefined
}

export function fitImageRect(x, y, w, h, ratio, fitPolicy = 'contain') {
  assertWithinSlide('image-slot', x, y, w, h)
  const sourceRatio = parseImageRatio(ratio)
  if (!sourceRatio) {
    throw new Error(`image slot requires a valid source ratio, got "${ratio ?? ''}"`)
  }
  const policy = String(fitPolicy || 'contain')
  const boxRatio = w / h
  if (policy === 'cover' || policy === 'crop-safe') {
    if (sourceRatio > boxRatio) {
      const visible = boxRatio / sourceRatio
      const side = (1 - visible) / 2
      return { ...roundedImageRect(x, y, w, h), crop: roundedCrop({ left: side, right: side }) }
    }
    const visible = sourceRatio / boxRatio
    const side = (1 - visible) / 2
    return { ...roundedImageRect(x, y, w, h), crop: roundedCrop({ top: side, bottom: side }) }
  }
  if (policy !== 'contain' && policy !== 'no-crop') {
    throw new Error(`unsupported image fitPolicy "${policy}"`)
  }
  if (sourceRatio > boxRatio) {
    const fittedH = w / sourceRatio
    return roundedImageRect(x, y + (h - fittedH) / 2, w, fittedH)
  }
  const fittedW = h * sourceRatio
  return roundedImageRect(x + (w - fittedW) / 2, y, fittedW, h)
}

// --- Op builders ---
export function createOps(options = {}) {
  const ops = []
  const textboxDefaults = options.textbox ?? {}

  const shape = (s, name, kind, x, y, w, h) => {
    assertWithinSlide(name, x, y, w, h)
    ops.push({
      op: 'add-shape',
      slide: s,
      kind: kind,
      name,
      x: `${x}in`,
      y: `${y}in`,
      w: `${w}in`,
      h: `${h}in`,
    })
    return name
  }
  const fill = (s, name, color) =>
    ops.push({ op: 'set-shape', slide: s, shape: { name }, fill: { type: 'solid', color } })
  const noLine = (s, name) =>
    ops.push({ op: 'set-shape', slide: s, shape: { name }, line: { noLine: true } })
  const setLine = (s, name, color, width = '0.75pt') =>
    ops.push({ op: 'set-shape', slide: s, shape: { name }, line: { width, color } })

  const box = (s, name, kind, x, y, w, h, color) => {
    shape(s, name, kind, x, y, w, h)
    fill(s, name, color)
    noLine(s, name)
    return name
  }

  const card = (s, name, x, y, w, h, color, line) => {
    shape(s, name, 'rounded-rectangle', x, y, w, h)
    fill(s, name, color)
    if (line) setLine(s, name, line, '0.75pt')
    else noLine(s, name)
    return name
  }

  const textbox = (s, name, x, y, w, h) => {
    assertWithinSlide(name, x, y, w, h)
    ops.push({
      op: 'add-text-box',
      slide: s,
      name,
      x: `${x}in`,
      y: `${y}in`,
      w: `${w}in`,
      h: `${h}in`,
      ...textboxDefaults,
    })
    return name
  }

  const setText = (s, name, text) =>
    ops.push({ op: 'set-text-frame', slide: s, shape: { name }, text })

  const runFont = (s, name, font, paragraph = 0, run = 0) =>
    ops.push({
      op: 'set-run',
      slide: s,
      shape: { name },
      paragraph,
      run,
      font: withFontFloor(font),
    })

  const addRun = (s, name, paragraph, text, font) =>
    ops.push({
      op: 'add-run',
      slide: s,
      shape: { name },
      paragraph,
      text,
      ...(font ? { font: withFontFloor(font) } : {}),
    })

  const pAlign = (s, name, alignment, paragraph = 0) =>
    ops.push({ op: 'set-paragraph', slide: s, shape: { name }, paragraph, format: { alignment } })

  const textParagraphCount = (text) => {
    const value = String(text ?? '')
    return value.length === 0 ? 0 : value.split(/\r\n|\r|\n/).length
  }

  const tx = (s, name, x, y, w, h, text, font, align) => {
    textbox(s, name, x, y, w, h)
    setText(s, name, text)
    const n = textParagraphCount(text)
    for (let p = 0; p < n; p++) runFont(s, name, font, p)
    if (align) for (let p = 0; p < n; p++) pAlign(s, name, align, p)
    return name
  }

  const fillText = (s, name, text, font, align) => {
    setText(s, name, text)
    const n = textParagraphCount(text)
    for (let p = 0; p < n; p++) runFont(s, name, font, p)
    if (align) for (let p = 0; p < n; p++) pAlign(s, name, align, p)
  }

  const addSlide = (s, bg) => {
    ops.push({ op: 'add-slide', layout: 'blank' })
    if (bg) ops.push({ op: 'set-slide-background', slide: s, fill: { type: 'solid', color: bg } })
  }

  const addImage = (s, name, x, y, w, h, assetSource) => {
    assertWithinSlide(name, x, y, w, h)
    if (!assetSource || typeof assetSource !== 'object') {
      throw new Error(`Image ${name} requires an asset source`)
    }
    ops.push({
      op: 'add-image',
      slide: s,
      name,
      x: `${x}in`,
      y: `${y}in`,
      w: `${w}in`,
      h: `${h}in`,
      assetSource,
    })
    return name
  }

  const setImageCrop = (s, name, crop) => {
    if (!crop) return
    ops.push({ op: 'set-image', slide: s, shape: { name }, crop })
  }

  const icon = (s, name, iconName, x, y, w, h, options) =>
    addTablerIconPicture(ops, s, name, iconName, x, y, w, h, options)

  return {
    ops,
    shape,
    fill,
    noLine,
    setLine,
    box,
    card,
    textbox,
    setText,
    runFont,
    addRun,
    pAlign,
    tx,
    fillText,
    addSlide,
    addImage,
    setImageCrop,
    icon,
  }
}

// --- Content loading ---
export async function loadContent(path) {
  if (path.endsWith('.mjs') || path.endsWith('.js')) {
    const mod = await import(join(process.cwd(), path))
    return mod.default ?? mod
  }
  return JSON.parse(readFileSync(path, 'utf8'))
}

// --- Content validation ---
const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'))

export function loadCatalog() {
  return readJson(join(DECKKIT_ROOT, 'catalog.json'))
}

const loadSchema = (name) => readJson(join(DECKKIT_ROOT, 'schemas', name))

const schemaPath = (...parts) => join(DECKKIT_ROOT, 'schemas', ...parts)

function loadSlideSchema(deckkit, slideType) {
  if (deckkit) {
    const deckkitPath = deckkitSchemaPath(deckkit, slideType)
    if (existsSync(deckkitPath)) return readJson(deckkitPath)
  }
  const globalPath = schemaPath(`${slideType}.schema.json`)
  if (existsSync(globalPath)) return readJson(globalPath)
  return null
}

const makeIssue = (type, message, extra = {}) => ({ type, message, ...extra })

const makeFitDiagnostic = ({
  slideIndex,
  slideType,
  severity,
  code,
  path,
  value,
  limit,
  message,
  suggestedActions,
  blocking,
  details = {},
}) => ({
  slideIndex,
  slideType,
  severity,
  code,
  path,
  value,
  limit,
  message,
  suggestedActions,
  blocking: blocking ?? severity === 'error',
  ...(details && typeof details === 'object' && !Array.isArray(details) ? details : {}),
})

const countText = (value) => (typeof value === 'string' ? value.length : 0)

const arrayValue = (value) => (Array.isArray(value) ? value : null)

const tupleValue = (value, index) => (Array.isArray(value) ? value[index] : undefined)

const LATIN_TOKEN_RE = /[A-Za-z0-9][A-Za-z0-9._:/-]{8,}/g

function longestLatinToken(value, path) {
  let longest = null
  const visit = (node, nodePath) => {
    if (typeof node === 'string') {
      for (const token of node.match(LATIN_TOKEN_RE) ?? []) {
        if (!longest || token.length > longest.value.length) {
          longest = { value: token, path: nodePath, length: token.length }
        }
      }
      return
    }
    if (Array.isArray(node)) {
      node.forEach((item, i) => visit(item, `${nodePath}[${i}]`))
      return
    }
    if (node && typeof node === 'object') {
      for (const [key, item] of Object.entries(node)) {
        visit(item, `${nodePath}.${key}`)
      }
    }
  }
  visit(value, path)
  return longest
}

const checkType = (value, type) => {
  if (!type) return true
  if (Array.isArray(type)) return type.some((t) => checkType(value, t))
  if (type === 'array') return Array.isArray(value)
  if (type === 'object') return value !== null && typeof value === 'object' && !Array.isArray(value)
  return typeof value === type
}

const describeType = (type) => (Array.isArray(type) ? type.join('|') : type)

function validateValueAgainstSchema(value, schema, path, errors) {
  if (!schema) return

  if (schema.type && !checkType(value, schema.type)) {
    errors.push(
      makeIssue('field', `${path}: expected ${describeType(schema.type)}`, {
        path,
        expected: schema.type,
      }),
    )
    return
  }

  if (schema.enum && !schema.enum.includes(value)) {
    errors.push(
      makeIssue('field', `${path}: expected one of ${schema.enum.join(', ')}`, {
        path,
        expected: schema.enum,
        value,
      }),
    )
    return
  }

  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) {
      errors.push(
        makeIssue('field', `${path}: ${value.length} chars below min ${schema.minLength}`, {
          path,
          value: value.length,
          limit: schema.minLength,
        }),
      )
    }
    if (schema.maxLength !== undefined && value.length > schema.maxLength) {
      errors.push(
        makeIssue('field', `${path}: ${value.length} chars exceeds max ${schema.maxLength}`, {
          path,
          value: value.length,
          limit: schema.maxLength,
        }),
      )
    }
  }

  if (Array.isArray(value)) {
    validateArrayAgainstSchema(value, schema, path, errors)
    return
  }

  if (value && typeof value === 'object') {
    validateObjectAgainstSchema(value, schema, path, errors)
  }
}

function validateArrayAgainstSchema(value, schema, path, errors) {
  if (schema.minItems !== undefined && value.length < schema.minItems) {
    errors.push(
      makeIssue('field', `${path}: ${value.length} items below min ${schema.minItems}`, {
        path,
        value: value.length,
        limit: schema.minItems,
      }),
    )
  }
  if (schema.maxItems !== undefined && value.length > schema.maxItems) {
    errors.push(
      makeIssue('field', `${path}: ${value.length} items exceeds max ${schema.maxItems}`, {
        path,
        value: value.length,
        limit: schema.maxItems,
      }),
    )
  }

  const itemSchema = schema.items
  if (!itemSchema) return
  if (Array.isArray(itemSchema)) {
    itemSchema.forEach((tupleSchema, i) => {
      if (i < value.length)
        validateValueAgainstSchema(value[i], tupleSchema, `${path}[${i}]`, errors)
    })
    return
  }
  value.forEach((item, i) => validateValueAgainstSchema(item, itemSchema, `${path}[${i}]`, errors))
}

function validateObjectAgainstSchema(value, schema, path, errors) {
  if (!schema || !schema.properties || !value || typeof value !== 'object') return

  for (const req of schema.required ?? []) {
    if (!(req in value)) {
      errors.push(makeIssue('field', `${path}: missing required field "${req}"`, { path }))
    }
  }

  if (schema.additionalProperties === false) {
    for (const key of Object.keys(value)) {
      if (!(key in schema.properties)) {
        errors.push(
          makeIssue('field', `${path}: unknown field "${key}"`, { path: `${path}.${key}` }),
        )
      }
    }
  }

  for (const [key, propSchema] of Object.entries(schema.properties)) {
    if (!(key in value)) continue
    const fieldPath = `${path}.${key}`
    validateValueAgainstSchema(value[key], propSchema, fieldPath, errors)
  }
}

function pushFitLimitDiagnostic({
  errors,
  warnings,
  fitDiagnostics,
  ignoreSoftLimits,
  slideIndex,
  slideType,
  field,
  path,
  value,
  softLimit,
  hardLimit,
  unit,
  codeBase,
  suggestedActions,
}) {
  if (value === null || value === undefined) return
  if (hardLimit !== undefined && value > hardLimit) {
    const message = `${path}: ${value} ${unit} exceeds hard limit ${hardLimit}`
    const diagnostic = makeFitDiagnostic({
      slideIndex,
      slideType,
      severity: 'error',
      code: `${codeBase}.hardLimit`,
      path,
      value,
      limit: hardLimit,
      message,
      suggestedActions,
    })
    fitDiagnostics.push(diagnostic)
    errors.push(makeIssue('fit', message, { path, field, diagnostic }))
  } else if (softLimit !== undefined && value > softLimit && !ignoreSoftLimits) {
    const message = `${path}: ${value} ${unit} exceeds soft limit ${softLimit}`
    const diagnostic = makeFitDiagnostic({
      slideIndex,
      slideType,
      severity: 'warning',
      code: `${codeBase}.softLimit`,
      path,
      value,
      limit: softLimit,
      message,
      suggestedActions,
    })
    fitDiagnostics.push(diagnostic)
    warnings.push(makeIssue('fit', message, { path, field, diagnostic }))
  }
}

function slideValidationContext({
  slide,
  slideIndex,
  soft,
  hard,
  errors,
  warnings,
  fitDiagnostics,
  ignoreSoftLimits,
  mode,
}) {
  return {
    slide,
    data: slide.data ?? {},
    slideIndex,
    slideType: slide.type,
    prefix: `slides[${slideIndex}].data`,
    soft,
    hard,
    errors,
    warnings,
    fitDiagnostics,
    ignoreSoftLimits,
    mode,
  }
}

function pushLimit(ctx, config) {
  pushFitLimitDiagnostic({
    errors: ctx.errors,
    warnings: ctx.warnings,
    fitDiagnostics: ctx.fitDiagnostics,
    ignoreSoftLimits: ctx.ignoreSoftLimits,
    slideIndex: ctx.slideIndex,
    slideType: ctx.slideType,
    ...config,
  })
}

function pushTextLimit(ctx, field, { softLimit, hardLimit, codeBase, suggestedActions }) {
  pushLimit(ctx, {
    field,
    path: `${ctx.prefix}.${field}`,
    value: countText(ctx.data[field]),
    softLimit,
    hardLimit,
    unit: 'chars',
    codeBase,
    suggestedActions,
  })
}

function pushArrayLimit(ctx, field, { value, softLimit, hardLimit, codeBase, suggestedActions }) {
  pushLimit(ctx, {
    field,
    path: `${ctx.prefix}.${field}`,
    value: value?.length,
    softLimit,
    hardLimit,
    unit: 'items',
    codeBase,
    suggestedActions,
  })
}

function checkCommonTitle(ctx, codeBase = `${ctx.slideType}.title`) {
  pushTextLimit(ctx, 'title', {
    softLimit: ctx.soft.titleMaxChars,
    hardLimit: ctx.hard.titleMaxChars,
    codeBase,
    suggestedActions: ['shorten-copy', 'split-title', 'switch-layout'],
  })
}

function checkHeroSlide(ctx) {
  checkCommonTitle(ctx, 'hero.title')
  pushTextLimit(ctx, 'sub', {
    softLimit: 90,
    hardLimit: 150,
    codeBase: 'hero.subtitle',
    suggestedActions: ['shorten-copy', 'move-copy-to-body-slide', 'split-slide'],
  })
  pushTextLimit(ctx, 'tag', {
    softLimit: 96,
    hardLimit: 140,
    codeBase: 'hero.tag',
    suggestedActions: ['shorten-copy', 'move-copy-to-notes'],
  })
}

function checkKpiRowSlide(ctx) {
  checkCommonTitle(ctx, 'kpi.title')
  const items = arrayValue(ctx.data.items)
  pushArrayLimit(ctx, 'items', {
    value: items,
    softLimit: Math.min(ctx.soft.kpisMax ?? 4, 4),
    hardLimit: 4,
    codeBase: 'kpi.items',
    suggestedActions: ['split-slide', 'switch-layout', 'remove-item'],
  })
  items?.forEach((item, i) => {
    pushLimit(ctx, {
      field: 'itemBody',
      path: `${ctx.prefix}.items[${i}][3]`,
      value: countText(tupleValue(item, 3)),
      softLimit: 72,
      hardLimit: 120,
      unit: 'chars',
      codeBase: 'kpi.itemBody',
      suggestedActions: ['shorten-copy', 'split-item', 'move-detail-to-notes'],
    })
  })
}

function checkMultiCardSlide(ctx) {
  checkCommonTitle(ctx, 'cards.title')
  const cards = arrayValue(ctx.data.cards)
  pushArrayLimit(ctx, 'cards', {
    value: cards,
    softLimit: ctx.soft.cardsMax,
    hardLimit: ctx.hard.cardsMax,
    codeBase: 'cards.count',
    suggestedActions: ['split-slide', 'switch-layout', 'remove-card'],
  })
  cards?.forEach((card, i) => {
    pushLimit(ctx, {
      field: 'cardTitle',
      path: `${ctx.prefix}.cards[${i}][2]`,
      value: countText(tupleValue(card, 2)),
      softLimit: 24,
      hardLimit: 42,
      unit: 'chars',
      codeBase: 'cards.titleText',
      suggestedActions: ['shorten-copy', 'split-card-title'],
    })
    const items = tupleValue(card, 3)
    pushLimit(ctx, {
      field: 'cardItems',
      path: `${ctx.prefix}.cards[${i}][3]`,
      value: Array.isArray(items) ? items.length : undefined,
      softLimit: ctx.soft.bulletsPerCardMax,
      hardLimit: ctx.hard.bulletsPerCardMax,
      unit: 'items',
      codeBase: 'cards.items',
      suggestedActions: ['shorten-copy', 'split-card', 'remove-bullet'],
    })
  })
}

function checkBenchmarkSlide(ctx) {
  checkCommonTitle(ctx, 'table.title')
  const rows = arrayValue(ctx.data.tableRows ?? ctx.data.rows)
  pushArrayLimit(ctx, ctx.data.tableRows ? 'tableRows' : 'rows', {
    value: rows,
    softLimit: ctx.soft.tableRowsMax,
    hardLimit: ctx.hard.tableRowsMax,
    codeBase: 'table.rows',
    suggestedActions: ['split-slide', 'switch-layout', 'shorten-table'],
  })
  if (rows?.[0]) {
    pushLimit(ctx, {
      field: 'tableColumns',
      path: `${ctx.prefix}.${ctx.data.tableRows ? 'tableRows' : 'rows'}[0]`,
      value: Array.isArray(rows[0]) ? rows[0].length : undefined,
      softLimit: 4,
      hardLimit: 5,
      unit: 'columns',
      codeBase: 'table.columns',
      suggestedActions: ['remove-column', 'split-table', 'switch-layout'],
    })
  }
}

function checkTimelineSlide(ctx) {
  checkCommonTitle(ctx, 'timeline.title')
  const steps = arrayValue(ctx.data.steps)
  pushArrayLimit(ctx, 'steps', {
    value: steps,
    softLimit: ctx.soft.timelineStepsMax,
    hardLimit: ctx.hard.timelineStepsMax,
    codeBase: 'timeline.steps',
    suggestedActions: ['split-slide', 'shorten-copy', 'remove-step'],
  })
  steps?.forEach((step, i) => {
    pushLimit(ctx, {
      field: 'stepDescription',
      path: `${ctx.prefix}.steps[${i}][3]`,
      value: countText(tupleValue(step, 3)),
      softLimit: 32,
      hardLimit: 60,
      unit: 'chars',
      codeBase: 'timeline.stepDescription',
      suggestedActions: ['shorten-copy', 'split-step', 'move-detail-to-notes'],
    })
  })
}

function checkAskSlide(ctx) {
  checkCommonTitle(ctx, 'ask.title')
  pushTextLimit(ctx, 'sub', {
    softLimit: 80,
    hardLimit: 130,
    codeBase: 'ask.subtitle',
    suggestedActions: ['shorten-copy', 'split-slide'],
  })
  const asks = arrayValue(ctx.data.asks)
  pushArrayLimit(ctx, 'asks', {
    value: asks,
    softLimit: 4,
    hardLimit: 5,
    codeBase: 'ask.items',
    suggestedActions: ['split-slide', 'remove-ask', 'switch-layout'],
  })
  asks?.forEach((ask, i) => {
    pushLimit(ctx, {
      field: 'askDescription',
      path: `${ctx.prefix}.asks[${i}][2]`,
      value: countText(tupleValue(ask, 2)),
      softLimit: 30,
      hardLimit: 56,
      unit: 'chars',
      codeBase: 'ask.description',
      suggestedActions: ['shorten-copy', 'split-ask', 'move-detail-to-notes'],
    })
  })
}

function checkGenericSlideDensity(ctx) {
  checkCommonTitle(ctx)
}

function checkTextTokenRisk(ctx) {
  const longest = longestLatinToken(ctx.data, ctx.prefix)
  pushLimit(ctx, {
    field: 'longLatinToken',
    path: longest?.path ?? ctx.prefix,
    value: longest?.length,
    softLimit: 34,
    hardLimit: 52,
    unit: 'chars',
    codeBase: 'text.longLatinToken',
    suggestedActions: ['insert-break-opportunity', 'shorten-token', 'switch-layout'],
  })
}

const SLIDE_FIT_CHECKERS = {
  heroSlide: checkHeroSlide,
  kpiRowSlide: checkKpiRowSlide,
  multiCardSlide: checkMultiCardSlide,
  benchmarkSlide: checkBenchmarkSlide,
  timelineSlide: checkTimelineSlide,
  askSlide: checkAskSlide,
}

function checkSlideDensity(args) {
  const ctx = slideValidationContext(args)
  const check = SLIDE_FIT_CHECKERS[ctx.slideType] ?? checkGenericSlideDensity
  check(ctx)
  checkTextTokenRisk(ctx)
}

function catalogEntryForDeckkit(deckkit) {
  if (!deckkit) return null
  try {
    return loadCatalog().entries.find((entry) => entry.id === deckkit) ?? null
  } catch {
    return null
  }
}

function slotBudgetSeverity(config, mode) {
  if (mode === 'delivery' && config.deliverySeverity) return config.deliverySeverity
  return config.severity ?? 'warning'
}

function pushSlotBudgetIssue(ctx, budget, path, code, value, limit, message) {
  const severity = slotBudgetSeverity(budget, ctx.mode)
  const diagnostic = makeFitDiagnostic({
    slideIndex: ctx.slideIndex,
    slideType: ctx.slideType,
    severity,
    code,
    path,
    value,
    limit,
    message,
    suggestedActions: budget.suggestedActions ?? ['shorten-copy', 'split-slide', 'switch-layout'],
  })
  ctx.fitDiagnostics.push(diagnostic)
  const issue = makeIssue('fit', message, { path, field: path.split('.').pop(), diagnostic })
  if (severity === 'error') ctx.errors.push(issue)
  else ctx.warnings.push(issue)
}

const SLOT_BUDGET_LINE_HEIGHT = 1.2

function finitePositiveNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) && n > 0 ? n : null
}

function budgetLengthPt(budget, ptKey, inKey) {
  const pt = finitePositiveNumber(budget?.[ptKey])
  if (pt !== null) return pt
  const inches = finitePositiveNumber(budget?.[inKey])
  return inches !== null ? inches * 72 : null
}

export function summarizeSlotBudgetFit(budget = {}) {
  const fontPt = finitePositiveNumber(budget.fontPt ?? budget.fontSizePt)
  const widthPt = budgetLengthPt(budget, 'widthPt', 'widthIn')
  const heightPt = budgetLengthPt(budget, 'heightPt', 'heightIn')
  const lineHeight = finitePositiveNumber(budget.lineHeight) ?? SLOT_BUDGET_LINE_HEIGHT
  const maxLines = finitePositiveNumber(budget.maxLines)
  const cjkCharsPerLine =
    fontPt !== null && widthPt !== null ? Math.max(1, Math.floor(widthPt / fontPt)) : null
  const heightSafeLines =
    fontPt !== null && heightPt !== null
      ? Math.max(0, Math.floor(heightPt / (fontPt * lineHeight)))
      : null
  const safeLines =
    maxLines !== null && heightSafeLines !== null
      ? Math.min(maxLines, heightSafeLines)
      : (heightSafeLines ?? maxLines)
  return {
    fontPt,
    widthPt,
    heightPt,
    lineHeight,
    maxLines,
    cjkCharsPerLine,
    heightSafeLines,
    safeLines,
  }
}

export function estimateSlotBudgetTextFit(value, budget = {}) {
  const text = Array.isArray(value)
    ? value.map((item) => String(item ?? '')).join('\n')
    : String(value ?? '')
  const fit = summarizeSlotBudgetFit(budget)
  if (!fit.fontPt || !fit.widthPt)
    return { ...fit, text, estimatedLines: null, neededHeightPt: null }
  const hardLines = text.split('\n').length
  const estimatedLines = Math.max(
    hardLines,
    estimateQualityLineCount(text, fit.fontPt, Math.max(1, fit.widthPt)),
  )
  return {
    ...fit,
    text,
    hardLines,
    estimatedLines,
    neededHeightPt: estimatedLines * fit.fontPt * fit.lineHeight,
  }
}

function checkSlotBudgetValue(ctx, value, schema, path) {
  const budget = schema?.['x-slotBudget']
  if (!budget || value === null || value === undefined) return
  if (typeof value === 'string' || Array.isArray(value)) {
    const text = Array.isArray(value) ? value.map((item) => String(item ?? '')).join('\n') : value
    if (budget.maxChars !== undefined && text.length > budget.maxChars) {
      pushSlotBudgetIssue(
        ctx,
        budget,
        path,
        'slotBudget.chars.limit',
        text.length,
        budget.maxChars,
        `${path}: ${text.length} chars exceeds budget ${budget.maxChars}`,
      )
    }
    const textFit = estimateSlotBudgetTextFit(text, budget)
    const estLines = textFit.estimatedLines
    if (estLines !== null && budget.maxLines !== undefined && estLines > budget.maxLines) {
      pushSlotBudgetIssue(
        ctx,
        budget,
        path,
        'slotBudget.lines.limit',
        estLines,
        budget.maxLines,
        `${path}: estimated ${estLines} lines exceeds budget ${budget.maxLines}`,
      )
    }
    if (
      textFit.neededHeightPt !== null &&
      textFit.heightPt !== null &&
      textFit.neededHeightPt > textFit.heightPt
    ) {
      pushSlotBudgetIssue(
        ctx,
        budget,
        path,
        'slotBudget.height.limit',
        Number(textFit.neededHeightPt.toFixed(2)),
        Number(textFit.heightPt.toFixed(2)),
        `${path}: estimated ${Number(textFit.neededHeightPt.toFixed(2))}pt text height exceeds budget ${Number(textFit.heightPt.toFixed(2))}pt`,
      )
    }
  }
  if (Array.isArray(value) && budget.maxItems !== undefined && value.length > budget.maxItems) {
    pushSlotBudgetIssue(
      ctx,
      budget,
      path,
      'slotBudget.items.limit',
      value.length,
      budget.maxItems,
      `${path}: ${value.length} items exceeds budget ${budget.maxItems}`,
    )
  }
}

function checkSlotBudgets(ctx, value, schema, path) {
  if (!schema || value === null || value === undefined) return
  checkSlotBudgetValue(ctx, value, schema, path)
  if (Array.isArray(value)) {
    const itemSchema = schema.items
    if (Array.isArray(itemSchema)) {
      value.forEach((item, index) => {
        const tupleSchema = itemSchema[index]
        if (tupleSchema) checkSlotBudgets(ctx, item, tupleSchema, `${path}[${index}]`)
      })
      return
    }
    if (itemSchema) {
      value.forEach((item, index) => checkSlotBudgets(ctx, item, itemSchema, `${path}[${index}]`))
    }
    return
  }
  if (value && typeof value === 'object' && schema.properties) {
    for (const [key, childSchema] of Object.entries(schema.properties)) {
      if (key in value) checkSlotBudgets(ctx, value[key], childSchema, `${path}.${key}`)
    }
  }
}

function pathValue(root, path) {
  if (!path) return undefined
  return String(path)
    .split('.')
    .reduce((cur, part) => (cur === null || cur === undefined ? undefined : cur[part]), root)
}

function hasContractValue(root, path) {
  const value = pathValue(root, path)
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  if (typeof value === 'object') return Object.keys(value).length > 0
  return true
}

function contractPathGroup(value) {
  if (Array.isArray(value)) return value
  if (typeof value === 'string') return [value]
  if (value && typeof value === 'object') return value.paths ?? value.anyOf ?? []
  return []
}

// 判定一个 item 级标签是否只是重复了版式自动生成的序号（如 steps[].year 填 "01"/"step 2"），
// 渲染层用它去重，validate 层用它提示作者改填语义标签。两侧共用同一判定，避免口径漂移。
const AUTO_INDEX_PREFIXES = new Set(['no', 'n', 'p', 'step', 'phase', 'stage', '第', '步', '第步'])

export function labelDuplicatesAutoIndex(value, index) {
  const str = String(value ?? '')
    .trim()
    .toLowerCase()
  if (!str) return false
  const digits = str.replace(/\D+/g, '')
  if (!digits || Number.parseInt(digits, 10) !== index + 1) return false
  const rest = str.replace(/[0-9\s·.\-_/]+/g, '')
  return rest === '' || AUTO_INDEX_PREFIXES.has(rest)
}

function pushValidationGateIssue({
  errors,
  warnings,
  fitDiagnostics,
  severity,
  type,
  slideIndex = null,
  slideType = null,
  code,
  path,
  value = null,
  limit = null,
  message,
  suggestedActions = [],
  details = {},
}) {
  const diagnostic = makeFitDiagnostic({
    slideIndex,
    slideType,
    severity,
    code,
    path,
    value,
    limit,
    message,
    suggestedActions,
    details,
  })
  fitDiagnostics.push(diagnostic)
  const issue = makeIssue(type, message, { path, diagnostic })
  if (severity === 'error') errors.push(issue)
  else warnings.push(issue)
}

function diversityContext(gate, content, groups) {
  const configuredGroups =
    gate?.groups && typeof gate.groups === 'object' && !Array.isArray(gate.groups)
      ? gate.groups
      : {}
  const groupMembers = Object.fromEntries(
    Object.entries(configuredGroups).map(([group, members]) => [
      group,
      Array.isArray(members) ? [...members] : [],
    ]),
  )
  const slideGroups = (content?.slides ?? []).map((slide, index) => ({
    index,
    slideType: slide?.type ?? null,
    group: groups[index] ?? '(unmapped)',
  }))
  for (const item of slideGroups) {
    const members = groupMembers[item.group] ?? []
    if (item.slideType && !members.includes(item.slideType)) members.push(item.slideType)
    groupMembers[item.group] = members
  }

  const configuredNames = Object.keys(configuredGroups)
  const usedSet = new Set(slideGroups.map((item) => item.group))
  const usedGroups = [
    ...configuredNames.filter((group) => usedSet.has(group)),
    ...[...usedSet].filter((group) => !configuredNames.includes(group)),
  ]
  const missingGroups = configuredNames.filter((group) => !usedSet.has(group))
  const excludedGroups = Array.isArray(gate?.excludeGroupsFromUnique)
    ? [...gate.excludeGroupsFromUnique]
    : []
  const countedGroups = usedGroups.filter((group) => !excludedGroups.includes(group))

  return {
    usedGroups,
    missingGroups,
    groupMembers,
    slideGroups,
    excludedGroups,
    countedGroups,
  }
}

function diversityContextSummary(context) {
  const used = context.usedGroups.length > 0 ? context.usedGroups.join(', ') : '(none)'
  const missing = context.missingGroups.length > 0 ? context.missingGroups.join(', ') : '(none)'
  const members = Object.entries(context.groupMembers)
    .map(([group, slideTypes]) => `${group}=[${slideTypes.join(', ') || '(none)'}]`)
    .join('; ')
  return `used groups: ${used}; missing groups: ${missing}; group members: ${members || '(none)'}`
}

function validationSeverity(config = {}, mode = 'draft') {
  if (mode === 'delivery' && config.deliverySeverity) return config.deliverySeverity
  return config.severity ?? 'warning'
}

function checkSlideLayoutContract({
  entry,
  slide,
  slideIndex,
  mode,
  errors,
  warnings,
  fitDiagnostics,
}) {
  const contract = entry?.layoutContract
  if (!contract) return
  const slideContract = contract.slideTypes?.[slide.type]
  if (!slideContract) return
  const basePath = `slides[${slideIndex}]`
  const severity = validationSeverity({ ...contract, ...slideContract }, mode)

  for (const slot of slideContract.requiredSlots ?? []) {
    const slotPath = typeof slot === 'string' ? slot : slot.path
    if (!hasContractValue(slide, slotPath)) {
      const slotHint =
        (typeof slot === 'object' && slot !== null && slot.hint) ||
        slideContract.slotHints?.[slotPath] ||
        contract.slotHints?.[slotPath] ||
        ''
      pushValidationGateIssue({
        errors,
        warnings,
        fitDiagnostics,
        severity,
        type: 'layout-contract',
        slideIndex,
        slideType: slide.type,
        code: 'layout.requiredSlot.missing',
        path: `${basePath}.${slotPath}`,
        value: null,
        limit: 'non-empty',
        message: `${basePath}: required layout slot "${slotPath}" is missing or empty${
          slotHint ? ` — ${slotHint}` : ''
        }`,
        suggestedActions: ['fill-required-slot', 'switch-slide-type', 'split-slide'],
      })
    }
  }

  for (const group of slideContract.requiredAny ?? []) {
    const paths = contractPathGroup(group)
    if (paths.length === 0) continue
    if (paths.some((slotPath) => hasContractValue(slide, slotPath))) continue

    const groupLabel =
      group && typeof group === 'object' && !Array.isArray(group) && group.label
        ? group.label
        : paths.join(' | ')
    const groupSeverity =
      group &&
      typeof group === 'object' &&
      !Array.isArray(group) &&
      (group.severity || group.deliverySeverity)
        ? validationSeverity(group, mode)
        : severity
    pushValidationGateIssue({
      errors,
      warnings,
      fitDiagnostics,
      severity: groupSeverity,
      type: 'layout-contract',
      slideIndex,
      slideType: slide.type,
      code: 'layout.requiredAny.missing',
      path: `${basePath}.${paths.join('|')}`,
      value: null,
      limit: groupLabel,
      message: `${basePath}: one of "${groupLabel}" is required by the layout contract`,
      suggestedActions: ['fill-one-required-slot', 'switch-slide-type', 'split-slide'],
    })
  }

  const allowedLayoutIds = slideContract.allowedLayoutIds ?? []
  for (const slot of slideContract.autoIndexSlots ?? []) {
    const slotPath = typeof slot === 'string' ? slot : slot?.path
    if (!slotPath) continue
    const match = slotPath.match(/^(.+)\[\]\.([A-Za-z0-9_]+)$/)
    if (!match) continue
    const items = pathValue(slide, match[1])
    if (!Array.isArray(items)) continue
    const offenders = []
    items.forEach((item, idx) => {
      const value = item?.[match[2]]
      if (labelDuplicatesAutoIndex(value, idx)) {
        offenders.push(`${match[1]}[${idx}].${match[2]}="${value}"`)
      }
    })
    if (offenders.length === 0) continue
    const slotHint =
      (typeof slot === 'object' && slot !== null && slot.hint) ||
      slideContract.slotHints?.[slotPath] ||
      contract.slotHints?.[slotPath] ||
      ''
    pushValidationGateIssue({
      errors,
      warnings,
      fitDiagnostics,
      severity: 'warning',
      type: 'layout-contract',
      slideIndex,
      slideType: slide.type,
      code: 'layout.autoIndexSlot.duplicate',
      path: `${basePath}.${slotPath}`,
      value: offenders.join(', '),
      limit: 'semantic-label',
      message: `${basePath}: "${slotPath}" duplicates the layout's auto-generated index (${offenders.join(
        ', ',
      )}); the renderer will suppress the duplicate label${slotHint ? ` — ${slotHint}` : ''}`,
      suggestedActions: ['use-semantic-label', 'drop-redundant-index'],
    })
  }

  if (slide.layoutId && allowedLayoutIds.length > 0 && !allowedLayoutIds.includes(slide.layoutId)) {
    pushValidationGateIssue({
      errors,
      warnings,
      fitDiagnostics,
      severity,
      type: 'layout-contract',
      slideIndex,
      slideType: slide.type,
      code: 'layout.layoutId.unregistered',
      path: `${basePath}.layoutId`,
      value: slide.layoutId,
      limit: allowedLayoutIds.join('|'),
      message: `${basePath}: layoutId "${slide.layoutId}" is not registered for ${slide.type}`,
      suggestedActions: ['use-registered-layout-id', 'remove-layout-id', 'extend-deckkit-contract'],
    })
  }

  const customOpsPolicy = slideContract.customOps ?? contract.customOps ?? {}
  if (
    Array.isArray(slide.customOps) &&
    slide.customOps.length > 0 &&
    customOpsPolicy.allowed === false
  ) {
    pushValidationGateIssue({
      errors,
      warnings,
      fitDiagnostics,
      severity: validationSeverity(customOpsPolicy, mode),
      type: 'layout-contract',
      slideIndex,
      slideType: slide.type,
      code: 'layout.customOps.disallowed',
      path: `${basePath}.customOps`,
      value: slide.customOps.length,
      limit: 0,
      message: `${basePath}: customOps are disabled by the DeckKit layout contract`,
      suggestedActions: [
        'move-change-into-deckkit',
        'choose-supported-slide-type',
        'request-studio-override',
      ],
    })
  }
}

function checkSlideAssetSlots({
  entry,
  slide,
  slideIndex,
  mode,
  errors,
  warnings,
  fitDiagnostics,
}) {
  const contract = entry?.layoutContract
  const slideContract = contract?.slideTypes?.[slide.type]
  const assetSlots = slideContract?.assetSlots
  if (
    !assetSlots ||
    typeof assetSlots !== 'object' ||
    Array.isArray(assetSlots) ||
    !slide?.imageSlots ||
    typeof slide.imageSlots !== 'object' ||
    Array.isArray(slide.imageSlots)
  ) {
    return
  }

  const basePath = `slides[${slideIndex}]`
  for (const [slotId, assetId] of Object.entries(slide.imageSlots)) {
    const slot = assetSlots[slotId]
    if (!slot || slot.acceptsAsset !== false) continue
    const severity = validationSeverity({ ...contract, ...slot }, mode)
    const placeholderBehavior = slot.placeholderBehavior ?? 'placeholder shell'
    pushValidationGateIssue({
      errors,
      warnings,
      fitDiagnostics,
      severity,
      type: 'layout-contract',
      slideIndex,
      slideType: slide.type,
      code: 'layout.assetSlot.unsupported',
      path: `${basePath}.imageSlots.${slotId}`,
      value: assetId,
      limit: 'placeholder-only',
      message: `${basePath}: asset slot "${slotId}" is placeholder-only and does not accept asset "${assetId}"; it renders a ${placeholderBehavior}. Remove the imageSlots entry, choose another slide type, or extend the DeckKit contract.`,
      suggestedActions: [
        'remove-unsupported-image-slot',
        'switch-slide-type',
        'extend-deckkit-asset-contract',
      ],
      details: {
        assetSlot: {
          id: slotId,
          ...slot,
        },
      },
    })
  }
}

function slideGroupFor(type, diversityGate) {
  for (const [group, types] of Object.entries(diversityGate?.groups ?? {})) {
    if (Array.isArray(types) && types.includes(type)) return group
  }
  return type
}

function matchingThreshold(thresholds = [], slideCount) {
  return thresholds
    .filter((item) => slideCount >= (item.minSlides ?? 0))
    .sort((a, b) => (b.minSlides ?? 0) - (a.minSlides ?? 0))[0]
}

function checkDeckDiversity({ entry, content, mode, errors, warnings, fitDiagnostics }) {
  const gate = entry?.diversityGate
  if (!gate || !Array.isArray(content?.slides)) return
  const { coveredSlides } = inspectAnimationCorpus(content)
  const groups = content.slides.map((slide, index) =>
    coveredSlides.has(index) ? null : slideGroupFor(slide?.type, gate),
  )
  const context = diversityContext(gate, content, groups)
  const contextSummary = diversityContextSummary(context)
  const slideCount = groups.filter((group) => group !== null).length
  const threshold = matchingThreshold(gate.thresholds, slideCount)
  const severity = validationSeverity(gate, mode)

  if (threshold?.minUniqueGroups) {
    const excluded = new Set(gate.excludeGroupsFromUnique ?? [])
    const unique = new Set(groups.filter((group) => group !== null && !excluded.has(group)))
    if (unique.size < threshold.minUniqueGroups) {
      pushValidationGateIssue({
        errors,
        warnings,
        fitDiagnostics,
        severity,
        type: 'diversity',
        code: 'diversity.uniqueGroups.tooLow',
        path: 'slides',
        value: unique.size,
        limit: threshold.minUniqueGroups,
        message: `deck uses ${unique.size} counted layout group(s); ${threshold.minUniqueGroups} required for ${slideCount} slides (${contextSummary})`,
        suggestedActions: [
          'vary-slide-types',
          'insert-data-or-compare-slide',
          'split-repeated-card-pages',
        ],
        details: context,
      })
    }
  }

  for (const required of threshold?.requiredGroups ?? []) {
    if (!groups.includes(required)) {
      pushValidationGateIssue({
        errors,
        warnings,
        fitDiagnostics,
        severity,
        type: 'diversity',
        code: 'diversity.requiredGroup.missing',
        path: 'slides',
        value: groups,
        limit: required,
        message: `deck is missing required layout group "${required}" for ${slideCount} slides (${contextSummary})`,
        suggestedActions: ['add-required-slide-group', 'remap-outline-to-supported-slide-type'],
        details: context,
      })
    }
  }

  const maxRun = gate.maxConsecutiveSameGroup
  if (maxRun) {
    let start = 0
    for (let i = 1; i <= groups.length; i += 1) {
      if (groups[i] === groups[start]) continue
      const runLength = i - start
      if (groups[start] !== null && runLength > maxRun) {
        pushValidationGateIssue({
          errors,
          warnings,
          fitDiagnostics,
          severity,
          type: 'diversity',
          slideIndex: start,
          slideType: content.slides[start]?.type ?? null,
          code: 'diversity.consecutiveGroup.tooLong',
          path: `slides[${start}..${i - 1}]`,
          value: runLength,
          limit: maxRun,
          message: `slides ${start + 1}-${i} repeat layout group "${groups[start]}" ${runLength} times (${contextSummary})`,
          suggestedActions: [
            'alternate-layout-group',
            'merge-or-split-repeated-pages',
            'insert-breathing-slide',
          ],
          details: context,
        })
      }
      start = i
    }
  }
}

export function validateContent(
  content,
  { deckkit, throwOnError = false, ignoreSoftLimits = false, mode = 'draft' } = {},
) {
  const catalog = loadCatalog()
  const contentSchema = loadSchema('content.schema.json')
  const requestedDeckkit = deckkit || content?.meta?.deckkit
  const entry = catalog.entries.find((e) => e.id === requestedDeckkit)
  const errors = []
  const warnings = []
  const fitDiagnostics = []
  errors.push(...inspectAnimationCorpus(content).errors)

  if (!content || typeof content !== 'object') {
    errors.push(makeIssue('structure', 'Content must be an object'))
  }
  if (!content?.meta || typeof content.meta !== 'object') {
    errors.push(makeIssue('structure', 'Missing or invalid "meta" field', { path: 'meta' }))
  }
  if (!Array.isArray(content?.slides) || content.slides.length === 0) {
    errors.push(makeIssue('structure', '"slides" must be a non-empty array', { path: 'slides' }))
  }

  if (errors.length === 0) {
    validateObjectAgainstSchema(content.meta, contentSchema.properties.meta, 'meta', errors)
  }

  if (!content?.meta?.deckkit) {
    errors.push(makeIssue('meta', 'meta.deckkit is required', { path: 'meta.deckkit' }))
  }
  if (!entry) {
    errors.push(
      makeIssue('meta', `DeckKit "${requestedDeckkit}" not found in catalog`, {
        path: 'meta.deckkit',
        available: catalog.entries.map((e) => e.id),
      }),
    )
  }
  if (deckkit && content?.meta?.deckkit && content.meta.deckkit !== deckkit) {
    errors.push(
      makeIssue(
        'meta',
        `content.meta.deckkit "${content.meta.deckkit}" does not match --deckkit "${deckkit}"`,
        { path: 'meta.deckkit' },
      ),
    )
  }
  if (mode === 'delivery' && entry && !['production', 'default'].includes(entry.readiness)) {
    const message = `DeckKit "${entry.id}" readiness is "${entry.readiness ?? 'unspecified'}"; delivery mode requires production/default readiness`
    const diagnostic = makeFitDiagnostic({
      slideIndex: null,
      slideType: null,
      severity: 'warning',
      code: 'catalog.readiness.delivery',
      path: 'catalog.readiness',
      value: entry.readiness ?? null,
      limit: 'production|default',
      message,
      suggestedActions: ['promote-deckkit-after-release-gate', 'use-production-deckkit'],
    })
    fitDiagnostics.push(diagnostic)
    warnings.push(
      makeIssue('catalog', message, {
        path: 'catalog.readiness',
        readiness: entry.readiness,
        diagnostic,
      }),
    )
  }

  const supportedTypes =
    entry?.supportedSlideTypes ?? contentSchema.properties.slides.items.properties.type.enum ?? []
  const soft = entry?.density?.soft ?? {}
  const hard = entry?.density?.hard ?? {}

  if (Array.isArray(content?.slides)) {
    content.slides.forEach((slide, i) => {
      const prefix = `slides[${i}]`

      if (!slide || typeof slide !== 'object') {
        errors.push(makeIssue('slide', `${prefix}: slide must be an object`, { path: prefix }))
        return
      }

      validateObjectAgainstSchema(slide, contentSchema.properties.slides.items, prefix, errors)

      if (!slide.type) {
        errors.push(makeIssue('slide', `${prefix}: missing "type"`, { path: `${prefix}.type` }))
        return
      }
      if (!supportedTypes.includes(slide.type)) {
        errors.push(
          makeIssue(
            'slide',
            `${prefix}: unknown type "${slide.type}". Supported: ${supportedTypes.join(', ')}`,
            {
              path: `${prefix}.type`,
              supported: supportedTypes,
            },
          ),
        )
        return
      }
      if (!slide.data || typeof slide.data !== 'object' || Array.isArray(slide.data)) {
        errors.push(
          makeIssue('slide', `${prefix}: missing or invalid "data"`, { path: `${prefix}.data` }),
        )
        return
      }

      try {
        const schema = loadSlideSchema(requestedDeckkit, slide.type)
        if (!schema) throw new Error('schema not found')
        validateObjectAgainstSchema(slide.data, schema, `${prefix}.data`, errors)
        checkSlotBudgets(
          {
            slideIndex: i,
            slideType: slide.type,
            mode,
            errors,
            warnings,
            fitDiagnostics,
          },
          slide.data,
          schema,
          `${prefix}.data`,
        )
      } catch {
        // Schema coverage is intentionally progressive.
      }

      checkSlideDensity({
        slide,
        slideIndex: i,
        soft,
        hard,
        errors,
        warnings,
        fitDiagnostics,
        ignoreSoftLimits,
        mode,
      })
      checkSlideLayoutContract({
        entry,
        slide,
        slideIndex: i,
        mode,
        errors,
        warnings,
        fitDiagnostics,
      })
      checkSlideAssetSlots({
        entry,
        slide,
        slideIndex: i,
        mode,
        errors,
        warnings,
        fitDiagnostics,
      })
    })
    checkDeckDiversity({
      entry,
      content,
      mode,
      errors,
      warnings,
      fitDiagnostics,
    })
  }

  if (throwOnError && errors.length > 0) {
    throw new Error(
      `Content validation failed:\n${errors.map((e) => `  [${e.type}] ${e.message}`).join('\n')}`,
    )
  }

  return {
    errors,
    warnings,
    fitDiagnostics,
    valid: errors.length === 0,
    entry,
    normalizedContent: content,
  }
}

// --- Build-time patch quality preflight ---
const QUALITY_MIN_FONT_PT = 10
const DEFAULT_TEXT_INSET_X_IN = 0.1
const DEFAULT_TEXT_INSET_Y_IN = 0.05
const QUALITY_GEOMETRY_EPSILON_IN = 0.000001
const QUALITY_PANEL_SHAPE_KINDS = new Set(['rectangle', 'rect'])

function parseInches(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  const m = String(value ?? '').match(/^(-?[0-9]+(?:\.[0-9]+)?)in$/i)
  return m ? Number.parseFloat(m[1]) : null
}

function normalizePatchFillColor(fill) {
  if (!fill || typeof fill !== 'object') return null
  const kind = fill.type ?? fill.kind
  if (kind !== 'solid') return null
  return normalizeHex(fill.color ?? fill.rgb)
}

function estimateQualityCharWidth(ch, fontPt) {
  if (/[\u2e80-\u9fff\uf900-\ufaff\uac00-\ud7af]/u.test(ch)) return fontPt
  if (/[A-Z]/.test(ch)) return fontPt * 0.68
  if (/[a-z]/.test(ch)) return fontPt * 0.55
  if (/[0-9]/.test(ch)) return fontPt * 0.56
  if (/[!-/:-@[-`{-~]/.test(ch)) return fontPt * 0.34
  return fontPt * 0.55
}

function estimateQualityTextWidth(text, fontPt) {
  return [...String(text ?? '')].reduce((sum, ch) => sum + estimateQualityCharWidth(ch, fontPt), 0)
}

function estimateQualityLineCount(text, fontPt, maxWidthPt) {
  if (!text) return 0
  if (maxWidthPt <= 0) return 1_000_000
  let lines = 1
  let lineWidth = 0
  let token = ''
  const measure = (value) => estimateQualityTextWidth(value, fontPt)
  const placeToken = () => {
    let tokenWidth = measure(token)
    token = ''
    if (tokenWidth <= 0) return
    if (lineWidth > 0 && lineWidth + tokenWidth > maxWidthPt) {
      lines += 1
      lineWidth = 0
    }
    while (tokenWidth > maxWidthPt) {
      lines += 1
      tokenWidth -= maxWidthPt
    }
    lineWidth += tokenWidth
  }
  for (const ch of String(text)) {
    if (ch === '\n' || ch === '\v') {
      placeToken()
      lines += 1
      lineWidth = 0
      token = ''
    } else if (ch === ' ' || ch === '\t') {
      placeToken()
      if (lineWidth > 0) {
        const spaceWidth = measure(ch === '\t' ? '    ' : ' ')
        if (lineWidth + spaceWidth > maxWidthPt) {
          lines += 1
          lineWidth = 0
        } else {
          lineWidth += spaceWidth
        }
      }
    } else {
      token += ch
    }
  }
  placeToken()
  return lines
}

export const estimateDeckTextLineCount = estimateQualityLineCount

function qualityShapeFontPt(shape) {
  const sizes = shape.fonts.map((font) => parseFontPt(font?.size)).filter((size) => size !== null)
  return sizes.length ? Math.max(...sizes) : 12
}

function qualityExplicitFontColors(shape) {
  return [...new Set(shape.fonts.map((font) => normalizeHex(font?.color)).filter(Boolean))]
}

function qualitySeverityForContrast(ratio, minRatio) {
  if (ratio < Math.min(3, minRatio)) return 'error'
  return 'warning'
}

function makeQualityIssue({
  kind,
  severity = 'warning',
  slideIndex,
  shapeName,
  message,
  metrics = {},
  suggestedActions = [],
}) {
  return {
    kind,
    severity,
    slideIndex,
    shapeName,
    message,
    metrics,
    suggestedActions,
  }
}

function collectPatchQualityFacts(patch) {
  const slides = new Map()
  const ensureSlide = (slideIndex) => {
    if (!slides.has(slideIndex)) {
      slides.set(slideIndex, {
        background: 'FFFFFF',
        shapes: [],
        byName: new Map(),
        byId: new Map(),
      })
    }
    return slides.get(slideIndex)
  }
  const rememberShape = (shape) => {
    const slide = ensureSlide(shape.slideIndex)
    slide.shapes.push(shape)
    if (shape.name) slide.byName.set(shape.name, shape)
    if (shape.id !== undefined) slide.byId.set(shape.id, shape)
  }
  const selectShape = (slideIndex, selector) => {
    const slide = ensureSlide(slideIndex)
    if (selector?.name) return slide.byName.get(selector.name)
    if (selector?.id !== undefined) return slide.byId.get(selector.id)
    return null
  }

  let nextSlideIndex = 0
  for (const [order, op] of (patch?.ops ?? []).entries()) {
    if (op.op === 'add-slide') {
      ensureSlide(nextSlideIndex)
      nextSlideIndex += 1
      continue
    }
    if (op.op === 'set-slide-background') {
      const color = normalizePatchFillColor(op.fill)
      if (color) ensureSlide(op.slide).background = color
      continue
    }
    if (op.op === 'add-text-box' || op.op === 'add-shape') {
      const x = parseInches(op.x)
      const y = parseInches(op.y)
      const w = parseInches(op.w)
      const h = parseInches(op.h)
      if ([x, y, w, h].some((v) => v === null)) continue
      rememberShape({
        slideIndex: op.slide,
        id: op.id,
        name: op.name ?? '',
        kind: op.op,
        shapeKind: op.kind,
        order,
        x,
        y,
        w,
        h,
        text: op.text ?? '',
        fonts: [],
        fillColor: null,
        textInsetLeft: parseInches(op.marginLeft) ?? DEFAULT_TEXT_INSET_X_IN,
        textInsetRight: parseInches(op.marginRight) ?? DEFAULT_TEXT_INSET_X_IN,
        textInsetTop: parseInches(op.marginTop) ?? DEFAULT_TEXT_INSET_Y_IN,
        textInsetBottom: parseInches(op.marginBottom) ?? DEFAULT_TEXT_INSET_Y_IN,
      })
      continue
    }
    if (op.op === 'set-text-frame') {
      const shape = selectShape(op.slide, op.shape)
      if (shape) shape.text = String(op.text ?? '')
      continue
    }
    if (op.op === 'add-run') {
      const shape = selectShape(op.slide, op.shape)
      if (shape) {
        shape.text += String(op.text ?? '')
        if (op.font) shape.fonts.push(op.font)
      }
      continue
    }
    if (op.op === 'set-run') {
      const shape = selectShape(op.slide, op.shape)
      if (shape && op.font) shape.fonts.push(op.font)
      continue
    }
    if (op.op === 'set-shape') {
      const shape = selectShape(op.slide, op.shape)
      const color = normalizePatchFillColor(op.fill)
      if (shape && color) shape.fillColor = color
    }
  }
  return [...slides.entries()].map(([slideIndex, slide]) => ({ slideIndex, ...slide }))
}

function qualityShapeContains(container, target) {
  return (
    container.x <= target.x + QUALITY_GEOMETRY_EPSILON_IN &&
    container.y <= target.y + QUALITY_GEOMETRY_EPSILON_IN &&
    container.x + container.w + QUALITY_GEOMETRY_EPSILON_IN >= target.x + target.w &&
    container.y + container.h + QUALITY_GEOMETRY_EPSILON_IN >= target.y + target.h
  )
}

function qualityEffectiveBackground(shape, slide) {
  const ownFill = normalizeHex(shape.fillColor)
  if (ownFill) return ownFill
  const panel = slide.shapes
    .filter(
      (candidate) =>
        candidate.kind === 'add-shape' &&
        QUALITY_PANEL_SHAPE_KINDS.has(candidate.shapeKind) &&
        candidate.order < shape.order &&
        normalizeHex(candidate.fillColor) &&
        qualityShapeContains(candidate, shape),
    )
    .at(-1)
  return normalizeHex(panel?.fillColor) ?? normalizeHex(slide.background)
}

function qualityShapePatternMatches(shapeName, pattern) {
  if (!pattern) return true
  try {
    return new RegExp(pattern).test(shapeName)
  } catch {
    return false
  }
}

function qualityContrastIsExempt(shape, textColor, backgroundColor, qualityProfile) {
  return (qualityProfile?.contrastExemptions ?? []).some(
    (exemption) =>
      (!exemption.textColor || normalizeHex(exemption.textColor) === textColor) &&
      (!exemption.backgroundColor || normalizeHex(exemption.backgroundColor) === backgroundColor) &&
      qualityShapePatternMatches(shape.name ?? '', exemption.shapePattern),
  )
}

function assessTextOverflowQuality(shape, issues) {
  if (!/subtitle/i.test(shape.name ?? '')) return
  const text = String(shape.text ?? '').trim()
  if (!text) return
  const fontPt = qualityShapeFontPt(shape)
  const availableWPt = Math.max(0, (shape.w - shape.textInsetLeft - shape.textInsetRight) * 72)
  const availableHPt = Math.max(0, (shape.h - shape.textInsetTop - shape.textInsetBottom) * 72)
  const lineCount = estimateQualityLineCount(text, fontPt, availableWPt)
  const neededHPt = lineCount * fontPt * 1.2
  if (lineCount > 1 || neededHPt > availableHPt) {
    issues.push(
      makeQualityIssue({
        kind: 'text-overflow-risk',
        slideIndex: shape.slideIndex,
        shapeName: shape.name,
        message: 'subtitle copy is likely to wrap or collide with nearby chrome',
        metrics: {
          textLength: text.length,
          estLines: lineCount,
          fontPt,
          availableHeightPt: Number(availableHPt.toFixed(2)),
          neededHeightPt: Number(neededHPt.toFixed(2)),
        },
        suggestedActions: ['shorten-subtitle', 'increase-subtitle-box', 'move-rule-down'],
      }),
    )
  }
}

function assessContrastQuality(shape, slide, issues, qualityProfile) {
  if (!String(shape.text ?? '').trim()) return
  const colors = qualityExplicitFontColors(shape)
  if (colors.length === 0) return
  const bg = qualityEffectiveBackground(shape, slide)
  if (!bg) return
  const fontPt = qualityShapeFontPt(shape)
  const minContrast = fontPt >= 18 ? 3 : 4.5
  for (const color of colors) {
    if (qualityContrastIsExempt(shape, color, bg, qualityProfile)) continue
    const ratio = contrastRatio(color, bg)
    if (ratio > 0 && ratio < minContrast) {
      issues.push(
        makeQualityIssue({
          kind: 'low-contrast-text',
          severity: qualitySeverityForContrast(ratio, minContrast),
          slideIndex: shape.slideIndex,
          shapeName: shape.name,
          message: 'explicit text color does not meet WCAG contrast for the solid background',
          metrics: {
            textColor: color,
            backgroundColor: bg,
            contrastRatio: Number(ratio.toFixed(3)),
            minContrast,
            fontPt,
          },
          suggestedActions: ['darken-text-color', 'increase-font-size', 'change-background'],
        }),
      )
    }
  }
}

function assessFontSizeQuality(shape, issues, minFontPt = QUALITY_MIN_FONT_PT) {
  if (!String(shape.text ?? '').trim()) return
  for (const font of shape.fonts) {
    const fontPt = parseFontPt(font?.size)
    if (fontPt !== null && fontPt < minFontPt) {
      issues.push(
        makeQualityIssue({
          kind: 'font-too-small',
          severity: fontPt < Math.max(6, minFontPt - 2) ? 'error' : 'warning',
          slideIndex: shape.slideIndex,
          shapeName: shape.name,
          message: 'explicit font size is below the readable threshold',
          metrics: { fontPt, minFontPt },
          suggestedActions: ['increase-font-size', 'reduce-copy', 'switch-layout'],
        }),
      )
      return
    }
  }
}

export function assessDeckQuality({ patch, deckkit = null } = {}) {
  const issues = []
  const slides = collectPatchQualityFacts(patch)
  const qualityProfile = catalogEntryForDeckkit(deckkit)?.qualityProfile ?? {}
  const minFontPt = qualityProfile.minFontPt ?? QUALITY_MIN_FONT_PT
  for (const slide of slides) {
    for (const shape of slide.shapes) {
      assessTextOverflowQuality(shape, issues)
      assessContrastQuality(shape, slide, issues, qualityProfile)
      assessFontSizeQuality(shape, issues, minFontPt)
    }
  }
  const bySeverity = issues.reduce((acc, issue) => {
    acc[issue.severity] = (acc[issue.severity] ?? 0) + 1
    return acc
  }, {})
  return {
    schemaVersion: 'pptx-nova-quality/v1',
    deckkit,
    status: issues.some((issue) => issue.severity === 'error')
      ? 'error'
      : issues.length
        ? 'warning'
        : 'ok',
    summary: {
      issueCount: issues.length,
      bySeverity,
    },
    issues,
  }
}
