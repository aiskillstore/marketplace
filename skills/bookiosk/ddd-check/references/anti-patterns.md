# Anti-Patterns Reference


## 目录
- [Domain Layer](#domain-layer)
  - [AP-D-01: Design Patterns in Domain Layer](#ap-d-01-design-patterns-in-domain-layer)
  - [AP-D-02: Plain Types Instead of Field\<T\> in Entities](#ap-d-02-plain-types-instead-of-field\<t\>-in-entities)
  - [AP-D-03: Mutable Value Objects](#ap-d-03-mutable-value-objects)
  - [AP-D-04: Generic Technical Method Names on Aggregates](#ap-d-04-generic-technical-method-names-on-aggregates)
  - [AP-D-05: Wrong Exception Mode in DomainService](#ap-d-05-wrong-exception-mode-in-domainservice)
  - [AP-D-06: DomainService Directly Depending on Adaptor](#ap-d-06-domainservice-directly-depending-on-adaptor)
- [Application Layer](#application-layer)
  - [AP-A-01: Core Business Logic in AppService](#ap-a-01-core-business-logic-in-appservice)
  - [AP-A-02: Direct Database or External Service Access](#ap-a-02-direct-database-or-external-service-access)
  - [AP-A-03: Validation Logic in AppService Instead of requestDTO.check()](#ap-a-03-validation-logic-in-appservice-instead-of-requestdtocheck)
  - [AP-A-04: Using Primitive Types or Map as Parameters](#ap-a-04-using-primitive-types-or-map-as-parameters)
  - [AP-A-05: Command Calling Query (CQRS Violation)](#ap-a-05-command-calling-query-cqrs-violation)
  - [AP-A-06: APP Throwing Exceptions to Adaptor](#ap-a-06-app-throwing-exceptions-to-adaptor)
- [Adaptor Layer](#adaptor-layer)
  - [AP-AD-01: Adaptor Interface Defined by 3rd-Party API Shape](#ap-ad-01-adaptor-interface-defined-by-3rd-party-api-shape)
  - [AP-AD-02: Business Logic in Adaptor](#ap-ad-02-business-logic-in-adaptor)
- [Infrastructure Layer](#infrastructure-layer)
  - [AP-I-01: Business Logic in RepositoryImpl](#ap-i-01-business-logic-in-repositoryimpl)
  - [AP-I-02: Business Logic in Converter](#ap-i-02-business-logic-in-converter)
  - [AP-I-03: Direct Technical Exception Propagation](#ap-i-03-direct-technical-exception-propagation)
  - [AP-I-04: PO Exposed to Domain or Application Layer](#ap-i-04-po-exposed-to-domain-or-application-layer)
  - [AP-I-05: External Service Calls from Infrastructure](#ap-i-05-external-service-calls-from-infrastructure)
- [Client Layer](#client-layer)
  - [AP-C-01: Client Depending on Model Layer](#ap-c-01-client-depending-on-model-layer)
  - [AP-C-02: Over-Reusing DTOs](#ap-c-02-over-reusing-dtos)
  - [AP-C-03: Flat Package Structure in Client](#ap-c-03-flat-package-structure-in-client)
- [Quick Reference: Severity Summary](#quick-reference-severity-summary)

Consolidated list of all forbidden patterns across every layer. Each entry shows the wrong approach, why it's wrong, and the correct alternative.

---

## Domain Layer

### AP-D-01: Design Patterns in Domain Layer

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | No Strategy, Factory, Template Method, Chain of Responsibility, or any GoF pattern in domain layer |

**Wrong:**
```java
// Business logic fragmented across multiple Strategy classes
public interface PriceStrategy {
    BigDecimal calculate(OrderItem item);
}
public class DomesticPriceStrategy implements PriceStrategy { ... }
public class InternationalPriceStrategy implements PriceStrategy { ... }

public FeeCalculateResult calculateFee(FeeCalculateParam param) {
    PriceStrategy strategy = priceStrategyFactory.getStrategy(param.getDomesticIntl());
    return strategy.calculate(param);  // logic hidden behind interface
}
```

**Why wrong:** Core business rules scattered across N implementation files. Reader must jump between files to understand complete pricing logic. Violates domain layer purpose — business rules should be directly expressed, not abstracted behind technical patterns.

**Correct:**
```java
public FeeCalculateResult calculateFee(FeeCalculateParam param) {
    if (DomesticIntlEnum.DOMESTIC.equals(param.getDomesticIntl())) {
        return calculateDomesticFee(param);
    } else {
        return calculateInternationalFee(param);
    }
}
```

**Exception:** Design patterns ARE allowed in Adaptor layer for technical routing (channel-based, protocol-based). See AP-A-01.

---

### AP-D-02: Plain Types Instead of Field\<T\> in Entities

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | Entity properties MUST use `Field<T>`, `FieldSet<T>`, `FieldList<T>` |

**Wrong:**
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderItemEntity extends BaseEntity<Long> {
    private Long orderId;        // plain type
    private String productName;  // plain type
    private Long price;          // plain type — mutable, no change tracking
}
```

**Why wrong:** Plain types allow silent mutation, no change tracking, null ambiguity. Violates project-wide immutability rule.

**Correct:**
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderItemEntity extends BaseEntity<Long> {
    private Field<Long> orderId;
    private Field<String> productName;
    private Field<Long> price;

    public void updatePrice(Long newPrice) {
        this.price = Field.of(newPrice);  // new instance, immutable
    }
}
```

---

### AP-D-03: Mutable Value Objects

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Value objects MUST be immutable — methods return new instances, never modify in-place |

**Wrong:**
```java
public class MoneyValue extends BaseValue {
    private BigDecimal amount;

    public void setAmount(BigDecimal amount) {  // setter = mutation
        this.amount = amount;
    }
}
```

**Why wrong:** Value objects represent conceptual wholes identified by their attribute values. Mutation breaks equality semantics and can cause bugs when shared across aggregates.

**Correct:**
```java
public class MoneyValue extends BaseValue {
    private final BigDecimal amount;

    public MoneyValue(BigDecimal amount) {
        this.amount = amount;
    }

    public MoneyValue add(MoneyValue other) {  // returns new instance
        return new MoneyValue(this.amount.add(other.amount));
    }

    public BigDecimal getAmount() { return amount; }
}
```

---

### AP-D-04: Generic Technical Method Names on Aggregates

| | |
|---|---|
| **Severity** | MEDIUM |
| **Rule** | Aggregate methods must use business verbs, not technical verbs |

**Wrong:**
```java
public void updateStatus(OrderStatus status) { ... }
public void save() { ... }
public void modify(List<OrderItem> items) { ... }
```

**Correct:**
```java
public void confirmPayment(ConfirmPaymentParam param) { ... }
public void cancelOrder(CancelOrderParam param) { ... }
public void backfillFees(FeeInfo feeInfo) { ... }
```

---

### AP-D-05: Wrong Exception Mode in DomainService

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | 阻断型 MUST throw exception (not return ResultDO). 分支型 MUST return ResultDO (not throw). See `domain-layer.md` A.6. |

**Wrong — 阻断型 returning ResultDO:**
```java
// Blocking error should throw, not return ResultDO
public ResultDO<Void> confirmPayment(ConfirmPaymentParam param) {
    try {
        OrderAggregate order = orderRepository.load(param.getOrderId());
        if (order == null) {
            return ResultDO.buildFailResult("ORDER_NOT_FOUND", "Order not found");  // WRONG
        }
        order.confirmPayment(param);
        orderRepository.save(order);
        return ResultDO.buildSuccessResult(null);
    } catch (BizException e) {
        return ResultDO.buildFailResult(e.getCode(), e.getMsg());  // WRONG: swallow in Domain
    }
}
```

**Correct — 阻断型:**
```java
public void confirmPayment(ConfirmPaymentParam param) {
    LevelLock lock = orderRepository.buildLock("order:confirmPayment:" + param.getOrderId());
    try {
        if (!lock.tryLock()) {
            throw new BizException("LOCK_FAIL", "Failed to acquire lock");
        }
        OrderAggregate order = orderRepository.load(param.getOrderId());
        if (order == null) {
            throw new BizException("ORDER_NOT_FOUND", "Order not found");
        }
        order.confirmPayment(param);
        orderRepository.save(order);
    } finally {
        lock.unlock();
    }
    // Blocking exceptions propagate to APP layer
}
```

**Correct — 分支型:**
```java
public ResultDO<OrderAggregate> checkDuplicate(CheckDuplicateParam param) {
    OrderAggregate existing = orderRepository.findByOrderNo(param.getOrderNo());
    if (existing != null) {
        return ResultDO.buildFailResult("DUPLICATE_ORDER", "Order already exists", existing);
    }
    return ResultDO.buildSuccessResult(null);
}
```

---

### AP-D-06: DomainService Directly Depending on Adaptor

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | DomainService MUST NOT directly depend on Adaptor. Use functional interface injection via Param |

**Wrong:**
```java
@Service
public class SalePriceDomainServiceImpl implements SalePriceDomainService {
    @Autowired
    private ExchangeRateAdaptor exchangeRateAdaptor;  // domain depends on adaptor!
    ...
}
```

**Correct:** Define `@FunctionalInterface` in domain, inject via Param. See `domain-layer.md` Section A.8.

---

## Application Layer

### AP-A-01: Core Business Logic in AppService

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | Application layer does scene orchestration only. Business logic MUST be in DomainService or aggregates |

**Wrong:**
```java
@Override
public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO requestDTO) {
    // Business logic in Application layer!
    if (requestDTO.getAmount() < 100) {
        return ResultDO.buildFailResult("AMOUNT_TOO_LOW", "Minimum order amount is 100");
    }
    if (requestDTO.getQuantity() > 10 && !vipUser) {
        return ResultDO.buildFailResult("LIMIT_EXCEEDED", "Non-VIP max 10 items");
    }
    // ... more business rules ...
}
```

**Why wrong:** Business rules become duplicated across scenes. Same validation for `createOrderOnline` and `createOrderManual` would be copied. Domain layer should own the rules — Application only orchestrates.

**Correct:** Move business rules to `OrderAggregate.validateCreate()` or `OrderDomainService`. Application only handles scene-specific orchestration (checking inventory via Adaptor, etc.).

---

### AP-A-02: Direct Database or External Service Access

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Application MUST NOT access DB directly (use Repository) or external services directly (use Adaptor) |

**Wrong:**
```java
@Service
public class OrderAppServiceImpl implements OrderAppService {
    @Autowired
    private OrderMapper orderMapper;         // direct DB access!
    @Autowired
    private ThirdPartyLogisticsClient client; // direct external call!

    @Override
    public ResultDO<GetOrderDetailResponseDTO> getOrderDetail(GetOrderDetailRequestDTO req) {
        OrderPO po = orderMapper.selectById(req.getOrderId());       // wrong
        LogisticsResponse resp = client.track(po.getLogisticsNo());  // wrong
        ...
    }
}
```

**Correct:** Use `OrderRepository` for DB, `LogisticsAdaptor` for external calls.

---

### AP-A-03: Validation Logic in AppService Instead of requestDTO.check()

| | |
|---|---|
| **Severity** | MEDIUM |
| **Rule** | Parameter validation MUST be via `requestDTO.check()` returning `ResultDO` |

**Wrong:**
```java
@Override
public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO req) {
    if (req.getProductId() == null || req.getProductId().isEmpty()) {
        return ResultDO.buildFailResult("PARAM_ERROR", "Product ID required");
    }
    if (req.getQuantity() == null || req.getQuantity() <= 0) {
        return ResultDO.buildFailResult("PARAM_ERROR", "Quantity must be > 0");
    }
    ...
}
```

**Correct:** Put validation in `CreateOrderRequestDTO.check()` method. AppService just calls `requestDTO.check()`.

---

### AP-A-04: Using Primitive Types or Map as Parameters

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Application methods MUST use typed RequestDTO, never primitives or Map |

**Wrong:**
```java
ResultDO<CreateOrderResponseDTO> createOrder(String productId, Integer quantity, Map<String, Object> extra);
```

**Correct:**
```java
ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO requestDTO);
```

---

### AP-A-05: Command Calling Query (CQRS Violation)

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | `AppService` (Command) MUST NOT call `QueryAppService` (Query) |

**Wrong:**
```java
@Service
public class OrderAppServiceImpl implements OrderAppService {  // Command
    @Autowired
    private OrderQueryAppService orderQueryAppService;  // Query — forbidden!

    @Override
    public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO req) {
        // Using query service in a write operation
        ResultDO<OrderDetailResponseDTO> existing = orderQueryAppService.getOrderDetail(...);
        ...
    }
}
```

**Correct:** Use `OrderRepository` directly if you need to load data in a write operation.

---

### AP-A-06: APP Throwing Exceptions to Adaptor

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | APP MUST NOT throw exceptions to Adaptor. APP catches Domain/Adaptor exceptions and converts to `ResultDO`. |

**Wrong:**
```java
public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO req) {
    // Domain exception propagates through APP to Adaptor
    orderDomainService.createOrder(param);  // BizException not caught
    return ResultDO.buildSuccessResult(responseDTO);
}
```

**Correct:**
```java
public ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO req) {
    try {
        orderDomainService.createOrder(param);
        return ResultDO.buildSuccessResult(responseDTO);
    } catch (BizException | AggregateException e) {
        log.error("Create order business error, req: {}", req, e);
        return ResultDO.buildFailResult(e.getCode(), e.getMsg());
    } catch (Throwable e) {
        log.error("Create order system error, req: {}", req, e);
        return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
    }
}
```

---

## Adaptor Layer

### AP-AD-01: Adaptor Interface Defined by 3rd-Party API Shape

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | Adaptor interfaces MUST be defined by Application needs, NOT by 3rd-party API shapes |

**Wrong:**
```java
// Interface mirrors 3rd-party API exactly
public interface LogisticsAdaptor {
    ThirdPartyTrackResponse track(String apiKey, String trackingNo, String carrier, int timeout);
}
```

**Correct:**
```java
// Interface expresses Application's business need
public interface LogisticsAdaptor {
    ResultDO<LogisticsInfoResponseDTO> queryLogistics(String logisticsNo);
}
```

---

### AP-AD-02: Business Logic in Adaptor

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Adaptors do protocol conversion only, no business logic |

**Wrong:**
```java
@Component
public class LogisticsAdaptorImpl implements LogisticsAdaptor {
    @Override
    public ResultDO<LogisticsInfoResponseDTO> queryLogistics(String logisticsNo) {
        ThirdPartyResponse response = client.track(logisticsNo);
        // Business judgment in Adaptor!
        if (response.getStatus().equals("DELIVERED") && response.getDaysSinceDelivery() > 7) {
            response.setStatus("ARCHIVED");
        }
        return ResultDO.buildSuccessResult(LogisticsConverter.toDTO(response));
    }
}
```

**Correct:** Adaptor returns raw (but anti-corruption-simplified) data. Business judgments happen in Domain or Application layer.

---

## Infrastructure Layer

### AP-I-01: Business Logic in RepositoryImpl

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | RepositoryImpl does pure persistence — store and retrieve only |

**Wrong:**
```java
@Component
public class OrderRepositoryImpl implements OrderRepository {
    @Override
    public ResultDO<Void> save(OrderAggregate aggregate) {
        // Business validation in Repository!
        if (aggregate.getAmount() < 0) {
            return ResultDO.buildFailResult("AMOUNT_INVALID", "Amount cannot be negative");
        }
        if (aggregate.getStatus() == OrderStatus.CANCELLED) {
            // Business rule in wrong layer
            aggregate.setStatus(OrderStatus.ARCHIVED);
        }
        orderMapper.insert(OrderConverter.toPO(aggregate));
        ...
    }
}
```

**Correct:** All business rules in `OrderAggregate` methods. RepositoryImpl only does PO conversion and DB calls.

---

### AP-I-02: Business Logic in Converter

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Converter does pure field mapping only, no business judgments |

**Wrong:**
```java
public class OrderConverter {
    public static OrderAggregate toAggregate(OrderPO po) {
        if (po == null) return null;
        OrderAggregate aggregate = new OrderAggregate();
        // Business logic in Converter!
        if (po.getAmount() > 10000) {
            aggregate.setHighValue(true);
        }
        if (po.getOrderStatus() == 3 && po.getGmtModified().before(lastWeek)) {
            // Business rule about stale orders — should be in aggregate
            aggregate.setArchived(true);
        }
        ...
    }
}
```

**Correct:** Converter does field mapping + enum conversion only. Business judgments belong in aggregate methods.

---

### AP-I-03: Direct Technical Exception Propagation

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | Catch exceptions in RepositoryImpl, convert to `ResultDO` failure |

**Wrong:**
```java
public ResultDO<OrderAggregate> query(OrderQuery query) {
    OrderPO po = orderMapper.selectById(query.getId());  // SQLException propagates!
    return ResultDO.buildSuccessResult(OrderConverter.toAggregate(po));
}
```

**Correct:**
```java
public ResultDO<OrderAggregate> query(OrderQuery query) {
    try {
        OrderPO po = orderMapper.selectById(query.getId());
        return ResultDO.buildSuccessResult(OrderConverter.toAggregate(po));
    } catch (Exception e) {
        log.error("Query order failed, query: {}", query, e);
        return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order data error");
    }
}
```

---

### AP-I-04: PO Exposed to Domain or Application Layer

| | |
|---|---|
| **Severity** | HIGH |
| **Rule** | PO stays strictly within Infrastructure layer |

**Wrong:**
```java
// Domain layer imports PO
import com.example.infrastructure.order.mysql.po.OrderPO;  // forbidden!

// Application layer uses PO
public ResultDO<OrderPO> getOrder(Long id) { ... }  // forbidden!
```

**Correct:** PO is an Infrastructure internal detail. Domain sees only aggregates. Application sees only DTOs.

---

### AP-I-05: External Service Calls from Infrastructure

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | Infrastructure handles middleware (DB, cache, MQ). External 3rd-party calls go through Adaptor |

**Wrong:**
```java
@Component
public class OrderRepositoryImpl implements OrderRepository {
    @Autowired
    private ThirdPartyPaymentClient paymentClient;  // should be in Adaptor!

    @Override
    public ResultDO<Void> save(OrderAggregate aggregate) {
        paymentClient.verify(aggregate.getPaymentId());  // wrong layer!
        ...
    }
}
```

**Correct:** External service calls happen in Output Adaptor, orchestrated by Application layer.

---

## Client Layer

### AP-C-01: Client Depending on Model Layer

| | |
|---|---|
| **Severity** | CRITICAL |
| **Rule** | Client MUST be self-contained — cannot depend on `model` module |

**Wrong:**
```java
package com.example.client.order.res;
import com.example.model.DomesticIntlEnum;  // model dependency — forbidden!

public class CreateOrderResponseDTO extends BaseDTO {
    private DomesticIntlEnum domesticIntl;  // external callers now need model jar
}
```

**Correct:** Define a client-side enum or use String in the DTO. Convert in Application Assembler.

---

### AP-C-02: Over-Reusing DTOs

| | |
|---|---|
| **Severity** | MEDIUM |
| **Rule** | Don't reuse a DTO if it introduces irrelevant fields for a given scene |

**Wrong:**
```java
// Using full OrderDTO for a simple list query — includes 20+ fields caller doesn't need
ResultDO<List<OrderDTO>> queryOrderList(QueryOrderListRequestDTO req);
```

**Correct:** Define a slim `OrderSummaryDTO` with only list-relevant fields.

---

### AP-C-03: Flat Package Structure in Client

| | |
|---|---|
| **Severity** | LOW |
| **Rule** | `req/`, `res/`, `model/` MUST be organized into sub-packages by category |

**Wrong:**
```
client/order/req/
├── CreateOrderRequestDTO.java
├── QueryOrderRequestDTO.java
├── PassengerInfo.java        // flat — should be in passenger/ sub-package
├── CredentialInfo.java
├── SegmentInfo.java
└── ...
```

**Correct:**
```
client/order/req/
├── passenger/
│   ├── PassengerInfo.java
│   └── CredentialInfo.java
├── segment/
│   └── SegmentInfo.java
├── CreateOrderRequestDTO.java
└── QueryOrderRequestDTO.java
```

---

## Quick Reference: Severity Summary

| ID | Layer | Severity | Pattern |
|----|-------|----------|---------|
| AP-D-01 | Domain | CRITICAL | Design patterns in domain layer |
| AP-D-02 | Domain | CRITICAL | Plain types instead of Field\<T\> in entities |
| AP-D-03 | Domain | HIGH | Mutable value objects |
| AP-D-04 | Domain | MEDIUM | Generic technical method names on aggregates |
| AP-D-05 | Domain | CRITICAL | Wrong exception mode — 阻断型 using ResultDO or 分支型 throwing |
| AP-D-06 | Domain | CRITICAL | DomainService directly depending on Adaptor |
| AP-A-01 | Application | CRITICAL | Core business logic in AppService |
| AP-A-02 | Application | HIGH | Direct DB or external service access |
| AP-A-03 | Application | MEDIUM | Validation logic in AppService |
| AP-A-04 | Application | HIGH | Primitive types or Map as parameters |
| AP-A-05 | Application | HIGH | Command calling Query (CQRS violation) |
| AP-A-06 | Application | CRITICAL | APP throwing exceptions to Adaptor instead of catching and converting |
| AP-AD-01 | Adaptor | CRITICAL | Interface defined by 3rd-party API shape |
| AP-AD-02 | Adaptor | HIGH | Business logic in Adaptor |
| AP-I-01 | Infrastructure | CRITICAL | Business logic in RepositoryImpl |
| AP-I-02 | Infrastructure | HIGH | Business logic in Converter |
| AP-I-03 | Infrastructure | HIGH | Direct technical exception propagation |
| AP-I-04 | Infrastructure | HIGH | PO exposed to domain/application |
| AP-I-05 | Infrastructure | CRITICAL | External service calls from Infrastructure |
| AP-C-01 | Client | CRITICAL | Client depending on model layer |
| AP-C-02 | Client | MEDIUM | Over-reusing DTOs |
| AP-C-03 | Client | LOW | Flat package structure |
