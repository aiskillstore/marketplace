/**
 * [INPUT]: 依赖 internal/dto, github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 Success, Custom 响应函数
 * [POS]: pkg/response 的统一响应模块，被 handler, middleware 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package response

import (
	"github.com/gin-gonic/gin"
	"github.com/liangze/go-project/internal/dto"
)

// ════════════════════════════════════════════════════════════════════════════
// Success 成功响应
// ════════════════════════════════════════════════════════════════════════════

func Success(c *gin.Context, data interface{}) {
	resp := dto.SuccessResponseWithMsg(data, "操作成功")
	c.JSON(200, resp)
}

// ════════════════════════════════════════════════════════════════════════════
// Custom 自定义响应
// ════════════════════════════════════════════════════════════════════════════

func Custom(c *gin.Context, data interface{}, message string, code int) {
	resp := dto.Custom(data, message, code)
	c.JSON(200, resp)
}
