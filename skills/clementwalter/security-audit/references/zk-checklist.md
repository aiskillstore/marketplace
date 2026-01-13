# ZK Circuit Security Checklist

## Constraint Soundness

- [ ] All witness values fully constrained
- [ ] No "free" variables that attacker can set arbitrarily
- [ ] Boundary constraints at input/output
- [ ] Intermediate values properly bounded
- [ ] Copy constraints where values must match

## Range Constraints

- [ ] Explicit range checks on all user inputs
- [ ] Field overflow awareness (values wrap at p)
- [ ] Bit decomposition verified (sum equals original)
- [ ] Negative number handling explicit
- [ ] Division by zero prevented

## Fiat-Shamir Transcript

- [ ] All public inputs included in transcript
- [ ] Circuit identifier/version in transcript
- [ ] Domain separation tags
- [ ] No mutable external sources for challenges
- [ ] Order of transcript operations consistent

## Witness Generation

- [ ] Witness computed deterministically from inputs
- [ ] No secret-dependent branching in constraints
- [ ] Auxiliary witness values properly derived
- [ ] Witness generation matches constraint system

## Trusted Setup (if applicable)

- [ ] Ceremony with multiple participants
- [ ] At least one honest participant assumption documented
- [ ] Toxic waste provably destroyed
- [ ] Parameters reproducibly generated
- [ ] Powers of tau ceremony verification

## Verifier Security

- [ ] Proof malleability considered
- [ ] Replay protection (binding to context)
- [ ] Verifier doesn't trust prover-supplied public inputs blindly
- [ ] Gas limits considered for on-chain verification
- [ ] Batch verification security (if used)

## Side Channels

- [ ] Prover key/secrets not in logs
- [ ] Constant-time witness generation where secrets exist
- [ ] Prover infrastructure isolated
- [ ] Memory zeroization after proving

## Common Circuit Bugs

| Bug                     | Impact                 | Check                        |
| ----------------------- | ---------------------- | ---------------------------- |
| Under-constrained       | Fake proofs            | Verify all paths constrained |
| Over-constrained        | Valid inputs fail      | Test valid edge cases        |
| Missing range check     | Overflow exploits      | Bound all inputs             |
| Transcript omission     | Challenge manipulation | Audit transcript             |
| Copy constraint missing | Value substitution     | Verify value flow            |

## Testing

- [ ] Property-based tests for constraint satisfaction
- [ ] Negative tests (invalid witnesses should fail)
- [ ] Boundary value tests
- [ ] Fuzzing on proof deserialization
- [ ] Cross-implementation verification
- [ ] Formal verification where feasible

## Proof Systems Specific

### SNARK (Groth16, PLONK)

- [ ] Pairing-friendly curve security level adequate
- [ ] Trusted setup handled (or universal setup)
- [ ] Proof size vs. verification time tradeoff understood

### STARK

- [ ] Hash function security (collision resistance)
- [ ] FRI parameters (blowup factor, queries)
- [ ] Field size adequate for security level

### Recursive Proofs

- [ ] Inner circuit soundness
- [ ] Accumulator security
- [ ] Depth limits considered
