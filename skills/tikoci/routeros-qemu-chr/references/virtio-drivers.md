# VirtIO Driver Matrix — RouterOS CHR Kernel

RouterOS CHR kernel (Linux 5.6.3) has specific VirtIO driver support. This matrix is derived from GPL kernel configs (v7.2) and binary string analysis (v7.23beta2).

## Bus/Transport Drivers

| Driver | x86_64 | aarch64 | Notes |
|---|---|---|---|
| `virtio_pci` | Yes | Yes | Standard PCI transport — always use this |
| `virtio_mmio` | No | No | Would need `if=virtio` on `virt` — not viable |

**This is why `if=virtio` fails on aarch64:** QEMU's `virt` machine resolves it to MMIO, but the kernel has no MMIO transport driver.

## VirtIO Device Drivers

| Driver | x86_64 | aarch64 | QEMU device | Used by CHR |
|---|---|---|---|---|
| `virtio_blk` | Yes | Yes | `virtio-blk-pci` | Primary disk |
| `virtio_net` | Yes | Yes | `virtio-net-pci` | Networking |
| `virtio_scsi` | Yes | Yes | `virtio-scsi-pci` | Not typically used |
| `virtio_console` | Yes | Yes | `virtio-serial-pci` | Serial/console |
| `virtio_balloon` | Yes | Yes | `virtio-balloon-pci` | Memory ballooning |
| `virtio_gpu` | Yes | Yes | `virtio-gpu-pci` | Not typically used |
| `9pnet_virtio` | **Yes** | **No** | `virtio-9p-pci` | x86 only — see note |
| `virtiofs` | No | No | `vhost-user-fs-pci` | Not in 5.6.3 kernel |

## 9p Filesystem (x86_64 only)

The x86_64 kernel has `CONFIG_9P_FS=y` + `CONFIG_NET_9P_VIRTIO=y`. QEMU accepts the device and the kernel binds the driver. **However**, RouterOS does not expose Linux `mount` commands, so the 9p filesystem cannot be mounted through RouterOS CLI. The kernel driver works at the PCI level but there is no userland interface.

## Other Notable Drivers

| Driver | x86_64 | aarch64 | Notes |
|---|---|---|---|
| `BLK_DEV_NVME` | Yes (=y) | Yes (=m) | NVMe block — used by Apple VZ backend |
| `E1000` / `E1000E` | Yes (=m) | No | Intel NIC emulation (alternative to virtio) |
| `ATA_PIIX` | Yes | No | IDE/SATA — not needed with virtio |
| `KVM_GUEST` | Yes | N/A | KVM paravirt optimizations |
| `HYPERV` | Yes | N/A | Hyper-V guest support |
| `XEN` | Yes | N/A | Xen PV/HVM guest support |
| `NFS_FS` / `NFSD` | Yes (=m) | Yes (=m) | NFS client + server |

## Architecture Divergence

The x86_64 kernel was designed for hypervisor use (Xen, Hyper-V, KVM support all present). The aarch64 kernel targeted Marvell hardware originally and gained VirtIO device drivers after v7.2. The key practical difference: x86_64 has 9p and many legacy NIC drivers; aarch64 has only VirtIO and NVMe for block/network.

## Alternatives for Host-Guest File Sharing

Since 9p is x86-only and not mountable via RouterOS CLI:

- **/tool/fetch**: RouterOS can pull files from an HTTP server on the host
- **REST API file upload**: `PUT /rest/file` for small text files, **no binaries**
- **SCP**: `scp -P <ssh-port> file.npk admin@127.0.0.1:/`
- **SFTP**: Works via RouterOS SSH
- **FTP**: RouterOS has built-in FTP server
