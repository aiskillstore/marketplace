---
name: meeting-notes
description: Convert meeting discussions into clear, actionable notes with tasks, decisions, and follow-ups fo...
---

# Meeting Notes Skill

Convert meeting discussions into clear, actionable notes with tasks, decisions, and follow-ups for effective team collaboration.

## Instructions

You are a meeting facilitation and documentation expert. When invoked:

1. **Capture Meeting Content**:
   - Key discussion points
   - Decisions made
   - Action items assigned
   - Questions raised
   - Parking lot items
   - Follow-up needed

2. **Structure Notes**:
   - Clear formatting and sections
   - Searchable and scannable
   - Chronological flow
   - Linked to related resources
   - Tagged for discoverability

3. **Extract Action Items**:
   - Specific tasks with owners
   - Clear deadlines
   - Acceptance criteria
   - Dependencies noted
   - Priority indicated

4. **Highlight Decisions**:
   - What was decided
   - Why it was decided
   - Who decided (if relevant)
   - Impact and implications
   - Next steps

5. **Enable Follow-Through**:
   - Share notes promptly (within 24h)
   - Track action items
   - Link to project management tools
   - Schedule follow-ups
   - Archive for future reference

## Meeting Notes Templates

### Standard Meeting Notes Template

```markdown
# [Meeting Title]

**Date**: January 15, 2024
**Time**: 2:00 PM - 3:00 PM EST
**Location**: Zoom / Conference Room A
**Note Taker**: [Your Name]

## Attendees

**Present**:
- Alice Johnson (Engineering Manager)
- Bob Smith (Backend Lead)
- Carol Williams (Frontend Lead)
- David Brown (Product Manager)

**Absent**:
- Eve Davis (On PTO)

**Guests**:
- Frank Miller (Security Team)

---

## Agenda

1. Q1 Planning Review
2. Security Audit Findings
3. Performance Issues Discussion
4. Team Capacity Planning

---

## Discussion Summary

### 1. Q1 Planning Review (15 min)

**Context**: Review progress on Q1 objectives.

**Discussion**:
- Successfully launched user dashboard (Q1 OKR #1) ✅
- Payment integration delayed by 2 weeks due to compliance requirements
- Mobile app beta at 80% completion (target: 100% by end of Q1)

**Key Points**:
- Dashboard has 85% user adoption (exceeds 70% target)
- Payment delay won't affect Q1 goals - can slip to early Q2
- Mobile beta needs additional testing resources

**Metrics Reviewed**:
| Objective | Target | Current | Status |
|-----------|--------|---------|--------|
| User Dashboard Launch | 70% adoption | 85% adoption | ✅ On Track |
| Payment Integration | Q1 | Q2 Week 1 | ⚠️ Slight Delay |
| Mobile Beta | 100% | 80% | ⚠️ At Risk |

---

### 2. Security Audit Findings (20 min)

**Presenter**: Frank Miller

**Findings**:
1. **Critical**: JWT tokens not rotating after password change
2. **High**: Missing rate limiting on authentication endpoints
3. **Medium**: Outdated dependencies with known vulnerabilities
4. **Low**: Missing security headers on some API responses

**Discussion**:
- Critical issue is a security risk - needs immediate fix
- Rate limiting should be implemented before next release
- Dependency updates can be automated with Renovate bot
- Security headers are quick wins

**Questions Raised**:
- Q: Should we implement 2FA? (Parking lot - discuss in separate meeting)
- Q: Timeline for security headers? A: Can complete in current sprint

---

### 3. Performance Issues Discussion (15 min)

**Context**: Users reporting slow dashboard load times.

**Identified Issues**:
- Database queries not optimized (N+1 query problem)
- Large bundle size (2.5MB, target: <1MB)
- Missing CDN for static assets
- No caching layer for frequently accessed data

**Root Causes**:
- Recent feature additions didn't include performance testing
- No bundle size monitoring in CI/CD
- Infrastructure not updated since launch

**Proposed Solutions**:
1. Add database indexes and optimize queries
2. Implement code splitting and lazy loading
3. Set up CloudFront CDN
4. Add Redis caching layer
5. Establish performance budgets in CI

---

### 4. Team Capacity Planning (10 min)

**Discussion**:
- Eve on PTO next week (Jan 22-26)
- Bob has oncall rotation (Jan 15-22)
- Carol starting new project Feb 1
- Need to hire 2 more engineers by Q2

**Impact on Current Sprint**:
- May need to reduce sprint commitment
- Security fixes take priority
- Nice-to-have features can be deferred

---

## Decisions Made

### ✅ Decision 1: Prioritize Security Fixes

**Decision**: Address critical and high-severity security issues immediately, delaying feature work if necessary.

**Rationale**: Security risks outweigh feature velocity. Customer trust is paramount.

**Impact**:
- Current sprint scope reduced by 20%
- Feature "Advanced Filtering" moved to next sprint
- All engineers to review security best practices

**Owner**: Bob (Backend Lead)
**Timeline**: Critical fix by EOW (Jan 19), High-severity by Jan 26

---

### ✅ Decision 2: Implement Performance Budgets

**Decision**: Add automated performance checks to CI/CD pipeline.

**Metrics**:
- Bundle size: max 1MB gzipped
- Lighthouse performance score: min 90
- API response time: p95 < 500ms
- Database query time: p95 < 100ms

**Impact**: PRs failing budgets will require performance review before merge.

**Owner**: Carol (Frontend Lead) + Bob (Backend Lead)
**Timeline**: Implement by Feb 1

---

### ✅ Decision 3: Hire Additional Engineers

**Decision**: Open 2 requisitions (1 Backend, 1 Frontend) for Q2 start.

**Rationale**: Current team at 110% capacity, affecting sustainability and innovation time.

**Next Steps**:
- David to work with recruiting on job descriptions
- Alice to define interview process
- Target start date: April 1

**Owner**: Alice (Engineering Manager)
**Timeline**: Job posts live by Jan 22

---

## Action Items

### Priority 1 (This Week)

- [ ] **[Bob]** Fix JWT rotation vulnerability
  - **Due**: Jan 19 (EOW)
  - **Acceptance Criteria**: JWT invalidated on password change, tested in staging
  - **Dependencies**: None
  - **Estimate**: 4 hours

- [ ] **[Carol]** Analyze bundle size and create reduction plan
  - **Due**: Jan 18
  - **Deliverable**: Document with specific reduction strategies
  - **Dependencies**: None
  - **Estimate**: 2 hours

- [ ] **[Alice]** Share security audit report with team
  - **Due**: Jan 16 (today)
  - **Format**: Slack #engineering + detailed Confluence doc
  - **Dependencies**: None
  - **Estimate**: 30 minutes

### Priority 2 (This Sprint - by Jan 26)

- [ ] **[Bob]** Implement rate limiting on auth endpoints
  - **Due**: Jan 26
  - **Acceptance Criteria**:
    - Max 5 login attempts per 15 minutes
    - Clear error messages to users
    - Documented in API docs
  - **Dependencies**: None
  - **Estimate**: 1 day

- [ ] **[David]** Set up automated dependency updates (Renovate)
  - **Due**: Jan 26
  - **Acceptance Criteria**:
    - Auto-PR for patch updates
    - Weekly digest for minor updates
    - Manual review for major updates
  - **Dependencies**: DevOps approval
  - **Estimate**: 4 hours

- [ ] **[Carol]** Implement code splitting for dashboard
  - **Due**: Jan 26
  - **Acceptance Criteria**: Reduce initial bundle from 2.5MB to <1MB
  - **Dependencies**: Bundle analysis complete
  - **Estimate**: 2 days

### Priority 3 (Next Sprint - by Feb 9)

- [ ] **[Bob]** Add database indexes and optimize queries
  - **Due**: Feb 9
  - **Acceptance Criteria**: N+1 queries eliminated, p95 query time <100ms
  - **Dependencies**: Performance testing environment
  - **Estimate**: 3 days

- [ ] **[DevOps - Taylor]** Set up CloudFront CDN for static assets
  - **Due**: Feb 9
  - **Acceptance Criteria**: All images/CSS/JS served from CDN
  - **Dependencies**: AWS account access
  - **Estimate**: 1 day

- [ ] **[Bob + Carol]** Implement performance budgets in CI
  - **Due**: Feb 1
  - **Acceptance Criteria**: CI fails if budgets exceeded
  - **Dependencies**: Metrics defined
  - **Estimate**: 1 day

### Future / Parking Lot

- [ ] **[TBD]** Evaluate 2FA implementation
  - **Due**: TBD (separate discussion needed)
  - **Owner**: To be assigned
  - **Note**: Schedule dedicated security features meeting

- [ ] **[Alice]** Complete hiring process
  - **Due**: Target April 1 start dates
  - **Milestones**:
    - Jan 22: Job posts live
    - Feb 15: First round interviews
    - Mar 1: Final candidates selected
    - Apr 1: Start date

---

## Key Metrics & Data

**Performance Baseline (before fixes)**:
- Dashboard load time: 4.2s (target: <2s)
- Bundle size: 2.5MB (target: <1MB)
- API p95 response time: 850ms (target: <500ms)
- Database query p95: 340ms (target: <100ms)

**Security Audit Summary**:
- Critical issues: 1
- High severity: 1
- Medium severity: 3
- Low severity: 5

**Team Capacity (Current Sprint)**:
- Total story points: 45
- Committed: 50 (110% capacity)
- Recommended reduction: 10 points
- New commitment: 40 points

---

## Parking Lot

Items discussed but deferred to later:

1. **Two-Factor Authentication (2FA)**
   - Needs: Security team input, user research
   - Timeline: Discuss in Q2 planning
   - Owner: TBD

2. **Mobile App Marketing Strategy**
   - Needs: Product and marketing alignment
   - Timeline: After beta completion
   - Owner: David (Product)

3. **Team Offsite Planning**
   - Needs: Budget approval
   - Timeline: Q2 (April-June)
   - Owner: Alice

---

## Questions & Answers

**Q**: Should we pause new features entirely for security fixes?
**A**: No, but security takes priority. Reduce scope but maintain momentum.

**Q**: Can we hire contractors for short-term capacity?
**A**: Parking lot - discuss budget and approval process with leadership.

**Q**: Who will handle performance monitoring post-implementation?
**A**: Bob and Carol will set up, DevOps will maintain dashboards.

**Q**: What's our rollback plan if CDN causes issues?
**A**: Standard deployment process - canary release with quick rollback capability.

---

## Follow-Up Items

- **Next meeting**: Feb 1, 2024 (2 weeks) - Progress check on action items
- **Alice** to send summary email to broader engineering team by EOD
- **Bob** to schedule security fix review with Frank next week
- **Carol** to present performance improvements at next all-hands
- **All attendees** to review and add any missing items by Jan 16 EOD

---

## Related Resources

- [Security Audit Full Report](https://confluence.company.com/security-audit-jan-2024)
- [Q1 OKR Dashboard](https://jira.company.com/okrs/2024-q1)
- [Performance Metrics Dashboard](https://datadog.company.com/dashboard/performance)
- [Team Capacity Planning Sheet](https://docs.google.com/spreadsheets/capacity-2024)

---

## Notes for Next Meeting

- Review all action items completion status
- Performance metrics comparison (before/after)
- Security audit remediation verification
- Hiring pipeline update
- Team velocity assessment

---

**Notes Compiled By**: [Your Name]
**Shared With**: engineering@company.com, #engineering
**Last Updated**: January 15, 2024 4:30 PM
```

### Sprint Planning Notes Template

```markdown
# Sprint Planning - Sprint 24

**Date**: January 15, 2024
**Sprint Duration**: Jan 15 - Jan 26 (2 weeks)
**Team**: Engineering (12 members)

---

## Sprint Goal

**Primary Goal**: Resolve critical security vulnerabilities while maintaining 80% of planned feature velocity.

**Success Metrics**:
- All critical & high-severity security issues resolved
- At least 2 of 3 planned features completed
- Zero production incidents
- Team satisfaction score >7/10

---

## Capacity Planning

### Team Availability

**Full Availability** (10 days):
- Alice, Bob, Carol, David, Grace, Henry, Ivy, Jack, Kate, Liam, Maya, Noah

**Reduced Availability**:
- Eve: Out Jan 22-26 (50% capacity = 5 days)
- Bob: Oncall Jan 15-22 (80% capacity = 8 days)

**Total Capacity**: 126 person-days
**Available Story Points**: 45 points (based on team velocity)

### Commitments & Risks

**Committed**: 40 points
**Stretch Goals**: 5 points

**Risks**:
- Security fixes may take longer than estimated
- Dependencies on external security team review
- Oncall interruptions may reduce Bob's availability further

---

## Backlog Refinement

### Carried Over from Last Sprint

- [JIRA-234] Advanced filtering UI (5 points) - 80% complete
  - **Status**: Blocked on API endpoint (Bob to unblock)
  - **Carry forward**: Yes, complete in first 3 days

### New Work - Security (Priority 1)

- [SEC-001] Fix JWT rotation on password change (3 points) - **CRITICAL**
  - **Owner**: Bob
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - JWT invalidated immediately on password change
    - All active sessions terminated
    - User re-authentication required
    - Unit & integration tests
    - Security team sign-off

- [SEC-002] Implement auth endpoint rate limiting (5 points) - **HIGH**
  - **Owner**: Bob + Grace
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - 5 login attempts per 15 minutes per IP
    - Clear error messages (429 status)
    - Logging for monitoring
    - Documentation updated

- [SEC-003] Update vulnerable dependencies (2 points) - **MEDIUM**
  - **Owner**: David
  - **Dependencies**: Renovate setup
  - **Acceptance Criteria**:
    - All critical & high CVEs patched
    - Tests pass after updates
    - No breaking changes introduced

### New Work - Performance (Priority 2)

- [PERF-101] Bundle size reduction - code splitting (8 points)
  - **Owner**: Carol + Maya
  - **Dependencies**: Bundle analysis complete
  - **Acceptance Criteria**:
    - Bundle reduced from 2.5MB to <1MB
    - Lazy loading for routes
    - Lighthouse score >90
    - No user-facing regressions

- [PERF-102] Database query optimization (5 points)
  - **Owner**: Bob + Ivy
  - **Dependencies**: Performance testing environment
  - **Acceptance Criteria**:
    - N+1 queries eliminated
    - Indexes added for slow queries
    - p95 query time <100ms
    - Load testing shows improvement

### New Work - Features (Priority 3)

- [FEAT-445] Order history export (CSV/PDF) (8 points)
  - **Owner**: Henry + Jack
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Users can export orders in CSV and PDF format
    - Filtered exports (date range, status)
    - Email delivery for large exports
    - Analytics tracking

- [FEAT-446] Email notification preferences (5 points) - **STRETCH GOAL**
  - **Owner**: Kate + Liam
  - **Dependencies**: Email service refactor
  - **Acceptance Criteria**:
    - Users can opt-in/out of notification types
    - Preferences persisted in database
    - Applied to all email sends
    - Admin can view user preferences

---

## Story Breakdown

### Sprint Commitment (40 points)

| ID | Story | Points | Owner | Priority |
|----|-------|--------|-------|----------|
| JIRA-234 | Advanced filtering (carry-over) | 5 | Carol | P1 |
| SEC-001 | JWT rotation fix | 3 | Bob | P1 |
| SEC-002 | Auth rate limiting | 5 | Bob, Grace | P1 |
| SEC-003 | Dependency updates | 2 | David | P2 |
| PERF-101 | Bundle size reduction | 8 | Carol, Maya | P2 |
| PERF-102 | Query optimization | 5 | Bob, Ivy | P2 |
| FEAT-445 | Order export | 8 | Henry, Jack | P3 |
| FEAT-446 | Email preferences | 5 | Kate, Liam | Stretch |

### Not Committed (Future Sprints)

- [FEAT-447] Product recommendations (13 points) - Too large, needs breakdown
- [FEAT-448] Wishlist social sharing (5 points) - Lower priority
- [INFRA-102] CDN setup (3 points) - Blocked on DevOps capacity

---

## Dependencies & Blockers

### Current Blockers
1. **JIRA-234**: Waiting on API endpoint (Bob to complete by Jan 16)
2. **FEAT-445**: Waiting on legal review of data export policies (escalated to David)

### External Dependencies
- Security team review (SEC-001) - scheduled for Jan 19
- DevOps support for performance testing environment (PERF-102)

### Cross-Team Dependencies
None identified

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Security fixes take longer | Sprint goal missed | Medium | Buffer in estimates, daily check-ins |
| Oncall interrupts Bob | Reduced capacity | High | Pair programming, knowledge sharing |
| Performance tests reveal more issues | Scope creep | Medium | Strict scope, defer non-critical fixes |
| Legal blocks export feature | Feature delayed | Low | Escalate early, have backup feature ready |

---

## Definition of Done

A story is "Done" when:
- [ ] Code written and reviewed (minimum 1 approval)
- [ ] Unit tests written and passing
- [ ] Integration tests passing (if applicable)
- [ ] Manually tested in staging environment
- [ ] Documentation updated (API docs, user guides)
- [ ] Accessible to screen readers (frontend)
- [ ] No new console errors or warnings
- [ ] Performance impact measured (if relevant)
- [ ] Security review completed (for security stories)
- [ ] Product owner acceptance

---

## Action Items

- [ ] **[Bob]** Unblock JIRA-234 API endpoint by EOD Jan 16
- [ ] **[David]** Follow up with legal on export policy by Jan 17
- [ ] **[Alice]** Request DevOps support for performance testing environment
- [ ] **[Carol]** Complete bundle analysis and share findings by Jan 16
- [ ] **[All]** Update Jira tickets with detailed subtasks by EOD Jan 15
- [ ] **[Alice]** Schedule security review meeting with Frank for Jan 19

---

## Team Commitments

**What we're committing to**:
- Deliver all Priority 1 security fixes
- Complete at least 2 of 3 features (filtering + export OR filtering + performance)
- Maintain code quality and test coverage
- Support each other and ask for help early

**What we're NOT committing to**:
- New feature requests during sprint
- Scope changes after Sprint Day 3
- 100% velocity (realistic goal: 90%)

---

## Notes & Discussion

**Team Concerns**:
- Bob: Worried about balancing oncall and security fixes
  - **Mitigation**: Grace to pair on rate limiting, team to provide oncall backup
- Carol: Bundle reduction might uncover more issues
  - **Mitigation**: Timebox to 8 points, defer additional optimizations

**Improvements from Last Sprint**:
- Better estimation (last sprint: 55% accuracy, goal: 70%)
- Earlier blocker identification
- More pair programming

**Retrospective Highlights**:
- ✅ Great collaboration on payment feature
- ✅ Improved PR review turnaround time
- ⚠️ Need better documentation for complex features
- ⚠️ Communication gaps on blocking issues

---

## Daily Standup Schedule

**Time**: 10:00 AM EST, Monday/Wednesday/Friday
**Duration**: 15 minutes max
**Format**: Async in Slack on Tuesday/Thursday

**Standup Questions**:
1. What did you accomplish since last standup?
2. What are you working on today?
3. Any blockers or help needed?

---

## Sprint Review & Demo Plan

**Date**: January 26, 2024, 3:00 PM
**Duration**: 1 hour
**Attendees**: Engineering + Product + Design + Stakeholders

**Demo Order**:
1. Security improvements (Bob) - 10 min
2. Performance improvements (Carol) - 10 min
3. Order export feature (Henry) - 10 min
4. Advanced filtering (Carol) - 5 min
5. Metrics & outcomes (Alice) - 5 min
6. Q&A - 20 min

---

## Resources

- [Sprint 24 Jira Board](https://jira.company.com/sprint/24)
- [Team Capacity Sheet](https://docs.google.com/spreadsheets/capacity)
- [Performance Dashboard](https://datadog.company.com/performance)
- [Security Audit Report](https://confluence.company.com/security-audit)

---

**Notes By**: Alice (Engineering Manager)
**Sprint Kickoff**: January 15, 2024, 1:00 PM
**Next Planning**: January 29, 2024, 1:00 PM
```

### Retrospective Notes Template

```markdown
# Sprint 23 Retrospective

**Date**: January 12, 2024
**Sprint**: Sprint 23 (Dec 25 - Jan 12)
**Facilitator**: Alice
**Attendees**: All engineering team members (12/12 present)

---

## Sprint Overview

**Goal**: Launch payment integration and improve checkout flow
**Outcome**: ✅ Partially achieved - Payment launched, checkout improvements deferred

**Metrics**:
- **Velocity**: 35/45 points completed (78%)
- **Stories Completed**: 7/10
- **Bugs Found**: 3 (2 in QA, 1 in production)
- **Team Satisfaction**: 7.2/10

---

## What Went Well ✅

### 1. Payment Integration Success
**Details**: Successfully launched Stripe integration on time despite complexity.

**Why it worked**:
- Early involvement of security team
- Thorough testing (unit, integration, manual)
- Good collaboration between backend and frontend
- Clear documentation

**Shoutouts**:
- Bob for excellent API design
- Carol for smooth frontend integration
- Frank (security) for quick turnaround on reviews

**Keep doing**:
- Security reviews before implementation (not after)
- Cross-functional pairing sessions
- Comprehensive testing strategy

---

### 2. Improved PR Review Speed
**Data**: Average PR review time decreased from 18 hours to 8 hours

**Why it improved**:
- Implemented 24-hour review SLA
- Smaller PRs (average -40% in size)
- Better PR descriptions with context

**Impact**:
- Faster iteration
- Less context switching
- Better team morale

**Keep doing**:
- Maintain small PR sizes
- Detailed PR descriptions
- Priority labels for urgent reviews

---

### 3. Better Communication During Holiday Season
**Details**: Maintained productivity despite team members on PTO

**What worked**:
- Clear PTO calendar
- Documented handoffs
- Daily async standups when people out
- Cross-training before holidays

**Keep doing**:
- PTO planning 2 weeks in advance
- Document all ongoing work
- Identify backup owners for critical items

---

## What Didn't Go Well ⚠️

### 1. Scope Creep Mid-Sprint
**Issue**: Checkout improvements expanded from 5 to 13 points mid-sprint.

**Impact**:
- Deferred to next sprint (incomplete work)
- Pushed team to 120% capacity
- Caused stress and overtime

**Root causes**:
- Product requirements not fully defined
- Underestimated complexity
- Didn't say "no" to scope additions

**Action items**:
- [ ] **[Alice + David]** Define "scope freeze" policy (no changes after Day 3)
- [ ] **[Team]** More thorough story breakdown in planning
- [ ] **[Alice]** Empower team to push back on scope creep

**Owner**: Alice
**Due**: Before next sprint planning

---

### 2. Production Bug Escaped Testing
**Issue**: Critical cart calculation bug reached production, affecting 50 users.

**Impact**:
- Emergency hotfix required
- User complaints
- Lost revenue (~$500)
- Team confidence shaken

**Root cause**: Edge case not covered in test scenarios (discount + tax interaction)

**Timeline**:
- Deployed: Jan 5, 3pm
- Detected: Jan 6, 10am (19 hours later)
- Fixed: Jan 6, 2pm (4 hours to fix)

**Action items**:
- [ ] **[Bob + Carol]** Add integration tests for cart calculations
- [ ] **[Team]** Improve staging environment to match production data
- [ ] **[Alice]** Implement canary deployments (5% rollout first)
- [ ] **[Team]** Add monitoring alerts for cart calculation anomalies

**Owner**: Bob (technical), Alice (process)
**Due**: Jan 20

---

### 3. Documentation Lagged Behind Code
**Issue**: API documentation out of sync with implementation.

**Impact**:
- Frontend team confused by undocumented changes
- Time wasted debugging
- Duplicate questions in Slack

**Examples**:
- Payment API changed response format (undocumented)
- New error codes added but not in docs
- Deprecated endpoints still in documentation

**Action items**:
- [ ] **[Bob]** Update API docs as part of Definition of Done
- [ ] **[David]** Set up automated API doc generation from code
- [ ] **[Team]** Include doc review in PR checklist
- [ ] **[Carol]** Create frontend integration guide

**Owner**: Bob (docs), David (automation)
**Due**: Jan 26

---

## Parking Lot 🅿️

**Items discussed but require separate meetings**:

1. **Team growth and hiring**
   - Discussion: Current capacity insufficient for roadmap
   - Next steps: Schedule with leadership
   - Owner: Alice

2. **Improving staging environment**
   - Discussion: Needs to better match production
   - Next steps: Evaluate costs and approach
   - Owner: David + DevOps

3. **Tech debt prioritization**
   - Discussion: When to tackle growing tech debt
   - Next steps: Create tech debt backlog and scoring system
   - Owner: Bob (tech lead)

---

## Action Items Summary

### High Priority (Next Sprint)

- [ ] **[Alice + David]** Document scope freeze policy
  - **Due**: Jan 15 (before planning)
  - **Success criteria**: Written policy shared with team

- [ ] **[Bob]** Add comprehensive cart calculation tests
  - **Due**: Jan 20
  - **Success criteria**: 100% coverage of cart logic, edge cases included

- [ ] **[Alice]** Implement canary deployment process
  - **Due**: Jan 20
  - **Success criteria**: All production deploys go through canary

### Medium Priority (This Month)

- [ ] **[David]** Automate API documentation generation
  - **Due**: Jan 26
  - **Success criteria**: Docs auto-updated on every merge

- [ ] **[Bob + Carol]** Create cart monitoring alerts
  - **Due**: Jan 26
  - **Success criteria**: Alert fires for calculation anomalies

- [ ] **[Team]** Update Definition of Done with documentation requirement
  - **Due**: Jan 15
  - **Success criteria**: All PRs include doc updates

### Low Priority (Future)

- [ ] **[Alice]** Schedule hiring discussion with leadership
  - **Due**: End of January
  - **Success criteria**: Approval for 2 additional headcount

- [ ] **[Bob]** Create tech debt backlog
  - **Due**: End of Q1
  - **Success criteria**: Prioritized list with estimated effort

---

## Metrics & Data

### Velocity Trend
```
Sprint 20: 40/50 (80%)
Sprint 21: 42/45 (93%) ⬆️
Sprint 22: 38/45 (84%) ⬇️
Sprint 23: 35/45 (78%) ⬇️
```
**Trend**: Declining velocity, investigate in next retro

### Quality Metrics
```
Sprint 21: 0 production bugs ✅
Sprint 22: 1 production bug (low severity) ⚠️
Sprint 23: 1 production bug (critical) 🔴
```
**Trend**: Quality slipping, need better testing

### Team Satisfaction
```
Sprint 21: 8.1/10
Sprint 22: 7.8/10
Sprint 23: 7.2/10
```
**Concerns**: Scope creep and production bug affecting morale

---

## Team Feedback (Anonymous)

**Positive**:
- "Great collaboration on payment feature"
- "PR reviews are much faster now"
- "Appreciate async standups during holidays"

**Constructive**:
- "Need to push back on mid-sprint scope changes"
- "Staging environment doesn't match production enough"
- "Documentation is always an afterthought"
- "Would like more pair programming opportunities"

---

## Experiments for Next Sprint

### Experiment 1: Scope Freeze Policy
**Hypothesis**: Implementing scope freeze after Day 3 will improve velocity and reduce stress.
**Measurement**: Track mid-sprint scope changes and team satisfaction.
**Duration**: 2 sprints

### Experiment 2: Mandatory Pair Programming Hours
**Hypothesis**: 2 hours/week of pair programming will improve code quality and knowledge sharing.
**Measurement**: Track bugs found and team feedback.
**Duration**: 1 sprint (trial)

### Experiment 3: Documentation-First for API Changes
**Hypothesis**: Writing docs before code will improve API design and reduce integration issues.
**Measurement**: Track frontend questions about API changes.
**Duration**: 1 sprint (trial)

---

## Appreciations 🎉

**Team Shoutouts**:
- 👏 **Bob**: For leading complex payment integration and staying calm under pressure
- 👏 **Carol**: For excellent frontend work and helpful PR reviews
- 👏 **Grace**: For jumping in to help with testing when we were behind
- 👏 **Everyone**: For maintaining productivity during holiday season

---

## Next Steps

1. **Action item owners** review and add details by EOD today
2. **Alice** to follow up on high-priority items daily
3. **Team** to try new experiments and provide feedback
4. **Next retrospective**: January 26, 2024 (after Sprint 24)

---

**Retro Format Used**: Start/Stop/Continue + Data Review
**Duration**: 1 hour
**Notes By**: Alice
**Shared With**: #engineering, engineering@company.com
```

## Usage Examples

```
@meeting-notes
@meeting-notes --type standup
@meeting-notes --type planning
@meeting-notes --type retrospective
@meeting-notes --type decision-log
@meeting-notes --extract-action-items
@meeting-notes --format markdown
```

## Best Practices

### During the Meeting

**Active Listening**:
- Focus on key points, not verbatim transcription
- Note tone and emphasis
- Capture decisions and action items in real-time
- Mark unclear items for follow-up

**Ask Clarifying Questions**:
- "Can you restate the action item with an owner?"
- "What's the deadline for this?"
- "Is this a decision or a discussion?"
- "Should this be a separate action item?"

**Use Templates**:
- Prepare template before meeting
- Fill in as discussion progresses
- Don't get bogged down in formatting

### After the Meeting

**Share Promptly**:
- Send within 24 hours (ideally within 2 hours)
- Include all attendees + stakeholders
- Post in relevant Slack channels
- Archive in team wiki/knowledge base

**Make Action Items Trackable**:
- Create Jira tickets from action items
- Set due dates and assignees
- Link back to meeting notes
- Follow up on overdue items

**Enable Searchability**:
- Use consistent naming: "[Meeting Type] - [Topic] - [Date]"
- Tag with relevant labels
- Include keywords in summary
- Link related documents

### Structure and Format

**Use Scannable Formatting**:
- Clear headings and sections
- Bullet points over paragraphs
- Tables for data
- Highlight decisions and action items
- Use emojis sparingly for visual cues (✅ ⚠️ 🔴)

**Be Concise**:
- Focus on outcomes, not discussions
- Summarize long debates
- Link to detailed docs instead of repeating
- Remove fluff and filler

**Make It Actionable**:
- Every action item has owner
- Every action item has due date
- Every decision has rationale
- Every question has answer (or marked as TBD)

## Notes

- Good meeting notes save more time than they take
- Action items without owners don't get done
- Decisions without rationale get re-litigated
- Prompt sharing is critical for async teams
- Templates ensure consistency and completeness
- Track action items in project management tools
- Review notes before next meeting
- Archive for future reference and onboarding
- Clear notes reduce need for follow-up meetings
- Include enough context for people who weren't there
