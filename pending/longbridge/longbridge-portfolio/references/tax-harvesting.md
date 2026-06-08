# longbridge-tax-harvesting

Prompt-only analysis skill. Scans account positions for unrealised losses, calculates the potential tax saving from harvesting each loss, flags wash-sale risk, and suggests economically-similar substitute securities. Applies to US-listed securities only (US tax rules). Read-only — does not place orders.

## Important Notes

- **US tax rules only**: wash-sale rule (IRS Section 1091) applies to US investors trading US-listed securities. Not applicable to HK, A-share, or other markets without equivalent rules.
- **Requires Trade permission**: cost basis data requires `longbridge auth login` with Trade scope.
- **Not tax advice**: always consult a qualified tax professional before executing.

## Workflow

1. Fetch all positions including cost basis (average cost).
2. Fetch current prices for all positions.
3. Compute unrealised gain/loss per position.
4. Filter to positions with unrealised losses.
5. For each loss position, compute potential tax saving (loss × estimated marginal tax rate).
6. Flag wash-sale risk (any purchase of the same or substantially-identical security within 30 days before or after the sale).
7. Suggest substitute securities that maintain similar market exposure.
8. Rank opportunities by tax saving magnitude.

## CLI

Run `longbridge <subcommand> --help` to verify exact flags before calling.

```bash
# Positions with cost basis
longbridge positions --format json

# Current prices (run concurrently for each symbol)
longbridge quote <SYMBOL> --format json
```

## Calculations

| Quantity            | Method                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------- |
| Unrealised loss     | (Current price − Average cost) × Quantity                                                 |
| Tax saving estimate |                                                                                           | Unrealised loss | × assumed marginal tax rate (default 37% short-term / 20% long-term) |
| Holding period      | Today − position open date (if available); classify short-term (<1yr) or long-term (≥1yr) |
| Wash-sale window    | 30 days before + 30 days after the sale date                                              |

## Substitute Securities

When suggesting substitutes to avoid wash-sale, recommend securities that are economically similar but not "substantially identical":

| Original          | Example substitute (same sector, different issuer) |
| ----------------- | -------------------------------------------------- |
| AAPL (tech)       | MSFT, GOOGL, or a tech ETF like QQQ                |
| SPY (S&P 500 ETF) | IVV or VOO (different fund family)                 |
| XOM (energy)      | CVX, SLB, or XLE ETF                               |
| Individual stock  | Sector ETF covering the same industry              |

Always note that substitute suitability depends on investor-specific factors; these are illustrative only.

## Output template

```
Tax-Loss Harvesting Analysis — Source: Longbridge Securities
Date: <today>  Account: US Securities

[Positions with Unrealised Losses]
Symbol   Cost Basis  Current Price  Unreal. Loss  Hold Period  Tax Saving Est.
TSLA.US  $280.00     $210.00        −$7,000       8 months     ~$2,590 (37% rate)
XOM.US   $120.00     $108.00        −$1,200       14 months    ~$240 (20% rate)

[Tax Harvesting Opportunity Analysis (ranked by potential tax saving)]
1. TSLA.US  若实现亏损 $7,000（示例）→ 预计可节省税款约 $2,590（仅为说明税务亏损收割原理，不构成具体操作建议）
   Substitute reference (for wash-sale avoidance illustration): RIVN.US / LCID.US / DRIV ETF (do not repurchase TSLA within 30 days of any sale)
   ⚠️ Wash-sale risk if TSLA was purchased in last 30 days

2. XOM.US   若实现亏损 $1,200（示例）→ 预计可节省税款约 $240（仅供参考）
   Substitute reference: CVX.US or XLE ETF

[Wash-Sale Warnings]
- Check recent purchase dates; do not repurchase within 30 days of sale.
- Purchasing a call option on the sold stock may also trigger wash-sale.

⚠️ 本分析仅供参考，不构成税务建议或投资建议。以上内容仅为说明税务亏损收割原理，不代表对任何具体操作的建议。请咨询持牌税务顾问。投资决策请结合自身风险承受能力独立判断。/ 本分析僅供參考，不構成稅務建議或投資建議。以上內容僅為說明稅務虧損收割原理，不代表對任何具體操作的建議。請諮詢持牌稅務顧問。/ For reference only. Not tax or investment advice. The above examples are for illustrative purposes only and do not constitute specific trading recommendations. Consult a qualified tax professional. Please make investment decisions independently based on your own risk tolerance.
```

## Error handling

| Situation                       | 简体回复                                           | 繁體回復                                           | English reply                                                         |
| ------------------------------- | -------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------- |
| `command not found: longbridge` | 回退到 MCP；若也不可用，请安装 longbridge-terminal | 回退到 MCP；若也不可用，請安裝 longbridge-terminal | Fall back to MCP; if unavailable, install longbridge-terminal.        |
| stderr `not logged in`          | 请运行 `longbridge auth login`（需要 Trade 权限）  | 請運行 `longbridge auth login`（需要 Trade 權限）  | Run `longbridge auth login` with Trade permission.                    |
| No US positions                 | 账户中无美股持仓，税损收割仅适用于美股             | 賬戶中無美股持倉，稅損收割僅適用於美股             | No US positions found; tax-loss harvesting applies to US stocks only. |
| All positions profitable        | 当前所有持仓均为浮盈，无税损收割机会               | 當前所有持倉均為浮盈，無稅損收割機會               | All positions are profitable; no harvesting opportunities.            |
| Cost basis unavailable          | 无法获取持仓成本，请检查账户权限                   | 無法獲取持倉成本，請檢查賬戶權限                   | Cannot retrieve cost basis; check account permissions.                |
