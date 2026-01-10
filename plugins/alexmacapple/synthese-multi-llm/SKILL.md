---
name: synthese-multi-llm
description: Synthèse co-fabriquée par un conseil de 3 LLMs (Claude, Gemini, Codex). Ce skill devrait être utilisé quand l'utilisateur demande une synthèse robuste, traçable et vérifiée. Il orchestre trois modèles avec des rôles experts distincts (Extracteur, Critique, Architecte) pour produire une synthèse fidèle au texte source, avec contrôle des glissements sémantiques et trail d'audit complet.
---

# Synthèse Multi-LLM (Council)

Synthèse co-fabriquée par délibération de trois LLMs : Claude, Gemini et Codex.

## Principe

> "Le sens ne s'extrait pas, il se co-fabrique."

Ce skill orchestre trois modèles IA avec des rôles experts distincts pour produire une synthèse robuste. Chaque modèle apporte une perspective différente, permettant de détecter les glissements de sens et de converger vers une synthèse fidèle.

## Prérequis

### Installation des CLI

```bash
# Claude CLI (nécessite abonnement Claude Pro/Max)
npm install -g @anthropic-ai/claude-code
claude auth login

# Gemini CLI
npm install -g @google/gemini-cli
gemini auth login

# Codex CLI
npm install -g @openai/codex
codex auth
```

### Vérification

```bash
python3 scripts/synthese.py --check
```

## Utilisation

### Phrases de déclenchement

| Phrase | Action |
|--------|--------|
| "Synthétise ce texte avec le conseil" | Processus complet multi-LLM |
| "Synthèse robuste de..." | Mode standard avec les 3 experts |
| "Synthèse rapide de..." | Mode accéléré (1 round) |
| "Analyse critique de..." | Focus sur les glissements |
| "Fais vérifier cette synthèse" | Critique croisée d'une synthèse existante |

### En ligne de commande

```bash
# Depuis un fichier
python3 scripts/synthese.py -f document.txt

# Texte direct
python3 scripts/synthese.py -t "Texte à synthétiser..."

# Mode rapide avec cadrage
python3 scripts/synthese.py -f doc.txt --mode rapide \
    --destinataire "comité de direction" \
    --finalite "décision" \
    --longueur "5 lignes" \
    --ton "formel"

# Sortie JSON
python3 scripts/synthese.py -f doc.txt --json
```

### Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `--mode` | standard, rapide, critique, pedagogique | standard |
| `--destinataire` | Public cible | interactif |
| `--finalite` | Objectif de la synthèse | interactif |
| `--longueur` | Longueur souhaitée | 10-15 lignes |
| `--ton` | Registre de langue | accessible |
| `--niveau` | Expertise attendue | intermédiaire |
| `--timeout` | Timeout par modèle (secondes) | 300 |
| `--no-trail` | Désactive la sauvegarde | false |
| `--json` | Sortie JSON structurée | false |

## Architecture

### Les 3 experts

| Rôle | Modèle par défaut | Focus |
|------|-------------------|-------|
| **L'Extracteur de Substance** | Claude | Faits, données, thèse centrale |
| **Le Gardien de la Fidélité** | Gemini | Glissements, biais, omissions |
| **L'Architecte du Sens** | Codex | Structure, logique, cohérence |

### Processus en 3 rounds

```
ROUND 1: EXTRACTION
├─ Chaque expert analyse selon son focus
├─ Identification thèse + faits + structure
└─ Production de 3 analyses indépendantes

ROUND 2: CRITIQUE CROISÉE
├─ Chaque expert critique les autres
├─ Détection des divergences
├─ Calcul du score de convergence
└─ Si convergence > 80%: passe à la synthèse

ROUND 3: SYNTHÈSE FINALE
├─ Consolidation des analyses
├─ Résolution des divergences
├─ Production de la synthèse
└─ Mention des points de dissensus
```

### Score de convergence

Le score de convergence (0-100%) indique le niveau d'accord entre les experts :

- **> 90%** : Consensus fort, haute fiabilité
- **70-90%** : Accord majoritaire, quelques nuances
- **50-70%** : Divergences significatives, vérifier les points de désaccord
- **< 50%** : Divergences majeures, analyse approfondie nécessaire

## Modes de délibération

### Standard (défaut)

Processus complet en 3 rounds. Recommandé pour les textes importants ou ambigus.

### Rapide

Un seul round d'extraction, synthèse directe. Pour les textes courts et clairs.

### Critique

Focus sur la détection des glissements. Utile pour vérifier une synthèse existante.

### Pédagogique

Explique chaque étape du processus. Pour comprendre la méthode.

## Trail d'audit

Chaque session génère un fichier JSON dans `synthese_trails/` contenant :

- Texte source (tronqué)
- Paramètres de cadrage
- Réponse de chaque expert à chaque round
- Score de convergence
- Synthèse finale
- Métadonnées (durée, modèles utilisés)

### Consulter un trail

```bash
cat synthese_trails/synthese-20250702-143052-a1b2c3.json | jq
```

## Résilience

### Modèles indisponibles

Le skill fonctionne avec 1 à 3 modèles :

| Modèles | Comportement |
|---------|--------------|
| 3 | Processus optimal |
| 2 | Processus réduit, convergence limitée |
| 1 | Mode dégradé, pas de critique croisée |

### Timeouts

Timeout adaptatif par modèle (défaut: 5 minutes). Configurable via `--timeout`.

### Erreurs

Les erreurs d'un modèle n'interrompent pas le processus. Le trail indique les échecs.

## Exemples

### Exemple 1 : Synthèse d'un rapport

```bash
python3 scripts/synthese.py -f rapport_annuel.txt \
    --destinataire "conseil d'administration" \
    --finalite "décision stratégique" \
    --longueur "1 page" \
    --ton "formel"
```

### Exemple 2 : Vérification critique

```bash
python3 scripts/synthese.py -t "Ma synthèse existante..." \
    --mode critique
```

### Exemple 3 : Pipeline avec sortie JSON

```bash
python3 scripts/synthese.py -f doc.txt --json | \
    jq -r '.synthese_finale' > synthese.md
```

## Documentation de référence

| Document | Description |
|----------|-------------|
| [configuration.md](references/configuration.md) | Paramètres avancés (timeouts, convergence, retry, cache) |
| [troubleshooting.md](references/troubleshooting.md) | Guide de résolution des problèmes |
| [cadrage.md](references/cadrage.md) | Guide du cadrage (destinataire, finalité, etc.) |
| [couches-semiotiques.md](references/couches-semiotiques.md) | Détail des 4 couches d'analyse |
| [glissements.md](references/glissements.md) | Catalogue des glissements sémantiques courants |

## Crédits

Inspiré de [Council](https://github.com/bacoco/Council-board-skill) par bacoco et du concept [LLM Council](https://github.com/karpathy/llm-council) d'Andrej Karpathy.
