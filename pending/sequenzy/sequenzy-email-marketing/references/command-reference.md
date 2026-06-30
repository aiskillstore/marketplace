# Command Reference

## Source Of Truth

- Command registration: `packages/cli/src/index.tsx`
- Auth storage and config: `packages/cli/src/config.ts`
- HTTP requests: `packages/cli/src/api.ts`
- Implemented handlers: `packages/cli/src/commands/`

If docs and code disagree, trust the code.

## Authentication

### Interactive login

```bash
sequenzy login
```

- starts device auth against `POST /api/device-auth/initiate`
- polls `POST /api/device-auth/poll`
- opens `${SEQUENZY_APP_URL}/setup/auth?code=...` in the browser
- stores the API key in `Bun.secrets` when available, otherwise in local config

### Non-interactive auth

Set `SEQUENZY_API_KEY` in the environment. `packages/cli/src/config.ts` checks this before local storage, so it is the safest path for automation.

### Identity and logout

```bash
sequenzy whoami
sequenzy account
sequenzy logout
```

Behavior:

- `whoami` prints cached local config only
- `account`: `GET /api/v1/account`
- `logout` removes locally stored auth

Caveat:

- treat `whoami` as "is this machine authenticated?" rather than authoritative server-side account discovery

## Environment Variables

```bash
SEQUENZY_API_KEY=...
SEQUENZY_API_URL=https://api.sequenzy.com
SEQUENZY_APP_URL=https://sequenzy.com
```

Notes:

- `SEQUENZY_API_KEY` overrides local keychain/config state
- the current CLI code defaults `SEQUENZY_APP_URL` to `https://sequenzy.com`
- many company-scoped commands accept `--company`, which sends `x-company-id` for personal API keys

## Dashboard URLs

```bash
sequenzy urls --company comp_123
sequenzy urls --company comp_123 --sequence seq_123
sequenzy urls --company comp_123 --campaign camp_123
sequenzy urls --company comp_123 --template tmpl_123
sequenzy urls --company comp_123 --settings-tab integrations
sequenzy urls --company comp_123 --json
```

Behavior:

- uses `SEQUENZY_APP_URL` as the base URL, defaulting to `https://sequenzy.com`
- if `--company` is omitted, tries the current company from `GET /api/v1/account`
- returns route templates, settings tab values, and concrete URLs when a company ID is known
- campaign, sequence, template, company, and account outputs include `url` or `appUrls` fields when the company can be resolved

Common route patterns:

- sequence editor: `/dashboard/company/{companyId}/sequences/{sequenceId}`
- campaign editor: `/dashboard/company/{companyId}/campaign/{campaignId}`
- template/email editor: `/dashboard/company/{companyId}/emails/{emailId}`
- settings: `/dashboard/company/{companyId}/settings`
- settings tab: `/dashboard/company/{companyId}/settings?tab={tab}`

## Stats

```bash
sequenzy stats
sequenzy stats --period 30d
sequenzy stats --campaign camp_123
sequenzy stats --sequence seq_123
```

Behavior:

- no ID: `GET /api/v1/metrics?period=7d|30d|90d`
- `--campaign`: `GET /api/v1/metrics/campaigns/:id`
- `--sequence`: `GET /api/v1/metrics/sequences/:id`

Output includes:

- `sent`
- `delivered`
- `opened`
- `clicked`
- `unsubscribed`
- `openRate`
- `clickRate`

## Subscribers

### List

```bash
sequenzy subscribers list
sequenzy subscribers list --tag vip
sequenzy subscribers list --list "Master List" --json
sequenzy subscribers list --segment seg_123
sequenzy subscribers list --limit 100
sequenzy subscribers list --tag vip --company comp_123 --json
```

Behavior:

- sends `GET /api/v1/subscribers`
- maps `--segment` to `segmentId`
- maps `--tag` to `tags`
- maps `--list` to `list`; the API resolves list ID first, then exact list name
- maps `--limit` to `limit`
- fetches every result page by default when `--limit` is omitted
- supports `--company` and `--json`

### Add

```bash
sequenzy subscribers add user@example.com
sequenzy subscribers add user@example.com --tag premium --attr name=John --attr plan=pro
sequenzy subscribers add user@example.com --tag premium --tag beta --company comp_123 --json
```

Behavior:

- sends `POST /api/v1/subscribers`
- body shape is `{ email, tags, customAttributes }`
- supports repeated `--tag` values
- supports `--company` and `--json`

### Get

```bash
sequenzy subscribers get user@example.com
sequenzy subscribers get user@example.com --company comp_123 --json
```

Behavior:

- sends `GET /api/v1/subscribers/:email`
- returns the full subscriber profile, including list memberships, sequence enrollments, email stats, and recent activity
- supports `--company` and `--json`

### Remove

```bash
sequenzy subscribers remove user@example.com
sequenzy subscribers remove user@example.com --hard
sequenzy subscribers remove user@example.com --company comp_123 --json
```

Behavior:

- without `--hard`, sends `PATCH /api/v1/subscribers/:email` with `{ status: "unsubscribed" }`
- with `--hard`, sends `DELETE /api/v1/subscribers/:email`
- supports `--company` and `--json`

## Transactional Send

### Template-based

```bash
sequenzy send user@example.com --template tmpl_123 --var name=John
```

### Raw HTML

```bash
sequenzy send user@example.com --subject "Hello" --html "<h1>Hi</h1>"
sequenzy send user@example.com --subject "Hello" --html-file ./email.html
```

Behavior:

- sends `POST /api/v1/transactional/send`
- body shape is `{ to, templateId, subject, html, variables }`

Validation enforced by the CLI:

- require either `--template` or `--html`/`--html-file`
- require `--subject` when sending raw HTML

## Companies, Lists, Tags, And Segments

### Companies

```bash
sequenzy companies list
sequenzy companies get comp_123
sequenzy companies create example.com --name Example
```

Behavior:

- `companies list`: `GET /api/v1/companies`
- `companies get`: `GET /api/v1/companies/:id`
- `companies create`: `POST /api/v1/companies`

### Lists

```bash
sequenzy lists list
sequenzy lists create Newsletter --description "Public newsletter list"
sequenzy lists create VIP --private --company comp_123
sequenzy lists update list_123 --name "Weekly Newsletter" --private
sequenzy lists update list_123 --no-private
sequenzy lists add-subscribers list_123 --email one@example.com two@example.com
sequenzy lists add-subscribers list_123 --emails-json '["one@example.com","two@example.com"]'
sequenzy lists add-subscribers list_123 --emails-file ./batch-001.csv
sequenzy lists import list_123 --emails-file ./batch-001.csv
sequenzy lists remove-subscribers list_123 --email one@example.com two@example.com
sequenzy lists remove-subscribers list_123 --emails-file ./churned.csv
sequenzy lists delete list_123 --yes
```

Behavior:

- `lists list`: `GET /api/v1/lists`
- `lists create`: `POST /api/v1/lists`
- create body shape is `{ name, description, isPrivate }`
- `lists update`: `PATCH /api/v1/lists/:listId` with at least one of `--name`, `--description`, `--private`, or `--no-private`
- `lists delete`: `DELETE /api/v1/lists/:listId`; removes the list and all of its memberships, reports `removedMemberships`, and keeps the subscribers themselves
- `lists add-subscribers` and `lists import`: `POST /api/v1/lists/:listId/subscribers`
- `lists remove-subscribers`: `POST /api/v1/lists/:listId/subscribers/remove`
- add-subscribers body shape is `{ emails, duplicateStrategy, enrollInSequences, optInMode }`
- remove-subscribers takes the same email input formats as add-subscribers, only removes list memberships, and reports `removed` plus `notFound` emails
- the CLI splits large files into API-safe batches of up to 500 emails for both add and remove
- files may be newline-separated, CSV with an email column, a JSON email array, or a JSON object with `emails` or `subscribers`
- CSV headers named `email`, `e-mail`, `email address`, or `mail` are detected; otherwise the first column is used
- `lists delete` prompts for confirmation; pass `--yes` to skip
- MCP parity: `update_list`, `delete_list`, and `remove_subscribers_from_list` (max 500 emails per call)

### Tags

```bash
sequenzy tags
sequenzy tags list --company comp_123 --json
sequenzy tags create vip --color purple
sequenzy tags update tag_123 --color red
sequenzy tags delete tag_123 --yes
```

Behavior:

- `tags list`: `GET /api/v1/tags`; bare `sequenzy tags` without a subcommand still lists tag definitions for backwards compatibility
- `tags create`: `POST /api/v1/tags` with `{ name, color? }`
- `tags update`: `PATCH /api/v1/tags/:tagId` with `{ color }` (`--color` is required)
- `tags delete`: `DELETE /api/v1/tags/:tagId`
- tag names are normalized to lowercase with dashes, so `VIP Customer` becomes `vip-customer`
- the color defaults to `gray`; valid colors are `gray`, `red`, `orange`, `amber`, `yellow`, `lime`, `green`, `emerald`, `teal`, `cyan`, `sky`, `blue`, `indigo`, `violet`, `purple`, `fuchsia`, `pink`, and `rose`
- system tags cannot be updated or deleted
- tags still referenced by sequences cannot be deleted until those sequences stop using them
- deleting a tag removes it from every subscriber; the delete prompt warns about this, and `--yes` skips it
- MCP parity: `list_tags`, `create_tag`, `update_tag`, and `delete_tag`

### Segments

```bash
sequenzy segments list
sequenzy segments count seg_123
sequenzy segments create --name "Bought Pro" --stripe-product prod_pro
sequenzy segments create --name "3+ Pro Payments" --stripe-product prod_pro --purchase-operator at-least --payments 3
sequenzy segments create --name "VIP or Churn Risk" --match any --filter-json '[{"field":"tag","operator":"contains","value":"vip"},{"field":"emailOpened","operator":"is_not","value":"30d"}]'
sequenzy segments create --name "Active non-paying" --filter-json '{"kind":"group","id":"root","joinOperator":"and","children":[{"kind":"filter","id":"f1","field":"attribute","operator":"gte","value":"last_login_days_ago:0"},{"kind":"group","id":"g1","joinOperator":"or","children":[{"kind":"filter","id":"f2","field":"attribute","operator":"is_empty","value":"plan_end"},{"kind":"filter","id":"f3","field":"attribute","operator":"lt","value":"plan_end:2026-04-21"}]}]}'
sequenzy segments update seg_123 --name "Churn Risk"
sequenzy segments update seg_123 --filters-json '[{"field":"tag","operator":"contains","value":"vip"}]'
sequenzy segments update seg_123 --join-operator or
sequenzy segments delete seg_123 --yes
```

Behavior:

- `segments list`: `GET /api/v1/segments`
- `segments count`: `GET /api/v1/segments/:id/count`
- `segments create`: `POST /api/v1/segments`
- `segments update`: `PATCH /api/v1/segments/:segmentId` with at least one of `--name`, `--filters-json`, `--filters-file`, or `--join-operator and|or`
- `segments delete`: `DELETE /api/v1/segments/:segmentId`; prompts for confirmation, `--yes` skips
- update filters replace the existing filter set; `--filters-json`/`--filters-file` accept the same array or `root` object shapes as create, and missing filter IDs are filled in by the CLI
- `--filter-json` accepts either the legacy raw segment filter array or a nested filter `root` object
- `--match all|any` controls whether top-level filters are combined with `and` or `or`
- MCP/API use `filterJoinOperator: "and" | "or"` for the same behavior
- nested segment logic uses `{ "kind": "group", "joinOperator": "and" | "or", "children": [...] }`
- custom event filters use `field: "event"` with values like `saas.purchase:30d`, `saas.purchase:all`, or `saas.purchase:5:30d`
- saved segment composition uses `field: "segment"` with `operator: "is" | "is_not"` and the referenced segment id as `value`
- Stripe product filters use `field: "stripeProduct"` and product IDs, not product names
- threshold operators encode the count as `productId:count`, for example `prod_pro:3`
- MCP parity: `update_segment` (reuses the create filter schemas) and `delete_segment`

## Products And Digital Delivery

```bash
sequenzy products list
sequenzy products list --provider stripe --search guide
sequenzy products sync
sequenzy products attach-file <product-id> --file ./guide.pdf
sequenzy products attach-file <product-id> --url https://example.com/template.zip --name template.zip
sequenzy products detach-file <product-id>
```

Behavior:

- `products list`: `GET /api/v1/products`, optionally with `?provider=stripe|shopify|woocommerce|manual&search=...`
- `products sync`: `POST /api/v1/products/sync`; queues a Stripe catalog sync and returns 404 without an active Stripe integration
- `products attach-file --file`: `POST /api/v1/products/delivery/upload-url` for a presigned URL, PUTs the file bytes there, then `PUT /api/v1/products/:id/delivery` with `source: "upload"`
- `products attach-file --url`: `PUT /api/v1/products/:id/delivery` with `source: "url"`
- `products detach-file`: `DELETE /api/v1/products/:id/delivery`
- MCP equivalents: `list_products`, `attach_product_file` (URL attach only), `remove_product_file`, `sync_products`

Caveats:

- the `<product-id>` argument is the internal Sequenzy product ID from `products list`, not the Stripe `prod_...` ID; the Stripe ID is shown as the provider product ID in list output
- uploads accept PDF, ePub, ZIP, images, audio, video, and text files up to 100MB; HTML, SVG, and executables are rejected
- after attaching, purchases of the product enrich the `saas.purchase` event with `download.url` and `download.name`, so purchase sequences can deliver the file with `{{event.download.url}}` and `{{event.download.name}}`
- to start a purchase sequence only for one product, the trigger needs a `productIds equals <stripe product id>` property filter on the `saas.purchase` event; this is configured in the dashboard sequence editor ("Only for product" picker), not through current CLI/MCP flags
- products archived in Stripe stay listed with an archived flag, and attached files survive catalog re-syncs
- the upload endpoint returns 503 when file storage is not configured on the server; fall back to `--url` in that case

## Templates

```bash
sequenzy templates list
sequenzy templates list --label edm
sequenzy templates get tmpl_123
sequenzy templates create welcome --subject "Welcome" --label edm --html-file ./welcome.html
sequenzy templates create welcome --subject "Welcome" --blocks-file ./welcome-blocks.json
sequenzy templates update tmpl_123 --subject "Updated" --label edm --html-file ./welcome-v2.html
sequenzy templates update tmpl_123 --blocks-file ./welcome-v2-blocks.json
sequenzy templates delete tmpl_123
```

Behavior:

- `templates list`: `GET /api/v1/templates`, optionally with `?label=...`
- `templates get`: `GET /api/v1/templates/:id`
- `templates create`: `POST /api/v1/templates`
- `templates update`: `PUT /api/v1/templates/:id`
- `templates delete`: `DELETE /api/v1/templates/:id`

Caveats:

- list accepts `--label <labels...>` to filter by template label name
- create requires `name`, `subject`, and either `html` or `blocks`; it can also assign labels with `--label <labels...>`
- update accepts `name`, `subject`, `html`, `blocks`, and replacement labels with `--label <labels...>`
- `--blocks-json` and `--blocks-file` pass Sequenzy block arrays through directly
- conditional email content is only available through block JSON, using a block-level `condition` object
- raw HTML is still stored as a single text block by the current API path
- deletion can fail if the template is still referenced by a campaign or sequence

## Campaigns

```bash
sequenzy campaigns list
sequenzy campaigns list --status draft --label edm --company comp_123
sequenzy campaigns get camp_123
sequenzy campaigns create "April Launch" --prompt "Announce our new dashboard"
sequenzy campaigns create "April Launch" --subject "We shipped" --label edm --html-file ./campaign.html
sequenzy campaigns create "April Launch" --subject "We shipped" --blocks-file ./campaign-blocks.json
sequenzy campaigns update camp_123 --subject "Updated subject" --label edm
sequenzy campaigns update camp_123 --blocks-file ./campaign-v2-blocks.json
sequenzy campaigns update camp_123 --reply-to support@example.com
sequenzy campaigns update camp_123 --reply-profile reply_123
sequenzy campaigns schedule camp_123 --at "2026-06-01T14:00:00Z"
sequenzy campaigns schedule camp_123 --at "2026-06-01T14:00:00Z" --target-lists-json '{"type":"all"}'
sequenzy campaigns test camp_123 --to you@example.com
sequenzy campaigns cancel camp_123
sequenzy campaigns pause camp_123
sequenzy campaigns resume camp_123 --spread-over-hours 6
sequenzy campaigns delete camp_123 --yes
sequenzy campaigns duplicate camp_123 --mode ab_test
sequenzy campaigns duplicate camp_123 --mode variant --variant-id var_b
```

Behavior:

- `campaigns list`: `GET /api/v1/campaigns`, optionally with `?status=...` and `?label=...`
- `campaigns get`: `GET /api/v1/campaigns/:id`
- `campaigns create`: `POST /api/v1/campaigns`
- `campaigns update`: `PUT /api/v1/campaigns/:id`
- `campaigns schedule`: `POST /api/v1/campaigns/:id/schedule`
- `campaigns test`: `POST /api/v1/campaigns/:id/test`
- `campaigns cancel`: `POST /api/v1/campaigns/:id/cancel`
- `campaigns pause`: `POST /api/v1/campaigns/:id/pause`
- `campaigns resume`: `POST /api/v1/campaigns/:id/resume`
- `campaigns delete`: `DELETE /api/v1/campaigns/:id`
- `campaigns duplicate`: `POST /api/v1/campaigns/:id/duplicate`
- dashboard-aware responses include `url`, campaign review `previewUrl`, and `appUrls` when the company can be resolved

Caveats:

- list accepts `--status` and `--label <labels...>` filters
- create supports `name`, optional `subject` when `--prompt` is used, `html`, `blocks`, `--prompt`, `--style`, `--tone`, and labels with `--label <labels...>`
- update supports `name`, `subject`, `html`, `blocks`, replacement labels with `--label <labels...>`, `--reply-to`, and `--reply-profile`
- schedule requires `--at <datetime>` with a future ISO timestamp and a verified sending domain
- schedule can pass targeting with `--target-lists-json` or `--target-lists-file`; omit it to reuse saved targeting or default to all active subscribers
- `--spread-over-hours` accepts integers from 1 to 72 and takes precedence over send-time optimization
- `--prompt` generates draft campaign content through `POST /api/v1/generate/email`; do not combine it with HTML or block flags
- `--blocks-json` and `--blocks-file` pass Sequenzy block arrays through directly
- conditional email content is only available through block JSON, using block-level `condition` rules
- `--reply-to` resolves an existing reply profile by email and `--reply-profile` sets it directly by ID
- `--reply-to` and `--reply-profile` are mutually exclusive
- `campaigns get` now includes saved reply-to details when the campaign has a reply profile
- only draft campaigns can be updated through this API path
- there is no CLI command for immediate send; schedule with a near-future `--at` timestamp instead
- `cancel` works from scheduled, sending, paused, waiting_approval, and rejected statuses; it shows no confirmation prompt so a bad send can be stopped fast
- `pause` only works on a campaign in sending status; `resume` only works on a paused campaign
- `resume --spread-over-hours` accepts integers from 1 to 72 to spread the remaining delivery
- `delete` is blocked while the campaign is sending, scheduled, or paused; cancel it first
- `duplicate --mode campaign` copies the campaign email, `--mode ab_test` also copies the A/B test with all variants, and `--mode variant` (requires `--variant-id`) copies one variant's content as a plain campaign; the copy is always a new draft
- in the current backend checkout, `campaigns test` returns a success message path rather than a confirmed email send

MCP parity:

- `list_templates` and `list_campaigns` accept `label`
- `create_template`, `update_template`, `create_campaign`, and `update_campaign` accept `labels`
- `update_campaign` accepts `name`, `subject`, `html`, `blocks`, `labels`, `replyTo`, and `replyProfileId`
- `schedule_campaign` accepts `campaignId`, `scheduledAt`, optional `targetLists`, `sendTimeOptimization`, and `spreadOverHours`
- `cancel_campaign`, `pause_campaign`, `resume_campaign` (optional `spreadOverHours`), `delete_campaign`, and `duplicate_campaign` (optional `mode` and `variantId`) mirror the lifecycle commands
- `replyTo` and `replyProfileId` are mutually exclusive
- MCP rejects calls that omit all update fields before hitting the API
- MCP rejects unsupported extra update fields before hitting the API

## Sequences

```bash
sequenzy sequences list
sequenzy sequences get seq_123
sequenzy sequences create onboarding --trigger event_received --event-name signup.completed --goal "Guide new users to activation" --email-count 4
sequenzy sequences create onboarding --trigger contact_added --list-id list_123 --steps-file ./steps.json
sequenzy sequences create winback --trigger tag_added --tag-name cancelled --steps-file ./discount-steps.json
sequenzy sequences update seq_123 --steps-file ./sequence-updates.json
sequenzy sequences update seq_123 --branch-file ./branch.json
sequenzy sequences enable seq_123
sequenzy sequences disable seq_123
sequenzy sequences delete seq_123
sequenzy sequences enroll seq_123 --email one@example.com two@example.com
sequenzy sequences enroll seq_123 --emails-file ./vips.csv
sequenzy sequences enroll seq_123 --email one@example.com --target-node-id node_email_2
sequenzy sequences cancel-enrollments seq_123 --subscriber-id sub_123 --reason "Converted"
sequenzy sequences cancel-enrollments seq_123 --field-path order.id --field-values ord_123,ord_456
sequenzy sequences cancel-enrollments seq_123 --field-values price_123 --apply
```

Behavior:

- `sequences list`: `GET /api/v1/sequences`
- `sequences get`: `GET /api/v1/sequences/:id`
- `sequences create`: `POST /api/v1/sequences`
- `sequences update`: `PUT /api/v1/sequences/:id`
- `sequences enable`: `POST /api/v1/sequences/:id/enable`
- `sequences disable`: `POST /api/v1/sequences/:id/disable`
- `sequences delete`: `DELETE /api/v1/sequences/:id`
- `sequences enroll`: `POST /api/v1/sequences/:id/enroll`
- `sequences cancel-enrollments`: `POST /api/v1/sequences/:id/enrollments/cancel`
- dashboard-aware responses include `url` on sequence records and `appUrls` on the top-level JSON when the company can be resolved

Caveats:

- CLI sequence creation supports either AI `--goal` mode or explicit `--steps-json` / `--steps-file` mode
- explicit create steps can include `{ "type": "create_discount" }`; emails after that action can reference `{{discount.code}}`, `{{discount.percentOff}}`, and related `discount.*` merge tags
- discount action sequences require a connected Stripe integration before activation
- `--email-count` is only meaningful with `--goal`
- `--email-count` accepts 1 to 10 generated emails
- trigger-specific options depend on `--trigger`
- updates accept either step payloads or email payloads via `--steps-*` or `--emails-*`
- branch insertion uses `--branch-json` or `--branch-file` with condition types `has_tag`, `in_list`, `in_segment`, `event_received`, `link_clicked`, and `field_*`
- branch condition fields are `tagId`/`tagName`, `listId`, `segmentId`/`segmentName`, `eventName`, `linkUrl`, `activityScope`, or `fieldName`/`fieldValue`; omit `linkUrl` to match any clicked link
- for `event_received` and `link_clicked`, set `activityScope` to `this_sequence`, `previous_email`, or `ever`; omitting it checks the contact's full history
- `enroll` takes exactly one email source: repeated `--email`, `--emails-json`, or `--emails-file`, with the same file formats as `lists add-subscribers` and the same 500-email batching
- `enroll` only enrolls active subscribers; unknown emails are reported as `notFound`, and inactive or already-enrolled subscribers count as `skipped`
- `enroll` requires the sequence to be accepting entrants (enabled and not paused for enrollment)
- `enroll` starts subscribers at the first step after the trigger unless `--target-node-id` points at a specific non-trigger node; the result reports `enrolled`, `skipped`, `notFound`, `targetNodeId`, and `scheduledFor`
- MCP uses `enroll_subscribers_in_sequence` with `emails` (max 500 per call) and optional `targetNodeId`
- `cancel-enrollments` requires a sequence ID and exactly one target: `--subscriber-id` or `--field-values`
- `--field-values` matches active/waiting enrollments by the stored entry event property at `--field-path`, or the sequence's configured `enrollmentFieldPath` when `--field-path` is omitted
- CLI cancellation is a dry run unless `--apply` is passed; use dry runs for field-value/bulk checks before mutating enrollments
- MCP uses `cancel_sequence_enrollments` with the same target rule; set `dryRun: false` to apply field-value cancellation

## A/B Tests

```bash
sequenzy ab-tests list
sequenzy ab-tests list --sequence seq_123
sequenzy ab-tests get ab_123
sequenzy ab-tests stats ab_123 --period 7d
sequenzy ab-tests stats ab_123 --start "2026-05-01T00:00:00Z" --end "2026-05-31T00:00:00Z"
sequenzy ab-tests restart ab_123 --source-variant var_b --test-type content --variant-count 3
sequenzy ab-tests update-variant ab_123 var_b --subject "New subject"
sequenzy ab-tests update-variant ab_123 var_b --blocks-file ./variant-b.json
sequenzy ab-tests create camp_123 --test-percentage 30 --duration-minutes 120 --winner-criteria click_rate
sequenzy ab-tests create camp_123 --variants-json '[{"subject":"Alternative subject"}]'
sequenzy ab-tests add-variant ab_123 --subject "Alternative subject" --blocks-file ./variant.json
sequenzy ab-tests delete-variant ab_123 var_b --yes
sequenzy ab-tests delete ab_123 --yes
```

Behavior:

- `ab-tests list`: `GET /api/v1/ab-tests`, optionally with `?sequenceId=...` via `--sequence`
- `ab-tests get`: `GET /api/v1/ab-tests/:id`
- `ab-tests stats`: `GET /api/v1/ab-tests/:id/stats`
- `ab-tests restart`: `POST /api/v1/ab-tests/:id/restart`
- `ab-tests update-variant`: `PATCH /api/v1/ab-tests/:id/variants/:variantId`
- `ab-tests create`: `POST /api/v1/ab-tests`
- `ab-tests add-variant`: `POST /api/v1/ab-tests/:id/variants`
- `ab-tests delete-variant`: `DELETE /api/v1/ab-tests/:id/variants/:variantId`
- `ab-tests delete`: `DELETE /api/v1/ab-tests/:id`

Caveats:

- run `ab-tests get` first to discover variant IDs before targeting a variant
- `stats` uses `--period` (`1h`, `24h`, `7d`, `30d`, `90d`) or both `--start` and `--end`; custom ranges max at 90 days
- `restart` only applies to sequence A/B tests with a selected winner; options are `--source-variant`, `--test-type subject|content`, `--winner-threshold` (10-1000), and `--variant-count` (2-4 including control)
- `update-variant` accepts `--subject`, `--preview-text`, and either HTML or blocks flags, not both; only draft A/B tests can be edited
- `create` targets a campaign: the campaign must be in draft or rejected status and must not already have an A/B test
- `create` builds variant A automatically as the control from the campaign's email; extra variants from `--variants-json`/`--variants-file` use `{subject, previewText?, blocks?}` objects
- `create` accepts `--name`, `--test-percentage` (5-50, default 20), `--duration-minutes` (15-1440, default 240), and `--winner-criteria open_rate|click_rate` (default open_rate)
- `add-variant` requires `--subject` and only works while the test is in draft status
- `delete-variant` cannot remove variant A (the protected control) and must leave at least 2 variants; a test holds at most 5 variants
- `delete` is blocked for running tests, and the linked campaign must be draft or rejected
- `create`, `add-variant`, `delete-variant`, and `delete` support campaign A/B tests only
- MCP parity: `list_ab_tests`, `get_ab_test`, `get_ab_test_stats`, `restart_ab_test`, `update_ab_test_variant`, `create_ab_test`, `add_ab_test_variant`, `delete_ab_test_variant`, and `delete_ab_test`

## AI Generation

```bash
sequenzy generate email "Welcome a new user to our analytics product"
sequenzy generate email "Product launch announcement" --style branded --tone friendly
sequenzy generate sequence "Onboard a new workspace admin" --count 4 --days 14
sequenzy generate subjects "April product launch" --count 8
```

Behavior:

- `generate email`: `POST /api/v1/generate/email`
- `generate sequence`: `POST /api/v1/generate/sequence`
- `generate subjects`: `POST /api/v1/generate/subjects`
- `--json` returns the raw API response for agent/tool parsing

Caveats:

- generated content is draft content and should be reviewed before sending
- `generate sequence --count` accepts 1 to 10 emails
- `generate email` supports optional `--style` and `--tone`

## Team

```bash
sequenzy team list
sequenzy team invite teammate@example.com --role admin
sequenzy team invite finance@example.com --role viewer --billing-access
sequenzy team cancel-invitation inv_123 --yes
```

Behavior:

- `team list`: `GET /api/v1/team`; returns the owner, members, and pending or expired invitations
- `team invite`: `POST /api/v1/team/invitations` with `{ email, role, canManageBilling? }`
- `team cancel-invitation`: `DELETE /api/v1/team/invitations/:invitationId`

Caveats:

- `--role` must be `admin` or `viewer`
- inviting and cancelling invitations requires owner or admin access; `--billing-access` can only be granted by the company owner
- existing Sequenzy users are added to the team immediately; new emails receive an invitation that expires after 14 days
- run `team list` first to find invitation IDs before cancelling
- `cancel-invitation` prompts for confirmation; pass `--yes` to skip
- MCP parity: `list_team_members`, `invite_team_member`, and `cancel_team_invitation`

## Inbox

```bash
sequenzy inbox list --status open --unread
sequenzy inbox list --search "refund" --page 2 --limit 50
sequenzy inbox get conv_123
sequenzy inbox reply conv_123 --text "Thanks for reaching out!"
sequenzy inbox reply conv_123 --html-file ./reply.html --subject "Re: your question"
sequenzy inbox reply conv_123 --text "Customer asked for a refund" --note
sequenzy inbox close conv_123
sequenzy inbox reopen conv_123
sequenzy inbox mark-read conv_123
```

Behavior:

- `inbox list`: `GET /api/v1/conversations` with optional `status` (`open`, `closed`, `all`), `search`, `unread`, `page`, and `limit` (1-100, default 20) query parameters
- `inbox get`: `GET /api/v1/conversations/:conversationId`; returns the conversation with its full message history
- `inbox reply`: `POST /api/v1/conversations/:conversationId/messages`
- `inbox close` and `inbox reopen`: `POST /api/v1/conversations/:conversationId/status` with `{ status: "closed" | "open" }`
- `inbox mark-read`: `POST /api/v1/conversations/:conversationId/read`; reports how many messages were marked read

Caveats:

- the inbox collects subscriber replies to campaigns, sequences, and transactional email
- `reply` requires a body from `--text` and/or `--html-file`
- `--note` adds an internal note instead of emailing the subscriber
- outbound replies are sent asynchronously by a worker, so the message starts in `pending` delivery status; they also reopen closed conversations
- MCP parity: `list_conversations`, `get_conversation`, `reply_to_conversation`, `update_conversation_status`, and `mark_conversation_read`

## Webhooks

```bash
sequenzy webhooks list
sequenzy webhooks create --name CI --url https://example.com/hook --event email.bounced subscriber.unsubscribed
sequenzy webhooks create --name "All events" --url https://example.com/hook
sequenzy webhooks update wh_123 --url https://example.com/new-hook
sequenzy webhooks update wh_123 --event email.bounced email.complained
sequenzy webhooks update wh_123 --disable
sequenzy webhooks delete wh_123 --yes
sequenzy webhooks test wh_123
sequenzy webhooks deliveries wh_123 --limit 50
sequenzy webhooks replay wh_123 del_456
```

Behavior:

- `webhooks list`: `GET /api/v1/webhooks`
- `webhooks create`: `POST /api/v1/webhooks` with `{ name, url, events? }`
- `webhooks update`: `PATCH /api/v1/webhooks/:id` with at least one of `--name`, `--url`, `--event`, `--enable`, or `--disable`
- `webhooks delete`: `DELETE /api/v1/webhooks/:id`; this permanently deletes the endpoint and its delivery history
- `webhooks test`: `POST /api/v1/webhooks/:id/test`
- `webhooks deliveries`: `GET /api/v1/webhooks/:id/deliveries`, optionally with `?limit=` (1-100)
- `webhooks replay`: `POST /api/v1/webhooks/:id/deliveries/:deliveryId/replay`

Caveats:

- valid event types are `email.sent`, `email.delivered`, `email.delivery_delayed`, `email.bounced`, `email.complained`, `email.opened`, `email.clicked`, `email.unsubscribed`, `subscriber.invalid`, `subscriber.updated`, `subscriber.unsubscribed`, `sequence.finished`, and `sequence.failed`; omit `--event` to use the default set
- `create` returns a signing secret exactly once and it cannot be retrieved later; handle it as sensitive output. Do not paste credential material into chat, logs, tickets, or public transcripts. Save it only to a user-approved secure destination such as a password manager, secret store, encrypted file, or local `.env` file outside version control, then report the storage location and a short fingerprint.
- `--enable` and `--disable` are mutually exclusive; changing the URL or re-enabling resets the failure circuit breaker
- the webhook must be enabled to receive a test event
- run `webhooks deliveries <id>` first to find delivery IDs before replaying
- `delete` prompts for confirmation; pass `--yes` to skip
- MCP parity: `list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `test_webhook`, `list_webhook_deliveries`, and `replay_webhook_delivery`

## API Keys

```bash
sequenzy api-keys create
sequenzy api-keys create --name "CI deploy key" --company comp_123
```

Behavior:

- sends `POST /api/v1/api-keys`
- body shape is `{ name }`

Caveat:

- newly created API credential material is returned only at creation time; handle it as sensitive output. Do not paste it into chat, logs, tickets, or public transcripts. Save it only to a user-approved secure destination such as a password manager, secret store, encrypted file, or local `.env` file outside version control, then report the storage location and a short fingerprint.

## Websites

```bash
sequenzy websites list --company comp_123
sequenzy websites add example.com --company comp_123
sequenzy websites check example.com --company comp_123
sequenzy websites guide --framework nextjs --use-case transactional
```

Behavior:

- `websites list`: `GET /api/v1/websites`
- `websites add`: `POST /api/v1/websites`
- `websites check`: `GET /api/v1/websites/:domain`
- `websites guide`: `POST /api/v1/integration-guide`

## Commands To Treat As Unsupported

Treat these requested workflows as unsupported in the CLI even though related nouns exist:

- campaign immediate send; there is no "send now" command, so schedule with a near-future `--at` timestamp instead

## Operational Caveats

- prefer `SEQUENZY_API_KEY` for automation instead of interactive login
- use `--json` when another tool or agent needs structured output; dashboard-aware commands add `url`/`appUrls` fields when possible
- destructive commands (`delete`, `delete-variant`, `cancel-invitation`, and similar) prompt for confirmation; pass `--yes` (or `-y`) to skip, and note that `--yes` is required when stdin is not a TTY, which covers most agent and CI runs
- `campaigns cancel` deliberately skips the confirmation prompt so a bad send can be stopped fast
- `webhooks create` returns a one-time signing secret; handle it as sensitive output because it cannot be retrieved later. Do not paste credential material into chat, logs, tickets, or public transcripts. Save it only to a user-approved secure destination such as a password manager, secret store, encrypted file, or local `.env` file outside version control, then report the storage location and a short fingerprint.
- when the user asks for a workflow outside the current CLI surface, say so directly and choose between dashboard or direct API use instead of inventing commands
