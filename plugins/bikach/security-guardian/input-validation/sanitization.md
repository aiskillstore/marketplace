# Sanitization des Entrées

## Définition

Nettoyage et normalisation des données utilisateur avant traitement ou stockage.

## Sévérité

🔴 **CRITIQUE** - Injection, XSS, corruption données

## Principe Fondamental

```
Defense in Depth :
1. Validation (rejeter invalide)
2. Sanitization (nettoyer si accepté)
3. Encoding (contexte output)

⚠️ Sanitization seule n'est PAS suffisante
```

## Types de Sanitization

### HTML Sanitization

**Objectif** : Supprimer/échapper tags dangereux

**Patterns Dangereux**
```
<script>
<iframe>
<object>
<embed>
<link>
<style>
javascript:
on* attributes (onclick, onerror)
```

**Approches**
```
✅ Whitelist tags autorisés (si HTML riche nécessaire)
✅ Strip all HTML (si pas nécessaire)
✅ Bibliothèques : DOMPurify, Bleach, HtmlSanitizer
❌ Regex manual (incomplet, bypassable)
```

### SQL Sanitization

**Objectif** : Prévenir SQL injection

**Caractères Spéciaux**
```
' (quote)
" (double quote)
; (semicolon)
-- (comment)
/* */ (comment)
```

**⚠️ IMPORTANT**
```
❌ Sanitization n'est PAS suffisante
✅ Utiliser prepared statements TOUJOURS
✅ Sanitization = defense in depth additionnel
```

### Filename Sanitization

**Objectif** : Prévenir path traversal, injection

**Patterns Dangereux**
```
../
..\
/
\
:
%00 (null byte)
Caractères spéciaux système
```

**Sanitization**
```
✅ Supprimer path separators
✅ Supprimer caractères spéciaux
✅ Limiter extension (whitelist)
✅ Générer nom aléatoire si possible
```

### URL Sanitization

**Objectif** : Prévenir open redirect, SSRF

**Validation**
```
✅ Whitelist protocols (http, https)
✅ Whitelist domaines autorisés
✅ Pas de javascript:, data:, file:
✅ Parser URL et valider composants
```

### Email Sanitization

**Normalisation**
```
✅ Lowercase
✅ Trim whitespace
✅ Valider format RFC 5322
✅ Remove comments si présents
```

### Integer/Number Sanitization

**Conversion**
```
✅ Parse en nombre
✅ Vérifier range
✅ Rejeter si NaN
✅ Attention overflow
```

## Whitelist vs Blacklist

### Whitelist (Recommandé)

```
✅ Accepter seulement caractères/patterns autorisés
✅ Plus sécurisé
✅ Explicit allow

Exemple : [A-Za-z0-9_-]+ pour username
```

### Blacklist (Éviter)

```
❌ Rejeter patterns connus dangereux
❌ Incomplet (nouveaux bypasses)
❌ Difficile maintenir

Toujours possibilité de bypass
```

## Context-Aware Sanitization

### HTML Context

```
< → &lt;
> → &gt;
& → &amp;
" → &quot;
' → &#x27;
```

### JavaScript Context

```
\ → \\
" → \"
' → \'
< → \x3c
> → \x3e
```

### URL Context

```
Encoder avec encodeURIComponent()
Spaces → %20
& → %26
= → %3D
```

### SQL Context

```
⚠️ Utiliser prepared statements
⚠️ Pas de sanitization manuelle
```

## Normalisation

### Unicode Normalization

**Problème**
```
Caractères Unicode équivalents :
é peut être : U+00E9 ou U+0065 + U+0301
→ Bypass validation/sanitization
```

**Solution**
```
✅ Normaliser en NFC ou NFKC
✅ Avant validation
```

### Case Normalization

```
✅ Lowercase pour comparaisons
✅ Cohérence recherche/matching
✅ Éviter bypass case-sensitive
```

### Whitespace Normalization

```
✅ Trim leading/trailing
✅ Normaliser espaces multiples
✅ Convertir tabs/newlines si approprié
```

## Bibliothèques Recommandées

### HTML

```
- DOMPurify (JavaScript)
- Bleach (Python)
- HtmlSanitizer (C#)
- OWASP Java HTML Sanitizer
```

### General

```
- validator.js (JavaScript)
- Apache Commons Validator (Java)
- WTForms (Python)
```

## Checklist d'Audit

### Validation First
- [ ] Validation avant sanitization ?
- [ ] Rejeter invalide plutôt que sanitizer ?
- [ ] Whitelist préférée à blacklist ?

### HTML
- [ ] Bibliothèque sanitization HTML (DOMPurify) ?
- [ ] Whitelist tags si HTML riche ?
- [ ] Strip HTML si pas nécessaire ?
- [ ] Output encoding contextuel ?

### SQL
- [ ] Prepared statements utilisés ?
- [ ] Sanitization n'est PAS la seule défense ?

### Files
- [ ] Noms fichiers sanitizés ?
- [ ] Path separators supprimés ?
- [ ] Extensions validées (whitelist) ?

### URLs
- [ ] Protocols whitelist (http/https) ?
- [ ] Domaines validés ?
- [ ] Pas de javascript:, data: ?

### Normalisation
- [ ] Unicode normalisé ?
- [ ] Case normalisé si nécessaire ?
- [ ] Whitespace nettoyé ?

## Ordre des Opérations

```
1. Normalisation (Unicode, case, whitespace)
2. Validation (format, type, range)
3. Sanitization (si validation passe)
4. Encoding (contexte output)
```

## Erreurs Courantes

### ❌ Sanitization Seule
Sans validation préalable

### ❌ Blacklist
Incomplet, bypassable

### ❌ Regex Manual pour HTML
Complexe, erreurs fréquentes

### ❌ Double Encoding
Sanitizer encode, template re-encode

### ❌ Pas de Normalisation
Unicode bypass

### ❌ Sanitization Wrong Context
HTML sanitization pour SQL

## Références

- **OWASP** : Input Validation Cheat Sheet
- **DOMPurify** : XSS Sanitizer
- **OWASP** : XSS Prevention Cheat Sheet
