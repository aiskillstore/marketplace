#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { resolveSessionRules } from '../../lib/edit/session-rules.mjs'

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/session-rules-resolve.mjs --rules <path> --operation <path> --source <pptx> [options]

Resolve active current-deck rules into a deterministic Edit Contract overlay.

Options:
  --rules <path>      Required normalized session-rules.json.
  --operation <path>  Required structured session operation plan.
  --source <pptx>     Required current deck revision.
  --output <path>     Defaults to session-rules-resolution.json beside the operation.
  --overwrite         Replace an existing output.
  --strict            Exit 2 when blockers remain.
  --json              Print the resolution report.
  --help              Show this help.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = {
    rules: '',
    operation: '',
    source: '',
    output: '',
    overwrite: false,
    strict: false,
    json: false,
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--strict') args.strict = true
    else if (arg === '--json') args.json = true
    else if (['--rules', '--operation', '--source', '--output', '-o'].includes(arg)) {
      const key = arg === '-o' ? 'output' : arg.slice(2)
      args[key] = valueAfter(argv, index, arg)
      index += 1
    } else throw new Error(`Unknown option: ${arg}\n\n${usage}`)
  }
  for (const key of ['rules', 'operation', 'source']) {
    if (!args[key]) throw new Error(`--${key} is required\n\n${usage}`)
    args[key] = resolve(args[key])
    if (!existsSync(args[key])) throw new Error(`${key} does not exist: ${args[key]}`)
  }
  args.output = resolve(
    args.output || join(dirname(args.operation), 'session-rules-resolution.json'),
  )
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(`output already exists: ${args.output}; use --overwrite for the current run`)
  }
  return args
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(
      `${label} is not valid JSON: ${error instanceof Error ? error.message : String(error)}`,
    )
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const report = resolveSessionRules({
    rulesDocument: readJson(args.rules, 'session rules'),
    operationDocument: readJson(args.operation, 'session operation'),
    sourcePath: args.source,
    rulesPath: args.rules,
    operationPath: args.operation,
  })
  writeFileSync(args.output, `${JSON.stringify(report, null, 2)}\n`)
  if (args.json) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
  else
    process.stdout.write(
      `Session rules resolution: ${report.status}\n${report.agentGate.message}\n`,
    )
  if (args.strict && report.status !== 'pass') process.exit(2)
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exit(1)
}
