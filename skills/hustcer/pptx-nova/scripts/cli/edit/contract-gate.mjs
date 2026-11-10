#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, join, posix, resolve } from 'node:path'
import { inflateRawSync } from 'node:zlib'
import { readResolvedSelectors } from '../../lib/pptx/resolved-selector.mjs'
import {
  documentFontTarget,
  fontAnalysisCoverage,
  validateFontContract,
} from '../../lib/edit/font-normalization.mjs'

const SCHEMA_VERSION = 'pptx-nova-edit-contract-gate/v1'
const CONTRACT_SCHEMA_VERSION = 'pptx-nova-edit-contract/v1'
const COPY_FROM_SCHEMA_VERSION = 'pptx-slide-copy/v1'
const COPY_SIZE_GATE_SCHEMA_VERSION = 'pptx-nova-copy-size-gate/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/contract-gate.mjs --contract <path> [options]

Verify source freshness, dry-run target coverage, reliable semantic diff locality,
and required scoped evidence for an existing-deck edit.

Options:
  --contract <path>        Required normalized edit-contract.json.
  --candidate <pptx>       Required stable run-directory candidate PPTX.
  --dry-run <path>         Defaults to dry-run.json beside the contract; accepts
                           pptx-dry-run/v1 or pptx-slide-copy/v1 preflight evidence.
  --copy-size-gate <path>  Defaults to copy-size-gate.json beside the contract;
                           required for native slide-copy structural evidence.
  --diff <path>            Defaults to pptx-diff.json beside the contract.
  --style-diff <path>      Defaults to style-diff.json beside the contract.
  --preview <path>         Defaults to preview.json beside the contract.
  --vision <path>          Defaults to vision.json beside the contract.
  --vision-diff <path>     Defaults to vision-diff.json beside the contract.
  --evidence-manifest <path> Defaults to evidence-manifest.json beside the contract.
  --final-inspect <path>   Optional/default final-inspect.json.
  --structure-check <path> Optional/default structure-check.json.
  --output <path>          Defaults to edit-contract-gate.json.
  --overwrite              Replace an existing gate report.
  --strict                 Exit 2 when blockers remain.
  --json                   Print the gate report to stdout.
  --help                   Show this help.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = {
    contract: '',
    candidate: '',
    dryRun: '',
    copySizeGate: '',
    diff: '',
    styleDiff: '',
    preview: '',
    vision: '',
    visionDiff: '',
    evidenceManifest: '',
    finalInspect: '',
    structureCheck: '',
    output: '',
    overwrite: false,
    strict: false,
    json: false,
  }
  const valueFlags = {
    '--contract': 'contract',
    '--candidate': 'candidate',
    '--dry-run': 'dryRun',
    '--copy-size-gate': 'copySizeGate',
    '--diff': 'diff',
    '--style-diff': 'styleDiff',
    '--preview': 'preview',
    '--vision': 'vision',
    '--vision-diff': 'visionDiff',
    '--evidence-manifest': 'evidenceManifest',
    '--final-inspect': 'finalInspect',
    '--structure-check': 'structureCheck',
    '--output': 'output',
    '-o': 'output',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--strict') {
      args.strict = true
    } else if (arg === '--json') {
      args.json = true
    } else if (valueFlags[arg]) {
      args[valueFlags[arg]] = valueAfter(argv, index, arg)
      index += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.contract) throw new Error(`--contract is required\n\n${usage}`)
  if (!args.candidate) throw new Error(`--candidate is required\n\n${usage}`)
  args.contract = resolve(args.contract)
  args.candidate = resolve(args.candidate)
  if (!existsSync(args.contract)) throw new Error(`contract does not exist: ${args.contract}`)
  if (!existsSync(args.candidate)) throw new Error(`candidate does not exist: ${args.candidate}`)
  const runDir = dirname(args.contract)
  args.dryRun = resolve(args.dryRun || join(runDir, 'dry-run.json'))
  args.copySizeGate = resolve(args.copySizeGate || join(runDir, 'copy-size-gate.json'))
  args.diff = resolve(args.diff || join(runDir, 'pptx-diff.json'))
  args.styleDiff = resolve(args.styleDiff || join(runDir, 'style-diff.json'))
  args.preview = resolve(args.preview || join(runDir, 'preview.json'))
  args.vision = resolve(args.vision || join(runDir, 'vision.json'))
  args.visionDiff = resolve(args.visionDiff || join(runDir, 'vision-diff.json'))
  args.evidenceManifest = resolve(args.evidenceManifest || join(runDir, 'evidence-manifest.json'))
  args.finalInspect = resolve(args.finalInspect || join(runDir, 'final-inspect.json'))
  args.structureCheck = resolve(args.structureCheck || join(runDir, 'structure-check.json'))
  args.output = resolve(args.output || join(runDir, 'edit-contract-gate.json'))
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(`output already exists: ${args.output}; use --overwrite for the current run`)
  }
  return args
}

function readJson(path, label, { required = true } = {}) {
  if (!existsSync(path)) {
    if (required) throw new Error(`${label} does not exist: ${path}`)
    return null
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    throw new Error(`${label} is not valid JSON: ${message}`)
  }
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function findEndOfCentralDirectory(buffer) {
  for (let offset = buffer.length - 22; offset >= 0; offset -= 1) {
    if (buffer.readUInt32LE(offset) === 0x06054b50) return offset
  }
  throw new Error('PPTX ZIP end of central directory was not found')
}

function readZipEntries(path) {
  const buffer = readFileSync(path)
  const eocd = findEndOfCentralDirectory(buffer)
  const entryCount = buffer.readUInt16LE(eocd + 10)
  const centralOffset = buffer.readUInt32LE(eocd + 16)
  const entries = []
  let cursor = centralOffset
  for (let index = 0; index < entryCount; index += 1) {
    if (buffer.readUInt32LE(cursor) !== 0x02014b50) {
      throw new Error(`Invalid ZIP central directory entry at ${cursor}`)
    }
    const method = buffer.readUInt16LE(cursor + 10)
    const compressedSize = buffer.readUInt32LE(cursor + 20)
    const uncompressedSize = buffer.readUInt32LE(cursor + 24)
    const fileNameLength = buffer.readUInt16LE(cursor + 28)
    const extraLength = buffer.readUInt16LE(cursor + 30)
    const commentLength = buffer.readUInt16LE(cursor + 32)
    const localOffset = buffer.readUInt32LE(cursor + 42)
    const name = buffer.toString('utf8', cursor + 46, cursor + 46 + fileNameLength)
    cursor += 46 + fileNameLength + extraLength + commentLength
    if (buffer.readUInt32LE(localOffset) !== 0x04034b50) {
      throw new Error(`Invalid ZIP local file header for ${name}`)
    }
    const localNameLength = buffer.readUInt16LE(localOffset + 26)
    const localExtraLength = buffer.readUInt16LE(localOffset + 28)
    const dataStart = localOffset + 30 + localNameLength + localExtraLength
    const compressed = buffer.subarray(dataStart, dataStart + compressedSize)
    let data
    if (method === 0) data = compressed
    else if (method === 8) data = inflateRawSync(compressed)
    else continue
    if (uncompressedSize !== 0 && data.length !== uncompressedSize) {
      throw new Error(`ZIP entry size mismatch for ${name}`)
    }
    entries.push({ name, data })
  }
  return entries
}

function normalizeHex(value) {
  const hex = String(value ?? '')
    .replace(/^#/, '')
    .trim()
    .toUpperCase()
  return /^[0-9A-F]{6}$/.test(hex) ? hex : null
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function slideXmlEntries(candidate) {
  const entries = readZipEntries(candidate)
  const byName = new Map(entries.map((entry) => [entry.name, entry]))
  const presentation = byName.get('ppt/presentation.xml')?.data.toString('utf8') ?? ''
  const relationships = byName.get('ppt/_rels/presentation.xml.rels')?.data.toString('utf8') ?? ''
  const relationshipTargets = new Map()
  for (const match of relationships.matchAll(/<Relationship\b[^>]*>/g)) {
    const tag = match[0]
    const id = tag.match(/\bId="([^"]+)"/)?.[1]
    const target = tag.match(/\bTarget="([^"]+)"/)?.[1]
    if (!id || !target) continue
    const name = target.startsWith('/')
      ? target.slice(1)
      : posix.normalize(posix.join('ppt', target))
    relationshipTargets.set(id, name)
  }
  const ordered = []
  for (const match of presentation.matchAll(/<p:sldId\b[^>]*\br:id="([^"]+)"[^>]*\/?\s*>/g)) {
    const name = relationshipTargets.get(match[1])
    const entry = name ? byName.get(name) : null
    if (entry) ordered.push({ index: ordered.length, name, xml: entry.data.toString('utf8') })
  }
  if (ordered.length > 0) return ordered
  return entries
    .filter((entry) => /^ppt\/slides\/slide\d+\.xml$/.test(entry.name))
    .map((entry) => ({
      index: Number(entry.name.match(/slide(\d+)\.xml$/)?.[1] ?? 0) - 1,
      name: entry.name,
      xml: entry.data.toString('utf8'),
    }))
    .sort((left, right) => left.index - right.index)
}

function findShapeXml(slides, slideIndex, identity) {
  const hasId = identity.id !== null && identity.id !== undefined
  const identityPattern = new RegExp(
    `\\b${hasId ? 'id' : 'name'}="${escapeRegExp(hasId ? identity.id : identity.name)}"`,
  )
  const slide = slides.find((item) => item.index === slideIndex)
  if (!slide) return null
  const blocks = slide.xml.match(/<p:sp(?:\s[^>]*)?>[\s\S]*?<\/p:sp>/g) ?? []
  const matches = blocks.filter((item) => {
    const nonVisualProperties = item.match(/<p:cNvPr\b[^>]*>/)?.[0]
    return nonVisualProperties && identityPattern.test(nonVisualProperties)
  })
  return matches.length === 1 ? { part: slide.name, xml: matches[0] } : null
}

function shapeFontColors(shapeXml) {
  const colors = []
  for (const match of shapeXml.matchAll(/<a:rPr\b[^>]*>([\s\S]*?)<\/a:rPr>/g)) {
    const color = match[1].match(/<a:srgbClr\b[^>]*\bval="([0-9A-Fa-f]{6})"/i)?.[1]
    colors.push(normalizeHex(color))
  }
  return colors
}

function shapeFillColor(shapeXml) {
  const shapeProperties = shapeXml.match(/<p:spPr\b[^>]*>([\s\S]*?)<\/p:spPr>/)?.[1] ?? ''
  return normalizeHex(
    shapeProperties.match(
      /<a:solidFill\b[^>]*>[\s\S]*?<a:srgbClr\b[^>]*\bval="([0-9A-Fa-f]{6})"/i,
    )?.[1],
  )
}

function sameJson(left, right) {
  return JSON.stringify(left) === JSON.stringify(right)
}

function sessionOverlayMatchesContract(contract, resolution) {
  const overlay = resolution.contractOverlay ?? {}
  for (const expected of overlay.targets ?? []) {
    const actual = contract.targets.find((target) => target.id === expected.id)
    if (!actual) return false
    if (
      actual.produced !== expected.produced ||
      actual.slide !== expected.slide ||
      !sameJson(actual.opIndexes, expected.opIndexes) ||
      !sameJson(actual.sessionRuleIds ?? [], expected.sessionRuleIds ?? []) ||
      actual.resolvedIdentity?.name !== expected.resolvedIdentity?.name ||
      !sameJson(
        actual.expected?.sessionRulePostconditions ?? [],
        expected.expected?.sessionRulePostconditions ?? [],
      )
    ) {
      return false
    }
  }
  for (const value of overlay.preserve ?? []) if (!contract.preserve.includes(value)) return false
  for (const value of overlay.allowedChanges ?? []) {
    if (!contract.allowedChanges.includes(value)) return false
  }
  for (const value of overlay.requiredEvidence ?? []) {
    if (!contract.requiredEvidence.includes(value)) return false
  }
  return true
}

function checkSessionRulesBinding(contract, report) {
  if (!contract.sessionRules) return null
  const binding = contract.sessionRules
  const paths = [
    ['rules', binding.rulesPath, binding.rulesSha256],
    ['resolution', binding.resolutionPath, binding.resolutionSha256],
    ['operation', binding.operationPath, binding.operationSha256],
  ]
  let stale = false
  for (const [kind, path, expectedSha256] of paths) {
    if (!path || !existsSync(path) || sha256(path) !== expectedSha256) {
      stale = true
      addIssue(
        report,
        'blockers',
        'session-rules-binding-stale',
        `${kind} session rules artifact is missing or changed after contract generation`,
        { kind, path: path ?? null },
      )
    }
  }
  if (stale) return null
  const rules = readJson(binding.rulesPath, 'session rules')
  const resolution = readJson(binding.resolutionPath, 'session rules resolution')
  if (
    rules.schemaVersion !== 'pptx-nova-session-rules/v1' ||
    resolution.schemaVersion !== 'pptx-nova-session-rules-resolution/v1' ||
    resolution.status !== 'pass' ||
    resolution.agentGate?.passed !== true ||
    rules.deckIdentity?.deckId !== binding.deckId ||
    rules.deckIdentity?.currentRevisionSha256 !== contract.source?.sha256 ||
    resolution.source?.sha256 !== contract.source?.sha256 ||
    JSON.stringify(resolution.applicableRules.map((item) => item.id)) !==
      JSON.stringify(binding.applicableRuleIds) ||
    !sessionOverlayMatchesContract(contract, resolution)
  ) {
    addIssue(
      report,
      'blockers',
      'session-rules-binding-stale',
      'session rules binding no longer matches the contract source or applicable rule set',
    )
    return null
  }
  addCheck(report, 'session-rules-binding', 'pass', {
    deckId: binding.deckId,
    applicableRuleCount: binding.applicableRuleIds.length,
  })
  return resolution
}

function checkSessionRulePostconditions(contract, args, resolution, finalInspect, report) {
  if (!contract.sessionRules || !resolution) return
  const results = (resolution.notApplicableRules ?? []).map((item) => ({
    id: item.id,
    status: 'not-applicable',
    reason: item.reason,
    ...(item.source ? { source: item.source } : {}),
    targets: [],
    postconditions: [],
  }))
  if ((resolution.applicableRules ?? []).every((item) => item.kind === 'preserve-invariant')) {
    for (const applicable of resolution.applicableRules ?? []) {
      results.push({
        id: applicable.id,
        kind: applicable.kind,
        status: 'satisfied',
        targets: [],
        postconditions: [],
      })
    }
    report.sessionRuleResults = results
    addCheck(report, 'session-rule-postconditions', 'pass', {
      satisfied: results.filter((item) => item.status === 'satisfied').length,
      notApplicable: results.filter((item) => item.status === 'not-applicable').length,
      total: results.length,
    })
    return
  }
  let slides
  try {
    slides = slideXmlEntries(args.candidate)
  } catch (error) {
    addIssue(
      report,
      'blockers',
      'session-rule-candidate-inspection-failed',
      `candidate PPTX could not be inspected for session rule postconditions: ${error instanceof Error ? error.message : String(error)}`,
    )
    return
  }
  for (const applicable of resolution.applicableRules) {
    const ruleTargets = contract.targets.filter((target) =>
      (target.sessionRuleIds ?? []).includes(applicable.id),
    )
    if (applicable.kind === 'preserve-invariant') {
      results.push({ id: applicable.id, kind: applicable.kind, status: 'satisfied', targets: [] })
      continue
    }
    const targetResults = []
    let rulePassed = ruleTargets.length > 0
    for (const target of ruleTargets) {
      const inspected = findInspectedShape(finalInspect, target)
      const shape = inspected ? findShapeXml(slides, target.slide, inspected) : null
      const postconditions = []
      for (const condition of target.expected?.sessionRulePostconditions ?? []) {
        let actual = null
        if (shape && condition.kind === 'font-color') {
          const colors = shapeFontColors(shape.xml)
          actual = colors.length === 1 ? colors[0] : colors
          const passed = colors.length > 0 && colors.every((color) => color === condition.value)
          postconditions.push({ ...condition, expected: condition.value, actual, passed })
          rulePassed &&= passed
        } else if (shape && condition.kind === 'fill-color') {
          actual = shapeFillColor(shape.xml)
          const passed = actual === condition.value
          postconditions.push({ ...condition, expected: condition.value, actual, passed })
          rulePassed &&= passed
        } else {
          postconditions.push({
            ...condition,
            expected: condition.value,
            actual: null,
            passed: false,
          })
          rulePassed = false
        }
      }
      if (!inspected || !shape || postconditions.length === 0) rulePassed = false
      targetResults.push({
        targetId: target.id,
        slide: target.slide,
        shapeId: inspected?.id ?? null,
        shapeName: target.resolvedIdentity?.name ?? null,
        inspected: Boolean(inspected),
        candidatePart: shape?.part ?? null,
        postconditions,
      })
    }
    const result = {
      id: applicable.id,
      kind: applicable.kind,
      status: rulePassed ? 'satisfied' : 'blocked',
      targets: targetResults,
      postconditions: targetResults.flatMap((item) => item.postconditions),
    }
    results.push(result)
    if (!rulePassed) {
      addIssue(
        report,
        'blockers',
        'session-rule-postcondition-failed',
        `candidate does not satisfy applicable session rule ${applicable.id}`,
        { ruleId: applicable.id, targets: targetResults },
      )
    }
  }
  report.sessionRuleResults = results
  addCheck(
    report,
    'session-rule-postconditions',
    results.every((item) => item.status !== 'blocked') ? 'pass' : 'fail',
    {
      satisfied: results.filter((item) => item.status === 'satisfied').length,
      notApplicable: results.filter((item) => item.status === 'not-applicable').length,
      total: results.length,
    },
  )
}

function checkEvidenceManifest(args, loaded, report) {
  const manifest = readJson(args.evidenceManifest, 'evidence manifest', { required: false })
  if (!manifest) {
    addIssue(
      report,
      'blockers',
      'required-evidence-missing',
      'required evidence manifest is missing',
      { kind: 'evidence-manifest', path: args.evidenceManifest },
    )
    return
  }
  const candidateHash = sha256(args.candidate)
  if (manifest.schemaVersion !== 'pptx-nova-edit-evidence-manifest/v1') {
    addIssue(report, 'blockers', 'evidence-manifest-invalid', 'evidence manifest schema is invalid')
    return
  }
  if (
    reportedPath(manifest.candidate, dirname(args.evidenceManifest)) !== args.candidate ||
    manifest.candidate?.sha256 !== candidateHash
  ) {
    addIssue(
      report,
      'blockers',
      'evidence-manifest-candidate-mismatch',
      'evidence manifest does not bind the current candidate bytes',
    )
  }
  const entries = new Map((manifest.evidence ?? []).map((item) => [item.kind, item]))
  for (const kind of Object.keys(loaded).filter((item) => item !== 'dry-run')) {
    const path = evidencePath(args, kind)
    const entry = entries.get(kind)
    if (
      !entry ||
      reportedPath(entry, dirname(args.evidenceManifest)) !== path ||
      entry.sha256 !== sha256(path)
    ) {
      addIssue(
        report,
        'blockers',
        'evidence-manifest-artifact-mismatch',
        `${kind} evidence is not bound to the manifest`,
        { kind },
      )
    }
  }
}

function addIssue(report, list, code, message, details = {}) {
  report[list].push({ code, message, ...details })
}

function addCheck(report, name, status, details = {}) {
  report.checks.push({ name, status, ...details })
}

function selectorIdentity(target) {
  const shape = target?.selector?.shape ?? target?.selector ?? {}
  const resolved = target?.resolvedIdentity ?? {}
  return {
    slide: target?.slide,
    id: resolved?.id ?? shape?.id ?? null,
    name: resolved?.name ?? shape?.name ?? null,
  }
}

function hasStableIdentity(target) {
  if (target?.kind === 'document-fonts') return true
  const identity = selectorIdentity(target)
  return target?.kind === 'slide' || identity.id !== null || Boolean(identity.name)
}

function sameIdentity(actual, expected) {
  if (!actual || !expected) return false
  if (Number.isInteger(expected.slide) && actual.slide !== expected.slide) return false
  if (expected.id !== null && expected.id !== undefined && actual.id !== expected.id) return false
  if (expected.name && actual.name !== expected.name) return false
  return expected.id !== null || Boolean(expected.name) || Number.isInteger(expected.slide)
}

function resultIdentities(result) {
  const identities = []
  for (const item of readResolvedSelectors(result)) {
    identities.push(item.resolved)
  }
  for (const item of result?.semanticChanges ?? []) {
    if (item?.target) identities.push(item.target)
  }
  return identities
}

function targetCoverage(contract, dryRun, report) {
  const opResults = new Map(
    (Array.isArray(dryRun?.opResults) ? dryRun.opResults : [])
      .filter((item) => Number.isInteger(item?.opIndex))
      .map((item) => [item.opIndex, item]),
  )
  const coveredIdentities = []
  const coverage = []

  for (const target of contract.targets) {
    const expectedIdentity = selectorIdentity(target)
    const slideTarget = target.kind === 'slide'
    const results = target.opIndexes.map((opIndex) => opResults.get(opIndex)).filter(Boolean)
    const missingOps = target.opIndexes.filter((opIndex) => !opResults.has(opIndex))
    const failedOps = results
      .filter((item) => item.status !== 'success')
      .map((item) => item.opIndex)
    if (target.kind === 'document-fonts') {
      const fontCoverage = fontAnalysisCoverage(target, results)
      const categoriesValid = results.every(
        (result) =>
          Array.isArray(result.semanticChanges) &&
          result.semanticChanges.every((change) => change.category === 'style'),
      )
      const covered =
        fontCoverage.covered &&
        missingOps.length === 0 &&
        categoriesValid &&
        dryRun.opResults.length === 1
      if (!covered)
        addIssue(
          report,
          'blockers',
          fontCoverage.reason ?? 'font-analysis-invalid',
          'set-font evidence must match the document font intent and reviewed selection analysis',
        )
      coverage.push({
        id: target.id,
        kind: target.kind,
        opIndexes: target.opIndexes,
        ...fontCoverage,
        covered,
        missingOps,
        failedOps,
        selectorMatchCount: null,
        expectedAfterObserved: true,
        unexpectedCategories: categoriesValid ? [] : ['non-style'],
        resolvedIdentities: [],
      })
      continue
    }
    const identities = results.flatMap(resultIdentities)
    const matchingIdentities = slideTarget
      ? identities.filter((item) => item?.slide === target.slide)
      : identities.filter((item) => sameIdentity(item, expectedIdentity))
    const semanticChanges = results.flatMap((item) => item.semanticChanges ?? [])
    const expectedAfter = target.expected?.afterText
    const alreadyCompliant = target.expected?.alreadyCompliant === true
    const afterObserved =
      expectedAfter === undefined ||
      semanticChanges.some(
        (item) => item?.after === expectedAfter && sameIdentity(item?.target, expectedIdentity),
      ) ||
      (alreadyCompliant && semanticChanges.length === 0)
    const categories = [
      ...new Set(semanticChanges.map((item) => String(item?.category ?? '')).filter(Boolean)),
    ]
    const unexpectedCategories = categories.filter(
      (category) =>
        !contract.allowedChanges.includes(category) ||
        !(target.expected?.changeCategories ?? []).includes(category),
    )
    const covered =
      missingOps.length === 0 &&
      failedOps.length === 0 &&
      (slideTarget || matchingIdentities.length > 0) &&
      afterObserved &&
      unexpectedCategories.length === 0

    if (matchingIdentities.length > 0) {
      for (const identity of matchingIdentities) {
        if (!coveredIdentities.some((item) => sameIdentity(item, identity))) {
          coveredIdentities.push(identity)
        }
      }
    }
    coverage.push({
      id: target.id,
      slide: target.slide,
      opIndexes: target.opIndexes,
      covered,
      missingOps,
      failedOps,
      selectorMatchCount: matchingIdentities.length,
      expectedAfterObserved: afterObserved,
      alreadyCompliant,
      changeCategories: categories,
      unexpectedCategories,
      resolvedIdentities: matchingIdentities,
    })
  }

  const coveredCount = coverage.filter((item) => item.covered).length
  if (
    contract.coverage?.required !== false &&
    coveredCount !== contract.coverage.expectedTargetCount
  ) {
    addIssue(
      report,
      'blockers',
      'target-coverage-incomplete',
      `dry-run covered ${coveredCount} of ${contract.coverage.expectedTargetCount} required target(s)`,
      { coverage },
    )
  }
  if (
    coverage.some(
      (item) =>
        !['slide', 'document-fonts'].includes(
          contract.targets.find((target) => target.id === item.id)?.kind,
        ) &&
        item.selectorMatchCount === 0 &&
        item.missingOps.length === 0,
    )
  ) {
    addIssue(
      report,
      'blockers',
      'selector-resolution-missing',
      'one or more target ops did not resolve to the contract selector',
    )
  }
  if (coverage.some((item) => !item.expectedAfterObserved)) {
    addIssue(
      report,
      'blockers',
      'expected-after-not-observed',
      'dry-run did not report the expected post-edit value for one or more targets',
    )
  }
  if (coverage.some((item) => item.unexpectedCategories.length > 0)) {
    addIssue(
      report,
      'blockers',
      'dry-run-change-category-outside-contract',
      'dry-run reported a change category not allowed by the contract',
    )
  }
  return { coverage, coveredCount, coveredIdentities }
}

function copyFromEntryValid(entry, copyReport) {
  const changedParts = new Set(copyReport?.changedParts ?? [])
  if (
    !Number.isInteger(entry?.sourceSlide) ||
    !Number.isInteger(entry?.targetSlide) ||
    typeof entry?.sourceSlidePartName !== 'string' ||
    typeof entry?.sourceSlideRelsPartName !== 'string' ||
    typeof entry?.targetSlidePartName !== 'string' ||
    typeof entry?.targetSlideRelsPartName !== 'string' ||
    !Array.isArray(entry?.dependencies)
  ) {
    return false
  }
  const plannedParts = Array.isArray(copyReport?.preflight?.parts) ? copyReport.preflight.parts : []
  const requiredMutations = [entry.targetSlidePartName, entry.targetSlideRelsPartName]
  const slidePlan = plannedParts.find(
    (item) =>
      item?.sourceSlide === entry.sourceSlide &&
      item?.sourcePartName === entry.sourceSlidePartName &&
      item?.targetPartName === entry.targetSlidePartName &&
      item?.role === 'slide' &&
      item?.action === 'add',
  )
  const slideRelsPlan = plannedParts.find(
    (item) =>
      item?.sourceSlide === entry.sourceSlide &&
      item?.sourcePartName === entry.sourceSlideRelsPartName &&
      item?.targetPartName === entry.targetSlideRelsPartName &&
      item?.role === 'relationship' &&
      item?.action === 'add',
  )
  if (!slidePlan || !slideRelsPlan) return false
  const dependencyMappings = Array.isArray(copyReport?.dependencyMappings)
    ? copyReport.dependencyMappings
    : []
  for (const dependency of entry.dependencies) {
    if (
      typeof dependency?.sourcePartName !== 'string' ||
      typeof dependency?.targetPartName !== 'string'
    ) {
      return false
    }
    const mapped = dependencyMappings.some(
      (item) =>
        item?.sourceSlide === entry.sourceSlide &&
        item?.targetSlide === entry.targetSlide &&
        item?.sourcePartName === dependency.sourcePartName &&
        item?.targetPartName === dependency.targetPartName,
    )
    const planned = plannedParts.find(
      (item) =>
        item?.sourceSlide === entry.sourceSlide &&
        item?.sourcePartName === dependency.sourcePartName &&
        item?.targetPartName === dependency.targetPartName,
    )
    if (!mapped || !planned || !['add', 'reuse', 'rename', 'rebind'].includes(planned.action)) {
      return false
    }
    if (planned.action !== 'reuse') requiredMutations.push(dependency.targetPartName)
  }
  return requiredMutations.every((part) => changedParts.has(part))
}

function sha256LooksValid(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/.test(value)
}

function checkCopyFromPreflight(contract, copyReport, report) {
  const preflight = copyReport?.preflight
  const workspace = contract.workspace || '.'
  let valid = true
  const fail = (code, message, details = {}) => {
    valid = false
    addIssue(report, 'blockers', code, message, details)
  }
  if (!preflight || typeof preflight !== 'object') {
    fail(
      'slide-copy-preflight-missing',
      'slide-copy/v2 evidence is missing its read-only preflight plan',
    )
    return false
  }
  if (
    preflight.ready !== true ||
    preflight.readOnly !== true ||
    !Array.isArray(preflight.parts) ||
    !Array.isArray(preflight.relationships) ||
    !Array.isArray(preflight.blockers) ||
    !Array.isArray(preflight.risks) ||
    !Array.isArray(preflight.preserveOnlyRisks) ||
    !Array.isArray(preflight.templates)
  ) {
    fail(
      'slide-copy-preflight-invalid',
      'slide-copy preflight must be ready, read-only, and include template, part, relationship, blocker, preserve-only risk, and risk arrays',
    )
  }
  if (
    !preflight.summary ||
    preflight.summary.partCount !== preflight.parts?.length ||
    preflight.summary.relationshipCount !== preflight.relationships?.length ||
    preflight.summary.blockerCount !== preflight.blockers?.length ||
    preflight.summary.riskCount !== preflight.risks?.length
  ) {
    fail(
      'slide-copy-preflight-summary-mismatch',
      'slide-copy preflight summary counts must exactly match the disclosed plan arrays',
    )
  }
  if (preflight.blockers?.length > 0 || Number(preflight.summary?.blockerCount ?? 0) > 0) {
    fail(
      'slide-copy-preflight-blocked',
      'slide-copy preflight contains blockers and cannot authorize a structural mutation',
      { blockers: preflight.blockers },
    )
  }
  if (
    !Number.isInteger(preflight.targetSlideCountBefore) ||
    !Number.isInteger(preflight.targetSlideCountAfter) ||
    preflight.targetSlideCountAfter - preflight.targetSlideCountBefore !==
      (copyReport.copied?.length ?? 0)
  ) {
    fail(
      'slide-copy-preflight-slide-count-invalid',
      'slide-copy preflight slide counts do not match the planned copied slide count',
    )
  }

  const targetPath = reportedPath(copyReport?.input, workspace)
  const donorPath = reportedPath(copyReport?.source?.path, workspace)
  const targetFileSha256 =
    targetPath && existsSync(targetPath) ? sha256(targetPath) : contract.source?.sha256
  const donorFileSha256 = donorPath && existsSync(donorPath) ? sha256(donorPath) : null
  if (
    !sha256LooksValid(preflight.targetFileSha256) ||
    preflight.targetFileSha256 !== targetFileSha256 ||
    preflight.targetFileSha256 !== contract.source?.sha256
  ) {
    fail(
      'slide-copy-target-file-sha256-mismatch',
      'slide-copy preflight targetFileSha256 is not bound to the current target PPTX bytes',
      {
        expected: contract.source?.sha256 ?? null,
        actual: preflight.targetFileSha256 ?? null,
      },
    )
  }
  if (
    !sha256LooksValid(preflight.sourceFileSha256) ||
    !donorFileSha256 ||
    preflight.sourceFileSha256 !== donorFileSha256
  ) {
    fail(
      'slide-copy-source-file-sha256-mismatch',
      'slide-copy preflight sourceFileSha256 is not bound to the declared donor PPTX bytes',
      {
        expected: donorFileSha256,
        actual: preflight.sourceFileSha256 ?? null,
      },
    )
  }
  if (
    !sha256LooksValid(preflight.targetFingerprint) ||
    !sha256LooksValid(preflight.sourceFingerprint)
  ) {
    fail(
      'slide-copy-package-fingerprint-invalid',
      'slide-copy preflight must include normalized OPC source/target package fingerprints',
    )
  }
  const templateStrategy = preflight.strategy?.template
  const slideSizeStrategy = preflight.strategy?.slideSize
  if (!['register-source', 'rebind-target'].includes(templateStrategy)) {
    fail(
      'slide-copy-template-strategy-invalid',
      'slide-copy preflight must declare register-source or rebind-target',
    )
  }
  if (slideSizeStrategy !== 'require-match') {
    fail(
      'slide-copy-size-strategy-invalid',
      'slide-copy preflight must declare slideSize strategy require-match',
    )
  }
  const allowedTemplateOutcomes =
    templateStrategy === 'register-source'
      ? new Set(['registered-source', 'reused-source'])
      : new Set(['rebound-target', 'reused-source'])
  for (const template of preflight.templates ?? []) {
    if (
      !allowedTemplateOutcomes.has(template?.outcome) ||
      !template?.layout?.sourcePartName ||
      !template?.layout?.targetPartName ||
      !template?.master?.sourcePartName ||
      !template?.master?.targetPartName ||
      template?.rollbackBoundary !== 'entire-copy-batch'
    ) {
      fail(
        'slide-copy-template-plan-invalid',
        'slide-copy templates[] contains an invalid outcome, mapping, or rollback boundary',
        { template },
      )
      break
    }
  }
  if (copyReport?.transaction?.rollbackBoundary !== 'entire-copy-batch') {
    fail(
      'slide-copy-rollback-boundary-invalid',
      'slide-copy report must declare the entire-copy-batch rollback boundary',
    )
  }
  if (preflight.risks?.length > 0) {
    addIssue(
      report,
      'attention',
      'slide-copy-preflight-risks',
      'slide-copy preflight reported fidelity risks that require Agent review',
      { risks: preflight.risks },
    )
  }
  addCheck(report, 'slide-copy-preflight', valid ? 'pass' : 'fail', {
    readOnly: preflight.readOnly === true,
    ready: preflight.ready === true,
    parts: preflight.parts?.length ?? 0,
    relationships: preflight.relationships?.length ?? 0,
    blockers: preflight.blockers?.length ?? 0,
    risks: preflight.risks?.length ?? 0,
  })
  return valid
}

function checkCopySizeGate(contract, copyReport, sizeGate, report) {
  const workspace = contract.workspace || '.'
  const targetPath = reportedPath(sizeGate?.target?.path, workspace)
  const donorPath = reportedPath(sizeGate?.donor?.path, workspace)
  const expectedTargetPath = resolve(contract.source?.pptx ?? '')
  const expectedDonorPath = reportedPath(copyReport?.source?.path, workspace)
  const valid =
    sizeGate?.schemaVersion === COPY_SIZE_GATE_SCHEMA_VERSION &&
    sizeGate?.status === 'pass' &&
    sizeGate?.agentGate?.passed === true &&
    sizeGate?.slideSizeComparison?.matches === true &&
    targetPath === expectedTargetPath &&
    donorPath === expectedDonorPath &&
    sizeGate?.target?.fileSha256 === copyReport?.preflight?.targetFileSha256 &&
    sizeGate?.donor?.fileSha256 === copyReport?.preflight?.sourceFileSha256
  addCheck(report, 'copy-size-gate', valid ? 'pass' : 'fail', {
    matches: sizeGate?.slideSizeComparison?.matches === true,
    nextAction: sizeGate?.agentGate?.nextAction ?? null,
    targetPath: targetPath || null,
    donorPath: donorPath || null,
  })
  if (!valid) {
    const mismatch = sizeGate?.slideSizeComparison?.matches === false
    addIssue(
      report,
      'blockers',
      mismatch ? 'copy-size-gate-failed' : 'copy-size-gate-stale',
      mismatch
        ? 'donor and target slide sizes differ under native require-match'
        : 'copy size gate is missing, failed, or not bound to the current slide-copy preflight',
      { sizeGate: sizeGate?.agentGate ?? null },
    )
  }
}

function copyFromExpectation(target) {
  const expected = target?.expected?.copyFrom ?? target?.copyFrom ?? {}
  return {
    sourceSlide: expected.sourceSlide ?? target?.expected?.sourceSlide ?? null,
    sourcePptx: expected.sourcePptx ?? target?.expected?.sourcePptx ?? null,
  }
}

function copyFromCoverage(contract, copyReport, report) {
  const copied = Array.isArray(copyReport?.copied) ? copyReport.copied : []
  const coverage = []
  const coveredIdentities = []
  const targetSlides = new Set(contract.targets.map((target) => target.slide))
  const outOfScope = copied.filter((entry) => !targetSlides.has(entry?.targetSlide))
  if (outOfScope.length > 0) {
    addIssue(
      report,
      'blockers',
      'slide-copy-slide-outside-contract',
      'slide-copy evidence contains target slides not owned by the structural contract',
      { targetSlides: outOfScope.map((entry) => entry?.targetSlide ?? null) },
    )
  }

  for (const target of contract.targets) {
    const entry = copied.find((item) => item?.targetSlide === target.slide) ?? null
    const expectation = copyFromExpectation(target)
    const sourceSlideMatches =
      !Number.isInteger(expectation.sourceSlide) || entry?.sourceSlide === expectation.sourceSlide
    const sourcePptxMatches =
      !expectation.sourcePptx ||
      reportedPath(copyReport?.source?.path, contract.workspace || '.') ===
        resolve(contract.workspace || '.', expectation.sourcePptx)
    const structuralEvidenceValid = entry ? copyFromEntryValid(entry, copyReport) : false
    const categories = ['structure']
    const unexpectedCategories = categories.filter(
      (category) =>
        !contract.allowedChanges.includes(category) ||
        !(target.expected?.changeCategories ?? []).includes(category),
    )
    const covered =
      Boolean(entry) &&
      sourceSlideMatches &&
      sourcePptxMatches &&
      structuralEvidenceValid &&
      unexpectedCategories.length === 0
    if (entry) coveredIdentities.push({ kind: 'slide', slide: target.slide })
    coverage.push({
      id: target.id,
      slide: target.slide,
      opIndexes: target.opIndexes,
      covered,
      missingOps: [],
      failedOps: [],
      selectorMatchCount: entry ? 1 : 0,
      expectedAfterObserved: Boolean(entry),
      alreadyCompliant: false,
      changeCategories: categories,
      unexpectedCategories,
      resolvedIdentities: entry ? [{ kind: 'slide', slide: target.slide }] : [],
      copyFrom: entry
        ? {
            sourceSlide: entry.sourceSlide,
            targetSlide: entry.targetSlide,
            sourceSlidePartName: entry.sourceSlidePartName,
            sourceSlideRelsPartName: entry.sourceSlideRelsPartName,
            targetSlidePartName: entry.targetSlidePartName,
            targetSlideRelsPartName: entry.targetSlideRelsPartName,
            dependencyCount: entry.dependencies.length,
          }
        : null,
    })
    if (entry && !sourceSlideMatches) {
      addIssue(
        report,
        'blockers',
        'slide-copy-source-slide-mismatch',
        `slide-copy source slide does not match contract target ${target.id}`,
        {
          targetId: target.id,
          expected: expectation.sourceSlide,
          actual: entry.sourceSlide,
        },
      )
    }
    if (entry && !sourcePptxMatches) {
      addIssue(
        report,
        'blockers',
        'slide-copy-source-pptx-mismatch',
        `slide-copy donor PPTX does not match contract target ${target.id}`,
      )
    }
    if (entry && !structuralEvidenceValid) {
      addIssue(
        report,
        'blockers',
        'slide-copy-structural-evidence-invalid',
        `slide-copy part/dependency mapping is incomplete for contract target ${target.id}`,
      )
    }
  }

  const coveredCount = coverage.filter((item) => item.covered).length
  if (
    contract.coverage?.required !== false &&
    coveredCount !== contract.coverage.expectedTargetCount
  ) {
    addIssue(
      report,
      'blockers',
      'target-coverage-incomplete',
      `slide-copy evidence covered ${coveredCount} of ${contract.coverage.expectedTargetCount} required target(s)`,
      { coverage },
    )
  }
  if (coverage.some((item) => item.unexpectedCategories.length > 0)) {
    addIssue(
      report,
      'blockers',
      'dry-run-change-category-outside-contract',
      'slide-copy reported a structural change not allowed by the contract',
    )
  }
  return { coverage, coveredCount, coveredIdentities }
}

function reliableShapeChanges(diff) {
  const changes = []
  for (const slide of diff?.slides ?? []) {
    for (const shape of slide?.shapeChanges ?? []) {
      if (shape?.reliability !== 'reliable' || shape?.conclusion === 'unchanged') continue
      changes.push({ slide: slide.index, shape })
    }
  }
  return changes
}

function diffIdentity(item) {
  const { source, candidate } = diffShapeSides(item.shape)
  const shape = candidate ?? source ?? {}
  return { slide: item.slide, id: shape.id ?? null, name: shape.name ?? null }
}

function diffShapeSides(shape) {
  return {
    source: shape?.baseline ?? shape?.source,
    candidate: shape?.target ?? shape?.candidate,
  }
}

function diffSlideCounts(diff) {
  return {
    source: diff?.summary?.baselineSlideCount ?? diff?.summary?.sourceSlideCount,
    candidate: diff?.summary?.targetSlideCount ?? diff?.summary?.candidateSlideCount,
  }
}

function diffCategories(item) {
  const nested = (item.shape?.changes ?? [])
    .filter((change) => change?.reliability === 'reliable')
    .map((change) => String(change?.category ?? ''))
    .filter(Boolean)
  if (nested.length > 0) return [...new Set(nested)]
  return [...new Set((item.shape?.categories ?? [item.shape?.category]).filter(Boolean))]
}

function checkDiff(contract, diff, coverageResult, report) {
  const counts = diffSlideCounts(diff)
  const coveredIdentities = coverageResult.coveredIdentities
  const outOfScope = []
  const disallowed = []
  const changes = reliableShapeChanges(diff)
  const fontTarget = documentFontTarget(contract)
  if (
    fontTarget &&
    (counts.source !== fontTarget.slideCount || counts.candidate !== fontTarget.slideCount)
  ) {
    addIssue(
      report,
      'blockers',
      'font-slide-count-mismatch',
      'document font scope must cover every source and candidate slide',
    )
  }
  for (const item of changes) {
    const identity = diffIdentity(item)
    const categories = diffCategories(item)
    const structuralSlideMatch =
      contract.scope === 'structural' &&
      contract.expectedStructure?.changedSlides?.includes(item.slide)
    const targetMatch =
      Boolean(fontTarget) ||
      structuralSlideMatch ||
      coveredIdentities.some((target) => sameIdentity(identity, target))
    if (!targetMatch) outOfScope.push({ identity, categories })
    const outsideCategories = categories.filter(
      (category) => !contract.allowedChanges.includes(category),
    )
    if (outsideCategories.length > 0) disallowed.push({ identity, categories: outsideCategories })
  }
  if (
    contract.preserve.includes('slide-count') &&
    (counts.source !== counts.candidate ||
      Number(diff?.summary?.slideAdded ?? 0) !== 0 ||
      Number(diff?.summary?.slideRemoved ?? 0) !== 0)
  ) {
    addIssue(
      report,
      'blockers',
      'slide-count-changed',
      'semantic diff reports a slide-count change',
    )
  }
  if (outOfScope.length > 0) {
    addIssue(
      report,
      'blockers',
      'reliable-change-outside-contract',
      `${outOfScope.length} reliable shape change(s) fall outside the resolved contract targets`,
      { changes: outOfScope },
    )
  }
  if (disallowed.length > 0) {
    addIssue(
      report,
      'blockers',
      'reliable-change-category-outside-contract',
      `${disallowed.length} reliable shape change(s) use categories not allowed by the contract`,
      { changes: disallowed },
    )
  }
  for (const target of contract.targets) {
    const targetCoverageItem = coverageResult.coverage.find((item) => item.id === target.id)
    const expectedIdentities =
      targetCoverageItem?.resolvedIdentities?.length > 0
        ? targetCoverageItem.resolvedIdentities
        : [selectorIdentity(target)]
    const change = changes.find((item) =>
      expectedIdentities.some((identity) => sameIdentity(diffIdentity(item), identity)),
    )
    if (target.expected?.alreadyCompliant === true && !change) continue
    const sides = diffShapeSides(change?.shape)
    const textChange = change?.shape?.changes?.find(
      (item) => item.field === 'textPreview' && item.reliability === 'reliable',
    )
    const before = sides.source?.textPreview ?? textChange?.before
    const after = sides.candidate?.textPreview ?? textChange?.after
    if (target.expected?.beforeText !== undefined && before !== target.expected.beforeText) {
      addIssue(
        report,
        'blockers',
        'expected-before-not-observed',
        `semantic diff source text does not match contract target ${target.id}`,
        { targetId: target.id, expected: target.expected.beforeText, actual: before ?? null },
      )
    }
    if (target.expected?.afterText !== undefined && after !== target.expected.afterText) {
      addIssue(
        report,
        'blockers',
        'expected-final-change-not-observed',
        `semantic diff candidate text does not match contract target ${target.id}`,
        { targetId: target.id, expected: target.expected.afterText, actual: after ?? null },
      )
    }
  }
  const uncertain = Number(diff?.summary?.uncertainChanges ?? 0)
  const unsupported = Number(diff?.summary?.unsupportedRegions ?? 0)
  if (uncertain > 0 || unsupported > 0) {
    addIssue(
      report,
      'attention',
      'semantic-diff-review-signals',
      'semantic diff contains uncertain or unsupported regions; scoped visual evidence remains required',
      { uncertainChanges: uncertain, unsupportedRegions: unsupported },
    )
  }
  return { reliableChanges: changes, outOfScope, disallowed }
}

function checkDeclaredOps(contract, dryRun, report) {
  const declared = new Set(contract.targets.flatMap((target) => target.opIndexes ?? []))
  const extra = (dryRun?.opResults ?? [])
    .map((item) => item?.opIndex)
    .filter((opIndex) => Number.isInteger(opIndex) && !declared.has(opIndex))
  if (extra.length > 0) {
    addIssue(
      report,
      'blockers',
      'dry-run-op-outside-contract',
      'dry-run contains patch operations that are not owned by any contract target',
      { opIndexes: [...new Set(extra)] },
    )
  }
}

function changedSlides(diff) {
  return [
    ...new Set(
      (diff?.slides ?? [])
        .filter((slide) => slide?.conclusion !== 'unchanged')
        .map((slide) => slide.index),
    ),
  ].sort((a, b) => a - b)
}

function checkExpectedStructure(contract, diff, report) {
  const expected = contract.expectedStructure
  if (!expected) return
  const counts = diffSlideCounts(diff)
  const actualDelta = counts.candidate - counts.source
  const actualSlides = changedSlides(diff)
  const expectedSlides = [...expected.changedSlides].sort((a, b) => a - b)
  if (actualDelta !== expected.slideCountDelta) {
    addIssue(
      report,
      'blockers',
      'structural-slide-delta-mismatch',
      'semantic diff slide-count delta does not match the structural contract',
      { expected: expected.slideCountDelta, actual: actualDelta },
    )
  }
  if (JSON.stringify(actualSlides) !== JSON.stringify(expectedSlides)) {
    addIssue(
      report,
      'blockers',
      'structural-changed-slides-mismatch',
      'semantic diff changed slides do not match the structural contract',
      { expected: expectedSlides, actual: actualSlides },
    )
  }
  if (expected.objectTypes.length > 0) {
    const actualTypes = new Set(
      reliableShapeChanges(diff)
        .flatMap((item) => {
          const sides = diffShapeSides(item.shape)
          return [sides.source?.shapeType, sides.candidate?.shapeType]
        })
        .filter(Boolean),
    )
    const unexpected = [...actualTypes].filter((type) => !expected.objectTypes.includes(type))
    if (unexpected.length > 0) {
      addIssue(
        report,
        'blockers',
        'structural-object-type-outside-contract',
        'semantic diff contains object types outside the structural contract',
        { objectTypes: unexpected },
      )
    }
  }
}

function findInspectedShape(inspect, target) {
  const slide = (inspect?.slides ?? []).find((item) => item?.index === target.slide)
  const identity = selectorIdentity(target)
  const matches = (slide?.shapes ?? []).filter((shape) =>
    identity.id !== null
      ? shape?.id === identity.id
      : identity.name && shape?.name === identity.name,
  )
  return matches.length === 1 ? matches[0] : null
}

function checkAlreadyCompliant(contract, finalInspect, report) {
  for (const target of contract.targets.filter(
    (item) => item.expected?.alreadyCompliant === true,
  )) {
    const shape = findInspectedShape(finalInspect, target)
    const actual = shape?.textPreview ?? shape?.text
    if (!shape || actual !== target.expected.afterText) {
      addIssue(
        report,
        'blockers',
        'already-compliant-value-not-observed',
        `final inspect does not prove the declared already-compliant value for ${target.id}`,
        { targetId: target.id, expected: target.expected.afterText, actual: actual ?? null },
      )
    }
  }
}

function targetSlides1Based(contract) {
  return [
    ...new Set(
      contract.targets.flatMap((target) =>
        target.kind === 'document-fonts'
          ? Array.from({ length: target.slideCount }, (_, index) => index + 1)
          : [target.slide + 1],
      ),
    ),
  ].sort((a, b) => a - b)
}

function containsAll(actual, expected) {
  const values = new Set((actual ?? []).map(Number))
  return expected.every((item) => values.has(item))
}

function reportedPath(value, workspace) {
  const raw = typeof value === 'string' ? value : value?.path
  if (!raw) return ''
  return resolve(workspace || '.', raw)
}

function evidenceBindings(kind, evidence) {
  if (kind === 'dry-run') {
    if (evidence?.schemaVersion === COPY_FROM_SCHEMA_VERSION) {
      return {
        source: evidence?.input,
        candidate: evidence?.candidate ?? evidence?.output ?? evidence?.wouldWrite,
      }
    }
    return { source: evidence?.input, candidate: evidence?.wouldWrite }
  }
  if (kind === 'semantic-diff') {
    return {
      source: evidence?.baselinePath ?? evidence?.source,
      candidate: evidence?.targetPath ?? evidence?.candidate,
    }
  }
  if (kind === 'style-diff' || kind === 'vision-diff') {
    return { source: evidence?.source, candidate: evidence?.candidate }
  }
  if (kind === 'png-preview') return { candidate: evidence?.input }
  if (kind === 'vision-check' || kind === 'final-inspect') return { candidate: evidence?.input }
  return {}
}

function evidencePath(args, kind) {
  return {
    'dry-run': args.dryRun,
    'copy-size-gate': args.copySizeGate,
    'semantic-diff': args.diff,
    'style-diff': args.styleDiff,
    'png-preview': args.preview,
    'vision-check': args.vision,
    'vision-diff': args.visionDiff,
    'final-inspect': args.finalInspect,
    'structure-check': args.structureCheck,
  }[kind]
}

function checkEvidenceBindings(contract, args, loaded, report) {
  const workspace = contract.workspace || dirname(args.contract)
  const source = resolve(contract.source.pptx)
  const candidate = args.candidate
  for (const [kind, evidence] of Object.entries(loaded)) {
    const bindings = evidenceBindings(kind, evidence)
    if (bindings.source) {
      const actual = reportedPath(bindings.source, workspace)
      if (actual !== source) {
        addIssue(
          report,
          'blockers',
          'evidence-source-mismatch',
          `${kind} evidence was generated from a different source PPTX`,
          { kind, expected: source, actual },
        )
      }
    }
    if (bindings.candidate) {
      const actual = reportedPath(bindings.candidate, workspace)
      if (actual !== candidate) {
        addIssue(
          report,
          'blockers',
          'evidence-candidate-mismatch',
          `${kind} evidence was generated for a different candidate PPTX`,
          { kind, expected: candidate, actual },
        )
      }
    }
    const artifactPath = evidencePath(args, kind)
    if (
      kind !== 'dry-run' &&
      kind !== 'copy-size-gate' &&
      artifactPath &&
      statSync(artifactPath).mtimeMs < statSync(candidate).mtimeMs
    ) {
      addIssue(
        report,
        'blockers',
        'evidence-candidate-stale',
        `${kind} evidence is older than the current candidate bytes`,
        { kind },
      )
    }
  }
}

function checkEvidence(contract, args, report) {
  const expectedSlides = targetSlides1Based(contract)
  const loaded = {}
  for (const kind of contract.requiredEvidence) {
    const path = evidencePath(args, kind)
    if (!path || !existsSync(path)) {
      addIssue(
        report,
        'blockers',
        kind === 'copy-size-gate' ? 'copy-size-gate-missing' : 'required-evidence-missing',
        `required ${kind} evidence is missing`,
        {
          kind,
          path: path ?? null,
        },
      )
      continue
    }
    loaded[kind] = readJson(path, `${kind} evidence`)
  }

  const dryRun = loaded['dry-run']
  if (dryRun && !['pptx-dry-run/v1', COPY_FROM_SCHEMA_VERSION].includes(dryRun.schemaVersion)) {
    addIssue(report, 'blockers', 'dry-run-not-successful', 'dry-run evidence is not successful')
  } else if (
    dryRun?.status !== undefined &&
    dryRun.status !== (dryRun.schemaVersion === COPY_FROM_SCHEMA_VERSION ? 'ready' : 'success')
  ) {
    addIssue(report, 'blockers', 'dry-run-not-successful', 'dry-run evidence is not successful')
  } else if (dryRun?.schemaVersion === 'pptx-dry-run/v1' && !Array.isArray(dryRun.semanticIssues)) {
    addIssue(
      report,
      'blockers',
      'dry-run-semantic-evidence-missing',
      'dry-run semanticIssues evidence is missing or malformed',
    )
  } else if (dryRun?.schemaVersion === 'pptx-dry-run/v1' && dryRun.semanticIssues.length > 0) {
    addIssue(
      report,
      'blockers',
      'dry-run-semantic-regression',
      'dry-run introduced semantic regressions',
      { semanticIssueCount: dryRun.semanticIssues.length },
    )
  } else if (dryRun?.schemaVersion === COPY_FROM_SCHEMA_VERSION) {
    const structurallyComplete =
      Array.isArray(dryRun.copied) &&
      dryRun.copied.length > 0 &&
      Array.isArray(dryRun.changedParts) &&
      Array.isArray(dryRun.dependencyMappings) &&
      dryRun.dryRun === true
    if (!structurallyComplete) {
      addIssue(
        report,
        'blockers',
        'slide-copy-structural-evidence-invalid',
        'slide-copy evidence is missing copied[], changedParts[], or dependencyMappings[]',
      )
    } else {
      checkCopyFromPreflight(contract, dryRun, report)
      const sizeGate = loaded['copy-size-gate']
      if (sizeGate) checkCopySizeGate(contract, dryRun, sizeGate, report)
      addCheck(report, 'slide-copy-structural-evidence', 'pass', {
        copiedSlides: dryRun.copied.length,
        dependencyMappings: dryRun.dependencyMappings.length,
      })
    }
  }
  const diff = loaded['semantic-diff']
  if (diff && (diff.schemaVersion !== 'pptx-diff/v1' || diff.status !== 'success')) {
    addIssue(
      report,
      'blockers',
      'semantic-diff-not-successful',
      'semantic diff evidence is not successful',
    )
  }
  if (diff) {
    if (diff.detail === 'summary') {
      addIssue(
        report,
        'blockers',
        'semantic-diff-detail-insufficient',
        'Edit Contract requires --detail full for per-object identity and field-level evidence',
      )
    }
    const counts = diffSlideCounts(diff)
    if (
      !Number.isInteger(counts.source) ||
      counts.source < 0 ||
      !Number.isInteger(counts.candidate) ||
      counts.candidate < 0
    ) {
      addIssue(
        report,
        'blockers',
        'semantic-diff-slide-counts-missing',
        'semantic diff must disclose valid source and candidate slide counts',
      )
    }
  }
  const styleDiff = loaded['style-diff']
  if (styleDiff) {
    const stylePassed =
      styleDiff.schemaVersion === 'pptx-i18n-style-diff/v1' &&
      styleDiff.status === 'pass' &&
      styleDiff.agentGate?.passed === true &&
      Number(styleDiff.agentGate?.styleBlockerCount ?? styleDiff.styleBlockers?.length ?? 0) === 0
    if (!stylePassed) {
      addIssue(
        report,
        'blockers',
        'target-text-style-changed',
        'text edit changed the target OOXML style signature; use a run/text-node preserving edit path',
        {
          styleBlockerCount: Number(
            styleDiff.agentGate?.styleBlockerCount ?? styleDiff.styleBlockers?.length ?? 0,
          ),
        },
      )
    }
  }
  const preview = loaded['png-preview']
  if (preview) {
    const selected =
      preview.slidesSelected ?? preview.pages?.map((page) => page.slide ?? page.index)
    const pagesHealthy = (preview.pages ?? []).every(
      (page) =>
        (page.file?.status ?? page.status) === 'ok' && Number(page.file?.byteLength ?? 1) > 0,
    )
    if (preview.schemaVersion !== 'pptx-preview/v1' || preview.status !== 'success') {
      addIssue(
        report,
        'blockers',
        'preview-not-successful',
        'PNG preview evidence is not successful',
      )
    } else if (!containsAll(selected, expectedSlides) || !pagesHealthy) {
      addIssue(
        report,
        'blockers',
        'preview-scope-incomplete',
        'PNG preview does not cover every contract target slide with a healthy page artifact',
        { expectedSlides, selectedSlides: selected ?? [] },
      )
    }
  }
  const vision = loaded['vision-check']
  if (vision) {
    const selected = vision.scope?.slides
    if (vision.schemaVersion !== 'pptx-vision/v1' || vision.status !== 'success') {
      addIssue(
        report,
        'blockers',
        'vision-not-successful',
        'vision-check evidence is not successful',
      )
    } else if (!containsAll(selected, expectedSlides)) {
      addIssue(
        report,
        'blockers',
        'vision-scope-incomplete',
        'vision-check does not cover every contract target slide',
        { expectedSlides, selectedSlides: selected ?? [] },
      )
    }
  }
  const visionDiff = loaded['vision-diff']
  if (visionDiff) {
    // Full-deck reports intentionally omit scope.slides. Only the explicit
    // runtime mode plus valid source/candidate counts prove that wider scope.
    const fullDeck =
      visionDiff.agentGate?.scopeMode === 'full-deck' &&
      [visionDiff.slideCount?.source, visionDiff.slideCount?.candidate].every(
        (count) => Number.isSafeInteger(count) && count >= 0,
      )
    const selected =
      visionDiff.scope?.slides ??
      (fullDeck
        ? Array.from(
            { length: Math.max(visionDiff.slideCount.source, visionDiff.slideCount.candidate) },
            (_, index) => index + 1,
          )
        : undefined)
    const newHigh = Number(
      visionDiff.agentGate?.newHighIssues ?? visionDiff.summary?.byClass?.new?.high ?? 0,
    )
    const newMedium = Number(
      visionDiff.agentGate?.newMediumIssues ?? visionDiff.summary?.byClass?.new?.medium ?? 0,
    )
    const worsenedHigh = Number(
      visionDiff.agentGate?.worsenedHighIssues ?? visionDiff.summary?.byClass?.worsened?.high ?? 0,
    )
    const worsenedMedium = Number(
      visionDiff.agentGate?.worsenedMediumIssues ??
        visionDiff.summary?.byClass?.worsened?.medium ??
        0,
    )
    if (visionDiff.schemaVersion !== 'pptx-vision-diff/v1' || visionDiff.status !== 'success') {
      addIssue(
        report,
        'blockers',
        'vision-diff-not-successful',
        'vision-diff evidence is not successful',
      )
    } else if (!containsAll(selected, expectedSlides)) {
      addIssue(
        report,
        'blockers',
        'vision-diff-scope-incomplete',
        'vision-diff does not cover every contract target slide',
        { expectedSlides, selectedSlides: selected ?? [] },
      )
    } else if (
      visionDiff.agentGate?.passed !== true ||
      newHigh > 0 ||
      newMedium > 0 ||
      worsenedHigh > 0 ||
      worsenedMedium > 0
    ) {
      addIssue(
        report,
        'blockers',
        'vision-diff-new-regression',
        'candidate introduces or worsens high/medium visual issues on the changed scope',
        { newHigh, newMedium, worsenedHigh, worsenedMedium },
      )
    }
  }
  const finalInspect = loaded['final-inspect']
  if (finalInspect && finalInspect.status !== 'success') {
    addIssue(
      report,
      'blockers',
      'final-inspect-not-successful',
      'final inspect evidence is not successful',
    )
  }
  if (finalInspect?.status === 'success') checkAlreadyCompliant(contract, finalInspect, report)
  const fontTarget = documentFontTarget(contract)
  if (
    fontTarget &&
    (finalInspect?.schemaVersion !== 'pptx-inspect/v1' ||
      finalInspect.slides?.length !== fontTarget.slideCount ||
      !containsAll(
        finalInspect.slides.map((slide) => slide.index + 1),
        expectedSlides,
      ))
  ) {
    addIssue(
      report,
      'blockers',
      'font-inspect-scope-incomplete',
      'final inspect must cover every document font target slide',
    )
  }
  const structure = loaded['structure-check']
  if (structure && structure.status !== 'pass') {
    addIssue(
      report,
      'blockers',
      'structure-check-not-passing',
      'structure check evidence did not pass',
    )
  }
  return loaded
}

function nextAction(report) {
  const codes = new Set(report.blockers.map((item) => item.code))
  if (codes.has('source-hash-stale') || codes.has('source-missing')) return 'refresh-inspect'
  if (codes.has('session-rules-binding-stale')) return 'refresh-session-rules-resolution'
  if (
    codes.has('session-rule-postcondition-failed') ||
    codes.has('session-rule-candidate-inspection-failed')
  ) {
    return 'apply-session-rules'
  }
  if (codes.has('semantic-diff-detail-insufficient')) return 'collect-full-semantic-diff'
  if (codes.has('expected-before-not-observed')) return 'refresh-inspect'
  if (codes.has('already-compliant-value-not-observed')) return 'complete-missing-coverage'
  if (codes.has('evidence-source-mismatch') || codes.has('evidence-candidate-mismatch')) {
    return 'regenerate-current-candidate-evidence'
  }
  if (
    codes.has('evidence-manifest-candidate-mismatch') ||
    codes.has('evidence-manifest-artifact-mismatch') ||
    codes.has('evidence-manifest-invalid')
  ) {
    return 'regenerate-current-candidate-evidence'
  }
  if (codes.has('evidence-candidate-stale')) return 'regenerate-current-candidate-evidence'
  if (
    codes.has('semantic-diff-not-successful') ||
    codes.has('semantic-diff-slide-counts-missing')
  ) {
    return 'regenerate-current-candidate-evidence'
  }
  if (codes.has('dry-run-not-successful')) return 'retry-dry-run-with-fix-patch'
  if (codes.has('copy-size-gate-missing')) return 'run-copy-size-gate'
  if (codes.has('copy-size-gate-failed')) return 'choose-explicit-slide-size-strategy'
  if (codes.has('copy-size-gate-stale')) return 'refresh-slide-copy-preflight'
  if (codes.has('target-text-style-changed')) return 'retry-with-style-preserving-text-edit'
  if (codes.has('vision-diff-new-regression')) return 'repair-new-visual-regressions'
  if (codes.has('selector-resolution-missing')) return 'rebind-selectors'
  if (
    codes.has('target-coverage-incomplete') ||
    codes.has('expected-after-not-observed') ||
    codes.has('expected-final-change-not-observed')
  ) {
    return 'complete-missing-coverage'
  }
  if (
    codes.has('reliable-change-outside-contract') ||
    codes.has('reliable-change-category-outside-contract') ||
    codes.has('slide-count-changed') ||
    codes.has('dry-run-op-outside-contract') ||
    codes.has('structural-slide-delta-mismatch') ||
    codes.has('structural-changed-slides-mismatch') ||
    codes.has('structural-object-type-outside-contract')
  ) {
    return 'review-out-of-scope-changes'
  }
  if (
    codes.has('required-evidence-missing') ||
    codes.has('preview-scope-incomplete') ||
    codes.has('vision-scope-incomplete') ||
    codes.has('vision-diff-scope-incomplete') ||
    codes.has('preview-not-successful') ||
    codes.has('vision-not-successful') ||
    codes.has('vision-diff-not-successful')
  ) {
    return 'verify-changed-scope'
  }
  if (codes.has('structure-check-not-passing')) return 'run-structure-audit'
  if (report.blockers.length > 0) return 'block-and-request-user-decision'
  return 'publish'
}

function buildReport(args) {
  const contract = readJson(args.contract, 'contract')
  if (contract.schemaVersion !== CONTRACT_SCHEMA_VERSION) {
    throw new Error(`contract schemaVersion must be ${CONTRACT_SCHEMA_VERSION}`)
  }
  if (!Array.isArray(contract.targets) || contract.targets.length === 0) {
    throw new Error('contract must contain targets[]')
  }
  validateFontContract(contract)
  if (contract.targets.some((target) => !hasStableIdentity(target))) {
    throw new Error('every object target must contain a stable resolvedIdentity id/name')
  }
  if (
    contract.targets.some((target) => target.kind === 'slide') &&
    contract.scope !== 'structural'
  ) {
    throw new Error('slide targets are only valid for structural scope')
  }
  if (!Array.isArray(contract.allowedChanges) || !Array.isArray(contract.preserve)) {
    throw new Error('contract allowedChanges/preserve arrays are required')
  }
  const report = {
    schemaVersion: SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    status: 'pass',
    contract: args.contract,
    candidate: {
      pptx: args.candidate,
      sha256: sha256(args.candidate),
      byteLength: readFileSync(args.candidate).length,
    },
    source: contract.source ?? null,
    artifacts: {
      dryRun: args.dryRun,
      copySizeGate: args.copySizeGate,
      semanticDiff: args.diff,
      styleDiff: args.styleDiff,
      preview: args.preview,
      vision: args.vision,
      visionDiff: args.visionDiff,
      evidenceManifest: args.evidenceManifest,
      finalInspect: args.finalInspect,
      structureCheck: args.structureCheck,
    },
    checks: [],
    targetCoverage: [],
    reliableChanges: [],
    blockers: [],
    attention: [],
    sessionRuleResults: [],
    summary: {
      targetCount: contract.targets.length,
      expectedTargetCount: contract.coverage?.expectedTargetCount ?? contract.targets.length,
      coveredTargetCount: 0,
      reliableShapeChangeCount: 0,
      outOfScopeReliableChangeCount: 0,
      blockerCount: 0,
      attentionCount: 0,
    },
  }

  const sourcePath = contract.source?.pptx ? resolve(contract.source.pptx) : ''
  const sessionResolution = checkSessionRulesBinding(contract, report)
  if (!sourcePath || !existsSync(sourcePath)) {
    addIssue(report, 'blockers', 'source-missing', 'contract source PPTX is missing', {
      path: sourcePath || null,
    })
    addCheck(report, 'source-freshness', 'fail')
  } else {
    const currentHash = sha256(sourcePath)
    const fresh = currentHash === contract.source?.sha256
    addCheck(report, 'source-freshness', fresh ? 'pass' : 'fail', {
      expectedSha256: contract.source?.sha256 ?? null,
      actualSha256: currentHash,
    })
    if (!fresh) {
      addIssue(
        report,
        'blockers',
        'source-hash-stale',
        'source PPTX changed after the edit contract was created; refresh inspect/select and rebuild the contract',
      )
    }
  }

  const evidence = checkEvidence(contract, args, report)
  checkEvidenceManifest(args, evidence, report)
  checkEvidenceBindings(contract, args, evidence, report)
  checkSessionRulePostconditions(
    contract,
    args,
    sessionResolution,
    evidence['final-inspect'],
    report,
  )
  const dryRun = evidence['dry-run']
  let coverageResult = { coverage: [], coveredCount: 0, coveredIdentities: [] }
  if (dryRun?.schemaVersion === 'pptx-dry-run/v1' && dryRun.status === 'success') {
    checkDeclaredOps(contract, dryRun, report)
    try {
      if (!Array.isArray(dryRun.opResults)) throw new TypeError('opResults must be an array')
      for (const result of dryRun.opResults) readResolvedSelectors(result)
      coverageResult = targetCoverage(contract, dryRun, report)
    } catch (error) {
      addIssue(report, 'blockers', 'dry-run-selector-evidence-invalid', error.message)
    }
    report.targetCoverage = coverageResult.coverage
    addCheck(
      report,
      'target-coverage',
      coverageResult.coveredCount === report.summary.expectedTargetCount ? 'pass' : 'fail',
      { covered: coverageResult.coveredCount, expected: report.summary.expectedTargetCount },
    )
  } else if (dryRun?.schemaVersion === COPY_FROM_SCHEMA_VERSION && dryRun.status === 'ready') {
    coverageResult = copyFromCoverage(contract, dryRun, report)
    report.targetCoverage = coverageResult.coverage
    addCheck(
      report,
      'target-coverage',
      coverageResult.coveredCount === report.summary.expectedTargetCount ? 'pass' : 'fail',
      {
        evidence: COPY_FROM_SCHEMA_VERSION,
        covered: coverageResult.coveredCount,
        expected: report.summary.expectedTargetCount,
      },
    )
  }

  const diff = evidence['semantic-diff']
  if (diff?.schemaVersion === 'pptx-diff/v1' && diff.status === 'success') {
    checkExpectedStructure(contract, diff, report)
    const diffResult = checkDiff(contract, diff, coverageResult, report)
    report.reliableChanges = diffResult.reliableChanges
    report.summary.reliableShapeChangeCount = diffResult.reliableChanges.length
    report.summary.outOfScopeReliableChangeCount = diffResult.outOfScope.length
    addCheck(
      report,
      'semantic-diff-locality',
      diffResult.outOfScope.length === 0 ? 'pass' : 'fail',
      {
        reliableShapeChanges: diffResult.reliableChanges.length,
        outOfScope: diffResult.outOfScope.length,
      },
    )
  }

  report.summary.coveredTargetCount = coverageResult.coveredCount
  report.summary.blockerCount = report.blockers.length
  report.summary.attentionCount = report.attention.length
  report.status = report.blockers.length === 0 ? 'pass' : 'fail'
  report.agentGate = {
    schemaVersion: 'pptx-nova-agent-gate/v1',
    passed: report.status === 'pass',
    canContinue: report.status === 'pass',
    nextAction: nextAction(report),
    scope: targetSlides1Based(contract).join(','),
    blockerCount: report.blockers.length,
    attentionCount: report.attention.length,
    message:
      report.status === 'pass'
        ? `Edit contract passed for ${coverageResult.coveredCount} target(s); required evidence covers the changed scope.`
        : `Edit contract failed with ${report.blockers.length} blocker(s); next action: ${nextAction(report)}.`,
  }
  return report
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const report = buildReport(args)
  writeFileSync(args.output, `${JSON.stringify(report, null, 2)}\n`)
  if (args.json) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
  else {
    process.stdout.write(`Edit contract gate: ${report.status}\n`)
    process.stdout.write(`${report.agentGate.message}\n`)
  }
  if (args.strict && report.status !== 'pass') process.exit(2)
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exit(1)
}
