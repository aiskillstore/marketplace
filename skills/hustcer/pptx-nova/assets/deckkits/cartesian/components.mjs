import { renderCartesianExhibit } from './exhibit.mjs'
import { createOps, fitImageRect } from '../shared/core-primitives.kit.mjs'
import { designFont, designTheme, finishDesign } from '../shared/design-contract.mjs'
import { resolveCartesianDeck } from './layouts.mjs'

// Rendering executes resolved component frames; it does not select page types.
export function createCartesianDeck(design, content, options = {}) {
  const resolved = resolveCartesianDeck(design, content),
    p = createOps({ textbox: design.textFrame }),
    b = design.cartesian
  const theme = designTheme(design)
  if (content.slides.some((slide) => design.cartesian.families[slide.type]?.role === 'exhibit')) {
    for (let i = 0; i < 6; i++) theme.colors[`accent${i + 1}`] = design.colors[`specimen${i}`]
  }
  p.ops.push(theme)
  const color = (token) => design.colors[token]
  for (const [s, slide] of content.slides.entries()) {
    p.addSlide(s, color(design.roles.surface))
    const named = (base) => `S${s}_${base}`
    const text = (name, frame, value, style, { owned = false, paragraphs = null } = {}) => {
      if (!owned) p.textbox(s, name, ...frame)
      p.setText(s, name, value)
      const { role, sizePt, lineHeight, alignment, verticalAnchor, color: token, ...extra } = style
      value.split(/\r\n|\r|\n/).forEach((_, i) => {
        p.runFont(s, name, designFont(design, role, sizePt, { color: color(token), ...extra }), i)
        p.ops.push({
          op: 'set-paragraph',
          slide: s,
          shape: { name },
          paragraph: i,
          format: {
            alignment: alignment ?? 'left',
            lineSpacing: lineHeight,
            spaceAfter: '0pt',
            ...(paragraphs
              ? {
                  level: paragraphs.levels[i],
                  indent: '0pt',
                  spaceAfter: `${paragraphs.pitch * 72 - sizePt * lineHeight}pt`,
                }
              : {}),
          },
        })
      })
      p.ops.push({
        op: 'set-text-frame',
        slide: s,
        shape: { name },
        frame: {
          verticalAnchor: verticalAnchor ?? 'top',
          ...(owned
            ? { marginLeft: '0in', marginRight: '0in', marginTop: '0in', marginBottom: '0in' }
            : {}),
        },
      })
    }
    const outline = (
      name,
      frame,
      kind = 'rectangle',
      fill = null,
      dash = null,
      lineColor = 'line',
    ) => {
      p.shape(s, name, kind, ...frame)
      p.ops.push({
        op: 'set-shape',
        slide: s,
        shape: { name },
        fill: fill ? { type: 'solid', color: color(fill) } : { type: 'none' },
        line: { color: color(lineColor), width: '0.65pt', ...(dash ? { dash } : {}) },
      })
    }
    for (const c of resolved.layouts[s].components) {
      const name = named(c.name),
        [x, y, w, h] = c.frame
      if (c.kind === 'text' || c.kind === 'paragraphs')
        text(name, c.frame, c.text, c.style, { paragraphs: c.kind === 'paragraphs' ? c : null })
      else if (c.kind === 'medallion') {
        outline(name, c.frame, 'oval', c.fill)
        text(name, c.frame, c.text, c.style, { owned: true })
      } else if (c.kind === 'panel') outline(name, c.frame, 'rectangle', c.color)
      else if (c.kind === 'rule') p.box(s, name, 'rectangle', ...c.frame, color(c.color))
      else if (c.kind === 'ring') {
        outline(name, c.frame, 'oval', null, null, c.color)
        const inset = (w * (1 - c.inner)) / 2
        outline(
          name + 'Inner',
          [x + inset, y + inset, w * c.inner, h * c.inner],
          'oval',
          null,
          'dash',
          c.color,
        )
      } else if (c.kind === 'image') {
        const slots = slide.imageSlots ?? {},
          keys = Object.keys(slots)
        if (keys.some((k) => k !== 'image.editorial'))
          throw Error('Cartesian supports only image.editorial')
        const asset = keys.length
          ? options.assets?.resolveImageSlot(slide, 'image.editorial')
          : null
        if (keys.length && !asset)
          throw Error(
            'image.editorial: no assets manifest was provided; pass --assets assets_manifest.json',
          )
        outline(name, c.frame, 'rectangle', 'bg2')
        if (asset) {
          const pad = b.spacing.imagePadding,
            fitted = fitImageRect(
              x + pad,
              y + pad,
              w - pad * 2,
              h - pad * 2,
              asset.ratio,
              asset.fitPolicy,
            )
          p.addImage(s, named('ImageAsset'), fitted.x, fitted.y, fitted.w, fitted.h, {
            path: asset.path,
            mimeType: asset.mime,
          })
          p.setImageCrop(s, named('ImageAsset'), fitted.crop)
        } else {
          for (const [suffix, begin, end] of [
            ['A', [x, y], [x + w, y + h]],
            ['B', [x, y + h], [x + w, y]],
          ]) {
            const diag = named('ImageDiag' + suffix)
            p.ops.push({
              op: 'add-connector',
              slide: s,
              name: diag,
              kind: 'straight',
              begin: { x: `${begin[0]}in`, y: `${begin[1]}in` },
              end: { x: `${end[0]}in`, y: `${end[1]}in` },
            })
            p.ops.push({
              op: 'set-shape',
              slide: s,
              shape: { name: diag },
              line: { color: color('line'), width: '0.65pt' },
            })
          }
        }
        text(
          named('ImageLabel'),
          [x + 0.3, asset ? y - 0.35 : y + h / 2 - 0.15, w - 0.6, 0.3],
          c.label,
          { ...b.styles.source, alignment: 'center' },
        )
      } else if (c.kind === 'chart') {
        const line = c.chartKind === 'line',
          chart = b.chart,
          font = designFont(design, 'body', chart.fontPt, { color: color('body') })
        p.ops.push({
          op: 'add-chart',
          slide: s,
          name,
          kind: c.chartKind,
          variant: line ? 'markers' : 'clustered',
          x: `${x}in`,
          y: `${y}in`,
          w: `${w}in`,
          h: `${h}in`,
          legend: 'bottom',
          data: c.data,
        })
        p.ops.push({
          op: 'set-chart',
          slide: s,
          shape: { name },
          legend: { position: 'bottom', includeInLayout: false, font },
          axes: [
            {
              axis: 'category',
              line: { color: color('line'), width: '0.5pt' },
              ticks: { font, major: 'none', minor: 'none', labelPosition: 'low' },
            },
            {
              axis: 'value',
              line: { color: color('bg2'), width: '0.5pt' },
              gridlines: { color: color('bg2'), width: '0.5pt' },
              minorGridlines: null,
              ticks: {
                font,
                major: 'none',
                minor: 'none',
                numberFormat: c.numberFormat,
                numberFormatLinked: false,
              },
              ...(Object.keys(c.axis).length ? { scale: c.axis } : {}),
            },
          ],
          series: c.data.series.map((_, i) => ({
            series: i,
            ...(!line
              ? {
                  fill: {
                    type: i ? 'none' : 'solid',
                    ...(i ? {} : { color: color('chartPrimary') }),
                  },
                  invertIfNegative: false,
                }
              : {}),
            line: {
              color: color(i ? 'line' : line ? 'ink' : 'chartPrimary'),
              width: `${i ? chart.comparisonWidthPt : chart.lineWidthPt}pt`,
              ...(i ? { dash: 'dash' } : {}),
            },
            ...(line
              ? {
                  smooth: false,
                  marker: {
                    symbol: 'circle',
                    size: 4,
                    fill: color(i ? 'accent' : 'ink'),
                    line: color('bg'),
                  },
                }
              : {}),
          })),
        })
      } else if (c.kind === 'exhibit') {
        renderCartesianExhibit({ p, s, c, design, text, named })
      } else throw Error(`Unregistered Cartesian component ${c.kind}`)
    }
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
