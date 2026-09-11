"""Small structural guard for authored summary headings; semantics need host review."""
import re


def validate_headline(item, *, required=False):
    if 'headline' not in item:
        if required:
            raise ValueError('核心结论缺少简短判断标题 headline')
        return
    headline = item['headline']
    if not isinstance(headline, str) or not headline.strip() or len(headline) > 40:
        raise ValueError('摘要判断标题须为一至四十字符，不能为空')
    if headline != headline.strip() or re.search(r'[\r\n<>*#]', headline):
        raise ValueError('摘要标题使用单行纯文本，不含格式标记')
    if headline in {'增长分析', '客户分析', '增长情况', '核心结论', '经营情况', '数据分析', '总结', '判断'}:
        raise ValueError('摘要标题须表达具体判断，不能只写分类标签')
    if headline.rstrip('。；：:') == item['text'].strip().rstrip('。；：:'):
        raise ValueError('摘要标题不能重复整条正文')


def validate_summary(model):
    required = bool(model.get('summary_revision') or model['snapshot'].get('capabilities', {}).get('summary_headline_version'))
    for item in model['summary']:
        validate_headline(item, required=required)
