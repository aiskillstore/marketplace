# Bonnes Pratiques de Chiffrement

## Sévérité

🔴 **CRITIQUE** - Exposition données sensibles

## Algorithmes Recommandés

### Chiffrement Symétrique

**AES (Advanced Encryption Standard)**
```
✅ AES-256-GCM (recommandé)
✅ AES-128-GCM
✅ Authentifié (GCM, CCM)
❌ AES-ECB (jamais utiliser)
⚠️ AES-CBC (nécessite HMAC séparé)
```

**ChaCha20-Poly1305**
```
✅ Alternative moderne à AES
✅ Authentifié
✅ Performance mobile
```

### Chiffrement Asymétrique

**RSA**
```
✅ RSA-2048 minimum
✅ RSA-4096 pour long terme
✅ OAEP padding
❌ PKCS#1 v1.5 (déprécié)
```

**Elliptic Curve**
```
✅ Curve25519 (X25519)
✅ P-256, P-384, P-521
✅ Plus petit clés, même sécurité
```

## Modes de Chiffrement

### GCM (Galois/Counter Mode)

```
✅ Authentifié (AEAD)
✅ Parallélisable
✅ Recommandé
⚠️ Nonce unique obligatoire
```

### CBC (Cipher Block Chaining)

```
⚠️ Nécessite IV aléatoire
⚠️ Padding oracle attack
⚠️ Ajouter HMAC pour authentification
```

### ECB (Electronic Codebook)

```
❌ NE JAMAIS UTILISER
❌ Patterns visibles
❌ Non sécurisé
```

## Génération Clés

### Clés Symétriques

**Génération**
```
✅ Cryptographically secure random
✅ 256 bits pour AES-256
✅ Unique par usage
❌ Jamais de mots de passe directs
```

**Dérivation (PBKDF)**
```
Password → KDF → Key

KDFs recommandés :
✅ Argon2id
✅ scrypt
✅ PBKDF2 (100k+ iterations)
```

### Clés Asymétriques

```
RSA : 2048+ bits
ECC : 256+ bits (Curve25519)

Génération via librairies crypto
Stockage sécurisé clé privée
```

## IV / Nonce

### Vecteur d'Initialisation

**Exigences**
```
✅ Unique pour chaque chiffrement
✅ Aléatoire (CBC)
✅ Jamais réutiliser avec même clé
✅ Taille appropriée (128 bits AES)
```

**Stockage**
```
✅ IV stocké avec ciphertext
✅ Pas besoin de secret
✅ Transmission en clair OK
```

### Nonce (GCM)

```
⚠️ CRITIQUE : UNIQUE OBLIGATOIRE
✅ 96 bits recommandé
✅ Counter ou random
❌ Réutilisation = catastrophique
```

## Authentification

### AEAD (Authenticated Encryption)

```
✅ GCM, CCM, ChaCha20-Poly1305
✅ Chiffrement + authentification intégrés
✅ Recommandé
```

### Encrypt-then-MAC

```
Si non-AEAD :
✅ Chiffrer données
✅ HMAC sur ciphertext
✅ Vérifier HMAC avant déchiffrer
```

### MAC Algorithms

```
✅ HMAC-SHA256
✅ HMAC-SHA512
✅ Poly1305 (avec ChaCha20)
❌ MD5, SHA1
```

## Padding

### PKCS#7

```
✅ Standard pour block ciphers
⚠️ Padding oracle attacks possibles
✅ Vérifier padding côté serveur
```

### OAEP (RSA)

```
✅ Pour RSA encryption
✅ Protection contre attaques
❌ Pas PKCS#1 v1.5
```

## Stockage Clés

### Ne Pas

```
❌ Hardcoder dans code
❌ Committer dans git
❌ Fichiers config non protégés
❌ Variables d'env non chiffrées (selon env)
```

### Solutions

```
✅ HSM (Hardware Security Module)
✅ KMS (Key Management Service)
✅ Secrets managers (Vault, AWS Secrets)
✅ Environment variables (chiffré si possible)
✅ Séparation dev/prod
```

## Rotation Clés

### Stratégie

```
✅ Rotation périodique (annuelle minimum)
✅ Rotation après incident
✅ Versioning clés
✅ Migration graduelle
✅ Garder anciennes pour déchiffrer
```

## Checklist d'Audit

### Algorithmes
- [ ] AES-GCM ou équivalent ?
- [ ] Pas d'algorithmes faibles (DES, RC4) ?
- [ ] Pas d'ECB mode ?
- [ ] Tailles clés appropriées ?

### Clés
- [ ] Génération sécurisée ?
- [ ] Stockage sécurisé (KMS, Vault) ?
- [ ] Rotation mise en place ?
- [ ] Pas de clés hardcodées ?

### IV/Nonce
- [ ] Unique par chiffrement ?
- [ ] Génération appropriée ?
- [ ] Jamais réutilisé ?

### Authentification
- [ ] AEAD utilisé (GCM) ?
- [ ] Ou Encrypt-then-MAC ?
- [ ] Vérification avant déchiffrement ?

## Erreurs Courantes

### ❌ ECB Mode
Patterns visibles

### ❌ Réutilisation IV/Nonce
Compromission sécurité

### ❌ Pas d'Authentification
Malleable ciphertext

### ❌ Clés Hardcodées
Exposition totale

### ❌ Padding Oracle
CBC sans authentification

## Références

- **NIST** : Cryptographic Standards
- **OWASP** : Cryptographic Storage Cheat Sheet
- **Libsodium** : Modern crypto library
