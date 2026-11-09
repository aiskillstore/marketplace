// Swiss Grid 2.0 — every role executes the registered component plan.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createSwissDeck } from './components.mjs'
export const DESIGN = loadDesignContract('swiss-grid')
export const C = DESIGN.colors
export const ACCENTS = [C.red, C.ink, C.secondary]
export const FONT_CN = DESIGN.fonts.body.eastAsian
export const FONT_EN = DESIGN.fonts.body.latin
export const createDeck = (content) => createSwissDeck(DESIGN, content)
