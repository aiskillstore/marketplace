// Bounded dark strategy compositions. Content is never inferred from the skin.
import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'

export function resolveStrategyDeck(design, content) {
  const e = design.strategy,
    layouts = [],
    warnings = []
  const fits = (v, w, h, pt = e.typography.body) =>
    String(v)
      .split('\n')
      .reduce(
        (n, line) =>
          n + Math.max(1, Math.ceil(textUnits(line) / Math.max(1, ((w - 0.12) * 72) / pt))),
        0,
      ) *
      pt *
      1.32 <=
    h * 72
  for (const [slideIndex, slide] of content.slides.entries()) {
    const family = e.families[slide.type],
      d = slide.data
    if (!family) throw Error(`Unregistered strategy family: ${slide.type}`)
    for (const k of ['title', 'label', 'source', 'asOf'])
      if (typeof d[k] !== 'string' || !d[k].trim()) throw Error(`${k} is required`)
    if (textUnits(d.title) > e.limits.titleUnits)
      throw Error('Title exceeds capacity; split or rewrite')
    if (textUnits(`${d.source} · ${d.asOf}`) > e.limits.footerUnits)
      throw Error('Source metadata exceeds capacity')
    if (
      d.verdict &&
      !fits(d.verdict, e.chrome.verdict[2] - 0.22, e.chrome.verdict[3], e.typography.body)
    )
      throw Error('Verdict exceeds capacity')
    const charts = [d.chart, d.investment].filter(Boolean)
    for (const ch of charts) {
      if (!ch.unit?.trim() || !ch.name?.trim()) throw Error('Chart name and unit are required')
      if (!Array.isArray(ch.categories) || ch.categories.length < 2 || ch.categories.length > 8)
        throw Error('Chart requires 2..8 categories')
      if (!ch.series?.length || ch.series.length > 3) throw Error('Chart requires 1..3 series')
      for (const series of ch.series)
        if (
          !series.name?.trim() ||
          series.values.length !== ch.categories.length ||
          series.values.some((v) => typeof v !== 'number' || !Number.isFinite(v))
        )
          throw Error('Chart series require names, matching categories and finite values')
    }
    if (family.role === 'range') {
      const range = d.range
      if (
        !range.unit?.trim() ||
        range.low.length !== range.high.length ||
        range.low.length !== range.categories.length ||
        range.low.some(
          (v, i) =>
            !Number.isFinite(v) || !Number.isFinite(range.high[i]) || v < 0 || v > range.high[i],
        )
      )
        throw Error('Ranges require matching finite 0 <= low <= high')
    }
    if (family.role === 'matrix') {
      const n = d.columns.length
      if (n < 3 || n > 6 || d.rows.length < 3 || d.rows.length > 6)
        throw Error('Matrix capacity is 3..6 columns and rows')
      if (d.rows.some((row) => row.cells.length !== n))
        throw Error('Every row must match the column count')
      if (d.columns.some((col) => !Number.isFinite(col.weight) || col.weight <= 0))
        throw Error('Column weights must be positive')
      if (d.rows.some((row) => row.cells.some((cell) => /[\r\n]/.test(cell.text))))
        throw Error('Matrix cells require one authored paragraph')
    }
    if (family.role === 'roadmap') {
      if (d.phases.some((p) => !Number.isFinite(p.duration) || p.duration <= 0))
        throw Error('Phase durations must be positive and finite')
      if (d.tracks.some((track) => track.activities.length !== d.phases.length))
        throw Error('Each track needs one activity per phase')
    }
    const items =
      d.rows?.length ?? d.range?.categories.length ?? d.steps?.length ?? d.phases?.length ?? 3
    const candidates = Object.entries(family.variants)
      .filter(([id, l]) => {
        if (items > l.maxItems) return false
        const r = l.regions
        if (family.role === 'matrix') {
          const total = d.columns.reduce((sum, c) => sum + c.weight, 0),
            rowH = r.main[3] / (d.rows.length + 1)
          if (
            !d.columns.every((c) =>
              fits(
                c.heading,
                (r.main[2] * c.weight) / total - 0.1,
                rowH - 0.12,
                e.typography.label,
              ),
            )
          )
            return false
          if (
            !d.rows.every((row) =>
              row.cells.every((cell, j) =>
                fits(cell.text, (r.main[2] * d.columns[j].weight) / total - 0.1, rowH - 0.14),
              ),
            )
          )
            return false
        }
        if (
          family.role === 'range' &&
          d.range.categories.some((v) => !fits(v, r.main[2] * 0.29, 0.45, e.typography.label))
        )
          return false
        if (d.notes) {
          const horizontal = family.role === 'range' && id === 'wide'
          const nw = horizontal
            ? (r.side[2] - 0.32 * (d.notes.length - 1)) / d.notes.length
            : r.side[2]
          if (
            !d.notes.every(
              (n) =>
                fits(n.heading, nw, horizontal ? 0.3 : 0.46) &&
                fits(n.body, nw, horizontal ? r.side[3] - 0.36 : r.side[3] / d.notes.length - 0.62),
            )
          )
            return false
        }
        if (family.role === 'range') {
          const value = d.range.categories
            .map((v, i) => `${v}: ${d.range.low[i]}–${d.range.high[i]}${d.range.unit}`)
            .join('  ·  ')
          if (!fits(value, r.main[2], id === 'wide' ? 0.25 : 0.55, e.typography.label)) return false
        }
        if (family.role === 'flow') {
          const horizontal = id === 'horizontal',
            stepW = horizontal
              ? (r.main[2] - 0.24 * (d.steps.length - 1)) / d.steps.length
              : r.main[2] - 0.72
          const stepH = horizontal ? r.main[3] - 0.9 : r.main[3] / d.steps.length
          if (!d.steps.every((n) => fits(n.heading, stepW, 0.65) && fits(n.body, stepW, stepH - 1)))
            return false
        }
        if (family.role === 'roadmap') {
          const total = d.phases.reduce((sum, p) => sum + p.duration, 0),
            w = r.main[2] - 1.22
          if (
            !d.phases.every(
              (p) =>
                fits(p.label, (w * p.duration) / total - 0.24, 0.5) &&
                fits(
                  p.gate,
                  (w * p.duration) / total - 0.24,
                  e.roadmap.gateHeight,
                  e.typography.label,
                ),
            )
          )
            return false
          const rowH =
            (r.main[3] - e.roadmap.gateHeight - e.roadmap.gateGap - e.roadmap.trackTop) /
            d.tracks.length
          if (
            !d.tracks.every((track) =>
              track.activities.every((v, j) =>
                fits(v, (w * d.phases[j].duration) / total - 0.24, Math.min(0.56, rowH - 0.12)),
              ),
            )
          )
            return false
        }
        return true
      })
      .map(([layoutId, frame]) => ({
        layoutId,
        frame,
        fingerprint: designHash({
          role: family.role,
          regions: frame.regions,
          typography: e.typography,
        }),
      }))
    const chosen = selectDesignLayout(
      candidates,
      slide.layoutId ?? 'auto',
      layouts,
      e.maxConsecutive,
    )
    layouts.push({
      ...chosen,
      slideIndex,
      role: family.role,
      candidates: candidates.map((c) => c.layoutId),
      reason: slide.layoutId && slide.layoutId !== 'auto' ? 'explicit' : 'fit-and-rhythm',
    })
    if (chosen.repeated && candidates.length > 1)
      warnings.push(`Slide ${slideIndex + 1}: repeated layout has alternatives`)
  }
  return { layouts, warnings }
}
