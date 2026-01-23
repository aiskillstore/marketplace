# Sprint Planning Reference

Quick reference for planning effective sprints and roadmaps.

## Sprint Duration Guidelines

**2-week sprints** (most common):
- 10 working days
- Good balance of planning and delivery
- Recommended for most teams

**1-week sprints**:
- 5 working days
- Fast feedback cycles
- Good for small teams or urgent projects

**3-week sprints**:
- 15 working days
- Longer planning horizon
- Good for complex features

## Sprint Capacity Planning

### Team Velocity
- Track completed deliverables per sprint
- Use last 3 sprints average
- Account for team size changes

### Capacity Rules
- Plan for 80% of available time
- Reserve 20% for meetings, bugs, unexpected work
- Factor in holidays and PTO

### Example Calculation
```
Team: 3 developers
Sprint: 2 weeks (10 days)
Total capacity: 3 × 10 = 30 developer-days
Realistic capacity: 30 × 0.8 = 24 developer-days
```

## Sprint Themes

Good sprint themes are:
- **Descriptive**: "Payment Integration" not "Sprint 1"
- **Goal-oriented**: Focus on outcome
- **Memorable**: Easy to reference in discussions

### Theme Examples
- Foundation / Setup / Infrastructure
- Core Features / MVP
- Polish / Optimization
- Testing / Bug Fixes
- Beta Launch / Production Release
- Performance / Security
- User Experience / Design
- Integration / API Development

## Task Guidelines

### Good Tasks
✅ Specific and measurable
✅ Can be completed in one sprint
✅ Has unique ticket code (T-001, T-002, etc.)
✅ Clear description of what to build
✅ Delivers user value

**Examples**:
- T-001: Stripe payment integration [ ]
- T-002: User profile editing [ ]
- T-003: Email notification system [ ]
- T-004: Mobile responsive checkout [ ]

### Avoid
❌ Vague tasks: "T-001: Work on backend"
❌ Too large: "T-001: Build entire platform"
❌ Technical jargon without context
❌ Dependencies unclear
❌ Missing ticket codes

### Task Numbering Best Practices
- Use 3-digit format: T-001, T-002, T-003
- Sequential across entire release (not per sprint)
- Never reuse codes, even for cancelled tasks
- Continue numbering from previous releases for consistency

## Sprint Dependencies

### Types of Dependencies
1. **Technical**: Feature B needs Feature A code
2. **Sequential**: Testing requires completed development
3. **External**: Third-party API access
4. **Resource**: Waiting for design assets

### Managing Dependencies
- Identify early in planning
- Document in sprint plan
- Schedule dependent sprints sequentially
- Have contingency plans

### Example
```
SPRINT-001: Build API endpoints
SPRINT-002: Connect frontend to API (depends on SPRINT-001)
SPRINT-003: Add authentication (can run parallel)
```

## Roadmap Best Practices

### Grouping Sprints
**By Quarter**:
```
Q1 2025: SPRINT-001 through SPRINT-006
Q2 2025: SPRINT-007 through SPRINT-012
```

**By Month**:
```
January: SPRINT-001, SPRINT-002
February: SPRINT-003, SPRINT-004
```

**By Phase**:
```
Phase 1 (Foundation): SPRINT-001 to SPRINT-003
Phase 2 (Features): SPRINT-004 to SPRINT-008
```

### Milestone Markers
Include key dates:
- Alpha release
- Beta release
- Feature freeze
- Production launch
- Major integrations

## Sprint Numbering

### Standard Format
- Use three digits: `SPRINT-001`, `SPRINT-002`
- Sequential across releases
- Never reuse numbers

### Multi-Project Numbering
Option 1: Project prefix
```
WEB-SPRINT-001
API-SPRINT-001
MOBILE-SPRINT-001
```

Option 2: Continue sequence
```
SPRINT-001: Web feature
SPRINT-002: API feature
SPRINT-003: Mobile feature
```

## Common Sprint Patterns

### MVP Pattern (3-4 sprints)
```
SPRINT-001: Core infrastructure
SPRINT-002: Essential features
SPRINT-003: Polish & testing
SPRINT-004: Launch preparation
```

### Feature Release Pattern (6 sprints)
```
SPRINT-001-002: Foundation
SPRINT-003-004: Feature development
SPRINT-005: Integration & testing
SPRINT-006: Beta & launch
```

### Continuous Delivery Pattern
```
SPRINT-001: Feature set A + deploy
SPRINT-002: Feature set B + deploy
SPRINT-003: Feature set C + deploy
```

## Release Planning Tips

### Prioritization
1. Must-have features first
2. High-value, low-effort next
3. Nice-to-have features last
4. Always include buffer sprint

### Risk Management
- Front-load risky/complex work
- Leave familiar tasks for later
- Plan demo/testing sprints
- Account for unknowns

### Communication
- Share roadmap with stakeholders
- Update after each sprint
- Highlight completed vs planned
- Adjust based on feedback

## Example Sprint Breakdown

### Small Feature (1-2 sprints)
```
SPRINT-001: User Authentication
**Tasks**:
- T-001: Login page implementation [ ]
- T-002: Registration form [ ]
- T-003: Password reset flow [ ]
- T-004: Session management [ ]
```

### Medium Feature (3-4 sprints)
```
SPRINT-001: Payment Foundation
**Tasks**:
- T-001: Payment provider setup [ ]
- T-002: Database schema design [ ]
- T-003: API endpoints [ ]

SPRINT-002: Payment UI
**Tasks**:
- T-004: Checkout flow [ ]
- T-005: Payment forms [ ]
- T-006: Confirmation screens [ ]

SPRINT-003: Testing & Polish
**Tasks**:
- T-007: Integration tests [ ]
- T-008: Error handling [ ]
- T-009: UX improvements [ ]
```

### Large Feature (6+ sprints)
```
SPRINT-001-002: Infrastructure (T-001 to T-008)
SPRINT-003-005: Core features (T-009 to T-025)
SPRINT-006: Integration (T-026 to T-030)
SPRINT-007: Testing (T-031 to T-035)
SPRINT-008: Beta launch (T-036 to T-040)
SPRINT-009: Production release (T-041 to T-045)
```
