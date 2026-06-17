# 示例：扫描合同（scan-contract）

适用：合同或协议的图片进行画质优化，让文字更清晰、画面更整洁，便于归档或办公处理。

---

## 用户输入示例

> 帮我把这份合同高清优化一下：`/Users/me/Desktop/contract-photo.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "scan-contract" --path "/Users/me/Desktop/contract-photo.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_b1c2d3.png"
  }
}
```

## 用户可见结果

> 合同已优化：`/tmp/imgs/1728912345_b1c2d3.png`，字迹清晰、背景干净，可直接存档。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "scan-contract" --url "https://example.com/contract.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "scan-contract" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 合同/协议拍照（字迹偏淡、背景不净）
- 需要电子化存档的纸质合同
- 传真件或复印件画质偏低

## 不适合此场景

- 需要将合同转为可编辑 Word → 使用 `yescan-transoffice-universal` 技能
- 需要提取合同中的文字 → 使用 `yescan-ocr-universal` 技能
- 通用文档增强 → `scan-document`
