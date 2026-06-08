# Go SDK — Content (News, Filings, Topics)

News and community topics live in package `content` (`ContentContext`); regulatory filings are on `QuoteContext`. Every method takes `context.Context` first and returns `(result, error)`.

## ContentContext

```go
import "github.com/longbridge/openapi-go/content"

contentCtx, err := content.NewFromCfg(cfg)   // or content.NewFromEnv()
```

### News & Topics

```go
news, err := contentCtx.News(c, "TSLA.US")      // []*content.NewsItem
topics, err := contentCtx.Topics(c, "700.HK")   // []*content.TopicItem
```

`NewsItem` and `TopicItem` share the same shape:
`Id`, `Title`, `Description`, `Url`, `PublishedAt time.Time`, `CommentsCount`, `LikesCount`, `SharesCount`.

## Filings (via QuoteContext)

Filings are **not** on `ContentContext` — they live on `quote.QuoteContext`:

```go
filings, err := quoteCtx.Filings(c, "AAPL.US")  // []*quote.FilingItem
```

`FilingItem`: `Id`, `Title`, `Description`, `FileName`, `FileUrls []string`, `PublishAt time.Time`
(note: `PublishAt`, not `PublishedAt` as on news/topics).

## Quick Example

```go
news, err := contentCtx.News(context.Background(), "TSLA.US")
if err != nil { log.Fatal(err) }
for _, n := range news {
    fmt.Printf("%s  %s  (%s)\n", n.PublishedAt.Format("2006-01-02"), n.Title, n.Url)
}
```

## Community Topics (write)

Beyond the read methods above, the Go `ContentContext` also exposes community-write APIs the Rust SDK does not:
`TopicDetail`, `MyTopics`, `CreateTopic`, `ListTopicReplies`, `CreateTopicReply`.

> Method set and request structs: GoDoc https://longbridge.github.io/openapi/go/
> or source `content/context.go` / `content/types.go`.
