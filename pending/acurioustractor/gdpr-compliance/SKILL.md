# GDPR Compliance Skill

This skill provides comprehensive guidance for implementing and reviewing GDPR-compliant features in Empathy Ledger.

## GDPR Rights Reference

### Article 15 - Right of Access
**Requirement**: Users can request a copy of their personal data

**Implementation**:
```typescript
// GET /api/user/export
const data = await gdprService.exportUserData(userId)
// Returns: stories, media, profile, consent records, activity logs
```

### Article 16 - Right to Rectification
**Requirement**: Users can correct inaccurate personal data

**Implementation**:
- Edit profile via profile settings
- Edit stories via story editor
- All changes logged in audit trail

### Article 17 - Right to Erasure (Right to be Forgotten)
**Requirement**: Users can request deletion of their data

**Implementation**:
```typescript
// POST /api/user/deletion-request
// Initiates 30-day deletion workflow

// POST /api/stories/[id]/anonymize
// Immediate anonymization of specific story
```

**Anonymization Process**:
1. Remove PII from story content
2. Replace author name with "Anonymous Storyteller"
3. Disassociate from profile (set storyteller_id = null)
4. Revoke all active distributions
5. Anonymize related media
6. Keep anonymized audit trail

### Article 20 - Right to Data Portability
**Requirement**: Users can export data in machine-readable format

**Implementation**:
- JSON export format
- Includes all user-generated content
- Downloadable via vault dashboard

## Consent Management

### Consent Capture
```typescript
interface ConsentRecord {
  has_consent: boolean           // Initial consent given
  consent_verified: boolean      // Consent verification completed
  consent_method?: string        // 'written' | 'verbal' | 'digital'
  consent_date?: Date
  consent_witness_id?: string    // For verbal consent
}
```

### Consent Withdrawal
```typescript
// POST /api/stories/[id]/consent/withdraw
// Triggers:
// 1. Set consent_withdrawn_at timestamp
// 2. Revoke all embed tokens
// 3. Mark all distributions as revoked
// 4. Send webhook notifications
// 5. Queue external takedown requests
// 6. Create audit log entries
```

## Data Processing Lawful Bases

For Empathy Ledger, we rely on:

1. **Consent (Article 6(1)(a))** - Primary basis for story sharing
2. **Legitimate Interest (Article 6(1)(f))** - Platform operation, security

## Data Minimization

### Collect Only What's Needed
- Essential profile data: name, email, organization
- Story content: as provided by user
- Technical data: minimal logging for security

### Retention Limits
- Active data: retained while account active
- Deleted data: fully removed within 30 days
- Anonymized data: kept for aggregate statistics only
- Audit logs: anonymized after account deletion

## Implementation Checklist

### User Data Export
```
□ Export includes all user stories
□ Export includes media files
□ Export includes profile data
□ Export includes consent records
□ Export includes activity log
□ Format is JSON (machine-readable)
□ Download is secure (authenticated)
```

### Data Deletion
```
□ Deletion request creates ticket
□ User receives confirmation email
□ 30-day processing window
□ All stories anonymized or deleted
□ All media files removed
□ Profile data erased
□ Audit trail anonymized
□ Third-party distributions notified
```

### Consent Tracking
```
□ Consent captured before distribution
□ Consent method recorded
□ Consent can be withdrawn
□ Withdrawal cascades automatically
□ Audit trail for consent changes
□ Re-consent required for new purposes
```

## API Endpoints

### Data Rights
- `GET /api/user/export` - Export all user data
- `POST /api/user/deletion-request` - Request account deletion
- `GET /api/user/deletion-request` - Check deletion status

### Story-Level GDPR
- `POST /api/stories/[id]/anonymize` - Anonymize specific story
- `POST /api/stories/[id]/consent/withdraw` - Withdraw consent

### Audit Access
- `GET /api/stories/[id]/audit` - View story audit trail
- `POST /api/stories/[id]/audit/export` - Export audit report

## Database Schema

### deletion_requests
```sql
CREATE TABLE deletion_requests (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  tenant_id UUID NOT NULL,
  request_type TEXT NOT NULL,     -- 'anonymize_story', 'delete_account'
  status TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'completed'
  requested_at TIMESTAMPTZ,
  processed_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);
```

### Story Anonymization Fields
```sql
-- On stories table
anonymization_status TEXT,        -- null, 'partial', 'full'
anonymized_fields JSONB,          -- Track what was anonymized
consent_withdrawn_at TIMESTAMPTZ  -- When consent was withdrawn
```

## Services

### GDPRService
```typescript
class GDPRService {
  exportUserData(userId: string): Promise<DataExport>
  anonymizeStory(storyId: string): Promise<AnonymizeResult>
  anonymizeUserData(userId: string): Promise<AnonymizeResult>
  createDeletionRequest(userId: string, type: string): Promise<Request>
  processDeletionRequest(requestId: string): Promise<void>
  scrubPII(content: string): string
}
```

## Code Review for GDPR

When reviewing code, verify:

1. **Data Collection**: Is this data necessary?
2. **Consent**: Is consent captured before processing?
3. **Access**: Can users access their data?
4. **Rectification**: Can users correct their data?
5. **Erasure**: Can users delete their data?
6. **Portability**: Can users export their data?
7. **Audit**: Are actions logged?
8. **Security**: Is data properly protected?
