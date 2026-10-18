---
name: shuffll-engage
description: Use when working with Shuffll Engage video campaigns, published templates, creative journeys, previews, recipient segments, generation jobs, video results, or campaign analytics through its MCP or API.
---

# Shuffll Engage

Shuffll Engage — Personalized video at scale. Help users build video campaigns around customer interests, behaviors and audience segments, including product and e-commerce use cases, through the Engage API and MCP. Product positioning does not establish what a particular connection can do.

## Connect and discover

Use the configured Shuffll Engage MCP tools. The hosted Streamable HTTP endpoint is `https://engage.shuffll.com/mcp`; the REST base is `https://engage.shuffll.com/api`. Read the [public documentation](https://api-docs.shuffll.com/engage) for REST contracts. Existing Shuffll video-production API credentials are not interchangeable with Engage credentials.

Authenticate through the client's supported OAuth flow or private credential settings. Never put credentials in URLs, source files, chat, or a public configuration. If OAuth lists no eligible organization, ask the workspace administrator to enable the intended organization's API/MCP access. Connection recovery does not authorize policy changes, credential creation or choosing another tenant. An explicitly requested administration task requires separately verified administrative capability.

Discover the current tools and schemas, call `capabilities_get` if exposed, and resolve the intended authorized organization before mutations. Available operations vary with grants, entitlements and release versions. Limits and catalog entries do not confer write permission. Use only tools actually exposed to this connection; names below are discovery hints, not permission or a complete tool inventory.

## Choose the supported workflow

| User goal | Starting point |
| --- | --- |
| Browse existing content | Authorized templates, versions, assets and campaigns |
| Make or refine a creative video | Available `journey_*` operations and their current schemas |
| Generate from a published template | Ready immutable template version, then campaign workflow below |
| Check completion or performance | Jobs, results and available analytics |

For published templates, inspect `templates_list`, `template_versions_list` and `template_versions_get` where available. Require a render-ready source before generation. Preserve a user's template selection; explain an unusable selection before proposing a different template. The legacy `flat-video-v1` route creates fixed video, as described in the [campaign guide](https://api-docs.shuffll.com/engage/workflows): recipient names, segments and contact fields alone do not personalize its media. For variation or personalization, establish the actual supported journey/template inputs and inspect representative outputs. Explain a missing capability before offering the available workflow.

Resolve the real audience and required inputs from the user's authorized source. A label such as “VIP customers” is not a recipient list. Use synthetic data for demonstrations. Do not import contacts, generate paid media, publish templates, or send messages beyond the user's request and the granted capabilities. Existing authorization is enough when it covers the concrete action; do not add repetitive confirmation steps.

## Campaigns, retries and results

Create the campaign with the chosen template/version; retain returned IDs and revisions. Add authorized recipients only when needed. Creating a campaign is distinct from starting generation. Start generation only when requested, with a ready source and the current schema's required inputs.

For MCP mutations requiring `operation_id`, use a unique value for each new action. After a timeout, inspect existing job/resource state first. Reuse the operation ID only for an uncertain retry with identical input. A new paid generation after a confirmed failure requires authorization covering that additional spend. Read the latest resource revision before supplying `expected_revision`; reconcile conflicts before retrying. REST uses the documented `Idempotency-Key` and `If-Match` equivalents. Follow returned pagination cursors and `pollAfterSeconds` rather than inventing offsets or repeatedly starting jobs.

Inspect jobs through `jobs_get` and then actual results through `campaign_results_list` / `campaign_results_get`, where exposed. Report queued, completed, failed and partially failed outcomes accurately. Generated media is not evidence of message sending, delivery, views or engagement. Sending requires a separately supported, authorized delivery operation; never substitute generation for delivery.

## Creative work

For available creative journey tools, read [creative guidance](references/creative.md) before authoring or finishing. Preserve the user's brief and explicit choices. Inspect the saved state and actual playable output before claiming that music, captions, overlays, personalization or transitions work. A preview does not prove final MP4 parity.

For example: “Show my available templates and explain which can render” needs read-only discovery and readiness inspection. “Create a campaign without generating it” authorizes campaign creation, not rendering or delivery. Return the relevant identifier, observed state, useful output link and any remaining blocker; exclude credentials and recipient details from diagnostic logs.
