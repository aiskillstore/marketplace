---
name: elderly-ui-audit
description: 依据中国工信部《互联网网站适老化通用设计规范》和《移动互联网应用(APP)适老化通用设计规范》，对项目代码进行适老化合规检测，生成问题报告、修改建议，并支持自动修复。
---

# 适老化设计规范检查 Skill

## 触发条件
当用户提到"适老化检查"、"适老化检测"、"老年模式审查"、"长辈版检查"、"elderly audit"时自动触发。

## 工作流程

### 第一步：项目识别
1. 检测项目类型：Web 还是 Mobile App？
   - 检查是否存在 `package.json` 中的移动端框架（React Native、Flutter、uni-app）或 Web 框架（React、Vue、Angular）。
   - 检查是否存在 `index.html` 或 `public/index.html`。
2. 检测入口文件：HTML入口、CSS文件、组件文件。
3. 询问用户：是全面扫描还是单项检查？

### 第二步：执行检查（按规范逐项扫描）

#### 模块一：字体与排版（可感知性）

**检查项：**
- [ ] 是否提供字体大小调整功能？【网站规范 1.2.3：提供网页放大设置与大字屏幕服务】
- [ ] 移动端适老版主信息字体是否 ≥ 30dp/pt？【APP规范 1.1】
- [ ] 移动端适老版一般字体是否 ≥ 18dp/pt？【APP规范 1.1】
- [ ] 行距是否 ≥ 1.3倍，段落间距是否 ≥ 行距的1.3倍？【APP规范 1.2】
- [ ] 移动网页是否提供 ≥ 18dp/pt 的大字体？【网站规范 1.2.3】

**检测方法：**
- 扫描 CSS 中的 `font-size`、`line-height`、`letter-spacing`、`margin`、`padding` 属性。
- 对于 Web，检查是否有 `font-size` 在 `@media` 或 `:root` 中的变量控制。
- 对于 App，检查样式文件中的 `fontSize`（RN）或 `textSize`（Flutter）。

**判定标准：**
| 平台 | 元素类型 | 最低尺寸 |
|------|---------|---------|
| 网站适老版 | 移动端大字体 | ≥ 18dp/pt |
| 网站适老版 | 计算机端 | 提供放大/大字服务 |
| App适老版 | 主信息 | ≥ 30dp/pt |
| App适老版 | 一般内容 | ≥ 18dp/pt |
| 行距（App） | 所有 | ≥ 1.3倍 |
| 段落间距（App） | 所有 | ≥ 行距的1.3倍 |

---

#### 模块二：颜色与对比度（可感知性）

**检查项：**
- [ ] 文本与背景对比度是否 ≥ 4.5:1？【APP规范】
- [ ] 是否仅依赖颜色传递信息？（应有文字/图标辅助）【APP规范】

**检测方法：**
- 提取所有 `color` 和 `background-color` 组合（或 `background`）。
- 使用 WCAG 对比度公式计算：(L1+0.05)/(L2+0.05)，其中 L 为相对亮度。
- 检查是否存在仅通过 `color` 区分的状态（如红色表示错误，但无文字提示）。

**判定标准：**
- 对比度 < 4.5:1 → 不通过
- 存在仅颜色区分的信息 → 不通过

---

#### 模块三：交互与操作（可操作性）

**检查项：**
- [ ] App 适老版主要组件可点击区域是否 ≥ 60×60 dp/pt？【APP规范 2.1】
- [ ] App 其他页面可点击区域是否 ≥ 44×44 dp/pt？【APP规范 2.1】
- [ ] App 弹窗关闭按钮响应区域是否 ≥ 44×44 dp/pt？【APP规范 2.4】
- [ ] App 是否避免了 3 个以上手指的复杂手势？【APP规范 2.2】
- [ ] App 限时操作是否为用户留出充足时间？【APP规范 2.3】
- [ ] 网站是否支持全程键盘操作？【网站规范 服务原则 2】
- [ ] 网站是否提供特大鼠标指针？【网站规范 服务原则 2】
- [ ] 网站多媒体播放控制是否可通过键盘完成？【网站规范 2.3】
- [ ] 网站是否存在不可关闭的广告弹窗或临时弹窗？【网站规范 2.4.1】
- [ ] 网站财务交易提交是否可逆/可撤销（10分钟内）？【网站规范 2.6.1】

**检测方法：**
- 扫描所有 `button`、`a`、`div[onClick]`、`TouchableOpacity` 等可交互元素。
- 检查其 `width`、`height`、`min-width`、`min-height`、`padding` 组合计算实际点击区域。
- 搜索手势相关代码（如 `onPan`、`onPinch`、`gesture` 等），检查是否超过 3 指。
- Web 检查是否有 `tabindex` 和键盘事件监听、`<video>/<audio>` 的键盘控制。
- 搜索 `setTimeout`/`setInterval` 触发的弹窗逻辑。
- 检查表单提交逻辑是否支持撤销或修改。

---

#### 模块四：验证码（可感知性）

**检查项：**
- [ ] App 非文本验证码是否提供语音/文字替代形式？【APP规范 1.5】
- [ ] 网站验证码放大倍数是否 ≥ 2倍？【网站规范 1.4.3】
- [ ] 网站是否同时提供验证码放大和替代形式（如语音验证码）？【网站规范 1.4.3】
- [ ] 网站限时验证码（≤3分钟）是否提供语音告知和延长时效？【网站规范 1.4.4】

**检测方法：**
- 搜索验证码相关组件（`captcha`、`verification code`、`验证码`）。
- 检查是否有 `audio` 或 `alt` 文本替代。
- Web 检查验证码图片的 `width`/`height` 是否支持 ≥ 2倍放大。
- 检查验证码时效设置是否 ≤ 3分钟且提供延长机制。

---

#### 模块五：广告与诱导（安全性）

**检查项：**
- [ ] 适老版界面是否**严禁**出现广告内容及插件？【APP规范 5.1.1】
- [ ] 是否**严禁**诱导下载、诱导付款按键？【APP规范 5.1.2 / 网站规范 2.4.2】
- [ ] 网站是否**严禁**随机广告或临时广告弹窗？【网站规范 2.4.1】
- [ ] App 是否遵循个人信息收集最小必要原则？【APP规范 5.2】

**检测方法：**
- 搜索代码中的广告关键词：`ad`、`banner`、`promotion`、`sponsor`、`广告`。
- 检查是否存在 `setTimeout` 或 `setInterval` 触发的弹窗。
- 检查是否有明显的诱导按钮文字（如"领取"、"立即下载"）。
- 检查个人信息收集相关代码（如位置、图片信息）是否符合最小必要原则。

---

#### 模块六：入口与导航（可理解性）

**检查项：**
- [ ] App 首次安装时是否为适老化设置提供显著引导？【APP规范 3.1】
- [ ] App 首页是否具备显著入口支持切换至适老版/长辈版？【APP规范 3.1】
- [ ] App 是否支持"长辈版"等关键词搜索直达（含"亲情版""关爱版""关怀版"别名）？【APP规范 3.1】
- [ ] 网站栏目是否避免使用专业词语或网络新词语？【网站规范 3.1.1】
- [ ] 网站操作流程是否与常规认知一致？【网站规范 3.1.2】
- [ ] 网站是否避免修改公认的通用名称或功能标识？【网站规范 3.1.3】
- [ ] 网站是否提供操作状态告知和撤销功能？【网站规范 3.1.4】

**检测方法：**
- 检查 App 首页、设置页、个人中心是否存在"长辈版"、"适老版"、"关怀模式"等入口。
- 检查全局搜索是否支持这些关键词及别名。
- 检查网站导航标签/栏目名称是否使用常见表述，有无网络新词或晦涩专业术语。
- 检查网站是否设有撤销操作按钮或返回机制。

---

#### 模块七：兼容性（兼容性）

**检查项：**
- [ ] App 是否禁止或限制读屏软件等辅助设备接入？【APP规范 4.1】
- [ ] App 在辅助工具开启时，所有功能性组件是否正常工作？【APP规范 4.1】
- [ ] 网站是否兼容主流操作系统、浏览器及辅助软件？【网站规范 4.1】
- [ ] 网站组件样式是否在不同浏览器/操作系统中保持一致？【网站规范 4.2.1】

**检测方法：**
- 检查是否有 `accessibility` 相关属性的限制（如 `important-for-accessibility="no"` 或 `aria-hidden="true"` 滥用）。
- 检查 `package.json` 中的 `browserslist` 是否覆盖主流浏览器。
- 检查组件是否使用了浏览器私有前缀或非标准 API 导致跨平台不一致。

---

### 第三步：生成报告

#### 报告格式

输出为独立的 HTML 文件，保存为 `elderly-audit-report.html`，用户可直接在浏览器中打开查看。

---

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>适老化设计规范检测报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            color: #1e293b;
            padding: 40px 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
            padding: 48px 56px;
        }

        /* 报告标题 */
        .report-header {
            border-bottom: 2px solid #e9edf4;
            padding-bottom: 24px;
            margin-bottom: 32px;
        }

        .report-header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.3px;
        }

        .report-header .subtitle {
            color: #64748b;
            font-size: 15px;
            margin-top: 4px;
        }

        /* 总览卡片区 */
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            background: #f8fafc;
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 24px;
        }

        .overview-item {
            text-align: center;
        }

        .overview-item .number {
            font-size: 32px;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }

        .overview-item .label {
            font-size: 14px;
            color: #64748b;
            margin-top: 2px;
        }

        .overview-item .number.pass {
            color: #16a34a;
        }
        .overview-item .number.fail {
            color: #dc2626;
        }
        .overview-item .number.warn {
            color: #f59e0b;
        }
        .overview-item .number.rate {
            color: #2563eb;
        }

        .summary-text {
            background: #f1f5f9;
            border-left: 4px solid #2563eb;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 32px;
            font-size: 15px;
            color: #1e293b;
        }

        .summary-text strong {
            color: #0f172a;
        }

        /* 模块统计表格 */
        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #0f172a;
            margin: 32px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9edf4;
        }

        .module-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 15px;
            margin-bottom: 12px;
        }

        .module-table th {
            background: #f1f5f9;
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 2px solid #dce2ec;
        }

        .module-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #e9edf4;
        }

        .module-table tr:hover td {
            background: #fafbfc;
        }

        .status-badge {
            display: inline-block;
            padding: 2px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }

        .status-badge.pass {
            background: #dcfce7;
            color: #166534;
        }

        .status-badge.fail {
            background: #fee2e2;
            color: #991b1b;
        }

        .status-badge.warn {
            background: #fef9c3;
            color: #854d0e;
        }

        /* 逐项清单 */
        .module-group {
            margin-top: 28px;
        }

        .module-group h3 {
            font-size: 17px;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .module-group h3 .badge {
            font-size: 13px;
            font-weight: 500;
            padding: 0 12px;
            border-radius: 16px;
            line-height: 24px;
        }

        .checklist-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .checklist-table th {
            background: #f8fafc;
            text-align: left;
            padding: 10px 14px;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 2px solid #dce2ec;
            font-size: 13px;
        }

        .checklist-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #e9edf4;
            vertical-align: top;
        }

        .checklist-table tr:hover td {
            background: #fafbfc;
        }

        .result-icon {
            font-weight: 600;
            white-space: nowrap;
        }

        .result-icon.pass {
            color: #16a34a;
        }
        .result-icon.fail {
            color: #dc2626;
        }
        .result-icon.warn {
            color: #f59e0b;
        }

        .code-loc {
            font-family: ui-monospace, "SF Mono", Menlo, monospace;
            font-size: 13px;
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 4px;
            color: #1e293b;
            white-space: nowrap;
        }

        .suggestion {
            font-size: 14px;
            color: #1e293b;
        }

        .suggestion .auto-fix {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            font-size: 12px;
            font-weight: 500;
            padding: 0 10px;
            border-radius: 12px;
            margin-left: 6px;
        }

        .empty-cell {
            color: #94a3b8;
            font-size: 13px;
        }

        /* 图例 */
        .legend {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            padding: 12px 0 4px 0;
            font-size: 14px;
            color: #475569;
        }

        .legend span {
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .legend .dot {
            display: inline-block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
        }

        .legend .dot.green {
            background: #16a34a;
        }
        .legend .dot.red {
            background: #dc2626;
        }
        .legend .dot.yellow {
            background: #f59e0b;
        }

        /* 页脚 */
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9edf4;
            font-size: 14px;
            color: #94a3b8;
            text-align: center;
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .container {
                padding: 20px 16px;
            }
            .overview-grid {
                grid-template-columns: repeat(3, 1fr);
                padding: 16px;
            }
            .overview-item .number {
                font-size: 24px;
            }
            .module-table,
            .checklist-table {
                font-size: 13px;
            }
            .module-table th,
            .module-table td,
            .checklist-table th,
            .checklist-table td {
                padding: 8px 10px;
            }
            .code-loc {
                font-size: 12px;
                white-space: normal;
                word-break: break-all;
            }
        }

        @media print {
            body {
                background: #fff;
                padding: 20px;
            }
            .container {
                box-shadow: none;
                padding: 20px;
            }
            .module-table tr:hover td,
            .checklist-table tr:hover td {
                background: transparent;
            }
        }
    </style>
</head>
<body>
    <div class="container">

        <!-- ======== 报告标题 ======== -->
        <div class="report-header">
            <h1>适老化设计规范检测报告</h1>
            <div class="subtitle">生成时间：2026-07-16 14:30 &nbsp;·&nbsp; 项目类型：Web</div>
        </div>

        <!-- ======== 第一部分：总览 ======== -->
        <h2 style="font-size:18px; font-weight:600; color:#0f172a; margin-bottom:12px;">一、总览</h2>

        <div class="overview-grid">
            <div class="overview-item">
                <div class="number">7</div>
                <div class="label">检测模块</div>
            </div>
            <div class="overview-item">
                <div class="number">36</div>
                <div class="label">检查项总数</div>
            </div>
            <div class="overview-item">
                <div class="number pass">21</div>
                <div class="label">✅ 通过</div>
            </div>
            <div class="overview-item">
                <div class="number fail">10</div>
                <div class="label">❌ 不通过</div>
            </div>
            <div class="overview-item">
                <div class="number warn">5</div>
                <div class="label">⚠️ 待确认</div>
            </div>
            <div class="overview-item">
                <div class="number rate">58.3%</div>
                <div class="label">合规率</div>
            </div>
        </div>

        <div class="summary-text">
            <strong>评估摘要：</strong>
            本次检测发现主要问题集中在【字体大小】和【颜色对比度】两个模块。
            适老版界面中的主标题字体普遍偏小（当前 18px，要求 ≥ 24px），
            部分按钮文本与背景对比度不足（当前约 3.2:1，要求 ≥ 4.5:1）。
            建议优先修复这两类问题，以提升老年用户的阅读体验。
            高风险项（严重）共 2 项，建议优先处理。
        </div>

        <!-- ======== 第二部分：模块统计 ======== -->
        <h2 class="section-title">二、模块检测结果</h2>

        <table class="module-table">
            <thead>
                <tr>
                    <th>模块</th>
                    <th>检查项</th>
                    <th>通过</th>
                    <th>不通过</th>
                    <th>待确认</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>字体与排版</td>
                    <td>5</td>
                    <td>2</td>
                    <td>2</td>
                    <td>1</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
                <tr>
                    <td>颜色与对比度</td>
                    <td>2</td>
                    <td>0</td>
                    <td>2</td>
                    <td>0</td>
                    <td><span class="status-badge fail">不通过</span></td>
                </tr>
                <tr>
                    <td>交互与操作</td>
                    <td>10</td>
                    <td>6</td>
                    <td>3</td>
                    <td>1</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
                <tr>
                    <td>验证码</td>
                    <td>4</td>
                    <td>1</td>
                    <td>0</td>
                    <td>3</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
                <tr>
                    <td>广告与安全</td>
                    <td>4</td>
                    <td>3</td>
                    <td>1</td>
                    <td>0</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
                <tr>
                    <td>入口与导航</td>
                    <td>7</td>
                    <td>3</td>
                    <td>2</td>
                    <td>2</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
                <tr>
                    <td>兼容性</td>
                    <td>4</td>
                    <td>2</td>
                    <td>1</td>
                    <td>1</td>
                    <td><span class="status-badge warn">需改进</span></td>
                </tr>
            </tbody>
        </table>

        <div class="legend">
            <span><span class="dot green"></span> 通过</span>
            <span><span class="dot yellow"></span> 需改进</span>
            <span><span class="dot red"></span> 不通过</span>
        </div>

        <!-- ======== 第三部分：逐项检查清单 ======== -->
        <h2 class="section-title">三、逐项检查清单</h2>

        <!-- 模块一 -->
        <div class="module-group">
            <h3>模块一：字体与排版（可感知性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1.1</td>
                        <td>是否提供字体大小调整功能</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>网站规范 1.2.3</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                    <tr>
                        <td>1.2</td>
                        <td>适老版主信息字体 ≥ 30dp/pt</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 1.1</td>
                        <td>当前主标题 18px</td>
                        <td><span class="code-loc">src/styles/global.css:45</span></td>
                        <td class="suggestion">调整为 30dp/pt 以上 <span class="auto-fix">自动修复</span></td>
                    </tr>
                    <tr>
                        <td>1.3</td>
                        <td>适老版一般字体 ≥ 18dp/pt</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 1.1</td>
                        <td>正文字体 14px</td>
                        <td><span class="code-loc">src/styles/global.css:78</span></td>
                        <td class="suggestion">调整为 18dp/pt 以上 <span class="auto-fix">自动修复</span></td>
                    </tr>
                    <tr>
                        <td>1.4</td>
                        <td>行距 ≥ 1.3倍</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>APP规范 1.2</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                    <tr>
                        <td>1.5</td>
                        <td>移动网页提供 ≥ 18dp/pt 大字体</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>网站规范 1.2.3</td>
                        <td>移动端默认字体 14px</td>
                        <td><span class="code-loc">src/styles/global.css:78</span></td>
                        <td class="suggestion">调整为 ≥ 18dp/pt 并支持系统字体缩放 <span class="auto-fix">自动修复</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 模块二 -->
        <div class="module-group">
            <h3>模块二：颜色与对比度（可感知性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2.1</td>
                        <td>对比度 ≥ 4.5:1</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 1.3</td>
                        <td>按钮文本 #999 / 背景 #fff，对比度 3.2:1</td>
                        <td><span class="code-loc">src/components/Button.css:12</span></td>
                        <td class="suggestion">将文本色调整为 #555 以上 <span class="auto-fix">自动修复</span></td>
                    </tr>
                    <tr>
                        <td>2.2</td>
                        <td>非颜色传递信息</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 1.4</td>
                        <td>错误提示仅用红色标识，无文字说明</td>
                        <td><span class="code-loc">src/components/Form.tsx:67</span></td>
                        <td class="suggestion">增加文字或图标辅助提示</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 模块三 -->
        <div class="module-group">
            <h3>模块三：交互与操作（可操作性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>3.1</td><td>App 主要组件可点击区域 ≥ 60×60dp/pt</td><td><span class="result-icon fail">❌ 不通过</span></td><td>APP规范 2.1</td><td>主按钮高度 88rpx≈44pt</td><td><span class="code-loc">app.wxss:118</span></td><td class="suggestion">提升至 ≥ 120rpx（60pt）<span class="auto-fix">自动修复</span></td></tr>
                    <tr><td>3.2</td><td>App 其他页面可点击区域 ≥ 44×44dp/pt</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 2.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.3</td><td>App 弹窗关闭按钮 ≥ 44×44dp/pt</td><td><span class="result-icon fail">❌ 不通过</span></td><td>APP规范 2.4</td><td>搜索浮层无关闭按钮</td><td><span class="code-loc">index.wxml:188</span></td><td class="suggestion">右上角添加 ≥ 88rpx 关闭按钮</td></tr>
                    <tr><td>3.4</td><td>App 避免 3 指以上复杂手势</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 2.2</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.5</td><td>App 限时操作留出充足时间</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 2.3</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.6</td><td>网站支持全程键盘操作</td><td><span class="result-icon pass">✅ 通过</span></td><td>网站规范 服务原则2</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.7</td><td>网站提供特大鼠标指针</td><td><span class="result-icon pass">✅ 通过</span></td><td>网站规范 服务原则2</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.8</td><td>网站多媒体键盘可控</td><td><span class="result-icon pass">✅ 通过</span></td><td>网站规范 2.3</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>3.9</td><td>网站无不可关闭的广告弹窗</td><td><span class="result-icon warn">⚠️ 待确认</span></td><td>网站规范 2.4.1</td><td>未检测到网站项目</td><td><span class="empty-cell">-</span></td><td class="suggestion">如为网站请确认弹窗关闭机制</td></tr>
                    <tr><td>3.10</td><td>网站交易提交可逆/10分钟可撤销</td><td><span class="result-icon pass">✅ 通过</span></td><td>网站规范 2.6.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                </tbody>
            </table>
        </div>

        <!-- 模块四 -->
        <div class="module-group">
            <h3>模块四：验证码（可感知性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>4.1</td>
                        <td>App 验证码提供语音/文字替代</td>
                        <td><span class="result-icon warn">⚠️ 待确认</span></td>
                        <td>APP规范 1.5</td>
                        <td>未检测到 App 验证码组件</td>
                        <td><span class="empty-cell">-</span></td>
                        <td class="suggestion">如有验证码请确认是否提供替代形式</td>
                    </tr>
                    <tr>
                        <td>4.2</td>
                        <td>网站验证码放大 ≥ 2倍</td>
                        <td><span class="result-icon warn">⚠️ 待确认</span></td>
                        <td>网站规范 1.4.3</td>
                        <td>未检测到网站验证码组件</td>
                        <td><span class="empty-cell">-</span></td>
                        <td class="suggestion">如有验证码请确认是否支持放大</td>
                    </tr>
                    <tr>
                        <td>4.3</td>
                        <td>网站验证码同时提供放大和替代形式</td>
                        <td><span class="result-icon warn">⚠️ 待确认</span></td>
                        <td>网站规范 1.4.3</td>
                        <td>未检测到网站验证码组件</td>
                        <td><span class="empty-cell">-</span></td>
                        <td class="suggestion">两种形式需同时存在</td>
                    </tr>
                    <tr>
                        <td>4.4</td>
                        <td>网站限时验证码提供语音告知和延长</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>网站规范 1.4.4</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 模块五 -->
        <div class="module-group">
            <h3>模块五：广告与诱导（安全性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>5.1</td><td>严禁广告内容及插件</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 5.1.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>5.2</td><td>严禁诱导下载/付款按键</td><td><span class="result-icon fail">❌ 不通过</span></td><td>APP规范 5.1.2 / 网站规范 2.4.2</td><td>发现"立即下载"按钮</td><td><span class="code-loc">src/components/Promote.tsx:24</span></td><td class="suggestion">移除诱导性按钮或移至非适老版界面</td></tr>
                    <tr><td>5.3</td><td>严禁随机广告弹窗</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 5.1.1 / 网站规范 2.4.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>5.4</td><td>个人信息收集遵循最小必要原则</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 5.2</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                </tbody>
            </table>
        </div>

        <!-- 模块六 -->
        <div class="module-group">
            <h3>模块六：入口与导航（可理解性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>6.1</td>
                        <td>App 首次安装时提供适老化引导</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 3.1</td>
                        <td>首次启动无适老版引导提示</td>
                        <td><span class="code-loc">app.js:12（onLaunch）</span></td>
                        <td class="suggestion">在首次启动时弹出适老版切换引导</td>
                    </tr>
                    <tr>
                        <td>6.2</td>
                        <td>App 首页具备显著"长辈版"入口</td>
                        <td><span class="result-icon fail">❌ 不通过</span></td>
                        <td>APP规范 3.1</td>
                        <td>首页未发现"长辈版"入口</td>
                        <td><span class="code-loc">src/pages/Home.tsx</span></td>
                        <td class="suggestion">在顶部导航或设置中添加入口</td>
                    </tr>
                    <tr>
                        <td>6.3</td>
                        <td>App 支持"长辈版"搜索直达</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>APP规范 3.1</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                    <tr>
                        <td>6.4</td>
                        <td>网站避免专业词语或网络新词语</td>
                        <td><span class="result-icon warn">⚠️ 待确认</span></td>
                        <td>网站规范 3.1.1</td>
                        <td>未检测到网站项目</td>
                        <td><span class="empty-cell">-</span></td>
                        <td class="suggestion">如为网站请对照规范确认</td>
                    </tr>
                    <tr>
                        <td>6.5</td>
                        <td>网站操作流程与常规认知一致</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>网站规范 3.1.2</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                    <tr>
                        <td>6.6</td>
                        <td>网站不修改公认通用名称或功能标识</td>
                        <td><span class="result-icon warn">⚠️ 待确认</span></td>
                        <td>网站规范 3.1.3</td>
                        <td>部分按钮命名非标准</td>
                        <td><span class="code-loc">src/components/Nav.tsx</span></td>
                        <td class="suggestion">建议对照设计规范确认</td>
                    </tr>
                    <tr>
                        <td>6.7</td>
                        <td>网站提供操作状态告知和撤销功能</td>
                        <td><span class="result-icon pass">✅ 通过</span></td>
                        <td>网站规范 3.1.4</td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                        <td><span class="empty-cell">-</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 模块七 -->
        <div class="module-group">
            <h3>模块七：兼容性（兼容性）</h3>
            <table class="checklist-table">
                <thead>
                    <tr>
                        <th style="width:50px;">序号</th>
                        <th>检查项</th>
                        <th style="width:80px;">结果</th>
                        <th style="width:140px;">规范条款</th>
                        <th>问题描述</th>
                        <th style="width:160px;">代码定位</th>
                        <th>修改建议</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>7.1</td><td>App 不禁用辅助设备接入</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 4.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>7.2</td><td>App 辅助工具开启时所有组件正常</td><td><span class="result-icon pass">✅ 通过</span></td><td>APP规范 4.1</td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td><td><span class="empty-cell">-</span></td></tr>
                    <tr><td>7.3</td><td>网站兼容主流操作系统及浏览器</td><td><span class="result-icon fail">❌ 不通过</span></td><td>网站规范 4.1</td><td>browserslist 未覆盖 IE11 和旧版 Safari</td><td><span class="code-loc">package.json:78</span></td><td class="suggestion">扩展 browserslist 覆盖主流浏览器</td></tr>
                    <tr><td>7.4</td><td>网站组件样式跨浏览器一致</td><td><span class="result-icon warn">⚠️ 待确认</span></td><td>网站规范 4.2.1</td><td>使用了 -webkit- 私有前缀</td><td><span class="code-loc">src/styles/vendor.css:15</span></td><td class="suggestion">确保跨浏览器兼容性测试通过</td></tr>
                </tbody>
            </table>
        </div>

        <!-- ======== 报告说明 ======== -->
        <div style="margin-top:40px; padding-top:20px; border-top:1px solid #e9edf4; font-size:14px; color:#64748b;">
            <p><strong>报告说明：</strong></p>
            <ul style="list-style:none; padding:0; margin:6px 0 0 0;">
                <li style="display:inline-block; margin-right:24px;">✅ 通过 — 完全符合规范</li>
                <li style="display:inline-block; margin-right:24px;">❌ 不通过 — 不符合规范，需修复</li>
                <li style="display:inline-block;">⚠️ 待确认 — 需人工确认或规范未明确</li>
            </ul>
            <p style="margin-top:8px; font-size:13px; color:#94a3b8;">
                <span class="auto-fix" style="background:#dbeafe; color:#1d4ed8; padding:0 10px; border-radius:12px; font-weight:500;">自动修复</span>
                标记表示该问题支持 <code>--fix</code> 一键修复
            </p>
        </div>

        <!-- ======== 页脚 ======== -->
        <div class="footer">
            报告由 Elderly UI Audit Skill 自动生成 &nbsp;·&nbsp; 基于工信部适老化设计规范
        </div>

    </div>
</body>
</html>
```

---

**使用方式**：Claude 在生成报告时，将上述模板中的数据（时间、数量、问题描述、代码定位等）替换为实际检测结果，保存为 `elderly-audit-report.html` 并告知用户文件路径。用户双击即可在浏览器中打开查看。


---


### 第四步：自动修复

对于可自动修复的问题，询问用户：
```
检测到以下问题可以自动修复：
1. 字体大小不足 → 调整为 30dp/pt
2. 对比度不足 → 调整为 4.5:1
3. 行距不足 → 调整为 1.3倍

是否执行自动修复？[Y/n]
```

**自动修复原则：**
- 仅修改样式文件中的数值。
- 保留原有样式作为注释备份（例如添加 `/* original: 16px */`）。
- 不修改业务逻辑代码。
- 每次修改后提示用户验证。

## 规范引用
- 《互联网网站适老化通用设计规范》（工信部）
- 《移动互联网应用（APP）适老化通用设计规范》（工信部）
- GB/T 37668-2019《信息技术 互联网内容无障碍可访问性技术要求与测试方法》

## 交互示例

**用户输入**：
> 帮我检查适老化

**Skill 响应**：
```
正在识别项目类型... 检测到 React Web 项目。
开始扫描 CSS 文件...
✅ 字体大小调整功能：已提供（通过 root 变量）
❌ 主标题字体 18px，低于适老版建议 24px
❌ 对比度 3.2:1，低于 4.5:1
✅ 无广告插件
...

已生成报告：elderly-audit-report.md
是否自动修复上述 2 个问题？(y/n)
```

## 扩展能力
- 支持通过 `--fix` 参数直接执行自动修复。
- 支持 `--only` 指定只检测某一模块（如 `--only font`）。
- 支持输出 JSON 格式报告以便集成到 CI/CD。


---

## 反馈与贡献

如果你在使用过程中发现以下情况，欢迎通过下方渠道反馈：

- 某条规范条款的检查逻辑有遗漏或偏差
- 新增的适老化规范需要补充支持
- 对自动修复功能有改进建议
- 遇到 Bug 或误报 / 漏报

**反馈渠道**：
- 提交 Issue：https://github.com/XuYuting133/elderly-ui-audit/issues
- 项目主页：https://github.com/XuYuting133/elderly-ui-audit

你的反馈会让这个 Skill 更加完善，造福更多开发者。感谢！
