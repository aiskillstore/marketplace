import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { basename, dirname, extname, isAbsolute, relative, sep } from 'node:path'
import { performance } from 'node:perf_hooks'
import { createProgressReporter } from './progress.mjs'

const DEFAULT_MAX_BUFFER = 128 * 1024 * 1024

export class PhaseFailure extends Error {
  constructor(phase, message, details = {}) {
    super(message)
    this.name = 'PhaseFailure'
    this.phase = phase
    Object.assign(this, details)
  }
}

export function durationMs(start) {
  return Number((performance.now() - start).toFixed(2))
}

export function relativeArtifact(runDir, path) {
  return path ? relative(runDir, path) || '.' : null
}

export function commandText(bin, args) {
  return [bin, ...args]
    .map((value) => (/\s|["']/.test(value) ? JSON.stringify(value) : value))
    .join(' ')
}

export function commandInvocation(bin, args) {
  const extension = extname(bin).toLowerCase()
  if (['.cjs', '.js', '.mjs'].includes(extension) && (/[\\/]/.test(bin) || existsSync(bin))) {
    return { bin: process.execPath, args: [bin, ...args] }
  }
  return { bin, args }
}

function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function saveStream(runDir, phase, kind, value) {
  if (!value?.trim()) return null
  const path = `${runDir}/${phase}.${kind}.txt`
  writeFileSync(path, value)
  return path
}

function jsonStatusFailure(report) {
  const status = typeof report?.status === 'string' ? report.status.toLowerCase() : ''
  return ['error', 'fail', 'failed', 'blocked'].includes(status)
}

function jsonStatusFailureKind(report) {
  return report?.error?.kind ?? report?.error?.code ?? report?.status ?? 'JsonStatusFailure'
}

function publicationFacts(report) {
  const facts = {}
  for (const key of ['primaryOutputPublished', 'outputUntouched']) {
    if (typeof report?.[key] === 'boolean') facts[key] = report[key]
  }
  for (const key of ['output', 'blockedOutput']) {
    if (typeof report?.[key] === 'string' || report?.[key] === null) facts[key] = report[key]
  }
  return facts
}

export function summarizePhaseError(error) {
  return {
    phase: error.phase ?? 'runner',
    kind: error.kind ?? error.name ?? 'Error',
    message: error.message,
    exitCode: error.exitCode ?? null,
    ...publicationFacts(error.report),
  }
}

function nullReporter() {
  return createProgressReporter({ mode: 'off' })
}

export function createRunnerRuntime({ getProgressReporter, maxBuffer = DEFAULT_MAX_BUFFER } = {}) {
  const reporter = () => getProgressReporter?.() ?? nullReporter()

  function runJsonPhase(summary, options) {
    const { name, bin, args, artifact, cwd = summary.runDir } = options
    const started = performance.now()
    const command = commandInvocation(bin, args)
    const progress = reporter()
    progress.emit('phase-start', {
      phase: name,
      executable: basename(command.bin),
      argumentCount: command.args.length,
    })
    const result = spawnSync(command.bin, command.args, {
      cwd,
      encoding: 'utf8',
      maxBuffer,
      env: {
        ...process.env,
        ...(options.env ?? {}),
        ...(options.forwardProgress ? { PPTX_NOVA_PROGRESS_FD: '3' } : {}),
      },
      stdio: options.forwardProgress
        ? ['ignore', 'pipe', 'pipe', progress.forwardFd ?? process.stderr]
        : ['ignore', 'pipe', 'pipe'],
    })
    if (result.error) {
      const phase = {
        name,
        status: 'failed',
        exitCode: null,
        signal: null,
        durationMs: durationMs(started),
        command: commandText(command.bin, command.args),
        artifact: relativeArtifact(summary.runDir, artifact),
        stderr: null,
        spawnError: result.error.message,
      }
      summary.phases.push(phase)
      progress.emit('phase-complete', {
        phase: name,
        status: 'failed',
        durationMs: phase.durationMs,
        error: result.error.message,
      })
      throw new PhaseFailure(name, `${name} could not start: ${result.error.message}`, {
        kind: result.error.code ?? 'SpawnError',
      })
    }

    const stderrPath = saveStream(summary.runDir, name, 'stderr', result.stderr ?? '')
    let report = null
    let parseError = null
    try {
      report = JSON.parse(result.stdout || '')
      if (artifact) writeJson(artifact, report)
    } catch (error) {
      parseError = error
      saveStream(summary.runDir, name, 'stdout', result.stdout ?? '')
    }

    const phase = {
      name,
      status:
        result.status === 0 && !parseError && !jsonStatusFailure(report) ? 'passed' : 'failed',
      exitCode: result.status,
      signal: result.signal ?? null,
      durationMs: durationMs(started),
      command: commandText(command.bin, command.args),
      artifact: relativeArtifact(summary.runDir, artifact),
      stderr: relativeArtifact(summary.runDir, stderrPath),
      ...(jsonStatusFailure(report) ? publicationFacts(report) : {}),
    }
    summary.phases.push(phase)
    progress.emit('phase-complete', {
      phase: name,
      status: phase.status,
      durationMs: phase.durationMs,
      exitCode: phase.exitCode,
      artifact: phase.artifact,
    })

    if (parseError) {
      throw new PhaseFailure(name, `${name} did not emit valid JSON: ${parseError.message}`, {
        exitCode: result.status,
        report,
      })
    }
    const publicationWarning =
      report?.primaryOutputPublished === true
        ? '; primary PPTX was published; inspect the output and blocked sidecar before recovery; do not automatically repeat the mutation'
        : ''
    if (result.status !== 0) {
      const kind = jsonStatusFailureKind(report)
      throw new PhaseFailure(
        name,
        `${name} failed with exit code ${result.status}${kind ? ` (${kind})` : ''}${publicationWarning}`,
        { exitCode: result.status, kind, report },
      )
    }
    if (jsonStatusFailure(report)) {
      const kind = jsonStatusFailureKind(report)
      throw new PhaseFailure(
        name,
        `${name} emitted failure JSON status ${JSON.stringify(report.status)}${kind ? ` (${kind})` : ''}${publicationWarning}`,
        { exitCode: result.status, kind, report },
      )
    }
    return report
  }

  function runPlainPhase(summary, options) {
    const { name, bin, args, cwd = summary.runDir } = options
    const started = performance.now()
    const command = commandInvocation(bin, args)
    const progress = reporter()
    progress.emit('phase-start', {
      phase: name,
      executable: basename(command.bin),
      argumentCount: command.args.length,
    })
    const result = spawnSync(command.bin, command.args, {
      cwd,
      encoding: 'utf8',
      maxBuffer,
      env: { ...process.env, ...(options.env ?? {}) },
    })
    if (result.error) {
      const phase = {
        name,
        status: 'failed',
        exitCode: null,
        signal: null,
        durationMs: durationMs(started),
        command: commandText(command.bin, command.args),
        artifact: null,
        stdout: null,
        stderr: null,
        spawnError: result.error.message,
      }
      summary.phases.push(phase)
      progress.emit('phase-complete', {
        phase: name,
        status: 'failed',
        durationMs: phase.durationMs,
        error: result.error.message,
      })
      throw new PhaseFailure(name, `${name} could not start: ${result.error.message}`, {
        kind: result.error.code ?? 'SpawnError',
      })
    }

    const stdoutPath = saveStream(summary.runDir, name, 'stdout', result.stdout ?? '')
    const stderrPath = saveStream(summary.runDir, name, 'stderr', result.stderr ?? '')
    const phase = {
      name,
      status: result.status === 0 ? 'passed' : 'failed',
      exitCode: result.status,
      signal: result.signal ?? null,
      durationMs: durationMs(started),
      command: commandText(command.bin, command.args),
      artifact: null,
      stdout: relativeArtifact(summary.runDir, stdoutPath),
      stderr: relativeArtifact(summary.runDir, stderrPath),
    }
    summary.phases.push(phase)
    progress.emit('phase-complete', {
      phase: name,
      status: phase.status,
      durationMs: phase.durationMs,
      exitCode: phase.exitCode,
    })
    if (result.status !== 0) {
      throw new PhaseFailure(name, `${name} failed with exit code ${result.status}`, {
        exitCode: result.status,
      })
    }
    return phase
  }

  function addInternalPhase(summary, name, status, details = {}) {
    const phase = {
      name,
      status,
      exitCode: null,
      signal: null,
      durationMs: details.durationMs ?? 0,
      command: null,
      artifact: details.artifact ?? null,
      details,
    }
    summary.phases.push(phase)
    reporter().emit('phase-complete', {
      phase: name,
      status,
      durationMs: phase.durationMs,
      ...details,
    })
    return phase
  }

  function requireGate(summary, name, passed, details = {}) {
    const { message, ...publicDetails } = details
    const gate = {
      name,
      passed: Boolean(passed),
      ...publicDetails,
      ...(message ? { policy: message } : {}),
    }
    summary.gates.push(gate)
    if (!gate.passed) {
      throw new PhaseFailure(name, message ?? `${name} gate failed`, { report: details })
    }
    return gate
  }

  return { runJsonPhase, runPlainPhase, addInternalPhase, requireGate }
}

export function gateByName(summary, name) {
  return summary.gates.find((gate) => gate.name === name) ?? null
}

export function gateStatus(gate) {
  if (!gate) return 'not-run'
  return gate.passed ? 'passed' : 'failed'
}

export function buildAgentResult(summary, { schemaVersion, requiredReferences } = {}) {
  return {
    schemaVersion,
    mode: summary.mode ?? null,
    status: summary.status,
    machineGatesPassed: Boolean(summary.machineGatesPassed),
    deliveryReady: Boolean(summary.deliveryReady),
    needsHumanReview: Boolean(summary.needsHumanReview),
    runDir: summary.runDir ?? null,
    output: summary.output ?? null,
    performance: compactPerformanceSummary(summary.performance),
    agentSummary: compactAgentSummary(summary.agentSummary, summary.runDir),
    requiredReferences: requiredReferences ?? summary.requiredReferences ?? [],
    error: summary.error ?? null,
  }
}

function compactPerformanceSummary(performanceSummary) {
  if (!performanceSummary) return null
  const compact = { ...performanceSummary }
  for (const key of Object.keys(performanceSummary.render ?? {})) delete compact[key]
  delete compact.renderBudget
  return compact
}

function compactArtifactPath(runDir, path) {
  if (!runDir || typeof path !== 'string' || !path) return path
  if (!isAbsolute(path)) return path
  const local = relative(runDir, path)
  const outside = local === '..' || local.startsWith(`..${sep}`) || isAbsolute(local)
  return outside ? path : local || '.'
}

function compactAgentSummary(agentSummary, runDir) {
  if (!agentSummary) return null
  const artifacts = agentSummary.artifacts
  if (!artifacts || typeof artifacts !== 'object') return agentSummary
  return {
    ...agentSummary,
    artifacts: Object.fromEntries(
      Object.entries(artifacts).map(([key, value]) => [
        key,
        Array.isArray(value)
          ? value.map((path) => compactArtifactPath(runDir, path))
          : compactArtifactPath(runDir, value),
      ]),
    ),
  }
}

export function buildPerformanceSummary(
  summary,
  totalMs,
  { renderPhaseNames = [], render = {}, budget = {} } = {},
) {
  const measured = summary.phases
    .filter((phase) => Number.isFinite(phase.durationMs) && phase.durationMs > 0)
    .map((phase) => ({ name: phase.name, durationMs: phase.durationMs }))
  const renderNames = new Set(renderPhaseNames)
  const renderMs = measured
    .filter((phase) => renderNames.has(phase.name))
    .reduce((sum, phase) => sum + phase.durationMs, 0)
  return {
    schemaVersion: 'pptx-nova-performance/v1',
    totalMs,
    measuredPhaseMs: Number(measured.reduce((sum, phase) => sum + phase.durationMs, 0).toFixed(2)),
    renderMs: Number(renderMs.toFixed(2)),
    renderShare: totalMs > 0 ? Number((renderMs / totalMs).toFixed(4)) : 0,
    render,
    ...(Object.keys(budget).length ? { budget } : {}),
    ...render,
    ...(Object.keys(budget).length ? { renderBudget: budget } : {}),
    topPhases: [...measured].sort((left, right) => right.durationMs - left.durationMs).slice(0, 5),
  }
}

export function finalizeRunnerSummary(
  summary,
  { summaryPath, totalMs, buildPerformance, buildAgentSummary, finalizeArtifacts } = {},
) {
  if (!summaryPath) throw new Error('finalizeRunnerSummary requires summaryPath')
  finalizeArtifacts?.(summary, summaryPath)
  if (buildPerformance) summary.performance = buildPerformance(summary, totalMs)
  if (buildAgentSummary) summary.agentSummary = buildAgentSummary(summary)
  writeJson(summaryPath, summary)
  return summary
}
