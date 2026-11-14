# Artifacts of the linkedin-voice skill

One block: the **Voice card**, first on Voice and messages (linkedin-outreach-method). Visual,
very little text: a title, problems first as red or amber chips, ONE visual (avant / après bubbles with the
principle per change, one chip per slot, the test bubble), one last line, the decision (Fields). Language
follows the user. No tool or tag name, no vendor, no em or en dash. Never an invented person or fact on this card: the test
message goes to a real lead (an invented example lives only inside this skill, never on a page shown to the user).

Chips: red = fix before saving, amber = to confirm, green = checked, grey = set aside or information.
Green only on a slot that passes the type's framework (SKILL Step 2b); a failing slot never shows green and
never reads as "kept as is": it shows its gap, and the upgrade sits in "après".

## Voice card

**When**: Step 3, again after each correction, and when the first Results promote it (provisional to confirmed: answers that engage, copied from Results, the reference
named; the only page that chooses the reference).
**Name**: `Carte de voix : <label>, <langue>` / `Voice card: <label>, <language>`.

```
Carte de voix : Premier message, FR                  [brouillon]
! red / amber chips
Avant (their message, greyed) | Après (the upgraded reference)
- one line per change: what changed : the principle, in plain words
Slots: [ouvre sur eux ✓] [qui écrit, avec le métier ✓] [un fait relié ✓] [votre offre ou une question ✓]
Votre voix : [vous] [Bonjour Prénom,] [Belle journée,]     Phrases à vous : [chip]     Jamais : [chip]
> vos 4 messages (folded)
Message test (bubble) + only the broken checks
Vous validez : votre voix et ces messages mis à niveau
```

**Fields**
- Band under the title, in the user's language: only frameworks from `references/frameworks.md` read in this session and visibly applied; none read, no band.
- Header: label, language, "sur N de vos messages (M réponses engagées : une piste, pas une preuve)",
  state. Engaged = a question, a yes, a conversation; politeness ("avec plaisir", an emoji) is not
  counted. Never "3 sur 3" or "ça marche" from these counts.
- Reference message: the user's best hand-written message after the expert upgrade, as "après"; their
  original, verbatim and greyed, as "avant" beside it whenever a slot was upgraded, one chip per gap under it
  in plain words, never a grade or a score; no slot failed: one bubble, "votre message passe tel quel". The
  samples stay folded, never repeated in full.
- Changes: one line per upgraded slot, "<ce qui change> : <le principe>" (e.g. "remerciement retiré : la
  raison dès la première phrase"; "métier ajouté : on sait qui écrit"; "souhait remplacé par une question
  sur son fait : un non facile").
- Slot chips (opening, who writes, fact and tie, offer or question): green only when the slot passes in
  "après" (SKILL Step 2b). An offer is green only when the user already made it or a prospect asked for it;
  else the slot is one plain question on their fact. Voice chips: address form, greeting, sign-off.
- Phrases à vous / Jamais: two short chip rows.
- Folded: their messages (to whom, got a reply), tone per message type. No word counts.
- Test message: one real person read off their list with `bereach_contacts` in a sure persona (list
  unreadable or none yet: a person the user names; until then the card waits, never invents one) the
  user has never written to (no sample recipient, no thread in `bereach_inbox` or the brief; that person gets a
  reply or follow-up briefed with `maxAgeDays` left at its default (the conversation is read anew), no reply text before that brief has returned their last
  message, and the "après" is never a draft for them), one new real fact
  from their full brief (never the reference's) tied to the user's work, who writes with the trade noun, the offer or interest
  question, the framework whole in full sentences, their identity fields; their voice, never a failing slot.
  After an invitation note, its first line never repeats the note's line (the moment line included): with no
  new fact, it opens on another reason. Only the version
  Claude proposes: the bubble, the person and persona; checks shown only when broken. "Votre version" only
  when the user changed a word; otherwise "validé tel quel".
- The decision, the only one: "Vous validez : votre voix et ces messages mis à niveau (corrigez un mot si
  besoin)." / "Your call: ..."; never a button that keeps a failing version.
- Nothing answered yet: the test bubble, three form chips marked `à confirmer`, the decision. Nothing else.
- Every chip says what it means in plain words.

**Flags**
- grey `mis de côté : pas confirmé par vous` · grey `mis de côté : écrit par un outil`
- red `tu/vous`; `langue`: Claude fixes.
- amber `voix enregistrée : mise à niveau`: a saved voice had a slot upgraded.
- Gaps on "avant" (grey: fixed in "après"): `remerciement sans contenu` · `rien sur eux` · `commence par
  vous` · `métier absent` · `fait sans lien` · `souhait vague` · `demande un rendez-vous` · `trop long` ·
  `titre recopié` · `pas de question` · `offre floue` · `parle de vous`.
- amber `à confirmer`: a habit seen once, or read from unanswered messages; green only once an answered
  message shows it.
- Test message: Claude fixes before showing (title recited, fact with no tie, stale fact, telegraphic, a
  meeting ask, a hedge, no tie to your work, an offer never made, a `[ ]`, `illisible`, `cadre tassé`), amber `long` (over about 500, linkedin-messages Size); red `pas ce persona` ·
  amber `persona incertain`.

**Example** (draft, French, invented: a seller of energy audits)

```
Carte de voix : Premier message, FR                      [brouillon]
Sur 4 de vos messages (2 réponses engagées : une piste, pas une preuve).

Avant : "Bonjour Claire, merci d'avoir accepté ma connexion ! Votre copropriété vote ses travaux en
  mars. J'espère que nous aurons l'occasion d'échanger."
  [remerciement sans contenu] [métier absent] [souhait vague]
Après : "Bonjour Claire, votre copropriété vote ses travaux en mars, c'est donc maintenant que le budget
  se joue. Je fais des audits énergétiques pour ce type d'immeuble. L'audit fait-il partie du vote ?"
- remerciement retiré : la raison dès la première phrase
- "c'est donc maintenant que le budget se joue" ajouté : pourquoi ce fait compte pour elle
- "je fais des audits énergétiques" ajouté : on sait qui écrit et pourquoi à elle
- souhait remplacé par une question sur son fait : un non facile (pas encore d'offre : on vous en demande une)
[ouvre sur elle ✓] [qui écrit ✓] [fait relié ✓] [une question ✓]
Votre voix : [vous] [Bonjour Prénom,] [sans signature]     Jamais : [solution] [rendez-vous]

Message test : Julie Marchand, lue sur la liste Syndics, Syndics
 "Bonjour Julie, vous reprenez la gestion de trois copropriétés à Lyon ce mois-ci, et chacune hérite d'un
  plan de travaux à revoir. Je fais des audits énergétiques pour ce type d'immeuble. Ces plans prévoient-ils
  déjà un audit ?"

Vous validez : votre voix et ces messages mis à niveau
```

## Promote and change

- **Promote it** after the first Results, by one rule: per persona, answers that engage (a question, a
  yes, a conversation; never a plain no, never politeness such as "avec plaisir" or an emoji) out of first
  messages sent in this voice, copied from Results (in a note test the first message is the same on both
  sides: both count). Among messages that pass every SKILL Step 2b slot, and only once an arm is past
  measuring.md's `trop tôt` threshold (linkedin-outreach-method), the reference is the one with the most
  such answers, as it now reads with the user's applied edits (an approved template counts). Below it: a
  direction, the reference unchanged. `provisoire` goes, one Overview line says so. A rule the bereach-setup skill moves here from the
  user's own saved rules is their statement: it lands confirmed, one line on the next page, no republish.
- **A change**: the same edit made twice by the user is offered on the next Drafts for review; on the yes
  it applies to the drafts still to come in both halves (a wording of the voice is not a test variable),
  and the page lists every template, follow-up and offer still carrying that word or its family.
  On wording it wins over a linkedin-messages default, which then shows as an amber chip, never a silent
  override. An edit that makes a Step 2b slot fail (the thank-you back, the trade removed, the offer
  turned into a wish) shows that slot red with its principle and a passing wording, never kept silently.
