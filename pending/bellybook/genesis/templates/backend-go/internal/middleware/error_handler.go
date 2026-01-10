/**
 * [INPUT]: 依赖 internal/common, pkg/response, github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 GlobalErrorHandler 中间件
 * [POS]: middleware 的全局错误处理器，被 router 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package middleware

import (
	"errors"

	"github.com/gin-gonic/gin"
	"github.com/liangze/go-project/internal/common"
	"github.com/liangze/go-project/pkg/response"
)

// ════════════════════════════════════════════════════════════════════════════
// GlobalErrorHandler 全局异常处理器
// ════════════════════════════════════════════════════════════════════════════

func GlobalErrorHandler(c *gin.Context) {
	defer func() {
		if r := recover(); r != nil {
			handleError(c, r)
		}
	}()

	c.Next()

	// 处理 c.Error() 写入的错误
	if len(c.Errors) > 0 && !c.Writer.Written() {
		handleError(c, c.Errors.Last().Err)
	}
}

// ════════════════════════════════════════════════════════════════════════════
// handleError 统一错误处理
// ════════════════════════════════════════════════════════════════════════════

func handleError(c *gin.Context, r any) {
	// 优先处理 BizErr
	var bizErr *common.BizErr
	if err, ok := r.(error); ok && errors.As(err, &bizErr) {
		code := common.CodeByError(bizErr.MessageId)
		// TODO: 接入 i18n 翻译
		c.Abort()
		response.Custom(c, nil, bizErr.MessageId, code)
		return
	}

	// 兜底处理
	code := common.CodeByError(common.ErrInternalProcess)
	c.Abort()
	response.Custom(c, nil, "服务器内部错误", code)
}
