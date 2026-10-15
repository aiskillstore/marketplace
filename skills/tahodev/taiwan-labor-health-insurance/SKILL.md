---
name: taiwan-labor-health-insurance
description: 台灣勞健保費率計算——依勞保局、健保署公告的費率與投保級距（115 年 1 月 1 日起適用），算受僱勞工每月自付的勞保（含就業保險）、健保保費與雇主提繳的勞退 6%。月薪投保哪一級、勞保費多少、健保費多少、眷屬加保多少錢的問題適用。免 API 金鑰、純離線計算。職災保險、職業工會、自營業者、補充保費、部分工時不適用。
license: MIT
metadata:
  category: civic
  locale: zh-TW
---

# taiwan-labor-health-insurance

> 實測日：2026-10-03（最近一次端對端實測；數值基準日各自標於內文）

受僱勞工的勞保、健保費率與投保級距由勞動部、衛福部公告，一年只改一兩次。這個技能把 115 年（2026）適用的數字放進一段純 Python，回答「月薪 X 每月被扣多少勞健保」。不需要金鑰或登入。

## 基本流程

1. 問清楚月薪（投保薪資看月薪資總額）、眷屬人數（健保，最多計 3 口）
2. 月薪對應級距：取「大於等於月薪的最小一級」
3. 用下方程式算自付金額與雇主勞退提繳，回報時註明「115 年適用、估算」

### 公告來源（2026-10-03 實測可讀）

| 內容 | URL |
|---|---|
| 勞工保險投保薪資分級表（115 年 1 月 1 日起） | https://www.bli.gov.tw/0005475.html |
| 勞工保險普通事故及就業保險合計保險費分擔金額表 | https://www.bli.gov.tw/0102606.html |
| 勞保費率與負擔比例 | https://www.bli.gov.tw/0005478.html |
| 勞工退休金月提繳分級表 | https://www.bli.gov.tw/0013083.html |
| 健保投保金額分級表（115.01.01 生效） | https://www.nhi.gov.tw/ch/cp-19422-c534e-2569-1.html |
| 健保保費計算公式與費率 5.17% | https://www.nhi.gov.tw/ch/cp-3277-6c895-2588-1.html |
| 最低工資調整與 115 年分級表修正說明 | https://www.mol.gov.tw/1607/1632/1633/86680/ |

### 費率與規則（2026-10-03 對照上列公告）

- 勞保：普通事故 11.5% 加就業保險 1%，合計 12.5%；被保險人負擔 20%（雇主 70%、政府 10%）
- 勞保投保薪資第一級 29,500 元（115 年 1 月 1 日起，配合最低工資），最高 45,800 元
- 健保：費率 5.17%，被保險人負擔 30%，眷屬每人各計一份，超過三口以三口計
- 健保投保金額第一級 29,500 元，最高 313,000 元
- 勞退：雇主每月提繳 6%，月提繳工資最高 150,000 元
- 金額四捨五入到整數

### 1. 計算程式

```python
from decimal import Decimal, ROUND_HALF_UP

# 勞保投保薪資級距（受僱勞工全時，115 年）
LABOR = [29500, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800]
# 健保投保金額級距（115 年，共 58 級）
HEALTH = LABOR + [48200, 50600, 53000, 55400, 57800, 60800, 63800, 66800, 69800, 72800,
                  76500, 80200, 83900, 87600, 92100, 96600, 101100, 105600, 110100,
                  115500, 120900, 126300, 131700, 137100, 142500, 147900, 150000,
                  156400, 162800, 169200, 175600, 182000, 189500, 197000, 204500, 212000,
                  219500, 228200, 236900, 245600, 254300, 263000, 273000, 283000, 293000,
                  303000, 313000]
# 勞退月提繳工資級距：同健保級距到 150,000 為止（29,500 以上）
PENSION = [x for x in HEALTH if x <= 150000]

def rnd(x):
    return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def tier(salary, table):
    for t in table:
        if salary <= t:
            return t
    return table[-1]

def premiums(salary, dependents=0):
    """受僱勞工每月自付的勞保（含就保）與健保，及雇主勞退提繳。"""
    labor_base = tier(salary, LABOR)
    health_base = tier(salary, HEALTH)
    pension_base = tier(salary, PENSION)
    labor = rnd(Decimal(labor_base) * Decimal('0.125') * Decimal('0.2'))
    health = rnd(Decimal(health_base) * Decimal('0.0517') * Decimal('0.3')) * (1 + min(dependents, 3))
    pension = rnd(Decimal(pension_base) * Decimal('0.06'))
    return dict(labor_base=labor_base, health_base=health_base,
                labor=labor, health=health, pension_employer=pension)

# 與公告分擔金額表對照（115 年）
assert premiums(29500)['labor'] == 738      # 勞保+就保，被保險人負擔
assert premiums(30300)['labor'] == 758
assert premiums(29500)['health'] == 458     # 健保，本人
assert premiums(29500, 3)['health'] == 1832 # 本人+3 眷口
assert premiums(45800)['health'] == 710
assert premiums(150000)['health'] == 2327
assert premiums(313000)['health'] == 4855
assert premiums(60000)['labor_base'] == 45800   # 勞保封頂
assert premiums(60000)['health_base'] == 60800
print(premiums(50000, 1))
```

2026-10-03 實測輸出：`{'labor_base': 45800, 'health_base': 50600, 'labor': 1145, 'health': 1570, 'pension_employer': 3036}`。

### 2. 回報範式

「月薪 5 萬、眷屬 1 人（115 年）：勞保投保薪資封頂 45,800，自付勞保（含就保）1,145 元；健保投保金額 50,600，本人加 1 眷口自付 1,570 元；雇主另提繳勞退 3,036 元。合計每月自付約 2,715 元（估算）。」

## 錯誤與失敗時的處理

- **年度**：本程式是 115 年（2026）數字。費率或最低工資調整後級距會變，年度不同就先抓上表公告確認，不要沿用
- **級距是「向上取」**：月薪 30,000 對應 30,300，不是 29,500
- **只涵蓋一般受僱全時勞工**：部分工時、職業工會、自營業者、外籍移工、65 歲以上與未滿 15 歲勞工（不參加就業保險）的費率或負擔比例不同，遇到就如實說不在範圍內
- **職災保險與補充保費不在這裡**：職災保險費率依行業別，由雇主全額負擔；補充保險費（費率 2.11%，獎金、兼職所得、股利等）另算
- **雇主負擔不完整**：這裡只算勞工自付與雇主勞退提繳，不算雇主的勞健保負擔
- **舊對照表**：網路上 28,590 起算的勞保級距是 114 年及以前的，已不適用
- **公告連結打不開**：換上表另一個連結，或請使用者到勞保局、健保署網站確認；不要憑記憶補數字

## English summary

Taiwan labor and health insurance premium calculator for salaried employees, offline and keyless, using the rates in force from 2026-01-01 (ROC year 115). Labor insurance: 11.5% ordinary accident plus 1% employment insurance, employee pays 20%, insured salary tiers from 29,500 to 45,800 TWD. National health insurance: 5.17%, employee pays 30% per person (dependents capped at 3), insured amount tiers from 29,500 to 313,000 TWD. Employer pension contribution 6% up to a 150,000 TWD wage cap. Sources: BLI tier table `https://www.bli.gov.tw/0005475.html` and the NHI tier table `https://www.nhi.gov.tw/ch/cp-19422-c534e-2569-1.html`. Verified 2026-10-03: the program reproduces the published amounts (29,500 tier: labor 738, health 458; 313,000 tier: health 4,855). Not covered: part-time or union members, occupational accident insurance, supplementary premium, employer-side labor and health shares. Re-check the announcements when the year changes.
