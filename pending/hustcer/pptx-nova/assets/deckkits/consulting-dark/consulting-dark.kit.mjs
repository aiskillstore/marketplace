// Consulting Dark 2.1: open editorial evidence with restrained solid process nodes.
import { loadDesignContract, finishDesign } from '../shared/design-contract.mjs'
import { resolveConsultingDeck } from './layouts.mjs'
import { renderConsultingPlan } from './components.mjs'
export const DESIGN = loadDesignContract('consulting-dark')
export const C = DESIGN.colors
export const ACCENTS = [C.primary, C.teal]
export const FONT_EN = DESIGN.fonts.body.latin
export const FONT_CN = DESIGN.fonts.body.eastAsian
export function createDeck(content) {
  const r = resolveConsultingDeck(DESIGN, content)
  const result = finishDesign(DESIGN, content, renderConsultingPlan(DESIGN, r.layouts), r.layouts)
  result.warnings = r.warnings
  return result
}
