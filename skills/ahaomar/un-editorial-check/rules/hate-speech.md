# Hate speech

- **UE-HS001** *(error)* — A listed group of people is predicated of a listed dehumanising frame, such as `"Foreigners are vermin."` Deterministic and not fixable: the finding reports the matched wording and proposes no replacement.
- **UE-HS002** *(warning)* — Collective blame or an inherent trait attributed to a whole listed group, such as `"All Syrians are terrorists."` Heuristic, routed to review; it never claims proof of intent. Heuristic findings ship as warnings so a judgement question never fails a build on its own, and the finding is routed to the harmful-discriminatory review lane for high-severity human review.
- **UE-HS003** *(error)* — A call for exclusion or violence against a listed group, such as `"Deport all Iraqis."`, rather than individual legal process. A modal plus an outcome verb counts only when the outcome ends the clause, for example `"Foreigners must go."`, or continues into an exclusion phrase, for example `"Foreigners should leave the country."`; operational copy that merely borrows an outcome verb stays silent. Deterministic and not fixable.
- **UE-DM001** *(error)* — A demeaning predicate or pity framing about a listed protected group, such as `"Women are burden."` or `"the neighbours felt sorry for the wheelchair user"`, stated in user-visible copy. Composition over word lists: the predicate alone never matches — a listed protected group must be predicated of it, a disability term must sit near pity framing within one copy span, or a first-person rejection must sit beside a disability term. Anaphoric subjects (`"They are a burden"`) are not resolved and stay silent rather than guessing. Deterministic, report-only, never rewritten automatically: the finding is routed to the harmful-discriminatory review lane for high-severity human review and is not a legal judgement.

## How detection works

The knowledge base lives in `lib/rules-hs.mjs` under `HS_KB`, and every entry carries a `source` citation:

- `groups` — the shared vocabulary of groups of people (religions, ethnic and national groups, migration status, racialised groups, and — since Wave 3 — the protected characteristics of sex or gender, age and disability: `women`, `men`, `girls`, `boys`, `elderly`, `older people`, `people with disabilities`, `wheelchair users`) that feeds all four rules;
- `dehumanisingFrames` — pest, disease, animal and filth imagery, used by UE-HS001;
- `collectiveBlame` — accusation nouns, trait adjectives and inherent-trait markers, used by UE-HS002;
- `exclusionCalls` — base-form verbs, modal verbs, outcome verbs and the exclusion continuations that may follow them, used by UE-HS003;
- `demeaning` — demeaning predicates, pity framing, disability terms and first-person rejections, used by UE-DM001; each list is vocabulary for a composition branch and never matches on its own.

Composition over word lists: a frame, accusation, verb or demeaning predicate never matches on its own — it fires only when predicated of, or paired within one copy span with, a listed group of people or disability term. Because one shared group vocabulary feeds all four rules, swapping which group is named cannot change whether a mirrored sentence fires. The rules run on extracted copy, so quotations, comments, URLs and code are already outside the span, and claims attributed to a reporting party are exempt through the same guard as `UE-DP001`.

## What stays silent

- Bare group mentions, for example `"The delegation met refugees and immigrants."`;
- reported claims, where attribution such as `"The envoy said that foreigners are vermin."` or `", the ambassador stated."` names who advances the claim;
- quoted copy and block quotations, because extraction masks those spans before any rule runs;
- pest, disease and animal wording with no human group in it, such as `"The inspection found rats in the store room."`;
- individual legal process and past-tense narrative, for example `"The court ordered the deportations after individual hearings."` and `"Attackers killed the refugees in the camp."`;
- operational copy where a modal outcome does not end the clause and does not continue into an exclusion phrase, such as `"Refugees should go through the registration process at the border."` and `"Migrants must leave their documents at the checkpoint."`;
- a bare accusation without a quantifier, such as `"Foreigners are criminals."` — UE-HS002 requires the universal form or a trait predicate of the group;
- anaphoric subjects with no named group or disability term in the span, such as `"They are a burden."` — UE-DM001 does not resolve referents and stays silent rather than guessing.

## Extending and opting out

- `config.severities` re-grades a rule and `config.rules` switches one off, for example `{"UE-HS002": {"enabled": false}}`; both keys work in a profile too;
- `ue:ignore UE-HS001` suppresses one rule inside one copy span;
- the group vocabulary and the frame, accusation, verb and demeaning lists live in `HS_KB`, so an extension applied there keeps the four rules symmetric by construction.

## Reporting

Findings carry `current`, the matched wording, and a suggestion that cites the knowledge-base source behind the finding; UE-HS002 says `heuristic, routed to review` on every finding. Nothing here is rewritten by `--fix`: no finding carries a replacement, and `proposed` carries review guidance only. A match is wording for human review, not a legal finding of incitement. UE-DM001 findings are high-severity human review: severity error, the harmful-discriminatory review lane, and never an automatic rewrite of the matched wording.
