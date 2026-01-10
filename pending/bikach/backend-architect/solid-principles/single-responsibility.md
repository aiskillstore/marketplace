# Single Responsibility Principle (SRP)

## Définition

Une classe ne devrait avoir qu'une seule raison de changer. Chaque classe doit avoir une seule responsabilité.

## Principe Fondamental

```
Une classe = Une responsabilité = Une raison de changer
```

## Signes de Violation

- Classe avec un nom générique (Manager, Handler, Service, Util)
- Méthodes qui n'ont pas de cohésion entre elles
- Changements métier différents impactent la même classe
- Classe difficile à nommer de façon concise
- Nombreuses dépendances (> 5-7)
- Tests qui nécessitent beaucoup de setup différent
- Classe utilisée pour des raisons différentes

## Impact des Violations

- **Couplage** : Classe couplée à plusieurs concepts
- **Fragilité** : Changement dans une responsabilité casse les autres
- **Réutilisation** : Impossible de réutiliser une seule responsabilité
- **Compréhension** : Difficile de comprendre toutes les facettes
- **Tests** : Complexes avec nombreux cas
- **Maintenance** : Conflits de merge fréquents

## Questions de Diagnostic

### Test de la Raison de Changer
"Pourquoi cette classe changerait-elle ?"
- Si plusieurs réponses → Violation du SRP

### Test du Nom
"Peut-on nommer cette classe sans utiliser 'et' ou 'ou' ?"
- Si non → Multiple responsabilités

### Test de Description
"Décrivez cette classe en une phrase sans utiliser 'et'"
- Si impossible → Violation du SRP

## Refactoring Recommandé

### Extract Class
Créer une classe par responsabilité identifiée

### Move Method
Déplacer les méthodes vers les classes appropriées

### Facade Pattern
Si besoin de coordination, créer une facade qui délègue

### Delegate Pattern
Déléguer chaque responsabilité à un collaborateur

## Checklist de Review

- [ ] Classe a-t-elle un nom précis et concis ?
- [ ] Toutes les méthodes sont-elles cohérentes ?
- [ ] Une seule raison métier de changer ?
- [ ] Cohésion élevée entre les attributs et méthodes ?
- [ ] Dépendances limitées (< 5-7) ?
- [ ] Tests focalisés sur un seul aspect ?

## Niveaux de Responsabilité

### Classe/Module
Une responsabilité métier ou technique claire

### Méthode
Une action cohérente et atomique

### Module/Package
Un domaine métier ou technique délimité

## Responsabilités Courantes

### Responsabilités Métier
- Validation de règles métier
- Calcul métier
- Orchestration de cas d'usage
- Gestion d'un aggregate

### Responsabilités Techniques
- Persistance
- Logging
- Validation de format
- Communication réseau
- Cache

## Seuils d'Alerte

- **2 responsabilités** : Vigilance
- **3 responsabilités** : Refactoring recommandé
- **4+ responsabilités** : Refactoring urgent

## Cohésion Élevée

### Signes de Bonne Cohésion
- Méthodes utilisent les mêmes attributs
- Changement métier touche plusieurs méthodes ensemble
- Nom de classe explicite
- Tests naturellement groupés

### Signes de Faible Cohésion
- Méthodes indépendantes
- Attributs utilisés par des sous-ensembles de méthodes
- Groupes de méthodes identifiables
- Tests sur des aspects différents

## Relation avec Autres Principes

### vs Open/Closed
SRP facilite l'extension sans modification

### vs Interface Segregation
SRP au niveau classe, ISP au niveau interface

### vs Dependency Inversion
SRP rend les abstractions plus claires

## Exceptions Acceptables

- Facades intentionnelles (avec délégation)
- DTOs simples (transport de données)
- Configuration centralisée
- Utilities purement techniques (avec justification)

## Bénéfices

- Code plus lisible et compréhensible
- Facilite les changements
- Réutilisation plus simple
- Tests plus simples
- Moins de conflits de merge
- Évolution indépendante des responsabilités
