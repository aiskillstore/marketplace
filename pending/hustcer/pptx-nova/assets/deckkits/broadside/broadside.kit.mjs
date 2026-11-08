// Broadside 2.0 — stable public adapter; every page uses a registered component plan.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createBroadsideDeck } from './components.mjs'
export const DESIGN = loadDesignContract('broadside')
export const C = DESIGN.colors
export const FONT_DISPLAY = DESIGN.fonts.display.latin
export const FONT_MONO = DESIGN.fonts.mono.latin
export const FONT_CN = DESIGN.fonts.body.eastAsian
export const createDeck = (content) => createBroadsideDeck(DESIGN, content)
