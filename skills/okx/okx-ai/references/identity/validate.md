# ASP Listing Validation

## Module Description

Validate ASP identity and service information before create or update.


## Flow
### When to run

- **Registration:** validate the full identity and service set after the user confirms all services.
- **Update:** validate after the user confirms all changes, using final identity values and changed
  create/update services. Skip delete-only updates.

Validate once per flow, never inside a service loop or before final confirmation.

### Workflow

#### 1. Run CLI validation

Call `validate-listing` once with the applicable identity and service information, then read `pass`
and `findings[]` from the result.

##### CLI reference

```bash
onchainos agent validate-listing \
  --role <role> \
  [--name <name>] \
  [--description <text>] \
  [--service '<json-array>']
```

- Each finding contains `field`, `severity`, `message`, and a diagnostic `code`.
- Preserve CLI severities and never expose `code`.

#### 2. Apply semantic validation

Keep every CLI finding and add only checks that require semantic judgment:

- **Agent name:** require a brand, not a personal/public-figure name or substring.
- **Agent description:** require one sentence based on the user's supplied information; do not
  invent capabilities or metrics.
- **Service name:** enforce the noun-phrase rule in the
  [`serviceName` contract](service-contract.md#servicename).
- **Service description:** follow the
  [`serviceDescription` contract](service-contract.md#servicedescription). Treat a missing A2A core
  capability as advisory; block any A2MCP violation and help the user revise it to satisfy the
  contract.

Use only these rules for semantic severity and exceptions; never restate or reinterpret CLI rules.

#### 3. Merge findings and resolve

- Merge CLI and semantic findings, preserve severity, de-duplicate by `(field,message)`, and
  localize messages. Map dotted `field` values to card rows, bold affected name rows, and never show
  diagnostic `code`.
- If there are no findings, say QA passed.
- If a required value is missing or no correction can be derived safely, ask the user to provide it.
- Otherwise, propose only corrections derived from the user's words. Label semantic drafts
  `drafted from your words — please review`, then offer one localized choice set:
  - **Any blocker:** `1 Use the drafted corrections / 2 I'll revise`.
  - **Advisory only:** `1 Skip and keep original / 2 Use suggestion / 3 I'll revise`.
- Apply only the user's selection, then redraw. If the user chooses to revise, recollect first.
