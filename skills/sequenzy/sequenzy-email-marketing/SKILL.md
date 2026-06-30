---
name: sequenzy-email-marketing
description: Primary agent guide for operating Sequenzy as an email-marketing platform. Use when Codex needs to authenticate, inspect identity, manage subscribers, create or edit campaigns/sequences/templates, control the campaign lifecycle (cancel, pause, resume, delete, duplicate), run campaign A/B tests, mutate lists/tags/segments, enroll subscribers into sequences, invite team members, triage and reply to inbox conversations, manage outbound webhooks, generate draft email content, send transactional email, read delivery stats, or decide whether a requested Sequenzy email-marketing workflow is currently supported. Prefer this over the generic sequenzy skill when both seem relevant.
---

# Sequenzy Email Marketing

## Overview

Use this as the default skill for Sequenzy email-marketing/product operations: subscribers, lists, tags, segments, campaigns, sequences, templates, AI email generation, transactional sends, delivery stats, dashboard URLs, CLI/MCP behavior, and currently-supported workflow checks. Prefer the `sequenzy` CLI for supported workflows, treat `packages/mcp/src/tools/index.ts` as the MCP source of truth when the task goes through MCP tools, and explicitly call out when a requested workflow is not wired in the current implementation. If both `sequenzy` and `sequenzy-email-marketing` match, load this skill first.

## Ground Rules

1. Treat `packages/cli/src/index.tsx` as the source of truth for which commands are actually wired.
2. Treat `packages/cli/src/commands/` and `packages/cli/src/api.ts` as the source of truth for CLI behavior, payload shape, and API routes.
3. Treat `packages/mcp/src/tools/index.ts` as the source of truth for MCP tool names, arguments, and preflight validation.
4. Do not promise support for commands or tools that only appear in docs or `--help` text without an attached implementation.
5. Prefer `sequenzy login` for interactive auth and `SEQUENZY_API_KEY` for automation.
6. Prefer inspection before mutation whenever the workflow allows it.

## Supported Workflows

Read [references/use-cases.md](references/use-cases.md) before executing anything non-trivial. The currently implemented CLI flows are:

- login and logout
- local auth/session check with `whoami`
- account inspection with `account`
- company inspection or creation with `companies list|get|create`
- stats overview or stats by campaign/sequence ID
- subscribers `list`, `add`, `get`, and `remove`, with `list` fetching every page by default and supporting tag, segment, and list filters
- lists `list`, `create`, `update`, `delete`, `add-subscribers`, `remove-subscribers`, and `import` alias for bulk list population from emails, JSON, CSV, or newline files
- tags `list`, `create`, `update`, and `delete`, with bare `sequenzy tags` still listing tag definitions for backwards compatibility
- segments `list`, `create`, `update`, `delete`, and `count`, including `--match any`, nested filter roots, custom event filters, and saved-segment composition filters
- templates `list`, `get`, `create`, `update`, and `delete`, with `list` supporting label filters and `create`/`update` accepting labels, raw HTML, or Sequenzy block JSON
- campaigns `list`, `get`, `create`, `update` including label and reply-to updates, `schedule`, and `test`, with `list` supporting label filters, `create` accepting labels plus raw HTML, Sequenzy block JSON, or prompt-generated content, `update` accepting labels plus raw HTML or Sequenzy block JSON, and `schedule` returning a review preview link
- campaign lifecycle control with `campaigns cancel` (stops scheduled, paused, waiting-approval, or sending campaigns immediately, no confirmation prompt), `campaigns pause` and `campaigns resume` for an active send (resume supports `--spread-over-hours`), `campaigns delete` (blocked while sending, scheduled, or paused - cancel first), and `campaigns duplicate` with `--mode campaign|ab_test|variant`
- ab-tests `list`, `get`, `stats`, `restart`, `update-variant`, `create`, `add-variant`, `delete-variant`, and `delete`; create/add-variant/delete-variant/delete work on campaign A/B tests in draft status, variant A is the protected control, and `restart` reruns a finished sequence A/B test
- MCP template and campaign tools support labels on list/create/update; MCP `update_campaign` also supports `replyTo` and `replyProfileId`, and MCP `schedule_campaign` schedules draft or already scheduled campaigns
- MCP `search_subscribers` supports list filters through `list`, `listId`, or `listName`; MCP `add_subscribers_to_list` accepts up to 500 emails per call
- sequences `list`, `get`, `create`, `update`, `enable`, `disable`, `delete`, `enroll`, and `cancel-enrollments`, including explicit discount action steps, cancellation by subscriber ID or event-property field values, and `update` branch insertion with tag, list, segment, event, clicked-link, and field conditions; event and clicked-link branch checks can use `activityScope` (`this_sequence`, `previous_email`, `ever`)
- manual sequence enrollment with `sequences enroll` from emails, JSON, or files, optionally at a specific node with `--target-node-id`, reporting enrolled, skipped, and not-found subscribers
- team `list`, `invite` with `--role admin|viewer` and owner-only `--billing-access`, and `cancel-invitation`
- inbox `list` with status, search, unread, and pagination filters, `get`, `reply` including internal notes with `--note`, `close`, `reopen`, and `mark-read`
- webhooks `list`, `create`, `update`, `delete`, `test`, `deliveries`, and `replay` for outbound webhook endpoints, with `create` returning a one-time signing secret that must be handled as sensitive
- AI generation with `generate email`, `generate sequence`, and `generate subjects`
- dashboard URL generation with CLI `urls`, MCP `get_app_urls`, and `appUrls`/`url` fields on campaign, sequence, template, and company results
- websites `list`, `add`, `check`, and `guide`
- products `list`, `sync`, `attach-file`, and `detach-file` for digital product delivery, with `attach-file --file` uploading local files via presigned URLs; attached files are exposed on `saas.purchase` events as `{{event.download.url}}` / `{{event.download.name}}` (MCP: `list_products`, `attach_product_file`, `remove_product_file`, `sync_products`)
- API key creation with `api-keys create`, handled as sensitive output
- send one transactional email by template or raw HTML

## Unsupported Or Placeholder Workflows

Treat missing subcommands as unsupported even when the noun exists. The main remaining gap is campaign immediate send: there is no "send now" command, so schedule the campaign with a near-future `--at` timestamp instead. Bulk list population is supported through `sequenzy lists add-subscribers` and its `sequenzy lists import` alias, not through `subscribers add`.

## Execution Pattern

1. Check auth first with `sequenzy whoami` or by verifying `SEQUENZY_API_KEY` is set.
2. Pick the narrowest command that matches the use case.
3. Validate IDs, recipient email, subject, template, or content input before issuing a mutation.
4. Surface CLI limitations directly instead of inventing a workaround.
5. If the workflow is unsupported in the CLI, say whether the next-best path is the Sequenzy dashboard or direct API use.
6. When you create, inspect, or schedule a campaign, sequence, template, or company and the user may want to review/edit it, surface the dashboard URL from `url`, `previewUrl`, or `appUrls` in the tool/CLI output. If needed, generate it with `sequenzy urls` or MCP `get_app_urls`.
7. Destructive commands (`delete`, `delete-variant`, `cancel-invitation`, and similar) prompt for confirmation. Pass `--yes` (or `-y`) to skip the prompt; `--yes` is required when stdin is not a TTY, which covers most agent and CI runs.
8. Treat API keys, webhook signing secrets, and other one-time credentials as sensitive output. Do not paste raw secret values into chat, logs, tickets, or public transcripts. Capture them to a user-approved secure destination such as a password manager, secret store, encrypted file, or local `.env` file outside version control; otherwise redact the value and report only where it was saved plus a short fingerprint.
9. Call out implementation caveats that matter operationally, such as `whoami` using cached local auth state, sequence creation supporting both `--goal` and explicit step modes, explicit discount steps requiring Stripe before activation, generated sequences being capped at 10 emails, `campaigns test` being a stubbed success path in the current backend, and conditional email content requiring block JSON rather than raw HTML.

## Dashboard URLs

Use `SEQUENZY_APP_URL` as the dashboard base when it is set; otherwise default to `https://sequenzy.com`.

Prefer actual URLs returned by the CLI/MCP result:

- sequence editor: `/dashboard/company/{companyId}/sequences/{sequenceId}`
- campaign editor: `/dashboard/company/{companyId}/campaign/{campaignId}`
- campaign preview/review: `/dashboard/company/{companyId}/campaign/{campaignId}?step=review`
- template/email editor: `/dashboard/company/{companyId}/emails/{emailId}`
- settings: `/dashboard/company/{companyId}/settings`
- settings tab: `/dashboard/company/{companyId}/settings?tab={tab}`

Useful settings tabs include `domain`, `tracking`, `localization`, `integrations`, `events`, `tags`, `goals`, `sync-rules`, `api-keys`, `widgets`, and `team`.

## References

- [references/command-reference.md](references/command-reference.md): exact command shapes, env vars, behavior, and caveats.
- [references/use-cases.md](references/use-cases.md): decision trees and examples for the most common agent tasks.
