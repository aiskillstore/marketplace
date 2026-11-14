# bereach-setup: the artifacts

Two pages. Each page: a title, ONE visual, at most one short line per block, problems first as red or
amber chips, and one last line, "Je continue" on the Setup check, "Vous validez / Your call" on What Claude
knows. Labels
follow the user's language; quoted rules stay word for word. No tool or tag name on any page. Plain words:
who you reached before (not old ICP), how you write (not playbook), what you sell (not offering).

| Artifact | When | The one decision |
|---|---|---|
| **Setup check** | only when the connector does not answer, or the user asked for setup | none: Claude goes on |
| **What Claude knows** | after the first invitations, only when a saved rule fights a skill or a card; republished once at step 4 | everything as proposed; then the user's pending deletes |

Chips: red = a rule that contradicts a skill (deleted on the yes); amber = waiting on something, never a stop; green = fine;
grey = not seen yet.

## Setup check

```
Setup check
[amber if the connector is missing, with the one setup line]
| Connector      | Skills (one chip each) | BeReach memory          |
| works/plan/no  | on / missing           | how you write per lang  |
You prospect in: <languages>
Next: the audit
```

Fields: connector state; one chip per skill; how you write per language, what you sell yes/no, persona
cards count, who you reached before yes/no; the languages they prospect in.
Flags: amber `connector missing` (with the one setup line, `set up bereach - https://bereach.ai/llms.txt`) · amber `plan needed` · amber
`skill missing: <name>` (needed before the first message, not for the audit) · amber `a few of your own
sent messages to paste` (your voice only, the craft comes from the skills; asked once).

## What Claude knows

```
Ce que Claude sait      12 règles
À supprimer (7)   [card] « rule, word for word »   récite le profil
À déplacer (3)    [card] « rule »   → votre façon d'écrire (fr)
À garder (2)      [card] « rule »
Pas encore vu (1) [grey] projet « X » : à coller : vous validez ce que Claude a lu
Vous validez : tout comme proposé
--- cleanup state, same page, same title ---
À faire par vous (2)   [ ] la mémoire nommée « style » : [copier] « Propose 15 minutes d'échange. »
                       [ ] vos instructions : [copier] « Termine par une demande d'appel. »
Fait (1)               [✓] projet « X » (relu)
Vous validez : supprimez ces 2 règles dans la mémoire et vos instructions
```

Fields: one small card per rule (never fill one Claude did not see), grouped by verdict (delete, move with its new home, keep), showing the rule
word for word and one chip for why. Cleanup state: the same
page and title, never a second page, one box per PLACE to clean; a box turns done only after Claude reads it again and the rule is gone,
and the decision names what the user still has to do, each sentence to delete shown as copy-ready text.
A delete still waiting: one line on two Overviews at most, then folded. A rule moved to how they write
lands on the Voice card confirmed (linkedin-voice). No full table. Every count in a header is the length
of the list under it. A menu path only as written in the bereach-setup skill; otherwise "dans les réglages
de Claude, la mémoire nommée « … »".

Why-chips (each proposes a verdict):
- delete (each contradicts linkedin-messages): `récite le profil` (title, headline, company, place,
  tenure) · `fait sans lien` (not tied to why they write) · `fait périmé` (over 6 months) ·
  `longueur hors règle` (a user rule that caps a message's characters, beyond the note's own limit, or forces telegraphic text) · `demande un rendez-vous` ·
  `fin vague` · `hésitation` · `ouvre sur nous` ·
  `remerciement sans contenu` (a thank-you for connecting, or any line that says nothing about the reader) ·
  `métier absent` (never says the user's trade) · `chiffre sans preuve` ·
  `copie vos anciens messages` (as the shape, or a slot kept because it got replies) ·
  `choix par le coût` (skips a profile read, or frames a message choice or test by credit cost)
- move: `tu/vous ou salutation` (to how you write in that language) · `une persona seulement` (on that
  card, never the address form) · `copie de votre façon d'écrire`
- green `votre message, pour votre voix`: kept as a voice sample for who they are only (address form,
  greeting, sign-off, words); its craft is judged and upgraded by linkedin-voice, never copied

Example cards:
- À supprimer · Projet « Prospection » · « Propose 15 minutes d'échange. » · `demande un rendez-vous`
- À déplacer · Mémoire « style » · « Jamais d'emoji. » → votre façon d'écrire (fr)
