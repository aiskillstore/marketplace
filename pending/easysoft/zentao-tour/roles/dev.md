# 开发视角

用户选了这个身份，意味着他最熟悉的是"我今天写啥 / 还有啥 Bug 要修"。陪他走一段"认领一个任务 → 开干 → 交工 → 顺手解只 Bug"的路子——**别编号也别列清单**，但开场顺口点一下这段路会怎么走。

## 开场：一句话点路 + 先确认身份

示例开场：

> "开发视角我们大概这样走：先确认是哪个账号在开发，翻翻手头有啥任务，挑一条从 wait 推到 done，最后顺手解只 Bug 看看 resolution 都有哪些选项。随时说换或者停。
>
> 先确认下身份——"

```bash
zentao profile
```

然后顺口一句："看下手头有啥活。"

## 翻一翻"我的任务"

```bash
zentao task --execution=<执行ID> --filter='assignedTo:<当前账号>,status:wait' --pick=id,name,estimate
```

两种分支：

- **有活**：让用户挑一条："挑哪个先动手？"
- **没活**：顺水推舟："那我们去公共池里领一个。" 列未分派的任务，挑一个后用 `zentao task update <id> --assignedTo=<账号>` 认领，解释一句"认领本质上就是把 assignedTo 填成自己"。

## 把那条任务从 wait 推到 doing

和用户确认一下预计用时（`estimate`），如果原先没填可以现在补：

```bash
zentao task update <id> --estimate=<小时>
zentao task start <id>
```

口语化地说一句："现在状态就是 `doing` 了，同事在看板上能看到你接手了。"

## 交工

聊一下"真做完 / 实际耗了多久"，然后：

```bash
zentao task finish <id> --consumed=<实际小时>
```

如果用户好奇差别，用一两句解释 estimate 是预估、consumed 是真实耗时，后者会影响项目的成本统计。

## 顺手捏一个 Bug 走完流程

> "开发视角最常打的另一个交道就是 Bug。我们看看有没有分给你的。"

```bash
zentao bug --product=<产品ID> --filter='assignedTo:<当前账号>,status:active' --pick=id,title,severity,pri
```

挑一条看详情 `zentao bug <id>`，聊两句可能的原因，然后：

```bash
zentao bug resolve <id> --resolution=fixed
```

顺带提一下其他 `resolution` 选项（fixed / duplicate / external / bydesign / notrepro / postponed / willnotfix），让用户知道不是只有"修好了"一条路。

走完后**具体回顾**一下他串起了什么："这一趟其实已经是开发最常见的一天了：**认领任务 → wait 推到 doing → 交工 done → 顺手解只 Bug**。真实工作无非是把 estimate、consumed、resolution 这几个字段写准，后面项目经理看报表才有意义。"

## 自然收尾

- 用户问"测试那边怎么再验"——指测试视角。
- 用户满足地表示够了——简短回顾："你认领了一个任务、把它从 wait 推到了 done，还顺手解了一个 Bug。"
- 回到 [../SKILL.md](../SKILL.md) 的收尾流程。

## 写操作速查（给 AI 用）

| 动作 | 命令 |
|------|------|
| 看我的任务 | `zentao task --execution=<id> --filter='assignedTo:<账号>,status:wait'` |
| 认领任务 | `zentao task update <id> --assignedTo=<账号>` |
| 改预估 | `zentao task update <id> --estimate=<小时>` |
| 开干 | `zentao task start <id>` |
| 交工 | `zentao task finish <id> --consumed=<小时>` |
| 看我的 Bug | `zentao bug --product=<id> --filter='assignedTo:<账号>,status:active'` |
| 解决 Bug | `zentao bug resolve <id> --resolution=fixed` |

> 本视角偏轻量，欢迎结合 Git / Build 联动等真实研发流程继续丰富。
