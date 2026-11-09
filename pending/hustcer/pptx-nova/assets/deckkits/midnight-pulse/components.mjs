import { createOps, fitImageRect } from '../shared/core-primitives.kit.mjs'
import { designTheme } from '../shared/design-contract.mjs'
export function renderPulsePlan(design, layouts, content, options = {}) {
  const p = createOps({ textbox: design.textFrame }),
    C = design.colors,
    b = design.pulse
  p.ops.push(designTheme(design))
  const font = (st) => ({
    name: design.fonts[st.role].latin,
    eastAsian: design.fonts[st.role].eastAsian,
    size: `${st.sizePt}pt`,
    color: C[st.color],
    bold: st.bold ?? false,
    italic: false,
  })
  const inch = (v) => v + 'in'
  const styleText = (s, name, c) => {
    const emphasis = c.style.emphasis ?? [],
      rx = emphasis.length
        ? new RegExp(
            '(' + emphasis.map((v) => v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')',
            'gu',
          )
        : null
    p.setText(s, name, c.runs ? c.runs[0].text : c.text)
    c.text.split(/\r\n|\r|\n/).forEach((line, i) => {
      p.runFont(s, name, font(c.style), i)
      if (c.runs) {
        for (const run of c.runs.slice(1))
          p.ops.push({
            op: 'add-run',
            slide: s,
            shape: { name },
            paragraph: i,
            text: run.text,
            font: font(run.style),
          })
      } else if (rx) {
        const parts = line.split(rx).filter(Boolean)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          text: parts[0] ?? line,
        })
        p.runFont(s, name, { ...font(c.style), bold: emphasis.includes(parts[0]) }, i)
        parts.slice(1).forEach((text) =>
          p.ops.push({
            op: 'add-run',
            slide: s,
            shape: { name },
            paragraph: i,
            text,
            font: { ...font(c.style), bold: emphasis.includes(text) },
          }),
        )
      }
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
        verticalAnchor: c.anchor ?? 'top',
        marginLeft: '0in',
        marginRight: '0in',
        marginTop: '0in',
        marginBottom: '0in',
        autofit: { mode: 'none' },
      },
    })
  }
  for (const [s, l] of layouts.entries()) {
    p.addSlide(s, l.role === 'cover' || l.role === 'close' ? C.deep : C.paper)
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'text') {
        p.textbox(s, name, x, y, w, h)
        if (c.caption)
          p.ops.push({
            op: 'set-shape',
            slide: s,
            shape: { name },
            fill: { type: 'solid', color: C.deep },
            line: { noLine: true },
          })
        styleText(s, name, c)
      } else if (c.kind === 'box' || c.kind === 'ellipse')
        p.box(s, name, c.kind === 'ellipse' ? 'ellipse' : 'rectangle', x, y, w, h, C[c.color])
      else if (c.kind === 'outline') {
        p.shape(s, name, c.ellipse ? 'ellipse' : 'rectangle', x, y, w, h)
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'none' },
          line: { color: C[c.color], width: '0.8pt' },
        })
      } else if (c.kind === 'node') {
        p.shape(s, name, 'ellipse', x, y, w, h)
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'solid', color: C.paper },
          line: { color: C.ice, width: '0.8pt' },
        })
        styleText(s, name, { ...c, anchor: 'middle' })
      } else if (c.kind === 'atmosphere') {
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name,
          x: inch(x),
          y: inch(y),
          w: inch(w),
          h: inch(h),
          path: {
            width: 100000,
            height: 100000,
            commands: [
              ...c.points.map(([a, z], i) => ({
                type: i ? 'line' : 'move',
                x: Math.round(a * 100000),
                y: Math.round(z * 100000),
              })),
              { type: 'close' },
            ],
          },
        })
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: {
            type: 'gradient',
            angle: c.gradientAngle,
            stops: [
              { position: 0, color: C[c.color], alpha: c.alpha },
              { position: 1, color: C[c.color], alpha: 0.05 },
            ],
          },
          line: { noLine: true },
        })
      } else if (c.kind === 'line') {
        p.ops.push({
          op: 'add-freeform',
          slide: s,
          name,
          x: inch(x),
          y: inch(y),
          w: inch(Math.max(0.01, w)),
          h: inch(Math.max(0.01, h)),
          path: {
            width: 100000,
            height: 100000,
            commands: c.points.map(([a, z], i) => ({
              type: i ? 'line' : 'move',
              x: Math.round(a * 100000),
              y: Math.round(z * 100000),
            })),
          },
        })
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'none' },
          line: { color: C[c.color], width: '0.65pt', ...(c.dash ? { dash: 'dash' } : {}) },
        })
      } else if (c.kind === 'image') {
        p.shape(s, name, 'rectangle', x, y, w, h)
        p.ops.push({
          op: 'set-shape',
          slide: s,
          shape: { name },
          fill: { type: 'none' },
          line: { color: C.connector, width: '0.7pt' },
        })
        const slide = content.slides[s],
          keys = Object.keys(slide.imageSlots ?? {})
        if (keys.some((k) => k !== 'cover.photo'))
          throw Error('Only cover.photo is a registered image slot')
        const asset = keys.length ? options.assets?.resolveImageSlot(slide, 'cover.photo') : null
        if (keys.length && !asset) throw Error('cover.photo requires an approved assets manifest')
        if (asset) {
          const f = fitImageRect(
            x + 0.01,
            y + 0.01,
            w - 0.02,
            h - 0.02,
            asset.ratio,
            asset.fitPolicy,
          )
          p.addImage(s, `S${s}_CoverPhoto`, f.x, f.y, f.w, f.h, {
            path: asset.path,
            mimeType: asset.mime,
          })
          p.setImageCrop(s, `S${s}_CoverPhoto`, f.crop)
        }
      } else if (c.kind === 'gauge' || c.kind === 'chart') {
        const ring = c.kind === 'gauge'
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: ring ? 'doughnut' : 'column',
          ...(!ring ? { variant: 'clustered' } : {}),
          x: inch(x),
          y: inch(y),
          w: inch(w),
          h: inch(h),
          data: c.data,
        })
        const series = {
          series: 0,
          fill: { type: 'solid', color: C[ring ? c.tone : 'accent'] },
          line: { color: C.paper, width: '0pt' },
          ...(!ring
            ? { invertIfNegative: false }
            : {
                points: c.data.categories.map((_, i) => ({
                  point: i,
                  fill: { type: 'solid', color: C[i ? 'track' : c.tone] },
                  line: { color: C.paper, width: '0pt' },
                })),
              }),
        }
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          series: [series],
          plot: ring ? { holeSize: 86, firstSliceAngle: 0 } : { gapWidth: 80 },
          dataLabels: [
            {
              showValue: !ring,
              showSeriesName: false,
              showCategoryName: false,
              showPercentage: false,
              ...(!ring ? { position: 'outside-end', numberFormat: c.numberFormat } : {}),
              font: font({ ...b.styles.small, color: 'ice' }),
            },
          ],
          ...(!ring
            ? {
                axes: [
                  {
                    axis: 'category',
                    line: { color: C.connector, width: '0.65pt' },
                    ticks: {
                      font: font(b.styles.small),
                      major: 'none',
                      minor: 'none',
                      labelPosition: 'low',
                    },
                  },
                  {
                    axis: 'value',
                    scale: {
                      min: c.minimum,
                      max: c.maximum,
                      majorUnit: (c.maximum - c.minimum) / 4,
                    },
                    line: { color: C.paper, width: '0pt' },
                    gridlines: { color: C.rule, width: '0.4pt' },
                    minorGridlines: null,
                    ticks: {
                      visible: false,
                      font: font(b.styles.small),
                      major: 'none',
                      minor: 'none',
                    },
                  },
                ],
              }
            : {}),
        })
      } else if (c.kind === 'table') {
        p.ops.push({
          op: 'add-table',
          slide: s,
          name,
          rows: c.cells.length,
          columns: c.cells[0].length,
          x: inch(x),
          y: inch(y),
          w: inch(w),
          h: inch(h),
          data: c.cells,
        })
        p.ops.push({
          op: 'set-table',
          slide: s,
          shape: { name },
          style: { firstRow: false, horizontalBanding: false, verticalBanding: false },
          columns: c.widths.map((v, column) => ({ column, width: inch(v) })),
          rows: c.rowHeights.map((v, row) => ({ row, height: inch(v) })),
          cells: c.cells.flatMap((row, i) =>
            row.map((_, j) => ({
              row: i,
              column: j,
              style: {
                fill: { type: 'none' },
                font: font({
                  ...b.styles.table,
                  bold: i === 0 || j === 2,
                  color:
                    i === 0
                      ? 'ice'
                      : j === 4
                        ? c.states[i - 1] === 'met'
                          ? 'accent'
                          : 'amber'
                        : 'body',
                }),
                alignment: [1, 2, 3].includes(j) ? 'right' : 'left',
                verticalAnchor: 'middle',
                marginLeft: '0.065in',
                marginRight: '0.065in',
                marginTop: '0.045in',
                marginBottom: '0.045in',
                borders: {
                  top: i === 1 ? { color: C.ice, width: '0.8pt' } : { noLine: true },
                  left: { noLine: true },
                  right: { noLine: true },
                  bottom: { color: C.rule, width: '0.5pt' },
                },
              },
            })),
          ),
        })
      } else throw Error(`Unregistered pulse component ${c.kind}`)
    }
  }
  return { schemaVersion: 'pptx-patch/v1', ops: p.ops }
}
