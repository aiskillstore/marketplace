"""
Multi-Agent Coordination

This module provides utilities for implementing multi-agent coordination patterns.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    HANDOVER = "handover"
    FEEDBACK = "feedback"
    ALERT = "alert"


@dataclass
class AgentMessage:
    """Message exchanged between agents."""
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requires_response: bool = False
    priority: int = 0  # 0 = normal, higher = more urgent


class AgentCommunication:
    """Communication channel for multi-agent systems."""
    
    def __init__(self):
        self.inbox: Dict[str, List[AgentMessage]] = {}
        self.outbox: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []
    
    def send(self, message: AgentMessage):
        """Send a message to an agent."""
        if message.receiver not in self.inbox:
            self.inbox[message.receiver] = []
        self.inbox[message.receiver].append(message)
        self.outbox.append(message)
        self.message_history.append(message)
    
    def receive(self, agent_id: str) -> List[AgentMessage]:
        """Receive all messages for an agent."""
        messages = self.inbox.get(agent_id, [])
        self.inbox[agent_id] = []  # Clear inbox after receiving
        return messages
    
    def broadcast(self, sender: str, message_type: MessageType, 
                  content: Dict[str, Any], receivers: List[str]):
        """Broadcast message to multiple agents."""
        for receiver in receivers:
            self.send(AgentMessage(
                sender=sender,
                receiver=receiver,
                message_type=message_type,
                content=content
            ))


# Supervisor Pattern Implementation

class SupervisorAgent:
    """
    Central supervisor agent that coordinates worker agents.
    """
    
    def __init__(self, name: str, communication: AgentCommunication):
        self.name = name
        self.communication = communication
        self.workers: Dict[str, Dict] = {}
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.current_state: Dict = {}
    
    def register_worker(self, worker_id: str, capabilities: List[str]):
        """Register a worker agent with the supervisor."""
        self.workers[worker_id] = {
            "capabilities": capabilities,
            "status": "available",
            "current_task": None,
            "metrics": {"tasks_completed": 0, "avg_response_time": 0}
        }
    
    def decompose_task(self, task: Dict) -> List[Dict]:
        """
        Decompose a task into subtasks.
        
        In production, this would use task analysis and planning.
        """
        subtasks = []
        
        # Simple decomposition based on task type
        task_type = task.get("type", "general")
        
        if task_type == "research":
            subtasks = [
                {"type": "search", "description": "Gather information"},
                {"type": "analyze", "description": "Analyze findings"},
                {"type": "synthesize", "description": "Synthesize results"}
            ]
        elif task_type == "create":
            subtasks = [
                {"type": "plan", "description": "Create plan"},
                {"type": "draft", "description": "Draft content"},
                {"type": "review", "description": "Review and refine"}
            ]
        else:
            subtasks = [
                {"type": "execute", "description": task.get("description", "Execute task")}
            ]
        
        # Add parent task info
        for subtask in subtasks:
            subtask["parent_task"] = task.get("id")
            subtask["priority"] = task.get("priority", 0)
        
        return subtasks
    
    def assign_task(self, subtask: Dict, worker_id: str):
        """Assign a subtask to a worker agent."""
        if worker_id not in self.workers:
            raise ValueError(f"Unknown worker: {worker_id}")
        
        self.workers[worker_id]["status"] = "busy"
        self.workers[worker_id]["current_task"] = subtask["id"]
        
        self.send(AgentMessage(
            sender=self.name,
            receiver=worker_id,
            message_type=MessageType.REQUEST,
            content={
                "action": "execute_task",
                "task": subtask
            },
            requires_response=True,
            priority=subtask.get("priority", 0)
        ))
    
    def select_worker(self, subtask: Dict) -> str:
        """Select the best worker for a subtask."""
        required_capability = subtask.get("type", "general")
        
        # Find available workers with required capability
        candidates = [
            wid for wid, info in self.workers.items()
            if info["status"] == "available"
            and required_capability in info["capabilities"]
        ]
        
        if not candidates:
            # Fall back to any available worker
            candidates = [
                wid for wid, info in self.workers.items()
                if info["status"] == "available"
            ]
        
        if not candidates:
            raise ValueError("No available workers")
        
        # Select based on metrics (fewest tasks completed = most available)
        return min(candidates, key=lambda w: self.workers[w]["metrics"]["tasks_completed"])
    
    def aggregate_results(self, subtask_results: List[Dict]) -> Dict:
        """Aggregate results from subtasks."""
        aggregated = {
            "results": subtask_results,
            "summary": "",
            "quality_score": 0.0
        }
        
        # Generate summary from results
        summaries = [r.get("summary", "") for r in subtask_results if r.get("success")]
        aggregated["summary"] = " | ".join(summaries)
        
        # Calculate quality score
        successful = sum(1 for r in subtask_results if r.get("success", False))
        aggregated["quality_score"] = successful / len(subtask_results) if subtask_results else 0
        
        return aggregated
    
    def run_workflow(self, task: Dict) -> Dict:
        """Execute a complete workflow with supervision."""
        # Decompose task
        subtasks = self.decompose_task(task)
        
        # Assign subtasks
        results = []
        for subtask in subtasks:
            worker = self.select_worker(subtask)
            self.assign_task(subtask, worker)
            
            # Wait for result
            messages = self.receive(self.name)
            for msg in messages:
                if msg.message_type == MessageType.RESPONSE:
                    results.append(msg.content)
        
        # Aggregate results
        final_result = self.aggregate_results(results)
        
        return {
            "task": task,
            "subtask_results": results,
            "final_result": final_result,
            "success": final_result["quality_score"] >= 0.8
        }
    
    def send(self, message: AgentMessage):
        """Send message through communication channel."""
        self.communication.send(message)


# Handoff Protocol

class HandoffProtocol:
    """
    Protocol for agent-to-agent handoffs.
    """
    
    def __init__(self, communication: AgentCommunication):
        self.communication = communication
    
    def create_handoff(self, from_agent: str, to_agent: str, 
                       context: Dict, reason: str) -> AgentMessage:
        """Create a handoff message."""
        return AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.HANDOVER,
            content={
                "handoff_reason": reason,
                "transferred_context": context,
                "handoff_timestamp": time.time()
            },
            priority=1
        )
    
    def accept_handoff(self, agent_id: str) -> Optional[AgentMessage]:
        """Accept pending handoff for an agent."""
        messages = self.communication.receive(agent_id)
        
        for msg in messages:
            if msg.message_type == MessageType.HANDOVER:
                return msg
        
        return None
    
    def transfer_with_state(self, from_agent: str, to_agent: str,
                           state: Dict, task: Dict) -> bool:
        """
        Transfer task state from one agent to another.
        
        Returns success status.
        """
        handoff = self.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            context={
                "task_state": state,
                "task_details": task,
                "progress": state.get("progress", 0)
            },
            reason="task_transfer"
        )
        
        self.communication.send(handoff)
        
        # Wait for acknowledgment
        time.sleep(0.1)  # In production, use async with timeout
        ack = self.communication.receive(from_agent)
        
        return any(
            m.message_type == MessageType.RESPONSE and 
            m.content.get("status") == "handoff_received"
            for m in ack
        )


# Consensus Mechanism

class ConsensusManager:
    """
    Manager for multi-agent consensus building.
    """
    
    def __init__(self):
        self.votes: Dict[str, List[Dict]] = {}
        self.debates: Dict[str, List[Dict]] = {}
    
    def initiate_vote(self, topic_id: str, agents: List[str], 
                      options: List[str]):
        """Initiate a voting round on a topic."""
        self.votes[topic_id] = []
        
        # Request votes from agents
        for agent in agents:
            vote_request = {
                "agent": agent,
                "topic": topic_id,
                "options": options,
                "status": "pending"
            }
            self.votes[topic_id].append(vote_request)
    
    def submit_vote(self, topic_id: str, agent_id: str, 
                    selection: str, confidence: float):
        """Submit a vote for a topic."""
        if topic_id not in self.votes:
            raise ValueError(f"Unknown topic: {topic_id}")
        
        vote_record = {
            "agent": agent_id,
            "selection": selection,
            "confidence": confidence,
            "timestamp": time.time()
        }
        
        for vote in self.votes[topic_id]:
            if vote["agent"] == agent_id:
                vote["status"] = "cast"
                vote["selection"] = selection
                vote["confidence"] = confidence
                break
    
    def calculate_weighted_consensus(self, topic_id: str) -> Dict:
        """
        votes.
        
        Weight = confidence * expertise_factor
        Calculate weighted consensus from """
        if topic_id not in self.votes:
            raise ValueError(f"Unknown topic: {topic_id}")
        
        votes = [v for v in self.votes[topic_id] if v.get("status") == "cast"]
        
        if not votes:
            return {"status": "no_votes", "result": None}
        
        # Group by selection
        selections: Dict[str, List[Dict]] = {}
        for vote in votes:
            selection = vote["selection"]
            if selection not in selections:
                selections[selection] = []
            selections[selection].append(vote)
        
        # Calculate weighted score for each selection
        results = {}
        for selection, selection_votes in selections.items():
            weighted_sum = sum(v["confidence"] for v in selection_votes)
            avg_confidence = weighted_sum / len(selection_votes) if selection_votes else 0
            results[selection] = {
                "weighted_score": weighted_sum,
                "avg_confidence": avg_confidence,
                "vote_count": len(selection_votes)
            }
        
        # Select winner
        winner = max(results.keys(), key=lambda s: results[s]["weighted_score"])
        
        return {
            "status": "complete",
            "result": winner,
            "details": results,
            "consensus_strength": results[winner]["weighted_score"] / len(votes) if votes else 0
        }


# Failure Handling

class AgentFailureHandler:
    """
    Handler for agent failures in multi-agent systems.
    """
    
    def __init__(self, communication: AgentCommunication, 
                 max_retries: int = 3):
        self.communication = communication
        self.max_retries = max_retries
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}  # agent -> unlock time
    
    def handle_failure(self, agent_id: str, task_id: str, 
                       error: str) -> Dict:
        """
        Handle a failure from an agent.
        
        Returns action to take.
        """
        # Increment failure count
        self.failure_counts[agent_id] = self.failure_counts.get(agent_id, 0) + 1
        
        # Check if circuit breaker should activate
        if self.failure_counts[agent_id] >= self.max_retries:
            self._activate_circuit_breaker(agent_id)
            return {
                "action": "reroute",
                "reason": "circuit_breaker_activated",
                "alternative": self._find_alternative_agent(agent_id)
            }
        
        return {
            "action": "retry",
            "reason": error,
            "retry_count": self.failure_counts[agent_id],
            "delay": min(2 ** self.failure_counts[agent_id], 60)  # Exponential backoff
        }
    
    def _activate_circuit_breaker(self, agent_id: str):
        """Temporarily disable an agent."""
        self.circuit_breakers[agent_id] = time.time() + 60  # 1 minute cooldown
    
    def _find_alternative_agent(self, failed_agent: str) -> str:
        """Find an alternative agent to handle the task."""
        # In production, this would check agent capabilities and availability
        return "default_backup_agent"
    
    def is_available(self, agent_id: str) -> bool:
        """Check if an agent is available (circuit breaker not active)."""
        if agent_id in self.circuit_breakers:
            if time.time() < self.circuit_breakers[agent_id]:
                return False
            # Reset after cooldown
            del self.circuit_breakers[agent_id]
            self.failure_counts[agent_id] = 0
        return True
    
    def record_success(self, agent_id: str):
        """Record a successful task completion."""
        self.failure_counts[agent_id] = 0
