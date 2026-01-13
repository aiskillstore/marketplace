/**
 * [INPUT]: 依赖 internal/config, internal/router, internal/service, pkg/database
 * [OUTPUT]: 无 - 程序入口
 * [POS]: 项目入口点，启动 HTTP 服务
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os/signal"
	"syscall"
	"time"

	"github.com/liangze/go-project/internal/config"
	"github.com/liangze/go-project/internal/router"
	"github.com/liangze/go-project/internal/service"
	"github.com/liangze/go-project/pkg/database"
)

func main() {
	// ════════════════════════════════════════════════════════════════════════
	// Step 1: 初始化核心组件
	// ════════════════════════════════════════════════════════════════════════
	if err := config.Load(); err != nil {
		log.Fatalf("配置加载失败: %v", err)
	}

	if err := database.Init(); err != nil {
		log.Fatalf("数据库连接失败: %v", err)
	}

	// ════════════════════════════════════════════════════════════════════════
	// Step 2: 初始化服务组
	// ════════════════════════════════════════════════════════════════════════
	serviceGroup := service.NewServiceGroup()

	// ════════════════════════════════════════════════════════════════════════
	// Step 3: 启动 HTTP 服务
	// ════════════════════════════════════════════════════════════════════════
	routerSetup := router.Setup(serviceGroup)

	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", config.GlobalConfig.Server.Port),
		Handler: routerSetup.Engine,
	}

	// Graceful shutdown
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	go func() {
		<-ctx.Done()
		log.Println("正在优雅关闭...")
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = database.Close()
		_ = srv.Shutdown(shutdownCtx)
	}()

	// ════════════════════════════════════════════════════════════════════════
	// Step 4: 启动
	// ════════════════════════════════════════════════════════════════════════
	port := config.GlobalConfig.Server.Port
	log.Printf("服务启动: http://localhost:%d", port)
	log.Printf("健康检查: http://localhost:%d/health", port)

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("服务启动失败: %v", err)
	}
}
