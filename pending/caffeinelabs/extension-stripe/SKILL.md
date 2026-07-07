---
name: extension-stripe
description: Payment support based on Stripe, supporting credit cards and debit cards
version: 0.1.6
compatibility:
  mops:
    caffeineai-stripe: "~0.1.2"
    caffeineai-http-outcalls: "~0.1.2"
    caffeineai-authorization: "~1.0.0"
caffeineai-subscription: [none]
---

# Stripe Payment Integration
Stripe payment extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds Stripe payment support using HTTP outcalls. The backend manages Stripe configuration, creates checkout sessions, and checks payment status. The frontend handles checkout flow and payment result pages.

# Backend

For Stripe payment integration:

Prerequisite: You must follow [extension-authorization](../extension-authorization/SKILL.md) first, as this integration depends on it.

There is the prefabricated module `mo:caffeineai-stripe/stripe.mo` that that cannot be modified. It provides fundamental functionality for making HTTP GET or PUT requests in the backend.

```mo:caffeineai-stripe/stripe.mo
import OutCall "mo:caffeineai-http-outcalls/outcall";

module {
  public type StripeConfiguration = {
    secretKey : Text;
    allowedCountries : [Text];
  };

  public type ShoppingItem = {
    currency : Text;
    productName : Text;
    productDescription : Text;
    priceInCents : Nat;
    quantity : Nat;
  };

  /// Initiate payment session for shopping items.
  /// Returns Stripe JSON reply message.
  public func createCheckoutSession(configuration : StripeConfiguration, caller : Principal, items : [ShoppingItem], successUrl : Text, cancelUrl : Text, transform : OutCall.Transform) : async Text;
  
  public type StripeSessionStatus = {
    #failed : { error : Text };
    #completed : { response : Text; userPrincipal : ?Text };
  };

  /// Check payment status.
  public func getSessionStatus(configuration : StripeConfiguration, sessionId : Text, transform : OutCall.Transform) : async StripeSessionStatus;
};
```

Usage:

```motoko filepath=src/backend/main.mo
import Stripe "mo:caffeineai-stripe/stripe";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import OutCall "mo:caffeineai-http-outcalls/outcall";
import Map "mo:core/Map";
import Iter "mo:core/Iter";
import Text "mo:core/Text";
import Runtime "mo:core/Runtime";

actor {
    // Include authorization
    let accessControlState = AccessControl.initState();
    include MixinAuthorization(accessControlState, null);

    // Shopping data
    public type Product = {
        id : Text;
        // add custom fields
    };

    let products = Map.empty<Text, Product>();

    public query func getProducts() : async [Product] {
        products.values().toArray();
    };

    public shared ({ caller }) func addProduct(product : Product) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can add products");
        };
        products.add(product.id, product);
    };

    public shared ({ caller }) func updateProduct(product : Product) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can update products");
        };
        products.add(product.id, product);
    };

    public shared ({ caller }) func deleteProduct(productId : Text) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can delete products");
        };
        products.remove(productId);
    };

    // Stripe integration
    var configuration : ?Stripe.StripeConfiguration = null;

    public query func isStripeConfigured() : async Bool {
        configuration != null;
    };

    public shared ({ caller }) func setStripeConfiguration(config : Stripe.StripeConfiguration) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can perform this action");
        };
        configuration := ?config;
    };

    func getStripeConfiguration() : Stripe.StripeConfiguration {
        switch (configuration) {
            case (null) { Runtime.trap("Stripe needs to be first configured") };
            case (?value) { value };
        };
    };

    public func getStripeSessionStatus(sessionId : Text) : async Stripe.StripeSessionStatus {
        await Stripe.getSessionStatus(getStripeConfiguration(), sessionId, transform);
    };

    public shared ({ caller }) func createCheckoutSession(items : [Stripe.ShoppingItem], successUrl : Text, cancelUrl : Text) : async Text {
        await Stripe.createCheckoutSession(getStripeConfiguration(), caller, items, successUrl, cancelUrl, transform);
    };

    public query func transform(input : OutCall.TransformationInput) : async OutCall.TransformationOutput {
        OutCall.transform(input);
    };

    // Add more data and functions as needed
};
```

# Frontend

For Stripe payment integration:

Usage:

1. Implement a PaymentSetup component with:
    * Use `isStripeConfigured()` and `setStripeConfiguration()`
    * Checks whether Stripe payment is configured.
    * If not, opens an admin panel and asks the user to initialze Stripe with `StripeConfiguration`.
      - Stripe secret key
      - List of allowed countries, notation ["US", "CA", "GB"] etc., see the Stripe documentation.
    * Do not show the payment setup when it has already been configured!

2. Implement a checkout hook:
    * Note that JSON parsing of backend `createCheckoutSession` result is needed.
    * Validate that the parsed session includes a non-empty `url`. If missing, throw an error and do not redirect.
    
    ```
    import { useMutation } from '@tanstack/react-query';
    import { useActor } from '@caffeineai/core-infrastructure';
    import { ShoppingItem } from '../backend';

    export type CheckoutSession = {
        id: string;
        url: string;
    };

    export function useCreateCheckoutSession() {
        const { actor } = useActor();

        return useMutation({
            mutationFn: async (items: ShoppingItem[]): Promise<CheckoutSession> => {
                if (!actor) throw new Error('Actor not available');
                const baseUrl = `${window.location.protocol}//${window.location.host}`;
                const successUrl = `${baseUrl}/payment-success`;
                const cancelUrl = `${baseUrl}/payment-failure`;
                const result = await actor.createCheckoutSession(items, successUrl, cancelUrl);
                // JSON parsing is important!
                const session = JSON.parse(result) as CheckoutSession;
                if (!session?.url) {
                    throw new Error('Stripe session missing url');
                }
                return session;
            }
        });
    }
    ```

3. Implement a Payment component with:
    * `useCreateCheckoutSession()`
    * Pass `ShoppingItem[]` as input.
    * Anaylze the `CheckoutSession` result.
    * Redirect webpage to url in `CheckoutSession`: This allows the user to complete the payment.
    * Do NOT use router navigation for the Stripe URL. Use `window.location.href`.
    * Never navigate to `/undefined`; if `session.url` is missing, show an error and stop.

    ```
    const session = await createCheckoutSession.mutateAsync(shoppingItems);
    if (!session?.url) throw new Error('Stripe session missing url');
    window.location.href = session.url;
    ```

4. Implement a PaymentSuccess and PaymentFailure component to handle payment success or failure, respectively.

5. Route two specific paths to the payment status components:
   * Path "/payment-success" to PaymentSuccess.
   * Path "/payment-failure" to PaymentFailure.
   You need to use @tanstack router.

6. The admin view offers a menu to configure Stripe. If not yet configured, it asks the admin to configure Stripe on login.

Side note: Make sure that product images are properly rendered and resized inside the product canvas.
