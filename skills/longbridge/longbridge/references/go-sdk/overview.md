# Go SDK Overview

**Module:** `github.com/longbridge/openapi-go` v0.21.0
**Docs:** https://longbridge.github.io/openapi/go/

## Install

```bash
go get github.com/longbridge/openapi-go
go get github.com/shopspring/decimal   # price fields use shopspring/decimal (quantities are uint64)
```

## Config

```go
import "github.com/longbridge/openapi-go/config"

// From env: LONGBRIDGE_APP_KEY / LONGBRIDGE_APP_SECRET / LONGBRIDGE_ACCESS_TOKEN
cfg, err := config.New()

// Or set manually
cfg, _ := config.New()
cfg.AppKey = "xxx"
cfg.AppSecret = "xxx"
cfg.AccessToken = "xxx"
```

### OAuth 2.0 (recommended)

```go
import (
    "github.com/longbridge/openapi-go/config"
    "github.com/longbridge/openapi-go/oauth"
)

o := oauth.New("your-client-id").
    OnOpenURL(func(url string) { fmt.Println("Open to authorize:", url) })
if err := o.Build(context.Background()); err != nil { log.Fatal(err) }

cfg, err := config.New(config.WithOAuthClient(o))
```

## Creating Contexts

Every API call takes a `context.Context` as the first argument. Always `Close()` the context when done.

```go
import (
    "github.com/longbridge/openapi-go/quote"
    "github.com/longbridge/openapi-go/trade"
)

quoteCtx, err := quote.NewFromCfg(cfg)
defer quoteCtx.Close()

tradeCtx, err := trade.NewFromCfg(cfg)
defer tradeCtx.Close()
```

## Push Callbacks

Unlike the Rust SDK (channel-based), the Go SDK registers callbacks via `On*` handlers. Register the handler, then subscribe.

```go
quoteCtx.OnQuote(func(e *quote.PushQuote) {
    fmt.Printf("%s last=%v\n", e.Symbol, e.LastDone)
})
quoteCtx.Subscribe(context.Background(),
    []string{"700.HK", "AAPL.US"},
    []quote.SubType{quote.SubTypeQuote, quote.SubTypeDepth},
    true) // isFirstPush: push current snapshot immediately
```

Other quote handlers: `OnDepth`, `OnTrade`, `OnBrokers`.
Trade order updates: `tradeCtx.OnTrade(func(e *trade.PushEvent){...})` after `tradeCtx.Subscribe(ctx, []string{"private"})`.

## Error Handling

Methods return idiomatic Go `(result, error)`. API errors carry a code:

```go
quotes, err := quoteCtx.Quote(context.Background(), []string{"INVALID.XX"})
if err != nil {
    log.Printf("quote failed: %v", err)
}
```

## Quick Example

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/longbridge/openapi-go/config"
    "github.com/longbridge/openapi-go/quote"
)

func main() {
    cfg, err := config.New()
    if err != nil { log.Fatal(err) }

    ctx, err := quote.NewFromCfg(cfg)
    if err != nil { log.Fatal(err) }
    defer ctx.Close()

    quotes, err := ctx.Quote(context.Background(), []string{"700.HK", "AAPL.US"})
    if err != nil { log.Fatal(err) }
    for _, q := range quotes {
        fmt.Printf("%s last=%v\n", q.Symbol, q.LastDone)
    }
}
```
