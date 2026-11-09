import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compilePinkLayout, resolvePinkDeck } from './layouts.mjs'
export const PINK_LAYOUTS = {
  cover: {
    hanging: ['hero', 'continuation', 'metadata'],
    offset: ['hero', 'continuation', 'metadata'],
  },
  index: { rail: ['hero', 'continuation', 'items'], band: ['hero', 'continuation', 'items'] },
  stats: { rail: ['title', 'intro', 'stats'], band: ['title', 'intro', 'stats'] },
  section: { left: ['number', 'story'], right: ['number', 'story'] },
  trend: {
    rail: ['title', 'legend', 'plot', 'callout'],
    band: ['title', 'legend', 'plot', 'callout'],
  },
  process: {
    columns: ['title', 'intro', 'steps', 'timeline'],
    rows: ['title', 'intro', 'steps', 'timeline'],
  },
  matrix: { full: ['title', 'table', 'note'], inset: ['title', 'table', 'note'] },
  quote: { rail: ['mark', 'quote', 'attribution'], broad: ['mark', 'quote', 'attribution'] },
  closing: { invitation: ['title', 'actions', 'ticket'], sidecar: ['title', 'actions', 'ticket'] },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
export function pinkSpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties).map(([k, v]) => [k, pinkSpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from({ length: maximum ? s.maxItems : s.minItems }, (_, i) =>
      pinkSpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  if (s.type === 'boolean') return false
  return 'x'
}
function assertPink(d, { assertFrame }) {
  for (const [k, v] of Object.entries({
    paper: '060507',
    ink: 'F5EDF1',
    accent: 'ED3D8C',
    lit: '1A1218',
  }))
    if (d.colors[k] !== v) throw Error(`Pink Script identity requires ${k} ${v}`)
  for (const [role, pair] of Object.entries({
    display: ['DM Serif Display', 'Songti SC'],
    body: ['Inter', 'Songti SC'],
    mono: ['JetBrains Mono', 'Noto Sans SC'],
  }))
    if (d.fonts[role]?.latin !== pair[0] || d.fonts[role]?.eastAsian !== pair[1])
      throw Error(`${role}: unregistered Pink Script font pair`)
  const seen = new Set()
  for (const [type, f] of Object.entries(d.pink.families)) {
    const expected = PINK_LAYOUTS[f.role]
    if (!type.startsWith('pink') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [k, frame] of Object.entries(v.regions))
        assertFrame(d, frame, `${type}.${id}.${k}`)
    }
  }
  if (seen.size !== 9) throw Error('Pink Script requires all nine registered editorial roles')
  for (const [k, s] of Object.entries(d.pink.styles))
    if (
      !d.fonts[s.role] ||
      !d.colors[s.color] ||
      s.italic ||
      s.sizePt < 10.5 ||
      s.sizePt > 300 ||
      (s.role === 'display' && s.lineHeight !== 1)
    )
      throw Error(`${k}: upright readable typography and tested display advance required`)
  for (const [k, f] of Object.entries(d.pink.chrome)) assertFrame(d, f, `pink.chrome.${k}`)
}
function checkPink(d, op, fail) {
  const name = op.name ?? op.shape?.name ?? ''
  if (/InteriorFrame|OuterFrame|TicketLabel|ContactPlate/.test(name))
    fail('Outer frames and contact plates are excluded by the design contract')
  if (
    ['add-shape', 'add-freeform'].includes(op.op) &&
    parseFloat(op.x) < 0.5 &&
    parseFloat(op.y) < 0.5 &&
    parseFloat(op.w) > d.canvas.widthIn - 1 &&
    parseFloat(op.h) > d.canvas.heightIn - 1
  )
    fail('Canvas-sized border geometry is not registered')
  if (op.op === 'add-image' && !/_ContactQR$/.test(name))
    fail('Only the square contact QR asset is registered')
  if (op.op === 'add-chart' && (op.kind !== 'line' || !/_Trend$/.test(name)))
    fail('Pink Script registers one native two-series line family')
  if (op.op === 'add-shape' && op.kind !== 'rectangle')
    fail('Pink Script uses square native geometry')
  if (op.op === 'add-group') fail('Groups are not registered')
  if (op.op === 'set-chart' && op.view3D) fail('Pink Script prohibits 3D')
  if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
    fail('Pink Script requires open table rules')
  if (op.op === 'set-slide-background') {
    const expected = [d.colors.lit, d.colors.paper, d.colors.edge]
    if (
      op.fill?.type !== 'gradient' ||
      op.fill.path !== 'circle' ||
      op.fill.stops?.map((v) => v.color).join('|') !== expected.join('|')
    )
      fail('Warm native radial surface required')
  }
  if (
    op.effect?.glow &&
    (!/(CoverTitle|ChapterNumber)$/.test(name) ||
      op.effect.glow.color !== d.colors.accent ||
      op.effect.glow.alpha > 0.15)
  )
    fail('Only restrained pink hero/chapter glow is registered')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Typography must remain upright')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
function budgets(design, family) {
  const type = Object.keys(design.pink.families).find((k) => design.pink.families[k] === family),
    schema = schemaFor(type),
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
  for (const [id, v] of Object.entries(family.variants))
    for (const c of compilePinkLayout(design, family, id, v, pinkSpecimen(schema))) {
      if (c.bindings?.length)
        for (const bind of c.bindings) for (const p of bind.paths) add(p, bind.frame, bind.style)
      else if (c.style)
        for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / 12, 0.5], design.pink.styles.small)
    }
  return out
}
export const PINK_FAMILY = {
  key: 'pink',
  name: 'pink-editorial/v1',
  assert: assertPink,
  resolve: (d, c) =>
    resolvePinkDeck(d, c, {
      validateData: (type, data, path) => {
        const s = schemaFor(type)
        assertDesignValue(data, s, s, path)
      },
    }),
  checks: { 'pink-language': checkPink },
  groups: {
    anchor: ['cover', 'section', 'closing'],
    editorial: ['index', 'quote'],
    evidence: ['stats', 'trend', 'matrix'],
    process: ['process'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.pink.capacity
    return (
      {
        cover: { metadata: c.metadata },
        index: { items: c.items },
        stats: { stats: c.stats },
        trend: { categories: c.categories, series: [2, 2], 'series[].values': c.categories },
        process: { steps: c.steps },
        matrix: { columns: c.columns, rows: c.rows, 'rows[]': c.columns, statuses: [0, 6] },
        closing: { actions: c.actions },
      }[f.role] ?? {}
    )
  },
}
