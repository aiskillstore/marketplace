# Checklist Code Review Sécurité

## Authentification & Sessions

- [ ] Passwords hashés avec algorithme fort (Argon2id, bcrypt) ?
- [ ] Paramètres hashing appropriés (bcrypt work factor 12+) ?
- [ ] Session IDs cryptographiquement sécurisés ?
- [ ] Cookies avec HttpOnly, Secure, SameSite ?
- [ ] Expiration session appropriée ?
- [ ] Régénération session ID après login ?
- [ ] Rate limiting sur authentification ?
- [ ] Protection brute force (lockout, CAPTCHA) ?
- [ ] MFA implémenté ou disponible ?
- [ ] Password reset sécurisé (tokens uniques, expiration) ?

## Autorisation & Contrôle d'Accès

- [ ] Autorisation vérifiée côté serveur (toutes requêtes) ?
- [ ] Principe least privilege appliqué ?
- [ ] Pas de dépendance autorisation côté client uniquement ?
- [ ] IDOR vérifié (user peut accéder seulement ses ressources) ?
- [ ] Vertical privilege escalation impossible ?
- [ ] Horizontal privilege escalation impossible ?
- [ ] RBAC/ABAC implémenté correctement ?

## Injection & Validation Input

- [ ] SQL : Prepared statements/parameterized queries ?
- [ ] NoSQL : Validation type et sanitization ?
- [ ] Command injection : Pas d'exec() avec user input ?
- [ ] XSS : Output encoding contextualisé ?
- [ ] Path traversal : Validation chemins fichiers ?
- [ ] XXE : External entities désactivées ?
- [ ] Input validation côté serveur (jamais que client) ?
- [ ] Whitelist validation plutôt que blacklist ?
- [ ] Type checking strict ?
- [ ] Longueur maximale respectée ?

## Cryptographie

- [ ] Algorithmes modernes (AES-256-GCM, RSA-2048+) ?
- [ ] Pas d'algorithmes faibles (MD5, SHA1, DES, RC4) ?
- [ ] IV/Nonce unique par chiffrement ?
- [ ] Pas de mode ECB ?
- [ ] AEAD utilisé (GCM) ou Encrypt-then-MAC ?
- [ ] Clés générées cryptographiquement ?
- [ ] Clés stockées de manière sécurisée (KMS, Vault) ?
- [ ] Pas de clés hardcodées dans code ?
- [ ] TLS 1.2+ pour communications ?
- [ ] Certificats valides et vérifiés ?

## Gestion des Secrets

- [ ] Pas de secrets hardcodés (passwords, API keys) ?
- [ ] Pas de secrets dans config versionnée ?
- [ ] Variables d'environnement ou secrets manager utilisés ?
- [ ] .env dans .gitignore ?
- [ ] Secrets rotation possible ?
- [ ] Pas de secrets dans logs ?
- [ ] Pas de secrets dans messages d'erreur ?

## API & CORS

- [ ] CORS configuré strictement (pas de wildcard *) ?
- [ ] Content-Type validé ?
- [ ] Rate limiting implémenté ?
- [ ] Input validation sur tous endpoints ?
- [ ] Authentication sur endpoints sensibles ?
- [ ] CSRF protection si state-changing via cookies ?
- [ ] Pas de données sensibles dans URLs ?
- [ ] Versioning API sécurisé ?

## Gestion des Erreurs

- [ ] Messages d'erreur génériques (pas de stack traces) ?
- [ ] Pas d'info sensible révélée dans erreurs ?
- [ ] Logs erreurs appropriés (forensics) ?
- [ ] Exceptions catchées correctement ?
- [ ] Fail secure (échec = refus accès) ?

## Logging & Monitoring

- [ ] Événements sécurité loggés (login, échecs auth) ?
- [ ] Pas de données sensibles dans logs (passwords, tokens) ?
- [ ] Logs suffisamment détaillés pour audit ?
- [ ] Timestamp et user ID dans logs ?
- [ ] Logs protégés (accès restreint) ?
- [ ] Monitoring alertes configurées ?

## File Upload

- [ ] Validation type fichier (pas que extension) ?
- [ ] Taille maximale fichier ?
- [ ] Scan antivirus si possible ?
- [ ] Stockage hors webroot ?
- [ ] Noms fichiers sécurisés (pas d'exécution) ?
- [ ] Pas d'exécution fichiers uploadés ?

## Data Protection

- [ ] Données sensibles chiffrées au repos ?
- [ ] Données sensibles chiffrées en transit ?
- [ ] PII minimisé et protégé ?
- [ ] Pas de données sensibles en logs ?
- [ ] Suppression sécurisée données ?
- [ ] Backups chiffrés ?

## Security Headers

- [ ] Content-Security-Policy configuré ?
- [ ] X-Content-Type-Options: nosniff ?
- [ ] X-Frame-Options: DENY ou SAMEORIGIN ?
- [ ] Strict-Transport-Security (HSTS) ?
- [ ] Referrer-Policy configuré ?
- [ ] Permissions-Policy configuré ?

## Dependencies & Configuration

- [ ] Dépendances à jour ?
- [ ] Pas de vulnérabilités connues (scan SAST) ?
- [ ] Configurations par défaut changées ?
- [ ] Features inutilisées désactivées ?
- [ ] Debug mode désactivé en production ?
- [ ] Pas de commentaires sensibles dans code ?

## Business Logic

- [ ] Race conditions vérifiées ?
- [ ] Integer overflow/underflow impossibles ?
- [ ] Logique métier pas bypassable ?
- [ ] State machine sécurisée ?
- [ ] Transactions atomiques si nécessaire ?

## Testing

- [ ] Tests sécurité inclus ?
- [ ] Tests cas limites (edge cases) ?
- [ ] Tests inputs malicieux ?
- [ ] Tests autorisation ?
- [ ] Tests injection basiques ?

## Référence

Utiliser en complément de OWASP Top 10 checklist
