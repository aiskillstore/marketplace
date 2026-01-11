# JWT 认证完整指南

Darkit Gin 内置完整的 JWT 认证系统，开箱即用。

## 快速启用

### 1. 启用 JWT 支持

```go
router := gin.NewRouter(
    gin.WithJWT("your-super-secret-key"),  // 从环境变量读取更安全
)
```

### 2. 实现登录接口

```go
type LoginRequest struct {
    Username string `json:"username" binding:"required"`
    Password string `json:"password" binding:"required"`
}

router.POST("/login", func(c *gin.Context) {
    var req LoginRequest
    if !c.BindJSON(&req) {
        return
    }

    // 验证用户名和密码（从数据库查询）
    user, err := userService.Authenticate(req.Username, req.Password)
    if err != nil {
        c.Unauthorized("用户名或密码错误")
        return
    }

    // 生成 JWT 令牌
    token, err := c.CreateJWTSession("your-secret-key", 2*time.Hour, gin.H{
        "user_id": user.ID,
        "username": user.Username,
        "role": user.Role,
    })

    if err != nil {
        c.ServerError("生成令牌失败")
        return
    }

    c.Success(gin.H{
        "token": token,
        "expires_in": 7200,  // 2小时
        "user": user,
    })
})
```

## 认证中间件

### 基础认证中间件

```go
func AuthMiddleware(c *gin.Context) {
    // 验证 JWT 并获取载荷
    jwt, ok := c.RequireJWT()
    if !ok {
        return  // RequireJWT 已自动返回 401
    }

    // 将用户信息存入 Context
    c.Set("user_id", jwt["user_id"])
    c.Set("username", jwt["username"])
    c.Set("role", jwt["role"])

    c.Next()
}
```

### 应用到路由组

```go
// 公开路由
router.POST("/login", handleLogin)
router.POST("/register", handleRegister)

// 受保护的路由
api := router.Group("/api")
api.Use(AuthMiddleware)
{
    api.GET("/profile", getProfile)
    api.PUT("/profile", updateProfile)
    api.GET("/orders", listOrders)
}
```

## 角色权限控制

### 使用内置角色中间件

```go
// 要求具备所有指定角色
admin := router.Group("/admin")
admin.Use(router.RequireAuth(), router.RequireRoles("admin"))
{
    admin.GET("/users", listUsers)
    admin.DELETE("/users/:id", deleteUser)
}

// 任一角色即可访问
ops := router.Group("/ops")
ops.Use(router.RequireAuth(), router.RequireAnyRole("admin", "ops", "sre"))
{
    ops.GET("/logs", viewLogs)
    ops.POST("/deploy", triggerDeploy)
}
```

### 自定义权限检查

```go
func RequirePermission(permission string) gin.HandlerFunc {
    return func(c *gin.Context) {
        jwt, ok := c.RequireJWT()
        if !ok {
            return
        }

        userID := jwt["user_id"]
        if !userService.HasPermission(userID, permission) {
            c.Forbidden("无权访问")
            c.Abort()
            return
        }

        c.Next()
    }
}

// 使用
router.DELETE("/users/:id", deleteUser, RequirePermission("user:delete"))
```

## 令牌刷新

```go
router.POST("/refresh", func(c *gin.Context) {
    // 验证当前令牌
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }

    // 生成新令牌（保持相同载荷）
    newToken, err := c.RefreshJWTSession("your-secret-key", 2*time.Hour)
    if err != nil {
        c.ServerError("刷新令牌失败")
        return
    }

    c.Success(gin.H{
        "token": newToken,
        "expires_in": 7200,
    })
})
```

## 用户注销

```go
router.POST("/logout", func(c *gin.Context) {
    // 清除 JWT Cookie
    c.ClearJWT()

    // 可选：将令牌加入黑名单（需要额外实现）
    if token := c.GetHeader("Authorization"); token != "" {
        blacklistService.Add(token)
    }

    c.Success(gin.H{"message": "已注销"})
})
```

## 获取当前用户信息

### 方法 1：从 Context 获取

```go
router.GET("/profile", func(c *gin.Context) {
    userID := c.GetInt("user_id")
    username := c.GetString("username")
    role := c.GetString("role")

    c.Success(gin.H{
        "user_id": userID,
        "username": username,
        "role": role,
    })
})
```

### 方法 2：使用 AuthInfo 辅助方法

```go
router.GET("/profile", func(c *gin.Context) {
    info, ok := c.AuthInfo()
    if !ok {
        c.Unauthorized("未登录")
        return
    }

    c.Success(info)
})
```

## 完整示例

```go
package main

import (
    "os"
    "time"
    "github.com/darkit/gin"
)

func main() {
    // 从环境变量读取密钥
    jwtSecret := os.Getenv("JWT_SECRET")
    if jwtSecret == "" {
        panic("JWT_SECRET is required")
    }

    router := gin.NewRouter(
        gin.WithJWT(jwtSecret),
        gin.WithCORS("http://localhost:3000"),
    )

    // 公开路由
    router.POST("/login", handleLogin)
    router.POST("/register", handleRegister)

    // 受保护的 API
    api := router.Group("/api")
    api.Use(AuthMiddleware)
    {
        api.GET("/profile", getProfile)
        api.PUT("/profile", updateProfile)
        api.POST("/logout", handleLogout)
        api.POST("/refresh", refreshToken)
    }

    // 管理员路由
    admin := router.Group("/admin")
    admin.Use(AuthMiddleware, RequireRole("admin"))
    {
        admin.GET("/users", listUsers)
        admin.DELETE("/users/:id", deleteUser)
    }

    router.Run(":8080")
}

// 登录处理
func handleLogin(c *gin.Context) {
    var req LoginRequest
    if !c.BindJSON(&req) {
        return
    }

    user, err := authenticateUser(req.Username, req.Password)
    if err != nil {
        c.Unauthorized("用户名或密码错误")
        return
    }

    token, _ := c.CreateJWTSession(
        os.Getenv("JWT_SECRET"),
        2*time.Hour,
        gin.H{
            "user_id": user.ID,
            "username": user.Username,
            "role": user.Role,
        },
    )

    c.Success(gin.H{
        "token": token,
        "user": user,
    })
}

// 认证中间件
func AuthMiddleware(c *gin.Context) {
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }
    c.Set("user_id", jwt["user_id"])
    c.Set("role", jwt["role"])
    c.Next()
}

// 角色检查中间件
func RequireRole(role string) gin.HandlerFunc {
    return func(c *gin.Context) {
        if !c.HasRole(role) {
            c.Forbidden("权限不足")
            c.Abort()
            return
        }
        c.Next()
    }
}
```

## 安全最佳实践

### ✅ 密钥管理

```go
// ✅ 正确：从环境变量读取
jwtSecret := os.Getenv("JWT_SECRET")

// ❌ 错误：硬编码密钥
jwtSecret := "hardcoded-secret"  // 危险！
```

### ✅ 设置合理的过期时间

```go
// 短期令牌：2小时
accessToken, _ := c.CreateJWTSession(secret, 2*time.Hour, payload)

// 长期刷新令牌：7天
refreshToken, _ := c.CreateJWTSession(secret, 7*24*time.Hour, payload)
```

### ✅ HTTPS 传输

```go
// 生产环境必须使用 HTTPS
router.RunTLS(":443", "cert.pem", "key.pem")
```

### ✅ 敏感操作需要重新验证

```go
router.DELETE("/account", func(c *gin.Context) {
    var req struct {
        Password string `json:"password" binding:"required"`
    }
    if !c.BindJSON(&req) {
        return
    }

    // 重新验证密码
    userID := c.GetInt("user_id")
    if !verifyPassword(userID, req.Password) {
        c.Unauthorized("密码错误")
        return
    }

    // 执行删除账户操作
    deleteAccount(userID)
    c.NoContent()
})
```

## 客户端集成

### JavaScript / TypeScript

```javascript
// 登录
const response = await fetch('http://localhost:8080/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'admin',
        password: 'password'
    })
});

const { data } = await response.json();
const token = data.token;

// 保存令牌
localStorage.setItem('token', token);

// 使用令牌访问 API
const apiResponse = await fetch('http://localhost:8080/api/profile', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

### curl 测试

```bash
# 1. 登录获取令牌
TOKEN=$(curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.data.token')

# 2. 使用令牌访问 API
curl http://localhost:8080/api/profile \
  -H "Authorization: Bearer $TOKEN"

# 3. 刷新令牌
curl -X POST http://localhost:8080/refresh \
  -H "Authorization: Bearer $TOKEN"
```

## 常见问题

### Q1: JWT 存储在哪里？

**答**: 可以存储在：
- **Cookie**（更安全，自动防御 XSS）
- **LocalStorage**（简单但需防御 XSS）
- **SessionStorage**（刷新页面会丢失）

推荐使用 **HttpOnly Cookie**：

```go
c.SetCookie("token", token, 7200, "/", "", false, true)
//                                              ↑     ↑
//                                          secure httpOnly
```

### Q2: 如何实现"记住我"功能？

**答**: 使用长期刷新令牌：

```go
// 短期访问令牌：2小时
accessToken, _ := c.CreateJWTSession(secret, 2*time.Hour, payload)

// 长期刷新令牌：7天
refreshToken, _ := c.CreateJWTSession(secret, 7*24*time.Hour, payload)

c.Success(gin.H{
    "access_token": accessToken,
    "refresh_token": refreshToken,
})
```

### Q3: 如何在令牌过期前刷新？

**答**: 客户端定时刷新或使用拦截器：

```javascript
// 定时刷新（令牌有效期前10分钟）
setInterval(async () => {
    const newToken = await refreshToken();
    localStorage.setItem('token', newToken);
}, 110 * 60 * 1000);  // 110分钟
```

## 相关文档

- [快速入门](./quick-start.md) - JWT 认证快速上手
- [API 参考](./api-reference.md) - JWT 相关 API 方法
- [OAuth 2.0 系统](./oauth.md) - OAuth 2.0 认证
- [角色权限控制](./rbac.md) - RBAC 权限管理
