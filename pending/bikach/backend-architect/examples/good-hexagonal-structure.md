# Exemple de Bonne Structure Hexagonale

## Structure du Module User

```
user-context/
├── domain/
│   ├── model/
│   │   ├── User.ts                    # Entity métier
│   │   ├── Email.ts                   # Value Object
│   │   ├── UserId.ts                  # Value Object
│   │   └── UserRole.ts                # Value Object ou Enum
│   │
│   ├── port/
│   │   ├── UserRepository.ts          # Interface repository
│   │   ├── EmailGateway.ts            # Interface gateway externe
│   │   └── PasswordHasher.ts          # Interface service technique
│   │
│   └── usecase/
│       ├── CreateUserUseCase.ts       # Use case création
│       ├── UpdateUserUseCase.ts       # Use case modification
│       └── DeleteUserUseCase.ts       # Use case suppression
│
├── infrastructure/
│   ├── api/
│   │   ├── request/
│   │   │   ├── CreateUserRequest.ts   # DTO entrée
│   │   │   └── UpdateUserRequest.ts
│   │   │
│   │   ├── response/
│   │   │   └── UserResponse.ts        # DTO sortie
│   │   │
│   │   └── UserController.ts          # Controller HTTP
│   │
│   └── persistence/
│       ├── entity/
│       │   └── UserEntity.ts          # Entity ORM/DB
│       │
│       ├── mapper/
│       │   └── UserMapper.ts          # Mapping domain ↔ DB
│       │
│       └── adapter/
│           ├── PostgresUserRepository.ts  # Impl repository
│           ├── SendGridEmailGateway.ts    # Impl gateway
│           └── BcryptPasswordHasher.ts    # Impl hasher
│
└── exception/
    ├── UserNotFoundException.ts
    ├── DuplicateEmailException.ts
    └── InvalidEmailException.ts
```

## Flux de Création d'Utilisateur

### 1. Requête HTTP arrive au Controller

```
POST /users
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secret123"
}
```

### 2. Controller (infrastructure/api)

```
Controller reçoit CreateUserRequest
    ↓
Valide le format (DTO validation)
    ↓
Appelle CreateUserUseCase
    ↓
Convertit résultat en UserResponse
    ↓
Retourne HTTP 201 avec UserResponse
```

### 3. Use Case (domain/usecase)

```
CreateUserUseCase reçoit la commande
    ↓
Crée les Value Objects (Email, UserId)
    ↓
Vérifie via UserRepository si email existe
    ↓
Hash le password via PasswordHasher
    ↓
Crée l'entité User (domain)
    ↓
Sauvegarde via UserRepository
    ↓
Envoie email de bienvenue via EmailGateway
    ↓
Retourne le User créé
```

### 4. Repository Adapter (infrastructure/persistence)

```
PostgresUserRepository.save(user)
    ↓
Mapper convertit User → UserEntity (ORM)
    ↓
Sauvegarde UserEntity en base
    ↓
Récupère l'entity persistée avec ID
    ↓
Mapper convertit UserEntity → User
    ↓
Retourne User avec ID assigné
```

## Points Clés de la Structure

### ✅ Domain Isolé
```
domain/
  ↓ ne dépend de rien
  ↓ définit les interfaces (ports)
  ↓ contient la logique métier pure
```

### ✅ Infrastructure Implémente
```
infrastructure/
  ↓ dépend du domain
  ↓ implémente les ports
  ↓ détails techniques
```

### ✅ Use Case Orchestre
```
UseCase:
  - Reçoit commande/query
  - Utilise le domain model
  - Passe par les ports (abstractions)
  - Coordonne le flux
  - Retourne résultat métier
```

### ✅ Mappers Séparent
```
UserMapper:
  - toDomain(UserEntity) → User
  - toEntity(User) → UserEntity
  - toResponse(User) → UserResponse
```

### ✅ Value Objects Encapsulent
```
Email:
  - Validation format
  - Logique métier sur email
  - Immutable
  - Comparaison par valeur
```

## Communication Entre Bounded Contexts

### Via Gateway (Correct ✅)

```
OrderContext needs User info
    ↓
OrderUseCase dépend de IUserGateway (port dans OrderContext)
    ↓
UserGatewayAdapter (infrastructure) implémente IUserGateway
    ↓
Appelle UserContext via API ou use case direct
    ↓
Convertit UserResponse en format OrderContext
    ↓
Retourne au OrderUseCase
```

### Règles
- Pas d'import direct d'entités d'un autre context
- Communication via Gateway (abstraction)
- Chaque context a sa représentation des concepts
- Anti-Corruption Layer si nécessaire

## Exemple de Dépendances

### ✅ Correct

```
CreateUserUseCase depends on:
  - IUserRepository (domain/port)
  - IEmailGateway (domain/port)
  - IPasswordHasher (domain/port)

PostgresUserRepository implements IUserRepository
SendGridEmailGateway implements IEmailGateway
BcryptPasswordHasher implements IPasswordHasher

→ Use case dépend des abstractions
→ Infrastructure implémente les abstractions
→ Inversion de dépendance respectée
```

### ❌ Incorrect

```
CreateUserUseCase depends on:
  - PostgresUserRepository (concrete class)
  - SendGridEmailGateway (concrete class)

→ Use case couplé à l'infrastructure
→ Pas d'inversion
→ Impossible de changer facilement
→ Tests difficiles
```

## Injection de Dépendances

### Configuration (main/app)

```
Container configuration:
  bind(IUserRepository).to(PostgresUserRepository)
  bind(IEmailGateway).to(SendGridEmailGateway)
  bind(IPasswordHasher).to(BcryptPasswordHasher)

CreateUserUseCase constructor:
  (userRepository: IUserRepository,
   emailGateway: IEmailGateway,
   passwordHasher: IPasswordHasher)

→ Runtime injecte les implémentations
→ Use case ne connaît que les interfaces
```

## Tests

### Use Case Test (Unitaire)

```
Test CreateUserUseCase:
  - Mock IUserRepository
  - Mock IEmailGateway
  - Mock IPasswordHasher
  - Test logique métier
  - Pas de DB, pas de réseau
  - Rapide (< 100ms)
```

### Repository Test (Intégration)

```
Test PostgresUserRepository:
  - DB test réelle
  - Test persistance
  - Test récupération
  - Test mapping
  - Nettoyage après test
```

## Avantages de cette Structure

1. **Isolation** : Domain indépendant
2. **Testabilité** : Use cases testables facilement
3. **Flexibilité** : Changement d'infrastructure sans impact métier
4. **Clarté** : Responsabilités claires
5. **Évolutivité** : Ajout de fonctionnalités facilité
6. **Maintenabilité** : Code organisé logiquement
