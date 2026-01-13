# Métriques du Skill Synthèse Council

## Vue d'ensemble

Le skill expose des métriques pour le monitoring opérationnel et l'optimisation des performances.

## Métriques de Cache (CacheMetrics)

### Champs disponibles

| Métrique | Type | Description |
|----------|------|-------------|
| `hits` | int | Nombre de requêtes servies depuis le cache |
| `misses` | int | Nombre de requêtes nécessitant un appel LLM |
| `hit_rate` | float | Ratio hits/(hits+misses), entre 0 et 1 |
| `latency_saved_ms` | float | Latence totale économisée en ms |
| `latency_saved_s` | float | Latence totale économisée en secondes |
| `entries` | int | Nombre d'entrées dans le cache |
| `size_mb` | float | Taille totale du cache en Mo |

### Seuils d'alerte recommandés

| Niveau | Condition | Action |
|--------|-----------|--------|
| OK | `hit_rate >= 0.5` | Fonctionnement normal |
| Warning | `0.1 <= hit_rate < 0.3` | Vérifier la diversité des prompts |
| Critical | `hit_rate < 0.1` | Cache inefficace, investiguer |
| Anomaly | `latency_saved < expected` | Vérifier les TTL du cache |

### Invariants mathématiques

```python
# Toujours vrai
hits + misses == total_requests
hit_rate == hits / (hits + misses) if (hits + misses) > 0 else 0
latency_saved_ms >= 0
0 <= hit_rate <= 1
```

### Accès aux métriques

```python
# Via SyntheseSession après run
session = council.run_async(text, cadrage, mode)
cache_metrics = session.cache_metrics

print(f"Cache hit rate: {cache_metrics['hit_rate']:.1%}")
print(f"Latence économisée: {cache_metrics['latency_saved_s']:.1f}s")
```

## Métriques de Retry (RetryMetrics)

### Champs disponibles par modèle

| Métrique | Type | Description |
|----------|------|-------------|
| `total_attempts` | int | Nombre total de tentatives |
| `successful_retries` | int | Retries ayant abouti |
| `total_retry_time` | float | Temps total passé en retry (s) |
| `reasons` | list[str] | Raisons des retries |
| `events` | list[RetryEvent] | Événements détaillés |

### RetryEvent (PRD-027)

Chaque retry génère un événement détaillé :

```python
RetryEvent(
    timestamp=1704000000.0,
    model="claude",
    attempt=2,
    reason="timeout",
    delay=2.5,
    error_snippet="Connection timed out..."
)
```

### Seuils d'alerte

| Niveau | Condition | Action |
|--------|-----------|--------|
| OK | `total_retries == 0` | Aucun retry nécessaire |
| Warning | `retries_per_model > 2` | Modèle potentiellement instable |
| Critical | `all_models_retrying` | Problème infrastructure |

### Accès aux métriques

```python
# Via SyntheseSession après run
session = council.run_async(text, cadrage, mode)
retry_metrics = session.retry_metrics

for model, metrics in retry_metrics.items():
    print(f"{model}: {metrics['total_attempts']} tentatives")
```

## Métriques de Convergence

### Champs disponibles

| Métrique | Type | Description |
|----------|------|-------------|
| `combined` | float | Score de convergence global (0-1) |
| `semantic` | float | Convergence sémantique |
| `lexical` | float | Convergence lexicale |

### Interprétation

| Score | Interprétation |
|-------|----------------|
| >= 0.8 | Convergence forte |
| 0.5-0.8 | Convergence modérée |
| < 0.5 | Divergence significative |

## Export des métriques

### Via trail JSON

Le trail JSON inclut toutes les métriques :

```json
{
  "session_id": "synthese-xxx",
  "cache_metrics": {
    "hits": 5,
    "misses": 10,
    "hit_rate": 0.333,
    "latency_saved_ms": 150000
  },
  "retry_metrics": {
    "claude": {"total_attempts": 3, "successful_retries": 1}
  },
  "convergence": 0.87
}
```

### Via sortie JSON

```bash
python3 synthese.py -t "texte" --json
```

## Bonnes pratiques

1. **Monitoring du hit_rate** : Un hit_rate < 0.3 indique que le cache est sous-utilisé
2. **Suivi des retries** : Des retries fréquents sur un modèle suggèrent un problème
3. **Latence économisée** : Indicateur ROI du cache
4. **Convergence** : Score < 0.5 peut nécessiter un ajustement du cadrage
