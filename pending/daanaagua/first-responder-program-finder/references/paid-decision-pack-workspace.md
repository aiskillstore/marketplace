# Paid Decision Pack and workspace

## Entry points

Main paths:

- `/decision-pack/`
- `/account/`
- `/account/workspace/`

Auth-related paths:

- `/account/sign-in/`
- `/account/register/`
- `/account/forgot-password/`
- `/account/reset-password/`
- `/account/verify-email/`

## When to move into the paid layer

Use the paid layer when the user needs any of the following:

- local or county program details
- employer-assisted paths
- public employee or pension-related paths
- specialty or conditional research details
- full research-record access instead of teasers
- scenario saving and comparison tools
- conflict checks
- question kit
- action checklist

## Sign-in and account state

Anonymous user:

- header entry should be `Sign in`
- an auth modal may appear first

Signed-in but not purchased:

- header entry should usually be `Account`
- the user should go to `/account/`

Active paid user:

- header entry should usually be `Workspace`
- the user should go to `/account/workspace/`

## What the paid user can access

The paid workspace can include:

- `Research Vault`
- `Saved scenarios`
- `Saved programs`
- `Saved opportunities`
- `Comparisons`
- `Conflict checks`
- `Question kit`
- `Action checklist`
- `Reminder settings`

## What the Research Vault is

The Research Vault is not just a “verified program list”.

It can include:

- `Current opportunities`
- `Needs judgment`
- `Historical / blocked`
- `Research notes`

## How an agent should explain paid records

Safe framing:

- these are deeper research records
- they include local, specialty, employer, pension, conditional, and historical layers
- some records are cautionary and require source review

Unsafe framing:

- every record is a currently open verified program
- every record is directly actionable for every user

## Recommended paid-user flow

1. Open `/account/workspace/`
2. choose a state
3. load the `Research Vault`
4. save programs and opportunities
5. review comparisons
6. review conflict checks
7. review question kit and action checklist

## Recommended guidance pattern

If the user starts from the free layer:

- answer the verified statewide question first
- then mention whether deeper opportunities exist
- if the user truly needs local/specialty detail, direct them into the paid workspace and Research Vault

