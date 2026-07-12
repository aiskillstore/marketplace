# Application Layer Specification

## Part A: Base Rules (All Modes)

### A.1 Package Structure

```
application/
└── {business}/               # Per business domain (order, booking, refund)
    ├── scenario/             # Scene orchestration (AppService implementations)
    └── assembler/            # DTO ↔ Domain object mapping
```

### A.2 Core Positioning

**Application layer is scene orchestration (unstable); Domain layer is core business logic (stable).**

- Application layer orchestrates domain services, Adaptors, and Repositories per business scene — this is where requirements change most frequently
- Domain layer (DomainService, aggregates) encapsulates **stable core business rules** — invariant across scenes
- Same domain service method reused by **multiple Application scene methods**; scene differences expressed in Application orchestration logic

**Example:** `orderDomainService.createOrder()` is the single stable domain method. Application provides two scene methods:
- `createOrderOnline` — validates inventory and price before creating (complex orchestration)
- `createOrderManual` — creates order directly (simple orchestration)

Future scenes (e.g., batch import) only need new Application methods — domain service stays unchanged.

### A.3 CQRS (Command Query Responsibility Segregation)

Application layer splits into:
- **Command (Write):** `{AggregateName}AppService extends ApplicationCmdService` — business changes only
- **Query (Read):** `{AggregateName}QueryAppService extends ApplicationQueryService` — data queries only

**Rule:** Command layer MUST NOT call Query layer interfaces.

### A.4 Parameters and Return Values

| Rule | Spec |
|------|------|
| Input parameter | MUST use `RequestDTO`, FORBIDDEN: primitive types or Map |
| Parameter validation | Via `requestDTO.check()` returning `ResultDO`, FORBIDDEN: writing validation logic in AppService |
| Return value | Always `ResultDO<T>`, generic is ResponseDTO |
| Error handling | Errors returned via `ResultDO` error codes, FORBIDDEN: throwing exceptions to caller |

```java
// Parameter self-validation (by RequestDTO itself)
ResultDO checkResult = requestDTO.check();
if (!checkResult.isSuccess()) {
    return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
}

// Success
return ResultDO.buildSuccessResult(responseDTO);

// Error
return ResultDO.buildFailResult("ORDER_NOT_FOUND", "Order not found");
```

### A.5 DTO Location

| Scenario | Location | Notes |
|----------|----------|-------|
| Exposed as external API | `client` module `req/` and `res/` packages | External callers depend on these DTOs |
| Application-internal only | `application` module `model/` package | Not exposed externally, only for internal orchestration |

**Rule:** If a DTO is transparently passed to external callers by Input Adaptor (Controller, HSF, etc.), put it in `client`. If only used within Application layer flow, put it in `application/model/`.

### A.6 Dependency Rules

**Allowed:**
- `domain` module
- `client` module
- `model` module
- I/O-free utility classes

**Forbidden:**
- Other business domain module JARs
- Middleware (message middleware, OSS, etc.)

### A.7 Behavior Constraints

**Allowed:**
- Call DomainService
- Use Repository interface
- Call Adaptor for external data (cross-domain queries)
- DTO ↔ Domain object conversion (via Assembler)

**Forbidden:**
- Direct database access (use Repository)
- Direct external service access (use Adaptor)
- Core business logic (belongs in DomainService or aggregates)

**Important distinction:** Application layer MAY include **orchestration flow control** (e.g., checking Adaptor results, early returns with error codes). This is scene orchestration, not business logic. Core business logic = aggregate state transitions, business calculation formulas, rule matching — these MUST stay in Domain layer.

### A.8 Assembler

**Naming:** `{AggregateName}Assembler` or `{BusinessScene}Assembler`

```java
public class OrderAssembler {

    /** RequestDTO → Domain Param */
    public static CreateOrderParam toParam(CreateOrderRequestDTO requestDTO) {
        CreateOrderParam param = new CreateOrderParam();
        param.setProductId(requestDTO.getProductId());
        param.setQuantity(requestDTO.getQuantity());
        return param;
    }

    /** Aggregate → ResponseDTO */
    public static CreateOrderResponseDTO toResponseDTO(OrderAggregate order) {
        CreateOrderResponseDTO responseDTO = new CreateOrderResponseDTO();
        responseDTO.setOrderId(order.getId());
        responseDTO.setStatus(order.getStatus());
        return responseDTO;
    }
}
```

---

## Part B: Write Mode

### B.1 Naming

| Rule | Spec | Example |
|------|------|---------|
| Interface | `{AggregateName}AppService` | `OrderAppService` |
| Implementation | `{AggregateName}AppServiceImpl` | `OrderAppServiceImpl` |
| Inheritance | MUST extend `ApplicationCmdService` | — |
| Method naming | Business verbs, NOT technical verbs (`save`, `update`) | `createOrder`, `confirmPayment` |
| Request DTO | `{MethodName}RequestDTO` | `CreateOrderRequestDTO` |
| Response DTO | `{MethodName}ResponseDTO` | `CreateOrderResponseDTO` |

### B.2 Call Chain

**Simple (e.g., manual order):**
```
Input Adaptor → AppService → DomainService → Repository
```

**Complex (e.g., online order with external validation):**
```
Input Adaptor → AppService → Adaptor (validate inventory/price)
                           → DomainService → Repository
```

### B.3 Orchestration Steps

1. Parameter self-validation (`requestDTO.check()`)
2. Fetch external data or validate preconditions via Adaptor (per scene needs)
3. Convert DTO to Domain Param (via Assembler)
4. Call DomainService (handles loading aggregate, executing business method, persisting)
5. Build ResponseDTO and return

### B.4 Template

See Part A.2 for complete online vs. manual order creation example.

---

## Part C: Read Mode

### C.1 Naming

| Rule | Spec | Example |
|------|------|---------|
| Interface | `{AggregateName}QueryAppService` | `OrderQueryAppService` |
| Implementation | `{AggregateName}QueryAppServiceImpl` | `OrderQueryAppServiceImpl` |
| Inheritance | MUST extend `ApplicationQueryService` | — |
| Method naming | Verbs with clear query intent, avoid abstract words (`process`) | `queryOrderList`, `getOrderDetail` |

### C.2 Data Sources

| Scenario | Data Source | Notes |
|----------|------------|-------|
| Intra-domain query | Repository | Get aggregate or Result, convert to DTO via Assembler |
| Cross-domain query | Adaptor | Get 3rd-party data, return directly or trim |
| Hybrid query | Repository + Adaptor | Query intra-domain first, supplement with Adaptor, assemble |

### C.3 Template (Hybrid Query)

```java
@Slf4j
@Service
public class OrderQueryAppServiceImpl implements OrderQueryAppService {

    @Autowired
    private OrderRepository orderRepository;
    @Autowired
    private LogisticsAdaptor logisticsAdaptor;

    @Override
    public ResultDO<GetOrderDetailResponseDTO> getOrderDetail(GetOrderDetailRequestDTO requestDTO) {
        try {
            // 1. Self-validate
            ResultDO checkResult = requestDTO.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // 2. Query intra-domain order data
            ResultDO<OrderAggregate> queryResult = orderRepository.findById(requestDTO.getOrderId());
            if (!queryResult.isSuccess()) {
                return ResultDO.buildFailResult(queryResult.getMsg());
            }
            OrderAggregate order = queryResult.getData();
            if (order == null) {
                return ResultDO.buildFailResult("ORDER_NOT_FOUND", "Order not found");
            }

            // 3. Cross-domain logistics query via Adaptor
            ResultDO<LogisticsInfoResponseDTO> logisticsResult = logisticsAdaptor.queryLogistics(order.getLogisticsNo());
            if (!logisticsResult.isSuccess()) {
                return ResultDO.buildFailResult(logisticsResult.getCode(), logisticsResult.getMsg());
            }

            // 4. Assemble response
            GetOrderDetailResponseDTO responseDTO = OrderAssembler.toGetOrderDetailResponseDTO(order, logisticsResult.getData());
            return ResultDO.buildSuccessResult(responseDTO);
        } catch (Exception e) {
            log.error("Get order detail failed, requestDTO: {}", requestDTO, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }
}
```

---

## Part D: Pure Calculate Mode

### D.1 Core Principle
**One calculation method = one class.** Each calculation method gets its own independent class with single responsibility.

### D.2 Naming

| Rule | Spec | Example |
|------|------|---------|
| Interface | `{Verb}QueryAppService` | `FeePreCalculateQueryAppService` |
| Implementation | `{Verb}QueryAppServiceImpl` | `FeePreCalculateQueryAppServiceImpl` |
| Inheritance | MUST extend `ApplicationQueryService` | — |
| Method naming | Verb | `feePreCalculate` |

### D.3 Call Chain
```
Input Adaptor → {Verb}QueryAppService → DomainService → calculate & return Result
```

### D.4 Orchestration Steps
1. Parameter self-validation (`requestDTO.check()`)
2. Fetch external data via Adaptor (if needed)
3. Assemble Param, call DomainService for computation
4. Convert Result to ResponseDTO and return

### D.5 Template
```java
@Slf4j
@Service
public class FeePreCalculateQueryAppServiceImpl implements FeePreCalculateQueryAppService {

    @Autowired
    private ExchangeRateAdaptor exchangeRateAdaptor;
    @Autowired
    private FeeCalculateDomainService feeCalculateDomainService;

    @Override
    public ResultDO<FeePreCalculateResponseDTO> feePreCalculate(FeePreCalculateRequestDTO requestDTO) {
        try {
            // 1. Self-validate
            ResultDO checkResult = requestDTO.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // 2. Cross-domain exchange rate query
            ResultDO<ExchangeRateResponseDTO> rateResult = exchangeRateAdaptor.queryExchangeRate(requestDTO.getCurrency());
            if (!rateResult.isSuccess()) {
                return ResultDO.buildFailResult(rateResult.getCode(), rateResult.getMsg());
            }

            // 3. Assemble calculation params
            FeeCalculateParam param = FeePreCalculateAssembler.toParam(requestDTO, rateResult.getData());

            // 4. Call DomainService
            ResultDO<FeeCalculateResult> domainResult = feeCalculateDomainService.calculate(param);
            if (!domainResult.isSuccess()) {
                return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
            }

            // 5. Convert to response
            return ResultDO.buildSuccessResult(FeePreCalculateAssembler.toResponseDTO(domainResult.getData()));
        } catch (Exception e) {
            log.error("Fee pre-calculation failed, requestDTO: {}", requestDTO, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }
}
```

---

## Part E: Rule+Calculate Mode

### E.1 Core Principle
Same as Pure Calculate: **one calculation method = one class.** Naming starts with **verb**, not aggregate name.

### E.2 Naming

| Rule | Spec | Example |
|------|------|---------|
| Interface | `{Verb}QueryAppService` | `SubsidyPreCalculateQueryAppService` |
| Implementation | `{Verb}QueryAppServiceImpl` | `SubsidyPreCalculateQueryAppServiceImpl` |
| Inheritance | MUST extend `ApplicationQueryService` | — |
| Method naming | Verb | `subsidyPreCalculate` |

### E.3 Call Chain
```
Input Adaptor → {Verb}QueryAppService → DomainService → Repository.queryRules()
                                                       → Aggregate.matchRule()/calculate() → return Result
```

### E.4 Template
```java
@Slf4j
@Service
public class SubsidyPreCalculateQueryAppServiceImpl implements SubsidyPreCalculateQueryAppService {

    @Autowired
    private UserLevelAdaptor userLevelAdaptor;
    @Autowired
    private SubsidyCalculateDomainService subsidyCalculateDomainService;

    @Override
    public ResultDO<SubsidyPreCalculateResponseDTO> subsidyPreCalculate(SubsidyPreCalculateRequestDTO requestDTO) {
        try {
            // 1. Self-validate
            ResultDO checkResult = requestDTO.check();
            if (!checkResult.isSuccess()) {
                return ResultDO.buildFailResult(checkResult.getCode(), checkResult.getMsg());
            }

            // 2. Cross-domain user level query
            ResultDO<UserLevelResponseDTO> levelResult = userLevelAdaptor.queryUserLevel(requestDTO.getUserId());
            if (!levelResult.isSuccess()) {
                return ResultDO.buildFailResult(levelResult.getCode(), levelResult.getMsg());
            }

            // 3. Assemble params
            SubsidyCalculateParam param = SubsidyPreCalculateAssembler.toParam(requestDTO, levelResult.getData());

            // 4. Call DomainService (match rules + calculate)
            ResultDO<SubsidyCalculateResult> domainResult = subsidyCalculateDomainService.calculate(param);
            if (!domainResult.isSuccess()) {
                return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
            }

            // 5. Convert to response
            return ResultDO.buildSuccessResult(SubsidyPreCalculateAssembler.toResponseDTO(domainResult.getData()));
        } catch (Exception e) {
            log.error("Subsidy pre-calculation failed, requestDTO: {}", requestDTO, e);
            return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
        }
    }
}
```
