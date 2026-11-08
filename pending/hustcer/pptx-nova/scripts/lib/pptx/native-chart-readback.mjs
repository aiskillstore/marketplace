// Native caches supplement xdoc JSON, which can omit combo series and XY/bubble details.
import { readPptxPackage } from './pptx-package.mjs'

const C = new Set([
  'http://schemas.openxmlformats.org/drawingml/2006/chart',
  'http://purl.oclc.org/ooxml/drawingml/chart',
])
const CX = 'http://schemas.microsoft.com/office/drawing/2014/chartex'
const R = new Set([
  'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
  'http://purl.oclc.org/ooxml/officeDocument/relationships',
])
const attr = (node, name) => node?.attrs.find((a) => a.local === name && !a.uri)?.value
const children = (node, name) =>
  (node?.children ?? []).filter((n) => n.local === name && (C.has(n.uri) || n.uri === CX))
const child = (node, name) => children(node, name)[0]
const all = (node) => (node ? [node, ...node.children.flatMap(all)] : [])
const text = (node) => (node ? node.text + node.children.map(text).join('') : '')
const val = (node, name) => attr(child(node, name), 'val')

function points(node) {
  const container = all(node).find((n) =>
    ['strCache', 'numCache', 'strLit', 'numLit', 'lvl'].includes(n.local),
  )
  if (!container) throw Error('Native chart cache is missing')
  const count = Number(attr(container, 'ptCount') ?? val(container, 'ptCount'))
  const rows = children(container, 'pt').sort(
    (a, b) => Number(attr(a, 'idx')) - Number(attr(b, 'idx')),
  )
  if (
    !Number.isInteger(count) ||
    rows.length !== count ||
    rows.some((n, i) => Number(attr(n, 'idx')) !== i)
  )
    throw Error('Native chart cache is sparse or inconsistent')
  return rows.map((n) => (child(n, 'v') ? text(child(n, 'v')) : text(n)))
}
const numbers = (node) =>
  points(node).map((value) => {
    if (!value.trim() || !Number.isFinite(Number(value)))
      throw Error('Invalid native numeric cache')
    return Number(value)
  })

function classicKind(group) {
  const types = {
    lineChart: 'line',
    line3DChart: 'line-3d',
    areaChart: 'area',
    area3DChart: 'area-3d',
    pieChart: 'pie',
    pie3DChart: 'pie-3d',
    doughnutChart: 'doughnut',
    scatterChart: 'scatter',
    bubbleChart: 'bubble',
    radarChart: 'radar',
    surfaceChart: 'surface',
    surface3DChart: 'surface-3d',
  }
  if (['barChart', 'bar3DChart'].includes(group.local))
    return (
      (val(group, 'barDir') === 'bar' ? 'bar' : 'column') +
      (group.local === 'bar3DChart' ? '-3d' : '')
    )
  return types[group.local]
}

function classicChart(root) {
  const plot = all(root).find((n) => C.has(n.uri) && n.local === 'plotArea')
  const groups = (plot?.children ?? []).filter((n) => C.has(n.uri) && classicKind(n))
  if (!groups.length) throw Error('Unrecognized native chart family')
  const firstAxes = children(groups[0], 'axId')
    .map((n) => attr(n, 'val'))
    .join(',')
  const series = groups
    .flatMap((group) =>
      children(group, 'ser').map((ser) => {
        const xy = child(ser, 'xVal')
        const row = {
          index: Number(val(ser, 'idx')),
          kind: classicKind(group),
          secondaryAxis:
            children(group, 'axId')
              .map((n) => attr(n, 'val'))
              .join(',') !== firstAxes,
          name: all(child(ser, 'tx')).some((n) => n.local === 'pt')
            ? points(child(ser, 'tx'))[0]
            : text(child(child(ser, 'tx'), 'v')),
        }
        if (xy) {
          const xs = numbers(xy),
            ys = numbers(child(ser, 'yVal'))
          const sizes = child(ser, 'bubbleSize') ? numbers(child(ser, 'bubbleSize')) : null
          if (xs.length !== ys.length || (sizes && sizes.length !== xs.length))
            throw Error('Native XY cache lengths differ')
          row.points = xs.map((x, i) => ({ x, y: ys[i], ...(sizes ? { size: sizes[i] } : {}) }))
        } else {
          row.categories = points(child(ser, 'cat'))
          row.values = numbers(child(ser, 'val'))
        }
        return row
      }),
    )
    .sort((a, b) => a.index - b.index)
  if (series.some((s, i) => s.index !== i)) throw Error('Native series indices changed')
  return { kind: groups.length > 1 ? 'combo' : classicKind(groups[0]), series }
}

function extendedChart(root) {
  const data = children(child(root, 'chartData'), 'data').map((n) => ({
    id: attr(n, 'id'),
    dimensions: n.children
      .filter((d) => d.uri === CX && ['strDim', 'numDim'].includes(d.local))
      .map((d) => ({
        type: attr(d, 'type'),
        numeric: d.local === 'numDim',
        levels: children(d, 'lvl').map((level) =>
          d.local === 'numDim' ? numbers(level) : points(level),
        ),
      })),
  }))
  const series = all(child(root, 'chart'))
    .filter((n) => n.uri === CX && n.local === 'series')
    .map((n) => ({
      name: text(child(n, 'tx')),
      layout: attr(n, 'layoutId'),
      dataId: val(n, 'dataId'),
      subtotals: all(child(n, 'layoutPr'))
        .filter((n) => n.local === 'idx')
        .map((n) => Number(attr(n, 'val'))),
    }))
  return { kind: series[0]?.layout, data, series }
}

export function readNativeCharts(path) {
  const pkg = readPptxPackage(path)
  return pkg.slides().flatMap((slide) =>
    all(pkg.partTree(slide.part))
      .filter((n) => n.local === 'graphicFrame')
      .map((frame) => {
        const refs = all(frame).filter((n) => (C.has(n.uri) || n.uri === CX) && n.local === 'chart')
        if (!refs.length) return null
        if (refs.length !== 1) throw Error('Ambiguous native chart reference')
        const ref = refs[0],
          id = ref.attrs.find((a) => a.local === 'id' && R.has(a.uri))?.value
        const root = pkg.partTree(pkg.relatedPart(slide.part, id))
        const name = attr(
          all(frame).find((n) => n.local === 'cNvPr'),
          'name',
        )
        return {
          slide: slide.slide - 1,
          name,
          ...(root.uri === CX ? extendedChart(root) : classicChart(root)),
        }
      })
      .filter(Boolean),
  )
}

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
export function nativeChartMatches(op, actual) {
  if (!actual) return false
  if (!op.dataEx) {
    if (actual.kind !== op.kind || actual.series.length !== op.data?.series?.length) return false
    return op.data.series.every((series, i) => {
      const read = actual.series[i]
      return (
        read.name === series.name &&
        (op.kind !== 'combo' ||
          (read.kind === series.kind && read.secondaryAxis === (series.secondaryAxis === true))) &&
        (series.points
          ? same(read.points, series.points)
          : same(read.categories, op.data.categories) && same(read.values, series.values))
      )
    })
  }
  // ChartEx cache dimensions preserve source rows; type-specific semantics are compared below.
  const q = op.dataEx
  const layouts = { 'box-whisker': 'boxWhisker', histogram: 'clusteredColumn' }
  if (actual.kind !== (layouts[op.kind] ?? op.kind)) return false
  const count = q.series?.length ?? 1
  if (
    actual.series.length !== count ||
    actual.data.length !== count ||
    actual.series.some((s) => s.layout !== actual.kind)
  )
    return false
  const firstData = actual.data.find((d) => d.id === actual.series[0].dataId)
  const dims = firstData?.dimensions ?? []
  const cats = dims.find((d) => !d.numeric)?.levels?.[0]
  const values = dims.find((d) => d.numeric)?.levels?.[0]
  if (q.points || q.stages) {
    const rows = q.points ?? q.stages
    if (
      !same(
        cats,
        rows.map((r) => r.label),
      ) ||
      !same(
        values,
        rows.map((r) => r.value),
      )
    )
      return false
    if (q.points)
      return same(
        actual.series[0]?.subtotals,
        q.points.flatMap((p, i) => (['total', 'subtotal'].includes(p.kind) ? [i] : [])),
      )
    return true
  }
  if (q.values) return same(values, q.values)
  if (q.nodes) {
    const byId = new Map(q.nodes.map((n) => [n.id, n]))
    if (byId.size !== q.nodes.length) return false
    const leaves = q.nodes.filter((n) => !q.nodes.some((other) => other.parent === n.id))
    const paths = leaves.map((leaf) => {
      const path = [],
        seen = new Set()
      for (let node = leaf; node; node = byId.get(node.parent)) {
        if (seen.has(node.id) || (node.parent && !byId.has(node.parent))) return null
        seen.add(node.id)
        path.push(node.label)
      }
      return path
    })
    if (paths.some((p) => !p)) return false
    const depth = Math.max(...paths.map((p) => p.length))
    const levels = Array.from({ length: depth }, (_, i) => paths.map((p) => p[i] ?? ''))
    return (
      same(dims.find((d) => !d.numeric)?.levels, levels) &&
      same(
        values,
        leaves.map((n) => n.value),
      )
    )
  }
  if (q.series)
    return q.series.every((series, i) => {
      const read = actual.series[i],
        data = actual.data.find((d) => d.id === read.dataId)
      const dimensions = data?.dimensions ?? []
      const categories = series.categories ?? series.values.map((_, i) => String(i + 1))
      return (
        read.name === series.name &&
        same(dimensions.find((d) => !d.numeric)?.levels[0], categories) &&
        same(dimensions.find((d) => d.numeric)?.levels[0], series.values)
      )
    })
  return false
}
