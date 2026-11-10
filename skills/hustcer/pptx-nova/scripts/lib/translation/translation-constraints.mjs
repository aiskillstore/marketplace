import { createHash } from 'node:crypto'

const MEMORY_SCHEMA = 'pptx-nova-translation-memory/v1'
const CONSTRAINTS_SCHEMA = 'pptx-nova-translation-constraints/v1'
const GLOSSARY_SCHEMA = 'pptx-nova-translation-glossary/v1'
const TRANSLATIONS_SCHEMA = 'pptx-i18n-translations/v1'

function memoryId(sourceText) {
  return `sha256:${createHash('sha256').update(sourceText).digest('hex')}`
}

function escapedToken(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function countExact(text, token) {
  const value = String(text ?? '')
  const needle = String(token ?? '')
  if (!needle) return 0
  let count = 0
  let offset = 0
  while (offset <= value.length - needle.length) {
    const index = value.indexOf(needle, offset)
    if (index < 0) break
    count += 1
    offset = index + needle.length
  }
  return count
}

function containsTerm(text, term, { caseSensitive = false, match = 'term' } = {}) {
  const value = String(text ?? '')
  const needle = String(term ?? '')
  if (!needle) return false
  if (match === 'substring') {
    return caseSensitive
      ? value.includes(needle)
      : value.toLowerCase().includes(needle.toLowerCase())
  }
  if (match !== 'term') throw new Error(`unsupported glossary match mode: ${match}`)
  const flags = caseSensitive ? 'gu' : 'giu'
  const pattern = new RegExp(
    `(?<![\\p{L}\\p{N}_])${escapedToken(needle)}(?![\\p{L}\\p{N}_])`,
    flags,
  )
  return pattern.test(value)
}

function addToken(map, token, kind) {
  const value = String(token ?? '').trim()
  if (!value || value.length < 2) return
  const entry = map.get(value) ?? { token: value, kinds: new Set() }
  entry.kinds.add(kind)
  map.set(value, entry)
}

function collectInlineCodeTokens(text, tokens) {
  for (const match of String(text ?? '').matchAll(/`([^`\n]+)`/g)) {
    const content = match[1]?.trim()
    if (!content) continue
    if (/^[A-Za-z_][A-Za-z0-9_./:@+-]*$/u.test(content)) {
      addToken(tokens, content, 'inline-code')
    }
    for (const identifier of content.matchAll(/[A-Za-z_][A-Za-z0-9_-]*/g)) {
      addToken(tokens, identifier[0], 'inline-code')
    }
  }
}

function collectQuotedIdentifierTokens(text, tokens) {
  for (const match of String(text ?? '').matchAll(/(["'])([A-Za-z_][A-Za-z0-9_-]*)\1/g)) {
    addToken(tokens, match[2], 'quoted-identifier')
  }
}

function isTechnicalSlashIdentifier(token) {
  const [left, right] = String(token).split('/')
  return /[\d_-]/u.test(token) || /[A-Z]/u.test(left ?? '') || /[A-Z]/u.test(right ?? '')
}

/**
 * Extract only high-confidence technical tokens. Ordinary natural-language
 * words are deliberately excluded; ambiguous short labels are reported
 * separately as manual-review warnings.
 */
export function extractProtectedTokens(text) {
  const value = String(text ?? '')
  const tokens = new Map()
  collectInlineCodeTokens(value, tokens)
  collectQuotedIdentifierTokens(value, tokens)
  const patterns = [
    ['url', /\b[a-z][a-z0-9+.-]*:\/\/[^\s<>"'`]+/giu],
    ['email', /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/giu],
    ['cli-flag', /(?:^|[^\p{L}\p{N}_])(--[A-Za-z0-9][A-Za-z0-9-]*(?:=[^\s<>"'`]+)?)/gu],
    ['qname', /\b[A-Za-z_][A-Za-z0-9_.-]*:[A-Za-z_][A-Za-z0-9_.-]*\b/gu],
    ['contract-id', /\b[A-Za-z][A-Za-z0-9._-]*\/v\d+(?:\.\d+)*\b/gu],
    [
      'filename',
      /(?:[A-Za-z0-9_@.+-]+[\\/])*[A-Za-z0-9_@.+-]+\.(?:pptx|potx|xlsx|xls|json|jsonl|xml|css|js|mjs|ts|tsx|html|md|csv|svg|png|jpe?g|pdf|wasm|mbt|nu|sh|toml|ya?ml|zip)\b/giu,
    ],
    ['qualified-identifier', /\b[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)+\b/gu],
    ['function', /\b[A-Za-z_$][A-Za-z0-9_$]*(?=\()/gu],
    [
      'camel-case',
      /\b(?:[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*|[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)\b/gu,
    ],
    ['snake-case', /\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b/gu],
    ['slash-identifier', /\b[A-Za-z_][A-Za-z0-9_-]*\/[A-Za-z_][A-Za-z0-9_-]*\b/gu],
    ['acronym', /\b[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)*\b/g],
  ]
  for (const [kind, pattern] of patterns) {
    for (const match of value.matchAll(pattern)) {
      // The CLI-flag pattern has a leading boundary capture.
      const matched = kind === 'cli-flag' ? match[1] : match[0]
      const token = kind === 'url' ? matched.replace(/[),.;:!?\]}]+$/u, '') : matched
      if (kind === 'slash-identifier' && !isTechnicalSlashIdentifier(token)) continue
      addToken(tokens, token, kind)
    }
  }
  const urlTokens = [...tokens.values()]
    .filter((entry) => entry.kinds.has('url'))
    .map((entry) => entry.token)
  return [...tokens.values()]
    .map((entry) => ({
      token: entry.token,
      count: countExact(value, entry.token),
      kinds: [...entry.kinds].sort(),
    }))
    .filter((entry) => entry.count > 0)
    .filter(
      (entry) =>
        entry.kinds.includes('url') ||
        !urlTokens.some((url) => url !== entry.token && url.includes(entry.token)),
    )
    .sort((left, right) => left.token.localeCompare(right.token))
}

export function highRiskShortWord(text) {
  const value = String(text ?? '').trim()
  if (!/^[A-Za-z]{2,4}$/u.test(value) || value === value.toUpperCase()) return null
  return {
    sourceText: value,
    reason: 'short-standalone-source-text',
    message:
      'Short standalone labels are semantically ambiguous; review the target manually instead of relying on a language model guess.',
  }
}

function normalizeGlossaryEntry(entry, index) {
  if (!entry || typeof entry !== 'object') {
    throw new Error(`glossary entry ${index + 1} must be an object`)
  }
  const source = typeof entry.source === 'string' ? entry.source.trim() : ''
  const target = typeof entry.target === 'string' ? entry.target.trim() : ''
  if (!source || !target) {
    throw new Error(`glossary entry ${index + 1} requires non-empty source and target`)
  }
  const match = entry.match ?? 'term'
  if (!['term', 'substring'].includes(match)) {
    throw new Error(`glossary entry ${index + 1} match must be term or substring`)
  }
  return {
    id: String(entry.id ?? `term-${index + 1}`),
    source,
    target,
    match,
    caseSensitive: entry.caseSensitive === true,
    note: typeof entry.note === 'string' ? entry.note : null,
  }
}

export function normalizeTranslationGlossary(value, { targetLang = '' } = {}) {
  if (value === null || value === undefined || value === '') return null
  if (typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('translation glossary must be a JSON object')
  }
  if (value.schemaVersion !== GLOSSARY_SCHEMA) {
    throw new Error(`translation glossary must use ${GLOSSARY_SCHEMA}`)
  }
  if (
    value.targetLang &&
    targetLang &&
    String(value.targetLang).toLowerCase() !== String(targetLang).toLowerCase()
  ) {
    throw new Error(
      `translation glossary targetLang ${value.targetLang} does not match target language ${targetLang}`,
    )
  }
  if (!Array.isArray(value.entries))
    throw new Error('translation glossary entries must be an array')
  const entries = value.entries.map(normalizeGlossaryEntry)
  const ids = new Set()
  const signatures = new Set()
  for (const entry of entries) {
    if (ids.has(entry.id))
      throw new Error(`translation glossary contains duplicate id: ${entry.id}`)
    ids.add(entry.id)
    const signature = JSON.stringify([entry.source, entry.match, entry.caseSensitive])
    if (signatures.has(signature)) {
      throw new Error(`translation glossary contains duplicate source term: ${entry.source}`)
    }
    signatures.add(signature)
  }
  return {
    schemaVersion: GLOSSARY_SCHEMA,
    sourceLang: value.sourceLang ?? null,
    targetLang: value.targetLang ?? targetLang ?? null,
    entries,
  }
}

function applicableGlossaryEntries(sourceText, glossary) {
  return (glossary?.entries ?? []).filter((entry) => containsTerm(sourceText, entry.source, entry))
}

export function buildTranslationConstraints(
  memory,
  { glossary = null, sourceSha256 = null, unitsSha256 = null } = {},
) {
  if (memory?.schemaVersion !== MEMORY_SCHEMA) {
    throw new Error(`translation memory must use ${MEMORY_SCHEMA}`)
  }
  const normalizedGlossary = normalizeTranslationGlossary(glossary, {
    targetLang: memory.targetLang,
  })
  const entries = []
  const highRiskShortWords = []
  let protectedTokenCount = 0
  let glossaryRuleCount = 0
  for (const memoryEntry of memory.entries ?? []) {
    const protectedTokens = extractProtectedTokens(memoryEntry.sourceText)
    const glossaryEntries = applicableGlossaryEntries(memoryEntry.sourceText, normalizedGlossary)
    const shortRisk = highRiskShortWord(memoryEntry.sourceText)
    if (shortRisk) highRiskShortWords.push({ memoryId: memoryEntry.memoryId, ...shortRisk })
    if (protectedTokens.length === 0 && glossaryEntries.length === 0 && !shortRisk) continue
    protectedTokenCount += protectedTokens.length
    glossaryRuleCount += glossaryEntries.length
    entries.push({
      memoryId: memoryEntry.memoryId,
      sourceText: memoryEntry.sourceText,
      protectedTokens,
      glossary: glossaryEntries,
      highRisk: shortRisk ? { reason: shortRisk.reason, message: shortRisk.message } : null,
    })
  }
  return {
    schemaVersion: CONSTRAINTS_SCHEMA,
    source: { sha256: sourceSha256 ?? memory.source?.sha256 ?? null },
    units: { sha256: unitsSha256 ?? memory.units?.sha256 ?? null },
    sourceLang: memory.sourceLang ?? null,
    targetLang: memory.targetLang ?? null,
    glossary: normalizedGlossary
      ? {
          schemaVersion: GLOSSARY_SCHEMA,
          targetLang: normalizedGlossary.targetLang,
          entryCount: normalizedGlossary.entries.length,
          entries: normalizedGlossary.entries,
        }
      : null,
    summary: {
      constrainedEntryCount: entries.length,
      protectedTokenCount,
      glossaryRuleCount,
      highRiskShortWordCount: highRiskShortWords.length,
    },
    highRiskShortWords,
    entries,
  }
}

function uniqueStrings(values) {
  return [...new Set(values)].sort()
}

function targetTokenSet(text) {
  return new Map(extractProtectedTokens(text).map((entry) => [entry.token, entry]))
}

/**
 * Validate the effective per-unit translation contract, rather than only the
 * deduplicated memory entries. This catches unitOverrides that intentionally
 * use different wording while keeping one shared memory entry.
 */
export function validateTranslationConstraints(translations, constraints) {
  if (translations?.schemaVersion !== TRANSLATIONS_SCHEMA) {
    throw new Error(`translations must use ${TRANSLATIONS_SCHEMA}`)
  }
  if (constraints?.schemaVersion !== CONSTRAINTS_SCHEMA) {
    throw new Error(`translation constraints must use ${CONSTRAINTS_SCHEMA}`)
  }
  const byMemoryId = new Map((constraints.entries ?? []).map((entry) => [entry.memoryId, entry]))
  const grouped = new Map()
  for (const record of translations.translations ?? []) {
    if (!record || typeof record.sourceText !== 'string') continue
    const id = memoryId(record.sourceText)
    const entry = byMemoryId.get(id)
    if (!entry) continue
    const group = grouped.get(id) ?? {
      entry,
      targets: new Map(),
    }
    const target = String(record.targetText ?? '')
    const targetGroup = group.targets.get(target) ?? { targetText: target, unitIds: [] }
    targetGroup.unitIds.push(record.unitId)
    group.targets.set(target, targetGroup)
    grouped.set(id, group)
  }

  const violations = []
  const tokenDiffs = []
  const warnings = []
  for (const { entry, targets } of grouped.values()) {
    for (const targetGroup of targets.values()) {
      const missing = []
      const targetTokens = targetTokenSet(targetGroup.targetText)
      for (const protectedToken of entry.protectedTokens ?? []) {
        const actualCount = countExact(targetGroup.targetText, protectedToken.token)
        if (actualCount !== protectedToken.count) {
          missing.push({
            token: protectedToken.token,
            kinds: protectedToken.kinds,
            expectedCount: protectedToken.count,
            actualCount,
          })
        }
      }
      const sourceTokenNames = new Set((entry.protectedTokens ?? []).map((item) => item.token))
      const unexpected = [...targetTokens.values()]
        .filter((item) => !sourceTokenNames.has(item.token))
        .map((item) => ({ token: item.token, count: item.count, kinds: item.kinds }))
        .sort((left, right) => left.token.localeCompare(right.token))
      if (missing.length > 0 || unexpected.length > 0) {
        const diff = {
          memoryId: entry.memoryId,
          sourceText: entry.sourceText,
          targetText: targetGroup.targetText,
          unitIds: uniqueStrings(targetGroup.unitIds),
          missing,
          unexpected,
        }
        tokenDiffs.push(diff)
        if (missing.length > 0) {
          violations.push({
            kind: 'protected-token-mismatch',
            ...diff,
          })
        } else {
          warnings.push({
            kind: 'unexpected-technical-token',
            ...diff,
          })
        }
      }
      for (const glossaryEntry of entry.glossary ?? []) {
        if (!containsTerm(targetGroup.targetText, glossaryEntry.target, glossaryEntry)) {
          violations.push({
            kind: 'glossary-mismatch',
            memoryId: entry.memoryId,
            sourceText: entry.sourceText,
            targetText: targetGroup.targetText,
            unitIds: uniqueStrings(targetGroup.unitIds),
            glossaryId: glossaryEntry.id,
            sourceTerm: glossaryEntry.source,
            expectedTargetTerm: glossaryEntry.target,
          })
        }
      }
      if (entry.highRisk) {
        warnings.push({
          kind: 'high-risk-short-word',
          memoryId: entry.memoryId,
          sourceText: entry.sourceText,
          targetText: targetGroup.targetText,
          unitIds: uniqueStrings(targetGroup.unitIds),
          reason: entry.highRisk.reason,
          message: entry.highRisk.message,
        })
      }
    }
  }
  const uniqueWarnings = warnings.filter(
    (warning, index, all) =>
      index ===
      all.findIndex(
        (candidate) =>
          candidate.kind === warning.kind &&
          candidate.memoryId === warning.memoryId &&
          candidate.targetText === warning.targetText,
      ),
  )
  return {
    schemaVersion: 'pptx-nova-translation-constraints-check/v1',
    status: violations.length === 0 ? 'pass' : 'blocked',
    agentGate: {
      passed: violations.length === 0,
      blockerCount: violations.length,
      warningCount: uniqueWarnings.length,
    },
    summary: {
      checkedEntryCount: grouped.size,
      constrainedEntryCount: constraints.summary?.constrainedEntryCount ?? 0,
      protectedTokenCount: constraints.summary?.protectedTokenCount ?? 0,
      glossaryRuleCount: constraints.summary?.glossaryRuleCount ?? 0,
      highRiskShortWordCount: constraints.summary?.highRiskShortWordCount ?? 0,
      violationCount: violations.length,
      warningCount: uniqueWarnings.length,
    },
    tokenDiffs,
    violations,
    warnings: uniqueWarnings,
    nextAction:
      violations.length === 0
        ? 'Protected technical tokens and glossary terms passed; review high-risk short-word warnings before finalizing wording.'
        : 'Repair the named targetText values while preserving protected tokens and glossary terms, then rerun preparation with --apply --overwrite.',
  }
}

export const translationConstraintsSchemas = {
  memory: MEMORY_SCHEMA,
  glossary: GLOSSARY_SCHEMA,
  constraints: CONSTRAINTS_SCHEMA,
  check: 'pptx-nova-translation-constraints-check/v1',
}
