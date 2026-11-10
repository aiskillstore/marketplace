import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

export const REVIEW_POLICY_SCHEMA_VERSION = 'pptx-nova-review-policy/v1'
export const REVIEW_POLICY_EVALUATION_SCHEMA_VERSION = 'pptx-nova-review-policy-evaluation/v1'
export const REVIEW_FINDING_SCHEMA_VERSION = 'pptx-nova-review-finding/v1'

const LEGACY_TARGET_REVIEW_CODES = new Set(['empty-placeholder'])
const SUPPORTED_DISPOSITIONS = new Set(['accepted'])
const REVIEW_CODE_PATTERN = /^[a-z][a-z0-9-]*$/

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

export function hasEmbeddedReviewedFindings(value) {
  if (!isPlainObject(value)) return false
  if ('reviewedFindings' in value) {
    return !Array.isArray(value.reviewedFindings) || value.reviewedFindings.length > 0
  }
  if ('reviewPolicy' in value) {
    const policy = value.reviewPolicy
    if (!isPlainObject(policy)) return true
    if ('reviewedFindings' in policy) {
      return !Array.isArray(policy.reviewedFindings) || policy.reviewedFindings.length > 0
    }
  }
  return false
}

function canonicalScalar(value) {
  return value === null || value === undefined ? '' : String(value)
}

function canonicalSha256(value) {
  const normalized = String(value ?? '')
    .trim()
    .toLowerCase()
  return /^[0-9a-f]{64}$/.test(normalized) ? normalized : ''
}

function unknownKeys(value, allowed) {
  if (!isPlainObject(value)) return []
  return Object.keys(value).filter((key) => !allowed.has(key))
}

function rejectUnknownKeys(value, allowed, errors, context) {
  const keys = unknownKeys(value, allowed)
  if (keys.length === 0) return
  errors.push({
    code: 'review-policy-unknown-properties',
    message: `${context} contains unsupported properties: ${keys.join(', ')}`,
    context,
    properties: keys,
  })
}

function fileIdentity(path) {
  if (!path) return null
  const absolutePath = resolve(path)
  if (!existsSync(absolutePath)) return { path: absolutePath, missing: true }
  const bytes = readFileSync(absolutePath)
  return {
    path: absolutePath,
    byteLength: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  }
}

function policyFromDocument(document, allowEmbeddedPolicy) {
  if (!isPlainObject(document)) return null
  if (String(document.schemaVersion ?? '').startsWith('pptx-nova-review-policy/')) {
    return document
  }
  if (!allowEmbeddedPolicy) return null
  if (isPlainObject(document.reviewPolicy)) return document.reviewPolicy
  if (Array.isArray(document.reviewedFindings) || isPlainObject(document.bindings)) {
    return {
      schemaVersion: REVIEW_POLICY_SCHEMA_VERSION,
      bindings: document.bindings ?? {},
      reviewedFindings: document.reviewedFindings ?? [],
    }
  }
  return null
}

function findingLocation(finding) {
  return {
    slideIndex: Number(finding?.slideIndex ?? finding?.slide),
    part: String(finding?.part ?? finding?.slidePart ?? ''),
    shapeId: canonicalScalar(finding?.shapeId ?? finding?.objectId),
    placeholder: {
      // ISO/IEC 29500 defaults omitted p:ph attributes to type="obj" and idx="0".
      type: canonicalScalar(finding?.placeholder?.type) || 'obj',
      idx: canonicalScalar(finding?.placeholder?.idx) || '0',
    },
  }
}

function canonicalJson(value) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value
  if (typeof value === 'number') return Number.isFinite(value) ? value : String(value)
  if (Array.isArray(value)) return value.map((item) => canonicalJson(item ?? null))
  if (!isPlainObject(value)) return String(value ?? '')
  const result = {}
  for (const key of Object.keys(value).sort()) {
    if (value[key] !== undefined) result[key] = canonicalJson(value[key])
  }
  return result
}

const FINDING_ENVELOPE_KEYS = new Set([
  'classification',
  'code',
  'message',
  'objectId',
  'objectName',
  'objectType',
  'part',
  'placeholder',
  'previewFile',
  'review',
  'reviewIdentity',
  'severity',
  'shapeId',
  'slide',
  'slideIndex',
  'slideNumber',
  'slidePart',
])

function reviewFindingContract(finding) {
  const location = findingLocation(finding)
  const target = {
    slideIndex: Number.isFinite(location.slideIndex) ? location.slideIndex : null,
    part: location.part,
  }
  if (location.shapeId) {
    target.shapeId = location.shapeId
  } else {
    const objectName = canonicalScalar(finding?.objectName)
    const objectType = canonicalScalar(finding?.objectType)
    if (objectName) target.objectName = objectName
    if (objectType) target.objectType = objectType
  }
  if (isPlainObject(finding?.placeholder)) target.placeholder = location.placeholder

  const evidence = {}
  for (const [key, value] of Object.entries(finding ?? {})) {
    if (!FINDING_ENVELOPE_KEYS.has(key) && value !== undefined) evidence[key] = value
  }
  return canonicalJson({
    schemaVersion: REVIEW_FINDING_SCHEMA_VERSION,
    code: String(finding?.code ?? ''),
    target,
    evidence,
  })
}

export function reviewFindingSha256(finding) {
  return createHash('sha256')
    .update(JSON.stringify(reviewFindingContract(finding)))
    .digest('hex')
}

export function reviewFindingIdentity(finding) {
  return {
    schemaVersion: REVIEW_FINDING_SCHEMA_VERSION,
    algorithm: 'sha256',
    sha256: reviewFindingSha256(finding),
  }
}

function ruleTarget(rule) {
  const target = isPlainObject(rule?.target) ? rule.target : {}
  return {
    slideIndex: Number(target.slideIndex),
    part: String(target.part ?? ''),
    shapeId: canonicalScalar(target.shapeId),
    placeholder: {
      type: canonicalScalar(target.placeholder?.type),
      idx: canonicalScalar(target.placeholder?.idx),
    },
  }
}

function targetKey(code, target) {
  return [
    code,
    target.slideIndex,
    target.part,
    target.shapeId,
    target.placeholder.type,
    target.placeholder.idx,
  ].join('|')
}

function findingMatchesRule(finding, rule) {
  if (finding?.code !== rule.code) return false
  if (finding?.classification !== 'actionable') return false
  if (rule.matchMode === 'fingerprint') {
    return reviewFindingSha256(finding) === rule.findingSha256
  }
  const actual = findingLocation(finding)
  const expected = rule.target
  return (
    actual.slideIndex === expected.slideIndex &&
    actual.part === expected.part &&
    actual.shapeId === expected.shapeId &&
    actual.placeholder.type === expected.placeholder.type &&
    actual.placeholder.idx === expected.placeholder.idx &&
    finding?.observed?.textEmpty === true &&
    rule.expected.textEmpty === true
  )
}

function normalizeRules(policy, errors) {
  const rules = []
  const seenIds = new Set()
  const seenTargets = new Set()
  for (const [index, value] of asArray(policy?.reviewedFindings).entries()) {
    if (!isPlainObject(value)) {
      errors.push({
        code: 'review-rule-invalid',
        message: `reviewedFindings[${index}] must be an object`,
        ruleIndex: index,
      })
      continue
    }
    const id = String(value.id ?? '').trim()
    const code = String(value.code ?? '').trim()
    const disposition = String(value.disposition ?? '').trim()
    const reason = String(value.reason ?? '').trim()
    const findingSha256 = canonicalSha256(value.findingSha256)
    const fingerprintMode = value.findingSha256 !== undefined
    const target = ruleTarget(value)
    const expected = isPlainObject(value.expected) ? value.expected : {}
    let valid = true

    rejectUnknownKeys(
      value,
      new Set(['id', 'code', 'disposition', 'findingSha256', 'target', 'expected', 'reason']),
      errors,
      `reviewedFindings[${index}]`,
    )
    rejectUnknownKeys(
      value.target,
      new Set(['slideIndex', 'part', 'shapeId', 'placeholder']),
      errors,
      `reviewedFindings[${index}].target`,
    )
    rejectUnknownKeys(
      value.target?.placeholder,
      new Set(['type', 'idx']),
      errors,
      `reviewedFindings[${index}].target.placeholder`,
    )
    rejectUnknownKeys(
      value.expected,
      new Set(['textEmpty']),
      errors,
      `reviewedFindings[${index}].expected`,
    )

    if (!id) {
      errors.push({
        code: 'review-rule-id-missing',
        message: `reviewedFindings[${index}] must declare a stable id`,
        ruleIndex: index,
      })
      valid = false
    } else if (seenIds.has(id)) {
      errors.push({
        code: 'review-rule-id-duplicate',
        message: `reviewed finding id ${JSON.stringify(id)} is duplicated`,
        ruleIndex: index,
        reviewId: id,
      })
      valid = false
    } else {
      seenIds.add(id)
    }
    if (!REVIEW_CODE_PATTERN.test(code)) {
      errors.push({
        code: 'review-rule-code-invalid',
        message: `reviewed finding ${JSON.stringify(id || index)} has an invalid finding code ${JSON.stringify(code)}`,
        ruleIndex: index,
        reviewId: id || null,
      })
      valid = false
    }
    if (!SUPPORTED_DISPOSITIONS.has(disposition)) {
      errors.push({
        code: 'review-rule-disposition-unsupported',
        message: `reviewed finding ${JSON.stringify(id || index)} must use disposition "accepted"`,
        ruleIndex: index,
        reviewId: id || null,
      })
      valid = false
    }
    if (!reason) {
      errors.push({
        code: 'review-rule-reason-missing',
        message: `reviewed finding ${JSON.stringify(id || index)} must explain why the finding is intentional`,
        ruleIndex: index,
        reviewId: id || null,
      })
      valid = false
    }
    if (fingerprintMode) {
      if (!findingSha256) {
        errors.push({
          code: 'review-rule-fingerprint-invalid',
          message: `reviewed finding ${JSON.stringify(id || index)} must declare a valid findingSha256`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
      if (value.target !== undefined || value.expected !== undefined) {
        errors.push({
          code: 'review-rule-match-mode-conflict',
          message: `reviewed finding ${JSON.stringify(id || index)} must use either findingSha256 or legacy target/expected matching, not both`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
    } else {
      if (!LEGACY_TARGET_REVIEW_CODES.has(code)) {
        errors.push({
          code: 'review-rule-fingerprint-required',
          message: `reviewed finding ${JSON.stringify(id || index)} with code ${JSON.stringify(code)} must bind findingSha256`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
      if (!Number.isInteger(target.slideIndex) || target.slideIndex < 0) {
        errors.push({
          code: 'review-rule-slide-invalid',
          message: `reviewed finding ${JSON.stringify(id || index)} has an invalid zero-based slideIndex`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
      if (!target.part || !target.shapeId || !target.placeholder.type || !target.placeholder.idx) {
        errors.push({
          code: 'review-rule-target-incomplete',
          message: `reviewed finding ${JSON.stringify(id || index)} must identify part, shapeId, placeholder type, and placeholder idx`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
      if (expected.textEmpty !== true) {
        errors.push({
          code: 'review-rule-expectation-invalid',
          message: `reviewed finding ${JSON.stringify(id || index)} must explicitly require expected.textEmpty=true`,
          ruleIndex: index,
          reviewId: id || null,
        })
        valid = false
      }
    }

    const key = fingerprintMode ? `${code}|sha256|${findingSha256}` : targetKey(code, target)
    if (seenTargets.has(key)) {
      errors.push({
        code: 'review-rule-target-duplicate',
        message: `multiple reviewed findings target the same exact finding ${JSON.stringify(key)}`,
        ruleIndex: index,
        reviewId: id || null,
      })
      valid = false
    } else {
      seenTargets.add(key)
    }

    if (valid) {
      rules.push(
        fingerprintMode
          ? {
              id,
              code,
              disposition,
              reason,
              matchMode: 'fingerprint',
              findingSha256,
            }
          : {
              id,
              code,
              disposition,
              reason,
              matchMode: 'legacy-target',
              target,
              expected: { textEmpty: true },
            },
      )
    }
  }
  return rules
}

function evidenceIdentities(paths) {
  const identities = {}
  for (const [name, path] of Object.entries(paths ?? {})) {
    if (!path) continue
    identities[name] = fileIdentity(path)
  }
  return identities
}

export function evaluateReviewPolicy({
  policyDocument = null,
  policyDocumentPath = '',
  allowEmbeddedPolicy = false,
  sourcePptx = '',
  candidatePptx = '',
  findings = [],
  evidencePaths = {},
} = {}) {
  const errors = []
  const policy = policyFromDocument(policyDocument, allowEmbeddedPolicy)
  const source = fileIdentity(sourcePptx)
  const candidate = fileIdentity(candidatePptx)
  const policyIdentity = fileIdentity(policyDocumentPath)
  const evidence = evidenceIdentities(evidencePaths)
  const declaredFindings = asArray(policy?.reviewedFindings)

  if (policyDocument !== null && policyDocument !== undefined && !policy) {
    errors.push({
      code: 'review-policy-document-invalid',
      message:
        'review policy document must be pptx-nova-review-policy/v1 or embed reviewPolicy/reviewedFindings',
    })
  }

  if (policy && policy.reviewedFindings !== undefined && !Array.isArray(policy.reviewedFindings)) {
    errors.push({
      code: 'review-policy-findings-invalid',
      message: 'review policy reviewedFindings must be an array',
    })
  }
  if (policy && !isPlainObject(policy.bindings)) {
    errors.push({
      code: 'review-policy-bindings-invalid',
      message: 'review policy bindings must be an object',
    })
  }
  if (policy && policy.schemaVersion !== REVIEW_POLICY_SCHEMA_VERSION) {
    errors.push({
      code: 'review-policy-schema-version',
      message: `review policy schemaVersion must be ${REVIEW_POLICY_SCHEMA_VERSION}`,
      schemaVersion: policy.schemaVersion ?? '',
    })
  }
  if (policy) {
    rejectUnknownKeys(
      policy,
      new Set(['schemaVersion', 'bindings', 'reviewedFindings']),
      errors,
      'review policy',
    )
    rejectUnknownKeys(policy.bindings, new Set(['sourceSha256']), errors, 'review policy bindings')
  }

  const rules = normalizeRules(policy, errors)
  const expectedSourceSha256 = canonicalSha256(policy?.bindings?.sourceSha256)
  let bindingValid = errors.length === 0
  if (policy) {
    if (!expectedSourceSha256) {
      errors.push({
        code: 'review-policy-source-binding-missing',
        message: 'review policy must bind bindings.sourceSha256',
      })
      bindingValid = false
    } else if (!source || source.missing) {
      errors.push({
        code: 'review-policy-source-missing',
        message: 'the source PPTX required by the review policy is missing',
        source: source?.path ?? resolve(sourcePptx || '.'),
      })
      bindingValid = false
    } else if (source.sha256 !== expectedSourceSha256) {
      errors.push({
        code: 'review-policy-source-hash-mismatch',
        message: 'review policy sourceSha256 does not match the current source PPTX',
        expectedSha256: expectedSourceSha256,
        actualSha256: source.sha256,
      })
      bindingValid = false
    }
  }
  if (rules.length > 0) {
    if (!candidate || candidate.missing) {
      errors.push({
        code: 'review-policy-candidate-missing',
        message: 'the candidate PPTX required by the final review receipt is missing',
        candidate: candidate?.path ?? resolve(candidatePptx || '.'),
      })
      bindingValid = false
    }
  }

  const applied = []
  const reviewedIndexes = new Set()
  const rawFindings = asArray(findings)
  if (bindingValid) {
    for (const rule of rules) {
      const matches = []
      for (const [findingIndex, finding] of rawFindings.entries()) {
        if (findingMatchesRule(finding, rule)) matches.push(findingIndex)
      }
      if (matches.length === 0) {
        errors.push({
          code: 'review-rule-unmatched',
          message: `reviewed finding ${JSON.stringify(rule.id)} did not match any current raw finding`,
          reviewId: rule.id,
          match:
            rule.matchMode === 'fingerprint'
              ? { findingSha256: rule.findingSha256 }
              : { target: rule.target },
        })
      } else if (matches.length > 1) {
        errors.push({
          code: 'review-rule-ambiguous',
          message: `reviewed finding ${JSON.stringify(rule.id)} matched multiple raw findings`,
          reviewId: rule.id,
          matchCount: matches.length,
          match:
            rule.matchMode === 'fingerprint'
              ? { findingSha256: rule.findingSha256 }
              : { target: rule.target },
        })
      } else {
        const findingIndex = matches[0]
        if (reviewedIndexes.has(findingIndex)) {
          errors.push({
            code: 'review-finding-matched-twice',
            message: `raw finding ${findingIndex} was matched by more than one review rule`,
            reviewId: rule.id,
            findingIndex,
          })
          continue
        }
        reviewedIndexes.add(findingIndex)
        applied.push({
          reviewId: rule.id,
          disposition: rule.disposition,
          reason: rule.reason,
          findingIndex,
          finding: rawFindings[findingIndex],
          matchMode: rule.matchMode,
          findingSha256:
            rule.matchMode === 'fingerprint'
              ? rule.findingSha256
              : reviewFindingSha256(rawFindings[findingIndex]),
        })
      }
    }
  }
  if (errors.length > 0) {
    applied.length = 0
    reviewedIndexes.clear()
  }

  const reviewedFindings = []
  const remainingActionable = []
  const informational = []
  for (const [findingIndex, finding] of rawFindings.entries()) {
    const appliedReview = applied.find((entry) => entry.findingIndex === findingIndex)
    if (appliedReview) {
      reviewedFindings.push({
        ...finding,
        classification: 'reviewed',
        review: {
          id: appliedReview.reviewId,
          disposition: appliedReview.disposition,
          reason: appliedReview.reason,
          matchMode: appliedReview.matchMode,
          findingSha256: appliedReview.findingSha256,
        },
      })
    } else if (finding?.classification === 'informational') {
      informational.push(finding)
    } else {
      remainingActionable.push(finding)
    }
  }

  return {
    schemaVersion: REVIEW_POLICY_EVALUATION_SCHEMA_VERSION,
    status: errors.length > 0 ? 'fail' : 'pass',
    bindings: {
      expectedSourceSha256: expectedSourceSha256 || null,
      source,
      candidate,
      policyDocument: policyIdentity,
      evidence,
    },
    summary: {
      declaredReviewCount: declaredFindings.length,
      validReviewCount: rules.length,
      appliedReviewCount: applied.length,
      reviewedFindingCount: reviewedFindings.length,
      remainingActionableCount: remainingActionable.length,
      informationalCount: informational.length,
      errorCount: errors.length,
    },
    applied,
    reviewedFindings,
    remainingActionable,
    informational,
    errors,
  }
}
