/**
 * [INPUT]: 依赖 internal/service, pkg/base, github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 UserHandler, NewUserHandler()
 * [POS]: handler 模块的用户处理器，被 router 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package handler

import (
	"github.com/gin-gonic/gin"
	"github.com/liangze/go-project/internal/service"
	"github.com/liangze/go-project/pkg/base"
)

// ════════════════════════════════════════════════════════════════════════════
// UserHandler 用户 HTTP 处理器
// ════════════════════════════════════════════════════════════════════════════

type UserHandler struct {
	svc *service.UserService
}

func NewUserHandler(svc *service.UserService) *UserHandler {
	return &UserHandler{svc: svc}
}

// ════════════════════════════════════════════════════════════════════════════
// GetProfile 获取用户信息
// @Summary 获取当前用户信息
// @Tags User
// @Success 200 {object} dto.BaseResponse
// @Router /user/profile/detail [get]
// ════════════════════════════════════════════════════════════════════════════

func (h *UserHandler) GetProfile(c *gin.Context) error {
	userID, err := base.MustAuth(c)
	if err != nil {
		return err
	}

	user, err := h.svc.GetByID(userID)
	if err != nil {
		return err // 直接透传 Service 层 BizErr
	}

	return base.OK(c, user)
}
