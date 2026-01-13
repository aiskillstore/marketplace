# Primitive Obsession

## Définition

Utilisation excessive de types primitifs (string, number, boolean, etc.) au lieu de Value Objects pour représenter des concepts métier.

## Signes de Détection

- Strings pour emails, URLs, codes postaux, numéros de téléphone
- Numbers pour montants, quantités, identifiants
- Booleans multiples pour représenter un état
- Validation répétée des mêmes types de données
- Logique métier dispersée
- Paramètres multiples de même type primitif
- Commentaires expliquant le format attendu

## Impact

- **Validation** : Répétée dans plusieurs endroits
- **Invariants métier** : Pas garantis
- **Type safety** : Pas de vérification à la compilation
- **Documentation** : Sémantique implicite
- **Erreurs** : Permutation de paramètres facile
- **Maintenance** : Changements de règles difficiles
- **Compréhension** : Intention du code floue

## Concepts Métier Typiques

### Identifiants
- UserId, OrderId, ProductId
- Au lieu de : string, number

### Coordonnées
- Email, PhoneNumber, Address
- Au lieu de : string

### Valeurs monétaires
- Money, Price, Amount
- Au lieu de : number

### Quantités
- Quantity, Weight, Distance
- Au lieu de : number

### Dates et Périodes
- DateRange, BusinessDay, Duration
- Au lieu de : Date, number

### Codes et Références
- PostalCode, SKU, IBAN
- Au lieu de : string

## Refactoring Recommandé

### Replace Data Value with Object
Créer un Value Object encapsulant le primitif et sa logique

### Introduce Parameter Object
Grouper les paramètres primitifs liés

### Replace Type Code with Class
Remplacer les codes/enums primitifs par des classes

## Avantages des Value Objects

- **Validation centralisée** : Une seule fois, dans le constructeur
- **Invariants garantis** : Impossible de créer un objet invalide
- **Sémantique claire** : Le type exprime l'intention
- **Type safety** : Pas de confusion entre types
- **Logique métier** : Méthodes de comportement encapsulées
- **Immutabilité** : Sécurité et prévisibilité

## Checklist de Review

- [ ] Strings utilisés pour concepts métier (email, phone, etc.) ?
- [ ] Numbers pour montants, quantités avec logique métier ?
- [ ] Validation répétée des mêmes types de données ?
- [ ] Paramètres multiples du même type primitif ?
- [ ] Commentaires expliquant le format des données ?
- [ ] Logique de validation/transformation dispersée ?
- [ ] Possibilité de permuter des paramètres sans erreur de compilation ?

## Caractéristiques d'un Value Object

- Immutable
- Validation dans le constructeur
- Égalité par valeur (pas par référence)
- Pas d'identité propre
- Méthodes de comportement métier
- Serializable si nécessaire

## Seuils d'Alerte

- **1-2 validations** : Vigilance
- **3+ validations identiques** : Refactoring recommandé
- **Logique métier sur primitif** : Refactoring urgent

## Exceptions Acceptables

- DTOs de transport pur (API, DB)
- Paramètres techniques (timeout, retry, etc.)
- Configurations simples
- Performance critique justifiée
