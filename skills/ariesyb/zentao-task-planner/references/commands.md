# 命令索引

## 环境

操作禅道必填变量（优先读取进程环境变量，其次读取 `.env` 文件）：

```env
ZENTAO_BASE_URL=https://your-zentao-instance.com/zentao/
ZENTAO_ACCOUNT=your-account
ZENTAO_PASSWORD=your-password
ZENTAO_NAME=your-name
```
ZENTAO_ACCOUNT一般是ZENTAO_NAME的拼音

### 凭据安全

- 推荐通过环境变量注入凭据；`.env` 只是本地便利选项，可通过 `--env-file` 指定路径。
- `.env` 只保存在本机并加入 `.gitignore`，绝不能提交到仓库或打进技能包（技能包内只提供 `.env.example` 模板）。
- 凭据只会用于登录用户自己配置的 `ZENTAO_BASE_URL`，脚本所有网络请求都限制在该地址内，不访问第三方服务、无遥测。
- 详见 [../SECURITY.md](../SECURITY.md)。

安装脚本依赖：

```bash
pip install requests beautifulsoup4 python-dotenv chinese-calendar
```

脚本默认读取 `skills/zentao-task-planner/.env`，推荐存放到该目录，方便下次使用，也可通过 `--env-file` 指定。

规划后的任务请保存到本地和.env一个目录，下一次可以查看上次规划的任务作为参考。

所有操作禅道的脚本都必须先预览，只有用户确认后加 `--execute` 才会真正执行。

## 脚本索引

- [workdays.md](workdays.md)：查询当前或下一段连续工作日
- [list-tasks.md](list-tasks.md)：查看任务列表
- [get-task-types.md](get-task-types.md)：获取任务类型枚举
- [create-tasks.md](create-tasks.md)：批量创建任务
- [finish-tasks.md](finish-tasks.md)：按日期完成任务
- [repair-finish-date.md](repair-finish-date.md)：修复任务完成日期
- [close-tasks.md](close-tasks.md)：关闭已完成任务
