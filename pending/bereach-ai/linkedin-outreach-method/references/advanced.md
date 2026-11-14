# Advanced options (optional)

Only after a text template per persona is validated and measured. Each one is a test: half of one persona,
the other half on the text baseline, sent the same days, read at 7 days (SKILL.md step 7). The user decides
whether to try any of them; none is needed to do well.

| Option | What it is | Evidence | Who does what |
|---|---|---|---|
| Voice note | A 20 to 40 second recording in place of follow-up 1 | One randomized vendor test, one segment: replies 30.7% to 33.7%, meetings 4.1% to 5.0%; did worse in a German-speaking audience. The bigger claims online (25 to 40% against 5 to 15%) trace to nothing solid | Claude writes the script; the user records and sends it from their phone |
| Cloned voice | A voice note made by software from a sample of the user's voice | None found. Vendor claims only | Only with the user's own voice and their choice; same test as a voice note |
| Image or short video | A picture or video made for the person (their site, their name) | None found on LinkedIn. In email data, images had no meaningful effect | The user makes and sends it |

## A voice note script (Claude writes it, the user says it)

1. Their name and the personal line (one fact and why it made you write).
2. One line of value: their problem in their words, or one proof.
3. One easy ask, the same kind as the first message.

About 60 to 90 words. Written to be said: short sentences, no list, no number they must remember. Best for a
warm, informal persona at a small company; never as the first touch.

## Counting a test the tools do not send

These go out from the user's own phone or app, so BeReach does not see them as messages. Before sending, tag
the two halves (`bereach_contact_update`, `tags: { add: ["arm:<persona>:voice"] }` and `arm:<persona>:text`).
At 7 days, count answers per tag as in SKILL.md step 6, read with the verdicts of `measuring.md`.
