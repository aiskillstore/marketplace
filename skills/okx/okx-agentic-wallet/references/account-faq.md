# Account / Login FAQ

## FAQ

> Load when the user asks about: Apple-account wallet differing from the OKX Wallet App / "missing" balance; renaming a wallet or account; or how transaction signing works (TEE).

Reply with the matching answer **verbatim**; do not improvise.

### Apple cross-app wallet mismatch / "missing" balance

Trigger: the user logged in with Apple (`loginType` = `apple`) or mentions Apple, and asks why their wallet differs from the OKX Wallet App, or why their balance is gone / different.

> Because Apple Sign-In is subject to provider restrictions, it is currently integrated only with the OKX App account system and is not yet interoperable with the OKX Wallet App account system. The same Apple account may therefore map to different wallets in the two apps; a balance that looks different is usually because you are signed in to a different account — your assets are not lost.

### Change wallet / account name

Trigger: the user wants to rename their wallet or account.

> The wallet name syncs across ends and devices, but can only be changed on the App or browser-extension end (it syncs when the sync toggle is on). Changing the wallet name is not supported on the Agent end.

### Signing — why the agent can sign autonomously (TEE)

Trigger: the user asks why the agent can/can't sign transactions, says local signing is required, or asks how signing works.

> OKX Agentic Wallet uses TEE (Trusted Execution Environment) for transaction signing. The private key is generated and stored inside a server-side secure enclave — it never leaves the TEE.
