import { createHash } from 'node:crypto'

export const VISION_BASELINE_SCHEMA_VERSION = 'pptx-nova-vision-baseline/v1'
export const VISION_FINGERPRINT_VERSION = 'pptx-nova-vision-fingerprint/v1'
export const VISION_STYLE_POLICY_SCHEMA_VERSION = 'pptx-nova-vision-style-policy/v1'

const SAMPLE_LIMIT = 12

export function emptyVisionLowBuckets() {
  return {
    total: 0,
    styleAllowed: 0,
    baselineKnown: 0,
    new: 0,
    changed: 0,
    resolved: 0,
    reviewable: 0,
    baselineUnavailable: false,
    baselineUpdated: false,
  }
}

export function normalizeVisionLowBuckets(value = {}) {
  const defaults = emptyVisionLowBuckets()
  const result = { ...defaults }
  for (const key of [
    'total',
    'styleAllowed',
    'baselineKnown',
    'new',
    'changed',
    'resolved',
    'reviewable',
  ]) {
    if (Number.isFinite(value?.[key])) result[key] = value[key]
  }
  result.baselineUnavailable = value?.baselineUnavailable === true
  result.baselineUpdated = value?.baselineUpdated === true
  return result
}

export function reviewableVisionLowCount(vision = {}) {
  const buckets = normalizeVisionLowBuckets(vision.lowBuckets)
  return buckets.new + buckets.changed
}

function normalizedString(value) {
  return String(value ?? '')
    .trim()
    .replace(/\s+/g, ' ')
}

function normalizedKey(value) {
  return normalizedString(value)
    .toLowerCase()
    .replace(/["'`]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function stableJson(value) {
  if (Array.isArray(value)) return value.map(stableJson)
  if (!value || typeof value !== 'object') return value
  return Object.fromEntries(
    Object.keys(value)
      .sort()
      .map((key) => [key, stableJson(value[key])]),
  )
}

function digest(value) {
  return createHash('sha256')
    .update(JSON.stringify(stableJson(value)))
    .digest('hex')
    .slice(0, 20)
}

function finiteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function roundedNumber(value) {
  const number = finiteNumber(value)
  return number === null ? null : Number(number.toFixed(2))
}

function normalizedMetrics(metrics) {
  if (!metrics || typeof metrics !== 'object' || Array.isArray(metrics)) return {}
  const result = {}
  for (const [key, value] of Object.entries(metrics)) {
    if (typeof value === 'number' && Number.isFinite(value)) {
      result[key] = roundedNumber(value)
    } else if (typeof value === 'string' || typeof value === 'boolean') {
      result[key] = value
    }
  }
  return stableJson(result)
}

function issueKind(issue) {
  return normalizedKey(issue?.kind ?? issue?.code ?? issue?.type ?? 'unknown')
}

function issueFamily(kind) {
  if (kind.includes('font') && kind.includes('small')) return 'small-font'
  if (kind.includes('unexpected') && kind.includes('wrap')) return 'unexpected-wrap'
  if (kind.includes('wrap')) return 'text-wrap'
  if (kind.includes('overflow') || kind.includes('fit')) return 'text-fit'
  if (kind.includes('contrast')) return 'contrast'
  if (kind.includes('overlap') || kind.includes('collision')) return 'overlap'
  if (kind.includes('arrangement') || kind.includes('imbalance')) return 'composition'
  return kind || 'unknown'
}

function issueTarget(issue) {
  return normalizedString(
    issue?.slotPath ??
      issue?.path ??
      issue?.selector ??
      issue?.shapeName ??
      issue?.target ??
      (issue?.shapeId === undefined ? '' : `shape-${issue.shapeId}`),
  )
}

function targetRole(target) {
  return normalizedKey(target.replace(/^s\d+_/i, ''))
}

export function buildVisionStylePolicy(deckkitEntry = {}) {
  const qualityProfile = deckkitEntry?.qualityProfile ?? {}
  return {
    schemaVersion: VISION_STYLE_POLICY_SCHEMA_VERSION,
    source: 'catalog.qualityProfile',
    minFontPt: finiteNumber(qualityProfile.minFontPt),
    labelFontPt: finiteNumber(qualityProfile.labelFontPt),
    sourceFontPt: finiteNumber(qualityProfile.sourceFontPt),
    note: typeof qualityProfile.baseline === 'string' ? qualityProfile.baseline : '',
  }
}

function fontFloorForTarget(policy, target) {
  const role = targetRole(target)
  if (/(foot|footer|source|caption|legal|page-mark|page-num|pagenum)/.test(role)) {
    return policy.sourceFontPt ?? policy.labelFontPt ?? policy.minFontPt
  }
  if (/(label|badge|tag|eyebrow|kicker|mark|head|sub|dtl|metric|num)/.test(role)) {
    return policy.labelFontPt ?? policy.minFontPt
  }
  return policy.minFontPt
}

function styleAllowance(issue, policy) {
  if (issue.severity !== 'low' || issue.family !== 'small-font') return null
  const fontPt = finiteNumber(issue.metrics.fontPt)
  const floor = fontFloorForTarget(policy, issue.target)
  if (fontPt === null || floor === null) return null
  if (fontPt + 0.001 < floor) return null
  return {
    disposition: 'style-allowed',
    reason: `fontPt ${fontPt} is within DeckKit qualityProfile floor ${floor}`,
  }
}

export function canonicalizeVisionIssue(issue = {}) {
  const kind = issueKind(issue)
  const family = issueFamily(kind)
  const severity = normalizedKey(issue.severity || 'unknown')
  const slideIndex = Number.isInteger(issue.slideIndex) ? issue.slideIndex : null
  const target = issueTarget(issue)
  const messageKey = normalizedKey(issue.message || kind)
  const metrics = normalizedMetrics(issue.metrics)
  const identityParts = {
    version: VISION_FINGERPRINT_VERSION,
    severity,
    family,
    kind,
    slideIndex,
    target,
    messageKey,
  }
  const fingerprintParts = {
    ...identityParts,
    metrics,
  }

  return {
    severity,
    family,
    kind,
    slideIndex,
    target,
    messageKey,
    metrics,
    identity: digest(identityParts),
    fingerprint: digest(fingerprintParts),
    source: {
      shapeName: issue.shapeName ?? null,
      shapeId: issue.shapeId ?? null,
    },
  }
}

function issueSample(issue, extra = {}) {
  return {
    severity: issue.severity,
    family: issue.family,
    kind: issue.kind,
    slideIndex: issue.slideIndex,
    target: issue.target,
    metrics: issue.metrics,
    identity: issue.identity,
    fingerprint: issue.fingerprint,
    ...extra,
  }
}

function summarizeByFamily(issues) {
  return issues.reduce((acc, issue) => {
    acc[issue.family] = (acc[issue.family] ?? 0) + 1
    return acc
  }, {})
}

function baselineIssueList(baseline) {
  if (!baseline || typeof baseline !== 'object') return []
  if (Array.isArray(baseline.issues)) return baseline.issues
  if (Array.isArray(baseline.visionBaseline?.issues)) return baseline.visionBaseline.issues
  return []
}

function baselineIndexes(baseline) {
  const issues = baselineIssueList(baseline)
  const fingerprints = new Set()
  const identities = new Map()
  for (const issue of issues) {
    if (!issue?.fingerprint || !issue?.identity) continue
    fingerprints.add(issue.fingerprint)
    const list = identities.get(issue.identity) ?? []
    list.push(issue)
    identities.set(issue.identity, list)
  }
  return { issues, fingerprints, identities }
}

function sampleIssues(issues, extraForIssue = () => ({})) {
  return issues.slice(0, SAMPLE_LIMIT).map((issue) => issueSample(issue, extraForIssue(issue)))
}

export function summarizeVisionReport(
  report,
  { baseline = null, deckkitEntry = null, baselinePath = '', baselineUpdated = false } = {},
) {
  const rawIssues = Array.isArray(report?.issues) ? report.issues : []
  const canonicalIssues = rawIssues.map(canonicalizeVisionIssue)
  const bySeverity = report?.summary?.bySeverity ?? {}
  const countSeverity = (severity) =>
    canonicalIssues.filter((issue) => issue.severity === severity).length
  const lowIssues = canonicalIssues.filter((issue) => issue.severity === 'low')
  const stylePolicy = buildVisionStylePolicy(deckkitEntry ?? {})
  const baselineData = baselineIndexes(baseline)
  const baselineAvailable = baseline?.schemaVersion === VISION_BASELINE_SCHEMA_VERSION
  const buckets = {
    styleAllowed: [],
    baselineKnown: [],
    new: [],
    changed: [],
  }

  for (const issue of lowIssues) {
    const allowance = styleAllowance(issue, stylePolicy)
    if (allowance) {
      buckets.styleAllowed.push({ ...issue, ...allowance })
    } else if (baselineData.fingerprints.has(issue.fingerprint)) {
      buckets.baselineKnown.push(issue)
    } else if (baselineData.identities.has(issue.identity)) {
      buckets.changed.push(issue)
    } else {
      buckets.new.push(issue)
    }
  }

  const currentLowFingerprints = new Set(lowIssues.map((issue) => issue.fingerprint))
  const resolved = baselineData.issues.filter(
    (issue) => issue?.fingerprint && !currentLowFingerprints.has(issue.fingerprint),
  )

  return {
    status: report?.status ?? '',
    slideCount: report?.slideCount ?? null,
    issueCount: report?.summary?.issueCount ?? rawIssues.length,
    autoFixable: report?.summary?.autoFixable ?? null,
    bySeverity: {
      high: bySeverity.high ?? countSeverity('high'),
      medium: bySeverity.medium ?? countSeverity('medium'),
      low: bySeverity.low ?? countSeverity('low'),
    },
    lowBuckets: {
      total: lowIssues.length,
      styleAllowed: buckets.styleAllowed.length,
      baselineKnown: buckets.baselineKnown.length,
      new: buckets.new.length,
      changed: buckets.changed.length,
      resolved: resolved.length,
      reviewable: buckets.new.length + buckets.changed.length,
      baselineUnavailable: !baselineAvailable,
      baselineUpdated,
    },
    lowByFamily: summarizeByFamily(lowIssues),
    newLowByFamily: summarizeByFamily(buckets.new),
    changedLowByFamily: summarizeByFamily(buckets.changed),
    baseline: {
      schemaVersion: baseline?.schemaVersion ?? '',
      fingerprintVersion: baseline?.fingerprintVersion ?? '',
      path: baselinePath,
      available: baselineAvailable,
      issueCount: baselineData.issues.length,
    },
    stylePolicy,
    newLowSamples: sampleIssues(buckets.new),
    changedLowSamples: sampleIssues(buckets.changed, (issue) => ({
      baselineFingerprints: (baselineData.identities.get(issue.identity) ?? [])
        .map((baselineIssue) => baselineIssue.fingerprint)
        .slice(0, 4),
    })),
    resolvedLowSamples: resolved.slice(0, SAMPLE_LIMIT).map((issue) => ({
      severity: issue.severity,
      family: issue.family,
      kind: issue.kind,
      slideIndex: issue.slideIndex,
      target: issue.target,
      fingerprint: issue.fingerprint,
    })),
  }
}

export function createVisionBaseline(
  report,
  { deckkit, caseId, kind, deckkitEntry = null, generatedAt = new Date() } = {},
) {
  const stylePolicy = buildVisionStylePolicy(deckkitEntry ?? {})
  const issues = (Array.isArray(report?.issues) ? report.issues : [])
    .map(canonicalizeVisionIssue)
    .filter((issue) => issue.severity === 'low')
    .map((issue) => {
      const allowance = styleAllowance(issue, stylePolicy)
      return {
        ...issue,
        disposition: allowance?.disposition ?? 'reviewed-low',
        reason: allowance?.reason ?? 'accepted by benchmark --update-baseline',
      }
    })

  const lowSummary = {
    total: issues.length,
    styleAllowed: issues.filter((issue) => issue.disposition === 'style-allowed').length,
    reviewed: issues.filter((issue) => issue.disposition !== 'style-allowed').length,
    byFamily: summarizeByFamily(issues),
  }

  return {
    schemaVersion: VISION_BASELINE_SCHEMA_VERSION,
    fingerprintVersion: VISION_FINGERPRINT_VERSION,
    deckkit,
    caseId,
    kind,
    generatedAt:
      generatedAt instanceof Date ? generatedAt.toISOString() : normalizedString(generatedAt),
    review: {
      status: 'accepted',
      source: '--update-baseline',
      note: 'Current low-severity issues are accepted as the DeckKit visual baseline.',
    },
    stylePolicy,
    summary: {
      low: lowSummary,
    },
    issues,
  }
}
