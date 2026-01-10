# Configuration CORS

## Définition

Cross-Origin Resource Sharing : mécanisme permettant à des ressources web d'être accédées depuis un domaine différent.

## Sévérité

🟡 **MOYENNE** - Accès non autorisé, fuite données

## Principe

```
Same-Origin Policy par défaut :
- Même protocol, domaine, port
- Bloque requêtes cross-origin

CORS relaxe cette politique de manière contrôlée
```

## Headers CORS

### Access-Control-Allow-Origin

```
Domaines autorisés à accéder

✅ Spécifique :
Access-Control-Allow-Origin: https://app.example.com

❌ Wildcard (dangereux) :
Access-Control-Allow-Origin: *

⚠️ Wildcard acceptable :
- APIs publiques non-authentifiées
- Pas de credentials
```

### Access-Control-Allow-Credentials

```
Permettre cookies/auth headers

Access-Control-Allow-Credentials: true

⚠️ Si true :
- Origin ne peut PAS être *
- Doit être domaine spécifique
```

### Access-Control-Allow-Methods

```
Méthodes HTTP autorisées

Access-Control-Allow-Methods: GET, POST, PUT, DELETE

✅ Limiter aux nécessaires
❌ Pas de wildcard
```

### Access-Control-Allow-Headers

```
Headers custom autorisés

Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key

✅ Whitelist stricte
❌ Pas de *
```

### Access-Control-Max-Age

```
Durée cache preflight

Access-Control-Max-Age: 3600

Évite preflight répétés
```

## Preflight Requests

### OPTIONS Request

```
Requête automatique browser avant requête réelle :

OPTIONS /api/resource
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type

Response :
200 OK
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: Content-Type
```

### Déclencheurs Preflight

```
Preflight si :
- Méthodes : PUT, DELETE, PATCH
- Headers custom
- Content-Type : application/json, etc.

Pas de preflight :
- GET, HEAD, POST simple
- Headers standards uniquement
- Content-Type : application/x-www-form-urlencoded, etc.
```

## Configuration Sécurisée

### Whitelist Origins

```
✅ Liste statique domaines autorisés

allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com'
]

Si request origin in allowedOrigins :
  Access-Control-Allow-Origin: <origin>
  Access-Control-Allow-Credentials: true
```

### Dynamic Origin Validation

```
✅ Validation pattern

if (origin matches /^https:\/\/.*\.example\.com$/) {
  return origin
}

⚠️ Attention regex injection
⚠️ Validation stricte
```

### Credentials

```
Si authentication nécessaire :
✅ Access-Control-Allow-Credentials: true
✅ Origin spécifique (pas *)
✅ Cookie SameSite=None; Secure
```

## Vulnérabilités CORS

### Wildcard avec Credentials

```
❌ DANGEREUX :
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

→ Tous sites peuvent lire réponse authentifiée
```

### Origin Reflection

```
❌ DANGEREUX :
Origin: https://evil.com
Response:
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true

→ Accepte tous origins sans validation
```

### Null Origin

```
❌ DANGEREUX :
Access-Control-Allow-Origin: null

→ Exploitable via iframe sandbox
```

### Regex Bypass

```
❌ DANGEREUX :
Pattern : /example\.com$/
Evil : evil.com.example.com.attacker.com

→ Validation regex trop permissive
```

### Subdomain Wildcard

```
⚠️ RISQUE :
Access-Control-Allow-Origin: *.example.com

→ Si un subdomain compromis, tous compromis
```

## Cas d'Usage

### API Publique Non-Auth

```
✅ Acceptable :
Access-Control-Allow-Origin: *

Pas de credentials
Données publiques
```

### API Authentifiée

```
✅ Obligatoire :
Whitelist origins spécifiques
Access-Control-Allow-Credentials: true
Validation stricte
```

### SPA (Single Page App)

```
✅ Configuration :
Origin : https://app.example.com
Credentials : true
Methods : GET, POST, PUT, DELETE
Headers : Content-Type, Authorization
```

### Mobile App

```
⚠️ Apps natives n'ont pas Same-Origin Policy
⚠️ CORS non applicable
✅ Authentication via tokens
```

## Checklist d'Audit

### Configuration
- [ ] Origins whitelist stricte ?
- [ ] Pas de wildcard * avec credentials ?
- [ ] Pas de origin reflection sans validation ?
- [ ] Pas de null origin accepté ?
- [ ] Méthodes limitées au nécessaire ?
- [ ] Headers limitées au nécessaire ?

### Credentials
- [ ] Credentials true seulement si nécessaire ?
- [ ] Origin spécifique (pas *) si credentials ?
- [ ] SameSite=None; Secure sur cookies ?

### Validation
- [ ] Validation origin stricte ?
- [ ] Pas de regex permissive ?
- [ ] Whitelist statique ou validation forte ?
- [ ] Logs accès cross-origin ?

## Tests

```
✅ Tester avec origin non autorisé
✅ Tester avec origin null
✅ Tester preflight requests
✅ Tester avec credentials
✅ Tester bypass regex si dynamic
```

## Erreurs Courantes

### ❌ Access-Control-Allow-Origin: *
Avec credentials ou données sensibles

### ❌ Origin Reflection
Accepter tous origins

### ❌ Null Origin
Accepté (exploitable)

### ❌ Validation Regex Faible
Bypass facile

### ❌ Subdomain Wildcard
Risque si subdomain compromis

## Références

- **MDN** : CORS
- **W3C** : CORS Specification
- **OWASP** : CORS Cheat Sheet
- **PortSwigger** : CORS Vulnerabilities
