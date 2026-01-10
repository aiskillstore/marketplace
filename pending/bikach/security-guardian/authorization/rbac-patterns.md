# Role-Based Access Control (RBAC)

## Définition

Contrôle d'accès basé sur les rôles attribués aux utilisateurs.

## Sévérité

🔴 **CRITIQUE** - Accès non autorisé, escalade privilèges

## Composants RBAC

### Roles

```
Groupement de permissions
Exemples : admin, editor, viewer, moderator
```

### Permissions

```
Actions spécifiques autorisées
Exemples : read, write, delete, publish
```

### Resources

```
Objets protégés
Exemples : documents, articles, users
```

## Modèle

### Simple RBAC

```
User → Role → Permissions
User "john" → Role "editor" → [read, write]
```

### Hiérarchie de Rôles

```
Admin
  ├─ Manager
  │   └─ Employee
  └─ Moderator

Admin hérite toutes permissions
```

## Implémentation

### Attribution Rôles

**Principe Least Privilege**
```
✅ Rôle minimum nécessaire
✅ Révision régulière
✅ Expiration temporaire (consultants)
❌ Pas de "super-admin" par défaut
```

**Séparation des Devoirs**
```
Éviter conflits d'intérêt :
- Créateur ≠ Approbateur
- Developer ≠ Déployeur production
```

### Vérification Permissions

**Chaque Requête**
```
1. Authentifier utilisateur
2. Récupérer rôles utilisateur
3. Vérifier permissions requises
4. Autoriser ou refuser
5. Log décision
```

**Où Vérifier**
```
✅ Backend (obligatoire)
✅ API gateway
⚠️ Frontend (UX uniquement, pas sécurité)
```

### Granularité

**Resource-Level**
```
Permission sur resource spécifique
Ex: edit article #123
```

**Action-Level**
```
Permission sur action
Ex: publish, delete, approve
```

**Field-Level**
```
Permission sur champs
Ex: voir email, modifier salaire
```

## Checklist d'Audit

### Modèle
- [ ] Rôles clairement définis ?
- [ ] Permissions granulaires ?
- [ ] Hiérarchie si nécessaire ?
- [ ] Least privilege respecté ?

### Implémentation
- [ ] Vérification backend toutes requêtes ?
- [ ] Pas de bypass possible ?
- [ ] Logs accès ?
- [ ] Séparation devoirs critiques ?

### Gestion
- [ ] Attribution rôles contrôlée ?
- [ ] Révision périodique ?
- [ ] Révocation accès départ ?

## Erreurs Courantes

### ❌ Frontend-Only Checks
Backend doit toujours vérifier

### ❌ Hardcoded Roles
user.role === 'admin' partout

### ❌ God Role
Super-admin avec tout accès

### ❌ Pas de Logs
Impossible auditer accès

## Références

- **NIST** : RBAC Models
- **OWASP** : Authorization Cheat Sheet
