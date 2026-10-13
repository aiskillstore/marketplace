---
name: taiwan-id-check
description: 統一編號與國民身分證統一編號的檢核碼驗證——純計算，不需要網路與 API 金鑰。統一編號檢查、統編對不對、身分證字號驗、身分證字號驗證、檢核碼、check digit 的問題適用。查詢公司登記資料、個人資料不適用（本技能只做數學檢核，不查任何資料庫）。
license: MIT
metadata:
  category: government
  locale: zh-TW
---

# taiwan-id-check

> 實測日：2026-10-02（最近一次端對端實測；數值基準日各自標於內文）

用財政部公布的檢核邏輯驗證統一編號（統編）與身分證字號。**純計算**，不連網、不需金鑰、不查任何資料庫——只能回答「這串號碼的檢核碼對不對」，不能回答「這家公司是否存在」。

## 1. 統一編號（8 碼）

財政部檢核邏輯：各碼乘上權重 `1,2,1,2,1,2,4,1`，乘積的十位數與個位數相加後總和，能被 5 整除即為合法。**特例：第 7 碼是 7 時**，該位乘積（7×4=28）的「各位數和」可視為 0 或 1 計算，任一成立即合法（財政部營利事業統一編號檢查邏輯的明文規定）。

```bash
python3 - <<'PY'
import re
def ubn_ok(n: str) -> bool:
    if not isinstance(n, str) or not re.fullmatch(r'[0-9]{8}', n):   # 只收 ASCII 數字（isdigit 會放行全形、上標數字）
        return False
    w = [1, 2, 1, 2, 1, 2, 4, 1]
    ds = lambda p: p // 10 + p % 10          # 乘積的各位數和
    base = sum(ds(int(d) * k) for d, k in zip(n, w))
    if base % 5 == 0:
        return True
    if n[6] == '7':                          # 第 7 碼 7 的特例
        c = ds(7 * 4)
        return (base - c + 0) % 5 == 0 or (base - c + 1) % 5 == 0
    return False

for n in ['22099131', '97176270', '10000073']:
    print(n, ubn_ok(n))
PY
```

2026-09-19 實測（公開公司統編）：台積電 `22099131`、中華電信 `96979933` 合法；台灣大哥大 `97176270` 也合法，但它的加權和 base=40，走一般路徑就過關，驗收不出特例實作；特例的驗收要用合成向量 `10000073`（base=14，無特例判非法、有特例判合法）才有鑑別力（2026-09-30 複測更正，原文誤植 97176270「只在特例路徑下合法」）；把任一碼改動（如 `22099132`）即判非法。

## 2. 國民身分證統一編號（1 英文字母 + 9 碼數字）

檢核邏輯（內政部）：首字母依對照表轉成兩位數（A=10、B=11 … I=34、O=35、W=32、X=30、Y=31、Z=33，跳過容易混淆的順序），十位數乘 1、個位數乘 9；之後 8 碼數字依序乘 8,7,6,5,4,3,2,1，最後一碼檢核碼乘 1。全部相加能被 10 整除即合法。

```bash
python3 - <<'PY'
import re
def pid_ok(s: str) -> bool:
    if not isinstance(s, str):
        return False
    s = s.strip().upper()
    # 1 個 ASCII 大寫字母 + 第二碼 1/2（國民）或 8/9（新式居留證）+ 8 碼 ASCII 數字
    if not re.fullmatch(r'[A-Z][1289][0-9]{8}', s):
        return False
    L = {'A':10,'B':11,'C':12,'D':13,'E':14,'F':15,'G':16,'H':17,'I':34,
         'J':18,'K':19,'L':20,'M':21,'N':22,'O':35,'P':23,'Q':24,'R':25,
         'S':26,'T':27,'U':28,'V':29,'W':32,'X':30,'Y':31,'Z':33}
    v = L[s[0]]
    total = v // 10 + (v % 10) * 9
    total += sum(int(d) * k for d, k in zip(s[1:], [8,7,6,5,4,3,2,1,1]))
    return total % 10 == 0

for s in ['A123456789', 'A123456788']:
    print(s, pid_ok(s))
PY
```

2026-10-02 補測異常輸入：`'２２０９９１３１'`（全形）、`'2209913¹'`、`''`、`None` 皆回 `False`；`'a123456789'`（小寫）會先轉大寫而合法。

2026-09-19 實測：經典測試值 `A123456789`、`B221003265` 合法；末碼改動（`A123456788`）即判非法。

## 錯誤與失敗時的處理

- **長度或字元不符**：直接回 `False`，不要嘗試補齊或猜測。非 ASCII 的輸入（全形數字、上標數字、希臘或土耳其字母等）一律回 `False`，不會丟例外（2026-10-02 測試）。
- **第二碼限 1、2、8、9**：1/2 為國民身分證性別碼，8/9 為新式居留證；舊式居留證（第二碼為英文字母）本技能不支援，會回 `False`。
- **檢核碼錯誤不等於「偽造」**：只代表這串號碼不符合檢核規則（常見於打錯字）。回報時用「檢核碼不符」，不要做法律判斷。
- **本技能不查資料庫**：統編對應的公司名稱、狀態請導向財政部「稅籍登記資料公示查詢」；身分證真偽無法以檢核碼判斷（檢核碼可計算，不等於實際核發）。
- **第 7 碼 7 的特例漏做**：舊版實作常漏掉特例，會把只靠特例才合法的統編（如合成向量 `10000073`）誤判非法；驗收時務必測這組（`97176270` 兩條路徑皆合法，不能驗收特例）。

## English summary

Checksum validation for Taiwan Unified Business Numbers (UBN, 8 digits) and National ID numbers (1 letter + 9 digits). Pure computation - no network, no key, no database lookup. UBN: weights 1,2,1,2,1,2,4,1, digit-sum of products, total divisible by 5; special case when the 7th digit is 7 (its contribution may count as 0 or 1). National ID: letter mapped per the MOI table (A=10 ... Z=33 with the 34/35/32/30/31/33 exceptions), tens x1 + ones x9, then digits weighted 8..1 with the check digit x1, total divisible by 10. Verified 2026-09-19 against public UBNs (TSMC 22099131, Chunghwa Telecom 96979933) and canonical ID test values; synthetic vector 10000073 exercises the 7-special-case (97176270 passes both paths and cannot discriminate - corrected 2026-09-30). A wrong checksum means "fails the check rule" (usually a typo) - never call it forgery; this skill cannot confirm existence or issuance.
