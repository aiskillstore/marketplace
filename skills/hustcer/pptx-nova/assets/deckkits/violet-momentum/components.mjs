import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'

// Keep the native table's rendered style in sync with its fitted cell plan.
export function renderVioletPlan(design, layouts) {
  const patch = renderNativeEvidencePlan(design, layouts, design.violet)
  for (const op of patch.ops) {
    if (op.op !== 'set-table') continue
    const table = layouts[op.slide].components.find(
      (c) => c.kind === 'table' && op.shape.name === `S${op.slide}_${c.name}`,
    )
    if (!table) throw Error(`Missing Violet table plan: ${op.shape.name}`)
    for (const cell of op.cells) {
      const binding = table.bindings[cell.row * table.columns.length + cell.column]
      cell.style.marginLeft = cell.style.marginRight = `${design.violet.spacing.tablePaddingIn}in`
      cell.style.font = {
        ...cell.style.font,
        size: `${binding.style.sizePt}pt`,
        bold: binding.style.bold,
        color: design.colors[binding.style.color],
      }
    }
  }
  return patch
}
