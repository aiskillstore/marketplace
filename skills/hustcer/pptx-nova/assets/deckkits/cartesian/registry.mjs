import { compileCartesianLayout, resolveCartesianDeck } from './layouts.mjs'

export const CARTESIAN_LAYOUTS = {
  cover: { hero: ['label', 'title', 'subtitle'], wide: ['label', 'title', 'subtitle'] },
  agenda: {
    split: ['label', 'title', 'body', 'items'],
    stacked: ['label', 'title', 'body', 'items'],
  },
  statement: {
    centered: ['quoteMark', 'quote', 'attribution'],
    reading: ['quoteMark', 'quote', 'attribution'],
  },
  column: {
    rail: ['label', 'title', 'body', 'chart', 'unit', 'source'],
    wide: ['label', 'title', 'body', 'chart', 'unit', 'source'],
  },
  image: {
    'image-left': ['image', 'label', 'title', 'paragraphs', 'stats'],
    'image-right': ['image', 'label', 'title', 'paragraphs', 'stats'],
  },
  cards: { row: ['label', 'title', 'items'], register: ['label', 'title', 'items'] },
  line: {
    wide: ['label', 'title', 'body', 'chart', 'unit', 'source'],
    rail: ['label', 'title', 'body', 'chart', 'unit', 'source'],
  },
  timeline: { horizontal: ['label', 'title', 'items'], vertical: ['label', 'title', 'items'] },
  team: { row: ['label', 'title', 'items'] },
  closing: { centered: ['label', 'title', 'cta', 'contact'] },
  exhibit: {
    wide: ['label', 'title', 'body', 'stage', 'source'],
    rail: ['label', 'title', 'body', 'stage', 'source'],
  },
}
const PAGE_ROLES = {
  Cover: 'cover',
  Agenda: 'agenda',
  Statement: 'statement',
  BarChart: 'column',
  ImageStats: 'image',
  Cards: 'cards',
  LineChart: 'line',
  Timeline: 'timeline',
  Team: 'team',
  Closing: 'closing',
  Exhibit: 'exhibit',
  Analytical: 'exhibit',
  Comparison: 'exhibit',
  Scene: 'exhibit',
  Formula: 'exhibit',
}

function assertCartesian(design, { assertFrame }) {
  const b = design.cartesian
  for (const name of [
    'hero',
    'cover',
    'closing',
    'title',
    'quote',
    'body',
    'subtitle',
    'label',
    'source',
    'number',
    'metric',
    'itemTitle',
    'small',
    'marker',
    'initial',
    'quoteMark',
  ])
    if (!b.styles[name]) throw Error(`Missing Cartesian style ${name}`)
  if (Object.keys(b.families).length !== Object.keys(PAGE_ROLES).length)
    throw Error('Cartesian requires all registered page roles')
  for (const [name, style] of Object.entries(b.styles)) {
    if (!design.fonts[style.role] || !design.colors[style.color])
      throw Error(`${name}: unregistered font/color role`)
    if (style.italic || (style.role === 'display' && style.bold))
      throw Error('Cartesian display text is regular upright')
  }
  for (const [type, family] of Object.entries(b.families)) {
    const role = PAGE_ROLES[type.replace(/^cartesian|Slide$/g, '')]
    if (!role || family.role !== role) throw Error(`${type}: unregistered Cartesian role`)
    for (const [id, v] of Object.entries(family.variants)) {
      const expected = CARTESIAN_LAYOUTS[role][id]
      if (
        !expected ||
        expected.length !== Object.keys(v.regions).length ||
        expected.some((k) => !v.regions[k])
      )
        throw Error(`${type}.${id}: unregistered composition`)
      if (!b.styles[v.titleStyle]) throw Error(`${type}: unknown title style`)
      for (const f of Object.values(v.regions)) assertFrame(design, f, `${type}.${id}`)
      for (const decoration of v.decorations) {
        assertFrame(design, decoration.frame, `${type}.${id}.decoration`)
        if (!design.colors[decoration.color]) throw Error('Unknown decoration color token')
      }
    }
    if (!Object.keys(family.variants).length) throw Error(`${type}: no layouts`)
  }
  for (const [key, [min, max]] of Object.entries(b.capacity))
    if (!Number.isInteger(min) || !Number.isInteger(max) || min < 1 || min > max)
      throw Error(`${key}: invalid capacity`)
}
function checkCartesian(design, op, fail) {
  // Exhibit specimens have their own bounded renderer; editorial chrome remains unchanged.
  if (/^S\d+_Exhibit/.test(op.name ?? op.shape?.name ?? '')) return
  if (op.op === 'set-shape' && parseFloat(op.line?.width) > 1)
    fail('Cartesian structural outlines are hairlines')
  if (op.op === 'add-shape' && !['rectangle', 'oval'].includes(op.kind))
    fail('Unregistered Cartesian shape')
  if (op.op === 'add-chart' && !['column', 'line'].includes(op.kind))
    fail('Unregistered Cartesian chart')
  if (op.op === 'add-table' || op.op === 'add-freeform' || op.op === 'add-group')
    fail('Unregistered Cartesian object')
  if (op.op === 'add-image' && !/^S\d+_ImageAsset$/.test(op.name ?? ''))
    fail('Images require the editorial asset slot')
  if (op.op === 'set-chart') {
    if (op.view3D || op.roundedCorners) fail('Cartesian plots are flat and square')
    if (op.series?.some((s) => s.smooth)) fail('Curves may not smooth source observations')
    for (const series of op.series ?? [])
      if (series.series === 1 && series.line && series.line.dash !== 'dash')
        fail('The comparison series uses a dashed outline')
  }
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'fill' && !['solid', 'none'].includes(v.type)) fail('Cartesian uses flat fill')
    if (key === 'font' && v.italic) fail('Cartesian uses upright text')
    if (key === 'font' && v.name === design.fonts.display.latin && v.bold)
      fail('Cartesian display is regular')
    for (const [k, c] of Object.entries(v)) walk(c, k)
  }
  walk(op)
}
// Schema projections use neutral maximum-count inputs and the same compiler as builds.
// They are discovery hints; the resolver still checks every actual text/geometry instance.
export function cartesianProjectedBudgets(design, family) {
  const n = (key) => design.cartesian.capacity[key][1],
    many = (key, fn) => Array.from({ length: n(key) }, fn)
  const basic = { label: 'x', title: 'x', body: 'x' },
    data = {
      cover: { label: 'x', title: 'x', subtitle: 'x' },
      agenda: { ...basic, items: many('agenda', () => ({ number: 'x', text: 'x' })) },
      statement: { quote: 'x', quoteMark: 'x', attribution: 'x' },
      column: {
        ...basic,
        unit: 'x',
        source: 'x',
        chart: {
          categories: many('columnPoints', () => 'x'),
          series: [
            { name: 'x', values: many('columnPoints', () => 1) },
            { name: 'x', values: many('columnPoints', () => 2) },
          ],
        },
      },
      image: {
        label: 'x',
        title: 'x',
        imageLabel: 'x',
        paragraphs: many('paragraphs', () => 'x'),
        stats: many('stats', () => ({ value: 'x', label: 'x' })),
      },
      cards: {
        label: 'x',
        title: 'x',
        cards: many('cards', () => ({ marker: 'x', title: 'x', body: 'x' })),
      },
      line: {
        ...basic,
        unit: 'x',
        source: 'x',
        chart: {
          categories: many('linePoints', () => 'x'),
          series: [
            { name: 'x', values: many('linePoints', () => 1) },
            { name: 'x', values: many('linePoints', () => 2) },
          ],
        },
      },
      timeline: {
        label: 'x',
        title: 'x',
        items: many('timeline', () => ({ phase: 'x', title: 'x', body: 'x' })),
      },
      team: {
        label: 'x',
        title: 'x',
        members: many('team', () => ({ initial: 'x', name: 'x', role: 'x' })),
      },
      closing: { label: 'x', title: 'x', cta: 'x', contact: 'x' },
      exhibit: {
        ...basic,
        source: 'x',
        specimen: { kind: 'nodes', nodes: [{ text: 'x', x: 0, y: 0, w: 1, h: 1 }] },
      },
    }[family.role]
  const [id, v] = Object.entries(family.variants)[0],
    components = compileCartesianLayout(design, family, id, v, data),
    budgets = {}
  const add = (path, frame, style) => {
    budgets[path.replace(/\[\d+\]/g, '[]')] = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(
        1,
        Math.floor((frame[3] * 72) / (style.sizePt * Math.max(1.5, style.lineHeight * 1.2))),
      ),
    }
  }
  for (const c of components) {
    if (c.path) {
      const field = c.path.replace(/^data\./, ''),
        frame = [...c.frame]
      if (field.startsWith('paragraphs[')) {
        const heading = components.find((c) => c.name === 'Title')
        const available =
          v.regions.paragraphs[1] +
          v.regions.paragraphs[3] -
          (heading.frame[1] + heading.frame[3] + design.cartesian.spacing.paragraphGap)
        frame[3] =
          (available - design.cartesian.spacing.paragraphGap * (n('paragraphs') - 1)) /
          n('paragraphs')
      }
      add(field, frame, c.style)
    }
    if (c.kind === 'image')
      add('imageLabel', [0, 0, c.frame[2] - 0.6, 0.3], design.cartesian.styles.source)
    if (c.kind === 'chart') {
      const style = { sizePt: design.cartesian.chart.fontPt, lineHeight: 1.2 }
      add('chart.categories[]', [0, 0, c.frame[2] / c.data.categories.length - 0.15, 0.3], style)
      add('chart.series[].name', [0, 0, c.frame[2] / 2 - 0.2, 0.3], style)
    }
  }
  return budgets
}
export const CARTESIAN_FAMILY = {
  key: 'cartesian',
  name: 'cartesian-editorial/v1',
  resolve: resolveCartesianDeck,
  assert: assertCartesian,
  checks: { 'cartesian-language': checkCartesian },
  groups: {
    anchor: ['cover', 'closing'],
    statement: ['statement'],
    evidence: ['column', 'line', 'image', 'exhibit'],
    structure: ['agenda', 'cards', 'timeline', 'team'],
  },
  projectedBudgets: cartesianProjectedBudgets,
  projectedCapacities(design, family) {
    const c = design.cartesian.capacity
    if (['column', 'line'].includes(family.role)) {
      const limits = c[family.role === 'column' ? 'columnPoints' : 'linePoints']
      return { 'chart.categories': limits, 'chart.series[].values': limits }
    }
    return (
      {
        agenda: { items: c.agenda },
        cards: { cards: c.cards },
        image: { paragraphs: c.paragraphs, stats: c.stats },
        timeline: { items: c.timeline },
        team: { members: c.team },
      }[family.role] ?? {}
    )
  },
}
