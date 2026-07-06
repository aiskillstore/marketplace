# 示例：行驶证识别（vehicle-license-ocr）

适用：行驶证图片，提取车牌号、所有人、车辆类型、使用性质等字段。

---

## 用户输入示例

> 识别这张行驶证：`/Users/me/Desktop/vehicle-license.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "vehicle-license-ocr" --path "/Users/me/Desktop/vehicle-license.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "plateNumber": "京A12345",
    "owner": "张三",
    "vehicleType": "小型轿车",
    "useNature": "非营运",
    "brand": "特斯拉 Model 3",
    "registrationDate": "2022-05-10"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "vehicle-license-ocr" --url "https://example.com/vehicle.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "vehicle-license-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 行驶证正本/副本照片
- 汽车租赁、交通管理

## 不适合此场景

- 驾驶证 → 使用 `driver-license-ocr`
- 身份证 → 使用 `idcard-ocr`
