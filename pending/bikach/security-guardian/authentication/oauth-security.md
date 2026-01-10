# Sécurité OAuth 2.0 / OpenID Connect

## Définition

OAuth 2.0 : Framework d'autorisation permettant accès délégué
OpenID Connect : Couche d'authentification au-dessus d'OAuth 2.0

## Sévérité

🔴 **CRITIQUE** - Account takeover, token theft

## Flows OAuth 2.0

### Authorization Code Flow (Recommandé)

```
1. Redirection vers authorization server
2. User authentifie et consent
3. Redirect back avec authorization code
4. Exchange code pour access token (server-side)
5. Utiliser access token
```

**Sécurité**
- Code éphémère
- Token jamais exposé au browser
- Client secret côté serveur

### Implicit Flow (Déprécié)

```
❌ Déprécié - Ne pas utiliser
Token dans URL fragment
Exposé au browser
Pas de client secret
```

### PKCE (Proof Key for Code Exchange)

**Obligatoire pour**
- Applications mobiles
- SPAs (Single Page Apps)
- Tout client public

**Process**
```
1. Générer code_verifier (random)
2. Calculer code_challenge = hash(code_verifier)
3. Envoyer code_challenge avec auth request
4. Provider stocke code_challenge
5. Exchange code avec code_verifier
6. Provider vérifie hash(code_verifier) == code_challenge
```

## Vulnérabilités OAuth

### 1. Authorization Code Interception

**Attaque**
```
Attaquant intercepte authorization code
→ Exchange pour token avant victime
```

**Mitigation**
```
✅ PKCE obligatoire
✅ state parameter
✅ Courte durée code (10 min max)
✅ Usage unique du code
```

### 2. CSRF sur Redirect URI

**Attaque**
```
Attaquant initie OAuth flow
Victime clique lien avec state de l'attaquant
Compte victime lié au compte attaquant
```

**Mitigation**
```
✅ state parameter unique et imprévisible
✅ Vérifier state au callback
✅ Lier à la session utilisateur
```

### 3. Open Redirect

**Attaque**
```
redirect_uri=https://trusted.com/callback?next=https://evil.com
→ Authorization code leak vers evil.com
```

**Mitigation**
```
✅ Whitelist strict redirect_uri
✅ Exact match (pas de wildcards)
✅ Validation côté authorization server
```

### 4. Token Theft

**Attaque**
```
XSS, MITM, Phishing
→ Vol access/refresh token
```

**Mitigation**
```
✅ HttpOnly cookies si possible
✅ Short-lived access tokens
✅ Refresh token rotation
✅ Token binding
```

## Configuration Sécurisée

### Redirect URI

**Validation Stricte**
```
✅ Enregistrer redirect_uris à l'avance
✅ Exact match uniquement
❌ Pas de wildcards (*.example.com)
❌ Pas de open redirects
❌ Pas de http:// (https uniquement)
```

### State Parameter

**Obligatoire**
```
✅ Générer state aléatoire unique
✅ Stocker en session
✅ Vérifier au callback
✅ Usage unique
✅ Expiration courte
```

### Client Credentials

**Client Secret**
```
✅ Secret fort (256+ bits)
✅ Stocké serveur uniquement
❌ Jamais dans code client public
❌ Jamais dans mobile/SPA
```

**Client Types**
```
Confidential :
- Backend server
- Client secret sécurisé

Public :
- Mobile app
- SPA
- Pas de secret
- PKCE obligatoire
```

### Scopes

**Principe Least Privilege**
```
✅ Demander scopes minimums nécessaires
✅ User consent pour scopes sensibles
✅ Validation scopes serveur
```

### Token Lifetime

**Access Token**
```
Durée courte : 1 heure max
Spécialisé par scope
```

**Refresh Token**
```
Durée moyenne : 7-90 jours
Révocable
Rotation recommandée
```

**Authorization Code**
```
Très court : 10 minutes max
Usage unique
```

## PKCE Implementation

### Génération

```
1. code_verifier :
   - 43-128 caractères
   - [A-Z][a-z][0-9]-._~
   - Cryptographiquement aléatoire

2. code_challenge :
   - S256 : BASE64URL(SHA256(code_verifier))
   - Plain : code_verifier (moins sécurisé)
```

### Flow

```
Authorization Request :
  ?code_challenge=<challenge>
  &code_challenge_method=S256

Token Request :
  code_verifier=<verifier>

Validation :
  hash(verifier) == stored_challenge
```

## Token Management

### Access Token

**Usage**
```
Authorization: Bearer <access_token>

Validation :
- Signature
- Expiration
- Scopes
- Audience
```

**Stockage Client**
```
✅ Memory (variables)
✅ SessionStorage si nécessaire
❌ localStorage (XSS risk)
```

### Refresh Token

**Usage**
```
POST /token
  grant_type=refresh_token
  refresh_token=<token>
  client_id=<id>
  client_secret=<secret>
```

**Stockage**
```
✅ HttpOnly cookie
✅ Secure storage (mobile)
❌ localStorage
```

**Rotation**
```
✅ Nouveau refresh token à chaque refresh
✅ Invalider ancien
✅ Détection réutilisation = révocation famille
```

## OpenID Connect

### ID Token (JWT)

**Claims Standards**
```
iss : Issuer
sub : Subject (user ID)
aud : Audience (client_id)
exp : Expiration
iat : Issued at
nonce : Anti-replay
```

**Validation**
```
1. Vérifier signature
2. Vérifier iss (issuer connu)
3. Vérifier aud (client_id)
4. Vérifier exp
5. Vérifier nonce si utilisé
```

### UserInfo Endpoint

**Usage**
```
GET /userinfo
Authorization: Bearer <access_token>

Retourne : Claims utilisateur
```

### Nonce

**Anti-Replay**
```
✅ Générer nonce unique
✅ Inclure dans auth request
✅ Vérifier dans ID token
✅ Usage unique
```

## Checklist d'Audit

### Configuration
- [ ] Authorization Code Flow utilisé ?
- [ ] PKCE activé (public clients) ?
- [ ] Implicit flow désactivé ?
- [ ] Client secret fort (confidential) ?

### Redirect URI
- [ ] Whitelist strict ?
- [ ] Exact match ?
- [ ] Pas de wildcards ?
- [ ] HTTPS uniquement ?

### State & Nonce
- [ ] state parameter utilisé et vérifié ?
- [ ] nonce pour OpenID Connect ?
- [ ] Génération cryptographiquement sécurisée ?
- [ ] Usage unique ?

### Tokens
- [ ] Access token courte durée (1h max) ?
- [ ] Refresh token rotation ?
- [ ] Authorization code usage unique ?
- [ ] Validation signatures ?

### Scopes
- [ ] Scopes minimums demandés ?
- [ ] User consent pour scopes sensibles ?
- [ ] Validation scopes serveur ?

## Erreurs Courantes

### ❌ Pas de State Parameter
CSRF possible sur callback

### ❌ Redirect URI Wildcard
Open redirect, code interception

### ❌ Implicit Flow
Tokens exposés dans URL

### ❌ Pas de PKCE
Code interception (public clients)

### ❌ Long-Lived Access Tokens
Fenêtre exploitation large

### ❌ Client Secret Exposé
Compromission totale

### ❌ Pas de Refresh Token Rotation
Refresh token volé utilisable longtemps

## Références

- **RFC 6749** : OAuth 2.0 Framework
- **RFC 7636** : PKCE
- **OpenID Connect** : Specification
- **OAuth 2.0 Security Best Practices**
- **OWASP** : OAuth Cheat Sheet
