# 安全配置 (Security Configuration)

自 2021 年 12 月 02 日起，高德地图 JSAPI v2.0 强制要求进行安全密钥配置，否则将无法正常加载地图或调用插件。

## 配置原理

为了提升密钥安全性，JSAPI v2.0 引入了“安全密钥”机制。开发者需要配合 `key` (用户 Key) 和 `securityJsCode` (安全密钥) 使用。

- **Key (用户 Key)**:用于标识开发者身份，明文传递。
- **SecurityJsCode (安全密钥)**: 用于后端验证，不应在生产环境前端明文暴露。

## 配置方式

### 方式一：明文设置（仅限开发环境）

在开发阶段，为方便调试，可以直接在前端代码中设置 `securityJsCode`。
**注意：请确保在调用 `AMapLoader.load` 之前设置。**

```javascript
window._AMapSecurityConfig = {
  securityJsCode: '您的安全密钥', // 必填，从高德控制台申请
};
```

### 方式二：代理转发（生产环境推荐）

在生产环境中，为了避免安全密钥泄露，强烈建议使用代理服务器转发请求。通过配置 `serviceHost`，将地图 API 请求转发到您的后端服务，再由后端服务附带安全密钥请求高德接口。

#### 1. 前端配置
设置 `serviceHost` 指向您的代理服务地址。

```javascript
window._AMapSecurityConfig = {
  serviceHost: 'https://您的代理服务器域名/_AMapService', 
  // 例如：'https://api.example.com/_AMapService'
};
```

#### 2. Nginx 代理配置示例

在您的 Nginx 服务器上配置转发规则。

```nginx
server {
    listen 80;
    server_name api.example.com;

    location /_AMapService/ {
        set $args "$args&jscode=您的安全密钥";
        proxy_pass https://restapi.amap.com/;
    }
}
```

**配置说明：**
- 前端请求 `https://api.example.com/_AMapService/v3/weather/weatherInfo?city=110101`
- Nginx 转发为 `https://restapi.amap.com/v3/weather/weatherInfo?city=110101&jscode=您的安全密钥`

#### 3. Node.js 代理配置示例

使用 `express` 和 `http-proxy-middleware` 实现代理转发。

```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

app.use('/_AMapService', createProxyMiddleware({
  target: 'https://restapi.amap.com',
  changeOrigin: true,
  pathRewrite: { '^/_AMapService': '' }, // 去除请求路径中的 /_AMapService 前缀
  onProxyReq: (proxyReq, req, res) => {
    // 拦截请求，追加 jscode 参数
    const url = new URL(req.url, 'https://restapi.amap.com');
    url.searchParams.append('jscode', '您的安全密钥');
    
    // 修改转发请求的路径
    proxyReq.path = url.pathname + url.search;
  }
}));

app.listen(3000, () => {
  console.log('Proxy server is running on http://localhost:3000');
});
```

#### 4. Java (Spring Boot) 代理配置示例

使用 `RestTemplate` 手动转发请求并追加安全密钥。

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import javax.servlet.http.HttpServletRequest;

@RestController
public class AMapProxyController {

    // 建议将密钥配置在 application.properties 中
    private static final String SECURITY_JS_CODE = "您的安全密钥";

    @GetMapping("/_AMapService/**")
    public ResponseEntity<String> proxy(HttpServletRequest request) {
        // 1. 解析目标路径，去除本地代理前缀
        String targetPath = request.getRequestURI().replace("/_AMapService", "");
        String amapUrl = "https://restapi.amap.com" + targetPath;

        // 2. 组装查询参数，追加 jscode
        String queryString = request.getQueryString();
        if (queryString == null || queryString.isEmpty()) {
            queryString = "jscode=" + SECURITY_JS_CODE;
        } else {
            queryString += "&jscode=" + SECURITY_JS_CODE;
        }

        // 3. 发起转发请求
        String finalUrl = amapUrl + "?" + queryString;
        RestTemplate restTemplate = new RestTemplate();
        
        // 注意：此处直接返回字符串，实际生产中可能需要处理 Headers 和状态码的透传
        return restTemplate.getForEntity(finalUrl, String.class);
    }
}
```

---

## 获取密钥

1. 登录 [高德开放平台控制台](https://console.amap.com/)
2. 进入「应用管理」→「我的应用」
3. 创建应用或选择已有应用
4. 添加 Key，选择「Web端(JS API)」
5. 获取 Key 和对应的安全密钥

## 常见问题

### 1. 地图白屏或提示 INVALID_USER_KEY

- 检查 Key 和安全密钥是否匹配
- 确认 `window._AMapSecurityConfig` 在 JSAPI 加载前已定义
- 检查 Key 是否已启用

### 2. 配额超限

- 登录控制台查看配额使用情况
- 生产环境务必使用代理方式，避免密钥被盗用

### 3. 部分服务不可用

- 确认插件已在 URL 或 Loader 中声明
- 检查 Key 是否有对应服务的使用权限

## 安全最佳实践

1. **开发环境与生产环境分离**: 使用不同的 Key
2. **生产环境必须使用代理**: 避免前端暴露安全密钥
3. **设置 IP 白名单**: 在控制台配置允许访问的服务器 IP
4. **定期更换密钥**: 如有泄露风险，及时重新生成
5. **监控配额使用**: 设置告警，防止异常调用
