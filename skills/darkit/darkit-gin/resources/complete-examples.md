# 生产级应用示例

本文档提供完整的生产级应用示例，展示如何使用 Darkit Gin 构建真实的企业应用。

## 完整的用户管理 API

这是一个包含所有企业级功能的完整示例。

### 项目结构

```
user-api/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── models/
│   │   └── user.go
│   ├── repository/
│   │   └── user_repo.go
│   ├── service/
│   │   └── user_service.go
│   └── handlers/
│       └── user_handler.go
├── configs/
│   └── config.yaml
├── go.mod
└── go.sum
```

### 1. 数据模型 (models/user.go)

```go
package models

import "time"

type User struct {
    ID        int       `json:"id" db:"id"`
    Username  string    `json:"username" db:"username" binding:"required,min=3,max=50"`
    Email     string    `json:"email" db:"email" binding:"required,email"`
    Password  string    `json:"-" db:"password_hash"`  // 不返回给客户端
    Role      string    `json:"role" db:"role" binding:"required,oneof=user admin"`
    Status    string    `json:"status" db:"status"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
    UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

type CreateUserRequest struct {
    Username string `json:"username" binding:"required,min=3,max=50"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=8"`
    Role     string `json:"role" binding:"required,oneof=user admin"`
}

type UpdateUserRequest struct {
    Email  string `json:"email" binding:"omitempty,email"`
    Role   string `json:"role" binding:"omitempty,oneof=user admin"`
    Status string `json:"status" binding:"omitempty,oneof=active inactive"`
}

type LoginRequest struct {
    Username string `json:"username" binding:"required"`
    Password string `json:"password" binding:"required"`
}
```

### 2. 数据访问层 (repository/user_repo.go)

```go
package repository

import (
    "database/sql"
    "user-api/internal/models"
)

type UserRepository interface {
    FindAll(page, size int) ([]models.User, int64, error)
    FindByID(id int) (*models.User, error)
    FindByUsername(username string) (*models.User, error)
    Create(user *models.User) error
    Update(user *models.User) error
    Delete(id int) error
}

type userRepo struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) UserRepository {
    return &userRepo{db: db}
}

func (r *userRepo) FindAll(page, size int) ([]models.User, int64, error) {
    offset := (page - 1) * size

    // 查询总数
    var total int64
    err := r.db.QueryRow("SELECT COUNT(*) FROM users").Scan(&total)
    if err != nil {
        return nil, 0, err
    }

    // 查询分页数据
    rows, err := r.db.Query(`
        SELECT id, username, email, role, status, created_at, updated_at
        FROM users
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
    `, size, offset)
    if err != nil {
        return nil, 0, err
    }
    defer rows.Close()

    var users []models.User
    for rows.Next() {
        var user models.User
        err := rows.Scan(
            &user.ID,
            &user.Username,
            &user.Email,
            &user.Role,
            &user.Status,
            &user.CreatedAt,
            &user.UpdatedAt,
        )
        if err != nil {
            return nil, 0, err
        }
        users = append(users, user)
    }

    return users, total, nil
}

func (r *userRepo) FindByID(id int) (*models.User, error) {
    var user models.User
    err := r.db.QueryRow(`
        SELECT id, username, email, role, status, created_at, updated_at
        FROM users
        WHERE id = $1
    `, id).Scan(
        &user.ID,
        &user.Username,
        &user.Email,
        &user.Role,
        &user.Status,
        &user.CreatedAt,
        &user.UpdatedAt,
    )

    if err == sql.ErrNoRows {
        return nil, nil
    }

    return &user, err
}

func (r *userRepo) FindByUsername(username string) (*models.User, error) {
    var user models.User
    err := r.db.QueryRow(`
        SELECT id, username, email, password_hash, role, status, created_at, updated_at
        FROM users
        WHERE username = $1
    `, username).Scan(
        &user.ID,
        &user.Username,
        &user.Email,
        &user.Password,
        &user.Role,
        &user.Status,
        &user.CreatedAt,
        &user.UpdatedAt,
    )

    if err == sql.ErrNoRows {
        return nil, nil
    }

    return &user, err
}

func (r *userRepo) Create(user *models.User) error {
    return r.db.QueryRow(`
        INSERT INTO users (username, email, password_hash, role, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, 'active', NOW(), NOW())
        RETURNING id, created_at, updated_at
    `, user.Username, user.Email, user.Password, user.Role).Scan(
        &user.ID,
        &user.CreatedAt,
        &user.UpdatedAt,
    )
}

func (r *userRepo) Update(user *models.User) error {
    _, err := r.db.Exec(`
        UPDATE users
        SET email = $1, role = $2, status = $3, updated_at = NOW()
        WHERE id = $4
    `, user.Email, user.Role, user.Status, user.ID)
    return err
}

func (r *userRepo) Delete(id int) error {
    _, err := r.db.Exec("DELETE FROM users WHERE id = $1", id)
    return err
}
```

### 3. 业务逻辑层 (service/user_service.go)

```go
package service

import (
    "errors"
    "user-api/internal/models"
    "user-api/internal/repository"
    "golang.org/x/crypto/bcrypt"
)

var (
    ErrUserNotFound      = errors.New("用户不存在")
    ErrInvalidPassword   = errors.New("密码错误")
    ErrUserAlreadyExists = errors.New("用户名已存在")
)

type UserService interface {
    GetUsers(page, size int) ([]models.User, int64, error)
    GetUser(id int) (*models.User, error)
    CreateUser(req *models.CreateUserRequest) (*models.User, error)
    UpdateUser(id int, req *models.UpdateUserRequest) (*models.User, error)
    DeleteUser(id int) error
    Authenticate(username, password string) (*models.User, error)
}

type userService struct {
    repo repository.UserRepository
}

func NewUserService(repo repository.UserRepository) UserService {
    return &userService{repo: repo}
}

func (s *userService) GetUsers(page, size int) ([]models.User, int64, error) {
    return s.repo.FindAll(page, size)
}

func (s *userService) GetUser(id int) (*models.User, error) {
    user, err := s.repo.FindByID(id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, ErrUserNotFound
    }
    return user, nil
}

func (s *userService) CreateUser(req *models.CreateUserRequest) (*models.User, error) {
    // 检查用户名是否已存在
    existing, err := s.repo.FindByUsername(req.Username)
    if err != nil {
        return nil, err
    }
    if existing != nil {
        return nil, ErrUserAlreadyExists
    }

    // 加密密码
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, err
    }

    user := &models.User{
        Username: req.Username,
        Email:    req.Email,
        Password: string(hashedPassword),
        Role:     req.Role,
        Status:   "active",
    }

    err = s.repo.Create(user)
    if err != nil {
        return nil, err
    }

    return user, nil
}

func (s *userService) UpdateUser(id int, req *models.UpdateUserRequest) (*models.User, error) {
    user, err := s.GetUser(id)
    if err != nil {
        return nil, err
    }

    // 更新字段
    if req.Email != "" {
        user.Email = req.Email
    }
    if req.Role != "" {
        user.Role = req.Role
    }
    if req.Status != "" {
        user.Status = req.Status
    }

    err = s.repo.Update(user)
    if err != nil {
        return nil, err
    }

    return user, nil
}

func (s *userService) DeleteUser(id int) error {
    user, err := s.GetUser(id)
    if err != nil {
        return err
    }
    if user == nil {
        return ErrUserNotFound
    }
    return s.repo.Delete(id)
}

func (s *userService) Authenticate(username, password string) (*models.User, error) {
    user, err := s.repo.FindByUsername(username)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, ErrUserNotFound
    }

    // 验证密码
    err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password))
    if err != nil {
        return nil, ErrInvalidPassword
    }

    return user, nil
}
```

### 4. 处理器层 (handlers/user_handler.go)

```go
package handlers

import (
    "errors"
    "time"
    "user-api/internal/models"
    "user-api/internal/service"
    "github.com/darkit/gin"
)

type UserHandler struct {
    service   service.UserService
    jwtSecret string
}

func NewUserHandler(service service.UserService, jwtSecret string) *UserHandler {
    return &UserHandler{
        service:   service,
        jwtSecret: jwtSecret,
    }
}

// 登录
func (h *UserHandler) Login(c *gin.Context) {
    var req models.LoginRequest
    if !c.BindJSON(&req) {
        return
    }

    user, err := h.service.Authenticate(req.Username, req.Password)
    if err != nil {
        if errors.Is(err, service.ErrUserNotFound) || errors.Is(err, service.ErrInvalidPassword) {
            c.Unauthorized("用户名或密码错误")
            return
        }
        c.ServerError("登录失败")
        return
    }

    // 生成 JWT 令牌
    token, _ := c.CreateJWTSession(h.jwtSecret, 2*time.Hour, gin.H{
        "user_id":  user.ID,
        "username": user.Username,
        "role":     user.Role,
    })

    c.Success(gin.H{
        "token":      token,
        "expires_in": 7200,
        "user":       user,
    })
}

// 获取用户列表
func (h *UserHandler) ListUsers(c *gin.Context) {
    page := c.ParamInt("page", 1)
    size := c.ParamInt("size", 10)

    // 限制分页大小
    if size > 100 {
        size = 100
    }

    // 尝试从缓存获取
    cacheKey := fmt.Sprintf("users:page:%d:size:%d", page, size)
    cache := c.GetCache()

    if cachedData, found := cache.Get(cacheKey); found {
        c.Success(cachedData)
        return
    }

    users, total, err := h.service.GetUsers(page, size)
    if err != nil {
        c.ServerError("获取用户列表失败")
        return
    }

    // 缓存结果（5分钟）
    result := gin.H{
        "users": users,
        "page":  page,
        "size":  size,
        "total": total,
    }
    cache.SetWithTTL(cacheKey, result, 5*time.Minute)

    c.Paginated(users, int64(page), int64(size), total)
}

// 获取单个用户
func (h *UserHandler) GetUser(c *gin.Context) {
    id := c.ParamInt("id")

    user, err := h.service.GetUser(id)
    if err != nil {
        if errors.Is(err, service.ErrUserNotFound) {
            c.NotFound("用户不存在")
            return
        }
        c.ServerError("获取用户失败")
        return
    }

    c.Success(user)
}

// 创建用户
func (h *UserHandler) CreateUser(c *gin.Context) {
    var req models.CreateUserRequest
    if !c.BindJSON(&req) {
        return
    }

    user, err := h.service.CreateUser(&req)
    if err != nil {
        if errors.Is(err, service.ErrUserAlreadyExists) {
            c.ValidationError(gin.H{"username": "用户名已存在"})
            return
        }
        c.ServerError("创建用户失败")
        return
    }

    // 清除用户列表缓存
    cache := c.GetCache()
    cache.Delete("users:*")

    c.Created(user)
}

// 更新用户
func (h *UserHandler) UpdateUser(c *gin.Context) {
    id := c.ParamInt("id")

    var req models.UpdateUserRequest
    if !c.BindJSON(&req) {
        return
    }

    user, err := h.service.UpdateUser(id, &req)
    if err != nil {
        if errors.Is(err, service.ErrUserNotFound) {
            c.NotFound("用户不存在")
            return
        }
        c.ServerError("更新用户失败")
        return
    }

    // 清除缓存
    cache := c.GetCache()
    cache.Delete(fmt.Sprintf("user:%d", id))
    cache.Delete("users:*")

    c.Success(user)
}

// 删除用户
func (h *UserHandler) DeleteUser(c *gin.Context) {
    id := c.ParamInt("id")

    err := h.service.DeleteUser(id)
    if err != nil {
        if errors.Is(err, service.ErrUserNotFound) {
            c.NotFound("用户不存在")
            return
        }
        c.ServerError("删除用户失败")
        return
    }

    // 清除缓存
    cache := c.GetCache()
    cache.Delete(fmt.Sprintf("user:%d", id))
    cache.Delete("users:*")

    c.NoContent()
}
```

### 5. 主程序 (cmd/server/main.go)

```go
package main

import (
    "context"
    "database/sql"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "user-api/internal/handlers"
    "user-api/internal/repository"
    "user-api/internal/service"

    "github.com/darkit/gin"
    "github.com/darkit/gin/cache"
    "github.com/darkit/gin/pkg/sse"
    _ "github.com/lib/pq"
)

func main() {
    // 从环境变量读取配置
    jwtSecret := getEnv("JWT_SECRET", "")
    if jwtSecret == "" {
        log.Fatal("JWT_SECRET is required")
    }

    dbURL := getEnv("DATABASE_URL", "postgres://localhost/userdb?sslmode=disable")
    port := getEnv("PORT", "8080")
    ginMode := getEnv("GIN_MODE", "release")

    // 初始化数据库
    db, err := sql.Open("postgres", dbURL)
    if err != nil {
        log.Fatalf("数据库连接失败: %v", err)
    }
    defer db.Close()

    // 配置连接池
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(5 * time.Minute)

    // 测试连接
    if err := db.Ping(); err != nil {
        log.Fatalf("数据库不可用: %v", err)
    }

    // 初始化依赖
    userRepo := repository.NewUserRepository(db)
    userService := service.NewUserService(userRepo)
    userHandler := handlers.NewUserHandler(userService, jwtSecret)

    // 创建路由器
    router := gin.NewRouter(
        gin.WithGinMode(ginMode),
        gin.WithJWT(jwtSecret),
        gin.WithCache(&cache.Config{
            TTL:             30 * time.Minute,
            CleanupInterval: 5 * time.Minute,
        }),
        gin.WithSSE(&sse.Config{
            HistorySize:  1000,
            PingInterval: 30 * time.Second,
        }),
        gin.WithOpenAPI(&gin.OpenAPI{
            Title:       "User Management API",
            Version:     "1.0.0",
            Description: "完整的用户管理 API 示例",
        }),
        gin.WithCORS("*"), // 生产环境请指定具体域名
        gin.WithRateLimit(1000),
        gin.WithRequestID(),
        gin.WithTimeout(30*time.Second),
    )

    // 健康检查和监控
    router.Health()
    router.Metrics()

    // 启用 Swagger UI
    router.EnableSwagger("/swagger")

    // 公开路由
    router.POST("/login", userHandler.Login)

    // 受保护的 API 路由
    api := router.Group("/api")
    api.Use(AuthMiddleware)
    {
        api.GET("/users", userHandler.ListUsers)
        api.GET("/users/:id", userHandler.GetUser)
        api.POST("/users", userHandler.CreateUser)
        api.PUT("/users/:id", userHandler.UpdateUser)
        api.DELETE("/users/:id", userHandler.DeleteUser)
    }

    // 创建 HTTP 服务器
    srv := &http.Server{
        Addr:         ":" + port,
        Handler:      router,
        ReadTimeout:  30 * time.Second,
        WriteTimeout: 30 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // 启动服务器（goroutine）
    go func() {
        log.Printf("服务器启动在端口 %s", port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("启动失败: %v", err)
        }
    }()

    // 优雅停机
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("正在关闭服务器...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("服务器强制关闭:", err)
    }

    log.Println("服务器已停止")
}

// 认证中间件
func AuthMiddleware(c *gin.Context) {
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }

    c.Set("user_id", jwt["user_id"])
    c.Set("username", jwt["username"])
    c.Set("role", jwt["role"])

    c.Next()
}

// 辅助函数：获取环境变量
func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}
```

### 6. 配置文件 (configs/config.yaml)

```yaml
server:
  port: 8080
  gin_mode: release
  read_timeout: 30s
  write_timeout: 30s

database:
  url: postgres://localhost/userdb?sslmode=disable
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 5m

jwt:
  secret: ${JWT_SECRET}
  expiry: 2h

cache:
  ttl: 30m
  cleanup_interval: 5m

sse:
  history_size: 1000
  ping_interval: 30s

cors:
  allowed_origins:
    - http://localhost:3000
    - https://example.com

rate_limit:
  requests_per_minute: 1000
```

### 7. 数据库初始化脚本

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
```

### 8. Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GIN_MODE=release
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=postgres://postgres:password@db:5432/userdb?sslmode=disable
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=userdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  db-data:
```

### 9. Dockerfile

```dockerfile
FROM golang:1.23-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server

FROM alpine:latest
RUN apk --no-cache add ca-certificates

WORKDIR /root/
COPY --from=builder /app/server .
COPY configs/ configs/

EXPOSE 8080
CMD ["./server"]
```

## 测试

### 单元测试示例

```go
// service/user_service_test.go
package service_test

import (
    "testing"
    "user-api/internal/service"
)

func TestCreateUser(t *testing.T) {
    mockRepo := &MockUserRepository{}
    svc := service.NewUserService(mockRepo)

    req := &models.CreateUserRequest{
        Username: "testuser",
        Email:    "test@example.com",
        Password: "password123",
        Role:     "user",
    }

    user, err := svc.CreateUser(req)
    if err != nil {
        t.Fatalf("创建用户失败: %v", err)
    }

    if user.Username != req.Username {
        t.Errorf("期望用户名 %s，实际 %s", req.Username, user.Username)
    }
}
```

### 集成测试示例

```go
// handlers/user_handler_test.go
package handlers_test

import (
    "bytes"
    "encoding/json"
    "net/http/httptest"
    "testing"

    "github.com/darkit/gin"
)

func TestListUsers(t *testing.T) {
    router := gin.Default()
    handler := setupTestHandler()

    router.GET("/users", handler.ListUsers)

    w := httptest.NewRecorder()
    req := httptest.NewRequest("GET", "/users?page=1&size=10", nil)

    router.ServeHTTP(w, req)

    if w.Code != 200 {
        t.Errorf("期望状态码 200，实际 %d", w.Code)
    }
}
```

## 相关文档

- [快速入门](./quick-start.md) - 基础概念和快速上手
- [API 参考](./api-reference.md) - 完整 API 文档
- [JWT 认证](./jwt-auth.md) - JWT 认证详解
- [最佳实践](../../docs/最佳实践.md) - 项目结构和代码规范
