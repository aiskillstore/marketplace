# SSE 实时通信指南

Server-Sent Events (SSE)是一种基于 HTTP 的服务器推送技术，Darkit Gin 内置完整的 SSE 支持。

## 快速开始

### 1. 启用 SSE

```go
import "github.com/darkit/gin/pkg/sse"

router := gin.NewRouter(
    gin.WithSSE(&sse.Config{
        HistorySize:  1000,              // 历史消息缓存大小
        PingInterval: 30 * time.Second,  // 心跳间隔
    }),
)
```

### 2. 创建 SSE 端点

```go
// 订阅事件流
router.GET("/events", func(c *gin.Context) {
    c.SSE()  // 开始 SSE 连接
})
```

### 3. 发送消息

```go
// 发送到所有客户端
router.SendSSE("news", gin.H{
    "title": "重要通知",
    "content": "系统将在 30 分钟后维护",
})

// 发送到指定频道
router.SendSSEToChannel("chat-room-1", "message", gin.H{
    "user": "Alice",
    "text": "Hello!",
})

// 发送到指定客户端
router.SendSSEToClient(clientID, "notification", gin.H{
    "type": "info",
    "message": "有新消息",
})
```

## 完整示例

### 实时通知系统

```go
package main

import (
    "time"
    "github.com/darkit/gin"
    "github.com/darkit/gin/pkg/sse"
)

func main() {
    router := gin.NewRouter(
        gin.WithSSE(&sse.Config{
            HistorySize:  1000,
            PingInterval: 30 * time.Second,
        }),
    )

    // SSE 端点
    router.GET("/notifications", handleNotifications)

    // 发送通知的 API
    router.POST("/notify", handleSendNotification)

    // 后台任务：定期发送系统状态
    go sendSystemStatus(router)

    router.Run(":8080")
}

// 订阅通知流
func handleNotifications(c *gin.Context) {
    // 获取用户 ID (从 JWT 或查询参数)
    userID := c.Query("user_id")

    // 订阅指定频道
    c.SSEWithChannel("user-" + userID)
}

// 发送通知
func handleSendNotification(c *gin.Context) {
    var req struct {
        UserID  string `json:"user_id" binding:"required"`
        Type    string `json:"type" binding:"required"`
        Message string `json:"message" binding:"required"`
    }

    if !c.BindJSON(&req) {
        return
    }

    // 发送到指定用户
    router.SendSSEToChannel("user-"+req.UserID, "notification", gin.H{
        "type":    req.Type,
        "message": req.Message,
        "time":    time.Now().Unix(),
    })

    c.Success(gin.H{"status": "sent"})
}

// 定期发送系统状态
func sendSystemStatus(router *gin.Engine) {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        status := getSystemStatus()

        // 广播到所有客户端
        router.SendSSE("system-status", status)
    }
}

func getSystemStatus() gin.H {
    return gin.H{
        "cpu":    getCPUUsage(),
        "memory": getMemoryUsage(),
        "time":   time.Now().Unix(),
    }
}
```

## 频道管理

### 订阅特定频道

```go
// 订阅单个频道
router.GET("/chat/:room", func(c *gin.Context) {
    room := c.Param("room")
    c.SSEWithChannel("chat-" + room)
})

// 订阅多个频道
router.GET("/events", func(c *gin.Context) {
    channels := []string{"news", "alerts", "updates"}
    c.SSEWithChannels(channels...)
})
```

### 发送到不同范围

```go
// 1. 广播到所有客户端
router.SendSSE("event-type", data)

// 2. 发送到指定频道
router.SendSSEToChannel("channel-name", "event-type", data)

// 3. 发送到指定客户端
router.SendSSEToClient("client-id", "event-type", data)

// 4. 发送到多个频道
channels := []string{"channel1", "channel2"}
router.SendSSEToChannels(channels, "event-type", data)
```

## 实时聊天室

```go
package main

import (
    "github.com/darkit/gin"
    "github.com/darkit/gin/pkg/sse"
)

type ChatMessage struct {
    Room      string    `json:"room"`
    User      string    `json:"user"`
    Message   string    `json:"message"`
    Timestamp time.Time `json:"timestamp"`
}

func main() {
    router := gin.NewRouter(
        gin.WithSSE(&sse.Config{
            HistorySize:  500,
            PingInterval: 30 * time.Second,
        }),
    )

    // 加入聊天室
    router.GET("/chat/:room/stream", joinChatRoom)

    // 发送消息
    router.POST("/chat/:room/message", sendChatMessage)

    // 获取在线用户
    router.GET("/chat/:room/users", getChatRoomUsers)

    router.Run(":8080")
}

// 加入聊天室
func joinChatRoom(c *gin.Context) {
    room := c.Param("room")
    user := c.Query("user")

    if user == "" {
        c.BadRequest("缺少用户名")
        return
    }

    // 订阅聊天室频道
    c.SSEWithChannel("chat-room-" + room)

    // 通知其他用户
    router.SendSSEToChannel("chat-room-"+room, "user-join", gin.H{
        "user": user,
        "time": time.Now().Unix(),
    })
}

// 发送聊天消息
func sendChatMessage(c *gin.Context) {
    room := c.Param("room")

    var msg ChatMessage
    if !c.BindJSON(&msg) {
        return
    }

    msg.Room = room
    msg.Timestamp = time.Now()

    // 广播消息到聊天室
    router.SendSSEToChannel("chat-room-"+room, "message", msg)

    c.Success(gin.H{"status": "sent"})
}

// 获取在线用户列表
func getChatRoomUsers(c *gin.Context) {
    room := c.Param("room")

    // 获取频道的客户端列表
    hub := c.GetSSEHub()
    clients := hub.GetChannelClients("chat-room-" + room)

    users := make([]string, 0, len(clients))
    for _, client := range clients {
        if user, ok := client.Metadata["user"].(string); ok {
            users = append(users, user)
        }
    }

    c.Success(gin.H{
        "room":  room,
        "users": users,
        "count": len(users),
    })
}
```

## 客户端集成

### JavaScript / TypeScript

```javascript
// 连接 SSE
const eventSource = new EventSource('http://localhost:8080/events');

// 监听消息事件
eventSource.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
});

// 监听自定义事件
eventSource.addEventListener('notification', (event) => {
    const notification = JSON.parse(event.data);
    showNotification(notification.message);
});

// 监听系统状态
eventSource.addEventListener('system-status', (event) => {
    const status = JSON.parse(event.data);
    updateSystemStatus(status);
});

// 错误处理
eventSource.onerror = (error) => {
    console.error('SSE 连接错误:', error);
    // 浏览器会自动重连
};

// 关闭连接
eventSource.close();
```

### React 示例

```jsx
import { useEffect, useState } from 'react';

function NotificationComponent() {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        const eventSource = new EventSource('/notifications?user_id=123');

        eventSource.addEventListener('notification', (event) => {
            const notification = JSON.parse(event.data);
            setNotifications(prev => [...prev, notification]);
        });

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <div>
            {notifications.map((notif, index) => (
                <div key={index} className={`alert alert-${notif.type}`}>
                    {notif.message}
                </div>
            ))}
        </div>
    );
}
```

### Vue 示例

```vue
<template>
  <div>
    <div v-for="(notif, index) in notifications" :key="index"
         :class="`alert alert-${notif.type}`">
      {{ notif.message }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      notifications: [],
      eventSource: null
    }
  },
  mounted() {
    this.eventSource = new EventSource('/notifications?user_id=123');

    this.eventSource.addEventListener('notification', (event) => {
      const notification = JSON.parse(event.data);
      this.notifications.push(notification);
    });
  },
  beforeUnmount() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }
}
</script>
```

## 高级功能

### 客户端元数据

```go
// 设置客户端元数据
router.GET("/events", func(c *gin.Context) {
    userID := c.Query("user_id")
    username := c.Query("username")

    // 保存客户端信息
    c.Set("sse_metadata", gin.H{
        "user_id":  userID,
        "username": username,
    })

    c.SSE()
})

// 获取客户端信息
hub := router.GetSSEHub()
clients := hub.GetAllClients()

for _, client := range clients {
    if userID, ok := client.Metadata["user_id"].(string); ok {
        // 使用用户 ID...
    }
}
```

### 历史消息重放

```go
router := gin.NewRouter(
    gin.WithSSE(&sse.Config{
        HistorySize: 100,  // 保留最近 100 条消息
    }),
)

// 新客户端连接时会自动接收历史消息
router.GET("/events", func(c *gin.Context) {
    c.SSE()  // 会自动发送历史消息
})
```

### 自定义心跳

```go
router := gin.NewRouter(
    gin.WithSSE(&sse.Config{
        PingInterval: 15 * time.Second,  // 15 秒发送一次心跳
    }),
)
```

### 连接认证

```go
router.GET("/events", func(c *gin.Context) {
    // 验证 JWT
    jwt, ok := c.RequireJWT()
    if !ok {
        return
    }

    userID := jwt["user_id"].(string)

    // 订阅用户专属频道
    c.SSEWithChannel("user-" + userID)
})
```

## 实时监控仪表板

```go
package main

import (
    "time"
    "github.com/darkit/gin"
    "github.com/darkit/gin/pkg/sse"
)

func main() {
    router := gin.NewRouter(
        gin.WithSSE(&sse.Config{
            HistorySize:  50,
            PingInterval: 10 * time.Second,
        }),
    )

    // 监控仪表板
    router.GET("/dashboard/stream", serveDashboard)

    // 启动监控任务
    go monitorSystem(router)

    router.Run(":8080")
}

func serveDashboard(c *gin.Context) {
    c.SSE()
}

func monitorSystem(router *gin.Engine) {
    ticker := time.NewTicker(2 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        // 收集系统指标
        metrics := gin.H{
            "timestamp": time.Now().Unix(),
            "cpu": gin.H{
                "usage":   getCPUUsage(),
                "cores":   runtime.NumCPU(),
                "threads": runtime.NumGoroutine(),
            },
            "memory": gin.H{
                "used":      getMemoryUsage(),
                "available": getAvailableMemory(),
            },
            "requests": gin.H{
                "total":   getTotalRequests(),
                "success": getSuccessRequests(),
                "failed":  getFailedRequests(),
            },
        }

        // 推送到所有仪表板
        router.SendSSE("metrics", metrics)
    }
}
```

## 进度跟踪

```go
// 长时间运行的任务
router.POST("/process", func(c *gin.Context) {
    taskID := generateTaskID()

    // 异步处理任务
    go processTask(router, taskID)

    c.Success(gin.H{"task_id": taskID})
})

// 订阅任务进度
router.GET("/process/:id/progress", func(c *gin.Context) {
    taskID := c.Param("id")
    c.SSEWithChannel("task-" + taskID)
})

// 处理任务并推送进度
func processTask(router *gin.Engine, taskID string) {
    channel := "task-" + taskID

    for i := 0; i <= 100; i += 10 {
        time.Sleep(1 * time.Second)

        router.SendSSEToChannel(channel, "progress", gin.H{
            "task_id":    taskID,
            "progress":   i,
            "message":    fmt.Sprintf("处理中... %d%%", i),
            "timestamp":  time.Now().Unix(),
        })
    }

    router.SendSSEToChannel(channel, "complete", gin.H{
        "task_id": taskID,
        "result":  "任务完成",
    })
}
```

## 错误处理

### 服务端错误处理

```go
router.GET("/events", func(c *gin.Context) {
    defer func() {
        if err := recover(); err != nil {
            log.Printf("SSE panic: %v", err)
        }
    }()

    c.SSE()
})
```

### 客户端断线重连

```javascript
function connectSSE(url) {
    const eventSource = new EventSource(url);

    eventSource.onerror = (error) => {
        console.error('SSE 连接错误:', error);

        // EventSource 会自动重连
        // 如需手动控制，关闭后重新创建
        if (eventSource.readyState === EventSource.CLOSED) {
            setTimeout(() => {
                connectSSE(url);
            }, 5000);  // 5 秒后重连
        }
    };

    return eventSource;
}
```

## 性能优化

### 限制客户端数量

```go
const maxClients = 1000

router.GET("/events", func(c *gin.Context) {
    hub := c.GetSSEHub()
    if hub.ClientCount() >= maxClients {
        c.Fail("服务器繁忙，请稍后再试")
        return
    }

    c.SSE()
})
```

### 清理断开的客户端

```go
// SSE 会自动清理断开的连接
// 可以手动触发清理
hub := router.GetSSEHub()
hub.CleanupDisconnected()
```

## 与 WebSocket 对比

| 特性 | SSE | WebSocket |
|------|-----|-----------|
| 方向 | 单向 (服务器→客户端) | 双向 |
| 协议 | HTTP | WebSocket |
| 实现复杂度 | 简单 | 较复杂 |
| 自动重连 | 是 | 需手动实现 |
| 浏览器支持 | 优秀 | 优秀 |
| 适用场景 | 通知、监控、实时更新 | 聊天、游戏、协作 |

### 何时使用 SSE?

✅ **适合使用 SSE**:
- 服务器推送通知
- 实时数据监控
- 进度更新
- 新闻推送
- 股票行情

❌ **不适合使用 SSE**:
- 需要客户端频繁发送数据
- 实时游戏
- 视频/音频流
- 文件传输

## 常见问题

### Q1: SSE 连接会超时吗?

**答**: 会。需要定期发送心跳保持连接:

```go
router := gin.NewRouter(
    gin.WithSSE(&sse.Config{
        PingInterval: 30 * time.Second,  // 每 30 秒心跳
    }),
)
```

### Q2: 如何处理客户端断线?

**答**: SSE 会自动检测并清理断开的客户端:

```go
// 获取断线事件
hub := router.GetSSEHub()
hub.OnClientDisconnect(func(clientID string) {
    log.Printf("客户端 %s 已断开", clientID)
})
```

### Q3: 可以发送二进制数据吗?

**答**: SSE 仅支持文本数据。需要发送二进制数据时，使用 Base64 编码:

```go
data := base64.StdEncoding.EncodeToString(binaryData)
router.SendSSE("binary-data", gin.H{"data": data})
```

## 相关文档

- [快速入门](./quick-start.md) - SSE 基础使用
- [API 参考](./api-reference.md) - SSE 相关 API
- [完整示例](./complete-examples.md) - 实时应用示例
