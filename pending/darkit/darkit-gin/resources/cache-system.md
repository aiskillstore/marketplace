# 缓存系统指南

Darkit Gin 内置高性能的内存缓存系统，开箱即用。

## 快速启用

### 1. 启用缓存

```go
import "github.com/darkit/gin/cache"

router := gin.NewRouter(
    gin.WithCache(&cache.Config{
        TTL:             30 * time.Minute,  // 默认过期时间
        CleanupInterval: 5 * time.Minute,   // 清理间隔
    }),
)
```

### 2. 使用缓存

```go
router.GET("/users/:id", func(c *gin.Context) {
    userID := c.Param("id")
    cache := c.GetCache()

    // 尝试从缓存获取
    cacheKey := "user:" + userID
    if cachedUser, found := cache.Get(cacheKey); found {
        c.Success(cachedUser)
        return
    }

    // 从数据库查询
    user, err := db.GetUser(userID)
    if err != nil {
        c.ServerError("查询失败")
        return
    }

    // 存入缓存
    cache.Set(cacheKey, user)

    c.Success(user)
})
```

## 基础操作

### 设置缓存

```go
cache := c.GetCache()

// 使用默认过期时间
cache.Set("key", "value")

// 指定过期时间
cache.SetWithTTL("key", "value", 10*time.Minute)

// 永不过期
cache.SetWithTTL("key", "value", 0)
```

### 获取缓存

```go
// 获取并检查是否存在
if value, found := cache.Get("key"); found {
    // 使用 value
} else {
    // 缓存未命中
}

// 类型断言
if user, found := cache.Get("user:123"); found {
    if u, ok := user.(*User); ok {
        // 使用 u
    }
}
```

### 删除缓存

```go
// 删除单个键
cache.Delete("key")

// 删除多个键
cache.Delete("key1", "key2", "key3")

// 批量删除（通配符）
cache.DeletePattern("user:*")  // 删除所有以 user: 开头的键
```

### 清空缓存

```go
// 清空所有缓存
cache.Flush()
```

### 检查键是否存在

```go
if cache.Has("key") {
    // 键存在
}
```

## 高级功能

### 缓存穿透保护

```go
router.GET("/users/:id", func(c *gin.Context) {
    userID := c.Param("id")
    cache := c.GetCache()
    cacheKey := "user:" + userID

    // 尝试从缓存获取
    if cachedValue, found := cache.Get(cacheKey); found {
        // 检查是否是空值标记
        if cachedValue == nil {
            c.NotFound("用户不存在")
            return
        }
        c.Success(cachedValue)
        return
    }

    // 从数据库查询
    user, err := db.GetUser(userID)
    if err != nil {
        c.ServerError("查询失败")
        return
    }

    if user == nil {
        // 缓存空值，防止缓存穿透
        cache.SetWithTTL(cacheKey, nil, 5*time.Minute)
        c.NotFound("用户不存在")
        return
    }

    // 缓存正常数据
    cache.Set(cacheKey, user)
    c.Success(user)
})
```

### 缓存预热

```go
func warmupCache(router *gin.Engine) {
    cache := router.GetCache()

    // 预加载热点数据
    hotUsers := db.GetHotUsers()
    for _, user := range hotUsers {
        cache.Set("user:"+user.ID, user)
    }

    // 预加载配置
    config := loadConfig()
    cache.Set("app:config", config)

    log.Println("缓存预热完成")
}
```

### 缓存更新策略

#### Cache-Aside (旁路缓存)

```go
// 读取
func getUser(c *gin.Context, userID string) (*User, error) {
    cache := c.GetCache()
    cacheKey := "user:" + userID

    // 1. 尝试从缓存读取
    if cached, found := cache.Get(cacheKey); found {
        return cached.(*User), nil
    }

    // 2. 缓存未命中，从数据库读取
    user, err := db.GetUser(userID)
    if err != nil {
        return nil, err
    }

    // 3. 写入缓存
    cache.Set(cacheKey, user)

    return user, nil
}

// 更新
func updateUser(c *gin.Context, userID string, data *UpdateUserRequest) error {
    // 1. 更新数据库
    err := db.UpdateUser(userID, data)
    if err != nil {
        return err
    }

    // 2. 删除缓存
    cache := c.GetCache()
    cache.Delete("user:" + userID)

    return nil
}
```

#### Write-Through (写穿)

```go
func updateUser(c *gin.Context, userID string, data *UpdateUserRequest) error {
    // 1. 更新数据库
    user, err := db.UpdateUser(userID, data)
    if err != nil {
        return err
    }

    // 2. 同时更新缓存
    cache := c.GetCache()
    cache.Set("user:"+userID, user)

    return nil
}
```

#### Write-Behind (写回)

```go
// 异步写入数据库
var writeQueue = make(chan *WriteTask, 1000)

func updateUser(c *gin.Context, userID string, data *UpdateUserRequest) error {
    cache := c.GetCache()

    // 1. 立即更新缓存
    user := applyUpdate(data)
    cache.Set("user:"+userID, user)

    // 2. 异步写入数据库
    writeQueue <- &WriteTask{
        Type:   "update_user",
        UserID: userID,
        Data:   user,
    }

    return nil
}

// 后台写入任务
func backgroundWriter() {
    for task := range writeQueue {
        db.UpdateUser(task.UserID, task.Data)
    }
}
```

## 缓存模式

### 1. 单对象缓存

```go
// 缓存单个用户
func getUser(c *gin.Context, id string) (*User, error) {
    cache := c.GetCache()
    key := "user:" + id

    if cached, found := cache.Get(key); found {
        return cached.(*User), nil
    }

    user, err := db.GetUser(id)
    if err != nil {
        return nil, err
    }

    cache.Set(key, user)
    return user, nil
}
```

### 2. 列表缓存

```go
// 缓存用户列表
func listUsers(c *gin.Context, page, size int) ([]User, error) {
    cache := c.GetCache()
    key := fmt.Sprintf("users:page:%d:size:%d", page, size)

    if cached, found := cache.Get(key); found {
        return cached.([]User), nil
    }

    users, err := db.ListUsers(page, size)
    if err != nil {
        return nil, err
    }

    // 缓存 5 分钟
    cache.SetWithTTL(key, users, 5*time.Minute)
    return users, nil
}
```

### 3. 查询结果缓存

```go
// 缓存查询结果
func searchUsers(c *gin.Context, query string) ([]User, error) {
    cache := c.GetCache()
    key := "search:" + query

    if cached, found := cache.Get(key); found {
        return cached.([]User), nil
    }

    users, err := db.SearchUsers(query)
    if err != nil {
        return nil, err
    }

    cache.SetWithTTL(key, users, 10*time.Minute)
    return users, nil
}
```

### 4. 聚合数据缓存

```go
// 缓存统计数据
func getStatistics(c *gin.Context) (*Statistics, error) {
    cache := c.GetCache()
    key := "stats:daily"

    if cached, found := cache.Get(key); found {
        return cached.(*Statistics), nil
    }

    stats, err := db.CalculateStatistics()
    if err != nil {
        return nil, err
    }

    // 缓存到当天结束
    tomorrow := time.Now().Add(24 * time.Hour).Truncate(24 * time.Hour)
    ttl := time.Until(tomorrow)
    cache.SetWithTTL(key, stats, ttl)

    return stats, nil
}
```

## 缓存失效

### 主动失效

```go
// 更新用户时删除相关缓存
func updateUser(c *gin.Context, userID string, data *UpdateUserRequest) error {
    cache := c.GetCache()

    // 更新数据库
    err := db.UpdateUser(userID, data)
    if err != nil {
        return err
    }

    // 删除单个用户缓存
    cache.Delete("user:" + userID)

    // 删除用户列表缓存
    cache.DeletePattern("users:page:*")

    // 删除搜索结果缓存
    cache.DeletePattern("search:*")

    return nil
}
```

### 被动失效（TTL）

```go
// 短期缓存：频繁变化的数据
cache.SetWithTTL("hot:news", news, 1*time.Minute)

// 中期缓存：较稳定的数据
cache.SetWithTTL("user:profile", profile, 30*time.Minute)

// 长期缓存：很少变化的数据
cache.SetWithTTL("config:app", config, 24*time.Hour)
```

## 性能优化

### 批量操作

```go
// 批量获取用户
func batchGetUsers(c *gin.Context, userIDs []string) ([]*User, error) {
    cache := c.GetCache()
    users := make([]*User, 0, len(userIDs))
    missingIDs := make([]string, 0)

    // 1. 先从缓存获取
    for _, id := range userIDs {
        if cached, found := cache.Get("user:" + id); found {
            users = append(users, cached.(*User))
        } else {
            missingIDs = append(missingIDs, id)
        }
    }

    // 2. 批量查询缓存未命中的数据
    if len(missingIDs) > 0 {
        dbUsers, err := db.BatchGetUsers(missingIDs)
        if err != nil {
            return nil, err
        }

        // 3. 写入缓存
        for _, user := range dbUsers {
            cache.Set("user:"+user.ID, user)
            users = append(users, user)
        }
    }

    return users, nil
}
```

### 缓存压缩

```go
import (
    "bytes"
    "compress/gzip"
    "encoding/json"
)

// 压缩大对象
func setCacheCompressed(cache *cache.Cache, key string, value interface{}) error {
    // 序列化
    data, err := json.Marshal(value)
    if err != nil {
        return err
    }

    // 压缩
    var buf bytes.Buffer
    w := gzip.NewWriter(&buf)
    w.Write(data)
    w.Close()

    // 存储
    cache.Set(key, buf.Bytes())
    return nil
}

// 解压读取
func getCacheCompressed(cache *cache.Cache, key string, dest interface{}) error {
    cached, found := cache.Get(key)
    if !found {
        return errors.New("cache miss")
    }

    // 解压
    buf := bytes.NewReader(cached.([]byte))
    r, err := gzip.NewReader(buf)
    if err != nil {
        return err
    }
    defer r.Close()

    // 反序列化
    return json.NewDecoder(r).Decode(dest)
}
```

### 分片缓存

```go
// 大列表分片缓存
func cacheUserList(cache *cache.Cache, users []User) {
    const shardSize = 100

    for i := 0; i < len(users); i += shardSize {
        end := i + shardSize
        if end > len(users) {
            end = len(users)
        }

        shard := users[i:end]
        key := fmt.Sprintf("users:shard:%d", i/shardSize)
        cache.Set(key, shard)
    }
}
```

## 监控和调试

### 缓存统计

```go
router.GET("/cache/stats", func(c *gin.Context) {
    cache := c.GetCache()

    stats := gin.H{
        "total_keys":  cache.Count(),
        "memory_size": cache.Size(),
    }

    c.Success(stats)
})
```

### 查看缓存键

```go
router.GET("/cache/keys", func(c *gin.Context) {
    cache := c.GetCache()

    keys := cache.Keys()

    c.Success(gin.H{
        "total": len(keys),
        "keys":  keys,
    })
})
```

### 清理过期缓存

```go
// 手动触发清理
router.POST("/cache/cleanup", func(c *gin.Context) {
    cache := c.GetCache()
    cache.Cleanup()

    c.Success(gin.H{"message": "清理完成"})
})
```

## 最佳实践

### ✅ 使用有意义的缓存键

```go
// ✅ 好的做法
cache.Set("user:123", user)
cache.Set("users:page:1:size:10", users)
cache.Set("search:golang:page:1", results)

// ❌ 不好的做法
cache.Set("u123", user)
cache.Set("data", users)
```

### ✅ 设置合理的过期时间

```go
// ✅ 根据数据特性设置 TTL
cache.SetWithTTL("hot:news", news, 1*time.Minute)      // 热点新闻
cache.SetWithTTL("user:profile", profile, 30*time.Minute)  // 用户信息
cache.SetWithTTL("config", config, 24*time.Hour)       // 配置
```

### ✅ 防止缓存穿透

```go
// ✅ 缓存空值
if user == nil {
    cache.SetWithTTL(key, nil, 5*time.Minute)
}
```

### ✅ 及时清理相关缓存

```go
// ✅ 更新时清理关联缓存
func updateUser(userID string) {
    db.UpdateUser(userID, data)

    cache.Delete("user:" + userID)
    cache.DeletePattern("users:*")
    cache.DeletePattern("search:*")
}
```

### ✅ 避免缓存大对象

```go
// ✅ 缓存关键数据
cache.Set("user:"+id, &UserCache{
    ID:       user.ID,
    Username: user.Username,
    Role:     user.Role,
})

// ❌ 避免缓存完整对象
cache.Set("user:"+id, user)  // user 包含大量冗余数据
```

## 常见问题

### Q1: 缓存和数据库不一致怎么办?

**答**: 使用 Cache-Aside 模式，更新时删除缓存:

```go
func updateUser(userID string, data *UpdateUserRequest) error {
    // 1. 更新数据库
    err := db.UpdateUser(userID, data)
    if err != nil {
        return err
    }

    // 2. 删除缓存
    cache.Delete("user:" + userID)

    return nil
}
```

### Q2: 如何防止缓存雪崩?

**答**: 设置随机过期时间:

```go
// 基础 TTL + 随机时间
baseTTL := 30 * time.Minute
randomTTL := time.Duration(rand.Intn(300)) * time.Second
cache.SetWithTTL(key, value, baseTTL+randomTTL)
```

### Q3: 缓存占用内存过大怎么办?

**答**:
1. 设置合理的 TTL
2. 只缓存必要数据
3. 使用压缩
4. 考虑使用 Redis 等外部缓存

## 相关文档

- [快速入门](./quick-start.md) - 缓存基础使用
- [API 参考](./api-reference.md) - 缓存相关 API
- [性能优化](./performance.md) - 缓存优化策略
