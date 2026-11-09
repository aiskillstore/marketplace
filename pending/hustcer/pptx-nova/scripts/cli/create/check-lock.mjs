#!/usr/bin/env node
import { SKILL_ROOT as skillRoot } from '../../lib/runtime/skill-paths.mjs'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import { normalizeChartSemantics, validateChartSemantics } from '../../lib/pptx/chart-semantics.mjs'
import { validateSessionRulesDocument } from '../../lib/edit/session-rules.mjs'
import { inspectAnimationCorpus } from '../../../assets/deckkits/shared/animation-corpus.mjs'

const deckkitRoot = join(skillRoot, 'assets', 'deckkits')

const LOCK_SCHEMA_VERSION = 'pptx-nova-deck-lock/v1'
const ASSETS_SCHEMA_VERSION = 'pptx-nova-assets-manifest/v1'
const COLOR_FIELD_RE =
  /(^|\.)(color|colors|fill|fills|stroke|strokes|linecolor|fontcolor|textcolor|fillcolor|bordercolor|backgroundcolor|bgcolor|foregroundcolor|accent|accent[1-9]|primary|secondary|success|warning|risk)(\.|$)/i
const IMAGE_READY_STATUSES = new Set(['available', 'generated', 'rendered'])
const ASSET_BLOCKING_STATUSES = new Set(['missing', 'needs-user', 'forbidden'])
const ASSET_REVIEW_STATUSES = new Set(['placeholder', 'needs-review'])
const IMAGE_LIKE_KINDS = new Set(['image', 'photo', 'photograph', 'illustration', 'screenshot'])
const IMAGE_SLOT_ROLE_RE = /(hero|image|photo|screenshot|background|visual|mockup|product-shot)/i
const IDENTITY_ASSET_RE =
  /(logo|brand|mark|app-icon|product-ui|product-screenshot|customer|client|portrait|person|headshot)/i
const IMAGE_SLOT_RATIOS = new Set(['21:9', '16:10', '16:9', '4:3', '3:2', '3:4', '1:1'])
const IMAGE_FIT_POLICIES = new Set(['cover', 'contain', 'no-crop', 'crop-safe'])
const SLIDE_RHYTHM_VALUES = ['anchor', 'dense', 'breathing', 'appendix']
const SLIDE_RHYTHMS = new Set(SLIDE_RHYTHM_VALUES)
const VISUAL_DENSITIES = new Set(['low', 'medium', 'high'])
const CHART_LEGENDS = new Set(['right', 'left', 'top', 'bottom', 'top-right'])
const CHART_LABEL_POSITIONS = new Set([
  'above',
  'below',
  'bestFit',
  'center',
  'insideBase',
  'insideEnd',
  'left',
  'outsideEnd',
  'right',
])
const TOPIC_TITLE_RE =
  /^(agenda|overview|market|roadmap|strategy|product|competition|competitors|summary|appendix|产品概览|市场分析|路线图|竞品|竞争|总结|目录|附录)$/i
// Category head-nouns: a short noun phrase ending in one of these reads as a topic
// label, not a conclusion. Catches multi-word titles like "Product Overview" /
// "Market Analysis" / "Competitive Landscape" that the single-word list above misses.
const TOPIC_HEAD_EN_RE =
  /\b(overview|introduction|background|analysis|roadmap|landscape|summary|recap|highlights|agenda)$/i
const TOPIC_HEAD_CN_RE = /(概览|综述|分析|路线图|总结|小结|介绍|背景)$/
const CLOSING_QUOTE_OR_BRACKET_RE = /["'”’）》】）\]]+$/u
const AI_IMAGE_SOURCE_KINDS = new Set([
  'ai',
  'generated',
  'imagegen',
  'prompt',
  'text-to-image',
  'dalle',
  'dall-e',
  'midjourney',
  'stable-diffusion',
])
const PPT_SAFE_FONTS = new Set(
  [
    'Microsoft YaHei',
    'SimHei',
    'SimSun',
    'FangSong',
    'KaiTi',
    'Arial',
    'Calibri',
    'Segoe UI',
    'Verdana',
    'Trebuchet MS',
    'Times New Roman',
    'Georgia',
    'Cambria',
    'Palatino',
    'Garamond',
    'Cambria Math',
    'Consolas',
    'Courier New',
    'Impact',
    'Arial Black',
  ].map((item) => item.toLowerCase()),
)
const SIMILAR_FONT_GROUPS = [
  ['microsoft yahei', 'pingfang sc', 'heiti sc'],
  ['simsun', 'songti sc', 'stsong'],
  ['arial', 'helvetica neue', 'segoe ui'],
  ['times new roman', 'times'],
  ['georgia', 'cambria'],
]

const usage = `Usage:
  node <skill-root>/scripts/cli/create/check-lock.mjs --lock deck_lock.json [options]

Options:
  --lock <path>        Required run-level design lock.
  --assets <path>      Optional assets_manifest.json.
  --content <path>     Optional DeckKit content manifest.
  --patch <path>       Optional xdoc patch envelope.
  --strict-colors      Treat colors not declared in deck_lock.json as errors.
  --strict-fonts       Treat font families not declared in deck_lock.json as errors.
  --json               Print machine-readable report.
  --help               Show this help.

Example:
  node <skill-root>/scripts/cli/create/check-lock.mjs \\
    --lock .pptx-nova/run/deck_lock.json \\
    --assets .pptx-nova/run/assets_manifest.json \\
    --content .pptx-nova/run/content.json \\
    --patch .pptx-nova/run/patch.json \\
    --json
`

function parseArgs(argv) {
  const args = {
    lock: '',
    assets: '',
    content: '',
    patch: '',
    strictColors: false,
    strictFonts: false,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--strict-colors') {
      args.strictColors = true
    } else if (arg === '--strict-fonts') {
      args.strictFonts = true
    } else if (arg === '--lock') {
      args.lock = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--assets') {
      args.assets = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--content') {
      args.content = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--patch') {
      args.patch = resolve(valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.lock) throw new Error(`--lock is required\n\n${usage}`)
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`Failed to read ${label} at ${path}: ${error.message}`)
  }
}

function push(list, code, message, details = {}) {
  list.push({ code, message, ...details })
}

function isPlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value)
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function normalizeHex(value) {
  const match = String(value ?? '').match(/^#?([0-9a-f]{6})(?:[0-9a-f]{2})?$/i)
  return match ? match[1].toUpperCase() : ''
}

function collectHexStrings(value, out = new Set()) {
  if (typeof value === 'string') {
    const matches = value.match(/(?<![0-9a-f])#?[0-9a-f]{6}(?:[0-9a-f]{2})?(?![0-9a-f])/gi) ?? []
    for (const item of matches) {
      const normalized = normalizeHex(item)
      if (normalized) out.add(normalized)
    }
    return out
  }
  if (Array.isArray(value)) {
    for (const item of value) collectHexStrings(item, out)
    return out
  }
  if (isPlainObject(value)) {
    for (const item of Object.values(value)) collectHexStrings(item, out)
  }
  return out
}

function collectAllowedColors(lock) {
  const colors = new Set()
  for (const source of [
    lock.colors,
    lock.theme,
    lock.themePack,
    lock.stylePack,
    lock.brand?.colors,
    lock.templateFusion?.identity,
  ]) {
    collectHexStrings(source, colors)
  }
  return colors
}

function normalizeFontName(value) {
  return String(value ?? '')
    .trim()
    .replace(/^['"]|['"]$/g, '')
    .replace(/\s+/g, ' ')
}

function splitFontStack(value) {
  return String(value ?? '')
    .split(',')
    .map(normalizeFontName)
    .filter(Boolean)
    .filter((item) => !['serif', 'sans-serif', 'monospace', 'system-ui'].includes(item))
}

function looksLikeFontName(value) {
  const text = normalizeFontName(value)
  if (!text) return false
  if (/^[0-9]+(?:\.[0-9]+)?pt$/i.test(text)) return false
  if (/^#?[0-9a-f]{6}(?:[0-9a-f]{2})?$/i.test(text)) return false
  if (/^(true|false|bold|italic|regular|normal|none)$/i.test(text)) return false
  return /[A-Za-z\u4e00-\u9fa5]/.test(text)
}

function collectAllowedFonts(lock) {
  const fonts = new Set()
  const collect = (value) => {
    if (typeof value === 'string') {
      for (const font of splitFontStack(value)) fonts.add(font.toLowerCase())
    } else if (Array.isArray(value)) {
      for (const item of value) collect(item)
    } else if (isPlainObject(value)) {
      for (const item of Object.values(value)) collect(item)
    }
  }
  collect(lock.typography)
  collect(lock.fonts)
  collect(lock.brand?.fonts)
  return fonts
}

function collectDeclaredFontStacks(lock) {
  const stacks = []
  const collect = (value, path) => {
    if (typeof value === 'string') {
      const key = path.at(-1)?.toLowerCase() ?? ''
      const root = path[0]?.toLowerCase() ?? ''
      const joined = path.join('.').toLowerCase()
      const isFontField =
        root === 'fonts' ||
        joined.includes('font') ||
        [
          'title',
          'heading',
          'major',
          'body',
          'minor',
          'code',
          'mono',
          'math',
          'caption',
          'label',
        ].includes(key)
      if (isFontField) {
        const fonts = splitFontStack(value)
        if (fonts.length > 0) stacks.push({ path: path.join('.'), fonts })
      }
      return
    }
    if (Array.isArray(value)) {
      value.forEach((item, index) => collect(item, [...path, String(index)]))
      return
    }
    if (isPlainObject(value)) {
      for (const [key, item] of Object.entries(value)) collect(item, [...path, key])
    }
  }
  collect(lock.typography, ['typography'])
  collect(lock.fonts, ['fonts'])
  collect(lock.brand?.fonts, ['brand', 'fonts'])
  return stacks
}

function fontRoleValue(lock, aliases) {
  for (const source of [lock.typography, lock.fonts, lock.brand?.fonts]) {
    if (!isPlainObject(source)) continue
    for (const key of aliases) {
      if (typeof source[key] === 'string') return source[key]
    }
  }
  return ''
}

function firstRoleFont(lock, role) {
  const aliases =
    role === 'title'
      ? ['title', 'heading', 'major', 'titleFont', 'headingFont']
      : ['body', 'minor', 'bodyFont', 'contentFont']
  return splitFontStack(fontRoleValue(lock, aliases))[0]?.toLowerCase() ?? ''
}

function similarFontGroup(font) {
  return SIMILAR_FONT_GROUPS.find((group) => group.includes(font)) ?? null
}

function checkTypographyQuality(lock, warnings) {
  for (const stack of collectDeclaredFontStacks(lock)) {
    const hasSafeFallback = stack.fonts.some((font) => PPT_SAFE_FONTS.has(font.toLowerCase()))
    if (!hasSafeFallback) {
      push(
        warnings,
        'font-stack-no-safe-fallback',
        `${stack.path} should include a common PowerPoint fallback font`,
      )
    }
  }

  const titleFont = firstRoleFont(lock, 'title')
  const bodyFont = firstRoleFont(lock, 'body')
  if (!titleFont || !bodyFont || titleFont === bodyFont) return
  const titleGroup = similarFontGroup(titleFont)
  if (titleGroup && titleGroup === similarFontGroup(bodyFont)) {
    push(
      warnings,
      'font-role-pair-too-similar',
      `title font "${titleFont}" and body font "${bodyFont}" are similar-but-different; use one stack or choose a clearer contrast`,
    )
  }
}

function collectFieldValues(value, predicate, path = [], out = []) {
  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      collectFieldValues(item, predicate, [...path, String(index)], out),
    )
    return out
  }
  if (!isPlainObject(value)) return out
  for (const [key, item] of Object.entries(value)) {
    const nextPath = [...path, key]
    if (predicate(key, nextPath, item)) out.push({ path: nextPath.join('.'), value: item })
    collectFieldValues(item, predicate, nextPath, out)
  }
  return out
}

function collectPatchFonts(patch) {
  const fontFields = collectFieldValues(patch, (key, path, value) => {
    if (typeof value !== 'string') return false
    const field = key.toLowerCase()
    const joined = path.join('.').toLowerCase()
    if (!looksLikeFontName(value)) return false
    return (
      field === 'fontface' ||
      field === 'fontfamily' ||
      field === 'typeface' ||
      field === 'family' ||
      field === 'font' ||
      joined.endsWith('.font.name') ||
      joined.endsWith('.font.family') ||
      joined.endsWith('.font.fontface') ||
      joined.endsWith('.font.fontfamily') ||
      joined.endsWith('.font.typeface')
    )
  })

  const fonts = []
  for (const field of fontFields) {
    for (const font of splitFontStack(field.value)) {
      fonts.push({ path: field.path, font })
    }
  }
  return fonts
}

function deckkitIdFrom(lock, content) {
  return lock.deckkit?.id ?? lock.deckkitId ?? content?.meta?.deckkit ?? content?.deckkit ?? ''
}

function loadDeckkitEntry(deckkitId) {
  if (!deckkitId) return null
  const catalogPath = join(deckkitRoot, 'catalog.json')
  if (!existsSync(catalogPath)) return null
  try {
    const catalog = readJson(catalogPath, 'DeckKit catalog')
    return catalog.entries?.find((entry) => entry.id === deckkitId) ?? null
  } catch {
    return null
  }
}

function collectDeckkitTokens(deckkitId) {
  const colors = new Set()
  const fonts = new Set()
  const entry = loadDeckkitEntry(deckkitId)
  if (!entry?.path) return { colors, fonts }
  const kitPath = join(deckkitRoot, entry.path)
  if (!existsSync(kitPath)) return { colors, fonts }
  const source = readFileSync(kitPath, 'utf8')
  collectHexStrings(source, colors)
  for (const match of source.matchAll(/\bFONT_[A-Z0-9_]*\s*=\s*['"]([^'"]+)['"]/g)) {
    for (const font of splitFontStack(match[1])) fonts.add(font.toLowerCase())
  }
  return { colors, fonts }
}

function collectPatchColors(patch) {
  const colorFields = collectFieldValues(patch, (key, path, value) => {
    if (typeof value !== 'string' && !Array.isArray(value) && !isPlainObject(value)) return false
    const joined = path
      .map((part) => (Number.isNaN(Number(part)) ? part : '[]'))
      .join('.')
      .toLowerCase()
    return COLOR_FIELD_RE.test(joined) || COLOR_FIELD_RE.test(key.toLowerCase())
  })

  const colors = new Set()
  for (const field of colorFields) collectHexStrings(field.value, colors)
  return colors
}

function collectAssetPaths(patch) {
  return collectFieldValues(patch, (key, path, value) => {
    if (typeof value !== 'string') return false
    const joined = path.join('.').toLowerCase()
    return joined.endsWith('assetsource.path') || joined.endsWith('.image.path')
  })
}

function slideTypeOf(slide) {
  return slide?.slideType ?? slide?.type ?? slide?.kind ?? slide?.layout ?? ''
}

function isFormalNarrativeLock(lock) {
  const mode = String(lock.mode ?? '').toLowerCase()
  const audience = String(lock.audience ?? lock.objective ?? '').toLowerCase()
  return (
    mode === 'studio' ||
    lock.narrativeQuality?.required === true ||
    isPlainObject(lock.deckProfile) ||
    /investor|customer|board|roadshow|strategy|executive|client|董事会|客户|投资人|路演|战略/.test(
      audience,
    )
  )
}

function proofObjectOf(slide) {
  return slide?.proofObject ?? slide?.proof ?? slide?.evidence ?? null
}

function layoutIntentOf(slide) {
  return slide?.layoutIntent ?? slide?.macroLayout ?? slide?.layoutRole ?? ''
}

function visualDensityOf(slide) {
  return slide?.visualDensity ?? slide?.density ?? ''
}

function isAppendixLike(slide) {
  const rhythm = String(slide?.rhythm ?? '').toLowerCase()
  const type = String(slideTypeOf(slide)).toLowerCase()
  return rhythm === 'appendix' || type.includes('appendix')
}

function looksTopicOnly(title) {
  const normalized = String(title ?? '')
    .trim()
    .replace(/[：:。.\s]+$/g, '')
  if (!normalized) return false
  if (TOPIC_TITLE_RE.test(normalized)) return true
  // Multi-word labels: only flag short noun phrases ending in a category head-noun,
  // so conclusion sentences (which put the predicate after the noun) are not flagged.
  if (/[一-鿿]/.test(normalized)) {
    return normalized.length <= 8 && TOPIC_HEAD_CN_RE.test(normalized)
  }
  return normalized.split(/\s+/).length <= 4 && TOPIC_HEAD_EN_RE.test(normalized)
}

function stripClosingQuoteOrBracket(value) {
  let text = String(value ?? '').trim()
  while (CLOSING_QUOTE_OR_BRACKET_RE.test(text)) {
    text = text.replace(CLOSING_QUOTE_OR_BRACKET_RE, '').trim()
  }
  return text
}

function hasSentenceEndingPeriod(value) {
  const text = stripClosingQuoteOrBracket(value)
  if (!text) return false
  if (/[。．｡]$/u.test(text)) return true
  if (!text.endsWith('.')) return false
  if (/(?:^|[\s([])(?:[A-Z]\.){2,}$/.test(text)) return false
  const previous = text.at(-2) ?? ''
  return !/\d/.test(previous)
}

function isUserSpecifiedDisplayText(slide, role) {
  const sourceFields =
    role === 'title'
      ? [slide?.titleSource, slide?.displayTitleSource, slide?.sources?.title]
      : [slide?.subtitleSource, slide?.displaySubtitleSource, slide?.sources?.subtitle]
  return sourceFields.some((source) => String(source ?? '').toLowerCase() === 'user')
}

function checkDisplayTextPunctuation(
  value,
  { path, role, warnings, preserveUserSpecified = false },
) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      checkDisplayTextPunctuation(item, {
        path: `${path}[${index}]`,
        role,
        warnings,
        preserveUserSpecified,
      })
    })
    return
  }
  if (preserveUserSpecified || typeof value !== 'string' || !hasSentenceEndingPeriod(value)) return
  push(
    warnings,
    `display-${role}-terminal-period`,
    `${path} ends with a period; prefer no sentence-ending period in display ${role}, with ?/! only when intentional`,
  )
}

function assetEntries(assets) {
  if (!assets) return []
  if (Array.isArray(assets.entries)) return assets.entries
  if (Array.isArray(assets.assets)) return assets.assets
  return []
}

function resolveMaybeRelative(path, baseDir) {
  if (!path || /^https?:\/\//i.test(path) || path.startsWith('data:')) return ''
  return isAbsolute(path) ? path : resolve(baseDir, path)
}

function assetFileCandidates(path, baseDir, assetRoot) {
  const normalized = normalizeAssetPath(path)
  if (!normalized || /^https?:\/\//i.test(normalized) || normalized.startsWith('data:')) return []
  if (isAbsolute(path)) return [path]

  const candidates = [resolveMaybeRelative(normalized, baseDir)]
  const root = normalizeAssetPath(assetRoot)
  if (root && !normalized.startsWith(`${root}/`)) {
    candidates.unshift(resolveMaybeRelative(`${root}/${normalized}`, baseDir))
  }
  return [...new Set(candidates)]
}

function normalizeAssetPath(value) {
  const text = String(value ?? '').trim()
  if (!text || /^https?:\/\//i.test(text) || text.startsWith('data:')) return text
  return text.replace(/\\/g, '/').replace(/^\.\//, '').replace(/\/+/g, '/')
}

function assetRole(entry) {
  return String(entry?.pptxUse?.role ?? entry?.role ?? '')
}

function isImageLikeAsset(entry) {
  const kind = String(entry?.kind ?? '').toLowerCase()
  return IMAGE_LIKE_KINDS.has(kind) || IMAGE_SLOT_ROLE_RE.test(assetRole(entry))
}

function isAiGeneratedImageAsset(entry) {
  if (!isImageLikeAsset(entry)) return false
  const sourceKind = String(entry?.source?.kind ?? entry?.sourceKind ?? '').toLowerCase()
  const generator = String(entry?.source?.generator ?? entry?.generator ?? '').toLowerCase()
  return (
    AI_IMAGE_SOURCE_KINDS.has(sourceKind) ||
    typeof entry?.source?.prompt === 'string' ||
    typeof entry?.prompt === 'string' ||
    /imagegen|dall-?e|midjourney|stable-diffusion/i.test(generator)
  )
}

function isIdentityAsset(entry) {
  const kind = String(entry?.kind ?? '').toLowerCase()
  const role = assetRole(entry).toLowerCase()
  const slot = String(
    entry?.pptxUse?.slotId ?? entry?.slot?.id ?? entry?.slotId ?? '',
  ).toLowerCase()
  return IDENTITY_ASSET_RE.test(`${kind} ${role} ${slot}`)
}

function assetSlot(entry) {
  const pptxUse = isPlainObject(entry?.pptxUse) ? entry.pptxUse : {}
  const directSlot = isPlainObject(entry?.slot) ? entry.slot : {}
  const nestedSlot = isPlainObject(pptxUse.slot) ? pptxUse.slot : {}
  return {
    id: pptxUse.slotId ?? nestedSlot.id ?? directSlot.id ?? entry?.slotId ?? '',
    ratio: pptxUse.ratio ?? nestedSlot.ratio ?? directSlot.ratio ?? '',
    fitPolicy:
      pptxUse.fitPolicy ??
      nestedSlot.fitPolicy ??
      directSlot.fitPolicy ??
      pptxUse.crop ??
      nestedSlot.crop ??
      directSlot.crop ??
      '',
    noSlideChrome:
      pptxUse.noSlideChrome ??
      nestedSlot.noSlideChrome ??
      directSlot.noSlideChrome ??
      pptxUse.promptGuard?.noSlideChrome ??
      entry?.generationPromptGuard?.noSlideChrome ??
      entry?.source?.promptGuard?.noSlideChrome,
  }
}

function checkChartSemantic(op, index, intent, errors, warnings) {
  const semantics = normalizeChartSemantics(op, intent)
  const label = `ops[${index}] ${op.op}`
  const validation = validateChartSemantics(semantics)
  for (const error of validation.errors) {
    push(errors, error.code, `${label}: ${error.message}`)
  }
  for (const warning of validation.warnings) {
    push(warnings, warning.code, `${label}: ${warning.message}`)
  }

  if (Object.hasOwn(op, 'legend') && !CHART_LEGENDS.has(op.legend)) {
    push(
      errors,
      'chart-legend-invalid',
      `${label} legend must be one of ${[...CHART_LEGENDS].join(', ')}`,
    )
  }
  if (op.position && !CHART_LABEL_POSITIONS.has(String(op.position))) {
    push(
      warnings,
      'chart-label-position-suspicious',
      `${label} uses chart label position "${op.position}"; verify schema spelling`,
    )
  }
}

function tableDataRows(op) {
  if (Array.isArray(op.data)) return op.data
  if (Array.isArray(op.json)) return op.json
  return []
}

function checkTableSemantic(op, index, errors, _warnings) {
  const label = `ops[${index}] ${op.op}`
  const rows = tableDataRows(op)
  if (op.op === 'add-table') {
    if (!Number.isInteger(op.rows) || op.rows <= 0) {
      push(errors, 'table-rows-invalid', `${label} must declare a positive rows count`)
    }
    if (!Number.isInteger(op.columns) || op.columns <= 0) {
      push(errors, 'table-columns-invalid', `${label} must declare a positive columns count`)
    }
  }
  if (rows.length > 0 && Array.isArray(rows[0])) {
    const width = rows[0].length
    rows.forEach((row, rowIndex) => {
      if (!Array.isArray(row)) {
        push(errors, 'table-row-invalid', `${label} data row ${rowIndex} is not an array`)
      } else if (row.length !== width) {
        push(
          errors,
          'table-row-width-mismatch',
          `${label} data row ${rowIndex} has ${row.length} cell(s), expected ${width}`,
        )
      }
    })
    if (op.columns && width !== op.columns && op.resize !== true) {
      push(
        errors,
        'table-data-cols-mismatch',
        `${label} data has ${width} column(s), table has ${op.columns}; set resize=true or fix data`,
      )
    }
    if (op.rows && rows.length !== op.rows && op.resize !== true) {
      push(
        errors,
        'table-data-rows-mismatch',
        `${label} data has ${rows.length} row(s), table has ${op.rows}; set resize=true or fix data`,
      )
    }
  }
}

function checkImageAssetSlot(entry, label, status, errors, warnings) {
  if (!IMAGE_READY_STATUSES.has(status) || !isImageLikeAsset(entry)) return

  const slot = assetSlot(entry)
  if (!slot.id) {
    push(
      warnings,
      'asset-image-slot-missing',
      `image asset ${label} should declare pptxUse.slotId or slot.id`,
    )
  }
  if (!slot.ratio) {
    push(
      warnings,
      'asset-image-ratio-missing',
      `image asset ${label} should declare intended slot ratio`,
    )
  } else if (!IMAGE_SLOT_RATIOS.has(String(slot.ratio))) {
    push(
      warnings,
      'asset-image-ratio-unknown',
      `image asset ${label} uses unsupported slot ratio "${slot.ratio}"`,
    )
  }
  if (!slot.fitPolicy) {
    push(
      warnings,
      'asset-image-fit-policy-missing',
      `image asset ${label} should declare fitPolicy cover/contain/no-crop/crop-safe`,
    )
  } else if (!IMAGE_FIT_POLICIES.has(String(slot.fitPolicy))) {
    push(
      warnings,
      'asset-image-fit-policy-unknown',
      `image asset ${label} uses unsupported fitPolicy "${slot.fitPolicy}"`,
    )
  }
  if (isAiGeneratedImageAsset(entry) && slot.noSlideChrome !== true) {
    push(
      errors,
      'asset-ai-slide-chrome-guard-missing',
      `AI-generated image asset ${label} must set pptxUse.noSlideChrome=true or slot.noSlideChrome=true`,
    )
  }
}

function checkLock(lock, errors, warnings) {
  if (lock.schemaVersion !== LOCK_SCHEMA_VERSION) {
    push(
      errors,
      'lock-schema-version',
      `deck_lock.json schemaVersion must be ${LOCK_SCHEMA_VERSION}`,
    )
  }
  if (!lock.mode) push(warnings, 'lock-mode-missing', 'deck_lock.json mode is missing')
  if (!lock.outlinePath && !lock.outline) {
    push(
      warnings,
      'lock-outline-missing',
      'deck_lock.json should point to outline.json or embed outline',
    )
  }
  if (!isPlainObject(lock.canvas)) push(warnings, 'lock-canvas-missing', 'canvas is missing')
  if (!isPlainObject(lock.colors) || collectAllowedColors(lock).size === 0) {
    push(warnings, 'lock-colors-missing', 'colors are missing or contain no 6-digit HEX values')
  }
  if (!isPlainObject(lock.typography) && !isPlainObject(lock.fonts)) {
    push(warnings, 'lock-typography-missing', 'typography/font declarations are missing')
  } else {
    checkTypographyQuality(lock, warnings)
  }
  const formalNarrative = isFormalNarrativeLock(lock)
  if (formalNarrative && !lock.deckProfile?.primary) {
    push(
      warnings,
      'lock-deck-profile-missing',
      'formal create deck should declare deckProfile.primary',
    )
  }
  if (!Array.isArray(lock.slides) || lock.slides.length === 0) {
    push(errors, 'lock-slides-missing', 'deck_lock.json must contain a non-empty slides[] array')
  } else {
    let sameRhythmRun = 1
    let previousRhythm = ''
    lock.slides.forEach((slide, index) => {
      const currentRhythm = String(slide?.rhythm ?? '').toLowerCase()
      if (currentRhythm && currentRhythm === previousRhythm) {
        sameRhythmRun += 1
      } else {
        sameRhythmRun = 1
      }
      if (
        sameRhythmRun >= 4 &&
        currentRhythm &&
        currentRhythm !== 'appendix' &&
        lock.slides.length >= 6
      ) {
        push(
          warnings,
          'lock-slide-rhythm-repetition',
          `slides ${index - 2}-${index + 1} repeat rhythm "${currentRhythm}"; verify contact-sheet variety`,
        )
      }
      previousRhythm = currentRhythm

      if (!slideTypeOf(slide)) {
        push(warnings, 'lock-slide-type-missing', `slides[${index}] has no slideType/type/kind`)
      }
      if (!slide.title && !slide.purpose) {
        push(
          warnings,
          'lock-slide-purpose-missing',
          `slides[${index}] should have title or purpose`,
        )
      }
      checkDisplayTextPunctuation(slide.title, {
        path: `slides[${index}].title`,
        role: 'title',
        warnings,
        preserveUserSpecified: isUserSpecifiedDisplayText(slide, 'title'),
      })
      checkDisplayTextPunctuation(slide.displayTitle, {
        path: `slides[${index}].displayTitle`,
        role: 'title',
        warnings,
        preserveUserSpecified: isUserSpecifiedDisplayText(slide, 'title'),
      })
      checkDisplayTextPunctuation(slide.subtitle ?? slide.displaySubtitle, {
        path: slide.subtitle ? `slides[${index}].subtitle` : `slides[${index}].displaySubtitle`,
        role: 'subtitle',
        warnings,
        preserveUserSpecified: isUserSpecifiedDisplayText(slide, 'subtitle'),
      })
      if (!slide.rhythm) {
        push(
          warnings,
          'lock-slide-rhythm-missing',
          `slides[${index}] should declare rhythm ${SLIDE_RHYTHM_VALUES.join('/')}`,
        )
      } else if (!SLIDE_RHYTHMS.has(String(slide.rhythm))) {
        push(
          warnings,
          'lock-slide-rhythm-unknown',
          `slides[${index}] uses unknown rhythm "${slide.rhythm}"; allowed values: ${SLIDE_RHYTHM_VALUES.join(', ')}`,
          { allowedValues: SLIDE_RHYTHM_VALUES },
        )
      }
      if (!layoutIntentOf(slide)) {
        push(
          warnings,
          'lock-slide-layout-intent-missing',
          `slides[${index}] should declare layoutIntent or macroLayout`,
        )
      }
      const visualDensity = visualDensityOf(slide)
      if (visualDensity && !VISUAL_DENSITIES.has(String(visualDensity))) {
        push(
          warnings,
          'lock-slide-density-unknown',
          `slides[${index}] uses unknown visualDensity "${visualDensity}"`,
        )
      }
      if (formalNarrative && !isAppendixLike(slide)) {
        if (!slide.claimTitle) {
          push(
            warnings,
            'lock-slide-claim-missing',
            `slides[${index}] formal narrative slide should have claimTitle`,
          )
        }
        if (!proofObjectOf(slide)) {
          push(
            warnings,
            'lock-slide-proof-missing',
            `slides[${index}] formal narrative slide should have proofObject`,
          )
        }
        if (!slide.rhythm) {
          push(
            warnings,
            'lock-formal-slide-rhythm-missing',
            `slides[${index}] formal narrative slide should declare rhythm`,
          )
        }
        if (looksTopicOnly(slide.claimTitle ?? slide.title)) {
          push(
            warnings,
            'lock-slide-topic-title',
            `slides[${index}] title looks topic-only; prefer a conclusion-style claimTitle`,
          )
        }
      }
    })
  }
}

function checkSessionRules(lock, lockPath, errors) {
  if (lock.sessionRulesPath === undefined) return null
  if (typeof lock.sessionRulesPath !== 'string' || !lock.sessionRulesPath.trim()) {
    push(
      errors,
      'session-rules-path-invalid',
      'deck_lock.sessionRulesPath must be a non-empty path string',
    )
    return null
  }
  const path = isAbsolute(lock.sessionRulesPath)
    ? resolve(lock.sessionRulesPath)
    : resolve(dirname(lockPath), lock.sessionRulesPath)
  if (!existsSync(path)) {
    push(errors, 'session-rules-missing', `session rules artifact does not exist: ${path}`)
    return null
  }
  try {
    return validateSessionRulesDocument(readJson(path, 'session-rules.json'))
  } catch (error) {
    push(
      errors,
      'session-rules-invalid',
      `session rules artifact is invalid: ${error instanceof Error ? error.message : String(error)}`,
    )
    return null
  }
}

function checkAssets(assets, assetsPath, referenced, errors, warnings) {
  if (!assets) return
  if (assets.schemaVersion !== ASSETS_SCHEMA_VERSION) {
    push(
      errors,
      'assets-schema-version',
      `assets_manifest.json schemaVersion must be ${ASSETS_SCHEMA_VERSION}`,
    )
  }

  const entries = assetEntries(assets)
  if (entries.length === 0 && referenced.size > 0) {
    push(
      errors,
      'assets-empty',
      'deck/content references assets but assets_manifest.json has no entries',
    )
  }

  const ids = new Set()
  const baseDir = dirname(assetsPath)
  const assetRoot = assets.assetRoot ?? ''
  for (const [index, entry] of entries.entries()) {
    const label = entry.id ?? `entries[${index}]`
    if (!entry.id) push(errors, 'asset-id-missing', `assets entry ${index} is missing id`)
    if (entry.id && ids.has(entry.id))
      push(errors, 'asset-id-duplicate', `duplicate asset id: ${entry.id}`)
    if (entry.id) ids.add(entry.id)
    if (!entry.kind) push(warnings, 'asset-kind-missing', `asset ${label} is missing kind`)

    const status = String(entry.status ?? 'available').toLowerCase()
    if (ASSET_BLOCKING_STATUSES.has(status)) {
      push(errors, 'asset-not-ready', `asset ${label} is not ready: status=${status}`)
    } else if (ASSET_REVIEW_STATUSES.has(status)) {
      push(warnings, 'asset-review-needed', `asset ${label} still needs review: status=${status}`)
    }
    const licenseRisk = String(entry.licenseRisk ?? entry.source?.licenseRisk ?? '').toLowerCase()
    if (licenseRisk === 'blocked') {
      push(errors, 'asset-license-blocked', `asset ${label} has blocked license risk`)
    } else if (licenseRisk === 'unknown') {
      push(warnings, 'asset-license-unknown', `asset ${label} has unknown license risk`)
    }
    if (isIdentityAsset(entry)) {
      const sourceKind = String(entry.source?.kind ?? entry.sourceKind ?? '').toLowerCase()
      if (!['user', 'source-deck', 'official', 'built-in'].includes(sourceKind)) {
        push(
          errors,
          'asset-identity-source-untrusted',
          `identity asset ${label} must come from user, source-deck, official, or built-in source`,
        )
      }
    }
    checkImageAssetSlot(entry, label, status, errors, warnings)

    const sourceKind = entry.source?.kind ?? entry.sourceKind ?? ''
    const path = entry.path ?? entry.source?.path ?? ''
    const shouldExist =
      path &&
      !['built-in', 'web', 'placeholder'].includes(sourceKind) &&
      !/^https?:\/\//i.test(path) &&
      !path.startsWith('data:')
    const candidates = assetFileCandidates(path, baseDir, assetRoot)
    const resolved = candidates.find((candidate) => existsSync(candidate))
    if (shouldExist && candidates.length > 0 && !resolved) {
      push(errors, 'asset-file-missing', `asset ${label} points to a missing file: ${path}`)
    } else if (shouldExist && resolved) {
      try {
        if (!statSync(resolved).isFile()) {
          push(errors, 'asset-not-file', `asset ${label} path is not a file: ${path}`)
        }
      } catch {
        push(errors, 'asset-file-missing', `asset ${label} points to a missing file: ${path}`)
      }
    }
  }

  for (const id of referenced) {
    if (!ids.has(id))
      push(errors, 'asset-reference-missing', `deck/content references unknown asset: ${id}`)
  }
}

function manifestAssetPaths(assets) {
  const paths = new Set()
  const assetRoot = normalizeAssetPath(assets?.assetRoot)
  const addPath = (value) => {
    const normalized = normalizeAssetPath(value)
    if (!normalized) return
    paths.add(normalized)
    if (assetRoot && normalized.startsWith(`${assetRoot}/`)) {
      paths.add(normalized.slice(assetRoot.length + 1))
    } else if (assetRoot && !isAbsolute(normalized) && !/^https?:\/\//i.test(normalized)) {
      paths.add(`${assetRoot}/${normalized}`)
    }
  }

  for (const entry of assetEntries(assets)) {
    for (const value of [
      entry.path,
      entry.source?.path,
      entry.pptxUse?.path,
      entry.assetSource?.path,
    ]) {
      addPath(value)
    }
  }
  return paths
}

function lockAssetReferences(lock) {
  const referenced = new Set()
  for (const slide of asArray(lock.slides)) {
    for (const id of asArray(slide.assets)) referenced.add(id)
    for (const id of asArray(slide.assetIds)) referenced.add(id)
    for (const id of asArray(slide.images)) referenced.add(id)
    for (const id of asArray(slide.formulas)) referenced.add(id)
    if (isPlainObject(slide.imageSlots)) {
      for (const id of Object.values(slide.imageSlots)) {
        if (id) referenced.add(id)
      }
    }
  }
  return referenced
}

function contentAssetReferences(content) {
  const referenced = new Set()
  for (const slide of asArray(content?.slides)) {
    for (const id of asArray(slide.assets)) referenced.add(id)
    for (const id of asArray(slide.assetIds)) referenced.add(id)
    for (const id of asArray(slide.images)) referenced.add(id)
    for (const id of asArray(slide.formulas)) referenced.add(id)
    if (isPlainObject(slide.imageSlots)) {
      for (const id of Object.values(slide.imageSlots)) {
        if (id) referenced.add(id)
      }
    }
  }
  return referenced
}

function checkContent(content, lock, errors, warnings) {
  if (!content) return
  if (
    (content.meta?.deckProfile === 'animation-corpus' ||
      lock.deckProfile?.primary === 'animation-corpus') &&
    content.meta?.deckProfile !== lock.deckProfile?.primary
  ) {
    push(
      errors,
      'corpus-profile-mismatch',
      'content.meta.deckProfile and lock.deckProfile.primary must both declare animation-corpus',
    )
  }
  if (!Array.isArray(content.slides)) {
    push(errors, 'content-slides-missing', 'content.json must contain slides[]')
    return
  }
  if (Array.isArray(lock.slides) && lock.slides.length !== content.slides.length) {
    push(
      errors,
      'slide-count-mismatch',
      `deck_lock has ${lock.slides.length} slide(s), content has ${content.slides.length}`,
    )
  }

  content.slides.forEach((slide, index) => {
    const data = slide?.data ?? {}
    const lockSlide = lock.slides?.[index] ?? {}
    checkDisplayTextPunctuation(data.title ?? slide?.title, {
      path: data.title !== undefined ? `slides[${index}].data.title` : `slides[${index}].title`,
      role: 'title',
      warnings,
      preserveUserSpecified: isUserSpecifiedDisplayText(lockSlide, 'title'),
    })
    checkDisplayTextPunctuation(data.displayTitle, {
      path: `slides[${index}].data.displayTitle`,
      role: 'title',
      warnings,
      preserveUserSpecified: isUserSpecifiedDisplayText(lockSlide, 'title'),
    })
    checkDisplayTextPunctuation(data.subtitle, {
      path: `slides[${index}].data.subtitle`,
      role: 'subtitle',
      warnings,
      preserveUserSpecified: isUserSpecifiedDisplayText(lockSlide, 'subtitle'),
    })
    checkDisplayTextPunctuation(data.sub, {
      path: `slides[${index}].data.sub`,
      role: 'subtitle',
      warnings,
      preserveUserSpecified: isUserSpecifiedDisplayText(lockSlide, 'subtitle'),
    })
    checkDisplayTextPunctuation(data.displaySubtitle, {
      path: `slides[${index}].data.displaySubtitle`,
      role: 'subtitle',
      warnings,
      preserveUserSpecified: isUserSpecifiedDisplayText(lockSlide, 'subtitle'),
    })
  })

  const limit = Math.min(lock.slides?.length ?? 0, content.slides.length)
  for (let index = 0; index < limit; index += 1) {
    const lockedType = slideTypeOf(lock.slides[index])
    const contentType = slideTypeOf(content.slides[index])
    if (lockedType && contentType && lockedType !== contentType) {
      push(
        errors,
        'slide-type-mismatch',
        `slide ${index + 1} type drift: deck_lock=${lockedType}, content=${contentType}`,
      )
    }
    const lockedRhythm = lock.slides[index]?.rhythm
    const contentRhythm = content.slides[index]?.rhythm
    if (lockedRhythm && contentRhythm && lockedRhythm !== contentRhythm) {
      push(
        warnings,
        'slide-rhythm-mismatch',
        `slide ${index + 1} rhythm drift: deck_lock=${lockedRhythm}, content=${contentRhythm}`,
      )
    }
    const lockedLayoutIntent = layoutIntentOf(lock.slides[index])
    const contentLayoutIntent = layoutIntentOf(content.slides[index])
    if (lockedLayoutIntent && contentLayoutIntent && lockedLayoutIntent !== contentLayoutIntent) {
      push(
        warnings,
        'slide-layout-intent-mismatch',
        `slide ${index + 1} layout intent drift: deck_lock=${lockedLayoutIntent}, content=${contentLayoutIntent}`,
      )
    }
    const lockedDensity = visualDensityOf(lock.slides[index])
    const contentDensity = visualDensityOf(content.slides[index])
    if (lockedDensity && contentDensity && lockedDensity !== contentDensity) {
      push(
        warnings,
        'slide-density-mismatch',
        `slide ${index + 1} visual density drift: deck_lock=${lockedDensity}, content=${contentDensity}`,
      )
    }
  }

  const lockedDeckkit = lock.deckkit?.id ?? lock.deckkitId ?? ''
  const contentDeckkit = content.meta?.deckkit ?? content.deckkit ?? ''
  if (lockedDeckkit && contentDeckkit && lockedDeckkit !== contentDeckkit) {
    push(
      errors,
      'deckkit-mismatch',
      `deckkit drift: deck_lock=${lockedDeckkit}, content=${contentDeckkit}`,
    )
  }

  if (
    content.meta?.themePack &&
    lock.themePack?.id &&
    content.meta.themePack !== lock.themePack.id
  ) {
    push(
      warnings,
      'theme-mismatch',
      `themePack differs: deck_lock=${lock.themePack.id}, content=${content.meta.themePack}`,
    )
  }
}

function checkPatch(patch, lock, content, assets, args, errors, warnings) {
  if (!patch) return
  if (patch.schemaVersion !== 'pptx-patch/v1') {
    push(errors, 'patch-schema-version', 'patch.json schemaVersion must be "pptx-patch/v1"')
  }
  if (!Array.isArray(patch.ops)) {
    push(errors, 'patch-ops-missing', 'patch.json must contain ops[]')
    return
  }

  const deckkitTokens = collectDeckkitTokens(deckkitIdFrom(lock, content))
  const allowedColors = collectAllowedColors(lock)
  for (const color of deckkitTokens.colors) allowedColors.add(color)
  if (allowedColors.size > 0) {
    const usedColors = collectPatchColors(patch)
    const unknown = [...usedColors].filter((color) => !allowedColors.has(color))
    for (const color of unknown) {
      push(
        args.strictColors ? errors : warnings,
        'patch-color-outside-lock',
        `patch uses color #${color} that is not declared in deck_lock.json`,
      )
    }
  }

  const allowedFonts = collectAllowedFonts(lock)
  for (const font of deckkitTokens.fonts) allowedFonts.add(font)
  if (allowedFonts.size > 0) {
    for (const item of collectPatchFonts(patch)) {
      if (!allowedFonts.has(item.font.toLowerCase())) {
        push(
          args.strictFonts ? errors : warnings,
          'patch-font-outside-lock',
          `patch uses font "${item.font}" outside deck_lock typography at ${item.path}`,
        )
      }
    }
  }

  const addSlideCount = patch.ops.filter(
    (op) => op?.op === 'add-slide' || op?.type === 'add-slide',
  ).length
  if (addSlideCount > 0 && Array.isArray(lock.slides) && addSlideCount !== lock.slides.length) {
    push(
      warnings,
      'patch-slide-count-mismatch',
      `patch adds ${addSlideCount} slide(s), deck_lock has ${lock.slides.length}; verify this is not an edit flow`,
    )
  }

  const patchAssetPaths = collectAssetPaths(patch)
  patch.ops.forEach((op, index) => {
    if (!isPlainObject(op)) return
    if (
      ['add-chart', 'set-chart-data'].includes(op.op) ||
      String(op.op ?? '').startsWith('set-chart-')
    ) {
      if (['add-chart', 'set-chart-data'].includes(op.op)) {
        const slideIndex = Number.isInteger(op.slide) ? op.slide : op.slideIndex
        const intent = Number.isInteger(slideIndex) ? (lock.slides?.[slideIndex] ?? null) : null
        checkChartSemantic(op, index, intent, errors, warnings)
      }
    }
    if (
      ['add-table', 'set-table-data'].includes(op.op) ||
      String(op.op ?? '').startsWith('set-table-') ||
      op.op === 'merge-table-cells'
    ) {
      if (['add-table', 'set-table-data'].includes(op.op)) {
        checkTableSemantic(op, index, errors, warnings)
      }
    }
  })

  if (patchAssetPaths.length > 0 && !assets) {
    push(
      errors,
      'assets-manifest-missing',
      'patch references assetSource.path but --assets was not provided',
    )
  }

  const registeredAssetPaths = assets ? manifestAssetPaths(assets) : new Set()
  for (const field of patchAssetPaths) {
    const normalizedPath = normalizeAssetPath(field.value)
    if (isAbsolute(field.value)) {
      push(
        warnings,
        'patch-absolute-asset-path',
        `patch uses absolute asset path at ${field.path}; prefer run-dir assets_manifest + --asset-root`,
      )
    }
    if (assets && normalizedPath && !registeredAssetPaths.has(normalizedPath)) {
      push(
        errors,
        'patch-asset-not-manifested',
        `patch asset path "${field.value}" at ${field.path} is not registered in assets_manifest.json`,
      )
    }
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const errors = []
  const warnings = []

  const lock = readJson(args.lock, 'deck_lock.json')
  const assets = args.assets ? readJson(args.assets, 'assets_manifest.json') : null
  const content = args.content ? readJson(args.content, 'content.json') : null
  const patch = args.patch ? readJson(args.patch, 'patch.json') : null
  const sessionRules = checkSessionRules(lock, args.lock, errors)
  const referencedAssets = new Set([
    ...lockAssetReferences(lock),
    ...contentAssetReferences(content),
  ])

  checkLock(lock, errors, warnings)
  if (!assets && referencedAssets.size > 0) {
    push(
      errors,
      'assets-manifest-missing',
      'deck/content references slide assets but --assets was not provided',
    )
  } else if (!assets && lock.assetsManifestPath) {
    push(
      warnings,
      'assets-manifest-not-checked',
      'deck_lock has assetsManifestPath but --assets was not provided',
    )
  }
  checkAssets(assets, args.assets, referencedAssets, errors, warnings)
  checkContent(content, lock, errors, warnings)
  checkPatch(patch, lock, content, assets, args, errors, warnings)
  if (content?.meta?.deckProfile === 'animation-corpus') {
    if (!patch)
      push(
        errors,
        'corpus-patch-missing',
        'animation-corpus requires the composed patch for authored-effect validation',
      )
    else errors.push(...inspectAnimationCorpus(content, patch).errors)
  }

  const report = {
    schemaVersion: 'pptx-nova-lock-check/v1',
    valid: errors.length === 0,
    summary: {
      errors: errors.length,
      warnings: warnings.length,
      slides: Array.isArray(lock.slides) ? lock.slides.length : 0,
      assets: assets ? assetEntries(assets).length : 0,
      patchOps: patch?.ops?.length ?? 0,
      sessionRules: sessionRules?.rules?.length ?? 0,
    },
    errors,
    warnings,
  }

  if (args.json) {
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
  } else {
    for (const error of errors) console.error(`[error] ${error.code}: ${error.message}`)
    for (const warning of warnings) console.error(`[warn]  ${warning.code}: ${warning.message}`)
    process.stdout.write(
      report.valid
        ? `Valid with ${warnings.length} warning(s).\n`
        : `Failed with ${errors.length} error(s), ${warnings.length} warning(s).\n`,
    )
  }

  if (!report.valid) process.exit(1)
}

try {
  main()
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(1)
}
