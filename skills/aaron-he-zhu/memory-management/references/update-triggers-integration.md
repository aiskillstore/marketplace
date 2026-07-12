# Update Triggers and Cross-Skill Integration

These are permission-aware working-memory routines. They never grant standing write authority and never bypass a registry owner.

## Common Sequence

1. Finish the user-facing result and label evidence/source dates.
2. If persistence is authorized, save the smallest useful WARM artifact in the producing skill's path.
3. For durable truth, submit one idempotent `operation: propose` event per aggregate to the owning registry with current `expected_revision`.
4. Do not write HOT unless the user explicitly pins a conclusion.
5. Do not publish, send, upload, spend, or delete as part of a memory update.

## Trigger Table

| Trigger | WARM action | Registry action | Safety note |
|---|---|---|---|
| Ranking/competitor read | Save dated research/monitoring artifact | Entity proposal only for durable identity facts | A movement threshold is a review cue, not automatic promotion |
| Content/ad/email/social build | Save versioned asset/handoff | Claims/Narrative/channel proposals as needed | Preserve `[needs source]`; no external execution |
| Influencer campaign close | Save closed-cycle analysis | Creator proposals for rate/rights/outcomes | Minimize personal data; no reputation label |
| Paid readback | Save normalized window and truth-set reconciliation | Claim/offer proposal when state changed | No automatic budget action |
| Email suppression event | Save no duplicate contact data | Direct consent `suppress`, then replay check | Never queue withdrawal as a proposal |
| Launch T-0 observation | Save incident/runbook evidence | Launch proposal per timestamped fact | Registry resolves in offset order; no stream clearing |
| Narrative change | Save authored draft/test evidence | Complete-canon proposal, not partial patch | Claims remain separate pointers |
| Auditor gate | Present result; save only when authorized | No registry mutation | v3 artifact validator required; no automatic HOT write |

## Archive Management

### Monthly

- Review HOT pointers older than 30 days and demote when no longer current.
- Review WARM artifacts older than 90 days and archive with original path/content hash metadata.
- Run the consolidation pass for duplicates, explicit supersession, broken links, and unsupported summaries.
- Do not archive or compress registry streams/projections through the temperature lifecycle.

### Quarterly

- Review COLD retention and legal-hold requirements.
- Link milestone summaries to source artifacts rather than copying scores/facts without context.
- Verify all seven registry streams and rebuild projections when needed.
- Review consent suppression by replay before any reactivation workflow.

## Integration Boundaries

| Role | Allowed persistent action |
|---|---|
| Ordinary execution skill | Own WARM artifact plus authorized proposal events |
| Auditor gate | Own validator-clean audit artifact after permission |
| Registry owner | Accept/reject/upsert/transition its registry through runtime |
| `memory-management` | HOT/WARM/COLD lifecycle and authorized tombstone/erase |

Monthly indexes may reference audit artifact IDs but must not synthesize a cross-framework score. Registry projections and human views always expose the source offset/revision.
