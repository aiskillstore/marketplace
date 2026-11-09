#!/usr/bin/env node
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { createHash } from 'node:crypto'
import { basename, dirname, extname, join, resolve } from 'node:path'

const SCHEMA_VERSION = 'pptx-nova-compare-gate/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/compare-gate.mjs --run-dir <dir> --final-pptx <path> [options]

Validate and optionally publish one SHA-256-bound delivery bundle containing
the final PPTX and its before/after compare PNG sibling(s).

Options:
  --run-dir <dir>          Required current pptx-nova run directory.
  --final-pptx <path>      Required final PPTX path.
  --final-pptx-source <path>
                           Staged final PPTX. Required with --publish; otherwise optional.
  --kind <name>            Compare kind, e.g. translation or refurbish. Defaults to compare.
  --compare-stem <stem>    Artifact/published stem. Defaults to <kind>-compare.
  --compare <path>         Run-directory compare PNG. Defaults to <run-dir>/<compare-stem>.png.
  --report <path>          Run-directory compare JSON. Defaults to <run-dir>/<compare-stem>.json.
  --sibling <path>         Expected/published sibling PNG path.
  --publish                Atomically publish compare sibling(s), then the bound final PPTX.
  --timestamp <MMDDhhmmss> Timestamp suffix to use with --publish.
  --output <path>          Write gate JSON. Defaults to <run-dir>/<compare-stem>-gate.json.
  --overwrite              Allow replacing --output and, with --publish, --sibling.
  --json                   Print the gate JSON to stdout.
  --help                   Show this help.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = {
    runDir: '',
    finalPptx: '',
    finalPptxSource: '',
    kind: 'compare',
    compareStem: '',
    compare: '',
    report: '',
    sibling: '',
    publish: false,
    timestamp: '',
    output: '',
    overwrite: false,
    json: false,
  }

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--run-dir') {
      args.runDir = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--final-pptx') {
      args.finalPptx = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--final-pptx-source') {
      args.finalPptxSource = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--kind') {
      args.kind = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--compare-stem') {
      args.compareStem = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--compare') {
      args.compare = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--report') {
      args.report = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--sibling') {
      args.sibling = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--timestamp') {
      args.timestamp = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--output' || arg === '-o') {
      args.output = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--publish') {
      args.publish = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--json') {
      args.json = true
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.runDir) throw new Error(`--run-dir is required\n\n${usage}`)
  if (!args.finalPptx) throw new Error(`--final-pptx is required\n\n${usage}`)
  if (args.publish && !args.finalPptxSource) {
    throw new Error(`--final-pptx-source is required with --publish\n\n${usage}`)
  }

  args.runDir = resolve(args.runDir)
  args.finalPptx = resolve(args.finalPptx)
  if (args.finalPptxSource) args.finalPptxSource = resolve(args.finalPptxSource)
  args.kind = normalizeSlug(args.kind || 'compare')
  args.compareStem = normalizeSlug(args.compareStem || `${args.kind}-compare`)
  args.compare = resolve(args.compare || join(args.runDir, `${args.compareStem}.png`))
  args.report = resolve(args.report || join(args.runDir, `${args.compareStem}.json`))
  args.output = resolve(args.output || join(args.runDir, `${args.compareStem}-gate.json`))
  if (args.sibling) args.sibling = resolve(args.sibling)
  return args
}

function normalizeSlug(value) {
  const normalized = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return normalized || 'compare'
}

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    return {
      __parseError: error instanceof Error ? error.message : String(error),
    }
  }
}

function fileState(path) {
  if (!existsSync(path)) return { path, exists: false, isFile: false, byteLength: 0 }
  const stat = statSync(path)
  return { path, exists: true, isFile: stat.isFile(), byteLength: stat.size, mtimeMs: stat.mtimeMs }
}

function stem(path) {
  const name = basename(path)
  const ext = extname(name)
  return ext ? name.slice(0, -ext.length) : name
}

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function timestampNow() {
  const date = new Date()
  const pad = (value) => String(value).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}${pad(date.getDate())}${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
}

function validateTimestamp(value) {
  if (!/^\d{10}$/.test(value)) return false
  const month = Number(value.slice(0, 2))
  const day = Number(value.slice(2, 4))
  const hour = Number(value.slice(4, 6))
  const minute = Number(value.slice(6, 8))
  const second = Number(value.slice(8, 10))
  return (
    month >= 1 && month <= 12 && day >= 1 && day <= 31 && hour <= 23 && minute <= 59 && second <= 59
  )
}

function addSecond(timestamp) {
  const month = Number(timestamp.slice(0, 2))
  const day = Number(timestamp.slice(2, 4))
  const hour = Number(timestamp.slice(4, 6))
  const minute = Number(timestamp.slice(6, 8))
  const second = Number(timestamp.slice(8, 10))
  const date = new Date(2000, month - 1, day, hour, minute, second + 1)
  const pad = (value) => String(value).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}${pad(date.getDate())}${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
}

function siblingPattern(finalPptx, compareStem) {
  return new RegExp(`^${escapeRegex(stem(finalPptx))}-${escapeRegex(compareStem)}-(\\d{10})\\.png$`)
}

function makeSiblingPath(args) {
  if (args.sibling) return args.sibling
  let timestamp = args.timestamp || timestampNow()
  if (!validateTimestamp(timestamp))
    throw new Error(`--timestamp must use MMDDhhmmss: ${timestamp}`)
  const dir = dirname(args.finalPptx)
  const base = stem(args.finalPptx)
  for (let attempt = 0; attempt < 60; attempt += 1) {
    const candidate = join(dir, `${base}-${args.compareStem}-${timestamp}.png`)
    if (!existsSync(candidate) || args.overwrite) return candidate
    timestamp = addSecond(timestamp)
  }
  throw new Error('Could not find a collision-free timestamped sibling path')
}

function multipartSiblingPattern(finalPptx, compareStem) {
  return new RegExp(
    `^${escapeRegex(stem(finalPptx))}-${escapeRegex(compareStem)}-(\\d{10})-(\\d{2,})\\.png$`,
  )
}

function makeMultipartSiblingPaths(args, partCount) {
  let timestamp = args.timestamp || timestampNow()
  if (!validateTimestamp(timestamp))
    throw new Error(`--timestamp must use MMDDhhmmss: ${timestamp}`)
  const width = Math.max(2, String(partCount).length)
  const dir = dirname(args.finalPptx)
  const base = stem(args.finalPptx)
  for (let attempt = 0; attempt < 60; attempt += 1) {
    const paths = Array.from({ length: partCount }, (_, index) =>
      join(
        dir,
        `${base}-${args.compareStem}-${timestamp}-${String(index + 1).padStart(width, '0')}.png`,
      ),
    )
    if (args.overwrite || paths.every((path) => !existsSync(path))) return { timestamp, paths }
    timestamp = addSecond(timestamp)
  }
  throw new Error('Could not find a collision-free timestamp for multipart sibling paths')
}

function findMultipartSiblings(args, partCount) {
  const dir = dirname(args.finalPptx)
  if (!existsSync(dir)) return { timestamp: null, paths: [] }
  const pattern = multipartSiblingPattern(args.finalPptx, args.compareStem)
  const groups = new Map()
  for (const name of readdirSync(dir)) {
    const match = name.match(pattern)
    if (!match || !validateTimestamp(match[1])) continue
    const group = groups.get(match[1]) ?? []
    group.push({ number: Number(match[2]), path: join(dir, name) })
    groups.set(match[1], group)
  }
  const timestamp = [...groups.keys()].sort().at(-1) ?? null
  if (!timestamp) return { timestamp: null, paths: [] }
  const paths = groups
    .get(timestamp)
    .sort((a, b) => a.number - b.number)
    .map((item) => item.path)
  return paths.length === partCount ? { timestamp, paths } : { timestamp, paths: [] }
}

function findSibling(args) {
  if (args.sibling) return args.sibling
  const dir = dirname(args.finalPptx)
  if (!existsSync(dir)) return ''
  const pattern = siblingPattern(args.finalPptx, args.compareStem)
  const matches = readdirSync(dir)
    .map((name) => {
      const match = name.match(pattern)
      if (!match) return null
      const path = join(dir, name)
      const timestamp = match[1]
      return validateTimestamp(timestamp) ? { path, timestamp, state: fileState(path) } : null
    })
    .filter(Boolean)
    .filter((item) => item.state.isFile && item.state.byteLength > 0)
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp) || b.state.mtimeMs - a.state.mtimeMs)
  return matches[0]?.path || ''
}

function sameSize(left, right) {
  return left.exists && right.exists && left.byteLength === right.byteLength
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

const SHA256_PATTERN = /^[0-9a-f]{64}$/

function validatedIdentity(endpoint, label, blockers) {
  const path = typeof endpoint?.path === 'string' ? resolve(endpoint.path) : ''
  const state = fileState(path || join(process.cwd(), '__missing__'))
  const expectedSha256 = typeof endpoint?.sha256 === 'string' ? endpoint.sha256 : ''
  const expectedByteLength = endpoint?.byteLength
  if (!path) blockers.push(`${label} path is missing from compare evidence`)
  else if (!state.exists || !state.isFile || state.byteLength <= 0) {
    blockers.push(`${label} file is missing or empty: ${path}`)
  }
  if (!SHA256_PATTERN.test(expectedSha256)) {
    blockers.push(`${label} SHA-256 is missing or invalid`)
  }
  if (!Number.isInteger(expectedByteLength) || expectedByteLength <= 0) {
    blockers.push(`${label} byteLength is missing or invalid`)
  } else if (state.exists && state.byteLength !== expectedByteLength) {
    blockers.push(`${label} byteLength does not match compare evidence`)
  }
  const actualSha256 = state.exists && state.isFile ? sha256(path) : null
  if (actualSha256 && expectedSha256 && actualSha256 !== expectedSha256) {
    blockers.push(`${label} SHA-256 does not match compare evidence`)
  }
  return {
    path: path || null,
    exists: state.exists,
    byteLength: state.byteLength,
    sha256: actualSha256,
    expectedByteLength: Number.isInteger(expectedByteLength) ? expectedByteLength : null,
    expectedSha256: expectedSha256 || null,
  }
}

function sameIdentity(left, right) {
  return (
    left?.path === right?.path &&
    left?.byteLength === right?.byteLength &&
    left?.sha256 === right?.sha256
  )
}

function evidenceIdentity(endpoint) {
  return {
    path: typeof endpoint?.path === 'string' ? resolve(endpoint.path) : null,
    byteLength: Number.isInteger(endpoint?.byteLength) ? endpoint.byteLength : null,
    sha256: typeof endpoint?.sha256 === 'string' ? endpoint.sha256 : null,
  }
}

function preparedPath(destination, index, suffix) {
  return join(
    dirname(destination),
    `.${basename(destination)}.pptx-nova-${process.pid}-${Date.now()}-${index + 1}.${suffix}`,
  )
}

function publishBundle(items, overwrite) {
  const destinations = new Set()
  for (const item of items) {
    if (destinations.has(item.destination)) {
      throw new Error(`duplicate publish destination: ${item.destination}`)
    }
    destinations.add(item.destination)
    const destinationState = fileState(item.destination)
    if (destinationState.exists && !destinationState.isFile) {
      throw new Error(`${item.label} destination is not a file: ${item.destination}`)
    }
    if (destinationState.exists && !overwrite) {
      throw new Error(`${item.label} destination already exists: ${item.destination}`)
    }
  }

  const prepared = []
  const committed = []
  try {
    for (const [index, item] of items.entries()) {
      mkdirSync(dirname(item.destination), { recursive: true })
      const temp = preparedPath(item.destination, index, 'tmp')
      copyFileSync(item.source, temp)
      const state = fileState(temp)
      const digest = sha256(temp)
      if (state.byteLength !== item.expectedByteLength) {
        throw new Error(`${item.label} staged byteLength does not match compare evidence`)
      }
      if (digest !== item.expectedSha256) {
        throw new Error(`${item.label} staged SHA-256 does not match compare evidence`)
      }
      prepared.push({ ...item, temp, backup: '', byteLength: state.byteLength, sha256: digest })
    }

    for (const [index, item] of prepared.entries()) {
      let backup = ''
      if (existsSync(item.destination)) {
        backup = preparedPath(item.destination, index, 'backup')
        renameSync(item.destination, backup)
      }
      item.backup = backup
      renameSync(item.temp, item.destination)
      committed.push(item)
    }

    for (const item of committed) {
      const state = fileState(item.destination)
      if (!state.exists || !state.isFile || state.byteLength !== item.expectedByteLength) {
        throw new Error(`${item.label} published byteLength does not match compare evidence`)
      }
      if (sha256(item.destination) !== item.expectedSha256) {
        throw new Error(`${item.label} published SHA-256 does not match compare evidence`)
      }
    }
  } catch (error) {
    for (const item of [...prepared].reverse()) {
      if (committed.includes(item)) rmSync(item.destination, { force: true })
      if (item.backup && existsSync(item.backup)) {
        rmSync(item.destination, { force: true })
        renameSync(item.backup, item.destination)
      }
      rmSync(item.temp, { force: true })
    }
    throw error
  }

  const cleanupWarnings = []
  for (const item of committed) {
    if (!item.backup) continue
    try {
      rmSync(item.backup, { force: true })
    } catch (error) {
      cleanupWarnings.push(
        `${item.label} backup cleanup failed after publish commit: ${
          error instanceof Error ? error.message : String(error)
        }`,
      )
    }
  }
  return {
    published: committed.map(({ label, source, destination, byteLength, sha256: digest }) => ({
      label,
      source,
      destination,
      byteLength,
      sha256: digest,
    })),
    cleanupWarnings,
  }
}

function coverageFromParts(parts, slideCount) {
  const counts = new Map()
  for (const part of parts) {
    for (const slide of Array.isArray(part.slides) ? part.slides : []) {
      counts.set(slide, (counts.get(slide) ?? 0) + 1)
    }
  }
  const expected = Array.from({ length: slideCount }, (_, index) => index + 1)
  return {
    missingSlides: expected.filter((slide) => !counts.has(slide)),
    duplicateSlides: expected.filter((slide) => (counts.get(slide) ?? 0) > 1),
    outOfRangeSlides: [...counts.keys()].filter((slide) => slide < 1 || slide > slideCount),
  }
}

function validateMultipartManifest(report, blockers) {
  if (report.status !== 'success') blockers.push('multipart compare manifest status is not success')
  if (!Number.isInteger(report.slideCount) || report.slideCount <= 0) {
    blockers.push('multipart compare manifest slideCount is missing or invalid')
  }
  if (!Array.isArray(report.parts) || report.parts.length < 2) {
    blockers.push('multipart compare manifest must contain at least two parts')
    return []
  }
  const manifestSource = evidenceIdentity(report.source)
  const manifestCandidate = evidenceIdentity(report.candidate)
  const states = report.parts.map((part, index) => {
    const label = `multipart part ${index + 1}`
    const path = typeof part.path === 'string' ? resolve(part.path) : ''
    const state = fileState(path || join(process.cwd(), '__missing__'))
    if (!path) blockers.push(`${label} path is missing`)
    else if (!state.exists || !state.isFile || state.byteLength <= 0) {
      blockers.push(`${label} PNG is missing or empty: ${path}`)
    }
    if (state.exists && part.byteLength !== state.byteLength) {
      blockers.push(`${label} byteLength does not match manifest`)
    }
    if (state.exists && part.sha256 !== sha256(path)) {
      blockers.push(`${label} SHA-256 does not match manifest`)
    }
    if (!Array.isArray(part.slides) || part.slides.length === 0) {
      blockers.push(`${label} slides are missing`)
    }
    if (part.pairCount !== part.slides?.length) {
      blockers.push(`${label} pairCount does not match its slide coverage`)
    }
    if (![192, 144].includes(part.dpi)) blockers.push(`${label} DPI must be 192 or 144`)
    if (part.agentGate?.passed !== true && part.agentGate?.status !== 'pass') {
      blockers.push(`${label} agent gate did not pass`)
    }
    const partReportPath = typeof part.reportPath === 'string' ? resolve(part.reportPath) : ''
    const partReportState = fileState(partReportPath || join(process.cwd(), '__missing__'))
    let partReport = null
    if (!partReportState.exists || !partReportState.isFile) {
      blockers.push(`${label} JSON report is missing: ${partReportPath || '(unset)'}`)
    } else {
      partReport = readJson(partReportPath)
      if (partReport.schemaVersion !== 'pptx-contact-diff/v1' || partReport.status !== 'success') {
        blockers.push(`${label} JSON report is not a successful pptx-contact-diff/v1 report`)
      }
      if (!sameIdentity(evidenceIdentity(partReport.baseline), manifestSource)) {
        blockers.push(`${label} source identity does not match multipart manifest`)
      }
      if (!sameIdentity(evidenceIdentity(partReport.target), manifestCandidate)) {
        blockers.push(`${label} candidate identity does not match multipart manifest`)
      }
      for (const outputPath of reportImagePaths(partReport)) {
        if (resolve(outputPath) !== path)
          blockers.push(`${label} JSON output path does not match PNG`)
      }
      const reportPairCount = reportNumber(
        partReport.agentGate?.pairCount,
        partReport.summary?.pairCount,
      )
      if (reportPairCount !== part.pairCount) {
        blockers.push(`${label} JSON pairCount does not match manifest`)
      }
      const reportDpi = reportNumber(partReport.render?.dpi, partReport.summary?.dpi)
      if (reportDpi !== part.dpi) blockers.push(`${label} JSON DPI does not match manifest`)
      if (
        !Array.isArray(partReport.scope?.slides) ||
        JSON.stringify(partReport.scope.slides) !== JSON.stringify(part.slides)
      ) {
        blockers.push(`${label} JSON scope does not match manifest slides`)
      }
    }
    const attempts = Array.isArray(part.attempts) ? part.attempts : []
    const cacheHit = validCacheHit(part.cache, partReport?.pptxNovaCompare?.cache, part.sha256)
    if (
      part.dpi === 192 &&
      !(
        attempts.length === 1 &&
        attempts[0]?.dpi === 192 &&
        (attempts[0]?.status === 'success' || (attempts[0]?.status === 'cache-hit' && cacheHit))
      )
    ) {
      blockers.push(`${label} attempt history is invalid for a 192 DPI part`)
    }
    if (
      part.dpi === 144 &&
      !(
        attempts.length === 2 &&
        attempts[0]?.dpi === 192 &&
        attempts[0]?.status === 'failed' &&
        attempts[0]?.error?.retryable === true &&
        (attempts[0]?.error?.kind === 'render_error' ||
          attempts[0]?.error?.code === 'render_error') &&
        attempts[1]?.dpi === 144 &&
        (attempts[1]?.status === 'success' || (attempts[1]?.status === 'cache-hit' && cacheHit))
      )
    ) {
      blockers.push(`${label} attempt history does not prove an allowed 192 to 144 retry`)
    }
    return {
      ...state,
      partNumber: part.partNumber,
      selector: part.selector,
      dpi: part.dpi,
      sha256: part.sha256,
    }
  })
  if (Number.isInteger(report.slideCount) && report.slideCount > 0) {
    const coverage = coverageFromParts(report.parts, report.slideCount)
    if (coverage.missingSlides.length > 0) {
      blockers.push(`multipart coverage has missing slides: ${coverage.missingSlides.join(',')}`)
    }
    if (coverage.duplicateSlides.length > 0) {
      blockers.push(
        `multipart coverage has duplicate slides: ${coverage.duplicateSlides.join(',')}`,
      )
    }
    if (coverage.outOfRangeSlides.length > 0) {
      blockers.push(
        `multipart coverage has out-of-range slides: ${coverage.outOfRangeSlides.join(',')}`,
      )
    }
  }
  if (report.agentGate?.passed !== true && report.agentGate?.status !== 'pass') {
    blockers.push('multipart compare manifest agent gate did not pass')
  }
  return states
}

function reportNumber(...values) {
  for (const value of values) {
    if (Number.isFinite(value)) return value
  }
  return null
}

function reportImagePaths(report) {
  const paths = [report.output, report.outputPath, report.render?.path, report.contactSheet?.path]
    .filter((path) => typeof path === 'string' && path.trim())
    .map((path) => path.trim())
  return [...new Set(paths)]
}

function validCacheHit(cache, reportCache, imageSha256) {
  return (
    cache?.status === 'hit' &&
    reportCache?.status === 'hit' &&
    typeof cache.key === 'string' &&
    /^[0-9a-f]{64}$/.test(cache.key) &&
    cache.key === reportCache.key &&
    cache.imageSha256 === imageSha256 &&
    reportCache.imageSha256 === imageSha256
  )
}

function validateNativeCompareReport(args, report, compareState, blockers, warnings) {
  if (report.status !== 'success') blockers.push('compare report status is not success')
  if (report.kind !== args.kind) {
    blockers.push(`compare report kind ${JSON.stringify(report.kind)} does not match ${args.kind}`)
  }
  if (report.slideSelector !== null && report.slideSelector !== undefined) {
    blockers.push(
      'compare report was generated with --slides; final delivery requires full-deck compare',
    )
  }
  if (!Number.isInteger(report.pageCount) || report.pageCount <= 0) {
    blockers.push('compare report pageCount is missing or invalid')
  }
  if (
    !Number.isFinite(report.width) ||
    report.width <= 0 ||
    !Number.isFinite(report.height) ||
    report.height <= 0
  ) {
    blockers.push('compare report image dimensions are missing or invalid')
  }
  if (!Number.isFinite(report.byteLength) || report.byteLength <= 0) {
    blockers.push('compare report byteLength is missing or invalid')
  } else if (compareState.exists && report.byteLength !== compareState.byteLength) {
    blockers.push('compare report byteLength does not match compare PNG')
  }
  if (report.output && resolve(report.output) !== compareState.path) {
    warnings.push(`compare report output differs from checked compare path: ${report.output}`)
  }
}

function validateXdocContactDiffReport(report, compareState, blockers) {
  if (report.status !== 'success') blockers.push('contact-diff report status is not success')
  const gate = report.agentGate ?? {}
  if (gate.passed !== true && gate.status !== 'pass') {
    blockers.push('contact-diff agent gate did not pass')
  }
  const scopeMode = gate.scopeMode ?? report.summary?.scopeMode
  if (scopeMode !== 'all-slides') {
    blockers.push(
      scopeMode
        ? 'contact-diff report was generated with a scoped slide selection'
        : 'contact-diff scopeMode is missing; final delivery requires all-slides contact-diff',
    )
  }
  const pairCount = reportNumber(gate.pairCount, report.summary?.pairCount)
  if (!Number.isInteger(pairCount) || pairCount <= 0) {
    blockers.push('contact-diff pairCount is missing or invalid')
  }
  const width = reportNumber(report.render?.width)
  const height = reportNumber(report.render?.height)
  if (!width || width <= 0 || !height || height <= 0) {
    blockers.push('contact-diff render dimensions are missing or invalid')
  }
  const outputPaths = reportImagePaths(report)
  if (outputPaths.length === 0) {
    blockers.push('contact-diff output path is missing')
  }
  for (const outputPath of outputPaths) {
    if (resolve(outputPath) !== compareState.path) {
      blockers.push(`contact-diff output differs from checked compare path: ${outputPath}`)
    }
  }
  const dpi = reportNumber(report.render?.dpi, report.summary?.dpi)
  if (![192, 144].includes(dpi)) blockers.push('contact-diff DPI must be 192 or 144')
  const attempts = report.pptxNovaCompare?.attempts
  if (Array.isArray(attempts)) {
    const cache = report.pptxNovaCompare?.cache
    const checkedSha256 = compareState.exists ? sha256(compareState.path) : null
    const cacheHit = validCacheHit(cache, cache, checkedSha256)
    const valid192 =
      dpi === 192 &&
      attempts.length === 1 &&
      attempts[0]?.dpi === 192 &&
      (attempts[0]?.status === 'success' || (attempts[0]?.status === 'cache-hit' && cacheHit))
    const valid144 =
      dpi === 144 &&
      attempts.length === 2 &&
      attempts[0]?.dpi === 192 &&
      attempts[0]?.status === 'failed' &&
      attempts[0]?.error?.retryable === true &&
      (attempts[0]?.error?.kind === 'render_error' ||
        attempts[0]?.error?.code === 'render_error') &&
      attempts[1]?.dpi === 144 &&
      (attempts[1]?.status === 'success' || (attempts[1]?.status === 'cache-hit' && cacheHit))
    if (!valid192 && !valid144)
      blockers.push('contact-diff attempt history does not prove an allowed DPI policy')
  }
}

function validateReport(args, report, compareState, blockers, warnings) {
  if (report.__parseError) {
    blockers.push(`compare report is not valid JSON: ${report.__parseError}`)
    return
  }
  if (report.schemaVersion === 'pptx-contact-diff/v1') {
    validateXdocContactDiffReport(report, compareState, blockers)
    return
  }
  validateNativeCompareReport(args, report, compareState, blockers, warnings)
}

function compareReportSummary(report) {
  if (!report || report.__parseError) {
    return {
      schemaVersion: null,
      status: report?.status ?? null,
      pageCount: null,
      slideSelector: null,
      width: null,
      height: null,
      byteLength: null,
    }
  }
  if (report.schemaVersion === 'pptx-contact-diff/v1') {
    const scopeMode = report.agentGate?.scopeMode ?? report.summary?.scopeMode ?? null
    return {
      schemaVersion: report.schemaVersion,
      status: report.status ?? null,
      pageCount: reportNumber(report.agentGate?.pairCount, report.summary?.pairCount),
      slideSelector: scopeMode === 'all-slides' ? null : scopeMode,
      width: reportNumber(report.render?.width),
      height: reportNumber(report.render?.height),
      byteLength: null,
    }
  }
  return {
    schemaVersion: report.schemaVersion ?? null,
    status: report.status ?? null,
    pageCount: report.pageCount ?? null,
    slideSelector: report.slideSelector ?? null,
    width: report.width ?? null,
    height: report.height ?? null,
    byteLength: report.byteLength ?? null,
  }
}

function buildReport(args) {
  const blockers = []
  const warnings = []
  let finalState = fileState(args.finalPptx)
  let finalSourceState = args.finalPptxSource ? fileState(args.finalPptxSource) : null
  const compareState = fileState(args.compare)
  const reportState = fileState(args.report)

  if (finalSourceState) {
    if (!finalSourceState.exists) {
      blockers.push(`staged final PPTX source is missing: ${args.finalPptxSource}`)
    } else if (!finalSourceState.isFile) {
      blockers.push(`staged final PPTX source is not a file: ${args.finalPptxSource}`)
    } else if (finalSourceState.byteLength <= 0) {
      blockers.push('staged final PPTX source is empty')
    }
  } else if (!args.publish) {
    if (!finalState.exists) blockers.push(`final PPTX is missing: ${args.finalPptx}`)
    else if (!finalState.isFile) blockers.push(`final PPTX is not a file: ${args.finalPptx}`)
  }
  if (finalState.exists && !finalState.isFile) {
    blockers.push(`final PPTX path is not a file: ${args.finalPptx}`)
  }
  if (!reportState.exists) blockers.push(`compare report is missing: ${args.report}`)
  else if (!reportState.isFile) blockers.push(`compare report is not a file: ${args.report}`)

  const compareReport = reportState.exists && reportState.isFile ? readJson(args.report) : null
  const multipart = compareReport?.schemaVersion === 'pptx-nova-compare-manifest/v1'
  const sourceIdentity = validatedIdentity(
    multipart ? compareReport?.source : compareReport?.baseline,
    'compare source',
    blockers,
  )
  const candidateIdentity = validatedIdentity(
    multipart ? compareReport?.candidate : compareReport?.target,
    'compare candidate',
    blockers,
  )
  if (
    compareReport?.baselinePath &&
    sourceIdentity.path &&
    resolve(compareReport.baselinePath) !== sourceIdentity.path
  ) {
    blockers.push('compare report baselinePath does not match baseline identity')
  }
  if (
    compareReport?.targetPath &&
    candidateIdentity.path &&
    resolve(compareReport.targetPath) !== candidateIdentity.path
  ) {
    blockers.push('compare report targetPath does not match target identity')
  }

  const expectedCandidateSha256 = candidateIdentity.expectedSha256
  const expectedCandidateByteLength = candidateIdentity.expectedByteLength
  let stagedFinalSha256 = null
  if (finalSourceState?.exists && finalSourceState.isFile) {
    stagedFinalSha256 = sha256(args.finalPptxSource)
    if (
      expectedCandidateByteLength &&
      finalSourceState.byteLength !== expectedCandidateByteLength
    ) {
      blockers.push('staged final PPTX byteLength does not match compared candidate')
    }
    if (expectedCandidateSha256 && stagedFinalSha256 !== expectedCandidateSha256) {
      blockers.push('staged final PPTX SHA-256 does not match compared candidate')
    }
  }

  let partStates = []
  let sibling = ''
  let siblingState = fileState(join(dirname(args.finalPptx), '__missing__'))
  let siblingPaths = []
  let siblingStates = []
  let timestamp = null
  let publishItems = []
  if (multipart) {
    partStates = validateMultipartManifest(compareReport, blockers)
    const selection = args.publish
      ? makeMultipartSiblingPaths(args, partStates.length)
      : findMultipartSiblings(args, partStates.length)
    timestamp = selection.timestamp
    siblingPaths = selection.paths
    if (!args.publish && (!timestamp || siblingPaths.length !== partStates.length)) {
      blockers.push(
        `no complete multipart sibling set found matching ${stem(args.finalPptx)}-${args.compareStem}-<MMDDhhmmss>-<part>.png`,
      )
    }
    publishItems = siblingPaths.map((path, index) => ({
      label: `multipart compare sibling ${index + 1}`,
      source: partStates[index]?.path,
      destination: path,
      expectedByteLength: partStates[index]?.byteLength,
      expectedSha256: partStates[index]?.sha256,
    }))
  } else {
    if (!compareState.exists) blockers.push(`run-directory compare PNG is missing: ${args.compare}`)
    else if (!compareState.isFile) blockers.push(`compare PNG is not a file: ${args.compare}`)
    else if (compareState.byteLength <= 0) blockers.push('compare PNG is empty')
    if (compareReport) validateReport(args, compareReport, compareState, blockers, warnings)
    sibling = args.publish ? makeSiblingPath(args) : findSibling(args)
    const pattern = siblingPattern(args.finalPptx, args.compareStem)
    const siblingBase = sibling ? basename(sibling) : ''
    timestamp = siblingBase.match(pattern)?.[1] || null
    if (!sibling) {
      blockers.push(
        `no sibling compare PNG found next to final PPTX matching ${stem(args.finalPptx)}-${args.compareStem}-<MMDDhhmmss>.png`,
      )
    } else {
      if (dirname(sibling) !== dirname(args.finalPptx)) {
        blockers.push('sibling compare PNG is not next to final PPTX')
      }
      if (!pattern.test(siblingBase)) {
        blockers.push(`sibling compare PNG has invalid name: ${siblingBase}`)
      }
    }
    if (sibling && compareState.exists && compareState.isFile) {
      publishItems = [
        {
          label: 'compare sibling',
          source: args.compare,
          destination: sibling,
          expectedByteLength: compareState.byteLength,
          expectedSha256: sha256(args.compare),
        },
      ]
      siblingPaths = [sibling]
    }
  }

  if (
    args.publish &&
    args.finalPptxSource !== args.finalPptx &&
    finalSourceState?.exists &&
    finalSourceState.isFile &&
    expectedCandidateByteLength &&
    expectedCandidateSha256
  ) {
    publishItems.push({
      label: 'final PPTX',
      source: args.finalPptxSource,
      destination: args.finalPptx,
      expectedByteLength: expectedCandidateByteLength,
      expectedSha256: expectedCandidateSha256,
    })
  }

  let published = []
  if (args.publish && blockers.length === 0) {
    try {
      const publishResult = publishBundle(publishItems, args.overwrite)
      published = publishResult.published
      warnings.push(...publishResult.cleanupWarnings)
    } catch (error) {
      blockers.push(
        `delivery bundle publish failed: ${error instanceof Error ? error.message : String(error)}`,
      )
    }
  }

  finalState = fileState(args.finalPptx)
  finalSourceState = args.finalPptxSource ? fileState(args.finalPptxSource) : null
  const publishedFinalSha256 =
    finalState.exists && finalState.isFile && finalState.byteLength > 0
      ? sha256(args.finalPptx)
      : null
  if (!finalState.exists) blockers.push(`final PPTX is missing: ${args.finalPptx}`)
  else if (!finalState.isFile) blockers.push(`final PPTX is not a file: ${args.finalPptx}`)
  else if (finalState.byteLength <= 0) blockers.push('final PPTX is empty')
  if (
    finalState.exists &&
    expectedCandidateByteLength &&
    expectedCandidateByteLength !== finalState.byteLength
  ) {
    blockers.push('published final PPTX byteLength does not match compared candidate')
  }
  if (
    publishedFinalSha256 &&
    expectedCandidateSha256 &&
    expectedCandidateSha256 !== publishedFinalSha256
  ) {
    blockers.push('published final PPTX SHA-256 does not match compared candidate')
  }

  if (multipart) {
    siblingStates = siblingPaths.map((path, index) => {
      const state = fileState(path)
      if (!state.exists || !state.isFile || state.byteLength <= 0) {
        blockers.push(`multipart sibling ${index + 1} is missing or empty: ${path}`)
      } else if (state.byteLength !== partStates[index]?.byteLength) {
        blockers.push(`multipart sibling ${index + 1} byteLength does not match run evidence`)
      } else if (sha256(path) !== partStates[index]?.sha256) {
        blockers.push(`multipart sibling ${index + 1} SHA-256 does not match run evidence`)
      }
      return { ...state, partNumber: index + 1, sha256: state.exists ? sha256(path) : null }
    })
    sibling = siblingPaths[0] || ''
    siblingState = siblingStates[0] ?? siblingState
  } else {
    siblingState = sibling
      ? fileState(sibling)
      : fileState(join(dirname(args.finalPptx), '__missing__'))
    if (!siblingState.exists || !siblingState.isFile || siblingState.byteLength <= 0) {
      blockers.push(`sibling compare PNG is missing or empty: ${sibling}`)
    } else if (!sameSize(compareState, siblingState)) {
      blockers.push('sibling compare PNG byteLength does not match run-directory compare PNG')
    } else if (sha256(args.compare) !== sha256(sibling)) {
      blockers.push('sibling compare PNG SHA-256 does not match run-directory compare PNG')
    }
  }
  const reportSummary = multipart
    ? {
        schemaVersion: compareReport.schemaVersion,
        status: compareReport.status,
        pageCount: compareReport.slideCount,
        partCount: compareReport.parts?.length ?? 0,
        slideSelector: null,
        width: null,
        height: null,
        byteLength: null,
      }
    : compareReportSummary(compareReport)

  const finalBindingStatus =
    expectedCandidateSha256 &&
    (!finalSourceState || stagedFinalSha256 === expectedCandidateSha256) &&
    publishedFinalSha256 === expectedCandidateSha256
      ? 'bound'
      : finalState.exists
        ? 'mismatch'
        : 'pending'
  if (finalBindingStatus !== 'bound') {
    blockers.push(`final PPTX binding status is ${finalBindingStatus}`)
  }
  const status = blockers.length === 0 ? 'pass' : 'fail'
  return {
    schemaVersion: SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    status,
    mode: args.publish ? 'publish-and-bind' : 'check-binding',
    kind: args.kind,
    compareStem: args.compareStem,
    runDir: args.runDir,
    finalPptx: finalState,
    finalPptxSource: finalSourceState ? { ...finalSourceState, sha256: stagedFinalSha256 } : null,
    finalBinding: {
      algorithm: 'sha256',
      status: finalBindingStatus,
      comparedCandidate: {
        path: candidateIdentity.path,
        byteLength: expectedCandidateByteLength,
        sha256: expectedCandidateSha256,
      },
      stagedFinal: finalSourceState
        ? {
            path: args.finalPptxSource,
            byteLength: finalSourceState.byteLength,
            sha256: stagedFinalSha256,
          }
        : null,
      publishedFinal: {
        path: args.finalPptx,
        byteLength: finalState.byteLength,
        sha256: publishedFinalSha256,
      },
    },
    compare: compareState,
    parts: partStates,
    compareReport: {
      path: args.report,
      exists: reportState.exists,
      ...reportSummary,
    },
    sibling: {
      ...siblingState,
      requiredPattern: multipart
        ? `${stem(args.finalPptx)}-${args.compareStem}-<MMDDhhmmss>-<part>.png`
        : `${stem(args.finalPptx)}-${args.compareStem}-<MMDDhhmmss>.png`,
      timestamp,
    },
    siblings: siblingStates,
    published,
    blockers,
    warnings,
    agentSummary: {
      status,
      siblingPath: sibling || siblingPaths[0] || null,
      siblingPaths: siblingPaths.length > 0 ? siblingPaths : sibling ? [sibling] : [],
      message:
        status === 'pass'
          ? multipart
            ? 'The final PPTX and complete numbered compare PNG set are SHA-256-bound to the compared candidate.'
            : 'The final PPTX and compare PNG are SHA-256-bound to the compared candidate.'
          : `Compare delivery gate failed with ${blockers.length} blocker(s).`,
    },
  }
}

function writeReport(args, report) {
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(
      `output already exists: ${args.output}; use --overwrite for a current-run gate artifact`,
    )
  }
  mkdirSync(dirname(args.output), { recursive: true })
  const text = `${JSON.stringify(report, null, 2)}\n`
  const temp = `${args.output}.pptx-nova-${process.pid}-${Date.now()}.tmp`
  try {
    writeFileSync(temp, text)
    renameSync(temp, args.output)
  } finally {
    rmSync(temp, { force: true })
  }
  if (args.json) process.stdout.write(text)
  else {
    process.stdout.write(`${report.compareStem} gate: ${report.status}\n`)
    process.stdout.write(`${report.agentSummary.message}\n`)
    process.stdout.write(`report: ${args.output}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  if (existsSync(args.output)) {
    if (!args.overwrite) {
      throw new Error(
        `output already exists: ${args.output}; use --overwrite for a current-run gate artifact`,
      )
    }
    if (args.publish) rmSync(args.output, { force: true })
  }
  const report = buildReport(args)
  writeReport(args, report)
  if (report.status === 'fail') process.exit(2)
} catch (error) {
  process.stderr.write(`[error] ${error instanceof Error ? error.message : String(error)}\n`)
  process.exit(1)
}
