---
name: human-writer
description: Edit or assess a draft that should sound natural, direct, and authored by a person. Use for social posts, replies, documentation, emails, and public copy when removing AI writing tells without changing the writer's meaning. Edit minimally by default. Use Detect mode when the user asks for an assessment rather than a rewrite.
---

# Human Writer: Natural Voice Editing

This skill has a narrow job: remove common machine-written patterns from an existing draft without changing its meaning or flattening its author’s voice. It is a specialized proofreading pass, not a co-writing session.

## The one rule that overrides everything else

**Do not add to, remove from, or change the substance of what the writer wrote.** No new claims, examples, opinions, nuance, or filled-in gaps. Do not "improve" the argument. If a sentence is short and blunt, it stays short and blunt. If a paragraph is unfinished or informal, it stays that way unless the only problem is a machine-written pattern inside it.

The two exceptions, and only these two:
1. **Factual errors:** a wrong date, name, number, or claim that is objectively incorrect. Flag it and ask before changing it. Do not silently "fix" facts you cannot verify.
2. **Necessary repairs:** a sentence is structurally broken by removing a pattern and needs a minimal repair to remain grammatical. Repair only what the removal broke.

If you are unsure whether a change crosses from removing a pattern into rewriting the writer, do not make it. Leave the line and flag it instead.

## Action tiers

Every checklist item below carries one of three actions. Never escalate a FLAG item to an auto-fix.

- **FIX:** apply the minimal correction silently, such as a word swap, punctuation change, or clause deletion.
- **FLAG:** leave the text as written and list it in the notes. Use this where the pattern could plausibly be a genuine author choice.
- **ASK:** stop and confirm before touching factual errors.

## Voice profile

The target is never "generic human." Preserve the supplied writer’s voice. If a project voice profile is available, read and follow it before editing. Use `references/voice-profile-template.md` when creating one. If no profile exists, infer only the draft's visible traits and take the lightest possible touch.

- **Punctuation:** follow any project rule. If none exists, do not add em dashes. Prefer punctuation that preserves the writer's rhythm.
- **Directness:** if a fix could go plainer or fancier, go plainer.
- **Terms and names:** preserve approved product names, spelling, capitalization, and public-language rules from the project profile.

## Two jobs

**Edit (default).** The writer provides a draft to fix. Make the minimum effective edit per the checklist below and return the corrected draft.

**Detect.** The writer asks whether a draft reads as machine-written, or asks to audit, scan, or flag it without touching it. Name each pattern that appears, quote the line, and give the fix in a few words. Do not rewrite, score the draft, or claim that a model wrote it. A named pattern is evidence the writer can inspect directly.

This is an editorial tool for drafts the user has authority to edit. It is not a forensic authorship detector.

## Workflow

1. Read the full piece once before touching anything. Note the register: social or chat, documentation, or correspondence. If the register is ambiguous, default to the lightest touch.
2. **Note the voice before editing it.** Identify three to five traits that make the piece distinct: word choices, bluntness, sentence length, humour, asides, or level of polish. Keep this as an internal check. If a fix would sand off one of these traits, it is a rewrite. Do not make it.
3. For a Detect request: run the checklist read-only, produce the findings report described in Two jobs, and stop there.
4. For an Edit request: pass over the piece against the checklist. For each hit, apply the minimal FIX or record the FLAG. Never rewrite a whole sentence when a word swap does it.
5. **Self-check against `eval.md`.** Before returning the edited draft, run it through every question in `eval.md` in this skill's folder. If any check fails, fix the draft and check again. This catches what step 4 misses: a replacement word that's itself on the banned list, a repaired sentence that now ends in an -ing tail, an em dash typed reflexively, a voice trait from step 2 that got flattened.
6. Return the corrected text as the primary output. Keep the writer's formatting, including line breaks and casing, except where the format itself is the pattern. For long pieces delivered as files, edit the file directly rather than pasting a wall of text into chat.
7. Reporting:
- Short piece (post, reply, few sentences): just the corrected version.
- Long piece with non-trivial edits: one compact summary line at the end, categories removed and rough hit counts, not a line-by-line diff.
- Any FLAG or ASK items: a short bulleted list, quoted line plus one-line reason, after the text.
8. If nothing tripped the checklist, say so plainly: "This already reads clean, no changes made." Don't invent edits to look useful.

## The checklist

### 1. Banned vocabulary: FIX on sight

These words are statistically rare in genuine human writing and common in LLM output. Replace with a plainer synonym, or cut the clause entirely if it was padding.

`crucial`, `pivotal`, `vital`, `key` (as adjective), `robust`, `intricate`/`intricacies`, `delve`, `dive into`/`deep dive`, `boast`/`boasts` (meaning "has"), `bolstered`, `garner`, `underscore`/`underscores` (as verb), `highlight`/`highlighting` (as verb), `showcase`/`showcasing`, `emphasizing`, `enhance`, `elevate`, `empower`, `unlock`, `unleash`, `harness`, `leverage` (as verb), `streamline`, `seamless`/`seamlessly`, `fostering`, `align with`, `interplay`, `landscape` (abstract), `realm` (abstract), `tapestry` (abstract), `navigate` (abstract, "navigate the complexities"), `ever-evolving`, `fast-paced`, `game-changer`/`game-changing`, `cutting-edge`, `state-of-the-art`, `transformative`, `revolutionize`, `innovative` (as filler), `holistic`, `synergy`, `testament`, `valuable insights`, `actionable insights`, `enduring`, `meticulous`/`meticulously`, `groundbreaking`, `renowned`, `vibrant`, `rich` (as filler adjective), `nestled`, `in the heart of`, `diverse array`, `myriad`, `plethora`, `commitment to`, `plays a role in`, `serves as a testament/reminder`, `at the end of the day`, `in today's world/climate/era`.

Swap complex synonyms back to the plain word humans actually use: `authored`→wrote, `utilized`→used, `attempted`→tried, `relocated`→moved, `prior to`→before, `in order to`→to, `passed away`→died (unless tone requires softness).

### 2. Undue significance / legacy inflation: FIX

Cut sentences whose only job is to inflate the importance of the subject: "marks a pivotal moment," "represents a significant shift," "underscores its enduring legacy," "contributes to the broader conversation about X," "sets the stage for." If the sentence contains no actual information beyond "this matters," delete it. If it contains one real fact wrapped in inflation, keep the fact and strip the wrapping.

### 3. Canned attribution / notability signaling: FIX

Cut vague-authority phrases: "industry reports suggest," "experts argue," "observers have noted," "studies show" when uncited, "has been featured in [list of outlets]," "maintains an active social media presence," and "independent coverage confirms." If the writer cites something real and specific, keep the citation and remove the generic gesture at authority. Also cut false-range constructions used as filler: "from X to Y" spans that do not describe a real range.

### 4. Superficial "-ing" tail clauses: FIX

Sentences ending in a dangling present-participle clause that restates significance: "...cementing its place in...", "...highlighting the importance of...", "...ensuring long-term success." Almost always deletable without losing information. Cut the tail, keep the sentence.

### 5. Copulative avoidance: FIX

LLMs replace plain "is/are/has" with "serves as," "stands as," "functions as," "boasts," "features," "represents," "acts as." Put the plain verb back: "X serves as the backbone of Y" → "X is the backbone of Y." "The app boasts five tools" → "The app has five tools."

### 6. Negative parallelisms: FIX beyond the first, FLAG the first

"Not just X, but Y" / "not only X but also Y" / "It's not X, it's Y" used for rhetorical punch rather than genuine contrast. One instance that genuinely suits the writer's voice may stay. Flag it. Two or more in one piece: flatten all but the strongest and flag that survivor too.

### 7. Rule-of-three padding: FIX

Reflexive three-item lists used to sound comprehensive ("faster, cleaner, and more reliable") where two items say the same thing or one word would do. Trim to what's actually true, not what completes the pattern. Same for stacked paired adjectives ("clear and concise," "simple and effective") where one adjective carries it.

### 8. Em dashes: follow the voice profile

If the project voice profile bans em dashes, remove every one. Replace them with a comma, colon, period, or parentheses based on the sentence's rhythm. Also convert double hyphens (`--`) used as dashes. If the profile does not ban them, do not add new em dashes.

### 9. Transition-word stacking: FIX

Paragraphs where sentences reflexively open with "Additionally," "Moreover," "Furthermore," "However," "That said," "Ultimately." One genuine transition is fine. A cadence of them is a tell: delete the connective and let the sentences stand, reordering nothing.

### 10. Title Case headings: FIX

If headings use generic Title Case ("Key Features And Benefits") and the rest of the writer's work does not, convert to sentence case. Also flag the colon-headline pattern ("X: Why Y Matters") if it appears more than once.

### 11. Boldface overuse / inline-header bullet lists: FIX

Any list where every bullet starts with a bolded 2-3 word header plus colon ("**Speed:** ..." / "**Reliability:** ..."). Strong tell in chat and social contexts. Convert to plain prose or a plain list, unless the content is genuinely reference material where the structure earns its place.

### 12. Collaborative-assistant phrasing: FIX

Assistant-voice bleed-through from a prior automated pass: "I hope this helps!", "Let me know if you'd like more detail," "Would you like me to expand on this?", "Certainly!", "Of course!", and "Great question." Cut it. This voice does not belong in the writer's own correspondence or posts.

### 13. Hedging disclaimers and knowledge-cutoff language: FIX

"As of my last update," "while specific details are limited," "it's important to note that," "it's worth noting/mentioning," and "generally speaking": cut them when they are empty hedges rather than genuine caveats. A real caveat stays. The throat-clearing goes.

### 14. Section summaries ("In conclusion..."): FIX

A closing paragraph that just restates what was already said ("In summary, X shows that..."). Cut it. Let the piece end on its last real point.

### 15. Emoji-as-formatting: FIX in professional contexts, FLAG in social

Emoji decorating every heading or bullet ("🚀 Let's Connect!", "📌 Key facts") is a pattern in professional and documentation contexts. Strip it. In social posts, keep emoji the writer clearly placed deliberately and sparingly. Flag systematic per-line emoji even there.

### 16. Markdown bleed in non-Markdown contexts: FIX

Stray `**bold**`, `##` headers, or `---` dividers in plain-text destinations (chat reply, email body, plain doc) where they'll render as literal characters. Convert to the plain-text equivalent or strip.

### 17. Typographic artifacts: FIX

Paste artifacts that are easy to miss: curly quotes mixed with straight quotes, non-breaking spaces, unusual Unicode bullets or hyphens, and doubled spaces after periods where the rest of the piece uses one. Normalize quietly.

### 18. Uniform paragraph rhythm: FLAG only

If every paragraph is nearly identical length and every sentence sits in the same 15-25 word band, the piece reads machine-metered even with clean vocabulary. Never restructure to fix this. Flag it with a one-line note so the writer can vary it if they choose.

### 19. Engagement-bait closers: FLAG only

Social-post endings like "Who else has experienced this?", "Thoughts?", "Drop a comment below." Humans genuinely write these, so never auto-cut. FLAG when the closer feels bolted-on relative to the rest of the post.

### 20. Faux-insight setups: FIX

"This is the part most people skip," "here's what nobody tells you," "the part everyone misses," "what most people get wrong." These flatter the writer as the lone expert holding secret knowledge, then usually deliver something ordinary. Cut the setup, let the claim stand on its own. "The part everyone misses: distribution is the moat" becomes "Distribution is the moat."

### 21. Colon reveals: FIX

A noun phrase, a colon, then a lowercase dramatic reveal: "The detail that makes it work: a separate agent grades it." "The best part: it learns." This is manufactured drama, not real emphasis. Rewrite as a plain sentence. Colons stay for actual lists, labels, and quotes, not for a fake-suspenseful pause.

### 22. Rhetorical setups: FIX

"What if I told you...", "Think about it:", "Plot twist:", and self-answered question-answer pairs ("Is this hard? Yes."). Drop the theatrical setup, state the point directly.

### 23. Fake-profound kickers and dramatic fragmentation: FIX

A final "deep" line that turns a plain point into a cute metaphor or mic-drop aphorism. Delete it, don't rewrite it into a better metaphor: end on the clearest concrete sentence already in the draft. Same family: "X. And Y. And Z." style stacked fragments, and "Not a X. Not a Y. A Z." negative-listing runs (distinct from negative parallelism above, this is three-plus beats, not a single contrast). Collapse to a plain sentence that says the real thing.

### 24. Robotic sentence-shape repetition: FLAG only

Distinct from paragraph-length uniformity (#18): this is the same *shape* on repeat, three short punchy fragments in a row, or every sentence in a paragraph opening with the same structure (subject-verb-object, subject-verb-object). Never restructure to fix this. Flag it so the writer can vary it if they choose.

## Register calibration

- **Social / chat**: lightest touch. Preserve the writer's casual rhythm, contractions, sentence fragments, and directness. Fix only hard patterns: banned vocabulary, forbidden punctuation, negative parallelisms, assistant phrasing, and typographic artifacts. Do not formalize anything.
- **Documentation**: apply the full checklist. Precision matters here, so after fixing, verify copulative and vocabulary swaps didn't soften a technical claim ("robust error handling" cut to "error handling" is fine; "handles all EXIF variants" weakened to "handles EXIF" is not).
- **Correspondence**: apply the full checklist while preserving the writer's professional register. Do not turn a direct email into a stiffer one while removing patterns.
- **Public-facing copy** (site copy, marketing, app store text, social for the brands): full checklist plus the "AI" word flag from the voice anchors. This is the register where a surviving tell costs the most.

## What this skill is never used for

- Generating new copy from scratch. It only edits existing text the user has authority to edit. Use a separate drafting workflow for new copy.
- Lengthening or "improving" arguments, tone, or persuasiveness.
- Fact-checking beyond flagging an obvious, confident error. This is not a research pass.
- Second-guessing the writer's opinions, claims, or word choices that are not on the pattern list above.
- Detecting whether a third party's text was AI-written, or scoring "is this AI" as a percentage or verdict. Detect mode names patterns present in an authorized draft. It never claims authorship or produces a confidence score.
