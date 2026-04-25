# 美团热敏打印机管理工具

一个用于门店热敏打印机管理和任务单打印的本地工具。项目通过 TCP Socket + ESC/POS 指令向美团热敏打印机发送格式化内容，支持多打印机配置、模板管理、定时打印、系统级定时任务导出，以及命令行直接打印。

适用场景包括后厨出菜、分菜档、前台检查单、早晚班任务单、库存盘点单等。

## 功能概览

| 功能 | 说明 |
| --- | --- |
| 多打印机管理 | 为不同打印机配置中文别名、IP、端口、类型和备注 |
| Web 管理后台 | 在浏览器中添加/编辑/删除打印机，测试连通性，管理任务和模板 |
| 一次性打印 | 通过命令行按别名或 IP 直接发送任务单 |
| 定时打印 | 支持每天、每周、每月定时打印 |
| 系统级任务导出 | macOS 导出为 launchd，Windows 导出为任务计划程序 |
| 模板管理 | 内置早班检查、晚班收尾、周报、月度盘点等模板，也可自定义 |
| 中文打印 | 使用 GB18030 编码，适配中文任务单内容 |

## 环境要求

- Python 3
- 电脑与打印机处于同一局域网
- 美团热敏打印机默认端口通常为 `9100`
- Web 管理后台依赖 `flask` 和 `apscheduler`

双击启动脚本会自动检查并安装 Web 依赖；如果手动安装，可执行：

```bash
python3 -m pip install flask apscheduler
```

Windows 环境可将 `python3` 替换为 `python`。

## 快速开始

### 1. 启动 Web 管理后台

推荐用 Web 后台完成首次配置。

macOS：

```bash
bash scripts/start.command
```

Windows：

```bat
scripts\start.bat
```

也可以直接运行后端：

```bash
cd scripts
python3 web_admin.py
```

启动后访问：

```text
http://localhost:5000
```

如果 `5000` 端口被占用，程序会自动切换到：

```text
http://localhost:5001
```

### 2. 添加打印机

在 Web 后台的“打印机管理”中点击“添加打印机”，填写：

| 字段 | 示例 | 说明 |
| --- | --- | --- |
| 别名 | 后厨 | 日常打印时使用的中文名称 |
| IP 地址 | 192.168.3.172 | 打印机在局域网内的地址 |
| 端口 | 9100 | 美团热敏打印机通常使用该端口 |
| 类型 | 后厨荤菜 | 可在后台自定义 |
| 备注 | 主厨房任务单 | 选填 |

添加后可以点击“测试”检查打印机是否可连接。

### 3. 打印测试单

配置好别名后，可以用命令行立即打印：

```bash
python3 scripts/print_to_printer.py --name 后厨 --title "测试单" --content "打印机连接正常\n请确认纸张和切纸"
```

也可以跳过配置，直接指定 IP 和端口：

```bash
python3 scripts/print_to_printer.py --ip 192.168.3.172 --port 9100 --title "测试单" --content "直接按 IP 打印"
```

正文内容居中打印：

```bash
python3 scripts/print_to_printer.py --name 后厨 --title "通知" --content "今日例会\n18:00 开始" --center
```

## 接入 QClaw / WorkBuddy

本项目根目录已经包含 `SKILL.md`，可以作为一个本地 AI 技能接入 QClaw 或 WorkBuddy。接入后，AI 可以根据自然语言自动调用本项目脚本，完成打印、配置查询、连通性检测、打开 Web 后台等操作。

### 接入前准备

先确认本地命令可用：

```bash
python3 scripts/print_to_printer.py --guide
python3 scripts/check_printer.py --ip 192.168.3.172 --port 9100
```

如果还没有配置打印机，建议先启动 Web 后台并添加打印机：

```bash
bash scripts/start.command
```

Windows 使用：

```bat
scripts\start.bat
```

### 通过 QClaw 接入

QClaw 识别本地技能时，通常需要一个带 `SKILL.md` 的技能目录。本项目已经满足这个结构：

```text
meituan-printer/
├── SKILL.md
├── README.md
├── scripts/
└── references/
```

接入方式：

1. 将整个 `meituan-printer` 目录放到 QClaw 的本地技能目录中，或在 QClaw 中选择“添加本地技能/导入技能”并指向该目录。
2. 确认 QClaw 能读取根目录的 `SKILL.md`。
3. 重新加载技能列表，或重启 QClaw。
4. 在对话中用打印相关指令触发技能。

可用示例：

```text
帮我启动美团打印机管理界面
列出已配置的打印机
检测后厨打印机是否在线
打印一张测试单到后厨，标题是测试单，内容是打印机连接正常
帮我创建一个每天 9 点打印的早班检查单
```

### 通过 WorkBuddy 接入

WorkBuddy 的使用方式类似：把整个项目目录作为一个技能目录导入，核心入口同样是 `SKILL.md`。

推荐步骤：

1. 将 `meituan-printer/` 放入 WorkBuddy 的技能目录，或通过 WorkBuddy 的技能管理页面导入该文件夹。
2. 保持目录结构不变，尤其不要单独移动 `SKILL.md` 或 `scripts/`。
3. 在 WorkBuddy 中刷新/重载技能。
4. 首次使用时先说“启动打印机管理界面”，通过 Web 后台完成打印机配置。

WorkBuddy 中可以这样使用：

```text
打开打印机 Web 后台
给后厨打一张早班任务单，内容是打卡拍照、检查冰柜温度、确认锅底库存
帮我查看现在有哪些打印机
新增一台打印机，别名叫前厅，IP 是 192.168.3.32，端口 9100
```

### AI 技能会做什么

接入后，AI 会优先使用 `SKILL.md` 中定义的工作流：

- 用户说“打印”“打单”“任务单”“检查单”时，确认打印机、标题和内容后调用 `scripts/print_to_printer.py`
- 用户说“配置打印机”“管理打印机”“定时打印”时，引导或启动 Web 管理后台
- 用户提供 IP 时，可调用 `scripts/check_printer.py` 做连通性检测
- 用户需要定时任务时，可通过 Web 后台创建，并可导出为系统级任务

注意：QClaw/WorkBuddy 需要有本机文件访问和命令执行权限，否则 AI 只能给出命令，不能直接替你执行打印或启动后台。

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `python3 scripts/print_to_printer.py --list` | 列出已配置的打印机 |
| `python3 scripts/print_to_printer.py --guide` | 查看命令行新手指南 |
| `python3 scripts/check_printer.py --ip <IP> --port 9100` | 检测打印机连通性，输出 JSON |
| `python3 scripts/web_admin.py` | 启动 Web 管理后台 |

打印脚本必填参数：

- `--title`：打印标题
- `--content`：打印正文，支持 `\n` 换行
- `--name` 或 `--ip`：二选一，用别名或 IP 指定目标打印机

## Web 后台能力

### 打印机管理

- 新增、编辑、删除打印机
- 检查打印机连通性
- 管理打印机类型
- 配置文件保存到 `scripts/config.json`

### 定时任务

- 创建每天、每周、每月定时打印任务
- 启用或暂停任务
- 立即执行一次任务
- 按打印机或频率分组查看任务
- 将任务导出到系统级定时任务

定时任务默认保存在：

```text
scripts/tasks.json
```

### 模板管理

- 查看内置模板
- 新建、编辑、删除自定义模板
- 创建定时任务时可直接套用模板

模板文件位于：

```text
scripts/templates/task_templates.json
```

## 系统级定时任务

Web 后台中的“载入系统”会把任务导出到操作系统，使任务不依赖 Web 服务进程也能执行。

| 系统 | 实现方式 |
| --- | --- |
| macOS | 写入 `~/Library/LaunchAgents/com.meituan-printer.<task-id>.plist` 并通过 `launchctl load` 加载 |
| Windows | 使用 `schtasks /create` 创建 `MeituanPrinter-<task-id>` 任务 |

如果任务不再需要，可在 Web 后台点击“移除”取消系统级任务。

## 配置文件

运行时主要使用这些文件：

```text
meituan-printer/
├── SKILL.md
├── README.md
├── config.example.json
├── references/
│   ├── onboarding.md
│   └── printer-config.md
└── scripts/
    ├── check_printer.py
    ├── platform_utils.py
    ├── print_to_printer.py
    ├── printer_types.json
    ├── start.bat
    ├── start.command
    ├── tasks.json
    ├── web_admin.py
    └── templates/
        ├── index.html
        └── task_templates.json
```

打印机配置由 Web 后台创建在：

```text
scripts/config.json
```

如果需要手动初始化，可参考 `config.example.json`，并将配置保存为 `scripts/config.json`：

```json
{
  "version": "1.0",
  "printers": [
    {
      "alias": "后厨",
      "ip": "192.168.3.172",
      "port": 9100,
      "type": "后厨荤菜",
      "remark": "主厨房任务单"
    }
  ]
}
```

## 打印格式

每张任务单会包含：

1. 居中大标题
2. 打印时间
3. 分隔线
4. 正文内容
5. 结尾提示“请按时完成各项工作”
6. 自动切纸指令

打印协议和编码：

- 协议：TCP Socket + ESC/POS
- 编码：GB18030
- 默认连接超时：5 秒

## 故障排查

| 现象 | 可能原因 | 处理方式 |
| --- | --- | --- |
| Web 后台打不开 | 服务未启动或端口变化 | 重新运行启动脚本，并查看终端输出的访问地址 |
| `localhost:5000` 无法访问 | 5000 被占用 | 尝试访问 `http://localhost:5001` |
| 打印连接超时 | 打印机离线、IP 错误或不在同一局域网 | 检查电源、网络和 IP 地址 |
| 连接被拒绝 | 端口错误或打印服务未就绪 | 确认端口为 `9100`，重启打印机后再试 |
| 找不到别名 | 尚未配置或别名输入不一致 | 运行 `python3 scripts/print_to_printer.py --list` 查看 |
| 中文乱码 | 打印机编码不兼容 | 确认设备支持 GB18030/中文 ESC/POS 打印 |
| 系统级任务未执行 | 系统任务未导出或打印机不可达 | 在 Web 后台确认“已导出”，并先手动执行一次任务 |

## 参考文档

- `references/onboarding.md`：面向新用户的操作指南
- `references/printer-config.md`：门店打印机 IP、用途和任务映射参考
- `SKILL.md`：给 AI 助手使用的技能说明和工作流

## 许可证

MIT License
