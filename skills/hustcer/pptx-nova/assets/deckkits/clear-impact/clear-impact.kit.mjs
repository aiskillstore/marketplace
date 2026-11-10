// Clear Impact: stable adapter; all geometry comes from the registered component plan.
import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { resolveImpactDeck } from './layouts.mjs'
import { renderImpactPlan } from './components.mjs'
export const DESIGN = loadDesignContract('clear-impact')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.body.latin
export const FONT_CN = DESIGN.fonts.body.eastAsian
export function createDeck(content) {
  const result = resolveImpactDeck(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderImpactPlan(DESIGN, result.layouts), result.layouts),
    warnings: result.warnings,
  }
}
