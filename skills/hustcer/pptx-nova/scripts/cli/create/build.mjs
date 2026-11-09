#!/usr/bin/env node
import { SKILL_ROOT as skillRoot } from '../../lib/runtime/skill-paths.mjs'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import {
  assessDeckQuality,
  loadCatalog,
} from '../../../assets/deckkits/shared/core-primitives.kit.mjs'
import { validateDeckkitContent as validateContent } from '../../../assets/deckkits/shared/validate-deckkit.mjs'
import { createAssetContext, readAssetManifest } from '../../lib/assets/asset-manifest.mjs'
import { resolveFilesystemPath } from '../../lib/runtime/filesystem-paths.mjs'

const deckkitRoot = join(skillRoot, 'assets', 'deckkits')

const usage = `Usage:
  node <skill-root>/scripts/cli/create/build.mjs --deckkit <id> content.json [options]

Options:
  --deckkit <id>             DeckKit id from assets/deckkits/catalog.json.
  --assets <path>            Optional assets_manifest.json for imageSlots/assets.
  -o, --output <path>        Write patch JSON to this file. Defaults to stdout.
  --quality-json <path>      Write assessDeckQuality output to this file.
  --mode <draft|delivery>    Validation mode. Defaults to delivery.
  --fail-on-quality <level>  Exit non-zero on quality level: warning or error.
  --ignore-soft-limits       Pass through to validateContent.
  --pretty                   Pretty-print patch JSON. Default is pretty when writing a file.
  --compact                  Compact patch JSON.
  --help                     Show this help.
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    assets: '',
    content: '',
    output: '',
    qualityJson: '',
    mode: 'delivery',
    failOnQuality: '',
    ignoreSoftLimits: false,
    pretty: null,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--deckkit') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--assets') {
      args.assets = resolveFilesystemPath(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '-o' || arg === '--output') {
      args.output = resolveFilesystemPath(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--quality-json') {
      args.qualityJson = resolveFilesystemPath(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--mode') {
      args.mode = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--fail-on-quality') {
      args.failOnQuality = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--ignore-soft-limits') {
      args.ignoreSoftLimits = true
    } else if (arg === '--pretty') {
      args.pretty = true
    } else if (arg === '--compact') {
      args.pretty = false
    } else if (!arg.startsWith('--') && !args.content) {
      args.content = resolveFilesystemPath(arg)
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.content) throw new Error(`content.json path is required\n\n${usage}`)
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function writeJson(path, value, pretty = true) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, pretty ? 2 : 0)}\n`)
}

function severityRank(status) {
  return status === 'error' ? 2 : status === 'warning' ? 1 : 0
}

function shouldFailQuality(status, threshold) {
  if (!threshold) return false
  if (!['warning', 'error'].includes(threshold)) {
    throw new Error(`--fail-on-quality must be warning or error, got "${threshold}"`)
  }
  return severityRank(status) >= severityRank(threshold)
}

async function loadDeckkit(deckkit) {
  const catalog = loadCatalog()
  const entry = catalog.entries.find((item) => item.id === deckkit)
  if (!entry) {
    throw new Error(
      `DeckKit "${deckkit}" not found. Available: ${catalog.entries.map((e) => e.id).join(', ')}`,
    )
  }
  const modulePath = join(deckkitRoot, entry.path)
  const mod = await import(pathToFileURL(modulePath).href)
  if (typeof mod.createDeck !== 'function') {
    throw new Error(`DeckKit "${deckkit}" at ${entry.path} does not export createDeck(content)`)
  }
  return mod
}

try {
  const args = parseArgs(process.argv.slice(2))
  const content = readJson(args.content)
  const deckkit = args.deckkit || content?.meta?.deckkit
  if (!deckkit) throw new Error('--deckkit is required when content.meta.deckkit is missing')

  const validation = validateContent(content, {
    deckkit,
    mode: args.mode,
    ignoreSoftLimits: args.ignoreSoftLimits,
  })
  if (!validation.valid) {
    const messages = validation.errors.map((error) => `  [${error.type}] ${error.message}`)
    throw new Error(`Content validation failed:\n${messages.join('\n')}`)
  }

  const deckkitModule = await loadDeckkit(deckkit)
  const assets = args.assets
    ? createAssetContext(readAssetManifest(args.assets), args.assets)
    : null
  const result = deckkitModule.createDeck(content, { assets })
  const patch = result.patch ?? result
  const quality = assessDeckQuality({ patch, deckkit })
  if (result.designPlan) {
    quality.design = result.designCheck
    if (args.output) {
      writeJson(join(dirname(args.output), 'design-plan.json'), result.designPlan)
      writeJson(join(dirname(args.output), 'design-check.json'), result.designCheck)
      writeJson(join(dirname(args.output), 'design-contract.json'), result.designContract)
    }
  }
  if (args.qualityJson) writeJson(args.qualityJson, quality)
  if (shouldFailQuality(quality.status, args.failOnQuality)) {
    throw new Error(
      `Deck quality status "${quality.status}" meets --fail-on-quality ${args.failOnQuality}`,
    )
  }

  const pretty = args.pretty ?? Boolean(args.output)
  const patchJson = `${JSON.stringify(patch, null, pretty ? 2 : 0)}\n`
  if (args.output) {
    mkdirSync(dirname(args.output), { recursive: true })
    writeFileSync(args.output, patchJson)
  } else {
    process.stdout.write(patchJson)
  }
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(1)
}
