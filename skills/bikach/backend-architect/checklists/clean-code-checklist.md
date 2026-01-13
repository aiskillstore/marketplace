# Checklist Clean Code

## Nommage

### Variables et Constantes
- [ ] Noms descriptifs et explicites ?
- [ ] Intention claire sans commentaire ?
- [ ] Pas d'abréviations obscures ?
- [ ] Pas de noms génériques (data, temp, obj) ?
- [ ] Conventions respectées (camelCase, UPPER_CASE) ?

### Fonctions/Méthodes
- [ ] Nom exprime clairement l'action ?
- [ ] Verbe d'action pour les méthodes ?
- [ ] Nom cohérent avec le comportement ?
- [ ] Pas de noms trompeurs ?

### Classes
- [ ] Nom substantif décrivant la responsabilité ?
- [ ] Pas de suffixes génériques (-Manager, -Handler) sans justification ?
- [ ] Respect des conventions (PascalCase) ?
- [ ] Nom du domaine métier si applicable ?

### Cohérence
- [ ] Vocabulaire uniforme dans le projet ?
- [ ] Pas de synonymes pour même concept ?
- [ ] Terminologie métier respectée ?

## Fonctions/Méthodes

### Taille
- [ ] Fonction < 20-30 lignes ?
- [ ] Une seule responsabilité ?
- [ ] Un seul niveau d'abstraction ?
- [ ] Extraction si trop longue ?

### Paramètres
- [ ] Nombre limité (< 3-4 paramètres) ?
- [ ] Parameter Object si paramètres groupés ?
- [ ] Pas de flag boolean (créer 2 méthodes) ?
- [ ] Ordre logique des paramètres ?

### Side Effects
- [ ] Effets de bord explicites dans le nom ?
- [ ] Pas de side effects cachés ?
- [ ] Méthodes query/command séparées ?
- [ ] Immutabilité privilégiée ?

### Retour
- [ ] Type de retour approprié ?
- [ ] Pas de null si évitable (Optional, exceptions) ?
- [ ] Valeur de retour cohérente ?

## Classes

### Taille
- [ ] Classe < 300-500 lignes ?
- [ ] Responsabilité unique ?
- [ ] Cohésion élevée ?
- [ ] Découpage si trop large ?

### Structure
- [ ] Attributs en haut ?
- [ ] Constructeurs après attributs ?
- [ ] Méthodes publiques avant privées ?
- [ ] Méthodes groupées par responsabilité ?

### Dépendances
- [ ] Injection de dépendances utilisée ?
- [ ] Pas d'instanciation directe de dépendances ?
- [ ] Nombre de dépendances raisonnable (< 5-7) ?

## Commentaires

### Principe
- [ ] Code auto-explicatif privilégié ?
- [ ] Commentaires uniquement si nécessaire ?
- [ ] Pas de commentaires évidents ?
- [ ] Pas de code commenté (supprimer) ?

### Quand Commenter
- [ ] Pourquoi et non comment ?
- [ ] Décisions architecturales ?
- [ ] Workarounds temporaires (avec TODO) ?
- [ ] Algorithmes complexes justifiés ?
- [ ] Warnings sur comportements non évidents ?

### Qualité
- [ ] Commentaires à jour avec le code ?
- [ ] Pas de commentaires trompeurs ?
- [ ] Français ou anglais cohérent ?

## Formatage

### Indentation
- [ ] Indentation cohérente (2 ou 4 espaces) ?
- [ ] Pas de tabs mixés avec espaces ?
- [ ] Niveau d'indentation raisonnable (< 4) ?

### Espacement
- [ ] Lignes vides pour séparer concepts ?
- [ ] Espaces autour des opérateurs ?
- [ ] Pas de lignes trop longues (< 80-120 chars) ?

### Organisation
- [ ] Code lié groupé ensemble ?
- [ ] Déclarations proches de l'utilisation ?
- [ ] Ordre logique du code ?

## Gestion des Erreurs

### Exceptions
- [ ] Exceptions pour cas exceptionnels ?
- [ ] Types d'exceptions appropriés ?
- [ ] Messages d'erreur descriptifs ?
- [ ] Pas de catch vide ?
- [ ] Cleanup dans finally ou try-with-resources ?

### Validation
- [ ] Validation des paramètres en entrée ?
- [ ] Fail fast (échouer rapidement) ?
- [ ] Exceptions métier explicites ?

## DRY (Don't Repeat Yourself)

### Duplication
- [ ] Pas de code dupliqué ?
- [ ] Logique commune extraite ?
- [ ] Pas de copier-coller ?
- [ ] Réutilisation via abstraction ?

### Extraction
- [ ] Méthodes communes factorisées ?
- [ ] Constantes pour valeurs répétées ?
- [ ] Utilities pour code générique ?

## KISS (Keep It Simple, Stupid)

### Simplicité
- [ ] Solution la plus simple choisie ?
- [ ] Pas de sur-ingénierie ?
- [ ] Complexité justifiée ?
- [ ] Code facile à comprendre ?

### Abstraction
- [ ] Niveau d'abstraction approprié ?
- [ ] Pas d'abstraction prématurée ?
- [ ] Abstractions justifiées par usage ?

## YAGNI (You Aren't Gonna Need It)

### Fonctionnalités
- [ ] Fonctionnalités nécessaires uniquement ?
- [ ] Pas de code "au cas où" ?
- [ ] Pas de généralisation prématurée ?
- [ ] Focus sur besoins actuels ?

### Flexibilité
- [ ] Extensibilité là où nécessaire ?
- [ ] Pas de flexibilité inutile ?

## Immutabilité

### Objets
- [ ] Immutabilité privilégiée quand possible ?
- [ ] Value Objects immutables ?
- [ ] État mutable justifié ?
- [ ] Copie défensive si nécessaire ?

### Collections
- [ ] Collections immuables quand approprié ?
- [ ] Pas de modification de collections partagées ?

## Principes Métier

### Ubiquitous Language
- [ ] Vocabulaire métier respecté ?
- [ ] Noms de classes/méthodes métier ?
- [ ] Pas de traduction technique inutile ?

### Clarté Métier
- [ ] Intentions métier claires ?
- [ ] Logique métier explicite ?
- [ ] Règles métier visibles ?

## Anti-patterns

### ❌ Magic Numbers
Constantes non nommées

### ❌ God Object
Classe qui fait tout

### ❌ Spaghetti Code
Code non structuré, difficile à suivre

### ❌ Cargo Cult
Code copié sans comprendre

### ❌ Dead Code
Code inutilisé à supprimer

### ❌ Callback Hell
Imbrication excessive de callbacks

## Lisibilité

### Compréhension
- [ ] Code lisible par un développeur junior ?
- [ ] Intent claire sans debug ?
- [ ] Flow logique facile à suivre ?
- [ ] Pas de cleverness inutile ?

### Structure
- [ ] Découpage logique ?
- [ ] Hiérarchie claire ?
- [ ] Dépendances évidentes ?

## Performance vs Lisibilité

### Équilibre
- [ ] Lisibilité privilégiée par défaut ?
- [ ] Optimisation seulement si nécessaire ?
- [ ] Optimisation justifiée par mesures ?
- [ ] Optimisation documentée si impact lisibilité ?

## Checklist Globale

### Before Commit
- [ ] Code auto-explicatif ?
- [ ] Pas de duplication ?
- [ ] Tests passent ?
- [ ] Linter/formatter appliqué ?
- [ ] Pas de code commenté ?
- [ ] Pas de console.log/print debug ?
- [ ] Imports inutilisés supprimés ?

### Code Review
- [ ] Intent claire ?
- [ ] Pas de surprise ?
- [ ] Maintenabilité acceptable ?
- [ ] Respect des conventions projet ?

## Boy Scout Rule

**"Laisser le code plus propre qu'on l'a trouvé"**
- [ ] Petits refactorings si opportunité ?
- [ ] Noms améliorés ?
- [ ] Duplication supprimée ?
- [ ] Simplicité augmentée ?

## Règles d'Or

1. **Clarté > Concision** : Code clair plus important que code court
2. **Lisible par humains** : Code lu plus souvent qu'écrit
3. **Simplicité** : Solution la plus simple qui fonctionne
4. **Consistance** : Respecter le style du projet
5. **Refactoring continu** : Améliorer régulièrement
