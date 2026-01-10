# Feature Envy

## Définition

Une méthode utilise excessivement les données et méthodes d'une autre classe plutôt que celles de sa propre classe.

## Signes de Détection

- Méthode qui accède principalement aux attributs d'un autre objet
- Nombreux appels de getters sur le même objet
- Logique qui semble appartenir à une autre classe
- Méthode qui connaît trop les détails internes d'un autre objet
- Chaînage excessif de méthodes (train wreck)
- Plus d'intérêt pour les données externes que locales

## Impact

- **Encapsulation** : Violée
- **Couplage** : Fort entre les classes
- **Cohésion** : Faible dans la classe actuelle
- **Maintenance** : Logique dispersée
- **Compréhension** : Responsabilités floues
- **Tell Don't Ask** : Principe violé

## Exemple de Détection

```
Méthode dans ClasseA qui :
- Appelle objetB.getX()
- Appelle objetB.getY()
- Appelle objetB.getZ()
- Fait des calculs sur X, Y, Z
- Retourne un résultat

→ La logique devrait probablement être dans ClasseB
```

## Refactoring Recommandé

### Move Method
Déplacer la méthode dans la classe dont elle utilise les données

### Extract Method puis Move Method
Si la méthode fait plusieurs choses, extraire d'abord la partie envieuse

### Hide Delegate
Créer une méthode dans la classe cible pour encapsuler la logique

### Tell Don't Ask
Demander à l'objet de faire l'action au lieu de demander ses données

## Checklist de Review

- [ ] Méthode appelle principalement des getters d'un autre objet ?
- [ ] Logique qui calcule/transforme les données d'un autre objet ?
- [ ] Chaînage de méthodes (a.getB().getC().getD()) ?
- [ ] Méthode qui connaît la structure interne d'un autre objet ?
- [ ] Plus de références à un objet externe qu'à l'objet courant ?
- [ ] Violation du principe "Tell Don't Ask" ?

## Tell Don't Ask Principle

### ❌ Ask (Feature Envy)
```
Demander les données
Faire le traitement
Utiliser le résultat
```

### ✅ Tell
```
Demander l'action
L'objet fait son traitement
Recevoir le résultat
```

## Seuils d'Alerte

- **2-3 getters** : Vigilance
- **4-5 getters du même objet** : Refactoring recommandé
- **Chaînage > 2 niveaux** : Refactoring urgent

## Exceptions Acceptables

- DTOs et mappers (transformation intentionnelle)
- Builders (construction d'objets)
- Visitors pattern (design intentionnel)
- Queries read-only (CQRS)
- Tests (vérification d'état)

## Relation avec Law of Demeter

Feature Envy viole souvent la Law of Demeter :
"N'appelle que les méthodes de :
- L'objet courant
- Les paramètres de la méthode
- Les objets créés dans la méthode
- Les attributs directs"

## Diagnostic

Si une méthode répond "oui" à ces questions :
1. Utilise-t-elle plus de données d'un autre objet que les siennes ?
2. Pourrait-elle vivre naturellement dans cet autre objet ?
3. Change-t-elle chaque fois que l'autre objet change ?

→ C'est probablement du Feature Envy
