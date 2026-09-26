# Runtime.evaluate

- `Runtime.evaluate` - Evaluates expression on global object
- Input:
  - `expression` (string): Required. Expression to evaluate.
  - `silent` (boolean, optional): Optional. In silent mode exceptions thrown during evaluation are not reported and do not pause execution.
  - `contextId` (integer, optional): Optional. Specifies in which execution context to perform evaluation. If the parameter is omitted the evaluation will be performed in the context of the inspected page.
  - `throwOnSideEffect` (boolean, optional): Optional. Whether to throw an exception if side effect cannot be ruled out during evaluation (commonly used for side-effect-free evaluation in debugger preview/hover).
  - `generatePreview` (boolean, optional): Optional. Whether preview should be generated for the result.
  - `objectGroup` (string, optional): Optional. Symbolic group name that can be used to release multiple objects.

  > Note: If Lynx runs on the V8 or JSC engine, it is taken over by the native Inspector of these engines. In addition to the above common parameters, they natively support the complete set of standard CDP parameters (e.g., returnByValue, awaitPromise, includeCommandLineAPI, etc.).
- Output: `{result: RemoteObject, exceptionDetails?: ExceptionDetails}`
- Description: Evaluates a JavaScript expression and returns the result
