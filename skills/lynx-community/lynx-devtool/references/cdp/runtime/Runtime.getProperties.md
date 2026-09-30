# Runtime.getProperties

- `Runtime.getProperties` - Returns properties of a given object. Object group of the result is inherited from the target object.
- Input:
  - `objectId` (string): Required. Identifier of the target object to query properties for (e.g., a RemoteObject ID returned by evaluate).
  - `ownProperties` (boolean, optional): Optional. If true, returns properties belonging only to the object itself, not its prototype chain. If true, it will also additionally return the engine's internal properties (Internal Property Descriptor).
- Output:
  - `result` (array of PropertyDescriptor): Object properties.
  - `internalProperties` (array of InternalPropertyDescriptor, optional): Internal object properties.
  - `privateProperties` (array of PrivatePropertyDescriptor, optional): Object private properties.
  - `exceptionDetails` (ExceptionDetails, optional): Exception details.
- Description: Retrieves the properties of a specified object. Commonly used in the debugger panel to expand object trees.

## Main-thread usage

If the `objectId` comes from a main-thread console log or evaluation result, query it on the same thread:

```bash
agent-lynx cdp --thread main -m Runtime.getProperties '{"objectId":"13561514624","ownProperties":true}'
```
