import requests
import json

def get_hot_articles():
    """
    获取ZAKER热榜文章
    """
    url = 'https://skills.myzaker.com/api/v1/article/hot?v=1.0.3'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 1:
            print("获取热榜成功！最新热门文章如下：")
            for idx, article in enumerate(result['data'].get('list', []), 1):
                print(f"\n[{idx}] {article.get('title')}")
                print(f"作者: {article.get('author')} | 时间: {article.get('publish_time')}")
                print(f"摘要: {article.get('summary')}")
        else:
            print(f"获取失败: {result.get('msg')}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    get_hot_articles()
