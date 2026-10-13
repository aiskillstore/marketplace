#!/usr/bin/env python3
"""月額表甲欄の源泉徴収税額を、財務省告示の電算機計算の特例(国税庁公表)で計算する。

使い方:
  python3 withholding-tax/lookup.py --salary 175000 --dependents 2            # 令和8年分(2026年支給分)
  python3 withholding-tax/lookup.py --salary 300000 --dependents 0 --year 2027 # 令和9年分(2027年支給分)

--salary: その月の社会保険料等控除後の給与等の金額(円)。額面ではない。
--dependents: 源泉控除対象配偶者 + 源泉控除対象親族(+障害者等の加算)の人数。
特例の結果は税額表(月額表)の金額と一致するとは限らない(年末調整で精算される)。
外部通信なし。根拠・基準日: 国税庁 令和8年分/令和9年分 電算機計算の特例(実測日 2026-10-03)
"""
import argparse, json, math, sys

# 第1表の下限額と最初の区分の上限(A)。年分で変わる(令和9年分から引上げ)
KYUYO_MIN = {2026: (54167, 158333), 2027: (57500, 169444)}
# 第3表の基礎控除の最大額。2,120,833円以下で適用(令和9年分から引上げ)
KISO_TOP = {2026: 48334, 2027: 51667}
SPOUSE_DEP = 31667  # 第2表: 配偶者控除/扶養控除 1人あたり(令和8・9年分とも)

def kyuyo_kojo(a, year):
    lo, thr = KYUYO_MIN[year]
    if a <= thr:
        v = lo
    elif a <= 299999:
        v = a * 0.30 + 6667
    elif a <= 549999:
        v = a * 0.20 + 36667
    elif a <= 708330:
        v = a * 0.10 + 91667
    else:
        v = 162500
    return math.ceil(round(v, 6))  # 1円未満切り上げ(浮動小数の誤差を丸めてから)

def kiso_kojo(a, year):
    if a <= 2120833:
        return KISO_TOP[year]
    if a <= 2162499:
        return 40000
    if a <= 2204166:
        return 26667
    if a <= 2245833:
        return 13334
    return 0

def tax_from_taxable(b):
    """第4表。10円未満は四捨五入。"""
    if b <= 0:
        return 0
    if b <= 162500:
        v = b * 0.05105
    elif b <= 275000:
        v = b * 0.10210 - 8296
    elif b <= 579166:
        v = b * 0.20420 - 36374
    elif b <= 750000:
        v = b * 0.23483 - 54113
    elif b <= 1500000:
        v = b * 0.33693 - 130688
    elif b <= 3333333:
        v = b * 0.40840 - 237893
    else:
        v = b * 0.45945 - 408061
    return int(math.floor(v / 10 + 0.5)) * 10

def calc(salary, dependents, year):
    if year not in KYUYO_MIN:
        raise ValueError("対応年分は 2026(令和8年分) と 2027(令和9年分) のみ")
    if salary < 0 or dependents < 0:
        raise ValueError("salary と dependents は 0 以上")
    k = kyuyo_kojo(salary, year)
    dep = SPOUSE_DEP * dependents
    kiso = kiso_kojo(salary, year)
    taxable = salary - k - dep - kiso
    return {
        "year": year, "reiwa": f"令和{year - 2018}年分",
        "salary_after_social_insurance": salary, "dependents": dependents,
        "kyuyo_shotoku_kojo": k, "dependents_deduction": dep, "kiso_kojo": kiso,
        "taxable": taxable, "tax": tax_from_taxable(taxable),
        "note": "財務省告示の特例による計算。税額表(月額表甲欄)とは一致しないことがあり、差は年末調整で精算される。",
    }

def main():
    ap = argparse.ArgumentParser(description="月額表甲欄の源泉徴収税額(特例計算)")
    ap.add_argument("--salary", type=int, required=True, help="社会保険料等控除後の月の給与等(円)")
    ap.add_argument("--dependents", type=int, required=True, help="源泉控除対象配偶者+親族の人数")
    ap.add_argument("--year", type=int, default=2026, help="2026=令和8年分(既定) / 2027=令和9年分")
    a = ap.parse_args()
    try:
        out = calc(a.salary, a.dependents, a.year)
    except ValueError as e:
        raise SystemExit(json.dumps({"error": str(e)}, ensure_ascii=False))
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == "__main__":
    main()
