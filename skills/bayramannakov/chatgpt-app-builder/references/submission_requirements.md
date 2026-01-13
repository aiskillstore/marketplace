# App Submission Requirements

Complete checklist and requirements for submitting to the ChatGPT App Store.

## Pre-Submission Requirements

### Organization Verification
- [ ] OpenAI Platform organization verified
- [ ] Individual or business verification completed in Dashboard
- [ ] Submitter has Owner role in organization

### Technical Requirements
- [ ] MCP server hosted on publicly accessible HTTPS domain
- [ ] No localhost or testing endpoints
- [ ] CSP configured with exact domains (no wildcards unless necessary)
- [ ] Streaming HTTP responses supported
- [ ] Server responds within reasonable timeout

### Data Residency
- [ ] Using global data residency project (EU residency not supported for apps)

### Required Endpoints
Your server must implement these endpoints:

#### 1. Domain Verification Challenge
```
Path: /.well-known/openai-apps-challenge
Method: GET
Response: Plain text challenge token (provided by OpenAI)
Content-Type: text/plain
```

Example implementation:
```typescript
if (url.pathname === '/.well-known/openai-apps-challenge') {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('YOUR_CHALLENGE_TOKEN_HERE');
  return;
}
```

#### 2. Privacy Policy Page
```
Path: /privacy
Method: GET
Response: HTML page with privacy policy
Content-Type: text/html
```

Required sections:
- Information collected and how it's used
- Data storage and retention practices
- Third-party services used
- Data sharing policies
- User rights
- Contact information

#### 3. Terms of Service Page
```
Path: /terms
Method: GET
Response: HTML page with terms of service
Content-Type: text/html
```

Required sections:
- Service description
- Acceptable use policy
- Data and privacy (link to privacy policy)
- Intellectual property
- Disclaimers and limitation of liability
- Rate limits and usage restrictions
- Modifications and termination
- Governing law
- Contact information

#### 4. MCP Endpoint
```
Path: /mcp (or your configured path)
Method: GET (SSE connection), POST (messages)
Response: Server-Sent Events stream
```

#### 5. Health Check
```
Path: / or /health
Method: GET
Response: JSON with status
```

Example:
```typescript
if (url.pathname === '/' || url.pathname === '/health') {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'ok', name: 'your-app-name' }));
  return;
}
```

---

## Tool Requirements

### Naming
- [ ] Tool names are snake_case with service prefix
- [ ] Names are action-oriented (verb_noun pattern)
- [ ] Names are unique within your connector

**Good**: `taskflow_get_tasks`, `taskflow_create_task`
**Bad**: `getTasks`, `task-list`, `myTool1`

### Descriptions
- [ ] Each tool has clear, specific description
- [ ] Descriptions start with "Use this when..."
- [ ] Descriptions explain what user will get back
- [ ] No marketing language or competitor comparisons
- [ ] No recommendations for overly broad triggering

### Annotations
- [ ] `readOnlyHint: true` for data retrieval tools
- [ ] `destructiveHint: true` for delete/modify tools
- [ ] `openWorldHint: true` for external system interactions
- [ ] Annotations are accurate (common rejection reason)

### Input Design
- [ ] Only request necessary parameters
- [ ] No "just in case" fields
- [ ] No request for full conversation history
- [ ] No raw transcript or broad context fields
- [ ] Parameters have clear descriptions

---

## Content & Commerce Requirements

### Prohibited Content
Your app must NOT contain:
- [ ] Adult/explicit sexual content
- [ ] Gambling or betting services
- [ ] Illegal drugs or controlled substances
- [ ] Weapons, explosives, dangerous materials
- [ ] Counterfeit or stolen goods
- [ ] Fake IDs or fraudulent documents
- [ ] Malware or malicious code

### Prohibited Commerce
Your app must NOT sell:
- [ ] Digital products, subscriptions, tokens, or credits
- [ ] Advertisements
- [ ] Cryptocurrency speculation/trading services
- [ ] Unregulated financial services
- [ ] Prescription medications
- [ ] High-chargeback travel services

**Allowed**: Physical goods only, via external checkout

### Data Collection Restrictions
Your app must NEVER collect:
- [ ] Payment card information (PCI DSS)
- [ ] Protected health information (PHI)
- [ ] Social security numbers
- [ ] Passwords, API keys, or MFA codes
- [ ] Full chat logs or conversation history
- [ ] Location data via input fields (use system channels)

---

## Widget Requirements

### Rendering
- [ ] Widget renders without JavaScript errors
- [ ] Widget works on mobile devices
- [ ] Widget supports dark mode
- [ ] Widget handles empty states gracefully
- [ ] Widget loads within reasonable time

### CSP Configuration
- [ ] Only necessary domains in `connect_domains`
- [ ] Only necessary domains in `resource_domains`
- [ ] `frame_domains` only if embedding iframes (triggers stricter review)
- [ ] No overly broad wildcards

---

## Authentication Requirements (if applicable)

### OAuth Setup
- [ ] `/.well-known/oauth-protected-resource` endpoint accessible
- [ ] `/.well-known/oauth-authorization-server` endpoint accessible
- [ ] PKCE (S256) supported
- [ ] Redirect URIs configured:
  - `https://chatgpt.com/connector_platform_oauth_redirect`
  - `https://platform.openai.com/apps-manage/oauth`

### Test Credentials
- [ ] Test account created with sample data
- [ ] Credentials documented for reviewers
- [ ] Test account has full functionality
- [ ] No 2FA required for test account
- [ ] Sample data demonstrates all features

---

## Metadata Requirements

### Connector Metadata
- [ ] Name is clear and descriptive
- [ ] Name accurately represents functionality
- [ ] Description explains what the app does
- [ ] Description explains when to use it
- [ ] Screenshots meet dimension requirements (if required)

### Accuracy
- [ ] Metadata accurately represents functionality
- [ ] No misleading claims
- [ ] No impersonation of other services

---

## Quality Requirements

### Functionality
- [ ] App reliably does what it promises
- [ ] Error handling is graceful with actionable messages
- [ ] No incomplete or demo-only features
- [ ] Consistent behavior across multiple uses

### Testing
- [ ] Tested with golden prompt set (direct, indirect, negative)
- [ ] Direct prompts trigger correctly
- [ ] Indirect prompts trigger correctly
- [ ] Negative prompts do NOT trigger
- [ ] Widget interactions work as expected

---

## Age & Safety Requirements

- [ ] App suitable for users 13+
- [ ] No content targeting children under 13
- [ ] Adult (18+) content has age verification (if applicable)
- [ ] Complies with OpenAI usage policies

---

## Submission Process

### Step 1: Access Dashboard
Go to: `platform.openai.com/apps-manage`

### Step 2: Enter Details
- MCP server URL (your `/mcp` endpoint)
- OAuth metadata (if authentication required)
- Connector name and description
- Category selection

### Step 3: Compliance Confirmation
Check all required compliance boxes:
- [ ] Confirm ownership of intellectual property
- [ ] Confirm compliance with OpenAI policies
- [ ] Confirm accuracy of metadata
- [ ] Confirm test credentials provided (if auth required)

### Step 4: Submit
Click "Submit for Review"

**Note**: Only one version per app can be in review at a time.

---

## Post-Submission

### Timeline
- Review typically takes several business days
- Status updates sent via email
- Check Dashboard for current status

### If Rejected
Common rejection reasons:
1. Incorrect or missing tool annotations
2. Missing or non-functional test credentials
3. Prohibited content or commerce
4. Incomplete functionality
5. Misleading metadata

Fix issues and resubmit.

### After Approval
1. Click "Publish" button in Dashboard
2. App becomes discoverable in ChatGPT Apps Directory
3. Users can find via direct links or search

---

## Ongoing Requirements

### Updates
Tool names, signatures, and descriptions are locked after publication.
Modifications require new review.

### Maintenance
- Keep app functional and responsive
- Inactive or unstable apps may be removed
- Non-compliant apps may be removed without notice

### Contact
- Maintain accurate customer support contact
- Respond to user issues promptly

---

## Quick Checklist

Copy this for final review:

```
PRE-SUBMISSION
[ ] Organization verified
[ ] HTTPS endpoint live
[ ] CSP configured

TOOLS
[ ] Snake_case naming with prefix
[ ] Clear descriptions
[ ] Correct annotations
[ ] Minimal inputs

CONTENT
[ ] No prohibited content
[ ] No prohibited commerce
[ ] No restricted data collection

WIDGET
[ ] Renders correctly
[ ] Mobile compatible
[ ] Dark mode support

AUTH (if applicable)
[ ] Well-known endpoints
[ ] Test credentials ready

TESTING
[ ] Golden prompts pass
[ ] Widget interactions work
[ ] Error handling works

METADATA
[ ] Accurate name/description
[ ] No misleading claims
```
