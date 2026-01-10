# Server-Side Request Forgery (SSRF)

## Définition

Exploitation permettant à l'attaquant de forcer le serveur à effectuer des requêtes HTTP vers des destinations arbitraires (internes ou externes).

## Sévérité

🔴 **CRITIQUE** - Accès services internes, cloud metadata, scan de ports

## Principe de l'Attaque

```
1. Application fait des requêtes HTTP basées sur input utilisateur
2. Attaquant fournit URL vers service interne
3. Serveur fait la requête (accès depuis l'intérieur)
4. Contournement des firewalls et ACLs
```

## Types de SSRF

### 1. Basic SSRF
URL complète fournie par l'utilisateur

### 2. Blind SSRF
Pas de réponse visible, détection via timing ou out-of-band

### 3. Partial SSRF
Seule partie de l'URL contrôlée (host, path, query)

### 4. SSRF via Redirect
Chain de redirections pour contourner protections

## Vecteurs d'Attaque

### Accès Services Internes
```
http://localhost:8080/admin
http://192.168.1.5/secret
http://internal-api:3000/users
```

### Cloud Metadata
```
AWS :
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/user-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

Azure :
http://169.254.169.254/metadata/instance?api-version=2021-02-01

GCP :
http://metadata.google.internal/computeMetadata/v1/
```

### Port Scanning
```
http://internal-host:22
http://internal-host:3306
http://internal-host:6379
→ Timing differences révèlent ports ouverts
```

### File Protocol
```
file:///etc/passwd
file:///c:/windows/win.ini
```

### Other Protocols
```
gopher://internal-host:6379/_SET key value
dict://internal-host:11211/stat
ftp://internal-ftp/file.txt
```

## Localisation dans le Code

### À Chercher

#### URL Fetching
- Webhooks
- URL preview/unfurling
- Image fetching (avatar, thumbnail)
- PDF generation from URL
- Document conversion
- XML external entities (XXE → SSRF)

#### Import Features
- Import from URL
- RSS/Atom feed readers
- Remote file inclusion
- API proxy/gateway

#### Integration Features
- OAuth callbacks
- Payment webhooks
- Third-party API calls
- Remote logging

### Patterns Vulnérables

```
Requêtes HTTP avec URL utilisateur :
- Fonctions de fetch/request avec paramètre utilisateur
- Download de fichiers depuis URL
- Webhooks avec URL configurable
- Proxy/forward de requêtes
- Import depuis URL externe
```

## Impact

### Accès Services Internes
- Admin panels
- Databases
- Redis, Memcached
- Elasticsearch
- Internal APIs

### Cloud Metadata Theft
- AWS credentials (IAM roles)
- Azure managed identity tokens
- GCP service account keys
- Environment variables

### Port Scanning
- Network reconnaissance
- Service discovery
- Topology mapping

### Data Exfiltration
- Lecture de fichiers locaux
- Dump de données internes
- Source code disclosure

### Attacks on Internal Services
- Redis exploitation
- Memcached exploitation
- Database access
- RCE sur services vulnérables

## Remédiation

### 1. Whitelist de Destinations (Recommandé)

**Principe**
- Liste fermée de domains/IPs autorisés
- Validation stricte avant requête
- Rejeter tout ce qui n'est pas whitelisté

**Domains Autorisés**
```
Whitelist :
- api.trusted.com
- images.cdn.com
- webhook.partner.com
```

**IP Whitelist**
```
Whitelist :
- 203.0.113.5
- 203.0.113.10
```

### 2. Blacklist (Defense in Depth)

**IPs Privées à Bloquer**
```
IPv4 Private :
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16
- 127.0.0.0/8
- 169.254.0.0/16 (Cloud metadata)
- localhost

IPv6 Private :
- ::1 (localhost)
- fc00::/7 (unique local)
- fe80::/10 (link-local)
```

**Protocols Autorisés**
```
Whitelist protocols :
- http
- https

Bloquer :
- file, gopher, dict, ftp
```

### 3. DNS Resolution puis Validation

**Process**
```
1. Parser l'URL
2. Résoudre le hostname en IP
3. Vérifier que l'IP n'est pas privée
4. Vérifier que l'IP n'est pas cloud metadata
5. Faire la requête vers l'IP validée
```

**Attention TOCTOU**
- Time-of-check Time-of-use
- DNS peut changer entre validation et requête
- Utiliser l'IP résolue directement pour la requête

### 4. Désactiver Redirects

**Principe**
- Ne pas suivre les redirections automatiquement
- Ou valider chaque URL de redirection

**Avantages**
- Empêche bypass via redirect
- Contrôle total sur les destinations

### 5. Network Segmentation

**Architecture**
- Application dans subnet séparé
- Firewall rules strictes
- Pas d'accès direct aux services internes
- Proxy pour requêtes externes

### 6. Response Validation

**Validations**
- Content-Type attendu
- Taille maximale de réponse
- Timeout configuré
- Pas de data sensible dans erreurs

### 7. Utiliser Services Dédiés

**Architecture**
- Service dédié pour HTTP fetching
- Sandboxé/isolé du reste
- Pas d'accès aux ressources internes
- Logs et monitoring

### 8. Authentication sur Services Internes

**Protection**
- Authentication même pour services internes
- Pas de confiance implicite network-based
- API keys, tokens
- Mutual TLS

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Requêtes HTTP avec URL utilisateur ?
- [ ] Pas de validation de destination ?
- [ ] Pas de restriction sur IP/domain ?
- [ ] Redirects suivis automatiquement ?
- [ ] Protocols non-HTTP autorisés (file, gopher) ?
- [ ] Webhooks sans validation ?
- [ ] Import/download depuis URL ?

### Validation des Correctifs
- [ ] Whitelist de domains/IPs implémentée ?
- [ ] Blacklist d'IPs privées en place ?
- [ ] DNS resolution + validation ?
- [ ] Redirects désactivés ou validés ?
- [ ] Protocols restreints (http/https uniquement) ?
- [ ] Network segmentation configurée ?
- [ ] Timeouts configurés ?

### Tests de Vulnérabilité
- [ ] Tester http://localhost ?
- [ ] Tester http://127.0.0.1 ?
- [ ] Tester http://169.254.169.254 (metadata) ?
- [ ] Tester http://192.168.x.x (interne) ?
- [ ] Tester file:// protocol ?
- [ ] Tester avec redirect vers localhost ?

## Bypass Techniques

### Alternative Representations IP
```
http://127.0.0.1
http://127.1
http://2130706433 (decimal)
http://0x7f.0x0.0x0.0x1 (hex)
http://[::1] (IPv6)
```

### DNS Tricks
```
http://localhost.localdomain
http://169.254.169.254.nip.io (wildcard DNS)
http://127.0.0.1.xip.io
```

### URL Encoding
```
http://127.0.0.%31
http://local%68ost
```

### DNS Rebinding
```
1. DNS pointe vers IP publique (validation passe)
2. Changer DNS rapidement vers IP privée
3. Requête effectuée vers IP privée
```

### Redirect Chains
```
1. URL publique autorisée
2. Redirect 302 vers localhost
3. SSRF via redirect si non validé
```

### Alternative Protocols
```
gopher:// (exploitation Redis, SMTP, etc.)
dict:// (port scanning)
ftp:// (si FTP wrapper activé)
file:// (local file access)
```

## IP Ranges à Bloquer

### IPv4 Private & Special
```
10.0.0.0/8           Private
172.16.0.0/12        Private
192.168.0.0/16       Private
127.0.0.0/8          Loopback
169.254.0.0/16       Link-local (metadata)
0.0.0.0/8            Current network
224.0.0.0/4          Multicast
240.0.0.0/4          Reserved
```

### IPv6 Special
```
::1/128              Loopback
fc00::/7             Unique local
fe80::/10            Link-local
ff00::/8             Multicast
```

### Cloud Metadata IPs
```
169.254.169.254      AWS, Azure, GCP
metadata.google.internal
169.254.169.123      Oracle Cloud
100.100.100.200      Alibaba Cloud
```

## Services Internes Couramment Ciblés

### Databases
```
PostgreSQL : 5432
MySQL : 3306
MongoDB : 27017
Redis : 6379
Elasticsearch : 9200
```

### Cache/Queue
```
Memcached : 11211
RabbitMQ : 5672, 15672
Kafka : 9092
```

### Admin/Management
```
Admin panels : 8080, 9000, 3000
Jenkins : 8080
Kubernetes API : 6443, 8001
Docker : 2375, 2376
```

## Détection et Monitoring

### Logs à Surveiller
- Requêtes vers IPs privées
- Requêtes vers cloud metadata
- Tentatives de protocols non-standard
- Multiples requêtes de scan de ports

### Alertes
- Accès à 169.254.169.254
- Accès à localhost depuis l'application
- Scan de ports détecté (timing patterns)
- Protocols non-HTTP utilisés

## Références

- **OWASP** : Server-Side Request Forgery (SSRF)
- **CWE-918** : Server-Side Request Forgery
- **PortSwigger** : SSRF
- **HackerOne** : SSRF Reports
