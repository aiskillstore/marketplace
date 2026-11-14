# The artifacts

One page per step: a title, the problems as chips (red holds a row or a send, amber: Claude goes on, grey
not readable yet), ONE visual, one short line per block, then, on a page that waits for a yes (the order table), "Vous
validez : ..." / "Your call: ..." with the one decision; on any other, "Je continue : ..." / "Next: ..." saying
what Claude does now. Real leads only, in the user's language. Counts under 10 sent, never a percent. Credits
only in the footer of a page whose searches spend them (an estimate says "estimé" and is never summed), never for briefs, profile reads, drafts, invitations or messages, never a chip, never a balance; no other footer (never how the page was made; at most
one line on what happens next, and at most one app link, App links below). Leads as first name and last
initial, never a photo. No tool, tag or field name, no vendor, never "scraper", "export", "autopilot",
"sends for you", never "data from LinkedIn", no em or en dash; the same words are rephrased inside the
user's own quoted text too. No statistics or method words on a page: say "le guide" / "l'exemple chiffré" (what
a half carries), never "moitié", "bras", "prémisse", "variante", "points", "bruit", "fallback", "strike" or
a p-value (EN: never "arm", "premise", "half"). A chip is a short sentence in the user's language saying
what happens ("3 déjà en conversation : retirés", the names behind it), only for a problem, never always
true, never a zero count, never "brief" or "filtre". A row the user may refuse carries "pas celle-ci" / "not
this one". A choice left to the user is named open in the decision ("Propriétaires : [changement ou pause]"),
filled only after the answer. Examples: Atelier Nord, energy audits of buildings, French, "vous" (invented).
Under each title one grey band "Framework (Author)", only names read in the frameworks file that holds them and visibly applied on that page (this skill's `references/frameworks.md`; Voice: the linkedin-voice skill's; messages: the linkedin-messages skill's), plain names in the user's language (FR shown): Plan and personas: Revenu prévisible (Ross), Signaux d'achat (Elias) · Invitations to send: Une seule différence (Kohavi), Taille fixée d'avance (Miller) · Voice and messages: Voix et ton (Mailchimp), Premise first (Becc Holland) · Drafts for review: Premise first (Becc Holland), Donner d'abord (Regan, Falk) · Follow-ups to send: Preuve sociale (Cialdini), Laisser partir (Braun), FAB (Rackham) · Results: Comparer à âge égal, Paradoxe de Simpson (Simpson) · Next test: Une seule différence (Kohavi) · Overview: its current step's band.

## The names (identical in every skill)
| Artifact | Step | Drawn by |
|---|---|---|
| Overview | on, only when nothing waits elsewhere | linkedin-outreach-method |
| Plan and personas | 1 | linkedin-outreach-method, cards by linkedin-personas |
| Persona cards v1, Who is who | blocks of Plan and personas and Invitations to send; own page only when linkedin-personas runs alone | linkedin-personas |
| Voice and messages | 3, after Invitations to send | linkedin-voice, linkedin-messages |
| What Claude knows | after the first invitations, only when a saved rule fights a skill or a card | bereach-setup |
| Invitations to send | 2 | linkedin-outreach-method |
| Drafts for review | 4 | linkedin-outreach-method, fields from linkedin-messages |
| Follow-ups to send | 4 | linkedin-outreach-method |
| Results | 5 | linkedin-outreach-method |
| Persona cards v2 | 5, after Results | linkedin-personas |
| Next test | 6 | linkedin-outreach-method |
| Go further | end of the fast start, a card | linkedin-outreach-method |
| Setup check | before 1, only when the connector does not answer; never stops the cards or the voice | bereach-setup |
| Sending check, Who is who, Message templates, Drafts for review, Ready to send, Results | cold email, beside LinkedIn | cold-email |

## Labels, FR | EN (every skill uses these)
| FR | EN |
|---|---|
| PRÊT · À CORRIGER · À VÉRIFIER · EN ATTENTE | READY · TO FIX · TO CHECK · ON HOLD |
| trop tôt · direction · prouvé · base seule | too early · direction · proven · baseline only |
| Vous validez : | Your call: |
| Je continue : | Next: |
| contrôles OK | checks OK |
| salutation comme la carte de voix | greeting as voice card |
| comparé à 7 jours | read at 7 days |
| sans objet | not used |
| attend votre oui · prévu · en cours | awaits your yes · planned · counting |
| piste, pas preuve · résumé, pas cité · aucune réponse | hint, not proof · summary, not quoted · no answer |
| direction (devant, pas prouvé) · nouvelle période, pas un test | ahead, not proven yet · new period, not a test |
| modifié par vous · intéressés · non | edited by you · interested · no |
| inventé · offre floue · fait périmé | invented · vague offer · stale fact |
| mois chargés · trop petit pour se voir | busy months · too small to see |
| illisible · cadre tassé · pas sur eux | hard to read · framework squeezed · not about them |
| réglé · réponse à écrire · [A ou B] | settled · answer to write · [A or B] |

## Message checks (only on a page that shows a message)
Every page that shows a message runs the chips of linkedin-messages `references/artifacts.md` (one vocabulary,
kept there), green `contrôles OK` when none. Each message is read aloud once and its `illisible` and `cadre
tassé` are fixed by Claude before the page is drawn; a draft carries its `Cadre :` line only when it visibly applies the framework (defined there).

## Before publishing any page
Every name unique on the page (add an initial or the company); every count copied from the page that made
it (kept leads, then the Who is who total, half sizes from Invitations to send, rates and labels from
Results); one person keeps one status and one persona on every page; every number recounted from the rows
it sums (due = sent minus answered minus held); every note length counted by the one rule (linkedin-messages, Size), the same
note the same count on every page; a chip that would show on every page is said once; every chip and
label read back as a whole phrase, agreement checked ("1 intéressé", "2 blancs"). An example is a lead
of THAT send not messaged yet; a quoted message is exactly as sent; no first name used as an ordinary word.

## Overview (same URL; only when nothing waits on another page: after the Invitations yes, between batches, after the Results decision)
```
Vue d'ensemble · Atelier Nord
✓ Invitations  ✓ Voix et messages  ● Brouillons lot 2  ○ Relances 24 oct  ○ Résultats 31 oct
Prochaine décision : 24 oct, les relances du lot 1
Crédits des recherches : 284
```
Fields: ONE stepper (at most 5 steps, done and next, dated next steps grey `prévu`), ONE line "Prochaine
décision : <date>, <what>" and no "Vous validez", ONE credits line: what the searches spent, nothing
else. At most one line per open fact with its consequence (a reply waiting and its age, a late accept,
"lecture le 26 nov", the next send date with its reason when over 2 weeks away). A to-do left to the user
shows on two Overviews at most, then in one folded "à faire" line. Never a chip row repeated from a page,
no message check before messages exist.

## Plan and personas (step 1, before the searches, then republished after)
```
Plan et personas
[grey fiches v1 : provisoires, les réponses les améliorent]
| Persona    | Déjà dans votre compte | À chercher | Pourquoi eux                     |
| Syndics    | 64                     | 0          | (assez pour la première semaine) |
| Promoteurs | 9                      | ~25        | par rôle, puis levée récente     |
> les fiches (open on the first) · > qui est où (folded per persona)
3 premiers messages · aperçu                    [grey aperçu : rien ne part]
( 3 bubbles: Claire M. (Syndics), Inès T. (Promoteurs), Hugo B. (Syndics), as each would get it )
Vous validez : je lance ces recherches
(footer) ~180 crédits estimés
--- after the searches, same page ---
126 gardés · 23 retirés : hors de Lyon, plus de 200 salariés, étudiants (grey)
Je continue : les invitations
(footer) 184 crédits · Votre liste : <list_url>
```
Fields: per persona the untouched people already in the account, what is still searched, why them in plain
words (one row per door: `references/search-doors.md`), found, kept, spent; the cards v1
(linkedin-personas); the questions answered in chat as chips; estimated credits in the footer; a count
only when not zero.
Band "3 premiers messages" / "3 first messages": 3 real leads sure on Who is who, one per persona when
possible (the rest from the largest), each the lead with the strongest known fact (a signal, a recent post);
its `bereach_brief`, every part on, gives the two per-lead slots, both highlighted: the fact (linkedin-messages, The fact per lead) and the offer's object framed by it. A brief with no
dated fact under 6 months: the next lead of that persona is briefed instead; the card's moment line only when
none of the persona has one, at most one bubble in 3. Written by the
linkedin-messages skill (its fact, Show and chips) from the v1 card in its template per type, the voice
from the user's messages that got replies; the offer only one the user made or a prospect asked for, else their
proven ask, never a placeholder. Grey `aperçu`
on each bubble: never drafted in BeReach, never queued, never sent; the Message checks run, each the framework whole, amber `long` over about 500. No lead in the account yet: drawn on the republish after the searches. No credits for the briefs.
Flags: amber `un rôle fait plus de la moitié : scinder ?` (only when its ICP was not put first) · grey
`marchés en attente` · amber `moins de nouveaux que prévu : on part avec ceux-là` · amber `pas de
profil : N`. No search ran: no "Vous validez", the page ends on "Je continue : les invitations".

## What got replies (no page: a folded band on Voice and messages; method `references/conversation-review.md`)
Fields: best message verbatim (folded as "avant" beside its upgraded version); the chart, keep, drop
(what not to do lives here, never on Message templates) and their words with N, as conversation-review.md
builds them (the cards copy this N). The voice reference is chosen on the Voice card only.
Flags: grey `piste, pas preuve` (always: past messages are never proof, `references/measuring.md`) · amber `résumé, pas cité`. Nothing answered: one line instead of the band ("11 lus,
aucune réponse : on évite l'appel, le titre récité").

## Invitations to send (step 2, after the dry run)
```
Invitations à envoyer              212 invitations
| Persona    | Réglés | Écartés | Le guide | L'exemple chiffré | Exemples |
| Syndics    | 185    | 5       | 90             | 90      | Claire M.  |
| Promoteurs | 33     | 1       | 32 (une seule version)     | Inès T.    |
Syndics : ~31 premiers messages de chaque côté, assez pour comparer     > le calcul (folded)
[grey Promoteurs : trop peu de leads pour comparer]
Tenus (3) : Nadia S. déjà en conversation · Paul V. deux fiches   pas celle-ci
60 par semaine, votre compte en permet 100 · dernier lot 4 nov · Résultats 11 nov
Vous validez : ces invitations partent, mêlées chaque jour
(footer) Vos invitations : https://chat.bereach.ai/connections
```
Fields: one row per persona: settled on Who is who, set aside (each lead once, why folded), then what each
side carries; the two versions side by side with the one changed slot highlighted (a note test: "Sans note
: (rien)" | "Avec note : <text> (n/200)", the first message identical in both and never opening on the note's fact or moment line; the note is the premise note (Holland), each
invitee's real fact, who writes in a few words, why it made them want to connect, their real first name (never a blank), the closing
line varied, never a shared trade the facts do not show; no fact, no note: linkedin-messages, invitation note); no pair: one count, grey
`base seule`. The expected first messages per side as one result line, the formula folded.
The headline proposal (SKILL step 5) as one amber line `titre de profil : <proposition>`. The pace: invitations per week against
the account's weekly ceiling from the dry run. Two computed dates, never reworded: last batch = the first batch day on or after the last invitation + 7; Results = that + 7. A
repeat search: its Who is who as one settled line ("176 Agents par titre, sûrs"), inside this page's yes.
Held rows (already talking, past client, two cards, outside the ICP) listed under the table with "pas
celle-ci", the page goes on. Flags: red `note > 200 car.` · red `blanc dans la note` · amber `côtés inégaux` (more than 1 apart) · amber `trop
petit pour se voir` (one grey line: se lit comme une direction) · amber `plus que votre
compte` (pace over the weekly ceiling) · grey `sans note : compte gratuit` (the account cannot add notes).

## Go further (last card of the fast start, after Invitations to send or after the first Drafts for review)
```
Pour aller plus loin
[grey départ rapide, voulu : chaque étape s'améliore ensuite]
· Fiches v2 avec les vraies réponses                 linkedin-personas
· Votre voix tirée des messages qui ont marché        linkedin-voice
· Un seul test à la fois                              linkedin-outreach-method
· Taux à 7 jours par persona                          linkedin-outreach-method
· L'email en second canal                             cold-email
Je continue : <the next dated step>
```
A card, not a page: 4 or 5 lines, each one improvement and the skill that does it (the skill name, never a
path), none already done or already dated on the Overview. Shown once; afterwards one Overview line at most.

## Drafts for review (step 4, each batch of accepts)
```
Brouillons à relire · Syndics, lot 1        12 acceptés
[1 à vérifier] [1 vous a écrit]
( 3 bubbles: real messages as Claire M., Hugo B., Inès T. get them, filled, fact and offer's object highlighted, each message version shown )
À trancher : Nadia S. À VÉRIFIER (deux fiches) · Léo P. EN ATTENTE (vous a écrit : his message + a reply)
> 10 PRÊT (folded)
Vous validez : les 10 PRÊT partent
(footer) Vos brouillons : https://chat.bereach.ai/drafts
```
Always 3 real messages rendered as the prospect gets them, each message version at least once (a note
test has one), never a placeholder, then ONLY the rows to decide under "À trancher"; never dozens of
identical rows, never a per-side count table. Fields per lead and statuses: linkedin-messages (its
artifacts). After the yes, each edit the user made is listed under it, the row tagged `modifié par vous`.
Flags: red as in "Message checks" · amber `À VÉRIFIER`.

## Follow-ups to send (step 4, each day something is due or an interested reply arrives)
```
Relances et réponses · 24 oct
Réponses à traiter (2) : Nadia S. « Vous chiffrez sur visite ? » → ( proposed answer, [ votre réponse : ... ] )
Lot 1, relance 1 · 9 dues [grey 2 ont répondu : arrêt · 1 collègue tenu]  ( 2 bubbles as two real people get them )
Lot 2, relance 2 · 6 dues                               ( 2 bubbles )
Vous validez : ces 2 réponses et ces 15 relances partent aujourd'hui
```
Every follow-up and every reply gets this page and the user's yes. A day with replies and nothing due: the
replies block only. Fields: on top, each interested reply, their words, a proposed answer
(the linkedin-messages skill, Replies); then one block per batch due that day (which follow-up, its
date = the batch's send date plus the template's day, 2 real examples, only the rows that need a yes/no),
the stopped people and their held colleagues as one grey count. Flags: as Message checks. Nothing is shown before the template's day.

## Results (step 5, and whenever a rate is asked)
```
Résultats                                   lecture 12 nov
[red Promoteurs : 0 réponse sur 9]
■ intéressés  □ non
Syndics        le guide            ████ 5/12, 4 intéressés   l'exemple chiffré ██ 2/11, 1 intéressé  [direction]
Promoteurs     une seule version   0/9                                              [base seule]
Acceptées à 7 jours   Syndics ███ 34/90   Promoteurs ██ 8/32   avant ███ 30 %
Réponses dans les 7 jours ; 3 de plus sont venues après, comptées la prochaine fois (grey)
Leurs mots : « le prix des travaux » 3 · « après le vote » 2
Vous validez : Syndics, on garde le guide · Promoteurs : [changement ou pause]
```
Fields: per persona, the bars (answered out of first messages, the interested part darker, the no part
labelled, each side named by what it carries); its verdict chip; amber `modifié par vous : N` per side
when drafts were edited; acceptance within 7 days per persona against the saved baseline. A note test: two
bar pairs, accepted out of invited and answered out of invited. Signal
leads count inside their side, and once more on one grey line with their own rate. The user's past rate:
one grey line with its n ("vos messages avant, choisis : 4/6, pas comparables"), never a bar; amber `le
modèle perd votre force` only when that past set holds 10 or more messages to strangers, the gap is over
the noise band, counted on interested answers; it points to the next angle, never back to a slot the
chips refuse. Their words from the replies, N each
(Persona cards v2 copies them). The legend is two swatches with words, each bar says "N intéressés" in
full. One decision line, one row per persona, each with "pas celle-ci". Verdicts: the four words of
`references/measuring.md`. No p-value, no noise wording, no week before the first send.

## Next test (step 6)
```
Prochain test · Syndics
| Le guide         | L'exemple chiffré     |
| bubble           | bubble, change marked |
170 invitations · ~60 premiers messages de chaque côté · lecture 17 nov
Inchangé : la note gardée, mêmes relances (grey)
Pourquoi ce test : deux réponses demandaient un exemple chiffré (grey)       > les autres pistes (folded)
Vous validez : on teste l'exemple chiffré contre le guide, rien d'autre
```
Fields: last verdict chip; both messages with the Message checks (the framework whole, amber `long` over about 500); invited
and expected first messages per side against the size the change needs; one grey line of what stays the
same (a note kept on direction stays); one grey line why this test; read date. When the change is WHO is
invited: before chip, after chip, expected count, and the message once. A persona without halves: titled
`nouvelle période, pas un test`, every difference against the earlier period listed, its messages checked
like any other. A new search is
its own Plan and personas page. No note lever for an account that cannot add notes. Flags: red `contredit les réponses` (keeps a premise replies refuted) · amber `petit
changement` (same pain reworded) · amber `trop petit pour se voir` (`references/measuring.md`) · amber `mois chargés` (the read window falls in the card's busy months) · amber `mot changé` (a
draft's fixed words differ from the saved template) · amber `deux changements` · amber `même idée que la note
ou la relance 1`.

## App links (one line in the footer)
At most one link per page, after any search credits, with one line saying what opens. Only a link a tool
returned or one in this table; never a list address built by hand. A `fixUrl` that starts with `/` gets
`https://chat.bereach.ai` in front (the sign-in challenge link is already whole). The same link is also
given in chat, one line, when the step it belongs to is done.

| Page | Link | Line |
|---|---|---|
| Plan and personas, after the searches | the `list_url` `bereach_run_searches` returned; none: https://chat.bereach.ai/search | Votre liste, avec les personnes trouvées |
| Plan and personas, no search ran | https://chat.bereach.ai/contacts | Tous vos contacts |
| Invitations to send, Results | https://chat.bereach.ai/connections | Vos invitations, envoyées et acceptées |
| Drafts for review | https://chat.bereach.ai/drafts | Lire, modifier ou approuver vos premiers messages |
| Drafts for review, after a reasons-to-write run | the `list_url` `bereach_add_signals` returned | La raison d'écrire de chacun est sur la liste |
| After a fit check the user asked for | the `list_url` `bereach_check_fit` returned | Triez ou filtrez par adéquation |
| Any page, while a tool says no account is connected or it signed out | https://chat.bereach.ai/connect/linkedin | Connecter votre compte |
| Any page, credits run out or a plan is needed | https://chat.bereach.ai/settings#billing | Votre abonnement |
