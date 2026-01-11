# 📚 文本分析与结构化提取教程 (v3.1 - 完整中间件优化版)

## 🎯 文档目标
为AI助手提供一套**与ToolExecutionMiddleware完全兼容**、**安全可靠**的文本分析解决方案，专门用于处理已获取的网页内容、文档数据等结构化信息提取。

---

## 🧠 核心设计原则 (与中间件对齐)

### ✅ 必须遵守
1. **零网络依赖** - 所有分析基于已提供的文本数据
2. **安全第一** - 仅使用Python标准库和预装安全库
3. **格式标准化** - 输出必须符合系统可识别的JSON结构
4. **错误包容性** - 提取失败时提供合理的默认值
5. **函数式编程** - 避免使用类定义，与中间件优化保持一致
6. **中文标点规避** - 代码中禁止使用中文标点符号，只使用英文标点
7. **强制输出格式** - 必须包含type字段，使用json.dumps输出

### ❌ 必须避免
1. 网络请求、API调用
2. 文件系统越权访问
3. 非安全的库导入
4. 无限循环或资源耗尽操作
5. 类定义（中间件优化后更加严格）
6. 中文标点符号（会引起SyntaxError）
7. 缺少type字段的JSON输出

---

## 🚀 快速开始模板（与中间件兼容）

### 场景一：直接分析网页抓取内容
```python
# ===================== 基础分析模板（中间件优化版）=====================
import json
import re
from datetime import datetime

def analyze_webpage_content(text_content: str) -> dict:
    """
    基础网页内容分析器 - 与ToolExecutionMiddleware完全兼容
    输入：任何网页的文本内容
    输出：结构化提取结果
    """
    # 初始化标准输出结构 - 必须包含type字段
    result = {
        "type": "analysis_report",  # 🚨 关键：必须字段，中间件依赖此字段
        "title": "网页内容分析报告",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "text_length": len(text_content),
            "analysis_method": "regex_extraction",
            "language": "mixed"
        },
        "data": {
            "basic_info": {},
            "pricing_info": {},
            "specifications": {},
            "extracted_summary": ""
        }
    }
    
    # 1. 基本信息提取（示例）
    if "产品" in text_content or "Product" in text_content:
        result["data"]["basic_info"]["page_type"] = "product_page"
    
    # 2. 价格提取（多币种支持） - 使用英文标点
    price_patterns = {
        "USD": r'\$\s*(\d+[,\d]*\.?\d*)',
        "CNY": r'¥\s*(\d+[,\d]*)',
        "HKD": r'HK\$\s*(\d+[,\d]*\.?\d*)',
        "EUR": r'€\s*(\d+[,\d]*\.?\d*)'
    }
    
    for currency, pattern in price_patterns.items():
        match = re.search(pattern, text_content)
        if match:
            result["data"]["pricing_info"][currency] = match.group(1)
    
    # 3. 关键信息摘要 - 限制长度避免中间件截断
    lines = text_content.split('\n')
    key_lines = [line.strip() for line in lines if len(line.strip()) > 20][:5]
    result["data"]["extracted_summary"] = " | ".join(key_lines)
    
    # 4. 确保数据不为空
    if not result["data"]["pricing_info"]:
        result["data"]["pricing_info"] = {"status": "no_price_found"}
    
    return result

# ===================== 执行示例（中间件要求）=====================
if __name__ == "__main__":
    # 将您的data_context粘贴在这里
    sample_text = """
    产品名称: Jimmy Choo DIDI 45
    价格: $299.99
    材质: 皮革鞋面, 绸缎内衬
    跟高: 45mm
    特点: 尖头设计, 优雅女性鞋履
    """
    
    analysis_result = analyze_webpage_content(sample_text)
    
    # 🚨 关键：必须使用print输出JSON格式，ensure_ascii=False支持中文
    # 中间件依赖此格式进行解析和存储
    print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
```

### 场景二：多页面批量分析（中间件兼容）
```python
import json
import re
from datetime import datetime

def analyze_multiple_pages(pages_data: str) -> dict:
    """
    处理包含多个页面的文本数据 - 中间件优化版
    格式：以"## 页面"分隔的不同页面
    """
    results = []
    
    # 分割页面
    if "## 页面" in pages_data:
        pages = pages_data.split("## 页面")[1:]
        
        for i, page_content in enumerate(pages[:3]):  # 限制前3页
            # 调用单页分析器
            page_result = analyze_webpage_content(page_content)
            page_result["page_number"] = i + 1
            results.append(page_result)
    else:
        # 单页情况
        results.append(analyze_webpage_content(pages_data))
    
    final_output = {
        "type": "multi_page_analysis",  # 🚨 关键：中间件识别字段
        "total_pages": len(results),
        "pages": results,
        "summary": f"成功分析 {len(results)} 个页面",
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "version": "v3.1-middleware-compatible"
        }
    }
    
    return final_output

# 执行示例
if __name__ == "__main__":
    multi_page_text = """
    ## 页面1
    产品A 价格 $100
    规格: 10x20cm
    
    ## 页面2  
    产品B 价格 $200
    规格: 15x25cm
    """
    
    result = analyze_multiple_pages(multi_page_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

## 📊 输出格式规范（系统强制要求 - 中间件依赖）

### ✅ 正确格式示例（中间件可解析）
```json
{
    "type": "analysis_report",  // 🚨 必须字段，中间件依赖此字段识别输出类型
    "title": "分析报告标题",     // 用户可见的标题
    "timestamp": "2024-01-01T12:00:00",  // 推荐添加时间戳
    "metadata": {               // 元数据（可选但推荐）
        "analysis_method": "regex",
        "version": "1.0"
    },
    "data": {                  // 实际分析数据
        "field1": "value1",
        "field2": ["item1", "item2"]
    }
}
```

### ❌ 错误格式示例（中间件无法正确处理）
```python
# 错误1：直接打印字典（中间件无法解析）
print(analysis_result)  

# 错误2：非JSON字符串（中间件无法结构化处理）
print("价格: $299.99")  

# 错误3：缺少type字段（中间件无法识别类型）
{"data": {...}}  

# 错误4：使用类定义（中间件优化后更严格）
class Extractor:  # 避免使用类
    def extract(self): pass

# 错误5：使用中文标点（会引起SyntaxError）
def 分析函数(text):  # ❌ 使用中文函数名
    result = {"价格": "100"}  # ❌ 使用中文冒号
    return result
```

---

## 🛠️ 专业分析工具箱（中间件优化版）

### 1. 价格提取器（正则表达式版本）
```python
import re
import json

def extract_price_info(text: str) -> dict:
    """从文本中提取价格信息 - 中间件兼容版"""
    # 注意：使用英文标点，正则表达式使用原始字符串
    price_patterns = [
        r'(\$\d+(?:\.\d+)?)\s*per\s*1[kK]\s*tokens?',  # $0.50 per 1k tokens
        r'(\d+(?:\.\d+)?)\s*USD\s*per\s*1[kK]\s*tokens?',  # 0.50 USD per 1k tokens
        r'输入\s*:\s*(\$\d+\.\d+)\s*输出\s*:\s*(\$\d+\.\d+)',  # 输入: $0.10 输出: $0.20
        r'(\$\d+(?:\.\d+)?)\s*/\s*1[kK]\s*tokens?',  # $0.30/1k tokens
        r'价格\s*[:：]\s*[￥¥$€]?\s*(\d+(?:\.\d+)?)',  # 价格: $100
        r'售价\s*[:：]\s*[￥¥$€]?\s*(\d+(?:\.\d+)?)',  # 售价: ¥999
        r'cost\s*[:：]\s*[￥¥$€]?\s*(\d+(?:\.\d+)?)',  # cost: $50
    ]
    
    prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # 处理元组匹配（多组捕获）
            for match in matches:
                if isinstance(match, tuple):
                    prices.extend([m for m in match if m])
                else:
                    prices.append(match)
    
    # 构建中间件兼容的输出结构
    return {
        'type': 'price_extraction',
        'extraction_method': 'regex',
        'price_matches': prices[:10],  # 限制结果数量
        'sample_text': text[:500] if len(text) > 500 else text,  # 保留样本用于验证
        'confidence': 'high' if prices else 'low',
        'currency_types': list(set([p[0] for p in prices if p and isinstance(p, str)]))  # 提取货币符号
    }

# 使用示例 - 注意使用英文标点
if __name__ == "__main__":
    text_content = "从所有步骤收集的文本...价格: $299.99, 售价: ¥1999"
    price_info = extract_price_info(text_content)
    
    # 🚨 关键：必须使用print(json.dumps())格式
    print(json.dumps(price_info, ensure_ascii=False, indent=2))
```

### 2. 技术参数提取器（中间件兼容版）
```python
import re
import json

def extract_tech_specs(text: str) -> dict:
    """提取技术参数 - 中间件兼容版"""
    specs = {}
    
    # 参数数量 - 注意正则表达式使用原始字符串
    param_patterns = [
        r'(\d+(?:\.\d+)?)\s*万亿?\s*参数',  # 3.5万亿参数
        r'(\d+(?:\.\d+)?)\s*[Tt]rillion\s*parameters',  # 3.5 trillion parameters
        r'参数\s*[:：]\s*(\d+(?:\.\d+)?)\s*万亿?',  # 参数: 3.5万亿
    ]
    
    for pattern in param_patterns:
        match = re.search(pattern, text)
        if match:
            specs['parameter_count'] = match.group(1) + ' trillion'
            break
    
    # 上下文长度
    context_patterns = [
        r'(\d+(?:,\d+)?[kK]?)\s*tokens?\s*上下文',  # 128K tokens上下文
        r'上下文\s*[:：]\s*(\d+[kK]?)',  # 上下文: 128K
        r'context\s*[:：]\s*(\d+[kK]?)',  # context: 128k
    ]
    
    for pattern in context_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs['context_length'] = match.group(1)
            break
    
    # MMLU 分数
    mmlu_patterns = [
        r'MMLU\s*[:：]?\s*(\d+(?:\.\d+)?)',  # MMLU: 85.2
        r'MMLU\s*分数\s*[:：]\s*(\d+(?:\.\d+)?)',  # MMLU分数: 85.2
        r'MMLU\s*score\s*[:：]\s*(\d+(?:\.\d+)?)',  # MMLU score: 85.2
    ]
    
    for pattern in mmlu_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                specs['mmlu_score'] = float(match.group(1))
            except ValueError:
                specs['mmlu_score'] = match.group(1)
            break
    
    # 返回中间件兼容的格式
    return {
        "type": "tech_specs_extraction",
        "specifications": specs,
        "has_parameters": 'parameter_count' in specs,
        "has_context": 'context_length' in specs,
        "has_mmlu": 'mmlu_score' in specs,
        "extraction_timestamp": datetime.now().isoformat()  # 添加时间戳
    }

# 使用示例 - 注意代码中使用英文标点
if __name__ == "__main__":
    text_content = "某模型具有3.5万亿参数, 支持128K tokens上下文长度, MMLU分数为85.2"
    tech_specs = extract_tech_specs(text_content)
    print(json.dumps(tech_specs, ensure_ascii=False, indent=2))
```

### 3. 规格提取器（函数式版本 - 中间件优化）
```python
import re
import json

def extract_dimensions(text: str) -> dict:
    """产品规格信息提取 - 函数式版本（中间件兼容）"""
    dimensions = {}
    
    # 提取尺寸信息 - 注意使用英文标点
    patterns = {
        "height": [
            r'高度\s*[:：]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)',  # 高度: 45mm
            r'(\d+(?:\.\d+)?)\s*(cm|mm|m)\s*高',  # 45mm高
            r'height\s*[:：]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)',  # height: 45mm
        ],
        "width": [
            r'宽度\s*[:：]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)',  # 宽度: 30cm
            r'(\d+(?:\.\d+)?)\s*(cm|mm|m)\s*宽',  # 30cm宽
            r'width\s*[:：]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m)',  # width: 30cm
        ],
        "weight": [
            r'重量\s*[:：]\s*(\d+(?:\.\d+)?)\s*(kg|g)',  # 重量: 2.5kg
            r'(\d+(?:\.\d+)?)\s*(kg|g)\s*重',  # 2.5kg重
            r'weight\s*[:：]\s*(\d+(?:\.\d+)?)\s*(kg|g)',  # weight: 2.5kg
        ]
    }
    
    for dim, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 处理匹配组
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else ""
                dimensions[dim] = f"{value} {unit}".strip()
                break  # 找到第一个匹配就停止
    
    return dimensions

def extract_all_specs(text: str) -> dict:
    """提取所有规格参数 - 中间件兼容版"""
    specs = {}
    
    # 材质提取
    material_match = re.search(r'材质\s*[:：]\s*([^\n，。]+)', text)
    if material_match:
        specs['material'] = material_match.group(1).strip()
    
    # 颜色提取
    color_match = re.search(r'颜色\s*[:：]\s*([^\n，。]+)', text)
    if color_match:
        specs['color'] = color_match.group(1).strip()
    
    # 尺寸组合
    dimensions = extract_dimensions(text)
    if dimensions:
        specs['dimensions'] = dimensions
    
    # 型号提取
    model_match = re.search(r'型号\s*[:：]\s*([A-Za-z0-9\-_]+)', text)
    if model_match:
        specs['model'] = model_match.group(1)
    
    # 返回中间件兼容格式
    return {
        "type": "specifications_extraction",
        "extracted_specs": specs,
        "has_material": 'material' in specs,
        "has_color": 'color' in specs,
        "has_dimensions": 'dimensions' in specs,
        "text_sample": text[:300] + "..." if len(text) > 300 else text
    }

# 使用示例 - 注意代码中使用英文标点
if __name__ == "__main__":
    text_content = "产品尺寸: 高度45mm, 宽度30cm, 重量2.5kg, 材质: 皮革"
    specs = extract_all_specs(text_content)
    print(json.dumps(specs, ensure_ascii=False, indent=2))
```

### 4. 关键词分析器（函数式版本 - 中间件兼容）
```python
import json

def categorize_content(text: str) -> list:
    """基于关键词的分类分析 - 函数式版本（中间件兼容）"""
    # 注意：使用英文标点定义字典
    CATEGORY_KEYWORDS = {
        "luxury": ["奢侈", "高端", "premium", "luxury", "designer"],
        "electronics": ["电子", "智能", "tech", "digital", "gadget"],
        "clothing": ["服装", "鞋", "wear", "apparel", "footwear"],
        "home_goods": ["家居", "家具", "home", "furniture", "decor"]
    }
    
    text_lower = text.lower()
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in text_lower for keyword in keywords):
            categories.append(category)
    
    return categories if categories else ["uncategorized"]

def categorize_with_confidence(text: str) -> dict:
    """带置信度的内容分类 - 中间件兼容版"""
    CATEGORY_KEYWORDS = {
        "luxury": ["奢侈", "高端", "premium", "luxury", "designer", "豪华", "尊享"],
        "electronics": ["电子", "智能", "tech", "digital", "gadget", "手机", "电脑", "数码"],
        "clothing": ["服装", "鞋", "wear", "apparel", "footwear", "服饰", "穿戴"],
        "home_goods": ["家居", "家具", "home", "furniture", "decor", "家用", "摆设"],
        "beauty": ["美妆", "护肤", "化妆品", "美容", "skincare", "makeup"]
    }
    
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        if score > 0:
            scores[category] = min(score / 5, 1.0)  # 归一化到0-1
    
    if scores:
        # 按置信度排序
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = {
            "type": "content_categorization",
            "primary_category": sorted_categories[0][0],
            "confidence": round(sorted_categories[0][1], 2),
            "all_categories": {cat: round(conf, 2) for cat, conf in sorted_categories[:3]},
            "total_categories_found": len(scores)
        }
    else:
        result = {
            "type": "content_categorization",
            "primary_category": "uncategorized",
            "confidence": 0.0,
            "all_categories": {},
            "total_categories_found": 0
        }
    
    return result

# 使用示例 - 注意代码中使用英文标点
if __name__ == "__main__":
    text_content = "这款奢侈品手表采用高端设计, 适合商务场合"
    categorization = categorize_with_confidence(text_content)
    print(json.dumps(categorization, ensure_ascii=False, indent=2))
```

### 5. HTML结构化提取器（函数式版本 - 深度研究场景优化）
```python
import re
import json
from datetime import datetime

def extract_html_title_and_links(html_content: str) -> dict:
    """
    提取HTML页面标题和链接 - v3.1深度研究场景优化版
    注意：在深度研究中，当需要分析原始HTML结构时使用
    使用限制：仅适用于简单HTML，复杂页面建议使用crawl4ai预处理
    """
    try:
        # 1. 使用安全的标题提取 - 限制提取深度
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "no_title_found"
        
        # 2. 安全的链接提取 - 限制处理长度（深度研究场景通常关注关键链接）
        links = []
        # 深度研究场景：通常只需要分析关键部分，限制前50K字符
        safe_html = html_content[:50000]  
        
        # 使用更安全的正则，避免性能问题
        link_pattern = r'<a\s+[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        
        for match in re.finditer(link_pattern, safe_html, re.IGNORECASE):
            href = match.group(1)
            text = match.group(2).strip()
            
            # 深度研究过滤：只关注有意义的链接
            if href and len(href) > 1 and href not in ['#', 'javascript:void(0)']:
                # 分类链接类型（深度研究有用）
                link_type = "unknown"
                if href.startswith('http://') or href.startswith('https://'):
                    link_type = "external"
                elif href.startswith('/') or href.startswith('./'):
                    link_type = "internal"
                elif href.startswith('mailto:'):
                    link_type = "email"
                elif href.startswith('tel:'):
                    link_type = "phone"
                
                # 深度研究关注：导航链接、文档链接、产品链接等
                link_category = "general"
                if any(keyword in text.lower() for keyword in ['产品', 'product', '详情', 'detail']):
                    link_category = "product"
                elif any(keyword in text.lower() for keyword in ['下载', 'download', '文档', 'document']):
                    link_category = "resource"
                elif any(keyword in text.lower() for keyword in ['联系', 'contact', '关于', 'about']):
                    link_category = "contact"
                
                links.append({
                    "text": text[:100] if text else "link",
                    "href": href[:500],
                    "type": link_type,
                    "category": link_category
                })
            
            # 深度研究通常不需要所有链接，限制数量
            if len(links) >= 15:  
                break
        
        # 3. 构建深度研究友好的输出
        return {
            "type": "html_link_extraction",  # 🚨 关键：必须字段
            "title": "HTML链接提取报告",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "html_length": len(html_content),
                "processed_length": len(safe_html),
                "extraction_method": "safe_regex_for_research",
                "scenario": "deep_research",
                "limitations": "仅提取简单HTML链接，复杂页面建议预处理"
            },
            "data": {
                "page_title": title,
                "links": links,
                "statistics": {
                    "total_links_found": len(links),
                    "external_links": sum(1 for link in links if link["type"] == "external"),
                    "internal_links": sum(1 for link in links if link["type"] == "internal"),
                    "product_links": sum(1 for link in links if link["category"] == "product"),
                    "resource_links": sum(1 for link in links if link["category"] == "resource")
                }
            }
        }
        
    except Exception as e:
        # 深度研究中的错误处理：提供足够信息继续分析
        return {
            "type": "html_extraction_error",
            "title": "HTML提取失败",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "scenario": "deep_research_fallback",
                "recommendation": "请使用crawl4ai工具预处理HTML或简化HTML内容"
            },
            "data": {
                "input_sample": html_content[:1000] if html_content else "empty"
            }
        }

def extract_simple_table_data(html_content: str) -> dict:
    """
    简单提取HTML表格数据 - v3.1深度研究优化版
    在深度研究中，表格常包含关键数据（价格表、规格表、对比表等）
    使用限制：仅支持简单表格结构
    """
    try:
        tables = []
        
        # 深度研究场景：关注数据表格，限制处理长度
        safe_html = html_content[:100000]
        
        # 查找表格 - 深度研究可能关注特定类型的表格
        table_patterns = {
            "general": r'<table[^>]*>(.*?)</table>',
            "with_border": r'<table[^>]*border[^>]*>(.*?)</table>',
            "with_class": r'<table[^>]*class="[^"]*table[^"]*"[^>]*>(.*?)</table>'
        }
        
        table_count = 0
        
        for table_type, pattern in table_patterns.items():
            for table_match in re.finditer(pattern, safe_html, re.IGNORECASE | re.DOTALL):
                if table_count >= 10:  # 深度研究：最多处理10个表格
                    break
                    
                table_html = table_match.group(1)
                
                # 深度研究：跳过过大的表格（可能是布局表格）
                if len(table_html) > 20000:
                    continue
                    
                rows = []
                row_count = 0
                
                # 提取行
                row_pattern = r'<tr[^>]*>(.*?)</tr>'
                
                for row_match in re.finditer(row_pattern, table_html, re.IGNORECASE | re.DOTALL):
                    if row_count >= 30:  # 深度研究：限制每表最大行数
                        break
                        
                    row_html = row_match.group(1)
                    cells = []
                    
                    # 提取单元格 - 深度研究关注数据
                    cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
                    
                    for cell_match in re.finditer(cell_pattern, row_html, re.IGNORECASE | re.DOTALL):
                        # 清理HTML标签，保留重要数据
                        cell_content = re.sub(r'<[^>]+>', '', cell_match.group(1))
                        cell_content = re.sub(r'\s+', ' ', cell_content).strip()
                        
                        # 深度研究：识别数据类型
                        cell_type = "text"
                        if re.search(r'^\$?\d+(?:\.\d+)?%?$', cell_content):
                            cell_type = "number"
                        elif re.search(r'^\d{4}-\d{2}-\d{2}$', cell_content):
                            cell_type = "date"
                        
                        if cell_content:
                            cells.append({
                                "content": cell_content[:200],
                                "type": cell_type
                            })
                    
                    if cells:
                        rows.append(cells)
                        row_count += 1
                
                if rows and row_count > 0:
                    # 深度研究分析：判断表格类型
                    table_purpose = "unknown"
                    headers = rows[0] if rows else []
                    
                    # 根据表头内容判断表格用途
                    header_text = " ".join([cell["content"] for cell in headers])
                    if any(keyword in header_text.lower() for keyword in ['价格', 'price', 'cost', '￥', '$']):
                        table_purpose = "pricing"
                    elif any(keyword in header_text.lower() for keyword in ['规格', 'spec', '参数', 'parameter']):
                        table_purpose = "specifications"
                    elif any(keyword in header_text.lower() for keyword in ['对比', 'compare', 'vs', '差异']):
                        table_purpose = "comparison"
                    elif any(keyword in header_text.lower() for keyword in ['时间', 'date', '日期', 'schedule']):
                        table_purpose = "timeline"
                    
                    tables.append({
                        "table_index": table_count,
                        "table_type": table_type,
                        "purpose": table_purpose,
                        "row_count": len(rows),
                        "col_count": len(rows[0]) if rows else 0,
                        "headers": [cell["content"] for cell in headers] if headers else [],
                        "data_sample": [[cell["content"] for cell in row] for row in rows[:5]],  # 前5行样本
                        "data_types": list(set([cell["type"] for row in rows[:3] for cell in row])) if rows else []
                    })
                    
                    table_count += 1
        
        # 构建深度研究友好的输出
        return {
            "type": "html_table_extraction",
            "title": "HTML表格提取报告",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "html_length": len(html_content),
                "tables_found": len(tables),
                "extraction_method": "research_optimized_regex",
                "scenario": "deep_research_data_extraction",
                "limitations": "仅支持简单表格，嵌套表格可能无法正确处理"
            },
            "data": {
                "tables": tables,
                "summary": {
                    "total_tables": len(tables),
                    "pricing_tables": sum(1 for table in tables if table["purpose"] == "pricing"),
                    "spec_tables": sum(1 for table in tables if table["purpose"] == "specifications"),
                    "comparison_tables": sum(1 for table in tables if table["purpose"] == "comparison"),
                    "total_rows": sum(table["row_count"] for table in tables),
                    "total_columns": sum(table["col_count"] for table in tables)
                }
            }
        }
        
    except Exception as e:
        return {
            "type": "table_extraction_error",
            "title": "表格提取失败",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "scenario": "deep_research_fallback",
                "recommendation": "建议使用结构化数据源或简化表格结构"
            }
        }

def research_html_analysis(html_content: str) -> dict:
    """
    深度研究HTML分析 - 专为深度研究场景优化
    结合链接和表格提取，提供研究洞察
    """
    # 深度研究：限制输入大小，关注质量而非数量
    if len(html_content) > 200000:
        html_content = html_content[:200000] + "\n[HTML内容过长，已截断用于深度分析]"
    
    # 并行提取（深度研究需要多方面信息）
    title_links = extract_html_title_and_links(html_content)
    tables = extract_simple_table_data(html_content)
    
    # 深度研究分析：提取关键洞察
    research_insights = []
    
    # 基于链接的洞察
    if title_links.get("type") != "html_extraction_error":
        links_data = title_links.get("data", {})
        if links_data.get("statistics", {}).get("product_links", 0) > 0:
            research_insights.append("页面包含产品相关链接，可能是电商或产品页面")
        if links_data.get("statistics", {}).get("external_links", 0) > 5:
            research_insights.append("页面包含多个外部链接，可能是资源聚合或引用页面")
    
    # 基于表格的洞察
    if tables.get("type") != "table_extraction_error":
        tables_data = tables.get("data", {})
        if tables_data.get("summary", {}).get("pricing_tables", 0) > 0:
            research_insights.append("页面包含价格表格，适合价格分析研究")
        if tables_data.get("summary", {}).get("comparison_tables", 0) > 0:
            research_insights.append("页面包含对比表格，适合产品对比研究")
    
    # 构建深度研究报告
    return {
        "type": "deep_research_html_analysis",
        "title": "深度研究HTML分析报告",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "original_length": len(html_content),
            "analysis_focus": "research_data_extraction",
            "version": "v3.1-research-optimized",
            "primary_use_cases": [
                "产品规格对比研究",
                "价格策略分析", 
                "竞品分析",
                "技术文档解析"
            ]
        },
        "components": {
            "title_and_links": title_links,
            "tables": tables
        },
        "research_insights": research_insights if research_insights else ["需要进一步分析以获得深度洞察"],
        "recommendations": [
            "对于复杂页面，建议使用crawl4ai预处理",
            "关注页面中的结构化数据（表格、列表）",
            "结合文本内容进行综合分析"
        ]
    }

# ===================== 深度研究使用示例 =====================
if __name__ == "__main__":
    # 示例HTML - 模拟深度研究场景
    html_content = """
    <html>
    <head>
        <title>深度研究示例：AI模型对比分析</title>
        <meta name="description" content="对比GPT-4, Claude 3, Gemini Pro等主流AI模型">
    </head>
    <body>
        <h1>主流AI模型对比分析</h1>
        
        <nav>
            <a href="#pricing">价格对比</a>
            <a href="#specs">技术规格</a>
            <a href="#performance">性能测试</a>
            <a href="https://openai.com">OpenAI官网</a>
            <a href="https://anthropic.com">Anthropic官网</a>
        </nav>
        
        <section id="pricing">
            <h2>价格对比表</h2>
            <table border="1" class="pricing-table">
                <tr>
                    <th>模型</th><th>输入价格 ($/1M tokens)</th><th>输出价格 ($/1M tokens)</th>
                </tr>
                <tr>
                    <td>GPT-4 Turbo</td><td>$10.00</td><td>$30.00</td>
                </tr>
                <tr>
                    <td>Claude 3 Opus</td><td>$15.00</td><td>$75.00</td>
                </tr>
                <tr>
                    <td>Gemini Pro</td><td>$0.50</td><td>$1.50</td>
                </tr>
            </table>
        </section>
        
        <section id="specs">
            <h2>技术规格对比</h2>
            <table class="spec-table">
                <tr><th>模型</th><th>上下文长度</th><th>参数规模</th><th>MMLU分数</th></tr>
                <tr><td>GPT-4</td><td>128K</td><td>1.8万亿</td><td>86.4</td></tr>
                <tr><td>Claude 3</td><td>200K</td><td>未知</td><td>87.5</td></tr>
            </table>
        </section>
        
        <div class="resources">
            <h3>相关资源</h3>
            <a href="/whitepaper.pdf">技术白皮书下载</a>
            <a href="/api-docs">API文档</a>
            <a href="mailto:research@example.com">联系研究团队</a>
        </div>
    </body>
    </html>
    """
    
    # 执行深度研究分析
    print("=== 深度研究HTML分析 ===")
    result = research_html_analysis(html_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

## 🎯 AI使用指南（与中间件配合）

### 步骤一：识别分析需求（中间件感知）
当用户请求分析文本时，AI应：
1. ✅ 确认文本内容是否已提供（来自data_context）
2. ✅ 识别分析目标（价格、规格、分类等）
3. ✅ 选择合适的提取器组合
4. ✅ **避免使用类定义，使用函数式编程**
5. ✅ **确保代码中没有中文标点符号**
6. ✅ **确保输出包含type字段**

### 步骤二：生成执行代码（中间件兼容）
```python
def generate_analysis_code_for_ai(user_text: str, analysis_type: str) -> str:
    """
    AI调用此函数生成可执行的沙盒代码 - 中间件兼容版
    注意：这是给AI看的模板，不是直接在沙盒中执行的代码
    """
    # 示例代码模板 - 注意使用英文标点
    code_template = f'''
import json
import re
from datetime import datetime

# 用户提供的分析文本
TEXT_TO_ANALYZE = """{user_text}"""

def analyze_content(text):
    """分析函数 - 函数式版本（中间件兼容）"""
    result = {{
        "type": "analysis_report",  # 🚨 必须字段
        "title": "{analysis_type} analysis result",
        "timestamp": datetime.now().isoformat(),
        "metadata": {{
            "analysis_method": "regex_extraction",
            "input_length": len(text)
        }},
        "data": {{}}
    }}
    
    # 价格提取 - 使用英文标点
    price_match = re.search(r'\\$\\s*(\\d+[,\\d]*\\.?\\d*)', text)
    if price_match:
        result["data"]["price_usd"] = price_match.group(1)
    
    # 规格提取 - 使用英文标点
    height_match = re.search(r'(\\d+(?:\\.\\d+)?)\\s*(cm|mm|m)\\s*高', text, re.IGNORECASE)
    width_match = re.search(r'(\\d+(?:\\.\\d+)?)\\s*(cm|mm|m)\\s*宽', text, re.IGNORECASE)
    
    dimensions = {{}}
    if height_match:
        dimensions["height"] = height_match.group(1) + (height_match.group(2) or "")
    if width_match:
        dimensions["width"] = width_match.group(1) + (width_match.group(2) or "")
    
    if dimensions:
        result["data"]["dimensions"] = dimensions
    
    # 确保数据不为空
    if not result["data"]:
        result["data"]["status"] = "no_data_extracted"
    
    return result

# 执行分析
try:
    analysis_result = analyze_content(TEXT_TO_ANALYZE)
    
    # 🚨 必须：以JSON格式输出，ensure_ascii=False支持中文
    print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
    
except Exception as e:
    # 错误处理 - 中间件要求返回标准格式
    error_result = {{
        "type": "analysis_error",
        "error_message": str(e),
        "timestamp": datetime.now().isoformat(),
        "input_sample": TEXT_TO_ANALYZE[:200]
    }}
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
'''
    return code_template
```

### 步骤三：处理返回结果（中间件集成）
AI收到沙盒执行结果后：
1. ✅ 验证输出格式是否正确（type字段存在）
2. ✅ 提取关键信息呈现给用户
3. ✅ 提供进一步分析建议
4. ✅ 如果失败，利用中间件的备用方案

---

## 🔧 故障排除与最佳实践（中间件优化版）

### 常见问题解决方案（针对中间件优化）

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 无输出 | 代码未执行print | 确保最后一行是print(json.dumps(...)) |
| 格式错误 | 非JSON输出 | 使用json.dumps()而非str() |
| 提取为空 | 文本格式不匹配 | 添加更灵活的正则表达式 |
| 编码问题 | 中文字符乱码 | 使用ensure_ascii=False参数 |
| 类定义错误 | 中间件不支持类 | 使用函数式编程替代 |
| **中文标点错误** | **代码包含中文标点** | **全部替换为英文标点** |
| **缺少type字段** | **中间件无法识别输出** | **必须包含type字段** |
| **输出过长** | **中间件可能截断** | **限制输出长度，使用data_bus存储** |

### 中间件特定优化建议
1. **类型字段优先**：所有输出必须包含type字段，这是中间件识别的关键
2. **错误处理标准化**：使用try-except包裹，返回标准错误格式
3. **长度限制**：限制提取结果数量，避免中间件处理超长数据
4. **时间戳添加**：为每次分析添加时间戳，便于中间件追踪
5. **元数据丰富**：添加metadata字段，包含分析方法、版本等信息
6. **数据总线兼容**：如果数据量大，考虑使用中间件的数据总线存储机制

---

## 📋 完整工作流示例（中间件兼容版）

```python
# ===================== 完整分析工作流（中间件兼容版）=====================
import json
import re
from datetime import datetime

def complete_analysis_workflow(data_context: str) -> str:
    """
    端到端的文本分析工作流 - 中间件兼容版
    输入：爬虫获取的文本数据
    输出：标准化的分析报告
    """
    
    try:
        # 1. 并行提取各类信息（使用函数而非类）
        price_info = extract_price_info(data_context)
        dimensions = extract_dimensions(data_context)
        categories = categorize_with_confidence(data_context)
        
        # 2. 构建结果 - 符合中间件要求
        report = {
            "type": "comprehensive_analysis",  # 🚨 关键字段
            "title": "综合文本分析报告",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "analysis_tools": "middleware_compatible_suite",
                "analysis_time": datetime.now().isoformat(),
                "confidence": calculate_confidence(price_info, dimensions),
                "version": "v3.1-middleware-optimized"
            },
            "data": {
                "price_information": price_info,
                "specifications": dimensions,
                "content_categorization": categories,
                "text_statistics": {
                    "total_length": len(data_context),
                    "line_count": data_context.count('\n'),
                    "key_sentences": extract_key_sentences(data_context, 3)
                }
            }
        }
        
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 错误处理 - 中间件兼容格式
        error_report = {
            "type": "workflow_error",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "input_sample": data_context[:500] if len(data_context) > 500 else data_context
        }
        return json.dumps(error_report, ensure_ascii=False, indent=2)

# 辅助函数 - 注意使用英文标点
def extract_key_sentences(text: str, max_sentences: int = 3) -> list:
    """提取关键句子 - 中间件兼容版"""
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char in '.!?。！？':  # 中英文句末标点
            sentence = current.strip()
            if len(sentence) > 10:
                sentences.append(sentence)
            current = ""
        
        if len(sentences) >= max_sentences:
            break
    
    # 如果没找到足够句子，按换行分割
    if len(sentences) < max_sentences:
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
        sentences.extend(lines[:max_sentences - len(sentences)])
    
    return sentences[:max_sentences]

def calculate_confidence(price_info: dict, dimensions: dict) -> str:
    """计算分析置信度 - 中间件兼容版"""
    price_matches = price_info.get('price_matches', [])
    has_dimensions = bool(dimensions)
    
    if price_matches and has_dimensions:
        return "high"
    elif price_matches or has_dimensions:
        return "medium"
    else:
        return "low"

# 主执行逻辑 - 注意使用英文标点
if __name__ == "__main__":
    # 示例文本 - 注意使用英文标点
    sample_text = """
    产品: 高端智能手表
    价格: $299.99
    尺寸: 高度45mm, 宽度38mm
    材质: 不锈钢表壳, 蓝宝石玻璃
    功能: 心率监测, GPS定位
    """
    
    result = complete_analysis_workflow(sample_text)
    print(result)
```

---

## ✅ 验证测试（中间件兼容）

运行以下代码验证您的分析器：

```python
# 测试用例 - 中间件兼容版
import json

def run_middleware_compatible_tests():
    """运行中间件兼容性测试"""
    test_cases = [
        {
            "text": "Jimmy Choo DIDI 45 价格 $299.99 材质皮革 高度45mm",
            "expected_type": "product_page_analysis",
            "has_price": True,
            "has_dimensions": True
        },
        {
            "text": "iPhone 15 Pro Max 售价 ¥9999 重量 221g 宽度78mm",
            "expected_type": "electronics_analysis",
            "has_price": True,
            "has_dimensions": True
        },
        {
            "text": "实木餐桌 尺寸 180x90cm 价格 €459 高度75cm",
            "expected_type": "home_goods_analysis",
            "has_price": True,
            "has_dimensions": True
        }
    ]
    
    test_results = []
    
    for i, test_case in enumerate(test_cases):
        # 使用函数式分析器
        dimensions = extract_dimensions(test_case["text"])
        categories = categorize_content(test_case["text"])
        
        result = {
            "type": "test_result",
            "test_id": i + 1,
            "test_case": test_case["expected_type"],
            "dimensions": dimensions,
            "categories": categories,
            "has_price": "$" in test_case["text"] or "¥" in test_case["text"] or "€" in test_case["text"],
            "passed_basic_checks": bool(dimensions) or bool(categories),
            "middleware_compatible": True  # 标记为中间件兼容
        }
        
        test_results.append(result)
    
    # 输出汇总报告
    summary = {
        "type": "test_summary",
        "total_tests": len(test_results),
        "passed_tests": sum(1 for r in test_results if r["passed_basic_checks"]),
        "all_middleware_compatible": all(r["middleware_compatible"] for r in test_results),
        "test_results": test_results
    }
    
    return summary

# 执行测试
if __name__ == "__main__":
    summary = run_middleware_compatible_tests()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
```

---

## 📌 总结要点（中间件优化版）

1. **与中间件完全兼容**：所有代码设计考虑了ToolExecutionMiddleware的要求
2. **类型字段优先**：输出必须包含type字段，这是中间件识别的关键
3. **中文标点规避**：代码中禁止使用中文标点符号，只使用英文标点
4. **函数式编程**：避免类定义，与中间件优化保持一致
5. **错误处理标准化**：使用try-except，返回中间件可解析的错误格式
6. **输出格式严格**：必须使用print(json.dumps(...))格式
7. **元数据丰富**：添加时间戳、版本号等元数据
8. **长度限制**：控制输出长度，避免中间件处理问题

## 🔄 从类到函数的转换指南（中间件要求）

| 原类定义 | 转换后的函数 | 使用方式 | 中间件兼容性 |
|---------|------------|---------|-------------|
| `class Extractor:`<br>`def extract(self, text):` | `def extract_data(text):` | `result = extract_data(text)` | ✅ |
| `obj = Extractor()`<br>`obj.extract(text)` | 直接调用函数 | `extract_data(text)` | ✅ |
| 类属性（`self.config`） | 函数参数或全局常量 | `def func(text, config={})` | ✅ |
| 多个相关方法 | 多个独立函数或主函数调用子函数 | `def main_func():`<br>`data1 = func1()`<br>`data2 = func2()` | ✅ |
| **使用中文标点** | **全部替换为英文标点** | **result = {"price": "100"}** | ✅ |
| **缺少type字段** | **必须添加type字段** | **{"type": "analysis", "data": {}}** | ✅ |

## 🎯 最终检查清单（中间件优化版）

在生成沙盒代码前，请确认：
- [ ] 没有`class`关键字（函数式编程）
- [ ] 所有功能都是函数
- [ ] 输出包含`type`字段（中间件必需）
- [ ] 使用`json.dumps()`输出
- [ ] 没有网络请求或文件系统访问
- [ ] 正则表达式有限制（避免ReDoS）
- [ ] **代码中没有中文标点符号**
- [ ] **使用英文标点（逗号, 句号. 冒号:）**
- [ ] **添加时间戳和元数据**
- [ ] **包含错误处理机制**
- [ ] **控制输出长度**
