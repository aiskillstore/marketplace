# Exemples Bad vs Good - Refactoring

## 1. Primitive Obsession → Value Object

### ❌ Bad : Primitives Partout

```
Structure:
  email: string
  password: string

Validation répétée dans:
  - Controller
  - Use Case
  - Repository
  - Partout où l'email est utilisé

Problèmes:
  - Duplication de validation
  - Pas de garantie de validité
  - Logique dispersée
```

### ✅ Good : Value Objects

```
Structure:
  email: Email (Value Object)
  password: Password (Value Object)

Email Value Object:
  - Validation dans constructeur
  - Impossible de créer Email invalide
  - Logique métier centralisée
  - Immutable

Avantages:
  - Validation unique
  - Type safety
  - Logique encapsulée
  - Intent claire
```

## 2. God Class → Responsabilités Séparées

### ❌ Bad : UserService fait tout

```
UserService:
  - createUser()
  - updateUser()
  - deleteUser()
  - sendWelcomeEmail()
  - generateReport()
  - exportToCsv()
  - validateUser()
  - hashPassword()
  - checkPermissions()

Problèmes:
  - Trop de responsabilités
  - Violation SRP
  - Difficile à tester
  - Changements fréquents
```

### ✅ Good : Use Cases Séparés

```
CreateUserUseCase:
  - Responsabilité: créer utilisateur
  - Dépendances: UserRepository, EmailGateway, PasswordHasher

UpdateUserUseCase:
  - Responsabilité: modifier utilisateur

DeleteUserUseCase:
  - Responsabilité: supprimer utilisateur

UserReportService:
  - Responsabilité: reporting utilisateurs

Avantages:
  - Une responsabilité par classe
  - Testabilité accrue
  - Changements isolés
```

## 3. Violation DIP → Inversion de Dépendance

### ❌ Bad : Dépendance Concrète

```
CreateUserUseCase:
  constructor() {
    this.repository = new PostgresUserRepository()
    this.emailService = new SendGridService()
  }

Problèmes:
  - Couplage fort
  - Impossible de tester sans DB/Email
  - Changement d'implémentation = changement use case
  - Domain dépend de l'infrastructure
```

### ✅ Good : Injection d'Abstractions

```
CreateUserUseCase:
  constructor(
    userRepository: IUserRepository,
    emailGateway: IEmailGateway
  ) {
    this.userRepository = userRepository
    this.emailGateway = emailGateway
  }

Configuration:
  bind(IUserRepository → PostgresUserRepository)
  bind(IEmailGateway → SendGridGateway)

Avantages:
  - Use case dépend des abstractions
  - Tests avec mocks faciles
  - Changement d'implémentation sans impact use case
  - Inversion respectée
```

## 4. Feature Envy → Move Method

### ❌ Bad : Logique au Mauvais Endroit

```
OrderService:
  calculateTotal(order) {
    total = 0
    for item in order.getItems():
      price = item.getPrice()
      quantity = item.getQuantity()
      discount = item.getDiscount()
      total += (price * quantity) - discount
    return total
  }

Problèmes:
  - OrderService connaît trop Item
  - Logique de calcul Item dans Order
  - Feature Envy
```

### ✅ Good : Logique Encapsulée

```
Item:
  calculateSubtotal() {
    return (this.price * this.quantity) - this.discount
  }

Order:
  calculateTotal() {
    return this.items.reduce(
      (total, item) => total + item.calculateSubtotal(),
      0
    )
  }

OrderService:
  processOrder(order) {
    total = order.calculateTotal()
    // ...
  }

Avantages:
  - Logique au bon endroit
  - Encapsulation respectée
  - Tell Don't Ask
```

## 5. Data Clumps → Parameter Object

### ❌ Bad : Paramètres Répétés

```
createAddress(street, city, postalCode, country)
updateAddress(id, street, city, postalCode, country)
validateAddress(street, city, postalCode, country)
formatAddress(street, city, postalCode, country)

Problèmes:
  - Signature répétée
  - Risque d'erreur (ordre, oubli)
  - Pas de validation groupée
  - Pas de comportement encapsulé
```

### ✅ Good : Value Object Address

```
Address (Value Object):
  - street
  - city
  - postalCode
  - country
  - validation dans constructeur
  - format()
  - isInCountry(country)

createAddress(address: Address)
updateAddress(id: string, address: Address)
validateAddress(address: Address)
formatAddress(address: Address)

Avantages:
  - Signature simplifiée
  - Validation centralisée
  - Comportement encapsulé
  - Type safety
```

## 6. Long Method → Extract Method

### ❌ Bad : Méthode Trop Longue

```
processOrder(order) {
  // Validation (10 lignes)
  if (!order.items || order.items.length === 0)
    throw error
  // ...

  // Calcul total (15 lignes)
  let total = 0
  for item in order.items
    // calculs complexes
  // ...

  // Application discount (12 lignes)
  if (order.customer.isVIP)
    // logique discount
  // ...

  // Paiement (20 lignes)
  // logique paiement complexe
  // ...

  // Notification (10 lignes)
  // envoi emails
  // ...
}

Total: 67 lignes, trop complexe
```

### ✅ Good : Méthodes Extraites

```
processOrder(order) {
  this.validateOrder(order)
  const total = this.calculateTotal(order)
  const discountedTotal = this.applyDiscount(total, order.customer)
  this.processPayment(order, discountedTotal)
  this.sendNotifications(order)
}

validateOrder(order) { ... }
calculateTotal(order) { ... }
applyDiscount(total, customer) { ... }
processPayment(order, amount) { ... }
sendNotifications(order) { ... }

Avantages:
  - Lisibilité accrue
  - Testabilité par méthode
  - Réutilisation possible
  - Intent clair
```

## 7. Switch sur Type → Polymorphisme

### ❌ Bad : Switch/If-Else

```
calculatePrice(product) {
  switch(product.type) {
    case "PHYSICAL":
      return product.basePrice + shippingCost
    case "DIGITAL":
      return product.basePrice
    case "SUBSCRIPTION":
      return product.basePrice * 12 * discount
  }
}

Problèmes:
  - Nouveau type = modifier le switch
  - Switch répété partout
  - Violation OCP
```

### ✅ Good : Polymorphisme

```
Interface Product:
  calculatePrice()

PhysicalProduct implements Product:
  calculatePrice() {
    return this.basePrice + this.shippingCost
  }

DigitalProduct implements Product:
  calculatePrice() {
    return this.basePrice
  }

SubscriptionProduct implements Product:
  calculatePrice() {
    return this.basePrice * 12 * this.discount
  }

Client:
  total = product.calculatePrice()

Avantages:
  - Nouveau type = nouvelle classe
  - Pas de modification existante
  - OCP respecté
  - Extensibilité
```

## 8. Couplage Entre Contexts → Gateway

### ❌ Bad : Import Direct

```
OrderUseCase (Order Context):
  import { UserRepository } from 'user-context/infrastructure'

  constructor(
    userRepository: UserRepository  // ← Import direct autre context
  )

Problèmes:
  - Couplage fort entre contexts
  - Dépendance sur infrastructure d'un autre context
  - Violation isolation bounded contexts
```

### ✅ Good : Gateway Interface

```
OrderUseCase (Order Context):
  import { IUserGateway } from 'domain/port'

  constructor(
    userGateway: IUserGateway  // ← Interface dans notre context
  )

IUserGateway (Order Context domain/port):
  findUserById(id: string): Promise<UserInfo>

UserGatewayAdapter (Order Context infrastructure):
  implements IUserGateway
  // Appelle User Context via API ou use case
  // Convertit en format Order Context

Avantages:
  - Isolation entre contexts
  - Pas de couplage infrastructure
  - Chaque context garde son modèle
  - Gateway peut changer implémentation
```

## 9. Anemic Domain → Rich Domain

### ❌ Bad : Entité Anémique

```
User:
  id: string
  email: string
  password: string
  createdAt: Date
  // Seulement des getters/setters

UserService:
  validateEmail(user)
  hashPassword(user)
  canLogin(user)
  // Toute la logique ici

Problèmes:
  - Entité = structure de données
  - Logique dispersée dans services
  - Pas d'encapsulation
```

### ✅ Good : Rich Domain

```
User:
  private id: UserId
  private email: Email  // Value Object
  private password: HashedPassword
  private createdAt: Date

  validateEmail(): boolean
  changePassword(newPassword: string)
  canLogin(): boolean
  isActive(): boolean
  // Comportement encapsulé

Avantages:
  - Logique avec les données
  - Encapsulation
  - Invariants garantis
  - DDD respecté
```

## 10. N+1 Queries → Eager Loading

### ❌ Bad : Requêtes en Boucle

```
orders = repository.findAll()  // 1 query

for order in orders:
  customer = customerRepo.findById(order.customerId)  // N queries
  order.customer = customer

Total: 1 + N queries
```

### ✅ Good : Eager Loading

```
orders = repository.findAllWithCustomers()  // 1 query avec JOIN

Total: 1 query

Ou:

orders = repository.findAll()  // 1 query
customerIds = orders.map(o => o.customerId)
customers = customerRepo.findByIds(customerIds)  // 1 query batch
// Associer en mémoire

Total: 2 queries
```

## Principes de Refactoring

### 1. Identifier le Smell
Quel est le problème exact ?

### 2. Choisir la Technique
Quel refactoring appliquer ?

### 3. Tests d'Abord
Assurer la couverture de tests

### 4. Petits Pas
Refactorings incrémentaux

### 5. Tester Après
Vérifier que tout fonctionne

### 6. Commit
Committer le refactoring
