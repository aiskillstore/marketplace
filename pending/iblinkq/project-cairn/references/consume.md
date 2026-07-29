# consume

Pull and cite knowledge from the configured external knowledge base into the current project.

## When

Apply the **graduation-symmetry test** before starting a piece of work (writing code, making a technical decision, debugging an error): would any conclusion this work produces — **or depends on** — qualify as a graduation candidate (see `graduation.md` → Candidate criteria — for work not yet done, judge by the reusability and abstraction criteria; verification and traceability can only come with the work itself)? If yes, check the INDEX first — someone may already have graduated the same kind of conclusion.

"Produces or depends on" matters: the work's own deliverable may be purely project-local (this repo's CI config file) while the reusable kernel inside it (how to structure CI caching, which pitfalls to avoid) is exactly what another project may have graduated. Test the reusable kernel of the work, not the deliverable.

The project's own `cairn/` topic notes take precedence: consult them first, and let the INDEX check trigger only for what the project itself has no recorded conclusion on.

With a deferred provider (`graduation.provider: none` in `.cairn/config.yaml`), there is no external INDEX to check yet: the reflex reduces to the project's own `cairn/` topic notes until a knowledge base is connected at the first graduation (`graduation.md` → Deferred provider).

Examples of applying the test (not an exhaustive list):

- Integrating an external API/SDK this project hasn't used before, where such integration experience is typically reusable → check.
- An error whose *solution shape* would be reusable and this project's own notes have nothing on it → check.
- A technology/architecture selection decision with no recorded conclusion in this project → check.
- The user directly asks "how should we do X" where X is a domain this project has no settled conclusion for → check.
- Configuring this repo's CI caching — the deliverable (a project-local config file) isn't reusable, but the work depends on reusable knowledge another project may have graduated → check.
- Pure project-internal detail judgments (naming a variable) — no reusable kernel anywhere in the work → don't check.

Checking is cheap (at any scale, the first read is titles + summaries, not note bodies — see Retrieval); when the test says yes, err toward checking. The precision lives at the citation step below, not here.

## Retrieval

How to *find* candidate notes scales with the knowledge base's size. The entry point is `graduation.index` in `.cairn/config.yaml`.

- **Tens of notes (flat INDEX)** — read the INDEX top-to-bottom; a full scan of a one-line-per-note list is still the cheapest reliable option.
- **Hundreds (tiered INDEX)** — read the top-level domain index, descend into the relevant domain sub-index, scan that.
- **Beyond that (query-first)** — don't scan; query. Run the funnel below, with the INDEX kept as the recall safety net.

Query funnel — use the provider's native query interfaces (`provider-interface.md` → Read side; prefer them over raw grep, fall back explicitly when they're unavailable):

1. **Structured/tag query** on the task's domain terms (frontmatter properties, tags).
2. **Fulltext search** scoped to the knowledge-base container, when structured/tag misses.
3. **Graph expansion** from any hit — follow links/backlinks to adjacent notes before concluding coverage.
4. **Fallback scan** — a query miss is not proof of absence; finish by scanning the relevant (sub-)INDEX the flat way.

At every tier the unit read is the same: index lines or query results give titles + summaries; open only the note bodies that look relevant.

## How

1. Locate candidate notes per **Retrieval** above.
2. Read only the relevant external notes.
3. Apply the **adoption bar** before writing any `cairn/Cited.md` entry: a note earns an entry only when its conclusion was adopted or adapted into the current work's concrete output — a decision made, a code approach taken, a fix applied. Checked the INDEX, opened a note, found it inapplicable or only loosely related → no entry; skip without trace. Checking is not a commitment to cite.
   - Adoption includes **negative adoption**: a note that shaped the judgment by ruling a path out ("we didn't go down road Y because of this note") has influenced the concrete output and earns an entry. The bar is "influenced the concrete output," not "was copied verbatim."
4. For each note that clears the bar, add a pointer row to `cairn/Cited.md`: what was pulled, why, where it applies, and a link back to the source note. Create `cairn/Cited.md` from the template on first use.
5. Never copy the full body of an external knowledge note into the project — a copy starts rotting the day it is made. Link back and re-read the latest version when needed.
6. Update project topic notes only with project-specific conclusions or adaptations, not with wholesale duplicated knowledge-base text.

`Cited.md` is a pointer list (the knowledge body lives in the knowledge base). `cairn/Reference/` is different: it holds raw external inputs the project owns outright. Keep them separate.
