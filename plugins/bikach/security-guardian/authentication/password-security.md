# Sécurité des Mots de Passe

## Principes Fondamentaux

Un système de gestion de mots de passe sécurisé doit protéger contre :
- Vol de la base de données
- Attaques par force brute
- Attaques par dictionnaire
- Rainbow tables
- Timing attacks

## Sévérité

🔴 **CRITIQUE** - Compromission de comptes utilisateurs

## Stockage des Mots de Passe

### ❌ À NE JAMAIS FAIRE

**Stockage en Clair**
- Mots de passe lisibles dans la base
- Exposition totale en cas de breach

**Chiffrement Réversible**
- Possibilité de déchiffrer
- Clé de chiffrement = point de défaillance unique

**Hash Simple (MD5, SHA1, SHA256)**
- Pas de salt
- Vulnérable aux rainbow tables
- Trop rapide = brute force facile

### ✅ BONNES PRATIQUES

**Password Hashing avec Salt**

**Algorithmes Recommandés**
```
1. Argon2id (recommandé)
   - Gagnant Password Hashing Competition 2015
   - Résistant GPU/ASIC
   - Protection mémoire

2. bcrypt
   - Éprouvé et largement supporté
   - Work factor configurable
   - Salt automatique

3. scrypt
   - Memory-hard function
   - Résistant attaques matérielles

4. PBKDF2
   - Standard NIST
   - Multiple itérations
   - Moins résistant que bcrypt/Argon2
```

**Paramètres Minimums**

**Argon2id**
```
Memory : 64 MB minimum (128 MB recommandé)
Iterations : 3-4
Parallelism : 4
```

**bcrypt**
```
Work factor (rounds) : 12 minimum (14+ recommandé)
→ Plus le nombre est élevé, plus c'est lent
```

**PBKDF2**
```
Iterations : 600,000+ pour SHA-256
Iterations : 210,000+ pour SHA-512
```

**scrypt**
```
N (CPU/memory cost) : 2^17 (128 MB)
r (block size) : 8
p (parallelization) : 1
```

## Politique de Mots de Passe

### Exigences de Complexité

**Longueur Minimale**
- **12 caractères minimum** (16+ recommandé)
- Longueur > complexité pour la sécurité

**Composition**
- Ne pas forcer mélange obligatoire (majuscules, chiffres, symboles)
- Privilégier la longueur
- Accepter espaces et caractères spéciaux
- Pas de limite maximale raisonnable (64+ caractères)

**À Éviter**
```
❌ Exigences trop complexes → passwords faibles mémorisés
❌ Rotation forcée (30/90 jours) → incréments prévisibles
❌ Interdire coller → empêche password managers
❌ Questions secrètes → facilement devinables
```

### Validation

**Check Passwords Compromis**
- Vérifier contre Have I Been Pwned API
- Rejeter passwords dans breaches connues
- k-anonymity pour privacy

**Reject Common Passwords**
- Liste top 10,000+ passwords courants
- Variations avec chiffres (password1, etc.)
- Patterns keyboard (qwerty, azerty)

**No Personal Info**
- Nom, prénom, email
- Date de naissance
- Nom d'entreprise

## Création de Compte

### Process Sécurisé

**Validation Email**
```
1. Créer compte avec password hashé
2. Générer token de validation sécurisé
3. Envoyer lien de confirmation
4. Compte activé après validation
5. Token expire (24h)
```

**Éviter Information Disclosure**
```
❌ "Email déjà utilisé" → Enumération
✅ "Si l'email existe, un lien a été envoyé"
```

## Authentification

### Rate Limiting

**Protection Brute Force**
```
Niveaux :
- Par IP : 5-10 tentatives / minute
- Par compte : 5 tentatives / 5 minutes
- Global : Protection DoS

Après échecs :
- Délai exponentiel (1s, 2s, 4s, 8s...)
- CAPTCHA après 3-5 échecs
- Compte temporairement verrouillé après X échecs
```

### Compte Lockout

**Stratégie**
```
Après X échecs consécutifs (5-10) :
- Verrouillage temporaire (15-30 min)
- OU CAPTCHA obligatoire
- Notification email au propriétaire

Éviter :
- Lockout permanent (DoS utilisateur)
- Lockout trop court (brute force continue)
```

### Timing Attack Prevention

**Constant-Time Comparison**
- Comparer hash en temps constant
- Éviter short-circuit sur premier byte différent
- Empêche timing analysis

**Même Durée Success/Failure**
- Hash même si user inexistant
- Délai similaire success/échec
- Empêche user enumeration

## Réinitialisation de Mot de Passe

### Process Sécurisé

**Token**
```
1. Génération token cryptographiquement sécurisé
   - Minimum 32 bytes random
   - Pas de patterns prévisibles

2. Stockage hash du token (pas en clair)

3. Expiration courte (1-24h)

4. Usage unique (invalidé après utilisation)

5. Invalidation de tous tokens lors du changement
```

**Envoi**
```
- Email au propriétaire uniquement
- Lien unique avec token
- Pas de question secrète
- Message générique si email inexistant
```

**Validation**
```
- Vérifier token non expiré
- Vérifier token non utilisé
- Rate limiting sur endpoint reset
- Nouvelle session après changement
```

## Changement de Mot de Passe

### Require Current Password

**Principe**
- Demander mot de passe actuel
- Protection si session compromise
- Confirmation utilisateur légitime

**Exceptions**
- Réinitialisation via token valide
- Premier login (compte temporaire)

### Invalidate Sessions

**Après Changement**
```
- Invalider toutes les sessions existantes
- Forcer reconnexion
- Invalider refresh tokens
- Notification autres devices
```

## Multi-Factor Authentication (MFA)

### Recommandations

**Encourage MFA**
- Optionnel mais fortement encouragé
- Obligatoire pour comptes privilégiés
- Backup codes fournis

**Méthodes**
```
Recommandé :
- TOTP (Time-based One-Time Password)
- Hardware keys (FIDO2/WebAuthn)
- Push notifications authenticator

À éviter :
- SMS (SIM swapping)
- Email seul (compromission email = compte)
```

## Checklist d'Audit

### Stockage
- [ ] Algorithm moderne utilisé (Argon2id, bcrypt) ?
- [ ] Pas de MD5, SHA1, SHA256 simple ?
- [ ] Paramètres suffisamment forts ?
- [ ] Salt unique par password ?
- [ ] Jamais de passwords en clair ou chiffrés ?

### Politique
- [ ] Longueur minimum 12+ caractères ?
- [ ] Pas de rotation forcée abusive ?
- [ ] Check passwords compromis (HIBP) ?
- [ ] Longueur maximale raisonnable (64+) ?

### Authentification
- [ ] Rate limiting implémenté ?
- [ ] Protection brute force (lockout, CAPTCHA) ?
- [ ] Timing attacks prévenus ?
- [ ] Messages génériques (pas d'enumeration) ?

### Réinitialisation
- [ ] Tokens cryptographiquement sécurisés ?
- [ ] Expiration des tokens ?
- [ ] Usage unique des tokens ?
- [ ] Rate limiting sur reset ?

### MFA
- [ ] MFA disponible ?
- [ ] MFA obligatoire pour admins ?
- [ ] Backup codes fournis ?
- [ ] Pas de SMS comme seul facteur ?

## Erreurs Courantes

### ❌ Password Hints
Stockage d'indices de mot de passe (facilite attaques)

### ❌ Security Questions
Réponses faciles à deviner ou trouver (nom de jeune fille, ville natale)

### ❌ Email en Username
Révèle email, facilite phishing

### ❌ Password Complexity Over Length
Forcer symboles au lieu de longueur suffisante

### ❌ Prevent Paste
Empêche password managers

### ❌ Client-Side Hashing Only
Hash côté serveur essentiel

## Références

- **OWASP** : Password Storage Cheat Sheet
- **NIST SP 800-63B** : Digital Identity Guidelines
- **Have I Been Pwned** : Compromised Password Check
- **Password Hashing Competition** : Argon2
