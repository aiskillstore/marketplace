# Universal Software Engineering Audit Specification

**Version:** 2.2
**Status:** Production audit standard
**Purpose:** Evidence-based, full-lifecycle software engineering audit standard for human and automated-tool-assisted auditors
**Updated:** 2026-07-10
**Supersedes:** Version 2.1
**License:** CC BY 4.0 - free to use, adapt, and redistribute with attribution
**Revision purpose:** Closes the remaining determinism gaps: normative control-to-category mapping, complete WARN scoring rules, cross-tier coverage disclosure, and gate-control separation.

---

## 1. Purpose and Authority

This specification defines a comprehensive, repeatable method for determining whether a software product is suitable for its intended production use.

The audit covers the complete system from product purpose and user experience through source code, data, infrastructure, deployment, operations, recovery, privacy, and retirement.

The auditor must be rigorous without becoming theatrical, speculative, or needlessly punitive. Findings and recommendations must be anchored in observable evidence, realistic risk, and measurable value.

This specification does not authorize penetration testing, production load testing, destructive actions, access-control bypass, data modification, or any other intrusive activity. Authorization must be established separately in the Rules of Engagement.

---

## 2. Mission

Act as an independent senior software assurance team.

Determine:

1. Whether the application performs its intended job reliably.
2. Whether users, data, systems, and business operations are adequately protected.
3. Whether the product can be deployed, operated, recovered, maintained, and retired safely.
4. Whether release risks are known, evidenced, owned, and proportionate.
5. Whether improvements have sufficient user, business, security, reliability, compliance, or maintainability value to justify their cost.

Do not guess.
Do not invent defects.
Do not manufacture recommendations to fill a quota.
Do not confuse missing evidence with proof of failure.
Do not confuse the absence of observed defects with proof of safety.
Do not soften verified material risk.
Do not use intimidating language to exaggerate minor issues.

When evidence is insufficient, state **UNVERIFIED** and identify exactly what would be required to verify it.

---

## 3. Core Trust Principles

1. **Evidence over assumption:** Every conclusion must be traceable to evidence.
2. **Proportionality:** Severity must reflect credible impact and likelihood, not auditor preference.
3. **Reproducibility:** Another qualified reviewer should be able to repeat the material checks.
4. **Least disruption:** Use the safest test capable of answering the question.
5. **Context matters:** Controls must be judged against the product, data, users, threat model, and intended scale.
6. **Verified positives:** PASS requires affirmative evidence, not silence from a scanner.
7. **Clear uncertainty:** Separate verified facts, supported inferences, assumptions, and unknowns.
8. **Remediation restraint:** Recommend the smallest robust correction before proposing redesign.
9. **No novelty tax:** Do not recommend new tools, services, dependencies, or architecture without demonstrated value.
10. **No false precision:** Scores must disclose evidence coverage and confidence.
11. **Safe disclosure:** Do not expose secrets, personal information, exploit details, or sensitive system data in the report.
12. **Independent judgment:** Tool output is evidence to assess, not a verdict to repeat.

---

## 4. Auditor Perspectives

Use the following perspectives as analytical lenses:

1. Product and business assurance
2. Application security and penetration testing
3. Software architecture
4. Full-stack engineering
5. Data and database architecture
6. Cloud, infrastructure, and DevOps
7. Site reliability and incident response
8. Quality engineering
9. Performance engineering
10. Product design and user experience
11. Accessibility
12. Privacy, data governance, and compliance
13. Supply-chain and dependency assurance
14. Desktop, mobile, or embedded engineering when applicable
15. Model-system assurance when applicable

These perspectives are not separate reports. Maintain one evidence ledger, consolidate duplicate observations, and produce one coherent set of findings. A finding affecting multiple disciplines must be recorded once and cross-tagged.

---

## 5. Audit Classification

Before work begins, declare the audit type:

- **Document review:** Policies, diagrams, requirements, and records only.
- **Source review:** Repository and configuration inspection without runtime access.
- **Black-box runtime review:** Runtime behavior without repository access.
- **Grey-box review:** Runtime access plus limited source, credentials, or architecture context.
- **Full-stack audit:** Repository, runtime, infrastructure, data, deployment, and operational evidence.
- **Release audit:** Assessment of a specific version or release candidate.
- **Focused audit:** Explicitly limited domains or controls.

Also declare:

- Depth: rapid, standard, or deep
- Environment: local, development, staging, production, or mixed
- Access level: none, read-only, test-user, privileged test-user, administrator, infrastructure, or other
- Assurance objective: advisory, release decision, customer assurance, internal control, regulatory support, acquisition review, or other

Never present a limited audit as a full production assurance review.

### 5.1 Audit Identifier

Assign every engagement an immutable identifier:

`AUD-[PRODUCT]-[YYYYMMDD]-[SEQUENCE]`

Example: `AUD-WG-20260710-001`.

Use the audit ID in the report, evidence ledger, findings, score sheet, exported artifacts, re-audits, and retained evidence. Finding IDs use `AUD-ID-FNNN`; evidence IDs use `AUD-ID-ENNN`; accepted-risk IDs use `AUD-ID-RNNN`.

### 5.2 Depth Tiers

| Requirement | Rapid | Standard | Deep |
|---|---|---|---|
| Primary purpose | Early risk screen | Production-readiness decision | High-assurance or high-consequence review |
| Typical control selection | All Core controls | Core plus applicable Standard controls | All applicable Core, Standard, and Deep controls |
| Evidence sources | Documents, source/config sampling, safe runtime checks | Correlated source, runtime, configuration, pipeline, and operations evidence | Standard evidence plus independent reproduction, specialized testing, and broader sampling |
| User journeys | Critical path only | All critical and major supporting paths | Critical, supporting, adversarial, failure, and recovery paths |
| Roles tested | Highest-risk roles | Every materially distinct role | Every role plus transitions, delegated access, and abuse cases |
| Dependency review | Direct production dependencies | Direct and material transitive dependencies | Reachability, provenance, build chain, and targeted manual validation |
| Performance | Static review and existing evidence | Representative safe tests or credible operational data | Authorized capacity, endurance, failure, and recovery testing |
| Recovery | Configuration and recent evidence | Restoration evidence for critical data | Witnessed or independently verified recovery exercise |
| Independent challenge | Auditor quality gate | Separate contradiction pass | Independent adversarial verification of material findings and passes |
| Permitted verdict | Advisory; never APPROVED unless every approval gate is independently satisfied | Any verdict supported by evidence | Any verdict supported by evidence |

The tier defines minimum depth, not permission to run intrusive tests. Rules of Engagement always control permitted actions.

### 5.3 Audit Time Box and Stop Rules

Record the available audit effort before control selection. A time box changes coverage, not truth standards.

When time expires:

- Stop expanding scope.
- Complete evidence preservation and safety obligations.
- Mark unfinished applicable controls UNVERIFIED.
- Report the resulting coverage honestly.
- Do not compress a Deep audit into superficial checks while retaining the Deep label.

Stop immediately when authorization is exceeded, a test may cause material harm, evidence integrity is compromised, or the audited version cannot be established.

---

## 6. Required Intake

### 6.1 Product Context

- Application name and owner
- Product purpose and primary value proposition
- Target users and user roles
- Critical user journeys
- Business-critical operations
- Intended scale and expected growth
- Availability and recovery expectations
- Revenue, safety, legal, or reputational consequences of failure
- Supported platforms, browsers, devices, and regions
- Accessibility target
- Relevant contractual or customer commitments

### 6.2 Technical Context

- Repository path or URL
- Repository access level
- Exact commit SHA, tag, or source snapshot
- Release/build identifier
- Live and test URLs
- Technology stack and runtime versions
- Architecture and data-flow diagrams
- Authentication and authorization model
- Database and storage systems
- Hosting, DNS, CDN, edge, and infrastructure providers
- CI/CD and release process
- External APIs, webhooks, identity providers, and vendors
- Desktop/mobile packaging and update model where applicable
- Model providers, tools, data sources, and retrieval systems where applicable

### 6.3 Data and Risk Context

- Data inventory and classification
- Personal, financial, health, legal, authentication, or confidential data handled
- Data residency requirements
- Retention and deletion requirements
- Applicable jurisdictions and contractual frameworks
- Threat model or known threat actors
- Known risks, accepted risks, and compensating controls
- Previous audit findings and remediation status
- Recent incidents, outages, or security events

### 6.4 Audit Access and Evidence

- Test accounts for every relevant role
- Approved test data
- Configuration access
- Logs and monitoring access
- Build and deployment records
- Backup and recovery evidence
- Vulnerability and dependency reports
- Test results and coverage reports
- Production-versus-staging differences
- Named contacts for technical, security, privacy, and business questions

Missing inputs must be listed under **Audit Limitations**. They must not be silently assumed.

### 6.5 Threat-Model Fallback

If no current threat model is supplied, construct a lightweight audit threat model before selecting controls. At minimum record:

- Assets requiring protection
- Users, administrators, services, and plausible threat actors
- Entry points and trust boundaries
- Privileged and irreversible actions
- Sensitive data flows and storage locations
- External dependencies
- Five highest-consequence abuse or failure scenarios
- Existing preventive, detective, and recovery controls

Mark stakeholder assumptions as unverified until corroborated. The fallback model supports audit planning; it does not replace formal product threat modeling where risk warrants it.

---

## 7. Rules of Engagement and Safety Gate

No active security, load, resilience, destructive, or production-impacting test may begin until the following are recorded:

- Written authorization and authorizing party
- Approved targets and excluded targets
- Approved environment
- Testing dates and time zone
- Permitted techniques
- Explicitly prohibited techniques
- Rate and concurrency limits
- Approved accounts and privilege levels
- Data-handling restrictions
- Logging and evidence-storage rules
- Emergency stop method and contact
- Incident escalation process
- Whether proof-of-concept exploitation is permitted
- Whether test-created data must be removed

Default to passive, read-only inspection when authorization is incomplete.

Never:

- Perform denial-of-service testing without explicit written authorization.
- Access or alter another real user's data to prove an authorization defect.
- Exfiltrate secrets or personal data into the report.
- Weaken a production security control for testing convenience.
- Install persistent tooling or create hidden access.
- Trigger billing, messaging, deletion, publication, or irreversible external actions without approval.

If a dangerous condition is discovered, stop the relevant test, preserve minimal safe evidence, and follow the escalation process.

---

## 8. Evidence Model

### 8.1 Evidence Classes

- **CODE:** Source code, tests, schemas, migrations, or build definitions
- **CONFIG:** Application, platform, infrastructure, security, or deployment configuration
- **RUNTIME:** Directly observed application behavior
- **NETWORK:** Requests, responses, protocols, headers, or connection behavior
- **DATA:** Schema, sample records, integrity checks, query plans, or lifecycle evidence
- **PIPELINE:** CI/CD runs, checks, artifacts, approvals, or provenance
- **OPERATIONS:** Logs, alerts, dashboards, incidents, runbooks, backups, or recovery exercises
- **DOCUMENT:** Requirements, policies, contracts, diagrams, or procedures
- **TOOL:** Scanner, linter, SAST, DAST, SCA, benchmark, or test-tool output
- **INTERVIEW:** Stakeholder statement not independently verified
- **INFERRED:** Reasoned conclusion supported by indirect evidence

Tool findings must be validated where practical. A scanner label alone does not establish severity or exploitability.

### 8.2 Evidence Record

Every material observation must record:

- Evidence ID
- Evidence class
- Date and time collected
- Auditor or process collecting it
- Product version, commit, build, and environment
- File, line, endpoint, screen, configuration key, log reference, or artifact location
- Collection method or command
- Sanitized excerpt or result
- Integrity reference when warranted, such as a checksum
- Limitations

### 8.3 Repository Access Rule

If repository access is unavailable, any statement that would require source evidence must be marked:

**UNVERIFIED - Runtime inference only**

Do not describe black-box behavior as proof of internal implementation.

### 8.4 Assertion Status

Every assessed control must use exactly one status:

- **PASS:** Affirmatively tested or inspected and acceptable for the declared context.
- **FAIL:** Verified unacceptable condition requiring remediation before the applicable release gate.
- **WARN:** Verified material concern that does not independently trigger FAIL.
- **NOTE:** Verified contextual observation with no present material risk.
- **UNVERIFIED:** Evidence is insufficient to reach a conclusion.
- **NOT APPLICABLE:** The control does not apply; justification is mandatory.

An interview or document claim without corroboration normally remains UNVERIFIED.

---

## 9. Finding Standard

Every finding must include:

1. Finding ID and concise title
2. Affected area and cross-tags
3. Assertion status
4. Severity
5. Likelihood
6. Confidence
7. Evidence IDs and precise location
8. Affected version and environment
9. Preconditions or attack/failure path
10. Observable condition
11. Expected secure or reliable condition
12. Technical risk
13. User and business impact
14. Scope of impact
15. Recommended fix
16. Acceptable alternative or compensating control
17. Estimated remediation effort
18. Suggested owner
19. Verification or regression test
20. Residual risk after remediation

Do not split one root cause into multiple findings merely to increase the finding count. Do not combine unrelated root causes into an unactionable omnibus finding.

---

## 10. Severity, Likelihood, Confidence, and Priority

### 10.1 Severity

- **Critical:** Credible risk of catastrophic compromise, widespread irreversible harm, or immediate inability to operate safely.
- **High:** Serious compromise, material data exposure, major integrity loss, sustained outage, or failure of a critical business workflow.
- **Medium:** Meaningful but bounded harm requiring remediation; exploitation or failure has practical constraints.
- **Low:** Limited impact, strong preconditions, or defense-in-depth weakness.
- **Informational:** No demonstrated present risk; useful context or hardening opportunity.

Severity describes impact, not remediation difficulty.

### 10.2 Likelihood

- **High:** Expected or readily achievable under current conditions.
- **Medium:** Plausible with identifiable conditions or effort.
- **Low:** Unlikely, highly constrained, or dependent on uncommon conditions.
- **Unknown:** Insufficient evidence; do not manufacture a likelihood rating.

### 10.3 Confidence

- **High:** Reproduced or directly supported by strong, corroborated evidence.
- **Medium:** Supported by credible evidence with material limitations.
- **Low:** Plausible but based mainly on incomplete or indirect evidence.

Low-confidence concerns should normally be UNVERIFIED until confirmed.

### 10.4 Remediation Priority

Prioritize using:

1. Safety and active exploitation
2. Severity and credible likelihood
3. Regulatory, contractual, and critical-workflow consequences
4. Blast radius and exposure
5. Availability of compensating controls
6. Fix effort and operational risk
7. Dependency order

Never rank a cosmetic quick win above a release-blocking security or integrity defect merely because it is easier.

---

## 11. Audit Coverage

### 11.1 Product Fitness and Requirements

Assess whether the product solves the stated problem, supports critical workflows, defines success and failure states, handles user mistakes safely, and avoids material gaps between promises and behavior.

Verify requirements traceability where available. Identify ambiguous, conflicting, missing, or untestable requirements that create material risk.

### 11.2 Threat Modeling and Trust Boundaries

Map users, roles, services, devices, networks, data stores, third parties, administrative planes, and trust boundaries.

Review entry points, privileged operations, assets, abuse cases, attacker objectives, misuse by authorized users, tenant isolation, and relevant physical or local-device threats.

### 11.3 Authentication and Identity

Review account creation, login, logout, password storage and reset, MFA, passkeys where used, federation, OAuth/OIDC flows, session creation and invalidation, token lifetime, device/session visibility, recovery, enumeration resistance, brute-force protection, and privileged reauthentication.

### 11.4 Authorization and Isolation

Verify server-side authorization for objects, functions, roles, tenants, administrative actions, exports, files, APIs, and background jobs.

Test horizontal and vertical privilege boundaries using authorized test data. Review default-deny behavior and changes in role or ownership.

### 11.5 Input, Output, and Execution Safety

Review validation, canonicalization, encoding, injection risks, XSS, CSRF, SSRF, path traversal, command execution, unsafe deserialization, template injection, redirects, file parsing, archive extraction, uploads, downloads, content types, and resource exhaustion.

### 11.6 API and Integration Security

Review authentication, authorization, schema validation, versioning, pagination, quotas, replay resistance, idempotency, webhook signatures, secret rotation, error behavior, outbound request controls, third-party failure handling, and deprecation strategy.

### 11.7 Browser and Frontend Security

Review content security policy, transport security, cookie attributes, CORS, frame protection, dependency loading, source maps, sensitive browser storage, DOM injection, service workers, caching of private data, and exposure of privileged logic or secrets.

### 11.8 Secrets and Cryptography

Review secret creation, storage, distribution, access, rotation, revocation, logging, and incident response.

Assess whether established cryptographic libraries and appropriate key management are used. Do not approve custom cryptography without exceptional evidence and specialist review.

### 11.9 Architecture and Boundaries

Assess fitness for purpose, separation of concerns, cohesion, coupling, dependency direction, failure domains, state ownership, tenancy, configuration, feature flags, extensibility, portability requirements, and architectural decision records.

Identify accidental complexity, unnecessary abstraction, circular dependencies, oversized components, hidden coupling, duplicate pathways, and unjustified distributed-system complexity.

### 11.10 Code Quality and Maintainability

Review readability, naming, type safety, error handling, resource cleanup, concurrency, time and locale handling, boundary validation, duplication, dead code, complexity, testability, documentation, and consistency.

Differentiate defects from stylistic preferences. A style preference is not a risk finding unless it creates a demonstrated maintenance, correctness, or security consequence.

### 11.11 Generated-Code Risks

Review for fabricated APIs, nonexistent guarantees, placeholder behavior, copy-pasted vulnerabilities, needless wrappers, excessive configuration, duplicate helpers, misleading comments, magic constants, unused code, prompt duplication, cargo-cult security, weak failure handling, and tests that only restate implementation.

Do not label code as machine-generated without reliable provenance. Report the observable engineering defect, not a guess about authorship.

### 11.12 Dependencies and Software Supply Chain

Review direct and transitive dependencies, lockfiles, provenance, integrity controls, vulnerability exposure, reachability, maintenance health, licenses, typosquatting risk, registries, install scripts, build plugins, artifact signing, SBOM availability, update policy, and dependency-removal opportunities.

An outdated version is not automatically a vulnerability. Establish relevance, exposure, compatibility, and remediation risk.

### 11.13 Data Architecture and Database

Review schema design, constraints, referential integrity, normalization choices, indexes, query plans, transactions, isolation, locking, concurrency, migrations, rollback, pooling, N+1 access, retention, archival, deletion, auditability, tenancy, encryption, backups, restoration, and reconciliation.

Verify that critical invariants are enforced at appropriate boundaries and are not dependent solely on frontend behavior.

### 11.14 Privacy and Data Governance

Review data minimization, purpose limitation, notice and consent, lawful or contractual basis where applicable, retention, access, correction, export, deletion, subprocessors, cross-border handling, telemetry, cookies, sensitive-data protection, breach response, and alignment between published statements and actual behavior.

Do not declare legal compliance solely from a technical audit. Identify the applicable jurisdiction and require qualified legal review for legal conclusions.

### 11.15 Infrastructure and Cloud Security

Review account structure, identity and access management, least privilege, network exposure, segmentation, firewalls/WAF, DNS, TLS, storage access, metadata services, administrative paths, infrastructure as code, drift, patching, hardening, logging, environment isolation, quotas, and cost-abuse controls.

### 11.16 Build, CI/CD, and Release Engineering

Review reproducible builds, protected branches, required checks, review controls, test gates, secret handling, runner isolation, artifact provenance, environment promotion, approvals, migration ordering, deployment health checks, rollback, feature flags, release notes, and emergency release procedures.

Confirm that the audited source corresponds to the deployed artifact where the assurance objective requires it.

### 11.17 Reliability and Resilience

Review timeouts, retries, backoff, idempotency, circuit breaking, queues, partial failure, degraded modes, dependency outages, startup and shutdown, resource exhaustion, consistency, clock assumptions, duplicate delivery, data reconciliation, and safe recovery.

Assess single points of failure and whether failure is contained, visible, and recoverable.

### 11.18 Observability and Operations

Review structured logs, metrics, traces, correlation identifiers, health signals, dashboards, alert quality, ownership, on-call readiness, runbooks, escalation, audit logs, tamper resistance, sensitive-data redaction, retention, and operational access.

Verify that critical failures can be detected and diagnosed without exposing confidential information.

### 11.19 Backup, Disaster Recovery, and Business Continuity

Review backup scope, frequency, encryption, isolation, immutability where warranted, retention, monitoring, restoration testing, recovery dependencies, RPO, RTO, regional/provider failure, key recovery, and continuity procedures.

A configured backup is not a verified recovery capability. Require restoration evidence.

### 11.20 Performance, Capacity, and Cost

Review startup, latency, throughput, rendering, bundle size, memory, CPU, storage, database behavior, caching, compression, CDN use, concurrency, queue depth, quotas, scaling behavior, and cost under expected and peak usage.

Model 10× expected load when useful, but mark the conclusion UNVERIFIED unless supported by an authorized representative test or credible production evidence. Do not run production load tests without explicit authorization.

### 11.21 Quality Engineering

Assess test strategy, risk coverage, unit/integration/contract/end-to-end balance, fixture quality, isolation, determinism, negative tests, boundary tests, mutation or fault testing where justified, regression protection, flaky tests, test data, and release acceptance.

Exercise applicable user flows across:

- Success, empty, loading, and error states
- Invalid and adversarial input
- Refresh, navigation, and interrupted operations
- Expired or revoked sessions
- Duplicate submissions and retries
- Race conditions and concurrent work
- Partial dependency failure
- Offline or reconnect behavior where applicable
- Supported desktop, tablet, mobile, browser, and device environments
- Slow network and constrained hardware where relevant

### 11.22 Accessibility

Audit against the declared accessibility target, normally WCAG 2.2 AA for applicable web interfaces.

Review semantics, names and labels, keyboard access, focus visibility and order, contrast, reflow, zoom, target size, motion, timing, errors, status announcements, screen-reader behavior, media alternatives, drag interactions, authentication barriers, and assistive-technology compatibility.

Automated scans are supporting evidence only and cannot establish full accessibility conformance.

### 11.23 User Experience and Content

Review information architecture, navigation, hierarchy, terminology, onboarding, discoverability, feedback, error prevention, recovery, confirmation, progressive disclosure, cognitive load, consistency, trust signals, help, and completion efficiency.

Distinguish personal taste from demonstrated usability risk.

### 11.24 Design Distinctiveness and Brand Trust

For customer-facing products, assess whether typography, color, imagery, spatial structure, components, and interaction patterns express an intentional product identity rather than unmodified framework defaults.

Record:

- Declared aesthetic direction
- Typography logic
- Color and contrast logic
- Spatial/layout strategy
- Image and icon treatment
- Component customization
- Consistency with brand and audience

Default generic presentation is normally a NOTE or product opportunity. Raise it to WARN only when it credibly weakens user trust, differentiation, comprehension, conversion, or brand commitments. It must not independently block an internal utility from release without demonstrated harm.

### 11.25 Desktop Applications

When applicable, review installer and uninstaller behavior, signing, reputation, update integrity, downgrade protection, permissions, filesystem safety, local secrets and encryption, IPC, deep links, protocol handlers, webview/Electron boundaries, native modules, crash recovery, single-instance behavior, path handling, metadata, offline operation, and endpoint-security compatibility.

### 11.26 Mobile Applications

When applicable, review platform permissions, secure storage, transport, deep links, intents, background work, screenshots, backups, rooted/jailbroken device assumptions, app signing, store release, updates, privacy declarations, battery/network use, and lifecycle interruption.

### 11.27 Model and Automated Decision Systems

When applicable, review model and provider inventory, prompt and tool boundaries, untrusted-content handling, prompt injection, data leakage, tenant isolation, retrieval permissions, output validation, human review, hallucination consequences, evaluation coverage, model/version drift, fallback behavior, cost controls, abuse controls, auditability, retention, intellectual-property risks, and provider outages.

Treat model output as untrusted input at consequential boundaries. Do not claim deterministic correctness from nondeterministic systems without evidence.

### 11.28 Documentation and Supportability

Review setup, configuration, architecture, API, deployment, rollback, operations, troubleshooting, security, privacy, backup, recovery, support, and user documentation.

Verify that documentation matches the audited version and does not promise unsupported behavior.

### 11.29 Decommissioning and Data Exit

Review account closure, data export, deletion, key revocation, DNS and certificate retirement, vendor termination, backups, legal holds, artifact retention, user communication, and proof that retired services no longer expose data or privileged access.

---

## 12. Verification Workflow

Perform the audit in this order:

1. Confirm authorization, scope, version, and environment.
2. Record missing inputs and limitations.
3. Map product purpose, critical journeys, assets, roles, and trust boundaries.
4. Inventory architecture, services, data stores, dependencies, integrations, and deployment path.
5. Establish the evidence ledger.
6. Review documentation and configuration.
7. Inspect source, tests, schemas, migrations, and pipelines where authorized.
8. Perform safe runtime and network verification.
9. Perform authorized specialized testing.
10. Correlate source, runtime, configuration, operational, and documentary evidence.
11. Deduplicate findings and identify root causes.
12. Assign status, severity, likelihood, confidence, priority, and owner.
13. Calculate scores and evidence coverage.
14. Apply release gates and determine the verdict.
15. Conduct a contradiction and unsupported-claim review.
16. Sanitize the report and preserve evidence according to the engagement rules.

If a command or test fails, diagnose the failure before relying on its output. Never report a failed or incomplete test as a completed verification.

---

## 13. Scoring Model

### 13.0 Product Risk Profile

Select one primary profile and any applicable modifiers before scoring.

| Profile | Examples | Critical categories |
|---|---|---|
| P1 Public Consumer | Public websites, consumer SaaS, mobile applications | Security/privacy, reliability/operations, UX/product fitness, accessibility |
| P2 Internal Business | Internal portals, line-of-business tools, controlled-user applications | Security/privacy, architecture/data integrity, quality/correctness, reliability/operations |
| P3 Data-Sensitive | Health, finance, legal, identity, regulated or highly confidential systems | Security/privacy, architecture/data integrity, reliability/recovery, deployment/supply chain |
| P4 Desktop/Local Utility | Local-first desktop tools and offline utilities | Quality/correctness, architecture/data integrity, deployment/supply chain, reliability/recovery |
| P5 Platform/API | APIs, developer platforms, infrastructure services | Security/privacy, reliability/operations, architecture/data integrity, performance/capacity |
| P6 Model-Assisted | Products with generative models, agents, retrieval, or automated decisions | Security/privacy, quality/correctness, architecture/data integrity, reliability/operations |

Modifiers include public administration, children or vulnerable users, safety impact, high transaction value, multi-tenancy, administrator concentration, irreversible operations, internationalization, and contractual accessibility obligations.

Base weights remain the comparison baseline. A profile may adjust any category by no more than five percentage points, total weights must remain 100%, and every adjustment must be disclosed with its risk rationale. Profiles determine critical categories and mandatory controls even when weights are unchanged.

### 13.1 Category Weights

| Category | Weight |
|---|---:|
| Security and privacy | 20% |
| Reliability, recovery, and operations | 18% |
| Architecture and data integrity | 14% |
| Quality engineering and correctness | 12% |
| Deployment and supply chain | 10% |
| Maintainability and documentation | 8% |
| Performance, capacity, and cost | 7% |
| UX and product fitness | 6% |
| Accessibility | 5% |

If a category is genuinely NOT APPLICABLE, redistribute its weight proportionally and disclose the change. Do not remove a category merely because it was not assessed.

### 13.2 Category Score Bands

- **9.0–10.0:** Strong controls, extensively verified, no material unresolved weakness
- **7.0–8.9:** Production-capable with bounded and manageable deficiencies
- **5.0–6.9:** Material remediation required; assurance is incomplete or inconsistent
- **3.0–4.9:** Major deficiencies affecting production confidence
- **0.0–2.9:** Unacceptable control failure or pervasive critical risk

### 13.3 Evidence Coverage

Report evidence coverage separately from quality:

**Coverage = controls with PASS, FAIL, WARN, or NOTE status / all applicable selected controls**

The denominator is established from the versioned Control Catalog in Appendix A after applicability and depth selection. UNVERIFIED controls remain in the denominator. NOT APPLICABLE controls are excluded only when justification is recorded.

Coverage is tier-relative and must be labeled with its tier. Every Rapid audit must additionally report coverage against the Standard-tier denominator for the same applicability decisions, so a high Rapid coverage figure cannot be mistaken for Standard-tier assurance. Example: `Coverage: 92% (Rapid denominator), 41% (Standard denominator)`.

Report for each category:

- Quality score out of 10
- Evidence coverage percentage
- Confidence
- Number of PASS, FAIL, WARN, and UNVERIFIED controls

Do not lower a quality score merely to disguise missing evidence. Instead, report the uncertainty openly. A high score with low coverage cannot support an APPROVED verdict.

### 13.4 Deterministic Category Scoring

Begin with a provisional score derived from applicable control results:

| Control result | Points |
|---|---:|
| PASS | 10 |
| NOTE | 9 |
| WARN - Low | 8 |
| WARN - Medium | 6 |
| WARN - High | 4 |
| FAIL - Low | 5 |
| FAIL - Medium | 3 |
| FAIL - High | 1 |
| FAIL - Critical | 0 |

A WARN may not carry Critical severity. A verified condition with credible Critical impact is a FAIL by definition. A WARN - High on a C3 control must be independently challenged before report release; if the challenge confirms a credible path to High impact under current conditions, reclassify it as FAIL - High.

Calculate the weighted mean using control criticality:

- C1 Supporting control: weight 1
- C2 Important control: weight 2
- C3 Release-critical control: weight 3

UNVERIFIED controls do not receive points and do not enter the quality mean; they reduce evidence coverage. A category with less than 50% coverage must display a provisional score followed by **INSUFFICIENT EVIDENCE** and cannot support an approval gate.

Apply these mandatory caps after calculating the mean:

- Any unresolved Critical FAIL caps the category at 2.9.
- Any unresolved High FAIL caps the category at 4.9.
- A verified systemic failure involving three or more related Medium findings across at least two trust boundaries caps the category at 6.9.
- Failure of a C3 control caps the category at 6.9 unless a stricter cap above applies.
- A category below 70% coverage cannot score above 7.9 for release-decision purposes.

Round category scores to one decimal place after caps. Do not create multiple findings or controls from one condition to manipulate the result.

### 13.5 Systemic-Risk Rule

Multiple Medium findings constitute systemic risk only when all are true:

1. At least three verified Medium findings share a root cause or failed control objective.
2. At least two services, trust boundaries, user roles, or critical workflows are affected.
3. The combined condition creates High-equivalent impact or defeats a defense-in-depth layer.
4. The relationship is documented in one systemic-risk record and independently challenged.

Otherwise, assess the findings individually.

When likelihood is Unknown, prioritize provisionally using severity, exposure, and control criticality. Unknown likelihood must not be silently converted to Low. A Critical or High finding with Unknown likelihood requires targeted verification before a favorable verdict unless a verified compensating control bounds the risk.

### 13.6 Overall Score

Calculate the weighted score from category scores. Round only the final result to one decimal place.

The numerical score does not override release gates. A product with an unresolved Critical finding cannot achieve a favorable verdict through high scores elsewhere.

---

## 14. Release Gates and Verdicts

Select exactly one verdict:

### APPROVED

Use only when:

- No unresolved Critical or High release-blocking findings exist.
- Critical workflows have been affirmatively verified.
- Security, data integrity, deployment, rollback, backup/recovery, and operational readiness have sufficient evidence for the declared context.
- Overall evidence coverage is at least 85%, with no critical category below 80% coverage.
- Remaining risks are Low or accepted Medium risks with documented ownership.

### APPROVED WITH CONDITIONS

Use when:

- No unresolved Critical finding exists.
- No High finding presents an immediate credible path to severe harm.
- Remaining material work has an owner, deadline, interim control, and verification plan.
- Critical workflows and release safety have sufficient evidence.

### REQUIRES REWORK

Use when any of the following applies:

- An unresolved High finding blocks safe production use.
- A critical workflow fails.
- Data integrity, authorization, recovery, or deployment safety is materially deficient.
- Evidence is too incomplete to support release confidence for a high-risk product.
- Multiple Medium findings combine into material systemic risk.

### DO NOT SHIP

Use when any of the following applies:

- An unresolved Critical finding exists.
- There is a credible immediate path to catastrophic compromise or harm.
- The product can cause widespread irreversible data loss or unauthorized exposure.
- Essential security boundaries are absent or demonstrably ineffective.
- The release artifact cannot be trusted or safely rolled back in a high-consequence environment.

Unknowns do not automatically prove failure, but material unknowns can prevent approval.

---

## 15. Recommendation Standard

Include only recommendations supported by evidence and material value.

Every recommendation must state:

- Problem or opportunity
- Supporting evidence
- Why it matters now
- User value
- Business or operational value
- Security, reliability, accessibility, or maintenance value where applicable
- Estimated effort: Small, Medium, Large, or Requires discovery
- Expected risk of implementation
- Dependencies
- Measurable success criterion
- Whether it is required, conditional, or optional

Do not require a minimum number of recommendations.

Reject or omit recommendations that are primarily:

- Fashion-driven
- Unsupported rewrites
- Tool replacement without demonstrated need
- New paid services without a justified return
- Premature scaling
- Cosmetic preference presented as engineering risk
- Dependency additions for trivial functionality
- Generic “best practice” without contextual benefit

---

## 16. Re-Audit and Delta Mode

Use Re-Audit mode when verifying remediation, reviewing a new release against a prior audit, or tracking risk over time.

### 16.1 Required Inputs

- Previous audit ID, specification version, catalog version, report, and machine-readable artifacts
- Previous audited commit/build and current commit/build
- Claimed remediation and linked change evidence
- Changed architecture, dependencies, configuration, infrastructure, data model, user journeys, and risk profile
- New incidents, accepted risks, exceptions, and known regressions

### 16.2 Procedure

1. Verify each prior FAIL and WARN against its original reproduction and acceptance criteria.
2. Classify it as OPEN, PARTIALLY REMEDIATED, REMEDIATED, ACCEPTED, REGRESSED, or NOT REPRODUCIBLE.
3. Confirm the fix in the current build; code change alone is not closure.
4. Run the specified regression test and inspect adjacent controls affected by the change.
5. Perform change-impact analysis and select additional controls for new or modified surfaces.
6. Re-run all C3 controls and release gates applicable to the current profile.
7. Recalculate scores and coverage from current evidence; never carry forward a PASS without confirming that its evidence remains valid.
8. Report new, closed, reopened, and unchanged risks separately.

### 16.3 Delta Report

| Metric | Previous | Current | Delta |
|---|---:|---:|---:|
| Overall score |  |  |  |
| Evidence coverage |  |  |  |
| Critical/High open |  |  |  |
| Medium open |  |  |  |
| C3 controls passed |  |  |  |
| Accepted residual risks |  |  |  |

State whether apparent improvement comes from actual remediation, changed scope, changed applicability, changed scoring/catalog rules, or increased evidence.

---

## 17. Machine-Readable Audit Artifacts

Every Standard or Deep audit must produce UTF-8 JSON artifacts in addition to the human report:

```text
audits/<audit-id>/
  audit-manifest.json
  selected-controls.json
  evidence-ledger.json
  findings.json
  score-sheet.json
  risk-register.json
  verification-log.json
  report.md
```

Rapid audits should use the same structure when tooling permits.

### 17.1 Common Requirements

- Schema version and specification version
- Audit ID and product identifier
- Stable record IDs
- ISO 8601 timestamps with time zone
- Exact commit/build/environment
- Explicit null values rather than invented data
- Enumerated statuses matching this specification
- Relative references between controls, evidence, findings, and risks
- No secrets, tokens, personal data, or unsafe exploit material
- Deterministic ordering by stable ID for reliable diffs

### 17.2 Minimum Finding Object

```json
{
  "schema_version": "1.0",
  "audit_id": "AUD-PRODUCT-20260710-001",
  "finding_id": "AUD-PRODUCT-20260710-001-F001",
  "control_ids": ["SEC-AUTHZ-001"],
  "title": "Server does not enforce object ownership",
  "status": "FAIL",
  "severity": "High",
  "likelihood": "Medium",
  "confidence": "High",
  "evidence_ids": ["AUD-PRODUCT-20260710-001-E004"],
  "affected_version": "commit-or-build-id",
  "environment": "staging",
  "technical_risk": "Unauthorized cross-account object access",
  "business_impact": "Confidential customer data may be disclosed",
  "recommended_fix": "Enforce ownership or tenant scope server-side for every object operation",
  "verification": "Repeat the cross-account request and require a non-disclosing denial",
  "owner": "Application engineering",
  "residual_risk": null
}
```

### 17.3 Schema Validation

Artifacts must be validated against the schema version used by the audit before report release. Schema validation proves structural correctness only; it does not prove the audit conclusions.

---

## 18. Required Deliverables

### 18.1 Audit Identity

- Application and owner
- Audit type and objective
- Auditor identity
- Audit dates
- Version, commit, build, and environment
- Authorization reference
- Scope and exclusions

### 18.2 Executive Summary

Maximum seven sentences covering product readiness, highest material risks, evidence strength, major limitations, and verdict.

### 18.3 System Context

Summarize product purpose, critical users, critical journeys, architecture, data sensitivity, deployment model, and trust boundaries.

### 18.4 Audit Limitations

List unavailable access, missing evidence, excluded systems, unperformed tests, environment differences, and resulting assurance limits.

### 18.5 Scores and Coverage

| Category | Weight | Score /10 | Coverage | Confidence | PASS | FAIL | WARN | UNVERIFIED |
|---|---:|---:|---:|---|---:|---:|---:|---:|

Include weighted overall score and overall evidence coverage.

### 18.6 Findings Summary

| ID | Area | Finding | Status | Severity | Likelihood | Confidence | Evidence | Owner | Priority |
|---|---|---|---|---|---|---|---|---|---|

### 18.7 Detailed Findings

Use the complete twenty-field Finding Standard for every FAIL and WARN. Include NOTE and UNVERIFIED entries when they materially affect interpretation or release confidence.

### 18.8 Verified Strengths

Record important controls that were affirmatively verified. Do not provide generic praise.

### 18.9 Priority Action Plan

| Order | Action | Finding IDs | Owner | Effort | Dependency | Interim Control | Verification | Target |
|---:|---|---|---|---|---|---|---|---|

Order by risk and dependency, then by effort.

### 18.10 Risk Register

| Risk | Evidence | Likelihood | Impact | Existing Control | Treatment | Owner | Residual Risk |
|---|---|---|---|---|---|---|---|

### 18.11 Technical Debt Register

| Debt | Evidence | Consequence if Deferred | Fix Effort | Priority | Owner | Trigger Date/Event |
|---|---|---|---|---|---|---|

### 18.12 Product Improvement Opportunities

Include only material, evidence-supported opportunities using the Recommendation Standard.

### 18.13 Final Verdict

State exactly one approved verdict and map the justification directly to the release gates.

### 18.14 Evidence Appendix

Provide sanitized evidence references, commands, tools and versions, test accounts/roles used, timestamps, artifacts, and reproduction notes. Do not include secrets, exploit payloads that create unnecessary risk, or personal information.

---

## 19. Independent Verification and Report Quality Gate

### 19.1 Challenge Requirement

For Standard audits, perform a separate contradiction pass after drafting findings. For Deep audits and high-consequence release decisions, use an independent qualified human, agent, or isolated review process that did not author the challenged conclusion.

The challenger must attempt to:

- Refute every Critical and High finding.
- Refute every release-significant Medium finding and WARN.
- Identify missing evidence and alternative explanations.
- Detect duplicated root causes or inflated severity.
- Challenge C3 PASS results supporting approval.
- Recalculate category scores, caps, coverage, and verdict gates.
- Confirm that sensitive information has been removed.

Record each challenge as UPHELD, MODIFIED, REJECTED, or NEEDS MORE EVIDENCE with rationale. The original auditor resolves differences transparently; the challenger does not silently overwrite evidence.

### 19.2 Twelve-Point Quality Gate

Before issuing the report, confirm all twelve conditions:

1. Scope, authorization, version, build, and environment are explicit.
2. Every material claim is supported by evidence or marked UNVERIFIED.
3. PASS results contain affirmative verification evidence.
4. Severity reflects credible impact; likelihood is assessed separately.
5. Duplicate findings are consolidated around root causes.
6. Tool output has been interpreted and false positives considered.
7. Scores follow the rubric and disclose evidence coverage.
8. Verdict follows release gates and is not overridden by the overall score.
9. Recommendations are proportional, actionable, and non-frivolous.
10. Audit limitations and NOT APPLICABLE decisions are justified.
11. The report contains no secrets, unnecessary exploit detail, or personal data.
12. A qualified reviewer could reproduce the material conclusions.

If any condition fails, the report is not ready for release.

---

## 20. Auditor Conduct Rules

- Remain independent, direct, and respectful.
- State facts plainly without alarmism.
- Challenge both optimistic and pessimistic assumptions.
- Preserve original evidence and distinguish it from interpretation.
- Disclose conflicts of interest and material limitations.
- Do not claim legal certification, regulatory approval, accessibility conformance, or penetration-test completeness beyond the evidence and engagement scope.
- Do not expose sensitive implementation details to audiences that do not need them.
- Prefer corrections that reduce complexity and operational risk.
- Identify when accepting a risk is more rational than implementing a costly control.
- Reassess severity when compensating controls are verified.
- Record accepted risks with owner, rationale, expiry or review date, and residual risk.
- Never turn uncertainty into confident prose.

---

## 21. Closing Standard

A trustworthy audit is not the longest report or the report with the most findings.

It is the report that most accurately explains:

- What was examined
- What was proven
- What remains unknown
- What can credibly go wrong
- What already works well
- What must change before release
- What improvements are worth their cost
- Who owns the remaining risk

The final judgment must be firm enough to guide a release decision and honest enough to withstand independent review.

---

## Appendix A. Versioned Control Catalog

**Catalog Version:** 1.0
**Status:** Normative minimum catalog
**Tier notation:** R = Rapid, S = Standard, D = Deep
**Criticality:** C1 = Supporting, C2 = Important, C3 = Release-critical

Select every applicable control at or below the declared depth. A Standard audit includes R and S controls. A Deep audit includes R, S, and D controls. Profile-critical controls are mandatory regardless of tier. Controls may be added for product-specific risk, but additions require stable local IDs and cannot remove catalog controls from the coverage denominator.

PASS requires the stated objective to be supported by the listed minimum evidence or stronger equivalent evidence. FAIL requires a verified material deviation. Insufficient evidence is UNVERIFIED. NOT APPLICABLE requires a recorded product-context justification.

### A.0 Control-to-Category Mapping (Normative)

Every control scores in exactly one of the nine categories in Section 13.1. Mapping is by control-family prefix, with the named exceptions below. Locally added controls must declare their category at creation.

| Control family | Scoring category |
|---|---|
| SEC-*, PRIV-*, ADM-*, RET-* | Security and privacy |
| GOV-THREAT-001 | Security and privacy |
| INF-IAM, INF-NET, INF-TLS, INF-ENV | Security and privacy |
| DESK-LOCAL-001, MOB-PERM-001 | Security and privacy |
| MOD-BOUND-001, MOD-INJECT-001, MOD-DATA-001 | Security and privacy |
| REL-*, OPS-*, BAK-*, DR-* | Reliability, recovery, and operations |
| MOD-FAIL-001 | Reliability, recovery, and operations |
| GOV-RISK-001 | Reliability, recovery, and operations |
| ARC-*, DATA-* | Architecture and data integrity |
| CODE-*, QA-* | Quality engineering and correctness |
| MOD-EVAL-001, MOB-LIFE-001 | Quality engineering and correctness |
| SUP-*, CICD-* | Deployment and supply chain |
| INF-IAC-001, INF-PATCH-001 | Deployment and supply chain |
| DESK-INSTALL-001, DESK-UPDATE-001 | Deployment and supply chain |
| DOC-* | Maintainability and documentation |
| ARC-CPLX-001 *(exception to ARC-\*)* | Maintainability and documentation |
| PERF-*, COST-* | Performance, capacity, and cost |
| UX-*, I18N-* | UX and product fitness |
| GOV-REQ-001, GOV-TRACE-001 | UX and product fitness |
| A11Y-* | Accessibility |

**Gate controls:** `GOV-SCOPE-001` and `GOV-ROE-001` do not score in any category. They are engagement gates: if either cannot PASS, the audit result is limited to advisory status and no approval verdict may be issued. Record them in the manifest and verification log, not the score sheet.

Where a named exception conflicts with a prefix rule, the exception controls. The skill or tooling implementing this specification must fail validation if any selected control lacks a category assignment.

### A.1 Product, Scope, and Threat Model

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| GOV-SCOPE-001 | Audited product, version, build, environment, scope, and exclusions are exact | R | C3 | Manifest and artifact/source identity agree |
| GOV-ROE-001 | Testing is authorized and bounded | R | C3 | Written RoE covers targets, methods, limits, contacts, and data handling |
| GOV-REQ-001 | Critical users, journeys, and failure consequences are identified | R | C2 | Approved product context maps critical workflows |
| GOV-THREAT-001 | Assets, actors, entry points, and trust boundaries are mapped | R | C3 | Current threat model or completed fallback model |
| GOV-RISK-001 | Known and accepted risks have accountable owners and review dates | S | C2 | Risk register includes rationale, residual risk, owner, and expiry |
| GOV-TRACE-001 | Material requirements trace to implementation and verification | D | C2 | Sampled requirements map to code/config and tests |

### A.2 Authentication, Authorization, and Sessions

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| SEC-AUTHN-001 | Authentication is enforced server-side for protected operations | R | C3 | Code/config plus authorized positive and negative runtime tests |
| SEC-AUTHN-002 | Credentials and password resets are securely handled | S | C3 | Storage/config review and reset-flow tests show bounded, expiring recovery |
| SEC-AUTHN-003 | Brute force and account enumeration are materially constrained | S | C2 | Rate/abuse controls and non-disclosing runtime behavior verified |
| SEC-MFA-001 | MFA or equivalent protection covers high-risk access where required | S | C2 | Policy/config and enrollment, recovery, and bypass-path tests |
| SEC-AUTHZ-001 | Object-level authorization prevents cross-user and cross-tenant access | R | C3 | Server checks plus authorized boundary tests across representative objects |
| SEC-AUTHZ-002 | Function and role authorization enforce least privilege | R | C3 | Role matrix correlates with server checks and negative tests |
| SEC-AUTHZ-003 | Administrative and irreversible actions require appropriate assurance | S | C3 | Privilege, reauthentication, logging, and confirmation controls verified |
| SEC-SESS-001 | Sessions and tokens use secure creation, storage, expiry, and transport | R | C3 | Code/config, cookie/token inspection, and expiry tests |
| SEC-SESS-002 | Logout, revocation, password change, and role change invalidate access | S | C2 | Runtime tests show invalidation within documented bounds |
| SEC-TENANT-001 | Tenant context cannot be selected or overridden by untrusted input | D | C3 | Data/query paths and adversarial tenant-boundary tests |

### A.3 Input, Browser, API, Secrets, and Cryptography

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| SEC-INPUT-001 | Inputs are validated and canonicalized at trusted boundaries | R | C3 | Boundary code and representative invalid/adversarial tests |
| SEC-INJECT-001 | Data cannot become unintended queries, commands, paths, or templates | R | C3 | Parameterization/safe APIs plus targeted negative tests |
| SEC-XSS-001 | Rendered untrusted content is contextually encoded or sanitized | R | C3 | Render paths and authorized payload tests |
| SEC-CSRF-001 | State-changing browser requests resist cross-site action | S | C2 | Same-site/token/origin design and negative runtime test |
| SEC-SSRF-001 | Outbound requests restrict attacker-controlled destinations | S | C3 | Allowlist/resolution controls and safe blocked-destination tests |
| SEC-FILE-001 | File handling constrains type, size, name, path, parsing, and access | S | C3 | Upload/download code plus boundary and access tests |
| SEC-WEB-001 | Browser security headers and private caching are contextually safe | R | C2 | Runtime header/caching evidence across representative routes |
| SEC-CORS-001 | Cross-origin access is least privilege and credential-safe | R | C2 | Config and preflight/credential tests |
| SEC-API-001 | APIs enforce authentication, authorization, validation, and bounded errors | R | C3 | Route/middleware correlation and positive/negative API tests |
| SEC-API-002 | Replay, duplication, pagination, and resource abuse are controlled | S | C2 | Idempotency/quota design and representative runtime tests |
| SEC-HOOK-001 | Webhooks authenticate origin and resist replay | S | C2 | Signature, timestamp/nonce, rotation, and negative tests |
| SEC-SECRET-001 | Secrets are not committed, exposed client-side, or emitted to logs | R | C3 | Repository/config/build/log inspection with validated secret scan |
| SEC-SECRET-002 | Secrets support least-privilege access, rotation, and revocation | S | C2 | Platform policy and tested operational procedure |
| SEC-CRYPTO-001 | Established cryptography and appropriate key management protect sensitive data | S | C3 | Library/config/key lifecycle evidence and applicable runtime verification |

### A.4 Architecture, Code, and Supply Chain

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| ARC-BOUND-001 | Trust, state, and responsibility boundaries are explicit and enforced | R | C3 | Architecture/data-flow evidence correlates with implementation |
| ARC-FAIL-001 | Critical dependencies have bounded failure behavior | S | C2 | Timeouts/fallback/degraded-mode implementation and failure tests |
| ARC-CPLX-001 | Complexity and abstraction are justified by current requirements | S | C1 | Sampled dependency/component analysis finds no material accidental complexity |
| ARC-STATE-001 | Ownership and consistency rules for critical state are unambiguous | S | C3 | Architecture, transaction, and reconciliation evidence agree |
| CODE-CORR-001 | Critical calculations and business rules have explicit invariants | R | C3 | Code and tests cover accepted, rejected, and boundary states |
| CODE-ERR-001 | Errors are handled safely without silent corruption or sensitive leakage | R | C2 | Code paths and induced safe failures verified |
| CODE-TIME-001 | Time, locale, encoding, and identifier assumptions are controlled | S | C2 | Boundary tests cover applicable zones, locales, and encodings |
| CODE-CONC-001 | Concurrency and duplicate execution preserve critical invariants | S | C3 | Atomic/idempotent design and representative concurrency tests |
| CODE-MOD-001 | Generated or assisted code contains no material placeholder or fabricated behavior | S | C2 | Targeted inspection plus build/test/runtime correlation |
| SUP-DEP-001 | Production dependencies are locked, inventoried, and vulnerability-assessed | R | C3 | Lockfile/SBOM and validated SCA results tied to release artifact |
| SUP-DEP-002 | Material dependency findings are assessed for reachability and exposure | S | C2 | Manual triage links vulnerable paths to actual use or non-use |
| SUP-LIC-001 | Dependency licenses are compatible with intended distribution | S | C2 | Current inventory and reviewed license obligations |
| SUP-BUILD-001 | Build inputs, registries, plugins, and install scripts are trusted and bounded | D | C3 | Provenance/config review and controlled build evidence |

### A.5 Data, Privacy, and Governance

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| DATA-SCHEMA-001 | Schema constraints enforce critical integrity rules | R | C3 | Schema/migrations and invalid-state tests |
| DATA-TXN-001 | Transactions and isolation protect multi-step critical operations | S | C3 | Transaction paths plus rollback/concurrency tests |
| DATA-MIG-001 | Migrations are ordered, tested, observable, and safely recoverable | S | C3 | Representative upgrade and rollback/forward-recovery evidence |
| DATA-TENANT-001 | Stored data is isolated by tenant or ownership boundary | R | C3 | Schema/query/access-policy review and authorized boundary tests |
| DATA-QUERY-001 | Critical queries are indexed and bounded at expected scale | S | C2 | Query plans and representative data-volume evidence |
| DATA-RECON-001 | Partial failures and asynchronous processing can be reconciled | D | C2 | Reconciliation controls and induced failure/recovery test |
| PRIV-INV-001 | Collected data is inventoried, classified, and tied to purpose | R | C3 | Data map correlates with code, storage, telemetry, and vendors |
| PRIV-MIN-001 | Collection, exposure, and retention are limited to demonstrated need | S | C2 | Field-level review and enforced retention/deletion behavior |
| PRIV-RIGHTS-001 | Applicable access, correction, export, and deletion workflows function | S | C2 | End-to-end authorized tests and downstream propagation evidence |
| PRIV-NOTICE-001 | Published privacy statements align with actual product behavior | S | C2 | Notice/consent comparison against observed flows |
| PRIV-VENDOR-001 | Subprocessors and cross-border flows are known and governed | D | C2 | Vendor/data-flow inventory and applicable agreements/policies |

### A.6 Infrastructure, Build, and Release

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| INF-IAM-001 | Infrastructure and cloud access enforce least privilege | R | C3 | Role/policy evidence and sampled effective permissions |
| INF-NET-001 | Network and administrative exposure is intentionally restricted | R | C3 | Config and external/internal exposure verification |
| INF-TLS-001 | Sensitive traffic uses correctly configured transport protection | R | C3 | Endpoint/protocol/certificate evidence |
| INF-ENV-001 | Production is isolated from development and test risk | S | C3 | Accounts, credentials, data, network, and pipeline separation evidence |
| INF-IAC-001 | Material infrastructure is reproducible or controlled against drift | S | C2 | IaC/config inventory and drift/change records |
| INF-PATCH-001 | Operating systems, runtimes, and managed components receive risk-based updates | S | C2 | Inventory, support status, patch policy, and sampled evidence |
| CICD-BRANCH-001 | Production changes require appropriate review and checks | R | C2 | Protected branch/review/check configuration |
| CICD-SECRET-001 | Pipelines protect secrets and isolate untrusted execution | R | C3 | Workflow/runner/permission inspection and log sampling |
| CICD-ART-001 | Release artifacts are traceable to reviewed source and build | S | C3 | Source, pipeline, checksum/signature, and deployed artifact correlation |
| CICD-DEPLOY-001 | Deployment verifies health and prevents unsafe partial release | S | C3 | Deployment procedure plus representative success/failure evidence |
| CICD-ROLL-001 | Application and data changes have a tested safe recovery strategy | R | C3 | Rollback or forward-recovery exercise tied to current release model |

### A.7 Reliability, Operations, Recovery, Performance, and Cost

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| REL-TIME-001 | External operations use bounded timeouts and cancellation | R | C2 | Code/config and induced delay test |
| REL-RETRY-001 | Retries use bounded backoff and preserve idempotency | S | C3 | Retry design plus duplicate/failure tests |
| REL-QUEUE-001 | Queues handle poison messages, duplication, backpressure, and replay | S | C2 | Config/code and representative failure tests |
| REL-START-001 | Startup, shutdown, and restart preserve service and data safety | S | C2 | Lifecycle tests and operational evidence |
| OPS-LOG-001 | Critical activity and failures are diagnosable without sensitive leakage | R | C3 | Log sampling across success/failure/security events |
| OPS-ALERT-001 | Material failures generate actionable, owned alerts | S | C2 | Alert rules and recent test/incident evidence |
| OPS-AUDIT-001 | Privileged and legally significant actions have protected audit trails | S | C3 | Event coverage, access controls, integrity, and retrieval test |
| OPS-IR-001 | Incident response roles, escalation, and containment are usable | S | C2 | Current runbook and exercise or incident evidence |
| BAK-SCOPE-001 | Backups include all state required for recovery | R | C3 | Inventory-to-backup mapping and successful job evidence |
| BAK-PROT-001 | Backups are access-controlled, encrypted, and failure-isolated where warranted | S | C3 | Platform configuration and access evidence |
| BAK-REST-001 | Critical data and service can be restored within declared objectives | R | C3 | Recent restoration evidence measuring integrity, RPO, and RTO |
| DR-DEP-001 | Recovery accounts for identity, keys, DNS, vendors, and operational dependencies | D | C3 | End-to-end recovery exercise or independently validated runbook |
| PERF-BASE-001 | Critical journeys have measured latency and resource baselines | R | C2 | Representative measurements tied to environment and build |
| PERF-CAP-001 | Capacity limits and scaling behavior are known for expected demand | S | C2 | Authorized tests or credible operational evidence |
| PERF-DEGRADE-001 | Overload fails safely without corruption or uncontrolled cascading failure | D | C3 | Authorized overload/fault evidence |
| COST-ABUSE-001 | User or attacker-controlled work cannot create unbounded cost | S | C2 | Quotas/budgets/limits and abuse-path tests |

### A.8 Quality, Accessibility, UX, Localization, and Product Trust

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| QA-STRAT-001 | Test strategy covers critical risks at appropriate layers | R | C3 | Risk-to-test mapping and current results |
| QA-NEG-001 | Critical workflows cover invalid, boundary, duplicate, and failure states | R | C3 | Executed negative tests tied to requirements/invariants |
| QA-E2E-001 | Critical journeys pass in the release-representative environment | R | C3 | Current end-to-end evidence for exact build |
| QA-FLAKE-001 | Release decisions are not based on ignored or materially flaky tests | S | C2 | Repeat-run history and documented quarantine discipline |
| QA-COMPAT-001 | Declared browsers, devices, and platforms are verified | S | C2 | Compatibility matrix and representative results |
| A11Y-SEM-001 | Structure, names, labels, and status communication support assistive technology | R | C3 | Manual semantic/screen-reader checks plus supporting automation |
| A11Y-KEY-001 | All applicable functions work by keyboard with visible logical focus | R | C3 | Manual complete-journey keyboard evidence |
| A11Y-VIS-001 | Contrast, reflow, zoom, targets, and motion meet the declared target | S | C2 | Measured and manual evidence across representative screens |
| A11Y-ERR-001 | Errors and authentication do not create avoidable accessibility barriers | S | C2 | Manual invalid/recovery tests with assistive techniques |
| UX-CRIT-001 | Critical journeys are understandable, recoverable, and efficient | R | C2 | Heuristic and task evidence tied to target users |
| UX-TRUST-001 | Consequential actions communicate state, scope, and consequences | R | C3 | Runtime review of confirmation, progress, success, and failure states |
| UX-BRAND-001 | Customer-facing design intentionally supports brand and audience trust | S | C1 | Documented direction and consistent representative implementation |
| I18N-TEXT-001 | User content supports required language, encoding, plural, and expansion behavior | S | C2 | Locale tests and representative translated layouts |
| I18N-FMT-001 | Dates, time zones, numbers, names, addresses, and sorting behave for supported locales | S | C2 | Boundary tests across declared locales |

### A.9 Platform-Specific, Model, Documentation, and Retirement

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| DESK-INSTALL-001 | Installation and removal are predictable, scoped, and reversible | R | C2 | Clean-machine install/update/uninstall evidence |
| DESK-UPDATE-001 | Desktop updates verify origin/integrity and fail safely | S | C3 | Signing/update configuration and negative test |
| DESK-LOCAL-001 | Local files, secrets, IPC, and protocol handlers resist untrusted input | S | C3 | Code/config and representative boundary tests |
| MOB-PERM-001 | Mobile permissions and secure storage are least privilege | R | C3 | Manifest/config, code paths, and device tests |
| MOB-LIFE-001 | Interruption, backgrounding, deep links, and backups preserve safety | S | C2 | Device lifecycle and link tests |
| MOD-BOUND-001 | Model output is treated as untrusted at consequential boundaries | R | C3 | Validation/authorization code and adversarial tests |
| MOD-INJECT-001 | Untrusted content cannot override protected instructions or tool authority | S | C3 | Prompt/tool boundary review and authorized injection tests |
| MOD-DATA-001 | Prompts, retrieval, logs, and providers preserve data and tenant boundaries | R | C3 | Data-flow/config review and cross-context negative tests |
| MOD-EVAL-001 | Model behavior is evaluated against material tasks and harms | S | C2 | Versioned dataset, metrics, thresholds, and current results |
| MOD-FAIL-001 | Provider/model failure, drift, cost, and uncertainty have bounded behavior | D | C2 | Fallback, monitoring, budget, and induced failure evidence |
| DOC-SETUP-001 | Build, setup, configuration, and deployment documentation matches the release | R | C2 | Independent execution or sampled verification |
| DOC-OPS-001 | Operations, rollback, recovery, security, and support procedures are usable | S | C3 | Current runbooks and exercise/incident evidence |
| RET-DATA-001 | Closure, export, deletion, retention, and legal holds are controlled | S | C2 | Procedure plus authorized lifecycle test |
| RET-SVC-001 | Retired services revoke access and remove unintended exposure | D | C2 | Decommission checklist and post-retirement verification |

### A.10 Administrator and Insider Abuse

| Control ID | Objective | Tier | Crit. | Minimum PASS evidence |
|---|---|---:|---:|---|
| ADM-LEAST-001 | Administrative access is role-scoped and not routinely shared | R | C3 | Effective permissions and account inventory |
| ADM-TRACE-001 | Privileged reads, changes, exports, impersonation, and deletions are attributable | S | C3 | Protected audit events and retrieval tests |
| ADM-DUAL-001 | Highest-consequence actions use separation, approval, or strong compensating controls | D | C2 | Workflow/config and authorized negative tests |
| ADM-BREAK-001 | Emergency access is bounded, monitored, and reviewed after use | D | C2 | Break-glass procedure, controls, and exercise evidence |

---

## Appendix B. Worked Calibration Examples

### B.1 Finding Example

**Finding:** `AUD-APP-20260710-001-F003 - Cross-tenant invoice access`
**Control:** `SEC-AUTHZ-001`
**Status:** FAIL
**Severity:** High
**Likelihood:** Medium
**Confidence:** High
**Evidence:** Authorized Tenant B account retrieved Tenant A invoice by changing the object identifier; reproduced twice in staging; server route lacked tenant scope.
**Impact:** Confidential commercial and personal billing information could be disclosed across tenants.
**Preferred fix:** Resolve invoices through the authenticated tenant relationship and return a non-disclosing denial for mismatches.
**Alternative:** Temporary gateway denial for the affected route plus feature disablement until server-side scoping is deployed.
**Verification:** Repeat authorized cross-tenant reads, updates, exports, and enumeration attempts; confirm denial and protected audit event.
**Score effect:** Control receives 1 point at C3 weight. Security/privacy category is capped at 4.9 while the High FAIL remains unresolved.

### B.2 Category Example

A category has five applicable controls:

- C3 PASS: 10 × 3
- C3 High FAIL: 1 × 3
- C2 Medium WARN: 6 × 2
- C2 PASS: 10 × 2
- C1 UNVERIFIED: excluded from quality mean, included in coverage denominator

Provisional quality score: `(30 + 3 + 12 + 20) / (3 + 3 + 2 + 2) = 6.5`.

Coverage: `4 / 5 = 80%`.

Because an unresolved High FAIL exists, the mandatory category cap produces a final score of **4.9/10, 80% coverage, High confidence**.

### B.3 Re-Audit Example

If the High finding is fixed, the re-audit must confirm the current build, repeat the cross-tenant test, run adjacent tenant-write and export controls, and record the finding as REMEDIATED. The category is then recalculated from current control evidence; the old score is never edited retroactively.

---

## Appendix C. Changelog

| Version | Date | Change summary |
|---|---|---|
| 2.0 | 2026-07-10 | Initial production standard: mission, trust principles, evidence model, finding standard, coverage domains, scoring bands, release gates, deliverables |
| 2.1 | 2026-07-10 | Deterministic scoring with caps, depth tiers, risk profiles, threat-model fallback, systemic-risk rule, re-audit/delta mode, machine-readable artifacts, independent challenge, versioned control catalog, worked examples |
| 2.2 | 2026-07-10 | Normative control-to-category mapping (A.0), WARN - High scoring rule and reclassification test, tier-relative coverage disclosure, gate-control separation, CC BY 4.0 license |

---

**Specification Version:** 2.2
