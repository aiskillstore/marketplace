import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileSkyLayout, resolveSkyDeck } from './layouts.mjs'
export const SKY_LAYOUTS = {
  cover: {
    verdict: ['hero', 'abstract', 'metrics', 'verdict', 'ornament'],
    rail: ['hero', 'abstract', 'metrics', 'verdict', 'ornament'],
  },
  performance: { wide: ['table'], rail: ['table', 'note'] },
  coverage: { plotLeft: ['plot', 'notes'], plotRight: ['plot', 'notes'] },
  ranking: { plotLeft: ['plot', 'notes'], plotRight: ['plot', 'notes'] },
  process: { horizontal: ['summary', 'flow', 'notes'], vertical: ['summary', 'flow', 'notes'] },
  diagnosis: { wide: ['table', 'note'], compact: ['table', 'note'] },
  actions: { horizontal: ['items'], vertical: ['items'] },
  project: { arcLeft: ['arc', 'metadata', 'notes'], arcRight: ['arc', 'metadata', 'notes'] },
  trend: { plotLeft: ['plot', 'notes'], plotRight: ['plot', 'notes'] },
  bridge: { plotLeft: ['plot', 'notes'], plotRight: ['plot', 'notes'] },
  appendix: { wide: ['table', 'note'], inset: ['table', 'note'] },
  decisions: { wide: ['table', 'note'], compact: ['table', 'note'] },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url), 'utf8'))
export function validateSkyData(type, data, path) {
  const schema = schemaFor(type)
  assertDesignValue(data, schema, schema, path)
}
function assertSky(design, { assertFrame }) {
  const b = design.sky,
    seen = new Set()
  for (const [k, v] of Object.entries({
    paper: 'FFFFFF',
    ink: '000000',
    accent: '007ACC',
    navy: '001142',
    pale: 'C2E6FF',
    highlight: 'D6F1FF',
  }))
    if (design.colors[k] !== v) throw Error(`Sky Compass identity requires ${k} ${v}`)
  if (Object.keys(b.families).length !== 12)
    throw Error('Sky Compass requires twelve registered roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = SKY_LAYOUTS[f.role]
    if (!type.startsWith('sky') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate Sky role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [name, frame] of Object.entries(v.regions))
        assertFrame(design, frame, `${type}.${id}.${name}`)
    }
  }
  for (const [name, st] of Object.entries(b.styles))
    if (!design.colors[st.color] || !design.fonts[st.role] || st.italic || st.sizePt < 10.5)
      throw Error(`${name}: readable upright registered style required`)
  for (const [name, f] of Object.entries(b.chrome)) assertFrame(design, f, `sky.chrome.${name}`)
  const { arcCount, radiusStep, strokePt } = b.compass
  if (
    !Number.isInteger(arcCount) ||
    arcCount < 2 ||
    arcCount > 5 ||
    !(radiusStep > 0 && radiusStep * (arcCount - 1) < 1) ||
    !(strokePt > 0 && strokePt <= 2)
  )
    throw Error('Sky Compass requires bounded open compass linework')
  for (const [name, v] of Object.entries(b.capacity))
    if (v.length !== 2 || v.some((n) => !Number.isInteger(n) || n < 1) || v[1] < v[0])
      throw Error(`${name}: invalid capacity`)
}
function checkSky(design, op, fail) {
  const name = op.name ?? op.shape?.name ?? ''
  if (
    op.op === 'add-chart' &&
    (!['bar', 'column', 'doughnut'].includes(op.kind) ||
      !/(MixRing|Ranking|ObservedTrend)$/.test(name))
  )
    fail('Unregistered Sky native chart')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Sky uses square regions and functional circles')
  if (
    op.op === 'add-freeform' &&
    !/(CoverCompassArc[0-4]|ProjectArc[0-4]|ProcessTarget)$/.test(name)
  )
    fail('Unregistered Sky path')
  if (/CoverCompassArc[0-4]$/.test(name)) {
    if (op.op === 'add-freeform' && op.path.commands.some((c) => c.type === 'close'))
      fail('Cover compass paths must remain open')
    if (op.op === 'set-shape' && op.fill && op.fill.type !== 'none')
      fail('Cover compass linework must not become a solid sector')
  }
  if (['add-image', 'add-group'].includes(op.op)) fail('No Sky image or group input is registered')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Sky uses white paper')
  if (op.op === 'set-chart' && op.view3D) fail('Sky prohibits 3D charts')
  if (
    op.op === 'set-shape' &&
    ['green', 'amber', 'red'].some((k) => op.fill?.color === design.colors[k]) &&
    !/_Status(?:Accent)?\d+$/.test(name)
  )
    fail('Status colors require an explicit status component')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Sky typography must be upright')
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Sky prohibits decorative fills')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
export function skySpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties).map(([k, v]) => [k, skySpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from({ length: maximum ? s.maxItems : s.minItems }, (_, i) =>
      skySpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
function budgets(design, family) {
  const type = Object.keys(design.sky.families).find((k) => design.sky.families[k] === family),
    schema = schemaFor(type),
    d = skySpecimen(schema),
    out = {}
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
  let count = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileSkyLayout(design, family, id, v, d)
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const bind of c.bindings ?? [])
        for (const p of bind.paths) add(p, bind.frame, bind.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / d.points.length, 0.6], design.sky.styles.small)
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return out
}
export const SKY_FAMILY = {
  key: 'sky',
  name: 'sky-wayfinding/v1',
  assert: assertSky,
  resolve: (d, c) => resolveSkyDeck(d, c, { validateData: validateSkyData }),
  checks: { 'sky-language': checkSky },
  groups: {
    anchor: ['cover', 'decisions'],
    judgment: ['performance', 'diagnosis'],
    evidence: ['coverage', 'ranking', 'trend', 'bridge', 'appendix'],
    process: ['process', 'actions', 'project'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.sky.capacity
    return {
      cover: { metrics: c.metrics },
      performance: { metrics: c.metrics },
      coverage: { points: [3, 3], notes: c.notes },
      ranking: { points: c.points, notes: c.notes },
      process: { steps: c.steps, notes: c.notes },
      diagnosis: { issues: c.issues },
      actions: { items: c.actions },
      project: { metadata: c.metadata, items: c.projectItems },
      trend: { points: c.trendPoints, notes: c.notes },
      bridge: { drivers: c.drivers, notes: c.notes },
      appendix: { columns: c.columns, rows: c.rows, 'rows[]': c.columns },
      decisions: { items: c.decisions },
    }[f.role]
  },
}
