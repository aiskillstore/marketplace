/**
 * [INPUT]: 依赖 internal/common, github.com/google/uuid
 * [OUTPUT]: 对外提供 UserService, NewUserService()
 * [POS]: service 模块的用户服务，被 handler/user_handler.go 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package service

import (
	"github.com/google/uuid"
	"github.com/liangze/go-project/internal/common"
)

// ════════════════════════════════════════════════════════════════════════════
// UserService 用户业务服务
// ════════════════════════════════════════════════════════════════════════════

type UserService struct {
	// 可注入 repository
}

func NewUserService() *UserService {
	return &UserService{}
}

// ════════════════════════════════════════════════════════════════════════════
// UserProfile 用户信息结构
// ════════════════════════════════════════════════════════════════════════════

type UserProfile struct {
	ID    uuid.UUID `json:"id"`
	Name  string    `json:"name"`
	Email string    `json:"email"`
}

// ════════════════════════════════════════════════════════════════════════════
// GetByID 根据ID获取用户信息
// ════════════════════════════════════════════════════════════════════════════

func (s *UserService) GetByID(userID uuid.UUID) (*UserProfile, error) {
	// TODO: 实际从数据库查询
	if userID == uuid.Nil {
		return nil, common.Err(common.ErrUserNotFound)
	}

	// 模拟返回
	return &UserProfile{
		ID:    userID,
		Name:  "Test User",
		Email: "test@example.com",
	}, nil
}
