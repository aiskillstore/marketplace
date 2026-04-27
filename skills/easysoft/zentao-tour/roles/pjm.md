# 项目经理视角

用户选了这个身份，意味着他关心的是"怎么把事情安排下去、推进下去"。陪他走一段"拉起一个项目 → 排一个 sprint → 把需求拆成任务、安排到人 → 跑一圈状态流转"的路子——**不要编号也不要列清单**，但开场顺口把这段路点一下，让他不迷路。

## 开场：一句话点路，马上动手

示例开场（可变奏，别照抄）：

> "那我们大概这样走：先挂个项目到某个产品下面，再开一个 sprint，把两三条需求拆成任务、排到人，最后跑一遍状态流转让你感受一下节奏。随时说换或者停都行。
>
> 先看看你们禅道里现在有哪些产品——项目总得挂在某个产品下面。"

顺手跑一下，让用户从现有产品里挑：

```bash
zentao product --pick=id,name --limit=10
```

如果一条都没有，别卡住，顺手建议："要不我们借 PM 视角先捏一个玩具产品出来？"（跳到 [pm.md](pm.md) 的建产品那段，建完回来）。

## 拉起项目这件事，用最简几个字段就够

和用户聊清三样就可以动手：

- 项目叫什么（`name`，建议与产品呼应，比如"XXX v1 研发"）
- 起止日期（`begin` / `end`，给 4 周 / 8 周 / 12 周 三挡让他挑）
- 绑定哪个产品（`products`）

征得同意后执行：

```bash
zentao project create --name="..." --begin=<YYYY-MM-DD> --end=<YYYY-MM-DD> --products=<产品ID>
```

记下返回的项目 ID——后面 `zentao execution` 的 `--project` 要用。

用**回顾 + 钩子**的一句话过渡："《XXX 研发》已经开张了，挂在《产品 XXX》下面——项目像个大框，还得切成一段段小冲刺才推得动。你们团队习惯两周一个 sprint 还是更长？"

## 接着把 Sprint 建出来

用户答完周期后：

```bash
zentao execution create --project=<项目ID> --name="Sprint 1" --begin=... --end=...
```

记下返回的执行 ID——后面 `zentao task create --execution=<执行ID>` 会一直用到。

一句话过渡到下一段："Sprint 1 挂好了——空的 sprint 没啥意思，我们挑几条需求塞进来拆成任务？"

## 顺势把需求拆成任务

> "既然 sprint 立起来了，我们挑几条需求塞进去？"

先看可以塞什么：

```bash
zentao story --product=<产品ID> --filter='stage:wait' --pick=id,title,pri
```

和用户挑 2–3 条就够，别贪多。对每一条都问一句"你打算把它拆成几个任务？给谁做？预估几小时？"——用户给出一组就创建一个：

```bash
zentao task create --execution=<执行ID> --name="..." --type=devel --assignedTo=<账号> --estimate=<小时>
```

拆到第三条的时候可以主动刹车："节奏差不多了，想不想看看现在已经排成什么样？"

## 让他看到"进度"是什么感觉

```bash
zentao task --execution=<执行ID> --pick=id,name,status,assignedTo,estimate
```

如果用户对流转感兴趣，顺手演示一个任务从开始到完成：

```bash
zentao task start <id>
zentao task finish <id> --consumed=<实际小时>
```

边演示边用一句话解释 status 从 `wait` → `doing` → `done` 的变化，就足够了。

跑完一圈之后来一句**具体的回顾**（不要空泛夸奖）："这一趟你其实已经把项目经理最核心的一条线串起来了：**产品 → 项目 → sprint → 任务 → 状态流转**。禅道里所有的进度汇总、人力统计都是从这条线长出来的。"

## 自然收尾

出现下列信号之一就可以收：

- 用户开始问"那 Bug 呢 / 测试呢"——介绍测试视角的存在，邀请切换。
- 用户自己说"差不多了"——就着话头回顾："你从一个产品拉起了项目、开了第一个 sprint、把几条需求拆成了任务，还跑了一遍状态流转。"
- 对话自然淡下来——回到 [../SKILL.md](../SKILL.md) 的收尾流程，问要不要换身份或清理演示数据。

## 写操作速查（给 AI 用）

| 动作 | 命令 |
|------|------|
| 建项目 | `zentao project create --name= --begin= --end= --products=<产品ID>` |
| 建 Sprint | `zentao execution create --project= --name= --begin= --end=` |
| 建任务 | `zentao task create --execution= --name= --type=devel --assignedTo= --estimate=` |
| 启动任务 | `zentao task start <id>` |
| 完成任务 | `zentao task finish <id> --consumed=<小时>` |
| 查执行下任务 | `zentao task --execution=<id> --pick=id,name,status,assignedTo` |

> 本视角目前剧情比较轻，欢迎根据真实团队节奏补得更丰满。
