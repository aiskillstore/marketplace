// Corpus declarations explain intentional layout repetition. They never waive
// content, geometry or visual gates; authored timing is checked after composition.
const object = (value) => value && typeof value === 'object' && !Array.isArray(value)
const strings = (value) =>
  typeof value === 'string'
    ? [value]
    : value && typeof value === 'object'
      ? Object.values(value).flatMap(strings)
      : []

function authoredFacts(patch, count) {
  const shapes = Array.from({ length: count }, () => new Map())
  const animations = new Map()
  const transitions = new Map()
  const text = Array.from({ length: count }, () => [])
  for (const op of patch.ops ?? []) {
    const names = shapes[op.slide]
    if (!names) continue
    if (
      ['add-text-box', 'set-text-frame', 'set-paragraph', 'add-paragraph', 'add-run'].includes(
        op.op,
      ) &&
      typeof op.text === 'string'
    )
      text[op.slide].push(op.text)
    if (op.op?.startsWith('add-') && typeof op.name === 'string') names.set(op.name, {})
    if (op.op === 'set-shape' && op.name && names.has(op.shape?.name)) {
      const identity = names.get(op.shape.name)
      names.delete(op.shape.name)
      names.set(op.name, identity)
    }
    if (op.op === 'set-slide-animations')
      animations.set(
        op.slide,
        (op.animations ?? []).map((step) => ({
          effect: step.effect,
          target: names.get(step.target?.shape?.name ?? step.shape?.name),
        })),
      )
    if (op.op === 'set-slide-transition') transitions.set(op.slide, op.clear ? null : op)
  }
  return { shapes, animations, transitions, text }
}

export function inspectAnimationCorpus(content, patch) {
  const errors = []
  const coveredSlides = new Set()
  const fail = (code, path, message) =>
    errors.push({ type: 'animation-corpus', code, path, message })
  const meta = content?.meta ?? {}
  if (meta.deckProfile !== 'animation-corpus') {
    if (meta.animationCases !== undefined)
      fail(
        'corpus.profile.missing',
        'meta.deckProfile',
        'animationCases requires deckProfile=animation-corpus',
      )
    return { errors, coveredSlides }
  }
  const cases = meta.animationCases
  if (!Array.isArray(cases) || !cases.length) {
    fail(
      'corpus.cases.missing',
      'meta.animationCases',
      'animation-corpus requires nonempty animationCases',
    )
    return { errors, coveredSlides }
  }
  const slides = content.slides ?? []
  const ids = new Set()
  const facts = patch ? authoredFacts(patch, slides.length) : null
  cases.forEach((item, index) => {
    const path = `meta.animationCases[${index}]`
    const before = errors.length
    if (!object(item)) {
      fail('corpus.case.invalid', path, 'Animation case must be an object')
      return
    }
    for (const field of ['id', 'feature', 'expectedPlayback']) {
      if (typeof item[field] !== 'string' || !item[field].trim())
        fail('corpus.description.missing', `${path}.${field}`, `Case ${field} must be nonempty`)
    }
    if (ids.has(item.id))
      fail('corpus.id.duplicate', path, `Duplicate animation case id: ${item.id}`)
    ids.add(item.id)
    if (!['animation', 'morph', 'transition'].includes(item.kind))
      fail('corpus.kind.invalid', path, 'Case kind must be animation, morph or transition')
    const expectedCount = item.kind === 'animation' ? 1 : 2
    if (
      !Array.isArray(item.slides) ||
      item.slides.length !== expectedCount ||
      item.slides.some(
        (slide) => !Number.isInteger(slide) || slide < 0 || slide >= slides.length,
      ) ||
      (expectedCount === 2 && item.slides[1] !== item.slides[0] + 1)
    ) {
      fail(
        'corpus.slides.invalid',
        `${path}.slides`,
        'Animation uses one 0-based slide; Morph/transition requires one adjacent source/destination pair',
      )
      return
    }
    const visible = item.slides
      .flatMap((slide) => (facts ? facts.text[slide] : strings(slides[slide]?.data)))
      .join('\n')
      .toLocaleLowerCase('en')
    for (const field of ['feature', 'expectedPlayback']) {
      if (typeof item[field] === 'string' && !visible.includes(item[field].toLocaleLowerCase('en')))
        fail(
          'corpus.description.notVisible',
          `${path}.${field}`,
          `Case ${field} must appear in slide text`,
        )
    }
    if (item.kind === 'morph') {
      if (!['by-object', 'by-word', 'by-char'].includes(item.morphMode))
        fail('corpus.mode.invalid', path, 'Morph case requires morphMode')
    } else if (
      typeof item.effect !== 'string' ||
      !item.effect.trim() ||
      (item.kind === 'transition' && item.effect === 'morph')
    ) {
      fail(
        'corpus.effect.missing',
        path,
        'Animation/basic transition case requires effect; Morph uses kind=morph',
      )
    }
    if (facts && errors.length === before) {
      const [from, to] = item.slides
      if (item.kind === 'animation') {
        if (
          !(facts.animations.get(from) ?? []).some(
            (step) => step.effect === item.effect && step.target,
          )
        )
          fail(
            'corpus.animation.missing',
            path,
            `No authored ${item.effect} animation with a target on slide ${from}`,
          )
      } else {
        const transition = facts.transitions.get(to)
        if (
          !transition ||
          transition.kind !== (item.kind === 'morph' ? 'morph' : item.effect) ||
          (item.kind === 'morph' && (transition.morphMode ?? 'by-object') !== item.morphMode)
        )
          fail(
            'corpus.transition.missing',
            path,
            `No matching authored transition on destination slide ${to}`,
          )
        if (
          item.kind === 'morph' &&
          ![...facts.shapes[from].keys()].some(
            (name) => name.startsWith('!!') && facts.shapes[to].has(name),
          )
        )
          fail(
            'corpus.morphPair.missing',
            path,
            'Morph case requires an explicit !! name shared by its adjacent slides',
          )
      }
    }
    if (errors.length === before) item.slides.forEach((slide) => coveredSlides.add(slide))
  })
  // Invalid annotations never grant partial exemptions.
  return { errors, coveredSlides: errors.length ? new Set() : coveredSlides }
}
