# Injection de Dépendances

## Principe

Les dépendances doivent être injectées via le constructeur, permettant :
- Inversion de contrôle
- Testabilité (injection de mocks)
- Découplage
- Respect du Dependency Inversion Principle

## Pattern d'Injection

```
Use Case (domain/usecase)
    ↓ dépend de
Interface (domain/port)
    ↑ implémentée par
Adapter (infrastructure/persistence/adapter)
    ↓ injecté via
Conteneur DI (main/configuration)
```

## Types d'Injection

### Constructor Injection (Recommandé)
- Dépendances obligatoires
- Immutabilité
- Testabilité

### Property Injection (Éviter)
- Dépendances optionnelles
- État mutable
- Risque d'oubli

### Method Injection (Rare)
- Dépendance ponctuelle
- Contexte spécifique

## Configuration DI

```
Configuration (infrastructure)
    ↓
Enregistre les bindings :
    - Port → Adapter
    - Interface → Implémentation
    ↓
Injecte dans Use Cases
```

## Règles d'Injection

### ✅ Bonnes Pratiques
- Injection par constructeur
- Dépendre des abstractions (interfaces)
- Une seule implémentation active par environnement
- Configuration centralisée

### ❌ Mauvaises Pratiques
- Instanciation directe dans le code
- Dépendance sur des classes concrètes
- Service Locator pattern
- Injection circulaire

## Checklist

### Use Cases
- [ ] Dépendances injectées via constructeur
- [ ] Dépend des ports (interfaces), pas des adapters
- [ ] Pas d'instanciation directe de dépendances

### Adapters
- [ ] Enregistrés dans le conteneur DI
- [ ] Implémentent les interfaces du domain/port
- [ ] Lifecycle correct (singleton, scoped, transient)

### Configuration
- [ ] Bindings centralisés
- [ ] Configuration par environnement
- [ ] Pas de logique métier dans la config

## Anti-patterns

### ❌ New dans le Use Case
Instanciation directe au lieu d'injection

### ❌ Dépendance concrète
Use case qui dépend de l'adapter au lieu du port

### ❌ Service Locator
Utilisation d'un locator pour récupérer des dépendances

### ❌ Circular Dependency
A dépend de B qui dépend de A

### ❌ Hidden Dependencies
Dépendances non visibles dans la signature (static, singleton)
