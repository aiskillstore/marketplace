import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileAmberLayout, resolveAmberDeck } from './layouts.mjs'

export const AMBER_LAYOUTS = {
  cover: {
    circleRight: ['hero', 'detail', 'ornament', 'register'],
    circleLeft: ['hero', 'detail', 'ornament', 'register'],
  },
  summary: {
    verdictCenter: ['metrics', 'focus', 'analysis', 'notes'],
    verdictBand: ['metrics', 'focus', 'analysis', 'notes'],
  },
  mix: {
    evidenceRail: ['history', 'ring', 'legend', 'metrics'],
    evidenceBand: ['history', 'ring', 'legend', 'metrics'],
  },
  trend: {
    chartRail: ['chart', 'notes', 'annotation'],
    chartBand: ['chart', 'notes', 'annotation'],
  },
  bridge: {
    bridgeRail: ['bridge', 'analysis', 'table', 'note'],
    bridgeBand: ['bridge', 'analysis', 'table', 'note'],
  },
  projects: { progressRows: ['projects', 'recovery'], progressColumns: ['projects', 'recovery'] },
  matrix: { matrixWide: ['table', 'note'], matrixRail: ['table', 'note'] },
  decisions: { decisionTable: ['items', 'closing'], decisionLedger: ['items', 'closing'] },
}
export function validateAmberData(type, data, path) {
  const schema = JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
  assertDesignValue(data, schema, schema, path)
}
function assertAmber(design, { assertFrame }) {
  const b = design.amber,
    seen = new Set()
  if (
    design.colors.paper !== 'FBF9EE' ||
    design.colors.accent !== 'FDC356' ||
    design.colors.ink !== '181716'
  )
    throw Error('Amber Ledger requires warm ivory, charcoal and honey amber identity')
  if (Object.keys(b.families).length !== Object.keys(AMBER_LAYOUTS).length)
    throw Error('Amber Ledger requires eight registered responsibilities')
  const evidence = b.evidence
  if (!evidence || !b.cover) throw Error('Amber Ledger requires explicit evidence and cover roles')
  for (const token of [
    evidence.series,
    evidence.history,
    ...evidence.categorical,
    evidence.track,
    evidence.plan,
    ...Object.values(evidence.focusTones),
  ])
    if (!design.colors[token] || token === 'ink')
      throw Error('Amber Ledger evidence fills require registered colors separate from text ink')
  if (new Set(evidence.categorical).size !== 4)
    throw Error('Amber Ledger composition categories require four distinct tones')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = AMBER_LAYOUTS[f.role]
    if (!type.startsWith('amber') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate amber role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [k, frame] of Object.entries(v.regions))
        assertFrame(design, frame, `${type}.${id}.${k}`)
    }
  }
  for (const [k, st] of Object.entries(b.styles))
    if (!design.fonts[st.role] || !design.colors[st.color] || st.italic || st.sizePt < 10.5)
      throw Error(`${k}: readable upright registered typography required`)
  for (const [k, frame] of Object.entries(b.chrome)) assertFrame(design, frame, `amber.chrome.${k}`)
  for (const [k, limits] of Object.entries(b.capacity))
    if (
      limits.length !== 2 ||
      limits.some((v) => !Number.isInteger(v) || v < 1) ||
      limits[0] > limits[1]
    )
      throw Error(`${k}: invalid amber capacity`)
}
function checkAmber(design, op, fail) {
  if (op.op === 'add-chart' && !['column', 'line', 'doughnut'].includes(op.kind))
    fail('Unregistered Amber Ledger chart kind')
  if (op.op === 'add-chart' && op.data?.series?.length !== 1)
    fail('Amber Ledger charts require one verifiable series')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Unregistered Amber Ledger shape')
  if (['add-image', 'add-group'].includes(op.op))
    fail('Amber Ledger has no registered image or group input')
  if (op.op === 'add-freeform' && !/MicroLine$/.test(op.name ?? ''))
    fail('Only registered numeric microplot paths are allowed')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Amber Ledger uses warm ivory paper')
  if (op.op === 'set-chart' && (op.view3D || op.series?.some((v) => v.smooth)))
    fail('Amber Ledger requires flat straight chart evidence')
  if (op.op === 'set-table') {
    if (op.style?.horizontalBanding || op.style?.verticalBanding)
      fail('Amber Ledger uses open table rules, not banding')
    for (const cell of op.cells ?? [])
      for (const key of ['left', 'right']) {
        const border = cell.style?.borders?.[key]
        if (border && !border.noLine && parseFloat(border.width ?? '1') > 0)
          fail('Amber Ledger prohibits boxed table cells')
      }
  }
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Amber Ledger requires upright type')
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Amber Ledger prohibits decorative fills')
    if (key === 'fill' && v.type === 'solid' && v.color === design.colors.ink)
      fail('Amber Ledger reserves charcoal for text and fine lines, not evidence fills')
    for (const [k, child] of Object.entries(v)) walk(child, k)
  }
  walk(op)
}
function specimen(s, index = 0) {
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(Object.entries(s.properties).map(([k, v]) => [k, specimen(v, index)]))
  if (s.type === 'array')
    return Array.from({ length: s.maxItems ?? s.minItems ?? 1 }, (_, i) => specimen(s.items, i))
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  if (s.type === 'boolean') return false
  return 'x'
}
function projectedBudgets(design, family) {
  const type = Object.keys(design.amber.families).find((k) => design.amber.families[k] === family)
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
  let count = 0
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileAmberLayout(design, family, id, v, data)
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const binding of c.bindings ?? [])
        for (const p of binding.paths) add(p, binding.frame, binding.style)
      for (const p of c.inputPaths ?? [])
        add(
          p,
          [0, 0, c.frame[2] / (data.points ?? data.history).length, 0.5],
          design.amber.styles.small,
        )
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return budgets
}
export const AMBER_FAMILY = {
  key: 'amber',
  name: 'amber-ledger/v1',
  assert: assertAmber,
  resolve: (d, c) => resolveAmberDeck(d, c, { validateData: validateAmberData }),
  checks: { 'amber-language': checkAmber },
  groups: {
    anchor: ['cover', 'decisions'],
    judgment: ['summary'],
    evidence: ['mix', 'trend', 'bridge', 'projects', 'matrix'],
  },
  projectedBudgets,
  projectedCapacities(d, f) {
    const c = d.amber.capacity
    return {
      cover: { metadata: c.metadata },
      summary: { metrics: c.metrics, notes: c.notes },
      mix: { history: c.history, segments: c.segments, metrics: [2, 3] },
      trend: { points: c.points, notes: c.notes },
      bridge: { steps: c.steps, tableColumns: c.columns, tableRows: [2, 3] },
      projects: { projects: c.projects },
      matrix: { columns: c.columns, rows: c.rows },
      decisions: { items: c.items },
    }[f.role]
  },
}
