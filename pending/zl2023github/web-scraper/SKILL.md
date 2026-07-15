---
name: web-scraper
description: 爬虫/数据采集工程师 Agent — 覆盖网页数据采集、API抓取、动态内容渲染、反爬对抗、数据清洗存储、分布式爬虫架构、App抓包逆向等全领域数据采集工作。能动手搭建完整爬虫系统，不只是出方案。
category: software-engineering
tags: [scrapy, selenium, playwright, mitmproxy, anti-crawling, data-collection, distributed-crawler]
---

# 爬虫/数据采集工程师 Agent

## 适用场景

当用户需要：
- 从网站/API/App采集结构化或非结构化数据
- 搭建可维护的爬虫系统（单机或分布式）
- 解决反爬问题（IP封禁、验证码、参数加密、字体反爬等）
- 抓取动态渲染页面（SPA/JS渲染/WebSocket）
- 逆向App请求协议（Protobuf/加密参数）
- 数据清洗、去重、存储到数据库/文件
- 爬虫监控与运维

## 工作流程

### 阶段一：需求分析与可行性评估

1. **明确目标**：需要采集什么数据？字段列表？数据量级？更新频率？
2. **来源分析**：
   - 网页 → 分析URL结构、分页方式、数据是否在HTML中
   - API → 抓包分析请求/响应格式、认证方式、参数加密
   - App → 确定抓包方案（mitmproxy/Charles）、协议类型（HTTP/WebSocket/gRPC）
3. **可行性评估**：
   - 是否有robots.txt限制
   - 反爬强度（验证码、频率限制、WAF、指纹检测）
   - 法律合规性（数据使用边界、个人信息保护）
4. **方案选择**：
   - 简单静态页面 → requests + BeautifulSoup/lxml
   - 动态渲染页面 → Playwright/Selenium/DrissionPage
   - 大规模采集 → Scrapy + 分布式方案
   - App数据 → mitmproxy + 逆向分析

### 阶段二：技术方案设计

根据目标选择技术栈：

| 场景 | 推荐方案 |
|------|----------|
| 简单静态页面（少量） | requests + BeautifulSoup + lxml |
| 简单静态页面（大量） | Scrapy + parsel |
| 动态渲染页面 | Playwright / DrissionPage |
| 大规模分布式 | Scrapy-Redis + Celery + Kafka |
| App抓包 | mitmproxy + Frida + jadx |
| 高性能异步 | aiohttp + BeautifulSoup + uvloop |
| 反爬对抗 | curl_cffi + 代理池 + 浏览器指纹伪装 |

### 阶段二：环境搭建

```bash
# 基础环境
pip install requests beautifulsoup4 lxml parsel httpx

# 爬虫框架
pip install scrapy scrapy-redis scrapy-splash

# 浏览器自动化
pip install playwright selenium
playwright install chromium

# 异步
pip install aiohttp aiofiles

# 数据存储
pip install pymongo redis pymysql psycopg2-binary

# 反爬工具
pip install curl_cffi fake-useragent

# App抓包与逆向
pip install mitmproxy
# Frida: pip install frida-tools (需配合手机端frida-server)
```

### 阶段三：实施步骤

#### 3.1 静态页面采集

```python
import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    'Accept': 'text/html,application/xhtml+xml,...',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 基础请求
resp = requests.get(url, headers=headers, timeout=10)
resp.raise_for_status()
resp.encoding = resp.apparent_encoding  # 自动检测编码

# 解析
soup = BeautifulSoup(resp.text, 'lxml')
# 或使用 parsel (Scrapy核心解析器)
from parsel import Selector
sel = Selector(text=resp.text)
```

#### 3.2 动态页面采集 (Playwright)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 ...',
        viewport={'width': 1920, 'height': 1080},
        locale='zh-CN'
    )
    page = context.new_page()
    page.goto(url, wait_until='networkidle')
    
    # 等待元素出现
    page.wait_for_selector('.content-item', timeout=10000)
    
    # 滚动加载
    for _ in range(5):
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(2000)
    
    # 提取数据
    items = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.item')).map(el => ({
            title: el.querySelector('.title')?.innerText,
            url: el.querySelector('a')?.href
        }))
    }''')
    
    browser.close()
```

#### 3.3 使用 Scrapy 框架

```bash
# 创建项目
scrapy startproject myproject
cd myproject
scrapy genspider example example.com
```

```python
# spiders/example.py
import scrapy
from scrapy.http import HtmlResponse

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['https://example.com/page/1']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            'myproject.pipelines.DuplicatesPipeline': 100,
            'myproject.pipelines.DatabasePipeline': 300,
        }
    }
    
    def parse(self, response: HtmlResponse):
        # 提取数据
        for item in response.css('.item'):
            yield {
                'title': item.css('.title::text').get(),
                'url': item.css('a::attr(href)').get(),
                'price': item.css('.price::text').re_first(r'[\d.]+'),
            }
        
        # 翻页
        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page))
```

#### 3.4 动态页面 (Playwright 完整示例)

```python
from playwright.sync_api import sync_playwright
import json

def scrape_dynamic_page(url: str) -> list:
    """采集动态渲染页面，支持滚动加载和等待条件"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            # 注入反检测脚本
            extra_http_headers={'Accept-Language': 'zh-CN,zh;q=0.9'}
        )
        
        # 注入反自动化检测
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        """)
        
        page = context.new_page()
        page.goto(url, wait_until='networkidle')
        
        # 等待数据加载
        page.wait_for_selector('.data-item', timeout=15000)
        
        # 滚动加载
        for _ in range(3):
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)
        
        # 提取数据
        data = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.item')).map(el => ({
                title: el.querySelector('.title')?.innerText?.trim(),
                price: el.querySelector('.price')?.innerText?.trim(),
                link: el.querySelector('a')?.href
            }))
        }''')
        
        browser.close()
        return data
```

#### 3.3 API 抓取

```python
import requests
import time
import hashlib
import json

def fetch_api_data(base_url: str, params: dict, api_key: str = None):
    """通用API数据采集，支持分页和认证"""
    headers = {
        'User-Agent': 'Mozilla/5.0 ...',
        'Accept': 'application/json',
    }
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    all_data = []
    page = 1
    while True:
        params['page'] = page
        resp = requests.get(base_url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        # 提取数据
        items = data.get('data', data.get('items', data.get('results', [])))
        if not items:
            break
        all_data.extend(items)
        
        # 分页判断
        total = data.get('total', data.get('count', 0))
        if page * len(items) >= total:
            break
        page += 1
        time.sleep(0.5)
    
    return all_data
```

#### 3.5 反爬对抗策略

| 反爬手段 | 应对方案 |
|----------|----------|
| IP频率限制 | 代理池轮换 + 请求间隔随机化 |
| User-Agent检测 | fake-useragent / 真实UA池 |
| Cookie验证 | 模拟登录 + Session维持 + Cookie持久化 |
| 字体反爬 | 下载字体文件 → fontTools解析映射关系 |
| CSS偏移 | 分析CSS样式还原真实文本顺序 |
| 图片验证码 | ddddocr / PaddleOCR / 打码平台 |
| 滑块验证 | Playwright模拟轨迹 / 第三方打码 |
| WebDriver检测 | Playwright stealth / undetected-chromedriver |
| 参数签名 | JS逆向 → Python重写签名算法 |
| WAF/Cloudflare | curl_cffi / cloudscraper / flaresolverr |
| 字体反爬 | fontTools解析TTF/WOFF映射表 |

#### 3.6 数据清洗与存储

```python
import pandas as pd
from pymongo import MongoClient
import json

def clean_and_store(raw_data: list, collection_name: str):
    """数据清洗与入库"""
    df = pd.DataFrame(raw_data)
    
    # 去重
    df = df.drop_duplicates(subset=['id', 'url'])
    
    # 清洗
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['title'] = df['title'].str.strip()
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # 过滤无效数据
    df = df.dropna(subset=['title'])
    
    # 入库
    client = MongoClient('mongodb://localhost:27017')
    db = client['scraped_data']
    collection = db[collection_name]
    
    records = df.to_dict('records')
    for record in records:
        collection.update_one(
            {'_id': record.get('id', record.get('url'))},
            {'$set': record},
            upsert=True
        )
    
    return len(records)
```

### 阶段四：反爬对抗实战

#### 4.1 IP代理池

```python
import random
import requests
from typing import List

class ProxyPool:
    """简易代理池"""
    def __init__(self):
        self.proxies: List[dict] = []
        self._load_proxies()
    
    def _load_proxies(self):
        """从代理源加载（示例：免费代理源）"""
        sources = [
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/proxies.json',
            # 也可从数据库/文件加载
        ]
        for source in sources:
            try:
                resp = requests.get(source, timeout=5)
                data = resp.json()
                for p in data:
                    self.proxies.append({
                        'http': f'http://{p["ip"]}:{p["port"]}',
                        'https': f'http://{p["ip"]}:{p["port"]}',
                    })
            except Exception:
                continue
    
    def get_random(self) -> dict:
        return random.choice(self.proxies) if self.proxies else {}
    
    def test_proxy(self, proxy: dict) -> bool:
        """测试代理可用性"""
        try:
            resp = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=5)
            return resp.status_code == 200
        except:
            return False
```

#### 4.2 浏览器指纹伪装 (Playwright)

```python
# 反检测初始化脚本
STEALTH_SCRIPT = """
// 隐藏WebDriver
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

// 伪装Chrome
window.chrome = { runtime: {} };

// 覆盖权限查询
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

// 覆盖plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// 覆盖languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en']
});
"""
```

#### 4.3 验证码处理

```python
# ddddocr - 轻量级OCR验证码
import ddddocr

ocr = ddddocr.DdddOcr()
with open('captcha.png', 'rb') as f:
    result = ocr.classification(f.read())
print(f'验证码识别结果: {result}')

# 滑块验证码 - 使用Playwright模拟轨迹
import random

def slide_verify(page, slider_selector: str, gap_selector: str):
    """模拟人类滑块验证"""
    slider = page.locator(slider_selector)
    gap = page.locator(gap_selector)
    
    slider_box = slider.bounding_box()
    gap_box = gap.bounding_box()
    
    start_x = slider_box['x'] + slider_box['width'] / 2
    start_y = slider_box['y'] + slider_box['height'] / 2
    target_x = gap_box['x'] + gap_box['width'] / 2
    
    distance = target_x - start_x
    
    # 模拟人类轨迹：先快后慢 + 抖动
    tracks = []
    current = 0
    mid = distance * 0.7
    while current < distance:
        if current < mid:
            move = random.randint(3, 8)
        else:
            move = random.randint(1, 3)
        current += move
        tracks.append(current)
    
    page.mouse.move(start_x, start_y)
    page.mouse.down()
    for x in tracks:
        page.mouse.move(start_x + x, start_y + random.randint(-2, 2))
        page.wait_for_timeout(random.randint(10, 30))
    page.mouse.up()
```

### 阶段五：数据清洗与存储

```python
import pandas as pd
from pymongo import MongoClient, UpdateOne
import json

def clean_scraped_data(raw_data: list) -> pd.DataFrame:
    """通用数据清洗流程"""
    df = pd.DataFrame(raw_data)
    
    # 去重
    if 'url' in df.columns:
        df = df.drop_duplicates(subset=['url'])
    if 'id' in df.columns:
        df = df.drop_duplicates(subset=['id'])
    
    # 文本清洗
    text_cols = [c for c in df.columns if df[c].dtype == 'object']
    for col in text_cols:
        df[col] = df[col].str.strip().str.replace(r'\s+', ' ', regex=True)
    
    # 数值清洗
    for col in ['price', 'amount', 'count', 'score']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 日期标准化
    for col in ['date', 'created_at', 'updated_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df
```

### 阶段六：分布式爬虫架构

```python
# Scrapy-Redis 配置
# settings.py
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = 'redis://localhost:6379'
SCHEDULER_PERSIST = True  # 爬虫停止后保留请求队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
```

### 阶段七：App抓包与逆向

```python
# mitmproxy 脚本示例 - 拦截App请求
# mitmproxy_script.py
from mitmproxy import http
import json

def request(flow: http.HTTPFlow):
    """拦截并记录请求"""
    url = flow.request.pretty_url
    if 'api.target.com' in url:
        print(f"[REQ] {url}")
        print(f"  Headers: {dict(flow.request.headers)}")
        if flow.request.content:
            print(f"  Body: {flow.request.content[:500]}")

def response(flow: http.HTTPFlow):
    """拦截并解析响应"""
    url = flow.request.pretty_url
    if 'api.target.com' in url:
        print(f"[RES] {url}")
        if 'application/json' in flow.response.headers.get('content-type', ''):
            data = json.loads(flow.response.text)
            # 保存到文件
            with open(f'data/{int(time.time())}.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
```

### 阶段八：常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 403 Forbidden | 请求被WAF/Cloudflare拦截 | 使用 curl_cffi / cloudscraper / 真实浏览器指纹 |
| 429 Too Many Requests | 请求频率过高 | 增加间隔、使用代理池、分布式 |
| 空数据/结构变化 | 网站改版 | 检查页面结构、更新选择器、添加结构变化告警 |
| 中文乱码 | 编码识别错误 | resp.encoding = resp.apparent_encoding / chardet检测 |
| 内存溢出 | 数据量过大 | 使用迭代器、分页写入、限制并发数 |
| 连接超时 | 网络/代理问题 | 设置重试机制、超时时间、备用代理 |
| 验证码弹出 | 触发风控 | 降低频率、更换IP、使用打码服务 |

### 阶段九：法律与合规

1. **robots.txt**：遵守网站的爬取规则声明
2. **频率控制**：不要对目标服务器造成压力（建议间隔 ≥ 1秒）
3. **数据使用**：不采集个人隐私信息、不用于竞争性商业用途
4. **版权注意**：注意数据的版权归属和使用许可
5. **反爬对抗边界**：不进行破坏性操作（DDoS、漏洞利用）

---

## 模板文件

### 1. Scrapy 项目模板

```python
# scrapy_spider_template.py
"""
Scrapy爬虫模板 - 使用方式:
1. scrapy startproject myproject
2. 将本模板放入 spiders/ 目录
3. 修改 settings.py 配置中间件和管道
"""
import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urljoin
import json

class BaseSpider(scrapy.Spider):
    """基础爬虫模板，继承后重写 parse_item 即可"""
    name = 'base'
    allowed_domains = []
    start_urls = []
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 8,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],
        'DOWNLOAD_TIMEOUT': 15,
        'ROBOTSTXT_OBEY': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    }
    
    def parse(self, response):
        """主解析方法 - 子类重写"""
        raise NotImplementedError
    
    def parse_item(self, response):
        """解析单个详情页 - 子类重写"""
        raise NotImplementedError
    
    def closed(self, reason):
        """爬虫关闭时的清理工作"""
        self.logger.info(f"Spider closed: {reason}")
```

### 阶段七：App抓包与逆向

#### 7.1 mitmproxy 拦截脚本

```python
# mitmproxy_addon.py
# 运行: mitmproxy -s mitmproxy_addon.py
from mitmproxy import http
import json
import time
import os

# 配置目标域名
TARGET_DOMAINS = ['api.target.com', 'data.target.com']
OUTPUT_DIR = 'captured_data'

def request(flow: http.HTTPFlow):
    """拦截请求"""
    for domain in TARGET_DOMAINS:
        if domain in flow.request.pretty_host:
            print(f"[REQ] {flow.request.method} {flow.request.pretty_url}")
            if flow.request.headers.get('Content-Type', '').startswith('application/json'):
                try:
                    body = json.loads(flow.request.content)
                    print(f"  Body: {json.dumps(body, ensure_ascii=False, indent=2)[:500]}")
                except:
                    pass

def response(flow: http.HTTPFlow):
    """拦截响应"""
    for domain in TARGET_DOMAINS:
        if domain in flow.request.pretty_host:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            fname = f"{OUTPUT_DIR}/{int(time.time())}_{flow.request.path.replace('/', '_')}.json"
            with open(fname, 'w') as f:
                f.write(flow.response.text)
            print(f"[SAVED] {fname}")
```

### 阶段八：数据质量保障

```python
def validate_scraped_data(df: pd.DataFrame, rules: dict) -> dict:
    """
    数据质量校验
    rules: {
        'title': {'required': True, 'min_length': 1, 'max_length': 200},
        'price': {'required': True, 'type': 'numeric', 'min': 0},
        'url': {'required': True, 'pattern': r'^https?://'},
    }
    """
    report = {'total': len(df), 'passed': 0, 'failed': 0, 'errors': []}
    
    for idx, row in df.iterrows():
        row_errors = []
        for field, rule in rules.items():
            val = row.get(field)
            if rule.get('required') and (pd.isna(val) or val == ''):
                row_errors.append(f"{field}: 必填字段为空")
            if rule.get('type') == 'numeric' and val:
                try:
                    float(val)
                except (ValueError, TypeError):
                    row_errors.append(f"{field}: 非数值类型")
            if rule.get('pattern') and val:
                import re
                if not re.match(rule['pattern'], str(val)):
                    row_errors.append(f"{field}: 格式不匹配")
        
        if row_errors:
            report['failed'] += 1
            report['errors'].append({'row': idx, 'errors': row_errors})
        else:
            report['passed'] += 1
    
    return report
```

### 阶段十：监控与运维

```python
# 爬虫健康检查脚本
import requests
import time
from datetime import datetime

def health_check(spider_name: str, expected_count: int, timeout: int = 300):
    """监控爬虫运行状态"""
    start = time.time()
    while time.time() - start < timeout:
        # 检查数据库记录数
        count = get_db_count(spider_name)
        if count >= expected_count:
            return {'status': 'success', 'count': count, 'time': time.time() - start}
        
        # 检查爬虫进程
        import psutil
        spider_running = any('scrapy' in p.name() for p in psutil.process_iter())
        if not spider_running:
            return {'status': 'crashed', 'count': count}
        
        time.sleep(10)
    
    return {'status': 'timeout', 'count': count}
```

### 阶段十：法律与合规检查清单

- [ ] 检查 robots.txt 是否允许采集
- [ ] 确认数据是否包含个人隐私信息（姓名、电话、地址、身份证等）
- [ ] 确认数据使用目的（研究/商业/个人）
- [ ] 设置合理的请求间隔，不对目标服务器造成压力
- [ ] 不进行密码破解、漏洞利用等破坏性操作
- [ ] 不将采集的数据用于直接竞争或非法用途
- [ ] 遵守目标网站的服务条款
- [ ] 注意跨境数据传输的法律要求

---

## 常见陷阱与注意事项

1. **不要硬编码选择器**：网站结构会变，使用相对稳定的属性（data-*、id）或配置化选择器
2. **永远处理异常**：网络超时、解析失败、结构变化都要有fallback
3. **日志是命根子**：记录每个请求的URL、状态码、耗时、数据量
4. **增量采集**：记录上次采集位置，避免全量重复
5. **数据版本化**：保存原始响应（HTML/JSON）以便后续重新解析
6. **代理池维护**：定期检测代理可用性，剔除失效代理
7. **频率控制**：不要用固定间隔，使用随机间隔 ±30%
8. **编码问题**：始终指定编码，优先使用 apparent_encoding
9. **错误重试**：网络错误重试3次，指数退避
10. **本地缓存**：已下载的页面不要重复请求

## 验证方法

1. **单页测试**：先用 requests/curl 测试单个URL能否正常获取数据
2. **解析验证**：提取的数据与页面实际内容逐字段对比
3. **批量验证**：采集100条样本，人工抽查准确率
4. **压力测试**：逐步增加并发数，观察目标服务器响应
5. **稳定性测试**：连续运行1小时，检查是否有中断或异常
6. **数据完整性**：检查是否有缺失字段、重复记录、格式异常
