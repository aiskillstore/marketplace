import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'
export function renderAmberPlan(design, layouts) {
  const patch = renderNativeEvidencePlan(design, layouts, design.amber)
  for (const [slide, layout] of layouts.entries())
    for (const c of layout.components) {
      const name = `S${slide}_${c.name}`
      if (c.outline)
        patch.ops.push({
          op: 'set-shape',
          slide,
          shape: { name },
          ...(c.hollow ? { fill: { type: 'none' } } : {}),
          line: { color: design.colors[c.outline], width: c.linePt + 'pt' },
        })
      if (c.kind === 'chart' && c.majorUnit !== undefined) {
        const op = patch.ops.find(
          (o) => o.op === 'set-chart' && o.slide === slide && o.shape?.name === name,
        )
        op.axes.find((a) => a.axis === 'value').scale.majorUnit = c.majorUnit
      }
    }
  return patch
}
