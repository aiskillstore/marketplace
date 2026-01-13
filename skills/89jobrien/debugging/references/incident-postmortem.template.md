---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: debugging
---

# Incident Postmortem: {{INCIDENT_TITLE}}

**Incident ID:** {{INC-XXXX}}
**Date:** {{YYYY-MM-DD}}
**Duration:** {{START_TIME}} - {{END_TIME}} ({{DURATION}})
**Severity:** {{SEV1|SEV2|SEV3|SEV4}}
**Status:** {{RESOLVED|MONITORING}}

---

## Summary

{{ONE_PARAGRAPH_SUMMARY}}

### Impact

| Metric | Value |
|--------|-------|
| Users Affected | {{N}} |
| Revenue Impact | ${{N}} |
| Requests Failed | {{N}} |
| Error Rate | {{N}}% |
| Downtime | {{DURATION}} |

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
| {{HH:MM}} | {{TRIGGER_EVENT}} |
| {{HH:MM}} | Alert fired: {{ALERT_NAME}} |
| {{HH:MM}} | On-call paged |
| {{HH:MM}} | Investigation started |
| {{HH:MM}} | Root cause identified |
| {{HH:MM}} | Mitigation applied |
| {{HH:MM}} | Service recovered |
| {{HH:MM}} | Incident closed |

---

## Root Cause

{{DETAILED_ROOT_CAUSE_ANALYSIS}}

### Contributing Factors

1. {{FACTOR_1}}
2. {{FACTOR_2}}
3. {{FACTOR_3}}

### What Failed

- **Detection:** {{HOW_WAS_IT_DETECTED}}
- **Prevention:** {{WHY_WASNT_IT_PREVENTED}}
- **Response:** {{RESPONSE_GAPS}}

---

## Resolution

### Immediate Actions

1. {{ACTION_1}}
2. {{ACTION_2}}

### Mitigation Steps

```bash
{{COMMANDS_OR_STEPS_TAKEN}}
```

### Verification

- [ ] Service health restored
- [ ] Error rates normalized
- [ ] No recurring alerts

---

## Lessons Learned

### What Went Well

- {{POSITIVE_1}}
- {{POSITIVE_2}}

### What Went Wrong

- {{NEGATIVE_1}}
- {{NEGATIVE_2}}

### Where We Got Lucky

- {{LUCKY_1}}

---

## Action Items

| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| 1 | {{ACTION}} | {{OWNER}} | {{P1-4}} | {{DATE}} | {{STATUS}} |
| 2 | {{ACTION}} | {{OWNER}} | {{P1-4}} | {{DATE}} | {{STATUS}} |
| 3 | {{ACTION}} | {{OWNER}} | {{P1-4}} | {{DATE}} | {{STATUS}} |

### Prevention

- [ ] {{PREVENTIVE_MEASURE_1}}
- [ ] {{PREVENTIVE_MEASURE_2}}

### Detection

- [ ] {{DETECTION_IMPROVEMENT_1}}
- [ ] {{DETECTION_IMPROVEMENT_2}}

### Response

- [ ] {{RESPONSE_IMPROVEMENT_1}}
- [ ] {{RESPONSE_IMPROVEMENT_2}}

---

## Technical Details

### Affected Systems

| System | Impact | Recovery |
|--------|--------|----------|
| {{SYSTEM}} | {{DESCRIPTION}} | {{TIME}} |

### Metrics During Incident

| Metric | Normal | During Incident | Peak |
|--------|--------|-----------------|------|
| Latency (p99) | {{MS}} | {{MS}} | {{MS}} |
| Error Rate | {{N}}% | {{N}}% | {{N}}% |
| CPU Usage | {{N}}% | {{N}}% | {{N}}% |
| Memory | {{N}}GB | {{N}}GB | {{N}}GB |

### Logs

```
{{RELEVANT_LOG_SNIPPETS}}
```

---

## Communication

### Internal

| Time | Channel | Message |
|------|---------|---------|
| {{TIME}} | {{SLACK/EMAIL}} | {{SUMMARY}} |

### External

| Time | Channel | Audience | Message |
|------|---------|----------|---------|
| {{TIME}} | Status Page | Customers | {{MESSAGE}} |

---

## Related Incidents

| ID | Date | Similarity |
|----|------|------------|
| {{INC-XXXX}} | {{DATE}} | {{DESCRIPTION}} |

---

## Appendix

### A. Alert Configuration

```yaml
{{ALERT_CONFIG}}
```

### B. Runbook Updates Needed

- {{RUNBOOK_UPDATE_1}}
- {{RUNBOOK_UPDATE_2}}

---

## Quality Checklist

- [ ] Timeline is complete and accurate
- [ ] Root cause clearly identified
- [ ] Impact quantified
- [ ] Action items have owners and due dates
- [ ] Lessons learned documented
- [ ] Prevention measures identified
- [ ] Related incidents linked
