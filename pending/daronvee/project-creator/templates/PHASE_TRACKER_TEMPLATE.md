# Multi-Phase Project Tracker: {{PROJECT_TITLE}}

**Project**: {{PROJECT_TITLE}}
**Status**: Phase 1 ({{PHASE_1_NAME}})
**Created**: {{CREATED_DATE}}
**Last Checked**: {{CREATED_DATE}}

---

## Phase Timeline

### Phase 1: {{PHASE_1_NAME}} (Target: {{PHASE_1_TARGET_DATES}})
**Status**: ✅ IN PROGRESS (started {{CREATED_DATE}})

**Goal**: {{PHASE_1_GOAL}}

**Duration**: {{PHASE_1_DURATION}}

**Completion Criteria**:
{{PHASE_1_CRITERIA}}

**Deliverables**:
{{PHASE_1_DELIVERABLES}}

**Proactive Reminder Logic**:
- **Weekly**: {{PHASE_1_REMINDER_LOGIC}}
- **Phase Transition**: {{PHASE_1_TRANSITION_TRIGGER}}

**Next Phase Trigger**: {{PHASE_1_NEXT_TRIGGER}}

---

### Phase 2: {{PHASE_2_NAME}} (Target: {{PHASE_2_TARGET_DATES}})
**Status**: ⏳ PENDING (starts after Phase 1 complete)

**Goal**: {{PHASE_2_GOAL}}

**Duration**: {{PHASE_2_DURATION}}

**Trigger**: {{PHASE_2_TRIGGER}}

**Completion Criteria**:
{{PHASE_2_CRITERIA}}

**Tasks**:
{{PHASE_2_TASKS}}

**Proactive Reminder**:
{{PHASE_2_REMINDER}}

**Next Phase Trigger**: {{PHASE_2_NEXT_TRIGGER}}

---

### Phase 3: {{PHASE_3_NAME}} (Target: {{PHASE_3_TARGET_DATES}})
**Status**: ⏳ PENDING (starts after Phase 2 complete)

**Goal**: {{PHASE_3_GOAL}}

**Duration**: {{PHASE_3_DURATION}}

**Trigger**: {{PHASE_3_TRIGGER}}

**Completion Criteria**:
{{PHASE_3_CRITERIA}}

**Tasks**:
{{PHASE_3_TASKS}}

**Proactive Reminder**:
{{PHASE_3_REMINDER}}

**Project Complete**: {{PROJECT_COMPLETION_DEFINITION}}

---

## Proactive Reminder Logic (How Claude Tracks This)

### Weekly Check (During Strategic Planning OR Friday Roadmap)
1. **Read** `PHASE_TRACKER.md` → Check current phase status
2. **Calculate** days since phase start (today - phase start date)
3. **Check** completion criteria:
   - Phase 1: {{PHASE_1_CHECK_LOGIC}}
   - Phase 2: {{PHASE_2_CHECK_LOGIC}}
   - Phase 3: {{PHASE_3_CHECK_LOGIC}}
4. **Prompt** phase transition if criteria met OR deadline passed

### Example Prompts
**Phase 1 Complete**:
```
"Phase 1 {{PHASE_1_NAME}} complete:
- {{PHASE_1_SUCCESS_INDICATORS}}

Ready to start Phase 2 ({{PHASE_2_NAME}})?"
```

**Phase 2 Complete**:
```
"Phase 2 {{PHASE_2_NAME}} complete:
- {{PHASE_2_SUCCESS_INDICATORS}}

Ready to move to Phase 3 ({{PHASE_3_NAME}})?"
```

### Manual Check (Anytime)
- User says: **"Check phase tracker"** OR **"Check phase tracker {{PROJECT_NAME}}"** → Claude reads PHASE_TRACKER.md, reports current status, prompts next phase if ready

---

## Success Criteria (Overall Project)

### Phase 1 Success
{{PHASE_1_SUCCESS_DEFINITION}}

### Phase 2 Success
{{PHASE_2_SUCCESS_DEFINITION}}

### Phase 3 Success
{{PHASE_3_SUCCESS_DEFINITION}}

**PROJECT COMPLETE**: {{OVERALL_SUCCESS_DEFINITION}}

---

## Reusable Pattern for Future Multi-Phase Projects

This Phase Tracker pattern can be applied to ANY multi-phase project:

**Step 1**: Create `PHASE_TRACKER.md` at project start
- List all phases, goals, duration, completion criteria
- Set target dates (realistic timelines)

**Step 2**: Add proactive reminders to root CLAUDE.md
- Weekly check during strategic planning
- Prompt phase transitions when criteria met

**Step 3**: Manual check available anytime
- User: "Check phase tracker" → Claude reports status

**Benefits**:
- Never forget Phase 2/3 (automatic transition prompts)
- Clear completion criteria (no guessing "am I done with Phase 1?")
- Documented timeline (realistic expectations)
- Reusable pattern (apply to any future project)

---

**Last Updated**: {{CREATED_DATE}}
**Next Check**: {{NEXT_CHECK_DATE}}
