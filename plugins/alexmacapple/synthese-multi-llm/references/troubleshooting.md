# Troubleshooting

Guide de résolution des problèmes courants.

## Erreurs de connexion

### "CLI non trouvé: claude"

**Symptôme** : Le script affiche `✗ claude non trouvé`.

**Causes possibles** :
1. Le CLI n'est pas installé
2. Le CLI n'est pas dans le PATH
3. Problème de permissions

**Solutions** :
1. Vérifier l'installation : `which claude`
2. Installer si manquant : `npm install -g @anthropic-ai/claude-code`
3. Vérifier le PATH : `echo $PATH`
4. Relancer l'authentification : `claude auth login`

### "CLI non trouvé: gemini"

**Solutions** :
1. Installer : `npm install -g @google/gemini-cli`
2. Authentifier : `gemini auth login`

### "CLI non trouvé: codex"

**Solutions** :
1. Installer : `npm install -g @openai/codex`
2. Authentifier : `codex auth`

---

## Erreurs de timeout

### "Timeout après Xs"

**Symptôme** : L'appel au modèle dépasse le délai autorisé.

**Causes possibles** :
1. Document source trop long
2. Serveur du modèle surchargé
3. Connexion réseau lente

**Solutions** :
1. Augmenter le timeout : `--timeout 600` (10 minutes)
2. Utiliser le mode rapide : `--mode rapide`
3. Réduire la taille du texte source
4. Vérifier la connectivité : `ping api.anthropic.com`

### Timeout récurrent sur un modèle spécifique

**Solutions** :
1. Vérifier le statut du service (status.anthropic.com, etc.)
2. Exclure temporairement le modèle : le script continue avec les autres
3. Augmenter le timeout spécifique dans `synthese.config.yaml`

---

## Erreurs d'authentification

### "ANTHROPIC_API_KEY non défini"

**Symptôme** : Erreur lors de l'utilisation du backend API direct.

**Solutions** :
1. Exporter la variable : `export ANTHROPIC_API_KEY="sk-ant-..."`
2. Ou utiliser les CLIs (recommandé) qui gèrent leur propre auth

### "Authentication failed" / "Invalid API key"

**Solutions** :
1. Vérifier la clé : `echo $ANTHROPIC_API_KEY | head -c 20`
2. Regénérer la clé sur console.anthropic.com
3. Relancer l'auth CLI : `claude auth login`

---

## Erreurs de rate limit

### "Rate limit dépassé"

**Symptôme** : Trop de requêtes envoyées au modèle.

**Solutions** :
1. Attendre quelques minutes avant de relancer
2. Utiliser le cache : ne pas ajouter `--no-cache`
3. Espacer les synthèses
4. Vérifier les quotas sur le dashboard du provider

### "429 Too Many Requests"

Le retry automatique gère généralement ce cas. Si persistant :
1. Vérifier `--cache-stats` pour le taux de hits
2. Augmenter `retry.max_attempts` dans la config
3. Augmenter `retry.base_delay` pour plus d'espacement

---

## Erreurs de contenu

### "Convergence faible (< 50%)"

**Symptôme** : Les modèles produisent des analyses très divergentes.

**Explication** : Ce n'est pas nécessairement une erreur. Une faible convergence indique :
- Texte source ambigu
- Perspectives légitimement différentes
- Sujet controversé

**Solutions** :
1. Accepter la divergence comme information utile
2. Reformuler le texte source s'il est trop vague
3. Utiliser `--mode critique` pour analyse détaillée des divergences
4. Ajuster le seuil : `convergence_threshold: 0.5` dans config

### "Synthèse vide ou incomplète"

**Symptôme** : La synthèse finale manque de contenu.

**Causes possibles** :
1. Texte source trop court
2. Paramètres de cadrage inadaptés
3. Erreur silencieuse d'un modèle

**Solutions** :
1. Vérifier le texte source (> 100 mots recommandés)
2. Ajuster le cadrage : `--longueur "10-15 lignes"`
3. Vérifier le trail pour les erreurs : `synthese_trails/`
4. Essayer un autre mode : `--mode standard`

### "Glissements détectés"

**Symptôme** : Le Gardien signale des glissements sémantiques.

**Explication** : Des termes ont été substitués ou le sens a été altéré.

**Action** : C'est informatif, pas une erreur. Consultez le trail pour les détails.

---

## Erreurs de cache

### "Cache miss systématique"

**Symptôme** : Le cache ne semble jamais être utilisé.

**Explication** : Le cache est indexé par (model, prompt, role, cadrage). Toute variation invalide le cache.

**Solutions** :
1. Vérifier que `--no-cache` n'est pas actif
2. Utiliser `--cache-stats` pour diagnostiquer
3. Les mêmes paramètres de cadrage sont nécessaires pour un hit
4. Vérifier le TTL (défaut: 1 heure)

### "Erreur de lecture/écriture cache"

**Solutions** :
1. Vérifier les permissions : `ls -la .cache/synthese/`
2. Vider le cache : `--clear-cache`
3. Vérifier l'espace disque disponible

---

## Erreurs de fichiers

### "Fichier non trouvé"

**Solutions** :
1. Vérifier le chemin : utiliser chemin absolu
2. Vérifier les permissions de lecture
3. Vérifier l'encodage (UTF-8 recommandé)

### "Format non supporté"

**Symptôme** : Tentative de lecture d'un PDF/DOCX sans dépendance.

**Solutions** :
1. Installer la dépendance : `pip install pdfplumber` ou `pip install python-docx`
2. Convertir en .txt avant traitement

### "Erreur d'encodage"

**Solutions** :
1. Convertir en UTF-8 : `iconv -f ISO-8859-1 -t UTF-8 fichier.txt > fichier_utf8.txt`
2. Spécifier l'encodage dans le code si nécessaire

---

## Commandes de diagnostic

```bash
# Vérifier les CLIs disponibles
python3 skills/synthese-multi-llm/scripts/synthese.py --check

# Afficher les statistiques du cache
python3 skills/synthese-multi-llm/scripts/synthese.py --cache-stats

# Lister les sessions sauvegardées
python3 skills/synthese-multi-llm/scripts/synthese.py --list-sessions

# Vider le cache
python3 skills/synthese-multi-llm/scripts/synthese.py --clear-cache

# Mode verbose pour debug
python3 skills/synthese-multi-llm/scripts/synthese.py -f doc.txt 2>&1 | tee debug.log
```

## Obtenir de l'aide

1. Consulter les trails dans `synthese_trails/` pour les détails d'exécution
2. Vérifier les logs avec `2>&1 | tee debug.log`
3. Reporter un bug : https://github.com/Alexmacapple/Synthese-Council/issues

## Voir aussi

- [configuration.md](configuration.md) - Paramètres de configuration
- [modes.md](modes.md) - Détail des modes de synthèse
