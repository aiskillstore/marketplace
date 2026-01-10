/**
 * [INPUT]: 无外部依赖
 * [OUTPUT]: 对外提供 Config, ServerConfig, AppConfig, DatabaseConfig 结构体
 * [POS]: config 模块的类型定义，被 config.go 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package config

// ════════════════════════════════════════════════════════════════════════════
// Config 应用配置结构
// ════════════════════════════════════════════════════════════════════════════

type Config struct {
	Environment string         `yaml:"environment"`
	Server      ServerConfig   `yaml:"server"`
	App         AppConfig      `yaml:"app"`
	Database    DatabaseConfig `yaml:"database"`
}

type ServerConfig struct {
	Port int `yaml:"port"`
}

type AppConfig struct {
	Name     string `yaml:"name"`
	Version  string `yaml:"version"`
	LogLevel string `yaml:"log_level"`
}

type DatabaseConfig struct {
	Host     string `yaml:"host"`
	Port     int    `yaml:"port"`
	Name     string `yaml:"name"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
}
