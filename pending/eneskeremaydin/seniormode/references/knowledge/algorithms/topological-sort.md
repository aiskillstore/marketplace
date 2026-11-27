---
id: "topological-sort"
title: "Topological sort and cycle detection"
category: "algorithms"
summary: "Schedule directed dependencies and produce a clear diagnostic when no valid order exists."
aliases: ["topological sort","kahn algorithm","course prerequisites","topolojik sıralama","dependency order","önkoşula göre ders sırası","bağımlılık döngüsü","işleri bağımlılıklarına göre sırala"]
decisions: [{"when":"A complete explicit dependency graph is available","use":"Use Kahn's queue and count incoming edges, with a stable priority if ties matter.","tradeoff":"It needs adjacency storage and an extra policy to report a concrete cycle."},{"when":"A diagnostic path is more important than stable scheduling","use":"Use depth-first search with color states and preserve the recursion stack or an explicit stack.","tradeoff":"Deep graphs must avoid overflowing the call stack."}]
checks: ["Verify every directed prerequisite precedes its dependent in the result.","Test detached nodes, duplicate input edges and cycles."]
sources: [{"title":"Python graphlib topological sorting","url":"https://docs.python.org/3/library/graphlib.html"},{"title":"Boost Graph topological sort","url":"https://www.boost.org/latest/libs/graph/doc/html/graph/algorithms/topological_sort/topological_sort.html"}]
---

<!-- Generated record title. -->
# Topological sort and cycle detection

## Scenario

A learning platform suggests a feasible order for courses, each of which may require several other courses first.

## Failure modes

An edge pointing in the wrong direction reverses meaning. Duplicate edges break counts if inserted inconsistently, and stable output needs a tie rule.

## Explain it simply

Take a course once all its prerequisites are done. If none can start and courses remain, the prerequisites form a loop.

## Implementation guidance

If course A is a prerequisite for B, put the edge from A to B and count it once. Pull a zero-incoming-degree node from the ready set, updating its dependants as it leaves. If the ready set empties with nodes remaining, report the cycle status. A remaining node can be downstream of a cycle without belonging to it. To diagnose one actual loop, search the remaining subgraph for a back edge in the active DFS path. Use a stable ready-node comparator when plans are saved or compared, and test a cycle with a downstream dependent alongside an isolated node.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A complete explicit dependency graph is available** Use Kahn's queue and count incoming edges, with a stable priority if ties matter. It needs adjacency storage and an extra policy to report a concrete cycle.
- **A diagnostic path is more important than stable scheduling** Use depth-first search with color states and preserve the recursion stack or an explicit stack. Deep graphs must avoid overflowing the call stack.

## Verification

- Verify every directed prerequisite precedes its dependent in the result.
- Test detached nodes, duplicate input edges and cycles.

## Sources

- [Python graphlib topological sorting](https://docs.python.org/3/library/graphlib.html)
- [Boost Graph topological sort](https://www.boost.org/latest/libs/graph/doc/html/graph/algorithms/topological_sort/topological_sort.html)

<!-- End generated record details. -->
