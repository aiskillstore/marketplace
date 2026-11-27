---
id: "route-preprocessing"
title: "Shortest paths with route preprocessing"
category: "geospatial"
summary: "Choose when to preprocess a road graph for repeated exact shortest-path queries."
aliases: ["dijkstra","contraction hierarchies","road routing","en kısa yol","en kısa rotayı önceden hızlandırma","yol grafiği kısayolları","iki uçtan rota arama"]
decisions: [{"when":"The graph is small or changes continuously","use":"Use Dijkstra or an admissible A* over the current graph.","tradeoff":"Query work grows, but updates stay cheap and semantics remain explicit."},{"when":"Many queries reuse a mostly stable graph","use":"Preprocess shortcuts and choose a customization strategy appropriate for changing weights.","tradeoff":"Build time, memory and graph update complexity increase."}]
checks: ["Compare costs and unpacked routes against a reference solver across random endpoints.","Test unreachable routes, one-way roads and changed weights after a refresh."]
sources: [{"title":"Contraction Hierarchies, original paper","url":"https://ae.iti.kit.edu/english/1536.php"},{"title":"Dibbelt et al., Customizable Contraction Hierarchies","url":"https://arxiv.org/abs/1402.0402"}]
---

<!-- Generated record title. -->
# Shortest paths with route preprocessing

## Scenario

A regional dispatch app serves repeat route queries between depots. Road geometry changes slowly, while travel-time weights need separate refreshes.

## Failure modes

A shortcut built with one weighting may fail to preserve optimal paths under another. Preserve directed edges, turn restrictions and the path behind each shortcut.

## Explain it simply

Prepare frequent route work ahead of time so each new request checks a smaller set of roads.

## Implementation guidance

Keep a representative unprocessed shortest-path baseline on the same directed graph and compare both travel cost and reconstructed turns. Reuse graph preprocessing across weight changes only with an algorithm designed for that customization, or refresh it according to the weight version. A region with irregular full rebuilds may prefer per-request routing. Test one-way streets, new turn restrictions and a closure that invalidates a formerly optimal shortcut.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The graph is small or changes continuously** Use Dijkstra or an admissible A* over the current graph. Query work grows, but updates stay cheap and semantics remain explicit.
- **Many queries reuse a mostly stable graph** Preprocess shortcuts and choose a customization strategy appropriate for changing weights. Build time, memory and graph update complexity increase.

## Verification

- Compare costs and unpacked routes against a reference solver across random endpoints.
- Test unreachable routes, one-way roads and changed weights after a refresh.

## Sources

- [Contraction Hierarchies, original paper](https://ae.iti.kit.edu/english/1536.php)
- [Dibbelt et al., Customizable Contraction Hierarchies](https://arxiv.org/abs/1402.0402)

<!-- End generated record details. -->
