import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileJournalLayout, resolveJournalDeck } from './layouts.mjs'
export const JOURNAL_LAYOUTS = {
  cover: {
    angular: ['hero', 'field', 'strip', 'summary', 'markers'],
    inset: ['hero', 'field', 'strip', 'summary', 'markers'],
  },
  outlook: { leadLeft: ['metric', 'plot', 'notes'], leadRight: ['metric', 'plot', 'notes'] },
  audience: { leadLeft: ['lead', 'table', 'note'], leadBottom: ['lead', 'table', 'note'] },
  calendar: { horizontal: ['phases', 'allocation'], vertical: ['phases', 'allocation'] },
  journey: { arc: ['route'], linear: ['route'] },
  anatomy: {
    center: ['sample', 'left', 'right', 'plot'],
    offset: ['sample', 'left', 'right', 'plot'],
  },
  results: { rail: ['outcomes', 'outputs', 'kpis'], band: ['outcomes', 'outputs', 'kpis'] },
  roadmap: {
    rail: ['allocation', 'targets', 'actions', 'rail'],
    stacked: ['allocation', 'targets', 'actions', 'rail'],
  },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url), 'utf8'))
export function journalSpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties).map(([k, v]) => [k, journalSpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from({ length: maximum ? s.maxItems : s.minItems }, (_, i) =>
      journalSpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
export function validateJournalData(type, data, path) {
  const schema = schemaFor(type)
  assertDesignValue(data, schema, schema, path)
}
function assertJournal(design, { assertFrame }) {
  const b = design.journal,
    seen = new Set()
  for (const [role, pair] of Object.entries({
    display: ['Arial', 'Arial Unicode MS'],
    body: ['Georgia', 'Songti SC'],
    numeral: ['Arial', 'Arial Unicode MS'],
  }))
    if (design.fonts[role]?.latin !== pair[0] || design.fonts[role]?.eastAsian !== pair[1])
      throw Error(`${role}: unregistered Journal font pair`)
  for (const [k, v] of Object.entries({
    paper: 'EFEBE5',
    ink: '246B81',
    accent: 'F8AA98',
    pale: 'B0D0D9',
    highlight: 'F8DFD7',
    deep: '164C5D',
  }))
    if (design.colors[k] !== v) throw Error(`Teal Journal identity requires ${k} ${v}`)
  if (Object.keys(b.families).length !== 8) throw Error('Journal requires eight registered roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = JOURNAL_LAYOUTS[f.role]
    if (!type.startsWith('journal') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate journal role`)
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
  for (const [name, f] of Object.entries(b.chrome)) assertFrame(design, f, `journal.chrome.${name}`)
  for (const [name, v] of Object.entries(b.capacity))
    if (v.length !== 2 || v.some((n) => !Number.isInteger(n) || n < 1) || v[1] < v[0])
      throw Error(`${name}: invalid capacity`)
}
function checkJournal(design, op, fail) {
  const name = op.name ?? op.shape?.name ?? ''
  if (op.op === 'add-chart' && (op.kind !== 'bar' || !/_Comparison$/.test(name)))
    fail('Journal registers one native comparison chart family')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Journal uses square fields and functional circular endpoints')
  if (
    op.op === 'add-freeform' &&
    !/(CoverAngularField|CoverCoralEdge|JourneyTrack|JourneySegment\d+)$/.test(name)
  )
    fail('Unregistered journal path')
  if (['add-image', 'add-group'].includes(op.op))
    fail('External images/groups are not registered in Journal 1.0')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Journal requires warm paper')
  if (op.op === 'set-chart' && op.view3D) fail('Journal prohibits 3D')
  if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
    fail('Journal uses open horizontal table rules')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font' && v.italic) fail('Journal typography must remain upright')
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Journal prohibits decorative fills')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
function budgets(design, family) {
  const type = Object.keys(design.journal.families).find(
      (k) => design.journal.families[k] === family,
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
      cs = compileJournalLayout(design, family, id, v, journalSpecimen(schema))
    } catch {
      continue
    }
    count++
    for (const c of cs) {
      if (c.bindings?.length)
        for (const bind of c.bindings) for (const p of bind.paths) add(p, bind.frame, bind.style)
      else if (c.style)
        for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / 4, 0.5], design.journal.styles.small)
    }
  }
  if (!count) throw Error(`${type}: no valid projection specimen`)
  return out
}
export const JOURNAL_FAMILY = {
  key: 'journal',
  name: 'teal-editorial/v1',
  assert: assertJournal,
  resolve: (d, c) => resolveJournalDeck(d, c, { validateData: validateJournalData }),
  checks: { 'journal-language': checkJournal },
  groups: {
    anchor: ['cover', 'roadmap'],
    judgment: ['outlook', 'results'],
    evidence: ['audience', 'anatomy'],
    process: ['calendar', 'journey'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.journal.capacity
    return {
      cover: { markers: c.markers },
      outlook: { points: c.points, notes: c.notes },
      audience: { columns: c.columns, rows: c.rows, 'rows[]': c.columns },
      calendar: { phases: c.phases, allocation: c.allocation },
      journey: { steps: c.steps },
      anatomy: { annotations: c.annotations },
      results: { outcomes: c.outcomes, outputs: c.outputs, kpis: c.kpis },
      roadmap: { allocation: c.allocation, targets: c.targets, actions: c.actions },
    }[f.role]
  },
}
