import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { SCHOLAR_FAMILY } from './registry.mjs'
import { renderScholarPlan } from './components.mjs'
export const DESIGN = loadDesignContract('paper-scholar')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.display.latin
export const FONT_CN = DESIGN.fonts.display.eastAsian
export function createDeck(content) {
  const resolved = SCHOLAR_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderScholarPlan(DESIGN, resolved.layouts), resolved.layouts),
    warnings: resolved.warnings,
  }
}
