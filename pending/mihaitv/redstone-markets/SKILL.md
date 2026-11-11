---
name: redstone-markets
description: Look up end-of-day performance and risk for US stocks and ETFs, compare tickers, backtest weighted portfolios and screen by metric with Redstone Markets. Use when someone asks how a stock, ETF or portfolio has done, how risky it is, or how two compare.
---

# Redstone Markets

Redstone (redstonemarkets.com) has end-of-day (not real-time) analytics for about 2,900 US-listed stocks (the Russell 1000, the largest foreign companies and every other stock trading $5M+ a day) and about 1,200 US ETFs: YTD, 1-year and 5-year annualized returns, past-year risk (max drawdown, volatility, Sharpe, Sortino, beta and alpha vs SPY), dividend yield, correlations, backtests of hypothetical weighted portfolios, screening, and the public portfolios Redstone's users shared and its model portfolios. Returns are total returns in percent: split-adjusted, with dividends reinvested on the ex-date. Present results as historical data, not investment advice or predictions. Link the Redstone page each result includes.

## MCP server

https://redstonemarkets.com/api/mcp speaks MCP over Streamable HTTP. It is public, read-only and stateless, and needs no account or key. Its tools:

- `get_security_metrics`: one stock or ETF's returns, risk and dividend yield
- `compare_securities`: 2 to 5 stocks or ETFs side by side, with their correlation
- `backtest_portfolio`: a weighted portfolio of 2 to 20 holdings, rebalanced quarterly
- `screen_securities`: stocks or ETFs ranked by a return, risk or yield metric
- `search_portfolios`: the portfolios Redstone's users shared, and its model portfolios
- `get_portfolio`: one shared or model portfolio

## Pages

Every page is public. Request one with `Accept: text/markdown` to get its content as markdown.

- A stock or ETF: https://redstonemarkets.com/dashboard/ticker/{TICKER}
- Two side by side: https://redstonemarkets.com/dashboard/compare/ticker/{A}/ticker/{B}
- A shared or model portfolio: https://redstonemarkets.com/dashboard/portfolio/{id}
- The shared and model portfolios, paged with `?page=n`: https://redstonemarkets.com/portfolios
- Screeners, paged with `?page=n`: https://redstonemarkets.com/screeners/stocks and https://redstonemarkets.com/screeners/etfs
- Guides: https://redstonemarkets.com/learn
- Methodology: https://redstonemarkets.com/about
