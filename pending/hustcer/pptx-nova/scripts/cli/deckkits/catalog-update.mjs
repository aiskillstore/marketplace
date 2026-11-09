#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { normalizeVisionLowBuckets } from '../../lib/review/vision-baseline.mjs'

const WORK_ROOT = process.cwd()
const VISUAL_ROOT = join(SKILL_ROOT, 'benchmarks/visual')
const CATALOG_PATH = join(SKILL_ROOT, 'assets/deckkits/catalog.json')
const DEFAULT_OUT = join(WORK_ROOT, '.tmp/pptx-nova-visual')
const MINIMUM_REQUIRED_KINDS = ['golden']
const PREFERRED_KIND_ORDER = ['golden', 'stress', 'mixed-language']
const READINESS = ['experimental', 'candidate', 'production', 'default']

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/catalog-update.mjs --deckkit <id> [options]

Options:
  --deckkit <id>                  DeckKit id to update
  --out <dir>                     Benchmark output directory. Defaults to <cwd>/.tmp/pptx-nova-visual
  --catalog <path>                Catalog path. Defaults to <skill-root>/assets/deckkits/catalog.json
  --visual-index <path>           Visual benchmark index path. Defaults to <skill-root>/benchmarks/visual/index.json
  --date <yyyy-mm-dd>             Benchmark date. Defaults to the local current date
  --manual-hard-defects <n>       Explicit manual PNG hard-defect count
  --readiness <level>             Set readiness: experimental|candidate|production|default
  --confirm-manual-png-review     Required when promoting to production/default
  --write                         Persist the catalog update. Without this flag, print a dry run
  --json                          Print machine-readable result
  --help                          Show this help

Typical flow:
  node <skill-root>/scripts/cli/deckkits/benchmark.mjs --deckkit consulting-dark --all --repeat 3 --clean
  node <skill-root>/scripts/cli/deckkits/catalog-update.mjs --deckkit consulting-dark --write
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    out: DEFAULT_OUT,
    catalog: CATALOG_PATH,
    visualIndex: join(VISUAL_ROOT, 'index.json'),
    date: localDate(),
    manualHardDefects: undefined,
    readiness: '',
    confirmManualPngReview: false,
    write: false,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--write') {
      args.write = true
    } else if (arg === '--confirm-manual-png-review') {
      args.confirmManualPngReview = true
    } else if (arg === '--deckkit') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--out') {
      args.out = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--catalog') {
      args.catalog = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--visual-index') {
      args.visualIndex = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--date') {
      args.date = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--manual-hard-defects') {
      args.manualHardDefects = parseNonNegativeInt(valueAfter(argv, i, arg), arg)
      i += 1
    } else if (arg === '--readiness') {
      args.readiness = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.deckkit) throw new Error(`--deckkit is required.\n\n${usage}`)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(args.date)) {
    throw new Error('--date must use yyyy-mm-dd format')
  }
  if (args.readiness && !READINESS.includes(args.readiness)) {
    throw new Error(`--readiness must be one of ${READINESS.join('|')}`)
  }
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseNonNegativeInt(value, flag) {
  const parsed = Number.parseInt(value, 10)
  if (!Number.isInteger(parsed) || String(parsed) !== value || parsed < 0) {
    throw new Error(`${flag} must be a non-negative integer`)
  }
  return parsed
}

function localDate(date = new Date()) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return local.toISOString().slice(0, 10)
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function rel(path) {
  return relative(WORK_ROOT, path)
}

function caseSlug(benchCase) {
  return benchCase.id.includes('.') ? benchCase.id.split('.').slice(1).join('.') : benchCase.id
}

function summaryPathFor(outDir, benchCase) {
  return join(outDir, benchCase.deckkit, caseSlug(benchCase), 'summary.json')
}

function kindRank(kind) {
  const rank = PREFERRED_KIND_ORDER.indexOf(kind)
  return rank === -1 ? PREFERRED_KIND_ORDER.length : rank
}

function orderedBenchmarkCases(deckkitCases) {
  return [...deckkitCases].sort((a, b) => {
    const rankDiff = kindRank(a.kind) - kindRank(b.kind)
    if (rankDiff !== 0) return rankDiff
    return a.id.localeCompare(b.id, 'en')
  })
}

function uniqueKinds(deckkitCases) {
  return [...new Set(orderedBenchmarkCases(deckkitCases).map((benchCase) => benchCase.kind))]
}

function countBlockingFitDiagnostics(fitDiagnostics) {
  return fitDiagnostics.filter((item) => item.blocking === true || item.severity === 'error').length
}

function sumLowBuckets(items) {
  return items.reduce(
    (acc, item) => {
      const buckets = normalizeVisionLowBuckets(item.vision.lowBuckets)
      return {
        total: acc.total + buckets.total,
        styleAllowed: acc.styleAllowed + buckets.styleAllowed,
        baselineKnown: acc.baselineKnown + buckets.baselineKnown,
        new: acc.new + buckets.new,
        changed: acc.changed + buckets.changed,
        resolved: acc.resolved + buckets.resolved,
        reviewable: acc.reviewable + buckets.reviewable,
        baselineUnavailableCases:
          acc.baselineUnavailableCases + (buckets.baselineUnavailable ? 1 : 0),
        baselineUpdatedCases: acc.baselineUpdatedCases + (buckets.baselineUpdated ? 1 : 0),
      }
    },
    {
      total: 0,
      styleAllowed: 0,
      baselineKnown: 0,
      new: 0,
      changed: 0,
      resolved: 0,
      reviewable: 0,
      baselineUnavailableCases: 0,
      baselineUpdatedCases: 0,
    },
  )
}

function summarizeCase(summaryPath, benchCase, indexRoot) {
  const summary = readJson(summaryPath)
  const fitDiagnostics = summary.validation?.fitDiagnostics ?? []
  const vision = summary.vision?.bySeverity ?? {}
  const lowBuckets = normalizeVisionLowBuckets(summary.vision?.lowBuckets)
  const previews = summary.previews ?? {}
  const contactSheet = summary.contactSheet ?? {}

  return {
    caseId: summary.caseId ?? benchCase.id,
    kind: summary.kind ?? benchCase.kind,
    passed: summary.gate?.passed === true,
    summaryPath: rel(summaryPath),
    reviewPath: benchCase.reviewPath ? rel(resolve(indexRoot, benchCase.reviewPath)) : null,
    validation: {
      valid: summary.validation?.valid === true,
      errors: summary.validation?.errors?.length ?? 0,
      warnings: summary.validation?.warnings?.length ?? 0,
      fitDiagnostics: fitDiagnostics.length,
      blockingFitDiagnostics: countBlockingFitDiagnostics(fitDiagnostics),
    },
    dryRun: {
      high: summary.dryRun?.visualRisks?.high ?? 0,
      medium: summary.dryRun?.visualRisks?.medium ?? 0,
    },
    vision: {
      high: vision.high ?? 0,
      medium: vision.medium ?? 0,
      low: vision.low ?? 0,
      lowBuckets,
    },
    previews: {
      count: previews.count ?? 0,
      expectedCount: previews.expectedCount ?? null,
      nonEmpty: previews.nonEmpty === true,
      countEqualsSlides: previews.countEqualsSlides === true,
    },
    contactSheet: {
      nonEmpty: contactSheet.nonEmpty === true,
      bytes: contactSheet.bytes ?? 0,
    },
    patchOps: summary.patch?.ops ?? 0,
    p50TotalMs: summary.timing?.p50?.totalMs ?? null,
  }
}

function collectBenchmark({ index, outDir, deckkit, date }) {
  const deckkitCases = index.cases.filter((benchCase) => benchCase.deckkit === deckkit)
  const indexRoot = dirname(index.__path)
  const blockers = []
  const cases = []
  const indexedKinds = uniqueKinds(deckkitCases)

  for (const kind of MINIMUM_REQUIRED_KINDS) {
    if (!indexedKinds.includes(kind))
      blockers.push(`missing ${kind} case in visual benchmark index`)
  }

  for (const benchCase of orderedBenchmarkCases(deckkitCases)) {
    const summaryPath = summaryPathFor(outDir, benchCase)
    if (!existsSync(summaryPath)) {
      blockers.push(`missing summary for ${benchCase.id}; run benchmark first`)
      continue
    }

    const summary = summarizeCase(summaryPath, benchCase, indexRoot)
    cases.push(summary)
    if (!summary.passed) blockers.push(`${benchCase.id} gate did not pass`)
    if (summary.validation.errors > 0) {
      blockers.push(`${benchCase.id} has ${summary.validation.errors} validation error(s)`)
    }
    if (summary.validation.blockingFitDiagnostics > 0) {
      blockers.push(
        `${benchCase.id} has ${summary.validation.blockingFitDiagnostics} blocking fit diagnostic(s)`,
      )
    }
    if (summary.vision.high > 0 || summary.vision.medium > 0) {
      blockers.push(
        `${benchCase.id} has vision high=${summary.vision.high} medium=${summary.vision.medium}`,
      )
    }
    if (!summary.previews.nonEmpty || !summary.previews.countEqualsSlides) {
      blockers.push(`${benchCase.id} PNG preview gate did not pass`)
    }
    if (!summary.contactSheet.nonEmpty) {
      blockers.push(`${benchCase.id} contact sheet gate did not pass`)
    }
  }

  const vision = cases.reduce(
    (acc, item) => ({
      high: acc.high + item.vision.high,
      medium: acc.medium + item.vision.medium,
      low: acc.low + item.vision.low,
    }),
    { high: 0, medium: 0, low: 0 },
  )
  vision.lowBuckets = sumLowBuckets(cases)

  return {
    schemaVersion: 'pptx-nova-deckkit-quality-benchmark/v1',
    date,
    source: {
      visualIndex: rel(resolve(index.__path)),
      out: rel(outDir),
    },
    minimumRequiredKinds: MINIMUM_REQUIRED_KINDS,
    requiredKinds: indexedKinds.length > 0 ? indexedKinds : MINIMUM_REQUIRED_KINDS,
    gatedKinds: indexedKinds,
    passed: blockers.length === 0,
    vision,
    cases,
    blockers,
  }
}

function assertPromotionAllowed({
  previousReadiness,
  requestedReadiness,
  targetReadiness,
  benchmark,
  nextQuality,
  confirmManualPngReview,
}) {
  if (!['production', 'default'].includes(targetReadiness)) return []
  const blockers = []
  if (!benchmark.passed) blockers.push('benchmark must pass before production/default promotion')
  if (benchmark.vision.high !== 0 || benchmark.vision.medium !== 0) {
    blockers.push('benchmark vision high/medium must both be 0')
  }
  if (
    (benchmark.vision.lowBuckets?.new ?? 0) !== 0 ||
    (benchmark.vision.lowBuckets?.changed ?? 0) !== 0
  ) {
    blockers.push('benchmark vision new/changed low issues must both be 0')
  }
  if ((benchmark.vision.lowBuckets?.baselineUnavailableCases ?? 0) !== 0) {
    blockers.push('benchmark vision low baseline must be available for every case')
  }
  if (nextQuality.manualHardDefects !== 0) {
    blockers.push('manualHardDefects must be 0 before production/default promotion')
  }
  if ((nextQuality.knownBlockingLimits ?? []).length > 0) {
    blockers.push('knownBlockingLimits must be empty before production/default promotion')
  }
  const isPromotionRequest =
    requestedReadiness &&
    ['production', 'default'].includes(targetReadiness) &&
    previousReadiness !== targetReadiness
  if (isPromotionRequest && !confirmManualPngReview) {
    blockers.push('--confirm-manual-png-review is required for production/default promotion')
  }
  return blockers
}

function updateCatalog(args) {
  const catalog = readJson(args.catalog)
  const index = {
    ...readJson(args.visualIndex),
    __path: args.visualIndex,
  }
  const entry = catalog.entries?.find((candidate) => candidate.id === args.deckkit)
  if (!entry) throw new Error(`DeckKit "${args.deckkit}" is missing from catalog`)

  const benchmark = collectBenchmark({
    index,
    outDir: args.out,
    deckkit: args.deckkit,
    date: args.date,
  })
  if (!benchmark.passed) {
    throw new Error(
      ['benchmark summaries are not eligible for catalog update:', ...benchmark.blockers]
        .map((line) => `- ${line}`)
        .join('\n'),
    )
  }

  const currentQuality = entry.quality && typeof entry.quality === 'object' ? entry.quality : {}
  const previousReadiness = entry.readiness
  const nextQuality = {
    ...currentQuality,
    lastBenchmark: args.date,
    vision: benchmark.vision,
    manualHardDefects:
      args.manualHardDefects === undefined
        ? (currentQuality.manualHardDefects ?? null)
        : args.manualHardDefects,
    knownBlockingLimits: Array.isArray(currentQuality.knownBlockingLimits)
      ? currentQuality.knownBlockingLimits
      : [],
    benchmark,
  }

  const nextReadiness = args.readiness || entry.readiness
  const promotionBlockers = assertPromotionAllowed({
    previousReadiness,
    requestedReadiness: args.readiness,
    targetReadiness: nextReadiness,
    benchmark,
    nextQuality,
    confirmManualPngReview: args.confirmManualPngReview,
  })
  if (promotionBlockers.length > 0) {
    throw new Error(
      ['catalog promotion is blocked:', ...promotionBlockers].map((line) => `- ${line}`).join('\n'),
    )
  }

  entry.quality = nextQuality
  if (args.readiness) entry.readiness = args.readiness
  if (args.write) writeJson(args.catalog, catalog)

  return {
    schemaVersion: 'pptx-nova-deckkit-catalog-update/v1',
    deckkit: args.deckkit,
    written: args.write,
    catalogPath: rel(args.catalog),
    readiness: {
      previous: previousReadiness,
      next: nextReadiness,
    },
    quality: nextQuality,
  }
}

function printHuman(result) {
  process.stdout.write(`DeckKit catalog update: ${result.deckkit}\n`)
  process.stdout.write(`- catalog: ${result.catalogPath}\n`)
  process.stdout.write(`- write: ${result.written ? 'yes' : 'no (dry run)'}\n`)
  process.stdout.write(`- lastBenchmark: ${result.quality.lastBenchmark}\n`)
  process.stdout.write(
    `- vision: high=${result.quality.vision.high} medium=${result.quality.vision.medium} low=${result.quality.vision.low}\n`,
  )
  process.stdout.write(
    `- vision low review: new=${result.quality.vision.lowBuckets.new} changed=${result.quality.vision.lowBuckets.changed} styleAllowed=${result.quality.vision.lowBuckets.styleAllowed} known=${result.quality.vision.lowBuckets.baselineKnown}\n`,
  )
  process.stdout.write(`- manualHardDefects: ${result.quality.manualHardDefects ?? 'unset'}\n`)
  process.stdout.write(`- benchmark cases: ${result.quality.benchmark.cases.length}\n`)
  process.stdout.write(`- readiness: ${result.readiness.next}\n`)
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const result = updateCatalog(args)
  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  else printHuman(result)
}

try {
  main()
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
