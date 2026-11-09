import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { basename, isAbsolute, relative, resolve, sep } from 'node:path'
import { readPptxPackage } from '../pptx/pptx-package.mjs'

export const POWERPOINT_SNAPSHOT_SCHEMA_VERSION = 'pptx-snapshot/v1'

const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex')
}

function asPositiveInteger(value) {
  const parsed = Number(value)
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null
}

function safeRealpath(path) {
  try {
    return realpathSync(path)
  } catch {
    return resolve(path)
  }
}

function pathInside(root, path) {
  const rel = relative(safeRealpath(root), safeRealpath(path))
  return rel === '' || (!rel.startsWith(`..${sep}`) && rel !== '..' && !isAbsolute(rel))
}

export function inspectChartExPackage(candidatePath) {
  return readPptxPackage(candidatePath).chartExScope()
}

export function detectPowerPointAvailability() {
  if (process.platform !== 'darwin') {
    return {
      available: false,
      reason: 'unsupported-platform',
      platform: process.platform,
      powerpointAvailable: false,
      nushellAvailable: false,
      mutoolAvailable: false,
      pdfRenderAvailable: false,
    }
  }
  const powerpoint = spawnSync('osascript', ['-e', 'id of application "Microsoft PowerPoint"'], {
    encoding: 'utf8',
  })
  const nushell = spawnSync('nu', ['--version'], { encoding: 'utf8' })
  const pdfRender = spawnSync('xdoc', ['pdf', 'render', '--help'], { encoding: 'utf8' })
  const powerpointAvailable = powerpoint.status === 0
  const nushellAvailable = nushell.status === 0
  const pdfRenderAvailable = pdfRender.status === 0
  const available = powerpointAvailable && nushellAvailable && pdfRenderAvailable
  const reason = !powerpointAvailable
    ? 'powerpoint-not-installed-or-not-scriptable'
    : !nushellAvailable
      ? 'optional-nushell-helper-unavailable'
      : !pdfRenderAvailable
        ? 'optional-pdf-render-helper-unavailable'
        : 'available'
  return {
    available,
    reason,
    platform: process.platform,
    powerpointAvailable,
    nushellAvailable,
    mutoolAvailable: null, // Retained legacy field; no longer a prerequisite.
    pdfRenderAvailable,
    error: available
      ? null
      : [
          [powerpointAvailable, powerpoint],
          [nushellAvailable, nushell],
          [pdfRenderAvailable, pdfRender],
        ]
          .filter(([probeAvailable]) => !probeAvailable)
          .map(([, result]) =>
            (result.stderr || result.stdout || result.error?.message || '').trim(),
          )
          .find(Boolean) || null,
  }
}

function pngIdentity(path) {
  const bytes = readFileSync(path)
  if (bytes.length < 24 || !bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    throw new Error('output is not a readable PNG image')
  }
  return {
    pixelWidth: bytes.readUInt32BE(16),
    pixelHeight: bytes.readUInt32BE(20),
    byteLength: bytes.length,
    sha256: sha256(bytes),
  }
}

function reportSlides(report) {
  const outputSlides = Array.isArray(report?.outputs)
    ? report.outputs.map((item) => asPositiveInteger(item?.slide)).filter(Boolean)
    : []
  const topSlides = Array.isArray(report?.slides)
    ? report.slides.map(asPositiveInteger).filter(Boolean)
    : []
  const single = asPositiveInteger(report?.slide)
  return [...new Set([...outputSlides, ...topSlides, ...(single ? [single] : [])])].sort(
    (left, right) => left - right,
  )
}

function outputForSlide(report, slide) {
  if (Array.isArray(report?.outputs)) {
    return report.outputs.find((item) => asPositiveInteger(item?.slide) === slide) ?? null
  }
  if (asPositiveInteger(report?.slide) === slide && report?.output_path) {
    return { slide, output_path: report.output_path, image: report.image }
  }
  return null
}

function validateImageBinding(item, runDir, errors) {
  const outputPath = item?.output_path ? resolve(item.output_path) : ''
  if (!outputPath || !existsSync(outputPath)) {
    errors.push({
      code: 'chartex-native-render-image-missing',
      slide: item?.slide ?? null,
      outputPath,
    })
    return null
  }
  if (!pathInside(runDir, outputPath)) {
    errors.push({
      code: 'chartex-native-render-image-outside-run',
      slide: item?.slide ?? null,
      outputPath,
    })
    return null
  }
  let actual
  try {
    actual = pngIdentity(outputPath)
  } catch (error) {
    errors.push({
      code: 'chartex-native-render-image-invalid',
      slide: item?.slide ?? null,
      outputPath,
      message: error.message,
    })
    return null
  }
  const declared = {
    pixelWidth: asPositiveInteger(item?.image?.pixel_width),
    pixelHeight: asPositiveInteger(item?.image?.pixel_height),
    byteLength: asPositiveInteger(item?.image?.byte_length),
    sha256: String(item?.image?.sha256 ?? '').toLowerCase(),
  }
  if (
    declared.pixelWidth !== actual.pixelWidth ||
    declared.pixelHeight !== actual.pixelHeight ||
    declared.byteLength !== actual.byteLength ||
    declared.sha256 !== actual.sha256
  ) {
    errors.push({
      code: 'chartex-native-render-image-identity-mismatch',
      slide: item?.slide ?? null,
      outputPath,
      declared,
      actual,
    })
  }
  return { slide: item?.slide ?? null, outputPath, ...actual }
}

export function validatePowerPointNativeRender({
  candidatePath,
  runDir,
  artifactPath,
  packageInfo,
}) {
  const errors = []
  if (!artifactPath || !existsSync(artifactPath)) {
    return { valid: false, errors: [{ code: 'chartex-native-render-missing' }], images: [] }
  }
  if (!pathInside(runDir, artifactPath)) {
    errors.push({ code: 'chartex-native-render-report-outside-run', artifactPath })
  }
  let report
  try {
    report = JSON.parse(readFileSync(artifactPath, 'utf8'))
  } catch (error) {
    return {
      valid: false,
      errors: [{ code: 'chartex-native-render-report-invalid', message: error.message }],
      images: [],
    }
  }

  const candidateBytes = readFileSync(candidatePath)
  const candidateSha256 = sha256(candidateBytes)
  const declaredPath = report?.pptx_path ? resolve(report.pptx_path) : ''
  if (report?.schema_version !== POWERPOINT_SNAPSHOT_SCHEMA_VERSION) {
    errors.push({
      code: 'chartex-native-render-schema-invalid',
      expected: POWERPOINT_SNAPSHOT_SCHEMA_VERSION,
      actual: report?.schema_version ?? null,
    })
  }
  if (report?.status !== 'ok' || report?.method !== 'pdf-render') {
    errors.push({
      code: 'chartex-native-render-method-invalid',
      status: report?.status ?? null,
      method: report?.method ?? null,
    })
  }
  if (!declaredPath || safeRealpath(declaredPath) !== safeRealpath(candidatePath)) {
    errors.push({
      code: 'chartex-native-render-candidate-path-mismatch',
      expected: safeRealpath(candidatePath),
      actual: declaredPath || null,
    })
  }
  if (String(report?.pptx_sha256 ?? '').toLowerCase() !== candidateSha256) {
    errors.push({
      code: 'chartex-native-render-candidate-hash-mismatch',
      expected: candidateSha256,
      actual: report?.pptx_sha256 ?? null,
    })
  }

  const coveredSlides = reportSlides(report)
  // Historical reports without hidden slides have an identity mapping. With
  // hidden slides, explicit logical-to-PDF mapping is required to avoid a false pass.
  const logicalSlides = readPptxPackage(candidatePath).slides()
  if (
    logicalSlides.some((slide) => slide.hidden) ||
    (report.pdf_pages !== null && report.pdf_pages !== undefined)
  ) {
    const visible = logicalSlides.filter((slide) => !slide.hidden)
    const exported =
      report.pdf_page_count === logicalSlides.length
        ? logicalSlides
        : report.pdf_page_count === visible.length
          ? visible
          : null
    const mapping = Array.isArray(report.pdf_pages) ? report.pdf_pages : []
    if (
      !exported ||
      packageInfo.chartExSlides.some((slide) => {
        const index = exported.findIndex((item) => item.slide === slide)
        const matches = mapping.filter((item) => item.slide === slide)
        return (
          index < 0 ||
          matches.length !== 1 ||
          matches[0].pdf_page !== index + 1 ||
          matches[0].part !== exported[index].part ||
          matches[0].hidden !== exported[index].hidden
        )
      })
    ) {
      errors.push({ code: 'chartex-native-render-pdf-page-identity-mismatch' })
    }
  }
  const missingSlides = packageInfo.chartExSlides.filter((slide) => !coveredSlides.includes(slide))
  if (packageInfo.chartExSlides.length === 0 || packageInfo.unmappedParts.length > 0) {
    errors.push({
      code: 'chartex-native-render-slide-scope-unresolved',
      chartExSlides: packageInfo.chartExSlides,
      unmappedParts: packageInfo.unmappedParts,
    })
  } else if (missingSlides.length > 0) {
    errors.push({
      code: 'chartex-native-render-slide-coverage-missing',
      requiredSlides: packageInfo.chartExSlides,
      coveredSlides,
      missingSlides,
    })
  }

  const images = []
  for (const slide of packageInfo.chartExSlides) {
    const item = outputForSlide(report, slide)
    if (!item) {
      errors.push({ code: 'chartex-native-render-output-missing', slide })
      continue
    }
    const identity = validateImageBinding(item, runDir, errors)
    if (identity) images.push(identity)
  }

  return {
    valid: errors.length === 0,
    errors,
    images,
    report: {
      schemaVersion: report?.schema_version ?? null,
      status: report?.status ?? null,
      method: report?.method ?? null,
      presentationName: report?.presentation_name ?? basename(candidatePath),
      candidateSha256,
      coveredSlides,
    },
  }
}

export function evaluateChartExNativeRender({
  candidatePath,
  runDir,
  artifactPath,
  availability = detectPowerPointAvailability(),
}) {
  if (!candidatePath) {
    return {
      status: 'not-run',
      applicable: null,
      reason: 'candidate-undisclosed',
      availability,
    }
  }
  if (!existsSync(candidatePath) || !statSync(candidatePath).isFile()) {
    return {
      status: 'failed',
      applicable: null,
      reason: 'candidate-missing',
      candidatePath,
      availability,
    }
  }

  let packageInfo
  try {
    packageInfo = inspectChartExPackage(candidatePath)
  } catch (error) {
    return {
      status: 'failed',
      applicable: null,
      reason: 'candidate-inspection-failed',
      candidatePath,
      availability,
      error: error.message,
    }
  }
  if (!packageInfo.hasChartEx) {
    return {
      status: 'not-applicable',
      applicable: false,
      reason: 'no-chartex-parts',
      candidatePath,
      packageInfo,
      availability,
    }
  }

  if (artifactPath && existsSync(artifactPath)) {
    const validation = validatePowerPointNativeRender({
      candidatePath,
      runDir,
      artifactPath,
      packageInfo,
    })
    return {
      status: validation.valid ? 'passed' : 'failed',
      applicable: true,
      reason: validation.valid ? 'candidate-bound-native-render' : 'native-render-invalid',
      candidatePath,
      artifactPath,
      packageInfo,
      availability,
      validation,
    }
  }

  return {
    status: availability.available ? 'failed' : 'warning',
    applicable: true,
    reason: availability.available
      ? 'native-render-required'
      : 'native-render-helper-unavailable-unverified',
    candidatePath,
    artifactPath: artifactPath || null,
    packageInfo,
    availability,
  }
}
