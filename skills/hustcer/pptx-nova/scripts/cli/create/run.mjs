#!/usr/bin/env node
import { cliPath, SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { ensureRenderContext } from '../../lib/review/render-context.mjs'
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { basename, dirname, extname, join } from 'node:path'
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
} from '../../lib/runtime/runner-runtime.mjs'
import { createProgressReporter } from '../../lib/runtime/progress.mjs'
import {
  semanticIssueValid,
  semanticValidationEvidence,
} from '../../lib/review/semantic-evidence.mjs'
import {
  canonicalCreatePreview,
  validateCreateDelivery,
} from '../../lib/create/create-delivery.mjs'
import { composeChoreography } from '../../lib/animation/animation-choreography.mjs'
import {
  designHash,
  loadDesignContract,
  checkDesignPatch,
} from '../../../assets/deckkits/shared/design-contract.mjs'
import { resolveFilesystemPath } from '../../lib/runtime/filesystem-paths.mjs'

const VALIDATE_CONTENT_SCRIPT = join(SKILL_ROOT, 'assets/deckkits/validate-content.mjs')
const BUILD_SCRIPT = cliPath('create/build.mjs')
const DESIGN_SCRIPT = cliPath('deckkits/design.mjs')
const CHECK_LOCK_SCRIPT = cliPath('create/check-lock.mjs')
const CAPABILITY_PROBE_SCRIPT = cliPath('runtime/probe.mjs')
const AGENT_SUMMARY_SCHEMA_VERSION = 'pptx-nova-agent-summary/v1'
const AGENT_RESULT_SCHEMA_VERSION = 'pptx-nova-create-result/v1'
let progressReporter = createProgressReporter({ mode: 'off' })
const { runJsonPhase, runPlainPhase, addInternalPhase, requireGate } = createRunnerRuntime({
  getProgressReporter: () => progressReporter,
})

const usage = `Usage:
  node <skill-root>/scripts/cli/create/run.mjs --deckkit <id> --content <content.json> --lock <deck_lock.json> --output <output.pptx> [options]

Options:
  --deckkit <id>          DeckKit id. Defaults to content.meta.deckkit when omitted.
  --content <path>        DeckKit content JSON.
  --lock <path>           deck_lock.json for drift checks.
  --assets <path>         Optional assets_manifest.json.
  --choreography <path>   Optional native animation/Morph operations JSON.
  --output <path>         Final PPTX published after canonical checks and actual visual review.
  --finalize              Publish the previously generated candidate without rendering again.
  --visual-review <path>  Hash-bound visual_review.json, required with --finalize.
  --run-dir <path>        Run artifact directory. Defaults to <cwd>/.pptx-nova/create-<deckkit>-<timestamp>.
  --xdoc-bin <path>       xdoc executable. Defaults to xdoc.
  --overwrite             Allow replacing an existing final output after all machine gates pass.
  --progress <mode>       Progress stream: auto|jsonl|text|off. Defaults to auto.
  --json                  Print the compact Agent result; the full summary is saved in the run directory.
  --json-full             Print the complete run summary for debugging.
  --help                  Show this help.

The runner executes validate-content, build, check-lock, dry-run, apply, vision-check,
and canonical Create rendering once. Review its PNGs, then use --finalize --visual-review
to publish the same candidate. Older runtimes retain diagnostic preview only and cannot
finalize automatically; update xdoc or follow the documented human-confirmation route.
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    content: '',
    lock: '',
    assets: '',
    choreography: '',
    output: '',
    runDir: '',
    xdocBin: 'xdoc',
    overwrite: false,
    finalize: false,
    visualReview: '',
    progress: 'auto',
    json: false,
    jsonFull: false,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--finalize') {
      args.finalize = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--json-full') {
      args.json = true
      args.jsonFull = true
    } else if (arg in valueFlags) {
      args[valueFlags[arg]] = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.content) throw new Error(`--content is required.\n\n${usage}`)
  if (!args.lock) throw new Error(`--lock is required.\n\n${usage}`)
  if (!args.output) throw new Error(`--output is required.\n\n${usage}`)
  if (args.finalize && (!args.runDir || !args.visualReview))
    throw new Error('--finalize requires --run-dir and --visual-review')
  if (args.visualReview && !args.finalize)
    throw new Error('--visual-review is only accepted with --finalize')
  return args
}

const valueFlags = {
  '--deckkit': 'deckkit',
  '--content': 'content',
  '--lock': 'lock',
  '--assets': 'assets',
  '--choreography': 'choreography',
  '--output': 'output',
  '--run-dir': 'runDir',
  '--xdoc-bin': 'xdocBin',
  '--progress': 'progress',
  '--visual-review': 'visualReview',
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function timestamp(now = new Date()) {
  const pad = (value) => String(value).padStart(2, '0')
  const millis = String(now.getMilliseconds()).padStart(3, '0')
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}${millis}`
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

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function countArray(value) {
  return Array.isArray(value) ? value.length : 0
}

function countSeverity(items, severity) {
  return (Array.isArray(items) ? items : []).filter((item) => item.severity === severity).length
}

function severityCounts(value) {
  return {
    high: Number(value?.high ?? 0),
    medium: Number(value?.medium ?? 0),
    low: Number(value?.low ?? 0),
  }
}

function summarizeApplyReport(report) {
  const visualRisks = report?.visualRisks ?? []
  const semanticIssues = report?.semanticIssues
  return {
    status: report?.status ?? '',
    warnings: countArray(report?.warnings),
    changedParts: countArray(report?.changedParts),
    opResults: countArray(report?.opResults),
    semanticEvidence: Array.isArray(semanticIssues) && semanticIssues.every(semanticIssueValid),
    semanticIssueCount: countArray(semanticIssues),
    visualRisks: {
      high: countSeverity(visualRisks, 'high'),
      medium: countSeverity(visualRisks, 'medium'),
      low: countSeverity(visualRisks, 'low'),
      total: countArray(visualRisks),
    },
    output: report?.output ?? null,
    sidecar: report?.sidecar ?? null,
    wouldWrite: report?.wouldWrite ?? null,
  }
}

function summarizeVisionReport(report) {
  const bySeverity = severityCounts(report?.summary?.bySeverity ?? report?.bySeverity)
  const semanticEvidence = semanticValidationEvidence(report)
  return {
    status: report?.status ?? '',
    issueCount: Number(report?.summary?.issueCount ?? report?.issues?.length ?? 0),
    bySeverity,
    semantic: {
      evidence: semanticEvidence.evidence,
      consistent: semanticEvidence.consistent,
      passed: semanticEvidence.passed === true,
      issueCount: semanticEvidence.issueCount,
      sourceRuleCount: semanticEvidence.sourceRuleCount,
      normalizedRuleCount: semanticEvidence.normalizedRuleCount,
    },
  }
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

function previewPageBytes(page) {
  return Number(page?.byteLength ?? page?.file?.byteLength ?? 0)
}

function previewPagePixels(page) {
  const width = Number(page?.width ?? page?.file?.width ?? 0)
  const height = Number(page?.height ?? page?.file?.height ?? 0)
  return width > 0 && height > 0 ? width * height : 0
}

function hasPathSeparator(value) {
  const text = String(value ?? '')
  return text.includes('/') || text.includes('\\')
}

function normalizeExecutablePath(value, cwd) {
  return hasPathSeparator(value) ? resolveFilesystemPath(value, cwd) : value
}

function defaultRunDir(args, cwd) {
  const deckkit = args.deckkit || 'deckkit'
  const root = join(cwd, '.pptx-nova')
  const slug = safeSlug(deckkit)
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const entropy = `${process.pid.toString(36)}-${Math.random().toString(36).slice(2, 8)}`
    const suffix = attempt === 0 ? entropy : `${entropy}-${attempt + 1}`
    const candidate = join(root, `create-${slug}-${timestamp()}-${suffix}`)
    if (!existsSync(candidate)) return candidate
  }
  throw new Error(`could not allocate a unique run directory under ${root}`)
}

function normalizeArgs(inputArgs) {
  const cwd = process.cwd()
  const content = resolveFilesystemPath(inputArgs.content, cwd)
  const contentJson = readJson(content)
  const deckkit = inputArgs.deckkit || contentJson?.meta?.deckkit || ''
  const args = {
    ...inputArgs,
    deckkit,
    content,
    lock: resolveFilesystemPath(inputArgs.lock, cwd),
    assets: inputArgs.assets ? resolveFilesystemPath(inputArgs.assets, cwd) : '',
    choreography: inputArgs.choreography ? resolveFilesystemPath(inputArgs.choreography, cwd) : '',
    visualReview: inputArgs.visualReview ? resolveFilesystemPath(inputArgs.visualReview, cwd) : '',
    output: resolveFilesystemPath(inputArgs.output, cwd),
    xdocBin: normalizeExecutablePath(inputArgs.xdocBin, cwd),
  }
  args.runDir = inputArgs.runDir
    ? resolveFilesystemPath(inputArgs.runDir, cwd)
    : defaultRunDir(args, cwd)
  return { args, contentJson }
}

function validatePaths(args) {
  if (!args.deckkit) throw new Error('--deckkit is required when content.meta.deckkit is missing')
  if (
    args.choreography &&
    [...Object.values(artifactPaths(args.runDir)), args.output].includes(args.choreography)
  )
    throw new Error('Choreography must not use a reserved run artifact or final output path')
  for (const [label, path] of [
    ['content', args.content],
    ['deck lock', args.lock],
    ...(args.assets ? [['assets manifest', args.assets]] : []),
    ...(args.choreography ? [['choreography', args.choreography]] : []),
  ]) {
    if (!existsSync(path) || !statSync(path).isFile()) {
      throw new Error(`${label} does not exist or is not a file: ${path}`)
    }
  }
  if (extname(args.output).toLowerCase() !== '.pptx') {
    throw new Error(`--output must be a .pptx file: ${args.output}`)
  }
  if (!existsSync(dirname(args.output))) {
    throw new Error(`final output directory does not exist: ${dirname(args.output)}`)
  }
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(
      `final output already exists; pass --overwrite only when replacement is intended: ${args.output}`,
    )
  }
}

function artifactPaths(runDir) {
  return {
    renderContext: join(runDir, 'render-context.json'),
    capabilities: join(runDir, 'xdoc-capabilities.json'),
    validation: join(runDir, 'validate-content.json'),
    patch: join(runDir, 'patch.json'),
    deckkitPatch: join(runDir, 'deckkit.patch.json'),
    quality: join(runDir, 'quality.json'),
    designPlan: join(runDir, 'design-plan.json'),
    designContract: join(runDir, 'design-contract.json'),
    designCheck: join(runDir, 'design-check.json'),
    designReadback: join(runDir, 'design-readback.json'),
    designSemantic: join(runDir, 'design-semantic.json'),
    designInspect: join(runDir, 'design-inspect.json'),
    designModel: join(runDir, 'design-model.json'),
    lockCheck: join(runDir, 'check-lock.json'),
    dryRun: join(runDir, 'dry-run.json'),
    apply: join(runDir, 'apply.json'),
    vision: join(runDir, 'vision.json'),
    candidate: join(runDir, 'candidate.pptx'),
    previews: join(runDir, 'previews'),
    previewReport: join(runDir, 'preview.json'),
    contactSheet: join(runDir, 'previews', 'contact-sheet.png'),
    summary: join(runDir, 'create-run-summary.json'),
    canonicalDir: join(runDir, 'visual-evidence'),
    canonicalManifest: join(runDir, 'visual-evidence', 'manifest.json'),
    visualGate: join(runDir, 'visual-evidence-gate.json'),
    reviewGallery: join(runDir, 'visual-evidence', 'review.html'),
    binding: join(runDir, 'create-binding.json'),
  }
}

function initialSummary(args, content, artifacts) {
  return {
    schemaVersion: 'pptx-nova-create-run/v1',
    status: 'running',
    mode: 'create',
    machineGatesPassed: false,
    deliveryReady: false,
    needsHumanReview: true,
    deckkit: args.deckkit,
    content: args.content,
    deckLock: args.lock,
    assetsManifest: args.assets || null,
    choreography: args.choreography || null,
    output: args.output,
    runDir: args.runDir,
    slideCount: Array.isArray(content?.slides) ? content.slides.length : null,
    artifacts: Object.fromEntries(Object.entries(artifacts).map(([key, path]) => [key, path])),
    phases: [],
    gates: [],
    review: {
      required: true,
      completed: false,
      instructions:
        'Review contact-sheet.png and suspicious full-size PNGs before treating the deck as visually delivered.',
    },
    requiredReferences: [
      {
        path: 'references/create/design-quality.md',
        section: 'Recorded design judgment',
        reason:
          'Every Create requires rendered design observations, including short Express decks.',
      },
      ...(content?.meta?.deckProfile === 'animation-corpus'
        ? [
            {
              path: 'references/content/animations.md',
              section: 'Animation corpus',
              reason: 'Review declared cases, actual timing and native playback evidence.',
            },
          ]
        : Array.isArray(content?.slides) && content.slides.length >= 6
          ? [
              {
                path: 'references/create/narrative-quality.md',
                section: 'Narrative Gate',
                reason:
                  'The generated deck contains at least six slides and requires narrative review.',
              },
            ]
          : []),
    ],
    warnings: [],
    error: null,
  }
}

function finalizeArtifactPaths(summary, summaryPath) {
  summary.artifacts = Object.fromEntries(
    Object.entries(summary.artifacts).map(([key, path]) => [
      key,
      key === 'summary' || (path && existsSync(path)) ? path : null,
    ]),
  )
  summary.artifacts.summary = summaryPath
}

function buildAgentSummary(summary) {
  const validate = gateByName(summary, 'validate-content')
  const build = gateByName(summary, 'build')
  const checkLock = gateByName(summary, 'check-lock')
  const dryRun = gateByName(summary, 'dry-run')
  const apply = gateByName(summary, 'apply')
  const vision = gateByName(summary, 'vision-check')
  const designReadback = gateByName(summary, 'design-readback')
  const preview = gateByName(summary, 'png-previews') ?? gateByName(summary, 'canonical-create')
  return {
    schemaVersion: AGENT_SUMMARY_SCHEMA_VERSION,
    mode: 'create',
    status: summary.status,
    machineGatesPassed: Boolean(summary.machineGatesPassed),
    deliveryReady: Boolean(summary.deliveryReady),
    needsHumanReview: Boolean(summary.needsHumanReview),
    decision: summary.deliveryReady
      ? 'deliver'
      : summary.machineGatesPassed
        ? 'continue-to-human-review'
        : 'stop-and-fix',
    deckkit: summary.deckkit,
    slideCount: summary.slideCount,
    gates: {
      validateContent: { gate: gateStatus(validate), errors: validate?.errors ?? null },
      build: { gate: gateStatus(build), patchOps: build?.patchOps ?? null },
      checkLock: {
        gate: gateStatus(checkLock),
        errors: checkLock?.errors ?? null,
        warnings: checkLock?.warnings ?? null,
      },
      dryRun: {
        gate: gateStatus(dryRun),
        status: dryRun?.status ?? null,
        high: dryRun?.visualRisks?.high ?? null,
        medium: dryRun?.visualRisks?.medium ?? null,
        semanticEvidence: dryRun?.semanticEvidence ?? null,
        semanticIssues: dryRun?.semanticIssueCount ?? null,
      },
      apply: {
        gate: gateStatus(apply),
        status: apply?.status ?? null,
        outputExists: apply?.outputExists ?? null,
        semanticEvidence: apply?.semanticEvidence ?? null,
        semanticIssues: apply?.semanticIssueCount ?? null,
      },
      vision: {
        gate: gateStatus(vision),
        status: vision?.status ?? null,
        high: vision?.bySeverity?.high ?? null,
        medium: vision?.bySeverity?.medium ?? null,
        semanticEvidence: vision?.semantic?.evidence ?? null,
        semanticConsistent: vision?.semantic?.consistent ?? null,
        semanticPassed: vision?.semantic?.passed ?? null,
        semanticIssues: vision?.semantic?.issueCount ?? null,
        semanticSourceRules: vision?.semantic?.sourceRuleCount ?? null,
        semanticNormalizedRules: vision?.semantic?.normalizedRuleCount ?? null,
      },
      preview: {
        gate: gateStatus(preview),
        pages: preview?.count ?? null,
        expectedPages: preview?.expectedCount ?? null,
        contactSheetBytes: preview?.contactSheetBytes ?? null,
      },
      ...(designReadback
        ? {
            designReadback: {
              gate: gateStatus(designReadback),
              contractHash: designReadback.contractHash,
              checkedObjects: designReadback.checkedObjects,
              checkedCharts: designReadback.checkedCharts,
              checkedTables: designReadback.checkedTables,
            },
          }
        : {}),
    },
    artifacts: {
      summary: summary.artifacts.summary,
      candidate: summary.artifacts.candidate,
      patch: summary.artifacts.patch,
      quality: summary.artifacts.quality,
      dryRun: summary.artifacts.dryRun,
      apply: summary.artifacts.apply,
      vision: summary.artifacts.vision,
      previewReport: summary.artifacts.previewReport,
      contactSheet: summary.artifacts.contactSheet,
      canonicalManifest: summary.artifacts.canonicalManifest,
      reviewGallery: summary.artifacts.reviewGallery,
      ...(designReadback
        ? {
            designContract: summary.artifacts.designContract,
            designPlan: summary.artifacts.designPlan,
            designCheck: summary.artifacts.designCheck,
            designReadback: summary.artifacts.designReadback,
            ...(existsSync(summary.artifacts.designSemantic)
              ? { designSemantic: summary.artifacts.designSemantic }
              : {}),
          }
        : {}),
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
  const previewPhase = summary.phases.find((phase) => phase.name === 'preview-render')
  const previewRenderInvocations = previewPhase ? 1 : 0
  const previewSlideCount = Number(previewPhase?.slideCount ?? 0)
  const estimatedRenderedPixels = Number(previewPhase?.estimatedRenderedPixels ?? 0)
  return buildRuntimePerformanceSummary(summary, totalMs, {
    renderPhaseNames: ['preview-render'],
    render: {
      previewRenderInvocations,
      previewSlideCount,
      estimatedRenderedPixels,
    },
    budget: {
      baselineInvocations: previewRenderInvocations ? 1 : 0,
      actualInvocations: previewRenderInvocations,
      withinBaseline: previewRenderInvocations <= 1,
      baselineEstimatedPixels: estimatedRenderedPixels,
      actualEstimatedPixels: estimatedRenderedPixels,
      withinPixelBaseline: true,
    },
  })
}

function runCapabilityProbe(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'xdoc-capability-probe',
    bin: process.execPath,
    args: [
      CAPABILITY_PROBE_SCRIPT,
      '--xdoc-bin',
      args.xdocBin,
      '--require-command',
      'pptx.apply',
      '--require-command',
      'pptx.vision-check',
      '--require-command',
      'pptx.preview',
      '--json',
    ],
    artifact: artifacts.capabilities,
  })
  if (report.status !== 'ready') {
    summary.warnings.push(
      'xdoc capability schema is degraded; runner continued and will rely on direct command results as gate evidence.',
    )
  }
  summary.canonicalCreateAvailable =
    report.capabilities?.visualAudit?.modes?.includes('create') === true
}

function runValidation(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'validate-content',
    bin: process.execPath,
    args: [
      VALIDATE_CONTENT_SCRIPT,
      args.content,
      '--deckkit',
      args.deckkit,
      '--mode',
      'delivery',
      '--json',
    ],
    artifact: artifacts.validation,
  })
  requireGate(summary, 'validate-content', report?.valid === true, {
    errors: countArray(report?.errors),
    warnings: countArray(report?.warnings),
    fitDiagnostics: countArray(report?.fitDiagnostics),
    message: 'content validation must pass in delivery mode',
  })
  for (const warning of report?.warnings ?? []) {
    summary.warnings.push(`validate-content ${warning.type ?? 'warning'}: ${warning.message ?? ''}`)
  }
}

function runBuild(summary, args, artifacts) {
  const buildArgs = [BUILD_SCRIPT, '--deckkit', args.deckkit]
  if (args.assets) buildArgs.push('--assets', args.assets)
  buildArgs.push(args.content, '-o', artifacts.patch, '--quality-json', artifacts.quality)
  runPlainPhase(summary, {
    name: 'build',
    bin: process.execPath,
    args: buildArgs,
  })
  const patch = readJson(artifacts.patch)
  const quality = readJson(artifacts.quality)
  requireGate(summary, 'build', Array.isArray(patch?.ops) && patch.ops.length > 0, {
    patchOps: patch?.ops?.length ?? 0,
    qualityStatus: quality?.status ?? null,
    message: 'DeckKit build must emit a patch with at least one op',
  })
  requireGate(summary, 'build-quality', quality?.status !== 'error', {
    status: quality?.status ?? null,
    errors: countArray(quality?.errors),
    warnings: countArray(quality?.warnings),
    message: 'Deck quality assessment must not be error',
  })
  for (const warning of quality?.warnings ?? []) {
    summary.warnings.push(`build-quality: ${warning.message ?? warning}`)
  }
  if (args.choreography) {
    const combined = composeChoreography({
      basePatch: patch,
      choreography: readJson(args.choreography),
      slideCount: summary.slideCount,
    })
    copyFileSync(artifacts.patch, artifacts.deckkitPatch)
    writeFileSync(artifacts.patch, JSON.stringify(combined, null, 2) + '\n')
    if (existsSync(artifacts.designPlan)) {
      const plan = readJson(artifacts.designPlan)
      plan.patchHash = designHash(combined)
      const check = checkDesignPatch(loadDesignContract(args.deckkit), combined)
      requireGate(summary, 'design-composition', check.status === 'pass', {
        message: 'Composed operations must preserve the design contract',
      })
      writeFileSync(artifacts.designPlan, JSON.stringify(plan, null, 2) + '\n')
      writeFileSync(artifacts.designCheck, JSON.stringify(check, null, 2) + '\n')
    }
  }
}

function runCheckLock(summary, args, artifacts) {
  const checkArgs = [
    CHECK_LOCK_SCRIPT,
    '--lock',
    args.lock,
    '--content',
    args.content,
    '--patch',
    artifacts.patch,
    '--json',
  ]
  if (args.assets) checkArgs.push('--assets', args.assets)
  const report = runJsonPhase(summary, {
    name: 'check-lock',
    bin: process.execPath,
    args: checkArgs,
    artifact: artifacts.lockCheck,
  })
  requireGate(summary, 'check-lock', report?.valid === true, {
    errors: Number(report?.summary?.errors ?? report?.errors?.length ?? 0),
    warnings: Number(report?.summary?.warnings ?? report?.warnings?.length ?? 0),
    message: 'deck_lock/content/patch drift check must pass',
  })
  for (const warning of report?.warnings ?? []) {
    summary.warnings.push(`check-lock ${warning.code ?? 'warning'}: ${warning.message ?? ''}`)
  }
}

function runDryRun(summary, args, artifacts) {
  const applyArgs = [
    'pptx',
    'apply',
    '-p',
    artifacts.patch,
    '-o',
    artifacts.candidate,
    '--overwrite',
  ]
  if (args.assets) applyArgs.push('--asset-root', dirname(args.assets))
  applyArgs.push('--dry-run', '--json')
  const report = runJsonPhase(summary, {
    name: 'dry-run',
    bin: args.xdocBin,
    args: applyArgs,
    artifact: artifacts.dryRun,
  })
  const dryRun = summarizeApplyReport(report)
  requireGate(
    summary,
    'dry-run',
    report?.schemaVersion === 'pptx-dry-run/v1' &&
      dryRun.status === 'success' &&
      dryRun.visualRisks.high === 0 &&
      dryRun.visualRisks.medium === 0 &&
      dryRun.semanticEvidence &&
      dryRun.semanticIssueCount === 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      ...dryRun,
      message:
        'dry-run must succeed with no high/medium visual risks and explicit zero semantic issues',
    },
  )
}

function runApply(summary, args, artifacts) {
  rmSync(artifacts.candidate, { force: true })
  const applyArgs = [
    'pptx',
    'apply',
    '-p',
    artifacts.patch,
    '-o',
    artifacts.candidate,
    '--overwrite',
  ]
  if (args.assets) applyArgs.push('--asset-root', dirname(args.assets))
  applyArgs.push('--json')
  const report = runJsonPhase(summary, {
    name: 'apply',
    bin: args.xdocBin,
    args: applyArgs,
    artifact: artifacts.apply,
  })
  const apply = summarizeApplyReport(report)
  const outputBytes = existsSync(artifacts.candidate) ? statSync(artifacts.candidate).size : 0
  requireGate(
    summary,
    'apply',
    report?.schemaVersion === 'pptx-apply/v1' &&
      apply.status === 'success' &&
      apply.visualRisks.high === 0 &&
      apply.visualRisks.medium === 0 &&
      apply.semanticEvidence &&
      apply.semanticIssueCount === 0 &&
      outputBytes > 0,
    {
      schemaVersion: report?.schemaVersion ?? '',
      ...apply,
      outputExists: outputBytes > 0,
      outputBytes,
      message:
        'apply must succeed, keep high/medium visual risks and semantic issues at zero, and write candidate.pptx',
    },
  )
}

function runDesignReadback(summary, args, artifacts) {
  if (!existsSync(artifacts.designPlan)) return
  const plan = readJson(artifacts.designPlan)
  const patch = readJson(artifacts.patch)
  runJsonPhase(summary, {
    name: 'design-inspect',
    bin: args.xdocBin,
    args: ['pptx', 'inspect', artifacts.candidate, '--json'],
    artifact: artifacts.designInspect,
  })
  const checkArgs = [
    DESIGN_SCRIPT,
    '--deckkit',
    args.deckkit,
    '--plan',
    artifacts.designPlan,
    '--patch',
    artifacts.patch,
    '--inspect',
    artifacts.designInspect,
  ]
  if (patch.ops.some((op) => ['add-chart', 'add-table'].includes(op.op))) {
    runPlainPhase(summary, {
      name: 'design-data-projection',
      bin: args.xdocBin,
      args: ['convert', artifacts.candidate, '--to', 'json', '--output', artifacts.designModel],
    })
    checkArgs.push('--model', artifacts.designModel)
  }
  const result = runJsonPhase(summary, {
    name: 'design-readback',
    bin: process.execPath,
    args: checkArgs,
    artifact: artifacts.designReadback,
  })
  requireGate(summary, 'design-readback', result?.status === 'pass', {
    contractHash: plan.contractHash,
    checkedObjects: result?.checkedObjects ?? null,
    checkedCharts: result?.checkedCharts ?? null,
    checkedTables: result?.checkedTables ?? null,
    message: 'Applied objects and native chart data must match the design plan',
  })
  if (patch.ops.some((op) => op.op === 'add-table')) {
    const audit = runJsonPhase(summary, {
      name: 'design-semantic',
      bin: process.execPath,
      args: [
        cliPath('review/semantic-audit.mjs'),
        '--deck-lock',
        args.lock,
        '--patch',
        artifacts.patch,
        '--final-inspect',
        artifacts.designInspect,
        '--output',
        artifacts.designSemantic,
        '--json',
      ],
      artifact: artifacts.designSemantic,
    })
    requireGate(
      summary,
      'design-semantic',
      audit.schemaVersion === 'pptx-nova-semantic-audit/v1' &&
        audit.status !== 'fail' &&
        audit.summary.errors === 0,
      {
        message: 'Native tables require semantic metadata and object checks',
        warnings: audit.summary.warnings,
      },
    )
    if (audit.summary.warnings)
      summary.warnings.push(
        `design-semantic: ${audit.summary.warnings} review warnings; inspect design-semantic.json`,
      )
  }
}

function runVision(summary, args, artifacts) {
  const report = runJsonPhase(summary, {
    name: 'vision-check',
    bin: args.xdocBin,
    args: ['pptx', 'vision-check', artifacts.candidate, '--json'],
    artifact: artifacts.vision,
  })
  const vision = summarizeVisionReport(report)
  requireGate(
    summary,
    'vision-check',
    report?.schemaVersion === 'pptx-vision/v1' &&
      (vision.status === 'pass' || vision.status === 'success') &&
      vision.bySeverity.high === 0 &&
      vision.bySeverity.medium === 0 &&
      vision.semantic.evidence &&
      vision.semantic.consistent &&
      vision.semantic.passed,
    {
      schemaVersion: report?.schemaVersion ?? '',
      ...vision,
      message:
        'vision-check must pass with high=0, medium=0, and a consistent passing semantic summary',
    },
  )
}

function runPreview(summary, args, artifacts) {
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
      '--overwrite',
      '--json',
    ],
    artifact: artifacts.previewReport,
  })
  const contactSheetName = basename(artifacts.contactSheet)
  const files = listPngFiles(artifacts.previews, new Set([contactSheetName]))
  const contactSheetBytes = existsSync(artifacts.contactSheet)
    ? statSync(artifacts.contactSheet).size
    : 0
  const manifestPages = Array.isArray(report?.pages) ? report.pages.length : 0
  const manifestPagesNonEmpty =
    !Array.isArray(report?.pages) || report.pages.every((page) => previewPageBytes(page) > 0)
  const phase = summary.phases.findLast((item) => item.name === 'preview-render')
  if (phase) {
    phase.slideCount = manifestPages
    phase.estimatedRenderedPixels = (report?.pages ?? []).reduce(
      (pixels, page) => pixels + previewPagePixels(page),
      0,
    )
  }
  requireGate(
    summary,
    'png-previews',
    report?.schemaVersion === 'pptx-preview/v1' &&
      report?.status === 'success' &&
      summary.slideCount !== null &&
      files.length === summary.slideCount &&
      files.length > 0 &&
      files.every((file) => file.bytes > 0) &&
      manifestPages === summary.slideCount &&
      manifestPagesNonEmpty &&
      contactSheetBytes > 0,
    {
      manifestStatus: report?.status ?? null,
      count: files.length,
      expectedCount: summary.slideCount,
      manifestPages,
      allNonEmpty: files.every((file) => file.bytes > 0),
      manifestPagesNonEmpty,
      contactSheetBytes,
      files: files.map((file) => ({ name: file.name, bytes: file.bytes })),
      message:
        'preview must emit a successful manifest, one non-empty PNG per slide, and a non-empty contact sheet',
    },
  )
}

function publishCandidate(summary, args, artifacts) {
  if (!existsSync(artifacts.candidate) || statSync(artifacts.candidate).size === 0) {
    throw new PhaseFailure('publish', 'candidate PPTX is missing or empty')
  }
  const tempOutput = join(
    dirname(args.output),
    `.${basename(args.output)}.pptx-nova-${process.pid}-${Date.now()}.tmp`,
  )
  const start = performance.now()
  try {
    copyFileSync(artifacts.candidate, tempOutput)
    renameSync(tempOutput, args.output)
  } finally {
    rmSync(tempOutput, { force: true })
  }
  const bytes = statSync(args.output).size
  addInternalPhase(summary, 'publish', 'passed', {
    durationMs: durationMs(start),
    output: args.output,
    bytes,
  })
  requireGate(summary, 'published-output', bytes > 0, {
    output: args.output,
    bytes,
    message: 'Published output is empty',
  })
}

function runCreate(inputArgs) {
  const runStarted = performance.now()
  const { args, contentJson } = normalizeArgs(inputArgs)
  validatePaths(args)
  mkdirSync(args.runDir, { recursive: true })
  ensureRenderContext(args.runDir)
  const artifacts = artifactPaths(args.runDir)
  if (args.finalize) {
    const summary = readJson(artifacts.summary)
    validateCreateDelivery(summary, args, artifacts)
    publishCandidate(summary, args, artifacts)
    summary.status = 'delivered'
    summary.deliveryReady = true
    summary.needsHumanReview = false
    summary.review = { ...summary.review, completed: true, artifact: args.visualReview }
    return finalizeRunnerSummary(summary, {
      summaryPath: artifacts.summary,
      totalMs: Number(summary.performance?.totalMs ?? 0) + durationMs(runStarted),
      finalizeArtifacts: finalizeArtifactPaths,
      buildPerformance: buildPerformanceSummary,
      buildAgentSummary,
    })
  }
  if (existsSync(artifacts.canonicalManifest))
    throw new Error(
      'This run already contains canonical evidence; use --finalize or a fresh run directory',
    )
  const summary = initialSummary(args, contentJson, artifacts)

  try {
    runCapabilityProbe(summary, args, artifacts)
    runValidation(summary, args, artifacts)
    runBuild(summary, args, artifacts)
    runCheckLock(summary, args, artifacts)
    runDryRun(summary, args, artifacts)
    runApply(summary, args, artifacts)
    runDesignReadback(summary, args, artifacts)
    runVision(summary, args, artifacts)
    if (summary.canonicalCreateAvailable) {
      canonicalCreatePreview(summary, args, artifacts, runJsonPhase)
      requireGate(summary, 'canonical-create', true, {
        count: summary.slideCount,
        expectedCount: summary.slideCount,
        message: 'Candidate checks passed; actual visual review remains required',
      })
    } else {
      runPreview(summary, args, artifacts)
      summary.warnings.push(
        'Runtime does not disclose Create visual policy; diagnostic preview is not delivery authorization. Update xdoc or obtain actual human confirmation through the canonical legacy flow.',
      )
    }

    summary.status = summary.canonicalCreateAvailable ? 'needs-visual-review' : 'needs-human-review'
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
  }
}

function printHuman(summary) {
  process.stdout.write(`PPTX create run: ${summary.status}\n`)
  process.stdout.write(`- deckkit: ${summary.deckkit}\n`)
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
    context: { tool: 'cli/create/run', deckkit: parsedArgs.deckkit || 'from-content' },
  })
  const summary = runCreate(parsedArgs)
  if (parsedArgs.json) {
    const output = parsedArgs.jsonFull
      ? summary
      : buildRuntimeAgentResult(summary, { schemaVersion: AGENT_RESULT_SCHEMA_VERSION })
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  } else printHuman(summary)
} catch (error) {
  const summary = error.summary ?? {
    schemaVersion: 'pptx-nova-create-run/v1',
    mode: 'create',
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
