# Domain-Driven Design (DDD)

## Bounded Context

Chaque bounded context représente une frontière de contexte métier autonome.

```
project/
├── user-context/         # Bounded Context 1
├── order-context/        # Bounded Context 2
└── payment-context/      # Bounded Context 3
```

### Règles d'Isolation
- Chaque context a son propre domain
- Communication via Gateway uniquement
- Pas d'entités partagées entre contexts
- Chaque context peut avoir sa propre représentation d'un concept

## Building Blocks DDD

### Entities (domain/model/)
- Identité unique et continue
- Cycle de vie distinct
- État mutable
- Logique métier encapsulée

### Value Objects (domain/model/)
- Identifiés par leurs valeurs
- Immutables
- Pas d'identité propre
- Encapsulent logique de validation
- Remplacent les types primitifs

### Aggregates
- Cluster d'entités et value objects
- Racine d'agrégat (Aggregate Root)
- Frontière de cohérence transactionnelle
- Seule la racine est accessible de l'extérieur

### Repository (domain/port/)
- Interface de persistance
- Collections d'aggregates
- Abstraction de la persistance
- Défini dans le domain, implémenté dans infrastructure

### Use Case (domain/usecase/)
- Orchestration de la logique métier
- Coordination des entités et services
- Point d'entrée de l'application
- Transactionnel

### Domain Service (domain/model/)
- Logique métier sans état
- Opérations sur plusieurs entités
- Pas naturellement dans une entité

### Gateway (domain/port/)
- Interface vers systèmes externes
- Communication entre bounded contexts
- Abstraction des services tiers

## Ubiquitous Language

Le langage du code doit refléter le langage métier :
- Classes nommées selon les concepts métier
- Méthodes exprimant les actions métier
- Pas de jargon technique dans le domain

## Checklist DDD

### Bounded Context
- [ ] Contextes clairement délimités
- [ ] Communication via Gateway
- [ ] Pas de dépendances directes entre contexts

### Entities
- [ ] Ont une identité unique
- [ ] Encapsulent leur logique métier
- [ ] Ne sont pas anémiques

### Value Objects
- [ ] Immutables
- [ ] Égalité par valeur
- [ ] Validation dans le constructeur
- [ ] Remplacent les primitives pour concepts métier

### Aggregates
- [ ] Racine d'agrégat identifiée
- [ ] Cohérence transactionnelle respectée
- [ ] Modifications via la racine uniquement

### Repository
- [ ] Interface dans domain/port/
- [ ] Opérations en termes d'aggregates
- [ ] Pas de détails de persistance

### Use Case
- [ ] Un use case = un cas d'usage métier
- [ ] Orchestration claire
- [ ] Pas de logique métier complexe (déléguée au model)

## Anti-patterns DDD

### ❌ Anemic Domain Model
Entités qui sont juste des conteneurs de données sans comportement

### ❌ Primitive Obsession
Utilisation excessive de types primitifs au lieu de Value Objects

### ❌ Shared Kernel non contrôlé
Partage excessif de code entre bounded contexts

### ❌ God Aggregate
Agrégat trop large avec trop de responsabilités

### ❌ Repository trop technique
Repository qui expose des détails SQL ou ORM
