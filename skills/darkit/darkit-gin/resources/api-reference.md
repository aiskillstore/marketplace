# API 速查表

快速查找 Darkit Gin 框架的所有 API 方法。

## Context API

### 响应方法

#### 成功响应

| 方法 | 状态码 | 说明 | 示例 |
|------|--------|------|------|
| `Success(data)` | 200 | 成功响应 | `c.Success(user)` |
| `Created(data)` | 201 | 创建成功 | `c.Created(newUser)` |
| `Accepted(data)` | 202 | 已接受处理 | `c.Accepted("任务已提交")` |
| `NoContent()` | 204 | 无内容 | `c.NoContent()` |

#### 错误响应

| 方法 | 状态码 | 说明 | 示例 |
|------|--------|------|------|
| `Fail(message)` | 400 | 业务失败 | `c.Fail("余额不足")` |
| `ValidationError(errors)` | 400 | 验证错误 | `c.ValidationError(gin.H{"name": "必填"})` |
| `Unauthorized(message)` | 401 | 未授权 | `c.Unauthorized("请先登录")` |
| `Forbidden(message)` | 403 | 禁止访问 | `c.Forbidden("无权访问")` |
| `NotFound(message)` | 404 | 资源不存在 | `c.NotFound("用户不存在")` |
| `ServerError(message)` | 500 | 服务器错误 | `c.ServerError("系统异常")` |

#### 特殊响应

| 方法 | 说明 | 示例 |
|------|------|------|
| `Paginated(data, page, size, total)` | 分页响应 | `c.Paginated(users, 1, 10, 100)` |
| `PaginateResponse(fetch)` | 自动分页查询 | `c.PaginateResponse(func(page,size int) (interface{}, int64) { ... })` |
| `StreamFile(path, filename)` | 文件下载 | `c.StreamFile("./data.pdf", "report.pdf")` |

### 请求处理

#### 参数提取

| 方法 | 说明 | 示例 |
|------|------|------|
| `Param(key, [default])` | 智能参数提取 | `id := c.Param("id")` |
| `ParamInt(key, [default])` | 整数参数提取 | `page := c.ParamInt("page", 1)` |
| `Query(key)` | 查询参数 | `name := c.Query("name")` |
| `DefaultQuery(key, def)` | 查询参数（带默认值） | `page := c.DefaultQuery("page", "1")` |
| `PostForm(key)` | 表单参数 | `title := c.PostForm("title")` |
| `RequireParams(keys...)` | 必填参数验证 | `if !c.RequireParams("name", "email") { return }` |

#### 请求信息

| 方法 | 说明 | 示例 |
|------|------|------|
| `Method()` | 请求方法 | `method := c.Method()` |
| `Host()` | 主机名 | `host := c.Host()` |
| `Scheme()` | 协议 | `scheme := c.Scheme()` |
| `URL()` | 完整 URL | `url := c.URL()` |
| `IsSSL()` | 是否 HTTPS | `if c.IsSSL() { ... }` |
| `IsAjax()` | 是否 AJAX 请求 | `if c.IsAjax() { ... }` |
| `GetIP()` | 客户端 IP | `ip := c.GetIP()` |
| `GetUserAgent()` | User-Agent | `ua := c.GetUserAgent()` |

### 数据绑定

| 方法 | 说明 | 示例 |
|------|------|------|
| `BindJSON(obj)` | 绑定 JSON（自动验证） | `if !c.BindJSON(&user) { return }` |
| `BindQuery(obj)` | 绑定查询参数 | `if !c.BindQuery(&filter) { return }` |
| `BindAndValidate(obj)` | 绑定并验证 | `if !c.BindAndValidate(&data) { return }` |
| `Validate(obj)` | 验证对象 | `if !c.Validate(user) { return }` |

### JWT 认证

| 方法 | 说明 | 示例 |
|------|------|------|
| `CreateJWTSession(secret, ttl, payload)` | 创建 JWT | `token, _ := c.CreateJWTSession("key", 2*time.Hour, data)` |
| `RequireJWT()` | 验证并获取 JWT | `jwt, ok := c.RequireJWT()` |
| `GetJWTPayload()` | 获取 JWT 载荷 | `payload := c.GetJWTPayload()` |
| `RefreshJWTSession(secret, ttl)` | 刷新 JWT | `newToken, _ := c.RefreshJWTSession("key", 2*time.Hour)` |
| `ClearJWT()` | 清除 JWT Cookie | `c.ClearJWT()` |
| `AuthInfo()` | 解析当前用户信息 | `info, ok := c.AuthInfo()` |
| `HasRole(role)` | 是否包含指定角色 | `if !c.HasRole("admin") { ... }` |

### OAuth 方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `GenerateTokens(claims, config)` | 生成 OAuth 令牌 | `tokens, _ := c.GenerateTokens(userClaims)` |

### 缓存操作

#### 基础缓存

| 方法 | 说明 | 示例 |
|------|------|------|
| `GetCache()` | 获取缓存实例 | `cache := c.GetCache()` |
| `cache.Get(key)` | 获取缓存 | `value, found := cache.Get("key")` |
| `cache.Set(key, value, ttl)` | 设置缓存 | `cache.Set("key", value, 5*time.Minute)` |
| `cache.SetWithTTL(key, value, ttl)` | 设置缓存（指定TTL） | `cache.SetWithTTL("key", value, time.Hour)` |
| `cache.Delete(key)` | 删除缓存 | `cache.Delete("key")` |
| `cache.Clear()` | 清空所有缓存 | `cache.Clear()` |

#### 列表缓存

| 方法 | 说明 | 示例 |
|------|------|------|
| `cache.SetList(key, ttl)` | 创建列表缓存 | `cache.SetList("queue", 10*time.Minute)` |
| `cache.LPush(key, values...)` | 左侧插入 | `cache.LPush("queue", "task1", "task2")` |
| `cache.RPush(key, values...)` | 右侧插入 | `cache.RPush("queue", "task3")` |
| `cache.LPop(key)` | 左侧弹出 | `value, _ := cache.LPop("queue")` |
| `cache.RPop(key)` | 右侧弹出 | `value, _ := cache.RPop("queue")` |
| `cache.LRange(key, start, stop)` | 范围获取 | `list := cache.LRange("queue", 0, -1)` |
| `cache.LLen(key)` | 列表长度 | `length := cache.LLen("queue")` |

## Router API

### 路由注册

#### 标准 HTTP 方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `GET(path, handlers...)` | GET 路由 | `router.GET("/users", listUsers)` |
| `POST(path, handlers...)` | POST 路由 | `router.POST("/users", createUser)` |
| `PUT(path, handlers...)` | PUT 路由 | `router.PUT("/users/:id", updateUser)` |
| `DELETE(path, handlers...)` | DELETE 路由 | `router.DELETE("/users/:id", deleteUser)` |
| `PATCH(path, handlers...)` | PATCH 路由 | `router.PATCH("/users/:id", patchUser)` |
| `Any(path, handlers...)` | 所有方法 | `router.Any("/webhook", handleWebhook)` |

#### 快捷路由

| 方法 | 说明 | 示例 |
|------|------|------|
| `CRUD(prefix, handler)` | CRUD 路由组 | `router.CRUD("users", &UserResource{})` |
| `REST(resource, handler, opts...)` | REST 路由 | `router.REST("projects", ctrl)` |
| `API(version)` | API 版本路由组 | `v1 := router.API("v1")` |
| `Upload(path, handler)` | 文件上传路由 | `router.Upload("/upload", uploadHandler)` |
| `Health(path...)` | 健康检查端点 | `router.Health()` |
| `Metrics(path...)` | 监控端点 | `router.Metrics()` |

### 中间件管理

| 方法 | 说明 | 示例 |
|------|------|------|
| `Use(middlewares...)` | 添加中间件 | `router.Use(logger, recovery)` |
| `RequireAuth(scopes...)` | OAuth 认证中间件 | `router.GET("/api/data", handler, router.RequireAuth())` |
| `RequireRoles(roles...)` | 要求具备全部角色 | `router.GET("/admin", handler, router.RequireRoles("admin"))` |
| `RequireAnyRole(roles...)` | 任一角色即可 | `router.GET("/ops", handler, router.RequireAnyRole("ops","sre"))` |

### 配置选项

#### 初始化选项

| 方法 | 说明 | 示例 |
|------|------|------|
| `Default()` | 默认路由器 | `router := gin.Default()` |
| `NewRouter(options...)` | 选项式路由器 | `router := gin.NewRouter(gin.WithJWT("key"))` |

#### 配置选项

| 方法 | 说明 | 示例 |
|------|------|------|
| `WithGinMode(mode)` | 设置模式 | `gin.WithGinMode("release")` |
| `WithJWT(secret)` | 启用 JWT | `gin.WithJWT("secret-key")` |
| `WithCache(config)` | 启用缓存 | `gin.WithCache(&cache.Config{TTL: 1*time.Hour})` |
| `WithSSE(config)` | 启用 SSE | `gin.WithSSE(&sse.Config{HistorySize: 1000})` |
| `WithOpenAPI(spec)` | 启用 OpenAPI | `gin.WithOpenAPI(&gin.OpenAPI{Title: "API"})` |
| `WithCORS(origins...)` | 启用 CORS | `gin.WithCORS("http://localhost:3000")` |
| `WithRateLimit(rpm)` | 启用限流 | `gin.WithRateLimit(100)` |
| `WithRequestID()` | 启用请求ID | `gin.WithRequestID()` |
| `WithTimeout(duration)` | 设置超时 | `gin.WithTimeout(30*time.Second)` |

### 辅助方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `Run(addr)` | 启动服务器 | `router.Run(":8080")` |
| `OAuth()` | 添加 OAuth 端点 | `router.OAuth()` |
| `JWTAuthRoutes(config)` | 注册JWT认证路由 | `router.JWTAuthRoutes(gin.JWTAuthRoutesConfig{...})` |
| `GetSSEHub()` | 获取 SSE Hub | `hub := router.GetSSEHub()` |
| `EnableSwagger(path)` | 启用 Swagger UI | `router.EnableSwagger("/swagger")` |

## OpenAPI 文档选项

### 基础文档选项

| 方法 | 说明 | 示例 |
|------|------|------|
| `Summary(text)` | 摘要 | `gin.Summary("获取用户列表")` |
| `Description(text)` | 描述 | `gin.Description("返回所有用户信息")` |
| `Tags(tags...)` | 标签 | `gin.Tags("User Management")` |

### 参数选项

| 方法 | 说明 | 示例 |
|------|------|------|
| `PathParam(name, type, desc)` | 路径参数 | `gin.PathParam("id", "int", "用户ID")` |
| `QueryParam(name, type, desc, required)` | 查询参数 | `gin.QueryParam("page", "int", "页码", false)` |
| `Header(name, type, desc, required)` | 请求头 | `gin.Header("X-Request-ID", "string", "请求ID", false)` |

### 请求和响应

| 方法 | 说明 | 示例 |
|------|------|------|
| `ReqBody[T]()` | 泛型请求体 | `gin.ReqBody[CreateUserRequest]()` |
| `Resp[T](code)` | 泛型响应 | `gin.Resp[User](200)` |
| `Response(code, example)` | 响应示例 | `gin.Response(200, User{})` |

### 安全选项

| 方法 | 说明 | 示例 |
|------|------|------|
| `BearerAuth()` | Bearer 认证 | `gin.BearerAuth()` |
| `BasicAuth()` | Basic 认证 | `gin.BasicAuth()` |

## 常用模式速查

### 标准 CRUD 操作

```go
// 列表
router.GET("/users", func(c *gin.Context) {
    c.Success(getAllUsers())
})

// 详情
router.GET("/users/:id", func(c *gin.Context) {
    id := c.ParamInt("id")
    user := getUser(id)
    if user == nil {
        c.NotFound("用户不存在")
        return
    }
    c.Success(user)
})

// 创建
router.POST("/users", func(c *gin.Context) {
    var user User
    if !c.BindJSON(&user) {
        return
    }
    c.Created(createUser(user))
})

// 更新
router.PUT("/users/:id", func(c *gin.Context) {
    id := c.ParamInt("id")
    var user User
    if !c.BindJSON(&user) {
        return
    }
    c.Success(updateUser(id, user))
})

// 删除
router.DELETE("/users/:id", func(c *gin.Context) {
    id := c.ParamInt("id")
    deleteUser(id)
    c.NoContent()
})
```

### 分页查询

```go
router.GET("/users", func(c *gin.Context) {
    page := c.ParamInt("page", 1)
    size := c.ParamInt("size", 10)

    users, total := queryUsers(page, size)
    c.Paginated(users, int64(page), int64(size), int64(total))
})
```

### JWT 认证流程

```go
// 登录
router.POST("/login", func(c *gin.Context) {
    var req LoginRequest
    if !c.BindJSON(&req) {
        return
    }

    user := authenticate(req.Username, req.Password)
    if user == nil {
        c.Unauthorized("用户名或密码错误")
        return
    }

    token, _ := c.CreateJWTSession("secret", 2*time.Hour, gin.H{
        "user_id": user.ID,
        "role": user.Role,
    })

    c.Success(gin.H{"token": token})
})

// 认证中间件
func AuthMiddleware(c *gin.Context) {
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }
    c.Set("user_id", jwt["user_id"])
    c.Next()
}

// 受保护路由
protected := router.Group("/api")
protected.Use(AuthMiddleware)
{
    protected.GET("/profile", getProfile)
}
```

### 缓存使用

```go
router.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    cacheKey := "user:" + id

    cache := c.GetCache()

    // 尝试缓存
    if user, found := cache.Get(cacheKey); found {
        c.Success(user)
        return
    }

    // 查询数据库
    user := getUserFromDB(id)

    // 设置缓存
    cache.SetWithTTL(cacheKey, user, 5*time.Minute)

    c.Success(user)
})
```

## 完整配置示例

```go
router := gin.NewRouter(
    // 基础配置
    gin.WithGinMode("release"),

    // JWT 认证
    gin.WithJWT(os.Getenv("JWT_SECRET")),

    // 缓存系统
    gin.WithCache(&cache.Config{
        TTL: 30 * time.Minute,
        CleanupInterval: 5 * time.Minute,
    }),

    // SSE 实时通信
    gin.WithSSE(&sse.Config{
        HistorySize: 1000,
        PingInterval: 30 * time.Second,
    }),

    // OpenAPI 文档
    gin.WithOpenAPI(&gin.OpenAPI{
        Title: "My API",
        Version: "1.0.0",
    }),

    // CORS 配置
    gin.WithCORS("https://example.com", "https://app.example.com"),

    // 安全配置
    gin.WithSecurityConfig(func(sec *gin.SecurityConfig) {
        sec.RateLimitRequestsPerMinute = 200
        sec.SensitiveFilter = true
    }),

    // 通用配置
    gin.WithConfig(func(cfg *gin.Config) {
        cfg.ErrorHandlerEnabled = true
    }),

    // 中间件
    gin.WithRateLimit(1000),
    gin.WithRequestID(),
    gin.WithTimeout(30*time.Second),
)
```
