---
name: mloda-plugins
description: >
  Guide an AI agent through building mloda (https://github.com/mloda-ai/mloda) plugins: FeatureGroup,
  ComputeFramework, and Extender classes. Use to check the mloda-registry index for an existing plugin before
  writing one, when writing or reviewing a FeatureGroup/ComputeFramework/Extender implementation, or when
  packaging, sharing, or publishing a plugin to mloda-registry.
license: MIT
---

# mloda-plugins: Building mloda Plugins

## Check the registry index first

Always do this before writing a plugin: it may already exist. mloda-registry publishes community plugins
covering common `{col}__{op}` transforms (aggregation, window/scalar/frame aggregate, scalar/point arithmetic,
rank, offset, percentile, binning, datetime, string ops, time bucketization, ffill, ema, sessionization,
resample); see its [plugins table](https://github.com/mloda-ai/mloda-registry#plugins) for the full list. None
of it ships with plain `pip install mloda`; install what you need (`pip install mloda-community` for all, or
one package like `pip install "mloda-community-rank[pandas]"`), then confirm what's actually loaded:

```python
from mloda.user import PluginLoader
from mloda.steward import get_feature_group_docs

PluginLoader.all()
for fg in get_feature_group_docs():
    print(fg.name, fg.description)
```

An empty or unrelated result means it isn't installed yet, not that it doesn't exist; see
[02-discover-plugins.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/02-discover-plugins.md)
for more on installed-vs-available. (The `mloda` skill covers the same check for requesting data instead of
writing a plugin.)

## The three plugin types

| Type | Role | Full guide |
|------|------|------------|
| **FeatureGroup** | A data transformation, the unit you'll write most often | [09-create-feature-group.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/09-create-feature-group.md) |
| **ComputeFramework** | The execution backend a transformation runs on (Pandas, PyArrow, Polars, DuckDB, ...) | [10-create-compute-framework.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/10-create-compute-framework.md) |
| **Extender** | Hooks for logging, tracing, validation around feature calculation | [11-create-extender.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/11-create-extender.md) |

Reach for a ComputeFramework only when adding a new execution backend, or an Extender for cross-cutting hooks.

## Minimal example

A primary-source FeatureGroup (no inputs):

```python
from mloda.provider import FeatureGroup

class CustomerScoring(FeatureGroup):
    @classmethod
    def calculate_feature(cls, data, features):
        return {"customer_score": 100}
```

A chained one, reusable via an `input__operation` feature name (see "FeatureGroup: key decisions" below):

```python
from mloda.provider import FeatureChainParserMixin, FeatureGroup

class MyOp(FeatureChainParserMixin, FeatureGroup):
    PREFIX_PATTERN = r".*__([\w]+)_my_op$"
    PROPERTY_MAPPING = {...}

    @classmethod
    def calculate_feature(cls, data, features): ...
```

Register either via `PluginLoader.all()` (installed package) or a direct import; see
[03-create-plugin-in-project.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/03-create-plugin-in-project.md).

## The plugin journey

Progression from using to sharing, each guide hosted in mloda-registry:

1. [Use an existing plugin](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/01-use-existing-plugin.md) / [Discover plugins](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/02-discover-plugins.md) - start here, before writing anything.
2. [Create a plugin in your project](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/03-create-plugin-in-project.md) - add a FeatureGroup inline, no separate package.
3. [Create a plugin package](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/04-create-plugin-package.md) - scaffold a standalone installable package from [mloda-plugin-template](https://github.com/mloda-ai/mloda-plugin-template).
4. [Share with your team](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/05-share-with-team.md) (private git) / [Publish to the community registry](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/06-publish-to-community.md) / [Contribute to official plugins](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/07-contribute-to-official.md) / [Become an official plugin](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/08-become-official.md).

Full progression: [docs/guides/index.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/index.md).

## FeatureGroup: key decisions

Full decision tree: [guide 09](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/09-create-feature-group.md). The recurring ones:

- **Loads external data (file, DB, API)?** Root feature pattern, see [01-root-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/01-root-features.md).
- **Transforms 1+ existing features?** Derived feature, see [02-derived-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/02-derived-features.md).
- **Should it be reusable via an `input__operation` naming pattern?** `FeatureChainParserMixin`, see [03-chained-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/03-chained-features.md) (2+ inputs: [04-multi-input-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/04-multi-input-features.md)).
- **Multiple output columns?** [05-multi-output-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/05-multi-output-features.md) (`feature~0`, `feature~1`).
- **Fitted/trained state between runs?** [06-artifact-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/06-artifact-features.md).
- **Time ordering, group-by, or joins across feature groups?** [07-index-features.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/07-index-features.md) / [08-links-joins.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/08-links-joins.md).
- **Group-identity option vs. runtime-only metadata?** [11-options.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/11-options.md) - a required context option that isn't forwarded through `input_features()` breaks chained requests; see [26-input-feature-forwarding.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/26-input-feature-forwarding.md) for the forwarding mechanism itself.
- **Standard column transform** (binning, window/scalar/frame aggregate, scalar/point arithmetic, rank, offset, percentile, string op, time bucketization, ffill, ema, resample, sessionization)? See the [data operation patterns index](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/data-operation-patterns/index.md) before writing one from scratch.
- **Feature defined via JSON/config instead of a naming pattern** (e.g. to back the `mloda` skill's LLM Tool Function pattern)? [22-feature-config.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/22-feature-config.md).
- **Ready to test?** [10-testing-guide.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/10-testing-guide.md).

Full pattern index (27 guides, covering filters, validators, versioning, streaming, realtime execution, and
more): [feature-group-patterns/index.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/feature-group-patterns/index.md).

## ComputeFramework: key decisions

Full decision tree: [guide 10](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/10-create-compute-framework.md).

- **Needs a connection/session object?** Data lake table format (Iceberg, Delta, Hudi) -> [05-data-lake.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/05-data-lake.md); otherwise -> [03-stateful-connection.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/03-stateful-connection.md) (DuckDB, Spark).
- **Lazy evaluation?** [02-stateless-lazy.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/02-stateless-lazy.md) (Polars Lazy, Ibis).
- **Eager, no external deps?** [04-zero-dependency.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/04-zero-dependency.md); with deps -> [01-stateless-eager.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/01-stateless-eager.md) (Pandas, PyArrow).
- **Cross-framework conversion?** [08-framework-transformer.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/08-framework-transformer.md).
- **Joins/merges or filters?** [06-merge-engine.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/06-merge-engine.md) / [07-filter-engine.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/07-filter-engine.md).
- **Ready to test?** [09-testing-guide.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/09-testing-guide.md).

Full pattern index: [compute-framework-patterns/index.md](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/compute-framework-patterns/index.md).

## Extender: key decisions

Full guide: [guide 11](https://github.com/mloda-ai/mloda-registry/blob/main/docs/guides/11-create-extender.md). Wraps feature calculation or input/output
validation; set a custom priority (lower runs first, default 100) if execution order matters; use class-level
storage for state under `ParallelizationMode.MULTIPROCESSING` (must be pickle-safe).

## Reference

- Registry (community/enterprise plugins, guides): <https://github.com/mloda-ai/mloda-registry>
- Plugin template (scaffold for a standalone package): <https://github.com/mloda-ai/mloda-plugin-template>
- Core docs: <https://mloda-ai.github.io/mloda/>
