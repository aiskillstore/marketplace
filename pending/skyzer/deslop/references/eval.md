# Deslop evaluation

Run this evaluation internally after every edit or detection report. Treat every item as pass or fail. If any item fails, revise the output and run the evaluation again.

## Hard invariant

1. Does the entire response contain zero Unicode em-dash characters?
2. If a detection quotation originally contained one, was it rendered as `[em dash]`?
3. In detect mode, was every source em dash flagged as the "Em dash" pattern?

A failure here blocks the response.

## Edit mode

1. Does the edit preserve the original meaning, factual claims, attitude, and intended level of formality?
2. Did it avoid inventing claims, examples, numbers, sources, opinions, or certainty?
3. Does it preserve recognizable voice signals such as vocabulary, cadence, bluntness, humor, uncertainty, and digressions?
4. Were strong human sentences left alone?
5. Is the amount of change proportional to the actual slop?
6. Were useful names, dates, numbers, mechanisms, and examples preserved?
7. Are direct verbs and active constructions used where they improve clarity?
8. Were empty significance, standalone filler sentences, promotional fog, vague authority, superficial analysis, fake-strong verbs, and filler removed?
9. Were binary contrasts, negative lists, faux-insight setups, colon reveals, rhetorical setups, synonym cycling, false ranges, and forced trios fixed?
10. Were dramatic fragments, robotic symmetry, fake-profound endings, recap endings, formatting slop, and chatbot residue removed where present?
11. Were genuine uncertainty, useful asides, and intentional fragments preserved?
12. Were contractions, opinions, rough edges, and rhythm changes preserved or introduced only when supported by the writer's voice and context?
13. Does the result sound like the same writer on a good day rather than a generic casual internet voice?
14. Would the copy sound natural when read aloud?
15. Did the response return only the cleaned text unless commentary was requested?

## Detect mode

1. Does every finding name a pattern from the skill?
2. Does every finding quote the relevant evidence and give a concise fix?
3. Does the response avoid rewriting the whole draft?
4. Does it avoid a numeric score and any claim about who or what wrote the text?
5. Does it avoid flagging a pattern without evidence?
6. If no pattern appears, does it say so plainly instead of inventing findings?

## Final read

1. Is the point easy to find?
2. Does every sentence earn its place?
3. Is the prose concrete where the source permits it?
4. Are sentence and paragraph shapes varied naturally rather than mechanically?
5. Has the edit removed AI mannerisms without sanding away the writer?