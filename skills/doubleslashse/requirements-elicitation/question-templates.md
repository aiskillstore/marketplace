# Requirements Elicitation Question Templates

## Stakeholder Identification Questions

### Business Stakeholders
1. Who are the primary users of this system?
2. Who will make decisions about system features and priorities?
3. Who controls the budget for this project?
4. Who will be responsible for maintaining the system?
5. Are there any external stakeholders (customers, partners, regulators)?

### Role-Based Questions
- What is your role in relation to this system?
- How often do you interact with systems like this?
- What are your main pain points with the current solution?
- What would make your job easier?

## Scope Definition Questions

### Project Boundaries
1. What problem are we trying to solve?
2. What is explicitly OUT of scope for this project?
3. What are the boundaries of the system?
4. Which existing systems will this interact with?
5. What is the timeline for delivery?

### Success Criteria
- How will we know if this project is successful?
- What metrics will we use to measure success?
- What does "done" look like for this project?

## Functional Requirements Questions

### Core Functionality
1. What are the main things users need to accomplish?
2. Walk me through a typical user workflow
3. What actions can users take in the system?
4. What data does the system need to process?
5. What outputs/reports does the system need to produce?

### Business Rules
1. What rules govern how the system should behave?
2. Are there any calculations or formulas the system must perform?
3. What validation rules apply to data entry?
4. Are there any approval workflows or escalation paths?
5. How should the system handle exceptions?

### Data Requirements
1. What data does the system need to store?
2. Where does the data come from?
3. How long must data be retained?
4. Who can see what data? (access controls)
5. Are there any data privacy requirements?

## Non-Functional Requirements Questions

### Performance (FURPS - P)
1. How many users will use the system concurrently?
2. What is an acceptable response time?
3. How much data will the system process?
4. Are there peak usage times?
5. What are the throughput requirements?

### Reliability (FURPS - R)
1. What is the required uptime (e.g., 99.9%)?
2. What happens if the system goes down?
3. How quickly must the system recover from failures?
4. Is 24/7 availability required?
5. What is the backup and recovery strategy?

### Usability (FURPS - U)
1. Who are the target users and what is their technical skill level?
2. Are there accessibility requirements (WCAG)?
3. What devices/browsers must be supported?
4. Is multi-language support required?
5. What training will users receive?

### Security (FURPS - F)
1. What authentication method is required?
2. What authorization/role-based access is needed?
3. Are there compliance requirements (GDPR, HIPAA, SOC2)?
4. How should sensitive data be protected?
5. What audit logging is required?

### Supportability (FURPS - S)
1. Who will maintain the system?
2. How will the system be monitored?
3. What logging and diagnostics are needed?
4. How will updates be deployed?
5. What documentation is required?

## Constraint Questions

### Technical Constraints
1. Are there required technologies or platforms?
2. Are there prohibited technologies?
3. What is the existing technical landscape?
4. Are there integration requirements?
5. What are the infrastructure limitations?

### Business Constraints
1. What is the budget?
2. What is the timeline?
3. Are there resource limitations?
4. Are there regulatory or compliance requirements?
5. Are there contractual obligations?

## Greenfield-Specific Questions

### Vision and Goals
1. What is the vision for this product/system?
2. What business problem does this solve?
3. Who is the target audience?
4. What is the competitive landscape?
5. What differentiates this solution?

### Initial Scope
1. What is the minimum viable product (MVP)?
2. What features are must-haves for launch?
3. What can be deferred to future phases?
4. Are there any proof-of-concept requirements?

## Brownfield-Specific Questions

### Current State
1. What does the current system do well?
2. What are the pain points with the current system?
3. What business processes does it support?
4. Who are the current users?
5. What integrations exist?

### Change Drivers
1. Why is change needed now?
2. What has changed in the business?
3. Are there new regulatory requirements?
4. Is the current technology end-of-life?
5. What risks exist with the current system?

### Migration Considerations
1. What data needs to be migrated?
2. Can we run both systems in parallel?
3. What is the cutover strategy?
4. How will we handle training for new features?
5. What is the rollback plan if issues occur?

## Integration Questions

### External Systems
1. What external systems must we integrate with?
2. What data flows between systems?
3. Are integrations real-time or batch?
4. What APIs or protocols are required?
5. Who owns the external systems?

### Data Exchange
1. What format is data exchanged in (JSON, XML, CSV)?
2. How is data transformation handled?
3. What happens if integration fails?
4. Are there rate limits or quotas?
5. How is authentication handled?

## Validation Questions

### Confirmation
1. Let me summarize what I've heard - is this accurate?
2. Have I missed any important requirements?
3. Are there any edge cases we haven't discussed?
4. Who else should I talk to about these requirements?
5. Can you prioritize the requirements we've discussed?

### Assumptions
1. I'm assuming [X] - is that correct?
2. Are there any assumptions I'm making that are incorrect?
3. What assumptions are you making about the solution?

## Adaptive Follow-Up Patterns

### When Answer is Vague
- "Can you give me a specific example?"
- "What would that look like in practice?"
- "How do you handle that today?"

### When Answer Reveals Complexity
- "Let's break that down - what are the steps?"
- "Are there different scenarios to consider?"
- "What are the exceptions to that rule?"

### When Answer Conflicts
- "Earlier you mentioned [X], but now [Y] - can you clarify?"
- "How does that work with [previous requirement]?"
- "What takes priority in that situation?"

### When Answer is Incomplete
- "What happens next?"
- "What if [edge case]?"
- "Who is involved in that process?"
