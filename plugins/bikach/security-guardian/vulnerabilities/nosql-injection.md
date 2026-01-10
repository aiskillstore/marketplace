# NoSQL Injection

## Définition

Injection de code malveillant dans les requêtes NoSQL (MongoDB, CouchDB, Redis, etc.), permettant de contourner l'authentification ou d'accéder à des données non autorisées.

## Sévérité

🔴 **CRITIQUE** - Bypass authentification, accès non autorisé aux données

## Bases de Données Concernées

- **MongoDB** (le plus courant)
- **CouchDB**
- **Redis**
- **Cassandra**
- **Elasticsearch**

## Types d'Injection NoSQL

### 1. Operator Injection
Injection d'opérateurs MongoDB ($gt, $ne, $where, etc.)

### 2. JavaScript Injection
Injection dans $where, mapReduce, $function

### 3. JSON Injection
Manipulation de la structure JSON de la requête

### 4. Array Injection
Transformation d'un string en array pour modifier la requête

## Patterns Vulnérables à Détecter

### Paramètres Non Validés dans Queries

```
MongoDB patterns dangereux :
- collection.find({ username: req.body.username })
- collection.find({ email: params.email })
- db.users.find({ $where: userInput })
- collection.find(JSON.parse(req.body.filter))
```

### Where Clauses avec Input Utilisateur

```
- $where: "this.username == '" + username + "'"
- $where: function() { return this.field == userInput }
```

### Regex Non Échappé

```
- { name: { $regex: req.query.search } }
- { field: new RegExp(userInput) }
```

## Vecteurs d'Attaque MongoDB

### Operator Injection

**Bypass Authentification**
```
Input JSON:
{
  "username": {"$ne": null},
  "password": {"$ne": null}
}

Query résultante:
db.users.find({ username: {$ne: null}, password: {$ne: null} })
→ Retourne tous les utilisateurs
```

**Extract Data**
```
Input:
{
  "username": {"$gt": ""},
  "password": {"$regex": "^a"}
}

→ Brute force du password caractère par caractère
```

### JavaScript Injection

**$where Injection**
```
Input: '; return true; //
Query:
db.users.find({ $where: "this.username == ''; return true; //'" })
→ Retourne tous les documents
```

### Array Injection

**Transformation String → Array**
```
Input: ["$ne", ""]
Si non validé:
{ password: ["$ne", ""] }
→ Interprété comme $ne operator
```

## Localisation dans le Code

### À Chercher

#### Controllers/Routes
- Utilisation directe de req.body/req.query
- Pas de validation de type
- Pas de sanitization

#### Repositories/DAL
- Construction de queries dynamiques
- Utilisation de $where
- Regex avec input utilisateur

#### Authentication
- Login endpoints
- Password reset
- Token validation

### Patterns à Grep

```
MongoDB patterns à rechercher :
- "find\(.*req\.body"
- "find\(.*req\.query"
- "find\(.*params\."
- "\$where.*\+"
- "\$regex.*req\."
- "JSON\.parse.*req\."
- "new RegExp\(.*req\."
```

## Impact

### Bypass Authentification
- Connexion sans credentials valides
- Accès à n'importe quel compte

### Extraction de Données
- Lecture de données sensibles
- Brute force de passwords
- Enumération d'utilisateurs

### Modification de Données
- Update de documents arbitraires
- Escalade de privilèges

### Déni de Service
- Requêtes coûteuses en ressources
- Regex catastrophiques
- $where avec boucles infinies

## Remédiation

### 1. Validation de Type Stricte

**Principe**
- S'assurer que les paramètres sont du bon type
- Rejeter les objets quand string attendu
- Validation avant query

**Implémentation**
```
✅ CORRECT :
if (typeof username !== 'string')
  throw new Error('Invalid type')

if (Array.isArray(password))
  throw new Error('Invalid type')

// Ou avec validation schema
const schema = {
  username: { type: 'string', required: true },
  password: { type: 'string', required: true }
}
```

### 2. Sanitization des Inputs

**Supprimer les Operators**
```
✅ CORRECT :
function sanitize(obj) {
  if (typeof obj !== 'object') return obj

  for (let key in obj) {
    if (key.startsWith('$')) {
      delete obj[key]
    } else if (typeof obj[key] === 'object') {
      sanitize(obj[key])
    }
  }
  return obj
}
```

### 3. Éviter $where

**Alternative**
- Utiliser les operators MongoDB standards
- Aggregation pipeline
- Éviter JavaScript execution

**Si $where Nécessaire**
- Jamais avec input utilisateur
- Validation extrêmement stricte

### 4. Regex Sécurisé

**Échapper les Caractères Spéciaux**
```
✅ CORRECT :
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const safePattern = escapeRegex(userInput)
collection.find({ name: { $regex: safePattern } })
```

### 5. Schema Validation

**MongoDB Schema Validation**
- Définir les types attendus
- Rejection automatique de types incorrects
- Validation au niveau base de données

**Application-level Schema**
- Joi, Yup, Zod, etc.
- Validation avant query
- Type enforcement

### 6. Principe du Moindre Privilège

**Permissions DB**
- Compte avec permissions minimales
- Pas de droits admin pour l'app
- Read-only pour queries de lecture

### 7. Requêtes Paramétrées

**Utiliser Query Builders**
- Mongoose avec validation
- Prisma
- TypeORM

**Éviter**
- String concatenation
- JSON.parse de user input
- Dynamic query construction

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Paramètres req.body/query utilisés directement ?
- [ ] Validation de type des paramètres ?
- [ ] Utilisation de $where avec input utilisateur ?
- [ ] Regex avec input non échappé ?
- [ ] JSON.parse de données utilisateur ?
- [ ] Construction dynamique de queries ?

### Validation des Correctifs
- [ ] Validation de type stricte implémentée ?
- [ ] Sanitization des operators ($) ?
- [ ] Regex inputs échappés ?
- [ ] $where évité ou sécurisé ?
- [ ] Schema validation en place ?
- [ ] Query builders utilisés ?

### Tests de Vulnérabilité
- [ ] Tester avec {"$ne": null} ?
- [ ] Tester avec {"$gt": ""} ?
- [ ] Tester array injection ?
- [ ] Tester $where injection ?
- [ ] Tester regex injection ?

## MongoDB Operators Dangereux

### Operators à Surveiller
- **$where** : Exécution JavaScript
- **$regex** : Si input non échappé
- **$ne** : Not equal (bypass)
- **$gt, $gte** : Greater than (enumeration)
- **$lt, $lte** : Less than (enumeration)
- **$in** : In array (si contrôlé par user)
- **$nin** : Not in array

## Exemples Sécurisés

### Login Sécurisé
```
✅ CORRECT :
// Validation stricte
if (typeof username !== 'string' || typeof password !== 'string')
  return res.status(400).json({ error: 'Invalid input' })

// Query sûre
const user = await User.findOne({
  username: username,  // string simple, pas d'object
  password: hashedPassword
})
```

### Recherche Sécurisée
```
✅ CORRECT :
// Échapper regex
const escapedSearch = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

// Query sécurisée
const results = await collection.find({
  name: { $regex: escapedSearch, $options: 'i' }
})
```

### Filter Sécurisé
```
✅ CORRECT :
// Whitelist des champs autorisés
const allowedFields = ['name', 'email', 'status']
const filter = {}

for (let [key, value] of Object.entries(req.query)) {
  if (allowedFields.includes(key) && typeof value === 'string') {
    filter[key] = value
  }
}

const results = await collection.find(filter)
```

## Références

- **OWASP** : NoSQL Injection
- **CWE-943** : Improper Neutralization of Special Elements in Data Query Logic
- **MongoDB Security Checklist**
