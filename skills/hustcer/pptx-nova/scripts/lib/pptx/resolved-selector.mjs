// Runtime decoder for the normalized selector evidence consumed by edit gates.
// IDs are local to a slide at the operation; the echo is not an authored patch.
const own = (value, key) => Object.hasOwn(value, key)
const integer = (value) => Number.isSafeInteger(value)
const index = (value) => integer(value) && value >= 0
const shapeId = (value) => index(value) && value <= 0xffffffff
const string = (value) => typeof value === 'string'

function requireValue(condition, path) {
  if (!condition) throw new TypeError(`Invalid resolved selector evidence at ${path}`)
}

function object(value, required, optional, path) {
  requireValue(value !== null && typeof value === 'object' && !Array.isArray(value), path)
  requireValue(
    required.every((key) => own(value, key)),
    path,
  )
  requireValue(
    Object.keys(value).every((key) => required.includes(key) || optional.includes(key)),
    path,
  )
}

function placeholder(value, path) {
  object(value, ['type'], ['idx'], path)
  requireValue(string(value.type), `${path}.type`)
  if (own(value, 'idx')) requireValue(index(value.idx), `${path}.idx`)
}

function query(value) {
  object(value, [], ['nameRegex', 'textRegex', 'placeholder', 'bboxNear'], 'input.query')
  requireValue(Object.keys(value).length > 0, 'input.query')
  for (const key of ['nameRegex', 'textRegex']) {
    if (own(value, key)) requireValue(string(value[key]), `input.query.${key}`)
  }
  if (own(value, 'placeholder') && !string(value.placeholder)) {
    placeholder(value.placeholder, 'input.query.placeholder')
  }
  if (own(value, 'bboxNear')) {
    const bbox = value.bboxNear
    object(bbox, ['xEmu', 'yEmu'], ['radiusEmu'], 'input.query.bboxNear')
    requireValue(integer(bbox.xEmu) && integer(bbox.yEmu), 'input.query.bboxNear')
    if (own(bbox, 'radiusEmu'))
      requireValue(index(bbox.radiusEmu), 'input.query.bboxNear.radiusEmu')
  }
}

/**
 * @typedef {{kind:'shape', slide:number, id:number, shapeType:string, name?:string,
 * contentKind?:string, placeholder?:{type:string, idx?:number}}} ResolvedShape
 * @typedef {{field:string, input:{id:number}|{name:string}|{placeholder:string,idx?:number}|{query:object},
 * resolved:ResolvedShape}} ResolvedSelector
 */

/** @returns {ResolvedSelector} Throws on missing, mistyped or unknown structural fields. */
export function readResolvedSelector(value) {
  object(value, ['field', 'input', 'resolved'], [], 'selector')
  requireValue(
    string(value.field) && /^(shape|begin\.shape|end\.shape|shapes\[[0-9]+\])$/.test(value.field),
    'field',
  )
  const input = value.input
  object(input, [], ['id', 'name', 'placeholder', 'idx', 'query'], 'input')
  const methods = ['id', 'name', 'placeholder', 'query'].filter((key) => own(input, key))
  requireValue(methods.length === 1, 'input')
  const [method] = methods
  object(input, [method], method === 'placeholder' ? ['idx'] : [], 'input')
  if (method === 'id') requireValue(shapeId(input.id), 'input.id')
  if (method === 'name') requireValue(string(input.name), 'input.name')
  if (method === 'placeholder') {
    requireValue(string(input.placeholder), 'input.placeholder')
    if (own(input, 'idx')) requireValue(index(input.idx), 'input.idx')
  }
  if (method === 'query') query(input.query)
  const resolved = value.resolved
  object(
    resolved,
    ['kind', 'slide', 'id', 'shapeType'],
    ['name', 'contentKind', 'placeholder'],
    'resolved',
  )
  requireValue(resolved.kind === 'shape', 'resolved.kind')
  requireValue(index(resolved.slide), 'resolved.slide')
  requireValue(shapeId(resolved.id), 'resolved.id')
  for (const key of ['shapeType', 'name', 'contentKind']) {
    if (own(resolved, key)) requireValue(string(resolved[key]), `resolved.${key}`)
  }
  if (own(resolved, 'placeholder')) placeholder(resolved.placeholder, 'resolved.placeholder')
  return value
}

/** @returns {ResolvedSelector[]} Validate a canonical op result's selector evidence. */
export function readResolvedSelectors(result) {
  requireValue(Array.isArray(result?.resolvedSelectors), 'resolvedSelectors')
  return result.resolvedSelectors.map(readResolvedSelector)
}
