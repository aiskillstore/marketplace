/**
 * [INPUT]: 无外部依赖
 * [OUTPUT]: 对外提供 BizErr, KVPair, Err(), ErrWith()
 * [POS]: common 模块的业务异常结构，被 handler, service 层消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package common

// ════════════════════════════════════════════════════════════════════════════
// KVPair 自定义键值对 (用于 i18n 占位符)
// ════════════════════════════════════════════════════════════════════════════

type KVPair map[string]any

// ════════════════════════════════════════════════════════════════════════════
// BizErr 业务异常，支持国际化
// ════════════════════════════════════════════════════════════════════════════

type BizErr struct {
	MessageId string // 对应 locales/*.toml 中的 key
	Data      KVPair // 占位符数据
}

func (be *BizErr) Error() string {
	return be.MessageId
}

// ════════════════════════════════════════════════════════════════════════════
// 极简错误构造器
// ════════════════════════════════════════════════════════════════════════════

// Err 创建业务错误 (无参数)
func Err(errId string) error {
	return &BizErr{MessageId: errId}
}

// ErrWith 创建业务错误 (带参数)
func ErrWith(errId string, data KVPair) error {
	return &BizErr{MessageId: errId, Data: data}
}
