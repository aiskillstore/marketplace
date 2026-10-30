#!/usr/bin/env python3
"""ChatSPSS public baseline: standalone statistical analyses and Markdown result tables."""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:  # keep the platform failure readable
    print(
        "ChatSPSS error: the runtime needs pandas and numpy for file analysis; "
        f"missing {exc.name}. Install the missing dependencies in an isolated Python environment using requirements.txt.",
        file=sys.stderr,
    )
    raise SystemExit(1)



def load_table(path: str, strict_columns: bool = False) -> pd.DataFrame:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"file not found: {path}")
    suf = p.suffix.lower()
    if suf == ".csv":
        for enc in ("utf-8-sig", "utf-8", "gb18030"):
            try:
                if strict_columns:
                    efa_header(pd.read_csv(p, encoding=enc, header=None, nrows=1).iloc[0])
                return pd.read_csv(p, encoding=enc)
            except UnicodeDecodeError:
                continue
    if suf in {".xlsx", ".xls"}:
        if strict_columns:
            efa_header(pd.read_excel(p, header=None, nrows=1).iloc[0])
        return pd.read_excel(p)
    if suf in {".sav", ".dta"}:
        try:
            import pyreadstat
        except ImportError as exc:
            raise RuntimeError("SPSS/Stata files need the optional pyreadstat dependency") from exc
        df, metadata = pyreadstat.read_sav(str(p)) if suf == ".sav" else pyreadstat.read_dta(str(p))
        return attach_labels(df, metadata)
    raise ValueError("supported files: .csv, .xlsx, .xls, .sav, .dta")


def cols(df: pd.DataFrame, text: str | None) -> list[str]:
    if not text:
        return list(df.columns)
    names = [x.strip() for x in text.replace("，", ",").split(",") if x.strip()]
    missing = [x for x in names if x not in df.columns]
    if missing:
        raise ValueError(f"unknown columns: {', '.join(missing)}")
    return names


def numeric(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    out = df[names].apply(pd.to_numeric, errors="coerce")
    if out.shape[1] == 0:
        raise ValueError("at least one numeric column is required")
    return out


"""Small display-only SAV/Stata metadata helpers; never recode data or sort labels."""

def attach_labels(df, metadata):
    """Keep file metadata in attrs while leaving original values and dtypes intact."""
    variable = getattr(metadata, 'column_names_to_labels', None) or {}
    values = getattr(metadata, 'variable_value_labels', None) or {}
    df.attrs['variable_labels'] = {
        k: v for k, v in variable.items() if v is not None and str(v).strip()
    }
    df.attrs['value_labels'] = {
        k: {value: label for value, label in mapping.items()
            if label is not None and str(label).strip()}
        for k, mapping in values.items() if mapping
    }
    return df


def variable_display(df, column):
    """Return a file variable label or the unchanged source column name."""
    label = df.attrs.get('variable_labels', {}).get(column, column)
    return column if label is None or not str(label).strip() else label


def value_display(df, column, value):
    """Return a value label for display, preserving the source value for analysis."""
    import pandas as pd
    try:
        label = df.attrs.get('value_labels', {}).get(column, {}).get(value)
        if label is not None and str(label).strip():
            return str(label)
    except (TypeError, ValueError):
        pass
    return str(value) if pd.notna(value) else 'NaN'


# Public formatting helpers for ordinary Markdown output.
def md_table(headers, rows, alignments=None, group_header=None):
    def escape(value):
        return str(value).replace('|', chr(92)+'|').replace(chr(13)+chr(10), ' ').replace(chr(13), ' ').replace(chr(10), ' ')
    alignments = alignments or ['c'] * len(headers)
    positions = {'l': ':---', 'c': ':---:', 'r': '---:'}
    lines = []
    if group_header:
        groups = [v.strip().replace('**','').replace('*','') for v in group_header.strip().strip('|').split('|') if v.strip() and v.strip() != '<']
        if groups:
            lines += ['**'+' ｜ '.join(groups)+'**', '']
    lines += ['| '+' | '.join(escape(v) for v in headers)+' |', '| '+' | '.join(positions.get(v, ':---:') for v in alignments)+' |']
    lines += ['| '+' | '.join(escape(v) for v in row)+' |' for row in rows]
    return '\n'.join(lines)


def fmt_num(value, decimals=3):
    if pd.isna(value):
        return '-'
    if np.isinf(value):
        return 'Inf' if value > 0 else '-Inf'
    return f'{value:.{decimals}f}'


def fmt_p(value):
    if value < .001:
        return '<0.001**'
    if value < .01:
        return f'{value:.3f}**'
    if value < .05:
        return f'{value:.3f}*'
    return f'{value:.3f}'


def fmt_sig(value):
    return '**' if value < .01 else '*' if value < .05 else ''


# Flat basic analyses. Shared imports/formatting helpers are supplied by analyze.py.

def _basic_names(names):
    return [names] if isinstance(names, str) else list(names)


def _basic_num(df, name):
    return pd.to_numeric(df[name], errors='coerce').dropna()


def _basic_value(value):
    return str(value) if pd.notna(value) else 'NaN'


def overview(df, names):
    rows = []
    for name in _basic_names(names):
        x = _basic_num(df, name)
        if len(x):
            rows.append([variable_display(df, name), str(len(x)), *[fmt_num(v) for v in (x.min(), x.max(), x.mean(), x.std(), x.median())]])
    if not rows:
        return '没有有效的数值列可供描述性统计分析。'
    return '## 描述性统计分析结果\n' + md_table(['变量', 'N', '最小值', '最大值', '均值', '标准差', '中位数'], rows, ['l'] + ['c'] * 6)


def frequency(df, names):
    names = _basic_names(names)
    rows, total = [], 0
    for name in names:
        if df[name].isna().all():
            continue
        counts = df[name].value_counts(dropna=False)
        n = counts.sum()
        total += int(n)
        items = []
        for value, count in counts.items():
            if pd.isna(value):
                key = (2, '')
            else:
                try:
                    key = (0, float(value))
                except (TypeError, ValueError):
                    key = (1, str(value))
            items.append((key, value_display(df, name, value), int(count), count / n * 100))
        items.sort(key=lambda x: x[0])
        cumulative = 0.0
        for i, (_, label, count, pct) in enumerate(items):
            cumulative += pct
            rows.append([variable_display(df, name) if i == 0 else '', label, str(count), f'{pct:.2f}%', f'{100.0 if i == len(items)-1 else cumulative:.2f}%'])
    if not rows:
        return '没有有效的列可供频数分析。'
    if len(names) == 1:
        rows.append(['**总计**', '', f'**{total}**', '**100.00%**', ''])
    return '## 频数分析结果\n\n' + md_table(['变量', '选项', '频数', '百分比(%)', '累积百分比(%)'], rows, ['l', 'l', 'c', 'c', 'c'])


def multiple_choice(df, names):
    patterns = [{0, 1}, {'0', '1'}, {'未选中', '选中'}, {'否', '是'}, {'No', 'Yes'}, {'no', 'yes'}, {'N', 'Y'}, {'FALSE', 'TRUE'}, {'False', 'True'}]
    positive = {1, '1', '选中', '是', 'Yes', 'yes', 'Y', 'TRUE', 'True', True}
    counts, selected = [], pd.Series(False, index=df.index)
    for name in _basic_names(names):
        x = df[name]
        values = x.dropna().unique()
        if len(values) > 2 or (len(values) != 2 and not any(set(values).issubset(p) for p in patterns)):
            continue
        value = next((v for v in values if v in positive), None)
        if value is None:
            value = max(values) if len(values) == 2 else 1
        yes = x == value
        selected |= yes
        counts.append((name, int(yes.sum())))
    if not counts:
        return '没有有效的二分类虚拟变量可用于多选题分析。'
    n = int(selected.sum())
    if not n:
        return '没有样本选择了任何选项。'
    total = sum(c for _, c in counts)
    rows = [[variable_display(df, name), str(c), f'{round(c / total * 100, 2):.2f}%', f'{round(c / n * 100, 2):.2f}%'] for name, c in counts]
    rows.append(['汇总', str(total), '100.00%', f'{round(total / n * 100, 2):.2f}%'])
    return '## 多选题分析结果\n\n' + md_table(['选项', '响应数', '响应率', f'普及率（n={n}）'], rows, ['l', 'c', 'c', 'c'])


def norm_reference(df, names, means=None, sds=None):
    from scipy import stats
    data = [(name, _basic_num(df, name)) for name in _basic_names(names)]
    data = [(name, x) for name, x in data if len(x) >= 3]
    if not data:
        return '错误：没有足够样本量的变量可供分析。'
    parts = ['## 常模分析结果\n']
    if means and sds:
        norm_means = [float(v) for v in means.split(',') if v.strip()] if isinstance(means, str) else list(means)
        norm_sds = [float(v) for v in sds.split(',') if v.strip()] if isinstance(sds, str) else list(sds)
        rows = []
        for (name, x), m, sd in zip(data, norm_means, norm_sds):
            difference = float(x.mean()) - m
            row = [variable_display(df, name), str(len(x)), f'{fmt_num(x.mean())} ({fmt_num(x.std())})', f'{fmt_num(m)} ({fmt_num(sd)})', fmt_num(difference)]
            if sd <= 0:
                row += ['-', '-', '常模SD无效，跳过']
            else:
                z = difference / (sd / (len(x) ** 0.5))
                p = float(2 * (1 - stats.norm.cdf(abs(z))))
                conclusion = ('显著高于外部常模' if z > 0 else '显著低于外部常模') if p < .01 else (('略高于外部常模' if z > 0 else '略低于外部常模') if p < .05 else '与外部常模无显著差异')
                row += [fmt_num(difference / sd, 3), fmt_p(p), conclusion]
            rows.append(row)
        if rows:
            parts += ['### 本研究样本与外部常模的比较\n', md_table(['变量', 'N', '本研究 M(SD)', '外部常模 M(SD)', '差值', "Cohen's d", 'p', '结论'], rows, ['l'] + ['c'] * 6 + ['l']), "\n注：差值=本研究均值-外部常模均值；Cohen's d=(本研究均值-外部常模均值)/外部常模SD；* p<0.05，** p<0.01。"]
    else:
        points = [5, 10, 25, 50, 75, 90, 95]
        rows = [[variable_display(df, name), str(len(x)), fmt_num(x.mean()), fmt_num(x.std()), *[fmt_num(float(np.percentile(x, p))) for p in points]] for name, x in data]
        parts += ['### 百分位常模表\n', md_table(['变量', 'N', 'M', 'SD'] + [f'P{p}' for p in points], rows, ['l'] + ['c'] * 10), '\n注：P5、P10、P25、P50、P75、P90、P95 分别表示对应百分位点。若样本并非代表性样本，本表应解释为本研究样本内部常模或样本百分位参考值。']
    return '\n'.join(parts)


def normality(df, names):
    from scipy import stats
    results = []
    for name in _basic_names(names):
        x = _basic_num(df, name)
        if len(x) < 3 or x.std() == 0 or x.nunique() < 3:
            continue
        skew, kurtosis = stats.skew(x), stats.kurtosis(x)
        if len(x) <= 5000:
            statistic, p = stats.shapiro(x)
            header = 'Shapiro-Wilk(W)'
        else:
            statistic, p = stats.kstest(x, stats.norm(loc=x.mean(), scale=x.std()).cdf)
            header = 'Kolmogorov-Smirnov(D)'
        conclusion = '符合正态分布' if p >= .05 else ('基本符合正态分布（依据偏度/峰度判据，非显著性 p 值）' if abs(skew) < 3 and abs(kurtosis) < 10 else '不符合正态分布')
        results.append((header, [variable_display(df, name), str(len(x)), *[fmt_num(v) for v in (x.mean(), x.std(), skew, kurtosis, statistic)], fmt_p(p), conclusion]))
    if not results:
        return '没有有效的数值列可供正态性检验分析。'
    header = results[0][0] if len(set(r[0] for r in results)) == 1 else '统计量'
    return '## 正态性检验分析结果\n\n' + md_table(['变量', 'N', '均值', '标准差', '偏度', '峰度', header, 'p值', '结论'], [r[1] for r in results], ['l'] + ['c'] * 7 + ['l']) + '\n\n注：\\* p<0.05 \\*\\* p<0.01'


def correlation(df, names, method='pearson'):
    from scipy import stats
    method = method.lower()
    if method not in ('pearson', 'spearman'):
        raise ValueError("method 参数必须是 'pearson' 或 'spearman'")
    data = pd.DataFrame({name: pd.to_numeric(df[name], errors='coerce') for name in _basic_names(names) if not pd.to_numeric(df[name], errors='coerce').isna().all()})
    if len(data.columns) < 2:
        return '错误：相关分析至少需要 2 个数值型变量。'
    if data.notna().sum().min() < 3:
        return '错误：有效数据不足 3 行。'
    rows = []
    for i, name in enumerate(data):
        row = [f'{i+1}.{variable_display(df, name)}', fmt_num(data[name].mean()), fmt_num(data[name].std())]
        for j, other in enumerate(data):
            if i == j:
                row.append('**1**')
            elif i < j:
                row.append('')
            else:
                pair = data[[name, other]].dropna()
                if len(pair) < 3:
                    row.append('-')
                else:
                    r, p = (stats.pearsonr if method == 'pearson' else stats.spearmanr)(pair[name], pair[other])
                    row.append(f'{r:.3f}{fmt_sig(p)}')
        rows.append(row)
    parts = []
    missing = int(data.isna().any(axis=1).sum())
    if missing:
        parts += [f'[notice] 数据含缺失值，采用成对删除（pairwise deletion）。共 {len(data)} 行中 {missing} 行 ({missing / len(data) * 100:.1f}%) 至少含一处缺失，各变量对的有效 N 见下表 N 列', '']
    parts += [f'## {"Pearson" if method == "pearson" else "Spearman"} 相关分析结果\n', md_table(['变量', '均值', '标准差'] + [str(i+1) for i in range(len(data.columns))], rows, ['l'] + ['c'] * (2 + len(data.columns))), f'\n注：\\* p<0.05 \\*\\* p<0.01，总行数 N = {len(data)}（各变量对采用成对删除，有效 N 可能不同）']
    return '\n'.join(parts)


def two_group(df, outcome, group):
    from scipy import stats
    groups = sorted(df[group].dropna().unique())
    if len(groups) != 2:
        raise ValueError('独立样本t检验需要恰好 2 个组。')
    a, b = [_basic_num(df.loc[df[group] == value], outcome) for value in groups]
    if len(a) < 2 or len(b) < 2:
        return '所有因变量的t检验均失败，请检查数据。'
    t, p = stats.ttest_ind(a, b)
    table = md_table(['变量', f'{value_display(df, group, groups[0])}(n={len(a)})', f'{value_display(df, group, groups[1])}(n={len(b)})', 't', 'p'], [[variable_display(df, outcome), f'{fmt_num(a.mean(), 2)}±{fmt_num(a.std(), 2)}', f'{fmt_num(b.mean(), 2)}±{fmt_num(b.std(), 2)}', fmt_num(t), fmt_p(p)]], ['l'] + ['c'] * 4)
    return f'## 独立样本t检验结果\n\n分组变量: {variable_display(df, group)}\n\n{table}\n\n注：\\* p<0.05 \\*\\* p<0.01；t自由度：{variable_display(df, outcome)} df={len(a)+len(b)-2}'


def paired(df, before, after):
    from scipy import stats
    data = df[[before, after]].apply(pd.to_numeric, errors='coerce').dropna()
    if len(data) < 3:
        return '所有配对变量的t检验均失败，请检查数据。'
    a, b = data[before], data[after]
    t, p = stats.ttest_rel(a, b)
    row = [f'{variable_display(df, before)} 配对 {variable_display(df, after)}', f'{fmt_num(a.mean(), 2)}±{fmt_num(a.std(), 2)}', f'{fmt_num(b.mean(), 2)}±{fmt_num(b.std(), 2)}', fmt_num((a-b).mean()), fmt_num(t), fmt_p(p)]
    table = md_table(['配对变量', '配对1(M±SD)', '配对2(M±SD)', '均值差', 't', 'p'], [row], ['l'] + ['c'] * 5)
    return f"## 配对样本t检验结果\n\n{table}\n\n注：\\* p<0.05 \\*\\* p<0.01；t自由度：{variable_display(df, before)}配{variable_display(df, after)} df={len(data)-1}"


def chi_square(df, row, col):
    from scipy import stats
    data = df[[row, col]].dropna()
    if row == col or len(data) < 5:
        raise ValueError('卡方检验需要两个不同变量及至少 5 行有效数据。')
    cross = pd.crosstab(data[row], data[col])
    if min(cross.shape) < 2:
        raise ValueError('卡方检验需要行、列变量各至少两个有效类别。')
    chi, p, dof, expected = stats.chi2_contingency(cross)
    columns = list(cross.columns)
    n = int(cross.to_numpy().sum())
    v = math.sqrt(chi / (n * (min(cross.shape) - 1)))
    rows = []
    for i, label in enumerate(cross.index):
        cells = [f'{int(cross.loc[label, c])}({cross.loc[label, c] / cross[c].sum() * 100:.2f}%)' for c in columns]
        rows.append([variable_display(df, row) if i == 0 else '', value_display(df, row, label), *cells, str(int(cross.loc[label].sum())), fmt_num(chi) if i == 0 else '', fmt_p(p) if i == 0 else ''])
    table = md_table(['变量', '类别'] + [value_display(df, col, c) for c in columns] + ['合计', 'χ²', 'p'], rows, ['l', 'l'] + ['c'] * (len(columns)+3))
    return f"## 卡方检验结果\n\n列变量: {variable_display(df, col)}\n\n{table}\n\n注：\\* p<0.05 \\*\\* p<0.01；频数格式为 频数(列百分比%)\n\n注：{variable_display(df, row)}：Cramer's V = {fmt_num(v)}，df = {dof}，N = {n}；最小期望频数 = {expected.min():.2f}；期望频数 <5 的单元格 {int((expected < 5).sum())}/{expected.size} 个"


def anova(df, outcome, group):
    from scipy import stats
    data = df[[group, outcome]].dropna()
    if len(data) < 5:
        return '所有因变量的方差分析均失败，请检查数据。'
    data = data.assign(**{outcome: pd.to_numeric(data[outcome], errors='coerce')}).dropna()
    try:
        groups = sorted(data[group].unique())
    except TypeError:
        groups = sorted(data[group].unique(), key=lambda v: (str(v).casefold(), type(v).__name__, repr(v)))
    if len(groups) < 2:
        return '所有因变量的方差分析均失败，请检查数据。'
    samples = [data.loc[data[group] == g, outcome] for g in groups]
    f, p = stats.f_oneway(*samples)
    headers = ['变量'] + [f'{value_display(df, group, g)}(n={len(x)})' for g, x in zip(groups, samples)] + ['F', 'p']
    row = [variable_display(df, outcome)] + [f'{fmt_num(x.mean(), 2)}±{fmt_num(x.std(), 2)}' for x in samples] + [fmt_num(f), fmt_p(p)]
    table = md_table(headers, [row], ['l'] + ['c'] * (len(groups)+2))
    return f'## 单因素方差分析结果\n\n分组变量: {variable_display(df, group)}\n\n{table}\n\n注：\\* p<0.05 \\*\\* p<0.01；{variable_display(df, outcome)}：F df1={len(groups)-1}, df2={len(data)-len(groups)}'


def nonparametric(df, outcome, group):
    from scipy import stats
    groups = sorted(df[group].dropna().unique())
    if len(groups) < 2:
        raise ValueError('非参数检验需要至少 2 个组。')
    samples = [_basic_num(df.loc[df[group] == g], outcome) for g in groups]
    def median_iqr(x):
        return f'{fmt_num(x.median())}({fmt_num(x.quantile(.25))}, {fmt_num(x.quantile(.75))})'
    prefix = f'## 非参数检验结果\n\n分组变量: {variable_display(df, group)}\n\n\n### '
    if len(groups) == 2:
        a, b = samples
        if min(len(a), len(b)) < 1:
            return '所有因变量的非参数检验均失败，请检查数据。'
        u, p = stats.mannwhitneyu(a, b, alternative='two-sided')
        z = (u - len(a)*len(b)/2) / np.sqrt(len(a)*len(b)*(len(a)+len(b)+1)/12)
        effect = abs(z) / np.sqrt(len(a)+len(b))
        headers = ['变量'] + [f'M(P25,P75) {value_display(df, group, g)}(n={len(x)})' for g, x in zip(groups, samples)] + ['U', 'z', 'p', 'r']
        row = [variable_display(df, outcome), median_iqr(a), median_iqr(b), fmt_num(u, 1), fmt_num(z), fmt_p(p), fmt_num(effect)]
        table = md_table(headers, [row], ['l'] + ['c'] * 6)
        return prefix + 'Mann-Whitney U 检验\n\n' + table + '\n\n\\* p<0.05 \\*\\* p<0.01 \\*\\*\\* p<0.001; r = \\|z\\|/sqrt(N), 0.1 small / 0.3 medium / 0.5 large'
    populated = [(i, g, x) for i, (g, x) in enumerate(zip(groups, samples)) if len(x)]
    if len(populated) < 2:
        return '所有因变量的非参数检验均失败，请检查数据。'
    h, p = stats.kruskal(*[x for _, _, x in populated])
    n = sum(len(x) for _, _, x in populated)
    headers = ['变量'] + [f'M(P25,P75) {chr(65+i)}.{value_display(df, group, g)}(n={len(x)})' for i, g, x in populated] + ['H', 'p', 'η²']
    row = [variable_display(df, outcome)] + [median_iqr(x) for _, _, x in populated] + [fmt_num(h), fmt_p(p), fmt_num(h/(n-1))]
    table = md_table(headers, [row], ['l'] + ['c'] * (len(populated)+3))
    return prefix + 'Kruskal-Wallis H 检验\n\n' + table + f'\n\n\\* p<0.05 \\*\\* p<0.01 \\*\\*\\* p<0.001; η² = H/(N-1), 0.01 small / 0.06 medium / 0.14 large；H自由度：{variable_display(df, outcome)} df={len(populated)-1}'


def word_frequency(df, column, top=30):
    from collections import Counter
    import logging
    import warnings
    stopwords = set(('的 了 是 在 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有 看 好 '
        '自己 这 他 她 它 们 那 里 为 什么 吗 与 及 等 但 而 或 从 中 把 被 让 对 给 向 '
        '还 可以 这个 那个 如果 因为 所以 虽然 但是 然后 可能 应该 已经 之后 以及 '
        '非常 比较 一些 这些 那些 每个 什么样 怎么 为什么 的话 之前 以后 其他 '
        '不是 没 能 想 做 用 啊 吧 呢 嗯 哦 呀 么 哈 嘛 啦 哪 '
        'the a an is are was were be been being have has had do does did will would '
        'shall should can could may might must need dare to of in on at by for with '
        'and or but not no nor so yet both either neither each every all any few more '
        'most other some such than that this these those I you he she it we they me '
        'him her us them my your his its our their mine yours hers ours theirs').split())
    texts = df[column].dropna().astype(str).tolist()
    if not texts:
        return '错误：指定列中没有有效文本数据。'
    if not ' '.join(texts).strip():
        return '错误：文本内容为空。'
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='pkg_resources is deprecated as an API.*', category=UserWarning)
            import jieba
        jieba.setLogLevel(logging.ERROR)
        segment = jieba.lcut
        tool = 'jieba'
    except ImportError:
        segment = lambda text: re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{2,}', text)
        tool = '正则提取（降级模式）'
    counts = Counter()
    for text in texts:
        counts.update(w.strip() for w in segment(text) if len(w.strip()) >= 2 and w.strip().lower() not in stopwords)
    total = sum(counts.values())
    if not total:
        return '错误：分词后没有有效词语（可能全部被停用词过滤）。'
    rows = [[str(i), w, str(n), fmt_num(n/total*100, 2)] for i, (w, n) in enumerate(counts.most_common(top), 1)]
    parts = ['## 词频分析结果\n', '### 数据概览\n', f'分析列: {variable_display(df, column)}', f'文本条数: {len(texts)}', f'有效词语总数: {total}', f'去重词语数: {len(counts)}', f'分词工具: {tool}\n', f'### 高频词表（Top {min(top, len(counts))}）\n', md_table(['排名', '词语', '频次', '占比(%)'], rows, ['c', 'l', 'c', 'c'])]
    if len(counts) >= 10:
        values = list(counts.values())
        bins = [sum(n == 1 for n in values), sum(2 <= n <= 5 for n in values), sum(6 <= n <= 20 for n in values), sum(n > 20 for n in values)]
        rows = [[label, str(n), fmt_num(n / len(counts)*100, 1)] for label, n in zip(['1 次', '2-5 次', '6-20 次', '>20 次'], bins)]
        parts += ['\n### 词频分布\n', md_table(['频次区间', '词语数', '占比(%)'], rows, ['l', 'c', 'c'])]
    parts.append('\n注：词频统计基于 jieba 分词，已去除停用词。')
    return '\n'.join(parts)


# Standalone basic analyses; Chinese Markdown result tables.
# No application framework, registry, label runtime, or snapshot imports.

def _am_drop_na(df, subset=None):
    if df is None or len(df) == 0:
        return (df, None)
    before = len(df)
    if isinstance(df, pd.Series):
        df_clean = df.dropna()
    elif subset is not None:
        df_clean = df.dropna(subset=subset)
    else:
        df_clean = df.dropna()
    after = len(df_clean)
    dropped = before - after
    if dropped == 0:
        return (df_clean, None)
    pct = dropped / before * 100
    notice = '[notice] 本次分析因含缺失值剔除 {dropped} 行 ({pct:.1f}%), 剩余 {after} 行'.format(dropped=dropped, pct=pct, after=after)
    return (df_clean, notice)

def _am_duplicates(matched_cols):
    seen = set()
    dups = set()
    for c in matched_cols:
        if c in seen:
            dups.add(c)
        else:
            seen.add(c)
    return sorted(dups)

def _am_intercept(X):
    intercept_name = '__cs_intercept__'
    while intercept_name in X.columns:
        intercept_name = '_' + intercept_name
    X_with_intercept = X.copy()
    X_with_intercept.insert(0, intercept_name, 1.0)
    return (X_with_intercept, intercept_name)

def _am_check_rank(X, variable_display_names=None):
    rank = int(np.linalg.matrix_rank(X.to_numpy(dtype='float64')))
    n_cols = X.shape[1]
    if rank >= n_cols:
        return None
    names_map = variable_display_names or {}
    cols = list(X.columns)
    kept = []
    redundant = []
    running_rank = 0
    for c in cols:
        trial_cols = kept + [c]
        trial_rank = int(np.linalg.matrix_rank(X[trial_cols].to_numpy(dtype='float64')))
        if trial_rank > running_rank:
            kept.append(c)
            running_rank = trial_rank
        else:
            redundant.append(c)
    redundant = [c for c in redundant if c != 'const']
    if not redundant:
        redundant = [c for c in cols if c != 'const']
    involved = [names_map.get(c, c) for c in redundant]
    involved_str = '、'.join((str(v) for v in involved))
    return f'错误：自变量之间存在完全共线关系（设计矩阵不满秩：秩 {rank} / 需要 {n_cols} 列），模型无法估计。涉及的自变量：{involved_str}。常见原因：把同一个类别变量的全部类别哑变量（含参照组）都当成独立自变量传入——应只保留其中 k-1 个哑变量，去掉一个作参照组；或其中存在两个完全线性相关/重复的变量。请去掉其中冗余的变量后重新分析。'

def regression(df, outcome, predictors):
    import sys
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.stattools import durbin_watson
    _state = {'df': df, 'matched_dependent': outcome, 'matched_independent': dict.fromkeys(predictors), 'warnings': []}
    _state['matched_independent'] = {c: c for c in predictors}

    def _analyze_and_format():
        lang = 'zh'
        if not _state['matched_dependent']:
            return '错误：因变量未匹配。'
        y_col = _state['matched_dependent']
        x_cols = list(_state['matched_independent'].values())
        dup_cols = _am_duplicates([y_col] + x_cols)
        if dup_cols:
            return '错误：因变量与自变量中有多个被解析到同一实际列（' + '、'.join(dup_cols) + '），会导致因变量被当成自变量之一参与回归。请检查 --dependent-var与 --independent-vars 中的名称是否重复，或存在拼写/标点差异导致被合并为同一列。'
        data_cols = [y_col] + x_cols
        valid_data = _state['df'][data_cols].copy()
        X = valid_data[x_cols].copy()
        y = valid_data[y_col].copy()
        for col in x_cols:
            numeric_series = pd.to_numeric(X[col], errors='coerce')
            is_categorical = X[col].dtype == 'object' or X[col].dtype.name == 'category' or (not pd.api.types.is_numeric_dtype(X[col]) and numeric_series.isnull().sum() > len(X) * 0.5)
            if is_categorical:
                non_null = X[col].dropna()
                if len(non_null) == 0:
                    continue
                display = variable_display(df, col)
                return f"错误：自变量 '{display}' 是非数值分类列，线性回归不自动决定编码。请先由 AI 在分析前完成可复核的外部预处理：名义分类（如城市）展开为哑变量并保留基准组；有序分类按明确顺序编码，再传入生成的数值列。若确认该列确有顺序，先按已确认的类别顺序生成数值列再运行。"
            else:
                X[col] = numeric_series
        if not pd.api.types.is_numeric_dtype(y):
            y = pd.to_numeric(y, errors='coerce')
        combined, _notice = _am_drop_na(pd.concat([X, y], axis=1))
        if _notice:
            _state['warnings'].append(_notice)
        n_samples = len(combined)
        min_required = len(x_cols) + 2
        if n_samples < min_required:
            return f'错误：有效样本量不足（当前 {n_samples}，至少需要 {min_required}）。请检查因变量是否为数值型，或自变量是否包含过多缺失值。'
        X_before_dropna = X
        X = combined[x_cols]
        y = combined[y_col]
        constant_predictors = [col for col in x_cols if X[col].nunique(dropna=True) <= 1]
        if constant_predictors:
            originally_constant = [c for c in constant_predictors if X_before_dropna[c].dropna().nunique() <= 1]
            became_constant_after_dropna = [c for c in constant_predictors if c not in originally_constant]
            detail_bits = []
            if originally_constant:
                names = [variable_display(df, c) for c in originally_constant]
                detail_bits.append(f"{'、'.join(names)}：原始数据里该列本身就只有 1 个唯一取值，与本次缺失值剔除无关——请确认是否传错了列，或该列在这批数据里本来就不该作为自变量")
            if became_constant_after_dropna:
                names = [variable_display(df, c) for c in became_constant_after_dropna]
                detail_bits.append(f"{'、'.join(names)}：该列本身有变化，但与其它列联合剔除缺失值后，剩余{n_samples} 个有效样本里只剩 1 个唯一取值——不是这批原始数据本身的问题，是当前自变量组合下的有效样本范围过窄；请检查为什么这么多行被联合剔除（缺失值集中在哪些列），或减少同时使用的自变量数量")
            return '错误：以下自变量在有效样本中是常数（没有变化），不能用于线性回归——' + '；'.join(detail_bits) + '。请移除这些列后重试，或调整自变量组合。'
        try:
            X_const, intercept_name = _am_intercept(X)
            model = sm.OLS(y, X_const)
            results = model.fit()
        except Exception as e:
            msg = f'线性回归模型拟合失败: {e}'
            print(f'[error] {msg}', file=sys.stderr)
            _state['warnings'].append(msg)
            return f'错误：{msg}'
        vif_values = {}
        for var in x_cols:
            try:
                col_idx = X_const.columns.get_loc(var)
                vif_values[var] = variance_inflation_factor(X_const.values, col_idx)
            except Exception as e:
                msg = 'VIF 计算失败（变量 {variable}）: {error}'.format(variable=var, error=e)
                print(f'[warning] {msg}', file=sys.stderr)
                _state['warnings'].append(msg)
                vif_values[var] = float('nan')
        dw_stat = durbin_watson(results.resid)
        f_stat = results.fvalue
        f_pvalue = results.f_pvalue
        if np.isnan(f_pvalue):
            f_pvalue = None
        df1 = len(x_cols)
        df2 = n_samples - len(x_cols) - 1
        dep_display = variable_display(df, y_col)
        parts = []
        parts.append('## 线性回归分析结果\n')

        def _fmt_b_with_sig(b_value, p_value):
            b_str = fmt_num(b_value)
            if p_value < 0.01:
                return f'{b_str}\\*\\*'
            elif p_value < 0.05:
                return f'{b_str}\\*'
            return b_str
        n_cols = 8
        group_header = '| | **非标准化系数** | < | **标准化系数** | < | < | **共线性诊断** | < |'
        headers = ['**变量**', '**B**', '**标准误**', '**Beta**', '**t**', '**p**', '**VIF**', '**容差**']
        alignments = ['l', 'r', 'r', 'c', 'r', 'c', 'r', 'r']
        rows = []
        rows.append(['(常数)', fmt_num(results.params.at[intercept_name]), fmt_num(results.bse.at[intercept_name]), '—', fmt_num(results.tvalues.at[intercept_name]), fmt_p(results.pvalues.at[intercept_name]), '—', '—'])
        for var in x_cols:
            var_display = variable_display(df, var)
            beta = results.params.at[var] * X[var].std() / y.std()
            vif_val = vif_values[var]
            tolerance = 1.0 / vif_val if not np.isnan(vif_val) and vif_val != 0 else float('nan')
            p_val = results.pvalues.at[var]
            rows.append([var_display, _fmt_b_with_sig(results.params.at[var], p_val), fmt_num(results.bse.at[var]), fmt_num(beta), fmt_num(results.tvalues.at[var]), fmt_p(p_val), fmt_num(vif_val), fmt_num(tolerance)])
        table_md = md_table(headers, rows, alignments=alignments, group_header=group_header)
        if f_pvalue is None:
            f_p_inline = 'p=—'
        elif f_pvalue < 0.001:
            f_p_inline = 'p<0.001'
        else:
            f_p_inline = f'p={f_pvalue:.3f}'
        _tail = ' |  |  |  |  |  |  |'
        tail_lines = [f'| R² | {fmt_num(results.rsquared)}{_tail}', f"| {'调整 R²'} | {fmt_num(results.rsquared_adj)}{_tail}", f'| F | F({df1},{df2})={fmt_num(f_stat)}, {f_p_inline}{_tail}', f"| {'D-W 值'} | {fmt_num(dw_stat)}{_tail}", f'| N | {n_samples}{_tail}']
        table_md = table_md + '\n' + '\n'.join(tail_lines)
        trailing = '\n\n**备注：** 因变量 = {dependent_variable}。\n\n**显著性：** \\* p<0.05，\\*\\* p<0.01。\n'.format(dependent_variable=dep_display)
        parts.append(table_md + trailing)
        high_vif = [(var, vif_values[var]) for var in x_cols if not np.isnan(vif_values[var]) and vif_values[var] > 10]
        if high_vif:
            vif_warning = ', '.join((f'{variable_display(df, v)}(VIF={fmt_num(val)})' for v, val in high_vif))
            parts.append('\n> 注意：以下变量存在严重多重共线性问题（VIF>10）：{variables}'.format(variables=vif_warning))
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def logistic(df, outcome, predictors):
    import sys
    import warnings
    import numpy as np
    import pandas as pd
    from statsmodels.discrete.discrete_model import Logit
    from statsmodels.tools.sm_exceptions import PerfectSeparationError
    from scipy import stats
    _state = {'df': df, 'matched_dependent': outcome, 'matched_independent': dict.fromkeys(predictors), 'warnings': []}
    _state['matched_independent'] = {c: c for c in predictors}

    def _with_internal_intercept(X):
        return _am_intercept(X)

    def _safe_exp(value):
        value = float(value)
        if np.isnan(value):
            return float('nan')
        if value > float(np.log(np.finfo(float).max)):
            return float('inf')
        if value < float(np.log(np.finfo(float).tiny)):
            return 0.0
        return float(np.exp(value))

    def _validate_binary_y(y_raw):
        clean_y, _notice_clean_y = _am_drop_na(y_raw)
        if _notice_clean_y:
            _state['warnings'].append(_notice_clean_y)
        if clean_y.dtype == object:
            stripped = clean_y.astype(str).str.strip()
            empty_mask = stripped == ''
            if empty_mask.any():
                n_empty = int(empty_mask.sum())
                stripped = stripped[~empty_mask]
                _state['warnings'].append(f'因变量中有 {n_empty} 个空字符串值（去除首尾空格后为空）已作为缺失值剔除。')
            numeric_attempt = pd.to_numeric(stripped, errors='coerce')
            if numeric_attempt.notna().all():
                clean_y = numeric_attempt
            else:
                clean_y = stripped
        unique_values = sorted(clean_y.unique())
        if len(unique_values) == 2 and set(unique_values) == {0, 1}:
            return clean_y
        if len(unique_values) != 2:
            raise ValueError(f'因变量必须是二元变量（只有两个不同的值），当前有 {len(unique_values)} 个不同值: {unique_values}')
        smaller, larger = unique_values
        encoded = clean_y.map({smaller: 0, larger: 1})
        dep_display = variable_display(df, _state['matched_dependent'])
        _state['warnings'].append("因变量 '{variable}' 已自动编码为二元变量: {smaller} -> 0, {larger} -> 1".format(variable=dep_display, smaller=smaller, larger=larger))
        return encoded

    def _encode_categorical_x(data):
        x_cols = list(_state['matched_independent'].values())
        for col in x_cols:
            numeric_series = pd.to_numeric(data[col], errors='coerce')
            is_categorical = data[col].dtype == 'object' or data[col].dtype.name == 'category' or numeric_series.isnull().sum() > len(data) * 0.5
            if is_categorical:
                non_null, _notice_non_null = _am_drop_na(data[col])
                if _notice_non_null:
                    _state['warnings'].append(_notice_non_null)
                if len(non_null) == 0:
                    raise ValueError(f"自变量 '{col}' 全部为空值")
                unique_vals = sorted(non_null.unique().astype(str))
                encoding_map = {val: i + 1 for i, val in enumerate(unique_vals)}
                data[col] = data[col].astype(str).map(encoding_map)
                display = variable_display(df, col)
                encoding_desc = '; '.join((f'{k} -> {v}' for k, v in list(encoding_map.items())[:5]))
                if len(encoding_map) > 5:
                    encoding_desc += '...'
                msg = "自变量 '{variable}' 为分类变量，已自动编码: {encoding}".format(variable=display, encoding=encoding_desc)
                print(f'[info] {msg}', file=sys.stderr)
                _state['warnings'].append(msg)
                _state['warnings'].append("注意：'{variable}' 已使用顺序编码（1,2,3...），若为名义变量（无序分类），建议改用哑变量编码以避免引入虚假排序关系。".format(variable=display))
            else:
                data[col] = numeric_series
        return data

    def _select_variables(X, y):
        return list(X.columns)

    def _pseudo_r_squared(null_ll, final_ll, n):
        try:
            mcfadden = 1 - final_ll / null_ll
            cox_snell = 1 - np.exp(-2 * (final_ll - null_ll) / n)
            max_cs = 1 - np.exp(2 * null_ll / n)
            nagelkerke = cox_snell / max_cs if max_cs != 0 else 0.0
            return {'mcfadden': mcfadden, 'cox_snell': cox_snell, 'nagelkerke': nagelkerke}
        except Exception as e:
            print(f"[warning] {'伪R2计算失败: {error}'.format(error=e)}", file=sys.stderr)
            return {'mcfadden': 0.0, 'cox_snell': 0.0, 'nagelkerke': 0.0}

    def _preflight_design_matrix(X, y, *, check_rank):
        zero_variance = [col for col in X.columns if X[col].nunique(dropna=True) <= 1]
        if zero_variance:
            names = [col for col in zero_variance]
            return '错误：以下自变量在有效样本中没有变化，不能用于二元逻辑回归：' + '、'.join(names) + '。请移除后重试。'
        columns = list(X.columns)
        if check_rank:
            duplicate_pairs = []
            for pos, left in enumerate(columns):
                for right in columns[pos + 1:]:
                    if X[left].equals(X[right]):
                        duplicate_pairs.append((left, right))
            if duplicate_pairs:
                pairs = [f'{left} 与 {right}' for left, right in duplicate_pairs]
                return '错误：检测到重复的自变量（' + '；'.join(pairs) + '），会导致模型不可估计。请只保留其中一个。'
            relative_singular_tolerance = float(np.sqrt(np.finfo(float).eps))

            def _is_rank_deficient(frame):
                raw_predictors = frame.to_numpy(dtype=float)
                centered = raw_predictors - raw_predictors.mean(axis=0)
                scales = np.linalg.norm(centered, axis=0)
                standardized = centered / scales
                normalized_intercept = np.ones(len(frame), dtype=float) / np.sqrt(len(frame))
                design = np.column_stack([normalized_intercept, standardized])
                singular_values = np.linalg.svd(design, compute_uv=False)
                relative_smallest = singular_values[-1] / singular_values[0] if singular_values.size and singular_values[0] > 0 else 0.0
                return design.shape[1] > design.shape[0] or relative_smallest <= relative_singular_tolerance
            numerically_rank_deficient = _is_rank_deficient(X)
            if numerically_rank_deficient:
                kept = []
                redundant = []
                for col in columns:
                    candidate = X[kept + [col]]
                    if _is_rank_deficient(candidate):
                        redundant.append(col)
                    else:
                        kept.append(col)
                names = [col for col in redundant]
                detail = '、'.join(names) if names else '相关自变量'
                return '错误：自变量设计矩阵秩不足；按当前变量顺序识别到可移除的冗余变量，涉及的自变量：' + detail + '。变量之间存在完全或数值上近乎完全线性相关，或有效样本相对于自变量数量不足。请先移除这些变量后重试；若仍失败，再尝试中心化变量、调整计量单位并检查相关性。'
        for col in columns:
            values = X[col]
            zero_values = values[y == 0]
            one_values = values[y == 1]
            if zero_values.max() < one_values.min() or one_values.max() < zero_values.min():
                return '错误：自变量「' + col + '」存在可完全分隔两类结局的阈值，属于完全分离，二元逻辑回归系数无法有限估计。请检查分组边界、增加重叠样本，或移除该变量后重试。'
        return None

    def _recoverable_fit_error(exc):
        detail = str(exc)
        lowered = detail.lower()
        if isinstance(exc, PerfectSeparationError) or 'perfect separation' in lowered:
            return '错误：检测到完全或近完全分离：预测变量几乎能完全区分两类结局，二元逻辑回归系数无法稳定估计。请合并稀疏类别、增加重叠样本，或减少相关自变量后重试。'
        if 'singular matrix' in lowered:
            return '错误：逻辑回归设计矩阵不可逆（Singular matrix）。这可能来自未被预检捕获的线性相关、稀疏类别或分离问题，无法仅凭该错误确定唯一原因。请检查自变量相关性、类别交叉表和两类结局的重叠情况后重试。'
        return None

    def _fit_logit_once(y, design, **fit_kwargs):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            result = Logit(y, design).fit(disp=0, **fit_kwargs)
        return (result, caught)

    def _has_separation_warning(caught):
        return any(('PerfectSeparation' in warning.category.__name__ for warning in caught))

    def _fit_not_converged(result, caught):
        retvals = getattr(result, 'mle_retvals', None) or {}
        if retvals.get('converged') is False:
            return True
        return any(('ConvergenceWarning' in warning.category.__name__ for warning in caught))

    def _standard_errors_invalid(result):
        try:
            bse = np.asarray(result.bse, dtype=float)
        except Exception:
            return True
        return not bool(np.all(np.isfinite(bse)))

    def _fit_logit_or_raise_recoverable(y, design):
        try:
            result, caught = _fit_logit_once(y, design)
            if not _has_separation_warning(caught) and _fit_not_converged(result, caught):
                result, caught = _fit_logit_once(y, design, maxiter=_state['_SAFE_RERUN_MAXITER'])
        except Exception as exc:
            recovered = _recoverable_fit_error(exc)
            if recovered:
                raise ValueError(recovered) from None
            raise
        if _has_separation_warning(caught):
            raise ValueError('错误：检测到完全或近完全分离：预测变量几乎能完全区分两类结局，二元逻辑回归系数无法稳定估计。请合并稀疏类别、增加重叠样本，或减少相关自变量后重试。')
        if _fit_not_converged(result, caught):
            raise ValueError('错误：逻辑回归模型没有收敛（已自动加大迭代次数重跑一次，估计仍不稳定），因此不给出系数、OR、置信区间和显著性。常见原因是自变量之间存在近乎完全的线性关系（例如由其他列换算得到的列）、稀疏类别或接近完全分离，也可能是某个变量数值极大而几乎不变（如时间戳、编号）。请移除高度相关或派生的变量、合并稀疏类别，或先把数值极大的变量减去均值（中心化）后重试。')
        if _standard_errors_invalid(result):
            raise ValueError('错误：逻辑回归的标准误无法计算（协方差矩阵无效），因此不给出系数、OR、置信区间和显著性。请检查自变量之间是否存在近乎完全的线性关系或稀疏类别后重试。')
        return result

    def _analyze_and_format():
        if not _state['matched_dependent']:
            return '错误：因变量未匹配。'
        y_col = _state['matched_dependent']
        x_cols = list(_state['matched_independent'].values())
        duplicate_roles = _am_duplicates([y_col] + x_cols)
        if duplicate_roles:
            return '错误：因变量和自变量中有多个请求被解析到同一实际列（' + '、'.join(duplicate_roles) + '），请检查变量名是否重复或存在拼写/标点差异。'
        data = _state['df'][[y_col] + x_cols].copy()
        data = _encode_categorical_x(data)
        original_count = len(data)
        data, _notice_data = _am_drop_na(data)
        if _notice_data:
            _state['warnings'].append(_notice_data)
        final_count = len(data)
        if original_count != final_count:
            _state['warnings'].append('数据清理：移除了 {rows} 行包含缺失值的数据'.format(rows=original_count - final_count))
        if final_count < 30:
            return f'错误：有效数据量不足 30 行（当前 {final_count} 行），无法进行可靠的逻辑回归分析。'
        try:
            y = _validate_binary_y(data[y_col])
        except ValueError as e:
            return f'错误：{e}'
        data = data.loc[y.index]
        X = data[x_cols]
        for col in x_cols:
            if not pd.api.types.is_numeric_dtype(X[col]):
                X[col] = pd.to_numeric(X[col], errors='coerce')
        combined, _notice_combined = _am_drop_na(pd.concat([X, y], axis=1))
        if _notice_combined:
            _state['warnings'].append(_notice_combined)
        X = combined[x_cols].astype('float64')
        y = combined[y_col].astype('float64')
        n_samples = len(combined)
        if n_samples < 30:
            return f'错误：有效样本量不足 30（当前 {n_samples}），无法进行可靠的逻辑回归分析。'
        preflight_error = _preflight_design_matrix(X, y, check_rank=True)
        if preflight_error:
            return preflight_error
        selected_vars = _select_variables(X, y)
        method_cn = '全进入法'
        if not selected_vars:
            _state['warnings'].append('所有变量均不显著，最终模型仅包含截距项')
        else:
            final_design_error = _preflight_design_matrix(X[selected_vars], y, check_rank=True)
            if final_design_error:
                return final_design_error
        X_null, null_intercept_name = _with_internal_intercept(pd.DataFrame(index=X.index))
        try:
            null_model = _fit_logit_or_raise_recoverable(y, X_null)
        except ValueError as e:
            return str(e)
        except Exception as e:
            msg = f'仅截距模型拟合失败: {e}'
            print(f'[error] {msg}', file=sys.stderr)
            return f'错误：{msg}'
        if selected_vars:
            X_final, final_intercept_name = _with_internal_intercept(X[selected_vars])
            try:
                final_model = _fit_logit_or_raise_recoverable(y, X_final)
            except ValueError as e:
                return str(e)
            except Exception as e:
                msg = f'逻辑回归模型拟合失败: {e}'
                print(f'[error] {msg}', file=sys.stderr)
                return f'错误：{msg}'
        else:
            final_model = null_model
            final_intercept_name = null_intercept_name
        ll_null = float(null_model.llf)
        ll_final = float(final_model.llf)
        chi2 = float(-2 * (ll_null - ll_final))
        df_model = len(selected_vars)
        chi2_p = float(1 - stats.chi2.cdf(chi2, df_model)) if df_model > 0 else 1.0
        r2 = _pseudo_r_squared(ll_null, ll_final, n_samples)
        dep_display = variable_display(df, y_col)
        parts = []
        parts.append('## 二元逻辑回归分析结果\n')
        parts.append('因变量: {dependent}，分析方法: {method}，候选变量: {candidates} 个，最终保留: {retained} 个\n'.format(dependent=dep_display, method=method_cn, candidates=len(x_cols), retained=len(selected_vars)))
        parts.append('### 模型似然比检验\n')
        lrt_headers = ['模型', '-2倍对数似然值', '卡方值', 'df', 'p', 'AIC 值', 'BIC 值']
        lrt_rows = [['仅截距', fmt_num(-2 * ll_null), '-', '-', '-', '-', '-'], ['最终模型', fmt_num(-2 * ll_final), fmt_num(chi2), str(df_model), fmt_p(chi2_p), fmt_num(float(final_model.aic)), fmt_num(float(final_model.bic))]]
        parts.append(md_table(lrt_headers, lrt_rows, ['l', 'r', 'r', 'c', 'c', 'r', 'r']))
        parts.append('\n### 回归系数\n')

        def _fmt_b_sig(b_val, p_val):
            b_str = fmt_num(b_val)
            if p_val < 0.01:
                return f'{b_str}\\*\\*'
            if p_val < 0.05:
                return f'{b_str}\\*'
            return b_str
        coef_headers = ['变量', '回归系数', '标准误', 'z 值', 'Wald χ²', 'p 值', 'OR 值', 'OR值95% CI']
        coef_alignments = ['l', 'r', 'r', 'r', 'r', 'c', 'r', 'c']
        coef_rows = []
        for var in selected_vars:
            if var in final_model.params.index:
                coef = float(final_model.params.at[var])
                se = float(final_model.bse.at[var])
                z_val = float(final_model.tvalues.at[var])
                wald = z_val ** 2
                p_val = float(final_model.pvalues.at[var])
                or_val = _safe_exp(coef)
                ci = final_model.conf_int().loc[var].values
                ci_lo = _safe_exp(ci[0])
                ci_hi = _safe_exp(ci[1])
                var_display = variable_display(df, var)
                coef_rows.append([var_display, _fmt_b_sig(coef, p_val), fmt_num(se), fmt_num(z_val), fmt_num(wald), fmt_p(p_val), fmt_num(or_val), f'{fmt_num(ci_lo)} ~ {fmt_num(ci_hi)}'])
        if final_intercept_name in final_model.params.index:
            c_coef = float(final_model.params.at[final_intercept_name])
            c_se = float(final_model.bse.at[final_intercept_name])
            c_z = float(final_model.tvalues.at[final_intercept_name])
            c_wald = c_z ** 2
            c_p = float(final_model.pvalues.at[final_intercept_name])
            c_or = _safe_exp(c_coef)
            c_ci = final_model.conf_int().loc[final_intercept_name].values
            coef_rows.append(['(截距)', _fmt_b_sig(c_coef, c_p), fmt_num(c_se), fmt_num(c_z), fmt_num(c_wald), fmt_p(c_p), fmt_num(c_or), f'{fmt_num(_safe_exp(c_ci[0]))} ~ {fmt_num(_safe_exp(c_ci[1]))}'])
        parts.append(md_table(coef_headers, coef_rows, coef_alignments))
        parts.append(f"\n\nMcFadden R² = {fmt_num(r2['mcfadden'])}, Cox & Snell R² = {fmt_num(r2['cox_snell'])}, Nagelkerke R² = {fmt_num(r2['nagelkerke'])}, N = {n_samples}")
        parts.append('\n\n**备注：** 因变量 = {dependent}。\n\n**显著性：** \\* p<0.05，\\*\\* p<0.01。'.format(dependent=dep_display))
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def ordinal(df, outcome, predictors):
    import sys
    import numpy as np
    import pandas as pd
    from scipy import stats
    from statsmodels.discrete.discrete_model import Logit
    from statsmodels.miscmodels.ordinal_model import OrderedModel
    _state = {'df': df, 'matched_dependent': outcome, 'matched_independent': dict.fromkeys(predictors), 'category_mapping': {}, 'category_labels': {}, 'ordered_categories': [], 'warnings': []}
    _state['matched_independent'] = {c: c for c in predictors}

    def _validate_ordinal_y(y_raw):
        clean_y, _notice_clean_y = _am_drop_na(y_raw)
        if _notice_clean_y:
            _state['warnings'].append(_notice_clean_y)
        if len(clean_y) < 10:
            raise ValueError('有效样本量不足，有序逻辑回归至少需要 10 个样本')
        if len(clean_y) < 30:
            _state['warnings'].append('样本量较少（{samples} 个），建议不少于 30 个以获得更可靠的结果'.format(samples=len(clean_y)))
        unique_values = sorted(clean_y.unique())
        if len(unique_values) < 3:
            raise ValueError(f'有序逻辑回归需要至少 3 个类别，当前只有 {len(unique_values)} 个: {unique_values}')
        if len(unique_values) > 10:
            _state['warnings'].append('因变量有 {categories} 个类别，类别过多可能影响模型稳定性'.format(categories=len(unique_values)))
        value_counts = clean_y.value_counts()
        min_count = value_counts.min()
        if min_count < 2:
            _state['warnings'].append('某些类别的样本量过少（最少 {minimum} 个），可能影响模型稳定性'.format(minimum=min_count))
        elif min_count < 5:
            _state['warnings'].append('某些类别的样本量较少（最少 {minimum} 个），建议每个类别至少 5 个'.format(minimum=min_count))
        _state['ordered_categories'] = unique_values
        _state['category_mapping'] = {val: idx for idx, val in enumerate(unique_values)}
        dep_col = _state['matched_dependent']
        for val in unique_values:
            _state['category_labels'][val] = value_display(df, dep_col, val)
        encoded_y = clean_y.map(_state['category_mapping'])
        if encoded_y.isnull().any():
            valid_mask = ~encoded_y.isnull()
            encoded_y = encoded_y[valid_mask]
            if len(encoded_y) < 10:
                raise ValueError(f'编码后有效样本量不足（{len(encoded_y)} 个）')
        original_is_zero_based = unique_values == list(range(len(unique_values)))
        if not original_is_zero_based:
            dep_display = variable_display(df, dep_col)
            encoding_details = [f"{_state['category_labels'].get(orig, orig)} -> {_state['category_mapping'][orig]}" for orig in unique_values]
            _state['warnings'].append("因变量 '{variable}' 已编码为 0-{maximum}: {encoding}".format(variable=dep_display, maximum=len(unique_values) - 1, encoding='; '.join(encoding_details)))
        category_order_str = ' < '.join([str(_state['category_labels'][cat]) for cat in _state['ordered_categories']])
        _state['warnings'].append('有序类别设定: {order}'.format(order=category_order_str))
        return encoded_y

    def _encode_categorical_x(data):
        x_cols = list(_state['matched_independent'].values())
        for col in x_cols:
            numeric_series = pd.to_numeric(data[col], errors='coerce')
            is_categorical = data[col].dtype == 'object' or data[col].dtype.name == 'category' or numeric_series.isnull().sum() > len(data) * 0.5
            if is_categorical:
                non_null, _notice_non_null = _am_drop_na(data[col])
                if _notice_non_null:
                    _state['warnings'].append(_notice_non_null)
                if len(non_null) == 0:
                    raise ValueError(f"自变量 '{col}' 全部为空值")
                unique_vals = sorted(non_null.unique().astype(str))
                encoding_map = {val: i + 1 for i, val in enumerate(unique_vals)}
                data[col] = data[col].astype(str).map(encoding_map)
                display = variable_display(df, col)
                encoding_desc = '; '.join((f'{k} -> {v}' for k, v in list(encoding_map.items())[:5]))
                if len(encoding_map) > 5:
                    encoding_desc += '...'
                msg = "自变量 '{variable}' 为分类变量，已自动编码: {encoding}".format(variable=display, encoding=encoding_desc)
                print(f'[info] {msg}', file=sys.stderr)
                _state['warnings'].append(msg)
                _state['warnings'].append("注意：'{variable}' 已使用顺序编码（1,2,3...），若为名义变量（无序分类），建议改用哑变量编码以避免引入虚假排序关系。".format(variable=display))
            else:
                data[col] = numeric_series
        return data

    def _valid_covariance(fitted):
        covariance = fitted.cov_params()
        if isinstance(covariance, pd.DataFrame) and (not covariance.index.equals(fitted.params.index) or not covariance.columns.equals(fitted.params.index)):
            return False
        cov = np.asarray(covariance, dtype=float)
        n_params = len(fitted.params)
        if cov.shape != (n_params, n_params) or not np.all(np.isfinite(cov)):
            return False
        scale = max(float(np.linalg.norm(cov, ord=2)), np.finfo(float).tiny)
        if not np.isfinite(scale):
            return False
        if np.max(np.abs(cov - cov.T)) > 1e-08 * scale:
            return False
        symmetric_cov = (cov + cov.T) / 2
        if np.any(np.diag(symmetric_cov) <= 0):
            return False
        return bool(np.linalg.eigvalsh(symmetric_cov)[0] >= -1000 * np.finfo(float).eps * scale)

    def _fit_converged_model(y, X):
        failures = []
        for method in ('bfgs', 'lbfgs'):
            try:
                fitted = OrderedModel(y, X, distr='logit').fit(disp=0, method=method, maxiter=1000, warn_convergence=False)
                if not bool(fitted.mle_retvals.get('converged')):
                    failures.append(f'{method}: 未收敛')
                    continue
                if not (np.isfinite(fitted.llf) and np.all(np.isfinite(fitted.params)) and np.all(np.isfinite(fitted.bse)) and np.all(np.isfinite(fitted.pvalues)) and _valid_covariance(fitted)):
                    failures.append(f'{method}: 系数或标准误无效')
                    continue
                return fitted
            except Exception as exc:
                failures.append(f'{method}: {type(exc).__name__}')
        raise ValueError('模型未收敛或无法计算可靠标准误（' + '; '.join(failures) + '）。本次不输出系数、p 值、OR 或置信区间。先核对类别样本量、自变量的单位/极端值、重复或高度相关变量及稀疏类别；排除数据或模型问题后，重新检查模型设定再运行。不要为了得到显著结果而删样本或换变量。')

    def _select_variables(X, y):
        return list(X.columns)

    def _pseudo_r_squared(null_ll, final_ll, n):
        try:
            if np.isinf(null_ll) or np.isinf(final_ll):
                return {'mcfadden': 0.0, 'cox_snell': 0.0, 'nagelkerke': 0.0}
            if final_ll <= null_ll:
                return {'mcfadden': 0.0, 'cox_snell': 0.0, 'nagelkerke': 0.0}
            mcfadden = 1 - final_ll / null_ll
            cox_snell = 1 - np.exp(-2 * (final_ll - null_ll) / n)
            max_cs = 1 - np.exp(2 * null_ll / n)
            nagelkerke = cox_snell / max_cs if max_cs > 0 else 0.0
            mcfadden = max(0.0, min(1.0, mcfadden))
            cox_snell = max(0.0, min(1.0, cox_snell))
            nagelkerke = max(0.0, min(1.0, nagelkerke))
            return {'mcfadden': mcfadden, 'cox_snell': cox_snell, 'nagelkerke': nagelkerke}
        except Exception as e:
            print(f"[warning] {'伪R2计算失败: {error}'.format(error=e)}", file=sys.stderr)
            return {'mcfadden': 0.0, 'cox_snell': 0.0, 'nagelkerke': 0.0}

    def _parallel_lines_test(y, X, selected_vars):
        result = {'available': False, 'method': '近似 Brant-Wald（各阈值独立二元 Logit）', 'reason': ''}
        if len(selected_vars) == 0:
            result['reason'] = '最终模型没有自变量，无法检验斜率是否跨阈值相等'
            return result
        categories = sorted(pd.unique(y.dropna()))
        if len(categories) < 3:
            result['reason'] = '有序因变量少于 3 个类别'
            return result
        design = X[selected_vars].astype(float)
        design = design.assign(_intercept_=1.0)
        design = design[['_intercept_'] + selected_vars]
        slopes = []
        covariances = []
        threshold_info = []
        for cut in categories[:-1]:
            y_bin = (y > cut).astype(int)
            threshold_info.append({'cut': cut, 'n_lower': int((y_bin == 0).sum()), 'n_upper': int((y_bin == 1).sum())})
            if y_bin.nunique() < 2:
                result['reason'] = f'阈值 {cut} 两侧没有同时出现有效类别'
                return result
            try:
                fit = Logit(y_bin, design).fit(disp=0, maxiter=200)
                slopes.append(fit.params.loc[selected_vars].to_numpy(float))
                covariances.append(fit.cov_params().loc[selected_vars, selected_vars].to_numpy(float))
            except Exception as exc:
                result['reason'] = f'阈值 {cut} 的二元 Logit 拟合失败: {exc}'
                return result
        if len(slopes) < 2:
            result['reason'] = '可比较的阈值少于 2 个'
            return result
        beta = np.asarray(slopes)
        p = beta.shape[1]
        differences = (beta[1:] - beta[0]).reshape(-1)
        blocks = []
        for idx in range(1, len(covariances)):
            row = []
            for jdx in range(1, len(covariances)):
                block = covariances[0].copy()
                if idx == jdx:
                    block = block + covariances[idx]
                row.append(block)
            blocks.append(row)
        covariance = np.block(blocks)
        if not np.all(np.isfinite(covariance)) or not np.all(np.isfinite(differences)):
            result['reason'] = '拟合结果包含非有限系数或协方差'
            return result
        try:
            statistic = float(differences @ np.linalg.pinv(covariance) @ differences)
            df = int(p * (len(slopes) - 1))
            p_value = float(stats.chi2.sf(max(0.0, statistic), df))
        except Exception as exc:
            result['reason'] = f'平行线检验计算失败: {exc}'
            return result
        result.update({'available': True, 'statistic': statistic, 'df': df, 'p_value': p_value, 'thresholds': threshold_info, 'n_thresholds': len(slopes), 'conclusion': '未发现显著偏离（p > 0.05）' if p_value > 0.05 else '发现可能的平行线假设偏离（p ≤ 0.05）'})
        return result

    def _analyze_and_format():
        if not _state['matched_dependent']:
            return '错误：因变量未匹配。'
        y_col = _state['matched_dependent']
        x_cols = list(_state['matched_independent'].values())
        dup_cols = _am_duplicates([y_col] + x_cols)
        if dup_cols:
            return '错误：因变量/自变量中有多个被解析到同一实际列（' + '、'.join(dup_cols) + '），请检查变量名是否重复或存在拼写/标点差异导致被合并为同一列。'
        data = _state['df'][[y_col] + x_cols].copy()
        data = _encode_categorical_x(data)
        original_count = len(data)
        data, _notice_data = _am_drop_na(data)
        if _notice_data:
            _state['warnings'].append(_notice_data)
        final_count = len(data)
        if original_count != final_count:
            _state['warnings'].append('数据清理：移除了 {rows} 行包含缺失值的数据'.format(rows=original_count - final_count))
        if final_count < 20:
            return f'错误：有效数据量不足 20 行（当前 {final_count} 行），无法进行可靠的有序逻辑回归分析。'
        try:
            y = _validate_ordinal_y(data[y_col])
        except ValueError as e:
            return f'错误：{e}'
        data = data.loc[y.index]
        X = data[x_cols].copy()
        for col in x_cols:
            if not pd.api.types.is_numeric_dtype(X[col]):
                X[col] = pd.to_numeric(X[col], errors='coerce')
        combined, _notice_combined = _am_drop_na(pd.concat([X, y], axis=1))
        if _notice_combined:
            _state['warnings'].append(_notice_combined)
        X = combined[x_cols]
        y = combined[y_col]
        n_samples = len(combined)
        if n_samples < 20:
            return f'错误：有效样本量不足 20（当前 {n_samples}），无法进行可靠的有序逻辑回归分析。'
        try:
            selected_vars = _select_variables(X, y)
        except ValueError as exc:
            return f'错误：有序逻辑回归变量选择失败: {exc}'
        method_cn = '全进入法'
        if not selected_vars:
            _state['warnings'].append('所有变量均不显著，最终模型仅包含截距项')
        counts = y.value_counts().to_numpy(dtype=float)
        null_ll = float(np.sum(counts * np.log(counts / len(y))))

        if selected_vars:
            try:
                final_model = _fit_converged_model(y, X[selected_vars])
            except ValueError as exc:
                msg = f'有序逻辑回归模型拟合失败: {exc}'
                print(f'[error] {msg}', file=sys.stderr)
                return f'错误：{msg}'
        else:
            final_model = None
        ll_null = null_ll
        ll_final = float(final_model.llf) if selected_vars else null_ll
        chi2 = float(max(0, -2 * (ll_null - ll_final))) if not (np.isinf(ll_null) or np.isinf(ll_final)) else 0.0
        df_model = len(selected_vars)
        if df_model > 0 and chi2 > 0:
            try:
                chi2_p = float(1 - stats.chi2.cdf(chi2, df_model))
            except Exception:
                chi2_p = 1.0
        else:
            chi2_p = 1.0
        r2 = _pseudo_r_squared(ll_null, ll_final, n_samples)
        if r2['cox_snell'] > 0.99 or r2['nagelkerke'] > 0.99:
            _state['warnings'].append('伪 R2 值异常高（接近 1.0），可能存在完全分离问题或样本量过少')
        if hasattr(final_model, 'bse') and len(selected_vars) > 0:
            max_se = final_model.bse.max()
            if max_se > 10:
                _state['warnings'].append('检测到过大的标准误（最大 = {maximum}），可能存在完全分离或多重共线性问题'.format(maximum=f'{max_se:.2f}'))
        aic = float(getattr(final_model, 'aic', np.inf))
        bic = float(getattr(final_model, 'bic', np.inf))
        dep_display = variable_display(df, y_col)
        n_categories = len(_state['ordered_categories'])
        parts = []
        parts.append('## 有序逻辑回归分析结果\n')
        parts.append('因变量: {dependent}（{categories} 个有序类别），分析方法: {method}，候选变量: {candidates} 个，最终保留: {retained} 个\n'.format(dependent=dep_display, categories=n_categories, method=method_cn, candidates=len(x_cols), retained=len(selected_vars)))
        if selected_vars:
            optimizer = str(final_model.mle_settings.get('optimizer', '')).upper()
            parts.append(f'估计状态：已收敛（{optimizer}；最大迭代次数 {1000}）。')
        parallel = _parallel_lines_test(y, X, selected_vars)
        parts.append('\n### 平行线（比例优势）检验')
        if parallel['available']:
            conclusion = str(parallel['conclusion'])
            parts.append(f"结论：{conclusion}；检验方法：{parallel['method']}。该检验用于提示假设风险，不会自动删除变量或否定系数估计。")
        else:
            parts.append('结论：无法计算；不会自动阻断模型。原因：' + str(True))
        parts.append('### 模型似然比检验\n')
        lrt_headers = ['模型', '-2倍对数似然值', '卡方值', 'df', 'p', 'AIC 值', 'BIC 值']
        lrt_rows = [['仅截距', fmt_num(-2 * ll_null) if not np.isinf(ll_null) else '-', '-', '-', '-', '-', '-'], ['最终模型', fmt_num(-2 * ll_final) if not np.isinf(ll_final) else '-', fmt_num(chi2), str(df_model), fmt_p(chi2_p) if df_model > 0 else '-', fmt_num(aic) if not np.isinf(aic) else '-', fmt_num(bic) if not np.isinf(bic) else '-']]
        parts.append(md_table(lrt_headers, lrt_rows, ['l', 'r', 'r', 'c', 'c', 'r', 'r']))
        if selected_vars and hasattr(final_model, 'params'):
            parts.append('\n### 回归系数\n')

            def _fmt_b_sig(b_val, p_val):
                b_str = fmt_num(b_val)
                if p_val < 0.001:
                    return f'{b_str}\\*\\*\\*'
                if p_val < 0.01:
                    return f'{b_str}\\*\\*'
                if p_val < 0.05:
                    return f'{b_str}\\*'
                return b_str
            coef_headers = ['变量', '回归系数', '标准误', 'z 值', 'Wald χ²', 'p 值', 'OR值', 'OR值95% CI']
            coef_alignments = ['l', 'r', 'r', 'r', 'r', 'c', 'r', 'c']
            coef_rows = []
            params = final_model.params
            bse = final_model.bse
            tvalues = final_model.tvalues
            pvalues = final_model.pvalues
            conf_int = final_model.conf_int()
            for var in selected_vars:
                if var in params.index:
                    coef = float(params[var])
                    se = float(bse[var])
                    z_val = float(tvalues[var])
                    wald = z_val ** 2
                    p_val = float(pvalues[var])
                    or_val = float(np.exp(coef))
                    ci = conf_int.loc[var].values
                    ci_lo = float(np.exp(ci[0]))
                    ci_hi = float(np.exp(ci[1]))
                    var_display = variable_display(df, var)
                    coef_rows.append([var_display, _fmt_b_sig(coef, p_val), fmt_num(se), fmt_num(z_val), fmt_num(wald), fmt_p(p_val), fmt_num(or_val), f'{fmt_num(ci_lo)} ~ {fmt_num(ci_hi)}'])
            thr_idx = [i for i in params.index if i not in selected_vars and i != '_null_']
            try:
                cov_mat = final_model.cov_params()
            except Exception:
                cov_mat = None
            thr_values = {}
            thr_ses = {}
            running = 0.0
            for order, idx in enumerate(thr_idx):
                raw = float(params[idx])
                if order == 0:
                    running = raw
                    thr_values[idx] = running
                    thr_ses[idx] = float(bse[idx])
                else:
                    e = float(np.exp(raw))
                    running = running + e
                    thr_values[idx] = running
                    se_val = float(bse[idx])
                    if cov_mat is not None:
                        try:
                            gradient = np.zeros(len(thr_idx), dtype=float)
                            gradient[0] = 1.0
                            gradient[1:order + 1] = np.exp(params.loc[thr_idx[1:order + 1]].to_numpy(dtype=float))
                            covariance = cov_mat.loc[thr_idx, thr_idx].to_numpy(dtype=float)
                            var_thr = float(gradient @ covariance @ gradient)
                            if var_thr > 0:
                                se_val = float(np.sqrt(var_thr))
                        except Exception:
                            _state['warnings'].append(f'阈值 {idx} 的标准误无法用 delta 法还原，展示的是内部参数化下的原始标准误，请谨慎解读。')
                    thr_ses[idx] = se_val
            for idx in params.index:
                if idx not in selected_vars and idx != '_null_':
                    coef = thr_values.get(idx, float(params[idx]))
                    se = thr_ses.get(idx, float(bse[idx]))
                    z_val = coef / se if se > 0 else 0.0
                    wald = z_val ** 2
                    p_val = float(2 * stats.norm.sf(abs(z_val)))
                    or_val = float(np.exp(coef))
                    ci_lo = float(np.exp(coef - 1.96 * se))
                    ci_hi = float(np.exp(coef + 1.96 * se))
                    coef_rows.append(['阈值 {threshold}'.format(threshold=idx), _fmt_b_sig(coef, p_val), fmt_num(se), fmt_num(z_val), fmt_num(wald), fmt_p(p_val), fmt_num(or_val), f'{fmt_num(ci_lo)} ~ {fmt_num(ci_hi)}'])
            parts.append(md_table(coef_headers, coef_rows, coef_alignments))
            parts.append(f"\n\nMcFadden R² = {fmt_num(r2['mcfadden'])}, Cox & Snell R² = {fmt_num(r2['cox_snell'])}, Nagelkerke R² = {fmt_num(r2['nagelkerke'])}, N = {n_samples}")
            parts.append('\n\n\\* p<0.05 \\*\\* p<0.01 \\*\\*\\* p<0.001')
        removed_vars = [v for v in x_cols if v not in selected_vars]
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def reliability(df, names):
    import sys
    import pandas as pd
    _state = {'df': df, 'matched_dimensions': {'总量表': dict.fromkeys(names)}, 'warnings': []}
    _state['matched_dimensions']['总量表'] = {c: c for c in names}

    def _calculate_cronbach_alpha(df_items):
        k = df_items.shape[1]
        if k < 2:
            return float('nan')
        item_variances = df_items.var(axis=0, ddof=1)
        total_variance = df_items.sum(axis=1).var(ddof=1)
        if total_variance == 0:
            return float('nan')
        alpha = k / (k - 1) * (1 - item_variances.sum() / total_variance)
        return float(alpha)

    def _warn_if_listwise_shrinks(dim_name, before, after):
        if before > 0 and after * 2 < before:
            _state['warnings'].append("维度 '{dimension}' 整行剔除后仅剩 {after} 例（原 {before} 例），α 在小样本下极不稳定（甚至为负）。当前公开入口采用整行删除；请先核对缺失值的定义是否经过用户确认（例如是否把「0=不清楚」等有效选项当成了缺失）。".format(dimension=dim_name, after=after, before=before))

    def _analyze_and_format():
        if not _state['matched_dimensions']:
            return '没有有效的维度进行信度分析。请确认 --columns 中的题项名称能匹配数据列。'
        dim_results = {}
        all_dimension_data = {}
        for dim_name, matched_items in _state['matched_dimensions'].items():
            if len(matched_items) < 2:
                _state['warnings'].append("维度 '{dimension}' 的题项少于 2 个，跳过信度分析".format(dimension=dim_name))
                continue
            numeric_data = {}
            for req_item, actual_col in matched_items.items():
                try:
                    series = pd.to_numeric(_state['df'][actual_col], errors='coerce')
                    if series.isnull().all():
                        _state['warnings'].append("维度 '{dimension}' 中题项 '{item}' 无法转换为数值型，跳过".format(dimension=dim_name, item=actual_col))
                        continue
                    numeric_data[req_item] = series
                except Exception as e:
                    msg = "处理列 '{column}' 时发生错误: {error}".format(column=actual_col, error=e)
                    print(f'[warning] {msg}', file=sys.stderr)
                    _state['warnings'].append(msg)
            if len(numeric_data) < 2:
                _state['warnings'].append("维度 '{dimension}' 有效题项少于 2 个，跳过信度分析".format(dimension=dim_name))
                continue
            raw_items = pd.DataFrame(numeric_data)
            df_items, _notice_df_items = _am_drop_na(raw_items)
            if _notice_df_items:
                _state['warnings'].append(_notice_df_items)
            _warn_if_listwise_shrinks(dim_name, len(raw_items), len(df_items))
            if len(df_items) < 3:
                _state['warnings'].append("维度 '{dimension}' 有效数据不足 3 行，跳过信度分析".format(dimension=dim_name))
                continue
            all_dimension_data[dim_name] = df_items
            alpha = _calculate_cronbach_alpha(df_items)
            total_score = df_items.sum(axis=1)
            item_stats = []
            for col in df_items.columns:
                actual_col = matched_items[col]
                display_name = variable_display(df, actual_col)
                corrected_total = total_score - df_items[col]
                if len(corrected_total.unique()) > 1:
                    item_total_corr = float(df_items[col].corr(corrected_total))
                else:
                    item_total_corr = float('nan')
                temp_df = df_items.drop(columns=[col])
                if temp_df.shape[1] > 1:
                    alpha_if_deleted = _calculate_cronbach_alpha(temp_df)
                else:
                    alpha_if_deleted = float('nan')
                item_stats.append({'display': display_name, 'mean': float(df_items[col].mean()), 'std': float(df_items[col].std()), 'item_total_corr': item_total_corr, 'alpha_if_deleted': alpha_if_deleted, 'n': len(df_items)})
            dim_results[dim_name] = {'alpha': alpha, 'item_count': len(df_items.columns), 'sample_size': len(df_items), 'item_stats': item_stats}
        if not dim_results:
            return '没有维度能够进行有效的信度分析。请检查题项是否为数值编码；如果数据中是文本选项，需要先转换为数值编码后再做 Cronbach α。'
        total_alpha = None
        total_n = 0
        total_item_count = 0
        if len(dim_results) > 1 and all_dimension_data:
            try:
                combined = {}
                for d_name, df_dim in all_dimension_data.items():
                    for c in df_dim.columns:
                        combined[f'{d_name}_{c}'] = df_dim[c]
                if combined:
                    total_df, _notice_total_df = _am_drop_na(pd.DataFrame(combined))
                    if _notice_total_df:
                        _state['warnings'].append(_notice_total_df)
                    if len(total_df) >= 3 and total_df.shape[1] >= 2:
                        total_alpha = _calculate_cronbach_alpha(total_df)
                        total_n = len(total_df)
                        total_item_count = total_df.shape[1]
            except Exception as e:
                msg = '计算总量表信度时发生错误: {error}'.format(error=e)
                print(f'[warning] {msg}', file=sys.stderr)
                _state['warnings'].append(msg)
        out = _format_simple(dim_results, total_alpha, total_n, total_item_count)
        return out

    def _format_simple(dim_results, total_alpha, total_n, total_item_count):
        headers = ['维度', '项数', '样本量', 'Cronbach α系数']
        rows = []
        for dim_name, res in dim_results.items():
            rows.append([dim_name, str(res['item_count']), str(res['sample_size']), fmt_num(res['alpha'])])
        if total_alpha is not None:
            rows.append(['**总量表**', str(total_item_count), str(total_n), fmt_num(total_alpha)])
        parts = ['## 信度分析结果\n', md_table(headers, rows, ['l', 'c', 'c', 'c'])]
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def pca(df, names, n_factors=None):
    import sys
    import numpy as np
    import pandas as pd
    _state = {'df': df, 'matched_columns': dict.fromkeys(names), 'n_components': n_factors, 'warnings': []}
    _state['matched_columns'] = {c: c for c in names}

    def _analyze_and_format():
        if len(_state['matched_columns']) < 2:
            return '错误：主成分分析至少需要 2 个变量。'
        numeric_data = {}
        var_display_names = {}
        for req_col, actual_col in _state['matched_columns'].items():
            series = pd.to_numeric(_state['df'][actual_col], errors='coerce')
            if series.isnull().all():
                _state['warnings'].append("列 '{column}' 无法转换为数值型，已跳过".format(column=actual_col))
                continue
            display_name = variable_display(df, actual_col)
            numeric_data[actual_col] = series
            var_display_names[actual_col] = display_name
        if len(numeric_data) < 2:
            return '错误：至少需要 2 个有效的数值型变量进行主成分分析。'
        df_items, _notice_df_items = _am_drop_na(pd.DataFrame(numeric_data))
        if _notice_df_items:
            _state['warnings'].append(_notice_df_items)
        if len(df_items) < 10:
            return '错误：有效数据不足 10 行，无法进行主成分分析。'
        n_vars = len(df_items.columns)
        n_samples = len(df_items)
        kmo_val = None
        bartlett_chi = None
        bartlett_df = int(n_vars * (n_vars - 1) / 2)
        bartlett_p = None
        kmo_all = None
        try:
            from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
            kmo_all, kmo_val = calculate_kmo(df_items)
            kmo_val = float(kmo_val)
            bartlett_chi, bartlett_p = calculate_bartlett_sphericity(df_items)
            bartlett_chi = float(bartlett_chi)
            bartlett_p = float(bartlett_p)
            if kmo_val < 0.5:
                _state['warnings'].append('KMO = {value} < 0.5：数据对主成分分析的适合度较低；结果仍输出，请谨慎解读。'.format(value=fmt_num(kmo_val)))
            if bartlett_p > 0.05:
                _state['warnings'].append('Bartlett 球形度检验不显著（p = {p} > 0.05）：变量相关性证据不足；结果仍输出，请谨慎解读。'.format(p=fmt_p(bartlett_p)))
        except ImportError:
            msg = 'factor_analyzer 未安装，KMO 检验已跳过。安装: pip install factor_analyzer'
            print(f'[warning] {msg}', file=sys.stderr)
            _state['warnings'].append(msg)
            try:
                from scipy import stats as sp_stats
                corr_matrix = df_items.corr()
                det = np.linalg.det(corr_matrix.values)
                if det > 0:
                    bartlett_chi = -(n_samples - 1 - (2 * n_vars + 5) / 6) * np.log(det)
                    bartlett_p = float(sp_stats.chi2.sf(bartlett_chi, bartlett_df))
                    if bartlett_p > 0.05:
                        _state['warnings'].append('Bartlett 球形度检验不显著（p = {p} > 0.05）：变量相关性证据不足；结果仍输出，请谨慎解读。'.format(p=fmt_p(bartlett_p)))
                else:
                    msg_det = '相关矩阵接近奇异（行列式 <= 0），Bartlett 检验无法计算'
                    print(f'[warning] {msg_det}', file=sys.stderr)
                    _state['warnings'].append(msg_det)
            except Exception as e:
                msg_b = 'Bartlett 降级计算也失败: {error}'.format(error=e)
                print(f'[warning] {msg_b}', file=sys.stderr)
                _state['warnings'].append(msg_b)
        except Exception as e:
            msg = 'KMO/Bartlett 计算失败: {error}'.format(error=e)
            print(f'[warning] {msg}', file=sys.stderr)
            _state['warnings'].append(msg)
        corr_matrix = df_items.corr()
        eigenvalues_raw, eigenvectors_raw = np.linalg.eigh(corr_matrix.values)
        order = np.argsort(eigenvalues_raw)[::-1]
        eigenvalues = eigenvalues_raw[order]
        eigenvectors = eigenvectors_raw[:, order]
        for j in range(eigenvectors.shape[1]):
            if np.sum(eigenvectors[:, j]) < 0:
                eigenvectors[:, j] *= -1
        variance_ratio = eigenvalues / n_vars * 100
        cumulative_ratio = np.cumsum(variance_ratio)
        if _state['n_components'] is None:
            n_keep = int(np.sum(eigenvalues > 1))
            if n_keep == 0:
                n_keep = 1
                _state['warnings'].append('没有特征根大于 1 的成分，默认保留 1 个主成分')
        else:
            n_keep = min(_state['n_components'], n_vars)
        loadings = eigenvectors[:, :n_keep] * np.sqrt(eigenvalues[:n_keep])
        communalities = np.sum(loadings ** 2, axis=1)
        parts = []
        parts.append('## 主成分分析结果\n')
        if kmo_val is not None or bartlett_chi is not None:
            parts.append('### KMO 和 Bartlett 球形度检验\n')
            kmo_headers = ['KMO值', 'Bartlett近似卡方', 'df', 'p']
            kmo_rows = [[fmt_num(kmo_val) if kmo_val is not None else '-', fmt_num(bartlett_chi, 3) if bartlett_chi is not None else '-', str(bartlett_df) if bartlett_chi is not None else '-', fmt_p(bartlett_p) if bartlett_p is not None else '-']]
            parts.append(md_table(kmo_headers, kmo_rows, ['c', 'c', 'c', 'c']))
            if kmo_val is not None:
                if kmo_val >= 0.9:
                    kmo_eval = '非常好'
                elif kmo_val >= 0.8:
                    kmo_eval = '适合'
                elif kmo_val >= 0.7:
                    kmo_eval = '比较适合'
                elif kmo_val >= 0.6:
                    kmo_eval = '可以接受'
                else:
                    kmo_eval = '不适合做主成分分析'
                parts.append('\n注：KMO = {value}（{evaluation}）；* p<0.05，** p<0.01。'.format(value=fmt_num(kmo_val), evaluation=kmo_eval))
        parts.append('\n### 方差解释率表\n')
        var_headers = ['主成分', '特征根', '方差解释率%', '累积方差解释率%', '是否提取']
        var_alignments = ['c', 'c', 'c', 'c', 'c']
        var_rows = []
        for i in range(n_vars):
            var_rows.append(['主成分{number}'.format(number=i + 1), fmt_num(float(eigenvalues[i])), fmt_num(float(variance_ratio[i]), 2), fmt_num(float(cumulative_ratio[i]), 2), '是' if i < n_keep else '否'])
        parts.append(md_table(var_headers, var_rows, var_alignments))
        extraction_rule = '按特征根 > 1 原则' if _state['n_components'] is None else '按用户指定成分数'
        parts.append('\n{rule}，提取 {count} 个主成分，累积解释 {variance}% 的方差。'.format(rule=extraction_rule, count=n_keep, variance=fmt_num(float(cumulative_ratio[n_keep - 1]), 2)))
        parts.append('\n### 主成分载荷与共同度表\n')
        load_headers = ['变量']
        for j in range(n_keep):
            load_headers.append('主成分{number}载荷'.format(number=j + 1))
        load_headers.append('共同度')
        load_alignments = ['l'] + ['c'] * (n_keep + 1)
        load_rows = []
        for i, col in enumerate(df_items.columns):
            display = var_display_names.get(col, col)
            row = [display]
            for j in range(n_keep):
                val = float(loadings[i, j])
                row.append(fmt_num(val))
            row.append(fmt_num(float(communalities[i])))
            load_rows.append(row)
        parts.append(md_table(load_headers, load_rows, load_alignments))
        parts.append('\n注：载荷绝对值 > 0.4 通常认为变量与该主成分存在较强对应关系；共同度为提取主成分解释该变量方差的比例。')
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def cluster(df, names, k):
    import sys
    import numpy as np
    import pandas as pd
    from scipy import stats as sp_stats
    _state = {'df': df, 'matched_columns': dict.fromkeys(names), 'n_clusters': k, 'warnings': []}
    _state['matched_columns'] = {c: c for c in names}

    def _prepare_data():
        needed = list(_state['matched_columns'].values())
        data = _state['df'][needed].copy()
        for col in needed:
            original = data[col]
            numeric = pd.to_numeric(original, errors='coerce')
            if numeric.isna().sum() > len(data) * 0.5:
                non_null, _notice_non_null = _am_drop_na(original)
                if _notice_non_null:
                    _state['warnings'].append(_notice_non_null)
                if len(non_null) == 0:
                    display = variable_display(df, col)
                    _state['warnings'].append(f"变量 '{display}' 全部为空值，无法参与聚类")
                    continue
                if non_null.dtype == object:
                    unique_vals = sorted(non_null.unique())
                    mapping = {v: i + 1 for i, v in enumerate(unique_vals)}
                    data[col] = original.map(mapping)
                    display = variable_display(df, col)
                    detail = '; '.join((f'{k} -> {v}' for k, v in mapping.items()))
                    _state['warnings'].append("变量 '{variable}' 为分类变量，已自动编码: {detail}".format(variable=display, detail=detail))
                else:
                    data[col] = numeric
            else:
                data[col] = numeric
        before = len(data)
        data, _notice_data = _am_drop_na(data)
        if _notice_data:
            _state['warnings'].append(_notice_data)
        after = len(data)
        if before != after:
            _state['warnings'].append('已移除 {count} 行含缺失值的数据'.format(count=before - after))
        min_required = max(_state['n_clusters'] * 2, 10)
        if after < min_required:
            raise ValueError(f'有效数据量不足（{after} 行），聚类分析至少需要 {min_required} 行')
        for col in needed:
            if col in data.columns and data[col].std() == 0:
                display = variable_display(df, col)
                raise ValueError(f"变量 '{display}' 无变异（所有值相同），无法聚类")
        return data

    def _analyze_and_format():
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            print('聚类分析需要 scikit-learn: pip install scikit-learn', file=sys.stderr)
            raise ImportError('缺少 scikit-learn，请执行: pip install scikit-learn')
        data = _prepare_data()
        needed = list(_state['matched_columns'].values())
        scaler = StandardScaler()
        scaled = scaler.fit_transform(data[needed])
        kmeans = KMeans(n_clusters=_state['n_clusters'], random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled)
        cluster_counts = pd.Series(labels).value_counts().sort_index()
        lang = 'zh'
        parts = []
        summary_headers = ['聚类类别', '频数', '百分比（%）']
        summary_rows = []
        total = len(labels)
        for i in range(_state['n_clusters']):
            cnt = int(cluster_counts.get(i, 0))
            pct = cnt / total * 100
            summary_rows.append([f'cluster_{i + 1}', str(cnt), f'{pct:.2f}%'])
        summary_rows.append(['合计', str(total), '100.00%'])
        anova_headers, anova_rows = _build_anova_table(data, labels, needed, cluster_counts)
        parts.append('## K-Means 聚类分析结果\n')
        parts.append('聚类数 k={count}，算法: K-Means，数据已标准化（Z-score）\n'.format(count=_state['n_clusters']))
        parts.append('### 聚类类别基本情况汇总\n')
        parts.append(md_table(summary_headers, summary_rows, ['l', 'r', 'r']))
        parts.append('\n### 聚类类别方差分析差异对比结果\n')
        parts.append(md_table(anova_headers, anova_rows, ['l'] + ['c'] * _state['n_clusters'] + ['r', 'r']))
        parts.append('\n注：\\* p<0.05 \\*\\* p<0.01')
        return '\n'.join(parts)

    def _build_anova_table(data, labels, needed, cluster_counts):
        anova_headers = [''] + [f'cluster_{i + 1}(n={int(cluster_counts.get(i, 0))})' for i in range(_state['n_clusters'])] + ['F', 'p']
        anova_rows = []
        for col in needed:
            display = variable_display(df, col)
            groups = [data.loc[labels == i, col].values for i in range(_state['n_clusters'])]
            row = [display]
            for g in groups:
                if len(g) > 0:
                    row.append(f'{np.mean(g):.3f}±{np.std(g, ddof=1):.3f}')
                else:
                    row.append('-')
            valid_groups = [g for g in groups if len(g) > 1]
            if len(valid_groups) >= 2:
                try:
                    f_stat, p_val = sp_stats.f_oneway(*valid_groups)
                    row.append(fmt_num(f_stat))
                    row.append(fmt_p(p_val))
                except Exception as e:
                    warning = "变量 '{variable}' ANOVA 失败: {error}".format(variable=display, error=e)
                    print(f'[warning] {warning}', file=sys.stderr)
                    _state['warnings'].append(warning)
                    row.extend(['-', '-'])
            else:
                _state['warnings'].append("变量 '{variable}' 有效分组不足，跳过 ANOVA".format(variable=display))
                row.extend(['-', '-'])
            anova_rows.append(row)
        return (anova_headers, anova_rows)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def roc(df, outcome, score):
    import sys
    import numpy as np
    import pandas as pd
    from scipy import stats
    from sklearn.metrics import roc_auc_score, roc_curve
    _state = {'df': df, 'matched_dependent': outcome, 'matched_independent': {score: score}, 'independent_vars': [score], 'negative_label': None, 'positive_label': None, 'plot_data_list': [], 'warnings': []}

    def _calculate_auc_ci_se(y_true, y_score):
        auc = roc_auc_score(y_true, y_score)
        n1 = int(np.sum(y_true == 1))
        n2 = int(np.sum(y_true == 0))
        q1 = auc / (2 - auc)
        q2 = 2 * auc ** 2 / (1 + auc)
        numerator = auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2) + (n2 - 1) * (q2 - auc ** 2)
        denominator = n1 * n2
        se = float(np.sqrt(numerator / denominator))
        ci_lower = max(0.0, auc - 1.96 * se)
        ci_upper = min(1.0, auc + 1.96 * se)
        z_score = (auc - 0.5) / se
        p_value = float(2 * (1 - stats.norm.cdf(abs(z_score))))
        return (auc, se, ci_lower, ci_upper, p_value)

    def _analyze_and_format():
        required_cols = [_state['matched_dependent']] + list(_state['matched_independent'].values())
        data, _notice_data = _am_drop_na(_state['df'][required_cols])
        if _notice_data:
            _state['warnings'].append(_notice_data)
        data = data.copy()
        if len(data) < 10:
            raise ValueError('有效样本量过少 (<10)，无法进行 ROC 分析')
        y_col = data[_state['matched_dependent']]
        unique_vals = y_col.unique()
        if len(unique_vals) != 2:
            raise ValueError(f"因变量 '{_state['matched_dependent']}' 必须恰好包含 2 个类别，当前发现: {unique_vals}")
        sorted_unique = sorted(unique_vals)
        _state['negative_label'] = sorted_unique[0]
        _state['positive_label'] = sorted_unique[1]
        y_true = (y_col == _state['positive_label']).astype(int)
        n_pos = int(np.sum(y_true))
        n_neg = len(y_true) - n_pos
        predictors = _prepare_predictors(data, y_true)
        if not predictors:
            raise ValueError('没有有效的数值型预测变量')
        auc_results = []
        cutoff_results = []
        for name, y_score in predictors.items():
            try:
                fpr, tpr, thresholds = roc_curve(y_true, y_score)
                auc, se, ci_lower, ci_upper, p_value = _calculate_auc_ci_se(y_true.values, np.asarray(y_score))
                youden = tpr - fpr
                best_idx = int(np.argmax(youden))
                best_threshold = thresholds[best_idx]
                best_sens = tpr[best_idx]
                best_spec = 1 - fpr[best_idx]
                display_name = '联合诊断' if name == '联合诊断' else variable_display(df, _state['matched_independent'].get(name, name))
                auc_results.append({'variable': display_name, 'auc': auc, 'se': se, 'p_value': p_value, 'ci_lower': ci_lower, 'ci_upper': ci_upper})
                cutoff_results.append({'variable': display_name, 'auc': auc, 'best_threshold': best_threshold, 'sensitivity': best_sens, 'specificity': best_spec, 'youden': youden[best_idx]})
                plot_df = pd.DataFrame({'fpr': fpr, 'tpr': tpr})
                if len(plot_df) > 1000:
                    plot_df = plot_df.iloc[::max(1, len(plot_df) // 1000)]
                _state['plot_data_list'].append({'name': display_name, 'data': plot_df.to_dict(orient='list')})
            except Exception as e:
                print("[warning] 变量 '{variable}' ROC 分析失败: {error}".format(variable=name, error=e), file=sys.stderr)
                _state['warnings'].append("变量 '{variable}' 分析失败: {error}".format(variable=name, error=e))
        if not auc_results:
            raise ValueError('所有变量分析均失败')
        image_path = ''
        dep_display = variable_display(df, _state['matched_dependent'])
        pos_label = value_display(df, _state['matched_dependent'], _state['positive_label'])
        neg_label = value_display(df, _state['matched_dependent'], _state['negative_label'])
        parts = ['## ROC 曲线与诊断效能分析' + '\n']
        if image_path:
            parts.append('![ROC曲线]({path})'.format(path=image_path) + '\n')
        freq_headers = ['因变量: {variable}'.format(variable=dep_display), '频数', '百分比(%)']
        freq_rows = [['阳性 ({label})'.format(label=pos_label), str(n_pos), f'{n_pos / len(y_true):.2%}'], ['阴性 ({label})'.format(label=neg_label), str(n_neg), f'{n_neg / len(y_true):.2%}'], ['**总计**', f'**{len(y_true)}**', '**100%**']]
        parts.append('### 因变量频数分布' + '\n')
        parts.append(md_table(freq_headers, freq_rows, ['l', 'r', 'r']))
        auc_headers = ['变量', 'AUC', '标准误(S.E.)', 'p值', '95% CI']
        auc_rows = []
        for r in auc_results:
            auc_rows.append([r['variable'], fmt_num(r['auc']), fmt_num(r['se']), fmt_p(r['p_value']), f"{r['ci_lower']:.3f} ~ {r['ci_upper']:.3f}"])
        parts.append('\n' + '### ROC 结果 AUC 汇总' + '\n')
        parts.append(md_table(auc_headers, auc_rows, ['l', 'r', 'r', 'r', 'c']))
        cut_headers = ['变量', 'AUC', '最佳界值', '敏感度', '特异度', '约登指数']
        cut_rows = []
        for r in cutoff_results:
            threshold_val = r['best_threshold']
            threshold_str = 'Inf' if np.isinf(threshold_val) else fmt_num(threshold_val, 4)
            cut_rows.append([r['variable'], fmt_num(r['auc']), threshold_str, fmt_num(r['sensitivity']), fmt_num(r['specificity']), fmt_num(r['youden'])])
        parts.append('\n' + '### ROC 最佳界值结果' + '\n')
        parts.append(md_table(cut_headers, cut_rows, ['l', 'r', 'r', 'r', 'r', 'r']))
        parts.append('\n注：\\* p<0.05 \\*\\* p<0.01')
        return '\n'.join(parts)

    def _prepare_predictors(data, y_true):
        predictors = {}
        ordered_vars = [v for v in _state['independent_vars'] if v in _state['matched_independent']]
        for var_name in ordered_vars:
            col_name = _state['matched_independent'][var_name]
            numeric_series = pd.to_numeric(data[col_name], errors='coerce')
            is_categorical = data[col_name].dtype == 'object' or data[col_name].dtype.name == 'category' or numeric_series.isna().sum() > len(data) * 0.5
            if is_categorical:
                non_null, _notice_non_null = _am_drop_na(data[col_name])
                if _notice_non_null:
                    _state['warnings'].append(_notice_non_null)
                if len(non_null) == 0:
                    _state['warnings'].append("变量 '{variable}' 无有效数据，已跳过".format(variable=var_name))
                    continue
                unique_values = sorted(non_null.unique().astype(str))
                encoding_map = {val: i + 1 for i, val in enumerate(unique_values)}
                data[col_name] = data[col_name].astype(str).map(encoding_map)
                predictors[var_name] = data[col_name]
                details = '; '.join((f'{k}->{v}' for k, v in list(encoding_map.items())[:5]))
                if len(encoding_map) > 5:
                    details += '...'
                var_display = variable_display(df, col_name)
                _state['warnings'].append("预测变量 '{variable}' 为非数值型，已自动编码: {encoding}".format(variable=var_display, encoding=details))
            else:
                data[col_name] = numeric_series
                predictors[var_name] = data[col_name]
        return predictors
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def tree(df, outcome, predictors):
    import numpy as np
    import pandas as pd
    from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, precision_recall_fscore_support, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

    def _is_classification(series):
        n_unique = series.nunique()
        if n_unique <= 20 and series.dtype.kind not in ('f',):
            return True
        if n_unique <= 10:
            return True
        return False
    _state = {'df': df, 'matched_columns': dict.fromkeys(predictors), 'dep_var_actual': outcome, 'max_depth': None, 'test_size': 0.2, 'warnings': []}
    _state['matched_columns'] = {c: c for c in predictors}

    def _analyze_and_format():
        if not _state['dep_var_actual']:
            return '错误：决策树分析需要 --dependent-var 指定目标变量。'
        if not 0 < _state['test_size'] < 1:
            return '错误：--test-size 必须介于 0 和 1 之间。'
        feature_cols = [c for c in _state['matched_columns'].values() if c != _state['dep_var_actual']]
        if not feature_cols:
            return '错误：除因变量外至少需要 1 个特征变量。'
        target = _state['df'][_state['dep_var_actual']].copy()
        features = _state['df'][feature_cols].copy()
        for col in feature_cols:
            numeric = pd.to_numeric(features[col], errors='coerce')
            if numeric.isna().sum() > len(features) * 0.5:
                le = LabelEncoder()
                non_null, _notice_non_null = _am_drop_na(features[col])
                if _notice_non_null:
                    _state['warnings'].append(_notice_non_null)
                if len(non_null) > 0:
                    le.fit(non_null)
                    features[col] = features[col].map(lambda x, _le=le: _le.transform([x])[0] if pd.notna(x) and x in _le.classes_ else np.nan)
            else:
                features[col] = numeric
        df_work = features.copy()
        df_work['__target__'] = target
        df_work, _notice_df_work = _am_drop_na(df_work)
        if _notice_df_work:
            _state['warnings'].append(_notice_df_work)
        if len(df_work) < 20:
            return f'错误：有效样本量不足（{len(df_work)}），决策树分析至少需要 20 个样本。'
        X = df_work[feature_cols].values
        y = df_work['__target__']
        is_clf = _is_classification(y)
        le_target = None
        class_values = None
        class_labels = []
        if is_clf:
            le_target = LabelEncoder()
            y_model = le_target.fit_transform(y)
            class_values = list(le_target.classes_)
            class_labels = [value_display(df, _state['dep_var_actual'], value) for value in class_values]
        else:
            y_model = y.values.astype(float)
        X_train, X_test, y_train, y_test = train_test_split(X, y_model, test_size=_state['test_size'], random_state=42)
        if is_clf:
            tree = DecisionTreeClassifier(max_depth=_state['max_depth'], criterion='gini', splitter='best', min_samples_split=2, min_samples_leaf=1, random_state=42)
        else:
            tree = DecisionTreeRegressor(max_depth=_state['max_depth'], criterion='squared_error', splitter='best', min_samples_split=2, min_samples_leaf=1, random_state=42)
        tree.fit(X_train, y_train)
        y_train_pred = tree.predict(X_train)
        y_test_pred = tree.predict(X_test)
        dep_display = variable_display(df, _state['dep_var_actual'])
        feat_display = [variable_display(df, c) for c in feature_cols]
        importances = np.asarray(tree.feature_importances_, dtype=float)
        task_label = '分类' if is_clf else '回归'
        parts = []
        parts.append('## 决策树{task}分析结果'.format(task=task_label) + '\n')
        parts.append('目标变量: {variable}'.format(variable=dep_display) + '\n')
        parts.append('### 特征权重值' + '\n')
        parts.append(_importance_table(feat_display, importances))
        if is_clf:
            labels = list(range(len(class_labels)))
            train_metrics = _classification_metrics(y_train, y_train_pred, labels, class_labels)
            test_metrics = _classification_metrics(y_test, y_test_pred, labels, class_labels)
            parts.append('\n' + '### 训练集模型评估结果' + '\n')
            parts.append(_classification_metrics_table(train_metrics))
            parts.append('\n' + '### 测试集模型评估结果' + '\n')
            parts.append(_classification_metrics_table(test_metrics))
            parts.append('\n' + '### 模型汇总表' + '\n')
            parts.append(_classification_summary_table(test_metrics, tree, len(X_train), len(X_test)))
            parts.append('\n注：平均值为宏平均，平均值(综合)为按样本数加权的综合平均；特征权重值反映各变量在决策树节点分裂中的相对重要性，权重加和值为 1。')
        else:
            train_reg = _regression_metrics(y_train, y_train_pred)
            test_reg = _regression_metrics(y_test, y_test_pred)
            parts.append('\n' + '### 训练集模型评估结果' + '\n')
            parts.append(_regression_metrics_table(train_reg))
            parts.append('\n' + '### 测试集模型评估结果' + '\n')
            parts.append(_regression_metrics_table(test_reg))
            parts.append('\n' + '### 模型汇总表' + '\n')
            parts.append(_regression_summary_table(test_reg, tree))
            parts.append('\n注：特征权重值反映各变量在决策树节点分裂中的相对重要性，权重加和值为 1。')
        return '\n'.join(parts)

    def _importance_table(feature_names, importances):
        rows = [[feature_name, fmt_num(float(importance), 3)] for feature_name, importance in zip(feature_names, importances)]
        return md_table(['项', '权重值'], rows, ['l', 'r'])

    def _classification_metrics(y_true, y_pred, labels, class_labels):
        precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
        acc = accuracy_score(y_true, y_pred)
        macro_p, macro_r, macro_f, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels, average='macro', zero_division=0)
        weighted_p, weighted_r, weighted_f, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels, average='weighted', zero_division=0)
        rows = []
        for label, p_val, r_val, f_val, n in zip(class_labels, precision, recall, f1, support):
            rows.append([str(label), fmt_num(float(p_val), 3), fmt_num(float(r_val), 3), fmt_num(float(f_val), 3), str(int(n))])
        n_total = int(len(y_true))
        rows.append(['准确率', '', '', fmt_num(float(acc), 3), str(n_total)])
        rows.append(['平均值', fmt_num(float(macro_p), 3), fmt_num(float(macro_r), 3), fmt_num(float(macro_f), 3), str(n_total)])
        rows.append(['平均值(综合)', fmt_num(float(weighted_p), 3), fmt_num(float(weighted_r), 3), fmt_num(float(weighted_f), 3), str(n_total)])
        return {'rows': rows, 'accuracy': float(acc), 'precision_weighted': float(weighted_p), 'recall_weighted': float(weighted_r), 'f1_weighted': float(weighted_f)}

    def _classification_metrics_table(metrics):
        return md_table(['项', '精确率', '召回率', 'f1-score', '样本数'], metrics['rows'], ['l', 'r', 'r', 'r', 'r'])

    def _classification_summary_table(metrics, tree, train_n, test_n):
        rows = [['模型参数设置', '数据预处理', 'None'], ['模型参数设置', '训练集比例', fmt_num(train_n / (train_n + test_n), 1)], ['模型参数设置', '交叉验证', '不进行'], ['模型参数设置', '节点分裂标准', tree.criterion], ['模型参数设置', '节点划分方式', tree.splitter], ['模型参数设置', '节点分裂最小样本数', str(tree.min_samples_split)], ['模型参数设置', '叶节点最小样本数', str(tree.min_samples_leaf)], ['模型参数设置', '树最大深度', str(_state['max_depth']) if _state['max_depth'] else '不限制'], ['模型评估效果', '准确率', f"{metrics['accuracy'] * 100:.3f}%"], ['模型评估效果', '精确率(综合)', f"{metrics['precision_weighted'] * 100:.3f}%"], ['模型评估效果', '召回率(综合)', f"{metrics['recall_weighted'] * 100:.3f}%"], ['模型评估效果', 'f1-score', fmt_num(metrics['f1_weighted'], 3)]]
        return md_table(['名称', '参数名', '参数值'], rows, ['l', 'l', 'l'])

    def _regression_metrics(y_true, y_pred):
        mse = mean_squared_error(y_true, y_pred)
        return {'R2': float(r2_score(y_true, y_pred)), 'RMSE': float(np.sqrt(mse)), 'MAE': float(mean_absolute_error(y_true, y_pred)), 'MSE': float(mse)}

    def _regression_metrics_table(metrics):
        rows = [[key, fmt_num(value, 4)] for key, value in metrics.items()]
        return md_table(['指标', '值'], rows, ['l', 'r'])

    def _regression_summary_table(metrics, tree):
        rows = [['模型参数设置', '数据预处理', 'None'], ['模型参数设置', '训练集比例', f"{1 - _state['test_size']:.1f}"], ['模型参数设置', '交叉验证', '不进行'], ['模型参数设置', '节点分裂标准', tree.criterion], ['模型参数设置', '节点划分方式', tree.splitter], ['模型参数设置', '节点分裂最小样本数', str(tree.min_samples_split)], ['模型参数设置', '叶节点最小样本数', str(tree.min_samples_leaf)], ['模型参数设置', '树最大深度', str(_state['max_depth']) if _state['max_depth'] else '不限制'], ['模型评估效果', 'R2', fmt_num(metrics['R2'], 4)], ['模型评估效果', 'RMSE', fmt_num(metrics['RMSE'], 4)], ['模型评估效果', 'MAE', fmt_num(metrics['MAE'], 4)]]
        return md_table(['名称', '参数名', '参数值'], rows, ['l', 'l', 'l'])
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result

def sample_size(effect, alpha, power):
    import math
    import sys
    _effect_reference = {'t': {'name': "Cohen's d", 'small': 0.2, 'medium': 0.5, 'large': 0.8}, 'paired_t': {'name': "Cohen's d", 'small': 0.2, 'medium': 0.5, 'large': 0.8}, 'anova': {'name': "Cohen's f", 'small': 0.1, 'medium': 0.25, 'large': 0.4}, 'regression': {'name': 'f2', 'small': 0.02, 'medium': 0.15, 'large': 0.35}, 'chi2': {'name': 'w', 'small': 0.1, 'medium': 0.3, 'large': 0.5}, 'correlation': {'name': 'r', 'small': 0.1, 'medium': 0.3, 'large': 0.5}}
    _test_names = {'t': '独立样本 t 检验', 'paired_t': '配对样本 t 检验', 'anova': '单因素方差分析', 'regression': '线性回归', 'chi2': '卡方检验', 'correlation': '相关分析'}
    _state = {'effect_size': effect, 'alpha': alpha, 'power': power, 'warnings': []}

    def _analyze_and_format():
        lang = 'zh'
        try:
            from statsmodels.stats.power import TTestIndPower, TTestPower, FTestAnovaPower, GofChisquarePower, FTestPower, NormalIndPower
        except ImportError:
            return '错误：需要安装 statsmodels。运行: pip install statsmodels'
        if _state['effect_size'] is None:
            ref = _effect_reference.get('t', _effect_reference['t'])
            _state['effect_size'] = ref['medium']
            _state['warnings'].append('未指定效应量，使用 {effect} 中等效应量标准: {value}'.format(effect=ref['name'], value=ref['medium']))
        test_label = _test_names['t'] if 't' in _test_names else 't'
        ref = _effect_reference.get('t', _effect_reference['t'])
        try:
            analysis = TTestIndPower()
            n_per_group = analysis.solve_power(effect_size=_state['effect_size'], alpha=_state['alpha'], power=_state['power'], ratio=1.0, alternative='two-sided')
            n_per_group = math.ceil(n_per_group)
            total_n = n_per_group * 2
        except Exception as e:
            msg = f'样本量计算失败: {e}'
            print(f'[error] {msg}', file=sys.stderr)
            return f'错误：{msg}'
        parts = []
        parts.append('## 样本量计算结果\n')
        parts.append('### 计算参数与结果\n')
        param_headers = ['参数', '值', '说明']
        param_alignments = ['l', 'c', 'l']
        param_rows = [['检验类型', test_label, ''], ['效应量', str(_state['effect_size']), f"{ref['name']}"], ['显著性水平(alpha)', str(_state['alpha']), '双尾检验'], ['统计功效(1-beta)', str(_state['power']), '']]
        param_rows.append(['分配比例', '1:1', '等组设计'])
        param_rows.append(['每组所需样本量', str(n_per_group), ''])
        param_rows.append(['**总样本量**', f'**{total_n}**', ''])
        parts.append(md_table(param_headers, param_rows, param_alignments))
        parts.append('\n### 效应量参考标准\n')
        ref_headers = ['统计方法', '效应量', '小效应', '中效应', '大效应']
        ref_alignments = ['l', 'l', 'c', 'c', 'c']
        ref_rows = []
        for tt, info in _effect_reference.items():
            label = _test_names[tt] if tt in _test_names else tt
            ref_rows.append([label, info['name'], str(info['small']), str(info['medium']), str(info['large'])])
        parts.append(md_table(ref_headers, ref_rows, ref_alignments))
        parts.append('\n注：效应量来源优先级 - 文献 Meta 分析 > 预实验数据 > Cohen 惯例标准')
        return '\n'.join(parts)
    result = _analyze_and_format()
    notices = list(dict.fromkeys(str(v) for v in _state["warnings"]))
    return ("\n\n".join(notices) + "\n\n" if notices else "") + result


def efa_header(labels):
    """Inspect source labels before pandas silently renames duplicate/empty headers."""
    labels = list(labels)
    if any(pd.isna(v) or not str(v).strip() for v in labels):
        raise ValueError("EFA 不接受空列名，请在源文件中明确每个题项名称")
    if pd.Index(labels).has_duplicates:
        raise ValueError("EFA 不接受重复列名，请先确认源文件中的题项身份")


def efa_fit(model, values):
    """Keep the library fit local when old factor_analyzer meets new sklearn."""
    import inspect
    from types import FunctionType
    from sklearn.utils.validation import check_array

    original = type(model).fit
    # factor_analyzer 0.5.1 uses force_all_finite; sklearn >=1.8 removed it.
    # Clone only this function's globals: never mutate a shared module/installer.
    if ("force_all_finite" in original.__code__.co_consts
            or any(isinstance(c, tuple) and "force_all_finite" in c
                   for c in original.__code__.co_consts)) and "force_all_finite" not in inspect.signature(check_array).parameters:
        def compatible_check_array(*args, **kwargs):
            if "force_all_finite" in kwargs:
                kwargs["ensure_all_finite"] = kwargs.pop("force_all_finite")
            return check_array(*args, **kwargs)
        scope = dict(original.__globals__)
        scope["check_array"] = compatible_check_array
        local_fit = FunctionType(original.__code__, scope, original.__name__, original.__defaults__, original.__closure__)
        return local_fit(model, values)
    return model.fit(values)


def efa_varimax(loadings):
    """Kaiser-normalized Varimax via exact two-column rotations, with 8 starts.

    Maximize sum_j[sum_i(b_ij**4) - sum_i(b_ij**2)**2 / p].
    Each Givens update maximizes its fourth-harmonic objective analytically;
    unlike factor_analyzer 0.5.1's SVD stopping rule, this checks the actual
    objective and the orthogonal gradient before accepting a solution.
    """
    n_items, n_factors = loadings.shape
    scales = np.sqrt((loadings ** 2).sum(axis=1))
    scales = np.where(scales > 0, scales, 1.0)
    normalized = loadings / scales[:, None]

    def objective(b):
        return float(np.sum(np.sum(b ** 4, axis=0) - np.sum(b ** 2, axis=0) ** 2 / n_items))

    rng = np.random.default_rng(42)
    starts = [np.eye(n_factors)] + [np.linalg.qr(rng.normal(size=(n_factors, n_factors)))[0] for _ in range(7)]
    best = None
    for start in starts:
        b = normalized @ start
        old_value = objective(b)
        converged = False
        for _ in range(1000):
            for j in range(n_factors - 1):
                for k in range(j + 1, n_factors):
                    u = b[:, j] ** 2 - b[:, k] ** 2
                    v = 2 * b[:, j] * b[:, k]
                    u, v = u - u.mean(), v - v.mean()
                    angle = 0.25 * np.arctan2(2 * np.dot(u, v), np.dot(u, u) - np.dot(v, v))
                    c, s = np.cos(angle), np.sin(angle)
                    first, second = b[:, j].copy(), b[:, k].copy()
                    b[:, j], b[:, k] = c * first + s * second, -s * first + c * second
            value = objective(b)
            gradient = 4 * (b ** 3 - b * np.mean(b ** 2, axis=0))
            tangent = b.T @ gradient
            stationary = np.max(np.abs(tangent - tangent.T)) / n_items < 1e-7
            if abs(value - old_value) <= 1e-10 * max(1.0, abs(value)) and stationary:
                converged = True
                break
            old_value = value
        if best is None or value > best[0]:
            best = (value, b.copy(), converged)
    if not best[2]:
        raise RuntimeError("Varimax 最佳目标解未稳定收敛；未输出可当作可靠结果的旋转载荷，请复核因子数或使用 --rotation none")
    return best[1] * scales[:, None]


def efa(df, names, factors=None, rotation="varimax", extraction="principal"):
    import warnings
    try:
        from factor_analyzer import FactorAnalyzer
        from scipy.stats import chi2
        from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
    except ImportError as exc:
        raise RuntimeError("EFA 需要 factor-analyzer、scipy 和 scikit-learn；请在当前 Python 环境安装这些依赖") from exc

    if extraction not in ("principal", "minres", "ml"):
        raise ValueError("提取方法应为 principal、minres 或 ml")
    efa_header(df.columns)
    if len(names) != len(set(names)):
        raise ValueError("EFA 的 --columns 不得重复选择同一题项")
    if len(names) < 3:
        raise ValueError("EFA 至少需要 3 个不同题项")
    raw = df[names]
    x = raw.apply(pd.to_numeric, errors="coerce")
    invalid = raw.notna() & x.isna()
    if invalid.any().any():
        bad = [str(n) for n in names if invalid[n].any()]
        raise ValueError("EFA 发现非数字内容，未将其静默当作缺失值：" + ", ".join(bad))
    if np.isinf(x.to_numpy(dtype=float)).any():
        raise ValueError("EFA 不接受正负无穷值")
    empty = [str(n) for n in names if x[n].notna().sum() == 0]
    if empty:
        raise ValueError("EFA 存在全空题项：" + ", ".join(empty))
    x = x.dropna()
    n, p = x.shape
    if n <= p:
        raise ValueError(f"EFA 完整样本不足：N={n}，题项数={p}；至少要求 N > 题项数以获得可逆相关矩阵")
    constant = [str(v) for v in names if x[v].nunique() < 2]
    if constant:
        raise ValueError("EFA 完整样本中存在常数题项：" + ", ".join(constant))
    corr = x.corr().to_numpy()
    if not np.isfinite(corr).all():
        raise ValueError("EFA 相关矩阵包含非有限值，请检查题项数值范围")
    eigenvalues = np.linalg.eigvalsh(corr)[::-1]
    if eigenvalues[-1] <= 1e-10 or eigenvalues[0] / eigenvalues[-1] > 1e10:
        raise ValueError("EFA 相关矩阵奇异或近奇异（可能有重复题项或线性依赖）；未自动删题或正则化")

    kmo_items, kmo = calculate_kmo(x)
    bartlett_stat, bartlett_p = calculate_bartlett_sphericity(x)
    bartlett_df = p * (p - 1) // 2
    suggested = int((eigenvalues > 1).sum())
    if factors is None:
        factors = max(1, suggested)
    if not 1 <= factors <= p:
        raise ValueError(f"因子数应为 1–{p}，实际为 {factors}")
    notes = []
    if not np.isfinite(kmo) or kmo < 0.6:
        notes.append("KMO 低于 0.60 或不可计算，数据的因子适配性不足")
    if bartlett_p >= 0.05:
        notes.append("Bartlett 检验不显著（p ≥ 0.05），未获得相关矩阵偏离单位阵的证据")
    if n < max(100, 5 * p):
        notes.append("样本较少（N < max(100, 5×题项数)），载荷和因子数可能不稳定；该提示是经验规则")
    class PublicFactorAnalysis(FactorAnalyzer):
        def _fit_principal(self, values):
            z = (values-values.mean(axis=0))/values.std(axis=0)
            matrix = z.T @ z / len(z)
            w, vectors = np.linalg.eigh((matrix+matrix.T)/2)
            order = np.argsort(-w, kind="stable")[:self.n_factors]
            w = np.clip(w[order],0,None); vectors=vectors[:,order]
            scores = z @ vectors
            signs = np.sign(scores[np.argmax(abs(scores),axis=0),np.arange(len(order))])
            signs[signs==0]=1
            return vectors * signs * np.sqrt(w)
    model = PublicFactorAnalysis(n_factors=factors, method=extraction,
        rotation="varimax" if factors>1 and rotation=="varimax" else None,
        rotation_kwargs={"tol":1e-12,"max_iter":5000} if factors>1 and rotation=="varimax" else None,
        impute="drop")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        efa_fit(model, x)
    if factors==1 and model.loadings_.sum()<0:
        model.loadings_=-model.loadings_
    rotated = model.loadings_
    for warning in caught:
        if "Failed to converge" in str(warning.message):
            raise RuntimeError("因子提取未收敛：" + str(warning.message))
        notes.append("计算库提示：" + str(warning.message))
    if not np.isfinite(rotated).all():
        raise RuntimeError("因子提取产生非有限载荷，未输出可解释的因子结果")
    if factors > 1 and rotation == "varimax":
        # Check the normalized rotation objective independently before displaying.
        scales = np.sqrt((rotated ** 2).sum(axis=1))
        scales = np.where(scales > 0, scales, 1.0)
        def objective(loadings):
            b = loadings / scales[:, None]
            return float(np.sum(np.sum(b ** 4, axis=0) - np.sum(b ** 2, axis=0) ** 2 / p))
        checked = efa_varimax(rotated)
        achieved, best = objective(rotated), objective(checked)
        if best - achieved > 1e-7 * max(1.0, abs(best)):
            raise RuntimeError("Varimax 旋转未稳定收敛，已停止展示载荷与结果表；请检查因子数或使用 --rotation none 复核未旋转解。")
    communalities = model.get_communalities()
    before, after = model.get_eigenvalues()
    extracted = before[:factors] if extraction=="principal" else after[:factors]
    rotated_ss = (rotated**2).sum(axis=0)
    use_rotation = factors>1 and rotation=="varimax"
    parts = ["## 效度分析结果（探索性因子分析）\n", "### KMO 和 Bartlett 检验\n"]
    parts.append(md_table(["检验项目","指标","值"], [
        ["KMO 取样适切性","",fmt_num(float(kmo))],
        ["Bartlett 球形度检验","近似卡方",fmt_num(float(bartlett_stat))],
        ["","df",str(bartlett_df)],["","p 值",fmt_p(float(bartlett_p))]
    ],["l","l","c"]))
    evaluation = "非常好" if kmo>=.9 else "好" if kmo>=.8 else "一般" if kmo>=.7 else "勉强可接受" if kmo>=.6 else "不适合做因子分析"
    parts.append(f"\nKMO = {fmt_num(float(kmo))}（{evaluation}）")
    parts.append("\n### 总方差解释\n")
    headers=["成分","初始特征值","方差解释率%","累积%","提取载荷平方和","方差解释率%","累积%"]
    if use_rotation:
        headers += ["旋转载荷平方和","方差解释率%","累积%"]
    rows=[]
    for i in range(factors):
        row=[str(i+1),fmt_num(float(before[i])),fmt_num(float(before[i]/p*100),2),fmt_num(float(before[:i+1].sum()/p*100),2),fmt_num(float(extracted[i])),fmt_num(float(extracted[i]/p*100),2),fmt_num(float(extracted[:i+1].sum()/p*100),2)]
        if use_rotation:
            row += [fmt_num(float(rotated_ss[i])),fmt_num(float(rotated_ss[i]/p*100),2),fmt_num(float(rotated_ss[:i+1].sum()/p*100),2)]
        rows.append(row)
    parts.append(md_table(headers,rows,["c"]*len(headers)))
    label="旋转后因子载荷矩阵" if use_rotation else "因子载荷矩阵"
    parts.append(f"\n### {label}\n")
    rows=[]
    for name,load,h in zip(names,rotated,communalities):
        cells=[f"**{fmt_num(float(v))}**" if abs(v)>.4 else fmt_num(float(v)) for v in load]
        htext=fmt_num(float(h)); htext=f"_{htext}_" if h<.4 else htext
        rows.append([variable_display(df, name)]+cells+[htext])
    parts.append(md_table(["名称"]+[f"因子{i+1}" for i in range(factors)]+["共同度(公因子方差)"],rows,["l"]+["c"]*(factors+1)))
    parts.append("\n注：加粗载荷表示绝对值 > 0.4；斜体共同度表示 < 0.4")
    parts.append("旋转方法："+("最大方差法（Varimax）" if use_rotation else "未旋转（仅 1 个因子）" if factors==1 else "未旋转"))
    parts.append("提取方法："+("主成分分析（PCA）" if extraction=="principal" else extraction))
    if len(df)!=n:
        notes.append(f"缺失处理：所选题项整行删除 {len(df)-n} 条，完整样本 N={n}，原始 N={len(df)}")
    if suggested==0 and factors==1:
        notes.append("没有特征根大于 1 的成分，按应用默认暂定 1 个；不得据此判为效度已验证")
    parts += ["\n提示："+note+"。" for note in notes]
    parts.append("\n本结果提供探索性结构证据；不能据此宣称整体效度已经通过。")
    return "\n".join(parts)



def parser():
    p = argparse.ArgumentParser(description="ChatSPSS public baseline analysis helper")
    p.add_argument("--task", required=True, choices=["overview", "frequency", "multiple_choice", "word_frequency", "norm_reference", "normality", "correlation", "independent_ttest", "paired_ttest", "chi_square", "anova", "nonparametric", "linear_regression", "binary_logistic", "ordinal_logistic", "reliability", "efa", "pca", "cluster", "roc", "decision_tree", "sample_size"])
    p.add_argument("--file")
    p.add_argument("--columns")
    p.add_argument("--outcome", "--dependent-var")
    p.add_argument("--group", "--group-var")
    p.add_argument("--row")
    p.add_argument("--col")
    p.add_argument("--before")
    p.add_argument("--after")
    p.add_argument("--predictors", "--independent-vars")
    p.add_argument("--method", choices=["pearson", "spearman"], default="pearson")
    p.add_argument("--k", "--n-clusters", type=int, default=3)
    p.add_argument("--effect", "--effect-size", type=float, default=0.5)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--power", type=float, default=0.8)
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--norm-means")
    p.add_argument("--norm-sds")
    p.add_argument("--factors", "--n-factors", type=int, help="EFA factor count; omitted: provisional eigenvalue > 1 suggestion")
    p.add_argument("--rotation", choices=["varimax", "none"], default="varimax", help="EFA rotation (default: varimax)")
    p.add_argument("--extraction", "--extract-method", choices=["principal", "minres", "ml"], default="principal", help="EFA extraction (default: principal, matching application)")
    return p


def show_result(out):
    if not out or not any(line.startswith("|") for line in out.splitlines()):
        raise ValueError(out or "分析未产生结果表")
    if out.lstrip().startswith("错误"):
        raise ValueError(out)
    print(out)
    print("\n\n---\n[INSTRUCTION]\n请将上方全部用户可见 Markdown 表格原样渲染在回复中，再紧跟解读。保留表头、列序、数值精度、显著性星号、标题、单位和注释；不加代码围栏，不删表，不只交付路径。本内部说明不展示给用户。\n[/INSTRUCTION]")


def main():
    args = parser().parse_args()
    if args.task == "sample_size":
        show_result(sample_size(args.effect, args.alpha, args.power)); return 0
    if not args.file:
        raise ValueError("--file is required for this task")
    df = load_table(args.file, strict_columns=args.task == "efa")
    names = cols(df, args.columns)
    if args.task == "overview": out = overview(df, names)
    elif args.task == "frequency": out = frequency(df, names)
    elif args.task == "multiple_choice": out = multiple_choice(df, names)
    elif args.task == "word_frequency": out = word_frequency(df, names[0], args.top)
    elif args.task == "norm_reference":
        if bool(args.norm_means) != bool(args.norm_sds):
            raise ValueError("常模均值和标准差需同时提供；都不提供时计算样本内部常模")
        out = norm_reference(df, names, args.norm_means, args.norm_sds)
    elif args.task == "normality": out = normality(df, names)
    elif args.task == "correlation": out = correlation(df, names, args.method)
    elif args.task == "independent_ttest": out = two_group(df, args.outcome, args.group)
    elif args.task == "paired_ttest": out = paired(df, args.before, args.after)
    elif args.task == "chi_square": out = chi_square(df, args.row, args.col)
    elif args.task == "anova": out = anova(df, args.outcome, args.group)
    elif args.task == "nonparametric": out = nonparametric(df, args.outcome, args.group)
    elif args.task == "linear_regression": out = regression(df, args.outcome, cols(df, args.predictors))
    elif args.task == "binary_logistic": out = logistic(df, args.outcome, cols(df, args.predictors))
    elif args.task == "ordinal_logistic": out = ordinal(df, args.outcome, cols(df, args.predictors))
    elif args.task == "reliability": out = reliability(df, names)
    elif args.task == "efa": out = efa(df, names, args.factors, args.rotation, args.extraction)
    elif args.task == "pca": out = pca(df, names, args.factors)
    elif args.task == "cluster": out = cluster(df, names, args.k)
    elif args.task == "roc": out = roc(df, args.outcome, names[0])
    elif args.task == "decision_tree": out = tree(df, args.outcome, cols(df, args.predictors))
    else: raise AssertionError(args.task)
    show_result(out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ChatSPSS error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
