# Cryptography Security Checklist

## Primitives & Libraries

- [ ] Use well-reviewed crypto libraries (libsodium, ring, RustCrypto)
- [ ] No custom crypto implementations
- [ ] AEAD for encryption (AES-GCM, ChaCha20-Poly1305)
- [ ] Ed25519 or ECDSA P-256 for signatures
- [ ] X25519 or ECDH P-256 for key exchange
- [ ] SHA-256/SHA-3/BLAKE3 for hashing
- [ ] Algorithm agility without downgrade attacks

## Randomness

- [ ] CSPRNG only (no `rand()`, no time seeds)
- [ ] System entropy source (/dev/urandom, getrandom)
- [ ] Verify RNG initialization before use
- [ ] No predictable seeds in tests that leak to prod

## Nonces & IVs

- [ ] Unique nonce per encryption
- [ ] Counter mode: never reuse (key, nonce) pair
- [ ] Random nonces: sufficient size (96+ bits for AES-GCM)
- [ ] Nonce misuse-resistant modes for high-risk contexts (AES-GCM-SIV)

## Key Management

- [ ] Keys generated from CSPRNG
- [ ] Key derivation: HKDF with domain separation
- [ ] Key rotation policy defined
- [ ] Separate keys per purpose (encryption ≠ signing ≠ MAC)
- [ ] Zeroize keys after use in memory

## Passwords

- [ ] Argon2id (preferred) or bcrypt/scrypt
- [ ] Per-user random salt (16+ bytes)
- [ ] Appropriate cost factor (tune for hardware)
- [ ] No password length limits below 64 chars
- [ ] Check against breach databases

## Signatures

- [ ] Domain separation in signed messages
- [ ] Include context/purpose in signed data
- [ ] Replay protection (nonce, timestamp, sequence)
- [ ] Verify signature before using data

## Hashing

- [ ] Domain separation prefix for different uses
- [ ] Length extension attack awareness (use HMAC or SHA-3)
- [ ] Collision resistance where needed

## Constant-Time Operations

- [ ] Secret-dependent branches avoided
- [ ] Secret-dependent array indexing avoided
- [ ] Use ct_eq for comparisons
- [ ] Timing attack testing where applicable

## Protocol Design

- [ ] Explicit transcript binding
- [ ] Version field for future changes
- [ ] Downgrade attack prevention
- [ ] Forward secrecy where appropriate

## Common Pitfalls

| Issue                      | Problem         | Fix                     |
| -------------------------- | --------------- | ----------------------- |
| ECB mode                   | Pattern leakage | Use AEAD                |
| Unauthenticated encryption | Malleability    | Use AEAD                |
| Reused nonce               | Key recovery    | Counter or random nonce |
| strcmp for MAC             | Timing attack   | Constant-time compare   |
| MD5/SHA1                   | Broken          | Use SHA-256+            |
| Raw RSA                    | Padding oracle  | Use RSA-OAEP/PSS        |
