# ADR Review Checklist

Use this checklist when reviewing Architecture Decision Records before accepting them.

## Pre-Review Checklist

Before distributing ADR for review, author should verify:

- [ ] **ADR Number**: Sequential 4-digit number assigned (check existing ADRs)
- [ ] **File Location**: Placed in `/docs/adr/` or `/architecture/decisions/`
- [ ] **File Naming**: Follows format `adr-####-brief-title.md`
- [ ] **Status**: Set to "Proposed" (not yet "Accepted")
- [ ] **Date**: Current date in YYYY-MM-DD format
- [ ] **Authors**: All contributors listed with roles
- [ ] **Formatting**: Markdown renders correctly, no broken links
- [ ] **Template**: Follows standard ADR template structure

---

## Content Quality Checklist

### 1. Context Section

- [ ] **Problem is Clear**: Anyone can understand what needs solving
- [ ] **Current State Documented**: What exists today is explained
- [ ] **Requirements Listed**: Business and technical needs specified
- [ ] **Constraints Identified**: Limitations are explicit (budget, time, tech, skills)
- [ ] **Forces Explained**: Competing concerns or trade-offs described
- [ ] **Stakeholders Identified**: Who cares about this decision?

**Quality Indicators:**
- ✅ Context is 3-5 paragraphs (not too brief, not too verbose)
- ✅ Someone unfamiliar with the problem can understand it
- ✅ Quantitative data provided where relevant (users, load, costs)
- ✅ No solution details leaked into context (remains problem-focused)

### 2. Decision Section

- [ ] **Decision is Specific**: Clear what is being adopted
- [ ] **Technology Stack Named**: Specific versions and tools listed
- [ ] **Implementation Strategy Defined**: How this will be rolled out
- [ ] **Timeline Provided**: When implementation starts and completes
- [ ] **Responsibilities Assigned**: Who owns what aspects
- [ ] **Success Criteria**: How we'll know this works (optional but recommended)

**Quality Indicators:**
- ✅ Decision uses active, declarative language ("We will adopt...")
- ✅ No ambiguity (another team could implement from this ADR)
- ✅ Scope is clear (what's included, what's not)
- ✅ Entry criteria specified if phased approach

**Red Flags:**
- ❌ Vague language: "We'll consider using..." or "We might try..."
- ❌ No timeline: "Eventually we'll implement this"
- ❌ No ownership: "Someone should do this"

### 3. Consequences Section

- [ ] **Positive Outcomes Listed**: Benefits are explicit (at least 3)
- [ ] **Negative Outcomes Listed**: Costs, risks, trade-offs documented (at least 3)
- [ ] **Neutral Outcomes Listed**: Changes that aren't clearly positive/negative
- [ ] **Honest Assessment**: Not just selling the decision, but balanced
- [ ] **Quantified Where Possible**: Numbers provided (latency, cost, time)

**Quality Indicators:**
- ✅ Negatives are substantial and honest, not trivial
- ✅ Each consequence explains "why it matters"
- ✅ Operational impact considered (monitoring, debugging, on-call)
- ✅ Long-term consequences addressed (not just short-term)

**Red Flags:**
- ❌ Only positive consequences listed
- ❌ Negatives are downplayed or hand-waved
- ❌ No mention of operational complexity
- ❌ Consequences are vague: "May be harder to..." vs "Will add 10-50ms latency"

### 4. Alternatives Section

- [ ] **At Least 2 Alternatives**: Minimum requirement
- [ ] **Alternatives Are Real**: Actually considered, not strawmen
- [ ] **Description Provided**: What each alternative entails
- [ ] **Pros Listed**: Advantages of each alternative (at least 2)
- [ ] **Cons Listed**: Disadvantages of each alternative (at least 2)
- [ ] **Rejection Rationale**: Clear explanation why not chosen
- [ ] **Comparative**: Alternatives compared against chosen solution

**Quality Indicators:**
- ✅ "Do nothing" or "Status quo" considered as alternative
- ✅ Alternatives span different approaches (not just vendor variations)
- ✅ Each alternative has enough detail to understand trade-offs
- ✅ Rejection rationale is specific, not generic

**Red Flags:**
- ❌ Only 1 alternative (should have at least 2)
- ❌ Alternatives are clearly inferior (strawmen)
- ❌ Rejection rationale is "We just liked the other one better"
- ❌ Pros/cons are imbalanced (chosen solution has 10 pros, alternatives have 1)

### 5. References Section (Optional but Recommended)

- [ ] **Discussion Links**: Slack threads, meeting notes, email chains
- [ ] **Research Sources**: Articles, books, documentation consulted
- [ ] **Related ADRs**: Other decisions that influenced this one
- [ ] **Proof of Concept**: Link to PoC implementation or spike results
- [ ] **Cost Analysis**: Spreadsheets or documents with cost projections

---

## Architecture Review Criteria

### Technical Viability

- [ ] **Technically Sound**: Solution is feasible with current state of technology
- [ ] **Scalability**: Addresses scale requirements (users, data, transactions)
- [ ] **Performance**: Meets latency, throughput, and responsiveness needs
- [ ] **Security**: Security implications considered and addressed
- [ ] **Reliability**: Failure modes and recovery strategies documented
- [ ] **Maintainability**: Long-term maintenance burden is acceptable
- [ ] **Testability**: Can be tested effectively (unit, integration, E2E)

### Business Alignment

- [ ] **Supports Goals**: Aligns with company/product strategic direction
- [ ] **Cost Justified**: ROI or value proposition is clear
- [ ] **Timeline Realistic**: Implementation window is achievable
- [ ] **Resource Availability**: Team has skills (or can acquire them)
- [ ] **Risk Acceptable**: Risks are understood and within tolerance

### Operational Considerations

- [ ] **Deployment Strategy**: How this goes to production is clear
- [ ] **Monitoring Plan**: How we'll observe this in production
- [ ] **Rollback Plan**: How we undo this if it fails
- [ ] **Training Needs**: Team knows how to work with this
- [ ] **Documentation**: Sufficient for ongoing maintenance
- [ ] **On-Call Impact**: Effect on operations team understood

### Compliance & Standards

- [ ] **Coding Standards**: Follows team/org conventions
- [ ] **Security Standards**: Meets security policies
- [ ] **Compliance Requirements**: Regulatory needs addressed (GDPR, HIPAA, SOC2)
- [ ] **Architecture Principles**: Consistent with existing principles
- [ ] **Technology Radar**: Aligns with approved technology choices

---

## Stakeholder Sign-Off

Required approvals (customize based on your organization):

### Technical Approvals

- [ ] **Chief/Principal Architect**: Overall architecture coherence
- [ ] **Domain Architect**: Specific domain expertise (frontend, backend, data, security)
- [ ] **Tech Lead**: Implementation feasibility
- [ ] **DevOps/SRE**: Operational viability

### Business Approvals

- [ ] **Engineering Manager**: Resource allocation and timeline
- [ ] **Product Manager**: Business value and priority
- [ ] **Security Team**: Security implications (if applicable)
- [ ] **Compliance Team**: Regulatory requirements (if applicable)

### Optional Approvals (depending on scope)

- [ ] **CTO/VP Engineering**: Strategic decisions
- [ ] **Finance**: Large cost impacts (>$50k)
- [ ] **Legal**: Licensing, contracts, IP considerations

---

## Common Review Feedback

### Context Issues

- "I don't understand the problem we're solving"
  - **Fix**: Add more background, quantify the pain points

- "Are these requirements from Product or assumptions?"
  - **Fix**: Clarify source of each requirement, validate with stakeholders

- "What's the urgency? Can this wait?"
  - **Fix**: Add business impact and timeline drivers

### Decision Issues

- "This seems too vague to implement"
  - **Fix**: Add specific technologies, versions, and implementation steps

- "Who's actually going to do this?"
  - **Fix**: Assign clear ownership with names/roles

- "What if we need to change this later?"
  - **Fix**: Document extensibility, plan for evolution

### Consequences Issues

- "You're only showing the upside"
  - **Fix**: Add honest trade-offs, costs, and risks

- "What about operational complexity?"
  - **Fix**: Document monitoring, debugging, on-call implications

- "How does this affect other teams?"
  - **Fix**: Assess cross-team impact, communication needs

### Alternatives Issues

- "These alternatives seem like strawmen"
  - **Fix**: Present alternatives fairly, with genuine pros/cons

- "Why didn't you consider [obvious alternative]?"
  - **Fix**: Add missing alternatives, explain evaluation process

- "I disagree with your reasoning"
  - **Fix**: Revisit decision rationale, possibly reconsider

---

## Post-Review Actions

After approval:

- [ ] **Update Status**: Change from "Proposed" to "Accepted"
- [ ] **Add Approval Dates**: Document when each stakeholder approved
- [ ] **Commit to Repository**: Merge ADR into main branch
- [ ] **Communicate**: Announce accepted ADR to relevant teams
- [ ] **Link in Implementation**: Reference ADR in PRs/tickets
- [ ] **Update Index**: Add to ADR index or table of contents
- [ ] **Schedule Review**: Calendar reminder to review effectiveness in 3-6 months

---

## ADR Rejection Criteria

When to reject an ADR (requires rewrite):

### Fatal Flaws

- ❌ **Decision is Premature**: Not enough information to decide yet
- ❌ **Problem Undefined**: Can't understand what's being solved
- ❌ **No Alternatives**: Only one option presented
- ❌ **Unjustified**: Decision rationale is weak or missing
- ❌ **Unrealistic**: Timeline, budget, or skills are infeasible
- ❌ **Wrong Scope**: Too big (break into multiple ADRs) or too small (not worthy of ADR)

### Serious Issues

- ⚠️ **Insufficient Analysis**: Trade-offs not explored deeply enough
- ⚠️ **Missing Stakeholders**: Key people weren't consulted
- ⚠️ **Conflicts with Strategy**: Doesn't align with org direction
- ⚠️ **Risks Unaddressed**: Major risks not acknowledged or mitigated
- ⚠️ **Compliance Issues**: Regulatory problems not resolved

### Process Problems

- ⚠️ **Bypassed Review**: ADR created after decision already made
- ⚠️ **Incomplete Template**: Major sections missing
- ⚠️ **Poor Quality**: Unclear writing, formatting issues

---

## Review Meeting Tips

**Before the Meeting:**
- [ ] Share ADR at least 48 hours in advance
- [ ] Request reviewers read before meeting
- [ ] Prepare to answer questions about alternatives and trade-offs

**During the Meeting:**
- [ ] Present context and decision clearly (5-10 minutes)
- [ ] Walk through alternatives and why not chosen
- [ ] Address questions and concerns
- [ ] Document feedback and action items
- [ ] Seek consensus, not just majority

**After the Meeting:**
- [ ] Incorporate feedback within 1 week
- [ ] Re-share revised ADR for final approval
- [ ] Don't "accept" ADR until concerns addressed

---

## Version History

- **v1.0.0** (2025-10-31): Initial checklist
- Template maintained by: AI Agent Hub Team
- Skill: architecture-decision-record v1.0.0
