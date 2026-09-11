"""Completeness of an explicit temporal question, separate from insight depth."""


def requested_coverage_gaps(question, evidence_index, metric_contracts=(), *, period_type='monthly', week_start='monday'):
    declared = question.get('comparison_scope')
    if declared not in ('latest_complete_period_vs_prior_period', 'latest_complete_vs_previous_and_year_over_year'):
        return []
    dimensions = question.get('dimensions', [])
    if not dimensions:
        return []
    records = [evidence_index[ref] for ref in question.get('evidence_ids', []) if ref in evidence_index]
    aliases = {str(c.get('metric_id')): c['name'] for c in metric_contracts}
    required = [aliases.get(name, name) for name in question.get('required_metrics', []) if name != 'any_primary_metric']
    if not required:
        required = sorted({r['metric'] for r in records if r.get('metric')})
    gaps = []
    for metric in required:
        series = next((r for r in records if r.get('kind') == 'metric_trend' and r.get('metric') == metric), None)
        labels = sorted(series.get('periods', [])) if series else []
        if len(labels) < 2:
            gaps.append(f'{metric}:comparison_periods')
            continue
        current, previous = labels[-1], labels[-2]
        baselines = [previous]
        if declared == 'latest_complete_vs_previous_and_year_over_year':
            from analysis_engine import _year_over_year_label
            baselines.append(_year_over_year_label(current, period_type, week_start))
        for dimension in dimensions:
            for baseline in baselines:
                if not any(r.get('kind') == 'dimension_yoy' and r.get('metric') == metric
                           and r.get('dimension') == dimension and r.get('latest_period') == current
                           and r.get('comparison_period') == baseline for r in records):
                    gaps.append(f'{metric}/{dimension}:{baseline}->{current}')
            if not any(r.get('kind') == 'dimension_contribution' and r.get('metric') == metric
                       and r.get('dimension') == dimension and r.get('periods') == [current] for r in records):
                gaps.append(f'{metric}/{dimension}:latest_composition')
    return gaps
