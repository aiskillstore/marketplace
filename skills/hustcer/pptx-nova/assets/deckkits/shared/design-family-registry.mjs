import { SCHOLAR_FAMILY } from '../paper-scholar/registry.mjs'
import { PINK_FAMILY } from '../pink-script/registry.mjs'
import { JOURNAL_FAMILY } from '../teal-journal/registry.mjs'
import { RESEARCH_FAMILY } from '../blue-research/registry.mjs'
import { VIOLET_FAMILY } from '../violet-momentum/registry.mjs'
import { SKY_FAMILY } from '../sky-compass/registry.mjs'
import { AMBER_FAMILY } from '../amber-ledger/registry.mjs'
import { PULSE_FAMILY } from '../midnight-pulse/registry.mjs'
// Registration seam for visual families: shared callers discover/resolve/validate
// through this interface. Existing families can move here independently.
import { CARTESIAN_FAMILY } from '../cartesian/registry.mjs'
import { BROADSIDE_FAMILY } from '../broadside/registry.mjs'
import { LONG_TABLE_FAMILY } from '../long-table/registry.mjs'
import { SWISS_FAMILY } from '../swiss-grid/registry.mjs'
import { MCK_FAMILY } from '../mckinsey-blue/registry.mjs'
import { CONSULTING_FAMILY } from '../consulting-dark/registry.mjs'
import { IMPACT_FAMILY } from '../clear-impact/registry.mjs'
import { CLAY_FAMILY } from '../warm-clay/registry.mjs'
export const DESIGN_FAMILIES = [
  SCHOLAR_FAMILY,
  PINK_FAMILY,
  RESEARCH_FAMILY,
  JOURNAL_FAMILY,
  VIOLET_FAMILY,
  SKY_FAMILY,
  PULSE_FAMILY,
  AMBER_FAMILY,
  CLAY_FAMILY,
  CARTESIAN_FAMILY,
  BROADSIDE_FAMILY,
  LONG_TABLE_FAMILY,
  SWISS_FAMILY,
  MCK_FAMILY,
  CONSULTING_FAMILY,
  IMPACT_FAMILY,
]
export const registeredDesignFamily = (design) => DESIGN_FAMILIES.find((f) => design[f.key])
export const registeredDesignChecks = DESIGN_FAMILIES.flatMap((f) => Object.keys(f.checks))
