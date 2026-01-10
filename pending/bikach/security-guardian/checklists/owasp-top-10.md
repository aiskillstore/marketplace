# OWASP Top 10 Checklist

## OWASP Top 10 2021

### A01:2021 - Broken Access Control

- [ ] Autorisation vérifiée côté serveur sur toutes requêtes ?
- [ ] Pas de bypass possible via manipulation paramètres ?
- [ ] IDOR (Insecure Direct Object Reference) vérifié ?
- [ ] CORS configuré correctement ?
- [ ] Metadata endpoints protégés (cloud) ?
- [ ] Principe least privilege appliqué ?

### A02:2021 - Cryptographic Failures

- [ ] Données sensibles chiffrées au repos ?
- [ ] Données sensibles chiffrées en transit (TLS) ?
- [ ] Algorithmes cryptographiques modernes (AES-GCM, RSA-2048+) ?
- [ ] Pas d'algorithmes faibles (MD5, SHA1, DES) ?
- [ ] Clés gérées de manière sécurisée (KMS, Vault) ?
- [ ] Pas de clés hardcodées ?
- [ ] TLS 1.2+ uniquement ?
- [ ] Certificats valides et à jour ?

### A03:2021 - Injection

- [ ] **SQL Injection** : Prepared statements/parameterized queries ?
- [ ] **NoSQL Injection** : Validation type et sanitization ?
- [ ] **Command Injection** : Pas d'exec() avec user input ?
- [ ] **LDAP Injection** : Input échappé ?
- [ ] **XPath Injection** : Requêtes paramétrées ?
- [ ] Input validation sur toutes entrées ?
- [ ] Output encoding approprié ?

### A04:2021 - Insecure Design

- [ ] Threat modeling effectué ?
- [ ] Security requirements définis ?
- [ ] Architecture sécurisée (defense in depth) ?
- [ ] Rate limiting sur endpoints sensibles ?
- [ ] Principe least privilege dans design ?
- [ ] Séparation des environnements (dev/staging/prod) ?
- [ ] Flow sécurisés pour fonctionnalités critiques ?

### A05:2021 - Security Misconfiguration

- [ ] Hardening serveurs/containers ?
- [ ] Frameworks/libraries à jour ?
- [ ] Features inutilisées désactivées ?
- [ ] Configurations par défaut changées ?
- [ ] Error messages ne révèlent pas d'infos sensibles ?
- [ ] Security headers configurés (CSP, HSTS, X-Frame-Options) ?
- [ ] CORS configuré strictement ?
- [ ] Pas de secrets dans config versionnée ?

### A06:2021 - Vulnerable and Outdated Components

- [ ] Inventaire dépendances maintenu ?
- [ ] Scan vulnérabilités automatique (Dependabot, Snyk) ?
- [ ] Dépendances mises à jour régulièrement ?
- [ ] Sources dépendances fiables (registries officiels) ?
- [ ] Pas de composants non maintenus ?
- [ ] Monitoring CVEs pour dépendances critiques ?

### A07:2021 - Identification and Authentication Failures

- [ ] **Passwords** : Hashing fort (Argon2id, bcrypt) ?
- [ ] **MFA** : Disponible et encouragé ?
- [ ] **Session** : IDs cryptographiquement sécurisés ?
- [ ] **Session** : HttpOnly, Secure, SameSite cookies ?
- [ ] **Session** : Expiration appropriée ?
- [ ] Rate limiting sur authentification ?
- [ ] Protection brute force (lockout, CAPTCHA) ?
- [ ] Pas d'enumeration users possible ?
- [ ] Password reset sécurisé (tokens uniques) ?

### A08:2021 - Software and Data Integrity Failures

- [ ] Signatures vérifiées (packages, updates) ?
- [ ] CI/CD pipeline sécurisé ?
- [ ] Pas d'auto-update non vérifié ?
- [ ] Intégrité artifacts build vérifiée ?
- [ ] Deserialization sécurisée (whitelist classes) ?
- [ ] Pas de données non fiables déserialisées ?

### A09:2021 - Security Logging and Monitoring Failures

- [ ] Logs événements sécurité (login, échecs auth, accès données) ?
- [ ] Logs suffisamment détaillés pour forensics ?
- [ ] Pas de données sensibles dans logs ?
- [ ] Monitoring actif avec alertes ?
- [ ] Logs centralisés et protégés ?
- [ ] Retention logs appropriée ?
- [ ] Incident response plan en place ?

### A10:2021 - Server-Side Request Forgery (SSRF)

- [ ] URLs utilisateur validées ?
- [ ] Whitelist domains/IPs autorisés ?
- [ ] Blacklist IPs privées (10.x, 192.168.x, 127.x) ?
- [ ] Cloud metadata IPs bloqués (169.254.169.254) ?
- [ ] Protocols restreints (http/https uniquement) ?
- [ ] Pas de redirects automatiques ?
- [ ] DNS resolution + validation avant requête ?

## Vérification Globale

### Transport Security
- [ ] HTTPS obligatoire partout ?
- [ ] HSTS activé ?
- [ ] Certificats valides ?
- [ ] TLS 1.2+ uniquement ?

### Headers Sécurité
- [ ] Content-Security-Policy ?
- [ ] X-Content-Type-Options: nosniff ?
- [ ] X-Frame-Options: DENY ou SAMEORIGIN ?
- [ ] Referrer-Policy configuré ?
- [ ] Permissions-Policy configuré ?

### API Security
- [ ] Authentication sur tous endpoints ?
- [ ] Rate limiting API ?
- [ ] Input validation stricte ?
- [ ] Output encoding approprié ?
- [ ] Versioning API sécurisé ?

### Data Protection
- [ ] PII identifié et protégé ?
- [ ] Données sensibles minimisées ?
- [ ] Backups chiffrés ?
- [ ] Suppression sécurisée données ?
- [ ] GDPR compliance si applicable ?

### Development Practices
- [ ] Secure SDLC en place ?
- [ ] Security training développeurs ?
- [ ] Code reviews incluent sécurité ?
- [ ] SAST/DAST dans CI/CD ?
- [ ] Penetration testing régulier ?

## Référence

OWASP Top 10 2021 : https://owasp.org/Top10/
