---
name: brainstorming-features
description: Facilitates creative ideation sessions for mobile and web app features, generating structured ideas with user stories, technical considerations, and implementation suggestions. Use when planning new features, exploring product direction, generating app ideas, feature discovery, product brainstorming, or when user mentions 'brainstorm', 'ideate', 'app ideas', or 'feature suggestions'.
---

# Brainstorming Features

## Overview

This skill helps generate, explore, and structure feature ideas for mobile and web applications through systematic ideation workflows. It produces actionable, well-organized feature concepts with technical context and user value.

## When to Use

- Planning new app features or product directions
- Exploring feature possibilities for existing apps
- Generating ideas for MVP (Minimum Viable Product)
- Feature discovery workshops
- Product roadmap planning sessions
- Competitive feature analysis
- User problem-solving sessions

## Brainstorming Workflow

### 1. Context Gathering

Before generating ideas, understand:

**Project Context:**
- App type (mobile, web, desktop, PWA)
- Tech stack (React Native, Next.js, etc.)
- Target users and personas
- Core value proposition
- Existing features (if applicable)

**Brainstorming Scope:**
- Specific feature area or general exploration
- Problem to solve or opportunity to capture
- Constraints (technical, budget, timeline)
- Success metrics

### 2. Idea Generation Methods

**Method A - Problem-First:**
1. Identify user pain points
2. Generate solutions addressing each pain point
3. Rank by impact vs. effort
4. Select top 3-5 for detailed exploration

**Method B - Opportunity-First:**
1. List market opportunities or trends
2. Generate features leveraging opportunities
3. Assess feasibility and differentiation
4. Select promising concepts

**Method C - Competitive Analysis:**
1. Review competitor features
2. Identify gaps and improvements
3. Generate unique variations or enhancements
4. Prioritize by competitive advantage

**Method D - User Journey Mapping:**
1. Map current user journey
2. Identify friction points
3. Generate features smoothing the journey
4. Test against user flow improvements

### 3. Feature Structure Template

For each feature idea, provide:

```markdown
## Feature: [Feature Name]

**One-line description:**
[Brief, compelling description in 10-15 words]

**Problem it solves:**
[User pain point or opportunity addressed]

**Target users:**
[Primary and secondary user personas]

**User story:**
As a [user type], I want to [action] so that [benefit].

**Key capabilities:**
- Capability 1
- Capability 2
- Capability 3

**Technical considerations:**
- Technology/library suggestions
- Integration points
- Data requirements
- Potential challenges

**Implementation complexity:**
[Low / Medium / High] - [Brief justification]

**Expected impact:**
[User value and business value]

**Success metrics:**
- Metric 1 (e.g., engagement increase)
- Metric 2 (e.g., task completion rate)
```

### 4. Idea Refinement

After initial generation, refine ideas by:

**Feasibility Check:**
- Technical achievability with current stack
- Resource requirements (time, team, infrastructure)
- Dependencies on other features or systems

**Value Assessment:**
- User value score (1-10)
- Business value score (1-10)
- Effort estimate (person-days or story points)

**Prioritization Matrix:**
```
High Value, Low Effort  → Do First (Quick Wins)
High Value, High Effort → Strategic Investments
Low Value, Low Effort   → Consider Later
Low Value, High Effort  → Avoid
```

### 5. Output Formats

**Format 1 - Feature Brief (Detailed):**
Use the full template above for 3-5 top features

**Format 2 - Feature List (Concise):**
```markdown
1. **[Feature Name]** - [One-line description] [Complexity: Low/Med/High]
2. **[Feature Name]** - [One-line description] [Complexity: Low/Med/High]
...
```

**Format 3 - Feature Roadmap:**
Organize by phases or sprints:
```markdown
### Phase 1 - Foundation (Sprint 1-2)
- Feature A (enables core workflow)
- Feature B (critical user need)

### Phase 2 - Enhancement (Sprint 3-4)
- Feature C (improves experience)
- Feature D (adds value)

### Phase 3 - Advanced (Sprint 5+)
- Feature E (differentiator)
- Feature F (scale optimization)
```

## Examples

### Example 1 - Mobile Note-Taking App

**Context:** React Native note-taking app for nursing students

**Brainstorm Request:** "Generate 5 feature ideas to improve study efficiency"

**Output:**

```markdown
## Feature: AI-Powered Flashcard Generation

**One-line description:**
Automatically create study flashcards from notes using AI term extraction

**Problem it solves:**
Students spend hours manually creating flashcards instead of studying

**Target users:**
Nursing students preparing for exams and clinical rotations

**User story:**
As a nursing student, I want my notes automatically converted to flashcards so that I can focus on studying instead of card creation.

**Key capabilities:**
- Auto-detect medical terms and concepts
- Generate question-answer pairs from context
- Spaced repetition scheduling
- Manual edit and refinement

**Technical considerations:**
- OpenAI API for term extraction
- IndexedDB/Dexie for local flashcard storage
- Background processing for large notes
- Offline-first sync with Firestore

**Implementation complexity:**
Medium - Requires AI integration and smart parsing logic, but leverages existing note structure

**Expected impact:**
- 70% reduction in flashcard creation time
- Increased study time availability
- Higher exam preparation quality

**Success metrics:**
- Flashcards generated per note
- User edits to auto-generated cards (lower = better accuracy)
- Study session frequency increase
```

### Example 2 - E-Commerce Platform

**Context:** Next.js e-commerce platform, early stage

**Brainstorm Request:** "Brainstorm checkout flow improvements"

**Output (Concise Format):**

```markdown
1. **One-Click Reorder** - Save previous orders as templates for instant reordering [Complexity: Low]

2. **Smart Address Autocomplete** - Google Places API integration for accurate shipping addresses [Complexity: Low]

3. **Guest Checkout Express** - No account required, optional account creation post-purchase [Complexity: Medium]

4. **Cart Recovery Emails** - Automated emails for abandoned carts with incentives [Complexity: Medium]

5. **Buy Now Pay Later Integration** - Klarna/Afterpay integration for flexible payments [Complexity: High]

6. **Multi-Item Gift Options** - Individual gift wrapping and messages per item [Complexity: Medium]

7. **Saved Payment Methods** - Tokenized card storage with Stripe for returning customers [Complexity: Medium]
```

### Example 3 - Fitness Tracking App

**Context:** Exploring gamification features

**Brainstorm Request:** "Generate gamification ideas for workout motivation"

**Output (Feature Brief):**

```markdown
## Feature: Achievement Streak Tracker

**One-line description:**
Visual streak counter with milestone rewards for consecutive workout days

**Problem it solves:**
Users lack motivation to maintain consistent workout routines

**Target users:**
Casual fitness enthusiasts seeking habit formation

**User story:**
As a user, I want to see my workout streak and earn rewards so that I stay motivated to exercise daily.

**Key capabilities:**
- Daily streak counter with flame icon visualization
- Milestone badges (7-day, 30-day, 100-day streaks)
- Streak freeze option (1 per week)
- Social sharing of achievements
- Push notifications for streak risk

**Technical considerations:**
- Local notification scheduling (Expo Notifications)
- Streak calculation with timezone handling
- Badge icon assets and animations
- Firebase Cloud Functions for streak validation
- Social sharing via React Native Share

**Implementation complexity:**
Low - Simple date tracking logic with notification system

**Expected impact:**
- 40% increase in daily active users
- 25% improvement in 30-day retention
- Higher social engagement and viral growth

**Success metrics:**
- % users with active streaks
- Average streak length
- Notification engagement rate
- Social shares per achievement
```

## Best Practices

### Do:
- Start broad, then narrow to specific features
- Consider technical feasibility early
- Include user value in every idea
- Provide clear prioritization rationale
- Use concrete examples over abstract concepts
- Balance innovation with practicality

### Don't:
- Generate ideas without context
- Ignore technical constraints
- Overlook existing features or patterns
- Skip impact assessment
- Propose features without user stories
- Forget about implementation complexity

## Brainstorming Triggers

Respond to these phrases by activating this skill:
- "Brainstorm features for..."
- "Generate app ideas for..."
- "What features could we add to..."
- "Help me ideate on..."
- "Feature discovery session for..."
- "Explore possibilities for..."

## Iteration and Refinement

After initial brainstorming:

1. **User Feedback:** Validate ideas against actual user needs
2. **Technical Review:** Assess implementation details with engineering team
3. **Design Exploration:** Create mockups or wireframes for top ideas
4. **MVP Scoping:** Identify minimum feature set for initial release
5. **Roadmap Planning:** Sequence features based on dependencies and value

## Additional Resources

For further refinement, consider:
- **references/feature-templates.md** - More detailed templates for specific feature types
- **references/prioritization-frameworks.md** - Advanced prioritization methods (RICE, MoSCoW, Kano)
