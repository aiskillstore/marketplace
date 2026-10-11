# Clue library

Check against it in steps 2 and 4. Entry sources are marked `vNNN` (the number of a creator video the author broke down; the breakdown notes are not public) or `case` (a real case).

## Where clues live

| Place | Scope |
|---|---|
| `global.md` (this folder) | Cross-country: telling countries and continents apart (driving side, plate shape, multilingual signs), Europe-wide patterns, South Asia, inherited standards |
| `regions/<cc>/clues.md` | Inside one country: plates and codes to the province/state, local vehicles, infrastructure, climate, urban form. `regions.py show <cc>` prints a one-line index with line numbers |

Rule for placing a new entry: if its "Points to" stays inside one country, it goes into that country's pack; if it separates countries, it goes into `global.md`.

## Entry format

```markdown
### <clue name>
- Look for: exactly what to find in the image and how to recognize it
- Points to: country / province / city / type of area within a city
- Strength: strong (a single clue reaches this level) / medium (needs one more) / weak (can only exclude or boost)
- Counterexamples: when it leads to a wrong call
- Sources: vNNN or case
```

## Rules

- Every entry must state strength and counterexamples. A clue with no counterexample usually just hasn't been seen to mislead yet; that doesn't make it reliable.
- A clue can be marked "strong" only when three or more sources mention it independently; for a single source, write "(single source)".
- **Only include clues that transfer to new photos.** What one particular landmark looks like (a certain bridge, fountain, or building) doesn't go into the library: it won't help with the next photo, and it contaminates evaluations built from video puzzles.
- **Counterexamples and source notes also never state a specific puzzle's place names or conclusion** (writing "puzzle X's IP was in province A, actually in city B" amounts to writing the answer into the skill). When citing a puzzle, state only method-level facts ("the photo was in a province neighboring the IP province"). The same goes for script examples: use places unrelated to eval puzzles, or `<placeholders>`.
- Strength changes with context: the same plate is strong evidence on the street and weak evidence in a parking lot; vegetation without a month is always weak.
- Write methods in your own words; don't copy the video's wording verbatim.
