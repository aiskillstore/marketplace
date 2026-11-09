import { createOps } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { resolveBroadsideDeck } from './layouts.mjs'
export function createBroadsideDeck(design, content) {
  const resolved = resolveBroadsideDeck(design, content),
    p = createOps({ textbox: design.textFrame }),
    b = design.broadside,
    color = (key) => design.colors[key]
  p.ops.push(designTheme(design))
  for (const [s, l] of resolved.layouts.entries()) {
    p.addSlide(s, color(l.mode === 'orange' ? 'orange' : 'ink'))
    for (const c of l.components) {
      const name = `S${s}_${c.name}`,
        [x, y, w, h] = c.frame
      if (c.kind === 'shape') p.box(s, name, 'rectangle', ...c.frame, color(c.color))
      else if (c.kind === 'image-shell') {
        p.box(s, name, 'rectangle', ...c.frame, color('inkAlt'))
        p.setLine(s, name, color('line'), '0.6pt')
      } else if (c.kind === 'text') {
        p.textbox(s, name, ...c.frame)
        p.setText(s, name, c.text)
        const {
          role,
          sizePt,
          lineHeight,
          alignment,
          color: token,
          cjkBold: _cjkBold,
          cjkLineHeight: _cjkLineHeight,
          ...extra
        } = c.style
        c.text.split(/\r\n|\r|\n/).forEach((_, i) => {
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
          frame: { verticalAnchor: 'top' },
        })
      } else if (c.kind === 'chart') {
        const donut = c.chartKind === 'doughnut',
          font = designFont(design, 'mono', b.chart.fontPt, { color: color('cream') })
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: c.chartKind,
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          data: c.data,
        })
        const points = c.data.categories.map((_, i) => ({
          point: i,
          fill: {
            type: 'solid',
            color: color(donut ? b.chart.pointColors[i] : i === c.focus ? 'orange' : 'gray1'),
          },
          line: { color: color('ink'), width: donut ? '1pt' : '0pt' },
        }))
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          series: [
            {
              series: 0,
              fill: { type: 'solid', color: color('gray1') },
              line: { color: color('gray1'), width: '0pt' },
              ...(!donut ? { invertIfNegative: false } : {}),
              points,
            },
          ],
          ...(donut
            ? {}
            : {
                axes: [
                  {
                    axis: 'category',
                    ...(c.chartKind === 'bar' ? { scale: { reverseOrder: true } } : {}),
                    line: { color: color('line'), width: '0.5pt' },
                    ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
                  },
                  {
                    axis: 'value',
                    line: { color: color('line'), width: '0pt' },
                    gridlines: null,
                    minorGridlines: null,
                    ticks: { visible: false, font, major: 'none', minor: 'none' },
                    scale: { min: 0, max: Math.max(...c.data.series[0].values) * 1.2 || 1 },
                  },
                ],
              }),
          dataLabels: [
            {
              showValue: !donut,
              showSeriesName: false,
              showCategoryName: false,
              showPercentage: false,
              showLegendKey: false,
              ...(!donut ? { position: 'outside-end' } : {}),
              font,
              numberFormat: c.numberFormat,
            },
          ],
          plot: donut ? { holeSize: b.chart.holeSize, firstSliceAngle: 270 } : { gapWidth: 70 },
        })
      } else throw Error(`Unregistered Broadside component ${c.kind}`)
    }
  }
  return finishDesign(
    design,
    content,
    { schemaVersion: 'pptx-patch/v1', ops: p.ops },
    resolved.layouts,
  )
}
