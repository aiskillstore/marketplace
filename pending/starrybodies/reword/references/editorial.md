# Editorial method

Use this reference for difficult edits, method changes, or provenance review. The default editing instructions live in `assets/editorial_kernel.txt`; do not load this reference for routine rewrites.

## Design and provenance

The method combines two useful upstream ideas: diagnose formula at the level of whole passages, then replace it with choices particular to the author and occasion. Cutting a blacklist of words cannot supply a voice. Repeated rewriting can remove the voice that was there.

| Pinned source | Retain | Change or omit |
| --- | --- | --- |
| [Harshaneel's humanize](https://github.com/harshaneel/humanize/tree/9c3dec34dc8e0ed9d26de14a869900a714da8f9e) | Derive actionable style hypotheses from samples; actively use those habits; rederive formulaic prose from its meaning; use domain-native vocabulary; remove the helpful-assistant wrapper. | Omit detector targets, universal word and punctuation bans, sentence-length arithmetic, plausible personal-experience framing, injected disfluency, and repeated generation loops. |
| [Blader's humanizer](https://github.com/blader/humanizer/tree/b48c832f0f809c1b5658edbb838c2521b72f2413) | Diagnose staging, inflation, repeated lessons, and the wrong reader; inspect paragraph movement; retain unusual details, mixed feelings, humor, and genuine asides. | Make patterns contextual editorial clues; preserve real contrasts and useful repetition. Return finished copy by default. Bound revision to one writing pass and one source comparison. |

These are design choices, not demonstrated quality advantages. Both upstream notices remain in `LICENSE`. Use the pinned versions when comparing methods; a moving upstream branch is a different comparator.

## Read for meaning and social purpose

Identify what the passage does for its reader: explain, invite, disagree, thank, persuade, reassure, or request a decision. Use the supplied occasion and conversation to decide which background the reader needs. An independent article may need context that a reply can omit. Do not infer shared knowledge merely to make a passage shorter.

Preserve informational and interpersonal work. A thank-you, expression of enthusiasm, gentle joke, pause, or acknowledgment can earn its place without adding a new fact. Remove interchangeable praise when it adds nothing; retain appreciation tied to a real contribution or relationship. Concision is one possible effect of editing, not the objective for every author.

## Track relationships before changing language

Keep an internal account of each substantive assertion and its qualifications. A list of unchanged names and numbers is insufficient: the same number can be reassigned to another project, a comparison can reverse, and a qualifier can move from one claim to another. Preserve agents, beneficiaries, value assignments, sequence, scope, evidence, and strength of commitment.

Maintain the difference between helping and leading, a plan and a promise, a possibility and an outcome, and correlation and cause. Keep the condition attached to the claim it limits. Preserve genuine uncertainty, even when a shorter unqualified sentence sounds more confident. Keep source ambiguity unless the supplied context resolves it.

For example, turning “I helped the team reduce X from A to B” into “I reduced X to B” changes both agency and the comparison. A polished sentence is still a failed edit if it makes that trade. Technical details, attribution, citations, and qualifications are not expendable merely because the prose is dense.

Source preservation means faithful editing, not independent fact verification. Do not use style samples, illustrative examples, background knowledge, or plausible guesses to fill factual gaps. When the text has no specifics, say its existing point plainly. Ask separately for a missing fact only if a useful, faithful edit depends on it.

## Replace formula with actual author habits

From deliberately supplied samples, infer a few observations that can guide the current edit: how the author enters a subject, which words they choose, how clauses accumulate or break, where they put asides, how they transition, and how they express feeling or disagreement. Prefer patterns repeated across samples to a striking one-off. Do not impose numerical imitation or copy signature phrases into unrelated situations.

Make the observations operational. An author who builds a thought through a winding sentence should not emerge as a row of slogans. An author who uses dry understatement can keep an understated aside. An author who speaks warmly and directly should retain both qualities. Use samples for these decisions while excluding their events, measurements, experiences, and personal claims from the target.

Without samples, develop the voice already present in the target and respect the requested register. Do not manufacture a personality to compensate for generic source material. In every case, preserve apt idiosyncrasies that make the passage sound chosen: an odd but accurate image, an unresolved feeling, familiar terminology, or an intentional repetition.

## Make warmth and humor possible

An editorial instruction to remove filler must leave room for human company. Keep a welcome that welcomes, thanks that acknowledge effort, and enthusiasm attached to the actual news. Preserve a stated wish to collaborate instead of reducing a friendly message to a transaction. Strengthen these moves through placement and phrasing before adding emotional intensity.

When the text and author support humor, preserve or sharpen the comic observation, timing, or understatement. A light aside or irony can comment on a situation already in the source without supplying a new event. Check that it fits the audience and does not change the author's attitude, belittle the recipient, or turn a factual claim into an exaggerated one. Leave literal technical and consequential claims literal.

Do not manufacture a comic anecdote, invented reaction, performed self-correction, deliberate typo, or unearned intimacy. Casual writing need not acquire slang, lowercase, fragments, or a joke. Let the available voice and situation make that choice.

## Rebuild passages around their point

For a formula-heavy passage, identify the claim or feeling beneath the scaffolding, choose the emphasis the reader needs, and write the sentence or paragraph anew. Preserve useful substance while changing how it arrives. This permits real structural editing without turning every revision into a shorter, blander paraphrase.

| Symptom | Editorial question and repair |
| --- | --- |
| Staged opener or candor | Does the run-up carry attitude or context the reader needs? If it only announces the point, start with the point. |
| Negation or contrast | Do both sides inform the reader, correct a real belief, or create deliberate emphasis? Keep the contrast when they do; state the supported point directly otherwise. |
| Repeated lesson or aphorism | Does the closing line add consequence, voice, or a necessary turn? Cut a redundant explanation of what the example already shows. |
| Abstraction or inflated significance | Use the actor, action, and specific detail already available. If none exists, simplify the claim without inventing evidence. |
| Borrowed authority | Preserve an actual attributed claim and its support. Do not replace an unnamed source with an invented authority or remove substantive uncertainty for neatness. |
| Uniform rhythm or format | Let thought, emphasis, and use determine sentence lengths, paragraphs, lists, and headings. Preserve deliberate patterns; break automatic ones. |
| Synonym churn | Name the same referent consistently. Find variety in syntax and emphasis instead of cycling labels. |
| Robotic warmth | Replace interchangeable praise with the author's supported appreciation or interest. Keep genuine politeness and conventional sign-offs when they serve the exchange. |

No punctuation mark, sentence shape, familiar word, or rhetorical device proves a passage needs editing. Evaluate its function and concentration in context. Strong claims may need qualification; a long sentence may hold the thought together; a list may be the clearest structure. Respect explicit house style and the author's supplied preferences.

## Keep the final comparison bounded

After one writing pass, compare the candidate with the source once. Look for changed claim relationships, missing substance, unsupported additions, lost attitude or warmth, and newly imposed formulas. Patch those defects. Do not begin a general second rewrite, generate variants for a detector, or keep smoothing until every sentence has the same voice.

Return only the finished text unless the user requests a critique, explanation, diff, or alternatives. Put necessary factual questions outside the finished copy. For file edits, keep technical spans protected and use the skill's local checks; a clean mechanical result cannot establish semantic equivalence.

## Integration contract

Use the same kernel for direct editing and provider-neutral generated prompts. Keep task constraints, target text, source context, samples, and illustrative examples in distinct input fields. Destination guidance may add reader expectations and format requirements; it must not silently replace the author's voice or authorize new facts. Examples demonstrate editing moves and never contribute target facts.

Keep the default path to one writing pass and one bounded source comparison. Load this reference only to resolve a hard editorial choice or inspect the method. Evaluate writing quality separately from mechanical preservation: reader preference, voice fidelity, unnecessary changes, claim drift, cost, and latency require different evidence. Model judgments can assist development; they do not establish human preference or detector evasion.
