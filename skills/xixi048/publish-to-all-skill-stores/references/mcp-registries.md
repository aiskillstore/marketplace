# MCP 分发：注册表、目录站与目录能自检的前置物

> 时间基准：2026-10。全部条目均为实测，含失败记录。
> 本文与 skill-store 那套是**两条赛道**：技能是「一份方法论」，MCP 是「一个可调用的服务」。
> 同一个产品可以两边都发，但交付物完全不同，不要互相套用配方。

## 一、先分清三种「上架」

| 形态 | 平台做什么 | 你要交什么 | 代表 |
|---|---|---|---|
| **元数据登记** | 只存一条记录，服务还在你自己服务器 | 一个 URL 或一份 `server.json` | 官方 Registry、mcp.so、Smithery、MCP.Directory |
| **目录自检型** | 平台会真的把服务跑起来、打分 | 仓库 + Dockerfile + 声明文件 | Glama |
| **平台托管** | 平台接管部署，代码跑在它的容器里 | 可容器化的完整代码 | 魔搭、百炼、火山（国内为主） |

前两类是「推送」，第三类是「移植」。第三类会生成平台自己的地址，从此你有两套端点要同步维护。

## 二、官方 Registry：所有下游的上游

`registry.modelcontextprotocol.io` 只存元数据，但它是一批目录站的数据源，登记一次可辐射多站。

### 2.1 `server.json` 的硬约束

- `$schema` 用 **`2025-12-11`**；`2025-09-29` 会告警
- `description` **硬上限 100 字符**（中文按字符算），超了直接 422
- 同时写 `packages`（npm/PyPI，stdio）与 `remotes`（streamable-http）——收录页两种装法都能给
- `packages[].identifier` 的包内必须声明 **`mcpName`**，且与 `server.json` 的 `name` 完全一致

用官方二进制校验，别用 npm 上的同名包：

```bash
# 官方 release（modelcontextprotocol/registry）
gh release download v1.8.5 --repo modelcontextprotocol/registry \
  --pattern "mcp-publisher_windows_amd64.tar.gz"
./mcp-publisher.exe validate
```

> ⚠️ npm 上有个 `mcp-publisher` 是个人发的同名包、**没有 repository 字段**，不要装。

### 2.2 命名空间：两种证明，二选一

| 方式 | 能拿到的命名空间 | 前提 |
|---|---|---|
| `login github` | `io.github.<user>/<server>` | 能完成 GitHub device flow |
| `login dns` / `login http` | 域名反写，如 `cloud.<domain>/<server>` | 能往自己域名挂一个验证文件 |

**域名验证的完整流程：**

1. 生成 ed25519 密钥对，私钥留在本机（**绝不入库**，尤其公开仓库）
2. 把公钥 proof 挂到 `https://<domain>/.well-known/mcp-registry-auth`，等部署生效
3. `mcp-publisher login http --domain <domain> --private-key <hex>`
4. `mcp-publisher publish`

代价：命名空间被锁死成 `cloud.<domain>/*`，拿不到 `io.github.<user>/*`。
身份归属从 GitHub 变成自有域名，对收录本身没影响。

**踩过的坑**：本机 CLI 到 `github.com` 的 HTTPS 不通（而 `api.github.com`、SSH push 都通）时，
device flow 拿不到授权码，`login github` 会一直卡住。**别在这一点上耗时间，直接切域名验证。**

### 2.3 发布后验证

```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=<name>"
# status: active 即为成功
```

## 三、让目录站能自检的三件套

Glama 这类站不放行「只有 URL」的条目——它要**在自己容器里把服务跑起来**才能打分，
而 `punkpeye/awesome-mcp-servers`（8K+ star）只收带 Glama 质量分的条目。所以这三件套是硬门槛：

| 文件 | 作用 | 要点 |
|---|---|---|
| `Dockerfile` | 让平台能起容器 | 零依赖服务用 `node:22-slim` 就够；不要 `npm ci`（没有 lockfile 会失败） |
| `glama.json` | 声明所有权与维护者 | 让平台知道仓库主人是谁 |
| `verify.js` / smoke test | 供评审现场握手 | 跑真实的 `initialize` + `tools/list` + 至少一次工具调用 |

```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package.json ./
COPY bin ./bin
COPY README.md ./
ENTRYPOINT ["node", "bin/cli.mjs"]
```

## 四、写条目文案的四条纪律

1. **别隐瞒付费。** 有付费档就写清「免费部分完整可用，付费只在 X 场景」，并说明增量价值。
   否则评审按「付费墙套壳」或「信息前后不一」直接关 PR，而且是从 README 里翻出来的。
2. **中文榜要中文。** 中文 MCP 榜单（`yzfly/Awesome-MCP-ZH`）要求：真实实现、可安装可调用、
   文档清晰、对中文用户有价值。**付费墙套壳、聚合导航站、营销文案**都明确不收。
3. **`description` 是给机器读的。** 官方 Registry 限 100 字符，先写能力，不要写愿景。
4. **不写会过期的固定数量。** `762 words / 598 styles` 这类数字是当前快照，词库一扩就失真，
   而它已经同时躺在 README、`package.json`、`server.json` 和三四个目录站的后台里。
   写能力：「一句话用感觉检索最匹配的视觉风格（背后是一份美术对照表）」。
   **这一条必须在第一份提交前定死**——目录站大多没有自助编辑入口，改一次要重发版本 + 重新排队。

## 五、发布顺序（返工最少）

```
服务跑起来（HTTPS 端点 + 冒烟测试通过）
  → npm / PyPI 包（mcpName 已声明）
    → 官方 Registry（命名空间验证）
      → Glama（Dockerfile + glama.json → 等打分）
        → awesome-mcp-servers PR（有分才收）
          → 其余目录站并行（mcpservers.org / MCP Market / MCP.Directory / Stork / Smithery / mcp.so）
            → 中文榜 PR（可与其他并行）
```

**PulseMCP 不用提交**：它从官方 Registry 自动同步，登记完等它拉。

## 六、表单层面的坑

| 现象 | 真实含义 | 处置 |
|---|---|---|
| `409 Conflict` | 往往是「该仓库已在队列中」，不是失败 | 换搜索/页面确认，别重复提交 |
| `403` 在 curl 但浏览器正常 | Cloudflare 拦 UA / TLS 指纹 | 走浏览器，不要用 curl 判定站点死亡 |
| 页面点提交才弹登录 | 表单是公开的，提交动作鉴权 | 物料备齐再登录，登一次当场填完 |
| 提交后只有 toast 没有 id | 可能是假表单 | 只有回执 id / 审核队列才算数 |

## 七、服务侧的四条静默错误（最贵的一类）

这些错误**不会报错**，只表现为「结果为空」，排查成本极高：

1. **部署包的 `includeFiles` 漏了数据文件** → 端点返回 `ok:true` 但 0 结果。
   必须写一条护栏：把代码里所有读数据文件的路径收集起来，与 `includeFiles` 做集合比对。
2. **入口与依赖被压进同一作用域** → `The symbol "onRequest" has already been declared`。
   云函数入口里不要与 import 进来的库使用同一个导出名，库侧改 `handleXxx`，入口自己做适配层。
3. **构建目标过旧**（如 node14）不支持 top-level await → 把自启动段从库文件里拆出去，
   单独放一个 server 入口脚本。
4. **本地默认与云端默认不一致** → 副本要显式改默认值（例如付费兜底开关），
   并且把这个改动写进同步脚本，不要靠人工。

护栏都要**反向验证**：故意制造一次错误，确认它真的会失败。没验证过的护栏等于没有。

## 八、版本与依赖的一致性

远端 MCP 服务和 npm 包是两套产物，但共用同一个 `tools.mjs`：

- 工具 schema 改了就**必须**同时更新远端与包，否则两边返回结构不一致
- 只在服务端改词表/数据 → 包不用发版（薄桥的价值就在这里）
- `mcpName` 一旦发布不能随意改，改了注册表的命名空间就对不上

## 九、目录速查

| 目录 | 提交形态 | 前置 | 备注 |
|---|---|---|---|
| Official Registry | `server.json` + publisher | 命名空间验证 + 包内 `mcpName` | 下游数据源，长期有效 |
| Glama | 网页 Add + GitHub 登录 | Dockerfile + glama.json | 有分才有 badge，卡着 awesome 榜 |
| punkpeye/awesome-mcp-servers | PR | Glama badge | 长期价值最高，硬门槛 |
| mcpservers.org | 免登录表单 + 邮箱 | 仓库 / 远端 URL | 自然搜索占比高 |
| MCP Market | 免登录表单，有免费队列 | 仓库 URL | 409 = 已在队列 |
| MCP.Directory | 免登录表单 | 仓库 URL | 约 24h 审核；**同时收 skill** |
| Stork.AI | 表单，提交时真握手 | HTTPS 端点可访问 | Cloudflare 挡 curl |
| Smithery | 登录后台登记 | 远端 URL | 需账号 |
| mcp.so | 登录 | 仓库或 URL | 免费路径不稳，别急着付费 |
| LobeHub MCP | 自动索引 + 账号提交 | 公开仓库 | 中文用户多 |
