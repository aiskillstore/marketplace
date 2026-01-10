# User Journey Diagram Reference

Complete guide for Mermaid user journey diagrams in Obsidian.

---

## Introduction

User journey diagrams visualize the steps a user takes to complete a specific task. They display the emotional experience at each step with satisfaction scores, and identify which actors (personas) are involved in each phase.

---

## Basic Structure

### Simple Journey

```mermaid
journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
    section Work
      Do work: 3: Me, Cat
      Have lunch: 2: Me
```

### Components

```
journey
    title [Title of the journey]
    section [Phase name]
      Task name: [score]: [actor(s)]
```

---

## Syntax Reference

### Title

Define the journey title:

```mermaid
journey
    title User Onboarding Process
```

### Sections

Group tasks into logical phases:

```mermaid
journey
    title Product Signup
    section Signup
      Create account: 4: User
    section Verification
      Verify email: 3: User
```

| Element | Purpose |
|---------|---------|
| `section name` | Phase or stage of the journey |
| Task definition | Individual step in the journey |

### Task Syntax

Define tasks with name, score, and actors:

```
Task name: <score>: <actor1>, <actor2>
```

| Component | Details | Example |
|-----------|---------|---------|
| Task name | Action description | `Submit form` |
| Score | 1-5 satisfaction | `4` (satisfied) |
| Actors | Who performs it | `User, Admin` |

### Score Meanings

| Score | Interpretation |
|-------|-----------------|
| `5` | Highly satisfied |
| `4` | Satisfied |
| `3` | Neutral |
| `2` | Unsatisfied |
| `1` | Very unsatisfied |

---

## Actors

### Defining Actors

Actors represent user personas or roles:

```mermaid
journey
    title User and Admin Interaction
    section Initial Contact
      User submits request: 4: User
      Admin receives notification: 4: Admin
    section Resolution
      Admin processes request: 3: Admin
      User receives update: 5: User
```

### Multiple Actors

Include actors in parentheses or as comma-separated list:

```mermaid
journey
    title Team Collaboration
    section Planning
      Define requirements: 4: PM, Dev
      Design solution: 3: Designer, Dev
    section Implementation
      Implement feature: 2: Dev
      Review code: 4: Dev, QA
```

---

## Practical Examples

### Example 1: Customer Support Journey

```mermaid
journey
    title Customer Support Experience
    section Contact Support
      Visit support page: 3: Customer
      Submit ticket: 2: Customer
    section Initial Response
      Support receives ticket: 3: Support Agent
      Send acknowledgment: 4: Support Agent
      Customer receives reply: 3: Customer
    section Resolution
      Agent troubleshoots: 3: Support Agent
      Customer tries solution: 4: Customer
      Issue resolved: 5: Customer
```

### Example 2: E-Commerce Checkout

```mermaid
journey
    title Online Shopping Checkout
    section Browse
      Search products: 4: Shopper
      View details: 4: Shopper
      Add to cart: 5: Shopper
    section Checkout
      Open cart: 4: Shopper
      Enter shipping address: 3: Shopper
      Select shipping method: 3: Shopper
      Enter payment info: 2: Shopper
    section Payment
      Process payment: 2: Payment System, Shopper
      Receive confirmation: 5: Shopper
    section Fulfillment
      Order preparation: 4: Warehouse
      Shipment dispatch: 5: Warehouse
      Delivery: 5: Shopper
```

### Example 3: Software Onboarding

```mermaid
journey
    title New User Onboarding
    section Signup
      Create account: 4: New User
      Set profile: 3: New User
    section Email Verification
      Check inbox: 2: New User
      Click link: 3: New User
      Verify email: 4: New User
    section Welcome Tour
      View intro: 3: New User
      Complete tutorial: 3: New User
    section First Use
      Create project: 4: New User
      Invite team member: 3: New User, Team Member
      Start collaboration: 5: New User
```

### Example 4: Mobile App User Flow

```mermaid
journey
    title Mobile Banking App Usage
    section App Launch
      Download app: 4: Mobile User
      Open app: 3: Mobile User
      Login: 2: Mobile User
    section Dashboard
      View balance: 5: Mobile User
      Check transactions: 4: Mobile User
    section Transfers
      Navigate to transfer: 3: Mobile User
      Enter recipient: 2: Mobile User
      Enter amount: 2: Mobile User
      Confirm transfer: 2: Mobile User
    section Confirmation
      Receive notification: 5: Mobile User
      View receipt: 5: Mobile User
```

### Example 5: Bug Reporting Workflow

```mermaid
journey
    title Bug Report Lifecycle
    section Report
      Encounter bug: 1: QA Tester
      Document issue: 3: QA Tester
      Submit report: 3: QA Tester
    section Triage
      Receive notification: 3: Developer
      Reproduce bug: 2: Developer
      Estimate effort: 3: Developer
    section Development
      Implement fix: 4: Developer
      Write tests: 4: Developer
      Submit PR: 4: Developer
    section Review
      Code review: 3: Code Reviewer
      Provide feedback: 2: Code Reviewer
      Approve PR: 5: Code Reviewer
    section Release
      Merge changes: 5: Developer
      Deploy to production: 4: DevOps Engineer
      Confirm fix: 5: QA Tester
```

---

## Advanced Features

### Comments

```mermaid
journey
    title Commented Journey
    section Setup
      %% Initial configuration
      Create account: 4: User
      %% Account ready
    section Usage
      Use feature: 3: User
```

### Long Task Names

Task names wrap automatically or can use line breaks:

```mermaid
journey
    title Long Task Names
    section Processing
      Validate form and check all fields for errors: 3: System
      Send email confirmation to user inbox: 4: System, User
```

### Section Organization

Organize related tasks within logical sections:

```mermaid
journey
    title Project Management Workflow
    section Planning
      Define scope: 4: PM
      Estimate timeline: 3: PM, Dev Lead
    section Execution
      Assign tasks: 4: PM
      Implement features: 3: Dev
      Test implementation: 3: QA
    section Delivery
      Deploy to production: 4: DevOps
      Monitor performance: 5: DevOps
      Get user feedback: 4: PM, Users
```

---

## Best Practices

### Organizing Sections

- Use logical workflow phases
- Group related tasks together
- Follow chronological order
- Use 3-5 sections maximum for clarity

### Scoring

- Be consistent with score meanings
- Lower scores indicate pain points to improve
- Higher scores indicate positive experiences
- Use full range (1-5) to show variation

### Actor Naming

- Keep actor names short and clear
- Use consistent naming across diagram
- Represent actual user roles or personas
- Include system actors when relevant (e.g., "Payment System")

---

## Styling with CSS Classes

```mermaid
journey
    title Styled User Journey
    section Initial
      First step: 4: User
      Second step: 3: Admin
```

---

## Obsidian Notes

**Viewport**: Very long journeys (20+ tasks) may exceed Obsidian viewport. Consider splitting into multiple diagrams.

**Satisfaction Scoring**: Use consistent scoring methodology. Lower scores highlight improvement opportunities.

**Actor Count**: Limit to 4-5 distinct actors for readability. Too many actors make the diagram cluttered.

**Section Names**: Keep section names short (1-2 words). Long names reduce space for tasks.

**Export**: PDF export renders diagrams as images. For external sharing, capture as PNG/SVG.

**Code Block Format**:
````
```mermaid
journey
    title My Journey
    section Phase
      Task: 5: User
```
````

---

## Quick Reference Table

| Element | Syntax | Example |
|---------|--------|---------|
| Diagram start | `journey` | `journey` |
| Title | `title text` | `title User Signup` |
| Section | `section name` | `section Verification` |
| Task | `name: score: actors` | `Submit form: 4: User` |
| Score 5 | `5` | Highly satisfied |
| Score 4 | `4` | Satisfied |
| Score 3 | `3` | Neutral |
| Score 2 | `2` | Unsatisfied |
| Score 1 | `1` | Very unsatisfied |
| Single actor | `Actor` | `User` |
| Multiple actors | `Actor1, Actor2` | `User, Admin` |
| Comment | `%% text` | `%% Setup phase` |
