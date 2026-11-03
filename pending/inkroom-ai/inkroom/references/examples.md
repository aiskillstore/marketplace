# 命令示例

所有相对路径都从技能目录解析。

## 读取工具

```bash
node scripts/inkroom.mjs tools --output inkroom-output
```

## 费用预览

创建 `preview.json`：

```json
{
  "action": "preview",
  "prompt": "暖色调的咖啡海报",
  "count": 1
}
```

再执行：

```bash
node scripts/inkroom.mjs call --tool generate_image --arguments preview.json --output inkroom-output
```

后续执行必须使用预览响应返回的原 `requestId` 或 `batchId`，不得重新构造付费请求。

## 自动续取已有任务

```bash
node scripts/inkroom.mjs resume --response inkroom-output/RESPONSE.response --output inkroom-output
```

默认最多 32 轮，命令只执行原 `nextAction` 指定的 `wait_images`。中断或达到上限后，将返回的检查点作为输入：

```bash
node scripts/inkroom.mjs resume --response inkroom-output/SESSION.resume.json --output inkroom-output --max-polls 32
```

使用同一输出目录；脚本核验之前保存的文件，不重新扣费生成。查看 `originalsSaved/requestedImages/allOriginalsSaved` 和每张图的身份；完整交付还需宿主解码核验。

## 恢复已有响应

```bash
node scripts/inkroom.mjs recover --response inkroom-output/RESPONSE.response --output inkroom-output
```

`recover` 只读取已有文件并保存其中的图片，不发送生成请求。
