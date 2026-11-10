#!/usr/bin/env node
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import {
  buildLayoutSnapshot,
  buildLayoutSnapshotFailure,
} from '../../lib/review/layout-snapshot.mjs'
import { ensureWritableOutput, writeJsonOutput } from '../../lib/runtime/output-files.mjs'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/layout-snapshot.mjs --inspect final-inspect.json [options]

Options:
  --inspect <path>  Required xdoc pptx inspect JSON for the final deck.
  --output <path>   Optional output path. Defaults to stdout only.
  --overwrite       Replace an existing current-run output.
  --json            Print machine-readable layout snapshot.
  --help            Show this help.

This script normalizes inspect JSON into layout-final.json. It reports structural
layout risks as warnings but does not act as a hard quality gate.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = { inspect: '', output: '', overwrite: false, json: false }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--inspect' || arg === '--output') {
      const key = arg === '--inspect' ? 'inspect' : 'output'
      args[key] = resolve(valueAfter(argv, index, arg))
      index += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.inspect) throw new Error(`--inspect is required\n\n${usage}`)
  return args
}

function readJson(path) {
  if (!existsSync(path)) throw new Error(`inspect JSON does not exist: ${path}`)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`Failed to read inspect JSON at ${path}: ${error.message}`)
  }
}

function printHuman(snapshot) {
  process.stdout.write(`pptx-nova layout snapshot: ${snapshot.status}\n`)
  process.stdout.write(`- slides: ${snapshot.summary.slideCount}\n`)
  process.stdout.write(`- objects: ${snapshot.summary.objectCount}\n`)
  process.stdout.write(`- risks: ${snapshot.summary.riskCount}\n`)
  process.stdout.write(`- actionable risks: ${snapshot.summary.actionableRiskCount ?? 0}\n`)
  process.stdout.write(`- informational risks: ${snapshot.summary.informationalRiskCount ?? 0}\n`)
}

let args = null
try {
  args = parseArgs(process.argv.slice(2))
  if (args.output) ensureWritableOutput(args.output, args.overwrite, 'layout snapshot output')
  const snapshot = buildLayoutSnapshot(readJson(args.inspect), { sourceLabel: args.inspect })
  if (args.output) {
    writeJsonOutput(args.output, snapshot, {
      overwrite: args.overwrite,
      label: 'layout snapshot output',
    })
  }
  if (args.json) process.stdout.write(`${JSON.stringify(snapshot, null, 2)}\n`)
  else printHuman(snapshot)
} catch (error) {
  const failure = buildLayoutSnapshotFailure(args?.inspect ?? '', error)
  if (args?.output && (args.overwrite || !existsSync(args.output))) {
    writeJsonOutput(args.output, failure, {
      overwrite: args.overwrite,
      label: 'layout snapshot output',
    })
  }
  if (args?.json) process.stdout.write(`${JSON.stringify(failure, null, 2)}\n`)
  else printHuman(failure)
  process.exitCode = 1
}
