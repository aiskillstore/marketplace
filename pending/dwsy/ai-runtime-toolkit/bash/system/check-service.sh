#!/bin/bash
# Service Health Checker
# 检查服务健康状态，支持HTTP、数据库、Redis

set -e

SERVICE_NAME="${1:-auth-service}"
CHECK_TYPE="${2:-http}"
TIMEOUT="${3:-5}"

echo "🔍 检查服务健康状态"
echo "服务: $SERVICE_NAME"
echo "检查类型: $CHECK_TYPE"
echo "超时: ${TIMEOUT}s"
echo "=========================================="

case $CHECK_TYPE in
  http)
    # HTTP健康检查
    URL="http://localhost:3000/health"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$URL" 2>/dev/null || echo "000")

    if [ "$STATUS" = "200" ]; then
      echo "✅ HTTP服务正常 (状态码: 200)"
      curl -s --max-time 2 "$URL" | jq '.' 2>/dev/null || echo "  (无法解析JSON响应)"
    else
      echo "❌ HTTP服务异常 (状态码: $STATUS)"
      exit 1
    fi
    ;;

  db|database)
    # 数据库连接检查
    if [ -f ".env" ]; then
      source .env
    fi

    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    DB_NAME="${DB_NAME:-myapp}"
    DB_USER="${DB_USER:-postgres}"

    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t "$TIMEOUT" >/dev/null 2>&1; then
      echo "✅ 数据库连接正常"
      echo "   Host: $DB_HOST:$DB_PORT"
      echo "   Database: $DB_NAME"
    else
      echo "❌ 数据库连接失败"
      exit 1
    fi
    ;;

  redis)
    # Redis连接检查
    REDIS_HOST="${REDIS_HOST:-localhost}"
    REDIS_PORT="${REDIS_PORT:-6379}"

    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
      echo "✅ Redis连接正常"
      echo "   Host: $REDIS_HOST:$REDIS_PORT"
    else
      echo "❌ Redis连接失败"
      exit 1
    fi
    ;;

  *)
    echo "❌ 未知的检查类型: $CHECK_TYPE"
    echo "支持的类型: http, db, redis"
    exit 1
    ;;
esac

echo "=========================================="
echo "✅ 所有检查通过"
exit 0
