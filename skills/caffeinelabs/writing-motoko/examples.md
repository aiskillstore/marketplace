# Motoko Development Examples

Complete working examples demonstrating Motoko patterns and features.

## Complete Actor Example

A full-featured actor using modern Motoko patterns:

```motoko project=complete-actor filepath=src/backend/main.mo
import Map "mo:core/Map";
import List "mo:core/List";
import Queue "mo:core/Queue";
import Stack "mo:core/Stack";
import Array "mo:core/Array";
import Iter "mo:core/Iter";
import Nat "mo:core/Nat";
import Text "mo:core/Text";
import Principal "mo:core/Principal";

actor {
  // Stable state — types only, values come from the migration chain
  let inventory : Map.Map<Nat, Text>;
  let orders : List.List<Nat>;
  let taskQueue : Queue.Queue<Text>;
  let history : Stack.Stack<Text>;
  let scores : [var Nat];

  // Private helpers
  func formatItem(key : Nat, item : Text) : Text {
    "Item " # key.toText() # ": " # item;
  };

  // Update function with caller
  public shared ({ caller }) func initialize() : async () {
    inventory.add(0, "Init by: " # caller.toText());
    inventory.add(1, "Apple");
    inventory.add(2, "Banana");
    orders.add(100);
    orders.add(200);
    taskQueue.pushBack("task1");
    taskQueue.pushBack("task2");
    history.push("action1");
    scores[0] := 10;
    scores[1] := 20;
  };

  // Query function
  public shared query func getData() : async Text {
    var result = "";

    // Iterate map
    for ((key, value) in inventory.entries()) {
      result := result # formatItem(key, value) # "\n";
    };

    // Process list with chaining
    let largeOrders = orders.values().filter(func x = x > 150).map(func x = x * 2).toArray();
    result := result # "Large orders: " # largeOrders.toText() # "\n";

    result;
  };
};

```

## Principled Architecture Example

Complete example following the architecture pattern:

### types.mo

```motoko project=architecture filepath=src/backend/types.mo
import List "mo:core/List";

module {
  // Entities
  public type UserId = Principal;

  public type User = {
    id : UserId; // Immutable field
    var username : Text; // Mutable field
    var bio : Text;
    var isActive : Bool;
  };

  public type Post = {
    id : Nat; // Immutable field
    author : User; // Immutable field
    var title : Text; // Mutable field
    var content : Text;
    var published : Bool;
  };

  // Shared (immutable) views for the API boundary.
  // User/Post hold `var` fields, so they are NOT shared — never return them directly.
  public type UserView = {
    id : UserId;
    username : Text;
    bio : Text;
    isActive : Bool;
  };

  public type PostView = {
    id : Nat;
    author : UserView;
    title : Text;
    content : Text;
    published : Bool;
  };

};

```

### lib/User.mo

```motoko project=architecture filepath=src/backend/lib/User.mo
import Types "../types";

module {
  public type User = Types.User;

  public func new(id : Types.UserId, username : Text) : User {
    {
      id = id;
      var username = username;
      var bio = "";
      var isActive = true;
    };
  };

  // Dot notation method
  public func updateBio(self : User, newBio : Text) {
    if (newBio.size() > 280) return;
    self.bio := newBio;
  };

  public func ban(self : User) {
    self.isActive := false;
  };

  public func isValid(self : User) : Bool {
    self.username.size() > 0 and self.isActive
  };

  // Immutable projection for the API boundary
  public func toView(self : User) : Types.UserView {
    { id = self.id; username = self.username; bio = self.bio; isActive = self.isActive };
  };
};

```

### lib/Post.mo

```motoko project=architecture filepath=src/backend/lib/Post.mo
import Types "../types";
import UserLib "User";

module {
  public type Post = Types.Post;

  public func new(id : Nat, author : Types.User, title : Text) : Post {
    {
      id;
      author;
      var title = title;
      var content = "";
      var published = false;
    };
  };

  public func publish(self : Post) {
    if (self.content.size() > 0) {
      self.published := true;
    };
  };

  public func setContent(self : Post, content : Text) {
    self.content := content;
  };

  // Immutable projection for the API boundary (UserLib import enables `self.author.toView()`)
  public func toView(self : Post) : Types.PostView {
    {
      id = self.id;
      author = self.author.toView();
      title = self.title;
      content = self.content;
      published = self.published;
    };
  };
};

```

### mixins/Auth.mo

```motoko project=architecture filepath=src/backend/mixins/Auth.mo
import Types "../types";
import UserLib "../lib/User";
import List "mo:core/List";

// In mixins, use {caller} destructuring in the function signature
mixin (users : List.List<Types.User>) {

  func findUser(p : Principal) : ?Types.User {
    users.find(func(u) { u.id == p });
  };

  public shared ({ caller }) func register(username : Text) : async Bool {
    switch (findUser(caller)) {
      case (?_) return false;
      case (null) {
        let newUser = UserLib.new(caller, username);
        users.add(newUser);
        return true;
      };
    };
  };

  public shared query ({ caller }) func getProfile() : async ?Types.UserView {
    switch (findUser(caller)) {
      case (?user) { ?user.toView() };
      case (null) { null };
    };
  };

  public shared ({ caller }) func updateBio(newBio : Text) : async Bool {
    switch (findUser(caller)) {
      case (null) false;
      case (?user) {
        user.updateBio(newBio); // Dot notation!
        true;
      };
    };
  };
};

```

### mixins/Blog.mo

```motoko project=architecture filepath=src/backend/mixins/Blog.mo
import Types "../types";
import PostLib "../lib/Post";
import Iter "mo:core/Iter";
import List "mo:core/List";
import Runtime "mo:core/Runtime";

mixin (
  users : List.List<Types.User>,
  posts : List.List<Types.Post>,
  state : { var nextPostId : Nat },
) {

  public shared ({ caller }) func createPost(title : Text) : async Nat {
    let author = users.find(func(u) { u.id == caller })
      ?? Runtime.trap("User not registered");

    let pid = state.nextPostId;
    state.nextPostId += 1;

    let newPost = PostLib.new(pid, author, title);
    posts.add(newPost);
    pid;
  };

  public shared ({ caller }) func publishPost(postId : Nat) : async Bool {
    let maybePost = posts.find(func(p) { p.id == postId });
    switch (maybePost) {
      case (null) { false };
      case (?post) {
        if (post.author.id != caller) { return false };
        post.publish(); // Dot notation!
        true;
      };
    };
  };

  public query func getAllPosts() : async [Types.PostView] {
    posts.values().map(func(p) { p.toView() }).toArray();
  };
};

```

### mixins/Admin.mo

```motoko project=architecture filepath=src/backend/mixins/Admin.mo
import Types "../types";
import UserLib "../lib/User";
import List "mo:core/List";
import Principal "mo:core/Principal";

mixin (users : List.List<Types.User>, posts : List.List<Types.Post>) {

  // Hardcoded admin (in production, use proper authorization)
  transient let ADMIN = Principal.fromText("aaaaa-aa"); // constant — `transient` keeps it out of stable state

  func isAdmin(caller : Principal) : Bool {
    caller == ADMIN;
  };

  public shared ({ caller }) func adminBanUser(targetId : Principal) : async Bool {
    if (not isAdmin(caller)) return false;

    let target = users.find(func(u) { u.id == targetId });
    switch (target) {
      case (?user) {
        user.ban(); // Dot notation!
        true;
      };
      case (null) { false };
    };
  };

  public query ({ caller }) func getStats() : async {
    userCount : Nat;
    postCount : Nat;
  } {
    if (not isAdmin(caller)) {
      return { userCount = 0; postCount = 0 };
    };
    {
      userCount = users.size();
      postCount = posts.size();
    };
  };
};

```

### main.mo

```motoko project=architecture filepath=src/backend/main.mo
import List "mo:core/List";
import Types "types";
import AuthMixin "mixins/Auth";
import BlogMixin "mixins/Blog";
import AdminMixin "mixins/Admin";

actor Main {

  let users : List.List<Types.User>;
  let posts : List.List<Types.Post>;
  let state : { var nextPostId : Nat };

  include AuthMixin(users);
  include BlogMixin(users, posts, state);
  include AdminMixin(users, posts);
};

```

### migrations/20260101_000000.mo

The first migration supplies the initial values. `OldActor = {}` because no prior version exists. Types are inlined — migration files may only import from `mo:core/...`. See `migrating-motoko-actors` for full rules.

```motoko
import List "mo:core/List";
import Principal "mo:core/Principal";

module {
  // Inlined copies of Types.User / Types.Post (migration files cannot import project types)
  type User = {
    id : Principal;
    var username : Text;
    var bio : Text;
    var isActive : Bool;
  };

  type Post = {
    id : Nat;
    author : User;
    var title : Text;
    var content : Text;
    var published : Bool;
  };

  type OldActor = {};

  type NewActor = {
    users : List.List<User>;
    posts : List.List<Post>;
    state : { var nextPostId : Nat };
  };

  public func migration(_ : OldActor) : NewActor {
    {
      users = List.empty();
      posts = List.empty();
      state = { var nextPostId = 0 };
    };
  };
};

```

## Iterator Examples

### Basic Iteration

```motoko project=iterators filepath=src/backend/main.mo
import Array "mo:core/Array";
import Iter "mo:core/Iter";
import Nat "mo:core/Nat";
import Bool "mo:core/Bool";

actor {
  let numbers : [Nat];

  public query func demonstrateIterators() : async Text {
    var output = "";

    // Map and filter with chaining
    let doubled = numbers.values().map(func x = x * 2).filter(func x = x > 10).toArray();
    output := output # "Doubled > 10: " # doubled.toText() # "\n";

    // Convert to iterator, chain, convert back
    let processed = numbers.values().map(func x = x * 3).filter(func x = x % 2 == 0).toArray();
    output := output # "Processed: " # processed.toText() # "\n";

    // Fold
    let sum = numbers.values().foldLeft(0, func(acc, x) = acc + x);
    output := output # "Sum: " # sum.toText() # "\n";

    // Find
    switch (numbers.find(func x = x > 5)) {
      case (?found) {
        output := output # "Found: " # found.toText() # "\n";
      };
      case (null) {};
    };

    // Any / All
    let hasLarge = numbers.any(func x = x > 8);
    let allPositive = numbers.all(func x = x > 0);
    output := output # "Has large: " # hasLarge.toText() # "\n";
    output := output # "All positive: " # allPositive.toText() # "\n";

    output;
  };
};

```

### Custom Iterator

```motoko project=custom-iterator filepath=src/backend/main.mo
import Iter "mo:core/Iter";

actor {
  // Fibonacci iterator
  func fibonacci(n : Nat) : Iter.Iter<Nat> {
    var count = 0;
    var prev = 0;
    var curr = 1;

    object {
      public func next() : ?Nat {
        if (count >= n) return null;
        count += 1;

        if (count == 1) return ?0;
        if (count == 2) return ?1;

        let next = prev + curr;
        prev := curr;
        curr := next;
        ?prev;
      };
    };
  };

  public query func getFibonacci() : async [Nat] {
    fibonacci(10).toArray();
  };
};

```

## Map Examples

### Complex Key Types

```motoko project=complex-key filepath=src/backend/main.mo
import Map "mo:core/Map";
import Order "mo:core/Order";
import Text "mo:core/Text";
import Int "mo:core/Int";
import Iter "mo:core/Iter";

actor {
  type Point = { x : Int; y : Int };

  // Module with compare for automatic inference
  module Point {
    public func compare(a : Point, b : Point) : Order.Order {
      switch (Int.compare(a.x, b.x)) {
        case (#equal) { Int.compare(a.y, b.y) };
        case (other) { other };
      };
    };
  };

  // Stable state — initial value comes from the migration chain
  let pointMap : Map.Map<Point, Text>;

  public func addPoint(x : Int, y : Int, pointLabel : Text) : async () {
    pointMap.add({ x = x; y = y }, pointLabel); // Point.compare inferred!
  };

  public query func getPoint(x : Int, y : Int) : async ?Text {
    pointMap.get({ x; y });
  };

  public query func getAllPoints() : async [(Point, Text)] {
    pointMap.entries().toArray();
  };
};

```

### Map Transformation

```motoko project=map-transform filepath=src/backend/main.mo
import Map "mo:core/Map";
import Nat "mo:core/Nat";
import Text "mo:core/Text";
import Iter "mo:core/Iter";
import Order "mo:core/Order";

actor {
  public type Score = {
    name : Text;
    score : Nat;
  };

  module Score {
    public func compare(score1 : Score, score2 : Score) : Order.Order {
      Nat.compare(score1.score, score2.score);
    };
  };

  // Stable state — initial value comes from the migration chain
  let scores : Map.Map<Text, Nat>;

  public func addScore(score : Score) : async () {
    scores.add(score.name, score.score);
  };

  public query func getTopScores(threshold : Nat) : async [Score] {
    let filteredScores = scores.entries().filterMap(
      func((name, score)) {
        if (score > threshold) {
          ?{ name; score };
        } else {
          null;
        };
      }
    );
    filteredScores.sort().toArray();
  };

  public query func doubleAllScores() : async [Score] {
    scores.entries().map(func((name, score)) { { name; score = score * 2 } }).toArray();
  };
};

```

### Safe Division Pattern

<!-- motoko-check:skip -->

```motoko
import Runtime "mo:core/Runtime";
import someModule "../lib/someModule";

actor {
  public func safeDivide(a : Nat, b : Nat) : async Nat {
    if (b == 0) {
      Runtime.trap("Division by zero is not defined");
    } else {
      (a / b);
    };
  };

  // Inter-canister calls that trap will cause the entire function to trap
  public func callOtherCanister() : async Text {
    try {
      // If someModule.method() traps, this will trap too, so you need to wrap it in try catch
      let result = await someModule.method();
    } catch (error) {
      "Canister call failed. ";
    };
  };
};

```

## Timer Example

```motoko project=timer filepath=src/backend/main.mo
import Timer "mo:core/Timer";
import Time "mo:core/Time";
import List "mo:core/List";

actor {
  // Stable state — initial values come from the migration chain
  let logs : List.List<(Int, Text)>;
  var timerId : Nat;

  func logEvent(message : Text) {
    logs.add((Time.now(), message));
  };

  public func startPeriodicCleanup() : async () {
    timerId := Timer.recurringTimer<system>(
      #seconds(3600), // Every hour
      func() : async () {
        let now = Time.now();
        let oneHourAgo = now - 3_600_000_000_000; // 1 hour in nanoseconds

        // Remove old logs
        let newLogs = logs.filter(func((timestamp, logText)) { timestamp > oneHourAgo });
        logs.clear();
        logs.addAll(newLogs.values());
        logEvent("Cleanup completed");
      },
    );
  };

  public func stopPeriodicCleanup() : async () {
    Timer.cancelTimer(timerId);
  };

  public query func getLogs() : async [(Int, Text)] {
    logs.toArray();
  };
};

```

These examples demonstrate real-world Motoko patterns and can be adapted for various use cases.

## Full-Stack Example: Motoko to Frontend

This example shows the complete round-trip from a Motoko backend to the generated TypeScript bindings to frontend usage. Always follow this pattern: write backend first, then use the generated `backend.d.ts` as the source of truth for frontend code.

### Motoko Backend (src/backend/main.mo)

```motoko project=fullstack filepath=src/backend/main.mo
import List "mo:core/List";
import Principal "mo:core/Principal";
import Time "mo:core/Time";

actor Main {

  type TodoItem = {
    id : Nat;
    title : Text;
    completed : Bool;
    createdAt : Int;
    owner : Principal;
  };

  // Stable state — initial values come from src/backend/migrations/*.mo
  let todos : List.List<TodoItem>;
  var nextId : Nat;

  public shared ({ caller }) func addTodo(title : Text) : async Nat {
    let id = nextId;
    nextId += 1;
    todos.add({
      id = id;
      title = title;
      completed = false;
      createdAt = Time.now();
      owner = caller;
    });
    id;
  };

  public shared query ({ caller }) func getMyTodos() : async [TodoItem] {
    todos.filter(func(t) { t.owner == caller }).toArray();
  };

  public shared ({ caller }) func toggleTodo(todoId : Nat) : async Bool {
    switch (todos.find(func(t) { t.id == todoId and t.owner == caller })) {
      case (?todo) {
        let idx = switch (todos.findIndex(func(t) { t.id == todoId })) {
          case (?i) { i };
          case (null) { return false };
        };
        todos.put(idx, { todo with completed = not todo.completed });
        true;
      };
      case (null) { false };
    };
  };
};

```

### Migration (src/backend/migrations/20260101_000000.mo)

```motoko
import List "mo:core/List";
import Principal "mo:core/Principal";

module {
  // Inlined copy of TodoItem — migration files cannot import project types
  type TodoItem = {
    id : Nat;
    title : Text;
    completed : Bool;
    createdAt : Int;
    owner : Principal;
  };

  type OldActor = {};

  type NewActor = {
    todos : List.List<TodoItem>;
    var nextId : Nat;
  };

  public func migration(_ : OldActor) : NewActor {
    {
      todos = List.empty();
      var nextId = 0;
    };
  };
};

```

