# God Class (Large Class)

## Définition

Classe qui accumule trop de responsabilités et devient un point central faisant trop de choses.

## Signes de Détection

- Nombreuses méthodes (> 15-20)
- Nombreux attributs (> 10-15)
- Fichier volumineux (> 300-500 lignes)
- Nom générique (Manager, Handler, Service, Util)
- Difficile à tester sans nombreux mocks
- Changements fréquents pour des raisons différentes
- Classe que "tout le monde utilise"

## Impact

- **Single Responsibility Principle** : Violé
- **Compréhension** : Difficile de comprendre toutes les responsabilités
- **Maintenance** : Changements risqués avec effets de bord
- **Couplage** : Dépendances multiples
- **Testabilité** : Tests complexes et lents
- **Réutilisabilité** : Impossible d'extraire une seule responsabilité

## Causes Communes

- "C'est plus simple de tout mettre ici"
- Évolution incrémentale sans refactoring
- Manque de vision architecturale
- Pression temporelle

## Refactoring Recommandé

### Extract Class
Identifier les responsabilités et créer des classes dédiées

### Extract Interface
Séparer les différents rôles de la classe

### Move Method
Déplacer les méthodes vers les classes appropriées

### Delegate Pattern
Déléguer les responsabilités à des collaborateurs

## Checklist de Review

- [ ] Classe > 300-500 lignes ?
- [ ] Plus de 15-20 méthodes ?
- [ ] Plus de 10-15 attributs ?
- [ ] Nom générique (Manager, Service, Handler, Util) ?
- [ ] Responsabilités multiples identifiables ?
- [ ] Changements pour des raisons métier différentes ?
- [ ] Nombreuses dépendances injectées ?

## Responsabilités à Identifier

Grouper les méthodes et attributs par :
- Cohésion fonctionnelle
- Utilisation commune
- Raison de changement
- Niveau d'abstraction

## Seuils d'Alerte

- **300-500 lignes** : Vigilance
- **500-1000 lignes** : Refactoring recommandé
- **> 1000 lignes** : Refactoring urgent

## Exceptions Acceptables

- Façades intentionnelles (avec délégation)
- Configurations ou constantes centralisées
- Generated code (DTOs, entities)
