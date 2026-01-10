/**
 * [INPUT]: 依赖 internal/common, pkg/response, github.com/gin-gonic/gin, github.com/google/uuid
 * [OUTPUT]: 对外提供 MustAuth, MustBind, OK 等 Handler 工具函数
 * [POS]: pkg/base 的核心工具，被所有 handler 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package base

import (
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/liangze/go-project/internal/common"
	"github.com/liangze/go-project/pkg/response"
)

// ════════════════════════════════════════════════════════════════════════════
// MustAuth 获取用户ID，未授权返回 error
// ════════════════════════════════════════════════════════════════════════════

func MustAuth(c *gin.Context) (uuid.UUID, error) {
	userID, exists := c.Get("user_id")
	if !exists {
		return uuid.UUID{}, common.Err(common.ErrUnauthorized)
	}
	return userID.(uuid.UUID), nil
}

// ════════════════════════════════════════════════════════════════════════════
// MustBind 绑定并验证 JSON 请求
// ════════════════════════════════════════════════════════════════════════════

func MustBind(c *gin.Context, req interface{}) error {
	if err := c.ShouldBindJSON(req); err != nil {
		return common.Err(common.ErrInvalidRequestData)
	}
	return nil
}

// ════════════════════════════════════════════════════════════════════════════
// OK 成功响应并返回 nil error
// ════════════════════════════════════════════════════════════════════════════

func OK(c *gin.Context, data interface{}) error {
	response.Success(c, data)
	return nil
}
