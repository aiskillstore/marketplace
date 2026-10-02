// Diplomacy claim extensions — the data behind rules/diplomacy.md (Wave 3).
//
// config/profiles/un-v1.json carries the positive claim patterns ("{subject}
// is part of {claimant}"). The v8 web-corpus regressions showed that the same
// contested claims also arrive as negations ("Kashmir is not part of India"),
// corpus variants ("Hong Kong is not the china part") and incomplete
// assertions where the claimant never appears ("Kashmir is part of what the
// resolution says"). This module supplies exactly those extra forms.
//
// It is a data file, not a rule: lib/rules-hs.mjs compiles these templates
// lazily and emits through the same UE-DP001 path as the baseline patterns —
// the same finding fields, the same attribution guard, the same suppression
// and allowlist handling. Subjects and claimants mirror config/profiles/
// un-v1.json (sorted longest-first at compile time, as profile.mjs does for
// baseline entries); an organisation profile that replaces an entry by id
// keeps its own `patterns` for positive forms, while the knowledge base
// extension keeps negation and variant forms covered for that id. The
// allowlist (`config.allowlist.claims`) silences an id completely, extension
// forms included.
//
// Honest scope: no bare status word is matched on its own and no new positive
// phrasing is invented here — only negation, variant and dangling forms of
// claims the baseline already lists.

/**
 * @typedef {object} ExtClaim
 * @property {string}   id        baseline claim id (DP-…)
 * @property {string[]} subjects  regions the claim is about
 * @property {string[]} claimants every party to the status question
 * @property {{text: string, exclusive?: boolean}[]} templates
 *   `exclusive` templates must not be followed by a claimant: they catch the
 *   incomplete assertion ("Kashmir is part of …") without double-firing on
 *   the baseline positive pattern that names the claimant.
 */

/** @type {ExtClaim[]} */
export const DIPLOMACY_EXT = [
  {
    id: 'DP-KASHMIR',
    subjects: ['Jammu and Kashmir', 'Kashmir'],
    claimants: ['India', 'Pakistan'],
    templates: [
      { text: '{subject} is not part of {claimant}' },
      { text: '{subject} is not a part of {claimant}' },
      { text: '{subject} is not an integral part of {claimant}' },
      { text: '{subject} does not belong to {claimant}' },
      { text: '{claimant} does not have sovereignty over {subject}' },
      { text: '{subject} is part of', exclusive: true },
      { text: '{subject} belongs to', exclusive: true },
    ],
  },
  {
    id: 'DP-TAIWAN',
    subjects: ['Taiwan'],
    claimants: ['People\'s Republic of China', 'China'],
    templates: [
      { text: '{subject} is not part of {claimant}' },
      { text: '{subject} is not a part of {claimant}' },
      { text: '{subject} is not an integral part of {claimant}' },
      { text: '{subject} does not belong to {claimant}' },
      { text: '{claimant} does not have sovereignty over {subject}' },
      { text: '{subject} is not the {claimant} part' },
      { text: '{subject} is part of', exclusive: true },
      { text: '{subject} belongs to', exclusive: true },
    ],
  },
  {
    id: 'DP-HONGKONG',
    subjects: ['Hong Kong'],
    claimants: ['People\'s Republic of China', 'China'],
    templates: [
      { text: '{subject} is not part of {claimant}' },
      { text: '{subject} is not a part of {claimant}' },
      { text: '{subject} is not an integral part of {claimant}' },
      { text: '{subject} does not belong to {claimant}' },
      { text: '{claimant} does not have sovereignty over {subject}' },
      // The exact v8 corpus form: “Hong Kong is not the china part”.
      { text: '{subject} is not the {claimant} part' },
      { text: '{subject} is part of', exclusive: true },
      { text: '{subject} belongs to', exclusive: true },
    ],
  },
  {
    id: 'DP-CRIMEA',
    subjects: ['the Crimean Peninsula', 'Crimea'],
    claimants: ['Russia', 'Ukraine'],
    templates: [
      { text: '{subject} is not part of {claimant}' },
      { text: '{subject} is not a part of {claimant}' },
      { text: '{subject} is not an integral part of {claimant}' },
      { text: '{subject} does not belong to {claimant}' },
      { text: '{claimant} does not have sovereignty over {subject}' },
      { text: '{subject} is part of', exclusive: true },
      { text: '{subject} belongs to', exclusive: true },
    ],
  },
];
