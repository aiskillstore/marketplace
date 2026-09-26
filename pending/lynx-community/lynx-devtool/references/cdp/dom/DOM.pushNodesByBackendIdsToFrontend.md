# DOM.pushNodesByBackendIdsToFrontend

- `DOM.pushNodesByBackendIdsToFrontend` - Map backend node IDs to frontend node IDs
- Input: `{backendNodeIds: Array<BackendNodeId>}`
- Output: `{nodeIds: Array<NodeId>}`
- Description: Returns node IDs for a batch of backend node IDs.

## LynxView behavior

- The current handler copies `backendNodeIds` into `nodeIds` without resolving the IDs against the element tree.
- Consequently, a returned value does not prove that the corresponding node exists or has been registered with the DevTools frontend.
- This method does not modify the inspected page or runtime state.
