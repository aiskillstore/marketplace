# The artifacts of the cold email skill

Six pages, one per Deliver in `SKILL.md`, named as there.

## Every page

- A title, one line under it (list, date), the flags as chips, ONE visual, then one line
  "Vous validez : ..." / "Your call: ..." with the one decision ("Je continue : ..." on the Sending check). At most one short line per block.
- Problems first: red chip = blocks the row, amber = the user looks, grey = info. Flagged rows on top.
- The user's language. No tool, tag or field name, no vendor, never "data from LinkedIn". No lead photo.
- Numbers only from a tool reply or the user; a cost before spending reads "jusqu'à N crédits".
- Leads as first name and last initial; no em or en dash; a chip only for a problem, never a zero count.
  Long lists fold ("+12 autres, tous ok").
- A band under the title, in the user's language, `Étape N · Framework (Auteur)`, naming the framework or rule from `frameworks.md` that shaped the page.
- A page that shows an email the user wrote shows "avant / après" when any part was upgraded, the principle
  applied named per change in plain words; the upgraded email is the version to validate (the user may
  correct words). Never "garder tel quel" as an option, never a green chip on a part that fails.
- Examples (invented): Atelier Nord sells energy audits of buildings, in French, with "vous".

## 1. Sending check (Step 1)

```
Vérification d'envoi                      Léa, 29 oct.
[1 à corriger] [1 à regarder]
Boîte       lea@ateliernord.fr     ok
DMARC       non publié             à regarder
Par jour    120 prévus             à corriger
Je continue : cette boîte, 30 par jour, suivi coupé.
```

Fields: mailbox, SPF, DKIM, DMARC, emails a day, countries, tracking; each with what was found and a short fix.
Flags: red `webmail gratuit`, red `plus de 50 par jour`, red `SPF/DKIM absent`, red `suivi activé`,
amber `DMARC absent`, amber `inconnu`, amber `Allemagne : avis juridique`, amber `{pays} : règle à vérifier`.
Decision: the mailbox, the daily volume, tracking off.

## 2. Who is who (Step 2)

```
Qui est qui : Syndics Lyon                29 oct.
[19 prêts] [1 à vérifier] [2 en attente] [1 ne plus contacter, retiré]
-- Syndic qui reprend un immeuble --
Hugo B.   Régie Fictia   reprend 3 immeubles   prêt
Sarah M.  Orvia          syndic ou gérant ?    à vérifier
> 2 en attente, aucun e-mail
Coût : jusqu'à 19 crédits e-mail ; +1 si Sarah est validée
Vous validez : ces 19 personnes et ce coût.
```

Fields per person, grouped by persona: name, company, why this persona, why now (fact and date, or none),
status. Waiting people fold at the bottom with their reason. Do-not-contact: one grey count only.
Flags: amber `à vérifier` with its question, grey `en attente` (student, side project, own profile,
colleague, out of scope, third at one company, Germany), red `crédits insuffisants`.
Cost for READY people only, plus the reasons-to-write ceiling for the whole list, "+N si validés" for CHECK people. Footer: Vos contacts : https://chat.bereach.ai/contacts.
Decision: these people and this cost.

## 3. Message templates (Step 3, one page per persona)

```
Modèles d'e-mail : Syndic qui reprend un immeuble    [défaut] [FR = EN]
 Jour 1        Jour 4         Jour 8         Jour 14
 objet, corps  réponse fil    nouvel angle   "on s'arrête là ?"
 72 mots       31 mots        44 mots        22 mots
Exemple pour Hugo B. : [ligne perso surlignée] + pied de page
Replis : ligne 1 / ligne 2
Vous validez : ce modèle, les replis et l'exemple.
```

Fields per card: day, subject, body with the personal line highlighted, word count, the yes/no question.
Under it: email 1 filled for one real person, footer once, 2 or 3 moment lines, the fact's source and date.
Flags: red `offre hors métier`, red `deuxième offre`, red `demande un appel`, red `pas de question`,
red `ouvre sur nous`, red `remerciement sans contenu`, red `métier absent`, red `souhait vague`,
red `chiffre non prouvé`, red `écart FR/EN`, red `> 90 mots`, amber `< 50 mots`,
amber `un seul repli`, amber `pas de sortie` on the last email.
Decision: the template, the moment lines and the example, together.

Example email 1 (about 65 words, footer not counted): "Bonjour Hugo, <mark>vous reprenez les Tilleuls ce mois-ci ;
la première facture de chauffage d'un immeuble repris surprend souvent, car les réglages de l'ancien syndic
restent en place.</mark> Je suis Léa, d'Atelier Nord : j'audite l'énergie des immeubles en copropriété. Trois
postes expliquent souvent l'écart, et ils se vérifient en une visite. Je vous envoie la liste des
trois postes à vérifier aux Tilleuls ?
Léa Martin, Atelier Nord. Je vous écris pour votre travail ; adresse pro trouvée avec un outil de recherche.
Pas pertinent ? Répondez « non » et je ne vous écrirai plus."

## 4. Drafts for review (Step 5)

```
Brouillons à relire : Syndics Lyon, 29 oct.
[3 à corriger] [2 à regarder]
( 3 e-mails réels, comme Hugo B., Marc D., Inès T. les reçoivent )
À trancher : the rows that need a decision, red first
Inès T.    repli 2               (profil lu, rien)       ~~ancienne ligne~~ ...     corrigé : profil récité
> 13 prêts (repliés)
Vous validez : 16 prêts, 2 retirés.
(footer) 15 crédits e-mail
```

Always 3 real emails rendered, then only the rows needing a decision; never dozens of identical rows.
Fields: person, email status, fact with date (or the moment line used), why it made the user write,
subject, the whole email 1 (personal line highlighted), words, language, flags. A fixed row keeps the old
line struck through with a grey `corrigé : {défaut}`.
Flags: red `profil récité`, `fait sans lien`, `date périmée` (over 6 months, or outside the card's window),
`temps du verbe` (tense against the date), `inventé`, `> 240 car.` (personal line),
`langue` (wrong tu/vous, lowercase "bonjour" with vous), `e-mail non vérifié`, and every red flag of the templates page;
amber `hésitation`, `ouverture répétée` (3 or more drafts sharing their first 5 words or shape), `sans fiche`, `même société`;
grey `hors ICP` / `pas ce persona` (on hold, no email), `aucune adresse, 0 crédit`, `profil lu, rien d'utile`.
Decision: which drafts go, which are removed.

## 5. Ready to send (Step 6)

```
Prêt à envoyer : Syndics Lyon          16 personnes   [CSV]
Hugo B.   Syndic   2026-11-02   relances 11-05, 11-09, 11-16
Marc D.   Syndic   2026-11-09   (même société : semaine 2)
[À : hugo@fictia.example  Copier] [Objet] [Corps + pied de page  Copier]
> Relances (repliées, chacune avec sa ligne de désinscription)
Vous validez : je marque ces 16 personnes comme envoyées par e-mail.
```

Fields: who gets what and when, then one copy block per person (To, Subject, Body, footer on email 1,
follow-ups with their date), and a CSV with the same content. Verified emails only.
Flags: red `pied de page manquant`, red `pied de page sur une relance` (not US), red `lien dans l'e-mail 1`,
amber `envoi un week-end`.
Decision: mark these people as emailed today.

## 6. Results (Step 7)

```
Résultats : Syndics Lyon            chiffres de votre boîte
[rebonds 3,1 %, lot du 1 oct.]
Syndic qui reprend   12 envoyés   ████ 3 réponses   2 positives
Gérant seul           7 envoyés   (moins de 10 : pas de taux)
Lot du 29 oct.       en cours jusqu'au 12 nov.
Prochain test : objet A contre objet B, envoi 9 nov., lisible 30 nov.
Vous validez : le prochain lot ne change que l'objet.
```

Fields per persona and batch: sent, replies, positive, opt-outs, bounces, all from the user's own counts;
positive = a question, a yes or a conversation, never politeness; a verdict in plain words: `trop tôt` or
`direction`.
No p-value, no noise wording.
Flags: red `rebonds > 2 %`, red `plainte spam`, red `chiffre pas de vous`, amber `désinscriptions en hausse`,
amber `deux changements`, grey `en cours`, grey `moins de 10 envoyés`, grey `avant la méthode` (the user's
past emails, one line).
Under the page: the next test in one line.
Decision: the one thing the next batch changes.
