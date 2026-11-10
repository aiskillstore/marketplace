#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { canonicalEvidencePath } from '../../lib/review/evidence-paths.mjs'

const REVIEW_SCHEMA_VERSION = 'pptx-nova-multi-column-review/v1'
const VISION_SCHEMA_VERSION = 'pptx-vision-diff/v1'
const PREVIEW_SCHEMA_VERSION = 'pptx-preview/v1'
const REVIEW_ONLY_KIND = 'multi-column-text-layout-review'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/multi-column-scaffold.mjs [options]

Options:
  --candidate <path>    Final candidate PPTX to review.
  --vision-diff <path>  Final xdoc pptx vision-diff JSON for that candidate.
  --preview <path>      Final xdoc pptx preview JSON for that candidate.
  --carry-review-from <path>
                        Copy judgments only when candidate, PNGs, finding set,
                        and normalized vision identity are unchanged.
  --output <path>       Write the review scaffold to this path.
  --overwrite           Allow replacing an existing output scaffold.
  --json                Print the scaffold as JSON.
  --help                Show this help.

The generated record binds immutable evidence automatically. Human or visual
review must still fill reviewer, decision, checks, and note before running the
multi-column review gate.
`

function parseArgs(argv) {
  const args = {
    candidate: '',
    visionDiff: '',
    preview: '',
    carryReviewFrom: '',
    output: '',
    overwrite: false,
    json: false,
  }
  const flags = {
    '--candidate': 'candidate',
    '--vision-diff': 'visionDiff',
    '--preview': 'preview',
    '--carry-review-from': 'carryReviewFrom',
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
  for (const key of ['candidate', 'visionDiff', 'preview', 'output']) {
    if (!args[key]) {
      const flag = key === 'visionDiff' ? 'vision-diff' : key
      throw new Error(`--${flag} is required`)
    }
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

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function normalizedIssue(value) {
  return value?.candidateIssue ?? value?.issue ?? value
}

function issueKey(value) {
  return `${value?.slideIndex}:${String(value?.shapeId)}`
}

function isBlockingSeverity(issue) {
  return issue?.severity === 'high' || issue?.severity === 'medium'
}

function collectReviewFindings(visionDiff) {
  const findings = [
    ...asArray(visionDiff?.newIssues).map(normalizedIssue).filter(isBlockingSeverity),
    ...asArray(visionDiff?.worsenedIssues).map(normalizedIssue).filter(isBlockingSeverity),
    ...asArray(visionDiff?.changedIssues).map(normalizedIssue),
  ].filter((item) => item?.kind === REVIEW_ONLY_KIND)
  const unique = new Map()
  for (const finding of findings) unique.set(issueKey(finding), finding)
  return [...unique.values()].sort(
    (left, right) => left.slideIndex - right.slideIndex || left.shapeId - right.shapeId,
  )
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue)
  if (!value || typeof value !== 'object') return value
  return Object.fromEntries(
    Object.keys(value)
      .sort()
      .map((key) => [key, stableValue(value[key])]),
  )
}

function normalizedVisionIdentity(visionDiff, findings) {
  const normalized = {
    schemaVersion: visionDiff.schemaVersion,
    status: visionDiff.status,
    findings: findings.map((finding) => stableValue(finding)),
  }
  return `sha256:${createHash('sha256').update(JSON.stringify(normalized)).digest('hex')}`
}

function reviewKey(review) {
  return `${review?.slideIndex}:${String(review?.shapeId)}`
}

function samePngEvidence(left, right) {
  return (
    left?.sha256 === right?.sha256 && left?.width === right?.width && left?.height === right?.height
  )
}

function carryReviewJudgments(scaffold, oldReview) {
  const reasons = []
  if (oldReview?.schemaVersion !== REVIEW_SCHEMA_VERSION) reasons.push('schema-mismatch')
  if (oldReview?.candidate?.sha256 !== scaffold.candidate.sha256) {
    reasons.push('candidate-mismatch')
  }
  if (oldReview?.visionDiff?.normalizedIdentity !== scaffold.visionDiff.normalizedIdentity) {
    reasons.push('vision-identity-mismatch')
  }
  const previous = new Map(asArray(oldReview?.reviews).map((review) => [reviewKey(review), review]))
  const currentKeys = scaffold.reviews.map(reviewKey)
  if (previous.size !== currentKeys.length || currentKeys.some((key) => !previous.has(key))) {
    reasons.push('finding-set-mismatch')
  }
  if (
    reasons.length === 0 &&
    scaffold.reviews.some(
      (review) => !samePngEvidence(review.png, previous.get(reviewKey(review))?.png),
    )
  ) {
    reasons.push('png-mismatch')
  }
  if (reasons.length > 0) return { status: 'not-carried', count: 0, reasons }
  for (const review of scaffold.reviews) {
    const prior = previous.get(reviewKey(review))
    review.reviewer = prior.reviewer ?? ''
    review.decision = prior.decision ?? 'pending'
    review.checks = stableValue(prior.checks ?? review.checks)
    review.note = prior.note ?? ''
  }
  return { status: 'carried', count: scaffold.reviews.length, reasons: [] }
}

function manifestPath(value, manifestPath) {
  if (!value) return ''
  return canonicalEvidencePath(value, { artifactPath: manifestPath })
}

function readPngDimensions(path) {
  const bytes = readFileSync(path)
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])
  if (
    bytes.length < 24 ||
    !bytes.subarray(0, 8).equals(signature) ||
    bytes.toString('ascii', 12, 16) !== 'IHDR'
  ) {
    throw new Error(`preview page is not a PNG with readable IHDR dimensions: ${path}`)
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) }
}

function expectedManifestHash(page) {
  const hash = page?.file?.hash
  if (hash?.algorithm !== 'sha256' || !hash?.value) return ''
  return `sha256:${hash.value}`
}

function validatePreviewPage(page, previewPath) {
  const path = manifestPath(page?.file?.path ?? page?.path, previewPath)
  if (!path || !existsSync(path))
    throw new Error(`preview page does not exist: ${path || '(missing path)'}`)
  if (page?.file?.status && page.file.status !== 'ok') {
    throw new Error(`preview page is not successful: slide ${page.slide}`)
  }
  const dimensions = readPngDimensions(path)
  if (page?.file?.width !== dimensions.width || page?.file?.height !== dimensions.height) {
    throw new Error(`preview page dimensions are stale for slide ${page.slide}`)
  }
  const actualHash = sha256(path)
  if (expectedManifestHash(page) !== actualHash) {
    throw new Error(`preview page hash is stale for slide ${page.slide}`)
  }
  return { path, sha256: actualHash, ...dimensions }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  if (!existsSync(args.candidate)) throw new Error(`candidate does not exist: ${args.candidate}`)
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(`Output already exists: ${args.output}`)
  }

  const visionDiff = readJson(args.visionDiff, 'vision diff')
  const preview = readJson(args.preview, 'preview manifest')
  if (visionDiff?.schemaVersion !== VISION_SCHEMA_VERSION || visionDiff?.status !== 'success') {
    throw new Error(`vision-diff must be successful ${VISION_SCHEMA_VERSION} output`)
  }
  if (preview?.schemaVersion !== PREVIEW_SCHEMA_VERSION || preview?.status !== 'success') {
    throw new Error(`preview must be successful ${PREVIEW_SCHEMA_VERSION} output`)
  }

  const visionCandidate = visionDiff?.candidate
    ? canonicalEvidencePath(visionDiff.candidate, { artifactPath: args.visionDiff })
    : ''
  if (visionCandidate !== args.candidate) {
    throw new Error('vision-diff candidate path does not match --candidate')
  }
  const previewCandidate = manifestPath(preview?.input?.path, args.preview)
  if (previewCandidate !== args.candidate) {
    throw new Error('preview input path does not match --candidate')
  }

  const findings = collectReviewFindings(visionDiff)
  if (findings.length === 0) {
    throw new Error(`vision-diff contains no ${REVIEW_ONLY_KIND} findings`)
  }

  const pagesBySlide = new Map()
  for (const page of asArray(preview?.pages)) {
    const slide = page?.slide
    if (!Number.isInteger(slide)) continue
    if (pagesBySlide.has(slide))
      throw new Error(`preview contains duplicate page for slide ${slide}`)
    pagesBySlide.set(slide, page)
  }
  const evidenceBySlide = new Map()
  const reviews = findings.map((finding) => {
    if (!Number.isInteger(finding.slideIndex) || !Number.isInteger(finding.shapeId)) {
      throw new Error('multi-column finding requires integer slideIndex and shapeId')
    }
    const previewSlide = finding.slideIndex + 1
    const page = pagesBySlide.get(previewSlide)
    if (!page) throw new Error(`preview is missing slide ${previewSlide} required by vision-diff`)
    if (!evidenceBySlide.has(previewSlide)) {
      evidenceBySlide.set(previewSlide, validatePreviewPage(page, args.preview))
    }
    return {
      slideIndex: finding.slideIndex,
      shapeId: finding.shapeId,
      reviewer: '',
      decision: 'pending',
      png: evidenceBySlide.get(previewSlide),
      checks: {
        noClipping: false,
        columnFlowReadable: false,
        noOverlap: false,
        marginsAcceptable: false,
      },
      note: '',
    }
  })

  const scaffold = {
    schemaVersion: REVIEW_SCHEMA_VERSION,
    candidate: { path: args.candidate, sha256: sha256(args.candidate) },
    visionDiff: {
      path: args.visionDiff,
      sha256: sha256(args.visionDiff),
      normalizedIdentity: normalizedVisionIdentity(visionDiff, findings),
    },
    reviews,
  }
  if (args.carryReviewFrom) {
    const previous = readJson(args.carryReviewFrom, 'carry review')
    scaffold.carryReview = {
      from: args.carryReviewFrom,
      ...carryReviewJudgments(scaffold, previous),
    }
  }
  const output = `${JSON.stringify(scaffold, null, 2)}\n`
  writeFileSync(args.output, output)
  if (args.json) process.stdout.write(output)
  else
    process.stdout.write(
      `Multi-column review scaffold: ${args.output} (${reviews.length} reviews)\n`,
    )
}

try {
  main()
} catch (error) {
  const failure = {
    schemaVersion: 'pptx-nova-multi-column-review-scaffold-error/v1',
    status: 'error',
    error: { code: 'multi-column-review-scaffold-error', message: error.message },
  }
  process.stderr.write(`${JSON.stringify(failure, null, 2)}\n`)
  process.exitCode = 1
}
