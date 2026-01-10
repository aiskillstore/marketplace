# Checklist Tests

## Pyramide des Tests

```
     /\
    /E2E\      Tests E2E (peu nombreux)
   /────\
  /Intég.\    Tests d'Intégration (Adapters)
 /────────\
/Unitaires \  Tests Unitaires (Use Cases, Domain)
────────────
```

### Équilibre
- [ ] Majorité de tests unitaires ?
- [ ] Tests d'intégration pour adapters ?
- [ ] Tests E2E pour parcours critiques uniquement ?
- [ ] Pas d'inversion de pyramide ?

## Tests Unitaires

### Scope
- [ ] Testent la logique métier (Use Cases, Entities) ?
- [ ] Isolés de l'infrastructure ?
- [ ] Utilisent des doublures (mocks/stubs) ?
- [ ] Rapides (< 100ms par test) ?

### Structure AAA
- [ ] **Arrange** : Setup clair ?
- [ ] **Act** : Une seule action testée ?
- [ ] **Assert** : Vérifications explicites ?

### Qualité
- [ ] Nom de test explicite (décrit le comportement) ?
- [ ] Un seul concept par test ?
- [ ] Pas de logique dans les tests ?
- [ ] Tests indépendants (ordre non important) ?
- [ ] Pas de dépendances entre tests ?

### Couverture
- [ ] Happy path testé ?
- [ ] Cas d'erreur testés ?
- [ ] Cas limites (edge cases) testés ?
- [ ] Validations métier testées ?

### Doublures
- [ ] **Stubs** pour données de test ?
- [ ] **Mocks** pour vérifier interactions ?
- [ ] Doublures appropriées au contexte ?
- [ ] Pas de mock excessif (over-mocking) ?

## Tests d'Intégration

### Scope
- [ ] Testent les adapters (repositories, gateways) ?
- [ ] Vérifient l'intégration réelle ?
- [ ] Base de données de test utilisée ?
- [ ] Services externes mockés/stubbed ?

### Infrastructure
- [ ] Base de données isolée par test ?
- [ ] Données de test réalistes ?
- [ ] Nettoyage après chaque test ?
- [ ] Transactions rollback si possible ?

### Vérifications
- [ ] Persistance vérifiée ?
- [ ] Récupération de données testée ?
- [ ] Mapping domain ↔ infrastructure validé ?
- [ ] Gestion d'erreurs infrastructure testée ?

### Performance
- [ ] Tests raisonnablement rapides (< 1s) ?
- [ ] Pas de dépendances externes lentes ?
- [ ] Setup/teardown optimisé ?

## Tests E2E

### Scope
- [ ] Parcours utilisateur complet ?
- [ ] Limités aux scénarios critiques ?
- [ ] Testent l'intégration complète ?

### Stabilité
- [ ] Tests déterministes ?
- [ ] Pas de flakiness ?
- [ ] Timeouts appropriés ?
- [ ] Gestion des états asynchrones ?

## Principes Généraux

### FIRST Principles
- [ ] **Fast** : Rapides à exécuter ?
- [ ] **Independent** : Indépendants les uns des autres ?
- [ ] **Repeatable** : Résultats reproductibles ?
- [ ] **Self-validating** : Pass/Fail clair ?
- [ ] **Timely** : Écrits en même temps que le code ?

### Lisibilité
- [ ] Arrange/Act/Assert visible ?
- [ ] Nom de test descriptif ?
- [ ] Pas de magic numbers (constantes nommées) ?
- [ ] Intent clair du test ?

### Maintenabilité
- [ ] Pas de duplication dans les tests ?
- [ ] Factories/builders pour données de test ?
- [ ] Setup commun factorisé ?
- [ ] Tests mis à jour avec le code ?

## Anti-patterns à Éviter

### ❌ Test Implementation
Tester les détails d'implémentation plutôt que le comportement

### ❌ Test de Getters/Setters
Tests triviaux sans valeur

### ❌ Test du Framework
Tester le framework/librairie au lieu du code métier

### ❌ Tests Dépendants
Tests qui dépendent de l'ordre d'exécution

### ❌ Tests Flaky
Tests qui passent/échouent aléatoirement

### ❌ Slow Tests
Tests unitaires lents (> 1s)

### ❌ Over-Mocking
Trop de mocks, test ne valide plus grand chose

### ❌ Assert Roulette
Multiples asserts non reliés dans un test

## Couverture de Tests

### Métriques
- [ ] Couverture > 80% pour le domain/usecases ?
- [ ] Branches critiques couvertes ?
- [ ] Logique métier complexe testée ?

### Limites de la Couverture
- [ ] Couverture ne garantit pas la qualité ?
- [ ] 100% couverture n'est pas l'objectif ?
- [ ] Focus sur les comportements critiques ?

## Doublures de Test

### Stub
- Fournit réponses prédéfinies
- Simule dépendances
- Ne vérifie pas interactions

### Mock
- Vérifie interactions
- Enregistre les appels
- Assertions sur les appels

### Spy
- Observe comportement réel
- Permet vérifications
- Hybride mock/réel

### Fake
- Implémentation simplifiée
- Fonctionnelle mais simple
- Ex: InMemoryRepository

## Stratégie par Couche

### Domain/Model
- Tests unitaires purs
- Pas de dépendances externes
- Focus sur logique métier

### Use Cases
- Tests unitaires avec mocks
- Mocks des ports (repositories, gateways)
- Vérification orchestration

### Adapters
- Tests d'intégration
- Infrastructure réelle (DB, API)
- Vérification implémentation

### API
- Tests E2E limités
- Parcours critiques
- Intégration complète

## Checklist de Review Tests

### Nouveaux Use Cases
- [ ] Tests unitaires créés ?
- [ ] Happy path testé ?
- [ ] Cas d'erreur testés ?
- [ ] Mocks des dépendances ?

### Nouveaux Adapters
- [ ] Tests d'intégration créés ?
- [ ] Persistance vérifiée ?
- [ ] Cas d'erreur testés ?

### Modifications Code
- [ ] Tests existants passent ?
- [ ] Nouveaux tests ajoutés ?
- [ ] Tests obsolètes supprimés/mis à jour ?

## Nommage des Tests

### Convention
```
methodName_scenario_expectedBehavior
should_behavior_when_condition
given_condition_when_action_then_outcome
```

### Exemples
```
createUser_withValidData_shouldSucceed
should_throwError_when_emailInvalid
given_userExists_when_createWithSameEmail_then_throwDuplicateError
```

## Assertions

### Qualité
- [ ] Assertions spécifiques (pas juste assertTrue) ?
- [ ] Messages d'erreur descriptifs ?
- [ ] Vérification de tous les aspects importants ?
- [ ] Pas d'assertions inutiles ?

### Anti-pattern
- Assertions sur tout l'objet (fragile)
- Assertions sur ordre de collections
- Comparaison d'objets sans equals approprié

## Performance des Tests

### Tests Unitaires
- [ ] < 100ms par test ?
- [ ] Pas d'I/O ?
- [ ] Pas de sleep/wait ?

### Tests d'Intégration
- [ ] < 1s par test ?
- [ ] Setup optimisé ?
- [ ] Données minimales ?

### Suite Complète
- [ ] < 5min pour tous tests ?
- [ ] Parallélisation si possible ?
- [ ] Feedback rapide ?
