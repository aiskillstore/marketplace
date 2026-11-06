import { createHash } from 'node:crypto'

const MEMORY_SCHEMA = 'pptx-nova-translation-memory/v1'
const TRANSLATIONS_SCHEMA = 'pptx-i18n-translations/v1'

function memoryId(sourceText) {
  return `sha256:${createHash('sha256').update(sourceText).digest('hex')}`
}

function unitsFrom(scan) {
  const units = scan?.i18nUnits?.units
  if (scan?.schemaVersion !== 'pptx-i18n-scan/v1' || !Array.isArray(units)) {
    throw new Error('scan must be pptx-i18n-scan/v1 with i18nUnits.units[]')
  }
  return units
}

function hasExecutableSelector(unit) {
  const selectors = unit?.selectors
  return Boolean(selectors?.textPlan || selectors?.replaceText || selectors?.replaceChartText)
}

function reviewPartition(unit, sharedParts) {
  if (unit?.category === 'embeddedWorkbook') return 'embeddedWorkbook'
  if (unit?.notes?.includes?.('language-classification-uncertain')) return 'languageUncertain'
  if (sharedParts.includes(unit?.part)) return 'shared'
  return 'other'
}

export function expandReviewInventory(scan, partition, sharedParts = []) {
  const allowed = new Set(['languageUncertain', 'shared', 'embeddedWorkbook', 'other'])
  if (!allowed.has(partition)) throw new Error(`unsupported review partition: ${partition}`)
  const units = unitsFrom(scan).filter(
    (unit) => unit.action === 'review' && reviewPartition(unit, sharedParts) === partition,
  )
  return {
    schemaVersion: 'pptx-nova-i18n-review-inventory/v1',
    partition,
    count: units.length,
    units,
  }
}

function partitionSummary(units, name, sharedParts) {
  const members = units.filter(
    (unit) => unit.action === 'review' && reviewPartition(unit, sharedParts) === name,
  )
  return {
    count: members.length,
    categories: [...new Set(members.map((unit) => unit.category).filter(Boolean))].sort(),
    parts: [...new Set(members.map((unit) => unit.part).filter(Boolean))].length,
    expansion:
      'Read matching units from the bound full scan only when this partition is actionable.',
  }
}

export function buildTranslationMemory(
  scan,
  { sourceSha256, unitsSha256, targetLang, sharedParts = [] },
) {
  if (!sourceSha256 || !unitsSha256 || !targetLang) {
    throw new Error('sourceSha256, unitsSha256, and targetLang are required')
  }
  const units = unitsFrom(scan)
  const eligible = units.filter(
    (unit) =>
      unit.action === 'translate' ||
      (unit.action === 'review' &&
        unit.category !== 'embeddedWorkbook' &&
        hasExecutableSelector(unit)),
  )
  const grouped = new Map()
  for (const unit of eligible) {
    const id = memoryId(unit.sourceText)
    const entry = grouped.get(id) ?? {
      memoryId: id,
      sourceText: unit.sourceText,
      targetText: null,
      contexts: [],
    }
    entry.contexts.push({
      unitId: unit.unitId,
      sourceHash: unit.sourceHash,
      action: unit.action,
      category: unit.category,
      part: unit.part ?? null,
      slide: unit.slide ?? null,
      recommendedMethod: unit.recommendedMethod ?? null,
      requiresReview: unit.requiresReview === true,
    })
    grouped.set(id, entry)
  }
  const entries = [...grouped.values()].sort((left, right) => {
    const leftOrder = units.findIndex((unit) => unit.unitId === left.contexts[0]?.unitId)
    const rightOrder = units.findIndex((unit) => unit.unitId === right.contexts[0]?.unitId)
    return leftOrder - rightOrder
  })
  return {
    schemaVersion: MEMORY_SCHEMA,
    source: { sha256: sourceSha256 },
    units: { sha256: unitsSha256 },
    sourceLang: scan.sourceLang ?? scan?.i18nUnits?.sourceLang ?? null,
    targetLang,
    summary: {
      eligibleUnitCount: eligible.length,
      uniqueSourceTextCount: entries.length,
      savedTranslationRecordCount: eligible.length - entries.length,
      reductionRatio:
        eligible.length === 0
          ? 0
          : Number(((eligible.length - entries.length) / eligible.length).toFixed(4)),
    },
    reviewPartitions: {
      languageUncertain: partitionSummary(units, 'languageUncertain', sharedParts),
      shared: partitionSummary(units, 'shared', sharedParts),
      embeddedWorkbook: partitionSummary(units, 'embeddedWorkbook', sharedParts),
      other: partitionSummary(units, 'other', sharedParts),
    },
    entries,
    unitOverrides: [],
  }
}

// The fill view exposes exactly what an agent needs to translate — memoryId,
// sourceText, and a targetText slot — as JSONL. The full memory keeps
// contexts[] and hashes on disk; the agent never has to load them.
export function buildMemoryFillView(memory) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  return `${(memory.entries ?? [])
    .map((entry) =>
      JSON.stringify({
        memoryId: entry.memoryId,
        sourceText: entry.sourceText,
        targetText: entry.targetText ?? null,
      }),
    )
    .join('\n')}\n`
}

// Merge a (possibly partial) JSONL fill back into the memory. Lines carry
// {memoryId, sourceText?, targetText}; unknown ids, stale sourceText, and
// unfilled targetText fail closed so a truncated or hand-edited fill cannot
// silently drop translations.
export function applyMemoryFill(memory, fillText) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  const merged = structuredClone(memory)
  const byId = new Map((merged.entries ?? []).map((entry) => [entry.memoryId, entry]))
  const problems = []
  let filledCount = 0
  const lines = String(fillText ?? '')
    .split('\n')
    .map((line, index) => ({ line: line.trim(), lineNumber: index + 1 }))
    .filter(({ line }) => line.length > 0)
  if (lines.length === 0) throw new Error('memory fill contains no entries')
  for (const { line, lineNumber } of lines) {
    let record = null
    try {
      record = JSON.parse(line)
    } catch (error) {
      problems.push(`line ${lineNumber}: invalid JSON (${error.message})`)
      continue
    }
    const entry = byId.get(record?.memoryId)
    if (!entry) {
      problems.push(`line ${lineNumber}: unknown memoryId ${record?.memoryId ?? '(missing)'}`)
      continue
    }
    if (typeof record.sourceText === 'string' && record.sourceText !== entry.sourceText) {
      problems.push(`line ${lineNumber}: sourceText is stale for ${record.memoryId}`)
      continue
    }
    if (typeof record.targetText !== 'string') {
      problems.push(`line ${lineNumber}: targetText must be filled for ${record.memoryId}`)
      continue
    }
    entry.targetText = record.targetText
    filledCount += 1
  }
  if (problems.length > 0) {
    const shown = problems.slice(0, 10).join('; ')
    const suffix = problems.length > 10 ? ` (+${problems.length - 10} more)` : ''
    throw new Error(`memory fill rejected: ${shown}${suffix}`)
  }
  return { memory: merged, filledCount }
}

export function materializeTranslations(scan, memory) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  const units = unitsFrom(scan)
  const entriesByUnit = new Map()
  for (const entry of memory.entries ?? []) {
    if (!entry?.memoryId || typeof entry.sourceText !== 'string') {
      throw new Error('translation memory contains an invalid entry')
    }
    for (const context of entry.contexts ?? []) {
      if (!context?.unitId || entriesByUnit.has(context.unitId)) {
        throw new Error(
          `translation memory contains a missing or duplicate unit context: ${context?.unitId}`,
        )
      }
      entriesByUnit.set(context.unitId, entry)
    }
  }
  const overrides = new Map()
  for (const override of memory.unitOverrides ?? []) {
    if (!override?.unitId || overrides.has(override.unitId)) {
      throw new Error('unitOverrides contain a missing or duplicate unitId')
    }
    overrides.set(override.unitId, override)
  }

  const translations = []
  for (const unit of units) {
    if (unit.action !== 'translate' && unit.action !== 'review') continue
    const entry = entriesByUnit.get(unit.unitId)
    const override = overrides.get(unit.unitId)
    if (unit.action === 'review' && override?.reviewDecision === 'preserve') continue
    if (!entry) continue
    if (entry.sourceText !== unit.sourceText) {
      throw new Error(`translation memory sourceText is stale for ${unit.unitId}`)
    }
    const targetText = override?.targetText ?? entry.targetText
    if (typeof targetText !== 'string') {
      throw new Error(`targetText is required for ${unit.unitId}`)
    }
    const record = {
      unitId: unit.unitId,
      sourceHash: unit.sourceHash,
      sourceText: unit.sourceText,
      targetText,
    }
    if (unit.action === 'review') {
      if (override?.reviewDecision !== 'translate') {
        throw new Error(`reviewDecision:"translate" is required for ${unit.unitId}`)
      }
      record.reviewDecision = 'translate'
    }
    for (const key of ['anchors', 'targetSegments', 'targetSegmentsContractId']) {
      if (override?.[key] !== undefined) record[key] = override[key]
    }
    translations.push(record)
  }
  for (const unitId of overrides.keys()) {
    if (!units.some((unit) => unit.unitId === unitId)) {
      throw new Error(`unitOverrides reference unknown unitId: ${unitId}`)
    }
  }
  return {
    schemaVersion: TRANSLATIONS_SCHEMA,
    sourceLang: memory.sourceLang,
    targetLang: memory.targetLang,
    translations,
  }
}

function countOccurrences(text, needle) {
  if (!needle) return 0
  let count = 0
  let cursor = 0
  while (cursor <= text.length - needle.length) {
    const found = text.indexOf(needle, cursor)
    if (found < 0) break
    count += 1
    cursor = found + 1
  }
  return count
}

export function mergeTranslationMemoryAnchorDrafts(memory, draft) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  if (draft?.schemaVersion !== 'pptx-i18n-anchor-draft/v1') {
    throw new Error('anchor draft must use pptx-i18n-anchor-draft/v1')
  }
  if (draft?.agentGate?.applyAuthorized !== false) {
    throw new Error('an anchor draft must never authorize apply')
  }
  const translations = draft?.translationsDraft?.translations
  const draftItems = draft?.drafts
  const blockedItems = draft?.blocked
  if (
    draft?.translationsDraft?.schemaVersion !== 'pptx-i18n-anchor-merge/v1' ||
    draft?.translationsDraft?.targetSchemaVersion !== TRANSLATIONS_SCHEMA ||
    draft?.translationsDraft?.mergeBy !== 'unitId' ||
    !Array.isArray(translations) ||
    !Array.isArray(draftItems) ||
    !Array.isArray(blockedItems)
  ) {
    throw new Error('anchor draft report arrays or translationsDraft contract are invalid')
  }
  if (
    draft?.summary?.draftCount !== draftItems.length ||
    draft?.summary?.blockedCount !== blockedItems.length ||
    draftItems.length !== translations.length
  ) {
    throw new Error('anchor draft summary counts do not match the report arrays')
  }
  if (draft?.agentGate?.plannerRerunRequired !== translations.length > 0) {
    throw new Error('anchor draft plannerRerunRequired does not match its draft count')
  }

  const merged = structuredClone(memory)
  const highConfidenceDrafts = new Map()
  for (const item of draftItems) {
    if (
      !item?.unitId ||
      item.confidence !== 'high' ||
      highConfidenceDrafts.has(item.unitId) ||
      typeof item.sourceHash !== 'string' ||
      typeof item.sourceText !== 'string' ||
      typeof item.targetText !== 'string' ||
      !Array.isArray(item.candidateAnchors) ||
      item.candidateAnchors.length === 0 ||
      item.candidateAnchors.some(
        (candidate) => typeof candidate?.targetText !== 'string' || !candidate.targetText.trim(),
      )
    ) {
      throw new Error('anchor draft drafts[] must contain unique high-confidence unitIds')
    }
    highConfidenceDrafts.set(item.unitId, item)
  }
  const blockedIds = new Set(
    blockedItems.map((item) => item?.unitId).filter((unitId) => typeof unitId === 'string'),
  )
  const units = new Map()
  for (const entry of merged.entries ?? []) {
    for (const context of entry.contexts ?? []) {
      if (!context?.unitId || units.has(context.unitId)) {
        throw new Error(
          `translation memory contains a missing or duplicate unit context: ${context?.unitId}`,
        )
      }
      units.set(context.unitId, { context, entry })
    }
  }
  const overrides = new Map((merged.unitOverrides ?? []).map((item) => [item.unitId, item]))
  const seen = new Set()
  for (const translation of translations) {
    const unitId = translation?.unitId
    if (!unitId || seen.has(unitId)) {
      throw new Error(`anchor drafts contain a missing or duplicate unitId: ${unitId}`)
    }
    seen.add(unitId)
    const evidence = highConfidenceDrafts.get(unitId)
    if (!evidence || blockedIds.has(unitId)) {
      throw new Error(`anchor draft merge projection is not high-confidence for ${unitId}`)
    }
    const unit = units.get(unitId)
    if (!unit) throw new Error(`anchor draft references unknown unitId: ${unitId}`)
    if (translation.sourceHash !== unit.context.sourceHash) {
      throw new Error(`anchor draft sourceHash is stale for ${unitId}`)
    }
    if (translation.sourceText !== unit.entry.sourceText) {
      throw new Error(`anchor draft sourceText is stale for ${unitId}`)
    }
    const prior = overrides.get(unitId) ?? { unitId }
    const expectedTarget = prior.targetText ?? unit.entry.targetText
    if (typeof expectedTarget !== 'string' || translation.targetText !== expectedTarget) {
      throw new Error(`anchor draft targetText is stale for ${unitId}`)
    }
    if (
      !Array.isArray(translation.anchors) ||
      translation.anchors.length === 0 ||
      translation.anchors.some((anchor) => typeof anchor !== 'string' || !anchor.trim())
    ) {
      throw new Error(`anchor draft anchors are invalid for ${unitId}`)
    }
    const evidenceAnchors = evidence.candidateAnchors.map((candidate) => candidate.targetText)
    if (
      evidence.sourceHash !== translation.sourceHash ||
      evidence.sourceText !== translation.sourceText ||
      evidence.targetText !== translation.targetText ||
      JSON.stringify(evidenceAnchors) !== JSON.stringify(translation.anchors)
    ) {
      throw new Error(`anchor draft merge projection does not match draft evidence for ${unitId}`)
    }
    let cursor = 0
    for (const anchor of translation.anchors) {
      if (countOccurrences(expectedTarget, anchor) !== 1) {
        throw new Error(`anchor draft anchor is not unique for ${unitId}`)
      }
      const found = expectedTarget.indexOf(anchor, cursor)
      if (found < cursor) throw new Error(`anchor draft anchors are out of order for ${unitId}`)
      cursor = found + anchor.length
    }
    if (
      prior.anchors !== undefined &&
      JSON.stringify(prior.anchors) !== JSON.stringify(translation.anchors)
    ) {
      throw new Error(`anchor draft conflicts with existing anchors for ${unitId}`)
    }
    overrides.set(unitId, { ...prior, anchors: structuredClone(translation.anchors) })
  }
  merged.unitOverrides = [...overrides.values()]
  return {
    memory: merged,
    anchorDraftMerge: {
      schemaVersion: 'pptx-nova-translation-anchor-draft-merge/v1',
      unitCount: translations.length,
      unitIds: [...seen],
      plannerRerunRequired: translations.length > 0,
    },
  }
}

export function mergeTranslationMemoryRepairs(memory, plan) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  const merged = structuredClone(memory)
  const overrides = new Map((merged.unitOverrides ?? []).map((item) => [item.unitId, item]))
  const repairedUnitIds = []
  for (const review of plan?.reviewRequired ?? []) {
    const repair = review?.repair
    const template = repair?.translationPatchTemplate
    if (
      repair?.schemaVersion !== 'pptx-i18n-target-segments-repair/v1' ||
      repair?.kind !== 'target-segments' ||
      !template?.unitId ||
      !Array.isArray(template.targetSegments)
    ) {
      continue
    }
    const prior = overrides.get(template.unitId) ?? { unitId: template.unitId }
    const next = { ...prior }
    for (const key of [
      'targetText',
      'targetSegments',
      'targetSegmentsContractId',
      'anchors',
      'reviewDecision',
    ]) {
      if (template[key] !== undefined) next[key] = structuredClone(template[key])
    }
    overrides.set(template.unitId, next)
    repairedUnitIds.push(template.unitId)
  }
  merged.unitOverrides = [...overrides.values()]
  merged.repairScaffold = {
    schemaVersion: 'pptx-nova-translation-memory-repair/v1',
    unitCount: repairedUnitIds.length,
    unitIds: repairedUnitIds,
    ready: repairedUnitIds.every((unitId) =>
      (overrides.get(unitId)?.targetSegments ?? []).every(
        (segment) => typeof segment?.text === 'string',
      ),
    ),
    instructions:
      'Fill every targetSegments[].text value, keep targetSegmentsContractId unchanged, then rerun with --apply --overwrite passing this repair file via --memory. Any further scaffold is written to a new translation-memory.repair-N.json, so the file you pass back stays read-only. Segments must keep the source run-group order: when the natural target word order would move text across a group boundary (German/Japanese/Korean verb placement around a hyperlink), rewrite into an order-preserving equivalent such as the German imperative instead of reordering groups.',
  }
  return merged
}
