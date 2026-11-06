#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'

const SCHEMA_VERSION = 'pptx-nova-edit-evidence-manifest/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/evidence-manifest.mjs --candidate <pptx> --evidence <kind=path> [options]

Bind the stable candidate bytes to the exact evidence files consumed by the edit-contract gate.

Options:
  --candidate <pptx>     Required stable candidate PPTX.
  --evidence <kind=path> Repeat for each post-apply evidence file.
  --output <path>        Defaults to evidence-manifest.json beside the candidate.
  --overwrite            Replace an existing output.
  --json                 Print the manifest to stdout.
  --help                 Show this help.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = { candidate: '', evidence: [], output: '', overwrite: false, json: false }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--candidate') {
      args.candidate = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--evidence') {
      args.evidence.push(valueAfter(argv, index, arg))
      index += 1
    } else if (arg === '--output' || arg === '-o') {
      args.output = valueAfter(argv, index, arg)
      index += 1
    } else if (arg === '--overwrite') args.overwrite = true
    else if (arg === '--json') args.json = true
    else throw new Error(`Unknown option: ${arg}\n\n${usage}`)
  }
  if (!args.candidate) throw new Error(`--candidate is required\n\n${usage}`)
  if (args.evidence.length === 0) throw new Error(`--evidence is required\n\n${usage}`)
  args.candidate = resolve(args.candidate)
  args.output = resolve(args.output || join(dirname(args.candidate), 'evidence-manifest.json'))
  if (!existsSync(args.candidate)) throw new Error(`candidate does not exist: ${args.candidate}`)
  if (existsSync(args.output) && !args.overwrite) {
    throw new Error(`output already exists: ${args.output}; use --overwrite for the current run`)
  }
  return args
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function evidenceEntries(values) {
  const seen = new Set()
  return values.map((value) => {
    const split = value.indexOf('=')
    if (split < 1) throw new Error(`--evidence must use kind=path: ${value}`)
    const kind = value.slice(0, split).trim()
    const path = resolve(value.slice(split + 1).trim())
    if (!kind || !path) throw new Error(`--evidence must use kind=path: ${value}`)
    if (seen.has(kind)) throw new Error(`duplicate evidence kind: ${kind}`)
    if (!existsSync(path)) throw new Error(`evidence does not exist: ${path}`)
    seen.add(kind)
    return { kind, path, sha256: sha256(path), byteLength: statSync(path).size }
  })
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const candidateStat = statSync(args.candidate)
  const manifest = {
    schemaVersion: SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    candidate: {
      path: args.candidate,
      sha256: sha256(args.candidate),
      byteLength: candidateStat.size,
    },
    evidence: evidenceEntries(args.evidence),
  }
  writeFileSync(args.output, `${JSON.stringify(manifest, null, 2)}\n`)
  if (args.json) process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`)
  else process.stdout.write(`Edit evidence manifest: ${args.output}\n`)
}

try {
  main()
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exit(1)
}
