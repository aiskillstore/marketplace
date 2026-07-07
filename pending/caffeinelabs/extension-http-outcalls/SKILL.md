---
name: extension-http-outcalls
description: HTTP outcalls performed by the backend canister (not in the frontend).
version: 0.1.6
compatibility:
  mops:
    caffeineai-http-outcalls: "~0.1.2"
caffeineai-subscription: [none]
---

# HTTP Outcalls
HTTP outcalls extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds the ability to make HTTP GET and POST requests from the backend canister. Useful for integrating with external APIs and services.

# Backend

For HTTP outcalls that must be performed in the backend:

There is the prefabricated module `mo:caffeineai-http-outcalls/outcall.mo` that that cannot be modified. It provides fundamental functionality for making HTTP GET or PUT requests in the backend.

```mo:caffeineai-http-outcalls/outcall
module {
  public type TransformationInput = {
    context : Blob;
    response : IC.HttpRequestResult;
  };
  public type TransformationOutput = IC.HttpRequestResult;
  public type Transform = query TransformationInput -> async TransformationOutput;
  public type Header = {
    name: Text;
    value: Text;
  };

  // Helper function for the transform callback used by the IC on HTTP outcalls.
  public func transform(input : TransformationInput) : TransformationOutput;

  // HTTP GET request with a transform callback function.
  public func httpGetRequest(url : Text, extraHeaders: [Header], transform : Transform) : async Text;

  // HTTP POST request, specifying a transform callback.
  public func httpPostRequest(url : Text, extraHeaders: [Header], body : Text, transform : Transform) : async Text;
};
```

Usage for GET:

```motoko filepath=src/backend/main.mo
import OutCall "mo:caffeineai-http-outcalls/outcall";

actor {
  public query func transform(input: OutCall.TransformationInput) : async OutCall.TransformationOutput {
    OutCall.transform(input);
  };

  func makeGetOutcall(url: Text) : async Text {
    await OutCall.httpGetRequest(url, [], transform);
  };
};
```

Hint: JSON parsing is not directly supported in Motoko. Better tunnel JSON to frontend for parsing.

POST usage is analogous.
