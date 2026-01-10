# Architecture Hexagonale - Structure DDD

## Structure de Module (Bounded Context)

```
boundedcontext/
├── domain/
│   ├── model/          # Entités métier et Value Objects
│   ├── port/           # Interfaces (Repository, Gateway)
│   └── usecase/        # Orchestrateur logique métier via le model
├── infrastructure/
│   ├── api/
│   │   ├── request/    # DTOs d'entrée
│   │   └── response/   # DTOs de sortie
│   └── persistence/
│       ├── entity/     # Entités de persistance
│       ├── mapper/     # Domain ↔ Infrastructure
│       └── adapter/    # Implémentations concrètes
└── exception/          # Exceptions métier
```

## Règles de Dépendance

```
Infrastructure ──────┐
                     ├──→ Domain
Infrastructure ──────┘

✅ AUTORISÉ:
  - domain → rien (totalement indépendant)
  - infrastructure → domain uniquement
  - usecase → model + port
  - adapter → port (implémente)
  - api → usecase

❌ INTERDIT:
  - domain → infrastructure
  - model → usecase
  - port → adapter
  - Dépendances circulaires entre bounded contexts
```

## Flux de Données

```
HTTP Request
    ↓
API (infrastructure/api/request)
    ↓
Use Case (domain/usecase)
    ↓
Model + Port (domain/model + domain/port)
    ↓
Adapter (infrastructure/persistence/adapter)
    ↓
Entity (infrastructure/persistence/entity)
    ↓
Database
    ↓
Mapper (infrastructure/persistence/mapper)
    ↓
Model (domain/model)
    ↓
Use Case (domain/usecase)
    ↓
API Response (infrastructure/api/response)
```

## Checklist de Conformité

### Domain
- [ ] `domain/model/` contient uniquement les entités métier et Value Objects
- [ ] `domain/port/` contient uniquement des interfaces (Repository, Gateway)
- [ ] `domain/usecase/` orchestre la logique métier via model et port
- [ ] Aucun import d'infrastructure dans domain
- [ ] Pas d'annotations framework dans domain

### Infrastructure
- [ ] `infrastructure/api/request/` contient les DTOs d'entrée
- [ ] `infrastructure/api/response/` contient les DTOs de sortie
- [ ] `infrastructure/persistence/entity/` contient les entités de persistance
- [ ] `infrastructure/persistence/mapper/` convertit domain ↔ infrastructure
- [ ] `infrastructure/persistence/adapter/` implémente les interfaces du domain/port

### Isolation des Bounded Contexts
- [ ] Pas d'import de repository d'un autre module
- [ ] Pas de couplage fort entre domaines
- [ ] Pas d'exposition des entités d'un bounded context à un autre
- [ ] Communication via Gateway défini dans domain/port

## Anti-patterns Critiques

### ❌ Gateway couplé à un autre module
Un gateway qui importe directement un repository d'un autre bounded context

### ❌ Entités exposées entre contexts
Les entités d'un bounded context utilisées directement dans un autre

### ❌ Logique métier dans l'infrastructure
Validation ou calculs métier dans les controllers ou adapters

### ❌ Use case qui accède directement à l'adapter
Use case qui ne passe pas par l'interface (port)

### ❌ Model qui dépend du use case
Inversion de dépendance incorrecte
