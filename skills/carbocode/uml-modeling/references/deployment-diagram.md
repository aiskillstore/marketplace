# Deployment Diagram Deep Dive

Use a deployment diagram to model runtime nodes, execution environments, deployed artifacts, and communication paths. It answers where software runs.

## Use When

- The user needs client/server/runtime topology.
- Devices, servers, containers, runtimes, or managed data stores matter.
- Artifacts must be mapped to nodes or execution environments.

Avoid when the question is logical component responsibility, package dependency, or class structure.

## Core Modeling Elements

- Node.
- Device.
- Execution environment.
- Artifact.
- Deployment relationship.
- Communication path with optional protocol.

## Expansion Questions

- Which elements are physical devices and which are execution environments?
- Which artifacts are deployed where?
- Is a client application an artifact on a device, an execution environment concern, or both?
- Which protocols or network boundaries matter?
- Are external services runtime nodes or neighboring systems?

## Design Moves

- Separate device from execution environment when it clarifies runtime behavior.
- Attach artifacts to nodes/environments rather than leaving them floating.
- Label communication paths with protocol only if useful.
- Keep logical components separate unless mapping components to artifacts is the point.
- Show trust/network boundaries with notes when they affect deployment decisions.

## Completeness Criteria

- Runtime locations are explicit.
- Deployed artifacts are mapped.
- Execution environments are shown when relevant.
- Communication paths describe runtime connectivity, not design dependency.

## Common Mistakes And Repairs

- No nodes: switch to component/package diagram or add real runtime nodes.
- Services with no deployment location: decide whether they are nodes or logical components.
- Class internals shown: move to class/component diagram.
- Protocol clutter: keep only operationally meaningful labels.
