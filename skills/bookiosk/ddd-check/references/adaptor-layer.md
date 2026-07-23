# Adaptor Layer Specification


## 目录
- [Part A: Base Rules (All Modes)](#part-a-base-rules-all-modes)
  - [A.1 Role](#a1-role)
  - [A.2 Package Structure](#a2-package-structure)
  - [A.3 Layer Responsibilities](#a3-layer-responsibilities)
  - [A.4 Adaptor Interface Design — CRITICAL](#a4-adaptor-interface-design-—-critical)
  - [A.5 Implementation Constraints](#a5-implementation-constraints)
  - [A.6 Design Patterns ALLOWED in Adaptor Layer](#a6-design-patterns-allowed-in-adaptor-layer)
  - [A.7 Call Chain Control](#a7-call-chain-control)
  - [A.8 Naming](#a8-naming)
  - [A.9 Input Adaptor Entry Types](#a9-input-adaptor-entry-types)
- [Part B: Write Mode](#part-b-write-mode)
  - [B.1 Call Chain](#b1-call-chain)
  - [B.2 Input Adaptor](#b2-input-adaptor)
  - [B.3 Output Adaptor](#b3-output-adaptor)
- [Part C: Read Mode](#part-c-read-mode)
  - [C.1 Call Chain](#c1-call-chain)
  - [C.2 Input Adaptor](#c2-input-adaptor)
  - [C.3 Output Adaptor — Example](#c3-output-adaptor-—-example)
- [Part D: Pure Calculate Mode](#part-d-pure-calculate-mode)
  - [D.1 Call Chain](#d1-call-chain)
  - [D.2 Input Adaptor](#d2-input-adaptor)
  - [D.3 Output Adaptor](#d3-output-adaptor)
- [Part E: Rule+Calculate Mode](#part-e-rule+calculate-mode)
  - [E.1 Call Chain](#e1-call-chain)
  - [E.2 Input Adaptor](#e2-input-adaptor)
  - [E.3 Output Adaptor](#e3-output-adaptor)

## Part A: Base Rules (All Modes)

### A.1 Role

Anti-Corruption Layer (ACL) — isolates external technical details (3rd-party services, middleware, frameworks) from polluting Domain and Application layers.

**Bidirectional adaptation:**
- **Input Adaptor:** Converts external requests (HTTP, message queues) into Application-layer commands
- **Output Adaptor:** Converts domain data formats into protocols required by external services

### A.2 Package Structure

```
adaptor/
└── {business}/               # Per business domain (order, booking, refund)
    ├── input/                # Controllers, MQ consumers, scheduled tasks
    ├── output/               # External 3rd-party service calls
    └── inner/                # Internal shared adaptors
```

### A.3 Layer Responsibilities

| Package | Responsibility | Dependencies |
|---------|---------------|--------------|
| `input/` | Handle external entry requests (Controller, MQ consumer, scheduled task), call Application services | Calls Application-layer interfaces, FORBIDDEN to directly depend on Domain layer |
| `output/` | Implement external service calls (RPC, payment gateway), encapsulate technical details | Implements adaptor interfaces defined in Application or Infrastructure layer |
| `inner/` | Internal adaptor reuse (auth, logging interceptors), avoid code duplication | Called only by other adaptors, FORBIDDEN to be directly depended on by Domain or Application |

### A.4 Adaptor Interface Design — CRITICAL

**The most important principle: Adaptor interfaces MUST be defined based on Application layer's business needs, NOT based on 3rd-party API shapes.**

- Method signatures, parameters, and return values MUST reflect the **caller's (Application) business semantics**, not external service technical details
- Interface and method names express the **caller's business intent**, not the callee's API name
- Even if calling the same 3rd-party API under the hood, different business intents = different Adaptor methods
- Adaptor internally may call **one or multiple** 3rd-party services — transparent to the caller
- External request/response format differences handled by Converter inside the Adaptor implementation — never exposed to caller
- **Core value:** When 3rd-party interfaces change, only the Adaptor implementation changes — Application layer is unaffected

**Interface definition ownership:**
- Adaptor interfaces defined in `application` module, method signatures driven by Application business needs
- Repository operates its own domain's database directly (via Mapper/DAO), NOT through Adaptor
- Non-self-domain external service calls go through Adaptor in Application layer

**Parameter and return value rules:**
- **Input:** Can be Application method's RequestDTO object, or primitive types (`long orderId`, `String logisticsNo`)
  - Prefer primitive types when parameter is **fixed and stable** (business identifiers like order number, logistics number) for better reusability
  - Use RequestDTO directly when parameters are **many or composite** — no need to define separate DTO for Adaptor
- **Return:** Follows two-mode exception handling (same as Domain, see `domain-layer.md` A.6):
  - **阻断型:** Throw exception — caught by APP
  - **分支型:** Return `ResultDO<T>` — APP extracts data for branching/fallback
  - Generic is ResponseDTO containing only fields Application needs (anti-corruption simplification)

### A.5 Implementation Constraints

- All adaptor implementations MUST reside in Adaptor layer, separate from interface definitions
- FORBIDDEN: business logic in adaptors — protocol conversion only
- Adaptor implementation internally handles converting business-semantic params/returns to/from 3rd-party formats

### A.6 Design Patterns ALLOWED in Adaptor Layer

Unlike Domain layer where design patterns are forbidden, Adaptor layer MAY use design patterns for technical adaptation.

**Why:** Adaptor layer's responsibility is **technical adaptation and anti-corruption**, not business rule expression. When routing to different 3rd-party APIs by channel ID or vendor type, this is **technical routing**, not business logic — Strategy or Router patterns are appropriate.

| Scenario | Approach | Notes |
|----------|----------|-------|
| Route to different 3rd-party pricing APIs by channel ID | `if/else` or Strategy pattern in Output Adaptor impl | Technical adaptation, not business logic |
| Call different order APIs by vendor type | Select different Client by vendor type in Output Adaptor impl | Transparent to Application layer |
| Adapt different protocols (HTTP/HSF/gRPC) | Select call method by protocol type in Output Adaptor impl | Technical details encapsulated in Adaptor |

#### Domain vs. Adaptor Design Pattern Usage

| Dimension | Domain Layer | Adaptor Layer |
|-----------|-------------|---------------|
| Design patterns | FORBIDDEN | ALLOWED |
| Branching basis | Business rules (domestic/international, passenger type) | Technical dimensions (channel ID, vendor type, protocol) |
| Handling | Direct `if/else` cohesive in domain objects | `if/else` or Strategy pattern to route to different services |
| Key difference | Business logic must be cohesive and visible | Technical details can be isolated and encapsulated |

### A.7 Call Chain Control

**Flow 1 (pure domain operation):**
```
Input Adaptor (optional) → Application → Domain → Infrastructure (own DB directly)
```

**Flow 2 (external data then domain logic):**
```
Input Adaptor (optional) → Application → Output Adaptor (fetch external data)
                                       → Domain → Infrastructure
```

**Flow 3 (pure external call):**
```
Input Adaptor (optional) → Application → Output Adaptor
```

### A.8 Naming

- Class names: `Adaptor` suffix
- Method names: verbs
- Converter classes: `Converter` suffix

### A.9 Input Adaptor Entry Types

| Entry Type | Description | Naming |
|-----------|------------|--------|
| Controller | HTTP endpoints (Spring MVC) | `{Business}Controller` |
| HSF Service | Alibaba HSF RPC provider | `{Business}HsfServiceImpl` |
| RocketMQ Consumer | RocketMQ message consumption | `{Business}MessageConsumer` |
| ScheduleX Task | ScheduleX distributed task | `{Business}ScheduleTask` |

**Rules for all entry types:**
- Same responsibility: receive external requests, convert params, call Application service
- FORBIDDEN: business logic in Input Adaptor
- Different modes call different Application services (see per-mode sections)

---

## Part B: Write Mode

### B.1 Call Chain
```
Input Adaptor → {AggregateName}AppService → DomainService → Repository (own DB directly)
```

### B.2 Input Adaptor
Write mode Input Adaptor calls `{AggregateName}AppService extends ApplicationCmdService`.

### B.3 Output Adaptor
Write mode's core is own domain model state changes. However, pre-validation via Output Adaptor (inventory check, price validation) before the write is **Application layer scene orchestration**. Adaptor params/returns follow A.4 rules.

---

## Part C: Read Mode

### C.1 Call Chain

**Intra-domain query:**
```
Input Adaptor → {AggregateName}QueryAppService → Repository (own DB directly)
```

**Cross-domain query:**
```
Input Adaptor → {AggregateName}QueryAppService → Output Adaptor
```

### C.2 Input Adaptor
Read mode Input Adaptor calls `{AggregateName}QueryAppService extends ApplicationQueryService`.

### C.3 Output Adaptor — Example

**Interface:**
```java
public interface LogisticsAdaptor {
    ResultDO<LogisticsInfoResponseDTO> queryLogistics(String logisticsNo);
}
```

**Implementation:**
```java
@Component
public class LogisticsAdaptorImpl implements LogisticsAdaptor {

    @Autowired
    private ThirdPartyLogisticsClient logisticsClient;

    @Override
    public LogisticsInfoResponseDTO queryLogistics(String logisticsNo) {
        ThirdPartyLogisticsResponse response = logisticsClient.track(logisticsNo);
        return LogisticsConverter.toLogisticsInfoResponseDTO(response);
        // Blocking error (network fail, timeout) → throw, caught by APP
    }
}
```

---

## Part D: Pure Calculate Mode

### D.1 Call Chain
```
Input Adaptor → {Verb}QueryAppService → DomainService → calculate & return Result
```

### D.2 Input Adaptor
Calls `{Verb}QueryAppService extends ApplicationQueryService`. Naming starts with **verb**, not aggregate name.

### D.3 Output Adaptor
Pure calculate mode's business logic is fully in DomainService — typically no Output Adaptor needed. When Application needs **cross-domain external data** as calculation input, use Output Adaptor. Adaptor params/returns follow A.4 rules.

**Interface example:**
```java
public interface ExchangeRateAdaptor {
    ResultDO<ExchangeRateResponseDTO> queryExchangeRate(String currency);
}
```

**Implementation:**
```java
@Component
public class ExchangeRateAdaptorImpl implements ExchangeRateAdaptor {

    @Autowired
    private ThirdPartyExchangeRateClient exchangeRateClient;

    @Override
    public ExchangeRateResponseDTO queryExchangeRate(String currency) {
        ThirdPartyRateResponse response = exchangeRateClient.getRate(currency);
        return ExchangeRateConverter.toExchangeRateResponseDTO(response);
        // Blocking error → throw, caught by APP
    }
}
```

---

## Part E: Rule+Calculate Mode

### E.1 Call Chain
```
Input Adaptor → {Verb}QueryAppService → DomainService → Repository.queryRules()
                                                       → Aggregate.matchRule()/calculate() → return Result
```

### E.2 Input Adaptor
Calls `{Verb}QueryAppService extends ApplicationQueryService`. Naming starts with **verb**, not aggregate name.

### E.3 Output Adaptor
Rule data loaded via Repository from database or config center — typically no Output Adaptor needed. When Application needs **cross-domain external data** as calculation input, use Output Adaptor. Adaptor params/returns follow A.4 rules.

**Interface example:**
```java
public interface UserLevelAdaptor {
    ResultDO<UserLevelResponseDTO> queryUserLevel(long userId);
}
```
