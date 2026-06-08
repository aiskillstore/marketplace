# Go SDK — QuoteContext

Every method takes `context.Context` first and returns `(result, error)`.

## Subscriptions

```go
// Subscribe (isFirstPush=true sends current snapshot immediately)
err := ctx.Subscribe(c, []string{"700.HK"}, []quote.SubType{quote.SubTypeQuote, quote.SubTypeDepth}, true)

// Unsubscribe (unSubAll=true clears everything)
err := ctx.Unsubscribe(c, false, []string{"700.HK"}, []quote.SubType{quote.SubTypeQuote})
```

Register push handlers **before** subscribing:

```go
ctx.OnQuote(func(e *quote.PushQuote)   { /* ... */ })
ctx.OnDepth(func(e *quote.PushDepth)   { /* ... */ })
ctx.OnTrade(func(e *quote.PushTrade)   { /* ... */ })
ctx.OnBrokers(func(e *quote.PushBrokers){ /* ... */ })
```

## Market Data

```go
// Real-time quote
quotes, err := ctx.Quote(c, []string{"700.HK", "AAPL.US"})         // []*SecurityQuote

// Static info: name, exchange, currency, lot size...
infos, err := ctx.StaticInfo(c, []string{"700.HK"})                // []*StaticInfo

// Level-2 order book
depth, err := ctx.Depth(c, "700.HK")                                // *SecurityDepth (.Ask / .Bid)

// Tick trades (count, max 1000)
trades, err := ctx.Trades(c, "700.HK", 50)                          // []*Trade

// Intraday line
lines, err := ctx.Intraday(c, "700.HK")                             // []*IntradayLine
```

## Candlesticks

```go
// Recent N candles
sticks, err := ctx.Candlesticks(c, "700.HK", quote.PeriodDay, 100, quote.AdjustTypeNo) // []*Candlestick

// History by offset (isForward=true: look forward from dateTime)
sticks, err := ctx.HistoryCandlesticksByOffset(c, "700.HK", quote.PeriodDay, quote.AdjustTypeNo, true, &dateTime, 100)

// History by date range
sticks, err := ctx.HistoryCandlesticksByDate(c, "700.HK", quote.PeriodDay, quote.AdjustTypeNo, &startDate, &endDate)
```

## Other

```go
ctx.OptionChainExpiryDateList(c, "AAPL.US")
ctx.OptionChainInfoByDate(c, "AAPL.US", &date)
ctx.WarrantIssuers(c)
ctx.TradingDays(c, market, &begin, &end)
ctx.CapitalFlow(c, "700.HK")
ctx.CapitalDistribution(c, "700.HK")
ctx.CalcIndex(c, []string{"700.HK"}, []quote.CalcIndex{quote.CalcIndexLastDone, quote.CalcIndexPeTTMRatio}) // method is singular
ctx.WatchedGroups(c)  // list watchlist groups; also CreateWatchlistGroup / UpdateWatchlistGroup / DeleteWatchlistGroup
```

> Method set mirrors the Rust SDK. When unsure of a signature, check the GoDoc:
> https://longbridge.github.io/openapi/go/ or the source `quote/context.go`.
