import requests
import json

def get_category_articles(app_id):
    """
    根据分类ID获取指定分类文章
    常用分类ID: 
    13(科技), 9(娱乐), 8(体育), 7(汽车), 4(财经)
    """
    url = 'https://skills.myzaker.com/api/v1/article/category?v=1.0.6'
    
    # 必填参数
    params = {
        'app_id': app_id
    }
    
    category_map = {
        13: '科技', 9: '娱乐', 8: '体育', 7: '汽车', 4: '财经',
        1: '国内新闻', 2: '国际新闻', 3: '军事', 5: '互联网'
    }
    category_name = category_map.get(app_id, f'分类{app_id}')
        
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 1:
            print(f"获取【{category_name}】分类文章成功！最新内容如下：")
            for idx, article in enumerate(result['data'].get('list', []), 1):
                print(f"\n[{idx}] {article.get('title')}")
                print(f"作者: {article.get('author')} | 时间: {article.get('publish_time')}")
                print(f"摘要: {article.get('summary')}")
        else:
            print(f"获取失败: {result.get('msg')}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    # 获取科技类文章 (app_id=13)
    get_category_articles(13)
