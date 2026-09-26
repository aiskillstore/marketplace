# Main-Thread Logs and Object Properties

Use `get-console --thread main` to capture main-thread console output, then inspect any logged runtime object with `Runtime.getProperties` on the same thread.

## 1. Capture main-thread logs

```bash
agent-lynx get-console --thread main
```

Example output:

```text
- [log/main-thread]: <Object (objectId:13561514624)>
```

## 2. Inspect the logged object

```bash
agent-lynx cdp --thread main -m Runtime.getProperties '{"objectId":"13561514624","ownProperties":true}'
```

This returns the object's enumerable properties from the main-thread VM.
