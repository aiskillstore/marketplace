#!/usr/bin/env node
import { inflateRawSync } from 'node:zlib'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { writeJsonOutput } from '../../lib/runtime/output-files.mjs'

const SCHEMA_VERSION = 'pptx-nova-structure-check/v1'

const usage =
  'Usage:\n' +
  '  node <skill-root>/scripts/cli/review/structure-check.mjs --pptx out.pptx [options]\n\n' +
  'Options:\n' +
  '  --pptx <path>           Required PPTX file to inspect.\n' +
  '  --deck-lock <path>      Optional deck_lock.json for expected fonts/colors.\n' +
  '  --expected-font <name>  Repeatable expected font name.\n' +
  '  --expected-color <hex>  Repeatable expected sRGB color without #.\n' +
  '  --strict-fonts          Missing expected fonts are errors instead of warnings.\n' +
  '  --strict-colors         Missing expected colors are errors instead of warnings.\n' +
  '  --strict-placeholders   Empty placeholder residue is an error instead of a warning.\n' +
  '  --output <path>         Output path. Defaults to structure-check.json in cwd.\n' +
  '  --overwrite             Replace an existing current-run report.\n' +
  '  --json                  Print structure-check.json to stdout.\n' +
  '  --help                  Show this help.\n\n' +
  'This helper performs lightweight OOXML structure checks for generated PPTX files.\n' +
  'It scans XML inside the PPTX ZIP for font declarations, sRGB/theme color use,\n' +
  'and empty placeholder residue. It is not a full OOXML validator.\n'

function parseArgs(argv) {
  const args = {
    pptx: '',
    deckLock: '',
    expectedFonts: [],
    expectedColors: [],
    strictFonts: false,
    strictColors: false,
    strictPlaceholders: false,
    output: resolve('structure-check.json'),
    overwrite: false,
    json: false,
  }
  const flags = {
    '--pptx': 'pptx',
    '--deck-lock': 'deckLock',
    '--output': 'output',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--json') {
      args.json = true
      continue
    }
    if (arg === '--overwrite') {
      args.overwrite = true
      continue
    }
    if (arg === '--strict-fonts') {
      args.strictFonts = true
      continue
    }
    if (arg === '--strict-colors') {
      args.strictColors = true
      continue
    }
    if (arg === '--strict-placeholders') {
      args.strictPlaceholders = true
      continue
    }
    if (arg === '--expected-font') {
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error('--expected-font requires a value')
      args.expectedFonts.push(value)
      index += 1
      continue
    }
    if (arg === '--expected-color') {
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error('--expected-color requires a value')
      args.expectedColors.push(value)
      index += 1
      continue
    }
    const key = flags[arg]
    const value = argv[index + 1]
    if (!key) throw new Error('Unknown option: ' + arg + '\n\n' + usage)
    if (!value || value.startsWith('--')) throw new Error(arg + ' requires a value')
    args[key] = resolve(value)
    index += 1
  }
  if (!args.pptx) throw new Error('--pptx is required\n\n' + usage)
  return args
}

function readJson(path, label) {
  if (!path) return null
  if (!existsSync(path)) throw new Error(label + ' does not exist: ' + path)
  return JSON.parse(readFileSync(path, 'utf8'))
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function issue(target, level, code, message, details = {}) {
  const item = { severity: level, code, message, ...details }
  target[level === 'error' ? 'errors' : 'warnings'].push(item)
}

function normalizeFont(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
}

function normalizeColor(value) {
  const color = String(value ?? '')
    .replace(/^#/, '')
    .trim()
    .toUpperCase()
  return /^[0-9A-F]{6}$/.test(color) ? color : ''
}

function unique(values) {
  return [...new Set(values.filter(Boolean))]
}

function collectLockFonts(lock) {
  const fonts = []
  const scanFontValue = (value) => {
    if (!value) return
    if (typeof value === 'string') {
      const first = value
        .split(',')[0]
        .trim()
        .replace(/^['"]|['"]$/g, '')
      if (first) fonts.push(first)
      return
    }
    if (Array.isArray(value)) {
      value.forEach(scanFontValue)
      return
    }
  }
  const typography = isPlainObject(lock?.typography) ? lock.typography : {}
  for (const key of ['title', 'body', 'code', 'mathFont', 'caption', 'label']) {
    scanFontValue(typography[key])
  }
  const scanFontObject = (value) => {
    if (!value) return
    if (typeof value === 'string' || Array.isArray(value)) {
      scanFontValue(value)
      return
    }
    if (isPlainObject(value)) {
      for (const item of Object.values(value)) scanFontObject(item)
    }
  }
  scanFontObject(lock?.fonts)
  scanFontObject(lock?.themePack?.fonts)
  return unique(fonts.map(normalizeFont))
}

function collectLockColors(lock) {
  const colors = []
  const scan = (value) => {
    if (!value) return
    if (typeof value === 'string') {
      const color = normalizeColor(value)
      if (color) colors.push(color)
      return
    }
    if (Array.isArray(value)) {
      value.forEach(scan)
      return
    }
    if (isPlainObject(value)) {
      for (const item of Object.values(value)) scan(item)
    }
  }
  scan(lock?.colors)
  scan(lock?.themePack?.colors)
  scan(lock?.brand?.colors)
  return unique(colors.map(normalizeColor))
}

function findEndOfCentralDirectory(buffer) {
  for (let offset = buffer.length - 22; offset >= 0; offset -= 1) {
    if (buffer.readUInt32LE(offset) === 0x06054b50) return offset
  }
  throw new Error('PPTX ZIP end of central directory was not found')
}

function readZipEntries(path) {
  const buffer = readFileSync(path)
  const eocd = findEndOfCentralDirectory(buffer)
  const entryCount = buffer.readUInt16LE(eocd + 10)
  const centralOffset = buffer.readUInt32LE(eocd + 16)
  const entries = []
  let cursor = centralOffset
  for (let index = 0; index < entryCount; index += 1) {
    if (buffer.readUInt32LE(cursor) !== 0x02014b50) {
      throw new Error('Invalid ZIP central directory entry at ' + cursor)
    }
    const method = buffer.readUInt16LE(cursor + 10)
    const compressedSize = buffer.readUInt32LE(cursor + 20)
    const uncompressedSize = buffer.readUInt32LE(cursor + 24)
    const fileNameLength = buffer.readUInt16LE(cursor + 28)
    const extraLength = buffer.readUInt16LE(cursor + 30)
    const commentLength = buffer.readUInt16LE(cursor + 32)
    const localOffset = buffer.readUInt32LE(cursor + 42)
    const name = buffer.toString('utf8', cursor + 46, cursor + 46 + fileNameLength)
    cursor += 46 + fileNameLength + extraLength + commentLength
    if (buffer.readUInt32LE(localOffset) !== 0x04034b50) {
      throw new Error('Invalid ZIP local file header for ' + name)
    }
    const localNameLength = buffer.readUInt16LE(localOffset + 26)
    const localExtraLength = buffer.readUInt16LE(localOffset + 28)
    const dataStart = localOffset + 30 + localNameLength + localExtraLength
    const compressed = buffer.subarray(dataStart, dataStart + compressedSize)
    let data
    if (method === 0) data = compressed
    else if (method === 8) data = inflateRawSync(compressed)
    else continue
    if (uncompressedSize !== 0 && data.length !== uncompressedSize) {
      throw new Error('ZIP entry size mismatch for ' + name)
    }
    entries.push({ name, data })
  }
  return entries
}

function xmlEntries(entries) {
  return entries
    .filter((entry) => entry.name.endsWith('.xml'))
    .map((entry) => ({ name: entry.name, xml: entry.data.toString('utf8') }))
}

function collectFonts(xmlFiles) {
  const fonts = []
  const typeface = /\btypeface="([^"]+)"/g
  for (const file of xmlFiles) {
    for (const match of file.xml.matchAll(typeface)) {
      const font = normalizeFont(match[1])
      if (font && font !== '+mj-lt' && font !== '+mn-lt') fonts.push(font)
    }
  }
  return unique(fonts)
}

function collectColors(xmlFiles) {
  const srgb = []
  const scheme = []
  const srgbRegex = /<a:srgbClr\b[^>]*\bval="([0-9A-Fa-f]{6})"/g
  const schemeRegex = /<a:schemeClr\b[^>]*\bval="([^"]+)"/g
  for (const file of xmlFiles) {
    for (const match of file.xml.matchAll(srgbRegex)) srgb.push(normalizeColor(match[1]))
    for (const match of file.xml.matchAll(schemeRegex)) scheme.push(match[1])
  }
  return { srgb: unique(srgb), scheme: unique(scheme) }
}

function textOfShape(shapeXml) {
  const texts = []
  for (const match of shapeXml.matchAll(/<a:t>([\s\S]*?)<\/a:t>/g)) {
    texts.push(match[1].replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&'))
  }
  return texts.join('').trim()
}

function collectPlaceholders(xmlFiles) {
  const placeholders = []
  const slideFiles = xmlFiles.filter((file) => /^ppt\/slides\/slide\d+\.xml$/.test(file.name))
  for (const file of slideFiles) {
    const shapes = file.xml.match(/<p:sp\b[\s\S]*?<\/p:sp>/g) ?? []
    shapes.forEach((shapeXml, index) => {
      if (!/<p:ph\b/.test(shapeXml)) return
      const text = textOfShape(shapeXml)
      const placeholderText = /click to|单击|点击|添加标题|add title|add text/i.test(text)
      placeholders.push({
        file: file.name,
        shapeIndex: index,
        text,
        empty: text.length === 0,
        placeholderText,
      })
    })
  }
  return placeholders
}

function addCheck(report, name, status, details = {}) {
  report.checks.push({ name, status, ...details })
}

function makeReport(args) {
  const lock = readJson(args.deckLock, 'deck_lock.json')
  const expectedFonts = unique([
    ...args.expectedFonts.map(normalizeFont),
    ...collectLockFonts(lock),
  ])
  const expectedColors = unique([
    ...args.expectedColors.map(normalizeColor),
    ...collectLockColors(lock),
  ])
  const entries = readZipEntries(args.pptx)
  const xmlFiles = xmlEntries(entries)
  const fonts = collectFonts(xmlFiles)
  const colors = collectColors(xmlFiles)
  const placeholders = collectPlaceholders(xmlFiles)
  const emptyPlaceholders = placeholders.filter((item) => item.empty || item.placeholderText)
  const report = {
    schemaVersion: SCHEMA_VERSION,
    status: 'pass',
    artifacts: {
      pptx: args.pptx,
      deckLock: args.deckLock || null,
    },
    summary: {
      zipEntries: entries.length,
      xmlFiles: xmlFiles.length,
      expectedFonts: expectedFonts.length,
      fontsFound: fonts.length,
      expectedColors: expectedColors.length,
      srgbColorsFound: colors.srgb.length,
      schemeColorsFound: colors.scheme.length,
      placeholders: {
        total: placeholders.length,
        emptyOrDefaultText: emptyPlaceholders.length,
      },
      errors: 0,
      warnings: 0,
    },
    checks: [],
    fonts: { expected: expectedFonts, found: fonts },
    colors: { expected: expectedColors, srgb: colors.srgb, scheme: colors.scheme },
    placeholders,
    errors: [],
    warnings: [],
  }

  if (xmlFiles.length === 0) {
    issue(report, 'error', 'pptx-xml-missing', 'PPTX has no XML entries to inspect')
  }

  const missingFonts = expectedFonts.filter((font) => !fonts.includes(font))
  if (expectedFonts.length === 0) {
    issue(
      report,
      'warning',
      'expected-fonts-undisclosed',
      'No expected fonts were provided or found in deck_lock',
    )
    addCheck(report, 'font-xml', 'warning', { expected: expectedFonts, found: fonts })
  } else if (missingFonts.length > 0) {
    issue(
      report,
      args.strictFonts ? 'error' : 'warning',
      'expected-fonts-missing',
      'Expected fonts were not found in PPTX XML',
      { missingFonts },
    )
    addCheck(report, 'font-xml', args.strictFonts ? 'failed' : 'warning', {
      missingFonts,
      found: fonts,
    })
  } else {
    addCheck(report, 'font-xml', 'passed', { expected: expectedFonts, found: fonts })
  }

  const missingColors = expectedColors.filter((color) => !colors.srgb.includes(color))
  if (expectedColors.length === 0) {
    issue(
      report,
      'warning',
      'expected-colors-undisclosed',
      'No expected sRGB colors were provided or found in deck_lock',
    )
    addCheck(report, 'theme-color-xml', 'warning', {
      expected: expectedColors,
      srgb: colors.srgb,
      scheme: colors.scheme,
    })
  } else if (missingColors.length > 0) {
    issue(
      report,
      args.strictColors ? 'error' : 'warning',
      'expected-colors-missing',
      'Expected sRGB colors were not found in PPTX XML',
      { missingColors },
    )
    addCheck(report, 'theme-color-xml', args.strictColors ? 'failed' : 'warning', {
      missingColors,
      srgb: colors.srgb,
      scheme: colors.scheme,
    })
  } else {
    addCheck(report, 'theme-color-xml', 'passed', {
      expected: expectedColors,
      srgb: colors.srgb,
      scheme: colors.scheme,
    })
  }

  if (emptyPlaceholders.length > 0) {
    issue(
      report,
      args.strictPlaceholders ? 'error' : 'warning',
      'placeholder-residue',
      'Empty or default-text placeholders remain in slide XML',
      { count: emptyPlaceholders.length },
    )
    addCheck(report, 'placeholder-residue', args.strictPlaceholders ? 'failed' : 'warning', {
      count: emptyPlaceholders.length,
      items: emptyPlaceholders,
    })
  } else {
    addCheck(report, 'placeholder-residue', 'passed', { count: 0 })
  }

  report.summary.errors = report.errors.length
  report.summary.warnings = report.warnings.length
  report.status = report.errors.length > 0 ? 'fail' : report.warnings.length > 0 ? 'warn' : 'pass'
  return report
}

try {
  const args = parseArgs(process.argv.slice(2))
  if (!existsSync(args.pptx)) throw new Error('PPTX does not exist: ' + args.pptx)
  const report = makeReport(args)
  writeJsonOutput(args.output, report, {
    overwrite: args.overwrite,
    label: 'structure check output',
  })
  if (args.json) process.stdout.write(JSON.stringify(report, null, 2) + '\n')
  else {
    process.stdout.write('pptx-nova structure check: ' + report.status + '\n')
    process.stdout.write('- xml files: ' + report.summary.xmlFiles + '\n')
    process.stdout.write('- expected fonts: ' + report.summary.expectedFonts + '\n')
    process.stdout.write('- expected colors: ' + report.summary.expectedColors + '\n')
    process.stdout.write(
      '- placeholder residue: ' + report.summary.placeholders.emptyOrDefaultText + '\n',
    )
    process.stdout.write('- report: ' + args.output + '\n')
  }
  if (report.status === 'fail') process.exitCode = 1
} catch (error) {
  process.stderr.write(error.message + '\n')
  process.exitCode = 1
}
