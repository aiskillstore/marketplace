---
name: make-git-escrow
description: Create a new git escrow bounty for a test suite. Use when the user wants to submit a challenge with escrowed token rewards for passing a failing test suite. Requires the git-escrows CLI (npm i -g git-escrows).
compatibility: Requires git-escrows CLI, a configured .env with PRIVATE_KEY, and network access to an Ethereum RPC endpoint.
allowed-tools: Bash Read Glob Grep
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
    emoji: "\U0001F512"
---

# Make Git Escrow

You are automating the creation of a git escrow bounty via the `git-escrows submit` CLI command. This locks ERC20 tokens in escrow as a bounty for someone who can make a failing test suite pass.

## Step 1: Check CLI availability

Run `git-escrows --help` to verify the CLI is installed. If it fails, try `npx git-escrows --help` or `bunx git-escrows --help`. Use whichever works for all subsequent commands. If none work, tell the user to install with `npm i -g git-escrows`.

## Step 2: Check .env configuration

Check if a `.env` file exists in the current directory. If not, tell the user they need one and suggest running:
```
git-escrows new-client --privateKey "0x..." --network "sepolia"
```

Verify it contains at least `PRIVATE_KEY` and `NETWORK` (or defaults to anvil). For base-sepolia and sepolia networks, contract addresses are auto-configured.

## Step 3: Gather parameters

You need all of these to run the submit command:

1. **`--tests-repo`** (required): Git repository URL containing the failing test suite.
   - If the user provided a URL as an argument, use that.
   - Otherwise, check if the current directory is a git repo and offer to use its remote URL.
   - Ask the user if neither is available.

2. **`--tests-commit`** (required): The commit hash of the test suite.
   - If using the current repo, detect HEAD with `git rev-parse HEAD`.
   - Otherwise ask the user.

3. **`--reward`** (required): Amount of tokens to escrow, in wei.
   - Ask the user. Help them convert if they give a human-readable amount (e.g., "1 USDC" = "1000000" for 6-decimal tokens, "1 ETH worth" = "1000000000000000000" for 18-decimal tokens).

4. **`--oracle`** (required): The Ethereum address of the oracle that will arbitrate.
   - Ask the user. Mention the public demo oracle on Sepolia: `0xc5c132B69f57dAAAb75d9ebA86cab504b272Ccbc`.

5. **`--arbiter`** (required): The arbiter contract address.
   - Ask the user. This is typically the TrustedOracleArbiter contract on their network.

6. **`--token`** (required): The ERC20 token contract address for the reward.
   - Ask the user.

Ask for any missing parameters, grouping related questions together when possible to minimize back-and-forth.

## Step 4: Execute

Run the submit command with all gathered parameters:

```
git-escrows submit \
  --tests-repo "<repo-url>" \
  --tests-commit "<commit-hash>" \
  --reward "<amount>" \
  --arbiter "<address>" \
  --oracle "<address>" \
  --token "<address>"
```

## Step 5: Report results

After successful execution:
- Report the **Escrow UID** prominently
- Show the full escrow details (attester, recipient, schema, reward, token, oracle)
- Provide the fulfill command that a solver would use:
  ```
  git-escrows fulfill --escrow-uid <UID> --solution-repo "<url>" --solution-commit "<hash>"
  ```
- Mention they can track status with: `git-escrows list --status open`

If the command fails, help diagnose the issue (insufficient balance, wrong network, missing approval, etc.).
