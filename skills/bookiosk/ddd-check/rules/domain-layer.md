# Domain Layer Specification

## Part A: Base Rules (All Modes)

### A.1 Package Structure

```
domain/
└── {business}/               # Per business domain (order, booking, refund)
    ├── model/
    │   ├── aggregate/        # Aggregate roots (extends BaseAggregate)
    │   ├── entity/           # Entities (extends BaseEntity)
    │   ├── value/            # Value objects (extends BaseValue)
    │   ├── param/            # Parameter objects (extends BaseParam)
    │   └── result/           # Result objects (extends BaseResult)
    ├── service/              # Domain services (DomainService)
    └── repository/           # Repository interfaces (extends AggregateRepository)
```

**Constraint:** Domain layer may ONLY contain the above types. No Utils, constants, config classes, or non-domain concepts.

### A.2 Domain Layer Isolation

- Contains **pure business code only**
- Forbidden: direct references to technical frameworks or 3rd-party libraries (Spring DI annotations like `@Service` and static utility classes are excepted)
- May depend on `model` module (shared enums, common business concepts)
- Repository **interfaces** defined here, **implementations** in Infrastructure layer
- Repository manages intra-domain DB, cache, and messaging — does NOT depend on Adaptor

### A.3 Design Patterns — FORBIDDEN in Domain Layer

**Prohibited patterns:** Strategy, Factory, Template Method, Chain of Responsibility, and all other Gang-of-Four patterns.

**Why:** Design patterns are technical mechanisms, not business semantics. In the domain layer they cause:
- **Fragmented business logic** — core logic scattered across multiple Strategy/Handler classes
- **Over-abstraction** — forcing logic splits to fit pattern interfaces, breaking cohesion
- **Violation of domain layer purpose** — domain should express business rules directly, not technical architecture

**Core principle:** Industry business rules are **enumerable and finite**. We build industry-specific business systems, not generic platforms. Business branches (domestic/international, adult/child/infant, pricing rules) are limited and exhaustively enumerable. Use plain `if/else` or `switch` in DomainService, aggregates, entities, and value objects.

| Scenario | Correct | Wrong |
|----------|---------|-------|
| Different price calculations (domestic/international) | `if/else` in DomainService or aggregate method | `PriceStrategy` interface + multiple implementations |
| Different fee rules by passenger type | `if/else` branching by passenger type in aggregate method | `FeeCalculateStrategy` + factory class |
| Business validation per status | Status enum check in aggregate method | State pattern + multiple State implementations |

```java
// CORRECT: Business logic directly in DomainService/aggregate — clear at a glance
public FeeCalculateResult calculateFee(FeeCalculateParam param) {
    if (DomesticIntlEnum.DOMESTIC.equals(param.getDomesticIntl())) {
        return calculateDomesticFee(param);
    } else {
        return calculateInternationalFee(param);
    }
}

// WRONG: Strategy pattern scatters business logic across multiple classes
public FeeCalculateResult calculateFee(FeeCalculateParam param) {
    FeeStrategy strategy = feeStrategyFactory.getStrategy(param.getDomesticIntl());
    return strategy.calculate(param);
}
```

**Where design patterns DO belong:** Adaptor layer may use patterns for **technical routing** (e.g., routing to different 3rd-party APIs by channel ID). See `adaptor-layer.md` Section 1.6.

### A.4 Param Objects

| Rule | Spec |
|------|------|
| Class name | `{MethodName}Param` |
| Inheritance | MUST extend `BaseParam` |
| Usage | DomainService method input, aggregate/entity method input |

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class ConfirmPaymentParam extends BaseParam {
    private Long orderId;
    private String paymentChannel;
    private BigDecimal amount;
}
```

### A.5 Result Objects

| Rule | Spec |
|------|------|
| Class name | `{MethodName}Result` |
| Inheritance | MUST extend `BaseResult` |
| Feature | May contain rich (behavior) methods |

**Use cases:**
1. DomainService method return values
2. Repository query return values (Application queries intra-domain data via Repository)

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class FeeCalculateResult extends BaseResult {
    private BigDecimal totalFee;
    private String currency;

    /** Rich method: check if free */
    public boolean isFree() {
        return totalFee == null || totalFee.compareTo(BigDecimal.ZERO) == 0;
    }
}
```

### A.6 Exception Handling — Two Modes

Domain and Adaptor choose exception mechanism based on **whether upstream needs the failure data**:

| Mode | Mechanism | When | Example |
|---|---|---|---|
| **阻断型** | Throw exception | Event must stop, no data needed | 库存不足, 余额不够, 支付超时 |
| **分支型** | Return `ResultDO<T>` | Upstream needs failure data for branching/fallback | 重复下单(需返回已有单号), 查无缓存(需降级走DB) |

**Key principle:** Throw when the operation can't proceed and no data is needed. Return ResultDO when the caller needs the payload to decide what to do next.

**阻断型 — throw:**
| Exception | Throw Location | Purpose |
|-----------|---------------|---------|
| `AggregateException` | Aggregate, Entity | Aggregate/entity internal validation failure |
| `BizException` | DomainService | Business rule violation, pre-condition check failure |

**分支型 — return ResultDO (with data):**
| Scenario | Return | Upstream Action |
|----------|--------|-----------------|
| 重复单检测 | `ResultDO.fail("DUPLICATE", orderNo, existingOrder)` | APP 拿 existingOrder 返回给用户 |
| 缓存未命中 | `ResultDO.fail("CACHE_MISS", key, null)` | APP 降级走 DB 查询 |

**Exception boundary:** APP layer catches all 阻断型 exceptions and converts to `ResultDO` failure. Adaptor never sees raw exceptions.

### A.7 Repository Interface

| Rule | Spec |
|------|------|
| Interface name | `{BusinessName}Repository` — matches corresponding DomainService prefix (e.g., `OrderDomainService` → `OrderRepository`) |
| Inheritance | MUST extend `AggregateRepository` |
| Defined in | domain layer |
| Implemented in | infrastructure layer |
| Method naming | MUST use verbs (`save`, `query`, etc.) |

**Core responsibility:** Repository manages **intra-domain** DB, cache, and messaging. Repository does NOT depend on Adaptor and does NOT call external 3rd-party services.

### A.8 Lazy-Loading External Data in DomainService

**Scenario:** DomainService loops over items and needs to query external data on-demand (e.g., exchange rates per currency). DomainService only has access to its own Repository — direct Adaptor dependency is forbidden.

**Solution:** Define a `@FunctionalInterface` in the domain layer, inject its implementation via the Param object. Application layer wires the Adaptor call into the Param. DomainService calls the interface without knowing the implementation.

**When to use:** Only for **in-loop on-demand queries**. Simple (non-loop) cases: Application layer fetches external data before calling DomainService and passes it in Param directly.

#### Step 1: Define functional interface in domain layer
```java
@FunctionalInterface
public interface ExchangeRateProvider {
    BigDecimal getExchangeRate(String currency);
}
```

#### Step 2: Reference in Param
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class CalculateSalePriceParam extends BaseParam {
    private List<ProductItem> productItems;
    private ExchangeRateProvider exchangeRateProvider; // injected by Application layer
}
```

#### Step 3: DomainService calls via interface
```java
@Slf4j
@Service
public class SalePriceDomainServiceImpl implements SalePriceDomainService {

    @Override
    public CalculateSalePriceResult calculateSalePrice(CalculateSalePriceParam param) {
        List<SalePriceItem> resultItems = new ArrayList<>();
        for (ProductItem item : param.getProductItems()) {
            BigDecimal rate = param.getExchangeRateProvider().getExchangeRate(item.getCurrency());
            BigDecimal salePrice = item.getBasePrice().multiply(rate);
            resultItems.add(new SalePriceItem(item.getProductId(), salePrice, item.getCurrency()));
        }
        CalculateSalePriceResult result = new CalculateSalePriceResult();
        result.setSalePriceItems(resultItems);
        return result;
    }
}
```

#### Step 4: Application layer injects Adaptor implementation
```java
@Slf4j
@Service
public class SalePriceCalculateQueryAppServiceImpl implements SalePriceCalculateQueryAppService {

    @Autowired
    private ExchangeRateAdaptor exchangeRateAdaptor;
    @Autowired
    private SalePriceDomainService salePriceDomainService;

    @Override
    public ResultDO<CalculateSalePriceResponseDTO> calculateSalePrice(CalculateSalePriceRequestDTO requestDTO) {
        CalculateSalePriceParam param = new CalculateSalePriceParam();
        param.setProductItems(SalePriceAssembler.toProductItems(requestDTO));
        param.setExchangeRateProvider(currency -> {
            ResultDO<ExchangeRateResponseDTO> rateResult = exchangeRateAdaptor.queryExchangeRate(currency);
            if (!rateResult.isSuccess()) {
                throw new RuntimeException("Exchange rate query failed: " + rateResult.getMsg());
            }
            return rateResult.getData().getRate();
        });

        ResultDO<CalculateSalePriceResult> domainResult = salePriceDomainService.calculateSalePrice(param);
        if (!domainResult.isSuccess()) {
            return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
        }
        return ResultDO.buildSuccessResult(SalePriceAssembler.toResponseDTO(domainResult.getData()));
    }
}
```

---

## Part B: Write Mode

### B.1 DomainService — Write Mode

#### Naming
| Rule | Spec | Example |
|------|------|---------|
| Interface | `{AggregateName}DomainService` | `OrderDomainService` |
| Implementation | `{AggregateName}DomainServiceImpl` | `OrderDomainServiceImpl` |
| Method | Business verbs, NOT technical verbs | `confirmPayment`, `cancelOrder` |
| Parameter | `{MethodName}Param extends BaseParam` | `ConfirmPaymentParam` |
| Return (阻断型) | `void` — success returns, failure throws exception | `void` |
| Return (分支型) | `ResultDO<T>` — carries data for upstream branching | `ResultDO<OrderAggregate>` |

#### Role
- **Core responsibility:** Encapsulate domain business logic, maintain aggregate integrity and consistency
- **Forbidden:** Direct DB/external service access, non-domain business logic

#### Standard Flow
1. Acquire distributed lock
2. Load aggregate root
3. Execute business logic (via aggregate methods)
4. Persist changes (via Repository — may include DB, cache, messaging)
5. Release lock

#### Behavior Constraints
- ALLOWED: intra-domain aggregate methods, Repository interface
- FORBIDDEN: Application layer services, Infrastructure layer implementations, external service adaptors, other domain services, other domain aggregates

#### Exception Handling

| Scenario | Mechanism | Example |
|---|---|---|
| Blocking error (阻断型) | Throw `BizException` — caught by APP | 库存不足, 余额不够 |
| Branch with data (分支型) | Return `ResultDO<T>` with data | 重复单检测, 缓存降级 |

- **阻断型:** Throw exception, let APP catch and convert to `ResultDO.fail()`. Do NOT catch in DomainService.
- **分支型:** Return `ResultDO<T>` so APP can extract data and take alternative path.
- System exceptions (`Throwable`): log and re-throw as `BizException` or let propagate to APP's catch-all.

#### Template
```java
@Slf4j
@Service
public class OrderDomainServiceImpl implements OrderDomainService {

    @Resource
    private OrderRepository orderRepository;

    @Override
    public void confirmPayment(ConfirmPaymentParam param) {
        // 1. Acquire lock
        LevelLock levelLock = orderRepository.buildLock("order:confirmPayment:" + param.getOrderId());
        try {
            if (!levelLock.tryLock()) {
                throw new BizException("LOCK_FAIL", "Failed to acquire lock, please retry");
            }

            // 2. Load aggregate
            OrderAggregate orderAggregate = orderRepository.load(param.getOrderId());
            if (orderAggregate == null) {
                throw new BizException("ORDER_NOT_FOUND", "Order not found");
            }

            // 3. Execute business logic (via aggregate method)
            orderAggregate.confirmPayment(param);

            // 4. Persist changes
            orderRepository.save(orderAggregate);

        } finally {
            levelLock.unlock();
        }
        // No catch — blocking exceptions propagate to APP layer
    }
}
```

**分支型 example — DomainService returns ResultDO when upstream needs data:**

```java
@Override
public ResultDO<OrderAggregate> checkDuplicate(CheckDuplicateParam param) {
    OrderAggregate existing = orderRepository.findByOrderNo(param.getOrderNo());
    if (existing != null) {
        // 分支型: 上游需要重复单数据, 返回 ResultDO 携带数据
        return ResultDO.buildFailResult("DUPLICATE_ORDER", "Order already exists", existing);
    }
    return ResultDO.buildSuccessResult(null);
}
```

### B.2 Aggregate Root — Write Mode

#### Definition
Aggregate root is the core domain model object. It maintains business consistency and integrity boundaries for a group of related entities and value objects. External access to internal objects MUST go through aggregate root methods only.

#### Design Principles
1. **Single responsibility:** One aggregate = one core business concept
2. **Strong consistency:** All modifications within an aggregate MUST be transactionally consistent
3. **Small aggregates:** Prefer small aggregates, avoid excessive complexity
4. **Reference by ID:** Aggregates reference each other by ID, not object reference
5. **Encapsulation:** Access aggregate only via business methods, never traverse internal structure via getters

#### Naming
| Rule | Spec | Example |
|------|------|---------|
| Class name | `{Noun}Aggregate extends BaseAggregate` | `OrderAggregate` |
| Method naming | MUST be verbs | `confirmPayment`, `cancelOrder` |
| Parameter | `{MethodName}Param extends BaseParam` or primitive type | `ConfirmPaymentParam` |
| Return | Primitive type | `void`, `boolean`, `Long` |

#### Four Method Types

**1. Write (state-modifying):** validate params + validate business rules + modify state
```java
public void cancelOrder(CancelOrderParam param) {
    if (param == null) {
        throw new AggregateException("Param must not be null");
    }
    if (!this.status.canCancel()) {
        throw new AggregateException("Current status cannot be cancelled");
    }
    this.status = OrderStatus.CANCELLED;
}
```

**2. Calculate (no state change):**
```java
public BigDecimal calculateTotalAmount() {
    return items.stream()
        .map(item -> item.getPrice().multiply(item.getQuantity()))
        .reduce(BigDecimal.ZERO, BigDecimal::add);
}
```

**3. Find (no state change):**
```java
@JSONField(serialize = false)
public OrderItemEntity findItemById(Long itemId) {
    return this.items.stream()
        .filter(item -> item.getId().equals(itemId))
        .findFirst()
        .orElse(null);
}
```

**4. Judge (no state change):**
```java
@JSONField(serialize = false)
public boolean isPaymentConfirmed() {
    return OrderStatus.PAID.equals(this.status);
}
```

**Serialization note:** If the aggregate may be serialized, annotate calculate/find/judge methods with `@JSONField(serialize = false)`.

#### Method Bloat Control

**1. State-related writes are stable:**
State-machine-driven writes (like order status transitions) are naturally stable. Verify business necessity before adding new methods.

**2. Non-state writes — abstract by business semantics:**
For supplementary data updates (bank card, fee info), merge similar operations into business concepts (e.g., `backfillFees` instead of multiple `updateXxx` methods). Method names MUST express business intent (e.g., `updatePaymentInfo`).

**3. Read/judge methods — split and delegate:**
For query/judge methods that bloat the aggregate:
- Split into base class (writes) and subclass (reads) for readability
- Expose finder methods on aggregate that return entity/value objects, then call methods directly on those objects (reduces aggregate method count)

#### Exception Handling
- Throw `AggregateException`

### B.3 Entity — Write Mode

Entities follow aggregate root conventions with these differences:

| Rule | Spec | Example |
|------|------|---------|
| Class name | `{Noun}Entity extends BaseEntity` | `OrderItemEntity` |
| Method naming | MUST be verbs | `updatePrice` |
| Parameter | `{MethodName}Param extends BaseParam` or primitive type | — |
| Return | Primitive type | — |
| **Property types** | **MUST use `Field<T>`, `FieldSet<T>`, `FieldList<T>`** | — |
| Exception | Throw `AggregateException` | — |

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderItemEntity extends BaseEntity<Long> {
    private Field<Long> orderId;
    private Field<String> productName;
    private Field<Long> price;
    private Field<DomesticIntlEnum> domesticIntl;

    public void updatePrice(Long newPrice) {
        if (newPrice == null || newPrice <= 0) {
            throw new AggregateException("Price must be greater than 0");
        }
        this.price = Field.of(newPrice);
    }
}
```

### B.4 Value Object — Write Mode

#### Core Characteristics
| Feature | Value Object | Entity |
|---------|-------------|--------|
| Identity | None | Has unique ID |
| Equality | By attribute values | By ID |
| Lifecycle | Created/destroyed freely | Has explicit lifecycle |
| Mutability | **Immutable** | Mutable (Write mode) |

#### Naming
| Rule | Spec | Example |
|------|------|---------|
| Class name | `{Noun}Value extends BaseValue` | `PassengerValue` |
| Method naming | Verbs for **calculate/judge** operations only | `passengerAge`, `isAdult` |
| Parameter | `{MethodName}Param extends BaseParam` or primitive type | — |
| Return | Primitive type | — |

#### Architectural Position
- Domain layer core model
- May appear in: Aggregate internals (as properties), DomainService params/returns, Repository query results (as part of aggregate)

```java
public class PassengerValue extends BaseValue {
    private Integer age;
    private Date birthday;

    /** Calculate passenger age, fallback to 0 if invalid */
    public Integer passengerAge() {
        if (this.age != null) {
            return this.age;
        }
        if (this.birthday == null) {
            return 0;
        }
        int calculatedAge = DateUtil.ageOfNow(this.birthday);
        return (calculatedAge < 0 || calculatedAge > 120) ? 0 : calculatedAge;
    }
}
```

### B.5 Repository — Write Mode

| Rule | Spec |
|------|------|
| Method naming | Use verbs: `save`, `query` |
| Parameter | Aggregate object (e.g., `OrderAggregate`) or query object |
| Return | `ResultDO<Void>` (save) or `ResultDO<AggregateType>` (query) |

```java
public interface OrderRepository extends AggregateRepository<OrderAggregate, Long> {
    ResultDO<Void> save(OrderAggregate aggregate);
    LevelLock buildLock(String lockKey);
    ResultDO<OrderAggregate> query(OrderQuery query);
}
```

---

## Part C: Read Mode

Read mode is **pure query** — no business logic, only data retrieval and format conversion. Aggregates serve as data carriers with no business methods.

**Characteristics:**
- No DomainService (read mode does not go through domain services)
- Aggregate is data carrier only, no business logic
- No domain model state modification

### C.1 Repository — Read Mode

| Rule | Spec | Example |
|------|------|---------|
| Method naming | Verbs expressing clear query intent, avoid abstract words | `queryOrderList`, `getOrderDetail` |
| Parameter | `{MethodName}Query` or primitive type | `QueryOrderListQuery`, `Long` |
| Return | `ResultDO<Aggregate>` or `ResultDO<List<Aggregate>>` | `ResultDO<OrderAggregate>`, `ResultDO<List<OrderAggregate>>` |

```java
public interface OrderRepository extends AggregateRepository<OrderAggregate, Long> {
    ResultDO<OrderAggregate> getOrderDetail(Long orderId);
    ResultDO<List<OrderAggregate>> queryOrderList(QueryOrderListQuery query);
}
```

---

## Part D: Pure Calculate Mode

### D.1 DomainService — Pure Calculate Mode

**Definition:**
- No aggregate roots or entities — business logic entirely in DomainService
- Stateless: no internal state modification, pure function of input parameters
- Business logic MUST stay in DomainService, NOT leak to Application or Infrastructure
- Avoid member variables, ensure method idempotency

**Typical scenarios:** Search control (allowlists, rate limiting), view processing (i18n), fee calculation

#### Naming
| Rule | Spec | Example |
|------|------|---------|
| Interface | `{Verb}DomainService` | `SearchControlDomainService` |
| Implementation | `{Verb}DomainServiceImpl` | `SearchControlDomainServiceImpl` |
| Method | Verb | `searchControl` |
| Parameter | `{MethodName}Param` | `SearchControlParam` |
| Return | `{MethodName}Result` — blocking errors throw exception | `SearchControlResult` |

#### Template
```java
@Slf4j
@Service
public class SearchControlDomainServiceImpl implements SearchControlDomainService {

    @Override
    public SearchControlResult searchControl(SearchControlParam param) {
        SearchControlResult result = new SearchControlResult();
        SearchControlRuleValue ruleValue = param.getSearchControlRuleValue();

        result.setMaxSearchWaitMilliSeconds(ruleValue.getMaxSearchWaitMilliSeconds());
        result.setWhiteAgentIds(ruleValue.getWhiteAgentIds());

        if (ruleValue.isQueryCacheOnly()) {
            result.setRealSearch(false);
            return result;
        }

        if (!ruleValue.isRealTimeSearchOD(param.getAirLegSet())) {
            result.setRealSearch(false);
            return result;
        }

        result.setRealSearch(true);
        return result;
    }
}
```

### D.2 Result — Pure Calculate Mode
Same as Base Rules A.5. Named `{Action}Result extends BaseResult`, may have rich methods.

---

## Part E: Rule+Calculate Mode

### E.1 DomainService — Rule+Calculate Mode

**Definition:**
- Has aggregates and entities — rules are modeled as aggregate roots
- Business logic carried by aggregates and entities — DomainService orchestrates only
- Stateless: entity methods compute from input parameters and return results, **never modify aggregate or entity internal state**

#### Naming
| Rule | Spec | Example |
|------|------|---------|
| Interface | `{Verb}DomainService` | `CalculateBonusDomainService` |
| Implementation | `{Verb}DomainServiceImpl` | `CalculateBonusDomainServiceImpl` |
| Method | Verb | `calculateBonus` |
| Parameter | `{MethodName}Param` | `CalculateBonusParam` |
| Return | `{MethodName}Result` — blocking errors throw exception | `List<ItemCalculateResult>` |

#### Flow
1. Query rules via Repository → get rule aggregate collection
2. Match rules against parameters
3. Call rule aggregate calculation methods

#### Template
```java
@Slf4j
@Service
public class CalculateBonusDomainServiceImpl implements CalculateBonusDomainService {

    @Resource
    private BonusRuleRepository bonusRuleRepository;

    @Override
    public List<ItemCalculateResult> calculateBonus(CalculateBonusParam param) {
        // 1. Query rule aggregates
        List<BonusRuleAggregate> ruleAggregates = bonusRuleRepository.queryAllRule();
        if (CollectionUtils.isEmpty(ruleAggregates)) {
            throw new BizException("RULE_IS_EMPTY", "Bonus rules empty");
        }

        // 2. Sort by priority
        ruleAggregates.sort(Comparator.comparingInt(BonusRuleAggregate::getRulePriority).reversed());

        // 3. Match rules and calculate
        List<ItemCalculateResult> results = new ArrayList<>();
        List<ItemParam> remainItems = new ArrayList<>(param.getItems());

        for (BonusRuleAggregate ruleAggregate : ruleAggregates) {
            if (CollectionUtils.isEmpty(remainItems)) break;
            BonusRuleMatchResult matchResult = ruleAggregate.matchRule(remainItems, param);
            if (!matchResult.getMatchedItems().isEmpty()) {
                results.addAll(ruleAggregate.calculateBonus(matchResult.getMatchedItems(), param));
            }
            remainItems = matchResult.getWaitMatchedItems();
        }

        return results;
        // Blocking exceptions propagate to APP layer
    }
}
```

### E.2 Rule Aggregate — Rule+Calculate Mode

#### Responsibilities
- Encapsulate business rules as aggregate roots (e.g., `BonusRuleAggregate`)
- Provide **stateless computation methods** (`matchRule`, `calculateBonus`) — compute from inputs, return results
- **Never modify aggregate or entity internal state** (methods are side-effect-free)

#### Business Logic Encapsulation
- Logic MUST be cohesive within aggregate/entity — **forbidden** to leak rule matching or calculation logic to Service layer
- Each method focuses on a single function (matching rules, calculating amounts), method names express business intent

#### Naming
| Rule | Spec |
|------|------|
| Parameter | `{MethodName}Param extends BaseParam` |
| Return | Result type `{MethodName}Result` |

#### Aggregate Template
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class BonusRuleAggregate extends BaseAggregate<Long> {
    private String ruleName;
    private Integer rulePriority;
    private BonusRuleEntity bonusRuleEntity;

    /** Match rules (side-effect-free) */
    public BonusRuleMatchResult matchRule(List<ItemParam> items, CalculateBonusParam param) {
        return this.bonusRuleEntity.matchItems(items, param);
    }

    /** Calculate bonus (side-effect-free) */
    public List<ItemCalculateResult> calculateBonus(List<ItemParam> matchedItems, CalculateBonusParam param) {
        return matchedItems.stream()
            .map(item -> this.bonusRuleEntity.calculateItemBonus(item, param))
            .collect(Collectors.toList());
    }
}
```

#### Rule Entity Template
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class BonusRuleEntity extends BaseEntity<Long> {
    private String bizType;
    private String condition;
    private Long baseValue;

    /** Match items (side-effect-free) */
    public BonusRuleMatchResult matchItems(List<ItemParam> items, CalculateBonusParam param) {
        List<ItemParam> matched = new ArrayList<>();
        List<ItemParam> waitMatched = new ArrayList<>();
        for (ItemParam item : items) {
            if (matchCondition(item, param)) {
                matched.add(item);
            } else {
                waitMatched.add(item);
            }
        }
        return new BonusRuleMatchResult(matched, waitMatched);
    }

    /** Calculate per-item bonus (side-effect-free) */
    public ItemCalculateResult calculateItemBonus(ItemParam item, CalculateBonusParam param) {
        Long bonusAmount = this.baseValue + item.getBasePrice();
        return ItemCalculateResult.of().setItemParam(item).setBonusAmount(bonusAmount);
    }

    private boolean matchCondition(ItemParam item, CalculateBonusParam param) {
        return Objects.equals(this.bizType, param.getDomesticIntl());
    }
}
```
