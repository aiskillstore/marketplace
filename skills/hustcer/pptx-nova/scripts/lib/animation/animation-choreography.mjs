// Create accepts native timing operations and explicit Morph names only.
// xdoc dry-run remains the authority for effect parameters and timing grammar.
const object = (value) => value && typeof value === 'object' && !Array.isArray(value)

export function composeChoreography({ basePatch, choreography, slideCount }) {
  if (
    !object(choreography) ||
    choreography.schemaVersion !== 'pptx-patch/v1' ||
    !Array.isArray(choreography.ops) ||
    Object.keys(choreography).some((key) => !['schemaVersion', 'ops'].includes(key))
  )
    throw new Error('Choreography must contain only schemaVersion "pptx-patch/v1" and ops')
  if (!choreography.ops.length) throw new Error('Choreography ops must not be empty')
  const names = Array.from({ length: slideCount }, () => new Set())
  for (const op of basePatch.ops) {
    if (op.op?.startsWith('add-') && typeof op.name === 'string') names[op.slide]?.add(op.name)
  }
  const targetName = (selector, slide) => {
    if (
      !object(selector) ||
      Object.keys(selector).length !== 1 ||
      typeof selector.name !== 'string' ||
      !names[slide].has(selector.name)
    )
      throw new Error(
        `Choreography target must name an existing unique DeckKit shape on slide ${slide}: ${JSON.stringify(selector)}`,
      )
    return selector.name
  }
  for (const op of choreography.ops) {
    if (!object(op) || !Number.isInteger(op.slide) || op.slide < 0 || op.slide >= slideCount)
      throw new Error('Choreography slide index must address an existing 0-based slide')
    if (op.op === 'set-slide-animations') {
      if (
        (op.mode !== undefined && op.mode !== 'replace') ||
        op.remove !== undefined ||
        !Array.isArray(op.animations) ||
        !op.animations.length
      )
        throw new Error('Create choreography requires a nonempty replacement animations list')
      for (const animation of op.animations)
        targetName(animation?.target?.shape ?? animation?.shape, op.slide)
    } else if (op.op === 'set-slide-transition') {
      if (op.clear || typeof op.kind !== 'string')
        throw new Error('Create choreography requires a transition kind')
      if (op.kind === 'morph' && op.slide === 0) throw new Error('Morph requires a preceding slide')
    } else if (op.op === 'set-shape') {
      if (
        Object.keys(op).some((key) => !['op', 'slide', 'shape', 'name'].includes(key)) ||
        !/^!!\S/.test(op.name ?? '')
      )
        throw new Error('Choreography set-shape supports only explicit !! Morph names')
      const previous = targetName(op.shape, op.slide)
      if (op.name !== previous && names[op.slide].has(op.name))
        throw new Error(`Duplicate Morph name on slide ${op.slide}: ${op.name}`)
      names[op.slide].delete(previous)
      names[op.slide].add(op.name)
    } else {
      throw new Error(`Choreography operation is not supported: ${op.op}`)
    }
  }
  // xdoc defaults to merge-safe. Create promises replacement lists so repeated
  // declarations and a DeckKit's own timing cannot accidentally accumulate.
  const ops = choreography.ops.map((op) =>
    op.op === 'set-slide-animations' ? { ...op, mode: 'replace' } : op,
  )
  return { ...basePatch, ops: [...basePatch.ops, ...ops] }
}
