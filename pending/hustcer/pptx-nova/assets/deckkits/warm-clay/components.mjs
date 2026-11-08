import { createOps } from '../shared/core-primitives.kit.mjs'
import { designTheme } from '../shared/design-contract.mjs'

export function renderClayPlan(design, layouts) {
  const p = createOps({ textbox: design.textFrame }),
    C = design.colors,
    b = design.clay
  p.ops.push(designTheme(design))
  const font = (st) => ({
    name: design.fonts[st.role].latin,
    eastAsian: design.fonts[st.role].eastAsian,
    size: `${st.sizePt}pt`,
    color: C[st.color],
    bold: st.bold ?? false,
    italic: false,
  })
  const ownedText = (s, name, c) => {
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
        verticalAnchor: c.kind === 'chip' ? 'middle' : 'top',
        marginLeft: '0in',
        marginRight: '0in',
        marginTop: '0in',
        marginBottom: '0in',
        autofit: { mode: 'none' },
      },
    })
    if (c.runs) {
      p.setText(s, name, c.runs[0].text)
      p.runFont(s, name, font(c.runs[0].style), 0)
      for (const run of c.runs.slice(1))
        p.ops.push({
          op: 'add-run',
          slide: s,
          shape: { name },
          paragraph: 0,
          text: run.text,
          font: font(run.style),
        })
    }
  }
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, C.paper)
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') {
        p.textbox(s, name, x, y, w, h)
        ownedText(s, name, c)
      } else if (c.kind === 'box') p.box(s, name, 'rectangle', x, y, w, h, C[c.color])
      else if (c.kind === 'chip') {
        p.box(s, name, 'rectangle', x, y, w, h, C[c.color])
        ownedText(s, name, { ...c, style: { ...c.style, alignment: 'center' } })
      } else if (c.kind === 'placeholder') {
        p.box(s, name, 'rectangle', x, y, w, h, C.paper)
        p.setLine(s, name, C.rule, '0.7pt')
      } else if (c.kind === 'ornament') {
        // Clipped quarter disk is native freeform inside the canvas, no out-of-bounds ellipse.
        const flipX = c.corner.includes('r'),
          flipY = c.corner.includes('b')
        const point = (a, b) => ({ x: flipX ? 1000 - a : a, y: flipY ? 1000 - b : b })
        const commands = [
          { type: 'move', ...point(0, 0) },
          { type: 'line', ...point(1000, 0) },
          {
            type: 'cubic',
            x1: point(1000, 552).x,
            y1: point(1000, 552).y,
            x2: point(552, 1000).x,
            y2: point(552, 1000).y,
            ...point(0, 1000),
          },
          { type: 'close' },
        ]
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name,
          x: x + 'in',
          y: y + 'in',
          w: w + 'in',
          h: h + 'in',
          path: { width: 1000, height: 1000, commands },
        })
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'solid', color: C[c.color] },
          line: { noLine: true },
        })
        const rw = w * 0.45,
          rx = x + w * 0.22,
          ry = y + h * 0.22
        p.shape(s, name + 'Ring', 'ellipse', rx, ry, rw, rw)
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name: name + 'Ring' },
          fill: { type: 'none' },
          line: { color: C.ink, width: '0.65pt' },
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
              const attention =
                  i > 0 &&
                  c.status &&
                  c.columns[j].kind === 'status' &&
                  c.rows[i - 1].status === 'attention',
                focus = i > 0 && j === c.focusColumn
              return {
                row: i,
                column: j,
                style: {
                  fill: { type: 'none' },
                  font: font({
                    ...b.styles.small,
                    color: attention || focus ? 'accent' : i === 0 ? 'body' : 'ink',
                    bold: attention || focus,
                  }),
                  alignment: c.columns[j].kind === 'number' ? 'right' : 'left',
                  verticalAnchor: 'middle',
                  marginLeft: '0.06in',
                  marginRight: '0.06in',
                  marginTop: '0.04in',
                  marginBottom: '0.04in',
                  borders: {
                    top: { noLine: true },
                    left: { noLine: true },
                    right: { noLine: true },
                    bottom: { color: C.rule, width: b.spacing.rulePt + 'pt' },
                  },
                },
              }
            }),
          ),
        })
      } else if (c.kind === 'chart') {
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
              fill: { type: 'solid', color: C.accent },
              line: { color: C.accent, width: '0pt' },
              invertIfNegative: false,
            },
          ],
          axes: [
            {
              axis: 'category',
              line: { color: C.rule, width: '0.7pt' },
              ticks: {
                font: font(b.styles.small),
                major: 'none',
                minor: 'none',
                labelPosition: 'low',
              },
            },
            {
              axis: 'value',
              scale: { min: c.minimum, max: c.maximum },
              line: { color: C.paper, width: '0pt' },
              gridlines: null,
              minorGridlines: null,
              ticks: { visible: false, font: font(b.styles.small), major: 'none', minor: 'none' },
            },
          ],
          dataLabels: [
            {
              showValue: true,
              showSeriesName: false,
              showCategoryName: false,
              position: c.inside ? 'center' : 'outside-end',
              font: font({ ...b.styles.small, color: c.inside ? 'paper' : 'ink', bold: true }),
              numberFormat: c.numberFormat,
            },
          ],
          plot: { gapWidth: 85 },
        })
      } else throw Error(`Unregistered clay component ${c.kind}`)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}
