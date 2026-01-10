# Gestion des PII (Personally Identifiable Information)

## Définition

Informations permettant d'identifier directement ou indirectement une personne physique.

## Sévérité

🔴 **CRITIQUE** - Conformité légale, privacy, amendes

## Types de PII

### PII Direct (Sensible)

```
- Nom complet
- Email
- Numéro téléphone
- Adresse postale
- Numéro sécurité sociale
- Passeport, carte identité
- Numéro compte bancaire
- Données biométriques
- Données santé
- Orientation sexuelle
- Opinions politiques
```

### PII Indirect

```
- IP address
- Cookie IDs
- Device IDs
- Géolocalisation
- Historique navigation
- Combinaison données permettant identification
```

## Principes Fondamentaux

### Minimisation

```
✅ Collecter uniquement nécessaire
✅ Pas de "nice to have"
✅ Justification business pour chaque donnée
❌ Collecter "au cas où"
```

### Purpose Limitation

```
✅ Utilisation pour objectif déclaré uniquement
❌ Réutilisation sans consentement
❌ Vente à tiers sans consentement
```

### Limitation Conservation

```
✅ Durée définie et justifiée
✅ Suppression automatique après
❌ Conservation indéfinie
```

### Transparence

```
✅ Privacy policy claire
✅ User informé collecte et usage
✅ Consentement explicite si nécessaire
```

## Protection PII

### Chiffrement

**Au Repos**
```
✅ PII chiffrées en database
✅ AES-256-GCM minimum
✅ Clés gérées KMS
❌ Stockage en clair
```

**En Transit**
```
✅ TLS 1.2+ obligatoire
✅ HSTS activé
❌ HTTP jamais pour PII
```

### Access Control

```
✅ Principe least privilege
✅ RBAC strict
✅ Logs accès PII
✅ MFA pour accès admin
✅ Séparation dev/prod (pas de PII en dev)
```

### Masking & Redaction

**Logs**
```
✅ Masquer PII dans logs
Email : u***@example.com
Phone : ***-***-1234
SSN : ***-**-1234
```

**UI**
```
✅ Masking partiel
Carte : **** **** **** 1234
```

**Dev/Test**
```
✅ Données anonymisées/synthétiques
❌ Copie production en dev
```

## Anonymisation & Pseudonymisation

### Anonymisation

```
Suppression complète lien avec personne
Irréversible
Plus considéré PII après

Techniques :
- Agrégation
- Généralisation
- Suppression identifiants
```

### Pseudonymisation

```
Remplacement par pseudonymes
Réversible avec clé séparée
Toujours considéré PII

Technique :
- Hashing avec salt
- Tokenization
- Encryption
```

## Droits Utilisateurs (GDPR)

### Droit d'Accès

```
✅ User peut demander ses données
✅ Réponse sous 30 jours
✅ Format machine-readable
```

### Droit de Rectification

```
✅ Correction données incorrectes
✅ Complétion données incomplètes
```

### Droit à l'Effacement

```
✅ "Right to be forgotten"
✅ Suppression définitive
✅ Vérifier backups
⚠️ Exceptions légales (comptabilité, etc.)
```

### Droit à la Portabilité

```
✅ Export données format standard
✅ JSON, CSV
✅ Transmission autre service si demandé
```

### Droit d'Opposition

```
✅ Refuser traitement
✅ Opt-out marketing
✅ Opt-out profiling
```

## Suppression Données

### Soft Delete vs Hard Delete

**Soft Delete**
```
Flag deleted = true
Données restent en base
Pour compliance (logs, audit)
```

**Hard Delete**
```
Suppression physique
Irréversible
GDPR requiert hard delete
```

### Process Suppression

```
1. Marquer pour suppression (soft)
2. Période grace (30 jours)
3. Hard delete après période
4. Vérifier backups
5. Anonymiser logs
6. Supprimer files associés
```

### Backups

```
⚠️ PII dans backups = problème GDPR
✅ Rotation backups (180 jours max recommandé)
✅ Anonymisation avant archivage long terme
✅ Process suppression dans backups si demandé
```

## Transferts Internationaux

### Hors UE (GDPR)

```
⚠️ Restrictions transfert PII hors UE
✅ Adequacy decision (pays "safe")
✅ Standard Contractual Clauses (SCC)
✅ Binding Corporate Rules (BCR)
❌ Privacy Shield invalidé
```

### Cloud Providers

```
✅ Vérifier localisation données
✅ Data residency options
✅ DPA (Data Processing Agreement)
```

## Breach Notification

### Obligations

```
Si breach PII :
✅ Notification autorité (72h - GDPR)
✅ Notification users si haut risque
✅ Documentation incident
✅ Mesures correctives
```

### Informations à Fournir

```
- Nature du breach
- Catégories et nombre personnes affectées
- Conséquences probables
- Mesures prises/proposées
```

## Checklist d'Audit

### Collection
- [ ] PII minimisée ?
- [ ] Justification business chaque PII ?
- [ ] Consentement obtenu si nécessaire ?
- [ ] Privacy policy claire ?

### Protection
- [ ] PII chiffrées au repos ?
- [ ] TLS pour transit ?
- [ ] Access control strict ?
- [ ] Masking dans logs ?
- [ ] Pas de PII en dev/test ?

### Droits
- [ ] Process droit d'accès ?
- [ ] Process droit effacement ?
- [ ] Process droit portabilité ?
- [ ] Délais respectés (30 jours) ?

### Suppression
- [ ] Durée conservation définie ?
- [ ] Suppression automatique ?
- [ ] Hard delete implémenté ?
- [ ] Backups gérés ?

### Conformité
- [ ] GDPR compliant (si applicable) ?
- [ ] DPO désigné si nécessaire ?
- [ ] Privacy by design ?
- [ ] DPIA pour traitements risqués ?

### Transferts
- [ ] Localisation données connue ?
- [ ] Transferts internationaux encadrés ?
- [ ] DPA avec processeurs ?

### Incident
- [ ] Breach notification process ?
- [ ] Contact autorité identifié ?
- [ ] Plan communication users ?

## Erreurs Courantes

### ❌ PII en Clair
Stockage non chiffré

### ❌ Logs avec PII
Emails, noms dans logs

### ❌ Copie Prod en Dev
PII en environnement non sécurisé

### ❌ Conservation Indéfinie
Pas de suppression automatique

### ❌ Pas de Process Suppression
Impossible respecter droit effacement

### ❌ Over-Collection
Données non nécessaires collectées

## Références

- **GDPR** : General Data Protection Regulation
- **CCPA** : California Consumer Privacy Act
- **ISO 27701** : Privacy Information Management
- **NIST** : Privacy Framework
