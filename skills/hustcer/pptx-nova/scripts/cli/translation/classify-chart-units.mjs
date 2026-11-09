#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const REPORT_SCHEMA = 'pptx-nova-i18n-chart-classification/v1'
const DECISIONS_SCHEMA = 'pptx-nova-i18n-chart-decisions/v1'

function parseArgs(argv) {
  const args = { scan: '', decisions: '', output: '', report: '', overwrite: false, json: false }
  const flags = {
    '--scan': 'scan',
    '--decisions': 'decisions',
    '--output': 'output',
    '--report': 'report',
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else if (arg === '--help' || arg === '-h') {
      process.stdout.write(
        'Usage: node cli/translation/classify-chart-units.mjs --scan scan.json --decisions decisions.json --output classified-scan.json [--report report.json] [--overwrite] [--json]\n',
      )
      process.exit(0)
    } else if (flags[arg]) {
      const value = argv[i + 1]
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
      args[flags[arg]] = resolve(value)
      i += 1
    } else throw new Error(`Unknown option: ${arg}`)
  }
  for (const key of ['scan', 'decisions', 'output']) {
    if (!args[key]) throw new Error(`--${key} is required`)
  }
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
  const reviewUnits = units.filter(
    (unit) => unit.category === 'chartVisibleCache' && unit.action === 'review',
  )
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

  const classified = structuredClone(scan)
  const classifiedUnits = classified.i18nUnits.units
  const applied = []
  for (let index = 0; index < units.length; index += 1) {
    const unit = units[index]
    if (unit.category !== 'chartVisibleCache' || unit.action !== 'review') continue
    const decision = decisions.get(unit.unitId)
    if (!decision) throw new Error(`missing chart classification for ${unit.unitId}`)
    if (decision.sourceHash !== unit.sourceHash)
      throw new Error(`sourceHash mismatch for ${unit.unitId}`)
    classifiedUnits[index].action = decision.decision
    classifiedUnits[index].requiresReview = false
    classifiedUnits[index].reason = decision.reason
    classifiedUnits[index].notes = [
      ...new Set([...(unit.notes ?? []), `classified-${decision.decision}`]),
    ]
    applied.push({
      unitId: unit.unitId,
      sourceText: unit.sourceText,
      decision: decision.decision,
      reason: decision.reason,
    })
    decisions.delete(unit.unitId)
  }
  if (decisions.size > 0)
    throw new Error(
      `decisions reference unknown or non-review units: ${[...decisions.keys()].join(', ')}`,
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
    },
    applied,
    agentGate: { passed: true, status: 'pass', unclassifiedCount: 0 },
  }
  if (args.report) write(args.report, report, args.overwrite)
  if (args.json || !args.report) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
}

try {
  main()
} catch (error) {
  process.stderr.write(
    `${JSON.stringify({ schemaVersion: REPORT_SCHEMA, status: 'error', error: { message: error.message }, agentGate: { passed: false, status: 'error' } }, null, 2)}\n`,
  )
  process.exitCode = 1
}
