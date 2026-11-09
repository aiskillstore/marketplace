import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileClayLayout, resolveClayDeck } from './layouts.mjs'

export const CLAY_LAYOUTS = {
  cover: {
    portrait: ['hero', 'quote', 'description', 'metrics', 'asset'],
    editorial: ['hero', 'quote', 'description', 'metrics', 'asset'],
  },
  overview: { rail: ['metrics', 'findings'], band: ['metrics', 'findings'] },
  chart: {
    chartLeft: ['chart', 'analysis', 'caption'],
    chartRight: ['chart', 'analysis', 'caption'],
  },
  comparison: {
    side: ['table', 'tableNote', 'evidence', 'quote'],
    stacked: ['table', 'tableNote', 'evidence', 'quote'],
  },
  process: { chain: ['metrics', 'steps'], vertical: ['metrics', 'steps'] },
  kpi: { strip: ['metrics', 'explanation'], rail: ['metrics', 'explanation'] },
  status: { wide: ['table', 'tableNote'] },
  commitments: {
    columns: ['title', 'items', 'mechanism'],
    ledger: ['title', 'items', 'mechanism'],
  },
}
export function validateClayData(type, data, path) {
  const s = JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
  assertDesignValue(data, s, s, path)
}
function assertClay(design, { assertFrame }) {
  const b = design.clay,
    seen = new Set()
  if (Object.keys(b.families).length !== 8)
    throw Error('Warm Clay requires eight registered responsibilities')
  if (design.colors.paper !== 'F9F4E9') throw Error('Warm Clay requires cream paper')
  for (const value of Object.values(design.colors)) {
    const [r, g, b] = value.match(/../g).map((v) => parseInt(v, 16))
    if (r < g || g < b) throw Error('Warm Clay prohibits cool colors')
  }
  for (const [type, f] of Object.entries(b.families)) {
    const expected = CLAY_LAYOUTS[f.role]
    if (!type.startsWith('clay') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate clay role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [k, f] of Object.entries(v.regions)) assertFrame(design, f, `${type}.${id}.${k}`)
    }
  }
  for (const [k, s] of Object.entries(b.styles))
    if (!design.colors[s.color] || !design.fonts[s.role] || s.italic || s.sizePt < 10.5)
      throw Error(`${k}: readable upright registered style required`)
  for (const [k, f] of Object.entries(b.chrome)) assertFrame(design, f, `clay.chrome.${k}`)
  for (const [k, v] of Object.entries(b.capacity))
    if (v.length !== 2 || v.some((n) => !Number.isInteger(n) || n < 1) || v[1] < v[0])
      throw Error(`${k}: invalid clay capacity`)
}
function checkClay(design, op, fail) {
  if (op.op === 'add-chart' && (op.kind !== 'column' || op.variant !== 'clustered'))
    fail('Warm Clay registers native single-series columns only')
  if (op.op === 'add-chart' && op.data?.series?.length !== 1)
    fail('Warm Clay requires a single evidence series')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Unregistered clay shape')
  if (op.op === 'add-freeform' && !/_Ornament(?:tl|tr|bl|br)$/.test(op.name ?? ''))
    fail('Unregistered clay freeform')
  if (['add-image', 'add-group'].includes(op.op))
    fail('Warm Clay has no registered image/group input')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Warm Clay uses cream paper throughout')
  const walk = (v, k = '') => {
    if (!v || typeof v !== 'object') return
    if (k === 'font' && v.italic) fail('Warm Clay type must be upright')
    if (k === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Warm Clay prohibits decorative fills')
    for (const [key, x] of Object.entries(v)) walk(x, key)
  }
  walk(op)
}
function specimen(s, index = 0) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties)
        .filter(([, v]) => !v['x-slotProbeOmit'])
        .map(([k, v]) => [k, specimen(v, index)]),
    )
  if (s.type === 'array')
    return Array.from({ length: s.maxItems ?? s.minItems ?? 1 }, (_, i) => specimen(s.items, i))
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
function projectedBudgets(design, family) {
  const type = Object.keys(design.clay.families).find((k) => design.clay.families[k] === family)
  const schema = JSON.parse(
      readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)),
    ),
    data = specimen(schema),
    budgets = {}
  const add = (path, frame, style) => {
    if (!path?.startsWith('data.')) return
    const key = path.slice(5).replace(/\[\d+\]/g, '[]')
    let node = schema
    for (const part of key.replaceAll('[]', '.[]').split('.'))
      node = part === '[]' ? node?.items : node?.properties?.[part]
    if (node?.type !== 'string' || node['x-slotRole'] === 'control') return
    const v = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(1, Math.floor(((frame[3] - 0.025) * 72) / (style.sizePt * 1.5))),
    }
    if (!budgets[key] || v.widthIn < budgets[key].widthIn) budgets[key] = v
  }
  let count = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileClayLayout(design, family, id, v, data)
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const bind of c.bindings ?? [])
        for (const p of bind.paths) add(p, bind.frame, design.clay.styles.small)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / data.points.length, 0.5], design.clay.styles.small)
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return budgets
}
export const CLAY_FAMILY = {
  key: 'clay',
  name: 'warm-clay-editorial/v1',
  assert: assertClay,
  resolve: (d, c) => resolveClayDeck(d, c, { validateData: validateClayData }),
  checks: { 'clay-language': checkClay },
  groups: {
    anchor: ['cover', 'commitments'],
    review: ['overview', 'kpi'],
    evidence: ['chart', 'comparison', 'status'],
    process: ['process'],
  },
  projectedBudgets,
  projectedCapacities(design, f) {
    const c = design.clay.capacity
    return {
      cover: { metrics: [2, 3] },
      overview: { metrics: c.railMetrics, findings: c.findings },
      chart: { points: c.points },
      comparison: { columns: c.columns, rows: [2, 4] },
      process: { metrics: [2, 2], steps: c.steps },
      kpi: { metrics: c.metrics },
      status: { columns: c.columns, rows: c.rows },
      commitments: { items: c.commitments },
    }[f.role]
  },
}
