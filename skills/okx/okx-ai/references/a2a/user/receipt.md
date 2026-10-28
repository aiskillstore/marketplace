# Subscription Device Delivery

## Module Description

Manage which logged-in devices receive messages for each subscription task.


## Flow
### View devices and delivery

1. List the user's logged-in devices:

   ```bash
   onchainos agent device-list
   ```

   Render each returned `deviceId`, device name, last-online time, and current-device marker.

2. Read the selected subscription from the current subscription list:

   ```bash
   onchainos agent subscribe-detail <jobId> --format json
   ```

3. Render its delivery mode and current-device result:

   | `deviceList` | Delivery mode |
   |---|---|
   | `null` | All logged-in devices receive messages. |
   | `[]` | No device receives messages. |
   | Non-empty array | Only the listed devices receive messages. |

   Render `thisDeviceReceives` as the current device's Yes/No status. Do not
   infer device names for IDs that are absent from the fresh device list.

### Set receiving devices

Use this flow when the user asks to enable or disable a device for one task,
receive on all devices, receive only on selected devices, or stop delivery to
all devices.

1. Require a selected `jobId` from the current subscription list and reread
   `subscribe-detail --format json` immediately before the change.
2. Read `device-list`; accept only its fresh `deviceId` values as targets.
3. Build the complete desired list:

   | User choice | Write value |
   |---|---|
   | All currently logged-in devices | Fresh complete `deviceId` list; preserve `deviceList: null` and do not write if it is already `null`. |
   | Selected devices | The complete selected `deviceId` list. |
   | Enable one device | Fresh explicit list union that `deviceId`; `null` is already enabled. |
   | Disable one device | Fresh explicit list minus that `deviceId`; for `null`, first ask for the complete replacement allowlist. |
   | No devices | Empty list. |

4. Before writing, show the affected task and the complete resulting receiver
   list. Require explicit confirmation when the operation removes a device or
   leaves no receiving device.
5. Write the complete list:

   ```bash
   onchainos agent subscribe-device-update \
     --job-id <jobId> --device-list <complete-device-ids>
   ```

   To apply different receiving-device lists to multiple selected subscription
   tasks in one operation, use the batch form:

   ```bash
   onchainos agent subscribe-device-update \
     --items '[{"jobId":"<jobId>","deviceList":["<deviceId>"]}]'
   ```

6. Reread `subscribe-detail --format json` and report the resulting delivery
   mode and `thisDeviceReceives` status.

### Constraints

- `subscribe-device-update` replaces the entire stored list. Never write a
  partial list from conversation memory; always fresh-read, merge or subtract,
  write, then reread.
- Treat `deviceList: null` as default-all, not an empty editable list. The
  current write API accepts only an explicit device array: to exclude one device
  or replace default-all, the user must choose the resulting device set
  explicitly.
- Do not update a task that is not selected from the current subscription list.
- Device delivery is configured independently for each task. Changing one task
  must not alter delivery for another task or device.
- A single batch submission accepts 1–100 selected tasks. Split a larger
  selection into separate, independently confirmed submissions.
