import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'
export const annualNumber = (n) =>
  Math.abs(n) > 0 && Math.abs(n) < 1e-6
    ? String(n)
    : new Intl.NumberFormat('en-US', { maximumFractionDigits: 20 }).format(n)
export const annualChartLegend = (ch) =>
  ch.series
    .map((ss) =>
      ch.kind === 'line'
        ? `${ss.name} · ${ch.categories[0]} ${annualNumber(ss.values[0])} → ${ch.categories.at(-1)} ${annualNumber(ss.values.at(-1))}`
        : ss.name,
    )
    .join(' / ')
export function resolveAnnualDeck(design, content) {
  const a = design.annual,
    layouts = [],
    warnings = []
  const fits = (text, w, h, pt = a.typography.body) =>
    String(text)
      .split('\n')
      .reduce(
        (n, l) => n + Math.max(1, Math.ceil(textUnits(l) / Math.max(1, ((w - 0.1) * 72) / pt))),
        0,
      ) *
      pt *
      1.32 <=
    h * 72
  for (const [s, slide] of content.slides.entries()) {
    const f = a.families[slide.type],
      d = slide.data
    if (!f) throw Error('Unknown annual family')
    for (const k of ['title', 'basis', 'source', 'asOf', 'verdict'])
      if (!d[k]?.trim()) throw Error(`${k} is required`)
    if (
      textUnits(d.title) > a.limits.titleUnits ||
      (f.role !== 'cover' &&
        !fits(d.title, a.chrome.title[2], a.chrome.title[3], a.typography.title))
    )
      throw Error(`Slide ${s + 1}: title exceeds capacity`)
    if (textUnits(`${d.source} · ${d.asOf}`) > a.limits.footerUnits)
      throw Error('Source exceeds capacity')
    if (
      !fits(d.basis, 12, 0.33, a.typography.label) ||
      !fits(d.verdict, 12, 0.4, a.typography.label)
    )
      throw Error('Chrome exceeds capacity')
    for (const ch of d.charts ?? []) {
      if (!ch.name?.trim() || !ch.basis?.trim() || !ch.unit?.trim())
        throw Error('Chart name, basis and unit required')
      if (
        ch.categories.length < 2 ||
        ch.categories.length > 8 ||
        ch.series.length < 1 ||
        ch.series.length > 4
      )
        throw Error('Chart capacity exceeded')
      for (const series of ch.series)
        if (
          !series.name?.trim() ||
          series.values.length !== ch.categories.length ||
          series.values.some((v) => !Number.isFinite(v))
        )
          throw Error('Chart values must be finite and match categories')
      if (
        ['donut', 'circles'].includes(ch.kind) &&
        (ch.series.length !== 1 ||
          ch.series[0].values.some((v) => v < 0) ||
          !ch.series[0].values.some((v) => v > 0))
      )
        throw Error('Part/circle charts require one nonnegative nonzero series')
      if (ch.kind === 'circles' && ch.categories.length !== 2)
        throw Error('Circle comparison requires two values')
      if (ch.variant === 'stacked' && ch.kind !== 'bar' && ch.kind !== 'column')
        throw Error('Stacking requires bars')
      if (
        ch.focus !== undefined &&
        (!Number.isInteger(ch.focus) ||
          ch.focus < 0 ||
          ch.focus >= ch.categories.length ||
          !['bar', 'column', 'donut'].includes(ch.kind) ||
          ch.series.length !== 1)
      )
        throw Error('Focus requires an existing category in a single bar, column or ring series')
      if (
        ch.forecastFrom !== undefined &&
        (!Number.isInteger(ch.forecastFrom) ||
          ch.kind !== 'column' ||
          ch.series.length !== 1 ||
          ch.forecastFrom < 1 ||
          ch.forecastFrom >= ch.categories.length - 1)
      )
        throw Error('Forecast boundary must leave history and forecast segments')
    }
    if (d.columns) {
      if (
        d.columns.length < 2 ||
        d.columns.length > 7 ||
        d.rows.some((r) => r.cells.length !== d.columns.length) ||
        d.rows.some((r) => r.cells.some((c) => /[\r\n]/.test(c.text))) ||
        d.columns.some((c) => /[\r\n]/.test(c.heading)) ||
        d.columns.some((c) => !Number.isFinite(c.weight) || c.weight <= 0)
      )
        throw Error('Invalid matrix dimensions/weights')
    }
    if (d.phases?.some((p) => !Number.isFinite(p.duration) || p.duration <= 0))
      throw Error('Phase duration must be positive')
    const candidates = Object.entries(f.variants)
      .filter(([id, v]) => {
        const r = v.regions,
          n = d.charts?.length ?? 0
        if (f.role === 'evidence' && n !== Object.keys(r).filter((k) => /^chart/.test(k)).length)
          return false
        if (d.notes) {
          const vert = id === 'rail',
            nw = vert ? r.detail[2] : (r.detail[2] - 0.3 * (d.notes.length - 1)) / d.notes.length,
            nh = vert ? (r.detail[3] - 0.2 * (d.notes.length - 1)) / d.notes.length : r.detail[3]
          if (!d.notes.every((x) => fits(x.heading, nw, 0.3) && fits(x.body, nw, nh - 0.35)))
            return false
        }
        if (d.columns) {
          if (
            !fits(
              d.tableName,
              r.main[2],
              f.role === 'composite' ? 0.36 : 0.25,
              f.role === 'composite' ? a.typography.figure : a.typography.label,
            )
          )
            return false
          const w = d.columns.reduce((n, c) => n + c.weight, 0),
            rh = r.main[3] / (d.rows.length + 1)
          if (
            d.rows.length > v.maxItems ||
            !d.columns.every((c) =>
              fits(c.heading, (r.main[2] * c.weight) / w - 0.16, rh - 0.12, a.typography.label),
            ) ||
            !d.rows.every((row) =>
              row.cells.every((c, j) =>
                fits(c.text, (r.main[2] * d.columns[j].weight) / w - 0.16, rh - 0.13),
              ),
            )
          )
            return false
        }
        if (d.paragraphs) {
          const cols = id === 'split' ? 2 : 1,
            h = r.main[3] / Math.ceil(d.paragraphs.length / cols)
          if (
            !d.paragraphs.every(
              (x) => fits(x.heading, r.main[2], 0.34) && fits(x.body, r.main[2], h - 0.6),
            )
          )
            return false
        }
        if (d.note && !fits(d.note, r.detail[2], r.detail[3], a.typography.label)) return false
        if (d.items) {
          const rh = r.main[3] / d.items.length
          if (
            !d.items.every(
              (x) =>
                fits(x.heading, r.main[2] - 0.73, 0.34) &&
                fits(x.body, r.main[2] - 0.73, rh - 0.56),
            )
          )
            return false
        }
        if (d.side) {
          const rh = r.side[3] / d.side.length
          if (
            !d.side.every(
              (x) =>
                fits(x.value, r.side[2], 0.58, f.role === 'summary' ? a.typography.metric : 19) &&
                fits(x.label, r.side[2], rh - 0.8, a.typography.label),
            )
          )
            return false
        }
        if (d.metrics) {
          const w = r.metrics[2] / d.metrics.length - 0.25
          if (
            !fits(d.title, r.title[2], r.title[3], a.typography.cover) ||
            !fits(d.abstract, r.abstract[2], r.abstract[3], 18) ||
            !d.metrics.every(
              (x) =>
                fits(x.value, w, 0.56, a.typography.metric) &&
                fits(x.label, w, 0.3, a.typography.label) &&
                fits(x.detail, w, r.metrics[3] - 1, a.typography.source),
            )
          )
            return false
        }
        if (d.phases) {
          const total = d.phases.reduce((n, p) => n + p.duration, 0)
          if (
            !d.phases.every(
              (p) =>
                fits(p.label, (r.phases[2] * p.duration) / total - 0.16, 0.33) &&
                fits(p.detail, (r.phases[2] * p.duration) / total - 0.16, 0.4, a.typography.label),
            )
          )
            return false
        }
        for (const [i, ch] of (d.charts ?? []).entries()) {
          const frame = r[`chart${i}`]
          if (
            !frame ||
            !fits(ch.label, 0.52, 0.27, a.typography.label) ||
            !fits(ch.name, frame[2] - 0.58, 0.38, a.typography.figure) ||
            !fits(`${ch.basis} · ${ch.unit}`, frame[2], 0.25, a.typography.source) ||
            !fits(annualChartLegend(ch), frame[2], 0.2, a.typography.source)
          )
            return false
          const labelW = ch.kind === 'bar' ? frame[2] * 0.26 : frame[2] / ch.categories.length
          if (ch.categories.some((x) => !fits(x, labelW, 0.45, a.typography.label))) return false
        }
        return true
      })
      .map(([layoutId, frame]) => ({
        layoutId,
        frame,
        fingerprint: designHash({ role: f.role, regions: frame.regions, typography: a.typography }),
      }))
    const chosen = selectDesignLayout(
      candidates,
      slide.layoutId ?? 'auto',
      layouts,
      a.maxConsecutive,
    )
    layouts.push({
      ...chosen,
      slideIndex: s,
      role: f.role,
      candidates: candidates.map((x) => x.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    if (chosen.repeated && candidates.length > 1)
      warnings.push(`Slide ${s + 1}: repeated layout has alternatives`)
  }
  return { layouts, warnings }
}
