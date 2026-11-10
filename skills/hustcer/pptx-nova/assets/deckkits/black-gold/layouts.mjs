// Bounded editorial families. A design supplies geometry/identity, content supplies every claim.
import { designHash, selectDesignLayout, textUnits } from '../shared/design-contract.mjs'

export function resolveEditorialDeck(design, content) {
  const e = design.editorial
  const layouts = []
  const warnings = []
  const full =
    content.meta.designScope === 'complete' ||
    (content.meta.designScope !== 'excerpt' && content.slides.length >= e.rhythm.minFullDeck)
  const counts = { dark: 0, light: 0 }
  for (const [slideIndex, slide] of content.slides.entries()) {
    const family = e.families[slide.type]
    if (!family) throw new Error(`Unregistered editorial family ${slide.type}`)
    const d = slide.data
    for (const key of family.role === 'cover'
      ? ['title', 'source', 'asOf', 'unit']
      : ['title', 'basis', 'source', 'asOf', 'unit', 'verdict']) {
      if (typeof d[key] !== 'string' || !d[key].trim())
        throw new Error(`slides[${slideIndex}].${key} is required`)
    }
    for (const [key, limit] of [
      ['title', e.limits.titleUnits],
      ['basis', e.limits.basisUnits],
      ['source', e.limits.footerUnits],
    ]) {
      if (textUnits(d[key]) > limit)
        throw new Error(`${key} exceeds content capacity; reorganize or split`)
    }
    if (
      textUnits(`${d.source} · ${d.asOf} · ${d.unit}`) > e.limits.footerUnits ||
      (family.role !== 'cover' &&
        textUnits(`${d.basis} · ${d.asOf} · ${d.unit}`) > e.limits.basisUnits)
    )
      throw new Error('Composed source/basis metadata exceeds capacity')
    const charts = [
      d.chart,
      d.secondary && { ...d.secondary, categories: d.chart.categories },
      d.support,
    ].filter(Boolean)
    for (const chart of charts) {
      if (!['bar', 'column', 'line'].includes(chart.kind)) throw new Error('Unsupported chart kind')
      if (
        chart.values.length !== chart.categories.length ||
        chart.values.length < 2 ||
        chart.values.length > 8
      )
        throw new Error('Chart categories and values must have matching lengths of 2..8')
      if (chart.values.some((v) => typeof v !== 'number' || !Number.isFinite(v)))
        throw new Error('Chart requires finite numbers; missing values cannot become zero')
      if (
        chart.focus !== undefined &&
        (!Number.isInteger(chart.focus) || chart.focus < 0 || chart.focus >= chart.values.length)
      )
        throw new Error('Focus must address one existing observation')
    }
    if (d.secondary?.categories)
      throw new Error('Secondary trend shares primary categories; do not duplicate them')
    if (d.secondary?.focus !== undefined || d.support?.focus !== undefined)
      throw new Error('Only the primary evidence chart may carry the gold focus')
    if (family.role === 'ranking' && d.chart.kind !== 'bar')
      throw new Error('Ranking requires a horizontal bar chart')
    if (family.role === 'trend' && !['column', 'line'].includes(d.chart.kind))
      throw new Error('Trend requires ordered columns or a line')
    if (family.role === 'matrix') {
      if (
        d.rows.some(
          (r) =>
            !Number.isFinite(r.amount) || !Number.isFinite(r.share) || r.share < 0 || r.share > 100,
        )
      )
        throw new Error('Matrix amount must be finite and share must be 0..100')
      if (
        d.rows.some((r) => Object.values(r).some((v) => typeof v === 'string' && /[\r\n]/.test(v)))
      )
        throw new Error(
          'Matrix cells require one paragraph; use automatic wrapping within the row capacity',
        )
    }
    if (
      (d.metrics ?? []).filter((m) => m.focus).length > 1 ||
      (d.actions ?? []).filter((a) => a.focus).length > 1
    )
      throw new Error('Only one gold focus is allowed')
    if (d.chart?.focus !== undefined && d.metrics?.some((m) => m.focus))
      throw new Error('Chart and metric cannot both be gold focuses')
    for (const note of [...(d.notes ?? []), ...(d.judgments ?? [])]) {
      if (textUnits(note.body) > e.limits.bodyUnits)
        throw new Error('Explanation exceeds body capacity')
    }
    if (full) {
      if (family.role === 'cover' && slideIndex !== 0)
        throw new Error('Cover must be the first page')
      if (family.role === 'summary' && slideIndex !== 1)
        throw new Error('Summary must follow the cover')
      if (family.role === 'decision' && slideIndex !== content.slides.length - 1)
        throw new Error('Decision must close the deck')
    }
    counts[family.mode]++
    const items =
      d.chart?.values.length ?? d.rows?.length ?? d.actions?.length ?? d.judgments?.length ?? 3
    const maxLabel = Math.max(
      0,
      ...(d.chart?.categories ?? d.rows?.map((r) => r.name) ?? []).map(textUnits),
    )
    const fits = (value, width, height, size) =>
      String(value)
        .split('\n')
        .reduce(
          (n, line) => n + Math.max(1, Math.ceil(textUnits(line) / (((width - 0.04) * 72) / size))),
          0,
        ) *
        size *
        1.4 <=
      height * 72
    const candidates = Object.entries(family.variants)
      .filter(([id, l]) => {
        if (items > l.maxItems || maxLabel > l.maxLabelUnits) return false
        if (family.role === 'trend' && Boolean(l.regions.support) !== Boolean(d.support))
          return false
        if (d.secondary && (id !== 'wide' || d.support)) return false
        if (family.role === 'trend' && id === 'wide' && d.notes.length > 3) return false
        if (family.role === 'trend') {
          const [, , w, h] = l.regions.detail,
            vertical = id === 'rail'
          const nw = vertical ? w : (w - 0.3 * (d.notes.length - 1)) / d.notes.length
          const nh = vertical ? (h - 0.3 * (d.notes.length - 1)) / d.notes.length : h
          if (
            !d.notes.every(
              (n) =>
                fits(n.heading, nw, 0.38, e.typography.body) &&
                fits(n.body, nw, Math.max(0.52, nh - 0.45), e.typography.body),
            )
          )
            return false
        }
        if (family.role === 'matrix') {
          const [, , w, h] = l.regions.main,
            widths = [0.2, 0.12, 0.2, 0.23, 0.25].map((v) => v * w),
            rowH = h / (d.rows.length + 1)
          if (
            !d.rows.every((row) =>
              [row.name, String(row.amount), `${row.share}%`, row.representative, row.thesis].every(
                (v, j) => fits(v, widths[j] - 0.12, rowH - 0.12, e.typography.body),
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
          mode: family.mode,
          regions: frame.regions,
          typography: e.typography,
          secondary: Boolean(d.secondary),
        }),
      }))
    const chosen = selectDesignLayout(
      candidates,
      slide.layoutId ?? 'auto',
      layouts,
      e.rhythm.maxConsecutive,
    )
    layouts.push({
      ...chosen,
      slideIndex,
      role: family.role,
      mode: family.mode,
      candidates: candidates.map((c) => c.layoutId),
      reason:
        slide.layoutId && slide.layoutId !== 'auto'
          ? 'explicit'
          : chosen.repeated
            ? 'only-fitting-composition'
            : 'fit-and-rhythm',
    })
    if (chosen.repeated && candidates.length > 1)
      warnings.push(`Slide ${slideIndex + 1}: repeated composition has fitting alternatives`)
  }
  if (full) {
    const roles = layouts.map((l) => l.role)
    if (roles[0] !== 'cover' || roles[1] !== 'summary' || roles.at(-1) !== 'decision')
      throw new Error(
        'A full deck requires cover, summary and closing decision; use a short evidence excerpt when those roles are not intended',
      )
    if (Math.abs(counts.dark / content.slides.length - e.rhythm.darkTarget) > 0.15)
      warnings.push(
        'Dark-page proportion differs from the design preference; review narrative rhythm',
      )
  }
  return {
    layouts,
    warnings,
    rhythm: { counts, target: e.rhythm.darkTarget, fullDeck: full },
    visualReviewRequired: true,
  }
}
