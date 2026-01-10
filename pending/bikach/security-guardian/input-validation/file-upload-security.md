# Sécurité Upload de Fichiers

## Définition

Protection contre attaques via upload de fichiers malveillants (malware, webshell, path traversal).

## Sévérité

🔴 **CRITIQUE** - RCE, malware, défacement

## Risques

### Remote Code Execution

```
Upload fichier exécutable (.php, .jsp, .asp)
→ Accès via URL
→ Exécution code serveur
```

### Malware Distribution

```
Upload malware
→ Téléchargé par autres users
→ Infection
```

### Path Traversal

```
Filename : ../../evil.php
→ Écrit hors dossier upload
→ Overwrite fichiers système
```

### DoS

```
Upload fichiers volumineux
→ Saturation disque/bande passante
```

### XSS via Upload

```
Upload HTML/SVG avec JavaScript
→ Servi avec mauvais Content-Type
→ XSS
```

## Validation Fichiers

### Extension

**❌ Extension Seule Insuffisante**
```
Facilement bypassé :
- evil.php.jpg
- evil.php%00.jpg (null byte)
- evil.pHp (case)
```

**✅ Whitelist Stricte**
```
allowedExtensions = ['.jpg', '.png', '.pdf']

extension = lowercase(getExtension(filename))
if extension not in allowedExtensions:
  reject
```

### Content-Type

**❌ Header Seul Insuffisant**
```
Content-Type contrôlé par client
Facilement spoofé
```

**✅ Vérifier avec Extension**
```
Validation combinée :
- Extension whitelist
- Content-Type attendu pour extension
- Magic bytes vérification
```

### Magic Bytes (File Signature)

**✅ Vérification Réelle**
```
Lire premiers bytes du fichier
Comparer avec signatures connues

JPG : FF D8 FF
PNG : 89 50 4E 47
PDF : 25 50 44 46
GIF : 47 49 46 38
```

**Bibliothèques**
```
- libmagic
- file-type (npm)
- python-magic
- Apache Tika
```

### Taille

**✅ Limite Stricte**
```
Limite par type :
- Images : 5-10 MB
- Documents : 20 MB
- Vidéos : 100 MB

Rejeter dépassement
```

### Contenu

**Images**
```
✅ Reprocess image (supprime metadata malveillant)
✅ ImageMagick, Pillow, Sharp
✅ Génération thumbnail (validation)
```

**Documents**
```
✅ Parser pour validation
✅ Scan macros (Office docs)
✅ Sandbox si possible
```

## Sanitization Filename

### Caractères Dangereux

```
../  (path traversal)
\    (Windows separator)
:    (drive Windows)
|    (pipe)
<>   (redirections)
&    (command separator)
;    (command separator)
%00  (null byte)
```

### Sanitization Stricte

```
✅ Supprimer path separators
✅ Whitelist caractères [A-Za-z0-9_.-]
✅ Limiter longueur (255 chars)
✅ Ou générer nom aléatoire (UUID)
```

### Génération Nom Sécurisé

```
✅ UUID + extension validée
✅ Hash(original_name) + timestamp
✅ Ne jamais utiliser nom original directement
```

## Stockage

### Localisation

**❌ Dangereux**
```
Webroot avec exécution possible
/var/www/html/uploads/
```

**✅ Sécurisé**
```
Hors webroot
/var/app_data/uploads/
/mnt/storage/uploads/

Ou service stockage (S3, Azure Blob)
```

### Permissions

```
✅ Pas d'exécution
✅ Read-only pour serveur web
✅ Write pour process upload uniquement
✅ Pas de chmod 777
```

### Séparation

```
✅ Dossier par user/session
✅ Pas de listing directory
✅ Accès contrôlé
```

## Serving Fichiers

### Content-Type

```
✅ Forcer Content-Type correct
✅ X-Content-Type-Options: nosniff
❌ Pas de Content-Type : text/html
```

**Headers Sécurisés**
```
Content-Type: image/jpeg
Content-Disposition: attachment; filename="file.jpg"
X-Content-Type-Options: nosniff
```

### Content-Disposition

```
✅ attachment : Force téléchargement
⚠️ inline : Affichage navigateur (seulement si sûr)
```

### URL Accès

```
✅ URLs non-prévisibles
✅ Authorization check avant serve
✅ Tokens temporaires si possible
❌ Accès direct sans auth
```

## Antivirus Scanning

### Scan Upload

```
✅ ClamAV ou équivalent
✅ Scan asynchrone si gros fichiers
✅ Quarantine si malware détecté
✅ Notification user si rejet
```

### Process

```
1. Upload
2. Stockage temporaire
3. Scan antivirus
4. Si clean → Déplacer vers storage final
5. Si malware → Supprimer + log + notifier
```

## Quotas & Rate Limiting

### Par User

```
✅ Limite uploads/jour
✅ Limite taille totale
✅ Limite taille individuelle
```

### Global

```
✅ Limite bande passante
✅ Limite stockage total
✅ Rate limiting upload endpoint
```

## Types Spécifiques

### Images

```
✅ Reprocess (ImageMagick, Pillow)
✅ Strip metadata EXIF
✅ Génération thumbnails
✅ Validation dimensions
⚠️ SVG = XML (XSS, XXE possible)
```

### Documents PDF

```
✅ Parser validation
⚠️ JavaScript dans PDF possible
⚠️ Embedded files
✅ Sandbox si nécessaire
```

### Archives (ZIP, TAR)

```
✅ Validation contenu
⚠️ Zip bomb (compression extrême)
⚠️ Path traversal dans archive
✅ Limite taille décompressée
```

### Office Documents

```
⚠️ Macros malveillantes
⚠️ Embedded objects
✅ Scan macros
✅ Conversion format sécurisé si possible
```

## Checklist d'Audit

### Validation
- [ ] Extension whitelist ?
- [ ] Content-Type vérifié ?
- [ ] Magic bytes vérifiés ?
- [ ] Taille maximale appliquée ?
- [ ] Contenu parsé/validé ?

### Filename
- [ ] Nom fichier sanitizé ?
- [ ] Path traversal impossible ?
- [ ] Caractères dangereux supprimés ?
- [ ] Ou nom généré aléatoirement ?

### Stockage
- [ ] Hors webroot ?
- [ ] Permissions restrictives ?
- [ ] Pas d'exécution possible ?
- [ ] Séparation par user ?

### Serving
- [ ] Content-Type forcé correct ?
- [ ] Content-Disposition: attachment ?
- [ ] X-Content-Type-Options: nosniff ?
- [ ] Authorization avant accès ?

### Scanning
- [ ] Antivirus scan ?
- [ ] Quarantine malware ?
- [ ] Logs uploads suspects ?

### Limites
- [ ] Quotas par user ?
- [ ] Rate limiting ?
- [ ] Taille maximale ?

## Erreurs Courantes

### ❌ Extension Seule
Facilement bypassé

### ❌ Stockage Webroot
Exécution possible

### ❌ Nom Original
Path traversal

### ❌ Pas de Content-Type Control
XSS via upload

### ❌ Pas de Scan Antivirus
Malware distribution

### ❌ Pas de Limite Taille
DoS

## Références

- **OWASP** : File Upload Cheat Sheet
- **CWE-434** : Unrestricted Upload of File with Dangerous Type
- **OWASP** : Unrestricted File Upload
