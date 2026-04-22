# Huawei Cloud ModelArts Skill
## 项目介绍

`huawei-cloud-modelarts-skill` 是一套适配 **华为云 ModelArts** 平台的技能工具集，旨在简化 AI 模型开发、训练、部署全流程的操作成本，提供高效的辅助脚本、自动化工具及最佳实践模板。

无论是 ModelArts 新手快速上手，还是资深开发者提升工作流效率，本项目都能提供针对性的工具支持，覆盖数据预处理、模型调优、部署运维等核心场景。

## 核心功能

* 🚀 **自动化脚本**：提供数据格式转换、模型导出、批量任务提交等脚本（`scripts/` 目录）

* 🔧 **实用工具**：包含日志分析、资源监控、配置管理等辅助工具（`tools/` 目录）

* 📋 **技能模板**：ModelArts 常见任务（如图像分类、文本生成）的标准化配置与执行流程（`SKILL.md` 详细说明）

* 🎯 **兼容性优化**：适配 ModelArts 平台环境，无缝对接华为云 OBS、AI 市场等服务

## 快速开始

### 1. 环境准备

* 操作系统：Linux/macOS/Windows（推荐 Linux 环境，适配 ModelArts 在线开发环境）

* Python 版本：3.7+

* 依赖安装：

```
\# 克隆仓库

git clone https://github.com/modelarts-agent/huawei-cloud-modelarts-skill.git

cd huawei-cloud-modelarts-skill

\# 安装依赖

pip install -r requirements.txt
```

### 2. 华为云配置

1. 登录 [华为云控制台](https://console.huaweicloud.com/)，开通 **ModelArts** 与 **OBS** 服务

2. 获取华为云访问密钥（AK/SK）：

* 进入「我的凭证」→「访问密钥」→「新增访问密钥」

* 保存 `credentials.csv` 文件（包含 AK/SK，请勿公开）


## 目录结构说明

```
huawei-cloud-modelarts-skill/

├── scripts/                # 核心自动化脚本目录

│   ├── init.sh     # 初始化脚本

│   ├── skill.py     # modelarts资源操作

├── tools/                  # 辅助工具

│   └── security.py # 安全脚本

├── README.md               # 项目说明（本文档）

├── SKILL.md                # 详细技能说明（含场景化教程）

└── requirements.txt        # 依赖清单
```

## 详细文档

* 完整功能说明与进阶用法：[SKILL.md](SKILL.md)

* 华为云 ModelArts 官方文档：[ModelArts 帮助中心](https://support.huaweicloud.com/modelarts/)

* OBS 存储使用指南：[OBS 官方文档](https://support.huaweicloud.com/obs/)

## 常见问题

### Q1：运行脚本时提示「OBS 访问失败」？

A：检查以下几点：

1. AK/SK 是否正确（避免空格、换行）

2. 区域是否匹配（如 ModelArts 部署在「华北 - 北京四」，region 需填 `cn-north-4`）

3. OBS 桶权限是否开放（建议给桶配置「公共读」或添加 ModelArts 服务授权）

### Q2：依赖安装失败？

A：尝试更换华为云镜像源：


```
pip install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple/
```

## 贡献指南

1. Fork 本仓库

2. 创建特性分支（`git checkout -b feature/xxx`）

3. 提交代码（`git commit -m "add: 新增xxx功能"`）

4. 推送分支（`git push origin feature/xxx`）

5. 提交 Pull Request

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源，详见 LICENSE 文件。

## 联系作者

若有问题或需求，可通过以下方式联系：

* GitHub Issues：[提交问题](https://github.com/modelarts-agent/huawei-cloud-modelarts-skill/issues)
