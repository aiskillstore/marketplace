import { createOps } from '../shared/core-primitives.kit.mjs'
import { designTheme } from '../shared/design-contract.mjs'

export function renderMckPlan(design, layouts) {
  const p = createOps({ textbox: design.textFrame }),
    C = design.colors,
    b = design.mck
  p.ops.push(designTheme(design))
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, C.paper)
    const font = (st) => ({
      name: design.fonts[st.role].latin,
      eastAsian: design.fonts[st.role].eastAsian,
      size: `${st.sizePt}pt`,
      color: C[st.color],
      bold: st.bold ?? false,
      italic: false,
    })
    const rect = (name, f, color, kind = 'rectangle', outline) => {
      p.shape(s, name, kind, ...f)
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        fill: color ? { type: 'solid', color: C[color] } : { type: 'none' },
        line: outline ? { color: C[outline], width: `${b.spacing.rulePt}pt` } : { noLine: true },
      })
    }
    const text = (name, f, v, st, own = false) => {
      if (!own) p.textbox(s, name, ...f)
      p.setText(s, name, v)
      v.split(/\r\n|\r|\n/).forEach((_, i) => {
        p.runFont(s, name, font(st), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          format: {
            alignment: st.alignment ?? 'left',
            lineSpacing: st.lineHeight,
            spaceAfter: '0pt',
          },
        })
      })
      p.ops.push({
        op: 'set-text-frame',
        slide: s,
        shape: { name },
        frame: {
          verticalAnchor: st.verticalAnchor ?? 'top',
          marginLeft: own ? '0.04in' : '0.02in',
          marginRight: own ? '0.04in' : '0.02in',
          marginTop: '0in',
          marginBottom: '0in',
          autofit: { mode: 'none' },
        },
      })
    }
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        f = c.frame,
        [x, y, w, h] = f
      if (c.kind === 'text') text(name, f, c.text, c.style)
      else if (c.kind === 'box') rect(name, f, c.color, 'rectangle', c.outline)
      else if (c.kind === 'owned') {
        rect(name, f, c.color)
        text(name, f, c.text, c.style, true)
      } else if (c.kind === 'circle') rect(name, f, c.color, 'oval')
      else if (c.kind === 'icon') {
        p.icon(s, name, c.icon, ...f, { color: C[c.color], strokeWidth: 2.6 })
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
            row.map((_, column) => ({
              row: i,
              column,
              style: {
                fill: { type: 'none' },
                font: font({ ...b.styles.small, color: 'ink' }),
                alignment: 'left',
                verticalAnchor: 'middle',
                marginLeft: '0.08in',
                marginRight: '0.08in',
                marginTop: '0.03in',
                marginBottom: '0.03in',
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: C.rule, width: '0.65pt' },
                },
              },
            })),
          ),
        })
      } else if (c.kind === 'hero') {
        rect(name, f, 'navy')
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: {
            type: 'gradient',
            angle: 0,
            stops: [
              { position: 0, color: C.navy },
              { position: 1, color: C.primary },
            ],
          },
        })
        // Entire rings are bounded to the title-safe region; no off-canvas clipping dependency.
        for (let i = 0; i < 3; i++) {
          const d = 2.5 - i * 0.65
          rect(
            name + 'Ring' + i,
            [10.45 + (2.5 - d) / 2, 0.1 + (2.5 - d) / 2, d, d],
            undefined,
            'oval',
            'blue',
          )
        }
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name: name + 'Cut',
          x: '0in',
          y: `${h - 0.24}in`,
          w: `${w}in`,
          h: '0.26in',
          path: {
            width: 1000,
            height: 100,
            commands: [
              { type: 'move', x: 0, y: 100 },
              { type: 'line', x: 1000, y: 0 },
              {
                type: 'line',
                x: 1000,
                y: 100,
              },
              { type: 'close' },
            ],
          },
        })
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name: name + 'Cut' },
          fill: { type: 'solid', color: C.paper },
          line: { noLine: true },
        })
      } else if (c.kind === 'chart') {
        const ft = font({ ...b.styles.small, sizePt: b.chart.fontPt, color: 'secondary' }),
          n = c.data.categories.length
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: 'bar',
          variant: 'clustered',
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data: c.data,
        })
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          series: [
            {
              series: 0,
              fill: { type: 'solid', color: C.primary },
              line: { color: C.paper, width: '0pt' },
              invertIfNegative: false,
              points: Array.from({ length: n }, (_, i) => ({
                point: i,
                fill: { type: 'solid', color: C[c.tones[i]] },
                line: { color: C.paper, width: '0pt' },
              })),
            },
          ],
          axes: [
            {
              axis: 'category',
              scale: { reverseOrder: true },
              line: { color: C.paper, width: '0pt' },
              ticks: { font: ft, major: 'none', minor: 'none', labelPosition: 'low' },
            },
            {
              axis: 'value',
              scale: { min: 0, max: 100, majorUnit: 25 },
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
              showLegendKey: false,
              position: 'outside-end',
              font: { ...ft, bold: true, color: C.ink },
              numberFormat: c.numberFormat,
            },
          ],
          plot: { gapWidth: 65 },
        })
      } else throw Error(`Unknown Mck component ${c.kind}`)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}
