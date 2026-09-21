"""Keep chart axis identifiers and references compatible with strict OOXML readers."""
import re

CHART_NS = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
AXIS_TAGS = {f'{{{CHART_NS}}}{name}' for name in ('catAx', 'valAx', 'dateAx', 'serAx')}
REFERENCE_TAGS = {f'{{{CHART_NS}}}{name}' for name in ('axId', 'crossAx')}


def axis_id_errors(chart):
    errors = []
    nodes = [node for node in chart.iter() if node.tag in REFERENCE_TAGS]
    for node in nodes:
        value = node.get('val', '')
        if not re.fullmatch(r'\d+', value) or int(value) > 0xFFFFFFFF:
            errors.append(f'invalid unsigned chart axis identifier: {value}')
    definitions = [child.get('val') for node in chart.iter() if node.tag in AXIS_TAGS
                   for child in node if child.tag == f'{{{CHART_NS}}}axId']
    if len(definitions) != len(set(definitions)):
        errors.append('duplicate chart axis definition')
    defined = set(definitions)
    for node in nodes:
        if node.get('val') not in defined:
            errors.append(f'unresolved chart axis reference: {node.get("val")}')
    return errors


def normalize_chart_axis_ids(chart):
    """Map signed 32-bit template IDs to unsigned equivalents, preserving every link.

    Valid unsigned IDs are unchanged. Fail rather than merge conflicting axes or
    repair dangling references. Series, values and chart geometry are untouched.
    """
    nodes = [node for node in chart.iter() if node.tag in REFERENCE_TAGS]
    mapping = {}
    for node in nodes:
        raw = node.get('val', '')
        if not re.fullmatch(r'-?\d+', raw):
            raise ValueError(f'Invalid chart axis identifier: {raw}')
        value = int(raw)
        if not -(2**31) <= value <= 0xFFFFFFFF:
            raise ValueError(f'Chart axis identifier outside supported range: {raw}')
        mapping[raw] = str(value + 2**32 if value < 0 else value)
    if len(set(mapping.values())) != len(mapping):
        raise ValueError('Chart axis identifiers would collide after normalization')
    for node in nodes:
        node.set('val', mapping[node.get('val')])
    errors = axis_id_errors(chart)
    if errors:
        raise ValueError('; '.join(errors))
