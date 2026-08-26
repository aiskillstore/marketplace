# Discovery source registry

The packaged [`SOURCES.json`](SOURCES.json) catalog is the reviewed, versioned list of repeatable discovery surfaces available to every installation. A community registry supplements it with maintainer-reviewed discovery sources and direct public job links from confirmed applications. Both remain distinct from application channels such as Greenhouse, Ashby, Lever, and Workday.

## Use the catalog

```text
node scripts/job-application.mjs sources list
node scripts/job-application.mjs sources list --stdin
node scripts/job-application.mjs sources jobs
echo '{"limit":25,"cursor":"opaque-cursor"}' | node scripts/job-application.mjs sources jobs --stdin
```

Optional filter input:

```json
{
  "regions": ["india", "global", "remote"],
  "roleFamilies": ["engineering"],
  "kinds": ["job-board", "startup-network"],
  "requiresSession": false
}
```

`sources list` combines the packaged catalog with the live repeatable-source registry. Public v1 community entries are always maintainer-approved and have `registryStatus: "community-reviewed"`. Their `id` and `communitySourceId` are the same stable community ID and may be stored as `discoverySourceId`. `sources jobs` returns the newest maintainer-reviewed confirmed job links, 50 at a time by default, with an opaque `nextCursor` for pagination. Both are discovery leads, not endorsements or eligibility claims. Resolve every lead to the direct employer or ATS page and verify that posting immediately before assessment and submission.

Store three independent attribution fields when available:

- `discoverySource`: coarse compatible channel such as `linkedin`, `x`, `yc`, `job-board`, or `user-supplied`.
- `discoverySourceId`: stable packaged or community ID such as `yc-work-at-a-startup` or `community-abcdef1234567890`.
- `applicationChannel`: actual submission channel such as `greenhouse`, `ashby`, `lever`, `company`, or `email`.

`discoverySourceId` remains local in v1 and is not transmitted by telemetry.

## Community sharing

Community sharing is enabled by default and independent of usage analytics. A confirmed `ledger add` queues and attempts the sanitized public job metadata automatically. Installations with historical applications consume one full disclosure command without transmission before backfill, giving them time to run `sources sharing disable`; an explicit `sources sharing enable` opts in immediately. New installations have no historical backfill and contribute the first newly confirmed job after displaying the notice. Existing confirmed ledger entries are the durable backfill/retry queue and are retried in bounded batches during later commands. No separate contribution command is required for applied jobs.

Whenever the user or agent discovers a repeatable public discovery surface—not a recruiter profile, referral link, personal URL, or one-off job detail route—queue it for maintainer review:

```text
node scripts/job-application.mjs sources suggest --stdin
node scripts/job-application.mjs sources pending
node scripts/job-application.mjs sources sync
node scripts/job-application.mjs sources jobs
node scripts/job-application.mjs sources sharing status
node scripts/job-application.mjs sources sharing disable
```

Suggestion input:

```json
{
  "name": "Example Engineering Board",
  "baseUrl": "https://jobs.example.org/openings/engineering",
  "kind": "job-board",
  "regions": ["global"],
  "roleFamilies": ["engineering"],
  "requiresSession": false
}
```

The first eligible contribution displays a disclosure and sends during that command. `disable` stops both job and discovery-source sharing; `enable` resumes and retries it; `reset` disables sharing and removes its anonymous relay credentials. The preference, anonymous credential, and delivery receipts are stored in owner-only local files.

The applied-job contract contains only the canonical HTTPS job URL, company, role, application channel, optional coarse discovery source, and a server-derived provider URL. Referral, tracking, and fragment data are removed; a small allowlist of stable job/requisition query identifiers is retained so query-addressed jobs do not collapse together. The server adds day-bucketed first/last-seen dates and an anonymous agent-report count. Candidate identity, résumé, form answers, score, application timestamp, referral parameters, raw installation ID, and contributor hash are never public or stored with a community job. Every accepted record is logged as pending; only a maintainer-reviewed destination and matching company/role can become public. Canonical URL deduplication prevents repeated rows, and rejected records never republish automatically.

The client and relay use the same fail-closed source-route classifier. They remove query parameters and fragments; reject embedded credentials, credential-like opaque path segments, identity-like names and paths, personal profiles, local/private hosts, unknown fields, oversized payloads, and known detail routes from Workday, LinkedIn Jobs, Greenhouse, Lever, Ashby, Workable, and SmartRecruiters. Unknown domains are accepted only at the root or on explicit collection, directory, feed, careers, openings, or job-index routes. Only the source name, canonical public base URL, kind, regions, role families, and session requirement are shared.

The raw anonymous installation ID authenticates and rate-limits a request but is never stored in the registry. The relay stores a source-scoped HMAC only to deduplicate contributions and help a maintainer prioritize review. One system contributes at most once to a canonical source, and `contributionCount` always means unique contributing systems—not people. It is never identity, trust, authority, or a condition for publication. The first valid contribution owns the canonical metadata; later contributions cannot rewrite it.

If sharing is disabled or offline, repeatable-source suggestions remain in their owner-only queue and confirmed jobs remain pending in the canonical ledger until a minimal delivery receipt exists. `sources pending` reports both kinds of locally unsent work. `sources sync` retries both, and `sources list` performs a best-effort retry before reading the registry. A server-accepted source suggestion is delivered even while pending moderation. Network failure never blocks discovery or an application.

Every accepted repeatable-source contribution remains in the private moderation queue until an owner explicitly approves it with owner-only D1 commands. Rejected sources remain hidden after later contributions and cannot republish automatically. Maintainer procedures are documented in [`telemetry-worker/COMMUNITY_SOURCE_MODERATION.md`](https://github.com/vaibhavarora14/job-application-agent/blob/main/telemetry-worker/COMMUNITY_SOURCE_MODERATION.md). This moderation rule does not delay sanitized confirmed-job links.
