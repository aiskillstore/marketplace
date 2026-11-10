function unitsFrom(value) {
  const units = value?.i18nUnits?.units
  if (value?.schemaVersion !== 'pptx-i18n-scan/v1') {
    throw new Error('--units-file must use pptx-i18n-scan/v1')
  }
  return { units: Array.isArray(units) ? units : [], complete: Array.isArray(units) }
}

function translationsFrom(value) {
  if (value?.schemaVersion !== 'pptx-i18n-translations/v1' || !Array.isArray(value.translations)) {
    throw new Error('--translations must use pptx-i18n-translations/v1')
  }
  return value.translations
}

export function parseTextAttributeAllowlist(value) {
  const entries = String(value ?? '')
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean)
  for (const entry of entries) {
    if (!/^[A-Za-z_][A-Za-z0-9_.:-]*$/u.test(entry)) {
      throw new Error(`invalid --allow-text-attrs entry: ${entry}`)
    }
  }
  return [...new Set(entries)].sort()
}

/**
 * Derive the exact typed user-visible attributes that the effective
 * translation contract intends to change. The runner uses this before any
 * xdoc process starts; it suggests but never grants missing authorization.
 */
export function analyzeTypedTextAttributeAllowlist(unitsContract, translationsContract, allowlist) {
  const unitContract = unitsFrom(unitsContract)
  const translations = translationsFrom(translationsContract)
  if (!unitContract.complete && translations.length > 0) {
    throw new Error('--units-file must contain i18nUnits.units[] when translations are present')
  }
  const units = unitContract.units
  const translatedByUnit = new Map()
  for (const translation of translations) {
    if (!translation?.unitId) continue
    if (translatedByUnit.has(translation.unitId)) {
      throw new Error(`translations contain duplicate unitId: ${translation.unitId}`)
    }
    translatedByUnit.set(translation.unitId, translation)
  }
  const required = new Map()
  for (const unit of units) {
    if (unit?.category !== 'visibleTextAttr') continue
    const translation = translatedByUnit.get(unit.unitId)
    if (!translation || translation.targetText === unit.sourceText) continue
    if (typeof translation.targetText !== 'string') continue
    const attrName = unit.origin?.attrName ?? unit.selectors?.replaceText?.attrName
    if (!attrName) {
      throw new Error(
        `visibleTextAttr unit does not disclose origin.attrName or selectors.replaceText.attrName: ${unit.unitId}`,
      )
    }
    const normalized = String(attrName)
    const entry = required.get(normalized) ?? { attrName: normalized, unitIds: [] }
    entry.unitIds.push(unit.unitId)
    required.set(normalized, entry)
  }
  const allowed = new Set(parseTextAttributeAllowlist(allowlist))
  const requiredEntries = [...required.values()]
    .map((entry) => ({
      ...entry,
      unitIds: [...entry.unitIds].sort(),
      unitCount: entry.unitIds.length,
    }))
    .sort((left, right) => left.attrName.localeCompare(right.attrName))
  const missing = requiredEntries.filter((entry) => !allowed.has(entry.attrName))
  return {
    complete: unitContract.complete,
    allowed: [...allowed].sort(),
    required: requiredEntries,
    missing,
    suggestedAllowlist: [...new Set([...allowed, ...required.keys()])].sort(),
  }
}
