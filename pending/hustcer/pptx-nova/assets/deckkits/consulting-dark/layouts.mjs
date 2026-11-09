import { readFileSync } from 'node:fs'
import { assertDesignValue, designHash, selectDesignLayout } from '../shared/design-contract.mjs'
import { wrapCjkText } from '../shared/design-text.mjs'

// Conservative instance capacity; rendering and visual review remain separate gates.
export function fitConsultingText(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const capacity = ((frame[2] - 0.04) * 72) / style.sizePt
  const text = wrapCjkText(value, capacity * 0.92)
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
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines need ${requiredHeight.toFixed(2)}in; available ${frame[3].toFixed(2)}in`,
    )
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

export function compileConsultingLayout(design, family, layoutId, variant, d, path = 'data') {
  const b = design.consulting,
    r = variant.regions,
    cs = [],
    gap = b.spacing.gap
  const tx = (name, f, v, key = 'body', fields = name, extra = {}) => {
    if (v === undefined) return
    const st = { ...b.styles[key], ...extra }
    const paths = (Array.isArray(fields) ? fields : [fields]).map((k) => path + '.' + k)
    const c = { ...fitConsultingText(v, f, st, paths[0]), name, paths, allocatedFrame: [...f] }
    c.frame[3] = c.requiredHeight
    cs.push(c)
    return c
  }
  const box = (name, frame, color) => cs.push({ kind: 'box', name, frame, color })
  const circle = (name, frame, color) => cs.push({ kind: 'circle', name, frame, color })
  const inset = ([x, y, w, h], p = b.spacing.inset) => [x + p, y + p, w - p * 2, h - p * 2]
  const rule = (name, x, y, w, vertical = false) =>
    box(name, vertical ? [x, y, 0.008, w] : [x, y, w, 0.008], 'darkRule')
  const grid = (f, n, cols = n, g = gap) => {
    const rows = Math.ceil(n / cols),
      w = (f[2] - g * (cols - 1)) / cols,
      h = (f[3] - g * (rows - 1)) / rows
    return Array.from({ length: n }, (_, i) => [
      f[0] + (i % cols) * (w + g),
      f[1] + Math.floor(i / cols) * (h + g),
      w,
      h,
    ])
  }
  const list = (name, f, values, field, key = 'body') => {
    const step = f[3] / values.length
    const frames = values.map((_, i) => [f[0], f[1] + i * step, f[2], step - 0.04])
    values.forEach((v, i) => tx(name + i, frames[i], v, key, `${field}[${i}]`))
  }
  const metric = (name, f, v, field, compact = false, horizontal = false) => {
    const [x, y, w, h] = f
    tx(
      name + 'Value',
      [x, y, horizontal ? Math.min(w * 0.4, 1.5) : w, compact ? 0.65 : 0.9],
      v.value,
      compact ? 'compactMetric' : 'metric',
      field + '.value',
    )
    const lx = horizontal ? x + Math.min(w * 0.4, 1.5) + 0.2 : x,
      ly = horizontal ? y + 0.02 : y + (compact ? 0.68 : 0.94),
      lw = horizontal ? w - Math.min(w * 0.4, 1.5) - 0.2 : w
    if (horizontal && v.note !== undefined) {
      const caption = tx(
        name + 'Caption',
        [lx, ly, lw, h - (ly - y)],
        v.label + '\n' + v.note,
        'small',
        [field + '.label', field + '.note'],
      )
      caption.paragraphStyles = [{ bold: true, color: 'paper' }, {}]
      return
    }
    tx(name + 'Label', [lx, ly, lw, 0.43], v.label, 'small', field + '.label', {
      bold: true,
      color: 'paper',
    })
    tx(name + 'Note', [lx, ly + 0.32, lw, h - (ly - y) - 0.32], v.note, 'small', field + '.note')
  }
  const capability = (f, title, left, right, prefix, merge = false) => {
    const [x, y, w, h] = f
    rule('CapabilitiesRule', x, y, w)
    tx(
      'CapabilitiesTitle',
      [x + 0.24, y + 0.16, w - 0.48, 0.4],
      title,
      'heading',
      prefix + 'Header',
      { color: 'tealLight' },
    )
    const cols = grid([x + 0.24, y + 0.71, w - 0.48, h - 0.8], 2)
    if (merge) {
      tx(
        'CapabilityLeft',
        cols[0],
        left.join('\n'),
        'small',
        left.map((_, i) => `${prefix}Left[${i}]`),
      )
      tx(
        'CapabilityRight',
        cols[1],
        right.join('\n'),
        'small',
        right.map((_, i) => `${prefix}Right[${i}]`),
      )
      return
    }
    list('CapabilityLeft', cols[0], left, prefix + 'Left', 'reading')
    list('CapabilityRight', cols[1], right, prefix + 'Right', 'reading')
  }
  // Anchor circles retain the old atmosphere without occupying live text or footer zones.
  if (['cover', 'decision'].includes(family.role)) {
    for (const [i, f] of [
      [12.6, 1.45, 0.46, 0.46],
      [10.65, 0.9, 0.24, 0.24],
      [0.25, 5.9, 0.42, 0.42],
      [12.6, 5.7, 0.58, 0.58],
      [12.83, 3.85, 0.14, 0.14],
      [0.35, 1.1, 0.12, 0.12],
      [11.75, 0.42, 0.13, 0.13],
    ].entries())
      circle('AnchorOrb' + i, f, i === 5 || i === 6 ? 'primary' : 'deep')
  }
  if (family.role !== 'cover' && family.role !== 'decision') {
    tx('Eyebrow', b.chrome.eyebrow, d.eyebrow, 'label', 'eyebrow')
    tx('Title', b.chrome.title, d.title, 'title', 'title')
  }
  if (family.role === 'cover') {
    const [x, y, w] = r.main,
      [dx, dy, dw, dh] = r.detail,
      stack = layoutId === 'stacked'
    tx('Eyebrow', [x, 0.65, w, 0.3], d.eyebrow, 'label', 'eyebrow')
    tx('Title', [x, y, w, stack ? 2.2 : 2.9], d.title, 'hero', 'title')
    tx('Sub', [x, y + (stack ? 2.4 : 3.1), w, stack ? 0.9 : 1.1], d.sub, 'subtitle', 'sub')
    if (!stack) rule('CoverDivider', dx - 0.38, dy, dh, true)
    tx('CoverSummary', [dx, dy, dw, stack ? 0.42 : 1.8], d.tag, 'small', 'tag')
    tx(
      'InfoL',
      [dx, dy + (stack ? 0.55 : 2.45), stack ? dw * 0.55 : dw, 0.65],
      d.infoL,
      'small',
      'infoL',
    )
    tx(
      'InfoR',
      stack ? [dx + dw * 0.6, dy + 0.55, dw * 0.4, 0.65] : [dx, dy + 3.2, dw, 0.65],
      d.infoR,
      'small',
      'infoR',
    )
  } else if (family.role === 'profile') {
    const band = layoutId === 'bands',
      frames = grid(r.history, d.rows.length, band ? d.rows.length : 1)
    d.rows.forEach((v, i) => {
      const [x, y, w, h] = frames[i],
        p = `rows[${i}]`
      rule('HistoryRule' + i, x, y, w)
      circle('HistoryNode' + i, [x + 1.62, y + 0.2, 0.12, 0.12], 'warm')
      tx('Period' + i, [x, y + 0.17, band ? w : 1.6, 0.4], v.period, 'label', p + '.period')
      tx(
        'Organisation' + i,
        band ? [x, y + 0.7, w, 0.8] : [x + 1.9, y + 0.1, w - 1.9, 0.4],
        v.organisation,
        'heading',
        p + '.organisation',
      )
      tx(
        'Role' + i,
        band ? [x, y + 1.6, w, h - 1.6] : [x + 1.9, y + 0.55, w - 1.9, h - 0.55],
        v.role,
        'small',
        p + '.role',
      )
    })
    grid(r.metrics, d.metrics.length, band ? d.metrics.length : 1, gap).forEach((f, i) => {
      rule('ProfileMetricRule' + i, f[0], f[1], f[2])
      metric('ProfileMetric' + i, inset(f, 0.16), d.metrics[i], `metrics[${i}]`, true, true)
    })
  } else if (family.role === 'achievements') {
    const rows = layoutId === 'ledger',
      frames = grid(r.items, d.items.length, rows ? 1 : Math.min(2, d.items.length))
    frames.forEach(([x, y, w, h], i) => {
      const v = d.items[i],
        p = `items[${i}]`
      rule('AchievementRule' + i, x, y, w)
      tx('AchievementIndex' + i, [x, y + 0.2, 0.45, 0.4], v.index, 'label', p + '.index')
      tx(
        'AchievementTitle' + i,
        [x + 0.65, y + 0.2, rows ? 3.5 : w - 2.8, 0.75],
        v.title,
        'heading',
        p + '.title',
      )
      tx(
        'AchievementBadge' + i,
        [x + w - 1.9, y + 0.12, 1.9, 0.85],
        v.badge,
        'proofMetric',
        p + '.badge',
        { alignment: 'right' },
      )
      tx(
        'AchievementBody' + i,
        rows ? [x + 4.65, y + 0.17, w - 6.85, h - 0.2] : [x + 0.65, y + 1.12, w - 0.65, h - 1.15],
        v.body,
        'body',
        p + '.body',
      )
    })
  } else if (family.role === 'product') {
    tx('Banner', r.banner, d.banner, 'body', 'banner')
    const rail = layoutId === 'rail',
      fs = grid(r.metrics, d.kpis.length, rail ? 1 : d.kpis.length, 0.14)
    fs.forEach((f, i) => {
      rule('KpiRule' + i, f[0], f[1], f[2])
      metric('Kpi' + i, inset(f, rail ? 0.12 : 0.18), d.kpis[i], `kpis[${i}]`, rail, rail)
    })
    capability(r.capabilities, d.capHeader, d.capLeft, d.capRight, 'cap')
  } else if (family.role === 'landscape') {
    const [x, y, w, h] = r.position,
      rows = layoutId === 'ledger'
    box('PositionSurface', [x - 0.18, y - 0.14, w + 0.36, h + 0.28], 'deep')
    tx('PositionLabel', [x, y, w, 0.3], d.usLabel, 'label', 'usLabel')
    tx('PositionTitle', [x, y + 0.4, w, rows ? 1.6 : 0.4], d.usTitle, 'heading', 'usTitle')
    tx(
      'PositionSub',
      [x, y + (rows ? 2.3 : 0.91), w, rows ? h - 2.3 : 0.35],
      d.usSub,
      'small',
      'usSub',
    )
    for (const c of cs.filter((c) => c.name.startsWith('Position')))
      if (c.style)
        c.style.color =
          c.name === 'PositionLabel' ? 'warm' : c.name === 'PositionTitle' ? 'paper' : 'pale'
    grid(r.competitors, d.comps.length, rows ? 1 : d.comps.length).forEach(
      ([cx, cy, cw, ch], i) => {
        const v = d.comps[i],
          p = `comps[${i}]`
        rule('ComparisonRule' + i, cx, cy, cw)
        tx(
          'Competitor' + i,
          [cx, cy + 0.16, rows ? 2.2 : cw, rows ? 0.45 : 0.5],
          v.name,
          'heading',
          p + '.name',
        )
        tx(
          'CompetitorTag' + i,
          [cx, cy + (rows ? 0.68 : 0.73), rows ? 2.2 : cw, 0.3],
          v.tag,
          'label',
          p + '.tag',
        )
        tx(
          'Strength' + i,
          rows ? [cx + 2.6, cy + 0.16, 2.3, ch - 0.2] : [cx, cy + 1.17, cw, 0.65],
          v.strength,
          'small',
          p + '.strength',
          { sizePt: 13 },
        )
        tx(
          'Limitation' + i,
          rows ? [cx + 5.1, cy + 0.16, cw - 5.1, ch - 0.2] : [cx, cy + 1.78, cw, ch - 1.78],
          v.limitation,
          'small',
          p + '.limitation',
          { sizePt: 13 },
        )
      },
    )
    tx('Conclusion', r.conclusion, d.conclusion, 'body', 'conclusion', {
      bold: true,
      color: 'warm',
    })
  } else if (family.role === 'audiences') {
    tx('Intro', r.intro, d.intro, 'body', 'intro')
    const rows = layoutId === 'ledger'
    grid(r.items, d.cards.length, rows ? 1 : d.cards.length, rows ? 0.14 : gap).forEach(
      ([x, y, w, h], i) => {
        const v = d.cards[i],
          p = `cards[${i}]`
        rule('AudienceRule' + i, x, y, w)
        tx('AudienceIndex' + i, [x, y + 0.08, 0.6, 0.6], v.index, 'index', p + '.index')
        tx(
          'AudienceName' + i,
          rows ? [x + 0.9, y + 0.1, 2.8, h - 0.15] : [x, y + 1.0, w, 0.8],
          v.name,
          'heading',
          p + '.name',
        )
        if (rows)
          tx(
            'AudienceItems' + i,
            [x + 4, y + 0.1, w - 4, h - 0.15],
            v.items.join(' · '),
            'small',
            v.items.map((_, j) => p + `.items[${j}]`),
          )
        else
          list('AudienceItem' + i + '_', [x, y + 2.0, w, h - 2.0], v.items, p + '.items', 'reading')
      },
    )
  } else if (family.role === 'flow') {
    const [x, y, w, h] = r.flow,
      vertical = layoutId === 'vertical'
    const src = vertical ? [x, y, 2.2, 1.05] : [x, y + 0.2, 2.05, 1.9],
      eng = vertical ? [x + 3, y, 3, 1.3] : [x + 3.0, y + 0.2, 3, 1.9],
      out = vertical ? [x, y + 2.2, w, h - 2.2] : [x + 7.25, y, w - 7.25, h]
    rule('SourceRule', src[0], src[1] - 0.14, src[2])
    box('EngineSurface', [eng[0] - 0.14, eng[1] - 0.14, eng[2] + 0.28, 1.95], 'primary')
    tx('SourceLabel', [src[0], src[1], src[2], 0.6], d.srcLabel, 'index', 'srcLabel')
    tx('SourceDetail', [src[0], src[1] + 0.8, src[2], 0.9], d.srcSub, 'body', 'srcSub')
    tx('EngineTitle', [eng[0], eng[1], eng[2], 0.8], d.engTitle, 'heading', 'engTitle')
    tx('EngineDetail', [eng[0], eng[1] + 0.8, eng[2], 1.2], d.engSub, 'body', 'engSub')
    for (const c of cs.filter((c) => ['EngineTitle', 'EngineDetail'].includes(c.name)))
      c.style.color = 'paper'
    // A shared connector is derived from the two content frames, not attached decoration.
    cs.push({
      kind: 'arrow',
      name: 'FlowConnector',
      frame: [src[0] + src[2] + 0.2, y + 0.35, eng[0] - (src[0] + src[2]) - 0.4, 0.16],
      color: 'warm',
    })
    if (vertical) {
      cs.push({
        kind: 'arrow',
        name: 'OutputConnector',
        direction: 'down',
        frame: [eng[0] + eng[2] / 2 - 0.08, eng[1] + 1.65, 0.16, out[1] - eng[1] - 1.8],
        color: 'warm',
      })
    }
    grid(out, d.outputs.length, 2).forEach(([ox, oy, ow, oh], i) => {
      const v = d.outputs[i],
        p = `outputs[${i}]`
      box('OutputSurface' + i, [ox - 0.1, oy + 0.04, ow + 0.2, oh - 0.08], 'deep')
      const heading = fitConsultingText(
        v.title,
        [ox, oy, ow, 0.45],
        b.styles.heading,
        path + '.' + p + '.title',
      )
      const caption = tx(
        'Output' + i,
        [ox, oy + 0.2, ow, oh - 0.2],
        v.title + '\n' + v.description,
        'small',
        [p + '.title', p + '.description'],
      )
      const extra =
        (heading.estimatedLines * (b.styles.heading.sizePt - b.styles.small.sizePt) * 1.5) / 72
      caption.requiredHeight += extra
      if (caption.requiredHeight > caption.allocatedFrame[3])
        throw Error(`${path}.${p}: output caption exceeds height`)
      caption.frame[3] = caption.requiredHeight
      caption.paragraphStyles = [{ ...b.styles.heading, color: 'tealLight' }, {}]
      caption.owner = 'OutputSurface' + i
      caption.ownerMargins = {
        marginLeft: '0.1in',
        marginRight: '0.1in',
        marginTop: '0.16in',
        marginBottom: '0.04in',
      }
    })
    {
      // Bind the group to actual output-node bounds, and draw above their fills.
      const nodes = cs.filter((c) => c.kind === 'box' && c.name.startsWith('OutputSurface')),
        groupLeft = Math.min(...nodes.map((c) => c.frame[0])) - 0.02,
        groupRight = Math.max(...nodes.map((c) => c.frame[0] + c.frame[2])) + 0.02,
        groupTop = Math.min(...nodes.map((c) => c.frame[1])),
        groupBottom = Math.max(...nodes.map((c) => c.frame[1] + c.frame[3])),
        engineRight = eng[0] + eng[2] + 0.14,
        engineCenterY = eng[1] - 0.14 + 1.95 / 2
      box('OutputGroupBracket', [groupLeft, groupTop, 0.012, groupBottom - groupTop], 'tealLight')
      box('OutputGroupTop', [groupLeft, groupTop, groupRight - groupLeft, 0.012], 'tealLight')
      box(
        vertical ? 'OutputGroupRight' : 'OutputGroupBottom',
        vertical
          ? [groupRight - 0.012, groupTop, 0.012, groupBottom - groupTop]
          : [groupLeft, groupBottom - 0.012, groupRight - groupLeft, 0.012],
        'tealLight',
      )
      if (!vertical)
        cs.push({
          kind: 'arrow',
          name: 'OutputConnector',
          frame: [engineRight + 0.05, engineCenterY - 0.07, groupLeft - engineRight - 0.05, 0.14],
          color: 'warm',
        })
    }
    capability(r.capabilities, d.featHeader, d.featLeft, d.featRight, 'feat', vertical)
  } else if (family.role === 'benchmark') {
    const rows = d.tableRows,
      cols = rows[0].length
    if (rows.some((row) => row.length !== cols))
      throw Error(`${path}.tableRows: rectangular table required`)
    const [x, y, w, h] = r.table,
      widths = Array.from({ length: cols }, (_, i) => w * (i === 0 ? 0.31 : 0.69 / (cols - 1))),
      rh = h / rows.length
    const bindings = []
    rows.forEach((row, i) => {
      let xx = x
      row.forEach((v, j) => {
        const f = [xx + 0.1, y + i * rh + 0.06, widths[j] - 0.2, rh - 0.12]
        if (v.length > b.table.maxCellChars)
          throw Error(`${path}.tableRows[${i}][${j}]: cell exceeds character capacity`)
        fitConsultingText(v, f, b.styles.small, `${path}.tableRows[${i}][${j}]`)
        bindings.push({ frame: f, paths: [`${path}.tableRows[${i}][${j}]`] })
        xx += widths[j]
      })
    })
    cs.push({
      kind: 'table',
      name: 'BenchmarkTable',
      frame: r.table,
      cells: rows,
      widths,
      rowHeights: rows.map(() => rh),
      bindings,
    })
    const data = d.chartData,
      values = data.series[0].values
    if (data.categories.length !== values.length)
      throw Error(`${path}.chartData: categories and values differ`)
    data.categories.forEach((v, i) =>
      fitConsultingText(
        v,
        [0, 0, r.chart[2] * 0.4, r.chart[3] / values.length],
        { ...b.styles.small, sizePt: b.chart.fontPt },
        `${path}.chartData.categories[${i}]`,
      ),
    )
    tx(
      'ChartTitle',
      [r.chart[0], r.chart[1] - 0.45, r.chart[2], 0.4],
      d.chartTitle,
      'small',
      'chartTitle',
      { bold: true, color: 'paper' },
    )
    tx(
      'ChartUnit',
      [r.chart[0], r.chart[1] + r.chart[3] + 0.1, r.chart[2], 0.5],
      d.unit + ' · ' + data.series[0].name,
      'source',
      ['unit', 'chartData.series[0].name'],
    )
    cs.push({
      kind: 'chart',
      name: 'BenchmarkChart',
      frame: r.chart,
      data,
      inputPaths: data.categories.map((_, i) => `${path}.chartData.categories[${i}]`),
    })
    metric(
      'Callout',
      r.callout,
      { value: d.calloutNum, label: d.calloutText, note: undefined },
      'callout',
      true,
    )
    cs.find((c) => c.name === 'CalloutValue').paths = [path + '.calloutNum']
    cs.find((c) => c.name === 'CalloutLabel').paths = [path + '.calloutText']
  } else if (family.role === 'roadmap') {
    const rows = layoutId === 'ledger',
      fs = grid(r.steps, d.steps.length, rows ? 1 : d.steps.length)
    if (!rows) rule('Timeline', r.steps[0], r.steps[1] + 1.03, r.steps[2])
    fs.forEach(([x, y, w, h], i) => {
      const v = d.steps[i],
        p = `steps[${i}]`
      if (rows) rule('StepRule' + i, x, y, w)
      if (!rows) {
        circle('PhaseNode' + i, [x + w / 2 - 0.065, y + 0.97, 0.13, 0.13], 'warm')
      }
      tx('StepIndex' + i, [x, y + 0.12, 0.7, 0.6], v.index, 'index', p + '.index')
      tx(
        'StepTitle' + i,
        rows ? [x + 1.0, y + 0.14, 2.4, h - 0.2] : [x, y + 1.4, w, 0.7],
        v.title,
        'heading',
        p + '.title',
      )
      tx(
        'StepDescription' + i,
        rows ? [x + 3.7, y + 0.14, w - 6.4, h - 0.2] : [x, y + 2.3, w, h - 2.3],
        v.description,
        'body',
        p + '.description',
      )
      tx(
        'StepStatus' + i,
        rows ? [x + w - 2.3, y + 0.14, 2.3, h - 0.2] : [x, y + 0.73, w, 0.3],
        v.status,
        'label',
        p + '.status',
      )
    })
  } else if (family.role === 'decision') {
    const [x, y, w, h] = r.intro,
      rows = layoutId === 'rows'
    tx('Eyebrow', [0.8, 0.6, 11.7, 0.3], d.eyebrow, 'label', 'eyebrow')
    tx('Title', [x, y, w, rows ? 2.9 : 2.0], d.title, rows ? 'title' : 'hero', 'title', {
      color: 'paper',
    })
    tx('Sub', [x, y + (rows ? 3.1 : 2.15), w, rows ? h - 3.1 : 0.7], d.sub, 'subtitle', 'sub')
    grid(r.items, d.asks.length, rows ? 1 : d.asks.length).forEach(([cx, cy, cw, ch], i) => {
      const v = d.asks[i],
        p = `asks[${i}]`
      rule('AskRule' + i, cx, cy, cw)
      tx(
        'AskTitle' + i,
        [cx, cy + 0.18, rows ? 2.5 : cw, rows ? ch - 0.2 : 0.75],
        v.title,
        'heading',
        p + '.title',
      )
      tx(
        'AskDescription' + i,
        rows ? [cx + 2.9, cy + 0.18, cw - 2.9, ch - 0.2] : [cx, cy + 1.1, cw, ch - 1.12],
        v.description,
        'body',
        p + '.description',
      )
    })
    tx('Closing', [r.closing[0], r.closing[1], 5.4, r.closing[3]], d.closing, 'source', 'closing')
    tx('ClosingRight', [6.7, r.closing[1], 5.8, r.closing[3]], d.closingR, 'source', 'closingR', {
      alignment: 'right',
    })
  } else throw Error(`Unknown Consulting role ${family.role}`)
  tx('Source', b.chrome.source, d.source, 'source', 'source')
  return cs
}

export function resolveConsultingDeck(design, content) {
  if (content.meta?.deckkit !== design.id) throw Error('Content DeckKit identity mismatch')
  const layouts = [],
    warnings = []
  for (const [s, slide] of content.slides.entries()) {
    const family = design.consulting.families[slide.type]
    if (!family) throw Error(`slides[${s}]: unregistered Consulting role ${slide.type}`)
    if (slide.customOps) throw Error(`slides[${s}]: customOps are not supported`)
    const schema = JSON.parse(
      readFileSync(new URL(`./schemas/${slide.type}.schema.json`, import.meta.url)),
    )
    assertDesignValue(slide.data, schema, schema, `slides[${s}].data`)
    const failures = []
    const candidates = Object.entries(family.variants).flatMap(([layoutId, v]) => {
      try {
        const components = compileConsultingLayout(
          design,
          family,
          layoutId,
          v,
          slide.data,
          `slides[${s}].data`,
        )
        components.push({
          ...fitConsultingText(
            `${s + 1} / ${content.slides.length}`,
            design.consulting.chrome.page,
            {
              ...design.consulting.styles.source,
              color: 'pale',
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
            throw Error(c.name + ': exceeds canvas')
        }
        return [
          {
            layoutId,
            role: family.role,
            mode: 'dark',
            components,
            fingerprint: designHash({
              role: family.role,
              frames: components.map((c) => [c.kind, c.frame]),
            }),
          },
        ]
      } catch (e) {
        failures.push(layoutId + ': ' + e.message)
        return []
      }
    })
    let chosen
    try {
      chosen = selectDesignLayout(
        candidates,
        slide.layoutId ?? 'auto',
        layouts,
        design.consulting.rhythm.maxConsecutive,
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
