# Identity service contract

## Module Description

Use this contract for ASP service fields, payloads, and collection.


## Flow
### Service fields

#### Shared rules

The case-sensitive `--service` element is shared across create, update, and `validate-listing`.
Trim text values and use exact camelCase keys.

#### serviceType

- Require the exact value `A2MCP` or `A2A`.

##### Service Information Collection Guide

Immediately below the service type choices, show:

> Not sure how to proceed? See the [Developer Documentation](https://web3.okx.com/onchainos/dev-docs/okxai/asp) for detailed instructions.

#### serviceName

- Require a noun phrase, 5–100 characters.
- Require it to differ from the agent name.
- Do not include a price.

#### serviceDescription

##### Value requirements

- Required. It describes the service inside `--service`; never use the Agent profile's top-level `--description` as its value.
- Require under 1,000 characters.

A2A differences:

- Include capability and audience; signal services also include signal kind.
- Preserve supplied text and do not invent details or impose extra structure. Optional inputs and delivery/copy-trading notes may use separate, optionally numbered lines.

A2MCP differences:

- Store only the service purpose (behavior and result); keep parameter schema and method in
  `inputSchema` and `method`.

##### Collection behavior

For A2A, show the following prompt:

> Please provide a service description of up to 1,000 characters.
>
> Be sure to include:
> 1. Core capability: What the service does
> 2. Deliverables: What users receive from the service

**NEVER** show this prompt for A2MCP; its description is the request
description under the A2MCP field rules above.

#### serviceGuide

##### Value requirements

- A2A monthly create accepts optional non-blank text.
- Omit for A2A per-call and A2MCP create.

##### Collection behavior

If `serviceGuide` is absent for A2A monthly create, show the following prompt:

> Please provide a Service Guide (optional), up to 5,000 characters.
>
> Complete this section only if the buyer's agent needs to take further action after receiving the service output—for example, executing copy trades. Otherwise, you may skip it.
>
> [View the guide](https://web3.okx.com/onchainos/dev-docs/okxai/a2a-subscription).

**MUST** visibly render `View the guide` as a clickable link with this prompt.

#### fee

##### Value requirements

- `fee` is required.
- Prices are quoted numeric strings (including `"0"`) with no units, symbols, or approximations.
- A2A prices have ≤2 decimals; A2MCP prices have ≤6 decimals.
- Never combine per-call and monthly billing or use a non-monthly interval.
- Store the per-call price in `fee`; for A2A monthly billing, use `""`.

##### Collection behavior

- For A2A, ask the user to choose a billing model and provide its price:

  > Choose a billing model:
  > 1. Per call
  > 2. Monthly
  > 3. Monthly + 3-day trial
- Derive `fee`, `subscription`, and `freeTrial` from the selected model and price; do not ask the user for raw encoded values.
- If the user requests another trial length, explain the restriction above and re-ask options 2/3.

#### subscription

- Required for A2A; omit for A2MCP.
- For A2A per-call billing, use `[]`.
- For A2A monthly billing, use `[{"interval":"month","fee":"N"}]`, where `N` is greater than 0, and set `fee` to `""`.

#### freeTrial

- Only a 3-day monthly trial is supported.
- For A2A monthly billing with a trial, use `"72"`.
- Otherwise omit `freeTrial`.

#### endpoint

##### Value requirements

- For A2MCP, require a deployed public HTTPS URL of ≤512 characters.
- Reject HTTP, localhost, loopback, RFC-1918, `*.local`, `*.internal`, mocks, and placeholders.

##### Collection behavior

- If no endpoint is available, require deployment first or let the user choose A2A.
- Explain that an on-chain endpoint change requires update.

#### A2MCP fields

Every A2MCP `--service` **MUST** include `reqType` and `method`; MCP **MUST**
include `toolName`. `inputSchema` is optional and, if present, **MUST** be a
JSON Schema object. **NEVER** include `{"type":"object","properties":{}}`
with an absent or empty `required`. With `inputSchema`, `reqExample` **MUST**
be non-blank.

For `reqType:"MCP"`, select only the registration endpoint and a probed tool.
Every field **MUST** come from the endpoint probe and callability check;
**NEVER** accept manual values or edits. **MUST** stop on incomplete or unsuitable data.

| Field | MCP | HTTP |
|---|---|---|
| `reqType` | `"MCP"` | `"HTTP"` |
| `method` | `"POST"` | user-selected `GET` / `POST` |
| `toolName` | selected tool's `name` | absent |
| `inputSchema` | returned tool schema, if present | built from the user's parameter specification, if any |
| `reqExample` | required when `inputSchema` is present | required when `inputSchema` is present |

After a successful check, parameterized `inputSchema` **MUST** include the checked compact JSON as `reqExample`. Without request parameters, **MUST** omit both fields; **NEVER** send or render `reqExample:"{}"`.

#### operation

- Use `operation` only during update, with the exact value `create`, `update`, or `delete`; omit it during register.

#### id

- For update and delete, use the matched record's `id`.
- For delete, send only `operation` and `id`.
