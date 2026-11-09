import { existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { dirname } from 'node:path'

export function ensureWritableOutput(path, overwrite = false, label = 'output') {
  if (existsSync(path) && !overwrite) {
    throw new Error(
      `${label} already exists: ${path}; use --overwrite only for a current-run artifact`,
    )
  }
}

export function ensureWritableOutputs(paths, overwrite = false) {
  if (overwrite) return
  const existing = paths.filter((path) => existsSync(path))
  if (existing.length > 0) {
    throw new Error(
      `current-run outputs already exist: ${existing.join(', ')}; use --overwrite only for current-run artifacts`,
    )
  }
}

export function writeJsonOutput(path, value, { overwrite = false, label = 'output' } = {}) {
  ensureWritableOutput(path, overwrite, label)
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}
