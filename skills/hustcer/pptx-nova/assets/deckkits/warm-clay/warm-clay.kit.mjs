// Stable DeckKit adapter: coordinates and capacities come from the registered contract.
import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { CLAY_FAMILY } from './registry.mjs'
import { renderClayPlan } from './components.mjs'
export const DESIGN = loadDesignContract('warm-clay')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.body.latin
export const FONT_CN = DESIGN.fonts.body.eastAsian
export function createDeck(content) {
  const result = CLAY_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderClayPlan(DESIGN, result.layouts), result.layouts),
    warnings: result.warnings,
  }
}
