# Shotgun Surgery

## Définition

Un changement nécessite de modifier plusieurs classes et méthodes dispersées dans le code. L'inverse de Divergent Change.

## Signes de Détection

- Changement simple qui touche de nombreux fichiers
- Logique dupliquée dans plusieurs classes
- Responsabilité fragmentée
- Changements systématiquement groupés
- Oublis fréquents lors des modifications
- Refactorings en cascade
- Grep nécessaire pour trouver tous les endroits à changer

## Impact

- **Maintenance** : Coûteuse et risquée
- **Bugs** : Oublis fréquents de modifications
- **Compréhension** : Logique dispersée
- **Tests** : Nombreux tests à modifier
- **Cohésion** : Faible
- **Coupling** : Fragmentation de la responsabilité
- **Évolution** : Frein aux changements

## Causes Communes

- Copy-paste de code
- Logique métier dupliquée
- Manque d'abstraction
- Sur-découpage sans vision globale
- Évolution incrémentale sans refactoring

## Exemples Typiques

### Logique de Calcul Dupliquée
Formule de calcul répétée dans plusieurs classes

### Validation Dispersée
Règles de validation du même concept dans plusieurs endroits

### Gestion d'Erreurs
Pattern de gestion d'erreur répété partout

### Transformation de Données
Mapping/conversion répété dans plusieurs adapters

### Configuration
Paramètres hardcodés dans plusieurs classes

## Refactoring Recommandé

### Move Method/Field
Regrouper les éléments dispersés dans une seule classe

### Inline Class
Si une classe ne fait plus grand chose après déplacements

### Extract Class
Créer une classe dédiée pour la responsabilité fragmentée

### Introduce Parameter/Field
Centraliser les données utilisées partout

### Extract Superclass/Interface
Factoriser le comportement commun

## Checklist de Review

- [ ] Changement simple qui touche > 3 classes ?
- [ ] Logique similaire/identique dans plusieurs endroits ?
- [ ] Modifications toujours groupées ?
- [ ] Besoin de chercher tous les endroits à modifier ?
- [ ] Risque d'oubli lors des changements ?
- [ ] Duplication de code détectée ?
- [ ] Responsabilité fragmentée identifiée ?

## Stratégies de Correction

### 1. Identifier la Responsabilité
Quelle est la responsabilité fragmentée ?

### 2. Trouver le Bon Endroit
Où devrait-elle être centralisée ?

### 3. Extraire ou Déplacer
Consolider la logique dispersée

### 4. Supprimer la Duplication
Faire référence à la source unique

### 5. Tester
Vérifier que tout fonctionne encore

## Seuils d'Alerte

- **3-4 fichiers** : Vigilance
- **5-7 fichiers** : Refactoring recommandé
- **> 7 fichiers** : Refactoring urgent

## Relation avec Autres Smells

### vs Divergent Change
- **Shotgun Surgery** : Un changement → Plusieurs classes
- **Divergent Change** : Plusieurs types de changements → Une classe

### Souvent Accompagné de
- Code duplication
- Feature Envy
- Large Class (la cible de consolidation)

## Diagnostic

### Questions Clés
1. Combien de classes dois-je modifier pour ce changement ?
2. La logique est-elle dupliquée ?
3. Y a-t-il un concept métier non capturé ?
4. Où devrait vivre cette responsabilité naturellement ?

### Test du Changement
Si ajouter une nouvelle règle métier nécessite :
- Modifier > 3 fichiers
- Chercher tous les endroits similaires
- Risquer d'oublier un endroit

→ C'est du Shotgun Surgery

## Exceptions Acceptables

- Changement d'API publique (inévitable)
- Renommage global intentionnel
- Migration de framework
- Refactoring architectural
