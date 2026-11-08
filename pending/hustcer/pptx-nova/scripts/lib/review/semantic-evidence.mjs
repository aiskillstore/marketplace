export const V2_SOURCE_RULE_COUNT = 82
export const V2_NORMALIZED_RULE_COUNT = 81

export function semanticIssueValid(issue) {
  return (
    issue !== null &&
    typeof issue === 'object' &&
    typeof issue.code === 'string' &&
    issue.code.length > 0 &&
    typeof issue.ruleId === 'string' &&
    issue.ruleId.length > 0 &&
    typeof issue.part === 'string' &&
    issue.part.length > 0 &&
    typeof issue.message === 'string' &&
    issue.message.length > 0
  )
}

export function semanticValidationEvidence(report) {
  const summary = report?.semanticSummary
  const issues = report?.semanticIssues
  const issueCount = summary?.issueCount
  const sourceRuleCount = summary?.sourceRuleCount
  const normalizedRuleCount = summary?.normalizedRuleCount
  const present = summary !== undefined || issues !== undefined
  const evidence =
    summary !== null &&
    typeof summary === 'object' &&
    typeof summary?.passed === 'boolean' &&
    typeof issueCount === 'number' &&
    Number.isInteger(issueCount) &&
    issueCount >= 0 &&
    typeof sourceRuleCount === 'number' &&
    Number.isInteger(sourceRuleCount) &&
    sourceRuleCount >= V2_SOURCE_RULE_COUNT &&
    typeof normalizedRuleCount === 'number' &&
    Number.isInteger(normalizedRuleCount) &&
    normalizedRuleCount >= V2_NORMALIZED_RULE_COUNT &&
    Array.isArray(issues) &&
    issues.every(semanticIssueValid)
  const consistent =
    evidence && issueCount === issues.length && summary.passed === (issueCount === 0)
  return {
    present,
    evidence,
    consistent,
    valid: evidence && consistent,
    passed: evidence && consistent ? summary.passed : null,
    issueCount: Number.isInteger(issueCount) ? issueCount : null,
    sourceRuleCount: Number.isInteger(sourceRuleCount) ? sourceRuleCount : null,
    normalizedRuleCount: Number.isInteger(normalizedRuleCount) ? normalizedRuleCount : null,
  }
}
