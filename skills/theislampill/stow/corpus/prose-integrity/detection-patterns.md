## How to Self-Check

1. Read your text aloud. If phrases sound unnatural in speech, revise them
2. Ask: "Would I say this in a conversation with a colleague?"
3. Check for repetitive sentence structures
4. Look for clusters of the words listed above
5. Ensure varied sentence lengths (not all similar length)
6. Verify each intensifier adds genuine meaning
7. Count hedging markers per paragraph. More than 3 in a single paragraph is a red flag.
8. Check paragraph word counts within each section. If they are all similar, vary them.
9. Search for hallucinated markup: `oaicite`, `contentReference`, `turn0search0`, `grok_card`
10. Check if your introduction, body, and conclusion have different pacing and sentence complexity

## Em Dashes: The Primary AI Tell

**The em dash (—) has become one of the most reliable markers of AI-generated content.**

Em dashes are longer than hyphens (-) and are used for emphasis, interruptions, or parenthetical information. While they have legitimate uses in writing, AI models drastically overuse them.

### Why Em Dashes Signal AI Writing
- AI models were trained on edited books, academic papers, and style guides where em dashes appear frequently
- AI uses em dashes as a shortcut for sentence variety instead of commas, colons, or parentheses
- Most human writers rarely use em dashes because they don't exist as a standard keyboard key
- The overuse is so consistent that it has become the unofficial signature of ChatGPT writing

### What To Do Instead
| Instead of | Use |
|------------|-----|
| The results—which were surprising—showed... | The results, which were surprising, showed... |
| This approach—unlike traditional methods—allows... | This approach, unlike traditional methods, allows... |
| The study found—as expected—that... | The study found, as expected, that... |
| Communication skills—both written and verbal—are essential | Communication skills (both written and verbal) are essential |

### Guidelines
- Use commas for most parenthetical information
- Use colons to introduce explanations or lists
- Use parentheses for supplementary information
- Reserve em dashes for rare, deliberate emphasis only
- If you find yourself using more than one em dash per page, revise

## Hallucinated Markup Artifacts

When AI generates wikitext, it sometimes hallucinates citation markup from its training data. These are 100% confidence indicators of unedited AI output:

| Artifact | Origin |
|----------|--------|
| `oaicite` | OpenAI ChatGPT citation placeholder |
| `contentReference` | OpenAI internal reference tag |
| `grok_card` | xAI Grok citation tag |
| `attributableIndex` | AI attribution tracking artifact |
| `turn0search0` | ChatGPT search result placeholder |

Any occurrence of these strings in wikitext means the text was pasted from an AI tool without editing. Zero tolerance.

## Model-Family-Specific Tells

Different AI model families produce distinct stylistic fingerprints based on their training and RLHF tuning.

### GPT-4o / GPT-4.5 (OpenAI)
- Heavy use of bullet-point formatting and structured lists
- Staccato short-sentence contrasting: "It's not X. It's Y." used to simulate punchy copy
- Rhetorical colon abuse: "Here's the thing:", "Think about it:", "The bottom line:", "The reality:"
- Over-structures arguments into numbered steps

### Claude 3.5 / Claude 4 (Anthropic)
- Better sentence length variation than GPT, but still exhibits flat segmental entropy
- Overly polite and conciliatory transitions: "It's worth considering that", "To be fair", "That said"
- Leans toward poetic and metaphorical prose with words like "nuanced," "complexities"
- Loses thread in long documents and resorts to increasingly generic transitions
- Tends toward diplomatic hedging even when stating documented facts

### Common Across All Models
- Uniform paragraph lengths
- Predictable section ordering (Background > Details > Impact > Response)
- Citation clustering at paragraph ends rather than distributed throughout sentences
- Excessive boldface on concepts, product names, and inline headers

## Self-check before returning text

Run this pass on every piece of prose before you hand it back. The full banned lists are in `references/ai-writing-detection.md`; check against them directly.

1. Search for the emdash character. Remove every one (Rule 1).
2. Scan for banned verbs (delve, leverage, utilize, foster, bolster, underscore, unveil, streamline) and replace with plain equivalents.
3. Scan for banned adjectives and intensifiers (robust, comprehensive, pivotal, seamless, significantly, extremely, truly) and cut or replace.
4. Scan for banned transitions and openers (Furthermore, Moreover, That being said, In today's world, It's worth noting that).
5. Check every number: is it real and attributable? If not, cut it (Rule 2).
6. Check every sentence ends on a concrete detail, not an assertion of importance (Rule 5).
7. Check headings: does each name the content rather than tease it (Rule 16)?
8. Check for repeated points and repeated section shapes (Rules 6, 7).
9. Count hedging markers per paragraph. More than three is a red flag.
10. Read it aloud. If a phrase would sound unnatural to a colleague, rewrite it.

## Structural and Statistical Patterns

Beyond lexical tells, AI text exhibits measurable structural uniformity that human writing does not.

### Paragraph Length Uniformity
AI aims for visual symmetry. Paragraphs tend toward identical sentence counts (typically 3-4 sentences each). Human writing varies paragraph length based on sub-topic complexity.
- **Threshold:** If all paragraphs in a section are within 15% of each other in word count, the section is likely AI-generated.
- **Exception:** Bulleted lists, tables, and template fields are structurally uniform by design.

### Sentence Length Uniformity (Burstiness)
Human writing alternates between short, punchy sentences and long, clause-heavy ones. AI sentences cluster uniformly around 15-20 words.
- **Threshold:** If a 500-word block contains no sentences under 8 words or over 30 words, it lacks human burstiness.
- **Human baseline:** Human text exhibits 3+ distinct syntactic patterns per 100 words. AI text shows 1.5 or fewer.

### Transition Density
AI over-relies on transition words and adverbial clauses to maintain flow between paragraphs.
- **Threshold:** If more than 30% of paragraphs in an article begin with a transition word or adverbial clause, the text is structurally artificial.

### Opening-Word Repetition
Three or more consecutive paragraphs starting with the same word or phrase pattern indicates mechanical generation. Vary opening words.

### Segmental Entropy
AI maintains flat stylistic consistency from introduction through conclusion. Human writers naturally vary pacing, complexity, and sentence structure between sections.
- **Threshold:** Calculate sentence length variance separately for the introduction, body, and conclusion. If variance differs by less than 10% across all three segments, the text was likely generated as a single pass by AI.
- **Why this matters:** Human introductions tend to be tighter and more declarative. Human body sections are denser with longer sentences. Human conclusions shift register. AI maintains a monotone throughout.

### Contrasting Parallelism Overuse
2025-era models overuse sequential contrasting structures to simulate punchy emphasis:
- "It's not X, it's Y."
- "It's not about X, it's about Y."
- "The issue isn't X. The issue is Y."
- **Threshold:** More than two contrasting parallelisms in a 500-word block.
