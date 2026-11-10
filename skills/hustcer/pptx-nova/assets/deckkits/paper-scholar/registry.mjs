import { readFileSync } from 'node:fs'
import { assertDesignValue } from '../shared/design-contract.mjs'
import { compileScholarLayout, resolveScholarDeck } from './layouts.mjs'
export const SCHOLAR_LAYOUTS = {
  cover: {
    contour: ['hero', 'subtitle', 'field', 'badge', 'metadata'],
    inset: ['hero', 'subtitle', 'field', 'badge', 'metadata'],
  },
  methods: { horizontal: ['steps', 'evidence', 'note'], vertical: ['steps', 'evidence', 'note'] },
  finding: { leadLeft: ['lead', 'comparison'], leadRight: ['lead', 'comparison'] },
  chart: { plotLeft: ['plot', 'notes', 'note'], plotRight: ['plot', 'notes', 'note'] },
  mechanism: {
    center: ['definitions', 'plot', 'model'],
    plotLeft: ['definitions', 'plot', 'model'],
  },
  segments: { full: ['table', 'summary', 'takeaway'], rail: ['table', 'summary', 'takeaway'] },
  case: {
    portrait: ['notes', 'asset', 'result', 'note'],
    resultFirst: ['notes', 'asset', 'result', 'note'],
  },
  closing: { bands: ['actions', 'review'], ledger: ['actions', 'review'] },
}
const schemaFor = (type) =>
  JSON.parse(readFileSync(new URL(`./schemas/${type}.schema.json`, import.meta.url)))
export function scholarSpecimen(s, index = 0, maximum = false) {
  if (s['x-slotProbeSequence'])
    return s['x-slotProbeSequence'][index % s['x-slotProbeSequence'].length]
  if (s['x-slotProbeValue'] !== undefined) return s['x-slotProbeValue']
  if (s.enum) return s.enum[0]
  if (s.type === 'object')
    return Object.fromEntries(
      Object.entries(s.properties).map(([k, v]) => [k, scholarSpecimen(v, index, maximum)]),
    )
  if (s.type === 'array')
    return Array.from({ length: maximum ? s.maxItems : s.minItems }, (_, i) =>
      scholarSpecimen(s.items, i, maximum),
    )
  if (s.type === 'number') return Math.max(1, s.minimum ?? 0, (s.exclusiveMinimum ?? 0) + 1)
  return 'x'
}
export function validateScholarData(type, data, path) {
  const schema = schemaFor(type)
  assertDesignValue(data, schema, schema, path)
  if (
    type === 'scholarMechanismSlide' &&
    data.ticks.some((v, i) => v > data.maxTime || (i && v <= data.ticks[i - 1]))
  )
    throw Error(`${path}.ticks: strictly increasing values within maxTime required`)
  if (type === 'scholarSegmentsSlide') {
    if (data.rows.some((v) => v.cells.length !== data.headers.length - 1))
      throw Error(`${path}.rows: every row must match header count`)
    if (
      data.rows.some(
        (v) =>
          v.emphasisColumn !== undefined &&
          (!Number.isInteger(v.emphasisColumn) || v.emphasisColumn >= data.headers.length),
      )
    )
      throw Error(`${path}.rows: emphasisColumn outside value columns`)
  }
}
function assertScholar(design, { assertFrame }) {
  const b = design.scholar,
    seen = new Set()
  for (const [k, v] of Object.entries({
    paper: 'FBFAF7',
    ink: '456F2F',
    body: '536676',
    muted: '4D5D69',
    accent: 'F5967D',
    accentText: '8F3D2B',
    pale: 'E5F1DE',
    blush: 'F7DDD5',
    rule: 'BAC6C9',
    contour: 'B7CDAB',
    history: 'ABC19D',
    white: 'FFFFFF',
    badgeText: '243A19',
  }))
    if (design.colors[k] !== v) throw Error(`Scholar identity requires ${k} ${v}`)
  if (Object.keys(design.colors).length !== 13) throw Error('Unregistered Scholar palette token')
  for (const [name, font] of Object.entries(design.fonts))
    if (font.latin !== 'Arial' || font.eastAsian !== 'Arial Unicode MS')
      throw Error(`${name}: unregistered Scholar font pair`)
  if (Object.keys(b.families).length !== 8) throw Error('Scholar requires eight roles')
  for (const [type, f] of Object.entries(b.families)) {
    const expected = SCHOLAR_LAYOUTS[f.role]
    if (!type.startsWith('scholar') || !expected || seen.has(f.role))
      throw Error(`${type}: unknown or duplicate Scholar role`)
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
      throw Error(`${name}: readable upright style required`)
  for (const [name, frame] of Object.entries(b.chrome))
    assertFrame(design, frame, `scholar.chrome.${name}`)
  for (const [name, v] of Object.entries(b.capacity))
    if (v.length !== 2 || v.some((n) => !Number.isInteger(n) || n < 1) || v[1] < v[0])
      throw Error(`${name}: invalid capacity`)
}
function checkScholar(design, op, fail) {
  const name = op.name ?? op.shape?.name ?? ''
  if (op.op === 'add-chart' && (op.kind !== 'column' || !name.endsWith('_EvidenceChart')))
    fail('Scholar registers native single-series columns')
  if (op.op === 'set-chart' && (op.view3D || op.series?.length > 1))
    fail('Scholar does not register 3D or additional evidence series')
  if (op.op === 'add-shape' && !['rectangle', 'ellipse'].includes(op.kind))
    fail('Scholar uses functional rectangles and circles')
  if (
    op.op === 'add-image' &&
    (!/_(ActionIcon|SegmentIcon)\d+$/.test(name) ||
      op.mimeType !== 'image/svg+xml' ||
      !op.bytesBase64)
  )
    fail('Scholar permits bundled semantic SVG icons only; no photo ingestion')
  if (op.op === 'add-group') fail('Scholar group input is not registered')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Scholar requires warm paper')
  if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
    fail('Scholar table tints are explicit semantic rows')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'font') {
      if (v.italic) fail('Scholar typography stays upright')
      if (parseFloat(v.size) >= 70 && !name.endsWith('_MetricValue'))
        fail('Scholar permits one registered large metric, not a second focal number')
    }
    if (key === 'fill' && ['gradient', 'picture', 'pattern'].includes(v.type))
      fail('Scholar prohibits decorative fills')
    for (const [k, x] of Object.entries(v)) walk(x, k)
  }
  walk(op)
}
function budgets(design, family) {
  const type = Object.keys(design.scholar.families).find(
      (k) => design.scholar.families[k] === family,
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
  for (const [id, v] of Object.entries(family.variants))
    for (const c of compileScholarLayout(design, family, id, v, scholarSpecimen(schema))) {
      if (c.bindings?.length)
        for (const bind of c.bindings) for (const p of bind.paths) add(p, bind.frame, bind.style)
      else if (c.style)
        for (const p of c.paths ?? [c.path]) add(p, c.allocatedFrame ?? c.frame, c.style)
      for (const p of c.inputPaths ?? [])
        add(p, [0, 0, c.frame[2] / 5, 0.5], design.scholar.styles.small)
    }
  return out
}
export const SCHOLAR_FAMILY = {
  key: 'scholar',
  name: 'paper-scholar/v1',
  assert: assertScholar,
  resolve: (d, c) => resolveScholarDeck(d, c, { validateData: validateScholarData }),
  checks: { 'scholar-language': checkScholar },
  groups: {
    anchor: ['cover', 'closing'],
    method: ['methods', 'mechanism'],
    evidence: ['finding', 'chart', 'segments'],
    case: ['case'],
  },
  projectedBudgets: budgets,
  projectedCapacities(d, f) {
    const c = d.scholar.capacity
    return {
      cover: {},
      methods: { steps: c.steps, sources: c.sources },
      finding: { notes: c.notes },
      chart: { points: c.points, notes: c.notes },
      mechanism: { definitions: c.definitions, series: [2, 2], ticks: c.ticks },
      segments: { headers: c.columns, rows: c.rows, 'rows[].cells': [2, 4] },
      case: { notes: [3, 3] },
      closing: { actions: c.actions, review: c.review },
    }[f.role]
  },
}
