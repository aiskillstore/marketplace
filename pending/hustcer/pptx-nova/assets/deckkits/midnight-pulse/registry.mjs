import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compilePulseLayout, resolvePulseDeck } from './layouts.mjs'

export const PULSE_LAYOUTS = {
  cover: { widePhoto: ['hero', 'metrics', 'image'], photoRail: ['hero', 'metrics', 'image'] },
  overview: { gaugeRail: ['judgment', 'gauges'], gaugeBand: ['judgment', 'gauges'] },
  audit: { auditWide: ['table', 'note'], auditRail: ['table', 'note'] },
  trend: { trendRail: ['notes', 'chart'], trendBand: ['notes', 'chart'] },
  attribution: { targetRight: ['factors', 'target'], targetLeft: ['factors', 'target'] },
  comparison: { compareColumns: ['overview', 'subjects'], compareRows: ['overview', 'subjects'] },
  status: { statusRows: ['projects'], statusColumns: ['projects'] },
  close: { routeTop: ['route', 'decisions'], routeLeft: ['route', 'decisions'] },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url), 'utf8'))
export function validatePulseData(type, data, path) {
  const schema = schemaFor(type)
  assertDesignValue(data, schema, schema, path)
}
function assertPulse(design, { assertFrame }) {
  const b = design.pulse,
    seen = new Set()
  for (const [k, value] of Object.entries({
    paper: '06070B',
    deep: '020307',
    accent: '1FB9D5',
    ice: 'B8ECF9',
    amber: 'DFA93C',
  }))
    if (design.colors[k] !== value) throw Error(`Midnight Pulse identity requires ${k} ${value}`)
  if (Object.keys(b.families).length !== 8)
    throw Error('Midnight Pulse requires eight registered responsibilities')
  for (const [type, family] of Object.entries(b.families)) {
    const expected = PULSE_LAYOUTS[family.role]
    if (!type.startsWith('pulse') || !expected || seen.has(family.role))
      throw Error(`${type}: unknown or duplicate pulse role`)
    seen.add(family.role)
    if (Object.keys(family.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, variant] of Object.entries(family.variants)) {
      if (Object.keys(variant.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [name, frame] of Object.entries(variant.regions))
        assertFrame(design, frame, `${type}.${id}.${name}`)
    }
  }
  for (const [name, st] of Object.entries(b.styles))
    if (!design.fonts[st.role] || !design.colors[st.color] || st.italic || st.sizePt < 10.5)
      throw Error(`${name}: readable upright registered typography required`)
  for (const [name, frame] of Object.entries(b.chrome))
    assertFrame(design, frame, `pulse.chrome.${name}`)
  const atmosphereCounts = {
    cover: 2,
    overview: 3,
    audit: 2,
    trend: 2,
    attribution: 2,
    comparison: 2,
    status: 1,
    close: 2,
  }
  for (const [role, count] of Object.entries(atmosphereCounts))
    if (b.atmosphere?.[role]?.length !== count)
      throw Error(`${role}: reference atmosphere layer count must be retained`)
  for (const [name, limits] of Object.entries(b.capacity))
    if (
      limits.length !== 2 ||
      limits.some((v) => !Number.isInteger(v) || v < 1) ||
      limits[0] > limits[1]
    )
      throw Error(`${name}: invalid pulse capacity`)
}
function checkPulse(design, op, fail) {
  const C = design.colors,
    name = op.name ?? op.shape?.name ?? ''
  if (
    op.op === 'add-chart' &&
    (!['column', 'doughnut'].includes(op.kind) ||
      op.data?.series?.length !== 1 ||
      !/(TrendChart|Gauge[0-2])$/.test(name))
  )
    fail('Only registered single-series pulse evidence charts are allowed')
  if (op.op === 'add-shape' && !['ellipse', 'rectangle'].includes(op.kind))
    fail('Only flat native pulse shapes are allowed')
  if (op.op === 'add-freeform' && !/(PhaseLine|ConvergingRay\d+|Atmosphere[0-2])$/.test(name))
    fail('Only registered atmosphere, phase and convergence paths are allowed')
  if (op.op === 'add-image' && (op.slide !== 0 || !name.endsWith('CoverPhoto')))
    fail('Photography is restricted to the first cover content slot')
  if (op.op === 'add-group') fail('Unregistered group input')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || ![C.paper, C.deep].includes(op.fill.color))
  )
    fail('Midnight Pulse requires the near-black blue ground')
  if (op.op === 'set-chart') {
    if (op.view3D || op.legend || op.series?.some((v) => v.smooth))
      fail('Pulse evidence is flat and directly labeled without legend dependence')
    for (const series of op.series ?? []) {
      if (name.endsWith('TrendChart') && series.fill?.color !== C.accent)
        fail('Trend evidence must use flame cyan')
      if (/Gauge\d$/.test(name) && ![C.accent, C.amber].includes(series.fill?.color))
        fail('Attainment cannot use project status green or red')
    }
  }
  if (op.op === 'set-shape' && op.fill?.type === 'solid') {
    if (
      [C.green, C.red, C.amber].includes(op.fill.color) &&
      !/ProjectDot\d$/.test(name) &&
      !(op.fill.color === C.amber && /JudgmentDot\d$/.test(name))
    )
      fail('Status fills are restricted to registered status or judgment dots')
    if (op.fill.color === C.ice && !/(GaugeTick\d|AuditTop)$/.test(name))
      fail('A second ice-blue focal block is not registered')
  }
  if (op.op === 'set-table') {
    if (op.style?.horizontalBanding || op.style?.verticalBanding)
      fail('Pulse audit tables are open and unbanded')
    for (const cell of op.cells ?? []) {
      if (cell.style?.fill?.type !== 'none') fail('Pulse audit cells require no fill')
      for (const side of ['left', 'right']) {
        const border = cell.style?.borders?.[side]
        if (border && !border.noLine && parseFloat(border.width ?? '1') > 0)
          fail('Pulse audit tables prohibit vertical rules')
      }
    }
  }
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Pulse typography is upright')
    if (
      key === 'fill' &&
      ['gradient', 'picture', 'pattern'].includes(v.type) &&
      !(v.type === 'gradient' && /_Atmosphere[0-2]$/.test(name))
    )
      fail('Only registered background atmosphere may use gradients')
    for (const [k, child] of Object.entries(v)) walk(child, k)
  }
  walk(op)
}
function specimen(s, index = 0) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(Object.entries(s.properties).map(([k, v]) => [k, specimen(v, index)]))
  if (s.type === 'array')
    return Array.from({ length: s.minItems ?? 1 }, (_, i) => specimen(s.items, i))
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
function projectedBudgets(design, family) {
  const type = Object.keys(design.pulse.families).find((k) => design.pulse.families[k] === family),
    schema = schemaFor(type),
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
      maxLines: Math.max(
        1,
        Math.floor(((frame[3] - 0.025) * 72) / (style.sizePt * (style.sizePt >= 23 ? 1.2 : 1.5))),
      ),
    }
    if (!budgets[key] || v.widthIn < budgets[key].widthIn) budgets[key] = v
  }
  let count = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let components
    try {
      components = compilePulseLayout(design, family, id, v, data)
    } catch {
      continue
    }
    count++
    for (const c of components) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const binding of c.bindings ?? [])
        for (const p of binding.paths) add(p, binding.frame, binding.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / data.points.length, 0.3], design.pulse.styles.small)
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return budgets
}
export const PULSE_FAMILY = {
  key: 'pulse',
  name: 'midnight-pulse/v1',
  assert: assertPulse,
  resolve: (d, c) => resolvePulseDeck(d, c, { validateData: validatePulseData }),
  checks: { 'pulse-language': checkPulse },
  groups: {
    anchor: ['cover', 'close'],
    judgment: ['overview'],
    evidence: ['audit', 'trend', 'attribution', 'comparison', 'status'],
  },
  projectedBudgets,
  projectedCapacities(d, f) {
    const c = d.pulse.capacity
    return {
      cover: { metrics: c.metrics },
      overview: { metrics: c.metrics, notes: [3, 3] },
      audit: { rows: c.rows },
      trend: { points: c.points, events: c.events },
      attribution: { factors: c.factors },
      comparison: { subjects: c.subjects, 'subjects[].kv': c.kv },
      status: { projects: c.projects },
      close: { phases: c.phases, decisions: c.decisions },
    }[f.role]
  },
}
