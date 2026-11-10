#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fallbackFor, hexFrom, luminance } from '../../lib/refurbish/style.mjs'

const CATALOG_PATH = join(SKILL_ROOT, 'assets/deckkits/catalog.json')

function sha256File(path) {
  return existsSync(path) ? createHash('sha256').update(readFileSync(path)).digest('hex') : null
}

const usage = `Usage:
  node <skill-root>/scripts/cli/refurbish/fallback-patch.mjs --deckkit <id> --inspect reference-inspect.json [options]

Options:
  --deckkit <id>       Target DeckKit id
  --inspect <path>     xdoc pptx inspect JSON for the source deck
  --source <path>      Source PPTX path recorded in generated artifacts
  --output <path>      Candidate/final PPTX path recorded in generated artifacts
  --catalog <path>     DeckKit catalog path. Defaults to <skill-root>/assets/deckkits/catalog.json
  --chrome-detect <path>
                       Optional xdoc pptx chrome-detect JSON report
  --patch <path>       Output patch JSON. Defaults to patch.json
  --lock <path>        Output deck_lock JSON. Defaults to deck_lock.json
  --audit <path>       Output content-audit JSON. Defaults to content-audit.json
  --map <path>         Output reference-map JSON. Defaults to reference-map.json
  --json               Print machine-readable summary
  --help               Show this help
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    inspect: '',
    source: 'source.pptx',
    output: 'candidate.pptx',
    catalog: CATALOG_PATH,
    chromeDetect: '',
    patch: 'patch.json',
    lock: 'deck_lock.json',
    audit: 'content-audit.json',
    map: 'reference-map.json',
    json: false,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg in flagSet) {
      args[flagSet[arg]] = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.deckkit) throw new Error(`--deckkit is required.\n\n${usage}`)
  if (!args.inspect) throw new Error(`--inspect is required.\n\n${usage}`)
  args.catalog = resolve(args.catalog)
  return args
}

const flagSet = {
  '--deckkit': 'deckkit',
  '--inspect': 'inspect',
  '--source': 'source',
  '--output': 'output',
  '--catalog': 'catalog',
  '--chrome-detect': 'chromeDetect',
  '--patch': 'patch',
  '--lock': 'lock',
  '--audit': 'audit',
  '--map': 'map',
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function readChromeDetect(path) {
  if (!path) return null
  const report = readJson(path)
  if (report?.schemaVersion !== 'pptx-chrome-detect/v1') {
    throw new Error(`--chrome-detect must point to a pptx-chrome-detect/v1 report: ${path}`)
  }
  return report
}

function srgbChannel(value) {
  const channel = value / 255
  return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
}

function relativeLuminance(hex) {
  const value = hexFrom(hex)
  if (!value) return 1
  const r = srgbChannel(parseInt(value.slice(0, 2), 16))
  const g = srgbChannel(parseInt(value.slice(2, 4), 16))
  const b = srgbChannel(parseInt(value.slice(4, 6), 16))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contrastRatio(foreground, background) {
  const fg = relativeLuminance(foreground)
  const bg = relativeLuminance(background)
  const light = Math.max(fg, bg)
  const dark = Math.min(fg, bg)
  return (light + 0.05) / (dark + 0.05)
}

function uniqueColors(values) {
  const seen = new Set()
  return values
    .map(hexFrom)
    .filter(Boolean)
    .filter((value) => {
      if (seen.has(value)) return false
      seen.add(value)
      return true
    })
}

function contrastSafeColor(preferred, background, fallback) {
  const bg = hexFrom(background) || fallback.palette.background
  for (const color of uniqueColors([
    preferred,
    fallback.palette.text,
    fallback.palette.accent,
    fallback.palette.secondary,
    '7A241A',
    '374151',
    fallback.palette.background,
    fallback.palette.surface,
    '111111',
    'FFFFFF',
  ])) {
    if (contrastRatio(color, bg) >= 4.5) return color
  }
  return relativeLuminance(bg) < 0.45 ? 'FFFFFF' : '111111'
}

function fontRoleForShape(shape) {
  const name = shape.name ?? ''
  const text = (shape.textPreview ?? '').trim()
  if (/sub[-_\s]*(?:title|headline|heading)/i.test(name)) return 'body'
  if (/title|headline|heading|(?:^|[_\s-])hero(?:$|[_\s-])/i.test(name)) return 'heading'
  if (/Eyebrow|Kicker|Foot|PageNum|Label|Badge/i.test(name)) return 'label'
  if (/Val|Num|Score|Pct|Metric/i.test(name) || /^[0-9.→+\-%年]+$/.test(text)) return 'heading'
  return 'body'
}

function fontForShape(shape, fallback, backgroundColor) {
  const role = fontRoleForShape(shape)
  const color = role === 'label' ? fallback.palette.secondary : fallback.palette.text
  return {
    name: fallback.fonts[role],
    color: contrastSafeColor(color, backgroundColor, fallback),
    ...(role === 'heading' ? { bold: fallback.headingBold ?? true } : {}),
    ...(role === 'label' ? { bold: true } : {}),
  }
}

function fillForShape(shape, fallback) {
  const original = shape.fillColor ?? ''
  if (!original) return null
  const lum = luminance(original)
  const text = (shape.textPreview ?? '').trim()
  if (!text && /Dot|Tick|Rule|Line/i.test(shape.name ?? '')) return fallback.palette.accent
  if (lum < 0.28) return fallback.palette.accent
  if (lum > 0.86) return fallback.palette.surface
  if (lum > 0.65) return fallback.palette.softAccent
  return fallback.palette.softAccent
}

function slideTextShapes(slide) {
  return (Array.isArray(slide.shapes) ? slide.shapes : []).filter((shape) =>
    (shape.textPreview ?? '').trim(),
  )
}

function slideTitle(slide) {
  const textShapes = slideTextShapes(slide)
  const titleShape =
    textShapes.find((shape) => /(^|_)Title$|_Title|title/i.test(shape.name ?? '')) ??
    textShapes.find((shape) => Number(shape.fontSizePt ?? shape.fontSize ?? 0) >= 18) ??
    textShapes[0]
  return (titleShape?.textPreview ?? `Source slide ${Number(slide.index) + 1}`).trim()
}

function refurbishRhythmFor(index, count) {
  if (index === 0 || index === count - 1) return 'anchor'
  return index % 2 === 0 ? 'breathing' : 'dense'
}

function densityForSlide(slide) {
  const stats = slide.semantic?.elementStats ?? {}
  const total = Number(stats.total ?? (Array.isArray(slide.shapes) ? slide.shapes.length : 0))
  const text = Number(stats.text ?? slideTextShapes(slide).length)
  if (total >= 36 || text >= 20) return 'high'
  if (total >= 18 || text >= 10) return 'medium'
  return 'low'
}

function emu(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : 0
}

function bboxOf(shape) {
  const bbox = shape?.bbox
  if (!bbox) return null
  const x = emu(bbox.xEmu)
  const y = emu(bbox.yEmu)
  const w = emu(bbox.wEmu)
  const h = emu(bbox.hEmu)
  if (w <= 0 || h <= 0) return null
  return { x, y, w, h, cx: x + w / 2, cy: y + h / 2, area: w * h }
}

function containsPoint(box, x, y) {
  return x >= box.x && x <= box.x + box.w && y >= box.y && y <= box.y + box.h
}

function overlapRatio(inner, outer) {
  const left = Math.max(inner.x, outer.x)
  const top = Math.max(inner.y, outer.y)
  const right = Math.min(inner.x + inner.w, outer.x + outer.w)
  const bottom = Math.min(inner.y + inner.h, outer.y + outer.h)
  if (right <= left || bottom <= top) return 0
  return ((right - left) * (bottom - top)) / inner.area
}

function textBackgroundForShape(shape, slideShapes, targetFills, fallback) {
  const ownFill = targetFills.get(shape.id)
  if (ownFill) return ownFill

  const box = bboxOf(shape)
  if (!box) return fallback.palette.background

  let best = null
  for (const candidate of slideShapes) {
    if (candidate === shape || candidate.shapeType !== 'autoShape') continue
    const fill = targetFills.get(candidate.id)
    if (!fill) continue
    const candidateBox = bboxOf(candidate)
    if (!candidateBox) continue
    const containsCenter = containsPoint(candidateBox, box.cx, box.cy)
    const overlap = overlapRatio(box, candidateBox)
    if (!containsCenter && overlap < 0.6) continue
    const score = (containsCenter ? 2 : 0) + overlap - candidateBox.area / 1e16
    if (!best || score > best.score) best = { score, fill }
  }

  return best?.fill ?? fallback.palette.background
}

function chromeKey(slide, shapeId) {
  return `${Number(slide)}:${String(shapeId ?? '')}`
}

function chromeShapeId(candidate) {
  return candidate?.shapeId ?? candidate?.patchSelector?.shape?.id
}

function summarizeChromeCandidate(candidate) {
  return {
    slide: candidate.slide,
    role: candidate.role,
    confidence: candidate.confidence,
    shapeId: chromeShapeId(candidate),
    shapeName: candidate.shapeName ?? '',
    patchSelector: candidate.patchSelector ?? {
      slide: candidate.slide,
      shape: { id: chromeShapeId(candidate) },
    },
  }
}

function chromeModelFrom(report) {
  if (!report) {
    return {
      status: 'not-provided',
      summary: null,
      candidates: [],
      duplicateRoles: [],
      byShape: new Map(),
      warnings: [
        'No chrome-detect report was provided; existing header/footer/page-number/rule chrome was not classified.',
      ],
    }
  }
  const highConfidence = (Array.isArray(report.candidates) ? report.candidates : [])
    .filter((candidate) => Number(candidate.confidence) >= 0.75)
    .map(summarizeChromeCandidate)
  const byShape = new Map()
  const bySlideRole = new Map()
  for (const candidate of highConfidence) {
    const key = chromeKey(candidate.slide, candidate.shapeId)
    const current = byShape.get(key)
    if (!current || Number(candidate.confidence) > Number(current.confidence))
      byShape.set(key, candidate)

    const slideRole = `${candidate.slide}:${candidate.role}`
    const entries = bySlideRole.get(slideRole) ?? []
    entries.push(candidate)
    bySlideRole.set(slideRole, entries)
  }
  const duplicateRoles = [...bySlideRole.entries()]
    .filter(([, entries]) => entries.length > 1)
    .map(([key, entries]) => {
      const [slide, role] = key.split(':')
      return {
        slide: Number(slide),
        role,
        count: entries.length,
        shapeIds: entries.map((entry) => entry.shapeId),
      }
    })
  const warnings = duplicateRoles.map(
    (item) =>
      `Slide ${item.slide} has ${item.count} high-confidence ${item.role} chrome candidates; fallback restyles them but does not remove duplicates.`,
  )
  return {
    status: 'loaded',
    summary: report.summary ?? null,
    candidates: highConfidence,
    duplicateRoles,
    byShape,
    warnings,
  }
}

function chromeCandidateForShape(model, slideIndex, shape) {
  return model.byShape.get(chromeKey(slideIndex, shape.id))
}

function chromeCandidatesForSlide(model, slideIndex) {
  return model.candidates.filter((candidate) => Number(candidate.slide) === Number(slideIndex))
}

function duplicateChromeForSlide(model, slideIndex) {
  return model.duplicateRoles.filter((item) => Number(item.slide) === Number(slideIndex))
}

function chromeOutput(model) {
  return {
    status: model.status,
    summary: model.summary,
    highConfidenceCount: model.candidates.length,
    duplicateRoles: model.duplicateRoles,
    warnings: model.warnings,
  }
}

function chromeFontFor(role, fallback, backgroundColor) {
  const preferred = role === 'header' ? fallback.palette.text : fallback.palette.secondary
  return {
    name: fallback.fonts.label,
    color: contrastSafeColor(preferred, backgroundColor, fallback),
    bold: role === 'header' || role === 'page-number',
  }
}

function targetStyleFingerprint(inspect, themeColors, fonts) {
  const themes = Array.isArray(inspect?.presentation?.themes) ? inspect.presentation.themes : []
  const relatedThemes = themes.filter(
    (theme) =>
      (Array.isArray(theme?.usedBySlides) && theme.usedBySlides.length > 0) ||
      (Array.isArray(theme?.usedByMasters) && theme.usedByMasters.length > 0),
  )
  const relevantThemes = relatedThemes.length > 0 ? relatedThemes : themes
  const target = {
    colors: themeColors,
    fonts: {
      major: {
        latin: fonts.major.typeface,
        eastAsian: fonts.major.eastAsian,
      },
      minor: {
        latin: fonts.minor.typeface,
        eastAsian: fonts.minor.eastAsian,
      },
    },
  }
  const targetSha256 = createHash('sha256').update(JSON.stringify(target)).digest('hex')
  if (relevantThemes.length !== 1) {
    return {
      relevantThemeCount: relevantThemes.length,
      themeColorsMatchTarget: null,
      fontMatchesTarget: null,
      themeMatchesTarget: null,
      target: { ...target, sha256: targetSha256 },
    }
  }
  const theme = relevantThemes[0]
  const currentColors = Object.fromEntries(
    (Array.isArray(theme?.colors) ? theme.colors : [])
      .map((entry) => [entry?.scheme, hexFrom(entry?.value)])
      .filter(([scheme, color]) => scheme && color),
  )
  const themeColorsMatchTarget = Object.entries(themeColors).every(
    ([scheme, color]) => currentColors[scheme] === hexFrom(color),
  )
  const fontMatchesTarget =
    theme?.majorFont?.latin === fonts.major.typeface &&
    theme?.majorFont?.ea === fonts.major.eastAsian &&
    theme?.minorFont?.latin === fonts.minor.typeface &&
    theme?.minorFont?.ea === fonts.minor.eastAsian
  return {
    relevantThemeCount: 1,
    themePartName: theme?.partName ?? null,
    themeColorsMatchTarget,
    fontMatchesTarget,
    themeMatchesTarget: themeColorsMatchTarget && fontMatchesTarget,
    target: { ...target, sha256: targetSha256 },
  }
}

function createOperationEmitter(ops, styleFingerprint) {
  const audit = {
    plannedOps: 0,
    emittedOps: 0,
    knownNoOpOps: 0,
    effectiveOps: null,
    knownChangingOps: 0,
    unknownEffectOps: 0,
    byOp: {},
    pruningReasons: {},
    styleFingerprint,
    evidenceNote:
      'knownNoOpOps contains only inspect-proven exact no-ops. effectiveOps remains null because deck-level diff cannot attribute effects to individual operations.',
  }
  const emit = (op, effect = 'unknown-effect', reason = '') => {
    const opType = op.op
    const byOp = audit.byOp[opType] ?? {
      planned: 0,
      emitted: 0,
      knownNoOp: 0,
      knownChanging: 0,
      unknownEffect: 0,
    }
    byOp.planned += 1
    audit.plannedOps += 1
    if (effect === 'known-no-op') {
      byOp.knownNoOp += 1
      audit.knownNoOpOps += 1
      if (reason) audit.pruningReasons[reason] = (audit.pruningReasons[reason] ?? 0) + 1
    } else {
      ops.push(op)
      byOp.emitted += 1
      audit.emittedOps += 1
      if (effect === 'known-changing') {
        byOp.knownChanging += 1
        audit.knownChangingOps += 1
      } else {
        byOp.unknownEffect += 1
        audit.unknownEffectOps += 1
      }
    }
    audit.byOp[opType] = byOp
  }
  return { emit, audit }
}

function appendChromeRestyleOps(emit, slideIndex, shape, candidate, fallback, backgroundColor) {
  const selector = candidate.patchSelector?.shape ?? { id: shape.id }
  if (shape.hasText || (shape.textPreview ?? '').trim()) {
    emit({
      op: 'set-text-frame',
      slide: slideIndex,
      shape: selector,
      font: chromeFontFor(candidate.role, fallback, backgroundColor),
    })
  }
  if (candidate.role === 'rule') {
    emit({
      op: 'set-shape',
      slide: slideIndex,
      shape: selector,
      line: { width: '0.5pt', color: fallback.palette.rule },
    })
  }
}

function buildArtifacts(args) {
  const catalog = readJson(args.catalog)
  const entry = catalog.entries.find((candidate) => candidate.id === args.deckkit)
  if (!entry) throw new Error(`DeckKit "${args.deckkit}" is missing from catalog`)
  const inspect = readJson(args.inspect)
  const chromeDetect = readChromeDetect(args.chromeDetect)
  const chrome = chromeModelFrom(chromeDetect)
  const fallback = fallbackFor(entry)
  const warnings = [...(fallback.derivationWarnings ?? []), ...chrome.warnings]
  const ops = []
  const palette = fallback.palette

  const themeColors = {
    dk1: palette.text,
    lt1: palette.background,
    dk2: palette.rule,
    lt2: palette.surface,
    accent1: palette.accent,
    accent2: palette.text,
    accent3: palette.softAccent,
    accent4: palette.secondary,
    accent5: palette.rule,
    accent6: palette.surface,
    hlink: palette.text,
    folHlink: palette.secondary,
  }
  const themeFonts = {
    major: { typeface: fallback.fonts.heading, eastAsian: fallback.fonts.cjk },
    minor: { typeface: fallback.fonts.body, eastAsian: fallback.fonts.cjk },
  }
  const styleFingerprint = targetStyleFingerprint(inspect, themeColors, themeFonts)
  const { emit, audit: operationAudit } = createOperationEmitter(ops, styleFingerprint)
  emit(
    {
      op: 'set-theme',
      colors: themeColors,
      fonts: themeFonts,
    },
    styleFingerprint.themeMatchesTarget === true
      ? 'known-no-op'
      : styleFingerprint.themeMatchesTarget === false
        ? 'known-changing'
        : 'unknown-effect',
    styleFingerprint.themeMatchesTarget === true ? 'theme-and-fonts-exact-match' : '',
  )
  emit({ op: 'set-master', background: { type: 'solid', color: palette.background } })
  emit({
    op: 'set-default-text-style',
    levels: [
      {
        level: 0,
        font: { name: fallback.fonts.body },
        color: palette.text,
        alignment: 'left',
      },
    ],
  })

  const slides = Array.isArray(inspect.slides) ? inspect.slides : []
  const canvas = {
    width: inspect.presentation?.size?.width ?? inspect.presentation?.slideSize?.width ?? '16:9',
    height: inspect.presentation?.size?.height ?? inspect.presentation?.slideSize?.height ?? '16:9',
    source: 'reference-inspect',
  }
  const outline = slides.map((slide) => ({
    slide: slide.index,
    title: slideTitle(slide),
    purpose: `Preserve and restyle source slide ${Number(slide.index) + 1}.`,
  }))
  const auditSlides = []
  const mapSlides = []
  for (const slide of slides) {
    const slideIndex = slide.index
    const stats = slide.semantic?.elementStats ?? {}
    emit({
      op: 'set-slide-background',
      slide: slideIndex,
      fill: { type: 'solid', color: palette.background },
      followMaster: false,
    })
    mapSlides.push({
      sourceSlide: slideIndex,
      outputSlides: [slideIndex],
      reuse: 'preserve-and-restyle',
      notes: '1:1 mapping; source editable objects are retained and restyled in place.',
    })
    auditSlides.push({
      sourceSlide: slideIndex,
      outputSlides: [slideIndex],
      status: 'preserved',
      text: { count: stats.text ?? 0, status: 'preserved' },
      tables: { count: stats.table ?? 0, status: 'preserved' },
      charts: { count: stats.chart ?? 0, status: 'preserved' },
      smartArtOrDiagrams: { count: slide.hasSmartArt ? 1 : 0, status: 'preserved' },
      imagesAndMedia: { count: (stats.picture ?? 0) + (stats.media ?? 0), status: 'preserved' },
      groupsAndShapes: {
        count: stats.total ?? 0,
        status: 'preserved',
        note: 'Native objects retained; eligible text, fill, and line styling is remapped.',
      },
      notes: { count: slide.hasNotes ? 1 : 0, status: 'preserved' },
      unsupportedObjects: {
        count: Array.isArray(slide.preserveOnly) ? slide.preserveOnly.length : 0,
        status:
          Array.isArray(slide.preserveOnly) && slide.preserveOnly.length ? 'blocked' : 'preserved',
      },
      chrome: {
        status: chrome.status === 'loaded' ? 'classified-and-restyled' : 'not-classified',
        policy: fallback.chromePolicy,
        candidates: chromeCandidatesForSlide(chrome, slideIndex),
        duplicateRoles: duplicateChromeForSlide(chrome, slideIndex),
      },
    })
    const slideShapes = Array.isArray(slide.shapes) ? slide.shapes : []
    const targetFills = new Map(
      slideShapes
        .filter((candidate) => candidate.shapeType === 'autoShape' && candidate.fillColor)
        .map((candidate) => [candidate.id, fillForShape(candidate, fallback)])
        .filter(([, fill]) => fill),
    )
    for (const shape of slideShapes) {
      const selector = { id: shape.id }
      const targetFill = targetFills.get(shape.id) ?? null
      const textBackground = textBackgroundForShape(shape, slideShapes, targetFills, fallback)
      const chromeCandidate = chromeCandidateForShape(chrome, slideIndex, shape)
      if (chromeCandidate) {
        appendChromeRestyleOps(emit, slideIndex, shape, chromeCandidate, fallback, textBackground)
        continue
      }
      if (shape.hasText && (shape.textPreview ?? '').trim()) {
        emit({
          op: 'set-text-frame',
          slide: slideIndex,
          shape: selector,
          font: fontForShape(shape, fallback, textBackground),
        })
      }
      if (shape.shapeType === 'autoShape' && shape.fillColor) {
        const color = targetFill
        if (color) {
          const fillIsExact =
            shape.fillType === 'solid' && hexFrom(shape.fillColor) === hexFrom(color)
          emit(
            {
              op: 'set-shape',
              slide: slideIndex,
              shape: selector,
              fill: { type: 'solid', color },
            },
            fillIsExact ? 'known-no-op' : 'known-changing',
            fillIsExact ? 'shape-solid-fill-exact-match' : '',
          )
        }
        if (!shape.lineNoFill) {
          emit({
            op: 'set-shape',
            slide: slideIndex,
            shape: selector,
            line: { width: '0.5pt', color: palette.rule },
          })
        }
      }
    }
  }

  const patch = {
    schemaVersion: 'pptx-patch/v1',
    metadata: {
      deckkit: entry.id,
      strategy: fallback.strategy,
      fallbackSource: fallback.source,
      chromeDetection: chromeOutput(chrome),
      source: args.source,
      output: args.output,
      warnings,
      notes: [
        'Generated by cli/refurbish/fallback-patch.mjs.',
        'This fallback preserves source slides and editable objects; it does not rasterize source slides.',
      ],
    },
    ops,
  }
  const deckLock = {
    schemaVersion: 'pptx-nova-deck-lock/v1',
    mode: 'Refurbish Existing Deck',
    outline,
    canvas,
    source: args.source,
    output: args.output,
    deckkit: entry.id,
    colors: {
      background: palette.background,
      text: palette.text,
      accent: palette.accent,
      softAccent: palette.softAccent,
      secondary: palette.secondary,
      surface: palette.surface,
      rule: palette.rule,
    },
    typography: {
      title: `${fallback.fonts.heading}, Arial`,
      heading: `${fallback.fonts.heading}, Arial`,
      body: `${fallback.fonts.body}, Times New Roman`,
      label: `${fallback.fonts.label}, Arial`,
      cjk: fallback.fonts.cjk,
    },
    readiness: {
      readiness: entry.readiness ?? '',
      nativeSkinning: Boolean(entry.nativeSkinning),
      fallbackSource: fallback.source,
      fallbackStrategy: fallback.strategy,
    },
    chromeDetection: chromeOutput(chrome),
    visualTarget: {
      palette,
      typography: fallback.fonts,
      chromePolicy: fallback.chromePolicy,
      contentPolicy: fallback.contentPolicy,
    },
    assumptions: [
      'No factual content is added or rewritten by the fallback patch generator.',
      'content-audit.json is a pre-apply preservation baseline; content-audit-final.json from xdoc pptx refurbish-audit remains required before delivery.',
      ...warnings.map((warning) => `Fallback warning: ${warning}`),
    ],
    slides: slides.map((slide, index) => ({
      index: slide.index,
      sourceSlide: slide.index,
      outputSlide: slide.index,
      slideType: 'preserve-restyle',
      title: slideTitle(slide),
      purpose: `Preserve source slide ${Number(slide.index) + 1} content while applying the ${entry.id} visual system.`,
      rhythm: refurbishRhythmFor(index, slides.length),
      visualDensity: densityForSlide(slide),
      layoutIntent: 'preserve source layout and restyle editable objects',
      contentStatus: 'preserved',
    })),
  }
  const audit = {
    schemaVersion: 'pptx-nova-content-audit/v1',
    phase: 'pre-apply-baseline',
    finalAuditRequired: true,
    source: args.source,
    final: args.output,
    strategy: fallback.strategy,
    deckkit: entry.id,
    fallbackSource: fallback.source,
    chromeDetection: chromeOutput(chrome),
    warnings,
    slides: auditSlides,
  }
  const referenceMap = {
    schemaVersion: 'pptx-nova-reference-map/v1',
    source: args.source,
    bindings: {
      sourceSha256: sha256File(args.source),
    },
    strategy: 'one-to-one editable-object restyle fallback',
    approvedChanges: [],
    reviewedFindings: [],
    slides: mapSlides,
  }
  return {
    patch,
    deckLock,
    audit,
    referenceMap,
    summary: {
      deckkit: entry.id,
      fallback,
      chromeDetection: chromeOutput(chrome),
      warnings,
      slideCount: slides.length,
      ops: operationAudit.emittedOps,
      operationAudit,
    },
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const artifacts = buildArtifacts(args)
  writeFileSync(args.patch, `${JSON.stringify(artifacts.patch, null, 2)}\n`)
  writeFileSync(args.lock, `${JSON.stringify(artifacts.deckLock, null, 2)}\n`)
  writeFileSync(args.audit, `${JSON.stringify(artifacts.audit, null, 2)}\n`)
  writeFileSync(args.map, `${JSON.stringify(artifacts.referenceMap, null, 2)}\n`)
  const result = {
    schemaVersion: 'pptx-nova-refurbish-fallback-patch-report/v1',
    status: 'success',
    outputs: {
      patch: args.patch,
      lock: args.lock,
      audit: args.audit,
      map: args.map,
    },
    summary: artifacts.summary,
  }
  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  else {
    process.stdout.write(
      `Generated fallback patch for ${result.summary.deckkit}: ${result.summary.ops} ops across ${result.summary.slideCount} slides\n`,
    )
  }
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
