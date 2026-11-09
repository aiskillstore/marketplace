import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { PULSE_FAMILY } from './registry.mjs'
import { renderPulsePlan } from './components.mjs'
export const DESIGN = loadDesignContract('midnight-pulse')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.display.latin
export const FONT_CN = DESIGN.fonts.display.eastAsian
export function createDeck(content, options = {}) {
  const result = PULSE_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(
      DESIGN,
      content,
      renderPulsePlan(DESIGN, result.layouts, content, options),
      result.layouts,
    ),
    warnings: result.warnings,
  }
}
