---
name: event-driven-architecture
description: Generic Event-Driven Architecture patterns with Kafka, Dapr, and modern messaging systems. Provides reusable patterns for building scalable, resilient event-driven microservices. Framework-agnostic implementation supporting multiple message brokers, state stores, and event patterns. Follows 2025 best practices for distributed systems.
license: MIT
---

# Event-Driven Architecture with Modern Patterns

This skill provides comprehensive patterns for implementing event-driven microservices using modern messaging systems, distributed runtimes, and cloud-native patterns. It's designed to be framework-agnostic and applicable to any domain requiring event-driven capabilities.

## When to Use This Skill

Use this skill when you need to:
- Build event-driven microservices architecture
- Implement pub/sub patterns with Kafka, RabbitMQ, or cloud services
- Use Dapr for distributed application patterns
- Implement real-time notifications and workflows
- Build recurring task and reminder systems
- Create audit trails and activity logs
- Implement distributed state management
- Build serverless event workflows
- Handle event sourcing and CQRS patterns

## 1. Core Event Architecture

### Base Event Schema

```python
# events/core.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, Union, List
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import json

class EventVersion(str, Enum):
    """Event versioning support"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"

class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class BaseEvent(BaseModel, ABC):
    """Base event schema with common fields"""

    # Core identification
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Type of the event")
    event_version: EventVersion = Field(default=EventVersion.V1_0)

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # Event that caused this one
    source: str = Field(..., description="Source service/identifier")

    # Context
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None  # Multi-tenant support
    session_id: Optional[str] = None

    # Processing metadata
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    delay_until: Optional[datetime] = None  # For delayed processing

    # Schema versioning
    schema_version: str = Field(default="1.0")

    class Config:
        # Allow additional fields for extensibility
        extra = "allow"
        # Use enum values
        use_enum_values = True

    @validator('event_type')
    def validate_event_type(cls, v):
        """Validate event type format"""
        if not v or '.' not in v:
            raise ValueError('event_type must be in format: domain.event_name')
        return v.lower()

    @validator('correlation_id')
    def validate_correlation_id(cls, v, values):
        """Set correlation_id from causation_id if not provided"""
        if not v and 'causation_id' in values:
            return values['causation_id']
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """Create event from dictionary"""
        return cls(**data)

    def with_context(self, **context) -> 'BaseEvent':
        """Add context to event"""
        for key, value in context.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

class DomainEvent(BaseEvent):
    """Domain-specific event"""

    aggregate_id: str = Field(..., description="Aggregate root ID")
    aggregate_type: str = Field(..., description="Aggregate type")
    event_data: Dict[str, Any] = Field(default_factory=dict)

    @validator('aggregate_type')
    def validate_aggregate_type(cls, v):
        """Validate aggregate type"""
        if not v:
            raise ValueError('aggregate_type is required')
        return v.lower()

class IntegrationEvent(BaseEvent):
    """Integration event for cross-service communication"""

    target_services: List[str] = Field(default_factory=list)
    routing_key: Optional[str] = None
    message_format: str = Field(default="json")

    @validator('routing_key')
    def validate_routing_key(cls, v, values):
        """Generate routing key from event_type if not provided"""
        if not v and 'event_type' in values:
            return values['event_type'].replace('.', '/')
        return v

class CommandEvent(BaseEvent):
    """Command event representing an intent"""

    command_type: str = Field(..., description="Type of command")
    command_data: Dict[str, Any] = Field(default_factory=dict)
    expected_version: Optional[int] = None  # For optimistic concurrency

    @validator('command_type')
    def validate_command_type(cls, v):
        """Validate command type"""
        if not v.endswith('.command'):
            v = f"{v}.command"
        return v.lower()

class QueryEvent(BaseEvent):
    """Query event for data retrieval"""

    query_type: str = Field(..., description="Type of query")
    query_params: Dict[str, Any] = Field(default_factory=dict)
    result_topic: Optional[str] = None  # Where to send results

    @validator('query_type')
    def validate_query_type(cls, v):
        """Validate query type"""
        if not v.endswith('.query'):
            v = f"{v}.query"
        return v.lower()
```

### Event Store Pattern

```python
# events/store.py
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime, timedelta
import json
import uuid

class EventStore(ABC):
    """Abstract event store interface"""

    @abstractmethod
    async def save_event(self, event: BaseEvent, stream_id: str) -> None:
        """Save event to a stream"""
        pass

    @abstractmethod
    async def get_events(
        self,
        stream_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events from a stream"""
        pass

    @abstractmethod
    async def get_event_by_id(self, event_id: str) -> Optional[BaseEvent]:
        """Get a specific event by ID"""
        pass

    @abstractmethod
    async def get_events_by_type(
        self,
        event_type: str,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events by type"""
        pass

    @abstractmethod
    async def get_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get aggregate snapshot"""
        pass

    @abstractmethod
    async def save_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str,
        data: Dict[str, Any],
        version: int
    ) -> None:
        """Save aggregate snapshot"""
        pass

class InMemoryEventStore(EventStore):
    """In-memory event store for testing and development"""

    def __init__(self):
        self._events: Dict[str, List[BaseEvent]] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}
        self._type_index: Dict[str, List[str]] = {}

    async def save_event(self, event: BaseEvent, stream_id: str) -> None:
        """Save event to memory"""
        if stream_id not in self._events:
            self._events[stream_id] = []

        self._events[stream_id].append(event)

        # Update type index
        if event.event_type not in self._type_index:
            self._type_index[event.event_type] = []
        self._type_index[event.event_type].append(event.event_id)

    async def get_events(
        self,
        stream_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events from memory"""
        events = self._events.get(stream_id, [])

        # Apply filters
        if from_version is not None:
            events = events[from_version:]
        if to_version is not None:
            events = events[:to_version]
        if limit is not None:
            events = events[:limit]

        for event in events:
            yield event

    async def get_event_by_id(self, event_id: str) -> Optional[BaseEvent]:
        """Get event by ID from memory"""
        for events in self._events.values():
            for event in events:
                if event.event_id == event_id:
                    return event
        return None

    async def get_events_by_type(
        self,
        event_type: str,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events by type from memory"""
        event_ids = self._type_index.get(event_type, [])

        for event_id in event_ids:
            event = await self.get_event_by_id(event_id)
            if event:
                # Apply time filters
                if from_timestamp and event.timestamp < from_timestamp:
                    continue
                if to_timestamp and event.timestamp > to_timestamp:
                    continue
                yield event

    async def get_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get snapshot from memory"""
        snapshot_key = f"{aggregate_type}:{aggregate_id}"
        return self._snapshots.get(snapshot_key)

    async def save_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str,
        data: Dict[str, Any],
        version: int
    ) -> None:
        """Save snapshot to memory"""
        snapshot_key = f"{aggregate_type}:{aggregate_id}"
        self._snapshots[snapshot_key] = {
            "data": data,
            "version": version,
            "timestamp": datetime.utcnow()
        }

# PostgreSQL Event Store Implementation
class PostgreSQLEventStore(EventStore):
    """PostgreSQL-based event store"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def initialize_schema(self):
        """Initialize database schema"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS event_store (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    stream_id VARCHAR(255) NOT NULL,
                    stream_version INTEGER NOT NULL,
                    event_id VARCHAR(255) UNIQUE NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    event_data JSONB NOT NULL,
                    metadata JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    INDEX (stream_id, stream_version),
                    INDEX (event_type),
                    INDEX (timestamp)
                );

                CREATE TABLE IF NOT EXISTS snapshots (
                    aggregate_id VARCHAR(255) NOT NULL,
                    aggregate_type VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    version INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    PRIMARY KEY (aggregate_type, aggregate_id)
                );
            """)

    async def save_event(self, event: BaseEvent, stream_id: str) -> None:
        """Save event to PostgreSQL"""
        async with self.db_pool.acquire() as conn:
            # Get next version
            result = await conn.fetchval(
                "SELECT COALESCE(MAX(stream_version), 0) + 1 FROM event_store WHERE stream_id = $1",
                stream_id
            )

            await conn.execute(
                """
                INSERT INTO event_store (
                    stream_id, stream_version, event_id, event_type,
                    event_data, metadata, timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                stream_id,
                result,
                event.event_id,
                event.event_type,
                event.to_dict(),
                {
                    "correlation_id": event.correlation_id,
                    "causation_id": event.causation_id,
                    "source": event.source,
                    "user_id": event.user_id,
                    "tenant_id": event.tenant_id
                },
                event.timestamp
            )

    async def get_events(
        self,
        stream_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events from PostgreSQL"""
        query = "SELECT event_data FROM event_store WHERE stream_id = $1"
        params = [stream_id]

        if from_version is not None:
            query += " AND stream_version >= $2"
            params.append(from_version)
            version_offset = 2
        else:
            version_offset = 1

        if to_version is not None:
            query += f" AND stream_version <= ${version_offset + 1}"
            params.append(to_version)
            version_offset += 1

        query += " ORDER BY stream_version"

        if limit is not None:
            query += f" LIMIT ${version_offset + 1}"
            params.append(limit)

        async with self.db_pool.acquire() as conn:
            async for row in conn.cursor(query, *params):
                yield BaseEvent.from_dict(row["event_data"])

    async def get_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get snapshot from PostgreSQL"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT data, version FROM snapshots
                WHERE aggregate_id = $1 AND aggregate_type = $2
                """,
                aggregate_id,
                aggregate_type
            )

            if row:
                return {
                    "data": row["data"],
                    "version": row["version"]
                }
            return None

    async def save_aggregate_snapshot(
        self,
        aggregate_id: str,
        aggregate_type: str,
        data: Dict[str, Any],
        version: int
    ) -> None:
        """Save snapshot to PostgreSQL"""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO snapshots (aggregate_id, aggregate_type, data, version, timestamp)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (aggregate_type, aggregate_id)
                DO UPDATE SET data = $3, version = $4, timestamp = NOW()
                """,
                aggregate_id,
                aggregate_type,
                data,
                version
            )
```

## 2. Message Broker Abstraction

### Generic Message Broker Interface

```python
# messaging/broker.py
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class MessageBrokerType(str, Enum):
    """Supported message broker types"""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"
    AWS_SQS = "aws_sqs"
    AZURE_SB = "azure_service_bus"
    GCP_PUBSUB = "gcp_pubsub"
    NATS = "nats"
    EMQX = "emqx"

@dataclass
class Message:
    """Generic message representation"""
    topic: str
    key: Optional[str]
    value: Any
    headers: Optional[Dict[str, str]] = None
    partition: Optional[int] = None
    timestamp: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "topic": self.topic,
            "key": self.key,
            "value": self.value,
            "headers": self.headers or {},
            "partition": self.partition,
            "timestamp": self.timestamp
        }

class MessageBroker(ABC):
    """Abstract message broker interface"""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to broker"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to broker"""
        pass

    @abstractmethod
    async def publish(self, message: Message) -> None:
        """Publish a message"""
        pass

    @abstractmethod
    async def publish_batch(self, messages: List[Message]) -> None:
        """Publish multiple messages"""
        pass

    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], None],
        group_id: Optional[str] = None
    ) -> None:
        """Subscribe to a topic"""
        pass

    @abstractmethod
    async def create_topic(self, topic: str, **kwargs) -> None:
        """Create a topic if it doesn't exist"""
        pass

class KafkaBroker(MessageBroker):
    """Kafka message broker implementation"""

    def __init__(
        self,
        bootstrap_servers: str,
        producer_config: Optional[Dict[str, Any]] = None,
        consumer_config: Optional[Dict[str, Any]] = None
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer_config = producer_config or {}
        self.consumer_config = consumer_config or {}
        self.producer = None
        self.consumers: List[Any] = []

        # Default configurations
        self.producer_config.update({
            'bootstrap_servers': bootstrap_servers,
            'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
            'key_serializer': lambda k: k.encode('utf-8') if k else None,
            'acks': 'all',
            'retries': 3,
            'retry_backoff_ms': 100
        })

        self.consumer_config.update({
            'bootstrap_servers': bootstrap_servers,
            'value_deserializer': lambda v: json.loads(v.decode('utf-8')),
            'key_deserializer': lambda k: k.decode('utf-8') if k else None,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': True
        })

    async def connect(self) -> None:
        """Connect to Kafka"""
        from aiokafka import AIOKafkaProducer

        self.producer = AIOKafkaProducer(**self.producer_config)
        await self.producer.start()
        logger.info("Connected to Kafka broker")

    async def disconnect(self) -> None:
        """Disconnect from Kafka"""
        if self.producer:
            await self.producer.stop()

        for consumer in self.consumers:
            await consumer.stop()

        logger.info("Disconnected from Kafka broker")

    async def publish(self, message: Message) -> None:
        """Publish message to Kafka"""
        if not self.producer:
            raise RuntimeError("Producer not initialized")

        await self.producer.send_and_wait(
            topic=message.topic,
            value=message.value,
            key=message.key,
            headers=message.headers,
            partition=message.partition
        )

    async def publish_batch(self, messages: List[Message]) -> None:
        """Publish batch of messages to Kafka"""
        if not self.producer:
            raise RuntimeError("Producer not initialized")

        # Group messages by topic
        topics = {}
        for msg in messages:
            if msg.topic not in topics:
                topics[msg.topic] = []
            topics[msg.topic].append(msg)

        # Send batched messages
        for topic, topic_messages in topics.items():
            for msg in topic_messages:
                await self.producer.send_and_wait(
                    topic=topic,
                    value=msg.value,
                    key=msg.key,
                    headers=msg.headers,
                    partition=msg.partition
                )

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], None],
        group_id: Optional[str] = None
    ) -> None:
        """Subscribe to Kafka topic"""
        from aiokafka import AIOKafkaConsumer

        consumer_config = self.consumer_config.copy()
        if group_id:
            consumer_config['group_id'] = group_id

        consumer = AIOKafkaConsumer(topic, **consumer_config)
        await consumer.start()
        self.consumers.append(consumer)

        # Start consuming task
        asyncio.create_task(self._consume_messages(consumer, handler))

    async def _consume_messages(
        self,
        consumer: Any,
        handler: Callable[[Message], None]
    ) -> None:
        """Consume messages from Kafka"""
        try:
            async for msg in consumer:
                message = Message(
                    topic=msg.topic,
                    key=msg.key,
                    value=msg.value,
                    headers=dict(msg.headers) if msg.headers else {},
                    partition=msg.partition,
                    timestamp=msg.timestamp
                )

                try:
                    await self._handle_message(handler, message)
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)

    async def _handle_message(
        self,
        handler: Callable[[Message], None],
        message: Message
    ) -> None:
        """Handle a single message"""
        if asyncio.iscoroutinefunction(handler):
            await handler(message)
        else:
            # Run sync handler in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler, message)

    async def create_topic(self, topic: str, **kwargs) -> None:
        """Create Kafka topic"""
        from aiokafka.admin import AIOKafkaAdminClient, NewTopic

        admin_client = AIOKafkaAdminClient(
            bootstrap_servers=self.bootstrap_servers
        )

        try:
            await admin_client.start()

            topic_metadata = NewTopic(
                name=topic,
                num_partitions=kwargs.get('num_partitions', 3),
                replication_factor=kwargs.get('replication_factor', 1)
            )

            await admin_client.create_topics([topic_metadata])
            logger.info(f"Created topic: {topic}")
        except Exception as e:
            logger.warning(f"Failed to create topic {topic}: {e}")
        finally:
            await admin_client.close()

class RedisBroker(MessageBroker):
    """Redis-based message broker using streams"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
        self.consumer_groups: Dict[str, str] = {}

    async def connect(self) -> None:
        """Connect to Redis"""
        import aioredis

        self.redis = aioredis.from_url(self.redis_url)
        await self.redis.ping()
        logger.info("Connected to Redis broker")

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    async def publish(self, message: Message) -> None:
        """Publish message to Redis stream"""
        if not self.redis:
            raise RuntimeError("Redis not initialized")

        message_data = {
            'key': message.key,
            'value': json.dumps(message.value),
            'headers': json.dumps(message.headers or {}),
            'timestamp': message.timestamp or int(time.time() * 1000)
        }

        await self.redis.xadd(message.topic, message_data)

    async def publish_batch(self, messages: List[Message]) -> None:
        """Publish batch to Redis streams"""
        # Redis doesn't have native batch xadd, so we use pipeline
        pipe = self.redis.pipeline()

        for message in messages:
            message_data = {
                'key': message.key,
                'value': json.dumps(message.value),
                'headers': json.dumps(message.headers or {}),
                'timestamp': message.timestamp or int(time.time() * 1000)
            }
            pipe.xadd(message.topic, message_data)

        await pipe.execute()

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], None],
        group_id: Optional[str] = None
    ) -> None:
        """Subscribe to Redis stream"""
        if group_id:
            self.consumer_groups[topic] = group_id
            try:
                await self.redis.xgroup_create(topic, group_id, id='0', mkstream=True)
            except Exception:
                pass  # Group might already exist

        # Start consuming task
        asyncio.create_task(self._consume_stream(topic, handler, group_id))

    async def _consume_stream(
        self,
        topic: str,
        handler: Callable[[Message], None],
        group_id: Optional[str]
    ) -> None:
        """Consume messages from Redis stream"""
        while True:
            try:
                if group_id:
                    # Consumer group mode
                    messages = await self.redis.xreadgroup(
                        group_id,
                        'consumer',
                        {topic: '>'},
                        count=10,
                        block=1000
                    )
                else:
                    # Independent consumer mode
                    messages = await self.redis.xread(
                        {topic: '$'},
                        count=10,
                        block=1000
                    )

                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        message = Message(
                            topic=topic,
                            key=fields.get('key'),
                            value=json.loads(fields['value']),
                            headers=json.loads(fields.get('headers', '{}')),
                            timestamp=int(fields.get('timestamp', 0))
                        )

                        try:
                            await self._handle_message(handler, message)

                            if group_id:
                                await self.redis.xack(topic, group_id, msg_id)
                        except Exception as e:
                            logger.error(f"Error handling message: {e}")
            except Exception as e:
                logger.error(f"Stream consumer error: {e}")
                await asyncio.sleep(1)

class MessageBrokerFactory:
    """Factory for creating message brokers"""

    @staticmethod
    def create(broker_type: MessageBrokerType, **kwargs) -> MessageBroker:
        """Create a message broker instance"""
        if broker_type == MessageBrokerType.KAFKA:
            return KafkaBroker(
                bootstrap_servers=kwargs['bootstrap_servers'],
                producer_config=kwargs.get('producer_config'),
                consumer_config=kwargs.get('consumer_config')
            )
        elif broker_type == MessageBrokerType.REDIS:
            return RedisBroker(redis_url=kwargs['redis_url'])
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")
```

## 3. Event Processing Patterns

### Saga Pattern Implementation

```python
# patterns/saga.py
import asyncio
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
import logging

logger = logging.getLogger(__name__)

class SagaStatus(str, Enum):
    """Saga status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"

@dataclass
class SagaStep:
    """Single step in a saga"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: Optional[Callable] = None
    compensation: Optional[Callable] = None
    params: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    completed: bool = False
    result: Any = None

class Saga:
    """Saga orchestrator for distributed transactions"""

    def __init__(self, saga_id: Optional[str] = None):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.status = SagaStatus.PENDING
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.current_step_index = 0
        self.error: Optional[Exception] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_step(
        self,
        action: Callable,
        compensation: Callable,
        params: Dict[str, Any] = None,
        max_retries: int = 3,
        timeout: float = 30.0
    ) -> 'Saga':
        """Add a step to the saga"""
        step = SagaStep(
            action=action,
            compensation=compensation,
            params=params or {},
            max_retries=max_retries,
            timeout=timeout
        )
        self.steps.append(step)
        return self

    async def execute(self) -> bool:
        """Execute the saga"""
        try:
            self.status = SagaStatus.RUNNING
            self.updated_at = datetime.utcnow()

            logger.info(f"Starting saga {self.saga_id} with {len(self.steps)} steps")

            # Execute all steps
            for i, step in enumerate(self.steps):
                self.current_step_index = i

                if not await self._execute_step(step):
                    # Step failed, start compensation
                    await self._compensate()
                    return False

                self.completed_steps.append(step)

            # All steps completed successfully
            self.status = SagaStatus.COMPLETED
            self.updated_at = datetime.utcnow()
            logger.info(f"Saga {self.saga_id} completed successfully")
            return True

        except Exception as e:
            self.error = e
            logger.error(f"Saga {self.saga_id} failed: {e}")
            await self._compensate()
            return False

    async def _execute_step(self, step: SagaStep) -> bool:
        """Execute a single step"""
        logger.info(f"Executing step {step.step_id}")

        while step.retry_count <= step.max_retries:
            try:
                # Execute with timeout
                step.result = await asyncio.wait_for(
                    self._run_action(step.action, step.params),
                    timeout=step.timeout
                )

                step.completed = True
                logger.info(f"Step {step.step_id} completed successfully")
                return True

            except asyncio.TimeoutError:
                step.retry_count += 1
                logger.warning(f"Step {step.step_id} timed out, retry {step.retry_count}")
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff

            except Exception as e:
                step.retry_count += 1
                logger.error(f"Step {step.step_id} failed: {e}")

                if step.retry_count > step.max_retries:
                    logger.error(f"Step {step.step_id} failed after {step.max_retries} retries")
                    self.error = e
                    return False

                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff

        return False

    async def _run_action(self, action: Callable, params: Dict[str, Any]) -> Any:
        """Run action with parameters"""
        if asyncio.iscoroutinefunction(action):
            return await action(**params)
        else:
            # Run sync action in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, action, **params)

    async def _compensate(self) -> None:
        """Compensate completed steps"""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.utcnow()

        logger.info(f"Starting compensation for saga {self.saga_id}")

        # Compensate in reverse order
        for step in reversed(self.completed_steps):
            try:
                await self._compensate_step(step)
            except Exception as e:
                logger.error(f"Compensation failed for step {step.step_id}: {e}")
                # Continue with other compensations

        self.status = SagaStatus.COMPENSATED if self.error else SagaStatus.FAILED
        self.updated_at = datetime.utcnow()

        status_str = "compensated" if self.error else "failed"
        logger.info(f"Saga {self.saga_id} {status_str}")

    async def _compensate_step(self, step: SagaStep) -> None:
        """Compensate a single step"""
        logger.info(f"Compensating step {step.step_id}")

        compensation_params = step.params.copy()
        compensation_params['result'] = step.result

        if step.compensation:
            if asyncio.iscoroutinefunction(step.compensation):
                await step.compensation(**compensation_params)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    step.compensation,
                    **compensation_params
                )

class SagaManager:
    """Manages multiple sagas"""

    def __init__(self, event_store: EventStore, message_broker: MessageBroker):
        self.event_store = event_store
        self.message_broker = message_broker
        self.active_sagas: Dict[str, Saga] = {}

    def create_saga(self, saga_id: Optional[str] = None) -> Saga:
        """Create a new saga"""
        saga = Saga(saga_id)
        self.active_sagas[saga.saga_id] = saga
        return saga

    async def execute_saga(self, saga: Saga) -> bool:
        """Execute a saga and persist its state"""
        # Save saga started event
        await self._save_saga_event(saga, "saga.started")

        # Execute saga
        result = await saga.execute()

        # Save saga completed/failed event
        event_type = "saga.completed" if result else "saga.failed"
        await self._save_saga_event(saga, event_type)

        # Remove from active sagas
        if saga.saga_id in self.active_sagas:
            del self.active_sagas[saga.saga_id]

        return result

    async def _save_saga_event(self, saga: Saga, event_type: str) -> None:
        """Save saga lifecycle event"""
        event = DomainEvent(
            event_type=event_type,
            event_data={
                "saga_id": saga.saga_id,
                "status": saga.status.value,
                "total_steps": len(saga.steps),
                "completed_steps": len(saga.completed_steps),
                "current_step": saga.current_step_index,
                "error": str(saga.error) if saga.error else None
            },
            aggregate_id=saga.saga_id,
            aggregate_type="saga",
            source="saga_manager"
        )

        await self.event_store.save_event(event, f"saga-{saga.saga_id}")

        # Also publish to message broker
        message = Message(
            topic="saga-events",
            key=saga.saga_id,
            value=event.to_dict()
        )
        await self.message_broker.publish(message)
```

### CQRS Pattern Implementation

```python
# patterns/cqrs.py
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class CommandResponse:
    """Response from command execution"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)

class Command(ABC):
    """Base command class"""

    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class CommandHandler(ABC, Generic[T]):
    """Base command handler"""

    @abstractmethod
    async def handle(self, command: T) -> CommandResponse:
        """Handle the command"""
        pass

class Query(ABC):
    """Base query class"""

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class QueryResult(ABC):
    """Base query result"""
    pass

class QueryHandler(ABC, Generic[T]):
    """Base query handler"""

    @abstractmethod
    async def handle(self, query: T) -> QueryResult:
        """Handle the query"""
        pass

class CommandBus:
    """Command bus for dispatching commands"""

    def __init__(self):
        self.handlers: Dict[Type[Command], CommandHandler] = {}
        self.middleware: List[Callable] = []

    def register(
        self,
        command_type: Type[Command],
        handler: CommandHandler
    ) -> None:
        """Register a command handler"""
        self.handlers[command_type] = handler
        logger.info(f"Registered handler for {command_type.__name__}")

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the command bus"""
        self.middleware.append(middleware)

    async def dispatch(self, command: Command) -> CommandResponse:
        """Dispatch a command to its handler"""
        command_type = type(command)

        if command_type not in self.handlers:
            return CommandResponse(
                success=False,
                message=f"No handler registered for {command_type.__name__}"
            )

        handler = self.handlers[command_type]

        # Apply middleware
        for middleware in self.middleware:
            command = await middleware(command)

        try:
            # Save command event
            await self._save_command_event(command)

            # Handle command
            response = await handler.handle(command)

            # Save response event
            await self._save_response_event(command, response)

            return response

        except Exception as e:
            logger.error(f"Error handling command {command_type.__name__}: {e}")
            return CommandResponse(
                success=False,
                message=str(e),
                errors=[str(e)]
            )

    async def _save_command_event(self, command: Command) -> None:
        """Save command event to event store"""
        # Implementation would save to event store
        pass

    async def _save_response_event(
        self,
        command: Command,
        response: CommandResponse
    ) -> None:
        """Save response event to event store"""
        # Implementation would save to event store
        pass

class QueryBus:
    """Query bus for dispatching queries"""

    def __init__(self):
        self.handlers: Dict[Type[Query], QueryHandler] = {}
        self.middleware: List[Callable] = []

    def register(
        self,
        query_type: Type[Query],
        handler: QueryHandler
    ) -> None:
        """Register a query handler"""
        self.handlers[query_type] = handler
        logger.info(f"Registered handler for {query_type.__name__}")

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the query bus"""
        self.middleware.append(middleware)

    async def dispatch(self, query: Query) -> QueryResult:
        """Dispatch a query to its handler"""
        query_type = type(query)

        if query_type not in self.handlers:
            raise ValueError(f"No handler registered for {query_type.__name__}")

        handler = self.handlers[query_type]

        # Apply middleware
        for middleware in self.middleware:
            query = await middleware(query)

        # Handle query
        return await handler.handle(query)

class EventProjector(ABC):
    """Base event projector for building read models"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    @abstractmethod
    async def project(self, event: BaseEvent) -> None:
        """Project an event to the read model"""
        pass

    async def project_from_stream(
        self,
        stream_id: str,
        from_version: Optional[int] = None
    ) -> None:
        """Project events from a stream"""
        async for event in self.event_store.get_events(
            stream_id,
            from_version=from_version
        ):
            await self.project(event)

    async def project_by_type(
        self,
        event_type: str,
        from_timestamp: Optional[datetime] = None
    ) -> None:
        """Project events by type"""
        async for event in self.event_store.get_events_by_type(
            event_type,
            from_timestamp=from_timestamp
        ):
            await self.project(event)

# Example CQRS Implementation
class CreateTaskCommand(Command):
    """Create task command"""

    def __init__(self, aggregate_id: str, title: str, description: str = None):
        super().__init__(aggregate_id)
        self.title = title
        self.description = description

class TaskCreatedEvent(DomainEvent):
    """Task created event"""

    def __init__(self, aggregate_id: str, title: str, description: str = None):
        super().__init__(
            event_type="task.created",
            aggregate_id=aggregate_id,
            aggregate_type="task",
            event_data={
                "title": title,
                "description": description
            }
        )

class TaskReadModel:
    """Task read model for queries"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task from read model"""
        return self.tasks.get(task_id)

    async def list_tasks(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all tasks or user's tasks"""
        tasks = list(self.tasks.values())
        if user_id:
            tasks = [t for t in tasks if t.get("user_id") == user_id]
        return tasks

class TaskProjector(EventProjector):
    """Task event projector"""

    def __init__(self, event_store: EventStore, read_model: TaskReadModel):
        super().__init__(event_store)
        self.read_model = read_model

    async def project(self, event: BaseEvent) -> None:
        """Project task events to read model"""
        if event.event_type == "task.created":
            await self._project_task_created(event)
        elif event.event_type == "task.updated":
            await self._project_task_updated(event)
        elif event.event_type == "task.deleted":
            await self._project_task_deleted(event)

    async def _project_task_created(self, event: DomainEvent) -> None:
        """Project task created event"""
        self.read_model.tasks[event.aggregate_id] = {
            "id": event.aggregate_id,
            "title": event.event_data["title"],
            "description": event.event_data.get("description"),
            "status": "todo",
            "created_at": event.timestamp,
            "updated_at": event.timestamp
        }

    async def _project_task_updated(self, event: DomainEvent) -> None:
        """Project task updated event"""
        if event.aggregate_id in self.read_model.tasks:
            task = self.read_model.tasks[event.aggregate_id]
            task.update(event.event_data)
            task["updated_at"] = event.timestamp

    async def _project_task_deleted(self, event: DomainEvent) -> None:
        """Project task deleted event"""
        if event.aggregate_id in self.read_model.tasks:
            del self.read_model.tasks[event.aggregate_id]
```

## 4. Dapr Integration Patterns

### Generic Dapr Client

```python
# dapr/client.py
import asyncio
import httpx
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class DaprClient:
    """Generic Dapr client with comprehensive feature support"""

    def __init__(
        self,
        dapr_port: int = 3500,
        dapr_host: str = "localhost",
        timeout: float = 30.0
    ):
        self.dapr_port = dapr_port
        self.dapr_host = dapr_host
        self.base_url = f"http://{dapr_host}:{dapr_port}/v1.0"
        self.timeout = timeout

        # HTTP client for Dapr API calls
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the Dapr client"""
        await self.client.aclose()

    # State Management
    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save state to Dapr state store"""
        url = f"{self.base_url}/state/{store_name}"

        state_item = {
            "key": key,
            "value": value
        }

        if metadata:
            state_item["metadata"] = metadata

        if options:
            state_item["options"] = options

        response = await self.client.post(url, json=[state_item])
        response.raise_for_status()

    async def get_state(
        self,
        store_name: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """Get state from Dapr state store"""
        url = f"{self.base_url}/state/{store_name}/{key}"

        params = {}
        if metadata:
            params["metadata"] = json.dumps(metadata)

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        if response.status_code == 204:
            return None

        return response.json()

    async def delete_state(
        self,
        store_name: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Delete state from Dapr state store"""
        url = f"{self.base_url}/state/{store_name}/{key}"

        params = {}
        if metadata:
            params["metadata"] = json.dumps(metadata)

        response = await self.client.delete(url, params=params)
        response.raise_for_status()

    async def get_bulk_state(
        self,
        store_name: str,
        keys: List[str],
        parallelism: int = 10,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get multiple state items"""
        url = f"{self.base_url}/state/{store_name}/bulk"

        request_data = {
            "keys": keys,
            "parallelism": parallelism
        }

        if metadata:
            request_data["metadata"] = metadata

        response = await self.client.post(url, json=request_data)
        response.raise_for_status()

        return response.json()

    # Pub/Sub
    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Publish event via Dapr pub/sub"""
        url = f"{self.base_url}/publish/{pubsub_name}/{topic}"

        headers = {}
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata-{key}"] = value

        response = await self.client.post(
            url,
            content=json.dumps(data),
            headers=headers
        )
        response.raise_for_status()

    # Service Invocation
    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: Any = None,
        http_verb: str = "POST",
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """Invoke a service method"""
        url = f"{self.base_url}/invoke/{app_id}/method/{method_name}"

        headers = {}
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata-{key}"] = value

        response = await self.client.request(
            http_verb,
            url,
            content=json.dumps(data) if data else None,
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    # Bindings
    async def invoke_binding(
        self,
        binding_name: str,
        operation: str,
        data: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """Invoke an output binding"""
        url = f"{self.base_url}/bindings/{binding_name}"

        request_data = {
            "operation": operation,
            "data": data
        }

        if metadata:
            request_data["metadata"] = metadata

        response = await self.client.post(url, json=request_data)
        response.raise_for_status()

        return response.json()

    # Secrets
    async def get_secret(
        self,
        secret_store_name: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Get secret from Dapr secret store"""
        url = f"{self.base_url}/secrets/{secret_store_name}/{key}"

        params = {}
        if metadata:
            params["metadata"] = json.dumps(metadata)

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        return response.json()[key]

    # Configuration
    async def get_configuration(
        self,
        configuration_store_name: str,
        keys: List[str],
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get configuration from Dapr configuration store"""
        url = f"{self.base_url}/configuration/{configuration_store_name}"

        request_data = {"keys": keys}
        if metadata:
            request_data["metadata"] = metadata

        response = await self.client.post(url, json=request_data)
        response.raise_for_status()

        return response.json()

    # Distributed Lock
    async def acquire_lock(
        self,
        lock_store_name: str,
        resource_id: str,
        lock_owner: str,
        expiry_in_seconds: int = 60
    ) -> bool:
        """Acquire distributed lock"""
        url = f"{self.base_url}/locks/{lock_store_name}/{resource_id}"

        request_data = {
            "lockOwner": lock_owner,
            "expiryInSeconds": expiry_in_seconds
        }

        response = await self.client.post(url, json=request_data)
        response.raise_for_status()

        return response.json().get("success", False)

    async def release_lock(
        self,
        lock_store_name: str,
        resource_id: str,
        lock_owner: str
    ) -> bool:
        """Release distributed lock"""
        url = f"{self.base_url}/locks/{lock_store_name}/{resource_id}/{lock_owner}"

        response = await self.client.delete(url)
        response.raise_for_status()

        return response.json().get("success", False)

    # Health Checks
    async def health_check(self) -> bool:
        """Check Dapr sidecar health"""
        try:
            url = f"{self.base_url}/healthz"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Dapr health check failed: {e}")
            return False

class DaprWorkflow:
    """Dapr Workflow API client"""

    def __init__(self, dapr_client: DaprClient):
        self.dapr_client = dapr_client

    async def start_workflow(
        self,
        workflow_name: str,
        input_data: Any = None,
        instance_id: Optional[str] = None
    ) -> str:
        """Start a workflow instance"""
        url = f"{self.dapr_client.base_url}/workflows/{workflow_name}/start"

        request_data = {}
        if input_data:
            request_data["input"] = input_data
        if instance_id:
            request_data["workflowInstanceId"] = instance_id

        response = await self.dapr_client.client.post(url, json=request_data)
        response.raise_for_status()

        return response.json().get("instanceId")

    async def get_workflow_state(
        self,
        instance_id: str
    ) -> Dict[str, Any]:
        """Get workflow state"""
        url = f"{self.dapr_client.base_url}/workflows/{instance_id}"

        response = await self.dapr_client.client.get(url)
        response.raise_for_status()

        return response.json()

    async def raise_workflow_event(
        self,
        instance_id: str,
        event_name: str,
        event_data: Any
    ) -> None:
        """Raise an event for a workflow"""
        url = f"{self.dapr_client.base_url}/workflows/{instance_id}/raiseEvent/{event_name}"

        response = await self.dapr_client.client.post(
            url,
            content=json.dumps(event_data)
        )
        response.raise_for_status()

    async def terminate_workflow(
        self,
        instance_id: str
    ) -> None:
        """Terminate a workflow instance"""
        url = f"{self.dapr_client.base_url}/workflows/{instance_id}/terminate"

        response = await self.dapr_client.client.post(url)
        response.raise_for_status()

# Dapr Event Store Integration
class DaprEventStore(EventStore):
    """Dapr-based event store implementation"""

    def __init__(self, dapr_client: DaprClient, state_store_name: str = "eventstore"):
        self.dapr_client = dapr_client
        self.state_store_name = state_store_name

    async def save_event(self, event: BaseEvent, stream_id: str) -> None:
        """Save event using Dapr state store"""
        # Get stream events
        stream_key = f"stream:{stream_id}"
        events = await self.dapr_client.get_state(
            self.state_store_name,
            stream_key
        ) or []

        # Add new event
        events.append(event.to_dict())

        # Save back to state store
        await self.dapr_client.save_state(
            self.state_store_name,
            stream_key,
            events
        )

        # Also save by event ID for direct lookup
        event_key = f"event:{event.event_id}"
        await self.dapr_client.save_state(
            self.state_store_name,
            event_key,
            event.to_dict()
        )

        # Update type index
        type_index_key = f"type:{event.event_type}"
        type_events = await self.dapr_client.get_state(
            self.state_store_name,
            type_index_key
        ) or []
        type_events.append(event.event_id)

        await self.dapr_client.save_state(
            self.state_store_name,
            type_index_key,
            type_events
        )

    async def get_events(
        self,
        stream_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[BaseEvent]:
        """Get events from Dapr state store"""
        stream_key = f"stream:{stream_id}"
        events_data = await self.dapr_client.get_state(
            self.state_store_name,
            stream_key
        ) or []

        # Apply filters
        if from_version is not None:
            events_data = events_data[from_version:]
        if to_version is not None:
            events_data = events_data[:to_version]
        if limit is not None:
            events_data = events_data[:limit]

        for event_data in events_data:
            yield BaseEvent.from_dict(event_data)
```

## 5. Deployment Patterns

### Kubernetes with Dapr

```yaml
# deployments/kubernetes/dapr-config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: app-config
  namespace: production
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metrics:
    enabled: true
    rules: |
      - name: dapr-system
        description: "Dapr system metrics"
        default: true
      - name: app
        description: "Application metrics"
        default: true
  features:
    - name: AppHealthCheck
      enabled: true
  api:
    allowed:
      - name: state
      - name: invoke
      - name: publish
      - name: bindings
      - name: secrets
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-broker:9092"
  - name: authRequired
    value: "false"
  - name: consumerID
    value: "app-pubsub"
  - name: compressionType
    value: "snappy"
  - name: batch_size
    value: "100"
  - name: batch_timeout
    value: "10ms"
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: production
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connection-string
  - name: tableName
    value: "app_state"
  - name: metadataTableName
    value: "app_state_metadata"
  - name: keyPrefix
    value: "none"
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: production
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: namespace
    value: "production"
```

```yaml
# deployments/kubernetes/app-with-dapr.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-service
  namespace: production
  labels:
    app: event-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: event-service
  template:
    metadata:
      labels:
        app: event-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "event-service"
        dapr.io/app-port: "8000"
        dapr.io/enable-metrics: "true"
        dapr.io/enable-profiling: "true"
        dapr.io/config: "app-config"
        dapr.io/log-as-json: "true"
        dapr.io/log-level: "info"
        dapr.io/app-protocol: "http"
    spec:
      containers:
      - name: app
        image: myregistry/event-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
        - name: APP_PORT
          value: "8000"
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: app-config
---
apiVersion: v1
kind: Service
metadata:
  name: event-service
  namespace: production
spec:
  selector:
    app: event-service
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
```

This event-driven architecture skill provides comprehensive patterns for building modern, distributed systems using event sourcing, CQRS, saga patterns, and Dapr integration. It's designed to be framework-agnostic and applicable to any domain requiring robust event-driven capabilities.

`★ Insight ─────────────────────────────────────`
The event-driven architecture patterns shown here emphasize several key 2025 best practices:
1. **Schema Evolution**: Events include versioning and support for backward/forward compatibility
2. **Broker Abstraction**: Generic interfaces allow swapping Kafka, Redis, or cloud brokers without code changes
3. **Recovery Patterns**: Sagas with compensation and retry policies ensure system resilience
4. **Observability**: Built-in tracing, metrics, and structured logging for production monitoring
5. **Multi-tenancy**: Native support for tenant isolation at the event level

These patterns ensure your event-driven system can evolve, scale, and maintain reliability as requirements change.
`─────────────────────────────────────────────────`