import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileVioletLayout, resolveVioletDeck } from './layouts.mjs'
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url), 'utf8'))
export const VIOLET_LAYOUTS = {
  cover: ['split', 'band'],
  summary: ['rail', 'band'],
  scorecard: ['wide'],
  trend: ['rail', 'wide'],
  attribution: ['converge', 'stack'],
  diagnosis: ['columns', 'rows'],
  projects: ['rows', 'columns'],
  actions: ['timeline', 'stack'],
  section: ['full'],
  rating: ['rows', 'columns'],
}
export function validateVioletData(type, data, path) {
  const s = schemaFor(type)
  assertDesignValue(data, s, s, path)
  if (type === 'violetSectionSlide' && !Number.isInteger(data.index))
    throw Error('Section index must be an integer')
}
function assertViolet(d, { assertFrame }) {
  for (const [k, v] of Object.entries({
    paper: 'FFFFFF',
    ink: '121212',
    accent: '5114F6',
    muted: '626262',
    rule: 'CCCCCC',
  }))
    if (d.colors[k] !== v) throw Error(`Violet identity requires ${k} ${v}`)
  if (d.fonts.body.latin !== 'Tahoma' || d.fonts.body.eastAsian !== 'Noto Sans SC')
    throw Error('Violet requires registered upright sans serif fonts')
  const seen = new Set()
  for (const [type, f] of Object.entries(d.violet.families)) {
    if (!type.startsWith('violet') || !VIOLET_LAYOUTS[f.role] || seen.has(f.role))
      throw Error('Unknown or duplicate Violet role')
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== VIOLET_LAYOUTS[f.role].join('|'))
      throw Error(type + ': unregistered layouts')
    for (const [id, v] of Object.entries(f.variants))
      for (const [k, frame] of Object.entries(v.regions))
        assertFrame(d, frame, `${type}.${id}.${k}`)
  }
  if (seen.size !== 10) throw Error('Violet requires ten registered roles')
  for (const [n, s] of Object.entries(d.violet.styles))
    if (!d.colors[s.color] || !d.fonts[s.role] || s.italic || s.sizePt < 11.5)
      throw Error(n + ': readable upright registered style required')
  for (const [n, f] of Object.entries(d.violet.chrome)) assertFrame(d, f, n)
}
function checkViolet(d, op, fail) {
  const name = op.name ?? op.shape?.name ?? ''
  if (['add-image', 'add-group'].includes(op.op)) fail('No image or group input is registered')
  if (
    op.op === 'add-chart' &&
    (op.kind !== 'column' || op.data?.series?.length !== 1 || !name.endsWith('TrendChart'))
  )
    fail('Violet requires a single registered native column series')
  if (op.op === 'set-chart' && op.view3D) fail('Violet prohibits 3D charts')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Violet uses sharp regions and functional circles')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== d.colors.paper)
  )
    fail('Violet base uses white paper')
  if (op.op === 'set-chart')
    for (const series of op.series ?? []) {
      if (series.fill?.color !== d.colors.accent) fail('Violet series uses one accent throughout')
      for (const point of series.points ?? [])
        if (point.fill?.color !== d.colors.accent) fail('Violet columns use one accent throughout')
    }
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Upright fonts required')
    if (key === 'fill' && ['gradient', 'pattern', 'picture'].includes(v.type))
      fail('Flat fills required')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
export function violetSpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties).map(([k, v]) => [k, violetSpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from({ length: maximum ? s.maxItems : s.minItems }, (_, i) =>
      violetSpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0)
  return 'x'
}
function budgets(d, f) {
  const type = Object.keys(d.violet.families).find((k) => d.violet.families[k] === f),
    schema = schemaFor(type),
    data = violetSpecimen(schema),
    out = {}
  let count = 0
  const add = (p, frame, st) => {
    if (!p?.startsWith('data.')) return
    const key = p.slice(5).replace(/\[\d+\]/g, '[]')
    let node = schema
    for (const k of key.replaceAll('[]', '.[]').split('.'))
      node = k === '[]' ? node?.items : node?.properties?.[k]
    if (node?.type !== 'string' || node['x-slotRole'] === 'control') return
    const v = {
      fontPt: st.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: st.lineHeight,
      maxLines: Math.max(1, Math.floor(((frame[3] - 0.025) * 72) / (st.sizePt * 1.5))),
    }
    if (!out[key] || v.widthIn < out[key].widthIn) out[key] = v
  }
  for (const [id, v] of Object.entries(f.variants)) {
    let cs
    try {
      cs = compileVioletLayout(d, f, id, v, data)
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const bind of c.bindings ?? [])
        for (const p of bind.paths) add(p, bind.frame, bind.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / data.points.length, 0.6], d.violet.styles.small)
    }
  }
  if (!count) throw Error(type + ': no valid projection specimen')
  return out
}
export const VIOLET_FAMILY = {
  key: 'violet',
  name: 'violet-operations/v1',
  assert: assertViolet,
  resolve: (d, c) => resolveVioletDeck(d, c, { validateData: validateVioletData }),
  checks: { 'violet-language': checkViolet },
  groups: {
    anchor: ['cover', 'section'],
    judgment: ['summary', 'diagnosis', 'actions'],
    evidence: ['scorecard', 'trend', 'attribution', 'projects', 'rating'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.violet.capacity
    return {
      cover: { metrics: c.metrics },
      summary: { metrics: c.metrics },
      scorecard: { rows: c.scoreRows },
      trend: { points: c.points, notes: c.notes },
      attribution: { drivers: c.drivers, notes: c.notes },
      diagnosis: { cases: c.cases },
      projects: { projects: c.projects },
      actions: { phases: c.phases, decisions: c.decisions },
      rating: { ratings: c.ratings },
      section: {},
    }[f.role]
  },
}
