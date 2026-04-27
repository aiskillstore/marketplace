# 测试视角

用户选了这个身份，意味着他对"怎么确保东西是对的 / 怎么把问题反馈出去"更有兴趣。陪他走一段"挑个目标 → 写个用例 → 建个测试单 → 抓一只 Bug 看它走完生老病死"的路子——**别编号也别列清单**，但开场顺口把这段路点一下。

## 开场：一句话点路 + 挑靶子

示例开场：

> "测试这块我们大概这样走：先从你们产品里挑一条需求当靶子，围着它写两条用例（正向一个、异常一个），拉个测试单装起来，最后提一只 Bug 陪它走完从 active 到 closed 的全程。随时喊停。
>
> 先看看产品里有哪些需求可以拿来练手——"

列几条候选让用户挑：

```bash
zentao story --product=<产品ID> --pick=id,title,pri --filter='stage:wait,stage:developing' --limit=10
```

如果产品里没需求，顺水推舟："要不我们借 PM 视角先捏一条？"（跳到 [pm.md](pm.md) 的建需求那段）。

## 围着这条需求写用例

不要一上来罗列用例类型。用联想的问法：

> "如果这条需求真上线，你第一个会想试什么？再想一个'要是乱搞会怎样'的场景？"

用户给出一个正向和一个异常场景，就可以各写一条用例，每条创建前把关键字段口语化报一遍：

```bash
zentao testcase create --product=<产品ID> --story=<storyID> --title="..." --pri=<1-4> --type=feature
```

如果用户想看完整字段（步骤/预期），用 `zentao testcase help` 展开，按需求补。

## 顺势拉个测试单

> "有了用例还得有个'测试本子'把它们装起来跑，禅道里叫测试单。"

```bash
zentao testtask create --product=<产品ID> --name="v1 冒烟测试" --begin=... --end=...
```

把刚才的用例关联进来（参见 `zentao testtask help`），然后列一眼：

```bash
zentao testtask --product=<产品ID> --pick=id,name,status
```

## 然后抓一只 Bug 看它走完一生

用带点戏剧感的口气：

> "假设你跑用例的时候发现点不对劲——要不我们提一个 Bug 练练手？"

和用户商量 Bug 的标题、严重度（`severity`）、优先级（`pri`）、重现步骤（`steps`）。严重度和优先级给个建议（比如"看起来能用就是有点歪，那严重 3 优先 3？"），让他点头即可。

```bash
zentao bug create --product=<产品ID> --title="..." --severity=<1-4> --pri=<1-4> --type=codeerror --steps="..."
```

顺手演示状态流转（边执行边用一句话解释它代表开发解决了、你关掉了）：

```bash
zentao bug resolve <id> --resolution=fixed
zentao bug close <id>
```

走完之后**具体点一下**用户刚才串起了什么：

> "你看，这一圈其实把测试最核心的一条链走完了：**需求 → 用例 → 测试单 → Bug → 状态流转**。真实工作里无非是每环都放大一些——写更多用例、加回归、跟踪遗留缺陷。骨架你已经有感觉了。"

## 自然收尾

- 用户如果开始问"开发那边怎么接 Bug"——指一下 dev 视角。
- 用户语气淡下来——顺口回顾："你从一条需求写出了用例，拉了测试单，还提了一个 Bug 并把它送走。"
- 回到 [../SKILL.md](../SKILL.md) 的收尾流程。

## 写操作速查（给 AI 用）

| 动作 | 命令 |
|------|------|
| 挑目标需求 | `zentao story --product=<id> --filter='stage:wait,stage:developing'` |
| 建用例 | `zentao testcase create --product= --story= --title= --pri= --type=feature` |
| 建测试单 | `zentao testtask create --product= --name= --begin= --end=` |
| 提 Bug | `zentao bug create --product= --title= --severity= --pri= --type=codeerror --steps=` |
| 解决 Bug | `zentao bug resolve <id> --resolution=fixed` |
| 关闭 Bug | `zentao bug close <id>` |

> 本视角目前剧情较轻，欢迎结合真实测试节奏继续扩展（例如回归、遗留缺陷分析）。
