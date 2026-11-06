import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { PINK_FAMILY } from './registry.mjs'
import { renderPinkPlan } from './components.mjs'
export const DESIGN = loadDesignContract('pink-script')
export const C = DESIGN.colors
export const FONT_DISPLAY = DESIGN.fonts.display.latin
export const FONT_BODY = DESIGN.fonts.body.latin
export function createDeck(content, options = {}) {
  const resolved = PINK_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(
      DESIGN,
      content,
      renderPinkPlan(DESIGN, resolved.layouts, content, options),
      resolved.layouts,
    ),
    warnings: resolved.warnings,
  }
}
