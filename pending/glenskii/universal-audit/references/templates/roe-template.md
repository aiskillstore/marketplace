# Rules of Engagement - {{AUDIT_ID}}

No active security, load, resilience, destructive, or production-impacting test begins
until every field below is recorded. Incomplete RoE = passive, read-only inspection only.
Spec Section 7 is normative.

- Written authorization by (name, role, date):
- Approved targets:
- Explicitly excluded targets:
- Approved environment(s):
- Testing dates and time zone:
- Permitted techniques:
- Prohibited techniques:
- Rate and concurrency limits:
- Approved accounts and privilege levels:
- Data-handling restrictions:
- Logging and evidence-storage rules:
- Emergency stop method and contact:
- Incident escalation process:
- Proof-of-concept exploitation permitted: yes / no
- Test-created data must be removed: yes / no

## Hard prohibitions (always, regardless of authorization fields above)

- No denial-of-service testing without explicit written authorization.
- Never access or alter another real user's data to prove an authorization defect.
- Never exfiltrate secrets or personal data into the report.
- Never weaken a production security control for testing convenience.
- Never install persistent tooling or create hidden access.
- Never trigger billing, messaging, deletion, publication, or irreversible external
  actions without approval.

If a dangerous condition is discovered: stop the relevant test, preserve minimal safe
evidence, escalate per the process above.
