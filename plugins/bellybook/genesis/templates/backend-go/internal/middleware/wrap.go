/**
 * [INPUT]: 依赖 github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 Wrap 函数
 * [POS]: middleware 的 Handler 包装器，被 router 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package middleware

import "github.com/gin-gonic/gin"

// ════════════════════════════════════════════════════════════════════════════
// Wrap 将返回 error 的 handler 转换为 gin.HandlerFunc
// 用法: router.POST("/create", middleware.Wrap(h.Create))
// ════════════════════════════════════════════════════════════════════════════

func Wrap(fn func(*gin.Context) error) gin.HandlerFunc {
	return func(c *gin.Context) {
		if err := fn(c); err != nil {
			c.Error(err) // 交给 GlobalErrorHandler 处理
		}
	}
}
