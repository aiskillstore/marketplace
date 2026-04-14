import requests
import json

def search_articles(keyword, start_time=None, end_time=None):
    """
    通过关键词搜索ZAKER文章
    """
    url = 'https://skills.myzaker.com/api/v1/article/search?v=1.0.6'
    
    # 必填参数
    params = {
        'keyword': keyword
    }
    
    # 选填参数
    if start_time:
        params['start_time'] = start_time
    if end_time:
        params['end_time'] = end_time
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 1:
            print(f"搜索成功！找到以下关于 '{keyword}' 的文章：")
            for idx, article in enumerate(result['data'].get('list', []), 1):
                print(f"\n[{idx}] {article.get('title')}")
                print(f"作者: {article.get('author')} | 时间: {article.get('publish_time')}")
                print(f"摘要: {article.get('summary')}")
        else:
            print(f"搜索失败: {result.get('msg')}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    # 测试基本搜索
    search_articles("人工智能")
    
    # 测试带时间范围的搜索
    print("-" * 50)
    search_articles("iPhone 15", start_time="2024-01-01 00:00:00")
