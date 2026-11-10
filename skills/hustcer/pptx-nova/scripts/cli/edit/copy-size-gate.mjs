#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, extname, resolve } from 'node:path'

const SCHEMA_VERSION = 'pptx-nova-copy-size-gate/v1'

const usage = `Usage:
  node <skill-root>/scripts/cli/edit/copy-size-gate.mjs [options]

Options:
  --target <path>       Target PPTX that will receive copied slides.
  --donor <path>        Donor PPTX passed to xdoc slide-copy --source.
  --copy-report <path>  Current pptx-slide-copy/v1 dry-run report.
  --xdoc-bin <path>     xdoc executable or JavaScript wrapper. Defaults to xdoc.
  --output <path>       Optional persisted gate report.
  --overwrite           Replace an existing output report.
  --json                Print the gate report as JSON.
  --help                Show this help.

Exit status:
  0  slide sizes match and the dry-run file/package identities are valid
  2  invalid arguments, unreadable inputs, or inspect failure
  3  stale/invalid preflight or donor/target slide-size mismatch
`

function parseArgs(argv) {
  const args = {
    target: '',
    donor: '',
    copyReport: '',
    xdocBin: 'xdoc',
    output: '',
    overwrite: false,
    json: false,
  }
  const valueFlags = {
    '--target': 'target',
    '--donor': 'donor',
    '--copy-report': 'copyReport',
    '--xdoc-bin': 'xdocBin',
    '--output': 'output',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--overwrite') {
      args.overwrite = true
      continue
    }
    if (arg === '--json') {
      args.json = true
      continue
    }
    const key = valueFlags[arg]
    if (!key) throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    const value = argv[index + 1]
    if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`)
    args[key] = value
    index += 1
  }
  for (const key of ['target', 'donor', 'copyReport']) {
    if (!args[key]) throw new Error(`--${key === 'copyReport' ? 'copy-report' : key} is required`)
    args[key] = resolve(args[key])
  }
  if (args.output) args.output = resolve(args.output)
  return args
}

function assertInputFile(path, label, extension = '') {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  if (!statSync(path).isFile()) throw new Error(`${label} is not a file: ${path}`)
  if (extension && extname(path).toLowerCase() !== extension) {
    throw new Error(`${label} must be a ${extension} file: ${path}`)
  }
}

function sha256(path) {
  const hash = createHash('sha256')
  hash.update(readFileSync(path))
  return hash.digest('hex')
}

function sha256LooksValid(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/.test(value)
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`)
  }
}

function resolveXdocCommand(xdocBin, args) {
  const javascriptPath =
    ['.js', '.mjs', '.cjs'].includes(extname(xdocBin).toLowerCase()) && existsSync(xdocBin)
  return javascriptPath
    ? { executable: process.execPath, args: [xdocBin, ...args] }
    : { executable: xdocBin, args }
}

function inspectDeck(xdocBin, path, label) {
  const command = resolveXdocCommand(xdocBin, ['pptx', 'inspect', path, '--json'])
  const result = spawnSync(command.executable, command.args, {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
  if (result.error) throw new Error(`${label} inspect failed: ${result.error.message}`)
  if (result.status !== 0) {
    const detail = (result.stderr || result.stdout || '').trim()
    throw new Error(`${label} inspect exited ${result.status}${detail ? `: ${detail}` : ''}`)
  }
  let report
  try {
    report = JSON.parse(result.stdout)
  } catch (error) {
    throw new Error(`${label} inspect did not emit valid JSON: ${error.message}`)
  }
  if (report?.status !== 'success') {
    throw new Error(`${label} inspect status must be success`)
  }
  const slideSize = report?.presentation?.slideSize
  const wEmu = String(slideSize?.wEmu ?? '')
  const hEmu = String(slideSize?.hEmu ?? '')
  if (!/^[1-9][0-9]*$/.test(wEmu) || !/^[1-9][0-9]*$/.test(hEmu)) {
    throw new Error(`${label} inspect is missing a positive presentation.slideSize wEmu/hEmu`)
  }
  return {
    path,
    byteLength: statSync(path).size,
    fileSha256: sha256(path),
    slideSize: { wEmu, hEmu },
  }
}

function compareSizes(target, donor) {
  const matches =
    target.slideSize.wEmu === donor.slideSize.wEmu && target.slideSize.hEmu === donor.slideSize.hEmu
  return {
    matches,
    target: target.slideSize,
    donor: donor.slideSize,
    donorToTargetScale: {
      x: Number((Number(target.slideSize.wEmu) / Number(donor.slideSize.wEmu)).toFixed(8)),
      y: Number((Number(target.slideSize.hEmu) / Number(donor.slideSize.hEmu)).toFixed(8)),
    },
    policy: 'native-require-match-plus-sha-bound-verification',
  }
}

function validateCopyReport(copyReport, target, donor) {
  const failures = []
  if (copyReport?.schemaVersion !== 'pptx-slide-copy/v1') {
    failures.push({
      code: 'copy-report-schema-invalid',
      message: 'copy report schemaVersion must be pptx-slide-copy/v1',
    })
  }
  if (copyReport?.outcome !== 'passed' || copyReport?.preflight?.ready !== true) {
    failures.push({
      code: 'copy-preflight-not-ready',
      message: 'slide-copy dry-run and preflight must both be ready',
    })
  }
  if (copyReport?.preflight?.readOnly !== true) {
    failures.push({
      code: 'copy-preflight-not-read-only',
      message: 'slide-copy preflight must be read-only',
    })
  }
  if (
    !Array.isArray(copyReport?.preflight?.blockers) ||
    !Array.isArray(copyReport?.preflight?.risks)
  ) {
    failures.push({
      code: 'copy-preflight-issues-missing',
      message: 'slide-copy preflight must include blockers and risks arrays',
    })
  }
  if ((copyReport?.preflight?.blockers?.length ?? 0) > 0) {
    failures.push({
      code: 'copy-preflight-has-blockers',
      message: 'slide-copy preflight contains blockers',
    })
  }
  const templateStrategy = copyReport?.preflight?.strategy?.template
  const slideSizeStrategy = copyReport?.preflight?.strategy?.slideSize
  if (!['register-source', 'rebind-target'].includes(templateStrategy)) {
    failures.push({
      code: 'copy-template-strategy-invalid',
      message: 'slide-copy preflight must declare register-source or rebind-target',
    })
  }
  if (slideSizeStrategy !== 'require-match') {
    failures.push({
      code: 'copy-size-strategy-invalid',
      message: 'slide-copy preflight must declare slideSize strategy require-match',
    })
  }
  if (!Array.isArray(copyReport?.preflight?.templates)) {
    failures.push({
      code: 'copy-template-plan-missing',
      message: 'slide-copy preflight must disclose templates[] closure mappings',
    })
  } else {
    const allowedOutcomes =
      templateStrategy === 'register-source'
        ? new Set(['registered-source', 'reused-source'])
        : new Set(['rebound-target', 'reused-source'])
    for (const template of copyReport.preflight.templates) {
      if (
        !allowedOutcomes.has(template?.outcome) ||
        !template?.layout?.sourcePartName ||
        !template?.layout?.targetPartName ||
        !template?.master?.sourcePartName ||
        !template?.master?.targetPartName
      ) {
        failures.push({
          code: 'copy-template-plan-invalid',
          message: 'slide-copy templates[] contains an invalid outcome or incomplete mapping',
        })
        break
      }
    }
  }
  if (copyReport?.transaction?.rollbackBoundary !== 'entire-copy-batch') {
    failures.push({
      code: 'copy-rollback-boundary-invalid',
      message: 'slide-copy report must declare the entire-copy-batch rollback boundary',
    })
  }
  if (!sha256LooksValid(copyReport?.preflight?.targetFingerprint)) {
    failures.push({
      code: 'target-package-fingerprint-invalid',
      message:
        'slide-copy preflight targetFingerprint must be a normalized OPC package fingerprint',
    })
  }
  if (!sha256LooksValid(copyReport?.preflight?.sourceFingerprint)) {
    failures.push({
      code: 'donor-package-fingerprint-invalid',
      message:
        'slide-copy preflight sourceFingerprint must be a normalized OPC package fingerprint',
    })
  }
  if (copyReport?.preflight?.targetFileSha256 !== target.fileSha256) {
    failures.push({
      code: 'target-file-sha256-mismatch',
      message: 'slide-copy preflight targetFileSha256 is stale or belongs to another PPTX',
    })
  }
  if (copyReport?.preflight?.sourceFileSha256 !== donor.fileSha256) {
    failures.push({
      code: 'donor-file-sha256-mismatch',
      message: 'slide-copy preflight sourceFileSha256 is stale or belongs to another PPTX',
    })
  }
  return failures
}

function buildReport(args) {
  assertInputFile(args.target, 'target PPTX', '.pptx')
  assertInputFile(args.donor, 'donor PPTX', '.pptx')
  assertInputFile(args.copyReport, 'copy report', '.json')
  const target = inspectDeck(args.xdocBin, args.target, 'target PPTX')
  const donor = inspectDeck(args.xdocBin, args.donor, 'donor PPTX')
  const copyReport = readJson(args.copyReport, 'copy report')
  const failures = validateCopyReport(copyReport, target, donor)
  const comparison = compareSizes(target, donor)
  if (!comparison.matches) {
    failures.push({
      code: 'slide-size-mismatch',
      message:
        `donor slide size ${donor.slideSize.wEmu}x${donor.slideSize.hEmu} EMU differs from ` +
        `target ${target.slideSize.wEmu}x${target.slideSize.hEmu} EMU; raw copied geometry ` +
        'is blocked by native require-match and must not be scaled implicitly',
    })
  }
  const nextAction = failures.some((failure) => failure.code === 'slide-size-mismatch')
    ? 'choose-explicit-slide-size-strategy'
    : failures.some((failure) => failure.code.endsWith('file-sha256-mismatch'))
      ? 'refresh-slide-copy-preflight'
      : failures.length > 0
        ? 'resolve-slide-copy-preflight'
        : 'continue-slide-copy'
  return {
    schemaVersion: SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    status: failures.length === 0 ? 'pass' : 'fail',
    target,
    donor,
    copyReport: {
      path: args.copyReport,
      schemaVersion: copyReport?.schemaVersion ?? null,
      status: copyReport?.status ?? null,
      sourceFileSha256: copyReport?.preflight?.sourceFileSha256 ?? null,
      targetFileSha256: copyReport?.preflight?.targetFileSha256 ?? null,
      sourcePackageFingerprint: copyReport?.preflight?.sourceFingerprint ?? null,
      targetPackageFingerprint: copyReport?.preflight?.targetFingerprint ?? null,
      templateStrategy: copyReport?.preflight?.strategy?.template ?? null,
      slideSizeStrategy: copyReport?.preflight?.strategy?.slideSize ?? null,
      templatePlanCount: copyReport?.preflight?.templates?.length ?? null,
      riskCount: copyReport?.preflight?.risks?.length ?? null,
      blockerCount: copyReport?.preflight?.blockers?.length ?? null,
    },
    slideSizeComparison: comparison,
    agentGate: {
      passed: failures.length === 0,
      nextAction,
      failures,
      attention:
        (copyReport?.preflight?.risks?.length ?? 0) > 0
          ? ['Review every slide-copy preflight risk separately; this gate covers slide size only.']
          : [],
    },
  }
}

function emit(report, args) {
  const text = `${JSON.stringify(report, null, 2)}\n`
  if (args.output) {
    if (existsSync(args.output) && !args.overwrite) {
      throw new Error(
        `output already exists; pass --overwrite only for a current-run report: ${args.output}`,
      )
    }
    mkdirSync(dirname(args.output), { recursive: true })
    writeFileSync(args.output, text)
  }
  if (args.json) process.stdout.write(text)
  else {
    process.stdout.write(`pptx-nova copy size gate: ${report.status}\n`)
    process.stdout.write(`- next action: ${report.agentGate.nextAction}\n`)
    if (args.output) process.stdout.write(`- report: ${args.output}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const report = buildReport(args)
  emit(report, args)
  if (!report.agentGate.passed) process.exitCode = 3
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exitCode = 2
}
