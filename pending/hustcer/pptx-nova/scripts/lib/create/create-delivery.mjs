import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { designHash, loadDesignContract } from '../../../assets/deckkits/shared/design-contract.mjs'
import { join, resolve } from 'node:path'
import { verifyRenderContext } from '../review/render-context.mjs'
import {
  captureVisualBinding,
  evaluateVisualEvidence,
  fileSha256,
} from '../review/canonical-visual-evidence.mjs'

export function recordCreateInputs(args, artifacts) {
  const paths = [
    args.content,
    args.lock,
    args.assets,
    args.choreography,
    args.choreography ? artifacts.deckkitPatch : null,
    artifacts.patch,
    artifacts.quality,
    artifacts.validation,
    artifacts.lockCheck,
    artifacts.dryRun,
    artifacts.apply,
    artifacts.vision,
    artifacts.candidate,
    artifacts.canonicalManifest,
    artifacts.renderContext,
    ...[
      artifacts.designContract,
      artifacts.designPlan,
      artifacts.designCheck,
      artifacts.designReadback,
      artifacts.designSemantic,
      artifacts.designInspect,
      artifacts.designModel,
    ].filter((p) => p && existsSync(p)),
  ].filter(Boolean)
  return {
    schemaVersion: 'pptx-nova-create-binding/v1',
    output: args.output,
    content: args.content,
    lock: args.lock,
    assets: args.assets,
    ...(args.choreography ? { choreography: args.choreography } : {}),
    files: paths.map((path) => ({ path, sha256: fileSha256(path) })),
  }
}

export function verifyCreateInputs(args, artifacts) {
  const before = JSON.parse(readFileSync(artifacts.binding, 'utf8'))
  if (JSON.stringify(before) !== JSON.stringify(recordCreateInputs(args, artifacts)))
    throw new Error(
      'Create inputs or machine evidence changed; generate and review a new candidate',
    )
  if (artifacts.designPlan && existsSync(artifacts.designPlan)) {
    const plan = JSON.parse(readFileSync(artifacts.designPlan, 'utf8'))
    if (plan.contractHash !== designHash(loadDesignContract(plan.designId)))
      throw new Error('Design contract changed; generate and review a new candidate')
  }
}

export function canonicalCreatePreview(summary, args, artifacts, runJsonPhase) {
  runJsonPhase(summary, {
    name: 'preview-render',
    bin: args.xdocBin,
    args: [
      'pptx',
      'visual-audit',
      '--candidate',
      artifacts.candidate,
      '--visual-mode',
      'create',
      '--output-dir',
      artifacts.canonicalDir,
      '--json',
    ],
    artifact: artifacts.previewReport,
  })
  verifyRenderContext(JSON.parse(readFileSync(artifacts.canonicalManifest, 'utf8')))
  const gate = evaluateVisualEvidence(artifacts.canonicalManifest, {
    candidate: artifacts.candidate,
  })
  writeFileSync(artifacts.visualGate, JSON.stringify(gate, null, 2) + '\n')
  if (!gate.machineChecksPassed)
    throw new Error(
      `Canonical create gate: ${gate.status}; ${gate.errors.join('; ')} ${gate.decision?.reasons?.join('; ') ?? ''}`,
    )
  const binding = captureVisualBinding(artifacts.canonicalManifest, artifacts.candidate)
  if (binding.slideCount !== summary.slideCount)
    throw new Error('canonical slide count does not match content')
  const pages = binding.artifacts.filter(
    (a) => a.mimeType === 'image/png' && a.subjectId === 'candidate',
  )
  const escape = (s) =>
    String(s).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;')
  const gallery =
    '<!doctype html><meta charset="utf-8"><title>Candidate review</title><style>body{background:#ddd;font:16px sans-serif}figure{margin:20px auto;max-width:1200px}img{width:100%;height:auto}</style>' +
    pages
      .map(
        (p) =>
          `<figure><figcaption>Slide ${p.slide}</figcaption><img src="${escape(p.path.split('/').map(encodeURIComponent).join('/'))}" alt="Slide ${p.slide}"></figure>`,
      )
      .join('\n')
  writeFileSync(artifacts.reviewGallery, gallery)
  summary.artifacts.previews = artifacts.canonicalDir
  summary.artifacts.contactSheet = null
  summary.review.instructions =
    'Open review.html or every canonical PNG; write design_review.json with slide-specific craft observations; record --candidate/--manifest/--design-review visual review, then rerun with --finalize --visual-review. No final output exists yet.'
  const phase = summary.phases.findLast((p) => p.name === 'preview-render')
  phase.slideCount = binding.slideCount
  phase.estimatedRenderedPixels = pages.reduce((sum, p) => {
    const bytes = readFileSync(join(artifacts.canonicalDir, p.path))
    return sum + bytes.readUInt32BE(16) * bytes.readUInt32BE(20)
  }, 0)
  writeFileSync(
    artifacts.binding,
    JSON.stringify(recordCreateInputs(args, artifacts), null, 2) + '\n',
  )
  return gate
}

export function validateCreateDelivery(summary, args, artifacts) {
  if (
    summary.mode !== 'create' ||
    summary.status !== 'needs-visual-review' ||
    summary.machineGatesPassed !== true
  )
    throw new Error('only a completed canonical create candidate can be finalized')
  if (
    resolve(summary.runDir) !== args.runDir ||
    resolve(summary.artifacts.candidate) !== artifacts.candidate
  )
    throw new Error('candidate does not belong to this run')
  verifyCreateInputs(args, artifacts)
  verifyRenderContext(JSON.parse(readFileSync(artifacts.canonicalManifest, 'utf8')))
  const lock = JSON.parse(readFileSync(args.lock, 'utf8'))
  const gate = evaluateVisualEvidence(artifacts.canonicalManifest, {
    candidate: artifacts.candidate,
    review: args.visualReview,
    expectedDesignMode: lock.artDirection?.mode ?? '',
  })
  writeFileSync(artifacts.visualGate, JSON.stringify(gate, null, 2) + '\n')
  if (!gate.deliveryAuthorized)
    throw new Error(`Create delivery gate: ${gate.status}; ${gate.errors.join('; ')}`)
  return gate
}
