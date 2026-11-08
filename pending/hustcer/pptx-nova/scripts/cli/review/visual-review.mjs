#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { captureVisualBinding, REVIEW_CHECKS } from '../../lib/review/canonical-visual-evidence.mjs'
import { validateDesignReview } from '../../lib/review/design-quality.mjs'

const SCHEMA_VERSION = 'pptx-nova-visual-review/v1'
const BASE_REQUIRED_CHECKS = REVIEW_CHECKS
const MODE_REQUIRED_CHECKS = {
  refurbish: ['targetDeckkitApplied'],
}
const CHECK_ALIASES = new Map([['visualTargetApplied', 'targetDeckkitApplied']])
const KNOWN_CHECKS = new Set([
  ...BASE_REQUIRED_CHECKS,
  ...Object.values(MODE_REQUIRED_CHECKS).flat(),
  ...CHECK_ALIASES.keys(),
])
const ALLOWED_CHECK_STATUSES = new Set(['pass', 'warn', 'fail', 'na'])
const FAIL_SEVERITIES = new Set(['error', 'high', 'fail'])
const WARN_SEVERITIES = new Set(['warning', 'warn', 'medium'])

const usage =
  'Usage:\n' +
  '  node <skill-root>/scripts/cli/review/visual-review.mjs [options]\n\n' +
  'Options:\n' +
  '  --run-dir <path>        Optional run directory. Defaults output to run-dir/visual_review.json.\n' +
  '  --output <path>         Output path. Defaults to visual_review.json in cwd or run-dir.\n' +
  '  --mode <mode>           Workflow mode for context.\n' +
  '  --candidate <path>      Bind the review to the current PPTX (requires --manifest).\n' +
  '  --manifest <path>       Canonical manifest whose exact PNGs were reviewed.\n' +
  '  --design-review <path>  Required for create: slide-specific design_review.json after PNG review.\n' +
  '  --reviewer <name>       reviewer label, e.g. agent or human.\n' +
  '  --slides-reviewed <n>   Number of rendered slides/contact-sheet pages reviewed.\n' +
  '  --contact-sheet <path>  Contact sheet image used for review.\n' +
  '  --previews <path>       Preview PNG directory used for review.\n' +
  '  --vision <path>         Optional vision.json evidence path.\n' +
  '  --layout-final <path>   Optional layout-final.json evidence path.\n' +
  '  --semantic-audit <path> Optional semantic-audit.json evidence path.\n' +
  '  --check <name=status>   Repeatable required check status: pass, warn, fail, or na.\n' +
  '                          In refurbish mode, include targetDeckkitApplied=pass|warn|fail|na.\n' +
  '  --issue <spec>          Repeatable issue: severity:slide:check:message.\n' +
  '  --json                  Print visual_review.json to stdout.\n' +
  '  --help                  Show this help.\n\n' +
  'This helper records the PNG/contact-sheet human or agent visual review as a\n' +
  'structured artifact. It validates review completeness; it does not perform\n' +
  'automatic image understanding.\n'

function parseArgs(argv) {
  const args = {
    runDir: '',
    output: '',
    mode: '',
    reviewer: 'agent',
    slidesReviewed: null,
    contactSheet: '',
    previews: '',
    vision: '',
    layoutFinal: '',
    semanticAudit: '',
    checks: [],
    issues: [],
    json: false,
  }
  const flags = {
    '--run-dir': 'runDir',
    '--output': 'output',
    '--mode': 'mode',
    '--candidate': 'candidate',
    '--manifest': 'manifest',
    '--design-review': 'designReview',
    '--reviewer': 'reviewer',
    '--slides-reviewed': 'slidesReviewed',
    '--contact-sheet': 'contactSheet',
    '--previews': 'previews',
    '--vision': 'vision',
    '--layout-final': 'layoutFinal',
    '--semantic-audit': 'semanticAudit',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--json') {
      args.json = true
      continue
    }
    if (arg === '--check') {
      const value = argv[index + 1]
      if (!value || value.startsWith('--')) throw new Error('--check requires name=status')
      args.checks.push(value)
      index += 1
      continue
    }
    if (arg === '--issue') {
      const value = argv[index + 1]
      if (!value || value.startsWith('--'))
        throw new Error('--issue requires severity:slide:check:message')
      args.issues.push(value)
      index += 1
      continue
    }
    const key = flags[arg]
    const value = argv[index + 1]
    if (!key) throw new Error('Unknown option: ' + arg + '\n\n' + usage)
    if (!value || value.startsWith('--')) throw new Error(arg + ' requires a value')
    args[key] = key === 'slidesReviewed' ? Number(value) : resolve(value)
    if (['mode', 'reviewer'].includes(key)) args[key] = value
    index += 1
  }
  if (args.runDir) args.runDir = resolve(args.runDir)
  if (!args.output) {
    args.output = resolve(args.runDir || '.', 'visual_review.json')
  } else {
    args.output = resolve(args.output)
  }
  return args
}

function issue(target, level, code, message, details = {}) {
  const item = { severity: level, code, message, ...details }
  target[level === 'error' ? 'errors' : 'warnings'].push(item)
}

function existingPath(path) {
  return Boolean(path && existsSync(path))
}

function parseCheck(value) {
  const eq = value.indexOf('=')
  if (eq <= 0) return { name: value, status: 'invalid' }
  const rawName = value.slice(0, eq).trim()
  return {
    name: CHECK_ALIASES.get(rawName) ?? rawName,
    status: value.slice(eq + 1).trim(),
  }
}

function parseIssue(value) {
  const parts = value.split(':')
  const severity = parts.shift() || 'warning'
  const slide = parts.shift() || 'all'
  const check = parts.shift() || 'general'
  const message = parts.join(':').trim()
  return {
    severity,
    slide: slide === 'all' ? null : Number(slide),
    check,
    message: message || value,
  }
}

function readStatus(path) {
  if (!path || !existsSync(path)) return null
  try {
    const json = JSON.parse(readFileSync(path, 'utf8'))
    return json?.status ?? json?.summary?.status ?? null
  } catch {
    return null
  }
}

function requiredChecksFor(mode) {
  const normalizedMode = String(mode || '').toLowerCase()
  return [...BASE_REQUIRED_CHECKS, ...(MODE_REQUIRED_CHECKS[normalizedMode] ?? [])]
}

function buildChecks(rawChecks, report, requiredChecks) {
  const byName = new Map()
  for (const raw of rawChecks) {
    const parsed = parseCheck(raw)
    if (!KNOWN_CHECKS.has(parsed.name)) {
      issue(
        report,
        'warning',
        'visual-review-extra-check',
        'visual review recorded an extra check',
        {
          check: parsed.name,
        },
      )
    }
    if (!ALLOWED_CHECK_STATUSES.has(parsed.status)) {
      issue(
        report,
        'error',
        'visual-review-check-status-invalid',
        'visual review check has invalid status',
        {
          check: parsed.name,
          status: parsed.status,
        },
      )
    }
    byName.set(parsed.name, parsed.status)
  }

  const checks = []
  for (const name of requiredChecks) {
    const status = byName.get(name)
    if (!status) {
      issue(
        report,
        'error',
        'visual-review-check-missing',
        'required visual review check is missing',
        {
          check: name,
        },
      )
      checks.push({ name, status: 'missing' })
    } else {
      checks.push({ name, status })
    }
  }
  for (const [name, status] of byName.entries()) {
    if (!requiredChecks.includes(name)) checks.push({ name, status })
  }
  return checks
}

function makeReport(args) {
  const report = {
    schemaVersion: SCHEMA_VERSION,
    status: 'pass',
    mode: args.mode || null,
    reviewer: args.reviewer,
    artifacts: {
      runDir: args.runDir || null,
      contactSheet: args.contactSheet || null,
      previews: args.previews || null,
      vision: args.vision || null,
      layoutFinal: args.layoutFinal || null,
      semanticAudit: args.semanticAudit || null,
    },
    upstreamStatus: {
      vision: readStatus(args.vision),
      layoutFinal: readStatus(args.layoutFinal),
      semanticAudit: readStatus(args.semanticAudit),
    },
    summary: {
      slidesReviewed: args.slidesReviewed,
      checks: { total: 0, passed: 0, warnings: 0, failed: 0, notApplicable: 0 },
      issueCount: 0,
      errors: 0,
      warnings: 0,
    },
    checks: [],
    issues: [],
    errors: [],
    warnings: [],
  }

  if (!Number.isInteger(args.slidesReviewed) || args.slidesReviewed <= 0) {
    issue(
      report,
      'error',
      'visual-review-slide-count-invalid',
      'slides-reviewed must be a positive integer',
      {
        slidesReviewed: args.slidesReviewed,
      },
    )
  }
  if (!args.contactSheet && !args.previews) {
    issue(
      report,
      'error',
      'visual-review-evidence-missing',
      'provide a contact sheet or preview directory',
    )
  }
  for (const [name, path] of Object.entries(report.artifacts)) {
    if (name === 'runDir') continue
    if (path && !existingPath(path)) {
      issue(
        report,
        'error',
        'visual-review-artifact-missing',
        'referenced visual review artifact does not exist',
        {
          artifact: name,
          path,
        },
      )
    }
  }

  const requiredChecks = requiredChecksFor(args.mode)
  report.policy = {
    requiredChecks,
  }
  report.checks = buildChecks(args.checks, report, requiredChecks)
  for (const check of report.checks) {
    if (check.status === 'pass') report.summary.checks.passed += 1
    else if (check.status === 'warn') {
      report.summary.checks.warnings += 1
      issue(
        report,
        'warning',
        'visual-review-check-warning',
        'visual review check needs disclosure',
        {
          check: check.name,
        },
      )
    } else if (check.status === 'fail') {
      report.summary.checks.failed += 1
      issue(report, 'error', 'visual-review-check-failed', 'visual review check failed', {
        check: check.name,
      })
    } else if (check.status === 'na') {
      report.summary.checks.notApplicable += 1
    }
  }
  report.summary.checks.total = report.checks.length

  report.issues = args.issues.map(parseIssue)
  for (const item of report.issues) {
    const severity = String(item.severity).toLowerCase()
    if (FAIL_SEVERITIES.has(severity)) {
      issue(report, 'error', 'visual-review-issue-failed', item.message, {
        check: item.check,
        slide: item.slide,
        issueSeverity: item.severity,
      })
    } else if (WARN_SEVERITIES.has(severity)) {
      issue(report, 'warning', 'visual-review-issue-warning', item.message, {
        check: item.check,
        slide: item.slide,
        issueSeverity: item.severity,
      })
    }
  }
  report.summary.issueCount = report.issues.length

  report.summary.errors = report.errors.length
  report.summary.warnings = report.warnings.length
  report.status = report.errors.length > 0 ? 'fail' : report.warnings.length > 0 ? 'warn' : 'pass'
  report.slidesReviewed = report.summary.slidesReviewed
  report.checkSummary = report.summary.checks
  report.issueCount = report.summary.issueCount
  report.errorCount = report.summary.errors
  report.warningCount = report.summary.warnings
  if (args.candidate || args.manifest) {
    if (!args.candidate || !args.manifest)
      throw new Error('--candidate and --manifest must be supplied together')
    report.binding = captureVisualBinding(args.manifest, args.candidate)
    if (args.slidesReviewed !== report.binding.slideCount)
      throw new Error('review must cover every candidate slide')
    report.artifacts.candidate = args.candidate
    report.artifacts.manifest = args.manifest
  }
  if (args.mode === 'create') {
    report.designReview = args.designReview
      ? JSON.parse(readFileSync(args.designReview, 'utf8'))
      : null
    for (const message of validateDesignReview(report.designReview, report.binding))
      issue(report, 'error', 'design-review-incomplete', message)
    report.summary.errors = report.errors.length
    report.errorCount = report.summary.errors
    if (report.errors.length) report.status = 'fail'
  }
  return report
}

try {
  const args = parseArgs(process.argv.slice(2))
  const report = makeReport(args)
  mkdirSync(dirname(args.output), { recursive: true })
  writeFileSync(args.output, JSON.stringify(report, null, 2) + '\n')
  if (args.json) process.stdout.write(JSON.stringify(report, null, 2) + '\n')
  else {
    process.stdout.write('pptx-nova visual review: ' + report.status + '\n')
    process.stdout.write('- slides reviewed: ' + report.summary.slidesReviewed + '\n')
    process.stdout.write('- errors: ' + report.summary.errors + '\n')
    process.stdout.write('- warnings: ' + report.summary.warnings + '\n')
    process.stdout.write('- report: ' + args.output + '\n')
  }
  if (report.status === 'fail') process.exitCode = 1
} catch (error) {
  process.stderr.write(error.message + '\n')
  process.exitCode = 1
}
