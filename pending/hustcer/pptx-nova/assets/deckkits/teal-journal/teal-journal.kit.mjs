import { finishDesign, loadDesignContract } from '../shared/design-contract.mjs'
import { JOURNAL_FAMILY } from './registry.mjs'
import { renderJournalPlan } from './components.mjs'
export const DESIGN = loadDesignContract('teal-journal')
export const C = DESIGN.colors
export const FONT_EN = DESIGN.fonts.display.latin
export const FONT_CN = DESIGN.fonts.display.eastAsian
export function createDeck(content) {
  const resolved = JOURNAL_FAMILY.resolve(DESIGN, content)
  return {
    ...finishDesign(DESIGN, content, renderJournalPlan(DESIGN, resolved.layouts), resolved.layouts),
    warnings: resolved.warnings,
  }
}
