# Runtime Methods

Use `agent-lynx evaluate <expression>` to evaluate JavaScript on the background VM with direct access to `lynx` and `nativeLynx`. Pass `--thread main` when you need the main-thread VM; main-thread expressions are sent unchanged without these injected variables.

The other `Runtime.*` methods listed here can be sent with `agent-lynx cdp --thread main ...`. `Runtime.getProperties` can be invoked directly. Some Runtime methods, including `Runtime.getHeapUsage`, and event consumers such as console output require `Runtime.enable`; follow each method page's prerequisites.

- [Runtime.evaluate](Runtime.evaluate.md) - Evaluates expression on global object
- [Runtime.getProperties](Runtime.getProperties.md) - Get properties of a given object
- [Runtime.callFunctionOn](Runtime.callFunctionOn.md) - Calls function with given declaration on the given object
- [Runtime.compileScript](Runtime.compileScript.md) - Compiles expression
- [Runtime.runScript](Runtime.runScript.md) - Runs script with given id in a given context
- [Runtime.globalLexicalScopeNames](Runtime.globalLexicalScopeNames.md) - Returns all let, const and class variables from global scope
- [Runtime.setAsyncCallStackDepth](Runtime.setAsyncCallStackDepth.md) - Enables or disables async call stacks tracking
- [Runtime.getHeapUsage](Runtime.getHeapUsage.md) - Returns the JavaScript engine's heap usage
