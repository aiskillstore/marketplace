# Liskov Substitution Principle (LSP)

## Définition

Les objets d'une classe dérivée doivent pouvoir remplacer les objets de la classe de base sans altérer le comportement correct du programme.

## Principe Fondamental

```
Si S est un sous-type de T, alors les objets de type T peuvent être remplacés par des objets de type S sans casser le programme
```

## Règles de Substitution

### Préconditions
Les sous-types ne peuvent pas renforcer les préconditions
(Ne peuvent pas exiger plus que la classe de base)

### Postconditions
Les sous-types ne peuvent pas affaiblir les postconditions
(Doivent garantir au moins ce que la classe de base garantit)

### Invariants
Les invariants de la classe de base doivent être préservés

### Exceptions
Les sous-types ne peuvent pas lancer de nouvelles exceptions non déclarées

## Signes de Violation

- Vérifications de type (instanceof, typeof)
- Cast de type nécessaire après récupération
- Comportements inattendus avec sous-types
- Exceptions lancées par sous-types mais pas par la base
- Méthodes qui lèvent NotImplementedException
- Préconditions plus strictes dans le sous-type
- Postconditions plus faibles dans le sous-type

## Impact des Violations

- **Fragility** : Code cassé par substitution
- **Confiance** : Impossibilité de faire confiance aux abstractions
- **Polymorphisme** : Inutilisable en pratique
- **Couplage** : Dépendance aux implémentations concrètes
- **Tests** : Comportements incohérents
- **Maintenance** : Surprise et bugs

## Exemples de Violations Classiques

### Rectangle/Square Problem
```
Rectangle
    setWidth(w)
    setHeight(h)

Square extends Rectangle
    setWidth(w) → modifie width ET height

Violation : Square ne peut pas remplacer Rectangle
car il change le contrat (width et height indépendants)
```

### NotImplementedException
```
Interface avec méthode non applicable à certaines implémentations
Sous-type lance NotImplementedException
→ Violation : L'interface n'est pas la bonne abstraction
```

### Préconditions Renforcées
```
Base : accepte tous les nombres
Dérivé : accepte seulement les nombres positifs
→ Violation : Plus restrictif que la base
```

### Postconditions Affaiblies
```
Base : retourne toujours un résultat non-null
Dérivé : peut retourner null
→ Violation : Garanties affaiblies
```

## Refactoring Recommandé

### Revoir la Hiérarchie
Vérifier si l'héritage est approprié (relation "est-un" vraie)

### Composition over Inheritance
Utiliser la composition au lieu de l'héritage

### Segregate Interfaces
Séparer en interfaces plus spécifiques

### Remove Inheritance
Si la substitution n'a pas de sens, supprimer l'héritage

### Extract Common Interface
Créer une abstraction commune sans héritage

## Checklist de Review

- [ ] Sous-types utilisent-ils instanceof ou cast ?
- [ ] Sous-types lancent-ils de nouvelles exceptions ?
- [ ] Sous-types ont-ils des méthodes NotImplemented ?
- [ ] Préconditions identiques ou plus faibles ?
- [ ] Postconditions identiques ou plus fortes ?
- [ ] Invariants de la base préservés ?
- [ ] Comportement cohérent avec la base ?

## Test de Substitution

Pour chaque sous-type S de type T :
1. Remplacer T par S dans le code client
2. Le programme fonctionne-t-il correctement ?
3. Le comportement est-il cohérent ?
4. Les tests passent-ils toujours ?

Si non à une question → Violation LSP

## Design by Contract

### Contrat de la Classe de Base
- **Préconditions** : Ce qui doit être vrai avant l'appel
- **Postconditions** : Ce qui sera vrai après l'appel
- **Invariants** : Ce qui est toujours vrai

### Contrat des Sous-types
- **Préconditions** : ≤ (égales ou plus faibles)
- **Postconditions** : ≥ (égales ou plus fortes)
- **Invariants** : Préservés

## Relation avec Autres Principes

### + Open/Closed
LSP rend OCP praticable (extensions fiables)

### + Interface Segregation
ISP évite les méthodes non-applicables

### + Dependency Inversion
DIP nécessite LSP pour les abstractions

## Alternatives à l'Héritage

### Composition
```
Contenir plutôt qu'hériter
Déléguer au composant
```

### Interface Implementation
```
Implémenter interface commune
Sans hiérarchie d'héritage
```

### Strategy Pattern
```
Comportements interchangeables
Sans relation d'héritage
```

## Seuils d'Alerte

- **1 instanceof** : Vigilance
- **2+ instanceof** : Violation probable
- **NotImplemented** : Violation certaine
- **Cast nécessaire** : Violation certaine

## Exceptions Acceptables

- Frameworks nécessitant instanceof (rare)
- Optimisations performance justifiées (avec documentation)
- Pattern Visitor (intentionnel)

## Questions de Diagnostic

1. Le sous-type peut-il vraiment remplacer la base partout ?
2. Le client doit-il connaître le type concret ?
3. Les tests de la base passent-ils pour tous les sous-types ?
4. Le contrat est-il respecté ?

## Bénéfices

- Polymorphisme fiable
- Abstractions utilisables en pratique
- Code robuste aux extensions
- Moins de vérifications de type
- Confiance dans les interfaces
- Maintenance facilitée
