import { readFileSync } from 'node:fs'
import { renderNativeEvidencePlan } from '../shared/native-evidence-plan.mjs'
export function renderPinkPlan(design, layouts, content, options = {}) {
  const imageComponents = layouts.flatMap((l, s) =>
    l.components.filter((c) => c.kind === 'image').map((c) => ({ s, c })),
  )
  const filtered = layouts.map((l) => ({
    ...l,
    components: l.components.filter((c) => c.kind !== 'image'),
  }))
  const patch = renderNativeEvidencePlan(design, filtered, design.pink),
    C = design.colors,
    ops = []
  const component = (op) =>
    layouts[op.slide]?.components.find((c) => `S${op.slide}_${c.name}` === op.shape?.name)
  for (const op of patch.ops) {
    const c = component(op)
    if (op.op === 'set-paragraph' && c?.paragraphAfterPt)
      op.format.spaceAfter = c.paragraphAfterPt[op.paragraph] + 'pt'
    if (op.op === 'set-slide-background')
      op.fill = {
        type: 'gradient',
        path: 'circle',
        fillToRect: { left: 0.3, top: 0.3, right: 0.7, bottom: 0.7 },
        stops: [
          { position: 0, color: C.lit },
          { position: 0.62, color: C.paper },
          { position: 1, color: C.edge },
        ],
      }
    if (op.op === 'set-chart') {
      const colors = [C.accent, C.muted]
      op.series = c.data.series.map((_, series) => ({
        series,
        line: {
          color: colors[series],
          width: series ? '1.1pt' : '1.6pt',
          ...(series ? { dash: 'dash' } : {}),
        },
        smooth: false,
        marker: { symbol: 'none', size: 4, fill: colors[series], line: colors[series] },
        ...(!series
          ? {
              points: [
                {
                  point: c.focusPoint,
                  marker: { symbol: 'circle', size: 7, fill: C.accent, line: C.accent },
                },
              ],
            }
          : {}),
      }))
      op.axes.find((a) => a.axis === 'value').ticks.visible = true
      op.dataLabels[0].showValue = false
    }
    if (op.op === 'set-table')
      for (const cell of op.cells) {
        const i = cell.row,
          j = cell.column
        cell.style.font = { ...cell.style.font, bold: false, color: i === 0 ? C.accent : C.ink }
        const status = c.statuses.find((v) => v.row === i - 1 && v.column === j)
        if (status) {
          cell.style.fill = {
            type: 'solid',
            color: status.state === 'solid' ? C.accent : j === c.focusColumn ? C.wash : C.paper,
          }
          cell.style.font.color =
            status.state === 'solid' ? C.paper : status.state === 'outline' ? C.accent : C.muted
          cell.style.font.bold = status.state === 'solid'
        }
      }
    if (op.op === 'set-run' && c?.style && c.kind !== 'table') {
      const text = c.text.split(/\r\n|\r|\n/)[op.paragraph ?? 0]
      const pieces = text.match(
        /[\p{Script=Han}\u3000-\u303f\uff00-\uffef]+|[^\p{Script=Han}\u3000-\u303f\uff00-\uffef]+/gu,
      ) ?? [text]
      const runs = pieces.map((text) => ({
        text,
        font: {
          ...op.font,
          ...(/\p{Script=Han}/u.test(text) && c.style.role === 'display'
            ? { name: design.fonts.display.eastAsian, bold: true }
            : {}),
          ...(c.style.role === 'mono' && !/\p{Script=Han}/u.test(text)
            ? { letterSpacing: '0.8pt' }
            : {}),
        },
      }))
      if (c.unit && text.endsWith(' ' + c.unit)) {
        const value = text.slice(0, -c.unit.length - 1)
        runs.splice(
          0,
          runs.length,
          { text: value, font: op.font },
          {
            text: ' ' + c.unit,
            font: {
              ...op.font,
              name: design.fonts.body.latin,
              eastAsian: design.fonts.body.eastAsian,
              size: '15pt',
              color: C.ink,
            },
          },
        )
      }
      // Reset the paragraph before appending rich runs. This keeps native text
      // and the shared applied-object readback on the same replay semantics.
      if (runs.length > 1)
        ops.push({
          op: 'set-paragraph',
          slide: op.slide,
          shape: op.shape,
          paragraph: op.paragraph ?? 0,
          text: runs[0].text,
        })
      ops.push({ ...op, font: runs[0].font })
      for (const run of runs.slice(1))
        ops.push({
          op: 'add-run',
          slide: op.slide,
          shape: op.shape,
          paragraph: op.paragraph ?? 0,
          ...run,
        })
      continue
    }
    if (op.op === 'set-text-frame' && op.frame && c) {
      if (c.vertical) op.frame.direction = 'vertical-270'
      if (c.kind === 'owned')
        Object.assign(op.frame, {
          marginLeft: '0.1in',
          marginRight: '0.1in',
          marginTop: '0.04in',
          marginBottom: '0.04in',
          verticalAnchor: 'middle',
        })
    }
    if (op.op === 'set-shape' && c?.transparent && op.fill) op.fill = { type: 'none' }
    ops.push(op)
    if (op.op === 'set-text-frame' && c?.style?.glow)
      ops.push({
        op: 'set-shape',
        slide: op.slide,
        shape: op.shape,
        effect: { glow: { color: C.accent, alpha: 0.12, radius: '12pt' } },
      })
  }
  for (const { s, c } of imageComponents) {
    const slide = content.slides[s],
      asset = options.assets?.resolveImageSlot(slide, c.slotId)
    if (slide.imageSlots?.[c.slotId] && !asset)
      throw Error('contact.qr requires --assets assets_manifest.json')
    if (asset) {
      if (asset.ratio !== '1:1' || !['contain', 'no-crop'].includes(asset.fitPolicy))
        throw Error('contact.qr requires a square uncropped image with its own quiet zone')
      const [x, y, w, h] = c.frame
      ops.push({
        op: 'add-image',
        slide: s,
        name: `S${s}_${c.name}`,
        x: x + 'in',
        y: y + 'in',
        w: w + 'in',
        h: h + 'in',
        bytesBase64: readFileSync(asset.absolutePath).toString('base64'),
        mimeType: asset.mime,
      })
    }
  }
  return { ...patch, ops }
}
