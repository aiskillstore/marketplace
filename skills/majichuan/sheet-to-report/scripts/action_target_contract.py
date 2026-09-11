"""Keep intervention subjects distinct from suggested execution roles."""
import re


def validate_target(action, snapshot, allowed, require_binding=False):
    target = action['target'].strip()
    if not target or target in {'整体', '相关业务', '相关对象', '待确认'}:
        raise ValueError('行动对象必须具体说明干预范围')
    if re.search(r'(负责人|责任人|主管|经理|总监|执行人|owner|manager|lead)\s*$', target, re.I):
        raise ValueError('行动对象不能仅填写执行负责人；建议协同角色须单列')
    refs = action.get('target_refs')
    if require_binding and not refs:
        raise ValueError('新行动对象必须绑定来源章节中的业务对象证据')
    if refs is not None:
        if not isinstance(refs, list) or not refs:
            raise ValueError('行动对象证据不能为空')
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {'evidence_id', 'row', 'column'} or ref['evidence_id'] not in allowed:
                raise ValueError('行动对象证据越出来源章节')
            record = snapshot['evidence'][ref['evidence_id']]
            if type(ref['row']) is not int or not 0 <= ref['row'] < len(record['rows']) or ref['column'] not in record['columns']:
                raise ValueError('行动对象单元格不存在')
            value = record['rows'][ref['row']].get(ref['column'])
            if not isinstance(value, str) or not value.strip() or value not in target or re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?', value):
                raise ValueError('行动对象须明确包含绑定的业务对象，不能仅引用数值或日期')
    if 'suggested_role' in action and (not isinstance(action['suggested_role'], str) or not action['suggested_role'].strip()):
        raise ValueError('建议协同角色不能为空；无法判断时省略')
