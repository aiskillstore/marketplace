# Base Classes & Core Types Reference

This document defines all base classes, interfaces, and core types referenced throughout the DDD layer specifications. These form the framework foundation that all layers build upon.

---

## 1. ResultDO\<T\> — Universal Result Wrapper

**Location:** `model` module (shared across all layers)
**Purpose:** Standardized operation result wrapper. Every method across all layers returns `ResultDO<T>` — no exceptions are thrown across layer boundaries.

```java
public class ResultDO<T> implements Serializable {

    private boolean success;
    private String code;
    private String msg;
    private T data;

    /** Create success result with data payload */
    public static <T> ResultDO<T> buildSuccessResult(T data) { ... }

    /** Create success result with no data (void operations) */
    public static <T> ResultDO<T> buildSuccessResult() { ... }

    /** Create failure result with error code and message */
    public static <T> ResultDO<T> buildFailResult(String code, String msg) { ... }

    /** Create failure result from another ResultDO's error info */
    public static <T> ResultDO<T> buildFailResult(String msg) { ... }

    public boolean isSuccess() { ... }
    public String getCode() { ... }
    public String getMsg() { ... }
    public T getData() { ... }
}
```

**Usage pattern:**
```java
// Success with data
return ResultDO.buildSuccessResult(aggregate);

// Success (void operation)
return ResultDO.buildSuccessResult(null);

// Failure
return ResultDO.buildFailResult("ORDER_NOT_FOUND", "Order does not exist");

// Propagate upstream error
if (!domainResult.isSuccess()) {
    return ResultDO.buildFailResult(domainResult.getCode(), domainResult.getMsg());
}
```

**Rules:**
- All Application layer public methods MUST return `ResultDO<T>`
- All DomainService methods MUST return `ResultDO<T>`
- All Repository methods MUST return `ResultDO<T>`
- Exceptions MUST be caught internally and converted to `ResultDO` failure — never propagate across layer boundaries
- Input Adaptors convert `ResultDO` to protocol-specific responses (HTTP JSON, RPC, etc.)

---

## 2. Domain Layer Base Classes

### 2.1 BaseParam

**Location:** `domain.model.param` package (convention)
**Purpose:** Base class for all domain method parameter objects. Marker class ensuring type safety and consistent serialization behavior.

```java
public abstract class BaseParam implements Serializable {
    // Common parameter infrastructure (trace ID, etc.) can be added here
}
```

**Naming:** `{MethodName}Param` (e.g., `ConfirmPaymentParam`, `FeeCalculateParam`)

**Usage:**
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class ConfirmPaymentParam extends BaseParam {
    private Long orderId;
    private String paymentChannel;
    private BigDecimal amount;
}
```

### 2.2 BaseResult

**Location:** `domain.model.result` package (convention)
**Purpose:** Base class for all domain method result objects. Unlike DTOs, Result objects may contain rich domain methods (behavior, not just data).

```java
public abstract class BaseResult implements Serializable {
    // Common result infrastructure can be added here
}
```

**Naming:** `{MethodName}Result` (e.g., `FeeCalculateResult`, `SearchControlResult`)

**Key difference from DTO:** Result objects can have "rich" methods — computation, judgment, and query methods that operate on the result data.

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class FeeCalculateResult extends BaseResult {
    private BigDecimal totalFee;
    private String currency;

    /** Rich method: check if the fee is zero/free */
    public boolean isFree() {
        return totalFee == null || totalFee.compareTo(BigDecimal.ZERO) == 0;
    }
}
```

### 2.3 BaseAggregate\<ID\>

**Location:** `domain.model.aggregate` package (convention)
**Purpose:** Base class for all aggregate roots. Provides identity management and domain event infrastructure.

```java
public abstract class BaseAggregate<ID extends Serializable> implements Serializable {
    private ID id;
    // Domain event collection, version tracking, etc.

    public ID getId() { ... }
    public void setId(ID id) { ... }
}
```

**Naming:** `{Noun}Aggregate` (e.g., `OrderAggregate`, `BonusRuleAggregate`)

### 2.4 BaseEntity\<ID\>

**Location:** `domain.model.entity` package (convention)
**Purpose:** Base class for all entities. Entities have identity but exist within an aggregate boundary.

```java
public abstract class BaseEntity<ID extends Serializable> implements Serializable {
    private ID id;
    // Version tracking, etc.

    public ID getId() { ... }
    public void setId(ID id) { ... }
}
```

**Naming:** `{Noun}Entity` (e.g., `OrderItemEntity`, `BonusRuleEntity`)

**Critical rule:** Entity properties MUST use `Field<T>`, `FieldSet<T>`, or `FieldList<T>` wrappers (see Section 3).

### 2.5 BaseValue

**Location:** `domain.model.value` package (convention)
**Purpose:** Base class for all value objects. Value objects have no identity, are immutable, and equality is based on attribute values.

```java
public abstract class BaseValue implements Serializable {
    // Value objects: no identity, compare by attributes
}
```

**Naming:** `{Noun}Value` (e.g., `PassengerValue`, `MoneyValue`)

**Key characteristics:**
- No unique identifier (no `id` field)
- Immutable — methods return new instances, never mutate
- Equality based on all attributes, not identity
- Methods are computation/judgment only (calculate age, check if adult, etc.)

---

## 3. Field\<T\>, FieldSet\<T\>, FieldList\<T\> — Immutable Property Wrappers

**Location:** `model` module (shared)
**Purpose:** Type-safe immutable wrappers for entity properties. Enforce the immutability principle: every update creates a new wrapper instance rather than mutating in-place. This prevents hidden side effects and enables safe change tracking.

### 3.1 Field\<T\> — Single Value Wrapper

```java
public final class Field<T> implements Serializable {

    private final T value;

    private Field(T value) {
        this.value = value;
    }

    /** Create a new Field with the given value */
    public static <T> Field<T> of(T value) {
        return new Field<>(value);
    }

    /** Get the wrapped value */
    public T get() {
        return value;
    }

    /** Transform the value via a mapping function (returns new Field) */
    public <R> Field<R> map(Function<T, R> mapper) {
        return Field.of(mapper.apply(value));
    }

    @Override
    public boolean equals(Object o) { ... }  // compares wrapped value
    @Override
    public int hashCode() { ... }
}
```

**Usage in Entity:**
```java
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderItemEntity extends BaseEntity<Long> {
    private Field<Long> orderId;
    private Field<String> productName;
    private Field<Long> price;

    public void updatePrice(Long newPrice) {
        // Creates new Field instance — never mutates in-place
        this.price = Field.of(newPrice);
    }

    public Long getPriceValue() {
        return this.price != null ? this.price.get() : null;
    }
}
```

### 3.2 FieldSet\<T\> — Set Wrapper

```java
public final class FieldSet<T> implements Serializable {

    private final Set<T> values;

    private FieldSet(Set<T> values) {
        this.values = Collections.unmodifiableSet(new HashSet<>(values));
    }

    public static <T> FieldSet<T> of(Set<T> values) { ... }
    public static <T> FieldSet<T> empty() { ... }

    public Set<T> get() { return values; }

    /** Add element (returns NEW FieldSet, original unchanged) */
    public FieldSet<T> add(T element) { ... }

    /** Remove element (returns NEW FieldSet, original unchanged) */
    public FieldSet<T> remove(T element) { ... }

    public boolean contains(T element) { ... }
    public int size() { ... }
}
```

### 3.3 FieldList\<T\> — List Wrapper

```java
public final class FieldList<T> implements Serializable {

    private final List<T> values;

    private FieldList(List<T> values) {
        this.values = Collections.unmodifiableList(new ArrayList<>(values));
    }

    public static <T> FieldList<T> of(List<T> values) { ... }
    public static <T> FieldList<T> empty() { ... }

    public List<T> get() { return values; }

    /** Add element (returns NEW FieldList, original unchanged) */
    public FieldList<T> add(T element) { ... }

    /** Add at index (returns NEW FieldList, original unchanged) */
    public FieldList<T> add(int index, T element) { ... }

    /** Remove element (returns NEW FieldList, original unchanged) */
    public FieldList<T> remove(T element) { ... }

    public T get(int index) { ... }
    public int size() { ... }
    public Stream<T> stream() { ... }
}
```

**Why Field wrappers instead of plain types?**
1. **Immutability enforced at type level** — compiler catches mutations, not code review
2. **Change tracking** — framework can detect which fields changed for optimized persistence
3. **Null safety** — `Field.of(null)` vs `null` has different semantics
4. **Consistent pattern** with the project-wide immutability rule

---

## 4. Repository Base Interface

### 4.1 AggregateRepository\<T, ID\>

**Location:** `domain.repository` package (convention)
**Purpose:** Base interface for all repositories. Defines the contract that infrastructure implements.

```java
public interface AggregateRepository<T extends BaseAggregate<ID>, ID extends Serializable> {
    // Common repository operations can be defined here
    // Concrete repositories add domain-specific save/query methods
}
```

**Naming:** `{BusinessName}Repository` (e.g., `OrderRepository`, `BonusRuleRepository`)

**Defined in:** `domain` layer
**Implemented in:** `infrastructure` layer

---

## 5. Application Layer Base Interfaces

### 5.1 ApplicationCmdService

**Location:** application layer base package
**Purpose:** Marker interface for command (write) application services.

```java
public interface ApplicationCmdService {
    // Marker interface — command-side application services
}
```

**Usage:** `OrderAppService extends ApplicationCmdService`

### 5.2 ApplicationQueryService

**Location:** application layer base package
**Purpose:** Marker interface for query (read) application services.

```java
public interface ApplicationQueryService {
    // Marker interface — query-side application services
}
```

**Usage:** `OrderQueryAppService extends ApplicationQueryService`

---

## 6. DTO Base Class

### 6.1 BaseDTO

**Location:** `client` module base package
**Purpose:** Base class for all Data Transfer Objects. Implements `Serializable` for RPC transmission.

```java
public abstract class BaseDTO implements Serializable {
    private static final long serialVersionUID = 1L;
    // Common DTO infrastructure (trace ID, etc.) can be added here
}
```

**Usage:**
- `{MethodName}RequestDTO extends BaseDTO`
- `{MethodName}ResponseDTO extends BaseDTO`
- `{ConceptName}DTO extends BaseDTO` (shared model objects in client layer)

---

## 7. Exception Classes

### 7.1 AggregateException

**Location:** `domain` layer
**Purpose:** Thrown when aggregate root or entity internal validation fails. Caught by DomainService and converted to `ResultDO` failure.

```java
public class AggregateException extends RuntimeException {
    private final String code;
    private final String msg;

    public AggregateException(String msg) {
        this("AGGREGATE_ERROR", msg);
    }

    public AggregateException(String code, String msg) {
        super(msg);
        this.code = code;
        this.msg = msg;
    }

    public String getCode() { return code; }
    public String getMsg() { return msg; }
}
```

**Usage:**
```java
// In aggregate/entity method
if (!this.status.canCancel()) {
    throw new AggregateException("ORDER_CANNOT_CANCEL", "Order cannot be cancelled in current status");
}
```

### 7.2 BizException

**Location:** `domain` layer
**Purpose:** Thrown when domain service business logic validation fails. Caught by DomainService itself and converted to `ResultDO` failure.

```java
public class BizException extends RuntimeException {
    private final String code;
    private final String msg;

    public BizException(String code, String msg) {
        super(msg);
        this.code = code;
        this.msg = msg;
    }

    public String getCode() { return code; }
    public String getMsg() { return msg; }
}
```

**Exception handling pattern in DomainService:**
```java
try {
    // Business logic...
} catch (BizException e) {
    log.error("Business validation failed, param: {}", param, e);
    return ResultDO.buildFailResult(e.getCode(), e.getMsg());
} catch (AggregateException e) {
    log.error("Aggregate validation failed, param: {}", param, e);
    return ResultDO.buildFailResult(e.getCode(), e.getMsg());
} catch (Throwable e) {
    log.error("System error, param: {}", param, e);
    return ResultDO.buildFailResult("SYSTEM_ERROR", "System error");
}
```

---

## 8. LevelLock — Distributed Lock

**Location:** `infrastructure` layer (constructed by Repository)
**Purpose:** Distributed lock abstraction for concurrent safety in write operations.

```java
public class LevelLock {
    private final String lockKey;
    // Internal lock implementation (Redis, ZooKeeper, etc.)

    public LevelLock(String lockKey) {
        this.lockKey = lockKey;
    }

    /** Attempt to acquire lock (non-blocking), returns true if acquired */
    public boolean tryLock() { ... }

    /** Release the lock */
    public void unlock() { ... }
}
```

**Usage pattern in DomainService:**
```java
LevelLock levelLock = orderRepository.buildLock("order:confirmPayment:" + param.getOrderId());
try {
    if (!levelLock.tryLock()) {
        return ResultDO.buildFailResult("LOCK_FAIL", "Failed to acquire lock, please retry");
    }
    // ... business logic ...
} finally {
    levelLock.unlock();
}
```

---

## 9. Quick Reference Table

| Type | Layer | Extends/Implements | Purpose |
|------|-------|-------------------|---------|
| `ResultDO<T>` | model (shared) | `Serializable` | Universal operation result wrapper |
| `BaseParam` | domain | `Serializable` | Domain method parameter base |
| `BaseResult` | domain | `Serializable` | Domain method result base (rich) |
| `BaseAggregate<ID>` | domain | `Serializable` | Aggregate root base |
| `BaseEntity<ID>` | domain | `Serializable` | Entity base (properties use Field) |
| `BaseValue` | domain | `Serializable` | Value object base (immutable, no ID) |
| `Field<T>` | model (shared) | `Serializable` | Immutable single-value wrapper |
| `FieldSet<T>` | model (shared) | `Serializable` | Immutable set wrapper |
| `FieldList<T>` | model (shared) | `Serializable` | Immutable list wrapper |
| `AggregateRepository<T,ID>` | domain | interface | Repository base interface |
| `ApplicationCmdService` | application | interface | Command service marker |
| `ApplicationQueryService` | application | interface | Query service marker |
| `BaseDTO` | client | `Serializable` | DTO base class |
| `AggregateException` | domain | `RuntimeException` | Aggregate validation failure |
| `BizException` | domain | `RuntimeException` | Business logic failure |
| `LevelLock` | infrastructure | — | Distributed lock abstraction |

---

## 10. Inheritance Chain Diagram

```
Domain Model Hierarchy:
  Serializable
    ├── BaseAggregate<ID>          ← aggregate roots
    ├── BaseEntity<ID>             ← entities (properties use Field<T>)
    └── BaseValue                  ← value objects (immutable, no ID)

Domain Method I/O:
  Serializable
    ├── BaseParam                  ← method input parameters
    └── BaseResult                 ← method return results (supports rich methods)

Client DTOs:
  Serializable
    └── BaseDTO
         ├── {Name}RequestDTO      ← API request parameters
         ├── {Name}ResponseDTO     ← API response data
         └── {Name}DTO             ← shared nested objects

Shared Model:
  Field<T> / FieldSet<T> / FieldList<T>   ← immutable property wrappers
  ResultDO<T>                             ← universal result envelope

Application Services:
  ApplicationCmdService    ← Command (write) marker interface
  ApplicationQueryService  ← Query (read) marker interface

Domain Repository:
  AggregateRepository<T,ID> ← Base repository interface

Domain Exceptions:
  RuntimeException
    ├── AggregateException  ← Aggregate/entity validation failure
    └── BizException        ← Domain service business failure
```
