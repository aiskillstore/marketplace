#!/usr/bin/env node
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { assessDeckQuality, loadContent } from '../../shared/core-primitives.kit.mjs'
import { validateDeckkitContent as validateContent } from '../../shared/validate-deckkit.mjs'
import { createDeck } from '../black-gold.kit.mjs'

function parseArgs(argv) {
  const args = {
    contentPath: null,
    qualityJson: null,
    failOnQuality: null,
  }
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--quality-json') {
      args.qualityJson = argv[++i]
    } else if (arg === '--fail-on-quality') {
      args.failOnQuality = argv[++i]
    } else if (!args.contentPath) {
      args.contentPath = arg
    } else {
      throw new Error(`unexpected argument: ${arg}`)
    }
  }
  if (args.qualityJson === undefined) throw new Error('--quality-json requires a path')
  if (args.failOnQuality === undefined)
    throw new Error('--fail-on-quality requires error or warning')
  if (args.failOnQuality && !['error', 'warning'].includes(args.failOnQuality)) {
    throw new Error('--fail-on-quality must be "error" or "warning"')
  }
  return args
}

function qualityFails(report, level) {
  if (!level) return false
  if (level === 'warning') return report.issues.length > 0
  return report.issues.some((issue) => issue.severity === 'error')
}

const deckkitId = 'black-gold'
const args = parseArgs(process.argv)
const content = await loadContent(
  args.contentPath ?? fileURLToPath(new URL('./content.json', import.meta.url)),
)
const validation = validateContent(content, { deckkit: deckkitId })
if (!validation.valid) {
  console.error(JSON.stringify(validation, null, 2))
  process.exit(1)
}

const { patch, warnings } = createDeck(content)
for (const warning of warnings) console.error(`[warning] ${warning}`)
const quality = assessDeckQuality({ patch, deckkit: deckkitId })
if (args.qualityJson) {
  writeFileSync(args.qualityJson, `${JSON.stringify(quality, null, 2)}\n`)
}
if (qualityFails(quality, args.failOnQuality)) {
  console.error(JSON.stringify(quality, null, 2))
  process.exit(1)
}
process.stdout.write(JSON.stringify(patch))
