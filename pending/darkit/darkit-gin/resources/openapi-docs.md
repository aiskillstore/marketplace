# OpenAPI 文档生成指南

Darkit Gin 支持自动生成 OpenAPI 3.0 规范的 API 文档，并提供 Swagger UI 界面。

## 快速启用

### 1. 启用 OpenAPI

```go
router := gin.NewRouter(
    gin.WithOpenAPI(&gin.OpenAPI{
        Title:       "My API",
        Version:     "1.0.0",
        Description: "API 文档描述",
    }),
)
```

### 2. 启用 Swagger UI

```go
// 在 /swagger 路径提供 Swagger UI
router.EnableSwagger("/swagger")
```

### 3. 访问文档

```bash
# OpenAPI JSON 规范
http://localhost:8080/openapi.json

# Swagger UI 界面
http://localhost:8080/swagger
```

## 完整配置

```go
router := gin.NewRouter(
    gin.WithOpenAPI(&gin.OpenAPI{
        Title:       "User Management API",
        Version:     "1.0.0",
        Description: "完整的用户管理系统 API",
        Contact: &gin.Contact{
            Name:  "API Support",
            Email: "support@example.com",
            URL:   "https://example.com/support",
        },
        License: &gin.License{
            Name: "Apache 2.0",
            URL:  "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        Servers: []gin.Server{
            {
                URL:         "https://api.example.com",
                Description: "生产环境",
            },
            {
                URL:         "https://staging-api.example.com",
                Description: "测试环境",
            },
            {
                URL:         "http://localhost:8080",
                Description: "本地开发",
            },
        },
        SecuritySchemes: map[string]gin.SecurityScheme{
            "bearerAuth": {
                Type:         "http",
                Scheme:       "bearer",
                BearerFormat: "JWT",
            },
        },
    }),
)
```

## 路由文档注解

### 基础注解

```go
router.GET("/users/:id",
    handleGetUser,
    gin.Summary("获取用户详情"),
    gin.Description("通过用户 ID 获取用户的详细信息"),
    gin.Tags("用户管理"),
)
```

### 完整注解示例

```go
router.GET("/users/:id",
    handleGetUser,
    gin.Summary("获取用户详情"),
    gin.Description("通过用户 ID 获取用户的详细信息，需要认证"),
    gin.Tags("用户管理"),
    gin.Param("id", "用户ID", "integer", true),
    gin.Response(200, "成功", &User{}),
    gin.Response(404, "用户不存在", nil),
    gin.Response(401, "未认证", nil),
    gin.Security("bearerAuth"),
)
```

## 文档注解详解

### 1. 基础信息

```go
// 摘要
gin.Summary("获取用户列表")

// 详细描述
gin.Description("分页获取系统中的所有用户信息")

// 标签（用于分组）
gin.Tags("用户管理", "查询接口")
```

### 2. 路径参数

```go
// 必需参数
gin.Param("id", "用户ID", "integer", true)

// 可选参数
gin.Param("filter", "过滤条件", "string", false)
```

### 3. 查询参数

```go
gin.Query("page", "页码", "integer", false, "1")
gin.Query("size", "每页数量", "integer", false, "10")
gin.Query("keyword", "搜索关键词", "string", false)
```

### 4. 请求体

```go
// 指定请求体模型
gin.RequestBody("用户信息", &CreateUserRequest{}, true)

// 示例
type CreateUserRequest struct {
    Username string `json:"username" binding:"required" example:"admin"`
    Email    string `json:"email" binding:"required,email" example:"admin@example.com"`
    Role     string `json:"role" binding:"required,oneof=user admin" example:"user"`
}
```

### 5. 响应

```go
// 成功响应
gin.Response(200, "成功", &User{})

// 创建成功
gin.Response(201, "创建成功", &User{})

// 错误响应
gin.Response(400, "请求参数错误", nil)
gin.Response(401, "未认证", nil)
gin.Response(404, "资源不存在", nil)
gin.Response(500, "服务器错误", nil)
```

### 6. 安全认证

```go
// 需要 JWT 认证
gin.Security("bearerAuth")

// 需要多种认证方式
gin.Security("bearerAuth", "apiKey")
```

## 完整示例

### 用户管理 API

```go
package main

import (
    "github.com/darkit/gin"
)

type User struct {
    ID        int       `json:"id" example:"1"`
    Username  string    `json:"username" example:"admin"`
    Email     string    `json:"email" example:"admin@example.com"`
    Role      string    `json:"role" example:"user"`
    CreatedAt time.Time `json:"created_at"`
}

type CreateUserRequest struct {
    Username string `json:"username" binding:"required" example:"newuser"`
    Email    string `json:"email" binding:"required,email" example:"user@example.com"`
    Password string `json:"password" binding:"required,min=8" example:"password123"`
    Role     string `json:"role" binding:"required,oneof=user admin" example:"user"`
}

type UpdateUserRequest struct {
    Email  string `json:"email" binding:"omitempty,email" example:"newemail@example.com"`
    Role   string `json:"role" binding:"omitempty,oneof=user admin" example:"admin"`
    Status string `json:"status" binding:"omitempty,oneof=active inactive" example:"active"`
}

func main() {
    router := gin.NewRouter(
        gin.WithOpenAPI(&gin.OpenAPI{
            Title:       "User Management API",
            Version:     "1.0.0",
            Description: "完整的用户管理系统 API，提供用户增删改查功能",
            Contact: &gin.Contact{
                Name:  "API Support",
                Email: "support@example.com",
            },
            SecuritySchemes: map[string]gin.SecurityScheme{
                "bearerAuth": {
                    Type:         "http",
                    Scheme:       "bearer",
                    BearerFormat: "JWT",
                },
            },
        }),
    )

    // 启用 Swagger UI
    router.EnableSwagger("/swagger")

    // 公开路由
    router.POST("/login",
        handleLogin,
        gin.Summary("用户登录"),
        gin.Description("使用用户名和密码登录，返回 JWT 令牌"),
        gin.Tags("认证"),
        gin.RequestBody("登录信息", &LoginRequest{}, true),
        gin.Response(200, "登录成功", &LoginResponse{}),
        gin.Response(401, "用户名或密码错误", nil),
    )

    // 用户管理路由
    api := router.Group("/api")
    {
        // 获取用户列表
        api.GET("/users",
            handleListUsers,
            gin.Summary("获取用户列表"),
            gin.Description("分页获取系统中的所有用户"),
            gin.Tags("用户管理"),
            gin.Query("page", "页码", "integer", false, "1"),
            gin.Query("size", "每页数量", "integer", false, "10"),
            gin.Query("keyword", "搜索关键词", "string", false),
            gin.Response(200, "成功", &UserListResponse{}),
            gin.Security("bearerAuth"),
        )

        // 获取用户详情
        api.GET("/users/:id",
            handleGetUser,
            gin.Summary("获取用户详情"),
            gin.Description("通过用户 ID 获取用户的详细信息"),
            gin.Tags("用户管理"),
            gin.Param("id", "用户ID", "integer", true),
            gin.Response(200, "成功", &User{}),
            gin.Response(404, "用户不存在", nil),
            gin.Security("bearerAuth"),
        )

        // 创建用户
        api.POST("/users",
            handleCreateUser,
            gin.Summary("创建用户"),
            gin.Description("创建一个新用户账号"),
            gin.Tags("用户管理"),
            gin.RequestBody("用户信息", &CreateUserRequest{}, true),
            gin.Response(201, "创建成功", &User{}),
            gin.Response(400, "请求参数错误", nil),
            gin.Security("bearerAuth"),
        )

        // 更新用户
        api.PUT("/users/:id",
            handleUpdateUser,
            gin.Summary("更新用户"),
            gin.Description("更新用户的邮箱、角色或状态"),
            gin.Tags("用户管理"),
            gin.Param("id", "用户ID", "integer", true),
            gin.RequestBody("更新信息", &UpdateUserRequest{}, true),
            gin.Response(200, "更新成功", &User{}),
            gin.Response(404, "用户不存在", nil),
            gin.Security("bearerAuth"),
        )

        // 删除用户
        api.DELETE("/users/:id",
            handleDeleteUser,
            gin.Summary("删除用户"),
            gin.Description("删除指定的用户账号"),
            gin.Tags("用户管理"),
            gin.Param("id", "用户ID", "integer", true),
            gin.Response(204, "删除成功", nil),
            gin.Response(404, "用户不存在", nil),
            gin.Security("bearerAuth"),
        )
    }

    router.Run(":8080")
}
```

## 数据模型注解

### 使用 struct tags

```go
type User struct {
    ID        int       `json:"id" example:"1" description:"用户ID"`
    Username  string    `json:"username" example:"admin" description:"用户名"`
    Email     string    `json:"email" example:"admin@example.com" description:"邮箱地址"`
    Role      string    `json:"role" example:"user" enums:"user,admin" description:"用户角色"`
    Status    string    `json:"status" example:"active" enums:"active,inactive" description:"账号状态"`
    CreatedAt time.Time `json:"created_at" description:"创建时间"`
}
```

### 嵌套模型

```go
type UserProfile struct {
    User      User   `json:"user"`
    Bio       string `json:"bio" example:"这是个人简介"`
    Avatar    string `json:"avatar" example:"https://example.com/avatar.jpg"`
    Location  string `json:"location" example:"北京"`
}
```

### 数组和切片

```go
type UserListResponse struct {
    Users []User `json:"users"`
    Total int64  `json:"total" example:"100"`
    Page  int    `json:"page" example:"1"`
    Size  int    `json:"size" example:"10"`
}
```

## 文档分组

### 使用标签分组

```go
// 用户管理组
router.GET("/users", handleListUsers, gin.Tags("用户管理"))
router.POST("/users", handleCreateUser, gin.Tags("用户管理"))

// 认证组
router.POST("/login", handleLogin, gin.Tags("认证"))
router.POST("/logout", handleLogout, gin.Tags("认证"))

// 订单管理组
router.GET("/orders", handleListOrders, gin.Tags("订单管理"))
router.POST("/orders", handleCreateOrder, gin.Tags("订单管理"))
```

## 自定义 Swagger UI

### 配置 Swagger UI 选项

```go
router.EnableSwaggerWithConfig("/swagger", &gin.SwaggerConfig{
    DeepLinking: true,
    Persist:     true,
    Layout:      "BaseLayout",
    Filter:      true,
})
```

### 自定义 UI 路径

```go
// 在 /docs 路径提供 Swagger UI
router.EnableSwagger("/docs")

// 在 /api/docs 路径提供
router.EnableSwagger("/api/docs")
```

## 导出文档

### 导出 OpenAPI JSON

```bash
# 直接访问
curl http://localhost:8080/openapi.json > api.json
```

### 生成客户端代码

```bash
# 使用 OpenAPI Generator
openapi-generator-cli generate \
  -i http://localhost:8080/openapi.json \
  -g typescript-axios \
  -o ./client

# 生成 Go 客户端
openapi-generator-cli generate \
  -i http://localhost:8080/openapi.json \
  -g go \
  -o ./client
```

## 最佳实践

### ✅ 为所有公开 API 添加文档

```go
// ✅ 好的做法
router.GET("/users",
    handleListUsers,
    gin.Summary("获取用户列表"),
    gin.Description("分页获取所有用户"),
    gin.Tags("用户管理"),
)

// ❌ 缺少文档
router.GET("/users", handleListUsers)
```

### ✅ 提供完整的响应示例

```go
// ✅ 完整的响应文档
gin.Response(200, "成功", &User{})
gin.Response(400, "请求错误", nil)
gin.Response(401, "未认证", nil)
gin.Response(500, "服务器错误", nil)
```

### ✅ 使用有意义的示例值

```go
type User struct {
    ID       int    `json:"id" example:"1"`                    // ✅ 具体值
    Username string `json:"username" example:"admin"`          // ✅ 有意义
    Email    string `json:"email" example:"admin@example.com"` // ✅ 完整示例
}
```

### ✅ 合理使用标签分组

```go
// ✅ 按功能模块分组
gin.Tags("用户管理")
gin.Tags("订单管理")
gin.Tags("认证授权")

// ❌ 分组过细或混乱
gin.Tags("用户", "管理", "API")
```

## 常见问题

### Q1: 如何隐藏内部 API?

**答**: 不添加文档注解的路由不会出现在文档中:

```go
// 有文档的公开 API
router.GET("/api/users", handleListUsers, gin.Summary("获取用户"))

// 无文档的内部 API
router.GET("/internal/stats", handleInternalStats)  // 不会出现在文档中
```

### Q2: 如何自定义响应模型?

**答**: 定义响应结构体:

```go
type APIResponse struct {
    Code    int         `json:"code" example:"0"`
    Message string      `json:"message" example:"success"`
    Data    interface{} `json:"data"`
}

gin.Response(200, "成功", &APIResponse{Data: &User{}})
```

### Q3: 如何添加请求示例?

**答**: 使用 `example` tag:

```go
type CreateUserRequest struct {
    Username string `json:"username" example:"newuser"`
    Email    string `json:"email" example:"user@example.com"`
    Password string `json:"password" example:"SecurePass123"`
}
```

## 相关文档

- [快速入门](./quick-start.md) - OpenAPI 基础使用
- [API 参考](./api-reference.md) - OpenAPI 相关 API
- [完整示例](./complete-examples.md) - 带完整文档的示例应用
