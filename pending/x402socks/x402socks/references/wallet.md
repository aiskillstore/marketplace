# Wallet access and signers

This skill needs a wallet the agent can use through a signer. This page covers
non-secret setup: address, USDC balance, signing paths, and key handling. It
never asks for a private key in chat.

## Required

- An EVM-compatible wallet on **Base** funded with **USDC**
  (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`).
- A signer the agent can call without a human typing a key each time:
  - a browser with a configured wallet and an injected EIP-1193 signer;
  - a signer-owned store or x402 client signer (`@x402/fetch` + `viem`, or the
    Python `x402` package);
  - a Foundry encrypted keystore, hardware wallet, KMS, or HSM.
- `python3` and `curl` for the helper. `cast` is optional and only needed for the
  manual recipes below.
- A Base RPC is optional for low-volume balance checks.

The x402 purchase is an EIP-3009 `TransferWithAuthorization` signature. The
facilitator submits the transfer, so the payer needs USDC but **no ETH** for the
purchase. A manual on-chain send needs ETH for gas.

If a browser wallet is used, run it in an operator-provisioned browser profile.
The agent must not read browser storage, export the key, or paste key material
into chat. Bind the actual signer object to the approved public address before
signing.

## Never do this

- `cast ... --private-key "$RAW_KEY"` or `--private-key "$(cat keyfile)"`. The
  key becomes a process argument visible to `ps`, shell history, and telemetry.
- `echo "$PRIVATE_KEY"`, `cat keyfile`, `set -x`, or any command that prints the
  key.
- Put the key in a URL, an exported variable that reaches logs, a commit, a chat,
  or a transcript.
- Use a hot wallet holding more than you are willing to spend.

Use a signer-owned store, injected wallet, `--account`, `--keystore` plus
`--password-file`, `--ledger`, or `--trezor`. Keep any local key material at mode
`0600`. Mode `0600` limits access to the same OS user, so any code running as
that user, including an agent with shell access, can read it. Give the agent
access only to a signer intended for this job.

## Free Base RPCs (low volume)

These are public and rate-limited. Use them for read-only calls and occasional
transactions. A public RPC operator can associate the queried address with the
caller source IP and request metadata. Use an operator-controlled RPC when that
is not acceptable.

- `https://mainnet.base.org`
- `https://base-rpc.publicnode.com`
- `https://1rpc.io/base`
- `https://base.drpc.org`

## Approval verification needs no wallet key

`scripts/x402socks.sh verify-approval` uses the bundled
`scripts/eip191_verify.py`. It is pure Python, reads the message and signature
from private files, and rejects a signature that does not recover to the pinned
operator address. No Foundry install and no wallet key are needed. An operator
may set `X402SOCKS_EIP191_VERIFIER` to an approved executable.

## Optional `cast` address and balance recipes

Use these only when a keystore signer is available:

```bash
export BASE_RPC=https://mainnet.base.org
export USDC=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
export KEYSTORE="$HOME/.foundry/keystores/x402socks"
export KEYPASS="$HOME/.config/x402socks/keystore.pass"   # mode 600

cast wallet address --keystore "$KEYSTORE" --password-file "$KEYPASS"
cast call "$USDC" "balanceOf(address)(uint256)" \
  "$(cast wallet address --keystore "$KEYSTORE" --password-file "$KEYPASS")" \
  --rpc-url "$BASE_RPC"
```

The balance is atomic USDC with 6 decimals: `1000000` is $1.00. Check it before
quoting a package.

## Optional manual USDC send, not the x402 flow

Use this only if the service tells you to pay by transfer. It needs ETH for gas
and does **not** create a proxy token.

```bash
cast send "$USDC" "transfer(address,uint256)" \
  0xRECIPIENT 1000000 \
  --keystore "$KEYSTORE" --password-file "$KEYPASS" --rpc-url "$BASE_RPC"
```

Confirm the recipient and amount with the user first.

## Signing the x402 authorization

The x402 `exact` EVM scheme signs EIP-712 typed data for EIP-3009. Prefer the
x402 client or injected wallet. If manual `cast` signing is used, build typed
data from the **live 402 challenge** and write it to a mode `0600` file:

```json
{
  "types": {
    "EIP712Domain": [
      { "name": "name", "type": "string" },
      { "name": "version", "type": "string" },
      { "name": "chainId", "type": "uint256" },
      { "name": "verifyingContract", "type": "address" }
    ],
    "TransferWithAuthorization": [
      { "name": "from", "type": "address" },
      { "name": "to", "type": "address" },
      { "name": "value", "type": "uint256" },
      { "name": "validAfter", "type": "uint256" },
      { "name": "validBefore", "type": "uint256" },
      { "name": "nonce", "type": "bytes32" }
    ]
  },
  "primaryType": "TransferWithAuthorization",
  "domain": {
    "name": "USD Coin",
    "version": "2",
    "chainId": 8453,
    "verifyingContract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
  },
  "message": {
    "from": "0x...",
    "to": "0x...",
    "value": "1000000",
    "validAfter": "0",
    "validBefore": "1799999999",
    "nonce": "0x...32-bytes..."
  }
}
```

```bash
umask 077
# Write the JSON above to typed-data.json (mode 600), then:
cast wallet sign --data --from-file typed-data.json \
  --keystore "$KEYSTORE" --password-file "$KEYPASS"
```

Before signing, require exactly one live 402 `accepts[]` option. Confirm its
`name`, `version`, `chainId`, `verifyingContract`, `to`, and `value` equal the
approved terms. Abort on any difference. Use a fresh random 32-byte `nonce`.
Keep `validBefore` in the future and within `maxTimeoutSeconds`. Put the
signature and authorization into the x402 v2 payload and retry the same URL with
`PAYMENT-SIGNATURE` as described in `payments.md`.

## Optional recovery signature with `cast`

Recovery uses EIP-191 `personal_sign`, not EIP-712.
`scripts/x402socks.sh recover-message <tx_hash>` prints the exact bytes and the
`issued_at` to reuse. Sign with the paying wallet and feed the signature to
`recover <tx_hash> <issued_at>` on stdin:

```bash
cast wallet sign "<message>" \
  --keystore "$KEYSTORE" --password-file "$KEYPASS"
```

Never put the signature or a private key in argv. The helper sends the timestamp
you pass, so use the exact one returned by `recover-message`.

## If there is no wallet access

There is no way to buy a package. The service has no free tier and no account
credit. Ask the operator for a funded wallet and a usable signer before
continuing. Missing `cast` is not a blocker.
