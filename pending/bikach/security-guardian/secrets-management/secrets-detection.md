# Détection de Secrets

## Définition

Identification de secrets (passwords, API keys, tokens) hardcodés dans le code ou configuration.

## Sévérité

🔴 **CRITIQUE** - Exposition credentials, compromission totale

## Types de Secrets à Détecter

### Credentials

```
- Passwords
- Database connection strings
- SMTP credentials
- FTP/SFTP credentials
```

### API Keys & Tokens

```
- AWS Access Keys (AKIA...)
- GitHub tokens (ghp_, gho_)
- Slack tokens
- Stripe keys (sk_live_)
- Google API keys
- JWT secrets
```

### Certificates & Keys

```
- Private keys (BEGIN PRIVATE KEY)
- SSH keys (BEGIN OPENSSH PRIVATE KEY)
- PGP private keys
- Certificates
```

### Other Secrets

```
- Encryption keys
- Signing secrets
- Webhook secrets
- OAuth client secrets
```

## Patterns de Détection

### Regex Patterns

**AWS Keys**
```
AKIA[0-9A-Z]{16}
aws_access_key_id.*=.*[A-Z0-9]{20}
```

**Private Keys**
```
-----BEGIN (RSA |DSA )?PRIVATE KEY-----
-----BEGIN OPENSSH PRIVATE KEY-----
```

**Generic Secrets**
```
(password|passwd|pwd).*=.*['\"][^'\"]+['\"]
api[_-]?key.*=.*['\"][^'\"]+['\"]
secret.*=.*['\"][^'\"]+['\"]
token.*=.*['\"][^'\"]+['\"]
```

**URLs avec Credentials**
```
https?://[^:]+:[^@]+@
mysql://.*:.*@
postgresql://.*:.*@
```

## Où Chercher

### Code Source

```
✅ Fichiers source (.js, .py, .java, etc.)
✅ Tests
✅ Scripts
✅ Documentation avec exemples
```

### Configuration

```
✅ .env files
✅ config.json, settings.yml
✅ docker-compose.yml
✅ kubernetes manifests
✅ CI/CD configs (.gitlab-ci.yml, .github/workflows)
```

### Git History

```
✅ Commits précédents
✅ Branches abandonnées
✅ Tags
✅ Fichiers supprimés
```

### Build Artifacts

```
✅ Binaires compilés
✅ Containers Docker
✅ Archives
✅ Logs build
```

## Outils de Détection

### Pre-commit Hooks

```
✅ git-secrets (AWS)
✅ detect-secrets (Yelp)
✅ gitleaks
✅ truffleHog
```

### CI/CD Scanning

```
✅ GitGuardian
✅ GitHub Secret Scanning
✅ GitLab Secret Detection
✅ Scan automatique chaque commit/PR
```

### Repository Scanning

```
✅ truffleHog (historique complet)
✅ gitleaks
✅ git-secrets
```

## Remédiation

### Si Secret Découvert

**1. Révoquer Immédiatement**
```
✅ Désactiver/révoquer credential
✅ Générer nouveau secret
✅ Mettre à jour applications
```

**2. Nettoyer Git History**
```
✅ git filter-branch
✅ BFG Repo-Cleaner
✅ Réécrire historique
⚠️ Force push
⚠️ Tous clones doivent re-clone
```

**3. Investiguer**
```
✅ Qui a commit ?
✅ Quand ?
✅ Secret utilisé ?
✅ Logs accès
✅ Compromission ?
```

**4. Prévention**
```
✅ Activer pre-commit hooks
✅ Formation équipe
✅ Process review
```

### Nettoyage Git

**BFG Repo-Cleaner (Recommandé)**
```
Télécharger BFG
bfg --replace-text passwords.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

**git filter-branch**
```
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret' \
  --prune-empty --tag-name-filter cat -- --all
```

## Prévention

### Ne Jamais Commit

```
❌ Passwords
❌ API keys
❌ Private keys
❌ Tokens
❌ Connection strings avec credentials
❌ Secrets de toute nature
```

### Utiliser

```
✅ Variables d'environnement
✅ Secrets managers (Vault, AWS Secrets)
✅ KMS
✅ .env (avec .gitignore)
✅ Config files non-versionnés
```

### .gitignore

```
.env
.env.local
.env.*.local
config/secrets.yml
credentials.json
*.pem
*.key
id_rsa
```

### Pre-commit Hooks

```
Installer :
- git-secrets
- detect-secrets
- gitleaks

Bloquer commit si secret détecté
```

### CI/CD Gates

```
✅ Scan automatique chaque PR
✅ Bloquer merge si secret trouvé
✅ Alertes équipe sécurité
```

## Checklist d'Audit

### Détection
- [ ] Scan repository effectué ?
- [ ] Historique Git scanné ?
- [ ] CI/CD scanning activé ?
- [ ] Pre-commit hooks installés ?

### Configuration
- [ ] .gitignore secrets files ?
- [ ] .env non commité ?
- [ ] Config files avec secrets exclus ?

### Process
- [ ] Formation équipe ?
- [ ] Process si secret découvert ?
- [ ] Review PR inclut secrets check ?
- [ ] Rotation régulière secrets ?

### Outils
- [ ] git-secrets ou équivalent ?
- [ ] CI/CD secret scanner ?
- [ ] Alertes automatiques ?

## Faux Positifs

### Réduire

```
✅ Whitelist patterns connus OK
✅ Ignore test fixtures (avec attention)
✅ Documenter exceptions
✅ Review manuel si doute
```

### Exemples Non-Secrets

```
- Example passwords dans docs
- Test fixtures
- Public API keys (non-sensible)
- Placeholders (<YOUR_API_KEY>)
```

## Références

- **GitHub** : Secret Scanning
- **GitGuardian** : Secrets Detection
- **OWASP** : Secrets Management Cheat Sheet
- **git-secrets** : AWS Labs
