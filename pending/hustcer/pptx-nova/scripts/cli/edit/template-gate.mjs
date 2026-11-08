#!/usr/bin/env node
import { inflateRawSync } from 'node:zlib'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { evaluateReviewPolicy, hasEmbeddedReviewedFindings } from '../../lib/review/policy.mjs'

const FRAME_SCHEMA_VERSION = 'pptx-nova-template-frame-map/v1'
const GATE_SCHEMA_VERSION = 'pptx-nova-template-gate/v1'

const REUSE_MODES = new Set([
  'duplicate-slide',
  'copy-slide',
  'slide-copy',
  'template-fill',
  'fill-template',
  'fill-placeholder',
  'preserve',
  'allowed-insertion',
  'insert',
])
const ADD_OPS = new Set([
  'add-text-box',
  'add-shape',
  'add-image',
  'add-table',
  'add-chart',
  'add-placeholder',
  'add-equation',
  'add-ole-object',
  'add-video',
  'add-group',
  'add-connector',
  'add-freeform',
])
const IDENTITY_KINDS = new Set([
  'logo',
  'customer-mark',
  'customer-logo',
  'brand-mark',
  'screenshot',
  'product-ui',
  'product-screenshot',
  'app-icon',
  'person-photo',
  'headshot',
  'event-photo',
])
const ALLOWED_IDENTITY_SOURCE_KINDS = new Set(['user', 'source-deck', 'official', 'built-in'])
const DISALLOWED_IDENTITY_SOURCE_KINDS = new Set([
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
const DEFAULT_TEXT_RE =
  /^(click to add|title goes here|subtitle goes here|name goes here|date|footer|slide number|单击此处|单击添加|添加标题|添加副标题|页脚|日期|幻灯片编号)$/i

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/template-gate.mjs \\
    --frame-map template-frame-map.json \\
    --source-inspect template-inspect.json [options]

Options:
  --frame-map <path>       Required template-frame-map.json.
  --source-inspect <path>  Required xdoc inspect JSON for the source/template deck.
  --source-pptx <path>     Source/template PPTX used for hash-bound reviewed findings.
  --edit-plan <path>       Optional template-edit-plan.json.
  --template-audit <path>  Optional template-audit.json.
  --assets <path>          Optional assets_manifest.json.
  --patch <path>           Optional xdoc patch JSON for edit/addition checks.
  --dry-run <path>         Optional xdoc dry-run JSON for selector/error checks.
  --final-inspect <path>   Optional xdoc inspect JSON for final deck.
  --final-pptx <path>      Optional final/starter PPTX for OOXML placeholder scan.
  --review-policy <path>   Optional pptx-nova-review-policy/v1 document.
  --json                   Print machine-readable report.
  --help                   Show this help.

Recommended placement:
  Run after dry-run/apply for strict template following, before final delivery.
`

function parseArgs(argv) {
  const args = {
    frameMap: '',
    sourceInspect: '',
    sourcePptx: '',
    editPlan: '',
    templateAudit: '',
    assets: '',
    patch: '',
    dryRun: '',
    finalInspect: '',
    finalPptx: '',
    reviewPolicy: '',
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--frame-map') {
      args.frameMap = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--source-inspect') {
      args.sourceInspect = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--source-pptx') {
      args.sourcePptx = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--edit-plan') {
      args.editPlan = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--template-audit') {
      args.templateAudit = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--assets') {
      args.assets = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--patch') {
      args.patch = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--dry-run') {
      args.dryRun = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--final-inspect') {
      args.finalInspect = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--final-pptx') {
      args.finalPptx = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--review-policy') {
      args.reviewPolicy = resolve(valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.frameMap) throw new Error(`--frame-map is required\n\n${usage}`)
  if (!args.sourceInspect) throw new Error(`--source-inspect is required\n\n${usage}`)
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

function push(list, severity, code, message, details = {}) {
  list.push({ severity, code, message, ...details })
}

function isPlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value)
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function findEndOfCentralDirectory(buffer) {
  for (let offset = buffer.length - 22; offset >= 0; offset -= 1) {
    if (buffer.readUInt32LE(offset) === 0x06054b50) return offset
  }
  throw new Error('PPTX ZIP end of central directory was not found')
}

function readZipEntries(path) {
  const buffer = readFileSync(path)
  const eocd = findEndOfCentralDirectory(buffer)
  const entryCount = buffer.readUInt16LE(eocd + 10)
  const centralOffset = buffer.readUInt32LE(eocd + 16)
  const entries = []
  let cursor = centralOffset
  for (let index = 0; index < entryCount; index += 1) {
    if (buffer.readUInt32LE(cursor) !== 0x02014b50) {
      throw new Error(`Invalid ZIP central directory entry at ${cursor}`)
    }
    const method = buffer.readUInt16LE(cursor + 10)
    const compressedSize = buffer.readUInt32LE(cursor + 20)
    const uncompressedSize = buffer.readUInt32LE(cursor + 24)
    const fileNameLength = buffer.readUInt16LE(cursor + 28)
    const extraLength = buffer.readUInt16LE(cursor + 30)
    const commentLength = buffer.readUInt16LE(cursor + 32)
    const localOffset = buffer.readUInt32LE(cursor + 42)
    const name = buffer.toString('utf8', cursor + 46, cursor + 46 + fileNameLength)
    cursor += 46 + fileNameLength + extraLength + commentLength
    if (buffer.readUInt32LE(localOffset) !== 0x04034b50) {
      throw new Error(`Invalid ZIP local file header for ${name}`)
    }
    const localNameLength = buffer.readUInt16LE(localOffset + 26)
    const localExtraLength = buffer.readUInt16LE(localOffset + 28)
    const dataStart = localOffset + 30 + localNameLength + localExtraLength
    const compressed = buffer.subarray(dataStart, dataStart + compressedSize)
    let data
    if (method === 0) data = compressed
    else if (method === 8) data = inflateRawSync(compressed)
    else continue
    if (uncompressedSize !== 0 && data.length !== uncompressedSize) {
      throw new Error(`ZIP entry size mismatch for ${name}`)
    }
    entries.push({ name, data })
  }
  return entries
}

function slideCountOf(inspect) {
  return inspect?.presentation?.slideCount ?? inspect?.slides?.length ?? 0
}

function inspectSlide(inspect, index) {
  return asArray(inspect?.slides).find((slide) => Number(slide.index) === Number(index))
}

function outputSlides(frameMap) {
  return asArray(frameMap.outputSlides ?? frameMap.slides)
}

function slideIndexOf(entry) {
  return Number(entry.outputSlide ?? entry.slide ?? entry.outputIndex ?? entry.index)
}

function sourceSlideIndexOf(entry) {
  return Number(entry.sourceSlide ?? entry.templateSlide ?? entry.fromSlide)
}

function editTargetsOf(entry) {
  return asArray(entry.editTargets ?? entry.targets)
}

function normalizeAction(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
}

function isInsertionMode(entry) {
  const mode = normalizeAction(entry.reuseMode ?? entry.reuse ?? entry.mode)
  return mode === 'allowed-insertion' || mode === 'insert'
}

function allowedInsertionKeys(frameMap, editPlan) {
  const keys = new Set()
  for (const entry of outputSlides(frameMap)) {
    const slide = slideIndexOf(entry)
    const mode = normalizeAction(entry.reuseMode ?? entry.reuse ?? entry.mode)
    if (mode === 'allowed-insertion' || mode === 'insert') keys.add(`slide:${slide}:*`)
    for (const target of editTargetsOf(entry)) {
      const action = normalizeAction(target.action ?? target.intent)
      if (['add', 'insert', 'allowed-insertion', 'replace'].includes(action)) {
        keys.add(`slide:${slide}:*`)
        const name = target.name ?? target.shape?.name ?? target.newShapeName
        if (name) keys.add(`slide:${slide}:name:${name}`)
      }
    }
  }
  for (const item of asArray(editPlan?.edits ?? editPlan?.operations ?? editPlan?.slides)) {
    if (Array.isArray(item?.edits)) {
      for (const edit of item.edits) collectAllowedEdit(keys, item.slide ?? item.outputSlide, edit)
    } else {
      collectAllowedEdit(keys, item.slide ?? item.outputSlide, item)
    }
  }
  return keys
}

function collectAllowedEdit(keys, slide, edit) {
  const action = normalizeAction(edit?.action ?? edit?.intent)
  if (!['add', 'insert', 'allowed-insertion', 'replace'].includes(action)) return
  const slideIndex = Number(slide ?? edit.slide ?? edit.outputSlide)
  if (!Number.isFinite(slideIndex)) return
  keys.add(`slide:${slideIndex}:*`)
  const name = edit.name ?? edit.shape?.name ?? edit.newShapeName
  if (name) keys.add(`slide:${slideIndex}:name:${name}`)
}

function validateFrameMap({ frameMap, sourceInspect, errors, warnings }) {
  if (frameMap.schemaVersion && frameMap.schemaVersion !== FRAME_SCHEMA_VERSION) {
    push(
      warnings,
      'warning',
      'frame-map-schema-version',
      `template-frame-map schemaVersion is "${frameMap.schemaVersion}", expected ${FRAME_SCHEMA_VERSION}`,
    )
  }
  const slides = outputSlides(frameMap)
  if (slides.length === 0) {
    push(errors, 'error', 'frame-map-empty', 'template-frame-map must contain outputSlides[]')
    return
  }

  const sourceCount = slideCountOf(sourceInspect)
  const seenOutputs = new Set()
  for (const [index, entry] of slides.entries()) {
    const outputSlide = slideIndexOf(entry)
    const sourceSlide = sourceSlideIndexOf(entry)
    const mode = normalizeAction(entry.reuseMode ?? entry.reuse ?? entry.mode)
    if (!Number.isInteger(outputSlide) || outputSlide < 0) {
      push(
        errors,
        'error',
        'frame-map-output-slide-invalid',
        `outputSlides[${index}] has invalid outputSlide`,
      )
    } else if (seenOutputs.has(outputSlide)) {
      push(
        errors,
        'error',
        'frame-map-output-slide-duplicate',
        `output slide ${outputSlide} is mapped more than once`,
      )
    } else {
      seenOutputs.add(outputSlide)
    }

    if (!mode) {
      push(
        warnings,
        'warning',
        'frame-map-reuse-mode-missing',
        `outputSlides[${index}] should declare reuseMode`,
      )
    } else if (!REUSE_MODES.has(mode)) {
      push(
        warnings,
        'warning',
        'frame-map-reuse-mode-unknown',
        `outputSlides[${index}] uses unknown reuseMode "${mode}"`,
      )
    }

    if (!isInsertionMode(entry)) {
      if (!Number.isInteger(sourceSlide) || sourceSlide < 0) {
        push(
          errors,
          'error',
          'frame-map-source-slide-missing',
          `outputSlides[${index}] must map to sourceSlide`,
        )
      } else if (sourceSlide >= sourceCount) {
        push(
          errors,
          'error',
          'frame-map-source-slide-oob',
          `sourceSlide ${sourceSlide} is outside source deck slide count ${sourceCount}`,
        )
      }
    } else if (!entry.reason && !entry.notes) {
      push(
        warnings,
        'warning',
        'frame-map-insertion-reason-missing',
        `outputSlides[${index}] insertion should record a reason`,
      )
    }

    if (!Array.isArray(entry.editTargets)) {
      push(
        warnings,
        'warning',
        'frame-map-edit-targets-missing',
        `outputSlides[${index}] should include editTargets[]; use [] for preserve-only`,
      )
    }
    for (const [targetIndex, target] of editTargetsOf(entry).entries()) {
      const action = normalizeAction(target.action ?? target.intent)
      if (!action) {
        push(
          warnings,
          'warning',
          'frame-map-edit-action-missing',
          `outputSlides[${index}].editTargets[${targetIndex}] should declare action`,
        )
      }
      if (
        !target.shape &&
        !target.shapeId &&
        !target.sourceElementId &&
        !target.name &&
        !target.placeholder
      ) {
        push(
          warnings,
          'warning',
          'frame-map-edit-selector-missing',
          `outputSlides[${index}].editTargets[${targetIndex}] should identify an inherited object or placeholder`,
        )
      }
    }
  }

  const sorted = [...seenOutputs].sort((a, b) => a - b)
  sorted.forEach((value, index) => {
    if (value !== index) {
      push(
        warnings,
        'warning',
        'frame-map-output-slide-gap',
        `outputSlides are not contiguous from 0; first gap near ${index}`,
      )
      return false
    }
    return true
  })
}

function validateDryRun({ dryRun, errors, warnings }) {
  if (!dryRun) return
  const status = dryRun.status ?? dryRun.summary?.status
  if (status && status !== 'success' && status !== 'ok') {
    push(errors, 'error', 'dry-run-not-success', `dry-run status is ${status}`)
  }
  for (const result of asArray(dryRun.opResults ?? dryRun.summary?.opResults)) {
    if (result.status === 'error') {
      push(errors, 'error', 'dry-run-op-error', `dry-run op ${result.opIndex ?? '?'} failed`, {
        opIndex: result.opIndex,
        error: result.error,
      })
    }
  }
  for (const risk of asArray(dryRun.visualRisks ?? dryRun.summary?.visualRisks)) {
    if (risk.severity === 'high' || risk.severity === 'medium') {
      push(
        warnings,
        'warning',
        'dry-run-visual-risk',
        `dry-run reported ${risk.severity} visual risk ${risk.code ?? ''}`.trim(),
        { risk },
      )
    }
  }
}

function validatePatchAdditions({ patch, frameMap, sourceInspect, editPlan, errors, warnings }) {
  if (!patch) return
  const slides = outputSlides(frameMap)
  const mapByOutput = new Map(slides.map((entry) => [slideIndexOf(entry), entry]))
  const allowedKeys = allowedInsertionKeys(frameMap, editPlan)
  const ops = asArray(patch.ops)

  for (const [opIndex, op] of ops.entries()) {
    const opName = normalizeAction(op.op)
    if (opName === 'add-slide') {
      const slide = Number(op.slide ?? op.index ?? op.at ?? opIndex)
      const mapped = mapByOutput.get(slide)
      if (!mapped || !isInsertionMode(mapped)) {
        push(
          errors,
          'error',
          'template-add-slide-unmapped',
          `op ${opIndex} adds a slide without an allowed insertion mapping`,
          { opIndex, op: compactOp(op) },
        )
      }
      continue
    }
    if (!ADD_OPS.has(opName)) continue

    const slide = Number(op.slide)
    const mapped = mapByOutput.get(slide)
    const name = op.name ?? op.shape?.name ?? ''
    const isAllowed =
      allowedKeys.has(`slide:${slide}:*`) ||
      (name && allowedKeys.has(`slide:${slide}:name:${name}`))
    if (!isAllowed) {
      push(
        errors,
        'error',
        'template-unplanned-new-object',
        `op ${opIndex} adds ${opName} on slide ${slide} without an allowed insertion in frame map/edit plan`,
        { opIndex, op: compactOp(op) },
      )
    }

    if (!mapped || !Number.isFinite(slide)) continue
    const bbox = opBBox(op)
    if (!bbox) {
      push(
        warnings,
        'warning',
        'template-added-object-no-bbox',
        `op ${opIndex} adds ${opName} but has no complete x/y/w/h for overlay analysis`,
        { opIndex },
      )
      continue
    }
    const sourceSlide = inspectSlide(sourceInspect, sourceSlideIndexOf(mapped))
    for (const shape of asArray(sourceSlide?.shapes)) {
      const sourceBox = inspectShapeBBox(shape)
      if (!sourceBox) continue
      const ratio = overlapRatio(bbox, sourceBox)
      if (ratio >= 0.35) {
        push(
          warnings,
          'warning',
          'template-overlay-risk',
          `op ${opIndex} adds ${opName} over ${Math.round(ratio * 100)}% of source shape "${shape.name ?? shape.id ?? '?'}"`,
          {
            opIndex,
            sourceSlide: sourceSlideIndexOf(mapped),
            outputSlide: slide,
            sourceShape: sourceShapeSummary(shape),
            ratio,
          },
        )
        break
      }
    }
  }
}

function compactOp(op) {
  const out = { op: op.op, slide: op.slide }
  for (const key of ['name', 'shape', 'x', 'y', 'w', 'h']) {
    if (op[key] !== undefined) out[key] = op[key]
  }
  return out
}

function opBBox(op) {
  const x = unitToInches(op.x)
  const y = unitToInches(op.y)
  const w = unitToInches(op.w)
  const h = unitToInches(op.h)
  if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) return null
  return { x, y, w, h }
}

function unitToInches(value) {
  if (typeof value === 'number') return value
  const text = String(value ?? '').trim()
  if (!text) return NaN
  const match = text.match(/^(-?\d+(?:\.\d+)?)(in|pt|px|emu)?$/i)
  if (!match) return NaN
  const n = Number(match[1])
  const unit = (match[2] ?? 'in').toLowerCase()
  if (unit === 'in') return n
  if (unit === 'pt') return n / 72
  if (unit === 'px') return n / 96
  if (unit === 'emu') return n / 914400
  return NaN
}

function inspectShapeBBox(shape) {
  const bbox = shape?.bbox
  if (!bbox) return null
  const x = emuToInches(bbox.xEmu ?? bbox.x)
  const y = emuToInches(bbox.yEmu ?? bbox.y)
  const w = emuToInches(bbox.wEmu ?? bbox.w)
  const h = emuToInches(bbox.hEmu ?? bbox.h)
  if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) return null
  return { x, y, w, h }
}

function emuToInches(value) {
  if (value === undefined || value === null || value === '') return NaN
  return Number(value) / 914400
}

function overlapRatio(a, b) {
  const x1 = Math.max(a.x, b.x)
  const y1 = Math.max(a.y, b.y)
  const x2 = Math.min(a.x + a.w, b.x + b.w)
  const y2 = Math.min(a.y + a.h, b.y + b.h)
  const w = Math.max(0, x2 - x1)
  const h = Math.max(0, y2 - y1)
  const area = w * h
  if (area <= 0) return 0
  return area / Math.min(a.w * a.h, b.w * b.h)
}

function sourceShapeSummary(shape) {
  return {
    id: shape.id,
    name: shape.name,
    shapeType: shape.shapeType,
    textPreview: shape.textPreview,
  }
}

function validateFinalInspect({ finalInspect, errors }) {
  if (!finalInspect) return
  for (const slide of asArray(finalInspect.slides)) {
    for (const shape of asArray(slide.shapes)) {
      const text = normalizeText(shape.textPreview ?? shape.text ?? '')
      if (text && DEFAULT_TEXT_RE.test(text)) {
        push(
          errors,
          'error',
          'template-default-placeholder-text',
          `final slide ${slide.index} still contains placeholder/sample text "${text}"`,
          { slide: slide.index, shape: sourceShapeSummary(shape) },
        )
      }
    }
  }
}

function collectFinalPptxPlaceholderFindings({ finalPptx, errors, warnings }) {
  const findings = []
  if (!finalPptx) return findings
  if (!existsSync(finalPptx)) {
    push(errors, 'error', 'final-pptx-missing', `final PPTX does not exist: ${finalPptx}`)
    return findings
  }
  let slideEntries = []
  try {
    slideEntries = readZipEntries(finalPptx)
      .filter((entry) => /^ppt\/slides\/slide\d+\.xml$/.test(entry.name))
      .sort((a, b) => slideNumber(a.name) - slideNumber(b.name))
  } catch (error) {
    push(
      warnings,
      'warning',
      'final-pptx-placeholder-scan-skipped',
      `could not read PPTX ZIP entries: ${error.message}`,
    )
    return findings
  }

  for (const entry of slideEntries) {
    const slideName = entry.name
    const slide = slideNumber(slideName) - 1
    const xml = entry.data.toString('utf8')
    for (const shapeXml of xml.match(/<p:sp\b[\s\S]*?<\/p:sp>/g) ?? []) {
      if (!/<p:ph\b/.test(shapeXml)) continue
      const ph = placeholderInfo(shapeXml)
      const text = normalizeText(extractText(shapeXml))
      const name = shapeName(shapeXml)
      const id = shapeId(shapeXml)
      if (!text) {
        findings.push({
          severity: 'error',
          classification: 'actionable',
          code: 'empty-placeholder',
          message: `final slide ${slide} has empty structural placeholder ${ph.type || '(unknown)'}`,
          slide,
          slideIndex: slide,
          slidePart: slideName,
          objectId: id,
          objectName: name,
          placeholder: ph,
          observed: { textEmpty: true },
        })
      } else if (DEFAULT_TEXT_RE.test(text)) {
        push(
          errors,
          'error',
          'template-default-placeholder-text',
          `final slide ${slide} still contains placeholder/sample text "${text}"`,
          { slide, placeholder: ph, name },
        )
      }
    }
  }
  return findings
}

function slideNumber(path) {
  return Number(path.match(/slide(\d+)\.xml$/)?.[1] ?? 0)
}

function legacyEmptyPlaceholderDeclarations(editPlan) {
  const declarations = []
  const visit = (value, slideHint) => {
    if (Array.isArray(value)) {
      for (const item of value) visit(item, slideHint)
      return
    }
    if (!isPlainObject(value)) return
    const slide = Number(value.slide ?? value.outputSlide ?? slideHint)
    const action = normalizeAction(value.action ?? value.intent)
    if (
      (value.allowEmptyPlaceholder === true || action === 'allow-empty-placeholder') &&
      Number.isFinite(slide)
    ) {
      const ph = value.placeholder ?? value.shape?.placeholder ?? {}
      declarations.push({ slide, placeholder: ph })
    }
    for (const child of Object.values(value))
      visit(child, Number.isFinite(slide) ? slide : slideHint)
  }
  visit(editPlan, undefined)
  return declarations
}

function placeholderInfo(xml) {
  const tag = xml.match(/<p:ph\b[^>]*>/)?.[0] ?? ''
  return {
    type: attr(tag, 'type') ?? '',
    idx: attr(tag, 'idx') ?? '',
  }
}

function shapeName(xml) {
  const tag = xml.match(/<p:cNvPr\b[^>]*>/)?.[0] ?? ''
  return attr(tag, 'name') ?? ''
}

function shapeId(xml) {
  const tag = xml.match(/<p:cNvPr\b[^>]*>/)?.[0] ?? ''
  return attr(tag, 'id') ?? ''
}

function attr(tag, name) {
  const re = new RegExp(`\\b${name}="([^"]*)"`)
  return decodeXml(tag.match(re)?.[1] ?? '')
}

function extractText(xml) {
  return (xml.match(/<a:t\b[^>]*>([\s\S]*?)<\/a:t>/g) ?? [])
    .map((item) => item.replace(/<[^>]+>/g, ''))
    .map(decodeXml)
    .join('')
}

function normalizeText(value) {
  return String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim()
}

function decodeXml(value) {
  return String(value ?? '')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
}

function assetEntries(assets) {
  if (!assets) return []
  if (Array.isArray(assets.entries)) return assets.entries
  if (Array.isArray(assets.assets)) return assets.assets
  return []
}

function isIdentityAsset(entry) {
  const kind = String(entry?.kind ?? '').toLowerCase()
  const role = String(entry?.pptxUse?.role ?? entry?.role ?? '').toLowerCase()
  return IDENTITY_KINDS.has(kind) || IDENTITY_KINDS.has(role)
}

function validateAssetProvenance({ assets, audit, errors, warnings }) {
  const entries = assetEntries(assets)
  const byId = new Map(entries.map((entry) => [entry.id, entry]))
  for (const entry of entries) {
    if (!isIdentityAsset(entry)) continue
    const id = entry.id ?? '(missing id)'
    const status = String(entry.status ?? 'available').toLowerCase()
    const sourceKind = String(entry.source?.kind ?? entry.sourceKind ?? '').toLowerCase()
    if (['missing', 'needs-user', 'placeholder'].includes(status)) {
      push(
        errors,
        'error',
        'identity-asset-not-ready',
        `identity asset ${id} is not ready: status=${status}`,
      )
    }
    if (!sourceKind) {
      push(
        errors,
        'error',
        'identity-asset-source-missing',
        `identity asset ${id} must declare source.kind`,
      )
    } else if (DISALLOWED_IDENTITY_SOURCE_KINDS.has(sourceKind)) {
      push(
        errors,
        'error',
        'identity-asset-generated',
        `identity asset ${id} cannot come from generated/AI source.kind=${sourceKind}`,
      )
    } else if (!ALLOWED_IDENTITY_SOURCE_KINDS.has(sourceKind)) {
      push(
        errors,
        'error',
        'identity-asset-source-unapproved',
        `identity asset ${id} uses unapproved source.kind=${sourceKind}`,
      )
    }
    if (
      !entry.source?.licenseNote &&
      !entry.source?.url &&
      !entry.source?.originalPath &&
      sourceKind !== 'built-in'
    ) {
      push(
        warnings,
        'warning',
        'identity-asset-provenance-thin',
        `identity asset ${id} should record licenseNote, url, or originalPath`,
      )
    }
  }

  for (const item of asArray(audit?.identityAssets ?? audit?.assets)) {
    const id = item.assetId ?? item.id
    const status = String(item.status ?? item.permissionStatus ?? '').toLowerCase()
    const kind = String(item.kind ?? item.role ?? '').toLowerCase()
    if (!IDENTITY_KINDS.has(kind) && !id) continue
    if (['missing', 'needs-user', 'unverified', 'unknown', 'placeholder'].includes(status)) {
      push(
        errors,
        'error',
        'audit-identity-asset-unready',
        `template audit marks identity asset ${id ?? kind} as ${status}`,
      )
    }
    if (id && !byId.has(id)) {
      push(
        warnings,
        'warning',
        'audit-identity-asset-not-in-manifest',
        `template audit identity asset ${id} is not present in assets_manifest.json`,
      )
    }
  }
}

function evaluateTemplateReviewPolicy({ args, editPlan, explicitReviewPolicy, findings, errors }) {
  const legacyDeclarations = legacyEmptyPlaceholderDeclarations(editPlan)
  if (legacyDeclarations.length > 0) {
    push(
      errors,
      'error',
      'legacy-empty-placeholder-exception',
      'allowEmptyPlaceholder/allow-empty-placeholder is no longer an auditable exception; migrate it to pptx-nova-review-policy/v1',
      { declarations: legacyDeclarations },
    )
  }

  const embeddedPolicy = hasEmbeddedReviewedFindings(editPlan) ? editPlan : null
  if (explicitReviewPolicy && embeddedPolicy) {
    push(
      errors,
      'error',
      'review-policy-source-ambiguous',
      'reviewed findings must come from either --review-policy or the edit plan, not both',
    )
  }
  const policyDocument = explicitReviewPolicy ?? embeddedPolicy
  const policyDocumentPath = explicitReviewPolicy
    ? args.reviewPolicy
    : embeddedPolicy
      ? args.editPlan
      : ''
  const evaluation = evaluateReviewPolicy({
    policyDocument,
    policyDocumentPath,
    allowEmbeddedPolicy: Boolean(!explicitReviewPolicy && embeddedPolicy),
    sourcePptx: args.sourcePptx,
    candidatePptx: args.finalPptx,
    findings,
  })
  for (const item of evaluation.errors) {
    push(errors, 'error', item.code, item.message, {
      source: 'review-policy',
      details: item,
    })
  }
  for (const finding of evaluation.remainingActionable) {
    push(errors, 'error', 'template-empty-structural-placeholder', finding.message, {
      slide: finding.slideIndex,
      part: finding.slidePart,
      shapeId: finding.objectId,
      placeholder: finding.placeholder,
    })
  }
  return evaluation
}

function buildReport({ args, errors, warnings, reviewPolicy }) {
  const bySeverity = {}
  for (const item of [...errors, ...warnings])
    bySeverity[item.severity] = (bySeverity[item.severity] ?? 0) + 1
  return {
    schemaVersion: GATE_SCHEMA_VERSION,
    status: errors.length > 0 ? 'error' : warnings.length > 0 ? 'warning' : 'ok',
    inputs: Object.fromEntries(
      Object.entries(args).filter(([, value]) => value && typeof value === 'string'),
    ),
    summary: {
      errors: errors.length,
      warnings: warnings.length,
      bySeverity,
      declaredReviews: reviewPolicy?.summary?.declaredReviewCount ?? 0,
      appliedReviews: reviewPolicy?.summary?.appliedReviewCount ?? 0,
      reviewedFindings: reviewPolicy?.summary?.reviewedFindingCount ?? 0,
      remainingActionableFindings: reviewPolicy?.summary?.remainingActionableCount ?? 0,
    },
    reviewPolicy,
    errors,
    warnings,
  }
}

function printReport(report, json) {
  if (json) {
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
    return
  }
  process.stdout.write(`Template gate: ${report.status}\n`)
  process.stdout.write(`- errors: ${report.summary.errors}\n`)
  process.stdout.write(`- warnings: ${report.summary.warnings}\n`)
  for (const item of [...report.errors, ...report.warnings]) {
    process.stdout.write(`  [${item.severity}] ${item.code}: ${item.message}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const frameMap = readJson(args.frameMap, 'template-frame-map')
  const sourceInspect = readJson(args.sourceInspect, 'source inspect')
  const editPlan = args.editPlan ? readJson(args.editPlan, 'template edit plan') : null
  const explicitReviewPolicy = args.reviewPolicy
    ? readJson(args.reviewPolicy, 'review policy')
    : null
  const audit = args.templateAudit ? readJson(args.templateAudit, 'template audit') : null
  const assets = args.assets ? readJson(args.assets, 'assets manifest') : null
  const patch = args.patch ? readJson(args.patch, 'patch') : null
  const dryRun = args.dryRun ? readJson(args.dryRun, 'dry-run') : null
  const finalInspect = args.finalInspect ? readJson(args.finalInspect, 'final inspect') : null

  const errors = []
  const warnings = []

  validateFrameMap({ frameMap, sourceInspect, errors, warnings })
  validateDryRun({ dryRun, errors, warnings })
  validatePatchAdditions({ patch, frameMap, sourceInspect, editPlan, errors, warnings })
  validateFinalInspect({ finalInspect, errors })
  const placeholderFindings = collectFinalPptxPlaceholderFindings({
    finalPptx: args.finalPptx,
    errors,
    warnings,
  })
  const reviewPolicy = evaluateTemplateReviewPolicy({
    args,
    editPlan,
    explicitReviewPolicy,
    findings: placeholderFindings,
    errors,
  })
  validateAssetProvenance({ assets, audit, errors, warnings })

  const report = buildReport({ args, errors, warnings, reviewPolicy })
  printReport(report, args.json)
  process.exit(report.status === 'error' ? 1 : 0)
} catch (error) {
  const report = {
    schemaVersion: GATE_SCHEMA_VERSION,
    status: 'error',
    summary: { errors: 1, warnings: 0, bySeverity: { error: 1 } },
    errors: [{ severity: 'error', code: 'template-gate-fatal', message: error.message }],
    warnings: [],
  }
  printReport(report, process.argv.includes('--json'))
  process.exit(1)
}
