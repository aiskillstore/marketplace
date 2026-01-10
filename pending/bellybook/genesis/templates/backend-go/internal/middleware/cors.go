/**
 * [INPUT]: 依赖 github.com/gin-gonic/gin
 * [OUTPUT]: 对外提供 CORS 中间件
 * [POS]: middleware 的跨域处理器，被 router 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package middleware

import "github.com/gin-gonic/gin"

// ════════════════════════════════════════════════════════════════════════════
// CORS 跨域中间件
// ════════════════════════════════════════════════════════════════════════════

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization, Accept-Language")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
}
