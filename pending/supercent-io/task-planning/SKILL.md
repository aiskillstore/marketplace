---
name: task-planning
description: Plan and organize software development tasks effectively. Use when breaking down features, creating user stories, or planning sprints. Handles task breakdown, user stories, acceptance criteria, and backlog management.
metadata:
  tags: task-planning, user-stories, backlog, sprint-planning, agile
  platforms: Claude, ChatGPT, Gemini
---


# Task Planning


## When to use this skill

- **Feature development**: Break down a new feature into small tasks
- **Sprint Planning**: Select work to include in the sprint
- **Backlog Grooming**: Clean up the backlog and set priorities

## Instructions

### Step 1: Write User Stories (INVEST)

**INVEST principles**:
- **I**ndependent: Independent
- **N**egotiable: Negotiable
- **V**aluable: Valuable
- **E**stimable: Estimable
- **S**mall: Small
- **T**estable: Testable

**Template**:
```markdown
## User Story: [title]

**As a** [user type]
**I want** [feature]
**So that** [value/reason]

### Acceptance Criteria
- [ ] Given [context] When [action] Then [outcome]
- [ ] Given [context] When [action] Then [outcome]
- [ ] Given [context] When [action] Then [outcome]

### Technical Notes
- API endpoint: POST /api/users
- Database: users table
- Frontend: React component

### Estimation
- Story Points: 5
- T-Shirt: M

### Dependencies
- User authentication must be completed first

### Priority
- MoSCoW: Must Have
- Business Value: High
```

**Example**:
```markdown
## User Story: User Registration

**As a** new visitor
**I want** to create an account
**So that** I can access personalized features

### Acceptance Criteria
- [ ] Given valid email and password When user submits form Then account is created
- [ ] Given duplicate email When user submits Then error message is shown
- [ ] Given weak password When user submits Then validation error is shown
- [ ] Given successful registration When account created Then welcome email is sent

### Technical Notes
- Hash password with bcrypt
- Validate email format
- Send welcome email via SendGrid
- Store user in PostgreSQL

### Estimation
- Story Points: 5

### Dependencies
- Email service integration (#123)

### Priority
- MoSCoW: Must Have
```

### Step 2: Decompose Epic → Story → Task

```markdown
## Epic: User Management System

### Story 1: User Registration
- **Points**: 5
- Tasks:
  - [ ] Design registration form UI (2h)
  - [ ] Create POST /api/users endpoint (3h)
  - [ ] Implement email validation (1h)
  - [ ] Add password strength checker (2h)
  - [ ] Write unit tests (2h)
  - [ ] Integration testing (2h)

### Story 2: User Login
- **Points**: 3
- Tasks:
  - [ ] Design login form (2h)
  - [ ] Create POST /api/auth/login endpoint (2h)
  - [ ] Implement JWT token generation (2h)
  - [ ] Add "Remember Me" functionality (1h)
  - [ ] Write tests (2h)

### Story 3: Password Reset
- **Points**: 5
- Tasks:
  - [ ] "Forgot Password" UI (2h)
  - [ ] Generate reset token (2h)
  - [ ] Send reset email (1h)
  - [ ] Reset password form (2h)
  - [ ] Update password API (2h)
  - [ ] Tests (2h)
```

### Step 3: MoSCoW prioritization

```markdown
## Feature Prioritization (MoSCoW)

### Must Have (Sprint 1)
- User Registration
- User Login
- Basic Profile Page

### Should Have (Sprint 2)
- Password Reset
- Email Verification
- Profile Picture Upload

### Could Have (Sprint 3)
- Two-Factor Authentication
- Social Login (Google, GitHub)
- Account Deletion

### Won't Have (This Release)
- Biometric Authentication
- Multiple Sessions Management
```

### Step 4: Sprint Planning

```markdown
## Sprint 10 Planning

**Sprint Goal**: Complete user authentication system

**Duration**: 2 weeks
**Team Capacity**: 40 hours × 4 people = 160 hours
**Estimated Velocity**: 30 story points

### Selected Stories
1. User Registration (5 points) - Must Have
2. User Login (3 points) - Must Have
3. Password Reset (5 points) - Must Have
4. Email Verification (3 points) - Should Have
5. Profile Edit (5 points) - Should Have
6. JWT Refresh Token (3 points) - Should Have
7. Rate Limiting (2 points) - Should Have
8. Security Audit (4 points) - Must Have

**Total**: 30 points

### Sprint Backlog
- [ ] User Registration (#101)
- [ ] User Login (#102)
- [ ] Password Reset (#103)
- [ ] Email Verification (#104)
- [ ] Profile Edit (#105)
- [ ] JWT Refresh Token (#106)
- [ ] Rate Limiting (#107)
- [ ] Security Audit (#108)

### Definition of Done
- [ ] Code written and reviewed
- [ ] Unit tests passing (80%+ coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] QA approved
```

## Output format

### Task board structure

```
Backlog → To Do → In Progress → Review → Done

Backlog:
- Sorted by priority
- Groomed stories

To Do:
- Work selected for the sprint
- Owner assigned

In Progress:
- WIP Limit: 2 per person
- Work in progress

Review:
- Waiting for code review
- In QA testing

Done:
- Meets DoD
- Deployed
```

## Constraints

### Required rules (MUST)

1. **Clear AC**: Acceptance Criteria required
2. **Estimation done**: Assign points to every story
3. **Dependencies identified**: Specify prerequisite work

### Prohibited (MUST NOT)

1. **Stories too large**: Split anything 13+ points
2. **Vague requirements**: Avoid "improve" and "optimize"

## Best practices

1. **INVEST**: Write good user stories
2. **Definition of Ready**: Ready before sprint start
3. **Definition of Done**: Clear completion criteria

## References

- [User Story Guide](https://www.atlassian.com/agile/project-management/user-stories)
- [MoSCoW Prioritization](https://www.productplan.com/glossary/moscow-prioritization/)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Compatible platforms**: Claude, ChatGPT, Gemini

### Tags
`#task-planning` `#user-stories` `#backlog` `#sprint-planning` `#agile` `#project-management`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
