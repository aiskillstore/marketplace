import { createOps } from '../shared/core-primitives.kit.mjs'
import { designTheme } from '../shared/design-contract.mjs'

export function renderImpactPlan(design, layouts) {
  const p = createOps({ textbox: design.textFrame }),
    C = design.colors,
    b = design.impact
  p.ops.push(designTheme(design))
  const font = (st) => ({
    name: design.fonts[st.role].latin,
    eastAsian: design.fonts[st.role].eastAsian,
    size: `${st.sizePt}pt`,
    color: C[st.color],
    bold: st.bold ?? false,
    italic: false,
  })
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, C.paper)
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') {
        p.textbox(s, name, x, y, w, h)
        p.setText(s, name, c.text)
        c.text.split(/\r\n|\r|\n/).forEach((_, i) => {
          p.runFont(s, name, font(c.style), i)
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
            verticalAnchor: 'top',
            marginLeft: '0.02in',
            marginRight: '0.02in',
            marginTop: '0in',
            marginBottom: '0in',
            autofit: { mode: 'none' },
          },
        })
      } else if (c.kind === 'box') p.box(s, name, 'rectangle', x, y, w, h, C[c.color])
      else if (c.kind === 'arrow' || c.kind === 'feedback') {
        const height = Math.max(h, 0.08),
          width = Math.max(w, 0.08)
        const commands =
          c.kind === 'arrow'
            ? w === 0
              ? [
                  { type: 'move', x: 500, y: 0 },
                  { type: 'line', x: 500, y: 1000 },
                  { type: 'move', x: 180, y: 750 },
                  { type: 'line', x: 500, y: 1000 },
                  { type: 'line', x: 820, y: 750 },
                ]
              : [
                  { type: 'move', x: 0, y: 500 },
                  { type: 'line', x: 1000, y: 500 },
                  { type: 'move', x: 750, y: 180 },
                  { type: 'line', x: 1000, y: 500 },
                  { type: 'line', x: 750, y: 820 },
                ]
            : c.vertical
              ? [
                  { type: 'move', x: 1000, y: 1000 },
                  { type: 'cubic', x1: 0, y1: 1000, x2: 0, y2: 0, x: 1000, y: 0 },
                ]
              : [
                  { type: 'move', x: 1000, y: 0 },
                  { type: 'cubic', x1: 700, y1: 1000, x2: 300, y2: 1000, x: 0, y: 0 },
                ]
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name,
          x: x + 'in',
          y: y + 'in',
          w: width + 'in',
          h: height + 'in',
          path: { width: 1000, height: 1000, commands },
        })
        if (c.kind === 'feedback') {
          const endX = c.vertical ? 1000 : 0
          const armX = c.vertical ? 750 : 35
          commands.push(
            { type: 'move', x: armX, y: 80 },
            { type: 'line', x: endX, y: 0 },
            { type: 'line', x: armX, y: 0 },
          )
        }
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'none' },
          line: {
            color: C.series,
            width: '1.2pt',
            ...(c.kind === 'feedback' ? { dash: 'dash' } : {}),
          },
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
          style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
          columns: c.widths.map((v, column) => ({ column, width: v + 'in' })),
          rows: c.rowHeights.map((v, row) => ({ row, height: v + 'in' })),
          cells: c.cells.flatMap((row, i) =>
            row.map((_, j) => {
              const status = i > 0 && c.status && c.columns[j].kind === 'status',
                dark = status && c.rows[i - 1].status === 'attention'
              return {
                row: i,
                column: j,
                style: {
                  fill: status
                    ? { type: 'solid', color: dark ? C.series : C.tint }
                    : { type: 'none' },
                  font: font({
                    ...b.styles.table,
                    color: dark ? 'paper' : i === 0 ? 'secondary' : 'ink',
                    bold: i > 0 && (j === 1 || status),
                  }),
                  alignment: c.columns[j].kind === 'number' ? 'right' : status ? 'center' : 'left',
                  verticalAnchor: 'middle',
                  marginLeft: '0.07in',
                  marginRight: '0.07in',
                  marginTop: '0.04in',
                  marginBottom: '0.04in',
                  borders: {
                    top: { noLine: true },
                    left: { noLine: true },
                    right: { noLine: true },
                    bottom: { color: C.rule, width: '0.65pt' },
                  },
                },
              }
            }),
          ),
        })
      } else if (c.kind === 'chart') {
        const ft = font(b.styles.table)
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: 'column',
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
              fill: { type: 'solid', color: C.series },
              line: { color: C.paper, width: '0pt' },
              invertIfNegative: false,
              points: c.data.categories.map((_, i) => ({
                point: i,
                fill:
                  c.data.series[0].values[i] < 0
                    ? { type: 'none' }
                    : {
                        type: 'solid',
                        color: i === c.focus ? C.spring : i === 0 ? C.pale : C.series,
                      },
                line:
                  c.data.series[0].values[i] < 0
                    ? { color: i === c.focus ? C.spring : C.series, width: '1pt' }
                    : { color: C.paper, width: '0pt' },
              })),
            },
          ],
          axes: [
            {
              axis: 'category',
              line: { color: C.rule, width: '0.65pt' },
              ticks: { font: ft, major: 'none', minor: 'none', labelPosition: 'low' },
            },
            {
              axis: 'value',
              scale: { min: c.minimum, max: c.maximum },
              line: { color: C.paper, width: '0pt' },
              gridlines: null,
              minorGridlines: null,
              ticks: { visible: false, font: ft, major: 'none', minor: 'none' },
            },
          ],
          dataLabels: [
            {
              showValue: true,
              showSeriesName: false,
              showCategoryName: false,
              position: 'outside-end',
              font: { ...ft, color: C.ink, bold: true },
              numberFormat: c.numberFormat,
            },
          ],
          plot: { gapWidth: 75 },
        })
      } else if (c.kind !== 'numeric-model') throw Error(`Unknown impact component ${c.kind}`)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}
