"""Presentation intent is authored separately from frozen calculations."""
import re
from html_analysis import resolve_text


def validate_story(model, story):
    if story is None:
        return None
    required = {'version', 'source_model_sha256', 'themes', 'chart_titles'}
    if not required <= set(story) or set(story)-required-{'visual'} or story['version'] != 'presentation-story/1' or story['source_model_sha256'] != model['sha256']:
        raise ValueError('演示编排来源或字段不匹配')
    if len(story['themes']) != len(model['summary']):
        raise ValueError('演示主线必须与核心结论逐条对应')
    for index, theme in enumerate(story['themes']):
        if set(theme) != {'summary_index', 'title'} or type(theme['summary_index']) is not int or theme['summary_index'] != index:
            raise ValueError('主线编号不得重排或悬空')
        if not isinstance(theme['title'], str) or not 1 <= len(theme['title']) <= 14 or any(c in theme['title'] for c in '\n<>'):
            raise ValueError('主线短名称须为一至十四字符纯文本')
    charts = {c['id']:(chapter,c) for chapter in model['chapters'] for c in chapter['charts']}
    if set(story['chart_titles']) != set(charts):
        raise ValueError('图表页判断标题必须覆盖且仅覆盖已选图表')
    resolved = {}
    for cid, fragments in story['chart_titles'].items():
        chapter, chart = charts[cid]
        title = resolve_text(fragments, model['snapshot'], [chart['evidence_id']])
        if not title.strip() or len(title) > 52 or any(c in title for c in '\n<>'):
            raise ValueError('图表页判断标题超出容量或不是纯文本')
        resolved[cid] = title
    visual = story.get('visual')
    if visual is not None:
        if not isinstance(visual, dict) or visual.get('version') not in {'presentation-visual/1','presentation-visual/2'}:
            raise ValueError('视觉编排字段不匹配')
        allowed = {'version','chart_focus'}
        if visual['version'] == 'presentation-visual/2':
            allowed |= {'overview_focus','action_layouts','chart_annotations'}
        if not {'version','chart_focus'} <= set(visual) or set(visual)-allowed:
            raise ValueError('视觉编排字段不匹配')
        if not isinstance(visual['chart_focus'],dict) or not set(visual['chart_focus']) <= set(charts):
            raise ValueError('视觉重点必须引用已选图表')
        for cid, labels in visual['chart_focus'].items():
            view = model['chart_views'][cid]
            if (not isinstance(labels,list) or not 1 <= len(labels) <= 2 or
                any(not isinstance(label,str) for label in labels) or len(set(labels)) != len(labels) or
                any(label not in view['labels'] or label not in resolved[cid] for label in labels)):
                raise ValueError('视觉重点必须是图中类别且出现在本页判断标题中')
        if visual['version'] == 'presentation-visual/2':
            validate_visual_design(model, visual, resolved)
    return {'themes':story['themes'], 'chart_titles':resolved, 'visual':visual}


def validate_visual_design(model, visual, titles):
    focus = visual.get('overview_focus')
    if focus is not None:
        columns = model['snapshot']['evidence']['overview']['columns']
        if (not isinstance(focus, dict) or set(focus) != {'metric','rationale'} or
            focus['metric'] not in columns or focus['metric'].startswith('_') or
            not isinstance(focus['rationale'], str) or not 10 <= len(focus['rationale']) <= 200):
            raise ValueError('主指标必须引用整体指标并提供宿主选择理由')
    annotations = visual.get('chart_annotations', {})
    if not isinstance(annotations, dict) or not set(annotations) <= set(visual['chart_focus']):
        raise ValueError('图旁短标注必须属于已选重点')
    for cid, notes in annotations.items():
        if not isinstance(notes, dict) or not set(notes) <= set(visual['chart_focus'][cid]):
            raise ValueError('图旁短标注类别不匹配')
        view = model['chart_views'][cid]
        if view['kind'] not in {'column','grouped'} or len(view['labels']) > 4:
            raise ValueError('当前短标注只开放最多四类别的柱形或分组柱形，密集图保留宽幅')
        for note in notes.values():
            if not isinstance(note, str) or not 1 <= len(note) <= 12 or note not in titles[cid]:
                raise ValueError('图旁短标注必须逐字引用当前图表判断标题')
    layouts = visual.get('action_layouts', {})
    actions = {f'action-{i}': a for i, a in enumerate(model['actions'], 1)}
    if not isinstance(layouts, dict) or not set(layouts) <= set(actions):
        raise ValueError('行动构图必须绑定已有行动')
    for owner, spec in layouts.items():
        action = actions[owner]
        if (not isinstance(spec, dict) or set(spec) != {'relation','parts','basis'} or
            spec['relation'] not in {'sequence','parallel'} or not isinstance(spec['parts'], list) or
            not 2 <= len(spec['parts']) <= 4 or not isinstance(spec['basis'], str) or
            not spec['basis'] or spec['basis'] not in action['title']+'\n'+action['steps']):
            raise ValueError('行动构图需要原文关系依据及完整分段')
        # This is a structural guard, not a substitute for the host's semantic review.
        if spec['relation'] == 'sequence' and not re.search(r'先.+再|首先.+然后|before.+after|first.+then', spec['basis'], re.I):
            raise ValueError('顺序构图需要原文明示先后，否则使用并列')
        for part in spec['parts']:
            if (not isinstance(part, dict) or set(part) != {'label','text'} or
                not isinstance(part['text'], str) or not part['text'] or
                not isinstance(part['label'], str) or not 1 <= len(part['label']) <= 14 or
                part['label'] not in part['text']):
                raise ValueError('步骤标签必须来自该段原文')
        if ''.join(p['text'] for p in spec['parts']) != action['steps']:
            raise ValueError('行动分段必须逐字拼回原文，不得丢失、改写或重排')


def visual_role(slide, intent, views):
    """Only represent relationships already present in the source, never rank them."""
    kind = slide['kind']
    relation = {'summary':'equal-judgements', 'overview':'equal-metrics',
                'chart':'evidence-comparison','action':'execution-and-validation'}.get(kind,'reference')
    role = {'version':intent['version'],'relation':relation,
            'block_indices':list(range(len(slide['blocks']))), 'focus_indices':[]}
    if kind == 'chart':
        v = views[slide['chart_id']]
        labels = intent['chart_focus'].get(slide['chart_id'], [])
        role['focus_indices'] = [v['labels'].index(label) for label in labels]
        if intent['version'] == 'presentation-visual/2':
            role['label_notes'] = intent.get('chart_annotations',{}).get(slide['chart_id'],{})
    if kind == 'overview' and intent.get('overview_focus'):
        focus = intent['overview_focus']
        role['focus_indices'] = [i for i,b in enumerate(slide['blocks']) if b['evidence_cell']['column'] == focus['metric']]
        if role['focus_indices']:
            role['relation'] = 'declared-metric-focus'
            role['focus_rationale'] = focus['rationale']
    spec = intent.get('action_layouts',{}).get(slide['owner'])
    if kind == 'action' and spec:
        # A capacity-split continuation stays in its lossless existing layout.
        source = ''.join(p['text'] for p in spec['parts'])
        index = next((i for i,b in enumerate(slide['blocks']) if b['label']=='执行步骤' and b['text']==source),None)
        if index is not None:
            role['action_layout'] = {**spec, 'block_index':index}
    return role


def conclusion_links(model, chapter_ids):
    return [i for i, item in enumerate(model['summary']) if set(chapter_ids).intersection(item['chapter_ids'])]


def page_navigation(model, chapter_ids, purpose, *, themes=None, action_number=None, phase='判断展开'):
    links = conclusion_links(model, chapter_ids)
    if phase in {'开场', '全局背景', '附录'}:
        section = phase
    elif action_number is not None:
        section = f'行动{action_number:02d}'
        if links:
            section += ' · 对应结论' + '、'.join(f'{i+1:02d}' for i in links)
    elif len(links) == 1:
        i = links[0]
        label = themes[i]['title'] if themes else next((c.get('nav_title') for c in model['chapters'] if c['id'] in chapter_ids and c.get('nav_title')), '判断展开')
        section = f'结论{i+1:02d} · {label}'
    elif links:
        section = '结论' + '、'.join(f'{i+1:02d}' for i in links) + ' · 共同依据'
    else:
        section = '补充背景'
    return {'phase':phase, 'conclusion_indices':links, 'section':section, 'purpose':purpose,
            'eyebrow':section+' · '+purpose}


def overview_blocks(model):
    record = model['snapshot']['evidence']['overview']
    if len(record['rows']) != 1 or not record['columns']:
        raise ValueError('整体概况需要单行整体汇总，不能猜测多行分母')
    result = []
    for key, column in record['columns'].items():
        if key.startswith('_'):
            continue
        value = record['rows'][0].get(key)
        if value is not None and (type(value) not in {int,float}):
            raise ValueError('整体指标必须为数值或明确缺失')
        formatted = resolve_text([{'evidence_id':'overview','row':0,'column':key}],model['snapshot'],['overview'])
        result.append({'label':column['label'], 'text':formatted,
                       'evidence_cell':{'evidence_id':'overview','row':0,'column':key}, 'raw_value':value})
    return result
