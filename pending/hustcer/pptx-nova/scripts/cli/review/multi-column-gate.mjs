#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { canonicalEvidencePath } from '../../lib/review/evidence-paths.mjs'

const SCHEMA_VERSION = 'pptx-nova-multi-column-review-gate/v1'
const REVIEW_SCHEMA_VERSION = 'pptx-nova-multi-column-review/v1'
const VISION_SCHEMA_VERSION = 'pptx-vision-diff/v1'
const REVIEW_ONLY_KIND = 'multi-column-text-layout-review'
const REQUIRED_CHECKS = ['noClipping', 'columnFlowReadable', 'noOverlap', 'marginsAcceptable']

const usage = `Usage:
  node <skill-root>/scripts/cli/review/multi-column-gate.mjs [options]

Options:
  --candidate <path>    Final candidate PPTX reviewed by the human.
  --vision-diff <path>  Final xdoc pptx vision-diff JSON for that candidate.
  --review <path>       Structured pptx-nova-multi-column-review/v1 record.
  --output <path>       Optional report output path.
  --overwrite           Allow replacing an existing output report.
  --json                Print the report as JSON.
  --help                Show this help.

The gate may close only multi-column-text-layout-review findings. Every other
new or worsened high/medium vision issue remains a blocker.
`

function parseArgs(argv) {
  const args = {
    candidate: '',
    visionDiff: '',
    review: '',
    output: '',
    overwrite: false,
    json: false,
  }
  const flags = {
    '--candidate': 'candidate',
    '--vision-diff': 'visionDiff',
    '--review': 'review',
    '--output': 'output',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--json') {
      args.json = true
      continue
    }
    if (arg === '--overwrite') {
      args.overwrite = true
      continue
    }
    const key = flags[arg]
    if (!key) throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    const value = argv[index + 1]
    if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
    args[key] = resolve(value)
    index += 1
  }
  for (const key of ['candidate', 'visionDiff', 'review']) {
    if (!args[key]) throw new Error(`--${key === 'visionDiff' ? 'vision-diff' : key} is required`)
  }
  return args
}

function readJson(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`Failed to read ${label} at ${path}: ${error.message}`)
  }
}

function sha256(path) {
  return `sha256:${createHash('sha256').update(readFileSync(path)).digest('hex')}`
}

function issue(report, code, message, details = {}) {
  report.blockers.push({ severity: 'error', code, message, ...details })
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function normalizedIssue(value) {
  return value?.candidateIssue ?? value?.issue ?? value
}

function issueKey(value) {
  const issue = normalizedIssue(value)
  return `${issue?.slideIndex}:${String(issue?.shapeId)}`
}

function isBlockingSeverity(issue) {
  return issue?.severity === 'high' || issue?.severity === 'medium'
}

function collectVisionFindings(visionDiff) {
  const newOrWorsened = [...asArray(visionDiff?.newIssues), ...asArray(visionDiff?.worsenedIssues)]
    .map(normalizedIssue)
    .filter(Boolean)
    .filter(isBlockingSeverity)
  const changedReviewOnly = asArray(visionDiff?.changedIssues)
    .map(normalizedIssue)
    .filter((item) => item?.kind === REVIEW_ONLY_KIND)
  const reviewByKey = new Map()
  for (const item of [...newOrWorsened, ...changedReviewOnly]) {
    if (item.kind === REVIEW_ONLY_KIND) reviewByKey.set(issueKey(item), item)
  }
  return {
    reviewOnly: [...reviewByKey.values()],
    nonReviewBlockers: newOrWorsened.filter((item) => item.kind !== REVIEW_ONLY_KIND),
  }
}

function readPngDimensions(path) {
  const bytes = readFileSync(path)
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])
  if (
    bytes.length < 24 ||
    !bytes.subarray(0, 8).equals(signature) ||
    bytes.toString('ascii', 12, 16) !== 'IHDR'
  ) {
    return null
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) }
}

function validateBinding(report, label, actualPath, claimed, claimArtifactPath) {
  if (!existsSync(actualPath)) {
    issue(report, `${label}-missing`, `${label} evidence does not exist`, { path: actualPath })
    return
  }
  let claimedPath = ''
  try {
    claimedPath = canonicalEvidencePath(claimed?.path, { artifactPath: claimArtifactPath })
  } catch (error) {
    issue(report, `${label}-path-invalid`, error.message, { actual: claimed?.path ?? null })
  }
  if (claimedPath !== actualPath) {
    issue(report, `${label}-path-mismatch`, `${label} path does not match the reviewed artifact`, {
      expected: actualPath,
      actual: claimed?.path ?? null,
    })
  }
  const actualHash = sha256(actualPath)
  if (claimed?.sha256 !== actualHash) {
    issue(
      report,
      `${label}-hash-mismatch`,
      `${label} SHA-256 does not match the reviewed artifact`,
      {
        expected: actualHash,
        actual: claimed?.sha256 ?? null,
      },
    )
  }
}

function validateReviewItem(report, finding, review, reviewArtifactPath) {
  const key = issueKey(finding)
  if (!review) {
    issue(report, 'review-missing', 'multi-column review is missing for a slide/shape finding', {
      slideIndex: finding.slideIndex,
      shapeId: finding.shapeId,
    })
    return false
  }
  let valid = true
  const block = (code, message, details = {}) => {
    valid = false
    issue(report, code, message, {
      slideIndex: finding.slideIndex,
      shapeId: finding.shapeId,
      ...details,
    })
  }
  if (review.decision !== 'pass') block('review-not-approved', 'review decision must be pass')
  if (!String(review.reviewer ?? '').trim())
    block('reviewer-missing', 'reviewer identity is required')
  if (!String(review.note ?? '').trim()) block('review-note-missing', 'review note is required')
  for (const check of REQUIRED_CHECKS) {
    if (review?.checks?.[check] !== true) {
      block('review-check-failed', `required manual check ${check} must be true`, { check })
    }
  }
  let pngPath = ''
  try {
    pngPath = canonicalEvidencePath(review?.png?.path, { artifactPath: reviewArtifactPath })
  } catch (error) {
    block('png-path-invalid', error.message, { path: review?.png?.path ?? null })
  }
  if (!review?.png?.path || !existsSync(pngPath)) {
    block('png-missing', 'full-size PNG evidence does not exist', {
      path: review?.png?.path ?? null,
    })
    return false
  }
  const actualHash = sha256(pngPath)
  if (review.png.sha256 !== actualHash) {
    block('png-hash-mismatch', 'PNG SHA-256 does not match the reviewed image', {
      expected: actualHash,
      actual: review.png.sha256 ?? null,
    })
  }
  const dimensions = readPngDimensions(pngPath)
  if (!dimensions) {
    block('png-invalid', 'review evidence is not a PNG with readable IHDR dimensions')
  } else if (review.png.width !== dimensions.width || review.png.height !== dimensions.height) {
    block('png-dimensions-mismatch', 'PNG dimensions do not match the review record', {
      expected: dimensions,
      actual: { width: review.png.width ?? null, height: review.png.height ?? null },
    })
  }
  if (valid)
    report.reviewed.push({
      key,
      slideIndex: finding.slideIndex,
      shapeId: finding.shapeId,
      png: pngPath,
    })
  return valid
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const report = {
    schemaVersion: SCHEMA_VERSION,
    status: 'fail',
    candidate: args.candidate,
    visionDiff: args.visionDiff,
    review: args.review,
    blockers: [],
    reviewed: [],
  }
  const visionDiff = readJson(args.visionDiff, 'vision diff')
  const reviewRecord = readJson(args.review, 'multi-column review')

  if (visionDiff?.schemaVersion !== VISION_SCHEMA_VERSION || visionDiff?.status !== 'success') {
    issue(
      report,
      'vision-diff-invalid',
      'vision-diff must be successful pptx-vision-diff/v1 output',
    )
  }
  if (reviewRecord?.schemaVersion !== REVIEW_SCHEMA_VERSION) {
    issue(report, 'review-schema-invalid', `review record must use ${REVIEW_SCHEMA_VERSION}`)
  }
  validateBinding(report, 'candidate', args.candidate, reviewRecord?.candidate, args.review)
  validateBinding(report, 'vision-diff', args.visionDiff, reviewRecord?.visionDiff, args.review)

  let visionCandidate = ''
  try {
    visionCandidate = visionDiff?.candidate
      ? canonicalEvidencePath(visionDiff.candidate, { artifactPath: args.visionDiff })
      : ''
  } catch (error) {
    issue(report, 'vision-candidate-path-invalid', error.message, {
      actual: visionDiff?.candidate ?? null,
    })
  }
  if (visionCandidate && visionCandidate !== args.candidate) {
    issue(
      report,
      'vision-candidate-path-mismatch',
      'vision-diff candidate path does not match --candidate',
      {
        expected: args.candidate,
        actual: visionCandidate,
      },
    )
  }

  const findings = collectVisionFindings(visionDiff)
  if (
    visionDiff?.agentGate?.passed === false &&
    findings.reviewOnly.length === 0 &&
    findings.nonReviewBlockers.length === 0
  ) {
    issue(
      report,
      'vision-gate-blockers-unresolved',
      'vision-diff failed but did not expose reviewable new/worsened findings; manual review cannot override an unknown blocker',
    )
  }
  for (const blocker of findings.nonReviewBlockers) {
    issue(
      report,
      'non-review-visual-blocker',
      'new or worsened high/medium issue cannot be manually exempted',
      {
        kind: blocker.kind,
        severity: blocker.severity,
        slideIndex: blocker.slideIndex,
        shapeId: blocker.shapeId ?? null,
      },
    )
  }

  const rawReviews = asArray(reviewRecord?.reviews)
  const reviews = new Map(rawReviews.map((item) => [issueKey(item), item]))
  if (reviews.size !== rawReviews.length) {
    issue(report, 'review-duplicate', 'review record contains duplicate slide/shape pairs')
  }
  for (const finding of findings.reviewOnly)
    validateReviewItem(report, finding, reviews.get(issueKey(finding)), args.review)
  for (const [key, review] of reviews) {
    if (!findings.reviewOnly.some((finding) => issueKey(finding) === key)) {
      issue(
        report,
        'review-not-required',
        'review record contains a slide/shape pair absent from final vision-diff',
        {
          slideIndex: review.slideIndex,
          shapeId: review.shapeId,
        },
      )
    }
  }

  report.summary = {
    reviewOnlyIssueCount: findings.reviewOnly.length,
    reviewedIssueCount: report.reviewed.length,
    nonReviewBlockerCount: findings.nonReviewBlockers.length,
    blockerCount: report.blockers.length,
  }
  report.agentGate = {
    passed: report.blockers.length === 0,
    status: report.blockers.length === 0 ? 'pass' : 'fail',
    blockerCount: report.blockers.length,
    policy: `Only ${REVIEW_ONLY_KIND} may be closed by bound manual review evidence.`,
  }
  report.status = report.agentGate.status

  const output = `${JSON.stringify(report, null, 2)}\n`
  if (args.output) {
    if (existsSync(args.output) && !args.overwrite)
      throw new Error(`Output already exists: ${args.output}`)
    writeFileSync(args.output, output)
  }
  if (args.json || !args.output) process.stdout.write(output)
  else process.stdout.write(`Multi-column review gate: ${report.status}\n`)
  process.exitCode = report.agentGate.passed ? 0 : 2
}

try {
  main()
} catch (error) {
  const failure = {
    schemaVersion: SCHEMA_VERSION,
    status: 'error',
    error: { code: 'multi-column-review-gate-error', message: error.message },
    agentGate: { passed: false, status: 'error', blockerCount: 1 },
  }
  process.stderr.write(`${JSON.stringify(failure, null, 2)}\n`)
  process.exitCode = 1
}
