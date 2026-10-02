# Migration examples

Minimal, self-contained examples. Each file below is what you would create directly in `src/backend/migrations/` with a UTC-timestamped filename. Inline both old AND new types — frozen migration files must be self-contained because the chain replays forever.

## Example 1: Add a required field to each record

**Old actor:** has `taxPayers : Map<Nat, { firstName; lastName; address }>`.

**New actor:** same map but each record has an extra required field `zipCode : Text`.

**`src/backend/migrations/YYYYMMDD_HHMMSS.mo`:**

```motoko project=add-required-field filepath=src/backend/migrations/20260101_000000.mo
import Map "mo:core/Map";
import Nat "mo:core/Nat";

module {
  type OldTaxPayer = { firstName : Text; lastName : Text; address : Text };
  type NewTaxPayer = {
    firstName : Text;
    lastName : Text;
    address : Text;
    zipCode : Text;
  };
  type OldActor = {
    var taxPayers : Map.Map<Nat, OldTaxPayer>;
    var taxPayerId : Nat;
  };
  type NewActor = {
    var taxPayers : Map.Map<Nat, NewTaxPayer>;
    var taxPayerId : Nat;
  };

  public func migration(old : OldActor) : NewActor {
    let taxPayers = old.taxPayers.map<Nat, OldTaxPayer, NewTaxPayer>(
      func(_id, p) { { p with zipCode = "" } }
    );
    { var taxPayers; var taxPayerId = old.taxPayerId };
  };
};

```

List every other stable field (e.g. `var taxPayerId`) in both `OldActor` and `NewActor` even when the body just copies them through.

---

## Example 2: Map over a collection and change type (Bool → variant)

**Old actor:** `todos : Map<Nat, { taskId; description; var completed : Bool }>`, `var nextTaskId`.

**New actor:** same keys but each task has `due : Time.Time` and `var status : { #pending; #inProgress; #completed }` instead of `completed`.

**`src/backend/migrations/YYYYMMDD_HHMMSS.mo`:**

```motoko project=map-collection filepath=src/backend/migrations/20260101_000000.mo
import Map "mo:core/Map";
import Nat "mo:core/Nat";
import Time "mo:core/Time";

module {
  type TaskID = Nat;
  type OldTask = { taskId : TaskID; description : Text; var completed : Bool };
  type Status = { #pending; #inProgress; #completed };
  type NewTask = {
    taskId : TaskID;
    description : Text;
    due : Time.Time;
    var status : Status;
  };
  type OldActor = {
    var todos : Map.Map<TaskID, OldTask>;
    var nextTaskId : TaskID;
  };
  type NewActor = {
    var todos : Map.Map<TaskID, NewTask>;
    var nextTaskId : TaskID;
  };

  public func migration(old : OldActor) : NewActor {
    let todos = old.todos.map<TaskID, OldTask, NewTask>(
      func(_, task) {
        {
          taskId = task.taskId;
          description = task.description;
          due = 0;
          var status = if (task.completed) { #completed } else { #pending };
        };
      }
    );
    { var todos; var nextTaskId = old.nextTaskId };
  };
};

```

---

## Example 3: Add an optional field to each record

**Old actor:** tasks have `due` and `var status`. **New actor:** same plus `var assignee : ?Principal`.

**Migration body (snippet):**

<!-- motoko-check:skip -->

```motoko
let todos = old.todos.map<TaskID, OldTask, NewTask>(
  func(_, task) {
    { task with var status = task.status; var assignee = null : ?Principal };
  }
);
{ var todos; var nextTaskId = old.nextTaskId };

```

Inline `OldTask`, `NewTask`, `OldActor`, `NewActor` in the migration file — even if `NewTask` matches a current `Types.Task` today, importing it breaks this frozen migration the moment a future draft changes `Task`.

