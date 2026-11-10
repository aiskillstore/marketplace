import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { renderEvidence, renderEvidenceChart } from '../shared/evidence-components.mjs'
import { resolveBiennaleDeck } from './layouts.mjs'

// Components execute resolved geometry only. They neither choose layouts nor carry
// slide-type dispatch, source copy, independent coordinates or fallback renderers.
export function createBiennaleDeck(design, content) {
  const resolved = resolveBiennaleDeck(design, content)
  const p = createOps({ textbox: design.textFrame })
  p.ops.push(designTheme(design))
  const color = (token) => design.colors[token]
  for (const [s, slide] of content.slides.entries()) {
    const layout = resolved.layouts[s]
    if (layout.role === 'evidence') {
      renderEvidence(p, design, s, slide, layout, content.slides.length)
      continue
    }
    p.addSlide(s, color(design.roles.surface))
    const text = (name, frame, value, style) => {
      p.textbox(s, name, ...frame)
      p.setText(s, name, value)
      const { role, sizePt, lineHeight, alignment, verticalAnchor, ...extra } = style
      for (let i = 0; i < value.split(/\r\n|\r|\n/).length; i++) {
        p.runFont(s, name, designFont(design, role, sizePt, extra), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          format: { lineSpacing: lineHeight, spaceAfter: '0pt', alignment: alignment ?? 'left' },
        })
      }
      if (verticalAnchor)
        p.ops.push({ op: 'set-text-frame', slide: s, shape: { name }, frame: { verticalAnchor } })
    }
    for (const c of layout.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') text(name, c.frame, c.text, c.style)
      else if (c.kind === 'plane') {
        p.box(s, name, 'rectangle', ...c.frame, color(c.color))
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'solid', color: color(c.color), alpha: c.alpha },
        })
      } else if (c.kind === 'bloom') {
        p.shape(s, name, 'oval', ...c.frame)
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          line: { noLine: true },
          fill: {
            type: 'gradient',
            path: 'circle',
            fillToRect: { left: 0.5, top: 0.5, right: 0.5, bottom: 0.5 },
            stops: [
              { position: 0, color: { rgb: color(c.color), alpha: c.alpha } },
              { position: 0.5, color: { rgb: color(c.color), alpha: c.alpha * 0.6 } },
              { position: 1, color: { rgb: color(c.color), alpha: 0 } },
            ],
          },
        })
      } else if (c.kind === 'chart')
        renderEvidenceChart(
          p,
          design,
          s,
          c.data,
          { frame: { chart: c.frame }, numberFormat: c.numberFormat },
          c.name,
        )
      else if (c.kind === 'table') {
        p.ops.push({
          op: 'add-table',
          slide: s,
          name,
          rows: c.cells.length,
          columns: 4,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data: c.cells,
        })
        const pad = `${design.biennale.spacing.cellPadding}in`
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name },
          style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
          columns: c.widths.map((w, column) => ({ column, width: `${w}in` })),
          rows: c.rowHeights.map((h, row) => ({ row, height: `${h}in` })),
          cells: c.cells.flatMap((row, i) =>
            row.map((_, column) => ({
              row: i,
              column,
              style: {
                fill: { type: 'solid', color: color(design.roles.surface) },
                font: designFont(
                  design,
                  'body',
                  design.biennale.styles[i ? 'body' : 'label'].sizePt,
                  { bold: i === 0 },
                ),
                alignment: column === 3 ? 'right' : 'left',
                verticalAnchor: 'middle',
                marginLeft: pad,
                marginRight: pad,
                marginTop: pad,
                marginBottom: pad,
                borders: {
                  top: { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: {
                    color: color(i === 0 ? design.roles.rule : 'paperDeep'),
                    width: i === 0 ? '0.75pt' : '0.5pt',
                  },
                },
              },
            })),
          ),
        })
      } else throw new Error(`Unregistered Biennale component: ${c.kind}`)
    }
    text(
      `S${s}_Page`,
      design.biennale.chrome.page,
      `${String(s + 1).padStart(2, '0')} / ${String(content.slides.length).padStart(2, '0')}`,
      { ...design.biennale.styles.mono, alignment: 'right' },
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
