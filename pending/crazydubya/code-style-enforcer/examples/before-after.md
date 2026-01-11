# Code Style: Before and After Examples

## Naming Improvements

### Example 1: Descriptive Variable Names

**Before:**
```javascript
function calc(a, b) {
  const x = a * 0.15;
  const y = b - x;
  return y;
}
```

**After:**
```javascript
function calculateTotalWithTax(subtotal, taxRate) {
  const taxAmount = subtotal * taxRate;
  const totalAmount = subtotal + taxAmount;
  return totalAmount;
}
```

### Example 2: Boolean Naming

**Before:**
```python
def check_user(user):
    active = user.status == "active"
    admin = user.role == "admin"
    return active and admin
```

**After:**
```python
def check_user(user):
    is_active = user.status == "active"
    is_admin = user.role == "admin"
    return is_active and is_admin
```

## Organization Improvements

### Example 3: Function Grouping

**Before:**
```javascript
class UserService {
  async getUser(id) { }
  async saveSettings(settings) { }
  async deleteUser(id) { }
  async updateUser(id, data) { }
  async getSettings(userId) { }
  async createUser(data) { }
}
```

**After:**
```javascript
class UserService {
  // CRUD operations
  async createUser(data) { }
  async getUser(id) { }
  async updateUser(id, data) { }
  async deleteUser(id) { }

  // Settings management
  async getSettings(userId) { }
  async saveSettings(settings) { }
}
```

### Example 4: Import Organization

**Before:**
```javascript
import { helper } from './utils/helper';
import React from 'react';
import { formatDate } from './utils/date';
import axios from 'axios';
import { UserModel } from '../models/User';
```

**After:**
```javascript
// External dependencies
import React from 'react';
import axios from 'axios';

// Internal modules
import { UserModel } from '../models/User';

// Local utilities
import { formatDate } from './utils/date';
import { helper } from './utils/helper';
```

## Consistency Improvements

### Example 5: Consistent Error Handling

**Before:**
```javascript
async function fetchUser(id) {
  try {
    return await api.get(`/users/${id}`);
  } catch (err) {
    throw err;
  }
}

async function fetchPosts(id) {
  try {
    return await api.get(`/posts/${id}`);
  } catch (error) {
    throw new Error(`Failed to fetch: ${error.message}`);
  }
}
```

**After:**
```javascript
async function fetchUser(id) {
  try {
    return await api.get(`/users/${id}`);
  } catch (error) {
    throw new Error(`Failed to fetch user ${id}: ${error.message}`);
  }
}

async function fetchPosts(userId) {
  try {
    return await api.get(`/posts?user=${userId}`);
  } catch (error) {
    throw new Error(`Failed to fetch posts for user ${userId}: ${error.message}`);
  }
}
```

### Example 6: Magic Numbers

**Before:**
```python
def process_order(order):
    if order.status == 1:
        discount = order.total * 0.10
    elif order.status == 2:
        discount = order.total * 0.20
    return order.total - discount
```

**After:**
```python
# Constants
ORDER_STATUS_REGULAR = 1
ORDER_STATUS_PREMIUM = 2
REGULAR_DISCOUNT_RATE = 0.10
PREMIUM_DISCOUNT_RATE = 0.20

def process_order(order):
    if order.status == ORDER_STATUS_REGULAR:
        discount = order.total * REGULAR_DISCOUNT_RATE
    elif order.status == ORDER_STATUS_PREMIUM:
        discount = order.total * PREMIUM_DISCOUNT_RATE
    else:
        discount = 0
    return order.total - discount
```

## Readability Improvements

### Example 7: Complex Conditionals

**Before:**
```javascript
if ((user.age >= 18 && user.verified) || (user.parent && user.parent.consent) && !user.banned && user.country !== 'XX') {
  allowAccess();
}
```

**After:**
```javascript
const isAdult = user.age >= 18 && user.verified;
const hasParentalConsent = user.parent && user.parent.consent;
const isEligible = (isAdult || hasParentalConsent);
const isNotBanned = !user.banned;
const isAllowedCountry = user.country !== 'XX';

if (isEligible && isNotBanned && isAllowedCountry) {
  allowAccess();
}
```

### Example 8: Nested Callbacks

**Before:**
```javascript
getData(id, function(err, data) {
  if (err) return handleError(err);
  process(data, function(err, result) {
    if (err) return handleError(err);
    save(result, function(err, saved) {
      if (err) return handleError(err);
      return saved;
    });
  });
});
```

**After:**
```javascript
async function handleData(id) {
  try {
    const data = await getData(id);
    const result = await process(data);
    const saved = await save(result);
    return saved;
  } catch (error) {
    handleError(error);
  }
}
```

## Documentation Improvements

### Example 9: Function Documentation

**Before:**
```javascript
// Get user
function getUser(id) {
  return db.query('SELECT * FROM users WHERE id = ?', [id]);
}
```

**After:**
```javascript
/**
 * Retrieves a user from the database by ID
 * @param {number} id - The user's unique identifier
 * @returns {Promise<User>} The user object
 * @throws {DatabaseError} If the query fails
 * @throws {NotFoundError} If user doesn't exist
 */
async function getUser(id) {
  return db.query('SELECT * FROM users WHERE id = ?', [id]);
}
```

## TypeScript Improvements

### Example 10: Type Safety

**Before:**
```typescript
function processData(data: any) {
  return data.map(item => item.value * 2);
}
```

**After:**
```typescript
interface DataItem {
  value: number;
  label: string;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value * 2);
}
```

## Pattern Consistency

### Example 11: Async/Await vs Promises

**Before (mixed):**
```javascript
function loadData() {
  return fetchUser()
    .then(user => {
      const posts = await fetchPosts(user.id);  // Mixed!
      return { user, posts };
    });
}
```

**After (consistent):**
```javascript
async function loadData() {
  const user = await fetchUser();
  const posts = await fetchPosts(user.id);
  return { user, posts };
}
```

### Example 12: String Concatenation

**Before:**
```javascript
const url = baseUrl + '/api/' + version + '/users/' + userId;
const msg = 'Hello, ' + userName + '! You have ' + count + ' messages.';
```

**After:**
```javascript
const url = `${baseUrl}/api/${version}/users/${userId}`;
const msg = `Hello, ${userName}! You have ${count} messages.`;
```
