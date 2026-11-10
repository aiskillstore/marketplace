#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { advanceSessionRules, normalizeSessionRules } from '../../lib/edit/session-rules.mjs'

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/session-rules.mjs --draft <path> --source <pptx> [options]
  node <skill-root>/scripts/cli/edit/session-rules.mjs --rules <path> --source <accepted.pptx> [options]

Normalize explicit current-deck session rules or advance them to an accepted deck revision.

Options:
  --draft <path>   Agent-authored session rules draft.
  --rules <path>   Existing normalized session-rules.json to advance.
  --source <pptx>  Current/accepted deck revision.
  --output <path>  Defaults to session-rules.json beside the input artifact.
  --overwrite      Replace an existing output.
  --json           Print the normalized artifact.
  --help           Show this help.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = { draft: '', rules: '', source: '', output: '', overwrite: false, json: false }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else if (['--draft', '--rules', '--source', '--output', '-o'].includes(arg)) {
      const key = arg === '-o' ? 'output' : arg.slice(2)
      args[key] = valueAfter(argv, index, arg)
      index += 1
    } else throw new Error(`Unknown option: ${arg}\n\n${usage}`)
  }
  if (Boolean(args.draft) === Boolean(args.rules)) {
    throw new Error(`exactly one of --draft or --rules is required\n\n${usage}`)
  }
  if (!args.source) throw new Error(`--source is required\n\n${usage}`)
  const input = resolve(args.draft || args.rules)
  args.draft = args.draft ? input : ''
  args.rules = args.rules ? input : ''
  args.source = resolve(args.source)
  args.output = resolve(args.output || resolve(dirname(input), 'session-rules.json'))
  if (!existsSync(input)) throw new Error(`input does not exist: ${input}`)
  if (!existsSync(args.source)) throw new Error(`source PPTX does not exist: ${args.source}`)
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
  const artifact = args.draft
    ? normalizeSessionRules(readJson(args.draft, 'session rules draft'), args.source)
    : advanceSessionRules(readJson(args.rules, 'session rules'), args.source)
  writeFileSync(args.output, `${JSON.stringify(artifact, null, 2)}\n`)
  if (args.json) process.stdout.write(`${JSON.stringify(artifact, null, 2)}\n`)
  else process.stdout.write(`Session rules: ${args.output}\n`)
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exit(1)
}
