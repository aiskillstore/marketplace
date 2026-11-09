import { compileSwissLayout, resolveSwissDeck } from './layouts.mjs'

export const SWISS_LAYOUTS = {
  cover: {
    poster: ['title', 'subtitle', 'tag', 'dot'],
    upper: ['title', 'subtitle', 'tag', 'dot'],
  },
  quote: {
    bracket: ['quote', 'body', 'author', 'source', 'mark'],
    wide: ['quote', 'body', 'author', 'source'],
  },
  timeline: {
    horizontal: ['items', 'callout'],
    vertical: ['items', 'callout'],
  },
  progress: {
    horizontal: ['items', 'callout'],
    vertical: ['items', 'callout'],
  },
  principles: { matrix: ['items'] },
  people: { matrix: ['items'] },
  columns: { columns: ['items'] },
  brands: { matrix: ['items'] },
  profile: { left: ['identity', 'events'], reversed: ['identity', 'events'] },
  typeface: { columns: ['items'] },
  gridTypes: { quadrants: ['items'] },
  system: { annotated: ['base', 'diagram'], reversed: ['base', 'diagram'] },
  statement: {
    right: ['label', 'title', 'subtitle', 'body', 'dot'],
    left: ['label', 'title', 'subtitle', 'body', 'dot'],
  },
  table: { full: ['table', 'source'], rail: ['table', 'source'] },
  closing: {
    lower: ['titleA', 'titleB', 'subtitle', 'footerL', 'footerR', 'dots'],
    upper: ['titleA', 'titleB', 'subtitle', 'footerL', 'footerR', 'dots'],
  },
}
const fieldForRole = {
  timeline: 'steps',
  progress: 'steps',
  principles: 'items',
  people: 'people',
  columns: 'items',
  brands: 'brands',
  profile: 'events',
  typeface: 'cards',
  gridTypes: 'items',
  table: 'rows',
}
function assertSwiss(design, { assertFrame }) {
  const b = design.swiss
  if (Object.keys(b.families).length !== Object.keys(SWISS_LAYOUTS).length)
    throw Error('Swiss requires all fifteen roles')
  const seen = new Set()
  for (const [type, f] of Object.entries(b.families)) {
    const expected = SWISS_LAYOUTS[f.role]
    if (!type.startsWith('swiss') || !expected || seen.has(f.role))
      throw Error(`${type}: unregistered/duplicate Swiss role`)
    seen.add(f.role)
    if (Object.keys(f.variants).join('|') !== Object.keys(expected).join('|'))
      throw Error(`${type}: registered layouts changed`)
    for (const [id, v] of Object.entries(f.variants)) {
      if (!b.styles[v.titleStyle]) throw Error(`${type}.${id}: unknown title style`)
      if (
        Object.keys(v.regions).length !== expected[id].length ||
        expected[id].some((k) => !v.regions[k])
      )
        throw Error(`${type}.${id}: unregistered regions`)
      for (const [k, frame] of Object.entries(v.regions))
        assertFrame(design, frame, `${type}.${id}.${k}`)
    }
  }
  for (const [k, s] of Object.entries(b.styles)) {
    if (!design.fonts[s.role] || !design.colors[s.color] || s.italic)
      throw Error(`${k}: Swiss requires registered upright fonts and colors`)
  }
  for (const k of [
    'hero',
    'title',
    'quote',
    'statement',
    'itemTitle',
    'denseTitle',
    'body',
    'small',
    'label',
    'source',
    'index',
    'year',
    'specimen',
    'monogram',
    'table',
    'tableHead',
  ])
    if (!b.styles[k]) throw Error(`Missing Swiss style ${k}`)
  for (const [k, range] of Object.entries(b.capacity))
    if (
      range.length !== 2 ||
      range.some((v) => !Number.isInteger(v) || v < 1) ||
      range[1] < range[0]
    )
      throw Error(`${k}: invalid capacity`)
  if (b.spacing.rulePt > 1) throw Error('Swiss rules must remain fine')
  for (const [k, f] of Object.entries(b.chrome)) assertFrame(design, f, `swiss.chrome.${k}`)
}
function checkSwiss(design, op, fail) {
  if (['add-chart', 'add-group', 'add-freeform'].includes(op.op))
    fail('No registered Swiss chart/group/freeform component')
  if (op.op === 'add-shape' && !['oval', 'rectangle'].includes(op.kind))
    fail('Unregistered Swiss shape')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill.color !== design.colors.paper)
  )
    fail('Swiss requires white paper')
  if (op.op === 'set-shape' && parseFloat(op.line?.width) > 1) fail('Swiss rules must remain fine')
  if (op.op === 'set-run' && op.font?.italic) fail('Swiss uses upright sans-serif type')
  if (op.op === 'set-table' && (op.style?.horizontalBanding || op.style?.verticalBanding))
    fail('Swiss tables use explicit horizontal rules')
  const walk = (v, k = '') => {
    if (!v || typeof v !== 'object') return
    if (k === 'fill' && v.type && !['solid', 'none'].includes(v.type)) fail('Swiss uses flat fills')
    if (k === 'font' && v.italic) fail('Swiss uses upright type')
    for (const [key, c] of Object.entries(v)) walk(c, key)
  }
  walk(op)
}
// Neutral probes publish planning hints; real content must still pass the resolver.
export function swissProjectedBudgets(design, family) {
  const b = design.swiss,
    many = (role, fn) => Array.from({ length: b.capacity[role][1] }, fn),
    basic = { eyebrow: 'x', title: 'x', subtitle: 'x' },
    event = () => ({ year: 'x', title: 'x', body: 'x' }),
    data = {
      cover: { eyebrow: 'x', title: 'x', subtitle: 'x', tag: 'x', footer: 'x' },
      quote: { quote: 'x', body: 'x', author: 'x', source: 'x' },
      timeline: {
        ...basic,
        steps: many('timeline', event),
        calloutTitle: 'x',
        callout: 'x',
      },
      progress: {
        ...basic,
        steps: many('progress', event),
        calloutTitle: 'x',
        callout: 'x',
      },
      principles: {
        ...basic,
        items: many('principles', () => ({
          num: 'x',
          title: 'x',
          subtitle: 'x',
          body: 'x',
        })),
      },
      people: {
        ...basic,
        people: many('people', () => ({ name: 'x', years: 'x', body: 'x' })),
      },
      columns: {
        ...basic,
        items: many('columns', () => ({
          title: 'x',
          subtitle: 'x',
          body: 'x',
          examples: 'x',
          note: 'x',
        })),
      },
      brands: {
        ...basic,
        brands: many('brands', () => ({
          name: 'x',
          meta: 'x',
          body: 'x',
          icon: 'building',
        })),
      },
      profile: {
        ...basic,
        initials: 'x',
        name: 'x',
        bio: 'x',
        meta: 'x',
        events: many('profile', event),
      },
      typeface: {
        ...basic,
        sampleText: 'x',
        cards: many('typeface', (_, i) => ({
          name: 'x',
          meta: 'x',
          weight: 'x',
          lead: 'x',
          body: 'x',
          specimenStyle: 'regular',
          ...(i ? { sampleText: 'x' } : {}),
        })),
      },
      gridTypes: {
        ...basic,
        items: many('gridTypes', () => ({
          num: 'x',
          title: 'x',
          subtitle: 'x',
          body: 'x',
          diagram: 'columns',
        })),
      },
      system: {
        ...basic,
        baseNote: 'x',
        callout: 'x',
        model: {
          baseUnit: 1,
          unit: 'u',
          columnUnits: 16,
          gapUnits: 2,
          rowUnits: 6,
          columns: 4,
          rows: 5,
        },
        labels: {
          base: 'x',
          column: 'x',
          gap: 'x',
          row: 'x',
          headline: 'x',
          image: 'x',
          text: 'x',
        },
      },
      statement: { label: 'x', title: 'x', subtitle: 'x', body: 'x' },
      table: {
        ...basic,
        columns: Array.from({ length: b.capacity.columnsTable[1] }, () => ({
          label: 'x',
        })),
        rows: many('rows', () => Array(b.capacity.columnsTable[1]).fill('x')),
        source: 'x',
      },
      closing: {
        eyebrow: 'x',
        titleA: 'x',
        titleB: 'x',
        subtitle: 'x',
        footerL: 'x',
        footerR: 'x',
      },
    }[family.role],
    budgets = {}
  const [id, v] = Object.entries(family.variants)[0]
  const add = (path, frame, style) => {
    if (!path || path.includes('structural.') || path.includes('.model.')) return
    const key = path.replace(/^data\./, '').replace(/\[\d+\]/g, '[]')
    const value = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(1, Math.floor((frame[3] * 72) / (style.sizePt * 1.5))),
    }
    if (!budgets[key] || value.widthIn < budgets[key].widthIn) budgets[key] = value
  }
  for (const c of compileSwissLayout(design, family, id, v, data)) {
    if (c.path && c.style)
      add(c.path, c.kind === 'owned' ? [0, 0, c.frame[2] - 0.1, c.frame[3]] : c.frame, c.style)
    if (c.kind === 'table')
      for (let j = 0; j < c.columns.length; j++) {
        add('columns[].label', [0, 0, c.widths[j] - 0.2, c.rowHeights[0]], b.styles.tableHead)
        add('rows[][]', [0, 0, c.widths[j] - 0.2, c.rowHeights[1]], b.styles.table)
      }
  }
  return budgets
}
export const SWISS_FAMILY = {
  key: 'swiss',
  name: 'swiss-typographic/v1',
  resolve: resolveSwissDeck,
  assert: assertSwiss,
  checks: { 'swiss-language': checkSwiss },
  groups: {
    anchor: ['cover', 'closing'],
    statement: ['quote', 'statement'],
    timeline: ['timeline', 'progress'],
    register: ['principles', 'people', 'columns', 'brands', 'profile'],
    system: ['typeface', 'gridTypes', 'system'],
    evidence: ['table'],
  },
  projectedBudgets: swissProjectedBudgets,
  projectedCapacities(design, family) {
    const field = fieldForRole[family.role]
    return field
      ? {
          [field]: design.swiss.capacity[family.role === 'table' ? 'rows' : family.role],
          ...(family.role === 'table' ? { columns: design.swiss.capacity.columnsTable } : {}),
        }
      : {}
  },
}
