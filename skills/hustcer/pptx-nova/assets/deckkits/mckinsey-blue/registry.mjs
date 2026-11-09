import { readFileSync } from 'node:fs'
import { compileMckLayout, resolveMckDeck } from './layouts.mjs'

export const MCK_LAYOUTS = {
  cover: { split: ['hero', 'details', 'metrics'], band: ['hero', 'details', 'metrics'] },
  snapshot: { stacked: ['metrics', 'cohort', 'notes'], rail: ['metrics', 'cohort', 'notes'] },
  profile: {
    quadrants: ['age', 'income', 'occupation', 'interests'],
    bands: ['age', 'income', 'occupation', 'interests'],
  },
  matrix: { rail: ['plot', 'detail'], reversed: ['plot', 'detail'] },
  drivers: { rail: ['chart', 'actions', 'summary'], wide: ['chart', 'actions', 'summary'] },
  pillars: { columns: ['items'], rows: ['items'] },
  initiatives: { columns: ['items'], ledger: ['items'] },
  roadmap: {
    horizontal: ['phases', 'metrics', 'governance'],
    vertical: ['phases', 'metrics', 'governance'],
  },
}
function assertMck(design, { assertFrame }) {
  const b = design.mck,
    seen = new Set()
  if (Object.keys(b.families).length !== 8) throw Error('McKinsey requires all eight roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = MCK_LAYOUTS[f.role]
    if (!type.startsWith('mck') || !expected || seen.has(f.role)) {
      throw Error(`${type}: unknown or duplicate McKinsey role`)
    }
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|')) {
      throw Error(`${type}: unregistered layouts`)
    }
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|')) {
        throw Error(`${type}.${id}: unregistered regions`)
      }
      for (const [key, frame] of Object.entries(v.regions)) {
        assertFrame(design, frame, `${type}.${id}.${key}`)
      }
    }
  }
  for (const key of [
    'hero',
    'title',
    'subtitle',
    'heading',
    'body',
    'small',
    'label',
    'source',
    'metric',
    'kpi',
    'index',
  ]) {
    const st = b.styles[key]
    if (!st || !design.colors[st.color] || !design.fonts[st.role] || st.italic) {
      throw Error(`${key}: registered upright font/color required`)
    }
  }
  for (const [key, f] of Object.entries(b.chrome)) assertFrame(design, f, `mck.chrome.${key}`)
  for (const [key, c] of Object.entries(b.capacity)) {
    if (c.length !== 2 || c.some((x) => !Number.isInteger(x) || x < 1) || c[1] < c[0]) {
      throw Error(`${key}: invalid McKinsey capacity`)
    }
  }
}
function checkMck(design, op, fail) {
  if (op.op === 'add-chart' && (op.kind !== 'bar' || op.variant !== 'clustered')) {
    fail('McKinsey registers only native clustered bar charts')
  }
  if (op.op === 'add-shape' && !['rectangle', 'oval'].includes(op.kind)) {
    fail('Unregistered McKinsey shape')
  }
  if (op.op === 'add-freeform' && !op.name?.endsWith('_HeroCut')) {
    fail('Only the registered cover cut is allowed')
  }
  if (op.op === 'set-shape' && op.fill?.type === 'gradient' && !op.shape?.name?.endsWith('_Hero'))
    fail('Gradient belongs to the cover hero only')
  if (op.op === 'add-group') fail('No registered grouped component')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('McKinsey requires white paper')
  const walk = (v, k = '') => {
    if (!v || typeof v !== 'object') return
    if (k === 'font' && v.italic) fail('McKinsey type must be upright')
    if (k === 'fill' && ['picture', 'pattern'].includes(v.type)) {
      fail('No registered texture fill')
    }
    for (const [key, c] of Object.entries(v)) walk(c, key)
  }
  walk(op)
}
function probe(schema) {
  if (schema['x-slotProbeValue'] !== undefined) return schema['x-slotProbeValue']
  if (schema.enum) return schema.enum[0]
  if (schema.type === 'object') {
    return Object.fromEntries(Object.entries(schema.properties).map(([k, v]) => [k, probe(v)]))
  }
  if (schema.type === 'array') {
    return Array.from({ length: schema.maxItems ?? schema.minItems ?? 1 }, () =>
      probe(schema.items),
    )
  }
  if (schema.type === 'number') {
    return Math.min(
      schema.maximum ?? Infinity,
      Math.max(1, schema.minimum ?? 0, (schema.exclusiveMinimum ?? 0) + 1),
    )
  }
  return 'x'
}
export function mckProjectedBudgets(design, family) {
  const type = Object.keys(design.mck.families).find((k) => design.mck.families[k] === family),
    schema = JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url))),
    data = probe(schema),
    budgets = {}
  if (family.role === 'matrix') {
    data.bubbles.forEach((v, i) => {
      v.x = 0.14 + i * 0.17
      v.y = i % 2 ? 0.68 : 0.26
      v.weight = 1
    })
  }
  const add = (path, frame, style) => {
    if (!path?.startsWith('data.')) return
    const key = path.slice(5).replace(/\[\d+\]/g, '[]')
    let node = schema
    for (const part of key.replaceAll('[]', '.[]').split('.')) {
      node = part === '[]' ? node?.items : node?.properties?.[part]
    }
    if (!node || node.type !== 'string' || node['x-slotRole'] === 'control') return
    const v = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(1, Math.floor(((frame[3] - 0.025) * 72) / (style.sizePt * 1.5))),
    }
    if (!budgets[key] || v.widthIn < budgets[key].widthIn) budgets[key] = v
  }
  // Publish the broadest supported composition's hint; actual combinations still run the resolver.
  for (const [id, v] of Object.entries(family.variants)) {
    let components
    try {
      components = compileMckLayout(design, family, id, v, data)
    } catch {
      continue
    }
    for (const c of components) {
      if (c.style) {
        for (const path of c.paths ?? [c.path]) {
          add(path, c.allocatedFrame ?? c.frame, c.style)
        }
      }
      if (c.kind === 'chart') {
        for (const item of c.inputPaths ?? []) {
          add(
            item,
            [0, 0, c.frame[2] * 0.35, c.frame[3] / c.data.categories.length],
            design.mck.styles.small,
          )
        }
      }
      if (c.kind === 'table') {
        for (const binding of c.bindings) {
          for (const path of binding.paths) add(path, binding.frame, design.mck.styles.small)
        }
      }
    }
  }
  if (!Object.keys(budgets).length) throw Error(`${type}: no projection could be compiled`)
  return budgets
}
export const MCK_FAMILY = {
  key: 'mck',
  name: 'mck-consulting/v1',
  resolve: resolveMckDeck,
  assert: assertMck,
  checks: { 'mck-language': checkMck },
  groups: {
    anchor: ['cover'],
    situation: ['snapshot', 'profile'],
    analysis: ['matrix', 'drivers'],
    action: ['pillars', 'initiatives'],
    timeline: ['roadmap'],
  },
  projectedBudgets: mckProjectedBudgets,
  projectedCapacities(design, family) {
    const c = design.mck.capacity
    return {
      cover: { details: [1, 4] },
      snapshot: { metrics: c.metrics, cohort: c.cohort },
      profile: {
        age: c.profile,
        income: c.profile,
        occupation: c.profile,
        interests: c.interests,
      },
      matrix: { bubbles: c.bubbles, legend: c.bubbles },
      drivers: { drivers: c.drivers },
      pillars: { pillars: c.pillars },
      initiatives: { initiatives: c.initiatives },
      roadmap: {
        phases: c.phases,
        'phases[].items': c.tasks,
        metrics: c.metrics,
        'governance.items': c.governance,
      },
    }[family.role]
  },
}
