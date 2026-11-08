import {
  BROADSIDE_COMPARE_LIMITS,
  compileBroadsideLayout,
  resolveBroadsideDeck,
} from './layouts.mjs'

// Registered page responsibilities and compositions. Geometry is owned by design.json.
export const BROADSIDE_LAYOUTS = {
  cover: { poster: ['title', 'subtitle'], reading: ['title', 'subtitle'] },
  chapter: { declaration: ['number', 'title', 'lead'] },
  statement: { wide: ['kicker', 'title'], rail: ['kicker', 'title'] },
  split: {
    'image-right': ['kicker', 'title', 'lead', 'bullets', 'image', 'caption'],
    'image-left': ['kicker', 'title', 'lead', 'bullets', 'image', 'caption'],
  },
  stats: { row: ['items'], register: ['items'] },
  fade: { stack: ['items', 'title'] },
  list: { split: ['kicker', 'title', 'items'], stacked: ['kicker', 'title', 'items'] },
  quote: {
    reading: ['kicker', 'quote', 'author', 'source'],
    wide: ['kicker', 'quote', 'author', 'source'],
  },
  compare: { equal: ['left', 'right'], weighted: ['left', 'right'] },
  bar: {
    column: ['title', 'caption', 'chart', 'source'],
    horizontal: ['title', 'caption', 'chart', 'source'],
  },
  flow: { horizontal: ['title', 'items'], vertical: ['title', 'items'] },
  donut: {
    'ring-left': ['title', 'chart', 'items', 'total', 'source'],
    'ring-right': ['title', 'chart', 'items', 'total', 'source'],
  },
  pyramid: { levels: ['title', 'items'] },
  timeline: { vertical: ['title', 'items'], horizontal: ['title', 'items'] },
  cycle: { loop: ['title', 'items'] },
  closing: { poster: ['title', 'contact'], wide: ['title', 'contact'] },
}
const names = [
  'Cover',
  'Chapter',
  'Statement',
  'Split',
  'Stats',
  'FadeList',
  'List',
  'Quote',
  'Compare',
  'BarChart',
  'Flow',
  'Donut',
  'Pyramid',
  'Timeline',
  'Cycle',
  'End',
]
const roles = Object.keys(BROADSIDE_LAYOUTS)
function assertBroadside(design, { assertFrame }) {
  const b = design.broadside
  if (Object.keys(b.families).length !== names.length)
    throw Error('Broadside requires all sixteen page roles')
  for (const [key, style] of Object.entries(b.styles)) {
    if (!design.fonts[style.role] || !design.colors[style.color])
      throw Error(`${key}: unregistered font/color role`)
    if (style.italic) throw Error('Broadside typography is upright')
  }
  for (const frame of Object.values(b.chrome)) assertFrame(design, frame, 'broadside.chrome')
  for (const [type, family] of Object.entries(b.families)) {
    const role = roles[names.findIndex((name) => type === `broadside${name}Slide`)]
    if (!role || family.role !== role) throw Error(`${type}: unregistered Broadside role`)
    const expectedMode = ['cover', 'chapter', 'stats', 'fade', 'flow', 'closing'].includes(role)
      ? 'orange'
      : 'dark'
    if (family.mode !== expectedMode) throw Error(`${type}: wrong register`)
    for (const [id, variant] of Object.entries(family.variants)) {
      const expected = BROADSIDE_LAYOUTS[role][id]
      if (
        !expected ||
        expected.length !== Object.keys(variant.regions).length ||
        expected.some((key) => !variant.regions[key])
      )
        throw Error(`${type}.${id}: unregistered composition`)
      if (!b.styles[variant.titleStyle]) throw Error(`${type}: unregistered title style`)
      for (const frame of Object.values(variant.regions))
        assertFrame(design, frame, `${type}.${id}`)
    }
    if (Object.keys(family.variants).length !== Object.keys(BROADSIDE_LAYOUTS[role]).length)
      throw Error(`${type}: missing registered composition`)
  }
  for (const [key, [min, max]] of Object.entries(b.capacity))
    if (!Number.isInteger(min) || !Number.isInteger(max) || min < 1 || min > max)
      throw Error(`${key}: invalid capacity`)
  for (const token of b.chart.pointColors)
    if (!design.colors[token]) throw Error('Unknown chart color token')
}
function checkBroadside(design, op, fail) {
  if (
    op.op === 'set-slide-background' &&
    ![design.colors.ink, design.colors.orange].includes(op.fill?.color)
  )
    fail('Broadside has only dark and orange registers')
  if (op.op === 'add-shape' && op.kind !== 'rectangle') fail('Unregistered Broadside shape')
  if (['add-freeform', 'add-table', 'add-image', 'add-group'].includes(op.op))
    fail('Unregistered Broadside object')
  if (op.op === 'add-chart' && !['column', 'bar', 'doughnut'].includes(op.kind))
    fail('Unregistered Broadside chart')
  if (op.op === 'set-chart') {
    if (op.view3D || op.roundedCorners) fail('Broadside charts are flat and square')
    if (
      (op.series ?? [])
        .flatMap((s) => s.points ?? [])
        .filter((p) => p.fill?.color === design.colors.orange).length > 1
    )
      fail('A chart has at most one orange focus')
  }
  if (op.op === 'set-shape' && parseFloat(op.line?.width) > 1)
    fail('Broadside structure uses hairlines')
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'fill' && !['solid', 'none'].includes(v.type)) fail('Broadside uses flat fills')
    if (key === 'font' && (v.italic || v.underline))
      fail('Broadside uses upright text without underlines')
    for (const [name, child] of Object.entries(v)) walk(child, name)
  }
  walk(op)
}
export function broadsideProbeData(design, family) {
  const many = (key, fn) =>
    Array.from({ length: design.broadside.capacity[key][1] }, (_, i) => fn(i))
  const chrome = { section: 'x', page: 'x', footerLeft: 'x', footerRight: 'x' },
    anchor = { number: 'x', author: 'x', context: 'x' },
    heading = { ...chrome, title: 'x' }
  const steps = (key) => many(key, () => ({ num: 'x', title: 'x', body: 'x' }))
  const side = () => ({
    label: 'x',
    title: 'x',
    body: 'x',
    bullets: many('compareBullets', () => 'x'),
  })
  return {
    cover: { ...anchor, label: 'x', title: 'x', subtitle: 'x' },
    chapter: { number: 'x', title: 'x', lead: 'x' },
    statement: { ...heading, kicker: 'x' },
    split: {
      ...heading,
      kicker: 'x',
      lead: 'x',
      bullets: many('splitBullets', () => 'x'),
      imageLabel: 'x',
      caption: 'x',
    },
    stats: { ...chrome, items: many('stats', () => ({ value: 'x', label: 'x', note: 'x' })) },
    fade: { ...anchor, title: 'x', items: many('fade', () => 'x') },
    list: { ...heading, kicker: 'x', items: many('bullets', () => 'x') },
    quote: { kicker: 'x', quote: 'x', author: 'x', source: 'x' },
    compare: { ...chrome, left: side(), right: side() },
    bar: {
      ...heading,
      caption: 'x',
      unit: 'x',
      source: 'x',
      seriesName: 'x',
      bars: many('bars', () => ({ label: 'x', value: 1 })),
    },
    flow: { ...heading, steps: steps('flow') },
    donut: {
      ...heading,
      unit: 'x',
      source: 'x',
      seriesName: 'x',
      total: 'x',
      items: many('donut', () => ({ label: 'x', value: 1 })),
    },
    pyramid: { ...heading, levels: many('levels', () => ({ name: 'x', desc: 'x' })) },
    timeline: { ...heading, events: many('events', () => ({ date: 'x', title: 'x', body: 'x' })) },
    cycle: { ...heading, steps: steps('cycle') },
    closing: { ...anchor, label: 'x', title: 'x', contact: 'x' },
  }[family.role]
}
export function broadsideProjectedBudgets(design, family) {
  const [id, variant] = Object.entries(family.variants)[0],
    data = broadsideProbeData(design, family)
  const components = compileBroadsideLayout(design, family, id, variant, data),
    budgets = {}
  const add = (path, frame, style) => {
    budgets[path.replace(/\[\d+\]/g, '[]')] = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(
        1,
        Math.floor(
          ((frame[3] - 0.03) * 72) / (style.sizePt * Math.max(1.45, style.lineHeight * 1.2)),
        ),
      ),
    }
  }
  for (const c of components) {
    if (c.kind === 'text' && c.path && !/^data\.steps\[\d+\]$/.test(c.path)) {
      const frame = [...c.frame],
        field = c.path.split('.').at(-1)
      // A one-character projection fixture must not collapse dynamic comparison capacity.
      if (family.role === 'compare' && BROADSIDE_COMPARE_LIMITS[field])
        frame[3] = BROADSIDE_COMPARE_LIMITS[field]
      add(c.path.replace(/^data\./, ''), frame, c.style)
    }
    if (c.kind === 'chart') {
      const style = { sizePt: design.broadside.chart.fontPt, lineHeight: 1.2 }
      add('seriesName', [0, 0, 6, 0.4], style)
      add('unit', family.role === 'bar' ? variant.regions.caption : [0, 0, 1.2, 0.4], style)
      if (family.role === 'bar')
        add('bars[].label', [0, 0, c.frame[2] / data.bars.length - 0.15, 0.55], style)
    }
  }
  return budgets
}
export const BROADSIDE_FAMILY = {
  key: 'broadside',
  name: 'broadside-poster/v1',
  resolve: resolveBroadsideDeck,
  assert: assertBroadside,
  checks: { 'broadside-language': checkBroadside },
  groups: {
    anchor: ['cover', 'chapter', 'fade', 'closing'],
    statement: ['statement', 'quote', 'list'],
    evidence: ['stats', 'bar', 'donut', 'pyramid', 'timeline'],
    process: ['split', 'compare', 'flow', 'cycle'],
  },
  projectedBudgets: broadsideProjectedBudgets,
  projectedCapacities(design, family) {
    const c = design.broadside.capacity
    return (
      {
        split: { bullets: c.splitBullets },
        stats: { items: c.stats },
        fade: { items: c.fade },
        list: { items: c.bullets },
        compare: { 'left.bullets': c.compareBullets, 'right.bullets': c.compareBullets },
        bar: { bars: c.bars },
        donut: { items: c.donut },
        flow: { steps: c.flow },
        cycle: { steps: c.cycle },
        pyramid: { levels: c.levels },
        timeline: { events: c.events },
      }[family.role] ?? {}
    )
  },
}
