# Technical Specifications - NEXLY RN

## How to Use This Template

**Required Sections:** 1, 2, 4, 6, 7, 8
**Optional Sections:** 3 (if no database), 5 (if simple auth), 9 (always valuable but not blocking)
**Desktop-Only:** Section 4.3 (IPC/Event Messages)
**Backend Services:** Section 4.1 (API Endpoints)

**Tip:** Remove sections that don't apply rather than leaving them empty. Replace all placeholder text in `[brackets]` with actual content. Delete example comments in `<!-- -->` after replacing with your own content.

---

## 1. Overview

**Name:** [Write the name of the product in detail]
**Product Description:** [Write the product description in detail]

**Core Technology Stack**

- [Tech Stack 1]
- [Tech Stack 2]
- [Tech Stack 3]
- ...

**Dependencies:**

- [Dependency 1]
- [Dependency 2]
- [Dependency 3]
- ...

**Deployment:**

- [Deployment 1]
- [Deployment 2]
- [Deployment 3]
- ...

**AI Integration:** _Optional_

- [AI Integration 1]
- [AI Integration 2]
- [AI Integration 3]
- ...

**Project Structure:**

```
<!-- Add the project structure here -->
```

<!-- Example of project structure:

```
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   ├── (dashboard)/
│   │   │   ├── notes/
│   │   │   ├── study/
│   │   │   ├── settings/
│   │   │   └── (other routes)
│   │   └── (other routes)
```
-->

## 2. Architecture Design

### Component Diagram

```
<!-- Add the component diagram here -->
```

### Core Component Architecture

**[Core Component 1]**

- [Core Component 1 Description]
- [Core Component 2 Description]
- [Core Component 3 Description]
- ...

**[Core Component 2]**

- [Core Component 2 Description]
- [Core Component 3 Description]
- ...

**[Core Component 3]**

- [Core Component 3 Description]
- ...

<!--

Example:

Frontend Layer (React + TypeScript)

- Handles all UI rendering and user interactions
- Manages local UI state (cursor position, editor focus, modal states)
- Communicates with Tauri backend via IPC for all data operations
- Implements rich text editing with TipTap or similar


Tauri Backend

- Acts as bridge between frontend and external services
- Manages secure API key storage for OpenAI
- Handles file system operations for local note caching
- Enforces business logic before database writes
 -->

### Key Design Decisions

**[Key Design Decision 1]**

- [Key Design Decision 1 Description]
- [Key Design Decision 2 Description]
- [Key Design Decision 3 Description]
- ...

**[Key Design Decision 2]**

- [Key Design Decision 2 Description]
- [Key Design Decision 3 Description]
- ...

...

### Architecture Decision Records (ADRs)

Document major technical decisions for future reference:

**ADR-001: [Decision Title]**

- **Date:** YYYY-MM-DD
- **Status:** Accepted | Superseded | Deprecated
- **Context:** [Why this decision was needed]
- **Decision:** [What was chosen]
- **Consequences:** [Trade-offs, implications]
- **Alternatives Considered:** [What else was evaluated]

<!--
Example:

ADR-001: Choose Tauri over Electron for Desktop App

- **Date:** 2025-01-15
- **Status:** Accepted
- **Context:** Need desktop app framework for NEXLY RN with secure API key storage, offline capabilities, and small bundle size
- **Decision:** Use Tauri (Rust backend + web frontend) instead of Electron
- **Consequences:**
  - Smaller app size (~5MB vs ~100MB)
  - Better security (Rust memory safety, no Node.js exposure)
  - Learning curve for Rust backend development
  - Smaller ecosystem than Electron
- **Alternatives Considered:**
  - Electron: Rejected due to large bundle size and security concerns
  - Progressive Web App: Rejected due to no secure API key storage
  - Native Swift/Kotlin: Rejected due to separate codebases for iOS/Android
-->

---

## 3. Data Models

### Schema

**[EntityName]** (`path/table_name`)

```
{
  // Example:
  id: string;
  field: type; // description
  field: type;
  nested: {
    field: type;
  }
}
```

**[EntityName2]**

```
{
  // repeat for each entity
}
```

<!-- Example:
{
  "noteId": "note_abc123",
  "title": "Diabetes Management - Week 3",
  "content": "<p>Type 2 DM characterized by insulin resistance...</p>",
  "subject": "medsurg",
  "tags": ["diabetes", "insulin"],
  "createdAt": "2025-11-15T10:30:00Z",
  "updatedAt": "2025-11-19T14:22:00Z",
  "wordCount": 847,
  "isFavorite": true
}

 -->

### Relationships

```
EntityA (1) ──< (many) EntityB
EntityC (many) ──< (many) EntityD via [joinField]
```

<!-- Example:

User (1) ──< (many) Notes
Note (many) ──< (many) Definitions via tags/content references

-->

### Indexes

- `entityA(field1, field2 DESC)` - purpose
- `entityB(field)` - purpose
- ...

<!-- Example:

notes(userId, updatedAt DESC) - fetch user's recent notes
notes(userId, subject) - filter by subject area
definitions(term) - fast term lookup for autocomplete
 -->

### Validation

**EntityA:**

- `field`: constraints
- `field`: constraints
- ...

**EntityB:**

- [Repeat for each entity]

<!-- Example:

Notes:

title: 1-200 characters, required
content: max 50,000 characters
tags: max 10 tags per note
subject: must be one of enum values

-->

## 4. API/Interface Specifications

### Endpoints

**[Endpoint Name]**

```
[METHOD] /path/to/endpoint
```

<!-- Example:

POST /api/notes

 -->

**Request:**

```typescript
{
  field: type;                  // description
  field?: type;                 // optional field
}
```

<!-- Example:

{
  title: string;
  content: string;
  subject: 'pharmacology' | 'medsurg' | 'pediatrics' | 'mental-health' | 'other';
  tags?: string[];              // optional
}
 -->

**Response:**

```typescript
{
  field: type;
  field: type;
}
```

<!--
{
  noteId: string;
  createdAt: string;            // ISO timestamp
  message: "Note created successfully"
}
 -->

**Errors:**

- `400` - [error condition]
- `401` - [error condition]
- `404` - [error condition]

<!--
- `400` - Invalid subject or title exceeds 200 chars
- `401` - Unauthenticated user
- `429` - Rate limit exceeded

 -->

**[Second Endpoint]**

<!-- Repeat the same structure for the second endpoint and other endpoints as needed -->

### Internal APIs _(if applicable)_

**[Component/Service Name]**

`functionName(param: type): returnType`

- **Purpose:** [what it does]
- **Example:** `functionName(value)` → `result`

<!--

noteService.ts
saveNoteLocally(note: Note): Promise<void>

Purpose: Cache note to local storage for offline access
Example: saveNoteLocally(myNote) → saves to IndexedDB


 -->

### IPC/Event Messages _(for Tauri, Electron, etc.)_

**[Command Name]**

```typescript
Frontend → Backend
{
  command: 'command_name';
  payload: {
    field: type;
  };
}

Backend → Frontend
{
  data: type;
  error?: string;
}
```

<!--

save_note
typescriptFrontend → Backend
{
  command: 'save_note';
  payload: {
    noteId?: string;            // omit for new notes
    title: string;
    content: string;
    subject: string;
    tags: string[];
  };
}

Backend → Frontend
{
  data: {
    noteId: string;
    savedAt: string;
  };
  error?: string;
}


 -->

## 5. Authentication & Security

### Authentication & Authorization

**Authentication:**

- Method: [e.g., Firebase Auth, JWT, OAuth]
- Session duration: [e.g., 7 days, refresh tokens]

**Authorization:**

- User can only access their own [resources]
- [Role/permission model if applicable]
- ... [Role/permission model if applicable]

<!--
Example:

Authentication:

Method: Firebase Authentication (email/password)
Session duration: 30 days with refresh tokens

Authorization:

Users can only access their own notes and study materials
Firebase Security Rules enforce userId matching on all queries
Admin role for content moderation (future)

 -->

### Data Protection

**At Rest:**

- [Sensitive data type]: encrypted using [method/algorithm]
- [Data type]: stored in [location] with [protection]

**In Transit:**

- All API calls: HTTPS/TLS 1.3
- [Specific connections]: [encryption method]

<!--
Example:

At Rest:

OpenAI API keys: encrypted in Tauri secure storage (OS keychain)
User notes: encrypted by Firebase at rest (AES-256)
Local cache: stored in encrypted SQLite database

In Transit:

All Firebase calls: HTTPS/TLS 1.3
OpenAI API calls: HTTPS with API key in headers (never in URL)
Tauri IPC: secure by default (no network exposure)

 -->

### API Security

**Rate Limiting:**

- [Endpoint/function]: [X] requests per [timeframe]

**Input Validation:**

- [Field]: sanitized for [threat type]
- [Field]: validated against [pattern/rules]

**API Keys:**

- Stored in: [environment variables, secure vault]
- Never exposed in: [client-side code, logs, error messages]

<!--
Example:

Rate Limiting:

AI autocomplete: 100 requests per hour per user
Definition lookup: 500 requests per hour per user
Note saves: 1000 requests per hour per user

Input Validation:

Note content: sanitized for XSS attacks, max 50,000 chars
Note titles: alphanumeric + basic punctuation, max 200 chars
Tags: validated against regex pattern, max 10 per note
AI prompts: stripped of prompt injection attempts


API Keys:

Stored in: Tauri secure storage (never in localStorage)
Never exposed in: client-side code, console logs, error messages
OpenAI key rotation: every 90 days


 -->

### Privacy & Compliance

**Data Collection:**

- We collect: [list minimal data collected]
- We don't collect: [list what you avoid]

**User Rights:**

- Data export: [how users can export]
- Data deletion: [how users can delete account/data]

**Compliance:** _(if applicable)_

- [GDPR, HIPAA, FERPA, COPPA]: [how you comply]

<!--
Example:

Privacy & Compliance
Data Collection:

We collect: email, notes, study progress, AI usage metrics
We don't collect: real patient data, PHI, location, browsing history

User Rights:

Data export: "Export All Notes" button → downloads JSON
Data deletion: "Delete Account" → removes all user data within 30 days
Data portability: notes exportable as Markdown or PDF

Compliance:

FERPA: Student education records kept private, no third-party sharing
GDPR: EU users have right to erasure, data portability
Not HIPAA-covered: App is for educational notes, not clinical documentation


 -->

### Threat Mitigation

**[Threat Type]:**

- Risk: [description]
- Mitigation: [how you handle it]

<!--
Example:

Prompt Injection (AI):

Risk: Malicious users try to manipulate AI responses
Mitigation: System prompts locked, user input sanitized, max token limits

XSS (Cross-Site Scripting):

Risk: Malicious code in note content executes in editor
Mitigation: DOMPurify sanitization, Content Security Policy headers

Data Leakage:

Risk: User A sees User B's notes due to authorization bug
Mitigation: Firebase Security Rules enforce userId checks, integration tests verify isolation

API Key Theft:

Risk: OpenAI key stolen from client-side code
Mitigation: Keys only stored in Tauri backend (Rust), never sent to frontend

Account Takeover:

Risk: Weak passwords or credential stuffing
Mitigation: Firebase Auth enforces strong passwords, email verification required, rate limit login attempts

Offline Data Exposure:

Risk: Someone accesses laptop and reads cached notes
Mitigation: Local database encrypted, requires re-authentication after 7 days idle
 -->

## 6. Testing Strategy

Here's a lean Testing Strategy template:

---

## Testing Strategy

### Test Types

**Unit Tests**

- **What:** [components/functions to test]
- **Tool:** [e.g., Jest, Vitest, pytest]
- **Coverage goal:** [e.g., 80% of business logic]

**Integration Tests**

- **What:** [component interactions, API endpoints]
- **Tool:** [e.g., React Testing Library, Supertest]
- **Focus:** [critical flows to test]

**End-to-End Tests**

- **What:** [user flows from start to finish]
- **Tool:** [e.g., Playwright, Cypress]
- **Scenarios:** [list key user journeys]

<!--
Example:

Unit Tests

- What: Utility functions, validation logic, state management, data transformers
- Tool: Vitest + React Testing Library
- Coverage goal: 80% of business logic (services, utils, hooks)

Integration Tests

- What: Tauri IPC commands, Firebase operations, AI service integration, note CRUD flows
- Tool: Vitest with mocked Tauri API, Firebase emulator
- Focus: Save/load notes, AI completion pipeline, definition lookup

End-to-End Tests

- What: Complete user workflows in real desktop app
- Tool: Playwright (can test Tauri apps)
- Scenarios: Create note → AI autocomplete → save → retrieve, Generate flashcards flow, Definition lookup



 -->

### Critical Test Cases

**[Feature/Flow Name]:**

- Test: [what you're testing]
- Expected: [expected behavior]
- Edge case: [unusual scenario]

**[Second Feature]:**

- Test: [what you're testing]
- Expected: [expected behavior]
- Edge case: [unusual scenario]

**[Third Feature]:**

<!-- Repeat the same structure for the third feature as needed -->

<!--
Example:

Note Creation & Saving:

Test: User creates note with title, content, tags
Expected: Note saved to Firestore with correct userId, appears in notes list
Edge case: Offline mode - note cached locally, syncs when online


 -->

### Test Execution

**When tests run:**

- Unit tests: [e.g., on every commit, pre-push hook]
- Integration tests: [e.g., on PR, CI pipeline]
- E2E tests: [e.g., before deployment, nightly]

**CI/CD integration:** [how tests run in pipeline]

<!--

Example:

When tests run:

- Unit tests: on every file save (watch mode), pre-commit hook
- Integration tests: on PR creation, merge to main
- E2E tests: before production release, weekly on staging

CI/CD integration:

- GitHub Actions workflow triggers on PR
- Run unit + integration tests (must pass to merge)
- E2E tests run on staging environment nightly
- Deployment blocked if tests fail

 -->

### Coverage Goals

- Minimum coverage: [percentage]
- Must cover: [critical paths that need 100% coverage]
- Can skip: [what doesn't need tests]

<!--
Example:

Coverage Goals

Minimum coverage: 70% overall
Must cover: Validation logic (100%), AI service layer (90%), note CRUD (90%)
Can skip: UI components without logic, third-party library wrappers, mock data generators

Mocking
 -->

### Mocking

**External services mocked:**

- [Service name]: [how you mock it]
- [Service name]: [how you mock it]
- ...
- [API name]: [mock strategy]
- [API name]: [mock strategy]
- ...

<!--
Example:

External services mocked:

- OpenAI API: Mock responses with fixtures for common prompts, simulate timeouts/errors
- Firebase Firestore: Use Firebase emulator for integration tests, mock SDK for unit tests
- Tauri IPC: Mock invoke() calls with test doubles
- System APIs: Mock OS keychain access for API key storage tests

 -->

### Performance & Optimization

**Performance Targets:**

- Page load time: [target, e.g., <2s]
- Time to interactive: [target]
- API response time: [target]
- Database query time: [target]

**Optimization Strategies:**

- [Strategy 1: e.g., Code splitting, lazy loading]
- [Strategy 2: e.g., Image optimization, CDN]
- [Strategy 3: e.g., Database indexing, query optimization]

**Bottleneck Monitoring:**

- Tool: [e.g., Lighthouse, WebPageTest, React DevTools Profiler]
- Metrics: [Core Web Vitals, custom metrics]

<!--
Example:

Performance Targets:

- Page load time: <1.5s on 4G connection
- Time to interactive: <2s
- API response time: <500ms for note operations
- Database query time: <100ms for list queries

Optimization Strategies:

- Code splitting: Lazy load AI features, study mode only when needed
- Image optimization: WebP format, responsive images with srcset
- Database indexing: Composite indexes on (userId, updatedAt) for fast note retrieval
- Caching: Redis for AI completions, Service Worker for offline assets
- Bundle size: Tree-shaking, remove unused dependencies, aim for <200KB initial JS

Bottleneck Monitoring:

- Tool: Lighthouse CI in GitHub Actions, React DevTools Profiler for component renders
- Metrics: Largest Contentful Paint (LCP < 2.5s), First Input Delay (FID < 100ms), Cumulative Layout Shift (CLS < 0.1)
- Custom metrics: Time to first note render, AI autocomplete response time
-->

## 7. Deployment & Operations

### Build Process

**Development:**

```bash
[commands to run locally]
```

**Production:**

```bash
[commands to build for production]
```

**Environment variables:**

- `VAR_NAME`: [description]
- `VAR_NAME`: [description]

<!--
Example:

Development:

```bash
bashnpm run dev          # Start frontend dev server
python train.py      # Train models locally with sample data
pytest tests/        # Run unit tests
```

Production:

```bash
bashnpm run build                    # Build React frontend
python scripts/train_models.py   # Train models with full dataset
docker build -t nba-predictor .  # Create Docker image
docker push nba-predictor:latest # Push to registry
```
Environment variables:

- ODDS_API_KEY: API key for odds data provider
- NBA_STATS_API_KEY: NBA official stats API key
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis cache for predictions
- MODEL_VERSION: Current ML model version (e.g., v2.3.1)

 -->

### Deployment

**Platform:** [e.g., Vercel, AWS, Desktop app distribution]

**Steps:**

1. [Step to deploy]
2. [Step to deploy]
3. [Step to deploy]

**Frequency:** [e.g., on every merge to main, manual releases]

<!--
Example:

Platform: AWS (EC2 + S3 + RDS)
Steps:

1. Trigger GitHub Actions workflow on merge to main
2. Run tests and build Docker image
3. Push image to AWS ECR
4. Deploy to EC2 via AWS CodeDeploy (rolling update)
5. Update model files in S3 bucket
6. Run database migrations (if any)
7. Warm up Redis cache with tonight's games

Frequency:

- Frontend: on every merge to main (automated)
- ML models: daily at 6 AM EST (before games start)
- Database schema: manual with approval

 -->

### Monitoring

**Metrics tracked:**

- [Metric]: [tool/method]
- [Metric]: [tool/method]

**Error tracking:** [tool - e.g., Sentry, LogRocket]

**Alerts:** [when/how you get notified]

<!--
Example:

Metrics tracked:

- Prediction accuracy: daily calculation stored in TimescaleDB
- API response times: CloudWatch (alert if >2s)
- Model performance: track ROI, win rate, Brier score
- Cache hit rate: Redis stats (target >80%)
- Error rate: Sentry (alert if >1%)

  Error tracking: Sentry for backend, LogRocket for frontend

Alerts:

- Slack webhook for deployment failures
- PagerDuty for prediction service downtime (>5 min)
- Email if prediction accuracy drops below 52% over 10 games
PagerDuty for prediction service downtime (>5 min)
Email if prediction accuracy drops below 52% over 10 games
 -->

#### Observability & Telemetry

**Logging:**

- Structured logging format: [JSON, logfmt]
- Log levels: DEBUG, INFO, WARN, ERROR, FATAL
- Log aggregation: [tool - e.g., CloudWatch, Datadog]
- Retention: [policy]

**Tracing:**

- Distributed tracing: [tool - e.g., OpenTelemetry, Jaeger]
- Trace sampling rate: [percentage]
- Critical paths traced: [list key user flows]

**Metrics:**

- Business metrics: [DAU, conversion rates, feature usage]
- Technical metrics: [response times, error rates, resource usage]
- Custom metrics: [domain-specific KPIs]

<!--
Example:

Logging:

- Structured logging format: JSON with timestamp, level, service, message, context
- Log levels: DEBUG (dev only), INFO (requests/responses), WARN (degraded performance), ERROR (failures), FATAL (crash)
- Log aggregation: CloudWatch Logs with log groups per service
- Retention: 30 days for INFO, 90 days for ERROR/FATAL

Tracing:

- Distributed tracing: OpenTelemetry with Jaeger backend
- Trace sampling rate: 100% for errors, 10% for successful requests
- Critical paths traced: Note save flow, AI completion pipeline, auth flow

Metrics:

- Business metrics: DAU, notes created/day, AI autocomplete acceptance rate
- Technical metrics: P95 API response time, error rate, Firestore read/write counts
- Custom metrics: Offline sync queue depth, AI token usage per user
-->

### Rollback

**If deployment fails:**

1. [Rollback step]
2. [Rollback step]

**Database migrations:** [how you handle rollback with schema changes]

<!--
Example:

If deployment fails:

1. Trigger rollback via AWS CodeDeploy console
2. Revert to previous Docker image tag
3. Restore previous model version from S3
4. Clear Redis cache to prevent stale predictions
5. Verify with health check endpoint

Database migrations:

- Use Alembic migrations with up and down scripts
- Take RDS snapshot before migration
- Test rollback on staging first
- Rollback: alembic downgrade -1 + restore snapshot if needed

 -->

### Maintenance

**Updates:** [how often, what gets updated]  
**Backups:** [frequency, retention policy]  
**Dependencies:** [update schedule]

<!--

Example:

Updates:

- Model retraining: daily with previous night's game results
- Dependency updates: weekly security patches, monthly major updates
- Historical data refresh: full re-scrape every off-season

Backups:

- RDS automated backups: daily, 7-day retention
- Model artifacts in S3: versioned, 90-day retention
- Prediction logs: archived to S3 Glacier after 30 days

Dependencies:

- Python packages: update monthly, pin versions
- NBA Stats API: monitor for breaking changes (historically unstable)
- Odds provider: have backup provider (DraftKings API) if primary fails

Scheduled jobs:

- 6:00 AM EST: Retrain models with last night's results
- 10:00 AM EST: Scrape odds for tonight's games
- 5:00 PM EST: Generate predictions for tonight's slate
- 11:00 PM EST: Update prediction accuracy metrics
- Sunday 3:00 AM EST: Weekly model performance report

 -->

### Disaster Recovery

**Backup Strategy:**

- RTO (Recovery Time Objective): [e.g., 4 hours]
- RPO (Recovery Point Objective): [e.g., 1 hour]
- Backup frequency: [schedule]
- Backup testing: [how often you verify restores]

**Failure Scenarios:**

- Database corruption: [recovery procedure]
- Complete service outage: [recovery steps]
- Data center failure: [multi-region strategy]
- Ransomware/security breach: [incident response]

<!--
Example:

Backup Strategy:

- RTO (Recovery Time Objective): 4 hours - app restored within 4 hours of incident
- RPO (Recovery Point Objective): 15 minutes - max 15 minutes of data loss
- Backup frequency: Firestore continuous backup, local cache snapshots every 6 hours
- Backup testing: Monthly restore drills to verify backup integrity

Failure Scenarios:

Database corruption:
1. Switch to Firestore point-in-time recovery
2. Restore to last known good state (up to 7 days back)
3. Verify data integrity with automated tests
4. Notify affected users if data was lost

Complete service outage:
1. Verify offline mode keeps app functional for existing users
2. Activate status page at status.nexlyrn.com
3. Switch to backup Firebase project if primary is down
4. Monitor recovery and communicate ETA to users

Data center failure:
- Firebase multi-region replication enabled (automatic failover)
- Static assets served from CDN with multiple edge locations
- Local-first architecture ensures app works offline

Ransomware/security breach:
1. Immediately revoke all API keys and rotate secrets
2. Lock down affected accounts and reset passwords
3. Restore from clean backup (pre-breach)
4. Conduct security audit and patch vulnerabilities
5. Notify users per privacy policy requirements
-->

## 8. Implementation Details

### Core Features

**[Feature Name]**

**How it works:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Key logic:**

- [Important algorithm or business rule]
- [Edge case handling]

**Code snippet:** _(optional)_

```typescript
// Brief example of critical logic
```

---

**[Second Feature]**

<!-- Repeat the same structure for the second feature as needed -->

**How it works:**
[Brief description]

**Key logic:**
[Important decisions]

<!-- Example:

Core Features
AI Autocomplete
How it works:

User types in note editor, debounce captures last 200 characters
Frontend sends context via IPC to Tauri backend
Backend constructs prompt: system instructions + nursing context + user text
OpenAI API returns completion suggestions
Frontend displays inline suggestions, user accepts with Tab key

Key logic:

Debounce delay: 800ms to avoid excessive API calls
Context window: last 200 chars + current sentence for relevance
Caching: identical contexts cached for 5 minutes to save API costs
Token limit: 100 tokens per completion to control costs

Code snippet:

```typescript
const debounceCompletion = debounce(async (text: string) => {
  const context = text.slice(-200); // Last 200 chars
  const cached = completionCache.get(context);
  if (cached) return cached;

  const result = await invoke('get_ai_completion', { context });
  completionCache.set(context, result, 300000); // 5 min cache
  return result;
}, 800);
```
 -->

### Technical Decisions

**[Decision topic - e.g., "State Management"]**

- **Choice:** [What you chose]
- **Why:** [Reason]
- **Alternative considered:** [What you didn't choose and why]

**[Second Decision]**

- **Choice:** [What you chose]
- **Why:** [Reason]

<!--

Example:

Desktop vs Web Deployment

Choice: Desktop-first with Tauri
Why: Better offline support, secure API key storage, native performance
Alternative considered: Web app (Vite + React) - rejected due to API key exposure risk and offline limitations
 -->

### Algorithms _(if applicable)_

**[Algorithm name - e.g., "Autocomplete Matching"]**

- **Purpose:** [What it does]
- **Approach:** [How it works]
- **Time complexity:** [e.g., O(n log n)]

<!--

Example:
Autocomplete Context Window

Purpose: Determine relevant text to send to AI for completion
Approach: Extract last 200 chars + current incomplete sentence, prioritize recent typing over older context
Time complexity: O(1) - simple string slicing

 -->

### Edge Cases

**[Scenario]:** [How you handle it]  
**[Scenario]:** [How you handle it]

<!--
Example:

Offline mode: Notes cached locally in encrypted SQLite, sync queue processes when reconnected

 -->

## 9. Future Work

### Future Features (Post-MVP)

**[Feature name]:**

- **Description:** [What it does]
- **Why later:** [Reason for deferral]
- **Priority:** [High/Medium/Low]

**[Second feature]:**

- **Description:** [Brief description]
- **Why later:** [Reason]

<!--
Example:

Collaborative Study Groups:

Description: Users can share notes and study together, comment on each other's flashcards
Why later: MVP focused on individual learning; collaboration adds complexity (permissions, moderation)
Priority: High (requested by 60% of beta testers)

 -->

### Known Technical Debt

Use this table format for better tracking and prioritization:

| ID | Component | Issue | Impact | Effort | Priority | Target Date |
|---|---|---|---|---|---|---|
| TD-001 | [Component] | [Issue description] | [Impact on system/users] | [Time estimate] | High/Medium/Low | [YYYY-MM-DD] |
| TD-002 | [Component] | [Issue description] | [Impact on system/users] | [Time estimate] | High/Medium/Low | [YYYY-MM-DD] |

<!--
Example:

| ID | Component | Issue | Impact | Effort | Priority | Target Date |
|---|---|---|---|---|---|---|
| TD-001 | Auth | No MFA support | Security risk for user accounts | 2 weeks | High | 2025-06-01 |
| TD-002 | Cache | No backup for local cache | Data loss if laptop fails before sync | 1 week | Medium | 2025-07-15 |
| TD-003 | Editor | Rich text parsing performance | Slow load for notes >10k words | 3 days | Low | 2025-08-01 |
| TD-004 | AI Service | No retry logic for API failures | Users lose autocomplete on network blips | 2 days | High | 2025-05-15 |
| TD-005 | Database | Missing indexes on tags query | Slow tag-based note filtering | 1 day | Medium | 2025-06-30 |

 -->

### Out of Scope

- [Item explicitly not included in this version]
- [Feature that won't be built]
- [Integration that's deferred]

<!--
Example:

- **Real-time collaboration (Google Docs-style co-editing)**
- **Integration with Electronic Health Records (EHR systems)**
- **Clinical rotation scheduling/tracking**
- **Peer review or instructor feedback workflows**
- **Video lessons or tutorials**
- **Integration with university LMS (Canvas, Blackboard)**
- **Medication calculation tools**
- **Clinical assessment checklists**
- **HIPAA-compliant patient data storage (app is for education only, not clinical use)**

 -->

### Research Needed

**[Topic]:**

- **What:** [What needs investigation]
- **Why:** [Purpose of research]
- **Estimated effort:** [Time needed]

<!--
Example:

Spaced Repetition Algorithm Optimization:

- **What:** Test modified SM-2 vs Anki's algorithm vs custom nursing-optimized intervals
- **Why:** Current algorithm is generic; nursing concepts may need different spacing
- **Estimated effort:** 2 weeks (implement variants, run experiments with beta users)

 -->
