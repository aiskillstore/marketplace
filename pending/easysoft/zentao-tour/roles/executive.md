# 高管视角

用户选了这个身份，意味着他不想看"一条记录"而想看"整体情况"。陪他从几个入口溜一圈全局数据，**只读、不写**，也**别列 4 个维度**。

## 开场：一句话点路，再让他挑一块最关心的

示例开场：

> "高管视角其实就是从不同角度扫一眼全局——项目节奏、产品健康度、发布动静、团队声音，都是入口。我们不用四个都看，挑你现在最想知道的那一块深挖就够了。
>
> 你现在最想先看哪块？"

用 AskQuestion 给 4 个选项：

- 项目节奏
- 产品健康度（需求 / Bug 分布）
- 发布与版本
- 团队反馈与工单

根据选择从下面对应段切入。**不要全部都看一遍**，陪用户挖他真正关心的那 1–2 个就好。

## 如果他关心项目节奏

```bash
zentao project --filter='status:doing' --pick=id,name,begin,end,progress
```

让他扫一眼，问："有没有哪条看着不对劲？进度慢的、日期要到的？"——挑出一个深入看：

```bash
zentao execution --project=<id> --pick=id,name,status
zentao task --execution=<执行ID> --pick=id,status --format=json
```

后一条可以本地聚合一下"wait/doing/done 各多少"，用一句话汇报给用户。

## 如果他关心产品健康度

```bash
zentao product --pick=id,name,status
```

挑他在意的那个产品：

```bash
zentao story --product=<id> --pick=id,pri,stage --format=json
zentao bug --product=<id> --pick=id,severity,pri,status --format=json
```

把 JSON 结果做个简单统计（高优先级未处理需求数、严重 Bug 数），用两句话告诉用户："《XXX》当前有 N 条高优需求还没排期，严重 Bug M 条——主要堆在这几个 severity 上。"

## 如果他关心发布与版本

```bash
zentao release --product=<id> --pick=id,name,date,status
zentao build --project=<projectID> --pick=id,name,date
```

挑最近一次已发布和最近一次待发布，用一句话把时间节点说出来。

## 如果他关心团队声音

```bash
zentao feedback --product=<id> --pick=id,title,status,pri
zentao ticket --product=<id> --pick=id,title,status,pri
```

扫一下高频类别或未处理量，用一两句汇报热点。

## 顺势介绍一招"驾驶舱"技巧

挖完用户关心的那块之后，顺手点一句**回顾 + 钩子**：

> "刚才我们用了不到十条命令，就把《XXX》这块的健康度摸清楚了——其实这些查询加 `--format=json` 之后都能本地汇总，就是一个极简驾驶舱。你想要哪类数字定期看，我都可以帮你凑一个小脚本。"

这是钩子，不必当场实现，除非用户明确要。

## 自然收尾

- 用户满足了——用一句话回顾他看过的那一两个维度，然后回到 [../SKILL.md](../SKILL.md) 的收尾流程。
- 用户问起操作类的事（比如"这条 Bug 谁来解"）——说"这就得换开发视角 / 项目经理视角了"，邀请切换。

## 查询速查（给 AI 用）

| 关注点 | 命令 |
|--------|------|
| 进行中的项目 | `zentao project --filter='status:doing' --pick=id,name,progress,begin,end` |
| 项目下的执行 | `zentao execution --project=<id> --pick=id,name,status`|
| 任务状态聚合 | `zentao task --execution=<id> --pick=status --format=json` |
| 产品下需求概览 | `zentao story --product=<id> --pick=id,pri,stage --format=json` |
| 产品下 Bug 概览 | `zentao bug --product=<id> --pick=id,severity,pri,status --format=json` |
| 即将 / 最近发布 | `zentao release --product=<id> --pick=id,name,date,status` |
| 版本 | `zentao build --project=<id> --pick=id,name,date` |
| 用户反馈 | `zentao feedback --product=<id> --pick=id,title,status,pri` |
| 工单 | `zentao ticket --product=<id> --pick=id,title,status,pri` |

> 本视角完全只读，不要触发任何 create / update / delete。
