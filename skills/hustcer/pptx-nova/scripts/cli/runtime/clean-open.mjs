#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { homedir, platform, tmpdir } from 'node:os'
import { basename, dirname, extname, join, resolve } from 'node:path'

const SCHEMA_VERSION = 'pptx-nova-clean-open/v1'
const DEFAULT_APP = 'Microsoft PowerPoint'
const DEFAULT_TIMEOUT_MS = 30000
const DEFAULT_OPEN_DELAY_MS = 8000
const OPEN_RETRY_DELAY_MS = 4000
const LOCK_DIR = join(tmpdir(), 'pptx-nova-clean-open.lock')

const usage = `Usage:
  node <skill-root>/scripts/cli/runtime/clean-open.mjs --pptx <candidate.pptx> [options]
  node <skill-root>/scripts/cli/runtime/clean-open.mjs --classify-ui <ui.json> [options]

Options:
  --pptx <path>            Candidate PPTX to open in Microsoft PowerPoint.
  --output <path>          Optional JSON report path, usually <run-dir>/clean-open.json.
  --app <name>             PowerPoint application name. Defaults to "${DEFAULT_APP}".
  --timeout-ms <ms>        osascript timeout per phase. Defaults to ${DEFAULT_TIMEOUT_MS}.
  --open-delay-ms <ms>     Settle time after opening before UI inspection. Defaults to ${DEFAULT_OPEN_DELAY_MS}.
  --required               Deprecated compatibility flag; unavailable environments still skip.
  --keep-open              Leave the staged presentation open for debugging.
  --classify-ui <path>     Test classifier against a saved UI snapshot JSON.
  --json                   Print machine-readable JSON to stdout.
  --help                   Show this help.

Live clean-open supports macOS only with Microsoft PowerPoint for Mac,
osascript, and System Events UI scripting. Windows/Linux, macOS without
PowerPoint, and missing UI scripting authorization return status "skipped" with
exit code 0; disclose that clean-open did not run and list replacement
structural checks. --classify-ui is platform-independent for saved UI snapshots.

This helper stages the PPTX inside PowerPoint's sandbox tmp directory, opens only
that staged copy, checks for Repair dialogs through System Events, and closes the
staged copy unless --keep-open is set. A plain Cancel button is not a failure; it
must appear in a Repair-like dialog or alongside Repair-specific text/button UI.
`

const REPAIR_TEXT_PATTERNS = [
  /PowerPoint\s+found\s+a\s+problem\s+with\s+content/i,
  /found\s+(?:unreadable\s+)?content/i,
  /can\s+attempt\s+to\s+repair/i,
  /repair\s+(?:this|the)\s+(?:presentation|file|document)/i,
  /there\s+was\s+an\s+error\s+accessing/i,
  /内容.*问题/,
  /发现.*问题/,
  /尝试.*修复/,
  /修复.*(?:演示文稿|文件|内容)/,
]
const REPAIR_BUTTON_PATTERNS = [/^Repair$/i, /^修复$/]
const CANCEL_BUTTON_PATTERNS = [/^Cancel$/i, /^取消$/, /^不修复$/]

function parseArgs(argv) {
  const args = {
    pptx: '',
    output: '',
    app: DEFAULT_APP,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    openDelayMs: DEFAULT_OPEN_DELAY_MS,
    required: false,
    keepOpen: false,
    classifyUi: '',
    json: false,
  }
  const valueFlags = {
    '--pptx': 'pptx',
    '--output': 'output',
    '--app': 'app',
    '--timeout-ms': 'timeoutMs',
    '--open-delay-ms': 'openDelayMs',
    '--classify-ui': 'classifyUi',
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--required') {
      args.required = true
      continue
    }
    if (arg === '--keep-open') {
      args.keepOpen = true
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
    args[key] = key.endsWith('Ms') ? Number(value) : value
    index += 1
  }
  if (!args.classifyUi && !args.pptx) throw new Error(`--pptx is required.\n\n${usage}`)
  if (args.pptx) args.pptx = resolve(args.pptx)
  if (args.output) args.output = resolve(args.output)
  if (args.classifyUi) args.classifyUi = resolve(args.classifyUi)
  if (!Number.isInteger(args.timeoutMs) || args.timeoutMs <= 0) {
    throw new Error('--timeout-ms must be a positive integer')
  }
  if (!Number.isInteger(args.openDelayMs) || args.openDelayMs < 0) {
    throw new Error('--open-delay-ms must be a non-negative integer')
  }
  return args
}

function sha256(path) {
  const hash = createHash('sha256')
  hash.update(readFileSync(path))
  return hash.digest('hex')
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function baseReport(args) {
  const inputExists = Boolean(args.pptx && existsSync(args.pptx))
  return {
    schemaVersion: SCHEMA_VERSION,
    status: 'error',
    gate: {
      passed: false,
      reason: 'not-run',
    },
    input: args.pptx
      ? {
          path: args.pptx,
          name: basename(args.pptx),
          byteLength: inputExists ? statSync(args.pptx).size : null,
          sha256: inputExists ? sha256(args.pptx) : null,
        }
      : null,
    environment: {
      platform: platform(),
      appName: args.app,
      osascriptAvailable: null,
      powerPointAvailable: null,
      uiScriptingAuthorized: null,
      required: args.required,
    },
    observations: {
      openedDocument: false,
      presentationName: null,
      openError: null,
      windows: [],
      repairSignals: [],
      nonRepairDialogs: [],
    },
    cleanup: {
      stagedPath: null,
      tmpDir: null,
      closeStaged: null,
      repairDialogDismissed: null,
      tmpRemoved: false,
      lockReleased: false,
    },
    error: null,
  }
}

function reportStatus(report, status, reason, details = {}) {
  report.status = status
  report.gate = {
    passed: status === 'pass',
    reason,
    ...details,
  }
  return report
}

function exitCodeFor(report) {
  if (report.status === 'pass') return 0
  if (report.status === 'fail') return 1
  if (report.status === 'skipped') return 0
  return 2
}

function emit(report, args) {
  const text = `${JSON.stringify(report, null, 2)}\n`
  if (args.output) {
    mkdirSync(dirname(args.output), { recursive: true })
    writeFileSync(args.output, text)
  }
  if (args.json) {
    process.stdout.write(text)
  } else {
    process.stdout.write(`pptx-nova clean-open: ${report.status}\n`)
    process.stdout.write(`- reason: ${report.gate.reason}\n`)
    if (args.output) process.stdout.write(`- report: ${args.output}\n`)
  }
  process.exitCode = exitCodeFor(report)
}

function commandAvailable(name) {
  const result = spawnSync('which', [name], { encoding: 'utf8' })
  return result.status === 0
}

function osascript(args, script, timeoutMs) {
  const result = spawnSync('osascript', args, {
    input: script,
    encoding: 'utf8',
    timeout: timeoutMs,
    maxBuffer: 16 * 1024 * 1024,
  })
  return {
    ok: result.status === 0,
    status: result.status,
    signal: result.signal ?? null,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? '').trim(),
    error: result.error?.message ?? null,
  }
}

function acquireLock() {
  try {
    mkdirSync(LOCK_DIR)
    return { ok: true, path: LOCK_DIR }
  } catch (error) {
    return {
      ok: false,
      path: LOCK_DIR,
      message:
        error.code === 'EEXIST'
          ? 'Another pptx-nova clean-open invocation is already running'
          : error.message,
    }
  }
}

function releaseLock(report) {
  try {
    rmSync(LOCK_DIR, { recursive: true, force: true })
    report.cleanup.lockReleased = true
  } catch {
    report.cleanup.lockReleased = false
  }
}

function powerpointContainerTmpRoot() {
  return join(homedir(), 'Library', 'Containers', 'com.microsoft.Powerpoint', 'Data', 'tmp')
}

function stagePptx(pptxPath) {
  const root = powerpointContainerTmpRoot()
  mkdirSync(root, { recursive: true })
  const tmpDir = mkdtempSync(join(root, 'pptx-nova-clean-open.'))
  const inputName = basename(pptxPath)
  const stagedName = extname(inputName).toLowerCase() === '.pptx' ? inputName : 'deck.pptx'
  const stagedPath = join(tmpDir, stagedName)
  copyFileSync(pptxPath, stagedPath)
  return { tmpDir, stagedPath }
}

function checkPowerPoint(appName, timeoutMs) {
  const script = `id of application "${appName.replaceAll('"', '\\"')}"`
  return spawnSync('osascript', ['-e', script], {
    encoding: 'utf8',
    timeout: timeoutMs,
  })
}

function waitMs(delayMs) {
  if (delayMs <= 0) return
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, delayMs)
}

function launchPresentation(stagedPath, appName, timeoutMs) {
  const result = spawnSync('open', ['-a', appName, stagedPath], {
    encoding: 'utf8',
    timeout: timeoutMs,
  })
  return {
    ok: result.status === 0,
    status: result.status,
    signal: result.signal ?? null,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? '').trim(),
    error: result.error?.message ?? null,
  }
}

function presentationState(stagedPath, appName, timeoutMs) {
  const timeoutSeconds = Math.max(5, Math.ceil(timeoutMs / 1000))
  const script = `
on run argv
  set ppt_path to item 1 of argv
  set app_name to item 2 of argv
  set tab_char to ASCII character 9
  using terms from application "Microsoft PowerPoint"
    with timeout of ${timeoutSeconds} seconds
      tell application app_name
        set matched to false
        set pres_name to ""
        set pres_count to count of presentations
        repeat with i from 1 to pres_count
          try
            if ((full name of presentation i) as string) is equal to ppt_path then
              set matched to true
              set pres_name to name of presentation i as string
              exit repeat
            end if
          end try
        end repeat
        return (matched as string) & tab_char & pres_name
      end tell
    end timeout
  end using terms from
end run
`
  const result = osascript(['-', stagedPath, appName], script, timeoutMs)
  if (!result.ok) {
    return {
      ok: false,
      openedDocument: false,
      presentationName: null,
      openError: {
        message: result.stderr || result.error || 'PowerPoint open script failed',
        number: result.status,
        stdout: result.stdout,
      },
    }
  }
  const fields = result.stdout.split('\t')
  return {
    ok: true,
    openedDocument: fields[0] === 'true',
    presentationName: fields[1] || null,
    openError: null,
  }
}

function closePresentation(stagedPath, appName, timeoutMs) {
  const script = `
on run argv
  set ppt_path to item 1 of argv
  set app_name to item 2 of argv
  using terms from application "Microsoft PowerPoint"
    tell application app_name
      set pres_count to count of presentations
      repeat with i from pres_count to 1 by -1
        try
          if ((full name of presentation i) as string) is equal to ppt_path then
            close presentation i saving no
          end if
        end try
      end repeat
    end tell
  end using terms from
end run
`
  return osascript(['-', stagedPath, appName], script, timeoutMs)
}

function uiSnapshot(appName, timeoutMs) {
  const script = `
function safe(fn, fallback) {
  try {
    const value = fn()
    if (value === undefined || value === null) return fallback
    return value
  } catch (_) {
    return fallback
  }
}
function asString(value) {
  try {
    if (value === undefined || value === null) return ''
    return String(value)
  } catch (_) {
    return ''
  }
}
function safeArray(fn) {
  const value = safe(fn, [])
  try {
    return Array.from(value)
  } catch (_) {
    return []
  }
}
function snapshotElement(element, depth, counter) {
  counter.count += 1
  const item = {
    role: asString(safe(() => element.role(), '')),
    subrole: asString(safe(() => element.subrole(), '')),
    name: asString(safe(() => element.name(), '')),
    description: asString(safe(() => element.description(), '')),
    value: asString(safe(() => element.value(), '')),
    children: []
  }
  if (depth <= 0 || counter.count > 600) return item
  item.children = safeArray(() => element.uiElements()).slice(0, 120).map((child) =>
    snapshotElement(child, depth - 1, counter)
  )
  return item
}
function run(argv) {
  const appName = argv[0]
  const se = Application('System Events')
  const process = se.processes.byName(appName)
  if (!process.exists()) {
    return JSON.stringify({ok: false, error: 'PowerPoint process is not running', windows: []})
  }
  safe(() => { process.frontmost = true }, null)
  const counter = {count: 0}
  const windows = safeArray(() => process.windows()).slice(0, 20).map((window) =>
    snapshotElement(window, 5, counter)
  )
  return JSON.stringify({ok: true, windows, nodeCount: counter.count})
}
`
  const result = osascript(['-l', 'JavaScript', '-', appName], script, timeoutMs)
  if (!result.ok) {
    return {
      ok: false,
      windows: [],
      error: result.stderr || result.error || 'System Events UI snapshot failed',
    }
  }
  try {
    return JSON.parse(result.stdout)
  } catch (error) {
    return {
      ok: false,
      windows: [],
      error: `System Events UI snapshot emitted invalid JSON: ${error.message}`,
      stdout: result.stdout,
    }
  }
}

function dismissRepairDialog(appName, timeoutMs) {
  const script = `
const repairText = [
  /PowerPoint\\s+found\\s+a\\s+problem\\s+with\\s+content/i,
  /found\\s+(?:unreadable\\s+)?content/i,
  /can\\s+attempt\\s+to\\s+repair/i,
  /repair\\s+(?:this|the)\\s+(?:presentation|file|document)/i,
  /内容.*问题/,
  /发现.*问题/,
  /尝试.*修复/,
  /修复.*(?:演示文稿|文件|内容)/
]
const cancelText = [/^Cancel$/i, /^取消$/, /^不修复$/]
function safe(fn, fallback) {
  try { return fn() } catch (_) { return fallback }
}
function safeArray(fn) {
  try { return Array.from(fn()) } catch (_) { return [] }
}
function strings(element, out) {
  for (const getter of ['name', 'description', 'value', 'role', 'subrole']) {
    const value = safe(() => element[getter](), '')
    let text = ''
    try {
      text = value === undefined || value === null ? '' : String(value)
    } catch (_) {
      text = ''
    }
    if (text) out.push(text)
  }
  for (const child of safeArray(() => element.uiElements())) strings(child, out)
}
function findCancel(element) {
  const buttons = safeArray(() => element.buttons())
  for (const button of buttons) {
    const name = String(safe(() => button.name(), ''))
    if (cancelText.some((pattern) => pattern.test(name))) return button
  }
  for (const child of safeArray(() => element.uiElements())) {
    const found = findCancel(child)
    if (found) return found
  }
  return null
}
function run(argv) {
  const appName = argv[0]
  const se = Application('System Events')
  const process = se.processes.byName(appName)
  if (!process.exists()) return JSON.stringify({ok: false, reason: 'process-not-running'})
  const windows = safeArray(() => process.windows()).slice(0, 20)
  for (const window of windows) {
    const text = []
    strings(window, text)
    if (!repairText.some((pattern) => pattern.test(text.join('\\n')))) continue
    const cancel = findCancel(window)
    if (!cancel) return JSON.stringify({ok: false, reason: 'repair-dialog-without-cancel'})
    cancel.click()
    return JSON.stringify({ok: true, reason: 'repair-dialog-cancel-clicked'})
  }
  return JSON.stringify({ok: false, reason: 'no-repair-dialog'})
}
`
  const result = osascript(['-l', 'JavaScript', '-', appName], script, timeoutMs)
  if (!result.ok) return { ok: false, reason: result.stderr || result.error || 'dismiss failed' }
  try {
    return JSON.parse(result.stdout)
  } catch {
    return { ok: false, reason: 'dismiss emitted invalid JSON', stdout: result.stdout }
  }
}

function collectStrings(node, out = []) {
  if (!node || typeof node !== 'object') return out
  for (const key of ['role', 'subrole', 'name', 'description', 'value']) {
    const value = node[key]
    if (typeof value === 'string' && value.trim()) out.push(value.trim())
  }
  const children = Array.isArray(node.children) ? node.children : []
  for (const child of children) collectStrings(child, out)
  return out
}

function collectButtonNames(node, out = []) {
  if (!node || typeof node !== 'object') return out
  const role = typeof node.role === 'string' ? node.role : ''
  const name = typeof node.name === 'string' ? node.name.trim() : ''
  if (/button/i.test(role) && name) out.push(name)
  const children = Array.isArray(node.children) ? node.children : []
  for (const child of children) collectButtonNames(child, out)
  return out
}

function summarizeWindows(windows) {
  return (Array.isArray(windows) ? windows : []).map((window) => {
    const strings = collectStrings(window)
    const buttons = collectButtonNames(window)
    return {
      name: window?.name || null,
      role: window?.role || null,
      subrole: window?.subrole || null,
      description: window?.description || null,
      modalLike: windowLooksModal(window, strings, buttons),
      buttons: buttons.slice(0, 40),
      textSample: strings
        .filter((value) => !/^AX[A-Za-z]+$/.test(value))
        .filter((value, index, values) => values.indexOf(value) === index)
        .slice(0, 30),
    }
  })
}

function windowLooksModal(node, strings, buttons) {
  const roles = strings.filter((value) => /^AX/.test(value)).join('\n')
  return (
    /AX(Dialog|Sheet|Alert)/i.test(roles) ||
    (buttons.some((name) => CANCEL_BUTTON_PATTERNS.some((pattern) => pattern.test(name))) &&
      strings.some((value) => value.length > 20))
  )
}

export function classifyCleanOpen(observations) {
  const windows = Array.isArray(observations.windows) ? observations.windows : []
  const repairSignals = []
  const nonRepairDialogs = []
  for (const window of windows) {
    const strings = collectStrings(window)
    const text = strings.join('\n')
    const buttons = collectButtonNames(window)
    const textMatches = REPAIR_TEXT_PATTERNS.filter((pattern) => pattern.test(text)).map(String)
    const repairButtons = buttons.filter((name) =>
      REPAIR_BUTTON_PATTERNS.some((pattern) => pattern.test(name)),
    )
    const modalLike = windowLooksModal(window, strings, buttons)
    if (textMatches.length > 0 || (modalLike && repairButtons.length > 0)) {
      repairSignals.push({
        window: window.name || null,
        role: window.role || null,
        textMatches,
        repairButtons,
        cancelButtons: buttons.filter((name) =>
          CANCEL_BUTTON_PATTERNS.some((pattern) => pattern.test(name)),
        ),
      })
    } else if (modalLike) {
      nonRepairDialogs.push({
        window: window.name || null,
        role: window.role || null,
        buttons,
        sampleText: strings.slice(0, 12),
      })
    }
  }

  if (observations.openError?.message) {
    const openErrorText = String(observations.openError.message)
    const textMatches = REPAIR_TEXT_PATTERNS.filter((pattern) => pattern.test(openErrorText)).map(
      String,
    )
    if (textMatches.length > 0) {
      repairSignals.push({
        window: null,
        role: null,
        source: 'openError',
        textMatches,
        repairButtons: [],
        cancelButtons: [],
      })
    }
  }

  if (repairSignals.length > 0) {
    return {
      status: 'fail',
      reason: 'repair-dialog-detected',
      repairSignals,
      nonRepairDialogs,
    }
  }
  if (observations.openedDocument) {
    return {
      status: 'pass',
      reason: 'opened-without-repair-dialog',
      repairSignals,
      nonRepairDialogs,
    }
  }
  if (observations.openError?.message) {
    return {
      status: 'fail',
      reason: 'powerpoint-open-error',
      repairSignals,
      nonRepairDialogs,
    }
  }
  return {
    status: 'error',
    reason: 'no-open-result',
    repairSignals,
    nonRepairDialogs,
  }
}

function classifyFixture(args) {
  const fixture = readJson(args.classifyUi)
  const observations = {
    openedDocument: Boolean(fixture.openedDocument ?? fixture.observations?.openedDocument),
    openError: fixture.openError ?? fixture.observations?.openError ?? null,
    windows: fixture.windows ?? fixture.observations?.windows ?? [],
  }
  const report = baseReport(args)
  report.environment.uiScriptingAuthorized = true
  report.observations = {
    ...report.observations,
    ...observations,
  }
  const classification = classifyCleanOpen(observations)
  report.observations.windows = summarizeWindows(observations.windows)
  report.observations.repairSignals = classification.repairSignals
  report.observations.nonRepairDialogs = classification.nonRepairDialogs
  return reportStatus(report, classification.status, classification.reason)
}

function unavailable(report, args, reason, details = {}) {
  report.environment = { ...report.environment, ...details.environment }
  report.error = details.error ?? null
  return reportStatus(report, 'skipped', reason, details.gate ?? {})
}

function runLive(args) {
  const report = baseReport(args)
  if (!existsSync(args.pptx)) {
    report.error = { message: 'PPTX file does not exist' }
    return reportStatus(report, 'error', 'input-missing')
  }
  if (extname(args.pptx).toLowerCase() !== '.pptx') {
    report.error = { message: '--pptx must point to a .pptx file' }
    return reportStatus(report, 'error', 'input-not-pptx')
  }
  if (platform() !== 'darwin') {
    return unavailable(report, args, 'not-macos', {
      environment: { osascriptAvailable: false, powerPointAvailable: false },
    })
  }
  report.environment.osascriptAvailable = commandAvailable('osascript')
  if (!report.environment.osascriptAvailable) {
    return unavailable(report, args, 'osascript-unavailable', {
      environment: { powerPointAvailable: false },
    })
  }
  const powerpoint = checkPowerPoint(args.app, args.timeoutMs)
  report.environment.powerPointAvailable = powerpoint.status === 0
  if (!report.environment.powerPointAvailable) {
    return unavailable(report, args, 'powerpoint-unavailable', {
      error: {
        message: powerpoint.stderr || powerpoint.error?.message || 'PowerPoint is unavailable',
        stdout: powerpoint.stdout?.trim() || '',
      },
    })
  }

  const lock = acquireLock()
  if (!lock.ok) {
    report.error = { message: lock.message, lockDir: lock.path }
    return reportStatus(report, 'error', 'lock-unavailable')
  }

  let staged = null
  try {
    staged = stagePptx(args.pptx)
    report.cleanup.tmpDir = staged.tmpDir
    report.cleanup.stagedPath = staged.stagedPath
    const launch = launchPresentation(staged.stagedPath, args.app, args.timeoutMs)
    if (!launch.ok) {
      report.observations.openError = {
        message: launch.stderr || launch.error || 'macOS open command failed',
        number: launch.status,
        stdout: launch.stdout,
      }
      return reportStatus(report, 'fail', 'powerpoint-open-error')
    }
    waitMs(args.openDelayMs)
    let open = presentationState(staged.stagedPath, args.app, args.timeoutMs)
    report.observations.openedDocument = open.openedDocument
    report.observations.presentationName = open.presentationName
    report.observations.openError = open.openError

    let ui = uiSnapshot(args.app, args.timeoutMs)
    if (
      !report.observations.openedDocument &&
      !report.observations.openError &&
      ui.ok &&
      ui.windows.length === 0
    ) {
      waitMs(OPEN_RETRY_DELAY_MS)
      open = presentationState(staged.stagedPath, args.app, args.timeoutMs)
      report.observations.openedDocument = open.openedDocument
      report.observations.presentationName = open.presentationName
      report.observations.openError = open.openError
      ui = uiSnapshot(args.app, args.timeoutMs)
    }
    report.environment.uiScriptingAuthorized = ui.ok
    if (!ui.ok) {
      const openClassification = classifyCleanOpen({
        ...report.observations,
        windows: [],
      })
      if (openClassification.status === 'fail') {
        report.observations.repairSignals = openClassification.repairSignals
        report.observations.nonRepairDialogs = openClassification.nonRepairDialogs
        report.error = {
          message: ui.error,
          note: 'UI snapshot failed after PowerPoint reported an open error',
        }
        return reportStatus(report, openClassification.status, openClassification.reason)
      }
      report.error = { message: ui.error }
      return unavailable(report, args, 'ui-scripting-unavailable', {
        environment: { uiScriptingAuthorized: false },
        error: report.error,
      })
    }

    const observationsForClassification = {
      ...report.observations,
      windows: ui.windows,
    }
    const classification = classifyCleanOpen(observationsForClassification)
    report.observations.windows = summarizeWindows(ui.windows)
    report.observations.repairSignals = classification.repairSignals
    report.observations.nonRepairDialogs = classification.nonRepairDialogs
    if (classification.status === 'fail' && classification.reason === 'repair-dialog-detected') {
      report.cleanup.repairDialogDismissed = dismissRepairDialog(args.app, args.timeoutMs)
    }
    return reportStatus(report, classification.status, classification.reason)
  } catch (error) {
    report.error = { message: error.message, stack: error.stack }
    return reportStatus(report, 'error', 'helper-error')
  } finally {
    if (staged?.stagedPath && !args.keepOpen) {
      report.cleanup.closeStaged = closePresentation(staged.stagedPath, args.app, args.timeoutMs)
    }
    if (staged?.tmpDir && !args.keepOpen) {
      try {
        rmSync(staged.tmpDir, { recursive: true, force: true })
        report.cleanup.tmpRemoved = true
      } catch {
        report.cleanup.tmpRemoved = false
      }
    }
    releaseLock(report)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const report = args.classifyUi ? classifyFixture(args) : runLive(args)
  emit(report, args)
} catch (error) {
  const args = {
    output: '',
    json: false,
    required: true,
    app: DEFAULT_APP,
  }
  const report = reportStatus(baseReport(args), 'error', 'argument-error')
  report.error = { message: error.message }
  process.stderr.write(`${error.message}\n`)
  process.exitCode = 2
}
