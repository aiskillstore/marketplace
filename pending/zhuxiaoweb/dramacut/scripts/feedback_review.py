"""Read-only feedback interpretation and conservative, item-scoped reuse evidence.

Does not write quality-review approvals, play media or modify a Jianying draft.
Unknown prose stays unresolved; an explicit action map records human/agent interpretation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ACTIONS = {'retain_candidate', 'restore_baseline', 'apply_named_choice', 'needs_changes',
           'remove_sfx', 'compare_without_sfx', 'pending', 'interpret_notes'}
KINDS = {'picture', 'sfx', 'removed_sfx', 'bgm', 'episode'}
NEGATIVE = ('不应景', '太单薄', '太轻柔', '太奇怪', '太怪', '误以为是消音', '像消音',
            '闪烁', '闪跳', '不合理', '不自然', '声音太小', '听不清', '去掉', '删除', '换掉', '需要修改')
PICTURE_AUDIO_FIELDS = {'volume', 'last_nonzero_volume', 'audio_fade', 'audio_fades',
                        'audio_keyframes', 'audio_adjust', 'audio_muted'}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def save_new(path, value, inputs=()):
    path = Path(path).resolve()
    if path.exists() or path in {Path(p).resolve() for p in inputs}:
        raise ValueError('Use a new output file outside the inputs')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def interpret(row, override=None):
    decision = row.get('decision')
    if decision not in ('pass', 'needs_changes', 'pending'):
        raise ValueError('Unknown review decision: '+str(decision))
    notes = row.get('notes', '')
    if not isinstance(notes, str):
        raise ValueError('Feedback notes must be text')
    compact = re.sub(r'[\s\"“”‘’\'，,。:：]', '', notes)
    selected = row.get('selected_option')
    if selected not in (None, 'baseline', 'candidate'):
        raise ValueError('selected_option must be baseline or candidate')
    baseline = bool(re.fullmatch(r'(?:(?:使用|选择|保留)用户手调基线(?:更好)?|用户手调基线更好|本轮候选不合理使用用户手调基线)', compact))
    candidate = bool(re.fullmatch(r'(?:(?:使用|选择|保留)本轮候选(?:更好)?|本轮候选更好|用户手调基线不合理使用本轮候选)', compact))
    if selected == 'baseline':
        baseline = True
    if selected == 'candidate':
        candidate = True
    basis = 'literal_decision'
    choice = None
    if override:
        action = override.get('action')
        if action not in ACTIONS or not str(override.get('reason', '')).strip():
            raise ValueError('Action override needs a supported action and concrete interpretation reason')
        basis = 'explicit_action_map'
        choice = override.get('choice')
    elif baseline and candidate:
        action, basis = 'interpret_notes', 'conflicting_choices'
    elif baseline:
        action, basis = 'restore_baseline', 'explicit_baseline_choice'
    elif candidate:
        action, basis = 'retain_candidate', 'explicit_candidate_choice'
    elif re.match(r'^使用[：:]', notes.strip()):
        action, basis = 'apply_named_choice', 'explicit_named_choice'
        choice = re.sub(r'^使用[：:]\s*', '', notes.strip())
    elif any(text in notes for text in NEGATIVE):
        action, basis = 'needs_changes', 'negative_notes_override_status'
    elif notes.strip():
        action, basis = 'interpret_notes', 'unrecognized_prose_requires_interpretation'
    else:
        action = 'retain_candidate' if decision == 'pass' else decision
    accepted = (action == 'retain_candidate' and
                (decision == 'pass' or basis == 'explicit_candidate_choice'))
    prior_origin = row.get('decision_origin', '').startswith('prior_') or bool((row.get('inheritance') or {}).get('inherited'))
    if prior_origin and row.get('decision_origin') != 'current_round_user_selection':
        accepted = False
        basis = 'prior_pass_requires_original_binding_check'
    return dict(action=action, choice=choice, interpretation_basis=basis,
                interpretation=override.get('reason') if override else None,
                candidate_accepted=accepted,
                scope='this_exact_item_only', needs_interpretation=action == 'interpret_notes')


def normalize(feedback_path, action_map=None):
    feedback_path = Path(feedback_path).resolve(strict=True)
    data = load(feedback_path)
    overrides = load(action_map).get('actions', {}) if action_map else {}
    rows, seen = [], set()
    for row in data.get('reviews', []):
        key = row.get('key')
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError('Review keys must be unique nonempty strings')
        seen.add(key)
        if row.get('kind') not in KINDS:
            raise ValueError('Unsupported item kind: '+str(row.get('kind')))
        rows.append(dict(key=key, kind=row['kind'], episode=row.get('episode'),
                         event_or_seam_id=row.get('event_or_seam_id'),
                         raw=copy.deepcopy(row), **interpret(row, overrides.get(key))))
    if set(overrides)-seen:
        raise ValueError('Action map includes unknown review keys')
    if not rows:
        raise ValueError('Feedback has no review items')
    bindings = {str(feedback_path): sha(feedback_path)}
    if action_map:
        bindings[str(Path(action_map).resolve())] = sha(action_map)
    return dict(schema_version=1, kind='normalized_item_feedback', bindings=bindings,
                prior_feedback_sha256=data.get('prior_feedback_sha256'), items=rows,
                reviewed_versions=copy.deepcopy(data.get('episodes', [])),
                unresolved_keys=[r['key'] for r in rows if r['needs_interpretation']],
                scope='Interpretation only; no subjective approval or draft mutation is generated')


def verify_dependencies(bindings):
    for raw, digest in bindings.items():
        path = Path(raw)
        if not path.is_file() or sha(path) != digest:
            raise ValueError('Bound evidence changed or missing: '+raw)


def context_graph(doc, start, end, kind, copy_root=None):
    """Hash complete overlapping segments and their referenced local resources."""
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= doc['duration']:
        raise ValueError('Context window must be integer microseconds inside the timeline')
    if kind not in KINDS:
        raise ValueError('Unsupported context kind')
    picture = kind == 'picture'
    mats, groups = {}, {}
    for group, values in doc.get('materials', {}).items():
        for value in values if isinstance(values, list) else []:
            if isinstance(value, dict) and value.get('id'):
                mid = value['id']
                if mid in mats and mats[mid] != value:
                    raise ValueError('Conflicting material IDs: '+mid)
                mats[mid], groups[mid] = value, group
    dependencies, memo, active = {}, {}, set()

    def resolve_file(raw):
        if raw.startswith('##_draftpath_placeholder_'):
            if not copy_root:
                raise ValueError('Draft placeholder requires copy_root')
            raw = re.sub(r'^##_draftpath_placeholder_[^#]+_##', lambda _: str(Path(copy_root).resolve()), raw, count=1)
        path = Path(raw)
        if not path.is_absolute() or not path.is_file():
            raise ValueError('Cannot fingerprint unresolved media/resource path: '+raw)
        path = path.resolve()
        digest = dependencies.setdefault(str(path), sha(path))
        return {'file_sha256': digest}

    def transform(value, key=''):
        if isinstance(value, dict):
            return {k: transform(v, k) for k, v in value.items()}
        if isinstance(value, list):
            if key == 'extra_material_refs' and picture:
                value = [v for v in value if groups.get(v) not in ('audio_fades', 'audio_effects', 'audio_balances')]
            if key == 'extra_material_refs' and any(not isinstance(v, str) or v not in mats for v in value):
                raise ValueError('Unresolved extra material reference')
            return [transform(v) for v in value]
        if isinstance(value, str):
            if value in mats:
                return material(value)
            if value and (key == 'material_id' or key.endswith('_material_id')) and key != 'local_material_id':
                raise ValueError('Unresolved material reference: '+value)
            if value and (key in ('path', 'file_path', 'resource_path') or key.endswith('_path')):
                return resolve_file(value)
        return value

    def material(mid):
        if mid in memo:
            return memo[mid]
        if mid in active:
            raise ValueError('Cyclic material reference: '+mid)
        if groups[mid] == 'drafts':
            raise ValueError('Nested draft resources need explicit complete dependency evidence; review this item again')
        active.add(mid)
        raw = {k: v for k, v in mats[mid].items() if k not in ('id', 'unique_id')}
        value = transform(raw)
        active.remove(mid)
        memo[mid] = value
        return value

    tracks = []
    for track in doc.get('tracks', []):
        if picture and track.get('type') == 'audio':
            continue
        segments = []
        for segment in track.get('segments', []):
            timing = segment.get('target_timerange', {})
            a, b = timing.get('start', 0), timing.get('start', 0)+timing.get('duration', 0)
            if max(a, start) >= min(b, end):
                continue
            raw = copy.deepcopy(segment)
            raw.pop('id', None)
            raw.pop('unique_id', None)
            if picture:
                for field in PICTURE_AUDIO_FIELDS:
                    raw.pop(field, None)
            for field in ('target_timerange', 'source_timerange'):
                if isinstance(raw.get(field), dict):
                    raw[field].setdefault('start', 0)
            segments.append(transform(raw))
        if segments:
            tr = transform({k: v for k, v in track.items() if k not in ('id', 'segments')})
            tr['segments'] = segments
            tracks.append(tr)
    if not tracks:
        raise ValueError('Context window contains no relevant segments')
    globals_ = {k: v for k, v in doc.items() if k not in ('id', 'tracks', 'materials')}
    graph = dict(timeline_id=doc['id'], globals=transform(globals_), start_us=start,
                 end_us=end, kind=kind, tracks=tracks)
    verify_dependencies(dependencies)
    return dict(sha256=canonical(graph), dependencies=dependencies,
                scope='picture_only' if picture else 'audiovisual_context')


def specs(path):
    values = load(path).get('items', [])
    keys = [x.get('key') for x in values]
    if not values or any(not isinstance(k, str) or not k for k in keys) or len(set(keys)) != len(keys):
        raise ValueError('Spec needs unique item keys')
    if any(x.get('kind') not in KINDS for x in values):
        raise ValueError('Spec contains an unsupported item kind')
    return values


def fingerprint(spec):
    path = Path(spec['input']).resolve(strict=True)
    before = sha(path)
    result = context_graph(load(path), spec['start_us'], spec['end_us'], spec['kind'], spec.get('copy_root'))
    if sha(path) != before:
        raise ValueError('Timeline changed during fingerprinting')
    return result


def bind(normalized_path, spec_path):
    normalized = load(normalized_path)
    if normalized.get('kind') != 'normalized_item_feedback':
        raise ValueError('Expected normalized feedback')
    verify_dependencies(normalized['bindings'])
    indexed = {r['key']: r for r in normalized['items']}
    if len(indexed) != len(normalized['items']):
        raise ValueError('Normalized feedback contains duplicate item keys')
    versions = {}
    for row in normalized.get('reviewed_versions', []):
        if not isinstance(row, dict) or 'episode' not in row or str(row['episode']) in versions:
            raise ValueError('Reviewed episode versions must be unique and explicitly identified')
        versions[str(row['episode'])] = row
    records = []
    for spec in specs(spec_path):
        row = indexed.get(spec['key'])
        if not row or spec['kind'] != row['kind']:
            raise ValueError('Spec key/kind differs from feedback')
        version = versions.get(str(row.get('episode')), {})
        item_hash = row['raw'].get('reviewed_input_sha256')
        episode_hash = version.get('edited_sha256')
        if item_hash and episode_hash and item_hash != episode_hash:
            raise ValueError('Item and episode identify conflicting reviewed JSON versions')
        expected = item_hash or episode_hash
        if not expected or sha(spec['input']) != expected:
            raise ValueError('Bind the exact JSON version identified in the original feedback, not a later edit')
        media = spec.get('review_media', [])
        if not media or not isinstance(media, list):
            raise ValueError('Bind the actual media presented for this accepted item')
        reviewed = {str(Path(p).resolve(strict=True)): sha(p) for p in media}
        signature = fingerprint(spec)
        records.append(dict(key=spec['key'], kind=spec['kind'], start_us=spec['start_us'], end_us=spec['end_us'],
                            candidate_accepted=row['candidate_accepted'], signature=signature,
                            reviewed_input_sha256=expected, review_media=reviewed, action=row['action'],
                            media_association='Caller identifies the media actually presented; hashes enforce subsequent immutability'))
    bindings = dict(normalized['bindings'])
    bindings[str(Path(normalized_path).resolve())] = sha(normalized_path)
    bindings[str(Path(spec_path).resolve())] = sha(spec_path)
    return dict(schema_version=1, kind='item_feedback_binding', bindings=bindings, items=records,
                scope='Evidence reuse only; submit through existing review-check with actual review provenance')


def check(binding_path, spec_path):
    old = load(binding_path)
    if old.get('kind') != 'item_feedback_binding':
        raise ValueError('Expected item feedback binding')
    verify_dependencies(old['bindings'])
    if len({r.get('key') for r in old['items']}) != len(old['items']):
        raise ValueError('Binding contains duplicate item keys')
    current = {r['key']: r for r in specs(spec_path)}
    results = []
    for record in old['items']:
        reasons, new = [], current.get(record['key'])
        if not record['candidate_accepted']:
            reasons.append('Prior user did not accept this candidate')
        verify_dependencies(record['review_media'])
        if not new:
            reasons.append('Item missing from current spec')
        elif any(new.get(k) != record[k] for k in ('kind', 'start_us', 'end_us')):
            reasons.append('Item scope/window changed')
        else:
            signature = fingerprint(new)
            if signature['sha256'] != record['signature']['sha256']:
                reasons.append('Playback graph/source/timing/gain/effect configuration changed')
        results.append(dict(key=record['key'], kind=record['kind'], inherited=not reasons, reasons=reasons,
                            approved_scope=record['signature']['scope'],
                            next_review='fold_unchanged_item' if not reasons else 'show_changed_item_comparison',
                            preview_audio_policy='use_current_mix; picture acceptance does not accept prior audio'))
    for key in current.keys()-{r['key'] for r in old['items']}:
        results.append(dict(key=key, inherited=False, reasons=['New unreviewed item'], next_review='show_changed_item_comparison'))
    return dict(schema_version=1, items=results, binding_sha256=sha(binding_path),
                scope='No whole-episode pass is inferred from individual item passes')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    n = sub.add_parser('normalize')
    n.add_argument('--feedback', required=True)
    n.add_argument('--action-map')
    b = sub.add_parser('bind')
    b.add_argument('--normalized', required=True)
    b.add_argument('--spec', required=True)
    c = sub.add_parser('check')
    c.add_argument('--binding', required=True)
    c.add_argument('--spec', required=True)
    for parser in (n, b, c):
        parser.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        if args.command == 'normalize':
            result = normalize(args.feedback, args.action_map)
        elif args.command == 'bind':
            result = bind(args.normalized, args.spec)
        else:
            result = check(args.binding, args.spec)
        save_new(args.output, result)
        print(json.dumps({'output': str(Path(args.output).resolve()), 'item_count': len(result['items']),
                          'scope': result['scope']}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, 'Feedback evidence unavailable: '+str(exc)+'\n')


if __name__ == '__main__':
    main()
