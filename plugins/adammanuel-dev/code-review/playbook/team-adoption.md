# Team Adoption Guide: Rolling Out Code Review Practices

<context>
This guide provides a phased approach to adopting code review best practices across a team. Starting with individual adoption, building to pilot programs, and eventually achieving full team implementation with measurable improvements.
</context>

## Why Teams Struggle with Code Review

**Common failure modes:**
- **Too much, too fast**: Imposing heavy process overnight creates resistance
- **No buy-in**: Top-down mandates without team understanding fail
- **Inconsistent adoption**: Some follow practices, others don't - creates friction
- **No metrics**: Can't prove improvement, hard to justify continued effort
- **Tool over culture**: Focusing on tools instead of practices

**Successful adoption principles:**
- Start small, prove value, expand
- Lead by example
- Make it easy (templates, automation)
- Measure and celebrate improvements
- Iterate based on feedback

## Phased Rollout Plan

### Phase 1: Individual Adoption (Week 1-2)

**Goal:** Prove value with 1-2 early adopters before team-wide rollout.

**Who:** You + 1-2 interested teammates (early adopters)

**What to do:**
1. Install the code-review-skill
2. Use author checklist on your own PRs
3. Practice two-pass review methodology
4. Use comment classification in reviews
5. Track your experience

**Success metrics:**
- PRs from adopters have fewer review cycles
- Reviews completed faster (measure time to first review, time to merge)
- Reviewers report PRs are easier to review

**Deliverables:**
- [ ] 5-10 PRs using author checklist
- [ ] 10-15 reviews using two-pass methodology
- [ ] Documented improvements (time saved, issues caught)

**Example narrative:**
> "I started using the author checklist this week. My last PR got approved in 2 hours instead of the usual 2 days. The reviewer said the test plan made it really easy to verify. I'm going to keep using this."

### Phase 2: Team Pilot (Week 3-4)

**Goal:** Expand to 30-50% of team, establish shared practices.

**Who:** Core team members who do most reviews

**What to do:**
1. Share Phase 1 results with team
2. Generate PR template for repo: `/code-review-init`
3. Establish CODEOWNERS for automatic assignment
4. Set initial SLAs (24h first response target)
5. Practice comment classification consistently

**New practices:**
- All new PRs use PR template
- Reviewers use comment classification
- Track review latency metrics

**Getting buy-in:**
- **Show data from Phase 1**: "My PRs merged 60% faster"
- **Address concerns**: "Won't this slow us down?" → "Actually speeds things up by reducing back-and-forth"
- **Make it optional at first**: "Try it on your next 3 PRs and see"

**Deliverables:**
- [ ] PR template in `.github/pull_request_template.md`
- [ ] CODEOWNERS file with team structure
- [ ] 50% of team using practices
- [ ] Baseline metrics established

**Team meeting agenda:**
```markdown
# Code Review Practice Pilot - Kickoff

## Results from Individual Adoption (5 min)
- 10 PRs using checklist merged 2.3 days faster on average
- Fewer review cycles (1.2 vs 2.8 average)
- Reviewers report higher confidence in approvals

## What We're Trying (10 min)
- PR template (shows example)
- Two-pass review methodology (quick demo)
- Comment classification (examples)

## What We're Asking (5 min)
- Try author checklist on your next 2-3 PRs
- Use comment classification in reviews
- Give feedback on what works / doesn't work

## Timeline
- 2 week pilot
- Retrospective at end of week 2
- Decide whether to continue / adjust / expand
```

### Phase 3: Full Team Rollout (Week 5-8)

**Goal:** All team members using practices consistently.

**Who:** Entire team

**What to do:**
1. Make practices standard (update team documentation)
2. Establish enforcement (reviewers can request author checklist completion)
3. Track metrics dashboard: `/code-review-metrics`
4. Iterate based on feedback
5. Celebrate wins publicly

**Team expectations:**
- All PRs use template and author checklist
- All reviews use two-pass methodology and comment classification
- SLAs are met (24h first response, 5d merge for medium PRs)
- Monthly metrics review

**Deliverables:**
- [ ] Updated team docs/handbook with code review standards
- [ ] Monthly metrics dashboard
- [ ] Retrospective process for continuous improvement
- [ ] Onboarding materials for new team members

**Enforcement approach:**
- **Light touch at first**: Remind, don't reject
- **Lead by example**: Senior team members model behavior
- **Automate where possible**: CI checks, templates
- **Celebrate good behavior**: Call out excellent PR descriptions and reviews

### Phase 4: Optimization (Month 2-3)

**Goal:** Refine practices based on team experience.

**What to do:**
1. Analyze metrics monthly
2. Identify pain points and anti-patterns
3. Adjust policies (e.g., PR size limits)
4. Expand automation
5. Share learnings with other teams

**Common refinements:**
- Adjust SLAs based on actual performance
- Customize PR template for team needs
- Add team-specific sections to CODEOWNERS
- Create team-specific review checklists for specialized domains

**Deliverables:**
- [ ] Monthly metrics reviews with action items
- [ ] Documented anti-patterns and solutions
- [ ] Refined PR template and checklists
- [ ] Case studies of improved code review quality

## Getting Buy-In from Different Roles

### For Developers

**Common objection:** "This will slow me down"

**Response:**
- "Actually, it speeds things up by reducing review cycles"
- Show data: PRs with good descriptions merge 2-3x faster
- "5 minutes preparing PR saves 30 minutes in review back-and-forth"

**What they care about:**
- Getting PRs merged faster
- Less frustrating review cycles
- Clear expectations

**Sell on:**
- Author checklist catches issues before embarrassment
- Comment classification clarifies what's blocking vs. optional
- Faster reviews mean faster shipping

### For Team Leads / Managers

**Common objection:** "We don't have time for process"

**Response:**
- "This reduces time spent on poor code review"
- "Faster reviews mean faster delivery"
- Industry research shows correlation with delivery performance

**What they care about:**
- Delivery velocity
- Code quality / fewer bugs
- Team efficiency

**Sell on:**
- Measurable improvements in review latency
- Reduced bug escape rate
- Better knowledge sharing across team

### For Senior Engineers / Architects

**Common objection:** "We already do this informally"

**Response:**
- "Making it explicit helps newer team members"
- "Consistency across team improves quality"
- "Codifying practices enables scaling"

**What they care about:**
- Code quality
- Architectural consistency
- Mentoring effectiveness

**Sell on:**
- Two-pass review catches design issues early
- Comment classification improves mentoring (distinguishes critical from nits)
- Documented practices make onboarding easier

## Handling Resistance

### "This is too much process"

**Response:**
- Start with just author checklist (minimal overhead)
- Show time savings data
- Make it optional, prove value first

**Compromise:**
- "Try it on just your next PR and see if it helps"

### "Our team is different / special"

**Response:**
- "These are principles, not rigid rules - adapt to your needs"
- "Let's try it and customize based on what works"
- Offer to adjust templates for team specifics

**Compromise:**
- Customize PR template for team's unique needs
- Adjust SLAs based on team size and workload

### "I don't have time to review thoroughly"

**Response:**
- Two-pass review is time-boxed (< 30 min)
- Faster than current multi-round back-and-forth
- Comment classification clarifies what needs deep review

**Compromise:**
- Start with just Pass 1 (design review, 10 min)
- Tag second reviewer for Pass 2 if needed

### "Authors never follow the template anyway"

**Response:**
- Lead by example - use it on your PRs
- Reviewers can request completion: "Please fill out the test plan section so I can verify"
- Make it easier with automation

**Compromise:**
- Start with partial template (just context and test plan)
- Expand sections as team adopts

## Success Metrics

### Leading Indicators (Week 1-2)
- % of PRs using template
- % of reviews using comment classification
- Team feedback (survey)

### Lagging Indicators (Week 3-8)
- Review latency (time to first review)
- Merge latency (time to merge)
- Review cycles per PR
- PR size distribution

### Quality Indicators (Month 2-3)
- Bug escape rate (bugs found in production)
- Test coverage trends
- Incident rate related to merged code

**Target improvements:**
- 30-50% reduction in review latency
- 20-40% reduction in review cycles per PR
- 80%+ of PRs under 400 lines
- < 1% bug escape rate

## Celebration & Recognition

**Publicly recognize:**
- Excellent PR descriptions (example in team meeting)
- Thorough, helpful reviews (call out great [praise] comments)
- Fast review turnarounds (meeting SLAs)
- Caught critical issues in review

**Ways to celebrate:**
- Slack shoutouts
- Team meeting recognition
- Monthly "Code Review Champion" (rotating)
- Include in performance reviews

**Example:**
> Shoutout to @alice for the excellent PR description on #456. The test plan made it so easy to verify, and the deployment notes caught a potential issue we would have missed. This is the standard we're aiming for! 🎉

## Onboarding New Team Members

**Include in onboarding:**
1. Code review philosophy (quality + velocity)
2. Author checklist walkthrough
3. Shadowing experienced reviewer
4. First few PRs mentored closely

**Onboarding checklist:**
- [ ] Read `playbook/author-guide.md`
- [ ] Read `playbook/reviewer-guide.md`
- [ ] Read `playbook/comment-classification.md`
- [ ] Shadow 2-3 code reviews
- [ ] Get PR reviewed with extra feedback
- [ ] Conduct first review with mentor oversight

**Pair programming for reviews:**
- New team member + experienced reviewer
- Review PR together, discuss thinking
- Practice comment classification
- Build confidence

## Continuous Improvement

### Monthly Retrospective

**Agenda:**
1. Review metrics (10 min)
   - Review/merge latency
   - PR size distribution
   - SLA compliance
2. What's working well? (10 min)
3. What's painful? (10 min)
4. Action items (5 min)

**Questions to ask:**
- Are PRs getting easier to review?
- Are reviews happening faster?
- What's still frustrating?
- Any new anti-patterns emerging?
- How can we improve?

### Evolve Practices

**Examples of evolution:**
- Team finds 400 line limit too strict for refactors → Add exception policy
- Security reviews taking too long → Create security checklist for common patterns
- Too many nits → Improve linting automation
- Large PRs still common → Add PR size warnings in CI

**Document changes:**
Update team docs when practices evolve. Keep skill guides as reference, customize in team handbook.

## Scaling to Multiple Teams

**Once one team succeeds:**

1. **Share results** with other teams
   - Metrics and improvements
   - Lessons learned
   - Anti-patterns encountered

2. **Offer pilot support**
   - Help other teams set up
   - Share customized templates
   - Provide coaching

3. **Create community of practice**
   - Monthly sharing sessions
   - Slack channel for tips
   - Document team customizations

4. **Standardize where helpful**
   - Common PR template across company
   - Shared comment classification
   - Company-wide SLAs

## Common Questions

### "How do I convince my manager?"

Show data from similar teams:
- Industry research linking code review quality to delivery performance
- Example metrics from other companies
- Pilot proposal (low commitment, measurable results)

### "What if people don't use the template?"

- Lead by example
- Make it easier (auto-fill common sections)
- Reviewers can request completion
- Eventually, can make it required (but only after proving value)

### "How do we handle urgent PRs?"

- Create "urgent" label with justification required
- Allow template shortcuts but require context
- Post-hoc review if truly emergency
- Track frequency (too many urgents means planning problems)

### "Our PRs are always large due to generated code"

- Exclude generated code from metrics
- Separate generated code commits from logic changes
- Review generated code at high level only
- Focus metrics on hand-written code

### "What about junior developers?"

- Extra support during first reviews
- Pair with senior reviewer
- More detailed feedback (teaching moment)
- Expect learning curve

## Example Timeline

**Week 1:**
- You adopt practices individually
- Document improvements

**Week 2:**
- Share results with 2-3 interested teammates
- They try practices

**Week 3:**
- Present to full team
- Generate PR template: `/code-review-init`
- 50% of team tries practices

**Week 4:**
- Collect feedback
- Adjust practices based on feedback
- Track metrics

**Week 5:**
- Make practices standard for team
- Update team documentation
- Establish SLAs

**Week 6-8:**
- Full team adoption
- Address stragglers
- Track metrics
- Iterate on process

**Month 2-3:**
- Optimize based on data
- Expand automation
- Share learnings with other teams

---

**Remember:** Change management is gradual. Start small, prove value, expand. Celebrate wins, address concerns, iterate based on feedback. The goal is sustainable improvement, not overnight transformation.
