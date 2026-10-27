# Framework setup

The snippets below come from the README of each LogBrew SDK package. Each
package README has the full options, privacy limits, and recovery steps.
Read it before you change defaults. All packages are in
[LogBrewCo/sdk](https://github.com/LogBrewCo/sdk).

Install only the packages that the app needs: the core package for the
runtime, then the framework package.

## Install commands

| Runtime or framework | Install | Package README |
| --- | --- | --- |
| Node.js | `npm install @logbrew/sdk @logbrew/node` | [`@logbrew/node`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-node) |
| Express | `npm install @logbrew/sdk @logbrew/node @logbrew/express express` | [`@logbrew/express`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-express) |
| Fastify | `npm install @logbrew/sdk @logbrew/node @logbrew/fastify fastify` | [`@logbrew/fastify`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-fastify) |
| NestJS | `npm install @logbrew/sdk @logbrew/node @logbrew/nestjs @nestjs/common @nestjs/core @nestjs/platform-express reflect-metadata rxjs` | [`@logbrew/nestjs`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-nestjs) |
| Next.js | `npm install @logbrew/sdk @logbrew/node @logbrew/next next react react-dom` | [`@logbrew/next`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-next) |
| React | `npm install @logbrew/sdk @logbrew/react react` | [`@logbrew/react`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-react) |
| Browser | `npm install @logbrew/sdk @logbrew/browser` | [`@logbrew/browser`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-browser) |
| Vue | `npm install @logbrew/sdk @logbrew/vue` | [`@logbrew/vue`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-vue) |
| Angular | `npm install @logbrew/sdk @logbrew/angular` | [`@logbrew/angular`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-angular) |
| Svelte and SvelteKit | `npm install @logbrew/sdk @logbrew/browser @logbrew/svelte` | [`@logbrew/svelte`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-svelte) |
| React Native | `npm install @logbrew/sdk @logbrew/react-native` | [`@logbrew/react-native`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-react-native) |
| Python | `python3 -m pip install logbrew-sdk` | [`logbrew-sdk`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_py) |
| FastAPI | `python3 -m pip install logbrew-fastapi` | [`logbrew-fastapi`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_fastapi) |
| Django | `python3 -m pip install logbrew-sdk logbrew-django` | [`logbrew-django`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_django) |
| Flask | `python3 -m pip install logbrew-sdk logbrew-flask` | [`logbrew-flask`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_flask) |
| Go | `go get github.com/LogBrewCo/sdk/go/logbrew@latest` | [`go/logbrew`](https://github.com/LogBrewCo/sdk/tree/main/go/logbrew) |
| Gin | `go get github.com/LogBrewCo/sdk/go/logbrew/gin@latest` | [`go/logbrew/gin`](https://github.com/LogBrewCo/sdk/tree/main/go/logbrew/gin) |
| Ruby and Rails | `gem "logbrew-sdk"` in the Gemfile, then `bundle install` | [`logbrew-sdk`](https://github.com/LogBrewCo/sdk/tree/main/ruby/logbrew-ruby) |
| PHP, Laravel, Symfony | `composer require logbrew/sdk` | [`logbrew/sdk`](https://github.com/LogBrewCo/sdk/tree/main/php/logbrew-php) |
| Rust | `cargo add logbrew --features http` | [`logbrew`](https://github.com/LogBrewCo/sdk/tree/main/rust/logbrew) |
| Java and Spring | `co.logbrew:logbrew-sdk` from Maven Central | [`logbrew-java`](https://github.com/LogBrewCo/sdk/tree/main/java/logbrew-java) |
| Kotlin and Android | `co.logbrew:logbrew-kotlin` from Maven Central | [`logbrew-kotlin`](https://github.com/LogBrewCo/sdk/tree/main/kotlin/logbrew-kotlin) |
| .NET | `dotnet add package LogBrew` | [`LogBrew`](https://github.com/LogBrewCo/sdk/tree/main/dotnet/logbrew-dotnet) |
| ASP.NET Core | `dotnet add package LogBrew.AspNetCore` | [`LogBrew.AspNetCore`](https://github.com/LogBrewCo/sdk/tree/main/dotnet/logbrew-dotnet/src/LogBrew.AspNetCore) |
| Swift and Apple apps | Add `https://github.com/LogBrewCo/sdk.git` with SwiftPM and use the `LogBrew` product | [`logbrew-swift`](https://github.com/LogBrewCo/sdk/tree/main/swift/logbrew-swift) |
| Unity | `co.logbrew.unity` | [`logbrew-unity`](https://github.com/LogBrewCo/sdk/tree/main/unity/logbrew-unity) |
| C | Source and header client | [`logbrew-c`](https://github.com/LogBrewCo/sdk/tree/main/c/logbrew-c) |
| C++ | CMake `FetchContent`; `logbrew setup --json` prints the block | [`logbrew-cpp`](https://github.com/LogBrewCo/sdk/tree/main/cpp/logbrew-cpp) |

## Express

```js
import express from "express";
import { logbrewMiddleware } from "@logbrew/express";

const app = express();
const logbrewServerApiKey = process.env.LOGBREW_SERVER_API_KEY;

if (logbrewServerApiKey) {
  app.use(logbrewMiddleware({
    serverApiKey: logbrewServerApiKey,
    onCaptureError(error) {
      console.error("LogBrew request capture failed", error);
    }
  }));
}
```

Register the error handler after the routes and before the app's own error
response handler:

```js
import { logbrewErrorHandler } from "@logbrew/express";

if (logbrewServerApiKey) {
  app.use(logbrewErrorHandler({
    serverApiKey: logbrewServerApiKey,
    onCaptureError(error) {
      console.error("LogBrew error capture failed", error);
    }
  }));
}
```

## Next.js (App Router)

```ts
// instrumentation.ts
import { createLogBrewNextRequestErrorHandler } from "@logbrew/next/instrumentation";

export const onRequestError = createLogBrewNextRequestErrorHandler({
  serverApiKey: process.env.LOGBREW_SERVER_API_KEY,
  onCaptureError(error) {
    console.error("LogBrew request-error capture failed", error);
  }
});
```

Issues get the release and environment from `LOGBREW_RELEASE` and
`LOGBREW_ENVIRONMENT`, or from `VERCEL_GIT_COMMIT_SHA` and `VERCEL_ENV`.
`LOGBREW_SERVICE_NAME` sets the service.

## React

Use a key of kind `browser` in `clientKey`.

```js
import React from "react";
import {
  LogBrewErrorBoundary,
  LogBrewProvider,
  createLogBrewReactClient
} from "@logbrew/react";

const client = createLogBrewReactClient({
  clientKey: "LOGBREW_CLIENT_KEY"
});

export function App() {
  return React.createElement(
    LogBrewProvider,
    { client },
    React.createElement(
      LogBrewErrorBoundary,
      {
        fallback: ({ error, resetError }) => React.createElement(
          "button",
          { onClick: resetError },
          `Retry after ${error instanceof Error ? error.message : "React error"}`
        ),
        metadata: { section: "checkout" },
        onError: (_error, _info, event) => {
          console.info("captured LogBrew issue", event.id);
        }
      },
      React.createElement(CheckoutButton)
    )
  );
}
```

## FastAPI

```python
import logging
import os

from fastapi import FastAPI
from logbrew_fastapi import init_logbrew

app = FastAPI()
logbrew = init_logbrew(
    app,
    api_key=os.environ["LOGBREW_API_KEY"],
    service_name="checkout-api",
)
client = logbrew.client
logger = logging.getLogger("checkout-api")
logger.addHandler(logbrew.logging_handler)
```

`environment` defaults to `LOGBREW_ENVIRONMENT`, then `production`. The
release comes from `LOGBREW_RELEASE` when it is set.

## Django

```python
# settings.py
MIDDLEWARE = [
    "logbrew_django.LogBrewDjangoMiddleware",
    *MIDDLEWARE,
]
```

```python
# app startup code, for example at the end of settings.py
import logging
import os

from logbrew_django import configure_logbrew, get_active_logbrew_trace
from logbrew_sdk import HttpTransport, LogBrewClient, LogBrewLoggingHandler

client = LogBrewClient.create(
    api_key=os.environ["LOGBREW_SERVER_API_KEY"],
)
logger = logging.getLogger("checkout-api")
logger.addHandler(LogBrewLoggingHandler(client, metadata={"service": "checkout-api"}))
configure_logbrew(client=client, transport=HttpTransport(), service_name="checkout-api")
```

Set `LOGBREW_ENVIRONMENT` and `LOGBREW_RELEASE` in the app's environment.

## Flask

```python
from flask import Flask
from logbrew_flask import init_logbrew

app = Flask(__name__)
logbrew = init_logbrew(app)
client = logbrew.client
```

The initializer reads `LOGBREW_SERVER_API_KEY`, `LOGBREW_SERVICE_NAME`,
`LOGBREW_ENVIRONMENT`, and `LOGBREW_RELEASE`.

## Gin

Catch `SIGTERM` so that queued events are sent when the host stops the
service. Go does not run deferred calls when a signal ends the process.

```go
package main

import (
  "context"
  "errors"
  "net/http"
  "os"
  "os/signal"
  "syscall"
  "time"

  "github.com/LogBrewCo/sdk/go/logbrew"
  logbrewgin "github.com/LogBrewCo/sdk/go/logbrew/gin"
  "github.com/gin-gonic/gin"
)

func main() {
  ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
  defer stop()

  transport, err := logbrew.NewHTTPTransport(logbrew.HTTPTransportConfig{})
  must(err)
  client, err := logbrew.NewAutomaticClient(logbrew.Config{
    APIKey: os.Getenv("LOGBREW_SERVER_API_KEY"),
  }, logbrew.AutomaticDeliveryConfig{
    Transport: transport,
  })
  must(err)

  middleware, err := logbrewgin.NewMiddleware(logbrewgin.Config{
    Client:                   client,
    CaptureRequestMetrics:   true,
    CaptureServerErrorIssues: true,
    Metadata: map[string]any{
      "service":     "checkout-api",
      "environment": "production",
    },
  })
  must(err)

  router := gin.New()
  router.Use(gin.Recovery(), middleware)

  server := &http.Server{Addr: ":8080", Handler: router}
  go func() {
    if err := server.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
      panic(err)
    }
  }()

  <-ctx.Done()
  stop()
  shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
  defer cancel()
  serverErr := server.Shutdown(shutdownCtx)
  _, err = client.Shutdown(nil)
  must(errors.Join(serverErr, err))
}

func must(err error) {
  if err != nil {
    panic(err)
  }
}
```

## Rails

```ruby
# Gemfile
gem "logbrew-sdk", "~> 0.1.17"
```

```bash
bundle install
export LOGBREW_SERVER_API_KEY="your project-scoped server ingest key"
bin/rails server
```

No initializer is needed. Without `LOGBREW_SERVER_API_KEY`, the integration
stays off. `LOGBREW_SERVICE_NAME`, `LOGBREW_ENVIRONMENT`, and
`LOGBREW_RELEASE` set the service, environment, and release.

## ASP.NET Core

Set `LOGBREW_SERVER_API_KEY`, `LOGBREW_SERVICE_NAME`,
`LOGBREW_ENVIRONMENT`, and `LOGBREW_RELEASE` outside source control. Place
the middleware after routing:

```csharp
using LogBrew;

var builder = WebApplication.CreateBuilder(args);
builder.AddLogBrew();

var app = builder.Build();
app.UseRouting();
app.UseLogBrew();
app.MapGet("/", () => "ok");
app.Run();
```

## Other runtimes

Open the package README from the table. It shows the install and setup
code, and most READMEs have a "Read Events Back" section. Use the HTTP
transport of the released package; a recording or preview transport sends
nothing.
