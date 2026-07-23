# Infrastructure Layer Specification


## 目录
- [Part A: Base Rules (All Modes)](#part-a-base-rules-all-modes)
  - [A.1 Package Structure](#a1-package-structure)
  - [A.2 Core Positioning](#a2-core-positioning)
  - [A.3 Repository Implementation Naming](#a3-repository-implementation-naming)
  - [A.4 Allowed vs Forbidden](#a4-allowed-vs-forbidden)
  - [A.5 Exception Handling](#a5-exception-handling)
  - [A.6 PO (Persistent Object)](#a6-po-persistent-object)
  - [A.7 Mapper Interface](#a7-mapper-interface)
  - [A.8 Converter](#a8-converter)
- [Part B: Write Mode](#part-b-write-mode)
  - [B.1 Core Responsibilities](#b1-core-responsibilities)
  - [B.2 Return Values](#b2-return-values)
  - [B.3 Template](#b3-template)
- [Part C: Read Mode](#part-c-read-mode)
  - [C.1 Core Responsibilities](#c1-core-responsibilities)
  - [C.2 Return Values](#c2-return-values)
  - [C.3 Template](#c3-template)
- [Part D: Rule+Calculate Mode](#part-d-rule+calculate-mode)
  - [D.1 Core Responsibilities](#d1-core-responsibilities)
  - [D.2 Return Values](#d2-return-values)
  - [D.3 Template](#d3-template)

## Part A: Base Rules (All Modes)

### A.1 Package Structure

```
infrastructure/
└── {business}/                    # Per business domain (order, booking, refund)
    ├── repository/                # Repository implementations
    │   └── {Business}RepositoryImpl
    ├── mysql/
    │   ├── po/                    # Persistent Objects
    │   └── mapper/                # MyBatis Mapper interfaces
    └── converter/                 # Data converters (Aggregate ↔ PO)
```

### A.2 Core Positioning

**Infrastructure layer is the technical implementation layer.** Implements Repository interfaces defined by Domain layer, shielding all technical details (DB, cache, messaging) from Domain.

- Implements `domain` layer Repository interfaces
- Does **pure technical conversion** (aggregate ↔ PO)
- **FORBIDDEN: any business logic** — business logic belongs in Domain layer (aggregate methods, DomainService)
- Infrastructure only handles "store" and "retrieve"

#### Layer Relationships

| Relationship | Notes |
|-------------|-------|
| With `domain` | Implements Repository interfaces defined by domain, depends on `domain` module |
| With `application` | No direct dependency — Application indirectly calls via domain Repository interfaces |
| With `client` | No dependency |
| With `model` | May depend on `model` module (shared enums, common business concepts) |

### A.3 Repository Implementation Naming

| Rule | Spec | Example |
|------|------|---------|
| Class name | `{Business}RepositoryImpl` | `OrderRepositoryImpl` |
| Prefix correspondence | Must match corresponding DomainService prefix | DomainService=`OrderDomainService` → RepoImpl=`OrderRepositoryImpl` |
| Annotation | Use `@Component` | — |
| Implements | Domain-layer `{Business}Repository` | `implements OrderRepository` |

### A.4 Allowed vs Forbidden

Infrastructure layer may directly use middleware technologies but MUST NOT access external 3rd-party services.

| Dimension | ALLOWED | FORBIDDEN |
|-----------|---------|-----------|
| Module dependency | `domain`, `model` | `application`, `client`, other business system JARs |
| Technology | MyBatis, Redis, Tair, RocketMQ, MetaQ, distributed locks, Diamond, Nacos etc. | HSF, HTTP Client (3rd-party external service calls) |
| Code responsibility | Repository impl, Aggregate↔PO pure technical conversion (Converter), DB operations (Mapper), cache read/write, domain event publishing, distributed lock construction, operation logging | Business logic, business judgments in Converter, exposing technical details to domain |
| Invocation | Called via domain Repository interface | Directly called by Application layer as implementation class |

### A.5 Exception Handling

- Repository implementation exception handling must be consistent with Domain layer patterns
- DB operation exceptions MUST be caught and converted to `ResultDO` — FORBIDDEN: throwing technical exceptions upward (e.g., `SQLException`)
- Logs must include key business parameters for troubleshooting

```java
// CORRECT: Catch exception, return ResultDO
@Override
public ResultDO<OrderAggregate> query(OrderQuery query) {
    try {
        OrderPO po = orderMapper.selectById(query.getId());
        return ResultDO.buildSuccessResult(OrderConverter.toAggregate(po));
    } catch (Exception e) {
        log.error("Query order failed, query: {}", query, e);
        return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order data error");
    }
}

// WRONG: Throw technical exception directly
@Override
public ResultDO<OrderAggregate> query(OrderQuery query) {
    OrderPO po = orderMapper.selectById(query.getId()); // exception propagates directly
    return ResultDO.buildSuccessResult(OrderConverter.toAggregate(po));
}
```

### A.6 PO (Persistent Object)

PO is a 1:1 mapping to database tables. Used ONLY within Infrastructure layer, FORBIDDEN from exposure to Domain or Application.

#### Naming

| Rule | Spec | Example |
|------|------|---------|
| Class name | `{TableBusinessName}PO` | `OrderPO`, `OrderItemPO` |
| Location | `infrastructure/{business}/mysql/po/` | — |
| Field naming | Match DB column names, camelCase | `orderId`, `orderStatus` |

#### Design Principles
- PO is **pure data carrier** — only fields and getter/setter, FORBIDDEN: business methods
- PO maps 1:1 to DB table structure, field types match DB column types
- PO FORBIDDEN from being referenced by domain, application, or client layers

#### Template
```java
@Data
public class OrderPO {
    private Long id;
    private String orderNo;
    private Long buyerId;
    private String productId;
    private Integer orderStatus;   // DB stored value: 0-pending, 1-paid, 2-cancelled
    private Long amount;           // Amount in cents
    private String logisticsNo;
    private Date gmtCreate;
    private Date gmtModified;
}
```

### A.7 Mapper Interface

MyBatis database access interface. Executes SQL operations.

#### Naming

| Rule | Spec | Example |
|------|------|---------|
| Interface name | `{TableBusinessName}Mapper` | `OrderMapper`, `OrderItemMapper` |
| Location | `infrastructure/{business}/mysql/mapper/` | — |
| Method naming | Verbs expressing operation intent | `insert`, `updateById`, `selectById`, `selectByCondition` |

#### Design Principles
- Mapper called ONLY by same-domain RepositoryImpl, FORBIDDEN from direct domain/application access
- Mapper params and returns MUST use PO or primitive types, FORBIDDEN: aggregates or DTOs

#### Template
```java
public interface OrderMapper {
    int insert(OrderPO po);
    int updateById(OrderPO po);
    OrderPO selectById(Long id);
    OrderPO selectByOrderNo(String orderNo);
    List<OrderPO> selectByCondition(OrderQueryCondition condition);
}
```

### A.8 Converter

Handles **pure technical conversion** between aggregates and POs. Core Infrastructure component.

#### Naming

| Rule | Spec | Example |
|------|------|---------|
| Class name | `{Business}Converter` | `OrderConverter` |
| Location | `infrastructure/{business}/converter/` | — |
| Method naming | `toAggregate` (PO→Aggregate), `toPO` (Aggregate→PO) | — |
| Method type | Static methods | — |

#### Design Principles
- Converter does **field mapping only** — FORBIDDEN: business judgment logic
- Must handle nested Entity, Value Object conversions within aggregates
- Enum conversion: PO stores DB values (Integer), aggregate uses domain enums, Converter handles mapping
- Null handling: return null when input is null, avoid NPE

#### Converter vs Assembler

| Dimension | Converter (Infrastructure) | Assembler (Application) |
|-----------|--------------------------|------------------------|
| Converts | Aggregate ↔ PO | RequestDTO/ResponseDTO ↔ Domain Param/Aggregate |
| Layer | Infrastructure | Application |
| Responsibility | Technical persistence conversion | Business-level DTO↔Domain conversion |

#### Template
```java
public class OrderConverter {

    /** PO → Aggregate (includes nested entity/value object conversion) */
    public static OrderAggregate toAggregate(OrderPO po) {
        if (po == null) return null;
        OrderAggregate aggregate = new OrderAggregate();
        aggregate.setId(po.getId());
        aggregate.setOrderNo(po.getOrderNo());
        aggregate.setBuyerId(po.getBuyerId());
        aggregate.setAmount(po.getAmount());
        aggregate.setLogisticsNo(po.getLogisticsNo());
        // Enum: DB Integer → Domain Enum
        aggregate.setStatus(OrderStatusEnum.getByCode(po.getOrderStatus()));
        return aggregate;
    }

    /** Aggregate → PO */
    public static OrderPO toPO(OrderAggregate aggregate) {
        if (aggregate == null) return null;
        OrderPO po = new OrderPO();
        po.setId(aggregate.getId());
        po.setOrderNo(aggregate.getOrderNo());
        po.setBuyerId(aggregate.getBuyerId());
        po.setAmount(aggregate.getAmount());
        po.setLogisticsNo(aggregate.getLogisticsNo());
        // Enum: Domain Enum → DB Integer
        if (aggregate.getStatus() != null) {
            po.setOrderStatus(aggregate.getStatus().getCode());
        }
        return po;
    }

    /** PO list → Aggregate list */
    public static List<OrderAggregate> toAggregateList(List<OrderPO> poList) {
        if (CollectionUtils.isEmpty(poList)) return Collections.emptyList();
        return poList.stream().map(OrderConverter::toAggregate).collect(Collectors.toList());
    }
}
```

---

## Part B: Write Mode

### B.1 Core Responsibilities

- **save:** Handle aggregate insert and update (determine insert vs update)
- **query:** Provide data for DomainService to load aggregates
- **buildLock:** Build distributed lock for concurrency safety
- **Optional:** Publish domain events, write operation logs

### B.2 Return Values

Must match domain Repository interface:

| Method Type | Return | Notes |
|------------|--------|-------|
| save | `ResultDO<Void>` | Success or error code on failure |
| query | `ResultDO<AggregateType>` | Aggregate or null |
| buildLock | `LevelLock` | Distributed lock object |

### B.3 Template

```java
@Slf4j
@Component
public class OrderRepositoryImpl implements OrderRepository {

    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private OrderItemMapper orderItemMapper;

    @Override
    public ResultDO<Void> save(OrderAggregate aggregate) {
        try {
            OrderPO orderPO = OrderConverter.toPO(aggregate);

            if (aggregate.getId() == null) {
                orderMapper.insert(orderPO);
                aggregate.setId(orderPO.getId()); // backfill ID
            } else {
                int affectedRows = orderMapper.updateById(orderPO);
                if (affectedRows == 0) {
                    return ResultDO.buildFailResult("UPDATE_FAIL", "Update failed, data may have been modified");
                }
            }

            // Save child entities (e.g., order items)
            if (CollectionUtils.isNotEmpty(aggregate.getItems())) {
                for (OrderItemEntity item : aggregate.getItems()) {
                    OrderItemPO itemPO = OrderItemConverter.toPO(item, aggregate.getId());
                    if (item.getId() == null) {
                        orderItemMapper.insert(itemPO);
                        item.setId(itemPO.getId());
                    } else {
                        orderItemMapper.updateById(itemPO);
                    }
                }
            }

            return ResultDO.buildSuccessResult(null);
        } catch (Exception e) {
            log.error("Save order failed, aggregateId: {}", aggregate.getId(), e);
            return ResultDO.buildFailResult("DB_SAVE_ERROR", "Save order data error");
        }
    }

    @Override
    public LevelLock buildLock(String lockKey) {
        return new LevelLock(lockKey);
    }

    @Override
    public ResultDO<OrderAggregate> query(OrderQuery query) {
        try {
            OrderPO orderPO = orderMapper.selectById(query.getId());
            if (orderPO == null) {
                return ResultDO.buildSuccessResult(null);
            }
            List<OrderItemPO> itemPOList = orderItemMapper.selectByOrderId(orderPO.getId());

            OrderAggregate aggregate = OrderConverter.toAggregate(orderPO);
            aggregate.setItems(OrderItemConverter.toEntityList(itemPOList));

            return ResultDO.buildSuccessResult(aggregate);
        } catch (Exception e) {
            log.error("Query order failed, query: {}", query, e);
            return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order data error");
        }
    }
}
```

---

## Part C: Read Mode

### C.1 Core Responsibilities
- Pure data query and format conversion only, NO business logic
- Query methods return aggregate (as data carrier) or Result objects
- Support single and list queries

### C.2 Return Values

| Method Type | Return | Notes |
|------------|--------|-------|
| Single query | `ResultDO<AggregateType>` | `ResultDO.buildSuccessResult(null)` when not found |
| List query | `ResultDO<List<AggregateType>>` | Empty list when no data |

### C.3 Template
```java
@Slf4j
@Component
public class OrderRepositoryImpl implements OrderRepository {

    @Autowired
    private OrderMapper orderMapper;

    @Override
    public ResultDO<OrderAggregate> getOrderDetail(Long orderId) {
        try {
            OrderPO po = orderMapper.selectById(orderId);
            if (po == null) {
                return ResultDO.buildSuccessResult(null);
            }
            return ResultDO.buildSuccessResult(OrderConverter.toAggregate(po));
        } catch (Exception e) {
            log.error("Query order detail failed, orderId: {}", orderId, e);
            return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order detail error");
        }
    }

    @Override
    public ResultDO<List<OrderAggregate>> queryOrderList(QueryOrderListQuery query) {
        try {
            List<OrderPO> poList = orderMapper.selectByCondition(query);
            return ResultDO.buildSuccessResult(OrderConverter.toAggregateList(poList));
        } catch (Exception e) {
            log.error("Query order list failed, query: {}", query, e);
            return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order list error");
        }
    }
}
```

---

## Part D: Rule+Calculate Mode

### D.1 Core Responsibilities
- Load rule aggregate collections from database or config center
- Rule data is typically **read-only** — no write operations
- Rule aggregates used by DomainService for matching and calculation — **rule aggregate state is never modified**

### D.2 Return Values

| Method Type | Return | Notes |
|------------|--------|-------|
| Query all rules | `ResultDO<List<RuleAggregateType>>` | All rule aggregate list |
| Query rules by condition | `ResultDO<List<RuleAggregateType>>` | Filtered by business condition |

### D.3 Template
```java
@Slf4j
@Component
public class BonusRuleRepositoryImpl implements BonusRuleRepository {

    @Autowired
    private BonusRuleMapper bonusRuleMapper;
    @Autowired
    private BonusRuleDetailMapper bonusRuleDetailMapper;

    @Override
    public ResultDO<List<BonusRuleAggregate>> queryAllRule() {
        try {
            // 1. Query all rule master table POs
            List<BonusRulePO> rulePOList = bonusRuleMapper.selectAll();
            if (CollectionUtils.isEmpty(rulePOList)) {
                return ResultDO.buildSuccessResult(Collections.emptyList());
            }

            // 2. Query rule detail POs
            List<Long> ruleIds = rulePOList.stream()
                .map(BonusRulePO::getId)
                .collect(Collectors.toList());
            List<BonusRuleDetailPO> detailPOList = bonusRuleDetailMapper.selectByRuleIds(ruleIds);

            // 3. Group by rule ID
            Map<Long, List<BonusRuleDetailPO>> detailMap = detailPOList.stream()
                .collect(Collectors.groupingBy(BonusRuleDetailPO::getRuleId));

            // 4. PO → Rule Aggregate (with nested Entity)
            List<BonusRuleAggregate> aggregateList = rulePOList.stream()
                .map(rulePO -> {
                    BonusRuleAggregate aggregate = BonusRuleConverter.toAggregate(rulePO);
                    List<BonusRuleDetailPO> details = detailMap.getOrDefault(rulePO.getId(), Collections.emptyList());
                    aggregate.setBonusRuleEntity(BonusRuleConverter.toEntity(details));
                    return aggregate;
                })
                .collect(Collectors.toList());

            return ResultDO.buildSuccessResult(aggregateList);
        } catch (Exception e) {
            log.error("Query bonus rules failed", e);
            return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query bonus rule data error");
        }
    }
}
```
