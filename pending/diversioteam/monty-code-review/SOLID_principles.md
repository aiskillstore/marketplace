# SOLID Principles Reference

Reference this document when checking code for SOLID violations or when designing new
features in Django4Lyfe. Each principle includes patterns, anti-patterns, and review
checklists with Django4Lyfe-specific examples.

---

## Dependency Inversion Principle (DIP)

### Core Concept

High-level modules should not depend on low-level modules. Both should depend on
abstractions. In Django4Lyfe, this is implemented using:

1. **Protocol classes** - Define abstract interfaces using `typing.Protocol`
2. **Factory type aliases** - Callables that construct implementations
3. **Optional injection** - Accept factories as optional parameters with sensible defaults

### When to Apply

- Background tasks (cron jobs) that use services or clients
- Services that interact with external systems (Slack, Teams, APIs)
- Any code where you want to decouple the "what" from the "how" for testability

### When NOT to Apply

Monty's taste: **simple > clever**. Do not reach for Protocol + Factory when:

- **Single implementation** - If there's only one concrete class and no realistic
  prospect of alternatives, direct instantiation is simpler and clearer.
- **Internal helpers** - Private/internal functions that won't be mocked in tests
  don't need injection; just call them directly.
- **Simple, deterministic logic** - Pure functions or small utilities that have no
  side effects and are trivially testable without mocks.
- **Ad-hoc or one-off scripts** - Short-lived code that won't be reused or
  extensively tested rarely benefits from the abstraction overhead. (Note:
  long-lived management commands that are part of the application should follow
  normal app patterns, including DIP where appropriate.)
- **Premature abstraction** - If you're adding a Protocol "just in case" without
  a concrete testing or extensibility need today, you're adding complexity for
  no immediate benefit. YAGNI applies.

**Rule of thumb:** If you can write a clear, focused test without injecting a mock,
you probably don't need DIP. Add the abstraction when the pain of tight coupling
actually manifests (e.g., tests become brittle, patching internals is messy, or
you genuinely need multiple implementations).

### Pattern: Protocol + Factory for Testable Task Injection

#### Step 1: Define a Protocol for the Dependency

```python
from typing import Protocol

class SlackReminderBotProtocol(Protocol):
    """Protocol for bots that can send Slack survey reminders."""

    def send_reminder(self, session: SlackSurveySession) -> bool:
        """Send a reminder for a single Slack survey session."""
```

#### Step 2: Define a Factory Type Alias

```python
from collections.abc import Callable

#: Callable that constructs a reminder bot for a Slack workspace.
SlackReminderBotFactory = Callable[[SlackWorkspace], SlackReminderBotProtocol]
```

#### Step 3: Accept Factory as Optional Parameter in Task

```python
from collections.abc import Callable, Iterable

@optimo_job("optimo_core_default", timeout=300)
def send_survey_reminders(
    *,
    workspaces: Iterable[SlackWorkspace] | None = None,
    bot_factory: SlackReminderBotFactory | None = None,
) -> int:
    """Send reminders for all eligible incomplete Slack survey sessions.

    Args:
        workspaces: Optional iterable of workspaces to process. If None,
            queries all active workspaces with ``send_reminders=True``.
        bot_factory: Optional callable used to construct the reminder bot
            for each workspace. Defaults to ``SlackSurveyBot`` and is
            primarily overridden in tests.
    """
    reminder_count: int = 0
    if workspaces is None:
        workspaces = SlackWorkspace.objects.filter(is_active=True, send_reminders=True)

    if bot_factory is None:
        bot_factory = SlackSurveyBot  # Default concrete implementation

    for workspace in workspaces:
        bot = bot_factory(workspace)
        # ... use bot.send_reminder(session) ...
```

#### Step 4: Test with Injected Factory (No Patching Needed)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
def test_send_survey_reminders_uses_injected_factory_and_workspaces(self):
    """Slack task should honor injected factory and explicit workspaces.

    Note: No @patch required - DIP lets us inject a mock factory directly.
    """
    mock_bot = MagicMock()
    mock_bot.send_reminder.return_value = True

    # Factory that returns our mock bot for any workspace
    def mock_bot_factory(workspace: SlackWorkspace) -> SlackReminderBotProtocol:
        return mock_bot

    reminder_count = send_survey_reminders(
        workspaces=[self.workspace],
        bot_factory=mock_bot_factory,
    )

    assert reminder_count == 1
    mock_bot.send_reminder.assert_called_once()
```

### Real-World Example: Teams Reminder Service

The same pattern applied to a more complex service:

```python
from typing import Protocol, TypedDict

class ReminderResult(TypedDict):
    """Reminder send results for a single Teams workspace."""
    sent: int
    failed: int
    abandoned: int
    expired: int


class ReminderServiceProtocol(Protocol):
    """Protocol for services that can send Teams survey reminders."""

    def send_bulk_reminders(self) -> ReminderResult:
        """Send reminders and return bulk counts."""


#: Callable that constructs a reminder service for a Teams workspace.
ReminderServiceFactory = Callable[[TeamsWorkspace], ReminderServiceProtocol]


@optimo_job("optimo_core_default", timeout=300)
def send_teams_survey_reminders(
    *,
    workspaces: Iterable[TeamsWorkspace] | None = None,
    reminder_service_factory: ReminderServiceFactory | None = None,
) -> int:
    """Send reminders for incomplete Teams survey sessions.

    Args:
        workspaces: Optional iterable of workspaces to process. If None,
            queries all active workspaces with ``send_reminders=True``.
        reminder_service_factory: Optional callable used to construct the
            reminder service for each workspace. Defaults to ``ReminderService``
            and is primarily overridden in tests.
    """
    total_sent: int = 0
    if workspaces is None:
        workspaces = TeamsWorkspace.objects.filter(is_active=True, send_reminders=True)

    # Use an injectable factory to construct the reminder service so the task
    # depends on an abstraction instead of the concrete implementation. This
    # also keeps tests and future implementations decoupled from the task.
    if reminder_service_factory is None:
        reminder_service_factory = ReminderService

    for workspace in workspaces:
        service = reminder_service_factory(workspace)
        results = service.send_bulk_reminders()
        total_sent += results["sent"]

    return total_sent
```

### Key Benefits

1. **Testability** - Tests can inject mocks without patching module internals
2. **Decoupling** - Tasks don't import or know about concrete implementations at call time
3. **Flexibility** - Easy to swap implementations (e.g., mock client vs real client)
4. **Type Safety** - Protocols ensure injected mocks have the right interface

### Review Checklist for DIP

When reviewing code, check:

- [ ] Are background tasks tightly coupled to concrete service/client classes?
- [ ] Could the code benefit from Protocol + Factory injection for testability?
- [ ] Are tests using `@patch` on internal module paths when injection would be cleaner?
- [ ] Is the factory parameter well-documented with Args in the docstring?
- [ ] Does the default (`if factory is None`) fall back to a sensible concrete implementation?

### Anti-Patterns to Flag

```python
# BAD: Task directly instantiates concrete class - hard to test
@optimo_job("optimo_core_default")
def send_reminders():
    for workspace in TeamsWorkspace.objects.filter(is_active=True):
        service = ReminderService(workspace)  # Tight coupling
        service.send_bulk_reminders()

# GOOD: Task accepts injectable factory
@optimo_job("optimo_core_default")
def send_reminders(
    *,
    reminder_service_factory: ReminderServiceFactory | None = None,
):
    if reminder_service_factory is None:
        reminder_service_factory = ReminderService

    for workspace in TeamsWorkspace.objects.filter(is_active=True):
        service = reminder_service_factory(workspace)
        service.send_bulk_reminders()
```

---

## Single Responsibility Principle (SRP)

### Core Concept

A unit (function/class/module) should have **one primary reason to change**.
In Django4Lyfe, SRP usually means you should not mix:

- Boundary glue (HTTP/task orchestration, permission checks)
- Query construction + tenant/time scoping
- Domain decisions (eligibility, retries, invariants)
- Formatting/serialization (Slack blocks, Teams cards, CSV/JSON shaping)
- Side effects (email, Slack/Teams API, file I/O)
- Persistence writes (saving models, audit logs)

### When to Apply

- You can’t describe the unit’s job in one sentence without “and”.
- One change request forces edits across unrelated concerns (query + formatting + API client).
- Tests need lots of patching because the unit touches many concerns at once.
- The code has “multiple verbs”: *fetch + decide + format + send + persist*.

### When NOT to Apply

Monty’s taste: **clarity > architecture**. Don’t split just to “be SRP” when:

- The function is already small (<30 lines) and cohesive.
- Extraction would create one-line wrappers with unclear ownership.
- Nothing else would reuse the extracted piece and tests wouldn’t become simpler.

### Pattern: Thin Boundary + Focused Services/Helpers

Aim for:

1. **Thin boundaries** (endpoints, views, admin actions, tasks)
   - Orchestrate: validate inputs, enforce permissions, call a service, shape output.
2. **Focused services**
   - Own one coherent domain job (e.g., “send reminders for a workspace”).
3. **Helpers**
   - Validators, formatters, selectors/query builders, and side-effect clients.

### Example: SRP Refactor (Also Enables DIP)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# BEFORE: One unit does everything (query + decisions + formatting + side effects + writes)
@optimo_job("optimo_core_default", timeout=300)
def send_reminders() -> int:
    total_sent = 0
    workspaces = TeamsWorkspace.objects.filter(is_active=True)  # query
    for workspace in workspaces:
        sessions = get_eligible_sessions(workspace)  # more query + domain decisions
        for session in sessions:
            card = build_reminder_card(session)  # formatting
            client = TeamsClient(workspace)  # side-effect setup
            client.send_activity(card)  # side effect
            session.last_reminder_at = timezone.now()  # persistence
            session.save(update_fields=["last_reminder_at"])
            total_sent += 1
    return total_sent


# AFTER: Thin boundary + focused service (service can be injected via DIP)
ReminderServiceFactory = Callable[[TeamsWorkspace], ReminderServiceProtocol]

@optimo_job("optimo_core_default", timeout=300)
def send_reminders(
    *,
    reminder_service_factory: ReminderServiceFactory | None = None,
) -> int:
    if reminder_service_factory is None:
        reminder_service_factory = ReminderService

    total_sent = 0
    for workspace in TeamsWorkspace.objects.filter(is_active=True):
        service = reminder_service_factory(workspace)
        total_sent += service.send_bulk_reminders()
    return total_sent
```

SRP win: "how reminders are computed/sent" moves behind one service boundary.
DIP win: tests can inject a fake `ReminderServiceFactory` and avoid patching internals.

### Key Benefits

1. **Clarity** - Each unit's purpose is obvious and can be named in one sentence
2. **Testability** - Less patching required; services can be injected and tested in isolation
3. **Maintainability** - Changes to one concern don't ripple across unrelated code
4. **DIP Alignment** - Focused services naturally compose with factory injection patterns

### Review Checklist for SRP

When reviewing code, check:

- [ ] Can you name the unit’s single responsibility precisely?
- [ ] Are permissions/auth checks kept at boundaries (not deep in helpers)?
- [ ] Are query construction and formatting separated from side effects?
- [ ] Would extracting a helper/service reduce cognitive load (vs add indirection)?
- [ ] Do tests become less patch-heavy after the split?

### Anti-Patterns to Flag

```python
# BAD: endpoint/service mixes too many concerns
def handler(request):
    assert_can_access(request)
    rows = Model.objects.filter(organization=request.optimo_organization).values(...)
    payload = build_payload(rows)
    send_email(payload)
    return JsonResponse(payload)
```

---

## Open/Closed Principle (OCP)

### Core Concept

Software entities should be **open for extension** but **closed for modification**.
In Django4Lyfe, this means: make core flows stable while allowing new behavior
(new platforms, question types, export formats) to be added via extension points
rather than editing existing code.

Monty's taste: prefer **simple, explicit extension points** (typed callables +
small registries) over framework-y abstractions, inheritance hierarchies, or
metaclass magic.

### When to Apply

- `if platform == "slack" / elif platform == "teams"` branching repeated across multiple files.
- `if question_type == ...` chains that grow every time a new type is added.
- "Add a new X" requires touching 3+ unrelated modules.
- Tests for new behavior require editing existing test files instead of adding new ones.

### When NOT to Apply

- The axis is truly fixed (2 stable cases) and new cases are not expected.
- The "registry" would only ever have 1 entry.
- The abstraction increases indirection but doesn't reduce churn or simplify tests.

### Pattern: Registry + Protocol for Extensible Dispatch

#### Step 1: Define a Protocol for the Extension Point

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
from typing import Protocol, Any

class IntegrationPlatformHandlerProtocol(Protocol):
    """Protocol for platform-specific integration operations."""
    platform: str

    def find_workspace(self, *, organization: OptimoOrganization) -> SlackWorkspace | TeamsWorkspace | None: ...
    def disconnect(self, *, organization: OptimoOrganization, workspace: SlackWorkspace | TeamsWorkspace) -> dict[str, Any]: ...
```

#### Step 2: Create a Single Registry (One Source of Truth)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
PLATFORM_HANDLERS: dict[str, IntegrationPlatformHandlerProtocol] = {
    "slack": SlackIntegrationHandler(),
    "teams": TeamsIntegrationHandler(),
}
SUPPORTED_PLATFORMS = frozenset(PLATFORM_HANDLERS.keys())  # Derived, not duplicated
```

#### Step 3: Replace Branching with Registry Lookup

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# BEFORE: branching grows every time you add a platform
def disconnect_integration(platform: str, organization: OptimoOrganization) -> dict[str, Any]:
    if platform == "slack":
        workspace = SlackWorkspace.objects.filter(organization=organization).first()
        # ... slack-specific logic ...
    elif platform == "teams":
        workspace = TeamsWorkspace.objects.filter(organization=organization).first()
        # ... teams-specific logic ...
    else:
        raise ValueError(f"Unknown platform: {platform}")

# AFTER: stable core; extend by adding a new handler + registry entry
def disconnect_integration(platform: str, organization: OptimoOrganization) -> dict[str, Any]:
    handler = PLATFORM_HANDLERS[platform]  # Fail fast on unknown platform
    workspace = handler.find_workspace(organization=organization)
    if workspace is None:
        return {"status": "no_workspace", "platform": platform}  # Or raise — define your policy
    return handler.disconnect(organization=organization, workspace=workspace)
```

#### Step 4: Test Registry Exhaustiveness

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
def test_platform_registry_exhaustiveness():
    """Ensure all supported platforms have handlers."""
    assert set(PLATFORM_HANDLERS) == {"slack", "teams"}

def test_unknown_platform_raises():
    """Unknown platform should fail fast."""
    with pytest.raises(KeyError):
        _ = PLATFORM_HANDLERS["unknown"]
```

### Choosing the Right Mechanism

| Mechanism | When to Use |
|-----------|-------------|
| **Data-driven dict** | Differences are mostly data/config (model classes, field names) |
| **Typed callables registry** | Differences are behavior but stateless (one function per variant) |
| **Strategy Protocol + factory** | Behavior needs dependencies, state, or multiple methods |

### Key Benefits

1. **Stability** - Core flows don't change when adding new variants
2. **Locality** - New behavior lives in new files with new tests
3. **Explicitness** - Extension axes are visible in registry definitions
4. **Testability** - Registries can be injected (DIP alignment)

### Review Checklist for OCP

When reviewing code, check:

- [ ] Is there repeated `if/elif` branching on the same axis across multiple files?
- [ ] Would adding a new variant require editing core flow code?
- [ ] Is `SUPPORTED_*` derived from `REGISTRY.keys()` (not duplicated)?
- [ ] Is unknown-key behavior defined (fail fast or explicit fallback)?
- [ ] Do new handlers come with their own tests (not edits to existing tests)?

### Anti-Patterns to Flag

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# BAD: Branching that grows with each new platform
def get_workspace(platform: str, org: OptimoOrganization):
    if platform == "slack":
        return SlackWorkspace.objects.filter(organization=org).first()
    elif platform == "teams":
        return TeamsWorkspace.objects.filter(organization=org).first()
    # ... more elif branches added over time ...


# GOOD: Registry-based dispatch with named functions (clearer than lambdas)
def _find_slack_workspace(org: OptimoOrganization) -> SlackWorkspace | None:
    return SlackWorkspace.objects.filter(organization=org).first()


def _find_teams_workspace(org: OptimoOrganization) -> TeamsWorkspace | None:
    return TeamsWorkspace.objects.filter(organization=org).first()


WORKSPACE_FINDERS: dict[str, Callable[[OptimoOrganization], SlackWorkspace | TeamsWorkspace | None]] = {
    "slack": _find_slack_workspace,
    "teams": _find_teams_workspace,
}


def get_workspace(platform: str, org: OptimoOrganization):
    finder = WORKSPACE_FINDERS[platform]
    return finder(org)
```

---

## Liskov Substitution Principle (LSP)

### Core Concept

If code works with a base type or Protocol, it should work with **any implementation**
of that type without surprises. Substituting one implementation for another must not
change correctness — behavior, return shapes, exceptions, and invariants must conform
to the contract.

Monty's taste: make contracts explicit, keep polymorphism boring, and avoid "fake
subclasses" that behave differently in subtle ways.

### When to Apply

- You have real + mock implementations (e.g., `TeamsClient` vs `MockTeamsClient`).
- Multiple subclasses implement a base service (e.g., Slack vs Teams discovery).
- Provider interfaces where implementations can be swapped (IP lookup, SMS, LLM).
- Tests pass with mocks but fail in prod due to semantic differences.

### When NOT to Apply

- Only one implementation exists and no realistic prospect of substitution.
- The "interface" would be a 1:1 mirror of the concrete class (no simplification).
- Adding abstraction would hide domain decisions and make control flow harder to read.

### Pattern: Protocol + Conformance Tests

LSP is enforced through two layers:

1. **Static typing** - Protocol/ABC signatures enforce substitutability at compile time.
2. **Conformance tests** - A shared test suite runs against every implementation.

#### Step 1: Define the Contract (Protocol)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
class TeamsClientProtocol(Protocol):
    """Contract for Teams API clients (real and mock)."""

    def send_message(
        self, *, conversation_id: str, message: str | None = None, card: dict | None = None
    ) -> dict[str, Any]: ...

    def update_message(
        self, *, conversation_id: str, activity_id: str, card: dict
    ) -> dict[str, Any]: ...
```

#### Step 2: Define Contract Assertions

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
def assert_send_message_postconditions(resp: dict[str, Any]) -> None:
    """Verify the fields callers actually rely on."""
    assert "conversationId" in resp, "Response must include conversationId"
    assert "activityId" in resp, "Response must include activityId"
```

#### Step 3: Write Conformance Tests (Run Against All Implementations)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
@pytest.mark.parametrize(
    "client_factory",
    [build_real_client, build_mock_client],
)
def test_send_message_returns_required_fields(client_factory):
    """Both real and mock clients must return the same shape."""
    client = client_factory()
    resp = client.send_message(conversation_id="c1", message="hello")
    assert_send_message_postconditions(resp)


@pytest.mark.parametrize(
    "client_factory",
    [build_real_client, build_mock_client],
)
def test_send_message_rejects_empty_payload(client_factory):
    """Both implementations must raise ValueError for missing message/card."""
    client = client_factory()
    with pytest.raises(ValueError):
        client.send_message(conversation_id="c1")  # No message or card
```

### Key Contract Elements

When defining a contract, document:

| Element | What to Specify |
|---------|-----------------|
| **Preconditions** | Required params, allowed ranges, non-null requirements |
| **Postconditions** | Return shape, required fields, side effects |
| **Error behavior** | Which exceptions for which conditions |
| **Invariants** | Tenant scoping, time dimensions preserved across calls |
| **Caller constraint** | Callers must not branch on concrete implementation type |

### Key Benefits

1. **Mock/Prod Parity** - Tests catch semantic differences before prod
2. **Explicit Contracts** - What callers rely on is documented and tested
3. **Safe Substitution** - New implementations must pass existing conformance tests
4. **DIP Alignment** - Protocol + factory pattern enables both DIP and LSP

### Review Checklist for LSP

When reviewing code, check:

- [ ] Is the substitution boundary clearly identified (what swaps with what)?
- [ ] Is the contract written down (inputs, outputs, errors)?
- [ ] Do all implementations match exception behavior and return semantics?
- [ ] Are mocks semantically faithful to prod (not just "happy path")?
- [ ] Is there a shared conformance test suite for all implementations?
- [ ] Are tenant/time scoping invariants preserved across implementations?
- [ ] Do callers avoid branching on concrete implementation type (`isinstance` checks)?

### Anti-Patterns to Flag

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# BAD: Mock returns richer shape than prod — callers couple to mock behavior
class MockTeamsClient:
    def send_message(self, **kwargs) -> dict[str, Any]:
        return {"id": "123", "conversationId": "c1", "extra_field": "only in mock"}

class TeamsClient:
    def send_message(self, **kwargs) -> dict[str, Any]:
        # Prod may return empty body or minimal shape on success
        return {"conversationId": response.conversation_id}  # No "id" field!


# BAD: Caller branches on concrete implementation type
def send_notification(client: TeamsClientProtocol, msg: str):
    if isinstance(client, MockTeamsClient):
        # Special handling for mock — LSP violation
        return {"mocked": True}
    return client.send_message(conversation_id="c1", message=msg)


# BAD: Subclass raises different exception than base contract
class SlackDiscoveryService(BaseDiscoveryService):
    def get_unlinked_users(self, org):
        if not org.slack_workspace:
            return []  # Silent no-op

class TeamsDiscoveryService(BaseDiscoveryService):
    def get_unlinked_users(self, org):
        if not org.teams_workspace:
            raise ValueError("No workspace")  # Different behavior!


# GOOD: Both implementations conform to the same contract
# Contract states: returns {"conversationId": str, "activityId": str} on success
class MockTeamsClient:
    def send_message(self, **kwargs) -> dict[str, Any]:
        # Return exactly what prod returns — no more, no less
        return {"conversationId": "c1", "activityId": "a1"}

class TeamsClient:
    def send_message(self, **kwargs) -> dict[str, Any]:
        return {"conversationId": response.conversation_id, "activityId": response.id}
```

**Contract choice: empty body success**

If prod can return an empty body on success (e.g., 204 No Content or `{}`), the contract
should explicitly state which fields callers can rely on. Mock must match this — if prod
doesn't guarantee `"id"` in the response, mock shouldn't return it either.

### LSP-Specific Risks

- **Narrowed preconditions** - Subclass rejects inputs the base accepts (stricter validation).
- **Weakened postconditions** - Subclass returns less info or different shape than callers rely on.
- **Different exceptions** - Subclass raises different exception type, forcing caller branching.
- **Mock/prod divergence** - Tests pass with mock but fail in prod due to semantic differences.
- **Hidden side effects** - Subclass introduces persistence/logging that callers don't expect.

---

## Interface Segregation Principle (ISP)

### Core Concept

Clients should not be forced to depend on methods they do not use. In practice:
prefer **many small Protocols** over one "god interface", but avoid creating dozens
of tiny interfaces that add indirection without improving clarity.

Monty's taste: keep interfaces small, explicit, and focused on what the *caller
actually needs*.

### When to Apply

- A consumer imports a concrete "big" class but only uses 1–2 methods.
- A mock must implement many unrelated methods just to satisfy a dependency.
- Protocols/ABCs have multiple methods but different call sites only need subsets.
- "Convenience" services become dumping grounds and start accreting unrelated APIs.

Heuristic: if the easiest test double is "copy the real class", the interface is too wide.

### When NOT to Apply

- Only one consumer exists and the interface wouldn't be reused.
- The "segregated interface" would be a 1:1 copy of the concrete class.
- Splitting would create many single-method Protocols with no cohesive concept.
- The overhead of maintaining multiple Protocols exceeds the testing/coupling benefit.

### Pattern: Segregated Protocols by Capability

#### Step 1: Identify Consumer's True Needs

List only the methods the consumer actually calls. If it's 1–2 methods out of 10,
you have an ISP opportunity.

#### Step 2: Define a Minimal Protocol

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# Instead of depending on the full TeamsClient (10+ methods),
# define a narrow Protocol for what reminders actually need:

class TeamsMessagingProtocol(Protocol):
    """Narrow interface for sending Teams messages."""

    def send_proactive_message(
        self, user_id: str, *, message: str | None = None, card: dict | None = None
    ) -> dict[str, Any]: ...
```

#### Step 3: Split Big Clients by Capability

When you have a large client, split by capability:

| Capability | Methods | Consumers |
|------------|---------|-----------|
| **Messaging** | `send_message`, `update_message` | Reminder tasks, notification services |
| **User sync** | `list_users`, `get_user` | Employee discovery, sync jobs |
| **Auth/token** | `refresh_token` | Token management services |
| **Health** | `test_connection` | Health check endpoints |

This prevents accidental coupling (reminder service shouldn't need "list all users").

#### Step 4: Inject the Narrow Interface (DIP Alignment)

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# Factory returns the segregated interface, not the concrete class
TeamsMessagingFactory = Callable[[TeamsWorkspace], TeamsMessagingProtocol]

def send_reminder_task(
    *,
    messaging_factory: TeamsMessagingFactory | None = None,
):
    if messaging_factory is None:
        messaging_factory = TeamsClient  # Concrete class implements the Protocol

    client = messaging_factory(workspace)
    client.send_proactive_message(user_id=user_id, card=reminder_card)
```

### Key Benefits

1. **Trivial Fakes** - Test doubles only implement methods actually used
2. **Reduced Coupling** - Adding methods to TeamsClient doesn't affect unrelated consumers
3. **Explicit Dependencies** - What a consumer needs is visible in its type signature
4. **DIP Alignment** - Narrow Protocols compose naturally with factory injection

### Review Checklist for ISP

When reviewing code, check:

- [ ] Does this consumer depend only on methods it actually uses?
- [ ] Is the interface small enough that a test fake is trivial?
- [ ] Are factories returning the segregated interface (not the concrete god class)?
- [ ] Are return shapes and exceptions part of an explicit contract?
- [ ] Is the interface shared/owned in a sensible module (no duplicated Protocols)?

### Anti-Patterns to Flag

Pseudocode (imports/types omitted for brevity — do not copy/paste as-is):

```python
# BAD: Consumer depends on giant interface but only uses one method
class TeamsClient:
    def send_message(...): ...
    def update_message(...): ...
    def list_users(...): ...
    def refresh_token(...): ...
    def test_connection(...): ...

def send_reminder(client: TeamsClient):  # Depends on 5-method interface
    client.send_message(...)  # Only uses 1 method!


# BAD: Fake must implement unused methods (brittle tests)
class FakeTeamsClient:
    def send_message(self, ...): return {"ok": True}
    def update_message(self, ...): raise NotImplementedError  # Never called
    def list_users(self, ...): raise NotImplementedError
    def refresh_token(self, ...): raise NotImplementedError
    def test_connection(self, ...): raise NotImplementedError


# GOOD: Consumer depends on segregated interface
class TeamsMessagingProtocol(Protocol):
    def send_message(...) -> dict[str, Any]: ...

def send_reminder(client: TeamsMessagingProtocol):  # Narrow dependency
    client.send_message(...)


# GOOD: Fake is trivial and focused
class FakeMessagingClient:
    def __init__(self):
        self.send_message_called = False

    def send_message(self, ...) -> dict[str, Any]:
        self.send_message_called = True
        return {"conversationId": "c1"}
```

### ISP-Specific Risks

- **Over-segmentation** - Too many tiny Protocols make navigation harder than the original class.
- **Protocol drift** - Different modules define slightly different Protocols for the same concept.
- **Leaky interfaces** - Consumers depend on return shapes "by accident" (mock richer than prod).
- **Fake-only design** - Designing the interface for tests instead of real domain needs.

**Mitigation:** Prefer one Protocol per concept per package, keep it near the boundary
where it's used, and add conformance tests for high-value interfaces.

