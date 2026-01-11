# Language-Specific Patterns

## Table of Contents
- [TypeScript/JavaScript](#typescriptjavascript)
- [Python](#python)
- [Go](#go)

---

## TypeScript/JavaScript

### any 类型滥用

```typescript
// ❌ 
function process(data: any) {
  return data.value;
}

// ✅ 
interface DataPayload {
  value: string;
}
function process(data: DataPayload) {
  return data.value;
}
```

### 回调地狱

```typescript
// ❌ 
getUser(id, (user) => {
  getOrders(user.id, (orders) => {
    processOrders(orders, (result) => {
      sendNotification(result, () => {
        console.log('done');
      });
    });
  });
});

// ✅ 
const user = await getUser(id);
const orders = await getOrders(user.id);
const result = await processOrders(orders);
await sendNotification(result);
```

### 可选链缺失

```typescript
// ❌ 
if (user && user.profile && user.profile.address && user.profile.address.city) {}

// ✅ 
if (user?.profile?.address?.city) {}
```

### 解构赋值

```typescript
// ❌ 
const name = user.name;
const email = user.email;
const age = user.age;

// ✅ 
const { name, email, age } = user;
```

---

## Python

### 列表推导滥用

```python
# ❌ 过于复杂的列表推导
result = [x.value for x in items if x.is_valid and x.type == 'A' for y in x.children if y.active]

# ✅ 拆分为函数
def get_active_children(items):
    for item in items:
        if item.is_valid and item.type == 'A':
            for child in item.children:
                if child.active:
                    yield child.value

result = list(get_active_children(items))
```

### 可变默认参数

```python
# ❌ 危险！可变对象作为默认参数
def add_item(item, items=[]):
    items.append(item)
    return items

# ✅ 
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 裸 except

```python
# ❌ 
try:
    risky_operation()
except:
    pass

# ✅ 
try:
    risky_operation()
except SpecificError as e:
    logger.warning(f"Operation failed: {e}")
```

### 字符串拼接

```python
# ❌ 
message = "Hello " + name + "! You have " + str(count) + " messages."

# ✅ 
message = f"Hello {name}! You have {count} messages."
```

### 类型提示缺失

```python
# ❌ 
def process(data):
    return data['value']

# ✅ 
from typing import TypedDict

class DataPayload(TypedDict):
    value: str

def process(data: DataPayload) -> str:
    return data['value']
```

---

## Go

### 忽略错误

```go
// ❌ 
result, _ := someFunction()

// ✅ 
result, err := someFunction()
if err != nil {
    return fmt.Errorf("someFunction failed: %w", err)
}
```

### 过长的 init 函数

```go
// ❌ init() 做太多事
func init() {
    // 数据库连接
    // 配置加载
    // 缓存初始化
    // 日志设置
    // 100+ 行...
}

// ✅ 拆分职责
func init() {
    initConfig()
    initLogger()
}

func main() {
    db := initDatabase()
    cache := initCache()
    // ...
}
```

### 空接口滥用

```go
// ❌ 
func process(data interface{}) {
    v := data.(map[string]interface{})
    // ...
}

// ✅ 
type Payload struct {
    Value string `json:"value"`
}

func process(data Payload) {
    // 类型安全
}
```

### 过深嵌套

```go
// ❌ 
func process(order *Order) error {
    if order != nil {
        if order.Items != nil {
            if len(order.Items) > 0 {
                for _, item := range order.Items {
                    if item.Valid {
                        // 实际逻辑
                    }
                }
            }
        }
    }
    return nil
}

// ✅ 早返回 (Guard Clauses)
func process(order *Order) error {
    if order == nil {
        return nil
    }
    if order.Items == nil || len(order.Items) == 0 {
        return nil
    }
    for _, item := range order.Items {
        if !item.Valid {
            continue
        }
        // 实际逻辑
    }
    return nil
}
```

### context 滥用

```go
// ❌ 用 context 传业务数据
ctx = context.WithValue(ctx, "user", user)
ctx = context.WithValue(ctx, "order", order)

// ✅ context 只用于取消和超时，业务数据显式传递
func processOrder(ctx context.Context, user User, order Order) error {
    // ...
}
```
