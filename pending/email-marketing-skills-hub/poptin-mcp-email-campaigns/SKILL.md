---
name: poptin-mcp-email-campaigns
description: Create and manage email campaigns through Poptin MCP, using a pre-made or saved template or user-provided HTML, previewing and saving the right audience, and leaving a verified draft or explicitly confirmed send or schedule. Use for hands-on Poptin campaign execution, not cold outreach or lifecycle automation design.
---

# Poptin MCP Email Campaigns

Turn the user's campaign brief into a verified Poptin campaign. Use the connected Poptin MCP tools, not Gmail or a substitute sending service. Installing this skill does not connect an account or authorize any campaign.

## Discover the connection and capabilities

Read the [capability reference](references/capabilities.md) when connecting, resolving a missing tool, or choosing the HTML route. Inspect the currently exposed MCP tools and their input schemas before calling them. Use actual returned account, campaign, audience, property and template IDs; never invent tool names, parameters or IDs.

Verify the authorized account/subaccount, email feature availability, sending setup and the intended sender/reply-to. A connection is scoped to one account. If missing, guide the user through the supported OAuth connection to `https://mcp.popt.in/mcp`; do not request passwords, API keys or tokens in chat. Do not change credentials, account permissions or DNS as a side effect.

## Establish the brief and end state

Reuse supplied context. Identify the objective, campaign name, subject/preheader, sender, approved content/offer, CTA, intended recipients and exclusions. Determine whether the user wants a **draft**, **send now**, or **scheduled send**. Ask only for missing facts that block that outcome. If launch intent is unclear, prepare a draft, not a send. This skill never grants standing send permission.

Inspect existing campaigns before creating one. Resume the intended draft rather than duplicating it; preserve human edits and do not alter an already-scheduled or sending campaign without explicit direction. Record its ID after creation. A timeout is not proof that creation failed.

## Build the right audience

1. Inspect existing segments, contact properties, subscription topics/preferences and supported filter operators. Reuse correct existing objects instead of creating duplicates.
2. Translate the brief into explicit inclusion and exclusion rules. Make AND/OR grouping and time windows clear. Distinguish subscribed recipients from all matching contacts. Preserve topic-specific consent, opt-outs, suppression and bounce exclusions; never subscribe contacts or import a list merely to enlarge the audience.
3. Preview the proposed segment using the actual supported tools. Review the counts and a minimal appropriate sample without exporting raw contact data unnecessarily. Check overlap with competing campaigns and exclude ineligible customers or recent recipients when the brief calls for it.
4. Save a reusable, descriptively named segment only when requested or needed for the authorized campaign. Explain the saved rule, not just the count. If segment creation is unavailable, retain a proposed rule and report the limitation rather than claiming it was saved.
5. Use the **campaign's own audience preview** after applying the segment/filter. A saved segment's matching count is not the campaign's eligible send count. Record count, exclusions and preview time. Determine whether recipients are fixed now or recalculated at send time; if the tool does not expose that, say so before launch.

## Choose and prepare the design

**Pre-made or saved template:** browse the connected account's available gallery and saved templates, inspect the selected design and use its real ID. Populate the approved copy, links and assets through supported editing tools. Do not overwrite a shared original template when only a campaign copy is intended.

**HTML upload:** inspect the supplied HTML and its assets first. Use an HTML import/upload/content field only if the currently exposed MCP schema supports it. Never pass HTML into a template-ID field or claim a file was uploaded when it was only drafted locally. If the MCP connection lacks HTML import, prepare checked HTML and give the user the precise Poptin UI handoff; resume with the resulting saved template/campaign ID after it exists. Do not silently substitute a gallery template. See the [capability reference](references/capabilities.md) for the verified boundary.

For either route, preserve unsubscribe and preference controls, required sender details and valid personalization fallbacks. Use Poptin's actual supported merge syntax, not guessed tags. Check CTA destinations, image alt text, mobile layout, subject/preheader and approved offer facts. Do not invent discounts, deadlines or claims. Inspect a rendered preview when available; distinguish source review from actual rendering. Missing content, broken mandatory links or unverified audience eligibility block launch, not saving a clearly identified draft.

## Review, then take exactly one outcome

Read back the saved campaign and preview its content and audience. Present a concise launch summary: account, campaign ID/name, sender/reply-to, subject, content/design version, audience rules/exclusions, eligible count, and requested outcome. For a schedule, resolve the full date, local time, IANA timezone and UTC equivalent, including daylight-saving ambiguity. Never silently shift a past time to another date.

- **Draft:** save through the supported draft operation and verify the campaign is a draft, not queued, scheduled or sending. Do not call a send/schedule operation to save it.
- **Send now:** obtain explicit confirmation of this final campaign, content and audience immediately before the actual send. Re-read status and audience for changes, then use the supported send operation once.
- **Schedule:** obtain explicit confirmation of this final campaign, content, audience and exact time/timezone immediately before scheduling. Re-read status and audience for changes, then use the supported schedule operation once.

A request to build the campaign, approve copy, or install this skill is not launch confirmation. If material content, recipients, sender or timing changes after confirmation, show the change and reconfirm. Honor any server-provided confirmation workflow without bypassing it. Test emails are real sends: send only when requested/approved to explicitly verified test recipients, never to the production audience by default.

## Verify and report

After a mutation, read the same campaign ID back. For asynchronous operations, follow the returned status/job identifier through supported read tools. Report **saved draft**, **scheduled** with the verified time, **sending**, or **completed dispatch**, exactly as observed. Accepted requests and SENT/dispatch are not proof of delivery.

On a timeout, denial or ambiguous response, stop further launch attempts. Reconcile the campaign status, job/request ID and logs before considering any retry; never create a replacement campaign to escape uncertainty. Keep an operation receipt in the user's existing authorized work context: campaign ID/link if returned, content version, audience count/preview time, confirmed outcome, request/job IDs and final observed status. Do not store recipient exports or secrets in this skill or a public repository.

Use [scenario checks](references/scenario-checks.md) to evaluate behavior without sending live campaigns.
