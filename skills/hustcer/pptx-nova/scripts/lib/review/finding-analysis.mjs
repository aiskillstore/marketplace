import { canonicalJsonV1, canonicalSha256V1 } from '../runtime/canonical-json.mjs'
import { LAYOUT_SNAPSHOT_SCHEMA_VERSION, layoutSemanticSha256 } from './layout-snapshot.mjs'
import { readResolvedSelectors } from '../pptx/resolved-selector.mjs'

const SCHEMA_VERSION = 'pptx-nova-finding-analysis/v1-draft'
const IDENTITY_SCHEMA_VERSION = 'pptx-nova-finding-analysis-identity/v1-draft'
const FINDING_KEY_SCHEMA_VERSION = 'pptx-nova-finding-key/v1'
const RULE_SET_VERSION = 'pptx-nova-finding-rules/v1-shadow.1'
const REVIEW_EVALUATION_SCHEMA_VERSION = 'pptx-nova-review-policy-evaluation/v1'
const HASH_RE = /^[0-9a-f]{64}$/
const WORKFLOW_MODES = new Set(['standard', 'studio', 'reference', 'structural', 'micro'])

const KNOWN_LAYOUT_CODES = new Set([
  'bbox-missing',
  'bbox-invalid',
  'bbox-off-canvas',
  'empty-placeholder',
  'default-placeholder-text',
  'font-family-missing',
  'font-size-missing',
  'font-size-too-small',
  'duplicate-object-id',
  'duplicate-object-name',
])

const DISPOSITION_PRIORITY = {
  block: 0,
  repair: 1,
  review: 2,
  informational: 3,
}

const ERROR_DEFINITIONS = {
  'finding-analysis-input-invalid': { phase: 1, nextAction: 'fix-analysis-input' },
  'finding-analysis-artifact-unreadable': {
    phase: 0,
    nextAction: 'regenerate-bound-evidence',
  },
  'finding-analysis-schema-unsupported': {
    phase: 2,
    nextAction: 'upgrade-or-regenerate-evidence',
  },
  'finding-analysis-binding-stale': { phase: 3, nextAction: 'regenerate-bound-evidence' },
  'finding-analysis-scope-invalid': { phase: 4, nextAction: 'rebuild-changed-scope' },
  'finding-analysis-mutation-evidence-invalid': {
    phase: 5,
    nextAction: 'rerun-mutation-evidence',
  },
  'finding-analysis-review-evaluation-invalid': {
    phase: 6,
    nextAction: 'rerun-review-policy-evaluation',
  },
  'finding-analysis-review-not-eligible': {
    phase: 6,
    nextAction: 'remove-ineligible-review-and-rerun',
  },
  'finding-analysis-rule-unsupported': { phase: 7, nextAction: 'add-or-upgrade-rule' },
  'finding-analysis-rule-failed': { phase: 7, nextAction: 'diagnose-rule' },
  'finding-analysis-output-invalid': { phase: 8, nextAction: 'diagnose-analysis-output' },
  'finding-analysis-internal-error': {
    phase: 9,
    nextAction: 'diagnose-analysis-internal-error',
  },
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function isPlainObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  const prototype = Object.getPrototypeOf(value)
  return prototype === Object.prototype || prototype === null
}

function cloneJson(value) {
  if (value === null || typeof value !== 'object') return value
  if (Array.isArray(value)) return value.map(cloneJson)
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, cloneJson(item)]))
}

function hashIdentity(schemaVersion, sha256) {
  return { schemaVersion, algorithm: 'sha256', sha256 }
}

function isSha256(value) {
  return typeof value === 'string' && HASH_RE.test(value)
}

function errorItem(code, message, details = {}) {
  if (!isPlainObject(details)) throw new TypeError('error details must be a plain object')
  return { code, message, ...details }
}

function diagnosticItem(code, message, details = {}) {
  if (!isPlainObject(details)) throw new TypeError('diagnostic details must be a plain object')
  return { code, message, ...details }
}

function compareText(left, right) {
  if (left === right) return 0
  return left < right ? -1 : 1
}

function compareIssues(left, right) {
  const leftPhase = ERROR_DEFINITIONS[left.code]?.phase ?? 99
  const rightPhase = ERROR_DEFINITIONS[right.code]?.phase ?? 99
  return (
    leftPhase - rightPhase ||
    compareText(String(left.code ?? ''), String(right.code ?? '')) ||
    compareText(String(left.findingKey ?? ''), String(right.findingKey ?? '')) ||
    compareText(String(left.reviewId ?? ''), String(right.reviewId ?? ''))
  )
}

function normalizedPartName(value, slideIndex) {
  const normalized = String(value ?? '')
    .replaceAll('\\', '/')
    .replace(/^\/+/, '')
  return normalized || `ppt/slides/slide${slideIndex + 1}.xml`
}

function workflowProjection(profile) {
  return {
    profileId:
      typeof profile?.profileId === 'string' ? profile.profileId : 'refurbish-shadow/v1-draft',
    kind: profile?.kind === 'refurbish' ? 'refurbish' : null,
    mode: WORKFLOW_MODES.has(profile?.mode) ? profile.mode : null,
    mutationIntent: profile?.mutationIntent === 'style' ? 'style' : null,
    deliveryStage: profile?.deliveryStage === 'final' ? 'final' : null,
  }
}

function bindingProjection(binding) {
  if (!binding) return null
  return {
    pptxSha256: binding.pptxSha256 ?? null,
    layoutArtifactSha256: binding.layoutArtifactSha256 ?? null,
    layoutSemanticSha256: binding.layoutSemanticSha256 ?? null,
  }
}

function outputBindings(input) {
  const mutation = input?.mutationEvidence
  const review = input?.reviewEvaluation
  return {
    assurance: input?.bindingContext?.assurance ?? null,
    schemaDeclaredInputs: cloneJson(asArray(input?.bindingContext?.schemaDeclaredInputs)),
    source: bindingProjection(input?.sourceLayout?.binding),
    candidate: bindingProjection(input?.candidateLayout?.binding),
    changedScope: input?.changedScope
      ? {
          origin: input.changedScope.origin ?? null,
          evidenceArtifactSha256: input.changedScope.binding?.evidenceArtifactSha256 ?? null,
        }
      : null,
    mutationEvidence: {
      dryRunArtifactSha256: mutation?.dryRun?.artifactSha256 ?? null,
      applyArtifactSha256: mutation?.apply?.artifactSha256 ?? null,
      semanticDiffArtifactSha256: mutation?.semanticDiff?.artifactSha256 ?? null,
      patchSha256:
        mutation?.apply?.binding?.patchSha256 ?? mutation?.dryRun?.binding?.patchSha256 ?? null,
    },
    reviewEvaluation: review
      ? {
          artifactSha256: review.artifactSha256 ?? null,
          status: review.report?.status ?? null,
          sourcePptxSha256: review.report?.bindings?.source?.sha256 ?? null,
          candidatePptxSha256: review.report?.bindings?.candidate?.sha256 ?? null,
        }
      : null,
  }
}

function failedReport(input, errors, diagnostics = []) {
  const sortedErrors = [...errors].sort(compareIssues)
  const requestedEnforcement = input?.executionPolicy?.enforcement
  const enforcement = ['shadow', 'required', 'optional'].includes(requestedEnforcement)
    ? requestedEnforcement
    : 'shadow'
  const highest = sortedErrors[0]
  const nextAction =
    ERROR_DEFINITIONS[highest?.code]?.nextAction ?? 'diagnose-analysis-internal-error'
  const report = {
    schemaVersion: SCHEMA_VERSION,
    evaluation: {
      status: 'failed',
      errors: sortedErrors,
      diagnostics: [...diagnostics].sort(compareIssues),
    },
    workflowProfile: workflowProjection(input?.workflowProfile),
    bindings: outputBindings(input),
    policy: { ruleSetVersion: RULE_SET_VERSION },
    analysisIdentity: null,
    findings: [],
    resolvedFindings: [],
    summary: { countsComplete: false, errorCount: sortedErrors.length },
    agentGate: {
      enforcement,
      proposedStatus: 'fail',
      effectiveStatus: enforcement === 'required' ? 'fail' : 'not-applied',
      governingFindingKeys: [],
      nextAction,
    },
  }
  validateFindingAnalysisReport(report)
  return report
}

function validateWorkflowAndBindings(input, errors, diagnostics) {
  const profile = input?.workflowProfile
  const execution = input?.executionPolicy
  const assurance = input?.bindingContext?.assurance
  if (!isPlainObject(profile) || profile.kind !== 'refurbish') {
    errors.push(
      errorItem(
        'finding-analysis-input-invalid',
        'shadow MVP supports only the refurbish workflow profile',
      ),
    )
  }
  if (!WORKFLOW_MODES.has(profile?.mode)) {
    errors.push(errorItem('finding-analysis-input-invalid', 'workflowProfile.mode is invalid'))
  }
  if (profile?.mutationIntent !== 'style' || profile?.deliveryStage !== 'final') {
    errors.push(
      errorItem(
        'finding-analysis-input-invalid',
        'refurbish shadow requires mutationIntent=style and deliveryStage=final',
      ),
    )
  }
  if (!['human-in-loop', 'unattended'].includes(execution?.automation)) {
    errors.push(
      errorItem('finding-analysis-input-invalid', 'executionPolicy.automation is invalid'),
    )
  }
  if (!['shadow', 'required', 'optional'].includes(execution?.enforcement)) {
    errors.push(
      errorItem('finding-analysis-input-invalid', 'executionPolicy.enforcement is invalid'),
    )
  }
  if (execution?.enforcement === 'optional') {
    errors.push(
      errorItem(
        'finding-analysis-input-invalid',
        'the refurbish profile cannot lower Finding Analysis to optional',
      ),
    )
  }
  if (!['runner-observed', 'advisory-replay'].includes(assurance)) {
    errors.push(errorItem('finding-analysis-input-invalid', 'binding assurance is invalid'))
  }
  if (execution?.enforcement === 'required' && assurance !== 'runner-observed') {
    errors.push(
      errorItem(
        'finding-analysis-input-invalid',
        'required enforcement needs a runner-observed binding envelope',
      ),
    )
  } else if (assurance === 'advisory-replay') {
    diagnostics.push(
      diagnosticItem(
        'finding-analysis-advisory-replay',
        'evidence was rehashed outside the trusted runner command chain and is advisory only',
      ),
    )
  }

  validateLayoutEnvelope(input?.sourceLayout, 'source', true, errors)
  validateLayoutEnvelope(input?.candidateLayout, 'candidate', true, errors)
}

function validateLayoutEnvelope(envelope, label, required, errors) {
  if (!envelope) {
    if (required) {
      errors.push(
        errorItem('finding-analysis-input-invalid', `${label} layout evidence is required`),
      )
    }
    return
  }
  const report = envelope.report
  const binding = envelope.binding
  if (report?.schemaVersion !== LAYOUT_SNAPSHOT_SCHEMA_VERSION) {
    errors.push(
      errorItem('finding-analysis-schema-unsupported', `${label} layout schema is unsupported`, {
        schemaVersion: report?.schemaVersion ?? null,
      }),
    )
    return
  }
  if (!['pass', 'warn'].includes(report?.status)) {
    errors.push(
      errorItem('finding-analysis-input-invalid', `${label} layout did not complete successfully`),
    )
  }
  for (const field of ['pptxSha256', 'layoutArtifactSha256', 'layoutSemanticSha256']) {
    if (!isSha256(binding?.[field])) {
      errors.push(
        errorItem('finding-analysis-input-invalid', `${label} layout binding ${field} is invalid`),
      )
    }
  }
  if (isSha256(binding?.layoutSemanticSha256)) {
    try {
      const actual = layoutSemanticSha256(report)
      if (actual !== binding.layoutSemanticSha256) {
        errors.push(
          errorItem(
            'finding-analysis-binding-stale',
            `${label} layout semantic hash does not match the supplied report`,
            { expectedSha256: binding.layoutSemanticSha256, actualSha256: actual },
          ),
        )
      }
    } catch (error) {
      errors.push(
        errorItem(
          'finding-analysis-input-invalid',
          `${label} layout cannot be canonicalized: ${error.message}`,
        ),
      )
    }
  }
}

function validateChangedScope(input, errors) {
  const scope = input?.changedScope
  if (!scope) return
  if (!['full-deck', 'slides', 'objects'].includes(scope.mode)) {
    errors.push(errorItem('finding-analysis-scope-invalid', 'changedScope.mode is invalid'))
    return
  }
  const slideIndexes = asArray(scope.slideIndexes)
  const objectIds = asArray(scope.objectIds)
  if (
    slideIndexes.some((value) => !Number.isInteger(value) || value < 0) ||
    new Set(slideIndexes).size !== slideIndexes.length
  ) {
    errors.push(
      errorItem('finding-analysis-scope-invalid', 'changedScope slide indexes must be unique'),
    )
  }
  if (
    objectIds.some(
      (value) =>
        !isPlainObject(value) ||
        !Number.isInteger(value.slideIndex) ||
        value.slideIndex < 0 ||
        value.shapeId === null ||
        value.shapeId === undefined,
    )
  ) {
    errors.push(errorItem('finding-analysis-scope-invalid', 'changedScope object ids are invalid'))
  }
  if (scope.mode === 'full-deck' && (slideIndexes.length > 0 || objectIds.length > 0)) {
    errors.push(
      errorItem(
        'finding-analysis-scope-invalid',
        'full-deck scope must not list slides or objects',
      ),
    )
  }
  if (scope.mode === 'slides' && (slideIndexes.length === 0 || objectIds.length > 0)) {
    errors.push(
      errorItem('finding-analysis-scope-invalid', 'slides scope needs slides and no objects'),
    )
  }
  if (scope.mode === 'objects' && objectIds.length === 0) {
    errors.push(errorItem('finding-analysis-scope-invalid', 'objects scope needs object ids'))
  }
  const sourceSha = input?.sourceLayout?.binding?.pptxSha256 ?? null
  const candidateSha = input?.candidateLayout?.binding?.pptxSha256 ?? null
  if (
    scope.binding?.candidatePptxSha256 !== candidateSha ||
    scope.binding?.sourcePptxSha256 !== sourceSha
  ) {
    errors.push(errorItem('finding-analysis-scope-invalid', 'changedScope binding is stale'))
  }
}

function validateMutationEvidence(input, errors, diagnostics) {
  const mutation = input?.mutationEvidence
  const sourceSha = input?.sourceLayout?.binding?.pptxSha256
  const candidateSha = input?.candidateLayout?.binding?.pptxSha256
  if (!mutation?.semanticDiff) {
    errors.push(
      errorItem(
        'finding-analysis-mutation-evidence-invalid',
        'refurbish analysis requires semantic diff evidence',
      ),
    )
    return
  }
  const semantic = mutation.semanticDiff
  if (semantic.report?.schemaVersion !== 'pptx-diff/v1' || semantic.report?.status !== 'success') {
    errors.push(
      errorItem(
        'finding-analysis-schema-unsupported',
        'semantic diff must be successful pptx-diff/v1 evidence',
      ),
    )
  }
  if (!isSha256(semantic.artifactSha256)) {
    errors.push(
      errorItem(
        'finding-analysis-mutation-evidence-invalid',
        'semantic diff artifact SHA-256 is invalid',
      ),
    )
  }
  if (
    semantic.binding?.sourcePptxSha256 !== sourceSha ||
    semantic.binding?.candidatePptxSha256 !== candidateSha
  ) {
    errors.push(
      errorItem('finding-analysis-mutation-evidence-invalid', 'semantic diff binding is stale'),
    )
  }

  validateOperationEvidence(mutation.dryRun, 'dryRun', sourceSha, candidateSha, errors)
  validateOperationEvidence(mutation.apply, 'apply', sourceSha, candidateSha, errors)
  const dryPatch = mutation.dryRun?.binding?.patchSha256
  const applyPatch = mutation.apply?.binding?.patchSha256
  if (dryPatch && applyPatch && dryPatch !== applyPatch) {
    errors.push(
      errorItem(
        'finding-analysis-mutation-evidence-invalid',
        'dry-run and apply evidence use different patch SHA-256 values',
      ),
    )
  }
  if (!mutation.dryRun && !mutation.apply) {
    diagnostics.push(
      diagnosticItem(
        'finding-analysis-operation-evidence-missing',
        'this refurbish route has no dry-run/apply report; selector usage remains unknown',
      ),
    )
  }
}

function validateOperationEvidence(envelope, stage, sourceSha, candidateSha, errors) {
  if (!envelope) return
  const expectedSchema = stage === 'dryRun' ? 'pptx-dry-run/v1' : 'pptx-apply/v1'
  if (envelope.report?.schemaVersion !== expectedSchema || envelope.report?.status !== 'success') {
    errors.push(
      errorItem(
        'finding-analysis-mutation-evidence-invalid',
        `${stage} evidence must be successful ${expectedSchema}`,
      ),
    )
  }
  if (!isSha256(envelope.artifactSha256) || !isSha256(envelope.binding?.patchSha256)) {
    errors.push(
      errorItem(
        'finding-analysis-mutation-evidence-invalid',
        `${stage} artifact or patch SHA-256 is invalid`,
      ),
    )
  }
  if (envelope.binding?.sourcePptxSha256 !== sourceSha) {
    errors.push(
      errorItem('finding-analysis-mutation-evidence-invalid', `${stage} source binding is stale`),
    )
  }
  if (stage === 'apply' && envelope.binding?.candidatePptxSha256 !== candidateSha) {
    errors.push(
      errorItem('finding-analysis-mutation-evidence-invalid', 'apply candidate binding is stale'),
    )
  }
  try {
    if (!Array.isArray(envelope.report?.opResults))
      throw new TypeError('opResults must be an array')
    for (const result of envelope.report.opResults) readResolvedSelectors(result)
  } catch (error) {
    errors.push(
      errorItem('finding-analysis-mutation-evidence-invalid', `${stage}: ${error.message}`),
    )
  }
}

function validateReviewEvaluation(input, errors) {
  const envelope = input?.reviewEvaluation
  if (!envelope) return
  const report = envelope.report
  const sourceSha = input?.sourceLayout?.binding?.pptxSha256
  const candidateSha = input?.candidateLayout?.binding?.pptxSha256
  const layoutArtifactSha = input?.candidateLayout?.binding?.layoutArtifactSha256
  if (!isPlainObject(report) || report.schemaVersion !== REVIEW_EVALUATION_SCHEMA_VERSION) {
    errors.push(
      errorItem('finding-analysis-schema-unsupported', 'review evaluation schema is unsupported'),
    )
    return
  }
  if (
    !isPlainObject(report.bindings) ||
    !isPlainObject(report.bindings.evidence) ||
    !Array.isArray(report.applied) ||
    !Array.isArray(report.errors)
  ) {
    errors.push(
      errorItem(
        'finding-analysis-review-evaluation-invalid',
        'review evaluation must contain complete bindings, applied, and errors fields',
      ),
    )
  }
  if (report.status !== 'pass' || asArray(report.errors).length > 0) {
    errors.push(
      errorItem(
        'finding-analysis-review-evaluation-invalid',
        'review policy evaluation did not pass atomically',
        { evaluationErrors: cloneJson(asArray(report.errors)) },
      ),
    )
  }
  if (!isSha256(envelope.artifactSha256)) {
    errors.push(
      errorItem(
        'finding-analysis-review-evaluation-invalid',
        'review evaluation artifact SHA-256 is invalid',
      ),
    )
  }
  if (
    report.bindings?.source?.sha256 !== sourceSha ||
    report.bindings?.candidate?.sha256 !== candidateSha ||
    report.bindings?.evidence?.layoutSnapshot?.sha256 !== layoutArtifactSha
  ) {
    errors.push(
      errorItem(
        'finding-analysis-review-evaluation-invalid',
        'review evaluation bindings do not match the current source, candidate, and layout',
      ),
    )
  }
}

function slideIndexOfRisk(risk) {
  const value = Number(risk?.slideIndex ?? risk?.slide)
  return Number.isInteger(value) && value >= 0 ? value : null
}

function indexLayout(layout) {
  const slides = new Map()
  for (const slide of asArray(layout?.slides)) {
    const slideIndex = Number(slide?.index)
    if (!Number.isInteger(slideIndex) || slideIndex < 0) continue
    const byId = new Map()
    const byName = new Map()
    for (const object of asArray(slide?.objects)) {
      if (object?.id !== null && object?.id !== undefined) byId.set(String(object.id), object)
      if (object?.name !== null && object?.name !== undefined && object.name !== '') {
        const key = String(object.name)
        const group = byName.get(key) ?? []
        group.push(object)
        byName.set(key, group)
      }
    }
    slides.set(slideIndex, {
      slide,
      partName: normalizedPartName(slide?.partName, slideIndex),
      byId,
      byName,
    })
  }
  return slides
}

function stableTargetForRisk(risk, layoutIndex) {
  const slideIndex = slideIndexOfRisk(risk)
  if (slideIndex === null) throw new Error('layout finding has no valid slide index')
  const slide = layoutIndex.get(slideIndex)
  const slidePart = normalizedPartName(risk?.slidePart ?? slide?.partName, slideIndex)
  const code = String(risk?.code ?? '')
  if (code === 'duplicate-object-name') {
    return { slidePart, duplicateName: String(risk?.name ?? '') }
  }
  if (code === 'duplicate-object-id') {
    return { slidePart, duplicateShapeId: String(risk?.id ?? '') }
  }
  if (code === 'font-size-too-small') {
    return { slidePart, shapeId: String(risk?.objectId ?? ''), sizePt: risk?.sizePt }
  }
  const shapeId = risk?.objectId ?? risk?.shapeId
  if (shapeId !== null && shapeId !== undefined && shapeId !== '') {
    return { slidePart, shapeId: String(shapeId) }
  }
  if (code === 'empty-placeholder') {
    return {
      slidePart,
      placeholderType: String(risk?.placeholder?.type ?? 'obj'),
      placeholderIdx: String(risk?.placeholder?.idx ?? '0'),
    }
  }
  throw new Error(`${code} finding has no stable shape target`)
}

function findingKeyForRisk(risk, layoutIndex) {
  const stableTargetKey = stableTargetForRisk(risk, layoutIndex)
  const sha256 = canonicalSha256V1({
    schemaVersion: FINDING_KEY_SCHEMA_VERSION,
    detectorKind: 'layout',
    code: String(risk.code),
    stableTargetKey,
  })
  return { identity: hashIdentity(FINDING_KEY_SCHEMA_VERSION, sha256), stableTargetKey }
}

function relatedObjectProjection(object) {
  if (!object) return null
  return {
    shapeId: object.id ?? null,
    name: object.name ?? null,
    type: object.type ?? null,
    bbox: cloneJson(object.bbox ?? null),
    zOrder: object.zOrder ?? null,
    placeholder: cloneJson(object.placeholder ?? null),
    textPreview: object.textPreview ?? '',
  }
}

function compareRelatedObjects(left, right) {
  return (
    compareText(String(left?.shapeId ?? ''), String(right?.shapeId ?? '')) ||
    compareText(String(left?.name ?? ''), String(right?.name ?? '')) ||
    Number(left?.zOrder ?? 0) - Number(right?.zOrder ?? 0)
  )
}

function relatedObjectsForRisk(risk, layoutIndex) {
  const slide = layoutIndex.get(slideIndexOfRisk(risk))
  if (!slide) return []
  let objects = []
  if (risk.code === 'duplicate-object-name') {
    objects = slide.byName.get(String(risk.name ?? '')) ?? []
  } else if (risk.code === 'duplicate-object-id') {
    const id = String(risk.id ?? '')
    objects = asArray(slide.slide?.objects).filter((object) => String(object?.id ?? '') === id)
  } else {
    const object = slide.byId.get(String(risk.objectId ?? risk.shapeId ?? ''))
    if (object) objects = [object]
  }
  return objects.map(relatedObjectProjection).filter(Boolean).sort(compareRelatedObjects)
}

function rawFindingEvidence(risk) {
  const evidence = { ...(risk ?? {}) }
  delete evidence.message
  delete evidence.previewFile
  delete evidence.slideNumber
  return evidence
}

function evidenceDigest(risk, relatedObjects) {
  if (!risk) return null
  return hashIdentity(
    'pptx-nova-finding-evidence/v1-draft',
    canonicalSha256V1({
      schemaVersion: 'pptx-nova-finding-evidence/v1-draft',
      rawFinding: rawFindingEvidence(risk),
      relatedObjects,
    }),
  )
}

function targetForRisk(risk, stableTargetKey) {
  const slideIndex = slideIndexOfRisk(risk)
  return {
    slideIndex,
    slideNumber: slideIndex + 1,
    slidePart: stableTargetKey.slidePart,
    ...(stableTargetKey.shapeId ? { shapeId: stableTargetKey.shapeId } : {}),
  }
}

function selectorUsageForDuplicateName(name, slideIndex, mutationEvidence) {
  const evidence = []
  for (const [stage, envelope] of [
    ['planned', mutationEvidence?.dryRun],
    ['applied', mutationEvidence?.apply],
  ]) {
    if (!envelope) continue
    for (const result of asArray(envelope.report?.opResults)) {
      if (result?.status && result.status !== 'success') continue
      for (const selector of readResolvedSelectors(result)) {
        if (selector.input.name === name && selector.resolved.slide === slideIndex) {
          evidence.push({
            stage,
            opIndex: Number.isInteger(result?.opIndex) ? result.opIndex : null,
            field: selector?.field ?? null,
          })
        }
      }
    }
  }
  evidence.sort((left, right) => {
    const stage = (left.stage === 'applied' ? 0 : 1) - (right.stage === 'applied' ? 0 : 1)
    return stage || Number(left.opIndex ?? -1) - Number(right.opIndex ?? -1)
  })
  const status = evidence.some((item) => item.stage === 'applied')
    ? 'applied'
    : evidence.some((item) => item.stage === 'planned')
      ? 'planned'
      : 'unknown'
  return { status, evidence }
}

function deltaForCandidate({
  candidateRisk,
  candidateDigest,
  sourceEntry,
  sourceLayoutIndex,
  candidateRelated,
}) {
  if (!sourceLayoutIndex) {
    return { status: 'no-baseline', matchMode: 'none', confidence: 'deterministic' }
  }
  if (sourceEntry) {
    const sourceCount = sourceEntry.relatedObjects.length
    const candidateCount = candidateRelated.length
    const status =
      sourceEntry.digest.sha256 === candidateDigest.sha256
        ? 'unchanged'
        : candidateCount > sourceCount
          ? 'worsened'
          : 'changed'
    return { status, matchMode: 'finding-key', confidence: 'deterministic' }
  }
  if (candidateRisk.code === 'empty-placeholder') {
    const slide = sourceLayoutIndex.get(slideIndexOfRisk(candidateRisk))
    const sourceObject = slide?.byId.get(
      String(candidateRisk.objectId ?? candidateRisk.shapeId ?? ''),
    )
    if (sourceObject && String(sourceObject.textPreview ?? '') !== '') {
      return { status: 'worsened', matchMode: 'shape-id', confidence: 'deterministic' }
    }
  }
  return { status: 'introduced', matchMode: 'finding-key', confidence: 'deterministic' }
}

function findingInScope(finding, scope) {
  if (!scope || scope.mode === 'full-deck') return true
  if (scope.mode === 'slides')
    return asArray(scope.slideIndexes).includes(finding.target.slideIndex)
  return asArray(scope.objectIds).some(
    (target) =>
      target.slideIndex === finding.target.slideIndex &&
      String(target.shapeId) === String(finding.target.shapeId),
  )
}

function reviewState(disposition, eligibility) {
  if (eligibility === 'not-required') {
    return { eligibility, status: 'not-requested', evaluationRef: null }
  }
  return {
    eligibility,
    status: disposition === 'informational' ? 'not-requested' : 'pending',
    evaluationRef: null,
  }
}

function analyzeDuplicateName(context) {
  const { risk, relatedObjects, delta, mutationEvidence } = context
  const selectorUsage = selectorUsageForDuplicateName(
    String(risk.name ?? ''),
    slideIndexOfRisk(risk),
    mutationEvidence,
  )
  const ids = relatedObjects.map((object) => String(object.shapeId ?? ''))
  const idsUnique = ids.every(Boolean) && new Set(ids).size === ids.length
  let disposition = 'review'
  let action = 'use-id-selector'
  let eligibility = 'reviewable'
  const basisCodes = ['duplicate-name-does-not-change-rendering', 'name-selector-is-ambiguous']
  if (idsUnique) basisCodes.push('related-objects-have-distinct-ids')
  if (selectorUsage.status !== 'unknown') {
    disposition = 'block'
    action = 'replace-name-selector'
    eligibility = 'non-reviewable'
    basisCodes.push(`ambiguous-name-selector-${selectorUsage.status}`)
  } else if (delta.status === 'unchanged' && idsUnique) {
    disposition = 'informational'
    eligibility = 'not-required'
    basisCodes.push('finding-inherited-unchanged')
  } else if (delta.status === 'introduced' || delta.status === 'worsened') {
    basisCodes.push('candidate-introduced-or-worsened-finding')
  }
  return {
    selectorUsage,
    impact: {
      visual: { likelihood: 'unlikely', severity: 'none' },
      content: 'none',
      structural: delta.status === 'introduced' || delta.status === 'worsened' ? 'medium' : 'low',
      selector: 'high',
      editability: idsUnique ? 'low' : 'high',
      confidence: 'deterministic',
      basisCodes,
    },
    decision: {
      disposition,
      action,
      autoExecutable: false,
      requiredEvidence:
        action === 'replace-name-selector'
          ? ['id-selector-and-rerun-mutation-evidence']
          : ['id-selector-or-hash-bound-review'],
      rationale:
        selectorUsage.status === 'unknown'
          ? '名称重复不会直接改变渲染，但按名称选择对象存在歧义。'
          : '本轮 operation evidence 使用了歧义名称 selector，必须改用稳定 ID。',
    },
    review: reviewState(disposition, eligibility),
  }
}

function placeholderRole(risk, relatedObjects) {
  return String(risk?.placeholder?.type ?? relatedObjects[0]?.placeholder?.type ?? 'unknown')
}

function analyzeEmptyPlaceholder(context) {
  const { risk, relatedObjects, delta } = context
  const role = placeholderRole(risk, relatedObjects)
  const structuralRole = ['sldNum', 'dt', 'ftr'].includes(role)
  const contentRole = ['title', 'subTitle', 'body', 'obj'].includes(role)
  let disposition = 'review'
  let action = structuralRole ? 'submit-hash-bound-review' : 'fill-placeholder'
  let eligibility = 'reviewable'
  const basisCodes = [`placeholder-role-${role || 'unknown'}`]
  if (delta.status === 'worsened' && contentRole) {
    disposition = 'block'
    eligibility = 'non-reviewable'
    action = 'fill-placeholder'
    basisCodes.push('source-content-became-empty')
  } else if ((delta.status === 'introduced' || delta.status === 'worsened') && !structuralRole) {
    disposition = 'repair'
    eligibility = contentRole ? 'non-reviewable' : 'reviewable'
    action = contentRole ? 'fill-placeholder' : 'manual-review'
    basisCodes.push('candidate-introduced-empty-placeholder')
  } else if (delta.status === 'unchanged' && structuralRole) {
    basisCodes.push('structural-placeholder-inherited-empty')
  } else if (delta.status === 'unchanged') {
    basisCodes.push('finding-inherited-unchanged')
  }
  return {
    selectorUsage: { status: 'unknown', evidence: [] },
    impact: {
      visual: {
        likelihood: structuralRole ? 'unlikely' : contentRole ? 'likely' : 'unknown',
        severity: structuralRole ? 'none' : contentRole ? 'high' : 'unknown',
      },
      content: structuralRole ? 'none' : contentRole ? 'high' : 'unknown',
      structural: structuralRole ? 'low' : 'medium',
      selector: 'none',
      editability: 'low',
      confidence: role === 'unknown' ? 'unknown' : 'deterministic',
      basisCodes,
    },
    decision: {
      disposition,
      action,
      autoExecutable: false,
      requiredEvidence:
        action === 'submit-hash-bound-review'
          ? ['hash-bound-review']
          : ['updated-candidate-layout-and-semantic-diff'],
      rationale: structuralRole
        ? `空 ${role} placeholder 通常不承载正文，但仍需保留明确的人工接受证据。`
        : '空内容 placeholder 可能造成内容丢失或未完成页面，需检查并修复。',
    },
    review: reviewState(disposition, eligibility),
  }
}

function analyzeConservativePassThrough(context) {
  const informational = context.risk?.classification === 'informational'
  const disposition = informational ? 'informational' : 'review'
  const eligibility = informational ? 'not-required' : 'reviewable'
  return {
    selectorUsage: { status: 'unknown', evidence: [] },
    impact: {
      visual: { likelihood: 'unknown', severity: 'unknown' },
      content: 'unknown',
      structural: informational ? 'none' : 'unknown',
      selector: 'unknown',
      editability: 'unknown',
      confidence: 'unknown',
      basisCodes: [
        informational
          ? 'legacy-informational-classification-preserved'
          : 'legacy-actionable-classification-preserved',
      ],
    },
    decision: {
      disposition,
      action: informational ? 'none' : 'inspect-preview',
      autoExecutable: false,
      requiredEvidence: informational ? [] : ['manual-layout-review'],
      rationale: informational
        ? '沿用 detector 的 informational 分类。'
        : 'Shadow MVP 尚未为该 code 启用专用规则，保持原有 review 严格度。',
    },
    review: reviewState(disposition, eligibility),
  }
}

function analyzeRule(context) {
  if (context.risk.code === 'duplicate-object-name') return analyzeDuplicateName(context)
  if (context.risk.code === 'empty-placeholder') return analyzeEmptyPlaceholder(context)
  return analyzeConservativePassThrough(context)
}

function buildSourceEntries(sourceLayout, sourceIndex, errors) {
  const entries = new Map()
  if (!sourceLayout) return entries
  for (const [findingIndex, risk] of asArray(sourceLayout.risks).entries()) {
    if (!KNOWN_LAYOUT_CODES.has(risk?.code)) {
      errors.push(
        errorItem(
          'finding-analysis-rule-unsupported',
          `layout finding code ${JSON.stringify(risk?.code ?? '')} is unsupported`,
          { detectorFindingIndex: findingIndex },
        ),
      )
      continue
    }
    try {
      const key = findingKeyForRisk(risk, sourceIndex)
      const relatedObjects = relatedObjectsForRisk(risk, sourceIndex)
      const digest = evidenceDigest(risk, relatedObjects)
      if (entries.has(key.identity.sha256)) {
        errors.push(
          errorItem(
            'finding-analysis-output-invalid',
            'source layout contains duplicate findingKey values',
            { findingKey: key.identity.sha256 },
          ),
        )
      } else {
        entries.set(key.identity.sha256, {
          risk,
          findingIndex,
          key,
          relatedObjects,
          digest,
        })
      }
    } catch (error) {
      errors.push(
        errorItem('finding-analysis-rule-unsupported', error.message, {
          detectorFindingIndex: findingIndex,
          code: risk?.code ?? null,
        }),
      )
    }
  }
  return entries
}

function buildCandidateFindings(input, sourceEntries, sourceIndex, candidateIndex, errors) {
  const findings = []
  const seenKeys = new Set()
  for (const [findingIndex, risk] of asArray(input.candidateLayout.report?.risks).entries()) {
    if (!KNOWN_LAYOUT_CODES.has(risk?.code)) {
      errors.push(
        errorItem(
          'finding-analysis-rule-unsupported',
          `layout finding code ${JSON.stringify(risk?.code ?? '')} is unsupported`,
          { detectorFindingIndex: findingIndex },
        ),
      )
      continue
    }
    try {
      const key = findingKeyForRisk(risk, candidateIndex)
      if (seenKeys.has(key.identity.sha256)) {
        errors.push(
          errorItem(
            'finding-analysis-output-invalid',
            'candidate layout contains duplicate findingKey values',
            { findingKey: key.identity.sha256 },
          ),
        )
        continue
      }
      seenKeys.add(key.identity.sha256)
      const relatedObjects = relatedObjectsForRisk(risk, candidateIndex)
      const sourceEntry = sourceEntries.get(key.identity.sha256) ?? null
      const candidateDigest = evidenceDigest(risk, relatedObjects)
      const delta = deltaForCandidate({
        candidateRisk: risk,
        candidateDigest,
        sourceEntry,
        sourceLayoutIndex: sourceIndex,
        candidateRelated: relatedObjects,
      })
      const base = {
        findingKey: key.identity,
        evidenceDigest: { source: sourceEntry?.digest ?? null, candidate: candidateDigest },
        detector: {
          kind: 'layout',
          schemaVersion: input.candidateLayout.report.schemaVersion,
          artifactSha256: input.candidateLayout.binding.layoutArtifactSha256,
          findingIndex,
          reviewIdentity: cloneJson(risk.reviewIdentity ?? null),
        },
        rawFinding: cloneJson(risk),
        target: targetForRisk(risk, key.stableTargetKey),
        relatedObjects,
        delta,
      }
      const analysis = analyzeRule({
        ...base,
        risk,
        sourceEntry,
        mutationEvidence: input.mutationEvidence,
      })
      findings.push({ ...base, ...analysis })
    } catch (error) {
      errors.push(
        errorItem('finding-analysis-rule-failed', error.message, {
          detectorFindingIndex: findingIndex,
          code: risk?.code ?? null,
        }),
      )
    }
  }
  for (const finding of findings)
    finding.inChangedScope = findingInScope(finding, input.changedScope)
  return findings
}

function buildResolvedFindings(input, sourceEntries, candidateFindings) {
  const candidateKeys = new Set(candidateFindings.map((finding) => finding.findingKey.sha256))
  const resolved = []
  for (const source of sourceEntries.values()) {
    if (candidateKeys.has(source.key.identity.sha256)) continue
    resolved.push({
      findingKey: source.key.identity,
      evidenceDigest: { source: source.digest, candidate: null },
      detector: {
        kind: 'layout',
        schemaVersion: input.sourceLayout.report.schemaVersion,
        artifactSha256: input.sourceLayout.binding.layoutArtifactSha256,
        findingIndex: source.findingIndex,
        reviewIdentity: cloneJson(source.risk.reviewIdentity ?? null),
      },
      rawFinding: cloneJson(source.risk),
      target: targetForRisk(source.risk, source.key.stableTargetKey),
      relatedObjects: source.relatedObjects,
      delta: { status: 'resolved', matchMode: 'finding-key', confidence: 'deterministic' },
    })
  }
  return resolved.sort(compareFindingOrder)
}

function reviewFingerprintOf(finding) {
  return finding?.rawFinding?.reviewIdentity?.sha256 ?? null
}

function applyReviewEvaluation(input, findings, errors, diagnostics) {
  const evaluation = input.reviewEvaluation?.report
  if (!evaluation || evaluation.status !== 'pass') return
  const byFingerprint = new Map()
  for (const finding of findings) {
    const fingerprint = reviewFingerprintOf(finding)
    if (fingerprint) byFingerprint.set(fingerprint, finding)
  }
  const matches = []
  for (const applied of asArray(evaluation.applied)) {
    const finding = byFingerprint.get(String(applied?.findingSha256 ?? ''))
    if (!finding) {
      errors.push(
        errorItem(
          'finding-analysis-review-evaluation-invalid',
          'an applied review does not match a current raw finding fingerprint',
          { reviewId: applied?.reviewId ?? null, findingSha256: applied?.findingSha256 ?? null },
        ),
      )
      continue
    }
    matches.push({ applied, finding })
  }
  const ineligible = matches.filter(
    ({ finding }) => finding.review.eligibility === 'non-reviewable',
  )
  if (ineligible.length > 0) {
    for (const { applied, finding } of ineligible) {
      errors.push(
        errorItem(
          'finding-analysis-review-not-eligible',
          'review policy attempted to accept a non-reviewable finding',
          {
            reviewId: applied.reviewId ?? null,
            findingSha256: applied.findingSha256 ?? null,
            findingKey: finding.findingKey.sha256,
            findingCode: finding.rawFinding.code,
            disposition: finding.decision.disposition,
            eligibility: finding.review.eligibility,
          },
        ),
      )
    }
    return
  }
  if (errors.length > 0) return
  for (const { applied, finding } of matches) {
    const evaluationRef = {
      reviewId: applied.reviewId,
      findingSha256: applied.findingSha256,
      evaluationArtifactSha256: input.reviewEvaluation.artifactSha256,
    }
    if (finding.delta.status !== 'unchanged') {
      finding.review = { ...finding.review, status: 'stale', evaluationRef }
      diagnostics.push(
        diagnosticItem(
          'finding-analysis-review-context-stale',
          'v1 review fingerprint does not cover the current Finding Analysis context',
          {
            reviewId: applied.reviewId,
            findingKey: finding.findingKey.sha256,
            deltaStatus: finding.delta.status,
          },
        ),
      )
    } else {
      finding.review = { ...finding.review, status: 'accepted', evaluationRef }
    }
  }
}

function unresolved(finding) {
  if (!finding?.decision || !finding?.review) return false
  if (finding.decision.disposition === 'informational') return false
  return finding.review.status !== 'accepted'
}

function compareFindingOrder(left, right) {
  const leftPriority = unresolved(left)
    ? (DISPOSITION_PRIORITY[left.decision?.disposition] ?? 9)
    : 4
  const rightPriority = unresolved(right)
    ? (DISPOSITION_PRIORITY[right.decision?.disposition] ?? 9)
    : 4
  return (
    leftPriority - rightPriority ||
    Number(left.target?.slideIndex ?? 0) - Number(right.target?.slideIndex ?? 0) ||
    compareText(String(left.rawFinding?.code ?? ''), String(right.rawFinding?.code ?? '')) ||
    compareText(String(left.findingKey?.sha256 ?? ''), String(right.findingKey?.sha256 ?? ''))
  )
}

function aggregateGate(findings, executionPolicy) {
  const active = findings.filter(unresolved)
  const highest = active.reduce((value, finding) => {
    const priority = DISPOSITION_PRIORITY[finding.decision.disposition]
    return priority < value ? priority : value
  }, 99)
  const governing = active
    .filter((finding) => DISPOSITION_PRIORITY[finding.decision.disposition] === highest)
    .map((finding) => finding.findingKey.sha256)
  const hasFailure = highest === 0 || highest === 1
  const hasReview = highest === 2
  const proposedStatus = hasFailure
    ? 'fail'
    : hasReview
      ? executionPolicy.automation === 'unattended'
        ? 'fail'
        : 'warn'
      : 'pass'
  const nextAction =
    highest === 0
      ? 'stop'
      : highest === 1
        ? 'repair-listed-findings'
        : highest === 2
          ? 'review-listed-findings'
          : 'publish'
  return {
    enforcement: executionPolicy.enforcement,
    proposedStatus,
    effectiveStatus: executionPolicy.enforcement === 'required' ? proposedStatus : 'not-applied',
    governingFindingKeys: governing,
    nextAction,
  }
}

function summarize(findings, resolvedFindings, agentGate) {
  const byDisposition = { informational: 0, review: 0, repair: 0, block: 0 }
  const byReviewStatus = {
    'not-requested': 0,
    pending: 0,
    accepted: 0,
    invalid: 0,
    stale: 0,
  }
  const byDeltaStatus = {}
  for (const finding of findings) {
    byDisposition[finding.decision.disposition] += 1
    byReviewStatus[finding.review.status] += 1
    byDeltaStatus[finding.delta.status] = (byDeltaStatus[finding.delta.status] ?? 0) + 1
  }
  const governing = new Set(agentGate.governingFindingKeys)
  const shapeTopFinding = (finding) => ({
    findingKey: finding.findingKey.sha256,
    code: finding.rawFinding.code,
    slideNumber: finding.target.slideNumber,
    disposition: finding.decision.disposition,
    action: finding.decision.action,
    reviewStatus: finding.review.status,
    deltaStatus: finding.delta.status,
    basisCodes: finding.impact.basisCodes,
  })
  const prioritized = [
    ...findings.filter((finding) => governing.has(finding.findingKey.sha256)),
    ...findings.filter(
      (finding) =>
        !governing.has(finding.findingKey.sha256) &&
        finding.decision.disposition !== 'informational',
    ),
  ].map(shapeTopFinding)
  const aggregatedInformational = new Map()
  for (const finding of findings) {
    if (governing.has(finding.findingKey.sha256)) continue
    if (finding.decision.disposition !== 'informational') continue
    const code = finding.rawFinding.code
    const entry = aggregatedInformational.get(code)
    if (entry) {
      entry.aggregatedCount += 1
      if (
        entry.aggregatedSlideNumbers.length < 8 &&
        !entry.aggregatedSlideNumbers.includes(finding.target.slideNumber)
      ) {
        entry.aggregatedSlideNumbers.push(finding.target.slideNumber)
      }
    } else {
      aggregatedInformational.set(code, {
        ...shapeTopFinding(finding),
        aggregated: true,
        aggregatedCount: 1,
        aggregatedSlideNumbers: [finding.target.slideNumber],
      })
    }
  }
  const topFindings = [...prioritized, ...aggregatedInformational.values()].slice(0, 5)
  return {
    countsComplete: true,
    findingCount: findings.length,
    unresolvedFindingCount: findings.filter(unresolved).length,
    resolvedFindingCount: resolvedFindings.length,
    byDisposition,
    byReviewStatus,
    byDeltaStatus,
    topFindings,
  }
}

function scopeDigest(scope) {
  if (!scope) return null
  return {
    mode: scope.mode,
    origin: scope.origin,
    sourcePptxSha256: scope.binding?.sourcePptxSha256 ?? null,
    candidatePptxSha256: scope.binding?.candidatePptxSha256 ?? null,
    slideIndexes: [...asArray(scope.slideIndexes)].sort((a, b) => a - b),
    objectIds: [...asArray(scope.objectIds)]
      .map((item) => ({ slideIndex: item.slideIndex, shapeId: String(item.shapeId) }))
      .sort(
        (left, right) =>
          left.slideIndex - right.slideIndex || compareText(left.shapeId, right.shapeId),
      ),
  }
}

function operationDigest(envelope) {
  if (!envelope) return null
  const schemaVersion = envelope.report?.schemaVersion ?? null
  const binding = {
    sourcePptxSha256: envelope.binding?.sourcePptxSha256 ?? null,
    patchSha256: envelope.binding?.patchSha256 ?? null,
  }
  if (schemaVersion === 'pptx-apply/v1') {
    binding.candidatePptxSha256 = envelope.binding?.candidatePptxSha256 ?? null
  }
  return {
    schemaVersion,
    status: envelope.report?.status ?? null,
    binding,
    opResults: asArray(envelope.report?.opResults)
      .map((result) => ({
        opIndex: result?.opIndex ?? null,
        op: result?.op ?? null,
        status: result?.status ?? null,
        resolvedSelectors: asArray(result?.resolvedSelectors)
          .map((selector) => ({
            field: selector?.field ?? null,
            input: cloneJson(selector?.input ?? null),
            resolved: cloneJson(selector?.resolved ?? null),
          }))
          .sort((left, right) => compareText(canonicalJsonV1(left), canonicalJsonV1(right))),
        semanticChanges: asArray(result?.semanticChanges)
          .map((change) => cloneJson(change))
          .sort((left, right) => compareText(canonicalJsonV1(left), canonicalJsonV1(right))),
      }))
      .sort((left, right) => Number(left.opIndex ?? -1) - Number(right.opIndex ?? -1)),
  }
}

function mutationDigest(mutation) {
  if (!mutation) return null
  return {
    dryRun: operationDigest(mutation.dryRun),
    apply: operationDigest(mutation.apply),
    semanticDiff: mutation.semanticDiff
      ? {
          schemaVersion: mutation.semanticDiff.report?.schemaVersion ?? null,
          status: mutation.semanticDiff.report?.status ?? null,
          binding: {
            sourcePptxSha256: mutation.semanticDiff.binding?.sourcePptxSha256 ?? null,
            candidatePptxSha256: mutation.semanticDiff.binding?.candidatePptxSha256 ?? null,
          },
          slides: cloneJson(asArray(mutation.semanticDiff.report?.slides)).sort((left, right) =>
            compareText(canonicalJsonV1(left), canonicalJsonV1(right)),
          ),
        }
      : null,
  }
}

function reviewDigest(review) {
  if (!review) return null
  const report = review.report
  return {
    schemaVersion: report?.schemaVersion ?? null,
    status: report?.status ?? null,
    bindings: {
      expectedSourceSha256: report?.bindings?.expectedSourceSha256 ?? null,
      sourceSha256: report?.bindings?.source?.sha256 ?? null,
      candidateSha256: report?.bindings?.candidate?.sha256 ?? null,
      evidence: Object.fromEntries(
        Object.entries(report?.bindings?.evidence ?? {})
          .map(([name, identity]) => [name, identity?.sha256 ?? null])
          .sort(([left], [right]) => compareText(left, right)),
      ),
    },
    applied: asArray(report?.applied)
      .map((item) => ({
        reviewId: item?.reviewId ?? null,
        findingSha256: item?.findingSha256 ?? null,
        disposition: item?.disposition ?? null,
        reason: item?.reason ?? null,
      }))
      .sort((left, right) => compareText(canonicalJsonV1(left), canonicalJsonV1(right))),
    errors: cloneJson(asArray(report?.errors)).sort((left, right) =>
      compareText(canonicalJsonV1(left), canonicalJsonV1(right)),
    ),
  }
}

function analysisIdentity(input, findings) {
  const value = {
    schemaVersion: IDENTITY_SCHEMA_VERSION,
    ruleSetVersion: RULE_SET_VERSION,
    workflowProfile: workflowProjection(input.workflowProfile),
    sourceBinding: {
      pptxSha256: input.sourceLayout.binding.pptxSha256,
      layoutSemanticSha256: input.sourceLayout.binding.layoutSemanticSha256,
    },
    candidateBinding: {
      pptxSha256: input.candidateLayout.binding.pptxSha256,
      layoutSemanticSha256: input.candidateLayout.binding.layoutSemanticSha256,
    },
    changedScopeDigest: scopeDigest(input.changedScope),
    mutationEvidenceDigest: mutationDigest(input.mutationEvidence),
    reviewEvaluationDigest: reviewDigest(input.reviewEvaluation),
    findingEvidence: findings
      .map((finding) => ({
        findingKey: finding.findingKey.sha256,
        sourceEvidenceDigest: finding.evidenceDigest.source?.sha256 ?? null,
        candidateEvidenceDigest: finding.evidenceDigest.candidate?.sha256 ?? null,
      }))
      .sort((left, right) => compareText(left.findingKey, right.findingKey)),
  }
  return hashIdentity(IDENTITY_SCHEMA_VERSION, canonicalSha256V1(value))
}

function validateFindingAnalysisReport(report) {
  if (report?.schemaVersion !== SCHEMA_VERSION) throw new Error('report schemaVersion is invalid')
  if (
    !isPlainObject(report.evaluation) ||
    !Array.isArray(report.evaluation.errors) ||
    !Array.isArray(report.evaluation.diagnostics) ||
    !isPlainObject(report.workflowProfile) ||
    !isPlainObject(report.bindings) ||
    !isPlainObject(report.policy) ||
    !Array.isArray(report.findings) ||
    !Array.isArray(report.resolvedFindings) ||
    !isPlainObject(report.summary) ||
    !isPlainObject(report.agentGate)
  ) {
    throw new Error('report is missing required envelope fields')
  }
  if (!['complete', 'failed'].includes(report?.evaluation?.status)) {
    throw new Error('evaluation status is invalid')
  }
  if (report.policy.ruleSetVersion !== RULE_SET_VERSION) {
    throw new Error('report ruleSetVersion is invalid')
  }
  if (
    !['shadow', 'required', 'optional'].includes(report.agentGate.enforcement) ||
    !['pass', 'warn', 'fail'].includes(report.agentGate.proposedStatus) ||
    !['not-applied', 'pass', 'warn', 'fail'].includes(report.agentGate.effectiveStatus) ||
    !Array.isArray(report.agentGate.governingFindingKeys) ||
    typeof report.agentGate.nextAction !== 'string'
  ) {
    throw new Error('agentGate contract is invalid')
  }
  const governingKeys = report.agentGate.governingFindingKeys
  if (
    governingKeys.some((key) => !isSha256(key)) ||
    new Set(governingKeys).size !== governingKeys.length
  ) {
    throw new Error('agentGate governing finding keys are invalid')
  }
  if (report.evaluation.status === 'failed') {
    if (
      report.analysisIdentity !== null ||
      report.evaluation.errors.length === 0 ||
      report.findings.length > 0 ||
      report.resolvedFindings.length > 0 ||
      report.agentGate.proposedStatus !== 'fail'
    ) {
      throw new Error('failed report discriminant is invalid')
    }
    if (
      report.summary.countsComplete !== false ||
      report.summary.errorCount !== report.evaluation.errors.length
    ) {
      throw new Error('failed report must mark countsComplete=false')
    }
    const expectedEffective = report.agentGate.enforcement === 'required' ? 'fail' : 'not-applied'
    if (report.agentGate.effectiveStatus !== expectedEffective) {
      throw new Error('failed report effectiveStatus is invalid')
    }
    return
  }
  if (
    report.analysisIdentity?.schemaVersion !== IDENTITY_SCHEMA_VERSION ||
    report.analysisIdentity?.algorithm !== 'sha256' ||
    !isSha256(report.analysisIdentity?.sha256) ||
    report.evaluation.errors.length > 0 ||
    report.summary.countsComplete !== true
  ) {
    throw new Error('complete report identity/errors are invalid')
  }
  const keys = report.findings.map((finding) => finding.findingKey?.sha256)
  if (keys.some((key) => !isSha256(key)) || new Set(keys).size !== keys.length) {
    throw new Error('finding keys must be valid and unique')
  }
  if (report.summary.findingCount !== report.findings.length) {
    throw new Error('summary findingCount is inconsistent')
  }
  if (report.summary.resolvedFindingCount !== report.resolvedFindings.length) {
    throw new Error('summary resolvedFindingCount is inconsistent')
  }
  if (report.summary.unresolvedFindingCount !== report.findings.filter(unresolved).length) {
    throw new Error('summary unresolvedFindingCount is inconsistent')
  }
  const resolvedKeys = report.resolvedFindings.map((finding) => finding.findingKey?.sha256)
  if (
    resolvedKeys.some((key) => !isSha256(key)) ||
    new Set(resolvedKeys).size !== resolvedKeys.length ||
    resolvedKeys.some((key) => keys.includes(key))
  ) {
    throw new Error('resolved finding keys must be valid, unique, and disjoint')
  }
  if (
    report.agentGate.enforcement === 'shadow' &&
    report.agentGate.effectiveStatus !== 'not-applied'
  ) {
    throw new Error('shadow analysis cannot contribute an effective gate status')
  }
  for (const finding of report.findings) {
    const rawReview = finding.rawFinding?.reviewIdentity ?? null
    if (canonicalJsonV1(rawReview) !== canonicalJsonV1(finding.detector?.reviewIdentity ?? null)) {
      throw new Error('raw and detector review identities diverged')
    }
    if (finding.decision?.autoExecutable !== false) {
      throw new Error('shadow MVP decisions must not be auto executable')
    }
    if (
      !['informational', 'review', 'repair', 'block'].includes(finding.decision?.disposition) ||
      !['not-required', 'reviewable', 'non-reviewable'].includes(finding.review?.eligibility) ||
      !['not-requested', 'pending', 'accepted', 'invalid', 'stale'].includes(finding.review?.status)
    ) {
      throw new Error('finding decision/review enum is invalid')
    }
  }
}

function buildCompleteReport(input, findings, resolvedFindings, diagnostics) {
  findings.sort(compareFindingOrder)
  const agentGate = aggregateGate(findings, input.executionPolicy)
  const summary = summarize(findings, resolvedFindings, agentGate)
  return {
    schemaVersion: SCHEMA_VERSION,
    evaluation: {
      status: 'complete',
      errors: [],
      diagnostics: [...diagnostics].sort(compareIssues),
    },
    workflowProfile: workflowProjection(input.workflowProfile),
    bindings: outputBindings(input),
    policy: { ruleSetVersion: RULE_SET_VERSION },
    analysisIdentity: analysisIdentity(input, findings),
    findings,
    resolvedFindings,
    summary,
    agentGate,
  }
}

export function annotateTopActionable(topActionable, findingReport) {
  const findings = Array.isArray(findingReport?.findings) ? findingReport.findings : []
  if (!Array.isArray(topActionable) || topActionable.length === 0 || findings.length === 0) {
    return topActionable
  }
  const byCode = new Map()
  for (const finding of findings) {
    const code = String(finding?.rawFinding?.code ?? '')
    if (!code) continue
    const delta = String(finding?.delta?.status ?? 'unknown')
    const entry = byCode.get(code) ?? { inheritedCount: 0, introducedCount: 0, otherCount: 0 }
    if (delta === 'unchanged') entry.inheritedCount += 1
    else if (delta === 'introduced') entry.introducedCount += 1
    else entry.otherCount += 1
    byCode.set(code, entry)
  }
  return topActionable.map((group) => {
    const counts = byCode.get(String(group?.code ?? ''))
    if (!counts) return group
    const { inheritedCount, introducedCount, otherCount } = counts
    const deltaStatus =
      inheritedCount > 0 && introducedCount === 0 && otherCount === 0
        ? 'unchanged'
        : introducedCount > 0 && inheritedCount === 0 && otherCount === 0
          ? 'introduced'
          : 'mixed'
    return {
      ...group,
      deltaStatus,
      inherited: deltaStatus === 'unchanged',
      inheritedCount,
      introducedCount,
    }
  })
}

export function evaluateFindings(input) {
  const errors = []
  const diagnostics = []
  try {
    validateWorkflowAndBindings(input, errors, diagnostics)
    validateChangedScope(input, errors)
    validateMutationEvidence(input, errors, diagnostics)
    validateReviewEvaluation(input, errors)
    if (errors.length > 0) return failedReport(input, errors, diagnostics)

    const sourceIndex = indexLayout(input.sourceLayout.report)
    const candidateIndex = indexLayout(input.candidateLayout.report)
    const sourceEntries = buildSourceEntries(input.sourceLayout.report, sourceIndex, errors)
    const findings = buildCandidateFindings(
      input,
      sourceEntries,
      sourceIndex,
      candidateIndex,
      errors,
    )
    if (errors.length > 0) return failedReport(input, errors, diagnostics)
    const resolvedFindings = buildResolvedFindings(input, sourceEntries, findings)
    applyReviewEvaluation(input, findings, errors, diagnostics)
    if (errors.length > 0) return failedReport(input, errors, diagnostics)

    const report = buildCompleteReport(input, findings, resolvedFindings, diagnostics)
    try {
      validateFindingAnalysisReport(report)
      return report
    } catch (error) {
      return failedReport(
        input,
        [errorItem('finding-analysis-output-invalid', error.message)],
        diagnostics,
      )
    }
  } catch (error) {
    return failedReport(
      input,
      [errorItem('finding-analysis-internal-error', error.message)],
      diagnostics,
    )
  }
}
