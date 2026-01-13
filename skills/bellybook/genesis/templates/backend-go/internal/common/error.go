/**
 * [INPUT]: 无外部依赖
 * [OUTPUT]: 对外提供错误常量 ErrUnknown, ErrInternalProcess 等，CodeByError 函数
 * [POS]: common 模块的错误定义，被 biz_err.go, middleware 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package common

// ════════════════════════════════════════════════════════════════════════════
// 错误常量 - 对应 locales/*.toml 中的 key
// ════════════════════════════════════════════════════════════════════════════

const (
	ErrUnknown            = "unknownError"
	ErrInternalProcess    = "internalProcess"
	ErrUnauthorized       = "unauthorized"
	ErrUserNotFound       = "userNotFound"
	ErrInvalidRequestData = "invalidRequestData"
	ErrParameterRequired  = "parameterRequired"
)

// ════════════════════════════════════════════════════════════════════════════
// 错误码映射
// ════════════════════════════════════════════════════════════════════════════

const DefaultBizCode = 10001

var errorCodeMapping = map[string]int{}

func init() {
	errorCodeMapping[ErrUnknown] = 10000
	errorCodeMapping[ErrInternalProcess] = 10001
	errorCodeMapping[ErrUnauthorized] = 10003
	errorCodeMapping[ErrUserNotFound] = 10004
	errorCodeMapping[ErrInvalidRequestData] = 10009
	errorCodeMapping[ErrParameterRequired] = 10005
}

// CodeByError 根据错误ID获取错误码
func CodeByError(errId string) int {
	if code, ok := errorCodeMapping[errId]; ok {
		return code
	}
	return DefaultBizCode
}
