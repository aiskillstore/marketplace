# Cross-Site Request Forgery (CSRF)

## Définition

Attaque forçant un utilisateur authentifié à exécuter des actions non désirées sur une application web à son insu.

## Sévérité

🟡 **MOYENNE** - Actions non autorisées au nom de l'utilisateur

## Principe de l'Attaque

```
1. Victime connectée sur site-vulnerable.com
2. Victime visite site-malicieux.com
3. Site malicieux déclenche requête vers site-vulnerable.com
4. Navigateur envoie automatiquement les cookies de session
5. Action exécutée au nom de la victime
```

## Types d'Attaques CSRF

### 1. CSRF via GET
Requête GET déclenchée via image, iframe, etc.

### 2. CSRF via POST
Formulaire auto-submit sur site malicieux

### 3. CSRF via JSON
API REST avec cookies sans protection CSRF

### 4. CSRF Login
Force la connexion de la victime avec compte attacker

## Vecteurs d'Attaque

### GET Request
```
<!-- Sur site malicieux -->
<img src="https://bank.com/transfer?to=attacker&amount=1000">
<iframe src="https://bank.com/delete-account">
<script src="https://api.site.com/delete-user"></script>
```

### POST Request
```
<!-- Formulaire auto-submit -->
<form action="https://site.com/transfer" method="POST">
  <input name="to" value="attacker">
  <input name="amount" value="1000">
</form>
<script>document.forms[0].submit()</script>
```

### AJAX Request
```
fetch('https://api.site.com/delete', {
  method: 'POST',
  credentials: 'include'  // Envoie les cookies
})
```

## Endpoints Vulnérables

### À Risque
- Actions de modification (POST, PUT, DELETE, PATCH)
- Transferts d'argent
- Changement de mot de passe/email
- Suppression de compte
- Mise à jour de paramètres
- Ajout/suppression de permissions

### Patterns Vulnérables

```
Rechercher routes sans protection CSRF :
- Routes POST/PUT/DELETE/PATCH
- Pas de vérification de token
- Pas de vérification origin/referer
- Authentication par cookies uniquement
```

## Localisation dans le Code

### À Chercher

#### Routes de Modification
- POST, PUT, DELETE, PATCH sans protection
- Actions sensibles (paiement, suppression)
- Changements de configuration

#### Authentication
- Cookies sans SameSite
- Pas de tokens CSRF
- Pas de vérification Origin/Referer

#### APIs REST
- Endpoints avec credentials: 'include'
- CORS mal configuré (Access-Control-Allow-Credentials)

### Patterns à Grep

```
Routes potentiellement vulnérables :
- "router\.post\(.*req\.session"
- "router\.delete\(.*req\.session"
- "router\.put\(.*req\.session"
- "@PostMapping"
- "@DeleteMapping"
- "[HttpPost]"
- "credentials.*include"
```

## Impact

### Actions Non Autorisées
- Transfert d'argent
- Changement d'email/password
- Suppression de compte
- Modifications de données

### Élévation de Privilèges
- Ajout d'admin
- Changement de permissions

### Vol de Compte
- CSRF login + XSS = takeover

## Remédiation

### 1. CSRF Tokens (Synchronizer Token)

**Principe**
- Token unique par session/requête
- Token dans form hidden field ou header
- Validation côté serveur

**Implémentation**
```
✅ CORRECT :
// Génération (server)
const csrfToken = generateSecureRandom()
session.csrfToken = csrfToken

// HTML form
<input type="hidden" name="_csrf" value="${csrfToken}">

// Validation (server)
if (req.body._csrf !== req.session.csrfToken)
  throw new Error('Invalid CSRF token')
```

**Pour APIs**
```
✅ CORRECT :
// Header custom
X-CSRF-Token: token-value

// Validation
if (req.headers['x-csrf-token'] !== session.csrfToken)
  return 403
```

### 2. SameSite Cookie Attribute

**Configuration**
```
✅ CORRECT :
Set-Cookie: sessionid=...; SameSite=Lax; Secure; HttpOnly

Ou pour protection stricte :
Set-Cookie: sessionid=...; SameSite=Strict; Secure; HttpOnly
```

**Valeurs**
- **Strict** : Cookie jamais envoyé depuis autre site (recommandé)
- **Lax** : Cookie envoyé sur navigation GET (par défaut moderne)
- **None** : Cookie toujours envoyé (nécessite Secure)

**Attention**
- Support navigateur (vérifier compatibilité)
- SameSite=Lax par défaut sur navigateurs modernes

### 3. Double Submit Cookie

**Principe**
- Token dans cookie ET dans paramètre/header
- Validation que les deux matchent
- Pas besoin de state serveur

**Implémentation**
```
✅ CORRECT :
// Cookie
Set-Cookie: csrf-token=random-value; SameSite=Strict

// Header ou form
X-CSRF-Token: random-value

// Validation
if (req.cookies['csrf-token'] !== req.headers['x-csrf-token'])
  return 403
```

### 4. Origin/Referer Verification

**Headers à Vérifier**
```
✅ CORRECT :
const origin = req.headers['origin'] || req.headers['referer']
if (!origin || !isSameSite(origin, req.hostname))
  return 403
```

**Attention**
- Headers peuvent être absents (privacy)
- Ne pas utiliser seul
- Defense in depth avec autres protections

### 5. Custom Headers

**Principe**
- Header custom obligatoire (ex: X-Requested-With)
- CORS empêche ajout de headers custom cross-origin

**Implémentation**
```
✅ CORRECT :
// Client (AJAX)
headers: { 'X-Requested-With': 'XMLHttpRequest' }

// Server
if (!req.headers['x-requested-with'])
  return 403
```

### 6. Re-authentication pour Actions Sensibles

**Actions Critiques**
- Demander mot de passe
- Confirmation explicite
- MFA

```
✅ CORRECT :
// Avant transfert important
if (!verifyPassword(req.body.password))
  return 401
```

### 7. GET Requests Safe

**Principe**
- GET ne modifie jamais de données
- Idempotent et safe
- POST/PUT/DELETE pour modifications

```
❌ BAD :
GET /delete-account

✅ GOOD :
DELETE /account
```

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Routes POST/PUT/DELETE sans CSRF protection ?
- [ ] Cookies sans SameSite attribute ?
- [ ] Pas de tokens CSRF ?
- [ ] Pas de vérification Origin/Referer ?
- [ ] Actions sensibles sans re-authentication ?
- [ ] GET requests modifient des données ?

### Validation des Correctifs
- [ ] CSRF tokens implémentés ?
- [ ] SameSite=Lax ou Strict sur cookies ?
- [ ] Validation des tokens côté serveur ?
- [ ] Origin/Referer vérifiés ?
- [ ] Re-authentication pour actions critiques ?
- [ ] GET requests idempotents ?

### Tests de Vulnérabilité
- [ ] Créer page HTML avec form auto-submit ?
- [ ] Tester sans token CSRF ?
- [ ] Tester avec token invalide ?
- [ ] Tester cross-origin request ?

## Protection par Framework

### Express.js
```
✅ CORRECT :
const csrf = require('csurf')
app.use(csrf({ cookie: true }))
```

### Django
```
✅ CORRECT :
# Middleware activé par défaut
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
]

# Template
{% csrf_token %}
```

### Spring
```
✅ CORRECT :
// CSRF activé par défaut
http.csrf().csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
```

### ASP.NET
```
✅ CORRECT :
// Form
@Html.AntiForgeryToken()

// Controller
[ValidateAntiForgeryToken]
```

## Cas Particuliers

### APIs Stateless
- JWT dans Authorization header : pas vulnérable CSRF
- Pas de cookies : pas vulnérable CSRF

### SPA (Single Page Apps)
- CSRF tokens dans headers
- Double submit cookie pattern

### Mobile Apps
- API token authentication : pas vulnérable

## Références

- **OWASP** : Cross-Site Request Forgery (CSRF)
- **CWE-352** : Cross-Site Request Forgery
- **OWASP CSRF Prevention Cheat Sheet**
