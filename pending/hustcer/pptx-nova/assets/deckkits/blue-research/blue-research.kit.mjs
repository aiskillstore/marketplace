import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { RESEARCH_FAMILY } from './registry.mjs'
import { renderResearchPlan } from './components.mjs'
export const DESIGN = loadDesignContract('blue-research')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.display.latin
export const FONT_CN = DESIGN.fonts.display.eastAsian
export function createDeck(content) {
  const result = RESEARCH_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderResearchPlan(DESIGN, result.layouts), result.layouts),
    warnings: result.warnings,
  }
}
