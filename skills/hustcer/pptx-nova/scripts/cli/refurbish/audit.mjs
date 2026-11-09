#!/usr/bin/env node
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const SCHEMA_VERSION = 'pptx-nova-refurbish-audit/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/refurbish/audit.mjs \\
    --source-pptx source.pptx \\
    --final-pptx final.pptx [options]

Options:
  --source-pptx <path>             Required source deck, the content truth.
  --final-pptx <path>              Required candidate/final refurbished deck.
  --source-inspect <path>          Optional xdoc inspect JSON for source deck.
  --final-inspect <path>           Optional xdoc inspect JSON for final deck.
  --reference-map <path>           Optional reference-map.json for slide coverage.
  --output <path>                  Optional path to write the JSON report.
  --forbidden-shape-name-regex <re> Fail when final inspect contains matching shape names. May repeat.
  --json                           Print machine-readable JSON report.
  --help                           Show this help.

Recommended placement:
  Run after apply + final inspect for Refurbish Existing Deck workflows.

Notes:
  This script intentionally uses only Node built-in modules. It reads PPTX XML
  through the system unzip command, matching the rest of pptx-nova scripts.
`

function parseArgs(argv) {
  const args = {
    sourcePptx: '',
    finalPptx: '',
    sourceInspect: '',
    finalInspect: '',
    referenceMap: '',
    output: '',
    forbiddenShapeNameRegex: [],
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--source-pptx') {
      args.sourcePptx = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--final-pptx' || arg === '--candidate-pptx') {
      args.finalPptx = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--source-inspect') {
      args.sourceInspect = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--final-inspect' || arg === '--candidate-inspect') {
      args.finalInspect = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--reference-map') {
      args.referenceMap = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--output' || arg === '-o') {
      args.output = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--forbidden-shape-name-regex') {
      args.forbiddenShapeNameRegex.push(valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.sourcePptx) throw new Error(`--source-pptx is required\n\n${usage}`)
  if (!args.finalPptx) throw new Error(`--final-pptx is required\n\n${usage}`)
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

function maybeReadJson(path, label, warnings) {
  if (!path) return null
  if (!existsSync(path)) {
    push(warnings, 'warning', 'missing-input', `${label} does not exist: ${path}`, { path })
    return null
  }
  return readJson(path, label)
}

function push(list, severity, code, message, details = {}) {
  list.push({ severity, code, message, ...details })
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function zipEntries(pptx) {
  try {
    return execFileSync('unzip', ['-Z1', pptx], {
      encoding: 'utf8',
      maxBuffer: 50 * 1024 * 1024,
    })
      .split(/\r?\n/)
      .filter(Boolean)
  } catch (error) {
    throw new Error(`Failed to list PPTX entries with unzip for ${pptx}: ${error.message}`)
  }
}

function pptxPart(pptx, partName) {
  try {
    return execFileSync('unzip', ['-p', pptx, partName], {
      encoding: 'utf8',
      maxBuffer: 50 * 1024 * 1024,
    })
  } catch (error) {
    throw new Error(`Failed to read ${partName} from ${pptx}: ${error.message}`)
  }
}

function slideEntries(pptx) {
  return zipEntries(pptx)
    .filter((entry) => /^ppt\/slides\/slide\d+\.xml$/.test(entry))
    .map((entry) => ({ entry, slideNumber: slideNumberFromEntry(entry) }))
    .filter((item) => Number.isFinite(item.slideNumber))
    .sort((a, b) => a.slideNumber - b.slideNumber)
}

function slideNumberFromEntry(entry) {
  const match = /slide(\d+)\.xml$/.exec(entry)
  return match ? Number(match[1]) : Number.NaN
}

function decodeXmlText(value) {
  return String(value)
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
}

function textsFromSlideXml(xml) {
  return [...String(xml).matchAll(/<a:t(?:\s+[^>]*)?>([\s\S]*?)<\/a:t>/g)]
    .map((match) => decodeXmlText(match[1]))
    .filter((text) => text.length > 0)
}

function normalizeText(value) {
  return String(value).replace(/\s+/g, ' ').trim()
}

function xmlTextLeaks(texts) {
  return texts.filter((text) =>
    /<\/?[A-Za-z][A-Za-z0-9_.-]*:|xmlns[:=]|<\/?(?:a|p|c|r):/.test(text),
  )
}

function xmlShapeTypeCounts(xml) {
  const textBoxes = countMatches(xml, /<p:cNvSpPr\b[^>]*\btxBox="1"/g)
  const shapes = countMatches(xml, /<p:sp\b/g)
  return compactCounts({
    autoShapeOrTextBox: shapes,
    textBox: textBoxes,
    picture: countMatches(xml, /<p:pic\b/g),
    connector: countMatches(xml, /<p:cxnSp\b/g),
    group: countMatches(xml, /<p:grpSp\b/g),
    table: countMatches(xml, /<a:tbl\b/g),
    chart: countMatches(xml, /<c:chart\b/g),
    graphicFrame: countMatches(xml, /<p:graphicFrame\b/g),
  })
}

function countMatches(value, regex) {
  return [...String(value).matchAll(regex)].length
}

function compactCounts(counts) {
  return Object.fromEntries(Object.entries(counts).filter(([, value]) => Number(value) > 0))
}

function inspectSlide(inspect, index) {
  return asArray(inspect?.slides).find((slide) => Number(slide.index) === Number(index))
}

function inspectShapeTypeCounts(inspect, index) {
  const slide = inspectSlide(inspect, index)
  if (!slide) return null
  const counts = {}
  for (const shape of asArray(slide.shapes)) {
    const type = String(shape?.shapeType || 'unknown')
    counts[type] = (counts[type] || 0) + 1
  }
  return counts
}

function slideCountFromInspect(inspect) {
  return inspect?.presentation?.slideCount ?? asArray(inspect?.slides).length
}

function compareCounts(sourceCounts, finalCounts) {
  const reduced = []
  for (const [type, source] of Object.entries(sourceCounts || {})) {
    const final = Number(finalCounts?.[type] || 0)
    if (final < Number(source)) reduced.push({ type, source: Number(source), final })
  }
  return reduced
}

function mediaCount(pptx) {
  return zipEntries(pptx).filter((entry) => /^ppt\/media\//.test(entry)).length
}

function notesCount(pptx) {
  return zipEntries(pptx).filter((entry) => /^ppt\/notesSlides\/notesSlide\d+\.xml$/.test(entry))
    .length
}

function externalHyperlinkCount(pptx) {
  let count = 0
  for (const entry of zipEntries(pptx).filter((item) =>
    /^ppt\/slides\/_rels\/slide\d+\.xml\.rels$/.test(item),
  )) {
    const xml = pptxPart(pptx, entry)
    for (const match of String(xml).matchAll(/<Relationship\b[^>]*>/g)) {
      const rel = match[0]
      if (/Type="[^"]*\/hyperlink"/.test(rel) && /TargetMode="External"/.test(rel)) count += 1
    }
  }
  return count
}

function sourceSlideIndexOf(entry) {
  const value =
    entry?.sourceSlide ?? entry?.sourceIndex ?? entry?.fromSlide ?? entry?.referenceSlide
  return Number(value)
}

function outputSlidesOf(entry) {
  if (Array.isArray(entry?.outputSlides)) return entry.outputSlides.map(Number)
  const value = entry?.outputSlide ?? entry?.outputIndex ?? entry?.slide
  return Number.isFinite(Number(value)) ? [Number(value)] : []
}

function auditReferenceMap({ referenceMap, sourceSlideCount, finalSlideCount, findings }) {
  if (!referenceMap) {
    push(
      findings,
      'warning',
      'missing-reference-map',
      'No reference-map.json was provided; slide ownership coverage was not audited.',
    )
    return
  }

  const approvedChanges = asArray(referenceMap.approvedChanges)
  const mappedSources = new Set()
  const mappedOutputs = new Set()

  for (const entry of asArray(referenceMap.slides)) {
    const source = sourceSlideIndexOf(entry)
    if (Number.isInteger(source)) mappedSources.add(source)
    for (const output of outputSlidesOf(entry)) {
      if (Number.isInteger(output)) mappedOutputs.add(output)
    }
  }

  const missingSources = range(sourceSlideCount).filter((index) => !mappedSources.has(index))
  const missingOutputs = range(finalSlideCount).filter((index) => !mappedOutputs.has(index))

  if (missingSources.length) {
    push(
      findings,
      'error',
      'reference-map-missing-source-slides',
      'reference-map.json does not cover every source slide.',
      {
        missingSources,
      },
    )
  }
  if (missingOutputs.length) {
    push(
      findings,
      'error',
      'reference-map-missing-output-slides',
      'reference-map.json does not cover every output slide.',
      {
        missingOutputs,
      },
    )
  }
  if (sourceSlideCount !== finalSlideCount && !approvedChanges.length) {
    push(
      findings,
      'error',
      'slide-count-changed-without-approval',
      'Slide count changed without approvedChanges in reference-map.json.',
      {
        sourceSlideCount,
        finalSlideCount,
      },
    )
  }
}

function range(length) {
  return Array.from({ length }, (_, index) => index)
}

function compileRegexes(patterns, findings) {
  const regexes = []
  for (const pattern of patterns) {
    try {
      regexes.push(new RegExp(pattern))
    } catch (error) {
      push(
        findings,
        'error',
        'invalid-forbidden-shape-name-regex',
        `Invalid forbidden shape name regex: ${pattern}`,
        {
          pattern,
          error: error.message,
        },
      )
    }
  }
  return regexes
}

function auditForbiddenShapeNames({ finalInspect, regexes, findings }) {
  if (!regexes.length) return
  if (!finalInspect) {
    push(
      findings,
      'warning',
      'forbidden-shape-name-scan-skipped',
      'Forbidden shape name scan requires --final-inspect.',
    )
    return
  }

  const matches = []
  for (const slide of asArray(finalInspect.slides)) {
    for (const shape of asArray(slide.shapes)) {
      const name = String(shape?.name || '')
      if (regexes.some((regex) => regex.test(name))) {
        matches.push({ slide: Number(slide.index) + 1, name, id: shape.id })
      }
    }
  }

  if (matches.length) {
    push(
      findings,
      'error',
      'forbidden-shape-name-found',
      'Final deck contains forbidden shape names.',
      { matches },
    )
  }
}

function buildAudit(args) {
  const findings = []

  for (const [label, path] of [
    ['source PPTX', args.sourcePptx],
    ['final PPTX', args.finalPptx],
  ]) {
    if (!existsSync(path))
      push(findings, 'error', 'missing-input', `${label} does not exist: ${path}`, { path })
  }
  if (findings.some((item) => item.severity === 'error')) {
    return makeReport({ args, findings, slides: [] })
  }

  const sourceInspect = maybeReadJson(args.sourceInspect, 'source inspect', findings)
  const finalInspect = maybeReadJson(args.finalInspect, 'final inspect', findings)
  const referenceMap = maybeReadJson(args.referenceMap, 'reference map', findings)

  if (!sourceInspect || !finalInspect) {
    push(
      findings,
      'warning',
      'inspect-json-missing',
      'Source/final inspect JSON was not fully provided; shape type counts use rough OOXML fallback.',
    )
  }

  const sourceSlideEntries = slideEntries(args.sourcePptx)
  const finalSlideEntries = slideEntries(args.finalPptx)
  const sourceSlideCount = sourceInspect
    ? slideCountFromInspect(sourceInspect)
    : sourceSlideEntries.length
  const finalSlideCount = finalInspect
    ? slideCountFromInspect(finalInspect)
    : finalSlideEntries.length

  if (sourceSlideCount !== finalSlideCount && !asArray(referenceMap?.approvedChanges).length) {
    push(findings, 'error', 'slide-count-mismatch', 'Source and final slide counts differ.', {
      sourceSlideCount,
      finalSlideCount,
    })
  }

  auditReferenceMap({ referenceMap, sourceSlideCount, finalSlideCount, findings })

  const slides = []
  const slideLimit = Math.min(sourceSlideEntries.length, finalSlideEntries.length)
  for (let i = 0; i < slideLimit; i += 1) {
    const sourceEntry = sourceSlideEntries[i]
    const finalEntry = finalSlideEntries[i]
    const sourceXml = pptxPart(args.sourcePptx, sourceEntry.entry)
    const finalXml = pptxPart(args.finalPptx, finalEntry.entry)
    const sourceTexts = textsFromSlideXml(sourceXml)
    const finalTexts = textsFromSlideXml(finalXml)
    const finalJoined = normalizeText(finalTexts.join(' '))
    const missingSourceTexts = [...new Set(sourceTexts.map(normalizeText).filter(Boolean))].filter(
      (text) => !finalJoined.includes(text),
    )
    const finalXmlLeaks = xmlTextLeaks(finalTexts)
    const sourceShapeTypes =
      inspectShapeTypeCounts(sourceInspect, i) || xmlShapeTypeCounts(sourceXml)
    const finalShapeTypes = inspectShapeTypeCounts(finalInspect, i) || xmlShapeTypeCounts(finalXml)
    const reducedShapeTypes = compareCounts(sourceShapeTypes, finalShapeTypes)

    if (missingSourceTexts.length) {
      push(
        findings,
        'error',
        'source-text-missing',
        `Final slide ${i + 1} is missing source text.`,
        {
          slide: i + 1,
          count: missingSourceTexts.length,
          sample: missingSourceTexts.slice(0, 8),
        },
      )
    }
    if (finalXmlLeaks.length) {
      push(
        findings,
        'error',
        'ooxml-text-leak',
        `Final slide ${i + 1} contains visible OOXML-like text.`,
        {
          slide: i + 1,
          count: finalXmlLeaks.length,
          sample: finalXmlLeaks.slice(0, 8),
        },
      )
    }
    if (reducedShapeTypes.length) {
      push(
        findings,
        'error',
        'shape-type-count-reduced',
        `Final slide ${i + 1} has fewer objects of a source shape type.`,
        {
          slide: i + 1,
          reducedShapeTypes,
        },
      )
    }

    slides.push({
      slideIndex: i,
      slideNumber: i + 1,
      sourceTextRunCount: sourceTexts.length,
      finalTextRunCount: finalTexts.length,
      missingSourceTexts,
      finalXmlLeaks,
      sourceShapeTypes,
      finalShapeTypes,
      reducedShapeTypes,
    })
  }

  const sourceMediaCount = mediaCount(args.sourcePptx)
  const finalMediaCount = mediaCount(args.finalPptx)
  if (finalMediaCount < sourceMediaCount) {
    push(
      findings,
      'error',
      'media-count-reduced',
      'Final deck has fewer media parts than source deck.',
      {
        sourceMediaCount,
        finalMediaCount,
      },
    )
  }

  const sourceNotesCount = notesCount(args.sourcePptx)
  const finalNotesCount = notesCount(args.finalPptx)
  if (finalNotesCount < sourceNotesCount) {
    push(
      findings,
      'error',
      'notes-count-reduced',
      'Final deck has fewer notes slides than source deck.',
      {
        sourceNotesCount,
        finalNotesCount,
      },
    )
  }

  const sourceExternalHyperlinkCount = externalHyperlinkCount(args.sourcePptx)
  const finalExternalHyperlinkCount = externalHyperlinkCount(args.finalPptx)
  if (finalExternalHyperlinkCount < sourceExternalHyperlinkCount) {
    push(
      findings,
      'error',
      'external-hyperlink-count-reduced',
      'Final deck has fewer external hyperlinks than source deck.',
      {
        sourceExternalHyperlinkCount,
        finalExternalHyperlinkCount,
      },
    )
  }

  const forbiddenShapeNameRegexes = compileRegexes(args.forbiddenShapeNameRegex, findings)
  auditForbiddenShapeNames({ finalInspect, regexes: forbiddenShapeNameRegexes, findings })

  return makeReport({
    args,
    findings,
    slides,
    sourceSlideCount,
    finalSlideCount,
    sourceMediaCount,
    finalMediaCount,
    sourceNotesCount,
    finalNotesCount,
    sourceExternalHyperlinkCount,
    finalExternalHyperlinkCount,
  })
}

function makeReport({
  args,
  findings,
  slides,
  sourceSlideCount = 0,
  finalSlideCount = 0,
  sourceMediaCount = 0,
  finalMediaCount = 0,
  sourceNotesCount = 0,
  finalNotesCount = 0,
  sourceExternalHyperlinkCount = 0,
  finalExternalHyperlinkCount = 0,
}) {
  const errors = findings.filter((item) => item.severity === 'error')
  const warnings = findings.filter((item) => item.severity === 'warning')
  const missingSourceTextRunTotal = slides.reduce(
    (sum, slide) => sum + slide.missingSourceTexts.length,
    0,
  )
  const finalXmlLeakTotal = slides.reduce((sum, slide) => sum + slide.finalXmlLeaks.length, 0)
  const reducedShapeTypeTotal = slides.reduce(
    (sum, slide) => sum + slide.reducedShapeTypes.length,
    0,
  )

  return {
    schemaVersion: SCHEMA_VERSION,
    status: errors.length ? 'failed' : 'passed',
    source: args.sourcePptx,
    final: args.finalPptx,
    inputs: {
      sourceInspect: args.sourceInspect || null,
      finalInspect: args.finalInspect || null,
      referenceMap: args.referenceMap || null,
    },
    summary: {
      errors: errors.length,
      warnings: warnings.length,
      sourceSlideCount,
      finalSlideCount,
      slideCountMatches: sourceSlideCount === finalSlideCount,
      missingSourceTextRunTotal,
      finalXmlLeakTotal,
      reducedShapeTypeTotal,
      sourceMediaCount,
      finalMediaCount,
      sourceNotesCount,
      finalNotesCount,
      sourceExternalHyperlinkCount,
      finalExternalHyperlinkCount,
      slidesWithMissingSourceText: slides
        .filter((slide) => slide.missingSourceTexts.length)
        .map((slide) => slide.slideNumber),
      slidesWithFinalXmlLeaks: slides
        .filter((slide) => slide.finalXmlLeaks.length)
        .map((slide) => slide.slideNumber),
      slidesWithReducedShapeTypes: slides
        .filter((slide) => slide.reducedShapeTypes.length)
        .map((slide) => slide.slideNumber),
    },
    findings,
    slides,
  }
}

function humanSummary(report) {
  const lines = []
  lines.push(`Refurbish audit: ${report.status}`)
  lines.push(`slides: ${report.summary.sourceSlideCount} -> ${report.summary.finalSlideCount}`)
  lines.push(`errors: ${report.summary.errors}`)
  lines.push(`warnings: ${report.summary.warnings}`)
  lines.push(`missing source text runs: ${report.summary.missingSourceTextRunTotal}`)
  lines.push(`OOXML text leaks: ${report.summary.finalXmlLeakTotal}`)
  lines.push(`reduced shape-type entries: ${report.summary.reducedShapeTypeTotal}`)
  for (const finding of report.findings.slice(0, 20)) {
    lines.push(`- ${finding.severity}: ${finding.code}: ${finding.message}`)
  }
  if (report.findings.length > 20) lines.push(`... ${report.findings.length - 20} more findings`)
  return `${lines.join('\n')}\n`
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const report = buildAudit(args)
  const json = `${JSON.stringify(report, null, 2)}\n`

  if (args.output) writeFileSync(args.output, json)
  if (args.json || !args.output) {
    process.stdout.write(args.json ? json : humanSummary(report))
  }
  if (report.status !== 'passed') process.exitCode = 1
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error.message}\n`)
  process.exitCode = 1
}
