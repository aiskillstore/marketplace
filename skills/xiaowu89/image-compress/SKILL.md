---
name: image-compress
description: 自动化图片压缩工作流，通过服务端智能压缩实现图片优化。支持本地路径、文件夹和远程 URL，返回 CDN 地址和压缩率。Use when compressing images, reducing file size, or optimizing photos.
license: MIT
compatibility: Requires Node.js >= 18 and nx-mcp-server with NX_API_KEY configured
metadata:
  author: xiaowu89
  version: 1.1.0
  tags:
    - image-compress
    - compression
    - optimization
    - cdn
---

# 图片压缩

通过 nx-mcp-server 远程压缩服务对图片进行智能压缩。

## 配置

在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "nx-mcp-compress": {
      "type": "url",
      "url": "https://mcp.api-inference.modelscope.net/4378d43d3e7d4c/mcp",
      "env": {
        "NX_API_KEY": "你的 API Key"
      }
    }
  }
}
```

查找顺序：项目根目录 → 用户家目录。提取 `url` → `MCP_URL`，`env.NX_API_KEY` → `API_KEY`。

Skill 直连 MCP 端点，**无需重启 Claude Code**。

> **没有 API Key？** 联系微信 `zhjian_2026` 获取。

## 压缩流程

### 步骤 1：检查配置

```bash
cat .mcp.json 2>/dev/null || cat ~/.mcp.json 2>/dev/null
```

- 找到 → 记录 `url` 和 `NX_API_KEY`，继续步骤 2
- 找不到 → 询问用户是否已有 API Key：
  - **有 Key**：帮用户创建 `~/.mcp.json`，全局和项目安装都通用
  - **没有 Key**：告知联系微信 `zhjian_2026` 获取

> ⚠️ 配置缺失时不要继续后续步骤。

### 步骤 2：执行压缩（一次 Bash 调用，纯内存，零文件）

替换 `PIC_DIR`、`MCP_URL`、`API_KEY`、`QUALITY` 后，heredoc 直接通过 stdin 喂给 node：

```bash
NODE_PATH=$(npm root -g) node << 'COMPRESSEOF'
const fs=require('fs'),path=require('path');
let PIC_DIR='<目标图片目录绝对路径>';
const SINGLE_FILE='<单张图片路径，为空则压缩整个目录>';
const MCP_URL='<从.mcp.json读取的url>';
const API_KEY='<从.mcp.json读取的NX_API_KEY>';
const QUALITY=90;
(async()=>{
const exts=['.png','.jpg','.jpeg','.webp','.bmp','.tga'];
let imgs;
if(SINGLE_FILE){imgs=[path.basename(SINGLE_FILE)];PIC_DIR=path.dirname(SINGLE_FILE)}
else{imgs=fs.readdirSync(PIC_DIR).filter(f=>exts.includes(path.extname(f).toLowerCase())).sort()}
const origTotal=imgs.reduce((s,f)=>s+fs.statSync(path.join(PIC_DIR,f)).size,0);
console.log(`共 ${imgs.length} 张，总 ${(origTotal/1024).toFixed(0)}KB`);
const maxSize=5*1024*1024;
const records=[];let skip=0;
for(let i=0;i<imgs.length;i++){const f=imgs[i],fp=path.join(PIC_DIR,f),osz=fs.statSync(fp).size;
if(osz>maxSize){records.push({name:f,origKb:osz,compKb:0,compUrl:null,ratio:null,error:'超过5MB限制'});skip++;console.log(`  [${i+1}/${imgs.length}] ${f} ${(osz/1024).toFixed(0)}KB ⚠️ 超过5MB跳过`);continue}
const buf=fs.readFileSync(fp);const ext=path.extname(f).toLowerCase().slice(1);
const mime=ext==='png'?'image/png':ext==='webp'?'image/webp':'image/jpeg';
records.push({name:f,origKb:osz,compKb:0,compUrl:null,ratio:null,dataUrl:'data:'+mime+';base64,'+buf.toString('base64')});}
console.log(`可压缩: ${records.length-skip} 张, 跳过: ${skip} 张`);
console.time('压缩');
const H={'Content-Type':'application/json','Accept':'application/json, text/event-stream'};
const r1=await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',id:'1',method:'initialize',params:{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'cc',version:'1'}}})});
H['Mcp-Session-Id']=r1.headers.get('Mcp-Session-Id');console.log('MCP: init');
await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})});console.log('MCP: notified');
// 并发池：始终保持 LIMIT 个请求在飞，完成一个补一个
	const LIMIT=5;
	let totalSaved=0,pass=0,fail=0,done=0;
	const pending=records.filter(r=>!r.error);
	
	async function compressOne(r,idx){
	  try{
	    const r3=await fetch(MCP_URL,{method:'POST',headers:H,body:JSON.stringify({jsonrpc:'2.0',id:'3',method:'tools/call',params:{name:'nx_compress',arguments:{files:[r.dataUrl],quality:QUALITY,apiKey:API_KEY}}})});
	    const raw=await r3.json();
	    if(!raw.result){r.error='MCP: '+(raw.error?.message||'unknown');fail++}
	    else{
	      const inner=JSON.parse(raw.result.content[0].text);
	      if(inner.error){r.error=inner.code+': '+inner.error;fail++}
	      else{const it=inner.items[0];
	        if(it.error){r.error=it.error;fail++}
	        else{r.compKb=it.compressedSize/1024;r.ratio=it.ratio;r.compUrl=it.compressedUrl;totalSaved+=it.originalSize-it.compressedSize;pass++;console.log(`  [${idx+1}/${imgs.length}] ${r.name} ${(r.origKb/1024).toFixed(0)}KB→${(r.compKb).toFixed(0)}KB (${r.ratio})`)}
	      }
	    }
	  }catch(e){r.error=e.message;fail++}
	  done++;
	}
	
	// 滑动窗口：始终保持 LIMIT 个并发
	let i=0;
	const running=new Set();
	while(i<pending.length||running.size>0){
	  while(running.size<LIMIT&&i<pending.length){
	    const p=compressOne(pending[i],i).then(()=>running.delete(p));
	    running.add(p);i++;
	  }
	  if(running.size>0) await Promise.race(running);
	}console.timeEnd('压缩');
console.log('\n'+'='.repeat(100));
console.log(`${'文件'.padEnd(40)} ${'原始'.padStart(8)} ${'压缩后'.padStart(8)} ${'压缩率'.padStart(8)} ${'结果'.padStart(6)}`);
console.log('-'.repeat(100));
for(const r of records){const oszS=(r.origKb/1024).toFixed(1)+'KB';
if(r.compUrl){const cszS=(r.compKb).toFixed(1)+'KB';console.log(`${r.name.padEnd(40)} ${oszS.padStart(8)} ${cszS.padStart(8)} ${(r.ratio||'?').padStart(8)} ${'✅'.padStart(6)} ${r.compUrl}`)}
else{console.log(`${r.name.padEnd(40)} ${oszS.padStart(8)} ${'—'.padStart(8)} ${'—'.padStart(8)} ${'❌'.padStart(6)}`)}}
console.log(`\n📊 ${records.length} 张 | ✅ ${pass} 成功 | ❌ ${fail} 失败 | 共节省 ${(totalSaved/1024).toFixed(0)}KB`);

})();
COMPRESSEOF
```

压缩参数：`quality` 默认 90（1-100），无需本地 sharp，直传服务端压缩。

### 步骤 3：下载到本地（如用户需要）

不要重新运行压缩！压缩结果中的 CDN URL 已在控制台输出，直接用 curl 下载：

```bash
curl -o <输出目录>/<文件名> "<CDN地址>"
```

- ✅ **成功**：压缩后的 CDN URL 可直接使用
- ⚠️ **超 5MB**：文件超过服务端限制，需手动处理
- ❌ **失败**：重试一次

---

## 返回字段速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `originalSize` | `number` | 原始大小（bytes） |
| `compressedSize` | `number` | 压缩后大小（bytes） |
| `ratio` | `string` | 压缩率，如 `"71.5%"` |
| `compressedUrl` | `string` | CDN 地址 |

## 常见错误速查

| 错误现象 | 原因 | 正确做法 |
|------|------|------|
| `MISSING_API_KEY` | 没传 `apiKey` | 必须传 |
| `API_AUTH_FAILED` | API Key 无效 | 检查 `.mcp.json` 中的 Key |
| `-32602 Invalid request parameters` | 未发送 `notifications/initialized` | 必须三步：init → notified → call |
| `406 Not Acceptable` | 缺少 `Accept` 头 | 同时声明 `application/json` 和 `text/event-stream` |
| 文件超过 5MB 被跳过 | 服务端限制 | 提示用户手动处理 |

## 禁止事项

- ❌ 不要本地压缩（服务端智能压缩，本地 sharp 多余）
- ❌ 不要传 `output` 参数（不存在）
- ❌ 不要省略 `apiKey` 参数
- ❌ 不要省略 `notifications/initialized` 步骤
- ❌ 不要写任何临时文件（heredoc 直接 stdin，纯内存执行）
- ❌ 不要把流程拆成多次 Bash 调用（一次 `node << 'COMPRESSEOF'` 搞定）
- ❌ 不要使用反斜杠路径，一律用正斜杠（`d:/path`）
