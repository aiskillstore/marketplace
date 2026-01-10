# Data Clumps

## Définition

Groupes de données qui apparaissent toujours ensemble dans plusieurs endroits du code (paramètres de méthodes, attributs de classes).

## Signes de Détection

- Mêmes 3-4 paramètres dans plusieurs méthodes
- Groupes d'attributs toujours initialisés/utilisés ensemble
- Paramètres passés ensemble d'une méthode à l'autre
- Commentaires groupant des attributs liés
- Préfixes ou suffixes communs (userFirstName, userLastName, userEmail)
- Validation/transformation groupée de plusieurs champs

## Impact

- **Duplication** : Signature répétée
- **Maintenance** : Changements en cascade
- **Erreurs** : Risque d'oublier un paramètre
- **Compréhension** : Relation implicite
- **Cohésion** : Opportunité de modélisation manquée
- **Type safety** : Pas de garantie de cohérence

## Exemples Typiques

### Coordonnées Géographiques
```
latitude: number
longitude: number
→ Location/Coordinates Value Object
```

### Informations d'Adresse
```
street: string
city: string
postalCode: string
country: string
→ Address Value Object
```

### Plage de Dates
```
startDate: Date
endDate: Date
→ DateRange Value Object
```

### Dimensions
```
width: number
height: number
depth: number
→ Dimensions Value Object
```

### Contact
```
firstName: string
lastName: string
email: string
phone: string
→ ContactInfo Value Object
```

## Refactoring Recommandé

### Introduce Parameter Object
Créer un objet regroupant les paramètres liés

### Preserve Whole Object
Passer l'objet entier plutôt que ses attributs

### Extract Class
Créer une nouvelle classe pour les attributs groupés

### Replace Data Value with Object
Transformer le groupe en Value Object

## Avantages du Regroupement

- **Sémantique** : Nom explicite pour le concept
- **Validation** : Cohérence garantie
- **Réutilisation** : Un seul type à utiliser
- **Évolution** : Ajout de comportements facile
- **Documentation** : Intention claire
- **Type safety** : Erreurs de compilation si incomplet

## Checklist de Review

- [ ] 3+ paramètres apparaissent ensemble régulièrement ?
- [ ] Attributs toujours initialisés ensemble ?
- [ ] Paramètres passés en groupe entre méthodes ?
- [ ] Préfixes/suffixes communs sur attributs liés ?
- [ ] Validation groupée de plusieurs champs ?
- [ ] Relation conceptuelle évidente entre les données ?
- [ ] Changements simultanés de plusieurs attributs ?

## Diagnostic

### Identifier les Data Clumps

1. **Chercher les patterns** : Mêmes paramètres/attributs ensemble
2. **Compter les occurrences** : Si > 2-3 fois, c'est un clump
3. **Tester la suppression** : Si supprimer un élément rend les autres inutiles, c'est un clump
4. **Vérifier la cohésion** : Les données ont-elles un sens ensemble ?

### Questions Clés

- Ces données forment-elles un concept métier ?
- Changent-elles ensemble ?
- Sont-elles toujours valides ensemble ?
- Ont-elles un nom naturel de groupe ?

## Seuils d'Alerte

- **2-3 occurrences** : Vigilance
- **4+ occurrences** : Refactoring recommandé
- **Signature > 4 paramètres** : Refactoring urgent

## Exceptions Acceptables

- Paramètres techniques indépendants
- Configurations avec options variées
- APIs publiques stables (breaking change)
- Performance critique (overhead objet)

## Bénéfices Long Terme

- Facilite l'ajout de nouvelles méthodes sur le groupe
- Permet d'ajouter des invariants métier
- Réduit le nombre de paramètres des méthodes
- Améliore la lisibilité des signatures
- Centralise la validation
