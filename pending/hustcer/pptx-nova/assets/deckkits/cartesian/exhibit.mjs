// Native specimens share Cartesian chrome; content never supplies executable operations.
import { designFont } from '../shared/design-contract.mjs'
const CHARTS = new Set([
  'column',
  'column-3d',
  'bar-3d',
  'line',
  'line-3d',
  'area-3d',
  'pie-3d',
  'surface',
  'surface-3d',
  'scatter',
  'bubble',
  'combo',
  'radar',
  'doughnut',
  'waterfall',
  'funnel',
  'histogram',
  'treemap',
  'sunburst',
  'box-whisker',
])

// Resolve once during layout selection, so validation and rendering use identical text.
export function resolveCartesianSpecimen(frame, specimen, checkText, path) {
  const q = structuredClone(specimen),
    [x, y, w, h] = frame
  const fit = (value, rect, key, sizePt = 11, display = false) =>
    checkText(
      value,
      rect,
      { role: display ? 'display' : 'body', sizePt, lineHeight: 1.2 },
      `${path}.${key}`,
    ).text
  if (q.kind === 'nodes') {
    for (const [i, n] of q.nodes.entries()) {
      const nw = n.w * w,
        nh = n.h * h
      const angle = ((n.rotation ?? 0) * Math.PI) / 180
      const rw = Math.abs(nw * Math.cos(angle)) + Math.abs(nh * Math.sin(angle))
      const rh = Math.abs(nw * Math.sin(angle)) + Math.abs(nh * Math.cos(angle))
      const cx = n.x * w + nw / 2,
        cy = n.y * h + nh / 2
      if (
        cx - rw / 2 < -0.00001 ||
        cy - rh / 2 < -0.00001 ||
        cx + rw / 2 > w + 0.00001 ||
        cy + rh / 2 > h + 0.00001
      )
        throw Error(`${path}.nodes[${i}]: rotated geometry is outside stage`)
      n.text = fit(
        n.text,
        [x + n.x * w, y + n.y * h, nw, nh],
        `nodes[${i}].text`,
        n.size ?? 20,
        n.display,
      )
    }
    if (q.paragraphs) q.paragraphs = [fit(q.paragraphs.join('\n'), frame, 'paragraphs', 24)]
    if (q.wordArt) q.wordArt = fit(q.wordArt, frame, 'wordArt', 50, true)
  } else if (q.kind === 'charts') {
    const cw = (w - 0.45 * (q.charts.length - 1)) / q.charts.length
    q.charts.forEach((chart, i) => {
      chart.caption = fit(chart.caption, [x, y, cw, 0.34], `charts[${i}].caption`)
    })
  } else if (q.kind === 'equations') {
    q.equations.forEach((e, i) => {
      e.caption = fit(
        e.caption,
        [x, y + (h / q.equations.length) * i, w, 0.3],
        `equations[${i}].caption`,
      )
    })
  }
  return q
}
export function renderCartesianExhibit({ p, s, c, design, text, named }) {
  const [x, y, w, h] = c.frame,
    q = c.specimen,
    col = (k) => design.colors[k]
  const palette = Array.from({ length: 6 }, (_, i) => col(`specimen${i}`))
  const font = designFont(design, 'body', 11, { color: col('body') })
  const label = (name, frame, value, sizePt = 11, display = false) =>
    text(named(`Exhibit${name}`), frame, value, {
      role: display ? 'display' : 'body',
      sizePt,
      lineHeight: 1.2,
      color: 'ink',
    })
  if (q.kind === 'charts') {
    if (!q.charts?.length || q.charts.length > 2) throw Error('Exhibit requires one or two charts')
    q.charts.forEach((ch, i) => {
      if (!CHARTS.has(ch.kind)) throw Error(`Unregistered exhibit chart ${ch.kind}`)
      const cw = (w - 0.45 * (q.charts.length - 1)) / q.charts.length,
        cx = x + i * (cw + 0.45),
        name = named(`ExhibitChart${i}`),
        ex = ['waterfall', 'funnel', 'histogram', 'treemap', 'sunburst', 'box-whisker'].includes(
          ch.kind,
        )
      label(`ChartLabel${i}`, [cx, y, cw, 0.34], ch.caption)
      p.ops.push({
        op: 'add-chart',
        slide: s,
        name,
        kind: ch.kind,
        variant: ch.variant ?? (ch.kind === 'scatter' ? 'markers' : 'standard'),
        x: `${cx}in`,
        y: `${y + 0.45}in`,
        w: `${cw}in`,
        h: `${h - 0.45}in`,
        ...(ch.data ? { data: ch.data } : { dataEx: ch.dataEx }),
        ...(!ex && ch.legend ? { legend: ch.legend } : {}),
      })
      if (ex) {
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          colorStyle: { method: 'cycle', colors: palette },
          ...(ch.labels ? { dataLabels: ch.labels } : {}),
        })
        return
      }
      const xy = ['scatter', 'bubble'].includes(ch.kind),
        axes = ['pie-3d', 'doughnut', 'radar'].includes(ch.kind)
          ? undefined
          : [
              {
                axis: xy ? 'x' : 'category',
                line: { color: col('line'), width: '0.5pt' },
                ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
                ...(ch.xScale ? { scale: ch.xScale } : {}),
              },
              {
                axis: xy ? 'y' : 'value',
                line: { color: col('line'), width: '0.5pt' },
                gridlines: { color: col('bg2'), width: '0.5pt' },
                ticks: { font, major: 'none', minor: 'none' },
                ...(ch.yScale ? { scale: ch.yScale } : {}),
              },
            ]
      p.ops.push({
        op: 'set-chart',
        slide: s,
        shape: { name },
        colorStyle: { method: 'cycle', colors: palette },
        ...(axes ? { axes } : {}),
        ...(ch.view3D ? { view3D: ch.view3D } : {}),
        ...(ch.plot ? { plot: ch.plot } : {}),
        legend: { position: ch.legend ?? 'bottom', font, includeInLayout: false },
        ...(!['surface', 'surface-3d'].includes(ch.kind) && ch.data?.series
          ? {
              series: ch.data.series.map((ss, j) => ({
                series: j,
                fill: { type: 'solid', color: palette[j % palette.length] },
                line: { color: palette[j % palette.length], width: '1.25pt' },
                ...(['pie-3d', 'doughnut'].includes(ch.kind)
                  ? {
                      points: ch.data.categories.map((_, z) => ({
                        point: z,
                        fill: { type: 'solid', color: palette[z % palette.length] },
                      })),
                    }
                  : {}),
                ...(ch.seriesStyles?.[j] ?? {}),
              })),
            }
          : {}),
        ...(ch.labels ? { dataLabels: ch.labels } : {}),
      })
    })
  } else if (q.kind === 'nodes') {
    for (const [i, n] of (q.nodes ?? []).entries()) {
      if (
        ![n.x, n.y, n.w, n.h].every(Number.isFinite) ||
        n.w <= 0 ||
        n.h <= 0 ||
        n.x < 0 ||
        n.y < 0 ||
        n.x + n.w > 1.001 ||
        n.y + n.h > 1.001
      )
        throw Error(`Exhibit node ${i} is outside stage`)
      const name = named(`ExhibitNode${i}`),
        frame = [x + n.x * w, y + n.y * h, n.w * w, n.h * h]
      p.shape(s, name, n.shape ?? 'oval', ...frame)
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        fill: { type: 'solid', color: col(n.fill ?? 'bg2') },
        line: { color: col('accent'), width: '0.7pt' },
        ...(n.rotation ? { rotation: n.rotation } : {}),
      })
      text(
        name,
        frame,
        n.text,
        {
          role: n.display ? 'display' : 'body',
          sizePt: n.size ?? 20,
          lineHeight: 1.2,
          color: 'ink',
          alignment: 'center',
          verticalAnchor: 'middle',
        },
        { owned: true },
      )
    }
    if (q.paragraphs) label('Paragraphs', [x, y, w, h], q.paragraphs.join('\n'), 24)
    if (q.wordArt) label('Words', [x, y, w, h], q.wordArt, 50, true)
  } else if (q.kind === 'equations') {
    for (const [i, e] of (q.equations ?? []).entries()) {
      const pitch = h / q.equations.length,
        name = named(`ExhibitEquation${i}`)
      label(`EquationLabel${i}`, [x, y + pitch * i, w, 0.3], e.caption)
      p.ops.push({
        op: 'add-equation',
        slide: s,
        name,
        x: `${x + 0.3}in`,
        y: `${y + pitch * i + 0.45}in`,
        w: `${w - 0.6}in`,
        h: `${pitch - 0.55}in`,
        latex: e.latex,
        mode: 'native-omml',
      })
    }
  } else throw Error(`Unknown exhibit kind ${q.kind}`)
}
