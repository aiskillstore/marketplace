# 图片上传（图生图必需）

本地图片需先上传到图床获取 URL，才能用于图生图。

## 推荐图床

### Litterbox（临时，1小时有效）

```bash
curl -s -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@本地图片路径" https://litterbox.catbox.moe/resources/internals/api.php
```

### Catbox（永久）

```bash
curl -s -F "reqtype=fileupload" -F "fileToUpload=@本地图片路径" https://catbox.moe/user/api.php
```

## 使用方式

1. 上传图片，获取返回的 URL
2. 将 URL 放在 prompt 开头，后面跟描述文字

示例：
```
https://litter.catbox.moe/xxxxx.png 将这张图片进行4K增强，保持原有内容不变
```
