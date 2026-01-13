# Flow Nexus Cloud Swarm - Quick Start

Deploy cloud-based AI agent swarms with event-driven workflow automation.

## Quick Start

```bash
# 1. Initialize swarm
mcp__flow-nexus__swarm_init {
  "topology": "hierarchical",
  "maxAgents": 8
}

# 2. Spawn agents
mcp__flow-nexus__agent_spawn { "type": "coordinator" }
mcp__flow-nexus__agent_spawn { "type": "analyst" }
mcp__flow-nexus__agent_spawn { "type": "coder" }

# 3. Create workflow
mcp__flow-nexus__workflow_create {
  "name": "Development Workflow",
  "steps": [...]
}

# 4. Monitor
mcp__flow-nexus__swarm_status
./swarm/monitoring/monitor-agents.sh

# 5. Scale
mcp__flow-nexus__swarm_scale { "target_agents": 10 }
```

## What This Skill Does

- **Initialize**: Create cloud swarm with chosen topology
- **Deploy**: Launch agents in E2B sandboxes
- **Coordinate**: Event-driven workflow execution
- **Monitor**: Track performance and metrics
- **Scale**: Dynamic auto-scaling based on load

## When to Use

- Distributed agent coordination
- Complex multi-step workflows
- Event-driven processing
- Cloud-based AI systems
- Auto-scaling requirements

## Agents Involved

- **hierarchical-coordinator**: Swarm orchestration
- **flow-nexus-swarm**: Cloud platform management
- **adaptive-coordinator**: Performance optimization

## Success Criteria

- Swarm deployed (8-10 agents)
- Workflows executing
- Auto-scaling active
- Performance monitored

## Duration

40-70 minutes

## See Also

- Full SOP: [SKILL.md](SKILL.md)
- Detailed Process: [PROCESS.md](PROCESS.md)
- Visual Workflow: [process-diagram.gv](process-diagram.gv)
