import { canonicalSha256V1 } from '../runtime/canonical-json.mjs'

export const FONT_NORMALIZATION_EVIDENCE = [
  'dry-run',
  'semantic-diff',
  'png-preview',
  'vision-diff',
  'final-inspect',
  'structure-check',
]

export function documentFontTarget(contract) {
  return contract.targets?.find((target) => target.kind === 'document-fonts') ?? null
}

// This is a deliberately narrow document target, not a selector bypass for
// arbitrary all-slides-style operations. Validate again at the consuming gate.
export function validateFontContract(contract) {
  const target = documentFontTarget(contract)
  if (!target && contract.operationKind !== 'font-normalization') return
  if (
    !target ||
    contract.targets.length !== 1 ||
    contract.operationKind !== 'font-normalization' ||
    contract.scope !== 'all-slides-style' ||
    contract.coverage?.required === false ||
    (contract.coverage?.expectedTargetCount ?? 1) !== 1 ||
    contract.allowedChanges?.length !== 1 ||
    contract.allowedChanges[0] !== 'style' ||
    !contract.preserve?.includes('slide-count') ||
    !Number.isSafeInteger(target.slideCount) ||
    target.slideCount < 1 ||
    target.slide !== undefined ||
    target.selector !== undefined ||
    target.opIndexes?.length !== 1 ||
    target.opIndexes[0] !== 0 ||
    target.expected?.changeCategories?.length !== 1 ||
    target.expected.changeCategories[0] !== 'style' ||
    !['chinese', 'east-asian'].includes(target.expected.fontTarget) ||
    typeof target.expected.typeface !== 'string' ||
    !target.expected.typeface.trim() ||
    target.expected.typeface !== target.expected.typeface.trim() ||
    [...target.expected.typeface].length > 256 ||
    [...target.expected.typeface].some((character) => {
      const codePoint = character.codePointAt(0)
      return codePoint < 32 || codePoint === 127
    }) ||
    target.expected.alreadyCompliant !== undefined ||
    target.expected.beforeText !== undefined ||
    target.expected.afterText !== undefined ||
    (target.expected.reviewedAnalysisSha256 !== undefined &&
      !/^[a-f0-9]{64}$/.test(target.expected.reviewedAnalysisSha256))
  ) {
    throw new Error(
      'document-fonts requires one all-slides-style font-normalization target, one op, a slide count, and only style changes',
    )
  }
  for (const kind of FONT_NORMALIZATION_EVIDENCE) {
    if (!contract.requiredEvidence?.includes(kind)) {
      throw new Error(`font-normalization requires ${kind} evidence`)
    }
  }
}

export function fontAnalysisCoverage(target, results) {
  const result = results[0]
  const analysis = result?.analysis
  const counts = ['visitedSlots', 'changedSlots', 'inferredSelections', 'ambiguousSelections']
  const valid =
    results.length === 1 &&
    result.op === 'set-font' &&
    result.status === 'success' &&
    analysis?.kind === 'set-font' &&
    analysis.target === target.expected.fontTarget &&
    analysis.typeface === target.expected.typeface &&
    analysis.coverage === 'supported-xml-only' &&
    analysis.fontAvailability === 'not-evaluated' &&
    analysis.visualFit === 'not-evaluated' &&
    counts.every((key) => Number.isSafeInteger(analysis[key]) && analysis[key] >= 0) &&
    Array.isArray(analysis.findings) &&
    analysis.findings.every(
      (finding) =>
        typeof finding.part === 'string' &&
        typeof finding.path === 'string' &&
        typeof finding.reason === 'string' &&
        ['changed', 'skipped', 'inferred'].includes(finding.status),
    )
  if (!valid) return { covered: false, reason: 'font-analysis-invalid' }
  const reviewRequired = analysis.inferredSelections > 0 || analysis.ambiguousSelections > 0
  if (analysis.selectionStatus !== (reviewRequired ? 'review-required' : 'complete')) {
    return { covered: false, reason: 'font-analysis-invalid' }
  }
  const analysisSha256 = canonicalSha256V1(analysis)
  const reviewed = target.expected.reviewedAnalysisSha256
  if ((reviewRequired || reviewed !== undefined) && reviewed !== analysisSha256) {
    return { covered: false, reason: 'font-selection-review-required', analysisSha256 }
  }
  return {
    covered: true,
    analysisSha256,
    selectionStatus: analysis.selectionStatus,
    inferredSelections: analysis.inferredSelections,
    ambiguousSelections: analysis.ambiguousSelections,
  }
}
