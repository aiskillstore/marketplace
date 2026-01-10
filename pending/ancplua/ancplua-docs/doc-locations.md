# ANcpLua Documentation Map

Complete file-by-file documentation reference.

---

## ANcpLua.Roslyn.Utilities
**Path:** `/Users/ancplua/RiderProjects/ANcpLua.Roslyn.Utilities`

### Root
| File | Content |
|------|---------|
| `README.md` | Package overview, quick API reference, highlights |
| `CLAUDE.md` | Build commands, SDK policies, banned packages |

### Structured Docs (`/docs`)
| File | Content |
|------|---------|
| `index.md` | Landing page, package links |
| `toc.yml` | Navigation structure |

### Utilities (`/docs/utilities/`)
| File | Content |
|------|---------|
| `index.md` | Utilities overview, extension method table |
| `diagnostic-flow.md` | Railway-oriented `DiagnosticFlow<T>` API |
| `semantic-guard.md` | Declarative `SemanticGuard<T>` validation |
| `patterns.md` | `SymbolPattern`, `Match.*`, `Invoke.*` DSL |
| `contexts.md` | AwaitableContext, AspNetContext, DisposableContext, CollectionContext |
| `pipeline.md` | IncrementalValuesProvider extensions |
| `symbols.md` | Symbol, Type, Method, Namespace extensions |
| `operations.md` | IOperation traversal, context detection |
| `codegen.md` | IndentedStringBuilder, GeneratedCodeHelpers |

### SDK Reference (`/docs/sdk/`)
| File | Content |
|------|---------|
| `index.md` | SDK overview |
| `variants.md` | SDK variants (Base, Web, Test) |
| `compiler.md` | Compiler settings |
| `analyzers.md` | Auto-injected analyzers |
| `banned-apis.md` | Banned APIs list |
| `testing.md` | Test framework configuration |
| `web.md` | Web project ServiceDefaults |
| `polyfills.md` | Legacy TFM polyfills |
| `build.md` | Build & package settings |

---

## ANcpLua.Analyzers
**Path:** `/Users/ancplua/RiderProjects/ANcpLua.Analyzers`

### Root
| File | Content |
|------|---------|
| `README.md` | Rules table, installation, configuration |
| `CLAUDE.md` | Rules matrix, test commands, patterns |

### Rule Documentation (`/docs/rules/`)
| File | Rule |
|------|------|
| `index.md` | Rules overview table |
| `AL0001.md` | Prohibit reassignment of primary constructor params |
| `AL0002.md` | Don't repeat negated patterns |
| `AL0003.md` | Don't divide by constant zero |
| `AL0004.md` | Use pattern matching for Span constants |
| `AL0005.md` | Use SequenceEqual for Span comparison |
| `AL0006.md` | Field conflicts with primary constructor |
| `AL0007.md` | GetSchema should be explicit |
| `AL0008.md` | GetSchema must return null |
| `AL0009.md` | Don't call GetSchema |
| `AL0010.md` | Type should be partial |
| `AL0011.md` | Avoid lock on non-Lock types |
| `AL0012.md` | Deprecated OTel attribute |
| `AL0013.md` | Missing telemetry schema URL |
| `AL0014.md` | Prefer pattern matching |
| `AL0015.md` | Normalize null-guard style |
| `AL0016.md` | Combine declaration with null-check |
| `AL0017.md` | Hardcoded package version |

---

## ANcpLua.NET.Sdk
**Path:** `/Users/ancplua/ANcpLua.NET.Sdk`

### Root
| File | Content |
|------|---------|
| `README.md` | SDK overview, variants, banned APIs, extensions |
| `CLAUDE.md` | Build commands, auto-injection, opt-in features |

### Shared Infrastructure (`/eng/Shared/`)
| File | Content |
|------|---------|
| `README.md` | Overview |
| `Throw/README.md` | Guard clauses: `Throw.IfNull()`, `Throw.IfNullOrEmpty()` |
| `CodeTests/README.md` | Code testing utilities |

### Extensions (`/eng/Extensions/`)
| File | Content |
|------|---------|
| `README.md` | Overview |
| `FakeLogger/README.md` | Fake logger for tests |
| `SourceGen/README.md` | Source generator utilities |
| `Comparers/README.md` | String ordinal comparison |

### Legacy Support (`/eng/LegacySupport/`)
| File | Content |
|------|---------|
| `README.md` | Polyfills overview |
| `TimeProvider/README.md` | TimeProvider for < net8.0 |
| `LanguageFeatures/README.md` | C# features (records, required) |
| `IndexRange/README.md` | Index/Range for < netcoreapp3.1 |
| `NullabilityAttributes/README.md` | Nullable attributes |
| `TrimAttributes/README.md` | AOT/trim attributes |
| `Experimental/README.md` | ExperimentalAttribute |
| `DiagnosticAttributes/README.md` | Diagnostic attributes |
| `IsExternalInit/README.md` | Init-only setters |
| `Exceptions/README.md` | UnreachableException |

### Web Defaults (`/eng/ANcpSdk.AspNetCore.ServiceDefaults/`)
| File | Content |
|------|---------|
| `README.md` | ServiceDefaults configuration |
| `AutoRegister/README.md` | Auto-registration behavior |

### MSBuild (`/eng/MSBuild/`)
| File | Content |
|------|---------|
| `README.md` | MSBuild configuration |
| `Polyfills/README.md` | Polyfill targets |

### SDK Entry Points (`/src/Sdk/`)
| File | Content |
|------|---------|
| `Readme.md` | SDK entry points, MSBuild flow |

---

## Search Index

### By Topic
| Topic | Files to Check |
|-------|---------------|
| **DiagnosticFlow** | Utilities: `docs/utilities/diagnostic-flow.md` |
| **SemanticGuard** | Utilities: `docs/utilities/semantic-guard.md` |
| **Pattern Matching** | Utilities: `docs/utilities/patterns.md` |
| **Analyzer Rules** | Analyzers: `docs/rules/AL*.md`, `README.md` |
| **Banned APIs** | SDK: `CLAUDE.md`, `README.md` |
| **Guard Clauses** | SDK: `eng/Shared/Throw/README.md` |
| **Polyfills** | SDK: `eng/LegacySupport/*/README.md` |
| **Test Fixtures** | SDK: `eng/Extensions/FakeLogger/README.md` |
| **Web Defaults** | SDK: `eng/ANcpSdk.AspNetCore.ServiceDefaults/README.md` |
| **MSBuild Properties** | SDK: `CLAUDE.md`, `src/Sdk/Readme.md` |

### By Keyword
| Keyword | Grep Pattern | Likely Location |
|---------|-------------|-----------------|
| Throw.IfNull | `Throw\.If` | SDK eng/Shared/Throw |
| IncrementalValuesProvider | `IncrementalValues` | Utilities docs/utilities/pipeline.md |
| EquatableArray | `EquatableArray` | Utilities docs/utilities/codegen.md |
| SymbolPattern | `SymbolPattern` | Utilities docs/utilities/patterns.md |
| ServiceDefaults | `ServiceDefaults` | SDK eng/ANcpSdk.AspNetCore |
| AL0001-AL0017 | `AL00[0-9][0-9]` | Analyzers docs/rules |
| xunit | `xunit\|IsTestProject` | SDK CLAUDE.md, README.md |
| TimeProvider | `TimeProvider` | SDK eng/LegacySupport/TimeProvider |
