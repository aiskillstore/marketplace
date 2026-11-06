// Cartesian 2.0 — every page uses the registered contract/component path.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createCartesianDeck } from './components.mjs'
export const DESIGN = loadDesignContract('cartesian')
export const C = DESIGN.colors
export const FONT_DISPLAY = DESIGN.fonts.display.latin
export const FONT_BODY = DESIGN.fonts.body.latin
export const createDeck = (content, options = {}) => createCartesianDeck(DESIGN, content, options)
