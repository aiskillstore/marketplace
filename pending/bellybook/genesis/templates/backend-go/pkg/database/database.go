/**
 * [INPUT]: 依赖 gorm.io/gorm, gorm.io/driver/postgres, internal/config
 * [OUTPUT]: 对外提供 DB, Init(), Close()
 * [POS]: pkg/database 的数据库连接模块，被 cmd/api/main.go 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package database

import (
	"fmt"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"github.com/liangze/go-project/internal/config"
)

// ════════════════════════════════════════════════════════════════════════════
// 全局数据库实例
// ════════════════════════════════════════════════════════════════════════════

var DB *gorm.DB

// ════════════════════════════════════════════════════════════════════════════
// Init 初始化数据库连接
// ════════════════════════════════════════════════════════════════════════════

func Init() error {
	cfg := config.GlobalConfig.Database
	dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.Name)

	logLevel := logger.Silent
	if config.IsDev() {
		logLevel = logger.Info
	}

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return fmt.Errorf("数据库连接失败: %w", err)
	}

	// 配置连接池
	sqlDB, _ := DB.DB()
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	return nil
}

// ════════════════════════════════════════════════════════════════════════════
// Close 关闭数据库连接
// ════════════════════════════════════════════════════════════════════════════

func Close() error {
	sqlDB, err := DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}
