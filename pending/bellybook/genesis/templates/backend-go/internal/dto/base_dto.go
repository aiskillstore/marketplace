/**
 * [INPUT]: 依赖 github.com/google/uuid
 * [OUTPUT]: 对外提供 ResponseCode, BaseResponse, BasePageRequest, BaseIdReq 及响应构造器
 * [POS]: dto 模块的基础结构，被所有 handler 消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

package dto

import (
	"time"

	"github.com/google/uuid"
)

// ════════════════════════════════════════════════════════════════════════════
// 响应码常量
// ════════════════════════════════════════════════════════════════════════════

type ResponseCode int

const (
	CodeSuccess      ResponseCode = 200
	CodeCreated      ResponseCode = 201
	CodeBadRequest   ResponseCode = 400
	CodeUnauthorized ResponseCode = 401
	CodeForbidden    ResponseCode = 403
	CodeNotFound     ResponseCode = 404
	CodeConflict     ResponseCode = 409
	CodeServerError  ResponseCode = 500
)

// ════════════════════════════════════════════════════════════════════════════
// BaseResponse 统一响应结构
// ════════════════════════════════════════════════════════════════════════════

type BaseResponse struct {
	Code      ResponseCode `json:"code"`
	Message   string       `json:"message"`
	Data      interface{}  `json:"data,omitempty"`
	Timestamp time.Time    `json:"timestamp"`
	RequestID string       `json:"request_id,omitempty"`
}

// ════════════════════════════════════════════════════════════════════════════
// 响应构造器
// ════════════════════════════════════════════════════════════════════════════

// SuccessResponse 成功响应
func SuccessResponse(data interface{}) *BaseResponse {
	return &BaseResponse{
		Code:      CodeSuccess,
		Message:   "操作成功",
		Data:      data,
		Timestamp: time.Now(),
	}
}

// SuccessResponseWithMsg 带自定义消息的成功响应 (支持 i18n)
func SuccessResponseWithMsg(data interface{}, message string) *BaseResponse {
	return &BaseResponse{
		Code:      CodeSuccess,
		Message:   message,
		Data:      data,
		Timestamp: time.Now(),
	}
}

// Custom 自定义响应
func Custom(data interface{}, message string, code int) *BaseResponse {
	return &BaseResponse{
		Code:      ResponseCode(code),
		Message:   message,
		Data:      data,
		Timestamp: time.Now(),
	}
}

// UnauthorizedResponse 未授权响应
func UnauthorizedResponse() *BaseResponse {
	return &BaseResponse{
		Code:      CodeUnauthorized,
		Message:   "用户未认证或token无效",
		Timestamp: time.Now(),
	}
}

// NotFoundResponse 资源不存在响应
func NotFoundResponse(resource string) *BaseResponse {
	return &BaseResponse{
		Code:      CodeNotFound,
		Message:   resource + "不存在或无访问权限",
		Timestamp: time.Now(),
	}
}

// ════════════════════════════════════════════════════════════════════════════
// 分页请求/响应
// ════════════════════════════════════════════════════════════════════════════

// BasePageRequest 分页请求基类
type BasePageRequest struct {
	Page     int `json:"page" binding:"omitempty,min=1"`
	PageSize int `json:"page_size" binding:"omitempty,min=1,max=100"`
}

// Normalize 标准化分页参数
func (p *BasePageRequest) Normalize() {
	if p.Page < 1 {
		p.Page = 1
	}
	if p.PageSize < 1 {
		p.PageSize = 20
	}
	if p.PageSize > 100 {
		p.PageSize = 100
	}
}

// GetOffset 计算 SQL OFFSET
func (p *BasePageRequest) GetOffset() int {
	return (p.Page - 1) * p.PageSize
}

// BaseIdReq 基础 ID 请求
type BaseIdReq struct {
	Id uuid.UUID `json:"id" binding:"required"`
}
