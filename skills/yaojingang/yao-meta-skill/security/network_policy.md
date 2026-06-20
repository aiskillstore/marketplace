# Network Policy

Network-capable scripts are allowed only when their outbound boundary is explicit and reviewable.

Current policy:

- `scripts/check_update.py` may read version metadata from `raw.githubusercontent.com/yaojingang/yao-meta-skill/` over HTTPS.
- `scripts/github_benchmark_scan.py` may call the GitHub REST API at `api.github.com` over HTTPS.
- Custom update URLs are denied by default and require explicit operator opt-in plus reviewer awareness.
- New network-capable scripts must be added to `security/network_policy.json` before a governed or team-distributed release.

The trust checker compares HTTPS URL literals in scripts with `security/network_policy.json`. Missing or mismatched host declarations are reported as warnings.
