# Sécurité JWT (JSON Web Tokens)

## Définition

Tokens auto-suffisants pour l'authentification stateless, contenant claims signés et optionnellement chiffrés.

## Sévérité

🔴 **CRITIQUE** - Token forgery, bypass authentification

## Structure JWT

```
Header.Payload.Signature

Header : Algorithm + Type
Payload : Claims (données)
Signature : Vérification intégrité
```

## Vulnérabilités Courantes

### 1. Algorithm None Attack

**Problème**
```
Header : { "alg": "none" }
→ Signature non vérifiée
→ Token forgé accepté
```

**Mitigation**
```
✅ Rejeter alg: "none"
✅ Whitelist algorithmes autorisés
```

### 2. Algorithm Confusion

**Problème**
```
Serveur attend RS256 (asymétrique)
Attaquant change en HS256 (symétrique)
Utilise clé publique comme secret HMAC
→ Token forgé validé
```

**Mitigation**
```
✅ Vérifier algorithme strictement
✅ Ne pas accepter multiples algos
✅ Séparer clés par algorithme
```

### 3. Weak Signing Key

**Problème**
```
Secret HMAC faible
→ Brute force possible
→ Forger tokens valides
```

**Mitigation**
```
✅ Secret minimum 256 bits (32 bytes)
✅ Généré cryptographiquement
✅ Unique par application
```

### 4. Missing Signature Verification

**Problème**
```
Application ne vérifie pas la signature
→ Modification payload possible
```

**Mitigation**
```
✅ Toujours vérifier signature
✅ Validation stricte
```

### 5. Token in URL

**Problème**
```
Token dans URL
→ Logs serveur
→ Historique navigateur
→ Referrer headers
```

**Mitigation**
```
✅ Authorization header uniquement
✅ Cookie HttpOnly
❌ Jamais dans URL/query params
```

## Configuration Sécurisée

### Algorithmes Recommandés

**Asymétrique (Recommandé)**
```
RS256 (RSA + SHA-256)
ES256 (ECDSA + SHA-256)

Avantages :
- Clé privée serveur uniquement
- Clé publique distribuable
- Meilleure séparation
```

**Symétrique**
```
HS256 (HMAC + SHA-256)

Attention :
- Secret partagé
- Si leak = compromission totale
```

### Claims Essentiels

**Registered Claims**
```
iss (issuer) : Émetteur du token
sub (subject) : Sujet (user ID)
aud (audience) : Destinataire prévu
exp (expiration) : Timestamp expiration
nbf (not before) : Valide après timestamp
iat (issued at) : Timestamp émission
jti (JWT ID) : ID unique (anti-replay)
```

**Custom Claims**
```
Inclure uniquement données nécessaires :
- user_id
- roles/permissions
- Pas de données sensibles
```

### Expiration

**Access Token**
```
Durée courte : 15 minutes - 1 heure
→ Limite window d'exploitation
```

**Refresh Token**
```
Durée longue : 7-30 jours
Stocké serveur (blacklist possible)
Usage unique
```

## Validation JWT

### Process Complet

```
1. Vérifier format (3 parties base64)
2. Decoder header
3. Vérifier algorithme attendu
4. Vérifier signature avec clé appropriée
5. Decoder payload
6. Vérifier exp (expiration)
7. Vérifier nbf (not before)
8. Vérifier iss (issuer)
9. Vérifier aud (audience)
10. Vérifier jti si blacklist
```

### Claims Validation

**Expiration**
```
✅ Toujours vérifier exp
✅ Rejeter tokens expirés
✅ Clock skew tolerance (1-2 min)
```

**Issuer**
```
✅ Vérifier iss attendu
✅ Rejeter issuer inconnu
```

**Audience**
```
✅ Vérifier aud correspond
✅ Protection multi-tenant
```

## Stockage JWT

### Côté Client

**Options**

**1. localStorage / sessionStorage**
```
❌ Vulnérable XSS
❌ Accessible JavaScript
❌ Pas de protection
```

**2. Cookie HttpOnly**
```
✅ Protection XSS
✅ SameSite protection
✅ Secure flag
✅ Recommandé
```

**3. Memory (variables)**
```
✅ Pas de persistence
✅ Protection XSS
❌ Perdu au refresh
❌ Nécessite refresh token
```

### Côté Serveur

**Refresh Tokens**
```
Stockage obligatoire :
- Database
- Redis
→ Révocation possible
→ Tracking usage
```

## Refresh Token Pattern

### Architecture

```
1. Login → Access Token (court) + Refresh Token (long)
2. Access Token expire → Utiliser Refresh Token
3. Refresh Token → Nouveau Access Token
4. Refresh Token usage unique (rotation)
```

### Sécurité

**Rotation**
```
✅ Nouveau Refresh Token à chaque refresh
✅ Ancien invalidé
✅ Détection si réutilisé (compromission)
```

**Stockage**
```
✅ Hash du Refresh Token en DB
✅ Associé au user
✅ Metadata (IP, User-Agent)
```

## Révocation

### Stratégies

**1. Blacklist**
```
Stocker JTI des tokens révoqués
Vérifier à chaque validation
Cleanup après expiration
```

**2. Courte Durée + Refresh**
```
Access Token : 15 min
Refresh Token : Révocable
Balance : Sécurité vs Performance
```

**3. Version Token**
```
Incrémenter version user après logout
Rejeter tokens avec ancienne version
```

## Données Sensibles

### ❌ Ne Pas Inclure

```
- Passwords
- Numéros carte bancaire
- SSN, données médicales
- Secrets, API keys
- Données personnelles sensibles
```

### ✅ Données Acceptables

```
- User ID
- Username
- Roles/permissions générales
- Timestamp
- Non-sensitive metadata
```

### JWT Encryption (JWE)

**Quand Utiliser**
```
Si données sensibles nécessaires :
✅ Utiliser JWE (chiffrement)
✅ Pas juste signature (JWS)
```

## Checklist d'Audit

### Configuration
- [ ] Algorithm whitelist strict ?
- [ ] "none" rejeté ?
- [ ] Algorithm confusion prévu ?
- [ ] Secret fort (256+ bits) ?
- [ ] RS256/ES256 utilisé (asymétrique) ?

### Claims
- [ ] exp (expiration) vérifié ?
- [ ] Durée appropriée (15-60 min) ?
- [ ] iss, aud vérifiés ?
- [ ] jti pour anti-replay si critique ?

### Stockage
- [ ] Pas dans localStorage ?
- [ ] Cookie HttpOnly si cookie ?
- [ ] Authorization header utilisé ?
- [ ] Jamais dans URL ?

### Validation
- [ ] Signature toujours vérifiée ?
- [ ] Algorithm vérifié strictement ?
- [ ] Claims validés ?
- [ ] Expiration respectée ?

### Refresh
- [ ] Refresh token séparé ?
- [ ] Rotation des refresh tokens ?
- [ ] Stockage serveur refresh tokens ?
- [ ] Révocation possible ?

### Données
- [ ] Pas de données sensibles ?
- [ ] JWE si nécessaire ?
- [ ] Minimal payload ?

## Erreurs Courantes

### ❌ Accept Any Algorithm
Pas de validation algorithme strict

### ❌ Weak Secret
Secret HMAC court ou prévisible

### ❌ No Expiration
Tokens valides indéfiniment

### ❌ Sensitive Data in JWT
Données sensibles en clair

### ❌ localStorage Storage
Vulnérable XSS

### ❌ No Signature Verification
Accepter tokens non vérifiés

### ❌ Long-Lived Access Tokens
Access token 24h+ sans refresh

## Références

- **JWT.io** : JWT Debugger
- **RFC 7519** : JSON Web Token
- **OWASP** : JWT Cheat Sheet
- **CWE-347** : Improper Verification of Cryptographic Signature
