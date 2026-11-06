const CHART_EX_KINDS = new Set([
  'waterfall',
  'funnel',
  'histogram',
  'pareto',
  'treemap',
  'sunburst',
  'box-whisker',
  'region-map',
])
const WATERFALL_POINT_KINDS = new Set(['increase', 'decrease', 'subtotal', 'total'])
const SCATTER_KINDS = new Set(['scatter', 'bubble', 'bubble-3d'])
const PIE_KINDS = new Set(['pie', 'pie-3d', 'doughnut'])

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function hasText(value) {
  return typeof value === 'string' && value.trim().length > 0
}

function numericLike(value) {
  if (typeof value === 'number') return Number.isFinite(value)
  return typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))
}

function normalizeKind(value) {
  return typeof value === 'string' ? value : ''
}

function inferChartExKind(data) {
  if (!isPlainObject(data)) return ''
  if (Array.isArray(data.points)) return 'waterfall'
  if (Array.isArray(data.stages)) return 'funnel'
  if (Array.isArray(data.values)) return 'histogram'
  if (Array.isArray(data.series)) return 'box-whisker'
  if (Array.isArray(data.nodes)) {
    return normalizeKind(data.kind)
  }
  return ''
}

export function chartDataOf(op) {
  return op?.dataEx ?? op?.chart?.dataEx ?? op?.data ?? op?.chart?.data ?? null
}

export function chartSourceOf(intent, op) {
  const scoped = intent?.chart
  const data = chartDataOf(op)
  return (
    op?.source ??
    op?.dataSource ??
    data?.source ??
    scoped?.semanticSource ??
    scoped?.source ??
    scoped?.dataSource ??
    intent?.source ??
    null
  )
}

export function normalizeChartSemantics(op, intent = null) {
  const chartExData = op?.dataEx ?? op?.chart?.dataEx ?? null
  const classicData = op?.data ?? op?.chart?.data ?? null
  const data = chartExData ?? classicData
  const explicitKind = op?.kind ?? intent?.chart?.kind ?? chartExData?.kind
  const kind = normalizeKind(explicitKind) || (chartExData ? inferChartExKind(chartExData) : '')
  const inputErrors = []
  if (
    explicitKind !== undefined &&
    (typeof explicitKind !== 'string' || !/^[a-z]+(?:-[a-z0-9]+)*$/.test(explicitKind))
  ) {
    add(inputErrors, 'chart-kind-invalid', 'Chart kind must use its canonical value')
  }
  if (isPlainObject(chartExData)) {
    for (const key of ['chartKind', 'type']) {
      if (Object.hasOwn(chartExData, key)) {
        add(inputErrors, 'chart-kind-retired-field', `dataEx.${key} is not supported; use kind`)
      }
    }
    if (Object.hasOwn(chartExData, 'kind') && chartExData.kind !== kind) {
      add(inputErrors, 'chart-kind-mismatch', 'dataEx.kind must match the selected chart kind')
    }
    if (
      op?.op === 'set-chart-data' &&
      Array.isArray(chartExData.nodes) &&
      !Object.hasOwn(chartExData, 'kind')
    ) {
      add(inputErrors, 'chart-kind-missing', 'Hierarchy set-chart-data requires dataEx.kind')
    }
  }
  return {
    kind,
    dialect: chartExData ? 'chartex' : classicData ? 'classic' : 'unknown',
    data,
    source: chartSourceOf(intent, op),
    hasClassicData: classicData !== null && classicData !== undefined,
    hasChartExData: chartExData !== null && chartExData !== undefined,
    inputErrors,
  }
}

function add(target, code, message, details = {}) {
  target.push({ code, message, ...details })
}

function validateLabelValueRows(rows, rowName, errors) {
  if (!Array.isArray(rows) || rows.length === 0) {
    add(
      errors,
      `chart-ex-${rowName}-missing`,
      `ChartEx ${rowName}[] must contain at least one item`,
    )
    return
  }
  rows.forEach((row, index) => {
    if (!isPlainObject(row)) {
      add(errors, `chart-ex-${rowName}-invalid`, `${rowName}[${index}] must be an object`)
      return
    }
    if (!hasText(row.label)) {
      add(errors, 'chart-ex-label-missing', `${rowName}[${index}] must provide a non-empty label`)
    }
    if (!numericLike(row.value)) {
      add(errors, 'chart-ex-value-nonnumeric', `${rowName}[${index}].value must be numeric`)
    }
  })
}

function validateHierarchy(data, kind, errors) {
  const nodes = data?.nodes
  if (!Array.isArray(nodes) || nodes.length === 0) {
    add(errors, 'chart-ex-nodes-missing', `${kind || 'hierarchy'} dataEx.nodes[] must not be empty`)
    return
  }
  const ids = new Set()
  const parentById = new Map()
  nodes.forEach((node, index) => {
    if (!isPlainObject(node)) {
      add(errors, 'chart-ex-node-invalid', `nodes[${index}] must be an object`)
      return
    }
    if (!hasText(node.id)) {
      add(errors, 'chart-ex-node-id-missing', `nodes[${index}] must provide a non-empty id`)
    } else if (ids.has(node.id)) {
      add(errors, 'chart-ex-node-id-duplicate', `nodes[${index}] duplicates id "${node.id}"`)
    } else {
      ids.add(node.id)
      parentById.set(node.id, hasText(node.parent) ? node.parent : null)
    }
    if (!hasText(node.label)) {
      add(errors, 'chart-ex-node-label-missing', `nodes[${index}] must provide a non-empty label`)
    }
    if (!numericLike(node.value)) {
      add(errors, 'chart-ex-node-value-nonnumeric', `nodes[${index}].value must be numeric`)
    }
  })
  for (const [id, parent] of parentById) {
    if (!parent) continue
    if (parent === id) {
      add(errors, 'chart-ex-node-parent-self', `node "${id}" cannot reference itself as parent`)
    } else if (!ids.has(parent)) {
      add(
        errors,
        'chart-ex-node-parent-missing',
        `node "${id}" references unknown parent "${parent}"`,
      )
    }
  }
  for (const id of ids) {
    const seen = new Set([id])
    let parent = parentById.get(id)
    while (parent && ids.has(parent)) {
      if (seen.has(parent)) {
        add(errors, 'chart-ex-node-parent-cycle', `node "${id}" participates in a parent cycle`)
        break
      }
      seen.add(parent)
      parent = parentById.get(parent)
    }
  }
}

function validateChartEx(semantics, errors, warnings) {
  const { data, kind } = semantics
  if (!isPlainObject(data)) {
    add(errors, 'chart-ex-data-invalid', 'ChartEx dataEx must be an object')
    return
  }
  if (!kind) {
    add(
      errors,
      'chart-ex-kind-missing',
      'ChartEx data kind cannot be inferred; disclose chart kind',
    )
    return
  }
  if (!CHART_EX_KINDS.has(kind)) {
    add(errors, 'chart-ex-kind-unsupported', `ChartEx dataEx is not supported for kind "${kind}"`)
    return
  }
  if (kind === 'waterfall') {
    validateLabelValueRows(data.points, 'points', errors)
    if (Array.isArray(data.points)) {
      data.points.forEach((point, index) => {
        if (
          isPlainObject(point) &&
          point.kind !== undefined &&
          !WATERFALL_POINT_KINDS.has(String(point.kind))
        ) {
          add(
            errors,
            'chart-ex-waterfall-kind-invalid',
            `points[${index}].kind must be increase, decrease, subtotal, or total`,
          )
        }
      })
    }
    return
  }
  if (kind === 'funnel') {
    validateLabelValueRows(data.stages, 'stages', errors)
    return
  }
  if (kind === 'histogram' || kind === 'pareto') {
    if (!Array.isArray(data.values) || data.values.length === 0) {
      add(errors, 'chart-ex-values-missing', `${kind} dataEx.values[] must not be empty`)
    } else {
      data.values.forEach((value, index) => {
        if (!numericLike(value)) {
          add(errors, 'chart-ex-value-nonnumeric', `values[${index}] must be numeric`)
        }
      })
    }
    return
  }
  if (kind === 'treemap' || kind === 'sunburst' || kind === 'region-map') {
    validateHierarchy(data, kind, errors)
    return
  }
  if (kind === 'box-whisker') {
    const series = data.series
    if (!Array.isArray(series) || series.length === 0) {
      add(errors, 'chart-ex-series-missing', 'box-whisker dataEx.series[] must not be empty')
      return
    }
    series.forEach((item, index) => {
      if (!isPlainObject(item)) {
        add(errors, 'chart-ex-series-invalid', `series[${index}] must be an object`)
        return
      }
      if (!hasText(item.name)) {
        add(errors, 'chart-series-name-missing', `series[${index}] must provide a non-empty name`)
      }
      if (!Array.isArray(item.values) || item.values.length === 0) {
        add(errors, 'chart-ex-series-values-missing', `series[${index}].values[] must not be empty`)
      } else {
        item.values.forEach((value, valueIndex) => {
          if (!numericLike(value)) {
            add(
              errors,
              'chart-value-nonnumeric',
              `series[${index}].values[${valueIndex}] is not numeric`,
            )
          }
        })
      }
      if (item.categories !== undefined && !Array.isArray(item.categories)) {
        add(errors, 'chart-ex-categories-invalid', `series[${index}].categories must be an array`)
      } else if (
        Array.isArray(item.categories) &&
        Array.isArray(item.values) &&
        item.categories.length !== item.values.length
      ) {
        add(
          errors,
          'chart-series-category-mismatch',
          `series[${index}] has ${item.values.length} value(s), categories has ${item.categories.length}`,
        )
      }
    })
    return
  }
  add(
    warnings,
    'chart-ex-data-not-validated',
    `no ChartEx validator is registered for kind "${kind}"`,
  )
}

function seriesValues(series) {
  if (!isPlainObject(series)) return []
  if (Array.isArray(series.values)) return series.values
  if (Array.isArray(series.points)) return series.points
  return []
}

function validateClassic(semantics, errors, warnings) {
  const { data, kind } = semantics
  if (!isPlainObject(data)) {
    add(errors, 'chart-data-invalid', 'chart data must be an object')
    return
  }
  const series = Array.isArray(data.series) ? data.series : []
  const categories = Array.isArray(data.categories) ? data.categories : null
  if (series.length === 0 && kind !== 'stock') {
    add(errors, 'chart-series-missing', 'chart must disclose at least one data series')
  }
  if (categories && series.length > 0) {
    series.forEach((item, index) => {
      if (Array.isArray(item?.values) && item.values.length !== categories.length) {
        add(
          errors,
          'chart-series-category-mismatch',
          `series[${index}] has ${item.values.length} value(s), categories has ${categories.length}`,
        )
      }
    })
  }
  if (SCATTER_KINDS.has(kind)) {
    series.forEach((item, seriesIndex) => {
      if (!Array.isArray(item?.points)) {
        add(
          errors,
          'chart-points-required',
          `${kind} series[${seriesIndex}] must use points[] instead of categories/values`,
        )
        return
      }
      const fields = kind.startsWith('bubble') ? ['x', 'y', 'size'] : ['x', 'y']
      item.points.forEach((point, pointIndex) => {
        if (!isPlainObject(point) || !fields.every((field) => numericLike(point[field]))) {
          add(
            errors,
            'chart-point-nonnumeric',
            `${kind} series[${seriesIndex}].points[${pointIndex}] must disclose numeric ${fields.join('/')}`,
          )
        }
      })
    })
  }
  if (PIE_KINDS.has(kind) && series.length > 1) {
    add(warnings, 'chart-pie-multi-series', `${kind} usually expects one series`)
  }
  if (kind === 'stock') {
    const length = categories?.length ?? null
    for (const field of ['open', 'high', 'low', 'close']) {
      if (field === 'open' && !Array.isArray(data.open)) continue
      if (!Array.isArray(data[field])) {
        add(errors, 'chart-stock-field-missing', `stock chart must disclose ${field}[]`)
      } else if (Number.isInteger(length) && data[field].length !== length) {
        add(
          errors,
          'chart-stock-field-length-mismatch',
          `stock ${field}[] has ${data[field].length} value(s), categories has ${length}`,
        )
      }
    }
  }
  series.forEach((item, seriesIndex) => {
    if (!hasText(item?.name)) {
      add(warnings, 'chart-series-name-missing', `series[${seriesIndex}] has no readable name`)
    }
    const values = seriesValues(item)
    if (values.length === 0) {
      add(warnings, 'chart-series-empty', `series[${seriesIndex}] has no values`)
    }
    values.forEach((value, valueIndex) => {
      if (isPlainObject(value)) return
      if (typeof value === 'string' && value.includes('%')) {
        add(
          warnings,
          'chart-percent-string-value',
          `series[${seriesIndex}] value[${valueIndex}] is a percent string`,
        )
      } else if (!numericLike(value)) {
        add(
          errors,
          'chart-value-nonnumeric',
          `series[${seriesIndex}] value[${valueIndex}] is not numeric`,
        )
      }
    })
  })
  if (kind === 'combo') {
    for (const [index, item] of series.entries()) {
      if (item && (Object.hasOwn(item, 'chartKind') || Object.hasOwn(item, 'type'))) {
        add(errors, 'chart-kind-retired-field', `series[${index}] must use kind`)
      }
      if (!['column', 'line', 'area'].includes(item?.kind)) {
        add(
          errors,
          'chart-combo-kind-invalid',
          `series[${index}].kind must be column, line, or area`,
        )
      }
    }
    const kinds = new Set(series.map((item) => item?.kind).filter(Boolean))
    const hasSecondaryAxis = series.some((item) => item?.secondaryAxis === true)
    if (kinds.size < 2 && !hasSecondaryAxis) {
      add(
        errors,
        'chart-combo-not-combo',
        'combo chart needs either multiple series kinds or secondaryAxis=true',
      )
    }
  }
}

export function validateChartSemantics(semantics) {
  const errors = [...(semantics.inputErrors ?? [])]
  const warnings = []
  if (semantics.hasClassicData && semantics.hasChartExData) {
    add(errors, 'chart-data-ambiguous', 'chart op must not disclose both data and dataEx')
  }
  if (!semantics.data) {
    add(warnings, 'chart-data-missing', 'chart op has no disclosed data or dataEx object')
    return { errors, warnings }
  }
  if (semantics.dialect === 'chartex') {
    validateChartEx(semantics, errors, warnings)
  } else {
    validateClassic(semantics, errors, warnings)
  }
  return { errors, warnings }
}

export { CHART_EX_KINDS }
