import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'
export function renderJournalPlan(design, layouts) {
  const patch = renderNativeEvidencePlan(design, layouts, design.journal)
  for (const op of patch.ops) {
    if (op.op === 'set-table')
      for (const cell of op.cells ?? [])
        if (cell.row === 0) cell.style.borders.bottom.color = design.colors.ink
    if (op.op === 'set-paragraph' && op.format) {
      const c = layouts[op.slide]?.components.find(
        (c) => `S${op.slide}_${c.name}` === op.shape?.name,
      )
      if (c?.paragraphAfterPt) op.format.spaceAfter = c.paragraphAfterPt[op.paragraph] + 'pt'
    }
    if (op.op === 'set-chart')
      for (const a of op.axes ?? [])
        if (a.axis === 'value') {
          a.gridlines = null
          a.line = { color: design.colors.paper, width: '0pt' }
        }
    if (op.op === 'set-text-frame' && op.frame) {
      const c = layouts[op.slide]?.components.find(
        (c) => `S${op.slide}_${c.name}` === op.shape?.name,
      )
      if (c?.kind === 'owned') {
        op.frame.marginLeft = '0.12in'
        op.frame.marginRight = '0.12in'
        op.frame.marginTop = '0.035in'
        op.frame.marginBottom = '0.035in'
      }
    }
  }
  return patch
}
