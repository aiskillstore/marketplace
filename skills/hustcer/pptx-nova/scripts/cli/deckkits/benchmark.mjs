#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { spawnSync } from 'node:child_process'
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { loadContent } from '../../../assets/deckkits/shared/core-primitives.kit.mjs'
import { validateDeckkitContent as validateContent } from '../../../assets/deckkits/shared/validate-deckkit.mjs'
import { createVisionBaseline, summarizeVisionReport } from '../../lib/review/vision-baseline.mjs'

const WORK_ROOT = process.cwd()
const VISUAL_ROOT = join(SKILL_ROOT, 'benchmarks/visual')
const DEFAULT_OUT = join(WORK_ROOT, '.tmp/pptx-nova-visual')

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/benchmark.mjs [options]

Options:
  --all                       Run all cases
  --deckkit, -d <id>          Filter by DeckKit id
  --case <id>                 Run one case id or case suffix
  --out <dir>                 Output directory. Defaults to <cwd>/.tmp/pptx-nova-visual
  --repeat <n>                Repeat validate+build for timing. Defaults to 1
  --fail-on-fit <level>       none|error|warning. Defaults to error
  --fail-on-vision <level>    none|high|medium|new-low|any. Defaults to medium
  --render-previews           Render per-slide PNG previews with xdoc convert. Default
  --no-render-previews        Skip PNG preview and contact-sheet rendering
  --contact-sheet             Render PNG previews and contact sheet. Default
  --no-contact-sheet          Skip contact sheet while keeping per-slide previews
  --contact-thumb <WxH>        Contact sheet thumbnail size. Defaults to 640x360
  --update-baseline           Accept current low vision issues as reviewed visual baselines
  --xdoc-bin <path>           xdoc binary path. Defaults to xdoc
  --clean                     Remove each case output directory before running
  --json                      Print machine-readable summary
  --help                      Show this help
`

function parseArgs(argv) {
  const args = {
    all: false,
    deckkit: '',
    caseId: '',
    out: DEFAULT_OUT,
    repeat: 1,
    failOnFit: 'error',
    failOnVision: 'medium',
    renderPreviews: true,
    contactSheet: true,
    contactThumb: '640x360',
    updateBaseline: false,
    xdocBin: '',
    clean: false,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--all') {
      args.all = true
    } else if (arg === '--clean') {
      args.clean = true
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--render-previews') {
      args.renderPreviews = true
    } else if (arg === '--no-render-previews') {
      args.renderPreviews = false
      args.contactSheet = false
    } else if (arg === '--contact-sheet') {
      args.renderPreviews = true
      args.contactSheet = true
    } else if (arg === '--no-contact-sheet') {
      args.contactSheet = false
    } else if (arg === '--contact-thumb') {
      args.contactThumb = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--update-baseline') {
      args.updateBaseline = true
    } else if (arg === '--deckkit' || arg === '-d') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--case') {
      args.caseId = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--out') {
      args.out = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--repeat') {
      args.repeat = Number.parseInt(valueAfter(argv, i, arg), 10)
      i += 1
    } else if (arg === '--fail-on-fit') {
      args.failOnFit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--fail-on-vision') {
      args.failOnVision = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--xdoc-bin') {
      args.xdocBin = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.all && !args.deckkit && !args.caseId) {
    throw new Error(`Specify --all, --deckkit/-d <id>, or --case <id>.\n\n${usage}`)
  }
  if (!Number.isInteger(args.repeat) || args.repeat < 1) {
    throw new Error('--repeat must be a positive integer')
  }
  if (!/^[1-9]\d*x[1-9]\d*$/.test(args.contactThumb)) {
    throw new Error('--contact-thumb must be a positive WxH size, e.g. 1920x1080')
  }
  if (!['none', 'error', 'warning'].includes(args.failOnFit)) {
    throw new Error('--fail-on-fit must be one of none|error|warning')
  }
  if (!['none', 'high', 'medium', 'new-low', 'any'].includes(args.failOnVision)) {
    throw new Error('--fail-on-vision must be one of none|high|medium|new-low|any')
  }
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function resolveVisual(path) {
  return resolve(VISUAL_ROOT, path)
}

let catalogCache = null

function loadDeckkitEntry(deckkit) {
  if (!catalogCache) {
    catalogCache = readJson(join(SKILL_ROOT, 'assets/deckkits/catalog.json'))
  }
  return catalogCache.entries?.find((entry) => entry.id === deckkit) ?? null
}

function readOptionalJson(path) {
  return existsSync(path) ? readJson(path) : null
}

function caseSlug(benchCase) {
  return benchCase.id.includes('.') ? benchCase.id.split('.').slice(1).join('.') : benchCase.id
}

function selectCases(index, args) {
  return index.cases.filter((benchCase) => {
    const slug = caseSlug(benchCase)
    if (args.deckkit && benchCase.deckkit !== args.deckkit) return false
    if (args.caseId && benchCase.id !== args.caseId && slug !== args.caseId) return false
    return args.all || args.deckkit || args.caseId
  })
}

function elapsedMs(start) {
  return Number((performance.now() - start).toFixed(2))
}

function percentile(values, p) {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const idx = Math.min(sorted.length - 1, Math.ceil((p / 100) * sorted.length) - 1)
  return sorted[idx]
}

function summarizeTimings(runs) {
  const validateMs = runs.map((r) => r.validateMs)
  const buildMs = runs.map((r) => r.buildMs)
  const totalMs = runs.map((r) => r.totalMs)
  return {
    runs,
    p50: {
      validateMs: percentile(validateMs, 50),
      buildMs: percentile(buildMs, 50),
      totalMs: percentile(totalMs, 50),
    },
    p95: {
      validateMs: percentile(validateMs, 95),
      buildMs: percentile(buildMs, 95),
      totalMs: percentile(totalMs, 95),
    },
  }
}

function countBlockingWarnings(warnings) {
  return warnings.filter((w) => w.blocking === true || w.diagnostic?.severity === 'error').length
}

function countFitErrors(fitDiagnostics) {
  return fitDiagnostics.filter((d) => d.severity === 'error').length
}

function countFitWarnings(fitDiagnostics) {
  return fitDiagnostics.filter((d) => d.severity === 'warning').length
}

function countBlockingFitDiagnostics(fitDiagnostics) {
  return fitDiagnostics.filter((d) => d.blocking === true || d.severity === 'error').length
}

function runBuild(buildPath, contentPath) {
  const result = spawnSync('node', [buildPath, contentPath], {
    cwd: WORK_ROOT,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
  if (result.status !== 0) {
    throw new Error(
      [
        `Build failed: node ${relative(WORK_ROOT, buildPath)} ${relative(WORK_ROOT, contentPath)}`,
        result.stderr,
        result.stdout,
      ]
        .filter(Boolean)
        .join('\n'),
    )
  }
  return {
    patch: JSON.parse(result.stdout),
    stdout: result.stdout,
    stderr: result.stderr,
  }
}

function runCommand(bin, commandArgs, label) {
  const result = spawnSync(bin, commandArgs, {
    cwd: WORK_ROOT,
    encoding: 'utf8',
    maxBuffer: 128 * 1024 * 1024,
  })
  if (result.status !== 0) {
    throw new Error(
      [`${label} failed: ${bin} ${commandArgs.join(' ')}`, result.stderr, result.stdout]
        .filter(Boolean)
        .join('\n'),
    )
  }
  return {
    stdout: result.stdout,
    stderr: result.stderr,
  }
}

function jsonStatusFailure(report) {
  const status = typeof report?.status === 'string' ? report.status.toLowerCase() : ''
  return ['error', 'fail', 'failed', 'blocked'].includes(status)
}

function runJsonCommand(bin, commandArgs, label) {
  const result = runCommand(bin, commandArgs, label)
  let json
  try {
    json = JSON.parse(result.stdout)
  } catch (error) {
    throw new Error(
      [
        `${label} did not emit valid JSON: ${error.message}`,
        result.stderr,
        result.stdout.slice(0, 4000),
      ]
        .filter(Boolean)
        .join('\n'),
    )
  }
  if (jsonStatusFailure(json)) {
    const kind = json?.error?.kind ?? json?.error?.code ?? json?.status ?? 'JsonStatusFailure'
    throw new Error(`${label} emitted failure JSON status ${JSON.stringify(json.status)} (${kind})`)
  }
  return {
    json,
    stdout: result.stdout,
    stderr: result.stderr,
  }
}

function listPngFiles(dir) {
  if (!existsSync(dir)) return []
  return readdirSync(dir)
    .filter((name) => /\.png$/i.test(name))
    .sort((a, b) => a.localeCompare(b, 'en'))
    .map((name) => {
      const path = join(dir, name)
      return {
        name,
        path,
        bytes: statSync(path).size,
      }
    })
}

function countArray(value) {
  return Array.isArray(value) ? value.length : 0
}

function countSeverity(items, severity) {
  return (Array.isArray(items) ? items : []).filter((item) => item.severity === severity).length
}

function summarizeApplyReport(report) {
  const visualRisks = report.visualRisks ?? []
  return {
    status: report.status ?? '',
    warnings: countArray(report.warnings),
    changedParts: countArray(report.changedParts),
    opResults: countArray(report.opResults),
    visualRisks: {
      high: countSeverity(visualRisks, 'high'),
      medium: countSeverity(visualRisks, 'medium'),
      low: countSeverity(visualRisks, 'low'),
      total: countArray(visualRisks),
    },
    output: report.output ?? null,
    sidecar: report.sidecar ?? null,
    wouldWrite: report.wouldWrite ?? null,
  }
}

function runXdocStages({ args, patchPath, deckPath, outDir }) {
  const bin = args.xdocBin || 'xdoc'
  const dryRunPath = join(outDir, 'dry-run.json')
  const applyPath = join(outDir, 'apply.json')
  const visionPath = join(outDir, 'vision.json')

  const dryRunStart = performance.now()
  const dryRun = runJsonCommand(
    bin,
    ['pptx', 'apply', '-p', patchPath, '-o', deckPath, '--dry-run', '--json'],
    'xdoc dry-run',
  )
  const dryRunMs = elapsedMs(dryRunStart)
  writeJson(dryRunPath, dryRun.json)
  if (dryRun.stderr.trim()) writeFileSync(join(outDir, 'dry-run-stderr.txt'), dryRun.stderr)

  const applyStart = performance.now()
  const apply = runJsonCommand(
    bin,
    ['pptx', 'apply', '-p', patchPath, '-o', deckPath, '--overwrite', '--json'],
    'xdoc apply',
  )
  const applyMs = elapsedMs(applyStart)
  writeJson(applyPath, apply.json)
  if (apply.stderr.trim()) writeFileSync(join(outDir, 'apply-stderr.txt'), apply.stderr)

  const visionStart = performance.now()
  const vision = runJsonCommand(
    bin,
    ['pptx', 'vision-check', deckPath, '--json'],
    'xdoc vision-check',
  )
  const visionMs = elapsedMs(visionStart)
  writeJson(visionPath, vision.json)
  if (vision.stderr.trim()) writeFileSync(join(outDir, 'vision-stderr.txt'), vision.stderr)

  return {
    paths: {
      deck: deckPath,
      dryRun: dryRunPath,
      apply: applyPath,
      vision: visionPath,
    },
    timing: {
      dryRunMs,
      applyMs,
      visionMs,
    },
    dryRun: summarizeApplyReport(dryRun.json),
    apply: summarizeApplyReport(apply.json),
    vision: summarizeVisionReport(vision.json),
    visionReport: vision.json,
  }
}

function runPreviewStages({ args, deckPath, outDir, expectedCount }) {
  const previewDir = join(outDir, 'previews')
  const convertReportPath = join(outDir, 'convert-report.json')
  const contactSheetPath = join(outDir, 'contact-sheet.png')

  if (!args.renderPreviews) {
    return {
      paths: {
        previews: previewDir,
        convertReport: null,
        contactSheet: null,
      },
      timing: {
        convertMs: 0,
      },
      previews: {
        enabled: false,
        dir: null,
        count: 0,
        expectedCount,
        countEqualsSlides: false,
        nonEmpty: false,
        totalBytes: 0,
        files: [],
      },
      contactSheet: {
        enabled: false,
        path: null,
        exists: false,
        bytes: 0,
        nonEmpty: false,
      },
      skipped: {
        previews: true,
        contactSheet: true,
      },
    }
  }

  rmSync(previewDir, { recursive: true, force: true })
  rmSync(contactSheetPath, { force: true })
  rmSync(convertReportPath, { force: true })

  const bin = args.xdocBin || 'xdoc'
  const commandArgs = [
    'convert',
    deckPath,
    '--to',
    'png',
    '--output',
    previewDir,
    '--overwrite',
    '--quiet',
    '--report',
    convertReportPath,
  ]
  if (args.contactSheet) {
    commandArgs.push(
      '--contact-sheet',
      '--contact-thumb',
      args.contactThumb,
      '--contact-output',
      contactSheetPath,
    )
  }

  const convertStart = performance.now()
  const convert = runCommand(bin, commandArgs, 'xdoc convert png')
  const convertMs = elapsedMs(convertStart)
  if (convert.stdout.trim()) writeFileSync(join(outDir, 'convert-stdout.txt'), convert.stdout)
  if (convert.stderr.trim()) writeFileSync(join(outDir, 'convert-stderr.txt'), convert.stderr)

  const files = listPngFiles(previewDir)
  const totalBytes = files.reduce((sum, file) => sum + file.bytes, 0)
  const contactSheetExists = args.contactSheet && existsSync(contactSheetPath)
  const contactSheetBytes = contactSheetExists ? statSync(contactSheetPath).size : 0
  const countEqualsSlides = expectedCount === null ? false : files.length === expectedCount
  const previewNonEmpty = files.length > 0 && files.every((file) => file.bytes > 0)

  return {
    paths: {
      previews: previewDir,
      convertReport: existsSync(convertReportPath) ? convertReportPath : null,
      contactSheet: args.contactSheet ? contactSheetPath : null,
    },
    timing: {
      convertMs,
    },
    previews: {
      enabled: true,
      dir: relative(WORK_ROOT, previewDir),
      count: files.length,
      expectedCount,
      countEqualsSlides,
      nonEmpty: previewNonEmpty,
      totalBytes,
      files: files.map((file) => ({
        name: file.name,
        path: relative(WORK_ROOT, file.path),
        bytes: file.bytes,
      })),
    },
    contactSheet: {
      enabled: args.contactSheet,
      path: args.contactSheet ? relative(WORK_ROOT, contactSheetPath) : null,
      exists: contactSheetExists,
      bytes: contactSheetBytes,
      nonEmpty: contactSheetExists && contactSheetBytes > 0,
    },
    skipped: {
      previews: false,
      contactSheet: !args.contactSheet,
    },
  }
}

function expectedPreviewCount({ content, vision }) {
  if (Number.isInteger(vision.slideCount)) return vision.slideCount
  const contentSlides = content.slides?.length
  return Number.isInteger(contentSlides) ? contentSlides : null
}

function addMaxGate(addGate, name, actual, expected) {
  if (expected === undefined) return
  addGate(name, actual <= expected, { actual, expected })
}

function addExactGate(addGate, name, actual, expected) {
  if (expected === undefined) return
  addGate(name, actual === expected, { actual, expected })
}

function evaluateExpected({
  benchCase,
  expected,
  content,
  validation,
  patch,
  dryRun,
  apply,
  vision,
  previews,
  contactSheet,
  args,
}) {
  const gates = []
  const addGate = (name, passed, details = {}) => gates.push({ name, passed, ...details })
  const expectedCfg = expected.expected ?? {}
  const slideTypes = new Set((content.slides ?? []).map((slide) => slide.type))
  const fitErrors = countFitErrors(validation.fitDiagnostics)
  const fitWarnings = countFitWarnings(validation.fitDiagnostics)
  const blockingFitDiagnostics = countBlockingFitDiagnostics(validation.fitDiagnostics)

  if (expectedCfg.minSlides !== undefined) {
    addGate('content.minSlides', (content.slides?.length ?? 0) >= expectedCfg.minSlides, {
      actual: content.slides?.length ?? 0,
      expected: expectedCfg.minSlides,
    })
  }

  for (const type of expectedCfg.requiredSlideTypes ?? []) {
    addGate(`content.requiredSlideType.${type}`, slideTypes.has(type), { expected: type })
  }

  if (expectedCfg.validate?.errors !== undefined) {
    addGate('validate.errors', validation.errors.length <= expectedCfg.validate.errors, {
      actual: validation.errors.length,
      expected: expectedCfg.validate.errors,
    })
  }

  if (expectedCfg.validate?.blockingWarnings !== undefined) {
    const blockingWarnings = countBlockingWarnings(validation.warnings)
    addGate(
      'validate.blockingWarnings',
      blockingWarnings <= expectedCfg.validate.blockingWarnings,
      {
        actual: blockingWarnings,
        expected: expectedCfg.validate.blockingWarnings,
      },
    )
  }
  if (expectedCfg.validate?.minWarnings !== undefined) {
    addGate(
      'validate.minWarnings',
      validation.warnings.length >= expectedCfg.validate.minWarnings,
      {
        actual: validation.warnings.length,
        expected: expectedCfg.validate.minWarnings,
      },
    )
  }
  if (expectedCfg.validate?.maxWarnings !== undefined) {
    addGate(
      'validate.maxWarnings',
      validation.warnings.length <= expectedCfg.validate.maxWarnings,
      {
        actual: validation.warnings.length,
        expected: expectedCfg.validate.maxWarnings,
      },
    )
  }

  if (expectedCfg.fitDiagnostics?.errors !== undefined) {
    addGate('fitDiagnostics.errors', fitErrors <= expectedCfg.fitDiagnostics.errors, {
      actual: fitErrors,
      expected: expectedCfg.fitDiagnostics.errors,
    })
  }

  if (expectedCfg.fitDiagnostics?.blockingWarnings !== undefined) {
    addGate(
      'fitDiagnostics.blockingWarnings',
      blockingFitDiagnostics <= expectedCfg.fitDiagnostics.blockingWarnings,
      {
        actual: blockingFitDiagnostics,
        expected: expectedCfg.fitDiagnostics.blockingWarnings,
      },
    )
  }
  if (expectedCfg.fitDiagnostics?.minWarnings !== undefined) {
    addGate('fitDiagnostics.minWarnings', fitWarnings >= expectedCfg.fitDiagnostics.minWarnings, {
      actual: fitWarnings,
      expected: expectedCfg.fitDiagnostics.minWarnings,
    })
  }
  if (expectedCfg.fitDiagnostics?.maxWarnings !== undefined) {
    addGate('fitDiagnostics.maxWarnings', fitWarnings <= expectedCfg.fitDiagnostics.maxWarnings, {
      actual: fitWarnings,
      expected: expectedCfg.fitDiagnostics.maxWarnings,
    })
  }

  if (args.failOnFit === 'error') {
    addGate('fitDiagnostics.failOnError', fitErrors === 0, { actual: fitErrors })
  } else if (args.failOnFit === 'warning') {
    addGate('fitDiagnostics.failOnWarning', fitErrors + fitWarnings === 0, {
      actual: fitErrors + fitWarnings,
    })
  }

  if (expectedCfg.patchOps?.min !== undefined) {
    addGate('patch.ops.min', (patch.ops?.length ?? 0) >= expectedCfg.patchOps.min, {
      actual: patch.ops?.length ?? 0,
      expected: expectedCfg.patchOps.min,
    })
  }
  if (expectedCfg.patchOps?.max !== undefined) {
    addGate('patch.ops.max', (patch.ops?.length ?? 0) <= expectedCfg.patchOps.max, {
      actual: patch.ops?.length ?? 0,
      expected: expectedCfg.patchOps.max,
    })
  }

  if (expectedCfg.dryRun) {
    addExactGate(addGate, 'dryRun.status', dryRun.status, expectedCfg.dryRun.status)
    addMaxGate(addGate, 'dryRun.warnings', dryRun.warnings, expectedCfg.dryRun.warnings)
    addMaxGate(
      addGate,
      'dryRun.visualRisks.high',
      dryRun.visualRisks.high,
      expectedCfg.dryRun.visualRisksHigh,
    )
    addMaxGate(
      addGate,
      'dryRun.visualRisks.medium',
      dryRun.visualRisks.medium,
      expectedCfg.dryRun.visualRisksMedium,
    )
    addMaxGate(
      addGate,
      'dryRun.visualRisks.low',
      dryRun.visualRisks.low,
      expectedCfg.dryRun.visualRisksLow,
    )
  }

  if (expectedCfg.apply) {
    addExactGate(addGate, 'apply.status', apply.status, expectedCfg.apply.status)
    addMaxGate(addGate, 'apply.warnings', apply.warnings, expectedCfg.apply.warnings)
    addMaxGate(
      addGate,
      'apply.visualRisks.high',
      apply.visualRisks.high,
      expectedCfg.apply.visualRisksHigh,
    )
    addMaxGate(
      addGate,
      'apply.visualRisks.medium',
      apply.visualRisks.medium,
      expectedCfg.apply.visualRisksMedium,
    )
  }

  if (expectedCfg.vision) {
    addExactGate(addGate, 'vision.status', vision.status, expectedCfg.vision.status)
    addMaxGate(addGate, 'vision.high', vision.bySeverity.high, expectedCfg.vision.high)
    addMaxGate(addGate, 'vision.medium', vision.bySeverity.medium, expectedCfg.vision.medium)
    addMaxGate(addGate, 'vision.low', vision.bySeverity.low, expectedCfg.vision.low)
    addMaxGate(addGate, 'vision.newLow', vision.lowBuckets?.new, expectedCfg.vision.newLow)
    addMaxGate(
      addGate,
      'vision.changedLow',
      vision.lowBuckets?.changed,
      expectedCfg.vision.changedLow,
    )
    addMaxGate(
      addGate,
      'vision.reviewableLow',
      vision.lowBuckets?.reviewable,
      expectedCfg.vision.reviewableLow,
    )
    addMaxGate(addGate, 'vision.issueCount', vision.issueCount, expectedCfg.vision.issueCount)
  }
  if (args.failOnVision === 'high') {
    addGate('vision.failOnHigh', vision.bySeverity.high === 0, {
      actual: vision.bySeverity.high,
    })
  } else if (args.failOnVision === 'medium') {
    addGate('vision.failOnMedium', vision.bySeverity.high + vision.bySeverity.medium === 0, {
      actual: vision.bySeverity.high + vision.bySeverity.medium,
    })
  } else if (args.failOnVision === 'new-low') {
    const hardIssues = vision.bySeverity.high + vision.bySeverity.medium
    const reviewableLow = vision.lowBuckets?.reviewable ?? 0
    addGate('vision.failOnNewLow', hardIssues + reviewableLow === 0, {
      hardIssues,
      reviewableLow,
    })
  } else if (args.failOnVision === 'any') {
    addGate('vision.failOnAny', vision.issueCount === 0, { actual: vision.issueCount })
  }

  if (expectedCfg.previews) {
    addExactGate(addGate, 'previews.enabled', previews.enabled, expectedCfg.previews.enabled)
    if (expectedCfg.previews.countEqualsSlides !== undefined) {
      addGate(
        'previews.countEqualsSlides',
        previews.countEqualsSlides === expectedCfg.previews.countEqualsSlides,
        {
          actual: previews.countEqualsSlides,
          expected: expectedCfg.previews.countEqualsSlides,
          count: previews.count,
          expectedCount: previews.expectedCount,
        },
      )
    }
    addExactGate(addGate, 'previews.nonEmpty', previews.nonEmpty, expectedCfg.previews.nonEmpty)
  }

  if (expectedCfg.contactSheet) {
    addExactGate(
      addGate,
      'contactSheet.enabled',
      contactSheet.enabled,
      expectedCfg.contactSheet.enabled,
    )
    addExactGate(
      addGate,
      'contactSheet.exists',
      contactSheet.exists,
      expectedCfg.contactSheet.exists,
    )
    addExactGate(
      addGate,
      'contactSheet.nonEmpty',
      contactSheet.nonEmpty,
      expectedCfg.contactSheet.nonEmpty,
    )
  }

  return {
    caseId: benchCase.id,
    passed: gates.every((gate) => gate.passed),
    gates,
  }
}

async function runCase(benchCase, args) {
  const slug = caseSlug(benchCase)
  const outDir = join(args.out, benchCase.deckkit, slug)
  if (args.clean && existsSync(outDir)) rmSync(outDir, { recursive: true, force: true })
  mkdirSync(outDir, { recursive: true })

  const contentPath = resolveVisual(benchCase.contentPath)
  const buildPath = resolveVisual(benchCase.buildPath)
  const expectedPath = resolveVisual(benchCase.expectedPath)
  const expected = readJson(expectedPath)
  const runs = []
  let content
  let validation
  let build

  for (let i = 0; i < args.repeat; i += 1) {
    const totalStart = performance.now()
    const validateStart = performance.now()
    content = await loadContent(contentPath)
    validation = validateContent(content, { deckkit: benchCase.deckkit })
    const validateMs = elapsedMs(validateStart)

    const buildStart = performance.now()
    build = runBuild(buildPath, contentPath)
    const buildMs = elapsedMs(buildStart)

    runs.push({
      iteration: i + 1,
      validateMs,
      buildMs,
      totalMs: elapsedMs(totalStart),
    })
  }

  const timing = summarizeTimings(runs)
  const patchPath = join(outDir, 'patch.json')
  const deckPath = join(outDir, 'deck.pptx')
  const timingPath = join(outDir, 'timing.json')
  const summaryPath = join(outDir, 'summary.json')
  const baselinePath = join(VISUAL_ROOT, 'baselines', `${benchCase.id}.vision-baseline.json`)
  const deckkitEntry = loadDeckkitEntry(benchCase.deckkit)
  writeJson(patchPath, build.patch)
  writeJson(timingPath, timing)
  if (build.stderr.trim()) writeFileSync(join(outDir, 'build-stderr.txt'), build.stderr)
  const xdoc = runXdocStages({ args, patchPath, deckPath, outDir })
  let visionBaseline = readOptionalJson(baselinePath)
  let baselineUpdated = false
  if (args.updateBaseline) {
    visionBaseline = createVisionBaseline(xdoc.visionReport, {
      deckkit: benchCase.deckkit,
      caseId: benchCase.id,
      kind: benchCase.kind,
      deckkitEntry,
    })
    writeJson(baselinePath, visionBaseline)
    baselineUpdated = true
  }
  xdoc.vision = summarizeVisionReport(xdoc.visionReport, {
    baseline: visionBaseline,
    deckkitEntry,
    baselinePath: relative(WORK_ROOT, baselinePath),
    baselineUpdated,
  })
  const preview = runPreviewStages({
    args,
    deckPath: xdoc.paths.deck,
    outDir,
    expectedCount: expectedPreviewCount({ content, vision: xdoc.vision }),
  })

  const gate = evaluateExpected({
    benchCase,
    expected,
    content,
    validation,
    patch: build.patch,
    dryRun: xdoc.dryRun,
    apply: xdoc.apply,
    vision: xdoc.vision,
    previews: preview.previews,
    contactSheet: preview.contactSheet,
    args,
  })
  const summary = {
    schemaVersion: 'pptx-nova-deckkit-benchmark-summary/v1',
    caseId: benchCase.id,
    deckkit: benchCase.deckkit,
    kind: benchCase.kind,
    paths: {
      content: relative(WORK_ROOT, contentPath),
      build: relative(WORK_ROOT, buildPath),
      expected: relative(WORK_ROOT, expectedPath),
      patch: relative(WORK_ROOT, patchPath),
      timing: relative(WORK_ROOT, timingPath),
      deck: relative(WORK_ROOT, xdoc.paths.deck),
      dryRun: relative(WORK_ROOT, xdoc.paths.dryRun),
      apply: relative(WORK_ROOT, xdoc.paths.apply),
      vision: relative(WORK_ROOT, xdoc.paths.vision),
      visionBaseline: relative(WORK_ROOT, baselinePath),
      previews: relative(WORK_ROOT, preview.paths.previews),
      convertReport: preview.paths.convertReport
        ? relative(WORK_ROOT, preview.paths.convertReport)
        : null,
      contactSheet: preview.paths.contactSheet
        ? relative(WORK_ROOT, preview.paths.contactSheet)
        : null,
    },
    validation: {
      valid: validation.valid,
      errors: validation.errors,
      warnings: validation.warnings,
      fitDiagnostics: validation.fitDiagnostics,
    },
    patch: {
      schemaVersion: build.patch.schemaVersion,
      ops: build.patch.ops?.length ?? 0,
    },
    dryRun: xdoc.dryRun,
    apply: xdoc.apply,
    vision: xdoc.vision,
    previews: preview.previews,
    contactSheet: preview.contactSheet,
    skipped: {
      dryRun: false,
      apply: false,
      vision: false,
      previews: preview.skipped.previews,
      contactSheet: preview.skipped.contactSheet,
      xdocBin: args.xdocBin ? relative(WORK_ROOT, resolve(args.xdocBin)) : '',
    },
    requested: {
      renderPreviews: args.renderPreviews,
      contactSheet: args.contactSheet,
      failOnVision: args.failOnVision,
      updateBaseline: args.updateBaseline,
    },
    timing: {
      ...timing,
      xdoc: xdoc.timing,
      preview: preview.timing,
    },
    gate,
  }
  writeJson(summaryPath, summary)
  return summary
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const index = readJson(join(VISUAL_ROOT, 'index.json'))
  const cases = selectCases(index, args)
  if (cases.length === 0) throw new Error('No benchmark cases matched the provided filters')

  const summaries = []
  for (const benchCase of cases) {
    const summary = await runCase(benchCase, args)
    summaries.push(summary)
    if (!args.json) {
      const status = summary.gate.passed ? 'PASS' : 'FAIL'
      const validationText =
        `errors=${summary.validation.errors.length}, ` +
        `warnings=${summary.validation.warnings.length}, ` +
        `fit=${summary.validation.fitDiagnostics.length}`
      const dryRunText = `dryRun=H${summary.dryRun.visualRisks.high}/M${summary.dryRun.visualRisks.medium}`
      const lowBuckets = summary.vision.lowBuckets ?? {}
      const visionText =
        `vision=H${summary.vision.bySeverity.high}/M${summary.vision.bySeverity.medium}` +
        `/L${summary.vision.bySeverity.low}` +
        ` new=${lowBuckets.new ?? 0} changed=${lowBuckets.changed ?? 0}`
      const pngText = `png=${summary.previews.count}/${summary.previews.expectedCount ?? '?'}`
      const contactText = `contactSheet=${summary.contactSheet.nonEmpty ? 'ok' : 'missing'}`
      process.stdout.write(
        `${status} ${summary.caseId}: ops=${summary.patch.ops}, ${validationText}, ${dryRunText}, ${visionText}, ${pngText}, ${contactText}, p50=${summary.timing.p50.totalMs}ms\n`,
      )
    }
  }

  const result = {
    schemaVersion: 'pptx-nova-deckkit-benchmark-run/v1',
    passed: summaries.every((summary) => summary.gate.passed),
    cases: summaries.map((summary) => ({
      caseId: summary.caseId,
      passed: summary.gate.passed,
      ops: summary.patch.ops,
      errors: summary.validation.errors.length,
      warnings: summary.validation.warnings.length,
      fitDiagnostics: summary.validation.fitDiagnostics.length,
      dryRunHigh: summary.dryRun.visualRisks.high,
      dryRunMedium: summary.dryRun.visualRisks.medium,
      visionHigh: summary.vision.bySeverity.high,
      visionMedium: summary.vision.bySeverity.medium,
      visionLow: summary.vision.bySeverity.low,
      visionNewLow: summary.vision.lowBuckets?.new ?? 0,
      visionChangedLow: summary.vision.lowBuckets?.changed ?? 0,
      visionBaselineUnavailable: summary.vision.lowBuckets?.baselineUnavailable === true,
      previewCount: summary.previews.count,
      previewExpectedCount: summary.previews.expectedCount,
      contactSheetBytes: summary.contactSheet.bytes,
      p50TotalMs: summary.timing.p50.totalMs,
    })),
  }

  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  if (!result.passed) process.exit(1)
}

main().catch((error) => {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
})
