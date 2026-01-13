---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: devops-runbooks
---

# Runbook: {{PROCEDURE_NAME}}

**Service:** {{SERVICE_NAME}}
**Last Updated:** {{DATE}}
**Owner:** {{TEAM_OR_PERSON}}
**Severity:** {{P1|P2|P3|P4}}

---

## Overview

**Purpose:** {{WHAT_THIS_RUNBOOK_ADDRESSES}}

**When to Use:** {{TRIGGER_CONDITIONS}}

**Expected Duration:** {{TIME_ESTIMATE}}

---

## Prerequisites

- [ ] Access to {{SYSTEM_1}}
- [ ] Access to {{SYSTEM_2}}
- [ ] {{TOOL}} installed
- [ ] On-call permissions

### Required Credentials

| System | Credential Location |
|--------|---------------------|
| {{SYSTEM}} | {{VAULT_PATH_OR_LOCATION}} |

---

## Quick Reference

### Key Commands

```bash
{{MOST_COMMON_COMMAND_1}}
{{MOST_COMMON_COMMAND_2}}
```

### Important URLs

| Resource | URL |
|----------|-----|
| Dashboard | {{URL}} |
| Logs | {{URL}} |
| Metrics | {{URL}} |

### Key Contacts

| Role | Contact |
|------|---------|
| Service Owner | {{CONTACT}} |
| Escalation | {{CONTACT}} |

---

## Procedure

### Step 1: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

```bash
{{COMMAND}}
```

**Expected Output:**

```
{{EXPECTED_OUTPUT}}
```

**If Unexpected:** Go to [Troubleshooting](#troubleshooting)

---

### Step 2: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

```bash
{{COMMAND}}
```

**Verify:**

```bash
{{VERIFICATION_COMMAND}}
```

---

### Step 3: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

**Decision Point:**

- If {{CONDITION_A}}: Continue to Step 4
- If {{CONDITION_B}}: Skip to Step 6
- If {{CONDITION_C}}: Escalate

---

### Step 4: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

---

## Verification

### Success Criteria

- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}

### Verification Commands

```bash
{{HEALTH_CHECK_COMMAND}}
```

**Expected:**

```
{{HEALTHY_OUTPUT}}
```

---

## Rollback

If the procedure fails or causes issues:

### Step 1: {{ROLLBACK_STEP}}

```bash
{{ROLLBACK_COMMAND}}
```

### Step 2: {{ROLLBACK_STEP}}

```bash
{{ROLLBACK_COMMAND}}
```

### Verify Rollback

```bash
{{VERIFY_ROLLBACK}}
```

---

## Troubleshooting

### {{ERROR_SCENARIO_1}}

**Symptom:**

```
{{ERROR_MESSAGE}}
```

**Cause:** {{ROOT_CAUSE}}

**Resolution:**

```bash
{{FIX_COMMAND}}
```

---

### {{ERROR_SCENARIO_2}}

**Symptom:** {{SYMPTOM}}

**Resolution:** {{FIX}}

---

### {{ERROR_SCENARIO_3}}

**Symptom:** {{SYMPTOM}}

**Resolution:** {{FIX}}

---

## Escalation

### When to Escalate

- {{ESCALATION_TRIGGER_1}}
- {{ESCALATION_TRIGGER_2}}
- Duration exceeds {{TIME}}

### Escalation Path

1. **L1:** {{CONTACT}}
2. **L2:** {{CONTACT}}
3. **L3:** {{CONTACT}}

### Escalation Template

```
Subject: [{{SEVERITY}}] {{SERVICE_NAME}} - {{ISSUE_SUMMARY}}

Issue: {{DESCRIPTION}}
Started: {{TIME}}
Impact: {{IMPACT}}
Actions Taken: {{ACTIONS}}
Current Status: {{STATUS}}
```

---

## Related Runbooks

- [{{RELATED_RUNBOOK_1}}]({{PATH}})
- [{{RELATED_RUNBOOK_2}}]({{PATH}})

---

## Appendix

### A. Architecture Context

{{RELEVANT_ARCHITECTURE_INFO}}

### B. Historical Issues

| Date | Issue | Resolution |
|------|-------|------------|
| {{DATE}} | {{ISSUE}} | {{RESOLUTION}} |

### C. Automation Opportunities

- {{AUTOMATION_IDEA_1}}
- {{AUTOMATION_IDEA_2}}

---

## Quality Checklist

- [ ] Steps are clear and actionable
- [ ] Commands are copy-pasteable
- [ ] Verification steps included
- [ ] Rollback procedure documented
- [ ] Escalation path defined
- [ ] Troubleshooting covers common issues
- [ ] Tested recently (within {{TIMEFRAME}})
