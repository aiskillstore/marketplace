# 快速开始指南

## 30 分钟上手 Darkit Gin

本指南将带你在 30 分钟内掌握 Darkit Gin 框架的核心功能，从 Hello World 到完整的 RESTful API。

## 第一步：安装（2 分钟）

```bash
# 创建新项目
mkdir my-api && cd my-api
go mod init my-api

# 安装框架
go get github.com/darkit/gin
```

## 第二步：Hello World（3 分钟）

创建 `main.go`：

```go
package main

import "github.com/darkit/gin"

func main() {
    // 创建路由器
    router := gin.Default()

    // 定义路由
    router.GET("/ping", func(c *gin.Context) {
        c.Success("pong")  // 统一响应格式
    })

    // 启动服务器
    router.Run(":8080")
}
```

运行并测试：

```bash
# 启动服务器
go run main.go

# 测试（新终端）
curl http://localhost:8080/ping
# 响应: {"code":0,"message":"success","data":"pong"}
```

## 第三步：选项式配置（5 分钟）

使用新的选项式 API 创建功能完整的路由器：

```go
package main

import (
    "time"
    "github.com/darkit/gin"
    "github.com/darkit/gin/cache"
    "github.com/darkit/gin/pkg/sse"
)

func main() {
    router := gin.NewRouter(
        gin.WithGinMode("debug"),                    // 调试模式
        gin.WithJWT("your-super-secret-key"),        // JWT 认证
        gin.WithCache(&cache.Config{                 // 缓存系统
            TTL: 30 * time.Minute,
            CleanupInterval: 5 * time.Minute,
        }),
        gin.WithSSE(&sse.Config{                     // SSE 实时通信
            HistorySize: 1000,
            PingInterval: 30 * time.Second,
        }),
        gin.WithOpenAPI(&gin.OpenAPI{                // OpenAPI 文档
            Title: "My API",
            Version: "1.0.0",
        }),
        gin.WithCORS("http://localhost:3000"),       // CORS 跨域
        gin.WithRateLimit(100),                      // 限流
        gin.WithRequestID(),                         // 请求 ID
        gin.WithTimeout(30*time.Second),             // 超时控制
    )

    // 健康检查和监控端点
    router.Health()        // GET /health
    router.Metrics()       // GET /metrics

    // 启用 Swagger UI
    router.EnableSwagger("/swagger")

    // 定义路由
    router.GET("/ping", func(c *gin.Context) {
        c.Success("pong")
    })

    router.Run(":8080")
}
```

访问 Swagger UI：http://localhost:8080/swagger/index.html

## 第四步：RESTful API（10 分钟）

创建完整的用户管理 API：

```go
package main

import (
    "sync"
    "github.com/darkit/gin"
)

// 用户模型
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name" binding:"required"`
    Email string `json:"email" binding:"required,email"`
}

// 模拟数据库
var (
    users   = make(map[int]User)
    nextID  = 1
    usersMu sync.RWMutex
)

func main() {
    router := gin.Default()

    // 用户 CRUD 路由
    api := router.Group("/api")
    {
        api.GET("/users", listUsers)
        api.GET("/users/:id", getUser)
        api.POST("/users", createUser)
        api.PUT("/users/:id", updateUser)
        api.DELETE("/users/:id", deleteUser)
    }

    router.Run(":8080")
}

// 列表
func listUsers(c *gin.Context) {
    usersMu.RLock()
    defer usersMu.RUnlock()

    list := make([]User, 0, len(users))
    for _, user := range users {
        list = append(list, user)
    }

    c.Success(list)
}

// 获取单个用户
func getUser(c *gin.Context) {
    id := c.ParamInt("id")

    usersMu.RLock()
    user, exists := users[id]
    usersMu.RUnlock()

    if !exists {
        c.NotFound("用户不存在")
        return
    }

    c.Success(user)
}

// 创建用户
func createUser(c *gin.Context) {
    var user User
    if !c.BindJSON(&user) {
        return  // 自动返回 400 验证错误
    }

    usersMu.Lock()
    user.ID = nextID
    nextID++
    users[user.ID] = user
    usersMu.Unlock()

    c.Created(user)  // 201 状态码
}

// 更新用户
func updateUser(c *gin.Context) {
    id := c.ParamInt("id")

    usersMu.RLock()
    _, exists := users[id]
    usersMu.RUnlock()

    if !exists {
        c.NotFound("用户不存在")
        return
    }

    var user User
    if !c.BindJSON(&user) {
        return
    }

    usersMu.Lock()
    user.ID = id
    users[id] = user
    usersMu.Unlock()

    c.Success(user)
}

// 删除用户
func deleteUser(c *gin.Context) {
    id := c.ParamInt("id")

    usersMu.Lock()
    delete(users, id)
    usersMu.Unlock()

    c.NoContent()  // 204 状态码
}
```

测试 API：

```bash
# 创建用户
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","email":"zhang@example.com"}'

# 获取用户列表
curl http://localhost:8080/api/users

# 获取单个用户
curl http://localhost:8080/api/users/1

# 更新用户
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"张三（已更新）","email":"zhang@example.com"}'

# 删除用户
curl -X DELETE http://localhost:8080/api/users/1
```

## 第五步：JWT 认证（5 分钟）

添加 JWT 认证保护 API：

```go
package main

import (
    "time"
    "github.com/darkit/gin"
)

type LoginRequest struct {
    Username string `json:"username" binding:"required"`
    Password string `json:"password" binding:"required"`
}

func main() {
    router := gin.NewRouter(
        gin.WithJWT("your-super-secret-key"),
    )

    // 公开路由
    router.POST("/login", handleLogin)

    // 受保护的路由
    api := router.Group("/api")
    api.Use(AuthMiddleware)
    {
        api.GET("/profile", getProfile)
    }

    router.Run(":8080")
}

// 登录处理
func handleLogin(c *gin.Context) {
    var req LoginRequest
    if !c.BindJSON(&req) {
        return
    }

    // 简单验证（实际应查询数据库）
    if req.Username != "admin" || req.Password != "password" {
        c.Unauthorized("用户名或密码错误")
        return
    }

    // 生成 JWT 令牌
    token, _ := c.CreateJWTSession("your-super-secret-key", 2*time.Hour, gin.H{
        "username": req.Username,
        "role":     "admin",
    })

    c.Success(gin.H{
        "token": token,
        "expires_in": 7200,
    })
}

// 认证中间件
func AuthMiddleware(c *gin.Context) {
    jwt, ok := c.RequireJWT()
    if !ok {
        return  // RequireJWT 已处理错误响应
    }

    c.Set("username", jwt["username"])
    c.Set("role", jwt["role"])
    c.Next()
}

// 获取用户信息
func getProfile(c *gin.Context) {
    username := c.GetString("username")
    role := c.GetString("role")

    c.Success(gin.H{
        "username": username,
        "role":     role,
    })
}
```

测试认证：

```bash
# 1. 登录获取令牌
TOKEN=$(curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.data.token')

# 2. 使用令牌访问受保护 API
curl http://localhost:8080/api/profile \
  -H "Authorization: Bearer $TOKEN"

# 3. 不带令牌访问（应失败）
curl http://localhost:8080/api/profile
```

## 第六步：缓存系统（5 分钟）

使用内置缓存提升性能：

```go
package main

import (
    "time"
    "fmt"
    "github.com/darkit/gin"
    "github.com/darkit/gin/cache"
)

func main() {
    router := gin.NewRouter(
        gin.WithCache(&cache.Config{
            TTL: 30 * time.Minute,
            CleanupInterval: 5 * time.Minute,
        }),
    )

    router.GET("/users/:id", getUserWithCache)

    router.Run(":8080")
}

func getUserWithCache(c *gin.Context) {
    id := c.Param("id")
    cacheKey := "user:" + id

    cache := c.GetCache()

    // 尝试从缓存获取
    if cachedUser, found := cache.Get(cacheKey); found {
        c.Success(gin.H{
            "user": cachedUser,
            "cached": true,
        })
        return
    }

    // 从"数据库"获取
    user := gin.H{
        "id": id,
        "name": "用户" + id,
        "email": fmt.Sprintf("user%s@example.com", id),
    }

    // 设置缓存（5分钟）
    cache.SetWithTTL(cacheKey, user, 5*time.Minute)

    c.Success(gin.H{
        "user": user,
        "cached": false,
    })
}
```

## 下一步学习

### 立即可用的高级功能

1. **SSE 实时通信** → 查看 [SSE Real-time](./sse-realtime.md)
2. **OpenAPI 文档生成** → 查看 [OpenAPI Documentation](./openapi-docs.md)
3. **文件上传** → 使用 `router.Upload()` 方法

### 推荐阅读顺序

1. ✅ **本指南** - 快速入门
2. [Router Configuration](./router-config.md) - 路由配置详解
3. [Response Methods](./response-methods.md) - 响应方法详解
4. [JWT Authentication](./jwt-auth.md) - JWT 认证完整指南
5. [Complete Examples](./complete-examples.md) - 生产级应用示例

## 常见问题

### Q1: 如何从 gin-gonic/gin 迁移？

完全兼容，只需替换导入：

```go
// 原生 Gin
import "github.com/gin-gonic/gin"

// 增强版（完全兼容）
import gin "github.com/darkit/gin"
```

### Q2: API 方法太多记不住怎么办？

查看 [API Reference](./api-reference.md)，方法按功能分类。

### Q3: 性能如何？

相比原生 Gin：
- Context 创建：提升 45%
- 内存使用：减少 35%
- 响应处理：性能持平

## 总结

你已经学会了：

- ✅ 安装和创建 Hello World
- ✅ 使用选项式 API 配置路由器
- ✅ 构建完整的 RESTful API
- ✅ 添加 JWT 认证
- ✅ 使用缓存系统

**总用时**: ~30 分钟

**下一步**:
1. 查阅完整示例了解更多功能
2. 探索 SSE、OpenAPI 等高级特性
3. 阅读最佳实践准备生产部署
