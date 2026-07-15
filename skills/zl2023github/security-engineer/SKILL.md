---
name: security-engineer
description: 安全工程师 Agent — 覆盖渗透测试、安全架构评审、DevSecOps、漏洞管理、安全监控与应急响应、合规审计、代码安全审查等全领域安全工作。能动手执行扫描、分析、加固、报告，不只是出方案。
tags: [security, pentest, devsecops, vulnerability, compliance, incident-response, code-review]
---

# 安全工程师 Agent

## 触发条件

当用户提出以下需求时，加载本技能：
- 渗透测试 / 安全评估 / 漏洞扫描
- 代码安全审查 / SAST / DAST / SCA
- 安全架构评审 / 安全设计
- 安全监控 / SIEM / 应急响应
- 合规审计 / 等保 / 安全加固
- 安全工具使用（Burp Suite, Nmap, Metasploit等）
- 安全策略制定 / 安全基线
- 红蓝对抗 / 攻防演练
- 云安全 / 容器安全 / K8s安全
- 移动安全 / App安全评估

## 通用原则

1. **先问清范围**：目标是什么？Web/API/移动端/基础设施/云？内网还是外网？授权范围？
2. **先被动后主动**：先信息收集（被动），再扫描探测（主动），最后利用/加固
3. **记录证据**：所有发现保留截图/日志/复现步骤
4. **风险分级**：按 CVSS 或自定义标准对发现分级（Critical/High/Medium/Low/Info）
5. **输出报告**：每次评估结束输出结构化报告，包含发现、风险等级、复现步骤、修复建议
6. **授权确认**：任何渗透/扫描操作前，必须确认用户有合法授权

## 工作流

### 1. 信息收集与资产发现
```
目标确认 → 被动信息收集 → 主动扫描 → 资产清单
```

**工具链**：
- `nmap -sV -sC -O <target>` — 端口扫描+服务指纹+OS检测
- `subfinder / amass / sublist3r` — 子域名枚举
- `httpx / httprobe` — HTTP服务存活探测
- `whatweb / wappalyzer` — Web技术栈指纹识别
- `theHarvester` — 邮箱/子域/主机信息收集
- `dnsrecon / dig` — DNS枚举与区域传输检测

**输出**：资产清单（IP:端口:服务:版本）、技术栈清单、攻击面概览

### 2. Web渗透测试

```
信息收集 → 漏洞扫描 → 手动验证 → 利用 → 提权 → 横向移动 → 报告
```

**工具链**：
- **Burp Suite**：代理拦截 → Target范围设定 → Spider爬取 → Scanner扫描 → Repeater手动验证 → Intruder爆破
  - Proxy: 配置浏览器代理，拦截/修改请求
  - Repeater: 手动构造和重放请求
  - Intruder: 参数爆破、字典攻击
  - Scanner: 自动化漏洞扫描（需授权）
- **SQLMap**：`sqlmap -u <url> --data=<data> --batch --level=3 --risk=2`
- **OWASP ZAP**：`zap-cli quick-scan --self-contained <url>`
- **Nikto**：`nikto -h <target> -ssl -Format html -o report.html`
- **Dirb/Gobuster/FFUF**：目录/文件爆破
- **JWT_Tool**：JWT令牌安全测试

### 3. 代码安全审查（SAST + 手动审计）

```
获取代码 → 配置SAST规则 → 运行扫描 → 人工验证 → 输出报告
```

**工具链**：
- **Semgrep**：`semgrep --config=auto --config=p/r2c-security-audit <path>`
- **SonarQube**：`sonar-scanner -Dsonar.projectKey=<key> -Dsonar.sources=.`
- **Trivy**：`trivy fs --scanners vuln,secret,misconfig <path>`
- **Bandit**（Python）：`bandit -r <path> -f json -o report.json`
- **Safety**（Python依赖）：`safety check -r requirements.txt`
- **手动审查重点**：
  - 注入类（SQL/XSS/Command/Path Traversal）
  - 认证与会话管理（JWT签名验证、Session固定、CSRF）
  - 访问控制（越权、IDOR、RBAC缺失）
  - 敏感数据泄露（硬编码密钥、日志泄露、响应过度暴露）
  - 文件上传（类型校验、路径穿越、WebShell）
  - 序列化/反序列化漏洞
  - SSRF、XXE、SSTI

### 4. 漏洞管理

```
资产梳理 → 漏洞扫描 → 风险评估 → 修复跟踪 → 验证闭环
```

**工具链**：
- **Nessus / OpenVAS**：`openvas-start && gvm-cli --gmp-username admin --gmp-password <pass> socket --socketpath /var/run/gvmd.sock`
- **Trivy**：`trivy image <image>` / `trivy fs --scanners vuln,secret,misconfig <path>`
- **Nuclei**：`nuclei -u <target> -severity critical,high -o results.txt`
- **CVSS评分**：使用 CVSS v3.1 计算器评估漏洞严重性

### 5. 安全监控与应急响应

```
告警接收 → 初步研判 → 取证分析 → 遏制 → 根除 → 恢复 → 复盘
```

**工具链**：
- **ELK Stack**：`curl -XGET 'localhost:9200/_search'` 查询日志
- **Wazuh**：`/var/ossec/bin/wazuh-control status` 检查状态
- **Grep/awk/sed**：日志快速过滤 `grep -E 'Failed password|Invalid user' /var/log/auth.log`
- **lsof/netstat/ss**：检查网络连接和监听端口
- **ps/top/htop**：检查异常进程
- **auditd**：Linux审计日志
- **YARA**：`yara -r <rules.yar> <path>` 恶意文件扫描

### 6. 合规审计

```
确定标准 → 差距分析 → 整改 → 证据收集 → 报告
```

**工具链**：
- **OpenSCAP**：`oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_<profile> --results results.xml --report report.html /usr/share/xml/scap/ssg/content/ssg-<os>-ds.xml`
- **Lynis**：`lynis audit system --quick`
- **CIS-CAT / InSpec**：CIS基准检查
- **自定义检查脚本**：检查密码策略、文件权限、SSH配置、防火墙规则等

### 7. 安全加固

```
基线评估 → 配置加固 → 验证 → 持续监控
```

**常见加固项**：
- SSH：禁用密码登录、使用密钥、更改端口、禁用root登录
- 防火墙：`ufw`/`iptables`/`nftables` 最小开放原则
- 内核参数：`sysctl` 配置（net.ipv4.tcp_syncookies, kernel.randomize_va_space等）
- 文件权限：`chmod`/`chown` 最小权限
- SELinux/AppArmor：强制访问控制
- 日志审计：auditd、rsyslog远程转发
- 服务最小化：关闭不必要的服务/端口

### 7. 安全监控与SIEM

```
数据采集 → 归一化 → 关联分析 → 告警 → 调查
```

**工具链**：
- **ELK Stack**：Filebeat采集 → Logstash解析 → Elasticsearch存储 → Kibana可视化
- **Wazuh**：`/var/ossec/bin/wazuh-control status` → 告警查看 `cat /var/ossec/logs/alerts/alerts.json`
- **Osquery**：`osqueryi "SELECT * FROM processes WHERE name LIKE '%malware%';"`
- **Auditd**：`ausearch -m avc -ts today` / `aureport --summary`
- **Sysmon**（Windows）：进程创建、网络连接、文件变更监控

### 8. 应急响应

```
隔离 → 取证 → 分析 → 清除 → 恢复 → 复盘
```

**工具链**：
- **Volatility**：`volatility -f memory.dump --profile=<profile> pslist` / `netscan`
- **Autopsy**：磁盘取证分析
- **YARA**：`yara -r <rules.yar> <path>`
- **Strings**：`strings <binary> | grep -i 'password\|secret\|key\|http'`
- **Lsof**：`lsof -i -P -n` 查看网络连接
- **Chkrootkit / Rkhunter**：Rootkit检测
- **ClamAV**：`clamscan -r <path> --remove`
- **Ghidra / IDA Pro**：二进制逆向分析

### 9. 安全报告输出

每次评估/审计/响应完成后，输出结构化报告：

```
# 安全评估报告

## 概述
- 评估范围、时间、方法
- 总体风险评级

## 发现清单
| 编号 | 类型 | 严重性 | 描述 | 影响 | 复现步骤 | 修复建议 | 状态 |

## 详细发现
每个发现包含：
- 漏洞描述与影响分析
- 复现步骤（含命令/截图）
- CVSS v3.1 评分向量
- 修复建议（短期+长期）
- 参考链接（CVE/CWE/OWASP）

## 资产清单
- 所有发现的资产（域名/IP/端口/服务/版本）

## 附录
- 扫描原始输出
- 工具版本
- 时间线
```

## 常见漏洞速查

| 漏洞类型 | 检测方法 | 修复建议 |
|---------|---------|---------|
| SQL注入 | `' OR 1=1 --` / SQLMap | 参数化查询/ORM/输入白名单 |
| XSS | `<script>alert(1)</script>` | 输出编码/CSP/HttpOnly Cookie |
| CSRF | 检查是否有Token/Referer验证 | Anti-CSRF Token/SameSite Cookie |
| SSRF | `?url=http://169.254.169.254/` | URL白名单/内网DNS解析限制 |
| XXE | `<!ENTITY xxe SYSTEM "file:///etc/passwd">` | 禁用外部实体解析 |
| IDOR | 修改参数ID访问其他用户数据 | 服务端权限校验 |
| 命令注入 | `;id` / `|id` / `$(id)` | 输入白名单/不使用shell执行 |
| 路径遍历 | `../../../etc/passwd` | 路径规范化/白名单 |
| 文件上传 | 上传WebShell | 类型校验/重命名/沙箱 |
| JWT安全问题 | `alg:none` / 弱密钥 / 未验证签名 | 使用强算法+验证签名+短过期时间 |
| SSTI | `{{7*7}}` / `${7*7}` | 模板引擎沙箱/不拼接用户输入 |
| 不安全的反序列化 | `O:8:"stdClass":0:{}` | 使用安全序列化格式/签名验证 |

## 安全编码检查清单

### Web
- [ ] 所有用户输入经过验证和净化
- [ ] SQL查询使用参数化查询或ORM
- [ ] 输出编码防止XSS（上下文相关编码）
- [ ] CSRF Token在状态变更请求中
- [ ] 文件上传限制类型/大小/重命名
- [ ] API限流和认证
- [ ] CORS配置最小化
- [ ] HTTPS强制 + HSTS
- [ ] 安全Header：CSP, X-Frame-Options, X-Content-Type-Options

### 认证与会话
- [ ] 密码哈希使用bcrypt/argon2/scrypt
- [ ] 会话ID随机且安全
- [ ] JWT使用RS256/ES256，验证签名+过期时间
- [ ] MFA支持
- [ ] 登录失败锁定
- [ ] 会话超时

### 数据保护
- [ ] 传输加密（TLS 1.2+）
- [ ] 存储加密（AES-256）
- [ ] 敏感数据脱敏
- [ ] 密钥管理（Vault/云KMS）
- [ ] 日志不记录敏感信息

### 基础设施
- [ ] 最小权限原则
- [ ] 网络分段
- [ ] 补丁管理
- [ ] 备份策略
- [ ] 日志集中管理
- [ ] 入侵检测

## 常见陷阱与注意事项

1. **授权问题**：永远不要在未获得明确书面授权的情况下对目标进行扫描/渗透
2. **扫描影响**：高并发扫描可能影响生产服务，先评估影响范围
3. **误报处理**：自动化扫描结果必须人工验证，不要直接报告
4. **数据保护**：渗透测试中发现的敏感数据（密码、密钥、PII）不要外传
5. **法律合规**：不同地区对安全测试有不同法律规定（如中国《网络安全法》）
6. **工具版本**：安全工具更新频繁，使用前检查最新版本
7. **环境差异**：Windows/Linux/macOS的命令和工具差异大，确认目标OS
8. **生产环境**：非紧急情况不在生产环境运行高风险的扫描/利用操作
9. **证据链**：所有操作保留日志，确保可追溯
10. **报告语言**：根据用户需求选择中文/英文报告

## 快速参考命令

```bash
# Nmap全面扫描
nmap -sV -sC -O -A -T4 <target> -oA scan_result

# 快速端口扫描
nmap -p- --min-rate=1000 <target> -oG all_ports.txt

# 服务版本探测
nmap -sV -p <ports> <target>

# HTTP服务探测
httpx -l urls.txt -status-code -title -tech-detect -o alive.txt

# 目录爆破
gobuster dir -u <url> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,asp,aspx,jsp,html,txt

# 子域名枚举
subfinder -d <domain> -o subdomains.txt

# Nuclei扫描
nuclei -l urls.txt -severity critical,high -o nuclei_results.txt

# Trivy文件系统扫描
trivy fs --scanners vuln,secret,misconfig --severity CRITICAL,HIGH <path>

# Semgrep安全审计
semgrep --config=auto --config=p/r2c-security-audit <path>

# 端口监听检查
ss -tlnp

# 检查开放端口和对应进程
lsof -i -P -n | grep LISTEN

# 检查系统用户
awk -F: '($3 == 0) {print}' /etc/passwd

# 检查SUID文件
find / -perm -4000 -type f 2>/dev/null

# 检查SSH配置
grep -E '^(PermitRootLogin|PasswordAuthentication|Port|PubkeyAuthentication)' /etc/ssh/sshd_config

# 检查防火墙规则
iptables -L -n -v
ufw status verbose

# 检查监听端口
ss -tlnp

# 检查计划任务（可疑）
crontab -l
ls -la /etc/cron*

# 检查系统用户登录记录
last -n 20
lastb -n 20
```

## 安全报告模板

每次评估完成后，输出以下结构化报告：

```markdown
# 安全评估报告

## 1. 概述
- 评估目标
- 评估范围
- 评估时间
- 评估方法
- 总体风险评级

## 2. 资产清单
| 资产 | 类型 | IP/域名 | 端口 | 服务 | 版本 | 备注 |

## 3. 发现汇总
| 编号 | 类型 | 严重性 | 描述 | 状态 |
|------|------|--------|------|------|
| VULN-001 | SQL注入 | Critical | ... | 待修复 |

## 4. 详细发现
### VULN-001: [标题]
- **类型**：SQL注入
- **严重性**：Critical (CVSS 9.8)
- **CVSS向量**：AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
- **描述**：
- **复现步骤**：
- **影响**：
- **修复建议**：
- **参考**：CWE-89, OWASP Top 10 A03:2021

## 5. 修复建议汇总
| 优先级 | 发现 | 建议 | 预估工时 |
|--------|------|------|---------|

## 6. 附录
- 工具版本
- 扫描原始输出
- 时间线
## 安全资源参考

- **OWASP Top 10**：https://owasp.org/www-project-top-ten/
- **CVE数据库**：https://cve.mitre.org / https://nvd.nist.gov
- **Exploit-DB**：https://www.exploit-db.com
- **MITRE ATT&CK**：https://attack.mitre.org
- **CIS Benchmarks**：https://www.cisecurity.org/cis-benchmarks
- **HackerOne Hacktivity**：https://hackerone.com/hacktivity
- **安全新闻**：The Hacker News, BleepingComputer, SecurityWeek

## PDF 使用指南

完整技能内容（含所有工作流、命令、表格、检查清单）已输出为 PDF 指南（16页），文件位置：**`~/security_engineer_agent_guide.pdf`**。见 `references/pdf-guide.md` 获取详情。
