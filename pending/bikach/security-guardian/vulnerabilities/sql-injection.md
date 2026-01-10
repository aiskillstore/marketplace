# SQL Injection

## Définition

Injection de code SQL malveillant dans les requêtes de l'application, permettant de manipuler la base de données.

## Sévérité

🔴 **CRITIQUE** - Accès non autorisé aux données, modification, suppression

## Types d'Injection SQL

### 1. Classic SQL Injection
Injection dans WHERE clause, ORDER BY, etc.

### 2. Blind SQL Injection
Pas de retour direct mais détection via comportement (timing, boolean)

### 3. Union-based Injection
Utilisation de UNION pour combiner résultats

### 4. Time-based Injection
Utilisation de SLEEP/WAITFOR pour détecter la vulnérabilité

### 5. Second-order Injection
Données malveillantes stockées puis exécutées plus tard

## Patterns Vulnérables à Détecter

### Concaténation de Strings
```
Rechercher patterns :
- "SELECT * FROM users WHERE id = " + userId
- `SELECT * FROM users WHERE name = '${userName}'`
- "DELETE FROM table WHERE id = " + id
- query = "INSERT INTO ... VALUES (" + values + ")"
```

### Interpolation dans Requêtes
```
- String.format("SELECT * FROM ...", param)
- f"SELECT * FROM users WHERE id = {user_id}"
- `UPDATE users SET name = '${name}'`
```

### Requêtes Dynamiques Non Paramétrées
```
- query = "SELECT * FROM " + tableName
- orderBy = req.params.sort  // utilisé directement dans ORDER BY
- filterClause = buildFilter(params)  // si non échappé
```

## Vecteurs d'Attaque

### WHERE Clause
```
Input: ' OR '1'='1
Résultat: WHERE username = '' OR '1'='1'
→ Toujours vrai, bypass authentification
```

### ORDER BY
```
Input: id; DROP TABLE users--
Résultat: ORDER BY id; DROP TABLE users--
→ Exécution de commande supplémentaire
```

### UNION
```
Input: 1 UNION SELECT password FROM users--
Résultat: Extraction de données d'autres tables
```

### Time-based
```
Input: 1' AND SLEEP(5)--
Résultat: Si délai, vulnérable
```

## Localisation dans le Code

### À Chercher

#### Controllers/Routes
- Paramètres de requête utilisés directement
- Validation insuffisante des entrées

#### Repositories/DAL
- Construction de requêtes SQL dynamiques
- Concaténation de strings
- Interpolation de variables

#### Services
- Filtres dynamiques
- Tri dynamique (ORDER BY)
- Recherche fulltext

### Patterns à Grep

```
Patterns dangereux :
- "SELECT .* FROM .* WHERE .* \+ "
- "query.*=.*\".*\+.*\""
- "\`SELECT.*\$\{.*\}\`"
- "String.format.*SELECT"
- "f\"SELECT.*\{.*\}\""
- "ORDER BY.*req\.params"
- "WHERE.*params\."
```

## Impact

### Lecture de Données
- Extraction de données sensibles
- Dump complet de la base
- Accès aux credentials

### Modification de Données
- UPDATE arbitraire
- Escalade de privilèges
- Modification de prix, soldes

### Suppression de Données
- DROP TABLE
- DELETE sans WHERE
- Perte de données

### Exécution de Commandes
- xp_cmdshell (SQL Server)
- INTO OUTFILE (MySQL)
- COPY TO (PostgreSQL)

## Remédiation

### 1. Prepared Statements (Recommandé)

**Principe**
- Séparation de la structure SQL et des données
- Paramètres liés après compilation de la requête
- Impossible d'altérer la structure SQL

**Implémentation**
```
✅ CORRECT :
query = "SELECT * FROM users WHERE id = ?"
executeQuery(query, [userId])

query = "UPDATE users SET name = $1 WHERE id = $2"
execute(query, [name, id])
```

### 2. ORM/Query Builder

**Avantages**
- Abstraction de la base de données
- Requêtes paramétrées par défaut
- Protection intégrée

**Attention**
- Requêtes raw SQL toujours vulnérables
- Interpolation dans raw queries dangereuse

### 3. Validation des Entrées

**Input Validation**
- Whitelist de caractères autorisés
- Type checking strict
- Longueur maximale
- Format attendu (regex)

**Sanitization**
- Échappement des caractères spéciaux SQL
- Dernière ligne de défense (pas suffisant seul)

### 4. Least Privilege

**Principe**
- Compte DB avec permissions minimales
- Pas de DROP, CREATE pour l'application
- READ-only pour queries de lecture
- Séparation des comptes par fonction

### 5. Requêtes Dynamiques Sécurisées

**Pour ORDER BY, table names**
- Whitelist stricte des valeurs autorisées
- Pas de paramètre utilisateur direct
- Mapping contrôlé

```
✅ CORRECT :
allowedSorts = ['name', 'date', 'price']
if (!allowedSorts.includes(req.query.sort))
  throw error
orderBy = req.query.sort  // sécurisé car validé
```

## Checklist d'Audit

### Recherche de Vulnérabilités
- [ ] Concaténation de strings dans requêtes SQL ?
- [ ] Interpolation de variables dans queries ?
- [ ] Paramètres utilisateur dans ORDER BY, table names ?
- [ ] Requêtes raw SQL sans paramètres ?
- [ ] Construction dynamique de WHERE clauses ?

### Validation des Correctifs
- [ ] Prepared statements utilisés partout ?
- [ ] ORM queries paramétrées ?
- [ ] Validation stricte des entrées ?
- [ ] Whitelist pour éléments dynamiques (ORDER BY) ?
- [ ] Permissions DB minimales ?

### Tests de Vulnérabilité
- [ ] Tester avec ' OR '1'='1 ?
- [ ] Tester avec UNION SELECT ?
- [ ] Tester avec time-based (SLEEP) ?
- [ ] Tester ORDER BY avec ; DROP ?

## Références

- **OWASP** : SQL Injection
- **CWE-89** : Improper Neutralization of Special Elements used in SQL Command
- **CAPEC-66** : SQL Injection

## Exemples de Code Sécurisé

### Node.js (PostgreSQL)
```
Prepared statement :
client.query('SELECT * FROM users WHERE id = $1', [userId])
```

### Python
```
Parameterized query :
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Java
```
PreparedStatement :
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
stmt.setInt(1, userId);
```

### C# / .NET
```
SqlCommand :
cmd.CommandText = "SELECT * FROM users WHERE id = @id";
cmd.Parameters.AddWithValue("@id", userId);
```
