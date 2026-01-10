# Long Method

## Définition

Méthode qui dépasse 20-30 lignes de code et tente de faire trop de choses.

## Signes de Détection

- Méthode > 20-30 lignes
- Plusieurs niveaux d'indentation (> 3)
- Multiples responsabilités
- Nombreuses variables locales
- Commentaires nécessaires pour expliquer les sections
- Difficulté à nommer la méthode de façon concise

## Impact

- **Compréhension** : Difficile à lire et comprendre
- **Maintenance** : Changements risqués
- **Testabilité** : Tests complexes et nombreux cas
- **Réutilisabilité** : Impossible d'extraire des parties
- **Duplication** : Code similaire difficile à factoriser

## Causes Communes

- Ajouts successifs de fonctionnalités
- "Pendant que j'y suis..."
- Peur de créer trop de petites méthodes
- Pas de refactoring régulier

## Refactoring Recommandé

### Extract Method
Extraire des sous-méthodes avec des noms explicites pour chaque responsabilité

### Compose Method Pattern
Décomposer en méthodes de même niveau d'abstraction

### Replace Temp with Query
Remplacer les variables temporaires par des méthodes

### Decompose Conditional
Extraire les conditions complexes

## Checklist de Review

- [ ] Méthode dépasse 20-30 lignes ?
- [ ] Plusieurs niveaux d'indentation ?
- [ ] Besoin de commentaires pour comprendre les sections ?
- [ ] Nom de méthode générique (process, handle, execute) ?
- [ ] Multiples variables temporaires ?
- [ ] Code qui pourrait être réutilisé ailleurs ?

## Seuils d'Alerte

- **20-30 lignes** : Vigilance
- **30-50 lignes** : Refactoring recommandé
- **> 50 lignes** : Refactoring urgent

## Exceptions Acceptables

- Méthodes avec logique séquentielle simple et claire
- Algorithmes nécessitant une vue d'ensemble
- Builders ou configurations explicites
