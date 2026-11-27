# Greenfield planning

Define the first user journey, its observable success, and one failure the system must handle. Determine the clients, existing constraints, data sensitivity, and expected deployment. Ask only about decisions that materially change the product or its operating cost.

Map each feature to a state owner and an invariant. In a small booking project, room availability and reservations may belong to one transactional component. Confirming the last available room must have one winner. Offline operations, money, or notifications add separate decisions and tests when the requested journey requires them.

Choose a stack that the user can run, test, and maintain in the intended environment. Prefer one usable slice with a real entry point and an observable check. For example, a small Node API can start with one reservation operation and SQLite. A Python CLI that transforms local files may need only a pure transform and a file I/O adapter. Use [structure](structure.md) and [architecture](architecture.md) when those choices matter.

Record how to run the slice, where data lives, what can be changed later, and a check for the highest-impact failure. Add packages or operational processes when they address a constraint of the proposed slice.
