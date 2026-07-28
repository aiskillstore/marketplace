---
name: image-audit
description: 自动化图片内容审核工作流。全量压缩后批量审核，支持鉴黄、政治、暴恐识别，以表格汇总结果。Use when auditing images, checking image content, or scanning photos for inappropriate material.
license: MIT
compatibility: Requires Node.js >= 18 with sharp (npm install -g sharp) and nx-mcp-audit MCP service with NX_API_KEY configured. No Python required.
metadata:
  author: xiaowu89
  version: 1.1.2
  tags:
    - image-audit
    - content-moderation
    - batch-processing
---

# Image Content Moderation

Audit images for adult, political, and violent content using the nx-mcp-audit MCP service.

## 配置

在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "nx-mcp-audit": {
      "type": "url",
      "url": "https://mcp.api-inference.modelscope.net/da16b3f65bdb4e/mcp",
      "env": {
        "NX_API_KEY": "你的 API Key"
      }
    }
  }
}
```

查找顺序：项目根目录 → 用户家目录。提取 `url` → `MCP_URL`，`env.NX_API_KEY` → `API_KEY`。

Skill 直连 MCP 端点，**无需重启 Claude Code**。

> **No API Key?** Contact WeChat `zhjian_2026` to get one.

## 审核流程

### 步骤 1：检查配置（缺少则立即停止）

```bash
cat .mcp.json 2>/dev/null || cat ~/.mcp.json 2>/dev/null
```

- 找到 → 记录 `url` 和 `NX_API_KEY`，继续步骤 2
- 找不到 → 询问用户是否已有 API Key：
  - **有 Key**：帮用户创建 `~/.mcp.json`（用户家目录），全局和项目安装都通用
  - **没有 Key**：告知联系微信 `zhjian_2026` 获取，等用户拿到后回来配置

> ⚠️ 配置缺失时不要安装 sharp 或继续后续步骤，先解决配置再往下走。

### 步骤 2：安装 sharp + 执行审核（一次 Bash 调用，纯内存，零文件）

替换 `PIC_DIR`、`MCP_URL`、`API_KEY` 后，heredoc 直接通过 stdin 喂给 node，**不写任何文件**：

```bash
NODE_PATH=$(npm root -g) node -e "require('sharp')" 2>/dev/null || npm install -g sharp
NODE_PATH=$(npm root -g) node << 'AUDITEOF'
const fs=require('fs'),path=require('path'),sharp=require('sharp');
let PIC_DIR='<目标图片目录绝对路径>';
const SINGLE_FILE='<单张图片路径，为空则审核整个目录>';
const MCP_URL='<从.mcp.json读取的url>';
const API_KEY='<从.mcp.json读取的NX_API_KEY>';
(async()=>{
const exts=['.png','.jpg','.jpeg','.webp','.bmp','.tga'];
let imgs;
if(SINGLE_FILE){imgs=[path.basename(SINGLE_FILE)];PIC_DIR=path.dirname(SINGLE_FILE)}
else{imgs=fs.readdirSync(PIC_DIR).filter(f=>exts.includes(path.extname(f).toLowerCase())).sort()}
const origTotal=imgs.reduce((s,f)=>s+fs.statSync(path.join(PIC_DIR,f)).size,0);
console.log(`共 ${imgs.length} 张，总 ${(origTotal/1024).toFixed(0)}KB`);
const records=[],data_urls=[];let compTotal=0;console.time('压缩');
for(let i=0;i<imgs.length;i++){const f=imgs[i],fp=path.join(PIC_DIR,f),osz=fs.statSync(fp).size;
try{const buf=await sharp(fp,{limitInputPixels:false}).resize({width:500,height:500,fit:'inside',withoutEnlargement:true}).jpeg({quality:40}).toBuffer();
const url='data:image/jpeg;base64,'+buf.toString('base64');records.push({name:f,origKb:osz,compKb:buf.length,dataUrl:url});
data_urls.push(url);compTotal+=buf.length;console.log(`  [${i+1}/${imgs.length}] ${f} ${(osz/1024).toFixed(0)}KB→${(buf.length/1024).toFixed(0)}KB`)}
catch(e){records.push({name:f,origKb:osz,compKb:0,dataUrl:null,error:e.message});console.log(`  [${i+1}/${imgs.length}] ${f} ❌ ${e.message}`)}}
console.timeEnd('压缩');
console.log(`payload: ${(compTotal/1024).toFixed(0)}KB`);
console.time('MCP审核');
const H={'Content-Type':'application/json','Accept':'application/json, text/event-stream','Authorization':`Bearer ${API_KEY}`};
const r1=await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',id:'1',method:'initialize',params:{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'cc',version:'1'}}})});
const sid=r1.headers.get('Mcp-Session-Id');H['Mcp-Session-Id']=sid;console.log(`MCP: init→${sid}`);
await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})});console.log('MCP: notified→202');
let items=[];
if(data_urls.length>0){const r3=await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',id:'3',method:'tools/call',params:{name:'nx_img_audit',arguments:{files:data_urls,apiKey:API_KEY}}})});
const raw=await r3.json();const inner=JSON.parse(raw.result.content[0].text);items=inner.items}
console.timeEnd('MCP审核');
let itemIdx=0,pass=0,block=0,fail=0;
console.log('\n'+'='.repeat(85));console.log(`${'文件'.padEnd(50)} ${'原始'.padStart(6)} ${'结果'.padStart(6)} ${'引擎'.padStart(6)} 说明`);console.log('-'.repeat(85));
for(const r of records){const oszS=(r.origKb/1024).toFixed(0)+'KB';
if(r.dataUrl){const item=items[itemIdx++],safe=item.safe,src=item.source||'-';const ec=item.errcode,em=item.errmsg||item.error||'';let st;
if(em==='invalid api key'||em==='未配置 API Key'){st='⚠️ 错误';fail++}else if(safe===true){st='✅ 通过';pass++}else if(safe===false){st='⛔ 违规';block++}else{st='❌ 失败';fail++}
console.log(`${r.name.padEnd(50)} ${oszS.padStart(6)} ${st.padStart(6)} ${src.padStart(6)} ${em.padStart(8)}`)}
else{console.log(`${r.name.padEnd(50)} ${oszS.padStart(6)} ${'❌ 失败'.padStart(6)} ${'—'.padStart(6)} 压缩失败`);fail++}}
const total=records.length;console.log(`\n📊 ${total} 张 | ✅ ${pass} 通过 | ⛔ ${block} 违规 | ⚠️ ${fail} 错误/失败 | v${items[0]?.auditVersion||'?'}`);
})();
AUDITEOF
```

### 建议

- ✅ **通过**：可正常使用
- ⛔ **违规**：建议删除或人工复核
- ❌ **失败**：重试一次

---

## 返回字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `safe` | `boolean` | `true`=通过，`false`=违规 |
| `source` | `string` | 审核引擎（`wechat` / `api`） |
| `errcode` | `number` | 错误码，`0`=正常 |
| `errmsg` | `string` | 错误信息，`"ok"`=正常 |
| `message` | `string` | 审核结果描述 |
| `auditVersion` | `string` | 服务版本号 |
| `summary` | `object` | `{total, pass, block, error}` |

## 常见错误速查

| 错误现象 | 原因 | 正确做法 |
|------|------|------|
| `-32602 Invalid request parameters` | 未发送 `notifications/initialized` | 必须三步：init → notified → call |
| `406 Not Acceptable` | 缺少 `Accept` 头 | 同时声明 `application/json` 和 `text/event-stream` |
| `"请提供 urls 或 files 参数"` | 用了不存在的 `imagePath` | 改用 `files`（base64 dataUrl 数组） |
| `"invalid api key"` | API Key 错误或过期（errcode=-1） | 检查 `.mcp.json` 中的 Key 是否正确 |
| `"未配置 API Key"` | 没传 `apiKey` | **必须传**，工具定义说可选是误导 |
| `413 Payload Too Large` | payload 超限 | 压缩后通常 < 200KB，不触发；未压缩大图需分批 |
| `Cannot find module 'sharp'` | 未全局安装或缺少 NODE_PATH | `NODE_PATH=$(npm root -g) node ...` |

## 禁止事项

- ❌ 不要跳过压缩（即使图片很小）
- ❌ 不要使用 `imagePath` 参数（不存在）
- ❌ 不要省略 `apiKey` 参数
- ❌ 不要省略 `notifications/initialized` 步骤
- ❌ 不要写任何临时文件（heredoc 直接喂 stdin，纯内存执行）
- ❌ 不要把流程拆成多次 Bash 调用（一次 `node << 'AUDITEOF'` 搞定）
- ❌ 不要使用反斜杠路径（`d:\path`），bash heredoc 会被转义，一律用正斜杠（`d:/path`）
