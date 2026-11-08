import { readFileSync } from 'node:fs'
import { compileImpactLayout, resolveImpactDeck } from './layouts.mjs'

export const IMPACT_LAYOUTS = {
  overview: {
    verdict: ['hero', 'verdict', 'description', 'index', 'metrics'],
    bandFirst: ['hero', 'verdict', 'description', 'index', 'metrics'],
  },
  review: { rail: ['metrics', 'findings', 'verdict'], band: ['metrics', 'findings', 'verdict'] },
  chart: { chartLeft: ['chart', 'notes', 'summary'], chartRight: ['chart', 'notes', 'summary'] },
  comparison: {
    side: ['table', 'metrics', 'tableNote', 'evidence'],
    stacked: ['table', 'metrics', 'tableNote', 'evidence'],
  },
  process: {
    chain: ['metrics', 'steps', 'feedback', 'feedbackNote', 'assurance'],
    vertical: ['metrics', 'steps', 'feedback', 'feedbackNote', 'assurance'],
  },
  capacity: {
    strip: ['metrics', 'explanation', 'outlook'],
    rail: ['metrics', 'explanation', 'outlook'],
  },
  scorecard: { wide: ['table', 'note'], inset: ['table', 'note'] },
  commitments: {
    columns: ['items', 'verificationLabel', 'verification'],
    ledger: ['items', 'verificationLabel', 'verification'],
  },
  progress: { rows: ['items', 'basis'], columns: ['items', 'basis'] },
  variance: { wide: ['plot', 'unit', 'explanation'], split: ['plot', 'unit', 'explanation'] },
  milestones: { horizontal: ['items', 'governance'], vertical: ['items', 'governance'] },
  decisions: { ledger: ['items', 'consequence'], split: ['items', 'owners', 'consequence'] },
}
function assertImpact(design, { assertFrame }) {
  const b = design.impact,
    seen = new Set()
  if (Object.keys(b.families).length !== 12) throw Error('Impact requires twelve registered roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = IMPACT_LAYOUTS[f.role]
    if (!type.startsWith('impact') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate impact role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [key, frame] of Object.entries(v.regions))
        assertFrame(design, frame, `${type}.${id}.${key}`)
    }
  }
  for (const [key, st] of Object.entries(b.styles))
    if (!design.colors[st.color] || !design.fonts[st.role] || st.italic || st.sizePt < 10.5)
      throw Error(`${key}: readable upright registered style required`)
  for (const [key, f] of Object.entries(b.chrome)) assertFrame(design, f, `impact.chrome.${key}`)
  for (const [key, c] of Object.entries(b.capacity))
    if (c.length !== 2 || c.some((v) => !Number.isInteger(v) || v < 1) || c[1] < c[0])
      throw Error(`${key}: invalid impact capacity`)
}
function checkImpact(design, op, fail) {
  if (op.op === 'add-chart' && (op.kind !== 'column' || op.variant !== 'clustered'))
    fail('Impact registers native clustered columns only')
  if (op.op === 'add-shape' && op.kind !== 'rectangle')
    fail('Impact uses open rectangular rules and data shapes')
  if (op.op === 'add-freeform' && !/_(?:StepArrow\d+|Feedback)$/.test(op.name ?? ''))
    fail('Unregistered impact path')
  if (['add-image', 'add-group'].includes(op.op))
    fail('No registered impact image or group component')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Impact uses white paper')
  const walk = (v, k = '') => {
    if (!v || typeof v !== 'object') return
    if (k === 'font' && v.italic) fail('Impact type must be upright')
    if (k === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Impact prohibits decorative fills')
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
export function impactProjectedBudgets(design, family) {
  const type = Object.keys(design.impact.families).find((k) => design.impact.families[k] === family)
  const schema = JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
  const data = specimen(schema),
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
  let compiled = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileImpactLayout(design, family, id, v, data)
    } catch {
      continue
    }
    compiled++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const bind of c.bindings ?? [])
        for (const p of bind.paths) add(p, bind.frame, design.impact.styles.table)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / data.points.length, 0.65], design.impact.styles.label)
    }
  }
  if (!compiled) throw Error(`${type}: no valid projection specimen`)
  return budgets
}
export const IMPACT_FAMILY = {
  key: 'impact',
  name: 'impact-evidence/v1',
  resolve: resolveImpactDeck,
  assert: assertImpact,
  checks: { 'impact-language': checkImpact },
  groups: {
    anchor: ['overview'],
    review: ['review', 'capacity'],
    evidence: ['chart', 'comparison', 'scorecard', 'progress', 'variance'],
    process: ['process', 'milestones'],
    action: ['commitments', 'decisions'],
  },
  projectedBudgets: impactProjectedBudgets,
  projectedCapacities(design, f) {
    const c = design.impact.capacity
    return {
      overview: { metrics: c.metrics, sections: c.sections },
      review: { metrics: c.railMetrics, findings: c.findings },
      chart: { points: c.points, notes: c.notes },
      comparison: { columns: c.columns, rows: c.comparisonRows, metrics: c.railMetrics },
      process: { metrics: c.railMetrics, steps: c.steps },
      capacity: { metrics: c.metrics },
      scorecard: { columns: c.columns, rows: c.scorecardRows },
      commitments: { items: c.items },
      progress: { items: c.progressItems },
      variance: { drivers: c.drivers },
      milestones: { items: c.milestones },
      decisions: { items: c.decisions },
    }[f.role]
  },
}
