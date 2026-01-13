# Skill Gap Analyzer - Process Flow

## Overview

Comprehensive process for analyzing skill library gaps, redundancies, and optimization opportunities.

## Process Phases

### Phase 1: Library Inventory (10-15 min)

**Input:** Skill directories

**Actions:**
1. Scan all SKILL.md files
2. Parse YAML frontmatter
3. Extract metadata (name, description, tags, complexity, agents)
4. Categorize skills by path/domain
5. Map capabilities from descriptions
6. Track agent usage patterns

**Output:**
```json
{
  "totalSkills": 47,
  "categories": {
    "development": 15,
    "github": 12,
    "optimization": 8,
    "testing": 5,
    "meta-tools": 3
  },
  "capabilities": {
    "code-generation": ["coder", "auto-coder", ...],
    "testing": ["tester", "tdd-swarm", ...]
  },
  "agents": {
    "coder": 12,
    "researcher": 8,
    "reviewer": 6
  },
  "complexity": {
    "LOW": 8,
    "MEDIUM": 27,
    "HIGH": 12
  }
}
```

**Hook Integration:**
```bash
npx claude-flow@alpha hooks pre-task --description "Inventorying skill library"
npx claude-flow@alpha memory store --key "gap-analysis/inventory" --value "{...}"
```

---

### Phase 2: Coverage Gap Detection (15-20 min)

**Input:** Inventory + domain requirements

**Actions:**
1. Define comprehensive domain matrix
2. Check coverage for each domain/capability
3. Calculate coverage percentages
4. Identify missing capabilities
5. Test scenario execution readiness
6. Prioritize gaps by impact

**Domain Matrix:**
```javascript
{
  "Development": [
    "code-generation", "testing", "debugging", "refactoring",
    "documentation", "code-review", "architecture"
  ],
  "DevOps": [
    "deployment", "monitoring", "ci-cd", "infrastructure",
    "security", "scaling", "backup-recovery"
  ],
  "Data Engineering": [
    "data-analysis", "data-transformation", "data-validation",
    "data-migration", "etl-pipeline", "data-visualization"
  ],
  // ... more domains
}
```

**Gap Detection Output:**
```json
{
  "gaps": [
    {
      "domain": "Data Engineering",
      "coverage": "23.1%",
      "missingCapabilities": [
        "data-transformation",
        "data-validation",
        "data-migration",
        "etl-pipeline"
      ],
      "priority": "high"
    }
  ],
  "scenarioCoverage": [
    {
      "scenario": "Full-stack web app",
      "coverage": "92.3%",
      "missing": ["load-testing"],
      "canExecute": true
    },
    {
      "scenario": "ML pipeline deployment",
      "coverage": "71.4%",
      "missing": ["model-versioning", "ab-testing"],
      "canExecute": false
    }
  ]
}
```

---

### Phase 3: Redundancy Detection (10-15 min)

**Input:** Inventory + capability mapping

**Actions:**
1. Find capabilities handled by multiple skills
2. Analyze overlap percentage (description similarity)
3. Identify naming collisions
4. Calculate consolidation opportunities
5. Estimate token/storage savings

**Redundancy Analysis:**
```javascript
function detectRedundancy(inventory) {
  const redundancies = [];

  for (const [capability, skills] of Object.entries(inventory.capabilities)) {
    if (skills.length > 2) {
      const skillDetails = skills.map(loadSkillDetails);
      const overlap = calculateJaccardSimilarity(skillDetails);

      if (overlap > 0.70) {
        redundancies.push({
          capability,
          skillCount: skills.length,
          skills,
          overlapPercentage: (overlap * 100).toFixed(1),
          recommendation: generateConsolidationPlan(skillDetails)
        });
      }
    }
  }

  return redundancies;
}
```

**Output:**
```json
{
  "redundancies": [
    {
      "capability": "code-review",
      "skillCount": 4,
      "skills": [
        "code-review-assistant",
        "github-code-review",
        "pr-review-automation",
        "code-quality-checker"
      ],
      "overlapPercentage": "78.3%",
      "recommendation": {
        "action": "consolidate",
        "newSkill": "code-review-orchestrator",
        "retainSpecialization": ["security", "performance"],
        "estimatedSavings": "~15K tokens"
      }
    }
  ]
}
```

---

### Phase 4: Optimization Analysis (15-20 min)

**Agent Task:** Researcher
**Instructions:**
1. Load usage metrics from memory
2. Identify under-utilized skills
3. Identify over-complex skills
4. Find composability improvements
5. Suggest dependency optimizations
6. Store findings

**Under-Utilization Detection:**
```javascript
function findUnderutilized(usageMetrics) {
  return usageMetrics.filter(m =>
    m.frequency < 0.05 && // Less than 5% usage
    m.lastUsed > 90 // Days since last use
  ).map(m => ({
    skill: m.name,
    frequency: (m.frequency * 100).toFixed(2) + "%",
    lastUsed: m.lastUsed + " days ago",
    totalUses: m.totalUses,
    recommendation: m.totalUses === 0
      ? "Consider archiving or adding promotion docs"
      : "Review value proposition and discoverability"
  }));
}
```

**Over-Complexity Detection:**
```javascript
function findOvercomplex(usageMetrics) {
  return usageMetrics.filter(m =>
    m.avgTokens > 5000 && // High token usage
    m.successRate < 0.7 // Low success rate
  ).map(m => ({
    skill: m.name,
    avgTokens: m.avgTokens,
    successRate: (m.successRate * 100).toFixed(1) + "%",
    recommendation: analyzeComplexity(m)
  }));
}

function analyzeComplexity(metric) {
  if (metric.avgSteps > 10) {
    return "Break into smaller, focused skills";
  }
  if (metric.avgAgents > 5) {
    return "Simplify orchestration or create sub-workflows";
  }
  if (metric.errorRate > 0.3) {
    return "Improve error handling and validation";
  }
  return "Review and simplify prompt/process";
}
```

**Output:**
```json
{
  "optimizations": {
    "underutilized": [
      {
        "skill": "legacy-converter",
        "frequency": "1.89%",
        "lastUsed": "127 days ago",
        "totalUses": 3,
        "recommendation": "Archive or add use-case documentation"
      }
    ],
    "overcomplex": [
      {
        "skill": "full-stack-architect",
        "avgTokens": 8743,
        "successRate": "64.3%",
        "recommendation": "Break into: backend-architect, frontend-architect, database-architect"
      }
    ],
    "composability": [
      {
        "pattern": "Repeated authentication setup",
        "affected": ["api-builder", "service-deployer", "webhook-handler"],
        "recommendation": "Extract 'auth-setup' micro-skill"
      }
    ]
  }
}
```

---

### Phase 5: Recommendation Generation (10-15 min)

**Input:** All analysis results

**Actions:**
1. Synthesize findings
2. Prioritize by impact and effort
3. Generate immediate/short/long-term actions
4. Create detailed recommendations
5. Calculate expected impact
6. Format comprehensive report

**Prioritization Matrix:**
```javascript
function prioritizeRecommendations(findings) {
  const recommendations = [];

  // Immediate (critical gaps, high-impact consolidations)
  findings.gaps.filter(g => g.priority === "critical").forEach(gap => {
    recommendations.push({
      timeframe: "immediate",
      type: "gap",
      action: `Create skill: ${suggestSkillName(gap)}`,
      impact: "high",
      effort: estimateEffort(gap),
      expectedOutcome: `Coverage ${gap.coverage} → ${gap.targetCoverage}`
    });
  });

  // Short-term (optimizations, medium gaps)
  findings.optimizations.overcomplex.forEach(opt => {
    recommendations.push({
      timeframe: "short-term",
      type: "optimization",
      action: `Refactor: ${opt.skill}`,
      impact: "medium",
      effort: "medium",
      expectedOutcome: opt.recommendation
    });
  });

  // Long-term (architectural improvements, low-priority gaps)
  findings.composability.forEach(comp => {
    recommendations.push({
      timeframe: "long-term",
      type: "architecture",
      action: `Refactor for composability: ${comp.pattern}`,
      impact: "medium",
      effort: "high",
      expectedOutcome: `Reusable across ${comp.affected.length} skills`
    });
  });

  return recommendations;
}
```

**Report Generation:**
```markdown
## Skill Gap Analysis Report
**Date:** 2025-01-15
**Total Skills:** 47
**Analysis Duration:** 52 minutes

---

## Executive Summary

### Coverage
- Overall: 67.2%
- Target: 90.0%
- Critical gaps: 2
- High-priority gaps: 5

### Redundancy
- Duplicate functionality: 3 instances
- Consolidation opportunities: 4
- Potential savings: ~22K tokens

### Optimization
- Under-utilized: 3 skills
- Over-complex: 2 skills
- Composability improvements: 6

---

## Prioritized Recommendations

### Immediate Actions (This Week)
1. [ ] **Create:** data-engineering-workflow
   - Gap: Data Engineering (23% coverage)
   - Impact: Coverage +62%
   - Effort: 2-3 days

2. [ ] **Consolidate:** code review skills (4 → 1)
   - Redundancy: 78% overlap
   - Impact: -15K tokens, clearer structure
   - Effort: 1-2 days

### Short-Term (This Month)
3. [ ] **Refactor:** full-stack-architect → 3 focused skills
   - Current: 8.7K tokens, 64% success
   - Impact: +30% success rate, easier maintenance
   - Effort: 3-4 days

4. [ ] **Archive:** legacy-converter
   - Usage: 1.89%, last used 127 days ago
   - Impact: Reduced maintenance overhead
   - Effort: 1 hour

### Long-Term (This Quarter)
5. [ ] **Extract:** auth-setup micro-skill
   - Affects: 6 skills with repeated auth code
   - Impact: DRY compliance, consistency
   - Effort: 1 week
```

**Hook Integration:**
```bash
npx claude-flow@alpha memory store --key "gap-analysis/recommendations" --value "{...}"
npx claude-flow@alpha hooks post-task --task-id "gap-analysis" --metrics "{...}"
```

---

## Decision Tree

```
Start: Analyze skill library
  |
  v
Library size?
  Small (<20) → Focus on gaps
  Medium (20-50) → Full analysis
  Large (>50) → Add sampling/clustering
  |
  v
Analysis type?
  Quick scan → Gaps + critical redundancy
  Comprehensive → All dimensions
  Targeted → Specific domain/category
  |
  v
Run inventory
  |
  v
Detect gaps (always)
  |
  v
Detect redundancy (if comprehensive or large library)
  |
  v
Analyze optimizations (if comprehensive)
  |
  v
Generate recommendations
  |
  v
Prioritize by impact/effort
  |
  v
Format report
  |
  v
Store findings in memory
  |
  v
End
```

## Integration Points

### Pre-Task Hook
```bash
npx claude-flow@alpha hooks pre-task \
  --description "Analyzing skill library" \
  --complexity "medium" \
  --estimated-duration "60min"
```

### Memory Storage
```bash
# Inventory
npx claude-flow@alpha memory store \
  --key "gap-analysis/inventory" \
  --value "{totalSkills, categories, capabilities, ...}"

# Findings
npx claude-flow@alpha memory store \
  --key "gap-analysis/findings" \
  --value "{gaps, redundancies, optimizations}"

# Recommendations
npx claude-flow@alpha memory store \
  --key "gap-analysis/recommendations" \
  --value "{immediate, shortTerm, longTerm}"
```

### Post-Task Hook
```bash
npx claude-flow@alpha hooks post-task \
  --task-id "gap-analysis-q1-2025" \
  --metrics "{coverage, redundancy, recommendations}"
```

## Success Criteria

- Complete inventory: 100% of skills catalogued
- Gap detection: All domains analyzed
- Redundancy detection: >70% overlap threshold
- Recommendations: Actionable, prioritized, measurable
- Report: Comprehensive, clear, decision-ready

## Follow-Up Actions

1. Review recommendations with team
2. Create tickets/tasks for implementation
3. Schedule regular reviews (quarterly)
4. Track recommendation adoption
5. Measure impact of changes
6. Update analysis criteria as needed

## Related Processes

- Prompt Optimization (optimize individual skills)
- Token Budget Management (estimate resource impact)
- Skill Creation (implement gap recommendations)
