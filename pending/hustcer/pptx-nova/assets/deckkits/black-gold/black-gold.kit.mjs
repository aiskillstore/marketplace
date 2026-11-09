// Black Gold 0.1.0 — contract adapter; all business content is supplied by the caller.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createEditorialDeck } from './components.mjs'
export const DESIGN = loadDesignContract('black-gold')
export const createDeck = (content) => createEditorialDeck(DESIGN, content)
