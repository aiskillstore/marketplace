---
name: seed-data-generator
description: Generate realistic test data for database development, testing, and demos.
---

# Seed Data Generator Skill

Generate realistic test data for database development, testing, and demos.

## Instructions

You are a test data generation expert. When invoked:

1. **Analyze Schema**:
   - Identify tables and relationships
   - Understand column types and constraints
   - Detect foreign key dependencies
   - Recognize data patterns (email, phone, dates, etc.)

2. **Generate Realistic Data**:
   - Use faker libraries for realistic data
   - Maintain referential integrity
   - Follow business logic constraints
   - Create diverse but realistic scenarios

3. **Seed Database**:
   - Insert data in correct order (respect foreign keys)
   - Handle different database systems
   - Provide both SQL and ORM-based seeders
   - Support incremental seeding

4. **Customize Generation**:
   - Allow quantity specification
   - Support different data scenarios (edge cases, happy path)
   - Enable data relationships customization
   - Provide reproducible seeds (with random seed values)

## Supported Tools

- **JavaScript/TypeScript**: Faker.js, Chance.js, Casual
- **Python**: Faker, Factory Boy, Mimesis
- **Ruby**: Faker, FactoryBot
- **Raw SQL**: Generate INSERT statements
- **ORMs**: Prisma, TypeORM, Sequelize, Django, Rails

## Usage Examples

```
@seed-data-generator
@seed-data-generator --count 100
@seed-data-generator --table users
@seed-data-generator --scenario e-commerce
@seed-data-generator --realistic-relationships
```

## SQL Seed Data

### PostgreSQL - Basic Insert
```sql
-- seed/001_users.sql
INSERT INTO users (username, email, password_hash, active, created_at)
VALUES
  ('john_doe', 'john@example.com', '$2b$10$...', true, '2024-01-15 10:00:00'),
  ('jane_smith', 'jane@example.com', '$2b$10$...', true, '2024-01-16 11:30:00'),
  ('bob_wilson', 'bob@example.com', '$2b$10$...', true, '2024-01-17 09:15:00'),
  ('alice_brown', 'alice@example.com', '$2b$10$...', false, '2024-01-18 14:45:00'),
  ('charlie_davis', 'charlie@example.com', '$2b$10$...', true, '2024-01-19 16:20:00');

-- seed/002_categories.sql
INSERT INTO categories (name, slug, parent_id)
VALUES
  ('Electronics', 'electronics', NULL),
  ('Computers', 'computers', 1),
  ('Laptops', 'laptops', 2),
  ('Desktops', 'desktops', 2),
  ('Accessories', 'accessories', 1),
  ('Clothing', 'clothing', NULL),
  ('Men', 'men', 6),
  ('Women', 'women', 6);

-- seed/003_products.sql
INSERT INTO products (name, description, price, stock_quantity, category_id, created_at)
VALUES
  (
    'MacBook Pro 16"',
    'Powerful laptop with M3 chip, 16GB RAM, 512GB SSD',
    2499.99,
    15,
    3,
    NOW()
  ),
  (
    'Dell XPS 13',
    'Compact laptop with Intel i7, 16GB RAM, 512GB SSD',
    1299.99,
    20,
    3,
    NOW()
  ),
  (
    'Gaming Desktop',
    'High-performance desktop with RTX 4080, 32GB RAM',
    2999.99,
    8,
    4,
    NOW()
  ),
  (
    'Wireless Mouse',
    'Ergonomic wireless mouse with precision tracking',
    29.99,
    100,
    5,
    NOW()
  ),
  (
    'Mechanical Keyboard',
    'RGB mechanical keyboard with Cherry MX switches',
    149.99,
    45,
    5,
    NOW()
  );

-- seed/004_orders.sql
INSERT INTO orders (user_id, total_amount, status, created_at)
VALUES
  (1, 2529.98, 'completed', '2024-01-20 10:30:00'),
  (2, 1299.99, 'completed', '2024-01-21 14:15:00'),
  (3, 179.98, 'processing', '2024-01-22 09:45:00'),
  (1, 2999.99, 'pending', '2024-01-23 16:00:00'),
  (4, 29.99, 'completed', '2024-01-24 11:20:00');

-- seed/005_order_items.sql
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES
  -- Order 1
  (1, 1, 1, 2499.99),
  (1, 4, 1, 29.99),
  -- Order 2
  (2, 2, 1, 1299.99),
  -- Order 3
  (3, 4, 1, 29.99),
  (3, 5, 1, 149.99),
  -- Order 4
  (4, 3, 1, 2999.99),
  -- Order 5
  (5, 4, 1, 29.99);
```

### Generated Seed with Functions
```sql
-- Generate random users
CREATE OR REPLACE FUNCTION generate_users(count INTEGER)
RETURNS void AS $$
DECLARE
  i INTEGER;
BEGIN
  FOR i IN 1..count LOOP
    INSERT INTO users (username, email, password_hash, active, created_at)
    VALUES (
      'user_' || i,
      'user' || i || '@example.com',
      '$2b$10$fakehashedpassword',
      random() > 0.1, -- 90% active
      NOW() - (random() * 365 || ' days')::INTERVAL
    );
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Generate random products
CREATE OR REPLACE FUNCTION generate_products(count INTEGER)
RETURNS void AS $$
DECLARE
  i INTEGER;
  categories INTEGER[];
BEGIN
  SELECT ARRAY_AGG(id) INTO categories FROM categories;

  FOR i IN 1..count LOOP
    INSERT INTO products (name, description, price, stock_quantity, category_id, created_at)
    VALUES (
      'Product ' || i,
      'Description for product ' || i,
      (random() * 1000 + 10)::NUMERIC(10,2),
      (random() * 100)::INTEGER,
      categories[1 + floor(random() * array_length(categories, 1))::INTEGER],
      NOW() - (random() * 180 || ' days')::INTERVAL
    );
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Generate random orders
CREATE OR REPLACE FUNCTION generate_orders(count INTEGER)
RETURNS void AS $$
DECLARE
  i INTEGER;
  user_ids INTEGER[];
  product_ids INTEGER[];
  order_id INTEGER;
  item_count INTEGER;
  j INTEGER;
  total NUMERIC(10,2);
BEGIN
  SELECT ARRAY_AGG(id) INTO user_ids FROM users WHERE active = true;
  SELECT ARRAY_AGG(id) INTO product_ids FROM products WHERE stock_quantity > 0;

  FOR i IN 1..count LOOP
    -- Random number of items (1-5)
    item_count := 1 + floor(random() * 5)::INTEGER;
    total := 0;

    INSERT INTO orders (user_id, total_amount, status, created_at)
    VALUES (
      user_ids[1 + floor(random() * array_length(user_ids, 1))::INTEGER],
      0, -- Will update after adding items
      (ARRAY['pending', 'processing', 'completed', 'cancelled'])[1 + floor(random() * 4)::INTEGER],
      NOW() - (random() * 90 || ' days')::INTERVAL
    )
    RETURNING id INTO order_id;

    -- Add order items
    FOR j IN 1..item_count LOOP
      DECLARE
        product_price NUMERIC(10,2);
        quantity INTEGER;
      BEGIN
        SELECT price INTO product_price
        FROM products
        WHERE id = product_ids[1 + floor(random() * array_length(product_ids, 1))::INTEGER];

        quantity := 1 + floor(random() * 3)::INTEGER;

        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (
          order_id,
          product_ids[1 + floor(random() * array_length(product_ids, 1))::INTEGER],
          quantity,
          product_price
        );

        total := total + (product_price * quantity);
      END;
    END LOOP;

    -- Update order total
    UPDATE orders SET total_amount = total WHERE id = order_id;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT generate_users(100);
SELECT generate_products(50);
SELECT generate_orders(200);
```

## JavaScript/TypeScript Seeders

### Faker.js + Prisma
```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';
import { faker } from '@faker-js/faker';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Clear existing data
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.review.deleteMany();
  await prisma.product.deleteMany();
  await prisma.category.deleteMany();
  await prisma.user.deleteMany();

  // Create categories
  const categories = await Promise.all([
    prisma.category.create({
      data: {
        name: 'Electronics',
        slug: 'electronics',
      },
    }),
    prisma.category.create({
      data: {
        name: 'Clothing',
        slug: 'clothing',
      },
    }),
    prisma.category.create({
      data: {
        name: 'Home & Garden',
        slug: 'home-garden',
      },
    }),
  ]);

  // Create users
  const users = await Promise.all(
    Array.from({ length: 20 }, async () => {
      const firstName = faker.person.firstName();
      const lastName = faker.person.lastName();

      return prisma.user.create({
        data: {
          username: faker.internet.userName({ firstName, lastName }),
          email: faker.internet.email({ firstName, lastName }),
          passwordHash: faker.string.alphanumeric(60), // In real app, use bcrypt
          active: faker.datatype.boolean(0.9), // 90% active
          createdAt: faker.date.past({ years: 2 }),
        },
      });
    })
  );

  console.log(`Created ${users.length} users`);

  // Create products
  const products = await Promise.all(
    Array.from({ length: 50 }, async () => {
      return prisma.product.create({
        data: {
          name: faker.commerce.productName(),
          description: faker.commerce.productDescription(),
          price: parseFloat(faker.commerce.price({ min: 10, max: 2000 })),
          stockQuantity: faker.number.int({ min: 0, max: 100 }),
          categoryId: faker.helpers.arrayElement(categories).id,
          createdAt: faker.date.past({ years: 1 }),
        },
      });
    })
  );

  console.log(`Created ${products.length} products`);

  // Create orders with items
  const activeUsers = users.filter(u => u.active);

  for (let i = 0; i < 100; i++) {
    const user = faker.helpers.arrayElement(activeUsers);
    const orderProducts = faker.helpers.arrayElements(
      products,
      faker.number.int({ min: 1, max: 5 })
    );

    const orderItems = orderProducts.map(product => ({
      productId: product.id,
      quantity: faker.number.int({ min: 1, max: 3 }),
      price: product.price,
    }));

    const totalAmount = orderItems.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );

    await prisma.order.create({
      data: {
        userId: user.id,
        totalAmount,
        status: faker.helpers.arrayElement([
          'pending',
          'processing',
          'completed',
          'cancelled',
        ]),
        createdAt: faker.date.past({ years: 0.5 }),
        items: {
          create: orderItems,
        },
      },
    });
  }

  console.log('Created 100 orders with items');

  // Create reviews
  for (let i = 0; i < 150; i++) {
    const user = faker.helpers.arrayElement(activeUsers);
    const product = faker.helpers.arrayElement(products);

    // Check if user already reviewed this product
    const existingReview = await prisma.review.findFirst({
      where: {
        userId: user.id,
        productId: product.id,
      },
    });

    if (!existingReview) {
      await prisma.review.create({
        data: {
          userId: user.id,
          productId: product.id,
          rating: faker.number.int({ min: 1, max: 5 }),
          comment: faker.helpers.maybe(() => faker.lorem.paragraph(), { probability: 0.7 }),
          createdAt: faker.date.past({ years: 0.5 }),
        },
      });
    }
  }

  console.log('Created reviews');
  console.log('Seeding completed!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

```json
// package.json
{
  "prisma": {
    "seed": "ts-node prisma/seed.ts"
  }
}
```

```bash
# Run seed
npx prisma db seed
```

### TypeORM Seeder
```typescript
// src/database/seeds/user.seeder.ts
import { DataSource } from 'typeorm';
import { Seeder } from 'typeorm-extension';
import { faker } from '@faker-js/faker';
import { User } from '../entities/user.entity';
import { Order } from '../entities/order.entity';
import { Product } from '../entities/product.entity';

export default class UserSeeder implements Seeder {
  async run(dataSource: DataSource): Promise<void> {
    const userRepository = dataSource.getRepository(User);
    const productRepository = dataSource.getRepository(Product);
    const orderRepository = dataSource.getRepository(Order);

    // Create users
    const users: User[] = [];
    for (let i = 0; i < 50; i++) {
      const user = userRepository.create({
        username: faker.internet.userName(),
        email: faker.internet.email(),
        passwordHash: faker.string.alphanumeric(60),
        active: faker.datatype.boolean(0.9),
        createdAt: faker.date.past({ years: 2 }),
      });
      users.push(user);
    }
    await userRepository.save(users);

    console.log(`Seeded ${users.length} users`);

    // Create products
    const products: Product[] = [];
    for (let i = 0; i < 100; i++) {
      const product = productRepository.create({
        name: faker.commerce.productName(),
        description: faker.commerce.productDescription(),
        price: parseFloat(faker.commerce.price({ min: 10, max: 1000 })),
        stockQuantity: faker.number.int({ min: 0, max: 100 }),
        createdAt: faker.date.past({ years: 1 }),
      });
      products.push(product);
    }
    await productRepository.save(products);

    console.log(`Seeded ${products.length} products`);

    // Create orders
    const activeUsers = users.filter(u => u.active);
    const orders: Order[] = [];

    for (let i = 0; i < 200; i++) {
      const user = faker.helpers.arrayElement(activeUsers);
      const orderProducts = faker.helpers.arrayElements(
        products,
        faker.number.int({ min: 1, max: 5 })
      );

      const totalAmount = orderProducts.reduce(
        (sum, p) => sum + p.price * faker.number.int({ min: 1, max: 3 }),
        0
      );

      const order = orderRepository.create({
        user,
        totalAmount,
        status: faker.helpers.arrayElement([
          'pending',
          'processing',
          'completed',
          'cancelled',
        ]),
        createdAt: faker.date.past({ years: 0.5 }),
      });
      orders.push(order);
    }
    await orderRepository.save(orders);

    console.log(`Seeded ${orders.length} orders`);
  }
}
```

```bash
# Run seeder
npm run seed
```

## Python Seeders

### Django Fixtures
```python
# management/commands/seed.py
from django.core.management.base import BaseCommand
from faker import Faker
from app.models import User, Product, Category, Order, OrderItem
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=200,
            help='Number of orders to create'
        )

    def handle(self, *args, **options):
        fake = Faker()

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        # Create categories
        self.stdout.write('Creating categories...')
        categories = []
        category_names = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports']
        for name in category_names:
            category = Category.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-')
            )
            categories.append(category)

        # Create users
        self.stdout.write(f'Creating {options["users"]} users...')
        users = []
        for _ in range(options['users']):
            user = User.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                password_hash=fake.sha256(),
                active=fake.boolean(chance_of_getting_true=90),
                created_at=fake.date_time_this_year()
            )
            users.append(user)

        # Create products
        self.stdout.write(f'Creating {options["products"]} products...')
        products = []
        for _ in range(options['products']):
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01')),
                stock_quantity=random.randint(0, 100),
                category=random.choice(categories),
                created_at=fake.date_time_this_year()
            )
            products.append(product)

        # Create orders
        self.stdout.write(f'Creating {options["orders"]} orders...')
        active_users = [u for u in users if u.active]
        statuses = ['pending', 'processing', 'completed', 'cancelled']

        for _ in range(options['orders']):
            user = random.choice(active_users)
            order_products = random.sample(products, random.randint(1, 5))

            order = Order.objects.create(
                user=user,
                status=random.choice(statuses),
                total_amount=0,  # Will calculate
                created_at=fake.date_time_this_year()
            )

            total = Decimal('0.00')
            for product in order_products:
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total += product.price * quantity

            order.total_amount = total
            order.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
```

```bash
# Run seeder
python manage.py seed --users 100 --products 200 --orders 500
```

### Factory Boy (Python)
```python
# factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from app.models import User, Product, Category, Order, OrderItem

fake = Faker()

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password_hash = factory.Faker('sha256')
    active = factory.Faker('boolean', chance_of_getting_true=90)
    created_at = factory.Faker('date_time_this_year')

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('catch_phrase')
    description = factory.Faker('text', max_nb_chars=200)
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True, min_value=10, max_value=1000)
    stock_quantity = factory.Faker('random_int', min=0, max=100)
    category = factory.SubFactory(CategoryFactory)
    created_at = factory.Faker('date_time_this_year')

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory, active=True)
    status = factory.Faker('random_element', elements=['pending', 'processing', 'completed', 'cancelled'])
    total_amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    created_at = factory.Faker('date_time_this_year')

class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_int', min=1, max=5)
    price = factory.LazyAttribute(lambda obj: obj.product.price)

# seed_db.py
from factories import UserFactory, ProductFactory, CategoryFactory, OrderFactory, OrderItemFactory

# Create data
categories = CategoryFactory.create_batch(5)
users = UserFactory.create_batch(50)
products = ProductFactory.create_batch(100)
orders = OrderFactory.create_batch(200)

print(f'Created {len(users)} users, {len(products)} products, {len(orders)} orders')
```

## Realistic Data Scenarios

### E-Commerce Platform
```typescript
// Realistic e-commerce scenario
import { faker } from '@faker-js/faker';

// Create realistic product catalog
const productCategories = {
  electronics: [
    { name: 'MacBook Pro 16"', price: 2499, stock: 15 },
    { name: 'iPhone 15 Pro', price: 999, stock: 50 },
    { name: 'iPad Air', price: 599, stock: 30 },
    { name: 'AirPods Pro', price: 249, stock: 100 },
  ],
  clothing: [
    { name: 'Men\'s T-Shirt', price: 29.99, stock: 200 },
    { name: 'Women\'s Jeans', price: 79.99, stock: 150 },
    { name: 'Sneakers', price: 89.99, stock: 80 },
    { name: 'Winter Jacket', price: 149.99, stock: 60 },
  ],
};

// Create realistic user personas
const userPersonas = [
  {
    type: 'frequent_buyer',
    orderFrequency: 'high',
    avgOrderValue: 200,
    preferredCategories: ['electronics'],
  },
  {
    type: 'occasional_shopper',
    orderFrequency: 'medium',
    avgOrderValue: 100,
    preferredCategories: ['clothing'],
  },
  {
    type: 'bargain_hunter',
    orderFrequency: 'low',
    avgOrderValue: 50,
    preferredCategories: ['clothing', 'home'],
  },
];

// Create orders matching user behavior
function generateRealisticOrders(user, persona) {
  const orderCount = {
    high: faker.number.int({ min: 10, max: 50 }),
    medium: faker.number.int({ min: 3, max: 10 }),
    low: faker.number.int({ min: 1, max: 3 }),
  }[persona.orderFrequency];

  const orders = [];
  for (let i = 0; i < orderCount; i++) {
    const products = getProductsFromCategories(persona.preferredCategories);
    const total = calculateTotal(products, persona.avgOrderValue);

    orders.push({
      userId: user.id,
      products,
      totalAmount: total,
      status: getRealisticStatus(),
      createdAt: faker.date.past({ years: 1 }),
    });
  }

  return orders;
}

function getRealisticStatus() {
  // 80% completed, 10% processing, 5% pending, 5% cancelled
  const rand = Math.random();
  if (rand < 0.8) return 'completed';
  if (rand < 0.9) return 'processing';
  if (rand < 0.95) return 'pending';
  return 'cancelled';
}
```

### SaaS Multi-Tenant
```python
# Realistic SaaS data
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Organization sizes (realistic distribution)
ORG_SIZES = {
    'startup': {'users': (1, 5), 'projects': (1, 3), 'weight': 0.5},
    'small': {'users': (5, 20), 'projects': (3, 10), 'weight': 0.3},
    'medium': {'users': (20, 100), 'projects': (10, 50), 'weight': 0.15},
    'enterprise': {'users': (100, 500), 'projects': (50, 200), 'weight': 0.05},
}

def create_organization():
    org_type = random.choices(
        list(ORG_SIZES.keys()),
        weights=[v['weight'] for v in ORG_SIZES.values()]
    )[0]

    config = ORG_SIZES[org_type]

    org = Organization.objects.create(
        name=fake.company(),
        slug=fake.slug(),
        plan=org_type,
        created_at=fake.date_time_between(start_date='-2y', end_date='now')
    )

    # Create users for org
    user_count = random.randint(*config['users'])
    users = []
    for i in range(user_count):
        role = 'admin' if i == 0 else random.choice(['member', 'member', 'member', 'viewer'])
        user = User.objects.create(
            organization=org,
            email=fake.email(),
            name=fake.name(),
            role=role,
            created_at=org.created_at + timedelta(days=random.randint(0, 30))
        )
        users.append(user)

    # Create projects
    project_count = random.randint(*config['projects'])
    for _ in range(project_count):
        Project.objects.create(
            organization=org,
            owner=random.choice(users),
            name=fake.catch_phrase(),
            description=fake.text(),
            status=random.choice(['active', 'active', 'active', 'archived']),
            created_at=org.created_at + timedelta(days=random.randint(0, 60))
        )

    return org
```

## Best Practices

### DO ✓
- **Use realistic data** - Names, emails, addresses should look real
- **Maintain referential integrity** - Respect foreign key constraints
- **Create diverse scenarios** - Include edge cases, not just happy path
- **Set random seed for reproducibility** - `faker.seed(12345)`
- **Clear data before seeding** - Prevent duplicate key errors
- **Seed in correct order** - Parents before children
- **Use transactions** - Rollback on error
- **Add meaningful relationships** - Realistic user-order patterns
- **Include timestamps** - Spread across realistic time periods
- **Validate data** - Ensure generated data meets constraints

### DON'T ✗
- **Don't use same password for all users** - Vary or use faker
- **Don't ignore constraints** - Check NOT NULL, UNIQUE, CHECK
- **Don't create unrealistic data** - No 200-year-old users
- **Don't hardcode IDs** - Use auto-generated values
- **Don't seed production** - Only development/staging
- **Don't create too much data** - Start small, increase as needed
- **Don't ignore performance** - Use batch inserts for large datasets
- **Don't forget to cleanup** - Delete test data when done

## Performance Tips

### Batch Inserts
```typescript
// Instead of individual creates
for (const data of userData) {
  await prisma.user.create({ data });
}

// Use createMany
await prisma.user.createMany({
  data: userData,
  skipDuplicates: true,
});
```

### Transaction for Multiple Tables
```typescript
await prisma.$transaction(async (tx) => {
  const users = await tx.user.createMany({ data: userData });
  const products = await tx.product.createMany({ data: productData });
  const orders = await tx.order.createMany({ data: orderData });
});
```

## Notes

- Always seed development and staging, never production
- Use environment variables to control seed behavior
- Include seed data in version control for consistency
- Document seed scenarios for team understanding
- Consider using database snapshots for faster resets
- Test application with seeded data regularly
- Keep seed scripts up to date with schema changes
