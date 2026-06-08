# Go SDK — Types & Enums

Quote types live in package `quote`, trade types in package `trade`.

## quote.SubType — subscription channels

```go
quote.SubTypeQuote    // real-time quote
quote.SubTypeDepth    // level-2 order book
quote.SubTypeBrokers  // HK broker queue
quote.SubTypeTrade    // tick-by-tick trades
```

## quote.Period

```go
quote.PeriodOneMinute    quote.PeriodFiveMinute   quote.PeriodFifteenMinute
quote.PeriodThirtyMinute quote.PeriodSixtyMinute
quote.PeriodDay          quote.PeriodWeek         quote.PeriodMonth   quote.PeriodYear
```

## quote.AdjustType

```go
quote.AdjustTypeNo       // unadjusted
quote.AdjustTypeForward  // forward-adjusted
```

## quote.CalcIndex (common)

```go
quote.CalcIndexLastDone   quote.CalcIndexChangeRate   quote.CalcIndexVolume
quote.CalcIndexTurnover   quote.CalcIndexPeTTMRatio   quote.CalcIndexPbRatio
quote.CalcIndexTotalMarketValue   quote.CalcIndexImpliedVolatility
quote.CalcIndexDELTA  quote.CalcIndexGAMMA  quote.CalcIndexTHETA  quote.CalcIndexVEGA
```

## trade.OrderType

```go
trade.OrderTypeLO   trade.OrderTypeELO  trade.OrderTypeMO   trade.OrderTypeAO
trade.OrderTypeALO  trade.OrderTypeODD  trade.OrderTypeLIT  trade.OrderTypeMIT
trade.OrderTypeTSLPAMT  trade.OrderTypeTSLPPCT  trade.OrderTypeTSMAMT  trade.OrderTypeTSMPCT
trade.OrderTypeSLO
```

## trade.OrderSide

```go
trade.OrderSideBuy
trade.OrderSideSell
```

## trade.TimeType

```go
trade.TimeTypeDay  // day order
trade.TimeTypeGTC  // good-til-canceled
trade.TimeTypeGTD  // good-til-date (set ExpireDate)
```

## trade.OutsideRTH (US only)

```go
trade.OutsideRTHOnly     // RTH_ONLY — regular hours only
trade.OutsideRTHAny      // ANY_TIME — pre & post market
trade.OutsideRTHUnknown  // default when the order is not a US stock
```

> Unlike the Rust SDK, the Go SDK has **no** `Overnight` value here. Enable overnight trading at the config level, not via `OutsideRTH`.

## trade.OrderStatus (common)

```go
trade.OrderNewStatus           trade.OrderFilledStatus       trade.OrderPartialFilledStatus
trade.OrderCanceledStatus      trade.OrderRejectedStatus     trade.OrderExpiredStatus
trade.OrderWaitToNew           trade.OrderPendingCancelStatus
```

## trade.Currency

```go
trade.CurrencyHKD  trade.CurrencyUSD  trade.CurrencyCNH  trade.CurrencyDefault
```

## Decimal

Price fields use `github.com/shopspring/decimal` (quantities are plain `uint64`):

```go
import "github.com/shopspring/decimal"

price := decimal.NewFromFloat(50.0)
price2, _ := decimal.NewFromString("50.00")
```

> Full enum list: GoDoc https://longbridge.github.io/openapi/go/ or source `quote/types.go`, `trade/types.go`.
