#!/usr/bin/env node

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { cwd, exit, argv } from 'node:process'
import { fileURLToPath } from 'node:url'

const SUPPORTED_PROVIDERS = new Set(['auto', 'text-svg'])

function fail(message) {
  throw new Error(message)
}

function parseArgs(args) {
  const options = {
    manifestPath: null,
    outPath: null,
    assetRoot: null,
    provider: 'auto',
    dryRun: false,
    help: false,
  }

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (arg === '--help' || arg === '-h') {
      options.help = true
    } else if (arg === '--dry-run') {
      options.dryRun = true
    } else if (arg === '--out') {
      options.outPath = args[++index] ?? fail('--out requires a path')
    } else if (arg === '--asset-root') {
      options.assetRoot = args[++index] ?? fail('--asset-root requires a path')
    } else if (arg === '--provider') {
      options.provider = args[++index] ?? fail('--provider requires a value')
    } else if (arg.startsWith('--')) {
      fail(`Unknown option: ${arg}`)
    } else if (!options.manifestPath) {
      options.manifestPath = arg
    } else {
      fail(`Unexpected argument: ${arg}`)
    }
  }

  return options
}

function usage() {
  return [
    'Usage: node skills/pptx-nova/scripts/cli/assets/formula-render.mjs <assets_manifest.json> [options]',
    '',
    'Options:',
    '  --out <path>          Write updated manifest to a different path',
    '  --asset-root <path>   Override manifest.assetRoot',
    '  --provider <name>     auto | text-svg (default: auto)',
    '  --dry-run             Validate and report writes without changing files',
  ].join('\n')
}

function xmlEscape(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;')
    .replace(/[\t\r\n]+/g, ' ')
}

function posixRelative(from, to) {
  const relative = path.relative(from, to)
  return relative === '' ? '.' : relative.split(path.sep).join('/')
}

function isInside(root, candidate) {
  const relative = path.relative(root, candidate)
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative))
}

function safeId(value, index) {
  const raw = String(value || `formula-${index + 1}`)
    .trim()
    .toLowerCase()
  const cleaned = raw.replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '')
  return cleaned || `formula-${index + 1}`
}

function displayKind(value) {
  if (value === true) return 'block'
  if (value === false) return 'inline'
  const text = String(value ?? 'block')
    .trim()
    .toLowerCase()
  return text === 'inline' ? 'inline' : 'block'
}

export function renderFormulaTextSvg(latex, display = 'block') {
  const block = displayKind(display) !== 'inline'
  const width = block ? 1200 : 900
  const height = block ? 240 : 160
  const fontSize = block ? 92 : 72
  const escaped = xmlEscape(latex)
  const metadata = xmlEscape(JSON.stringify({ latex, provider: 'text-svg' }))
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="formula">
  <metadata>${metadata}</metadata>
  <rect width="${width}" height="${height}" fill="none"/>
  <text x="${width / 2}" y="${height / 2}" text-anchor="middle" dominant-baseline="middle" font-family="Cambria Math, STIX Two Math, Latin Modern Math, Noto Sans Math, serif" font-size="${fontSize}" fill="#111111">${escaped}</text>
</svg>
`
  return { svg, width, height, mime: 'image/svg+xml', provider: 'text-svg' }
}

function resolveAssetRoot(manifestDir, manifest, override) {
  const raw = override ?? manifest.assetRoot ?? 'assets'
  return path.isAbsolute(raw) ? path.normalize(raw) : path.resolve(manifestDir, raw)
}

function resolveEntryPath(manifestDir, assetRootAbs, entry, id, index) {
  const rawPath = entry.path ?? `formulas/${safeId(id, index)}.svg`
  if (path.isAbsolute(rawPath)) {
    fail(`formula entry ${id} path must be relative: ${rawPath}`)
  }
  const fromManifest = path.resolve(manifestDir, rawPath)
  if (isInside(assetRootAbs, fromManifest)) return fromManifest
  const fromAssetRoot = path.resolve(assetRootAbs, rawPath)
  if (isInside(assetRootAbs, fromAssetRoot)) return fromAssetRoot
  fail(`formula entry ${id} path escapes assetRoot: ${rawPath}`)
}

export function renderFormulaManifest(options) {
  if (!SUPPORTED_PROVIDERS.has(options.provider)) {
    fail(`unsupported provider ${options.provider}; expected auto or text-svg`)
  }

  const manifestPath = path.resolve(options.manifestPath)
  const manifestDir = path.dirname(manifestPath)
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  const entries = Array.isArray(manifest.entries) ? manifest.entries : []
  const assetRootAbs = resolveAssetRoot(manifestDir, manifest, options.assetRoot)
  const updatedEntries = []
  const writes = []
  const errors = []
  let rendered = 0
  let skipped = 0
  let needsUser = 0

  for (const [index, entry] of entries.entries()) {
    if (entry?.kind !== 'formula') {
      updatedEntries.push(entry)
      skipped += 1
      continue
    }

    const id = entry.id ?? `formula-${index + 1}`
    const source = entry.source && typeof entry.source === 'object' ? entry.source : {}
    const latex = String(source.latex ?? entry.latex ?? '').trim()
    if (!latex) {
      needsUser += 1
      updatedEntries.push({
        ...entry,
        status: 'needs-user',
        render: {
          ...(entry.render ?? {}),
          provider: 'text-svg',
          error: 'missing source.latex',
        },
      })
      continue
    }

    const display = displayKind(source.display ?? entry.display)
    let target
    try {
      target = resolveEntryPath(manifestDir, assetRootAbs, entry, id, index)
    } catch (error) {
      errors.push({ id, message: error.message })
      updatedEntries.push({ ...entry, status: 'missing' })
      continue
    }

    const { svg, width, height, mime, provider } = renderFormulaTextSvg(latex, display)
    if (!options.dryRun) {
      mkdirSync(path.dirname(target), { recursive: true })
      writeFileSync(target, svg, 'utf8')
    }
    writes.push(posixRelative(manifestDir, target))
    rendered += 1
    updatedEntries.push({
      ...entry,
      status: 'rendered',
      path: entry.path ?? posixRelative(manifestDir, target),
      source: {
        ...source,
        kind: 'formula',
        latex,
        display,
      },
      render: {
        ...(entry.render ?? {}),
        provider,
        mime,
        width,
        height,
        deterministic: true,
      },
      pptxUse: {
        ...(entry.pptxUse ?? {}),
        noCrop: true,
      },
    })
  }

  const updatedManifest = { ...manifest, entries: updatedEntries }
  const outPath = options.outPath ? path.resolve(options.outPath) : manifestPath
  if (!options.dryRun) {
    writeFileSync(outPath, `${JSON.stringify(updatedManifest, null, 2)}\n`, 'utf8')
  }

  return {
    ok: errors.length === 0,
    provider: 'text-svg',
    dryRun: Boolean(options.dryRun),
    manifestPath: posixRelative(cwd(), manifestPath),
    outPath: posixRelative(cwd(), outPath),
    assetRoot: posixRelative(cwd(), assetRootAbs),
    counts: { rendered, skipped, needsUser, errors: errors.length },
    writes,
    errors,
  }
}

function main() {
  const options = parseArgs(argv.slice(2))
  if (options.help) {
    console.log(usage())
    return
  }
  if (!options.manifestPath) {
    console.error(usage())
    exit(2)
  }
  const summary = renderFormulaManifest(options)
  console.log(JSON.stringify(summary, null, 2))
  if (!summary.ok) exit(1)
}

const invokedPath = argv[1] ? path.resolve(argv[1]) : ''
const modulePath = fileURLToPath(import.meta.url)
if (invokedPath === modulePath) {
  try {
    main()
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error))
    exit(1)
  }
}
