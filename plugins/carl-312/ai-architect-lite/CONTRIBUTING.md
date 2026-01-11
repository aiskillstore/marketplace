# Contributing to AI Architect Lite

[English](#english) | [中文](#中文)

---

## English

Thank you for your interest in contributing to AI Architect Lite! This document provides guidelines for contributing.

### How to Contribute

1. **Fork the Repository**
2. **Create a Branch**: `git checkout -b feature/your-feature-name`
3. **Make Changes**: Follow the coding standards below
4. **Test Your Changes**: Ensure scripts work as expected
5. **Commit**: Use clear, descriptive commit messages
6. **Push**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Describe your changes clearly

### Coding Standards

#### Python Code
- Follow PEP 8 style guide
- Use type hints (Python 3.8+ compatible)
- Add docstrings to functions and modules
- Keep functions small and focused
- Use `pathlib.Path` for file operations

#### Documentation
- Maintain bilingual (English/Chinese) README
- Update relevant docs when adding features
- Use clear, concise language
- Include examples where helpful

#### Commit Messages
```
type(scope): brief description

Detailed explanation if needed

Examples:
- feat(scripts): add validation to append_log.py
- fix(docs): correct typo in README
- docs(references): update lite-protocol examples
```

### Types of Contributions

- 🐛 **Bug Reports**: Open an issue with reproduction steps
- ✨ **Feature Requests**: Describe the use case and benefit
- 📝 **Documentation**: Improve clarity or add examples
- 🔧 **Code**: Fix bugs or implement features
- 🌍 **Translations**: Help with bilingual documentation

### Testing

Before submitting:
1. Test scripts with Python 3.8, 3.9, 3.10+
2. Verify file operations don't escape project root
3. Check that documentation is accurate
4. Ensure no secrets or sensitive data are included

### Code Review Process

1. Maintainers will review within 1 week
2. Address feedback in your branch
3. Once approved, changes will be merged
4. Your contribution will be credited

### Questions?

Open an issue with the `question` label or start a discussion.

---

## 中文

感谢你对 AI Architect Lite 的贡献兴趣！本文档提供贡献指南。

### 如何贡献

1. **Fork 仓库**
2. **创建分支**：`git checkout -b feature/你的功能名称`
3. **进行修改**：遵循下面的编码标准
4. **测试修改**：确保脚本按预期工作
5. **提交**：使用清晰、描述性的提交信息
6. **推送**：`git push origin feature/你的功能名称`
7. **开启 Pull Request**：清楚描述你的修改

### 编码标准

#### Python 代码
- 遵循 PEP 8 风格指南
- 使用类型提示（兼容 Python 3.8+）
- 为函数和模块添加文档字符串
- 保持函数小而专注
- 使用 `pathlib.Path` 进行文件操作

#### 文档
- 维护双语（英文/中文）README
- 添加功能时更新相关文档
- 使用清晰、简洁的语言
- 在有帮助的地方包含示例

#### 提交信息
```
type(scope): 简短描述

如需要，提供详细解释

示例：
- feat(scripts): 为 append_log.py 添加验证
- fix(docs): 修正 README 中的拼写错误
- docs(references): 更新 lite-protocol 示例
```

### 贡献类型

- 🐛 **Bug 报告**：开启 issue 并提供复现步骤
- ✨ **功能请求**：描述使用场景和好处
- 📝 **文档**：改进清晰度或添加示例
- 🔧 **代码**：修复 bug 或实现功能
- 🌍 **翻译**：帮助完善双语文档

### 测试

提交前：
1. 使用 Python 3.8、3.9、3.10+ 测试脚本
2. 验证文件操作不会逃逸项目根目录
3. 检查文档准确性
4. 确保不包含密钥或敏感数据

### 代码审查流程

1. 维护者将在 1 周内审查
2. 在你的分支中处理反馈
3. 批准后，修改将被合并
4. 你的贡献将被记录

### 有问题？

使用 `question` 标签开启 issue 或开始讨论。

---

**Thank you for making AI Architect Lite better! / 感谢你让 AI Architect Lite 变得更好！**
