# Go Gin + GORM 初始化指南

## 一、环境检查

```bash
go version
```

**显示版本号（如 go1.23.x）**：跳到步骤二

**提示 command not found**：按以下方式安装

### macOS 安装 Go

```bash
brew install go

# 验证安装
go version
```

### Windows 安装 Go

1. 访问 https://go.dev/dl/
2. 下载 Windows 安装包
3. 双击安装，一路 Next
4. 重启终端，运行 `go version` 验证

---

## 二、项目初始化

### 1. 初始化 Go 模块

```bash
go mod init {项目名}
```

> 项目名由用户指定，如 `my-api`、`github.com/company/backend` 等

### 2. 安装核心依赖

```bash
# Web 框架
go get -u github.com/gin-gonic/gin

# ORM
go get -u gorm.io/gorm
go get -u gorm.io/driver/postgres

# 配置管理
go get -u github.com/spf13/viper

# 日志
go get -u go.uber.org/zap

# 验证
go get -u github.com/go-playground/validator/v10
```

### 3. 创建目录结构

```
.
├── cmd/                          # 入口点
│   ├── api/main.go               # API 服务入口
│   └── migrate/main.go           # 数据库迁移工具
│
├── internal/                     # 核心业务（私有）
│   ├── common/                   # 公共常量/错误码
│   ├── config/                   # 配置加载
│   ├── dto/                      # 请求/响应数据结构
│   ├── handler/                  # HTTP 处理器
│   ├── middleware/               # 中间件 (认证/限流/错误处理)
│   ├── model/                    # GORM 数据模型
│   ├── repository/               # 数据访问层
│   ├── router/                   # 路由注册
│   └── service/                  # 业务逻辑层
│
├── pkg/                          # 公共工具（可复用）
│   ├── auth/                     # 认证工具
│   ├── cache/                    # 缓存封装
│   ├── database/                 # 数据库连接
│   ├── logger/                   # 日志
│   ├── response/                 # 统一响应
│   ├── util/                     # 通用工具
│   └── validation/               # 参数校验
│
├── configs/                      # 配置文件
│   ├── config.common.yaml        # 公共配置
│   ├── config.dev.yaml           # 开发环境
│   └── config.prod.yaml          # 生产环境
│
├── migrations/                   # 数据库迁移脚本
├── locales/                      # i18n 翻译文件
├── test/                         # 测试文件
├── .gitignore
├── go.mod
├── go.sum
└── local-run.sh
```

---

## 三、初始化代码配置

> 注释使用中文

### 1. configs/config.common.yaml

```yaml
# 公共配置
server:
  port: 8080
  mode: debug  # debug | release

api:
  prefix: /api/v1
```

### 2. configs/config.dev.yaml

```yaml
# 开发环境配置
environment: dev

database:
  host: localhost
  port: 5432
  name: postgres
  user: YourUsername
  password: YourPassword
  sslmode: disable
  timezone: Asia/Shanghai
```

### 3. internal/config/config.go

```go
// Package config 配置管理模块
// 负责加载和管理应用配置
package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

// Config 应用配置结构
type Config struct {
	Environment string         `mapstructure:"environment"`
	Server      ServerConfig   `mapstructure:"server"`
	Database    DatabaseConfig `mapstructure:"database"`
	API         APIConfig      `mapstructure:"api"`
}

type ServerConfig struct {
	Port int    `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

type DatabaseConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	Name     string `mapstructure:"name"`
	User     string `mapstructure:"user"`
	Password string `mapstructure:"password"`
	SSLMode  string `mapstructure:"sslmode"`
	Timezone string `mapstructure:"timezone"`
}

type APIConfig struct {
	Prefix string `mapstructure:"prefix"`
}

// 全局配置实例
var Cfg *Config

// Load 加载配置
func Load(env string) error {
	if env == "" {
		env = "dev"
	}

	// 加载公共配置
	viper.SetConfigName("config.common")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./configs")

	if err := viper.ReadInConfig(); err != nil {
		return fmt.Errorf("读取公共配置失败: %w", err)
	}

	// 合并环境配置
	viper.SetConfigName(fmt.Sprintf("config.%s", env))
	if err := viper.MergeInConfig(); err != nil {
		return fmt.Errorf("读取环境配置失败: %w", err)
	}

	// 支持环境变量覆盖
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	Cfg = &Config{}
	if err := viper.Unmarshal(Cfg); err != nil {
		return fmt.Errorf("配置解析失败: %w", err)
	}

	return nil
}

// DSN 返回数据库连接字符串
func (c *Config) DSN() string {
	return fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s TimeZone=%s",
		c.Database.Host, c.Database.Port, c.Database.User,
		c.Database.Password, c.Database.Name, c.Database.SSLMode, c.Database.Timezone,
	)
}

// IsDev 判断是否为开发环境
func (c *Config) IsDev() bool {
	return c.Environment == "dev"
}
```

### 4. pkg/database/database.go

```go
// Package database 数据库模块
// 负责数据库连接和会话管理
package database

import (
	"fmt"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// 全局数据库实例
var DB *gorm.DB

// Connect 连接数据库
func Connect(dsn string, isDev bool) error {
	var err error

	// GORM 日志配置
	logLevel := logger.Silent
	if isDev {
		logLevel = logger.Info
	}

	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return fmt.Errorf("数据库连接失败: %w", err)
	}

	// 配置连接池
	sqlDB, err := DB.DB()
	if err != nil {
		return fmt.Errorf("获取数据库实例失败: %w", err)
	}

	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	// 测试连接
	if err := sqlDB.Ping(); err != nil {
		return fmt.Errorf("数据库连接测试失败: %w", err)
	}

	fmt.Println("数据库连接成功")
	return nil
}

// Close 关闭数据库连接
func Close() error {
	sqlDB, err := DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}
```

### 5. pkg/response/response.go

```go
// Package response 统一响应模块
// 提供统一的 API 响应格式
package response

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// Response 统一响应结构
type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
	Extra   interface{} `json:"extra,omitempty"`
}

// Success 成功响应
func Success(c *gin.Context, data interface{}, message string) {
	if message == "" {
		message = "success"
	}
	c.JSON(http.StatusOK, Response{
		Code:    200,
		Message: message,
		Data:    data,
	})
}

// Error 错误响应
func Error(c *gin.Context, code int, message string) {
	c.JSON(http.StatusOK, Response{
		Code:    code,
		Message: message,
	})
}

// BadRequest 参数错误响应
func BadRequest(c *gin.Context, message string) {
	Error(c, 400, message)
}

// Unauthorized 未授权响应
func Unauthorized(c *gin.Context, message string) {
	if message == "" {
		message = "未授权访问"
	}
	Error(c, 401, message)
}

// NotFound 资源不存在响应
func NotFound(c *gin.Context, message string) {
	if message == "" {
		message = "资源不存在"
	}
	Error(c, 404, message)
}

// ServerError 服务器错误响应
func ServerError(c *gin.Context, message string) {
	if message == "" {
		message = "服务器内部错误"
	}
	Error(c, 500, message)
}
```

### 6. internal/middleware/cors.go

```go
// Package middleware 中间件模块
// 提供 HTTP 中间件
package middleware

import (
	"github.com/gin-gonic/gin"
)

// CORS 跨域中间件
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization")
		c.Header("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}
```

### 7. internal/middleware/logger.go

```go
package middleware

import (
	"log"
	"time"

	"github.com/gin-gonic/gin"
)

// Logger 日志中间件
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		log.Printf("[%d] %s %s %v",
			status,
			c.Request.Method,
			path,
			latency,
		)
	}
}
```

### 8. internal/model/user.go

```go
// Package model 数据模型模块
// 定义数据库模型
package model

import (
	"time"

	"gorm.io/gorm"
)

// User 用户模型
type User struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	Username string `gorm:"size:64;not null;uniqueIndex" json:"username"`
	Phone    string `gorm:"size:20;uniqueIndex" json:"phone"`
	Email    string `gorm:"size:128" json:"email"`
	Avatar   string `gorm:"size:256" json:"avatar"`
}

// TableName 表名
func (User) TableName() string {
	return "users"
}
```

### 9. internal/handler/user.go

```go
// Package handler 处理器模块
// 处理 HTTP 请求
package handler

import (
	"{项目名}/pkg/response"

	"github.com/gin-gonic/gin"
)

// UserHandler 用户处理器
type UserHandler struct{}

// NewUserHandler 创建用户处理器
func NewUserHandler() *UserHandler {
	return &UserHandler{}
}

// GetUserInfo 获取用户信息
func (h *UserHandler) GetUserInfo(c *gin.Context) {
	// TODO: 从 service 层获取用户信息
	data := gin.H{
		"name": "张三",
		"age":  18,
	}
	response.Success(c, data, "获取用户信息成功")
}
```

### 10. internal/handler/login.go

```go
package handler

import (
	"{项目名}/pkg/response"

	"github.com/gin-gonic/gin"
)

// LoginHandler 登录处理器
type LoginHandler struct{}

// NewLoginHandler 创建登录处理器
func NewLoginHandler() *LoginHandler {
	return &LoginHandler{}
}

// RequestSMSCode 发送登录验证码
func (h *LoginHandler) RequestSMSCode(c *gin.Context) {
	// TODO: 调用 service 层发送验证码
	data := gin.H{
		"code": "null",
	}
	response.Success(c, data, "发送登录验证码成功")
}
```

### 11. internal/router/router.go

```go
// Package router 路由模块
// 配置 API 路由
package router

import (
	"{项目名}/internal/config"
	"{项目名}/internal/handler"
	"{项目名}/internal/middleware"
	"{项目名}/pkg/response"

	"github.com/gin-gonic/gin"
)

// Setup 配置路由
func Setup() *gin.Engine {
	// 根据环境设置模式
	if !config.Cfg.IsDev() {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()

	// 全局中间件
	r.Use(gin.Recovery())
	r.Use(middleware.Logger())
	r.Use(middleware.CORS())

	// 根路由
	r.GET("/", func(c *gin.Context) {
		response.Error(c, 400, "请检查 path - root")
	})

	// API v1 路由组
	v1 := r.Group(config.Cfg.API.Prefix)
	{
		// 用户模块
		userHandler := handler.NewUserHandler()
		userGroup := v1.Group("/user")
		{
			userGroup.GET("/get_user_info", userHandler.GetUserInfo)
		}

		// 登录模块
		loginHandler := handler.NewLoginHandler()
		loginGroup := v1.Group("/login")
		{
			loginGroup.GET("/request_sms_code", loginHandler.RequestSMSCode)
		}
	}

	return r
}
```

### 12. cmd/api/main.go

```go
// Package main 应用入口
// 启动 HTTP 服务器
package main

import (
	"flag"
	"fmt"
	"log"

	"{项目名}/internal/config"
	"{项目名}/internal/router"
	"{项目名}/pkg/database"
)

func main() {
	// 解析命令行参数
	env := flag.String("env", "dev", "运行环境: dev | staging | prod")
	flag.Parse()

	// 加载配置
	if err := config.Load(*env); err != nil {
		log.Fatalf("配置加载失败: %v", err)
	}

	// 连接数据库
	if err := database.Connect(config.Cfg.DSN(), config.Cfg.IsDev()); err != nil {
		log.Fatalf("数据库连接失败: %v", err)
	}
	defer database.Close()

	// 配置路由
	r := router.Setup()

	// 启动服务器
	addr := fmt.Sprintf(":%d", config.Cfg.Server.Port)
	log.Printf("服务器启动: http://localhost%s", addr)
	log.Printf("API 路径: http://localhost%s%s", addr, config.Cfg.API.Prefix)

	if err := r.Run(addr); err != nil {
		log.Fatalf("服务器启动失败: %v", err)
	}
}
```

### 13. .gitignore

```gitignore
# 环境配置（敏感信息）
configs/config.prod.yaml
configs/config.staging.yaml

# 编译产物
bin/
*.exe
*.exe~
*.dll
*.so
*.dylib

# 测试
*.test
*.out
coverage.txt

# IDE
.idea/
.vscode/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/
```

---

## 四、脚本配置

### local-run.sh

```bash
#!/bin/bash

# 运行应用（开发环境）
go run cmd/api/main.go -env=dev
```

赋予执行权限：

```bash
chmod +x local-run.sh
```

---

## 五、初始化完成检查

- [ ] 所有文件无乱码
- [ ] `./local-run.sh` 启动成功
- [ ] 访问 http://localhost:8080/api/v1/user/get_user_info 返回 JSON
- [ ] 数据库连接测试通过
- [ ] 构建 L1/L2/L3 文档，实现分形初始化

完成后等待下一步指令。
