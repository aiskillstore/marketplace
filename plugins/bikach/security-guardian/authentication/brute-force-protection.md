# Protection Brute Force

## Définition

Tentatives répétées de deviner mot de passe, code, ou credentials via essais multiples.

## Sévérité

🟠 **HAUTE** - Account takeover via énumération

## Types d'Attaques

### 1. Credential Stuffing
Utilisation de breaches connues (username:password pairs)

### 2. Dictionary Attack
Test passwords courants et variations

### 3. Brute Force Classique
Énumération exhaustive

### 4. Reverse Brute Force
Un password, multiples usernames

## Mesures de Protection

### 1. Rate Limiting

**Par IP**
```
5-10 tentatives / minute
Blocage temporaire après dépassement
```

**Par Compte**
```
5 tentatives / 5 minutes
Verrouillage progressif
```

**Global**
```
Protection DoS
Limite totale requêtes auth
```

### 2. Account Lockout

**Lockout Temporaire**
```
Après X échecs (5-10) :
- Verrouillage 15-30 minutes
- OU CAPTCHA obligatoire
- Notification email
```

**Progressive Delays**
```
Échec 1 : Immédiat
Échec 2 : 1 seconde
Échec 3 : 2 secondes
Échec 4 : 4 secondes
Échec 5+ : 8+ secondes (exponentiel)
```

### 3. CAPTCHA

**Déclenchement**
```
Après 3-5 échecs
Avant lockout permanent
Pour requêtes suspectes
```

**Types**
- reCAPTCHA v3 (invisible, score)
- hCaptcha
- Turnstile (Cloudflare)

### 4. Login Honeypots

**Détection Bots**
```
Champs cachés (CSS)
Si remplis → Bot détecté
Blocage automatique
```

### 5. Device Fingerprinting

**Tracking**
- Browser fingerprint
- IP + User-Agent
- Patterns comportementaux
- Détection devices suspects

### 6. Geo-blocking

**Restrictions**
```
Blocage pays suspects
Alertes connexions inhabituelles
Whitelist/blacklist IPs
```

## Monitoring et Alertes

### Logs à Surveiller

```
- Échecs login répétés
- Même IP / multiples comptes
- Patterns horaires suspects
- Multiples IPs / même compte
- Succès après nombreux échecs
```

### Alertes Automatiques

```
Déclencher si :
- X échecs / minute
- Scan comptes détecté
- Pattern brute force
- Succès depuis IP suspecte
```

## Notifications Utilisateur

### Alertes

```
Email après :
- X échecs consécutifs
- Lockout compte
- Login depuis nouveau device
- Changement mot de passe
```

### Informations

```
- Timestamp tentative
- IP source
- Géolocalisation
- Device/browser
- Lien sécuriser compte
```

## Checklist d'Audit

### Rate Limiting
- [ ] Par IP implémenté ?
- [ ] Par compte implémenté ?
- [ ] Seuils appropriés (5-10) ?
- [ ] Global rate limit ?

### Lockout
- [ ] Lockout temporaire configuré ?
- [ ] Durée raisonnable (15-30 min) ?
- [ ] Progressive delays ?
- [ ] Évite DoS utilisateur ?

### CAPTCHA
- [ ] Après X échecs ?
- [ ] Type moderne (reCAPTCHA v3) ?
- [ ] Pas trop agressif (UX) ?

### Monitoring
- [ ] Logs échecs auth ?
- [ ] Alertes automatiques ?
- [ ] Dashboard patterns ?
- [ ] Notifications utilisateur ?

### Protection Additionnelle
- [ ] MFA disponible ?
- [ ] Device fingerprinting ?
- [ ] Honeypots ?
- [ ] Geo-restrictions si nécessaire ?

## Erreurs Courantes

### ❌ Pas de Rate Limiting
Énumération illimitée

### ❌ Lockout Permanent
DoS utilisateur légitime

### ❌ Lockout Trop Court
Brute force continue

### ❌ Pas de CAPTCHA
Bots automatisés

### ❌ Pas de Notification
User ignore compromission

### ❌ Rate Limit Trop Élevé
Pas de protection réelle

## Références

- **OWASP** : Blocking Brute Force Attacks
- **CWE-307** : Improper Restriction of Excessive Authentication Attempts
