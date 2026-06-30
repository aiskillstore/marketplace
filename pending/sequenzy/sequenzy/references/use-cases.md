# Use Cases

## Pick The Right Flow

### "Log into Sequenzy on this machine"

Use:

```bash
sequenzy login
```

Then verify:

```bash
sequenzy whoami
```

Prefer `SEQUENZY_API_KEY` instead when the task is fully non-interactive or running in CI.

## "Check whether I am authenticated"

Use:

```bash
sequenzy whoami
```

Interpretation:

- success means a local API key is available
- failure means the agent should ask for login or a `SEQUENZY_API_KEY`

Remember that this is local-state validation, not a fresh server-side account lookup.

## "Show me account or company info"

Use:

```bash
sequenzy account
sequenzy companies list
sequenzy companies get comp_123
sequenzy urls --company comp_123
```

Choose:

- `account` for user ID, current company, and accessible companies
- `companies list` for a compact list with localization info
- `companies get` when the user already has a company ID
- `urls` when the user needs a dashboard/settings link

## "Open, review, or edit something I just created"

Prefer the `url` or `appUrls` fields returned by recent CLI/MCP calls. If you need to generate links from IDs:

```bash
sequenzy urls --company comp_123 --sequence seq_123
sequenzy urls --company comp_123 --campaign camp_123
sequenzy urls --company comp_123 --settings-tab integrations
```

MCP equivalent: call `get_app_urls` with:

```json
{
  "companyId": "comp_123",
  "sequenceId": "seq_123",
  "settingsTab": "integrations"
}
```

URL patterns:

- sequence editor: `/dashboard/company/{companyId}/sequences/{sequenceId}`
- campaign editor: `/dashboard/company/{companyId}/campaign/{campaignId}`
- template/email editor: `/dashboard/company/{companyId}/emails/{emailId}`
- settings: `/dashboard/company/{companyId}/settings`
- settings tab: `/dashboard/company/{companyId}/settings?tab={tab}`

After generating a sequence or campaign, give the user the relevant review/edit URL instead of only returning the ID.

## "Show me delivery performance"

Use:

```bash
sequenzy stats
sequenzy stats --period 30d
sequenzy stats --campaign camp_123
sequenzy stats --sequence seq_123
```

Choose:

- plain `stats` for account-level overview
- `--campaign` when the user gives a campaign ID
- `--sequence` when the user gives a sequence ID

Ask for the missing ID instead of guessing.

## "Add or update a subscriber"

What works today:

```bash
sequenzy subscribers add user@example.com --tag premium --attr name=John
sequenzy subscribers add user@example.com --tag premium --tag beta --company comp_123
sequenzy subscribers get user@example.com
sequenzy subscribers list --list "Master List" --json
```

Guidance:

- use `add` for single-recipient creation or upsert
- use repeated `--attr key=value` pairs for metadata
- repeated `--tag` values are supported
- use `--company` when the API key can access multiple companies
- use `subscribers get` when you need the full profile, list memberships, sequence enrollments, email stats, or recent activity
- use `subscribers list --list <id-or-exact-name> --json` to export subscribers from one list; omit `--limit` to fetch every page

What does not work well today:

- advanced subscriber workflows across many records

For bulk list population, do not loop over `subscribers add`. Use:

```bash
sequenzy lists add-subscribers list_123 --emails-file ./batch-001.csv
sequenzy lists import list_123 --emails-file ./batch-001.csv
```

Guidance:

- `lists import` is an alias for `lists add-subscribers`
- accepted input formats are repeated `--email`, `--emails-json`, or `--emails-file`
- files may be newline-separated, CSV with an email column, a JSON email array, or a JSON object with `emails` or `subscribers`
- CSV headers named `email`, `e-mail`, `email address`, or `mail` are detected; otherwise the first column is used
- the CLI splits files into API-safe batches of up to 500 emails
- use this path instead of one API call per subscriber

## "Remove a subscriber"

Use:

```bash
sequenzy subscribers list --tag vip
sequenzy subscribers get user@example.com
sequenzy subscribers remove user@example.com
```

Use `--hard` only when the task explicitly requires permanent deletion:

```bash
sequenzy subscribers remove user@example.com --hard
```

Notes:

- plain `remove` performs a full unsubscribe workflow rather than a hard delete
- use `--company` when operating with a personal API key across multiple companies

## "Send one transactional email"

Template flow:

```bash
sequenzy send user@example.com --template tmpl_123 --var name=John
```

Raw HTML flow:

```bash
sequenzy send user@example.com --subject "Status update" --html-file ./email.html --var orderId=123
```

Checklist:

1. Confirm recipient email.
2. Confirm template ID or HTML source.
3. Confirm subject when sending raw HTML.
4. Confirm merge variables as `key=value`.

This command is for one-off transactional send behavior, not bulk campaign sends.

## "Create a list, tag view, or saved segment"

What works today:

```bash
sequenzy lists create Newsletter --description "Public newsletter list"
sequenzy lists update list_123 --name "Weekly Newsletter" --private
sequenzy lists remove-subscribers list_123 --emails-file ./churned.csv
sequenzy lists delete list_123 --yes
sequenzy tags list
sequenzy tags create vip --color purple
sequenzy tags update tag_123 --color red
sequenzy tags delete tag_123 --yes
sequenzy segments list
sequenzy segments count seg_123
sequenzy segments create --name "Bought Pro" --stripe-product prod_pro
sequenzy segments create --name "VIP or Churn Risk" --match any --filter-json '[{"field":"tag","operator":"contains","value":"vip"},{"field":"emailOpened","operator":"is_not","value":"30d"}]'
sequenzy segments create --name "Active non-paying" --filter-json '{"kind":"group","id":"root","joinOperator":"and","children":[{"kind":"filter","id":"f1","field":"attribute","operator":"gte","value":"last_login_days_ago:0"},{"kind":"group","id":"g1","joinOperator":"or","children":[{"kind":"filter","id":"f2","field":"attribute","operator":"is_empty","value":"plan_end"},{"kind":"filter","id":"f3","field":"attribute","operator":"lt","value":"plan_end:2026-04-21"}]}]}'
sequenzy segments update seg_123 --name "Churn Risk" --join-operator or
sequenzy segments delete seg_123 --yes
```

For Stripe purchase thresholds:

```bash
sequenzy segments create --name "3+ Pro Payments" --stripe-product prod_pro --purchase-operator at-least --payments 3
```

Guidance:

- bare `sequenzy tags` still lists tag definitions; `tags create`, `tags update`, and `tags delete` mutate them
- tag names are normalized to lowercase with dashes, system tags cannot be changed or deleted, and tags used by sequences cannot be deleted
- deleting a tag removes it from every subscriber, so confirm intent before running `tags delete`
- `lists update` changes name, description, or visibility; `lists remove-subscribers` only removes memberships, while `lists delete` removes the whole list and all of its memberships (subscribers themselves are kept)
- `segments update` replaces the filter set; run `segments count` afterwards to confirm the new size
- use Stripe product IDs, not product names
- use `--filter-json` when the user needs a non-Stripe, mixed, nested, custom event, or saved-segment payload
- use `--match any` when the segment should match any top-level filter instead of all filters
- `segments count` is the quickest way to preview impact before using a segment in a campaign

For MCP-driven workflows, `create_segment` supports the same legacy filter array with `filterJoinOperator: "or"` for match-any segments:

```json
{
  "filterJoinOperator": "or",
  "filters": [
    {
      "id": "filter-1",
      "field": "stripeProduct",
      "operator": "at_least",
      "value": "prod_pro:3"
    }
  ]
}
```

For nested AND/OR logic, send a `root` instead of `filters`. Event filters use `field: "event"` and values like `saas.purchase:30d` or `saas.purchase:5:30d`; segment-of-segment filters use `field: "segment"` with the referenced segment id as `value`.

```json
{
  "root": {
    "kind": "group",
    "id": "root",
    "joinOperator": "and",
    "children": [
      {
        "kind": "filter",
        "id": "filter-1",
        "field": "event",
        "operator": "at_least",
        "value": "saas.purchase:2:30d"
      },
      {
        "kind": "filter",
        "id": "filter-2",
        "field": "segment",
        "operator": "is_not",
        "value": "seg_churned"
      }
    ]
  }
}
```

## "Create or manage a template"

What works today:

```bash
sequenzy templates list
sequenzy templates list --label edm
sequenzy templates get tmpl_123
sequenzy templates create welcome --subject "Welcome" --label edm --html-file ./welcome.html
sequenzy templates create welcome --subject "Welcome" --blocks-file ./welcome-blocks.json
sequenzy templates update tmpl_123 --subject "Updated" --label edm --html-file ./welcome-v2.html
sequenzy templates update tmpl_123 --blocks-file ./welcome-v2-blocks.json
```

Guidance:

- use block JSON when the user needs conditional content or an exact editor-compatible structure
- use HTML input for simpler one-off content; this API path stores raw HTML as a single text block
- use `--label` on `list` to filter by label, and on `create` or `update` to assign replacement labels
- a conditional block uses a block-level `condition` object with merge-tag variable names and no `{{ }}` braces
- use `get` before `update` or `delete` when the user is uncertain about the target ID
- warn that delete can fail when the template is still referenced by a campaign or sequence

## "Create or manage a campaign"

What works today:

```bash
sequenzy campaigns list --status draft --label edm
sequenzy campaigns get camp_123
sequenzy campaigns create "April Launch" --prompt "Announce our new dashboard"
sequenzy campaigns create "April Launch" --subject "We shipped" --label edm --html-file ./campaign.html
sequenzy campaigns create "April Launch" --subject "We shipped" --blocks-file ./campaign-blocks.json
sequenzy campaigns update camp_123 --subject "Updated subject" --label edm
sequenzy campaigns update camp_123 --blocks-file ./campaign-v2-blocks.json
sequenzy campaigns update camp_123 --reply-to support@example.com
sequenzy campaigns update camp_123 --reply-profile reply_123
sequenzy campaigns schedule camp_123 --at "2026-06-01T14:00:00Z"
sequenzy campaigns test camp_123 --to you@example.com
sequenzy campaigns duplicate camp_123
sequenzy campaigns delete camp_123 --yes
```

Guidance:

- the CLI handles draft creation, draft updates, inspection, scheduling, test requests, duplication, deletion, and lifecycle control (cancel, pause, resume)
- create, get, update, schedule, list, and test outputs include dashboard URLs when the company can be resolved; campaign outputs include a review `previewUrl`
- use `--prompt` for AI-generated draft content; do not combine it with HTML or block flags
- use `--label` on `list` to filter by campaign label, and on `create` or `update` to assign replacement labels
- use block JSON when the user needs conditional content or an exact editor-compatible structure
- use `--reply-to` when the user knows the reply profile email and it already exists for the company
- use `--reply-profile` when the user already has the reply profile ID
- do not pass `--reply-to` and `--reply-profile` together
- use `campaigns get` after an update when you want to confirm the saved reply-to details
- use `campaigns schedule --at <future ISO datetime>` when the user asks to schedule a campaign; it requires a verified sending domain
- use `--target-lists-json` or `--target-lists-file` only when the user explicitly needs new targeting at schedule time
- there is no CLI command for immediately sending a campaign; schedule with a near-future `--at` timestamp instead
- use `campaigns duplicate` to clone a campaign as a new draft; `--mode ab_test` also copies its A/B test and `--mode variant --variant-id <id>` copies one variant's content
- `campaigns delete` only works once the campaign is not sending, scheduled, or paused; cancel it first
- in the current backend checkout, `campaigns test` returns a success message path rather than confirmed delivery

For MCP-driven campaign updates, `update_campaign` supports labels and the same reply-to behavior:

```json
{
  "campaignId": "camp_123",
  "labels": ["edm"],
  "replyTo": "support@example.com"
}
```

For MCP-driven scheduling, call `schedule_campaign`:

```json
{
  "campaignId": "camp_123",
  "scheduledAt": "2026-06-01T14:00:00Z",
  "targetLists": { "type": "all" }
}
```

Use `replyProfileId` instead when the caller already has the reply profile ID, and never send both fields together.

Preferred fallback for unsupported campaign workflows:

- use the dashboard
- use direct API calls only if the task explicitly allows it and the relevant API is available

## "Stop a campaign that is scheduled or already sending"

Use:

```bash
sequenzy campaigns get camp_123
sequenzy campaigns cancel camp_123
sequenzy campaigns pause camp_123
sequenzy campaigns resume camp_123 --spread-over-hours 6
```

Decide between cancel, pause, and resume:

- use `cancel` when the send should not continue at all; it is permanent and works from scheduled, sending, paused, waiting-approval, and rejected statuses
- use `pause` when the user wants to stop a send temporarily and may continue it; it only works while the campaign is in sending status
- use `resume` to continue a paused campaign, optionally spreading the remaining delivery with `--spread-over-hours` (1-72)
- `cancel` needs no `--yes` and shows no confirmation prompt, so it is the fastest way to stop a bad send; run it first and ask questions after when the user reports a mistake
- check `campaigns get` first when you are unsure of the current status; the API rejects transitions from the wrong status

MCP equivalents are `cancel_campaign`, `pause_campaign`, and `resume_campaign` (optional `spreadOverHours`).

## "Run an A/B test on a campaign"

Use:

```bash
sequenzy campaigns get camp_123
sequenzy ab-tests create camp_123 --test-percentage 20 --duration-minutes 240 --winner-criteria open_rate
sequenzy ab-tests add-variant ab_123 --subject "Alternative subject"
sequenzy ab-tests get ab_123
sequenzy ab-tests update-variant ab_123 var_b --subject "New subject"
sequenzy ab-tests delete-variant ab_123 var_c --yes
sequenzy ab-tests stats ab_123 --period 7d
```

Guidance:

- the campaign must be in draft or rejected status and must not already have an A/B test
- variant A is created automatically from the campaign email and is the protected control; it cannot be deleted
- a test holds 2 to 5 variants; structure changes (add, edit, delete variants) are only allowed while the test is in draft status
- `--test-percentage` (5-50), `--duration-minutes` (15-1440), and `--winner-criteria open_rate|click_rate` control how the winner is picked once the campaign is scheduled
- use `ab-tests get` to find variant IDs, `ab-tests stats` to compare results after sending, and `ab-tests delete` (draft or finished tests only) to remove a test
- `campaigns duplicate camp_123 --mode ab_test` clones a campaign together with its A/B test
- MCP equivalents are `create_ab_test`, `add_ab_test_variant`, `update_ab_test_variant`, `delete_ab_test_variant`, `delete_ab_test`, `get_ab_test`, and `get_ab_test_stats`

## "Create or manage a sequence"

What works today:

```bash
sequenzy sequences list
sequenzy sequences get seq_123
sequenzy sequences create onboarding --trigger event_received --event-name signup.completed --goal "Guide new users to activation" --email-count 4
sequenzy sequences create onboarding --trigger contact_added --list-id list_123 --steps-file ./steps.json
sequenzy sequences create winback --trigger tag_added --tag-name cancelled --steps-file ./discount-steps.json
sequenzy sequences update seq_123 --steps-file ./sequence-updates.json
sequenzy sequences enable seq_123
sequenzy sequences disable seq_123
sequenzy sequences cancel-enrollments seq_123 --subscriber-id sub_123
sequenzy sequences cancel-enrollments seq_123 --field-path order.id --field-values ord_123,ord_456
sequenzy sequences cancel-enrollments seq_123 --field-values price_123 --apply
```

Minimal `steps.json` shape:

```json
[
  {
    "subject": "Welcome to Acme",
    "html": "<p>Hi there</p>",
    "delay": { "days": 0 }
  },
  {
    "subject": "Day 3 follow-up",
    "html": "<p>Here is the next step</p>",
    "delay": { "days": 3 }
  }
]
```

Discount step shape:

```json
[
  {
    "type": "create_discount",
    "label": "Create win-back discount",
    "discountType": "percent",
    "percentOff": 20,
    "duration": "once",
    "appliesToAllPlans": true,
    "maxRedemptions": 1,
    "codePrefix": "WINBACK"
  },
  {
    "subject": "Come back with {{discount.code}}",
    "html": "<p>Use {{discount.code}} for {{discount.percentOff}}% off.</p>",
    "delay": { "days": 1 }
  }
]
```

Branch insertion shape for "clicked invite, otherwise remind":

```json
{
  "afterNodeId": "node_email",
  "branches": [
    {
      "conditionType": "link_clicked",
      "linkUrl": "project-invites",
      "activityScope": "previous_email",
      "steps": [
        {
          "subject": "Project invite accepted",
          "html": "<p>Here is your next project step.</p>"
        }
      ]
    }
  ],
  "elseSteps": [
    {
      "subject": "Reminder: accept your invite",
      "html": "<p>Please accept your project invite.</p>"
    }
  ]
}
```

Guidance:

- CLI sequence creation supports either AI `--goal` mode or explicit step files
- create, get, update, and list outputs include dashboard URLs when the company can be resolved
- choose the correct trigger options for `--trigger`
- use `--goal` when you want AI-generated drafts, or `--steps-file` when you already know the exact step content
- discount action steps require Stripe to be connected before activation
- use either `--steps-file` or `--emails-file` for update
- use `--branch-file` for if/else insertion; branch conditions support tag, list, segment, event, clicked-link, and field checks
- for `link_clicked`, set `linkUrl` to part of the target URL or omit it to match any tracked click
- for `event_received` and `link_clicked`, set `activityScope` to `this_sequence`, `previous_email`, or `ever`
- enable/disable are real CLI actions

## "Stop people in a sequence"

Use:

```bash
sequenzy sequences cancel-enrollments seq_123 --subscriber-id sub_123 --reason "Converted"
sequenzy sequences cancel-enrollments seq_123 --field-path order.id --field-values ord_123,ord_456
sequenzy sequences cancel-enrollments seq_123 --field-values price_123 --apply
```

Guidance:

- require the sequence ID; never attempt cross-sequence cancellation from only an event or field value
- use `--subscriber-id` when the caller knows the exact subscriber enrollment to stop
- use `--field-values` when the caller wants to stop all active/waiting enrollments whose stored entry event property matches specific IDs
- include `--field-path` unless the sequence already has the correct `enrollmentFieldPath`
- omit `--apply` for a dry run; pass `--apply` only after reviewing the matched count
- MCP equivalent is `cancel_sequence_enrollments` with exactly one of `subscriberId` or `fieldValues`; set `dryRun: false` to apply a field-value cancellation

## "Enroll existing subscribers into a sequence"

Use:

```bash
sequenzy sequences get seq_123
sequenzy sequences enroll seq_123 --email one@example.com two@example.com
sequenzy sequences enroll seq_123 --emails-file ./vips.csv
sequenzy sequences enroll seq_123 --email one@example.com --target-node-id node_email_2
```

Guidance:

- use `enroll` when subscribers should enter a sequence now instead of waiting for its trigger (for example, back-filling a new onboarding sequence with existing contacts)
- the sequence must be accepting entrants: enabled and not paused for enrollment
- provide exactly one email source: repeated `--email`, `--emails-json`, or `--emails-file`; the CLI batches large inputs into 500-email requests
- only active subscribers are enrolled; the result reports `notFound` for unknown emails and `skipped` for inactive or already-enrolled subscribers, so check those counts instead of assuming everyone entered
- enrollment starts at the first step after the trigger unless `--target-node-id` points at a specific node; use `sequences get` first to find node IDs
- MCP equivalent is `enroll_subscribers_in_sequence` with `emails` and optional `targetNodeId`

## "Create an API key or inspect website/domain setup"

Use:

```bash
sequenzy api-keys create --name "CI deploy key" --company comp_123
sequenzy websites list --company comp_123
sequenzy websites add example.com --company comp_123
sequenzy websites check example.com --company comp_123
sequenzy websites guide --framework nextjs --use-case transactional
```

Guidance:

- save API keys immediately; the raw key is only returned on creation
- use `websites check` when the user needs DNS verification details
- use `websites guide` for integration code snippets rather than inventing framework examples

## "Sell a digital product and deliver the file after purchase"

What works today:

```bash
sequenzy products sync
sequenzy products list --provider stripe
sequenzy products attach-file <product-id> --file ./guide.pdf
```

Then create the delivery sequence on the purchase event:

```bash
sequenzy sequences create ebook-delivery \
  --trigger event_received \
  --event-name saas.purchase \
  --steps-json '[{"type":"email","subject":"Your download is ready","html":"<p>Thanks for your purchase! <a href=\"{{event.download.url}}\">Download {{event.download.name}}</a></p>"}]'
```

Guidance:

- sync first so the Stripe catalog exists locally, then take the internal product ID from `products list`
- `attach-file --file` uploads the file to Sequenzy storage in one step; use `--url` when the file is hosted elsewhere
- the purchase event carries `download.url` and `download.name` only for products that have an attached file; `downloads` contains all files when an order has several products
- per-product filtering (start the sequence only when one specific product is bought) is configured in the dashboard sequence trigger via the "Only for product" picker or a `productIds equals <stripe product id>` property filter; trigger property filters are not currently settable through the CLI or MCP, so say so and link the sequence editor URL
- buyers become subscribers automatically when the Stripe purchase webhook arrives, so delivery works for brand-new customers
- MCP flows use `list_products` + `attach_product_file`, then `create_sequence` with the same event trigger

## "Invite a teammate"

Use:

```bash
sequenzy team list
sequenzy team invite teammate@example.com --role admin
sequenzy team invite finance@example.com --role viewer --billing-access
sequenzy team cancel-invitation inv_123 --yes
```

Guidance:

- `--role` is `admin` (can manage the workspace) or `viewer` (read-only); choose `viewer` unless the user explicitly needs management access
- `--billing-access` can only be granted by the company owner; expect a permission error otherwise
- existing Sequenzy users join the team immediately; new emails receive an invitation that expires after 14 days
- use `team list` to see the owner, members, and pending or expired invitations, and to find invitation IDs before cancelling
- MCP equivalents are `list_team_members`, `invite_team_member`, and `cancel_team_invitation`

## "Triage and reply to inbox conversations"

Use:

```bash
sequenzy inbox list --status open --unread
sequenzy inbox get conv_123
sequenzy inbox reply conv_123 --text "Thanks for reaching out!"
sequenzy inbox reply conv_123 --text "Customer asked for a refund" --note
sequenzy inbox mark-read conv_123
sequenzy inbox close conv_123
```

Guidance:

- triage flow: `inbox list --unread` to find conversations needing attention, `inbox get` to read the full message history, then `inbox reply`, `mark-read`, and `close`
- use `--note` to record internal context (decisions, escalations) without emailing the subscriber
- outbound replies are sent asynchronously by a worker, so report the message as queued rather than delivered; replies also reopen closed conversations
- use `--search` to find conversations by subscriber email, name, or subject, and `--status open|closed|all` plus `--page`/`--limit` for larger inboxes
- MCP equivalents are `list_conversations`, `get_conversation`, `reply_to_conversation`, `update_conversation_status`, and `mark_conversation_read`

## "Manage outbound webhooks"

Use:

```bash
sequenzy webhooks create --name CI --url https://example.com/hook --event email.bounced subscriber.unsubscribed
sequenzy webhooks list
sequenzy webhooks test wh_123
sequenzy webhooks deliveries wh_123 --limit 50
sequenzy webhooks replay wh_123 del_456
sequenzy webhooks update wh_123 --disable
sequenzy webhooks delete wh_123 --yes
```

Guidance:

- `create` prints the signing secret exactly once; surface it to the user immediately and tell them to store it, because it cannot be retrieved later
- pick events from the 13 supported `email.*`, `subscriber.*`, and `sequence.*` types, or omit `--event` for the default set
- debug delivery problems with `test` (fires a test event), `deliveries` (recent attempts with status codes and errors), and `replay` (re-sends one delivery)
- use `update --disable`/`--enable` to toggle an endpoint; re-enabling or changing the URL resets the failure circuit breaker
- `delete` permanently removes the endpoint and its delivery history; use `update --disable` to keep it
- MCP equivalents are `list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `test_webhook`, `list_webhook_deliveries`, and `replay_webhook_delivery`

## "Generate email content with AI"

Use the CLI when the user wants draft copy or structured generated output:

```bash
sequenzy generate email "Welcome email for new SaaS trial users"
sequenzy generate sequence "Onboarding for SaaS trial users" --count 4 --days 14
sequenzy generate subjects "Black Friday sale" --count 5
```

Guidance:

- use `--json` when another agent or tool should parse the result
- generated content is draft content and should be reviewed before sending
- sequence generation accepts at most 10 emails
- use `sequenzy campaigns create "Name" --prompt "..."` when the user wants to create a draft campaign from generated content in one step
