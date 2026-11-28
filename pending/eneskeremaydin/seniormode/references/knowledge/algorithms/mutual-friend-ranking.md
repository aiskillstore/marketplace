---
id: "mutual-friend-ranking"
title: "Two-hop friend recommendations"
category: "algorithms"
summary: "Traverse a local friendship graph and rank eligible candidates by distinct shared neighbors."
aliases: ["breadth first search","bfs","friends of friends","mutual friends","ortak arkadaş","arkadaş önerisi","ortak arkadaş sayısı","arkadaşın arkadaşları"]
decisions: [{"when":"The local graph fits a bounded traversal","use":"Expand first-hop neighbors and count distinct valid paths to second-hop candidates.","tradeoff":"High-degree neighbors can make latency variable."},{"when":"Hubs dominate or recommendations can be stale","use":"Use bounded sampling or periodically compute candidates with exposure filters.","tradeoff":"Sampling affects ranking and precomputation must honor current privacy exclusions."}]
checks: ["Compare against an exact graph fixture with duplicates, blocks and existing friends.","Set a budget for a hub node and verify bounded behavior."]
sources: [{"title":"Boost Graph breadth-first search","url":"https://www.boost.org/doc/libs/latest/libs/graph/doc/html/graph/algorithms/traversal/breadth_first_search.html"},{"title":"Neo4j Common Neighbors scoring","url":"https://neo4j.com/docs/graph-data-science/current/algorithms/topological-link-prediction/common-neighbors/"}]
---

<!-- Generated record title. -->
# Two-hop friend recommendations

## Scenario

A study group app recommends peers discovered through two steps of accepted connections. Blocked or hidden accounts must remain excluded.

## Failure modes

Repeated edges can inflate counts, and high-degree nodes can dominate query time. Private relationships must not leak through candidate scoring.

## Explain it simply

Count friends shared with each eligible candidate by looking two connections away.

## Implementation guidance

At request time distinguish visible edges from visible candidate accounts, then count distinct eligible first-hop intermediaries for each candidate. Exclude the requesting account and existing connections. A visible candidate's score can still encode a hidden relationship. Build scores from edges visible to the viewer, and recompute or suppress stale scores when an edge's visibility changes. Define a stable tie rule for pagination. Test that hiding one of two shared edges reduces the score of an otherwise visible candidate.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The local graph fits a bounded traversal** Expand first-hop neighbors and count distinct valid paths to second-hop candidates. High-degree neighbors can make latency variable.
- **Hubs dominate or recommendations can be stale** Use bounded sampling or periodically compute candidates with exposure filters. Sampling affects ranking and precomputation must honor current privacy exclusions.

## Verification

- Compare against an exact graph fixture with duplicates, blocks and existing friends.
- Set a budget for a hub node and verify bounded behavior.

## Sources

- [Boost Graph breadth-first search](https://www.boost.org/doc/libs/latest/libs/graph/doc/html/graph/algorithms/traversal/breadth_first_search.html)
- [Neo4j Common Neighbors scoring](https://neo4j.com/docs/graph-data-science/current/algorithms/topological-link-prediction/common-neighbors/)

<!-- End generated record details. -->
