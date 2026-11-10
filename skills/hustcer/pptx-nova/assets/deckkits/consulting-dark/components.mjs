import { createOps } from '../shared/core-primitives.kit.mjs'
import { designTheme } from '../shared/design-contract.mjs'

export function renderConsultingPlan(design, layouts) {
  const p = createOps({ textbox: design.textFrame }),
    C = design.colors,
    b = design.consulting
  p.ops.push(designTheme(design))
  const font = (st) => ({
    name: design.fonts[st.role].latin,
    eastAsian: design.fonts[st.role].eastAsian,
    size: st.sizePt + 'pt',
    color: C[st.color],
    bold: st.bold ?? false,
    italic: false,
  })
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, C.navy)
    for (const c of l.components) {
      const name = `S${s}_${c.owner ?? c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') {
        if (!c.owner) p.textbox(s, name, x, y, w, h)
        p.setText(s, name, c.text)
        c.text.split(/\r\n|\r|\n/).forEach((_, i) => {
          p.runFont(s, name, font({ ...c.style, ...c.paragraphStyles?.[i] }), i)
          p.ops.push({
            op: 'set-paragraph',
            slide: s,
            shape: { name },
            paragraph: i,
            format: {
              alignment: c.style.alignment ?? 'left',
              lineSpacing: c.style.lineHeight,
              spaceAfter: '0pt',
            },
          })
        })
        p.ops.push({
          op: 'set-text-frame',
          slide: s,
          shape: { name },
          frame: {
            ...design.textFrame,
            ...c.ownerMargins,
            verticalAnchor: 'top',
            autofit: { mode: 'none' },
          },
        })
      } else if (c.kind === 'box' || c.kind === 'arrow' || c.kind === 'circle') {
        p.shape(
          s,
          name,
          c.kind === 'arrow'
            ? c.direction === 'down'
              ? 'down-arrow'
              : 'right-arrow'
            : c.kind === 'circle'
              ? 'oval'
              : 'rectangle',
          x,
          y,
          w,
          h,
        )
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'solid', color: C[c.color] },
          line: { noLine: true },
        })
      } else if (c.kind === 'table') {
        p.ops.push({
          op: 'add-table',
          slide: s,
          name,
          rows: c.cells.length,
          columns: c.cells[0].length,
          x: x + 'in',
          y: y + 'in',
          w: w + 'in',
          h: h + 'in',
          data: c.cells,
        })
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name },
          style: { firstRow: true, horizontalBanding: false, verticalBanding: false },
          columns: c.widths.map((v, column) => ({ column, width: v + 'in' })),
          rows: c.rowHeights.map((v, row) => ({ row, height: v + 'in' })),
          cells: c.cells.flatMap((row, i) =>
            row.map((_, column) => ({
              row: i,
              column,
              style: {
                fill: i === 0 ? { type: 'solid', color: C.deep } : { type: 'none' },
                font: font({
                  ...b.styles.small,
                  color: i === 0 || column === 1 ? 'paper' : 'pale',
                  bold: i === 0 || column === 1,
                }),
                alignment: 'left',
                verticalAnchor: 'middle',
                marginLeft: '0.1in',
                marginRight: '0.1in',
                marginTop: '0.03in',
                marginBottom: '0.03in',
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: C.darkRule, width: b.spacing.rulePt + 'pt' },
                },
              },
            })),
          ),
        })
      } else if (c.kind === 'chart') {
        const ft = font({ ...b.styles.small, sizePt: b.chart.fontPt, color: 'pale' })
        const values = c.data.series[0].values
        const minimum = Math.min(0, ...values)
        // Reserve room before a negative outside-end label, away from category text.
        // Values remain untouched; only the native value-axis domain gains whitespace.
        const paddedMinimum = minimum - Math.max(...values.map(Math.abs)) * 0.3
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: 'bar',
          variant: 'clustered',
          x: x + 'in',
          y: y + 'in',
          w: w + 'in',
          h: h + 'in',
          data: c.data,
        })
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          series: [
            {
              series: 0,
              fill: { type: 'solid', color: C.warm },
              invertIfNegative: false,
              line: { color: C.warm, width: '0pt' },
            },
          ],
          axes: [
            {
              axis: 'category',
              scale: { reverseOrder: true },
              line: { color: C.darkRule, width: '0.6pt' },
              ticks: { font: ft, major: 'none', minor: 'none', labelPosition: 'low' },
            },
            {
              axis: 'value',
              ...(minimum < 0 && Number.isFinite(paddedMinimum)
                ? { scale: { min: paddedMinimum } }
                : {}),
              line: { color: C.darkRule, width: '0pt' },
              gridlines: null,
              minorGridlines: null,
              ticks: { font: ft, visible: false, major: 'none', minor: 'none' },
            },
          ],
          dataLabels: [
            {
              showValue: true,
              showSeriesName: false,
              showCategoryName: false,
              showLegendKey: false,
              position: 'outside-end',
              font: { ...ft, color: C.paper, bold: true },
              numberFormat: 'General',
            },
          ],
          plot: { gapWidth: 65 },
        })
      } else throw Error('Unknown Consulting component ' + c.kind)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}
