#!/usr/bin/env node
import { SKILL_ROOT as skillRoot } from '../../lib/runtime/skill-paths.mjs'
// cli/deckkits/slot-consistency.mjs — DeckKit 槽位渲染覆盖守卫
//
// 检查目标：schema 声明的每个文本槽位都必须能影响 createDeck 的 patch 输出，
// 杜绝 "validate 通过但渲染静默丢弃" 的幽灵槽位（ghost slot）。
//
// 原理：为每个 slideType 构造探针 content，把所有可检查的 string 槽位填入唯一
// 哨兵 token，渲染为 patch 后断言每个哨兵出现在 JSON.stringify(patch) 中。
//
// schema 注解（按需标注，避免误报）：
//   x-slotRole: "control"        布局/匹配控制值（如 calloutHighlights、align），不要求出现在输出文本中
//   x-slotFallbackOf: "<field>"  本槽位是同级 <field> 的回退别名；用移除 <field> 的 solo 探针复验
//   enum 槽位与非 string 槽位自动跳过；无 properties 的 object/array（动态结构）记为 dynamic 并跳过
//   x-slotProbeVariants: [{omit: ['optionalField']}] probes legal alternatives; every field must remain covered.
//   x-slotProbeOmit: true       Omit optional control fields that conflict in a generic probe; never visible text.
//   x-slotProbeValue: value     A valid control value or finite numeric specimen for coupled data constraints; never visible text.
//   x-slotProbeSequence: [...]  Array-item control values by item index; never visible text.
//
// 用法：
//   node <skill-root>/scripts/cli/deckkits/slot-consistency.mjs [--deckkit <id>] [--json]
// 退出码：发现 ghost slot 或渲染失败时为 1，可直接用作 CI / deckkit-examples 门禁。
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const deckkitRoot = join(skillRoot, 'assets', 'deckkits')
const schemasRoot = join(deckkitRoot, 'schemas')

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/slot-consistency.mjs [--deckkit <id>] [--json]

Options:
  --deckkit <id>   Only check this DeckKit. Default: all catalog entries.
  --json           Machine-readable report.
  --help           Show this help.
`

// 这些字段名是公认的控制值（被消费为布局参数/查找键，而不是输出文本）
const CONTROL_FIELD_NAMES = new Set(['key', 'accent', 'color', 'tone', 'id', 'slotId'])

function parseArgs(argv) {
  const args = { deckkit: '', json: false }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--deckkit') {
      args.deckkit = argv[i + 1] ?? ''
      i += 1
    } else if (arg === '--json') {
      args.json = true
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  return args
}

const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'))

function loadSlideSchema(deckkit, slideType) {
  const deckkitSchema = join(deckkitRoot, deckkit, 'schemas', `${slideType}.schema.json`)
  if (existsSync(deckkitSchema)) return readJson(deckkitSchema)
  const globalSchema = join(schemasRoot, `${slideType}.schema.json`)
  if (existsSync(globalSchema)) return readJson(globalSchema)
  return null
}

let tokenCounter = 0
function nextToken() {
  tokenCounter += 1
  // Keep probes inside compact KPI slots, including composed value+unit fields.
  // Base32 excludes the Z terminator, so short tokens cannot match longer tokens.
  return `Q${tokenCounter.toString(32).toUpperCase()}Z`
}

// 返回 { value, sentinels: [{path, token, fallbackOf}], dynamics: [path] }
function buildProbe(schema, basePath) {
  const sentinels = []
  const dynamics = []

  function fillObject(objSchema, path) {
    const out = {}
    for (const [field, fieldSchema] of Object.entries(objSchema.properties ?? {})) {
      if (fieldSchema['x-slotProbeOmit'] === true) {
        if (fieldSchema['x-slotRole'] !== 'control' || objSchema.required?.includes(field))
          throw new Error('Probe-only omissions require optional control fields')
        continue
      }
      const fieldPath = `${path}.${field}`
      const value = fillField(field, fieldSchema, fieldPath)
      if (value !== undefined) out[field] = value
    }
    return out
  }

  function fillField(field, fieldSchema, path, inheritedSlotRole = null) {
    const type = Array.isArray(fieldSchema.type) ? fieldSchema.type[0] : fieldSchema.type
    const slotRole = fieldSchema['x-slotRole'] ?? inheritedSlotRole
    if (Object.hasOwn(fieldSchema, 'x-slotProbeSequence')) {
      const sequence = fieldSchema['x-slotProbeSequence']
      const indices = [...path.matchAll(/\[(\d+)\]/g)]
      if (
        slotRole !== 'control' ||
        !Array.isArray(sequence) ||
        !sequence.length ||
        !indices.length ||
        Object.hasOwn(fieldSchema, 'x-slotProbeValue')
      )
        throw new Error('Probe sequences require an array-item control field and non-empty values')
      const index = Number(indices.at(-1)[1])
      return structuredClone(sequence[index % sequence.length])
    }
    if (Object.hasOwn(fieldSchema, 'x-slotProbeValue')) {
      const value = fieldSchema['x-slotProbeValue']
      const numeric =
        ['number', 'integer'].includes(type) &&
        typeof value === 'number' &&
        Number.isFinite(value) &&
        (type !== 'integer' || Number.isInteger(value))
      if (slotRole !== 'control' && !numeric)
        throw new Error('Probe values require control fields or finite numeric data')
      return structuredClone(fieldSchema['x-slotProbeValue'])
    }
    if (Object.hasOwn(fieldSchema, 'const')) return fieldSchema.const
    if (fieldSchema.enum) return fieldSchema.enum[0]
    if (type === 'string') {
      if (slotRole === 'control' || CONTROL_FIELD_NAMES.has(field)) {
        return `probe-${field}`
      }
      const token = nextToken()
      sentinels.push({ path, token, fallbackOf: fieldSchema['x-slotFallbackOf'] ?? null })
      return token
    }
    if (type === 'number' || type === 'integer') {
      let value = Math.max(1, fieldSchema.minimum ?? -Infinity)
      if (fieldSchema.exclusiveMinimum !== undefined && value <= fieldSchema.exclusiveMinimum)
        value = fieldSchema.exclusiveMinimum + 1
      if (fieldSchema.maximum !== undefined) value = Math.min(value, fieldSchema.maximum)
      return type === 'integer' ? Math.ceil(value) : value
    }
    if (type === 'boolean') return false
    if (type === 'array') {
      const itemSchema = fieldSchema.items
      if (!itemSchema) {
        dynamics.push(path)
        return []
      }
      const min = fieldSchema.minItems ?? 0
      const max = fieldSchema.maxItems ?? Infinity
      const count = max === 0 ? 0 : Math.max(Math.min(2, max), min, 1)
      if (Array.isArray(itemSchema)) {
        return itemSchema.map((tupleSchema, i) =>
          fillField(`${field}${i}`, tupleSchema, `${path}[${i}]`, slotRole),
        )
      }
      return Array.from({ length: count }, (_, i) =>
        fillField(field, itemSchema, `${path}[${i}]`, slotRole),
      )
    }
    if (type === 'object') {
      if (fieldSchema.properties) return fillObject(fieldSchema, path)
      dynamics.push(path)
      return {}
    }
    dynamics.push(path)
    return undefined
  }

  const value = fillObject(schema, basePath)
  return { value, sentinels, dynamics }
}

function renderPatchText(mod, deckkit, slideType, data) {
  const result = mod.createDeck({
    meta: { deckkit, designScope: 'excerpt' },
    slides: [{ type: slideType, data }],
  })
  return JSON.stringify(result?.patch ?? result)
}

function checkProbe(mod, deckkit, slideType, schema) {
  // Tokens need uniqueness only within this rendered probe. Compact figure labels
  // must be exercised with realistic text rather than a six-character fixture.
  tokenCounter = 0
  const { value, sentinels, dynamics } = buildProbe(schema, 'data')
  let text
  try {
    text = renderPatchText(mod, deckkit, slideType, value)
  } catch (error) {
    return { slideType, status: 'render-error', error: error.message, ghosts: [], dynamics }
  }
  const ghosts = []
  for (const sentinel of sentinels) {
    if (text.includes(sentinel.token)) continue
    if (sentinel.fallbackOf) {
      const soloData = structuredClone(value)
      const nested = sentinel.fallbackOf.match(/^([A-Za-z0-9_]+)\[\]\.([A-Za-z0-9_]+)$/)
      if (nested) {
        const arr = soloData[nested[1]]
        if (Array.isArray(arr)) for (const item of arr) delete item?.[nested[2]]
      } else delete soloData[sentinel.fallbackOf]
      try {
        if (renderPatchText(mod, deckkit, slideType, soloData).includes(sentinel.token)) continue
      } catch {
        /* report the ghost */
      }
    }
    ghosts.push(sentinel.path)
  }
  return { slideType, status: ghosts.length ? 'ghost-slots' : 'ok', ghosts, dynamics }
}

async function checkDeckkit(entry) {
  const mod = await import(pathToFileURL(join(deckkitRoot, entry.path)).href)
  if (typeof mod.createDeck !== 'function')
    return { deckkit: entry.id, error: 'no createDeck export', slideTypes: [] }
  const report = []
  for (const slideType of entry.supportedSlideTypes ?? []) {
    const schema = loadSlideSchema(entry.id, slideType)
    if (!schema) {
      report.push({ slideType, status: 'no-schema', ghosts: [], dynamics: [] })
      continue
    }
    const variants = schema['x-slotProbeVariants'] ?? [{ omit: [] }]
    try {
      const covered = new Set()
      if (!Array.isArray(variants) || !variants.length)
        throw new Error('Slot probe variants must be a non-empty array')
      const probes = variants
        .map((variant) => {
          const selected = structuredClone(schema)
          for (const key of variant.omit ?? []) {
            if (!selected.properties[key] || selected.required?.includes(key))
              throw new Error('Probe omissions must name optional top-level fields')
            delete selected.properties[key]
          }
          for (const key of Object.keys(selected.properties)) covered.add(key)
          return expandProbeSchemas(selected).map((branch) =>
            checkProbe(mod, entry.id, slideType, branch),
          )
        })
        .flat()
      if (Object.keys(schema.properties).some((key) => !covered.has(key)))
        throw new Error('Every declared field needs at least one probe variant')
      const failure = probes.find((p) => p.status !== 'ok')
      report.push({
        slideType,
        status: failure?.status ?? 'ok',
        ...(failure?.error ? { error: failure.error } : {}),
        ghosts: [...new Set(probes.flatMap((p) => p.ghosts))],
        dynamics: [...new Set(probes.flatMap((p) => p.dynamics))],
        ...(probes.length > 1 ? { probeVariants: probes.length } : {}),
      })
    } catch (error) {
      report.push({
        slideType,
        status: 'probe-config-error',
        error: error.message,
        ghosts: [],
        dynamics: [],
      })
    }
  }
  return { deckkit: entry.id, slideTypes: report }
}

// Probe every discriminated branch, keeping visible fields in their legal context.
function expandProbeSchemas(schema) {
  if (!schema || typeof schema !== 'object') return [schema]
  if (schema.oneOf) {
    const { oneOf, ...base } = schema
    return oneOf.flatMap((branch) =>
      expandProbeSchemas({
        ...base,
        ...branch,
        required: [...new Set([...(base.required ?? []), ...(branch.required ?? [])])],
        properties: Object.fromEntries(
          Object.entries({ ...base.properties, ...branch.properties })
            .filter(([, value]) => value !== false)
            .map(([key, value]) => [
              key,
              typeof value === 'object'
                ? {
                    ...base.properties?.[key],
                    ...value,
                    ...(value.properties
                      ? {
                          properties: {
                            ...base.properties?.[key]?.properties,
                            ...value.properties,
                          },
                        }
                      : {}),
                  }
                : value,
            ]),
        ),
      }),
    )
  }
  const properties = Object.fromEntries(
    Object.entries(schema.properties ?? {}).filter(([, value]) => value !== false),
  )
  let variants = [{ ...schema, ...(schema.properties ? { properties } : {}) }]
  for (const [key, value] of Object.entries(properties)) {
    const alternatives = expandProbeSchemas(value)
    variants = variants.flatMap((variant) =>
      alternatives.map((child) => ({
        ...variant,
        properties: { ...variant.properties, [key]: child },
      })),
    )
  }
  if (schema.items && !Array.isArray(schema.items))
    variants = variants.flatMap((variant) =>
      expandProbeSchemas(schema.items).map((items) => ({ ...variant, items })),
    )
  return variants
}

try {
  const args = parseArgs(process.argv.slice(2))
  const catalog = readJson(join(deckkitRoot, 'catalog.json'))
  const entries = catalog.entries.filter((entry) => !args.deckkit || entry.id === args.deckkit)
  if (entries.length === 0) {
    throw new Error(
      `DeckKit "${args.deckkit}" not found. Available: ${catalog.entries.map((e) => e.id).join(', ')}`,
    )
  }
  const results = []
  for (const entry of entries) {
    results.push(await checkDeckkit(entry))
  }
  const failed = results.some(
    (kit) =>
      kit.error || kit.slideTypes.some((slide) => !['ok', 'no-schema'].includes(slide.status)),
  )
  if (args.json) {
    process.stdout.write(`${JSON.stringify({ ok: !failed, results }, null, 2)}\n`)
  } else {
    for (const kit of results) {
      console.log(`# ${kit.deckkit}`)
      if (kit.error) {
        console.log(`  [error] ${kit.error}`)
        continue
      }
      for (const slide of kit.slideTypes) {
        if (slide.status === 'ok') {
          const dyn =
            slide.dynamics.length > 0 ? ` (dynamic skipped: ${slide.dynamics.join(', ')})` : ''
          console.log(`  ok            ${slide.slideType}${dyn}`)
        } else if (slide.status === 'no-schema') {
          console.log(`  no-schema     ${slide.slideType}`)
        } else if (slide.status === 'render-error') {
          console.log(`  render-error  ${slide.slideType}: ${slide.error}`)
        } else if (slide.status === 'probe-config-error') {
          console.log(`  config-error  ${slide.slideType}: ${slide.error}`)
        } else {
          console.log(`  GHOST-SLOTS   ${slide.slideType}: ${slide.ghosts.join(', ')}`)
        }
      }
    }
    console.log(
      failed
        ? '\nFAILED: ghost slots or render errors found.'
        : '\nAll declared slots reach the rendered patch.',
    )
  }
  process.exit(failed ? 1 : 0)
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(1)
}
