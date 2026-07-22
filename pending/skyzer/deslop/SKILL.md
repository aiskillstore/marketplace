---
name: "deslop"
description: "Deslop, humanize, edit, or audit AI-sounding, robotic, generic, corporate, or ChatGPT-like copy while preserving the writer's voice."
---

# Deslop

Edit AI-sounding writing into clear human prose without replacing the writer's voice with a different generic voice.

Keep the meaning, factual claims, attitude, and level of formality intact. Make the minimum effective edit. Leave strong human sentences alone.

One rule overrides every stylistic preference: never return an em dash. Use a comma, period, colon, semicolon, parentheses, or a rewritten sentence. This applies to edited copy, explanations, and quoted evidence.

## Choose the job

### Edit

Use edit mode by default when the user wants text rewritten, cleaned up, humanized, or deslopped.

Return the cleaned text. Do not explain the changes unless the user asks. For a sentence or two, use a light touch.

### Detect

Use detect mode when the user asks to audit, scan, flag, or judge a draft without rewriting it.

For every pattern found:

1. Name the pattern.
2. Quote the relevant line or fragment.
3. Give a short fix.

Do not rewrite the full draft, assign a slop score, or claim that AI wrote it. Named patterns are evidence; authorship detectors are guesses. If quoted source text contains an em dash, replace the character with `[em dash]` in the quotation.

If the user has not provided text, ask for it. Ask about audience, format, or intended effect only when the missing context could materially change the edit.

## Pass 1: Read before editing

Read the whole draft and identify internally:

- Its core point
- Its audience and job, when evident
- Three to five voice signals worth preserving, such as vocabulary, cadence, bluntness, humor, uncertainty, digressions, or formality
- The lines that already sound specific and human

Do not reorganize the draft unless its structure blocks understanding. Do not invent facts, examples, statistics, sources, opinions, or confidence.

## Pass 2: Remove slop

### Empty significance

Cut claims that tell the reader something matters instead of showing why:

- "Stands as a testament"
- "Marks a pivotal moment"
- "Plays a vital role"
- "Underscores its significance"
- "Sets the stage"
- Generic "challenges remain, but the future looks bright" endings

Keep the concrete fact and let the reader judge its importance.

### Standalone filler sentences

Cut sentences that only announce importance, simplicity, contrast, scope, or what the next paragraph will explain. Common examples include "That distinction matters," "This matters because," "The practical mental model is simple," "The key point is," "The same principle applies," and "This is why it matters."

Delete the sentence if it adds no fact, argument, or useful tension. If it contains a real point, merge that point into the surrounding sentence.

### Promotional fog

Replace inflated words such as "vibrant," "groundbreaking," "stunning," "breathtaking," "cutting-edge," and "game-changing" with specific details, or remove them.

### Vague authority

Replace "experts agree," "studies show," "industry reports suggest," and similar claims with a named source. If no source exists, remove or flag the claim. Never invent attribution.

### Superficial analysis

Cut trailing clauses built around "highlighting," "underscoring," "showcasing," "reflecting," "emphasizing," or "fostering" when they merely gesture at meaning. State the real consequence when the draft supports one.

### AI vocabulary

Prefer plain language over habitual AI words such as:

- crucial, robust, comprehensive, leverage, utilize, facilitate, empower
- navigate, landscape, realm, foster, paradigm, holistic, synergy
- delve, underscore, transformative, tapestry, interplay, intricacies
- pivotal, multifaceted, meticulous, paramount, elevate, embark, harness
- additionally, align with, enhance, valuable, ever-evolving

Do not replace a precise technical term just because it appears on this list.

### Fake-strong verbs and copula avoidance

Prefer "is," "has," and direct verbs over "serves as," "stands as," "functions as," "acts as," "made a decision," or "has the ability to."

Use active voice when it makes the actor and action clearer. Do not force active voice when the actor is unknown or irrelevant.

### Binary contrasts and negative lists

Remove templates such as:

- "It's not X. It's Y."
- "It's not just X, it's Y."
- "The question isn't X, it's Y."
- "Not X. Not Y. Z."

State the real point directly.

### Throat-clearing and faux insight

Cut setups that delay or inflate the point:

- "Here's the thing"
- "Let me be clear"
- "The uncomfortable truth is"
- "What nobody tells you"
- "The part everyone misses"
- "What most people get wrong"
- "The key takeaway is"
- "It's worth noting"
- "Let's explore" or "Let's dive in"

Keep a personal admission or aside only when it adds character, context, or honest uncertainty.

### Colon reveals

Rewrite dramatic noun-phrase reveals such as "The best part: it learns" or "The real problem: distribution." Use colons for lists, labels, explanations, and quotations, not manufactured suspense.

### Rhetorical setups

Remove "What if I told you," "Think about it," "Plot twist," and self-answered question-and-answer pairs when a direct statement works better.

### Dramatic fragmentation

Fix stacked fragments such as "That's it. That's the whole thing." and "X. And Y. And Z." Keep fragments that genuinely match the writer's natural cadence and do not create fake drama.

### Rule-of-three overuse

Do not force ideas into neat trios. Remove the third item when it is redundant or exists only for rhythm.

### Synonym cycling

Use the same clear noun consistently instead of rotating among near-synonyms to avoid repetition.

### False ranges

Replace "from X to Y" when X and Y are not endpoints on a meaningful scale. Use "X and Y" or name the actual scope.

### Filler and hedging

Compress empty phrases:

- "In order to" becomes "to"
- "Due to the fact that" becomes "because"
- "At this point in time" becomes "now"
- "Has the ability to" becomes "can"
- "It is important to note" is usually deleted

Remove stacked hedges. Keep "I think," "maybe," "probably," and similar language when it expresses real uncertainty or belongs to the writer's voice.

### Robotic rhythm

Break repeated sentence shapes, identical paragraph structures, and overly tidy parallelism. Do not replace them with a stack of manufactured punchy fragments. Let rhythm serve the point and the writer.

### Fake-profound endings

Delete the cute metaphor, aphorism, or mic-drop line when it adds no information. End on the last concrete point, useful takeaway, or next action.

### Summary-recap endings

Remove "In conclusion," "Ultimately," "Overall," and final paragraphs that only repeat what the reader just read.

### Formatting slop

Remove decorative formatting that does not help the content:

- Random bold emphasis
- Repeated inline-header lists when prose reads better
- Emoji headings unless the context clearly calls for them
- Headings over tiny sections
- Title Case headings when sentence case fits
- Curly quotation marks when plain straight quotes are required by the user's format

### Em dashes

Remove every em dash from edited text. Replace it with punctuation or rewrite the sentence. In detect mode, flag every source occurrence as the "Em dash" pattern and render the character as `[em dash]` in quoted evidence.

### Chatbot residue

Remove:

- "I hope this helps"
- "Let me know if you have questions"
- "Great question"
- Sycophantic openers
- Knowledge-cutoff disclaimers that are not relevant
- Meta-commentary about generating or presenting the answer

## Pass 3: Preserve the person

After removing slop, prevent the edit from becoming sterile or uniformly polished.

- Preserve the writer's recognizable vocabulary, cadence, bluntness, humor, uncertainty, digressions, and formality.
- Keep strong opinions already present. Do not invent stronger opinions.
- Use contractions when they fit the writer and context. Do not force casual speech into formal copy.
- Keep useful rough edges and asides. Do not manufacture roughness.
- Vary rhythm only where the original drones or repeats itself.
- Keep concrete names, numbers, dates, mechanisms, and examples.
- Trust the reader. Remove explanations that merely restate an obvious implication.
- Preserve the original progression unless a structural change clearly improves comprehension.

The result should sound like this writer on a good day, not like a universal "human" persona.

## Final audit

Read `references/eval.md` and check the full output against it. If any check fails, revise and run the audit again.

Before returning, scan the actual response for the Unicode em-dash character. There must be zero occurrences.

## Output

For edit mode, return only the cleaned text unless the user asks for commentary.

For detect mode, return the named findings with quoted evidence and concise fixes. If no listed pattern appears, say that plainly without inventing problems.

Preserve meaning above all.
