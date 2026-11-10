import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'
import { createOps } from '../shared/core-primitives.kit.mjs'
export function renderScholarPlan(design, layouts) {
  const filtered = layouts.map((l) => ({
    ...l,
    components: l.components.filter((c) => c.kind !== 'icon'),
  }))
  const patch = renderNativeEvidencePlan(design, filtered, design.scholar)
  for (const op of patch.ops) {
    const c = layouts[op.slide]?.components.find((c) => `S${op.slide}_${c.name}` === op.shape?.name)
    if (c?.paragraphAfterPt && op.op === 'set-paragraph')
      op.format.spaceAfter = `${c.paragraphAfterPt[op.paragraph] ?? 0}pt`
    if (op.op === 'set-chart') {
      op.dataLabels.forEach((v) => {
        // Keep label visibility, format and font in one explicit series scope.
        // The current runtime's point-position override renders differently in
        // PowerPoint, so small columns move the whole series outside instead.
        v.scope = { series: 0 }
        v.position = 'center'
        v.font.color = design.colors.badgeText
      })
      const chart = layouts[op.slide].components.find(
        (c) => `S${op.slide}_${c.name}` === op.shape.name,
      )
      const labelHeight = (design.scholar.styles.small.sizePt * 1.5) / 72 + 0.06
      if (
        chart.data.series[0].values.some(
          (value) =>
            (Math.abs(value) / (chart.maximum - chart.minimum)) * chart.frame[3] < labelHeight,
        )
      )
        op.dataLabels.forEach((v) => {
          v.position = 'outside-end'
        })
      op.axes.forEach((v) => {
        if (v.axis === 'value') v.gridlines = null
      })
    }
    if (c?.kind === 'table' && op.op === 'set-table') {
      for (const cell of op.cells) {
        const i = cell.row,
          j = cell.column
        cell.style.fill = {
          type: 'solid',
          color: design.colors[i === 0 ? 'paper' : j === 0 ? 'ink' : c.rowTones[i - 1]],
        }
        cell.style.font.color =
          design.colors[
            i > 0 && j === 0
              ? 'white'
              : i > 0 && c.emphasis[i - 1] === j
                ? 'accentText'
                : i === 0
                  ? 'ink'
                  : 'body'
          ]
        cell.style.font.bold = i === 0 || j === 0 || (i > 0 && c.emphasis[i - 1] === j)
        cell.style.borders.bottom.color = design.colors[i === 0 ? 'ink' : 'rule']
      }
      for (const cell of op.cells)
        if (cell.row > 0 && cell.column === 0) cell.style.marginLeft = '0.52in'
    }
  }
  const p = createOps()
  layouts.forEach((l, s) =>
    l.components
      .filter((c) => c.kind === 'icon')
      .forEach((c) =>
        p.icon(s, `S${s}_${c.name}`, c.icon, ...c.frame, {
          color: design.colors[c.color],
          strokeWidth: 2,
        }),
      ),
  )
  patch.ops.push(...p.ops.filter((o) => !['set-slide-size'].includes(o.op)))
  return patch
}
