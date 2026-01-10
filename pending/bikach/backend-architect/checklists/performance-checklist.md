# Checklist Performance

## Requêtes Base de Données

### N+1 Queries
- [ ] Pas de boucles avec requêtes individuelles ?
- [ ] Utilisation de joins ou eager loading ?
- [ ] Requêtes batch quand possible ?
- [ ] Pagination pour grandes collections ?

### Indexation
- [ ] Index sur colonnes utilisées dans WHERE ?
- [ ] Index sur colonnes de jointure ?
- [ ] Index sur colonnes de tri (ORDER BY) ?
- [ ] Pas d'over-indexing (trop d'index) ?

### Requêtes Optimisées
- [ ] SELECT avec colonnes spécifiques (pas de SELECT *) ?
- [ ] Filtrage au niveau base de données (pas en mémoire) ?
- [ ] Agrégations côté base si possible ?
- [ ] Utilisation de vues matérialisées si approprié ?

## Caching

### Stratégie de Cache
- [ ] Cache pour données fréquemment lues ?
- [ ] TTL (Time To Live) approprié ?
- [ ] Invalidation de cache correcte ?
- [ ] Cache distribué si nécessaire ?

### Niveaux de Cache
- [ ] Cache applicatif pour calculs coûteux ?
- [ ] Cache base de données (query cache) ?
- [ ] Cache HTTP (CDN, reverse proxy) ?
- [ ] Cache navigateur (headers appropriés) ?

## Algorithmes et Structures de Données

### Complexité
- [ ] Algorithmes avec complexité acceptable ?
- [ ] Pas de O(n²) évitable ?
- [ ] Structures de données appropriées ?
- [ ] Recherches efficaces (Map, Set vs Array) ?

### Collections
- [ ] Streams/iterators pour grandes collections ?
- [ ] Lazy loading quand approprié ?
- [ ] Pas de chargement inutile en mémoire ?
- [ ] Filtrage précoce des données ?

## Concurrence et Asynchrone

### Traitement Asynchrone
- [ ] Opérations longues en asynchrone ?
- [ ] Utilisation appropriée de queues ?
- [ ] Traitement batch pour volume élevé ?
- [ ] Workers pour tâches de fond ?

### Parallélisation
- [ ] Opérations indépendantes parallélisées ?
- [ ] Pool de threads configuré correctement ?
- [ ] Pas de blocking I/O inutile ?
- [ ] Gestion correcte des resources partagées ?

## Mémoire

### Gestion Mémoire
- [ ] Pas de fuites mémoire (listeners non nettoyés) ?
- [ ] Streams fermés correctement ?
- [ ] Références circulaires évitées ?
- [ ] Objets volumineux libérés après usage ?

### Optimisation
- [ ] Réutilisation d'objets si approprié (pooling) ?
- [ ] Pas de création excessive d'objets temporaires ?
- [ ] Strings concatenées efficacement ?
- [ ] Buffer sizing approprié ?

## I/O et Réseau

### Appels Réseau
- [ ] Timeouts configurés ?
- [ ] Retry avec backoff exponentiel ?
- [ ] Circuit breaker pour services externes ?
- [ ] Compression des payloads ?

### Fichiers
- [ ] Lecture/écriture par chunks ?
- [ ] Streams pour gros fichiers ?
- [ ] Buffering approprié ?
- [ ] Fermeture des ressources garantie ?

## Sérialisation

### Format de Données
- [ ] Format compact (Protobuf vs JSON si approprié) ?
- [ ] Compression si données volumineuses ?
- [ ] Champs optionnels pas sérialisés si vides ?
- [ ] Lazy deserialization quand possible ?

## Monitoring et Mesures

### Observabilité
- [ ] Métriques de performance exposées ?
- [ ] Logs de performance pour opérations lentes ?
- [ ] Traces distribuées si microservices ?
- [ ] Alertes sur dégradation ?

### Profilage
- [ ] Points de mesure critiques identifiés ?
- [ ] Benchmarks pour opérations sensibles ?
- [ ] Profiling régulier des hot paths ?

## Seuils Critiques

### Response Time
- [ ] API < 100ms pour 95e percentile ?
- [ ] Requêtes DB < 50ms en moyenne ?
- [ ] Batch processing dimensionné ?

### Resources
- [ ] Consommation mémoire acceptable ?
- [ ] CPU usage sous contrôle ?
- [ ] Connexions DB poolées correctement ?

### Scalabilité
- [ ] Stateless quand possible ?
- [ ] Scalabilité horizontale possible ?
- [ ] Pas de bottleneck identifié ?

## Anti-patterns Performance

### ❌ À Éviter
- Requêtes en boucle (N+1)
- SELECT * systématique
- Chargement complet en mémoire
- Synchrone pour opérations longues
- Pas de cache pour données stables
- Pas de pagination
- Algorithmes O(n²) évitables
- Blocking I/O inutile

## Optimisation Prématurée

### ⚠️ Attention
- [ ] Optimisation justifiée par mesures réelles ?
- [ ] Impact significatif démontré ?
- [ ] Compromis lisibilité/performance acceptable ?
- [ ] Pas de sur-optimisation ?

## Règle d'Or

**"Mesurer avant d'optimiser"**
- Profiler d'abord
- Identifier les vraies bottlenecks
- Optimiser ce qui compte
- Re-mesurer après optimisation
