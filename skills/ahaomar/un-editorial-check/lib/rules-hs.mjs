// Hate-speech and safety family — UE-HS001, UE-HS002, UE-HS003 (category:
// hate-speech), UE-DM001 (category: discriminatory), plus the UE-DP001
// diplomacy extension rule (category: diplomacy). This module registers all
// of them through HS_META and HS_RULES, which lib/rules.mjs spreads after its
// own UE-DP001 entries, so the safety set ships without editing rules.mjs.
//
// Like every shipped rule, these match `unit.text`: the extracted copy span,
// from which quotations, comments, URLs and code are already absent. Three
// disciplines define the family:
//
//   * Composition over word lists: a dehumanising frame, an accusation or an
//     exclusion verb only fires when it is predicated of — or aimed at — a
//     listed group of people. The frame word alone never matches.
//   * Symmetry: one shared group vocabulary feeds all three rules, so swapping
//     which group is named cannot change whether a mirrored sentence fires.
//     The verify script sweeps every group term through every template.
//   * Attribution: `attributedClaim` (the UE-DP001 guard) exempts anything a
//     reporting party is quoted as saying, and UE-HS002 — a heuristic — routes
//     to review and never claims proof of intent.
//
// Findings are never fixable: no rule passes a `replacement`.
//
// Patterns are compiled lazily inside the rule functions (never at module
// top level), so the import cycle created at integration time cannot observe
// a half-initialised knowledge base.

import { emit, attributedClaim, escapeRe } from './rules.mjs';
import { DIPLOMACY_EXT } from './diplomacy-ext.mjs';

/**
 * Knowledge base. Every entry carries a non-empty `source` citation and a
 * short `cite` used in finding suggestions. The sources establish the
 * standard the rules surface for human review; they do not prove that any
 * matched sentence meets the legal threshold of incitement, and no finding
 * here is a legal judgement.
 */
export const HS_KB = {
  groups: {
    source: 'United Nations Strategy and Plan of Action on Hate Speech (18 June 2019), working definition: '
      + '“any kind of communication in speech, writing or behaviour, that attacks or uses pejorative or '
      + 'discriminatory language with reference to a person or a group on the basis of who they are, in other '
      + 'words, based on their religion, ethnicity, nationality, race, colour, descent, gender or other '
      + 'identity factor.” https://www.un.org/en/hate-speech/understanding-hate-speech/what-is-hate-speech',
    cite: 'UN Strategy and Plan of Action on Hate Speech (un.org/en/hate-speech)',
    terms: [
      // Religions and belief.
      'muslims', 'christians', 'jews', 'hindus', 'sikhs', 'buddhists', 'atheists',
      // Ethnic and national groups.
      'roma', 'kurds', 'yazidis', 'uighurs', 'uyghurs', 'tibetans', 'palestinians',
      'arabs', 'syrians', 'iraqis', 'afghans', 'somalis', 'nigerians', 'pakistanis',
      'bangladeshis', 'ethiopians', 'eritreans', 'burmese',
      // Migration and legal status.
      'foreigners', 'immigrants', 'migrants', 'refugees', 'asylum seekers',
      // Racialised and other targeted groups.
      'black people', 'white people', 'indigenous peoples', 'gay people', 'trans people',
      // Protected characteristics (Wave 3): sex or gender, age, disability —
      // longest-first inside each family so "wheelchair user" wins over
      // "wheelchair" and "older people" over "older".
      'wheelchair users', 'wheelchair user',
      'people with disabilities', 'persons with disabilities', 'disabled people',
      'older people', 'elderly people', 'elderly',
      'women', 'men', 'girls', 'boys',
    ],
  },
  dehumanisingFrames: {
    source: 'United Nations, “Hate speech and real harm”: a campaign against the Rohingya Muslim minority '
      + 'was “loaded with derogatory and dehumanizing language”. '
      + 'https://www.un.org/en/hate-speech/understanding-hate-speech/hate-speech-and-real-harm',
    cite: 'UN, Hate speech and real harm (un.org/en/hate-speech)',
    frames: [
      'vermin', 'cockroaches', 'cockroach', 'rats', 'rat', 'lice', 'fleas', 'flea',
      'parasites', 'parasite', 'maggots', 'worms', 'insects', 'beasts', 'animals',
      'swine', 'pigs', 'disease', 'plague', 'cancer', 'virus', 'filth', 'garbage',
      'trash', 'subhuman',
    ],
  },
  collectiveBlame: {
    source: 'Rabat Plan of Action on the prohibition of advocacy of national, racial or religious hatred that '
      + 'constitutes incitement to discrimination, hostility or violence (United Nations document '
      + 'A/HRC/22/17/Add.4, 2013): the six-part threshold test weighs the context, the status of the speaker, '
      + 'the intent of the speaker, the content and form of the speech, the extent of the speech, and the '
      + 'likelihood of harm including imminence.',
    cite: 'Rabat Plan of Action, six-part threshold test (A/HRC/22/17/Add.4)',
    accusations: [
      'criminals', 'criminal', 'terrorists', 'terrorist', 'scum', 'killers',
      'murderers', 'rapists', 'thieves', 'extremists',
    ],
    traits: [
      'violent', 'dangerous', 'evil', 'savage', 'barbaric', 'cruel', 'vicious',
      'inferior',
    ],
    markers: ['inherently', 'naturally', 'genetically', 'instinctively', 'by nature'],
  },
  exclusionCalls: {
    source: 'International Covenant on Civil and Political Rights, article 20(2): “Any advocacy of national, '
      + 'racial or religious hatred that constitutes incitement to discrimination, hostility or violence shall '
      + 'be prohibited by law.” Office of the United Nations High Commissioner for Human Rights, International '
      + 'Covenant on Civil and Political Rights. '
      + 'https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights',
    cite: 'ICCPR article 20(2) (OHCHR)',
    verbs: [
      'deport', 'ban', 'banish', 'expel', 'exile', 'eliminate', 'purge',
      'exterminate', 'kill', 'murder', 'slaughter', 'massacre', 'destroy',
      'ethnically cleanse', 'round up',
    ],
    modals: ['must', 'should', 'ought to', 'has to', 'have to'],
    outcomes: [
      'go', 'leave', 'depart', 'die', 'disappear', 'deported', 'banned',
      'expelled', 'exiled', 'eliminated', 'purged', 'removed', 'killed',
      'murdered', 'slaughtered', 'destroyed', 'exterminated', 'massacred',
    ],
    // Continuations that turn a modal outcome into an exclusion demand: the
    // outcome only names an exclusion when it heads one of these phrases
    // ("must leave the country", "should go home"). Any other continuation
    // — a route ("through the registration process"), an object ("their
    // documents"), a prepositional destination ("to the reception centre")
    // — is operational copy and never matches: the outcome must instead end
    // its clause. Guard note: rules/hate-speech.md. Locks: tests/run.mjs and
    // tests/audit-detection.mjs.
    continuations: [
      'away', 'back', 'home', 'out', 'immediately', 'for good',
      'the country', 'the nation', 'the region', 'the borders', 'the border',
      'this country', 'this nation', 'their own country',
      'from the country', 'from the nation', 'from the region',
      'from this country', 'from our country', 'from our midst',
      'to their country of origin', 'to their home countries',
      'to third countries',
    ],
  },
  demeaning: {
    source: 'United Nations Convention on the Rights of Persons with Disabilities, General Assembly '
      + 'resolution A/RES/61/106 (13 December 2006): persons with disabilities include those with '
      + 'long-term physical, mental, intellectual or sensory impairments which, in interaction with '
      + 'barriers, may hinder full and effective participation in society on an equal basis with others — '
      + 'the basis for refusing infantilising pity framing. And the Convention on the Elimination of All '
      + 'Forms of Discrimination against Women (1979), article 1: discrimination against women is any '
      + 'distinction, exclusion or restriction on the basis of sex. '
      + 'https://www.un.org/en/development/desa/disabilities/convention-on-the-rights-of-persons-with-disabilities.html',
    cite: 'CRPD (A/RES/61/106) and CEDAW (1979)',
    // A demeaning predicate never matches alone: UE-DM001 requires it to be
    // predicated of a listed group, or a disability term beside pity framing
    // or a first-person rejection inside one 300-character window.
    predicates: ['burden', 'liability', 'blight', 'eyesore', 'nuisance'],
    pity: [
      'felt sorry for', 'feel sorry for', 'feel pity for',
      'take pity on', 'took pity on', 'pities', 'pitied',
    ],
    // Longest-first: "wheelchair user" must win over "wheelchair".
    disability: [
      'wheelchair user', 'wheelchair', 'handicapped', 'handicap',
      'disability', 'disabilities', 'disabled',
    ],
    // First-person forms only: an institutional "the team hates delays" is
    // operational copy, not a person-rejection, and stays silent.
    rejection: [
      'i do not like', 'i dont like', 'i don\'t like',
      'i cannot stand', 'i cant stand', 'i can\'t stand',
      'i hate', 'i detest', 'i despise',
    ],
  },
};

/**
 * Unique knowledge-base source citations, in knowledge-base order: the
 * appendix list for a generated report. Every citation comes from an HS_KB
 * entry above, so the array stays in step with the knowledge base by
 * construction.
 */
export const HS_SOURCES = [...new Set(Object.values(HS_KB).map((entry) => entry.source))];

/** Rule metadata for the hate-speech set. Catalogue fields are asserted equal. */
export const HS_META = {
  'UE-HS001': { category: 'hate-speech', confidence: 'deterministic', severity: 'error' },
  // Heuristic judgement questions ship as warnings: they route to the
  // harmful-discriminatory review lane and never fail a build on their own.
  'UE-HS002': { category: 'hate-speech', confidence: 'heuristic', severity: 'warning' },
  'UE-HS003': { category: 'hate-speech', confidence: 'deterministic', severity: 'error' },
  'UE-DM001': { category: 'discriminatory', confidence: 'deterministic', severity: 'error' },
  // Spread after lib/rules.mjs's own UE-DP001 entry (HS_META is spread last):
  // a contested claim is a warning that requires diplomatic review, never a
  // declaration that the text is factually false.
  'UE-DP001': { category: 'diplomacy', confidence: 'deterministic', severity: 'warning' },
};

// Compiled lazily on the first rule call: escapeRe is a const binding in
// rules.mjs, and the integration import cycle must never observe a call made
// while either module is still evaluating.
let compiled = null;

function patterns() {
  if (compiled) return compiled;
  const alt = (terms) => terms.map((term) => escapeRe(term)).join('|');
  const group = `(?:the\\s+)?(?:${alt(HS_KB.groups.terms)})`;
  const frame = `(?:${alt(HS_KB.dehumanisingFrames.frames)})`;
  const accusation = `(?:${alt(HS_KB.collectiveBlame.accusations)})`;
  const trait = `(?:${alt(HS_KB.collectiveBlame.traits)})`;
  const marker = `(?:(?:${alt(HS_KB.collectiveBlame.markers)})\\s+)?`;
  const verb = `(?:${alt(HS_KB.exclusionCalls.verbs)})`;
  const modal = `(?:${alt(HS_KB.exclusionCalls.modals)})`;
  const outcome = `(?:${alt(HS_KB.exclusionCalls.outcomes)})`;
  const continuation = `(?:${alt(HS_KB.exclusionCalls.continuations)})`;
  const demeaningPredicate = `(?:${alt(HS_KB.demeaning.predicates)})`;
  const pity = `(?:${alt(HS_KB.demeaning.pity)})`;
  const disability = `(?:${alt(HS_KB.demeaning.disability)})`;
  const rejection = `(?:${alt(HS_KB.demeaning.rejection)})`;
  const copula = '(?:is|are|was|were)';

  // Each pattern is one template literal: a `+`-concatenated string piece in
  // this file would be extracted as user-visible copy by extract-js, and the
  // self-scan gate must stay silent on this module's own source.
  compiled = {
    // A listed group of people copulated to a listed dehumanising frame,
    // optionally reached through an intensifier or a comparison ("are nothing
    // but vermin", "are like cockroaches").
    hs001: new RegExp(`\\b${group}\\s+${copula}\\s+(?:(?:a|an|the|just|like|such|essentially|basically|literally)\\s+|nothing (?:but|more than)\\s+)*${frame}\\b`, 'gi'),
    // Universal quantifier plus an accusation noun ("all foreigners are criminals").
    hs002Universal: new RegExp(`\\ball\\s+(?:of\\s+(?:the|those)\\s+)?${group}\\s+${copula}\\s+(?:nothing (?:but|more than)\\s+|just\\s+)?${accusation}\\b`, 'gi'),
    // A trait predicate of the group, with or without an inherent marker
    // ("Muslims are inherently violent", "Kurds are dangerous by nature").
    hs002Trait: new RegExp(`\\b${group}\\s+${copula}\\s+${marker}${trait}\\b(?:\\s+by\\s+nature)?`, 'gi'),
    // Base-form exclusion or violence verb aimed at the group. Base forms
    // only: a past-tense narrative ("attackers killed the refugees") is not a
    // call and never matches.
    hs003Verb: new RegExp(`\\b${verb}\\s+(?:all\\s+|every\\s+)?${group}\\b`, 'gi'),
    // Modal outcome construction ("Foreigners must go", "Refugees must be
    // deported", "Foreigners should leave the country"). The outcome must
    // end its clause — clause-ending punctuation, end of line or end of the
    // copy — or head an exclusion continuation from the KB: any other
    // continuation (a route, an object, a prepositional destination) is
    // operational copy and stays silent.
    // The trailing literal carries no copy: extraction may classify the
    // template fragment as prose, and the clause-end class is not a finding.
    hs003Modal: new RegExp(`\\b${group}\\s+${modal}\\s+(?:be\\s+)?${outcome}\\b(?:\\s+${continuation}\\b)?(?=[.!?;:'"\\),\\]]|\\s*$|\\s*\\n)`, 'gi'), // ue:ignore UE-RE005
    // Wave 3 — UE-DM001, the discriminatory-or-demeaning rule. The predicate
    // branch mirrors hs001's composition (group + copula + predicate); the
    // pity and rejection patterns are proximity partners that ruleDM001 pairs
    // with a disability term inside one 300-character window. Vocabulary
    // alone never matches: every branch needs the pairing.
    dm001Predicate: new RegExp(`\\b${group}\\s+${copula}\\s+(?:(?:a|an|the)\\s+)?${demeaningPredicate}\\b`, 'gi'),
    dm001Pity: new RegExp(`\\b${pity}\\b`, 'gi'),
    dm001Disability: new RegExp(`\\b${disability}\\b`, 'gi'),
    dm001Rejection: new RegExp(`\\b${rejection}\\b`, 'gi'),
  };
  return compiled;
}

// --- UE-HS002 subject gate ---------------------------------------------------
//
// The false positives this removes are not marginal. In "The rights of women
// are inferior to those guaranteed to men" the copula's subject is *rights*,
// not women: the group term is the object of a preposition, and the finding
// misread the sentence. Same for "Data on older people are inferior in
// quality", "The welfare of refugees is inferior to that of others" and
// "Access to justice for migrants is inferior to that for others" — four
// comparative statements about conditions, services and data that the rule
// reported as collective blame against a group of people. The tool then told
// an editor to rewrite them, on wording it had misparsed.
//
// The gate is a grammar fact, not a judgement: a preposition immediately
// before the group term (optionally through a determiner) makes the group the
// complement of that preposition, so it cannot be the subject of the copula.
// A partitive is not a preposition here — in "All of the foreigners are
// criminals" the subject is the quantifier "all", and that sentence is a
// required true positive in .feedbacks/old/verify-hs.mjs and a control line in
// the dummydata corpus, so the partitive is explicitly exempt.
//
// Deliberately narrow, and narrow in the direction that keeps findings: the
// window is a fixed 60 characters ending at the match, an intervening comma or
// any other word ends the phrase ("In Europe, refugees are criminals." and
// "Of all groups, migrants are criminals." both still fire), and only UE-HS002
// is gated. UE-HS001 and UE-DM001 keep matching on the same compositions.
const GROUP_AS_OBJECT_RE =
  /\b(?:of|for|on|in|to|about|regarding|concerning|among|amongst|within|by|from|against|per|via|with|without|despite|beyond|across|through|during|under|over|before|after|at)\s+(?:the\s+|a\s+|an\s+)?$/i;
const PARTITIVE_RE =
  /\b(?:all|most|some|any|every|each|both|neither|either|none|no|one|two|three|half|many|few|much)$/i;

/**
 * True when the group term at `index` is the complement of a preposition, so
 * the copula in the match is not predicated of the group. Partitives are
 * exempt: "all of the foreigners" is a quantifier phrase whose subject is
 * "all", and that is a required true positive.
 */
function groupIsPrepositionalObject(text, index) {
  const window = text.slice(Math.max(0, index - 60), index);
  const preposition = GROUP_AS_OBJECT_RE.exec(window);
  if (!preposition) return false;
  return !PARTITIVE_RE.test(window.slice(0, preposition.index));
}

/** Report, never rewrite: the override carries `proposed` guidance, never a `replacement`. */
function ruleHS001(state, unit) {
  const re = patterns().hs001;
  re.lastIndex = 0;
  let m;
  while ((m = re.exec(unit.text))) {
    if (attributedClaim(unit.text, m.index, m[0].length)) continue;
    emit(state, unit, 'UE-HS001', m[0], m.index,
      `Dehumanising frame "${m[0]}" is predicated of a group of people.`,
      `Describe the group or its conduct without pest, disease or animal imagery (source: ${HS_KB.dehumanisingFrames.cite}).`,
      { proposed: 'Describe the specific conduct or policy at issue instead of comparing any group of people to a disease, pest or animal.' });
  }
}

/**
 * Collective blame and inherent-trait accusations: heuristic, routed to review.
 *
 * The prepositional-object gate (groupIsPrepositionalObject) keeps the rule off
 * comparatives about conditions, rights, services and data — "The rights of
 * women are inferior to those guaranteed to men" is a statement about rights,
 * not a claim that women are inferior people, and reporting it told an editor
 * to rewrite wording the tool had misparsed. The gate is a grammar fact, not a
 * leniency: a preposition immediately before the group term makes the group its
 * complement, so the copula cannot be predicated of it. A partitive is exempt,
 * so "All of the foreigners are criminals" still fires.
 */
function ruleHS002(state, unit) {
  const text = unit.text;
  const { hs002Universal, hs002Trait } = patterns();

  hs002Universal.lastIndex = 0;
  let m;
  while ((m = hs002Universal.exec(text))) {
    // A negated universal ("not all foreigners are criminals") is a corrected
    // or hedged statement, not collective blame.
    const before = text.slice(Math.max(0, m.index - 12), m.index);
    if (/\b(?:not|never)\s+$/i.test(before)) continue;
    if (groupIsPrepositionalObject(text, m.index)) continue;
    if (attributedClaim(text, m.index, m[0].length)) continue;
    emit(state, unit, 'UE-HS002', m[0], m.index,
      `Collective framing "${m[0]}" targets a group of people; heuristic, routed to review.`,
      `State a sourced finding about specific conduct rather than a trait of the whole group (source: ${HS_KB.collectiveBlame.cite}).`,
      { proposed: 'Attribute the conduct to specific actors and cite a source, rather than assigning an inherent trait to every member of the group.' });
  }

  hs002Trait.lastIndex = 0;
  while ((m = hs002Trait.exec(text))) {
    if (groupIsPrepositionalObject(text, m.index)) continue;
    if (attributedClaim(text, m.index, m[0].length)) continue;
    emit(state, unit, 'UE-HS002', m[0], m.index,
      `Collective framing "${m[0]}" targets a group of people; heuristic, routed to review.`,
      `State a sourced finding about specific conduct rather than a trait of the whole group (source: ${HS_KB.collectiveBlame.cite}).`,
      { proposed: 'Attribute the conduct to specific actors and cite a source, rather than assigning an inherent trait to every member of the group.' });
  }
}

/** Calls for exclusion or violence against a group, never against individuals. */
function ruleHS003(state, unit) {
  const text = unit.text;
  const { hs003Verb, hs003Modal } = patterns();
  for (const re of [hs003Verb, hs003Modal]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text))) {
      if (attributedClaim(text, m.index, m[0].length)) continue;
      emit(state, unit, 'UE-HS003', m[0], m.index,
        `Call for exclusion or violence against a group of people: "${m[0]}".`,
        `Remove the blanket demand; due process is described for individuals, never as a demand about a group (source: ${HS_KB.exclusionCalls.cite}).`,
        { proposed: 'Ask for the specific legal or policy step, addressed to identified individuals rather than to a group of people.' });
    }
  }
}

/**
 * UE-DM001 — discriminatory or demeaning wording. High-severity human review,
 * never auto-rewrite: the rule passes no replacement, so no finding is ever
 * fixable. Three composition branches (guard note: rules/hate-speech.md):
 *
 *   1. a listed protected group predicated of a demeaning predicate;
 *   2. a disability term within one 300-character window of pity framing;
 *   3. a disability term beside a first-person rejection.
 *
 * For branches 2 and 3 the emitted match is the combined span, so the finding
 * shows both halves that make the wording demeaning, and an exact span is
 * emitted once even when several partners sit in the same window. Anaphoric
 * subjects are not resolved — "They are a burden" stays silent rather than
 * guessing at the referent.
 */
function ruleDM001(state, unit) {
  const text = unit.text;
  const { dm001Predicate, dm001Pity, dm001Disability, dm001Rejection } = patterns();
  const seen = new Set();
  const emitSpan = (matched, index, message) => {
    const key = `${index}:${matched}`;
    if (seen.has(key)) return;
    seen.add(key);
    if (attributedClaim(text, index, matched.length)) return;
    emit(state, unit, 'UE-DM001', matched, index, message,
      `Describe the conduct or policy at issue instead of demeaning or pitying the people concerned (source: ${HS_KB.demeaning.cite}).`,
      { proposed: 'Describe the specific conduct or policy at issue instead of demeaning or pitying the people concerned.' });
  };

  dm001Predicate.lastIndex = 0;
  let m;
  while ((m = dm001Predicate.exec(text))) {
    emitSpan(m[0], m.index,
      `Demeaning predicate "${m[0]}" is predicated of a group of people.`);
  }

  // One finding per partner: pity framing or a first-person rejection pairs
  // with the nearest disability term inside the 300-character window, so two
  // anchors in one window never double-report the same partner and a partner
  // with no anchor nearby stays silent (vocabulary alone never matches).
  const pairNearest = (partner, kind) => {
    let best = null;
    let bestDistance = Infinity;
    dm001Disability.lastIndex = 0;
    let a;
    while ((a = dm001Disability.exec(text))) {
      const from = Math.min(a.index, partner.index);
      const to = Math.max(a.index + a[0].length, partner.index + partner[0].length);
      if (to - from > 300) continue;
      if (to - from < bestDistance) bestDistance = to - from;
      else continue;
      best = { from, to };
    }
    if (!best) return;
    const matched = text.slice(best.from, best.to);
    emitSpan(matched, best.from, kind === 'pity'
      ? `Pity framing around a disability term: "${matched}".`
      : `Demeaning first-person rejection beside a disability term: "${matched}".`);
  };

  dm001Pity.lastIndex = 0;
  let p;
  while ((p = dm001Pity.exec(text))) pairNearest(p, 'pity');
  dm001Rejection.lastIndex = 0;
  while ((p = dm001Rejection.exec(text))) pairNearest(p, 'rejection');
}

// --- UE-DP001 knowledge-base extension ---------------------------------------

// Extension patterns compile lazily, once per compiled claim object: one
// vocabulary build creates the claim objects and every copy span of the scan
// reuses them.
let extCache = null;

function extPatterns(claim) {
  if (!extCache) extCache = new WeakMap();
  if (extCache.has(claim)) return extCache.get(claim);
  const entry = DIPLOMACY_EXT.find(e => e.id === claim.id);
  const compiled = [];
  if (entry) {
    // The extension resolves its own subjects and claimants (they mirror
    // config/profiles/un-v1.json): compileClaim bakes the profile's vocabulary
    // into the baseline regexes and keeps no arrays, and an organisation
    // profile that replaces an entry by id keeps its own `patterns` for the
    // positive forms while the knowledge-base extension keeps negation and
    // variant forms covered for that id. Longest-first alternation, exactly as
    // profile.mjs compiles the baseline patterns.
    const longestFirst = (terms) => [...terms].sort((a, b) => b.length - a.length)
      .map(escapeRe).join('|');
    const subjects = longestFirst(entry.subjects);
    const claimants = longestFirst(entry.claimants);
    for (const template of entry.templates) {
      const parts = template.text.split(/(\{subject\}|\{claimant\})/g);
      let source = '';
      for (const part of parts) {
        if (part === '{subject}') source += `\\b(?:${subjects})\\b`;
        else if (part === '{claimant}') source += `\\b(?:${claimants})\\b`;
        else source += escapeRe(part).replace(/ /g, '\\s+');
      }
      if (template.exclusive) {
        // A dangling "… is part of" must not double-fire where the baseline
        // positive pattern already names the claimant right after it.
        source += `(?!\\s*\\b(?:${claimants})\\b)`;
      }
      compiled.push(new RegExp(source, 'gi'));
    }
  }
  extCache.set(claim, compiled);
  return compiled;
}

/**
 * UE-DP001 with the knowledge-base extension: first the baseline claim
 * patterns — byte-identical to lib/rules.mjs's local ruleDP001, which this
 * registry entry overrides — then the negation, variant and
 * incomplete-assertion templates from lib/diplomacy-ext.mjs for claim ids
 * present in the vocabulary. Allowlist filtering already happened in
 * buildVocabulary, so an allowlisted id never reaches this rule at all, and
 * the attribution guard runs before every emission, baseline or extension.
 */
function ruleDP001ext(state, unit) {
  for (const claim of state.vocab.claims) {
    const claimPatterns = [...claim.patterns, ...extPatterns(claim)];
    for (const re of claimPatterns) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(unit.text))) {
        if (attributedClaim(unit.text, m.index, m[0].length)) continue;
        emit(state, unit, 'UE-DP001', m[0], m.index,
          `Contested status claim "${m[0]}" about ${claim.topic} stated as fact.`,
          `Attribute the claim to the party advancing it or use neutral wording: "${claim.neutral}" `
          + `(UN terminology: "${claim.unTerminology}"; source: ${claim.source}).`,
          { proposed: claim.neutral });
      }
    }
  }
}

export const HS_RULES = {
  'UE-HS001': ruleHS001,
  'UE-HS002': ruleHS002,
  'UE-HS003': ruleHS003,
  'UE-DM001': ruleDM001,
  // Spread after lib/rules.mjs's local 'UE-DP001' key in RULE_BY_ID: this
  // override replays the baseline behaviour and adds the extension forms.
  'UE-DP001': ruleDP001ext,
};
