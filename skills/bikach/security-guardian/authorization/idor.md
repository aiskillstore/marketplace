# Insecure Direct Object Reference (IDOR)

## Définition

Accès direct à des objets via identifiant sans vérification d'autorisation.

## Sévérité

🔴 **CRITIQUE** - Accès données non autorisées

## Exemples d'Attaque

```
GET /api/users/123/profile
→ Changer 123 en 456
→ Accès profil autre utilisateur

GET /documents/5432
→ Énumération documents
→ Accès sans autorisation
```

## Vulnérabilité

### Patterns Vulnérables

```
❌ /api/users/{id} sans check ownership
❌ /orders/{orderId} sans vérifier user
❌ /files/{filename} accès direct
❌ IDs séquentiels prévisibles
```

## Remédiation

### 1. Vérification Autorisation

**Toujours Vérifier**
```
✅ User a droit d'accès à la resource
✅ Sur chaque endpoint
✅ Backend obligatoire
```

**Process**
```
1. Authentifier utilisateur
2. Récupérer resource par ID
3. Vérifier ownership/permissions
4. Si autorisé → retourner data
5. Sinon → 403 Forbidden
```

### 2. IDs Non-Prévisibles

**UUIDs**
```
✅ UUID v4 : 128 bits aléatoires
✅ Difficile deviner/énumérer
Exemple : 550e8400-e29b-41d4-a716-446655440000
```

**Hashids**
```
✅ Encoder ID séquentiel
✅ Non-séquentiel en apparence
⚠️ Pas sécurité seule, toujours vérifier ownership
```

### 3. Indirect Reference Map

**Mapping**
```
Session map :
user_resources = {
  "abc123": real_resource_id_456,
  "def456": real_resource_id_789
}

User accède via "abc123" (non prévisible)
Backend map vers resource réelle
```

### 4. Access Control Lists

**Explicite**
```
Table permissions :
user_id | resource_id | permission
123     | doc_456     | read
123     | doc_789     | write
```

## Checklist d'Audit

### Endpoints
- [ ] Tous endpoints vérifient ownership ?
- [ ] Pas d'accès direct sans check ?
- [ ] IDs prévisibles remplacés ?
- [ ] Tests énumération effectués ?

### Vérification
- [ ] Backend vérifie autorisation ?
- [ ] Pas de confiance client-side ?
- [ ] 403 si non autorisé ?
- [ ] Logs accès non autorisés ?

## Tests

```
✅ Tester avec ID autre user
✅ Tester énumération (ID +1, -1)
✅ Tester sans authentification
✅ Tester avec rôle insuffisant
```

## Références

- **OWASP** : Insecure Direct Object References
- **CWE-639** : Authorization Bypass Through User-Controlled Key
