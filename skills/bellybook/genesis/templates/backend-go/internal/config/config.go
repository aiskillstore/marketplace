/**
 * [INPUT]: 依赖 dario.cat/mergo, gopkg.in/yaml.v3, internal/config/types.go
 * [OUTPUT]: 对外提供 GlobalConfig, Load(), IsDev()
 * [POS]: config 模块的核心加载器，被 cmd/api/main.go 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package config

import (
	"fmt"
	"os"
	"path/filepath"

	"dario.cat/mergo"
	"gopkg.in/yaml.v3"
)

// ════════════════════════════════════════════════════════════════════════════
// 全局配置实例
// ════════════════════════════════════════════════════════════════════════════

var GlobalConfig *Config

// ════════════════════════════════════════════════════════════════════════════
// Load 加载配置文件
// 分层加载：common -> env -> 环境变量覆盖
// ════════════════════════════════════════════════════════════════════════════

func Load() error {
	env := os.Getenv("GO_ENV")
	if env == "" {
		env = "development"
	}

	// ────────────────────────────────────────────────────────────────────────
	// Step 1: 加载通用业务配置
	// ────────────────────────────────────────────────────────────────────────
	commonPath := resolveConfigPath("common")
	commonData, err := os.ReadFile(commonPath)
	if err != nil {
		return fmt.Errorf("读取通用配置失败 [%s]: %w", commonPath, err)
	}

	config := &Config{}
	if err := yaml.Unmarshal(commonData, config); err != nil {
		return fmt.Errorf("解析通用配置失败: %w", err)
	}

	// ────────────────────────────────────────────────────────────────────────
	// Step 2: 加载环境配置并合并
	// ────────────────────────────────────────────────────────────────────────
	envPath := resolveConfigPath(env)
	envData, err := os.ReadFile(envPath)
	if err != nil {
		return fmt.Errorf("读取环境配置失败 [%s]: %w", envPath, err)
	}

	envConfig := &Config{}
	if err := yaml.Unmarshal(envData, envConfig); err != nil {
		return fmt.Errorf("解析环境配置失败: %w", err)
	}

	// 合并：环境配置覆盖通用配置
	if err := mergo.Merge(config, envConfig, mergo.WithOverride); err != nil {
		return fmt.Errorf("合并配置失败: %w", err)
	}

	// ────────────────────────────────────────────────────────────────────────
	// Step 3: 环境变量覆盖（部署场景）
	// ────────────────────────────────────────────────────────────────────────
	applyEnvOverrides(config)

	GlobalConfig = config
	return nil
}

// ════════════════════════════════════════════════════════════════════════════
// resolveConfigPath 解析配置文件路径
// ════════════════════════════════════════════════════════════════════════════

func resolveConfigPath(env string) string {
	var filename string
	switch env {
	case "common":
		filename = "config.common.yaml"
	case "production", "prod":
		filename = "config.prod.yaml"
	case "staging":
		filename = "config.staging.yaml"
	default:
		filename = "config.dev.yaml"
	}

	paths := []string{
		filepath.Join("configs", filename),
		filepath.Join("/app/configs", filename), // Docker 容器内
	}

	for _, p := range paths {
		if _, err := os.Stat(p); err == nil {
			return p
		}
	}
	return paths[0]
}

// ════════════════════════════════════════════════════════════════════════════
// applyEnvOverrides 应用环境变量覆盖
// ════════════════════════════════════════════════════════════════════════════

func applyEnvOverrides(c *Config) {
	if v := os.Getenv("DB_HOST"); v != "" {
		c.Database.Host = v
	}
	if v := os.Getenv("DB_PASSWORD"); v != "" {
		c.Database.Password = v
	}
}

// ════════════════════════════════════════════════════════════════════════════
// IsDev 判断是否为开发环境
// ════════════════════════════════════════════════════════════════════════════

func IsDev() bool {
	return GlobalConfig.Environment == "development"
}
