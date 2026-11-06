import { createHash } from 'node:crypto'
import { readFileSync, statSync } from 'node:fs'
import { resolve } from 'node:path'

export const SESSION_RULES_SCHEMA_VERSION = 'pptx-nova-session-rules/v1'
export const SESSION_OPERATION_SCHEMA_VERSION = 'pptx-nova-session-operation/v1'
export const SESSION_RESOLUTION_SCHEMA_VERSION = 'pptx-nova-session-rules-resolution/v1'

const RULE_KINDS = new Set(['preserve-invariant', 'future-element-style'])
const RULE_STATUSES = new Set(['active', 'candidate', 'superseded'])
const RULE_EVENTS = new Set(['any-edit', 'slide-added', 'element-added'])
const OPERATION_EVENTS = new Set(['slide-added', 'element-added', 'ordinary-edit'])
const ELEMENT_KINDS = new Set(['slide-title', 'summary-box'])
const PRESERVE_VALUES = new Set(['slide-count', 'non-target-shapes', 'target-text-style'])
const CHANGE_CATEGORIES = new Set(['shape', 'text', 'style', 'structure'])

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function requireObject(value, label) {
  if (!isPlainObject(value)) throw new Error(`${label} must be an object`)
  return value
}

function requireString(value, label) {
  const text = String(value ?? '').trim()
  if (!text) throw new Error(`${label} is required`)
  return text
}

function uniqueStrings(value, label, { allowed, required = false } = {}) {
  if (!Array.isArray(value)) throw new Error(`${label} must be an array`)
  const result = []
  for (const item of value) {
    const text = requireString(item, `${label}[]`)
    if (allowed && !allowed.has(text))
      throw new Error(`${label} contains unsupported value: ${text}`)
    if (!result.includes(text)) result.push(text)
  }
  if (required && result.length === 0) throw new Error(`${label} must not be empty`)
  return result
}

function uniqueIntegers(value, label) {
  if (!Array.isArray(value) || value.length === 0)
    throw new Error(`${label} must be a non-empty array`)
  const result = []
  for (const item of value) {
    if (!Number.isInteger(item) || item < 0)
      throw new Error(`${label} must contain non-negative integers`)
    if (!result.includes(item)) result.push(item)
  }
  return result
}

export function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

export function sha256Json(value) {
  return createHash('sha256').update(JSON.stringify(value)).digest('hex')
}

function normalizeHex(value, label) {
  const hex = String(value ?? '')
    .replace(/^#/, '')
    .trim()
    .toUpperCase()
  if (!/^[0-9A-F]{6}$/.test(hex)) throw new Error(`${label} must be a 6-digit RGB hex color`)
  return hex
}

function normalizeRuleSource(value, label) {
  const source = requireObject(value, label)
  const kind = requireString(source.kind, `${label}.kind`)
  if (!['user-feedback', 'artifact'].includes(kind)) {
    throw new Error(`${label}.kind must be user-feedback or artifact`)
  }
  const quote = requireString(source.quote, `${label}.quote`)
  const turn = source.turn
  if (turn !== undefined && (!Number.isInteger(turn) || turn < 0)) {
    throw new Error(`${label}.turn must be a non-negative integer`)
  }
  return { ...source, kind, quote, ...(turn !== undefined ? { turn } : {}) }
}

function normalizeRule(value, index) {
  const label = `rules[${index}]`
  const rule = requireObject(value, label)
  const id = requireString(rule.id, `${label}.id`)
  const kind = requireString(rule.kind, `${label}.kind`)
  if (!RULE_KINDS.has(kind)) throw new Error(`${label}.kind is unsupported: ${kind}`)
  const status = requireString(rule.status, `${label}.status`)
  if (!RULE_STATUSES.has(status)) throw new Error(`${label}.status is unsupported: ${status}`)
  if (rule.lifetime !== 'current-deck') throw new Error(`${label}.lifetime must be current-deck`)
  const trigger = requireObject(rule.trigger, `${label}.trigger`)
  const event = requireString(trigger.event, `${label}.trigger.event`)
  if (!RULE_EVENTS.has(event)) throw new Error(`${label}.trigger.event is unsupported: ${event}`)
  const target = requireObject(rule.target, `${label}.target`)
  const action = requireObject(rule.action, `${label}.action`)
  const source = normalizeRuleSource(rule.source, `${label}.source`)
  const supersedes = uniqueStrings(rule.supersedes ?? [], `${label}.supersedes`)

  if (kind === 'preserve-invariant') {
    if (target.scope !== 'deck') throw new Error(`${label}.target.scope must be deck`)
    const preserve = uniqueStrings(action.preserve, `${label}.action.preserve`, {
      allowed: PRESERVE_VALUES,
      required: true,
    })
    return {
      ...rule,
      id,
      kind,
      status,
      lifetime: 'current-deck',
      trigger: { event },
      target: { scope: 'deck' },
      action: { preserve },
      source,
      supersedes,
    }
  }

  if (!['slide-added', 'element-added'].includes(event)) {
    throw new Error(`${label}.trigger.event must be slide-added or element-added for style rules`)
  }
  if (target.slideScope !== 'future') throw new Error(`${label}.target.slideScope must be future`)
  const elementKind = requireString(target.elementKind, `${label}.target.elementKind`)
  if (!ELEMENT_KINDS.has(elementKind)) {
    throw new Error(`${label}.target.elementKind is unsupported: ${elementKind}`)
  }
  const normalizedAction = {}
  if (action.fontColor !== undefined) {
    normalizedAction.fontColor = normalizeHex(action.fontColor, `${label}.action.fontColor`)
  }
  if (action.fillColor !== undefined) {
    normalizedAction.fillColor = normalizeHex(action.fillColor, `${label}.action.fillColor`)
  }
  if (elementKind === 'slide-title') {
    if (!normalizedAction.fontColor || normalizedAction.fillColor) {
      throw new Error(`${label} slide-title action must contain only fontColor`)
    }
  } else if (!normalizedAction.fillColor || normalizedAction.fontColor) {
    throw new Error(`${label} summary-box action must contain only fillColor`)
  }
  return {
    ...rule,
    id,
    kind,
    status,
    lifetime: 'current-deck',
    trigger: { event },
    target: { slideScope: 'future', elementKind },
    action: normalizedAction,
    source,
    supersedes,
  }
}

function conflictFields(rule) {
  if (rule.kind !== 'future-element-style') return []
  return Object.keys(rule.action).map((field) => ({ field, value: rule.action[field] }))
}

function conflictKey(rule) {
  if (rule.kind !== 'future-element-style') return ''
  return `${rule.trigger.event}:${rule.target.elementKind}`
}

export function findActiveRuleConflicts(rules) {
  const conflicts = []
  const active = rules.filter(
    (rule) => rule.status === 'active' && rule.kind === 'future-element-style',
  )
  for (let leftIndex = 0; leftIndex < active.length; leftIndex += 1) {
    for (let rightIndex = leftIndex + 1; rightIndex < active.length; rightIndex += 1) {
      const left = active[leftIndex]
      const right = active[rightIndex]
      if (conflictKey(left) !== conflictKey(right)) continue
      for (const leftField of conflictFields(left)) {
        const rightField = conflictFields(right).find((item) => item.field === leftField.field)
        if (rightField && rightField.value !== leftField.value) {
          conflicts.push({
            code: 'active-rule-conflict',
            ruleIds: [left.id, right.id],
            event: left.trigger.event,
            elementKind: left.target.elementKind,
            field: leftField.field,
            values: [leftField.value, rightField.value],
          })
        }
      }
    }
  }
  return conflicts
}

function validateRuleGraph(rules) {
  const byId = new Map(rules.map((rule) => [rule.id, rule]))
  if (byId.size !== rules.length) throw new Error('session rule ids must be unique')
  for (const rule of rules) {
    if (rule.supersedes.includes(rule.id))
      throw new Error(`rule ${rule.id} cannot supersede itself`)
    for (const id of rule.supersedes) {
      const previous = byId.get(id)
      if (!previous) throw new Error(`rule ${rule.id} supersedes unknown rule ${id}`)
      if (previous.status !== 'superseded') {
        throw new Error(`rule ${id} must have status superseded before ${rule.id} can supersede it`)
      }
    }
  }
  const conflicts = findActiveRuleConflicts(rules)
  if (conflicts.length > 0) {
    const conflict = conflicts[0]
    throw new Error(
      `active rule conflict between ${conflict.ruleIds.join(' and ')} for ${conflict.elementKind}.${conflict.field}`,
    )
  }
}

function validateSourceFile(path) {
  const stat = statSync(path)
  if (!stat.isFile() || stat.size === 0) throw new Error(`source PPTX is empty: ${path}`)
  return stat
}

export function normalizeSessionRules(draft, sourcePath) {
  const document = requireObject(draft, 'session rules draft')
  if (document.schemaVersion !== SESSION_RULES_SCHEMA_VERSION) {
    throw new Error(`schemaVersion must be ${SESSION_RULES_SCHEMA_VERSION}`)
  }
  const deckIdentity = requireObject(document.deckIdentity, 'deckIdentity')
  const deckId = requireString(deckIdentity.deckId, 'deckIdentity.deckId')
  const rules = (
    Array.isArray(document.rules)
      ? document.rules
      : (() => {
          throw new Error('rules must be an array')
        })()
  ).map(normalizeRule)
  validateRuleGraph(rules)
  const absoluteSource = resolve(sourcePath)
  validateSourceFile(absoluteSource)
  return {
    ...document,
    schemaVersion: SESSION_RULES_SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    deckIdentity: {
      deckId,
      currentRevisionSha256: sha256File(absoluteSource),
      parentRevisionSha256: deckIdentity.parentRevisionSha256 ?? null,
    },
    rules,
  }
}

export function validateSessionRulesDocument(value) {
  const document = requireObject(value, 'session rules')
  if (document.schemaVersion !== SESSION_RULES_SCHEMA_VERSION) {
    throw new Error(`session rules schemaVersion must be ${SESSION_RULES_SCHEMA_VERSION}`)
  }
  const deckIdentity = requireObject(document.deckIdentity, 'deckIdentity')
  requireString(deckIdentity.deckId, 'deckIdentity.deckId')
  if (!/^[a-f0-9]{64}$/.test(String(deckIdentity.currentRevisionSha256 ?? ''))) {
    throw new Error('deckIdentity.currentRevisionSha256 must be a SHA-256 hex digest')
  }
  if (
    deckIdentity.parentRevisionSha256 !== null &&
    deckIdentity.parentRevisionSha256 !== undefined &&
    !/^[a-f0-9]{64}$/.test(String(deckIdentity.parentRevisionSha256))
  ) {
    throw new Error('deckIdentity.parentRevisionSha256 must be null or a SHA-256 hex digest')
  }
  const rules = (
    Array.isArray(document.rules)
      ? document.rules
      : (() => {
          throw new Error('rules must be an array')
        })()
  ).map(normalizeRule)
  validateRuleGraph(rules)
  return { ...document, deckIdentity: { ...deckIdentity }, rules }
}

export function advanceSessionRules(document, sourcePath) {
  const current = validateSessionRulesDocument(document)
  const absoluteSource = resolve(sourcePath)
  validateSourceFile(absoluteSource)
  return {
    ...current,
    observedAt: new Date().toISOString(),
    deckIdentity: {
      deckId: current.deckIdentity.deckId,
      currentRevisionSha256: sha256File(absoluteSource),
      parentRevisionSha256: current.deckIdentity.currentRevisionSha256,
    },
  }
}

export function normalizeSessionOperation(value) {
  const operation = requireObject(value, 'session operation')
  if (operation.schemaVersion !== SESSION_OPERATION_SCHEMA_VERSION) {
    throw new Error(`session operation schemaVersion must be ${SESSION_OPERATION_SCHEMA_VERSION}`)
  }
  const event = requireString(operation.event, 'session operation event')
  if (!OPERATION_EVENTS.has(event))
    throw new Error(`session operation event is unsupported: ${event}`)
  const slideCountDelta = operation.slideCountDelta ?? 0
  if (!Number.isInteger(slideCountDelta)) throw new Error('slideCountDelta must be an integer')
  if (!Array.isArray(operation.targets)) throw new Error('targets must be an array')
  const ids = new Set()
  const targets = operation.targets.map((value, index) => {
    const label = `targets[${index}]`
    const target = requireObject(value, label)
    const id = requireString(target.id, `${label}.id`)
    if (ids.has(id)) throw new Error(`duplicate operation target id: ${id}`)
    ids.add(id)
    if (target.kind !== 'produced-object') throw new Error(`${label}.kind must be produced-object`)
    if (!Number.isInteger(target.slide) || target.slide < 0) {
      throw new Error(`${label}.slide must be a non-negative integer`)
    }
    const elementKind = requireString(target.elementKind, `${label}.elementKind`)
    if (!ELEMENT_KINDS.has(elementKind)) throw new Error(`${label}.elementKind is unsupported`)
    const shapeName = requireString(target.shapeName, `${label}.shapeName`)
    if (!/^[A-Za-z0-9_.:-]+$/.test(shapeName)) {
      throw new Error(
        `${label}.shapeName must be a stable ASCII name without spaces or XML quoting`,
      )
    }
    const opIndexes = uniqueIntegers(target.opIndexes, `${label}.opIndexes`)
    const changeCategories = uniqueStrings(target.changeCategories, `${label}.changeCategories`, {
      allowed: CHANGE_CATEGORIES,
      required: true,
    })
    return {
      ...target,
      id,
      kind: 'produced-object',
      elementKind,
      shapeName,
      opIndexes,
      changeCategories,
    }
  })
  if (!Array.isArray(operation.explicitOverrides ?? [])) {
    throw new Error('explicitOverrides must be an array')
  }
  const explicitOverrides = (operation.explicitOverrides ?? []).map((value, index) => {
    const label = `explicitOverrides[${index}]`
    const item = requireObject(value, label)
    const ruleId = requireString(item.ruleId, `${label}.ruleId`)
    const source = requireObject(item.source, `${label}.source`)
    if (source.kind !== 'current-user-request') {
      throw new Error(`${label}.source.kind must be current-user-request`)
    }
    const quote = requireString(source.quote, `${label}.source.quote`)
    return { ruleId, source: { ...source, kind: 'current-user-request', quote } }
  })
  return {
    ...operation,
    schemaVersion: SESSION_OPERATION_SCHEMA_VERSION,
    event,
    slideCountDelta,
    targets,
    explicitOverrides,
  }
}

function eventMatches(ruleEvent, operationEvent) {
  if (ruleEvent === 'any-edit') return true
  return ruleEvent === operationEvent
}

function postconditions(rule) {
  const result = []
  if (rule.action.fontColor) result.push({ kind: 'font-color', value: rule.action.fontColor })
  if (rule.action.fillColor) result.push({ kind: 'fill-color', value: rule.action.fillColor })
  return result
}

export function resolveSessionRules({
  rulesDocument,
  operationDocument,
  sourcePath,
  rulesPath,
  operationPath,
}) {
  const rules = validateSessionRulesDocument(rulesDocument)
  const operation = normalizeSessionOperation(operationDocument)
  const absoluteSource = resolve(sourcePath)
  validateSourceFile(absoluteSource)
  const actualRevision = sha256File(absoluteSource)
  const blockers = []
  const conflicts = findActiveRuleConflicts(rules.rules)
  if (actualRevision !== rules.deckIdentity.currentRevisionSha256) {
    blockers.push({
      code: 'session-rules-revision-stale',
      message: 'session rules are bound to a different deck revision',
      expectedSha256: rules.deckIdentity.currentRevisionSha256,
      actualSha256: actualRevision,
    })
  }
  if (conflicts.length > 0) {
    blockers.push({
      code: 'session-rules-conflict',
      message: 'active session rules conflict and must be explicitly superseded',
      conflicts,
    })
  }

  const overridden = new Map(operation.explicitOverrides.map((item) => [item.ruleId, item]))
  for (const ruleId of overridden.keys()) {
    if (!rules.rules.some((rule) => rule.id === ruleId)) {
      throw new Error(`explicit override references unknown session rule: ${ruleId}`)
    }
  }
  const applicableRules = []
  const notApplicableRules = []
  const overlayTargets = []
  const preserve = []
  const allowedChanges = []
  const requiredEvidence = []

  if (blockers.length === 0) {
    for (const rule of rules.rules) {
      if (rule.status !== 'active') {
        notApplicableRules.push({ id: rule.id, reason: `status-${rule.status}` })
        continue
      }
      if (overridden.has(rule.id)) {
        notApplicableRules.push({
          id: rule.id,
          reason: 'explicitly-overridden',
          source: overridden.get(rule.id).source,
        })
        continue
      }
      if (!eventMatches(rule.trigger.event, operation.event)) {
        notApplicableRules.push({ id: rule.id, reason: 'event-not-matched' })
        continue
      }
      if (rule.kind === 'preserve-invariant') {
        if (rule.action.preserve.includes('slide-count') && operation.slideCountDelta !== 0) {
          blockers.push({
            code: 'session-rule-operation-conflict',
            message: `operation slideCountDelta=${operation.slideCountDelta} conflicts with session rule ${rule.id}`,
            ruleId: rule.id,
            preserve: 'slide-count',
          })
          continue
        }
        for (const item of rule.action.preserve) if (!preserve.includes(item)) preserve.push(item)
        if (
          rule.action.preserve.includes('target-text-style') &&
          !requiredEvidence.includes('style-diff')
        ) {
          requiredEvidence.push('style-diff')
        }
        applicableRules.push({ id: rule.id, kind: rule.kind, targetIds: [] })
        continue
      }
      const matchingTargets = operation.targets.filter(
        (target) => target.elementKind === rule.target.elementKind,
      )
      if (matchingTargets.length === 0) {
        notApplicableRules.push({ id: rule.id, reason: 'no-matching-target' })
        continue
      }
      const targetIds = []
      for (const target of matchingTargets) {
        const id = `session-rule:${rule.id}:${target.id}`
        targetIds.push(id)
        overlayTargets.push({
          id,
          kind: 'object',
          produced: true,
          slide: target.slide,
          opIndexes: target.opIndexes,
          selector: { shape: { name: target.shapeName } },
          resolvedIdentity: { slide: target.slide, name: target.shapeName },
          sessionRuleIds: [rule.id],
          expected: {
            changeCategories: target.changeCategories,
            sessionRulePostconditions: postconditions(rule),
          },
        })
        for (const category of target.changeCategories) {
          if (!allowedChanges.includes(category)) allowedChanges.push(category)
        }
      }
      if (!requiredEvidence.includes('final-inspect')) requiredEvidence.push('final-inspect')
      applicableRules.push({ id: rule.id, kind: rule.kind, targetIds })
    }
  }

  let nextAction = 'continue-without-session-rules'
  if (blockers.some((item) => item.code === 'session-rules-revision-stale')) {
    nextAction = 'refresh-session-rules-revision'
  } else if (blockers.length > 0) {
    nextAction = 'block-and-request-user-decision'
  } else if (overlayTargets.length > 0) {
    nextAction = 'write-rule-compliant-patch'
  } else if (applicableRules.length > 0) {
    nextAction = 'continue-with-contract-overlay'
  }

  const status = blockers.length === 0 ? 'pass' : 'fail'
  return {
    schemaVersion: SESSION_RESOLUTION_SCHEMA_VERSION,
    observedAt: new Date().toISOString(),
    status,
    source: { pptx: absoluteSource, sha256: actualRevision },
    sessionRules: {
      path: resolve(rulesPath),
      sha256: sha256File(rulesPath),
      deckId: rules.deckIdentity.deckId,
    },
    operation: {
      path: resolve(operationPath),
      sha256: sha256File(operationPath),
      event: operation.event,
    },
    applicableRules,
    notApplicableRules,
    conflicts,
    contractOverlay: { targets: overlayTargets, preserve, allowedChanges, requiredEvidence },
    blockers,
    agentGate: {
      schemaVersion: 'pptx-nova-agent-gate/v1',
      passed: status === 'pass',
      canContinue: status === 'pass',
      nextAction,
      blockerCount: blockers.length,
      applicableRuleCount: applicableRules.length,
      message:
        status === 'pass'
          ? `${applicableRules.length} session rule(s) resolved; next action: ${nextAction}.`
          : `Session rule resolution failed with ${blockers.length} blocker(s); next action: ${nextAction}.`,
    },
  }
}
