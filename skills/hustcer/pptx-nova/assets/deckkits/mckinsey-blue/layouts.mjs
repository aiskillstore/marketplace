// Bounded consulting grammar: content -> measured component plan -> renderer.
import { readFileSync } from 'node:fs'
import { assertDesignValue, designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'
import { contrastRatio } from '../shared/core-primitives.kit.mjs'
import { hasTablerIcon } from '../shared/icon-assets.kit.mjs'

export function fitMckText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = ((frame[2] - 0.04) * 72) / style.sizePt
  const text = wrapCjkText(value, capacity * 0.94)
  let lines = 0
  for (const line of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const word of line.split(/(\s+)/u)) {
      const units = [...word].reduce(
        (n, c) => n + (c.codePointAt(0) > 255 ? 1 : 0.54 + (/[MW@]/.test(c) ? 0.23 : 0)),
        0,
      )
      if (units > capacity + 0.01) throw Error(`${path}: word exceeds width`)
      if (used && used + units > capacity) {
        lines++
        used = 0
      }
      used += units
    }
  }
  const requiredHeight = (lines * style.sizePt * 1.5) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002) {
    throw Error(
      `${path}: ${lines} lines require ${requiredHeight.toFixed(2)}in; available ${frame[3].toFixed(
        2,
      )}in`,
    )
  }
  return {
    kind: 'text',
    text,
    frame: [...frame],
    style: { ...style },
    path,
    estimatedLines: lines,
    requiredHeight,
  }
}

export function compileMckLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.mck,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap,
    pad = b.spacing.inset
  const tx = (name, f, v, key = 'body', field = name, extra = {}) => {
    if (v === undefined) return
    const fields = Array.isArray(field) ? field : [field]
    const c = {
      ...fitMckText(v, f, { ...b.styles[key], ...extra }, `${path}.${fields[0]}`),
      name,
      paths: fields.map((k) => `${path}.${k}`),
      allocatedFrame: [...f],
    }
    c.frame[3] = c.requiredHeight
    cs.push(c)
    return c
  }
  const box = (name, frame, color = 'paper', outline) =>
    cs.push({ kind: 'box', name, frame, color, outline })
  const line = (name, x, y, w, color = 'rule', vertical = false) =>
    box(name, vertical ? [x, y, 0.008, w] : [x, y, w, 0.008], color)
  const owned = (name, f, v, key = 'index', color = 'primary', field = name, extra = {}) => {
    const c = tx(name, [f[0] + 0.04, f[1], f[2] - 0.08, f[3]], v, key, field, {
      ...extra,
      alignment: 'center',
      verticalAnchor: 'middle',
    })
    c.kind = 'owned'
    c.frame = f
    c.color = color
    const bg = design.colors[color]
    c.style.color = contrastRatio(design.colors.paper, bg) >= 4.5 ? 'paper' : 'ink'
  }
  const icon = (name, f, id, color, field) => {
    if (!hasTablerIcon(id)) throw Error(`${path}.${field}: unknown Tabler icon ${id}`)
    cs.push({ kind: 'icon', name, frame: f, icon: id, color, path: `${path}.${field}` })
  }
  const grid = (f, n, cols = n) => {
    const rows = Math.ceil(n / cols),
      w = (f[2] - gap * (cols - 1)) / cols,
      h = (f[3] - gap * (rows - 1)) / rows
    return Array.from({ length: n }, (_, i) => [
      f[0] + (i % cols) * (w + gap),
      f[1] + Math.floor(i / cols) * (h + gap),
      w,
      h,
    ])
  }
  const ink = (t) =>
    ({
      amber: 'amberInk',
      red: 'redInk',
      teal: 'tealInk',
      sky: 'primary',
      muted: 'secondary',
    })[t] ?? t
  const note = (
    name,
    f,
    value,
    field,
    { color = 'primary', bg = 'blueTint', dark = false } = {},
  ) => {
    box(name + 'Bg', f, dark ? 'deep' : bg)
    box(name + 'Mark', [f[0], f[1], 0.045, f[3]], color)
    tx(
      name + 'Title',
      [f[0] + pad, f[1] + 0.1, f[2] - pad * 2, 0.3],
      value.title,
      'heading',
      field + '.title',
      { color: dark ? 'paper' : ink(color) },
    )
    tx(
      name + 'Body',
      [f[0] + pad, f[1] + 0.43, f[2] - pad * 2, f[3] - 0.49],
      value.body,
      'body',
      field + '.body',
      { color: dark ? 'paper' : 'ink' },
    )
  }
  const metric = (name, f, v, field, compact = false) => {
    box(name + 'Bg', f, 'panel')
    box(name + 'Mark', [f[0], f[1], 0.045, f[3]], v.tone)
    tx(
      name + 'Label',
      [f[0] + pad, f[1] + 0.1, f[2] - pad * 2, 0.26],
      v.label,
      'label',
      field + '.label',
    )
    const nH = compact ? 0.44 : 0.71
    tx(
      name + 'Value',
      [f[0] + pad, f[1] + 0.39, f[2] - pad * 2, nH],
      v.value,
      compact ? 'kpi' : 'metric',
      field + '.value',
      { color: ink(v.tone) },
    )
    const tail = [v.sub, v.note].filter(Boolean).join(' · ')
    if (tail) {
      tx(
        name + 'Detail',
        [f[0] + pad, f[1] + (compact ? 0.87 : 1.15), f[2] - pad * 2, f[3] - (compact ? 0.92 : 1.2)],
        tail,
        'small',
        ['sub', 'note'].filter((k) => v[k] !== undefined).map((k) => field + '.' + k),
      )
    }
  }
  const chart = (name, f, items, field, label, unit) => {
    const actual = items.map((x) => x.value)
    const categories = items.map((x) => x.label + (x.note ? ' — ' + x.note : ''))
    categories.forEach((v, i) =>
      fitMckText(
        v,
        [0, 0, f[2] * 0.35, f[3] / items.length],
        b.styles.small,
        `${path}.${field}[${i}].label`,
      ),
    )
    const digits = actual.map((v) =>
        String(v).includes('e') ? 7 : (String(v).split('.')[1]?.length ?? 0),
      ),
      decimals = Math.max(...digits)
    const numberFormat =
      decimals > 6 ? 'General' : (decimals ? '0.' + '0'.repeat(decimals) : '0') + '"%"'
    if (actual.some((x) => !Number.isFinite(x) || x < 0 || x > 100)) {
      throw Error(`${path}.${field}: percentage outside 0..100`)
    }
    // Numeric values and direct labels share the very same input; no separately editable overlays.
    cs.push({
      kind: 'chart',
      name,
      frame: f,
      data: { categories, series: [{ name: label, values: actual }] },
      tones: items.map(
        (x, i) => x.tone ?? ['primary', 'blue', 'teal', 'muted', 'secondary'][i % 5],
      ),
      numberFormat,
      unit,
      path: `${path}.${field}`,
      inputPaths: items.flatMap((v, i) =>
        ['label', 'note']
          .filter((k) => v[k] !== undefined)
          .map((k) => `${path}.${field}[${i}].${k}`),
      ),
    })
  }
  if (family.role !== 'cover') {
    tx('Title', b.chrome.title, d.title, 'title', 'title')
    box('SubtitleBar', b.chrome.bar, 'deep')
    box('SubtitleAccent', [b.chrome.bar[0], b.chrome.bar[1], 0.055, b.chrome.bar[3]], 'sky')
    tx('Subtitle', b.chrome.subtitle, d.subtitle, 'subtitle', 'subtitle')
    box('TopRule', [0, 0, design.canvas.widthIn, 0.035], 'primary')
  }
  if (family.role === 'cover') {
    cs.push({ kind: 'hero', name: 'Hero', frame: r.hero })
    tx('Eyebrow', [0.75, 0.42, 10.6, 0.3], d.eyebrow, 'small', 'eyebrow', { color: 'paper' })
    tx('Title', [0.75, 0.88, 9.7, 1.48], d.title, 'hero', 'title')
    box('CoverAccent', [0.77, 2.39, 0.6, 0.035], 'sky')
    tx('Subtitle', [0.75, 2.5, 11.3, 0.35], d.subtitle, 'subtitle', 'subtitle', { bold: false })
    const [x, y, w, h] = r.details,
      band = layoutId === 'band'
    tx('DetailsLabel', [x, y, w, 0.26], d.detailsLabel, 'label', 'detailsLabel')
    line('DetailsRule', x, y + 0.36, w)
    const frames = band
      ? grid([x, y + 0.48, w, h - 0.48], d.details.length)
      : grid([x, y + 0.52, w, h - 0.52], d.details.length, 1)
    for (const [i, item] of d.details.entries()) {
      const [cx, cy, cw, ch] = frames[i]
      tx(
        'DetailLabel' + i,
        [cx, cy, band ? cw : 1.1, band ? 0.27 : ch],
        item.label,
        'small',
        `details[${i}].label`,
        { bold: true },
      )
      tx(
        'DetailValue' + i,
        band ? [cx, cy + 0.32, cw, ch - 0.32] : [cx + 1.22, cy, cw - 1.22, ch],
        item.value,
        'small',
        `details[${i}].value`,
      )
    }
    for (const [i, v] of [d.primaryMetric, d.lossMetric].entries()) {
      const [cx, cy, cw, ch] = grid(r.metrics, 2)[i],
        base = i ? 'lossMetric' : 'primaryMetric',
        c = i ? 'amber' : 'red'
      box('CoverMetric' + i, [cx, cy, cw, ch], 'paper', 'rule')
      box('CoverMetricTop' + i, [cx, cy, cw, 0.05], c)
      tx(
        base + 'Label',
        [cx + pad, cy + 0.15, cw - pad * 2, 0.45],
        v.label,
        'label',
        base + '.label',
      )
      if (!band) {
        tx(
          base + 'value',
          [cx + pad, cy + 0.64, cw - pad * 2, 0.71],
          v.value,
          'metric',
          base + '.value',
          { color: ink(c) },
        )
        tx(base + 'sub', [cx + pad, cy + 1.38, cw - pad * 2, 0.3], v.sub, 'small', base + '.sub')
        if (i) {
          tx(
            base + 'value2',
            [cx + pad, cy + 1.75, cw - pad * 2, 0.71],
            v.value2,
            'metric',
            base + '.value2',
            { color: ink(c) },
          )
          tx(
            base + 'sub2',
            [cx + pad, cy + 2.5, cw - pad * 2, 0.26],
            v.sub2,
            'small',
            base + '.sub2',
          )
        }
        tx(
          base + 'Notes',
          [cx + pad, cy + (i ? 2.83 : 2.0), cw - pad * 2, i ? 0.48 : 1.0],
          [v.note, v.bottom, v.extra].filter(Boolean).join('\n'),
          'small',
          ['note', 'bottom', 'extra'].filter((k) => v[k] !== undefined).map((k) => base + '.' + k),
        )
      } else {
        tx(
          base + 'values',
          [cx + pad, cy + 0.65, cw * 0.35, 0.75],
          [v.value, v.value2].filter(Boolean).join(' / '),
          'kpi',
          base + '.value',
          { color: ink(c) },
        )
        tx(
          base + 'Notes',
          [cx + cw * 0.4, cy + 0.6, cw * 0.6 - pad, ch - 0.65],
          [v.sub, v.sub2, v.note, v.bottom, v.extra].filter(Boolean).join(' · '),
          'small',
          ['sub', 'sub2', 'note', 'bottom', 'extra']
            .filter((k) => v[k] !== undefined)
            .map((k) => base + '.' + k),
        )
      }
    }
  } else if (family.role === 'snapshot') {
    const rail = layoutId === 'rail'
    tx(
      'MetricHeading',
      [r.metrics[0], r.metrics[1] - 0.25, r.metrics[2], 0.25],
      d.metricLabel,
      'label',
      'metricLabel',
    )
    const f = grid(r.metrics, d.metrics.length, rail ? 1 : d.metrics.length)
    d.metrics.forEach((v, i) => metric('Metric' + i, f[i], v, `metrics[${i}]`, true))
    const [x, y, w] = r.cohort
    tx('CohortHeading', [x, y, w, 0.25], d.cohortTitle, 'label', 'cohortTitle')
    tx('CohortUnit', [x, y + 0.29, w, 0.25], d.unit, 'label', 'unit')
    const total = d.cohort.reduce((n, c) => n + c.value, 0)
    if (!(total > 0)) throw Error(`${path}.cohort: positive total required`)
    let xx = x
    d.cohort.forEach((v, i) => {
      const ww = (w * v.value) / total
      if (ww > 0.001) box('CohortSegment' + i, [xx, y + 0.59, ww, 0.37], v.tone)
      xx += ww
    })
    // Small/zero values keep their full semantic label in the legend below; no minimum fake width.
    const leg = grid(
      [x, y + 1.05, w, rail ? 1.12 : 0.71],
      d.cohort.length,
      rail ? 2 : d.cohort.length,
    )
    d.cohort.forEach((v, i) => {
      const [lx, ly, lw, lh] = leg[i]
      owned(
        'CohortValue' + i,
        [lx, ly, 0.48, 0.29],
        String(v.value),
        'label',
        v.tone,
        `cohort[${i}].value`,
        { color: ['amber', 'muted', 'teal', 'sky'].includes(v.tone) ? 'ink' : 'paper' },
      )
      tx(
        'CohortLabel' + i,
        [lx + 0.58, ly, lw - 0.58, lh],
        v.label + (v.note ? '\n' + v.note : ''),
        'small',
        ['label', 'note'].filter((k) => v[k] !== undefined).map((k) => `cohort[${i}].${k}`),
      )
    })
    const [nx, ny, nw, nh] = r.notes,
      baseY = ny + 0.4
    tx('CohortSum', [nx, ny, nw, 0.31], d.cohortSum, 'heading', 'cohortSum', {
      color: 'redInk',
    })
    const noteFrames = grid([nx, baseY, nw, nh - 0.4], 3, 3)
    note('Implication', noteFrames[0], d.implication, 'implication')
    note('Gap', noteFrames[1], d.gap, 'gap', { color: 'amber', bg: 'amberTint' })
    note('Lever', noteFrames[2], d.lever, 'lever', { color: 'green', bg: 'greenTint' })
  } else if (family.role === 'profile') {
    const band = layoutId === 'bands'
    for (const key of ['age', 'income', 'occupation']) {
      const [x, y, w, h] = r[key],
        chartH = band ? h * 0.43 : h * 0.43
      tx(key + 'Title', [x, y, w, 0.26], d.labels[key], 'label', 'labels.' + key)
      chart(key + 'Chart', [x, y + 0.32, w, chartH], d[key], key, d.labels[key], d.unit)
      const val = d[key + 'Note'],
        f = [x, y + chartH + 0.42, w, h - chartH - 0.42]
      if (typeof val === 'string') {
        tx(key + 'Note', [f[0], f[1] + 0.1, f[2], f[3] - 0.1], val, 'small', key + 'Note')
      } else note(key + 'Note', f, val, key + 'Note')
    }
    const [x, y, w, h] = r.interests
    tx('InterestsHeading', [x, y, w, 0.26], d.labels.interests, 'label', 'labels.interests')
    const f = Array.from({ length: d.interests.length }, (_, i) =>
      band
        ? [x + (i * w) / d.interests.length, y + 0.36, w / d.interests.length - 0.08, h - 0.75]
        : [x, y + 0.36 + (i * (h - 0.85)) / d.interests.length, w, (h - 0.85) / d.interests.length],
    )
    d.interests.forEach((v, i) => {
      const [cx, cy, cw, ch] = f[i]
      owned(
        'InterestIndex' + i,
        [cx, cy, 0.27, 0.27],
        String(v.index),
        'label',
        'primary',
        `interests[${i}].index`,
        { color: 'paper' },
      )
      tx(
        'InterestTitle' + i,
        [cx + 0.36, cy, band ? cw - 0.36 : 2.0, band ? 0.3 : 0.26],
        v.title,
        'small',
        `interests[${i}].title`,
        { bold: true },
      )
      tx(
        'InterestBody' + i,
        band ? [cx + 0.36, cy + 0.35, cw - 0.36, ch - 0.35] : [cx + 2.55, cy, cw - 2.55, ch],
        v.body,
        'small',
        `interests[${i}].body`,
      )
    })
    tx('InterestNote', [x, y + h - 0.28, w, 0.28], d.interestNote, 'small', 'interestNote')
  } else if (family.role === 'matrix') {
    const [x, y, w, h] = r.plot,
      [dx, dy, dw, dh] = r.detail
    for (let i = 0; i < 4; i++) {
      const xx = x + ((i % 2) * w) / 2,
        yy = y + (Math.floor(i / 2) * h) / 2
      box(
        'Quadrant' + i,
        [xx, yy, w / 2, h / 2],
        i === 1 ? 'greenTint' : i === 3 ? 'redTint' : 'panel',
      )
      tx(
        'QuadrantLabel' + i,
        [xx + 0.12, i < 2 ? yy + 0.08 : yy + h / 2 - 0.33, w / 2 - 0.24, 0.25],
        d.labels.quadrants[i],
        'label',
        `labels.quadrants[${i}]`,
        { alignment: 'center' },
      )
    }
    line('MatrixVertical', x + w / 2, y, h, 'rule', true)
    line('MatrixHorizontal', x, y + h / 2, w)
    tx('AxisX', [x, y + h + 0.06, w, 0.28], d.labels.xAxis, 'small', 'labels.xAxis', {
      alignment: 'center',
    })
    tx('AxisY', [x, y - 0.35, w, 0.25], d.labels.yAxis, 'small', 'labels.yAxis')
    const maxWeight = Math.max(...d.bubbles.map((v) => v.weight))
    const circles = []
    d.bubbles.forEach((v, i) => {
      const diam = 0.72 * Math.sqrt(v.weight / maxWeight),
        cx = x + w * v.x,
        cy = y + h * v.y
      if (!Number.isFinite(diam) || !(diam > 0)) {
        throw Error(`${path}.bubbles[${i}]: positive finite weight required`)
      }
      if (cx - diam / 2 < x || cx + diam / 2 > x + w || cy - diam / 2 < y || cy + diam / 2 > y + h)
        throw Error(`${path}.bubbles[${i}]: circle exceeds plot`)
      for (const a of circles) {
        if (Math.hypot(cx - a.x, cy - a.y) < (diam + a.d) / 2 + 0.03) {
          throw Error(`${path}.bubbles[${i}]: overlapping bubbles`)
        }
      }
      circles.push({ x: cx, y: cy, d: diam })
      cs.push({
        kind: 'circle',
        name: 'Bubble' + i,
        frame: [cx - diam / 2, cy - diam / 2, diam, diam],
        color: v.tone,
        path: `${path}.bubbles[${i}].weight`,
        value: v.weight,
      })
      const labelW = Math.min(
        2.6,
        Math.max(
          0.45,
          (([...v.label].reduce((n, c) => n + (c.codePointAt(0) > 255 ? 1 : 0.54), 0) *
            b.styles.small.sizePt) /
            72) *
            1.18 +
            0.2,
        ),
      )
      tx(
        'BubbleLabel' + i,
        [
          cx - labelW / 2,
          v.y > 0.7 || v.y < 0.4 ? cy - diam / 2 - 0.36 : cy + diam / 2 + 0.04,
          labelW,
          0.3,
        ],
        v.label,
        'small',
        `bubbles[${i}].label`,
        { color: ink(v.tone), alignment: 'center', bold: true },
      )
    })
    tx('LegendHeading', [dx, dy, dw, 0.5], d.labels.legend, 'label', 'labels.legend')
    d.legend.forEach((v, i) => {
      box('LegendMark' + i, [dx, dy + 0.57 + i * 0.33, 0.12, 0.12], v.tone)
      tx(
        'Legend' + i,
        [dx + 0.23, dy + 0.53 + i * 0.33, dw - 0.23, 0.27],
        v.label,
        'small',
        `legend[${i}].label`,
      )
    })
    const fy = dy + 2.18
    box('FindingBg', [dx, fy, dw, dh - 2.18], 'redTint')
    box('FindingMark', [dx, fy, 0.045, dh - 2.18], 'red')
    let yy = fy + 0.12
    for (const [k, key, hh] of [
      ['label', 'label', 0.28],
      ['title', 'heading', 0.3],
      ['rank', 'small', 0.3],
      ['value', 'metric', 0.71],
      ['body', 'small', 0.5],
      ['action', 'small', 0.3],
      ['must', 'small', 0.27],
    ]) {
      if (d.finding[k]) {
        tx('Finding' + k, [dx + pad, yy, dw - pad * 2, hh], d.finding[k], key, 'finding.' + k, {
          color: k === 'value' ? 'redInk' : 'ink',
        })
        yy += hh + 0.03
      }
    }
    if (yy > dy + dh + 0.01) throw Error(`${path}.finding: content exceeds detail region`)
  } else if (family.role === 'drivers') {
    tx(
      'ChartTitle',
      [r.chart[0], r.chart[1] - 0.25, r.chart[2], 0.25],
      d.chartTitle,
      'label',
      'chartTitle',
    )
    chart('DriversChart', r.chart, d.drivers, 'drivers', d.chartTitle, d.unit)
    tx(
      'DriversUnit',
      [r.chart[0], r.chart[1] + r.chart[3] + 0.02, r.chart[2], 0.25],
      d.unit,
      'label',
      'unit',
    )
    const fs = Array.from({ length: d.drivers.length }, (_, i) => [
      r.actions[0],
      r.actions[1] + (i * r.actions[3]) / d.drivers.length,
      r.actions[2],
      r.actions[3] / d.drivers.length,
    ])
    d.drivers.forEach((v, i) => {
      const [x, y, w, h] = fs[i]
      line('DriverRule' + i, x, y, w)
      tx(
        'Driver' + i,
        [x, y + 0.04, w, h - 0.05],
        [v.label, v.sub, v.tag, v.action].filter(Boolean).join(' · '),
        'small',
        ['label', 'sub', 'tag', 'action']
          .filter((k) => v[k] !== undefined)
          .map((k) => `drivers[${i}].${k}`),
      )
    })
    const [x, y, w, h] = r.summary,
      wide = layoutId === 'wide'
    box('Summary', [x, y, w, wide ? h : 2.28], 'deep')
    const sum = wide
      ? [x + pad, y + 0.1, w * 0.28 - pad, 1.7]
      : [x + pad, y + 0.12, w - pad * 2, 2.0]
    tx('SummaryLabel', [sum[0], sum[1], sum[2], 0.25], d.summary.label, 'label', 'summary.label', {
      color: 'paper',
    })
    tx(
      'SummaryValue',
      [sum[0], sum[1] + 0.35, sum[2], 0.71],
      d.summary.value,
      'metric',
      'summary.value',
      { color: 'paper' },
    )
    tx(
      'SummaryText',
      [sum[0], sum[1] + 1.05, sum[2], 0.65],
      d.summary.text,
      'body',
      'summary.text',
      { color: 'paper' },
    )
    const explain = wide ? [x + w * 0.3, y + 0.12, w * 0.3, 1.65] : [x, y + 2.45, w, 1.2]
    tx(
      'SummaryEquation',
      [explain[0] + pad, explain[1], explain[2] - pad * 2, 0.8],
      d.summary.eq,
      'body',
      'summary.eq',
      { color: wide ? 'paper' : 'ink' },
    )
    tx(
      'Controllable',
      [explain[0] + pad, explain[1] + 0.83, explain[2] - pad * 2, 0.3],
      d.controllable.value + ' ' + d.controllable.label,
      'small',
      ['controllable.value', 'controllable.label'],
      { color: wide ? 'paper' : 'redInk', bold: true },
    )
    const nf = wide
      ? [x + w * 0.63, y + 0.08, w * 0.37 - pad, h - 0.16]
      : [x, y + 3.78, w, h - 3.78]
    note('Uncontrollable', nf, d.uncontrollable, 'uncontrollable', { dark: wide })
    // Pareto is an independent retained argument rather than a silent fallback.
    const paretoF = wide ? [0.45, 4.58, 12.43, 0.25] : [0.45, 6.64, 8.4, 0.25]
    tx('ParetoInline', paretoF, d.pareto.title + ' ' + d.pareto.body, 'small', [
      'pareto.title',
      'pareto.body',
    ])
  } else if (family.role === 'pillars') {
    const rows = layoutId === 'rows',
      fs = grid(r.items, d.pillars.length, rows ? 1 : d.pillars.length)
    d.pillars.forEach((v, i) => {
      const [x, y, w, h] = fs[i],
        field = `pillars[${i}]`
      box('Pillar' + i, [x, y, w, h], 'paper', 'rule')
      if (!rows) {
        owned('PillarIndex' + i, [x, y, w, 0.48], v.index, 'index', v.tone, field + '.index')
        icon(
          'PillarIcon' + i,
          [x + w / 2 - 0.22, y + 0.66, 0.44, 0.44],
          v.icon,
          v.tone,
          field + '.icon',
        )
        tx(
          'PillarTitle' + i,
          [x + pad, y + 1.2, w - pad * 2, 0.64],
          v.title,
          'heading',
          field + '.title',
          { alignment: 'center' },
        )
        line('PillarLineA' + i, x + pad, y + 1.96, w - pad * 2)
        tx('PillarBody' + i, [x + pad, y + 2.08, w - pad * 2, 1.0], v.body, 'body', field + '.body')
        line('PillarLineB' + i, x + pad, y + 3.18, w - pad * 2)
        tx(
          'PillarOutcomeLabel' + i,
          [x + pad, y + 3.3, w - pad * 2, 0.25],
          d.labels.outcome,
          'label',
          'labels.outcome',
        )
        tx(
          'PillarOutcome' + i,
          [x + pad, y + 3.61, w - pad * 2, 0.55],
          v.outcome,
          'body',
          field + '.outcome',
          { bold: true, color: ink(v.tone) },
        )
        tx(
          'PillarKpiLabel' + i,
          [x + pad, y + 4.2, w - pad * 2, 0.25],
          d.labels.kpi,
          'label',
          'labels.kpi',
        )
        tx('PillarKpi' + i, [x + pad, y + 4.5, w - pad * 2, 0.3], v.kpi, 'body', field + '.kpi', {
          bold: true,
          color: 'amberInk',
        })
        tx(
          'PillarTime' + i,
          [x + pad, y + 4.83, w - pad * 2, 0.25],
          d.defaultTimeframe,
          'label',
          'defaultTimeframe',
        )
      } else {
        owned('PillarIndex' + i, [x, y, 0.55, h], v.index, 'index', v.tone, field + '.index')
        icon('PillarIcon' + i, [x + 0.7, y + 0.1, 0.4, 0.4], v.icon, v.tone, field + '.icon')
        tx(
          'PillarTitle' + i,
          [x + 1.25, y + 0.08, 2.45, h - 0.14],
          v.title,
          'heading',
          field + '.title',
        )
        tx('PillarBody' + i, [x + 4.0, y + 0.08, 3.2, h - 0.14], v.body, 'body', field + '.body')
        tx(
          'PillarOutcome' + i,
          [x + 7.5, y + 0.08, 2.5, h - 0.14],
          d.labels.outcome + '\n' + v.outcome,
          'small',
          ['labels.outcome', field + '.outcome'],
        )
        tx(
          'PillarKpi' + i,
          [x + 10.2, y + 0.08, w - 10.4, h - 0.14],
          d.labels.kpi + '\n' + v.kpi + '\n' + (v.timeframe ?? d.defaultTimeframe),
          'small',
          ['labels.kpi', field + '.kpi', 'defaultTimeframe'],
          { bold: true, color: 'amberInk' },
        )
      }
    })
  } else if (family.role === 'initiatives') {
    tx('SectionTitle', [0.45, 1.58, 12.43, 0.27], d.sectionTitle, 'label', 'sectionTitle')
    if (layoutId === 'ledger') {
      const [x, y, w, h] = r.items,
        rh = h / d.initiatives.length,
        widths = [(w - 0.7) * 0.2, (w - 0.7) * 0.35, (w - 0.7) * 0.17, (w - 0.7) * 0.28],
        bindings = []
      const cells = d.initiatives.map((v, i) => {
        const f = `initiatives[${i}]`,
          row = [
            v.index + ' ' + v.title + ' · ' + v.tag,
            v.body,
            d.labels.cost + ': ' + v.cost + ' · ' + d.labels.pillars + ': ' + v.pillars,
            d.labels.owner + ': ' + v.owner + ' · ' + v.ownerDetail + ' · ' + v.footer,
          ]
        let xx = x + 0.7
        const paths = [
          [f + '.index', f + '.title', f + '.tag'],
          [f + '.body'],
          ['labels.cost', f + '.cost', 'labels.pillars', f + '.pillars'],
          ['labels.owner', f + '.owner', f + '.ownerDetail', f + '.footer'],
        ]
        row.forEach((v, j) => {
          if (v.length > b.table.maxCellChars)
            throw Error(
              `${path}.${f}.cell[${j}]: table cell exceeds ${b.table.maxCellChars} characters; use columns or reorganize content`,
            )
          const frame = [xx + 0.08, y + i * rh + 0.03, widths[j] - 0.16, rh - 0.06]
          fitMckText(v, frame, b.styles.small, `${path}.${f}.cell[${j}]`)
          bindings.push({ frame, paths: paths[j].map((k) => `${path}.${k}`) })
          xx += widths[j]
        })
        icon(
          'InitiativeIcon' + i,
          [x + 0.12, y + i * rh + 0.18, 0.35, 0.35],
          v.icon,
          v.tone,
          f + '.icon',
        )
        return row
      })
      cs.push({
        kind: 'table',
        name: 'InitiativesTable',
        frame: [x + 0.7, y, w - 0.7, h],
        cells,
        widths,
        rowHeights: cells.map(() => rh),
        bindings,
      })
    } else {
      const fs = grid(r.items, d.initiatives.length)
      d.initiatives.forEach((v, i) => {
        const [x, y, w, h] = fs[i],
          f = `initiatives[${i}]`,
          color = ink(v.tone)
        if (layoutId === 'columns') {
          box('Initiative' + i, [x, y, w, h], 'paper', 'rule')
          box('InitiativeMark' + i, [x, y, w, 0.055], v.tone)
          tx(
            'InitiativeIndex' + i,
            [x + pad, y + 0.12, 0.5, 0.38],
            v.index,
            'heading',
            f + '.index',
            { color },
          )
          tx('InitiativeTag' + i, [x + 0.7, y + 0.17, w - 0.85, 0.45], v.tag, 'label', f + '.tag', {
            color,
          })
          icon(
            'InitiativeIcon' + i,
            [x + w / 2 - 0.19, y + 0.7, 0.38, 0.38],
            v.icon,
            v.tone,
            f + '.icon',
          )
          tx(
            'InitiativeTitle' + i,
            [x + pad, y + 1.25, w - pad * 2, 0.7],
            v.title,
            'heading',
            f + '.title',
            { alignment: 'center' },
          )
          line('InitiativeRule' + i, x + pad, y + 2.02, w - pad * 2)
          tx(
            'InitiativeBody' + i,
            [x + pad, y + 2.14, w - pad * 2, 0.95],
            v.body,
            'body',
            f + '.body',
          )
          tx(
            'InitiativeCost' + i,
            [x + pad, y + 3.12, w - pad * 2, 0.3],
            d.labels.cost + ': ' + v.cost,
            'small',
            ['labels.cost', f + '.cost'],
          )
          tx(
            'InitiativePillars' + i,
            [x + pad, y + 3.46, w - pad * 2, 0.3],
            d.labels.pillars + ': ' + v.pillars,
            'small',
            ['labels.pillars', f + '.pillars'],
          )
          tx(
            'InitiativeOwner' + i,
            [x + pad, y + 3.8, w - pad * 2, 0.7],
            d.labels.owner + ': ' + v.owner + '\n' + v.ownerDetail,
            'small',
            ['labels.owner', f + '.owner', f + '.ownerDetail'],
          )
          tx('InitiativeFooter' + i, [x + pad, y + 4.58, w - pad * 2, h - 4.6], v.footer, 'small', [
            'labels.cost',
            f + '.cost',
            'labels.pillars',
            f + '.pillars',
            f + '.footer',
          ])
        }
      })
    }
  } else if (family.role === 'roadmap') {
    const vertical = layoutId === 'vertical',
      fs = grid(r.phases, d.phases.length, vertical ? 1 : d.phases.length)
    d.phases.forEach((v, i) => {
      const [x, y, w, h] = fs[i],
        f = `phases[${i}]`
      if (!vertical) {
        box('Phase' + i, [x, y, w, h], 'panel')
        owned('PhaseTitle' + i, [x, y, w, 0.52], v.title, 'small', v.tone, f + '.title', {
          color: 'paper',
          bold: true,
        })
        tx('PhaseSub' + i, [x + pad, y + 0.59, w - pad * 2, 0.25], v.sub, 'label', f + '.sub')
        v.items.forEach((it, j) => {
          icon(
            `PhaseIcon${i}_${j}`,
            [x + pad, y + 0.96 + j * 0.5, 0.23, 0.25],
            it.icon,
            v.tone,
            `${f}.items[${j}].icon`,
          )
          tx(
            `PhaseTask${i}_${j}`,
            [x + pad + 0.33, y + 0.93 + j * 0.5, w - pad * 2 - 0.33, 0.47],
            it.title + '\n' + it.body,
            'small',
            ['title', 'body'].map((k) => `${f}.items[${j}].${k}`),
          )
        })
        tx(
          'PhaseCost' + i,
          [x + pad, y + h - 0.32, w - pad * 2, 0.26],
          v.cost,
          'label',
          f + '.cost',
        )
      } else {
        owned(
          'PhaseIndex' + i,
          [x, y, 0.4, 0.4],
          String(i + 1),
          'label',
          v.tone,
          'structural.phase',
          { color: 'paper' },
        )
        line('PhaseLine' + i, x + 0.2, y + 0.42, h - 0.4, v.tone, true)
        tx(
          'PhaseTitle' + i,
          [x + 0.6, y, 2.2, h],
          v.title + '\n' + v.sub + '\n' + v.cost,
          'small',
          f + '.title',
          { bold: true },
        )
        v.items.forEach((it, j) => {
          icon(
            `PhaseIcon${i}_${j}`,
            [x + 3.05, y + j * 0.48, 0.26, 0.26],
            it.icon,
            v.tone,
            `${f}.items[${j}].icon`,
          )
          tx(
            `PhaseTask${i}_${j}`,
            [x + 3.43, y + j * 0.48, w - 3.43, 0.47],
            it.title + '\n' + it.body,
            'small',
            `${f}.items[${j}]`,
          )
        })
      }
    })
    if (!vertical) {
      const [x, y, w, h] = r.phases
      line('Timeline', x, y + h + 0.06, w, 'blue')
      fs.forEach(([cx, , cw], i) =>
        cs.push({
          kind: 'circle',
          name: 'TimelineNode' + i,
          frame: [cx + cw / 2 - 0.055, y + h + 0.01, 0.11, 0.11],
          color: d.phases[i].tone,
        }),
      )
    }
    if (vertical) {
      const [x, y, w, h] = r.metrics,
        rowH = h / d.metrics.length
      d.metrics.forEach((v, i) => {
        const yy = y + i * rowH,
          f = `metrics[${i}]`
        line('OutcomeRule' + i, x, yy, w)
        tx('OutcomeLabel' + i, [x, yy + 0.06, w, 0.25], v.label, 'label', f + '.label')
        tx('OutcomeValue' + i, [x, yy + 0.37, 0.95, 0.48], v.value, 'kpi', f + '.value', {
          color: ink(v.tone),
        })
        tx(
          'OutcomeTarget' + i,
          [x + 1.1, yy + 0.37, w - 1.1, rowH - 0.4],
          [v.target, v.by, v.note].join(' · '),
          'small',
          [f + '.target', f + '.by', f + '.note'],
        )
      })
    } else {
      const mf = grid(r.metrics, d.metrics.length, vertical ? 1 : d.metrics.length)
      d.metrics.forEach((v, i) => {
        const [x, y, w, h] = mf[i],
          f = `metrics[${i}]`
        box('Outcome' + i, [x, y, w, h], 'panel')
        box('OutcomeMark' + i, [x, y, w, 0.035], v.tone)
        tx(
          'OutcomeLabel' + i,
          [x + pad, y + 0.09, w - pad * 2, 0.25],
          v.label,
          'label',
          f + '.label',
        )
        tx('OutcomeValue' + i, [x + pad, y + 0.4, w * 0.3, 0.48], v.value, 'kpi', f + '.value', {
          color: ink(v.tone),
        })
        tx(
          'OutcomeTarget' + i,
          [x + w * 0.38, y + 0.4, w * 0.62 - pad, h - 0.45],
          [v.target, v.by, v.note].join('\n'),
          'small',
          [f + '.target', f + '.by', f + '.note'],
        )
      })
    }
    const [x, y, w, h] = r.governance
    box('Governance', [x, y, w, h], 'deep')
    tx(
      'GovernanceTitle',
      [x + pad, y + 0.08, w - pad * 2, 0.3],
      d.governance.title,
      'label',
      'governance.title',
      { color: 'paper', bold: true, alignment: 'center' },
    )
    const gf = grid(
      [x + pad, y + 0.46, w - pad * 2, h - 0.52],
      d.governance.items.length,
      d.governance.items.length,
    )
    d.governance.items.forEach((v, i) => {
      const f = `governance.items[${i}]`
      tx(
        'GovernanceItem' + i,
        gf[i],
        [v.label, v.value, v.note].join('\n'),
        'small',
        ['label', 'value', 'note'].map((k) => f + '.' + k),
        { color: 'paper', alignment: vertical ? 'left' : 'center' },
      )
    })
  } else throw Error(`Unknown Mck role ${family.role}`)
  if (d.source) {
    tx(
      'Source',
      b.chrome.source,
      d.source + (family.role === 'profile' ? ' · ' + d.unit : ''),
      'source',
      family.role === 'profile' ? ['source', 'unit'] : 'source',
    )
  }
  if (d.confidentiality) {
    tx(
      'Confidentiality',
      b.chrome.confidentiality,
      d.confidentiality,
      'source',
      'confidentiality',
      { alignment: 'right' },
    )
  }
  line('FooterRule', 0.45, 6.91, 12.43)
  return cs
}

export function resolveMckDeck(design, content) {
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const f = design.mck.families[slide.type]
    if (!f) throw Error(`slides[${s}]: unregistered McKinsey role ${slide.type}`)
    const schema = JSON.parse(
      readFileSync(new URL(`./schemas/${slide.type}.schema.json`, import.meta.url)),
    )
    assertDesignValue(slide.data, schema, schema, `slides[${s}].data`)
    if (f.role === 'matrix' && slide.data.legend.length !== slide.data.bubbles.length) {
      throw Error(`slides[${s}]: one legend entry per bubble required`)
    }
    if (slide.customOps) throw Error(`slides[${s}]: customOps are not supported`)
    if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
    const failures = [],
      candidates = Object.entries(f.variants).flatMap(([layoutId, v]) => {
        try {
          const components = compileMckLayout(
            design,
            f,
            layoutId,
            v,
            slide.data,
            `slides[${s}].data`,
          )
          components.push({
            ...fitMckText(
              `${s + 1} / ${content.slides.length}`,
              design.mck.chrome.page,
              {
                ...design.mck.styles.source,
                alignment: 'right',
              },
              'structural.page',
            ),
            name: 'PageNum',
          })
          for (const c of components) {
            const [x, y, w, h] = c.frame
            if (
              x < 0 ||
              y < 0 ||
              w <= 0 ||
              h <= 0 ||
              x + w > design.canvas.widthIn + 0.001 ||
              y + h > design.canvas.heightIn + 0.001
            )
              throw Error(`${c.name}: exceeds canvas`)
          }
          return [
            {
              layoutId,
              role: f.role,
              components,
              fingerprint: designHash({
                role: f.role,
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
        design.mck.rhythm.maxConsecutive,
      )
    } catch (e) {
      throw Error(`slides[${s}]: ${e.message}; ${failures.join('; ')}`)
    }
    Object.assign(chosen, {
      candidates: candidates.map((c) => c.layoutId),
      slideIndex: s,
      slideType: slide.type,
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    layouts.push(chosen)
    if (chosen.repeated) warnings.push(`slides[${s}]: repeated composition`)
  }
  return { layouts, warnings }
}
