# CHR Licensing

## License Tiers

| Level | Speed Limit | Cost | Notes |
|-------|-------------|------|-------|
| Free | 1 Mbps | $0 | No registration needed. Unlimited use. Sufficient for API work, testing, sniffer debugging |
| P1 | 1 Gbps | paid | Perpetual |
| P10 | 10 Gbps | paid | Perpetual |
| P-Unlimited | Unlimited | paid | Perpetual |
| 60-day trial | P-Unlimited speeds | $0 | Requires free mikrotik.com account. See below |

## Free License (Default)

Every CHR instance starts with a free license. No registration, no activation — just boot and use.

**The 1 Mbps limit** applies to interface throughput, not API/management traffic. This means:
- REST API calls, SSH, WinBox, WebFig — unaffected by the speed limit
- Packet sniffer TZSP streaming — works fine for debugging (TZSP packets are small)
- Actual data forwarding between interfaces — capped at 1 Mbps
- If users report "slow" traffic through a CHR, the free license limit is the most likely cause

**1 Mbps is sufficient for:**
- Development and API testing
- Protocol debugging with `/tool/sniffer` or mangle `sniff-tzsp`
- CI/CD integration tests
- Learning RouterOS configuration
- Container (`/container`) development (image pull may be slow)

## 60-Day Trial License

A free 60-day trial provides **P-Unlimited speeds** (no throughput cap).

### How to Obtain

1. Create a free account at [mikrotik.com](https://www.mikrotik.com) (Account → Register)
2. In the CHR, run: `/system/license/renew account=<email> password=<password> level=p-unlimited`
3. Or via WebFig: System → License → Renew
4. The trial activates immediately — no reboot needed

### Trial Expiry Behavior

After 60 days:
- The CHR **continues to work** — it does NOT stop or become unusable
- Speed reverts to the free 1 Mbps limit
- The license shows as expired but the VM keeps running
- **The CHR cannot be upgraded** to a newer RouterOS version while the trial is expired
- Since CHR is a VM, you can simply delete and recreate it with a fresh trial if needed

### When to Use Trial vs Free

| Scenario | License |
|----------|---------|
| API development / testing | Free (1 Mbps is fine) |
| Sniffer / TZSP debugging | Free (packet mirroring is low bandwidth) |
| Throughput testing | Trial (need real speeds) |
| QoS / queue testing | Trial (need measurable bandwidth) |
| Container image pulls | Trial (faster downloads) |
| CI pipelines | Free (API tests don't need throughput) |
| Demo / training | Free or Trial depending on scenario |

## Checking Current License

```routeros
/system/license/print
```

Via REST API:
```sh
curl -u admin: http://<router-ip>/rest/system/license
```

## Licensing and VMs

Each CHR VM instance needs its own license. Paid licenses are tied to the VM's system-id (generated on first boot from the virtual disk). Cloning a VM disk duplicates the system-id — MikroTik's license server will detect this.

For testing purposes, the free license avoids all these concerns — just create and destroy VMs freely.
