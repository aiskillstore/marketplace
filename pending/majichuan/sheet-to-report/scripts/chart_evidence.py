"""Deterministic chart evidence; no narrative, user formulas, or rendering geometry."""
from __future__ import annotations

import copy
import math

import pandas as pd

from canonical_json import canonical_sha256


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def derived(source, rows, columns, label, definition, semantics, operands):
    scope = copy.deepcopy(source['scope'])
    scope['denominator'] += '；' + definition
    return {'rows': rows, 'columns': columns, 'label': label, 'scope': scope,
            'kind': 'chart_derived', 'chart_semantics': semantics,
            'derivation': {'definition': definition, 'operands': operands,
                           'source_record_sha256': canonical_sha256(source)}}


def histogram_record(source, key, entity_key):
    """One observation per grouped entity, equal-width Sturges bins, capped at 12."""
    raw = [row.get(key) for row in source['rows']]
    values = [float(value) for value in raw if number(value)]
    if not values:
        return None
    if len({str(row[entity_key]) for row in source['rows']}) != len(raw):
        raise ValueError('分布必须先明确唯一实体粒度')
    low, high = min(values), max(values)
    bins = 1 if low == high else min(12, math.ceil(math.log2(len(values)) + 1))
    # Constant samples retain their exact value in a unit-width display interval.
    edges = ([low - .5, high + .5] if low == high else
             [low + (high-low)*i/bins for i in range(bins)] + [high])
    counts = [0] * bins
    for value in values:
        index = 0 if low == high else min(bins-1, int((value-low)/(high-low)*bins))
        counts[index] += 1
    rows = [{'bin': f'区间{i+1}', 'lower': edges[i], 'upper': edges[i+1], 'count': count}
            for i, count in enumerate(counts)]
    unit = source['columns'][key]['unit']
    definition = ('按每个已聚合对象的指标值等宽分箱；箱数为Sturges规则向上取整并最多十二箱；'
                  '左闭右开，最后箱包含右端点；缺失不当零；常数样本用该值上下各半单位的单箱')
    columns = {'bin': {'label': '区间', 'unit': ''},
               'lower': {'label': source['columns'][key]['label']+'下界', 'unit': unit},
               'upper': {'label': '上界', 'unit': unit},
               'count': {'label': '对象数', 'unit': '个', 'additive': True}}
    semantics = {'histogram': {'lower_key': 'lower', 'upper_key': 'upper',
                              'count_key': 'count', 'sample_count': len(values)},
                 'missing_count': len(raw)-len(values), 'entity_key': entity_key}
    return derived(source, rows, columns, source['columns'][key]['label']+'的对象分布',
                   definition, semantics, {'value_key': key, 'entity_key': entity_key})


def bridge_record(source, category, value, start=0.0, end=None,
                  start_label='变动起点', end_label='变动净额'):
    values = [row[value] for row in source['rows']]
    if not all(number(v) for v in values) or not number(start):
        raise ValueError('瀑布分解只接受有限已算数值')
    finish = start + math.fsum(values)
    if end is not None and (not number(end) or not math.isclose(finish, end, rel_tol=1e-10, abs_tol=1e-6)):
        raise ValueError('瀑布分解与起终点不对账')
    rows = [{'stage': start_label, 'amount': start, 'role': 'start', 'base': 0.0, 'end': start}]
    running = start
    for row in source['rows']:
        following = running + row[value]
        rows.append({'stage': str(row[category]), 'amount': row[value], 'role': 'delta',
                     'base': running, 'end': following})
        running = following
    rows.append({'stage': end_label, 'amount': finish, 'role': 'end', 'base': 0.0, 'end': finish})
    unit = source['columns'][value]['unit']
    columns = {'stage': {'label': '组成', 'unit': ''},
               'amount': {'label': '金额', 'unit': unit, 'additive': True},
               'role': {'label': '组成角色', 'unit': ''},
               'base': {'label': '累计起点', 'unit': unit},
               'end': {'label': '累计终点', 'unit': unit}}
    return derived(source, rows, columns, source['label']+'：起终点对账',
                   '起点加全部已计算分量等于终点；累计坐标由确定性计算生成，非因果解释',
                   {'waterfall': {'role_key': 'role', 'base_key': 'base', 'end_key': 'end'}},
                   {'category': category, 'value': value, 'start': start, 'end': finish})


def _time(record, key, period_type):
    values = sorted({str(row[key]) for row in record['rows']})
    if not values:
        return
    frequency = 'month' if period_type == 'monthly' else 'week'
    if frequency == 'month':
        expected = [str(value) for value in pd.period_range(values[0], values[-1], freq='M')]
    else:
        expected = [value.date().isoformat() for value in pd.date_range(values[0], values[-1], freq='7D')]
    record.setdefault('chart_semantics', {})['time'] = {
        'frequency': frequency, 'expected_values': expected}


def enrich(snapshot):
    """Declared presentation evidence, based only on already computed snapshot records.

    Safe to call again after a followup. No input reads and no dynamic query budget reset.
    """
    evidence = snapshot['evidence']
    metrics = {item['name']: item for item in snapshot['metrics']}
    pending = {}
    for ref, record in list(evidence.items()):
        if record['kind'] == 'chart_derived':
            continue
        # Isolate shared column dictionaries before assigning semantic annotations.
        record['columns'] = copy.deepcopy(record['columns'])
        columns = record['columns']
        for key, meta in columns.items():
            if key in metrics:
                meta['additive'] = metrics[key]['aggregation'] in {'sum', 'sum_product'}
            base = key if key in metrics else next((name for name in metrics if key in {name+'_baseline', name+'_current', name+'_change'}), None)
            if base and metrics[base]['aggregation'] == 'ratio':
                metric = metrics[base]
                meta['denominator'] = ('按已确认范围汇总的'+metric['denominator']+
                    ('；前期分母' if key.endswith('_baseline') else '；本期分母' if key.endswith('_current') else
                     '；两期各自分母，比例差不可相加' if key.endswith('_change') else ''))
        if ref == 'trend':
            _time(record, '__period', snapshot['request']['period_type'])
        if ref == 'commerce_trend':
            _time(record, 'period', snapshot['request']['period_type'])
        if ref in {'overview', 'commerce_trend', 'geography_totals', 'product_totals', 'product_view', 'pending_items'}:
            for key in ('net', 'units'):
                if key in columns:
                    columns[key]['additive'] = True
        if ref.startswith('dimension_') or ref in {'geography_totals', 'product_totals', 'customer_frequency'}:
            record.setdefault('chart_semantics', {})['partition'] = {'mutually_exclusive': True, 'complete': True}
            for key, meta in list(columns.items()):
                if meta.get('additive') is not True:
                    continue
                values = [row.get(key) for row in record['rows']]
                if not all(number(value) for value in values):
                    continue
                total = math.fsum(values)
                if not total:
                    continue
                share_key = key+'__share'
                for row in record['rows']:
                    row[share_key] = row[key]/total*100
                columns[share_key] = {'label': meta['label']+'占比', 'unit': '%',
                                      'denominator': record['label']+'中的'+meta['label']+'合计'}
                record.setdefault('chart_derivations', {})[share_key] = {
                    'formula': 'value / sum(exclusive grouped values) * 100', 'value_key': key, 'denominator': total}
        if ref == 'customer_frequency':
            for key in ('people', 'net'):
                columns[key]['additive'] = True
            total = sum(row['people'] for row in record['rows'])
            for row in record['rows']:
                row['people_share'] = row['people'] / total * 100 if total else None
            denominator = '全部可识别客户人数'
            columns['people_share'] = {'label': '客户人数占比', 'unit': '%', 'denominator': denominator}
            columns['share']['denominator'] = '可识别客户净销售合计'
            record['derivation'] = {'definition': '人数占比=互斥组客户数/全部可识别客户数×100',
                                    'operands': {'total_people': total}}
        if ref == 'customer_concentration':
            count = evidence['customer_summary']['rows'][0]['identified_people']
            if count:
                rows = [{'customer_pct': 0.0, 'share': 0.0}]
                # Small populations can collapse adjacent requested percentiles to one entity count.
                rows += [{'customer_pct': n/count*100, 'share': next(r['share'] for r in record['rows'] if r['people']==n)}
                         for n in sorted({r['people'] for r in record['rows']})]
                columns_new = {'customer_pct': {'label': '累计客户比例', 'unit': '%'},
                               'share': {'label': '累计净销售贡献', 'unit': '%'}}
                if all(number(row['share']) for row in rows):
                    pending['customer_curve'] = derived(record, rows, columns_new,
                        '客户累计贡献曲线', '横轴为实际累计客户数/全部可识别客户数；客户按净消费降序，累计组不可相加',
                        {'cumulative': {'x_key': 'customer_pct', 'y_key': 'share', 'total': 100, 'order': 'descending'}},
                        {'total_customers': count})
        if ref.startswith('dimension_'):
            # JSON persistence sorts column keys; derived share columns are not entities.
            category = next((key for key in snapshot['request'].get('dimensions', []) if key in columns), None)
            if category:
                for key in metrics:
                    if key not in columns:
                        continue
                    histogram = histogram_record(record, key, category)
                    if histogram:
                        pending['hist_'+ref+'_'+canonical_sha256(key)[:8]] = histogram
        if ref.startswith('followup_'):
            dimension = next((key for key in columns if key != '__period' and key not in metrics), None)
            if dimension and '__period' in columns:
                categories = sorted({row[dimension] for row in record['rows']})
                periods = sorted({row['__period'] for row in record['rows']})
                # Keep complete series; excessive categories are an explicit capability boundary,
                # never an invitation to silently drop small categories.
                if 1 <= len(categories) <= 6:
                    indexed = {(row['__period'], row[dimension]): row for row in record['rows']}
                    for key, meta in list(columns.items()):
                        if meta.get('additive') is not True:
                            continue
                        keys = {value: 'segment_'+str(i) for i, value in enumerate(categories)}
                        pivot_rows = [{'period': period, **{keys[value]: indexed.get((period, value), {}).get(key, 0)
                                       for value in categories}} for period in periods]
                        pivot_columns = {'period': {'label': '周期', 'unit': ''},
                            **{keys[value]: {'label': str(value), 'unit': meta['unit'], 'additive': True}
                               for value in categories}}
                        part = derived(record, pivot_rows, pivot_columns, record['label']+'：'+meta['label']+'构成',
                            '按已确认类别转为互斥系列，各期保留全部类别；缺少某类交易的可加总值为零，缺少整期不补零',
                            {'series_partition': {'mutually_exclusive': True, 'complete': True}},
                            {'metric': key, 'dimension': dimension, 'categories': categories})
                        _time(part, 'period', snapshot['request']['period_type'])
                        pending['series_'+ref+'_'+canonical_sha256(key)[:8]] = part
        if ref == 'period_components' or ref.startswith('components_'):
            columns['amount']['additive'] = True
            if ref == 'period_components' and len(evidence.get('commerce_trend', {}).get('rows', [])) >= 2:
                before, after = evidence['commerce_trend']['rows'][-2:]
                pending['bridge_'+ref] = bridge_record(record, 'component', 'amount', before['net'], after['net'],
                                                      before['period'], after['period'])
            else:
                pending['bridge_'+ref] = bridge_record(record, 'component', 'amount')
        if ref.startswith('change_'):
            for key, meta in columns.items():
                if not key.endswith('_change') or meta.get('additive') is not True:
                    continue
                rows = record['rows']
                if not rows:
                    continue
                leader = max((r for r in rows if r[key] > 0), key=lambda r: r[key], default=max(rows, key=lambda r: abs(r[key])))
                parts = copy.deepcopy(record)
                parts['rows'] = [{'object': leader['object'], 'amount': leader[key]},
                                 {'object': '其余对象合计', 'amount': math.fsum(r[key] for r in rows if r is not leader)}]
                parts['columns'] = {'object': {'label': '对象', 'unit': ''}, 'amount': copy.deepcopy(meta)}
                bridge = bridge_record(parts, 'object', 'amount')
                bridge['derivation'].update(source_record_sha256=canonical_sha256(record),
                    definition='最大正向对象与全部其余对象合计的净变动；无正值时取绝对值最大对象；尾部未遗漏',
                    source_count=len(rows), source_value_key=key)
                pending['bridge_'+ref+'_'+canonical_sha256(key)[:8]] = bridge
    if 'customer_summary' in evidence:
        record = evidence['overview']
        total = record['rows'][0]['net']
        known = evidence['customer_summary']['rows'][0]['identified_net']
        if total:
            columns = {'part': {'label': '身份覆盖', 'unit': ''},
                       'net': {'label': '净销售', 'unit': record['columns']['net']['unit'], 'additive': True},
                       'share': {'label': '占全体净销售', 'unit': '%', 'denominator': '完整分析期全体净销售'}}
            rows = [{'part': label, 'net': amount, 'share': amount/total*100}
                    for label, amount in [('可识别客户', known), ('缺少客户标识', total-known)]]
            pending['identity_coverage'] = derived(record, rows, columns, '销售的客户身份覆盖',
                '可识别与缺失客户标识两部分金额占全体净销售；缺失身份不等于收入损失',
                {'partition': {'mutually_exclusive': True, 'complete': True}},
                {'total': total, 'identified': known,
                 'identified_record_sha256': canonical_sha256(evidence['customer_summary'])})
    evidence.update(pending)
    snapshot['initial_scan'].setdefault('declared_chart_derivations',
        ['grouped_entity_histograms', 'frequency_people_share', 'numeric_cumulative_curve',
         'identity_amount_coverage', 'existing_component_bridges'])
    snapshot['capabilities']['chart_spec_version'] = 'chart-spec/1'
