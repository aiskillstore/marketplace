#!/usr/bin/env node
import { SKILL_ROOT as skillRoot } from '../../lib/runtime/skill-paths.mjs'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { summarizeSlotBudgetFit } from '../../../assets/deckkits/shared/core-primitives.kit.mjs'

const deckkitRoot = join(skillRoot, 'assets', 'deckkits')
const schemasRoot = join(deckkitRoot, 'schemas')

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/slots.mjs --deckkit <id> [--format md|json]

Options:
  --deckkit <id>   DeckKit id from assets/deckkits/catalog.json.
  --format <fmt>   Output format: md (default) or json.
  --help           Show this help.
`

function parseArgs(argv) {
  const args = { deckkit: '', format: 'md' }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--deckkit') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--format') {
      args.format = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.deckkit) throw new Error(`--deckkit is required\n\n${usage}`)
  if (!['md', 'json'].includes(args.format)) throw new Error(`Unsupported --format ${args.format}`)
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'))

function loadCatalog() {
  return readJson(join(deckkitRoot, 'catalog.json'))
}

function loadSlideSchema(deckkit, slideType) {
  const deckkitSchema = join(deckkitRoot, deckkit, 'schemas', `${slideType}.schema.json`)
  if (existsSync(deckkitSchema)) return readJson(deckkitSchema)
  const globalSchema = join(schemasRoot, `${slideType}.schema.json`)
  if (existsSync(globalSchema)) return readJson(globalSchema)
  return null
}

function hasRequired(contract, path) {
  return new Set(contract?.requiredSlots ?? []).has(path)
}

function normalizeAssetSlots(contract) {
  const slots = contract?.assetSlots
  if (!slots || typeof slots !== 'object' || Array.isArray(slots)) return []
  return Object.entries(slots).map(([id, details]) => ({
    ...(details && typeof details === 'object' && !Array.isArray(details)
      ? details
      : { note: String(details ?? '') }),
    id,
  }))
}

function budgetSummary(schema = {}) {
  const budget = schema['x-slotBudget'] ?? {}
  const parts = []
  if (schema.minItems !== undefined || schema.maxItems !== undefined) {
    const min = schema.minItems ?? ''
    const max = schema.maxItems ?? ''
    parts.push(`items ${min || '?'}-${max || '?'}`)
  }
  if (budget.maxItems !== undefined) parts.push(`max ${budget.maxItems} items`)
  if (schema.maxLength !== undefined) parts.push(`max ${schema.maxLength} chars`)
  if (budget.maxChars !== undefined) parts.push(`~${budget.maxChars} chars`)
  if (budget.maxLines !== undefined) parts.push(`~${budget.maxLines} line(s)`)
  if (
    budget.fontPt !== undefined &&
    (budget.widthIn !== undefined || budget.widthPt !== undefined)
  ) {
    const width = budget.widthIn !== undefined ? `${budget.widthIn}in` : `${budget.widthPt}pt`
    const height =
      budget.heightIn !== undefined
        ? `${budget.heightIn}in`
        : budget.heightPt !== undefined
          ? `${budget.heightPt}pt`
          : ''
    parts.push(`${budget.fontPt}pt @ ${height ? `${width} x ${height}` : width}`)
    const fit = summarizeSlotBudgetFit(budget)
    if (fit.cjkCharsPerLine !== null) {
      const lineText = fit.safeLines !== null ? ` x ${fit.safeLines} line(s)` : ''
      parts.push(`CJK ~${fit.cjkCharsPerLine} chars${lineText}`)
    }
  }
  return parts.join('; ')
}

function schemaType(schema = {}) {
  return Array.isArray(schema.type) ? schema.type.join('|') : (schema.type ?? '')
}

function pushSchemaRow(rows, path, schema) {
  rows.push({
    path,
    type: schemaType(schema),
    budget: budgetSummary(schema),
    description: schema.description ?? '',
  })
}

function collectNestedRows(schema, path, rows) {
  if (schema.type === 'object' && schema.properties) collectSchemaRows(schema, path, rows)
  if (schema.type === 'array') collectArrayItemRows(schema, path, rows)
}

function collectArrayItemRows(schema, path, rows) {
  const itemSchema = schema.items
  if (!itemSchema) return
  if (itemSchema.properties) {
    collectSchemaRows(itemSchema, `${path}[]`, rows)
    return
  }
  if (Array.isArray(itemSchema)) {
    itemSchema.forEach((tupleSchema, index) => {
      const tuplePath = `${path}[${index}]`
      pushSchemaRow(rows, tuplePath, tupleSchema)
      collectNestedRows(tupleSchema, tuplePath, rows)
    })
    return
  }
  if (itemSchema.type === 'array') collectArrayItemRows(itemSchema, `${path}[]`, rows)
}

function collectSchemaRows(schema, basePath = 'data', rows = []) {
  if (!schema?.properties) return rows
  for (const [field, fieldSchema] of Object.entries(schema.properties)) {
    const path = `${basePath}.${field}`
    pushSchemaRow(rows, path, fieldSchema)
    if (fieldSchema.type === 'object' && fieldSchema.properties) {
      collectSchemaRows(fieldSchema, path, rows)
    }
    if (fieldSchema.type === 'array') collectArrayItemRows(fieldSchema, path, rows)
  }
  return rows
}

function buildReference(deckkit) {
  const catalog = loadCatalog()
  const entry = catalog.entries.find((item) => item.id === deckkit)
  if (!entry) {
    throw new Error(
      `DeckKit "${deckkit}" not found. Available: ${catalog.entries.map((e) => e.id).join(', ')}`,
    )
  }
  const slideTypes =
    entry.supportedSlideTypes ?? Object.keys(entry.layoutContract?.slideTypes ?? {})
  return {
    deckkit,
    readiness: entry.readiness ?? '',
    qualityProfile: entry.qualityProfile ?? {},
    slideTypes: slideTypes.map((slideType) => {
      const schema = loadSlideSchema(deckkit, slideType)
      const contract = entry.layoutContract?.slideTypes?.[slideType] ?? {}
      const rows = collectSchemaRows(schema)
      return {
        slideType,
        hasSchema: Boolean(schema),
        requiredSlots: contract.requiredSlots ?? [],
        assetSlots: normalizeAssetSlots(contract),
        rows: rows.map((row) => ({
          ...row,
          required: hasRequired(contract, row.path),
        })),
      }
    }),
  }
}

function escapeCell(value) {
  return String(value ?? '')
    .replace(/\|/g, '\\|')
    .replace(/\n/g, '<br>')
}

function renderMarkdown(ref) {
  const lines = [
    `# ${ref.deckkit} DeckKit Slot Reference`,
    '',
    `Readiness: ${ref.readiness || 'unknown'}`,
    '',
  ]
  for (const slide of ref.slideTypes) {
    lines.push(`## ${slide.slideType}`)
    lines.push('')
    if (!slide.hasSchema) {
      lines.push('_No per-slide schema found; only catalog required slots are available._')
      lines.push('')
    }
    lines.push('| slot | required | type | budget | notes |')
    lines.push('| --- | --- | --- | --- | --- |')
    if (slide.rows.length === 0) {
      for (const slot of slide.requiredSlots) {
        lines.push(`| \`${escapeCell(slot)}\` | yes |  |  | catalog contract |`)
      }
    } else {
      for (const row of slide.rows) {
        lines.push(
          `| \`${escapeCell(row.path)}\` | ${row.required ? 'yes' : ''} | ${escapeCell(row.type)} | ${escapeCell(row.budget)} | ${escapeCell(row.description)} |`,
        )
      }
    }
    lines.push('')
    if (slide.assetSlots.length > 0) {
      lines.push('### Asset slots')
      lines.push('')
      lines.push(
        '| asset slot | kind | accepts asset | placeholder behavior | label/caption slots | notes |',
      )
      lines.push('| --- | --- | --- | --- | --- | --- |')
      for (const slot of slide.assetSlots) {
        const labelSlots = [slot.labelSlot, slot.captionSlot].filter(Boolean).join('<br>')
        lines.push(
          `| \`${escapeCell(slot.id)}\` | ${escapeCell(slot.kind ?? '')} | ${
            slot.acceptsAsset === true ? 'yes' : 'no'
          } | ${escapeCell(slot.placeholderBehavior ?? '')} | ${escapeCell(labelSlots)} | ${escapeCell(
            slot.note ?? slot.description ?? '',
          )} |`,
        )
      }
      lines.push('')
    }
  }
  return `${lines.join('\n').trimEnd()}\n`
}

try {
  const args = parseArgs(process.argv.slice(2))
  const ref = buildReference(args.deckkit)
  process.stdout.write(
    args.format === 'json' ? `${JSON.stringify(ref, null, 2)}\n` : renderMarkdown(ref),
  )
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(1)
}
