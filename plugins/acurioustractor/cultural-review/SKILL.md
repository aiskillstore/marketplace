# Cultural Review Skill

This skill provides comprehensive guidance for reviewing code, features, and content for cultural sensitivity and Indigenous data sovereignty compliance.

## OCAP Framework Reference

### Ownership
**Requirement**: Storytellers maintain ownership of their narratives

**Check for**:
- [ ] Story ownership tracked via `author_id` and `storyteller_id`
- [ ] Both author and storyteller have control rights
- [ ] Ownership cannot be transferred without consent
- [ ] Community collective ownership respected

### Control
**Requirement**: Users decide who accesses their stories

**Check for**:
- [ ] Privacy levels properly enforced (public/community/org/private)
- [ ] Users can revoke access at any time
- [ ] Distribution requires explicit consent
- [ ] Bulk revocation available ("Pull All")

### Access
**Requirement**: Tiered access based on cultural sensitivity

**Check for**:
- [ ] Sensitivity levels correctly implemented
- [ ] Elder approval workflow for high/sacred content
- [ ] Community membership verification where required
- [ ] Access audit trail maintained

### Possession
**Requirement**: Data can be exported or deleted anytime

**Check for**:
- [ ] Data export functionality (GDPR Article 20)
- [ ] Full deletion/anonymization (GDPR Article 17)
- [ ] No data lock-in or artificial barriers
- [ ] Portable data format (JSON)

## Sensitivity Level Guidelines

### Standard
- General stories, no restrictions
- Can be embedded externally
- Public sharing allowed

### Medium
- Some cultural context important
- May require community membership
- External sharing needs approval

### High
- Significant cultural value
- Elder review before sharing
- Limited distribution options
- No unauthorized embedding

### Sacred/Restricted
- Protected traditional knowledge
- Elder approval mandatory
- NO external distribution ever
- May have viewing time/place restrictions

## Code Review Checklist

### API Endpoints
```
□ Authentication required (unless public embed)
□ Authorization checks ownership/permissions
□ Sensitivity level verified before action
□ Elder approval status checked for high/sacred
□ Audit log created for significant actions
□ Consent verified before distribution
□ Revocation cascades properly
```

### UI Components
```
□ Cultural indicators are respectful
□ Sensitivity badges are clear
□ Elder approval status prominent
□ Consent status visible
□ Privacy level clearly shown
□ Revocation controls accessible
□ Trauma-informed animations (gentle)
□ Language is inclusive
```

### Database Operations
```
□ Tenant isolation maintained
□ Ownership fields populated
□ Consent fields checked
□ Audit trail created
□ Soft delete preferred over hard delete
□ Anonymization preserves audit trail
```

## Red Flags

### Immediate Action Required
- External distribution of sacred content
- Missing consent verification
- Broken revocation cascade
- Elder approval bypassed
- Tenant isolation breached

### Needs Improvement
- Missing audit logging
- Hard delete without anonymization
- Unclear sensitivity indicators
- Missing ownership checks
- No bulk revocation option

## Approval Workflow

### Standard Content
1. Author creates story
2. Consent captured
3. Ready for distribution

### Medium Sensitivity
1. Author creates story
2. Cultural context added
3. Consent captured
4. Community review (optional)
5. Ready for limited distribution

### High Sensitivity
1. Author creates story
2. Cultural context added
3. Consent captured
4. Elder review requested
5. Elder approves/requests changes
6. Limited distribution (no embedding)

### Sacred Content
1. Author creates story
2. Cultural context added
3. Consent captured
4. Elder review mandatory
5. Elder approval required
6. Platform-only access
7. Never distributed externally
