# UX Waiting States Audit Report Template

Use this template structure for audit reports.

---

# UX Waiting States Audit: [Application Name]

**Audit Date:** [Date]  
**URL:** [Target URL]  
**Operation Tested:** [Description of long-running operation]  
**Duration Observed:** [How long the operation took]

---

## Executive Summary

**Overall Score: X/10** categories addressed

[2-3 sentence summary of findings]

### Key Findings
- [Most important finding 1]
- [Most important finding 2]
- [Most important finding 3]

---

## Screenshots Timeline

| Timestamp | Screenshot | Key Observations |
|-----------|------------|------------------|
| T+0s (Start) | [screenshot_start.png] | [What user sees when operation begins] |
| T+10s | [screenshot_10s.png] | [Changes, activity indicators] |
| T+30s | [screenshot_30s.png] | [Progress, partial results] |
| T+Complete | [screenshot_complete.png] | [Final state, completion UX] |

---

## Detailed Findings

| # | Category | Score | Evidence | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | Progressive Value | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 2 | Heartbeat Indicators | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 3 | Time Estimation | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 4 | Process Explanation | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 5 | Sunk Cost Visibility | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 6 | Work While Waiting | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 7 | Interruptible/Exit | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 8 | Graceful Degradation | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 9 | Completion Celebration | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |
| 10 | Anxiety Reduction | ✅/⚠️/❌ | [What was observed] | [Specific improvement] |

---

## Strengths

What the application does well:

1. **[Strength 1]**: [Description]
2. **[Strength 2]**: [Description]
3. **[Strength 3]**: [Description]

---

## Critical Gaps

Missing elements that hurt UX most:

1. **[Gap 1]**: [Description and impact]
2. **[Gap 2]**: [Description and impact]
3. **[Gap 3]**: [Description and impact]

---

## Priority Matrix

### P1 - High Impact (Implement First)
| Improvement | Effort | Impact | Why Priority |
|-------------|--------|--------|--------------|
| [Improvement 1] | Low/Med/High | High | [Reason] |
| [Improvement 2] | Low/Med/High | High | [Reason] |

### P2 - Medium Impact
| Improvement | Effort | Impact | Why Priority |
|-------------|--------|--------|--------------|
| [Improvement 3] | Low/Med/High | Medium | [Reason] |
| [Improvement 4] | Low/Med/High | Medium | [Reason] |

### P3 - Nice to Have
| Improvement | Effort | Impact | Why Priority |
|-------------|--------|--------|--------------|
| [Improvement 5] | Low/Med/High | Low | [Reason] |

---

## Quick Wins

Low-effort improvements with high impact:

1. **[Quick Win 1]**: [Implementation suggestion]
   - Effort: ~[X hours/days]
   - Impact: [Expected improvement]

2. **[Quick Win 2]**: [Implementation suggestion]
   - Effort: ~[X hours/days]
   - Impact: [Expected improvement]

3. **[Quick Win 3]**: [Implementation suggestion]
   - Effort: ~[X hours/days]
   - Impact: [Expected improvement]

---

## Best-in-Class Comparisons

| Feature | [Application] | Best-in-Class Example |
|---------|---------------|----------------------|
| Progress indicator | [Current state] | Figma: percentage + file count |
| Streaming results | [Current state] | ChatGPT: token-by-token |
| Background processing | [Current state] | Slack: upload continues + notification |
| Completion UX | [Current state] | Duolingo: celebration animation |

---

## Technical Implementation Notes

### Suggested Code Patterns

**Progress indicator:**
```jsx
<ProgressBar 
  value={progress} 
  label={`${processed} of ${total} items processed`}
/>
```

**Heartbeat counter:**
```jsx
<StatusText>
  Found {count} results • {elapsed}s elapsed
</StatusText>
```

**Cancel button:**
```jsx
<Button onClick={handleCancel} variant="secondary">
  Stop and show current results
</Button>
```

---

## Appendix: Raw Observations

### Page State at Each Interval

**T+0s:**
```json
{
  "url": "",
  "hasSpinner": false,
  "hasProgressBar": false,
  "statusText": ""
}
```

**T+10s:**
```json
{
  "url": "",
  "hasSpinner": true,
  "hasProgressBar": false,
  "statusText": ""
}
```

**T+30s:**
```json
{
  "url": "",
  "hasSpinner": true,
  "hasProgressBar": false,
  "statusText": ""
}
```

**T+Complete:**
```json
{
  "url": "",
  "hasSpinner": false,
  "hasProgressBar": false,
  "statusText": ""
}
```
