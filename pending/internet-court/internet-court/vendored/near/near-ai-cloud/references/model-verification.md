# Model Verification

Verify that a NEAR AI model is running inside genuine TEE hardware. Two main steps:

1. [Request model attestation](#request-model-attestation) from NEAR AI Cloud
2. [Verify the attestation](#verify-gpu-attestation-nvidia-nras) using NVIDIA NRAS and Intel TDX

> See working implementations:
> - [Verification Example](https://github.com/near-examples/nearai-cloud-verification-example) (easy-to-follow)
> - [Full Verifier](https://github.com/nearai/nearai-cloud-verifier) (complete)

---

## Request Model Attestation

```
GET https://cloud-api.near.ai/v1/attestation/report?model={model_name}&signing_algo=ecdsa&nonce={nonce}
```

**Parameters:**

- `model` — Model name (e.g. `deepseek-ai/DeepSeek-V3.1`)
- `signing_algo` — `ecdsa` or `ed25519`
- `nonce` — Random 64-char hex string (32 bytes). Optional but recommended for freshness/replay prevention

### curl

```bash
NONCE=$(openssl rand -hex 32)

curl "https://cloud-api.near.ai/v1/attestation/report?model=deepseek-ai/DeepSeek-V3.1&signing_algo=ecdsa&nonce=${NONCE}" \
  -H 'accept: application/json'
```

### JavaScript

```js
import crypto from 'crypto';

const MODEL_NAME = 'deepseek-ai/DeepSeek-V3.1';
const nonce = crypto.randomBytes(32).toString('hex');

const response = await fetch(
  `https://cloud-api.near.ai/v1/attestation/report?model=${MODEL_NAME}&signing_algo=ecdsa&nonce=${nonce}`,
  { headers: { 'accept': 'application/json' } }
);

const data = await response.json();
// data.model_attestations[0].signing_address  — TEE public key
// data.model_attestations[0].nvidia_payload   — GPU attestation for NVIDIA NRAS
// data.model_attestations[0].intel_quote      — CPU attestation for Intel TDX
```

### Python

```python
import requests
import secrets

MODEL_NAME = 'deepseek-ai/DeepSeek-V3.1'
nonce = secrets.token_hex(32)

response = requests.get(
    f'https://cloud-api.near.ai/v1/attestation/report?model={MODEL_NAME}&signing_algo=ecdsa&nonce={nonce}',
    headers={'accept': 'application/json'}
)

data = response.json()
# data['model_attestations'][0]['signing_address']  — TEE public key
# data['model_attestations'][0]['nvidia_payload']   — GPU attestation for NVIDIA NRAS
# data['model_attestations'][0]['intel_quote']      — CPU attestation for Intel TDX
```

### Response Structure

```json
{
  "model_attestations": [
    {
      "signing_address": "0x...",
      "nvidia_payload": "{ ... }",
      "intel_quote": "..."
    }
  ]
}
```

- `model_attestations` — List of attestations from all GPU nodes serving this model (multiple TEE nodes may be active)
- `signing_address` — Public key generated inside the TEE. Used to sign chat responses. **This is the key binding** — verify it matches the signer of chat message signatures
- `nvidia_payload` — JSON object to submit to NVIDIA NRAS for GPU verification
- `intel_quote` — TDX quote for Intel CPU TEE verification

---

## Verify GPU Attestation (NVIDIA NRAS)

Submit the `nvidia_payload` to NVIDIA's Remote Attestation Service:

```bash
curl -X POST https://nras.attestation.nvidia.com/v3/attest/gpu \
  -H "accept: application/json" \
  -H "content-type: application/json" \
  -d '<nvidia_payload from model attestation>'
```

> API docs: https://docs.api.nvidia.com/attestation/reference/attestmultigpu_1

### NRAS Response Structure

The response is a **two-part array**:

```json
[
  ["JWT", "<overall-attestation-jwt>"],
  {"GPU-0": "<gpu-specific-jwt>", "GPU-1": "<gpu-specific-jwt>"}
]
```

- **Part 1** `["JWT", "..."]` — Overall platform attestation JWT
- **Part 2** `{"GPU-0": "..."}` — Per-GPU attestation JWTs, keyed by GPU identifier

Both are standard JWTs (header.payload.signature). Decode with [jwt.io](https://jwt.io), [jose](https://www.npmjs.com/package/jose), or any JWT library.

### Overall JWT Payload

```json
{
  "sub": "NVIDIA-PLATFORM-ATTESTATION",
  "x-nvidia-ver": "2.0",
  "iss": "https://nras.attestation.nvidia.com",
  "x-nvidia-overall-att-result": true,
  "submods": {
    "GPU-0": ["DIGEST", ["SHA-256", "02fc2f1873bdf89cee4f3e43c57e17c248518702d8dfc3706a7b7fe8036e93d0"]]
  },
  "eat_nonce": "4d6e0c49321d22daa9bd7fc2205e381f9506c20e77dd5082ecf5e124ec0f4618",
  "exp": 1756172526,
  "iat": 1756168926
}
```

**Key fields:**

- `x-nvidia-overall-att-result` — Must be `true` for attestation to pass
- `eat_nonce` — **Must match your request nonce** (prevents replay attacks)
- `submods` — SHA-256 digests for each GPU, keyed by identifier
- `exp` / `iat` — Token expiration and issuance timestamps

### Per-GPU JWT Payload (GPU-0)

```json
{
  "iss": "https://nras.attestation.nvidia.com",
  "eat_nonce": "4d6e0c49321d22daa9bd7fc2205e381f9506c20e77dd5082ecf5e124ec0f4618",
  "ueid": "642960189298007511250958030500749152730221142468",
  "hwmodel": "GH100 A01 GSP BROM",
  "dbgstat": "disabled",
  "secboot": true,
  "measres": "success",
  "x-nvidia-gpu-driver-version": "570.133.20",
  "x-nvidia-gpu-vbios-version": "96.00.CF.00.02",
  "x-nvidia-gpu-driver-rim-schema-validated": true,
  "x-nvidia-gpu-driver-rim-signature-verified": true,
  "x-nvidia-gpu-driver-rim-cert-validated": true,
  "x-nvidia-gpu-driver-rim-fetched": true,
  "x-nvidia-gpu-driver-rim-measurements-available": true,
  "x-nvidia-gpu-vbios-rim-schema-validated": true,
  "x-nvidia-gpu-vbios-rim-signature-verified": true,
  "x-nvidia-gpu-vbios-rim-cert-validated": true,
  "x-nvidia-gpu-vbios-rim-fetched": true,
  "x-nvidia-gpu-vbios-rim-measurements-available": true,
  "x-nvidia-gpu-vbios-index-no-conflict": true,
  "x-nvidia-gpu-attestation-report-parsed": true,
  "x-nvidia-gpu-attestation-report-nonce-match": true,
  "x-nvidia-gpu-attestation-report-cert-chain-validated": true,
  "x-nvidia-gpu-attestation-report-signature-verified": true,
  "x-nvidia-gpu-arch-check": true,
  "x-nvidia-attestation-warning": null
}
```

**What to verify:**

| Field | Expected | Why |
|-------|----------|-----|
| `eat_nonce` | Matches your request nonce | Freshness / anti-replay |
| `secboot` | `true` | Secure boot is active |
| `dbgstat` | `"disabled"` | Debug mode is off |
| `measres` | `"success"` | Measurements passed |
| `hwmodel` | e.g. `"GH100 A01 GSP BROM"` | Confirms GPU hardware model |
| `ueid` | Present | Unique equipment identifier for the GPU |
| All `x-nvidia-*-verified` fields | `true` | RIM signatures, certs, attestation report all valid |
| `x-nvidia-attestation-warning` | `null` | No warnings |

---

## Verify CPU Attestation (Intel TDX)

Verify the `intel_quote` from the model attestation using the [`dcap-qvl`](https://github.com/Phala-Network/dcap-qvl) library. This verifies:

- CPU TEE measurements are valid
- The quote is authentic and signed by Intel
- The TEE environment is genuine

Alternatively, paste the `intel_quote` at the [TEE Attestation Explorer](https://proof.t16z.com/) for manual verification.

### Verify TDX Report Data

The TDX report data validates:

- The `signing_address` is **cryptographically bound** to the hardware TEE
- The request `nonce` is embedded in the report

This is the **GPU-CPU binding** — it proves the signing key was generated inside the Intel TDX environment, which in turn is connected to the NVIDIA TEE GPUs. Without this step, an attacker could present valid GPU attestation but use a signing key from outside the TEE.

### Verify Compose Manifest

The attestation response includes Docker compose manifest information in the `info` field:

1. Extract the Docker compose manifest from the attestation
2. Calculate the SHA-256 hash of the compose manifest
3. Compare with the `mr_config` measurement from the verified TDX quote
4. Verify they match — this proves the exact container configuration running in the TEE

---

## Common Pitfalls

### 1. Not verifying the nonce

The `eat_nonce` in the NRAS response **must match** the nonce you sent in the attestation request. Skipping this check allows replay attacks — an attacker could present a stale but valid attestation.

Always generate a fresh random nonce per verification:

```js
const nonce = crypto.randomBytes(32).toString('hex');  // 64 hex chars
```

### 2. Only checking the overall result

Don't just check `x-nvidia-overall-att-result: true` on the overall JWT and call it done. You should also verify:

- Per-GPU JWT fields: `secboot`, `dbgstat`, all `x-nvidia-*-verified` fields
- `eat_nonce` match on both overall and per-GPU JWTs
- JWT `exp` (expiration) is still in the future

### 3. Ignoring JWT expiration

NRAS JWTs have short lifetimes (typically ~1 hour). Check the `exp` field and re-attest if expired.

### 4. Skipping TDX verification (GPU-CPU binding)

Verifying only the `nvidia_payload` (GPU attestation) is **not sufficient**. You must also verify the `intel_quote` (CPU/TDX attestation) and confirm the `signing_address` is bound in the TDX report data. This is what ties the GPU to the CPU TEE and prevents an attacker from using valid GPU attestation with a compromised signing key.

### 5. Not binding signing_address to chat signatures

After attestation, when you verify chat message signatures, the recovered signer address **must match** the `signing_address` from the attestation. This is the complete chain of trust:

```
GPU hardware (NRAS) → CPU TEE (TDX) → signing_address (bound in TDX report) → chat signature
```

---

## Full Verification Checklist

1. Generate random nonce (64 hex chars)
2. Request model attestation with nonce
3. Submit `nvidia_payload` to NVIDIA NRAS
4. Decode overall JWT — verify `x-nvidia-overall-att-result: true` and `eat_nonce` matches
5. Decode per-GPU JWTs — verify `secboot: true`, `dbgstat: "disabled"`, all `x-nvidia-*-verified: true`, `eat_nonce` matches
6. Verify `intel_quote` with `dcap-qvl` or TEE Explorer
7. Verify TDX report data binds the `signing_address` and nonce
8. Verify compose manifest hash matches `mr_config` from TDX quote
9. Save `signing_address` — use it later to verify chat message signatures
