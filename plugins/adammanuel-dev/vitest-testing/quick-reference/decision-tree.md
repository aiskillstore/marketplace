# Visual Decision Trees

**Visual flowcharts and decision diagrams for quick test strategy selection.**

This guide provides visual decision trees to help you quickly determine the right testing approach for any scenario.

---

## 🎯 Main Decision Tree: What Test Should I Write?

```mermaid
graph TD
    Start[What am I testing?] --> NewFeature{New Feature?}
    Start --> BugFix{Bug Fix?}
    Start --> Refactor{Refactoring?}
    Start --> Component{UI Component?}
    Start --> API{API/HTTP?}
    Start --> Logic{Complex Logic?}

    NewFeature -->|Yes| UnitTest[Unit Test - Black Box]
    UnitTest --> ApplyFIRST[Apply F.I.R.S.T Principles]
    ApplyFIRST --> UseAAA[Use AAA Pattern]
    UseAAA --> MockDeps[Mock External Dependencies]

    BugFix -->|Yes| RegressionTest[Regression Test]
    RegressionTest --> WriteFailingTest[1. Write Failing Test]
    WriteFailingTest --> FixImpl[2. Fix Implementation]
    FixImpl --> VerifyPass[3. Verify Test Passes]
    VerifyPass --> AddEdgeCases[4. Add Edge Cases]

    Refactor -->|Yes| ExistingTests[Ensure Existing Tests Pass]
    ExistingTests --> IdentifyUntestable[Identify Untestable Code]
    IdentifyUntestable --> ExtractTestable[Extract Testable Units]
    ExtractTestable --> AddTests[Add Tests for Extracted Units]

    Component -->|Yes| ComponentTest[Component Test]
    ComponentTest --> TestUserBehavior[Test User Interactions]
    TestUserBehavior --> QueryByRole[Query by Roles/Labels]
    QueryByRole --> TestStates[Test Loading/Error States]

    API -->|Yes| APITest[API/Integration Test]
    APITest --> TestContract[Test HTTP Contract]
    TestContract --> TestErrors[Test 4xx/5xx Errors]
    TestErrors --> MockExternal[Mock External APIs]

    Logic -->|Yes| DomainTest[Domain/Business Logic Test]
    DomainTest --> TestInvariants[Test Business Rules]
    TestInvariants --> UseBDD[Use Given/When/Then]
    UseBDD --> TestBlackBox[Test Via Public API]

    style UnitTest fill:#90EE90
    style ComponentTest fill:#87CEEB
    style APITest fill:#FFB6C1
    style DomainTest fill:#DDA0DD
    style RegressionTest fill:#F0E68C
```

---

## 🔀 Test Double Selection Tree

```mermaid
graph TD
    Start[Need to isolate dependency?] --> Purpose{What's the purpose?}

    Purpose -->|Verify function was called| Spy[Use Spy]
    Purpose -->|Replace external API| Mock[Use Mock]
    Purpose -->|Return specific values| Stub[Use Stub]
    Purpose -->|Lightweight replacement| Fake[Use Fake]
    Purpose -->|Control time/randomness| FakeTimer[Use Fake Timers]

    Spy --> SpyExample["vi.spyOn(obj, 'method')"]
    Mock --> MockExample["vi.mock('./module')"]
    Stub --> StubExample["vi.fn().mockReturnValue()"]
    Fake --> FakeExample["In-memory implementation"]
    FakeTimer --> TimerExample["vi.useFakeTimers()"]

    SpyExample --> SpyUse[Use for: Logging, Analytics]
    MockExample --> MockUse[Use for: HTTP, Database]
    StubExample --> StubUse[Use for: Config, Feature Flags]
    FakeExample --> FakeUse[Use for: In-memory DB, FS]
    TimerExample --> TimerUse[Use for: setTimeout, Date.now]

    style Spy fill:#90EE90
    style Mock fill:#87CEEB
    style Stub fill:#FFB6C1
    style Fake fill:#DDA0DD
    style FakeTimer fill:#F0E68C
```

---

## 🏗️ Testability Refactoring Decision Tree

```mermaid
graph TD
    Start[Code is hard to test?] --> Identify{What's the issue?}

    Identify -->|Mixed logic & side effects| Pattern1[Extract Pure Functions]
    Identify -->|Hard-coded dependencies| Pattern2[Dependency Injection]
    Identify -->|Complex private method| Pattern3[Extract Complex Class]
    Identify -->|Direct library usage| Pattern4[Wrap External Library]
    Identify -->|Time-dependent code| Pattern5[Control Time with Clock Interface]

    Pattern1 --> Pure[Separate calculation from I/O]
    Pure --> TestPure[Test pure function exhaustively]
    TestPure --> TestOrch[Test orchestration with mocks]

    Pattern2 --> Inject[Inject dependencies via constructor]
    Inject --> Interface[Create interface for dependency]
    Interface --> MockDep[Mock dependency in tests]

    Pattern3 --> Extract[Extract private logic to new class]
    Extract --> PublicAPI[Give it public API]
    PublicAPI --> TestBlackBox[Test as black box]

    Pattern4 --> Wrapper[Create thin wrapper]
    Wrapper --> WrapInterface[Define interface]
    WrapInterface --> TestWrapper[Test wrapper usage]

    Pattern5 --> ClockInterface[Create Clock interface]
    ClockInterface --> InjectClock[Inject clock dependency]
    InjectClock --> MockTime[Mock time in tests]

    style Pattern1 fill:#90EE90
    style Pattern2 fill:#87CEEB
    style Pattern3 fill:#FFB6C1
    style Pattern4 fill:#DDA0DD
    style Pattern5 fill:#F0E68C
```

---

## 🎯 Black Box vs White Box Decision Tree

```mermaid
graph TD
    Start[Should I test this?] --> Public{Is it a public API?}

    Public -->|Yes| BlackBox[Black Box Testing]
    Public -->|No, it's private| Question1{Complex algorithm?}

    Question1 -->|Yes| CanExtract{Can I extract to class?}
    Question1 -->|No| DontTest[Don't Test - Test via Public API]

    CanExtract -->|Yes| Extract[Extract to Public Class]
    CanExtract -->|No| Question2{Legacy code?}

    Extract --> BlackBox

    Question2 -->|Yes| Characterization[Characterization Test - Temporary]
    Question2 -->|No| Question3{Performance requirement?}

    Question3 -->|Yes| PerfTest[Test Performance Characteristic]
    Question3 -->|No| Question4{Only observable output?}

    Question4 -->|Yes| AddPublic[Add Public Query Method]
    Question4 -->|No| DontTest

    AddPublic --> BlackBox

    Characterization --> Refactor[Refactor to Black Box ASAP]
    PerfTest --> PreferBlackBox[Prefer Public API Test]

    BlackBox --> Success[✅ Robust, Maintainable Test]
    DontTest --> Success
    Refactor --> Success
    PreferBlackBox --> Success

    style BlackBox fill:#90EE90
    style DontTest fill:#87CEEB
    style Characterization fill:#FFB6C1
    style Extract fill:#DDA0DD
```

---

## 🔄 F.I.R.S.T Compliance Check

```mermaid
graph TD
    Start[Is my test F.I.R.S.T compliant?] --> Fast{Fast < 100ms?}

    Fast -->|No| SlowIssue[Issue: Real DB/Network/FS?]
    Fast -->|Yes| Isolated{Isolated?}

    SlowIssue --> MockExternal[Mock external dependencies]
    MockExternal --> Isolated

    Isolated -->|No| IsolatedIssue[Issue: Shared state?]
    Isolated -->|Yes| Repeatable{Repeatable?}

    IsolatedIssue --> FreshMocks[Use beforeEach for fresh mocks]
    FreshMocks --> Repeatable

    Repeatable -->|No| RepeatableIssue[Issue: Time/Random/External?]
    Repeatable -->|Yes| SelfCheck{Self-Checking?}

    RepeatableIssue --> ControlTime[Use vi.useFakeTimers]
    RepeatableIssue --> MockRandom[Mock Math.random]
    ControlTime --> SelfCheck
    MockRandom --> SelfCheck

    SelfCheck -->|No| SelfCheckIssue[Issue: No assertions?]
    SelfCheck -->|Yes| Timely{Timely/Maintainable?}

    SelfCheckIssue --> AddAssertions[Add expect assertions]
    AddAssertions --> Timely

    Timely -->|No| TimelyIssue[Issue: Unclear/Magic values?]
    Timely -->|Yes| Success[✅ F.I.R.S.T Compliant!]

    TimelyIssue --> ClearNames[Use descriptive names]
    TimelyIssue --> DocValues[Document magic values]
    ClearNames --> Success
    DocValues --> Success

    style Success fill:#90EE90
    style SlowIssue fill:#FFB6C1
    style IsolatedIssue fill:#FFB6C1
    style RepeatableIssue fill:#FFB6C1
    style SelfCheckIssue fill:#FFB6C1
    style TimelyIssue fill:#FFB6C1
```

---

## 🧪 Test Type Selection Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                     WHAT AM I TESTING?                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
           ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
           │ Layer?  │   │ Scope?  │  │ Focus?  │
           └────┬────┘   └────┬────┘  └────┬────┘
                │             │             │
    ┌───────────┼──────┐      │      ┌──────┼──────┐
    │           │      │      │      │      │      │
┌───▼───┐  ┌───▼───┐ │  ┌───▼───┐ │ ┌────▼───┐ ┌▼────┐
│ Unit  │  │ Integ │ │  │ E2E   │ │ │Behavior│ │Perf │
│ Test  │  │ Test  │ │  │ Test  │ │ │ Test   │ │Test │
└───┬───┘  └───┬───┘ │  └───┬───┘ │ └────┬───┘ └┬────┘
    │          │     │      │     │      │      │
    ├─ Single │     │      │     │      │      │
    │  function│     │      │     │      │      │
    ├─ Black  │     │      │     │      │      │
    │  box    │     │      │     │      │      │
    ├─ Fast   │     │      │     │      │      │
    │  < 10ms │     │      │     │      │      │
    │         │     │      │     │      │      │
    │         ├─ Multiple  │      │      │      │
    │         │  modules   │      │      │      │
    │         ├─ Real DB   │      │      │      │
    │         │  (optional)│      │      │      │
    │         ├─ Fast      │      │      │      │
    │         │  < 1s      │      │      │      │
    │         │            │      │      │      │
    │         │            ├─ Full flow  │      │
    │         │            ├─ Real deps  │      │
    │         │            ├─ UI testing │      │
    │         │            ├─ Slow       │      │
    │         │            │  > 5s       │      │
    │         │            │             │      │
    │         │            │     ├─ Business   │
    │         │            │     │  rules      │
    │         │            │     ├─ Given/When │
    │         │            │     │  Then       │
    │         │            │     │             │
    │         │            │     │      ├─ Benchmarks
    │         │            │     │      ├─ Memory
    │         │            │     │      ├─ Load test
    │         │            │     │      │
    └─────────┴────────────┴─────┴──────┴──────┴──────
         ↓           ↓        ↓      ↓       ↓
    patterns/   patterns/  patterns/ principles/ patterns/
    test-       async-     component bdd-      performance-
    doubles.md  testing.md testing.md integration testing.md
                                      .md
```

---

## 🔧 Refactoring for Testability Flow

```
┌──────────────────────────────────────────────────┐
│ Is my code hard to test?                         │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Identify the problem │
        └──────────┬───────────┘
                   │
    ┌──────────────┼──────────────┬─────────────┬──────────────┐
    │              │              │             │              │
    ▼              ▼              ▼             ▼              ▼
┌───────┐    ┌──────────┐   ┌─────────┐  ┌─────────┐   ┌──────────┐
│Mixed  │    │Hard-coded│   │Complex  │  │Direct   │   │Time      │
│Logic &│    │Deps      │   │Private  │  │Library  │   │Dependent │
│Effects│    │          │   │Method   │  │Usage    │   │          │
└───┬───┘    └────┬─────┘   └────┬────┘  └────┬────┘   └────┬─────┘
    │             │              │           │             │
    ▼             ▼              ▼           ▼             ▼
┌───────────┐ ┌──────────┐  ┌─────────┐ ┌─────────┐  ┌──────────┐
│Extract    │ │Inject    │  │Extract  │ │Create   │  │Inject    │
│Pure       │ │via       │  │to New   │ │Wrapper  │  │Clock     │
│Functions  │ │Constructor│ │Class    │ │Interface│  │Interface │
└─────┬─────┘ └─────┬────┘  └────┬────┘ └────┬────┘  └────┬─────┘
      │             │             │           │             │
      ▼             ▼             ▼           ▼             ▼
┌──────────────────────────────────────────────────────────────┐
│ Test pure logic exhaustively + Test orchestration with mocks│
└──────────────────────────────────────────────────────────────┘
```

**Reference:** [testability-patterns.md](../refactoring/testability-patterns.md)

---

## 🎭 Mock Strategy Selector

```
Need to isolate a dependency?
│
├─ What do you need to verify?
│
├─ ❓ "Was this function called?"
│  └─ 🎯 Use SPY
│     └─ vi.spyOn(object, 'method')
│     └─ Example: Logger, Analytics, Event tracking
│
├─ ❓ "Replace external system (API/DB)"
│  └─ 🎯 Use MOCK
│     └─ vi.mock('./module')
│     └─ Example: HTTP client, Database, Email service
│
├─ ❓ "Return specific value"
│  └─ 🎯 Use STUB
│     └─ vi.fn().mockReturnValue(value)
│     └─ Example: Configuration, Feature flags
│
├─ ❓ "Need working but simplified implementation"
│  └─ 🎯 Use FAKE
│     └─ Custom in-memory implementation
│     └─ Example: In-memory DB, Fake file system
│
└─ ❓ "Control time or randomness"
   └─ 🎯 Use FAKE TIMERS
      └─ vi.useFakeTimers(), vi.setSystemTime()
      └─ Example: setTimeout, Date.now(), Math.random()
```

**Reference:** [test-doubles.md](../patterns/test-doubles.md)

---

## 📋 Test Structure Checklist Flow

```
Writing a test?
│
├─ Step 1: ARRANGE (Given)
│  ├─ ✅ Create system under test
│  ├─ ✅ Set up test data
│  ├─ ✅ Configure mocks
│  ├─ ✅ Define expected values
│  └─ ❌ Don't execute behavior yet
│
├─ Step 2: ACT (When)
│  ├─ ✅ Call ONE public method
│  ├─ ✅ Capture result or exception
│  └─ ❌ Don't call multiple methods
│
└─ Step 3: ASSERT (Then)
   ├─ ✅ Verify expected outcome
   ├─ ✅ Check return value
   ├─ ✅ Verify state changes
   ├─ ✅ Verify mock interactions
   └─ ❌ Don't perform additional actions
```

**Reference:** [aaa-pattern.md](../principles/aaa-pattern.md)

---

## 🚦 Test Coverage Strategy

```
┌─────────────────────────────────────────────┐
│         Testing Pyramid                     │
│                                             │
│              /\                             │
│             /  \     E2E Tests              │
│            /    \    (Few)                  │
│           /──────\   - Full user flows     │
│          /        \  - Critical paths      │
│         /          \ - UI integration      │
│        /────────────\                      │
│       /              \ Integration Tests   │
│      /                \ (Some)             │
│     /                  \ - API contracts   │
│    /                    \ - DB queries     │
│   /──────────────────────\ - Module integ  │
│  /                        \                │
│ /                          \ Unit Tests    │
│/____________________________\ (Many)       │
│                              - Pure logic  │
│                              - Business    │
│                              - Fast        │
└─────────────────────────────────────────────┘
```

**Where to focus:**
- **70-80%** Unit tests (fast, isolated, black box)
- **15-20%** Integration tests (API, database, modules)
- **5-10%** E2E tests (critical user flows)

**Reference:** [testing-pyramid.md](../principles/testing-pyramid.md) _(to be created)_

---

## 🎨 Component Testing Decision Flow

```
Testing a React/Vue component?
│
├─ Step 1: What are you testing?
│  ├─ Rendering → Use screen.getByRole()
│  ├─ User interaction → Use userEvent.click()
│  ├─ State changes → Test observable output
│  ├─ Props → Render with different props
│  └─ Async data → Test loading/error/success states
│
├─ Step 2: How to query elements?
│  ├─ ✅ PREFER: getByRole (accessibility)
│  ├─ ✅ GOOD: getByLabelText (forms)
│  ├─ ✅ OK: getByText (visible text)
│  ├─ ⚠️  AVOID: getByTestId (implementation detail)
│  └─ ❌ NEVER: querySelector (CSS coupling)
│
├─ Step 3: How to interact?
│  ├─ ✅ PREFER: userEvent.click(), userEvent.type()
│  ├─ ⚠️  OK: fireEvent (for simple cases)
│  └─ ❌ AVOID: Calling component methods directly
│
└─ Step 4: What to assert?
   ├─ ✅ Rendered output (text, attributes)
   ├─ ✅ Callback invocations (onClick, onSubmit)
   ├─ ✅ Accessibility (roles, labels)
   └─ ❌ Component internal state
```

**Reference:** [component-testing.md](../patterns/component-testing.md)

---

## 🌐 API Testing Decision Flow

```
Testing an API or HTTP client?
│
├─ What to test?
│  ├─ Happy path (200/201)
│  │  └─ Request structure (method, headers, body)
│  │  └─ Response parsing
│  │  └─ Data transformation
│  │
│  ├─ Client errors (4xx)
│  │  ├─ 400 Bad Request
│  │  ├─ 401 Unauthorized → Test auth flow
│  │  ├─ 404 Not Found → Test error handling
│  │  └─ 409 Conflict → Test business rule errors
│  │
│  ├─ Server errors (5xx)
│  │  ├─ 500 Internal Server Error
│  │  ├─ 503 Service Unavailable → Test retry logic
│  │  └─ 504 Gateway Timeout → Test timeout handling
│  │
│  └─ Network errors
│     ├─ Connection failures
│     ├─ Timeouts
│     └─ DNS errors
│
└─ How to mock?
   ├─ Simple: vi.fn() for fetch
   ├─ Realistic: MSW (Mock Service Worker)
   └─ Full integration: Test container with real API
```

**Reference:** [api-testing.md](../patterns/api-testing.md)

---

## 📊 Async Testing Decision

```
Testing async code?
│
├─ Type of async?
│  │
│  ├─ Promises
│  │  └─ await expect(promise).resolves.toBe()
│  │  └─ await expect(promise).rejects.toThrow()
│  │
│  ├─ Async/Await Functions
│  │  └─ Make test async: it('test', async () => {})
│  │  └─ Always await: await functionCall()
│  │
│  ├─ Callbacks (legacy)
│  │  └─ Convert to promises
│  │  └─ Use util.promisify()
│  │
│  └─ Timers (setTimeout/setInterval)
│     └─ vi.useFakeTimers()
│     └─ vi.advanceTimersByTime(ms)
│     └─ await vi.runAllTimersAsync()
│
└─ Testing loading states?
   ├─ Mock that never resolves → Test loading
   ├─ Mock that resolves → Test success
   └─ Mock that rejects → Test error
```

**Reference:** [async-testing.md](../patterns/async-testing.md)

---

## 🎯 Quick Pattern Lookup

| I need to... | Use this pattern | Reference |
|--------------|------------------|-----------|
| Mock a function | `vi.fn()` | [test-doubles.md](../patterns/test-doubles.md#stub) |
| Mock a module | `vi.mock('./module')` | [test-doubles.md](../patterns/test-doubles.md#mock) |
| Spy on object method | `vi.spyOn(obj, 'method')` | [test-doubles.md](../patterns/test-doubles.md#spy) |
| Control time | `vi.useFakeTimers()` | [async-testing.md](../patterns/async-testing.md#timer-mocking) |
| Test async function | `async/await` + `expect().resolves` | [async-testing.md](../patterns/async-testing.md) |
| Test React component | Testing Library | [component-testing.md](../patterns/component-testing.md) |
| Test API client | Mock fetch or MSW | [api-testing.md](../patterns/api-testing.md) |
| Test errors | `expect(() => {}).toThrow()` | [error-testing.md](../patterns/error-testing.md) |
| Make code testable | Extract pure functions | [testability-patterns.md](../refactoring/testability-patterns.md) |
| Generate test data | Test factories | [test-data.md](../patterns/test-data.md) |

---

## 🎨 ASCII Decision Tree: Start Here

```
                    ┌─────────────────────────┐
                    │  What am I testing?     │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
            New Feature     Bug Fix        Refactoring
                │               │               │
                ▼               ▼               ▼
        ┌───────────────┐  ┌──────────┐  ┌─────────────┐
        │ Unit Test     │  │Regression│  │ Ensure      │
        │ (Black Box)   │  │Test      │  │ Tests Pass  │
        └───┬───────────┘  └────┬─────┘  └──────┬──────┘
            │                   │                │
            ▼                   ▼                ▼
        F.I.R.S.T          Write Failing     Extract
        Principles         Test First         Testable Units
            │                   │                │
            ▼                   ▼                ▼
        AAA Pattern        Fix Code          Add Granular
                                             Tests
            │                   │                │
            ▼                   ▼                ▼
        Mock External      Verify Pass       All Tests
        Dependencies                         Pass
            │                   │                │
            └───────────────────┴────────────────┘
                                │
                                ▼
                        ✅ Test Complete
```

---

## 🔗 Related Guides

- **[Main Decision Tree](../index.md)** - Detailed scenarios with examples
- **[F.I.R.S.T Principles](../principles/first-principles.md)** - Quality checklist
- **[AAA Pattern](../principles/aaa-pattern.md)** - Test structure
- **[Testability Patterns](../refactoring/testability-patterns.md)** - Refactoring guide

---

## 💡 How to Use These Diagrams

### For Quick Decisions
1. Start with "Main Decision Tree"
2. Follow the path based on your scenario
3. Jump to the referenced file for details

### For Learning
1. Review each decision tree
2. Understand the branching logic
3. Practice applying to real scenarios

### For Code Reviews
1. Use trees as checklists
2. Verify proper pattern selection
3. Check test quality compliance

---

**Tip:** Bookmark this page for quick access during development!
