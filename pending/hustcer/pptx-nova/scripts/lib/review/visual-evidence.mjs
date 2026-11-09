import { createHash } from 'node:crypto'
import { copyFileSync, existsSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, extname } from 'node:path'
import { mkdirSync } from 'node:fs'

export class VisualEvidenceError extends Error {
  constructor(message, details = {}) {
    super(message)
    this.name = 'VisualEvidenceError'
    Object.assign(this, details)
  }
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function validateDeclaredFileIdentity(path, descriptor, label) {
  if (!existsSync(path) || statSync(path).size <= 0) {
    throw new VisualEvidenceError(`${label} is missing or empty`, { path })
  }
  const actualByteLength = statSync(path).size
  const actualSha256 = sha256(path)
  if (
    descriptor?.byteLength !== undefined &&
    descriptor.byteLength !== null &&
    Number(descriptor.byteLength) !== actualByteLength
  ) {
    throw new VisualEvidenceError(`${label} byte length does not match its manifest`, {
      path,
      expectedByteLength: descriptor.byteLength,
      actualByteLength,
    })
  }
  if (descriptor?.sha256 && descriptor.sha256 !== actualSha256) {
    throw new VisualEvidenceError(`${label} SHA-256 does not match its manifest`, {
      path,
      expectedSha256: descriptor.sha256,
      actualSha256,
    })
  }
  return { byteLength: actualByteLength, sha256: actualSha256 }
}

function numberedArtifactPath(path, partNumber, partCount) {
  const extension = extname(path)
  const stem = path.slice(0, -extension.length)
  const width = Math.max(2, String(partCount).length)
  return `${stem}-${String(partNumber).padStart(width, '0')}${extension}`
}

function reportForPart(part) {
  return part?.reportPath ? JSON.parse(readFileSync(part.reportPath, 'utf8')) : part
}

function sameIdentity(left, right) {
  return (
    left?.path === right?.path &&
    Number(left?.byteLength) === Number(right?.byteLength) &&
    normalizedSha256(left?.sha256) === normalizedSha256(right?.sha256)
  )
}

function normalizedSha256(value) {
  return String(value ?? '').replace(/^sha256:/, '')
}

function validateInputIdentity(descriptor, label) {
  if (!descriptor?.path) {
    throw new VisualEvidenceError(`${label} identity is missing its path`)
  }
  const actual = validateDeclaredFileIdentity(descriptor.path, descriptor, label)
  return { path: descriptor.path, ...actual }
}

function validateMultipartContract(compareReport) {
  if (compareReport?.status !== 'success') {
    throw new VisualEvidenceError('Compare manifest did not report success')
  }
  const source = validateInputIdentity(compareReport.source, 'Compare source')
  const candidate = validateInputIdentity(compareReport.candidate, 'Compare candidate')
  const parts = compareReport.parts ?? []
  if (parts.length === 0) {
    throw new VisualEvidenceError('Cannot materialize aliases from an empty compare manifest')
  }
  const expectedSlides = compareReport?.coverage?.expectedSlides ?? []
  const coveredSlides = parts.flatMap((part) => part?.slides ?? [])
  const uniqueSlides = new Set(coveredSlides)
  if (
    expectedSlides.length === 0 ||
    uniqueSlides.size !== coveredSlides.length ||
    JSON.stringify([...uniqueSlides].sort((a, b) => a - b)) !==
      JSON.stringify([...expectedSlides].sort((a, b) => a - b)) ||
    Number(compareReport.slideCount) !== expectedSlides.length
  ) {
    throw new VisualEvidenceError('Compare manifest coverage is incomplete or overlapping')
  }
  for (const [index, part] of parts.entries()) {
    if (
      Number(part?.partNumber) !== index + 1 ||
      Number(part?.pairCount) !== part?.slides?.length
    ) {
      throw new VisualEvidenceError('Compare part numbering or pair coverage is inconsistent', {
        part,
      })
    }
    if (!existsSync(part.reportPath)) {
      throw new VisualEvidenceError('Compare part report is missing', { part })
    }
    const report = reportForPart(part)
    if (
      report?.status !== 'success' ||
      !sameIdentity(report?.baseline, source) ||
      !sameIdentity(report?.target, candidate) ||
      report?.outputPath !== part.path ||
      report?.render?.path !== part.path ||
      JSON.stringify(report?.scope?.slides ?? []) !== JSON.stringify(part.slides)
    ) {
      throw new VisualEvidenceError('Compare part report is not bound to its manifest', { part })
    }
  }
}

function attemptsForPart(part, report) {
  if (Array.isArray(part?.attempts)) return part.attempts
  if (Array.isArray(report?.pptxNovaCompare?.attempts)) return report.pptxNovaCompare.attempts
  return []
}

function cacheForPart(part, report) {
  return part?.cache ?? report?.pptxNovaCompare?.cache ?? null
}

function pageBitmapCacheForPart(part, report) {
  return part?.pageBitmapCache ?? report?.pptxNovaCompare?.pageBitmapCache ?? null
}

export function analyzeCompareRendering(compareReport, { primaryDpi = 192 } = {}) {
  const parts =
    compareReport?.schemaVersion === 'pptx-nova-compare-manifest/v1'
      ? (compareReport.parts ?? [])
      : [compareReport]
  const metrics = parts.reduce(
    (result, part) => {
      const report = reportForPart(part)
      const attemptReports = attemptsForPart(part, report)
      const cache = cacheForPart(part, report)
      const pageBitmapCache = pageBitmapCacheForPart(part, report)
      const cacheHit = cache?.status === 'hit'
      const effectiveAttempts = attemptReports.length
        ? attemptReports
        : cacheHit
          ? []
          : [{ dpi: Number(report?.render?.dpi ?? 0), status: 'success' }]
      const renderedAttempts = effectiveAttempts.filter(
        (attempt) => attempt?.status !== 'cache-hit',
      )
      const width = Number(report?.render?.width ?? 0)
      const height = Number(report?.render?.height ?? 0)
      const finalDpi = Number(report?.render?.dpi ?? 0)
      result.renderInvocations += renderedAttempts.length
      result.retryInvocations += effectiveAttempts.filter(
        (attempt, index) => index > 0 && attempt?.status !== 'cache-hit',
      ).length
      if (cacheHit) result.cacheHitCount += 1
      for (const side of ['source', 'candidate']) {
        const page = pageBitmapCache?.[side]
        if (!page) continue
        result.pageBitmapCache[side].requestedPageCount += Number(page.requestedPageCount ?? 0)
        result.pageBitmapCache[side].hitCount += Number(page.hitCount ?? 0)
        result.pageBitmapCache[side].missCount += Number(page.missCount ?? 0)
        result.pageBitmapCache[side].populatedCount += Number(page.populatedCount ?? 0)
        result.pageBitmapCache[side].complete = result.pageBitmapCache[side].observed
          ? result.pageBitmapCache[side].complete && page.complete === true
          : page.complete === true
        result.pageBitmapCache[side].observed = true
      }
      if (width > 0 && height > 0) {
        const pixelsAtDpi = (dpi) => {
          const scale = finalDpi > 0 && dpi > 0 ? dpi / finalDpi : 1
          return Math.round(width * height * scale * scale)
        }
        result.baselineEstimatedPixels += pixelsAtDpi(primaryDpi)
        result.estimatedRenderedPixels += renderedAttempts.reduce(
          (pixels, attempt) => pixels + pixelsAtDpi(Number(attempt?.dpi ?? finalDpi)),
          0,
        )
      }
      return result
    },
    {
      partCount: parts.length,
      renderInvocations: 0,
      estimatedRenderedPixels: 0,
      baselineEstimatedPixels: 0,
      cacheHitCount: 0,
      retryInvocations: 0,
      pageBitmapCache: {
        source: {
          requestedPageCount: 0,
          hitCount: 0,
          missCount: 0,
          populatedCount: 0,
          observed: false,
          complete: false,
        },
        candidate: {
          requestedPageCount: 0,
          hitCount: 0,
          missCount: 0,
          populatedCount: 0,
          observed: false,
          complete: false,
        },
      },
    },
  )
  const uncachedPartCount = metrics.partCount - metrics.cacheHitCount
  return {
    ...metrics,
    cacheMissCount: uncachedPartCount,
    renderInvocationsSaved: metrics.cacheHitCount,
  }
}

export function materializeCompareAliases({
  compareReport,
  compareReportPath,
  compareOutputPath,
  aliasOutputPath,
  aliasReportPath,
  aliasKind = 'contact',
  sourceKind,
}) {
  const multipart = compareReport?.schemaVersion === 'pptx-nova-compare-manifest/v1'
  let report
  let partPaths = []
  let renderInvocationsSaved = 1

  if (multipart) {
    const sourceParts = compareReport.parts ?? []
    validateMultipartContract(compareReport)
    const parts = sourceParts.map((part, index) => {
      const partNumber = index + 1
      const path = numberedArtifactPath(aliasOutputPath, partNumber, sourceParts.length)
      const reportPath = numberedArtifactPath(aliasReportPath, partNumber, sourceParts.length)
      if (!existsSync(part.path) || !existsSync(part.reportPath)) {
        throw new VisualEvidenceError('Compare part or report is missing', { part })
      }
      const sourceIdentity = validateDeclaredFileIdentity(part.path, part, 'Compare part')
      copyFileSync(part.path, path)
      const sourcePartReport = JSON.parse(readFileSync(part.reportPath, 'utf8'))
      writeJson(reportPath, {
        ...sourcePartReport,
        outputPath: path,
        output: path,
        render: sourcePartReport?.render
          ? { ...sourcePartReport.render, path }
          : sourcePartReport?.render,
        reuse: {
          status: 'reused',
          sourceReport: part.reportPath,
          sourcePath: part.path,
        },
      })
      const aliasPart = {
        ...part,
        path,
        reportPath,
        byteLength: sourceIdentity.byteLength,
        sha256: sourceIdentity.sha256,
        reusedFrom: { path: part.path, reportPath: part.reportPath },
      }
      const aliasPartReport = JSON.parse(readFileSync(reportPath, 'utf8'))
      const valid =
        statSync(path).size > 0 &&
        aliasPart.byteLength === statSync(path).size &&
        aliasPart.sha256 === sha256(path) &&
        aliasPartReport.outputPath === path &&
        aliasPartReport.render?.path === path &&
        readFileSync(path).equals(readFileSync(part.path))
      if (!valid) {
        throw new VisualEvidenceError('Materialized multipart alias evidence is inconsistent', {
          part: aliasPart,
        })
      }
      return aliasPart
    })
    renderInvocationsSaved = parts.length
    partPaths = parts.map((part) => part.path)
    report = {
      ...compareReport,
      kind: aliasKind,
      parts,
      reuse: {
        status: 'reused',
        sourceKind: sourceKind ?? compareReport.kind,
        sourceReport: compareReportPath,
        renderInvocationsSaved,
      },
    }
  } else {
    validateDeclaredFileIdentity(compareOutputPath, compareReport, 'Single compare output')
    if (
      compareReport?.status !== 'success' ||
      compareReport?.outputPath !== compareOutputPath ||
      compareReport?.render?.path !== compareOutputPath
    ) {
      throw new VisualEvidenceError('Single compare report is not bound to its output')
    }
    validateInputIdentity(compareReport.baseline, 'Compare source')
    validateInputIdentity(compareReport.target, 'Compare candidate')
    copyFileSync(compareOutputPath, aliasOutputPath)
    report = {
      ...compareReport,
      outputPath: aliasOutputPath,
      output: aliasOutputPath,
      render: compareReport?.render
        ? { ...compareReport.render, path: aliasOutputPath }
        : compareReport?.render,
      reuse: {
        status: 'reused',
        sourceKind:
          sourceKind ??
          compareReport?.kind ??
          compareReport?.pptxNovaCompare?.kind ??
          compareReport?.sourceKind ??
          null,
        sourceReport: compareReportPath,
        sourcePath: compareOutputPath,
        renderInvocationsSaved,
      },
    }
    const valid =
      statSync(aliasOutputPath).size > 0 &&
      sha256(aliasOutputPath) === sha256(compareOutputPath) &&
      report.outputPath === aliasOutputPath &&
      report.render?.path === aliasOutputPath
    if (!valid) throw new VisualEvidenceError('Materialized single alias evidence is inconsistent')
  }

  writeJson(aliasReportPath, report)
  return {
    report,
    partPaths,
    partCount: multipart ? report.parts.length : 1,
    renderInvocationsSaved,
  }
}
