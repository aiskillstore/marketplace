#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const REPORT_SCHEMA = 'pptx-nova-i18n-review-classification/v1'
const DECISIONS_SCHEMA = 'pptx-nova-i18n-review-decisions/v1'
const REVIEWABLE_CATEGORIES = new Set(['visibleBody', 'visibleTextAttr', 'chartVisibleCache'])

function parseArgs(argv) {
  const args = {
    scan: '',
    decisions: '',
    output: '',
    report: '',
    overwrite: false,
    json: false,
    jsonFull: false,
  }
  const values = {
    '--scan': 'scan',
    '--decisions': 'decisions',
    '--output': 'output',
    '--report': 'report',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else if (arg === '--json-full') {
      args.json = true
      args.jsonFull = true
    } else if (arg === '--help' || arg === '-h') {
      process.stdout.write(
        'Usage: node cli/translation/classify-review-units.mjs --scan scan.json --decisions decisions.json --output classified-scan.json [--report report.json] [--overwrite] [--json|--json-full]\n',
      )
      process.exit(0)
    } else if (values[arg]) {
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
      args[values[arg]] = resolve(value)
      index += 1
    } else throw new Error(`Unknown option: ${arg}`)
  }
  for (const key of ['scan', 'decisions', 'output'])
    if (!args[key]) throw new Error(`--${key} is required`)
  return args
}

function readJson(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  return JSON.parse(readFileSync(path, 'utf8'))
}

function digest(path) {
  return `sha256:${createHash('sha256').update(readFileSync(path)).digest('hex')}`
}

function write(path, value, overwrite) {
  if (existsSync(path) && !overwrite) throw new Error(`Output already exists: ${path}`)
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function isLanguageReviewUnit(unit) {
  return (
    unit?.action === 'review' &&
    unit?.requiresReview === true &&
    REVIEWABLE_CATEGORIES.has(unit?.category) &&
    Array.isArray(unit?.notes) &&
    unit.notes.includes('language-classification-uncertain')
  )
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const scan = readJson(args.scan, 'scan')
  const decisionsDoc = readJson(args.decisions, 'decisions')
  if (scan.schemaVersion !== 'pptx-i18n-scan/v1') throw new Error('scan must use pptx-i18n-scan/v1')
  if (decisionsDoc.schemaVersion !== DECISIONS_SCHEMA)
    throw new Error(`decisions must use ${DECISIONS_SCHEMA}`)
  const scanHash = digest(args.scan)
  if (decisionsDoc.scanSha256 !== scanHash)
    throw new Error('decisions scanSha256 does not match the scan artifact')
  const units = scan?.i18nUnits?.units
  if (!Array.isArray(units)) throw new Error('scan is missing i18nUnits.units[]')
  const reviewUnits = units.filter(isLanguageReviewUnit)
  const decisions = new Map()
  for (const decision of decisionsDoc.decisions ?? []) {
    if (!decision?.unitId || decisions.has(decision.unitId))
      throw new Error('decisions contain a missing or duplicate unitId')
    if (!['translate', 'preserve'].includes(decision.decision))
      throw new Error(`invalid decision for ${decision.unitId}`)
    if (!String(decision.reason ?? '').trim())
      throw new Error(`decision reason is required for ${decision.unitId}`)
    decisions.set(decision.unitId, decision)
  }
  const byTextInput = decisionsDoc.byText ?? []
  if (!Array.isArray(byTextInput)) throw new Error('byText must be an array of grouped decisions')
  const byText = new Map()
  for (const rule of byTextInput) {
    if (typeof rule?.sourceText !== 'string' || rule.sourceText.length === 0)
      throw new Error('byText rules require a non-empty sourceText')
    if (byText.has(rule.sourceText))
      throw new Error(
        `byText rules contain a duplicate sourceText: ${JSON.stringify(rule.sourceText)}`,
      )
    if (!['translate', 'preserve'].includes(rule.decision))
      throw new Error(`invalid byText decision for ${JSON.stringify(rule.sourceText)}`)
    if (!String(rule.reason ?? '').trim())
      throw new Error(`byText decision reason is required for ${JSON.stringify(rule.sourceText)}`)
    byText.set(rule.sourceText, rule)
  }
  const reviewTexts = new Set(reviewUnits.map((unit) => unit.sourceText))
  const unmatchedByText = [...byText.keys()]
    .filter((sourceText) => !reviewTexts.has(sourceText))
    .map((sourceText) => JSON.stringify(sourceText))
  if (unmatchedByText.length > 0)
    throw new Error(`byText rules match no language-review units: ${unmatchedByText.join(', ')}`)
  const classified = structuredClone(scan)
  const applied = []
  for (let index = 0; index < units.length; index += 1) {
    const unit = units[index]
    if (!isLanguageReviewUnit(unit)) continue
    const rule = byText.get(unit.sourceText)
    const ruleHash = rule?.sourceHash ?? null
    if (rule && ruleHash !== null && ruleHash !== unit.sourceHash)
      throw new Error(
        `byText sourceHash mismatch for ${JSON.stringify(unit.sourceText)} at ${unit.unitId}`,
      )
    const unitDecision = decisions.get(unit.unitId)
    const decision = unitDecision ?? rule
    if (!decision) throw new Error(`missing language classification for ${unit.unitId}`)
    if (unitDecision && unitDecision.sourceHash !== unit.sourceHash)
      throw new Error(`sourceHash mismatch for ${unit.unitId}`)
    const target = classified.i18nUnits.units[index]
    target.action = decision.decision
    target.requiresReview = false
    target.reason = decision.reason
    target.notes = [...new Set([...(unit.notes ?? []), `classified-${decision.decision}`])]
    applied.push({
      unitId: unit.unitId,
      category: unit.category,
      sourceText: unit.sourceText,
      decision: decision.decision,
      reason: decision.reason,
      decisionSource: unitDecision ? 'unit' : 'byText',
    })
    decisions.delete(unit.unitId)
  }
  if (decisions.size > 0)
    throw new Error(
      `decisions reference unknown or non-language-review units: ${[...decisions.keys()].join(', ')}`,
    )
  write(args.output, classified, args.overwrite)
  const report = {
    schemaVersion: REPORT_SCHEMA,
    status: 'pass',
    scan: args.scan,
    scanSha256: scanHash,
    decisions: args.decisions,
    output: args.output,
    summary: {
      reviewUnitCount: reviewUnits.length,
      translateCount: applied.filter((item) => item.decision === 'translate').length,
      preserveCount: applied.filter((item) => item.decision === 'preserve').length,
      byTextRuleCount: byText.size,
      byTextDecidedCount: applied.filter((item) => item.decisionSource === 'byText').length,
      unitDecidedCount: applied.filter((item) => item.decisionSource === 'unit').length,
      byCategory: Object.fromEntries(
        [...REVIEWABLE_CATEGORIES].map((category) => [
          category,
          applied.filter((item) => item.category === category).length,
        ]),
      ),
    },
    applied,
    agentGate: { passed: true, status: 'pass', unclassifiedCount: 0 },
  }
  if (args.report) write(args.report, report, args.overwrite)
  const compact = {
    schemaVersion: 'pptx-nova-i18n-review-classification-result/v1',
    status: report.status,
    report: args.report || null,
    output: args.output,
    summary: report.summary,
    agentGate: report.agentGate,
  }
  if (args.json) {
    process.stdout.write(`${JSON.stringify(args.jsonFull ? report : compact, null, 2)}\n`)
  } else if (!args.report) {
    process.stdout.write(
      `Classified ${report.summary.reviewUnitCount} review units (${report.summary.translateCount} translate, ${report.summary.preserveCount} preserve)\n`,
    )
  }
}

try {
  main()
} catch (error) {
  process.stderr.write(
    `${JSON.stringify({ schemaVersion: REPORT_SCHEMA, status: 'error', error: { message: error.message }, agentGate: { passed: false, status: 'error' } }, null, 2)}\n`,
  )
  process.exitCode = 1
}
