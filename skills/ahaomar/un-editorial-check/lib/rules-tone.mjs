// Aggressive / undiplomatic tone rules — UE-RE006..UE-RE008.
//
// The register family (UE-RE001..UE-RE005 in lib/rules.mjs) polishes neutral
// wording; this file catches the sharper failures: name-calling, threat
// posture and all-caps shouting. All three are REPORT-ONLY in this phase —
// no finding ever carries a replacement, because a heuristic tone call must
// not be auto-applied to copy before it has soaked against real documents.
//
// Patterns are regex literals or built inside the rule functions, and the
// helpers from lib/rules.mjs are only ever called from inside a rule: never
// at module top level, so this file can be imported alongside rules.mjs
// without depending on evaluation order.

import { emit } from './rules.mjs';

export const TONE_RULES = {
  'UE-RE006': ruleRE006,
  'UE-RE007': ruleRE007,
  'UE-RE008': ruleRE008,
};

export const TONE_META = {
  'UE-RE006': { category: 'register', confidence: 'heuristic', severity: 'warning' },
  'UE-RE007': { category: 'register', confidence: 'heuristic', severity: 'warning' },
  'UE-RE008': { category: 'register', confidence: 'deterministic', severity: 'warning' },
};

// --- UE-RE006: insult, name-calling, contempt appellation -------------------
//
// Two appellation shapes only: an article (optionally followed by an
// intensifier) plus a singular insult noun ("a clown", "a complete idiot"),
// or a bare plural used as a label ("idiots", "losers"). Adjective uses
// ("foolish"), verb uses and singulars with no article never match — the rule
// reports the shape it can prove and leaves the judgement to review, because
// it cannot tell criticism of a person from criticism of a policy.
const INSULT_RE =
  /\b(?:a|an|another|such\s+a|such\s+an)\s+(?:(?:complete|total|absolute|utter|real|contemptible|stupid)\s+)*(?:clown|buffoon|fool|idiot|moron|loser|amateur|incompetent|crook|thug|bigot|bully|coward|hypocrite|fraud|fanatic)\b|\b(?:clowns|buffoons|idiots|morons|losers|amateurs|incompetents|crooks|thugs|bigots|bullies|cowards|hypocrites|frauds|fanatics)\b/gi;

function ruleRE006(state, unit) {
  INSULT_RE.lastIndex = 0;
  let m;
  while ((m = INSULT_RE.exec(unit.text))) {
    emit(state, unit, 'UE-RE006', m[0], m.index,
      `Insult or contempt label "${m[0]}" — the CLI cannot judge whether the target is a person, a group or a policy.`,
      'Replace the label with a neutral description of the conduct or decision at issue.',
      { proposed: 'Describe the specific statement, decision or conduct at issue in place of a label for the person or group.' });
  }
}

// --- UE-RE007: threat / intimidation posture --------------------------------
//
// Fixed phrases only. The rule cannot separate a threat from idiom — a
// sports sentence ("the squad will regret the missed penalty") matches and is
// routed to review — while two finance/sports collocations are excluded by
// pattern so they never fire: "crush expectations" and "crush records".
// Both halves of that claim are locked by fixtures and by assertions in
// .feedbacks/verify-tone.mjs.
const THREAT_RE =
  /\bwill regret\b|\b(?:is|are) going to regret\b|\bwill be sorry\b|\bshould (?:really |certainly )?be afraid\b|\bshould (?:really |certainly )?fear\b|\bno choice but to crush\b|\b(?:will|must|shall) crush\b(?!\s+(?:the\s+)?(?:expectations?|records?|targets?|numbers?)\b)/gi;

function ruleRE007(state, unit) {
  THREAT_RE.lastIndex = 0;
  let m;
  while ((m = THREAT_RE.exec(unit.text))) {
    emit(state, unit, 'UE-RE007', m[0], m.index,
      `Threat or intimidation phrase "${m[0]}" — matched as a fixed phrase; intent cannot be judged here.`,
      'Rephrase as a formal statement of consequences without the threatening framing.',
      { proposed: 'State the consequence you expect and the action that would avoid it, phrased as a formal position.' });
  }
}

// --- UE-RE008: ALL-CAPS shouting --------------------------------------------
//
// A standalone token of five or more uppercase letters, with no adjacent word
// character, digit, hyphen or slash (so "COVID-19", "path/LOUDER" and
// hyphenated compounds never match) and no file-name extension after it
// ("README.md" is a file reference, not shouting). Short initialisms are out
// of scope by the length floor; the exemption list covers the ones the floor
// does not reach. The list is finite and that limitation is stated in the
// catalogue guardNotes: an initialism, heading or reference word missing from
// it is reported.
export const CAPS_EXEMPT = new Set([
  // short initialisms — kept for documentation even though the five-letter
  // floor already excludes them
  'UN', 'USA', 'NATO', 'WHO', 'EU', 'DPRK', 'OAU', 'IAEA', 'OPEC',
  // five letters or more: these would match without the list
  'ASEAN', 'UNHCR', 'ECOSOC', 'UNCTAD', 'UNFCCC', 'UNESCO', 'UNICEF',
  'UNEP', 'UNIDO', 'UNODC', 'UNFPA', 'UNOPS', 'OECD', 'BRICS', 'COVID',
  'SARIF',
  // file and help-heading reference words that read as structure, not prose
  'README', 'USAGE', 'OPTIONS', 'CODES',
]);

const CAPS_RE = /(?<![\w/-])[A-Z]{5,}(?![\w/-])(?!\.[a-z])/g;

function ruleRE008(state, unit) {
  CAPS_RE.lastIndex = 0;
  let m;
  while ((m = CAPS_RE.exec(unit.text))) {
    if (CAPS_EXEMPT.has(m[0])) continue;
    emit(state, unit, 'UE-RE008', m[0], m.index,
      `All-caps word "${m[0]}" in running prose.`,
      'Use lower case in running prose; suppress an accepted initialism with ue:ignore UE-RE008.',
      { proposed: 'Set the word in lower case in running prose; keep upper case for accepted initialisms and headings.' });
  }
}
