import { validateContent } from './core-primitives.kit.mjs'
import { loadDesignContract } from './design-contract.mjs'
import { resolveBiennaleDeck } from '../biennale-yellow/layouts.mjs'
import { resolveEditorialDeck } from '../black-gold/layouts.mjs'
import { resolveStrategyDeck } from '../green-slate/layouts.mjs'
import { resolveAnnualDeck } from '../clear-value/layouts.mjs'
import { registeredDesignFamily } from './design-family-registry.mjs'

// Keep legacy validation intact. Only registered design contracts add semantic checks.
export function validateDeckkitContent(content, options = {}) {
  const result = validateContent(content, options)
  if (!result.valid && result.errors.some((e) => e.type !== 'diversity')) return result
  try {
    const design = loadDesignContract(options.deckkit || content.meta.deckkit)
    if (!design) return result
    const registered = registeredDesignFamily(design)
    if (registered || design.editorial || design.strategy || design.annual || design.biennale) {
      // Registered compositions own diversity even when capacity resolution fails.
      // Keep the actual design error without unrelated legacy group blockers.
      result.errors = result.errors.filter((e) => e.type !== 'diversity')
      result.warnings = result.warnings.filter((e) => e.type !== 'diversity')
      result.fitDiagnostics = result.fitDiagnostics.filter((d) => !d.code?.startsWith('diversity.'))
      const resolved = registered
        ? registered.resolve(design, content)
        : design.biennale
          ? resolveBiennaleDeck(design, content)
          : design.annual
            ? resolveAnnualDeck(design, content)
            : design.strategy
              ? resolveStrategyDeck(design, content)
              : resolveEditorialDeck(design, content)
      if (registered || design.annual || design.biennale) {
        // Annual frames depend on the resolved chart count, column weights and row count.
        // The resolver above checked actual instances; generic repeating budgets are discovery hints.
        const generic = (d) => d?.code?.startsWith('slotBudget.')
        result.warnings = result.warnings.filter((w) => !generic(w.diagnostic))
        result.fitDiagnostics = result.fitDiagnostics.filter((d) => !generic(d))
      }
      result.valid = result.errors.length === 0
      result.designDiversity = {
        mode: registered
          ? `resolved-${registered.key}-layouts`
          : design.biennale
            ? 'resolved-biennale-layouts'
            : design.annual
              ? 'resolved-annual-layouts'
              : design.strategy
                ? 'resolved-strategy-layouts'
                : 'resolved-editorial-layouts',
        uniqueCompositions: new Set(resolved.layouts.map((r) => r.fingerprint)).size,
      }
      if (registered || design.biennale)
        result.designCapacity = resolved.layouts.map((l) => ({
          slideIndex: l.slideIndex,
          layoutId: l.layoutId,
          components:
            l.components
              ?.filter((c) => c.kind === 'text')
              .map((c) => ({
                path: c.path,
                estimatedLines: c.estimatedLines,
                heightIn: c.frame[3],
                requiredHeight: c.requiredHeight,
              })) ?? [],
        }))
      for (const message of resolved.warnings)
        result.warnings.push({
          type: 'design',
          message,
          diagnostic: { code: 'design.diversity.repeated' },
        })
      return result
    }
    throw new Error('Design contract has no supported deck resolver')
  } catch (error) {
    result.errors.push({ type: 'design', path: 'slides', message: error.message })
    result.valid = false
  }
  return result
}
