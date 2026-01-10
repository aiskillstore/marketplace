# Dependency Inversion Principle (DIP)

## Définition

1. Les modules de haut niveau ne doivent pas dépendre des modules de bas niveau. Les deux doivent dépendre d'abstractions.
2. Les abstractions ne doivent pas dépendre des détails. Les détails doivent dépendre des abstractions.

## Principe Fondamental

```
Haut Niveau → Abstraction ← Bas Niveau
(Inversion : Bas niveau dépend de l'abstraction définie par le haut niveau)
```

## Hiérarchie Traditionnelle (❌)

```
Use Case (haut niveau)
    ↓ dépend de
Repository Concret (bas niveau)

Problème : Use Case couplé à l'implémentation
```

## Avec DIP (✅)

```
Use Case (haut niveau)
    ↓ dépend de
IRepository (abstraction)
    ↑ implémenté par
Repository Concret (bas niveau)

Solution : Les deux dépendent de l'abstraction
```

## Signes de Violation

- Import de classes concrètes d'infrastructure dans le domaine
- Use cases qui dépendent d'implémentations spécifiques
- Instanciation directe de dépendances (new)
- Dépendance sur des détails techniques
- Logique métier couplée à la base de données
- Impossible de tester sans infrastructure réelle
- Changement d'infrastructure nécessite changement du domaine

## Impact des Violations

- **Couplage** : Fort entre couches
- **Testabilité** : Difficile sans infrastructure
- **Flexibilité** : Changements techniques impactent le métier
- **Réutilisation** : Impossible sans dépendances
- **Maintenance** : Changements en cascade
- **Évolution** : Rigidité architecturale

## Architecture en Couches avec DIP

```
┌─────────────────────────────────────┐
│         Domain (Haut niveau)        │
│   - Entities, Use Cases, Ports      │
│         ↓ définit                   │
│      Interfaces (Abstractions)      │
│         ↑ implémente                │
└─────────────────────────────────────┘
           ↑
           │
┌─────────────────────────────────────┐
│    Infrastructure (Bas niveau)       │
│  - Repositories, Controllers, etc.  │
└─────────────────────────────────────┘
```

## Application dans Architecture Hexagonale

### Domain définit les Ports
```
domain/port/
  IUserRepository (interface)
  IEmailGateway (interface)
```

### Infrastructure implémente les Adapters
```
infrastructure/persistence/adapter/
  PostgresUserRepository implements IUserRepository

infrastructure/external/
  SendGridEmailGateway implements IEmailGateway
```

### Use Case dépend des Ports
```
domain/usecase/
  CreateUser(IUserRepository, IEmailGateway)
```

## Techniques d'Application

### Dependency Injection
Injecter les dépendances via constructeur

### Repository Pattern
Interface dans le domaine, implémentation dans l'infrastructure

### Factory Pattern
Créer des instances via abstractions

### Plugin Architecture
Modules chargeables implémentant des interfaces

## Checklist de Review

### Domain Layer
- [ ] Pas d'import d'infrastructure ?
- [ ] Interfaces (ports) définies dans le domain ?
- [ ] Dépendances injectées via abstractions ?
- [ ] Pas d'instanciation directe (new) de dépendances ?
- [ ] Pas d'annotations framework (@Entity, @Column) ?

### Infrastructure Layer
- [ ] Implémente les interfaces du domain ?
- [ ] Dépend du domain (via ports) ?
- [ ] Enregistre les implémentations dans le conteneur DI ?

### Application Layer
- [ ] Dépend des abstractions du domain ?
- [ ] Pas de dépendance directe sur infrastructure ?
- [ ] Use cases testables avec mocks ?

## Refactoring Recommandé

### Extract Interface
Créer une interface pour les dépendances concrètes

### Introduce Dependency Injection
Injecter au lieu d'instancier

### Move Interface to Domain
Déplacer l'interface dans le domain si elle y appartient

### Remove Direct Instantiation
Remplacer new par injection

## Relation avec Architecture Hexagonale

DIP est le fondement de l'architecture hexagonale :
- **Ports** = Abstractions définies par le domaine
- **Adapters** = Implémentations dans l'infrastructure
- **Inversion** = Infrastructure dépend du domaine

## Avantages

### Testabilité
```
Use Case testé avec mock repository
Pas besoin de base de données
```

### Flexibilité
```
Changer PostgreSQL → MongoDB
Seul l'adapter change
Use Case inchangé
```

### Découplage
```
Domaine indépendant de l'infrastructure
Évolution séparée
```

### Réutilisation
```
Domaine réutilisable
Avec différentes infrastructures
```

## Seuils d'Alerte

- **1 import infra dans domain** : Violation
- **Instanciation directe** : Violation
- **Dépendance concrète** : Violation

## Exceptions Acceptables

- Types de base du langage (string, number, Date)
- Librairies utilitaires pures (lodash, etc.)
- Value Objects techniques (UUID, etc.)

## Tests de Validation

### Test d'Isolation
Le domaine peut-il être testé sans infrastructure ?

### Test de Substitution
Peut-on changer l'implémentation sans toucher le domaine ?

### Test d'Import
Le domaine importe-t-il des modules d'infrastructure ?

### Test d'Instantiation
Y a-t-il des "new" de classes d'infrastructure dans le domaine ?

## Configuration DI

```
Infrastructure configure le conteneur :
  - Bind IUserRepository → PostgresUserRepository
  - Bind IEmailGateway → SendGridGateway

Use Case injecté avec :
  - IUserRepository (abstraction)
  - IEmailGateway (abstraction)

Runtime résout :
  - PostgresUserRepository (implémentation)
  - SendGridGateway (implémentation)
```

## Ownership des Abstractions

### ❌ Infrastructure possède l'interface
```
infrastructure/IRepository
domain dépend de infrastructure
→ Pas d'inversion
```

### ✅ Domain possède l'interface
```
domain/port/IRepository
infrastructure implémente
→ Inversion réalisée
```

## Bénéfices

- Architecture flexible et évolutive
- Domaine testable en isolation
- Changements d'infrastructure sans impact métier
- Réutilisation du domaine
- Parallélisation du développement
- Découplage fort
- Maintenance facilitée
