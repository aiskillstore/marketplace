---
name: multi-agent-analysis
description: Analyze coordination patterns, handoff mechanisms, and state sharing in multi-agent systems. Use when (1) understanding how agents transfer control, (2) evaluating shared vs isolated state patterns, (3) mapping communication protocols between agents, (4) assessing multi-agent orchestration approaches, or (5) comparing coordination models across frameworks.
---

# Multi-Agent Analysis

Analyzes coordination patterns in multi-agent systems.

## Process

1. **Identify coordination model** — Supervisor, peer-to-peer, pipeline
2. **Document handoffs** — How control transfers between agents
3. **Classify state sharing** — Blackboard vs message passing
4. **Trace communication** — Protocol and data flow

## Coordination Models

### Supervisor (Hierarchical)

```
        ┌─────────────┐
        │  Supervisor │
        │   (Router)  │
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐
│Worker1│  │Worker2│  │Worker3│
│(Search)│  │(Code) │  │(Write)│
└───────┘  └───────┘  └───────┘
```

```python
class Supervisor:
    def route(self, task: str) -> Agent:
        """Decide which worker handles the task"""
        if "search" in task:
            return self.search_agent
        elif "code" in task:
            return self.code_agent
        else:
            return self.general_agent
    
    def run(self, input: str):
        while not self.is_done():
            agent = self.route(self.current_task)
            result = agent.run(self.current_task)
            self.update_state(result)
```

**Characteristics**:
- Central control point
- Clear routing logic
- Single point of failure
- Easy to understand

### Peer-to-Peer

```
┌───────┐     ┌───────┐
│Agent A│◄───►│Agent B│
└───┬───┘     └───┬───┘
    │             │
    │  ┌───────┐  │
    └─►│Agent C│◄─┘
       └───────┘
```

```python
class PeerAgent:
    def __init__(self, peers: list["PeerAgent"]):
        self.peers = peers
    
    def delegate(self, task: str):
        """Find a peer that can handle this"""
        for peer in self.peers:
            if peer.can_handle(task):
                return peer.run(task)
        return self.run_locally(task)
    
    def broadcast(self, message: str):
        """Send to all peers"""
        for peer in self.peers:
            peer.receive(message)
```

**Characteristics**:
- Decentralized
- Resilient to single failures
- Complex coordination
- Harder to debug

### Pipeline (Sequential)

```
┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐
│Planner│───►│Executor│───►│Reviewer│───►│Output │
└───────┘    └───────┘    └───────┘    └───────┘
```

```python
class Pipeline:
    def __init__(self, stages: list[Agent]):
        self.stages = stages
    
    def run(self, input):
        result = input
        for stage in self.stages:
            result = stage.run(result)
        return result
```

**Characteristics**:
- Clear data flow
- Easy to reason about
- Limited parallelism
- Each stage is a bottleneck

### Market-Based

```python
class MarketCoordinator:
    def __init__(self, agents: list[Agent]):
        self.agents = agents
    
    def auction(self, task: str):
        """Agents bid on tasks"""
        bids = []
        for agent in self.agents:
            bid = agent.bid(task)  # Returns confidence/cost
            bids.append((agent, bid))
        
        # Select winner
        winner = max(bids, key=lambda x: x[1])
        return winner[0].run(task)
```

**Characteristics**:
- Dynamic allocation
- Self-organizing
- Overhead of bidding
- Complex to tune

## Handoff Mechanisms

### Explicit Transfer

```python
class Agent:
    def handoff_to(self, target: "Agent", context: dict):
        """Explicit control transfer"""
        return HandoffResult(
            target_agent=target,
            context=context,
            return_control=True
        )
    
    def run(self, input):
        result = self.think(input)
        if result.needs_specialist:
            return self.handoff_to(
                self.get_specialist(result.domain),
                context={"original_task": input, "progress": result}
            )
        return result
```

### Router-Based

```python
class Router:
    def __init__(self, agents: dict[str, Agent]):
        self.agents = agents
        self.routing_llm = LLM()
    
    def route(self, input: str) -> Agent:
        decision = self.routing_llm.generate(f"""
        Given this input: {input}
        Which agent should handle it?
        Options: {list(self.agents.keys())}
        """)
        return self.agents[decision.agent_name]
```

### Implicit (State-Based)

```python
class StateBasedCoordinator:
    def run(self, input):
        state = {"input": input, "stage": "planning"}
        
        while state["stage"] != "done":
            # Agent selection based on state
            agent = self.get_agent_for_stage(state["stage"])
            result = agent.run(state)
            state = self.update_state(state, result)
        
        return state["output"]
```

## State Sharing Patterns

### Blackboard (Shared Global State)

```python
class Blackboard:
    """Shared state all agents can read/write"""
    def __init__(self):
        self.state = {}
        self.lock = threading.Lock()
    
    def read(self, key: str):
        return self.state.get(key)
    
    def write(self, key: str, value):
        with self.lock:
            self.state[key] = value

# Agents share the blackboard
blackboard = Blackboard()
agent_a = Agent(blackboard)
agent_b = Agent(blackboard)
```

**Pros**: Simple, full visibility
**Cons**: Race conditions, tight coupling, hard to scale

### Message Passing (Isolated State)

```python
class Agent:
    def __init__(self):
        self.inbox = Queue()
        self.state = {}  # Private state
    
    def send(self, target: "Agent", message: dict):
        target.inbox.put(message)
    
    def receive(self) -> dict:
        return self.inbox.get()
    
    def run(self):
        while True:
            message = self.receive()
            result = self.process(message)
            if message.get("reply_to"):
                self.send(message["reply_to"], result)
```

**Pros**: Isolation, clear boundaries, scalable
**Cons**: More complex, async handling

### Hybrid

```python
class HybridCoordinator:
    def __init__(self, agents):
        # Shared read-only context
        self.shared_context = {"tools": [...], "config": {...}}
        
        # Per-agent mutable state
        self.agent_states = {a.id: {} for a in agents}
        
        # Message queues for communication
        self.queues = {a.id: Queue() for a in agents}
```

## Communication Protocol Analysis

### Direct Invocation

```python
result = agent_b.run(input)
```

**Latency**: Lowest
**Coupling**: Highest
**Async**: No

### Queue-Based

```python
task_queue.put(task)
# ... later ...
result = result_queue.get()
```

**Latency**: Medium
**Coupling**: Low
**Async**: Yes

### Event-Driven

```python
event_bus.emit("task:created", task)

@event_bus.on("task:created")
def handle_task(task):
    result = process(task)
    event_bus.emit("task:completed", result)
```

**Latency**: Variable
**Coupling**: Lowest
**Async**: Yes

## Output Template

```markdown
## Multi-Agent Analysis: [Framework Name]

### Coordination Model
- **Type**: [Supervisor/Peer-to-Peer/Pipeline/Market]
- **Central Control**: [Yes/No]
- **Location**: `path/to/orchestrator.py`

### Agent Inventory

| Agent | Role | Can Delegate To |
|-------|------|-----------------|
| Supervisor | Routing | All workers |
| SearchAgent | Web search | None |
| CodeAgent | Code execution | Reviewer |

### Handoff Mechanism
- **Type**: [Explicit/Router/Implicit]
- **Bidirectional**: [Yes/No]
- **Context Preserved**: [Full/Partial/Minimal]

### State Sharing
- **Pattern**: [Blackboard/Message/Hybrid]
- **Shared State**: [List what's shared]
- **Isolation Level**: [None/Partial/Full]

### Communication Protocol
- **Method**: [Direct/Queue/Event]
- **Async**: [Yes/No]
- **Location**: `path/to/comms.py`

### Loop Prevention
- **Mechanism**: [Depth limit/Visited set/None]
- **Max Handoffs**: [N or Unlimited]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify agent files
- **Feeds into**: `comparative-matrix` for coordination decisions
- **Related**: `control-loop-extraction` for individual agent loops
