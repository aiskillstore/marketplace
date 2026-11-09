import { existsSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

// The SKILL's global guidance stores the capability probe as
// xdoc-capabilities.json inside a freshly created run directory before any
// runner is invoked. Every runner therefore accepts a missing directory, an
// empty directory, or a directory holding only that probe artifact — anything
// else is run reuse and must fail closed.
const PRE_PROBE_ALLOWED_ENTRIES = new Set(['xdoc-capabilities.json'])

function inspectRunDir(runDir) {
  const allowedEntries = [...PRE_PROBE_ALLOWED_ENTRIES].sort()
  if (!existsSync(runDir)) {
    return {
      status: 'missing',
      allowedEntries,
      detectedEntries: [],
      unexpectedEntries: [],
      capabilityPath: join(runDir, 'xdoc-capabilities.json'),
    }
  }
  if (!statSync(runDir).isDirectory()) {
    return {
      status: 'not-directory',
      allowedEntries,
      detectedEntries: [],
      unexpectedEntries: [],
      capabilityPath: join(runDir, 'xdoc-capabilities.json'),
    }
  }
  const detectedEntries = readdirSync(runDir).sort()
  const unexpectedEntries = detectedEntries.filter((name) => !PRE_PROBE_ALLOWED_ENTRIES.has(name))
  const capabilityPath = join(runDir, 'xdoc-capabilities.json')
  const capabilityIsInvalid = existsSync(capabilityPath) && !statSync(capabilityPath).isFile()
  return {
    status:
      unexpectedEntries.length > 0
        ? 'unexpected-entries'
        : capabilityIsInvalid
          ? 'invalid-capability-artifact'
          : 'fresh',
    allowedEntries,
    detectedEntries,
    unexpectedEntries,
    capabilityPath,
  }
}

function formatEntries(entries) {
  return entries.length > 0 ? entries.join(', ') : '(none)'
}

function runDirRecoveryMessage(runDir, inspection) {
  return [
    `run directory is not a fresh runner target: ${runDir}`,
    `allowed initial entries: ${formatEntries(inspection.allowedEntries)} (the directory may also be absent or empty)`,
    `detected entries: ${formatEntries(inspection.detectedEntries)}`,
    'safe recovery: keep this directory unchanged as audit evidence and retry with a new --run-dir; keep prompt text and probe stdout outside the run directory, then pass them through supported input flags such as --prompt-file',
  ].join('; ')
}

export function isNewOrPreProbedRunDir(runDir) {
  return ['missing', 'fresh'].includes(inspectRunDir(runDir).status)
}

export function assertNewOrPreProbedRunDir(runDir) {
  const inspection = inspectRunDir(runDir)
  if (['missing', 'fresh'].includes(inspection.status)) return
  const detail =
    inspection.status === 'not-directory'
      ? 'the path exists but is not a directory'
      : inspection.status === 'invalid-capability-artifact'
        ? `the allowed capability artifact is not a file: ${inspection.capabilityPath}`
        : `unexpected entries: ${formatEntries(inspection.unexpectedEntries)}`
  throw new Error(`${runDirRecoveryMessage(runDir, inspection)}; detail: ${detail}`)
}
