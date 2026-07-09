---
name: extension-email-verification
description: Support for sending an email with a link the recipient can click to prove they own the email address.
version: 0.1.5
compatibility:
  mops:
    caffeineai-email-verification: "~0.1.1"
    caffeineai-email: "~0.1.1"
caffeineai-subscription: [plus, pro]
---

# Email — Verification
Email verification extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds email address verification via a click-to-verify link. The `MixinEmailVerification` handles the verification callback; `verifiedEmails` tracks verified addresses.

# Backend

## This component is for sending an email to users with a verification link which the user can click to prove they own the email address.

### To check if an email address has been verified

Use the prefabricated module `mo:caffeineai-email-verification/verifiedEmails.mo` which cannot be modified.

```mo:caffeineai-email-verification/verifiedEmails.mo
module {
  public type State = {
    var verifiedEmails : Set.Set<Text>;
  };

  public func new() : State {
    {
      var verifiedEmails = Set.empty<Text>();
    };
  };

  public func contains(state : State, email : Text) : Bool;

  public func iter(state : State) : Iter.Iter<Text>;

  public func size(state : State) : Nat;
};
```

To check whether an email is verified use the `contains` function. Do NOT try to track the email verification status independently by storing it against the user profile.

### To handle the verification link

Use the prefabricated module `mo:caffeineai-email-verification/verificationMixin.mo` which cannot be modified.

The MixinEmailVerification handles calls to the verification link to verify an email address.

```mo:caffeineai-email-verification/verificationMixin.mo
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
```

### For sending users a verification email

- This extension depends on the [extension-email](../extension-email/SKILL.md) for sending emails.
- Use the sendVerificationEmail function. 
- It returns a SendResult which is #ok if the email is sent successfully otherwise #err(error) with the error text. 
- Each recipient receives an individual email with a specific verification link for them
- The htmlBody MUST contain the placeholder text {{VERIFICATION_URL}}

```mo:caffeineai-email/emailClient.mo
module {
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendVerificationEmail(
    fromUsername : Text,
    recipients : [Text],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### Example usage with endpoints for registering a user and for checking whether a user is verified.

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Runtime "mo:core/Runtime";
import Principal "mo:core/Principal";
import Text "mo:core/Text";
import EmailClient "mo:caffeineai-email/emailClient";
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

actor {
  // Stores which emails are verified
  let verifiedEmails = VerifiedEmails.new();

  // User profiles storage
  let users = Map.empty<Principal, User>();

  // Email to principal mapping for uniqueness check
  let emailToPrincipal = Map.empty<Text, Principal>();

  // Handles the verification link and updates the verifiedEmails store
  include MixinEmailVerification(verifiedEmails);

  type User = {
    name : Text;
    email : Text;
  };

  public shared ({ caller }) func registerUser(email : Text, name : Text) : async () {
    if (users.containsKey(caller)) {
      Runtime.trap("User already registered");
    };
    if (emailToPrincipal.containsKey(email)) {
      Runtime.trap("Email already registered");
    };

    let user : User = {
      name;
      email;
    };
    users.add(caller, user);
    emailToPrincipal.add(email, caller);
    let result = await EmailClient.sendVerificationEmail(
      "no-reply",
      [email],
      "Welcome to Our Service",
      "Hello " # name # ",<br><br>Thank you for registering with our service. Please <a href=\"{{VERIFICATION_URL}}\">click here</a> to verify your email address<br><br>Best regards,<br>The Team",
    );

    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Couldn't send verification email: " # error);
      };
    };
  };

  public shared ({ caller }) func isEmailVerified() : async Bool {
    switch (users.get(caller)) {
      case (null) {
        Runtime.trap("User not registered");
      };
      case (?user) {
        VerifiedEmails.contains(verifiedEmails, user.email);
      };
    };
  };
};
```

# Frontend

If there is a UI for the admin to enter the content of a verification email then indicate that the placeholder text {{VERIFICATION_URL}} must be present in the email body.
