# Detailed Examples by Dimension

## Table of Contents
- [1. 命名问题](#1-命名问题)
- [2. 函数问题](#2-函数问题)
- [3. 重复问题](#3-重复问题)
- [4. 过度设计](#4-过度设计)
- [5. 魔法数字](#5-魔法数字)

---

## 1. 命名问题

### 无意义命名

```typescript
// ❌ 
const list = getUsers();           // list of what?
const flag = checkPermission();    // what flag?
const handler = () => {};          // handles what?

// ✅ 
const activeUsers = getUsers();
const hasEditPermission = checkPermission();
const onFormSubmit = () => {};
```

### 命名不一致

```typescript
// ❌ 同一概念多种命名
getUserData();
fetchUserInfo();
retrieveUserProfile();

// ✅ 统一使用一种
getUser();
getUserProfile();
getUserSettings();
```

### 布尔命名

```typescript
// ❌ 
const open = true;
const disabled = false;

// ✅ 带 is/has/can/should 前缀
const isOpen = true;
const isDisabled = false;
const hasPermission = true;
const canEdit = true;
```

---

## 2. 函数问题

### 函数过长

```typescript
// ❌ 160 行的 processOrder 函数
async function processOrder(order) {
  // 验证逻辑 (40 行)
  // 计算逻辑 (30 行)
  // 库存检查 (25 行)
  // 支付处理 (35 行)
  // 通知发送 (30 行)
}

// ✅ 拆分为单一职责函数
async function processOrder(order) {
  await validateOrder(order);
  const total = calculateTotal(order);
  await checkInventory(order.items);
  await processPayment(order, total);
  await sendNotifications(order);
}
```

### 参数过多

```typescript
// ❌ 
function createUser(name, email, age, address, phone, role, department, manager) {}

// ✅ 使用配置对象
interface CreateUserParams {
  name: string;
  email: string;
  profile: { age: number; phone: string };
  organization: { role: string; department: string; manager: string };
}
function createUser(params: CreateUserParams) {}
```

### 副作用

```typescript
// ❌ 函数名暗示只读，但有副作用
function getUser(id) {
  const user = db.find(id);
  user.lastAccess = new Date();  // 副作用！
  db.save(user);                  // 副作用！
  return user;
}

// ✅ 分离读写
function getUser(id) {
  return db.find(id);
}

function recordUserAccess(id) {
  const user = db.find(id);
  user.lastAccess = new Date();
  db.save(user);
}
```

---

## 3. 重复问题

### 相似的验证逻辑

```typescript
// ❌ 重复的验证模式
function validateUser(user) {
  if (!user.name) throw new Error('Name required');
  if (!user.email) throw new Error('Email required');
  if (!user.age) throw new Error('Age required');
}

function validateProduct(product) {
  if (!product.name) throw new Error('Name required');
  if (!product.price) throw new Error('Price required');
  if (!product.sku) throw new Error('SKU required');
}

// ✅ 提取通用验证器
function validateRequired(obj, fields) {
  for (const field of fields) {
    if (!obj[field]) throw new Error(`${field} required`);
  }
}

validateRequired(user, ['name', 'email', 'age']);
validateRequired(product, ['name', 'price', 'sku']);
```

### 相似的错误处理

```typescript
// ❌ 重复的 try-catch 模式
async function fetchUsers() {
  try {
    return await api.get('/users');
  } catch (e) {
    logger.error('Failed to fetch users', e);
    throw new ApiError('Failed to fetch users');
  }
}

async function fetchProducts() {
  try {
    return await api.get('/products');
  } catch (e) {
    logger.error('Failed to fetch products', e);
    throw new ApiError('Failed to fetch products');
  }
}

// ✅ 提取通用包装器
async function apiCall(endpoint, errorMessage) {
  try {
    return await api.get(endpoint);
  } catch (e) {
    logger.error(errorMessage, e);
    throw new ApiError(errorMessage);
  }
}

const users = await apiCall('/users', 'Failed to fetch users');
const products = await apiCall('/products', 'Failed to fetch products');
```

---

## 4. 过度设计

### 无用的抽象层

```typescript
// ❌ 只有一个实现的接口
interface IUserRepository {
  findById(id: string): User;
}

class UserRepository implements IUserRepository {
  findById(id: string): User { /* ... */ }
}

// ✅ 直接使用类，需要时再抽象
class UserRepository {
  findById(id: string): User { /* ... */ }
}
```

### 过度防御

```typescript
// ❌ 过度防御的代码
function add(a, b) {
  if (typeof a !== 'number') throw new Error('a must be number');
  if (typeof b !== 'number') throw new Error('b must be number');
  if (isNaN(a)) throw new Error('a is NaN');
  if (isNaN(b)) throw new Error('b is NaN');
  if (!isFinite(a)) throw new Error('a is not finite');
  if (!isFinite(b)) throw new Error('b is not finite');
  return a + b;
}

// ✅ 合理的类型安全 (TypeScript)
function add(a: number, b: number): number {
  return a + b;
}
```

### 从未使用的配置

```typescript
// ❌ 
if (config.enableNewFeature) {  // 一直是 true
  newFeature();
} else {
  oldFeature();  // 死代码
}

// ✅ 删除死代码
newFeature();
```

---

## 5. 魔法数字

### 业务逻辑中的数字

```typescript
// ❌ 
if (user.age >= 18) {}
if (order.total > 100) {}
if (retryCount < 3) {}

// ✅ 
const LEGAL_AGE = 18;
const FREE_SHIPPING_THRESHOLD = 100;
const MAX_RETRY_ATTEMPTS = 3;

if (user.age >= LEGAL_AGE) {}
if (order.total > FREE_SHIPPING_THRESHOLD) {}
if (retryCount < MAX_RETRY_ATTEMPTS) {}
```

### 时间常量

```typescript
// ❌ 
setTimeout(fn, 86400000);  // 这是多久？
setInterval(poll, 300000); // 这是多久？

// ✅ 
const ONE_DAY_MS = 24 * 60 * 60 * 1000;
const FIVE_MINUTES_MS = 5 * 60 * 1000;

setTimeout(fn, ONE_DAY_MS);
setInterval(poll, FIVE_MINUTES_MS);
```

### HTTP 状态码

```typescript
// ❌ 
if (response.status === 200) {}
if (response.status === 404) {}

// ✅ 
const HTTP_OK = 200;
const HTTP_NOT_FOUND = 404;
// 或使用常量库: import { StatusCodes } from 'http-status-codes';
```
