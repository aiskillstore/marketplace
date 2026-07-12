# Exception Handling — Two-Mode Philosophy

## Core Principle

Domain 和 outAdaptor 根据 **上游是否需要失败数据** 选择异常机制：

| | 阻断型 (Throw) | 分支型 (ResultDO) |
|---|---|---|
| **意图** | 事件终止，不继续 | 分支路由，继续走 |
| **携带数据** | 无（只有 code + msg） | 有（失败但有 data） |
| **APP 处理** | catch → ResultDO.fail() | 判断 → 走其他链路 |
| **典型场景** | 库存不足、余额不够 | 重复单、降级兜底 |

## Layer Responsibilities

```
Domain / outAdaptor          APP (边界)                   inAdaptor
      │                        │                            │
      │  throw BizEx     →     │  catch → fail()           │
      │  throw AggEx     →     │  catch → fail()           │
      │  return ResultDO →     │  分支处理                  │
      │                        │                            │
      │                        │  ← ResultDO ─────────────  │
```

### Domain Layer

- **阻断型:** Throw `BizException` (DomainService) or `AggregateException` (Aggregate/Entity). Do NOT catch in DomainService — let propagate to APP.
- **分支型:** Return `ResultDO<T>` with failure data. APP extracts data for alternative path.
- **Finally blocks:** Only for resource cleanup (lock release). No catch.

### outAdaptor Layer

- **阻断型:** External call failure (network error, timeout, 3rd-party error) → throw or let propagate. APP catches and decides: retry / fallback / fail.
- **分支型:** Return `ResultDO<T>` when APP needs response data for branching.

### APP Layer (Exception Boundary)

- **Catches** all blocking exceptions from Domain and outAdaptor.
- **Converts** to `ResultDO.fail()` for inAdaptor.
- **Handles** 分支型 ResultDO — extracts data, takes alternative path.
- **Never throws** to inAdaptor.

### inAdaptor Layer

- Receives only `ResultDO<T>` from APP.
- No exception handling needed — just protocol conversion.

## Examples

### 阻断型: Order Confirm

```java
// Domain — throws on blocking error
public void confirmPayment(ConfirmPaymentParam param) {
    OrderAggregate order = orderRepository.load(param.getOrderId());
    if (order == null) {
        throw new BizException("ORDER_NOT_FOUND", "Order not found");
    }
    order.confirmPayment(param);  // may throw AggregateException
    orderRepository.save(order);
}

// APP — catches and converts
public ResultDO<Void> confirmPayment(ConfirmPaymentRequestDTO req) {
    try {
        orderDomainService.confirmPayment(toParam(req));
        return ResultDO.buildSuccessResult(null);
    } catch (BizException | AggregateException e) {
        return ResultDO.buildFailResult(e.getCode(), e.getMsg());
    }
}
```

### 分支型: Duplicate Check

```java
// Domain — returns ResultDO with data
public ResultDO<OrderAggregate> checkDuplicate(CheckDuplicateParam param) {
    OrderAggregate existing = orderRepository.findByOrderNo(param.getOrderNo());
    if (existing != null) {
        return ResultDO.buildFailResult("DUPLICATE", "Order exists", existing);
    }
    return ResultDO.buildSuccessResult(null);
}

// APP — extracts data for branching
public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO req) {
    ResultDO<OrderAggregate> dupResult = orderDomainService.checkDuplicate(toCheckParam(req));
    if (dupResult.isFail()) {
        // 分支型: 把重复单信息返回给用户
        OrderAggregate existing = dupResult.getData();
        return ResultDO.buildSuccessResult(toResponseDTO(existing));
    }
    // Continue normal flow...
}
```

## Decision Flow

```
Domain/Adaptor needs to signal failure
├─ Upstream needs failure data?
│   ├─ Yes → return ResultDO.fail(code, msg, data)  [分支型]
│   └─ No  → throw BizException / AggregateException [阻断型]
│
APP receives:
├─ Exception caught → ResultDO.fail(code, msg)
├─ ResultDO.fail() with data → extract data, branch
└─ ResultDO.success() → continue
```

## Anti-Patterns

| Wrong | Why | Right |
|---|---|---|
| DomainService catches BizException, returns ResultDO.fail | 阻断型错误被吞掉, 堆栈丢失 | Let propagate to APP |
| DomainService returns ResultDO.fail with no data | 上游拿不到信息, 只能看 msg 判断 | Use throw if no data needed |
| APP throws exception to Adaptor | Adaptor 需要理解业务异常类型 | APP always returns ResultDO |
| Adaptor catches and wraps all exceptions | 上游失去错误上下文 | Throw on blocking, ResultDO for branch |
