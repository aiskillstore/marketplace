# Logging Sécurité

## Définition

Enregistrement des événements de sécurité pour détection, investigation, forensics, et compliance.

## Sévérité

🟠 **HAUTE** - Détection incidents, forensics, compliance

## Événements à Logger

### Authentification

```
✅ Login succès (user, timestamp, IP, device)
✅ Login échec (user/email, reason, IP)
✅ Logout
✅ Password change/reset
✅ MFA succès/échec
✅ Account lockout
✅ Session expiration
```

### Autorisation

```
✅ Access denied (403)
✅ Privilege escalation tentative
✅ Accès ressources sensibles
✅ Changements permissions/rôles
```

### Modifications Données

```
✅ Création/modification/suppression données sensibles
✅ Changements configuration sécurité
✅ Changements paramètres système
✅ Bulk operations
```

### Admin Actions

```
✅ User creation/deletion
✅ Role assignments
✅ Configuration changes
✅ Database modifications
✅ Code deployments
```

### Sécurité

```
✅ Failed validation attempts
✅ Injection attempts détectés
✅ Rate limit exceeded
✅ Anomalies détectées
✅ Antivirus alerts
✅ Firewall blocks
```

### Erreurs Application

```
✅ Exceptions non catchées
✅ Erreurs critiques
✅ Crashes
✅ Timeouts
```

## Format Logs

### Informations Essentielles

```
Chaque log doit contenir :
- Timestamp (UTC, ISO 8601)
- Event type/category
- Severity level
- User ID (si authentifié)
- IP address
- Request ID (correlation)
- Action performed
- Resource accessed
- Result (success/failure)
- User agent
- Session ID
```

### Format Structuré

**JSON (Recommandé)**
```
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "WARN",
  "event": "auth.login.failed",
  "user": {"id": "123", "email": "user@example.com"},
  "ip": "203.0.113.45",
  "request_id": "abc-123",
  "reason": "invalid_password",
  "attempt": 3,
  "user_agent": "Mozilla/5.0..."
}
```

**Avantages JSON**
- Parseable
- Searchable
- Structured queries
- Intégration SIEM facile

## Niveaux de Sévérité

```
TRACE : Détails debugging
DEBUG : Informations développement
INFO : Événements normaux importants
WARN : Événements anormaux non critiques
ERROR : Erreurs nécessitant attention
FATAL/CRITICAL : Erreurs critiques système
```

## Données Sensibles

### ❌ NE JAMAIS LOGGER

```
- Passwords (hashed ou clair)
- Tokens d'authentification complets
- API keys, secrets
- Credit card numbers complets
- SSN, données santé
- Private keys
- Session tokens complets
- Security answers
```

### ✅ Logging Sécurisé

**Masking**
```
Email : u***r@example.com
Phone : ***-***-1234
Card : **** **** **** 1234
Token : abc...xyz (premiers/derniers chars uniquement)
```

**Hashing**
```
User identifiers : Hash si nécessaire
Pas de données permettant identification directe
```

## Centralisation

### Log Aggregation

```
✅ Système centralisé (ELK, Splunk, Datadog)
✅ Tous serveurs/services envoient logs
✅ Corrélation events multi-services
✅ Recherche globale
```

### Avantages

```
- Vue globale
- Corrélation événements
- Détection patterns
- Alerting centralisé
- Backup centralisé
- Performance (pas I/O local)
```

## Retention

### Durées Recommandées

```
Logs sécurité : 1-2 ans minimum
Logs audit : Selon compliance (7 ans parfois)
Logs debug : 7-30 jours
Logs access : 90 jours minimum
```

### Archivage

```
✅ Compression logs anciens
✅ Stockage cold storage
✅ Chiffrement archives
✅ Suppression automatique après rétention
```

## Protection Logs

### Accès Restreint

```
✅ Read-only pour application
✅ Write via log service
✅ Admin access seulement pour consultation
✅ RBAC strict
✅ Logs accès aux logs (meta-logging)
```

### Intégrité

```
✅ Write-once storage si possible
✅ Hashing logs (tampering detection)
✅ Signatures cryptographiques
✅ WORM (Write Once Read Many) storage
```

### Chiffrement

```
✅ Chiffrement en transit (TLS)
✅ Chiffrement au repos
✅ Clés séparées application
```

## Monitoring & Alerting

### Alertes Automatiques

```
Déclencher alerte si :
- X échecs auth en Y minutes (même IP/user)
- Accès denied répétés
- Pattern injection détecté
- Anomalie comportement user
- Erreurs critiques
- Accès admin hors heures
- Géolocalisation impossible
```

### Dashboards

```
✅ Vue temps réel
✅ Métriques clés (login rate, errors, etc.)
✅ Trends
✅ Anomalies visualisées
```

## Correlation & Analysis

### Request Tracing

```
✅ Request ID unique
✅ Propagé à travers microservices
✅ Permet reconstruction flow complet
```

### Pattern Detection

```
✅ Brute force tentatives
✅ Account enumeration
✅ Distributed attacks
✅ Time-based patterns
```

### Forensics

```
Lors d'incident :
✅ Timeline événements
✅ Reconstruction actions attacker
✅ Identification compromission
✅ Evidence collection
```

## Compliance

### Exigences Légales

```
PCI-DSS : Logs accès données cartes
HIPAA : Logs accès données santé
GDPR : Logs traitement données personnelles
SOX : Logs financiers
```

### Audit Trail

```
✅ Qui a fait quoi et quand
✅ Non-répudiation
✅ Immutable logs
✅ Complet et chronologique
```

## Performance

### Asynchronous Logging

```
✅ Logging non-blocking
✅ Queue messages
✅ Background workers
❌ Pas de I/O synchrone dans request path
```

### Sampling

```
Si volume très élevé :
✅ Log 100% événements sécurité
⚠️ Sample logs debug/trace
✅ Augmenter sampling si incident
```

### Structured Logging

```
✅ JSON/structured > plain text
✅ Indexation efficace
✅ Requêtes rapides
```

## Checklist d'Audit

### Événements
- [ ] Authentification loggée (succès/échec) ?
- [ ] Autorisation denials loggées ?
- [ ] Modifications données sensibles loggées ?
- [ ] Admin actions loggées ?
- [ ] Anomalies détectées loggées ?

### Format
- [ ] Timestamp présent ?
- [ ] User ID présent ?
- [ ] IP address présente ?
- [ ] Request ID pour corrélation ?
- [ ] Format structuré (JSON) ?

### Données Sensibles
- [ ] Pas de passwords ?
- [ ] Pas de tokens complets ?
- [ ] Pas de PII non masquée ?
- [ ] Masking appliqué ?

### Infrastructure
- [ ] Logs centralisés ?
- [ ] Rétention appropriée ?
- [ ] Logs protégés (accès restreint) ?
- [ ] Logs chiffrés ?
- [ ] Intégrité vérifiable ?

### Monitoring
- [ ] Alertes configurées ?
- [ ] Dashboard temps réel ?
- [ ] Pattern detection ?
- [ ] Correlation multi-services ?

### Compliance
- [ ] Exigences légales respectées ?
- [ ] Audit trail complet ?
- [ ] Logs immutables ?

## Erreurs Courantes

### ❌ Logging Passwords
Même hashés, sensible

### ❌ Pas de Logs Échecs Auth
Impossible détecter brute force

### ❌ Logs Locaux Uniquement
Perte si serveur compromis

### ❌ Pas de Protection Logs
Attacker peut supprimer traces

### ❌ Trop de Détails
PII dans logs

### ❌ Pas Assez de Contexte
Impossible forensics

## Références

- **OWASP** : Logging Cheat Sheet
- **NIST SP 800-92** : Guide to Computer Security Log Management
- **CWE-778** : Insufficient Logging
