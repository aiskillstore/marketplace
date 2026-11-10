# x402socks skill

An [Agent Skill](https://agentskills.io) for buying short-lived anonymous proxy
egress with USDC on Base through [x402](https://x402.org). TLS HTTP CONNECT is
the default transport; SOCKS5 and plaintext CONNECT are opt-in.

The skill teaches an agent to quote a package, get approval for an exact amount,
complete the x402 v2 payment, store the one-time token safely, route traffic
through a chosen exit, and prove that the egress IP actually changed.

## Wallet access (required)

The agent cannot use this skill without a wallet it can operate. There is no free
tier, and no account credit: without wallet access there is no way to buy a
package.

1. **An EVM-compatible wallet funded with USDC on Base.** The cheapest package is
   $1.00 for 6 hours / 1 GB. USDC on Base is
   `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`. No ETH is needed for the x402
   purchase because the facilitator submits the EIP-3009 transfer; a manual
   `cast send` needs ETH for gas.
2. **A signing method the agent can use non-interactively.** Use a Foundry
   encrypted keystore (`cast wallet import <name> --interactive`, then
   `--keystore <path> --password-file <0600 file>`), a hardware wallet, or a
   signer configured in the x402 client. Do not paste a raw private key into
   chat.
3. **`cast` and a free Base RPC for low-volume checks.** For example:

   ```bash
   export BASE_RPC=https://mainnet.base.org
   export USDC=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
   export KEYSTORE="$HOME/.foundry/keystores/x402socks"
   export KEYPASS="$HOME/.config/x402socks/keystore.pass"   # mode 600
   export ADDR="$(cast wallet address --keystore "$KEYSTORE" --password-file "$KEYPASS")"
   cast call "$USDC" "balanceOf(address)(uint256)" "$ADDR" --rpc-url "$BASE_RPC"
   ```

   The result is atomic USDC (6 decimals), so `1000000` is $1.00. Other free
   public Base RPCs: `https://base-rpc.publicnode.com`, `https://1rpc.io/base`,
   `https://base.drpc.org`.

**Never print or output the private key in a terminal, log, chat, or commit, and
never pass it as a command argument.** Use an encrypted keystore or hardware
wallet; keep the keystore and password file at mode `0600`. See
[`references/wallet.md`](references/wallet.md) for manual sends, EIP-712
signing, and recovery.

### Other requirements

- An Agent Skills client that can run shell commands (Claude Code, Codex,
  Cursor, GitHub Copilot, OpenCode, and others).
- `curl`, plus `python3` for the helper.
- Node.js + npm for the TypeScript x402 client, or Python 3.10+ with `uv` for
  the Python client.

No account, email, card, or API key.

## Install

```bash
npx skills add X402Socks/skill
```

Or copy this folder to your client's skills directory:

```bash
cp -r skills/x402socks ~/.claude/skills/       # Claude Code
cp -r skills/x402socks ~/.agents/skills/       # OpenCode and other clients
```

## What is here

| Path | Purpose |
| --- | --- |
| `SKILL.md` | The skill itself: triggers, wallet requirement, spending rule, buy flow, routing, credential rules. |
| `references/wallet.md` | `cast` recipes: address, USDC balance, manual send, EIP-712 signing, key handling. |
| `references/payments.md` | x402 v2 flow, guarded TypeScript/Python clients, recovery. |
| `references/endpoints.md` | Endpoints, client snippets, safe credential handling. |
| `references/troubleshooting.md` | Symptom-to-cause table for 401/402/407/connection errors. |
| `scripts/x402socks.sh` | Helper: health, nodes, quote, status, validate, rotate, test, recover. |
| `assets/purchase-approval.md` | Template for recording the approved amount before spending. |

## Safety defaults

- **Spending:** the skill requires explicit approval for an exact amount and
  enforces it against the live 402 challenge before signing.
- **Credentials:** the helper reads the token from a `0600` file
  (`~/.config/x402socks/token`) and passes it to curl on stdin, so it never
  appears in the process list. Rotation and recovery save the replacement token
  instead of printing it. Endpoint overrides must be `https://`; a plaintext
  override is refused before the token is read, and credential transfers are
  restricted to HTTPS. `X402SOCKS_ALLOW_INSECURE_API=1` is for a trusted local
  test only.
- **Transport:** TLS HTTP CONNECT on port 3129 is the default where the exit
  offers it (`eu-north1`, `asia-central2`, `asia-west1`). SOCKS5 and plaintext
  HTTP CONNECT do not encrypt proxy authentication and require
  `X402SOCKS_ALLOW_PLAINTEXT=1`.

## Links

- Repository: https://github.com/X402Socks/skill
- Directory: https://skills.sh/X402Socks/skill
- Service: https://x402socks.com

MIT. Maintained by the x402socks project.
