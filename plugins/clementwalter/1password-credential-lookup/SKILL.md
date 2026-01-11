---
name: 1password-credential-lookup
description: This skill should be used when agents need to log into websites, retrieve passwords, or access credentials. CRITICAL - always use find_credential with the website URL, never guess item names.
version: 2.0.0
---

# 1Password Credential Lookup

## CRITICAL: Use URL, Not Item Names

**WRONG:**

```text
get_credential(item_name="github.com")  ← NEVER DO THIS
get_credential(item_name="GitHub")      ← NEVER DO THIS
```

**RIGHT:**

```text
find_credential(url="github.com")                           ← CORRECT
find_credential(url="github.com", username="clementwalter") ← EVEN BETTER
```

## The One Rule

**When logging into a website, use `find_credential` with the domain.**

1Password items have arbitrary names that don't match URLs. The `find_credential` tool searches by the URL field stored in 1Password, which matches the website you're visiting.

## Tools (in order of preference)

### 1. `find_credential` - PRIMARY TOOL

Use this for ALL credential lookups:

```text
find_credential(url="github.com")
find_credential(url="linkedin.com", username="clement@example.com")
```

**Parameters:**

- `url` (required): Domain of website (e.g., "github.com", "twitter.com")
- `username` (optional): Filter by username when multiple accounts exist

**Returns:**

- Single match: `{"username": "...", "password": "...", "item_name": "..."}`
- Multiple matches: List of accounts to choose from
- No match: Error message

### 2. `list_items_for_url` - When unsure which account

```text
list_items_for_url(url="github.com")
```

Shows all accounts for a domain with usernames. Use before `find_credential` if you don't know which account to use.

### 3. `get_credential` - RARELY NEEDED

Only use if you have an exact item ID (like `ct2jszznlzlp7r7jeb53rhy5li`). Never pass URLs or guessed names.

## Workflow Example

When logging into github.com:

```text
# Step 1: Get credentials for the domain
find_credential(url="github.com", username="clementwalter")

# If multiple accounts and no username filter:
# → Returns list: [{"username": "work@company.com"}, {"username": "personal@gmail.com"}]
# → Pick one and retry with username filter

# Step 2: Use returned credentials to fill login form
```

## Domain Aliases

These domains are treated as equivalent:

- `x.com` ↔ `twitter.com`

## Error Handling

| Error                  | Solution                           |
| ---------------------- | ---------------------------------- |
| "No items found"       | Check domain spelling              |
| "Multiple items found" | Add `username` parameter to filter |
| "op CLI not installed" | User needs 1Password CLI           |
| "Timed out"            | User needs to run `op signin`      |

## Anti-Patterns

**NEVER do these:**

- `get_credential(item_name="github.com")` - URL is not an item name
- `get_credential(item_name="GitHub")` - Guessed names don't work
- `get_credential(item_name="my github")` - Item names are arbitrary

**ALWAYS do this:**

- `find_credential(url="github.com")` - Search by the website URL
