#!/usr/bin/env node
import { cliPath, SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { ensureRenderContext, verifyRenderContext } from '../../lib/review/render-context.mjs'
import { verifyDiffEvidence } from '../../lib/review/diff-evidence.mjs'
import { createHash } from 'node:crypto'
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { basename, dirname, extname, join, resolve } from 'node:path'
import { performance } from 'node:perf_hooks'
import { fileURLToPath } from 'node:url'
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
import { annotateTopActionable, evaluateFindings } from '../../lib/review/finding-analysis.mjs'
import { buildLayoutSnapshot, layoutSemanticSha256 } from '../../lib/review/layout-snapshot.mjs'
import { assertNewOrPreProbedRunDir } from '../../lib/runtime/run-dir.mjs'
import {
  createPageBitmapCacheBinding,
  pageBitmapCacheMetrics,
  snapshotPageBitmapCache,
} from '../../lib/review/page-bitmap-cache.mjs'
import { createProgressReporter } from '../../lib/runtime/progress.mjs'
import { buildRefurbishPlan } from './plan.mjs'
import { evaluateReviewPolicy, hasEmbeddedReviewedFindings } from '../../lib/review/policy.mjs'

const CATALOG_PATH = join(SKILL_ROOT, 'assets/deckkits/catalog.json')
const READINESS_SCRIPT = cliPath('deckkits/readiness.mjs')
const FALLBACK_PATCH_SCRIPT = cliPath('refurbish/fallback-patch.mjs')
const CHECK_LOCK_SCRIPT = cliPath('create/check-lock.mjs')
const CAPABILITY_PROBE_SCRIPT = cliPath('runtime/probe.mjs')
const FIDELITY_GATE_SCRIPT = cliPath('review/fidelity-gate.mjs')
const COMPARE_SCRIPT = cliPath('review/compare.mjs')
const COMPARE_GATE_SCRIPT = cliPath('review/compare-gate.mjs')
const VISUAL_REVIEW_SCRIPT = cliPath('review/visual-review.mjs')
const FEEDBACK_GATE_SCRIPT = cliPath('review/feedback-gate.mjs')
const REFURBISH_RUN_SCRIPT = fileURLToPath(import.meta.url)
const AGENT_SUMMARY_SCHEMA_VERSION = 'pptx-nova-agent-summary/v1'
const AGENT_RESULT_SCHEMA_VERSION = 'pptx-nova-refurbish-result/v1'
let progressReporter = createProgressReporter({ mode: 'off' })
const { runJsonPhase, runPlainPhase, addInternalPhase, requireGate } = createRunnerRuntime({
  getProgressReporter: () => progressReporter,
})

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function readJson(path, label) {
  if (!path || !existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`Failed to read ${label} at ${path}: ${error.message}`)
  }
}

const usage = `Usage:
  node <skill-root>/scripts/cli/refurbish/run.mjs --deckkit <id> --source <source.pptx> --output <output.pptx> [options]

Options:
  --deckkit <id>          Target DeckKit id
  --source <path>         Read-only source PPTX
  --output <path>         Final PPTX published only after machine gates pass
  --run-dir <path>        New, empty, or pre-probed run directory. Defaults to <cwd>/.pptx-nova/refurbish-<deckkit>-<timestamp>
  --catalog <path>        DeckKit catalog. Defaults to <skill-root>/assets/deckkits/catalog.json
  --route <route>         auto|native|fallback. Defaults to auto
  --xdoc-bin <path>       xdoc executable. Defaults to xdoc
  --readiness-out <path>  Optional benchmark output for a full delivery readiness audit
  --review-policy <path>  Optional hash-bound pptx-nova-review-policy/v1 document
  --explicit              User explicitly named a non-production/default DeckKit
  --contact-diff          Materialize contact-diff aliases from the final refurbish comparison
  --compare-chunk-size <n>
                          Maximum slides per compare PNG. Defaults to 20.
  --compare-concurrency <n>
                          Concurrent compare part renders. Defaults to 3.
  --overwrite             Allow replacing an existing final output after all machine gates pass
  --progress <mode>       Progress stream: auto|jsonl|text|off. Defaults to auto.
  --progress-file <path>  Progress JSONL archive. Defaults to <run-dir>/progress.jsonl; pass
                          "none" to disable. While active, stderr only carries single-line
                          phase-boundary summaries.
  --prompt-text <text>    Original user prompt; archived to <run-dir>/prompt.txt for the
                          feedback gate.
  --prompt-file <path>    Read the original user prompt from a file instead of --prompt-text.
  --json                  Print the compact Agent result; the full summary is always saved in the run directory
  --json-full             Print the complete run summary for debugging
  --help                  Show this help

The runner never marks manual PNG/contact review complete. A successful run exits 0 with
status "needs-human-review", publishes the machine-validated candidate, and records all
artifacts in the run directory.
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    source: '',
    output: '',
    runDir: '',
    catalog: CATALOG_PATH,
    route: 'auto',
    xdocBin: 'xdoc',
    readinessOut: '',
    reviewPolicy: '',
    explicit: false,
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

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--explicit') {
      args.explicit = true
    } else if (arg === '--contact-diff') {
      args.contactDiff = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--json-full') {
      args.json = true
      args.jsonFull = true
    } else if (arg in valueFlags) {
      const key = valueFlags[arg]
      const value = valueAfter(argv, i, arg)
      args[key] = ['compareChunkSize', 'compareConcurrency'].includes(key) ? Number(value) : value
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.deckkit) throw new Error(`--deckkit is required.\n\n${usage}`)
  if (!args.source) throw new Error(`--source is required.\n\n${usage}`)
  if (!args.output) throw new Error(`--output is required.\n\n${usage}`)
  if (!['auto', 'native', 'fallback'].includes(args.route)) {
    throw new Error('--route must be one of auto|native|fallback')
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
  '--deckkit': 'deckkit',
  '--source': 'source',
  '--output': 'output',
  '--run-dir': 'runDir',
  '--catalog': 'catalog',
  '--route': 'route',
  '--xdoc-bin': 'xdocBin',
  '--readiness-out': 'readinessOut',
  '--review-policy': 'reviewPolicy',
  '--compare-chunk-size': 'compareChunkSize',
  '--compare-concurrency': 'compareConcurrency',
  '--progress': 'progress',
  '--progress-file': 'progressFile',
  '--prompt-text': 'promptText',
  '--prompt-file': 'promptFile',
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
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

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function commandArg(value) {
  return JSON.stringify(String(value))
}

function countBy(items, keyFor) {
  const counts = {}
  for (const item of items) {
    const key = String(keyFor(item) || 'unknown')
    counts[key] = (counts[key] ?? 0) + 1
  }
  return counts
}

function summarizeOpResults(report) {
  const opResults = Array.isArray(report?.opResults) ? report.opResults : []
  return {
    reportedOps: opResults.length,
    byStatus: countBy(opResults, (item) => item?.status),
    byOp: countBy(opResults, (item) => item?.op),
    changedPartCount: new Set(
      opResults.flatMap((item) => (Array.isArray(item?.changedParts) ? item.changedParts : [])),
    ).size,
  }
}

function walkFiles(root) {
  const files = []
  if (!root || !existsSync(root)) return files
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name)
    if (entry.isDirectory()) files.push(...walkFiles(path))
    else if (entry.isFile()) files.push(path)
  }
  return files
}

function artifactRole(path) {
  const extension = extname(path).toLowerCase()
  if (extension === '.pptx') return 'pptx'
  if (extension === '.json') return 'json'
  if (extension === '.jsonl' || extension === '.log') return 'logs'
  if (['.png', '.jpg', '.jpeg', '.webp'].includes(extension)) return 'images'
  if (['.txt', '.md'].includes(extension)) return 'text'
  return 'other'
}

function aggregateGuidanceFor(path) {
  const name = basename(path)
  if (['dry-run.json', 'apply.json'].includes(name)) {
    return [
      'schemaVersion',
      'status',
      'semanticIssues | length',
      'opResults grouped by op and status',
      'changedParts | length',
    ]
  }
  if (name.includes('inspect')) {
    return ['presentation.slideCount', 'presentation.themes', 'slides[].semantic']
  }
  if (name.startsWith('layout-')) {
    return ['status', 'summary', 'risks grouped by code and classification']
  }
  if (name === 'finding-analysis.json') {
    return ['evaluation.status', 'summary', 'agentGate', 'summary.topFindings']
  }
  if (name === 'pptx-diff.json') {
    return ['agentGate', 'summary', 'changeRollup.reliable']
  }
  return ['top-level status and summary fields']
}

function collectArtifactContextEvidence(runDir) {
  const files = walkFiles(runDir)
  const byRole = {}
  for (const path of files) {
    const role = artifactRole(path)
    const current = byRole[role] ?? { files: 0, bytes: 0 }
    current.files += 1
    current.bytes += statSync(path).size
    byRole[role] = current
  }
  const largeJsonArtifacts = files
    .filter((path) => extname(path).toLowerCase() === '.json')
    .map((path) => ({
      path: relativeArtifact(runDir, path),
      bytes: statSync(path).size,
      readInstead: aggregateGuidanceFor(path),
    }))
    .filter((item) => item.bytes >= 128 * 1024)
    .sort((left, right) => right.bytes - left.bytes)
  return {
    artifactBytesByRole: byRole,
    agentContextRisk: {
      level: largeJsonArtifacts.length > 0 ? 'high' : 'low',
      largeJsonArtifacts,
      guidance: [
        'Read agentSummary and operationAudit before opening full JSON artifacts.',
        'Project large JSON with jq and group opResults; do not expand full opResults arrays into Agent context.',
        'Token usage must come from platform telemetry; this runner does not estimate it.',
      ],
    },
  }
}

function artifactSet(summary, keys) {
  return Object.fromEntries(keys.map((key) => [key, summary.artifacts?.[key] ?? null]))
}

function buildAgentLayoutSummary(layout) {
  if (!layout) return null
  return {
    status: layout.status ?? null,
    riskCount: layout.riskCount ?? 0,
    actionableRiskCount: layout.actionableRiskCount ?? 0,
    informationalRiskCount: layout.informationalRiskCount ?? 0,
    actionableSlideCount: layout.actionableSlideCount ?? 0,
    actionableSlideNumbers: layout.actionableSlideNumbers ?? [],
    actionablePreviewFiles: layout.actionablePreviewFiles ?? [],
    topActionable: layout.topActionable ?? [],
    reviewedRiskCount: layout.reviewedRiskCount ?? 0,
    reviewPolicyStatus: layout.reviewPolicyStatus ?? null,
  }
}

function classifyNativeContrastRecovery(report) {
  const visionDiff = report?.reports?.visionDiff
  const audit = report?.reports?.audit
  const newCounts = visionCounts(visionDiff, 'new')
  const worsenedCounts = visionCounts(visionDiff, 'worsened')
  const newIssues = Array.isArray(visionDiff?.newIssues) ? visionDiff.newIssues : []
  const blockingNewIssues = newIssues.filter((issue) =>
    ['high', 'medium'].includes(String(issue?.severity ?? '').toLowerCase()),
  )
  const mediumIssues = blockingNewIssues.filter(
    (issue) => String(issue?.severity ?? '').toLowerCase() === 'medium',
  )
  const highIssues = blockingNewIssues.filter(
    (issue) => String(issue?.severity ?? '').toLowerCase() === 'high',
  )
  const remapTheme = (Array.isArray(report?.steps) ? report.steps : []).find(
    (step) => step?.name === 'remap-theme',
  )
  const checks = {
    reportSchema:
      report?.schemaVersion === 'pptx-refurbish-skin/v1' && report?.outcome === 'failed',
    auditPassed:
      audit?.schemaVersion === 'pptx-refurbish-audit/v1' &&
      audit?.outcome === 'passed' &&
      Number(audit?.summary?.errorCount ?? 0) === 0 &&
      report?.gate?.auditStatus === 'passed',
    visionDiffValid:
      visionDiff?.schemaVersion === 'pptx-vision-diff/v1' && visionDiff?.status === 'success',
    gateCountsMatch:
      Number(report?.gate?.newHighIssues ?? -1) === newCounts.high &&
      Number(report?.gate?.newMediumIssues ?? -1) === newCounts.medium &&
      highIssues.length === newCounts.high &&
      mediumIssues.length === newCounts.medium,
    noNewHigh: newCounts.high === 0,
    contrastOnlyNewMedium:
      newCounts.medium > 0 && mediumIssues.every((issue) => issue?.kind === 'low-contrast-text'),
    noWorsenedBlockers: worsenedCounts.high === 0 && worsenedCounts.medium === 0,
    remapThemeSucceeded: remapTheme?.status === 'success',
  }
  const eligible = Object.values(checks).every(Boolean)
  return {
    schemaVersion: 'pptx-nova-native-recovery/v1',
    eligible,
    reasonCode: eligible ? 'native-theme-contrast-only' : 'native-failure-not-fallback-eligible',
    checks,
    findings: {
      blockingNew: blockingNewIssues.length,
      newHigh: newCounts.high,
      newMedium: newCounts.medium,
      worsenedHigh: worsenedCounts.high,
      worsenedMedium: worsenedCounts.medium,
      byKind: countBy(blockingNewIssues, (issue) => issue?.kind),
      affectedSlides: [
        ...new Set(
          blockingNewIssues
            .map((issue) => Number(issue?.slideIndex))
            .filter((value) => Number.isInteger(value) && value >= 0)
            .map((value) => value + 1),
        ),
      ].sort((left, right) => left - right),
    },
  }
}

function visualReviewCommand(summary) {
  const contactSheet = summary.artifacts?.contactSheet
  const previews = summary.artifacts?.previews
  if (!contactSheet || !previews || !existsSync(contactSheet) || !existsSync(previews)) return null
  const preview = gateByName(summary, 'png-previews')
  const slideCount = Number(preview?.expectedCount ?? preview?.count ?? 0)
  const args = [
    process.execPath,
    VISUAL_REVIEW_SCRIPT,
    '--run-dir',
    summary.runDir,
    '--mode',
    'refurbish',
    '--reviewer',
    'agent',
    '--slides-reviewed',
    slideCount > 0 ? String(slideCount) : '<slide-count>',
    '--contact-sheet',
    contactSheet,
    '--previews',
    previews,
  ]
  if (summary.artifacts?.visionDiff) args.push('--vision', summary.artifacts.visionDiff)
  if (summary.artifacts?.layoutFinal) args.push('--layout-final', summary.artifacts.layoutFinal)
  if (summary.artifacts?.contentAuditFinal) {
    args.push('--semantic-audit', summary.artifacts.contentAuditFinal)
  }
  for (const check of [
    'titleWrap',
    'bodyReadability',
    'alignment',
    'spacing',
    'contrast',
    'chartTableLegibility',
    'repeatedLayoutRhythm',
    'placeholderResidue',
    'footerPageChrome',
    'assetFit',
    'targetDeckkitApplied',
  ]) {
    args.push('--check', `${check}=pass`)
  }
  args.push('--json')
  return args.map(commandArg).join(' ')
}

function recoveryCommand(summary) {
  if (!summary.error || !summary.runDir) return null
  const selectedRoute =
    summary.route?.planned === 'fallback-patch' || summary.route?.executed === 'fallback-patch'
      ? 'fallback'
      : summary.route?.requested || 'auto'
  return [
    process.execPath,
    REFURBISH_RUN_SCRIPT,
    '--deckkit',
    summary.deckkit,
    '--source',
    summary.source,
    '--output',
    summary.output,
    '--run-dir',
    '<new-empty-run-dir>',
    '--route',
    selectedRoute,
    '--json',
  ]
    .map(commandArg)
    .join(' ')
}

function feedbackGateCommand(summary) {
  const prompt = summary.artifacts?.prompt
  if (!prompt || !existsSync(prompt)) return null
  return [
    process.execPath,
    FEEDBACK_GATE_SCRIPT,
    '--run-dir',
    summary.runDir,
    '--prompt-file',
    prompt,
    '--workflow',
    'refurbish',
    '--strict',
    '--overwrite',
    '--json',
    '>',
    join(summary.runDir, 'feedback-gate.json'),
  ]
    .map((value) => (value === '>' ? value : commandArg(value)))
    .join(' ')
}

function buildAgentSummary(summary) {
  const visionDiff = gateByName(summary, 'vision-diff')
  const audit = gateByName(summary, 'refurbish-audit')
  const fidelity = gateByName(summary, 'fidelity-gate')
  const semanticDiff = gateByName(summary, 'pptx-semantic-diff')
  const preview = gateByName(summary, 'png-previews')
  const compare = gateByName(summary, 'refurbish-compare-delivery')
  const route = summary.route?.executed || summary.route?.planned || summary.route?.requested || ''
  const decision = summary.machineGatesPassed
    ? summary.needsHumanReview
      ? 'continue-to-human-review'
      : 'deliver'
    : 'stop-and-fix'
  const focusedSlides = summary.layout?.actionableSlideNumbers ?? []
  const focusedSelector = focusedSlides.join(',')

  return {
    schemaVersion: AGENT_SUMMARY_SCHEMA_VERSION,
    mode: 'refurbish',
    status: summary.status,
    machineGatesPassed: Boolean(summary.machineGatesPassed),
    deliveryReady: Boolean(summary.deliveryReady),
    needsHumanReview: Boolean(summary.needsHumanReview),
    decision,
    deckkit: summary.deckkit,
    route,
    routeDecision: summary.route,
    requiredReferences: summary.requiredReferences ?? [],
    recovery: summary.recovery,
    operationAudit: summary.operationAudit,
    agentContextRisk: summary.agentContextRisk ?? null,
    layout: buildAgentLayoutSummary(summary.layout),
    findingAnalysis: summary.findingAnalysis
      ? {
          status: summary.findingAnalysis.status,
          proposedStatus: summary.findingAnalysis.proposedStatus,
          effectiveStatus: summary.findingAnalysis.effectiveStatus,
          findingCount: summary.findingAnalysis.findingCount,
          unresolvedFindingCount: summary.findingAnalysis.unresolvedFindingCount,
          resolvedFindingCount: summary.findingAnalysis.resolvedFindingCount,
          nextAction: summary.findingAnalysis.nextAction,
          topFindings: summary.findingAnalysis.topFindings,
        }
      : null,
    slides: {
      source: fidelity?.sourceSlides ?? null,
      final: fidelity?.finalSlides ?? null,
      mapped: fidelity?.mappedSlides ?? null,
    },
    gates: {
      visionDiff: {
        status: visionDiff?.status ?? null,
        gate: gateStatus(visionDiff),
        newHigh: visionDiff?.new?.high ?? null,
        newMedium: visionDiff?.new?.medium ?? null,
        changedHigh: visionDiff?.changed?.high ?? null,
      },
      refurbishAudit: {
        status: audit?.status ?? null,
        gate: gateStatus(audit),
        errors: audit?.errorCount ?? null,
        warnings: audit?.warningCount ?? null,
      },
      fidelityGate: {
        status: fidelity?.status ?? null,
        gate: gateStatus(fidelity),
        errors: fidelity?.errors ?? null,
        warnings: fidelity?.warnings ?? null,
        declaredReviews: fidelity?.declaredReviews ?? null,
        appliedReviews: fidelity?.appliedReviews ?? null,
        reviewedFindings: fidelity?.reviewedFindings ?? null,
        remainingActionableFindings: fidelity?.remainingActionableFindings ?? null,
      },
      semanticDiff: {
        status: semanticDiff?.status ?? null,
        gate: gateStatus(semanticDiff),
        semanticStatus: semanticDiff?.semanticStatus ?? null,
        reliableChanges: semanticDiff?.reliableChanges ?? null,
        uncertainChanges: semanticDiff?.uncertainChanges ?? null,
        unsupportedRegions: semanticDiff?.unsupportedRegions ?? null,
      },
      preview: {
        gate: gateStatus(preview),
        mode: preview?.mode ?? null,
        pages: preview?.count ?? null,
        expectedPages: preview?.expectedCount ?? null,
        contactSheetBytes: preview?.contactSheetBytes ?? null,
      },
      compare: {
        gate: gateStatus(compare),
        partCount: compare?.partCount ?? null,
      },
    },
    artifacts: artifactSet(summary, [
      'summary',
      'plan',
      'capabilities',
      'nativeReport',
      'fallbackReport',
      'patch',
      'dryRun',
      'apply',
      'visionDiff',
      'contentAuditFinal',
      'fidelityGate',
      'pptxDiff',
      'contactSheet',
      'contactDiffParts',
      'refurbishCompare',
      'refurbishCompareParts',
      'refurbishAgentReviewParts',
      'refurbishCompareGate',
      'layoutSource',
      'layoutFinal',
      'reviewPolicyEvaluation',
      'findingAnalysis',
    ]),
    nextSteps: {
      cwd: summary.runDir,
      overview:
        'Open artifacts.refurbishAgentReviewParts for the full-deck Agent overview; retain the published high-DPI compare parts as delivery evidence.',
      focusedReviewCommand:
        focusedSlides.length > 0
          ? `node ${COMPARE_SCRIPT} --source source.pptx --candidate candidate.pptx --run-dir . --kind refurbish --slides ${focusedSelector} --output focused-review.png --report focused-review.json --overwrite --json`
          : null,
      visualReviewCommand: visualReviewCommand(summary),
      feedbackGateCommand: feedbackGateCommand(summary),
      recoveryCommand: recoveryCommand(summary),
      recoveryRules: summary.error
        ? [
            `Keep ${summary.runDir} read-only as failure evidence.`,
            'Retry only with a new, empty --run-dir; never reuse the failed run directory.',
          ]
        : [],
      focusedSlides,
    },
    warnings: summary.warnings,
    error: summary.error
      ? {
          phase: summary.error.phase,
          message: summary.error.message,
          kind: summary.error.kind ?? null,
        }
      : null,
  }
}

function buildPerformanceSummary(summary, totalMs) {
  const contextEvidence = collectArtifactContextEvidence(summary.runDir)
  summary.agentContextRisk = contextEvidence.agentContextRisk
  const comparePhase = summary.phases.find((phase) => phase.name === 'refurbish-compare')
  const compareRenderInvocations = Number(comparePhase?.renderInvocations ?? 0)
  const comparePartCount = Number(comparePhase?.partCount ?? 0)
  const compareRetryInvocations = Number(comparePhase?.retryInvocations ?? 0)
  const compareCacheHitCount = Number(comparePhase?.cacheHitCount ?? 0)
  const compareCacheRenderInvocationsSaved = Number(
    comparePhase?.renderInvocationsSaved ?? compareCacheHitCount,
  )
  const renderInvocationsSaved = Number(
    summary.review?.contactDiffReuse?.renderInvocationsSaved ?? 0,
  )
  const estimatedRenderedPixels = Number(comparePhase?.estimatedRenderedPixels ?? 0)
  const baselineEstimatedPixels = Number(comparePhase?.baselineEstimatedPixels ?? 0)
  const performanceSummary = buildRuntimePerformanceSummary(summary, totalMs, {
    renderPhaseNames: [
      'preview-render',
      'preview-render-fallback-convert',
      'contact-diff',
      'refurbish-compare',
    ],
    render: {
      compareRenderInvocations,
      comparePartCount,
      compareRetryInvocations,
      compareCacheHitCount,
      compareCacheRenderInvocationsSaved,
      previewPageBitmapCache:
        summary.phases.find((phase) =>
          ['preview-render', 'preview-render-fallback-convert'].includes(phase.name),
        )?.pageBitmapCache ?? null,
      comparePageBitmapCache: comparePhase?.pageBitmapCache ?? null,
      estimatedRenderedPixels,
      renderInvocationsSaved: renderInvocationsSaved + compareCacheRenderInvocationsSaved,
      contactAliasRenderInvocationsSaved: renderInvocationsSaved,
      contactDiffRequested: Boolean(summary.review?.contactDiffRequested),
      contactDiffReused: summary.review?.contactDiffReuse?.status === 'reused',
    },
    budget: {
      baselineInvocations: comparePartCount,
      actualInvocations: compareRenderInvocations,
      withinBaseline: compareRenderInvocations <= comparePartCount,
      maximumRetryInvocations: comparePartCount,
      maximumTotalInvocations: comparePartCount * 2,
      withinRetryBudget: compareRetryInvocations <= comparePartCount,
      baselineEstimatedPixels,
      actualEstimatedPixels: estimatedRenderedPixels,
      withinPixelBaseline: estimatedRenderedPixels <= baselineEstimatedPixels,
      maximumRetryEstimatedPixels: Math.round(baselineEstimatedPixels * 1.5625),
      withinPixelRetryBudget:
        estimatedRenderedPixels <= Math.round(baselineEstimatedPixels * 1.5625),
    },
  })
  const findingAnalysisPhase = summary.phases.find(
    (phase) => phase.name === 'finding-analysis-shadow',
  )
  return {
    ...performanceSummary,
    artifactBytesByRole: contextEvidence.artifactBytesByRole,
    findingAnalysisMs: Number(findingAnalysisPhase?.durationMs ?? 0),
    findingAnalysisObjectCount: Number(findingAnalysisPhase?.details?.objectCount ?? 0),
    findingAnalysisFindingCount: Number(findingAnalysisPhase?.details?.findingCount ?? 0),
    findingAnalysisAdditionalInspectCount: 0,
    findingAnalysisAdditionalRenderCount: 0,
  }
}

function visionCounts(report, classification) {
  const counts = report?.summary?.byClass?.[classification] ?? {}
  return {
    high: Number(counts.high ?? 0),
    medium: Number(counts.medium ?? 0),
    low: Number(counts.low ?? 0),
  }
}

function gateVisionDiff(summary, report) {
  const schemaValid = report?.schemaVersion === 'pptx-vision-diff/v1'
  const statusValid = report?.status === 'success'
  const fresh = visionCounts(report, 'new')
  const changed = visionCounts(report, 'changed')
  return requireGate(
    summary,
    'vision-diff',
    schemaValid && statusValid && fresh.high === 0 && fresh.medium === 0 && changed.high === 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      status: report?.status ?? '',
      new: fresh,
      changed,
      message:
        'vision-diff requires valid v1 output, no new high/medium issues, and no changed issue ending at high severity',
    },
  )
}

function gateAudit(summary, report) {
  return requireGate(
    summary,
    'refurbish-audit',
    report?.schemaVersion === 'pptx-refurbish-audit/v1' &&
      report?.outcome === 'passed' &&
      Number(report?.summary?.errorCount ?? 0) === 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      outcome: report?.outcome ?? '',
      errorCount: Number(report?.summary?.errorCount ?? 0),
      warningCount: Number(report?.summary?.warningCount ?? 0),
      message: 'refurbish-audit must pass with zero errors',
    },
  )
}

function gateSemanticDiff(summary, report) {
  return requireGate(
    summary,
    'pptx-semantic-diff',
    report?.schemaVersion === 'pptx-diff/v1' && report?.status === 'success',
    {
      schemaVersion: report?.schemaVersion ?? '',
      status: report?.status ?? '',
      semanticStatus: report?.agentGate?.semanticStatus ?? null,
      reliableChanges: Number(report?.summary?.reliableChanges ?? 0),
      uncertainChanges: Number(report?.summary?.uncertainChanges ?? 0),
      unsupportedRegions: Number(report?.summary?.unsupportedRegions ?? 0),
      message: 'pptx semantic diff must emit successful pptx-diff/v1 output',
    },
  )
}

function defaultRunDir(args, cwd) {
  const sourceStem = basename(args.source, extname(args.source))
  const slug = safeSlug(`${sourceStem}-${args.deckkit}`)
  return join(cwd, '.pptx-nova', `refurbish-${slug}-${timestamp()}`)
}

function normalizeArgs(args) {
  const cwd = process.cwd()
  const normalized = {
    ...args,
    source: resolve(cwd, args.source),
    output: resolve(cwd, args.output),
    catalog: resolve(cwd, args.catalog),
    readinessOut: args.readinessOut ? resolve(cwd, args.readinessOut) : '',
    reviewPolicy: args.reviewPolicy ? resolve(cwd, args.reviewPolicy) : '',
  }
  normalized.runDir = args.runDir ? resolve(cwd, args.runDir) : defaultRunDir(normalized, cwd)
  return normalized
}

function validatePaths(args) {
  if (!existsSync(args.source) || !statSync(args.source).isFile()) {
    throw new Error(`source PPTX does not exist or is not a file: ${args.source}`)
  }
  if (extname(args.source).toLowerCase() !== '.pptx') {
    throw new Error(`--source must be a .pptx file: ${args.source}`)
  }
  if (extname(args.output).toLowerCase() !== '.pptx') {
    throw new Error(`--output must be a .pptx file: ${args.output}`)
  }
  if (!existsSync(args.catalog) || !statSync(args.catalog).isFile()) {
    throw new Error(`DeckKit catalog does not exist: ${args.catalog}`)
  }
  if (
    args.reviewPolicy &&
    (!existsSync(args.reviewPolicy) || !statSync(args.reviewPolicy).isFile())
  ) {
    throw new Error(`review policy does not exist or is not a file: ${args.reviewPolicy}`)
  }
  if (!existsSync(dirname(args.output))) {
    throw new Error(`final output directory does not exist: ${dirname(args.output)}`)
  }
  if (existsSync(args.runDir)) {
    assertNewOrPreProbedRunDir(args.runDir)
  }
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(
      `final output already exists; pass --overwrite only when replacement is intended: ${args.output}`,
    )
  }
  if (args.source === args.output && !args.overwrite) {
    throw new Error(
      'in-place refurbishment requires --overwrite and still validates through the run directory',
    )
  }
}

function artifactPaths(runDir) {
  return {
    renderContext: join(runDir, 'render-context.json'),
    sourceSnapshot: join(runDir, 'source.pptx'),
    capabilities: join(runDir, 'xdoc-capabilities.json'),
    plan: join(runDir, 'refurbish-plan.json'),
    readiness: join(runDir, 'catalog-readiness.json'),
    deliveryReadiness: join(runDir, 'delivery-readiness.json'),
    inspect: join(runDir, 'reference-inspect.json'),
    nativeReport: join(runDir, 'refurbish-skin.json'),
    chromeDetect: join(runDir, 'chrome-detect.json'),
    fallbackReport: join(runDir, 'fallback-patch-report.json'),
    patch: join(runDir, 'patch.json'),
    deckLock: join(runDir, 'deck_lock.json'),
    contentAuditBaseline: join(runDir, 'content-audit.json'),
    referenceMap: join(runDir, 'reference-map.json'),
    lockCheck: join(runDir, 'check-lock.json'),
    dryRun: join(runDir, 'dry-run.json'),
    apply: join(runDir, 'apply.json'),
    visionDiff: join(runDir, 'vision-diff.json'),
    contentAuditFinal: join(runDir, 'content-audit-final.json'),
    reviewPolicy: join(runDir, 'review-policy.json'),
    reviewPolicyEvaluation: join(runDir, 'review-policy-evaluation.json'),
    fidelityGate: join(runDir, 'fidelity-gate.json'),
    pptxDiff: join(runDir, 'pptx-diff.json'),
    pptxDiffFull: join(runDir, 'pptx-diff-full.json'),
    finalInspect: join(runDir, 'candidate-inspect.json'),
    layoutSource: join(runDir, 'layout-source.json'),
    layoutFinal: join(runDir, 'layout-final.json'),
    findingAnalysis: join(runDir, 'finding-analysis.json'),
    candidate: join(runDir, 'candidate.pptx'),
    previews: join(runDir, 'previews'),
    previewReport: join(runDir, 'preview.json'),
    convertReport: join(runDir, 'convert-report.json'),
    contactSheet: join(runDir, 'previews', 'contact-sheet.png'),
    contactDiff: join(runDir, 'contact-diff.png'),
    contactDiffParts: [],
    contactDiffReport: join(runDir, 'contact-diff.json'),
    refurbishCompare: join(runDir, 'refurbish-compare.png'),
    refurbishCompareParts: [],
    refurbishAgentReviewParts: [],
    refurbishCompareReport: join(runDir, 'refurbish-compare.json'),
    refurbishCompareGate: join(runDir, 'refurbish-compare-gate.json'),
    progressLog: join(runDir, 'progress.jsonl'),
    prompt: join(runDir, 'prompt.txt'),
    summary: join(runDir, 'refurbish-run-summary.json'),
  }
}

function initialSummary(args, artifacts) {
  return {
    schemaVersion: 'pptx-nova-refurbish-run/v1',
    mode: 'refurbish',
    status: 'running',
    machineGatesPassed: false,
    deliveryReady: false,
    needsHumanReview: true,
    deckkit: args.deckkit,
    source: args.source,
    output: args.output,
    runDir: args.runDir,
    route: {
      requested: args.route,
      initialPlan: '',
      planned: '',
      executed: '',
      fallbackReason: '',
    },
    requiredReferences: [],
    recovery: null,
    operationAudit: null,
    artifacts: Object.fromEntries(Object.entries(artifacts).map(([key, path]) => [key, path])),
    phases: [],
    gates: [],
    review: {
      required: true,
      completed: false,
      contactDiffRequested: args.contactDiff,
      instructions:
        'Review contact-sheet.png, the complete refurbish-compare PNG set listed by the compare gate, and suspicious full-size PNGs. Confirm the target DeckKit is visibly applied and source content remains intact.',
    },
    warnings: [],
    layout: null,
    findingAnalysis: null,
    error: null,
  }
}

function finalizeArtifactPaths(summary, summaryPath) {
  summary.artifacts = Object.fromEntries(
    Object.entries(summary.artifacts).map(([key, value]) => {
      if (Array.isArray(value)) {
        return [key, value.filter((path) => typeof path === 'string' && existsSync(path))]
      }
      return [key, key === 'summary' || existsSync(value) ? value : null]
    }),
  )
  summary.artifacts.summary = summaryPath
}

function persistCatalogReadiness(summary, plan, args, artifacts) {
  const started = performance.now()
  const standardReadiness = ['production', 'default'].includes(plan.readiness)
  const explicitException = ['experimental', 'candidate'].includes(plan.readiness) && args.explicit
  const benchmarkPassed = plan.catalog?.benchmarkPassed
  const readinessPassed = standardReadiness || explicitException
  const benchmarkGatePassed = benchmarkPassed !== false
  const report = {
    schemaVersion: 'pptx-nova-catalog-readiness/v1',
    status: readinessPassed && benchmarkGatePassed ? 'pass' : 'fail',
    deckkit: args.deckkit,
    catalogPath: args.catalog,
    readiness: plan.readiness,
    explicit: args.explicit,
    explicitException,
    catalog: {
      found: plan.catalog?.found === true,
      id: plan.catalog?.id ?? args.deckkit,
      kitPath: plan.catalog?.path ?? '',
      benchmarkPassed,
    },
    agentGate: {
      passed: readinessPassed && benchmarkGatePassed,
      readinessPassed,
      benchmarkAvailable: benchmarkPassed !== null,
      benchmarkEvidencePassed: benchmarkPassed,
      benchmarkGatePassed,
      nextAction:
        readinessPassed && benchmarkGatePassed
          ? 'continue'
          : 'fix DeckKit readiness or use an allowed explicit selection before continuing',
    },
  }
  writeJson(artifacts.readiness, report)
  addInternalPhase(
    summary,
    'catalog-readiness-evidence',
    report.status === 'pass' ? 'passed' : 'failed',
    {
      artifact: relativeArtifact(summary.runDir, artifacts.readiness),
      durationMs: durationMs(started),
      readiness: plan.readiness,
      benchmarkPassed,
    },
  )
}

function runCatalogGate(summary, plan, args) {
  const standardReadiness = ['production', 'default'].includes(plan.readiness)
  const explicitException = ['experimental', 'candidate'].includes(plan.readiness) && args.explicit
  const benchmarkPassed = plan.catalog?.benchmarkPassed
  requireGate(summary, 'catalog-readiness', standardReadiness || explicitException, {
    readiness: plan.readiness,
    explicit: args.explicit,
    message:
      'DeckKit must be production/default or explicitly selected when candidate/experimental',
  })
  requireGate(summary, 'catalog-benchmark-summary', benchmarkPassed !== false, {
    available: benchmarkPassed !== null,
    passed: benchmarkPassed,
    message: 'Catalog benchmark summary explicitly reports failure',
  })
  if (benchmarkPassed === null) {
    summary.warnings.push(
      'Catalog does not include a quality benchmark summary; catalog readiness was used without a live benchmark audit.',
    )
  }
}

function runOptionalReadiness(summary, args, artifacts) {
  if (!args.readinessOut) return
  const readinessArgs = [
    READINESS_SCRIPT,
    '--deckkit',
    args.deckkit,
    '--target',
    'delivery',
    '--catalog',
    args.catalog,
    '--out',
    args.readinessOut,
    '--json',
  ]
  if (args.explicit) readinessArgs.push('--explicit')
  const report = runJsonPhase(summary, {
    name: 'delivery-readiness',
    bin: process.execPath,
    args: readinessArgs,
    artifact: artifacts.deliveryReadiness,
  })
  requireGate(summary, 'delivery-readiness', report?.passed === true, {
    readiness: report?.catalog?.readiness ?? '',
    message: 'Full delivery readiness audit did not pass',
  })
}

function runInspect(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'source-inspect',
    bin: args.xdocBin,
    args: ['pptx', 'inspect', artifacts.sourceSnapshot, '--json'],
    artifact: artifacts.inspect,
  })
  requireGate(
    summary,
    'source-inspect',
    report?.schemaVersion === 'pptx-inspect/v1' && expectedSlideCount(report) > 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      slideCount: expectedSlideCount(report),
      message: 'source inspect must be pptx-inspect/v1 with at least one slide',
    },
  )
  return report
}

function validateNativeReport(summary, report, artifacts) {
  requireGate(
    summary,
    'refurbish-skin-report',
    report?.schemaVersion === 'pptx-refurbish-skin/v1' &&
      report?.outcome === 'passed' &&
      report?.gate?.passed === true &&
      Number(report?.gate?.newHighIssues ?? 0) === 0 &&
      Number(report?.gate?.newMediumIssues ?? 0) === 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      status: report?.status ?? '',
      gate: report?.gate ?? null,
      message: 'refurbish-skin report must pass with no new high/medium issues',
    },
  )
  if (!report?.reports?.visionDiff || !report?.reports?.audit) {
    throw new PhaseFailure(
      'refurbish-skin-report',
      'refurbish-skin report is missing embedded visionDiff or audit evidence',
    )
  }
  writeJson(artifacts.visionDiff, report.reports.visionDiff)
  writeJson(artifacts.contentAuditFinal, report.reports.audit)
  gateVisionDiff(summary, report.reports.visionDiff)
  gateAudit(summary, report.reports.audit)
}

function runNative(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'native-refurbish-skin',
    bin: args.xdocBin,
    args: [
      'pptx',
      'refurbish-skin',
      '--source',
      artifacts.sourceSnapshot,
      '--deckkit',
      args.deckkit,
      '--output',
      artifacts.candidate,
      '--json',
    ],
    artifact: artifacts.nativeReport,
  })
  validateNativeReport(summary, report, artifacts)
}

function runFallback(summary, args, artifacts) {
  rmSync(artifacts.candidate, { force: true })
  const chromeDetect = runJsonPhase(summary, {
    name: 'chrome-detect',
    bin: args.xdocBin,
    args: ['pptx', 'chrome-detect', artifacts.sourceSnapshot, '--json'],
    artifact: artifacts.chromeDetect,
  })
  requireGate(
    summary,
    'chrome-detect',
    chromeDetect?.schemaVersion === 'pptx-chrome-detect/v1' && chromeDetect?.status !== 'failed',
    {
      schemaVersion: chromeDetect?.schemaVersion ?? '',
      status: chromeDetect?.status ?? '',
      message: 'chrome-detect must emit a successful pptx-chrome-detect/v1 report',
    },
  )

  const fallbackReport = runJsonPhase(summary, {
    name: 'fallback-patch',
    bin: process.execPath,
    args: [
      FALLBACK_PATCH_SCRIPT,
      '--deckkit',
      args.deckkit,
      '--source',
      artifacts.sourceSnapshot,
      '--inspect',
      artifacts.inspect,
      '--chrome-detect',
      artifacts.chromeDetect,
      '--output',
      artifacts.candidate,
      '--catalog',
      args.catalog,
      '--patch',
      artifacts.patch,
      '--lock',
      artifacts.deckLock,
      '--audit',
      artifacts.contentAuditBaseline,
      '--map',
      artifacts.referenceMap,
      '--json',
    ],
    artifact: artifacts.fallbackReport,
  })
  requireGate(
    summary,
    'fallback-patch-report',
    fallbackReport?.schemaVersion === 'pptx-nova-refurbish-fallback-patch-report/v1' &&
      fallbackReport?.status === 'success' &&
      Number(fallbackReport?.summary?.slideCount ?? 0) > 0 &&
      Number(fallbackReport?.summary?.ops ?? 0) > 0,
    {
      slideCount: Number(fallbackReport?.summary?.slideCount ?? 0),
      ops: Number(fallbackReport?.summary?.ops ?? 0),
      message: 'Fallback patch report must contain at least one slide and one patch op',
    },
  )
  for (const warning of fallbackReport?.summary?.warnings ?? []) {
    summary.warnings.push(`fallback-patch: ${warning}`)
  }
  summary.operationAudit = fallbackReport?.summary?.operationAudit
    ? structuredClone(fallbackReport.summary.operationAudit)
    : {
        plannedOps: Number(fallbackReport?.summary?.ops ?? 0),
        emittedOps: Number(fallbackReport?.summary?.ops ?? 0),
        knownNoOpOps: 0,
        effectiveOps: null,
        knownChangingOps: 0,
        unknownEffectOps: Number(fallbackReport?.summary?.ops ?? 0),
        evidenceNote:
          'The fallback report predates operation classification; emitted operations are not evidence of effective changes.',
      }

  const lockCheck = runJsonPhase(summary, {
    name: 'check-lock',
    bin: process.execPath,
    args: [CHECK_LOCK_SCRIPT, '--lock', artifacts.deckLock, '--patch', artifacts.patch, '--json'],
    artifact: artifacts.lockCheck,
  })
  requireGate(summary, 'check-lock', lockCheck?.valid === true, {
    errors: Number(lockCheck?.summary?.errors ?? 0),
    warnings: Number(lockCheck?.summary?.warnings ?? 0),
    message: 'Generated fallback deck_lock and patch did not pass check-lock',
  })
  for (const warning of lockCheck?.warnings ?? []) {
    summary.warnings.push(`check-lock ${warning.code ?? 'warning'}: ${warning.message ?? warning}`)
  }

  const dryRun = runJsonPhase(summary, {
    name: 'dry-run',
    bin: args.xdocBin,
    args: [
      'pptx',
      'apply',
      '-p',
      artifacts.patch,
      '-i',
      artifacts.sourceSnapshot,
      '-o',
      artifacts.candidate,
      '--dry-run',
      '--json',
    ],
    artifact: artifacts.dryRun,
  })
  requireGate(
    summary,
    'dry-run',
    dryRun?.schemaVersion === 'pptx-dry-run/v1' && dryRun?.status === 'success',
    {
      schemaVersion: dryRun?.schemaVersion ?? '',
      status: dryRun?.status ?? '',
      message: 'xdoc dry-run reported failure',
    },
  )

  const apply = runJsonPhase(summary, {
    name: 'apply',
    bin: args.xdocBin,
    args: [
      'pptx',
      'apply',
      '-p',
      artifacts.patch,
      '-i',
      artifacts.sourceSnapshot,
      '-o',
      artifacts.candidate,
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.apply,
  })
  requireGate(
    summary,
    'apply',
    apply?.schemaVersion === 'pptx-apply/v1' &&
      apply?.status === 'success' &&
      existsSync(artifacts.candidate),
    {
      schemaVersion: apply?.schemaVersion ?? '',
      status: apply?.status ?? '',
      outputExists: existsSync(artifacts.candidate),
      message: 'xdoc apply did not produce a successful pptx-apply/v1 candidate',
    },
  )
  summary.operationAudit.execution = {
    dryRun: summarizeOpResults(dryRun),
    apply: summarizeOpResults(apply),
  }
  fallbackReport.summary.operationAudit = summary.operationAudit
  writeJson(artifacts.fallbackReport, fallbackReport)

  const visionDiff = runJsonPhase(summary, {
    name: 'vision-diff-command',
    bin: args.xdocBin,
    args: [
      'pptx',
      'vision-diff',
      '--source',
      artifacts.sourceSnapshot,
      '--candidate',
      artifacts.candidate,
      '--json',
    ],
    artifact: artifacts.visionDiff,
  })
  gateVisionDiff(summary, visionDiff)

  const audit = runJsonPhase(summary, {
    name: 'refurbish-audit-command',
    bin: args.xdocBin,
    args: [
      'pptx',
      'refurbish-audit',
      '--source',
      artifacts.sourceSnapshot,
      '--final',
      artifacts.candidate,
      '--map',
      artifacts.referenceMap,
      '--json',
    ],
    artifact: artifacts.contentAuditFinal,
  })
  gateAudit(summary, audit)
}

function runReviewPolicyEvaluation(summary, artifacts, candidateSnapshot) {
  const started = performance.now()
  const explicitPolicy = existsSync(artifacts.reviewPolicy)
    ? readJson(artifacts.reviewPolicy, 'review policy')
    : null
  const referenceMap = existsSync(artifacts.referenceMap)
    ? readJson(artifacts.referenceMap, 'reference map')
    : null
  const embeddedPolicy = hasEmbeddedReviewedFindings(referenceMap) ? referenceMap : null
  const policyDocument = explicitPolicy ?? embeddedPolicy
  const policyDocumentPath = explicitPolicy
    ? artifacts.reviewPolicy
    : embeddedPolicy
      ? artifacts.referenceMap
      : ''
  const evaluation = evaluateReviewPolicy({
    policyDocument,
    policyDocumentPath,
    allowEmbeddedPolicy: Boolean(!explicitPolicy && embeddedPolicy),
    sourcePptx: artifacts.sourceSnapshot,
    candidatePptx: artifacts.candidate,
    findings: Array.isArray(candidateSnapshot?.risks) ? candidateSnapshot.risks : [],
    evidencePaths: {
      layoutSnapshot: artifacts.layoutFinal,
      finalAudit: artifacts.contentAuditFinal,
      visionDiff: artifacts.visionDiff,
      referenceMap: existsSync(artifacts.referenceMap) ? artifacts.referenceMap : '',
    },
  })
  if (explicitPolicy && embeddedPolicy) {
    const ambiguity = {
      code: 'review-policy-source-ambiguous',
      message:
        'reviewed findings must come from either --review-policy or reference-map.json, not both',
    }
    evaluation.status = 'fail'
    evaluation.applied = []
    evaluation.reviewedFindings = []
    evaluation.remainingActionable = candidateSnapshot.risks.filter(
      (finding) => finding?.classification !== 'informational',
    )
    evaluation.informational = candidateSnapshot.risks.filter(
      (finding) => finding?.classification === 'informational',
    )
    evaluation.errors = [...evaluation.errors, ambiguity]
    evaluation.summary = {
      ...evaluation.summary,
      appliedReviewCount: 0,
      reviewedFindingCount: 0,
      remainingActionableCount: evaluation.remainingActionable.length,
      informationalCount: evaluation.informational.length,
      errorCount: evaluation.errors.length,
    }
  }
  writeJson(artifacts.reviewPolicyEvaluation, evaluation)
  addInternalPhase(
    summary,
    'review-policy-evaluation',
    evaluation.status === 'pass' ? 'passed' : 'warning',
    {
      artifact: relativeArtifact(summary.runDir, artifacts.reviewPolicyEvaluation),
      durationMs: durationMs(started),
      status: evaluation.status,
      declaredReviews: Number(evaluation.summary?.declaredReviewCount ?? 0),
      appliedReviews: Number(evaluation.summary?.appliedReviewCount ?? 0),
      errors: Number(evaluation.summary?.errorCount ?? 0),
    },
  )
  return evaluation
}

function operationEnvelope(path, report, binding) {
  if (!report || !path || !existsSync(path)) return null
  return { report, artifactSha256: sha256(path), binding }
}

function buildFindingAnalysisInput({
  artifacts,
  sourceSnapshot,
  candidateSnapshot,
  semanticDiff,
  reviewEvaluation,
}) {
  const sourcePptxSha256 = sha256(artifacts.sourceSnapshot)
  const candidatePptxSha256 = sha256(artifacts.candidate)
  const patchSha256 = existsSync(artifacts.patch) ? sha256(artifacts.patch) : null
  const dryRun = existsSync(artifacts.dryRun)
    ? readJson(artifacts.dryRun, 'dry-run evidence')
    : null
  const apply = existsSync(artifacts.apply) ? readJson(artifacts.apply, 'apply evidence') : null
  return {
    workflowProfile: {
      profileId: 'refurbish-shadow/v1-draft',
      kind: 'refurbish',
      mode: 'standard',
      mutationIntent: 'style',
      deliveryStage: 'final',
    },
    bindingContext: { assurance: 'runner-observed', schemaDeclaredInputs: [] },
    sourceLayout: {
      report: sourceSnapshot,
      binding: {
        pptxSha256: sourcePptxSha256,
        layoutArtifactSha256: sha256(artifacts.layoutSource),
        layoutSemanticSha256: layoutSemanticSha256(sourceSnapshot),
      },
    },
    candidateLayout: {
      report: candidateSnapshot,
      binding: {
        pptxSha256: candidatePptxSha256,
        layoutArtifactSha256: sha256(artifacts.layoutFinal),
        layoutSemanticSha256: layoutSemanticSha256(candidateSnapshot),
      },
    },
    changedScope: {
      mode: 'full-deck',
      slideIndexes: [],
      objectIds: [],
      origin: 'workflow-profile',
      binding: {
        sourcePptxSha256,
        candidatePptxSha256,
        evidenceArtifactSha256: null,
      },
    },
    mutationEvidence: {
      dryRun: operationEnvelope(artifacts.dryRun, dryRun, {
        sourcePptxSha256,
        patchSha256,
      }),
      apply: operationEnvelope(artifacts.apply, apply, {
        sourcePptxSha256,
        candidatePptxSha256,
        patchSha256,
      }),
      semanticDiff: {
        report: semanticDiff,
        artifactSha256: sha256(artifacts.pptxDiff),
        binding: { sourcePptxSha256, candidatePptxSha256 },
      },
    },
    reviewEvaluation: {
      report: reviewEvaluation,
      artifactSha256: sha256(artifacts.reviewPolicyEvaluation),
    },
    executionPolicy: { automation: 'human-in-loop', enforcement: 'shadow' },
  }
}

function findingAnalysisShadowFailure(error) {
  const message = error instanceof Error ? error.message : String(error)
  const artifactFailure = /does not exist|failed to read|ENOENT|valid JSON/i.test(message)
  const code = artifactFailure
    ? 'finding-analysis-artifact-unreadable'
    : 'finding-analysis-internal-error'
  return {
    schemaVersion: 'pptx-nova-finding-analysis/v1-draft',
    evaluation: {
      status: 'failed',
      errors: [{ code, message }],
      diagnostics: [],
    },
    workflowProfile: {
      profileId: 'refurbish-shadow/v1-draft',
      kind: 'refurbish',
      mode: 'standard',
      mutationIntent: 'style',
      deliveryStage: 'final',
    },
    bindings: {
      assurance: 'runner-observed',
      schemaDeclaredInputs: [],
      source: null,
      candidate: null,
      changedScope: null,
      mutationEvidence: {},
      reviewEvaluation: null,
    },
    policy: { ruleSetVersion: 'pptx-nova-finding-rules/v1-shadow.1' },
    analysisIdentity: null,
    findings: [],
    resolvedFindings: [],
    summary: { countsComplete: false, errorCount: 1 },
    agentGate: {
      enforcement: 'shadow',
      proposedStatus: 'fail',
      effectiveStatus: 'not-applied',
      governingFindingKeys: [],
      nextAction: artifactFailure
        ? 'regenerate-bound-evidence'
        : 'diagnose-analysis-internal-error',
    },
  }
}

function runFindingAnalysis({
  summary,
  artifacts,
  sourceSnapshot,
  candidateSnapshot,
  semanticDiff,
  reviewEvaluation,
}) {
  const started = performance.now()
  let report
  try {
    report = evaluateFindings(
      buildFindingAnalysisInput({
        artifacts,
        sourceSnapshot,
        candidateSnapshot,
        semanticDiff,
        reviewEvaluation,
      }),
    )
  } catch (error) {
    report = findingAnalysisShadowFailure(error)
  }
  const elapsedMs = durationMs(started)
  writeJson(artifacts.findingAnalysis, report)
  addInternalPhase(
    summary,
    'finding-analysis-shadow',
    report.evaluation.status === 'complete' ? 'passed' : 'warning',
    {
      artifact: relativeArtifact(summary.runDir, artifacts.findingAnalysis),
      durationMs: elapsedMs,
      evaluationStatus: report.evaluation.status,
      proposedStatus: report.agentGate.proposedStatus,
      effectiveStatus: report.agentGate.effectiveStatus,
      findingCount: Number(report.summary?.findingCount ?? 0),
      objectCount: Number(candidateSnapshot.summary?.objectCount ?? 0),
      additionalInspectCount: 0,
      additionalRenderCount: 0,
    },
  )
  summary.findingAnalysis = {
    status: report.evaluation.status,
    proposedStatus: report.agentGate.proposedStatus,
    effectiveStatus: report.agentGate.effectiveStatus,
    findingCount: Number(report.summary?.findingCount ?? 0),
    unresolvedFindingCount: Number(report.summary?.unresolvedFindingCount ?? 0),
    resolvedFindingCount: Number(report.summary?.resolvedFindingCount ?? 0),
    nextAction: report.agentGate.nextAction,
    topFindings: report.summary?.topFindings ?? [],
    errors: report.evaluation.errors,
    diagnostics: report.evaluation.diagnostics,
  }
  if (report.evaluation.status === 'failed') {
    summary.warnings.push(
      `finding-analysis shadow failed: ${report.evaluation.errors.map((item) => item.code).join(', ')}`,
    )
  }
  return report
}

function runFidelityGate(summary, artifacts, findingAnalysisReport = null) {
  const gateArgs = [
    FIDELITY_GATE_SCRIPT,
    '--mode',
    'refurbish',
    '--source-inspect',
    artifacts.inspect,
    '--source-pptx',
    artifacts.sourceSnapshot,
    '--candidate-pptx',
    artifacts.candidate,
    '--final-audit',
    artifacts.contentAuditFinal,
    '--vision-diff',
    artifacts.visionDiff,
    '--layout-snapshot',
    artifacts.layoutFinal,
    '--review-evaluation',
    artifacts.reviewPolicyEvaluation,
  ]
  if (existsSync(artifacts.referenceMap)) {
    gateArgs.push('--reference-map', artifacts.referenceMap)
  }
  if (existsSync(artifacts.contentAuditBaseline)) {
    gateArgs.push('--content-audit', artifacts.contentAuditBaseline)
  }
  if (existsSync(artifacts.reviewPolicy)) {
    gateArgs.push('--review-policy', artifacts.reviewPolicy)
  }
  gateArgs.push('--json')

  const report = runJsonPhase(summary, {
    name: 'fidelity-gate',
    bin: process.execPath,
    args: gateArgs,
    artifact: artifacts.fidelityGate,
  })
  requireGate(summary, 'fidelity-gate', report?.status !== 'fail', {
    status: report?.status ?? '',
    errors: Number(report?.summary?.errors ?? 0),
    warnings: Number(report?.summary?.warnings ?? 0),
    sourceSlides: report?.summary?.sourceSlides ?? null,
    finalSlides: report?.summary?.finalSlides ?? null,
    mappedSlides: report?.summary?.mappedSlides ?? null,
    declaredReviews: Number(report?.summary?.declaredReviews ?? 0),
    appliedReviews: Number(report?.summary?.appliedReviews ?? 0),
    reviewedFindings: Number(report?.summary?.reviewedFindings ?? 0),
    remainingActionableFindings: Number(report?.summary?.remainingActionableFindings ?? 0),
    message:
      'fidelity-gate must pass or warn using final audit, vision diff, and available reference-map evidence',
  })
  if (summary.layout) {
    const remaining = Array.isArray(report?.reviewPolicy?.remainingActionable)
      ? report.reviewPolicy.remainingActionable
      : []
    const remainingSlideIndexes = [
      ...new Set(
        remaining
          .map((finding) => Number(finding?.slideIndex ?? finding?.slide))
          .filter((value) => Number.isInteger(value) && value >= 0),
      ),
    ].sort((a, b) => a - b)
    const remainingByCode = new Map()
    for (const finding of remaining) {
      const code = String(finding?.code ?? 'layout-finding')
      remainingByCode.set(code, (remainingByCode.get(code) ?? 0) + 1)
    }
    summary.layout.rawActionableRiskCount = summary.layout.actionableRiskCount
    summary.layout.rawActionableSlideCount = summary.layout.actionableSlideCount
    summary.layout.rawActionableSlideIndexes = summary.layout.actionableSlideIndexes
    summary.layout.rawActionableSlideNumbers = summary.layout.actionableSlideNumbers
    summary.layout.rawActionablePreviewFiles = summary.layout.actionablePreviewFiles
    summary.layout.rawTopActionable = summary.layout.topActionable
    summary.layout.reviewedRiskCount = Number(report?.summary?.reviewedFindings ?? 0)
    summary.layout.actionableRiskCount = Number(
      report?.summary?.remainingActionableFindings ?? summary.layout.actionableRiskCount,
    )
    summary.layout.actionableSlideCount = remainingSlideIndexes.length
    summary.layout.actionableSlideIndexes = remainingSlideIndexes
    summary.layout.actionableSlideNumbers = remainingSlideIndexes.map((index) => index + 1)
    summary.layout.actionablePreviewFiles = remainingSlideIndexes.map(
      (index) => `slide-${String(index + 1).padStart(3, '0')}.png`,
    )
    summary.layout.topActionable = annotateTopActionable(
      [...remainingByCode.entries()]
        .map(([code, count]) => ({ code, classification: 'actionable', count }))
        .sort((a, b) => b.count - a.count || a.code.localeCompare(b.code))
        .slice(0, 5),
      findingAnalysisReport,
    )
    summary.layout.reviewPolicyStatus = report?.reviewPolicy?.status ?? null
    summary.layout.appliedReviews = report?.reviewPolicy?.applied ?? []
  }
  for (const warning of report?.warnings ?? []) {
    summary.warnings.push(`fidelity-gate ${warning.code ?? 'warning'}: ${warning.message ?? ''}`)
  }
}

function runLayoutSnapshots(summary, args, artifacts, sourceInspect) {
  const candidateInspect = runJsonPhase(summary, {
    name: 'final-inspect',
    bin: args.xdocBin,
    args: ['pptx', 'inspect', artifacts.candidate, '--json'],
    artifact: artifacts.finalInspect,
  })
  const sourceStarted = performance.now()
  const sourceSnapshot = buildLayoutSnapshot(sourceInspect, {
    sourceLabel: artifacts.inspect,
  })
  writeJson(artifacts.layoutSource, sourceSnapshot)
  addInternalPhase(summary, 'source-layout-snapshot', 'passed', {
    artifact: relativeArtifact(summary.runDir, artifacts.layoutSource),
    durationMs: durationMs(sourceStarted),
    objectCount: Number(sourceSnapshot.summary?.objectCount ?? 0),
    findingCount: Number(sourceSnapshot.summary?.riskCount ?? 0),
    layoutSemanticSha256: layoutSemanticSha256(sourceSnapshot),
  })

  const candidateStarted = performance.now()
  const candidateSnapshot = buildLayoutSnapshot(candidateInspect, {
    sourceLabel: artifacts.finalInspect,
  })
  writeJson(artifacts.layoutFinal, candidateSnapshot)
  addInternalPhase(summary, 'layout-snapshot', 'passed', {
    artifact: relativeArtifact(summary.runDir, artifacts.layoutFinal),
    durationMs: durationMs(candidateStarted),
    objectCount: Number(candidateSnapshot.summary?.objectCount ?? 0),
    findingCount: Number(candidateSnapshot.summary?.riskCount ?? 0),
    layoutSemanticSha256: layoutSemanticSha256(candidateSnapshot),
  })

  const riskCount = Number(candidateSnapshot?.summary?.riskCount ?? 0)
  const actionableRiskCount = Number(candidateSnapshot?.summary?.actionableRiskCount ?? riskCount)
  const informationalRiskCount = Number(candidateSnapshot?.summary?.informationalRiskCount ?? 0)
  const topActionable = Array.isArray(candidateSnapshot?.summary?.topActionable)
    ? candidateSnapshot.summary.topActionable
    : []
  summary.layout = {
    status: candidateSnapshot?.status ?? null,
    riskCount,
    actionableRiskCount,
    informationalRiskCount,
    slideIndexBase: Number(candidateSnapshot?.summary?.slideIndexBase ?? 0),
    slideNumberBase: Number(candidateSnapshot?.summary?.slideNumberBase ?? 1),
    affectedSlideCount: Number(candidateSnapshot?.summary?.affectedSlideCount ?? 0),
    actionableSlideCount: Number(candidateSnapshot?.summary?.actionableSlideCount ?? 0),
    actionableSlideIndexes: candidateSnapshot?.summary?.actionableSlideIndexes ?? [],
    actionableSlideNumbers: candidateSnapshot?.summary?.actionableSlideNumbers ?? [],
    actionablePreviewFiles: candidateSnapshot?.summary?.actionablePreviewFiles ?? [],
    topActionable,
  }
  return { sourceSnapshot, candidateSnapshot, candidateInspect }
}

function listPngFiles(dir, excludedNames = new Set()) {
  if (!existsSync(dir)) return []
  return readdirSync(dir)
    .filter((name) => /\.png$/i.test(name) && !excludedNames.has(name))
    .sort((a, b) => a.localeCompare(b, 'en'))
    .map((name) => {
      const path = join(dir, name)
      return { name, path, bytes: statSync(path).size }
    })
}

function expectedSlideCount(inspect) {
  const count = Number(inspect?.presentation?.slideCount)
  if (Number.isInteger(count) && count >= 0) return count
  return Array.isArray(inspect?.slides) ? inspect.slides.length : null
}

function runPreviews(summary, args, artifacts, inspect) {
  let mode = 'pptx-preview'
  let previewReport = null
  const expectedCount = expectedSlideCount(inspect)
  const slides = Array.from({ length: expectedCount ?? 0 }, (_, index) => index + 1)
  const cache = createPageBitmapCacheBinding({
    cacheDir: join(dirname(args.runDir), '.render-cache'),
    pptxPath: artifacts.candidate,
    dpi: 192,
    xdocBin: args.xdocBin,
  })
  const cacheBefore = snapshotPageBitmapCache(cache, slides)
  try {
    previewReport = runJsonPhase(summary, {
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
  } catch (error) {
    const phase = summary.phases.findLast((item) => item.name === 'preview-render')
    if (phase) {
      phase.status = 'recovered'
      phase.recoveredBy = 'preview-render-fallback-convert'
    }
    mode = 'convert-fallback'
    summary.warnings.push(
      `xdoc pptx preview failed; used xdoc convert PNG fallback for visual review artifacts. ${error.message}`,
    )
    mkdirSync(artifacts.previews, { recursive: true })
    runPlainPhase(summary, {
      name: 'preview-render-fallback-convert',
      bin: args.xdocBin,
      args: [
        'convert',
        artifacts.candidate,
        '--to',
        'png',
        '--output',
        artifacts.previews,
        '--dpi',
        '192',
        '--overwrite',
        '--quiet',
        '--report',
        artifacts.convertReport,
        '--contact-sheet',
        '--contact-output',
        artifacts.contactSheet,
      ],
      env: { XDOC_PAGE_CACHE_PREFIX: cache.prefix },
    })
  }
  if (previewReport) verifyRenderContext(previewReport)
  else {
    const converted = JSON.parse(readFileSync(artifacts.convertReport, 'utf8'))
    const manifests = (converted.items ?? [])
      .flatMap((item) => item.outputs ?? [])
      .filter((path) => /(?:^|[/.])manifest\.json$/.test(path))
    if (manifests.length !== 1)
      throw new Error('Fallback conversion must retain one render-context manifest')
    verifyRenderContext(JSON.parse(readFileSync(manifests[0], 'utf8')))
  }
  const cacheAfter = snapshotPageBitmapCache(cache, slides)
  const previewPhase = summary.phases.findLast((item) =>
    ['preview-render', 'preview-render-fallback-convert'].includes(item.name),
  )
  if (previewPhase) {
    previewPhase.pageBitmapCache = pageBitmapCacheMetrics(cache, cacheBefore, cacheAfter)
  }
  const contactSheetName = basename(artifacts.contactSheet)
  const files = listPngFiles(artifacts.previews, new Set([contactSheetName]))
  const contactBytes = existsSync(artifacts.contactSheet)
    ? statSync(artifacts.contactSheet).size
    : 0
  const manifestPages = Array.isArray(previewReport?.pages) ? previewReport.pages.length : null
  requireGate(
    summary,
    'png-previews',
    (mode === 'convert-fallback' || previewReport?.status === 'success') &&
      expectedCount !== null &&
      files.length === expectedCount &&
      files.length > 0 &&
      files.every((file) => file.bytes > 0) &&
      contactBytes > 0,
    {
      mode,
      manifestStatus: previewReport?.status ?? null,
      manifestPages,
      count: files.length,
      expectedCount,
      allNonEmpty: files.every((file) => file.bytes > 0),
      contactSheetBytes: contactBytes,
      files: files.map((file) => ({ name: file.name, bytes: file.bytes })),
      message:
        'PNG preview count must match source slides and all preview/contact artifacts must be non-empty',
    },
  )
}

function materializeContactDiff(summary, args, artifacts, compareReport) {
  if (!args.contactDiff) return
  const materialized = materializeCompareAliases({
    compareReport,
    compareReportPath: artifacts.refurbishCompareReport,
    compareOutputPath: artifacts.refurbishCompare,
    aliasOutputPath: artifacts.contactDiff,
    aliasReportPath: artifacts.contactDiffReport,
    aliasKind: 'contact',
    sourceKind: 'refurbish',
  })
  const { report, partCount, renderInvocationsSaved } = materialized
  summary.artifacts.contactDiffParts = materialized.partPaths
  summary.review.contactDiffReuse = report.reuse
  requireGate(summary, 'contact-diff-artifact', report?.status === 'success', {
    status: report?.status ?? '',
    partCount,
    reused: true,
    renderInvocationsSaved,
    message: 'Requested contact-diff aliases were not materialized from final compare evidence',
  })
  addInternalPhase(summary, 'contact-diff-reuse', 'passed', {
    artifact: relativeArtifact(args.runDir, artifacts.contactDiffReport),
    partCount,
    renderInvocationsSaved,
  })
}

function runSemanticDiff(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'pptx-semantic-diff',
    bin: args.xdocBin,
    args: [
      'pptx',
      'diff',
      '--source',
      artifacts.sourceSnapshot,
      '--candidate',
      artifacts.candidate,
      '--detail',
      'summary',
      '--output',
      artifacts.pptxDiffFull,
      '--json',
    ],
    artifact: artifacts.pptxDiff,
  })
  verifyDiffEvidence(report, artifacts.sourceSnapshot, artifacts.candidate)
  gateSemanticDiff(summary, report)
  if (summary.operationAudit) {
    const emittedOps = Number(summary.operationAudit.emittedOps ?? 0)
    const reliableChanges = Number(report?.summary?.reliableChanges ?? 0)
    summary.operationAudit.semanticDiff = {
      reliableChanges,
      shapeChanged: Number(report?.summary?.shapeChanged ?? 0),
      slideChanged: Number(report?.summary?.slideChanged ?? 0),
      reliableChangesPerEmittedOp:
        emittedOps > 0 ? Number((reliableChanges / emittedOps).toFixed(4)) : null,
      attribution:
        'Deck-level semantic diff cannot attribute reliable changes to individual patch operations.',
    }
    if (existsSync(artifacts.fallbackReport)) {
      const fallbackReport = readJson(artifacts.fallbackReport, 'fallback patch report')
      fallbackReport.summary.operationAudit = summary.operationAudit
      writeJson(artifacts.fallbackReport, fallbackReport)
    }
  }
  return report
}

function runRefurbishCompare(summary, args, artifacts, inspect) {
  const report = runJsonPhase(summary, {
    name: 'refurbish-compare',
    bin: process.execPath,
    args: [
      COMPARE_SCRIPT,
      '--source',
      artifacts.sourceSnapshot,
      '--candidate',
      artifacts.candidate,
      '--run-dir',
      args.runDir,
      '--kind',
      'refurbish',
      '--output',
      artifacts.refurbishCompare,
      '--report',
      artifacts.refurbishCompareReport,
      '--slide-count',
      String(expectedSlideCount(inspect)),
      '--compare-chunk-size',
      String(args.compareChunkSize),
      '--compare-concurrency',
      String(args.compareConcurrency),
      '--dpi',
      '192',
      '--fallback-dpi',
      '144',
      '--agent-review-dpi',
      '96',
      '--xdoc-bin',
      args.xdocBin,
      '--progress',
      progressReporter.forwardFd !== null ? 'jsonl' : args.progress,
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.refurbishCompareReport,
    forwardProgress: true,
  })
  const renderMetrics = analyzeCompareRendering(report)
  const agentReviewParts = Array.isArray(report?.agentReviewParts)
    ? report.agentReviewParts
    : report?.pptxNovaCompare?.agentReview
      ? [report.pptxNovaCompare.agentReview]
      : []
  summary.artifacts.refurbishAgentReviewParts = agentReviewParts
    .map((part) => part?.path)
    .filter(Boolean)
  const phase = summary.phases.findLast((item) => item.name === 'refurbish-compare')
  if (phase) Object.assign(phase, renderMetrics)
  return report
}

function runRefurbishCompareGate(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'refurbish-compare-delivery',
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
      'refurbish',
      '--publish',
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.refurbishCompareGate,
  })
  const siblingPaths = report?.agentSummary?.siblingPaths ?? []
  summary.artifacts.refurbishCompareParts = siblingPaths.length > 1 ? siblingPaths : []
  requireGate(summary, 'refurbish-compare-delivery', report?.status === 'pass', {
    status: report?.status ?? '',
    finalBinding: report?.finalBinding?.status ?? null,
    finalSha256: report?.finalBinding?.publishedFinal?.sha256 ?? null,
    siblingPath: report?.agentSummary?.siblingPath ?? null,
    siblingPaths,
    partCount: report?.parts?.length || 1,
    message:
      'The final PPTX and complete refurbish compare PNG set must be SHA-256-bound to the compared candidate',
  })
  requireGate(
    summary,
    'published-output-binding',
    report?.finalBinding?.status === 'bound' &&
      report?.finalBinding?.publishedFinal?.path === args.output &&
      existsSync(args.output) &&
      statSync(args.output).size === report?.finalBinding?.publishedFinal?.byteLength &&
      sha256(args.output) === report?.finalBinding?.publishedFinal?.sha256,
    {
      output: args.output,
      bytes: existsSync(args.output) ? statSync(args.output).size : 0,
      sha256: report?.finalBinding?.publishedFinal?.sha256 ?? null,
      message: 'Published output is not bound to the compared candidate',
    },
  )
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
  const started = performance.now()
  writeFileSync(artifacts.prompt, text.endsWith('\n') ? text : `${text}\n`)
  addInternalPhase(summary, 'prompt-archive', 'passed', {
    artifact: relativeArtifact(args.runDir, artifacts.prompt),
    durationMs: durationMs(started),
    bytes: statSync(artifacts.prompt).size,
    source: args.promptFile ? 'file' : 'text',
  })
}

function buildRecoveredFallbackPlan(args, artifacts, initialPlan, recovery) {
  const fallbackPlan = buildRefurbishPlan({
    deckkit: args.deckkit,
    source: artifacts.sourceSnapshot,
    output: artifacts.candidate,
    catalog: args.catalog,
    explicit: args.explicit,
    route: 'fallback',
  })
  fallbackPlan.routeSelection.requested = args.route
  fallbackPlan.routeSelection.initialSelected = initialPlan.route
  fallbackPlan.recovery = recovery
  return fallbackPlan
}

function runRefurbish(inputArgs) {
  const runStarted = performance.now()
  const args = normalizeArgs(inputArgs)
  validatePaths(args)
  mkdirSync(args.runDir, { recursive: true })
  ensureRenderContext(args.runDir)
  const artifacts = artifactPaths(args.runDir)
  const summary = initialSummary(args, artifacts)
  attachProgressArchive(args, artifacts)

  try {
    archivePrompt(summary, args, artifacts)
    const sourceSnapshotStarted = performance.now()
    copyFileSync(args.source, artifacts.sourceSnapshot)
    addInternalPhase(summary, 'source-snapshot', 'passed', {
      artifact: relativeArtifact(args.runDir, artifacts.sourceSnapshot),
      durationMs: durationMs(sourceSnapshotStarted),
      bytes: statSync(artifacts.sourceSnapshot).size,
    })
    if (args.reviewPolicy) {
      copyFileSync(args.reviewPolicy, artifacts.reviewPolicy)
      addInternalPhase(summary, 'review-policy-snapshot', 'passed', {
        artifact: relativeArtifact(args.runDir, artifacts.reviewPolicy),
        bytes: statSync(artifacts.reviewPolicy).size,
        sha256: sha256(artifacts.reviewPolicy),
      })
    }

    const planStarted = performance.now()
    let plan = buildRefurbishPlan({
      deckkit: args.deckkit,
      source: artifacts.sourceSnapshot,
      output: artifacts.candidate,
      catalog: args.catalog,
      explicit: args.explicit,
      route: args.route,
    })
    writeJson(artifacts.plan, plan)
    addInternalPhase(summary, 'refurbish-plan', plan.status === 'blocked' ? 'failed' : 'passed', {
      artifact: relativeArtifact(args.runDir, artifacts.plan),
      durationMs: durationMs(planStarted),
      status: plan.status,
      route: plan.route ?? '',
    })
    summary.route.initialPlan = plan.route
    summary.route.planned = plan.route
    summary.requiredReferences = plan.requiredReferences ?? []
    persistCatalogReadiness(summary, plan, args, artifacts)
    if (plan.status === 'blocked') {
      throw new PhaseFailure('refurbish-plan', plan.blockers.join('; ') || 'refurbish plan blocked')
    }
    runCatalogGate(summary, plan, args)
    runOptionalReadiness(summary, args, artifacts)

    const capabilityProbeArgs = [CAPABILITY_PROBE_SCRIPT, '--xdoc-bin', args.xdocBin]
    if (plan.nativeSkinning?.supported === true && args.route !== 'fallback') {
      capabilityProbeArgs.push(
        '--require-command',
        'pptx.refurbish-skin',
        '--require-native-deckkit',
        args.deckkit,
      )
    }
    capabilityProbeArgs.push('--json')
    const capabilityReport = runJsonPhase(summary, {
      name: 'xdoc-capability-probe',
      bin: process.execPath,
      args: capabilityProbeArgs,
      artifact: artifacts.capabilities,
    })
    if (capabilityReport.status !== 'ready') {
      summary.warnings.push(
        'xdoc capability schema is degraded; the runner will continue with its existing plan, command errors, and fallback gates instead of assuming missing capabilities are unsupported.',
      )
    }
    if (capabilityReport.requirements?.status === 'attention') {
      const undisclosed = (capabilityReport.requirements?.undisclosedRequired ?? [])
        .map((item) => `${item.kind}=${item.value}`)
        .join(', ')
      summary.warnings.push(
        `Undisclosed refurbish capabilities: ${undisclosed || 'unknown'}. This is audit evidence only and does not disable native or fallback execution.`,
      )
    }

    const inspect = runInspect(summary, args, artifacts)

    const nativeSupported = plan.nativeSkinning?.supported === true
    if (args.route === 'native' && !nativeSupported) {
      throw new PhaseFailure(
        'route-selection',
        `DeckKit "${args.deckkit}" does not declare native skinning support`,
      )
    }

    const tryNative = args.route === 'native' || (args.route === 'auto' && nativeSupported)
    let useFallback = args.route === 'fallback' || !tryNative
    if (tryNative) {
      try {
        runNative(summary, args, artifacts)
        summary.route.executed = 'native-skin-first'
      } catch (error) {
        const unsupportedComplexity =
          error instanceof PhaseFailure && error.kind === 'UnsupportedComplexity'
        const contrastRecovery = classifyNativeContrastRecovery(error?.report)
        const contrastRecoverable = args.route === 'auto' && contrastRecovery.eligible
        summary.recovery = {
          ...contrastRecovery,
          status: contrastRecoverable
            ? 'recovered'
            : contrastRecovery.eligible
              ? 'eligible-but-disabled'
              : 'not-eligible',
          automaticFallbackAllowed: args.route === 'auto',
          nativeReport: relativeArtifact(args.runDir, artifacts.nativeReport),
        }
        if (contrastRecoverable) {
          const phase = summary.phases.findLast((item) => item.name === 'native-refurbish-skin')
          if (phase) {
            phase.status = 'recovered'
            phase.recoveredBy = 'fallback-patch'
          }
          summary.route.fallbackReason =
            'native refurbish-skin failed only on attributable new low-contrast-text findings'
          summary.warnings.push(
            `Native refurbish-skin introduced only low-contrast-text blockers (${contrastRecovery.findings.newMedium} medium across ${contrastRecovery.findings.affectedSlides.length} slide(s)); runner retained the failed native report and continued with the same DeckKit fallback patch.`,
          )
          plan = buildRecoveredFallbackPlan(args, artifacts, plan, summary.recovery)
          summary.route.planned = plan.route
          summary.requiredReferences = plan.requiredReferences ?? []
          writeJson(artifacts.plan, plan)
          useFallback = true
        } else if (args.route === 'auto' && unsupportedComplexity) {
          const phase = summary.phases.findLast((item) => item.name === 'native-refurbish-skin')
          if (phase) {
            phase.status = 'recovered'
            phase.recoveredBy = 'fallback-patch'
          }
          summary.route.fallbackReason = 'native refurbish-skin returned UnsupportedComplexity'
          summary.recovery = {
            schemaVersion: 'pptx-nova-native-recovery/v1',
            status: 'recovered',
            eligible: true,
            reasonCode: 'native-unsupported-complexity',
            automaticFallbackAllowed: true,
            nativeReport: relativeArtifact(args.runDir, artifacts.nativeReport),
            findings: null,
          }
          summary.warnings.push(
            'Native refurbish-skin exceeded its current complexity limit; runner continued with the catalog-driven fallback patch route.',
          )
          plan = buildRecoveredFallbackPlan(args, artifacts, plan, summary.recovery)
          summary.route.planned = plan.route
          summary.requiredReferences = plan.requiredReferences ?? []
          writeJson(artifacts.plan, plan)
          useFallback = true
        } else {
          throw error
        }
      }
    }

    if (useFallback) {
      runFallback(summary, args, artifacts)
      summary.route.executed = 'fallback-patch'
    }

    const { sourceSnapshot, candidateSnapshot } = runLayoutSnapshots(
      summary,
      args,
      artifacts,
      inspect,
    )
    const semanticDiff = runSemanticDiff(summary, args, artifacts)
    const reviewEvaluation = runReviewPolicyEvaluation(summary, artifacts, candidateSnapshot)
    const findingAnalysisReport = runFindingAnalysis({
      summary,
      artifacts,
      sourceSnapshot,
      candidateSnapshot,
      semanticDiff,
      reviewEvaluation,
    })
    if (summary.layout) {
      summary.layout.topActionable = annotateTopActionable(
        summary.layout.topActionable,
        findingAnalysisReport,
      )
    }
    runFidelityGate(summary, artifacts, findingAnalysisReport)
    runPreviews(summary, args, artifacts, inspect)
    const compareReport = runRefurbishCompare(summary, args, artifacts, inspect)
    materializeContactDiff(summary, args, artifacts, compareReport)
    runRefurbishCompareGate(summary, args, artifacts)

    summary.status = 'needs-human-review'
    summary.machineGatesPassed = true
    summary.deliveryReady = false
    return finalizeRunnerSummary(summary, {
      summaryPath: artifacts.summary,
      totalMs: durationMs(runStarted),
      finalizeArtifacts: finalizeArtifactPaths,
      buildPerformance: buildPerformanceSummary,
      buildAgentSummary,
    })
  } catch (error) {
    summary.status = 'failed'
    summary.machineGatesPassed = false
    summary.deliveryReady = false
    summary.error = summarizePhaseError(error)
    finalizeRunnerSummary(summary, {
      summaryPath: artifacts.summary,
      totalMs: durationMs(runStarted),
      finalizeArtifacts: finalizeArtifactPaths,
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
  process.stdout.write(`PPTX refurbish run: ${summary.status}\n`)
  process.stdout.write(
    `- route: ${summary.route.executed || summary.route.planned || 'not-started'}\n`,
  )
  process.stdout.write(`- run dir: ${summary.runDir}\n`)
  process.stdout.write(`- output: ${summary.output}\n`)
  process.stdout.write(`- machine gates: ${summary.machineGatesPassed ? 'passed' : 'failed'}\n`)
  process.stdout.write(`- manual review: ${summary.needsHumanReview ? 'required' : 'complete'}\n`)
  if (summary.error)
    process.stdout.write(`- error: ${summary.error.phase}: ${summary.error.message}\n`)
}

let parsedArgs = null
try {
  parsedArgs = parseArgs(process.argv.slice(2))
  progressReporter = createProgressReporter({
    mode: parsedArgs.progress,
    jsonOutput: parsedArgs.json,
    context: { tool: 'cli/refurbish/run', deckkit: parsedArgs.deckkit },
  })
  const summary = runRefurbish(parsedArgs)
  if (parsedArgs.json) {
    const output = parsedArgs.jsonFull
      ? summary
      : buildRuntimeAgentResult(summary, { schemaVersion: AGENT_RESULT_SCHEMA_VERSION })
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  } else printHuman(summary)
} catch (error) {
  const summary = error.summary ?? {
    schemaVersion: 'pptx-nova-refurbish-run/v1',
    mode: 'refurbish',
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
