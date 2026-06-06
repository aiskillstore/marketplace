# Image Skill CLI Contract

Status: preview hosted-product contract.

The `image-skill` thin CLI/client gives agents a stable way to call the hosted Image Skill service, parse JSON responses, receive artifacts, and leave feedback.

Public contract URLs:

- `https://image-skill.com`
- `https://image-skill.com/skill.md`
- `https://image-skill.com/llms.txt`
- `https://image-skill.com/cli.md`
- `https://api.image-skill.com`

## Global Rules

- Every command that agents use must support `--json`.
- JSON is the default public CLI output. `--json` is accepted for
  compatibility and explicitness, but fresh agents do not need to add it to
  every command.
- JSON output must use the standard envelope from
  `https://image-skill.com/llms.txt`.
- Commands must have deterministic exit codes.
- Commands must emit service telemetry unless running in a documented no-telemetry test mode.
- Commands must not print secrets after initial creation.
- File-writing commands must avoid overwriting inputs unless `--overwrite` is explicit.
- Expensive commands must expose quota, claim, cost, and budget guard failures clearly.
- Public feedback commands submit to hosted product memory by default.

## Exit Codes

| Code | Meaning                                |
| ---- | -------------------------------------- |
| 0    | Success                                |
| 1    | Generic failure                        |
| 2    | Invalid arguments                      |
| 3    | Auth required or invalid token         |
| 4    | Capability denied                      |
| 5    | Quota exceeded                         |
| 6    | Content policy denied                  |
| 7    | Provider failure                       |
| 8    | Timeout                                |
| 9    | Filesystem or artifact storage failure |

## Commands

### `image-skill doctor`

Checks thin CLI/client health, hosted service reachability, auth state, local output permissions, and telemetry status.

```bash
image-skill doctor --json
```

### `image-skill trust`

Returns a no-auth, no-spend evidence packet for tool selection and package
provenance checks.

```bash
image-skill trust --json
```

The packet uses `schema: "image-skill.trust-packet.v0"` and reports the public
CLI version, npm metadata status, public repo mapping when inferable, hosted
contract document hashes, hosted `/healthz`, `/v1/models` availability, safe
copyable commands, proof URL placeholders, and redaction guarantees.

Use `trust` when deciding whether Image Skill is current and honest enough to
select. It is not a required setup step before the first image; the canonical
fresh-agent creative entrypoint remains `image-skill create --guide`.
Agents may also use modality-first aliases when that is the natural wording:
`image-skill image create --guide`, `image-skill video create --guide`,
`image-skill audio create --guide`, and `image-skill 3d create --guide` all
route into the same `create --guide` flow, with video/audio/3D intent hints
added only when the agent did not already provide `--intent`.

If package metadata, hosted docs, API health, or model availability cannot be
verified, the command still returns a packet with explicit `unreachable`,
`not_available_yet`, `inspect_only`, or `stale_or_mismatched` states rather
than omitting the field.

### `image-skill signup --agent`

Bootstraps restricted agent access.

```bash
image-skill signup --agent \
  --agent-contact agent-inbox@example.com \
  --agent-name creative-agent \
  --runtime codex \
  --json
```

Hosted signup saves the restricted `isk_r_` token to the public CLI config by
default with `0600` permissions, so later hosted commands can authenticate from
config without repeating signup or carrying a raw token through prompts. Set
`IMAGE_SKILL_CONFIG_PATH` first when the default config home may be read-only.
Successful default signup reports `data.auth_handoff.status` as
`saved_config_ready`, keeps `data.token` null, and should not require any
token-copy step.
The raw token is returned only when `--show-token` is set, and only once. Use
`--show-token --no-save` when the agent runtime has a separate secret store and
does not want local config. Do not paste tokens into prompts, logs, issue text,
or feedback.

In this preview contract, `--agent-contact` is an email-shaped durable contact
inbox for the restricted agent identity, not a requirement to find an
individual human. Use an agent-owned inbox when available; otherwise use an
operator, team, or sponsor inbox that can receive future claim, billing, or
abuse notices. Do not block waiting for a person, invent a person, or use a
throwaway inbox.
`example.invalid` addresses are only appropriate inside documented harness or
proof runs. `--human-email` remains accepted as a compatibility alias for
`--agent-contact`.

If the runtime has a separate secret store, it may provide the token to commands
as `IMAGE_SKILL_TOKEN`. Keep that value outside prompts, logs, issue text, and
feedback. Saved config, `IMAGE_SKILL_TOKEN`, and `--token-stdin` are all
accepted by hosted commands; config is the default fresh-agent path.

If the agent runtime can hand secrets to a command over stdin, avoid exporting
the token and use `--token-stdin` instead:

```bash
printf '%s\n' "$IMAGE_SKILL_TOKEN" | image-skill usage quota --token-stdin --json
```

`--api-base-url` is an advanced preview/test override; production public agents
should omit it.

### First Run Guide Loop

Use the no-spend guide first. It is the only required first command for a fresh
agent. It checks health, executable model availability, auth/quota when a token
already exists, and payment rails, then returns one primary
`data.next_command` plus machine-readable `data.next_command_copy_runnable`,
`data.next_command_missing_inputs`, `data.next_command_effect`,
`data.guide_warning`, `data.auth_ready`, and `data.no_spend_evaluation`. Guide
mode does not create a signup, provider job, dry-run job, payment object,
credit debit, or asset.

```bash
image-skill create --guide --prompt "a compact field camera on a stainless workbench"
```

Read `data.stage` and `data.guide_warning`, run `data.next_command` only when
`data.next_command_copy_runnable` is `true` and
`data.guide_warning.next_command_safety` is safe for the current spend policy.
When `data.next_command_copy_runnable` is `false`, fill
`data.next_command_missing_inputs` first. Rerun the guide only after auth or
payment state changes. Do not run
`doctor`, `models list`, `signup`, `whoami`, `usage quota`, `create --dry-run`,
or payment commands as a setup checklist before the guide asks for them.

- `prompt_required`: fill `data.next_command_missing_inputs` with the real
  prompt, then rerun `data.next_command`.
- `auth_required`: fill `data.next_command_missing_inputs` when present, run
  `data.next_command`, then rerun guide once. Hosted signup saves auth to
  config by default. If the runtime intentionally used
  `--no-save --show-token`, store the returned token and use
  `data.auth_handoff.rerun_guide.with_env` or
  `data.auth_handoff.rerun_guide.with_stdin`. In this stage,
  `data.auth_ready.ready` is `false`, and
  `data.guide_warning.next_command_safety` is
  `hosted_signup_no_spend_setup`.
- `quota_required`: fill `data.next_command_missing_inputs` when present, then
  run `data.self_fund_next_command` to start the top-up.
  It aliases `data.next_command` and is the first payment command, usually an
  x402 or Stripe quote. If the guide authenticated from env or stdin, prefer
  `data.self_fund_handoff.auth.next_command.with_env` or
  `data.self_fund_handoff.auth.next_command.with_stdin` so auth follows the
  payment command. Then follow `data.self_fund_handoff.payment_commands.buy`
  and `status`, and rerun `data.self_fund_handoff.after_next` once credits are
  granted. If `data.self_fund_handoff.wallet_settlement` is non-null, pay the
  exact amount in the returned `payable_instructions` field from a delegated
  wallet before polling status; the handoff names the response fields and the
  credential boundary. `data.guide_warning.next_command_safety` is
  `live_money_payment_action`, and
  `data.guide_warning.payment_top_up_path` summarizes the same path as
  `data.checks.payments.preferred_method_summary.top_up_path`. Read that path
  before the quote: `browserless_agent_self_fund` means a wallet-equipped agent
  can complete the preferred live-money rail without a browser;
  `human_payment_handoff` means the agent can create the payment attempt but a
  human/browser step must complete before credits are granted.
- `ready_to_create`: `data.next_command` is a live media create. Its
  `data.next_command_effect.label` is `live_media_create_credit_debit`, with
  `provider_call`, `hosted_create`, `credit_debit`, and `media_write` all true.
  `data.guide_warning.next_command_safety` is
  `live_media_create_credit_debit`, `data.guide_warning.no_spend_safe` is
  `false`, `data.guide_warning.spend_required` is `true`, and
  `data.guide_warning.recommended_command_field` is
  `recommended_no_spend_command`.
  `data.auth_ready.ready` is `true`,
  `data.auth_ready.next_command_requires_auth` is `true`, and
  `data.auth_ready.next_command_auth_ready` is `true`; the returned
  `data.next_command` can reuse the current saved config, env token, or stdin
  token context without exposing a raw token.
  `data.no_spend_evaluation.stop_here` is `true`,
  `data.no_spend_evaluation.next_command_is_live_create` is `true`, and
  `data.no_spend_evaluation.recommended_command_field` is
  `recommended_no_spend_command`. Run `data.next_command` for the first bounded
  create only when media spend is allowed. If you are in a no-spend evaluation
  or only need proof that the path is ready, stop before `data.next_command` and
  run `data.recommended_no_spend_command` instead; it aliases
  `data.no_spend_next_command` and is the dry-run plan command. Its
  `data.no_spend_next_command_effect.label` is
  `dry_run_planned_job_no_provider_call_no_credit_debit_no_media_write`, with
  `no_spend`, `hosted_create_dry_run`, `planned_job`, and `plan_receipt` true,
  `activity_event: "job.planned"`, and provider call, credit debit, and media
  write false. It may create a recoverable planned job/activity receipt, but no
  provider execution, debit, downloadable asset, or media write. If the guide authenticated from
  env or stdin, prefer
  `data.auth_handoff.next_command.with_env` or
  `data.auth_handoff.next_command.with_stdin` so auth follows the create.

Manual escape hatches are not prerequisites. Use them only when
`data.next_command` / `data.escape_hatches` asks, or when the task genuinely
needs deeper capability, quota, payment, or planning detail:

```bash
image-skill trust
image-skill doctor
image-skill models list
image-skill models show openai.gpt-image-2
image-skill whoami
image-skill usage quota
image-skill create --dry-run --prompt "a compact field camera on a stainless workbench"
```

Use `--show-token --no-save` for hosted signup only when the runtime can
immediately store the raw token once outside local config. For later commands,
saved config is the default; `IMAGE_SKILL_TOKEN` and `--token-stdin` remain
available for runtimes with a separate secret store.
`create --guide` also returns `data.auth_handoff` with copy-safe env/stdin
templates when auth is required or when the returned create command needs the
same auth context.

### Local Config And Install

Prefer package execution in fresh agent sandboxes:

```bash
npm_config_update_notifier=false npx -y image-skill@latest create --guide --prompt "a compact field camera on a stainless workbench" --json
```

Global install is optional, not the primary path. If `npm install -g image-skill`
or `npx image-skill@latest ...` hits prefix/cache `EACCES`, retry with writable
package-manager paths instead of cloning private source:

```bash
export npm_config_cache="${npm_config_cache:-$PWD/.npm-cache}"
export npm_config_prefix="${npm_config_prefix:-$PWD/.npm-global}"
export PATH="$npm_config_prefix/bin:$PATH"
npm_config_update_notifier=false npx -y image-skill@latest create --guide --prompt "a compact field camera on a stainless workbench" --json
```

For `npx skills add ... -g -a codex` installs, the writable target is Codex
agent home rather than the npm prefix. If the Codex/global skill target is
read-only or cannot create its default directory, keep the tracked slug install
and point agent skill state at a writable workspace home. The skills.sh Codex
adapter writes to `$HOME/.agents`; `CODEX_HOME` keeps Codex profile state on the
same writable path:

```bash
export HOME="$PWD/.agent-home"
export CODEX_HOME="$HOME/.codex"
mkdir -p "$HOME" "$CODEX_HOME"
npx skills add danielgwilson/image-skill-cli --skill image-skill -g -a codex -y
```

Hosted signup saves auth state to the public CLI config by default. If the
runtime needs a writable compatibility config path, set
`IMAGE_SKILL_CONFIG_PATH` before `signup`:

```bash
export IMAGE_SKILL_CONFIG_PATH="$PWD/.image-skill/config.json"
npm_config_update_notifier=false npx -y image-skill@latest signup --agent \
  --agent-contact agent-inbox@example.com \
  --agent-name creative-agent \
  --runtime codex \
  --json
```

Config write failures return `PUBLIC_CLI_CONFIG_WRITE_FAILED` with a structured
`error.recovery.suggested_command`. Agents should follow that recovery field,
then rerun `create --guide` for the requested creative flow.
When `create --guide` reaches `auth_required`, it probes the configured auth
path first. If local config cannot be written, `data.next_command` prefixes the
normal saved-config signup with
`IMAGE_SKILL_CONFIG_PATH="$PWD/.image-skill/config.json"`, so the first recovery
step still saves auth locally without exposing the one-time token.
`--show-token --no-save` and `data.auth_handoff.rerun_guide.with_stdin` remain
structured fallback paths for runtimes that intentionally use a separate secret
store.

### `image-skill whoami`

Shows current actor, organization, claim state, token class, and grants.
The JSON includes `session_origin` so a fresh agent can tell whether it is
unauthenticated, loaded a saved config, created the token in this process, or
is using hosted-session auth. `token_created_at` is the active token creation
timestamp when Image Skill can prove it, otherwise `null`.

```bash
image-skill whoami --json
```

Minimum success data:

```json
{
  "authenticated": true,
  "session_origin": "loaded_from_config",
  "token_status": "active",
  "token_created_at": "2026-05-08T12:00:00.000Z"
}
```

### `image-skill usage quota`

Canonical pre-spend check. Shows remaining credits, job limits, model limits,
and reset windows before create/edit.

```bash
image-skill usage quota --json
```

`image-skill quota --json` remains a compatibility alias.

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/quota \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN"
```

### `image-skill credits methods`

Machine-readable payment rail discovery. Use this before quoting or buying so
agents can tell which rails are available, whether live money can move, whether
browser/human action is required, and which command to try next.

```bash
image-skill credits methods --json
```

Minimum success data shape:

```json
{
  "contract_version": "image-skill.payment-methods.v1",
  "credit_unit_cents": 1,
  "currency": "USD",
  "quote_endpoint": "/v1/credit-quotes",
  "packs_endpoint": "/v1/credit-packs",
  "status_endpoint": "/v1/credit-purchases/status",
  "methods": [
    {
      "method_id": "stripe_checkout",
      "status": "available",
      "available": true,
      "quoteable": true,
      "purchasable": true,
      "live_money": true,
      "buyer_modes": ["hybrid", "human_only"],
      "requires_browser": true,
      "agent_initiated": true,
      "agent_settleable": false,
      "settlement_blocker": "requires human browser checkout completion",
      "default_pack_id": "starter-500",
      "purchase_endpoint": "/v1/credit-purchases/stripe-checkout-sessions"
    },
    {
      "method_id": "stripe_x402.exact.usdc",
      "status": "available",
      "available": true,
      "quoteable": true,
      "purchasable": true,
      "live_money": true,
      "buyer_modes": ["agent_only", "hybrid"],
      "requires_browser": false,
      "agent_initiated": true,
      "agent_settleable": true,
      "settlement_blocker": null,
      "default_pack_id": "starter-500",
      "purchase_endpoint": "/v1/credit-purchases/stripe-x402-deposits"
    }
  ]
}
```

Public payment discovery is intentionally action-first. Limited-rollout rails
may be returned with `available:false`, `quoteable:false`, `purchasable:false`,
and a non-null `unavailable_reason` so headless agents can understand the path
without trying it. Use a method only when it is returned with `available:true`,
`quoteable:true`, and `purchasable:true`.

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/payment-methods
```

### `image-skill credits packs list`

Lists the recommended Image Skill credit packs. Packs are the default
live-money buying UX because agents get obvious starter choices and avoid tiny
fee traps. Use the payment method catalog to choose the rail:
`stripe_checkout` when a human sponsor can complete Checkout, or
`stripe_x402.exact.usdc` when a wallet-equipped agent can settle a browserless
live crypto deposit attempt from returned pay-to instructions.
Exact custom quotes are still supported when an agent already knows the
required credit budget.

```bash
image-skill credits packs list --json
```

Minimum success data:

```json
{
  "credit_unit_cents": 1,
  "credit_unit_usd": 0.01,
  "currency": "USD",
  "default_pack_id": "starter-500",
  "packs": [
    {
      "pack_id": "starter-500",
      "name": "Starter",
      "display_name": "Starter (500 credits)",
      "credits": 500,
      "amount_cents": 500,
      "amount_usd": "5.00",
      "price_usd": "5.00",
      "currency": "USD"
    }
  ],
  "custom_quotes": {
    "supported": true,
    "min_credits": 1,
    "max_credits": 5000
  }
}
```

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/credit-packs
```

### `image-skill credits quote`

Requests a bounded credit quote from the hosted service. Public top-ups use the
payment method returned by `credits methods --json`: `stripe_checkout` for the
human Checkout path, or `stripe_x402.exact.usdc` for a browserless
action-required deposit attempt. A quote never grants credits.
One Image Skill credit is a stable user-facing value unit worth `$0.01`.
Creative operations can consume more than one credit based on the selected
model's provider cost and Image Skill's margin policy; inspect
`models show MODEL_ID --json` and operation `cost.credit_pricing` for the exact
debit before spending.

```bash
image-skill credits quote --credits 10 --payment-method stripe_x402.exact.usdc --json
```

Always pass the payment method from `credits methods --json`; the public CLI
does not infer one. For retry-stable automation, provide an explicit non-secret
idempotency key:

```bash
image-skill credits quote \
  --credits 10 \
  --payment-method stripe_x402.exact.usdc \
  --idempotency-key quote-run-001 \
  --json
```

Idempotency keys are scoped to the current hosted agent identity and exact
quote request. Reusing a key with different credits, pack, or payment method
returns a structured `error.recovery.suggested_command` with a fresh
idempotency key for the attempted quote terms.

For Stripe Checkout terms, prefer a named pack:

```bash
image-skill credits quote \
  --pack starter-500 \
  --payment-method stripe_checkout \
  --idempotency-key stripe-pack-quote-run-001 \
  --json
```

For the browserless agent x402 rail, quote the exact method id returned by
`credits methods --json`:

```bash
image-skill credits quote \
  --pack starter-500 \
  --payment-method stripe_x402.exact.usdc \
  --idempotency-key agent-x402-quote-run-001 \
  --json
```

For exact custom terms, keep the same rail choice. Use
`stripe_x402.exact.usdc` for an agent-settleable browserless rail, or use
`stripe_checkout` only for a human Checkout fallback:

```bash
image-skill credits quote \
  --credits 137 \
  --payment-method stripe_checkout \
  --idempotency-key exact-quote-run-001 \
  --json
```

Minimum success data:

```json
{
  "quote_id": "quote_...",
  "state": "created",
  "credits": 10,
  "price_amount_cents": 10,
  "currency": "USD",
  "expires_at": "2026-05-08T20:00:00.000Z",
  "accepted_payment_method": "stripe_checkout",
  "idempotency_key": "quote-run-001",
  "pack_id": null,
  "pack": null,
  "live_money": true
}
```

For x402 quotes, `accepted_payment_method` is
`"stripe_x402.exact.usdc"`. The quote does not grant credits or include pay-to
instructions; `credits buy --provider stripe_x402` creates the action-required
deposit challenge.

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/credit-quotes \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN" \
  -H "content-type: application/json" \
  -d '{"pack_id":"starter-500","payment_method":"stripe_x402.exact.usdc","idempotency_key":"agent-x402-quote-run-001"}'
```

### `image-skill credits buy`

Creates a payment action for a previously returned quote. Choose the provider
that matches the quote's `accepted_payment_method`.

For a `stripe_x402.exact.usdc` quote, `--provider stripe_x402` creates a
browserless action-required USDC deposit attempt. When the response includes
`stripe_x402.payable_instructions`, a wallet-equipped agent may pay the exact
USDC amount to `deposit_address` on Base without using a browser. The response
is live money when `live_money:true`. Credits are granted only after verified
settlement and webhook fulfillment succeeds. Deposit challenge creation itself
must not mutate credit balances. Stay within the delegated cap and never pass
wallet private keys, seed phrases, x402 payment headers, deposit client
secrets, card data, Stripe secrets, or provider receipts to Image Skill.
When `create --guide` enters `quota_required` for this rail, it returns
`data.self_fund_handoff.wallet_settlement` with the buy/status response fields
to inspect: `data.stripe_x402.payable_instructions` after `credits buy`, or
`data.payment_attempt.stripe_x402.payable_instructions` after `credits status`.

```bash
image-skill credits buy \
  --provider stripe_x402 \
  --quote-id quote_... \
  --idempotency-key agent-x402-buy-run-001 \
  --json
```

Minimum x402 action-required data:

```json
{
  "state": "action_required",
  "quote_id": "quote_...",
  "payment_attempt_id": "payatt_...",
  "provider": "stripe",
  "accepted_payment_method": "stripe_x402.exact.usdc",
  "credits": 500,
  "amount_cents": 500,
  "currency": "USD",
  "live_money": true,
  "stripe_x402": {
    "method_id": "stripe_x402.exact.usdc",
    "scheme": "exact",
    "network": "base",
    "token_currency": "usdc",
    "deposit_address_present": true,
    "payable_instructions": {
      "kind": "stripe_crypto_deposit",
      "network": "base",
      "token_currency": "usdc",
      "token_decimals": 6,
      "token_amount": "5.00",
      "token_amount_atomic": "5000000",
      "amount_cents": 500,
      "amount_usd": "5.00",
      "deposit_address": "0x...",
      "token_contract_address": "0x...",
      "supported_token_currencies": ["usdc"],
      "expires_at": "2026-05-08T20:00:00.000Z",
      "exact_amount_required": true
    },
    "redacted": {
      "payment_intent_id": "[redacted-stripe-payment-intent]",
      "deposit_address": "[redacted-stripe-crypto-deposit-address]",
      "client_secret": "[redacted-stripe-client-secret]"
    }
  },
  "next": {
    "agent_action": "pay_stripe_crypto_deposit",
    "suggested_commands": [
      "image-skill credits status --payment-attempt-id payatt_... --json"
    ]
  }
}
```

For a `stripe_checkout` quote, `--provider stripe` creates a hosted Stripe
Checkout Session and returns an `action_required` response with
`checkout_handoff_url`.

Agents should present or open `checkout_handoff_url` for humans. It is a short
Image Skill URL that redirects to Stripe Checkout and is safe to copy from
mobile terminals, SSH clients, and wrapped chat output. `checkout_compact_url`
is also copy-safe and equals the Image Skill handoff when the hosted API can
provide one. `checkout_url` is the raw Stripe compatibility fallback only; do
not present it unless no handoff URL is available. Do not trim Stripe Checkout
URLs: the long `#...` fragment is required by Stripe Checkout in the browser.
Present any fallback Stripe URL in a fenced code block so terminal wrapping does
not corrupt it. Stripe-hosted Checkout may also show a promotion-code field for
operator-provided codes; agents should let the human enter those codes on
Stripe, never collect promo codes, card details, or wallet credentials in the
Image Skill CLI.

```bash
image-skill credits buy \
  --provider stripe \
  --quote-id quote_... \
  --idempotency-key stripe-buy-run-001 \
  --json
```

Minimum success data:

```json
{
  "state": "action_required",
  "quote_id": "quote_...",
  "payment_attempt_id": "payatt_...",
  "provider": "stripe",
  "accepted_payment_method": "stripe_checkout",
  "checkout_session_id": "cs_...",
  "checkout_handoff_url": "https://api.image-skill.com/pay/payatt_...",
  "checkout_compact_url": "https://api.image-skill.com/pay/payatt_...",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_...#fid...",
  "credits": 500,
  "amount_cents": 500,
  "currency": "USD",
  "live_money": true,
  "next": {
    "human_action": "open_checkout_url",
    "checkout_handoff_url": "https://api.image-skill.com/pay/payatt_...",
    "checkout_compact_url": "https://api.image-skill.com/pay/payatt_...",
    "fallback_checkout_url": "https://checkout.stripe.com/c/pay/cs_...#fid...",
    "after_payment": "open checkout_handoff_url or checkout_compact_url; use the full checkout_url only if no Image Skill handoff URL is available, and preserve its Stripe # fragment. Then poll image-skill credits status --payment-attempt-id PAYMENT_ATTEMPT_ID --json or image-skill usage quota --json; credits are granted only after verified webhook fulfillment"
  }
}
```

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/credit-purchases/stripe-checkout-sessions \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN" \
  -H "content-type: application/json" \
  -d '{"quote_id":"quote_...","idempotency_key":"stripe-buy-run-001"}'
```

x402 hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/credit-purchases/stripe-x402-deposits \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN" \
  -H "content-type: application/json" \
  -d '{"quote_id":"quote_...","idempotency_key":"agent-x402-buy-run-001"}'
```

### `image-skill credits status`

Without a payment reference, shows the current credit balance using the same
quota data as `image-skill usage quota --json`. With a payment reference,
shows the durable state of a quote, x402 deposit attempt, Stripe Checkout
attempt, Checkout Session, or receipt. Use the referenced form after
`credits buy` so agents do not have to infer payment state from quota deltas
or activity text.

```bash
image-skill credits status --json
image-skill credits status \
  --payment-attempt-id payatt_... \
  --json
```

At most one reference flag is allowed: `--quote-id`,
`--payment-attempt-id`, `--checkout-session-id`, or `--receipt-id`. Passing no
reference returns the balance/quota state.

Minimum action-required data:

```json
{
  "state": "action_required",
  "quote": {
    "quote_id": "quote_...",
    "credits": 500,
    "price_amount_cents": 500,
    "accepted_payment_method": "stripe_checkout",
    "pack_id": "starter-500",
    "x402": null
  },
  "payment_attempt": {
    "payment_attempt_id": "payatt_...",
    "checkout_session_id": "cs_...",
    "checkout_handoff_url": "https://api.image-skill.com/pay/payatt_...",
    "checkout_compact_url": "https://api.image-skill.com/pay/payatt_...",
    "checkout_url": "https://checkout.stripe.com/c/pay/cs_...#fid...",
    "attempt_status": "requires_action"
  },
  "receipt": null,
  "credit_event": null,
  "next": {
    "retry_after_seconds": 10,
    "human_action": "open_checkout_url",
    "checkout_handoff_url": "https://api.image-skill.com/pay/payatt_...",
    "checkout_compact_url": "https://api.image-skill.com/pay/payatt_..."
  }
}
```

Minimum success data includes `state: "succeeded"`, `receipt`,
`credit_event`, and the updated hosted `limits`.

Hosted API equivalent:

```bash
curl -sS "https://api.image-skill.com/v1/credit-purchases/status?payment_attempt_id=payatt_..." \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN"
```

Do not pass card data, wallet secrets, provider receipts, Stripe secrets, MPP
tokens, SPTs, live x402 payment headers, deposit client secrets, wallet
private keys, seed phrases, or any payment credential to credits commands.
Stripe Checkout collects payment details only on Stripe-hosted pages; x402
settlement is handled by the agent/wallet against the returned redacted deposit
challenge, not by pasting credentials into Image Skill. The public request
fields are `credits`, `pack_id`, `payment_method`, `quote_id`, status reference
IDs, and `idempotency_key`.

### `image-skill models`

First-run creative discovery. Lists public models and shows the full
capability-preserving schema for one model.

```bash
image-skill models --json
image-skill models list --json
image-skill models list --summary --json
image-skill models list --available --operation image.generate --json
image-skill models list --available --operation image.edit --json
image-skill models list --available --modality video --operation video.generate --json
image-skill models list --catalog-only --provider fal --json
image-skill models show MODEL_ID --json
image-skill models show default --json
```

Hosted API equivalents:

```bash
curl -sS https://api.image-skill.com/v1/models
curl -sS 'https://api.image-skill.com/v1/models?available=true&modality=video&operation=video.generate'
curl -sS https://api.image-skill.com/v1/models/xai.grok-imagine-image
```

`models show` exposes operation support, media input/output types, parameter
schemas, defaults and fixed controls, cost and latency class, safety behavior,
and migration hints. Agents should inspect it before assuming a model supports
seeds, masks, reference images, transparent backgrounds, arbitrary aspect
ratios, image-size presets, output counts, resolution controls, safety
controls, or provider-native options.

`models list` is executable-first by default and returns one
`default: true` row when the default executable create model is included.
`models show default --json` resolves to that model so first-run agents can
inspect the recommended create surface without knowing a provider-specific
model id. The list response also returns `summary` with total, returned,
available, executable, catalog-only, provider split,
`execution_availability`, first actionable model ids, recommended filter
commands, and catalog-inclusion flags. Default list output excludes
catalog-only rows so fresh agents see executable candidates first. Use
`--summary` when you need a compact, sortable model menu: each row keeps the
model id, flat `estimated_usd_per_image`, `credits_required`, lightweight
`task_tags`, status, provider, max output count/resolution, storage, and
`show_command`, while omitting full parameter schemas. Use `--available` for
currently usable executable rows, `--modality image|video|audio|3d` for media
type, `--operation image.generate`, `--operation image.edit`,
`--operation video.generate`, `--operation audio.generate`, or
`--operation 3d.generate` for the task, `--provider fal|xai|openai` to narrow by
provider, and `--catalog-only` when you intentionally want source-backed rows
that are inspectable but not runnable yet. Provider-level availability is not
the same thing as model executability; for runnable choices require both
`status:"available"` and
`execution.model_execution_status:"executable"`. If a reachable provider has no
runnable model for the requested operation, `summary.execution_availability`
says so directly and includes the fastest `--available --operation ...`
recovery command.

Image Skill standardizes common controls so agents can work quickly, but it
must not flatten rich model capabilities into coarse universal categories.
Use `model_parameters` for rare or model-specific parameters advertised by the
capability schema.

Current executable provider-native controls include:

- Fal FLUX.1 dev: `model_parameters.image_size` for presets such as
  `square_hd`, plus `seed`.
- Fal FLUX Pro 1.1 Ultra Create: `model_parameters.seed` and
  `model_parameters.raw`; optional reference-image controls remain cataloged
  for inspection but are not executable on the create-only path.
- Fal Z-Image Turbo Create/Edit: `model_parameters.image_size` for
  `square_hd`, `square`, portrait/landscape presets, and `auto` on edit; costs
  are quoted from requested megapixels when the output size is explicit.
- Fal Nano Banana 2 Edit: `model_parameters.resolution` for `0.5K`, `1K`,
  `2K`, and `4K`, plus `seed`.
- Fal Ideogram V2 Edit: `model_parameters.expand_prompt`, `seed`, and
  `style`; pass masks as top-level `--mask` / `mask_asset_id`, not as
  provider `mask_url`.
- Fal Gemini 3 Pro Image Preview Create/Edit:
  `model_parameters.resolution` for `1K`, `2K`, and `4K`, plus `seed`; 4K is
  quoted as the higher-priced provider tier.
- Fal Nano Banana Pro Create/Edit: `model_parameters.resolution` for `1K`,
  `2K`, and `4K`, plus `seed`; 4K is quoted as the higher-priced provider tier.
- Fal FLUX Pro Kontext Pro/Max Edit: `model_parameters.seed`; guidance scale
  and aspect-ratio controls remain cataloged for inspection but are not
  executable until their UX and receipt behavior are represented.
- Fal Bytedance Seedream 4.5 Create/Edit: `model_parameters.image_size` for
  `square_hd`, `square`, portrait/landscape presets, `auto_2K`, and
  `auto_4K`, plus `seed`; multi-output and multi-reference controls remain
  cataloged but fixed for hosted accounting.
- Fal Bytedance Seedream 5.0 Lite Create/Edit:
  `model_parameters.image_size` for `square_hd`, `square`, portrait/landscape
  presets, `auto_2K`, and `auto_3K`; multi-output and multi-reference controls
  remain cataloged but fixed for hosted accounting.
- xAI Grok Imagine Image Quality: `model_parameters.resolution` for `1k` and
  `2k`; 2k is priced from the higher provider tier. Create supports top-level
  `--output-count` up to the model's advertised `max_outputs_per_request`,
  currently mapped to xAI's documented `n` batch parameter.
- GPT Image 1.5 create/edit: documented fixed sizes `1024x1024`,
  `1024x1536`, and `1536x1024`, output format, compression, transparent or
  opaque background, moderation, and the upstream provider-native quality
  parameter. GPT Image 1.5 create quotes output-token estimates when quality
  and concrete size are known; GPT Image 1.5 create supports top-level
  `--output-count` up to the model's advertised `max_outputs_per_request`,
  currently mapped to OpenAI's `n` parameter. GPT Image 1.5 edit accepts
  low/high `input_fidelity` and remains preflight unknown-cost until usage is
  returned.
- GPT Image 2 create/edit: size, output format, compression, background,
  moderation, and the upstream provider-native quality parameter. GPT Image 2
  create quotes request-aware output-token estimates when quality and concrete
  size are known; GPT Image 2 create supports top-level `--output-count` up to
  the model's advertised `max_outputs_per_request`, currently mapped to
  OpenAI's `n` parameter. GPT Image 2 edit remains preflight unknown-cost, then
  records usage-priced provider cost when OpenAI returns token usage.

Inspect each model before use; provider-native controls are available only
through validated `model_parameters`.

### `image-skill capabilities`

Schema-language view over the same capability catalog. Use this when you need
the capability abstraction directly rather than starting from a model.

```bash
image-skill capabilities --json
image-skill capabilities list --json
image-skill capabilities show CAPABILITY_ID --json
```

### `image-skill create`

Guides, creates, or plans a zero-cost dry run.

Guide the first image path without mutation:

```bash
image-skill create --guide --prompt "A compact field camera on a stainless workbench" --json
```

`create --guide` returns `schema: image-skill.create-guide.v1`,
`stage`, `next_command`, `next_command_copy_runnable`,
`next_command_missing_inputs`, `guide_warning`, `auth_ready`,
`no_spend_evaluation`, `recommended_no_spend_command`,
`self_fund_next_command`, `self_fund_handoff`, `escape_hatches`, selected
executable model and cost, auth/quota/payment blockers, and mutation flags. All
mutation flags must be false in guide mode: no provider call, hosted create,
signup, payment object, credit debit, or media write.
For next-command safety, read `next_command_copy_runnable`,
`next_command_missing_inputs`, and `guide_warning.next_command_safety` before
acting: `hosted_signup_no_spend_setup` is no-spend auth setup,
`live_money_payment_action` is top-up/payment work, and
`live_media_create_credit_debit` is a live create that can call a provider,
debit credits, and write media.
For payment state, read
`checks.payments.preferred_method_summary.top_up_path` instead of inferring
from several arrays. It is `browserless_agent_self_fund` when the preferred
rail is live money, browserless, agent initiated, and agent settleable;
`human_payment_handoff` when a human/browser completion step is required; and
`payment_method_inspection` when the guide cannot classify a direct top-up path.
In guide cost output, `cost.estimated_usd_per_image` is the estimated Image
Skill debit in dollars for one output, matching
`cost.estimated_debit_usd_per_image` and
`cost.estimated_credits * cost.credit_unit_usd` when credit pricing is known.
`cost.estimated_provider_usd_per_image` is the upstream provider estimate for
transparency; do not use it as the amount the agent needs to fund.

```bash
image-skill create \
  --prompt "A compact field camera on a stainless workbench" \
  --intent explore \
  --aspect-ratio 1:1 \
  --max-estimated-usd-per-image 0.07 \
  --json
```

Hosted defaults are quality-first. If an agent does not choose a model, Image
Skill selects the strongest available create capability for the requested
intent and budget, then records the decision in `request.selection`. Explicit
`--provider`, `--model`, namespaced model ids, and validated
`model_parameters` always take precedence. For final/product/hero-style
intents, Image Skill may default an eligible quality-capability request to a
higher output tier only when `--max-estimated-usd-per-image` is high enough for
that tier; otherwise it stays on a lower-cost quality tier or chooses a cheaper
capability within the budget and tells agents what happened in the selection
receipt. Use the `--max-estimated-usd-per-image` value returned by
`create --guide`; it is sized to the Image Skill credit debit, not only the
upstream provider estimate.

Preview-compatible richer shape:

```bash
image-skill create \
  --prompt "Campaign-ready product image of a compact field camera" \
  --intent finalize \
  --model MODEL_ID \
  --aspect-ratio 1:1 \
  --output-count 2 \
  --max-estimated-usd-per-image 0.07 \
  --model-parameters-json '{"seed":1234}' \
  --json
```

Use `--output-count N` only when `models show MODEL_ID --json` advertises
`media.output.max_outputs_per_request` greater than `1`. `--output-count` is a
top-level Image Skill create control; do not pass provider-native `n` through
`model_parameters` unless the selected model schema explicitly advertises that
field. Credit pricing and `cost.credit_pricing.credits_required` are total
operation debits across all requested outputs. `--max-estimated-usd-per-image`
and raw API `max_estimated_usd_per_image` are per-image Image Skill debit
budget guards.

Generate video through the same `create` command and durable-media loop. For
video prompts, run `image-skill create --guide --prompt "..." --json`; the guide
can select the executable video model, suggest `--aspect-ratio 16:9`, and emit
the next create command. Plain `create` without a model still defaults to an
image model, so use the guide or pass the video model id directly. The response
returns a durable owned `video_...` mp4 asset URL, a `job_id`, and a
`cost.credit_pricing` receipt just like an image create.

```bash
image-skill create \
  --model fal.ltx-video-13b-distilled \
  --prompt "A slow dolly push-in on a steaming espresso cup on a cafe counter, morning light" \
  --aspect-ratio 16:9 \
  --json
```

Discover runnable video models with `image-skill models list --available
--modality video --operation video.generate --json`. Inspect parameters, output
media type, and cost first with `image-skill models show
fal.ltx-video-13b-distilled --json`. Video runs synchronously through the same
create call and can take longer than an image; the returned `assets[].url` is an
owned `video/mp4`.

Generate audio (music, sound) through the same `create` command and
durable-media loop. Request an audio model by id; the response returns a durable
owned `audio_...` wav asset URL, a `job_id`, and a `cost.credit_pricing` receipt
just like an image create. Audio has no aspect ratio, so do not pass
`--aspect-ratio`.

```bash
image-skill create \
  --model fal.stable-audio-25-text-to-audio \
  --prompt "A warm lo-fi hip-hop loop with vinyl crackle and a mellow Rhodes piano" \
  --json
```

`fal.stable-audio-25-text-to-audio` (Stable Audio 2.5) is text-to-audio at a flat
$0.20/clip (about 34 credits, quoted before spend) and returns an owned
`audio/wav` clip. The first slice is defaults-only (no tunable
`model_parameters`); duration/steps controls are a later milestone. Inspect
parameters, output media type, and cost first with `image-skill models show
fal.stable-audio-25-text-to-audio --json`. Audio runs synchronously through the
same create call and can take longer than an image.

For create models with wired reference support, pass owned reference assets
with the model's advertised reference role. Kling element routes use
`--element-frontal IMAGE[@ELEMENT_INDEX]` and
`--element-reference IMAGE[@ELEMENT_INDEX[:REFERENCE_INDEX]]`; flat
reference-image routes use `--reference-image IMAGE[@INDEX]`; Fal DreamO also
accepts `:TASK` where `TASK` is `ip`, `id`, or `style`. The public CLI uploads
local paths and external URLs first, then
sends top-level `references[]` entries with Image Skill `asset_id` values to
`/v1/create`. Do not pass provider-native `elements`, `frontal_image_url`,
`reference_image_urls`, `first_image_url`, `second_image_url`, `images`, or
`*_reference_task` through `model_parameters`; provider-private URLs are
resolved server-side after ownership and media-policy validation.

```bash
image-skill create \
  --model fal.kling-image-o3-text-to-image \
  --prompt "Place the same character in a clean studio campaign" \
  --element-frontal ./character-front.png@0 \
  --element-reference ./character-side.webp@0:0 \
  --output-count 2 \
  --max-estimated-usd-per-image 0.06 \
  --json
```

```bash
image-skill create \
  --model fal.dreamo \
  --prompt "Studio portrait preserving identity with a bolder editorial style" \
  --reference-image ./identity.png@0:id \
  --reference-image ./style.webp@1:style \
  --model-parameters-json '{"image_size":{"width":1280,"height":720}}' \
  --max-estimated-usd-per-image 0.06 \
  --json
```

High-resolution examples:

```bash
image-skill create \
  --prompt "Campaign-ready product image of a compact field camera" \
  --intent final \
  --max-estimated-usd-per-image 0.07 \
  --json

image-skill create \
  --prompt "Campaign-ready product image of a compact field camera" \
  --model fal.gemini-3-pro-image-preview \
  --model-parameters-json '{"resolution":"4K"}' \
  --max-estimated-usd-per-image 0.30 \
  --json

image-skill create \
  --prompt "Campaign-ready product image of a compact field camera" \
  --model xai.grok-imagine-image-quality \
  --model-parameters-json '{"resolution":"2k"}' \
  --max-estimated-usd-per-image 0.07 \
  --json

image-skill edit \
  --input-asset-id image_... \
  --prompt "preserve the subject and make this campaign-ready" \
  --model fal.nano-banana-2-edit \
  --model-parameters-json '{"resolution":"4K"}' \
  --accept-unknown-cost \
  --json
```

`model_parameters` must be validated against the selected model/capability
schema before any provider call or paid reservation. Unknown fields fail closed
unless the capability explicitly allows additional properties. This is how
Image Skill preserves rare model controls without turning every
provider-specific parameter into a top-level flag.
In the current preview, Fal create/edit, xAI quality generation, and OpenAI GPT
Image 2 expose the executable provider-native controls listed in the selected
model schema. GPT Image 2 create has request-aware output-token credit quotes
for concrete quality/size requests; GPT Image 2 edit still requires
unknown-cost acceptance before execution, but records usage-priced provider cost
after execution when OpenAI returns token usage. Provider-native controls remain
visible for planning and fail closed until their capability schema marks them
executable. Hosted `create --dry-run` validates `model_parameters` against the
selected model, returns accepted keys/provenance and request-aware credit
pricing for planning, and never executes provider controls or consumes credits.
Hosted `edit --dry-run` validates the same owned input, mask/reference,
prompt-policy, budget, and `model_parameters` checks as a live edit, then
returns planned outputs without storage, provider, or billing side effects.
For dry-run responses, `cost.credit_pricing.credits_required` is the planned
live execution debit for the selected model. The actual debit for the dry run is
`quota.consumed_credits: 0`.
Authenticated hosted dry-runs also create a recoverable planned job:
`jobs show` returns `status: "planned"` with `plan_receipt`, and `activity`
emits `job.planned`. Planned receipts do not create downloadable media assets or
usage debits, media writes, or provider execution. In the first-run guide, this
exact no-spend command behavior is exposed as
`data.no_spend_next_command_effect` and
`data.recommended_no_spend_command_effect`; the evaluator stop policy is exposed
as `data.no_spend_evaluation`.

Minimum success data:

```json
{
  "job_id": "job_...",
  "capability": {
    "id": "is.image.generate.xai-grok-imagine-image-quality.v1"
  },
  "assets": [
    {
      "asset_id": "image_...",
      "path": "https://media.image-skill.com/a/image_abc123.png",
      "mime_type": "image/png",
      "url": "https://media.image-skill.com/a/image_abc123.png",
      "content_length": 333444,
      "width": 2048,
      "height": 2048
    }
  ],
  "cost": {
    "estimated_usd": 0.07,
    "credit_pricing": {
      "credit_unit_usd": 0.01,
      "credits_required": 12,
      "estimated_provider_cost_usd": 0.07,
      "estimated_revenue_usd": 0.12,
      "pricing_confidence": "known"
    }
  },
  "request": {
    "output_count": 1,
    "selection": {
      "policy": "hosted_default_create_v1",
      "reason": "hosted default selected the strongest currently available quality-first create model",
      "intent": "explore",
      "capability": {
        "id": "is.image.generate.xai-grok-imagine-image-quality.v1"
      },
      "model_parameters": {
        "keys": ["resolution"],
        "defaults_applied": ["resolution=2k"],
        "source": "default_policy"
      },
      "output": {
        "resolution_class": "2k",
        "expected_width": null,
        "expected_height": null,
        "expected_min_short_edge": 2048
      }
    }
  },
  "safety": {
    "status": "allowed"
  }
}
```

When hosted artifact storage is configured, `url` is an Image Skill-owned URL.
Agents should prefer `assets[].url` over provider-origin URLs and should not
need provider account access to fetch outputs.

Hosted create does not accept `--output-dir`. A future download/fetch command
may add CLI-side local file convenience while preserving hosted artifact URLs as
the source of truth.

If provider generation succeeds but artifact storage fails, the command returns
`ARTIFACT_STORAGE_WRITE_FAILED` with exit `9` and `retryable: false`. Agents
should not retry the whole create blindly, because that may duplicate paid
provider spend.

For retry-safe create automation, pass an explicit non-secret
`--idempotency-key`. A retry that reuses the same key does not create a second
credit reservation, so a transient `502`/`PROVIDER_FAILURE` that already
reserved a credit cannot double-charge on retry. `create --guide` bakes a
generated `--idempotency-key` into its advertised create `next_command`, and a
retryable create error returns an `error.recovery.idempotency_key` plus an
`error.recovery.suggested_command` that re-runs the same create with that key.

```bash
image-skill create \
  --prompt "A compact field camera on a stainless workbench" \
  --idempotency-key create-run-001 \
  --json
```

Hosted free-preview API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/create \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN" \
  -H "content-type: application/json" \
  -d '{
    "prompt": "A compact field camera on a stainless workbench",
    "intent": "explore",
    "aspect_ratio": "1:1",
    "output_count": 1,
    "max_estimated_usd_per_image": 0.07
  }'
```

Hosted free-preview create currently requires owned artifact storage and returns
one `assets[]` entry per output with `assets[].url` under
`https://media.image-skill.com/...` on success.

### `image-skill upload`

Normalizes a local image path or remote image URL into an Image Skill-owned
input asset for later edit workflows.

```bash
image-skill upload ./source.png --json
image-skill upload https://example.com/source.png --json
```

The CLI reads local files and remote URLs client-side, then sends image bytes to
`POST /v1/upload`. The hosted API does not fetch arbitrary remote URLs in this
preview. This keeps server-side URL fetching out of the public upload path.

Minimum success data:

```json
{
  "request": {
    "source_kind": "local_path",
    "filename": "source.png",
    "remote_origin": null
  },
  "asset": {
    "asset_id": "image_...",
    "job_id": "job_...",
    "kind": "uploaded",
    "url": "https://media.image-skill.com/a/image_abc123.png",
    "mime_type": "image/png",
    "content_length": 12345
  },
  "upload": {
    "bytes": 12345,
    "mime_type": "image/png",
    "sha256": "...",
    "policy": {
      "status": "allowed"
    }
  }
}
```

Supported preview MIME types are `image/png`, `image/jpeg`, `image/webp`,
`image/gif`, and `image/avif`. Unsupported input returns
`INPUT_POLICY_DENIED` with exit `6`. Responses never include local paths, raw
bytes, base64 payloads, full remote URLs, bucket names, or object keys.

### `image-skill edit`

Edits an Image Skill-owned input asset or client-normalized local/remote image
with one hosted provider-backed edit model.

```bash
image-skill edit \
  --input ASSET_ID_OR_PATH_OR_URL \
  --mask MASK_ASSET_ID_OR_PATH_OR_URL \
  --prompt "Remove the background and keep natural object shadows" \
  --accept-unknown-cost \
  --json
```

If `--input` is a local path or external URL, the public CLI first normalizes it
through the same upload resolver as `image-skill upload`, then sends only the
resulting `asset_id` to `POST /v1/edit`. If `--input` is an Image Skill asset id
or owned asset URL, edit uses that owned asset directly.
Add `--dry-run` to plan the edit after owned-asset, prompt-policy,
`model_parameters`, and budget validation. Dry-run edit responses return planned
assets and `quota.consumed_credits: 0`, store a recoverable `job.planned`
receipt, and do not call the provider, debit credits, or write media.
For models with wired mask support, `--mask` follows the same upload/asset-id
resolver and sends only `mask_asset_id`; never pass provider-native `mask_url`
through `model_parameters`.
For models with wired reference support, pass owned reference assets with the
model's advertised reference role. Kling element routes use
`--element-frontal IMAGE[@ELEMENT_INDEX]` and
`--element-reference IMAGE[@ELEMENT_INDEX[:REFERENCE_INDEX]]`; flat
reference-image routes use `--reference-image IMAGE[@INDEX[:TASK]]`. The
public CLI uploads local paths and external URLs first, then sends top-level
`references[]` entries with Image Skill `asset_id` values. For Kling element
routes, `--element-frontal ./front.png@0` becomes role `element_frontal` for
element index `0`, and `--element-reference ./side.webp@0:0` becomes role
`element_reference` for the same element with reference slot `0`. For DreamO
create, `--reference-image ./identity.png@0:id` becomes role
`reference_image`, index `0`, and `reference_task` `id`. For xAI edit,
`--reference-image ./reference.png@0` becomes the second ordered source image;
the primary `--input` asset remains the first source image. Do not pass
provider-native `elements`, `image_url`, `image_urls`, `frontal_image_url`,
`reference_image_urls`, `first_image_url`, `second_image_url`, `images`, or
`*_reference_task` through `model_parameters`; provider-private URLs are
resolved server-side after ownership and media-policy validation.
Current public `references[]` support covers Kling Image O1, Kling Image O3
image-to-image/text-to-image, Kling Image v3 image-to-image/text-to-image, and
Fal DreamO create plus xAI Grok Imagine image edit/quality edit. Kling requests
may contain at most 40 reference entries across at most 10 contiguous element
indexes starting at `0`; each referenced element requires one frontal image and
may include up to three additional reference images. DreamO accepts up to two
contiguous `reference_image` indexes starting at `0`, each with optional
`reference_task` `ip`, `id`, or `style`. xAI edit accepts up to two contiguous
`reference_image` indexes starting at `0` and does not accept `reference_task`.
Reference assets must be Image Skill-owned PNG, JPEG, or WebP images with
known non-empty byte length up to 10MB, known width and height of at least
300px, and aspect ratio from 0.40 to 2.50.

```bash
image-skill edit \
  --model fal.kling-image-o3-image-to-image \
  --input ./starting-frame.png \
  --element-frontal ./character-front.png@0 \
  --element-reference ./character-side.webp@0:0 \
  --prompt "Place the same character in a clean studio product portrait" \
  --accept-unknown-cost \
  --json
```

Direct `/v1/edit` callers use the same owned-asset contract:

```json
{
  "input_asset_id": "image_starting_frame",
  "model": "fal.kling-image-o3-image-to-image",
  "prompt": "Place the same character in a clean studio product portrait",
  "references": [
    {
      "asset_id": "image_character_front",
      "role": "element_frontal",
      "index": 0
    },
    {
      "asset_id": "image_character_side",
      "role": "element_reference",
      "index": 0,
      "reference_index": 0
    }
  ]
}
```

Set `dry_run: true` on `/v1/edit` to get the same no-spend plan the CLI returns.
The server still validates ownership, prompt policy, references, masks,
`model_parameters`, and budget guards before returning the planned job.

Create a 3D asset from an image through the same `edit` command and
durable-media loop. Image-to-3D is promptless and image-conditioned, so it ships
as a variation transform: pass exactly one owned input image (no prompt) to a 3D
model by id and the response returns a durable owned `.glb` mesh asset URL (in
`assets[].url`), a `job_id`, and a `cost.credit_pricing` receipt. A 3D mesh has
no aspect ratio.

```bash
image-skill edit \
  --input image_... \
  --model fal.trellis-image-to-3d \
  --json
```

`fal.trellis-image-to-3d` (Trellis) is image-to-3D at a flat $0.02/asset (about 4
credits, quoted before spend) and returns an owned `model/gltf-binary` (`.glb`)
textured mesh. The first slice is defaults-only (no tunable `model_parameters`);
guidance/steps/mesh_simplify/texture_size controls are a later milestone. Inspect
parameters, output media type, and cost first with `image-skill models show
fal.trellis-image-to-3d --json`. The input must be one Image Skill-owned image;
3D runs synchronously through the same edit call and can take longer than an
image.

Preview hosted create/edit supports model-specific provider-backed paths such
as Fal Gemini 3 Pro Image Preview Create (`fal.gemini-3-pro-image-preview`),
Fal Nano Banana 2 Edit (`fal.nano-banana-2-edit`), Fal Ideogram V2 Edit
(`fal.ideogram-v2-edit`), Fal Gemini 3 Pro Image
Preview Edit (`fal.gemini-3-pro-image-preview-edit`), Fal FLUX Pro 1.1 Ultra
Create (`fal.flux-pro-v1-1-ultra`), Fal FLUX Pro Kontext Edit
(`fal.flux-pro-kontext`), Fal FLUX Pro Kontext Max Edit
(`fal.flux-pro-kontext-max`), Fal Seedream 5.0 Lite Create
(`fal.bytedance-seedream-v5-lite-text-to-image`), Fal Seedream 5.0 Lite Edit
(`fal.bytedance-seedream-v5-lite-edit`), Fal Seedream 4.5 Create
(`fal.bytedance-seedream-v4-5-text-to-image`), Fal Seedream 4.5 Edit
(`fal.bytedance-seedream-v4-5-edit`), Fal Nano Banana Pro Create
(`fal.nano-banana-pro`), Fal Nano Banana Pro Edit
(`fal.nano-banana-pro-edit`), GPT Image 1.5 Create
(`openai.gpt-image-1.5`), GPT Image 1.5 Edit
(`openai.gpt-image-1.5-edit`), and GPT Image 2 Edit
(`openai.gpt-image-2-edit`) when their provider credentials are configured.
Fal Gemini 3 Pro Image Preview create/edit has known per-image pricing: 1K/2K
requests quote `$0.15` provider cost and 4K quotes the doubled provider tier.
Fal Nano Banana Pro create/edit uses the same `$0.15` standard and doubled 4K
provider tier. Fal FLUX Pro 1.1 Ultra Create quotes `$0.06` provider cost per
image. Fal FLUX Pro Kontext Edit quotes `$0.04` provider cost per image, and
Fal FLUX Pro Kontext Max Edit quotes `$0.08` provider cost per image. Fal
Seedream 4.5 create/edit quotes `$0.04` provider cost per image.
Fal Seedream 5.0 Lite create/edit quotes `$0.035` provider cost per image. Fal
Z-Image Turbo create/edit quotes `$0.005/MP` when `image_size` is explicit or
derived from aspect ratio; edit `auto` remains unknown-cost. GPT Image 1.5
create quotes output-token estimates for concrete quality/size requests using
OpenAI's fixed-size token table; GPT Image 1.5 edit remains preflight
unknown-cost because edit input image/text tokens are provider-metered, then
records usage-priced provider cost when OpenAI returns token usage. GPT Image 2
create quotes output-token estimates for concrete quality/size requests. GPT
Image 2 edit remains preflight unknown-cost because edit input image/text tokens
are provider-metered, then records usage-priced provider cost when OpenAI
returns token usage. Other edit paths without machine-readable pricing require
`--accept-unknown-cost` until a stable price source is captured. Responses
include a new generated asset URL, job id, safety state, quota consumption, and
input asset metadata where
applicable. Responses do not include raw prompts, source bytes, base64
payloads, local paths, full external URLs, bucket names, or object keys.

Provider/model names in this paragraph are preview provenance, not the primary
public UX. The public selection surface should be Image Skill capabilities and
model-parameter schemas; provider/model details belong in explicit
provenance/debug output.

Edit accepts the same retry-safe `--idempotency-key` as create. A retry that
reuses the same key does not create a second credit reservation, so a transient
`502`/`PROVIDER_FAILURE` after a reservation cannot double-charge; a retryable
edit error returns an `error.recovery.idempotency_key` and an
`error.recovery.suggested_command` that re-runs the same edit with that key.

### `image-skill assets show`

Inspects an Image Skill-owned asset URL or hosted asset id.

```bash
image-skill assets show \
  https://media.image-skill.com/a/image_abc123.png \
  --json
```

For asset-id lookup, use hosted auth:

```bash
image-skill assets show image_... --json
```

Minimum success data:

```json
{
  "request": {
    "reference": "image_...",
    "reference_type": "asset_id"
  },
  "asset": {
    "asset_id": "image_...",
    "job_id": "job_...",
    "url": "https://media.image-skill.com/a/image_abc123.png",
    "mime_type": "image/png",
    "content_length": 12345,
    "width": 1024,
    "height": 1024,
    "source": "hosted_metadata"
  }
}
```

External URLs are rejected. Older assets created before hosted asset metadata
was recorded may still be inspectable by Image Skill-owned URL.

### `image-skill assets get`

Downloads an Image Skill-owned asset URL or hosted asset id to a local file.

```bash
image-skill assets get \
  https://media.image-skill.com/a/image_abc123.png \
  --output ./result.png \
  --json
```

The command refuses to overwrite existing files unless `--overwrite` is
explicit. It verifies byte length when the asset server provides a
`content-length` header.

### `image-skill jobs show`

Inspects a hosted Image Skill job visible to the authenticated agent.

```bash
image-skill jobs show job_... --json
```

Output includes public job status, trace id, timestamps, capability id, cost
summary, safety status, and Image Skill-owned asset metadata. For fresh-agent
parsing, `status`, `state`, `assets`, and `cost` are mirrored at top level and
match `job.status`, `job.assets`, and `job.cost`. Provider/model provenance is
available only through explicit provenance/debug affordances for authorized
actors. Default output does not include raw prompts, generated bytes, provider
credentials, DB/storage keys, bucket names, or local paths.

Minimum success data:

```json
{
  "request": {
    "job_id": "job_..."
  },
  "status": "completed",
  "state": "completed",
  "assets": [],
  "cost": {
    "estimated_usd": 0.05,
    "provider_reported_usd_ticks": null
  },
  "job": {
    "job_id": "job_...",
    "status": "completed",
    "assets": [],
    "cost": {
      "estimated_usd": 0.05,
      "provider_reported_usd_ticks": null
    }
  }
}
```

### `image-skill jobs wait`

Waits for a hosted Image Skill job to reach a terminal status.

```bash
image-skill jobs wait job_... --timeout-ms 30000 --poll-interval-ms 1000 --json
```

Completed jobs return immediately. Non-terminal jobs poll until completion,
failure, cancellation, or deterministic timeout. Terminal success uses the same
top-level `status`, `state`, `assets`, and `cost` mirrors as `jobs show`, with
`request.timeout_ms` and `request.poll_interval_ms` added for provenance.

### `image-skill activity list`

Lists recent hosted activity ledger events visible to the authenticated agent.

```bash
image-skill activity list --limit 20 --json
image-skill activity list --subject job_... --json
```

Activity is the ledger, not the work queue. Use it to find recent event IDs,
related job IDs, asset IDs, usage IDs, feedback IDs, trace IDs, status changes,
and product-memory writes. Use `jobs show` or `jobs wait` when you need
operational recovery, polling, retry judgment, or final job assets.

Minimum success data:

```json
{
  "events": [
    {
      "event_id": "evt_...",
      "type": "job.completed",
      "occurred_at": "2026-05-05T19:00:23.000Z",
      "summary": "Create job completed",
      "operation": "create",
      "subject": {
        "type": "job",
        "id": "job_..."
      },
      "links": {
        "job_id": "job_...",
        "asset_ids": ["image_..."],
        "feedback_id": null,
        "usage_event_id": "usage_..."
      },
      "status": "completed",
      "cost": {
        "estimated_usd": 0.025
      }
    }
  ],
  "source": "hosted_activity_ledger"
}
```

The ledger hides provider and storage implementation details by default. It is
safe to cite `evt_...`, `job_...`, `image_...`, `usage_...`, `feedback_id`,
and `trace_id` values in feedback.

Hosted API equivalent:

```bash
curl -sS "https://api.image-skill.com/v1/activity?limit=20&subject=job_..." \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN"
```

### `image-skill activity show`

Shows one hosted activity event or the latest events related to one subject.

```bash
image-skill activity show evt_... --json
image-skill activity show job_... --json
image-skill activity show image_... --json
image-skill activity show sig_... --json
```

`activity show` accepts activity event IDs plus job, asset, usage, feedback, and
trace references. When the reference is a subject rather than one exact event,
the response includes matching ledger events so an agent can cite the right
event without reading telemetry logs.

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/activity/evt_... \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN"
```

### Activity Event Registry

Activity `type` values are stable public contract values. Do not infer new
event names from provider responses or telemetry logs; use only the registry
below.

| Event type                                 | Subject    | Operation   | Emitted when                                                       | Stable links                                                       |
| ------------------------------------------ | ---------- | ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `job.completed`                            | `job`      | create/edit | A hosted create or edit job reaches a terminal state.              | `job_id`, `asset_ids`, `usage_event_id`                            |
| `job.planned`                              | `job`      | create/edit | An authenticated hosted dry-run stores a recoverable plan receipt. | `job_id`                                                           |
| `asset.created`                            | `asset`    | create/edit | A hosted create or edit produces an output asset.                  | `job_id`, `asset_ids`, `usage_event_id`                            |
| `asset.uploaded`                           | `asset`    | upload      | A public edit workflow uploads or imports input media.             | `job_id`, `asset_ids`, `usage_event_id`                            |
| `usage.credit_consumed`                    | `usage`    | usage       | A creative operation records a preview-credit entry.               | `job_id`, `usage_event_id`                                         |
| `feedback.created`                         | `feedback` | feedback    | Hosted agent feedback is accepted into product memory.             | `feedback_id`                                                      |
| `feedback.github_queue.processed`          | `feedback` | feedback    | Feedback is processed by the GitHub implementation queue handoff.  | `feedback_id`                                                      |
| `payment.checkout_session.created`         | `payment`  | payment     | A Stripe Checkout session is created and awaits external action.   | `quote_id`, `payment_attempt_id`, `checkout_session_id`            |
| `credits.payment_backed_granted`           | `credit`   | credits     | Verified payment fulfillment grants paid credits.                  | `quote_id`, `receipt_id`, `credit_event_id`                        |
| `credits.payment_backed_refunded`          | `credit`   | credits     | A Stripe refund debits payment-backed credits.                     | `quote_id`, `receipt_id`, `payment_reversal_id`, `credit_event_id` |
| `credits.payment_backed_disputed`          | `credit`   | credits     | A Stripe dispute debit applies to payment-backed credits.          | `quote_id`, `receipt_id`, `payment_reversal_id`, `credit_event_id` |
| `credits.payment_backed_reinstated`        | `credit`   | credits     | Stripe dispute funds were reinstated and recorded.                 | `quote_id`, `receipt_id`, `payment_reversal_id`                    |
| `credits.payment_backed_reversal_pending`  | `credit`   | credits     | A reversal was recorded but could not be fully applied.            | `quote_id`, `receipt_id`, `payment_reversal_id`                    |
| `credits.payment_backed_reversal_rejected` | `credit`   | credits     | A reversal was rejected because it could not safely reconcile.     | `quote_id`, `receipt_id`, `payment_reversal_id`                    |

`feedback.github_queue.processed` includes `details.github_queue` with
machine-readable lifecycle fields such as `state`, `reason`, `issue_urls`,
`issue_numbers`, `mode`, and `github_mutation`. Agents should use it to learn
whether submitted feedback was promoted, skipped, deduped, blocked, or already
mirrored without reading private repository artifacts.
`job.planned` includes `details.plan_receipt` for authenticated hosted
dry-runs. It is a recoverable planning receipt, not completed media work:
planned outputs do not have durable asset IDs, download URLs, usage debits, or
provider execution.

If a response includes an event type outside this registry, treat it as a
contract bug and submit `image-skill feedback create --json` with the event ID
and trace ID.

### `image-skill feedback create`

Leaves structured product feedback in hosted Image Skill product memory.
At minimum, provide `--title` and `--body`; Image Skill accepts narrative
feedback and adds quality guidance server-side. Use the structured fields below
when the agent already knows them.

```bash
image-skill feedback create \
  --type user_feedback \
  --title "Short concrete title" \
  --body "What happened, what was expected, and why it matters" \
  --command "Command or workflow observed" \
  --expected "Expected result" \
  --actual "Actual result" \
  --proof-needed "What would prove this is handled" \
  --surface cli,docs \
  --evidence trace:TRACE_ID \
  --severity medium \
  --confidence high \
  --next-state watch \
  --json
```

Hosted feedback authenticates the same way as other hosted commands: saved
public CLI config from default signup, `IMAGE_SKILL_TOKEN`, or
`--token-stdin`. If guide/signup already saved config, run `feedback create`
normally; no raw token copy step is required. If the runtime uses its own
secret store, prefer `IMAGE_SKILL_TOKEN` or `--token-stdin`. Do not paste tokens
into feedback title, body, evidence, issues, or logs. Feedback persists through
`https://api.image-skill.com/v1/feedback`. The hosted API fails closed if
durable hosted feedback storage is unavailable.

JSON errors may include `error.recovery` with machine-readable fields such as
`required_flag`, `suggested_command`, `docs_url`, or `retry_after_seconds`.
Agents should prefer those fields over parsing prose error messages. For
example, `BUDGET_REQUIRES_CONFIRMATION` returns
`required_flag: "--accept-unknown-cost"`.

`whoami`, `usage quota`, `quota`, `credits quote`, `credits buy`,
`credits status`, `create`, `activity list`,
`activity show`, and `feedback create` accept `--token-stdin` for stdin-based
secret handoff.
`credits methods` and `credits packs list` do not require auth.

Feedback should avoid raw prompts, hosted tokens, provider keys, generated
image bytes, source image bytes, and private user data.

Hosted API equivalent:

```bash
curl -sS https://api.image-skill.com/v1/feedback \
  -H "authorization: Bearer $IMAGE_SKILL_TOKEN" \
  -H "content-type: application/json" \
  -d '{
    "type": "user_feedback",
    "title": "Short concrete title",
    "body": "What happened, what was expected, and why it matters",
    "command": "Command or workflow observed",
    "expected": "Expected result",
    "actual": "Actual result",
    "proof_needed": "What would prove this is handled",
    "surface": ["cli", "docs"],
    "evidence": ["trace:TRACE_ID"],
    "severity": "medium",
    "confidence": "high",
    "next_state": "watch"
  }'
```

### Planned Resource Commands

`jobs list`, `assets list`, `assets delete`, and async job cancellation are
planned public resource commands. They are not part of the current public
allowlist until the hosted service backs them and this contract lists their
exact command shapes. `activity list/show` is available now for ledger
readback, but it is not a substitute for future job listing, cancellation, or
retry controls.
