# WorkBuddy 连接器（MCP 上架通道）

> 适用：把一个已有的 MCP Server 挂到 WorkBuddy 市场。
> 关键前提：**连接器 ≠ 技能**。技能卖"方法论"，连接器卖"能连的服务"。
> 同一个产品想两边都出现，要分别提交两份资产，各走各的审核。

## 一、包结构（4 个文件就够）

```
your-connector/
├── connector-meta.json      # 必须：市场展示元信息
├── mcp.json                 # 必须：MCP Server 连接配置
├── icon.svg                 # 必须：SVG 优先，PNG/JPG 建议 64×64
└── skills/                  # 可选但强烈建议
    └── {skill-name}/
        └── SKILL.md
```

打包成 zip 上传，平台自动开包解析、生成连接器 ID（`oc_` 开头）。
体积上限 **20 MB**（技能包是 3 MB，两者不同）。

## 二、远程 MCP 优先，不必自己起服务

已有 HTTPS 端点时，`mcp.json` 只要三行核心字段：

```json
{
  "mcpServers": {
    "your-service": {
      "type": "streamableHttp",
      "url": "https://example.com/mcp",
      "timeout": 30000
    }
  }
}
```

- `type`：`streamableHttp` / `sse` / `stdio`。远程必须 HTTPS。
- 一个连接器**只能配一个 MCP Server**。
- stdio 方案走 `command` + `args`，可声明 `runtime: {type:"node", version:"20"}`，
  由 WorkBuddy 托管运行时，不要依赖用户机器预装 Node/Python。

## 三、connector-meta.json 必填 6 项

```json
{
  "name": "中文名",
  "name_zh": "中文名",
  "name_en": "English Name",
  "description": "English one-liner",
  "description_zh": "中文说明，20～100 字，说清用户能完成什么",
  "description_en": "English description",
  "source": "kebab-case-全局唯一",
  "type": "mcp",
  "version": "1.0.0",
  "examples_zh": ["真实会说的自然语言 ×2~5"],
  "examples_en": ["..."]
}
```

- `source` 只能小写字母、数字、连字符，**全局唯一**，不能改（改=新连接器）。
- `type`：`mcp`（默认）/ `cli` / `skill-only`。
- 示例必须是用户真会说的话，不是功能点罗列 —— 它直接显示在市场详情页。

## 四、认证三选一，别自己造轮子

| 场景 | 配置 | 用户看到什么 |
|---|---|---|
| 无需认证 / MCP 自带 OAuth | `auth_mode` 省略 | 按标准 MCP 流程，需要时自动开浏览器 |
| 用户填 API Key / Token | `auth_mode: "token"` + `token-schema.json` | 弹表单，凭证只存本机 |
| WorkBuddy 云端托管 OAuth | `auth_mode: "server-side"` / `"gateway"` | 需先与官方对接 |

`token` 模式下，`mcp.json` 用 `${VAR}` 占位，**变量名必须与表单 key 完全一致**：

```json
"headers": { "Authorization": "Bearer ${API_KEY}" }
```

`token-schema.json` 字段：`title` / `description` / `fields[]`（`key` `label` `type`
`required` `placeholder` `description`）。敏感字段一律 `type: "password"`。
同一服务若要同时提供 OAuth 和 Token，必须用**两个不同 source** 作为两个连接器提交。

## 五、提交前自检（照抄这 8 条）

1. `source` 是 kebab-case 且未被占用
2. `mcp.json` 只配一个 Server，远程是 HTTPS
3. `connector-meta.json` 六项必填 + 中英示例各 2~5 条
4. `icon.svg` 存在，小尺寸可辨识
5. 文件里**没有**真实 Token / 密钥，全用 `${VAR}`
6. 端点能自己握手：`initialize` → `tools/list` → 一次真实 `tools/call`
7. 单次请求 30 秒内返回，错误信息可读
8. 用到新字段时在 meta 里声明 `minWorkbuddyVersion`

## 六、审核与生效

- 提交后进人审，**10～15 分钟**同步生效（比技能快得多，技能是 7 个工作日）。
- 更新版本重新提交即可，已安装用户自动跟进。
- 连接器**不参与**「收入变现」的收费体系 —— 想收费得走技能/专家的付费设置。
  也就是说：**连接器做曝光，技能做变现**，别指望连接器挂价格。

## 七、实测踩过的坑

1. **草稿残留**：`/skill/publish?action=create` 和 `/connector/publish?action=create`
   是同一个 SPA，上传过一个包后，再点「创建」会带出上一次的文件且**不显示 file input**，
   表现为 `no file input`。解法：点「上一步」退出 → 清 `localStorage/sessionStorage`
   里含 skill/publish/draft 的键 → 重新进列表点创建。
2. **服务类目是两级选择器**（Radix 两栏 Popover，不是 `role=option`）：
   `hover` 不展开，必须 `click` 左栏的 `button`，再点右栏二级项。
3. **头像必须 512×512、≤500 KB**；连接器图标则建议 64×64 SVG。
   两个字段不是一回事，别混用同一个文件。
