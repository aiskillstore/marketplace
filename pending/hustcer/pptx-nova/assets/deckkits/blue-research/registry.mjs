import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileResearchLayout, resolveResearchDeck } from './layouts.mjs'

export const RESEARCH_LAYOUTS = {
  cover: {
    spine: ['hero', 'abstract', 'edition'],
    split: ['hero', 'abstract', 'edition'],
  },
  overview: { rail: ['claims', 'notes', 'agenda'], reverse: ['claims', 'notes', 'agenda'] },
  evidence: { rail: ['plot', 'notes', 'capsule'], band: ['plot', 'notes', 'capsule'] },
  matrix: { rail: ['table', 'note', 'excerpt'], reverse: ['table', 'note', 'excerpt'] },
  bridge: { rail: ['plot', 'drivers'], reverse: ['plot', 'drivers'] },
  tiers: { rail: ['table', 'note', 'notes'], reverse: ['table', 'note', 'notes'] },
  timeline: { horizontal: ['events', 'unit'], vertical: ['events', 'unit'] },
  scorecard: {
    steps: ['goals', 'steps', 'acceptance'],
    register: ['goals', 'steps', 'acceptance'],
  },
  findings: { register: ['items'], leadRail: ['items'] },
  implications: {
    matrix: ['items', 'dependencyLabel', 'dependencies', 'shared'],
    ledger: ['items', 'dependencyLabel', 'dependencies', 'shared'],
  },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
export const validateResearchData = (type, data, path) => {
  const schema = schemaFor(type)
  assertDesignValue(data, schema, schema, path)
}
function assertResearch(design, { assertFrame }) {
  const b = design.research,
    seen = new Set()
  for (const [key, color] of Object.entries({
    paper: 'FFFFFF',
    ink: '000000',
    navy: '00295F',
    accent: '00ACEE',
    deep: '0064BC',
    pale: 'BEE0FF',
    orange: 'F17E00',
    highlight: 'F2E292',
  }))
    if (design.colors[key] !== color) throw Error(`Blue Research identity requires ${key} ${color}`)
  if (Object.keys(b.families).length !== Object.keys(RESEARCH_LAYOUTS).length)
    throw Error('Blue Research requires ten registered roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = RESEARCH_LAYOUTS[f.role]
    if (!type.startsWith('research') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate research role`)
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
    if (!design.fonts[st.role] || !design.colors[st.color] || st.italic || st.sizePt < 10.5)
      throw Error(`${name}: readable upright registered style required`)
  for (const [name, f] of Object.entries(b.chrome))
    assertFrame(design, f, `research.chrome.${name}`)
  for (const [name, v] of Object.entries(b.capacity))
    if (v.length !== 2 || v.some((n) => !Number.isInteger(n) || n < 1) || v[1] < v[0])
      throw Error(`${name}: invalid capacity`)
}
function checkResearch(design, op, fail, context) {
  const name = op.name ?? op.shape?.name ?? ''
  if (op.op === 'set-shape' && op.fill?.color === design.colors.orange) {
    const focalOwners = new Set(
      context.patch.ops
        .filter(
          (o) =>
            o.slide === op.slide && o.op === 'set-shape' && o.fill?.color === design.colors.orange,
        )
        .map((o) => o.shape?.name),
    )
    if (focalOwners.size > 1) fail('Research permits one orange focal event per slide')
  }
  if (
    op.op === 'add-chart' &&
    (!['column', 'line'].includes(op.kind) || !name.endsWith('_EvidenceChart'))
  )
    fail('Unregistered research chart')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Research uses square fields and functional ellipses')
  if (op.op === 'add-freeform' && op.path.commands.some((c) => !['move', 'line'].includes(c.type)))
    fail('Research paths are fine linear rules')
  if (['add-image', 'add-group'].includes(op.op))
    fail('No image/group input registered in Blue Research')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Research requires white paper')
  if (op.op === 'set-chart' && op.view3D) fail('Research prohibits 3D')
  if (
    op.op === 'set-shape' &&
    op.fill?.color === design.colors.orange &&
    !/_EventNumber\d+$/.test(name)
  )
    fail('Orange is limited to a numbered event, never a background field')
  if (
    op.op === 'set-shape' &&
    op.fill?.color === design.colors.highlight &&
    !/_FindingEmphasis\d+$/.test(name)
  )
    fail('Yellow requires a content-authored emphasis field')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Research typography must remain upright')
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Research prohibits decorative fills')
    if (op.op === 'set-chart' && key === 'fill' && v.color === design.colors.ink)
      fail('Native evidence must not use black plot fills')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
export function researchSpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties)
        .filter(([, v]) => !v['x-slotProbeOmit'])
        .map(([k, v]) => [k, researchSpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from(
      { length: maximum ? s.maxItems : Math.max(s.minItems, Math.min(2, s.maxItems)) },
      (_, i) => researchSpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
function budgets(design, family) {
  const type = Object.keys(design.research.families).find(
      (k) => design.research.families[k] === family,
    ),
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
    if (
      !out[key] ||
      v.widthIn < out[key].widthIn ||
      (v.widthIn === out[key].widthIn && v.heightIn < out[key].heightIn)
    )
      out[key] = v
  }
  let count = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileResearchLayout(design, family, id, v, researchSpecimen(schema))
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const bind of c.bindings ?? [])
        for (const p of bind.paths) add(p, bind.frame, bind.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / 6, 0.5], design.research.styles.small)
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return out
}
export const RESEARCH_FAMILY = {
  key: 'research',
  name: 'blue-research/v1',
  assert: assertResearch,
  resolve: (d, c) => resolveResearchDeck(d, c, { validateData: validateResearchData }),
  checks: { 'research-language': checkResearch },
  groups: {
    anchor: ['cover', 'implications'],
    judgment: ['overview', 'findings'],
    evidence: ['evidence', 'matrix', 'bridge', 'tiers'],
    process: ['timeline', 'scorecard'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.research.capacity
    return {
      cover: {},
      overview: { claims: c.claims, notes: [3, 3], agenda: c.agenda },
      evidence: {
        'chart.categories': c.chartCategories,
        'chart.series': c.chartSeries,
        'chart.series[].values': c.chartCategories,
        notes: c.notes,
      },
      matrix: { columns: c.columns, rows: c.rows, 'rows[].cells': c.columns },
      bridge: { drivers: c.drivers },
      tiers: { rows: c.tierRows, headers: [4, 4], notes: [3, 3] },
      timeline: { events: c.events },
      scorecard: { goals: c.goals, steps: c.steps, 'steps[].actions': c.stepActions },
      findings: { items: c.findings },
      implications: { readers: c.readers, headers: [4, 4], dependencies: c.dependencies },
    }[f.role]
  },
}
