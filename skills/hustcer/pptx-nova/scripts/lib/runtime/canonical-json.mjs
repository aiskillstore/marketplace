import { createHash } from 'node:crypto'

function isPlainObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  const prototype = Object.getPrototypeOf(value)
  return prototype === Object.prototype || prototype === null
}

function compareUnicodeCodePoints(left, right) {
  const leftPoints = Array.from(left, (character) => character.codePointAt(0))
  const rightPoints = Array.from(right, (character) => character.codePointAt(0))
  const length = Math.min(leftPoints.length, rightPoints.length)
  for (let index = 0; index < length; index += 1) {
    if (leftPoints[index] !== rightPoints[index]) return leftPoints[index] - rightPoints[index]
  }
  return leftPoints.length - rightPoints.length
}

function serialize(value, path) {
  if (value === null) return 'null'
  if (typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value)
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || Object.is(value, -0)) {
      throw new TypeError(`canonicalJsonV1 rejects non-finite numbers and -0 at ${path}`)
    }
    return JSON.stringify(value)
  }
  if (Array.isArray(value)) {
    const items = Array.from({ length: value.length }, (_, index) =>
      serialize(value[index], `${path}[${index}]`),
    )
    return `[${items.join(',')}]`
  }
  if (!isPlainObject(value)) {
    throw new TypeError(`canonicalJsonV1 only accepts JSON values at ${path}`)
  }
  const fields = []
  for (const key of Object.keys(value).sort(compareUnicodeCodePoints)) {
    if (value[key] === undefined) {
      throw new TypeError(`canonicalJsonV1 rejects undefined at ${path}.${key}`)
    }
    fields.push(`${JSON.stringify(key)}:${serialize(value[key], `${path}.${key}`)}`)
  }
  return `{${fields.join(',')}}`
}

export function canonicalJsonV1(value) {
  return serialize(value, '$')
}

export function canonicalSha256V1(value) {
  return createHash('sha256').update(canonicalJsonV1(value), 'utf8').digest('hex')
}
