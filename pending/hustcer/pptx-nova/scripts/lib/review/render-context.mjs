import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

function validDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value) || value.startsWith('0000-'))
    return false
  const date = new Date(`${value}T00:00:00Z`)
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
}

export function calendarDate(now = new Date()) {
  return `${String(now.getFullYear()).padStart(4, '0')}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

export function renderContextForDate(fieldDate = process.env.XDOC_FIELD_DATE || calendarDate()) {
  if (!validDate(fieldDate))
    throw new Error('Render field date must be a valid Gregorian YYYY-MM-DD date')
  return { schemaVersion: 'xdoc-render-context/v1', fieldDate }
}

export function verifyRenderContext(report, expected = renderContextForDate()) {
  const context = report?.renderContext
  if (
    context?.schemaVersion !== 'xdoc-render-context/v1' ||
    context.fieldDate !== expected.fieldDate ||
    context.authorizationClock !== 'independent' ||
    context.bitmapCacheBinding !== 'pdf-sha256'
  ) {
    throw new Error(
      'Rendering evidence does not match this workflow calendar and PDF-bound cache contract',
    )
  }
  return context
}

// Persist the calendar once for the whole workflow, including child processes
// and resume/finalize. A conflicting override must not silently reuse evidence.
export function ensureRenderContext(runDir, { env = process.env, now = new Date() } = {}) {
  mkdirSync(runDir, { recursive: true })
  const path = join(runDir, 'render-context.json')
  const requested = env.XDOC_FIELD_DATE
  let context
  if (existsSync(path)) {
    context = JSON.parse(readFileSync(path, 'utf8'))
    if (context?.schemaVersion !== 'xdoc-render-context/v1' || !validDate(context.fieldDate)) {
      throw new Error(`Invalid persisted render context: ${path}`)
    }
    if (requested && requested !== context.fieldDate) {
      throw new Error(
        `Render date conflicts with this run's evidence (${context.fieldDate}); use a new run directory`,
      )
    }
  } else {
    context = renderContextForDate(requested || calendarDate(now))
    writeFileSync(path, `${JSON.stringify(context, null, 2)}\n`, { flag: 'wx' })
  }
  env.XDOC_FIELD_DATE = context.fieldDate
  return context
}
