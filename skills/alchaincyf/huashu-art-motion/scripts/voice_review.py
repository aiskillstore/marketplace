"""读取安装目录外的模型检查记录；不联网、不更换默认模型。"""
import json
from datetime import datetime, timezone
from pathlib import Path


def review_status(provider, model, config_file=None, now=None):
    if config_file is None:
        from capabilities import config_path
        config_file = config_path()
    path = Path(config_file).expanduser().resolve().parent / 'voice-model-review.json'
    result = {'provider': provider, 'selected_model': model,
              'last_checked_at': None, 'needs_check': True, 'record': str(path)}
    try:
        record = json.loads(path.read_text()).get('providers', {}).get(provider, {})
        selection = record.get('selection', {})
        result['selected_model'] = model or selection.get('model')
        result['user_selection'] = selection
        checked = record.get('checked_at')
        stamp = datetime.fromisoformat(checked)
        if stamp.tzinfo is None:
            raise ValueError('检查时间需要时区')
        age = ((now or datetime.now(timezone.utc)) - stamp).total_seconds()
        result.update(last_checked_at=checked, needs_check=not 0 <= age < 7 * 86400,
                      candidates=record.get('models', []), findings=record.get('findings', ''))
    except (OSError, ValueError, TypeError, AttributeError):
        result['record_status'] = 'missing_or_invalid'
    return result


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider', choices=['volcengine', 'qwen'], default='volcengine')
    p.add_argument('--model')
    p.add_argument('--config')
    a = p.parse_args()
    from capabilities import effective
    model = a.model
    if not model and a.provider == 'volcengine':
        model = effective(a.config)[0]['provider_options']['volcengine']['model']
    print(json.dumps(review_status(a.provider, model, a.config), ensure_ascii=False, indent=2))
