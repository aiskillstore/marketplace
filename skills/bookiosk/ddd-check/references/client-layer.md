# Client Layer Specification


## 目录
- [1. Package Structure](#1-package-structure)
- [2. Dependency Rules](#2-dependency-rules)
- [3. AppService Interface Definitions](#3-appservice-interface-definitions)
  - [3.1 Write Mode Interface](#31-write-mode-interface)
  - [3.2 Read Mode Interface](#32-read-mode-interface)
  - [3.3 Pure Calculate Mode Interface](#33-pure-calculate-mode-interface)
  - [3.4 Rule+Calculate Mode Interface](#34-rule+calculate-mode-interface)
- [4. Model Package — Shared Nested DTOs](#4-model-package-—-shared-nested-dtos)
  - [4.1 Purpose](#41-purpose)
  - [4.2 Naming and Inheritance](#42-naming-and-inheritance)
  - [4.3 Reuse Guidelines](#43-reuse-guidelines)
  - [4.4 Template](#44-template)
- [5. RequestDTO Specification](#5-requestdto-specification)
- [6. ResponseDTO Specification](#6-responsedto-specification)

## 1. Package Structure

```
client/
└── {business}/
    ├── model/             # Shared nested DTOs (industry concepts: Segment, Passenger, etc.)
    │   └── {category}/    # Sub-package by category (e.g., passenger/, segment/)
    ├── req/               # Request DTOs
    │   └── {category}/    # Sub-package by category
    └── res/               # Response DTOs
        └── {category}/    # Sub-package by category
```

**Sub-package rule:** Classes under `req/`, `res/`, `model/` MUST NOT be flat — organize into sub-packages by category. For example, passenger-related classes (passenger info, credentials, address) go under `passenger/`.

## 2. Dependency Rules

Client layer is the **external RPC API definition layer** — depended on by external systems.

| Rule | Notes |
|------|-------|
| FORBIDDEN from depending on `model` layer | `model` is internal shared — if client depends on it, external callers are forced to transitively depend on `model`, causing unnecessary dependency spread |
| FORBIDDEN from depending on `domain` layer | Domain is internal core business logic, must not be exposed |
| FORBIDDEN from depending on `application` layer | Application is internal scene orchestration, must not be exposed |
| FORBIDDEN from depending on `infrastructure` layer | Infrastructure is internal technical implementation, must not be exposed |

**Key principle:** All client layer DTOs MUST be **self-contained** — cannot reference classes from other internal modules. If similar concepts exist in client and model, define independently in client and convert via Assembler in Application layer.

## 3. AppService Interface Definitions

Client layer defines the service interfaces that Application layer implements.

### 3.1 Write Mode Interface

| Rule | Spec |
|------|------|
| Interface naming | `{AggregateName}AppService` (e.g., `OrderAppService`) |
| Inheritance | MUST extend `ApplicationCmdService` |
| Method naming | Business verbs (e.g., `createOrder`, `confirmPayment`), FORBIDDEN: technical verbs (`save`, `update`) |
| Parameter naming | `{MethodName}RequestDTO` (e.g., `CreateOrderRequestDTO`) |
| Return | `ResultDO<{MethodName}ResponseDTO>` (e.g., `ResultDO<CreateOrderResponseDTO>`) |

```java
public interface OrderAppService extends ApplicationCmdService {
    ResultDO<CreateOrderResponseDTO> createOrder(CreateOrderRequestDTO requestDTO);
}
```

### 3.2 Read Mode Interface

| Rule | Spec |
|------|------|
| Interface naming | `{AggregateName}QueryAppService` (e.g., `OrderQueryAppService`) |
| Inheritance | MUST extend `ApplicationQueryService` |
| Method naming | Verbs with clear query intent (e.g., `queryOrderList`, `getOrderDetail`), avoid abstract words (`process`) |
| Parameter naming | `{MethodName}RequestDTO` (e.g., `QueryOrderListRequestDTO`) |
| Return | `ResultDO<{MethodName}ResponseDTO>` (e.g., `ResultDO<QueryOrderListResponseDTO>`) |

```java
public interface OrderQueryAppService extends ApplicationQueryService {
    ResultDO<QueryOrderListResponseDTO> queryOrderList(QueryOrderListRequestDTO requestDTO);
    ResultDO<GetOrderDetailResponseDTO> getOrderDetail(GetOrderDetailRequestDTO requestDTO);
}
```

### 3.3 Pure Calculate Mode Interface

| Rule | Spec |
|------|------|
| Interface naming | `{Verb}QueryAppService` (e.g., `RefundPreCalculateQueryAppService`) |
| Inheritance | MUST extend `ApplicationQueryService` |
| Special rule | **One calculation method = one class** |
| Method naming | Verb |
| Parameter naming | `{MethodName}RequestDTO` |
| Return | `ResultDO<{MethodName}ResponseDTO>` |

```java
public interface FeePreCalculateQueryAppService extends ApplicationQueryService {
    ResultDO<FeePreCalculateResponseDTO> feePreCalculate(FeePreCalculateRequestDTO requestDTO);
}
```

### 3.4 Rule+Calculate Mode Interface
Same as Pure Calculate Mode.

## 4. Model Package — Shared Nested DTOs

### 4.1 Purpose
Holds DTOs **shared across** RequestDTO and ResponseDTO objects. These typically represent industry concepts: Segment, Passenger, Fare, etc.

### 4.2 Naming and Inheritance
- Naming suffix: MUST end with `DTO` (e.g., `PassengerDTO`, `SegmentDTO`, `CredentialDTO`)
- Names should reflect industry concepts with business meaning
- Inheritance: MUST extend `BaseDTO`

### 4.3 Reuse Guidelines

Avoid **over-reuse**:

- **Input bloat:** If reuse causes RequestDTO to contain fields the caller doesn't need, it increases input complexity and reduces API friendliness. Define a separate slim DTO instead.
- **Output redundancy:** If reuse causes ResponseDTO to output unnecessary fields, it leaks information. Trim to a scene-specific DTO with only needed fields.

**Rule:** When reuse introduces obviously redundant or irrelevant fields, define an independent DTO instead.

### 4.4 Template
```java
public class PassengerDTO extends BaseDTO {
    private static final long serialVersionUID = 1L;
    private String name;
    private Integer age;
    private String credentialNo;
    // getter/setter
}
```

## 5. RequestDTO Specification

- Naming: `{MethodName}RequestDTO` — MUST end with `RequestDTO`
- Inheritance: MUST extend `BaseDTO`
- MUST use RequestDTO to encapsulate parameters, FORBIDDEN: primitive types or Map
- Each method gets its own independent RequestDTO

```java
public class CreateOrderRequestDTO extends BaseDTO {
    private static final long serialVersionUID = 1L;
    private String productId;
    private Integer quantity;

    public ResultDO check() {
        if (productId == null || productId.isEmpty()) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Product ID must not be empty");
        }
        if (quantity == null || quantity <= 0) {
            return ResultDO.buildFailResult("PARAM_ERROR", "Quantity must be greater than 0");
        }
        return ResultDO.buildSuccessResult();
    }
}
```

## 6. ResponseDTO Specification

- Naming: `{MethodName}ResponseDTO` — MUST end with `ResponseDTO`
- Inheritance: MUST extend `BaseDTO`
- Always returned via `ResultDO<ResponseDTO>`
- Error codes wrapped in ResultDO, FORBIDDEN: throwing exceptions directly

```java
public class CreateOrderResponseDTO extends BaseDTO {
    private static final long serialVersionUID = 1L;
    private Long orderId;
    private String status;
    // getter/setter
}
```
