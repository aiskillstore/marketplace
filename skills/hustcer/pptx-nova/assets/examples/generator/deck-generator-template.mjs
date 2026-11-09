#!/usr/bin/env node
import { readFileSync } from 'node:fs'
import { BUILTIN_STYLE_PACKS, BUILTIN_THEME_PACKS } from './theme-packs.generated.mjs'

// deck-generator-template.mjs —— 客户演示级 8 页 deck 的 JS 生成器骨架
//
// 用法：
//   1. 同时复制 deck-generator-template.mjs 为 ./generate.mjs 及相邻的 theme-packs.generated.mjs
//   2. 选择 themePack/stylePack:
//        node generate.mjs --theme corporate-blue --style consulting --layout executive-grid > patch.json
//      或加载外部 pack:
//        node generate.mjs --theme-pack ./theme.json --style-pack ./style.json > patch.json
//   3. 改各 slide 函数里的文字与数据
//   4. node generate.mjs --theme corporate-blue > patch.json
//   5. jq '.ops | length' patch.json  # 只记录构建规模；质量由内容、结构和真实渲染证明
//   6. xdoc pptx apply -p patch.json -o out.pptx --dry-run --json | tee dry-run.json
//   7. apply 后跑 vision-check；创建型 deck 必须 high=0 且 medium=0
//   8. xdoc convert out.pptx --to png -o previews --overwrite
//   9. 逐页 Read PNG，确认没有字符重叠/换行压字/截断
//
// 为什么用 JS 生成器：手写 700+ 行 JSON envelope 不可维护；JS 生成器允许共享
// helpers / themePack / 循环构造，把 "deck = 数据 + 模板 + themePack" 显式化。
// 换主题优先改 --theme 或 --theme-pack，而不是手工改 C 再重跑。
//
// 实测耗时分布 A(从零探索:10 页客户演示级 deck,1105 ops,总 ~20min):
//   - 内容大纲提炼            ~3 min (15%)
//   - JS 生成器编写           ~9 min (45%) ← 最耗时,优化点在 grid()/txH() helper
//   - dry-run + 修 schema bug ~3 min (15%)
//   - 落盘 + PNG 视觉验证     ~5 min (25%)
//
// 实测耗时分布 B(模板熟练:8 页橙色 roadmap deck,893 ops,总 ~6.6min):
//   - 内容大纲提炼            ~1.0 min (15-20%)
//   - JS 生成器编写           ~3.0-3.3 min (45-50%) ← 仍是最耗时环节
//   - dry-run + 小修          ~0.7-1.0 min (10-15%)
//   - apply + PNG + 结构验证  ~1.3-1.6 min (20-25%)

const BASE_COLORS = {
  primary: '1A73E8',
  primaryDk: '174EA6',
  primaryDp: '0D47A1',
  secondary: '00A3A1',
  light: '7BAAF7',
  amber: 'F9AB00',
  warn: 'EA4335',
  textPri: '202124',
  textSec: '5F6368',
  textMut: '9AA0A6',
  cardBg: 'E8F0FE',
  cream: 'F8FAFC',
  pale: 'D2E3FC',
  divider: 'DADCE0',
  posBg: 'E6F4EA',
  posTxt: '188038',
  negBg: 'FCE8E6',
  negTxt: 'C5221F',
  white: 'FFFFFF',
}

const BASE_SIZES = {
  hero: '54pt', // hero 收尾页大标题
  cover: '44pt', // 封面主标题（如挤压可降到 40pt）
  pageH1: '32pt', // 内容页主标题
  pageH2: '24pt', // 章节标题
  kpiNum: '40pt', // KPI 大数字
  body: '14pt', // 正文
  pill: '11pt', // delta pill
  eyebrow: '10pt', // eyebrow 小标
  foot: '9pt', // 页脚 / 注脚
}

const SLIDE_W = 13.333
const SLIDE_H = 7.5
const BOUNDS_EPS = 0.001

const argValue = (name, fallback = '') => {
  const idx = process.argv.indexOf(name)
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback
}

const LAYOUT_VARIANTS = ['executive-grid', 'narrative-split', 'data-room']
const layoutVariant = argValue('--layout', 'executive-grid')
if (!LAYOUT_VARIANTS.includes(layoutVariant)) {
  throw new Error(`Unknown --layout '${layoutVariant}'. Built-ins: ${LAYOUT_VARIANTS.join(', ')}`)
}

const readJsonFile = (path) => JSON.parse(readFileSync(path, 'utf8'))

const selectPack = (kind, builtins, id, file) => {
  const pack = file ? readJsonFile(file) : builtins[id]
  if (!pack) {
    throw new Error(`Unknown ${kind} '${id}'. Built-ins: ${Object.keys(builtins).join(', ')}`)
  }
  return pack
}

const themePack = selectPack(
  'themePack',
  BUILTIN_THEME_PACKS,
  argValue('--theme', 'corporate-blue'),
  argValue('--theme-pack'),
)
const stylePack = selectPack(
  'stylePack',
  BUILTIN_STYLE_PACKS,
  argValue('--style', 'consulting'),
  argValue('--style-pack'),
)

// Theme-derived tokens. Slide helpers below consume C/F/S/fonts, so swapping
// themePack/stylePack does not require editing the body of each slide function.
const C = { ...BASE_COLORS, ...(themePack.generator?.colors ?? {}) }
const F = {
  ...BASE_SIZES,
  ...(themePack.generator?.sizes ?? {}),
  ...(stylePack.generator?.sizes ?? {}),
}

const MIN_VISIBLE_FONT_PT = 9
const MIN_TABLE_TEXT_CONTRAST = 4.5

const parseFontPt = (size) => {
  if (typeof size === 'number' && Number.isFinite(size)) return size
  const match = String(size ?? '').match(/^([0-9]+(?:\.[0-9]+)?)pt$/i)
  return match ? Number.parseFloat(match[1]) : null
}

const fontSizeValue = (sizePt) => {
  const rounded = Number(sizePt.toFixed(2))
  return `${Number.isInteger(rounded) ? rounded.toFixed(0) : rounded}pt`
}

const withFontFloor = (font, floorPt = MIN_VISIBLE_FONT_PT) => {
  if (!font || typeof font !== 'object') return font
  const current = parseFontPt(font.size)
  if (current === null || current >= floorPt) return font
  return { ...font, size: fontSizeValue(floorPt) }
}

const normalizeHex = (value) => {
  const hex = String(value ?? '')
    .replace(/^#/, '')
    .toUpperCase()
  return /^[0-9A-F]{6}$/.test(hex) ? hex : null
}

const channelToLinear = (channel) => {
  const value = channel / 255
  return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4
}

const luminance = (value) => {
  const hex = normalizeHex(value)
  if (!hex) return null
  const red = channelToLinear(Number.parseInt(hex.slice(0, 2), 16))
  const green = channelToLinear(Number.parseInt(hex.slice(2, 4), 16))
  const blue = channelToLinear(Number.parseInt(hex.slice(4, 6), 16))
  return 0.2126 * red + 0.7152 * green + 0.0722 * blue
}

const contrastRatio = (foreground, background) => {
  const fg = luminance(foreground)
  const bg = luminance(background)
  if (fg === null || bg === null) return 0
  const lighter = Math.max(fg, bg)
  const darker = Math.min(fg, bg)
  return (lighter + 0.05) / (darker + 0.05)
}

const isDarkColor = (value) => {
  const lum = luminance(value)
  return lum !== null && lum < 0.35
}

const readableTextOn = (background, preferred = C.textPri) => {
  const bg = normalizeHex(background)
  const preferredHex = normalizeHex(preferred)
  if (!bg) return preferredHex ?? normalizeHex(C.textPri) ?? '111827'
  if (preferredHex && contrastRatio(preferredHex, bg) >= MIN_TABLE_TEXT_CONTRAST) {
    return preferredHex
  }

  const semanticCandidates = [
    C.tableBodyText,
    C.textPri,
    C.chartAxis,
    C.primaryDp,
    C.primaryDk,
    C.textSec,
    C.onHero,
    C.onAccent,
    C.white,
  ]
    .map(normalizeHex)
    .filter(Boolean)

  for (const candidate of new Set(semanticCandidates)) {
    if (contrastRatio(candidate, bg) >= MIN_TABLE_TEXT_CONTRAST) {
      return candidate
    }
  }

  return contrastRatio('111827', bg) >= contrastRatio('FFFFFF', bg) ? '111827' : 'FFFFFF'
}

const FONT_LATIN = themePack.fonts?.heading ?? 'Inter'
const _FONT_EA = themePack.fonts?.body ?? 'Source Han Sans SC'
const CHART_PALETTE = themePack.chartPalette ?? [C.primary, C.secondary, C.amber, C.posTxt, C.warn]
const PAGE_BG = C.pageBg ?? themePack.background ?? C.cream
const SURFACE_BG = C.surfaceBg ?? C.cardBg
const SURFACE_ALT = C.surfaceAlt ?? C.pale
const ACCENT_TEXT = C.accentText ?? C.primaryDk ?? C.primary
const CHART_BG = C.chartBg ?? C.white
const CHART_AXIS = C.chartAxis ?? C.textPri
const CHART_GRID = C.chartGrid ?? C.divider
const TABLE_HEADER_BG = C.tableHeaderBg ?? C.accentTextBg ?? C.primaryDk ?? C.primary
const TABLE_HEADER_TEXT = readableTextOn(
  TABLE_HEADER_BG,
  C.tableHeaderText ?? C.onAccent ?? C.white,
)
const TABLE_FIRST_COL_BG = C.tableFirstColBg ?? C.surfaceAlt ?? SURFACE_ALT
const TABLE_FIRST_COL_TEXT = readableTextOn(
  TABLE_FIRST_COL_BG,
  C.tableFirstColText ?? C.tableBodyText ?? C.textPri,
)
const TABLE_BODY_BG = C.tableBodyBg ?? (isDarkColor(PAGE_BG) ? SURFACE_BG : C.white)
const TABLE_BODY_TEXT = readableTextOn(TABLE_BODY_BG, C.tableBodyText ?? C.textPri)
const TABLE_BAND_BG = C.tableBandBg ?? (isDarkColor(PAGE_BG) ? SURFACE_ALT : SURFACE_BG)
const TABLE_BAND_TEXT = readableTextOn(
  TABLE_BAND_BG,
  C.tableBandText ?? C.tableBodyText ?? C.textPri,
)
const TABLE_BORDER = C.tableBorder ?? C.divider
const CHROME_COLOR = C.chromeColor ?? C.primary
const HEADER_ACCENT = C.headerAccent ?? C.primary
const CARD_SHELL_BG = C.cardShellBg ?? null
const CARD_INNER_LINE = C.cardInnerLine ?? C.divider
const PANEL_SHELL_BG = C.panelShellBg ?? CARD_SHELL_BG
const PANEL_INNER_LINE = C.panelInnerLine ?? C.divider
const BEZEL_INSET = 0.035

const MCKINSEY = {
  footer: 'Source: McKinsey Customer Loyalty Programme Brief, November 2025',
  confidentiality: 'STRICTLY CONFIDENTIAL | NOT FOR DISTRIBUTION',
  title: 'McKinsey Customer Loyalty Programme',
  subtitle: 'Strategic Framework for Customer Retention · European Market',
  metrics: [
    {
      label: 'Repeat purchase rate',
      value: '15%',
      detail: 'vs. target 30%',
      note: 'Gap to target: -50%',
      color: 'warn',
    },
    {
      label: 'Lost to competitors',
      value: '52%',
      detail: 'of lapsed buyers',
      note: 'Controllable driver',
      color: 'amber',
    },
    {
      label: 'After-sales rated Fair or Poor',
      value: '67%',
      detail: 'of all customers',
      note: 'Must-fix service gap',
      color: 'warn',
    },
  ],
  drivers: [
    { label: 'Return to McKinsey', value: 15, color: 'primary', note: 'Retained customers' },
    { label: 'Competitor switch', value: 52, color: 'warn', note: 'Loyalty discount + trade-in' },
    { label: 'Service failure', value: 26, color: 'amber', note: 'Free 3-year after-sales' },
    { label: 'Other', value: 7, color: 'divider', note: 'Residual churn' },
  ],
  segments: [
    { label: 'Under 30', value: '48%', note: 'Primary cohort' },
    { label: '31-40', value: '27%', note: '75% under 40 combined' },
    { label: 'Middle income', value: '82%', note: 'Core addressable segment' },
    { label: 'Employed', value: '75%', note: 'Predictable purchase cycle' },
  ],
  initiatives: [
    {
      label: 'Loyalty discount',
      impact: 'High',
      body: 'Directly counters competitor switching for price-sensitive buyers.',
    },
    {
      label: '3-year after-sales',
      impact: 'High',
      body: 'Targets the lowest McKinsey satisfaction score and 26% of defection.',
    },
    {
      label: 'Trade-in path',
      impact: 'Medium',
      body: 'Creates a structured second-purchase trigger for employed mainstream buyers.',
    },
  ],
}

const metricAccent = (key) =>
  key === 'warn' ? C.warn : key === 'amber' ? C.amber : key === 'primary' ? C.primary : C.divider

const isPlainObject = (value) =>
  value !== null && typeof value === 'object' && !Array.isArray(value)

const deepMerge = (...sources) => {
  const result = {}
  for (const source of sources) {
    if (!isPlainObject(source)) continue
    for (const [key, value] of Object.entries(source)) {
      if (isPlainObject(value) && isPlainObject(result[key])) {
        result[key] = deepMerge(result[key], value)
      } else if (isPlainObject(value)) {
        result[key] = deepMerge(value)
      } else {
        result[key] = value
      }
    }
  }
  return result
}

// Compatibility fallback for hand-written external style packs only.
// Built-in consulting/minimal/product visual tokens live in themes/catalog.json.
const MIN_STYLE_FALLBACK = {
  layout: {
    marginX: 0.65,
    gridGap: 0.3,
    rowGap: 0.32,
    cardPadX: 0.3,
    cardPadY: 0.24,
    agendaRowH: 1.35,
    kpiCardH: 3.8,
    pillarCardH: 4.0,
    workflowCardH: 3.7,
  },
  surface: {
    cardShape: 'rounded-rectangle',
    panelShape: 'rounded-rectangle',
    cardLine: true,
    cardLineWidth: '0.5pt',
    accentBarH: 0.08,
  },
  effects: { cardShadow: null, panelShadow: null },
  chrome: {
    topBarH: 0.08,
    headerAccentW: 0.1,
    headerAccentH: 0.55,
    footerY: 7.12,
    watermark: false,
  },
  chart: { panelW: 8.4, calloutW: 3.1 },
}

const resolveStyle = (pack) => {
  return deepMerge(MIN_STYLE_FALLBACK, pack.generator ?? {})
}

const S = resolveStyle(stylePack)
const FOOTER_TEXT_H = 0.18
const FOOTER_TEXT_Y_OFFSET = 0.22
const footerTextY = () =>
  Number(
    Math.min(S.chrome.footerY + FOOTER_TEXT_Y_OFFSET, SLIDE_H - FOOTER_TEXT_H - 0.02).toFixed(2),
  )

// ============================================================
// 共享 helpers
// ============================================================
const ops = []

// shape name 必须双向：生成和引用都走 nm()，否则 selector 命不中
const nm = (slide, base) => `S${slide}_${base}`

const addThemedSlide = (slide, background = PAGE_BG) => {
  ops.push({ op: 'add-slide', layout: 'blank' })
  ops.push({ op: 'set-slide-background', slide, fill: { type: 'solid', color: background } })
}

const assertWithinSlide = (slide, name, x, y, w, h) => {
  const right = x + w
  const bottom = y + h
  if (
    x < -BOUNDS_EPS ||
    y < -BOUNDS_EPS ||
    right > SLIDE_W + BOUNDS_EPS ||
    bottom > SLIDE_H + BOUNDS_EPS
  ) {
    throw new Error(
      `Shape ${name} on slide ${slide + 1} exceeds slide bounds: ` +
        `x=${x}, y=${y}, w=${w}, h=${h}, right=${right.toFixed(3)}, bottom=${bottom.toFixed(3)}`,
    )
  }
}

const shape = (slide, name, kind, x, y, w, h) => {
  assertWithinSlide(slide, name, x, y, w, h)
  ops.push({
    op: 'add-shape',
    slide,
    kind,
    name,
    x: `${x}in`,
    y: `${y}in`,
    w: `${w}in`,
    h: `${h}in`,
  })
  return name
}

const fill = (slide, name, color) => {
  ops.push({ op: 'set-shape', slide, shape: { name }, fill: { type: 'solid', color } })
}

const noLine = (slide, name) => {
  ops.push({ op: 'set-shape', slide, shape: { name }, line: { noLine: true } })
}

const thinLine = (slide, name, color, width = '0.75pt') => {
  ops.push({ op: 'set-shape', slide, shape: { name }, line: { width, color } })
}

const applyShapeEffect = (slide, name, effect) => {
  if (!effect) return
  ops.push({
    op: 'set-shape',
    slide,
    shape: { name },
    effect: effect.shadow ? effect : { shadow: effect },
  })
}

const textbox = (slide, name, x, y, w, h) => {
  assertWithinSlide(slide, name, x, y, w, h)
  ops.push({ op: 'add-text-box', slide, name, x: `${x}in`, y: `${y}in`, w: `${w}in`, h: `${h}in` })
  return name
}

const setText = (slide, name, text) => {
  ops.push({ op: 'set-text-frame', slide, shape: { name }, text })
}

const runFont = (slide, name, font, paragraph = 0, run = 0) => {
  ops.push({ op: 'set-run', slide, shape: { name }, paragraph, run, font: withFontFloor(font) })
}

// Paragraph formatting is carried by the canonical set-paragraph.format object.
const pAlign = (slide, name, align, paragraph = 0) => {
  ops.push({ op: 'set-paragraph', slide, shape: { name }, paragraph, format: { alignment: align } })
}

// 组合 helper：一次完成 textbox + setText + runFont
// 注意 h 给字号的 1.4-1.5 倍，否则触发 text-overflow-possible。
// 可见文字低于 MIN_VISIBLE_FONT_PT 会在 runFont 层自动抬高；正文仍应按设计锁字号
// 规划，塞不下时删字/换布局，而不是缩到 7pt/8pt。
const tx = (slide, name, x, y, w, h, text, font) => {
  textbox(slide, name, x, y, w, h)
  setText(slide, name, text)
  const paragraphs = String(text).split(/\r\n|\r|\n/).length
  for (let paragraph = 0; paragraph < paragraphs; paragraph += 1) {
    runFont(slide, name, font, paragraph)
  }
}

// 矩形装饰块：fill + 无描边
const box = (slide, name, kind, x, y, w, h, color) => {
  shape(slide, name, kind, x, y, w, h)
  fill(slide, name, color)
  noLine(slide, name)
  return name
}

const cardTopAccent = (slide, name, x, y, w, h, color) => {
  const kind = S.surface.cardShape === 'rounded-rectangle' ? 'rounded-rectangle' : 'rectangle'
  return box(slide, name, kind, x, y, w, h, color)
}

const styledBox = (slide, name, kind, x, y, w, h, color, options = {}) => {
  shape(slide, name, kind, x, y, w, h)
  fill(slide, name, color)
  if (options.line) {
    thinLine(slide, name, options.line.color ?? C.divider, options.line.width ?? '0.75pt')
  } else {
    noLine(slide, name)
  }
  applyShapeEffect(slide, name, options.effect)
  return name
}

const canInset = (w, h) => w > BEZEL_INSET * 4 && h > BEZEL_INSET * 4

const cardBox = (slide, name, x, y, w, h, color = SURFACE_BG) => {
  if (CARD_SHELL_BG && canInset(w, h)) {
    styledBox(slide, `${name}Shell`, S.surface.cardShape, x, y, w, h, CARD_SHELL_BG, {
      line: { color: C.divider, width: '0.35pt' },
      effect: S.effects.cardShadow,
    })
    return styledBox(
      slide,
      name,
      S.surface.cardShape,
      x + BEZEL_INSET,
      y + BEZEL_INSET,
      w - BEZEL_INSET * 2,
      h - BEZEL_INSET * 2,
      color,
      {
        line: S.surface.cardLine
          ? { color: CARD_INNER_LINE, width: S.surface.cardLineWidth ?? '0.75pt' }
          : null,
      },
    )
  }

  return styledBox(slide, name, S.surface.cardShape, x, y, w, h, color, {
    line: S.surface.cardLine
      ? { color: C.divider, width: S.surface.cardLineWidth ?? '0.75pt' }
      : null,
    effect: S.effects.cardShadow,
  })
}

const panelBox = (slide, name, x, y, w, h, color = SURFACE_BG) => {
  if (PANEL_SHELL_BG && canInset(w, h)) {
    styledBox(slide, `${name}Shell`, S.surface.panelShape, x, y, w, h, PANEL_SHELL_BG, {
      line: { color: C.divider, width: '0.35pt' },
      effect: S.effects.panelShadow,
    })
    return styledBox(
      slide,
      name,
      S.surface.panelShape,
      x + BEZEL_INSET,
      y + BEZEL_INSET,
      w - BEZEL_INSET * 2,
      h - BEZEL_INSET * 2,
      color,
      {
        line: { color: PANEL_INNER_LINE, width: S.surface.cardLineWidth ?? '0.75pt' },
      },
    )
  }

  return styledBox(slide, name, S.surface.panelShape, x, y, w, h, color, {
    line: { color: C.divider, width: S.surface.cardLineWidth ?? '0.75pt' },
    effect: S.effects.panelShadow,
  })
}

const tableCellStyle = (slide, tableName, row, column, style) => {
  ops.push({
    op: 'set-table',
    slide,
    shape: { name: tableName },
    cells: [
      {
        row,
        column,
        style: {
          verticalAnchor: 'middle',
          marginLeft: '0.1in',
          marginRight: '0.1in',
          ...style,
        },
      },
    ],
  })
}

const styleComparisonTable = (slide, tableName, rows, cols) => {
  ops.push({
    op: 'set-table',
    slide,
    shape: { name: tableName },
    style: {
      firstRow: true,
      lastRow: false,
      firstColumn: true,
      lastColumn: false,
      horizontalBanding: true,
      verticalBanding: false,
    },
  })

  for (let row = 0; row < rows; row += 1) {
    ops.push({
      op: 'set-table',
      slide,
      shape: { name: tableName },
      rows: [{ row, height: row === 0 ? '0.52in' : '0.66in' }],
    })
    for (let col = 0; col < cols; col += 1) {
      const isHeader = row === 0
      const isFirstCol = col === 0
      const fillColor = isHeader
        ? TABLE_HEADER_BG
        : isFirstCol
          ? TABLE_FIRST_COL_BG
          : row % 2 === 0
            ? TABLE_BAND_BG
            : TABLE_BODY_BG
      const fontColor = isHeader
        ? TABLE_HEADER_TEXT
        : isFirstCol
          ? TABLE_FIRST_COL_TEXT
          : row % 2 === 0
            ? TABLE_BAND_TEXT
            : TABLE_BODY_TEXT
      tableCellStyle(slide, tableName, row, col, {
        fill: { type: 'solid', color: fillColor },
        font: {
          name: FONT_LATIN,
          size: isHeader ? '12pt' : '13pt',
          bold: isHeader || isFirstCol,
          color: fontColor,
        },
        alignment: isHeader ? 'center' : 'left',
        borders: {
          bottom: { color: TABLE_BORDER, width: '0.75pt' },
        },
      })
    }
  }

  ops.push({
    op: 'set-table',
    slide,
    shape: { name: tableName },
    borders: [
      {
        range: { startRow: 0, startColumn: 0, endRow: rows - 1, endColumn: cols - 1 },
        value: {
          top: { color: TABLE_BORDER, width: '0.75pt' },
          bottom: { color: TABLE_BORDER, width: '0.75pt' },
          left: { color: TABLE_BORDER, width: '0.75pt' },
          right: { color: TABLE_BORDER, width: '0.75pt' },
          insideH: { color: TABLE_BORDER, width: '0.5pt' },
          insideV: { color: TABLE_BORDER, width: '0.5pt' },
        },
      },
    ],
  })
}

// 自动算 N 列等距网格,返回 [{x, w}, ...] —— 4-across KPI / 3-across pillar 用
//   const cells = grid(4)  // 默认占满 stylePack 定义的安全区
//   cells.forEach((c, i) => cardBox(s, nm(s, `K${i}`), c.x, 2.4, c.w, 4.0, C.cardBg))
// 比手算 `startX + i*(w+gap)` 不容易写错,也方便居中(传 startX = (SLIDE_W - contentW) / 2)
const grid = (
  cols,
  gap = S.layout.gridGap,
  startX = S.layout.marginX,
  contentW = SLIDE_W - S.layout.marginX * 2,
) => {
  const cardW = (contentW - gap * (cols - 1)) / cols
  return Array.from({ length: cols }, (_, i) => ({
    x: startX + i * (cardW + gap),
    w: cardW,
  }))
}

// 字号自动给 textbox 高度,避免 text-overflow-possible risk
//   tx(s, name, x, y, w, Number.parseFloat(_txH(32)), title, {...})       // 单行 32pt → 0.67in
//   tx(s, name, x, y, w, Number.parseFloat(_txH(14, 3)), bodyMulti, {...}) // 3 行 14pt → 0.88in
// 中文环境多给一点保险(系数 1.5 而非 1.4),CJK 行高比西文略高
const _txH = (sizePt, lines = 1) => `${((sizePt / 72) * 1.5 * lines).toFixed(2)}in`

// 每页通用底层：顶部品牌色横条 + 页脚 + 页码 + watermark
// watermark 参数化:默认空串(不渲染);传字串则渲染为右上角半透明品牌标识。
// 早期模板把 'structurify.io' 硬编码在这里,导致换品牌时左下角 footerLeft 写"BRAND·X"、
// 右上角 watermark 仍写"structurify.io"—— 同一页面两种身份。
const pageChrome = (slide, total, footerLeft, watermark = '') => {
  const top = nm(slide, 'TopBar')
  if (S.chrome.topBarH > 0) {
    box(slide, top, 'rectangle', 0, 0, SLIDE_W, S.chrome.topBarH, CHROME_COLOR)
  }

  const foot = nm(slide, 'Foot')
  const footerY = footerTextY()
  tx(slide, foot, S.layout.marginX, footerY, 8, FOOTER_TEXT_H, footerLeft, {
    name: FONT_LATIN,
    size: F.foot,
    color: C.textMut,
  })

  const pg = nm(slide, 'PageNum')
  tx(
    slide,
    pg,
    12.0,
    footerY,
    1.2,
    FOOTER_TEXT_H,
    `${String(slide + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}`,
    { name: FONT_LATIN, size: F.foot, color: C.textMut },
  )
  pAlign(slide, pg, 'right')

  if (watermark && S.chrome.watermark !== false) {
    const wm = nm(slide, 'Watermark')
    tx(slide, wm, 11.4, 0.18, 1.85, 0.28, watermark, {
      name: FONT_LATIN,
      size: F.foot,
      bold: true,
      color: C.divider,
    })
    pAlign(slide, wm, 'right')
  }
}

const mckFooter = (slide, total, colors = {}) => {
  const footerY = 7.02
  const footerH = 0.32
  tx(slide, nm(slide, 'MckSource'), S.layout.marginX, footerY, 4.25, footerH, MCKINSEY.footer, {
    name: FONT_LATIN,
    size: F.foot,
    color: colors.source ?? C.textMut,
  })
  tx(slide, nm(slide, 'MckConf'), 5.35, footerY, 3.4, footerH, MCKINSEY.confidentiality, {
    name: FONT_LATIN,
    size: F.foot,
    color: colors.confidentiality ?? C.textMut,
  })
  const pg = nm(slide, 'MckPage')
  tx(slide, pg, 12.05, footerY, 1.1, 0.16, `${slide + 1}`, {
    name: FONT_LATIN,
    size: F.foot,
    color: colors.page ?? C.textMut,
  })
  pAlign(slide, pg, 'right')
  if (slide > 0 && S.chrome.topBarH > 0) {
    box(
      slide,
      nm(slide, 'MckTopBar'),
      'rectangle',
      0,
      0,
      SLIDE_W,
      Math.max(0.05, S.chrome.topBarH),
      CHROME_COLOR,
    )
  }
}

const mckHeader = (slide, title, subtitle) => {
  tx(slide, nm(slide, 'Title'), S.layout.marginX, 0.32, 12, 0.42, title, {
    name: FONT_LATIN,
    size: '21pt',
    bold: true,
    color: C.textPri,
  })
  box(
    slide,
    nm(slide, 'InsightBand'),
    'rectangle',
    S.layout.marginX,
    0.86,
    12.15,
    0.46,
    C.primaryDp,
  )
  box(
    slide,
    nm(slide, 'InsightAccent'),
    'rectangle',
    S.layout.marginX,
    0.86,
    0.06,
    0.46,
    C.secondary,
  )
  tx(slide, nm(slide, 'Subtitle'), S.layout.marginX + 0.18, 0.98, 11.7, 0.18, subtitle, {
    name: FONT_LATIN,
    size: '10.5pt',
    bold: true,
    color: C.onHero,
  })
}

const metricCard = (slide, name, x, y, w, h, metric) => {
  const accent = metricAccent(metric.color)
  cardBox(slide, `${name}Bg`, x, y, w, h, isDarkColor(PAGE_BG) ? SURFACE_BG : C.white)
  box(slide, `${name}Rule`, 'rectangle', x, y, 0.05, h, accent)
  tx(slide, `${name}Label`, x + 0.22, y + 0.22, w - 0.42, 0.42, metric.label, {
    name: FONT_LATIN,
    size: '9.5pt',
    color: C.textMut,
  })
  tx(slide, `${name}Value`, x + 0.22, y + 0.78, w - 0.42, 0.55, metric.value, {
    name: FONT_LATIN,
    size: '32pt',
    bold: true,
    color: accent,
  })
  tx(slide, `${name}Detail`, x + 0.22, y + 1.5, w - 0.42, 0.25, metric.detail, {
    name: FONT_LATIN,
    size: '10pt',
    color: C.textMut,
  })
  thinLine(slide, `${name}Bg`, C.divider, S.surface.cardLineWidth ?? '0.5pt')
  tx(slide, `${name}Note`, x + 0.22, y + h - 0.5, w - 0.42, 0.3, metric.note, {
    name: FONT_LATIN,
    size: '9pt',
    bold: true,
    color: accent,
  })
}

const compactMetricCard = (slide, name, x, y, w, h, metric) => {
  const accent = metricAccent(metric.color)
  cardBox(slide, `${name}Bg`, x, y, w, h, isDarkColor(PAGE_BG) ? SURFACE_BG : C.white)
  box(slide, `${name}Rule`, 'rectangle', x, y, 0.05, h, accent)
  tx(slide, `${name}Label`, x + 0.22, y + 0.18, w - 0.44, 0.18, metric.label, {
    name: FONT_LATIN,
    size: '8.5pt',
    color: C.textMut,
  })
  tx(slide, `${name}Value`, x + 0.22, y + 0.48, 1.05, 0.42, metric.value, {
    name: FONT_LATIN,
    size: '24pt',
    bold: true,
    color: accent,
  })
  tx(slide, `${name}Detail`, x + 1.32, y + 0.54, w - 1.6, 0.2, metric.detail, {
    name: FONT_LATIN,
    size: '8.5pt',
    color: C.textMut,
  })
  tx(slide, `${name}Note`, x + 0.22, y + h - 0.32, w - 0.44, 0.18, metric.note, {
    name: FONT_LATIN,
    size: '7.5pt',
    bold: true,
    color: accent,
  })
}

const stackedCohortBar = (slide, y, x = S.layout.marginX, w = 12.15) => {
  const total = MCKINSEY.drivers.reduce((sum, item) => sum + item.value, 0)
  let cursor = x
  MCKINSEY.drivers.forEach((driver, i) => {
    const segmentW = (w * driver.value) / total
    const color = metricAccent(driver.color)
    box(slide, nm(slide, `Driver${i + 1}Seg`), 'rectangle', cursor, y, segmentW, 0.55, color)
    tx(
      slide,
      nm(slide, `Driver${i + 1}Val`),
      cursor + 0.05,
      y + 0.14,
      segmentW - 0.1,
      0.24,
      `${driver.value}`,
      {
        name: FONT_LATIN,
        size: '16pt',
        bold: true,
        color: readableTextOn(color, C.white),
      },
    )
    pAlign(slide, nm(slide, `Driver${i + 1}Val`), 'center')
    tx(
      slide,
      nm(slide, `Driver${i + 1}Lab`),
      cursor,
      y + 0.82,
      Math.max(1, segmentW),
      0.32,
      driver.label,
      {
        name: FONT_LATIN,
        size: '10pt',
        bold: true,
        color,
      },
    )
    pAlign(slide, nm(slide, `Driver${i + 1}Lab`), 'center')
    cursor += segmentW
  })
}

// 每页 header：左侧 accent 竖条 + eyebrow + 主标题
// 返回 yEnd（content 起始 y），避免每页重算
const pageHeader = (slide, eyebrow, title) => {
  const bar = nm(slide, 'AccentBar')
  box(
    slide,
    bar,
    'rectangle',
    S.layout.marginX,
    0.6,
    S.chrome.headerAccentW,
    S.chrome.headerAccentH,
    HEADER_ACCENT,
  )
  const textX = S.layout.marginX + S.chrome.headerAccentW + 0.24

  const eb = nm(slide, 'Eyebrow')
  tx(slide, eb, textX, 0.6, 11, 0.3, eyebrow, {
    name: FONT_LATIN,
    size: F.eyebrow,
    bold: true,
    color: HEADER_ACCENT,
  })

  const h1 = nm(slide, 'Title')
  tx(slide, h1, textX, 0.95, 11, 0.7, title, {
    name: FONT_LATIN,
    size: F.pageH1,
    bold: true,
    color: C.textPri,
  })

  return 1.85 // content 起始 y
}

// ============================================================
// 8 页 slide 函数
// ============================================================

// slide 0：封面（无 pageChrome，自有装饰）
function slideCover(total) {
  const s = 0
  addThemedSlide(s)

  // 顶部品牌条
  if (S.chrome.topBarH > 0) {
    box(s, nm(s, 'TopBar'), 'rectangle', 0, 0, SLIDE_W, S.chrome.topBarH, CHROME_COLOR)
  }

  // 左侧 accent 竖条
  box(
    s,
    nm(s, 'AccentBar'),
    'rectangle',
    S.layout.marginX,
    2.4,
    S.chrome.headerAccentW,
    2.4,
    HEADER_ACCENT,
  )
  const textX = S.layout.marginX + S.chrome.headerAccentW + 0.25

  // eyebrow
  tx(s, nm(s, 'Eyebrow'), textX, 2.4, 11, 0.4, 'MCKINSEY EUROPE · CUSTOMER STRATEGY PRACTICE', {
    name: FONT_LATIN,
    size: '13pt',
    bold: true,
    color: HEADER_ACCENT,
  })

  // 主标题（注意 w 不要超过 11in；右侧留装饰空间）
  tx(s, nm(s, 'Title'), textX, 2.85, 11, 1.5, MCKINSEY.title, {
    name: FONT_LATIN,
    size: F.cover,
    bold: true,
    color: C.textPri,
  })

  // 副标题
  tx(s, nm(s, 'Subtitle'), textX, 4.4, 11, 0.5, MCKINSEY.subtitle, {
    name: FONT_LATIN,
    size: '22pt',
    color: C.textSec,
  })

  // tagline（4.95-5.35in）
  tx(
    s,
    nm(s, 'Tagline'),
    textX,
    4.95,
    11,
    0.4,
    'Controllable churn · Loyalty economics · Franchise execution',
    {
      name: FONT_LATIN,
      size: '13pt',
      color: C.textMut,
    },
  )

  // 底部 hero strip
  box(s, nm(s, 'HeroStrip'), 'rectangle', 0, 6.95, SLIDE_W, 0.55, SURFACE_ALT)

  // ⚠️ 装饰元素放右下角（避开主标题 textbox），不要放右上
  // 主标题 textbox 起 x=0.95、w=11 → 延伸到 x=11.95，与右上 (10+, 2-4) 区域必撞
  cardBox(s, nm(s, 'Deco1'), 10.4, 5.45, 1.45, 1.4, SURFACE_BG)
  cardBox(s, nm(s, 'Deco2'), 11.45, 5.55, 1.45, 1.3, SURFACE_ALT)

  // 页码（封面通常只显示 01 / N，不显示全 footer）
  const pg = nm(s, 'PageNum')
  tx(s, pg, 12.0, footerTextY(), 1.2, FOOTER_TEXT_H, `01 / ${String(total).padStart(2, '0')}`, {
    name: FONT_LATIN,
    size: F.foot,
    color: C.textMut,
  })
  pAlign(s, pg, 'right')
}

// slide 1：议程（5-6 个编号卡片）
function slideAgenda(total) {
  const s = 1
  addThemedSlide(s)
  pageChrome(s, total, 'Agenda · Customer loyalty')
  pageHeader(s, 'AGENDA · READOUT PATH', 'Customer retention strategy readout')

  const items = [
    ['01', 'Executive context'],
    ['02', 'Critical metrics'],
    ['03', 'Buyer segments'],
    ['04', 'Performance gaps'],
    ['05', 'Root causes'],
    ['06', 'Action register'],
  ]
  const cols = 3,
    rowH = S.layout.agendaRowH,
    gap = S.layout.gridGap
  const cells = grid(cols, gap)
  items.forEach(([num, label], i) => {
    const col = i % cols,
      row = Math.floor(i / cols)
    const { x, w: cardW } = cells[col]
    const y = 2.2 + row * (rowH + S.layout.rowGap)

    const card = nm(s, `Ag${i + 1}Bg`)
    cardBox(s, card, x, y, cardW, rowH, SURFACE_BG)

    tx(s, nm(s, `Ag${i + 1}Num`), x + S.layout.cardPadX, y + S.layout.cardPadY, 0.8, 0.5, num, {
      name: FONT_LATIN,
      size: '26pt',
      bold: true,
      color: C.primary,
    })

    tx(s, nm(s, `Ag${i + 1}Lab`), x + 1.15, y + S.layout.cardPadY + 0.1, cardW - 1.35, 0.7, label, {
      name: FONT_LATIN,
      size: '16pt',
      bold: true,
      color: C.textPri,
    })
  })
}

// slide 2：KPI 4-across（手堆，不用 add-slide 的 kpi-grid recipe）
function slideKPI(total) {
  const s = 2
  addThemedSlide(s)
  pageChrome(s, total, 'KPI · Customer loyalty')
  pageHeader(s, 'KPI · CRITICAL METRICS', 'Three numbers define the retention challenge')

  const kpis = [
    {
      label: 'Repeat purchase rate',
      value: '15%',
      delta: 'Target 30%',
      pos: false,
      note: 'Only 1 in 7 returns',
    },
    {
      label: 'Lost to competitors',
      value: '52%',
      delta: 'Controllable',
      pos: false,
      note: 'Primary defection driver',
    },
    {
      label: 'Service rated fair/poor',
      value: '67%',
      delta: 'Must fix',
      pos: false,
      note: 'Drives 26% of defection',
    },
    {
      label: 'Controllable loss',
      value: '78%',
      delta: 'Addressable',
      pos: true,
      note: 'Competitor + service',
    },
  ]
  const cells = grid(kpis.length, S.layout.gridGap)
  const cardH = S.layout.kpiCardH

  kpis.forEach((k, i) => {
    const { x, w: cardW } = cells[i]
    const y = 2.4

    const cardName = nm(s, `Kpi${i + 1}Bg`)
    cardBox(s, cardName, x, y, cardW, cardH, SURFACE_BG)

    // 顶部色条
    const topName = nm(s, `Kpi${i + 1}Top`)
    cardTopAccent(s, topName, x, y, cardW, S.surface.accentBarH, C.primary)

    // label / value / delta / note
    tx(
      s,
      nm(s, `Kpi${i + 1}Lab`),
      x + S.layout.cardPadX,
      y + 0.35,
      cardW - S.layout.cardPadX * 2,
      0.45,
      k.label,
      {
        name: FONT_LATIN,
        size: '13pt',
        color: C.textSec,
      },
    )

    tx(
      s,
      nm(s, `Kpi${i + 1}Val`),
      x + S.layout.cardPadX,
      y + 0.9,
      cardW - S.layout.cardPadX * 2,
      1.4,
      k.value,
      {
        name: FONT_LATIN,
        size: F.kpiNum,
        bold: true,
        color: C.textPri,
      },
    )

    // delta pill
    const pillName = nm(s, `Kpi${i + 1}Pill`)
    shape(
      s,
      pillName,
      S.surface.cardShape,
      x + S.layout.cardPadX,
      y + 2.4,
      cardW - S.layout.cardPadX * 2,
      0.4,
    )
    fill(s, pillName, k.pos ? C.posBg : C.negBg)
    noLine(s, pillName)
    setText(s, pillName, k.delta)
    runFont(s, pillName, {
      name: FONT_LATIN,
      size: F.pill,
      bold: true,
      color: k.pos ? C.posTxt : C.negTxt,
    })
    pAlign(s, pillName, 'center')

    tx(
      s,
      nm(s, `Kpi${i + 1}Note`),
      x + S.layout.cardPadX,
      y + 2.95,
      cardW - S.layout.cardPadX * 2,
      0.4,
      k.note,
      {
        name: FONT_LATIN,
        size: F.foot,
        color: C.textMut,
      },
    )
  })
}

// slide 3：chart + 右侧 callout（chart 占左 2/3，callout 占右 1/3）
function slideChart(total) {
  const s = 3
  addThemedSlide(s)
  pageChrome(s, total, 'Data · Customer loss')
  pageHeader(s, 'DATA · ROOT CAUSES', 'Why customers do not return')

  const chartPanel = nm(s, 'ChartPanel')
  const chartX = S.layout.marginX
  const chartY = 2.3
  const chartH = 4.45
  const chartW = Math.min(
    S.chart.panelW,
    SLIDE_W - S.layout.marginX * 2 - S.layout.gridGap - S.chart.calloutW,
  )
  const calloutX = chartX + chartW + S.layout.gridGap
  const calloutW = SLIDE_W - S.layout.marginX - calloutX
  panelBox(s, chartPanel, chartX, chartY, chartW, chartH, CHART_BG)

  // chart
  ops.push({
    op: 'add-chart',
    slide: s,
    kind: 'column',
    variant: 'clustered',
    x: `${chartX + 0.2}in`,
    y: `${chartY + 0.15}in`,
    w: `${chartW - 0.4}in`,
    h: `${chartH - 0.4}in`,
    name: 'RevChart',
    legend: 'bottom',
    data: {
      categories: ['Competitor switch', 'Service failure', 'Unknown', 'Relocated'],
      series: [
        { name: 'Loss share', values: [52, 26, 9, 8] },
        { name: 'Target focus', values: [52, 26, 0, 0] },
      ],
    },
  })
  ops.push({
    op: 'set-chart',
    slide: s,
    shape: { name: 'RevChart' },
    series: [
      { series: 0, fill: { type: 'solid', color: CHART_PALETTE[1] ?? C.divider } },
      { series: 1, fill: { type: 'solid', color: CHART_PALETTE[0] ?? C.primary } },
    ],
    dataLabels: [{ scope: { series: 1 }, showValue: true, position: 'outside-end' }],
    axes: [
      { axis: 'category', line: { color: CHART_AXIS, width: '0.75pt' } },
      {
        axis: 'value',
        line: { color: CHART_AXIS, width: '0.75pt' },
        gridlines: { color: CHART_GRID, width: '0.5pt' },
      },
    ],
  })

  // 右侧 3 个 callout 卡片
  const callouts = [
    { label: 'Controllable pool', value: '78%' },
    { label: 'Competitor switch', value: '52%' },
    { label: 'Service failure', value: '26%' },
  ]
  callouts.forEach((c, i) => {
    const y = 2.4 + i * (1.3 + S.layout.rowGap)
    const card = nm(s, `Co${i + 1}Bg`)
    cardBox(s, card, calloutX, y, calloutW, 1.3, SURFACE_BG)

    tx(
      s,
      nm(s, `Co${i + 1}Lab`),
      calloutX + S.layout.cardPadX,
      y + 0.2,
      calloutW - S.layout.cardPadX * 2,
      0.32,
      c.label,
      {
        name: FONT_LATIN,
        size: '12pt',
        bold: true,
        color: C.textPri,
      },
    )

    tx(
      s,
      nm(s, `Co${i + 1}Val`),
      calloutX + S.layout.cardPadX,
      y + 0.66,
      calloutW - S.layout.cardPadX * 2,
      0.56,
      c.value,
      {
        name: FONT_LATIN,
        size: '30pt',
        bold: true,
        color: ACCENT_TEXT,
      },
    )
  })
}

// slide 4：对比表 + 结论 banner（用 add-table）
function slideTable(total) {
  const s = 4
  addThemedSlide(s)
  pageChrome(s, total, 'Compare · Programme options')
  pageHeader(s, 'COMPARE · INITIATIVES', 'Programme initiatives mapped to loss drivers')

  const tableX = S.layout.marginX + 0.2
  const tableW = SLIDE_W - tableX * 2
  const tableName = 'CmpTable'
  ops.push({
    op: 'add-table',
    slide: s,
    rows: 5,
    columns: 3,
    name: tableName,
    x: `${tableX}in`,
    y: '2.4in',
    w: `${tableW}in`,
    h: '3.4in',
    data: [
      ['Initiative', 'Target driver', 'Expected role'],
      ['Loyalty discount', 'Competitor switch', 'Recover price-sensitive buyers'],
      ['3-year after-sales', 'Service failure', 'Fix must-fix satisfaction gap'],
      ['Trade-in path', 'Under-40 mainstream', 'Create second-purchase trigger'],
      ['Survey incentive', 'Unknown reason', 'Improve decision quality'],
    ],
  })
  styleComparisonTable(s, tableName, 5, 3)

  // 结论 banner
  const ban = nm(s, 'ConclBanner')
  cardBox(s, ban, tableX, 6.05, tableW, 0.65, SURFACE_ALT)
  setText(
    s,
    ban,
    'Conclusion: focus investment on the 78% controllable loss pool before broad brand activity',
  )
  runFont(s, ban, { name: FONT_LATIN, size: '14pt', bold: true, color: C.textPri })
  pAlign(s, ban, 'center')
}

// slide 5：3 列支柱（行动计划 / recipe 卡片网格）
function slidePillars(total) {
  const s = 5
  addThemedSlide(s)
  pageChrome(s, total, 'Action · Three pillars')
  pageHeader(s, 'ACTION · THREE PILLARS', 'How McKinsey should concentrate the loyalty programme')

  const cols = [
    {
      color: C.primary,
      title: 'Price recovery',
      bullets: ['loyalty discount', 'trade-in trigger', 'franchise cost share'],
    },
    {
      color: C.secondary,
      title: 'Service repair',
      bullets: ['3-year free after-sales', 'service quality SLA', 'critical gap closure'],
    },
    {
      color: C.amber,
      title: 'Data quality',
      bullets: ['survey incentive', '40% to 70% response', 'unknown loss reduction'],
    },
  ]
  const gap = S.layout.gridGap
  const cells = grid(cols.length, gap)
  cols.forEach((c, i) => {
    const { x, w: cardW } = cells[i]
    const card = nm(s, `P${i + 1}Bg`)
    cardBox(s, card, x, 2.4, cardW, S.layout.pillarCardH, SURFACE_BG)

    cardTopAccent(s, nm(s, `P${i + 1}Bar`), x, 2.4, cardW, S.surface.accentBarH, c.color)

    tx(
      s,
      nm(s, `P${i + 1}T`),
      x + S.layout.cardPadX,
      2.7,
      cardW - S.layout.cardPadX * 2,
      0.6,
      c.title,
      {
        name: FONT_LATIN,
        size: '22pt',
        bold: true,
        color: C.textPri,
      },
    )

    c.bullets.forEach((b, j) => {
      tx(
        s,
        nm(s, `P${i + 1}B${j + 1}`),
        x + S.layout.cardPadX,
        3.5 + j * 0.6,
        cardW - S.layout.cardPadX * 2,
        0.5,
        `• ${b}`,
        {
          name: FONT_LATIN,
          size: F.body,
          color: C.textSec,
        },
      )
    })
  })
}

// slide 6：流程 / workflow（3 个 PHASE 卡片）
function slideWorkflow(total) {
  const s = 6
  addThemedSlide(s)
  pageChrome(s, total, 'Workflow · Mobilisation')
  pageHeader(s, 'WORKFLOW · MOBILISATION', 'Diagnose → Target → Execute')

  const phases = [
    {
      num: 'PHASE 01',
      title: 'Diagnose',
      body: 'Confirm the 78% controllable loss pool by franchise and customer segment.',
    },
    {
      num: 'PHASE 02',
      title: 'Target',
      body: 'Sequence loyalty discount, trade-in, and after-sales repair against root causes.',
    },
    {
      num: 'PHASE 03',
      title: 'Execute',
      body: 'Launch with Head Office and franchise cost-sharing plus weekly KPI cadence.',
    },
  ]
  const gap = S.layout.gridGap
  const cells = grid(phases.length, gap)
  phases.forEach((p, i) => {
    const { x, w: cardW } = cells[i]
    const card = nm(s, `Ph${i + 1}Bg`)
    cardBox(s, card, x, 2.4, cardW, S.layout.workflowCardH, SURFACE_BG)

    tx(
      s,
      nm(s, `Ph${i + 1}Num`),
      x + S.layout.cardPadX,
      2.6,
      cardW - S.layout.cardPadX * 2,
      0.4,
      p.num,
      {
        name: FONT_LATIN,
        size: F.eyebrow,
        bold: true,
        color: C.primary,
      },
    )

    tx(
      s,
      nm(s, `Ph${i + 1}T`),
      x + S.layout.cardPadX,
      3.0,
      cardW - S.layout.cardPadX * 2,
      0.7,
      p.title,
      {
        name: FONT_LATIN,
        size: '22pt',
        bold: true,
        color: C.textPri,
      },
    )

    tx(
      s,
      nm(s, `Ph${i + 1}B`),
      x + S.layout.cardPadX,
      3.8,
      cardW - S.layout.cardPadX * 2,
      1.8,
      p.body,
      {
        name: FONT_LATIN,
        size: F.body,
        color: C.textSec,
      },
    )
  })
}

// slide 7：hero 收尾（整页 primaryDk 背景 + 大标题 + 3 个 takeaway 卡片）
function slideHero(total) {
  const s = 7
  addThemedSlide(s)

  // 右上装饰圆形
  box(s, nm(s, 'Deco'), 'oval', 10.4, 0.2, 2.6, 2.6, C.primary)

  // 左侧 accent 竖条
  box(
    s,
    nm(s, 'AccentBar'),
    'rectangle',
    S.layout.marginX,
    2.0,
    S.chrome.headerAccentW,
    3.0,
    C.amber,
  )
  const textX = S.layout.marginX + S.chrome.headerAccentW + 0.22

  // eyebrow
  tx(s, nm(s, 'Eyebrow'), textX, 2.0, 11, 0.4, 'FINAL · MANAGEMENT RECOMMENDATION', {
    name: FONT_LATIN,
    size: '13pt',
    bold: true,
    color: C.primary,
  })

  // hero 大标题
  tx(
    s,
    nm(s, 'Hero'),
    textX,
    2.5,
    12,
    2.4,
    'Fund the controllable loss pool\nbefore broad brand activity',
    {
      name: FONT_LATIN,
      size: F.hero,
      bold: true,
      color: C.textPri,
    },
  )

  // 副标
  tx(
    s,
    nm(s, 'Sub'),
    textX,
    5.1,
    12,
    0.5,
    'A focused loyalty programme can address 78% of customer loss with low incremental cost',
    { name: FONT_LATIN, size: '16pt', color: C.textSec },
  )

  // 底部 3 个 takeaway 卡片
  const tasks = [
    { t: 'Price', b: 'loyalty discount + trade-in' },
    { t: 'Service', b: '3-year after-sales repair' },
    { t: 'Data', b: 'survey incentive + tracking' },
  ]
  const gap = S.layout.gridGap
  const cells = grid(tasks.length, gap)
  tasks.forEach((tk, i) => {
    const { x, w: cardW } = cells[i]
    const card = nm(s, `Tk${i + 1}Bg`)
    cardBox(s, card, x, 5.64, cardW, 1.18, SURFACE_BG)

    tx(
      s,
      nm(s, `Tk${i + 1}T`),
      x + S.layout.cardPadX,
      5.79,
      cardW - S.layout.cardPadX * 2,
      0.5,
      tk.t,
      {
        name: FONT_LATIN,
        size: '18pt',
        bold: true,
        color: C.textPri,
      },
    )

    tx(
      s,
      nm(s, `Tk${i + 1}B`),
      x + S.layout.cardPadX,
      6.27,
      cardW - S.layout.cardPadX * 2,
      0.5,
      tk.b,
      {
        name: FONT_LATIN,
        size: '11pt',
        color: C.textSec,
      },
    )
  })

  // 页脚（白色文字）
  const pg = nm(s, 'PageNum')
  tx(
    s,
    pg,
    12.0,
    footerTextY(),
    1.2,
    FOOTER_TEXT_H,
    `${String(total).padStart(2, '0')} / ${String(total).padStart(2, '0')}`,
    { name: FONT_LATIN, size: F.foot, color: C.textMut },
  )
  pAlign(s, pg, 'right')
}

// ============================================================
// layout variant: narrative-split
// ============================================================

function slideNarrativeCover(total) {
  const s = 0
  addThemedSlide(s, C.primaryDp)
  box(s, nm(s, 'LeftInk'), 'rectangle', 0, 0, 5.05, SLIDE_H, C.primaryDp)
  box(s, nm(s, 'RightPaper'), 'rectangle', 5.05, 0, 8.283, SLIDE_H, PAGE_BG)
  box(s, nm(s, 'SplitRule'), 'rectangle', 5.02, 0, 0.05, SLIDE_H, C.secondary)
  tx(s, nm(s, 'Eyebrow'), 0.72, 0.7, 3.85, 0.25, 'MCKINSEY EUROPE · CUSTOMER STRATEGY PRACTICE', {
    name: FONT_LATIN,
    size: '9.5pt',
    color: C.onHero,
  })
  thinLine(s, nm(s, 'LeftInk'), C.primaryDp, '0pt')
  tx(s, nm(s, 'Title'), 0.72, 1.28, 4.15, 0.5, 'McKinsey', {
    name: FONT_LATIN,
    size: '26pt',
    bold: true,
    color: C.onHero,
  })
  tx(s, nm(s, 'Title2'), 0.72, 1.83, 4.15, 0.5, 'Customer', {
    name: FONT_LATIN,
    size: '26pt',
    bold: true,
    color: C.onHero,
  })
  tx(s, nm(s, 'Title3'), 0.72, 2.38, 4.15, 0.5, 'Loyalty', {
    name: FONT_LATIN,
    size: '26pt',
    bold: true,
    color: C.onHero,
  })
  tx(s, nm(s, 'Title4'), 0.72, 2.93, 4.15, 0.5, 'Programme', {
    name: FONT_LATIN,
    size: '26pt',
    bold: true,
    color: C.onHero,
  })
  tx(s, nm(s, 'Sub'), 0.72, 4.05, 4.25, 0.58, MCKINSEY.subtitle, {
    name: FONT_LATIN,
    size: '14pt',
    color: C.pale,
  })
  MCKINSEY.metrics.forEach((metric, i) => {
    metricCard(s, nm(s, `CoverMetric${i + 1}`), 5.65 + i * 2.45, 1.55, 2.1, 3.0, metric)
  })
  cardBox(s, nm(s, 'ProjectBox'), 5.65, 5.25, 7.15, 1.15, SURFACE_BG)
  tx(s, nm(s, 'ProjectTitle'), 5.95, 5.46, 1.5, 0.22, 'PROJECT DETAILS', {
    name: FONT_LATIN,
    size: F.eyebrow,
    bold: true,
    color: C.textMut,
  })
  tx(
    s,
    nm(s, 'ProjectBody'),
    7.45,
    5.38,
    4.7,
    0.52,
    'Client: McKinsey European Headquarters, Paris\nScope: Customer loyalty programme - European market strategy',
    { name: FONT_LATIN, size: '10.5pt', color: C.textSec },
  )
  mckFooter(s, total)
}

function slideNarrativeMetrics(total) {
  const s = 1
  addThemedSlide(s)
  mckHeader(
    s,
    'McKinsey retains only 15% of buyers - a structural loyalty crisis threatening long-term growth',
    '85% of customers never return; 78% of defections stem from competitive pricing and service failure',
  )
  box(s, nm(s, 'StoryRail'), 'rectangle', 0.55, 1.65, 4.05, 5.55, C.primaryDp)
  const railText = readableTextOn(C.primaryDp, C.onHero)
  const railMuted = readableTextOn(C.primaryDp, C.pale)
  const railAccent = contrastRatio(C.secondary, C.primaryDp) >= 4.5 ? C.secondary : railText
  tx(s, nm(s, 'StoryEyebrow'), 0.86, 2.0, 3.3, 0.24, 'CORE THESIS', {
    name: FONT_LATIN,
    size: F.eyebrow,
    bold: true,
    color: railAccent,
  })
  tx(
    s,
    nm(s, 'StoryTitle'),
    0.86,
    2.35,
    3.45,
    1.48,
    'The retention problem is\nnarrow enough to target\nand large enough to matter.',
    { name: FONT_LATIN, size: '18pt', bold: true, color: railText },
  )
  tx(
    s,
    nm(s, 'StoryBody'),
    0.86,
    4.18,
    3.35,
    1.45,
    'Competitor switching and service disappointment explain 78 of every 100 lost customers. Both causes are controllable through the proposed programme.',
    { name: FONT_LATIN, size: '11pt', color: railMuted },
  )
  MCKINSEY.metrics.forEach((metric, i) => {
    compactMetricCard(s, nm(s, `NarrMetric${i + 1}`), 5.0, 1.75 + i * 1.65, 7.55, 1.35, metric)
  })
  mckFooter(s, total, { source: railMuted })
}

function slideNarrativeDrivers(total) {
  const s = 2
  addThemedSlide(s)
  mckHeader(
    s,
    '52% switch to competitors, 26% cite service failure - 78% of customer loss is controllable',
    'Targeting both root causes can recover the vast majority of lapsed customers',
  )
  tx(
    s,
    nm(s, 'BarLabel'),
    S.layout.marginX,
    1.62,
    8.2,
    0.22,
    'FATE OF 100 MCKINSEY BUYERS - ONE PURCHASE COHORT',
    {
      name: FONT_LATIN,
      size: '10pt',
      color: C.textMut,
    },
  )
  stackedCohortBar(s, 2.05)
  panelBox(s, nm(s, 'NarrConclusion'), S.layout.marginX, 4.2, 7.9, 1.3, SURFACE_BG)
  tx(s, nm(s, 'NarrConclusionT'), 0.82, 4.48, 2.2, 0.28, 'Strategic implication:', {
    name: FONT_LATIN,
    size: '14pt',
    bold: true,
    color: C.primary,
  })
  tx(
    s,
    nm(s, 'NarrConclusionB'),
    0.82,
    4.9,
    7.35,
    0.34,
    'A targeted loyalty programme addressing pricing and service can realistically double repeat purchases within 12 months.',
    { name: FONT_LATIN, size: '12pt', color: C.textSec },
  )
  cardBox(s, nm(s, 'NarrSummary'), 9.0, 3.95, 3.5, 2.0, C.primaryDp)
  tx(s, nm(s, 'NarrSummaryLab'), 9.35, 4.25, 2.8, 0.24, 'STRATEGIC SUMMARY', {
    name: FONT_LATIN,
    size: '10pt',
    color: C.pale,
  })
  tx(s, nm(s, 'NarrSummaryNum'), 9.35, 4.72, 2.8, 0.72, '78%', {
    name: FONT_LATIN,
    size: '40pt',
    bold: true,
    color: C.amber,
  })
  tx(s, nm(s, 'NarrSummaryTxt'), 9.35, 5.56, 2.8, 0.36, 'of customer loss is controllable', {
    name: FONT_LATIN,
    size: '12pt',
    color: C.onHero,
  })
  mckFooter(s, total)
}

function slideNarrativeActions(total) {
  const s = 3
  addThemedSlide(s)
  mckHeader(
    s,
    'After-sales service is the highest-priority performance gap',
    'Reliability and price are strengths to protect; service sits in the urgent Invest quadrant',
  )
  const leftX = S.layout.marginX
  panelBox(
    s,
    nm(s, 'Matrix'),
    leftX,
    1.55,
    7.35,
    4.95,
    isDarkColor(PAGE_BG) ? SURFACE_BG : 'F8FAFC',
  )
  box(s, nm(s, 'MatrixV'), 'rectangle', leftX + 3.66, 1.55, 0.015, 4.95, C.divider)
  box(s, nm(s, 'MatrixH'), 'rectangle', leftX, 4.02, 7.35, 0.015, C.divider)
  const investBg = C.negBg
  const protectBg = C.posBg
  box(s, nm(s, 'InvestZone'), 'rectangle', leftX + 3.67, 4.04, 3.68, 2.46, investBg)
  box(s, nm(s, 'ProtectZone'), 'rectangle', leftX + 3.67, 1.55, 3.68, 2.47, protectBg)
  const bubbles = [
    ['Reliability', leftX + 4.65, 2.25, 0.86, C.posTxt],
    ['Price', leftX + 5.8, 2.86, 0.7, C.primary],
    ['Economy', leftX + 6.55, 3.62, 0.76, C.primaryDk],
    ['After-\nsales', leftX + 4.75, 5.02, 1.08, C.warn],
  ]
  bubbles.forEach(([label, x, y, size, color], i) => {
    box(s, nm(s, `Bubble${i + 1}`), 'oval', x, y, size, size, color)
    tx(s, nm(s, `Bubble${i + 1}T`), x + 0.08, y + size / 2 - 0.18, size - 0.16, 0.38, label, {
      name: FONT_LATIN,
      size: '9pt',
      bold: true,
      color: readableTextOn(color, C.white),
    })
    pAlign(s, nm(s, `Bubble${i + 1}T`), 'center')
  })
  const findingBg = C.negBg
  const findingText = readableTextOn(findingBg, C.onHero)
  const findingMuted = readableTextOn(findingBg, C.pale)
  const findingAccent = contrastRatio(C.warn, findingBg) >= 4.5 ? C.warn : findingText
  const findingPositive = contrastRatio(C.posTxt, findingBg) >= 4.5 ? C.posTxt : findingText
  cardBox(s, nm(s, 'CriticalFinding'), 8.35, 1.55, 3.75, 4.95, findingBg)
  box(s, nm(s, 'CriticalRule'), 'rectangle', 8.35, 1.55, 0.06, 4.95, findingAccent)
  tx(s, nm(s, 'CriticalEyebrow'), 8.65, 1.95, 2.8, 0.2, 'CRITICAL FINDING', {
    name: FONT_LATIN,
    size: F.eyebrow,
    bold: true,
    color: findingAccent,
  })
  tx(s, nm(s, 'CriticalTitle'), 8.65, 2.45, 2.85, 0.3, 'After-Sales Service', {
    name: FONT_LATIN,
    size: '14pt',
    bold: true,
    color: findingText,
  })
  tx(s, nm(s, 'CriticalNum'), 8.65, 3.25, 2.85, 0.62, '67%', {
    name: FONT_LATIN,
    size: '30pt',
    bold: true,
    color: findingAccent,
  })
  tx(
    s,
    nm(s, 'CriticalText'),
    8.65,
    3.9,
    2.85,
    1.25,
    'rate it Fair or Poor\nOnly 33% say Good+\nDrives 26% of defection',
    {
      name: FONT_LATIN,
      size: '11pt',
      color: findingMuted,
    },
  )
  tx(s, nm(s, 'CriticalPriority'), 8.65, 5.55, 2.85, 0.28, 'Must-fix priority', {
    name: FONT_LATIN,
    size: '11pt',
    bold: true,
    color: findingPositive,
  })
  mckFooter(s, total)
}

// ============================================================
// layout variant: data-room
// ============================================================

function dataRoomHeader(slide, title) {
  box(slide, nm(slide, 'DataTop'), 'rectangle', 0, 0, SLIDE_W, 0.42, C.primaryDp)
  tx(
    slide,
    nm(slide, 'DataKicker'),
    S.layout.marginX,
    0.12,
    3.8,
    0.14,
    'MCKINSEY CUSTOMER LOYALTY DATA ROOM',
    {
      name: FONT_LATIN,
      size: '8pt',
      bold: true,
      color: C.onHero,
    },
  )
  tx(slide, nm(slide, 'Title'), S.layout.marginX, 0.72, 11.8, 0.38, title, {
    name: FONT_LATIN,
    size: '20pt',
    bold: true,
    color: C.textPri,
  })
}

function slideDataRoomCover(total) {
  const s = 0
  addThemedSlide(s)
  dataRoomHeader(s, MCKINSEY.title)
  tx(s, nm(s, 'Sub'), S.layout.marginX, 1.22, 8.5, 0.34, MCKINSEY.subtitle, {
    name: FONT_LATIN,
    size: '14pt',
    color: C.textSec,
  })
  const cells = grid(4, 0.18, S.layout.marginX, 12.15)
  MCKINSEY.segments.forEach((seg, i) => {
    const { x, w } = cells[i]
    cardBox(s, nm(s, `Segment${i + 1}`), x, 2.0, w, 1.45, SURFACE_BG)
    tx(s, nm(s, `Segment${i + 1}Val`), x + 0.18, 2.25, w - 0.36, 0.5, seg.value, {
      name: FONT_LATIN,
      size: '28pt',
      bold: true,
      color: C.primary,
    })
    tx(s, nm(s, `Segment${i + 1}Lab`), x + 0.18, 2.86, w - 0.36, 0.24, seg.label, {
      name: FONT_LATIN,
      size: '10pt',
      color: C.textPri,
      bold: true,
    })
    tx(s, nm(s, `Segment${i + 1}Note`), x + 0.18, 3.13, w - 0.36, 0.22, seg.note, {
      name: FONT_LATIN,
      size: '8.5pt',
      color: C.textMut,
    })
  })
  stackedCohortBar(s, 4.55, S.layout.marginX, 12.15)
  cardBox(s, nm(s, 'DataSummary'), S.layout.marginX, 6.15, 12.15, 0.62, C.primaryDp)
  tx(
    s,
    nm(s, 'DataSummaryText'),
    0.85,
    6.33,
    11.5,
    0.22,
    'Decision gate: fund a five-initiative programme focused on price incentives, after-sales repair, and survey data quality.',
    {
      name: FONT_LATIN,
      size: '11pt',
      bold: true,
      color: C.onHero,
    },
  )
  mckFooter(s, total)
}

function slideDataRoomTable(total) {
  const s = 1
  addThemedSlide(s)
  dataRoomHeader(s, 'Customer loss drivers and programme countermeasures')
  const tableName = 'DataRoomTable'
  ops.push({
    op: 'add-table',
    slide: s,
    rows: 5,
    columns: 5,
    name: tableName,
    x: `${S.layout.marginX}in`,
    y: '1.55in',
    w: '12.15in',
    h: '3.55in',
    data: [
      ['Driver', 'Share', 'Controllable', 'Countermeasure', 'Expected role'],
      [
        'Competitor switch',
        '52%',
        'Yes',
        'Loyalty discount + trade-in',
        'Recover price-sensitive buyers',
      ],
      ['Service failure', '26%', 'Yes', '3-year free after-sales', 'Fix must-fix satisfaction gap'],
      ['Unknown reason', '9%', 'Reducible', 'Survey incentive', 'Improve decision quality'],
      ['Structural loss', '13%', 'No', 'Monitor only', 'Avoid over-investment'],
    ],
  })
  styleComparisonTable(s, tableName, 5, 5)
  const cells = grid(3, 0.22, S.layout.marginX, 12.15)
  MCKINSEY.initiatives.forEach((item, i) => {
    const { x, w } = cells[i]
    cardBox(s, nm(s, `Initiative${i + 1}`), x, 5.65, w, 1.05, SURFACE_BG)
    tx(s, nm(s, `Initiative${i + 1}T`), x + 0.18, 5.86, w - 0.36, 0.22, item.label, {
      name: FONT_LATIN,
      size: '11pt',
      bold: true,
      color: C.textPri,
    })
    tx(s, nm(s, `Initiative${i + 1}B`), x + 0.18, 6.17, w - 0.36, 0.32, item.body, {
      name: FONT_LATIN,
      size: '8.8pt',
      color: C.textSec,
    })
  })
  mckFooter(s, total)
}

function slideDataRoomDashboard(total) {
  const s = 2
  addThemedSlide(s)
  dataRoomHeader(
    s,
    'Retention economics: small number of controllable levers, large addressable upside',
  )
  const cells = grid(3, 0.22, S.layout.marginX, 12.15)
  MCKINSEY.metrics.forEach((metric, i) => {
    const { x, w } = cells[i]
    compactMetricCard(s, nm(s, `DashMetric${i + 1}`), x, 1.55, w, 1.55, metric)
  })
  panelBox(s, nm(s, 'DataChartPanel'), S.layout.marginX, 3.85, 7.8, 2.65, CHART_BG)
  ops.push({
    op: 'add-chart',
    slide: s,
    kind: 'bar',
    variant: 'clustered',
    x: `${S.layout.marginX + 0.24}in`,
    y: '4.06in',
    w: '7.25in',
    h: '2.22in',
    name: 'DataDriverChart',
    data: {
      categories: [
        'Competitor switch',
        'Service failure',
        'Unknown',
        'Relocated',
        'Stopped driving',
      ],
      series: [{ name: 'Loss share', values: [52, 26, 9, 8, 5] }],
    },
  })
  ops.push({
    op: 'set-chart',
    slide: s,
    shape: { name: 'DataDriverChart' },
    series: [{ series: 0, fill: { type: 'solid', color: C.warn } }],
  })
  cardBox(s, nm(s, 'DataDecision'), 8.85, 3.85, 3.7, 2.65, C.primaryDp)
  tx(s, nm(s, 'DataDecisionNum'), 9.25, 4.35, 2.9, 0.72, '78%', {
    name: FONT_LATIN,
    size: '38pt',
    bold: true,
    color: C.amber,
  })
  tx(
    s,
    nm(s, 'DataDecisionText'),
    9.25,
    5.12,
    2.9,
    0.82,
    'controllable loss pool\n= competitor + service',
    {
      name: FONT_LATIN,
      size: '12pt',
      color: C.onHero,
    },
  )
  mckFooter(s, total)
}

function slideDataRoomActions(total) {
  const s = 3
  addThemedSlide(s)
  dataRoomHeader(
    s,
    'Action register: fund the programme where the loss pool is both large and controllable',
  )
  const x = S.layout.marginX
  const rowH = 0.82
  const rows = [
    ['1', 'Loyalty discount', 'Competitor switch', '52%', 'Launch with franchise cost share'],
    [
      '2',
      'Free 3-year after-sales',
      'Service failure',
      '26%',
      'Make service the first-phase flagship',
    ],
    ['3', 'Trade-in path', 'Under-40 mainstream', '75%', 'Create a second-purchase trigger'],
    ['4', 'Survey incentive', 'Unknown reason', '9%', 'Lift response rate from 40% to 70%'],
    [
      '5',
      'Editorial programme',
      'Lifestyle interests',
      'Top 5',
      'Align magazine content to customer priorities',
    ],
  ]
  rows.forEach((row, i) => {
    const y = 1.45 + i * (rowH + 0.12)
    cardBox(s, nm(s, `ActionRow${i + 1}`), x, y, 12.15, rowH, i < 2 ? C.posBg : SURFACE_BG)
    tx(s, nm(s, `ActionNum${i + 1}`), x + 0.16, y + 0.23, 0.35, 0.22, row[0], {
      name: FONT_LATIN,
      size: '11pt',
      bold: true,
      color: C.primary,
    })
    tx(s, nm(s, `ActionName${i + 1}`), x + 0.65, y + 0.2, 2.4, 0.24, row[1], {
      name: FONT_LATIN,
      size: '11pt',
      bold: true,
      color: C.textPri,
    })
    tx(s, nm(s, `ActionCause${i + 1}`), x + 3.3, y + 0.2, 2.2, 0.24, row[2], {
      name: FONT_LATIN,
      size: '10pt',
      color: C.textSec,
    })
    tx(s, nm(s, `ActionShare${i + 1}`), x + 5.75, y + 0.16, 0.85, 0.3, row[3], {
      name: FONT_LATIN,
      size: '14pt',
      bold: true,
      color: i < 2 ? C.warn : C.primary,
    })
    tx(s, nm(s, `ActionNext${i + 1}`), x + 6.95, y + 0.2, 4.75, 0.24, row[4], {
      name: FONT_LATIN,
      size: '10pt',
      color: C.textSec,
    })
  })
  mckFooter(s, total)
}

const variantSlideSets = {
  'executive-grid': [
    slideCover,
    slideAgenda,
    slideKPI,
    slideChart,
    slideTable,
    slidePillars,
    slideWorkflow,
    slideHero,
  ],
  'narrative-split': [
    slideNarrativeCover,
    slideNarrativeMetrics,
    slideNarrativeDrivers,
    slideNarrativeActions,
    slideTable,
    slidePillars,
    slideWorkflow,
    slideHero,
  ],
  'data-room': [
    slideDataRoomCover,
    slideDataRoomTable,
    slideDataRoomDashboard,
    slideDataRoomActions,
    slideTable,
    slidePillars,
    slideWorkflow,
    slideHero,
  ],
}

// ============================================================
// main
// ============================================================
const TOTAL = 8
for (const renderSlide of variantSlideSets[layoutVariant]) {
  renderSlide(TOTAL)
}

process.stdout.write(
  JSON.stringify({ schemaVersion: 'pptx-patch/v1', layoutVariant, ops }, null, 2),
)
