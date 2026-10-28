# Manage an Agent's Marketplace Listing

## Module Description

Use this reference only when the user explicitly asks to publish or unpublish an agent.


## Flow
### Commands

Publish an ASP agent:

```bash
onchainos agent activate --agent-id <agentId> --preferred-language <BCP-47>
```

Unpublish an agent:

```bash
onchainos agent deactivate --agent-id <agentId>
```

### Constraints

1. **Agent ID.** Use an ID supplied by the user or returned in the current
   structured result; never infer it from an agent name.
2. **Review language (publish only).** Pass the user's preferred language as
   a BCP-47 tag, such as `zh-CN`. It controls backend listing-review messages.

### Result

- `blockType: 1`: explain that only ASP agents can be listed.
- `submitApproval[0].success: true`: localize and render the complete
  `submissionNotice` without summarizing, preserving the Agent Name.
- `activate.approvalStatus: 2`: say the listing is under review.
- `activate.success: true`: say the agent is published.
- Deactivation with `success: true`: say the agent is unpublished.
- Otherwise, present the CLI error or failure result without retrying,
  polling, or performing a follow-up read.
