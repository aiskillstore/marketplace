# Sample Violation Report

## Incremental Mode Output

```
## DDD Check: feature/add-coupon → 3 files changed

### CouponAggregate.java — Domain
CRITICAL: setId is public. Change to protected to prevent external identity mutation.
HIGH: Missing exception mode — CouponAggregate.confirm() modifies state but doesn't throw AggregateException on validation failure.

### CouponAppService.java — Application
HIGH: Caught DomainException but returned raw exception message to Adaptor. Wrap in ResultDO.fail() instead.

### CouponDTO.java — Client
No violations found.

### Summary
- 3 files checked, 2 violations (C: 1, H: 1, M: 0, L: 0)
```

## Full Mode Output (excerpt)

```
# DDD Full Compliance Audit
Project: order-system | Files: 87 | Layers: 4 | Date: 2026-07-21

## Executive Summary
- Total violations: 12 (CRITICAL: 2, HIGH: 5, MEDIUM: 3, LOW: 2)
- Compliance score: 78%
- Worst layer: Domain

## By Layer

### Domain Layer (23 files, 4 violations)
| File | Severity | Issue | Fix |
|------|----------|-------|-----|
| Order.java | CRITICAL | setId public | Change to protected |
| Order.java | HIGH | Constructor validates nothing | Add param validation in create() factory |
| Payment.java | MEDIUM | Missing JavaDoc on pay() | Add /** Processes payment and updates order status */ |
| RefundService.java | CRITICAL | Imports JdbcTemplate | Move to Infrastructure, expose via GatewayI |

### Application Layer (31 files, 3 violations)
| File | Severity | Issue | Fix |
|------|----------|-------|-----|
| OrderAppService.java | HIGH | Does not extend ApplicationCmdService | Add extends ApplicationCmdService |
| OrderAppService.java | HIGH | Throws BizException to Adaptor | Catch and convert to ResultDO.fail() |
| QueryOrderService.java | MEDIUM | Direct Repository call without Assembler | Use Assembler to convert PO → DTO |

## Anti-Patterns Found
- AP-D-01: Strategy pattern in domain (RefundService.java:42) — extract to DomainService
- AP-D-03: Anemic entity (Payment.java) — only getters/setters, zero behavior

## Recommendations
1. Fix setId visibility on all aggregates (2 files, 5min)
2. Add exception mode contract to all domain mutators (8 files, 30min)
3. Move RefundService JDBC logic to Infrastructure (1 file, 20min)
```
