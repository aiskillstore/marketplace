---
name: fulfill-git-escrow
description: Fulfill a git escrow bounty by writing a solution or submitting an existing one. Use when the user wants to solve a test suite challenge, write code to pass tests, and claim a token reward. Requires the git-escrows CLI (npm i -g git-escrows).
compatibility: Requires git-escrows CLI, git, a configured .env with PRIVATE_KEY, and network access to an Ethereum RPC endpoint.
allowed-tools: Bash Read Write Edit Glob Grep
metadata:
  author: arkhai-io
  version: "1.0"
  openclaw:
    requires:
      bins:
        - git-escrows
        - git
      config:
        - .env
    primaryEnv: PRIVATE_KEY
    homepage: https://github.com/arkhai-io/git-commit-trading
    emoji: "\U0001F3AF"
---

# Fulfill Git Escrow

You are helping the user fulfill a git escrow bounty. This means submitting code that passes a failing test suite to claim the escrowed token reward.

There are two modes:
- **Mode A (Write + Submit)**: You write the solution code, commit it, and submit. This is the default when no `--solution-repo` is provided by the user.
- **Mode B (Submit Existing)**: The user already has a solution repo and commit. You just submit the fulfillment.

Determine the mode from the user's input:
- If they provide `--solution-repo`, use **Mode B**.
- Otherwise, use **Mode A**.

The escrow UID is always required.

## Step 1: Check CLI availability

Run `git-escrows --help` to verify the CLI is installed. If it fails, try `npx git-escrows --help` or `bunx git-escrows --help`. Use whichever works for all subsequent commands. If none work, tell the user to install with `npm i -g git-escrows`.

## Step 2: Check .env configuration

Check if a `.env` file exists in the current directory. If not, tell the user they need one and suggest running:
```
git-escrows new-client --privateKey "0x..." --network "sepolia"
```

## Step 3: Validate the escrow

Run `git-escrows list --verbose --format json` and find the escrow matching the provided UID. Confirm:
- The escrow exists and is **open**
- Note the test repo URL, test commit hash, reward amount, and oracle address

If no escrow UID was provided, ask the user for one. You can help them browse with `git-escrows list --status open`.

## Mode A: Write Solution + Submit

### A1: Understand the tests

Clone or read the test repository to understand what the tests expect:
1. Identify the test repo URL and commit from the escrow details
2. Clone it to a temporary location: `git clone <url> /tmp/escrow-tests-<uid> && cd /tmp/escrow-tests-<uid> && git checkout <commit>`
3. Read the test files to understand:
   - What functions/modules/APIs the tests import
   - What behavior they assert
   - What test framework is used
   - The project structure expected

### A2: Write the solution

In the **current working directory** (or a subdirectory the user specifies):
1. Create/modify files to implement the code that will make the tests pass
2. Follow the project structure the tests expect (e.g., if tests import from `src/math.ts`, create that file)
3. Include any necessary config files (package.json, Cargo.toml, etc.)
4. Ensure the test framework's dependencies are accounted for

### A3: Commit and get repo details

1. Stage and commit the solution: `git add -A && git commit -m "solution for escrow <uid>"`
2. Get the commit hash: `git rev-parse HEAD`
3. Get the remote URL: `git remote get-url origin`
   - If no remote exists, ask the user to push to a public git repo and provide the URL

### A4: Submit the fulfillment

```
git-escrows fulfill \
  --escrow-uid "<uid>" \
  --solution-repo "<repo-url>" \
  --solution-commit "<commit-hash>"
```

## Mode B: Submit Existing Solution

### B1: Gather parameters

From the user's input, extract:
- `--solution-repo`: The git repo URL with the solution
- `--solution-commit`: The commit hash of the solution

If either is missing, ask the user.

### B2: Submit the fulfillment

```
git-escrows fulfill \
  --escrow-uid "<uid>" \
  --solution-repo "<repo-url>" \
  --solution-commit "<commit-hash>"
```

## Step 4: Report results (both modes)

After successful execution:
- Report the **Fulfillment UID** prominently
- Explain that the oracle will now automatically test the solution
- Provide the collect command for after arbitration passes:
  ```
  git-escrows collect --escrow-uid <escrow-uid> --fulfillment-uid <fulfillment-uid>
  ```
- Suggest checking status with: `git-escrows list --verbose`

If the command fails, help diagnose the issue (escrow already fulfilled, wrong network, key not registered, etc.). If the user's git key isn't registered, suggest `git-escrows register-key`.
