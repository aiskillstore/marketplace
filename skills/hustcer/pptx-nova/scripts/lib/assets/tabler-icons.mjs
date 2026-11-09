import { SKILL_ROOT } from '../runtime/skill-paths.mjs'

import { Buffer } from 'node:buffer'
import { brotliCompressSync, brotliDecompressSync, constants as zlibConstants } from 'node:zlib'
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'

export const PACK_SCHEMA_VERSION = 'pptx-nova-tabler-icon-pack/v1'
export const DEFAULT_SOURCE_ROOT = process.env.TABLER_ICONS_ROOT ?? ''

export const DEFAULT_PACK_PATH = join(SKILL_ROOT, 'assets/icons/tabler-icons.pack.br')
export const DEFAULT_LICENSE_PATH = join(SKILL_ROOT, 'assets/icons/icon-license')

const STYLES = ['outline', 'filled']
const ICON_NAME_RE = /^[a-z0-9][a-z0-9-]*$/
const FIELD_SEP = '\t'
const DEFAULT_LIMIT = 20
const DEFAULT_OUTLINE_STROKE_WIDTH = '1'

export const TABLER_SHELLS = {
  outline: {
    prefix:
      '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
    suffix: '</svg>',
  },
  filled: {
    prefix:
      '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">',
    suffix: '</svg>',
  },
}

function formatPackStrokeWidth(value = DEFAULT_OUTLINE_STROKE_WIDTH) {
  const width = Number(value)
  if (!Number.isFinite(width) || width <= 0 || width > 8) {
    fail(`Tabler outline stroke width must be between 0 and 8, got: ${value}`)
  }
  return Number(width.toFixed(2)).toString()
}

function tablerShellsForPack({ outlineStrokeWidth = DEFAULT_OUTLINE_STROKE_WIDTH } = {}) {
  const strokeWidth = formatPackStrokeWidth(outlineStrokeWidth)
  return {
    outline: {
      ...TABLER_SHELLS.outline,
      prefix: TABLER_SHELLS.outline.prefix.replace(
        'stroke-width="2"',
        `stroke-width="${strokeWidth}"`,
      ),
    },
    filled: TABLER_SHELLS.filled,
  }
}

const packTextCache = new Map()
const parsedPackCache = new Map()

function fail(message) {
  throw new Error(message)
}

function normalizeSvg(text) {
  return String(text)
    .replace(/<!--.*?-->\s*/gs, '')
    .trim()
    .replace(/>\s+</g, '><')
    .replace(/\s+/g, ' ')
    .replace(/\s+\/>/g, '/>')
    .replace(/\s+>/g, '>')
}

function parseFrontMatter(text) {
  const match = String(text).match(/^<!--\s*([\s\S]*?)\s*-->/)
  const data = {
    tags: [],
    category: '-',
    version: '-',
    unicode: '-',
  }
  if (!match) return data

  for (const line of match[1]
    .split(/\r?\n/)
    .map((value) => value.trim())
    .filter(Boolean)) {
    const field = line.match(/^([\w-]+):\s*(.*)$/)
    if (!field) continue
    const [, key, rawValue] = field
    if (key === 'tags') {
      data.tags = [...rawValue.matchAll(/[a-z0-9][a-z0-9-]*/gi)].map((item) =>
        item[0].toLowerCase(),
      )
    } else if (key in data) {
      data[key] = rawValue.replace(/^"|"$/g, '')
    }
  }
  return data
}

function assertCleanField(value, label) {
  const text = String(value)
  if (text.includes('\t') || text.includes('\n') || text.includes('\r')) {
    fail(`Tabler icon pack field ${label} contains a tab or newline`)
  }
  return text
}

function normalizeStyle(style = 'outline') {
  const value = String(style ?? 'outline').trim()
  if (!STYLES.includes(value)) {
    fail(`Tabler icon style must be outline or filled, got: ${style}`)
  }
  return value
}

export function normalizeTablerIconName(name) {
  const iconName = String(name ?? '').trim()
  if (!ICON_NAME_RE.test(iconName)) {
    fail(`Invalid Tabler icon name: ${name}`)
  }
  return iconName
}

function listSvgFiles(dir) {
  if (!existsSync(dir)) fail(`Tabler icon directory does not exist: ${dir}`)
  return readdirSync(dir)
    .filter((file) => file.endsWith('.svg'))
    .sort((a, b) => a.localeCompare(b))
}

function readJsonIfExists(path, fallback) {
  if (!existsSync(path)) return fallback
  return JSON.parse(readFileSync(path, 'utf8'))
}

function tablerVersion(sourceRoot) {
  return readJsonIfExists(join(sourceRoot, 'package.json'), {}).version ?? 'unknown'
}

function aliasesForIcon(aliases, style, name) {
  return Object.entries(aliases[style] ?? {})
    .filter(([, target]) => target === name)
    .map(([alias]) => alias)
    .sort((a, b) => a.localeCompare(b))
}

function readSourceRows(sourceRoot) {
  const aliases = readJsonIfExists(join(sourceRoot, 'aliases.json'), {})
  const rows = []

  for (const style of STYLES) {
    const iconDir = join(sourceRoot, 'icons', style)
    for (const file of listSvgFiles(iconDir)) {
      const name = file.replace(/\.svg$/, '')
      if (!ICON_NAME_RE.test(name)) fail(`Invalid Tabler icon file name: ${file}`)

      const iconPath = join(iconDir, file)
      const raw = readFileSync(iconPath, 'utf8')
      const svg = normalizeSvg(raw)
      const shell = TABLER_SHELLS[style]

      if (!svg.startsWith(shell.prefix) || !svg.endsWith(shell.suffix)) {
        fail(`Tabler icon ${style}/${name} does not match the fixed ${style} SVG shell`)
      }

      rows.push({
        style,
        name,
        body: svg.slice(shell.prefix.length, svg.length - shell.suffix.length),
        ...parseFrontMatter(raw),
        aliases: aliasesForIcon(aliases, style, name),
      })
    }
  }

  return rows.sort((a, b) => a.style.localeCompare(b.style) || a.name.localeCompare(b.name))
}

function renderPackText({ rows, version, shells = TABLER_SHELLS }) {
  const header = [
    `# ${PACK_SCHEMA_VERSION}`,
    `# source=tabler-icons`,
    `# version=${assertCleanField(version, 'version')}`,
    ...STYLES.map((style) =>
      [
        '@shell',
        style,
        assertCleanField(shells[style].prefix, `${style}.prefix`),
        assertCleanField(shells[style].suffix, `${style}.suffix`),
      ].join(FIELD_SEP),
    ),
    '@@catalog',
  ].join('\n')

  const catalog = rows
    .map((row) =>
      [
        '@icon',
        assertCleanField(row.style, `${row.name}.style`),
        assertCleanField(row.name, `${row.name}.name`),
        assertCleanField(row.category || '-', `${row.name}.category`),
        assertCleanField(row.tags.join(','), `${row.name}.tags`),
        assertCleanField(row.aliases.join(','), `${row.name}.aliases`),
        assertCleanField(row.version || '-', `${row.name}.version`),
        assertCleanField(row.unicode || '-', `${row.name}.unicode`),
      ].join(FIELD_SEP),
    )
    .join('\n')

  const icons = rows
    .map((row) =>
      [
        '@svg',
        assertCleanField(row.style, `${row.name}.style`),
        assertCleanField(row.name, `${row.name}.name`),
        assertCleanField(row.body, `${row.name}.body`),
      ].join(FIELD_SEP),
    )
    .join('\n')

  return `${header}\n${catalog}\n@@icons\n${icons}\n`
}

export function buildTablerIconPackText(sourceRoot = DEFAULT_SOURCE_ROOT, options = {}) {
  if (!sourceRoot)
    fail('Tabler source root is required. Pass --source-root or set TABLER_ICONS_ROOT.')
  const sourceRootPath = resolve(sourceRoot)
  const rows = readSourceRows(sourceRootPath)
  return renderPackText({
    rows,
    version: tablerVersion(sourceRootPath),
    shells: tablerShellsForPack(options),
  })
}

function compressPackText(text) {
  const bytes = Buffer.from(text, 'utf8')
  return brotliCompressSync(bytes, {
    params: {
      [zlibConstants.BROTLI_PARAM_QUALITY]: 11,
      [zlibConstants.BROTLI_PARAM_SIZE_HINT]: bytes.length,
    },
  })
}

function syncBytes(path, bytes, check) {
  const current = existsSync(path) ? readFileSync(path) : null
  const changed = !current || !current.equals(bytes)
  if (changed && !check) {
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, bytes)
  }
  return { path, changed, bytes: bytes.length }
}

function syncText(path, text, check) {
  const current = existsSync(path) ? readFileSync(path, 'utf8') : null
  const changed = current !== text
  if (changed && !check) {
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, text)
  }
  return { path, changed, bytes: Buffer.byteLength(text) }
}

export function generateTablerIconPack({
  sourceRoot = DEFAULT_SOURCE_ROOT,
  output = DEFAULT_PACK_PATH,
  licenseOutput = DEFAULT_LICENSE_PATH,
  outlineStrokeWidth = DEFAULT_OUTLINE_STROKE_WIDTH,
  check = false,
} = {}) {
  if (!sourceRoot)
    fail('Tabler source root is required. Pass --source-root or set TABLER_ICONS_ROOT.')
  const sourceRootPath = resolve(sourceRoot)
  const outputPath = resolve(output)
  const licenseOutputPath = resolve(licenseOutput)
  const licensePath = join(sourceRootPath, 'LICENSE')

  if (!existsSync(sourceRootPath)) fail(`Tabler source root does not exist: ${sourceRootPath}`)
  if (!existsSync(licensePath)) fail(`Tabler LICENSE does not exist: ${licensePath}`)

  const packText = buildTablerIconPackText(sourceRootPath, { outlineStrokeWidth })
  const packBytes = compressPackText(packText)
  const licenseText = readFileSync(licensePath, 'utf8')

  const outputResult = syncBytes(outputPath, packBytes, check)
  const licenseResult = syncText(licenseOutputPath, licenseText, check)
  const stale = outputResult.changed || licenseResult.changed

  if (check && stale) {
    const stalePaths = [outputResult, licenseResult]
      .filter((item) => item.changed)
      .map((item) => item.path)
      .join(', ')
    fail(`generated Tabler icon pack is stale: ${stalePaths}`)
  }

  const info = parseTablerIconPackText(packText)
  return {
    schemaVersion: 'pptx-nova-tabler-icons-sync/v2',
    checked: check,
    sourceRoot: sourceRootPath,
    output: outputResult,
    license: licenseResult,
    sourceVersion: info.version,
    outlineStrokeWidth: formatPackStrokeWidth(outlineStrokeWidth),
    iconCount: info.catalog.length,
    counts: info.counts,
  }
}

export function readTablerIconPackText(packPath = DEFAULT_PACK_PATH) {
  const path = resolve(packPath)
  if (!packTextCache.has(path)) {
    packTextCache.set(path, brotliDecompressSync(readFileSync(path)).toString('utf8'))
  }
  return packTextCache.get(path)
}

function splitCsvField(value) {
  if (!value || value === '-') return []
  return value.split(',').filter(Boolean)
}

export function parseTablerIconPackText(text) {
  const shells = {}
  const catalog = []
  const bodies = new Map()
  const aliases = new Map()
  let section = 'header'
  let version = 'unknown'

  for (const line of String(text).split('\n')) {
    if (!line) continue
    if (line === '@@catalog') {
      section = 'catalog'
      continue
    }
    if (line === '@@icons') {
      section = 'icons'
      continue
    }
    if (line.startsWith('# version=')) {
      version = line.slice('# version='.length)
      continue
    }
    if (line.startsWith('#')) continue

    const parts = line.split(FIELD_SEP)
    if (parts[0] === '@shell') {
      const [, style, prefix, suffix] = parts
      shells[style] = { prefix, suffix }
      continue
    }

    if (section === 'catalog' && parts[0] === '@icon') {
      const [, style, name, category, tags, rowAliases, rowVersion, unicode] = parts
      const entry = {
        style,
        name,
        category,
        tags: splitCsvField(tags),
        aliases: splitCsvField(rowAliases),
        version: rowVersion,
        unicode,
      }
      catalog.push(entry)
      for (const alias of entry.aliases) aliases.set(`${style}/${alias}`, entry.name)
      continue
    }

    if (section === 'icons' && parts[0] === '@svg') {
      const [, style, name, body] = parts
      bodies.set(`${style}/${name}`, body)
    }
  }

  const counts = Object.fromEntries(
    STYLES.map((style) => [style, catalog.filter((entry) => entry.style === style).length]),
  )

  return {
    schemaVersion: PACK_SCHEMA_VERSION,
    version,
    shells,
    catalog,
    bodies,
    aliases,
    counts,
  }
}

export function loadTablerIconPack({ packPath = DEFAULT_PACK_PATH } = {}) {
  const path = resolve(packPath)
  if (!parsedPackCache.has(path)) {
    parsedPackCache.set(path, parseTablerIconPackText(readTablerIconPackText(path)))
  }
  return parsedPackCache.get(path)
}

export function getTablerIconPackInfo(options = {}) {
  const pack = loadTablerIconPack(options)
  return {
    schemaVersion: pack.schemaVersion,
    version: pack.version,
    iconCount: pack.catalog.length,
    counts: pack.counts,
  }
}

function catalogForStyle(pack, style) {
  const normalizedStyle = normalizeStyle(style)
  return pack.catalog.filter((entry) => entry.style === normalizedStyle)
}

export function listTablerIconNames({ style = 'outline', packPath } = {}) {
  const pack = loadTablerIconPack({ packPath })
  return catalogForStyle(pack, style)
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b))
}

export function loadTablerIcons({ style = 'outline', packPath } = {}) {
  const iconMap = {}
  for (const name of listTablerIconNames({ style, packPath })) {
    iconMap[name] = getTablerIconSvg(name, { style, color: null, packPath })
  }
  return iconMap
}

function findCatalogEntry(pack, name, style) {
  return pack.catalog.find((entry) => entry.style === style && entry.name === name) ?? null
}

export function resolveTablerIconEntry(nameOrAlias, { style = 'outline', packPath } = {}) {
  const iconName = normalizeTablerIconName(nameOrAlias)
  const iconStyle = normalizeStyle(style)
  const pack = loadTablerIconPack({ packPath })
  const direct = findCatalogEntry(pack, iconName, iconStyle)
  if (direct) return { ...direct, matched: 'name', input: iconName }

  const aliasTarget = pack.aliases.get(`${iconStyle}/${iconName}`)
  if (aliasTarget) {
    const entry = findCatalogEntry(pack, aliasTarget, iconStyle)
    if (entry) return { ...entry, matched: 'alias', input: iconName }
  }

  fail(`Tabler icon not found in ${iconStyle} pack: ${iconName}`)
}

export function resolveTablerIconName(nameOrAlias, options = {}) {
  return resolveTablerIconEntry(nameOrAlias, options).name
}

export function hasTablerIcon(name, options = {}) {
  try {
    resolveTablerIconEntry(name, options)
    return true
  } catch {
    return false
  }
}

function normalizeSvgColor(value) {
  const color = String(value ?? '').trim()
  if (/^#[0-9A-F]{6}$/i.test(color)) return color.toUpperCase()
  if (/^[0-9A-F]{6}$/i.test(color)) return `#${color.toUpperCase()}`
  fail(`Tabler icon color must be a 6-digit hex value, got: ${value}`)
}

function formatStrokeWidth(value) {
  const width = Number(value)
  if (!Number.isFinite(width) || width <= 0 || width > 8) {
    fail(`Tabler icon strokeWidth must be between 0 and 8, got: ${value}`)
  }
  return Number(width.toFixed(2)).toString()
}

export function getTablerIconSvg(name, options = {}) {
  const entry = resolveTablerIconEntry(name, options)
  const pack = loadTablerIconPack({ packPath: options.packPath })
  const shell = pack.shells[entry.style]
  const body = pack.bodies.get(`${entry.style}/${entry.name}`)
  if (!shell || body === undefined)
    fail(`Tabler icon body is missing: ${entry.style}/${entry.name}`)

  const color = options.color === null ? null : normalizeSvgColor(options.color ?? '111827')
  const strokeWidth =
    options.strokeWidth === undefined ? null : formatStrokeWidth(options.strokeWidth)

  let result = `${shell.prefix}${body}${shell.suffix}`
  if (color) result = result.replaceAll('currentColor', color)
  if (strokeWidth) result = result.replace(/stroke-width="[^"]+"/, `stroke-width="${strokeWidth}"`)
  return result
}

export function getTablerIconAsset(name, options = {}) {
  const svg = getTablerIconSvg(name, options)
  return {
    bytesBase64: Buffer.from(svg, 'utf8').toString('base64'),
    mimeType: 'image/svg+xml',
  }
}

function tokenize(value) {
  return String(value ?? '')
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean)
}

function scoreIcon(entry, query, tokens) {
  const name = entry.name.toLowerCase()
  const aliases = entry.aliases.map((item) => item.toLowerCase())
  const tags = entry.tags.map((item) => item.toLowerCase())
  const category = String(entry.category ?? '').toLowerCase()
  let score = 0

  if (name === query) score += 1000
  if (aliases.includes(query)) score += 950
  if (name.startsWith(query)) score += 500
  if (name.includes(query)) score += 350

  for (const token of tokens) {
    if (name.split('-').includes(token)) score += 120
    else if (name.includes(token)) score += 80
    if (aliases.some((alias) => alias.includes(token))) score += 70
    if (tags.includes(token)) score += 60
    else if (tags.some((tag) => tag.includes(token))) score += 30
    if (category.includes(token)) score += 20
  }

  return score
}

export function searchTablerIcons(
  query,
  { style = 'outline', limit = DEFAULT_LIMIT, packPath } = {},
) {
  const normalizedQuery = String(query ?? '')
    .trim()
    .toLowerCase()
  if (!normalizedQuery) return []

  const pack = loadTablerIconPack({ packPath })
  const styles = style === 'any' ? STYLES : [normalizeStyle(style)]
  const tokens = tokenize(normalizedQuery)
  const results = []

  for (const entry of pack.catalog) {
    if (!styles.includes(entry.style)) continue
    const score = scoreIcon(entry, normalizedQuery, tokens)
    if (score <= 0) continue
    results.push({ ...entry, score })
  }

  return results
    .sort(
      (a, b) =>
        b.score - a.score ||
        STYLES.indexOf(a.style) - STYLES.indexOf(b.style) ||
        a.name.localeCompare(b.name),
    )
    .slice(0, Number(limit) || DEFAULT_LIMIT)
}

export function loadTablerIconSet(names, options = {}) {
  if (!Array.isArray(names)) fail('loadTablerIconSet requires an array of icon names')
  return Object.fromEntries(
    names.map((name) => {
      const entry = resolveTablerIconEntry(name, options)
      return [entry.name, getTablerIconSvg(entry.name, { ...options, style: entry.style })]
    }),
  )
}

function parseCliArgs(argv) {
  const flags = {}
  const positional = []
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (!arg.startsWith('--')) {
      positional.push(arg)
      continue
    }

    const key = arg.slice(2)
    if (['check', 'json', 'svg'].includes(key)) {
      flags[key] = true
      continue
    }
    const value = argv[index + 1]
    if (value === undefined) fail(`Missing value for --${key}`)
    flags[key] = value
    index += 1
  }
  return { flags, positional }
}

function printJson(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`)
}

function usage() {
  return `Usage:
  node <skill-root>/scripts/cli/assets/icons.mjs generate [--source-root <dir>] [--output <pack.br>] [--license-output <path>] [--stroke <width>] [--check]
  node <skill-root>/scripts/cli/assets/icons.mjs info [--pack <pack.br>] [--json]
  node <skill-root>/scripts/cli/assets/icons.mjs search <query> [--style outline|filled|any] [--limit <n>] [--pack <pack.br>] [--json]
  node <skill-root>/scripts/cli/assets/icons.mjs names [--style outline|filled] [--pack <pack.br>] [--json]
  node <skill-root>/scripts/cli/assets/icons.mjs get <name...> [--style outline|filled] [--pack <pack.br>] [--svg|--json]
`
}

function commandGenerate(flags) {
  const result = generateTablerIconPack({
    sourceRoot: flags['source-root'] ?? DEFAULT_SOURCE_ROOT,
    output: flags.output ?? DEFAULT_PACK_PATH,
    licenseOutput: flags['license-output'] ?? DEFAULT_LICENSE_PATH,
    outlineStrokeWidth: flags.stroke ?? DEFAULT_OUTLINE_STROKE_WIDTH,
    check: Boolean(flags.check),
  })
  printJson(result)
}

function commandInfo(flags) {
  const info = getTablerIconPackInfo({ packPath: flags.pack ?? DEFAULT_PACK_PATH })
  if (flags.json) printJson(info)
  else
    process.stdout.write(
      `${info.iconCount} icons (${info.counts.outline} outline, ${info.counts.filled} filled)\n`,
    )
}

function commandSearch(flags, positional) {
  const query = positional.join(' ')
  const results = searchTablerIcons(query, {
    style: flags.style ?? 'outline',
    limit: flags.limit ? Number(flags.limit) : DEFAULT_LIMIT,
    packPath: flags.pack ?? DEFAULT_PACK_PATH,
  })
  if (flags.json) {
    printJson(results)
    return
  }
  for (const item of results) {
    process.stdout.write(`${item.style}\t${item.name}\t${item.category}\t${item.tags.join(',')}\n`)
  }
}

function commandNames(flags) {
  const names = listTablerIconNames({
    style: flags.style ?? 'outline',
    packPath: flags.pack ?? DEFAULT_PACK_PATH,
  })
  if (flags.json) printJson(names)
  else process.stdout.write(`${names.join('\n')}\n`)
}

function commandGet(flags, positional) {
  if (positional.length === 0) fail('get requires at least one icon name')
  const rows = positional.map((name) => {
    const entry = resolveTablerIconEntry(name, {
      style: flags.style ?? 'outline',
      packPath: flags.pack ?? DEFAULT_PACK_PATH,
    })
    return {
      input: name,
      style: entry.style,
      name: entry.name,
      matched: entry.matched,
      svg: getTablerIconSvg(entry.name, {
        style: entry.style,
        color: null,
        packPath: flags.pack ?? DEFAULT_PACK_PATH,
      }),
    }
  })

  if (flags.json) {
    printJson(rows)
    return
  }
  if (flags.svg) {
    process.stdout.write(rows.map((row) => row.svg).join('\n'))
    process.stdout.write('\n')
    return
  }
  for (const row of rows) process.stdout.write(`${row.style}\t${row.name}\n`)
}

export function runCli(argv = []) {
  const [command, ...rest] = argv
  if (!command || command === '--help' || command === '-h') {
    process.stdout.write(usage())
    return
  }

  const { flags, positional } = parseCliArgs(rest)
  switch (command) {
    case 'generate':
      commandGenerate(flags)
      break
    case 'info':
      commandInfo(flags)
      break
    case 'search':
      commandSearch(flags, positional)
      break
    case 'names':
      commandNames(flags)
      break
    case 'get':
      commandGet(flags, positional)
      break
    default:
      fail(`Unknown command: ${command}\n${usage()}`)
  }
}
