# Anemic Model vs DDD — Side-by-Side Comparison


## 目录
- [Scenario](#scenario)
- [Anemic Model (Common Anti-Pattern)](#anemic-model-common-anti-pattern)
  - [Entity — Data Bag Only](#entity-—-data-bag-only)
  - [Service — All Logic in Procedural Code](#service-—-all-logic-in-procedural-code)
  - [Problems](#problems)
- [DDD Model (This Framework)](#ddd-model-this-framework)
  - [Domain Layer — Business Logic Encapsulated](#domain-layer-—-business-logic-encapsulated)
  - [Application Layer — Scene Orchestration Only](#application-layer-—-scene-orchestration-only)
- [Side-by-Side Comparison](#side-by-side-comparison)
- [When Anemic Model Hurts Most](#when-anemic-model-hurts-most)
- [Migration Path (Anemic → DDD)](#migration-path-anemic-→-ddd)

Same business scenario implemented both ways: **"Create an order and confirm payment"** — with inventory validation and price verification.

---

## Scenario

User places an online order. System must:
1. Validate input parameters
2. Check inventory sufficiency (external service)
3. Verify price hasn't changed (external service)
4. Create order with business rules (amount limit, status validation)
5. Persist the order
6. Return result

---

## Anemic Model (Common Anti-Pattern)

### Entity — Data Bag Only

```java
// Entity: just getters/setters, zero behavior
@Data
public class Order {
    private Long id;
    private String orderNo;
    private Long buyerId;
    private String productId;
    private Integer quantity;
    private Long amount;
    private Integer status;  // 0-pending, 1-paid, 2-cancelled
    private Date gmtCreate;
    private Date gmtModified;
}

@Data
public class OrderItem {
    private Long id;
    private Long orderId;
    private String productName;
    private Long price;
    private Integer quantity;
}
```

### Service — All Logic in Procedural Code

```java
// "Service" contains ALL logic — business rules + orchestration + persistence
@Service
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private OrderItemMapper orderItemMapper;
    @Autowired
    private InventoryClient inventoryClient;  // direct external dependency
    @Autowired
    private PriceClient priceClient;

    public ResultDO<Order> createOrder(CreateOrderRequest req) {
        // 1. Validation scattered in service
        if (req.getProductId() == null) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Product ID required");
        }
        if (req.getQuantity() == null || req.getQuantity() <= 0) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Quantity must be > 0");
        }

        // 2. External calls mixed with business logic
        InventoryResponse invResp = inventoryClient.check(req.getProductId(), req.getQuantity());
        if (!invResp.isSufficient()) {
            return ResultDO.buildFailResult("INVENTORY_NOT_ENOUGH", "Insufficient inventory");
        }

        PriceResponse priceResp = priceClient.checkPrice(req.getProductId(), req.getPrice());
        if (!priceResp.isValid()) {
            return ResultDO.buildFailResult("PRICE_INVALID", "Price changed, please refresh");
        }

        // 3. Business rules inline — duplicated across every "create" method
        if (req.getAmount() < 100) {
            return ResultDO.buildFailResult("AMOUNT_TOO_LOW", "Minimum order 100");
        }
        if (req.getAmount() > 50000 && !req.isVip()) {
            return ResultDO.buildFailResult("LIMIT_EXCEEDED", "Non-VIP max 50000");
        }

        // 4. Manual DB operations interleaved with logic
        Order order = new Order();
        order.setOrderNo(generateOrderNo());
        order.setBuyerId(req.getBuyerId());
        order.setProductId(req.getProductId());
        order.setQuantity(req.getQuantity());
        order.setAmount(req.getAmount());
        order.setStatus(0); // pending
        order.setGmtCreate(new Date());
        orderMapper.insert(order);

        OrderItem item = new OrderItem();
        item.setOrderId(order.getId());
        item.setProductName(req.getProductName());
        item.setPrice(req.getPrice());
        item.setQuantity(req.getQuantity());
        orderItemMapper.insert(item);

        return ResultDO.buildSuccessResult(order);
    }
}
```

### Problems

| Problem | Consequence |
|---------|-------------|
| Business rules in Service | Duplicated across `createOrderOnline`, `createOrderManual`, `createOrderBatch` — or worse, inconsistent |
| Entity has no behavior | "Order" is just a struct — can be put in any invalid state by any code |
| Service depends on everything | `OrderService` has 5+ dependencies, impossible to unit test without mocks |
| No aggregate boundary | Any code can modify `order.status = 99` — no consistency guarantee |
| Transaction logic ad-hoc | Developer must remember to lock, validate, and persist in correct order every time |
| Hard to change | Adding a new order creation scene (e.g., group buy) requires copying all the inline rules |

---

## DDD Model (This Framework)

### Domain Layer — Business Logic Encapsulated

#### Aggregate Root
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderAggregate extends BaseAggregate<Long> {
    private String orderNo;
    private Long buyerId;
    private String productId;
    private Field<Integer> quantity;
    private Field<Long> amount;
    private OrderStatusEnum status;
    private List<OrderItemEntity> items;

    /** Write method: create order — business rules HERE */
    public void create(CreateOrderParam param) {
        // Parameter validation
        if (param == null) {
            throw new AggregateException("Param must not be null");
        }
        // Business rules — cohesive, single source of truth
        if (param.getAmount() < 100) {
            throw new AggregateException("AMOUNT_TOO_LOW", "Minimum order amount is 100");
        }
        if (param.getAmount() > 50000 && !param.isVip()) {
            throw new AggregateException("LIMIT_EXCEEDED", "Non-VIP max 50000");
        }

        this.orderNo = OrderNoGenerator.generate();
        this.buyerId = param.getBuyerId();
        this.productId = param.getProductId();
        this.quantity = Field.of(param.getQuantity());
        this.amount = Field.of(param.getAmount());
        this.status = OrderStatusEnum.PENDING;
        this.gmtCreate = new Date();
    }

    /** Write method: confirm payment */
    public void confirmPayment(ConfirmPaymentParam param) {
        if (!this.status.canPay()) {
            throw new AggregateException("ORDER_CANNOT_PAY", "Order status " + this.status + " cannot pay");
        }
        this.status = OrderStatusEnum.PAID;
        this.paymentChannel = param.getPaymentChannel();
    }

    /** Calculate method (side-effect-free) */
    public Long calculateTotalAmount() {
        return this.items.stream()
            .mapToLong(item -> item.getPrice().get() * item.getQuantity().get())
            .sum();
    }
}
```

#### DomainService
```java
@Slf4j
@Service
public class OrderDomainServiceImpl implements OrderDomainService {

    @Resource
    private OrderRepository orderRepository;

    @Override
    public ResultDO<OrderAggregate> createOrder(CreateOrderParam param) {
        LevelLock lock = orderRepository.buildLock("order:create:" + param.getBuyerId());
        try {
            if (!lock.tryLock()) {
                return ResultDO.buildFailResult("LOCK_FAIL", "Failed to acquire lock");
            }

            // 1. Create aggregate — business rules inside aggregate.create()
            OrderAggregate order = new OrderAggregate();
            order.create(param);

            // 2. Persist — Repository handles all DB details
            ResultDO<Void> saveResult = orderRepository.save(order);
            if (!saveResult.isSuccess()) {
                return ResultDO.buildFailResult(saveResult.getMsg());
            }

            return ResultDO.buildSuccessResult(order);
        } catch (AggregateException e) {
            log.error("Create order aggregate error, param: {}", param, e);
            return ResultDO.buildFailResult(e.getCode(), e.getMsg());
        } catch (Throwable e) {
            log.error("Create order system error, param: {}", param, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        } finally {
            lock.unlock();
        }
    }
}
```

### Application Layer — Scene Orchestration Only

```java
@Slf4j
@Service
public class OrderAppServiceImpl implements OrderAppService {

    @Autowired
    private OrderDomainService orderDomainService;
    @Autowired
    private InventoryAdaptor inventoryAdaptor;
    @Autowired
    private PriceAdaptor priceAdaptor;

    /** Scene: online order — validate inventory + price before creating */
    @Override
    public ResultDO<CreateOrderResponseDTO> createOrderOnline(CreateOrderOnlineRequestDTO req) {
        try {
            // 1. Self-validation
            ResultDO checkResult = req.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // 2. Scene-specific pre-checks (Adaptor, not business rules)
            ResultDO<InventoryCheckResponseDTO> invResult = inventoryAdaptor.checkInventory(req.getProductId(), req.getQuantity());
            if (!invResult.isSuccess()) {
                return ResultDO.buildFailResult(invResult.getCode(), invResult.getMsg());
            }
            if (!invResult.getData().isSufficient()) {
                return ResultDO.buildFailResult("INVENTORY_NOT_ENOUGH", "Insufficient inventory");
            }

            ResultDO<PriceCheckResponseDTO> priceResult = priceAdaptor.checkPrice(req.getProductId(), req.getPrice());
            if (!priceResult.isSuccess()) {
                return ResultDO.buildFailResult(priceResult.getCode(), priceResult.getMsg());
            }
            if (!priceResult.getData().isValid()) {
                return ResultDO.buildFailResult("PRICE_INVALID", "Price changed");
            }

            // 3. Call domain service — business rules are in the aggregate
            CreateOrderParam param = OrderAssembler.toParam(req);
            ResultDO<OrderAggregate> domainResult = orderDomainService.createOrder(param);
            if (!domainResult.isSuccess()) {
                return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
            }

            return ResultDO.buildSuccessResult(OrderAssembler.toResponseDTO(domainResult.getData()));
        } catch (Exception e) {
            log.error("Create order online error, req: {}", req, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }

    /** Scene: manual order entry — no inventory/price checks, directly create */
    @Override
    public ResultDO<CreateOrderResponseDTO> createOrderManual(CreateOrderManualRequestDTO req) {
        try {
            ResultDO checkResult = req.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // Same domain service, different scene orchestration
            CreateOrderParam param = OrderAssembler.toParam(req);
            ResultDO<OrderAggregate> domainResult = orderDomainService.createOrder(param);
            if (!domainResult.isSuccess()) {
                return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
            }

            return ResultDO.buildSuccessResult(OrderAssembler.toResponseDTO(domainResult.getData()));
        } catch (Exception e) {
            log.error("Create order manual error, req: {}", req, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }

    /** Future scene: batch import orders — just add method, domain unchanged */
}
```

---

## Side-by-Side Comparison

| Dimension | Anemic Model | DDD (This Framework) |
|-----------|-------------|---------------------|
| **Business rules location** | Scattered in Service methods, copied across scenes | Single source of truth in Aggregate methods |
| **Entity** | Data bag (getters/setters only) | Rich object with behavior + Field\<T\> immutability |
| **Consistency boundary** | None — any code can modify any field | Aggregate enforces invariants; only methods can change state |
| **Service responsibility** | Everything (validation + rules + orchestration + persistence) | DomainService: business flow. AppService: scene orchestration only |
| **New scene (e.g. batch create)** | Copy inline rules from existing method, or extract to shared method (still in wrong layer) | Add AppService method — domain methods reused as-is |
| **Unit testing** | Mock 5+ dependencies to test business rules | Test aggregate methods with zero mocks. Test DomainService with only Repository mock |
| **Business rule change** | Find and update every Service method that has the rule | Change one aggregate method |
| **External dependency** | Service directly calls HTTP client | Adaptor interface in Application layer, implementation isolated |
| **Concurrency** | Developer must remember to lock | DomainService template enforces lock → load → execute → persist → unlock |
| **Error handling** | Exceptions may propagate to caller | All errors caught and converted to ResultDO |
| **Code navigation** | Open OrderService (1000+ lines), search for rule | Open OrderAggregate — all business rules in one 50-200 line file |

---

## When Anemic Model Hurts Most

```
Initial: 1 entity, 3 use cases, 1 developer
  → Anemic works fine. Service is 200 lines.

6 months later: 5 entities, 15 use cases, 3 developers
  → createOrderOnline: validates amount >= 100
  → createOrderManual: forgot to validate amount >= 100
  → createOrderBatch: validates amount >= 50 (copied wrong)
  → Business rules inconsistent across scenes. Bug reports start.

12 months later: 20 entities, 50 use cases, 8 developers
  → OrderService is 3000 lines. Nobody fully understands it.
  → Adding a field requires touching Service + 3 Mappers + 5 tests.
  → New developer changes "status" directly instead of using the method.
  → Data corruption incident. Weekend war room.
```

**DDD prevents this by making the right thing the only thing.** You can't create an order without going through `OrderAggregate.create()`. You can't change status without going through `confirmPayment()`. The aggregate IS the consistency boundary.

---

## Migration Path (Anemic → DDD)

1. **Identify the aggregate boundary** — what entities must be consistent together?
2. **Move business rules into the aggregate** — start with validation and state transitions
3. **Replace plain types with Field\<T\>** — enforces immutability incrementally
4. **Extract DomainService** — separates business flow from Application orchestration
5. **Introduce Repository interface** — Application no longer touches Mapper directly
6. **Wrap external calls in Adaptor** — Application no longer touches HTTP clients
7. **Add CQRS** — split read and write paths

Each step is independently deployable. Start with the most problematic aggregate.
