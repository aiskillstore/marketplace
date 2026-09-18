---
name: connector-weatherapi
description: >-
  MANDATORY recipe for every Caffeine build that reads weather data from a
  canister. The supported path is the `weatherapi-client` mops package
  (WeatherAPI.com) over outbound HTTPS, authenticated with a query-string API
  key. Hand-rolling `ic.http_request` calls to `api.weatherapi.com` is a
  FORBIDDEN anti-pattern — it bypasses the non-replicated-outcall safeguard
  (WeatherAPI bodies carry per-request clocks and fail consensus), the generated
  JSON decoding, and the API-key handling. Load this skill whenever the user,
  spec, or any prior task mentions weather, forecast, temperature, humidity,
  wind, rain, snow, conditions, sunrise, sunset, moon phase, astronomy,
  timezone, IP geolocation, marine or tide forecasts, or location autocomplete —
  and BEFORE writing any code that touches a weather endpoint.
version: 0.2.0
caffeineai-subscription: [none]
compatibility:
  mops:
    weatherapi-client: "~0.2.0"
---

# Weather data with `weatherapi-client`

Motoko bindings for [WeatherAPI.com](https://www.weatherapi.com/), generated
from its OpenAPI spec. All nine operations live in a single module,
**`Apis/APIsApi`**, and all nine are read-only `GET`s.

# Backend

A canister that reads the current temperature and a three-day maximum series.
Non-replicated is the default, so you only supply the key:

```motoko filepath=src/backend/main.mo
import { realtimeWeather; forecastWeather } "mo:weatherapi-client/Apis/APIsApi";
import { type Config; defaultConfig } "mo:weatherapi-client/Config";
import Array "mo:core/Array"; // in scope so `days.map(…)` dot notation resolves

persistent actor {
  // The key is a query-string credential. Hold it in a stable variable set by
  // an admin call; never hard-code it in source.
  func config(apiKey : Text) : Config = { defaultConfig with auth = ?#apiKey apiKey };

  // `q` is any WeatherAPI location query: "Zurich", "47.37,8.55", a postcode,
  // an IATA code, or "auto:ip".
  public func currentTempC(apiKey : Text, q : Text) : async ?Float {
    let res = await* realtimeWeather(config apiKey, q, "");
    do ? { res.current!.temp_c! };
  };

  // Daily maxima for the next three days.
  public func maxTempsC(apiKey : Text, q : Text) : async [?Float] {
    let res = await* forecastWeather(config apiKey, q, #_3_, "", 0, 0, "", "no", "no", 0);
    let ?forecast = res.forecast else return [];
    let ?days = forecast.forecastday else return [];
    days.map(func(d) = do ? { d.day!.maxtemp_c! });
  };
}
```

## The nine operations

| Function | Endpoint | Returns |
|---|---|---|
| `realtimeWeather(cfg, q, lang)` | `/current.json` | `RealtimeWeather200Response` |
| `forecastWeather(cfg, q, days, dt, unixdt, hour, lang, alerts, aqi, tp)` | `/forecast.json` | `ForecastWeather200Response` |
| `historyWeather(cfg, q, dt, unixdt, endDt, unixendDt, hour, lang)` | `/history.json` | `FutureWeather200Response` |
| `futureWeather(cfg, q, dt, lang)` | `/future.json` | `FutureWeather200Response` |
| `marineWeather(cfg, q, days, dt, unixdt, hour, lang)` | `/marine.json` | `MarineWeather200Response` |
| `astronomy(cfg, q, dt)` | `/astronomy.json` | `Astronomy200Response` |
| `timeZone(cfg, q)` | `/timezone.json` | `Location` |
| `ipLookup(cfg, q)` | `/ip.json` | `Ip` |
| `searchAutocompleteWeather(cfg, q)` | `/search.json` | `[Search]` |

`days` is an enum, not a number: `ForecastWeatherDaysParameter` is `#_1_` … `#_14_`
and `MarineWeatherDaysParameter` is `#_1_` … `#_7_` (the underscores are how the
generator escapes numeric enum values — `#_3_`, not `#_3` or `3`).

## API key setup

1. Sign up at [weatherapi.com](https://www.weatherapi.com/signup.aspx) — the
   free tier covers current weather, 3-day forecast, astronomy, timezone,
   search and IP lookup. History, future, marine and 14-day forecasts need a
   paid plan and return **403** on free keys.
2. Copy the key from the dashboard and pass it as `auth = ?#apiKey key`.
3. The client appends it as `?key=…` (WeatherAPI takes no `Authorization`
   header), so **it appears in the request URL**. Keep it in a stable variable
   written by an admin-only call, and never log the built URL.

## Calls are non-replicated by default

The package ships `is_replicated = ?false` in `defaultConfig`, and that is a
*correctness* requirement here, not just a cost saving. Every response carries
per-request clocks — `Location.localtime` / `localtime_epoch`,
`Current.last_updated` / `last_updated_epoch` — which change second to second. A
*replicated* outcall has every subnet node issue its own request and demands
bit-identical bodies, so those fields would break consensus on most calls while
burning ~13× the cycles. You don't set it yourself; the default is correct.

Override with `is_replicated = ?true` only together with a `transform` that
strips the volatile fields.

## Everything is optional

WeatherAPI marks no response field required, so the generated models are
all-optional: `RealtimeWeather200Response.current : ?Current`,
`Current.temp_c : ?Float`, and so on. Reach through them with a `do ?` block
(`do ? { res.current!.temp_c! }`) rather than nested `switch`es, and decide what
an absent field means for your caller — the API omits fields your plan does not
cover (for example `air_quality` without the `aqi=yes` parameter).

## Empty string and zero mean "omit"

Optional query parameters are dropped when they are `""` or `0`, because
WeatherAPI rejects empty `lang=` and zero-valued numerics. So passing `""` for
`lang`, `dt`, `alerts`, `aqi` and `0` for `unixdt`, `tp` is how you say "not
supplied" — there is no `?Text` parameter to leave `null`.

One consequence worth knowing: **`hour = 0` does not select midnight**, it omits
the `hour` filter entirely and you get the whole day's hourly array. Filter the
returned `hour : ?[ForecastForecastdayInnerHourInner]` yourself if you need
00:00.

## Errors

Non-2xx responses and decode failures `throw Error.reject(…)`. The client is
generated with `diagnostics`, so the message is
`HTTP <status> body[<n>B]=<first 100 chars>: <reason>` — enough to tell a 401
(bad key) from a 403 (endpoint not on your plan) from a 400 (`q` not resolvable)
without extra logging. Catch with `try`/`catch` and surface
`Error.message(err)`.
