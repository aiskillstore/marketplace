---
name: x402-api-paywall
description: 'Add stablecoin micropayment paywalls to FastAPI and Express routes using the HTTP 402 standard. Use when: Monetize specific high-cost API endpoints for AI agent consumption; Enforce per-request billing without managing complex user accounts; Integrate standard HTTP 402 handshakes into existing Node or Python backends.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: x402-api-paywall
compatibility: Optimized for Claude Code, Windsurf, Cursor, and Aider.
---

# X402 API Paywall

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/x402-api-paywall). Scripts, extension source, and templates from the original package are not in this folder.

## Turn your API into a Revenue Stream

Modern AI agents need a way to pay for the services they consume. The **x402 API Paywall** skill enables you to monetize your Express or FastAPI endpoints using the HTTP 402 "Payment Required" standard and stablecoins.

## What it does

This skill acts as a specialized developer assistant that integrates a middleware-based paywall into your existing codebase. Instead of manually writing complex web3 verification logic, the skill automatically implements the x402 handshake: it detects missing or invalid payment proofs, returns machine-readable 402 errors with payment requirements, and verifies proof-of-payment on the server side before granting access to your protected routes.

## Supported Tools & Frameworks

- **FastAPI (Python):** Implements via route dependencies for granular control.
- **Express (Node.js):** Implements via standard middleware mounting.
- **Stablecoin Ecosystem:** Built for USDC and other assets on networks like Base.
- **Verification:** Integrates with facilitator services for secure, server-side proof validation.

## Why use this over raw prompting?

Implementing a cryptographically secure paywall requires precise handling of headers, status codes, and external verification APIs. This skill understands the specific architecture of the x402 protocol, ensuring you don't leak "free" requests through logic errors or hardcode sensitive wallet information. It follows a non-destructive path, protecting only the routes you choose while keeping your existing business logic and public endpoints intact.

Built by Nex AI. More skills and info at nex-ai.be and slopsome.com.

## When to use

- Monetize specific high-cost API endpoints for AI agent consumption
- Enforce per-request billing without managing complex user accounts
- Integrate standard HTTP 402 handshakes into existing Node or Python backends
- Automate the setup of secure, server-side payment proof verification

## Known limitations

- Only supports FastAPI and Express.
- Requires external facilitator for server-side verification.
- Local tests use mocked proofs.

## Example

**Request**

Add an x402 paywall to the /generate-image route in my FastAPI app. Use Base Sepolia and charge 0.10 USDC.

**Result**

I've added the x402_middleware.py and updated your /generate-image route.

@app.post("/generate-image", dependencies=[Depends(require_payment)])
async def generate_image(request: ImageRequest):
    # Protected logic
    ...

Unauthenticated requests will now receive a 402 Payment Required response.

## Questions

### How does x402-api-paywall help monetize my existing API?

This skill automates the integration of the HTTP 402 "Payment Required" protocol into your API, allowing you to charge AI agents micro-amounts of stablecoins per request without building a billing system from scratch.

### Which programming languages and frameworks are compatible with this skill?

It is specifically designed for FastAPI (Python) and Express (Node.js) frameworks, providing native-style middleware and dependencies for these environments.

### What specific cryptocurrencies and networks does this paywall support?

The skill focuses on stablecoin ecosystems, specifically USDC, and is optimized for low-fee networks like Base to ensure micropayments remain cost-effective for both providers and consumers.

### What exactly is included in the purchase of this skill?

You will receive a specialized AI agent workflow capable of generating, configuring, and troubleshooting the x402 middleware logic within your specific codebase.

### Do I need to rewrite my entire API to use this paywall?

No, the skill is designed to be non-destructive; it allows you to wrap specific routes in a paywall while leaving your public endpoints and core business logic untouched.

### How does the skill ensure that a payment is actually valid before granting access?

The skill implements a secure server-side handshake that verifies cryptographically signed payment proofs against dedicated facilitators before any sensitive data is returned by your API.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
