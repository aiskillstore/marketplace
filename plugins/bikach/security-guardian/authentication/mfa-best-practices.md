# Multi-Factor Authentication (MFA)

## Définition

Authentification nécessitant deux ou plusieurs facteurs de vérification indépendants.

## Sévérité

🟢 **INFO** - MFA améliore significativement la sécurité

## Facteurs d'Authentification

### Types

**1. Quelque chose que vous savez**
- Mot de passe
- PIN
- Questions secrètes

**2. Quelque chose que vous avez**
- Smartphone (TOTP)
- Hardware key (FIDO2)
- Smart card

**3. Quelque chose que vous êtes**
- Biométrie (empreinte, visage)
- Comportemental (frappe clavier)

## Méthodes MFA

### TOTP (Time-based One-Time Password)

**Recommandé**
```
✅ Algorithme standard (RFC 6238)
✅ Offline (pas besoin réseau)
✅ Apps : Google Authenticator, Authy, etc.
✅ Code 6 chiffres, 30 secondes
```

**Configuration**
- Générer secret partagé
- QR code pour setup
- Backup codes fournis
- Validation fenêtre temps (±1 période)

### Hardware Keys (FIDO2/WebAuthn)

**Le Plus Sécurisé**
```
✅ Résistant phishing
✅ Pas de secret partagé
✅ Cryptographie forte
✅ Yubikey, Titan Key, etc.
```

**Avantages**
- Protection phishing totale
- Pas de MITM possible
- Expérience utilisateur simple

### Push Notifications

**Modéré**
```
✅ Expérience utilisateur simple
✅ Apps : Duo, Microsoft Authenticator
⚠️ Nécessite connexion réseau
⚠️ Fatigue MFA possible
```

**Recommandations**
- Afficher contexte (IP, localisation)
- Limite tentatives
- Timeout court

### SMS (À Éviter)

**Moins Sécurisé**
```
❌ SIM swapping
❌ Interception SS7
❌ Phishing SMS
⚠️ Dernier recours uniquement
```

**Si Utilisé**
- Alerter utilisateur des risques
- Proposer alternatives meilleures
- Rate limiting strict

### Email (À Éviter pour MFA)

```
❌ Email compromis = compte compromis
❌ Pas vraiment un second facteur
⚠️ Acceptable pour notifications, pas MFA
```

## Implémentation

### Enrollment

**Process**
```
1. User active MFA dans paramètres
2. Choisir méthode (TOTP, hardware key)
3. Setup (QR code, enregistrement clé)
4. Vérification initiale
5. Génération backup codes
6. Confirmation enrollment
```

**Backup Codes**
```
✅ Générer 10-12 codes
✅ Usage unique
✅ Stockage hash côté serveur
✅ Téléchargement une seule fois
✅ Régénération possible
```

### Validation

**À Chaque Login**
```
1. Username/password validés
2. Demander second facteur
3. Valider code/key
4. Rate limiting échecs
5. Log tentatives
```

**Remember Device (Optionnel)**
```
⚠️ Cookie sur device trusted
⚠️ Durée limitée (30 jours max)
⚠️ Révocable par utilisateur
⚠️ Pas pour comptes sensibles
```

### Recovery

**Si Perte Accès MFA**
```
Options :
1. Backup codes (recommandé)
2. Email recovery (si configuré)
3. Support manual (vérification identité)
```

**Process Recovery**
- Vérification stricte identité
- Email confirmation
- Reset MFA
- Force re-enrollment
- Log événement

## Politique MFA

### Obligatoire Pour

```
✅ Comptes administrateurs
✅ Accès données sensibles
✅ Actions financières
✅ Changement email/password
```

### Optionnel Mais Encouragé

```
✅ Tous les utilisateurs
✅ Incentives (badge, réduction)
✅ Education sur bénéfices
```

### Bypass MFA (Attention)

```
⚠️ APIs avec API keys (pas MFA)
⚠️ Trusted networks (interne)
⚠️ Automated systems

→ Alternatives : API keys sécurisées, service accounts
```

## User Experience

### Bonnes Pratiques

**Simplicité**
- Flow clair et guidé
- Instructions explicites
- Support multiple méthodes

**Flexibilité**
- Choix méthode préférée
- Backup methods
- Remember device option

**Éducation**
- Expliquer bénéfices
- Guides setup
- FAQ

### Éviter Friction

```
❌ MFA sur chaque action mineure
✅ MFA sur login + actions sensibles
✅ Session durée raisonnable
✅ Remember device pour non-sensible
```

## MFA Fatigue

### Problème

```
Bombardement notifications MFA
→ User approve sans vérifier
→ Attaquant obtient accès
```

### Mitigation

```
✅ Limite tentatives MFA
✅ Afficher contexte (IP, location)
✅ Délai entre tentatives
✅ Alert après X refus
✅ Notification tentatives suspectes
```

## Checklist d'Audit

### Implémentation
- [ ] MFA disponible ?
- [ ] Méthodes sécurisées (TOTP, FIDO2) ?
- [ ] Backup codes fournis ?
- [ ] Recovery process sécurisé ?

### Politique
- [ ] MFA obligatoire pour admins ?
- [ ] MFA encouragé pour tous ?
- [ ] MFA pour actions sensibles ?

### Sécurité
- [ ] Rate limiting MFA attempts ?
- [ ] Protection MFA fatigue ?
- [ ] Remember device sécurisé ?
- [ ] Logs tentatives MFA ?

### UX
- [ ] Multiple méthodes supportées ?
- [ ] Setup guidé clair ?
- [ ] Recovery accessible ?

### SMS/Email
- [ ] SMS non seule option ?
- [ ] Email non utilisé comme MFA ?
- [ ] Warnings sur risques SMS ?

## Erreurs Courantes

### ❌ SMS Seul Facteur
SIM swapping facile

### ❌ Pas de Backup Codes
User bloqué si perte device

### ❌ MFA Optionnel Partout
Admins sans MFA = risque

### ❌ Pas de Rate Limiting
Brute force codes possibles

### ❌ Remember Device Permanent
Compromission device = bypass MFA

### ❌ Pas de Context Push
User approve sans vérifier

## Références

- **NIST SP 800-63B** : Authentication Guidelines
- **FIDO Alliance** : WebAuthn, FIDO2
- **RFC 6238** : TOTP
- **OWASP** : Multi-Factor Authentication
