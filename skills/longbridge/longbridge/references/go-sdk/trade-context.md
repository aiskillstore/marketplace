# Go SDK — TradeContext

Every method takes `context.Context` first and returns `(result, error)`.

## Submit Order

Build a `*trade.SubmitOrder` and pass it. Price fields use `shopspring/decimal`; quantities are `uint64`.

```go
import "github.com/shopspring/decimal"

order := &trade.SubmitOrder{
    Symbol:            "700.HK",
    OrderType:         trade.OrderTypeLO,
    Side:              trade.OrderSideBuy,
    SubmittedQuantity: 200,
    SubmittedPrice:    decimal.NewFromFloat(50.0), // required for LO/ELO/ALO/ODD/LIT
    TimeInForce:       trade.TimeTypeDay,
    // Optional per order type:
    // TriggerPrice    decimal.Decimal  // LIT / MIT
    // TrailingAmount  decimal.Decimal  // TSLPAMT / TSMAMT
    // TrailingPercent decimal.Decimal  // TSLPPCT / TSMPCT
    // LimitOffset     decimal.Decimal  // required for TSLPAMT / TSLPPCT
    // ExpireDate      *time.Time       // required when TimeInForce = GTD
    // OutsideRTH      trade.OutsideRTHAny  // US pre/post market
    // Remark          string
}
orderId, err := tradeCtx.SubmitOrder(context.Background(), order)
```

## Replace / Cancel

```go
err := tradeCtx.ReplaceOrder(c, &trade.ReplaceOrder{
    OrderId:  "709043056541253632",
    Quantity: 100,
    Price:    decimal.NewFromFloat(100.0),
})

err := tradeCtx.CancelOrder(c, "709043056541253632")
```

## Query Orders & Executions

```go
// Today's orders (params optional, nil for all)
orders, err := tradeCtx.TodayOrders(c, &trade.GetTodayOrders{
    Symbol: "700.HK",
    Status: []trade.OrderStatus{trade.OrderFilledStatus, trade.OrderNewStatus},
})

// Historical orders (does not include today) — also returns hasMore.
// NOTE: GetHistoryOrders.StartAt/EndAt are int64 Unix seconds (use .Unix()).
orders, hasMore, err := tradeCtx.HistoryOrders(c, &trade.GetHistoryOrders{
    Symbol:  "700.HK",
    StartAt: start.Unix(),
    EndAt:   end.Unix(),
})

// Today's fills
execs, err := tradeCtx.TodayExecutions(c, &trade.GetTodayExecutions{Symbol: "700.HK"})

// Historical fills — NOTE: GetHistoryExecutions.StartAt/EndAt are time.Time (differs from GetHistoryOrders)
hexecs, err := tradeCtx.HistoryExecutions(c, &trade.GetHistoryExecutions{Symbol: "700.HK", StartAt: start, EndAt: end})
```

## Account & Positions

```go
// Currency is type trade.Currency (trade.CurrencyHKD / CurrencyUSD / CurrencyCNH); zero value = all
balances, err := tradeCtx.AccountBalance(c, &trade.GetAccountBalance{Currency: trade.CurrencyHKD}) // []*AccountBalance
positions, err := tradeCtx.StockPositions(c, []string{"700.HK"})                       // []*StockPositionChannel
```

## Order Push

```go
tradeCtx.OnTrade(func(e *trade.PushEvent) {
    fmt.Printf("order update: %+v\n", e)
})
_, err := tradeCtx.Subscribe(context.Background(), []string{"private"})
```

> Method set mirrors the Rust SDK. Check GoDoc https://longbridge.github.io/openapi/go/
> or source `trade/context.go` / `trade/requests.go` for exact request structs.
