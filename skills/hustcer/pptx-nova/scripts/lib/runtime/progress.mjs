import { closeSync, openSync, writeSync } from 'node:fs'

const SCHEMA_VERSION = 'pptx-nova-progress/v1'
const VALID_MODES = new Set(['auto', 'jsonl', 'text', 'off'])
const PHASE_BOUNDARY_EVENTS = new Set([
  'runner-start',
  'runner-complete',
  'phase-start',
  'phase-complete',
])

function normalizeMode(mode, jsonOutput) {
  const normalized = String(mode || 'auto')
    .trim()
    .toLowerCase()
  if (!VALID_MODES.has(normalized)) {
    throw new Error(`progress mode must be one of auto|jsonl|text|off: ${mode}`)
  }
  return normalized === 'auto' ? (jsonOutput ? 'jsonl' : 'text') : normalized
}

function progressFd() {
  const configured = Number(process.env.PPTX_NOVA_PROGRESS_FD || 2)
  return Number.isInteger(configured) && (configured === 2 || configured >= 3) ? configured : 2
}

function textLine(event, payload) {
  const fields = Object.entries(payload)
    .filter(
      ([key, value]) =>
        key !== 'schemaVersion' &&
        key !== 'event' &&
        value !== null &&
        value !== undefined &&
        value !== '',
    )
    .map(([key, value]) => `${key}=${JSON.stringify(value)}`)
  return `[pptx-nova] ${event}${fields.length > 0 ? ` ${fields.join(' ')}` : ''}`
}

export function createProgressReporter({ mode = 'auto', jsonOutput = false, context = {} } = {}) {
  const resolvedMode = normalizeMode(mode, jsonOutput)
  const fd = progressFd()
  let fileFd = null
  let filePath = null

  function attachFile(path) {
    if (!path || path === 'none') return
    detachFile()
    fileFd = openSync(path, 'a')
    filePath = path
  }

  function detachFile() {
    if (fileFd === null) return
    try {
      closeSync(fileFd)
    } catch {
      // fd may already be closed by the OS on process teardown
    }
    fileFd = null
    filePath = null
  }

  function emit(event, details = {}) {
    if (resolvedMode === 'off' && fileFd === null) return
    const payload = {
      schemaVersion: SCHEMA_VERSION,
      event,
      timestamp: new Date().toISOString(),
      ...context,
      ...details,
    }
    if (fileFd !== null) {
      try {
        writeSync(fileFd, `${JSON.stringify(payload)}\n`)
      } catch {
        // progress archive failures must never break the run
      }
    }
    if (resolvedMode === 'off') return
    // With an attached archive, stderr carries only single-line phase-boundary
    // summaries; the full event stream lives in the file.
    if (fileFd !== null && !PHASE_BOUNDARY_EVENTS.has(event)) return
    const line =
      fileFd === null && resolvedMode === 'jsonl'
        ? JSON.stringify(payload)
        : textLine(event, payload)
    try {
      writeSync(fd, `${line}\n`)
    } catch {
      if (fd !== 2) writeSync(2, `${line}\n`)
    }
  }

  return {
    emit,
    mode: resolvedMode,
    enabled: resolvedMode !== 'off',
    attachFile,
    detachFile,
    get forwardFd() {
      return fileFd
    },
    get filePath() {
      return filePath
    },
  }
}

export function progressHeartbeatMs() {
  const configured = Number(process.env.PPTX_NOVA_PROGRESS_HEARTBEAT_MS || 15000)
  return Number.isFinite(configured) && configured >= 10 ? configured : 15000
}
