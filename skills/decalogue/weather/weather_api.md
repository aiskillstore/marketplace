# 天气 API 使用说明

## 当前实现

当前 Weather Skill 使用模拟数据。要集成真实天气 API，可以参考以下步骤：

## 推荐的天气 API

1. **OpenWeatherMap**
   - 免费层：每分钟 60 次请求
   - 需要 API Key
   - 文档：https://openweathermap.org/api

2. **WeatherAPI**
   - 免费层：每月 1M 次请求
   - 需要 API Key
   - 文档：https://www.weatherapi.com/

## 集成步骤

1. 获取 API Key
2. 在 `weather.py` 中实现 API 调用
3. 添加错误处理和缓存机制
4. 更新 `SKILL.md` 说明文档

## 注意事项

- API 调用需要网络连接
- 注意 API 调用频率限制
- 建议添加缓存机制减少 API 调用
- 处理 API 失败的情况
