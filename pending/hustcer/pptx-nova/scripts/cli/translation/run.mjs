#!/usr/bin/env node
import { cliPath } from '../../lib/runtime/skill-paths.mjs'
import { ensureRenderContext, verifyRenderContext } from '../../lib/review/render-context.mjs'
import { verifyDiffEvidence } from '../../lib/review/diff-evidence.mjs'
import { createHash } from 'node:crypto'
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { basename, dirname, extname, join, resolve } from 'node:path'
import { performance } from 'node:perf_hooks'
import {
  PhaseFailure,
  summarizePhaseError,
  buildAgentResult as buildRuntimeAgentResult,
  buildPerformanceSummary as buildRuntimePerformanceSummary,
  createRunnerRuntime,
  durationMs,
  finalizeRunnerSummary,
  gateByName,
  gateStatus,
  relativeArtifact,
} from '../../lib/runtime/runner-runtime.mjs'
import {
  analyzeCompareRendering,
  materializeCompareAliases,
} from '../../lib/review/visual-evidence.mjs'
import { canonicalEvidencePath } from '../../lib/review/evidence-paths.mjs'
import { assertNewOrPreProbedRunDir } from '../../lib/runtime/run-dir.mjs'
import {
  analyzeTypedTextAttributeAllowlist,
  parseTextAttributeAllowlist,
} from '../../lib/translation/translation-contract.mjs'
import {
  createPageBitmapCacheBinding,
  pageBitmapCacheMetrics,
  snapshotPageBitmapCache,
} from '../../lib/review/page-bitmap-cache.mjs'
import { createProgressReporter } from '../../lib/runtime/progress.mjs'

const COMPARE_SCRIPT = cliPath('review/compare.mjs')
const COMPARE_GATE_SCRIPT = cliPath('review/compare-gate.mjs')
const MULTI_COLUMN_REVIEW_GATE_SCRIPT = cliPath('review/multi-column-gate.mjs')
const AGENT_SUMMARY_SCHEMA_VERSION = 'pptx-nova-agent-summary/v1'
const AGENT_RESULT_SCHEMA_VERSION = 'pptx-nova-translation-result/v1'
// xdoc `i18n-scan --mode candidate --json` emits the compact candidate-result
// schema on stdout; the full scan schema only appears with --json-full or in
// the report persisted via --output. Accept both so the gate binds to the
// contract, not to one projection of it.
const CANDIDATE_SCAN_SCHEMAS = ['pptx-i18n-candidate-result/v1', 'pptx-i18n-scan/v1']
let progressReporter = createProgressReporter({ mode: 'off' })
const { runJsonPhase, addInternalPhase, requireGate } = createRunnerRuntime({
  getProgressReporter: () => progressReporter,
})

const usage = `Usage:
  node <skill-root>/scripts/cli/translation/run.mjs --source <source.pptx> --candidate <candidate.pptx> --units-file <i18n-scan.json> --translations <translations.json> --output <output.pptx> [options]

Options:
  --source <path>                    Read-only source PPTX
  --candidate <path>                 Stable translated candidate PPTX
  --units-file <path>                     Classified/source i18n scan consumed by i18n-plan
  --translations <path>              pptx-i18n-translations/v1 contract
  --output <path>                    Final PPTX published only after machine gates pass
  --run-dir <path>                   New, empty, or pre-probed (only xdoc-capabilities.json) finalization run directory
  --xdoc-bin <path>                  xdoc executable. Defaults to xdoc
  --allow-text-attrs <csv>           Explicit typed i18n-style-diff allowlist
  --multi-column-review-gate <path>  Optional passing bound review gate for review-only vision blockers
  --contact-diff                     Materialize contact-diff aliases from translation-compare evidence
  --compare-chunk-size <n>           Maximum slides per compare PNG. Defaults to 20
  --compare-concurrency <n>          Concurrent compare part renders. Defaults to 3
  --overwrite                        Allow replacing an existing final output after machine gates pass
  --progress <mode>                  Progress stream: auto|jsonl|text|off. Defaults to auto
  --progress-file <path>             Progress JSONL archive. Defaults to <run-dir>/progress.jsonl;
                                     pass "none" to disable. While active, stderr only carries
                                     single-line phase-boundary summaries
  --prompt-text <text>               Original user prompt; archived to <run-dir>/prompt.txt
  --prompt-file <path>               Read the original user prompt from a file
  --json                             Print compact Agent result
  --json-full                        Print complete run summary for debugging
  --help                             Show this help

This runner finalizes an already translated stable candidate. It does not create translations or mark
manual review complete.
`

function parseArgs(argv) {
  const args = {
    source: '',
    candidate: '',
    units: '',
    translations: '',
    output: '',
    runDir: '',
    xdocBin: 'xdoc',
    allowTextAttrs: '',
    multiColumnReviewGate: '',
    contactDiff: false,
    compareChunkSize: 20,
    compareConcurrency: 3,
    overwrite: false,
    progress: 'auto',
    progressFile: '',
    promptText: '',
    promptFile: '',
    json: false,
    jsonFull: false,
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--contact-diff') args.contactDiff = true
    else if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else if (arg === '--json-full') {
      args.json = true
      args.jsonFull = true
    } else if (arg in valueFlags) {
      const key = valueFlags[arg]
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
      args[key] = ['compareChunkSize', 'compareConcurrency'].includes(key) ? Number(value) : value
      index += 1
    } else throw new Error(`Unknown option: ${arg}\n\n${usage}`)
  }
  for (const key of ['source', 'candidate', 'units', 'translations', 'output']) {
    if (!args[key]) throw new Error(`--${key} is required.\n\n${usage}`)
  }
  if (!Number.isInteger(args.compareChunkSize) || args.compareChunkSize <= 0) {
    throw new Error('--compare-chunk-size must be a positive integer')
  }
  if (
    !Number.isInteger(args.compareConcurrency) ||
    args.compareConcurrency <= 0 ||
    args.compareConcurrency > 16
  ) {
    throw new Error('--compare-concurrency must be an integer between 1 and 16')
  }
  if (args.promptText && args.promptFile) {
    throw new Error('--prompt-text and --prompt-file are mutually exclusive')
  }
  return args
}

const valueFlags = {
  '--source': 'source',
  '--candidate': 'candidate',
  '--units-file': 'units',
  '--translations': 'translations',
  '--output': 'output',
  '--run-dir': 'runDir',
  '--xdoc-bin': 'xdocBin',
  '--allow-text-attrs': 'allowTextAttrs',
  '--multi-column-review-gate': 'multiColumnReviewGate',
  '--compare-chunk-size': 'compareChunkSize',
  '--compare-concurrency': 'compareConcurrency',
  '--progress': 'progress',
  '--progress-file': 'progressFile',
  '--prompt-text': 'promptText',
  '--prompt-file': 'promptFile',
}

function timestamp(now = new Date()) {
  const pad = (value) => String(value).padStart(2, '0')
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
}

function safeSlug(value) {
  return (
    String(value)
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 64) || 'deck'
  )
}

function normalizeExecutable(value, cwd) {
  return /[\\/]/.test(value) ? resolve(cwd, value) : value
}

function normalizeArgs(input) {
  const cwd = process.cwd()
  const args = {
    ...input,
    source: resolve(cwd, input.source),
    candidate: resolve(cwd, input.candidate),
    units: resolve(cwd, input.units),
    translations: resolve(cwd, input.translations),
    output: resolve(cwd, input.output),
    xdocBin: normalizeExecutable(input.xdocBin, cwd),
    allowTextAttrs: parseTextAttributeAllowlist(input.allowTextAttrs).join(','),
    multiColumnReviewGate: input.multiColumnReviewGate
      ? resolve(cwd, input.multiColumnReviewGate)
      : '',
    promptFile: input.promptFile ? resolve(cwd, input.promptFile) : '',
  }
  args.runDir = input.runDir
    ? resolve(cwd, input.runDir)
    : join(
        cwd,
        '.pptx-nova',
        `translation-finalize-${safeSlug(basename(args.source, extname(args.source)))}-${timestamp()}`,
      )
  return args
}

function validatePaths(args) {
  for (const [label, path] of [
    ['source', args.source],
    ['candidate', args.candidate],
    ['units', args.units],
    ['translations', args.translations],
    ...(args.multiColumnReviewGate
      ? [['multi-column review gate', args.multiColumnReviewGate]]
      : []),
  ]) {
    if (!existsSync(path) || !statSync(path).isFile()) {
      throw new Error(`${label} does not exist or is not a file: ${path}`)
    }
  }
  if (extname(args.source).toLowerCase() !== '.pptx') throw new Error('--source must be .pptx')
  if (extname(args.candidate).toLowerCase() !== '.pptx')
    throw new Error('--candidate must be .pptx')
  if (extname(args.output).toLowerCase() !== '.pptx') throw new Error('--output must be .pptx')
  if (!existsSync(dirname(args.output))) {
    throw new Error(`final output directory does not exist: ${dirname(args.output)}`)
  }
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(
      `final output already exists; pass --overwrite only when intended: ${args.output}`,
    )
  }
  if (existsSync(args.runDir)) {
    assertNewOrPreProbedRunDir(args.runDir)
  }
  if (args.promptFile && (!existsSync(args.promptFile) || !statSync(args.promptFile).isFile())) {
    throw new Error(`--prompt-file does not exist or is not a file: ${args.promptFile}`)
  }
  const typedTextAttrs = analyzeTypedTextAttributeAllowlist(
    JSON.parse(readFileSync(args.units, 'utf8')),
    JSON.parse(readFileSync(args.translations, 'utf8')),
    args.allowTextAttrs,
  )
  if (typedTextAttrs.missing.length > 0) {
    const details = typedTextAttrs.missing
      .map(
        (entry) =>
          `${entry.attrName} (${entry.unitCount} changed unit${entry.unitCount === 1 ? '' : 's'})`,
      )
      .join(', ')
    throw new Error(
      `typed text attribute allowlist is incomplete: ${details}; retry with --allow-text-attrs ${typedTextAttrs.suggestedAllowlist.join(',')}; authorization is never added automatically`,
    )
  }
  return typedTextAttrs
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function normalizedSha256(value) {
  return String(value ?? '').replace(/^sha256:/, '')
}

function resolveEvidencePath(basePath, value) {
  return value ? canonicalEvidencePath(value, { artifactPath: basePath }) : ''
}

function reviewOnlyFindingKeys(report) {
  const blockingSeverity = (issue) => ['high', 'medium'].includes(issue?.severity)
  const findings = [
    ...(report?.newIssues ?? []).filter(blockingSeverity),
    ...(report?.worsenedIssues ?? [])
      .map((change) => change?.candidateIssue)
      .filter(blockingSeverity),
  ]
  return findings
    .filter(
      (issue) =>
        issue?.evidenceClass === 'review-only' && issue?.kind === 'multi-column-text-layout-review',
    )
    .map((issue) => `${issue.slideIndex}:${issue.shapeId}`)
    .sort()
}

function visionEvidenceIdentity(report) {
  const withoutPath = (value) => {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return null
    const { path: _path, ...identity } = value
    return identity
  }
  const canonical = {
    ...report,
    source: withoutPath(report?.source),
    candidate: withoutPath(report?.candidate),
  }
  return createHash('sha256').update(JSON.stringify(canonical)).digest('hex')
}

function artifactPaths(runDir) {
  return {
    renderContext: join(runDir, 'render-context.json'),
    source: join(runDir, 'source.pptx'),
    candidate: join(runDir, 'candidate.pptx'),
    units: join(runDir, 'i18n-units.json'),
    translations: join(runDir, 'translations.json'),
    sourceInspect: join(runDir, 'source-inspect.json'),
    styleDiff: join(runDir, 'i18n-style-diff.json'),
    candidateScan: join(runDir, 'i18n-scan-candidate.json'),
    visionDiff: join(runDir, 'vision-diff.json'),
    multiColumnReviewGate: join(runDir, 'multi-column-review-gate.json'),
    previews: join(runDir, 'previews-candidate'),
    previewReport: join(runDir, 'preview-candidate.json'),
    contactSheet: join(runDir, 'previews-candidate', 'contact-sheet.png'),
    semanticDiff: join(runDir, 'pptx-diff.json'),
    semanticDiffFull: join(runDir, 'pptx-diff-full.json'),
    compare: join(runDir, 'translation-compare.png'),
    compareReport: join(runDir, 'translation-compare.json'),
    compareGate: join(runDir, 'translation-compare-gate.json'),
    contactDiff: join(runDir, 'contact-diff.png'),
    contactDiffReport: join(runDir, 'contact-diff.json'),
    progressLog: join(runDir, 'progress.jsonl'),
    prompt: join(runDir, 'prompt.txt'),
    summary: join(runDir, 'translation-run-summary.json'),
  }
}

function initialSummary(args, artifacts) {
  return {
    schemaVersion: 'pptx-nova-translation-run/v1',
    status: 'running',
    mode: 'translation',
    machineGatesPassed: false,
    deliveryReady: false,
    needsHumanReview: true,
    source: args.source,
    candidate: args.candidate,
    output: args.output,
    runDir: args.runDir,
    artifacts: { ...artifacts, compareParts: [], contactDiffParts: [] },
    phases: [],
    gates: [],
    review: {
      required: true,
      completed: false,
      contactDiffRequested: args.contactDiff,
      instructions:
        'Review the candidate contact sheet, the complete translation-compare set, and every bound review-only page before delivery.',
    },
    requiredReferences: [],
    warnings: [],
    error: null,
  }
}

function finalizeArtifacts(summary, summaryPath) {
  summary.artifacts = Object.fromEntries(
    Object.entries(summary.artifacts).map(([key, value]) => {
      if (Array.isArray(value)) return [key, value.filter((path) => existsSync(path))]
      return [key, key === 'summary' || (value && existsSync(value)) ? value : null]
    }),
  )
  summary.artifacts.summary = summaryPath
}

function expectedSlideCount(inspect) {
  const count = Number(inspect?.presentation?.slideCount)
  if (Number.isInteger(count) && count > 0) return count
  return Array.isArray(inspect?.slides) ? inspect.slides.length : 0
}

function previewBytes(page) {
  return Number(page?.byteLength ?? page?.file?.byteLength ?? 0)
}

function previewPixels(page) {
  const width = Number(page?.width ?? page?.file?.width ?? 0)
  const height = Number(page?.height ?? page?.file?.height ?? 0)
  return width > 0 && height > 0 ? width * height : 0
}

function previewPageValid(page, runDir) {
  const descriptor = page?.file ?? page
  const pathValue = descriptor?.path ?? page?.path
  if (!pathValue) return false
  const path = resolve(runDir, pathValue)
  if (!existsSync(path) || !statSync(path).isFile()) return false
  const actualBytes = statSync(path).size
  const declaredBytes = Number(descriptor?.byteLength ?? page?.byteLength ?? 0)
  if (actualBytes <= 0 || declaredBytes !== actualBytes) return false
  if (descriptor?.status && descriptor.status !== 'ok') return false
  const declaredSha = normalizedSha256(descriptor?.sha256 ?? page?.sha256)
  if (declaredSha && declaredSha !== sha256(path)) return false
  const width = Number(descriptor?.width ?? page?.width ?? 0)
  const height = Number(descriptor?.height ?? page?.height ?? 0)
  return width > 0 && height > 0
}

function runInspect(summary, args, artifacts) {
  return runJsonPhase(summary, {
    name: 'source-inspect',
    bin: args.xdocBin,
    args: ['pptx', 'inspect', artifacts.source, '--json'],
    artifact: artifacts.sourceInspect,
  })
}

function runStyleDiff(summary, args, artifacts) {
  const commandArgs = [
    'pptx',
    'i18n-style-diff',
    '--source',
    artifacts.source,
    '--candidate',
    artifacts.candidate,
  ]
  if (args.allowTextAttrs) commandArgs.push('--allow-text-attrs', args.allowTextAttrs)
  commandArgs.push('--json')
  const report = runJsonPhase(summary, {
    name: 'i18n-style-diff',
    bin: args.xdocBin,
    args: commandArgs,
    artifact: artifacts.styleDiff,
  })
  requireGate(
    summary,
    'i18n-style-diff',
    report?.schemaVersion === 'pptx-i18n-style-diff/v1' &&
      report?.status === 'pass' &&
      report?.agentGate?.passed === true,
    {
      status: report?.status ?? null,
      blockerCount: Number(report?.agentGate?.blockerCount ?? report?.blockers?.length ?? 0),
      message: 'Translation style signatures must pass before visual finalization',
    },
  )
}

function runCandidateConsistency(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'i18n-candidate-consistency',
    bin: args.xdocBin,
    args: [
      'pptx',
      'i18n-scan',
      '--source',
      artifacts.candidate,
      '--mode',
      'candidate',
      '--units-file',
      artifacts.units,
      '--data',
      artifacts.translations,
      '--json',
    ],
    artifact: artifacts.candidateScan,
  })
  const schemaVersion = typeof report?.schemaVersion === 'string' ? report.schemaVersion : null
  requireGate(
    summary,
    'i18n-candidate-consistency-contract',
    CANDIDATE_SCAN_SCHEMAS.includes(schemaVersion),
    {
      schemaVersion,
      acceptedSchemaVersions: CANDIDATE_SCAN_SCHEMAS,
      status: report?.status ?? null,
      message: `The candidate scan must emit a known schema; got ${schemaVersion ?? 'no schemaVersion'} while accepting ${CANDIDATE_SCAN_SCHEMAS.join(' or ')} — the runner and the installed xdoc disagree on the i18n-scan contract`,
    },
  )
  requireGate(
    summary,
    'i18n-candidate-consistency',
    report?.status === 'pass' && report?.agentGate?.passed === true,
    {
      schemaVersion,
      status: report?.status ?? null,
      blockerCount: Number(report?.agentGate?.blockerCount ?? report?.blockers?.length ?? 0),
      verifiedCount: Number(report?.summary?.verifiedCount ?? 0),
      message: 'Every translated unit must resolve to its target text in the candidate',
    },
  )
}

function runVisionDiff(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'translation-vision-diff',
    bin: args.xdocBin,
    args: [
      'pptx',
      'vision-diff',
      '--source',
      artifacts.source,
      '--candidate',
      artifacts.candidate,
      '--json',
    ],
    artifact: artifacts.visionDiff,
  })
  let reviewGate = null
  if (args.multiColumnReviewGate) {
    const suppliedGate = JSON.parse(readFileSync(args.multiColumnReviewGate, 'utf8'))
    const gateCandidate = resolveEvidencePath(args.multiColumnReviewGate, suppliedGate?.candidate)
    const gateVisionDiff = resolveEvidencePath(args.multiColumnReviewGate, suppliedGate?.visionDiff)
    const gateReview = resolveEvidencePath(args.multiColumnReviewGate, suppliedGate?.review)
    requireGate(
      summary,
      'multi-column-review-input',
      suppliedGate?.schemaVersion === 'pptx-nova-multi-column-review-gate/v1' &&
        gateCandidate &&
        gateVisionDiff &&
        gateReview &&
        [gateCandidate, gateVisionDiff, gateReview].every(
          (path) => existsSync(path) && statSync(path).isFile(),
        ),
      {
        message:
          'The supplied multi-column gate must disclose existing candidate, vision-diff, and review evidence',
      },
    )
    reviewGate = runJsonPhase(summary, {
      name: 'multi-column-review-revalidate',
      bin: process.execPath,
      args: [
        MULTI_COLUMN_REVIEW_GATE_SCRIPT,
        '--candidate',
        gateCandidate,
        '--vision-diff',
        gateVisionDiff,
        '--review',
        gateReview,
        '--output',
        artifacts.multiColumnReviewGate,
        '--overwrite',
        '--json',
      ],
      artifact: artifacts.multiColumnReviewGate,
    })
    const currentReviewKeys = reviewOnlyFindingKeys(report)
    const gateVisionReport = JSON.parse(readFileSync(gateVisionDiff, 'utf8'))
    const revalidatedReviewKeys = (reviewGate?.reviewed ?? [])
      .map((item) => `${item.slideIndex}:${item.shapeId}`)
      .sort()
    const bindingValid =
      reviewGate?.schemaVersion === 'pptx-nova-multi-column-review-gate/v1' &&
      reviewGate?.status === 'pass' &&
      reviewGate?.agentGate?.passed === true &&
      sha256(gateCandidate) === sha256(artifacts.candidate) &&
      visionEvidenceIdentity(gateVisionReport) === visionEvidenceIdentity(report) &&
      JSON.stringify(currentReviewKeys) === JSON.stringify(revalidatedReviewKeys)
    requireGate(summary, 'multi-column-review-binding', bindingValid, {
      status: reviewGate?.status ?? null,
      reviewedIssueCount: Number(reviewGate?.summary?.reviewedIssueCount ?? 0),
      currentReviewKeys,
      revalidatedReviewKeys,
      message:
        'The multi-column review must revalidate its candidate, vision findings, PNG evidence, and exact current finding set',
    })
  }
  const directPass = report?.agentGate?.passed === true
  const blockersByEvidenceClass = report?.agentGate?.blockersByEvidenceClass ?? {}
  const reviewOnlyCount = Number(blockersByEvidenceClass['review-only'] ?? 0)
  const nonReviewEvidenceCount = Object.entries(blockersByEvidenceClass)
    .filter(([evidenceClass]) => evidenceClass !== 'review-only')
    .reduce((sum, [, count]) => sum + Number(count ?? 0), 0)
  const blockerCount = Number(report?.agentGate?.blockerCount ?? 0)
  const reviewedPass =
    !directPass &&
    reviewGate?.agentGate?.passed === true &&
    reviewOnlyCount > 0 &&
    nonReviewEvidenceCount === 0 &&
    Number(reviewGate?.summary?.reviewedIssueCount ?? 0) === reviewOnlyCount &&
    Number(reviewGate?.summary?.nonReviewBlockerCount ?? 0) === 0
  requireGate(
    summary,
    'translation-vision-diff',
    report?.schemaVersion === 'pptx-vision-diff/v1' &&
      report?.status === 'success' &&
      (directPass || reviewedPass),
    {
      directPass,
      reviewedPass,
      blockerCount,
      reviewOnlyCount,
      nonReviewEvidenceCount,
      message:
        'Translation vision-diff must pass directly or only through a bound review-only multi-column exception',
    },
  )
}

function runPreview(summary, args, artifacts, slideCount) {
  const slides = Array.from({ length: slideCount }, (_, index) => index + 1)
  const cache = createPageBitmapCacheBinding({
    cacheDir: join(dirname(args.runDir), '.render-cache'),
    pptxPath: artifacts.candidate,
    dpi: 192,
    xdocBin: args.xdocBin,
  })
  const cacheBefore = snapshotPageBitmapCache(cache, slides)
  const report = runJsonPhase(summary, {
    name: 'preview-render',
    bin: args.xdocBin,
    args: [
      'pptx',
      'preview',
      artifacts.candidate,
      '--output-dir',
      artifacts.previews,
      '--contact-sheet',
      '--contact-output',
      artifacts.contactSheet,
      '--dpi',
      '192',
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.previewReport,
    env: { XDOC_PAGE_CACHE_PREFIX: cache.prefix },
  })
  verifyRenderContext(report)
  const cacheAfter = snapshotPageBitmapCache(cache, slides)
  const pages = report?.pages ?? []
  const phase = summary.phases.findLast((item) => item.name === 'preview-render')
  if (phase) {
    phase.slideCount = pages.length
    phase.estimatedRenderedPixels = pages.reduce((sum, page) => sum + previewPixels(page), 0)
    phase.pageBitmapCache = pageBitmapCacheMetrics(cache, cacheBefore, cacheAfter)
  }
  requireGate(
    summary,
    'translation-preview',
    report?.schemaVersion === 'pptx-preview/v1' &&
      report?.status === 'success' &&
      pages.length === slideCount &&
      pages.length > 0 &&
      pages.every((page) => previewBytes(page) > 0 && previewPageValid(page, args.runDir)) &&
      existsSync(artifacts.contactSheet) &&
      statSync(artifacts.contactSheet).size > 0,
    {
      pages: pages.length,
      expectedPages: slideCount,
      contactSheetBytes: existsSync(artifacts.contactSheet)
        ? statSync(artifacts.contactSheet).size
        : 0,
      message: 'Translation preview must cover every slide with non-empty PNG evidence',
    },
  )
}

function runSemanticDiff(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'pptx-semantic-diff',
    bin: args.xdocBin,
    args: [
      'pptx',
      'diff',
      '--source',
      artifacts.source,
      '--candidate',
      artifacts.candidate,
      '--detail',
      'summary',
      '--output',
      artifacts.semanticDiffFull,
      '--json',
    ],
    artifact: artifacts.semanticDiff,
  })
  verifyDiffEvidence(report, artifacts.source, artifacts.candidate)
  requireGate(summary, 'pptx-semantic-diff', report?.status === 'success', {
    status: report?.status ?? null,
    semanticStatus: report?.agentGate?.semanticStatus ?? null,
    message: 'Translation semantic diff must emit successful evidence',
  })
}

function runCompare(summary, args, artifacts, slideCount) {
  const report = runJsonPhase(summary, {
    name: 'translation-compare',
    bin: process.execPath,
    args: [
      COMPARE_SCRIPT,
      '--source',
      artifacts.source,
      '--candidate',
      artifacts.candidate,
      '--run-dir',
      args.runDir,
      '--kind',
      'translation',
      '--output',
      artifacts.compare,
      '--report',
      artifacts.compareReport,
      '--slide-count',
      String(slideCount),
      '--compare-chunk-size',
      String(args.compareChunkSize),
      '--compare-concurrency',
      String(args.compareConcurrency),
      '--dpi',
      '192',
      '--fallback-dpi',
      '144',
      '--xdoc-bin',
      args.xdocBin,
      '--progress',
      progressReporter.forwardFd !== null ? 'jsonl' : args.progress,
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.compareReport,
    forwardProgress: true,
  })
  let metrics
  try {
    metrics = analyzeCompareRendering(report)
  } catch (error) {
    throw new PhaseFailure('translation-compare-artifact', error.message, {
      kind: error.name,
    })
  }
  const phase = summary.phases.findLast((item) => item.name === 'translation-compare')
  if (phase) Object.assign(phase, metrics)
  requireGate(
    summary,
    'translation-compare-artifact',
    report?.status === 'success' && report?.agentGate?.passed === true,
    {
      partCount: metrics.partCount,
      renderInvocations: metrics.renderInvocations,
      message: 'The full translation comparison must cover every slide',
    },
  )
  return report
}

function materializeContactDiff(summary, args, artifacts, compareReport) {
  if (!args.contactDiff) return
  let materialized
  try {
    materialized = materializeCompareAliases({
      compareReport,
      compareReportPath: artifacts.compareReport,
      compareOutputPath: artifacts.compare,
      aliasOutputPath: artifacts.contactDiff,
      aliasReportPath: artifacts.contactDiffReport,
      aliasKind: 'contact',
      sourceKind: 'translation',
    })
  } catch (error) {
    throw new PhaseFailure('contact-diff-artifact', error.message, { kind: error.name })
  }
  summary.artifacts.contactDiffParts = materialized.partPaths
  summary.review.contactDiffReuse = materialized.report.reuse
  requireGate(summary, 'contact-diff-artifact', materialized.report?.status === 'success', {
    partCount: materialized.partCount,
    renderInvocationsSaved: materialized.renderInvocationsSaved,
    message: 'Requested contact-diff aliases were not materialized from translation evidence',
  })
  addInternalPhase(summary, 'contact-diff-reuse', 'passed', {
    artifact: relativeArtifact(args.runDir, artifacts.contactDiffReport),
    partCount: materialized.partCount,
    renderInvocationsSaved: materialized.renderInvocationsSaved,
  })
}

function publish(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'translation-compare-delivery',
    bin: process.execPath,
    args: [
      COMPARE_GATE_SCRIPT,
      '--run-dir',
      args.runDir,
      '--final-pptx',
      args.output,
      '--final-pptx-source',
      artifacts.candidate,
      '--kind',
      'translation',
      '--publish',
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.compareGate,
  })
  const siblings = report?.agentSummary?.siblingPaths ?? []
  summary.artifacts.compareParts = siblings.length > 1 ? siblings : []
  requireGate(
    summary,
    'translation-compare-delivery',
    report?.status === 'pass' &&
      report?.finalBinding?.status === 'bound' &&
      report?.finalBinding?.publishedFinal?.path === args.output &&
      existsSync(args.output) &&
      sha256(args.output) === report?.finalBinding?.publishedFinal?.sha256,
    {
      status: report?.status ?? null,
      siblingPaths: siblings,
      finalSha256: report?.finalBinding?.publishedFinal?.sha256 ?? null,
      message: 'Translation output and complete compare evidence must be hash-bound before publish',
    },
  )
}

function buildPerformanceSummary(summary, totalMs) {
  const preview = summary.phases.find((phase) => phase.name === 'preview-render')
  const compare = summary.phases.find((phase) => phase.name === 'translation-compare')
  const partCount = Number(compare?.partCount ?? 0)
  const invocations = Number(compare?.renderInvocations ?? 0)
  const retryInvocations = Number(compare?.retryInvocations ?? Math.max(0, invocations - partCount))
  const estimatedPixels =
    Number(preview?.estimatedRenderedPixels ?? 0) + Number(compare?.estimatedRenderedPixels ?? 0)
  const baselinePixels =
    Number(preview?.estimatedRenderedPixels ?? 0) + Number(compare?.baselineEstimatedPixels ?? 0)
  const saved = Number(summary.review?.contactDiffReuse?.renderInvocationsSaved ?? 0)
  const cacheHits = Number(compare?.cacheHitCount ?? 0)
  const cacheSaved = Number(compare?.renderInvocationsSaved ?? cacheHits)
  return buildRuntimePerformanceSummary(summary, totalMs, {
    renderPhaseNames: ['preview-render', 'translation-compare'],
    render: {
      previewRenderInvocations: preview ? 1 : 0,
      comparePartCount: partCount,
      compareRenderInvocations: invocations,
      compareRetryInvocations: retryInvocations,
      compareCacheHitCount: cacheHits,
      compareCacheRenderInvocationsSaved: cacheSaved,
      previewPageBitmapCache: preview?.pageBitmapCache ?? null,
      comparePageBitmapCache: compare?.pageBitmapCache ?? null,
      estimatedRenderedPixels: estimatedPixels,
      renderInvocationsSaved: saved + cacheSaved,
      contactAliasRenderInvocationsSaved: saved,
      contactDiffRequested: Boolean(summary.review?.contactDiffRequested),
      contactDiffReused: summary.review?.contactDiffReuse?.status === 'reused',
    },
    budget: {
      baselineInvocations: (preview ? 1 : 0) + partCount,
      actualInvocations: (preview ? 1 : 0) + invocations,
      maximumRetryInvocations: partCount,
      maximumTotalInvocations: (preview ? 1 : 0) + partCount * 2,
      withinBaseline: retryInvocations === 0,
      withinRetryBudget: retryInvocations <= partCount,
      baselineEstimatedPixels: baselinePixels,
      actualEstimatedPixels: estimatedPixels,
      withinPixelBaseline: estimatedPixels <= baselinePixels,
      maximumRetryEstimatedPixels: Math.round(
        Number(preview?.estimatedRenderedPixels ?? 0) +
          Number(compare?.baselineEstimatedPixels ?? 0) * 1.5625,
      ),
      withinPixelRetryBudget:
        estimatedPixels <=
        Math.round(
          Number(preview?.estimatedRenderedPixels ?? 0) +
            Number(compare?.baselineEstimatedPixels ?? 0) * 1.5625,
        ),
    },
  })
}

function buildAgentSummary(summary) {
  const style = gateByName(summary, 'i18n-style-diff')
  const consistency = gateByName(summary, 'i18n-candidate-consistency')
  const vision = gateByName(summary, 'translation-vision-diff')
  const preview = gateByName(summary, 'translation-preview')
  const semantic = gateByName(summary, 'pptx-semantic-diff')
  const compare = gateByName(summary, 'translation-compare-delivery')
  return {
    schemaVersion: AGENT_SUMMARY_SCHEMA_VERSION,
    mode: 'translation',
    status: summary.status,
    machineGatesPassed: Boolean(summary.machineGatesPassed),
    deliveryReady: Boolean(summary.deliveryReady),
    needsHumanReview: true,
    decision: summary.machineGatesPassed ? 'continue-to-human-review' : 'stop-and-fix',
    gates: {
      style: { gate: gateStatus(style), blockers: style?.blockerCount ?? null },
      consistency: {
        gate: gateStatus(consistency),
        blockers: consistency?.blockerCount ?? null,
        verified: consistency?.verifiedCount ?? null,
      },
      vision: {
        gate: gateStatus(vision),
        directPass: vision?.directPass ?? null,
        reviewedPass: vision?.reviewedPass ?? null,
        blockers: vision?.blockerCount ?? null,
      },
      preview: {
        gate: gateStatus(preview),
        pages: preview?.pages ?? null,
        expectedPages: preview?.expectedPages ?? null,
      },
      semanticDiff: {
        gate: gateStatus(semantic),
        semanticStatus: semantic?.semanticStatus ?? null,
      },
      compare: {
        gate: gateStatus(compare),
        partCount: compare?.siblingPaths?.length || null,
      },
    },
    artifacts: {
      summary: summary.artifacts.summary,
      styleDiff: summary.artifacts.styleDiff,
      candidateScan: summary.artifacts.candidateScan,
      visionDiff: summary.artifacts.visionDiff,
      previewReport: summary.artifacts.previewReport,
      contactSheet: summary.artifacts.contactSheet,
      semanticDiff: summary.artifacts.semanticDiff,
      compare: summary.artifacts.compare,
      compareParts: summary.artifacts.compareParts,
      compareGate: summary.artifacts.compareGate,
      contactDiffParts: summary.artifacts.contactDiffParts,
    },
    warnings: summary.warnings,
    error: summary.error,
  }
}

function failureReferences(error) {
  const routes = {
    'i18n-style-diff': {
      path: 'references/translation/translation-mode.md',
      section: 'Style Signature Gate',
      reason: 'The stable candidate changed translation-protected style signatures.',
    },
    'i18n-candidate-consistency-contract': {
      path: 'references/translation/translation-runner.md',
      section: 'Failure routing',
      reason:
        'The installed xdoc emitted an i18n-scan schema this runner does not recognize; align the skill and xdoc versions instead of debugging translations.',
    },
    'i18n-candidate-consistency': {
      path: 'references/translation/translation-mode.md',
      section: 'I18n Plan Gate',
      reason: 'One or more planned translation units do not resolve to the expected target text.',
    },
    'multi-column-review-input': {
      path: 'references/translation/translation-mode.md',
      section: 'Visual Parity Gate',
      reason: 'The supplied multi-column review evidence is incomplete or stale.',
    },
    'multi-column-review-revalidate': {
      path: 'references/translation/translation-mode.md',
      section: 'Visual Parity Gate',
      reason: 'The multi-column review evidence no longer passes its fail-closed gate.',
    },
    'multi-column-review-binding': {
      path: 'references/translation/translation-mode.md',
      section: 'Visual Parity Gate',
      reason: 'The reviewed findings do not bind the current candidate and final vision evidence.',
    },
    'translation-vision-diff': {
      path: 'references/translation/translation-mode.md',
      section: 'Visual Parity Gate',
      reason: 'Vision blockers require translation repair or a bound multi-column review.',
    },
    'translation-preview': {
      path: 'references/translation/translation-runner.md',
      section: 'Visual evidence and performance',
      reason: 'The candidate preview did not produce complete verified slide evidence.',
    },
    'preview-render': {
      path: 'references/translation/translation-runner.md',
      section: 'Visual evidence and performance',
      reason: 'The candidate preview command failed before complete slide evidence was produced.',
    },
    'pptx-semantic-diff': {
      path: 'references/translation/translation-runner.md',
      section: 'Failure routing',
      reason: 'The final semantic evidence command failed and must be diagnosed before comparison.',
    },
    'translation-compare-artifact': {
      path: 'references/translation/translation-runner.md',
      section: 'Visual evidence and performance',
      reason: 'The full translation comparison is incomplete or invalid.',
    },
    'translation-compare': {
      path: 'references/translation/translation-runner.md',
      section: 'Visual evidence and performance',
      reason: 'The full translation comparison command failed and requires evidence diagnosis.',
    },
    'contact-diff-artifact': {
      path: 'references/translation/translation-runner.md',
      section: 'Visual evidence and performance',
      reason: 'The requested compatibility aliases could not be verified from compare evidence.',
    },
    'translation-compare-delivery': {
      path: 'references/translation/translation-runner.md',
      section: 'Delivery boundary',
      reason: 'The final PPTX and comparison evidence were not hash-bound for publication.',
    },
  }
  const route = routes[error?.phase]
  return route ? [route] : []
}

function attachProgressArchive(args, artifacts) {
  const target = args.progressFile === 'none' ? '' : args.progressFile || artifacts.progressLog
  if (!target) return
  progressReporter.attachFile?.(target)
}

function archivePrompt(summary, args, artifacts) {
  if (args.promptFile && !existsSync(args.promptFile)) {
    throw new Error(`--prompt-file does not exist: ${args.promptFile}`)
  }
  const text = args.promptFile ? readFileSync(args.promptFile, 'utf8') : args.promptText
  if (!text) return
  const promptStarted = performance.now()
  writeFileSync(artifacts.prompt, text.endsWith('\n') ? text : `${text}\n`)
  addInternalPhase(summary, 'prompt-archive', 'passed', {
    artifact: relativeArtifact(args.runDir, artifacts.prompt),
    durationMs: durationMs(promptStarted),
    bytes: statSync(artifacts.prompt).size,
    source: args.promptFile ? 'file' : 'text',
  })
}

function runTranslation(input) {
  const started = performance.now()
  const args = normalizeArgs(input)
  const typedTextAttrs = validatePaths(args)
  mkdirSync(args.runDir, { recursive: true })
  ensureRenderContext(args.runDir)
  const artifacts = artifactPaths(args.runDir)
  const summary = initialSummary(args, artifacts)
  attachProgressArchive(args, artifacts)
  try {
    addInternalPhase(summary, 'typed-text-attribute-preflight', 'passed', {
      unitsContractComplete: typedTextAttrs.complete,
      required: typedTextAttrs.required.map((entry) => ({
        attrName: entry.attrName,
        unitCount: entry.unitCount,
      })),
      allowed: typedTextAttrs.allowed,
    })
    archivePrompt(summary, args, artifacts)
    copyFileSync(args.source, artifacts.source)
    copyFileSync(args.candidate, artifacts.candidate)
    copyFileSync(args.units, artifacts.units)
    copyFileSync(args.translations, artifacts.translations)
    addInternalPhase(summary, 'input-snapshot', 'passed', {
      sourceSha256: sha256(artifacts.source),
      candidateSha256: sha256(artifacts.candidate),
    })
    const inspect = runInspect(summary, args, artifacts)
    const slideCount = expectedSlideCount(inspect)
    requireGate(summary, 'source-slide-count', slideCount > 0, {
      slideCount,
      message: 'Source inspect must disclose a positive slide count',
    })
    runStyleDiff(summary, args, artifacts)
    runCandidateConsistency(summary, args, artifacts)
    runVisionDiff(summary, args, artifacts)
    runPreview(summary, args, artifacts, slideCount)
    runSemanticDiff(summary, args, artifacts)
    const compareReport = runCompare(summary, args, artifacts, slideCount)
    materializeContactDiff(summary, args, artifacts, compareReport)
    publish(summary, args, artifacts)

    summary.status = 'needs-human-review'
    summary.machineGatesPassed = true
    return finalizeRunnerSummary(summary, {
      summaryPath: artifacts.summary,
      totalMs: durationMs(started),
      finalizeArtifacts,
      buildPerformance: buildPerformanceSummary,
      buildAgentSummary,
    })
  } catch (error) {
    summary.status = 'failed'
    summary.error = summarizePhaseError(error)
    summary.requiredReferences = failureReferences(error)
    finalizeRunnerSummary(summary, {
      summaryPath: artifacts.summary,
      totalMs: durationMs(started),
      finalizeArtifacts,
      buildPerformance: buildPerformanceSummary,
      buildAgentSummary,
    })
    error.summary = summary
    throw error
  } finally {
    progressReporter.detachFile?.()
  }
}

function printHuman(summary) {
  process.stdout.write(`PPTX translation finalization: ${summary.status}\n`)
  process.stdout.write(`- run dir: ${summary.runDir}\n`)
  process.stdout.write(`- output: ${summary.output}\n`)
  process.stdout.write(`- machine gates: ${summary.machineGatesPassed ? 'passed' : 'failed'}\n`)
  process.stdout.write('- manual review: required\n')
  if (summary.error)
    process.stdout.write(`- error: ${summary.error.phase}: ${summary.error.message}\n`)
}

let parsedArgs = null
try {
  parsedArgs = parseArgs(process.argv.slice(2))
  progressReporter = createProgressReporter({
    mode: parsedArgs.progress,
    jsonOutput: parsedArgs.json,
    context: { tool: 'cli/translation/run' },
  })
  const summary = runTranslation(parsedArgs)
  if (parsedArgs.json) {
    const output = parsedArgs.jsonFull
      ? summary
      : buildRuntimeAgentResult(summary, { schemaVersion: AGENT_RESULT_SCHEMA_VERSION })
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  } else printHuman(summary)
} catch (error) {
  const summary = error.summary ?? {
    schemaVersion: 'pptx-nova-translation-run/v1',
    mode: 'translation',
    status: 'failed',
    error: {
      phase: error.phase ?? 'preflight',
      kind: error.kind ?? error.name ?? 'Error',
      message: error.message,
      exitCode: error.exitCode ?? null,
    },
  }
  if (parsedArgs?.json) {
    const output = parsedArgs.jsonFull
      ? summary
      : buildRuntimeAgentResult(summary, { schemaVersion: AGENT_RESULT_SCHEMA_VERSION })
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  } else if (summary.runDir) printHuman(summary)
  else process.stderr.write(`[error] ${summary.error.phase}: ${summary.error.message}\n`)
  process.exitCode = 1
}
