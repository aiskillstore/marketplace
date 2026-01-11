---
name: virtual-machine-management
description: Create, manage, and optimize virtual machines in Proxmox. Control VM lifecycle, monitor performance, adjust resources, and plan VM deployment strategies.
---

# Virtual Machine Management Skill

Create, manage, and optimize virtual machines in your Proxmox environment.

## What this skill does

This skill enables you to:
- List virtual machines on specific nodes
- Get detailed VM configuration and status
- Start, stop, reboot, suspend, and resume virtual machines
- Create new virtual machines with basic or advanced configuration
- Clone existing virtual machines
- Delete virtual machines
- Modify VM resource allocation
- Monitor VM performance metrics
- Manage VM snapshots
- Plan VM deployment strategies
- Optimize resource allocation

## When to use this skill

Use this skill when you need to:
- Check VM status and configuration
- Manage VM lifecycle (start/stop/reboot)
- Monitor VM performance and resource usage
- Adjust VM resources (CPU, memory, storage)
- Create new virtual machines
- Troubleshoot VM issues
- Plan VM migrations
- Optimize VM placement

## Available Tools

- `get_vms` - List all VMs on a specific node
- `get_vm_status` - Get detailed VM status and configuration
- `get_vm_config` - Get full VM configuration details
- `start_vm` - Start a virtual machine
- `stop_vm` - Stop a VM immediately
- `shutdown_vm` - Gracefully shutdown a VM
- `reboot_vm` - Reboot a virtual machine
- `suspend_vm` - Suspend (pause) a running VM
- `resume_vm` - Resume a suspended VM
- `create_vm` - Create a new virtual machine with basic configuration
- `create_vm_advanced` - Create a VM with advanced configuration options
- `clone_vm` - Clone an existing virtual machine
- `update_vm_config` - Update VM configuration (resources, options, mark as template)
- `delete_vm` - Delete a virtual machine

## Template VM Creation

Creating template VMs allows you to quickly deploy preconfigured virtual machines:

### Workflow: Create a Template VM

1. **Create or prepare a base VM**
   - Use `create_vm_advanced` or clone from an existing VM
   - Install and configure the OS and applications
   - Test thoroughly before templating

2. **Update VM as Template**
   - Use `update_vm_config` with `template: 1` to mark as template
   ```json
   {
     "template": 1
   }
   ```

3. **Clone from Template**
   - Use `clone_vm` to create instances from the template
   - Template VMs cannot be directly used as running instances
   - Each clone becomes a full, independent VM

### Example: Mark VM as Template
```bash
# First, prepare your VM (install OS, apps, configure)
# Then mark it as a template:
update_vm_config(node="pve2", vmid=100, config={"template": 1})
```

### Example: Clone from Template
```bash
# Clone the template to create a new VM
clone_vm(node="pve2", source_vmid=100, new_vmid=200, new_name="web-server-01", full=true)
```

## Typical Workflows

### VM Lifecycle Management
1. Use `get_vms` to list available VMs
2. Use `get_vm_status` or `get_vm_config` to check VM state
3. Use start/stop/reboot/suspend/resume to manage VM operations
4. Monitor VM health during changes

### VM Creation & Configuration
1. Use `create_vm` or `create_vm_advanced` to provision new VM
2. Use `get_vm_status` to verify configuration
3. Use `clone_vm` to create copies for testing or deployment
4. Use `get_vm_config` to review detailed settings
5. Document VM details for reference

### VM Lifecycle Operations
1. Use `suspend_vm` to pause a running VM (preserves state)
2. Use `resume_vm` to resume operations from suspended state
3. Use `shutdown_vm` for graceful shutdown
4. Use `reboot_vm` to restart VM
5. Use `stop_vm` for immediate termination if needed

### VM Troubleshooting
1. Use `get_vm_status` to check VM health
2. Use reboot/restart to recover from issues
3. Use snapshots to rollback problematic changes
4. Analyze performance metrics for root cause

## Example Questions

- "List all VMs on the production node"
- "What's the status and resource usage of VM 100?"
- "Get the full configuration of VM 105"
- "Start the web server VM"
- "Create a new VM with 4 cores and 8GB RAM"
- "Clone VM 100 to create a test copy"
- "Mark VM 100 as a template for future deployments"
- "Clone the template VM 100 to create web-server-01"
- "Update VM 105 to use 16GB RAM"
- "Suspend VM 200 for maintenance"
- "Resume VM 200 to continue operations"
- "Gracefully shutdown VM 150"
- "Delete VM 199 and remove all data"

## Response Format

When using this skill, I provide:
- VM listings with status and resource allocation
- Detailed VM configuration and performance metrics
- Status confirmations for VM operations
- Resource utilization analysis
- Optimization recommendations

## Best Practices

- Monitor VM performance regularly
- Use cloning for quick VM deployment
- Create VMs with appropriate resource allocation
- Use suspend/resume for temporary pauses
- Use graceful shutdown to minimize data loss
- Plan resource allocation carefully
- Balance VMs across nodes
- Implement high-availability for critical VMs
- Keep VM templates updated
- Document VM configuration and purpose
- Test changes in non-production first
- Monitor disk usage to prevent full disks
- Clean up unused VMs to conserve resources

