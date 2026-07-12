# Quick-Start Tutorial — End-to-End "Create Order"

Walk through building a complete "create online order" feature across all 6 layers. Copy-paste ready.

---

## Scenario

User places an online order. The system:
1. Receives HTTP POST request with order details
2. Validates input
3. Checks inventory (external service)
4. Verifies price (external service)
5. Applies business rules: minimum amount 100, non-VIP max 50000
6. Creates order and persists to database
7. Returns order ID and status

**Mode:** Write Mode
**Call chain:** `Controller → AppService → Adaptor (inventory/price) → DomainService → Aggregate → Repository → DB`

---

## File Manifest

```
# Layer: client
client/order/req/CreateOrderRequestDTO.java

# Layer: model (already exists, reference only)
model/common/DomesticIntlEnum.java

# Layer: domain
domain/order/model/aggregate/OrderAggregate.java
domain/order/model/entity/OrderItemEntity.java
domain/order/model/param/CreateOrderParam.java
domain/order/model/result/CreateOrderResult.java
domain/order/service/OrderDomainService.java
domain/order/service/OrderDomainServiceImpl.java
domain/order/repository/OrderRepository.java

# Layer: application
application/order/scenario/OrderAppService.java
application/order/scenario/OrderAppServiceImpl.java
application/order/assembler/OrderAssembler.java

# Layer: infrastructure
infrastructure/order/repository/OrderRepositoryImpl.java
infrastructure/order/mysql/po/OrderPO.java
infrastructure/order/mysql/po/OrderItemPO.java
infrastructure/order/mysql/mapper/OrderMapper.java
infrastructure/order/mysql/mapper/OrderItemMapper.java
infrastructure/order/converter/OrderConverter.java

# Layer: adaptor (output — called by Application)
application/order/adaptor/InventoryAdaptor.java          # interface in application
application/order/adaptor/PriceAdaptor.java               # interface in application
adaptor/order/output/InventoryAdaptorImpl.java            # impl in adaptor
adaptor/order/output/PriceAdaptorImpl.java                # impl in adaptor

# Layer: adaptor (input — entry point)
adaptor/order/input/OrderController.java
```

---

## Step 1: Client Layer — Request DTO

```java
// client/order/req/CreateOrderRequestDTO.java
package com.example.client.order.req;

@Data
@EqualsAndHashCode(callSuper = true)
public class CreateOrderRequestDTO extends BaseDTO {
    private static final long serialVersionUID = 1L;

    private Long buyerId;
    private String productId;
    private String productName;
    private Integer quantity;
    private Long price;
    private Long amount;
    private Boolean isVip;

    public ResultDO check() {
        if (productId == null || productId.isEmpty()) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Product ID required");
        }
        if (quantity == null || quantity <= 0) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Quantity must be > 0");
        }
        if (price == null || price <= 0) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Price must be > 0");
        }
        if (amount == null || amount <= 0) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Amount must be > 0");
        }
        return ResultDO.buildSuccessResult();
    }
}
```

---

## Step 2: Domain Layer — Aggregate, DomainService, Repository Interface

### Aggregate

```java
// domain/order/model/aggregate/OrderAggregate.java
package com.example.domain.order.model.aggregate;

@Data
@EqualsAndHashCode(callSuper = true)
public class OrderAggregate extends BaseAggregate<Long> {
    private String orderNo;
    private Long buyerId;
    private String productId;
    private Integer quantity;
    private Long amount;
    private OrderStatusEnum status;  // PENDING, PAID, CANCELLED
    private Date gmtCreate;
    private List<OrderItemEntity> items;

    /** Create order — all business rules HERE, single source of truth */
    public void create(CreateOrderParam param) {
        if (param == null) {
            throw new AggregateException("Param must not be null");
        }
        if (param.getAmount() < 100) {
            throw new AggregateException("AMOUNT_TOO_LOW", "Minimum order amount is 100");
        }
        if (param.getAmount() > 50000 && !Boolean.TRUE.equals(param.getIsVip())) {
            throw new AggregateException("LIMIT_EXCEEDED", "Non-VIP max amount is 50000");
        }

        this.orderNo = "ORD" + System.currentTimeMillis();
        this.buyerId = param.getBuyerId();
        this.productId = param.getProductId();
        this.quantity = param.getQuantity();
        this.amount = param.getAmount();
        this.status = OrderStatusEnum.PENDING;
        this.gmtCreate = new Date();
    }

    /** Check if order can be cancelled */
    @JSONField(serialize = false)
    public boolean canCancel() {
        return this.status == OrderStatusEnum.PENDING;
    }

    /** Calculate total amount from items */
    @JSONField(serialize = false)
    public Long calculateTotalAmount() {
        if (items == null || items.isEmpty()) {
            return this.amount;
        }
        return items.stream()
            .mapToLong(item -> item.getPrice().get() * item.getQuantity().get())
            .sum();
    }
}
```

### Entity

```java
// domain/order/model/entity/OrderItemEntity.java
package com.example.domain.order.model.entity;

@Data
@EqualsAndHashCode(callSuper = true)
public class OrderItemEntity extends BaseEntity<Long> {
    private Field<Long> orderId;
    private Field<String> productName;
    private Field<Long> price;
    private Field<Integer> quantity;
}
```

### Param

```java
// domain/order/model/param/CreateOrderParam.java
package com.example.domain.order.model.param;

@Data
@EqualsAndHashCode(callSuper = true)
public class CreateOrderParam extends BaseParam {
    private Long buyerId;
    private String productId;
    private String productName;
    private Integer quantity;
    private Long price;
    private Long amount;
    private Boolean isVip;
}
```

### DomainService Interface

```java
// domain/order/service/OrderDomainService.java
package com.example.domain.order.service;

public interface OrderDomainService {
    ResultDO<OrderAggregate> createOrder(CreateOrderParam param);
}
```

### DomainService Implementation

```java
// domain/order/service/OrderDomainServiceImpl.java
package com.example.domain.order.service;

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
                return ResultDO.buildFailResult("LOCK_FAIL", "Failed to acquire lock, retry");
            }

            // Create aggregate — business rules execute inside
            OrderAggregate order = new OrderAggregate();
            order.create(param);

            // Persist
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

### Repository Interface

```java
// domain/order/repository/OrderRepository.java
package com.example.domain.order.repository;

public interface OrderRepository extends AggregateRepository<OrderAggregate, Long> {
    ResultDO<Void> save(OrderAggregate aggregate);
    LevelLock buildLock(String lockKey);
    ResultDO<OrderAggregate> query(OrderQuery query);
}
```

---

## Step 3: Application Layer — Scene Orchestration

### Adaptor Interfaces (defined in Application, per Application needs)

```java
// application/order/adaptor/InventoryAdaptor.java
package com.example.application.order.adaptor;

public interface InventoryAdaptor {
    ResultDO<InventoryCheckResponseDTO> checkInventory(String productId, Integer quantity);
}
```

```java
// application/order/adaptor/PriceAdaptor.java
package com.example.application.order.adaptor;

public interface PriceAdaptor {
    ResultDO<PriceCheckResponseDTO> checkPrice(String productId, Long expectedPrice);
}
```

### AppService Interface

```java
// application/order/scenario/OrderAppService.java
package com.example.application.order.scenario;

public interface OrderAppService extends ApplicationCmdService {
    ResultDO<CreateOrderResponseDTO> createOrderOnline(CreateOrderRequestDTO requestDTO);
}
```

### AppService Implementation

```java
// application/order/scenario/OrderAppServiceImpl.java
package com.example.application.order.scenario;

@Slf4j
@Service
public class OrderAppServiceImpl implements OrderAppService {

    @Autowired
    private OrderDomainService orderDomainService;
    @Autowired
    private InventoryAdaptor inventoryAdaptor;
    @Autowired
    private PriceAdaptor priceAdaptor;

    @Override
    public ResultDO<CreateOrderResponseDTO> createOrderOnline(CreateOrderRequestDTO req) {
        try {
            // 1. Self-validation (RequestDTO owns its validation)
            ResultDO checkResult = req.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // 2. Scene-specific: check inventory (via Adaptor)
            ResultDO<InventoryCheckResponseDTO> invResult =
                inventoryAdaptor.checkInventory(req.getProductId(), req.getQuantity());
            if (!invResult.isSuccess()) {
                return ResultDO.buildFailResult(invResult.getCode(), invResult.getMsg());
            }
            if (!invResult.getData().isSufficient()) {
                return ResultDO.buildFailResult("INVENTORY_NOT_ENOUGH", "Insufficient inventory");
            }

            // 3. Scene-specific: verify price (via Adaptor)
            ResultDO<PriceCheckResponseDTO> priceResult =
                priceAdaptor.checkPrice(req.getProductId(), req.getPrice());
            if (!priceResult.isSuccess()) {
                return ResultDO.buildFailResult(priceResult.getCode(), priceResult.getMsg());
            }
            if (!priceResult.getData().isValid()) {
                return ResultDO.buildFailResult("PRICE_INVALID", "Price changed, please refresh");
            }

            // 4. Call domain service — business rules are in aggregate, not here
            CreateOrderParam param = OrderAssembler.toParam(req);
            ResultDO<OrderAggregate> domainResult = orderDomainService.createOrder(param);
            if (!domainResult.isSuccess()) {
                return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
            }

            // 5. Return response
            return ResultDO.buildSuccessResult(
                OrderAssembler.toCreateOrderResponseDTO(domainResult.getData()));
        } catch (Exception e) {
            log.error("Create order online error, req: {}", req, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }
}
```

### Assembler

```java
// application/order/assembler/OrderAssembler.java
package com.example.application.order.assembler;

public class OrderAssembler {

    public static CreateOrderParam toParam(CreateOrderRequestDTO req) {
        CreateOrderParam param = new CreateOrderParam();
        param.setBuyerId(req.getBuyerId());
        param.setProductId(req.getProductId());
        param.setProductName(req.getProductName());
        param.setQuantity(req.getQuantity());
        param.setPrice(req.getPrice());
        param.setAmount(req.getAmount());
        param.setIsVip(req.getIsVip());
        return param;
    }

    public static CreateOrderResponseDTO toCreateOrderResponseDTO(OrderAggregate aggregate) {
        CreateOrderResponseDTO dto = new CreateOrderResponseDTO();
        dto.setOrderId(aggregate.getId());
        dto.setOrderNo(aggregate.getOrderNo());
        dto.setStatus(aggregate.getStatus().name());
        dto.setAmount(aggregate.getAmount());
        return dto;
    }
}
```

---

## Step 4: Infrastructure Layer — Persistence

### PO

```java
// infrastructure/order/mysql/po/OrderPO.java
package com.example.infrastructure.order.mysql.po;

@Data
public class OrderPO {
    private Long id;
    private String orderNo;
    private Long buyerId;
    private String productId;
    private Integer quantity;
    private Long amount;
    private Integer orderStatus;  // DB value: 0=PENDING, 1=PAID, 2=CANCELLED
    private Date gmtCreate;
    private Date gmtModified;
}
```

### Mapper

```java
// infrastructure/order/mysql/mapper/OrderMapper.java
package com.example.infrastructure.order.mysql.mapper;

public interface OrderMapper {
    int insert(OrderPO po);
    int updateById(OrderPO po);
    OrderPO selectById(Long id);
}
```

### Converter

```java
// infrastructure/order/converter/OrderConverter.java
package com.example.infrastructure.order.converter;

public class OrderConverter {

    /** PO → Aggregate — pure field mapping + enum conversion */
    public static OrderAggregate toAggregate(OrderPO po) {
        if (po == null) return null;
        OrderAggregate aggregate = new OrderAggregate();
        aggregate.setId(po.getId());
        aggregate.setOrderNo(po.getOrderNo());
        aggregate.setBuyerId(po.getBuyerId());
        aggregate.setProductId(po.getProductId());
        aggregate.setQuantity(po.getQuantity());
        aggregate.setAmount(po.getAmount());
        aggregate.setStatus(OrderStatusEnum.getByCode(po.getOrderStatus()));
        aggregate.setGmtCreate(po.getGmtCreate());
        return aggregate;
    }

    /** Aggregate → PO — pure field mapping + enum conversion */
    public static OrderPO toPO(OrderAggregate aggregate) {
        if (aggregate == null) return null;
        OrderPO po = new OrderPO();
        po.setId(aggregate.getId());
        po.setOrderNo(aggregate.getOrderNo());
        po.setBuyerId(aggregate.getBuyerId());
        po.setProductId(aggregate.getProductId());
        po.setQuantity(aggregate.getQuantity());
        po.setAmount(aggregate.getAmount());
        if (aggregate.getStatus() != null) {
            po.setOrderStatus(aggregate.getStatus().getCode());
        }
        po.setGmtCreate(aggregate.getGmtCreate());
        po.setGmtModified(new Date());
        return po;
    }
}
```

### Repository Implementation

```java
// infrastructure/order/repository/OrderRepositoryImpl.java
package com.example.infrastructure.order.repository;

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
            OrderPO po = OrderConverter.toPO(aggregate);

            if (aggregate.getId() == null) {
                orderMapper.insert(po);
                aggregate.setId(po.getId());  // backfill generated ID
            } else {
                int affected = orderMapper.updateById(po);
                if (affected == 0) {
                    return ResultDO.buildFailResult("UPDATE_FAIL", "Update failed, data may be stale");
                }
            }

            // Save child entities
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
            return ResultDO.buildFailResult("DB_SAVE_ERROR", "Save order error");
        }
    }

    @Override
    public LevelLock buildLock(String lockKey) {
        return new LevelLock(lockKey);
    }

    @Override
    public ResultDO<OrderAggregate> query(OrderQuery query) {
        try {
            OrderPO po = orderMapper.selectById(query.getId());
            if (po == null) {
                return ResultDO.buildSuccessResult(null);
            }
            OrderAggregate aggregate = OrderConverter.toAggregate(po);
            // Load child entities
            List<OrderItemPO> itemPOs = orderItemMapper.selectByOrderId(po.getId());
            aggregate.setItems(OrderItemConverter.toEntityList(itemPOs));
            return ResultDO.buildSuccessResult(aggregate);
        } catch (Exception e) {
            log.error("Query order failed, query: {}", query, e);
            return ResultDO.buildFailResult("DB_QUERY_ERROR", "Query order error");
        }
    }
}
```

---

## Step 5: Adaptor Layer — Input & Output

### Input Adaptor — HTTP Entry Point

```java
// adaptor/order/input/OrderController.java
package com.example.adaptor.order.input;

@RestController
@RequestMapping("/api/order")
public class OrderController {

    @Autowired
    private OrderAppService orderAppService;

    @PostMapping("/create")
    public ResultDO<CreateOrderResponseDTO> createOrder(@RequestBody CreateOrderRequestDTO req) {
        return orderAppService.createOrderOnline(req);
    }
}
```

### Output Adaptor — External Service Calls

```java
// adaptor/order/output/InventoryAdaptorImpl.java
package com.example.adaptor.order.output;

@Component
public class InventoryAdaptorImpl implements InventoryAdaptor {

    @Autowired
    private ThirdPartyInventoryClient inventoryClient;

    @Override
    public ResultDO<InventoryCheckResponseDTO> checkInventory(String productId, Integer quantity) {
        try {
            ThirdPartyInventoryResponse response = inventoryClient.check(productId, quantity);
            // Anti-corruption: only return fields Application needs
            InventoryCheckResponseDTO dto = new InventoryCheckResponseDTO();
            dto.setSufficient(response.getRemainingQty() >= quantity);
            dto.setRemainingQuantity(response.getRemainingQty());
            return ResultDO.buildSuccessResult(dto);
        } catch (Exception e) {
            log.error("Check inventory failed, productId: {}, quantity: {}", productId, quantity, e);
            return ResultDO.buildFailResult("INVENTORY_CHECK_FAIL", "Inventory check failed");
        }
    }
}
```

```java
// adaptor/order/output/PriceAdaptorImpl.java
package com.example.adaptor.order.output;

@Component
public class PriceAdaptorImpl implements PriceAdaptor {

    @Autowired
    private ThirdPartyPriceClient priceClient;

    @Override
    public ResultDO<PriceCheckResponseDTO> checkPrice(String productId, Long expectedPrice) {
        try {
            ThirdPartyPriceResponse response = priceClient.getCurrentPrice(productId);
            PriceCheckResponseDTO dto = new PriceCheckResponseDTO();
            dto.setValid(Objects.equals(expectedPrice, response.getCurrentPrice()));
            dto.setCurrentPrice(response.getCurrentPrice());
            return ResultDO.buildSuccessResult(dto);
        } catch (Exception e) {
            log.error("Check price failed, productId: {}, price: {}", productId, expectedPrice, e);
            return ResultDO.buildFailResult("PRICE_CHECK_FAIL", "Price check failed");
        }
    }
}
```

---

## Step 6: Data Flow Summary

```
HTTP POST /api/order/create
  │
  ▼
OrderController
  │  CreateOrderRequestDTO
  ▼
OrderAppServiceImpl.createOrderOnline()
  │  1. req.check()                        ← self-validation
  │  2. inventoryAdaptor.checkInventory()   ← external (Adaptor)
  │  3. priceAdaptor.checkPrice()           ← external (Adaptor)
  │  4. OrderAssembler.toParam()            ← DTO → Param
  ▼
OrderDomainServiceImpl.createOrder()
  │  1. buildLock + tryLock                 ← concurrency
  │  2. new OrderAggregate().create(param)  ← business rules
  │  3. orderRepository.save(aggregate)     ← persist
  ▼
OrderRepositoryImpl.save()
  │  1. OrderConverter.toPO()               ← Aggregate → PO
  │  2. orderMapper.insert(po)              ← DB insert
  │  3. Backfill ID
  ▼
  ResultDO<OrderAggregate>
  │
  ▼
OrderAssembler.toCreateOrderResponseDTO()   ← Aggregate → ResponseDTO
  │
  ▼
  ResultDO<CreateOrderResponseDTO> → HTTP 200 JSON
```

---

## How to Add a New Scene

**Scenario:** "Manual order entry" — no inventory or price checks.

Add ONE method to `OrderAppServiceImpl`:

```java
@Override
public ResultDO<CreateOrderResponseDTO> createOrderManual(CreateOrderManualRequestDTO req) {
    try {
        ResultDO checkResult = req.check();
        if (!checkResult.isSuccess()) {
            return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
        }

        CreateOrderParam param = OrderAssembler.toParam(req);
        ResultDO<OrderAggregate> domainResult = orderDomainService.createOrder(param);
        if (!domainResult.isSuccess()) {
            return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
        }

        return ResultDO.buildSuccessResult(OrderAssembler.toCreateOrderResponseDTO(domainResult.getData()));
    } catch (Exception e) {
        log.error("Create order manual error, req: {}", req, e);
        return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
    }
}
```

No changes to domain layer. No changes to infrastructure. No duplicated business rules. Just scene orchestration differences in Application layer.
