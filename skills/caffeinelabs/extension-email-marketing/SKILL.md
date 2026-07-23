---
name: extension-email-marketing
description: Send personalised marketing emails to subscribers with an unsubscribe link.
version: 0.1.5
compatibility:
  mops:
    caffeineai-email-marketing: "~0.1.1"
    caffeineai-authorization: "~0.1.1"
    caffeineai-email-verification: "~0.1.1"
caffeineai-subscription: [plus, pro]
---

# Email — Marketing
Marketing email extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds direct marketing email support with subscriber management, topic-based subscriptions, and automatic unsubscribe links. Requires email verification before users can receive marketing emails.

# Backend

## This component is for sending direct marketing emails and managing subscribers to marketing topics.

- Users MUST have verified their email address AND MUST be subscribed to a marketing topic before they can receive marketing emails on that topic
- Marketing emails MUST contain an unsubscribe link which will unsubscribe the user from the given topic
- This component depends on the [extension-email-verification](../extension-email-verification/SKILL.md) for verifying email addresses, be sure to check that too.

### To subscribe users to marketing topics and manage lists of subscribers

- Use the prefabricated module `mo:caffeineai-email-marketing/subscribers.mo` which cannot be modified.
- Marketing email subscribers MUST be handled solely through this subscribers module
- Do NOT also store a subscribed status against user profiles

```mo:caffeineai-email-marketing/subscribers.mo
module {
  public type State = {
    var topics : Map.Map<Nat, TopicRecord>;
    var topicsByName : Map.Map<Text, Nat>;
  };

  // Add a new topic by name or get an existing topic if it already exists. Returns the topic ID.
  public func addTopic(state : State, name : Text) : Nat;

  // Rename a topic. Returns false if a topic with the new name already exists or the topic ID does not exist.
  public func renameTopic(state : State, topicId : Nat, newName : Text) : Bool;

  // Remove a topic. Also removes all subscribers from that topic.
  public func removeTopic(state : State, topicId : Nat);

  // List all topics (id, name).
  public func listTopics(state : State) : [Topic];

  // Get a topic ID by name
  public func getTopicId(state : State, name : Text) : ?Nat;

  // Get a topic name by ID
  public func getTopicName(state : State, topicId : Nat) : ?Text;

  // Add a subscriber to a topic. Returns false if the topic doesn't exist
  public func add(state : State, topicId : Nat, email : Text) : Bool;

  // Remove a subscriber from a topic
  public func remove(state : State, topicId : Nat, email : Text);

  // Remove a subscriber from all topics
  public func removeFromAllTopics(state : State, email : Text);

  // List all subscribers alongside their verification status for a given topic. Returns null if the topic doesn't exist.
  public func list(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : ?[(Text, Bool)];

  // List all verified subscribers for a given topic. Returns null if the topic doesn't exist.
  public func verified(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : ?[Text];

  // Return whether a subscriber is subscribed to a topic
  public func isSubscribed(state : State, topicId : Nat, email : Text) : Bool;

  // List all topics a subscriber is subscribed to.
  public func listTopicsForSubscriber(state : State, email : Text) : [Topic];

  // Returns the count of subscribers for a given topic
  public func count(state : State, topicId : Nat) : Nat;

  // Returns the count of verified subscribers for a given topic
  public func verifiedCount(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : Nat;
};
```

### To handle the unsubscribe link

Use the prefabricated module `caffeineai-email-marketing/unsubscribeMixin.mo` which cannot be modified.

The MixinEmailUnsubscribe module handles calls to the unsubscribe link to unsubscribe an email address from a topic.

```mo:caffeineai-email-marketing/unsubscribeMixin.mo
import MixinEmailUnsubscribe "mo:caffeineai-email-marketing/unsubscribeMixin";
```

### For sending direct marketing emails from the backend

- This component depends on the `email` component for sending email addresses.
- Use the sendMarketingEmail function.
- This MUST be used alongside the subscribers.mo module and unsubscribeMixin.mo module
- The `recipients` argument is an array of email addresses, where for each email an optional array of substitution name/value pairs can be specified.
  - These substitutions allow the email to be personalised for each recipient.
  - If the email body contains the substitution name in double curly braces it is replaced by the substitution value in the email to that recipient.
- It returns a Result which is #ok if the email is sent successfully otherwise #err(error) with the error text.
- Ensure the placeholder text {{UNSUBSCRIBE_URL}} is appended to the htmlBody if not already present. This will be replaced automatically by the system with a specific unsubscribe url for each recipient.

```mo:caffeineai-email/emailClient.mo
module {
  public type BroadcastEmailRecipient = {
    email : Text;
    substitutions : ?[(Text, Text)];
  };

  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendMarketingEmail(
    topicId : Nat,
    fromUsername : Text,
    recipients : [BroadcastEmailRecipient],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### Example usage for an app which can send marketing emails to users who are subscribed to topics managed by the admin

```motoko filepath=src/backend/main.mo
import Array "mo:core/Array";
import Runtime "mo:core/Runtime";
import Option "mo:core/Option";
import Principal "mo:core/Principal";
import Iter "mo:core/Iter";
import Map "mo:core/Map";
import Set "mo:core/Set";
import Text "mo:core/Text";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import EmailClient "mo:caffeineai-email/emailClient";
import MixinEmailUnsubscribe "mo:caffeineai-email-marketing/unsubscribeMixin";
import EmailSubscribers "mo:caffeineai-email-marketing/subscribers";
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

actor {
  public type UserProfile = {
    name : Text;
    email : Text;
  };

  // Include authorization component
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState);

  // Store a map of caller principal to UserProfile
  let userProfiles = Map.empty<Principal, UserProfile>();

  // Store a set of emails for uniqueness check
  let emails = Set.empty<Text>();

  // Stores which emails are verified
  let verifiedEmails = VerifiedEmails.new();

  // In this example we use a single hardcoded topic.
  // In general there could be CRUD endpoints for the admin to manage email subscription topics.
  let newsletterTopic = "Newsletter";

  // Store the email subscribers per topic
  let emailSubscribers = EmailSubscribers.new([newsletterTopic]);

  // Include this mixin to handle the unsubscribe link which updates the EmailSubscribers state
  include MixinEmailUnsubscribe(emailSubscribers);

  // Include this mixin to handle the verification link which updates the VerifiedEmails state
  include MixinEmailVerification(verifiedEmails);

  func getUserInternal(caller : Principal) : UserProfile {
    switch (userProfiles.get(caller)) {
      case (null) { Runtime.trap("User profile does not exist!") };
      case (?userProfile) { userProfile };
    };
  };

  public shared ({ caller }) func registerUser(name : Text, email : Text) : async () {
    // Check if the user already exists
    if (userProfiles.containsKey(caller)) {
      Runtime.trap("User already registered");
    };
    // Check if the email is already used
    if (emails.contains(email)) {
      Runtime.trap("Email already taken");
    };
    // Add a user record
    userProfiles.add(
      caller,
      {
        name;
        email;
      },
    );
    emails.add(email);
    // Subscribe the user to the Newsletter topic by default
    switch (EmailSubscribers.getTopicId(emailSubscribers, newsletterTopic)) {
      case (null) { Runtime.trap("Newsletter topic not found") };
      case (?topicId) {
        ignore EmailSubscribers.add(emailSubscribers, topicId, email);
      };
    };
    // Send a verification email
    let result = await EmailClient.sendVerificationEmail(
      "no-reply",
      [email],
      "Welcome to Our Service",
      "Hello " # name # ",<br><br>Thank you for registering with our service.<br><br>Please <a href=\"{{VERIFICATION_URL}}\">click here</a> to verify your email address.<br><br>By clicking on the verification link you also agree to sign-up to the monthly Newsletter which you can unsubscribe from at any time.<br><br>Best regards,<br>The Team",
    );
    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send verification email: " # error);
      };
    };
  };

  public shared ({ caller }) func addTopic(name : Text) : async Nat {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add topics");
    };
    EmailSubscribers.addTopic(emailSubscribers, name);
  };

  public shared ({ caller }) func removeTopic(topicId : Nat) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can remove topics");
    };
    EmailSubscribers.removeTopic(emailSubscribers, topicId);
  };

  public shared ({ caller }) func renameTopic(topicId : Nat, newName : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can rename topics");
    };
    let success = EmailSubscribers.renameTopic(emailSubscribers, topicId, newName);
    if (not success) {
      Runtime.trap("Failed to rename topic");
    };
  };

  public shared ({ caller }) func subscribeToTopic(topicId : Nat) : async () {
    let userProfile = getUserInternal(caller);
    ignore EmailSubscribers.add(emailSubscribers, topicId, userProfile.email);
  };

  public shared ({ caller }) func unsubscribeFromTopic(topicId : Nat) : async () {
    let userProfile = getUserInternal(caller);
    EmailSubscribers.remove(emailSubscribers, topicId, userProfile.email);
  };

  public shared ({ caller }) func sendMarketingEmail(topicId : Nat, subject : Text, htmlBody : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can send the newsletter");
    };
    // Get the array of subscriber emails that have been verified
    let recipientEmails = switch (EmailSubscribers.verified(emailSubscribers, verifiedEmails, topicId)) {
      case (null) {
        Runtime.trap("No verified subscribers found for newsletter topic");
      };
      case (?recipientEmails) { recipientEmails };
    };
    if (recipientEmails.size() == 0) {
      Runtime.trap("No verified subscribers found for newsletter topic");
    };
    // Ensure the email body contains the unsubscribe link placeholder
    let finalHtmlBody = if (htmlBody.contains(#text "{{UNSUBSCRIBE_URL}}")) {
      htmlBody;
    } else {
      htmlBody # "<br><br>To unsubscribe <a href=\"{{UNSUBSCRIBE_URL}}\">click here</a>";
    };
    // For each recipient specify the NAME substitution to personalise the email
    let recipients = recipientEmails.filterMap(
      func(email) {
        switch (userProfiles.values().find(func(user) { user.email == email })) {
          case (?user) { ?{ email; substitutions = ?[("NAME", user.name)] } };
          case (null) { null };
        };
      }
    );
    let result = await EmailClient.sendMarketingEmail(
      topicId,
      "no-reply",
      recipients,
      subject,
      finalHtmlBody,
    );
    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send newsletter: " # error);
      };
    };
  };

  public query ({ caller }) func listTopics() : async [EmailSubscribers.Topic] {
    EmailSubscribers.listTopics(emailSubscribers);
  };

  // Admin function to list topic subscribers and whether the email is verified or not
  public query ({ caller }) func listSubscribers(topicId : Nat) : async [(Text, Bool)] {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can list topic subscribers");
    };
    EmailSubscribers.list(emailSubscribers, verifiedEmails, topicId).get([]);
  };

  public query ({ caller }) func isCallerSubscribedToTopic(topicId : Nat) : async Bool {
    let userProfile = getUserInternal(caller);
    EmailSubscribers.listTopicsForSubscriber(emailSubscribers, userProfile.email).find(
      func(topic) { topic.id == topicId }
    ).isSome();
  };

  public query ({ caller }) func isCallerEmailVerified() : async Bool {
    let userProfile = getUserInternal(caller);
    VerifiedEmails.contains(verifiedEmails, userProfile.email);
  };
};
```
