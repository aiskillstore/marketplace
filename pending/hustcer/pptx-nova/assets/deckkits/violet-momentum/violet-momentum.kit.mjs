import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { renderVioletPlan } from './components.mjs'
import { VIOLET_FAMILY } from './registry.mjs'
export const DESIGN = loadDesignContract('violet-momentum')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.body.latin
export const FONT_CN = DESIGN.fonts.body.eastAsian
export function createDeck(content) {
  const result = VIOLET_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderVioletPlan(DESIGN, result.layouts), result.layouts),
    warnings: result.warnings,
  }
}
