# What got replies: learn from what the user already has

Done once, before the persona cards. Its output feeds three skills, so nobody reads the same conversations
twice: linkedin-personas (pains, objections, their words), linkedin-voice (voice samples, every slot judged),
linkedin-messages (angles, the prospects' words and what they asked to receive; never a template to keep).

## 1. Ask for what exists (inside the one question round)

"Do you have a message playbook, templates you send, a sales deck, persona notes, or numbers from past
campaigns (what got accepted or answered)? Paste or attach them. And may I read your recent LinkedIn
conversations to see which of your messages got answers?"

- Also read what BeReach already keeps: `bereach_memory_list` once per type (`offering`, `playbook`,
  `user-profile`), then `fullContent: true` with the type and the entry's `scope` for each one you use (it
  reads one entry in full). None saved for a type: say so. A saved playbook or persona section is the starting
  point, not a blank page.
- Nothing exists: say so in one line on the artifact and go on. Never invent a past result.

## 2. Read the conversations (only with their yes)

1. `bereach_inbox` (free). Keep one-to-one conversations (`groupChat` false) about work, not personal ones.
2. Pick up to 20 where the user wrote first to someone they were prospecting: about half where the other
   side answered, half where nobody did. `lastMessage.senderProfileUrn` tells who spoke last.
3. Nobody answered any of them (the inbox shows who spoke last): stop here; read the
   openers from the inbox list only, for what to avoid.
4. Otherwise `bereach_brief` on each, every part on (no `include`), `historyVerbatim` 200: the whole
   conversation word for word, and who the person is to read why they answered.
5. Use only messages that came back word for word. Never quote a summary as if they wrote it.

## 3. Read each opener the same way

For the user's first message in each conversation, note:

| Column | Values |
|---|---|
| Written by | the user by hand / a tool (unsure: grey chip `écrit par vous ?`, kept unless the user says no; only hand-written ones count as theirs) |
| Opened on | a fact about them with a reason / their title or company recited / a pitch about us / a question / a tie (event, shared connection) |
| Length | characters |
| Ask | none / interest / offer / permission / meeting |
| Answered | interested (a question, a yes, a request, a conversation) / politeness (a thanks, an emoji, "au plaisir") / no / none, and how many days later |
| Their words | pain, objection or exact phrase from the answer, quoted; what they asked to receive (it feeds the offer) |

Count, never conclude: a count is a hint for the slot judgment ("4 of 6 openers on a fact got an interested
answer"), never "this works because" (`measuring.md`, Past messages).

## 4. What got replies, folded on Voice and messages

- One bar chart: answered / sent, the interested part darker and politeness apart, split first by who wrote
  it (the user by hand, a tool), then by opener and ask.
- Three short lists: **Keep**, **Drop**, **Their words**: N is the answers saying the same thing in
  meaning, each wording quoted verbatim beside it ("combien coûtent les travaux", "le prix des travaux": 2).
- Every bar is recounted from the table rows before publishing; a row with two traits counts in both.
- The conversations table folded. The header says how many were read.
- One grey chip on top, `piste, pas preuve`, whatever the count. It never overrides a measured test nor
  keeps a slot that fails the expert shape (SKILL step 4).
- After Results, their words from the new replies sit on Results and feed Persona cards v2. Keep and Drop
  name only traits that differ between interested and unanswered messages; Keep is a hint, never a slot kept
  against the shape; a wording the user edited is never a lesson here.
- No answered message at all: no band; one line on Voice and messages with what to
  avoid, and the persona questions carry the Pain and Objection lines.
- A tool-written message or saved rule that recites the profile is noted for What Claude knows, after the
  first invitations; it never becomes a sample.

The user corrects it ("that one was a friend", "I did not write that one"). Then:
- Their words go on the persona cards as `Seen in N replies`, N counted as above; under 2 the line ends in
  `(guess)`.
- Answered messages the user confirms writing become the voice card's samples: their voice is kept, every
  slot of their craft (opening line, fact and tie, who writes with the trade, ask, ending, length) is judged
  and the failing ones upgraded (linkedin-outreach-method step 4). Their clause and their ask keep their words
  only where they pass.
