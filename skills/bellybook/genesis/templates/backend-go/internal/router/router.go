/**
 * [INPUT]: 依赖 internal/handler, internal/middleware, internal/service, pkg/response, github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 RouterSetup, Setup()
 * [POS]: router 模块的路由配置，被 cmd/api/main.go 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package router

import (
	"github.com/gin-gonic/gin"
	"github.com/liangze/go-project/internal/handler"
	"github.com/liangze/go-project/internal/middleware"
	"github.com/liangze/go-project/internal/service"
	"github.com/liangze/go-project/pkg/response"
)

// ════════════════════════════════════════════════════════════════════════════
// RouterSetup 路由配置结构
// ════════════════════════════════════════════════════════════════════════════

type RouterSetup struct {
	Engine *gin.Engine
}

// ════════════════════════════════════════════════════════════════════════════
// Setup 配置路由
// ════════════════════════════════════════════════════════════════════════════

func Setup(svc *service.ServiceGroup) *RouterSetup {
	r := gin.New()

	// ─────────────────────────────────────────────────────────────────────────
	// Middleware Chain (Order matters!)
	// ─────────────────────────────────────────────────────────────────────────
	r.Use(gin.Recovery())
	r.Use(middleware.GlobalErrorHandler)
	r.Use(middleware.CORS())

	// ─────────────────────────────────────────────────────────────────────────
	// 健康检查
	// ─────────────────────────────────────────────────────────────────────────
	r.GET("/health", func(c *gin.Context) {
		response.Success(c, gin.H{
			"status":  "ok",
			"service": "go-project",
			"version": "1.0.0",
		})
	})

	// ─────────────────────────────────────────────────────────────────────────
	// API 路由组
	// ─────────────────────────────────────────────────────────────────────────
	api := r.Group("/api/v1")
	{
		// 用户模块
		userHandler := handler.NewUserHandler(svc.UserService)
		api.GET("/user/profile/detail", middleware.Wrap(userHandler.GetProfile))
	}

	return &RouterSetup{Engine: r}
}
