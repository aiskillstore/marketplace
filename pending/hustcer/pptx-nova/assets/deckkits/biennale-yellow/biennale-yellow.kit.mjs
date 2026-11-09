// Biennale Yellow 2.0.0 — one contract and one component execution path.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createBiennaleDeck } from './components.mjs'

export const DESIGN = loadDesignContract('biennale-yellow')
export const C = DESIGN.colors
export const FONT_DISPLAY = DESIGN.fonts.display.latin
export const FONT_BODY = DESIGN.fonts.body.latin
export const FONT_MONO = DESIGN.fonts.mono.latin
export const createDeck = (content) => createBiennaleDeck(DESIGN, content)
