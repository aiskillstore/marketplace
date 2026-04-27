# 命令索引

## 环境

操作禅道必填变量：

```env
ZENTAO_BASE_URL=https://your-zentao-instance.com/zentao/
ZENTAO_ACCOUNT=your-account
ZENTAO_PASSWORD=your-password
ZENTAO_NAME=your-name
```
ZENTAO_ACCOUNT一般是ZENTAO_NAME的拼音

安装脚本依赖：

```bash
pip install requests beautifulsoup4 python-dotenv chinese-calendar
```

脚本默认读取 `skills/zentao-task-planner/.env`，推荐存放到该目录，方便下次使用，也可通过 `--env-file` 指定。

规划后的任务请保存到本地和.env一个目录，下一次可以查看上次规划的任务作为参考。

所有操作禅道的脚本都必须先预览，只有用户确认后加 `--execute` 才会真正执行。