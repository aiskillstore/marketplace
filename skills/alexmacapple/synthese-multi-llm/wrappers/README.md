# CLI Wrappers

Ce dossier contient des exemples de scripts wrapper pour intégrer différents LLMs avec Synthèse Council.

## Concept

Un CLI wrapper est un script qui :
1. Reçoit un prompt en argument
2. Appelle un LLM (API, local, etc.)
3. Retourne la réponse sur stdout

## Wrappers disponibles

| Wrapper | LLM | Prérequis |
|---------|-----|-----------|
| `claude_wrapper.sh` | Claude (API) | `ANTHROPIC_API_KEY`, curl |
| `ollama_wrapper.sh` | Ollama (local) | Ollama installé |

## Utilisation

### 1. Rendre exécutable

```bash
chmod +x wrappers/*.sh
```

### 2. Configurer dans YAML

```yaml
# synthese.config.yaml
backends:
  cli:
    claude:
      command: "./wrappers/claude_wrapper.sh"
      args: []
    ollama:
      command: "./wrappers/ollama_wrapper.sh"
      args: []
```

### 3. Tester manuellement

```bash
# Test Claude
export ANTHROPIC_API_KEY="sk-ant-..."
./wrappers/claude_wrapper.sh "Dis bonjour"

# Test Ollama
./wrappers/ollama_wrapper.sh "Dis bonjour"
```

## Créer un wrapper personnalisé

### Template minimal

```bash
#!/bin/bash
# mon_llm_wrapper.sh

PROMPT="$1"
if [ -z "$PROMPT" ]; then
    echo "Erreur: Prompt requis" >&2
    exit 1
fi

# Appeler votre LLM ici
# La réponse doit être sur stdout
my-llm-command "$PROMPT"
```

### Bonnes pratiques

1. **Validation** : Vérifier que le prompt est fourni
2. **Erreurs sur stderr** : Les erreurs sur stderr, contenu sur stdout
3. **Code de sortie** : 0 = succès, autre = échec
4. **Timeout** : Gérer les timeouts longs
5. **Échappement** : Échapper le prompt pour JSON si nécessaire

### Exemple Python

```python
#!/usr/bin/env python3
# mon_llm_wrapper.py

import sys
import requests

def main():
    if len(sys.argv) < 2:
        print("Erreur: Prompt requis", file=sys.stderr)
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    # Appeler votre API
    response = requests.post(
        "https://api.example.com/generate",
        json={"prompt": prompt}
    )
    
    if response.ok:
        print(response.json()["text"])
    else:
        print(f"Erreur: {response.status_code}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Anthropic | - |
| `CLAUDE_MODEL` | Modèle Claude | claude-3-5-sonnet-20241022 |
| `OLLAMA_MODEL` | Modèle Ollama | llama2 |
| `OLLAMA_HOST` | URL Ollama | http://localhost:11434 |

## Dépannage

### "Commande non trouvée"

```bash
# Vérifier le chemin
which mon_wrapper.sh

# Ou utiliser le chemin absolu
command: "/chemin/complet/vers/mon_wrapper.sh"
```

### "Permission denied"

```bash
chmod +x mon_wrapper.sh
```

### "curl: command not found"

```bash
# Ubuntu/Debian
sudo apt install curl

# macOS
brew install curl
```
