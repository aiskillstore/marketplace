---
id: "cryptographic-randomness"
title: "Random sources for tokens and product choices"
category: "security"
summary: "Select randomness according to whether predictability or bias creates a material requirement."
aliases: ["csprng","secure token generation","random integers","entropy","unpredictable identifiers","öngörülemez şifre sıfırlama kodu","kriptografik rastgele sayı","gizli anahtar için entropi"]
decisions: [{"when":"A secret must resist guessing or prediction","use":"Use the platform cryptographic RNG, scoped lifetime and secure storage or verification.","tradeoff":"Stronger randomness does not replace rate limiting and authorization."},{"when":"Randomness is for a reproducible test or nonsecurity simulation","use":"Use an explicit seeded test generator and an unbiased selection scheme where needed.","tradeoff":"Deterministic sequences should remain isolated from security decisions."}]
checks: ["Check token generation uses the intended primitive and expiry rules.","Use deterministic fixtures for distribution-related logic without claiming tests prove unpredictability."]
sources: [{"title":"RFC 4086 randomness requirements","url":"https://www.rfc-editor.org/rfc/rfc4086"},{"title":"Node.js crypto random integers","url":"https://nodejs.org/api/crypto.html#cryptorandomintmin-max-callback"}]
related: ["music-shuffle"]
---

<!-- Generated record title. -->
# Random sources for tokens and product choices

## Scenario

A service produces password reset tokens and also rotates a list of featured articles. The two decisions have different consequences.

## Failure modes

A deterministic or general-purpose source can expose authentication tokens. Modulo reduction can bias selection, even if the input bytes are strong.

## Explain it simply

Use hard-to-guess randomness for access tokens, and select a suitable random source and rule for viewing experiences.

## Implementation guidance

Choose a random source based on predictability risk and distribution requirements. For reset tokens, generate with a platform cryptographic generator and protect the stored verifier with bounded lifetime. A seeded source can reproduce presentation tests. Use a bounded draw designed to preserve fairness where needed and test expiry and token replay separately from the random branch tests.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A secret must resist guessing or prediction** Use the platform cryptographic RNG, scoped lifetime and secure storage or verification. Stronger randomness does not replace rate limiting and authorization.
- **Randomness is for a reproducible test or nonsecurity simulation** Use an explicit seeded test generator and an unbiased selection scheme where needed. Deterministic sequences should remain isolated from security decisions.

## Verification

- Check token generation uses the intended primitive and expiry rules.
- Use deterministic fixtures for distribution-related logic without claiming tests prove unpredictability.

## Sources

- [RFC 4086 randomness requirements](https://www.rfc-editor.org/rfc/rfc4086)
- [Node.js crypto random integers](https://nodejs.org/api/crypto.html#cryptorandomintmin-max-callback)

## Related decisions

- [Shuffle semantics and perceived variety](../product/music-shuffle.md)

<!-- End generated record details. -->
