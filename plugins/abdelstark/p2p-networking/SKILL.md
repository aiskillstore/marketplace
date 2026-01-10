---
name: p2p-networking
description: Peer-to-peer networking patterns using commonware for building decentralized Guts network
---

# P2P Networking Skill for Guts

You are implementing peer-to-peer networking for a decentralized code collaboration platform.

## Commonware P2P Overview

The `commonware-p2p` crate provides authenticated, encrypted peer communication.

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Guts P2P Network                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ Node A  │────│ Node B  │────│ Node C  │              │
│   └────┬────┘     └────┬────┘     └────┬────┘              │
│        │               │               │                    │
│        └───────────────┼───────────────┘                    │
│                        │                                    │
│                   ┌────┴────┐                               │
│                   │ Node D  │                               │
│                   └─────────┘                               │
│                                                             │
│   Protocol: Noise_XX + Ed25519                              │
│   Transport: QUIC / TCP                                     │
│   Discovery: DHT + Bootstrap nodes                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Message Types

```rust
use serde::{Deserialize, Serialize};
use commonware_codec::Codec;

#[derive(Debug, Clone, Serialize, Deserialize, Codec)]
pub enum Message {
    // Handshake
    Hello { version: u32, capabilities: Vec<Capability> },
    HelloAck { version: u32, capabilities: Vec<Capability> },

    // Repository sync
    GetRefs { repository: RepositoryId },
    Refs { repository: RepositoryId, refs: Vec<Ref> },

    GetObjects { repository: RepositoryId, objects: Vec<ObjectId> },
    Objects { repository: RepositoryId, objects: Vec<Object> },

    // Announcements
    NewCommit { repository: RepositoryId, commit: CommitId },
    NewRepository { repository: RepositoryInfo },

    // Gossip
    Gossip { topic: Topic, data: Vec<u8> },

    // Keep-alive
    Ping { nonce: u64 },
    Pong { nonce: u64 },
}
```

## Peer Management

```rust
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct PeerManager {
    peers: Arc<RwLock<HashMap<PeerId, PeerState>>>,
    config: PeerConfig,
}

#[derive(Debug)]
pub struct PeerState {
    pub id: PeerId,
    pub address: SocketAddr,
    pub connection: Connection,
    pub last_seen: Instant,
    pub repositories: HashSet<RepositoryId>,
    pub capabilities: Vec<Capability>,
}

impl PeerManager {
    pub async fn connect(&self, addr: SocketAddr) -> Result<PeerId> {
        // Establish encrypted connection
        let connection = Connection::connect(addr, &self.config.keypair).await?;

        // Exchange hello messages
        let peer_info = self.handshake(&connection).await?;

        // Store peer state
        let peer_id = peer_info.id.clone();
        self.peers.write().await.insert(peer_id.clone(), PeerState {
            id: peer_id.clone(),
            address: addr,
            connection,
            last_seen: Instant::now(),
            repositories: HashSet::new(),
            capabilities: peer_info.capabilities,
        });

        Ok(peer_id)
    }

    pub async fn broadcast(&self, message: Message) -> Result<()> {
        let peers = self.peers.read().await;

        let futures: Vec<_> = peers.values()
            .map(|peer| peer.connection.send(message.clone()))
            .collect();

        futures::future::try_join_all(futures).await?;
        Ok(())
    }
}
```

## Gossip Protocol

```rust
use std::collections::HashSet;

pub struct GossipProtocol {
    seen_messages: HashSet<MessageId>,
    fanout: usize,
    peer_manager: Arc<PeerManager>,
}

impl GossipProtocol {
    pub async fn broadcast(&mut self, topic: Topic, data: Vec<u8>) -> Result<()> {
        let message_id = MessageId::from_content(&topic, &data);

        // Don't rebroadcast
        if !self.seen_messages.insert(message_id.clone()) {
            return Ok(());
        }

        // Select random peers
        let peers = self.peer_manager.random_peers(self.fanout).await;

        // Send to selected peers
        for peer in peers {
            peer.send(Message::Gossip {
                topic: topic.clone(),
                data: data.clone(),
            }).await?;
        }

        Ok(())
    }

    pub async fn handle_gossip(&mut self, peer: PeerId, message: Message) -> Result<()> {
        if let Message::Gossip { topic, data } = message {
            let message_id = MessageId::from_content(&topic, &data);

            // New message, process and rebroadcast
            if self.seen_messages.insert(message_id) {
                self.process_message(topic.clone(), data.clone()).await?;
                self.broadcast(topic, data).await?;
            }
        }
        Ok(())
    }
}
```

## Repository Synchronization

```rust
pub struct RepoSync {
    peer_manager: Arc<PeerManager>,
    storage: Arc<Storage>,
}

impl RepoSync {
    pub async fn sync_repository(&self, repo_id: RepositoryId) -> Result<()> {
        // Find peers that have this repository
        let peers = self.peer_manager
            .peers_with_repository(&repo_id)
            .await;

        if peers.is_empty() {
            return Err(SyncError::NoPeers);
        }

        // Get refs from peers
        let local_refs = self.storage.get_refs(&repo_id).await?;

        for peer in peers {
            let remote_refs = self.fetch_refs(&peer, &repo_id).await?;

            // Find missing objects
            let missing = self.diff_refs(&local_refs, &remote_refs);

            if !missing.is_empty() {
                // Fetch missing objects
                let objects = self.fetch_objects(&peer, &repo_id, missing).await?;

                // Store objects
                for object in objects {
                    self.storage.put_object(&repo_id, object).await?;
                }
            }
        }

        Ok(())
    }
}
```

## Connection Configuration

```rust
pub struct NetworkConfig {
    /// Listen address for incoming connections
    pub listen_addr: SocketAddr,

    /// Bootstrap nodes for initial peer discovery
    pub bootstrap_nodes: Vec<SocketAddr>,

    /// Maximum number of concurrent connections
    pub max_connections: usize,

    /// Connection timeout
    pub connection_timeout: Duration,

    /// Keep-alive interval
    pub keepalive_interval: Duration,

    /// Node keypair for authentication
    pub keypair: Ed25519Keypair,
}

impl Default for NetworkConfig {
    fn default() -> Self {
        Self {
            listen_addr: "0.0.0.0:9000".parse().unwrap(),
            bootstrap_nodes: vec![],
            max_connections: 50,
            connection_timeout: Duration::from_secs(10),
            keepalive_interval: Duration::from_secs(30),
            keypair: Ed25519Keypair::generate(),
        }
    }
}
```

## Security Considerations

1. **Authentication**: All peers authenticated via Ed25519
2. **Encryption**: All traffic encrypted with Noise protocol
3. **Rate Limiting**: Limit messages per peer to prevent DoS
4. **Peer Scoring**: Track peer behavior, disconnect bad actors
5. **Message Validation**: Verify all messages before processing
