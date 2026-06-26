# Workflow 3: MeSH Search Strategy

**Purpose:** Build precise PubMed queries from MeSH terms.

## Procedure

1. Use `pubmed_lookup_mesh` to explore terms related to the topic.
2. Show term hierarchy (broader / narrower / related).
3. Construct Boolean query: MeSH terms + keywords.
   See [Query Construction](../search-strategy.md#query-construction) for templates.
4. Optionally spell-check query with `pubmed_spell_check`.
5. Execute via `pubmed_search_articles`.

## Output

Final PubMed query string, result count, and top results.
