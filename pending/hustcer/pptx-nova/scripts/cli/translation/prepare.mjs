#!/usr/bin/env node
import { cliPath } from '../../lib/runtime/skill-paths.mjs'
import { spawnSync } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { basename, dirname, extname, join, resolve } from 'node:path'
import { performance } from 'node:perf_hooks'
import { readPptxPackage } from '../../lib/pptx/pptx-package.mjs'

import { assertNewOrPreProbedRunDir, isNewOrPreProbedRunDir } from '../../lib/runtime/run-dir.mjs'
import {
  buildTranslationConstraints,
  normalizeTranslationGlossary,
  validateTranslationConstraints,
} from '../../lib/translation/translation-constraints.mjs'
import {
  applyMemoryFill,
  buildMemoryFillView,
  buildTranslationMemory,
  expandReviewInventory,
  materializeTranslations,
  mergeTranslationMemoryAnchorDrafts,
  mergeTranslationMemoryRepairs,
} from '../../lib/translation/translation-memory.mjs'
import { createProgressReporter } from '../../lib/runtime/progress.mjs'

const PROBE_SCRIPT = cliPath('runtime/probe.mjs')
const CLASSIFY_SCRIPT = cliPath('translation/classify-review-units.mjs')
const SUMMARY_SCHEMA = 'pptx-nova-translation-prepare/v1'
const RESULT_SCHEMA = 'pptx-nova-translation-prepare-result/v1'
// Targets that typically render 20-25% longer than English source text; used
// only to surface a compact-wording prior before the first apply round.
const LONGER_TARGET_LANGS = new Set(['de', 'fr', 'es', 'it', 'pt', 'ru', 'nl', 'pl'])

const usage = `Usage:
  node <skill-root>/scripts/cli/translation/prepare.mjs --source <source.pptx> --source-lang <multi|zh|en> --target-lang <lang> --run-dir <run-dir> [options]

Options:
  --review-decisions <path>  Optional bound language-review decisions.
  --memory <path>            Translation memory to consume; defaults to run-dir/translation-memory.json.
  --glossary <path>          Optional pptx-nova-translation-glossary/v1 project glossary.
                             It is normalized and snapshotted into the run before translation.
  --prompt-file <path>       Read the original user prompt from outside the run directory and
                             archive it as run-dir/prompt.txt after the fresh-run guard passes.
  --fill <path>              Apply-time JSONL overlay ({memoryId, sourceText?, targetText} per line)
                             merged into the memory; supports partial/incremental wording revisions
                             without touching the full memory JSON. Requires --apply.
  --expand-review <name>     Persist one lazy review partition: languageUncertain,
                             shared, embeddedWorkbook, or other.
  --resume-stage review      Reuse the bound source scan to expand one review partition after
                             needs-translations; requires --expand-review and does not rescan or
                             modify translation memory.
  --output-candidate <path>  Prepared stable candidate; defaults to run-dir/candidate-prepared.pptx.
  --apply                    Materialize translations, plan, dry-run, and apply all generated artifacts.
  --xdoc-bin <path>          xdoc executable. Defaults to xdoc.
  --overwrite                Replace current-run generated outputs intentionally.
  --progress <mode>          Progress stream: auto|jsonl|text|off. Defaults to auto.
  --json                     Print compact Agent result.
  --json-full                Print the complete persisted run summary.
  --help                     Show this help.

Without --apply the runner scans/classifies and creates a deduplicated translation-memory template
plus a compact translation-memory.fill.jsonl view. Fill targetText in the fill view (or directly in
the memory JSON) and required per-unit review overrides, then rerun the same run directory with
--apply [--fill <fill.jsonl>].
`

const valueFlags = {
  '--source': 'source',
  '--source-lang': 'sourceLang',
  '--target-lang': 'targetLang',
  '--run-dir': 'runDir',
  '--review-decisions': 'reviewDecisions',
  '--memory': 'memory',
  '--glossary': 'glossary',
  '--prompt-file': 'promptFile',
  '--fill': 'fill',
  '--expand-review': 'expandReview',
  '--resume-stage': 'resumeStage',
  '--output-candidate': 'outputCandidate',
  '--xdoc-bin': 'xdocBin',
  '--progress': 'progress',
}

function parseArgs(argv) {
  const args = {
    source: '',
    sourceLang: '',
    targetLang: '',
    runDir: '',
    reviewDecisions: '',
    memory: '',
    memoryExplicit: false,
    glossary: '',
    promptFile: '',
    fill: '',
    expandReview: '',
    resumeStage: '',
    outputCandidate: '',
    xdocBin: 'xdoc',
    apply: false,
    overwrite: false,
    progress: 'auto',
    json: false,
    jsonFull: false,
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--apply') args.apply = true
    else if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else if (arg === '--json-full') {
      args.json = true
      args.jsonFull = true
    } else {
      const key = valueFlags[arg]
      if (!key) throw new Error(`Unknown option: ${arg}\n\n${usage}`)
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
      args[key] = value
      if (key === 'memory') args.memoryExplicit = true
      index += 1
    }
  }
  for (const key of ['source', 'sourceLang', 'targetLang', 'runDir']) {
    if (!args[key])
      throw new Error(`--${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)} is required`)
  }
  if (!['multi', 'zh', 'en'].includes(args.sourceLang)) {
    throw new Error('--source-lang must be multi, zh, or en')
  }
  if (
    args.expandReview &&
    !['languageUncertain', 'shared', 'embeddedWorkbook', 'other'].includes(args.expandReview)
  ) {
    throw new Error('--expand-review must be languageUncertain, shared, embeddedWorkbook, or other')
  }
  if (args.resumeStage && args.resumeStage !== 'review') {
    throw new Error('--resume-stage currently supports only review')
  }
  if (args.resumeStage === 'review' && !args.expandReview) {
    throw new Error('--resume-stage review requires --expand-review <partition>')
  }
  if (
    args.resumeStage === 'review' &&
    (args.apply ||
      args.reviewDecisions ||
      args.fill ||
      args.glossary ||
      args.promptFile ||
      args.memoryExplicit)
  ) {
    throw new Error(
      '--resume-stage review cannot be combined with --apply, --review-decisions, --fill, --memory, --glossary, or --prompt-file',
    )
  }
  const cwd = process.cwd()
  args.source = resolve(cwd, args.source)
  args.runDir = resolve(cwd, args.runDir)
  args.reviewDecisions = args.reviewDecisions ? resolve(cwd, args.reviewDecisions) : ''
  args.glossary = args.glossary ? resolve(cwd, args.glossary) : ''
  args.promptFile = args.promptFile ? resolve(cwd, args.promptFile) : ''
  args.fill = args.fill ? resolve(cwd, args.fill) : ''
  if (args.fill && !args.apply) {
    throw new Error('--fill requires --apply; the fill overlay is merged at apply time')
  }
  args.memory = args.memory
    ? resolve(cwd, args.memory)
    : join(args.runDir, 'translation-memory.json')
  args.outputCandidate = args.outputCandidate
    ? resolve(cwd, args.outputCandidate)
    : join(args.runDir, 'candidate-prepared.pptx')
  args.xdocBin = /[\\/]/.test(args.xdocBin) ? resolve(cwd, args.xdocBin) : args.xdocBin
  return args
}

function artifactsFor(args) {
  return {
    capabilities: join(args.runDir, 'xdoc-capabilities.json'),
    prompt: join(args.runDir, 'prompt.txt'),
    scan: join(args.runDir, 'i18n-scan-source.json'),
    reviewDecisionsTemplate: join(args.runDir, 'i18n-review-decisions.template.json'),
    classifiedScan: join(args.runDir, 'i18n-scan-classified.json'),
    classificationReport: join(args.runDir, 'i18n-review-classification.json'),
    memory: args.memory,
    memoryFill: join(args.runDir, 'translation-memory.fill.jsonl'),
    memoryFilled: join(args.runDir, 'translation-memory.filled.json'),
    anchorDraftMemory: join(args.runDir, 'translation-memory.anchor-draft.json'),
    glossary: join(args.runDir, 'translation-glossary.json'),
    constraints: join(args.runDir, 'translation-constraints.json'),
    constraintsCheck: join(args.runDir, 'translation-constraints-check.json'),
    reviewInventory: args.expandReview
      ? join(args.runDir, `review-inventory-${args.expandReview}.json`)
      : null,
    reviewExpansionSummary: args.expandReview
      ? join(args.runDir, `review-expansion-${args.expandReview}-summary.json`)
      : null,
    memoryRepair: nextRepairArtifactPath(args),
    translations: join(args.runDir, 'translations.json'),
    translationsBeforeAnchorDraft: join(args.runDir, 'translations.before-anchor-draft.json'),
    anchorDraft: join(args.runDir, 'i18n-anchor-draft.json'),
    plan: join(args.runDir, 'i18n-plan.json'),
    planBeforeAnchorDraft: join(args.runDir, 'i18n-plan.before-anchor-draft.json'),
    textPlan: join(args.runDir, 'i18n-text-plan-input.json'),
    replaceText: join(args.runDir, 'replace-text-input.json'),
    replaceChartText: join(args.runDir, 'replace-chart-text-input.json'),
    patch: join(args.runDir, 'patch.json'),
    chartDryRun: join(args.runDir, 'replace-chart-text-dry-run.json'),
    chartApply: join(args.runDir, 'replace-chart-text.json'),
    replaceTextReport: join(args.runDir, 'replace-text.json'),
    patchDryRun: join(args.runDir, 'patch-dry-run.json'),
    patchApply: join(args.runDir, 'patch-apply.json'),
    candidate: args.outputCandidate,
    summary: join(args.runDir, 'translation-prepare-summary.json'),
  }
}

function sha256(path) {
  return `sha256:${createHash('sha256').update(readFileSync(path)).digest('hex')}`
}

function pathIdentity(path) {
  const resolved = resolve(path)
  if (!existsSync(resolved)) return { path: resolved, device: null, inode: null }
  const state = statSync(resolved)
  return { path: realpathSync(resolved), device: state.dev, inode: state.ino }
}

function sameIdentity(left, right) {
  return (
    left.path === right.path ||
    (left.device !== null &&
      right.device !== null &&
      left.device === right.device &&
      left.inode === right.inode)
  )
}

// Each targetSegments repair round writes a fresh scaffold file: the file the
// agent filled and passed back via --memory is a read-only input, so the next
// scaffold must never resolve to it or to any earlier round's file.
function nextRepairArtifactPath(args) {
  const memoryIdentity = pathIdentity(args.memory)
  for (let round = 1; round <= 20; round += 1) {
    const name =
      round === 1 ? 'translation-memory.repair.json' : `translation-memory.repair-${round}.json`
    const candidate = join(args.runDir, name)
    if (existsSync(candidate)) continue
    if (sameIdentity(pathIdentity(candidate), memoryIdentity)) continue
    return candidate
  }
  throw new Error(
    'too many translation-memory repair rounds in this run directory; start a fresh preparation run',
  )
}

function readJson(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  return JSON.parse(readFileSync(path, 'utf8'))
}

function supportsPptxSubcommand(artifacts, name) {
  if (!existsSync(artifacts.capabilities)) return false
  const capabilities = readJson(artifacts.capabilities, 'xdoc capabilities')
  return capabilities?.capabilities?.pptxSubcommands?.includes(name) === true
}

function writeJson(path, value, overwrite = false) {
  if (existsSync(path) && !overwrite) throw new Error(`Output already exists: ${path}`)
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function sameJson(left, right) {
  return JSON.stringify(left) === JSON.stringify(right)
}

function archivePrompt(args, artifacts, summary, reporter) {
  if (!args.promptFile) return
  phase(summary, reporter, 'prompt-archive', () => {
    const prompt = readFileSync(args.promptFile)
    if (existsSync(artifacts.prompt)) {
      const archived = readFileSync(artifacts.prompt)
      if (!archived.equals(prompt)) {
        throw new Error(
          `archived prompt differs from --prompt-file; keep ${artifacts.prompt} unchanged and start a fresh run to bind a different prompt`,
        )
      }
      return
    }
    writeFileSync(artifacts.prompt, prompt)
  })
}

function bindGlossary(args, artifacts, summary, reporter) {
  const supplied = args.glossary
    ? normalizeTranslationGlossary(readJson(args.glossary, 'translation glossary'), {
        targetLang: args.targetLang,
      })
    : null
  let bound = null
  phase(summary, reporter, 'translation-glossary-bind', () => {
    if (existsSync(artifacts.glossary)) {
      bound = normalizeTranslationGlossary(
        readJson(artifacts.glossary, 'bound translation glossary'),
        { targetLang: args.targetLang },
      )
      if (supplied && !sameJson(bound, supplied)) {
        throw new Error(
          'the supplied glossary differs from the glossary already bound to this run; keep the existing run unchanged and start a fresh run for a different glossary',
        )
      }
      return
    }
    if (!supplied) return
    if (args.apply) {
      throw new Error(
        '--apply cannot introduce a new glossary after translation memory was created; start a fresh preparation run with --glossary',
      )
    }
    writeJson(artifacts.glossary, supplied)
    bound = supplied
  })
  summary.glossary = bound
    ? {
        path: artifacts.glossary,
        sha256: sha256(artifacts.glossary),
        entryCount: bound.entries.length,
      }
    : null
  return bound
}

function executable(bin, args) {
  if (['.js', '.mjs', '.cjs'].includes(extname(bin).toLowerCase()) && existsSync(bin)) {
    return { bin: process.execPath, args: [bin, ...args] }
  }
  return { bin, args }
}

function runCommand(bin, args, { allowFailure = false } = {}) {
  const command = executable(bin, args)
  const result = spawnSync(command.bin, command.args, {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
  if (result.error) throw result.error
  const stdout = result.stdout ?? ''
  const stderr = result.stderr ?? ''
  let json = null
  if (stdout.trim()) {
    try {
      json = JSON.parse(stdout)
    } catch (error) {
      throw new Error(`${basename(command.bin)} returned invalid JSON: ${error.message}`)
    }
  }
  if (!allowFailure && result.status !== 0) {
    throw new Error(
      stderr.trim() || json?.error?.message || `${basename(command.bin)} exited ${result.status}`,
    )
  }
  return { status: result.status, json, stderr }
}

function phase(summary, reporter, name, action) {
  const started = performance.now()
  reporter.emit('phase-start', { phase: name })
  try {
    const value = action()
    summary.phases.push({
      name,
      status: 'pass',
      durationMs: Math.round(performance.now() - started),
    })
    reporter.emit('phase-complete', { phase: name, status: 'pass' })
    return value
  } catch (error) {
    summary.phases.push({
      name,
      status: 'error',
      durationMs: Math.round(performance.now() - started),
      message: error.message,
    })
    error.phase = name
    throw error
  }
}

function runProbe(args, artifacts, summary, reporter) {
  phase(summary, reporter, 'xdoc-probe', () =>
    runCommand(process.execPath, [
      PROBE_SCRIPT,
      '--xdoc-bin',
      args.xdocBin,
      '--output',
      artifacts.capabilities,
      ...(existsSync(artifacts.capabilities) ? ['--overwrite'] : []),
      '--json',
    ]),
  )
}

function runXdocReport(
  args,
  reportPath,
  commandArgs,
  { allowFailure = false, expectedSchema } = {},
) {
  const temporary = `${reportPath}.${process.pid}.${randomUUID()}.tmp`
  const flags = [...commandArgs, '--output', temporary, '--json']
  try {
    const result = runCommand(args.xdocBin, flags, { allowFailure })
    if (!existsSync(temporary)) {
      throw new Error(`xdoc did not persist a current report: ${reportPath}`)
    }
    const full = readJson(temporary, 'current xdoc report')
    if (expectedSchema && full?.schemaVersion !== expectedSchema) {
      throw new Error(
        `xdoc current report schema must be ${expectedSchema}, got ${full?.schemaVersion ?? 'missing'}`,
      )
    }
    mkdirSync(dirname(reportPath), { recursive: true })
    renameSync(temporary, reportPath)
    const compact = result.json ? { ...result.json, report: reportPath } : result.json
    return { compact, full, status: result.status }
  } finally {
    rmSync(temporary, { force: true })
  }
}

function requiredReference(path, section, reason) {
  return { path, section, reason }
}

function languageReviewUnits(scan) {
  return (scan?.i18nUnits?.units ?? []).filter(
    (unit) =>
      unit.action === 'review' &&
      unit.requiresReview === true &&
      ['visibleBody', 'visibleTextAttr', 'chartVisibleCache'].includes(unit.category) &&
      unit.notes?.includes?.('language-classification-uncertain'),
  )
}

function writeReviewDecisionTemplate(scanPath, scan, output, overwrite) {
  const grouped = new Map()
  for (const unit of languageReviewUnits(scan)) {
    const entry = grouped.get(unit.sourceText) ?? {
      sourceText: unit.sourceText,
      sourceHash: unit.sourceHash,
      decision: null,
      reason: '',
      context: { unitCount: 0, categories: new Set(), slides: new Set(), detectedLangs: new Set() },
    }
    if (entry.sourceHash !== unit.sourceHash) {
      throw new Error(
        `scan units with identical sourceText carry different sourceHash values: ${unit.unitId}`,
      )
    }
    entry.context.unitCount += 1
    if (unit.category) entry.context.categories.add(unit.category)
    if ((unit.slide ?? null) !== null) entry.context.slides.add(unit.slide)
    for (const lang of unit.detectedLangs ?? []) entry.context.detectedLangs.add(lang)
    grouped.set(unit.sourceText, entry)
  }
  const byText = [...grouped.values()].map((entry) => ({
    ...entry,
    context: {
      unitCount: entry.context.unitCount,
      categories: [...entry.context.categories].sort(),
      slides: [...entry.context.slides].sort((left, right) => left - right),
      detectedLangs: [...entry.context.detectedLangs].sort(),
    },
  }))
  writeJson(
    output,
    {
      schemaVersion: 'pptx-nova-i18n-review-decisions/v1',
      scanSha256: sha256(scanPath),
      byText,
      decisions: [],
    },
    overwrite,
  )
  return byText.length
}

function classifyIfNeeded(args, artifacts, scan, summary, reporter) {
  const reviewCount = languageReviewUnits(scan).length
  if (reviewCount === 0) return { path: artifacts.scan, scan }
  if (!args.reviewDecisions) {
    if (
      args.apply &&
      existsSync(artifacts.classifiedScan) &&
      existsSync(artifacts.classificationReport)
    ) {
      const prior = readJson(artifacts.classificationReport, 'review classification')
      if (
        prior?.agentGate?.passed === true &&
        prior.scanSha256 === sha256(artifacts.scan) &&
        resolve(prior.output) === artifacts.classifiedScan
      ) {
        return {
          path: artifacts.classifiedScan,
          scan: readJson(artifacts.classifiedScan, 'classified scan'),
        }
      }
    }
    phase(summary, reporter, 'review-decisions-template', () =>
      writeReviewDecisionTemplate(
        artifacts.scan,
        scan,
        artifacts.reviewDecisionsTemplate,
        args.overwrite,
      ),
    )
    return { path: null, scan: null, reviewCount }
  }
  const result = phase(summary, reporter, 'classify-review-units', () =>
    runCommand(process.execPath, [
      CLASSIFY_SCRIPT,
      '--scan',
      artifacts.scan,
      '--decisions',
      args.reviewDecisions,
      '--output',
      artifacts.classifiedScan,
      '--report',
      artifacts.classificationReport,
      '--overwrite',
      '--json',
    ]),
  )
  if (result.json?.agentGate?.passed !== true) throw new Error('review classification did not pass')
  return {
    path: artifacts.classifiedScan,
    scan: readJson(artifacts.classifiedScan, 'classified scan'),
  }
}

function initialSummary(args, artifacts) {
  return {
    schemaVersion: SUMMARY_SCHEMA,
    status: 'running',
    source: { path: args.source, sha256: sha256(args.source) },
    sourceLang: args.sourceLang,
    targetLang: args.targetLang,
    runDir: args.runDir,
    mode: args.apply ? 'apply' : 'inventory',
    artifacts,
    phases: [],
    inventory: null,
    units: null,
    memory: null,
    glossary: null,
    constraints: null,
    plan: null,
    anchorDraft: null,
    candidate: null,
    nextAction: null,
    resumeStage: null,
    requiredReferences: [],
    error: null,
  }
}

function prepareInventory(args, artifacts, summary, reporter) {
  const scanResult = phase(summary, reporter, 'i18n-scan-source', () =>
    runXdocReport(
      args,
      artifacts.scan,
      [
        'pptx',
        'i18n-scan',
        '--source',
        args.source,
        '--source-lang',
        args.sourceLang,
        '--mode',
        'source',
      ],
      { expectedSchema: 'pptx-i18n-scan/v1' },
    ),
  )
  const scan = scanResult.full
  if (args.expandReview) {
    phase(summary, reporter, 'expand-review-inventory', () =>
      writeJson(
        artifacts.reviewInventory,
        {
          ...expandReviewInventory(
            scan,
            args.expandReview,
            readPptxPackage(args.source).sharedParts,
          ),
          source: summary.source,
          scan: { path: artifacts.scan, sha256: sha256(artifacts.scan) },
        },
        args.overwrite,
      ),
    )
  }
  const classified = classifyIfNeeded(args, artifacts, scan, summary, reporter)
  if (!classified.path) {
    summary.status = 'needs-review-decisions'
    summary.resumeStage = 'review-decisions'
    summary.inventory = scanResult.compact?.inventory ?? null
    summary.nextAction =
      'Fill each byText entry once (decision plus reason cover every unit with that source text), add decisions[] entries only for per-unit exceptions, then rerun this command with --review-decisions.'
    summary.requiredReferences = [
      requiredReference(
        'references/translation/translation-mode.md',
        'Chart And Table Coverage',
        'Classify the bound language-review partition before translation.',
      ),
    ]
    return null
  }
  summary.units = { path: classified.path, sha256: sha256(classified.path) }
  return classified
}

function buildMemory(args, artifacts, summary, classified, glossary, reporter) {
  const memory = buildTranslationMemory(classified.scan, {
    sharedParts: readPptxPackage(args.source).sharedParts,
    sourceSha256: summary.source.sha256,
    unitsSha256: sha256(classified.path),
    targetLang: args.targetLang,
  })
  phase(summary, reporter, 'translation-memory', () =>
    writeJson(artifacts.memory, memory, args.overwrite),
  )
  phase(summary, reporter, 'translation-memory-fill-view', () => {
    if (existsSync(artifacts.memoryFill) && !args.overwrite) {
      throw new Error(`Output already exists: ${artifacts.memoryFill}`)
    }
    mkdirSync(dirname(artifacts.memoryFill), { recursive: true })
    writeFileSync(artifacts.memoryFill, buildMemoryFillView(memory))
  })
  const constraints = buildTranslationConstraints(memory, {
    glossary,
    sourceSha256: summary.source.sha256,
    unitsSha256: sha256(classified.path),
  })
  phase(summary, reporter, 'translation-constraints', () =>
    writeJson(artifacts.constraints, constraints, args.overwrite),
  )
  summary.memory = memory.summary
  summary.constraints = constraints.summary
  summary.inventory = memory.reviewPartitions
  summary.status = 'needs-translations'
  summary.nextAction =
    'Review translation-constraints.json first, including protected tokens, glossary rules, and non-blocking highRiskShortWords. Fill targetText in translation-memory.fill.jsonl (one {memoryId, sourceText, targetText} line per unique text; much smaller than the full memory JSON) and add required unitOverrides in the memory JSON, then rerun the same command with --apply --fill <fill.jsonl>. Editing entries[].targetText in the memory JSON directly and rerunning with --apply also works.'
  if (LONGER_TARGET_LANGS.has(args.targetLang.toLowerCase().split('-')[0])) {
    summary.nextAction += ` Target ${args.targetLang} text typically runs 20-25% longer; prefer compact wording for labels, legends, badges, and table headers up front to avoid a post-apply overflow rework round.`
  }
  summary.requiredReferences = [
    requiredReference(
      'references/translation/translation-mode.md',
      'Translation Quality Rules',
      'Fill unique target text and only the necessary unit-level overrides.',
    ),
  ]
  return memory
}

function validateMemoryBinding(args, classified, memory, summary) {
  if (memory?.source?.sha256 !== summary.source.sha256) {
    throw new Error('translation memory source SHA-256 does not match the current source')
  }
  const unitsHash = sha256(classified.path)
  if (memory?.units?.sha256 !== unitsHash) {
    throw new Error('translation memory units SHA-256 does not match the current classified scan')
  }
  if (memory.sourceLang !== classified.scan.sourceLang || memory.targetLang !== args.targetLang) {
    throw new Error('translation memory language contract does not match the current run')
  }
}

function resolveTranslationConstraints(
  args,
  artifacts,
  summary,
  classified,
  memory,
  glossary,
  reporter,
) {
  let constraints = null
  if (existsSync(artifacts.constraints)) {
    constraints = readJson(artifacts.constraints, 'translation constraints')
  } else {
    constraints = buildTranslationConstraints(memory, {
      glossary,
      sourceSha256: summary.source.sha256,
      unitsSha256: sha256(classified.path),
    })
    phase(summary, reporter, 'translation-constraints-backfill', () =>
      writeJson(artifacts.constraints, constraints),
    )
  }
  if (
    constraints?.source?.sha256 !== summary.source.sha256 ||
    constraints?.units?.sha256 !== sha256(classified.path) ||
    constraints?.sourceLang !== memory.sourceLang ||
    constraints?.targetLang !== memory.targetLang ||
    !sameJson(constraints?.glossary?.entries ?? null, glossary?.entries ?? null)
  ) {
    throw new Error(
      'translation constraints do not match the bound source, classified units, or language contract',
    )
  }
  return constraints
}

function materializePlanArtifacts(plan, artifacts, overwrite) {
  writeJson(artifacts.textPlan, plan.textPlan, overwrite)
  writeJson(artifacts.replaceText, plan.replaceText, overwrite)
  writeJson(artifacts.replaceChartText, plan.replaceChartText, overwrite)
  writeJson(artifacts.patch, plan.patch, overwrite)
}

function countItems(value, key) {
  return Array.isArray(value?.[key]) ? value[key].length : 0
}

function runJsonArtifact(bin, commandArgs, artifact, overwrite) {
  if (existsSync(artifact) && !overwrite) throw new Error(`Output already exists: ${artifact}`)
  const result = runCommand(bin, commandArgs)
  writeJson(artifact, result.json, overwrite)
  return result.json
}

function applyPlan(args, artifacts, summary, classified, memory, glossary, reporter) {
  validateMemoryBinding(args, classified, memory, summary)
  const translations = phase(summary, reporter, 'materialize-translations', () => {
    const value = materializeTranslations(classified.scan, memory)
    writeJson(artifacts.translations, value, args.overwrite)
    return value
  })
  const constraints = resolveTranslationConstraints(
    args,
    artifacts,
    summary,
    classified,
    memory,
    glossary,
    reporter,
  )
  const constraintsCheck = phase(summary, reporter, 'translation-constraints-check', () => {
    const value = validateTranslationConstraints(translations, constraints)
    writeJson(artifacts.constraintsCheck, value, args.overwrite)
    return value
  })
  summary.constraints = constraintsCheck.summary
  if (constraintsCheck.agentGate?.passed !== true) {
    summary.status = 'needs-translation-constraints'
    summary.nextAction = constraintsCheck.nextAction
    summary.requiredReferences = [
      requiredReference(
        'references/translation/translation-mode.md',
        'Protected Tokens And Project Glossary',
        'Repair only the protected-token or glossary violations in the bound constraints report.',
      ),
    ]
    return
  }
  let planResult = phase(summary, reporter, 'i18n-plan', () =>
    runXdocReport(
      args,
      artifacts.plan,
      [
        'pptx',
        'i18n-plan',
        '--source',
        args.source,
        '--units-file',
        classified.path,
        '--data',
        artifacts.translations,
      ],
      { allowFailure: true, expectedSchema: 'pptx-i18n-plan/v1' },
    ),
  )
  let planningMemory = memory
  if (
    planResult.full?.applyGate?.passed !== true &&
    supportsPptxSubcommand(artifacts, 'i18n-anchor-draft')
  ) {
    const draftResult = phase(summary, reporter, 'i18n-anchor-draft', () =>
      runXdocReport(
        args,
        artifacts.anchorDraft,
        [
          'pptx',
          'i18n-anchor-draft',
          '--source',
          args.source,
          '--units-file',
          classified.path,
          '--data',
          artifacts.translations,
        ],
        { expectedSchema: 'pptx-i18n-anchor-draft/v1' },
      ),
    )
    const merged = mergeTranslationMemoryAnchorDrafts(memory, draftResult.full)
    summary.anchorDraft = {
      status: draftResult.full.status,
      summary: draftResult.full.summary,
      agentGate: draftResult.full.agentGate,
      mergedUnitCount: merged.anchorDraftMerge.unitCount,
    }
    if (merged.anchorDraftMerge.unitCount > 0) {
      phase(summary, reporter, 'anchor-draft-plan-snapshot', () =>
        writeJson(artifacts.planBeforeAnchorDraft, planResult.full, args.overwrite),
      )
      phase(summary, reporter, 'anchor-draft-translations-snapshot', () =>
        writeJson(artifacts.translationsBeforeAnchorDraft, translations, args.overwrite),
      )
      phase(summary, reporter, 'anchor-draft-memory', () =>
        writeJson(artifacts.anchorDraftMemory, merged.memory, args.overwrite),
      )
      const anchorDraftTranslations = phase(summary, reporter, 'anchor-draft-translations', () => {
        const value = materializeTranslations(classified.scan, merged.memory)
        // translations.json is generated earlier in this same run. Replace
        // it only after preserving the pre-draft snapshot so downstream
        // finalization consumes the exact planner-authorized contract.
        writeJson(artifacts.translations, value, true)
        return value
      })
      planResult = phase(summary, reporter, 'i18n-plan-after-anchor-draft', () =>
        runXdocReport(
          args,
          artifacts.plan,
          [
            'pptx',
            'i18n-plan',
            '--source',
            args.source,
            '--units-file',
            classified.path,
            '--data',
            artifacts.translations,
          ],
          { allowFailure: true, expectedSchema: 'pptx-i18n-plan/v1' },
        ),
      )
      planningMemory = merged.memory
      summary.anchorDraft.translationCount = anchorDraftTranslations.translations.length
    }
  }
  summary.plan = {
    status: planResult.full.status,
    summary: planResult.full.summary,
    applyGate: planResult.full.applyGate,
  }
  if (planResult.full?.applyGate?.passed !== true) {
    const repairedMemory = mergeTranslationMemoryRepairs(planningMemory, planResult.full)
    if (repairedMemory.repairScaffold.unitCount > 0) {
      phase(summary, reporter, 'target-segments-repair-scaffold', () =>
        writeJson(artifacts.memoryRepair, repairedMemory, args.overwrite),
      )
      summary.status = 'needs-target-segments'
      summary.nextAction = repairedMemory.repairScaffold.instructions
    } else {
      summary.status = 'needs-plan-repair'
      summary.nextAction =
        planResult.compact?.nextAction ?? 'Repair the blocking plan items and rerun.'
      if (summary.anchorDraft?.mergedUnitCount > 0) {
        summary.nextAction += ` Continue from the guarded anchor memory with --memory ${artifacts.anchorDraftMemory} so accepted anchors are not lost.`
      }
    }
    summary.requiredReferences = [
      requiredReference(
        'references/translation/translation-mode.md',
        'I18n Plan Gate',
        'Repair only the blocker class emitted by the current bound plan.',
      ),
    ]
    return
  }
  phase(summary, reporter, 'materialize-plan-artifacts', () =>
    materializePlanArtifacts(planResult.full, artifacts, args.overwrite),
  )

  let current = join(args.runDir, 'candidate-00-source.pptx')
  phase(summary, reporter, 'copy-source-candidate', () => {
    if (existsSync(current) && !args.overwrite) throw new Error(`Output already exists: ${current}`)
    copyFileSync(args.source, current)
  })
  let stage = 1
  const nextCandidate = (label) =>
    join(args.runDir, `candidate-${String(stage++).padStart(2, '0')}-${label}.pptx`)

  if (countItems(planResult.full.replaceChartText, 'replacements') > 0) {
    const output = nextCandidate('chart')
    phase(summary, reporter, 'replace-chart-text-dry-run', () =>
      runJsonArtifact(
        args.xdocBin,
        [
          'pptx',
          'replace-chart-text',
          '--source',
          current,
          '--data',
          artifacts.replaceChartText,
          '--output',
          output,
          '--visible-cache-only',
          '--dry-run',
          '--json',
        ],
        artifacts.chartDryRun,
        args.overwrite,
      ),
    )
    phase(summary, reporter, 'replace-chart-text-apply', () =>
      runJsonArtifact(
        args.xdocBin,
        [
          'pptx',
          'replace-chart-text',
          '--source',
          current,
          '--data',
          artifacts.replaceChartText,
          '--output',
          output,
          '--visible-cache-only',
          ...(args.overwrite ? ['--overwrite'] : []),
          '--json',
        ],
        artifacts.chartApply,
        args.overwrite,
      ),
    )
    current = output
  }

  if (countItems(planResult.full.replaceText, 'replacements') > 0) {
    const output = nextCandidate('replace-text')
    phase(summary, reporter, 'replace-text-apply', () =>
      runJsonArtifact(
        args.xdocBin,
        [
          'pptx',
          'replace-text',
          '--source',
          current,
          '--data',
          artifacts.replaceText,
          '--output',
          output,
          ...(args.overwrite ? ['--overwrite'] : []),
          '--json',
        ],
        artifacts.replaceTextReport,
        args.overwrite,
      ),
    )
    current = output
  }

  if (countItems(planResult.full.patch, 'ops') > 0) {
    const output = nextCandidate('patch')
    phase(summary, reporter, 'patch-dry-run', () =>
      runJsonArtifact(
        args.xdocBin,
        [
          'pptx',
          'apply',
          '--input',
          current,
          '--patch',
          artifacts.patch,
          '--output',
          output,
          '--dry-run',
          '--json',
        ],
        artifacts.patchDryRun,
        args.overwrite,
      ),
    )
    phase(summary, reporter, 'patch-apply', () =>
      runJsonArtifact(
        args.xdocBin,
        [
          'pptx',
          'apply',
          '--input',
          current,
          '--patch',
          artifacts.patch,
          '--output',
          output,
          ...(args.overwrite ? ['--overwrite'] : []),
          '--json',
        ],
        artifacts.patchApply,
        args.overwrite,
      ),
    )
    current = output
  }

  phase(summary, reporter, 'publish-prepared-candidate', () => {
    if (existsSync(artifacts.candidate) && !args.overwrite) {
      throw new Error(`Output already exists: ${artifacts.candidate}`)
    }
    mkdirSync(dirname(artifacts.candidate), { recursive: true })
    copyFileSync(current, artifacts.candidate)
  })
  summary.candidate = {
    path: artifacts.candidate,
    sha256: sha256(artifacts.candidate),
    byteLength: statSync(artifacts.candidate).size,
  }
  summary.status = 'prepared'
  summary.nextAction = 'Run the standard translation finalizer with this stable candidate.'
  summary.requiredReferences = [
    requiredReference(
      'references/translation/translation-runner.md',
      'Standard command',
      'Finalize and publish the stable prepared candidate with delivery gates.',
    ),
  ]
  summary.translationCount = translations.translations.length
}

function compactResult(summary) {
  const phasePassed = (name) =>
    summary.phases?.some((entry) => entry.name === name && entry.status === 'pass') === true
  return {
    schemaVersion: RESULT_SCHEMA,
    status: summary.status,
    runDir: summary.runDir,
    source: summary.source,
    summary: {
      memory: summary.memory,
      glossary: summary.glossary,
      constraints: summary.constraints,
      inventory: summary.inventory,
      units: summary.units,
      plan: summary.plan,
      anchorDraft: summary.anchorDraft,
      translationCount: summary.translationCount ?? null,
    },
    artifacts: {
      summary: summary.artifacts.summary,
      units: summary.units?.path ?? null,
      prompt:
        summary.artifacts.prompt && existsSync(summary.artifacts.prompt)
          ? summary.artifacts.prompt
          : null,
      scan:
        phasePassed('i18n-scan-source') && existsSync(summary.artifacts.scan)
          ? summary.artifacts.scan
          : null,
      reviewInventory:
        phasePassed('expand-review-inventory') &&
        summary.artifacts.reviewInventory &&
        existsSync(summary.artifacts.reviewInventory)
          ? summary.artifacts.reviewInventory
          : null,
      classifiedScan:
        summary.units?.path === summary.artifacts.classifiedScan &&
        existsSync(summary.artifacts.classifiedScan)
          ? summary.artifacts.classifiedScan
          : null,
      reviewDecisionsTemplate:
        phasePassed('review-decisions-template') &&
        existsSync(summary.artifacts.reviewDecisionsTemplate)
          ? summary.artifacts.reviewDecisionsTemplate
          : null,
      memory:
        (phasePassed('translation-memory') || (summary.mode === 'apply' && summary.memory)) &&
        existsSync(summary.artifacts.memory)
          ? summary.artifacts.memory
          : null,
      memoryFill:
        phasePassed('translation-memory-fill-view') && existsSync(summary.artifacts.memoryFill)
          ? summary.artifacts.memoryFill
          : null,
      memoryFilled:
        phasePassed('memory-fill-merge') && existsSync(summary.artifacts.memoryFilled)
          ? summary.artifacts.memoryFilled
          : null,
      anchorDraftMemory:
        phasePassed('anchor-draft-memory') && existsSync(summary.artifacts.anchorDraftMemory)
          ? summary.artifacts.anchorDraftMemory
          : null,
      glossary:
        summary.artifacts.glossary && existsSync(summary.artifacts.glossary)
          ? summary.artifacts.glossary
          : null,
      constraints:
        summary.artifacts.constraints && existsSync(summary.artifacts.constraints)
          ? summary.artifacts.constraints
          : null,
      constraintsCheck:
        phasePassed('translation-constraints-check') &&
        existsSync(summary.artifacts.constraintsCheck)
          ? summary.artifacts.constraintsCheck
          : null,
      memoryRepair:
        phasePassed('target-segments-repair-scaffold') && existsSync(summary.artifacts.memoryRepair)
          ? summary.artifacts.memoryRepair
          : null,
      translations:
        phasePassed('materialize-translations') && existsSync(summary.artifacts.translations)
          ? summary.artifacts.translations
          : null,
      translationsBeforeAnchorDraft:
        phasePassed('anchor-draft-translations-snapshot') &&
        existsSync(summary.artifacts.translationsBeforeAnchorDraft)
          ? summary.artifacts.translationsBeforeAnchorDraft
          : null,
      anchorDraft:
        phasePassed('i18n-anchor-draft') && existsSync(summary.artifacts.anchorDraft)
          ? summary.artifacts.anchorDraft
          : null,
      plan:
        phasePassed('i18n-plan') && summary.plan && existsSync(summary.artifacts.plan)
          ? summary.artifacts.plan
          : null,
      planBeforeAnchorDraft:
        phasePassed('anchor-draft-plan-snapshot') &&
        existsSync(summary.artifacts.planBeforeAnchorDraft)
          ? summary.artifacts.planBeforeAnchorDraft
          : null,
      candidate:
        summary.status === 'prepared' &&
        summary.candidate?.path === summary.artifacts.candidate &&
        existsSync(summary.artifacts.candidate)
          ? summary.artifacts.candidate
          : null,
    },
    nextAction: summary.nextAction,
    requiredReferences: summary.requiredReferences,
    error: summary.error,
  }
}

function reviewExpansionResumeHint(args) {
  return `rerun the same preparation command with --resume-stage review --expand-review ${args.expandReview} and without --apply/--review-decisions/--fill; the runner will reuse ${join(args.runDir, 'i18n-scan-source.json')} without rescanning or modifying translation memory`
}

function validateReviewExpansionRun(args, artifacts) {
  if (!existsSync(args.source) || !statSync(args.source).isFile()) {
    throw new Error(`source does not exist or is not a file: ${args.source}`)
  }
  if (!existsSync(args.runDir) || !statSync(args.runDir).isDirectory()) {
    throw new Error('--resume-stage review requires the existing preparation run directory')
  }
  if (!existsSync(artifacts.summary)) {
    throw new Error('--resume-stage review requires the prior preparation summary')
  }
  const prior = readJson(artifacts.summary, 'prior preparation summary')
  if (
    prior.schemaVersion !== SUMMARY_SCHEMA ||
    prior.status !== 'needs-translations' ||
    prior.source?.sha256 !== sha256(args.source) ||
    prior.sourceLang !== args.sourceLang ||
    prior.targetLang !== args.targetLang ||
    resolve(prior.runDir ?? '') !== args.runDir ||
    resolve(prior.artifacts?.scan ?? '') !== artifacts.scan
  ) {
    throw new Error(
      `review expansion must match a bound needs-translations preparation run; ${reviewExpansionResumeHint(args)}`,
    )
  }
  for (const [label, path] of [
    ['bound source scan', artifacts.scan],
    ['translation memory', artifacts.memory],
  ]) {
    if (!existsSync(path) || !statSync(path).isFile()) {
      throw new Error(`${label} does not exist or is not a file: ${path}`)
    }
  }
  const scan = readJson(artifacts.scan, 'bound source scan')
  if (
    scan.schemaVersion !== 'pptx-i18n-scan/v1' ||
    (scan.sourceLang && scan.sourceLang !== args.sourceLang)
  ) {
    throw new Error('bound source scan does not match the preparation language contract')
  }
  for (const [label, output] of [
    ['review inventory', artifacts.reviewInventory],
    ['review expansion summary', artifacts.reviewExpansionSummary],
  ]) {
    if (existsSync(output) && !args.overwrite) {
      throw new Error(
        `${label} already exists; pass --overwrite only for this current-run artifact: ${output}`,
      )
    }
    for (const [inputLabel, input] of [
      ['source', args.source],
      ['bound source scan', artifacts.scan],
      ['translation memory', artifacts.memory],
      ['preparation summary', artifacts.summary],
    ]) {
      if (sameIdentity(pathIdentity(input), pathIdentity(output))) {
        throw new Error(`${label} must not resolve to the read-only ${inputLabel} input`)
      }
    }
  }
  return { prior, scan }
}

function compactReviewExpansionResult(summary) {
  return {
    schemaVersion: RESULT_SCHEMA,
    status: summary.status,
    runDir: summary.runDir,
    source: summary.source,
    summary: {
      partition: summary.partition,
      count: summary.inventory?.count ?? null,
      scanUnchanged: summary.integrity?.scanUnchanged ?? null,
      memoryUnchanged: summary.integrity?.memoryUnchanged ?? null,
    },
    artifacts: {
      summary: summary.artifacts.summary,
      reviewInventory:
        summary.artifacts.reviewInventory && existsSync(summary.artifacts.reviewInventory)
          ? summary.artifacts.reviewInventory
          : null,
      scan: summary.scan.path,
      memory: summary.memory.path,
    },
    nextAction: summary.nextAction,
    requiredReferences: summary.requiredReferences,
    error: summary.error,
  }
}

function runReviewExpansion(args, artifacts, binding, reporter) {
  const scanBefore = sha256(artifacts.scan)
  const memoryBefore = sha256(artifacts.memory)
  const summary = {
    schemaVersion: 'pptx-nova-translation-review-expansion/v1',
    status: 'running',
    source: binding.prior.source,
    sourceLang: args.sourceLang,
    targetLang: args.targetLang,
    runDir: args.runDir,
    partition: args.expandReview,
    scan: { path: artifacts.scan, sha256: scanBefore },
    memory: { path: artifacts.memory, sha256: memoryBefore },
    inventory: null,
    artifacts: {
      reviewInventory: artifacts.reviewInventory,
      summary: artifacts.reviewExpansionSummary,
    },
    phases: [],
    integrity: null,
    nextAction: null,
    requiredReferences: [],
    error: null,
  }
  try {
    summary.inventory = phase(summary, reporter, 'expand-bound-review-inventory', () => {
      const inventory = {
        ...expandReviewInventory(
          binding.scan,
          args.expandReview,
          readPptxPackage(args.source).sharedParts,
        ),
        source: summary.source,
        scan: summary.scan,
      }
      writeJson(artifacts.reviewInventory, inventory, args.overwrite)
      return { partition: inventory.partition, count: inventory.count }
    })
    summary.integrity = {
      scanUnchanged: sha256(artifacts.scan) === scanBefore,
      memoryUnchanged: sha256(artifacts.memory) === memoryBefore,
    }
    if (!summary.integrity.scanUnchanged || !summary.integrity.memoryUnchanged) {
      throw new Error('bound source scan or translation memory changed during review expansion')
    }
    summary.status = 'review-expanded'
    summary.nextAction =
      'Review only the persisted partition, then continue filling the existing translation memory; this expansion does not change preparation state.'
    summary.requiredReferences = [
      requiredReference(
        'references/translation/translation-mode.md',
        'Review Partition Recovery',
        'Use the expanded bound partition without restarting translation preparation.',
      ),
    ]
  } catch (error) {
    summary.status = 'error'
    summary.error = { phase: error.phase ?? null, message: error.message }
    summary.nextAction = reviewExpansionResumeHint(args)
  }
  writeJson(artifacts.reviewExpansionSummary, summary, args.overwrite)
  const output = args.jsonFull ? summary : compactReviewExpansionResult(summary)
  if (args.json) process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  else
    process.stdout.write(
      `Translation review expansion ${summary.status}: ${artifacts.reviewExpansionSummary}\n`,
    )
  if (summary.status === 'error') process.exitCode = 1
}

function validateRun(args, artifacts) {
  if (!existsSync(args.source) || !statSync(args.source).isFile()) {
    throw new Error(`source does not exist or is not a file: ${args.source}`)
  }
  for (const [flag, path] of [
    ['--prompt-file', args.promptFile],
    ['--glossary', args.glossary],
  ]) {
    if (path && (!existsSync(path) || !statSync(path).isFile())) {
      throw new Error(`${flag} does not exist or is not a file: ${path}`)
    }
  }
  if (extname(args.source).toLowerCase() !== '.pptx') throw new Error('--source must be .pptx')
  if (extname(args.outputCandidate).toLowerCase() !== '.pptx') {
    throw new Error('--output-candidate must be .pptx')
  }
  if (extname(args.memory).toLowerCase() !== '.json') {
    throw new Error('--memory must be .json')
  }
  if (args.fill && extname(args.fill).toLowerCase() !== '.jsonl') {
    throw new Error('--fill must be .jsonl')
  }
  if (args.glossary && extname(args.glossary).toLowerCase() !== '.json') {
    throw new Error('--glossary must be .json')
  }
  if (args.apply) {
    if (!existsSync(args.runDir) || !statSync(args.runDir).isDirectory()) {
      throw new Error('--apply requires the existing preparation run directory')
    }
    if (!existsSync(artifacts.summary)) {
      throw new Error('--apply requires the prior preparation summary')
    }
    const prior = readJson(artifacts.summary, 'prior preparation summary')
    if (
      prior.schemaVersion !== SUMMARY_SCHEMA ||
      prior.source?.sha256 !== sha256(args.source) ||
      prior.sourceLang !== args.sourceLang ||
      prior.targetLang !== args.targetLang ||
      resolve(prior.runDir ?? '') !== args.runDir
    ) {
      throw new Error(
        '--apply source, languages, and run directory must match the prior preparation run',
      )
    }
  }
  const readOnlyInputs = [
    ['source', args.source],
    ...(args.reviewDecisions ? [['reviewDecisions', args.reviewDecisions]] : []),
    ...(args.apply ? [['memory', args.memory]] : []),
    ...(args.fill ? [['fill', args.fill]] : []),
    ...(args.glossary ? [['glossary', args.glossary]] : []),
    ...(args.promptFile ? [['promptFile', args.promptFile]] : []),
  ]
  const writableArtifacts = Object.entries(artifacts).filter(
    ([label, path]) =>
      typeof path === 'string' &&
      !(args.apply && label === 'memory') &&
      !(args.reviewDecisions && label === 'reviewDecisionsTemplate'),
  )
  for (const [outputLabel, outputPath] of writableArtifacts) {
    for (const [inputLabel, inputPath] of readOnlyInputs) {
      if (sameIdentity(pathIdentity(inputPath), pathIdentity(outputPath))) {
        throw new Error(
          `${outputLabel} output must not resolve to the read-only ${inputLabel} input`,
        )
      }
    }
  }
  for (let left = 0; left < writableArtifacts.length; left += 1) {
    for (let right = left + 1; right < writableArtifacts.length; right += 1) {
      const [leftLabel, leftPath] = writableArtifacts[left]
      const [rightLabel, rightPath] = writableArtifacts[right]
      if (sameIdentity(pathIdentity(leftPath), pathIdentity(rightPath))) {
        throw new Error(`${leftLabel} and ${rightLabel} outputs must be distinct`)
      }
    }
  }
  if (!args.apply && !isNewOrPreProbedRunDir(args.runDir)) {
    if (args.expandReview && existsSync(artifacts.summary)) {
      const prior = readJson(artifacts.summary, 'prior preparation summary')
      if (prior.status === 'needs-translations') {
        throw new Error(
          `review partition expansion after needs-translations requires an explicit resume stage; ${reviewExpansionResumeHint(args)}`,
        )
      }
    }
    if (!args.reviewDecisions || !existsSync(artifacts.summary)) {
      assertNewOrPreProbedRunDir(args.runDir)
    }
    const prior = readJson(artifacts.summary, 'prior preparation summary')
    if (
      !(prior.status === 'needs-review-decisions' || prior.resumeStage === 'review-decisions') ||
      prior.source?.sha256 !== sha256(args.source) ||
      prior.sourceLang !== args.sourceLang ||
      prior.targetLang !== args.targetLang
    ) {
      throw new Error('review-decision resume does not match the prior preparation run')
    }
  } else {
    mkdirSync(args.runDir, { recursive: true })
  }
}

async function main(args, reporter) {
  const artifacts = artifactsFor(args)
  if (args.resumeStage === 'review') {
    const binding = validateReviewExpansionRun(args, artifacts)
    runReviewExpansion(args, artifacts, binding, reporter)
    return
  }
  validateRun(args, artifacts)
  const summary = initialSummary(args, artifacts)
  const started = performance.now()
  try {
    archivePrompt(args, artifacts, summary, reporter)
    const glossary = bindGlossary(args, artifacts, summary, reporter)
    runProbe(args, artifacts, summary, reporter)
    const classified = prepareInventory(args, artifacts, summary, reporter)
    if (classified) {
      if (args.apply) {
        let memory = readJson(artifacts.memory, 'translation memory')
        if (args.fill) {
          memory = phase(summary, reporter, 'memory-fill-merge', () => {
            if (!existsSync(args.fill) || !statSync(args.fill).isFile()) {
              throw new Error(`--fill does not exist or is not a file: ${args.fill}`)
            }
            const filled = applyMemoryFill(memory, readFileSync(args.fill, 'utf8'))
            writeJson(artifacts.memoryFilled, filled.memory, args.overwrite)
            summary.memoryFill = {
              path: args.fill,
              filledCount: filled.filledCount,
              mergedMemory: artifacts.memoryFilled,
            }
            return filled.memory
          })
        }
        summary.memory = memory.summary ?? null
        summary.inventory = memory.reviewPartitions ?? null
        applyPlan(args, artifacts, summary, classified, memory, glossary, reporter)
      } else {
        buildMemory(args, artifacts, summary, classified, glossary, reporter)
      }
    }
  } catch (error) {
    summary.status = 'error'
    if (!args.apply && args.reviewDecisions) summary.resumeStage = 'review-decisions'
    summary.error = { phase: error.phase ?? null, message: error.message }
    summary.nextAction =
      'Inspect the persisted summary and the named phase artifact before retrying.'
  }
  summary.durationMs = Math.round(performance.now() - started)
  writeJson(artifacts.summary, summary, true)
  const output = args.jsonFull ? summary : compactResult(summary)
  if (args.json) process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  else
    process.stdout.write(
      `Translation preparation ${summary.status}: ${artifacts.summary}${summary.candidate ? `\nCandidate: ${summary.candidate.path}` : ''}\n`,
    )
  if (summary.status === 'error') process.exitCode = 1
}

let args = null
try {
  args = parseArgs(process.argv.slice(2))
  const reporter = createProgressReporter({
    mode: args.progress,
    jsonOutput: args.json,
    context: { tool: 'cli/translation/prepare' },
  })
  await main(args, reporter)
} catch (error) {
  const failure = {
    schemaVersion: RESULT_SCHEMA,
    status: 'error',
    error: { phase: null, message: error.message },
  }
  if (args?.json || process.argv.includes('--json') || process.argv.includes('--json-full')) {
    process.stdout.write(`${JSON.stringify(failure, null, 2)}\n`)
  } else {
    process.stderr.write(`${error.message}\n`)
  }
  process.exitCode = 1
}
