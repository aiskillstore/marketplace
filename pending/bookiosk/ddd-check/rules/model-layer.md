# Model Layer Specification

## 1. Shared Model Definitions

The model layer holds models shared across all internal modules:

- **Enums:** Cross-module shared enum definitions
- **Common business concepts:** Generic business objects like Segment, Passenger, etc.

## 2. Dependency Rules

Model layer is **internal shared** — only for project-internal module use.

| Module | Can depend on model? | Notes |
|--------|---------------------|-------|
| `domain` | ALLOWED | Domain uses shared enums, common business concepts |
| `application` | ALLOWED | Application uses shared models for scene orchestration |
| `adaptor` | ALLOWED | Adaptor uses shared models for protocol conversion |
| `infrastructure` | ALLOWED | Infrastructure uses shared models for data conversion |
| `client` | FORBIDDEN | Client is the external RPC API definition layer. If client depends on model, external callers are forced to transitively depend on model, causing unnecessary dependency spread |

**Key principle:** Client layer DTOs MUST be self-contained, cannot reference model layer classes. If similar concepts exist in client and model, define independently in client and convert via Assembler in Application layer.

## 3. Applicable Scenarios

| Scenario | Notes |
|----------|-------|
| Cross-module enums | Enums shared across multiple business modules (e.g., `DomesticIntlEnum`) |
| Common business concepts | Business objects not belonging to a specific domain but used by multiple domains |
| Shared constants | Constant definitions shared across modules |

## 4. Code Templates

### 4.1 Shared Enum
```java
package {basePackage}.model.{business};

public enum DomesticIntlEnum {
    DOMESTIC("D", "Domestic"),
    INTERNATIONAL("I", "International"),
    ;

    private final String code;
    private final String description;

    DomesticIntlEnum(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() { return code; }
    public String getDescription() { return description; }

    public static DomesticIntlEnum getByCode(String code) {
        for (DomesticIntlEnum e : values()) {
            if (e.getCode().equals(code)) return e;
        }
        return null;
    }
}
```

### 4.2 Common Business Concept
```java
package {basePackage}.model.{business};

import java.io.Serializable;

public class Segment implements Serializable {
    private static final long serialVersionUID = 1L;
    private String departureCity;
    private String arrivalCity;
    private Date departureTime;
    // getter/setter
}
```
