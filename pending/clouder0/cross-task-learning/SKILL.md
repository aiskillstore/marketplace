---
name: cross-task-learning
description: Pattern for aggregating insights across multiple tasks to enable data-driven evolution.
allowed-tools: Read, Write, Glob
---

# Cross-Task Learning Skill

Pattern for maintaining aggregated insights across all completed tasks.

## When to Load This Skill

- Reflector: After writing individual reflection
- Evolver: Before analyzing reflections (to get aggregated view)

## Core Concept

Individual reflections capture task-specific learnings. Cross-task learning aggregates these to identify:

- **Patterns that keep appearing** → Skill candidates
- **Strategies that consistently work** → Best practices
- **Strategies that keep failing** → Anti-patterns
- **Bottlenecks that recur** → System weaknesses
- **Proposals that keep emerging** → Priority improvements

## Aggregate File

Location: `memory/reflections/_aggregate.json`

Example structure (compact JSON):

```json
{"last_updated":"ISO-8601","tasks_analyzed":15,"strategy_effectiveness":[{"strategy":"Spawn parallel explorers for context","uses":12,"successes":10,"effectiveness_score":0.83,"notes":"Works well for unfamiliar codebases"}],"failure_patterns":[{"pattern":"Contract conflicts in parallel implementation","occurrences":4,"severity":"high","status":"active"}],"skill_candidates":[{"pattern":"Read → Explore → Implement → Test → Verify","frequency":8,"effectiveness":"high","proposed_skill_name":"implementation-cycle"}]}
```

## Update Protocol (for Reflector)

After writing individual reflection, update aggregate:

```
1. Read current _aggregate.json
2. Read the reflection just written

3. Update task_history:
   - Add new entry with task_id, timestamp, outcome
   - Keep last 20 entries (trim oldest)

4. Update strategy_effectiveness:
   FOR each strategy in reflection.patterns.effective_strategies:
     IF strategy exists in aggregate:
       → Increment uses and successes
       → Recalculate effectiveness_score
     ELSE:
       → Add new entry with uses=1, successes=1

   FOR each strategy in reflection.patterns.ineffective_strategies:
     IF strategy exists in aggregate:
       → Increment uses and failures
       → Recalculate effectiveness_score
     ELSE:
       → Add new entry with uses=1, failures=1

5. Update failure_patterns:
   FOR each issue in reflection.process_analysis.phases[].issues:
     IF similar pattern exists (fuzzy match):
       → Increment occurrences
       → Update last_seen
     ELSE:
       → Add new pattern

6. Update bottleneck_hotspots:
   FOR each bottleneck in reflection.process_analysis.bottlenecks:
     IF location exists:
       → Increment frequency
       → Add cause if new
     ELSE:
       → Add new hotspot

7. Update skill_candidates:
   FOR each sequence in reflection.patterns.repeated_sequences:
     IF sequence.skill_candidate == true:
       IF similar pattern exists:
         → Increment frequency
       ELSE:
         → Add new candidate

8. Update recurring_discoveries:
   FOR each finding in reflection.knowledge_discovered:
     IF similar finding exists:
       → Increment discovery_count
       → Set should_be_documented = true if count >= 3
     ELSE:
       → Add new entry

9. Update recurring_proposals:
   FOR each proposal in reflection.evolution_proposals:
     IF similar proposal exists:
       → Increment occurrence_count
     ELSE:
       → Add new entry

10. Update retry_analysis:
    FOR each retry in reflection.process_analysis.retries:
      → Increment total_retries
      → Update by_strategy counts

11. Increment tasks_analyzed
12. Update last_updated
13. Write updated _aggregate.json (compact JSON)
```

## Similarity Matching

When checking if patterns are "similar":

```
Normalize both strings:
  - Lowercase
  - Remove punctuation
  - Remove common words (the, a, an, is, are)

Compare using:
  - Exact match after normalization
  - OR: >70% word overlap
  - OR: Same key terms present
```

## Thresholds for Action

| Metric | Threshold | Action |
|--------|-----------|--------|
| Strategy effectiveness < 0.3 | After 5 uses | Flag as anti-pattern |
| Strategy effectiveness > 0.8 | After 5 uses | Flag as best practice |
| Failure pattern occurrences | >= 3 | Flag for urgent fix |
| Skill candidate frequency | >= 5 | Propose as new skill |
| Recurring discovery count | >= 3 | Add to knowledge base |
| Recurring proposal count | >= 3 | Prioritize for evolution |

## Query Patterns (for Evolver)

**Get top issues to fix:**
```
failure_patterns
  WHERE status == "active"
  ORDER BY occurrences * severity_weight DESC
  LIMIT 5
```

**Get best practices to document:**
```
strategy_effectiveness
  WHERE effectiveness_score > 0.8
  AND uses >= 5
```

**Get skill candidates ready for implementation:**
```
skill_candidates
  WHERE frequency >= 5
  AND effectiveness == "high"
  AND status == "candidate"
```

**Get knowledge gaps:**
```
recurring_discoveries
  WHERE should_be_documented == true
  AND NOT in knowledge_base
```

## Integration with Evolver

The evolver should:

1. Read `_aggregate.json` FIRST (not individual reflections)
2. Use aggregated data for proposal prioritization:
   - High-occurrence failure patterns → High priority
   - High-frequency skill candidates → Medium priority
   - Recurring proposals → Already validated ideas
3. Reference individual reflections only for details
4. Update `recurring_proposals[].status` after evolution

## Principles

1. **Aggregate, don't duplicate** - Summary stats, not copies
2. **Track trends** - First seen, last seen, frequency
3. **Enable queries** - Structure for easy filtering
4. **Threshold-based actions** - Clear criteria for when to act
5. **Fuzzy matching** - Similar patterns should merge, not duplicate
