---
name: study-first
description: Load BEFORE answering any message that asks for more than a single fact, and whenever answering means reading something (a document, PDF, chat transcript, web page, code, screenshot, task status, ad campaign). It makes the agent break down EVERYTHING the user asked (including messy dictated voice messages and "scratch that" corrections), read the sources IN FULL (not the title, not the first lines, not the "succeeded" label), cross-check with a second source, and answer point by point with evidence, never writing a detail it did not actually see. Triggers on "study this", "look into it properly", "read it carefully", "analyze", "investigate", "what does it say", "how is it going", "did it work", long or dictated messages, and in Spanish "estudia", "revisa a fondo", "a profundidad", "léelo bien", "analiza", "cómo vas", "qué pasó con", "funcionó".
license: MIT
---

# Study first, then answer

Most agent mistakes share one root: **the agent skimmed and then answered as if it had studied.** Real cases this skill was built from:

- A scheduled task was reported fine because the app said "succeeded". All 6 runs had died on a permission prompt.
- An account was said to belong to the agency because a link redirected there.
- A data format was changed without searching for its readers, and another part of the code broke.
- A file number was taken from memory instead of from the folder, and an existing file was overwritten.

This skill puts the study before the answer. It cannot promise zero mistakes. It does make sure no answer rests on something nobody read.

## 0. Size it (5 seconds)

- **A single fact** from one source (a time, a number, a yes/no): read it at the source and answer. Skip the rest.
- **Anything else**: steps 1-5. The more a mistake costs (a client, money, publishing, deleting), the deeper you go.

## 1. Break down what the user said (before opening anything)

Write, for yourself, the **list of asks**: every question, every instruction, every condition, and anything that clearly bothers them.

- Use their exact words for names, numbers, dates, prices and clients.
- People dictate and type fast. Read what they meant ("Hit" may be "GitHub", "OCMO VAS" is "cómo vas").
- If they change their mind ("scratch that", "no, better..."), the **last** version counts.
- A long message usually carries 3 to 6 asks. If you found only one, read it again.
- Unspoken asks count too. "How is it going?" means the live state right now, not the last report.
- If a missing fact really changes the answer, ask ONE question with options. Otherwise do not ask.

## 2. Map the sources

For each ask, note where its answer comes from:
- the document, file or chat the user named;
- what was already decided: project notes, error logs, the client file, memory;
- the live state: the page, the API, the task run, the campaign.

No ask is answered from memory or from an old summary.

## 3. Read IN FULL what matters

- **Documents and chats**: start to end. Long ones go in parts, all the way. When you look for one topic, find every occurrence and read each in context. Note how much you read ("read all 12 pages", "the 3 places X appears").
- **A status is not the reality.** "Done", "succeeded", "active" or a green check are labels. Open what happened inside: the log, the last action, the result.
- **A name does not tell you what something is.** A file name, an ad title, a redirect or a column header proves nothing about the content. Open the content.
- **Code and formats**: before changing anything, find EVERY place that reads or uses it.
- **Screenshots and images**: look closely at the area that matters, not at a thumbnail.
- Anything you could not open is noted as "not read", with the reason.

## 4. Cross-check before concluding

- Every important conclusion needs **two signals that agree**, for example the task status and its log, or what a chat says and the file it delivered.
- If two sources disagree, settle it before answering. The more direct one wins: the real result beats a report about it.
- Look for what contradicts your idea, not only for what confirms it.

## 5. Answer point by point

- First what matters most, in one sentence. Then every ask on the list with its answer. None left unanswered.
- Each claim carries short evidence: what you saw and where ("opened it: it stopped at step 3", "the live page says...").
- **No detail you did not see with your own eyes.** If the source does not show which command, file or number it was, write "I did not see which" and how to find out. Do not fill the gap with what it "surely was": a confident invented detail is worse than an admitted gap. (In testing, the first version of this skill wrote "stuck on read_sessions.py" when it was really `cd && ls && tail`. This rule fixed it.)
- Keep verified and unverified apart ("not verified, we will know at 6:18").
- Plain words, no padding. No "should", "I think" or "probably" about something you could have checked: check it.

## Check before sending

- Does every ask in the message have its answer?
- Did I read in full every document or chat I talk about, and say how much I read?
- Did I open what is inside, or did I stop at a label, a name or a summary?
- Does every important conclusion have two agreeing signals?
- Is there a vague sentence I could have checked? Check it or delete it.
- Did I see in a source every name, command, number and cause I wrote? Mark deductions as deductions, or remove them.

Pairs with [`one-answer`](https://github.com/RabbitDesigns22/one-answer) (one final answer, thought through) and [`never-twice`](https://github.com/RabbitDesigns22/never-twice) (an error log so the same mistake never happens twice). This skill is the step before both: understand, then study.
