# Reliability and recovery

Determine observable completion for each important operation and who owns unfinished work. Give network calls a deadline from the caller's available budget. Retry failures that can improve, with bounded attempts and jitter, at one appropriate layer.

Make repeated effects safe. Keep long calls outside storage locks where feasible. Record ambiguous outcomes and reconcile them with the authoritative system. For queues, acknowledge after the durable effect or use an explicit idempotent processing strategy. Handle shutdown and recovery around the commit boundary.

Test slow dependencies, a lost response, cleanup after interruption, and replay where real paths can encounter them.
