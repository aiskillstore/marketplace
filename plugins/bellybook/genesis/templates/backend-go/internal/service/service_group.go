/**
 * [INPUT]: 依赖本包内的各 Service
 * [OUTPUT]: 对外提供 ServiceGroup, NewServiceGroup()
 * [POS]: service 模块的服务组，被 router 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package service

// ════════════════════════════════════════════════════════════════════════════
// ServiceGroup 服务组 - 统一管理所有业务服务
// 通过依赖注入传递给 Handler
// ════════════════════════════════════════════════════════════════════════════

type ServiceGroup struct {
	UserService *UserService
	// ... 添加更多服务
}

// NewServiceGroup 初始化服务组
func NewServiceGroup() *ServiceGroup {
	userSvc := NewUserService()

	return &ServiceGroup{
		UserService: userSvc,
	}
}
