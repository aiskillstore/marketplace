import { existsSync } from 'node:fs'
import { dirname, isAbsolute, resolve } from 'node:path'

/**
 * Resolve an evidence path without assuming every producer used the same base.
 * New producers should write absolute paths. For legacy relative records we
 * accept either artifact-relative or producer-cwd-relative paths, but fail on
 * ambiguity instead of silently binding the wrong bytes.
 */
export function canonicalEvidencePath(
  value,
  { artifactPath = '', cwd = process.cwd(), mustExist = true } = {},
) {
  if (!String(value ?? '').trim()) return ''
  const raw = String(value)
  if (isAbsolute(raw)) return resolve(raw)

  const candidates = [
    artifactPath ? resolve(dirname(artifactPath), raw) : '',
    cwd ? resolve(cwd, raw) : '',
  ].filter(Boolean)
  const unique = [...new Set(candidates)]
  const existing = unique.filter((path) => existsSync(path))
  if (existing.length > 1) {
    throw new Error(`ambiguous relative evidence path ${raw}: ${existing.join(', ')}`)
  }
  if (existing.length === 1) return existing[0]
  if (mustExist) {
    throw new Error(`relative evidence path does not exist from known bases: ${raw}`)
  }
  return unique[0] ?? resolve(raw)
}

export function canonicalOutputPath(value, cwd = process.cwd()) {
  return value ? resolve(cwd, value) : ''
}
