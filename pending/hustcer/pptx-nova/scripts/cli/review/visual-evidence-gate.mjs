#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { evaluateVisualEvidence } from '../../lib/review/canonical-visual-evidence.mjs'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/visual-evidence-gate.mjs --manifest <path> [options]

Options:
  --manifest <path>  Canonical pptx-visual-evidence/v1 manifest.
  --candidate <path> Current PPTX, required for create evidence binding.
  --review <path>    Actual visual review bound by --candidate and --manifest.
  --lock <path>      Run deck_lock.json, required to authorize a reviewed Create.
  --output <path>    Optional persisted gate report.
  --json             Print the gate report as JSON.
  --help             Show this help.

Exit status:
  0  applicable canonical and review requirements passed
  2  invalid command arguments
  3  invalid or inconsistent evidence manifest
  4  manifest.decision.action is stop
  5  manifest.decision.action requires human confirmation
  6  candidate checks passed; actual visual review is still required
`

function parseArgs(argv) {
  const args = { manifest: '', output: '', candidate: '', review: '', lock: '', json: false }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (['--manifest', '--output', '--candidate', '--review', '--lock'].includes(arg)) {
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
      args[arg.slice(2)] = value
      index += 1
    } else {
      throw new Error(`Unknown option: ${arg}`)
    }
  }
  if (!args.manifest) throw new Error('--manifest is required')
  return args
}

function readManifest(path) {
  const resolved = resolve(path)
  if (!existsSync(resolved)) throw new Error(`visual evidence manifest does not exist: ${resolved}`)
  try {
    return { path: resolved, value: JSON.parse(readFileSync(resolved, 'utf8')) }
  } catch (error) {
    throw new Error(`visual evidence manifest is not valid JSON: ${error.message}`)
  }
}

function writeReport(args, report) {
  const text = `${JSON.stringify(report, null, 2)}\n`
  if (args.output) writeFileSync(resolve(args.output), text)
  if (args.json) process.stdout.write(text)
  else {
    process.stdout.write(`Visual evidence gate: ${report.status}\n`)
    process.stdout.write(`Action: ${report.decision?.action ?? 'invalid'}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const { path, value: manifest } = readManifest(args.manifest)
  const expectedDesignMode = args.lock
    ? (JSON.parse(readFileSync(resolve(args.lock), 'utf8'))?.artDirection?.mode ?? '')
    : ''
  const report = evaluateVisualEvidence(path, {
    candidate: args.candidate,
    review: args.review,
    expectedDesignMode,
  })
  writeReport(args, report)
  if (report.status === 'invalid') process.exit(3)
  if (report.status === 'needs-visual-review') process.exit(6)
  if (manifest.decision.action === 'stop') process.exit(4)
  if (manifest.decision.action === 'require-human-confirmation') process.exit(5)
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(2)
}
