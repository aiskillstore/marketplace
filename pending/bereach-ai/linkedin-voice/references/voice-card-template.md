# Voice card template

Fill every field from the samples, counted where it can be (I/we/you share, ! and ?, sentence length).
Each value needs its proof (a quoted fragment); no proof, the field stays empty.

## Artifact layout (the page)

The page is the Voice card in `artifacts.md`: wireframe, fields, flags, one example.

## The data to fill (not the page)

```
VOICE CARD: <name>, <language>
Validated by the user on: <date>

LAYOUT: <one block | short lines with blank lines between>

GREETING
  Greets: <yes/no>   Exact form: "<...>"            proof: "<fragment>"

SIGN-OFF
  Signs: <yes/no>    Exact form: "<...>"            proof: "<fragment>"

ADDRESS FORM
  <tu | vous | none> (switch to the prospect's form once they answer)

PUNCTUATION AND FORMALITY
  Exclamation marks: <never | rare | often>
  Ends on a question: <usually | sometimes | never>
  Emoji: <never | ...>
  Contractions: <yes/no>
  Name used: <first name | full name | none>
  Pronoun habit: <I | we | you-first>, counted: <I n, we n, you n>   proof: "<fragment>"
  Sentence length: <words per sentence, counted>

SIGNATURE PHRASES (verbatim, at most one per message; SKILL Step 2)
  - "<...>"
  - "<...>"

NEVER
  - <word or move they never use>
  - <...>

TONE PER MESSAGE TYPE (types the samples show or the user described, else empty)
  Invitation note: <...>
  First message:   <...>
  Follow-up:       <...>
  Reply:           <...>

SAMPLES (3 to 5, varied: the originals verbatim, for identity only; the playbook's `samples` hold the
upgraded versions the user validated, SKILL Step 4)
  1. <...>
  2. <...>
  3. <...>
```

## Mapping to the BeReach playbook

| Card | Playbook field |
|---|---|
| Language | `language` |
| Address form | `addressForm` (`tu`, `vous` or `none`) |
| Tone per message type | `tone` |
| Greeting, sign-off, punctuation, formality, signature phrases | `guidelines` |
| Never list (the user's own words) | `hardRules` |
| Samples | `samples` (one message per item, the 3 to 5 upgraded versions the user validated, plus the test message) |
