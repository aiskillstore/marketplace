# Register flow

## Module Description

Registration flow for User, ASP, and Evaluator identities. Use canonical roles, user-provided data, and the CLI reference below. Require explicit final confirmation and never fabricate fields or IDs.


## Flow
### Workflow

#### 1. Role confirmation

Actions:

1. If the role is clear, use it; otherwise ask once and accept `1 User`, `2 ASP`, `3 Evaluator`, or a role name.
2. Map numbers, synonyms, and names in any language to `user`, `asp`, or `evaluator` before calling the CLI.

Rules:

1. Translate User / ASP / Evaluator labels into the user's language. Never
   expose raw enums, legacy role names, or bilingual labels.

#### 2. Pre-check

Actions:

1. Run the initial `agent pre-check`.
2. If `consent` is returned, show the complete translated `consent.terms` and ask the user to agree or decline. On agreement, rerun `agent pre-check` with the returned consent key; on decline, stop; if the response is ambiguous, redisplay once.
3. If `canCreate:false` is returned without `consent`, stop and follow `reason`. If `existingSameRole[0]` exists, direct the user to update that identity.
4. If `canCreate:true` is returned, continue to field collection.

Rules:

1. Each address can register only one User identity and one Evaluator identity. ASP identities are not subject to this same-role limit.

#### 3. Field collection

Follow the flow for the confirmed role.

##### Shared rules

1. Name, Description, and Avatar must come from the user. Never invent capabilities, metrics, or optional content.
2. Reject avatar URLs. Upload user-provided images with `agent upload` and pass the returned URL as `--picture`.
3. Upload images as-is; never resize, crop, or convert them. Non-square images are acceptable; 1:1 is only recommended.

##### User / Evaluator flow

1. Collect Name.
2. Accept Avatar and Description only when supplied; do not prompt for Description.
3. Upload a supplied Avatar. Omit `--picture` or `--description` when the corresponding optional field is absent.

##### ASP flow

##### Step 1: Identity profile

1. Ask for Name, Description, and Avatar in one message. Do not ask for service information in this step.
2. Require an Agent Name with no test markers or celebrity names, a one-sentence Agent Description, and an uploaded Avatar.
3. Once all three fields are ready, immediately render the identity confirmation card below.
4. Wait for reply `1` before proceeding to Step 2. This reply never runs `agent create`.

###### Identity confirmation card

```markdown
### Service Provider Identity Information

| # | Name | Avatar | Description |
|---|---|---|---|
| 1 | {Service ProviderName} | {avatarUrl} | {Service ProviderDescription} |

Please review the information above. Reply `1` to continue adding services. This will not create the identity.
```

Rules:

- Show the name and description verbatim. Preserve description line breaks. Do not add Role or Agent ID.
- Show the complete avatar URL as plain text without truncation. Do not render it as an image.
- Keep the column order shown above.
- Only reply `1` proceeds to Step 2. It does not run `agent create`.

##### Step 2: Service collection

First collect and confirm [`serviceType`](service-contract.md#servicetype), then strictly follow the matching order below. For batched answers, validate fields in this order and do not advance past a missing or invalid field. Keep valid later-step values and do not ask for them again.

###### A2A service order

1. Collect the billing choice and price; derive [`fee`](service-contract.md#fee), [`subscription`](service-contract.md#subscription), and [`freeTrial`](service-contract.md#freetrial).
2. Collect [`serviceName`](service-contract.md#servicename) and [`serviceDescription`](service-contract.md#servicedescription) together.
3. Monthly only: collect or skip [`serviceGuide`](service-contract.md#serviceguide).

###### A2MCP service order

Follow [`a2mcp-service-definition.md`](a2mcp-service-definition.md).

For `data.type:"mcp"`, collect only the endpoint and a probed tool. All fields
**MUST** come from endpoint discovery and callability verification per the
[`A2MCP fields` contract](service-contract.md#a2mcp-fields); **NEVER** accept manual values or edits.

###### Service collection completion

1. Ask **1. Add another service / 2. Done**.
2. On 1, collect `serviceType` for the next service and repeat the matching order.
3. On 2, continue to [§4. Service validation](#4-service-validation).

#### 4. Service validation

ASP only: after explicit Done, execute Create mode from `validate.md`. Continue only when it permits progression. User and Evaluator skip this step.

#### 5. Final confirmation

Actions:

1. For User / Evaluator, render one `| Field | Value |` identity card and end with localized
   `Reply 1 to confirm and run. Nothing will run before that.`
2. For ASP, do not repeat the confirmed Identity card. Render the service creation confirmation
   below after all services pass validation.

##### ASP service creation confirmation

scene: ASP registration after all services are collected and validated

display template:

```markdown
### Service Information

| # | Name | Type | Fee | Free trial | Endpoint | Description | Service Guide |
|---|---|---|---|---|---|---|---|
| 1 | <serviceName> | <serviceType> | <fee> | <freeTrial> | <endpoint> | <serviceDescription> | <serviceGuide> |

Please review the service information above. Reply `1` to confirm and create, or directly state what information needs to be changed.
```

Rules:

1. Render confirmed services in collection order, numbered consecutively from 1. Hide type-specific columns when inapplicable.
2. Show `serviceName` and `serviceDescription` verbatim. Do not rewrite or translate them.
3. Show `serviceType` only as `A2A` or `A2MCP`.
4. Show a zero price as `Free`, without a currency or billing period. Otherwise, show `N USDT / call` or `N USDT / month`, based on the confirmed billing model.
5. A2A NEVER renders `Endpoint`; show `freeTrial: "72"` as `3 days`, otherwise `—`; show non-blank `serviceGuide` verbatim, otherwise `—`.
6. A2MCP preserves the complete HTTPS `endpoint` and NEVER renders `Free trial` or `Service Guide`.
7. If any confirmed service is `A2MCP`, localize and append once: `Want to view method, inputSchema, or reqExample? Tell me which service.`
8. For every role, only the exact reply `1` to that role's final confirmation card may trigger the single `agent create`.
9. For ASP, a reply that specifies changes returns to service collection without creating the identity. Apply the requested changes, revalidate all services, and render the updated final confirmation card again.
10. Do not skip final confirmation, reuse an earlier confirmation, or show bash.

#### 6. Registration execution

Actions:

1. After final confirmation, run `agent create` once with all confirmed fields and, for ASP, every confirmed service.
2. Resolve the Agent ID using the CLI-reference precedence. If neither supported ID field exists, do not output a bare `#`.

Rules:

1. Never reuse an ID from pre-check.

#### 7. Post-success handling

Actions:

1. Report registration success. If an Agent ID is available, display it; otherwise state that it was not returned and tell the user to say `list my agents` to find it.
2. For every role, follow [Chat communication initialization](../shared/chat-comm-init.md) and complete its communication setup/readiness check.
3. For an ASP with a resolved Agent ID, append this localized template at the bottom after communication setup:

   ```markdown
   Reply `Submit for listing review` to submit it to OKX.AI and earn rewards!
   ```

4. After an Evaluator identity is registered and communication setup is complete, ask whether the user wants to stake now. If yes, hand off to [Evaluator staking](../a2a/evaluator/staking.md); if no, finish registration.

Rules:

1. Keep the success message concise; do not add txHash or detail cards.
2. Evaluator staking is optional and always happens after registration and communication setup.


## CLI Reference

- [identity-cli-reference.md](identity-cli-reference.md)
