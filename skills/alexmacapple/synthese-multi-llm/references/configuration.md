# Configuration Avancée

Ce document détaille tous les paramètres configurables dans `synthese.config.yaml`.

## Timeouts

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `timeout_default` | 300 | Timeout global par appel modèle (secondes) |
| `timeout_claude` | 300 | Override spécifique pour Claude |
| `timeout_gemini` | 300 | Override spécifique pour Gemini |
| `timeout_codex` | 300 | Override spécifique pour Codex |

## Convergence

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `convergence_threshold` | 0.7 | Seuil minimum de convergence (0.0-1.0) |
| `convergence.backend` | `hybrid` | Méthode: `lexical`, `semantic`, ou `hybrid` |

### Poids de convergence (mode lexical/hybrid)

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `convergence_weights.jaccard_unigram` | 0.3 | Poids similarité Jaccard unigrams |
| `convergence_weights.jaccard_bigram` | 0.2 | Poids similarité Jaccard bigrams |
| `convergence_weights.cosine` | 0.5 | Poids similarité cosinus TF-IDF |

### Backend sémantique

Quand `convergence.backend` est `semantic` ou `hybrid` et que `sentence-transformers` est installé :

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `convergence.semantic_model` | `paraphrase-multilingual-MiniLM-L12-v2` | Modèle d'embeddings |
| `convergence.semantic_weight` | 0.7 | Poids du score sémantique en mode hybrid |
| `convergence.lexical_weight` | 0.3 | Poids du score lexical en mode hybrid |

## Retry & Backoff

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `retry.max_attempts` | 3 | Nombre maximum de tentatives par modèle |
| `retry.base_delay` | 2.0 | Délai initial entre tentatives (secondes) |
| `retry.max_delay` | 60.0 | Délai maximum (plafonné) |
| `retry.exponential_base` | 2.0 | Base pour backoff exponentiel |
| `retry.jitter` | 0.1 | Facteur de jitter aléatoire (0.0-1.0) |

### Formule de délai

```
delay = min(base_delay * (exponential_base ^ attempt), max_delay) * (1 ± jitter)
```

Exemple avec défauts :
- Attempt 1 : 2.0s (± 0.2s)
- Attempt 2 : 4.0s (± 0.4s)
- Attempt 3 : 8.0s (± 0.8s)

## Cache

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `cache.enabled` | true | Activer/désactiver le cache |
| `cache.ttl` | 3600 | Durée de vie des entrées (secondes) |
| `cache.max_size` | 1000 | Nombre maximum d'entrées |
| `cache.directory` | `.cache/synthese` | Répertoire de stockage |

### Clé de cache

Le cache est indexé par le hash SHA-256 de :
- `model` : Nom du modèle (claude, gemini, codex)
- `prompt` : Contenu du prompt
- `role` : Rôle de l'expert
- `cadrage` : Paramètres de cadrage (destinataire, finalité, etc.)

Toute variation dans ces paramètres génère une nouvelle entrée.

## Modes de synthèse

| Mode | Rounds | Description |
|------|--------|-------------|
| `standard` | 3 | Extraction → Critique → Synthèse |
| `rapide` | 2 | Extraction → Synthèse (sans critique croisée) |
| `critique` | 3 | Focus sur la critique détaillée |
| `pedagogique` | 3 | Explications du processus incluses |
| `direct` | 1 | Un seul modèle, pas de délibération |

## Rôles des experts

| Modèle | Rôle | Focus |
|--------|------|-------|
| Claude | Extracteur de Substance | Faits, données, thèse centrale |
| Gemini | Gardien de la Fidélité | Glissements, biais, omissions |
| Codex | Architecte du Sens | Structure logique, cohérence |

## Exemple de configuration personnalisée

```yaml
# synthese.config.yaml

# Timeouts généreux pour documents longs
timeout_default: 600

# Convergence sémantique stricte
convergence:
  backend: semantic
  semantic_model: paraphrase-multilingual-MiniLM-L12-v2
convergence_threshold: 0.8

# Retry agressif
retry:
  max_attempts: 5
  base_delay: 3.0
  max_delay: 120.0

# Cache longue durée
cache:
  enabled: true
  ttl: 7200  # 2 heures
  max_size: 2000
```

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Clé API pour backend Anthropic direct |
| `SYNTHESE_CONFIG` | Chemin vers fichier de configuration alternatif |
| `SYNTHESE_CACHE_DIR` | Override du répertoire de cache |
| `SYNTHESE_TRAIL_DIR` | Override du répertoire des trails |

## Voir aussi

- [troubleshooting.md](troubleshooting.md) - Résolution des problèmes
- [cadrage.md](cadrage.md) - Paramètres de cadrage détaillés
