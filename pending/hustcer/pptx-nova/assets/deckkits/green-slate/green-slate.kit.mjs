// Green Slate 0.1.0: contract adapter for bounded strategy reports.
import { loadDesignContract } from '../shared/design-contract.mjs'
import { createStrategyDeck } from './components.mjs'
export const DESIGN = loadDesignContract('green-slate')
export const createDeck = (content) => createStrategyDeck(DESIGN, content)
