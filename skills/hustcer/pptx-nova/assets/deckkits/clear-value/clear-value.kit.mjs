import { loadDesignContract } from '../shared/design-contract.mjs'
import { createAnnualDeck } from './components.mjs'
export const DESIGN = loadDesignContract('clear-value')
export const createDeck = (content) => createAnnualDeck(DESIGN, content)
