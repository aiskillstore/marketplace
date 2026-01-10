# Interface Segregation Principle (ISP)

## Définition

Les clients ne devraient pas être forcés de dépendre d'interfaces qu'ils n'utilisent pas.

## Principe Fondamental

```
Plusieurs interfaces spécifiques valent mieux qu'une interface générale
```

## Objectif

- Interfaces cohésives et focalisées
- Clients dépendent uniquement de ce qu'ils utilisent
- Changements isolés
- Pas de méthodes inutilisées imposées

## Signes de Violation

- Interface avec nombreuses méthodes (> 5-7)
- Implémentations qui lancent NotImplementedException
- Méthodes vides ou avec implémentation par défaut
- Clients qui n'utilisent qu'une partie de l'interface
- Changements dans l'interface impactent des clients non concernés
- Commentaires "non applicable" sur des méthodes
- Interfaces nommées de façon générique (IService, IManager)

## Impact des Violations

- **Couplage** : Clients couplés à des méthodes inutiles
- **Fragilité** : Changements impactent des clients non concernés
- **Compréhension** : Interface trop large, intention floue
- **Implémentation** : Méthodes forcées sans sens
- **Maintenance** : Changements en cascade
- **Tests** : Mocks complexes avec méthodes inutilisées

## Exemples de Violations

### Interface Monolithique
```
Interface IWorker {
    work()
    eat()
    sleep()
    manage()
}

Robot implements IWorker
    → eat() et sleep() non applicables
    → Violation ISP
```

### Interface avec Rôles Multiples
```
Interface IRepository {
    // CRUD
    save()
    findById()
    delete()

    // Reporting
    generateReport()
    exportToCSV()

    // Administration
    optimize()
    backup()
}

Clients CRUD forcés de connaître reporting et admin
→ Violation ISP
```

## Refactoring Recommandé

### Split Interface
Séparer en plusieurs interfaces cohésives

### Role Interfaces
Créer une interface par rôle/responsabilité

### Interface Composition
Client dépend de multiples petites interfaces

### Extract Interface
Extraire sous-ensemble de méthodes en nouvelle interface

## Patterns d'Application

### Role Interfaces
```
IReadable { read() }
IWritable { write() }
ICloseable { close() }

Client dépend uniquement de ce dont il a besoin
```

### Interface Segregation par Capacité
```
IPersistable
IValidatable
ISerializable
IComparable

Chaque interface = une capacité
```

### Composition d'Interfaces
```
class Repository implements IPersistable, IQueryable {
    // Implémente les deux
}

Client A dépend de IPersistable
Client B dépend de IQueryable
```

## Checklist de Review

- [ ] Interface a > 5-7 méthodes ?
- [ ] Implémentations avec NotImplemented ?
- [ ] Méthodes vides ou par défaut ?
- [ ] Clients utilisent toutes les méthodes ?
- [ ] Interface représente plusieurs rôles ?
- [ ] Changements impactent clients non concernés ?
- [ ] Interfaces nommées de façon générique ?

## Granularité des Interfaces

### Trop Large (❌)
- Nombreuses méthodes
- Plusieurs responsabilités
- Clients utilisent des sous-ensembles

### Trop Fine (❌)
- Une méthode par interface
- Fragmentation excessive
- Nombreuses interfaces par classe

### Juste Équilibrée (✅)
- Cohésion élevée
- Une responsabilité/rôle claire
- Clients utilisent la majorité des méthodes

## Stratégies de Séparation

### Par Responsabilité
Grouper méthodes par responsabilité cohérente

### Par Client
Créer interfaces selon les besoins des clients

### Par Fréquence d'Usage
Séparer méthodes fréquentes vs rares

### Par Niveau d'Abstraction
Interfaces de base vs étendues

## Relation avec Autres Principes

### + Single Responsibility
ISP au niveau interface, SRP au niveau classe

### + Liskov Substitution
ISP évite les méthodes non-applicables (NotImplemented)

### + Dependency Inversion
Interfaces focalisées facilitent les abstractions

## Checklist de Conception

### Lors de la Création
- [ ] Interface focalisée sur un rôle clair ?
- [ ] Nom explicite et précis ?
- [ ] Cohésion élevée entre les méthodes ?
- [ ] Tous les clients utiliseront toutes les méthodes ?

### Lors de l'Évolution
- [ ] Nouvelle méthode cohérente avec existantes ?
- [ ] Tous les implémenteurs concernés ?
- [ ] Séparation en nouvelle interface plus appropriée ?

## Seuils d'Alerte

- **5-7 méthodes** : Vigilance
- **8-10 méthodes** : Review recommandée
- **> 10 méthodes** : Séparation urgente
- **1 NotImplemented** : Violation certaine

## Exceptions Acceptables

- Standards (Comparable, Serializable)
- APIs publiques stables (breaking change coûteux)
- Interfaces framework avec défauts (avec justification)

## Tests d'Interface

### Test de Cohésion
Les méthodes sont-elles naturellement liées ?

### Test du Client
Chaque client utilise-t-il > 70% des méthodes ?

### Test du Rôle
L'interface représente-t-elle un seul rôle ?

### Test du Nom
Peut-on nommer sans "et" ou "ou" ?

## Avantages de Petites Interfaces

- **Clarté** : Intention évidente
- **Flexibilité** : Composition libre
- **Découplage** : Dépendances minimales
- **Testabilité** : Mocks simples
- **Évolution** : Changements isolés
- **Réutilisation** : Interfaces combinables

## Anti-pattern : Fat Interface

```
Interface trop large
    ↓
Implémentations forcées
    ↓
NotImplemented / Méthodes vides
    ↓
Clients couplés inutilement
    ↓
Maintenance difficile
```

## Bénéfices

- Interfaces claires et focalisées
- Clients découplés des fonctionnalités inutiles
- Changements localisés
- Implémentations cohérentes
- Tests simplifiés
- Meilleure réutilisabilité
