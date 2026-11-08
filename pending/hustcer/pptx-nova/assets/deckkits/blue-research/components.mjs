import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'

// Reuse the shared native evidence executor. Only research-specific chart/table
// styling and inline highlight semantics are compiled here.
export function renderResearchPlan(design, layouts) {
  const patch = renderNativeEvidencePlan(design, layouts, design.research),
    C = design.colors
  for (const op of patch.ops) {
    const name = op.name ?? op.shape?.name
    const c = layouts[op.slide]?.components.find((c) => `S${op.slide}_${c.name}` === name)
    if (!c) continue
    if (op.op === 'set-run' && c.trackingPt) op.font.letterSpacing = c.trackingPt + 'pt'
    if (op.op === 'set-paragraph' && c.paragraphGapPt)
      op.format.spaceAfter = c.paragraphGapPt + 'pt'
    if (op.op === 'set-text-frame' && op.frame && c.anchor) op.frame.verticalAnchor = c.anchor
    if (op.op === 'add-chart') op.variant = c.chartKind === 'line' ? 'markers' : c.variant
    if (op.op === 'set-chart') {
      const stacked = c.variant === 'stacked'
      if (stacked) op.plot.overlap = 100
      op.series = op.series.map((v, i) => {
        const out = {
          ...v,
          fill: { type: 'solid', color: C[i ? 'pale' : 'accent'] },
          line: { color: C.deep, width: '0pt' },
        }
        if (c.chartKind === 'line')
          Object.assign(out, { line: { color: C.deep, width: '1.6pt' }, smooth: false })
        if (c.forecastFrom !== undefined)
          out.points = c.data.categories.map((_, j) => ({
            point: j,
            fill: { type: 'solid', color: C[j > c.forecastFrom ? 'paper' : 'accent'] },
            line:
              j > c.forecastFrom
                ? { color: C.deep, width: '1.1pt', dash: 'dash' }
                : { color: C.accent, width: '0pt' },
          }))
        return out
      })
      op.dataLabels[0].position = stacked
        ? 'center'
        : c.chartKind === 'line'
          ? 'above'
          : 'outside-end'
      op.axes[1].ticks.visible = true
      op.axes[1].ticks.numberFormat = c.numberFormat
    }
    if (op.op === 'set-table' && c.cellFills) {
      op.cells.forEach((cell) => {
        const tone = c.cellFills[cell.row]?.[cell.column] ?? 'paper'
        cell.style.fill = { type: 'solid', color: C[tone] }
        cell.style.font.color = C[tone === 'deep' ? 'paper' : 'ink']
        cell.style.borders.bottom = {
          color: C[cell.row === 0 ? 'accent' : 'rule'],
          width: '0.5pt',
          ...(cell.row ? { dash: 'dash' } : {}),
        }
      })
    }
  }
  return patch
}
