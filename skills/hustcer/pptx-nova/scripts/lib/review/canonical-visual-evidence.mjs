import { createHash } from 'node:crypto'
import { readFileSync, realpathSync } from 'node:fs'
import { dirname, resolve, relative, isAbsolute } from 'node:path'
import { validateDesignReview } from './design-quality.mjs'

const actions = new Set(['proceed', 'stop', 'require-human-confirmation'])
const outcomes = new Set(['pass', 'fail', 'skipped', 'inconclusive'])
const checkRegistry = [
  'input-integrity',
  'static-layout',
  'pdf-final-layout',
  'pdfium-raster',
  'pixel-diff',
  'ocr-overflow',
  'font-resolution',
  'region-attribution',
  'independent-reference',
  'policy',
]
const assurancesByAction = {
  proceed: new Set(['same-renderer-regression', 'candidate-checks']),
  stop: new Set(['content-blocked']),
  'require-human-confirmation': new Set([
    'candidate-only',
    'environment-dependent',
    'same-renderer-change-detected',
  ]),
}
const policyOutcomeByAction = {
  proceed: 'pass',
  stop: 'fail',
  'require-human-confirmation': 'inconclusive',
}

export function validateManifest(manifest) {
  const errors = []
  if (manifest?.schemaVersion !== 'pptx-visual-evidence/v1') {
    errors.push('schemaVersion must be pptx-visual-evidence/v1')
  }
  if (manifest?.status !== 'success') errors.push('status must be success')
  if (!Array.isArray(manifest?.checks) || manifest.checks.length === 0) {
    errors.push('checks must be a non-empty array')
  }
  const checks = new Map()
  for (const check of Array.isArray(manifest?.checks) ? manifest.checks : []) {
    if (!check || typeof check.id !== 'string' || !check.id) {
      errors.push('every check must have a non-empty id')
      continue
    }
    if (checks.has(check.id)) errors.push(`duplicate check id: ${check.id}`)
    checks.set(check.id, check)
    if (!outcomes.has(check.outcome)) {
      errors.push(`check ${check.id} has invalid outcome: ${String(check.outcome)}`)
    }
    if (check.required === true && check.outcome === 'skipped') {
      errors.push(`required check ${check.id} cannot be skipped`)
    }
  }
  const actualRegistry = Array.isArray(manifest?.checks)
    ? manifest.checks.map((check) => check?.id ?? null)
    : []
  if (JSON.stringify(actualRegistry) !== JSON.stringify(checkRegistry)) {
    errors.push(
      `check registry must exactly match pptx-visual-evidence/v1: ${checkRegistry.join(', ')}`,
    )
  }

  const action = manifest?.decision?.action
  const assurance = manifest?.decision?.assurance
  const create = manifest?.policyId === 'pptx-visual-oracle-create/v1'
  if (
    manifest.policyId &&
    !['pptx-visual-oracle-default/v1', 'pptx-visual-oracle-create/v1'].includes(manifest.policyId)
  )
    errors.push('unknown visual evidence policy')
  if (assurance === 'candidate-checks' && !create)
    errors.push('candidate-checks requires the explicit create policy')
  if (create && assurance === 'same-renderer-regression')
    errors.push('create cannot establish regression equivalence')
  if (create) {
    for (const id of [
      'input-integrity',
      'static-layout',
      'pdf-final-layout',
      'pdfium-raster',
      'policy',
    ]) {
      if (checks.get(id)?.required !== true) errors.push(`create requires check ${id}`)
    }
    if (
      checks.get('pixel-diff')?.required !== false ||
      checks.get('pixel-diff')?.outcome !== 'skipped'
    ) {
      errors.push('create must not claim a pixel regression comparison')
    }
    if (action === 'proceed' && assurance !== 'candidate-checks')
      errors.push('create proceed requires candidate-checks')
    if (
      action === 'proceed' &&
      manifest.findings?.some((f) => f.disposition !== 'contradicted-by-rendered-layout')
    ) {
      errors.push('create proceed cannot contain unresolved findings')
    }
  }
  if (!actions.has(action)) errors.push(`decision.action is invalid: ${String(action)}`)
  if (!assurancesByAction[action]?.has(assurance)) {
    errors.push(
      `decision assurance ${String(assurance)} is inconsistent with action ${String(action)}`,
    )
  }
  const policy = checks.get('policy')
  if (policy && policy.outcome !== policyOutcomeByAction[action]) {
    errors.push(
      `policy outcome ${String(policy.outcome)} is inconsistent with action ${String(action)}`,
    )
  }
  const requiredEvidenceChecks = [...checks.values()].filter(
    (check) => check.required === true && check.id !== 'policy',
  )
  if (action === 'stop' && !requiredEvidenceChecks.some((check) => check.outcome === 'fail')) {
    errors.push('stop requires at least one failed required evidence check')
  }
  if (action === 'proceed' && requiredEvidenceChecks.some((check) => check.outcome !== 'pass')) {
    errors.push('proceed requires every required check to pass')
  }
  return errors
}

export const REVIEW_CHECKS = [
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
]

export function fileSha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

/** Bind the current candidate and exact renderer artifacts, including opaque bytes.
 * This validates provenance/completeness; it does not perform visual understanding.
 */
export function captureVisualBinding(manifestPath, candidatePath) {
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  const errors = validateManifest(manifest)
  if (errors.length) throw new Error(errors.join('; '))
  if (!candidatePath) throw new Error('current --candidate is required for evidence binding')
  const candidate = manifest.subjects?.find((s) => s.id === 'candidate')
  const candidateSha256 = fileSha256(candidatePath)
  if (
    !candidate ||
    candidate.sha256 !== candidateSha256 ||
    candidate.byteLength !== readFileSync(candidatePath).length
  ) {
    throw new Error('candidate bytes do not match the canonical manifest')
  }
  const expected = Array.from({ length: candidate.slideCount }, (_, i) => i + 1)
  if (!expected.length || JSON.stringify(candidate.selectedSlides) !== JSON.stringify(expected)) {
    throw new Error('delivery review requires complete candidate slide coverage')
  }
  if (manifest.policyId === 'pptx-visual-oracle-create/v1' && manifest.subjects.length !== 1) {
    throw new Error('create evidence must contain only the candidate subject')
  }
  const root = realpathSync(dirname(manifestPath))
  const artifacts = (manifest.artifacts ?? []).map((a) => {
    if (!a?.path || isAbsolute(a.path))
      throw new Error('artifact must use a relative evidence path')
    const path = realpathSync(resolve(root, a.path))
    const local = relative(root, path)
    if (local === '..' || local.startsWith('../') || isAbsolute(local))
      throw new Error('artifact escapes the evidence directory')
    const bytes = readFileSync(path)
    const sha256 = fileSha256(path)
    if (bytes.length <= 0 || bytes.length !== a.byteLength || sha256 !== a.sha256)
      throw new Error(`stale renderer artifact: ${a.path}`)
    return {
      id: a.id,
      path: a.path,
      mimeType: a.mimeType,
      subjectId: a.subjectId,
      slide: a.slide,
      sha256,
      byteLength: bytes.length,
    }
  })
  const pages = artifacts.filter((a) => a.subjectId === 'candidate' && a.mimeType === 'image/png')
  if (JSON.stringify(pages.map((a) => a.slide).sort((a, b) => a - b)) !== JSON.stringify(expected))
    throw new Error('canonical PNG coverage is incomplete or duplicated')
  if (!artifacts.some((a) => a.subjectId === 'candidate' && a.mimeType === 'application/pdf'))
    throw new Error('canonical candidate PDF is missing')
  return {
    candidateSha256,
    manifestSha256: fileSha256(manifestPath),
    slideCount: candidate.slideCount,
    artifacts,
  }
}

export function evaluateVisualEvidence(
  manifestPath,
  { candidate = '', review = '', expectedDesignMode = '' } = {},
) {
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  const errors = validateManifest(manifest)
  const create = manifest.policyId === 'pptx-visual-oracle-create/v1'
  let binding
  if (!errors.length && (create || candidate)) {
    try {
      binding = captureVisualBinding(manifestPath, candidate)
    } catch (error) {
      errors.push(error.message)
    }
  }
  const report = gateReport(manifestPath, manifest, errors)
  report.machineChecksPassed = report.status === 'passed'
  if (create && report.status === 'passed') {
    report.deliveryAuthorized = false
    report.status = 'needs-visual-review'
    if (review) {
      try {
        const value = JSON.parse(readFileSync(review, 'utf8'))
        if (
          value.schemaVersion !== 'pptx-nova-visual-review/v1' ||
          value.mode !== 'create' ||
          value.status !== 'pass' ||
          !value.reviewer?.trim()
        )
          throw new Error('create requires a completed passing visual review')
        if (
          value.summary?.slidesReviewed !== binding.slideCount ||
          JSON.stringify(value.binding) !== JSON.stringify(binding)
        )
          throw new Error('visual review is stale or has incomplete candidate coverage')
        if (
          !Array.isArray(value.checks) ||
          REVIEW_CHECKS.some(
            (name) =>
              !value.checks.some((c) => c.name === name && ['pass', 'na'].includes(c.status)),
          )
        )
          throw new Error('visual review required checks are incomplete')
        if (
          value.checks.some((c) => !['pass', 'na'].includes(c.status)) ||
          value.errors?.length ||
          value.warnings?.length ||
          value.issues?.length
        )
          throw new Error('visual review contains unresolved findings')
        const designErrors = validateDesignReview(
          value.designReview,
          binding,
          expectedDesignMode ?? '',
        )
        if (designErrors.length) throw new Error(designErrors.join('; '))
        report.status = 'passed'
        report.deliveryAuthorized = true
      } catch (error) {
        report.status = 'invalid'
        report.errors.push(error.message)
      }
    }
  }
  return report
}

export function gateReport(manifestPath, manifest, errors) {
  const action = manifest?.decision?.action ?? null
  const status =
    errors.length > 0
      ? 'invalid'
      : action === 'proceed'
        ? 'passed'
        : action === 'stop'
          ? 'blocked'
          : 'review-required'
  return {
    schemaVersion: 'pptx-nova-visual-evidence-gate/v1',
    status,
    deliveryAuthorized: status === 'passed',
    manifest: manifestPath,
    decision: manifest?.decision ?? null,
    errors,
  }
}
