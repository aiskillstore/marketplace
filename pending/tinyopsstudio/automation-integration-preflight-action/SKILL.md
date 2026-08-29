---
name: automation-integration-preflight-action
description: Audit a public webpage for automation and integration readiness through the TinyOps paid x402 service. Use for evidence-backed readiness findings, prioritized integration risks, or a structured acceptance checklist. Do not use for private or authenticated pages, form submission, or security testing.
license: MIT
version: 1.0.1
author: tinyopsstudio
tags: [automation, x402, integration, workflow, agent-tools]
---

# Automation Integration Preflight

Use the TinyOps x402 service to inspect a public HTTP or HTTPS page without executing its JavaScript, submitting forms, authenticating, or bypassing access controls.

Inspect the wallet-free static sample at `GET https://x402-preflight.tinyopsstudio.com/demo` before deciding whether a paid result fits the task. The demo always represents `https://example.com/` and does not inspect a caller-supplied target.

## Choose the result

- Use `POST https://x402-preflight.tinyopsstudio.com/analyze` for a readiness analysis. The published price is USD 0.03.
- Use `POST https://x402-preflight.tinyopsstudio.com/acceptance-pack` for evidence, launch gates, acceptance tests, and a prioritized remediation backlog. The published price is USD 0.10.

Send JSON containing a public URL:

```json
{"url":"https://example.com"}
```

## Confirm payment safely

Treat the prices above as discovery information, not authority to spend.

1. Read `https://x402-preflight.tinyopsstudio.com/openapi.json` and make an unpaid request to the selected endpoint to obtain its current HTTP 402 payment requirements.
2. Verify the live amount, asset, network, payee, and resource match the intended request. Stop on any mismatch or unexpected redirect.
3. If the user has not already authorized this exact purchase, state the total price and request confirmation immediately before payment.
4. Use only an already configured x402-capable client or wallet that the user has authorized. Never request, reveal, store, or reconstruct private keys, seed phrases, personal passwords, or payment credentials.
5. Submit one paid request. Do not retry a paid request automatically when settlement or delivery is ambiguous.

If no authorized payment client is available, return the verified payment requirements and explain that the paid request was not made.

## Protect the target

- Accept only a public `http://` or `https://` URL.
- Do not send private-network URLs, credential-bearing URLs, secrets, session tokens, unpublished customer data, or authenticated page content.
- Do not present the service as a vulnerability scanner, browser automation tool, or proof that an integration works end to end.

## Return useful evidence

Summarize the service response with the target, selected mode, readiness result, strongest evidence, prioritized gaps, and practical next actions. Preserve uncertainty and distinguish observed page evidence from recommendations. Include the raw structured response when the user requests an auditable artifact.
