# Open/Closed Principle (OCP)

## Définition

Les entités logicielles doivent être ouvertes à l'extension mais fermées à la modification.

## Principe Fondamental

```
Ajouter de nouvelles fonctionnalités sans modifier le code existant
```

## Objectif

- **Ouvert à l'extension** : Nouveau comportement ajouté facilement
- **Fermé à la modification** : Code existant non touché
- **Stabilité** : Code testé reste intact
- **Évolutivité** : Croissance sans régression

## Signes de Violation

- Modifications fréquentes du même code pour nouveaux cas
- Switch/if-else qui grandit pour chaque nouveau type
- Ajout de fonctionnalité nécessite modification de classes existantes
- Tests existants cassés par nouvelles fonctionnalités
- Code changeant pour des raisons d'extension
- Risque de régression à chaque ajout

## Impact des Violations

- **Régression** : Code stable devient instable
- **Tests** : Retester tout le code modifié
- **Risque** : Introduction de bugs dans code fonctionnel
- **Couplage** : Dépendances rigides
- **Fragility** : Changements en cascade

## Techniques d'Application

### Abstraction
Définir des interfaces que les extensions implémentent

### Polymorphisme
Utiliser le polymorphisme pour supporter de nouvelles variations

### Composition
Composer des comportements plutôt que modifier

### Strategy Pattern
Encapsuler des algorithmes interchangeables

### Template Method
Définir le squelette, laisser les détails aux sous-classes

### Dependency Injection
Injecter les dépendances pour faciliter l'extension

## Patterns Courants

### Strategy
```
Interface Strategy
    ↑
ConcreteStrategyA | ConcreteStrategyB | ConcreteStrategyC
(Extension par ajout de nouvelles stratégies)
```

### Decorator
```
Ajout de comportements sans modifier l'original
Component → wrappé par Decorators
```

### Chain of Responsibility
```
Ajout de handlers sans modifier la chaîne
Handler1 → Handler2 → Handler3 → ...
```

### Factory
```
Ajout de nouveaux types sans modifier le factory
Factory crée des instances selon le type
```

## Checklist de Review

- [ ] Ajout de fonctionnalité nécessite modification de code existant ?
- [ ] Switch/if-else sur type pour dispatcher le comportement ?
- [ ] Nouvelle variation nécessite éditer plusieurs classes ?
- [ ] Code utilise des abstractions pour les variations ?
- [ ] Nouveaux comportements ajoutables par implémentation ?
- [ ] Code existant testé reste intouché ?

## Exemple de Violation

### Switch sur Type (❌)
```
Chaque nouveau type nécessite :
- Ajouter un case dans le switch
- Modifier tous les switch similaires
- Retester tout le code modifié
```

### Solution avec Polymorphisme (✅)
```
Chaque nouveau type :
- Implémente l'interface
- Ajout sans modification du code existant
- Tests existants inchangés
```

## Équilibre Nécessaire

### Sur-engineering à Éviter
- Abstractions prématurées
- Complexité pour des variations hypothétiques
- YAGNI (You Aren't Gonna Need It)

### Quand Appliquer OCP
- Points de variation identifiés
- Extensions probables
- Code stabilisé
- Coût de modification élevé

## Checklist d'Application

### Avant Extension
- [ ] Identifier les points de variation
- [ ] Définir les abstractions
- [ ] Implémenter les variations existantes
- [ ] Tester le polymorphisme

### Lors d'Extension
- [ ] Nouvelle classe pour nouveau comportement
- [ ] Implémente l'abstraction existante
- [ ] Aucun code existant modifié
- [ ] Tests existants passent toujours

## Relation avec Autres Principes

### + Single Responsibility
Classes focalisées plus faciles à étendre

### + Liskov Substitution
Sous-types substituables garantissent l'extension

### + Dependency Inversion
Dépendre d'abstractions facilite l'extension

## Seuils d'Alerte

- **2-3 modifications** : Vigilance
- **4-5 modifications** : Considérer abstraction
- **6+ modifications** : Refactoring urgent

## Exceptions Acceptables

- Bugs à corriger (modification nécessaire)
- Refactoring interne (amélioration)
- Code jetable ou prototype
- Changement de spécification métier

## Bénéfices

- Code stable reste stable
- Extensions sans risque de régression
- Tests existants valides
- Facilite l'ajout de fonctionnalités
- Réduit le couplage
- Améliore la maintenabilité
