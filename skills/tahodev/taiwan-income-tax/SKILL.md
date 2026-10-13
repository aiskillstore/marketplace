---
name: taiwan-income-tax
description: 台灣綜合所得稅試算——依財政部公告的免稅額、標準扣除額、薪資所得特別扣除額與課稅級距，估算個人綜所稅（114、115 年度）。幾級稅率、免稅額多少、標準扣除額、薪資特別扣除、年薪多少要繳多少稅的問題適用。免 API 金鑰、免登入、純離線計算。實際申報、列舉扣除、基本生活費差額、股利與海外所得不適用。
license: MIT
metadata:
  category: civic
  locale: zh-TW
---

# taiwan-income-tax

> 實測日：2026-10-03（最近一次端對端實測；數值基準日各自標於內文）

綜合所得稅的免稅額、扣除額、級距由財政部每年公告，金額固定，不需要呼叫任何 API。這個技能把公告的數字放進一段純 Python 計算，回答「這個所得大概要繳多少」。不需要金鑰或登入。

## 基本流程

1. 問清楚年度（所得年度，不是申報年度）、申報身分（單身或與配偶合併）、扶養人數、薪資與其他所得
2. 用下方程式算出綜合所得淨額與應納稅額
3. 回報時附上年度、公告來源與「估算」字樣

### 公告來源（2026-10-03 實測可讀）

| 年度 | 公告 | URL |
|---|---|---|
| 115 年度（2027 年 5 月申報） | 財政部台財稅字第 1140466407 號公告 | https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg031224/ch04/type3/gov30/num12/Eg.pdf |
| 114 年度（2026 年 5 月申報） | 財政部 2024-11-28 公告 | https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=e6bfc90ed42e42ccbcd83be96e331afc |

### 公告數字（2026-10-03 對照上列公告）

| 項目 | 114 年度 | 115 年度 |
|---|---|---|
| 免稅額（每人） | 97,000 | 101,000 |
| 免稅額（年滿 70 歲） | 145,500 | 151,500 |
| 標準扣除額（單身） | 131,000 | 136,000 |
| 標準扣除額（有配偶） | 262,000 | 272,000 |
| 薪資所得特別扣除額（上限） | 218,000 | 227,000 |
| 課稅級距上限（5% / 12% / 20% / 30%） | 590,000 / 1,330,000 / 2,660,000 / 4,980,000 | 610,000 / 1,380,000 / 2,770,000 / 5,190,000 |
| 第 5 級稅率 | 40% | 40% |

### 1. 計算程式

```python
RATES = [0.05, 0.12, 0.20, 0.30, 0.40]
YEARS = {
    114: dict(exempt=97000, exempt70=145500, std=(131000, 262000), salary=218000,
              top=[590000, 1330000, 2660000, 4980000]),
    115: dict(exempt=101000, exempt70=151500, std=(136000, 272000), salary=227000,
              top=[610000, 1380000, 2770000, 5190000]),
}

def income_tax(year, salary=0, other=0, married=False, dependents=0,
               seniors=0, extra_deduction=0):
    """估算綜合所得淨額與應納稅額。dependents 為本人以外的人數（含配偶），
    seniors 為其中年滿 70 歲的人數。extra_deduction 為其他特別扣除額合計。"""
    p = YEARS[year]
    people = 1 + dependents
    exemption = (people - seniors) * p['exempt'] + seniors * p['exempt70']
    std = p['std'][1] if married else p['std'][0]
    sal_ded = min(salary, p['salary'])
    net = max(0, salary + other - exemption - std - sal_ded - extra_deduction)
    tax, low = 0.0, 0
    for rate, high in zip(RATES, p['top'] + [float('inf')]):
        if net > low:
            tax += (min(net, high) - low) * rate
        low = high
    return net, round(tax)

# 單身、薪資 80 萬、無扶養
assert income_tax(115, salary=800000) == (336000, 16800)
assert income_tax(114, salary=800000) == (354000, 17700)
# 薪資 200 萬進入 20% 級距：122,900 + (1,536,000 - 1,380,000) * 20%
assert income_tax(115, salary=2000000) == (1536000, 154100)
# 級距累進額與公告一致
assert round(610000 * 0.05) == 30500
assert 30500 + round((1380000 - 610000) * 0.12) == 122900
assert 122900 + round((2770000 - 1380000) * 0.20) == 400900
assert 400900 + round((5190000 - 2770000) * 0.30) == 1126900
print(income_tax(115, salary=800000), income_tax(114, salary=800000))
```

2026-10-03 實測輸出：`(336000, 16800) (354000, 17700)`。

### 2. 回報範式

「115 年度、單身、薪資 80 萬、無扶養：免稅額 101,000 ＋ 標準扣除額 136,000 ＋ 薪資特別扣除 227,000，綜合所得淨額 336,000，落在 5% 級距，約繳 16,800 元（估算，未計其他扣除）。」

## 錯誤與失敗時的處理

- **年度不確定**：所得年度與申報年度差一年。114 年度所得在 2026 年 5 月申報，115 年度所得在 2027 年 5 月申報。使用者沒說就先問
- **每年可能調整**：免稅額與扣除額在消費者物價指數累計漲幅達 3% 時調整（114 年度因漲幅 2.29% 未調整）。年度不在上表時，抓公告確認，不要沿用舊數字
- **不在這個估算裡的項目**：列舉扣除、儲蓄投資特別扣除、幼兒學前與長期照顧等特別扣除、基本生活費差額、股利分開計稅、基本稅額（最低稅負）與海外所得。使用者有這些情況時，只回報本程式的估算，並明講沒算進去的項目；其他特別扣除可由 `extra_deduction` 手動帶入
- **薪資特別扣除是上限**：實際薪資低於上限時，只能扣薪資金額
- **公告連結打不開**：換上表另一個連結，或請使用者到財政部網站確認；不要憑記憶補數字
- **不要代為申報**：這個技能只估算，實際申報請走財政部電子申報

## English summary

Taiwan personal income tax estimator, offline and keyless. It encodes the Ministry of Finance annual announcements for income years 114 and 115 (exemption 97,000 / 101,000 TWD, standard deduction 131,000 / 136,000 single, salary special deduction cap 218,000 / 227,000, brackets 5/12/20/30/40%). Sources: the Gazette announcement `https://gazette.nat.gov.tw/EG_FileManager/eguploadpub/eg031224/ch04/type3/gov30/num12/Eg.pdf` (income year 115) and the 2024-11-28 MOF announcement page for year 114. Verified 2026-10-03: single filer with 800,000 TWD salary pays 16,800 (year 115) and 17,700 (year 114). It is an estimate only: itemized deductions, other special deductions, basic living expense difference, dividends and the alternative minimum tax are not modelled. Always state the income year and re-check the announcement when the year is not in the table.
