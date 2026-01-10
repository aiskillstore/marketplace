# 中间件使用指南

中间件是 Gin 框架的核心功能,Darkit Gin 提供了丰富的内置中间件和灵活的自定义机制。

## 中间件基础

### 什么是中间件?

中间件是在请求到达处理器之前或之后执行的函数,用于:
- 请求预处理(认证、日志、限流等)
- 响应后处理(CORS、压缩等)
- 错误处理和恢复

### 中间件执行顺序

```go
全局中间件 → 路由组中间件 → 路由级中间件 → 处理器
```

## 应用中间件

### 1. 全局中间件

```go
router := gin.Default()

// 应用到所有路由
router.Use(LoggerMiddleware())
router.Use(RecoveryMiddleware())
router.Use(CORSMiddleware())

router.GET("/ping", handlePing)  // 会经过所有全局中间件
```

### 2. 路由组中间件

```go
router := gin.Default()

// 仅应用到 /api 组
api := router.Group("/api")
api.Use(AuthMiddleware())
{
    api.GET("/users", listUsers)
    api.GET("/posts", listPosts)
}

// 不会经过 AuthMiddleware
router.GET("/public", handlePublic)
```

### 3. 路由级中间件

```go
router := gin.Default()

// 仅应用到单个路由
router.GET("/admin",
    adminHandler,
    AuthMiddleware(),      // 先认证
    RequireRole("admin"),  // 再检查角色
)
```

## 内置中间件

### 1. 请求 ID 中间件

```go
router := gin.NewRouter(
    gin.WithRequestID(),
)

// 在处理器中获取
router.GET("/", func(c *gin.Context) {
    requestID := c.GetString("request_id")
    c.Success(gin.H{"request_id": requestID})
})
```

### 2. 超时中间件

```go
router := gin.NewRouter(
    gin.WithTimeout(30 * time.Second),
)

// 超过 30 秒会自动取消请求
```

### 3. 限流中间件

```go
router := gin.NewRouter(
    gin.WithRateLimit(100),  // 100 次/分钟
)
```

### 4. CORS 中间件

```go
router := gin.NewRouter(
    gin.WithCORS(
        "http://localhost:3000",
        "https://example.com",
    ),
)
```

### 5. 认证中间件

```go
// JWT 认证
router := gin.NewRouter(
    gin.WithJWT("your-secret-key"),
)

protected := router.Group("/api")
protected.Use(func(c *gin.Context) {
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }
    c.Set("user_id", jwt["user_id"])
    c.Next()
})

// OAuth 认证
protected.Use(router.RequireAuth())

// 角色检查
admin := router.Group("/admin")
admin.Use(router.RequireRoles("admin"))
```

## 自定义中间件

### 基础结构

```go
func MyMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 请求前处理
        log.Printf("请求开始: %s %s", c.Request.Method, c.Request.URL.Path)

        // 调用下一个中间件/处理器
        c.Next()

        // 请求后处理
        log.Printf("请求结束: 状态码 %d", c.Writer.Status())
    }
}

// 使用
router.Use(MyMiddleware())
```

### 中断请求

```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")

        if token == "" {
            c.Unauthorized("缺少认证令牌")
            c.Abort()  // 中断后续处理
            return
        }

        // 验证令牌...
        c.Next()
    }
}
```

### 共享数据

```go
func UserMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := extractUserID(c)

        // 存储数据供后续使用
        c.Set("user_id", userID)

        c.Next()
    }
}

// 在处理器中获取
func handleProfile(c *gin.Context) {
    userID := c.GetInt("user_id")
    // ...
}
```

## 常用中间件示例

### 1. 日志中间件

```go
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        c.Next()

        latency := time.Since(start)
        statusCode := c.Writer.Status()
        clientIP := c.ClientIP()

        log.Printf("[%s] %s %s %d %v",
            method,
            path,
            clientIP,
            statusCode,
            latency,
        )
    }
}
```

### 2. 恢复中间件

```go
func RecoveryMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("Panic 恢复: %v", err)
                c.ServerError("服务器内部错误")
            }
        }()

        c.Next()
    }
}
```

### 3. 认证中间件

```go
func JWTAuthMiddleware(secret string) gin.HandlerFunc {
    return func(c *gin.Context) {
        jwt, ok := c.RequireJWT()
        if !ok {
            return  // RequireJWT 已处理错误
        }

        // 将用户信息存入 Context
        c.Set("user_id", jwt["user_id"])
        c.Set("username", jwt["username"])
        c.Set("role", jwt["role"])

        c.Next()
    }
}
```

### 4. 角色检查中间件

```go
func RequireRole(role string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole := c.GetString("role")

        if userRole != role {
            c.Forbidden("权限不足")
            c.Abort()
            return
        }

        c.Next()
    }
}

// 使用
router.GET("/admin", adminHandler, RequireRole("admin"))
```

### 5. 限流中间件

```go
import "golang.org/x/time/rate"

func RateLimitMiddleware(rps int) gin.HandlerFunc {
    limiter := rate.NewLimiter(rate.Limit(rps), rps)

    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.Fail("请求过于频繁")
            c.Abort()
            return
        }
        c.Next()
    }
}
```

### 6. CORS 中间件

```go
func CORSMiddleware(allowOrigins ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        origin := c.GetHeader("Origin")

        // 检查来源
        allowed := false
        for _, o := range allowOrigins {
            if o == "*" || o == origin {
                allowed = true
                break
            }
        }

        if !allowed {
            c.AbortWithStatus(http.StatusForbidden)
            return
        }

        c.Header("Access-Control-Allow-Origin", origin)
        c.Header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type,Authorization")
        c.Header("Access-Control-Allow-Credentials", "true")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(http.StatusNoContent)
            return
        }

        c.Next()
    }
}
```

### 7. 请求体大小限制

```go
func RequestSizeLimit(maxSize int64) gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxSize)
        c.Next()
    }
}

// 使用: 限制为 5MB
router.Use(RequestSizeLimit(5 * 1024 * 1024))
```

### 8. API 版本控制

```go
func VersionMiddleware(version string) gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Set("api_version", version)
        c.Header("X-API-Version", version)
        c.Next()
    }
}

// 使用
v1 := router.Group("/api/v1")
v1.Use(VersionMiddleware("1.0.0"))

v2 := router.Group("/api/v2")
v2.Use(VersionMiddleware("2.0.0"))
```

### 9. 缓存中间件

```go
func CacheMiddleware(ttl time.Duration) gin.HandlerFunc {
    cache := make(map[string]cachedResponse)
    mu := sync.RWMutex{}

    return func(c *gin.Context) {
        // 只缓存 GET 请求
        if c.Request.Method != "GET" {
            c.Next()
            return
        }

        key := c.Request.URL.Path

        mu.RLock()
        cached, found := cache[key]
        mu.RUnlock()

        if found && time.Now().Before(cached.ExpiresAt) {
            // 返回缓存数据
            c.JSON(cached.StatusCode, cached.Data)
            c.Abort()
            return
        }

        // 拦截响应
        writer := &responseWriter{
            ResponseWriter: c.Writer,
            body:          bytes.NewBuffer(nil),
        }
        c.Writer = writer

        c.Next()

        // 缓存响应
        if c.Writer.Status() == 200 {
            mu.Lock()
            cache[key] = cachedResponse{
                StatusCode: c.Writer.Status(),
                Data:       writer.body.Bytes(),
                ExpiresAt:  time.Now().Add(ttl),
            }
            mu.Unlock()
        }
    }
}
```

### 10. 安全头中间件

```go
func SecurityHeadersMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Strict-Transport-Security", "max-age=31536000")
        c.Header("Content-Security-Policy", "default-src 'self'")
        c.Next()
    }
}
```

## 中间件组合

### 链式组合

```go
// 定义中间件组
func APIMiddlewares() []gin.HandlerFunc {
    return []gin.HandlerFunc{
        LoggerMiddleware(),
        RecoveryMiddleware(),
        CORSMiddleware("*"),
        RateLimitMiddleware(100),
    }
}

// 应用
router.Use(APIMiddlewares()...)
```

### 条件中间件

```go
func ConditionalMiddleware(condition bool, middleware gin.HandlerFunc) gin.HandlerFunc {
    if condition {
        return middleware
    }
    return func(c *gin.Context) {
        c.Next()
    }
}

// 使用
isDev := os.Getenv("ENV") == "development"
router.Use(ConditionalMiddleware(isDev, DebugMiddleware()))
```

## 最佳实践

### ✅ 按顺序注册中间件

```go
router := gin.Default()

// 1. 日志(最先)
router.Use(LoggerMiddleware())

// 2. 恢复(捕获panic)
router.Use(RecoveryMiddleware())

// 3. CORS(跨域)
router.Use(CORSMiddleware())

// 4. 认证(需要时)
router.Use(AuthMiddleware())

// 5. 限流(防滥用)
router.Use(RateLimitMiddleware(100))
```

### ✅ 避免在中间件中修改请求体

```go
// ❌ 错误
func BadMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        body, _ := io.ReadAll(c.Request.Body)
        // 请求体已被读取,后续处理器无法读取
        c.Next()
    }
}

// ✅ 正确
func GoodMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        body, _ := io.ReadAll(c.Request.Body)
        // 重新设置请求体
        c.Request.Body = io.NopCloser(bytes.NewBuffer(body))
        c.Next()
    }
}
```

### ✅ 使用 Context 共享数据

```go
// ✅ 正确
func Middleware1(c *gin.Context) {
    c.Set("key", "value")
    c.Next()
}

func Middleware2(c *gin.Context) {
    value := c.GetString("key")
    // 使用 value...
    c.Next()
}
```

### ✅ 正确使用 Abort

```go
// ✅ 正确
func AuthMiddleware(c *gin.Context) {
    if !isAuthenticated(c) {
        c.Unauthorized("未登录")
        c.Abort()  // 停止后续处理
        return
    }
    c.Next()
}
```

## 错误处理

### 统一错误处理中间件

```go
func ErrorHandlerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        // 检查是否有错误
        if len(c.Errors) > 0 {
            err := c.Errors.Last()

            log.Printf("请求错误: %v", err)

            // 根据错误类型返回适当响应
            switch err.Type {
            case gin.ErrorTypeBind:
                c.ValidationError(gin.H{"error": err.Error()})
            default:
                c.ServerError("服务器内部错误")
            }
        }
    }
}
```

## 性能优化

### 缓存中间件实例

```go
// ✅ 好的做法: 缓存中间件实例
var (
    loggerMiddleware   = LoggerMiddleware()
    recoveryMiddleware = RecoveryMiddleware()
)

func setupRouter() *gin.Engine {
    router := gin.Default()
    router.Use(loggerMiddleware)
    router.Use(recoveryMiddleware)
    return router
}
```

### 避免重复计算

```go
func ExpensiveMiddleware() gin.HandlerFunc {
    // 在中间件外部初始化(只执行一次)
    cache := initializeCache()
    config := loadConfig()

    return func(c *gin.Context) {
        // 使用预初始化的资源
        data := cache.Get(c.Request.URL.Path)
        // ...
        c.Next()
    }
}
```

## 相关文档

- [快速入门](./quick-start.md) - 中间件基础使用
- [JWT 认证](./jwt-auth.md) - JWT 认证中间件详解
- [API 参考](./api-reference.md) - 中间件相关 API
