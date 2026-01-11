# Smart Contract Security Checklist

## Access Control

- [ ] Owner/admin functions protected
- [ ] Role-based access properly implemented
- [ ] No unprotected initializers
- [ ] Privilege separation (different roles for different actions)
- [ ] Emergency pause mechanism
- [ ] Timelocks on critical operations

## Reentrancy

- [ ] Checks-Effects-Interactions pattern
- [ ] ReentrancyGuard on external calls
- [ ] State updates before external calls
- [ ] Read-only reentrancy considered (view functions)
- [ ] Cross-contract reentrancy paths analyzed

## Integer Handling

- [ ] SafeMath or Solidity 0.8+ overflow checks
- [ ] Division by zero prevented
- [ ] Rounding direction explicit and consistent
- [ ] Precision loss in calculations acceptable
- [ ] Token decimals handled correctly

## External Calls

- [ ] Return values checked
- [ ] Low-level call failures handled
- [ ] Gas limits on external calls considered
- [ ] Untrusted contract interactions minimized
- [ ] Callback attack surface minimized

## Token Handling

- [ ] ERC20 return value handling (SafeERC20)
- [ ] Fee-on-transfer tokens considered
- [ ] Rebasing tokens considered
- [ ] Flash loan attack vectors analyzed
- [ ] Approval race conditions (use increaseAllowance)

## Oracles & Price Feeds

- [ ] Multiple oracle sources where possible
- [ ] Staleness checks on oracle data
- [ ] Price manipulation resistance (TWAP vs spot)
- [ ] Circuit breakers for extreme values
- [ ] Fallback oracle strategy

## Upgradeability

- [ ] Upgrade mechanism secured (multisig, timelock)
- [ ] Storage layout preserved across upgrades
- [ ] Initializer protection (initializer modifier)
- [ ] Implementation contract secured
- [ ] Upgrade path tested

## Economic Security

- [ ] MEV/sandwich attack resistance
- [ ] Flash loan attack vectors
- [ ] Griefing attack costs analyzed
- [ ] Incentive alignment verified
- [ ] Liquidity manipulation resistance

## Signatures

- [ ] EIP-712 typed data signing
- [ ] Chain ID included
- [ ] Contract address included
- [ ] Nonce for replay protection
- [ ] Deadline for time-limited signatures
- [ ] ecrecover return value (address(0)) checked

## Gas & DoS

- [ ] Unbounded loops avoided
- [ ] Array length limits
- [ ] Pull over push for payments
- [ ] Gas griefing prevention
- [ ] Block gas limit considerations

## Common Vulnerabilities

| Vulnerability       | Check                           |
| ------------------- | ------------------------------- |
| Reentrancy          | CEI pattern, guards             |
| Access control      | Modifier on all admin functions |
| Oracle manipulation | TWAP, multiple sources          |
| Flash loan          | Spot price avoided              |
| Front-running       | Commit-reveal, MEV protection   |
| Denial of service   | Bounded loops, pull payments    |
| Integer overflow    | SafeMath or 0.8+                |
| Uninitialized proxy | Initializer protection          |

## Testing Requirements

- [ ] Unit tests for all functions
- [ ] Integration tests for workflows
- [ ] Invariant/property tests
- [ ] Fork tests against mainnet state
- [ ] Formal verification for critical invariants
- [ ] Fuzzing on entry points

## Deployment Checklist

- [ ] Constructor arguments verified
- [ ] Initial state correct
- [ ] Permissions set correctly
- [ ] Verified on block explorer
- [ ] Monitoring and alerting configured
- [ ] Incident response plan ready
