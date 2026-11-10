import { createOps } from '../shared/core-primitives.kit.mjs'
import { designTheme, finishDesign } from '../shared/design-contract.mjs'
import { resolveSwissDeck } from './layouts.mjs'

function renderSwissPlan(design, layouts) {
  const p = createOps({ textbox: design.textFrame }),
    b = design.swiss,
    C = design.colors
  p.ops.push(designTheme(design))
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, C.paper)
    const font = (style) => ({
      name: design.fonts[style.role].latin,
      eastAsian: design.fonts[style.role].eastAsian,
      size: `${style.sizePt}pt`,
      color: C[style.color],
      bold: style.bold ?? false,
      italic: false,
    })
    const tx = (name, f, v, style, owned = false, inset = 0, highlights = []) => {
      if (!owned) p.textbox(s, name, ...f)
      p.setText(s, name, v)
      v.split(/\r\n|\r|\n/).forEach((para, i) => {
        p.runFont(s, name, font(style), i)
        if (highlights.length) {
          const escaped = highlights
              .map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
              .sort((a, b) => b.length - a.length),
            parts = para.split(new RegExp('(' + escaped.join('|') + ')', 'g')).filter(Boolean)
          parts.forEach((text, j) =>
            p.ops.push({
              op: j ? 'add-run' : 'set-run',
              slide: s,
              shape: { name },
              paragraph: i,
              ...(j ? {} : { run: 0 }),
              text,
              font: font({
                ...style,
                bold: highlights.includes(text) || style.bold,
              }),
            }),
          )
        }
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          format: {
            alignment: style.alignment ?? 'left',
            lineSpacing: style.lineHeight,
            spaceAfter: '0pt',
          },
        })
      })
      p.ops.push({
        op: 'set-text-frame',
        slide: s,
        shape: { name },
        frame: {
          verticalAnchor: style.verticalAnchor ?? 'top',
          marginLeft: `${inset}in`,
          marginRight: `${inset}in`,
          marginTop: '0in',
          marginBottom: '0in',
          autofit: { mode: 'none' },
        },
      })
    }
    const box = (name, f, color = null, outline) => {
      p.shape(s, name, 'rectangle', ...f)
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        fill: color ? { type: 'solid', color: C[color] } : { type: 'none' },
        line: outline ? { color: C[outline], width: '0.65pt' } : { noLine: true },
      })
    }
    const line = (name, x, y, w, token = 'rule', vertical = false) => {
      p.ops.push({
        op: 'add-connector',
        slide: s,
        name,
        kind: 'straight',
        begin: { x: `${x}in`, y: `${y}in` },
        end: {
          x: `${x + (vertical ? 0 : w)}in`,
          y: `${y + (vertical ? w : 0)}in`,
        },
      })
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        line: { color: C[token], width: `${b.spacing.rulePt}pt` },
      })
    }
    const diagram = (name, f, kind, token) => {
      const [x, y, w, h] = f,
        pad = 0.12,
        innerX = x + pad,
        innerY = y + pad,
        innerWidth = w - pad * 2,
        innerHeight = h - pad * 2
      box(name, f, undefined, token)
      if (kind === 'manuscript') {
        for (let j = 0; j < 6; j++)
          line(
            name + 'Line' + j,
            innerX,
            innerY + ((j + 1) * innerHeight) / 7,
            innerWidth * (j === 5 ? 0.72 : 1),
            'secondary',
          )
      } else if (kind === 'columns') {
        for (let i = 0; i < 3; i++) {
          const cw = (innerWidth - 0.12) / 3,
            cx = innerX + i * (cw + 0.06)
          box(name + 'Column' + i, [cx, innerY, cw, innerHeight], 'panel')
          for (let j = 0; j < 3; j++)
            line(name + `Line${i}_${j}`, cx, innerY + ((j + 1) * innerHeight) / 6, cw, 'secondary')
        }
      } else if (kind === 'modular') {
        for (let j = 0; j < 4; j++)
          for (let i = 0; i < 4; i++)
            box(
              name + `Cell${i}_${j}`,
              [x + (i * w) / 4, y + (j * h) / 4, w / 4, h / 4],
              j === 0 && i < 2
                ? 'redTint'
                : i === 1 && j > 1
                  ? 'ink'
                  : i === 3 && j === 3
                    ? 'secondary'
                    : undefined,
              token,
            )
      } else if (kind === 'hierarchical') {
        box(name + 'Headline', [x, y, w, h * 0.23], 'ink')
        box(name + 'Feature', [x, y + h * 0.28, w * 0.64, h * 0.46], 'rule')
        box(name + 'Aside', [x + w * 0.7, y + h * 0.28, w * 0.3, h * 0.23], 'secondary')
        box(name + 'Aside2', [x + w * 0.7, y + h * 0.57, w * 0.3, h * 0.17], 'panel')
        box(name + 'Foot1', [x, y + h * 0.8, w * 0.3, h * 0.2], 'secondary')
        box(name + 'Foot2', [x + w * 0.36, y + h * 0.8, w * 0.64, h * 0.2], 'rule')
      }
    }
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') tx(name, c.frame, c.text, c.style, false, 0, c.highlights)
      else if (c.kind === 'owned') {
        box(name, c.frame, c.fill, 'ink')
        tx(name, c.frame, c.text, c.style, true, c.inset)
      } else if (c.kind === 'panel') box(name, c.frame, c.color, c.outline)
      else if (c.kind === 'dot') {
        p.shape(s, name, 'oval', ...c.frame)
        p.fill(s, name, C[c.color])
        p.noLine(s, name)
      } else if (c.kind === 'rule') line(name, x, y, c.vertical ? h : w, c.color, c.vertical)
      else if (c.kind === 'icon')
        p.icon(s, name, c.icon, ...c.frame, {
          color: C[c.color],
          strokeWidth: 1,
        })
      else if (c.kind === 'diagram') diagram(name, c.frame, c.diagram, c.color)
      else if (c.kind === 'table') {
        p.ops.push({
          op: 'add-table',
          slide: s,
          name,
          rows: c.cells.length,
          columns: c.columns.length,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data: c.cells,
        })
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name },
          style: {
            firstRow: false,
            horizontalBanding: false,
            verticalBanding: false,
          },
          columns: c.widths.map((v, column) => ({ column, width: `${v}in` })),
          rows: c.rowHeights.map((v, row) => ({ row, height: `${v}in` })),
          cells: c.cells.flatMap((row, i) =>
            row.map((v, column) => ({
              row: i,
              column,
              style: {
                fill: { type: 'none' },
                font: font({
                  ...b.styles[i ? 'table' : 'tableHead'],
                  bold: i === 0 || column === 0,
                  color: i && c.rowTones[i - 1] === 'focus' ? 'red' : 'ink',
                }),
                alignment: c.columns[column].align ?? 'left',
                verticalAnchor: 'middle',
                marginLeft: '0.1in',
                marginRight: '0.1in',
                marginTop: '0in',
                marginBottom: '0in',
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: {
                    color: C[i ? 'rule' : 'ink'],
                    width: i ? '0.5pt' : '0.8pt',
                  },
                },
              },
            })),
          ),
        })
      } else throw Error(`Unknown component ${c.kind}`)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}

export function createSwissDeck(design, content) {
  const resolved = resolveSwissDeck(design, content)
  const result = finishDesign(
    design,
    content,
    renderSwissPlan(design, resolved.layouts),
    resolved.layouts,
  )
  result.warnings = resolved.warnings
  return result
}
