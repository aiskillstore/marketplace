import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { resolveLongTableDeck } from './layouts.mjs'

// Native capsule: semicircle ends, exact aspect ratio, editable path and owned text.
function capsule(w, h) {
  const W = Math.round(w * 10000),
    H = Math.round(h * 10000),
    r = Math.round(H / 2),
    k = Math.round(r * 0.55228475)
  return {
    width: W,
    height: H,
    commands: [
      { type: 'move', x: r, y: 0 },
      { type: 'line', x: W - r, y: 0 },
      { type: 'cubic', x1: W - r + k, y1: 0, x2: W, y2: r - k, x: W, y: r },
      { type: 'cubic', x1: W, y1: r + k, x2: W - r + k, y2: H, x: W - r, y: H },
      { type: 'line', x: r, y: H },
      { type: 'cubic', x1: r - k, y1: H, x2: 0, y2: r + k, x: 0, y: r },
      { type: 'cubic', x1: 0, y1: r - k, x2: r - k, y2: 0, x: r, y: 0 },
      { type: 'close' },
    ],
  }
}
export function createLongTableDeck(design, content) {
  const b = design.longTable,
    p = createOps({ textbox: design.textFrame }),
    resolved = resolveLongTableDeck(design, content),
    color = (t) => design.colors[t]
  p.ops.push(designTheme(design))
  for (const [s] of content.slides.entries()) {
    p.addSlide(s, color('paper'))
    const text = (name, frame, value, style, owned = false, inset = 0) => {
      if (!owned) p.textbox(s, name, ...frame)
      p.setText(s, name, value)
      const { role, sizePt, color: token, lineHeight, alignment, verticalAnchor, ...extra } = style
      value.split(/\r\n|\r|\n/).forEach((_, i) => {
        p.runFont(s, name, designFont(design, role, sizePt, { color: color(token), ...extra }), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          format: { alignment: alignment ?? 'left', lineSpacing: lineHeight, spaceAfter: '0pt' },
        })
      })
      p.ops.push({
        op: 'set-text-frame',
        slide: s,
        shape: { name },
        frame: {
          verticalAnchor: verticalAnchor ?? 'top',
          marginLeft: `${inset}in`,
          marginRight: `${inset}in`,
          marginTop: '0in',
          marginBottom: '0in',
          autofit: { mode: 'none' },
        },
      })
    }
    const outline = (name, frame, kind = 'rectangle') => {
      const [x, y, w, h] = frame
      if (kind === 'pill')
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          path: capsule(w, h),
        })
      else p.shape(s, name, kind, ...frame)
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        fill: { type: 'none' },
        line: { color: color('ink'), width: `${b.spacing.outlinePt}pt` },
      })
    }
    for (const c of resolved.layouts[s].components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') text(name, c.frame, c.text, c.style)
      else if (['pill', 'badge', 'tag'].includes(c.kind)) {
        outline(
          name,
          c.frame,
          c.kind === 'badge' ? 'oval' : c.kind === 'tag' ? 'rectangle' : 'pill',
        )
        text(name, c.frame, c.text, c.style, true, c.inset)
      } else if (c.kind === 'panel') outline(name, c.frame)
      else if (c.kind === 'rule') {
        p.ops.push({
          op: 'add-connector',
          slide: s,
          name,
          kind: 'straight',
          begin: { x: `${x}in`, y: `${y}in` },
          end: { x: `${x + w}in`, y: `${y}in` },
        })
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          line: {
            color: color(c.color),
            width: c.color === 'ink' ? '0.75pt' : '0.5pt',
            ...(c.dash ? { dash: 'dash' } : {}),
          },
        })
      } else if (c.kind === 'table') {
        p.ops.push({
          op: 'add-table',
          slide: s,
          name,
          rows: c.cells.length,
          columns: 5,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data: c.cells,
        })
        const pad = `${b.spacing.cellPad}in`
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name },
          style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
          columns: c.widths.map((w, column) => ({ column, width: `${w}in` })),
          rows: c.rowHeights.map((h, row) => ({ row, height: `${h}in` })),
          cells: c.cells.flatMap((row, i) =>
            row.map((value, column) => ({
              row: i,
              column,
              style: {
                fill: { type: 'none' },
                font: designFont(design, 'body', b.styles[i ? 'table' : 'tableHead'].sizePt, {
                  color: color('ink'),
                  bold: i === 0,
                }),
                alignment: column === 4 ? 'center' : 'left',
                verticalAnchor: 'middle',
                marginLeft: pad,
                marginRight: pad,
                marginTop: pad,
                marginBottom: pad,
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: color(i ? 'ruleSoft' : 'ink'), width: i ? '0.5pt' : '0.75pt' },
                },
              },
            })),
          ),
        })
        // Status outlines surround table-owned text without duplicating cell content.
        let top = y + c.rowHeights[0]
        const statusX = x + c.widths.slice(0, 4).reduce((n, v) => n + v, 0)
        for (let i = 1; i < c.cells.length; i++) {
          outline(
            `${name}Status${i}`,
            [statusX + 0.05, top + (c.rowHeights[i] - 0.4) / 2, c.widths[4] - 0.1, 0.4],
            'pill',
          )
          top += c.rowHeights[i]
        }
      } else throw Error(`Unknown Long Table component ${c.kind}`)
    }
    text(
      `S${s}_PageNum`,
      b.chrome.page,
      `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
      { ...b.styles.source, alignment: 'right' },
    )
  }
  const result = finishDesign(
    design,
    content,
    { schemaVersion: 'pptx-patch/v1', ops: p.ops },
    resolved.layouts,
  )
  result.warnings = resolved.warnings
  return result
}
