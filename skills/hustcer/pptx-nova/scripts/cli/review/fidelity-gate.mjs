#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import {
  REVIEW_POLICY_EVALUATION_SCHEMA_VERSION,
  evaluateReviewPolicy,
  hasEmbeddedReviewedFindings,
} from '../../lib/review/policy.mjs'

const SCHEMA_VERSION = 'pptx-nova-fidelity-gate/v1'
const TEMPLATE_GATE_SCHEMA_VERSION = 'pptx-nova-template-gate/v1'
const REFURBISH_AUDIT_SCHEMA_VERSION = 'pptx-refurbish-audit/v1'
const VISION_DIFF_SCHEMA_VERSION = 'pptx-vision-diff/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/fidelity-gate.mjs --mode <mode> [options]

Modes:
  template-following  Summarize template-following evidence after template-gate.
  refurbish           Summarize refurbish evidence after vision-diff and refurbish-audit.

Options:
  --mode <mode>             Required. template-following|template|refurbish.
  --source-inspect <path>   xdoc inspect JSON for the source/template deck.
  --source-pptx <path>      Source PPTX used for hash-bound reviewed findings.
  --final-inspect <path>    xdoc inspect JSON for the final deck.
  --candidate-pptx <path>   Candidate PPTX recorded in the final review receipt.
  --frame-map <path>        template-frame-map.json for Template Following.
  --template-gate <path>    template-gate.json from cli/edit/template-gate.mjs.
  --reference-map <path>    reference-map.json for Refurbish Existing Deck.
  --content-audit <path>    Optional baseline content-audit.json.
  --final-audit <path>      content-audit-final.json from xdoc pptx refurbish-audit.
  --vision-diff <path>      vision-diff.json from xdoc pptx vision-diff.
  --layout-snapshot <path>  layout-final.json with raw layout findings.
  --review-policy <path>    Optional pptx-nova-review-policy/v1 document.
  --review-evaluation <path>
                            Optional precomputed review-policy evaluation; when present,
                            fidelity consumes it instead of evaluating the policy again.
  --json                    Print machine-readable report.
  --help                    Show this help.
`

function parseArgs(argv) {
  const args = {
    mode: '',
    sourceInspect: '',
    sourcePptx: '',
    finalInspect: '',
    candidatePptx: '',
    frameMap: '',
    templateGate: '',
    referenceMap: '',
    contentAudit: '',
    finalAudit: '',
    visionDiff: '',
    layoutSnapshot: '',
    reviewPolicy: '',
    reviewEvaluation: '',
    json: false,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg in valueFlags) {
      const key = valueFlags[arg]
      args[key] = key === 'mode' ? valueAfter(argv, i, arg) : resolve(valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  args.mode = normalizeMode(args.mode)
  if (!args.mode) throw new Error(`--mode is required\n\n${usage}`)
  return args
}

const valueFlags = {
  '--mode': 'mode',
  '--source-inspect': 'sourceInspect',
  '--source-pptx': 'sourcePptx',
  '--final-inspect': 'finalInspect',
  '--candidate-pptx': 'candidatePptx',
  '--frame-map': 'frameMap',
  '--template-gate': 'templateGate',
  '--reference-map': 'referenceMap',
  '--content-audit': 'contentAudit',
  '--final-audit': 'finalAudit',
  '--vision-diff': 'visionDiff',
  '--layout-snapshot': 'layoutSnapshot',
  '--review-policy': 'reviewPolicy',
  '--review-evaluation': 'reviewEvaluation',
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function normalizeMode(mode) {
  if (mode === 'template') return 'template-following'
  if (mode === 'template-following' || mode === 'refurbish') return mode
  return ''
}

function readJson(path, label) {
  if (!path) throw new Error(`${label} path is required`)
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`Failed to read ${label} at ${path}: ${error.message}`)
  }
}

function readOptionalJson(path, label) {
  if (!path) return null
  return readJson(path, label)
}

function fileSha256(path) {
  if (!path || !existsSync(path)) return null
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function push(list, severity, code, message, details = {}) {
  list.push({ severity, code, message, ...details })
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

function numeric(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

function slideCountOf(inspect) {
  const presentationCount = numeric(inspect?.presentation?.slideCount)
  if (presentationCount !== null) return presentationCount
  return Array.isArray(inspect?.slides) ? inspect.slides.length : null
}

function integerInRange(value, maxExclusive) {
  return Number.isInteger(value) && value >= 0 && value < maxExclusive
}

function templateFrameEntries(frameMap) {
  return asArray(frameMap?.outputSlides ?? frameMap?.slides)
}

function entryOutputSlide(entry) {
  return numeric(entry?.outputSlide ?? entry?.slide ?? entry?.outputIndex ?? entry?.index)
}

function entrySourceSlide(entry) {
  return numeric(entry?.sourceSlide ?? entry?.templateSlide ?? entry?.fromSlide)
}

function referenceMapEntries(referenceMap) {
  return asArray(referenceMap?.slides ?? referenceMap?.mappings ?? referenceMap?.outputSlides)
}

function outputSlidesForReferenceEntry(entry) {
  const values = Array.isArray(entry?.outputSlides)
    ? entry.outputSlides
    : [entry?.outputSlide ?? entry?.slide ?? entry?.outputIndex ?? entry?.index]
  return values.map(numeric).filter((value) => value !== null)
}

function sourceSlideForReferenceEntry(entry) {
  return numeric(entry?.sourceSlide ?? entry?.source ?? entry?.sourceIndex ?? entry?.fromSlide)
}

function visionCounts(report, classification) {
  const counts = report?.summary?.byClass?.[classification] ?? {}
  return {
    high: Number(counts.high ?? 0),
    medium: Number(counts.medium ?? 0),
    low: Number(counts.low ?? 0),
  }
}

function addCheck(checks, name, status, details = {}) {
  checks.push({ name, status, ...details })
}

function validateTemplateFollowing(args, report) {
  const sourceInspect = readJson(args.sourceInspect, 'source inspect')
  const finalInspect = readJson(args.finalInspect, 'final inspect')
  const frameMap = readJson(args.frameMap, 'template frame map')
  const templateGate = readJson(args.templateGate, 'template gate report')

  const sourceCount = slideCountOf(sourceInspect)
  const finalCount = slideCountOf(finalInspect)
  const entries = templateFrameEntries(frameMap)
  const outputSlides = new Set()
  const sourceSlides = new Set()

  if (!Number.isInteger(sourceCount) || sourceCount <= 0) {
    push(report.errors, 'error', 'source-slide-count-missing', 'source inspect has no slides')
  }
  if (!Number.isInteger(finalCount) || finalCount <= 0) {
    push(report.errors, 'error', 'final-slide-count-missing', 'final inspect has no slides')
  }
  if (entries.length === 0) {
    push(report.errors, 'error', 'frame-map-empty', 'template frame map has no output slides')
  }

  for (const [index, entry] of entries.entries()) {
    const outputSlide = entryOutputSlide(entry)
    const sourceSlide = entrySourceSlide(entry)
    if (!Number.isInteger(outputSlide) || outputSlide < 0) {
      push(
        report.errors,
        'error',
        'frame-map-output-invalid',
        'frame map output slide is invalid',
        {
          entry: index,
          outputSlide,
        },
      )
    } else if (Number.isInteger(finalCount) && outputSlide >= finalCount) {
      push(
        report.errors,
        'error',
        'frame-map-output-out-of-range',
        `frame map output slide ${outputSlide} is outside final slide count ${finalCount}`,
        { entry: index, outputSlide, finalCount },
      )
    } else if (outputSlides.has(outputSlide)) {
      push(
        report.errors,
        'error',
        'frame-map-output-duplicate',
        `frame map output slide ${outputSlide} is duplicated`,
        { entry: index, outputSlide },
      )
    } else {
      outputSlides.add(outputSlide)
    }

    if (!Number.isInteger(sourceSlide) || sourceSlide < 0) {
      push(
        report.errors,
        'error',
        'frame-map-source-invalid',
        'frame map source slide is invalid',
        {
          entry: index,
          sourceSlide,
        },
      )
    } else if (Number.isInteger(sourceCount) && sourceSlide >= sourceCount) {
      push(
        report.errors,
        'error',
        'frame-map-source-out-of-range',
        `frame map source slide ${sourceSlide} is outside source slide count ${sourceCount}`,
        { entry: index, sourceSlide, sourceCount },
      )
    } else {
      sourceSlides.add(sourceSlide)
    }
  }

  if (Number.isInteger(finalCount) && outputSlides.size !== finalCount) {
    const missing = []
    for (let slide = 0; slide < finalCount; slide += 1) {
      if (!outputSlides.has(slide)) missing.push(slide)
    }
    push(
      report.errors,
      'error',
      'frame-map-final-coverage',
      'template frame map must cover every final slide exactly once',
      { finalCount, mappedSlides: outputSlides.size, missing },
    )
  }

  const templateErrors = Number(templateGate?.summary?.errors ?? templateGate?.errors?.length ?? 0)
  const templateWarnings = Number(
    templateGate?.summary?.warnings ?? templateGate?.warnings?.length ?? 0,
  )
  if (templateGate?.schemaVersion !== TEMPLATE_GATE_SCHEMA_VERSION) {
    push(
      report.errors,
      'error',
      'template-gate-schema-version',
      `template gate schemaVersion must be ${TEMPLATE_GATE_SCHEMA_VERSION}`,
      { schemaVersion: templateGate?.schemaVersion ?? '' },
    )
  }
  if (templateErrors > 0 || templateGate?.status === 'error') {
    push(
      report.errors,
      'error',
      'template-gate-failed',
      'template gate reported errors; fidelity gate cannot pass',
      { status: templateGate?.status ?? '', errors: templateErrors },
    )
    for (const item of asArray(templateGate?.errors)) {
      push(
        report.errors,
        'error',
        item.code ?? 'template-gate-error',
        item.message ?? 'template gate error',
        { source: 'template-gate', details: item },
      )
    }
  }
  for (const item of asArray(templateGate?.warnings)) {
    push(
      report.warnings,
      'warning',
      item.code ?? 'template-gate-warning',
      item.message ?? 'template gate warning',
      { source: 'template-gate', details: item },
    )
  }

  addCheck(report.checks, 'template-slide-map', report.errors.length === 0 ? 'passed' : 'failed', {
    sourceSlides: sourceCount,
    finalSlides: finalCount,
    mappedSlides: outputSlides.size,
    uniqueSourceSlides: sourceSlides.size,
  })
  addCheck(
    report.checks,
    'template-gate-report',
    templateErrors === 0 && templateGate?.status !== 'error' ? 'passed' : 'failed',
    {
      status: templateGate?.status ?? '',
      errors: templateErrors,
      warnings: templateWarnings,
    },
  )

  report.summary.sourceSlides = sourceCount
  report.summary.finalSlides = finalCount
  report.summary.mappedSlides = outputSlides.size
}

function validateRefurbish(args, report) {
  const sourceInspect = readJson(args.sourceInspect, 'source inspect')
  const referenceMap = readOptionalJson(args.referenceMap, 'reference map')
  const explicitReviewPolicy = readOptionalJson(args.reviewPolicy, 'review policy')
  const contentAudit = readOptionalJson(args.contentAudit, 'content audit')
  const finalAudit = readJson(args.finalAudit, 'final audit')
  const visionDiff = readJson(args.visionDiff, 'vision diff')
  const layoutSnapshot = readOptionalJson(args.layoutSnapshot, 'layout snapshot')
  const reviewEvaluation = readOptionalJson(args.reviewEvaluation, 'review evaluation')

  const inspectSourceCount = slideCountOf(sourceInspect)
  const auditSourceCount = numeric(finalAudit?.summary?.baselineSlideCount)
  const auditFinalCount = numeric(finalAudit?.summary?.targetSlideCount)
  const sourceCount = auditSourceCount ?? inspectSourceCount
  const finalCount = auditFinalCount

  validateFinalAudit(report, finalAudit, sourceCount, finalCount)
  validateVisionDiff(report, visionDiff)
  validateReferenceMap(report, referenceMap, sourceCount, finalCount)
  validateReviewedFindings({
    args,
    report,
    referenceMap,
    explicitReviewPolicy,
    layoutSnapshot,
    reviewEvaluation,
  })

  if (contentAudit && contentAudit.schemaVersion !== 'pptx-nova-content-audit/v1') {
    push(
      report.warnings,
      'warning',
      'content-audit-schema-version',
      'baseline content-audit schemaVersion is not pptx-nova-content-audit/v1',
      { schemaVersion: contentAudit.schemaVersion ?? '' },
    )
  }

  report.summary.sourceSlides = sourceCount
  report.summary.finalSlides = finalCount
}

function validateReviewedFindings({
  args,
  report,
  referenceMap,
  explicitReviewPolicy,
  layoutSnapshot,
  reviewEvaluation,
}) {
  const embeddedPolicy = hasEmbeddedReviewedFindings(referenceMap) ? referenceMap : null
  const precomputedReportsAmbiguity = asArray(reviewEvaluation?.errors).some(
    (item) => item?.code === 'review-policy-source-ambiguous',
  )
  if (explicitReviewPolicy && embeddedPolicy && !precomputedReportsAmbiguity) {
    push(
      report.errors,
      'error',
      'review-policy-source-ambiguous',
      'reviewed findings must come from either --review-policy or reference-map.json, not both',
    )
  }
  if (layoutSnapshot && layoutSnapshot.schemaVersion !== 'pptx-nova-layout-snapshot/v1') {
    push(
      report.errors,
      'error',
      'layout-snapshot-schema-version',
      'layout snapshot schemaVersion must be pptx-nova-layout-snapshot/v1',
      { schemaVersion: layoutSnapshot.schemaVersion ?? '' },
    )
  }

  const policyDocument = explicitReviewPolicy ?? embeddedPolicy
  const policyDocumentPath = explicitReviewPolicy
    ? args.reviewPolicy
    : embeddedPolicy
      ? args.referenceMap
      : ''
  let evaluation = reviewEvaluation
    ? reviewEvaluation
    : evaluateReviewPolicy({
        policyDocument,
        policyDocumentPath,
        allowEmbeddedPolicy: Boolean(!explicitReviewPolicy && embeddedPolicy),
        sourcePptx: args.sourcePptx,
        candidatePptx: args.candidatePptx,
        findings: asArray(layoutSnapshot?.risks),
        evidencePaths: {
          layoutSnapshot: args.layoutSnapshot,
          finalAudit: args.finalAudit,
          visionDiff: args.visionDiff,
          referenceMap: args.referenceMap,
        },
      })
  if (reviewEvaluation) {
    const bindingErrors = []
    if (
      !isPlainObject(evaluation) ||
      !isPlainObject(evaluation.summary) ||
      !Array.isArray(evaluation.applied) ||
      !Array.isArray(evaluation.reviewedFindings) ||
      !Array.isArray(evaluation.remainingActionable) ||
      !Array.isArray(evaluation.informational) ||
      !Array.isArray(evaluation.errors)
    ) {
      const raw = isPlainObject(evaluation) ? evaluation : {}
      const rawSummary = isPlainObject(raw.summary) ? raw.summary : {}
      evaluation = {
        schemaVersion: raw.schemaVersion ?? null,
        status: 'fail',
        bindings: isPlainObject(raw.bindings) ? raw.bindings : {},
        summary: {
          declaredReviewCount: Number(rawSummary.declaredReviewCount ?? 0),
          validReviewCount: Number(rawSummary.validReviewCount ?? 0),
          appliedReviewCount: 0,
          reviewedFindingCount: 0,
          remainingActionableCount: Number(rawSummary.remainingActionableCount ?? 0),
          informationalCount: Number(rawSummary.informationalCount ?? 0),
          errorCount: asArray(raw.errors).length + 1,
        },
        applied: [],
        reviewedFindings: [],
        remainingActionable: asArray(raw.remainingActionable),
        informational: asArray(raw.informational),
        errors: [
          ...asArray(raw.errors),
          {
            code: 'review-evaluation-structure-invalid',
            message: 'precomputed review evaluation is missing required fields',
          },
        ],
      }
    }
    if (evaluation?.schemaVersion !== REVIEW_POLICY_EVALUATION_SCHEMA_VERSION) {
      bindingErrors.push({
        code: 'review-evaluation-schema-version',
        message: `review evaluation schemaVersion must be ${REVIEW_POLICY_EVALUATION_SCHEMA_VERSION}`,
      })
    }
    const expectedBindings = [
      ['source', evaluation?.bindings?.source?.sha256, fileSha256(args.sourcePptx)],
      ['candidate', evaluation?.bindings?.candidate?.sha256, fileSha256(args.candidatePptx)],
      [
        'layoutSnapshot',
        evaluation?.bindings?.evidence?.layoutSnapshot?.sha256,
        fileSha256(args.layoutSnapshot),
      ],
      [
        'finalAudit',
        evaluation?.bindings?.evidence?.finalAudit?.sha256,
        fileSha256(args.finalAudit),
      ],
      [
        'visionDiff',
        evaluation?.bindings?.evidence?.visionDiff?.sha256,
        fileSha256(args.visionDiff),
      ],
    ]
    const referenceMapExpected = evaluation?.bindings?.evidence?.referenceMap?.sha256 ?? null
    const referenceMapActual = fileSha256(args.referenceMap)
    if (referenceMapExpected || referenceMapActual) {
      expectedBindings.push(['referenceMap', referenceMapExpected, referenceMapActual])
    }
    const policyPath = explicitReviewPolicy
      ? args.reviewPolicy
      : embeddedPolicy
        ? args.referenceMap
        : ''
    const policyExpected = evaluation?.bindings?.policyDocument?.sha256 ?? null
    const policyActual = fileSha256(policyPath)
    if (policyExpected || policyActual) {
      expectedBindings.push(['policyDocument', policyExpected, policyActual])
    }
    const semanticErrors = []
    if (!['pass', 'fail'].includes(evaluation.status)) {
      semanticErrors.push('status must be pass or fail')
    }
    if (evaluation.status === 'pass' && evaluation.errors.length > 0) {
      semanticErrors.push('pass evaluation must not contain errors')
    }
    if (evaluation.status === 'fail' && evaluation.errors.length === 0) {
      semanticErrors.push('fail evaluation must contain at least one error')
    }
    const summaryCounts = [
      ['declaredReviewCount', null],
      ['validReviewCount', null],
      ['appliedReviewCount', evaluation.applied.length],
      ['reviewedFindingCount', evaluation.reviewedFindings.length],
      ['remainingActionableCount', evaluation.remainingActionable.length],
      ['informationalCount', evaluation.informational.length],
      ['errorCount', evaluation.errors.length],
    ]
    for (const [field, expectedCount] of summaryCounts) {
      const actualCount = evaluation.summary[field]
      if (!Number.isInteger(actualCount) || actualCount < 0) {
        semanticErrors.push(`summary.${field} must be a non-negative integer`)
      } else if (expectedCount !== null && actualCount !== expectedCount) {
        semanticErrors.push(`summary.${field} does not match its evidence array`)
      }
    }
    if (semanticErrors.length > 0) {
      bindingErrors.push({
        code: 'review-evaluation-semantic-invalid',
        message: 'precomputed review evaluation has inconsistent status, arrays, or summary',
        reasons: semanticErrors,
      })
    }
    for (const [name, expected, actual] of expectedBindings) {
      if (!actual || expected !== actual) {
        bindingErrors.push({
          code: 'review-evaluation-binding-stale',
          message: `precomputed review evaluation ${name} binding is stale`,
          evidence: name,
          expectedSha256: expected ?? null,
          actualSha256: actual,
        })
      }
    }
    if (bindingErrors.length > 0) {
      evaluation.status = 'fail'
      evaluation.applied = []
      evaluation.reviewedFindings = []
      evaluation.errors = [...asArray(evaluation.errors), ...bindingErrors]
      evaluation.summary = {
        ...evaluation.summary,
        appliedReviewCount: 0,
        reviewedFindingCount: 0,
        remainingActionableCount: evaluation.remainingActionable.length,
        informationalCount: evaluation.informational.length,
        errorCount: evaluation.errors.length,
      }
    }
  }
  report.reviewPolicy = evaluation
  report.summary.declaredReviews = evaluation.summary.declaredReviewCount
  report.summary.appliedReviews = evaluation.summary.appliedReviewCount
  report.summary.reviewedFindings = evaluation.summary.reviewedFindingCount
  report.summary.remainingActionableFindings = evaluation.summary.remainingActionableCount

  for (const item of evaluation.errors) {
    push(report.errors, 'error', item.code, item.message, {
      source: 'review-policy',
      details: item,
    })
  }
  if (evaluation.summary.remainingActionableCount > 0) {
    const counts = new Map()
    for (const finding of evaluation.remainingActionable) {
      const code = String(finding?.code ?? 'layout-finding')
      counts.set(code, (counts.get(code) ?? 0) + 1)
    }
    push(
      report.warnings,
      'warning',
      'layout-actionable-findings',
      'layout snapshot retains actionable findings that were not covered by reviewed exceptions',
      {
        count: evaluation.summary.remainingActionableCount,
        byCode: Object.fromEntries(counts),
      },
    )
  }
  addCheck(report.checks, 'review-policy', evaluation.status === 'pass' ? 'passed' : 'failed', {
    declaredReviews: evaluation.summary.declaredReviewCount,
    appliedReviews: evaluation.summary.appliedReviewCount,
    reviewedFindings: evaluation.summary.reviewedFindingCount,
    remainingActionableFindings: evaluation.summary.remainingActionableCount,
    errors: evaluation.summary.errorCount,
  })
}

function validateFinalAudit(report, finalAudit, sourceCount, finalCount) {
  const errorCount = Number(finalAudit?.summary?.errorCount ?? 0)
  const warningCount = Number(finalAudit?.summary?.warningCount ?? 0)
  if (finalAudit?.schemaVersion !== REFURBISH_AUDIT_SCHEMA_VERSION) {
    push(
      report.errors,
      'error',
      'refurbish-audit-schema-version',
      `final audit schemaVersion must be ${REFURBISH_AUDIT_SCHEMA_VERSION}`,
      { schemaVersion: finalAudit?.schemaVersion ?? '' },
    )
  }
  if (finalAudit?.outcome !== 'passed') {
    push(report.errors, 'error', 'refurbish-audit-outcome', 'final audit did not pass', {
      outcome: finalAudit?.outcome ?? '',
    })
  }
  if (errorCount > 0) {
    push(report.errors, 'error', 'refurbish-audit-errors', 'final audit reported errors', {
      errorCount,
    })
    for (const issue of asArray(finalAudit?.issues).filter((item) => item.severity === 'error')) {
      push(report.errors, 'error', issue.code ?? 'refurbish-audit-issue', issue.message ?? '', {
        source: 'refurbish-audit',
        details: issue,
      })
    }
  }
  if (finalAudit?.summary?.slideCountMatches === false) {
    push(
      report.errors,
      'error',
      'refurbish-slide-count-mismatch',
      'final audit reports a source/final slide count mismatch',
      { sourceSlides: sourceCount, finalSlides: finalCount },
    )
  }
  if (Number.isInteger(sourceCount) && Number.isInteger(finalCount) && sourceCount !== finalCount) {
    push(
      report.errors,
      'error',
      'refurbish-slide-count-mismatch',
      `source slide count ${sourceCount} does not match final slide count ${finalCount}`,
      { sourceSlides: sourceCount, finalSlides: finalCount },
    )
  }
  addCheck(
    report.checks,
    'refurbish-final-audit',
    finalAudit?.schemaVersion === REFURBISH_AUDIT_SCHEMA_VERSION &&
      finalAudit?.outcome === 'passed' &&
      errorCount === 0 &&
      finalAudit?.summary?.slideCountMatches !== false
      ? 'passed'
      : 'failed',
    {
      status: finalAudit?.status ?? '',
      errorCount,
      warningCount,
      sourceSlides: sourceCount,
      finalSlides: finalCount,
    },
  )
}

function validateVisionDiff(report, visionDiff) {
  const fresh = visionCounts(visionDiff, 'new')
  const changed = visionCounts(visionDiff, 'changed')
  if (visionDiff?.schemaVersion !== VISION_DIFF_SCHEMA_VERSION) {
    push(
      report.errors,
      'error',
      'vision-diff-schema-version',
      `vision diff schemaVersion must be ${VISION_DIFF_SCHEMA_VERSION}`,
      { schemaVersion: visionDiff?.schemaVersion ?? '' },
    )
  }
  if (visionDiff?.status !== 'success') {
    push(report.errors, 'error', 'vision-diff-status', 'vision diff did not succeed', {
      status: visionDiff?.status ?? '',
    })
  }
  if (fresh.high > 0 || fresh.medium > 0) {
    push(
      report.errors,
      'error',
      'vision-diff-new-issue',
      'candidate introduced new high/medium visual issues',
      { new: fresh },
    )
  }
  if (changed.high > 0) {
    push(
      report.errors,
      'error',
      'vision-diff-changed-high',
      'candidate changed an inherited issue into high severity',
      { changed },
    )
  }
  addCheck(
    report.checks,
    'refurbish-vision-diff',
    visionDiff?.schemaVersion === VISION_DIFF_SCHEMA_VERSION &&
      visionDiff?.status === 'success' &&
      fresh.high === 0 &&
      fresh.medium === 0 &&
      changed.high === 0
      ? 'passed'
      : 'failed',
    { new: fresh, changed },
  )
}

function validateReferenceMap(report, referenceMap, sourceCount, finalCount) {
  if (!referenceMap) {
    push(
      report.warnings,
      'warning',
      'reference-map-missing',
      'reference-map.json is missing; relying on final audit and vision diff evidence',
    )
    addCheck(report.checks, 'refurbish-reference-map', 'warning', { mappedSlides: null })
    return
  }

  const entries = referenceMapEntries(referenceMap)
  const mappedOutputs = new Set()
  const mappedSources = new Set()
  if (entries.length === 0) {
    push(report.errors, 'error', 'reference-map-empty', 'reference map has no slide mappings')
  }
  for (const [index, entry] of entries.entries()) {
    const sourceSlide = sourceSlideForReferenceEntry(entry)
    if (
      Number.isInteger(sourceCount) &&
      (!Number.isInteger(sourceSlide) || !integerInRange(sourceSlide, sourceCount))
    ) {
      push(
        report.errors,
        'error',
        'reference-map-source-out-of-range',
        'reference map source slide is outside source slide count',
        { entry: index, sourceSlide, sourceCount },
      )
    } else if (Number.isInteger(sourceSlide)) {
      mappedSources.add(sourceSlide)
    }

    const outputSlides = outputSlidesForReferenceEntry(entry)
    if (outputSlides.length === 0) {
      push(
        report.errors,
        'error',
        'reference-map-output-missing',
        'reference map entry has no output slide',
        { entry: index },
      )
      continue
    }
    for (const outputSlide of outputSlides) {
      if (
        Number.isInteger(finalCount) &&
        (!Number.isInteger(outputSlide) || !integerInRange(outputSlide, finalCount))
      ) {
        push(
          report.errors,
          'error',
          'reference-map-output-out-of-range',
          'reference map output slide is outside final slide count',
          { entry: index, outputSlide, finalCount },
        )
      } else if (Number.isInteger(outputSlide)) {
        mappedOutputs.add(outputSlide)
      }
    }
  }
  if (Number.isInteger(finalCount)) {
    const missing = []
    for (let slide = 0; slide < finalCount; slide += 1) {
      if (!mappedOutputs.has(slide)) missing.push(slide)
    }
    if (missing.length > 0) {
      push(
        report.errors,
        'error',
        'reference-map-final-coverage',
        'reference map must cover every final slide',
        { finalCount, mappedSlides: mappedOutputs.size, missing },
      )
    }
  }
  addCheck(
    report.checks,
    'refurbish-reference-map',
    report.errors.some((item) => item.code.startsWith('reference-map-')) ? 'failed' : 'passed',
    {
      mappedSlides: mappedOutputs.size,
      mappedSourceSlides: mappedSources.size,
      finalSlides: finalCount,
    },
  )
  report.summary.mappedSlides = mappedOutputs.size
}

function buildReport(mode) {
  return {
    schemaVersion: SCHEMA_VERSION,
    mode,
    status: 'pass',
    summary: {
      errors: 0,
      warnings: 0,
      sourceSlides: null,
      finalSlides: null,
      mappedSlides: null,
    },
    checks: [],
    errors: [],
    warnings: [],
  }
}

function finalizeReport(report) {
  report.summary.errors = report.errors.length
  report.summary.warnings = report.warnings.length
  report.status = report.errors.length > 0 ? 'fail' : report.warnings.length > 0 ? 'warn' : 'pass'
  return report
}

function printHuman(report) {
  process.stdout.write(`pptx-nova fidelity gate: ${report.status}\n`)
  process.stdout.write(`- mode: ${report.mode}\n`)
  process.stdout.write(`- errors: ${report.summary.errors}\n`)
  process.stdout.write(`- warnings: ${report.summary.warnings}\n`)
  for (const item of [...report.errors, ...report.warnings]) {
    process.stdout.write(`- ${item.severity}: ${item.code}: ${item.message}\n`)
  }
}

let args = null
try {
  args = parseArgs(process.argv.slice(2))
  const report = buildReport(args.mode)
  if (args.mode === 'template-following') validateTemplateFollowing(args, report)
  else validateRefurbish(args, report)
  finalizeReport(report)
  if (args.json) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
  else printHuman(report)
  if (report.status === 'fail') process.exitCode = 1
} catch (error) {
  const report = {
    schemaVersion: SCHEMA_VERSION,
    mode: args?.mode ?? '',
    status: 'fail',
    summary: { errors: 1, warnings: 0, sourceSlides: null, finalSlides: null, mappedSlides: null },
    checks: [],
    errors: [
      {
        severity: 'error',
        code: 'fidelity-gate-error',
        message: error.message,
      },
    ],
    warnings: [],
  }
  if (args?.json) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
  else printHuman(report)
  process.exitCode = 1
}
