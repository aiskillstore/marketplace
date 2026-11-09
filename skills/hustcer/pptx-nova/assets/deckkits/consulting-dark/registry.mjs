import { readFileSync } from 'node:fs'
import { compileConsultingLayout, resolveConsultingDeck } from './layouts.mjs'

export const CONSULTING_LAYOUTS = {
  cover: { split: ['main', 'detail'], stacked: ['main', 'detail'] },
  profile: { ledger: ['history', 'metrics'], bands: ['history', 'metrics'] },
  achievements: { quadrants: ['items'], ledger: ['items'] },
  product: {
    strip: ['banner', 'metrics', 'capabilities'],
    rail: ['banner', 'metrics', 'capabilities'],
  },
  landscape: {
    columns: ['position', 'competitors', 'conclusion'],
    ledger: ['position', 'competitors', 'conclusion'],
  },
  audiences: { columns: ['intro', 'items'], ledger: ['intro', 'items'] },
  flow: { horizontal: ['flow', 'capabilities'], vertical: ['flow', 'capabilities'] },
  benchmark: { rail: ['table', 'chart', 'callout'], stacked: ['table', 'chart', 'callout'] },
  roadmap: { horizontal: ['steps'], ledger: ['steps'] },
  decision: { columns: ['intro', 'items', 'closing'], rows: ['intro', 'items', 'closing'] },
}
function assertConsulting(design, { assertFrame }) {
  const b = design.consulting,
    seen = new Set()
  if (Object.keys(b.families).length !== 10) throw Error('Consulting requires all ten roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = CONSULTING_LAYOUTS[f.role]
    if (!expected || seen.has(f.role)) throw Error(`${type}: unknown or duplicate Consulting role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: unregistered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (Object.keys(v.regions).sort().join('|') !== [...expected[id]].sort().join('|'))
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [key, f] of Object.entries(v.regions))
        assertFrame(design, f, `${type}.${id}.${key}`)
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
    'index',
    'compactMetric',
    'proofMetric',
    'reading',
  ]) {
    const st = b.styles[key]
    if (!st || !design.colors[st.color] || !design.fonts[st.role] || st.italic)
      throw Error(`${key}: registered upright font/color required`)
  }
  for (const [key, f] of Object.entries(b.chrome))
    assertFrame(design, f, 'consulting.chrome.' + key)
  for (const [key, c] of Object.entries(b.capacity))
    if (c.length !== 2 || c.some((x) => !Number.isInteger(x) || x < 1) || c[1] < c[0])
      throw Error(key + ': invalid capacity')
}
function checkConsulting(design, op, fail) {
  if (op.op === 'add-chart' && (op.kind !== 'bar' || op.variant !== 'clustered'))
    fail('Consulting registers only native clustered bar charts')
  if (
    op.op === 'add-shape' &&
    !['rectangle', 'oval', 'right-arrow', 'down-arrow'].includes(op.kind)
  )
    fail('Unregistered Consulting shape; rounded containers are not part of this language')
  if (op.op === 'add-freeform')
    fail('Consulting uses open ruled layouts; cut-corner surfaces are not registered')
  if (['add-group', 'add-image'].includes(op.op)) fail('No registered grouped or raster component')
  if (
    op.op === 'set-slide-background' &&
    (design.colors.navy !== op.fill?.color || op.fill?.type !== 'solid')
  )
    fail('Consulting Dark requires a navy canvas on every slide')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Consulting typography must be upright')
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Consulting uses flat fills')
    for (const [k, c] of Object.entries(v)) walk(c, k)
  }
  walk(op)
}
function probe(schema) {
  if (schema.type === 'object')
    return Object.fromEntries(Object.entries(schema.properties).map(([k, v]) => [k, probe(v)]))
  if (schema.type === 'array')
    return Array.from({ length: schema.maxItems ?? schema.minItems ?? 1 }, () =>
      probe(schema.items),
    )
  if (schema.type === 'number') return 1
  return 'x'
}
export function consultingProjectedBudgets(design, family) {
  const type = Object.keys(design.consulting.families).find(
      (k) => design.consulting.families[k] === family,
    ),
    schema = JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url))),
    data = probe(schema),
    budgets = {}
  const add = (path, frame, style) => {
    if (!path?.startsWith('data.')) return
    const key = path.slice(5).replace(/\[\d+\]/g, '[]')
    let node = schema
    for (const part of key.replaceAll('[]', '.[]').split('.'))
      node = part === '[]' ? node?.items : node?.properties?.[part]
    if (node?.type !== 'string') return
    const v = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(1, Math.floor(((frame[3] - 0.025) * 72) / (style.sizePt * 1.5))),
    }
    if (!budgets[key] || v.widthIn < budgets[key].widthIn) budgets[key] = v
  }
  for (const [id, v] of Object.entries(family.variants)) {
    let cs
    try {
      cs = compileConsultingLayout(design, family, id, v, data)
    } catch {
      continue
    }
    for (const c of cs) {
      if (c.style) for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      if (c.kind === 'table')
        for (const binding of c.bindings)
          for (const p of binding.paths) add(p, binding.frame, design.consulting.styles.small)
      if (c.kind === 'chart')
        for (const p of c.inputPaths)
          add(p, [0, 0, c.frame[2] * 0.4, c.frame[3] / c.data.categories.length], {
            ...design.consulting.styles.small,
            sizePt: design.consulting.chart.fontPt,
          })
    }
  }
  if (!Object.keys(budgets).length) throw Error(type + ': no projection could be compiled')
  return budgets
}
export const CONSULTING_FAMILY = {
  key: 'consulting',
  name: 'consulting-editorial/v1',
  resolve: resolveConsultingDeck,
  assert: assertConsulting,
  checks: { 'consulting-language': checkConsulting },
  groups: {
    anchor: ['cover', 'decision'],
    evidence: ['profile', 'landscape', 'benchmark'],
    operating: ['achievements', 'product', 'audiences'],
    process: ['flow', 'roadmap'],
  },
  projectedBudgets: consultingProjectedBudgets,
  projectedCapacities(design, family) {
    const c = design.consulting.capacity
    return {
      cover: {},
      profile: { rows: c.history, metrics: c.metrics },
      achievements: { items: c.achievements },
      product: { kpis: c.kpis, capLeft: c.capabilities, capRight: c.capabilities },
      landscape: { comps: c.competitors },
      audiences: { cards: c.audiences, 'cards[].items': c.audienceItems },
      flow: { outputs: c.outputs, featLeft: c.capabilities, featRight: c.capabilities },
      benchmark: {
        tableRows: c.tableRows,
        'tableRows[]': c.tableColumns,
        'chartData.categories': c.categories,
        'chartData.series[].values': c.categories,
      },
      roadmap: { steps: c.steps },
      decision: { asks: c.asks },
    }[family.role]
  },
}
