import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
import { fitTextPlan } from '../shared/text-layout.mjs'
export const number = (n) => {
  if (!Number.isFinite(n)) throw Error('Finite evidence required')
  return n !== 0 && (Math.abs(n) < 0.001 || Math.abs(n) >= 1e7)
    ? n.toExponential(2)
    : Number(n.toPrecision(10)).toString()
}
export const numberFormat = (values) =>
  values.some((v) => v !== 0 && (Math.abs(v) < 0.001 || Math.abs(v) >= 1e7))
    ? '0.00E+00'
    : values.every(Number.isInteger)
      ? '0'
      : '0.00'
// This narrow heading intentionally occupies multiple lines. Make Latin wrapping
// explicit as well as CJK wrapping, retaining every word and the allocated frame.
function wrapReviewHeading(value, width, style) {
  const capacity = (((width - 0.04) * 72) / style.sizePt / 1.08) * 0.85
  return value
    .split('\n')
    .map((paragraph) => {
      const lines = []
      let line = ''
      for (const word of paragraph.split(/\s+/u)) {
        const next = line ? `${line} ${word}` : word
        if (line && textUnits(next) > capacity) {
          lines.push(line)
          line = word
        } else line = next
      }
      if (line) lines.push(line)
      return lines.join('\n')
    })
    .join('\n')
}
export function compileScholarLayout(design, family, id, variant, d, path = 'data') {
  const b = design.scholar,
    r = variant.regions,
    cs = []
  const tx = (name, frame, value, key = 'body', fields = name, extra = {}) => {
    const paths = (Array.isArray(fields) ? fields : [fields]).map((v) => `${path}.${v}`)
    const c = {
      ...fitTextPlan(value, frame, { ...b.styles[key], ...extra }, paths[0]),
      name,
      paths,
    }
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'rule', kind = 'box') => {
    const c = { kind, name, frame, color }
    cs.push(c)
    return c
  }
  const line = (name, x, y, len, color = 'rule', vertical = false, thickness = 0.009) =>
    box(name, vertical ? [x, y, thickness, len] : [x, y, len, thickness], color)
  const cells = (f, n, vertical = false, g = b.spacing.gap) =>
    Array.from({ length: n }, (_, i) =>
      vertical
        ? [f[0], f[1] + (i * (f[3] + g)) / n, f[2], (f[3] - g * (n - 1)) / n]
        : [f[0] + (i * (f[2] + g)) / n, f[1], (f[2] - g * (n - 1)) / n, f[3]],
    )
  const poly = (
    name,
    frame,
    points,
    { fill, line: stroke = 'ink', linePt = 0.8, close = false } = {},
  ) => {
    const c = {
      kind: 'path',
      name,
      frame,
      fill,
      line: stroke,
      linePt,
      path: {
        width: 100000,
        height: 100000,
        commands: points
          .map(([x, y], i) => ({
            type: i ? 'line' : 'move',
            x: Math.round(x * 100000),
            y: Math.round(y * 100000),
          }))
          .concat(close ? [{ type: 'close' }] : []),
      },
    }
    cs.push(c)
    return c
  }
  const ellipse = (name, frame, fill = 'paper', stroke = 'ink') =>
    poly(
      name,
      frame,
      Array.from({ length: 73 }, (_, i) => [
        0.5 + 0.49 * Math.cos((i * Math.PI) / 36),
        0.5 + 0.49 * Math.sin((i * Math.PI) / 36),
      ]),
      { fill, line: stroke, linePt: 1.1, close: true },
    )
  const owned = (
    name,
    frame,
    value,
    fields,
    { color = 'accent', textColor = 'badgeText', shapeKind = 'ellipse', size = 12 } = {},
  ) => {
    const c = tx(name, frame, value, 'badge', fields, {
      sizePt: size,
      color: textColor,
      alignment: 'center',
    })
    Object.assign(c, { kind: 'owned', color, shapeKind, anchor: 'middle' })
    return c
  }
  const noteRows = (frame, items, field = 'notes', key = 'body') =>
    cells(frame, items.length, true, 0.24).forEach(([x, y, w, h], i) => {
      box(`${field}Mark${i}`, [x, y + 0.055, 0.1, 0.1], 'accent')
      const st = tx(
        `${field}Text${i}`,
        [x + 0.23, y, w - 0.23, h],
        `${items[i].heading}\n${items[i].body}`,
        key,
        [`${field}[${i}].heading`, `${field}[${i}].body`],
      )
      st.paragraphStyles = st.text
        .split('\n')
        .map((_, j) => (j === 0 ? b.styles.heading : b.styles[key]))
      st.paragraphAfterPt = st.text.split('\n').map((_, j) => (j === 0 ? 8 : 0))
      if (i) line(`${field}Divider${i}`, x, y - 0.14, w)
    })
  const table = (frame) => {
    const cellsData = [d.headers, ...d.rows.map((v) => [v.label, ...v.cells])],
      weights = d.headers.map((_, i) => (i ? 1 : 1.45)),
      sum = weights.reduce((a, v) => a + v, 0),
      widths = weights.map((v) => (frame[2] * v) / sum),
      rowHeights = cellsData.map((_, i) => (i === 0 ? 0.48 : (frame[3] - 0.48) / d.rows.length)),
      bindings = []
    let yy = frame[1]
    cellsData.forEach((row, i) => {
      let xx = frame[0]
      row.forEach((v, j) => {
        const paths = [
            `${path}.${i === 0 ? `headers[${j}]` : j === 0 ? `rows[${i - 1}].label` : `rows[${i - 1}].cells[${j - 1}]`}`,
          ],
          // The native first-column cell reserves 0.52in for its icon. Use that
          // actual inset in capacity checks and projected slot budgets as well.
          f = [
            xx + (i > 0 && j === 0 ? 0.52 : 0.12),
            yy + 0.07,
            widths[j] - (i > 0 && j === 0 ? 0.59 : 0.24),
            rowHeights[i] - 0.14,
          ],
          st = {
            ...b.styles.table,
            bold: i === 0 || j === 0,
            color: i && j === 0 ? 'white' : 'ink',
          }
        fitTextPlan(v, f, st, paths[0])
        bindings.push({ paths, frame: f, style: st })
        xx += widths[j]
      })
      yy += rowHeights[i]
    })
    cs.push({
      kind: 'table',
      name: 'SegmentTable',
      frame,
      cells: cellsData,
      columns: d.headers.map((label, i) => ({ label, align: i === 0 ? 'left' : 'center' })),
      widths,
      rowHeights,
      bindings,
      useBindingStyles: true,
      focusColumn: 0,
      focusTone: 'ink',
      rowTones: d.rows.map((v) => v.tone),
      emphasis: d.rows.map((v) => v.emphasisColumn),
    })
    let rowY = frame[1] + rowHeights[0]
    d.rows.forEach((v, i) => {
      const iconFrame = [frame[0] + 0.14, rowY + (rowHeights[i + 1] - 0.28) / 2, 0.28, 0.28]
      ellipse(`SegmentIconBack${i}`, iconFrame, 'white', null)
      cs.push({
        kind: 'icon',
        name: `SegmentIcon${i}`,
        frame: [iconFrame[0] + 0.045, iconFrame[1] + 0.045, 0.19, 0.19],
        icon: v.icon,
        color: 'ink',
      })
      rowY += rowHeights[i + 1]
    })
  }
  if (family.role === 'case') box('CaseHeaderBand', [0, 0, 13.333, 2.05], 'blush')
  if (family.role === 'cover') {
    tx('Eyebrow', b.chrome.eyebrow, d.eyebrow, 'label', 'eyebrow', { color: 'ink' })
    tx('Hero', r.hero, d.title, 'hero', 'title')
    tx('Subtitle', r.subtitle, d.subtitle, 'heading', 'subtitle', { bold: false })
    line('CoverRule', 0.8, 4.78, 7.7, 'ink')
    line('CoverCoralRule', 0.8, 4.78, 0.7, 'accent', false, 0.018)
    owned('StudyBadge', r.badge, d.badge, 'badge', { shapeKind: 'rectangle', size: 12 })
    const f = r.field,
      [x, y, w, h] = f
    const arch = [
      ...[...Array(41)].map((_, i) => {
        const a = Math.PI + (i * Math.PI) / 40
        return [0.5 + 0.5 * Math.cos(a), 0.31 + 0.31 * Math.sin(a)]
      }),
      [1, 1],
      [0, 1],
    ]
    poly('CoverArch', f, arch, { fill: 'pale', line: 'contour', close: true })
    for (let j = 0; j < 17; j++) {
      const t = 0.07 + j * 0.053,
        edge = t < 0.31 ? 0.5 - Math.sqrt(Math.max(0, 1 - ((t - 0.31) / 0.31) ** 2)) * 0.5 : 0
      const pts = Array.from({ length: 31 }, (_, i) => {
        const u = edge + ((1 - 2 * edge) * i) / 30
        return [
          u,
          Math.min(
            0.99,
            Math.max(0.005, t + 0.012 * Math.sin(u * 7 + j * 0.8) * Math.sin((i * Math.PI) / 30)),
          ),
        ]
      })
      poly(`CoverContour${j}`, f, pts, {
        line: j > 10 ? 'history' : 'contour',
        linePt: j > 10 ? 1.1 : 0.6,
      })
    }
    const commands = [
      { type: 'move', x: 17000, y: 19000 },
      { type: 'cubic', x1: 85000, y1: 20000, x2: 82000, y2: 34000, x: 52000, y: 47000 },
      { type: 'cubic', x1: 4000, y1: 66000, x2: 3000, y2: 65000, x: 100000, y: 88000 },
    ]
    const route = poly('CoverStudyPath', f, [], { line: 'ink', linePt: 3 })
    route.path.commands = commands
    const bez = (p, a, b, c, t) => [
      (1 - t) ** 3 * p[0] +
        3 * (1 - t) ** 2 * t * a[0] +
        3 * (1 - t) * t * t * b[0] +
        t ** 3 * c[0],
      (1 - t) ** 3 * p[1] +
        3 * (1 - t) ** 2 * t * a[1] +
        3 * (1 - t) * t * t * b[1] +
        t ** 3 * c[1],
    ]
    const ticks = [0.22, 0.65, 0.88]
      .map((t) => bez([0.17, 0.19], [0.85, 0.2], [0.82, 0.34], [0.52, 0.47], t))
      .concat([0.35, 0.75].map((t) => bez([0.52, 0.47], [0.04, 0.66], [0.03, 0.65], [1, 0.88], t)))
    for (const [i, [u, v]] of ticks.entries())
      poly(
        `CoverTick${i}`,
        [x + u * w - 0.05, y + v * h - 0.055, 0.1, 0.11],
        [
          [0, 1],
          [1, 0],
        ],
        { line: 'history', linePt: 1.3 },
      )
    tx('Metadata', r.metadata, `${d.metadata}\n${d.scope}`, 'label', ['metadata', 'scope'])
  } else {
    const isCase = family.role === 'case'
    tx('Title', isCase ? [0.8, 0.45, 7.05, 1] : b.chrome.title, d.title, 'title', 'title')
    line('TitleUnderline', 0.8, isCase ? 1.47 : 1.18, 0.6, 'accent', false, 0.04)
    tx('Basis', isCase ? [0.8, 1.61, 7.05, 0.36] : b.chrome.basis, d.basis, 'small', 'basis')
    if (family.role === 'methods') {
      const horizontal = id === 'horizontal',
        frames = cells(r.steps, d.steps.length, !horizontal, 0.3)
      frames.forEach(([x, y, w, h], i) => {
        const cx = horizontal ? x + w / 2 : x + 0.23,
          cy = y + 0.2
        if (i < frames.length - 1) {
          const next = frames[i + 1]
          if (horizontal)
            poly(
              `StepArrow${i}`,
              [cx + 0.25, cy - 0.045, next[0] + next[2] / 2 - cx - 0.5, 0.09],
              [
                [0, 0.5],
                [1, 0.5],
                [0.97, 0],
                [1, 0.5],
                [0.97, 1],
              ],
              { line: 'body', linePt: 0.9 },
            )
          else
            poly(
              `StepArrow${i}`,
              [cx - 0.045, cy + 0.25, 0.09, next[1] + 0.2 - cy - 0.5],
              [
                [0.5, 0],
                [0.5, 1],
                [0, 0.95],
                [0.5, 1],
                [1, 0.95],
              ],
              { line: 'body', linePt: 0.9 },
            )
        }
        owned(`StepNumber${i}`, [cx - 0.2, cy - 0.2, 0.4, 0.4], String(i + 1), 'structural.number')
        const st = tx(
          `StepText${i}`,
          horizontal ? [x, y + 0.65, w, h - 0.65] : [x + 0.7, y, w - 0.7, h],
          `${d.steps[i].heading}\n${d.steps[i].body}`,
          'label',
          [`steps[${i}].heading`, `steps[${i}].body`],
          { alignment: horizontal ? 'center' : 'left' },
        )
        st.paragraphStyles = st.text
          .split('\n')
          .map((_, j) => (j === 0 ? b.styles.heading : b.styles.label))
        st.paragraphAfterPt = st.text.split('\n').map((_, j) => (j === 0 ? 7 : 0))
      })
      const [x, y, w, h] = r.evidence
      line('TriangulationTop', x, y - 0.15, w)
      tx('TriangulationLabel', [x, y, w, 0.35], d.evidenceLabel, 'heading', 'evidenceLabel')
      const f = [x, y + 0.55, w, h - 0.55]
      cells(f, d.sources.length, !horizontal, 0.3).forEach(([xx, yy, ww, hh], i) => {
        const c = tx(
          `SourceEvidence${i}`,
          [xx, yy, ww, hh],
          `${d.sources[i].heading}\n${d.sources[i].body}`,
          'small',
          [`sources[${i}].heading`, `sources[${i}].body`],
        )
        c.paragraphStyles = c.text
          .split('\n')
          .map((_, j) =>
            j === 0 ? { ...b.styles.label, bold: true, color: 'ink' } : b.styles.small,
          )
        if (i) {
          if (horizontal) line(`SourceDivider${i}`, xx - 0.15, yy, hh, 'rule', true)
          else line(`SourceDivider${i}`, xx, yy - 0.12, ww)
        }
      })
      box('AttritionMark', [r.note[0], r.note[1] + 0.07, 0.09, 0.09], 'accent')
      tx(
        'AttritionNote',
        [r.note[0] + 0.22, r.note[1], r.note[2] - 0.22, r.note[3]],
        d.note,
        'small',
        'note',
      )
    } else if (family.role === 'finding') {
      const [x, y, w] = r.lead
      tx('MetricLabel', [x, y, w, 0.45], d.metric.label, 'heading', 'metric.label')
      tx('MetricValue', [x, y + 0.62, w, 2.0], `${number(d.metric.value)}${d.unit}`, 'metric', [
        'metric.value',
        'unit',
      ])
      tx('DotCaption', [x, y + 2.66, w, 0.65], d.dotCaption, 'small', 'dotCaption')
      const size = 0.36,
        gap = (w - size * 10) / 9,
        amount = d.metric.value / 10
      for (let i = 0; i < 10; i++) {
        const f = [x + i * (size + gap), y + 3.4, size, size],
          fraction = Math.max(0, Math.min(1, amount - i))
        ellipse(`RetentionDot${i}`, f, fraction === 1 ? 'ink' : 'paper')
        if (fraction > 0 && fraction < 1) {
          const pts = [
            [0.5, 0.5],
            ...Array.from({ length: Math.ceil(fraction * 100) + 1 }, (_, j) => {
              const a = -Math.PI / 2 + (fraction * 2 * Math.PI * j) / Math.ceil(fraction * 100)
              return [0.5 + 0.49 * Math.cos(a), 0.5 + 0.49 * Math.sin(a)]
            }),
          ]
          poly(`RetentionPartial${i}`, f, pts, { fill: 'ink', line: null, close: true })
        }
      }
      const [xx, yy, ww, hh] = r.comparison
      line('ComparisonRule', id === 'leadLeft' ? xx - 0.35 : xx + ww + 0.35, yy, hh, 'rule', true)
      tx('ComparatorLabel', [xx, yy, ww, 0.5], d.comparator.label, 'heading', 'comparator.label', {
        color: 'body',
      })
      tx(
        'ComparatorValue',
        [xx, yy + 0.65, ww, 0.8],
        `${number(d.comparator.value)}${d.unit}`,
        'comparator',
        ['comparator.value', 'unit'],
      )
      tx(
        'Gap',
        [xx, yy + 1.65, ww, 0.65],
        `${d.gapLabel}: ${number(d.metric.value - d.comparator.value)} ${d.gapUnit}`,
        'heading',
        ['gapLabel', 'gapUnit'],
        { color: 'accentText' },
      )
      noteRows([xx, yy + 2.65, ww, hh - 2.65], d.notes, 'notes', 'small')
    } else if (family.role === 'chart') {
      const values = d.points.map((v) => v.value),
        lo = Math.min(0, ...values),
        hi = Math.max(0, ...values),
        range = Math.max(hi - lo, 1)
      if (![range, lo - range * 0.15, hi + range * 0.15].every(Number.isFinite))
        throw Error(`${path}.points: derived axis range must remain finite; use a different unit`)
      for (const [i, v] of d.points.entries())
        fitTextPlan(
          `${number(v.value)}${d.unit}`,
          [0, 0, (r.plot[2] / d.points.length) * 0.7, 0.8],
          b.styles.small,
          `${path}.points[${i}].value+unit`,
        )
      cs.push({
        kind: 'chart',
        name: 'EvidenceChart',
        frame: r.plot,
        chartKind: 'column',
        data: {
          categories: d.points.map((v) => v.label),
          series: [{ name: d.seriesName, values }],
        },
        uniformSeriesTone: 'accent',
        minimum: lo < 0 ? lo - range * 0.15 : 0,
        maximum: hi + range * 0.15,
        numberFormat: numberFormat(values) + '"' + d.unit.replaceAll('"', '""') + '"',
        showValues: true,
        inputPaths: [`${path}.seriesName`, ...d.points.map((_, i) => `${path}.points[${i}].label`)],
      })
      noteRows(r.notes, d.notes)
      tx('PlotNote', r.note, `${d.plotNote} · ${d.unit}`, 'small', ['plotNote', 'unit'])
    } else if (family.role === 'mechanism') {
      noteRows(r.definitions, d.definitions, 'definitions', 'body')
      const [x, y, w, h] = r.plot
      box('ModelField', r.plot, 'pale')
      const plot = [x + 0.45, y + 0.45, w - 0.7, h - 1.55]
      tx('ModelYLabel', [x + 0.15, y + 0.1, w - 0.3, 0.27], d.yLabel, 'small', 'yLabel')
      line('ModelYAxis', plot[0], plot[1], plot[3], 'body', true)
      line('ModelXAxis', plot[0], plot[1] + plot[3], plot[2], 'body')
      poly(
        'ModelAxisArrow',
        [plot[0] + plot[2] - 0.08, plot[1] + plot[3] - 0.04, 0.08, 0.08],
        [
          [0, 0],
          [1, 0.5],
          [0, 1],
        ],
        { line: 'body' },
      )
      d.series.forEach((v, i) => {
        const pts = Array.from({ length: 81 }, (_, j) => {
          const t = d.maxTime * (j / 80)
          return [j / 80, 1 - Math.pow(2, -t / v.halfLife)]
        })
        const curve = poly(`DecayCurve${i}`, plot, pts, { line: i ? 'ink' : 'accent', linePt: 1.8 })
        curve.derived = { model: 'half-life', halfLife: v.halfLife, maxTime: d.maxTime }
      })
      d.series.forEach((v, i) =>
        tx(
          `CurveLabel${i}`,
          [x + 1.6, y + 0.8 + i * 0.45, w - 1.8, 0.3],
          `${v.label}: h=${number(v.halfLife)}`,
          'small',
          [`series[${i}].label`, `series[${i}].halfLife`],
          { color: i ? 'ink' : 'accentText', bold: true },
        ),
      )
      d.ticks.forEach((t, i) => {
        const xx = plot[0] + (t / d.maxTime) * plot[2]
        line(`ModelTick${i}`, xx, plot[1] + plot[3] - 0.08, 0.08, 'body', true)
        tx(
          `TickLabel${i}`,
          [xx - 0.16, plot[1] + plot[3] + 0.06, 0.32, 0.25],
          number(t),
          'small',
          `ticks[${i}]`,
          { alignment: 'center' },
        )
      })
      tx(
        'ModelXLabel',
        [x + 0.2, y + h - 0.65, w - 0.4, 0.28],
        `${d.xLabel} (${d.unit})`,
        'small',
        ['xLabel', 'unit'],
        { alignment: 'center' },
      )
      tx('ModelPlotNote', [x + 0.2, y + h - 0.33, w - 0.4, 0.27], d.plotNote, 'small', 'plotNote', {
        alignment: 'center',
      })
      const [xx, yy, ww, hh] = r.model
      tx('FormulaLabel', [xx, yy, ww, 0.45], d.formulaLabel, 'heading', 'formulaLabel')
      tx('Formula', [xx, yy + 0.65, ww, 0.6], 'R(t) = 2^(−t/h)', 'formula', 'structural.formula')
      line('FormulaRule', xx, yy + 1.48, ww)
      d.series.forEach((v, i) => {
        box(`LegendDot${i}`, [xx, yy + 1.85 + i * 0.6, 0.14, 0.14], i ? 'ink' : 'accent', 'circle')
        tx(
          `ModelSeries${i}`,
          [xx + 0.25, yy + 1.8 + i * 0.6, ww - 0.25, 0.5],
          `${v.label}: h = ${number(v.halfLife)} ${d.unit}`,
          'label',
          [`series[${i}].label`, `series[${i}].halfLife`, 'unit'],
          { color: i ? 'ink' : 'body', bold: true },
        )
      })
      tx('ModelNote', [xx, yy + 3.25, ww, hh - 3.25], d.modelNote, 'small', 'modelNote')
    } else if (family.role === 'segments') {
      if (d.rows.some((v) => v.cells.length !== d.headers.length - 1))
        throw Error(`${path}.rows: every row must match header count`)
      for (const row of d.rows)
        if (
          row.emphasisColumn !== undefined &&
          (!Number.isInteger(row.emphasisColumn) ||
            row.emphasisColumn < 1 ||
            row.emphasisColumn >= d.headers.length)
        )
          throw Error(`${path}.rows: emphasisColumn outside value columns`)
      table(r.table)
      tx(
        'Summary',
        r.summary,
        `${d.summaryLabel}  ${d.summaryValue}  ·  ${d.footnote}`,
        'small',
        ['summaryLabel', 'summaryValue', 'footnote'],
        { color: 'ink' },
      )
      const [x, y, w, h] = r.takeaway
      box('TakeawayMark', [x, y + 0.04, 0.1, 0.1], 'accent')
      tx('Takeaway', [x + 0.23, y, w - 0.23, h], d.takeaway, 'label', 'takeaway', {
        color: 'ink',
        bold: true,
      })
    } else if (family.role === 'case') {
      noteRows(r.notes, d.notes)
      const [x, y, w, h] = r.asset
      box('CaseImageShell', r.asset, 'pale')
      poly(
        'CaseImageCrossA',
        r.asset,
        [
          [0, 0],
          [1, 1],
        ],
        { line: 'history' },
      )
      poly(
        'CaseImageCrossB',
        r.asset,
        [
          [1, 0],
          [0, 1],
        ],
        { line: 'history' },
      )
      owned(
        'CaseImageCaption',
        [x + 0.18, y + h / 2 - 0.22, w - 0.36, 0.44],
        d.assetCaption,
        'assetCaption',
        { shapeKind: 'rectangle', color: 'pale', textColor: 'ink', size: 12 },
      )
      const [xx, yy, ww, hh] = r.result
      box('CaseResultField', r.result, 'ink')
      tx(
        'CaseResultLabel',
        [xx + 0.25, yy + 0.2, ww - 0.5, 0.5],
        d.resultLabel,
        'small',
        'resultLabel',
        { color: 'paper' },
      )
      tx(
        'CaseResultValues',
        [xx + 0.25, yy + 0.85, ww - 0.5, 0.65],
        `${number(d.before)}${d.unit} → ${number(d.after)}${d.unit}`,
        'comparator',
        ['before', 'after', 'unit'],
        { sizePt: 30, color: 'accent' },
      )
      line('CaseResultRule', xx + 0.25, yy + 1.6, ww - 0.5, 'history')
      tx(
        'CaseResultNote',
        [xx + 0.25, yy + 1.8, ww - 0.5, hh - 1.85],
        d.resultNote,
        'small',
        'resultNote',
        { color: 'paper' },
      )
      tx('CaseCaution', r.note, d.caution, 'small', 'caution')
    } else if (family.role === 'closing') {
      const frames = cells(r.actions, d.actions.length, true, 0.2)
      frames.forEach(([xx, yy, ww, hh], i) => {
        const band = poly(`ActionBand${i}`, [xx, yy, ww, hh], [], { fill: 'pale', line: null }),
          rx = 0.12 / ww,
          ry = 0.12 / hh,
          k = 0.55228475
        const p = (type, values) =>
          Object.fromEntries([
            ['type', type],
            ...Object.entries(values).map(([key, value]) => [key, Math.round(value * 100000)]),
          ])
        band.path.commands = [
          p('move', { x: rx, y: 0 }),
          p('line', { x: 1 - rx, y: 0 }),
          p('cubic', { x1: 1 - rx + k * rx, y1: 0, x2: 1, y2: ry - k * ry, x: 1, y: ry }),
          p('line', { x: 1, y: 1 - ry }),
          p('cubic', { x1: 1, y1: 1 - ry + k * ry, x2: 1 - rx + k * rx, y2: 1, x: 1 - rx, y: 1 }),
          p('line', { x: rx, y: 1 }),
          p('cubic', { x1: rx - k * rx, y1: 1, x2: 0, y2: 1 - ry + k * ry, x: 0, y: 1 - ry }),
          p('line', { x: 0, y: ry }),
          p('cubic', { x1: 0, y1: ry - k * ry, x2: rx - k * rx, y2: 0, x: rx, y: 0 }),
          { type: 'close' },
        ]
        owned(
          `ActionNumber${i}`,
          [xx + 0.15, yy + 0.13, 0.32, 0.32],
          String(i + 1),
          'structural.number',
          { size: 11 },
        )
        ellipse(`ActionIconBack${i}`, [xx + 0.13, yy + 0.62, 0.36, 0.36], 'white', null)
        cs.push({
          kind: 'icon',
          name: `ActionIcon${i}`,
          frame: [xx + 0.19, yy + 0.68, 0.24, 0.24],
          icon: d.actions[i].icon,
          color: 'ink',
        })
        const compact = id === 'ledger',
          left = compact ? 3.05 : 3.2,
          mid = compact ? 4.85 : 4.05,
          bodyX = xx + left + 0.3,
          howX = bodyX + mid + 0.2
        const c = tx(
          `ActionHeading${i}`,
          [xx + 0.67, yy + 0.19, left - 0.85, hh - 0.29],
          `${d.actions[i].heading}\n${d.actions[i].detail}`,
          'label',
          [`actions[${i}].heading`, `actions[${i}].detail`],
          { color: 'ink', bold: true },
        )
        c.paragraphStyles = c.text
          .split('\n')
          .map((_, j) => (j === 0 ? b.styles.heading : b.styles.small))
        line(`ActionDividerA${i}`, xx + left, yy + 0.18, hh - 0.36, 'history', true)
        if (compact)
          tx(
            `ActionExplanation${i}`,
            [bodyX, yy + 0.18, ww - left - 0.53, hh - 0.36],
            `${d.actions[i].why}\n${d.actions[i].how}`,
            'label',
            [`actions[${i}].why`, `actions[${i}].how`],
          )
        else {
          tx(
            `ActionWhy${i}`,
            [bodyX, yy + 0.18, mid - 0.2, hh - 0.36],
            d.actions[i].why,
            'label',
            `actions[${i}].why`,
          )
          line(`ActionDividerB${i}`, howX - 0.17, yy + 0.18, hh - 0.36, 'history', true)
          tx(
            `ActionHow${i}`,
            [howX, yy + 0.18, xx + ww - howX - 0.23, hh - 0.36],
            d.actions[i].how,
            'label',
            `actions[${i}].how`,
          )
        }
      })
      const [xx, yy, ww, hh] = r.review
      line('NextReviewRule', xx, yy - 0.12, ww)
      const reviewHeading =
        id === 'ledger' ? wrapReviewHeading(d.reviewLabel, ww, b.styles.label) : d.reviewLabel
      tx(
        'NextReviewLabel',
        [xx, yy, ww, id === 'ledger' ? 0.9 : 0.3],
        reviewHeading,
        'label',
        'reviewLabel',
        { color: 'ink', bold: true },
      )
      const f = id === 'ledger' ? [xx, yy + 1.3, ww, hh - 1.3] : [xx, yy + 0.4, ww, hh - 0.4]
      cells(f, d.review.length, id === 'ledger', 0.3).forEach(([x, y, w, h], i) => {
        tx(
          `ReviewItem${i}`,
          [x, y, w, h],
          `${d.review[i].label}: ${d.review[i].value}`,
          'small',
          [`review[${i}].label`, `review[${i}].value`],
          { color: 'ink', bold: true },
        )
        if (i) {
          if (id === 'ledger') line(`ReviewDivider${i}`, x, y - 0.12, w)
          else line(`ReviewDivider${i}`, x - 0.15, y, h, 'rule', true)
        }
      })
    } else throw Error('Unregistered Scholar role')
  }
  tx('Source', b.chrome.source, d.source, 'small', 'source')
  return cs
}
export function resolveScholarDeck(design, content, { validateData } = {}) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  if (!content.slides?.length) throw Error('At least one slide required')
  if (
    content.meta.designScope !== 'excerpt' &&
    (content.slides[0].type !== 'scholarCoverSlide' ||
      content.slides.at(-1).type !== 'scholarClosingSlide')
  )
    throw Error(
      'Complete Scholar decks require cover and closing; extracts declare designScope excerpt',
    )
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.scholar.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered type`)
    if (slide.customOps || slide.imageSlots)
      throw Error('Scholar accepts registered native content; image input is not registered')
    validateData?.(slide.type, slide.data, `slides[${s}].data`)
    const failures = []
    const candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
      try {
        const components = compileScholarLayout(
          design,
          family,
          layoutId,
          v,
          slide.data,
          `slides[${s}].data`,
        )
        components.push({
          ...fitTextPlan(
            `${String(s + 1).padStart(2, '0')}/${String(content.slides.length).padStart(2, '0')}`,
            design.scholar.chrome.page,
            design.scholar.styles.small,
            'structural.page',
          ),
          name: 'Page',
        })
        if (family.role !== 'cover')
          components.push({
            ...fitTextPlan(
              String(s + 1).padStart(2, '0'),
              design.scholar.chrome.index,
              { ...design.scholar.styles.label, color: 'accentText' },
              'structural.index',
            ),
            name: 'Index',
          })
        for (const c of components) {
          const [x, y, w, h] = c.frame
          if (
            [x, y, w, h].some((v) => !Number.isFinite(v)) ||
            Math.min(x, y, w, h) < 0 ||
            x + w > design.canvas.widthIn + 0.001 ||
            y + h > design.canvas.heightIn + 0.001
          )
            throw Error(`${c.name}: outside canvas`)
        }
        return [
          {
            layoutId,
            role: family.role,
            components,
            fingerprint: designHash({
              role: family.role,
              frames: components.map((c) => [c.kind, c.frame]),
            }),
          },
        ]
      } catch (e) {
        failures.push(`${layoutId}: ${e.message}`)
        return []
      }
    })
    let chosen
    try {
      chosen = selectDesignLayout(
        candidates,
        slide.layoutId ?? 'auto',
        layouts,
        design.scholar.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(chosen, {
      slideIndex: s,
      slideType: slide.type,
      candidates: candidates.map((v) => v.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (chosen.repeated)
      throw Error(`slides[${s}]: repeated composition exceeds registered cadence`)
  }
  return { layouts, warnings }
}
