import { compileLongTableLayout, resolveLongTableDeck } from './layouts.mjs'

// The bounded visual vocabulary, independent of any showcase business topic.
export const LONG_TABLE_LAYOUTS = {
  cover: {
    split: [
      'badge',
      'eyebrow',
      'title',
      'pills',
      'stats',
      'tagline',
      'description',
      'edition',
      'bigLabel',
      'bigMeta',
    ],
    verso: [
      'badge',
      'eyebrow',
      'title',
      'pills',
      'stats',
      'tagline',
      'description',
      'edition',
      'bigLabel',
      'bigMeta',
    ],
  },
  manifesto: {
    letter: ['badge', 'eyebrow', 'title', 'paragraphs', 'signature', 'source'],
    wide: ['badge', 'eyebrow', 'title', 'paragraphs', 'signature', 'source'],
  },
  index: { cards: ['title', 'subtitle', 'items'], register: ['title', 'subtitle', 'items'] },
  featured: {
    right: ['badge', 'eyebrow', 'title', 'body', 'pills', 'details'],
    left: ['badge', 'eyebrow', 'title', 'body', 'pills', 'details'],
  },
  menu: { ledger: ['title', 'subtitle', 'items'], programme: ['title', 'subtitle', 'items'] },
  quote: {
    centered: ['label', 'quote', 'author', 'role'],
    reading: ['label', 'quote', 'author', 'role'],
  },
  calendar: { ledger: ['title', 'subtitle', 'table'] },
  closing: {
    left: ['badge', 'eyebrow', 'title', 'body', 'actions', 'footer'],
    centered: ['badge', 'eyebrow', 'title', 'body', 'actions', 'footer'],
  },
}
const roles = ['Cover', 'Manifesto', 'Index', 'Featured', 'Menu', 'Quote', 'Calendar', 'Closing']
const capacityForRole = {
  manifesto: 'paragraphs',
  index: 'cards',
  featured: 'details',
  menu: 'menu',
  calendar: 'rows',
  closing: 'footer',
}
function assertLongTable(design, { assertFrame }) {
  const b = design.longTable
  if (Object.keys(b.families).length !== roles.length)
    throw Error('Long Table requires all eight roles')
  for (const key of [
    'hero',
    'title',
    'chapter',
    'quote',
    'cardTitle',
    'itemTitle',
    'body',
    'small',
    'label',
    'pill',
    'source',
    'edition',
    'table',
    'tableHead',
  ])
    if (!b.styles[key]) throw Error(`Missing Long Table style ${key}`)
  for (const [name, style] of Object.entries(b.styles)) {
    if (!design.fonts[style.role] || !design.colors[style.color])
      throw Error(`${name}: unknown font/color role`)
    if (style.color !== 'ink') throw Error(`${name}: Long Table text uses the single ink`)
    if (style.role === 'display' && (!style.bold || style.italic))
      throw Error(`${name}: display requires heavy upright type`)
    if (style.role === 'body' && style.sizePt < 10.5)
      throw Error(`${name}: body requires at least 10.5pt`)
  }
  for (const [type, f] of Object.entries(b.families)) {
    const role = roles.find((v) => type === `longTable${v}Slide`)?.toLowerCase()
    if (!role || f.role !== role) throw Error(`${type}: unregistered Long Table role`)
    if (Object.keys(f.variants).length !== Object.keys(LONG_TABLE_LAYOUTS[role]).length)
      throw Error(`${type}: missing registered layouts`)
    for (const [id, v] of Object.entries(f.variants)) {
      const expected = LONG_TABLE_LAYOUTS[role][id]
      if (
        !expected ||
        Object.keys(v.regions).length !== expected.length ||
        expected.some((k) => !v.regions[k])
      )
        throw Error(`${type}.${id}: unregistered composition`)
      if (!b.styles[v.titleStyle]) throw Error(`${type}.${id}: unknown title style`)
      for (const frame of Object.values(v.regions)) assertFrame(design, frame, `${type}.${id}`)
    }
  }
  for (const key of Object.values(capacityForRole)) {
    const [min, max] = b.capacity[key] ?? []
    if (!Number.isInteger(min) || !Number.isInteger(max) || min < 1 || max < min)
      throw Error(`${key}: invalid capacity`)
  }
  if (Math.abs(b.table.weights.reduce((n, v) => n + v, 0) - 1) > 0.00001)
    throw Error('Long Table column weights must sum to one')
  if (b.spacing.outlinePt > 1) throw Error('Long Table requires hairline outlines')
  assertFrame(design, b.chrome.page, 'Long Table page number')
}
function checkLongTable(design, op, fail) {
  if (['add-image', 'add-chart', 'add-group'].includes(op.op))
    fail('Long Table has no registered picture/chart/group component')
  if (op.op === 'add-shape' && !['oval', 'rectangle'].includes(op.kind))
    fail('Unregistered Long Table shape')
  if (
    op.op === 'add-freeform' &&
    !/^S\d+_(?:Pill\d+|Site|Cta|CalendarStatus\d+)$/.test(op.name ?? '')
  )
    fail('Freeforms are reserved for registered capsules')
  if (
    op.op === 'set-slide-background' &&
    (op.fill?.type !== 'solid' || op.fill?.color !== design.colors.paper)
  )
    fail('Long Table requires cream paper background')
  if (op.op === 'set-shape' && parseFloat(op.line?.width) > 1)
    fail('Long Table outlines are hairlines')
  if (op.op === 'set-run' && op.font) {
    if (op.font.color !== design.colors.ink) fail('Long Table text uses a single ink')
    if (op.font.name === design.fonts.display.latin && (!op.font.bold || op.font.italic))
      fail('Long Table display is heavy and upright')
  }
  const walk = (v, key = '') => {
    if (!v || typeof v !== 'object') return
    if (key === 'fill' && !['solid', 'none'].includes(v.type))
      fail('Long Table uses flat ink and paper')
    if (key === 'font' && v.color !== design.colors.ink) fail('Long Table text uses a single ink')
    for (const [k, c] of Object.entries(v)) walk(c, k)
  }
  walk(op)
}
export function longTableProjectedBudgets(design, family) {
  const b = design.longTable,
    n = (key) => b.capacity[key][1],
    many = (key, fn) => Array.from({ length: n(key) }, fn)
  const basic = { title: 'x', subtitle: 'x' },
    data = {
      cover: {
        edition: '1',
        editionLabel: 'x',
        title: 'x',
        pills: ['x', 'x'],
        stat: 'x',
        statNote: 'x',
        tagline: 'x',
        description: 'x',
        bigEdition: '1',
        bigLabel: 'x',
        bigMeta: 'x',
      },
      manifesto: {
        mark: '1',
        eyebrow: 'x',
        title: 'x',
        paragraphs: many('paragraphs', () => 'x'),
        signature: 'x',
        source: 'x',
      },
      index: {
        ...basic,
        cards: many('cards', () => ({
          no: 'x',
          city: 'x',
          title: 'x',
          text: 'x',
          meta: ['x', 'x'],
        })),
      },
      featured: {
        edition: '1',
        eyebrow: 'x',
        title: 'x',
        body: 'x',
        pills: ['x', 'x'],
        details: many('details', () => ['x', 'x']),
      },
      menu: { ...basic, items: many('menu', () => ['x', 'x', 'x', 'x']) },
      quote: { label: 'x', quote: 'x', author: 'x', role: 'x' },
      calendar: {
        ...basic,
        columns: ['x', 'x', 'x', 'x', 'x'],
        rows: many('rows', () => ['x', 'x', 'x', 'x', 'x']),
      },
      closing: {
        mark: '1',
        eyebrow: 'x',
        title: 'x',
        body: 'x',
        site: 'x',
        cta: 'x',
        footer: many('footer', () => ['x', 'x']),
      },
    }[family.role],
    budgets = {}
  const [id, v] = Object.entries(family.variants)[0]
  const add = (path, frame, style) => {
    const key = path.replace(/^data\./, '').replace(/\[\d+\]/g, '[]')
    const budget = {
      fontPt: style.sizePt,
      widthIn: frame[2],
      heightIn: frame[3],
      lineHeight: style.lineHeight,
      maxLines: Math.max(1, Math.floor((frame[3] * 72) / (style.sizePt * 1.5))),
    }
    // A repeated tuple has one schema node; publish the conservative hint.
    if (!budgets[key] || budget.widthIn < budgets[key].widthIn) budgets[key] = budget
  }
  for (const c of compileLongTableLayout(design, family, id, v, data)) {
    if (c.path) {
      const width = c.path.startsWith('data.pills[')
        ? (v.regions.pills[2] - b.spacing.gap) / 2 - b.spacing.pad * 2
        : c.frame[2] - (c.inset ?? 0) * 2
      add(c.path, [c.frame[0], c.frame[1], width, c.frame[3]], c.style)
    }
    if (c.kind === 'table') {
      for (let j = 0; j < 5; j++) {
        add('columns[]', [0, 0, c.widths[j] - 0.16, c.rowHeights[0] - 0.16], b.styles.tableHead)
        add('rows[][]', [0, 0, c.widths[j] - 0.16, c.rowHeights[1] - 0.16], b.styles.table)
      }
    }
  }
  return budgets
}
export const LONG_TABLE_FAMILY = {
  key: 'longTable',
  name: 'long-table-editorial/v1',
  resolve: resolveLongTableDeck,
  assert: assertLongTable,
  checks: { 'long-table-language': checkLongTable },
  groups: {
    anchor: ['cover', 'closing'],
    editorial: ['manifesto', 'quote', 'featured'],
    register: ['index', 'menu', 'calendar'],
  },
  projectedBudgets: longTableProjectedBudgets,
  projectedCapacities(design, family) {
    const key = capacityForRole[family.role]
    return key ? { [key === 'menu' ? 'items' : key]: design.longTable.capacity[key] } : {}
  },
}
