// Validates a recorded visual judgment; never infers taste from PPTX structure or scores.
export const DESIGN_CRITERIA = [
  'hierarchy',
  'composition',
  'typography',
  'color',
  'specificity',
  'rhythm',
]
const MODES = ['persuade', 'read', 'operate', 'experience']
const text = (value) => typeof value === 'string' && value.trim().length > 0
const validSlide = (slide, count) => Number.isInteger(slide) && slide >= 1 && slide <= count

export function validateDesignReview(review, binding, expectedMode = null) {
  const errors = []
  if (!review || review.schemaVersion !== 'pptx-nova-design-review/v1')
    return ['Create requires design_review.json with rendered design observations']
  if (
    review.candidateSha256 !== binding?.candidateSha256 ||
    review.manifestSha256 !== binding?.manifestSha256
  )
    errors.push('design review is stale: candidate or canonical manifest hash differs')
  if (!MODES.includes(review.mode)) errors.push('design review requires an audience mode')
  if (expectedMode !== null) {
    if (!MODES.includes(expectedMode))
      errors.push(
        'Create delivery requires a valid deck_lock.artDirection.mode; generate a fresh candidate with the intended audience mode locked',
      )
    if (review.mode !== expectedMode)
      errors.push(
        `design review mode "${review.mode}" does not match deck_lock.artDirection.mode "${expectedMode}"`,
      )
  }
  for (const key of ['audience', 'idea', 'visualAnchor', 'intentionalRestraint'])
    if (!text(review.direction?.[key])) errors.push(`design direction.${key} is missing`)
  if (!Array.isArray(review.criteria) || review.criteria.length !== DESIGN_CRITERIA.length)
    errors.push('design review must contain exactly the six design criteria')
  for (const id of DESIGN_CRITERIA) {
    const matches = Array.isArray(review.criteria)
      ? review.criteria.filter((c) => c?.id === id)
      : []
    const criterion = matches[0]
    if (
      matches.length !== 1 ||
      criterion?.verdict !== 'pass' ||
      !text(criterion?.observation) ||
      !Array.isArray(criterion?.slides) ||
      !criterion.slides.length ||
      !criterion.slides.every((s) => validSlide(s, binding?.slideCount))
    )
      errors.push(`design criterion ${id} needs one passing, slide-specific rendered observation`)
  }
  if (
    !validSlide(review.weakestSlide?.slide, binding?.slideCount) ||
    !text(review.weakestSlide?.observation)
  )
    errors.push('design review must name and assess its weakest slide')
  if (
    ['persuade', 'experience'].includes(expectedMode ?? review.mode) &&
    (!validSlide(review.signatureMoment?.slide, binding?.slideCount) ||
      !text(review.signatureMoment?.description))
  )
    errors.push('persuade/experience requires a content-led signature moment')
  if (!Array.isArray(review.unresolvedIssues) || review.unresolvedIssues.length)
    errors.push(
      'design review has missing or unresolved issues; repair the source and review again',
    )
  return errors
}
