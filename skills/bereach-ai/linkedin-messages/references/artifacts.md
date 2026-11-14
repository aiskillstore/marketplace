# The artifacts of this skill

Three pages, the first a block of Voice and messages, in order: **Message templates** (Step 2),
**Drafts for review** (Step 4, each batch of accepts), **Follow-ups to send** (the day they are due). Names and FR/EN labels as in the
linkedin-outreach-method skill's artifacts.

Every page: a title, the problem chips first (red holds the message, amber: Claude goes on), ONE visual,
at most one short line per block, then one line **"Vous validez : ..."** / **"Your call: ..."** with one decision.
Language of the page follows the user; the leads' words stay as written. What Claude already fixed is a
green chip (at most 3, then "+n"), never red. All checks held: one green `contrôles OK`, nothing else.
Any part upgraded from the user's own message: their message folded as "avant" beside the version, one
line per changed part with its principle in plain words. The decision is to validate the upgraded
version (the user may change words); never a "garder tel quel" choice, never a choice framed by cost.
Never on a page: a tool or tag name, a vendor, how a person was found, where a fact came from, a credit or a balance,
an internal word ("fallback", "strike", "brief"). Chips are problems only, in the user's language, saying
what happens ("3 sans fait récent : phrase générale", names behind it). The footer holds only the app link.
Under each draft or template, its line `Cadre : <framework>, <why for this persona and this type>`, in
the user's language, only when the message visibly applies it; otherwise no line and no name. The user's own messages are their voice, never named as a framework.

## The chips (the same on every page)

Red, holds the message:
- `inventé` (a fact, date, tense, proof, figure, quote or claim no source shows; a guess in quotes; a
  proof not in the user's words; a "votre X" the lead never said; a reply stating a product, price or
  work fact the user never gave; an offer the user never made)
- `fait périmé` (over 6 months, or older than the card's window)
- `mauvaise personne` (Who is who unsure, already talking to the user, a customer or a past client)
- `tu/vous` (address form or greeting casing not as the Voice card says)
- `données d'un tiers` (the offer needs their clients' data)
- `note > 200 car.` · `blanc dans la note`

Amber, Claude fixes first:
- `pas sur eux` (opens on the sender or the sender's clients, a title or headline recited, a thanks or
  praise that says nothing about them, a lesson on their own job)
- `pas de raison` (the fact is not tied to why the user writes)
- `qui écrit ?` (no name or trade in the who-writes part)
- `offre floue` (a wish, a call, an offer outside the user's trade, two questions, an object not named in words)
- `relance sans neuf` (a follow-up that brings nothing new)
- `illisible` (a verbless opener, a colon joining clauses, a statement that turns into a question, a
  run-on, a sentence read twice)
- `cadre tassé` (the framework does not fit the size and its parts were shrunk instead of dropped)
- `long` (over about 500 characters)
- `persona incertain` (two cards fit or the company does not: row CHECK, nothing sent)
- `ouverture répétée` (3 or more drafts in a batch open the same way, or a first message opens on its note's fact or moment line)

No chip that nothing can clear: a chip shows only what Claude or the user can fix on this page.

## 1. Message templates (Modèles de messages)

When: the second block of Voice and messages, after the invitations go, before any draft.

```
Modèles de messages
[vos messages : 2 vraies réponses sur 20, piste, pas preuve]   [contrôles OK]
+ SYNDICS ----------------------------------------------+
| [aucune note] [l'offre] [relances J+4, J+10]          |
| (bubble) Bonjour {Prénom}, [fait], qui écrit + métier, offre [objet] ? |
| Cadre : Premise first et offre donnée, ...            |
| > Avant / après : votre message, chaque partie changée et pourquoi (folded) |
| > Relances (folded)                                   |
+-------------------------------------------------------+
+ L'offre : la liste des 5 postes, celle de votre message qui a eu des réponses
Vous validez : votre voix, ces messages et le type d'offre (fait et objet changent par personne)
```

Fields per persona: persona name; what each message does as one chip (note: none or premise note; first:
the offer; follow-up 1: "votre preuve" or "une question"; follow-up 2: offer + way out) and the day of
each follow-up; the first message with its two per-lead slots highlighted (the fact, the offer's object
framed by it); its `Cadre` line; the yes covers the kind of offer, never a lead's object words; the
moment line; a count of the user's past replies is engaged answers only,
labelled "piste, pas preuve"; follow-ups folded, each ending on its question. A second language only if
this persona's leads read it, same offer and ask. No offer yet (SKILL.md, The offer): one question to the user on top, and
the messages end on their proven ask meanwhile. A voice change lists only
the templates that really contain the changed text.

Example (Atelier Nord, energy audits of buildings, vous):
> **Syndics** · aucune note · l'offre
> Bonjour {Prénom}, [le vote des travaux en assemblée, c'est souvent le moment où un poste de charges
> surprend tout le monde, faute d'avoir été chiffré avant.]
> Je suis Léa et j'audite ces immeubles avant le vote, pour que le syndic arrive avec des chiffres.
> Voulez-vous que je vous envoie [la liste des 5 postes qui pèsent le plus sur les charges] ?
> *Cadre : Premise first et offre donnée, parce qu'un syndic répond à un moment qu'il reconnaît et garde la liste.*

## 2. Drafts for review (Brouillons à relire)

When: Step 4, with the list name, again for each batch of accepts (the footer link opens the drafts).

Every batch: 3 real messages rendered as the prospect gets them (filled, never a placeholder), the READY
count with the PRÊT rows folded (tap to open), then ONLY the rows that need a decision, each with why.

```
Brouillons à relire : Syndics Lyon, lot 2
[1 à vérifier] [1 vous a écrit]
( 3 bubbles: Camille F., Hugo B., Inès T., fact and offer's object highlighted, date shown )
À trancher : Nadia K. À VÉRIFIER · Léo P. EN ATTENTE
> 4 PRÊT (folded)
Vous validez : les 4 PRÊT partent
(footer) Vos brouillons : https://chat.bereach.ai/drafts
```
After the yes: each edit the user made to a row of this page, listed under it ("modifié par vous : 2").

Fields per row: status (with the reason for all but PRÊT); name and company; the fact with its date; why
it matters to the sender; the draft with the fact and the offer's object highlighted; its `Cadre` line;
open chips; fixed chips in green.

Statuses (EN in the outreach labels table):
- PRÊT: no open red chip, the offer one the user made. Whatever Claude could fix itself is PRÊT.
- À CORRIGER: only a fact only the user knows is missing: one yes/no question to the user ("avez-vous
  rénové dans cet immeuble ?") and both versions ready; or the brief contradicts the fact Who is who used
  (both dates shown).
- À VÉRIFIER: two cards fit, or the company does not; nothing sent until the user answers.
- EN ATTENTE: a customer, a past client (a company in a card's Proof), or a contacts offer that cannot be
  produced now. Already talking or they wrote first: their last message and a proposed reply in the voice,
  stating only what the card, the offer or the user said, else a question to the user (EN "already talking to you:
  answer yourself").

Example (same seller, list "Syndics Lyon"):
> **PRÊT** Camille F. · Régie Exemple · `corrigé : illisible`
> Fait (30 sept) : a publié sur un vote de travaux reporté · Pourquoi pour moi : j'audite ces immeubles
> Bonjour Camille, [j'ai lu votre post sur le vote de travaux reporté.] Reporter un vote, c'est souvent voir
> les charges monter sans savoir quel poste pèse le plus.
> Je suis Léa et j'audite ces immeubles avant le vote, pour que chacun sache ce qu'il paiera.
> Voulez-vous que je vous envoie [les 5 postes à chiffrer avant de remettre ce vote à l'ordre du jour] ?
> **À VÉRIFIER** Nadia K. · "Responsable technique et achats" · `persona incertain` (deux fiches)

## 3. Follow-ups to send (Relances à envoyer)

When: each day something is due, ONE page for every batch due that day; no follow-up or reply goes
without it. Wireframe: linkedin-outreach-method artifacts. On top, "Réponses à traiter": each interested
reply, their words, a proposed answer (`references/follow-ups.md`). Then per batch: which follow-up and its
date, 2 real examples as sent, each with its `Cadre` line, ONLY the rows that need a yes/no, the stopped
people as a grey count. Each message ends on one easy yes/no question. Decision: "Vous validez : ces N
réponses et ces N relances partent aujourd'hui".
