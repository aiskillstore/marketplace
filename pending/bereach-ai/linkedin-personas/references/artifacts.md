# Artifacts of the personas skill

Where each block goes: SKILL.md, top.

## Every page

- A title, ONE visual, at most one short line per block. No theory, no paragraph.
- Problems first, as chips at the top and again on the card or row: red holds a row or a message,
  amber: Claude goes on, grey is too early, green is fine. A card shows only its current value: what Claude fixed is fixed before the
  page; old against new only on the Step 6 table. No open flag: one green chip "Rien à corriger".
- Chips in the user's language, never an internal word ("brief", "filtre", "strike"). A row the user may
  refuse carries "pas celle-ci" / "not this one".
- A republish that changes only counts or one line shows the changed lines only, never the full cards.
- Ends on one line: "Je continue : ..." / "Next: ..." when nothing waits for a yes; "Vous validez : ..." only
  for v2's changed lines, the open rows of Who is who (when it runs alone; inside the outreach pages they
  are held rows of Invitations to send), or a removal. ONE decision, never two joined by "and".
- The user's language (French: "Fiches persona", "Qui est qui", "vous"). Leads as first name and last
  initial, never a photo.
- Never on a page: a tool or tag name, where the data comes from, how people were found, a credit balance.

One word per status, the same on every page:

| Internal | French | English | Chip |
|---|---|---|---|
| `HOLD` | Pas de message | No message | red |
| `CHECK` | À vérifier | To check | amber |
| `sure` | Sûr | Sure | green |
| `sure` by title | Sûr : par titre | Sure: by title | green |
| `(guess)` at a line's end | (hypothèse) | (guess) | grey text |
| Seen in N replies | Vu dans N réponses | Seen in N replies | green |

## 1. Persona cards

When: v1, a block of Plan and personas, provisional. Again in Step 6, after Results, as Persona cards v2: a small table, one row per changed line, three cells (avant /
maintenant / source: "vu dans N réponses" or "votre idée"), an open question as one amber chip on its row;
a figure is the Results one, label unchanged; a confirmed line keeps the user's saved answer (only its source changes); an unchanged card is one grey line.

```
Fiches persona
[grey fiches v1 : provisoires] [! client cité : accord ?] [! réponse à écrire : 1]
+ Responsable réseau          + + Bureau d'études         +
| Qui · Trouvé par            | | ...                     |
| Pourquoi maintenant         | |                         |
| Douleur                     | |                         |
| Offre                       | |                         |
| Preuve                      | |                         |
| Objection                   | |                         |
|  Votre réponse : [ champ ]  | |                         |
| Ton · À ne jamais dire      | |                         |
| > Plus                      | |                         |
+-----------------------------+ +-------------------------+
Je continue : ces fiches v1 ; votre réponse sur « pas maintenant » quand vous l'avez.
```

Band under the title: only frameworks from `references/frameworks.md` read in this session that the cards visibly apply; none read, no band.

The 7 Core lines of `references/persona-card.md`, in order, read in one go; the More fields only when known,
folded under "Plus". Card header: the persona name, no count (Who is who carries the counts). The header's
"réponse à écrire : N" counts exactly the answer fields on the page. Pain and Proof show their source in grey.
Top chip row (what was read, what is missing): `references/sources.md` section 4. Only open chips about facts
the user must supply; wording fixes belong to message pages.

Claude fixes before the page: the Offer retelling the Proof, two cards with the same first message
(merged), an Offer the user never made, a Pain fighting the objection, a tool, date or deadline the facts
do not give. Pain and Proof never sit beside a
status that contradicts their source. An unnamed Proof keeps the client company folded (it leaves past
clients out of the searches and finds companies like them).

Flags:

- red `chiffre non prouvé` (EN `unproven figure`): a rate, % or before/after figure in Proof the user did
  not give for a real customer.
- red `réponse inventée`: an answer promises a service, speed or result the user never stated. Empty it.
- red `inventé`: a line marked seen with fewer than 2 replies behind it (same meaning, each wording
  quoted), or a line neither given by the user nor marked `(guess)`.
- red `preuve sans source`: Proof not in the user's words; blocks the templates.
- red `données d'un tiers`: the Offer needs their clients', patients' or staff's data; a no-data version
  is proposed.
- red `traits personnels`: age, gender, hobbies, school, photo, personality type.
- red `demande un rendez-vous`, only when the user's Never list has it; otherwise Claude rewrites it.
- amber `titre récité`: Why now or Pain restates the title or headline.
- amber `hésitation`: a line hedges or guesses their feelings.
- amber `pas de fenêtre`: Why now has no window (6 months shown in grey).
- amber `pas de signal`: Why now says no public fact to look for.
- amber `trop tôt : moment à confirmer`: Why now is earlier than the hiring moment the user gave, or the
  objection answer places the user's work after it. The v1 card goes on.
- amber `tu/vous`: empty, or against how their world writes (vous by default, in grey).
- amber `réponse à écrire par vous`: the objection has no answer from the user yet. Never fill it: a text
  field on the page; the follow-up that needs it waits; the cards do not.
- amber `client cité : accord ?`: Proof names a customer not yet cleared. Removing the name keeps the proof,
  described.

Decision: "Je continue : ces 3 fiches v1." (Step 6: "Vous validez : les 2 lignes changées.")
A "queued for next test" note goes on Next test only.

Example (fictional seller: field calibration software for water networks):

```
Régie des eaux aux compteurs anciens : son responsable réseau
Trouvé par   Responsable réseau, Head of Water Networks, Chef d'exploitation ; régies des eaux 50 à 2 000
Pourquoi     un appel d'offres de renouvellement des compteurs (6 mois) : la précision à prouver. Signal : un appel d'offres publié (hypothèse)
Douleur      nos compteurs dérivent et on le découvre à l'audit annuel (hypothèse)
Offre        un contrôle de dérive sur les compteurs d'un secteur (vous l'offrez déjà)
Preuve       une dérive trouvée sur un secteur avant l'audit annuel, pour une régie (sans nom ; vos mots)
Objection    Pas maintenant. Votre réponse : [ champ ]
Ton          vous ; jamais "disruptif", "solution"
> Plus       Qui d'autre décide, Prix
```

## 2. Who is who

When: the split of the untouched people on Plan and personas (its count is the one kept there, with every
filter the user answered applied), the settled count and the held rows on Invitations to send. The cards
are never republished for counts.

```
Qui est qui   126 leads
[x 3 pas de message] [! 4 à vérifier] [119 sûrs]
Responsable réseau ||||||||||||||||    56
Bureau d'études    ||||||||||||||||||  63
À vérifier      ||||                 4
Pas de message  |||                  3
À TRANCHER  Léa R.  Étudiante · Régie Delta  [Pas de message : étudiante]
            Paul V. Chef de projet eau · ...     [À vérifier : deux fiches]
> Responsable réseau : 56 sûrs (folded)
Vous validez : Paul V. va dans Responsable réseau
```

Band under the title: "ICP puis persona (Wind et Cardozo), anti-persona (Pruitt et Grudin)".

Fields per row: lead, title, company, persona chip, why (title, or one dated fact with month and year),
status with its reason said once in the chip. One bar per persona with its tagged `sure` count (the count
every later page reads), then To check, No message; a lead found out of scope here leaves with one grey
line.
Only the rows to settle are open; `sure` rows fold per persona.

Flags:

- red `Pas de message : étudiant`, `: projet perso`, `: votre équipe`, `: hors ICP`, only for a lead added
  after step 1 (those found in step 1 left on Plan and personas).
- amber `À vérifier : deux fiches`: two cards fit and nothing splits them; name both cards.
- amber `À vérifier : entreprise hors ICP`: the company is outside the ICP (kind, size, place).
- amber `fait à revoir`: a later brief dates the fact that settled the persona differently (both shown).

Decision, computed from what is still open: row by row up to 10 ("Vous validez : Paul V. va dans Responsable
réseau"); above 10, one rule per lot ("Vous validez : les 31 à deux fiches vont dans la fiche de leur
taille d'entreprise"); several lots: "Vous validez : les règles proposées", one row per lot, each
with "pas celle-ci". After the yes, the same page with a
green `réglé` chip, never a second page.

Example:

| Lead | Titre | Persona | Pourquoi | Statut |
|---|---|---|---|---|
| Léa R. | Étudiante, alternance | Responsable réseau | En master jusqu'en 2027 | Pas de message : étudiante |
| Sami L. | Network Manager | Responsable réseau | Titre | Sûr : par titre |
| Inès B. | Head of Water Networks | Responsable réseau | Appel d'offres compteurs publié en 2026-10 | Sûr |
