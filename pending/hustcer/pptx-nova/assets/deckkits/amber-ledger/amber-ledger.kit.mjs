import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { AMBER_FAMILY } from './registry.mjs'
import { renderAmberPlan } from './components.mjs'
export const DESIGN = loadDesignContract('amber-ledger')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.display.latin
export const FONT_CN = DESIGN.fonts.display.eastAsian
export function createDeck(content) {
  const result = AMBER_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderAmberPlan(DESIGN, result.layouts), result.layouts),
    warnings: result.warnings,
  }
}
