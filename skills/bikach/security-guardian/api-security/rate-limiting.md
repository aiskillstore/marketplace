# Rate Limiting

## Définition

Limitation du nombre de requêtes qu'un client peut effectuer dans une période de temps donnée.

## Sévérité

🟡 **MOYENNE** - DoS, brute force, abus de ressources

## Objectifs

- **Protection DoS** : Empêcher surcharge serveur
- **Prévention Brute Force** : Limiter tentatives authentification
- **Fair Usage** : Partage équitable ressources
- **Protection Coûts** : Limiter abus APIs payantes

## Stratégies

### Par IP

```
Limite : 100 requêtes / minute par IP
Usage : Protection générale
Bypass : VPN, proxies, botnet
```

### Par User/Account

```
Limite : 1000 requêtes / heure par compte
Usage : APIs authentifiées
Plus précis qu'IP
```

### Par API Key

```
Limite : Variable selon plan (free/premium)
Usage : APIs publiques avec keys
Tiers pricing
```

### Par Endpoint

```
Limites différentes selon endpoint :
- /auth/login : 5/min
- /api/search : 100/min
- /api/data : 1000/min
```

### Global

```
Limite totale serveur
Protection infrastructure
Indépendant des clients
```

## Algorithmes

### Fixed Window

```
Compteur reset à intervalles fixes
Simple mais burst possible en début fenêtre

Exemple :
0:00-0:59 : 100 requêtes max
1:00-1:59 : 100 requêtes max (reset)
```

### Sliding Window

```
Fenêtre glissante
Plus lisse que fixed window
Calcul sur dernières N secondes
```

### Token Bucket

```
Bucket avec tokens
Requête consomme 1 token
Tokens régénérés au fil du temps
Permet bursts contrôlés
```

### Leaky Bucket

```
Queue FIFO avec rate fixe
Requêtes traitées à vitesse constante
Lisse les pics
```

## Implémentation

### Headers Response

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000

Ou standard :
RateLimit-Limit: 100
RateLimit-Remaining: 45
RateLimit-Reset: 1640000000
```

### Status Code

```
429 Too Many Requests

Retry-After: 60 (secondes)
```

### Response Body

```
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "remaining": 0,
  "reset": 1640000000,
  "retry_after": 60
}
```

## Configuration

### Seuils Recommandés

**Authentification**
```
Login : 5-10 / 5 minutes
Password reset : 3 / heure
MFA : 5 / 5 minutes
```

**APIs Publiques**
```
Non-auth : 50-100 / heure
Auth : 1000-5000 / heure
Premium : Illimité ou élevé
```

**Search/Query**
```
20-50 / minute
Coûteux en ressources
```

**Write Operations**
```
Plus strict que read
10-20 / minute
```

### Exemptions

```
Whitelist IPs :
- Monitoring
- Partenaires
- Internal services

Whitelist Users :
- Admins (avec limite haute)
- Premium accounts
```

## Storage

### Redis (Recommandé)

```
Avantages :
- Atomic operations (INCR)
- TTL automatique
- Performance
- Distributed
```

### In-Memory

```
Avantages :
- Rapide
- Simple

Inconvénients :
- Pas de partage entre instances
- Perdu au restart
```

### Database

```
Moins performant
Persistence
Pour analytics long terme
```

## Bypass & Mitigation

### Techniques Bypass

```
- Rotation IPs (VPN, proxies)
- Botnet distribué
- API key compromisées
```

### Protections

```
✅ Combiner IP + User + API key
✅ CAPTCHA après X échecs
✅ Progressive delays
✅ Monitoring patterns suspects
✅ Geo-blocking si nécessaire
```

## Monitoring

### Métriques

```
- Taux de 429 errors
- IPs/Users bloqués
- Patterns temporels
- Endpoints plus touchés
```

### Alertes

```
- Spike 429 errors
- Même IP bloquée répétitivement
- Pattern attaque détecté
```

## User Experience

### Communication

```
✅ Headers clairs (remaining, reset)
✅ Messages explicites
✅ Documentation limites
✅ Retry-After header
```

### Graceful Degradation

```
Au lieu de bloquer total :
- Ralentir réponses
- Queue requests
- Proposer upgrade plan
```

## Checklist d'Audit

### Configuration
- [ ] Rate limiting activé ?
- [ ] Limites appropriées par endpoint ?
- [ ] Limites authentification strictes (5-10/5min) ?
- [ ] Algorithme adapté (token bucket, sliding) ?

### Implémentation
- [ ] Storage performant (Redis) ?
- [ ] Headers informatifs ?
- [ ] Status 429 correct ?
- [ ] Retry-After header ?

### Protection
- [ ] Combinaison IP + User ?
- [ ] CAPTCHA après échecs ?
- [ ] Whitelist pour services internes ?
- [ ] Monitoring alertes ?

### UX
- [ ] Documentation limites publique ?
- [ ] Messages clairs ?
- [ ] Upgrade path pour users légitimes ?

## Erreurs Courantes

### ❌ Limites Trop Élevées
Pas de protection réelle

### ❌ IP Seule
Facilement bypassé

### ❌ Pas de Headers Informatifs
User ne sait pas quand réessayer

### ❌ Même Limite Partout
Endpoints sensibles pas protégés

### ❌ Pas de Whitelist
Services internes bloqués

## Références

- **IETF Draft** : RateLimit Headers
- **OWASP** : Denial of Service Cheat Sheet
- **RFC 6585** : Additional HTTP Status Codes (429)
