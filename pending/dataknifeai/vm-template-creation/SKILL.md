---
name: vm-template-creation
description: Create, configure, and manage VM templates in Proxmox. Build reusable VM images for rapid deployment of standardized environments, including Kubernetes clusters and managed applications.
---

# VM Template Creation Skill

Create, manage, and deploy VM templates in your Proxmox environment for rapid, standardized infrastructure provisioning.

## What this skill does

This skill enables you to:
- Prepare virtual machines from cloud images or custom configurations
- Convert configured VMs into templates for reuse
- Clone templates to create multiple instances
- Manage template configurations and updates
- Deploy standardized environments rapidly
- Maintain template consistency across deployments
- Create specialized templates for different workloads
- Update and version templates
- Manage template lifecycle

## When to use this skill

Use this skill when you need to:
- Create template VMs for rapid deployment
- Prepare Ubuntu Cloud-Init compatible templates
- Deploy multiple identical VMs for Kubernetes clusters
- Build standardized application environments
- Automate VM provisioning workflows
- Maintain consistent infrastructure-as-code
- Support Infrastructure-as-Code (IaC) automation
- Create reusable templates for different projects
- Build CI/CD infrastructure templates

## Available Tools

### Core VM Management
- `create_vm_advanced` - Create a VM with advanced configuration (disk, network, CD/DVD)
- `update_vm_config` - Update VM configuration and mark as template
- `get_vm_config` - Get full VM configuration details
- `clone_vm` - Clone a template VM to create instances
- `delete_vm` - Remove a VM or template

### Supporting Tools
- `get_vm_status` - Get VM status and resource usage
- `get_vms` - List all VMs on a node
- `start_vm` - Start a VM (for testing/configuration)
- `stop_vm` - Stop a running VM
- `shutdown_vm` - Gracefully shut down a VM

## Template VM Creation Workflow

### Step 1: Prepare Base VM

Create a new VM with desired base configuration:

```bash
create_vm_advanced(
  node_name="pve2",
  vmid=100,
  name="ubuntu-22.04-template",
  memory=2048,
  cores=2,
  sockets=1,
  ide2="local:iso/jammy-server-cloudimg-amd64.iso",
  sata0="local-lvm:50",  # 50GB disk
  net0="virtio,bridge=vmbr0"
)
```

### Step 2: Install and Configure OS

1. Boot the VM with the Cloud-Init image
2. Configure hostname, network, and storage
3. Install required packages and applications
4. Apply security patches and hardening
5. Configure Cloud-Init for automation
6. Test all functionality thoroughly

### Step 3: Mark as Template

Once configuration is complete and tested:

```bash
update_vm_config(
  node_name="pve2",
  vmid=100,
  config={
    "template": 1
  }
)
```

**Important**: Once a VM is marked as template, it cannot be started directly. It can only be cloned.

### Step 4: Clone from Template

Create instances from the template:

```bash
clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=101,
  new_name="web-server-01",
  full=true
)
```

## Real-World Example: Rancher Kubernetes Template

### Create Ubuntu Template for RKE2

```bash
# 1. Create base VM
create_vm_advanced(
  node_name="pve2",
  vmid=100,
  name="ubuntu-rke2-template",
  memory=4096,     # 4GB for control plane
  cores=4,
  sockets=1,
  ide2="local:iso/jammy-server-cloudimg-amd64.iso",
  sata0="local-lvm:100",  # 100GB for system + RKE2
  net0="virtio,bridge=vmbr0"
)

# 2. Boot, configure, and install:
#    - OS configuration
#    - Cloud-Init setup
#    - RKE2 dependencies (curl, wget, etc.)
#    - System optimization

# 3. Mark as template
update_vm_config(
  node_name="pve2",
  vmid=100,
  config={"template": 1}
)

# 4. Clone for Rancher Manager cluster
clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=101,
  new_name="rancher-manager-1",
  full=true
)

clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=102,
  new_name="rancher-manager-2",
  full=true
)

clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=103,
  new_name="rancher-manager-3",
  full=true
)

# 5. Clone for NPRD-Apps cluster
clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=201,
  new_name="nprd-apps-1",
  full=true
)

clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=202,
  new_name="nprd-apps-2",
  full=true
)

clone_vm(
  node_name="pve2",
  source_vmid=100,
  new_vmid=203,
  new_name="nprd-apps-3",
  full=true
)
```

## Template Configuration Options

### Common Configuration Parameters

When creating or updating templates, you can set:

- `template=1` - Mark VM as template (prevents direct boot)
- `cores=N` - Number of CPU cores
- `sockets=N` - Number of CPU sockets
- `memory=NNNN` - Memory in MB
- `sata0="storage:size"` - Primary disk
- `net0="virtio,bridge=vmbr0"` - Network configuration
- `ide2="storage:iso/image.iso"` - CD/DVD drive for installation

### Cloud-Init Configuration

For Cloud-Init enabled templates:

- Set `cicustom` parameter for custom Cloud-Init configs
- Pre-stage user data for automatic configuration
- Use network metadata for DHCP or static IPs
- Enable serial console for debugging

## Typical Workflows

### Workflow: Create Standard Linux Template

1. Create VM with base configuration
2. Boot from Cloud-Init ISO
3. Configure hostname, network, and disk
4. Install base packages: `curl wget vim git`
5. Apply security hardening
6. Shutdown VM gracefully
7. Mark as template with `update_vm_config`
8. Clone as needed for deployments

### Workflow: Update Existing Template

1. Clone template to temporary VM
2. Apply updates, patches, security fixes
3. Test thoroughly
4. Stop the test VM
5. Create new template from test VM
6. Delete old template and test VM
7. Update documentation with version

### Workflow: Kubernetes Cluster Deployment

1. Create and test RKE2 template (steps above)
2. Clone template 3 times for control plane nodes
3. Clone template 3 times for worker nodes
4. Boot cloned VMs
5. Configure networking (hostname, IPs via Cloud-Init)
6. Initialize RKE2 on control plane
7. Join worker nodes to cluster
8. Verify cluster health

## Best Practices

### Template Design
- Keep templates minimal (smaller disk = faster cloning)
- Pre-install common tools and dependencies
- Use Cloud-Init for network and host configuration
- Document template versions and purposes
- Include installation dates and applied patches

### Security
- Keep templates patched and updated
- Remove sensitive data before templating
- Use strong default passwords during setup
- Enable SSH key-based authentication
- Disable unnecessary services
- Apply OS-level hardening

### Performance
- Use virtio drivers for disks and network (better performance)
- Set appropriate memory/CPU for cloned VMs
- Use thin provisioning where possible
- Monitor template update frequency

### Organization
- Use clear naming conventions: `distro-version-purpose`
- Document template contents and purpose
- Version templates systematically
- Maintain changelog for updates
- Remove old unused templates
- Tag templates with creation date

### Testing
- Always test templates before deployment
- Boot cloned VMs to verify functionality
- Test network configuration with Cloud-Init
- Verify all installed packages work correctly
- Test scaling (clone multiple instances)
- Validate performance meets requirements

## Example Questions

- "Create a template VM for Ubuntu 22.04 with RKE2"
- "Mark VM 100 as a template for reuse"
- "Clone template VM 100 to create 3 Kubernetes nodes"
- "What's the configuration of the Ubuntu template?"
- "Update the template to add Docker support"
- "Clone the template with custom hostname and IP"
- "Create a template for database servers"
- "Build a template for CI/CD runners"

## Response Format

When using this skill, I provide:
- Clear step-by-step template creation instructions
- VM configuration commands ready to execute
- Cloning examples for your use case
- Configuration validation results
- Template status and details
- Recommendations for optimization
- Best practices guidance

## Integration with Terraform

The MCP tools complement Terraform's `telmate/proxmox` provider:

- Use MCP to prepare and test templates interactively
- Use Terraform to clone templates at scale for production
- Use MCP to update template configurations
- Use MCP for troubleshooting template issues
- Combine for complete IaC automation

## Limitations

- Templates cannot be booted directly (must be cloned)
- Large templates take longer to clone
- Network configuration happens post-clone via Cloud-Init
- Some fine-tuning may be needed per clone
- Disk image import requires manual steps (see Proxmox documentation)

## Related Skills

- **Virtual Machine Management** - General VM lifecycle operations
- **Cluster Management** - Monitor Proxmox cluster health
- **Disaster Recovery** - Backup and restore templates
- **Infrastructure as Code** - Deploy with Terraform automation
